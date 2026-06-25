import copy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


SCHEMA_PATH = Path("schemas/decision_envelope_v0.1.schema.json")

EXAMPLE_FILES = [
    Path("examples/allow_read_source_file.v0.1.json"),
    Path("examples/deny_read_env_file.v0.1.json"),
    Path("examples/request_review_modify_workflow.v0.1.json"),
]

GENESIS = "0" * 64


def sha256(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_record_hash(envelope: dict) -> str:
    without_record_hash = copy.deepcopy(envelope)
    without_record_hash.pop("record_hash", None)
    return sha256(canonical_json(without_record_hash))


def load_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_examples():
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in EXAMPLE_FILES
    ]


def test_examples_validate_against_schema():
    schema = load_schema()
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    for envelope in load_examples():
        validator.validate(envelope)


def test_examples_have_valid_proposal_hashes():
    for envelope in load_examples():
        assert envelope["proposal_hash"] == sha256(envelope["proposed_action"])


def test_examples_have_valid_normalized_action_hashes():
    for envelope in load_examples():
        assert envelope["normalized_action_hash"] == sha256(envelope["normalized_action"])


def test_examples_have_valid_record_hashes():
    for envelope in load_examples():
        assert envelope["record_hash"] == compute_record_hash(envelope)


def test_examples_form_valid_chain():
    envelopes = load_examples()

    assert envelopes[0]["previous_record_hash"] == GENESIS
    assert envelopes[1]["previous_record_hash"] == envelopes[0]["record_hash"]
    assert envelopes[2]["previous_record_hash"] == envelopes[1]["record_hash"]


def test_required_decision_sequence_is_present():
    envelopes = load_examples()

    assert envelopes[0]["decision"] == "ALLOW"
    assert envelopes[0]["consequence_classification"]["consequence_class"] == "READ_ONLY_ACCESS"

    assert envelopes[1]["decision"] == "DENY"
    assert envelopes[1]["consequence_classification"]["consequence_class"] == "CREDENTIAL_EXPOSURE"

    assert envelopes[2]["decision"] == "REQUEST_REVIEW"
    assert envelopes[2]["consequence_classification"]["consequence_class"] == "PRODUCTION_STATE_CHANGE"