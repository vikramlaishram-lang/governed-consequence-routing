#!/usr/bin/env python3
"""
verify_verification_receipt.py

Verify a local v0.6 GCR verification receipt.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict

from jsonschema import Draft202012Validator, FormatChecker


RECEIPT_SCHEMA_PATH = Path("schemas/verification_receipt_v0.6.schema.json")


class VerificationReceiptError(Exception):
    """Raised when verification receipt validation fails."""


def canonical_json(value: Dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_receipt_hash(receipt: Dict[str, Any]) -> str:
    material = copy.deepcopy(receipt)
    material.pop("receipt_hash", None)
    return sha256_text(canonical_json(material))


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise VerificationReceiptError(f"INPUT_NOT_FOUND: {path}")

    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise VerificationReceiptError(f"JSON_INVALID: {exc}") from exc

    if not isinstance(value, dict):
        raise VerificationReceiptError("INPUT_MUST_BE_JSON_OBJECT")

    return value


def load_schema(path: Path = RECEIPT_SCHEMA_PATH) -> Dict[str, Any]:
    schema = load_json(path)
    Draft202012Validator.check_schema(schema)
    return schema


def check_schema(receipt: Dict[str, Any], schema: Dict[str, Any]) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(receipt), key=lambda error: error.path)

    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.path) or "<root>"
        raise VerificationReceiptError(f"RECEIPT_SCHEMA_INVALID at {location}: {first.message}")


def verify_receipt(receipt: Dict[str, Any], schema: Dict[str, Any]) -> None:
    check_schema(receipt, schema)

    expected_hash = compute_receipt_hash(receipt)
    actual_hash = receipt.get("receipt_hash")

    if actual_hash != expected_hash:
        raise VerificationReceiptError(
            f"RECEIPT_HASH_MISMATCH: expected {expected_hash}, got {actual_hash}"
        )

    overall_status = receipt["overall_status"]
    failure_reasons = receipt["failure_reasons"]

    if overall_status == "PASS" and failure_reasons:
        raise VerificationReceiptError("PASS_RECEIPT_HAS_FAILURE_REASONS")

    if overall_status == "FAIL" and not failure_reasons:
        raise VerificationReceiptError("FAIL_RECEIPT_MISSING_FAILURE_REASONS")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify a v0.6 GCR verification receipt.")
    parser.add_argument("input", help="Verification receipt JSON file.")
    parser.add_argument(
        "--schema",
        default=str(RECEIPT_SCHEMA_PATH),
        help="Path to verification receipt schema.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        schema = load_schema(Path(args.schema))
        receipt = load_json(Path(args.input))
        verify_receipt(receipt, schema)

        print("VERIFICATION RECEIPT VERIFY PASS")
        print(f"receipt_id: {receipt['receipt_id']}")
        print(f"bundle_id: {receipt['bundle_subject']['bundle_id']}")
        print(f"overall_status: {receipt['overall_status']}")
        print(f"receipt_hash: {receipt['receipt_hash']}")
        return 0

    except Exception as exc:
        print(f"VERIFICATION RECEIPT VERIFY FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
