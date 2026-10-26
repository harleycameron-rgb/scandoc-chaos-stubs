# Module B — Moiré fields

**Rule family:** `scandoc-moire-invariants/v1`  
**Role:** Combine pairs (or small groups) of Module A stubs into sealed **convergence fields**. Pure functions. No semantic payload.

## Intent

A moiré field records what is shared and what differs when two (or more) interference seeds are placed on the same plate:

| Quantity | Meaning |
|----------|---------|
| `overlap_phi` | Element-wise min of φ sequences (shared structure) |
| `residue_phi` | Absolute difference of φ sequences (non-overlap) |
| `drift_mean` | Mean of detune drift vectors |
| `drift_delta` | Difference of drift vectors |
| `gate_xor` | XOR of gate_burn digests (hex) truncated |

These are **structural** combinations only — not claims of physical optics or quantum decode.

## Contract

1. Inputs are existing `stub_phi*.json` ids.
2. Output is a sealed `moire_field` record with `rule_version`, params, inputs, derived vectors, sentinel.
3. `semantic_payload` is always `null`.
4. `completeness` is `intentionally_incomplete`.
5. Same inputs → same field (pure).

## Default plate layout

Consecutive pairs: `(01,02), (03,04), … (11,12)` plus one full-set summary field over all 12.

### Pinned calculations and sealed format

Pair ids are `moire_phi01_02` through `moire_phi11_12`. Each field contains
ordered `inputs` (stub ids), a corresponding `input_seeds` snapshot copied
from the existing stubs, and `params` pinning these conventions:

- `drift_delta` is the first drift vector minus the second.
- `gate_xor` is the XOR of the two 32-digit hexadecimal `gate_burn` values,
  zero-padded to 32 lowercase digits (the existing burns are already truncated).
- `moire_full_set.mean_phi` and `mean_drift` are element-wise arithmetic means
  over all twelve inputs.
- `pair_residue_energy` is a scalar: the sum of squared φ differences across
  all seven components of each of the six consecutive pairs.

Fields and `manifest.json` use SHA-512 over UTF-8 canonical JSON with
`sentinel` set to `""`, sorted keys, compact separators, and `ensure_ascii=False`.
Generation validates the existing stub seals and requires exactly inputs 01–12;
it never creates stubs. Verification recomputes the quantities from the embedded
seeds, checks the pinned metadata and seals, and, for a directory, also requires
the sealed manifest, all seven fields, and consistent pair/full-set inputs.
Verification is structural, not a signature or external provenance guarantee.

## Commands

```bash
python -B src/moire_engine.py --stubs stubs --out moire-fields
python -B src/verify_moire.py moire-fields
```
