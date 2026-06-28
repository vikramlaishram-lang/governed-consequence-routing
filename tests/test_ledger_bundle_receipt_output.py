import subprocess
import sys
from pathlib import Path


LEDGER_VERIFIER = Path("tools/verify_ledger_bundle.py")
RECEIPT_VERIFIER = Path("tools/verify_verification_receipt.py")
BUNDLE_FIXTURE = Path("examples/verification_bundle/full_gcr_bundle.v0.5.json")


def run_command(args):
    return subprocess.run(
        [sys.executable, *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def test_ledger_bundle_verifier_emits_pass_receipt(tmp_path):
    receipt_path = tmp_path / "verification_receipt.v0.6.json"

    result = run_command([
        str(LEDGER_VERIFIER),
        str(BUNDLE_FIXTURE),
        "--receipt-out",
        str(receipt_path),
    ])

    assert result.returncode == 0, result.stderr
    assert "LEDGER BUNDLE VERIFY PASS" in result.stdout
    assert "receipt_out:" in result.stdout
    assert receipt_path.exists()


def test_emitted_pass_receipt_verifies(tmp_path):
    receipt_path = tmp_path / "verification_receipt.v0.6.json"

    emit_result = run_command([
        str(LEDGER_VERIFIER),
        str(BUNDLE_FIXTURE),
        "--receipt-out",
        str(receipt_path),
    ])
    assert emit_result.returncode == 0, emit_result.stderr

    verify_result = run_command([
        str(RECEIPT_VERIFIER),
        str(receipt_path),
    ])

    assert verify_result.returncode == 0, verify_result.stderr
    assert "VERIFICATION RECEIPT VERIFY PASS" in verify_result.stdout
