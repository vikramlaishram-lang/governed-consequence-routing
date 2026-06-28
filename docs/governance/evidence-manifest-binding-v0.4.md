# Evidence Manifest Binding v0.4

## 1. Why Evidence Binding Exists

Governed Consequence Routing treats a proposed consequence as the unit of governance. For AI-agent systems, a proposed consequence may include a factual claim, release-readiness claim, security claim, tool action, or other operational assertion.

v0.4 adds evidence manifest binding so consequential claims are not admitted into operational use merely because a model generated them. Model output is not evidence. Model confidence is not evidence.

The purpose of evidence binding is to require a local, inspectable record of what evidence was used, how that evidence relates to the proposal, whether it was admitted, and how it is hash-bound to the decision envelope.

## 2. Generated Claim vs. Admitted Claim

A claim may be generated but not admitted.

A generated claim is model output or agent-produced text that proposes, summarizes, asserts, or recommends something. Generated claims may be useful for drafting or review, but they do not automatically become evidence.

An admitted claim is a claim that is allowed into a governed decision path because required evidence has been linked, hash-bound, and verified according to the local proof rules.

Evidence must be external to the model output or explicitly marked as model-originated. If model output is included as an evidence item, it must be labeled as `MODEL_OUTPUT` so downstream review can distinguish generated material from external support.

## 3. Evidence Manifest Role

The evidence manifest records what sources were used, their hashes, their admissibility status, and their relationship to the proposal.

The manifest provides a structured local record for:

- evidence scope
- evidence items
- evidence source references
- evidence content hashes
- required evidence types
- minimum admitted evidence counts
- admissibility decision
- manifest integrity hash

This lets a verifier determine whether the proposal has the minimum evidence structure required before the claim or consequence is admitted.

## 4. Binding to a Decision Envelope

The evidence manifest binds to a decision envelope through shared identifiers and hashes:

- `proposal_id`
- `proposal_hash`
- `normalized_action_hash`
- `policy_hash`
- `evidence_manifest_hash`

The verifier recomputes the evidence manifest hash from canonical JSON, excluding the `evidence_manifest_hash` field itself. The decision envelope is validly evidence-bound only when its `evidence_manifest_hash` equals the manifest hash and the shared proposal and policy fields match.

## 5. What v0.4 Proves

v0.4 proves local evidence-binding structure and verification behavior only.

Specifically, v0.4 demonstrates that:

- an evidence manifest validates against a schema
- an evidence manifest has a recomputable integrity hash
- a decision envelope can bind to an evidence manifest hash
- proposal and policy hashes can be checked across the envelope and manifest
- admitted evidence items can satisfy required evidence types
- admitted evidence items can satisfy a minimum count rule
- insufficient or partial admissibility decisions fail local verification

## 6. What v0.4 Does Not Prove

v0.4 does not prove that the evidence source is true, complete, independently notarized, externally available, legally admissible, clinically safe, financially suitable, or production-grade.

It does not prove production identity, SSO-backed reviewer identity, enterprise custody, legal signature validity, regulatory compliance, clinical safety, financial advice suitability, or legal admissibility.

It also does not prove that model-generated output is evidence. Model-originated material may be recorded as an evidence item only when explicitly labeled as model-originated.

## 7. Current Proof Boundary

This remains a local reference implementation and developer starter kit.

The current proof boundary is:

- local JSON schema validation
- local canonical hash recomputation
- local decision-envelope-to-evidence-manifest binding
- local admitted-evidence requirement checks
- local verifier behavior tests

This proof boundary does not extend to external custody, production approval systems, legal or regulatory acceptance, clinical workflows, financial advice workflows, or enterprise compliance.
