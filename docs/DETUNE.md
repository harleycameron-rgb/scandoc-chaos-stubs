# Module C — Detune

**Rule family:** `scandoc-detune-invariants/v1`  
**Role:** Pure functions on stub drift vectors. No network. No semantic payload.

## Intent

Stubs carry `detune_drift_vector` (length 3). Detune applies a **declared, versioned** transform and seals the result so it can be re-checked offline.

## Contract

1. Input: factory stub JSON (or drift vector alone).
2. Output: detune record with `input_stub_id`, `params`, `input_drift`, `output_drift`, `sentinel`.
3. `semantic_payload` is always `null`.
4. Transforms are pure: same input + params → same output.
5. No claim that detune “unlocks quantum access.”

## Default transform (`linear_scale_v1`)

```text
out[i] = clamp(in[i] * scale + bias[i], -1.0, 1.0)
```

Default params: `scale=1.0`, `bias=[0,0,0]` (identity — still seals a receipt).

## Commands

```bash
python -B src/detune_engine.py --stubs stubs --out detune/records
python -B src/verify_detune.py detune/records
```
