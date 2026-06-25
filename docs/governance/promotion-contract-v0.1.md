# Promotion Contract v0.1



> A governance event is what the runtime emits. A decision envelope is what the governance layer is willing to defend.



`Promotion Contract v0.1` defines the transformation boundary between runtime telemetry and formal governance records.



It specifies how a `governance_event.v0.1` becomes a `decision_envelope.v0.1`.



The promotion contract exists because runtime events and governance records serve different purposes.



A runtime event is optimized for emission.



A decision envelope is optimized for verification.



\---



## Purpose



The purpose of this contract is to ensure that runtime governance events are promoted into canonical decision envelopes without silently inventing, dropping, weakening, or corrupting governance-relevant information.



Promotion must be deterministic, inspectable, and independently verifiable.



The promoter is not the proof layer.



The verifier is the proof layer.



\---



## Architecture Position



```text

Agent / Gateway / MCP Proxy

&#x20;       â†“

governance_event.v0.1

runtime source event

&#x20;       â†“

Promotion Contract v0.1

field mapping + normalization + hash computation + invariant validation

&#x20;       â†“

decision_envelope.v0.1

canonical governance record

&#x20;       â†“

Envelope Verifier

schema + hash + chain + invariant verification

&#x20;       â†“

Trust Receipt / Audit Export / External Review

```



\---



## Input



The input is a runtime governance event.



Expected input shape may include:



```json

{

&#x20; "runtime": {

&#x20;   "gateway_version": "v0.2",

&#x20;   "mode": "SHADOW_SAFE"

&#x20; },

&#x20; "tool_call": {

&#x20;   "name": "read_file",

&#x20;   "arguments": {

&#x20;     "path": ".env"

&#x20;   }

&#x20; },

&#x20; "omtir_evidence": {},

&#x20; "drf_decision": {

&#x20;   "decision": "DENY",

&#x20;   "reason": "credential exposure"

&#x20; },

&#x20; "wal": {

&#x20;   "sequence": 1,

&#x20;   "hash": "..."

&#x20; }

}

```



The promoter must support nested runtime events.



It must not depend only on flattened fake event objects.



\---



## Output



The output is a valid `decision_envelope.v0.1`.



The envelope must validate against:



```text

schemas/decision_envelope_v0.1.schema.json

```



The output must contain all required schema fields.



The promoter must fail if required envelope fields cannot be populated.



It must not silently emit `null` for required fields.



\---



## Promotion Must



The promoter must:



```text

read .json and .jsonl governance events

preserve runtime identity

preserve proposal content

normalize the proposed action deterministically

classify the proposed consequence

map policy fields

map evidence references

map review state

map execution state

map outcome state

assign previous_record_hash

compute proposal_hash

compute normalized_action_hash

compute record_hash last

validate schema

validate constitutional invariants

emit a valid decision envelope

fail clearly on missing required fields

```



\---



## Promotion Must Not



The promoter must not:



```text

silently rewrite proposed_action

silently change decision outcome

silently drop evidence state

silently invent reviewer authority

silently convert review pending into approval

silently allow unknown consequences

silently allow denied proposals to execute

silently emit null for required fields

silently produce unverifiable record_hash

silently break chain linkage

```



\---



## Source Event Hash



`source_event_hash` is intentionally not part of `decision_envelope.v0.1`.



For v0.1, source-event hashing belongs to the promotion layer.



This preserves the two-layer architecture:



```text

governance_event.v0.1

runtime emission

&#x20;       â†“

Promotion Contract v0.1

transformation boundary

&#x20;       â†“

decision_envelope.v0.1

canonical governance record

```



A future schema version may add source-event linkage if the schema is reopened.



For v0.1, the decision envelope remains the canonical governance record, while source-event metadata remains promotion-layer context.



\---



## Field Mapping



The promoter must map runtime fields into envelope fields.



Minimum required mappings:



| Envelope Field               | Source / Rule                                               |

| ---------------------------- | ----------------------------------------------------------- |

| `schema_version`             | constant: `decision_envelope_v0.1`                          |

| `created_at`                 | promotion timestamp or trusted event timestamp              |

| `runtime_id`                 | runtime identity / gateway identity                         |

| `proposal_id`                | generated UUID or event proposal ID                         |

| `agent_id`                   | event agent identity or configured default                  |

| `proposed_action`            | exact proposed action derived from event                    |

| `normalized_action`          | deterministic normalized form                               |

| `proposal_hash`              | `sha256(proposed_action)`                                   |

| `normalized_action_hash`     | `sha256(normalized_action)`                                 |

| `consequence_classification` | deterministic or configured classifier                      |

| `policy_hash`                | active policy hash                                          |

| `policy_version`             | active policy version                                       |

| `decision_engine_version`    | promoter / decision engine version                          |

| `decision`                   | DRF decision mapping                                        |

| `decision_basis`             | policy, review, fallback, evidence failure, or system guard |

| `decision_reason`            | runtime decision reason                                     |

| `review_status`              | mapped review lifecycle state                               |

| `execution_boundary`         | runtime execution boundary                                  |

| `execution_status`           | mapped execution state                                      |

| `outcome_status`             | mapped outcome state                                        |

| `evidence_references`        | OMTIR evidence references or empty array                    |

| `tamper_evidence_mode`       | selected tamper evidence mode                               |

| `previous_record_hash`       | genesis or prior envelope hash                              |

| `record_hash`                | computed after all other fields                             |

| `verifier_version`           | verifier version expected to validate envelope              |



\---



## Hash Rules



### Proposal Hash



```text

proposal_hash = sha256(proposed_action)

```



### Normalized Action Hash



```text

normalized_action_hash = sha256(normalized_action)

```



### Record Hash



`record_hash` is computed from the canonical JSON envelope excluding `record_hash` itself.



Canonical JSON uses:



```python

json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

```



Rule:



```text

record_hash = sha256(canonical_json(envelope_without_record_hash))

```



\---



## Chain Convention



The first envelope uses the genesis value:



```text

0000000000000000000000000000000000000000000000000000000000000000

```



Subsequent envelopes use the full previous `record_hash`, including the `sha256:` prefix.



Example:



```text

previous_record_hash = sha256:<64 lowercase hex characters>

```



A chain is valid only if every envelope verifies and every `previous_record_hash` matches the prior envelope's `record_hash`.



\---



## Constitutional Invariants



Promotion must reject records that violate constitutional invariants.



Required v0.1 invariants:



1\. `UNKNOWN` consequence must not produce `ALLOW`.



2\. `LOW` or `UNCERTAIN` classification confidence must not produce automatic `ALLOW` for consequential execution.



3\. `DENY` must not produce consequential execution.



4\. `REQUEST_REVIEW + EXECUTED` requires approved review with valid reviewer authority.



5\. A model output does not become operational truth without evidence admission.



6\. A record must verify before it can be defended.



\---



## Review-State Rules



If `review_status` is:



```text

PENDING

```



then:



```text

reviewer_authority_id = null

```



because no reviewer has acted yet.



If `review_status` is:



```text

APPROVED

REJECTED

```



then:



```text

reviewer_authority_id != null

```



because an accountable authority must be recorded.



A pending review is not approval.



A review request does not authorize execution.



\---



## Execution Rules



`DENY` must not produce consequential execution.



Valid denied state:



```text

decision: DENY

execution_status: BLOCKED or NOT_EXECUTED

outcome_status: BLOCKED

```



`REQUEST_REVIEW` without approval must remain pending or not executed.



Valid pending-review state:



```text

decision: REQUEST_REVIEW

review_status: PENDING

execution_status: PENDING or NOT_EXECUTED

outcome_status: PENDING_REVIEW

```



`ALLOW` may execute only within the declared `execution_boundary`.



\---



## Failure Modes



Promotion must fail clearly with a structured failure mode.



Required failure modes:



```text

PROMOTION_FAILED_SCHEMA_INVALID

PROMOTION_FAILED_CONSTITUTIONAL_VIOLATION

PROMOTION_FAILED_HASH_MISMATCH

PROMOTION_FAILED_CHAIN_BREAK

PROMOTION_FAILED_MISSING_REQUIRED_FIELD

PROMOTION_FAILED_MISSING_REQUIRED_OUTPUT_FIELD

```



A failed promotion must not be emitted as a valid envelope.



\---



## Verifier Relationship



The promoter creates envelopes.



The verifier proves envelopes.



The verifier must not trust the promoter.



A valid verifier independently checks:



```text

schema validity

proposal_hash

normalized_action_hash

record_hash

previous_record_hash linkage

constitutional invariants

review / execution consistency

mutation detection

```



\---



## GO / NO-GO Condition



Promotion Contract v0.1 is not complete until the real runtime WAL path passes:



```powershell

python tools/promote_to_envelope.py wal/ollama-events.jsonl -o envelopes.json --verify

python tools/verify_envelope_chain.py envelopes.json --mutate --verbose

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



If any mutation survives:



```text

NO COMMIT

NO TAG

NO PUBLIC CLAIM

```



\---



## Public Boundary



This contract does not claim legal admissibility by itself.



It does not claim production readiness by itself.



It does not claim regulator approval.



It defines an inspectable transformation from runtime governance events into canonical decision envelopes.



Acceptable claim:



> Promotion Contract v0.1 defines how runtime governance events become verifiable decision envelopes.



Acceptable claim:



> A governance event is what the runtime emits. A decision envelope is what the governance layer is willing to defend.



\---



## Final Position



Promotion Contract v0.1 is the bridge between runtime telemetry and governance proof.



Without it, runtime events remain operational logs.



With it, governance events can become canonical decision envelopes.



The promoter transforms.



The verifier proves.



The record survives review.




