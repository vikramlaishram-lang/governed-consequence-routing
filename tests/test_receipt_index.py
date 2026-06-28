import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path


VERIFIER = Path("tools/verify_receipt_index.py")
INDEX_FIXTURE = Path("examples/verification_receipt_index/index.v0.7.json")


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def index_hash(index):
    material = copy.deepcopy(index)
    material.pop("index_hash", None)
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


def copy_index(tmp_path):
    index_path = tmp_path / "index.v0.7.json"
    write_json(index_path, load_json(INDEX_FIXTURE))
    return index_path


def verify(index_path):
    return run_command([str(VERIFIER), str(index_path)])


def test_verify_receipt_index_accepts_fixture(tmp_path):
    index_path = copy_index(tmp_path)

    result = verify(index_path)

    assert result.returncode == 0, result.stderr
    assert "RECEIPT INDEX VERIFY PASS" in result.stdout
    assert "receipt_count: 2" in result.stdout


def test_verify_receipt_index_rejects_hash_mismatch(tmp_path):
    index_path = copy_index(tmp_path)
    index = load_json(index_path)
    index["index_hash"] = "sha256:" + ("0" * 64)
    write_json(index_path, index)

    result = verify(index_path)

    assert result.returncode != 0
    assert "INDEX_HASH_MISMATCH" in result.stderr


def test_verify_receipt_index_rejects_count_mismatch(tmp_path):
    index_path = copy_index(tmp_path)
    index = load_json(index_path)
    index["receipt_count"] = 99
    index["index_hash"] = index_hash(index)
    write_json(index_path, index)

    result = verify(index_path)

    assert result.returncode != 0
    assert "RECEIPT_COUNT_MISMATCH" in result.stderr


def test_verify_receipt_index_rejects_status_count_mismatch(tmp_path):
    index_path = copy_index(tmp_path)
    index = load_json(index_path)
    index["status_counts"]["PASS"] = 2
    index["index_hash"] = index_hash(index)
    write_json(index_path, index)

    result = verify(index_path)

    assert result.returncode != 0
    assert "STATUS_COUNT_MISMATCH" in result.stderr


def test_verify_receipt_index_rejects_malformed_receipt_hash(tmp_path):
    index_path = copy_index(tmp_path)
    index = load_json(index_path)
    index["receipts"][0]["receipt_hash"] = "not-a-sha256-hash"
    index["index_hash"] = index_hash(index)
    write_json(index_path, index)

    result = verify(index_path)

    assert result.returncode != 0
    assert "RECEIPT_INDEX_SCHEMA_INVALID" in result.stderr


def test_verify_receipt_index_rejects_receipt_entry_mutation(tmp_path):
    index_path = copy_index(tmp_path)
    index = load_json(index_path)
    index["receipts"][0]["receipt_path"] = "examples/verification_receipt/tampered.json"
    write_json(index_path, index)

    result = verify(index_path)

    assert result.returncode != 0
    assert "INDEX_HASH_MISMATCH" in result.stderr


def test_verify_receipt_index_rejects_unknown_field(tmp_path):
    index_path = copy_index(tmp_path)
    index = load_json(index_path)
    index["unexpected"] = True
    index["index_hash"] = index_hash(index)
    write_json(index_path, index)

    result = verify(index_path)

    assert result.returncode != 0
    assert "RECEIPT_INDEX_SCHEMA_INVALID" in result.stderr


def test_verify_receipt_index_accepts_empty_index(tmp_path):
    index_path = tmp_path / "empty_index.v0.7.json"
    index = {
        "created_at": "2026-06-28T00:00:00Z",
        "index_id": "88888888-8888-4888-8888-888888888888",
        "latest_verification_time": None,
        "receipt_count": 0,
        "receipts": [],
        "schema_version": "verification_receipt_index_v0.7",
        "status_counts": {
            "FAIL": 0,
            "PASS": 0,
        },
        "updated_at": "2026-06-28T00:00:00Z",
    }
    index["index_hash"] = index_hash(index)
    write_json(index_path, index)

    result = verify(index_path)

    assert result.returncode == 0, result.stderr
    assert "RECEIPT INDEX VERIFY PASS" in result.stdout
    assert "receipt_count: 0" in result.stdout


def test_verify_receipt_index_rejects_latest_time_mismatch(tmp_path):
    index_path = copy_index(tmp_path)
    index = load_json(index_path)
    index["latest_verification_time"] = "2026-06-27T00:00:00Z"
    index["index_hash"] = index_hash(index)
    write_json(index_path, index)

    result = verify(index_path)

    assert result.returncode != 0
    assert "LATEST_VERIFICATION_TIME_MISMATCH" in result.stderr


def test_verify_receipt_index_mutation_mode_passes():
    result = run_command([str(VERIFIER), str(INDEX_FIXTURE), "--mutate"])

    assert result.returncode == 0, result.stderr
    assert "MUTATION CHECK PASS" in result.stdout
