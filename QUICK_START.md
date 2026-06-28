# Governed Consequence Routing — AI Agent Governance Record Starter Kit

This starter kit is a local reference implementation for creating, binding, exporting, and locally verifying approval records around AI-agent actions.

## Proof Ladder

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

## Requirements

- Python 3.11 or newer
- PowerShell on Windows, or an equivalent shell
- `pip`

## Setup

From the package root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run the Test Suite

```powershell
python -m pytest -q
```

Expected result:

```text
107 passed
```

## Verify the Approval Token

```powershell
python .\tools\verify_approval_token.py .\examples\reviewer_authority\approval_token.v0.3.json
```

Expected result:

```text
APPROVAL TOKEN VERIFY PASS
```

## Verify Reviewer Authority Binding

```powershell
python .\tools\verify_reviewer_authority_binding.py --manifest .\examples\reviewer_authority\manifest.v0.3.json --token .\examples\reviewer_authority\approval_token.v0.3.json
```

Expected result:

```text
REVIEWER AUTHORITY BINDING VERIFY PASS
```

## Verify Decision-Envelope Approval Binding

```powershell
python .\tools\verify_decision_envelope_approval_binding.py --envelope .\examples\reviewer_authority\approved_decision_envelope.v0.3.json --token .\examples\reviewer_authority\approval_token.v0.3.json --manifest .\examples\reviewer_authority\manifest.v0.3.json
```

Expected result:

```text
DECISION ENVELOPE APPROVAL BINDING VERIFY PASS
```

## Verify Evidence Manifest Binding

```powershell
python .\tools\verify_evidence_manifest_binding.py --envelope .\examples\evidence_manifest\evidence_bound_decision_envelope.v0.4.json --manifest .\examples\evidence_manifest\manifest.v0.4.json
```

Expected result:

```text
EVIDENCE MANIFEST BINDING VERIFY PASS
```

## Export a Ledger Bundle

```powershell
python .\tools\export_ledger_bundle.py --envelope .\examples\evidence_manifest\evidence_bound_decision_envelope.v0.4.json --approval-token .\examples\reviewer_authority\approval_token.v0.3.json --reviewer-manifest .\examples\reviewer_authority\manifest.v0.3.json --evidence-manifest .\examples\evidence_manifest\manifest.v0.4.json --out .\examples\verification_bundle\full_gcr_bundle.v0.5.json --write-hash
```

Expected result:

```text
LEDGER BUNDLE EXPORT PASS
```

## Verify the Ledger Bundle

```powershell
python .\tools\verify_ledger_bundle.py .\examples\verification_bundle\full_gcr_bundle.v0.5.json
```

Expected result:

```text
LEDGER BUNDLE VERIFY PASS
```

## Proof Boundary

Governed Consequence Routing — AI Agent Governance Record Starter Kit is a local reference implementation and developer starter kit.

It does not claim production custody, external notarization, legal admissibility, regulatory compliance, clinical safety, financial advice suitability, enterprise compliance, SSO-backed identity, production identity, or non-repudiation.
