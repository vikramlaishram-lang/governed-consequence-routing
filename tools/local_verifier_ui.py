#!/usr/bin/env python3
"""
local_verifier_ui.py

Local read-only interface for invoking the approved GCR verifier fixtures.
"""

from __future__ import annotations

import argparse
import html
import subprocess
import sys
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Mapping
from urllib.parse import parse_qs, urlparse


REPO_ROOT = Path(__file__).resolve().parents[1]

APP_TITLE = "Governed Consequence Routing Local Verifier UI"

BOUNDARY_TEXT = """
<section id="boundary">
  <h2>Boundary</h2>
  <p>v0.8 exposes existing verifier results through a local human-facing interface without changing verification semantics.</p>
  <p>The interface does not claim: certified, compliant, legally, production, enterprise, admissible, safe, correct.</p>
  <p>The interface does not create new authority, policy, custody, verification semantics, decisions, approvals, receipts, indexes, bundles, evidence manifests, authority manifests, policy results, or governance claims.</p>
</section>
""".strip()


@dataclass(frozen=True)
class VerifierSpec:
    name: str
    script: str
    fixture_paths: tuple[str, ...]
    args: tuple[str, ...]
    primary_pass_output: str


@dataclass(frozen=True)
class VerifierResult:
    verifier_name: str
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    status: str
    primary_output: str
    fixture_paths: tuple[str, ...]


VERIFIERS: dict[str, VerifierSpec] = {
    "approval_token": VerifierSpec(
        name="approval_token",
        script="tools/verify_approval_token.py",
        fixture_paths=("examples/reviewer_authority/approval_token.v0.3.json",),
        args=("examples/reviewer_authority/approval_token.v0.3.json",),
        primary_pass_output="APPROVAL TOKEN VERIFY PASS",
    ),
    "reviewer_authority_binding": VerifierSpec(
        name="reviewer_authority_binding",
        script="tools/verify_reviewer_authority_binding.py",
        fixture_paths=(
            "examples/reviewer_authority/manifest.v0.3.json",
            "examples/reviewer_authority/approval_token.v0.3.json",
        ),
        args=(
            "--manifest",
            "examples/reviewer_authority/manifest.v0.3.json",
            "--token",
            "examples/reviewer_authority/approval_token.v0.3.json",
        ),
        primary_pass_output="REVIEWER AUTHORITY BINDING VERIFY PASS",
    ),
    "decision_envelope_approval_binding": VerifierSpec(
        name="decision_envelope_approval_binding",
        script="tools/verify_decision_envelope_approval_binding.py",
        fixture_paths=(
            "examples/reviewer_authority/approved_decision_envelope.v0.3.json",
            "examples/reviewer_authority/approval_token.v0.3.json",
            "examples/reviewer_authority/manifest.v0.3.json",
        ),
        args=(
            "--envelope",
            "examples/reviewer_authority/approved_decision_envelope.v0.3.json",
            "--token",
            "examples/reviewer_authority/approval_token.v0.3.json",
            "--manifest",
            "examples/reviewer_authority/manifest.v0.3.json",
        ),
        primary_pass_output="DECISION ENVELOPE APPROVAL BINDING VERIFY PASS",
    ),
    "evidence_manifest_binding": VerifierSpec(
        name="evidence_manifest_binding",
        script="tools/verify_evidence_manifest_binding.py",
        fixture_paths=(
            "examples/evidence_manifest/evidence_bound_decision_envelope.v0.4.json",
            "examples/evidence_manifest/manifest.v0.4.json",
        ),
        args=(
            "--envelope",
            "examples/evidence_manifest/evidence_bound_decision_envelope.v0.4.json",
            "--manifest",
            "examples/evidence_manifest/manifest.v0.4.json",
        ),
        primary_pass_output="EVIDENCE MANIFEST BINDING VERIFY PASS",
    ),
    "ledger_bundle": VerifierSpec(
        name="ledger_bundle",
        script="tools/verify_ledger_bundle.py",
        fixture_paths=("examples/verification_bundle/full_gcr_bundle.v0.5.json",),
        args=("examples/verification_bundle/full_gcr_bundle.v0.5.json",),
        primary_pass_output="LEDGER BUNDLE VERIFY PASS",
    ),
    "verification_receipt": VerifierSpec(
        name="verification_receipt",
        script="tools/verify_verification_receipt.py",
        fixture_paths=("examples/verification_receipt/verification_receipt.v0.6.json",),
        args=("examples/verification_receipt/verification_receipt.v0.6.json",),
        primary_pass_output="VERIFICATION RECEIPT VERIFY PASS",
    ),
    "receipt_index": VerifierSpec(
        name="receipt_index",
        script="tools/verify_receipt_index.py",
        fixture_paths=("examples/verification_receipt_index/index.v0.7.json",),
        args=("examples/verification_receipt_index/index.v0.7.json",),
        primary_pass_output="RECEIPT INDEX VERIFY PASS",
    ),
}


def _primary_fail_output(spec: VerifierSpec) -> str:
    return spec.primary_pass_output.replace(" PASS", " FAIL")


def _extract_status(spec: VerifierSpec, returncode: int, stdout: str, stderr: str) -> tuple[str, str]:
    output = stdout + stderr
    if spec.primary_pass_output in output and returncode == 0:
        return "PASS", spec.primary_pass_output

    fail_output = _primary_fail_output(spec)
    if fail_output in output or returncode != 0:
        return "FAIL", fail_output if fail_output in output else ""

    return "FAIL", ""


def _apply_fixture_overrides(
    spec: VerifierSpec,
    fixture_overrides: Mapping[str, str] | None,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if not fixture_overrides:
        return spec.args, spec.fixture_paths

    args = list(spec.args)
    fixture_paths = list(spec.fixture_paths)

    for original, replacement in fixture_overrides.items():
        if original not in spec.fixture_paths:
            raise ValueError(f"Fixture override is not allowed for {spec.name}: {original}")

        fixture_paths[fixture_paths.index(original)] = replacement
        args = [replacement if value == original else value for value in args]

    return tuple(args), tuple(fixture_paths)


def run_verifier(
    verifier_name: str,
    *,
    fixture_overrides: Mapping[str, str] | None = None,
) -> VerifierResult:
    if verifier_name not in VERIFIERS:
        raise ValueError(f"Unknown verifier: {verifier_name}")

    spec = VERIFIERS[verifier_name]
    args, fixture_paths = _apply_fixture_overrides(spec, fixture_overrides)
    run_command = (sys.executable, spec.script, *args)
    display_command = ("python", spec.script, *args)

    completed = subprocess.run(
        run_command,
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    status, primary_output = _extract_status(
        spec,
        completed.returncode,
        completed.stdout,
        completed.stderr,
    )

    return VerifierResult(
        verifier_name=verifier_name,
        command=display_command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        status=status,
        primary_output=primary_output,
        fixture_paths=fixture_paths,
    )


def render_index() -> str:
    items = "\n".join(
        f'<li><a href="/verify?name={html.escape(name)}">{html.escape(name)}</a></li>'
        for name in VERIFIERS
    )
    return _page(
        "Verifier Choices",
        f"""
        <section>
          <h2>Verifier Choices</h2>
          <ul>{items}</ul>
        </section>
        {BOUNDARY_TEXT}
        """,
    )


def render_result(result: VerifierResult) -> str:
    command = " ".join(result.command)
    fixtures = "\n".join(html.escape(path) for path in result.fixture_paths)
    return _page(
        f"Result {result.verifier_name}",
        f"""
        <section>
          <h2>{html.escape(result.verifier_name)}</h2>
          <p>Status: <strong>{html.escape(result.status)}</strong></p>
          <p>Primary output: <code>{html.escape(result.primary_output)}</code></p>
          <h3>Command</h3>
          <pre>{html.escape(command)}</pre>
          <h3>Fixture Paths</h3>
          <pre>{fixtures}</pre>
          <h3>stdout</h3>
          <pre>{html.escape(result.stdout)}</pre>
          <h3>stderr</h3>
          <pre>{html.escape(result.stderr)}</pre>
          <h3>Exit Status</h3>
          <pre>{result.returncode}</pre>
        </section>
        {BOUNDARY_TEXT}
        """,
    )


def render_verifier(verifier_name: str) -> str:
    return render_result(run_verifier(verifier_name))


def _page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(APP_TITLE)} - {html.escape(title)}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; max-width: 72rem; }}
    pre {{ background: #f4f4f4; padding: 1rem; overflow-x: auto; }}
    code {{ background: #f4f4f4; padding: 0.15rem 0.25rem; }}
  </style>
</head>
<body>
  <h1>{html.escape(APP_TITLE)}</h1>
  {body}
</body>
</html>
"""


class LocalVerifierHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        try:
            if parsed.path == "/":
                self._send_html(200, render_index())
                return

            if parsed.path == "/verify":
                names = parse_qs(parsed.query).get("name", [])
                if len(names) != 1 or names[0] not in VERIFIERS:
                    self._send_html(404, _page("Unknown", "<p>Unknown verifier.</p>"))
                    return
                self._send_html(200, render_verifier(names[0]))
                return

            self._send_html(404, _page("Not Found", "<p>Not found.</p>"))
        except Exception as exc:
            self._send_html(500, _page("Error", f"<pre>{html.escape(str(exc))}</pre>"))

    def log_message(self, format: str, *args) -> None:
        return

    def _send_html(self, status_code: int, body: str) -> None:
        payload = body.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def serve(host: str, port: int) -> None:
    server = ThreadingHTTPServer((host, port), LocalVerifierHandler)
    print(f"{APP_TITLE} listening on http://{host}:{port}")
    server.serve_forever()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=APP_TITLE)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    serve(args.host, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
