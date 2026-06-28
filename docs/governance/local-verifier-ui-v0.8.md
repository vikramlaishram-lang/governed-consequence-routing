# Governed Consequence Routing v0.8 -- Local Verifier UI Acceptance Gate

This document defines the proof boundary and acceptance gate for v0.8 before any Local Verifier UI implementation begins.

v0.8 is a presentation and invocation surface over existing GCR verifier tools.

It is not a new authority layer.

It is not a new policy layer.

It is not a new custody layer.

It is not a new verification semantics layer.

---

## Proof Sentence

v0.8 proves that existing GCR verification results can be exposed through a local human-facing interface without changing verification semantics.

---

## Central Invariant

For every verifier exposed through the UI:

```text
CLI output == UI output semantically
```

Semantic equality means:

* PASS in CLI -> PASS displayed in UI
* FAIL in CLI -> FAIL displayed in UI
* same failure reason in CLI -> same failure reason displayed in UI
* same hash values in CLI -> same hash values displayed in UI

The UI may format, color, or structure output differently.

The UI may not alter, abbreviate, reinterpret, summarize, promote, suppress, or replace the verification result.

Hard rule:

```text
If CLI verification and UI verification disagree, v0.8 fails.
```

---

## Verifiers Exposed

The v0.8 UI may expose exactly these seven verifier-fixture pairs, no more and no fewer.

The UI does not implement new verification logic.

The UI calls these exact scripts with these exact fixtures and displays the result.

### 1. Approval Token Verification

Verifier:

```text
tools/verify_approval_token.py
```

Input:

```text
examples/reviewer_authority/approval_token.v0.3.json
```

Output:

```text
APPROVAL TOKEN VERIFY PASS / FAIL
```

### 2. Reviewer Authority Binding Verification

Verifier:

```text
tools/verify_reviewer_authority_binding.py
```

Inputs:

```text
examples/reviewer_authority/manifest.v0.3.json
examples/reviewer_authority/approval_token.v0.3.json
```

Output:

```text
REVIEWER AUTHORITY BINDING VERIFY PASS / FAIL
```

### 3. Decision Envelope Approval Binding Verification

Verifier:

```text
tools/verify_decision_envelope_approval_binding.py
```

Inputs:

```text
examples/reviewer_authority/approved_decision_envelope.v0.3.json
examples/reviewer_authority/approval_token.v0.3.json
examples/reviewer_authority/manifest.v0.3.json
```

Output:

```text
DECISION ENVELOPE APPROVAL BINDING VERIFY PASS / FAIL
```

### 4. Evidence Manifest Binding Verification

Verifier:

```text
tools/verify_evidence_manifest_binding.py
```

Inputs:

```text
examples/evidence_manifest/evidence_bound_decision_envelope.v0.4.json
examples/evidence_manifest/manifest.v0.4.json
```

Output:

```text
EVIDENCE MANIFEST BINDING VERIFY PASS / FAIL
```

### 5. Portable Verification Bundle Verification

Verifier:

```text
tools/verify_ledger_bundle.py
```

Input:

```text
examples/verification_bundle/full_gcr_bundle.v0.5.json
```

Output:

```text
LEDGER BUNDLE VERIFY PASS / FAIL
```

### 6. Verification Receipt Verification

Verifier:

```text
tools/verify_verification_receipt.py
```

Input:

```text
examples/verification_receipt/verification_receipt.v0.6.json
```

Output:

```text
VERIFICATION RECEIPT VERIFY PASS / FAIL
```

### 7. Verification Receipt Index Verification

Verifier:

```text
tools/verify_receipt_index.py
```

Input:

```text
examples/verification_receipt_index/index.v0.7.json
```

Output:

```text
RECEIPT INDEX VERIFY PASS / FAIL
```

---

## Acceptance Gate

If any check fails, v0.8 is not sealed.

### Parity Checks

* [ ] verify_approval_token: CLI PASS == UI PASS
* [ ] verify_reviewer_authority_binding: CLI PASS == UI PASS
* [ ] verify_decision_envelope_approval_binding: CLI PASS == UI PASS
* [ ] verify_evidence_manifest_binding: CLI PASS == UI PASS
* [ ] verify_ledger_bundle: CLI PASS == UI PASS
* [ ] verify_verification_receipt: CLI PASS == UI PASS
* [ ] verify_receipt_index: CLI PASS == UI PASS

### FAIL Parity Checks

* [ ] Each verifier: tampered input -> CLI FAIL == UI FAIL
* [ ] Each verifier: failure reason matches between CLI and UI
* [ ] Each verifier: hash values reported by CLI match hash values displayed by UI

### Non-Introduction Checks

* [ ] UI does not store uploaded files
* [ ] UI does not modify fixture content
* [ ] UI does not create new governance artifacts
* [ ] UI does not add words not present in the verifier result or approved boundary text
* [ ] UI does not promote FAIL to PASS
* [ ] UI does not suppress failure reasons
* [ ] UI does not reinterpret verifier output

### Hard Fail Rule

* [ ] No CLI/UI disagreement on any fixture for any verifier

### Boundary Language Check

* [ ] UI displays approved proof boundary language
* [ ] UI does not claim: certified, compliant, legally, production, enterprise, admissible, safe, correct

### Full Test Suite

* [ ] `python -m pytest -q` reports 127 + new v0.8 tests passing

---

## Required Tests for v0.8 Implementation

These test classes are required for the future v0.8 implementation.

They are not implemented by this acceptance-gate document.

### Test Class 1 -- Semantic Parity On PASS

One test per verifier.

Each test must:

1. Run the CLI verifier and capture stdout, stderr, and status.
2. Invoke the UI verifier path with the same input.
3. Assert PASS/FAIL status matches.
4. Assert the primary output string appears in the UI response.
5. Assert hash values match where applicable.

### Test Class 2 -- Semantic Parity On FAIL

One test per verifier with tampered input.

Each test must:

1. Run the CLI verifier against tampered input.
2. Invoke the UI verifier path with the same tampered input.
3. Assert both return FAIL.
4. Assert failure reason matches.
5. Assert UI does not suppress or rewrite the failure.

### Test Class 3 -- Non-Introduction Tests

Required future tests:

* UI does not store uploaded files
* UI does not modify fixture content
* UI does not create new governance artifacts
* UI does not claim beyond verifier output and approved boundary text
* UI does not add forbidden claim words
* UI does not add governance authority
* UI does not promote FAIL to PASS

### Test Class 4 -- Hard Fail Rule

Required future test:

For every verifier-fixture pair, if CLI and UI disagree on PASS/FAIL, the test must fail.

---

## Forbidden Additions

The v0.8 UI may not include or claim:

* certification
* compliance status
* legal admissibility
* production readiness
* enterprise identity
* external custody
* external notarization
* safety of the original action
* correctness of the original action
* real-world truth of evidence
* legal validity of approval
* non-repudiation
* new authorization
* new policy decision
* new governance authority

The UI may not create a new:

* decision
* approval
* receipt
* index
* bundle
* evidence manifest
* authority manifest
* policy result
* governance claim

---

## What v0.8 Prevents

### 1. Result Drift

Example:

```text
APPROVAL TOKEN VERIFY PASS becomes "Verified"
```

This is not acceptable because it changes the semantic surface.

### 2. Silent File Storage

The UI accepts an uploaded fixture and stores it locally without explicit user intent.

This is not acceptable because v0.8 is an interface layer, not a custody layer.

### 3. Overclaiming

The UI adds language like "compliant", "certified", "legally valid", or "production ready".

This is not acceptable because the verifier does not make those claims.

### 4. Authority Inflation

The UI turns a verifier result into approval or authorization.

This is not acceptable because the UI has no authority.

---

## Local Interface Boundary

The local verifier UI is only:

```text
local verifier UI
        |
        v
existing verifier tools
        |
        v
receipt index / receipt / bundle checks
        |
        v
same PASS / FAIL semantics as CLI
```

The UI may help a human inspect and invoke verifier results.

The UI may not become a substitute for verifier scripts, schemas, fixtures, release notes, or proof-boundary documents.

---

## Implementation Blocker

No v0.8 implementation may begin until this acceptance-gate document is committed and the seven verifier-fixture pairs are confirmed passing on current main.
