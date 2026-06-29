#!/usr/bin/env python3
"""
capture_runtime_proposal.py

Capture a simulated AI-agent proposal as a governed proposal record.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from jsonschema import Draft202012Validator, FormatChecker


SCHEMA_PATH = Path("schemas/runtime_proposal_v0.9.schema.json")
SCHEMA_VERSION = "runtime_proposal_v0.9"
DEFAULT_SOURCE_TYPE = "SIMULATED_AGENT"
DEFAULT_SOURCE_ID = "local-simulated-proposal"
DEFAULT_CREATED_AT = "2026-06-29T00:00:00Z"
DEFAULT_PROPOSAL_ID = "99999999-9999-4999-8999-999999999999"

RISK_ORDER = {
    "UNKNOWN": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}

PROOF_BOUNDARY = {
    "proves": [
        "v0.9 proves that a live or simulated AI-agent proposal can be captured before execution and converted into a governed proposal record without granting execution authority.",
        "The runtime proposal hook captures, normalizes, classifies, and records a proposal before execution.",
        "The runtime proposal hook records execution_status as NOT_EXECUTED.",
    ],
    "does_not_prove": [
        "execution authority",
        "authorization",
        "tool execution",
        "external system calls",
        "production custody",
        "legal admissibility",
        "regulatory compliance",
        "clinical safety",
        "financial advice suitability",
        "enterprise compliance",
        "SSO-backed identity",
        "production identity",
        "non-repudiation",
        "correctness of the underlying AI action",
        "real-world truth of evidence",
        "legal validity of approval",
        "safety of the original action",
        "that proposal capture equals approval",
        "that model output becomes authority",
        "that a captured proposal should execute",
    ],
}


class RuntimeProposalError(Exception):
    """Raised when runtime proposal capture or verification fails."""


def canonical_json(value: Dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def compute_record_hash(record: Dict[str, Any]) -> str:
    material = copy.deepcopy(record)
    material.pop("record_hash", None)
    return sha256_json(material)


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise RuntimeProposalError(f"INPUT_NOT_FOUND: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise RuntimeProposalError(f"JSON_INVALID: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeProposalError("INPUT_MUST_BE_JSON_OBJECT")
    return value


def load_schema(path: Path = SCHEMA_PATH) -> Dict[str, Any]:
    schema = load_json(path)
    Draft202012Validator.check_schema(schema)
    return schema


def validate_schema(record: Dict[str, Any], schema: Dict[str, Any]) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(record), key=lambda error: error.path)
    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.path) or "<root>"
        raise RuntimeProposalError(
            f"RUNTIME_PROPOSAL_SCHEMA_INVALID at {location}: {first.message}"
        )


def require_non_empty(value: str | None, field_name: str) -> str:
    if value is None or value == "":
        raise RuntimeProposalError(f"MISSING_REQUIRED_FIELD: {field_name}")
    return value


def choose_higher_risk(current: tuple[str, str], candidate: tuple[str, str]) -> tuple[str, str]:
    if RISK_ORDER[candidate[1]] > RISK_ORDER[current[1]]:
        return candidate
    return current


def classify_consequence(action_type: str, target: str | None) -> tuple[str, str]:
    action = action_type.lower()
    target_text = (target or "").lower()
    result = ("UNKNOWN", "UNKNOWN")

    if action == "read_file":
        result = choose_higher_risk(result, ("READ_ONLY_ACCESS", "LOW"))
    if action == "write_file":
        result = choose_higher_risk(result, ("FILE_WRITE", "MEDIUM"))
    if action == "delete_file":
        result = choose_higher_risk(result, ("FILE_DELETE", "HIGH"))
    if action in {"send_message", "external_request"}:
        result = choose_higher_risk(result, ("EXTERNAL_COMMUNICATION", "MEDIUM"))
    if action == "mutate_policy":
        result = choose_higher_risk(result, ("POLICY_MUTATION", "HIGH"))
    if action == "change_permission":
        result = choose_higher_risk(result, ("IDENTITY_OR_PERMISSION_CHANGE", "HIGH"))
    if any(marker in target_text for marker in [".env", "secret", "token", "key"]):
        result = choose_higher_risk(result, ("SECRET_ACCESS", "CRITICAL"))
    if any(marker in target_text for marker in ["deploy", "workflow", "production"]):
        result = choose_higher_risk(result, ("PRODUCTION_STATE_CHANGE", "HIGH"))

    return result


def normalize_consequence(
    action_type: str,
    target: str | None,
    intent: str,
) -> tuple[Dict[str, Any], str, str]:
    classification, risk = classify_consequence(action_type, target)
    normalized = {
        "consequence_summary": (
            f"{action_type} proposal for {target or 'unspecified target'}: {intent}"
        ),
        "consequence_type": classification,
        "normalized_target": target,
    }
    return normalized, classification, risk


def build_runtime_proposal(
    *,
    agent_id: str,
    action_type: str,
    target: str | None,
    intent: str,
    source_type: str = DEFAULT_SOURCE_TYPE,
    source_id: str = DEFAULT_SOURCE_ID,
    proposal_id: str | None = None,
    created_at: str | None = None,
) -> Dict[str, Any]:
    agent_id = require_non_empty(agent_id, "agent_id")
    action_type = require_non_empty(action_type, "action_type")
    intent = require_non_empty(intent, "intent")
    source_id = require_non_empty(source_id, "source_id")

    if source_type not in {"SIMULATED_AGENT", "LOCAL_FIXTURE", "TEST_HARNESS"}:
        raise RuntimeProposalError(f"INVALID_SOURCE_TYPE: {source_type}")

    if proposal_id is None:
        proposal_id = str(uuid.uuid4())
    if created_at is None:
        created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    proposed_action = {
        "action_type": action_type,
        "intent": intent,
        "target": target,
    }
    normalized, classification, risk = normalize_consequence(action_type, target, intent)

    record = {
        "agent_id": agent_id,
        "authorization_status": (
            "REQUIRES_GOVERNANCE" if risk in {"MEDIUM", "HIGH", "CRITICAL"} else "NOT_AUTHORIZED"
        ),
        "consequence_classification": classification,
        "consequence_risk": risk,
        "created_at": created_at,
        "execution_status": "NOT_EXECUTED",
        "normalized_consequence": normalized,
        "normalized_consequence_hash": sha256_json(normalized),
        "proof_boundary": PROOF_BOUNDARY,
        "proposal_id": proposal_id,
        "proposed_action": proposed_action,
        "proposed_action_hash": sha256_json(proposed_action),
        "record_hash": "sha256:" + ("0" * 64),
        "schema_version": SCHEMA_VERSION,
        "source": {
            "source_id": source_id,
            "source_type": source_type,
        },
    }
    record["record_hash"] = compute_record_hash(record)
    return record


def verify_runtime_proposal(record: Dict[str, Any], schema: Dict[str, Any]) -> None:
    validate_schema(record, schema)

    if record["proposed_action_hash"] != sha256_json(record["proposed_action"]):
        raise RuntimeProposalError("PROPOSED_ACTION_HASH_MISMATCH")
    if record["normalized_consequence_hash"] != sha256_json(record["normalized_consequence"]):
        raise RuntimeProposalError("NORMALIZED_CONSEQUENCE_HASH_MISMATCH")
    if record["record_hash"] != compute_record_hash(record):
        raise RuntimeProposalError("RECORD_HASH_MISMATCH")
    if record["execution_status"] != "NOT_EXECUTED":
        raise RuntimeProposalError("EXECUTION_STATUS_NOT_ALLOWED")
    if record["authorization_status"] == "AUTHORIZED":
        raise RuntimeProposalError("AUTHORIZATION_STATUS_NOT_ALLOWED")


def write_json(path: Path, value: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture a v0.9 runtime proposal.")
    parser.add_argument("--agent-id")
    parser.add_argument("--action-type")
    parser.add_argument("--target", default=None)
    parser.add_argument("--intent")
    parser.add_argument("--source-type", default=DEFAULT_SOURCE_TYPE)
    parser.add_argument("--source-id", default=DEFAULT_SOURCE_ID)
    parser.add_argument("--proposal-id", default=None)
    parser.add_argument("--created-at", default=None)
    parser.add_argument("--input-json", default=None)
    parser.add_argument("--output", default=None)
    parser.add_argument("--verify-only", default=None)
    return parser.parse_args()


def args_from_input(args: argparse.Namespace) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    if args.input_json:
        data = load_json(Path(args.input_json))

    return {
        "action_type": args.action_type if args.action_type is not None else data.get("action_type"),
        "agent_id": args.agent_id if args.agent_id is not None else data.get("agent_id"),
        "created_at": args.created_at if args.created_at is not None else data.get("created_at"),
        "intent": args.intent if args.intent is not None else data.get("intent"),
        "proposal_id": args.proposal_id if args.proposal_id is not None else data.get("proposal_id"),
        "source_id": args.source_id if args.source_id is not None else data.get("source_id", DEFAULT_SOURCE_ID),
        "source_type": args.source_type if args.source_type is not None else data.get("source_type", DEFAULT_SOURCE_TYPE),
        "target": args.target if args.target is not None else data.get("target"),
    }


def capture(args: argparse.Namespace) -> int:
    if not args.output:
        raise RuntimeProposalError("MISSING_REQUIRED_FIELD: output")

    schema = load_schema()
    build_args = args_from_input(args)
    record = build_runtime_proposal(**build_args)
    verify_runtime_proposal(record, schema)
    write_json(Path(args.output), record)

    print("PROPOSAL CAPTURED")
    print("CONSEQUENCE NORMALIZED")
    print("RUNTIME PROPOSAL RECORD CREATED")
    print("EXECUTION_STATUS: NOT_EXECUTED")
    print(f"AUTHORIZATION_STATUS: {record['authorization_status']}")
    return 0


def verify_only(path: Path) -> int:
    schema = load_schema()
    record = load_json(path)
    verify_runtime_proposal(record, schema)
    print("RUNTIME PROPOSAL VERIFY PASS")
    return 0


def main() -> int:
    args = parse_args()
    try:
        if args.verify_only:
            return verify_only(Path(args.verify_only))
        return capture(args)
    except Exception as exc:
        if args.verify_only:
            print(f"RUNTIME PROPOSAL VERIFY FAIL: {exc}", file=sys.stderr)
        else:
            print(f"RUNTIME PROPOSAL CAPTURE FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
