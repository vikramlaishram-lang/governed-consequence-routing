# Portable Verification Bundle v0.5

## 1. Why Portable Verification Bundles Exist

Governed Consequence Routing records proposed AI-agent consequences as structured artifacts that can be validated, hash-bound, and independently inspected.

v0.5 adds a portable verification bundle so a governed AI decision can be exported with the local material needed for outside review.

A vendor-only dashboard is not independent verification.

A private database record is not a portable proof bundle.

A portable bundle lets a reviewer inspect the decision envelope, authority material, evidence material, schema hashes, verification results, and proof-boundary metadata without relying on a private service view.

## 2. Internal Log vs. Portable Proof Bundle

An internal log is useful for runtime observability, custody, and operational debugging. It may live in a local file, database, dashboard, or service-specific storage layer.

A portable proof bundle is a standalone artifact. It packages local verification material for independent inspection.

The source of truth remains the included structured artifacts and their hashes, not the human-readable summary.

## 3. Included Artifacts

A full v0.5 GCR bundle includes:

- decision envelope
- approval token
- reviewer authority manifest
- evidence manifest
- artifact hashes
- schema hashes
- verification results
- proof-boundary metadata
- bundle hash

The bundle records both the artifacts and the hashes expected to verify them locally.

## 4. Combining v0.3 and v0.4

v0.3 proves local authority binding:

```text
decision envelope <-> approval token <-> reviewer authority manifest
```

v0.4 proves local evidence binding:

```text
decision envelope <-> evidence manifest <-> evidence items
```

v0.5 packages the authority material and evidence material into one portable verification bundle:

```text
portable bundle
  -> decision envelope
  -> approval token
  -> reviewer authority manifest
  -> evidence manifest
  -> schema hashes
  -> verification results
  -> proof boundary
```

## 5. What v0.5 Proves

v0.5 proves that a governed AI decision can be exported into a portable verification bundle whose included artifacts, hashes, verification results, and proof-boundary metadata are independently inspectable and locally verifiable.

Specifically, v0.5 demonstrates local verification of:

- bundle schema validity
- bundle hash integrity
- embedded artifact hash integrity
- schema file hash integrity
- approval token verification
- reviewer authority binding verification
- evidence manifest binding verification
- bundle subject linkage to embedded artifacts
- recorded verification results

## 6. What v0.5 Does Not Prove

A bundle is not a legal certificate.

A bundle is not external notarization.

v0.5 does not prove production custody, external notarization, legal admissibility, regulatory compliance, clinical safety, financial advice suitability, enterprise compliance, non-repudiation, or truth of evidence source content.

## 7. Current Proof Boundary

This remains a local reference implementation and developer starter kit.

The v0.5 proof boundary is local export and local verification of structured artifacts, hashes, schema hashes, verification results, and proof-boundary metadata.

The bundle makes verification material portable. It does not make the underlying decision legally certified, externally notarized, production-custodied, or regulator-approved.
