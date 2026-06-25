import copy
import json
from pathlib import Path

import pytest

from tools.verify_envelope_chain import (
    GENESIS_HASH,
    VerificationError,
    compute_record_hash,
    load_schema,
    verify_envelopes,
)


EXAMPLE_FILES = [
    Path("examples/allow_read_source_file.v0.1.json"),
    Path("examples/deny_read_env_file.v0.1.json"),
    Path("examples/request_review_modify_workflow.v0.1.json"),
]


def load_examples():
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in EXAMPLE_FILES
    ]


def test_valid_example_chain_passes_verifier():
    schema = load_schema()
    envelopes = load_examples()

    verify_envelopes(envelopes, schema)


def test_first_envelope_uses_genesis_hash():
    envelopes = load_examples()

    assert envelopes[0]["previous_record_hash"] == GENESIS_HASH


def test_tampered_proposed_action_fails():
    schema = load_schema()
    envelopes = load_examples()

    envelopes[0]["proposed_action"] = envelopes[0]["proposed_action"] + " # tampered"

    with pytest.raises(VerificationError, match="PROPOSAL_HASH_MISMATCH"):
        verify_envelopes(envelopes, schema)


def test_tampered_normalized_action_fails():
    schema = load_schema()
    envelopes = load_examples()

    envelopes[0]["normalized_action"] = envelopes[0]["normalized_action"] + ":tampered"

    with pytest.raises(VerificationError, match="NORMALIZED_ACTION_HASH_MISMATCH"):
        verify_envelopes(envelopes, schema)


def test_tampered_record_hash_fails():
    schema = load_schema()
    envelopes = load_examples()

    envelopes[0]["record_hash"] = "sha256:" + ("e" * 64)

    with pytest.raises(VerificationError, match="RECORD_HASH_MISMATCH"):
        verify_envelopes(envelopes, schema)


def test_broken_chain_fails():
    schema = load_schema()
    envelopes = load_examples()

    envelopes[1]["previous_record_hash"] = "sha256:" + ("f" * 64)
    envelopes[1]["record_hash"] = compute_record_hash(envelopes[1])

    with pytest.raises(VerificationError, match="CHAIN_BREAK"):
        verify_envelopes(envelopes, schema)


def test_unknown_allow_fails_even_if_record_hash_recomputed():
    schema = load_schema()
    envelopes = load_examples()

    mutated = copy.deepcopy(envelopes[0])
    mutated["decision"] = "ALLOW"
    mutated["consequence_classification"]["consequence_class"] = "UNKNOWN"
    mutated["record_hash"] = compute_record_hash(mutated)
    envelopes[0] = mutated

    with pytest.raises(VerificationError, match="UNKNOWN_ALLOW_CONSTITUTIONAL_VIOLATION"):
        verify_envelopes(envelopes, schema)


def test_uncertain_allow_fails_even_if_record_hash_recomputed():
    schema = load_schema()
    envelopes = load_examples()

    mutated = copy.deepcopy(envelopes[0])
    mutated["decision"] = "ALLOW"
    mutated["consequence_classification"]["classification_confidence"] = "UNCERTAIN"
    mutated["record_hash"] = compute_record_hash(mutated)
    envelopes[0] = mutated

    with pytest.raises(VerificationError, match="UNCERTAIN_ALLOW_CONSTITUTIONAL_VIOLATION"):
        verify_envelopes(envelopes, schema)


def test_deny_executed_fails_even_if_record_hash_recomputed():
    schema = load_schema()
    envelopes = load_examples()

    mutated = copy.deepcopy(envelopes[1])
    mutated["decision"] = "DENY"
    mutated["execution_status"] = "EXECUTED"
    mutated["record_hash"] = compute_record_hash(mutated)
    envelopes[1] = mutated

    with pytest.raises(VerificationError, match="DENY_EXECUTION_INVARIANT_VIOLATED"):
        verify_envelopes(envelopes, schema)


def test_request_review_executed_without_approval_fails_even_if_record_hash_recomputed():
    schema = load_schema()
    envelopes = load_examples()

    mutated = copy.deepcopy(envelopes[2])
    mutated["decision"] = "REQUEST_REVIEW"
    mutated["review_status"] = "PENDING"
    mutated["reviewer_authority_id"] = None
    mutated["execution_status"] = "EXECUTED"
    mutated["outcome_status"] = "SUCCESS"
    mutated["record_hash"] = compute_record_hash(mutated)
    envelopes[2] = mutated

    with pytest.raises(VerificationError, match="REQUEST_REVIEW_EXECUTED_WITHOUT_VALID_APPROVAL"):
        verify_envelopes(envelopes, schema)