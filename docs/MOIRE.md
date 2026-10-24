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

## Commands

```bash
python -B src/moire_engine.py --stubs stubs --out moire-fields
python -B src/verify_moire.py moire-fields
```
