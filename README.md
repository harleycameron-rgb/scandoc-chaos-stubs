# SCANDOC / Artificial Chaos Stubs

**Long-horizon substrate for residual interference units**  
Constellation: CLOUDBURNER17 · Scandoc Zero · zero-data · sentinel-sealed

## Purpose

This repository archives **artificial chaos stubs** — small, intentionally incomplete interference units. They preserve structure without semantic payload so they can accumulate as causal fossils and residual anchors.

They are **not** a claim that quantum decoding works today. Quantum-access folders are placeholders only.

## What a stub is

Each stub carries:

| Field | Role |
|-------|------|
| `interference_seed.phi` | φ₁–φ₇ sequence (Fibonacci-style interference seed) |
| `gate_burn` | Symbol-gate burn signature (hex fragment) |
| `detune_drift_vector` | 3-axis drift ready for the detune layer |
| `invariant_residue` | Non-semantic residue marker |
| `completeness` | Always `intentionally_incomplete` |
| `semantic_payload` | Always `null` (zero semantic storage) |
| `sentinel` | SHA-512 of canonical JSON |

## Layout

```
scandoc-chaos-stubs/
├── README.md
├── CONTRACT.md
├── stubs/
│   ├── schema.json
│   ├── stub_phi01.json … stub_phi12.json
│   └── manifest.json
├── moire-fields/          # reserved (module B)
├── detune/                # reserved (module C)
├── quantum-access/        # dormant placeholders
└── src/
    └── stub_factory.py
```

## Generate / verify

```bash
python -B src/stub_factory.py --count 12 --out stubs
python -B src/stub_factory.py --verify stubs
```

Requires only the Python standard library.

## Relation to constellation

- **Residue** → `invariant_residue`
- **Sentinel** → same SHA-512 canonical discipline as CLOUDBURNER17
- **Zero-data at runtime** → factory does not log or persist outside the explicit stub files you commit
- **Scandoc** → long-horizon archive arm; stubs age in the repo, not in a live AGI baseline

## Next modules

- **B** — Moiré convergence fields over these stubs  
- **C** — Detune engine (Δφ, φ_Δ, Σφ, τ₀)  

## Status

**Module A (this package): first stub set + schema + factory — ready.**
