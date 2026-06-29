import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from tools import build_governance_record_graph, verify_governance_record_graph


SCHEMA = Path("schemas/governance_record_graph_v1.0.schema.json")
FIXTURE = Path("examples/governance_record_graph/graph.v1.0.json")
BUILD_TOOL = Path("tools/build_governance_record_graph.py")
VERIFY_TOOL = Path("tools/verify_governance_record_graph.py")
CONTRACT = Path("docs/governance/governance-record-layer-v1.0.md")

REQUIRED_NODE_TYPES = verify_governance_record_graph.REQUIRED_NODE_TYPES
REQUIRED_EDGE_TYPES = verify_governance_record_graph.REQUIRED_EDGE_TYPES

FORBIDDEN_OUTPUT_LINES = {
    "PRODUCTION READY",
    "COMPLIANT",
    "CERTIFIED",
    "LEGALLY VALID",
    "LEGAL AUDIT PASS",
    "SAFE TO EXECUTE",
    "CORRECT ACTION",
    "REAL WORLD TRUTH VERIFIED",
    "AUTHORITY CREATED",
    "APPROVAL CREATED",
    "EXECUTION AUTHORIZED",
}

ARTIFACT_PATTERNS = {
    "approval_tokens": "examples/**/approval_token*.json",
    "verification_receipts": "examples/**/verification_receipt*.json",
    "receipt_indexes": "examples/**/index*.json",
    "bundles": "examples/**/full_gcr_bundle*.json",
    "evidence_manifests": "examples/evidence_manifest/*.json",
    "authority_manifests": "examples/reviewer_authority/manifest*.json",
}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_python(*args):
    return subprocess.run(
        [sys.executable, *map(str, args)],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def validate_graph(graph):
    schema = load_json(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(graph), key=lambda error: error.path)
    assert errors == []


def recompute_graph_hash(graph):
    graph["graph_hash"] = build_governance_record_graph.compute_graph_hash(graph)


def verify_graph_data(graph):
    verify_governance_record_graph.verify_graph(
        graph,
        verify_governance_record_graph.load_schema(),
    )


def mutated_graph(tmp_path, mutate, recompute=True):
    graph = copy.deepcopy(load_json(FIXTURE))
    mutate(graph)
    if recompute:
        recompute_graph_hash(graph)
    path = tmp_path / "graph.mutated.json"
    write_json(path, graph)
    return path, graph


def artifact_snapshot():
    return {
        name: {path.as_posix() for path in Path(".").glob(pattern)}
        for name, pattern in ARTIFACT_PATTERNS.items()
    }


def file_hashes(paths):
    return {path.as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def source_paths(graph=None):
    graph = graph or load_json(FIXTURE)
    return [Path(artifact["path"]) for artifact in graph["source_artifacts"]]


def test_01_graph_schema_is_valid_json():
    schema = load_json(SCHEMA)
    Draft202012Validator.check_schema(schema)


def test_02_stable_graph_fixture_validates_against_schema():
    validate_graph(load_json(FIXTURE))


def test_03_graph_hash_verifies():
    graph = load_json(FIXTURE)
    assert graph["graph_hash"] == build_governance_record_graph.compute_graph_hash(graph)


def test_04_generated_graph_verifies(tmp_path):
    out = tmp_path / "graph.generated.v1.0.json"
    result = run_python(BUILD_TOOL, "--output", out)
    assert result.returncode == 0, result.stderr
    verify_graph_data(load_json(out))


def test_05_verify_tool_passes_on_stable_fixture():
    result = run_python(VERIFY_TOOL, FIXTURE)
    assert result.returncode == 0, result.stderr
    assert "GOVERNANCE RECORD GRAPH VERIFY PASS" in result.stdout


def test_06_build_tool_creates_generated_graph(tmp_path):
    out = tmp_path / "graph.generated.v1.0.json"
    result = run_python(BUILD_TOOL, "--output", out)
    assert result.returncode == 0, result.stderr
    assert out.exists()
    assert "GOVERNANCE RECORD GRAPH BUILD PASS" in result.stdout


def test_07_source_artifact_paths_exist():
    for path in source_paths():
        assert path.exists()


def test_08_source_artifact_hashes_verify():
    graph = load_json(FIXTURE)
    for artifact in graph["source_artifacts"]:
        assert build_governance_record_graph.artifact_hash(artifact["path"]) == artifact["sha256"]


def test_09_every_node_references_existing_source_artifact():
    graph = load_json(FIXTURE)
    artifact_ids = {artifact["artifact_id"] for artifact in graph["source_artifacts"]}
    for node in graph["nodes"]:
        assert set(node["source_artifact_ids"]) <= artifact_ids


def test_10_every_edge_references_existing_nodes():
    graph = load_json(FIXTURE)
    node_ids = {node["node_id"] for node in graph["nodes"]}
    for edge in graph["edges"]:
        assert edge["from_node"] in node_ids
        assert edge["to_node"] in node_ids


def test_11_every_edge_has_derivation_metadata():
    graph = load_json(FIXTURE)
    for edge in graph["edges"]:
        assert "derived_from" in edge
        assert set(edge["derived_from"]) == {"source_artifact_ids", "verifier_result_ids"}


def test_12_every_edge_derivation_references_existing_sources_or_verifiers():
    graph = load_json(FIXTURE)
    artifact_ids = {artifact["artifact_id"] for artifact in graph["source_artifacts"]}
    verifier_ids = {result["verifier_id"] for result in graph["verifier_results"]}
    for edge in graph["edges"]:
        derived = edge["derived_from"]
        assert set(derived["source_artifact_ids"]) <= artifact_ids
        assert set(derived["verifier_result_ids"]) <= verifier_ids


def test_13_required_node_types_are_present():
    graph = load_json(FIXTURE)
    assert REQUIRED_NODE_TYPES <= {node["node_type"] for node in graph["nodes"]}


def test_14_required_edge_types_are_present():
    graph = load_json(FIXTURE)
    assert REQUIRED_EDGE_TYPES <= {edge["edge_type"] for edge in graph["edges"]}


def test_15_unknown_node_type_is_rejected(tmp_path):
    path, _ = mutated_graph(tmp_path, lambda graph: graph["nodes"][0].update({"node_type": "UnknownNode"}))
    result = run_python(VERIFY_TOOL, path)
    assert result.returncode != 0


def test_16_unknown_edge_type_is_rejected(tmp_path):
    path, _ = mutated_graph(tmp_path, lambda graph: graph["edges"][0].update({"edge_type": "UNKNOWN_EDGE"}))
    result = run_python(VERIFY_TOOL, path)
    assert result.returncode != 0


def test_17_unknown_top_level_field_is_rejected(tmp_path):
    path, _ = mutated_graph(tmp_path, lambda graph: graph.update({"unknown": True}), recompute=False)
    result = run_python(VERIFY_TOOL, path)
    assert result.returncode != 0


def test_18_missing_source_artifact_fails_closed(tmp_path):
    def mutate(graph):
        graph["source_artifacts"][0]["path"] = "examples/missing/source.json"
        graph["source_artifacts"][0]["sha256"] = "sha256:" + ("0" * 64)

    path, _ = mutated_graph(tmp_path, mutate)
    result = run_python(VERIFY_TOOL, path)
    assert result.returncode != 0


def test_19_source_artifact_hash_mismatch_fails_closed(tmp_path):
    def mutate(graph):
        graph["source_artifacts"][0]["sha256"] = "sha256:" + ("1" * 64)

    path, _ = mutated_graph(tmp_path, mutate)
    result = run_python(VERIFY_TOOL, path)
    assert result.returncode != 0


def test_20_missing_required_node_fails_closed(tmp_path):
    path, _ = mutated_graph(
        tmp_path,
        lambda graph: graph.update({"nodes": [node for node in graph["nodes"] if node["node_type"] != "RuntimeProposal"]}),
    )
    result = run_python(VERIFY_TOOL, path)
    assert result.returncode != 0


def test_21_missing_required_edge_fails_closed(tmp_path):
    path, _ = mutated_graph(
        tmp_path,
        lambda graph: graph.update({"edges": [edge for edge in graph["edges"] if edge["edge_type"] != "PROPOSED_BY"]}),
    )
    result = run_python(VERIFY_TOOL, path)
    assert result.returncode != 0


def test_22_graph_mutation_changes_graph_hash_and_is_detected(tmp_path):
    graph = load_json(FIXTURE)
    mutated = copy.deepcopy(graph)
    mutated["proof_boundary"]["proves"].append("mutation")
    assert mutated["graph_hash"] != build_governance_record_graph.compute_graph_hash(mutated)
    path = tmp_path / "graph.mutated.json"
    write_json(path, mutated)
    result = run_python(VERIFY_TOOL, path)
    assert result.returncode != 0


def test_23_node_mutation_is_detected(tmp_path):
    path, _ = mutated_graph(
        tmp_path,
        lambda graph: graph["nodes"][0].update({"label": "mutated"}),
        recompute=False,
    )
    assert run_python(VERIFY_TOOL, path).returncode != 0


def test_24_edge_mutation_is_detected(tmp_path):
    path, _ = mutated_graph(
        tmp_path,
        lambda graph: graph["edges"][0].update({"to_node": "local-verifier-ui-001"}),
        recompute=False,
    )
    assert run_python(VERIFY_TOOL, path).returncode != 0


def test_25_graph_traversal_works_from_runtime_proposal_to_local_verifier_ui():
    verify_governance_record_graph.verify_traversal(load_json(FIXTURE))


def test_26_runtime_proposal_execution_status_remains_not_executed():
    runtime = load_json(Path("examples/runtime_proposal/proposal.v0.9.json"))
    assert runtime["execution_status"] == "NOT_EXECUTED"


def test_27_runtime_proposal_authorization_status_is_bounded():
    runtime = load_json(Path("examples/runtime_proposal/proposal.v0.9.json"))
    assert runtime["authorization_status"] in {"NOT_AUTHORIZED", "REQUIRES_GOVERNANCE"}


def test_28_graph_does_not_invent_authority():
    graph = load_json(FIXTURE)
    authority_nodes = [node for node in graph["nodes"] if node["node_type"] == "ReviewerAuthorityManifest"]
    assert authority_nodes
    assert all(node["source_artifact_ids"] == ["reviewer-authority-manifest-v0.3"] for node in authority_nodes)


def test_29_graph_does_not_invent_approval():
    graph = load_json(FIXTURE)
    approval_nodes = [node for node in graph["nodes"] if node["node_type"] == "ApprovalToken"]
    assert approval_nodes
    assert all(node["source_artifact_ids"] == ["approval-token-v0.3"] for node in approval_nodes)


def test_30_graph_does_not_invent_evidence():
    graph = load_json(FIXTURE)
    evidence_nodes = [node for node in graph["nodes"] if node["node_type"] in {"EvidenceManifest", "EvidenceItem"}]
    assert evidence_nodes
    assert all("evidence-manifest-v0.4" in node["source_artifact_ids"] for node in evidence_nodes)


def test_31_graph_does_not_invent_execution():
    graph = load_json(FIXTURE)
    text = json.dumps(graph)
    assert "EXECUTION_AUTHORIZED" not in text
    assert "NOT_EXECUTED" in text


def test_32_graph_does_not_invent_verification_results():
    graph = load_json(FIXTURE)
    artifact_ids = {artifact["artifact_id"] for artifact in graph["source_artifacts"]}
    for result in graph["verifier_results"]:
        assert set(result["source_artifact_ids"]) <= artifact_ids
        assert result["status"] == "PASS"


def test_33_graph_does_not_invent_receipt_membership():
    graph = load_json(FIXTURE)
    index_edges = [edge for edge in graph["edges"] if edge["edge_type"] == "INDEXED_IN"]
    assert index_edges
    assert all("receipt-index-v0.7" in edge["derived_from"]["source_artifact_ids"] for edge in index_edges)


def test_34_graph_builder_does_not_mutate_source_artifacts(tmp_path):
    paths = source_paths()
    before = file_hashes(paths)
    result = run_python(BUILD_TOOL, "--output", tmp_path / "graph.generated.v1.0.json")
    assert result.returncode == 0, result.stderr
    assert file_hashes(paths) == before


def test_35_graph_verifier_does_not_mutate_source_artifacts():
    paths = source_paths()
    before = file_hashes(paths)
    result = run_python(VERIFY_TOOL, FIXTURE)
    assert result.returncode == 0, result.stderr
    assert file_hashes(paths) == before


def test_36_graph_builder_creates_no_new_approvals(tmp_path):
    before = artifact_snapshot()
    assert run_python(BUILD_TOOL, "--output", tmp_path / "graph.json").returncode == 0
    assert artifact_snapshot()["approval_tokens"] == before["approval_tokens"]


def test_37_graph_builder_creates_no_new_receipts(tmp_path):
    before = artifact_snapshot()
    assert run_python(BUILD_TOOL, "--output", tmp_path / "graph.json").returncode == 0
    assert artifact_snapshot()["verification_receipts"] == before["verification_receipts"]


def test_38_graph_builder_creates_no_new_receipt_indexes(tmp_path):
    before = artifact_snapshot()
    assert run_python(BUILD_TOOL, "--output", tmp_path / "graph.json").returncode == 0
    assert artifact_snapshot()["receipt_indexes"] == before["receipt_indexes"]


def test_39_graph_builder_creates_no_new_bundles(tmp_path):
    before = artifact_snapshot()
    assert run_python(BUILD_TOOL, "--output", tmp_path / "graph.json").returncode == 0
    assert artifact_snapshot()["bundles"] == before["bundles"]


def test_40_graph_builder_creates_no_new_evidence_manifests(tmp_path):
    before = artifact_snapshot()
    assert run_python(BUILD_TOOL, "--output", tmp_path / "graph.json").returncode == 0
    assert artifact_snapshot()["evidence_manifests"] == before["evidence_manifests"]


def test_41_graph_builder_creates_no_new_authority_manifests(tmp_path):
    before = artifact_snapshot()
    assert run_python(BUILD_TOOL, "--output", tmp_path / "graph.json").returncode == 0
    assert artifact_snapshot()["authority_manifests"] == before["authority_manifests"]


def test_42_graph_builder_does_not_call_external_systems():
    source = BUILD_TOOL.read_text(encoding="utf-8")
    assert "requests" not in source
    assert "urllib" not in source
    assert "socket" not in source


def test_43_graph_verifier_does_not_call_external_systems():
    source = VERIFY_TOOL.read_text(encoding="utf-8")
    assert "requests" not in source
    assert "urllib" not in source
    assert "socket" not in source


def test_44_graph_output_contains_allowed_strings(tmp_path):
    build_result = run_python(BUILD_TOOL, "--output", tmp_path / "graph.json")
    verify_result = run_python(VERIFY_TOOL, FIXTURE)
    output = build_result.stdout + verify_result.stdout
    for expected in [
        "GOVERNANCE RECORD GRAPH BUILD PASS",
        "GOVERNANCE RECORD GRAPH VERIFY PASS",
        "GRAPH HASH VERIFY PASS",
        "SOURCE ARTIFACT CHECK PASS",
        "EDGE DERIVATION CHECK PASS",
        "GRAPH PROJECTION ONLY",
        "NO EXECUTION AUTHORITY CREATED",
    ]:
        assert expected in output


def test_45_graph_output_does_not_contain_forbidden_overclaim_lines(tmp_path):
    result = run_python(BUILD_TOOL, "--output", tmp_path / "graph.json")
    lines = {line.strip() for line in result.stdout.splitlines()}
    assert FORBIDDEN_OUTPUT_LINES.isdisjoint(lines)


def test_46_contract_states_graph_is_projection_not_source_of_truth():
    text = CONTRACT.read_text(encoding="utf-8").lower()
    assert "the graph is a projection, not the source of truth." in text


def test_47_contract_states_existing_verifiers_remain_proof_mechanism():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "Existing verifiers remain the proof mechanism." in text


def test_48_graph_proof_boundary_states_local_governance_record_continuity():
    graph = load_json(FIXTURE)
    assert "v1.0 proves local governance-record continuity." in graph["proof_boundary"]["proves"]


def test_49_graph_proof_boundary_states_non_claims():
    graph = load_json(FIXTURE)
    non_claims = set(graph["proof_boundary"]["does_not_prove"])
    assert verify_governance_record_graph.REQUIRED_NON_CLAIMS <= non_claims


def test_50_mutate_returns_graph_mutation_check_pass():
    result = run_python(VERIFY_TOOL, FIXTURE, "--mutate")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "GRAPH MUTATION CHECK PASS"
