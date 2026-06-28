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


def test_decision_envelope_evidence_binding_accepts_fixtures(tmp_path):
    envelope_path, manifest_path = copy_fixtures(tmp_path)

    result = verify(envelope_path, manifest_path)

    assert result.returncode == 0, result.stderr
    assert "EVIDENCE MANIFEST BINDING VERIFY PASS" in result.stdout
    assert "evidence-manifest-demo-release-readiness-001" in result.stdout


def test_decision_envelope_evidence_binding_rejects_envelope_hash_mismatch(tmp_path):
    envelope_path, manifest_path = copy_fixtures(tmp_path)

    envelope = load_json(envelope_path)
    envelope["evidence_manifest_hash"] = "sha256:" + ("9" * 64)
    write_json(envelope_path, envelope)

    result = verify(envelope_path, manifest_path)

    assert result.returncode != 0
    assert "EVIDENCE_MANIFEST_HASH_BINDING_MISMATCH" in result.stderr


def test_decision_envelope_evidence_binding_rejects_proposal_hash_mismatch(tmp_path):
    envelope_path, manifest_path = copy_fixtures(tmp_path)

    envelope = load_json(envelope_path)
    envelope["proposal_hash"] = "sha256:" + ("8" * 64)
    write_json(envelope_path, envelope)

    result = verify(envelope_path, manifest_path)

    assert result.returncode != 0
    assert "PROPOSAL_HASH_MISMATCH" in result.stderr


def test_decision_envelope_evidence_binding_rejects_missing_required_evidence_type(tmp_path):
    envelope_path, manifest_path = copy_fixtures(tmp_path)

    manifest = load_json(manifest_path)
    manifest["evidence_items"] = [
        item
        for item in manifest["evidence_items"]
        if item["evidence_type"] != "RELEASE_NOTE"
    ]
    write_json(manifest_path, manifest)

    result = verify(envelope_path, manifest_path)

    assert result.returncode != 0
    assert "EVIDENCE_MANIFEST_HASH_MISMATCH" in result.stderr

    run_command([
        str(VERIFIER),
        "--envelope",
        str(envelope_path),
        "--manifest",
        str(manifest_path),
        "--write-hash",
    ])
    repaired_manifest = load_json(manifest_path)
    envelope = load_json(envelope_path)
    envelope["evidence_manifest_hash"] = repaired_manifest["evidence_manifest_hash"]
    write_json(envelope_path, envelope)

    repaired_result = verify(envelope_path, manifest_path)

    assert repaired_result.returncode != 0
    assert "REQUIRED_EVIDENCE_TYPE_MISSING" in repaired_result.stderr


def test_decision_envelope_evidence_binding_rejects_minimum_admitted_count_failure(tmp_path):
    envelope_path, manifest_path = copy_fixtures(tmp_path)

    manifest = load_json(manifest_path)
    manifest["evidence_requirements"]["minimum_admitted_items"] = 5
    write_json(manifest_path, manifest)

    run_command([
        str(VERIFIER),
        "--envelope",
        str(envelope_path),
        "--manifest",
        str(manifest_path),
        "--write-hash",
    ])
    repaired_manifest = load_json(manifest_path)
    envelope = load_json(envelope_path)
    envelope["evidence_manifest_hash"] = repaired_manifest["evidence_manifest_hash"]
    write_json(envelope_path, envelope)

    result = verify(envelope_path, manifest_path)

    assert result.returncode != 0
    assert "MINIMUM_ADMITTED_EVIDENCE_COUNT_NOT_MET" in result.stderr


def test_decision_envelope_evidence_binding_rejects_insufficient_decision(tmp_path):
    envelope_path, manifest_path = copy_fixtures(tmp_path)

    manifest = load_json(manifest_path)
    manifest["admissibility_decision"] = "INSUFFICIENT"
    write_json(manifest_path, manifest)

    run_command([
        str(VERIFIER),
        "--envelope",
        str(envelope_path),
        "--manifest",
        str(manifest_path),
        "--write-hash",
    ])
    repaired_manifest = load_json(manifest_path)
    envelope = load_json(envelope_path)
    envelope["evidence_manifest_hash"] = repaired_manifest["evidence_manifest_hash"]
    write_json(envelope_path, envelope)

    result = verify(envelope_path, manifest_path)

    assert result.returncode != 0
    assert "ADMISSIBILITY_DECISION_NOT_SUFFICIENT" in result.stderr
