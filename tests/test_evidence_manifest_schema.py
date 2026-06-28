import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


SCHEMA_PATH = Path("schemas/evidence_manifest_v0.4.schema.json")
EXAMPLE_PATH = Path("examples/evidence_manifest/manifest.v0.4.json")


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def validator():
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def errors_for(manifest):
    return list(validator().iter_errors(manifest))


def test_evidence_manifest_example_validates():
    manifest = load_json(EXAMPLE_PATH)

    errors = errors_for(manifest)

    assert errors == []


def test_evidence_manifest_rejects_unknown_claim_type():
    manifest = load_json(EXAMPLE_PATH)
    manifest["evidence_scope"]["claim_type"] = "UNSUPPORTED_CLAIM"

    errors = errors_for(manifest)

    assert errors


def test_evidence_manifest_rejects_bad_hash_format():
    manifest = load_json(EXAMPLE_PATH)
    manifest["evidence_manifest_hash"] = "not-a-sha256-hash"

    errors = errors_for(manifest)

    assert errors


def test_evidence_manifest_rejects_additional_properties():
    manifest = load_json(EXAMPLE_PATH)
    manifest["unexpected_field"] = "not allowed"

    errors = errors_for(manifest)

    assert errors
    assert any(error.validator == "additionalProperties" for error in errors)
