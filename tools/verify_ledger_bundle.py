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
from datetime import datetime, timezone
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

VERIFIER_NAME = "gcr-ledger-bundle-verifier"
VERIFIER_VERSION = "v0.6"
VERIFICATION_TOOL = "tools/verify_ledger_bundle.py"

RECEIPT_PROOF_BOUNDARY = {
    "boundary_type": "local reference implementation and developer starter kit",
    "claims": [
        "v0.6 proves that a portable GCR bundle can be independently verified and that the verification run can be recorded as a durable local receipt.",
        "The receipt attests to a verification run.",
        "A verification receipt is evidence of verification, not evidence of correctness."
    ],
    "non_claims": [
        "re-authorization of the original action",
        "replacement of the portable verification bundle",
        "legal or compliance status",
        "production custody",
        "external notarization",
        "legal admissibility",
        "regulatory compliance",
        "clinical safety",
        "financial advice suitability",
        "enterprise compliance",
        "SSO-backed identity",
        "production identity",
        "non-repudiation"
    ]
}

CHECKS_PERFORMED = [
    "verification_bundle_schema_valid",
    "bundle_hash_matches",
    "artifact_hashes_match",
    "schema_hashes_match",
    "embedded_approval_token_verifies",
    "reviewer_authority_binding_verifies",
    "evidence_manifest_binding_verifies",
    "bundle_subject_matches_embedded_artifacts",
    "recorded_verification_results_are_pass"
]


class LedgerBundleVerificationError(Exception):
    """Raised when ledger bundle verification fails."""


def canonical_json(value: Dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_schema_file(path: Path) -> str:
    schema = load_json(path)
    return sha256_text(canonical_json(schema))


def compute_artifact_hash(value: Dict[str, Any]) -> str:
    return sha256_text(canonical_json(value))


def compute_bundle_hash(bundle: Dict[str, Any]) -> str:
    material = copy.deepcopy(bundle)
    material.pop("bundle_hash", None)
    return sha256_text(canonical_json(material))


def compute_receipt_hash(receipt: Dict[str, Any]) -> str:
    material = copy.deepcopy(receipt)
    material.pop("receipt_hash", None)
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


def write_json(path: Path, value: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, sort_keys=True) + "\n"
    path.write_text(payload, encoding="utf-8")


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


def split_hashes(hashes: Dict[str, Any]) -> tuple[Dict[str, str], Dict[str, str]]:
    schema_hashes = {
        key: value
        for key, value in hashes.items()
        if key.endswith("_schema_hash")
    }
    artifact_hashes = {
        key: value
        for key, value in hashes.items()
        if not key.endswith("_schema_hash")
    }
    return schema_hashes, artifact_hashes


def build_verification_results(overall_status: str, failure_reasons: list[str]) -> Dict[str, Dict[str, str]]:
    if overall_status == "PASS":
        return {
            check: {
                "status": "PASS",
                "message": "Check completed successfully."
            }
            for check in CHECKS_PERFORMED
        }

    return {
        "ledger_bundle_verification": {
            "status": "FAIL",
            "message": "; ".join(failure_reasons)
        }
    }


def build_verification_receipt(
    bundle: Dict[str, Any],
    bundle_path_or_subject: str,
    verification_command: str,
    overall_status: str,
    failure_reasons: list[str],
) -> Dict[str, Any]:
    bundle_subject = bundle.get("bundle_subject", {})
    artifact_hashes = bundle.get("artifact_hashes", {})
    schema_hashes_checked, artifact_hashes_checked = split_hashes(artifact_hashes)
    bundle_id = bundle.get("bundle_id", "unknown-bundle-id")
    proposal_id = bundle_subject.get("proposal_id", "00000000-0000-4000-8000-000000000000")

    receipt = {
        "receipt_schema_version": "verification_receipt_v0.6",
        "receipt_id": f"verification-receipt-{bundle_id}",
        "created_at": utc_now(),
        "verifier": {
            "verifier_name": VERIFIER_NAME,
            "verifier_version": VERIFIER_VERSION,
            "verification_tool": VERIFICATION_TOOL,
            "verification_command": verification_command,
        },
        "bundle_subject": {
            "bundle_id": bundle_id,
            "bundle_hash": bundle.get("bundle_hash", "sha256:" + ("0" * 64)),
            "bundle_type": bundle.get("bundle_type", "UNKNOWN_BUNDLE"),
            "proposal_id": proposal_id,
            "bundle_path_or_subject": bundle_path_or_subject,
        },
        "schema_hashes_checked": schema_hashes_checked,
        "artifact_hashes_checked": artifact_hashes_checked,
        "checks_performed": CHECKS_PERFORMED,
        "verification_results": build_verification_results(overall_status, failure_reasons),
        "overall_status": overall_status,
        "failure_reasons": failure_reasons,
        "proof_boundary": RECEIPT_PROOF_BOUNDARY,
        "receipt_hash": "sha256:" + ("0" * 64),
    }
    receipt["receipt_hash"] = compute_receipt_hash(receipt)
    return receipt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify a portable v0.5 GCR ledger bundle.")
    parser.add_argument("input", help="Verification bundle JSON file.")
    parser.add_argument(
        "--receipt-out",
        default=None,
        help="Optional output path for a v0.6 verification receipt JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bundle = None
    input_path = Path(args.input)
    verification_command = " ".join(sys.argv)

    try:
        bundle = load_json(input_path)
        verify_ledger_bundle(bundle)

        if args.receipt_out:
            receipt = build_verification_receipt(
                bundle=bundle,
                bundle_path_or_subject=str(input_path).replace("\\", "/"),
                verification_command=verification_command,
                overall_status="PASS",
                failure_reasons=[],
            )
            write_json(Path(args.receipt_out), receipt)

        print("LEDGER BUNDLE VERIFY PASS")
        print(f"bundle_id: {bundle['bundle_id']}")
        print(f"proposal_id: {bundle['bundle_subject']['proposal_id']}")
        print(f"bundle_type: {bundle['bundle_type']}")
        print(f"bundle_hash: {bundle['bundle_hash']}")
        if args.receipt_out:
            print(f"receipt_out: {args.receipt_out}")
            print(f"receipt_id: {receipt['receipt_id']}")
            print(f"receipt_hash: {receipt['receipt_hash']}")
        return 0

    except Exception as exc:
        if args.receipt_out and bundle is not None:
            try:
                receipt = build_verification_receipt(
                    bundle=bundle,
                    bundle_path_or_subject=str(input_path).replace("\\", "/"),
                    verification_command=verification_command,
                    overall_status="FAIL",
                    failure_reasons=[str(exc)],
                )
                write_json(Path(args.receipt_out), receipt)
            except Exception:
                pass
        print(f"LEDGER BUNDLE VERIFY FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
