#!/usr/bin/env python3
"""
verify_reviewer_authority_binding.py

Local verifier for reviewer-authority v0.3 binding.

This verifier checks:
- reviewer authority manifest schema validity
- approval token schema validity
- approval token hash integrity
- approval token is bound to the reviewer authority record
- reviewer authority is ACTIVE
- approval issued_at is within reviewer authority validity window
- approval scope is within reviewer authority scope

It does not bind approval tokens to decision envelopes yet.
That binding is reserved for a later v0.3 step.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable

from jsonschema import Draft202012Validator, FormatChecker


AUTHORITY_SCHEMA_PATH = Path("schemas/reviewer_authority_manifest_v0.3.schema.json")
TOKEN_SCHEMA_PATH = Path("schemas/approval_token_v0.3.schema.json")


class ReviewerAuthorityBindingError(Exception):
    """Raised when reviewer authority binding verification fails."""


def canonical_json(obj: Dict[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_approval_token_hash(token: Dict[str, Any]) -> str:
    material = copy.deepcopy(token)
    material.pop("approval_token_hash", None)
    return sha256_text(canonical_json(material))


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise ReviewerAuthorityBindingError(f"INPUT_NOT_FOUND: {path}")

    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ReviewerAuthorityBindingError(f"JSON_INVALID: {exc}") from exc

    if not isinstance(value, dict):
        raise ReviewerAuthorityBindingError("INPUT_MUST_BE_JSON_OBJECT")

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
        raise ReviewerAuthorityBindingError(
            f"{label}_SCHEMA_INVALID at {location}: {first.message}"
        )


def parse_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed


def require_subset(values: Iterable[str], allowed: Iterable[str], error_name: str) -> None:
    allowed_set = set(allowed)

    for value in values:
        if value not in allowed_set:
            raise ReviewerAuthorityBindingError(f"{error_name}: {value}")


def verify_token_hash(token: Dict[str, Any]) -> None:
    expected_hash = compute_approval_token_hash(token)
    actual_hash = token.get("approval_token_hash")

    if actual_hash != expected_hash:
        raise ReviewerAuthorityBindingError(
            f"APPROVAL_TOKEN_HASH_MISMATCH: expected {expected_hash}, got {actual_hash}"
        )


def verify_binding(manifest: Dict[str, Any], token: Dict[str, Any]) -> None:
    verify_token_hash(token)

    if token["reviewer_authority_id"] != manifest["reviewer_authority_id"]:
        raise ReviewerAuthorityBindingError("REVIEWER_AUTHORITY_ID_MISMATCH")

    if token["authority_record_hash"] != manifest["authority_record_hash"]:
        raise ReviewerAuthorityBindingError("AUTHORITY_RECORD_HASH_MISMATCH")

    if manifest["authority_status"] != "ACTIVE":
        raise ReviewerAuthorityBindingError(
            f"AUTHORITY_NOT_ACTIVE: {manifest['authority_status']}"
        )

    issued_at = parse_datetime(token["issued_at"])
    expires_at = parse_datetime(token["expires_at"])
    valid_from = parse_datetime(manifest["valid_from"])
    valid_until = parse_datetime(manifest["valid_until"])

    if expires_at <= issued_at:
        raise ReviewerAuthorityBindingError("APPROVAL_TOKEN_TIME_WINDOW_INVALID")

    if issued_at < valid_from or issued_at > valid_until:
        raise ReviewerAuthorityBindingError("APPROVAL_ISSUED_OUTSIDE_AUTHORITY_WINDOW")

    token_class = token["consequence_classification"]["consequence_class"]
    manifest_classes = manifest["authority_scope"]["allowed_consequence_classes"]
    manifest_decisions = manifest["authority_scope"]["allowed_decisions"]

    if token_class not in manifest_classes:
        raise ReviewerAuthorityBindingError(f"CONSEQUENCE_CLASS_NOT_AUTHORIZED: {token_class}")

    require_subset(
        token["approval_scope"]["approved_consequence_classes"],
        manifest_classes,
        "APPROVED_CONSEQUENCE_CLASS_NOT_AUTHORIZED",
    )

    require_subset(
        token["approval_scope"]["approved_decisions"],
        manifest_decisions,
        "APPROVED_DECISION_NOT_AUTHORIZED",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify reviewer authority manifest and approval token binding."
    )
    parser.add_argument("--manifest", required=True, help="Reviewer authority manifest JSON file.")
    parser.add_argument("--token", required=True, help="Approval token JSON file.")
    parser.add_argument(
        "--authority-schema",
        default=str(AUTHORITY_SCHEMA_PATH),
        help="Path to reviewer authority manifest schema.",
    )
    parser.add_argument(
        "--token-schema",
        default=str(TOKEN_SCHEMA_PATH),
        help="Path to approval token schema.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        authority_schema = load_schema(Path(args.authority_schema))
        token_schema = load_schema(Path(args.token_schema))

        manifest = load_json(Path(args.manifest))
        token = load_json(Path(args.token))

        check_schema(manifest, authority_schema, "REVIEWER_AUTHORITY_MANIFEST")
        check_schema(token, token_schema, "APPROVAL_TOKEN")
        verify_binding(manifest, token)

        print("REVIEWER AUTHORITY BINDING VERIFY PASS")
        print(f"reviewer_authority_id: {manifest['reviewer_authority_id']}")
        print(f"approval_token_id: {token['approval_token_id']}")
        print(f"authority_record_hash: {manifest['authority_record_hash']}")
        print(f"approval_token_hash: {token['approval_token_hash']}")
        return 0

    except ReviewerAuthorityBindingError as exc:
        print(f"REVIEWER AUTHORITY BINDING VERIFY FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())