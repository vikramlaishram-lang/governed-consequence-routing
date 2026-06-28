# Governed Consequence Routing — AI Agent Approval Record Starter Kit

This starter kit is a local reference implementation for creating and verifying AI agent approval records.

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
78 passed
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

## Proof Boundary

Governed Consequence Routing — AI Agent Approval Record Starter Kit is a local reference implementation and developer starter kit.

It does not claim production identity, SSO-backed approval, legal signature validity, enterprise compliance, legal admissibility, clinical safety, financial advice suitability, or regulatory compliance.
