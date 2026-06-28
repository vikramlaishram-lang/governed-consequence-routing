# Current Proof Boundary

This document states what the current Governed Consequence Routing reference implementation proves and what it does not prove.

Publishing limitations is not weakness.

It is part of trust architecture.

---

## Current Public Proof Status

The current proof layer is:

```text
v0.6 — Verification Receipt
```

v0.6 proves that a portable GCR bundle can be independently verified and that the verification run can be recorded as a durable local receipt.

The current proof ladder is:

```text
v0.3:
decision envelope ↔ approval token ↔ reviewer authority manifest

v0.4:
decision envelope ↔ evidence manifest ↔ evidence items

v0.5:
portable verification bundle
        ↕
decision envelope
        ↕
approval token ↔ reviewer authority manifest
        ↕
evidence manifest ↔ evidence items

v0.6:
verification receipt
        ↕
portable verification bundle
        ↕
decision envelope
        ↕
approval token ↔ reviewer authority manifest
        ↕
evidence manifest ↔ evidence items
```

---

## v0.6 — Verification Receipt

### Proof Sentence

v0.6 proves that a portable GCR bundle can be independently verified and that the verification run can be recorded as a durable local receipt.

### What Is Proven

Under local reference conditions, v0.6 proves that:

* a portable GCR bundle can be verified by the local ledger bundle verifier
* the verifier can emit a durable verification receipt
* the receipt records verifier metadata, bundle subject, schema hashes, artifact hashes, checks performed, verification results, failure reasons, proof boundary, and receipt hash
* the receipt hash can be independently recomputed and checked
* a standalone receipt verifier can validate the receipt schema, hash, PASS/FAIL consistency, and failure-reason rules

### What Is Not Proven

v0.6 does not prove:

* correctness of the underlying AI action
* real-world truth of the evidence
* legal validity of the approval
* safety of the original action
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

### Design Rule

The receipt attests to a verification run.

It does not re-authorize the original action.

It does not replace the bundle.

It does not create legal or compliance status.

A verification receipt is evidence of verification, not evidence of correctness.

---

## v0.5 — Portable Verification Bundle

### Proof Sentence

v0.5 proves that a governed AI decision can be exported into a portable verification bundle whose included artifacts, hashes, verification results, and proof-boundary metadata are independently inspectable and locally verifiable.

### What Is Proven

Under local reference conditions, v0.5 proves that:

* a decision envelope, approval token, reviewer authority manifest, evidence manifest, and evidence items can be packaged into a portable verification bundle
* artifact hashes can be recomputed and checked
* schema hashes can be checked using canonical parsed JSON hashing
* verification results can be included in the bundle
* proof-boundary metadata can travel with the bundle
* the bundle can be independently verified locally

### What Is Not Proven

v0.5 does not prove:

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

---

## v0.4 — Evidence Manifest Binding

### Proof Sentence

v0.4 proves that a decision envelope can be bound to a structured evidence manifest whose hash, required evidence, admissibility decision, and envelope linkage are independently verifiable under local reference conditions.

### What Is Proven

Under local reference conditions, v0.4 proves that:

* a decision envelope can reference a structured evidence manifest
* the evidence manifest hash can be recomputed and checked
* required evidence can be represented explicitly
* evidence admissibility can be recorded
* envelope-to-manifest linkage can be independently verified

### What Is Not Proven

v0.4 does not prove:

* real-world truth of the evidence
* external evidence custody
* production compliance
* legal admissibility
* clinical safety
* financial advice suitability
* enterprise custody
* SSO-backed identity
* external notarization
* third-party validation

---

## v0.3 — Reviewer Authority Binding

### Proof Sentence

v0.3 proves that a decision envelope can be bound to an approval token and reviewer authority manifest under local reference conditions.

### What Is Proven

Under local reference conditions, v0.3 proves that:

* an approval token can be represented as a structured artifact
* a reviewer authority manifest can define reviewer scope
* an approval token can be bound to reviewer authority
* a decision envelope can be bound to the approval token
* the approval chain can be locally verified

### What Is Not Proven

v0.3 does not prove:

* SSO-backed reviewer identity
* production identity
* legal signature validity
* production custody
* enterprise compliance
* external notarization
* non-repudiation

---

## Local Reference Implementation Boundary

The current implementation remains a local reference implementation and developer starter kit.

It uses local schemas, local examples, local hash computation, local verification tools, and local test fixtures.

It does not observe or guarantee:

* external infrastructure state
* production reviewer identity
* real-world legal authority
* real-world evidence truth
* external audit custody
* external timestamping
* regulatory acceptance
* adversarial robustness in production environments

---

## Acceptable Public Claim

Acceptable:

> Governed Consequence Routing is a local reference implementation for generating and verifying governance records around AI-agent actions.

Acceptable:

> GCR creates and verifies portable governance records for AI-agent actions, binding proposal, authority, evidence, decision, and proof boundary into an inspectable record.

Acceptable:

> v0.6 adds a verification receipt that records a local verifier run over a portable GCR bundle.

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

## Final Boundary

The current project is strong because it makes its proof boundary explicit.

The current build is not a full governance platform.

It is the inspectable core of a governance-record system:

```text
decision envelope
+
reviewer authority binding
+
evidence manifest binding
+
portable verification bundle
+
verification receipt
+
local verifiers
```

That is the current proof boundary.
