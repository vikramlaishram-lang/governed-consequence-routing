import json
from pathlib import Path

from jsonschema import Draft202012Validator


SCHEMA_PATH = Path("schemas/decision_envelope_v0.1.schema.json")


def test_schema_loads_and_is_valid_draft_2020_12():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)


def test_schema_requires_locked_fields():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    required = set(schema["required"])

    expected = {
        "schema_version",
        "created_at",
        "runtime_id",
        "proposal_id",
        "proposal_hash",
        "agent_id",
        "proposed_action",
        "normalized_action",
        "normalized_action_hash",
        "consequence_classification",
        "policy_hash",
        "policy_version",
        "decision_engine_version",
        "decision",
        "decision_basis",
        "decision_reason",
        "review_status",
        "execution_boundary",
        "execution_status",
        "outcome_status",
        "evidence_references",
        "tamper_evidence_mode",
        "previous_record_hash",
        "record_hash",
        "verifier_version",
    }

    assert expected.issubset(required)


def test_schema_rejects_additional_root_properties():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert schema["additionalProperties"] is False


def test_consequence_classification_rejects_additional_properties():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    classification = schema["properties"]["consequence_classification"]
    assert classification["additionalProperties"] is False


def test_source_event_hash_is_not_in_v0_1_schema():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert "source_event_hash" not in schema["properties"]
    assert "source_event_hash" not in schema["required"]