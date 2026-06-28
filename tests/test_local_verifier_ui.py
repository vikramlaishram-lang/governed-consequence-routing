import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from tools import local_verifier_ui


FORBIDDEN_WORDS = [
    "certified",
    "compliant",
    "legally",
    "production",
    "enterprise",
    "admissible",
    "safe",
    "correct",
]


def run_cli(verifier_name):
    spec = local_verifier_ui.VERIFIERS[verifier_name]
    return subprocess.run(
        [sys.executable, spec.script, *spec.args],
        cwd=local_verifier_ui.REPO_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hash_values(text):
    return set(re.findall(r"sha256:[a-f0-9]{64}", text))


def json_artifact_snapshot():
    roots = [
        local_verifier_ui.REPO_ROOT / "examples",
        local_verifier_ui.REPO_ROOT / "schemas",
    ]
    return {
        path.relative_to(local_verifier_ui.REPO_ROOT).as_posix()
        for root in roots
        for path in root.rglob("*.json")
    }


def strip_boundary(html_text):
    return re.sub(
        r'<section id="boundary">.*?</section>',
        "",
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    )


@pytest.mark.parametrize("verifier_name", local_verifier_ui.VERIFIERS)
def test_local_verifier_ui_semantic_parity_on_pass(verifier_name):
    cli = run_cli(verifier_name)
    ui = local_verifier_ui.run_verifier(verifier_name)
    rendered = local_verifier_ui.render_result(ui)
    combined_cli = cli.stdout + cli.stderr
    combined_ui = ui.stdout + ui.stderr

    assert cli.returncode == ui.returncode
    assert local_verifier_ui._extract_status(
        local_verifier_ui.VERIFIERS[verifier_name],
        cli.returncode,
        cli.stdout,
        cli.stderr,
    )[0] == ui.status
    assert ui.status == "PASS"
    assert local_verifier_ui.VERIFIERS[verifier_name].primary_pass_output in rendered
    assert ui.stdout == cli.stdout
    assert ui.stderr == cli.stderr
    assert hash_values(combined_cli) == hash_values(combined_ui)


@pytest.mark.parametrize("verifier_name", local_verifier_ui.VERIFIERS)
def test_local_verifier_ui_hard_fail_rule_on_pass_fixtures(verifier_name):
    cli = run_cli(verifier_name)
    ui = local_verifier_ui.run_verifier(verifier_name)
    spec = local_verifier_ui.VERIFIERS[verifier_name]
    cli_status = local_verifier_ui._extract_status(
        spec,
        cli.returncode,
        cli.stdout,
        cli.stderr,
    )[0]

    assert cli_status == ui.status, (
        f"{verifier_name}: CLI status {cli_status} != UI status {ui.status}"
    )


def test_local_verifier_ui_rejects_unknown_verifier(monkeypatch):
    called = False

    def fake_run(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("subprocess.run should not be called")

    monkeypatch.setattr(local_verifier_ui.subprocess, "run", fake_run)

    with pytest.raises(ValueError):
        local_verifier_ui.run_verifier("not_approved")

    assert called is False


@pytest.mark.parametrize("verifier_name", local_verifier_ui.VERIFIERS)
def test_local_verifier_ui_does_not_modify_fixture_content(verifier_name):
    spec = local_verifier_ui.VERIFIERS[verifier_name]
    before = {
        fixture: hash_file(local_verifier_ui.REPO_ROOT / fixture)
        for fixture in spec.fixture_paths
    }

    local_verifier_ui.run_verifier(verifier_name)

    after = {
        fixture: hash_file(local_verifier_ui.REPO_ROOT / fixture)
        for fixture in spec.fixture_paths
    }
    assert after == before


def test_local_verifier_ui_does_not_store_uploaded_files():
    candidate_dirs = [
        local_verifier_ui.REPO_ROOT / "uploads",
        local_verifier_ui.REPO_ROOT / "upload",
        local_verifier_ui.REPO_ROOT / "tmp_uploads",
    ]
    before = {path: path.exists() for path in candidate_dirs}

    for verifier_name in local_verifier_ui.VERIFIERS:
        local_verifier_ui.run_verifier(verifier_name)

    after = {path: path.exists() for path in candidate_dirs}
    assert after == before


def test_local_verifier_ui_does_not_create_governance_artifacts():
    before = json_artifact_snapshot()

    for verifier_name in local_verifier_ui.VERIFIERS:
        local_verifier_ui.run_verifier(verifier_name)

    after = json_artifact_snapshot()
    assert after == before


def test_local_verifier_ui_does_not_promote_fail_to_pass_for_receipt_index(tmp_path):
    source = (
        local_verifier_ui.REPO_ROOT
        / "examples"
        / "verification_receipt_index"
        / "index.v0.7.json"
    )
    tampered = tmp_path / "index.tampered.v0.7.json"
    index = json.loads(source.read_text(encoding="utf-8-sig"))
    index["receipt_count"] = 999
    tampered.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    override_key = "examples/verification_receipt_index/index.v0.7.json"
    ui = local_verifier_ui.run_verifier(
        "receipt_index",
        fixture_overrides={override_key: str(tampered)},
    )
    spec = local_verifier_ui.VERIFIERS["receipt_index"]
    cli = subprocess.run(
        [sys.executable, spec.script, str(tampered)],
        cwd=local_verifier_ui.REPO_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    cli_status = local_verifier_ui._extract_status(
        spec,
        cli.returncode,
        cli.stdout,
        cli.stderr,
    )[0]

    assert cli_status == "FAIL"
    assert ui.status == "FAIL"
    assert "RECEIPT INDEX VERIFY FAIL" in ui.stderr
    assert ui.stderr == cli.stderr


def test_local_verifier_ui_rejects_unapproved_fixture_override(tmp_path):
    with pytest.raises(ValueError):
        local_verifier_ui.run_verifier(
            "receipt_index",
            fixture_overrides={"examples/not-approved.json": str(tmp_path / "x.json")},
        )


def test_local_verifier_ui_does_not_add_forbidden_words_outside_boundary():
    pages = [local_verifier_ui.render_index()]
    pages.extend(
        local_verifier_ui.render_result(local_verifier_ui.run_verifier(name))
        for name in local_verifier_ui.VERIFIERS
    )

    for page in pages:
        text = strip_boundary(page).lower()
        for word in FORBIDDEN_WORDS:
            assert word not in text


@pytest.mark.parametrize(
    ("verifier_name", "primary_output"),
    [
        ("approval_token", "APPROVAL TOKEN VERIFY PASS"),
        ("reviewer_authority_binding", "REVIEWER AUTHORITY BINDING VERIFY PASS"),
        (
            "decision_envelope_approval_binding",
            "DECISION ENVELOPE APPROVAL BINDING VERIFY PASS",
        ),
        ("evidence_manifest_binding", "EVIDENCE MANIFEST BINDING VERIFY PASS"),
        ("ledger_bundle", "LEDGER BUNDLE VERIFY PASS"),
        ("verification_receipt", "VERIFICATION RECEIPT VERIFY PASS"),
        ("receipt_index", "RECEIPT INDEX VERIFY PASS"),
    ],
)
def test_local_verifier_ui_primary_output_parity(verifier_name, primary_output):
    result = local_verifier_ui.run_verifier(verifier_name)
    rendered = local_verifier_ui.render_result(result)

    assert result.primary_output == primary_output
    assert primary_output in result.stdout
    assert primary_output in rendered
