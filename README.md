# Governed Consequence Routing

![CI](https://github.com/vikramlaishram-lang/governed-consequence-routing/actions/workflows/tests.yml/badge.svg)

> The model reasons. The policy decides. The record proves.

This repository is a local reference implementation for governed consequence routing in agentic systems.

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

## Published Artifacts

This repository currently includes:

* `schemas/decision_envelope_v0.1.schema.json`
* valid example decision envelopes with recomputable hashes
* `docs/governance/promotion-contract-v0.1.md`
* `docs/governance/decision-envelope-v0.1.md`
* `docs/governance/current-proof-boundary.md`
* `tools/promote_to_envelope.py`
* `tools/verify_envelope_chain.py`
* governance-event fixture input
* schema, example, promoter, verifier, and mutation-detection tests
* GitHub Actions workflow for CI verification

## Proof Status

This repository demonstrates:

* promotion from governance events into decision envelopes
* JSON Schema validation of `decision_envelope.v0.1`
* recomputation of proposal, normalized-action, and record hashes
* hash-chain verification across decision envelopes
* constitutional invariant checks
* mutation-tested detection of envelope tampering
* CI verification through GitHub Actions

Current proof tags:

* `promotion-contract-v0.1`
* `ci-verified-promotion-contract-v0.1`

## Proof Boundary

This project does not claim to solve all of AI governance.

It demonstrates a local, inspectable architecture for governed consequence routing in agentic systems.

This repository does not claim production readiness, legal admissibility, third-party validation, complete AI governance coverage, external custody, independent notarization, or SSO-backed reviewer identity.

Those remain future proof-boundary items.
