import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path("tools/ollama_local_adapter.py")


def load_module():
    spec = importlib.util.spec_from_file_location("ollama_local_adapter", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_extract_json_object_from_qwen_thinking_output():
    module = load_module()

    text = """
Thinking...
I will propose a safe read-only call.
...done thinking.

{"tool_name": "read_file", "path": "src/app.py"}
"""

    parsed = module.extract_json_object(text)

    assert parsed == {
        "tool_name": "read_file",
        "path": "src/app.py",
    }


def test_extract_json_object_returns_empty_dict_for_non_json_output():
    module = load_module()

    parsed = module.extract_json_object("no json here")

    assert parsed == {}


def test_normalize_tool_call_allows_read_file_only():
    module = load_module()

    tool_call = module.normalize_tool_call(
        {"tool_name": "read_file", "path": "src/app.py"},
        "read_file",
        "fallback.py",
    )

    assert tool_call == {
        "name": "read_file",
        "arguments": {
            "path": "src/app.py",
        },
    }


def test_normalize_tool_call_falls_back_for_unsafe_tool_name():
    module = load_module()

    tool_call = module.normalize_tool_call(
        {"tool_name": "delete_file", "path": "important.db"},
        "read_file",
        "src/app.py",
    )

    assert tool_call == {
        "name": "read_file",
        "arguments": {
            "path": "important.db",
        },
    }


def test_build_governance_event_preserves_proposal_only_boundary():
    module = load_module()

    event = module.build_governance_event(
        model="qwen3:8b",
        ollama_version="0.30.10",
        raw_proposal='{"tool_name":"read_file","path":"src/app.py"}',
        parsed_proposal={"tool_name": "read_file", "path": "src/app.py"},
        tool_call={"name": "read_file", "arguments": {"path": "src/app.py"}},
        decision="ALLOW",
        policy_version="policy-v0.1-local-demo",
        runtime_id="ollama-local-adapter-runtime-v0.1",
        agent_id="ollama-local-agent",
    )

    assert event["model"]["provider"] == "ollama"
    assert event["model"]["role"] == "proposal_only"
    assert event["model"]["note"] == "Ollama proposed; policy still decides."
    assert event["drf_decision"]["decision"] == "ALLOW"
    assert event["omtir_evidence"]["adapter_boundary"] == "proposal_capture_only_no_execution"


def test_write_jsonl_event_writes_one_json_line(tmp_path):
    module = load_module()

    path = tmp_path / "event.jsonl"
    event = {"a": 1, "b": {"c": 2}}

    module.write_jsonl_event(path, event)

    lines = path.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 1
    assert json.loads(lines[0]) == event