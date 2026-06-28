# Governed Consequence Routing v0.5 — Portable Verification Bundle

## Release Summary

v0.5 adds portable verification bundle export and verification for Governed Consequence Routing.

v0.3 proved local reviewer authority binding:

```text
decision envelope <-> approval token <-> reviewer authority manifest
```

v0.4 proved local evidence manifest binding:

```text
decision envelope <-> evidence manifest <-> evidence items
```

v0.5 packages those proof objects into a portable verification bundle:

```text
portable verification bundle
        <->
decision envelope
        <->
approval token <-> reviewer authority manifest
        <->
evidence manifest <-> evidence items
```

v0.5 proves that a governed AI decision can be exported into a portable verification bundle whose included artifacts, hashes, verification results, and proof-boundary metadata are independently inspectable and locally verifiable.

## What Changed

Added the v0.5 governance boundary document:

```text
docs/governance/portable-verification-bundle-v0.5.md
```

Added the portable verification bundle schema:

```text
schemas/verification_bundle_v0.5.schema.json
```

Added a full GCR bundle example:

```text
examples/verification_bundle/full_gcr_bundle.v0.5.json
```

Added the ledger bundle exporter:

```text
tools/export_ledger_bundle.py
```

Added the ledger bundle verifier:

```text
tools/verify_ledger_bundle.py
```

Added tests for schema validation, bundle export, bundle verification, hash mismatch detection, embedded artifact tampering, schema hash mismatch, recorded verification-result failure, and bundle-subject mismatch:

```text
tests/test_verification_bundle_schema.py
tests/test_export_ledger_bundle.py
tests/test_verify_ledger_bundle.py
```

## Governance Principle

A vendor-only dashboard is not independent verification.

A private database record is not a portable proof bundle.

A bundle is not a legal certificate.

A bundle is not external notarization.

A bundle packages local verification material for independent inspection.

The source of truth remains the included structured artifacts and their hashes, not the human-readable summary.

## How to Verify

Run the full test suite:

```powershell
python -m pytest -q
```

Expected result:

```text
107 passed
```

Export the v0.5 bundle:

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

Verify the v0.5 bundle:

```powershell
python .\tools\verify_ledger_bundle.py .\examples\verification_bundle\full_gcr_bundle.v0.5.json
```

Expected result:

```text
LEDGER BUNDLE VERIFY PASS
```

## What v0.5 Proves

v0.5 proves local portable-bundle export and verification behavior.

It verifies:

```text
verification bundle schema validity
bundle_hash integrity
embedded decision envelope artifact hash
embedded approval token artifact hash
embedded reviewer authority manifest artifact hash
embedded evidence manifest artifact hash
decision envelope schema hash
approval token schema hash
reviewer authority manifest schema hash
evidence manifest schema hash
approval token verification
reviewer authority binding verification
evidence manifest binding verification
bundle subject linkage
recorded verification results are PASS
```

## What v0.5 Does Not Prove

v0.5 remains a local reference implementation and developer starter kit.

It does not claim:

```text
production custody
external notarization
legal admissibility
regulatory compliance
clinical safety
financial advice suitability
enterprise compliance
non-repudiation
truth of evidence source content
```

## Correct Public Claim

```text
v0.5 adds local portable verification bundle export and verification for governed AI decision artifacts, including embedded proof objects, artifact hashes, schema hashes, verification results, and proof-boundary metadata.
```

## Incorrect Claims

Do not claim:

```text
production custody
external notarization
legal certificate
legally admissible evidence records
regulatory compliance
clinical workflow safety
financial advice suitability
enterprise compliance
non-repudiation
```
