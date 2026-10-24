# Module B — Moiré fields

**Rule family:** `scandoc-moire-invariants/v1`

Combine Module A stubs into sealed convergence fields (pair plates + full_set).

```bash
python -B src/moire_engine.py --stubs stubs --out moire-fields
python -B src/verify_moire.py moire-fields
```
