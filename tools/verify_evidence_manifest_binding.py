#!/usr/bin/env python3
"""
verify_evidence_manifest_binding.py

Local verifier for decision-envelope evidence manifest binding.

This verifier checks:
- evidence manifest schema validity
- evidence_manifest_hash integrity
- decision envelope schema validity
- envelope evidence_manifest_hash matches the manifest hash
- proposal and policy hash fields match across envelope and manifest
- admitted evidence satisfies the manifest requirements
- SUFFICIENT admissibility decision is required for a pass

It does not claim production compliance, legal admissibility, clinical safety,
financial advice suitability, enterprise custody, or external evidence truth.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from jsonschema import Draft202012Validator, FormatChecker


EVIDENCE_SCHEMA_PATH = Path("schemas/evidence_manifest_v0.4.schema.json")
ENVELOPE_SCHEMA_PATH = Path("schemas/decision_envelope_v0.1.schema.json")


class EvidenceManifestBindingVerificationError(Exception):
    """Raised when evidence manifest binding verification fails."""


def canonical_json(obj: Dict[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_evidence_manifest_hash(manifest: Dict[str, Any]) -> str:
    material = copy.deepcopy(manifest)
    material.pop("evidence_manifest_hash", None)
    return sha256_text(canonical_json(material))


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise EvidenceManifestBindingVerificationError(f"INPUT_NOT_FOUND: {path}")

    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise EvidenceManifestBindingVerificationError(f"JSON_INVALID: {exc}") from exc

    if not isinstance(value, dict):
        raise EvidenceManifestBindingVerificationError("INPUT_MUST_BE_JSON_OBJECT")

    return value


def write_json(path: Path, value: Dict[str, Any]) -> None:
    payload = json.dumps(value, indent=2, sort_keys=True) + "\n"
    path.write_text(payload, encoding="utf-8")


def load_schema(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise EvidenceManifestBindingVerificationError(f"SCHEMA_NOT_FOUND: {path}")

    schema = load_json(path)
    Draft202012Validator.check_schema(schema)
    return schema


def check_schema(value: Dict[str, Any], schema: Dict[str, Any], label: str) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(value), key=lambda error: error.path)

    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.path) or "<root>"
        raise EvidenceManifestBindingVerificationError(
            f"{label}_SCHEMA_INVALID at {location}: {first.message}"
        )


def verify_field_match(envelope: Dict[str, Any], manifest: Dict[str, Any], field: str) -> None:
    if envelope.get(field) != manifest.get(field):
        raise EvidenceManifestBindingVerificationError(
            f"{field.upper()}_MISMATCH: envelope={envelope.get(field)} manifest={manifest.get(field)}"
        )


def admitted_evidence_items(manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        item
        for item in manifest.get("evidence_items", [])
        if item.get("admissibility_status") == "ADMITTED"
    ]


def verify_evidence_requirements(manifest: Dict[str, Any]) -> int:
    admitted_items = admitted_evidence_items(manifest)
    admitted_count = len(admitted_items)
    requirements = manifest["evidence_requirements"]
    minimum_admitted_items = requirements["minimum_admitted_items"]

    if admitted_count < minimum_admitted_items:
        raise EvidenceManifestBindingVerificationError(
            f"MINIMUM_ADMITTED_EVIDENCE_COUNT_NOT_MET: required={minimum_admitted_items} admitted={admitted_count}"
        )

    admitted_types = {item["evidence_type"] for item in admitted_items}
    missing_types = [
        evidence_type
        for evidence_type in requirements["required_evidence_types"]
        if evidence_type not in admitted_types
    ]

    if missing_types:
        raise EvidenceManifestBindingVerificationError(
            f"REQUIRED_EVIDENCE_TYPE_MISSING: {','.join(missing_types)}"
        )

    return admitted_count


def verify_evidence_manifest_binding(
    envelope: Dict[str, Any],
    manifest: Dict[str, Any],
    evidence_schema: Dict[str, Any],
    envelope_schema: Dict[str, Any],
) -> int:
    check_schema(manifest, evidence_schema, "EVIDENCE_MANIFEST")

    expected_hash = compute_evidence_manifest_hash(manifest)
    actual_hash = manifest.get("evidence_manifest_hash")

    if actual_hash != expected_hash:
        raise EvidenceManifestBindingVerificationError(
            f"EVIDENCE_MANIFEST_HASH_MISMATCH: expected {expected_hash}, got {actual_hash}"
        )

    check_schema(envelope, envelope_schema, "DECISION_ENVELOPE")

    if envelope.get("evidence_manifest_hash") != manifest.get("evidence_manifest_hash"):
        raise EvidenceManifestBindingVerificationError(
            "EVIDENCE_MANIFEST_HASH_BINDING_MISMATCH"
        )

    for field in [
        "proposal_id",
        "proposal_hash",
        "normalized_action_hash",
        "policy_hash",
    ]:
        verify_field_match(envelope, manifest, field)

    admitted_count = verify_evidence_requirements(manifest)

    if manifest["admissibility_decision"] != "SUFFICIENT":
        raise EvidenceManifestBindingVerificationError(
            f"ADMISSIBILITY_DECISION_NOT_SUFFICIENT: {manifest['admissibility_decision']}"
        )

    return admitted_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify decision envelope and evidence manifest binding."
    )
    parser.add_argument("--envelope", required=True, help="Decision envelope JSON file.")
    parser.add_argument("--manifest", required=True, help="Evidence manifest JSON file.")
    parser.add_argument(
        "--evidence-schema",
        default=str(EVIDENCE_SCHEMA_PATH),
        help="Path to evidence manifest schema.",
    )
    parser.add_argument(
        "--envelope-schema",
        default=str(ENVELOPE_SCHEMA_PATH),
        help="Path to decision envelope schema.",
    )
    parser.add_argument(
        "--write-hash",
        action="store_true",
        help="Rewrite evidence_manifest_hash with the computed value before verification.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest)

    try:
        evidence_schema = load_schema(Path(args.evidence_schema))
        envelope_schema = load_schema(Path(args.envelope_schema))
        manifest = load_json(manifest_path)
        envelope = load_json(Path(args.envelope))

        if args.write_hash:
            manifest["evidence_manifest_hash"] = compute_evidence_manifest_hash(manifest)
            write_json(manifest_path, manifest)
            print(f"EVIDENCE MANIFEST HASH WRITTEN: {manifest_path}")

        admitted_count = verify_evidence_manifest_binding(
            envelope,
            manifest,
            evidence_schema,
            envelope_schema,
        )

        print("EVIDENCE MANIFEST BINDING VERIFY PASS")
        print(f"evidence_manifest_id: {manifest['evidence_manifest_id']}")
        print(f"proposal_id: {manifest['proposal_id']}")
        print(f"admissibility_decision: {manifest['admissibility_decision']}")
        print(f"admitted_evidence_count: {admitted_count}")
        return 0

    except EvidenceManifestBindingVerificationError as exc:
        print(f"EVIDENCE MANIFEST BINDING VERIFY FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
