import copy
import importlib.util
import json
from pathlib import Path

import pytest


MODULE_PATH = Path("tools/verify_envelope_chain.py")
EXAMPLE_PATH = Path("examples/allow_read_source_file.v0.1.json")


def load_module():
    spec = importlib.util.spec_from_file_location("verify_envelope_chain", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_example_envelope():
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))


def build_hmac_envelope(monkeypatch, key="demo-hmac-key", key_id="demo-key-id"):
    module = load_module()
    envelope = copy.deepcopy(load_example_envelope())

    envelope["tamper_evidence_mode"] = "HMAC_SHA256_V1"
    envelope["key_id"] = key_id
    envelope["previous_record_hash"] = module.GENESIS_HASH
    envelope["record_hash"] = "sha256:" + ("0" * 64)

    monkeypatch.setenv("GCR_HMAC_KEY", key)
    monkeypatch.setenv("GCR_HMAC_KEY_ID", key_id)

    envelope["record_hash"] = module.compute_record_hash(envelope)

    return module, envelope


def test_hmac_custody_envelope_verifies_with_env_key(monkeypatch):
    module, envelope = build_hmac_envelope(monkeypatch)

    module.verify_envelopes([envelope], module.load_schema())


def test_hmac_custody_envelope_fails_when_key_missing(monkeypatch):
    module, envelope = build_hmac_envelope(monkeypatch)

    monkeypatch.delenv("GCR_HMAC_KEY", raising=False)

    with pytest.raises(module.VerificationError) as exc:
        module.verify_envelopes([envelope], module.load_schema())

    assert "HMAC_KEY_MISSING" in str(exc.value)


def test_hmac_custody_envelope_fails_when_key_id_missing(monkeypatch):
    module, envelope = build_hmac_envelope(monkeypatch)

    envelope["key_id"] = None

    with pytest.raises(module.VerificationError) as exc:
        module.verify_envelopes([envelope], module.load_schema())

    assert "HMAC_KEY_ID_MISSING" in str(exc.value)


def test_hmac_custody_envelope_fails_when_key_id_mismatch(monkeypatch):
    module, envelope = build_hmac_envelope(monkeypatch)

    monkeypatch.setenv("GCR_HMAC_KEY_ID", "different-key-id")

    with pytest.raises(module.VerificationError) as exc:
        module.verify_envelopes([envelope], module.load_schema())

    assert "HMAC_KEY_ID_MISMATCH" in str(exc.value)


def test_hmac_custody_envelope_fails_when_key_is_wrong(monkeypatch):
    module, envelope = build_hmac_envelope(monkeypatch)

    monkeypatch.setenv("GCR_HMAC_KEY", "wrong-demo-key")

    with pytest.raises(module.VerificationError) as exc:
        module.verify_envelopes([envelope], module.load_schema())

    assert "RECORD_HASH_MISMATCH" in str(exc.value)