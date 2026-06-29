#!/usr/bin/env python3
"""
verify_governance_record_graph.py

Verify a local v1.0 GCR governance record graph projection.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from collections import deque
from pathlib import Path
from typing import Any, Dict, Iterable

from jsonschema import Draft202012Validator, FormatChecker


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas/governance_record_graph_v1.0.schema.json"

REQUIRED_NODE_TYPES = {
    "RuntimeProposal",
    "Agent",
    "Consequence",
    "DecisionEnvelope",
    "ApprovalToken",
    "ReviewerAuthorityManifest",
    "EvidenceManifest",
    "EvidenceItem",
    "VerificationBundle",
    "VerificationReceipt",
    "ReceiptIndex",
    "VerifierResult",
    "LocalVerifierUI",
}

REQUIRED_EDGE_TYPES = {
    "PROPOSED_BY",
    "NORMALIZED_TO",
    "CLASSIFIED_AS",
    "HAS_EXECUTION_STATUS",
    "HAS_AUTHORIZATION_STATUS",
    "BOUND_TO",
    "AUTHORIZED_BY",
    "SUPPORTED_BY",
    "CONTAINS",
    "VERIFIED_BY",
    "RECEIPT_FOR",
    "INDEXED_IN",
    "DISPLAYED_BY",
    "DERIVED_FROM",
}

REQUIRED_NON_CLAIMS = {
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
    "execution authority",
}


class GovernanceRecordGraphVerificationError(Exception):
    """Raised when graph verification fails."""


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
        raise GovernanceRecordGraphVerificationError(f"INPUT_NOT_FOUND: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise GovernanceRecordGraphVerificationError(f"JSON_INVALID: {exc}") from exc
    if not isinstance(value, dict):
        raise GovernanceRecordGraphVerificationError("INPUT_MUST_BE_JSON_OBJECT")
    return value


def load_schema(path: Path = SCHEMA_PATH) -> Dict[str, Any]:
    schema = load_json(path)
    Draft202012Validator.check_schema(schema)
    return schema


def check_schema(graph: Dict[str, Any], schema: Dict[str, Any]) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(graph), key=lambda error: error.path)
    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.path) or "<root>"
        raise GovernanceRecordGraphVerificationError(
            f"GOVERNANCE_RECORD_GRAPH_SCHEMA_INVALID at {location}: {first.message}"
        )


def verify_graph_hash(graph: Dict[str, Any]) -> None:
    expected_hash = compute_graph_hash(graph)
    if graph.get("graph_hash") != expected_hash:
        raise GovernanceRecordGraphVerificationError(
            f"GRAPH_HASH_MISMATCH: expected {expected_hash}, got {graph.get('graph_hash')}"
        )


def reject_absolute_path(path_text: str) -> None:
    path = Path(path_text)
    if path.is_absolute() or ":" in path_text.replace("://", ""):
        raise GovernanceRecordGraphVerificationError(f"ABSOLUTE_OR_REMOTE_PATH_FORBIDDEN: {path_text}")


def artifact_indexes(graph: Dict[str, Any]) -> tuple[dict[str, Dict[str, Any]], set[str], set[str]]:
    artifact_by_id = {artifact["artifact_id"]: artifact for artifact in graph["source_artifacts"]}
    verifier_ids = {result["verifier_id"] for result in graph["verifier_results"]}
    node_ids = {node["node_id"] for node in graph["nodes"]}
    if len(artifact_by_id) != len(graph["source_artifacts"]):
        raise GovernanceRecordGraphVerificationError("DUPLICATE_SOURCE_ARTIFACT_ID")
    if len(verifier_ids) != len(graph["verifier_results"]):
        raise GovernanceRecordGraphVerificationError("DUPLICATE_VERIFIER_RESULT_ID")
    if len(node_ids) != len(graph["nodes"]):
        raise GovernanceRecordGraphVerificationError("DUPLICATE_NODE_ID")
    return artifact_by_id, verifier_ids, node_ids


def verify_source_artifacts(graph: Dict[str, Any]) -> None:
    for artifact in graph["source_artifacts"]:
        relative_path = artifact["path"]
        reject_absolute_path(relative_path)
        path = REPO_ROOT / relative_path
        if not path.exists():
            raise GovernanceRecordGraphVerificationError(
                f"SOURCE_ARTIFACT_NOT_FOUND: {relative_path}"
            )
        actual_hash = sha256_bytes(path.read_bytes())
        if actual_hash != artifact["sha256"]:
            raise GovernanceRecordGraphVerificationError(
                f"SOURCE_ARTIFACT_HASH_MISMATCH: {relative_path}"
            )


def require_known_artifacts(ids: Iterable[str], artifact_ids: set[str], context: str) -> None:
    missing = set(ids) - artifact_ids
    if missing:
        raise GovernanceRecordGraphVerificationError(
            f"{context}_UNKNOWN_SOURCE_ARTIFACT: {sorted(missing)}"
        )


def require_known_verifiers(ids: Iterable[str], verifier_ids: set[str], context: str) -> None:
    missing = set(ids) - verifier_ids
    if missing:
        raise GovernanceRecordGraphVerificationError(
            f"{context}_UNKNOWN_VERIFIER_RESULT: {sorted(missing)}"
        )


def verify_mappings(graph: Dict[str, Any]) -> None:
    artifact_by_id, verifier_ids, node_ids = artifact_indexes(graph)
    artifact_ids = set(artifact_by_id)

    for result in graph["verifier_results"]:
        require_known_artifacts(result["source_artifact_ids"], artifact_ids, "VERIFIER_RESULT")

    for node in graph["nodes"]:
        require_known_artifacts(node["source_artifact_ids"], artifact_ids, "NODE")

    for edge in graph["edges"]:
        if edge["from_node"] not in node_ids or edge["to_node"] not in node_ids:
            raise GovernanceRecordGraphVerificationError(f"EDGE_UNKNOWN_NODE: {edge['edge_id']}")
        derived = edge["derived_from"]
        if not derived["source_artifact_ids"] and not derived["verifier_result_ids"]:
            raise GovernanceRecordGraphVerificationError(
                f"EDGE_WITHOUT_SOURCE_EVIDENCE: {edge['edge_id']}"
            )
        require_known_artifacts(derived["source_artifact_ids"], artifact_ids, "EDGE")
        require_known_verifiers(derived["verifier_result_ids"], verifier_ids, "EDGE")


def verify_required_types(graph: Dict[str, Any]) -> None:
    node_types = {node["node_type"] for node in graph["nodes"]}
    edge_types = {edge["edge_type"] for edge in graph["edges"]}
    missing_node_types = REQUIRED_NODE_TYPES - node_types
    missing_edge_types = REQUIRED_EDGE_TYPES - edge_types
    if missing_node_types:
        raise GovernanceRecordGraphVerificationError(
            f"REQUIRED_NODE_TYPE_MISSING: {sorted(missing_node_types)}"
        )
    if missing_edge_types:
        raise GovernanceRecordGraphVerificationError(
            f"REQUIRED_EDGE_TYPE_MISSING: {sorted(missing_edge_types)}"
        )


def verify_runtime_boundary(graph: Dict[str, Any]) -> None:
    runtime_artifacts = [
        artifact for artifact in graph["source_artifacts"]
        if artifact["artifact_type"] == "RUNTIME_PROPOSAL"
    ]
    if not runtime_artifacts:
        raise GovernanceRecordGraphVerificationError("RUNTIME_PROPOSAL_SOURCE_MISSING")

    runtime_record = load_json(REPO_ROOT / runtime_artifacts[0]["path"])
    if runtime_record.get("execution_status") != "NOT_EXECUTED":
        raise GovernanceRecordGraphVerificationError("RUNTIME_PROPOSAL_EXECUTION_STATUS_INVALID")
    if runtime_record.get("authorization_status") not in {"NOT_AUTHORIZED", "REQUIRES_GOVERNANCE"}:
        raise GovernanceRecordGraphVerificationError("RUNTIME_PROPOSAL_AUTHORIZATION_STATUS_INVALID")


def verify_projection_boundary(graph: Dict[str, Any]) -> None:
    proves = set(graph["proof_boundary"]["proves"])
    does_not_prove = set(graph["proof_boundary"]["does_not_prove"])
    if "v1.0 proves local governance-record continuity." not in proves:
        raise GovernanceRecordGraphVerificationError("PROOF_BOUNDARY_PROVES_MISSING")
    missing_non_claims = REQUIRED_NON_CLAIMS - does_not_prove
    if missing_non_claims:
        raise GovernanceRecordGraphVerificationError(
            f"PROOF_BOUNDARY_NON_CLAIMS_MISSING: {sorted(missing_non_claims)}"
        )


def verify_traversal(graph: Dict[str, Any]) -> None:
    start_nodes = {
        node["node_id"] for node in graph["nodes"]
        if node["node_type"] == "RuntimeProposal"
    }
    target_nodes = {
        node["node_id"] for node in graph["nodes"]
        if node["node_type"] == "LocalVerifierUI"
    }
    adjacency: dict[str, set[str]] = {}
    for edge in graph["edges"]:
        adjacency.setdefault(edge["from_node"], set()).add(edge["to_node"])
        adjacency.setdefault(edge["to_node"], set()).add(edge["from_node"])

    queue = deque(start_nodes)
    visited = set(start_nodes)
    while queue:
        current = queue.popleft()
        if current in target_nodes:
            return
        for next_node in adjacency.get(current, set()):
            if next_node not in visited:
                visited.add(next_node)
                queue.append(next_node)

    raise GovernanceRecordGraphVerificationError("GRAPH_TRAVERSAL_MISSING_RUNTIME_TO_UI")


def verify_graph(graph: Dict[str, Any], schema: Dict[str, Any]) -> None:
    check_schema(graph, schema)
    verify_graph_hash(graph)
    verify_source_artifacts(graph)
    verify_mappings(graph)
    verify_required_types(graph)
    verify_runtime_boundary(graph)
    verify_projection_boundary(graph)
    verify_traversal(graph)


def assert_mutation_detected(graph: Dict[str, Any], mutation_name: str, mutate) -> None:
    mutated = copy.deepcopy(graph)
    mutate(mutated)
    try:
        verify_graph_hash(mutated)
    except GovernanceRecordGraphVerificationError:
        return
    raise GovernanceRecordGraphVerificationError(f"MUTATION_NOT_DETECTED: {mutation_name}")


def run_mutation_checks(graph: Dict[str, Any], schema: Dict[str, Any]) -> None:
    verify_graph(graph, schema)
    assert_mutation_detected(
        graph,
        "node_label",
        lambda mutated: mutated["nodes"][0].update({"label": "mutated label"}),
    )
    assert_mutation_detected(
        graph,
        "edge_type",
        lambda mutated: mutated["edges"][0].update({"edge_type": "DERIVED_FROM"}),
    )
    assert_mutation_detected(
        graph,
        "proof_boundary",
        lambda mutated: mutated["proof_boundary"]["does_not_prove"].append("mutated"),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify a v1.0 GCR governance record graph.")
    parser.add_argument("input", help="Governance record graph JSON file.")
    parser.add_argument(
        "--schema",
        default=str(SCHEMA_PATH),
        help="Path to governance record graph schema.",
    )
    parser.add_argument(
        "--mutate",
        action="store_true",
        help="Run graph mutation checks against a valid graph.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        schema = load_schema(Path(args.schema))
        graph = load_json(Path(args.input))

        if args.mutate:
            run_mutation_checks(graph, schema)
            print("GRAPH MUTATION CHECK PASS")
            return 0

        verify_graph(graph, schema)
        print("GOVERNANCE RECORD GRAPH VERIFY PASS")
        print("GRAPH HASH VERIFY PASS")
        print("SOURCE ARTIFACT CHECK PASS")
        print("EDGE DERIVATION CHECK PASS")
        print("GRAPH PROJECTION ONLY")
        print("NO EXECUTION AUTHORITY CREATED")
        return 0
    except Exception as exc:
        if args.mutate:
            print(f"GRAPH MUTATION CHECK FAIL: {exc}", file=sys.stderr)
        else:
            print(f"GOVERNANCE RECORD GRAPH VERIFY FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
