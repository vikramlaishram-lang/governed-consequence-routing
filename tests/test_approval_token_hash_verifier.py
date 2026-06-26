import json
import shutil
import subprocess
import sys
from pathlib import Path


VERIFIER = Path("tools/verify_approval_token.py")
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


def test_approval_token_verifier_accepts_fixture():
    result = run_command([
        str(VERIFIER),
        str(TOKEN_FIXTURE),
    ])

    assert result.returncode == 0, result.stderr
    assert "APPROVAL TOKEN VERIFY PASS" in result.stdout
    assert "approval-token-demo-release-review-001" in result.stdout


def test_approval_token_verifier_detects_hash_mismatch(tmp_path):
    token_path = tmp_path / "approval_token.v0.3.json"
    shutil.copyfile(TOKEN_FIXTURE, token_path)

    token = json.loads(token_path.read_text(encoding="utf-8-sig"))
    token["approval_reason"] = "Tampered approval reason."
    token_path.write_text(json.dumps(token, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = run_command([
        str(VERIFIER),
        str(token_path),
    ])

    assert result.returncode != 0
    assert "APPROVAL TOKEN VERIFY FAIL" in result.stderr
    assert "APPROVAL_TOKEN_HASH_MISMATCH" in result.stderr


def test_approval_token_verifier_write_hash_repairs_copy(tmp_path):
    token_path = tmp_path / "approval_token.v0.3.json"
    shutil.copyfile(TOKEN_FIXTURE, token_path)

    token = json.loads(token_path.read_text(encoding="utf-8-sig"))
    token["approval_token_hash"] = "sha256:" + ("0" * 64)
    token_path.write_text(json.dumps(token, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    write_result = run_command([
        str(VERIFIER),
        str(token_path),
        "--write-hash",
    ])

    assert write_result.returncode == 0, write_result.stderr
    assert "APPROVAL TOKEN HASH WRITTEN" in write_result.stdout
    assert "APPROVAL TOKEN VERIFY PASS" in write_result.stdout

    verify_result = run_command([
        str(VERIFIER),
        str(token_path),
    ])

    assert verify_result.returncode == 0, verify_result.stderr
    assert "APPROVAL TOKEN VERIFY PASS" in verify_result.stdout


def test_approval_token_verifier_fails_for_missing_input():
    result = run_command([
        str(VERIFIER),
        "missing-approval-token.json",
    ])

    assert result.returncode != 0
    assert "INPUT_NOT_FOUND" in result.stderr