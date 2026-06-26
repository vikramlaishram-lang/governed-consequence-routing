import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


SCHEMA_PATH = Path("schemas/approval_token_v0.3.schema.json")
EXAMPLE_PATH = Path("examples/reviewer_authority/approval_token.v0.3.json")


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def validator():
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def errors_for(token):
    return list(validator().iter_errors(token))


def test_approval_token_example_validates():
    token = load_json(EXAMPLE_PATH)

    errors = errors_for(token)

    assert errors == []


def test_approval_token_requires_proposal_hash():
    token = load_json(EXAMPLE_PATH)
    del token["proposal_hash"]

    errors = errors_for(token)

    assert errors
    assert any(error.validator == "required" for error in errors)


def test_approval_token_rejects_bad_hash_format():
    token = load_json(EXAMPLE_PATH)
    token["approval_token_hash"] = "not-a-sha256-hash"

    errors = errors_for(token)

    assert errors


def test_approval_token_rejects_unknown_approval_decision():
    token = load_json(EXAMPLE_PATH)
    token["approval_decision"] = "MAYBE"

    errors = errors_for(token)

    assert errors
    assert any("approval_decision" in [str(part) for part in error.path] for error in errors)


def test_approval_token_rejects_unsupported_consequence_class():
    token = load_json(EXAMPLE_PATH)
    token["consequence_classification"]["consequence_class"] = "UNSUPPORTED_CLASS"

    errors = errors_for(token)

    assert errors


def test_approval_token_rejects_duplicate_approved_decisions():
    token = load_json(EXAMPLE_PATH)
    token["approval_scope"]["approved_decisions"] = [
        "REQUEST_REVIEW",
        "REQUEST_REVIEW",
    ]

    errors = errors_for(token)

    assert errors
    assert any(error.validator == "uniqueItems" for error in errors)


def test_approval_token_rejects_additional_properties():
    token = load_json(EXAMPLE_PATH)
    token["unexpected_field"] = "not allowed"

    errors = errors_for(token)

    assert errors
    assert any(error.validator == "additionalProperties" for error in errors)