# Governed Consequence Routing

**The model proposes. The policy decides. The record proves.**

Governed Consequence Routing is a local reference implementation for generating and verifying governance records around AI-agent actions.

It demonstrates how consequential AI proposals can be captured before execution and represented as inspectable records that bind proposal capture, authority, evidence, decision, verification, receipt history, receipt-index membership, local interface exposure, governance graph projection, and proof boundary.

---

## Current Release

```text
Governed Consequence Routing v1.0 -- Governance Record Graph
```

Current release tag:

```text
v1.0-governance-record-graph
```

Expected local test result:

```text
241 passed
```

Current proof ladder:

```text
v0.3 -> v0.4 -> v0.5 -> v0.6 -> v0.7 -> v0.8 -> v0.9 -> v1.0
```

Current v1.0 proof sentence:

```text
v1.0 proves that GCR can assemble its verified local artifacts into an end-to-end governance record graph for an AI-agent consequence, linking proposal capture, authority, evidence, verification, receipt, index, and human inspection without creating new authority or execution.
```

Core v1.0 boundary:

```text
v1.0 proves local governance-record continuity.
The governance record graph is a projection, not the source of truth.
JSON artifacts remain the source of truth.
Existing verifiers remain the proof mechanism.
```

---

## Current Public Proof Status

Current proof layer:

```text
v1.0 -- Governance Record Graph
```

The governance record graph may represent verified local artifacts as graph nodes and verified relationships as graph edges.

It may not become the source of truth, replace existing verifiers, invent authority, invent evidence, invent verification results, execute tools, call external systems, or claim real-world correctness.

---

## Proof Ladder

```text
v0.3:
decision envelope <-> approval token <-> reviewer authority manifest

v0.4:
decision envelope <-> evidence manifest <-> evidence items

v0.5:
portable verification bundle
        ^
        |
decision envelope
        ^
        |
approval token <-> reviewer authority manifest
        ^
        |
evidence manifest <-> evidence items

v0.6:
verification receipt
        ^
        |
portable verification bundle
        ^
        |
decision envelope
        ^
        |
approval token <-> reviewer authority manifest
        ^
        |
evidence manifest <-> evidence items

v0.7:
verification receipt index
        ^
        |
verification receipt
        ^
        |
portable verification bundle
        ^
        |
decision envelope
        ^
        |
approval token <-> reviewer authority manifest
        ^
        |
evidence manifest <-> evidence items

v0.8:
local verifier UI
        ^
        |
existing verifier tools
        ^
        |
verification receipt index
        ^
        |
verification receipt
        ^
        |
portable verification bundle

v0.9:
runtime proposal hook
        |
        v
captured proposal
        |
        v
normalized consequence
        |
        v
governance record input
        |
        v
existing verifier tools
        ^
        |
verification receipt index
        ^
        |
local verifier UI

v1.0:
governance record graph
        ^
        |
local verifier UI
        ^
        |
verification receipt index
        ^
        |
verification receipt
        ^
        |
portable verification bundle
        ^
        |
decision envelope
        ^
        |
approval token <-> reviewer authority manifest
        ^
        |
evidence manifest <-> evidence items
        ^
        |
runtime proposal hook
```

---

## What This Repository Contains

This repository contains a local developer reference implementation for **Verifiable AI Governance Records**.

Core artifacts include:

* runtime proposal schema and fixture
* runtime proposal capture tool
* governance record graph schema and fixture
* governance record graph builder and verifier
* decision envelope examples
* reviewer authority manifest
* approval token example
* evidence manifest example
* portable verification bundle example
* verification receipt examples
* verification receipt index example
* local verifier UI
* CLI/UI semantic parity tests
* runtime proposal non-execution tests
* governance record graph projection tests
* JSON schemas
* local verification tools
* governance documentation
* release notes through v0.7
* v0.8, v0.9, and v1.0 release notes in GitHub Releases
* buyer/developer quick start
* test suite

The repository is intended to make the governance record chain inspectable, testable, and reproducible under local reference conditions.

---

## Core Pattern

```text
Capture proposal -> normalize consequence -> classify -> evidence-bind -> authorize -> record -> verify -> receipt -> index -> expose through local UI -> project governance record graph
```

The system does not treat model output as authority.

It captures proposed consequences before execution, then binds them to policy, evidence, reviewer authority, verification results, verification receipts, receipt-index membership, interface exposure, graph projection, and proof-boundary metadata.

---

## Key Entry Points

### Standards and Governance

* `docs/standard/GCR_BEHAVIORAL_STANDARD_v0.1.md`
* `docs/governance/current-proof-boundary.md`
* `docs/governance/governance-record-layer-v1.0.md`
* `docs/governance/runtime-proposal-hook-v0.9.md`
* `docs/governance/local-verifier-ui-v0.8.md`
* `docs/governance/verification-receipt-index-v0.7.md`
* `docs/governance/verification-receipt-v0.6.md`
* `docs/governance/portable-verification-bundle-v0.5.md`
* `docs/governance/evidence-manifest-binding-v0.4.md`

### Release Notes

* `RELEASE_NOTES_v0.3.md`
* `RELEASE_NOTES_v0.4.md`
* `RELEASE_NOTES_v0.5.md`
* `RELEASE_NOTES_v0.6.md`
* `RELEASE_NOTES_v0.7.md`

v0.8 release notes are published in the GitHub Release for tag `v0.8-local-verifier-ui`.

v0.9 release notes are published in the GitHub Release for tag `v0.9-runtime-proposal-hook`.

v1.0 release notes are published in the GitHub Release for tag `v1.0-governance-record-graph`.

### Schemas

* `schemas/decision_envelope_v0.1.schema.json`
* `schemas/approval_token_v0.3.schema.json`
* `schemas/reviewer_authority_manifest_v0.3.schema.json`
* `schemas/evidence_manifest_v0.4.schema.json`
* `schemas/verification_bundle_v0.5.schema.json`
* `schemas/verification_receipt_v0.6.schema.json`
* `schemas/verification_receipt_index_v0.7.schema.json`
* `schemas/runtime_proposal_v0.9.schema.json`
* `schemas/governance_record_graph_v1.0.schema.json`

### Examples

* `examples/reviewer_authority/approval_token.v0.3.json`
* `examples/reviewer_authority/manifest.v0.3.json`
* `examples/reviewer_authority/approved_decision_envelope.v0.3.json`
* `examples/evidence_manifest/manifest.v0.4.json`
* `examples/evidence_manifest/evidence_bound_decision_envelope.v0.4.json`
* `examples/verification_bundle/full_gcr_bundle.v0.5.json`
* `examples/verification_receipt/verification_receipt.v0.6.json`
* `examples/verification_receipt/verification_receipt.fail.v0.7.json`
* `examples/verification_receipt_index/index.v0.7.json`
* `examples/runtime_proposal/proposal.v0.9.json`
* `examples/governance_record_graph/graph.v1.0.json`

### Verification and Capture Tools

* `tools/capture_runtime_proposal.py`
* `tools/verify_approval_token.py`
* `tools/verify_reviewer_authority_binding.py`
* `tools/verify_decision_envelope_approval_binding.py`
* `tools/verify_evidence_manifest_binding.py`
* `tools/export_ledger_bundle.py`
* `tools/verify_ledger_bundle.py`
* `tools/verify_verification_receipt.py`
* `tools/verify_receipt_index.py`
* `tools/local_verifier_ui.py`
* `tools/build_governance_record_graph.py`
* `tools/verify_governance_record_graph.py`

### Tests

* `tests/test_runtime_proposal_hook.py`
* `tests/test_local_verifier_ui.py`
* `tests/test_governance_record_graph.py`

The v0.9 runtime proposal tests verify proposal capture, schema validation, proposed-action hash verification, normalized-consequence hash verification, record hash verification, non-execution, authorization boundary behavior, failure-closed behavior, and artifact non-mutation.

The v0.8 UI tests verify CLI/UI semantic parity, hard fail behavior, unknown verifier rejection, fixture non-mutation, no upload storage, no new governance artifacts, FAIL-not-promoted behavior, forbidden overclaim language checks, and primary output parity.

The v1.0 governance record graph tests verify graph schema validation, graph hash verification, source artifact hash verification, edge derivation, required node and edge coverage, graph mutation detection, source-of-truth boundaries, non-invention checks, and end-to-end traversal.

---

## Verify Locally

Create a virtual environment and install requirements:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run the full test suite:

```powershell
python -m pytest -q
```

Expected result:

```text
241 passed
```

Run the v1.0 governance record graph tests:

```powershell
python -m pytest tests/test_governance_record_graph.py -q
```

Expected result:

```text
50 passed
```

Run the v0.9 runtime proposal tests:

```powershell
python -m pytest tests/test_runtime_proposal_hook.py -q
```

Expected result:

```text
30 passed
```

Run the v0.8 local verifier UI tests:

```powershell
python -m pytest tests/test_local_verifier_ui.py -q
```

Expected result:

```text
34 passed
```

---

## Smoke Tests

### Runtime Proposal Capture

Use a generated proposal path so the stable fixture is not overwritten:

```powershell
python .\tools\capture_runtime_proposal.py --agent-id simulated-coding-agent --action-type write_file --target .github/workflows/deploy.yml --intent "modify deployment workflow" --output .\examples\runtime_proposal\proposal.generated.v0.9.json
```

Expected:

```text
PROPOSAL CAPTURED
CONSEQUENCE NORMALIZED
RUNTIME PROPOSAL RECORD CREATED
EXECUTION_STATUS: NOT_EXECUTED
AUTHORIZATION_STATUS: REQUIRES_GOVERNANCE
```

### Runtime Proposal Verification

```powershell
python .\tools\capture_runtime_proposal.py --verify-only .\examples\runtime_proposal\proposal.generated.v0.9.json
python .\tools\capture_runtime_proposal.py --verify-only .\examples\runtime_proposal\proposal.v0.9.json
```

Expected:

```text
RUNTIME PROPOSAL VERIFY PASS
RUNTIME PROPOSAL VERIFY PASS
```

Remove the generated proposal after smoke testing:

```powershell
Remove-Item .\examples\runtime_proposal\proposal.generated.v0.9.json
```

### Approval Token Verification

```powershell
python .\tools\verify_approval_token.py .\examples\reviewer_authority\approval_token.v0.3.json
```

Expected:

```text
APPROVAL TOKEN VERIFY PASS
```

### Reviewer Authority Binding Verification

```powershell
python .\tools\verify_reviewer_authority_binding.py --manifest .\examples\reviewer_authority\manifest.v0.3.json --token .\examples\reviewer_authority\approval_token.v0.3.json
```

Expected:

```text
REVIEWER AUTHORITY BINDING VERIFY PASS
```

### Decision Envelope Approval Binding Verification

```powershell
python .\tools\verify_decision_envelope_approval_binding.py --envelope .\examples\reviewer_authority\approved_decision_envelope.v0.3.json --token .\examples\reviewer_authority\approval_token.v0.3.json --manifest .\examples\reviewer_authority\manifest.v0.3.json
```

Expected:

```text
DECISION ENVELOPE APPROVAL BINDING VERIFY PASS
```

### Evidence Manifest Binding Verification

```powershell
python .\tools\verify_evidence_manifest_binding.py --envelope .\examples\evidence_manifest\evidence_bound_decision_envelope.v0.4.json --manifest .\examples\evidence_manifest\manifest.v0.4.json
```

Expected:

```text
EVIDENCE MANIFEST BINDING VERIFY PASS
```

### Portable Verification Bundle Verification

```powershell
python .\tools\verify_ledger_bundle.py .\examples\verification_bundle\full_gcr_bundle.v0.5.json
```

Expected:

```text
LEDGER BUNDLE VERIFY PASS
```

### Verification Receipt Verification

```powershell
python .\tools\verify_verification_receipt.py .\examples\verification_receipt\verification_receipt.v0.6.json
```

Expected:

```text
VERIFICATION RECEIPT VERIFY PASS
```

### Verification Receipt Index Verification

```powershell
python .\tools\verify_receipt_index.py .\examples\verification_receipt_index\index.v0.7.json
```

Expected:

```text
RECEIPT INDEX VERIFY PASS
```

### Verification Receipt Index Mutation Check

```powershell
python .\tools\verify_receipt_index.py .\examples\verification_receipt_index\index.v0.7.json --mutate
```

Expected:

```text
MUTATION CHECK PASS
```

### Governance Record Graph Build

Use a generated graph path so the stable fixture is not overwritten:

```powershell
python .\tools\build_governance_record_graph.py --output .\examples\governance_record_graph\graph.generated.v1.0.json
```

Expected:

```text
GOVERNANCE RECORD GRAPH BUILD PASS
SOURCE ARTIFACT CHECK PASS
EDGE DERIVATION CHECK PASS
GRAPH HASH VERIFY PASS
GRAPH PROJECTION ONLY
NO EXECUTION AUTHORITY CREATED
```

### Governance Record Graph Verification

```powershell
python .\tools\verify_governance_record_graph.py .\examples\governance_record_graph\graph.generated.v1.0.json
python .\tools\verify_governance_record_graph.py .\examples\governance_record_graph\graph.v1.0.json
```

Expected:

```text
GOVERNANCE RECORD GRAPH VERIFY PASS
GOVERNANCE RECORD GRAPH VERIFY PASS
```

### Governance Record Graph Mutation Check

```powershell
python .\tools\verify_governance_record_graph.py .\examples\governance_record_graph\graph.v1.0.json --mutate
```

Expected:

```text
GRAPH MUTATION CHECK PASS
```

Remove the generated graph after smoke testing:

```powershell
Remove-Item .\examples\governance_record_graph\graph.generated.v1.0.json
```

---

## Governance Record Graph

v1.0 adds a governance record graph projection:

```text
tools/build_governance_record_graph.py
tools/verify_governance_record_graph.py
```

The graph links verified local artifacts into an inspectable governance record graph for an AI-agent consequence.

It includes:

* runtime proposal node
* agent node
* consequence node
* decision envelope node
* approval token node
* reviewer authority manifest node
* evidence manifest and evidence item nodes
* verification bundle node
* verification receipt node
* receipt index node
* verifier result node
* local verifier UI node
* graph hash
* proof boundary

The graph is a projection, not the source of truth.

JSON artifacts remain the source of truth.

Existing verifiers remain the proof mechanism.

The graph does not require RAG, embeddings, vector search, Neo4j, RDF, SPARQL, graph databases, ontology engines, external calls, or agent execution.

---

## Runtime Proposal Hook

v0.9 adds a local simulated runtime proposal hook:

```text
tools/capture_runtime_proposal.py
```

The runtime proposal hook captures a proposed AI-agent action before execution and emits a governed proposal record.

It records:

* proposal identifier
* schema version
* creation timestamp
* agent identifier
* source metadata
* proposed action
* proposed action hash
* normalized consequence
* normalized consequence hash
* consequence classification
* consequence risk
* execution status
* authorization status
* proof boundary
* record hash

The stable v0.9 fixture records a simulated coding agent proposing a deployment workflow file write:

```text
execution_status: NOT_EXECUTED
authorization_status: REQUIRES_GOVERNANCE
consequence_classification: PRODUCTION_STATE_CHANGE
consequence_risk: HIGH
```

The hook proves proposal capture only.

It does not grant execution authority.

It does not execute tools.

It does not call external systems.

It does not create approvals, receipts, receipt indexes, bundles, evidence manifests, or authority manifests.

---

## Local Verifier UI

v0.8 adds a local verifier UI entrypoint:

```text
tools/local_verifier_ui.py
```

The local verifier UI exposes existing verifier results through a human-facing interface without changing verification semantics.

The UI exposes exactly seven approved verifier surfaces:

* approval token
* reviewer authority binding
* decision envelope approval binding
* evidence manifest binding
* ledger bundle
* verification receipt
* receipt index

The UI does not implement new verification logic. It calls the existing verifier scripts and preserves verifier outputs.

v0.8 is governed by the hard parity rule:

```text
If CLI verification and UI verification disagree, v0.8 fails.
```

The UI may display verifier results. It may not create new governance authority.

---

## Proof Boundary

This repository remains a local reference implementation and developer starter kit.

It does not claim:

* production custody
* external notarization
* legal admissibility
* regulatory compliance
* clinical safety
* financial advice suitability
* enterprise compliance
* SSO-backed identity
* production identity
* non-repudiation
* correctness of the underlying AI action
* real-world truth of the evidence
* legal validity of the approval
* safety of the original action
* that proposal capture grants execution authority
* that a captured proposal should execute
* that model output becomes authority
* that the graph becomes the source of truth
* that the graph replaces existing verifiers
* that the graph proves production custody
* that the graph proves legal or compliance status
* that the graph proves RAG correctness or retrieval quality
* that the graph requires graph database readiness
* that index membership proves receipt validity
* that receipt validity proves real-world correctness
* that the UI creates governance authority
* that the UI creates new verification semantics

The current implementation uses local schemas, local examples, local hash computation, local verification tools, a local verifier UI, a local simulated runtime proposal capture tool, a local governance record graph projection, and local test fixtures.

---

## Acceptable Public Claims

Acceptable:

> Governed Consequence Routing is a local reference implementation for generating and verifying governance records around AI-agent actions.

Acceptable:

> GCR creates and verifies portable governance records for AI-agent actions, binding proposal capture, authority, evidence, decision, receipt history, interface exposure, graph projection, and proof boundary into an inspectable record.

Acceptable:

> v1.0 assembles verified local GCR artifacts into a governance record graph projection without creating new authority or execution.

Acceptable:

> v0.9 captures a simulated AI-agent proposal before execution and converts it into a governed proposal record without granting execution authority.

Acceptable:

> v0.8 exposes existing GCR verifier results through a local human-facing interface without changing verifier semantics.

Not acceptable:

> Capturing a proposal authorizes the action.

Not acceptable:

> The UI creates new governance authority.

Not acceptable:

> The graph is the source of truth.

Not acceptable:

> The graph proves legal, compliance, production, RAG, retrieval, or graph database readiness.

Not acceptable:

> This system solves AI governance.

Not acceptable:

> This system is production-ready.

Not acceptable:

> This system is legally admissible by default.

Not acceptable:

> This system proves the underlying AI action was correct or safe.

Not acceptable:

> This system replaces AI GRC platforms.

---

## Category Direction

The emerging category is:

```text
Verifiable AI Governance Records
```

The core product-category sentence is:

```text
GCR creates and verifies portable governance records for AI-agent actions, binding proposal capture, authority, evidence, decision, receipt history, interface exposure, graph projection, and proof boundary into an inspectable record.
```

---

## Development Status

Current public release:

```text
Governed Consequence Routing v1.0 -- Governance Record Graph
```

Current expected local test result:

```text
241 passed
```

Current proof chain:

```text
governance record graph
        ^
        |
local verifier UI
        ^
        |
verification receipt index
        ^
        |
verification receipt
        ^
        |
portable verification bundle
        ^
        |
decision envelope
        ^
        |
evidence manifest <-> evidence items
        ^
        |
approval token <-> reviewer authority manifest
        ^
        |
runtime proposal hook
```
