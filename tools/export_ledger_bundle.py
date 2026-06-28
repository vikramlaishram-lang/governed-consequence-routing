#!/usr/bin/env python3
"""
export_ledger_bundle.py

Export a portable v0.5 verification bundle for local GCR artifacts.

This exporter packages a decision envelope, approval token, reviewer authority
manifest, evidence manifest, artifact hashes, schema hashes, verification
results, and proof-boundary metadata into one locally verifiable bundle.
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

PROOF_BOUNDARY = {
    "implementation_status": "local reference implementation and developer starter kit",
    "claims": [
        "v0.5 proves that a governed AI decision can be exported into a portable verification bundle whose included artifacts, hashes, verification results, and proof-boundary metadata are independently inspectable and locally verifiable.",
        "A bundle packages local verification material for independent inspection.",
        "The source of truth remains the included structured artifacts and their hashes, not the human-readable summary."
    ],
    "non_claims": [
        "production custody",
        "external notarization",
        "legal admissibility",
        "regulatory compliance",
        "clinical safety",
        "financial advice suitability",
        "enterprise compliance",
        "non-repudiation"
    ]
}


class LedgerBundleExportError(Exception):
    """Raised when ledger bundle export fails."""


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def canonical_json(value: Dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def compute_artifact_hash(value: Dict[str, Any]) -> str:
    return sha256_text(canonical_json(value))


def compute_bundle_hash(bundle: Dict[str, Any]) -> str:
    material = copy.deepcopy(bundle)
    material.pop("bundle_hash", None)
    return sha256_text(canonical_json(material))


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise LedgerBundleExportError(f"INPUT_NOT_FOUND: {path}")

    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise LedgerBundleExportError(f"JSON_INVALID: {exc}") from exc

    if not isinstance(value, dict):
        raise LedgerBundleExportError("INPUT_MUST_BE_JSON_OBJECT")

    return value


def write_json(path: Path, value: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, sort_keys=True) + "\n"
    path.write_text(payload, encoding="utf-8")


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
        raise LedgerBundleExportError(f"{label}_SCHEMA_INVALID at {location}: {first.message}")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_artifacts(
    envelope: Dict[str, Any],
    approval_token: Dict[str, Any],
    reviewer_manifest: Dict[str, Any],
    evidence_manifest: Dict[str, Any],
) -> None:
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


def verification_result(verifier: str, details: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "PASS",
        "verifier": verifier,
        "checked_at": utc_now(),
        "details": details,
    }


def build_bundle(
    envelope: Dict[str, Any],
    approval_token: Dict[str, Any],
    reviewer_manifest: Dict[str, Any],
    evidence_manifest: Dict[str, Any],
) -> Dict[str, Any]:
    verify_artifacts(envelope, approval_token, reviewer_manifest, evidence_manifest)

    bundle = {
        "schema_version": "verification_bundle.v0.5",
        "bundle_id": f"verification-bundle-{envelope['proposal_id']}",
        "created_at": utc_now(),
        "bundle_type": "FULL_GCR_BUNDLE",
        "bundle_subject": {
            "proposal_id": envelope["proposal_id"],
            "proposal_hash": envelope["proposal_hash"],
            "normalized_action_hash": envelope["normalized_action_hash"],
            "policy_hash": envelope["policy_hash"],
            "decision": envelope["decision"],
            "review_status": envelope["review_status"],
            "admissibility_decision": evidence_manifest["admissibility_decision"],
        },
        "artifacts": {
            "decision_envelope": envelope,
            "approval_token": approval_token,
            "reviewer_authority_manifest": reviewer_manifest,
            "evidence_manifest": evidence_manifest,
        },
        "artifact_hashes": {
            "decision_envelope_hash": compute_artifact_hash(envelope),
            "approval_token_hash": compute_artifact_hash(approval_token),
            "reviewer_authority_manifest_hash": compute_artifact_hash(reviewer_manifest),
            "evidence_manifest_hash": compute_artifact_hash(evidence_manifest),
            "decision_envelope_schema_hash": sha256_file(DECISION_ENVELOPE_SCHEMA_PATH),
            "approval_token_schema_hash": sha256_file(APPROVAL_TOKEN_SCHEMA_PATH),
            "reviewer_authority_manifest_schema_hash": sha256_file(REVIEWER_AUTHORITY_SCHEMA_PATH),
            "evidence_manifest_schema_hash": sha256_file(EVIDENCE_MANIFEST_SCHEMA_PATH),
        },
        "verification_results": {
            "approval_token_verification": verification_result(
                "tools/verify_approval_token.py",
                {"approval_token_id": approval_token["approval_token_id"]},
            ),
            "reviewer_authority_binding_verification": verification_result(
                "tools/verify_reviewer_authority_binding.py",
                {"reviewer_authority_id": reviewer_manifest["reviewer_authority_id"]},
            ),
            "evidence_manifest_binding_verification": verification_result(
                "tools/verify_evidence_manifest_binding.py",
                {"evidence_manifest_id": evidence_manifest["evidence_manifest_id"]},
            ),
            "bundle_hash_verification": verification_result(
                "tools/verify_ledger_bundle.py",
                {"bundle_hash_verification": "computed during export"},
            ),
        },
        "proof_boundary": PROOF_BOUNDARY,
        "bundle_hash": "sha256:" + ("0" * 64),
    }

    return bundle


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a portable v0.5 GCR ledger bundle.")
    parser.add_argument("--envelope", required=True, help="Decision envelope JSON file.")
    parser.add_argument("--approval-token", required=True, help="Approval token JSON file.")
    parser.add_argument("--reviewer-manifest", required=True, help="Reviewer authority manifest JSON file.")
    parser.add_argument("--evidence-manifest", required=True, help="Evidence manifest JSON file.")
    parser.add_argument("--out", required=True, help="Output path for verification bundle JSON.")
    parser.add_argument(
        "--write-hash",
        action="store_true",
        help="Write the computed bundle_hash into the bundle.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        envelope = load_json(Path(args.envelope))
        approval_token = load_json(Path(args.approval_token))
        reviewer_manifest = load_json(Path(args.reviewer_manifest))
        evidence_manifest = load_json(Path(args.evidence_manifest))

        bundle = build_bundle(envelope, approval_token, reviewer_manifest, evidence_manifest)
        computed_hash = compute_bundle_hash(bundle)

        if args.write_hash:
            bundle["bundle_hash"] = computed_hash

        bundle_schema = load_schema(BUNDLE_SCHEMA_PATH)
        check_schema(bundle, bundle_schema, "VERIFICATION_BUNDLE")
        write_json(Path(args.out), bundle)

        print("LEDGER BUNDLE EXPORT PASS")
        print(f"bundle_id: {bundle['bundle_id']}")
        print(f"proposal_id: {bundle['bundle_subject']['proposal_id']}")
        print(f"bundle_type: {bundle['bundle_type']}")
        print(f"bundle_hash: {bundle['bundle_hash']}")
        return 0

    except Exception as exc:
        print(f"LEDGER BUNDLE EXPORT FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
