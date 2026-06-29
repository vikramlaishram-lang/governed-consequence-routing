# Governed Consequence Routing v1.0 — Governance Record Layer Acceptance Gate

## Proof Sentence

v1.0 proves that GCR can assemble its verified local artifacts into an end-to-end governance record graph for an AI-agent consequence, linking proposal capture, authority, evidence, verification, receipt, index, and human inspection without creating new authority or execution.

## Core Boundary

v1.0 proves local governance-record continuity.

v1.0 does not prove:

* production custody
* external identity
* legal admissibility
* regulatory compliance
* real-world evidence truth
* execution safety
* hosted product readiness
* RAG correctness
* retrieval quality
* graph database production readiness
* ontology completeness

## Central Invariant

The governance record graph may:

* represent verified local GCR artifacts as graph nodes
* represent verified relationships as graph edges
* link runtime proposal, consequence, authority, evidence, bundle, receipt, index, and UI inspection records
* compute graph hash over canonical graph serialization
* verify that each node maps back to an existing source artifact
* verify that each edge is derived from source artifact content or verifier output
* expose the full local governance chain as an inspectable graph

The governance record graph may not:

* become the source of truth
* replace existing verifiers
* invent new authority
* invent evidence
* invent reviewer approval
* invent execution
* invent verification results
* invent receipt membership
* assert real-world correctness
* assert legal/compliance status
* mutate source artifacts
* execute tools
* call external systems
* require a graph database
* require RAG, embeddings, vector search, or retrieval infrastructure

## v1.0 Proof Chain

The target proof chain is:

```text
runtime proposal hook
↓
governed proposal record
↓
authority binding
↓
evidence binding
↓
portable verification bundle
↓
verification receipt
↓
receipt index
↓
local verifier UI
↓
governance record graph projection
```

The graph projection must point back to the source artifacts and verifier results.

## Governance Record Graph Model

The future implementation may represent the graph using:

* nodes
* edges
* source_artifacts
* verifier_results
* graph_hash
* proof_boundary

Conceptual node types:

* RuntimeProposal
* Agent
* Consequence
* DecisionEnvelope
* ApprovalToken
* ReviewerAuthorityManifest
* EvidenceManifest
* EvidenceItem
* VerificationBundle
* VerificationReceipt
* ReceiptIndex
* VerifierResult
* LocalVerifierUI

Conceptual edge types:

* PROPOSED_BY
* NORMALIZED_TO
* CLASSIFIED_AS
* HAS_EXECUTION_STATUS
* HAS_AUTHORIZATION_STATUS
* BOUND_TO
* AUTHORIZED_BY
* SUPPORTED_BY
* CONTAINS
* VERIFIED_BY
* RECEIPT_FOR
* INDEXED_IN
* DISPLAYED_BY
* DERIVED_FROM

Example triples:

```text
runtime-proposal-001 PROPOSED_BY simulated-coding-agent
runtime-proposal-001 NORMALIZED_TO consequence-001
consequence-001 CLASSIFIED_AS PRODUCTION_STATE_CHANGE
runtime-proposal-001 HAS_EXECUTION_STATUS NOT_EXECUTED
runtime-proposal-001 HAS_AUTHORIZATION_STATUS REQUIRES_GOVERNANCE
decision-envelope-001 BOUND_TO approval-token-001
approval-token-001 AUTHORIZED_BY reviewer-authority-001
decision-envelope-001 SUPPORTED_BY evidence-manifest-001
bundle-001 CONTAINS decision-envelope-001
receipt-001 VERIFIES bundle-001
index-001 CONTAINS receipt-001
ui-result-001 DISPLAYS verifier-result-001
```

## Proposed v1.0 Artifact Boundary

The future implementation may add only these artifact types unless the acceptance gate is amended first:

```text
schemas/governance_record_graph_v1.0.schema.json
examples/governance_record_graph/graph.v1.0.json
tools/build_governance_record_graph.py
tools/verify_governance_record_graph.py
tests/test_governance_record_graph.py
docs/governance/governance-record-layer-v1.0.md
RELEASE_NOTES_v1.0.md
```

No implementation should be added in this acceptance-gate commit.

## Non-RAG Boundary

v1.0 is not a RAG milestone.

v1.0 must not add:

* ingestion pipeline
* parsing pipeline
* cleaning pipeline
* chunking
* embeddings
* vector database
* metadata filtering engine
* hybrid search
* query transformation
* reranking
* context construction
* LLM generation
* RAG observability
* RAG evaluation
* retrieval quality scoring

RAG and evidence-quality pipelines may become future evidence-adapter or product milestones.

For v1.0, evidence remains represented by existing local evidence manifests and evidence items.

## Non-Knowledge-Graph-Database Boundary

v1.0 may use graph concepts.

v1.0 must not require:

* Neo4j
* RDF store
* SPARQL endpoint
* graph database
* ontology engine
* external knowledge graph service

The v1.0 graph must be a local JSON graph projection derived from verified GCR artifacts.

## Acceptance Gate

v1.0 passes only when all of the following are true.

### GRAPH CONSTRUCTION CHECKS

[ ] A governance record graph can be built from existing local GCR artifacts.
[ ] The graph includes nodes for runtime proposal, consequence, authority, evidence, bundle, receipt, index, verifier result, and UI inspection where applicable.
[ ] The graph includes edges linking proposal capture, authority binding, evidence binding, bundle verification, receipt generation, receipt indexing, and UI inspection.
[ ] Every graph node references a source artifact or approved verifier/UI result.
[ ] Every graph edge is derived from source artifact content or verifier output.
[ ] The graph validates against the v1.0 graph schema.
[ ] The graph hash verifies using canonical serialization excluding graph_hash itself.

### SOURCE-OF-TRUTH CHECKS

[ ] JSON artifacts remain the source of truth.
[ ] Existing verifiers remain the proof mechanism.
[ ] The graph is only a projection.
[ ] The graph does not replace source artifacts.
[ ] The graph does not replace verifier results.

### NON-INVENTION CHECKS

[ ] The graph does not invent authority.
[ ] The graph does not invent approval.
[ ] The graph does not invent evidence.
[ ] The graph does not invent execution.
[ ] The graph does not invent verification results.
[ ] The graph does not invent receipt membership.
[ ] The graph does not invent UI inspection.
[ ] The graph does not infer real-world truth.
[ ] The graph does not claim correctness or safety.

### CONTINUITY CHECKS

[ ] Runtime proposal node links to agent and normalized consequence.
[ ] Runtime proposal execution_status remains NOT_EXECUTED.
[ ] Runtime proposal authorization_status remains NOT_AUTHORIZED or REQUIRES_GOVERNANCE.
[ ] Authority node links to approval token and reviewer authority manifest.
[ ] Evidence node links to evidence manifest and admitted evidence items.
[ ] Verification bundle node links to included governance artifacts.
[ ] Verification receipt node links to verified bundle.
[ ] Receipt index node links to indexed receipts.
[ ] UI inspection node links to verifier result or approved local UI output.
[ ] The end-to-end chain can be traversed from runtime proposal to UI inspection.

### FAILURE CHECKS

[ ] Missing source artifact fails closed.
[ ] Missing required node fails closed.
[ ] Missing required edge fails closed.
[ ] Hash mismatch fails closed.
[ ] Unknown node type fails closed.
[ ] Unknown edge type fails closed.
[ ] Edge without source evidence fails closed.
[ ] Graph mutation is detected.
[ ] Source artifact mutation is detected by existing verifier path.
[ ] Any attempted execution path fails the test suite.

### BOUNDARY LANGUAGE CHECKS

[ ] Documentation states that v1.0 proves local governance-record continuity.
[ ] Documentation states that the graph is a projection, not the source of truth.
[ ] Documentation states that existing verifiers remain the proof mechanism.
[ ] Documentation states that v1.0 does not prove production custody, external identity, legal admissibility, regulatory compliance, real-world evidence truth, execution safety, hosted product readiness, RAG correctness, or graph database readiness.
[ ] Documentation does not claim legal/compliance status, production readiness, safety, or correctness.

### FULL TEST SUITE

[ ] python -m pytest -q reports 191 + new v1.0 tests passing after implementation.

If any check fails, v1.0 is not sealed.

## Required Tests for Future v1.0 Implementation

Document the required future tests, but do not implement them in this contract commit.

### Test Class 1 — Graph Schema and Fixture

Must prove:

* graph fixture validates against schema
* graph_hash verifies
* graph contains required node types
* graph contains required edge types
* graph rejects unknown fields
* graph rejects unknown node types
* graph rejects unknown edge types

### Test Class 2 — Source Artifact Mapping

Must prove:

* every graph node maps to a source artifact or approved verifier/UI result
* every source artifact path exists
* every source artifact hash matches
* missing source artifact fails closed
* source artifact mutation is detected

### Test Class 3 — Edge Derivation

Must prove:

* every graph edge is derived from source artifact content or verifier output
* edge without source evidence fails closed
* missing required edge fails closed
* graph cannot invent authority, approval, evidence, execution, receipt, index, or UI inspection

### Test Class 4 — End-to-End Chain Traversal

Must prove graph traversal from:

```text
runtime proposal
→ consequence
→ decision envelope
→ approval token
→ reviewer authority manifest
→ evidence manifest
→ verification bundle
→ verification receipt
→ receipt index
→ local verifier UI result
```

### Test Class 5 — Non-Execution and Non-Authority

Must prove:

* graph builder does not execute tools
* graph builder does not call external systems
* graph builder does not mutate source artifacts
* graph builder does not create new approvals
* graph builder does not create new receipts
* graph builder does not create new receipt indexes
* graph builder does not authorize execution
* graph builder does not promote proposal capture into approval

### Test Class 6 — Mutation Detection

Must prove:

* changing a node changes graph_hash
* changing an edge changes graph_hash
* changing a source artifact hash causes verification failure
* removing a required node causes verification failure
* removing a required edge causes verification failure

### Test Class 7 — Boundary Language

Must prove:

* output and docs do not claim production custody
* output and docs do not claim legal admissibility
* output and docs do not claim regulatory compliance
* output and docs do not claim real-world truth
* output and docs do not claim safety or correctness
* output states graph is a projection, not authority

## Allowed Outputs for Future Implementation

Allowed output strings:

```text
GOVERNANCE RECORD GRAPH BUILD PASS
GOVERNANCE RECORD GRAPH VERIFY PASS
GRAPH HASH VERIFY PASS
GRAPH MUTATION CHECK PASS
SOURCE ARTIFACT CHECK PASS
EDGE DERIVATION CHECK PASS
GRAPH PROJECTION ONLY
NO EXECUTION AUTHORITY CREATED
```

Forbidden output strings:

```text
PRODUCTION READY
COMPLIANT
CERTIFIED
LEGALLY VALID
LEGAL AUDIT PASS
SAFE TO EXECUTE
CORRECT ACTION
REAL WORLD TRUTH VERIFIED
AUTHORITY CREATED
APPROVAL CREATED
EXECUTION AUTHORIZED
```

## Non-Claims

v1.0 does not claim:

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
* real-world truth of evidence
* legal validity of approval
* safety of the original action
* execution authority
* hosted product readiness
* graph database readiness
* RAG correctness
* retrieval quality
* ontology completeness

## What v1.0 Prevents

Document these failure modes:

1. Graph-as-authority

The graph is treated as a new source of authority.

This is forbidden. The graph is a projection.

2. Relationship invention

The graph creates edges not supported by source artifacts or verifier outputs.

This is forbidden. Edges must be derivable.

3. Evidence inflation

The graph makes evidence appear stronger than the evidence manifest supports.

This is forbidden. Evidence truth is not proven by v1.0.

4. Execution leakage

The graph builder or verifier executes tools while building or checking the graph.

This is forbidden. v1.0 is non-executing.

5. Product overclaiming

The graph is described as compliant, legally valid, production ready, safe, or correct.

This is forbidden.

6. RAG drift

v1.0 expands into ingestion, embeddings, vector search, reranking, or LLM generation.

This is forbidden. v1.0 is a governance record graph, not a RAG pipeline.

## Implementation Blocker

No v1.0 implementation may begin until this acceptance-gate document is committed, merged to main, and the current v0.9 baseline is confirmed passing on main.
