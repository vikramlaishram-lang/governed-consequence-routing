import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


BUNDLE_VERSION = "verification_bundle.v0.2"
SUMMARY_VERSION = "verification_summary.v0.2"
VERIFIER_VERSION = "decision-envelope-verifier-v0.1"
DEFAULT_SCHEMA_PATH = Path("schemas/decision_envelope_v0.1.schema.json")
REPO_ROOT = Path(__file__).resolve().parents[1]

PROOF_BOUNDARY = (
    "This verification bundle is a reproducible local custody artifact. "
    "It does not claim legal admissibility, third-party validation, external "
    "notarization, production custody, or non-repudiation."
)


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def load_envelopes(source):
    source = Path(source)

    if source.is_dir():
        envelopes = []
        for path in sorted(source.glob("*.json")):
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                envelopes.extend(loaded)
            else:
                envelopes.append(loaded)
        return envelopes

    if source.suffix == ".jsonl":
        envelopes = []
        for line in source.read_text(encoding="utf-8").splitlines():
            if line.strip():
                envelopes.append(json.loads(line))
        return envelopes

    loaded = json.loads(source.read_text(encoding="utf-8"))
    if isinstance(loaded, list):
        return loaded
    return [loaded]


def run_verifier(source, mutate):
    args = [
        sys.executable,
        "tools/verify_envelope_chain.py",
        str(source),
    ]

    if mutate:
        args.extend(["--mutate", "--verbose"])

    return subprocess.run(
        args,
        cwd=str(REPO_ROOT),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def parse_detected_mutations(verifier_stdout):
    detected = []

    for line in verifier_stdout.splitlines():
        stripped = line.strip()
        if " mutation:" in stripped and "DETECTED" in stripped:
            detected.append(stripped.split(" mutation:", 1)[0])

    return detected


def unique_values(envelopes, field_name):
    values = []

    for envelope in envelopes:
        value = envelope.get(field_name)
        if value is not None and value not in values:
            values.append(value)

    return values


def build_bundle(source, schema_path, mutate):
    source = Path(source)
    schema_path = Path(schema_path)

    envelopes = load_envelopes(source)
    if not envelopes:
        raise RuntimeError("No envelopes found for verification bundle export.")

    verifier_result = run_verifier(source, mutate=mutate)
    verification_passed = verifier_result.returncode == 0

    if not verification_passed:
        raise RuntimeError(
            "Verifier failed while exporting bundle.\n"
            f"stdout:\n{verifier_result.stdout}\n\n"
            f"stderr:\n{verifier_result.stderr}"
        )

    detected_mutations = parse_detected_mutations(verifier_result.stdout)
    mutation_check_passed = (
        "MUTATION CHECK PASS: all mutations detected" in verifier_result.stdout
        if mutate
        else None
    )

    source_payload_hash = sha256_bytes(
        canonical_json(envelopes).encode("utf-8")
    )

    return {
        "bundle_version": BUNDLE_VERSION,
        "created_at": utc_now(),
        "verifier_version": VERIFIER_VERSION,
        "schema_path": str(schema_path).replace("\\", "/"),
        "schema_hash": sha256_bytes(schema_path.read_bytes()),
        "envelope_source": str(source).replace("\\", "/"),
        "envelope_source_hash": source_payload_hash,
        "envelope_count": len(envelopes),
        "first_record_hash": envelopes[0].get("record_hash"),
        "final_record_hash": envelopes[-1].get("record_hash"),
        "chain_head": envelopes[-1].get("record_hash"),
        "tamper_evidence_modes": unique_values(envelopes, "tamper_evidence_mode"),
        "key_ids": unique_values(envelopes, "key_id"),
        "verification_result": "PASS",
        "mutation_checks_requested": mutate,
        "mutation_check_result": (
            "PASS" if mutation_check_passed else "NOT_REQUESTED"
        ),
        "detected_mutation_classes": detected_mutations,
        "verifier_stdout": verifier_result.stdout,
        "verifier_stderr": verifier_result.stderr,
        "proof_boundary": PROOF_BOUNDARY,
    }


def build_summary(bundle):
    return {
        "summary_version": SUMMARY_VERSION,
        "created_at": bundle["created_at"],
        "verifier_version": bundle["verifier_version"],
        "schema_path": bundle["schema_path"],
        "schema_hash": bundle["schema_hash"],
        "envelope_source": bundle["envelope_source"],
        "envelope_source_hash": bundle["envelope_source_hash"],
        "envelope_count": bundle["envelope_count"],
        "first_record_hash": bundle["first_record_hash"],
        "final_record_hash": bundle["final_record_hash"],
        "chain_head": bundle["chain_head"],
        "tamper_evidence_modes": bundle["tamper_evidence_modes"],
        "key_ids": bundle["key_ids"],
        "verification_result": bundle["verification_result"],
        "mutation_checks_requested": bundle["mutation_checks_requested"],
        "mutation_check_result": bundle["mutation_check_result"],
        "detected_mutation_classes": bundle["detected_mutation_classes"],
        "proof_boundary": bundle["proof_boundary"],
    }


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, sort_keys=True) + "\n"
    path.write_text(payload, encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Export v0.2 custody artifacts for a decision-envelope chain."
    )
    parser.add_argument("source", help="Envelope JSON file, JSONL file, or directory.")
    parser.add_argument(
        "--schema-path",
        default=str(DEFAULT_SCHEMA_PATH),
        help="Path to the decision envelope schema.",
    )
    parser.add_argument(
        "--bundle-out",
        required=True,
        help="Output path for the full verification bundle JSON.",
    )
    parser.add_argument(
        "--summary-out",
        default=None,
        help="Optional output path for a concise verification summary JSON.",
    )
    parser.add_argument(
        "--mutate",
        action="store_true",
        help="Run verifier mutation checks and include mutation results.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        bundle = build_bundle(
            source=args.source,
            schema_path=args.schema_path,
            mutate=args.mutate,
        )
        write_json(args.bundle_out, bundle)

        print(f"VERIFICATION BUNDLE PASS: wrote {args.bundle_out}")
        print(f"envelope_count: {bundle['envelope_count']}")
        print(f"chain_head: {bundle['chain_head']}")
        print(f"schema_hash: {bundle['schema_hash']}")
        print(f"tamper_evidence_modes: {', '.join(bundle['tamper_evidence_modes'])}")
        print(f"mutation_check_result: {bundle['mutation_check_result']}")

        if args.summary_out:
            summary = build_summary(bundle)
            write_json(args.summary_out, summary)
            print(f"VERIFICATION SUMMARY PASS: wrote {args.summary_out}")

        return 0
    except Exception as exc:
        print(f"VERIFICATION BUNDLE FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())