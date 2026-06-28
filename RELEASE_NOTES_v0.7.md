# Governed Consequence Routing v0.7 — Verification Receipt Index

v0.7 proves that multiple verification receipts can be collected into a local receipt index whose membership and integrity are independently verifiable.

---

## Proof Chain

```text
verification receipt index
        ↕
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

---

## What v0.7 Adds

v0.7 adds a Verification Receipt Index proof layer.

The index collects multiple verification receipt records into a local index with:

- explicit receipt membership
- recorded PASS and FAIL status counts
- latest verification time
- canonical index hash
- standalone receipt index verifier
- mutation checks for receipt entry fields

The index does not re-verify the receipts it indexes.

It records receipt membership and the recorded status at the time the receipt was added.

---

## Included Files

```text
schemas/verification_receipt_index_v0.7.schema.json
examples/verification_receipt_index/index.v0.7.json
examples/verification_receipt/verification_receipt.fail.v0.7.json
tools/verify_receipt_index.py
tests/test_receipt_index.py
docs/governance/verification-receipt-index-v0.7.md
RELEASE_NOTES_v0.7.md
```

---

## Verification Commands

Validate the schema JSON:

```powershell
python -m json.tool schemas/verification_receipt_index_v0.7.schema.json > $null
Write-Host "schema: OK"
```

Verify the receipt index:

```powershell
python tools/verify_receipt_index.py examples/verification_receipt_index/index.v0.7.json
```

Expected:

```text
RECEIPT INDEX VERIFY PASS
```

Run mutation checks:

```powershell
python tools/verify_receipt_index.py examples/verification_receipt_index/index.v0.7.json --mutate
```

Expected:

```text
MUTATION CHECK PASS
```

Verify the indexed receipts:

```powershell
python .\tools\verify_verification_receipt.py .\examples\verification_receipt\verification_receipt.v0.6.json
python .\tools\verify_verification_receipt.py .\examples\verification_receipt\verification_receipt.fail.v0.7.json
```

Expected:

```text
VERIFICATION RECEIPT VERIFY PASS
VERIFICATION RECEIPT VERIFY PASS
```

Run the full test suite:

```powershell
python -m pytest -q
```

Expected:

```text
127 passed
```

---

## Stable Fixture Values

```text
index_id: 77777777-7777-4777-8777-777777777777
receipt_count: 2
status_counts: PASS 1, FAIL 1
index_hash: sha256:ec4ab3dfb958df29c05da0214999031fde663496f55442681ca866fd95337b59
v0.6 PASS receipt_hash: sha256:abd980d2c7ac825522f1caf6466667f9a2a9afb2d2b6c5ce7e73007c30320864
v0.7 FAIL receipt_hash: sha256:f9214ffb70f8636134e0dccb16735576a37e7085ff34f216b0207e04b5828722
```

---

## Proof Distinction

```text
index_hash proves:   the membership of this index has not changed
receipt_hash proves: this specific receipt has not been modified
verifier proves:     the receipt was valid when it was verified
```

Index integrity is not the same as receipt validity.

Receipt validity is not the same as real-world correctness.

---

## Boundary / Non-Claims

v0.7 is a local reference implementation and developer starter kit proof layer.

v0.7 does not claim:

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
- that index membership proves receipt validity
- that receipt validity proves real-world correctness
