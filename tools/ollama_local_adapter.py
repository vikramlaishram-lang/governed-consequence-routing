import argparse
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_MODEL = "qwen3:8b"
DEFAULT_TOOL_NAME = "read_file"
DEFAULT_PATH = "src/app.py"
DEFAULT_POLICY_VERSION = "policy-v0.1-local-demo"
DEFAULT_RUNTIME_ID = "ollama-local-adapter-runtime-v0.1"
DEFAULT_AGENT_ID = "ollama-local-agent"

SAFE_TOOL_NAMES = {"read_file"}


class AdapterError(RuntimeError):
    pass


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def default_prompt(tool_name, path):
    return (
        "You are an agent. Propose one safe read-only tool call. "
        "Return JSON only with keys tool_name and path. "
        f"Use tool_name {tool_name} and path {path}."
    )


def run_ollama(model, prompt, timeout_seconds):
    result = subprocess.run(
        ["ollama", "run", model, prompt],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
        timeout=timeout_seconds,
    )

    if result.returncode != 0:
        raise AdapterError(
            "OLLAMA_CALL_FAILED\n"
            f"stdout:\n{result.stdout}\n\n"
            f"stderr:\n{result.stderr}"
        )

    return result.stdout.strip()


def extract_json_object(text):
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        return {}

    candidate = text[start : end + 1]

    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        return {}

    if not isinstance(parsed, dict):
        return {}

    return parsed


def normalize_tool_call(parsed_proposal, default_tool_name, default_path):
    proposed_name = parsed_proposal.get("tool_name") or parsed_proposal.get("name")
    proposed_path = parsed_proposal.get("path")

    if proposed_path is None and isinstance(parsed_proposal.get("arguments"), dict):
        proposed_path = parsed_proposal["arguments"].get("path")

    tool_name = str(proposed_name or default_tool_name).strip()
    path = str(proposed_path or default_path).strip()

    if tool_name not in SAFE_TOOL_NAMES:
        tool_name = default_tool_name

    if not path:
        path = default_path

    return {
        "name": tool_name,
        "arguments": {
            "path": path,
        },
    }


def build_governance_event(
    model,
    ollama_version,
    raw_proposal,
    parsed_proposal,
    tool_call,
    decision,
    policy_version,
    runtime_id,
    agent_id,
):
    event_id = str(uuid.uuid4())

    return {
        "created_at": utc_now(),
        "runtime": {
            "runtime_id": runtime_id,
            "mode": "SHADOW_SAFE",
        },
        "agent": {
            "id": agent_id,
        },
        "model": {
            "provider": "ollama",
            "name": model,
            "version": ollama_version,
            "role": "proposal_only",
            "note": "Ollama proposed; policy still decides.",
        },
        "tool_call": tool_call,
        "policy": {
            "version": policy_version,
        },
        "drf_decision": {
            "decision": decision,
            "basis": "POLICY_RULE",
            "reason": "Local adapter smoke test records the proposed consequence without executing it.",
            "rule_id": "local-ollama-adapter-smoke",
        },
        "omtir_evidence": {
            "model_proposal_raw": raw_proposal,
            "model_proposal_parsed": parsed_proposal,
            "adapter_boundary": "proposal_capture_only_no_execution",
        },
        "wal": {
            "sequence": 1,
            "hash": f"ollama-local-adapter-smoke-{event_id}",
        },
    }


def write_jsonl_event(path, event):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n"
    path.write_text(payload, encoding="utf-8")


def run_command(args, cwd):
    return subprocess.run(
        args,
        cwd=str(cwd),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def run_promotion_and_verification(repo_root, event_path, envelope_path):
    promoter = repo_root / "tools" / "promote_to_envelope.py"
    verifier = repo_root / "tools" / "verify_envelope_chain.py"

    promote_result = run_command(
        [
            sys.executable,
            str(promoter),
            str(event_path),
            "-o",
            str(envelope_path),
            "--verify",
        ],
        cwd=repo_root,
    )

    print(promote_result.stdout, end="")
    if promote_result.returncode != 0:
        raise AdapterError(
            "PROMOTION_FAILED\n"
            f"stdout:\n{promote_result.stdout}\n\n"
            f"stderr:\n{promote_result.stderr}"
        )

    verify_result = run_command(
        [
            sys.executable,
            str(verifier),
            str(envelope_path),
            "--mutate",
            "--verbose",
        ],
        cwd=repo_root,
    )

    print(verify_result.stdout, end="")
    if verify_result.returncode != 0:
        raise AdapterError(
            "VERIFICATION_FAILED\n"
            f"stdout:\n{verify_result.stdout}\n\n"
            f"stderr:\n{verify_result.stderr}"
        )


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Capture an Ollama proposal as a governance event, promote it into "
            "a decision envelope, and verify it without executing the tool call."
        )
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--ollama-version", default="0.30.10")
    parser.add_argument("--tool-name", default=DEFAULT_TOOL_NAME)
    parser.add_argument("--path", default=DEFAULT_PATH)
    parser.add_argument("--decision", default="ALLOW", choices=["ALLOW", "DENY", "REQUEST_REVIEW"])
    parser.add_argument("--policy-version", default=DEFAULT_POLICY_VERSION)
    parser.add_argument("--runtime-id", default=DEFAULT_RUNTIME_ID)
    parser.add_argument("--agent-id", default=DEFAULT_AGENT_ID)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--prompt", default=None)
    parser.add_argument(
        "--proposal-text",
        default=None,
        help="Bypass Ollama and use this text as the proposal. Useful for tests.",
    )
    parser.add_argument("--event-out", default="wal/ollama-local-adapter-event.jsonl")
    parser.add_argument("--envelope-out", default="wal/ollama-local-adapter-envelopes.json")
    return parser.parse_args()


def main():
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    prompt = args.prompt or default_prompt(args.tool_name, args.path)

    try:
        raw_proposal = args.proposal_text
        if raw_proposal is None:
            raw_proposal = run_ollama(args.model, prompt, args.timeout_seconds)

        parsed_proposal = extract_json_object(raw_proposal)
        tool_call = normalize_tool_call(parsed_proposal, args.tool_name, args.path)

        event = build_governance_event(
            model=args.model,
            ollama_version=args.ollama_version,
            raw_proposal=raw_proposal,
            parsed_proposal=parsed_proposal,
            tool_call=tool_call,
            decision=args.decision,
            policy_version=args.policy_version,
            runtime_id=args.runtime_id,
            agent_id=args.agent_id,
        )

        event_path = repo_root / args.event_out
        envelope_path = repo_root / args.envelope_out

        write_jsonl_event(event_path, event)

        print(f"OLLAMA ADAPTER EVENT WRITTEN: {event_path}")
        print("BOUNDARY: proposal captured only; no tool execution performed")

        run_promotion_and_verification(
            repo_root=repo_root,
            event_path=event_path,
            envelope_path=envelope_path,
        )

        print("OLLAMA ADAPTER PASS: proposal captured, promoted, and verified")
        return 0

    except AdapterError as exc:
        print(f"OLLAMA ADAPTER FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())