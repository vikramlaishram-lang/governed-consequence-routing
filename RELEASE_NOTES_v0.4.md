# Governed Consequence Routing v0.4 — Evidence Manifest Binding

## Release Summary

v0.4 adds evidence manifest binding for Governed Consequence Routing.

v0.3 proved local reviewer authority binding:

```text
decision envelope <-> approval token <-> reviewer authority manifest
```

v0.4 adds local evidence manifest binding:

```text
decision envelope <-> evidence manifest <-> evidence items
```

v0.4 proves that a decision envelope can be bound to a structured evidence manifest whose hash, required evidence, admissibility decision, and envelope linkage are independently verifiable under local reference conditions.

## What Changed

Added the v0.4 governance boundary document:

```text
docs/governance/evidence-manifest-binding-v0.4.md
```

Added the evidence manifest schema:

```text
schemas/evidence_manifest_v0.4.schema.json
```

Added release-readiness evidence manifest examples:

```text
examples/evidence_manifest/manifest.v0.4.json
examples/evidence_manifest/evidence_bound_decision_envelope.v0.4.json
```

Added the evidence manifest binding verifier:

```text
tools/verify_evidence_manifest_binding.py
```

Added tests for schema validation, hash verification, and decision-envelope binding behavior:

```text
tests/test_evidence_manifest_schema.py
tests/test_evidence_manifest_hash_verifier.py
tests/test_decision_envelope_evidence_binding_verifier.py
```

## Governance Principle

Model output is not evidence.

Model confidence is not evidence.

A claim may be generated but not admitted.

Evidence must be external to the model output or explicitly marked as model-originated.

The evidence manifest records what sources were used, their hashes, their admissibility status, and their relationship to the proposal.

## How to Verify

Run the full test suite:

```powershell
python -m pytest -q
```

Expected result:

```text
90 passed
```

Verify evidence manifest binding:

```powershell
python .\tools\verify_evidence_manifest_binding.py `
  --envelope .\examples\evidence_manifest\evidence_bound_decision_envelope.v0.4.json `
  --manifest .\examples\evidence_manifest\manifest.v0.4.json
```

Expected result:

```text
EVIDENCE MANIFEST BINDING VERIFY PASS
```

## What v0.4 Proves

v0.4 proves local evidence-binding structure and verification behavior.

It verifies:

```text
evidence manifest schema validity
evidence_manifest_hash integrity
decision envelope schema validity
envelope evidence_manifest_hash linkage
proposal_id linkage
proposal_hash linkage
normalized_action_hash linkage
policy_hash linkage
minimum admitted evidence count
required admitted evidence types
SUFFICIENT admissibility decision
```

## What v0.4 Does Not Prove

v0.4 remains a local reference implementation and developer starter kit.

It does not claim:

```text
production compliance
legal admissibility
clinical safety
financial advice suitability
enterprise custody
SSO-backed identity
external notarization
third-party validation
truth of evidence source content
```

## Correct Public Claim

```text
v0.4 adds local evidence manifest binding for governed decision envelopes, including evidence manifest schema validation, manifest hash verification, admitted evidence requirement checks, and decision-envelope evidence linkage verification.
```

## Incorrect Claims

Do not claim:

```text
production compliance
legally admissible evidence records
clinical workflow safety
financial advice suitability
enterprise custody
independent evidence truth verification
```
