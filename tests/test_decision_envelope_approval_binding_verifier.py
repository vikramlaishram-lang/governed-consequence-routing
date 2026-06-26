import json
import shutil
import subprocess
import sys
from pathlib import Path


VERIFIER = Path("tools/verify_decision_envelope_approval_binding.py")
ENVELOPE_FIXTURE = Path("examples/reviewer_authority/approved_decision_envelope.v0.3.json")
TOKEN_FIXTURE = Path("examples/reviewer_authority/approval_token.v0.3.json")
MANIFEST_FIXTURE = Path("examples/reviewer_authority/manifest.v0.3.json")


def run_command(args):
    return subprocess.run(
        [sys.executable, *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def copy_fixtures(tmp_path):
    envelope_path = tmp_path / "approved_decision_envelope.v0.3.json"
    token_path = tmp_path / "approval_token.v0.3.json"
    manifest_path = tmp_path / "manifest.v0.3.json"

    shutil.copyfile(ENVELOPE_FIXTURE, envelope_path)
    shutil.copyfile(TOKEN_FIXTURE, token_path)
    shutil.copyfile(MANIFEST_FIXTURE, manifest_path)

    return envelope_path, token_path, manifest_path


def verify(envelope_path, token_path, manifest_path):
    return run_command([
        str(VERIFIER),
        "--envelope",
        str(envelope_path),
        "--token",
        str(token_path),
        "--manifest",
        str(manifest_path),
    ])


def test_decision_envelope_approval_binding_accepts_fixtures(tmp_path):
    envelope_path, token_path, manifest_path = copy_fixtures(tmp_path)

    result = verify(envelope_path, token_path, manifest_path)

    assert result.returncode == 0, result.stderr
    assert "DECISION ENVELOPE APPROVAL BINDING VERIFY PASS" in result.stdout
    assert "approval-token-demo-release-review-001" in result.stdout


def test_decision_envelope_approval_binding_rejects_reviewer_authority_id_mismatch(tmp_path):
    envelope_path, token_path, manifest_path = copy_fixtures(tmp_path)

    envelope = load_json(envelope_path)
    envelope["reviewer_authority_id"] = "different-reviewer-authority-id"
    write_json(envelope_path, envelope)

    result = verify(envelope_path, token_path, manifest_path)

    assert result.returncode != 0
    assert "REVIEWER_AUTHORITY_ID_MISMATCH" in result.stderr


def test_decision_envelope_approval_binding_rejects_proposal_hash_mismatch(tmp_path):
    envelope_path, token_path, manifest_path = copy_fixtures(tmp_path)

    envelope = load_json(envelope_path)
    envelope["proposal_hash"] = "sha256:" + ("9" * 64)
    write_json(envelope_path, envelope)

    result = verify(envelope_path, token_path, manifest_path)

    assert result.returncode != 0
    assert "PROPOSAL_HASH_MISMATCH" in result.stderr


def test_decision_envelope_approval_binding_rejects_normalized_action_hash_mismatch(tmp_path):
    envelope_path, token_path, manifest_path = copy_fixtures(tmp_path)

    envelope = load_json(envelope_path)
    envelope["normalized_action_hash"] = "sha256:" + ("8" * 64)
    write_json(envelope_path, envelope)

    result = verify(envelope_path, token_path, manifest_path)

    assert result.returncode != 0
    assert "NORMALIZED_ACTION_HASH_MISMATCH" in result.stderr


def test_decision_envelope_approval_binding_rejects_policy_hash_mismatch(tmp_path):
    envelope_path, token_path, manifest_path = copy_fixtures(tmp_path)

    envelope = load_json(envelope_path)
    envelope["policy_hash"] = "sha256:" + ("7" * 64)
    write_json(envelope_path, envelope)

    result = verify(envelope_path, token_path, manifest_path)

    assert result.returncode != 0
    assert "POLICY_HASH_MISMATCH" in result.stderr


def test_decision_envelope_approval_binding_rejects_unapproved_consequence_class(tmp_path):
    envelope_path, token_path, manifest_path = copy_fixtures(tmp_path)

    envelope = load_json(envelope_path)
    envelope["consequence_classification"]["consequence_class"] = "CLAIM_PUBLICATION"
    write_json(envelope_path, envelope)

    result = verify(envelope_path, token_path, manifest_path)

    assert result.returncode != 0
    assert "ENVELOPE_CONSEQUENCE_CLASS_NOT_APPROVED" in result.stderr


def test_decision_envelope_approval_binding_rejects_unapproved_decision(tmp_path):
    envelope_path, token_path, manifest_path = copy_fixtures(tmp_path)

    envelope = load_json(envelope_path)
    envelope["decision"] = "DENY"
    write_json(envelope_path, envelope)

    result = verify(envelope_path, token_path, manifest_path)

    assert result.returncode != 0
    assert "ENVELOPE_DECISION_NOT_APPROVED" in result.stderr


def test_decision_envelope_approval_binding_rejects_non_approved_review_status(tmp_path):
    envelope_path, token_path, manifest_path = copy_fixtures(tmp_path)

    envelope = load_json(envelope_path)
    envelope["review_status"] = "PENDING"
    write_json(envelope_path, envelope)

    result = verify(envelope_path, token_path, manifest_path)

    assert result.returncode != 0
    assert "ENVELOPE_REVIEW_STATUS_NOT_APPROVED" in result.stderr


def test_decision_envelope_approval_binding_rejects_expired_token_window(tmp_path):
    envelope_path, token_path, manifest_path = copy_fixtures(tmp_path)

    envelope = load_json(envelope_path)
    envelope["created_at"] = "2026-06-28T00:00:00Z"
    write_json(envelope_path, envelope)

    result = verify(envelope_path, token_path, manifest_path)

    assert result.returncode != 0
    assert "ENVELOPE_OUTSIDE_APPROVAL_TOKEN_WINDOW" in result.stderr


def test_decision_envelope_approval_binding_rejects_inactive_manifest(tmp_path):
    envelope_path, token_path, manifest_path = copy_fixtures(tmp_path)

    manifest = load_json(manifest_path)
    manifest["authority_status"] = "SUSPENDED"
    write_json(manifest_path, manifest)

    result = verify(envelope_path, token_path, manifest_path)

    assert result.returncode != 0
    assert "AUTHORITY_NOT_ACTIVE" in result.stderr


def test_decision_envelope_approval_binding_rejects_token_hash_mismatch(tmp_path):
    envelope_path, token_path, manifest_path = copy_fixtures(tmp_path)

    token = load_json(token_path)
    token["approval_reason"] = "Tampered approval reason."
    write_json(token_path, token)

    result = verify(envelope_path, token_path, manifest_path)

    assert result.returncode != 0
    assert "APPROVAL_TOKEN_HASH_MISMATCH" in result.stderr