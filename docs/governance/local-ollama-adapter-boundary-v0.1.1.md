\# Local Ollama Adapter Boundary v0.1.1



\## Purpose



The local Ollama adapter demonstrates how a local model can act as a proposal source for Governed Consequence Routing.



It captures a model-generated proposal, normalizes it into a `governance\_event.v0.1`, promotes that event into a `decision\_envelope.v0.1`, and verifies the resulting envelope chain.



The adapter does not execute the proposed tool call.



\## Boundary Statement



Ollama proposes only.



The adapter captures and records the proposal.



Policy remains the source of decision authority.



The decision envelope is the governed record.



\## Flow



```text

Ollama / local model

&#x20;       ↓

proposal text

&#x20;       ↓

local adapter

&#x20;       ↓

governance\_event.v0.1

&#x20;       ↓

Promotion Contract v0.1

&#x20;       ↓

decision\_envelope.v0.1

&#x20;       ↓

independent verifier

&#x20;       ↓

mutation-tested verification

```



\## What the Adapter Does



The adapter:



\* calls a local Ollama model for a proposed tool call

\* extracts a JSON-like proposal from model output

\* normalizes the proposal into a safe governance-event shape

\* records model output as proposal evidence

\* emits a `governance\_event.v0.1`

\* promotes the event into a `decision\_envelope.v0.1`

\* runs the independent verifier

\* runs mutation checks

\* writes only local ignored smoke-test output under `wal/`



\## What the Adapter Does Not Do



The adapter does not:



\* execute the proposed tool call

\* grant authority to the model

\* treat model output as a policy decision

\* modify files requested by the model

\* access secrets

\* call external services

\* create production actions

\* make the Ollama adapter part of the sealed v0.1 proof boundary



\## Governance Principle



The local Ollama adapter preserves the core governance rule:



> The model may propose. It may not authorize.



In this adapter, Ollama output is recorded as proposal evidence, not as authority.



The policy decision is represented separately in the governance event under `drf\_decision`.



The verifier evaluates the resulting decision envelope, not the model's reasoning.



\## Verified v0.1.1 Behavior



The v0.1.1 local smoke test demonstrated:



\* Ollama `qwen3:8b` produced a proposal

\* the adapter captured the proposal

\* the proposal was wrapped into a governance event

\* the governance event was promoted into a decision envelope

\* the envelope verified successfully

\* mutation checks detected tampering

\* no tool execution occurred



\## Correct Public Claim



v0.1.1 adds a local Ollama proposal adapter that captures model output as proposal evidence, promotes it into a governed decision envelope, and verifies it without executing the proposed tool call.



\## Claims Not Made



This milestone does not claim:



\* production readiness

\* secure automatic JSON parsing against all hostile model outputs

\* end-to-end governed tool execution

\* enterprise deployment readiness

\* legal admissibility

\* third-party validation

\* external custody or notarization

\* automatic enforcement against live systems



\## Status



This is a local proposal-source adapter.



It is useful for demonstrating model-agnostic proposal capture while preserving the separation between proposal, policy decision, and verifiable record.



