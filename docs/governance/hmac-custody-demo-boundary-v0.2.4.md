\# HMAC Custody Demo Boundary v0.2.4



\## Purpose



v0.2.3 introduced optional HMAC-backed verification for decision-envelope record hashes.



This document defines the boundary of that feature.



The feature is a local custody demonstration.



It is not production key management, legal admissibility, external notarization, non-repudiation, or third-party validation.



\## Modes



Governed Consequence Routing now supports two tamper-evidence modes:



```text

UNKEYED\_HASH\_CHAIN

HMAC\_SHA256\_V1

```



`UNKEYED\_HASH\_CHAIN` remains the default mode.



`HMAC\_SHA256\_V1` is optional and must be explicitly declared by the envelope.



\## UNKEYED\_HASH\_CHAIN



In unkeyed mode, the verifier recomputes the record hash from the canonical decision envelope payload after removing the `record\_hash` field.



This mode proves local tamper evidence.



It does not prove custody of a secret.



It does not prove who generated the record.



It does not provide cryptographic authentication beyond hash-chain consistency.



\## HMAC\_SHA256\_V1



In HMAC mode, the verifier recomputes the record hash using HMAC-SHA256 over the canonical decision envelope payload after removing the `record\_hash` field.



The verifier requires:



```text

tamper\_evidence\_mode = HMAC\_SHA256\_V1

key\_id

GCR\_HMAC\_KEY

```



The optional environment variable `GCR\_HMAC\_KEY\_ID` may be used to require that the runtime key identifier matches the envelope `key\_id`.



\## Environment Variables



HMAC verification uses environment-provided secrets.



```text

GCR\_HMAC\_KEY

GCR\_HMAC\_KEY\_ID

```



`GCR\_HMAC\_KEY` contains the local HMAC secret.



`GCR\_HMAC\_KEY\_ID` contains the expected key identifier.



Only `key\_id` may appear in envelopes, summaries, bundles, or logs.



The secret itself must never be committed, printed, bundled, logged, or published.



\## Failure Conditions



The verifier must fail if:



```text

HMAC\_SHA256\_V1 is declared but key\_id is missing.

HMAC\_SHA256\_V1 is declared but GCR\_HMAC\_KEY is missing.

GCR\_HMAC\_KEY\_ID is set and does not match envelope key\_id.

The recomputed HMAC record hash does not match record\_hash.

The tamper\_evidence\_mode is unknown.

```



These failures are expected custody behavior.



They prevent an HMAC-backed envelope from silently degrading into an unkeyed hash-chain check.



\## What HMAC Adds



HMAC mode adds a local keyed integrity check.



It demonstrates that a decision envelope can be verified against a secret not stored in the envelope itself.



It strengthens the custody story for local demonstrations by separating public verification metadata from private verification material.



\## What HMAC Does Not Add



HMAC mode does not provide:



```text

secure key management

hardware-backed custody

external notarization

legal admissibility

third-party validation

non-repudiation

production audit readiness

enterprise custody guarantees

identity proof

reviewer authentication

timestamp authority

```



HMAC mode should not be described as production custody.



It should be described as an optional local custody demonstration.



\## Key Handling Rule



The repository must not contain real HMAC secrets.



Demo keys may appear only in tests.



Demo keys must be clearly treated as test fixtures.



No committed test key may be represented as a production key.



\## Bundle and Summary Behavior



Verification bundles and summaries may record:



```text

tamper\_evidence\_modes

key\_ids

verification\_result

mutation\_check\_result

chain\_head

schema\_hash

proof\_boundary

```



They must not record:



```text

GCR\_HMAC\_KEY

raw HMAC secret

derived secret material

private custody material

```



A bundle or summary may prove that verification succeeded under HMAC mode.



It does not prove that the secret was securely stored, independently controlled, or legally admissible.



\## Governance Boundary



HMAC strengthens the record.



It does not change the authority model.



The core rule remains:



```text

The model may propose.

It may not authorize.

```



Policy decides.



The decision envelope records.



The verifier checks.



The custody artifact explains what was checked.



\## Correct Public Claim



A correct public claim is:



```text

v0.2.3 adds optional local HMAC-backed verification for decision-envelope record hashes using environment-provided keys, while preserving unkeyed hash-chain verification as the default.

```



A correct boundary claim is:



```text

This is a local custody demonstration, not production custody or legal admissibility.

```



\## Incorrect Public Claims



Do not claim:



```text

production-grade custody

legal admissibility

external notarization

non-repudiation

secure key management

third-party validation

enterprise audit readiness

identity-backed reviewer custody

```



\## Status



This document defines the HMAC custody demo boundary for v0.2.4.



