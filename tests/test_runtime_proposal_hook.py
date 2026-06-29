import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from tools import capture_runtime_proposal


TOOL = Path("tools/capture_runtime_proposal.py")
SCHEMA = Path("schemas/runtime_proposal_v0.9.schema.json")
FIXTURE = Path("examples/runtime_proposal/proposal.v0.9.json")

FORBIDDEN_OUTPUT_STRINGS = [
    "ACTION EXECUTED",
    "TOOL EXECUTED",
    "APPROVED",
    "COMPLIANT",
    "CERTIFIED",
    "LEGALLY VALID",
    "PRODUCTION READY",
    "SAFE",
    "CORRECT",
]

ARTIFACT_PATTERNS = {
    "approval_tokens": "examples/**/approval_token*.json",
    "verification_receipts": "examples/**/verification_receipt*.json",
    "receipt_indexes": "examples/**/index*.json",
    "bundles": "examples/**/full_gcr_bundle*.json",
    "evidence_manifests": "examples/evidence_manifest/*.json",
    "authority_manifests": "examples/reviewer_authority/manifest*.json",
}


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value):
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def record_hash(record):
    material = copy.deepcopy(record)
    material.pop("record_hash", None)
    return sha256_json(material)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_tool(args):
    return subprocess.run(
        [sys.executable, str(TOOL), *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def capture_to(tmp_path, *extra_args):
    out = tmp_path / "proposal.generated.v0.9.json"
    result = run_tool([
        "--agent-id",
        "simulated-coding-agent",
        "--action-type",
        "write_file",
        "--target",
        ".github/workflows/deploy.yml",
        "--intent",
        "modify deployment workflow",
        "--output",
        str(out),
        *extra_args,
    ])
    return result, out


def validate_record(record):
    schema = load_json(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(record), key=lambda error: error.path)
    assert errors == []


def file_hashes(paths):
    return {
        path.as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in paths
    }


def artifact_snapshot(pattern):
    return {
        path.relative_to(Path(".")).as_posix()
        for path in Path(".").glob(pattern)
    }


def test_valid_simulated_proposal_capture_passes(tmp_path):
    result, out = capture_to(tmp_path)

    assert result.returncode == 0, result.stderr
    assert out.exists()
    assert "PROPOSAL CAPTURED" in result.stdout
    assert "CONSEQUENCE NORMALIZED" in result.stdout
    assert "RUNTIME PROPOSAL RECORD CREATED" in result.stdout


def test_generated_runtime_proposal_validates_against_schema(tmp_path):
    result, out = capture_to(tmp_path)
    assert result.returncode == 0, result.stderr

    validate_record(load_json(out))


def test_proposed_action_hash_verifies():
    record = load_json(FIXTURE)

    assert record["proposed_action_hash"] == sha256_json(record["proposed_action"])


def test_normalized_consequence_hash_verifies():
    record = load_json(FIXTURE)

    assert record["normalized_consequence_hash"] == sha256_json(record["normalized_consequence"])


def test_record_hash_verifies():
    record = load_json(FIXTURE)

    assert record["record_hash"] == record_hash(record)


def test_execution_status_is_always_not_executed(tmp_path):
    result, out = capture_to(tmp_path)
    assert result.returncode == 0, result.stderr

    assert load_json(out)["execution_status"] == "NOT_EXECUTED"


def test_authorization_status_is_never_authorized(tmp_path):
    result, out = capture_to(tmp_path)
    assert result.returncode == 0, result.stderr

    assert load_json(out)["authorization_status"] != "AUTHORIZED"


def test_deploy_workflow_write_classifies_as_production_state_change_high(tmp_path):
    result, out = capture_to(tmp_path)
    assert result.returncode == 0, result.stderr
    record = load_json(out)

    assert record["consequence_classification"] == "PRODUCTION_STATE_CHANGE"
    assert record["consequence_risk"] == "HIGH"


def test_secret_target_classifies_as_secret_access_critical(tmp_path):
    out = tmp_path / "proposal.secret.v0.9.json"
    result = run_tool([
        "--agent-id",
        "simulated-coding-agent",
        "--action-type",
        "read_file",
        "--target",
        ".env",
        "--intent",
        "inspect environment configuration",
        "--output",
        str(out),
    ])
    assert result.returncode == 0, result.stderr
    record = load_json(out)

    assert record["consequence_classification"] == "SECRET_ACCESS"
    assert record["consequence_risk"] == "CRITICAL"


def test_missing_agent_id_fails_closed(tmp_path):
    out = tmp_path / "missing-agent.json"
    result = run_tool([
        "--action-type",
        "write_file",
        "--intent",
        "modify deployment workflow",
        "--output",
        str(out),
    ])

    assert result.returncode != 0
    assert not out.exists()


def test_missing_action_type_fails_closed(tmp_path):
    out = tmp_path / "missing-action.json"
    result = run_tool([
        "--agent-id",
        "simulated-coding-agent",
        "--intent",
        "modify deployment workflow",
        "--output",
        str(out),
    ])

    assert result.returncode != 0
    assert not out.exists()


def test_missing_intent_fails_closed(tmp_path):
    out = tmp_path / "missing-intent.json"
    result = run_tool([
        "--agent-id",
        "simulated-coding-agent",
        "--action-type",
        "write_file",
        "--output",
        str(out),
    ])

    assert result.returncode != 0
    assert not out.exists()


def test_malformed_input_fails_closed(tmp_path):
    input_path = tmp_path / "bad.json"
    output_path = tmp_path / "should-not-exist.json"
    input_path.write_text("{not-json", encoding="utf-8")

    result = run_tool(["--input-json", str(input_path), "--output", str(output_path)])

    assert result.returncode != 0
    assert not output_path.exists()


def test_output_path_omitted_fails_closed():
    result = run_tool([
        "--agent-id",
        "simulated-coding-agent",
        "--action-type",
        "write_file",
        "--intent",
        "modify deployment workflow",
    ])

    assert result.returncode != 0
    assert "MISSING_REQUIRED_FIELD: output" in result.stderr


def test_validation_failure_writes_no_output_file(tmp_path):
    out = tmp_path / "invalid-source.json"
    result = run_tool([
        "--agent-id",
        "simulated-coding-agent",
        "--action-type",
        "write_file",
        "--intent",
        "modify deployment workflow",
        "--source-type",
        "REMOTE_AGENT",
        "--output",
        str(out),
    ])

    assert result.returncode != 0
    assert not out.exists()


def test_capture_does_not_execute_tools():
    assert not hasattr(capture_runtime_proposal, "subprocess")

    record = capture_runtime_proposal.build_runtime_proposal(
        agent_id="simulated-coding-agent",
        action_type="write_file",
        target=".github/workflows/deploy.yml",
        intent="modify deployment workflow",
    )

    assert record["execution_status"] == "NOT_EXECUTED"


def test_capture_does_not_call_external_systems(monkeypatch):
    def fail_network(*args, **kwargs):
        raise AssertionError("network call should not be made")

    monkeypatch.setattr("socket.create_connection", fail_network)
    record = capture_runtime_proposal.build_runtime_proposal(
        agent_id="simulated-coding-agent",
        action_type="external_request",
        target="https://example.test",
        intent="propose outbound request",
    )

    assert record["execution_status"] == "NOT_EXECUTED"


def test_capture_does_not_mutate_existing_fixtures(tmp_path):
    fixture_paths = [
        path
        for path in Path("examples").rglob("*.json")
        if "runtime_proposal" not in path.as_posix()
    ]
    before = file_hashes(fixture_paths)
    result, _ = capture_to(tmp_path)
    assert result.returncode == 0, result.stderr
    after = file_hashes(fixture_paths)

    assert after == before


@pytest.mark.parametrize("label", list(ARTIFACT_PATTERNS))
def test_capture_does_not_create_disallowed_governance_artifacts(tmp_path, label):
    pattern = ARTIFACT_PATTERNS[label]
    before = artifact_snapshot(pattern)
    result, _ = capture_to(tmp_path)
    assert result.returncode == 0, result.stderr
    after = artifact_snapshot(pattern)

    assert after == before


def test_output_contains_allowed_status_strings(tmp_path):
    result, _ = capture_to(tmp_path)

    assert result.returncode == 0, result.stderr
    assert "PROPOSAL CAPTURED" in result.stdout
    assert "CONSEQUENCE NORMALIZED" in result.stdout
    assert "RUNTIME PROPOSAL RECORD CREATED" in result.stdout
    assert "EXECUTION_STATUS: NOT_EXECUTED" in result.stdout
    assert "AUTHORIZATION_STATUS: REQUIRES_GOVERNANCE" in result.stdout


def test_output_does_not_contain_forbidden_overclaim_strings(tmp_path):
    result, _ = capture_to(tmp_path)
    output = result.stdout + result.stderr

    assert result.returncode == 0, result.stderr
    for forbidden in FORBIDDEN_OUTPUT_STRINGS:
        assert forbidden not in output


def test_verify_only_mode_passes_on_valid_fixture():
    result = run_tool(["--verify-only", str(FIXTURE)])

    assert result.returncode == 0, result.stderr
    assert "RUNTIME PROPOSAL VERIFY PASS" in result.stdout


def test_verify_only_mode_fails_on_tampered_fixture(tmp_path):
    tampered = tmp_path / "proposal.tampered.v0.9.json"
    record = load_json(FIXTURE)
    record["proposed_action"]["intent"] = "tampered intent"
    write_json(tampered, record)

    result = run_tool(["--verify-only", str(tampered)])

    assert result.returncode != 0
    assert "RUNTIME PROPOSAL VERIFY FAIL" in result.stderr


def test_unknown_classification_never_becomes_authorized(tmp_path):
    out = tmp_path / "unknown.v0.9.json"
    result = run_tool([
        "--agent-id",
        "simulated-coding-agent",
        "--action-type",
        "invent_new_action",
        "--intent",
        "propose an unknown operation",
        "--output",
        str(out),
    ])

    assert result.returncode == 0, result.stderr
    record = load_json(out)
    assert record["consequence_classification"] == "UNKNOWN"
    assert record["authorization_status"] != "AUTHORIZED"


def test_record_proof_boundary_states_capture_is_not_execution_authority():
    record = load_json(FIXTURE)
    boundary_text = " ".join(record["proof_boundary"]["does_not_prove"])

    assert "execution authority" in boundary_text
    assert "authorization" in boundary_text
    assert record["execution_status"] == "NOT_EXECUTED"
