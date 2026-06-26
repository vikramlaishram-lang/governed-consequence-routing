#!/usr/bin/env python3
"""
verify_decision_envelope_approval_binding.py

Local verifier for decision-envelope approval binding.

This verifier checks:
- reviewer authority manifest and approval token binding passes
- approval token hash integrity passes
- decision envelope schema validity passes
- approval token binds to the same proposal_id
- approval token binds to the same proposal_hash
- approval token binds to the same normalized_action_hash
- approval token binds to the same policy_hash
- reviewer_authority_id matches
- approval scope covers the envelope consequence class
- approval scope covers the envelope decision path
- envelope created_at is within the approval token window

It does not claim identity proof, SSO-backed approval, legal signature validity,
external notarization, or production approval workflow readiness.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from jsonschema import Draft202012Validator, FormatChecker


ENVELOPE_SCHEMA_PATH = Path("schemas/decision_envelope_v0.1.schema.json")
AUTHORITY_BINDING_VERIFIER_PATH = Path("tools/verify_reviewer_authority_binding.py")


class DecisionEnvelopeApprovalBindingError(Exception):
    """Raised when decision-envelope approval binding verification fails."""


def load_authority_binding_module():
    spec = importlib.util.spec_from_file_location(
        "verify_reviewer_authority_binding",
        AUTHORITY_BINDING_VERIFIER_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise DecisionEnvelopeApprovalBindingError(f"INPUT_NOT_FOUND: {path}")

    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise DecisionEnvelopeApprovalBindingError(f"JSON_INVALID: {exc}") from exc

    if not isinstance(value, dict):
        raise DecisionEnvelopeApprovalBindingError("INPUT_MUST_BE_JSON_OBJECT")

    return value


def load_schema(path: Path) -> Dict[str, Any]:
    schema = load_json(path)
    Draft202012Validator.check_schema(schema)
    return schema


def check_schema(value: Dict[str, Any], schema: Dict[str, Any], label: str) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(value), key=lambda error: error.path)

    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.path) or "<root>"
        raise DecisionEnvelopeApprovalBindingError(
            f"{label}_SCHEMA_INVALID at {location}: {first.message}"
        )


def parse_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed


def verify_field_match(envelope: Dict[str, Any], token: Dict[str, Any], field: str) -> None:
    if envelope.get(field) != token.get(field):
        raise DecisionEnvelopeApprovalBindingError(
            f"{field.upper()}_MISMATCH: envelope={envelope.get(field)} token={token.get(field)}"
        )


def verify_approval_window(envelope: Dict[str, Any], token: Dict[str, Any]) -> None:
    envelope_created_at = parse_datetime(envelope["created_at"])
    issued_at = parse_datetime(token["issued_at"])
    expires_at = parse_datetime(token["expires_at"])

    if envelope_created_at < issued_at or envelope_created_at > expires_at:
        raise DecisionEnvelopeApprovalBindingError("ENVELOPE_OUTSIDE_APPROVAL_TOKEN_WINDOW")


def verify_decision_envelope_approval_binding(
    envelope: Dict[str, Any],
    token: Dict[str, Any],
    manifest: Dict[str, Any],
) -> None:
    authority_module = load_authority_binding_module()

    authority_schema = authority_module.load_schema(authority_module.AUTHORITY_SCHEMA_PATH)
    token_schema = authority_module.load_schema(authority_module.TOKEN_SCHEMA_PATH)

    authority_module.check_schema(manifest, authority_schema, "REVIEWER_AUTHORITY_MANIFEST")
    authority_module.check_schema(token, token_schema, "APPROVAL_TOKEN")
    authority_module.verify_binding(manifest, token)

    envelope_schema = load_schema(ENVELOPE_SCHEMA_PATH)
    check_schema(envelope, envelope_schema, "DECISION_ENVELOPE")

    if envelope.get("reviewer_authority_id") != token.get("reviewer_authority_id"):
        raise DecisionEnvelopeApprovalBindingError("REVIEWER_AUTHORITY_ID_MISMATCH")

    for field in [
        "proposal_id",
        "proposal_hash",
        "normalized_action_hash",
        "policy_hash",
    ]:
        verify_field_match(envelope, token, field)

    envelope_class = envelope["consequence_classification"]["consequence_class"]
    approved_classes = token["approval_scope"]["approved_consequence_classes"]

    if envelope_class not in approved_classes:
        raise DecisionEnvelopeApprovalBindingError(
            f"ENVELOPE_CONSEQUENCE_CLASS_NOT_APPROVED: {envelope_class}"
        )

    envelope_decision = envelope["decision"]
    approved_decisions = token["approval_scope"]["approved_decisions"]

    if envelope_decision not in approved_decisions:
        raise DecisionEnvelopeApprovalBindingError(
            f"ENVELOPE_DECISION_NOT_APPROVED: {envelope_decision}"
        )

    if envelope["review_status"] != "APPROVED":
        raise DecisionEnvelopeApprovalBindingError(
            f"ENVELOPE_REVIEW_STATUS_NOT_APPROVED: {envelope['review_status']}"
        )

    verify_approval_window(envelope, token)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify decision envelope, approval token, and reviewer authority binding."
    )
    parser.add_argument("--envelope", required=True, help="Decision envelope JSON file.")
    parser.add_argument("--token", required=True, help="Approval token JSON file.")
    parser.add_argument("--manifest", required=True, help="Reviewer authority manifest JSON file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        envelope = load_json(Path(args.envelope))
        token = load_json(Path(args.token))
        manifest = load_json(Path(args.manifest))

        verify_decision_envelope_approval_binding(envelope, token, manifest)

        print("DECISION ENVELOPE APPROVAL BINDING VERIFY PASS")
        print(f"proposal_id: {envelope['proposal_id']}")
        print(f"reviewer_authority_id: {envelope['reviewer_authority_id']}")
        print(f"approval_token_id: {token['approval_token_id']}")
        print(f"decision: {envelope['decision']}")
        print(f"review_status: {envelope['review_status']}")
        return 0

    except Exception as exc:
        print(f"DECISION ENVELOPE APPROVAL BINDING VERIFY FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())