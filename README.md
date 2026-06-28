# Governed Consequence Routing

**The model proposes. The policy decides. The record proves.**

Governed Consequence Routing is a local reference implementation for generating and verifying governance records around AI-agent actions.

It demonstrates how consequential AI proposals can be represented as inspectable records that bind proposal, authority, evidence, decision, verification, receipt history, receipt-index membership, interface exposure, and proof boundary.

---

## Current Release

```text
Governed Consequence Routing v0.8 — Local Verifier UI
```

Expected local test result:

```text
161 passed
```

Current proof ladder:

```text
v0.3 -> v0.4 -> v0.5 -> v0.6 -> v0.7 -> v0.8
```

Current release tag:

```text
v0.8-local-verifier-ui
```

Current v0.8 proof sentence:

```text
Existing GCR verification results can be exposed through a local human-facing interface without changing verification semantics.
```

Core v0.8 boundary:

```text
The UI is interface exposure only.
It does not create new governance authority.
If CLI verification and UI verification disagree, v0.8 fails.
```

---

## Current Public Proof Status

Current proof layer:

```text
v0.8 — Local Verifier UI
```

v0.8 proves that existing GCR verification results can be exposed through a local human-facing interface without changing verification semantics.

The UI may display existing verifier results. It may not create new verification semantics, new approvals, new decisions, new receipts, new indexes, runtime hooks, upload persistence, production custody, legal/compliance status, or correctness claims.

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
        ^
        |
decision envelope
        ^
        |
approval token <-> reviewer authority manifest
        ^
        |
evidence manifest <-> evidence items
```

---

## What This Repository Contains

This repository contains a local developer reference implementation for **Verifiable AI Governance Records**.

Core artifacts include:

* decision envelope examples
* reviewer authority manifest
* approval token example
* evidence manifest example
* portable verification bundle example
* verification receipt examples
* verification receipt index example
* local verifier UI
* CLI/UI semantic parity tests
* JSON schemas
* local verification tools
* governance documentation
* release notes through v0.7
* v0.8 release notes in the GitHub Release for tag `v0.8-local-verifier-ui`
* buyer/developer quick start
* test suite

The repository is intended to make the governance record chain inspectable, testable, and reproducible under local reference conditions.

---

## Core Pattern

```text
Generate -> classify -> evidence-bind -> authorize -> record -> verify -> receipt -> index -> expose through local UI
```

The system does not treat model output as authority.

It records proposed consequences, binds them to policy, evidence, reviewer authority, verification results, verification receipts, receipt-index membership, interface exposure, and proof-boundary metadata.

---

## Key Entry Points

### Standards and Governance

* `docs/standard/GCR_BEHAVIORAL_STANDARD_v0.1.md`
* `docs/governance/current-proof-boundary.md`
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

v0.8 release notes are published in the GitHub Release for tag:

```text
v0.8-local-verifier-ui
```

### Schemas

* `schemas/decision_envelope_v0.1.schema.json`
* `schemas/approval_token_v0.3.schema.json`
* `schemas/reviewer_authority_manifest_v0.3.schema.json`
* `schemas/evidence_manifest_v0.4.schema.json`
* `schemas/verification_bundle_v0.5.schema.json`
* `schemas/verification_receipt_v0.6.schema.json`
* `schemas/verification_receipt_index_v0.7.schema.json`

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

### Verification Tools

* `tools/verify_approval_token.py`
* `tools/verify_reviewer_authority_binding.py`
* `tools/verify_decision_envelope_approval_binding.py`
* `tools/verify_evidence_manifest_binding.py`
* `tools/export_ledger_bundle.py`
* `tools/verify_ledger_bundle.py`
* `tools/verify_verification_receipt.py`
* `tools/verify_receipt_index.py`
* `tools/local_verifier_ui.py`

### Tests

* `tests/test_local_verifier_ui.py`

The v0.8 UI tests verify CLI/UI semantic parity, hard fail behavior, unknown verifier rejection, fixture non-mutation, no upload storage, no new governance artifacts, FAIL-not-promoted behavior, forbidden overclaim language checks, and primary output parity.

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
161 passed
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

### Verification Receipt Emission

Use a generated receipt path so the stable fixture is not overwritten:

```powershell
python .\tools\verify_ledger_bundle.py .\examples\verification_bundle\full_gcr_bundle.v0.5.json --receipt-out .\examples\verification_receipt\verification_receipt.generated.v0.6.json
```

Expected:

```text
LEDGER BUNDLE VERIFY PASS
```

### Generated Verification Receipt Verification

```powershell
python .\tools\verify_verification_receipt.py .\examples\verification_receipt\verification_receipt.generated.v0.6.json
```

Expected:

```text
VERIFICATION RECEIPT VERIFY PASS
```

Remove the generated receipt after smoke testing:

```powershell
Remove-Item .\examples\verification_receipt\verification_receipt.generated.v0.6.json
```

### Stable Receipt Fixture Verification

```powershell
python .\tools\verify_verification_receipt.py .\examples\verification_receipt\verification_receipt.v0.6.json
python .\tools\verify_verification_receipt.py .\examples\verification_receipt\verification_receipt.fail.v0.7.json
```

Expected:

```text
VERIFICATION RECEIPT VERIFY PASS
VERIFICATION RECEIPT VERIFY PASS
```

Stable fixture receipt hashes:

```text
v0.6 PASS receipt_hash: sha256:abd980d2c7ac825522f1caf6466667f9a2a9afb2d2b6c5ce7e73007c30320864
v0.7 FAIL receipt_hash: sha256:f9214ffb70f8636134e0dccb16735576a37e7085ff34f216b0207e04b5828722
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

Stable fixture index values:

```text
index_id: 77777777-7777-4777-8777-777777777777
receipt_count: 2
status_counts: PASS 1, FAIL 1
index_hash: sha256:ec4ab3dfb958df29c05da0214999031fde663496f55442681ca866fd95337b59
```

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

## What v0.8 Adds

v0.8 adds a local human-facing verifier interface over existing GCR verifier tools.

It adds:

* local verifier UI entrypoint
* seven approved verifier surfaces
* CLI/UI semantic parity tests
* hard fail rule tests
* fixture non-mutation tests
* no-upload-storage tests
* no-new-governance-artifact tests
* forbidden overclaim language checks
* primary output parity tests

v0.8 proves interface exposure, not new governance authority.

The UI may display existing verification results.

The UI may not:

* change verification semantics
* create new approvals
* create new decisions
* create new receipts
* create new receipt indexes
* create new bundles
* create new evidence manifests
* create new authority manifests
* create runtime hooks
* persist uploads
* promote FAIL to PASS
* suppress failure reasons
* reinterpret verifier output
* claim compliance, legal admissibility, production custody, safety, or correctness

---

## What v0.7 Adds

v0.7 adds a verification receipt index as a governance-record layer.

The index records local membership for multiple verification receipts.

It records:

* index identifier
* schema version
* created and updated timestamps
* receipt count
* receipt entries
* PASS and FAIL status counts
* latest verification time
* index hash

Proof distinction:

```text
index_hash proves:   the membership of this index has not changed
receipt_hash proves: this specific receipt has not been modified
verifier proves:     the receipt was valid when it was verified
```

The index does not re-verify the receipts it indexes.

The index records receipt membership and the recorded status at the time the receipt was added.

Index integrity is not the same as receipt validity.

Receipt validity is not the same as real-world correctness.

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
* that index membership proves receipt validity
* that receipt validity proves real-world correctness
* that the UI creates governance authority
* that the UI creates new verification semantics
* that the UI certifies, validates, or approves the underlying AI action

The current implementation uses local schemas, local examples, local hash computation, local verification tools, a local verifier UI, and local test fixtures.

---

## Acceptable Public Claims

Acceptable:

> Governed Consequence Routing is a local reference implementation for generating and verifying governance records around AI-agent actions.

Acceptable:

> GCR creates and verifies portable governance records for AI-agent actions, binding proposal, authority, evidence, decision, receipt history, interface exposure, and proof boundary into an inspectable record.

Acceptable:

> v0.7 adds a local verification receipt index whose membership and integrity can be independently verified.

Acceptable:

> v0.8 exposes existing GCR verifier results through a local human-facing interface without changing verifier semantics.

Not acceptable:

> Index membership proves receipt validity or real-world correctness.

Not acceptable:

> The UI creates new governance authority.

Not acceptable:

> The UI certifies the underlying AI action.

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
GCR creates and verifies portable governance records for AI-agent actions, binding proposal, authority, evidence, decision, receipt history, interface exposure, and proof boundary into an inspectable record.
```

---

## Development Status

Current public release:

```text
Governed Consequence Routing v0.8 — Local Verifier UI
```

Current expected local test result:

```text
161 passed
```

Current proof chain:

```text
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
        ^
        |
decision envelope
        ^
        |
approval token <-> reviewer authority manifest
        ^
        |
evidence manifest <-> evidence items
```
