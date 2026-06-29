#!/usr/bin/env python3
"""
build_governance_record_graph.py

Build a local v1.0 GCR governance record graph projection.

The graph is a projection, not the source of truth. JSON artifacts remain the
source of truth and existing verifiers remain the proof mechanism.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

from jsonschema import Draft202012Validator, FormatChecker


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas/governance_record_graph_v1.0.schema.json"
SCHEMA_VERSION = "governance_record_graph_v1.0"

GRAPH_ID = "10101010-1010-4010-8010-101010101010"
CREATED_AT = "2026-06-29T00:00:00Z"

SOURCE_ARTIFACTS = [
    (
        "runtime-proposal-v0.9",
        "RUNTIME_PROPOSAL",
        "examples/runtime_proposal/proposal.v0.9.json",
    ),
    (
        "approval-token-v0.3",
        "APPROVAL_TOKEN",
        "examples/reviewer_authority/approval_token.v0.3.json",
    ),
    (
        "reviewer-authority-manifest-v0.3",
        "REVIEWER_AUTHORITY_MANIFEST",
        "examples/reviewer_authority/manifest.v0.3.json",
    ),
    (
        "approved-decision-envelope-v0.3",
        "DECISION_ENVELOPE",
        "examples/reviewer_authority/approved_decision_envelope.v0.3.json",
    ),
    (
        "evidence-manifest-v0.4",
        "EVIDENCE_MANIFEST",
        "examples/evidence_manifest/manifest.v0.4.json",
    ),
    (
        "evidence-bound-decision-envelope-v0.4",
        "DECISION_ENVELOPE",
        "examples/evidence_manifest/evidence_bound_decision_envelope.v0.4.json",
    ),
    (
        "verification-bundle-v0.5",
        "VERIFICATION_BUNDLE",
        "examples/verification_bundle/full_gcr_bundle.v0.5.json",
    ),
    (
        "verification-receipt-v0.6",
        "VERIFICATION_RECEIPT",
        "examples/verification_receipt/verification_receipt.v0.6.json",
    ),
    (
        "receipt-index-v0.7",
        "RECEIPT_INDEX",
        "examples/verification_receipt_index/index.v0.7.json",
    ),
    (
        "local-verifier-ui-v0.8",
        "LOCAL_VERIFIER_UI",
        "tools/local_verifier_ui.py",
    ),
]

VERIFIER_RESULTS = [
    (
        "runtime-proposal-verify",
        "capture_runtime_proposal --verify-only",
        "PASS",
        "RUNTIME PROPOSAL VERIFY PASS",
        ["runtime-proposal-v0.9"],
    ),
    (
        "approval-token-verify",
        "verify_approval_token",
        "PASS",
        "APPROVAL TOKEN VERIFY PASS",
        ["approval-token-v0.3"],
    ),
    (
        "reviewer-authority-binding-verify",
        "verify_reviewer_authority_binding",
        "PASS",
        "REVIEWER AUTHORITY BINDING VERIFY PASS",
        ["reviewer-authority-manifest-v0.3", "approval-token-v0.3"],
    ),
    (
        "decision-envelope-approval-binding-verify",
        "verify_decision_envelope_approval_binding",
        "PASS",
        "DECISION ENVELOPE APPROVAL BINDING VERIFY PASS",
        [
            "approved-decision-envelope-v0.3",
            "approval-token-v0.3",
            "reviewer-authority-manifest-v0.3",
        ],
    ),
    (
        "evidence-manifest-binding-verify",
        "verify_evidence_manifest_binding",
        "PASS",
        "EVIDENCE MANIFEST BINDING VERIFY PASS",
        ["evidence-bound-decision-envelope-v0.4", "evidence-manifest-v0.4"],
    ),
    (
        "ledger-bundle-verify",
        "verify_ledger_bundle",
        "PASS",
        "LEDGER BUNDLE VERIFY PASS",
        ["verification-bundle-v0.5"],
    ),
    (
        "verification-receipt-verify",
        "verify_verification_receipt",
        "PASS",
        "VERIFICATION RECEIPT VERIFY PASS",
        ["verification-receipt-v0.6"],
    ),
    (
        "receipt-index-verify",
        "verify_receipt_index",
        "PASS",
        "RECEIPT INDEX VERIFY PASS",
        ["receipt-index-v0.7"],
    ),
    (
        "local-verifier-ui-inspection",
        "local_verifier_ui",
        "PASS",
        "CLI/UI SEMANTIC PARITY PASS",
        ["local-verifier-ui-v0.8"],
    ),
]

PROOF_BOUNDARY = {
    "proves": [
        "v1.0 proves local governance-record continuity.",
        "v1.0 proves that GCR can assemble its verified local artifacts into an end-to-end governance record graph for an AI-agent consequence, linking proposal capture, authority, evidence, verification, receipt, index, and human inspection without creating new authority or execution.",
        "The graph is an inspectable projection of verified local relationships.",
    ],
    "does_not_prove": [
        "production custody",
        "external identity",
        "legal admissibility",
        "regulatory compliance",
        "real-world evidence truth",
        "execution safety",
        "hosted product readiness",
        "RAG correctness",
        "retrieval quality",
        "graph database production readiness",
        "ontology completeness",
        "external notarization",
        "clinical safety",
        "financial advice suitability",
        "enterprise compliance",
        "SSO-backed identity",
        "production identity",
        "non-repudiation",
        "correctness of the underlying AI action",
        "legal validity of approval",
        "execution authority",
    ],
}


class GovernanceRecordGraphBuildError(Exception):
    """Raised when graph construction fails."""


def canonical_json(value: Dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def compute_graph_hash(graph: Dict[str, Any]) -> str:
    material = copy.deepcopy(graph)
    material.pop("graph_hash", None)
    return sha256_text(canonical_json(material))


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise GovernanceRecordGraphBuildError(f"INPUT_NOT_FOUND: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise GovernanceRecordGraphBuildError(f"JSON_INVALID: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise GovernanceRecordGraphBuildError(f"INPUT_MUST_BE_JSON_OBJECT: {path}")
    return value


def load_schema(path: Path = SCHEMA_PATH) -> Dict[str, Any]:
    schema = load_json(path)
    Draft202012Validator.check_schema(schema)
    return schema


def validate_schema(graph: Dict[str, Any], schema: Dict[str, Any]) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(graph), key=lambda error: error.path)
    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.path) or "<root>"
        raise GovernanceRecordGraphBuildError(
            f"GOVERNANCE_RECORD_GRAPH_SCHEMA_INVALID at {location}: {first.message}"
        )


def artifact_hash(relative_path: str) -> str:
    path = REPO_ROOT / relative_path
    if not path.exists():
        raise GovernanceRecordGraphBuildError(f"SOURCE_ARTIFACT_NOT_FOUND: {relative_path}")
    return sha256_bytes(path.read_bytes())


def source_artifacts() -> List[Dict[str, Any]]:
    return [
        {
            "artifact_id": artifact_id,
            "artifact_type": artifact_type,
            "path": path,
            "sha256": artifact_hash(path),
        }
        for artifact_id, artifact_type, path in SOURCE_ARTIFACTS
    ]


def verifier_results() -> List[Dict[str, Any]]:
    return [
        {
            "verifier_id": verifier_id,
            "verifier_name": verifier_name,
            "status": status,
            "primary_output": primary_output,
            "source_artifact_ids": source_artifact_ids,
        }
        for verifier_id, verifier_name, status, primary_output, source_artifact_ids in VERIFIER_RESULTS
    ]


def node(
    node_id: str,
    node_type: str,
    label: str,
    source_artifact_ids: Iterable[str],
) -> Dict[str, Any]:
    return {
        "node_id": node_id,
        "node_type": node_type,
        "label": label,
        "source_artifact_ids": list(source_artifact_ids),
    }


def edge(
    edge_id: str,
    edge_type: str,
    from_node: str,
    to_node: str,
    source_artifact_ids: Iterable[str],
    verifier_result_ids: Iterable[str] = (),
) -> Dict[str, Any]:
    return {
        "edge_id": edge_id,
        "edge_type": edge_type,
        "from_node": from_node,
        "to_node": to_node,
        "derived_from": {
            "source_artifact_ids": list(source_artifact_ids),
            "verifier_result_ids": list(verifier_result_ids),
        },
    }


def build_nodes() -> List[Dict[str, Any]]:
    return [
        node("runtime-proposal-001", "RuntimeProposal", "Runtime proposal v0.9", ["runtime-proposal-v0.9"]),
        node("agent-001", "Agent", "simulated-coding-agent", ["runtime-proposal-v0.9"]),
        node("consequence-001", "Consequence", "PRODUCTION_STATE_CHANGE / NOT_EXECUTED / REQUIRES_GOVERNANCE", ["runtime-proposal-v0.9"]),
        node("decision-envelope-001", "DecisionEnvelope", "Approved decision envelope v0.3", ["approved-decision-envelope-v0.3"]),
        node("approval-token-001", "ApprovalToken", "Approval token v0.3", ["approval-token-v0.3"]),
        node("reviewer-authority-001", "ReviewerAuthorityManifest", "Reviewer authority manifest v0.3", ["reviewer-authority-manifest-v0.3"]),
        node("evidence-manifest-001", "EvidenceManifest", "Evidence manifest v0.4", ["evidence-manifest-v0.4"]),
        node("evidence-item-001", "EvidenceItem", "Admitted evidence item from evidence manifest", ["evidence-manifest-v0.4"]),
        node("verification-bundle-001", "VerificationBundle", "Portable verification bundle v0.5", ["verification-bundle-v0.5"]),
        node("verification-receipt-001", "VerificationReceipt", "Verification receipt v0.6", ["verification-receipt-v0.6"]),
        node("receipt-index-001", "ReceiptIndex", "Verification receipt index v0.7", ["receipt-index-v0.7"]),
        node("verifier-result-001", "VerifierResult", "Approved local verifier result set", ["verification-bundle-v0.5", "verification-receipt-v0.6", "receipt-index-v0.7"]),
        node("local-verifier-ui-001", "LocalVerifierUI", "Local verifier UI v0.8", ["local-verifier-ui-v0.8"]),
    ]


def build_edges() -> List[Dict[str, Any]]:
    return [
        edge("edge-001", "PROPOSED_BY", "runtime-proposal-001", "agent-001", ["runtime-proposal-v0.9"], ["runtime-proposal-verify"]),
        edge("edge-002", "NORMALIZED_TO", "runtime-proposal-001", "consequence-001", ["runtime-proposal-v0.9"], ["runtime-proposal-verify"]),
        edge("edge-003", "CLASSIFIED_AS", "consequence-001", "decision-envelope-001", ["runtime-proposal-v0.9", "approved-decision-envelope-v0.3"], ["runtime-proposal-verify", "decision-envelope-approval-binding-verify"]),
        edge("edge-004", "HAS_EXECUTION_STATUS", "runtime-proposal-001", "consequence-001", ["runtime-proposal-v0.9"], ["runtime-proposal-verify"]),
        edge("edge-005", "HAS_AUTHORIZATION_STATUS", "runtime-proposal-001", "consequence-001", ["runtime-proposal-v0.9"], ["runtime-proposal-verify"]),
        edge("edge-006", "BOUND_TO", "decision-envelope-001", "approval-token-001", ["approved-decision-envelope-v0.3", "approval-token-v0.3"], ["decision-envelope-approval-binding-verify"]),
        edge("edge-007", "AUTHORIZED_BY", "approval-token-001", "reviewer-authority-001", ["approval-token-v0.3", "reviewer-authority-manifest-v0.3"], ["reviewer-authority-binding-verify"]),
        edge("edge-008", "SUPPORTED_BY", "decision-envelope-001", "evidence-manifest-001", ["evidence-bound-decision-envelope-v0.4", "evidence-manifest-v0.4"], ["evidence-manifest-binding-verify"]),
        edge("edge-009", "CONTAINS", "evidence-manifest-001", "evidence-item-001", ["evidence-manifest-v0.4"], ["evidence-manifest-binding-verify"]),
        edge("edge-010", "CONTAINS", "verification-bundle-001", "decision-envelope-001", ["verification-bundle-v0.5", "approved-decision-envelope-v0.3"], ["ledger-bundle-verify"]),
        edge("edge-011", "CONTAINS", "verification-bundle-001", "approval-token-001", ["verification-bundle-v0.5", "approval-token-v0.3"], ["ledger-bundle-verify"]),
        edge("edge-012", "CONTAINS", "verification-bundle-001", "evidence-manifest-001", ["verification-bundle-v0.5", "evidence-manifest-v0.4"], ["ledger-bundle-verify"]),
        edge("edge-013", "VERIFIED_BY", "verification-bundle-001", "verifier-result-001", ["verification-bundle-v0.5"], ["ledger-bundle-verify"]),
        edge("edge-014", "RECEIPT_FOR", "verification-receipt-001", "verification-bundle-001", ["verification-receipt-v0.6", "verification-bundle-v0.5"], ["verification-receipt-verify"]),
        edge("edge-015", "INDEXED_IN", "verification-receipt-001", "receipt-index-001", ["verification-receipt-v0.6", "receipt-index-v0.7"], ["receipt-index-verify"]),
        edge("edge-016", "DISPLAYED_BY", "verifier-result-001", "local-verifier-ui-001", ["local-verifier-ui-v0.8"], ["local-verifier-ui-inspection"]),
        edge("edge-017", "DERIVED_FROM", "local-verifier-ui-001", "runtime-proposal-001", ["runtime-proposal-v0.9", "local-verifier-ui-v0.8"], ["runtime-proposal-verify", "local-verifier-ui-inspection"]),
    ]


def build_graph() -> Dict[str, Any]:
    graph = {
        "created_at": CREATED_AT,
        "edges": build_edges(),
        "graph_hash": "sha256:" + ("0" * 64),
        "graph_id": GRAPH_ID,
        "nodes": build_nodes(),
        "proof_boundary": PROOF_BOUNDARY,
        "schema_version": SCHEMA_VERSION,
        "source_artifacts": source_artifacts(),
        "verifier_results": verifier_results(),
    }
    graph["graph_hash"] = compute_graph_hash(graph)
    return graph


def check_source_artifact_ids(graph: Dict[str, Any]) -> None:
    artifact_ids = {artifact["artifact_id"] for artifact in graph["source_artifacts"]}
    verifier_ids = {result["verifier_id"] for result in graph["verifier_results"]}

    for result in graph["verifier_results"]:
        missing = set(result["source_artifact_ids"]) - artifact_ids
        if missing:
            raise GovernanceRecordGraphBuildError(f"VERIFIER_SOURCE_ARTIFACT_UNKNOWN: {sorted(missing)}")

    for node_item in graph["nodes"]:
        missing = set(node_item["source_artifact_ids"]) - artifact_ids
        if missing:
            raise GovernanceRecordGraphBuildError(f"NODE_SOURCE_ARTIFACT_UNKNOWN: {sorted(missing)}")

    for edge_item in graph["edges"]:
        derived = edge_item["derived_from"]
        missing_sources = set(derived["source_artifact_ids"]) - artifact_ids
        missing_verifiers = set(derived["verifier_result_ids"]) - verifier_ids
        if missing_sources:
            raise GovernanceRecordGraphBuildError(f"EDGE_SOURCE_ARTIFACT_UNKNOWN: {sorted(missing_sources)}")
        if missing_verifiers:
            raise GovernanceRecordGraphBuildError(f"EDGE_VERIFIER_RESULT_UNKNOWN: {sorted(missing_verifiers)}")


def validate_graph(graph: Dict[str, Any]) -> None:
    validate_schema(graph, load_schema())
    if graph["graph_hash"] != compute_graph_hash(graph):
        raise GovernanceRecordGraphBuildError("GRAPH_HASH_MISMATCH")
    check_source_artifact_ids(graph)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a v1.0 GCR governance record graph.")
    parser.add_argument("--output", required=True, help="Output graph JSON path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        graph = build_graph()
        validate_graph(graph)

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(graph, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        print("GOVERNANCE RECORD GRAPH BUILD PASS")
        print("SOURCE ARTIFACT CHECK PASS")
        print("EDGE DERIVATION CHECK PASS")
        print("GRAPH HASH VERIFY PASS")
        print("GRAPH PROJECTION ONLY")
        print("NO EXECUTION AUTHORITY CREATED")
        return 0
    except Exception as exc:
        print(f"GOVERNANCE RECORD GRAPH BUILD FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
