import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


SCHEMA_PATH = Path("schemas/reviewer_authority_manifest_v0.3.schema.json")
EXAMPLE_PATH = Path("examples/reviewer_authority/manifest.v0.3.json")


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator():
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def errors_for(manifest):
    return list(validator().iter_errors(manifest))


def test_reviewer_authority_manifest_example_validates():
    manifest = load_json(EXAMPLE_PATH)

    errors = errors_for(manifest)

    assert errors == []


def test_reviewer_authority_manifest_requires_authority_scope():
    manifest = load_json(EXAMPLE_PATH)
    del manifest["authority_scope"]

    errors = errors_for(manifest)

    assert errors
    assert any(error.validator == "required" for error in errors)


def test_reviewer_authority_manifest_rejects_unknown_status():
    manifest = load_json(EXAMPLE_PATH)
    manifest["authority_status"] = "UNKNOWN_STATUS"

    errors = errors_for(manifest)

    assert errors
    assert any("authority_status" in [str(part) for part in error.path] for error in errors)


def test_reviewer_authority_manifest_rejects_unsupported_consequence_class():
    manifest = load_json(EXAMPLE_PATH)
    manifest["authority_scope"]["allowed_consequence_classes"] = [
        "UNSUPPORTED_CONSEQUENCE_CLASS"
    ]

    errors = errors_for(manifest)

    assert errors


def test_reviewer_authority_manifest_rejects_bad_record_hash():
    manifest = load_json(EXAMPLE_PATH)
    manifest["authority_record_hash"] = "not-a-sha256-hash"

    errors = errors_for(manifest)

    assert errors


def test_reviewer_authority_manifest_rejects_additional_properties():
    manifest = load_json(EXAMPLE_PATH)
    manifest["unexpected_field"] = "not allowed"

    errors = errors_for(manifest)

    assert errors
    assert any(error.validator == "additionalProperties" for error in errors)


def test_reviewer_authority_manifest_rejects_duplicate_scope_entries():
    manifest = load_json(EXAMPLE_PATH)
    manifest["authority_scope"]["allowed_decisions"] = [
        "REQUEST_REVIEW",
        "REQUEST_REVIEW",
    ]

    errors = errors_for(manifest)

    assert errors
    assert any(error.validator == "uniqueItems" for error in errors)
