\# Governed Consequence Routing v0.1 Release Notes



Tag reference: `public-proof-readme-v0.1`



\## Summary



This release publishes a local reference implementation for governed consequence routing in agentic systems.



The core thesis is:



> The unit of governance in an agentic system is the proposed consequence, not the tool call.



This release demonstrates how runtime governance events can be promoted into decision envelopes, validated against a schema, linked through a hash chain, and independently verified with mutation-tested integrity checks.



\## Included in v0.1



\* `decision\_envelope.v0.1` JSON Schema

\* Valid example decision envelopes with recomputable hashes

\* Promotion Contract v0.1

\* Governance-event to decision-envelope promotion tool

\* Independent envelope-chain verifier

\* Fixture governance-event input

\* Schema, example, promoter, verifier, and mutation-detection tests

\* GitHub Actions CI workflow

\* README proof-status and proof-boundary documentation



\## Verified Properties



This release demonstrates:



\* JSON Schema validation of decision envelopes

\* recomputation of `proposal\_hash`

\* recomputation of `normalized\_action\_hash`

\* recomputation of `record\_hash`

\* previous-record hash-chain linkage

\* constitutional invariant checks

\* mutation-tested detection of envelope tampering

\* CI verification through GitHub Actions



\## Proof Boundary



This release does not claim production readiness, legal admissibility, third-party validation, complete AI governance coverage, external custody, independent notarization, or SSO-backed reviewer identity.



Those remain future proof-boundary items.



\## Current Status



v0.1 is a public reference architecture and local proof artifact.



It is suitable for inspection, discussion, reproducible local verification, and future extension.



