# Governed Consequence Routing v0.6 — Verification Receipt

## Proof Sentence

v0.6 proves that a portable GCR bundle can be independently verified and that the verification run can be recorded as a durable local receipt.

## Proof Chain

```text
verification receipt
        ↕
portable verification bundle
        ↕
decision envelope
        ↕
approval token ↔ reviewer authority manifest
        ↕
evidence manifest ↔ evidence items
```

## What the Verification Receipt Is

A verification receipt is a durable local record of a verification run over a portable GCR bundle.

It records that a specific verifier, under a specific verifier version and proof boundary, checked a specific bundle and produced a PASS or FAIL result.

The receipt is a governance-record object. It does not replace the bundle. It attests to the verification run performed over the bundle.

## What the Receipt Records

A v0.6 verification receipt records:

- receipt identifier
- receipt schema version
- creation timestamp
- verifier name
- verifier version
- verification tool
- verification command
- bundle identifier
- bundle hash
- bundle type
- proposal identifier
- bundle path or subject
- schema hashes checked
- artifact hashes checked
- checks performed
- per-check verification results
- overall PASS or FAIL status
- failure reasons
- proof boundary
- receipt hash

## Design Rule

The receipt attests to a verification run.

It does not re-authorize the original action.

It does not replace the bundle.

It does not create legal or compliance status.

A verification receipt is evidence of verification, not evidence of correctness.

## What v0.6 Adds

v0.5 proved that a governed AI decision could be exported into a portable verification bundle.

v0.6 adds a second record layer: the verifier can now emit a durable receipt after checking that bundle.

This means the record chain can show not only the governed decision and its supporting artifacts, but also the fact that a verification run occurred and what that run concluded.

## Local Verification Boundary

v0.6 remains a local reference implementation and developer starter kit.

The verifier checks local bundle structure, schema validity, artifact hashes, schema hashes, binding relationships, verification results, and proof-boundary metadata.

It does not observe external systems, production identity, real-world legal authority, real-world evidence truth, or external custody.

## Non-Claims

v0.6 does not claim:

- production custody
- external notarization
- legal admissibility
- regulatory compliance
- clinical safety
- financial advice suitability
- enterprise compliance
- SSO-backed identity
- production identity
- non-repudiation
- correctness of the underlying AI action
- real-world truth of the evidence
- legal validity of the approval
- safety of the original action

## Verification Commands

Verify the existing v0.5 portable bundle and emit a generated receipt:

```powershell
python .\tools\verify_ledger_bundle.py .\examples\verification_bundle\full_gcr_bundle.v0.5.json --receipt-out .\examples\verification_receipt\verification_receipt.generated.v0.6.json
```

Expected output:

```text
LEDGER BUNDLE VERIFY PASS
```

Verify the generated receipt:

```powershell
python .\tools\verify_verification_receipt.py .\examples\verification_receipt\verification_receipt.generated.v0.6.json
```

Expected output:

```text
VERIFICATION RECEIPT VERIFY PASS
```

Verify the stable fixture receipt:

```powershell
python .\tools\verify_verification_receipt.py .\examples\verification_receipt\verification_receipt.v0.6.json
```

Expected output:

```text
VERIFICATION RECEIPT VERIFY PASS
```

## Stable Fixture

The v0.6 fixture receipt is:

```text
examples/verification_receipt/verification_receipt.v0.6.json
```

Stable fixture receipt hash:

```text
sha256:abd980d2c7ac825522f1caf6466667f9a2a9afb2d2b6c5ce7e73007c30320864
```
