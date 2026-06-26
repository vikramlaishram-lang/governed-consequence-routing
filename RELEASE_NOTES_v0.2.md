\# Governed Consequence Routing v0.2 — Custody Hardening



\## Release Summary



v0.2 strengthens the custody and verification surface for Governed Consequence Routing.



v0.1 proved that governance events can be promoted into decision envelopes, schema-validated, hash-linked, independently verified, and mutation-tested.



v0.2 adds custody hardening around that verification process.



The core shift is:



```text

v0.1: The envelope chain verifies.

v0.2: The verification itself becomes a portable custody artifact.

```



\## Included Tags



```text

v0.2.0-custody-boundary

v0.2.1-verification-bundle

v0.2.2-verification-summary

v0.2.3-hmac-custody-demo

v0.2.4-hmac-custody-boundary-docs

```



\## What Changed



\### v0.2.0 — Custody Boundary



Added the v0.2 custody-hardening boundary document:



```text

docs/governance/custody-hardening-v0.2.md

```



This document defines the custody goal, proof boundary, verification-bundle concept, and explicit non-claims.



\### v0.2.1 — Verification Bundle Export



Added a verification bundle exporter:



```text

tools/export\_verification\_bundle.py

```



The bundle records:



```text

bundle\_version

created\_at

verifier\_version

schema\_path

schema\_hash

envelope\_source

envelope\_source\_hash

envelope\_count

first\_record\_hash

final\_record\_hash

tamper\_evidence\_modes

key\_ids

verification\_result

mutation\_check\_result

detected\_mutation\_classes

proof\_boundary

verifier\_stdout

verifier\_stderr

```



This creates a portable local custody artifact for independent inspection.



\### v0.2.2 — Verification Summary Export



Added concise verification summaries through:



```text

\--summary-out verification\_summary.json

```



The summary records the proof state without including full verifier stdout or stderr.



It includes:



```text

chain\_head

schema\_hash

envelope\_count

envelope\_source\_hash

tamper\_evidence\_modes

key\_ids

verification\_result

mutation\_check\_result

detected\_mutation\_classes

proof\_boundary

```



This makes the custody state easier to inspect.



\### v0.2.3 — HMAC Custody Demo Mode



Added optional local HMAC-backed record-hash verification.



Supported tamper-evidence modes are now:



```text

UNKEYED\_HASH\_CHAIN

HMAC\_SHA256\_V1

```



`UNKEYED\_HASH\_CHAIN` remains the default.



`HMAC\_SHA256\_V1` is optional and requires:



```text

key\_id

GCR\_HMAC\_KEY

```



The optional environment variable `GCR\_HMAC\_KEY\_ID` may be used to require that the runtime key identifier matches the envelope `key\_id`.



The verifier fails when:



```text

HMAC\_SHA256\_V1 is declared but key\_id is missing.

HMAC\_SHA256\_V1 is declared but GCR\_HMAC\_KEY is missing.

GCR\_HMAC\_KEY\_ID is set and does not match envelope key\_id.

The recomputed HMAC record hash does not match record\_hash.

The tamper\_evidence\_mode is unknown.

```



\### v0.2.4 — HMAC Custody Boundary Docs



Added the HMAC custody demo boundary document:



```text

docs/governance/hmac-custody-demo-boundary-v0.2.4.md

```



This document clarifies that HMAC mode is a local custody demonstration, not production custody.



\## How to Verify



Run the test suite:



```powershell

python -m pytest -q

```



Expected result:



```text

41 passed

```



Verify the existing example chain:



```powershell

python .\\tools\\verify\_envelope\_chain.py .\\examples --mutate --verbose

```



Expected result:



```text

VERIFIER PASS: 3 envelope(s) valid

MUTATION CHECK PASS: all mutations detected

```



Export a full verification bundle and concise summary:



```powershell

python .\\tools\\export\_verification\_bundle.py .\\examples --mutate --bundle-out verification\_bundle.json --summary-out verification\_summary.json

```



Expected result:



```text

VERIFICATION BUNDLE PASS

VERIFICATION SUMMARY PASS

```



\## HMAC Demo Boundary



HMAC mode is intentionally limited.



It demonstrates that a decision envelope can be verified against a local secret that is not stored inside the envelope.



It does not provide production key management.



It does not provide external notarization.



It does not provide legal admissibility.



It does not provide third-party validation.



It does not provide non-repudiation.



It does not prove reviewer identity.



It does not make the system enterprise custody-ready.



\## Secret Handling Rule



The repository must not contain real HMAC secrets.



Demo keys may appear only inside tests.



Only `key\_id` may appear in envelopes, bundles, summaries, or logs.



`GCR\_HMAC\_KEY` must never be committed, printed, bundled, logged, or published.



\## Correct Public Claim



A correct public claim for v0.2 is:



```text

v0.2 adds custody hardening for Governed Consequence Routing through portable verification bundles, concise verification summaries, chain-head and schema-hash reporting, and optional local HMAC-backed verification using environment-provided keys.

```



A correct boundary claim is:



```text

v0.2 remains a local reference implementation and custody demonstration. It does not claim production custody, legal admissibility, external notarization, or third-party validation.

```



\## Incorrect Claims



Do not claim:



```text

production-ready custody

legal admissibility

external notarization

non-repudiation

secure key management

third-party validation

enterprise audit readiness

identity-backed reviewer custody

```



\## Governance Principle



The custody layer strengthens the record.



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



