#!/usr/bin/env python3
"""
verify_approval_token.py

Local verifier for approval_token.v0.3 records.

This verifier checks:
- approval token schema validity
- approval_token_hash integrity

It does not bind approval tokens to decision envelopes yet.
That binding is intentionally reserved for a later v0.3 step.
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


SCHEMA_PATH = Path("schemas/approval_token_v0.3.schema.json")


class ApprovalTokenVerificationError(Exception):
    """Raised when approval token verification fails."""


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
        raise ApprovalTokenVerificationError(f"INPUT_NOT_FOUND: {path}")

    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ApprovalTokenVerificationError(f"JSON_INVALID: {exc}") from exc

    if not isinstance(value, dict):
        raise ApprovalTokenVerificationError("INPUT_MUST_BE_JSON_OBJECT")

    return value


def load_schema(schema_path: Path = SCHEMA_PATH) -> Dict[str, Any]:
    if not schema_path.exists():
        raise ApprovalTokenVerificationError(f"SCHEMA_NOT_FOUND: {schema_path}")

    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    return schema


def check_schema(token: Dict[str, Any], schema: Dict[str, Any]) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(token), key=lambda error: error.path)

    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.path) or "<root>"
        raise ApprovalTokenVerificationError(
            f"SCHEMA_INVALID at {location}: {first.message}"
        )


def verify_approval_token(token: Dict[str, Any], schema: Dict[str, Any]) -> None:
    check_schema(token, schema)

    expected_hash = compute_approval_token_hash(token)
    actual_hash = token.get("approval_token_hash")

    if actual_hash != expected_hash:
        raise ApprovalTokenVerificationError(
            f"APPROVAL_TOKEN_HASH_MISMATCH: expected {expected_hash}, got {actual_hash}"
        )


def write_token(path: Path, token: Dict[str, Any]) -> None:
    payload = json.dumps(token, indent=2, sort_keys=True) + "\n"
    path.write_text(payload, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify approval_token.v0.3 schema and hash integrity."
    )
    parser.add_argument("input", help="Approval token JSON file.")
    parser.add_argument(
        "--schema",
        default=str(SCHEMA_PATH),
        help="Path to approval token schema.",
    )
    parser.add_argument(
        "--write-hash",
        action="store_true",
        help="Rewrite approval_token_hash with the computed value before verification.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    input_path = Path(args.input)

    try:
        schema = load_schema(Path(args.schema))
        token = load_json(input_path)

        if args.write_hash:
            token["approval_token_hash"] = compute_approval_token_hash(token)
            write_token(input_path, token)
            print(f"APPROVAL TOKEN HASH WRITTEN: {input_path}")

        verify_approval_token(token, schema)

        print("APPROVAL TOKEN VERIFY PASS")
        print(f"approval_token_id: {token['approval_token_id']}")
        print(f"approval_token_hash: {token['approval_token_hash']}")
        return 0

    except ApprovalTokenVerificationError as exc:
        print(f"APPROVAL TOKEN VERIFY FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())