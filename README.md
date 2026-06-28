# Governed Consequence Routing

![CI](https://github.com/vikramlaishram-lang/governed-consequence-routing/actions/workflows/tests.yml/badge.svg)

> The model proposes. The policy decides. The record proves.

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

## What This Repository Contains

- Decision envelope schema and examples
- Reviewer authority manifest and approval token schemas
- Evidence manifest schema and release-readiness examples
- Portable verification bundle schema and full GCR bundle example
- Local verifier tools for envelope chains, approval binding, reviewer authority binding, evidence manifest binding, and ledger bundle verification
- Local ledger bundle exporter
- Governance boundary documents
- GCR Behavioral Standard v0.1
- Buyer/developer quick start
- Tests for schema validation, hash verification, binding verification, and mutation detection

## Key Entry Points

- [QUICK_START.md](QUICK_START.md)
- [RELEASE_NOTES_v0.5.md](RELEASE_NOTES_v0.5.md)
- [RELEASE_NOTES_v0.4.md](RELEASE_NOTES_v0.4.md)
- [GCR Behavioral Standard v0.1](docs/standard/GCR_BEHAVIORAL_STANDARD_v0.1.md)
- [Portable Verification Bundle v0.5](docs/governance/portable-verification-bundle-v0.5.md)
- [Evidence Manifest Binding v0.4](docs/governance/evidence-manifest-binding-v0.4.md)
- [Current Proof Boundary](docs/governance/current-proof-boundary.md)
- [Ledger Bundle Exporter](tools/export_ledger_bundle.py)
- [Ledger Bundle Verifier](tools/verify_ledger_bundle.py)
- [Full GCR Bundle Example](examples/verification_bundle/full_gcr_bundle.v0.5.json)
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
107 passed
```

Export v0.5 portable verification bundle:

```powershell
python .\tools\export_ledger_bundle.py `
  --envelope .\examples\evidence_manifest\evidence_bound_decision_envelope.v0.4.json `
  --approval-token .\examples\reviewer_authority\approval_token.v0.3.json `
  --reviewer-manifest .\examples\reviewer_authority\manifest.v0.3.json `
  --evidence-manifest .\examples\evidence_manifest\manifest.v0.4.json `
  --out .\examples\verification_bundle\full_gcr_bundle.v0.5.json `
  --write-hash
```

Expected result:

```text
LEDGER BUNDLE EXPORT PASS
```

Verify v0.5 portable verification bundle:

```powershell
python .\tools\verify_ledger_bundle.py .\examples\verification_bundle\full_gcr_bundle.v0.5.json
```

Expected result:

```text
LEDGER BUNDLE VERIFY PASS
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
6. A governed AI decision should be exportable as a portable bundle for local inspection.
7. The model proposes.
8. The policy decides.
9. The record proves.

## Proof Boundary

This project is a local reference implementation and developer starter kit.

It demonstrates local schema validation, local hash recomputation, local reviewer authority binding, local evidence manifest binding, portable verification bundle export, portable verification bundle verification, and local verifier behavior.

It does not claim production custody, external notarization, legal admissibility, regulatory compliance, clinical safety, financial advice suitability, enterprise compliance, or non-repudiation.

## Release Notes

- [v0.5 - Portable Verification Bundle](RELEASE_NOTES_v0.5.md)
- [v0.4 - Evidence Manifest Binding](RELEASE_NOTES_v0.4.md)
- [v0.3 - Reviewer Authority](RELEASE_NOTES_v0.3.md)
- [v0.2 - Custody Hardening](RELEASE_NOTES_v0.2.md)
- [v0.1.1 - Local Ollama Adapter Boundary](RELEASE_NOTES_v0.1.1.md)
- [v0.1 - Initial Decision Envelope Proof](RELEASE_NOTES_v0.1.md)
