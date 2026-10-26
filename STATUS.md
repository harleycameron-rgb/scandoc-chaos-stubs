# SCANDOC status board

Last update: 2026-10-26

## On `main` (flying)

| Module | Path | Verify |
|--------|------|--------|
| **A** stubs | `stubs/` | `python -B src/verify_snapshot.py stubs` |
| **B** moiré engine | `src/moire_engine.py` | generate then `verify_moire` |
| **C** detune | `detune/records/` | `python -B src/verify_detune.py detune/records` |
| Silhouette | `silhouette/instances/` | `verify_silhouette` |
| Geometry snapshot | `sil_tentacled_geometry_default.json` | `verify_geometry_snapshot` |
| Counter-Symbol | `src/counter_symbol.py` | `python -m unittest tests.test_counter_symbol` |
| CI | `.github/workflows/verify.yml` | Actions on push/PR |

Gates: **CLOSED**. Sphere writes: **false**.

## Open PRs

| PR | Title | Action |
|----|-------|--------|
| **#5** draft | Module B moiré fields | Superseded by engines on main — **close** after confirming fields committed |
| **#6** draft | Counter-symbol v0.1 | Superseded — **close** |
| **#7** draft | Counter-Symbol Chaos Stub | Superseded — **close** |
| **#8** ready | Dual nuclear reference topology | Research-only; merge when CI green |

## Sister repos

| Repo | Open | Note |
|------|------|------|
| cloudburner17 | [#54](https://github.com/harleycameron-rgb/cloudburner17/pull/54) | Persistent authority — hold until Postgres CI |
| Tentacled-sphere | [#16](https://github.com/harleycameron-rgb/Tentacled-sphere/pull/16) draft | Six-leg separation research |
| waxtablet.co.uk | — | Runtime 500: missing `admission` on sys.path — see DEPLOY_ADMISSION_FIX |

## Next to fly

1. Commit sealed `moire-fields/` JSON (engine is on main; fields optional until generated).
2. Close draft PRs #5–#7.
3. Merge #8 after isolated CI.
4. cloudburner17: admission path fix → Vercel preview (not prod without approval).
5. PR #54: wait for Postgres workflow green.
