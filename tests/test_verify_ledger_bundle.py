import copy
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


VERIFIER = Path("tools/verify_ledger_bundle.py")
BUNDLE_FIXTURE = Path("examples/verification_bundle/full_gcr_bundle.v0.5.json")


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text):
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def artifact_hash(value):
    return sha256_text(canonical_json(value))


def bundle_hash(bundle):
    material = copy.deepcopy(bundle)
    material.pop("bundle_hash", None)
    return sha256_text(canonical_json(material))


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


def copy_bundle(tmp_path):
    bundle_path = tmp_path / "full_gcr_bundle.v0.5.json"
    shutil.copyfile(BUNDLE_FIXTURE, bundle_path)
    return bundle_path


def rewrite_bundle_hash(bundle):
    bundle["bundle_hash"] = bundle_hash(bundle)


def rewrite_artifact_hash(bundle, artifact_name, hash_name):
    bundle["artifact_hashes"][hash_name] = artifact_hash(bundle["artifacts"][artifact_name])


def verify(bundle_path):
    return run_command([
        str(VERIFIER),
        str(bundle_path),
    ])


def test_verify_ledger_bundle_accepts_fixture(tmp_path):
    bundle_path = copy_bundle(tmp_path)

    result = verify(bundle_path)

    assert result.returncode == 0, result.stderr
    assert "LEDGER BUNDLE VERIFY PASS" in result.stdout
    assert "verification-bundle-33333333-3333-4333-8333-333333333333" in result.stdout


def test_verify_ledger_bundle_rejects_bundle_hash_tampering(tmp_path):
    bundle_path = copy_bundle(tmp_path)
    bundle = load_json(bundle_path)
    bundle["bundle_hash"] = "sha256:" + ("0" * 64)
    write_json(bundle_path, bundle)

    result = verify(bundle_path)

    assert result.returncode != 0
    assert "BUNDLE_HASH_MISMATCH" in result.stderr


def test_verify_ledger_bundle_rejects_embedded_decision_envelope_tampering(tmp_path):
    bundle_path = copy_bundle(tmp_path)
    bundle = load_json(bundle_path)
    bundle["artifacts"]["decision_envelope"]["proposal_hash"] = "sha256:" + ("8" * 64)
    rewrite_artifact_hash(bundle, "decision_envelope", "decision_envelope_hash")
    rewrite_bundle_hash(bundle)
    write_json(bundle_path, bundle)

    result = verify(bundle_path)

    assert result.returncode != 0
    assert "PROPOSAL_HASH_MISMATCH" in result.stderr


def test_verify_ledger_bundle_rejects_embedded_approval_token_tampering(tmp_path):
    bundle_path = copy_bundle(tmp_path)
    bundle = load_json(bundle_path)
    bundle["artifacts"]["approval_token"]["approval_reason"] = "Tampered approval reason."
    rewrite_artifact_hash(bundle, "approval_token", "approval_token_hash")
    rewrite_bundle_hash(bundle)
    write_json(bundle_path, bundle)

    result = verify(bundle_path)

    assert result.returncode != 0
    assert "APPROVAL_TOKEN_HASH_MISMATCH" in result.stderr


def test_verify_ledger_bundle_rejects_embedded_reviewer_manifest_tampering(tmp_path):
    bundle_path = copy_bundle(tmp_path)
    bundle = load_json(bundle_path)
    bundle["artifacts"]["reviewer_authority_manifest"]["authority_status"] = "SUSPENDED"
    rewrite_artifact_hash(
        bundle,
        "reviewer_authority_manifest",
        "reviewer_authority_manifest_hash",
    )
    rewrite_bundle_hash(bundle)
    write_json(bundle_path, bundle)

    result = verify(bundle_path)

    assert result.returncode != 0
    assert "AUTHORITY_NOT_ACTIVE" in result.stderr


def test_verify_ledger_bundle_rejects_embedded_evidence_manifest_tampering(tmp_path):
    bundle_path = copy_bundle(tmp_path)
    bundle = load_json(bundle_path)
    bundle["artifacts"]["evidence_manifest"]["evidence_items"][0]["source_ref"] = "pytest:tampered"
    rewrite_artifact_hash(bundle, "evidence_manifest", "evidence_manifest_hash")
    rewrite_bundle_hash(bundle)
    write_json(bundle_path, bundle)

    result = verify(bundle_path)

    assert result.returncode != 0
    assert "EVIDENCE_MANIFEST_HASH_MISMATCH" in result.stderr


def test_verify_ledger_bundle_rejects_schema_hash_mismatch(tmp_path):
    bundle_path = copy_bundle(tmp_path)
    bundle = load_json(bundle_path)
    bundle["artifact_hashes"]["evidence_manifest_schema_hash"] = "sha256:" + ("7" * 64)
    rewrite_bundle_hash(bundle)
    write_json(bundle_path, bundle)

    result = verify(bundle_path)

    assert result.returncode != 0
    assert "EVIDENCE_MANIFEST_SCHEMA_HASH_MISMATCH" in result.stderr


def test_verify_ledger_bundle_rejects_artifact_hash_mismatch(tmp_path):
    bundle_path = copy_bundle(tmp_path)
    bundle = load_json(bundle_path)
    bundle["artifact_hashes"]["decision_envelope_hash"] = "sha256:" + ("6" * 64)
    rewrite_bundle_hash(bundle)
    write_json(bundle_path, bundle)

    result = verify(bundle_path)

    assert result.returncode != 0
    assert "DECISION_ENVELOPE_HASH_MISMATCH" in result.stderr


def test_verify_ledger_bundle_rejects_failed_verification_result(tmp_path):
    bundle_path = copy_bundle(tmp_path)
    bundle = load_json(bundle_path)
    bundle["verification_results"]["approval_token_verification"]["status"] = "FAIL"
    rewrite_bundle_hash(bundle)
    write_json(bundle_path, bundle)

    result = verify(bundle_path)

    assert result.returncode != 0
    assert "VERIFICATION_RESULT_NOT_PASS" in result.stderr


def test_verify_ledger_bundle_rejects_bundle_subject_mismatch(tmp_path):
    bundle_path = copy_bundle(tmp_path)
    bundle = load_json(bundle_path)
    bundle["bundle_subject"]["proposal_id"] = "44444444-4444-4444-8444-444444444444"
    rewrite_bundle_hash(bundle)
    write_json(bundle_path, bundle)

    result = verify(bundle_path)

    assert result.returncode != 0
    assert "BUNDLE_SUBJECT_PROPOSAL_ID_MISMATCH" in result.stderr
