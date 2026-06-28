\# GCR Behavioral Standard v0.1



\## 1. Master Thesis



Consequential AI systems must separate generation from authorization.



A model may generate an answer, proposal, tool call, recommendation, summary, claim, or action plan. But that generated output must not automatically become operational truth or executable authority.



For consequential use, AI systems should follow this behavioral pattern:



```text

Generate → classify → evidence-bind → authorize → record → verify → receipt

```



This standard defines the missing boundary between model generation and real-world consequence.



The core claim is:



```text

AI systems that can generate and act without a separation between proposal and authorization are architecturally incomplete for consequential use.

```



GCR does not attempt to make the model smarter. It does not claim to solve alignment, factuality, clinical validity, legal validity, or institutional judgment.



It defines the authority boundary around AI output.



The model proposes.



The policy decides.



The record proves.



\---



\## 2. The Seven Principles



\### Principle 1 — Proposal Is Not Authorization



A model output is a proposal, not permission.



A generated tool call, recommendation, answer, summary, or claim must not be treated as authorized merely because the model produced it.



The system must distinguish:



```text

generated output

```



from:



```text

authorized consequence

```



\### Principle 2 — Model Confidence Is Not Authority



Model confidence, fluency, reasoning quality, or persuasive explanation does not grant authority.



A model cannot authorize its own consequential action.



Authorization must come from policy, evidence, human authority, or a system-governed approval path outside the model’s control.



\### Principle 3 — Claims Require Evidence Before Admission



AI-generated claims must not become operational truth unless they are linked to admissible evidence.



The relevant question is not only:



```text

Is this claim likely true?

```



The relevant governance question is:



```text

Is this claim admissible for operational use?

```



A claim may be generated but still not admitted.



\### Principle 4 — Consequential Actions Require Policy Routing



Every proposed consequence must be classified and evaluated against policy before execution.



Policy routing may decide:



```text

ALLOW

DENY

REQUEST\_REVIEW

QUARANTINE

```



The policy must predate the proposal. A model must not invent the policy that authorizes its own output.



\### Principle 5 — Human Approval Requires Scoped Authority



A human approval is not automatically valid.



A reviewer name, identity string, or approval click is insufficient by itself.



Valid approval requires authority that is:



```text

scoped

active

time-bound

consequence-specific

policy-compatible

verifiable

```



Approval must not be reusable across different proposals, states, or time windows unless the policy explicitly permits that reuse.



\### Principle 6 — Records Must Be Verifiable



Consequential decisions must produce records that can be independently verified.



A log that only the original system can interpret is insufficient.



A compliant system must produce structured records with verifiable hashes, schemas, and verification logic that an external party can run.



\### Principle 7 — Users Need a Receipt, Not Just a Log



Technical logs are not enough.



A consequential AI system should produce a human-readable receipt that explains:



```text

what was proposed

how it was classified

what policy applied

what evidence was used

who or what authorized it

whether execution occurred

whether verification passed

```



The receipt is not the source of truth. The verifiable record is the source of truth.



The receipt is the human-readable explanation of that record.



\---



\## 3. Compliance Requirements



A system claiming conformance with GCR Behavioral Standard v0.1 must implement, at minimum, the following requirements.



\### Requirement 1 — Intercept Proposed Consequences Before Execution



The system must intercept proposed consequential actions before execution.



A system that only logs after execution is not compliant.



The governed boundary must occur before the proposed consequence is allowed to proceed.



\### Requirement 2 — Evaluate Against Predating Policy



The system must evaluate proposals against policy that exists before the proposal is made.



A model-generated justification cannot become the policy that authorizes the action.



The policy may be local, organizational, or externally defined, but it must be inspectable as a separate authority source.



\### Requirement 3 — Produce a Decision Envelope or Equivalent Formal Record



The system must produce a structured governance record containing, at minimum:



```text

proposal identifier

agent or system identifier

proposed consequence

classification

policy reference

decision

decision basis

review status if applicable

execution boundary

outcome status

record hash

previous record hash or equivalent chain context

```



This record is called a decision envelope in the GCR reference implementation.



Equivalent implementations may use different names, but they must preserve the same governance function.



\### Requirement 4 — Record the Chain From Proposal to Outcome



The system must record the complete governed chain:



```text

proposal

classification

policy decision

evidence reference where required

review or approval where required

execution boundary

outcome

verification material

```



Partial records are insufficient if they omit the decision path.



\### Requirement 5 — Provide an Independent Verifier



The system must provide verification logic that can be run independently by a party outside the original execution system.



A vendor-only dashboard is not sufficient.



A private database record is not sufficient.



A system-controlled audit view is not sufficient.



The verifier must be capable of detecting relevant record mismatches, missing fields, broken bindings, hash inconsistencies, or invalid approval linkage.



\---



\## 4. Scope Boundary



This standard governs the boundary between AI generation and consequential authorization.



It does not govern every part of an AI system.



\### In Scope



This standard governs:



```text

proposal-to-authorization separation

consequence classification

policy routing

evidence linkage for admitted claims

review and approval binding

authority scope verification

decision record creation

tamper-evident record verification

human-readable receipts

```



\### Out of Scope



This standard does not govern:



```text

model training

fine-tuning

alignment methods

RLHF

prompt engineering quality

model factual accuracy

model benchmark performance

policy quality

human reviewer judgment quality

institutional governance design

legal validity of signatures

regulatory compliance certification

clinical validity

financial advice suitability

```



The standard does not claim that the model is accurate.



The standard does not claim that the policy is wise.



The standard does not claim that the human reviewer made the right decision.



The standard claims only that consequential AI output passed through a governed boundary and produced a verifiable record of what was allowed, why, by whom or by what authority, and under what evidence.



\---



\## 5. Falsifiability Conditions



A behavioral standard must be falsifiable.



A system violates GCR Behavioral Standard v0.1 if any of the following conditions occur.



\### Violation 1 — Operational Use Without Governed Boundary



A model output becomes operational truth or executable action without passing through a governed boundary.



Example:



```text

The model generates a tool call and the system executes it directly without classification, policy decision, or record.

```



\### Violation 2 — Decision Without Predating Policy



A decision is made without policy that predates the proposal.



Example:



```text

The model explains why an action is safe, and that explanation is treated as the authorization policy.

```



\### Violation 3 — Record Cannot Be Independently Verified



A record exists, but an external party cannot verify it independently.



Example:



```text

The system provides a dashboard log, but no schema, hash, verifier, or portable verification material.

```



\### Violation 4 — Approval Reuse Across Proposal, State, or Time



An approval can be reused across different proposals, states, or time windows without explicit policy authorization.



Example:



```text

A reviewer approves release candidate A, code changes afterward, and the same approval is reused for release candidate B.

```



\### Violation 5 — Claim Admitted Without Evidence Linkage



An AI-generated claim is admitted into operational use without evidence linkage where evidence is required.



Example:



```text

The AI states that a release is ready, a patient has a condition, a customer is eligible, or a legal document supports a claim, but no source evidence is linked.

```



Any system that fails one or more of these conditions is not compliant with this standard.



\---



\## 6. Reference Implementation



The reference implementation for this standard is:



```text

governed-consequence-routing

```



Current public release:



```text

v0.3 — Reviewer Authority

```



GCR v0.3 implements the proposal-authority-record portion of this behavioral standard.



It demonstrates:



```text

decision envelopes

approval tokens

reviewer authority manifests

approval token hash verification

reviewer authority binding verification

decision-envelope approval binding verification

local test-backed verification

```



The v0.3 proof chain is:



```text

decision envelope

&#x20;       ↕

approval token

&#x20;       ↕

reviewer authority manifest

```



Current proof status:



```text

local reference implementation

public pre-release

78 passing tests

not production identity

not SSO-backed approval

not legal signature validity

not enterprise compliance

not legal admissibility

```



Future releases extend the standard:



```text

v0.4 — Evidence Manifest Binding

v0.5 — Portable Ledger / Verification Bundle Export

v0.6 — Hosted Verifier Demo

v0.7 — Agent Gateway Demo

```



The full behavioral pattern is complete only when evidence binding, portable verification, hosted verification, and execution-boundary demonstration are implemented.



\---



\## 7. Current Proof Boundary



This standard must be read together with the current proof-boundary documentation.



The current implementation proves local governance-record structure and verification behavior under controlled conditions.



It does not prove:



```text

production deployment readiness

external identity verification

SSO or OIDC-backed reviewer authentication

legal admissibility

regulatory compliance

clinical safety

financial advice suitability

non-repudiation

external notarization

enterprise custody

```



The current implementation is a reference implementation of the behavioral pattern, not a complete production governance platform.



\---



\## 8. Relationship to Product and Category



This standard is the source of truth.



The product is the standard made purchasable.



The category is the standard made visible.



The hierarchy is:



```text

The standard is the source of truth.

The category is the standard made visible.

The product is the category made purchasable.

```



Commercial simplification must not contradict the standard.



Category demonstrations must remain technically accurate against the standard.



The standard must not bend to accommodate marketing claims, demos, or sales language.



\---



\## 9. Commercial, Category, and Standard Statements



\### Commercial Statement



A developer starter kit for verifiable approval records around AI-agent actions.



\### Category Statement



A system for deciding whether AI-generated claims and actions are admissible for operational use.



\### Standard Statement



Consequential AI systems must separate generation from authorization and produce verifiable records of what was allowed, why, by whom, and under what evidence.



\---



\## 10. Constitutional Principle



The model proposes.



The policy decides.



The record proves.



