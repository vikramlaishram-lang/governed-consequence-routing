import json
import subprocess
import sys
from pathlib import Path


EXPORTER = Path("tools/export_ledger_bundle.py")
VERIFIER = Path("tools/verify_ledger_bundle.py")
ENVELOPE_FIXTURE = Path("examples/evidence_manifest/evidence_bound_decision_envelope.v0.4.json")
TOKEN_FIXTURE = Path("examples/reviewer_authority/approval_token.v0.3.json")
REVIEWER_MANIFEST_FIXTURE = Path("examples/reviewer_authority/manifest.v0.3.json")
EVIDENCE_MANIFEST_FIXTURE = Path("examples/evidence_manifest/manifest.v0.4.json")


def run_command(args):
    return subprocess.run(
        [sys.executable, *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def export_bundle(out_path):
    return run_command([
        str(EXPORTER),
        "--envelope",
        str(ENVELOPE_FIXTURE),
        "--approval-token",
        str(TOKEN_FIXTURE),
        "--reviewer-manifest",
        str(REVIEWER_MANIFEST_FIXTURE),
        "--evidence-manifest",
        str(EVIDENCE_MANIFEST_FIXTURE),
        "--out",
        str(out_path),
        "--write-hash",
    ])


def test_export_ledger_bundle_produces_bundle(tmp_path):
    bundle_path = tmp_path / "full_gcr_bundle.v0.5.json"

    result = export_bundle(bundle_path)

    assert result.returncode == 0, result.stderr
    assert "LEDGER BUNDLE EXPORT PASS" in result.stdout
    assert "FULL_GCR_BUNDLE" in result.stdout
    assert bundle_path.exists()

    bundle = json.loads(bundle_path.read_text(encoding="utf-8-sig"))
    assert bundle["schema_version"] == "verification_bundle.v0.5"
    assert bundle["bundle_type"] == "FULL_GCR_BUNDLE"
    assert bundle["bundle_subject"]["proposal_id"] == "33333333-3333-4333-8333-333333333333"
    assert bundle["bundle_hash"].startswith("sha256:")


def test_exported_ledger_bundle_verifies(tmp_path):
    bundle_path = tmp_path / "full_gcr_bundle.v0.5.json"
    export_result = export_bundle(bundle_path)
    assert export_result.returncode == 0, export_result.stderr

    verify_result = run_command([
        str(VERIFIER),
        str(bundle_path),
    ])

    assert verify_result.returncode == 0, verify_result.stderr
    assert "LEDGER BUNDLE VERIFY PASS" in verify_result.stdout


def test_export_ledger_bundle_fails_for_missing_input(tmp_path):
    bundle_path = tmp_path / "full_gcr_bundle.v0.5.json"

    result = run_command([
        str(EXPORTER),
        "--envelope",
        "missing-envelope.json",
        "--approval-token",
        str(TOKEN_FIXTURE),
        "--reviewer-manifest",
        str(REVIEWER_MANIFEST_FIXTURE),
        "--evidence-manifest",
        str(EVIDENCE_MANIFEST_FIXTURE),
        "--out",
        str(bundle_path),
        "--write-hash",
    ])

    assert result.returncode != 0
    assert "LEDGER BUNDLE EXPORT FAIL" in result.stderr
