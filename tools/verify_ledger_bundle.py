#!/usr/bin/env python3
"""
verify_ledger_bundle.py

Verify a portable v0.5 GCR verification bundle locally.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict

from jsonschema import Draft202012Validator, FormatChecker


BUNDLE_SCHEMA_PATH = Path("schemas/verification_bundle_v0.5.schema.json")
DECISION_ENVELOPE_SCHEMA_PATH = Path("schemas/decision_envelope_v0.1.schema.json")
APPROVAL_TOKEN_SCHEMA_PATH = Path("schemas/approval_token_v0.3.schema.json")
REVIEWER_AUTHORITY_SCHEMA_PATH = Path("schemas/reviewer_authority_manifest_v0.3.schema.json")
EVIDENCE_MANIFEST_SCHEMA_PATH = Path("schemas/evidence_manifest_v0.4.schema.json")

APPROVAL_TOKEN_VERIFIER_PATH = Path("tools/verify_approval_token.py")
REVIEWER_AUTHORITY_VERIFIER_PATH = Path("tools/verify_reviewer_authority_binding.py")
EVIDENCE_BINDING_VERIFIER_PATH = Path("tools/verify_evidence_manifest_binding.py")


class LedgerBundleVerificationError(Exception):
    """Raised when ledger bundle verification fails."""


def canonical_json(value: Dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_schema_file(path: Path) -> str:
    schema = load_json(path)
    return sha256_text(canonical_json(schema))


def compute_artifact_hash(value: Dict[str, Any]) -> str:
    return sha256_text(canonical_json(value))


def compute_bundle_hash(bundle: Dict[str, Any]) -> str:
    material = copy.deepcopy(bundle)
    material.pop("bundle_hash", None)
    return sha256_text(canonical_json(material))


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise LedgerBundleVerificationError(f"INPUT_NOT_FOUND: {path}")

    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise LedgerBundleVerificationError(f"JSON_INVALID: {exc}") from exc

    if not isinstance(value, dict):
        raise LedgerBundleVerificationError("INPUT_MUST_BE_JSON_OBJECT")

    return value


def load_schema(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise LedgerBundleVerificationError(f"SCHEMA_NOT_FOUND: {path}")

    schema = load_json(path)
    Draft202012Validator.check_schema(schema)
    return schema


def check_schema(value: Dict[str, Any], schema: Dict[str, Any], label: str) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(value), key=lambda error: error.path)

    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.path) or "<root>"
        raise LedgerBundleVerificationError(f"{label}_SCHEMA_INVALID at {location}: {first.message}")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require_equal(label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        raise LedgerBundleVerificationError(f"{label}_MISMATCH: expected {expected}, got {actual}")


def verify_bundle_hash(bundle: Dict[str, Any]) -> None:
    require_equal("BUNDLE_HASH", bundle.get("bundle_hash"), compute_bundle_hash(bundle))


def verify_artifact_hashes(bundle: Dict[str, Any]) -> None:
    artifacts = bundle["artifacts"]
    hashes = bundle["artifact_hashes"]

    expected = {
        "decision_envelope_hash": compute_artifact_hash(artifacts["decision_envelope"]),
        "approval_token_hash": compute_artifact_hash(artifacts["approval_token"]),
        "reviewer_authority_manifest_hash": compute_artifact_hash(artifacts["reviewer_authority_manifest"]),
        "evidence_manifest_hash": compute_artifact_hash(artifacts["evidence_manifest"]),
        "decision_envelope_schema_hash": sha256_schema_file(DECISION_ENVELOPE_SCHEMA_PATH),
        "approval_token_schema_hash": sha256_schema_file(APPROVAL_TOKEN_SCHEMA_PATH),
        "reviewer_authority_manifest_schema_hash": sha256_schema_file(REVIEWER_AUTHORITY_SCHEMA_PATH),
        "evidence_manifest_schema_hash": sha256_schema_file(EVIDENCE_MANIFEST_SCHEMA_PATH),
    }

    for field, expected_hash in expected.items():
        require_equal(field.upper(), hashes.get(field), expected_hash)


def verify_embedded_artifacts(bundle: Dict[str, Any]) -> None:
    artifacts = bundle["artifacts"]
    envelope = artifacts["decision_envelope"]
    approval_token = artifacts["approval_token"]
    reviewer_manifest = artifacts["reviewer_authority_manifest"]
    evidence_manifest = artifacts["evidence_manifest"]

    approval_module = load_module("verify_approval_token", APPROVAL_TOKEN_VERIFIER_PATH)
    reviewer_module = load_module("verify_reviewer_authority_binding", REVIEWER_AUTHORITY_VERIFIER_PATH)
    evidence_module = load_module("verify_evidence_manifest_binding", EVIDENCE_BINDING_VERIFIER_PATH)

    approval_schema = load_schema(APPROVAL_TOKEN_SCHEMA_PATH)
    reviewer_schema = load_schema(REVIEWER_AUTHORITY_SCHEMA_PATH)
    evidence_schema = load_schema(EVIDENCE_MANIFEST_SCHEMA_PATH)
    envelope_schema = load_schema(DECISION_ENVELOPE_SCHEMA_PATH)

    check_schema(envelope, envelope_schema, "DECISION_ENVELOPE")
    check_schema(approval_token, approval_schema, "APPROVAL_TOKEN")
    check_schema(reviewer_manifest, reviewer_schema, "REVIEWER_AUTHORITY_MANIFEST")
    check_schema(evidence_manifest, evidence_schema, "EVIDENCE_MANIFEST")

    approval_module.verify_approval_token(approval_token, approval_schema)
    reviewer_module.verify_binding(reviewer_manifest, approval_token)
    evidence_module.verify_evidence_manifest_binding(
        envelope,
        evidence_manifest,
        evidence_schema,
        envelope_schema,
    )


def verify_bundle_subject(bundle: Dict[str, Any]) -> None:
    subject = bundle["bundle_subject"]
    envelope = bundle["artifacts"]["decision_envelope"]
    evidence_manifest = bundle["artifacts"]["evidence_manifest"]

    for field in [
        "proposal_id",
        "proposal_hash",
        "normalized_action_hash",
        "policy_hash",
    ]:
        require_equal(f"BUNDLE_SUBJECT_{field.upper()}", subject.get(field), envelope.get(field))
        require_equal(f"BUNDLE_SUBJECT_EVIDENCE_{field.upper()}", subject.get(field), evidence_manifest.get(field))

    require_equal("BUNDLE_SUBJECT_DECISION", subject.get("decision"), envelope.get("decision"))
    require_equal("BUNDLE_SUBJECT_REVIEW_STATUS", subject.get("review_status"), envelope.get("review_status"))
    require_equal(
        "BUNDLE_SUBJECT_ADMISSIBILITY_DECISION",
        subject.get("admissibility_decision"),
        evidence_manifest.get("admissibility_decision"),
    )


def verify_results_are_pass(bundle: Dict[str, Any]) -> None:
    for name, result in bundle["verification_results"].items():
        if result.get("status") != "PASS":
            raise LedgerBundleVerificationError(
                f"VERIFICATION_RESULT_NOT_PASS: {name}={result.get('status')}"
            )


def verify_ledger_bundle(bundle: Dict[str, Any]) -> None:
    check_schema(bundle, load_schema(BUNDLE_SCHEMA_PATH), "VERIFICATION_BUNDLE")
    verify_bundle_hash(bundle)
    verify_artifact_hashes(bundle)
    verify_embedded_artifacts(bundle)
    verify_bundle_subject(bundle)
    verify_results_are_pass(bundle)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify a portable v0.5 GCR ledger bundle.")
    parser.add_argument("input", help="Verification bundle JSON file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        bundle = load_json(Path(args.input))
        verify_ledger_bundle(bundle)

        print("LEDGER BUNDLE VERIFY PASS")
        print(f"bundle_id: {bundle['bundle_id']}")
        print(f"proposal_id: {bundle['bundle_subject']['proposal_id']}")
        print(f"bundle_type: {bundle['bundle_type']}")
        print(f"bundle_hash: {bundle['bundle_hash']}")
        return 0

    except Exception as exc:
        print(f"LEDGER BUNDLE VERIFY FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
