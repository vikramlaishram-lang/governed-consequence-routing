import json
import shutil
import subprocess
import sys
from pathlib import Path


VERIFIER = Path("tools/verify_evidence_manifest_binding.py")
ENVELOPE_FIXTURE = Path("examples/evidence_manifest/evidence_bound_decision_envelope.v0.4.json")
MANIFEST_FIXTURE = Path("examples/evidence_manifest/manifest.v0.4.json")


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
    envelope_path = tmp_path / "evidence_bound_decision_envelope.v0.4.json"
    manifest_path = tmp_path / "manifest.v0.4.json"

    shutil.copyfile(ENVELOPE_FIXTURE, envelope_path)
    shutil.copyfile(MANIFEST_FIXTURE, manifest_path)

    return envelope_path, manifest_path


def verify(envelope_path, manifest_path):
    return run_command([
        str(VERIFIER),
        "--envelope",
        str(envelope_path),
        "--manifest",
        str(manifest_path),
    ])


def test_evidence_manifest_verifier_detects_hash_mismatch(tmp_path):
    envelope_path, manifest_path = copy_fixtures(tmp_path)

    manifest = load_json(manifest_path)
    manifest["evidence_items"][0]["source_ref"] = "pytest:tampered"
    write_json(manifest_path, manifest)

    result = verify(envelope_path, manifest_path)

    assert result.returncode != 0
    assert "EVIDENCE_MANIFEST_HASH_MISMATCH" in result.stderr


def test_evidence_manifest_verifier_write_hash_repairs_manifest_copy(tmp_path):
    envelope_path, manifest_path = copy_fixtures(tmp_path)

    manifest = load_json(manifest_path)
    manifest["evidence_manifest_hash"] = "sha256:" + ("0" * 64)
    write_json(manifest_path, manifest)

    write_result = run_command([
        str(VERIFIER),
        "--envelope",
        str(envelope_path),
        "--manifest",
        str(manifest_path),
        "--write-hash",
    ])

    assert write_result.returncode == 0, write_result.stderr
    assert "EVIDENCE MANIFEST HASH WRITTEN" in write_result.stdout
    assert "EVIDENCE MANIFEST BINDING VERIFY PASS" in write_result.stdout

    verify_result = verify(envelope_path, manifest_path)

    assert verify_result.returncode == 0, verify_result.stderr
    assert "EVIDENCE MANIFEST BINDING VERIFY PASS" in verify_result.stdout
