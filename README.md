# SCANDOC / Artificial Chaos Stubs

**Long-horizon substrate for residual interference units**  
Constellation: CLOUDBURNER17 · Scandoc Zero · zero-data · sentinel-sealed

## Purpose

Archives **artificial chaos stubs** — intentionally incomplete interference units. Structure without semantic payload. Quantum-access folders are placeholders only.

## Status

| Module | State |
|--------|--------|
| **A** stubs (12) | on `main` |
| **B** moiré engine + verifier | on `main` |
| **C** detune records (12) | on `main` |
| Silhouette + geometry snapshot | on `main` |
| Counter-Symbol v0.1 | on `main` (gate CLOSED) |
| CI uphold workflow | on `main` |

See [STATUS.md](STATUS.md) for PR board and next actions.

## Quick verify

```bash
python -B src/verify_snapshot.py stubs
python -B src/verify_detune.py detune/records
python -B src/moire_engine.py --stubs stubs --out moire-fields
python -B src/verify_moire.py moire-fields
python -m unittest tests.test_counter_symbol -v
```

Stdlib only. Gates stay CLOSED.
