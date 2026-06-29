# Governed Consequence Routing v0.9 -- Runtime Proposal Hook Acceptance Gate

This document defines the proof boundary and acceptance gate for v0.9 before any Runtime Proposal Hook implementation begins.

v0.9 is a proposal-capture boundary.

It is not an execution layer.

It is not an authorization layer.

It is not an agent gateway.

---

## Proof Sentence

v0.9 proves that a live or simulated AI-agent proposal can be captured before execution and converted into a governed proposal record without granting execution authority.

---

## Core Boundary

v0.9 proves proposal capture.

v0.9 does not prove execution authority.

Hard fail rule:

```text
If a runtime proposal hook causes execution, v0.9 fails.
```

---

## Central Invariant

The runtime proposal hook may capture, normalize, classify, and emit a governed proposal record.

The runtime proposal hook may not authorize, execute, mutate policy, mutate evidence, mutate authority, create approvals, create receipts, create indexes, bypass verifiers, or grant operational permission.

The hook may:

* capture a proposed AI-agent action or consequence
* assign a proposal identifier
* record the proposing agent identifier
* record the proposed action or proposed consequence
* normalize the proposed action into a consequence-oriented representation
* classify the consequence
* compute hashes for the proposal and normalized consequence
* emit a governed proposal record
* mark execution status as NOT_EXECUTED
* hand the record to existing governance/verifier paths later

The hook may not:

* authorize execution
* execute tools
* call external systems
* mutate files outside explicit test/temp output
* mutate policy
* mutate evidence
* mutate reviewer authority
* create approval tokens
* create verification receipts
* create receipt indexes
* bypass existing verifier logic
* claim compliance, legal status, production readiness, safety, or correctness
* silently convert model output into authority

---

## Proposed v0.9 Artifact Boundary

The future implementation may add only these artifact types unless the acceptance gate is amended first:

* schema for a runtime proposal record
* example runtime proposal fixture
* local capture tool for simulated proposals
* tests for proposal capture and non-execution
* release notes after implementation
* README polish only after release

Allowed future artifact paths:

```text
schemas/runtime_proposal_v0.9.schema.json
examples/runtime_proposal/proposal.v0.9.json
tools/capture_runtime_proposal.py
tests/test_runtime_proposal_hook.py
docs/governance/runtime-proposal-hook-v0.9.md
RELEASE_NOTES_v0.9.md
```

No implementation should be added in this acceptance-gate commit.

---

## Proposed Runtime Proposal Record

The future runtime proposal record should represent a proposal before execution.

Required conceptual fields:

* proposal_id
* schema_version
* created_at
* agent_id
* source
* proposed_action
* proposed_action_hash
* normalized_consequence
* normalized_consequence_hash
* consequence_classification
* consequence_risk
* execution_status
* authorization_status
* record_hash
* proof_boundary

Required status values:

```text
execution_status must be NOT_EXECUTED.
authorization_status must be NOT_AUTHORIZED or REQUIRES_GOVERNANCE.
```

The record_hash must be computed over canonical serialization excluding record_hash itself.

---

## Acceptance Gate

v0.9 passes only when all of the following are true.

If any check fails, v0.9 is not sealed.

### Proposal Capture Checks

* [ ] A simulated proposal can be captured into a runtime proposal record.
* [ ] The captured record includes proposal_id, agent_id, proposed_action, normalized_consequence, consequence_classification, execution_status, authorization_status, and record_hash.
* [ ] proposed_action_hash matches the proposed_action.
* [ ] normalized_consequence_hash matches the normalized_consequence.
* [ ] record_hash verifies.
* [ ] The record validates against the v0.9 schema.

### Non-Execution Checks

* [ ] execution_status is always NOT_EXECUTED.
* [ ] authorization_status is never AUTHORIZED.
* [ ] The hook does not execute tools.
* [ ] The hook does not call external systems.
* [ ] The hook does not mutate policy, evidence, reviewer authority, approval tokens, receipts, or indexes.
* [ ] The hook does not create governance artifacts other than the allowed runtime proposal record.
* [ ] The hook does not write outside the explicitly requested output path or test temp directory.

### Authority Boundary Checks

* [ ] The hook does not create approval tokens.
* [ ] The hook does not approve or deny proposals as final governance decisions.
* [ ] The hook does not replace reviewer authority checks.
* [ ] The hook does not bypass existing verifier tools.
* [ ] The hook does not claim that capture equals authorization.

### Failure Checks

* [ ] Invalid proposal input fails closed.
* [ ] Missing proposed_action fails closed.
* [ ] Missing agent_id fails closed.
* [ ] Unknown consequence classification fails closed or is marked UNKNOWN.
* [ ] Any attempted execution path fails the test suite.
* [ ] Any attempted authorization path fails the test suite.

### Hard Fail Rule

* [ ] If the runtime proposal hook causes execution, v0.9 fails.

### Boundary Language Check

* [ ] Documentation states that v0.9 proves proposal capture, not execution authority.
* [ ] Documentation states that model output does not become authority.
* [ ] Documentation does not claim production custody, legal admissibility, regulatory compliance, clinical safety, financial suitability, enterprise identity, non-repudiation, correctness, or safety.
* [ ] Documentation does not claim that proposal capture proves the action should execute.

### Full Test Suite

* [ ] `python -m pytest -q` reports 161 + new v0.9 tests passing after implementation.

---

## Required Tests for Future v0.9 Implementation

These tests are required for the future v0.9 implementation.

They are not implemented by this acceptance-gate document.

### Test Class 1 -- Valid Proposal Capture

Must prove:

* a simulated proposal is captured
* the record validates against schema
* proposal hash verifies
* normalized consequence hash verifies
* record hash verifies
* execution_status is NOT_EXECUTED
* authorization_status is not AUTHORIZED

### Test Class 2 -- Non-Execution

Must prove:

* capture does not execute any tool
* capture does not call external systems
* capture does not mutate source fixtures
* capture writes only the allowed output record
* capture creates no approval tokens, receipts, receipt indexes, bundles, evidence manifests, or authority manifests

### Test Class 3 -- Failure Behavior

Must prove:

* missing agent_id fails closed
* missing proposed_action fails closed
* malformed input fails closed
* unknown consequence classification is not allowed to become authorized
* attempted execution fails the test suite

### Test Class 4 -- Boundary Language

Must prove:

* output and docs do not claim compliance, certification, legal admissibility, production readiness, safety, or correctness
* output states capture is not authorization
* output states execution did not occur

### Test Class 5 -- Integration Boundary

Must prove:

* the proposal record is suitable as input to later governance record formation
* v0.9 does not itself complete the full v1.0 governance record layer

---

## Allowed Outputs for Future Implementation

Allowed output strings:

```text
PROPOSAL CAPTURED
CONSEQUENCE NORMALIZED
RUNTIME PROPOSAL RECORD CREATED
EXECUTION_STATUS: NOT_EXECUTED
AUTHORIZATION_STATUS: NOT_AUTHORIZED
AUTHORIZATION_STATUS: REQUIRES_GOVERNANCE
```

Forbidden output strings:

```text
ACTION EXECUTED
TOOL EXECUTED
AUTHORIZED
APPROVED
COMPLIANT
CERTIFIED
LEGALLY VALID
PRODUCTION READY
SAFE
CORRECT
```

AUTHORIZED may appear only as part of NOT_AUTHORIZED.

---

## Non-Claims

v0.9 does not claim:

* execution authority
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
* that proposal capture equals approval
* that model output becomes authority
* that a captured proposal should execute

---

## What v0.9 Prevents

### 1. Silent Execution

The hook captures a proposal and also executes it.

This is forbidden. If capture causes execution, v0.9 fails.

### 2. Authority Inflation

The hook turns a captured proposal into an approval or authorization.

This is forbidden. Capture is not authority.

### 3. Record Pollution

The hook mutates policy, evidence, authority, receipts, indexes, or bundles while capturing a proposal.

This is forbidden. v0.9 is a proposal-capture layer only.

### 4. Overclaiming

The hook or docs claim compliance, legal validity, production readiness, safety, or correctness.

This is forbidden.

### 5. Model-Output Authority Leakage

The system treats the model's proposal as permission to act.

This is forbidden.

---

## Implementation Blocker

No v0.9 implementation may begin until this acceptance-gate document is committed, merged to main, and the current v0.8 verifier/UI baseline is confirmed passing on main.
