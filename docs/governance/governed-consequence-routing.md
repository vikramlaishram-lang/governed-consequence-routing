# Governed Consequence Routing



> The model reasons. The policy decides. The record proves.



Governed Consequence Routing is a reference architecture for governing proposed AI-agent consequences.



The central claim is:



> The unit of governance in an agentic system is the proposed consequence, not the tool call.



A tool call is a mechanism.



A proposed consequence is what may affect a system, organization, person, policy, claim, release, workflow, or external state.



\---



## Constitutional Statements



1. The unit of governance in an agentic system is the proposed consequence, not the tool call.



2. DRF/OMTIR composes policy-bound authorization, evidence-linked claim admission, state-witness approval binding, and hash-chained audit records at the agentic decision boundary.



3. Their logs explain execution. Our envelope adjudicates authority.



4. The model reasons. The policy decides. The record proves.



\---



## Core Insight



AI governance is not primarily about making models behave nicely.



It is about preventing model outputs from silently becoming authority.



In agentic systems, model outputs can begin to behave like authority:



```text id="q5xo2w"

a claim becomes accepted truth

a recommendation becomes action

a handoff becomes delegated permission

a summary becomes an official record

a prediction becomes decision basis

a tool call becomes institutional consequence

```



Governance must control the transition from:



```text id="754ccv"

model output

```



to:



```text id="tuj4ex"

operational authority

```



That transition requires explicit gates:



```text id="i05rxw"

evidence gate

policy gate

authority gate

execution boundary

record gate

verification gate

```



\---



## Architecture



```text id="lqxt0i"

Agent / Gateway / MCP Proxy

&#x20;       â†“

governance_event.v0.1

runtime source event

what the gateway emits

operational telemetry

&#x20;       â†“

Promotion Contract v0.1

field mapping

normalization

hash computation

invariant validation

&#x20;       â†“

decision_envelope.v0.1

canonical governance record

what the governance layer is willing to defend

&#x20;       â†“

Envelope Verifier

schema verification

hash verification

chain verification

invariant verification

mutation verification

&#x20;       â†“

Trust Receipt / Audit Export / External Review

```



Locked principle:



> A governance event is what the runtime emits. A decision envelope is what the governance layer is willing to defend.



\---



## Governed Object



The governed object is not merely:



```text id="tn90vo"

tool call

message

trace

permission

log entry

model output

```



The governed object is:



```text id="c3ricx"

proposed consequence

```



A proposed consequence may appear as:



```text id="j9zf4p"

a tool call

a generated claim

a delegated task

an agent handoff

a release recommendation

an external communication

a policy mutation

a workflow modification

a system-state change

```



The same governance architecture can apply because the system routes the consequence through:



```text id="y2rjir"

classification

policy

evidence

authority

execution boundary

record

verification

```



\---



## Decision Envelope



`decision_envelope.v0.1` is the canonical governance record.



It records:



```text id="kufscn"

who proposed the consequence

what was proposed

how it was normalized

how it was classified

which policy applied

which evidence state applied

whether review was required

whether authority was present

what decision was made

whether execution occurred

what outcome resulted

how the record links to the prior record

what hash proves integrity

```



A log says:



```text id="g5t3k6"

The agent called read_file(".env").

```



A decision envelope says:



```text id="6mw5uc"

The agent proposed a credential-exposure consequence.

The active policy denied it.

Execution was blocked.

The record links to the prior envelope.

The verifier can recompute the hash chain.

```



That is the distinction behind:



> Their logs explain execution. Our envelope adjudicates authority.



\---



## Promotion Contract



`Promotion Contract v0.1` defines how runtime events become formal decision envelopes.



It exists because runtime events and governance records serve different purposes.



```text id="2r93j2"

governance_event.v0.1

= runtime source event

= fast, operational, telemetry-oriented



decision_envelope.v0.1

= canonical governance record

= formal, normalized, hash-chained, independently verifiable

```



The promotion contract is the transformation boundary.



It must not silently invent missing values.



It must not silently weaken the record.



It must fail clearly when required governance information is missing.



\---



## Envelope Verifier



The verifier is the independent proof layer.



The promoter creates envelopes.



The verifier proves envelopes.



The verifier must independently check:



```text id="mqsz9y"

schema validity

required fields

proposal_hash

normalized_action_hash

record_hash

previous_record_hash linkage

constitutional invariants

review / execution consistency

mutation detection

```



The verifier must detect mutation of:



```text id="8g42lm"

proposed_action

normalized_action

decision

previous_record_hash

record_hash

classification_confidence

consequence_class

execution_status

```



If any mutation survives, the verifier is not ready.



\---



## Mandate Outcomes



Every proposed consequence resolves into one of four outcomes:



```text id="p95hlp"

ALLOW

DENY

REQUEST_REVIEW

QUARANTINE

```



### ALLOW



A bounded mandate is granted.



The proposed consequence is authorized within scope.



### DENY



A mandate is refused.



The proposed consequence must not execute.



### REQUEST_REVIEW



Authority is unresolved.



The proposed consequence requires review before execution.



### QUARANTINE



The proposal is isolated because it is unsupported, unsafe, ambiguous, outside policy, or otherwise inadmissible for normal execution.



\---



## Current Proof Boundary



The current build proves a local, inspectable core:



```text id="5zubwc"

strict Decision Envelope v0.1 schema

valid example envelopes

real proposal_hash values

real normalized_action_hash values

real record_hash values

valid previous_record_hash chain linkage

explicit proof-boundary documentation

local schema and example tests

```



It does not yet prove:



```text id="v98h4x"

production durability

independent custody

external notarization

SSO/OIDC reviewer identity

third-party validation

real-world adversarial robustness

legal admissibility by itself

regulator approval

```



The proof boundary is part of the architecture.



\---



## Market Position



This repository is not a general AI governance platform.



It is not a replacement for AI GRC systems.



It is not merely an AI gateway, firewall, or logging layer.



It is a runtime evidence architecture for governed consequence routing in agentic systems.



Best distinction:



> AI GRC governs use cases. Governed Consequence Routing governs consequence events.



Runtime distinction:



> Gateways enforce policy. Decision envelopes prove authority.



\---



## Build Sequence



The clean build proceeds in this order:



```text id="18fbns"

1. Decision Envelope v0.1 schema

2. Valid example envelopes with real hashes

3. Current proof boundary

4. Promotion Contract v0.1

5. Governed Consequence Routing overview

6. Promotion tool

7. Independent verifier

8. Real WAL promotion

9. Mutation verification

```



\---



## GO / NO-GO Condition



The stronger public claim is blocked until the real runtime path passes:



```powershell id="h1l571"

python tools/promote_to_envelope.py wal/ollama-events.jsonl -o envelopes.json --verify

python tools/verify_envelope_chain.py envelopes.json --mutate --verbose

```



Required mutation-detection output:



```text id="c8dj7b"

proposed_action mutation:           DETECTED

normalized_action mutation:         DETECTED

decision mutation:                  DETECTED

previous_record_hash mutation:      DETECTED

record_hash mutation:               DETECTED

classification_confidence mutation: DETECTED

consequence_class mutation:         DETECTED

execution_status mutation:          DETECTED

```



If any mutation survives:



```text id="b6wpfj"

NO COMMIT

NO TAG

NO PUBLIC CLAIM

```



\---



## Final Position



Governed Consequence Routing holds AI-agent output at the boundary between model generation and operational authority.



The model may propose.



The system must classify, evaluate, record, and verify.



Only then may a bounded mandate be granted.



That is AI governance made inspectable.




