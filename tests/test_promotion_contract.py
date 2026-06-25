import json
import subprocess
import sys
from pathlib import Path


FIXTURE_EVENT_PATH = Path("tests/fixtures/governance_events/ollama_event_sample.jsonl")
PROMOTER = Path("tools/promote_to_envelope.py")
VERIFIER = Path("tools/verify_envelope_chain.py")


def run_command(args):
    return subprocess.run(
        [sys.executable, *args],
        text=True,
        capture_output=True,
        check=False,
    )


def test_promoter_cli_promotes_fixture_and_verifies_chain(tmp_path):
    output_path = tmp_path / "envelopes.json"

    result = run_command([
        str(PROMOTER),
        str(FIXTURE_EVENT_PATH),
        "-o",
        str(output_path),
        "--verify",
    ])

    assert result.returncode == 0, result.stderr
    assert "PROMOTION PASS: 3 envelope(s)" in result.stdout
    assert "PROMOTION VERIFY PASS" in result.stdout
    assert output_path.exists()

    envelopes = json.loads(output_path.read_text(encoding="utf-8"))

    assert len(envelopes) == 3
    assert envelopes[0]["decision"] == "ALLOW"
    assert envelopes[1]["decision"] == "DENY"
    assert envelopes[2]["decision"] == "REQUEST_REVIEW"


def test_promoter_output_contains_no_source_event_hash(tmp_path):
    output_path = tmp_path / "envelopes.json"

    result = run_command([
        str(PROMOTER),
        str(FIXTURE_EVENT_PATH),
        "-o",
        str(output_path),
        "--verify",
    ])

    assert result.returncode == 0, result.stderr

    envelopes = json.loads(output_path.read_text(encoding="utf-8"))

    for envelope in envelopes:
        assert "source_event_hash" not in envelope


def test_promoted_output_passes_independent_verifier(tmp_path):
    output_path = tmp_path / "envelopes.json"

    promote_result = run_command([
        str(PROMOTER),
        str(FIXTURE_EVENT_PATH),
        "-o",
        str(output_path),
        "--verify",
    ])

    assert promote_result.returncode == 0, promote_result.stderr

    verify_result = run_command([
        str(VERIFIER),
        str(output_path),
        "--mutate",
        "--verbose",
    ])

    assert verify_result.returncode == 0, verify_result.stderr
    assert "VERIFIER PASS: 3 envelope(s) valid" in verify_result.stdout
    assert "MUTATION CHECK PASS: all mutations detected" in verify_result.stdout


def test_promoter_fails_when_required_tool_call_is_missing(tmp_path):
    bad_event_path = tmp_path / "bad-event.jsonl"
    output_path = tmp_path / "envelopes.json"

    bad_event_path.write_text(
        json.dumps({
            "created_at": "2026-06-25T00:00:00Z",
            "runtime": {"runtime_id": "local-reference-runtime-v0.1"},
            "drf_decision": {
                "decision": "ALLOW",
                "reason": "bad event missing tool_call"
            }
        }) + "\n",
        encoding="utf-8",
    )

    result = run_command([
        str(PROMOTER),
        str(bad_event_path),
        "-o",
        str(output_path),
        "--verify",
    ])

    assert result.returncode != 0
    assert "PROMOTION FAIL" in result.stderr
    assert "PROMOTION_FAILED_MISSING_REQUIRED_FIELD" in result.stderr