# Decision Envelope v0.1

> The model reasons. The policy decides. The record proves.

`decision_envelope.v0.1` is the canonical governance record for one proposed AI-agent consequence.

It records what was proposed, how it was classified, which policy and evidence state applied, what decision was made, whether review was required, whether execution occurred, what outcome resulted, and how the record links into a verifiable chain.

A decision envelope is not a runtime log.

A runtime log explains what happened.

A decision envelope records how authority was adjudicated.

---

## Constitutional Statements

1. The unit of governance in an agentic system is the proposed consequence, not the tool call.

2. DRF/OMTIR composes policy-bound authorization, evidence-linked claim admission, state-witness approval binding, and hash-chained audit records at the agentic decision boundary.

3. Their logs explain execution. Our envelope adjudicates authority.

4. The model reasons. The policy decides. The record proves.

---

## Core Principle

A model output is not authority.

A tool call is not, by itself, the governable object.

The governable object is the proposed consequence.

For example:

```text
write_file(path='.github/workflows/deploy.yml')
```

As a tool call, this is file writing.

As a proposed consequence, it may be:

```text
PRODUCTION_STATE_CHANGE
HIGH risk
requires reviewer authority
must not execute without approval
```

The decision envelope records that governance judgment.

---

## Two-Layer Architecture

`decision_envelope.v0.1` belongs to the formal governance layer.

It is promoted from a runtime event.

```text
Agent / Gateway / MCP Proxy
        ↓
governance_event.v0.1
runtime source event
        ↓
Promotion Contract v0.1
field mapping + normalization + hash computation + invariant validation
        ↓
decision_envelope.v0.1
canonical governance record
        ↓
Envelope Verifier
schema + hash + chain + invariant verification
        ↓
Trust Receipt / Audit Export / External Review
```

Principle:

> A governance event is what the runtime emits. A decision envelope is what the governance layer is willing to defend.

---

## Schema Location

```text
schemas/decision_envelope_v0.1.schema.json
```

The schema uses JSON Schema Draft 2020-12.

The root object uses:

```text
additionalProperties: false
```

This prevents silent expansion of the record surface.

---

## Required Fields

Every decision envelope must include:

```text
schema_version
created_at
runtime_id
proposal_id
proposal_hash
agent_id
proposed_action
normalized_action
normalized_action_hash
consequence_classification
policy_hash
policy_version
decision_engine_version
decision
decision_basis
decision_reason
review_status
execution_boundary
execution_status
outcome_status
evidence_references
tamper_evidence_mode
previous_record_hash
record_hash
verifier_version
```

`evidence_references` is required even when empty.

An empty evidence array means no evidence references were attached.

A missing evidence field is invalid.

---

## Proposed Action

`proposed_action` is the exact proposed action, claim, handoff, or consequence-bearing request received by the governance layer.

It must not be silently rewritten.

The hash rule is:

```text
proposal_hash = sha256(proposed_action)
```

---

## Normalized Action

`normalized_action` is the deterministic representation used for classification, policy evaluation, hashing, and verification.

The hash rule is:

```text
normalized_action_hash = sha256(normalized_action)
```

---

## Consequence Classification

Each envelope contains a structured consequence classification.

Required fields:

```text
consequence_class
risk_level
reversibility
blast_radius
authority_required
evidence_required
classification_method
classification_confidence
```

The consequence class may be one of:

```text
UNBOUNDED_SHELL_EXECUTION
SECRET_ACCESS
CREDENTIAL_EXPOSURE
DATA_EXPORT
EXTERNAL_COMMUNICATION
PRODUCTION_STATE_CHANGE
POLICY_MUTATION
IDENTITY_OR_PERMISSION_CHANGE
IRREVERSIBLE_DELETE
CLAIM_PUBLICATION
MODEL_OR_PROMPT_MODIFICATION
SELF_MODIFICATION
READ_ONLY_ACCESS
LOCAL_COMPUTATION
UNKNOWN
```

---

## Policy Fields

Each envelope records the policy state used at decision time.

Required policy fields:

```text
policy_hash
policy_version
decision_engine_version
```

Optional policy field:

```text
policy_rule_id
```

`policy_hash` identifies the policy material applied to the decision.

`policy_version` identifies the declared policy version.

`policy_rule_id` may identify the specific rule responsible for the decision when available.

---

## Evidence Fields

Each envelope contains evidence-related fields.

Required:

```text
evidence_references
```

Optional:

```text
evidence_manifest_hash
state_witness_hash
```

`evidence_references` is always required, even when empty.

This avoids ambiguity between:

```text
no evidence references were attached
```

and:

```text
the evidence field was forgotten
```

A model-generated claim does not become operational truth merely because the model produced it.

Evidence admission remains a governance step.

---

## Decision

The governance decision must be one of:

```text
ALLOW
DENY
REQUEST_REVIEW
QUARANTINE
```

Decision basis must be one of:

```text
POLICY_RULE
REVIEWER_APPROVAL
CONSERVATIVE_FALLBACK
EVIDENCE_FAILURE
SYSTEM_GUARD
```

Decision meanings:

```text
ALLOW
A bounded mandate is granted.

DENY
A mandate is refused.

REQUEST_REVIEW
Authority is unresolved and review is required.

QUARANTINE
The proposal is isolated because it is unsupported, unsafe, ambiguous, outside policy, or otherwise inadmissible for normal execution.
```

---

## Review Status

Review status must be one of:

```text
NOT_REQUIRED
PENDING
APPROVED
REJECTED
EXPIRED
INVALIDATED
```

If `review_status` is `PENDING`, `reviewer_authority_id` should be null because no reviewer has acted yet.

If `review_status` is `APPROVED` or `REJECTED`, `reviewer_authority_id` must be non-null.

Optional review fields:

```text
reviewer_authority_id
approval_scope
approval_expiry
```

A pending review is not approval.

A review request does not authorize execution.

---

## Execution and Outcome

Execution and outcome are separate fields.

`execution_status` describes whether execution occurred or was blocked.

`outcome_status` describes the result after governance and execution-boundary handling.

Execution status must be one of:

```text
NOT_EXECUTED
EXECUTED
BLOCKED
FAILED
PARTIAL
PENDING
```

Outcome status must be one of:

```text
SUCCESS
FAILURE
BLOCKED
QUARANTINED
PENDING_REVIEW
```

Examples:

```text
DENY
execution_status: BLOCKED
outcome_status: BLOCKED
```

```text
ALLOW
execution_status: EXECUTED
outcome_status: SUCCESS
```

```text
REQUEST_REVIEW
execution_status: PENDING
outcome_status: PENDING_REVIEW
```

A boolean `executed` field is not sufficient for governance.

---

## Execution Boundary

`execution_boundary` records where execution occurred or where execution was prevented.

Allowed values:

```text
LOCAL_STUB
MCP_PROXY
CONTROLLED_PILOT
NOT_EXECUTED
```

This field keeps the proof boundary explicit.

An envelope may prove that a local stub or controlled pilot was governed.

It does not automatically prove production enforcement.

---

## Tamper Evidence

The envelope supports:

```text
UNKEYED_HASH_CHAIN
HMAC_SHA256_V1
```

In v0.1 examples, `UNKEYED_HASH_CHAIN` is used.

Unkeyed hash chaining is tamper-evident, not custody-proof.

Keyed authentication, durable custody, key rotation, and external notarization are outside the v0.1 proof boundary unless separately implemented and verified.

---

## Record Hash

`record_hash` is computed from the canonical JSON envelope excluding the `record_hash` field itself.

Canonical JSON uses:

```python
json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
```

The hash rule is:

```text
record_hash = sha256(canonical_json(envelope_without_record_hash))
```

The verifier must independently recompute `record_hash`.

The promoter must not be trusted as the final authority on record integrity.

---

## Chain Linkage

Each envelope links to the prior envelope by `previous_record_hash`.

The first envelope uses the genesis value:

```text
0000000000000000000000000000000000000000000000000000000000000000
```

Subsequent envelopes use the full prior `record_hash`, including the `sha256:` prefix.

Valid `previous_record_hash` values are:

```text
sha256:<64 lowercase hex characters>
```

or, for genesis only:

```text
<64 zero characters>
```

A chain is valid only if every envelope verifies and every `previous_record_hash` matches the prior envelope's `record_hash`.

---

## Constitutional Invariants

The verifier must reject records that violate core invariants.

Required v0.1 invariants:

1. `UNKNOWN` consequence must not produce `ALLOW`.

2. `LOW` or `UNCERTAIN` classification confidence must not produce automatic `ALLOW` for consequential execution.

3. `DENY` must not produce consequential execution.

4. `REQUEST_REVIEW + EXECUTED` requires approved review with valid reviewer authority.

5. A model output does not become operational truth without evidence admission.

6. A record must verify before it can be defended.

---

## Source Event Hash

`source_event_hash` is intentionally not part of `decision_envelope.v0.1`.

For v0.1, source-event hashing belongs to the promotion layer.

This preserves the two-layer model:

```text
governance_event.v0.1
runtime emission
        ↓
Promotion Contract v0.1
transformation boundary
        ↓
decision_envelope.v0.1
canonical governance record
```

The envelope records the canonical governance state.

The promotion contract may separately record source-event metadata.

---

## Examples

The v0.1 examples are:

```text
examples/allow_read_source_file.v0.1.json
examples/deny_read_env_file.v0.1.json
examples/request_review_modify_workflow.v0.1.json
```

The three examples form a valid chain:

```text
ALLOW read-only source file
        ↓
DENY credential exposure
        ↓
REQUEST_REVIEW production workflow modification
```

Example 1 uses the genesis previous-record hash.

Example 2 links to Example 1.

Example 3 links to Example 2.

Each example must use real hashes, not placeholders.

---

## Verifier Requirements

A valid verifier must independently check:

```text
schema validity
required fields
proposal_hash
normalized_action_hash
record_hash
previous_record_hash chain linkage
constitutional invariants
review / execution consistency
```

A valid verifier must detect mutation of:

```text
proposed_action
normalized_action
decision
previous_record_hash
record_hash
classification_confidence
consequence_class
execution_status
```

Required mutation-detection output:

```text
proposed_action mutation:           DETECTED
normalized_action mutation:         DETECTED
decision mutation:                  DETECTED
previous_record_hash mutation:      DETECTED
record_hash mutation:               DETECTED
classification_confidence mutation: DETECTED
consequence_class mutation:         DETECTED
execution_status mutation:          DETECTED
```

If any mutation survives, the verifier is not ready.

---

## Minimum Local Validation

At minimum, the following should pass before publication of a release or tag:

```powershell
python -m json.tool schemas/decision_envelope_v0.1.schema.json > $null
python -m json.tool examples/allow_read_source_file.v0.1.json > $null
python -m json.tool examples/deny_read_env_file.v0.1.json > $null
python -m json.tool examples/request_review_modify_workflow.v0.1.json > $null
```

And:

```powershell
python tools/verify_envelope_chain.py examples --mutate --verbose
```

Once promotion is implemented, the stronger condition is:

```powershell
python tools/promote_to_envelope.py wal/ollama-events.jsonl -o envelopes.json --verify
python tools/verify_envelope_chain.py envelopes.json --mutate --verbose
```

---

## What This Does Not Prove

`decision_envelope.v0.1` does not prove:

```text
production durability
independent custody
external notarization
SSO-backed reviewer identity
third-party validation
real-world adversarial robustness
legal admissibility by itself
regulator approval
```

It defines and validates the canonical record surface.

The current claim is local and bounded:

> This project demonstrates a local, inspectable architecture for governed consequence routing in agentic systems.

---

## Public Claim

This repository is not a general AI governance platform.

It is not a replacement for AI GRC systems.

It is not merely an AI gateway, firewall, or logging layer.

It is a runtime evidence architecture for governed consequence routing in agentic systems.

Best distinction:

> Gateways enforce policy. Decision envelopes prove authority.

---

## Final Position

`decision_envelope.v0.1` is the first public governance object of this architecture.

It says:

```text
This was proposed.
This was classified.
This policy applied.
This evidence state was present.
This review state applied.
This decision was made.
This execution boundary was enforced.
This outcome resulted.
This record links to the prior record.
This is how the record verifies.
```

That is AI governance made inspectable.
