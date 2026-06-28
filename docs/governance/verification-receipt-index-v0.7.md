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

## Public Artifacts

Schema:

```text
schemas/verification_receipt_index_v0.7.schema.json
```

Example:

```text
examples/verification_receipt_index/index.v0.7.json
```

Verifier:

```text
tools/verify_receipt_index.py
```

---

## What The Index Records

The verification receipt index records local membership for verification receipts.

Each receipt entry records:

- receipt identifier
- receipt hash
- bundle identifier
- proposal identifier
- recorded verification status
- verification time
- local receipt path or subject reference

The index also records:

- index identifier
- schema version
- created and updated timestamps
- receipt count
- PASS and FAIL status counts
- latest verification time
- index hash

---

## Proof Distinction

```text
index_hash proves:   the membership of this index has not changed
receipt_hash proves: this specific receipt has not been modified
verifier proves:     the receipt was valid when it was verified
```

The index does not re-verify the receipts it indexes.

The index records receipt membership and the recorded status at the time the receipt was added.

Index integrity is not the same as receipt validity.

Receipt validity is not the same as real-world correctness.

---

## What `index_hash` Proves

The `index_hash` is computed over canonical JSON with `index_hash` excluded.

It proves that the indexed membership and recorded index metadata have not changed since the hash was computed.

It does not prove that the referenced receipts are currently valid.

It does not prove that the underlying bundle, approval, evidence, or AI action is correct.

---

## What `receipt_hash` Proves

A `receipt_hash` proves that a specific verification receipt has not been modified relative to its recorded hash.

It does not prove:

- the real-world correctness of the underlying AI action
- the real-world truth of the evidence
- legal validity of the approval
- safety of the original action
- that index membership proves receipt validity
- that receipt validity proves real-world correctness

---

## What The Verifier Proves

The receipt index verifier checks:

- receipt index schema validity
- index hash correctness
- receipt count consistency
- PASS and FAIL status count consistency
- latest verification time consistency
- mutation detection for receipt entry fields when `--mutate` is used

The verifier proves that the index is structurally valid and internally consistent under local reference conditions.

It does not re-run the receipt verifier for each indexed receipt.

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

Verify the indexed PASS receipt:

```powershell
python .\tools\verify_verification_receipt.py .\examples\verification_receipt\verification_receipt.v0.6.json
```

Expected:

```text
VERIFICATION RECEIPT VERIFY PASS
```

Verify the deterministic local FAIL receipt fixture:

```powershell
python .\tools\verify_verification_receipt.py .\examples\verification_receipt\verification_receipt.fail.v0.7.json
```

Expected:

```text
VERIFICATION RECEIPT VERIFY PASS
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

## Local Verification Boundary

v0.7 is a local reference implementation and developer starter kit proof layer.

It uses local schemas, local examples, local hash computation, local verification tools, and local test fixtures.

The index can show that receipt membership has not changed. It cannot show that external systems, real-world claims, legal authority, or production custody are valid.

---

## Non-Claims

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

---

## Acceptable Public Claims

Acceptable:

> v0.7 adds a local verification receipt index whose membership and integrity can be independently verified.

Acceptable:

> The receipt index records receipt membership and recorded PASS/FAIL status under local reference conditions.

Acceptable:

> The index hash can detect changes to indexed receipt membership or recorded index metadata.

Not acceptable:

> The index re-verifies every receipt.

Not acceptable:

> Index membership proves a receipt is currently valid.

Not acceptable:

> Receipt validity proves the underlying AI action was correct, safe, compliant, or legally approved.

Not acceptable:

> v0.7 provides production custody, external notarization, legal admissibility, regulatory compliance, clinical safety, financial advice suitability, enterprise compliance, SSO-backed identity, production identity, or non-repudiation.
