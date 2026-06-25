#!/usr/bin/env python3
"""
verify_envelope_chain.py

Independent verifier for decision_envelope.v0.1 records.

The verifier does not trust the promoter.

It checks:
- schema validity
- proposal_hash
- normalized_action_hash
- record_hash
- previous_record_hash chain linkage
- constitutional invariants
- mutation detection
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from jsonschema import Draft202012Validator, FormatChecker


GENESIS_HASH = "0" * 64
SCHEMA_PATH = Path("schemas/decision_envelope_v0.1.schema.json")


class VerificationError(Exception):
    """Raised when verification fails."""


def sha256(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json(obj: Dict[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_record_hash(envelope: Dict[str, Any]) -> str:
    obj = copy.deepcopy(envelope)
    obj.pop("record_hash", None)
    return sha256(canonical_json(obj))


def load_schema(schema_path: Path = SCHEMA_PATH) -> Dict[str, Any]:
    if not schema_path.exists():
        raise VerificationError(f"SCHEMA_NOT_FOUND: {schema_path}")

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return schema


def load_envelopes(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise VerificationError(f"INPUT_NOT_FOUND: {path}")

    if path.is_dir():
        json_files = sorted(path.glob("*.json"))
        if not json_files:
            raise VerificationError(f"NO_JSON_FILES_FOUND: {path}")
        return [json.loads(p.read_text(encoding="utf-8")) for p in json_files]

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise VerificationError(f"EMPTY_INPUT: {path}")

    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]

    data = json.loads(text)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]

    raise VerificationError("INPUT_MUST_BE_JSON_OBJECT_ARRAY_OR_JSONL")


def check_schema(envelope: Dict[str, Any], validator: Draft202012Validator) -> None:
    errors = sorted(validator.iter_errors(envelope), key=lambda e: e.path)
    if errors:
        first = errors[0]
        location = ".".join(str(p) for p in first.path) or "<root>"
        raise VerificationError(f"SCHEMA_INVALID at {location}: {first.message}")


def check_hashes(envelope: Dict[str, Any]) -> None:
    expected_proposal_hash = sha256(envelope["proposed_action"])
    if envelope["proposal_hash"] != expected_proposal_hash:
        raise VerificationError("PROPOSAL_HASH_MISMATCH")

    expected_normalized_hash = sha256(envelope["normalized_action"])
    if envelope["normalized_action_hash"] != expected_normalized_hash:
        raise VerificationError("NORMALIZED_ACTION_HASH_MISMATCH")

    expected_record_hash = compute_record_hash(envelope)
    if envelope["record_hash"] != expected_record_hash:
        raise VerificationError("RECORD_HASH_MISMATCH")


def check_chain(envelopes: List[Dict[str, Any]]) -> None:
    expected_previous = GENESIS_HASH

    for index, envelope in enumerate(envelopes):
        actual_previous = envelope["previous_record_hash"]
        if actual_previous != expected_previous:
            raise VerificationError(
                f"CHAIN_BREAK at index {index}: expected {expected_previous}, got {actual_previous}"
            )
        expected_previous = envelope["record_hash"]


def check_constitutional_invariants(envelope: Dict[str, Any]) -> None:
    decision = envelope["decision"]
    classification = envelope["consequence_classification"]
    consequence_class = classification["consequence_class"]
    confidence = classification["classification_confidence"]
    execution_status = envelope["execution_status"]
    review_status = envelope["review_status"]
    reviewer_authority_id = envelope.get("reviewer_authority_id")

    if consequence_class == "UNKNOWN" and decision == "ALLOW":
        raise VerificationError("UNKNOWN_ALLOW_CONSTITUTIONAL_VIOLATION")

    if confidence in {"LOW", "UNCERTAIN"} and decision == "ALLOW":
        raise VerificationError("UNCERTAIN_ALLOW_CONSTITUTIONAL_VIOLATION")

    if decision == "DENY" and execution_status not in {"BLOCKED", "NOT_EXECUTED"}:
        raise VerificationError("DENY_EXECUTION_INVARIANT_VIOLATED")

    if decision == "REQUEST_REVIEW" and execution_status == "EXECUTED":
        if review_status != "APPROVED" or not reviewer_authority_id:
            raise VerificationError("REQUEST_REVIEW_EXECUTED_WITHOUT_VALID_APPROVAL")

    if review_status in {"APPROVED", "REJECTED"} and not reviewer_authority_id:
        raise VerificationError("REVIEW_DECISION_WITHOUT_REVIEWER_AUTHORITY")


def verify_envelopes(envelopes: List[Dict[str, Any]], schema: Dict[str, Any]) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    for envelope in envelopes:
        check_schema(envelope, validator)
        check_hashes(envelope)
        check_constitutional_invariants(envelope)

    check_chain(envelopes)


def mutate_envelope(envelope: Dict[str, Any], mutation_name: str) -> Dict[str, Any]:
    mutated = copy.deepcopy(envelope)

    if mutation_name == "proposed_action":
        mutated["proposed_action"] = mutated["proposed_action"] + " # tampered"
        return mutated

    if mutation_name == "normalized_action":
        mutated["normalized_action"] = mutated["normalized_action"] + ":tampered"
        return mutated

    if mutation_name == "decision":
        mutated["decision"] = "ALLOW" if mutated["decision"] != "ALLOW" else "DENY"
        return mutated

    if mutation_name == "previous_record_hash":
        mutated["previous_record_hash"] = "sha256:" + ("f" * 64)
        return mutated

    if mutation_name == "record_hash":
        mutated["record_hash"] = "sha256:" + ("e" * 64)
        return mutated

    if mutation_name == "classification_confidence":
        current = mutated["consequence_classification"]["classification_confidence"]
        mutated["consequence_classification"]["classification_confidence"] = (
            "LOW" if current != "LOW" else "HIGH"
        )
        return mutated

    if mutation_name == "consequence_class":
        current = mutated["consequence_classification"]["consequence_class"]
        mutated["consequence_classification"]["consequence_class"] = (
            "UNKNOWN" if current != "UNKNOWN" else "READ_ONLY_ACCESS"
        )
        return mutated

    if mutation_name == "execution_status":
        mutated["execution_status"] = (
            "EXECUTED" if mutated["execution_status"] != "EXECUTED" else "BLOCKED"
        )
        return mutated

    raise ValueError(f"Unknown mutation: {mutation_name}")


def run_mutation_checks(envelopes: List[Dict[str, Any]], schema: Dict[str, Any]) -> List[Tuple[str, bool, str]]:
    mutation_names = [
        "proposed_action",
        "normalized_action",
        "decision",
        "previous_record_hash",
        "record_hash",
        "classification_confidence",
        "consequence_class",
        "execution_status",
    ]

    results: List[Tuple[str, bool, str]] = []

    for mutation_name in mutation_names:
        mutated_chain = copy.deepcopy(envelopes)
        target_index = 0 if mutation_name != "previous_record_hash" else min(1, len(mutated_chain) - 1)
        mutated_chain[target_index] = mutate_envelope(mutated_chain[target_index], mutation_name)

        try:
            verify_envelopes(mutated_chain, schema)
        except VerificationError as exc:
            results.append((mutation_name, True, str(exc)))
        else:
            results.append((mutation_name, False, "MUTATION_SURVIVED"))

    return results


def print_mutation_results(results: Iterable[Tuple[str, bool, str]], verbose: bool = False) -> bool:
    all_detected = True

    labels = {
        "proposed_action": "proposed_action mutation",
        "normalized_action": "normalized_action mutation",
        "decision": "decision mutation",
        "previous_record_hash": "previous_record_hash mutation",
        "record_hash": "record_hash mutation",
        "classification_confidence": "classification_confidence mutation",
        "consequence_class": "consequence_class mutation",
        "execution_status": "execution_status mutation",
    }

    for name, detected, reason in results:
        label = labels[name]
        status = "DETECTED" if detected else "SURVIVED"
        print(f"{label + ':':38} {status}")
        if verbose:
            print(f"  reason: {reason}")
        if not detected:
            all_detected = False

    return all_detected


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify decision_envelope.v0.1 chain integrity.")
    parser.add_argument("input", help="Envelope JSON file, JSONL file, or directory of JSON files.")
    parser.add_argument("--schema", default=str(SCHEMA_PATH), help="Path to decision envelope schema.")
    parser.add_argument("--mutate", action="store_true", help="Run mutation-detection checks.")
    parser.add_argument("--verbose", action="store_true", help="Print detailed verification reasons.")

    args = parser.parse_args()

    try:
        schema = load_schema(Path(args.schema))
        envelopes = load_envelopes(Path(args.input))
        verify_envelopes(envelopes, schema)

        print(f"VERIFIER PASS: {len(envelopes)} envelope(s) valid")

        if args.mutate:
            results = run_mutation_checks(envelopes, schema)
            all_detected = print_mutation_results(results, verbose=args.verbose)
            if not all_detected:
                print("VERIFIER FAIL: one or more mutations survived")
                return 1
            print("MUTATION CHECK PASS: all mutations detected")

        return 0

    except VerificationError as exc:
        print(f"VERIFIER FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
