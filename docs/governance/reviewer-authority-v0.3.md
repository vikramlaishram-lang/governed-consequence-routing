\# Reviewer Authority v0.3



\## Purpose



v0.3 introduces reviewer authority governance for Governed Consequence Routing.



v0.1 proved that proposed consequences can be promoted into decision envelopes and verified.



v0.2 strengthened custody through verification bundles, concise summaries, and optional local HMAC-backed verification.



v0.3 adds the next governance question:



Who approved the consequence, under what authority, and was that authority valid at the time?



\## Core Shift



v0.1 answered:



The envelope chain verifies.



v0.2 answered:



The verification itself can become a custody artifact.



v0.3 begins answering:



The reviewer was authorized to approve this consequence.



\## Authority Principle



A reviewer name is not authority.



A reviewer identity string is not authority.



A human approval is not automatically valid.



A valid approval requires a reviewer authority record.



\## Reviewer Authority Record



A reviewer authority record should describe:



\* reviewer\_authority\_id

\* reviewer identity reference

\* reviewer role

\* authority scope

\* allowed consequence classes

\* allowed decision types

\* valid\_from

\* valid\_until

\* issuer

\* issuer\_authority\_id

\* authority\_record\_hash

\* authority\_status



\## Approval Token



An approval token should bind a reviewer decision to a specific governed consequence.



It should include:



\* approval\_token\_id

\* reviewer\_authority\_id

\* proposal\_id

\* proposal\_hash

\* normalized\_action\_hash

\* policy\_hash

\* consequence\_classification

\* approval\_scope

\* approval\_decision

\* approval\_reason

\* issued\_at

\* expires\_at

\* authority\_record\_hash

\* approval\_token\_hash



\## Required v0.3 Checks



The verifier should eventually be able to check:



\* reviewer\_authority\_id is present when review\_status requires it

\* reviewer authority record exists

\* reviewer authority was valid when approval was issued

\* approval scope covers the consequence class

\* approval scope covers the decision type

\* approval token binds to the same proposal\_hash

\* approval token binds to the same normalized\_action\_hash

\* approval token binds to the same policy\_hash

\* expired approval tokens fail

\* revoked or inactive authority records fail

\* approval token hash mismatch fails



\## Scope Boundary



v0.3 is a local reviewer authority demonstration.



It does not claim:



\* identity proof

\* SSO integration

\* OIDC verification

\* legal signature validity

\* HR system integration

\* production access control

\* enterprise approval workflow

\* external reviewer attestation

\* non-repudiation

\* legal admissibility



\## What v0.3 Adds



v0.3 adds a local model for reviewer authority.



It makes reviewer approval more inspectable.



It prevents a decision envelope from treating a bare reviewer string as sufficient authority.



It creates the foundation for later identity-backed approval workflows.



\## What v0.3 Does Not Add



v0.3 does not prove that the reviewer is a real person.



v0.3 does not prove that the reviewer logged in through an enterprise identity provider.



v0.3 does not prove legal approval.



v0.3 does not make the system production-ready.



v0.3 does not replace access-control systems.



\## Governance Rule



A consequence requiring review may only proceed when the approval is bound to valid reviewer authority.



The model may propose.



The reviewer may approve only within granted scope.



The policy decides whether that approval is admissible.



The envelope records the result.



The verifier checks the record.



\## Correct Public Claim



A correct public claim is:



v0.3 introduces local reviewer authority checks for governed decision envelopes, making approval scope, authority validity, and approval binding explicit and testable.



\## Incorrect Public Claims



Do not claim:



\* production reviewer identity

\* legal signature validity

\* enterprise approval readiness

\* SSO-backed reviewer authentication

\* external authority verification

\* non-repudiation

\* legally admissible approval records



\## Status



This document defines the reviewer authority boundary for v0.3.



