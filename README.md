# Governed Consequence Routing

> The model reasons. The policy decides. The record proves.

This repository is a reference implementation for governed consequence routing in agentic systems.

The core thesis is:

> The unit of governance in an agentic system is the proposed consequence, not the tool call.

A tool call is a mechanism. A proposed consequence is what may affect a system, organization, person, policy, claim, release, or external state.

This project defines an inspectable governance architecture for recording and verifying proposed AI-agent consequences through policy, evidence, authority, execution boundaries, and tamper-evident records.

## Core Architecture

```text
Agent / Gateway / MCP Proxy
        ↓
governance_event.v0.1
        ↓
Promotion Contract v0.1
        ↓
decision_envelope.v0.1
        ↓
Envelope Verifier
        ↓
Trust Receipt / Audit Export / External Review
```

## Core Statements

1. The unit of governance in an agentic system is the proposed consequence, not the tool call.

2. DRF/OMTIR composes policy-bound authorization, evidence-linked claim admission, state-witness approval binding, and hash-chained audit records at the agentic decision boundary.

3. Their logs explain execution. Our envelope adjudicates authority.

4. The model reasons. The policy decides. The record proves.

## Initial Public Artifacts

This repository will publish:

* `decision_envelope.v0.1`
* `Promotion Contract v0.1`
* independent envelope verification
* proof-boundary documentation
* valid example envelopes with real hashes
* runtime-to-envelope promotion tools

## Proof Boundary

This project does not claim to solve all of AI governance.

It demonstrates a local, inspectable architecture for governed consequence routing in agentic systems.

Production durability, external custody, independent notarization, SSO-backed reviewer identity, and broad third-party validation remain future proof-boundary items.
