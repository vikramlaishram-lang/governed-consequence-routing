import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


SCHEMA_PATH = Path("schemas/verification_bundle_v0.5.schema.json")
EXAMPLE_PATH = Path("examples/verification_bundle/full_gcr_bundle.v0.5.json")


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def validator():
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def errors_for(bundle):
    return list(validator().iter_errors(bundle))


def test_verification_bundle_example_validates():
    bundle = load_json(EXAMPLE_PATH)

    errors = errors_for(bundle)

    assert errors == []


def test_verification_bundle_rejects_unknown_bundle_type():
    bundle = load_json(EXAMPLE_PATH)
    bundle["bundle_type"] = "UNSUPPORTED_BUNDLE"

    errors = errors_for(bundle)

    assert errors


def test_verification_bundle_requires_artifact_hashes():
    bundle = load_json(EXAMPLE_PATH)
    del bundle["artifact_hashes"]["evidence_manifest_hash"]

    errors = errors_for(bundle)

    assert errors
    assert any(error.validator == "required" for error in errors)


def test_verification_bundle_rejects_additional_properties():
    bundle = load_json(EXAMPLE_PATH)
    bundle["unexpected_field"] = "not allowed"

    errors = errors_for(bundle)

    assert errors
    assert any(error.validator == "additionalProperties" for error in errors)
