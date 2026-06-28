# Governed Consequence Routing

![CI](https://github.com/vikramlaishram-lang/governed-consequence-routing/actions/workflows/tests.yml/badge.svg)

> The model reasons. The policy decides. The record proves.

Governed Consequence Routing is a local reference implementation for recording and verifying proposed AI-agent consequences through policy, evidence, authority, execution boundaries, and tamper-evident records.

The core thesis:

> The unit of governance in an agentic system is the proposed consequence, not the tool call.

A tool call is a mechanism. A proposed consequence is what may affect a system, organization, person, policy, claim, release, or external state.

## Current Public Proof Status

```text
v0.3:
decision envelope <-> approval token <-> reviewer authority manifest

v0.4:
decision envelope <-> evidence manifest <-> evidence items
```

v0.4 proves that a decision envelope can be bound to a structured evidence manifest whose hash, required evidence, admissibility decision, and envelope linkage are independently verifiable under local reference conditions.

## What This Repository Contains

- Decision envelope schema and examples
- Reviewer authority manifest and approval token schemas
- Evidence manifest schema and release-readiness examples
- Local verifier tools for envelope chains, approval binding, reviewer authority binding, and evidence manifest binding
- Governance boundary documents
- GCR Behavioral Standard v0.1
- Buyer/developer quick start
- Tests for schema validation, hash verification, binding verification, and mutation detection

## Key Entry Points

- [QUICK_START.md](QUICK_START.md)
- [RELEASE_NOTES_v0.4.md](RELEASE_NOTES_v0.4.md)
- [GCR Behavioral Standard v0.1](docs/standard/GCR_BEHAVIORAL_STANDARD_v0.1.md)
- [Evidence Manifest Binding v0.4](docs/governance/evidence-manifest-binding-v0.4.md)
- [Current Proof Boundary](docs/governance/current-proof-boundary.md)
- [Evidence Manifest Binding Verifier](tools/verify_evidence_manifest_binding.py)

## Core Architecture

```text
Generate
  -> classify
  -> evidence-bind
  -> authorize
  -> record
  -> verify
  -> receipt
```

The implementation keeps these proof layers inspectable as local JSON artifacts, schemas, verifier tools, and tests.

## Verify Locally

Install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run the full test suite:

```powershell
python -m pytest -q
```

Current expected result:

```text
90 passed
```

Verify v0.4 evidence manifest binding:

```powershell
python .\tools\verify_evidence_manifest_binding.py `
  --envelope .\examples\evidence_manifest\evidence_bound_decision_envelope.v0.4.json `
  --manifest .\examples\evidence_manifest\manifest.v0.4.json
```

Expected result:

```text
EVIDENCE MANIFEST BINDING VERIFY PASS
```

Verify v0.3 approval binding:

```powershell
python .\tools\verify_decision_envelope_approval_binding.py `
  --envelope .\examples\reviewer_authority\approved_decision_envelope.v0.3.json `
  --token .\examples\reviewer_authority\approval_token.v0.3.json `
  --manifest .\examples\reviewer_authority\manifest.v0.3.json
```

Expected result:

```text
DECISION ENVELOPE APPROVAL BINDING VERIFY PASS
```

## Governance Principles

1. The unit of governance in an agentic system is the proposed consequence, not the tool call.
2. A reviewer name is not authority; valid approval requires a reviewer authority record and an approval token bound to the governed consequence.
3. Model output is not evidence.
4. Model confidence is not evidence.
5. A claim may be generated but not admitted.
6. The envelope records the result; the verifier checks the record.

## Proof Boundary

This project is a local reference implementation and developer starter kit.

It demonstrates local schema validation, local hash recomputation, local reviewer authority binding, local evidence manifest binding, and local verifier behavior.

It does not claim production compliance, production identity, SSO-backed approval, enterprise custody, legal admissibility, clinical safety, financial advice suitability, regulatory compliance, external notarization, or third-party validation.

## Release Notes

- [v0.4 - Evidence Manifest Binding](RELEASE_NOTES_v0.4.md)
- [v0.3 - Reviewer Authority](RELEASE_NOTES_v0.3.md)
- [v0.2 - Custody Hardening](RELEASE_NOTES_v0.2.md)
- [v0.1.1 - Local Ollama Adapter Boundary](RELEASE_NOTES_v0.1.1.md)
- [v0.1 - Initial Decision Envelope Proof](RELEASE_NOTES_v0.1.md)
