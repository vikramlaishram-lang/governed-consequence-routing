import json
import subprocess
import sys
from pathlib import Path


EXPORTER = Path("tools/export_verification_bundle.py")


def run_command(args):
    return subprocess.run(
        [sys.executable, *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def test_export_verification_bundle_for_examples(tmp_path):
    bundle_path = tmp_path / "verification_bundle.json"

    result = run_command([
        str(EXPORTER),
        "examples",
        "--bundle-out",
        str(bundle_path),
        "--mutate",
    ])

    assert result.returncode == 0, result.stderr
    assert "VERIFICATION BUNDLE PASS" in result.stdout
    assert bundle_path.exists()

    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))

    assert bundle["bundle_version"] == "verification_bundle.v0.2"
    assert bundle["verification_result"] == "PASS"
    assert bundle["mutation_check_result"] == "PASS"
    assert bundle["envelope_count"] == 3
    assert bundle["first_record_hash"]
    assert bundle["final_record_hash"]
    assert bundle["schema_hash"]
    assert bundle["envelope_source_hash"]
    assert bundle["tamper_evidence_modes"] == ["UNKEYED_HASH_CHAIN"]
    assert "proposed_action" in bundle["detected_mutation_classes"]
    assert "record_hash" in bundle["detected_mutation_classes"]


def test_export_verification_bundle_without_mutation_checks(tmp_path):
    bundle_path = tmp_path / "verification_bundle.json"

    result = run_command([
        str(EXPORTER),
        "examples",
        "--bundle-out",
        str(bundle_path),
    ])

    assert result.returncode == 0, result.stderr

    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))

    assert bundle["verification_result"] == "PASS"
    assert bundle["mutation_checks_requested"] is False
    assert bundle["mutation_check_result"] == "NOT_REQUESTED"
    assert bundle["detected_mutation_classes"] == []


def test_export_verification_bundle_fails_for_missing_source(tmp_path):
    bundle_path = tmp_path / "verification_bundle.json"

    result = run_command([
        str(EXPORTER),
        "missing-envelope-source",
        "--bundle-out",
        str(bundle_path),
        "--mutate",
    ])

    assert result.returncode != 0
    assert "VERIFICATION BUNDLE FAIL" in result.stderr
