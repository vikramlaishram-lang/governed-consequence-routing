\# Current Proof Boundary

## v0.5 Current Boundary

The current v0.5 proof layer is Portable Verification Bundle export and verification.

```text
v0.3:
decision envelope <-> approval token <-> reviewer authority manifest

v0.4:
decision envelope <-> evidence manifest <-> evidence items

v0.5:
portable verification bundle
        <->
decision envelope
        <->
approval token <-> reviewer authority manifest
        <->
evidence manifest <-> evidence items
```

v0.5 proves that a governed AI decision can be exported into a portable verification bundle whose included artifacts, hashes, verification results, and proof-boundary metadata are independently inspectable and locally verifiable.

This remains a local reference implementation and developer starter kit. It does not claim production custody, external notarization, legal admissibility, regulatory compliance, clinical safety, financial advice suitability, enterprise compliance, or non-repudiation.

---

## v0.4 Current Boundary

The current v0.4 proof layer is Evidence Manifest Binding.

```text
v0.3:
decision envelope <-> approval token <-> reviewer authority manifest

v0.4:
decision envelope <-> evidence manifest <-> evidence items
```

v0.4 proves that a decision envelope can be bound to a structured evidence manifest whose hash, required evidence, admissibility decision, and envelope linkage are independently verifiable under local reference conditions.

This remains a local reference implementation and developer starter kit. It does not claim production compliance, legal admissibility, clinical safety, financial advice suitability, enterprise custody, SSO-backed identity, external notarization, or third-party validation.

---



This document states what the current reference implementation proves and what it does not yet prove.



Publishing limitations is not weakness.



It is part of trust architecture.



\---



\## Current Claim



This project demonstrates a local, inspectable architecture for governed consequence routing in agentic systems.



The current v0.1 build focuses on:



```text

decision\_envelope.v0.1

valid example envelopes

hash-linked envelope chain

proof-boundary documentation

independent verification path

```



The project should not claim to solve all of AI governance.



It should claim a bounded architectural contribution:



> The unit of governance in an agentic system is the proposed consequence, not the tool call.



\---



\## Proven Locally



The broader DRF/OMTIR prototype has demonstrated the following local governance primitives under controlled conditions:



```text

policy-bound action authorization

evidence-linked claim admission

state-witness-bound approval tokens

hash-chained WAL / envelope sequence

review lifecycle with recorded transitions

Trust Receipt generation

local verifier checks

consequence-aware governance at the tool-call boundary

bounded local runtime / MCP proxy behavior

```



For this clean reference repository, the initial public proof surface is narrower:



```text

strict Decision Envelope v0.1 schema

valid example envelopes

real proposal\_hash values

real normalized\_action\_hash values

real record\_hash values

valid previous\_record\_hash chain linkage

explicit proof boundary

```



\---



\## Not Yet Proven



The current v0.1 build does not yet prove:



```text

production durability beyond local filesystem

durable key management and rotation

independent custody of audit records

independent third-party validation

real-world adversarial robustness

broad agent-framework integration

SSO/OIDC reviewer identity

external timestamping or notarization

public protocol adoption by external systems

full cross-session policy induction

complete cognitive-layer governance

formal legal admissibility

regulator approval

```



These are not defects in the claim.



They define the current proof boundary.



\---



\## Local MVP Conditions



The current work should be understood under local MVP conditions:



```text

local filesystem storage

local schema validation

local example generation

local hash computation

local chain verification

local policy placeholder hash

local reviewer identity model

no external custody

no external timestamp anchor

no production key management

no third-party audit

```



\---



\## What Closes Each Gap



| Gap                         | Closes With                                                                |

| --------------------------- | -------------------------------------------------------------------------- |

| WAL / envelope durability   | S3, blob storage, or append-only storage adapter                           |

| Reviewer identity           | OIDC / SSO-backed reviewer identity                                        |

| Key management              | KMS-backed HMAC signing and key rotation                                   |

| Independent custody         | External log sink or third-party audit store                               |

| External timestamping       | Merkle epoch roots with timestamp authority or public anchor               |

| Third-party validation      | Independent reproducibility run                                            |

| Agent-framework integration | SDK adapters for MCP, OpenAI Agents SDK, LangGraph, AutoGen, or equivalent |

| Runtime-to-record bridge    | Promotion Contract v0.1 and promoter tool                                  |

| Independent proof           | verify\_envelope\_chain.py with mutation detection                           |

| Public protocol maturity    | External implementers and stable schema versioning                         |



\---



\## Current GO / NO-GO Boundary



The project should not publish strong claims until the following passes:



```powershell

python tools/promote\_to\_envelope.py wal/ollama-events.jsonl -o envelopes.json --verify

python tools/verify\_envelope\_chain.py envelopes.json --mutate --verbose

```



Required mutation-detection output:



```text

proposed\_action mutation:           DETECTED

normalized\_action mutation:         DETECTED

decision mutation:                  DETECTED

previous\_record\_hash mutation:      DETECTED

record\_hash mutation:               DETECTED

classification\_confidence mutation: DETECTED

consequence\_class mutation:         DETECTED

execution\_status mutation:          DETECTED

```



If any mutation survives:



```text

NO COMMIT

NO TAG

NO PUBLIC CLAIM

```



\---



\## Acceptable Public Claim Today



Acceptable:



> This repository defines a local reference architecture for governed consequence routing in agentic systems.



Acceptable:



> Decision Envelope v0.1 records proposed AI-agent consequences, policy decisions, evidence state, review state, execution boundaries, outcomes, and hash-chain linkage.



Acceptable:



> The current implementation demonstrates local schema validation and hash-linked example records.



Not acceptable yet:



> This system solves AI governance.



Not acceptable yet:



> This system is production-ready.



Not acceptable yet:



> This system is legally admissible by default.



Not acceptable yet:



> This system replaces AI GRC platforms.



\---



\## Final Boundary



The current project is strong because it makes its proof boundary explicit.



The immediate build is not a full governance platform.



It is the inspectable core:



```text

decision\_envelope.v0.1

\+

Promotion Contract v0.1

\+

Independent Envelope Verifier

\+

real WAL proof

```



That is enough for the clean build.



