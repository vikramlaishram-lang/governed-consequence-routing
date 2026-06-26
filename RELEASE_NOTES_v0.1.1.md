\# Governed Consequence Routing v0.1.1 Release Notes



Tag reference: `v0.1.1-local-ollama-adapter-docs`



\## Summary



v0.1.1 adds a local Ollama proposal adapter and boundary documentation.



This milestone demonstrates how local model output can be captured as proposal evidence, normalized into a governance event, promoted into a governed decision envelope, and verified without executing the proposed tool call.



The core boundary remains:



> The model may propose. It may not authorize.



\## Included in v0.1.1



\* `tools/ollama\_local\_adapter.py`

\* tests for Ollama proposal extraction and normalization

\* local adapter boundary documentation

\* proposal-only model boundary

\* governance-event emission from local model output

\* promotion into `decision\_envelope.v0.1`

\* independent verification of the promoted envelope

\* mutation-tested tamper detection



\## Verified Properties



This release demonstrates:



\* local Ollama model output can be captured as proposal evidence

\* reasoning text before JSON can be tolerated by proposal extraction

\* unsafe proposed tool names are normalized back to the safe local demo boundary

\* the adapter emits a `governance\_event.v0.1`

\* the event promotes into a `decision\_envelope.v0.1`

\* the verifier validates the resulting envelope

\* mutation checks detect tampering

\* no tool execution occurs



\## Boundary



The adapter does not execute proposed tool calls.



The adapter does not grant authority to Ollama.



The adapter does not treat model output as a policy decision.



The policy decision remains separate under `drf\_decision`.



The decision envelope remains the governed record.



\## Claims Not Made



This release does not claim:



\* production readiness

\* secure automatic parsing against all hostile model outputs

\* end-to-end governed live tool execution

\* enterprise deployment readiness

\* legal admissibility

\* third-party validation

\* external custody or notarization



\## Status



v0.1.1 is a local proposal-source adapter milestone.



It is suitable for demonstrating model-agnostic proposal capture while preserving the separation between model proposal, policy decision, and verifiable record.



