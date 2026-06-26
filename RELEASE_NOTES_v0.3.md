\# Governed Consequence Routing v0.3 — Reviewer Authority



\## Release Summary



v0.3 introduces local reviewer authority governance for Governed Consequence Routing.



v0.1 proved that governance events can be promoted into decision envelopes, schema-validated, hash-linked, independently verified, and mutation-tested.



v0.2 strengthened custody through verification bundles, concise summaries, chain-head and schema-hash reporting, and optional local HMAC-backed verification.



v0.3 adds reviewer authority structure and binding.



The core shift is:



```text

v0.1: The envelope chain verifies.

v0.2: The verification itself becomes a custody artifact.

v0.3: Reviewer approval must be bound to valid authority.

```



\## Included Tags



```text

v0.3.0-reviewer-authority-boundary

v0.3.1-reviewer-authority-manifest-schema

v0.3.2-approval-token-schema

v0.3.3-approval-token-hash-verifier

v0.3.4-reviewer-authority-binding-verifier

v0.3.5-decision-envelope-approval-binding-verifier

```



\## What Changed



\### v0.3.0 — Reviewer Authority Boundary



Added the reviewer authority boundary document:



```text

docs/governance/reviewer-authority-v0.3.md

```



This defines the v0.3 governance question:



```text

Who approved the consequence, under what authority, and was that authority valid at the time?

```



It also establishes the boundary that v0.3 is a local reviewer-authority demonstration, not identity proof, SSO integration, legal signature validity, or production access control.



\### v0.3.1 — Reviewer Authority Manifest Schema



Added a reviewer authority manifest schema and fixture:



```text

schemas/reviewer\_authority\_manifest\_v0.3.schema.json

examples/reviewer\_authority/manifest.v0.3.json

tests/test\_reviewer\_authority\_manifest\_schema.py

```



The reviewer authority manifest records:



```text

reviewer\_authority\_id

reviewer\_identity\_ref

reviewer\_role

authority\_scope

valid\_from

valid\_until

issuer

issuer\_authority\_id

authority\_status

authority\_record\_hash

```



This prevents the system from treating a bare reviewer string as sufficient authority.



\### v0.3.2 — Approval Token Schema



Added an approval token schema and fixture:



```text

schemas/approval\_token\_v0.3.schema.json

examples/reviewer\_authority/approval\_token.v0.3.json

tests/test\_approval\_token\_schema.py

```



The approval token records:



```text

approval\_token\_id

reviewer\_authority\_id

proposal\_id

proposal\_hash

normalized\_action\_hash

policy\_hash

consequence\_classification

approval\_scope

approval\_decision

approval\_reason

issued\_at

expires\_at

authority\_record\_hash

approval\_token\_hash

```



This makes reviewer approval explicit and inspectable.



\### v0.3.3 — Approval Token Hash Verifier



Added a local approval token verifier:



```text

tools/verify\_approval\_token.py

tests/test\_approval\_token\_hash\_verifier.py

```



The verifier checks:



```text

approval token schema validity

approval\_token\_hash integrity

hash mismatch detection

missing input handling

\--write-hash repair path for local fixture generation

```



This means the approval token can be verified before it is trusted by any higher-level binding logic.



\### v0.3.4 — Reviewer Authority Binding Verifier



Added a reviewer authority binding verifier:



```text

tools/verify\_reviewer\_authority\_binding.py

tests/test\_reviewer\_authority\_binding\_verifier.py

```



The verifier checks the relationship between:



```text

reviewer authority manifest

&#x20;       ↕

approval token

```



It verifies:



```text

reviewer\_authority\_id match

authority\_record\_hash match

authority\_status is ACTIVE

approval issued\_at is within authority valid\_from / valid\_until

approval consequence class is authorized

approval decision is authorized

approval token hash integrity

```



\### v0.3.5 — Decision Envelope Approval Binding Verifier



Added a decision-envelope approval binding verifier:



```text

tools/verify\_decision\_envelope\_approval\_binding.py

examples/reviewer\_authority/approved\_decision\_envelope.v0.3.json

tests/test\_decision\_envelope\_approval\_binding\_verifier.py

```



The verifier checks the full local reviewer-authority chain:



```text

decision envelope

&#x20;       ↕

approval token

&#x20;       ↕

reviewer authority manifest

```



It verifies:



```text

envelope reviewer\_authority\_id matches approval token

envelope proposal\_id matches approval token

envelope proposal\_hash matches approval token

envelope normalized\_action\_hash matches approval token

envelope policy\_hash matches approval token

approval token authority binding passes

approval token scope covers envelope consequence class

approval token scope covers envelope decision path

envelope review\_status is APPROVED

envelope created\_at is within approval token issued\_at / expires\_at

```



This is the main v0.3 proof surface.



Reviewer approval is no longer just a string on the envelope. It is bound to an approval token, and the approval token is bound to a reviewer authority manifest.



\## How to Verify



Run the full test suite:



```powershell

python -m pytest -q

```



Expected result:



```text

78 passed

```



Verify the approval token:



```powershell

python .\\tools\\verify\_approval\_token.py .\\examples\\reviewer\_authority\\approval\_token.v0.3.json

```



Expected result:



```text

APPROVAL TOKEN VERIFY PASS

```



Verify reviewer authority binding:



```powershell

python .\\tools\\verify\_reviewer\_authority\_binding.py `

&#x20; --manifest .\\examples\\reviewer\_authority\\manifest.v0.3.json `

&#x20; --token .\\examples\\reviewer\_authority\\approval\_token.v0.3.json

```



Expected result:



```text

REVIEWER AUTHORITY BINDING VERIFY PASS

```



Verify decision-envelope approval binding:



```powershell

python .\\tools\\verify\_decision\_envelope\_approval\_binding.py `

&#x20; --envelope .\\examples\\reviewer\_authority\\approved\_decision\_envelope.v0.3.json `

&#x20; --token .\\examples\\reviewer\_authority\\approval\_token.v0.3.json `

&#x20; --manifest .\\examples\\reviewer\_authority\\manifest.v0.3.json

```



Expected result:



```text

DECISION ENVELOPE APPROVAL BINDING VERIFY PASS

```



\## What v0.3 Adds



v0.3 adds a local reviewer authority model.



It makes approval scope, authority validity, approval token integrity, and envelope approval binding explicit and testable.



It demonstrates that a decision envelope requiring review can be checked against a specific approval token and a specific authority record.



\## What v0.3 Does Not Add



v0.3 does not provide:



```text

production reviewer identity

SSO-backed reviewer authentication

OIDC verification

legal signature validity

HR system integration

production access control

enterprise approval workflow

external authority verification

non-repudiation

legal admissibility

```



\## Correct Public Claim



A correct public claim for v0.3 is:



```text

v0.3 introduces local reviewer authority checks for governed decision envelopes, including reviewer authority manifests, approval tokens, approval token hash verification, authority-token binding, and decision-envelope approval binding.

```



A correct boundary claim is:



```text

v0.3 remains a local reference implementation. It demonstrates reviewer authority binding but does not claim production identity, SSO-backed approval, legal signature validity, or enterprise approval readiness.

```



\## Incorrect Claims



Do not claim:



```text

production reviewer identity

legal signature validity

enterprise approval readiness

SSO-backed reviewer authentication

external authority verification

non-repudiation

legally admissible approval records

```



\## Governance Principle



A reviewer name is not authority.



A reviewer identity string is not authority.



A human approval is not automatically valid.



A valid approval requires a reviewer authority record and an approval token bound to the governed consequence.



The model may propose.



The reviewer may approve only within granted scope.



The policy decides whether that approval is admissible.



The envelope records the result.



The verifier checks the record.



