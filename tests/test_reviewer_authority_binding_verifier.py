import json
import shutil
import subprocess
import sys
from pathlib import Path


VERIFIER = Path("tools/verify_reviewer_authority_binding.py")
MANIFEST_FIXTURE = Path("examples/reviewer_authority/manifest.v0.3.json")
TOKEN_FIXTURE = Path("examples/reviewer_authority/approval_token.v0.3.json")


def run_command(args):
    return subprocess.run(
        [sys.executable, *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def copy_fixtures(tmp_path):
    manifest_path = tmp_path / "manifest.v0.3.json"
    token_path = tmp_path / "approval_token.v0.3.json"
    shutil.copyfile(MANIFEST_FIXTURE, manifest_path)
    shutil.copyfile(TOKEN_FIXTURE, token_path)
    return manifest_path, token_path


def verify(manifest_path, token_path):
    return run_command([
        str(VERIFIER),
        "--manifest",
        str(manifest_path),
        "--token",
        str(token_path),
    ])


def test_reviewer_authority_binding_verifier_accepts_fixtures(tmp_path):
    manifest_path, token_path = copy_fixtures(tmp_path)

    result = verify(manifest_path, token_path)

    assert result.returncode == 0, result.stderr
    assert "REVIEWER AUTHORITY BINDING VERIFY PASS" in result.stdout
    assert "reviewer-authority-demo-release-reviewer-001" in result.stdout


def test_reviewer_authority_binding_rejects_reviewer_authority_id_mismatch(tmp_path):
    manifest_path, token_path = copy_fixtures(tmp_path)

    manifest = load_json(manifest_path)
    manifest["reviewer_authority_id"] = "different-reviewer-authority-id"
    write_json(manifest_path, manifest)

    result = verify(manifest_path, token_path)

    assert result.returncode != 0
    assert "REVIEWER_AUTHORITY_ID_MISMATCH" in result.stderr


def test_reviewer_authority_binding_rejects_authority_record_hash_mismatch(tmp_path):
    manifest_path, token_path = copy_fixtures(tmp_path)

    manifest = load_json(manifest_path)
    manifest["authority_record_hash"] = "sha256:" + ("c" * 64)
    write_json(manifest_path, manifest)

    result = verify(manifest_path, token_path)

    assert result.returncode != 0
    assert "AUTHORITY_RECORD_HASH_MISMATCH" in result.stderr


def test_reviewer_authority_binding_rejects_inactive_authority(tmp_path):
    manifest_path, token_path = copy_fixtures(tmp_path)

    manifest = load_json(manifest_path)
    manifest["authority_status"] = "SUSPENDED"
    write_json(manifest_path, manifest)

    result = verify(manifest_path, token_path)

    assert result.returncode != 0
    assert "AUTHORITY_NOT_ACTIVE" in result.stderr


def test_reviewer_authority_binding_rejects_approval_outside_authority_window(tmp_path):
    manifest_path, token_path = copy_fixtures(tmp_path)

    manifest = load_json(manifest_path)
    manifest["valid_from"] = "2027-01-01T00:00:00Z"
    manifest["valid_until"] = "2028-01-01T00:00:00Z"
    write_json(manifest_path, manifest)

    result = verify(manifest_path, token_path)

    assert result.returncode != 0
    assert "APPROVAL_ISSUED_OUTSIDE_AUTHORITY_WINDOW" in result.stderr


def test_reviewer_authority_binding_rejects_unauthorized_consequence_class(tmp_path):
    manifest_path, token_path = copy_fixtures(tmp_path)

    manifest = load_json(manifest_path)
    manifest["authority_scope"]["allowed_consequence_classes"] = [
        "CLAIM_PUBLICATION"
    ]
    write_json(manifest_path, manifest)

    result = verify(manifest_path, token_path)

    assert result.returncode != 0
    assert "CONSEQUENCE_CLASS_NOT_AUTHORIZED" in result.stderr


def test_reviewer_authority_binding_rejects_unauthorized_decision(tmp_path):
    manifest_path, token_path = copy_fixtures(tmp_path)

    manifest = load_json(manifest_path)
    manifest["authority_scope"]["allowed_decisions"] = [
        "DENY"
    ]
    write_json(manifest_path, manifest)

    result = verify(manifest_path, token_path)

    assert result.returncode != 0
    assert "APPROVED_DECISION_NOT_AUTHORIZED" in result.stderr


def test_reviewer_authority_binding_rejects_token_hash_mismatch(tmp_path):
    manifest_path, token_path = copy_fixtures(tmp_path)

    token = load_json(token_path)
    token["approval_reason"] = "Tampered approval reason."
    write_json(token_path, token)

    result = verify(manifest_path, token_path)

    assert result.returncode != 0
    assert "APPROVAL_TOKEN_HASH_MISMATCH" in result.stderr