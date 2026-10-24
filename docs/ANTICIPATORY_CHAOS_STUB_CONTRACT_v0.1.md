# Anticipatory Chaos Stub Contract v0.1 (research, opt-in)

Status: PROPOSED. Gate: CLOSED. Sphere writes: DISABLED. Quantum measurement: UNAVAILABLE.

A Chaos Stub is an intentionally incomplete provenance contract, not a substitute for unrecorded measurements. Existing `src/stub_factory.py` and `stubs/schema.json` remain unchanged; compatibility with legacy synthetic stubs must be tested before adoption.

## Record requirements

- `schema_version`: `scandoc-anticipatory-stub/0.1`.
- `stub_id`, `family`, `source_modality`: one of `synthetic`, `observed_classical`, `hypothetical`.
- `timestamp_utc` and `t0_reference`: separate observation time from historical Sentinel provenance; optional solar phase requires location/algorithm provenance and is not a universal clock.
- `topology`: canonical graph encoding specification, SHA-512 digest, canonicalizer version, optional filtration/complex type, and derived fingerprints. Hash does not disclose or reconstruct original graph.
- `input_commitments`: digests with algorithms, source availability, acquisition conventions and limitations. No personal data required.
- `measurements`: names, units, methods, uncertainty and observed values; absent measurements use `null` with explicit `missing_reason` and must never be zero-filled.
- `reserved_fields`: declared future *schema slots*, each with expected method, missing reason, and verification status `UNVERIFIED`. Quantum slots remain empty.
- `claims`: claim ID, evidential modality (`measured`, `inferred`, `assumed`, `inherited`, `contested`, `unverified`), cited parent records and interpretive limits.
- `derivation_edges`: typed parent references forming a provenance DAG; provenance integrity does not prove semantic correctness.
- `geometry`: six spatial leg associations and distinct `past` / `future` temporal identifiers. All derived trajectories require prior valid separation; never substitute diurnal/Krylov cycles for tentacle identities.
- `safety`: `live_gate=CLOSED`, `sphere_writes=false`, `receipt_trust=UNVERIFIED`.

## Append-only refinement

Once committed, a stub is immutable. New classical measurements, corrected interpretations or eventually verified quantum measurements are NEW records referencing the old `stub_id` and commitment digest. Never overwrite an old digest or silently upgrade `hypothetical` to `observed_classical`. A verified quantum category requires separate independent attestation and an explicitly versioned schema extension.

## Proposed research adapters (NOT integrated)

1. Gain solar phase: UTC plus location, ephemeris version, time-zone/session controls. Solar phase is an optional derived coordinate.
2. Persistent-homology provenance fingerprint: source graph, filtration, complex and distance convention are all versioned; label permutation must preserve mathematical diagram.
3. Derivational provenance gap: typed claims and attested sources, with explicit annotation uncertainty.
4. Krylov research: operator, initial observable, inner product, recurrence method, sampling and uncertainty must be specified before a Lanczos chain is meaningful. Neither generic time-series Lanczos coefficients nor decreasing Krylov complexity automatically demonstrate quantum correspondence or VelocitySplat counterflow.

## Required tests before adoption

- Canonical graph isomorphic relabeling leaves topology fingerprint stable under documented canonicalization; changed edges produce appropriate structural drift measurements.
- New measurement attachment leaves committed historical records byte-for-byte unchanged.
- Null values without missing reasons fail validation; hypothetical quantum input is never marked observed.
- Out-of-order or non-finite time values fail; solar-phase fallback covers polar day/night.
- Claims promoted from assumed to measured without external attestation fail.
- Closed gate and disabled sphere writes remain mandatory.
- Surrogate and holdout tests establish empirical utility; correlation does not certify causal mechanism.

This document introduces an experimental contract only; no deployed endpoint, Gate writer, operational collector or eight-app trajectory connection is asserted.
