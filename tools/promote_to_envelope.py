#!/usr/bin/env python3
"""
promote_to_envelope.py

Promotes runtime governance events into decision_envelope.v0.1 records.

A governance event is what the runtime emits.
A decision envelope is what the governance layer is willing to defend.
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
from typing import Any, Dict, List, Optional

from jsonschema import Draft202012Validator, FormatChecker

from verify_envelope_chain import (
    GENESIS_HASH,
    VerificationError,
    compute_record_hash,
    load_schema,
    verify_envelopes,
)


SCHEMA_VERSION = "decision_envelope_v0.1"
DEFAULT_RUNTIME_ID = "local-reference-runtime-v0.1"
DEFAULT_AGENT_ID = "reference-agent"
DEFAULT_POLICY_VERSION = "policy-v0.1-local-demo"
DEFAULT_DECISION_ENGINE_VERSION = "drf-omtir-decision-engine-v0.1"
DEFAULT_VERIFIER_VERSION = "decision-envelope-verifier-v0.1"
DEFAULT_TAMPER_EVIDENCE_MODE = "UNKEYED_HASH_CHAIN"


class PromotionError(Exception):
    """Raised when event promotion fails."""


def sha256(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json(obj: Dict[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def get_path(obj: Dict[str, Any], dotted_path: str, default: Any = None) -> Any:
    current: Any = obj
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current


def require_path(obj: Dict[str, Any], dotted_path: str) -> Any:
    value = get_path(obj, dotted_path)
    if value is None:
        raise PromotionError(f"PROMOTION_FAILED_MISSING_REQUIRED_FIELD: {dotted_path}")
    return value


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_events(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise PromotionError(f"PROMOTION_FAILED_MISSING_REQUIRED_FIELD: input not found: {path}")

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise PromotionError("PROMOTION_FAILED_MISSING_REQUIRED_FIELD: input is empty")

    if path.suffix.lower() == ".jsonl":
        events = [json.loads(line) for line in text.splitlines() if line.strip()]
        if not events:
            raise PromotionError("PROMOTION_FAILED_MISSING_REQUIRED_FIELD: no events in jsonl")
        return events

    data = json.loads(text)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]

    raise PromotionError("PROMOTION_FAILED_SCHEMA_INVALID: input must be object, array, or jsonl")


def stable_proposal_id(event: Dict[str, Any], proposed_action: str, previous_record_hash: str) -> str:
    existing = get_path(event, "proposal_id") or get_path(event, "proposal.id")
    if existing:
        return str(existing)

    seed = canonical_json(
        {
            "proposed_action": proposed_action,
            "previous_record_hash": previous_record_hash,
            "wal_sequence": get_path(event, "wal.sequence"),
        }
    )
    return str(uuid.uuid5(uuid.NAMESPACE_URL, seed))


def format_value(value: Any) -> str:
    return repr(value)


def make_proposed_action(event: Dict[str, Any]) -> str:
    tool_name = require_path(event, "tool_call.name")
    arguments = get_path(event, "tool_call.arguments", {})

    if not isinstance(arguments, dict):
        raise PromotionError("PROMOTION_FAILED_SCHEMA_INVALID: tool_call.arguments must be an object")

    if not arguments:
        return f"{tool_name}()"

    rendered = ", ".join(f"{key}={format_value(arguments[key])}" for key in sorted(arguments))
    return f"{tool_name}({rendered})"


def make_normalized_action(event: Dict[str, Any]) -> str:
    tool_name = require_path(event, "tool_call.name")
    arguments = get_path(event, "tool_call.arguments", {})

    if not isinstance(arguments, dict):
        raise PromotionError("PROMOTION_FAILED_SCHEMA_INVALID: tool_call.arguments must be an object")

    if "path" in arguments:
        return f"{tool_name}:{arguments['path']}"

    if not arguments:
        return f"{tool_name}:"

    return f"{tool_name}:{canonical_json(arguments)}"


def classify_consequence(event: Dict[str, Any], normalized_action: str) -> Dict[str, str]:
    tool_name = require_path(event, "tool_call.name")
    path = get_path(event, "tool_call.arguments.path", "")

    secret_paths = {".env", "secrets.env", ".env.local", ".env.production"}
    secret_markers = ["secret", "credential", "token", "private_key", "password"]

    if tool_name == "read_file" and (
        path in secret_paths or any(marker in str(path).lower() for marker in secret_markers)
    ):
        return {
            "consequence_class": "CREDENTIAL_EXPOSURE",
            "risk_level": "CRITICAL",
            "reversibility": "IRREVERSIBLE",
            "blast_radius": "ORGANIZATION",
            "authority_required": "ADMIN",
            "evidence_required": "HUMAN_APPROVAL",
            "classification_method": "DETERMINISTIC_RULE",
            "classification_confidence": "HIGH",
        }

    if tool_name == "read_file":
        return {
            "consequence_class": "READ_ONLY_ACCESS",
            "risk_level": "LOW",
            "reversibility": "REVERSIBLE",
            "blast_radius": "LOCAL",
            "authority_required": "NONE",
            "evidence_required": "NONE",
            "classification_method": "DETERMINISTIC_RULE",
            "classification_confidence": "HIGH",
        }

    if tool_name == "write_file" and ".github/workflows" in str(path):
        return {
            "consequence_class": "PRODUCTION_STATE_CHANGE",
            "risk_level": "HIGH",
            "reversibility": "PARTIALLY_REVERSIBLE",
            "blast_radius": "ORGANIZATION",
            "authority_required": "REVIEWER",
            "evidence_required": "HUMAN_APPROVAL",
            "classification_method": "DETERMINISTIC_RULE",
            "classification_confidence": "HIGH",
        }

    if tool_name == "delete_file":
        return {
            "consequence_class": "IRREVERSIBLE_DELETE",
            "risk_level": "HIGH",
            "reversibility": "IRREVERSIBLE",
            "blast_radius": "LOCAL",
            "authority_required": "REVIEWER",
            "evidence_required": "HUMAN_APPROVAL",
            "classification_method": "DETERMINISTIC_RULE",
            "classification_confidence": "HIGH",
        }

    return {
        "consequence_class": "UNKNOWN",
        "risk_level": "HIGH",
        "reversibility": "UNKNOWN",
        "blast_radius": "UNKNOWN",
        "authority_required": "REVIEWER",
        "evidence_required": "HUMAN_APPROVAL",
        "classification_method": "FALLBACK",
        "classification_confidence": "UNCERTAIN",
    }


def map_decision(event: Dict[str, Any]) -> str:
    raw = require_path(event, "drf_decision.decision")
    decision = str(raw).upper()

    aliases = {
        "SUCCEEDED": "ALLOW",
        "ALLOWED": "ALLOW",
        "BLOCK": "DENY",
        "BLOCKED": "DENY",
        "DENIED": "DENY",
        "REVIEW": "REQUEST_REVIEW",
        "PENDING_REVIEW": "REQUEST_REVIEW",
        "QUARANTINED": "QUARANTINE",
    }

    decision = aliases.get(decision, decision)

    allowed = {"ALLOW", "DENY", "REQUEST_REVIEW", "QUARANTINE"}
    if decision not in allowed:
        raise PromotionError(f"PROMOTION_FAILED_SCHEMA_INVALID: unsupported decision {raw}")

    return decision


def map_decision_basis(event: Dict[str, Any], decision: str) -> str:
    raw = get_path(event, "drf_decision.basis")
    if raw:
        basis = str(raw).upper()
        allowed = {
            "POLICY_RULE",
            "REVIEWER_APPROVAL",
            "CONSERVATIVE_FALLBACK",
            "EVIDENCE_FAILURE",
            "SYSTEM_GUARD",
        }
        if basis in allowed:
            return basis

    if decision == "QUARANTINE":
        return "CONSERVATIVE_FALLBACK"

    return "POLICY_RULE"


def map_review_status(event: Dict[str, Any], decision: str) -> str:
    raw = get_path(event, "review.status")
    if raw:
        status = str(raw).upper()
        allowed = {"NOT_REQUIRED", "PENDING", "APPROVED", "REJECTED", "EXPIRED", "INVALIDATED"}
        if status in allowed:
            return status
        raise PromotionError(f"PROMOTION_FAILED_SCHEMA_INVALID: unsupported review status {raw}")

    if decision == "REQUEST_REVIEW":
        return "PENDING"

    return "NOT_REQUIRED"


def map_execution_and_outcome(event: Dict[str, Any], decision: str) -> Dict[str, str]:
    explicit_execution = get_path(event, "execution.status")
    explicit_outcome = get_path(event, "outcome.status")
    explicit_boundary = get_path(event, "execution.boundary")

    if explicit_execution and explicit_outcome and explicit_boundary:
        return {
            "execution_boundary": str(explicit_boundary).upper(),
            "execution_status": str(explicit_execution).upper(),
            "outcome_status": str(explicit_outcome).upper(),
        }

    if decision == "ALLOW":
        return {
            "execution_boundary": "LOCAL_STUB",
            "execution_status": "EXECUTED",
            "outcome_status": "SUCCESS",
        }

    if decision == "DENY":
        return {
            "execution_boundary": "NOT_EXECUTED",
            "execution_status": "BLOCKED",
            "outcome_status": "BLOCKED",
        }

    if decision == "REQUEST_REVIEW":
        return {
            "execution_boundary": "NOT_EXECUTED",
            "execution_status": "PENDING",
            "outcome_status": "PENDING_REVIEW",
        }

    return {
        "execution_boundary": "NOT_EXECUTED",
        "execution_status": "NOT_EXECUTED",
        "outcome_status": "QUARANTINED",
    }


def map_evidence_references(event: Dict[str, Any]) -> List[str]:
    refs = get_path(event, "evidence_references")
    if isinstance(refs, list):
        return [str(ref) for ref in refs]

    omtir = get_path(event, "omtir_evidence", {})
    if isinstance(omtir, dict):
        return [f"evidence:{key}" for key in sorted(omtir.keys())]

    return []


def get_policy_hash(event: Dict[str, Any]) -> str:
    value = get_path(event, "policy_hash") or get_path(event, "policy.hash")
    if value:
        return str(value)

    return sha256("policy:v0.1:local-demo")


def get_policy_version(event: Dict[str, Any]) -> str:
    return str(get_path(event, "policy_version") or get_path(event, "policy.version") or DEFAULT_POLICY_VERSION)


def validate_promoted_envelope(envelope: Dict[str, Any], schema: Dict[str, Any]) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(envelope), key=lambda e: e.path)
    if errors:
        first = errors[0]
        location = ".".join(str(p) for p in first.path) or "<root>"
        raise PromotionError(f"PROMOTION_FAILED_SCHEMA_INVALID at {location}: {first.message}")


def promote_event(
    event: Dict[str, Any],
    *,
    previous_record_hash: str,
    schema: Dict[str, Any],
) -> Dict[str, Any]:
    proposed_action = make_proposed_action(event)
    normalized_action = make_normalized_action(event)
    decision = map_decision(event)
    review_status = map_review_status(event, decision)
    execution = map_execution_and_outcome(event, decision)

    envelope: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "created_at": str(get_path(event, "created_at") or get_path(event, "timestamp") or utc_now()),
        "runtime_id": str(
            get_path(event, "runtime.runtime_id")
            or get_path(event, "runtime.id")
            or get_path(event, "runtime.gateway_version")
            or DEFAULT_RUNTIME_ID
        ),
        "proposal_id": stable_proposal_id(event, proposed_action, previous_record_hash),
        "proposal_hash": sha256(proposed_action),
        "agent_id": str(get_path(event, "agent_id") or get_path(event, "agent.id") or DEFAULT_AGENT_ID),
        "agent_identity_manifest_hash": get_path(event, "agent_identity_manifest_hash"),
        "proposed_action": proposed_action,
        "normalized_action": normalized_action,
        "normalized_action_hash": sha256(normalized_action),
        "consequence_classification": classify_consequence(event, normalized_action),
        "policy_hash": get_policy_hash(event),
        "policy_version": get_policy_version(event),
        "policy_rule_id": get_path(event, "policy_rule_id") or get_path(event, "drf_decision.rule_id"),
        "decision_engine_version": str(
            get_path(event, "decision_engine_version") or DEFAULT_DECISION_ENGINE_VERSION
        ),
        "evidence_manifest_hash": get_path(event, "evidence_manifest_hash"),
        "evidence_references": map_evidence_references(event),
        "state_witness_hash": get_path(event, "state_witness_hash"),
        "decision": decision,
        "decision_basis": map_decision_basis(event, decision),
        "decision_reason": str(get_path(event, "drf_decision.reason") or "No decision reason provided."),
        "review_status": review_status,
        "reviewer_authority_id": get_path(event, "review.reviewer_authority_id"),
        "approval_scope": get_path(event, "review.approval_scope"),
        "approval_expiry": get_path(event, "review.approval_expiry"),
        "execution_boundary": execution["execution_boundary"],
        "execution_status": execution["execution_status"],
        "outcome_status": execution["outcome_status"],
        "outcome_hash": get_path(event, "outcome_hash"),
        "failure_mode": get_path(event, "failure_mode"),
        "tamper_evidence_mode": str(
            get_path(event, "tamper_evidence_mode") or DEFAULT_TAMPER_EVIDENCE_MODE
        ),
        "key_id": get_path(event, "key_id"),
        "previous_record_hash": previous_record_hash,
        "verifier_version": str(get_path(event, "verifier_version") or DEFAULT_VERIFIER_VERSION),
    }

    envelope["record_hash"] = compute_record_hash(envelope)

    validate_promoted_envelope(envelope, schema)

    try:
        verify_envelopes([envelope], schema)
    except VerificationError:
        # Single-envelope verification expects genesis chain only. For non-genesis
        # records, full-chain verification is performed after all records are promoted.
        pass

    return envelope


def promote_events(events: List[Dict[str, Any]], schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    envelopes: List[Dict[str, Any]] = []
    previous = GENESIS_HASH

    for event in events:
        envelope = promote_event(event, previous_record_hash=previous, schema=schema)
        envelopes.append(envelope)
        previous = envelope["record_hash"]

    try:
        verify_envelopes(envelopes, schema)
    except VerificationError as exc:
        raise PromotionError(f"PROMOTION_FAILED_CONSTITUTIONAL_VIOLATION: {exc}") from exc

    return envelopes


def write_envelopes(envelopes: List[Dict[str, Any]], output_path: Path) -> None:
    if output_path.suffix.lower() == ".jsonl":
        output_path.write_text(
            "\n".join(json.dumps(env, ensure_ascii=False) for env in envelopes) + "\n",
            encoding="utf-8",
        )
        return

    output_path.write_text(json.dumps(envelopes, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Promote governance_event.v0.1 records into decision_envelope.v0.1 records."
    )
    parser.add_argument("input", help="Input governance event JSON or JSONL file.")
    parser.add_argument("-o", "--output", required=True, help="Output envelope JSON or JSONL file.")
    parser.add_argument("--schema", default=str(Path("schemas/decision_envelope_v0.1.schema.json")))
    parser.add_argument("--verify", action="store_true", help="Verify promoted envelope chain before exit.")

    args = parser.parse_args()

    try:
        schema = load_schema(Path(args.schema))
        events = load_events(Path(args.input))
        envelopes = promote_events(events, schema)
        write_envelopes(envelopes, Path(args.output))

        print(f"PROMOTION PASS: {len(envelopes)} envelope(s) written to {args.output}")

        if args.verify:
            verify_envelopes(envelopes, schema)
            print("PROMOTION VERIFY PASS: promoted envelope chain verifies")

        return 0

    except (PromotionError, VerificationError) as exc:
        print(f"PROMOTION FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())