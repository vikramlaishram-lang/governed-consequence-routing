#!/usr/bin/env python3
"""
verify_receipt_index.py

Verify a local v0.7 GCR verification receipt index.

The index verifies receipt membership and recorded receipt status. It does not
re-verify the receipts it indexes.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from jsonschema import Draft202012Validator, FormatChecker


INDEX_SCHEMA_PATH = Path("schemas/verification_receipt_index_v0.7.schema.json")


class ReceiptIndexVerificationError(Exception):
    """Raised when receipt index verification fails."""


def canonical_json(value: Dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_index_hash(index: Dict[str, Any]) -> str:
    material = copy.deepcopy(index)
    material.pop("index_hash", None)
    return sha256_text(canonical_json(material))


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise ReceiptIndexVerificationError(f"INPUT_NOT_FOUND: {path}")

    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ReceiptIndexVerificationError(f"JSON_INVALID: {exc}") from exc

    if not isinstance(value, dict):
        raise ReceiptIndexVerificationError("INPUT_MUST_BE_JSON_OBJECT")

    return value


def load_schema(path: Path = INDEX_SCHEMA_PATH) -> Dict[str, Any]:
    schema = load_json(path)
    Draft202012Validator.check_schema(schema)
    return schema


def check_schema(index: Dict[str, Any], schema: Dict[str, Any]) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(index), key=lambda error: error.path)

    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.path) or "<root>"
        raise ReceiptIndexVerificationError(
            f"RECEIPT_INDEX_SCHEMA_INVALID at {location}: {first.message}"
        )


def verify_index_hash(index: Dict[str, Any]) -> None:
    expected_hash = compute_index_hash(index)
    actual_hash = index.get("index_hash")

    if actual_hash != expected_hash:
        raise ReceiptIndexVerificationError(
            f"INDEX_HASH_MISMATCH: expected {expected_hash}, got {actual_hash}"
        )


def latest_verified_at(receipts: List[Dict[str, Any]]) -> str | None:
    if not receipts:
        return None

    return max(receipt["verified_at"] for receipt in receipts)


def verify_index(index: Dict[str, Any], schema: Dict[str, Any]) -> None:
    check_schema(index, schema)
    verify_index_hash(index)

    receipts = index["receipts"]

    if index["receipt_count"] != len(receipts):
        raise ReceiptIndexVerificationError(
            f"RECEIPT_COUNT_MISMATCH: expected {len(receipts)}, got {index['receipt_count']}"
        )

    status_counts = Counter(receipt["verification_status"] for receipt in receipts)

    for status in ["PASS", "FAIL"]:
        if index["status_counts"][status] != status_counts.get(status, 0):
            raise ReceiptIndexVerificationError(
                f"STATUS_COUNT_MISMATCH: {status} expected {status_counts.get(status, 0)}, got {index['status_counts'][status]}"
            )

    expected_latest = latest_verified_at(receipts)
    if index["latest_verification_time"] != expected_latest:
        raise ReceiptIndexVerificationError(
            f"LATEST_VERIFICATION_TIME_MISMATCH: expected {expected_latest}, got {index['latest_verification_time']}"
        )


def assert_mutation_detected(index: Dict[str, Any], mutation_name: str, mutate) -> None:
    mutated = copy.deepcopy(index)
    mutate(mutated)

    try:
        verify_index_hash(mutated)
    except ReceiptIndexVerificationError:
        return

    raise ReceiptIndexVerificationError(f"MUTATION_NOT_DETECTED: {mutation_name}")


def run_mutation_checks(index: Dict[str, Any], schema: Dict[str, Any]) -> None:
    verify_index(index, schema)

    if not index["receipts"]:
        raise ReceiptIndexVerificationError("MUTATION_CHECK_REQUIRES_RECEIPTS")

    assert_mutation_detected(
        index,
        "receipt_hash",
        lambda mutated: mutated["receipts"][0].update(
            {"receipt_hash": "sha256:" + ("9" * 64)}
        ),
    )
    assert_mutation_detected(
        index,
        "verification_status",
        lambda mutated: mutated["receipts"][0].update(
            {
                "verification_status": (
                    "FAIL"
                    if mutated["receipts"][0]["verification_status"] == "PASS"
                    else "PASS"
                )
            }
        ),
    )
    assert_mutation_detected(
        index,
        "verified_at",
        lambda mutated: mutated["receipts"][0].update(
            {"verified_at": "2026-06-28T23:59:59Z"}
        ),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify a v0.7 GCR receipt index.")
    parser.add_argument("input", help="Receipt index JSON file.")
    parser.add_argument(
        "--schema",
        default=str(INDEX_SCHEMA_PATH),
        help="Path to receipt index schema.",
    )
    parser.add_argument(
        "--mutate",
        action="store_true",
        help="Run mutation checks against a valid receipt index.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        schema = load_schema(Path(args.schema))
        index = load_json(Path(args.input))

        if args.mutate:
            run_mutation_checks(index, schema)
            print("MUTATION CHECK PASS")
            return 0

        verify_index(index, schema)
        print("RECEIPT INDEX VERIFY PASS")
        print(f"index_id: {index['index_id']}")
        print(f"receipt_count: {index['receipt_count']}")
        print(f"index_hash: {index['index_hash']}")
        return 0

    except Exception as exc:
        if args.mutate:
            print(f"MUTATION CHECK FAIL: {exc}", file=sys.stderr)
        else:
            print(f"RECEIPT INDEX VERIFY FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
