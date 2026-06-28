import copy
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


VERIFIER = Path("tools/verify_verification_receipt.py")
RECEIPT_FIXTURE = Path("examples/verification_receipt/verification_receipt.v0.6.json")


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def receipt_hash(receipt):
    material = copy.deepcopy(receipt)
    material.pop("receipt_hash", None)
    return "sha256:" + hashlib.sha256(canonical_json(material).encode("utf-8")).hexdigest()


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


def copy_receipt(tmp_path):
    receipt_path = tmp_path / "verification_receipt.v0.6.json"
    shutil.copyfile(RECEIPT_FIXTURE, receipt_path)
    return receipt_path


def verify(receipt_path):
    return run_command([
        str(VERIFIER),
        str(receipt_path),
    ])


def test_verify_verification_receipt_accepts_fixture(tmp_path):
    receipt_path = copy_receipt(tmp_path)

    result = verify(receipt_path)

    assert result.returncode == 0, result.stderr
    assert "VERIFICATION RECEIPT VERIFY PASS" in result.stdout
    assert "verification-receipt-verification-bundle" in result.stdout


def test_verify_verification_receipt_rejects_receipt_hash_tampering(tmp_path):
    receipt_path = copy_receipt(tmp_path)
    receipt = load_json(receipt_path)
    receipt["receipt_hash"] = "sha256:" + ("0" * 64)
    write_json(receipt_path, receipt)

    result = verify(receipt_path)

    assert result.returncode != 0
    assert "RECEIPT_HASH_MISMATCH" in result.stderr


def test_verify_verification_receipt_rejects_pass_with_failure_reasons(tmp_path):
    receipt_path = copy_receipt(tmp_path)
    receipt = load_json(receipt_path)
    receipt["overall_status"] = "PASS"
    receipt["failure_reasons"] = ["This should not appear in a PASS receipt."]
    receipt["receipt_hash"] = receipt_hash(receipt)
    write_json(receipt_path, receipt)

    result = verify(receipt_path)

    assert result.returncode != 0
    assert "PASS_RECEIPT_HAS_FAILURE_REASONS" in result.stderr


def test_verify_verification_receipt_rejects_fail_without_failure_reasons(tmp_path):
    receipt_path = copy_receipt(tmp_path)
    receipt = load_json(receipt_path)
    receipt["overall_status"] = "FAIL"
    receipt["failure_reasons"] = []
    receipt["verification_results"]["ledger_bundle_verification"] = {
        "status": "FAIL",
        "message": "Expected failure for test."
    }
    receipt["receipt_hash"] = receipt_hash(receipt)
    write_json(receipt_path, receipt)

    result = verify(receipt_path)

    assert result.returncode != 0
    assert "FAIL_RECEIPT_MISSING_FAILURE_REASONS" in result.stderr
