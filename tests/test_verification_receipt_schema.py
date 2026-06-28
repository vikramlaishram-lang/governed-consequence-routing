import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


SCHEMA_PATH = Path("schemas/verification_receipt_v0.6.schema.json")
EXAMPLE_PATH = Path("examples/verification_receipt/verification_receipt.v0.6.json")


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def validator():
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def errors_for(receipt):
    return list(validator().iter_errors(receipt))


def test_verification_receipt_example_validates():
    receipt = load_json(EXAMPLE_PATH)

    errors = errors_for(receipt)

    assert errors == []


def test_verification_receipt_rejects_missing_required_field():
    receipt = load_json(EXAMPLE_PATH)
    del receipt["receipt_hash"]

    errors = errors_for(receipt)

    assert errors
    assert any(error.validator == "required" for error in errors)


def test_verification_receipt_rejects_bad_hash_format():
    receipt = load_json(EXAMPLE_PATH)
    receipt["receipt_hash"] = "not-a-sha256-hash"

    errors = errors_for(receipt)

    assert errors


def test_verification_receipt_rejects_additional_properties():
    receipt = load_json(EXAMPLE_PATH)
    receipt["unexpected_field"] = "not allowed"

    errors = errors_for(receipt)

    assert errors
    assert any(error.validator == "additionalProperties" for error in errors)
