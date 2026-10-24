# Constellation index

Single map of linked repositories and verify commands.  
No symbolic claims — roles and carriers only.

| Repo | Role | Primary carrier | Verify / run |
|------|------|-----------------|--------------|
| [scandoc-chaos-stubs](https://github.com/harleycameron-rgb/scandoc-chaos-stubs) | Module A stubs, silhouette, geometry snapshot, detune | Sealed JSON + SHA-512 | `python -B src/verify_snapshot.py stubs` · `python -B src/verify_silhouette.py silhouette/instances` · `python -B src/verify_geometry_snapshot.py silhouette/instances/sil_tentacled_geometry_default.json` · `python -B src/verify_detune.py detune/records` |
| [Tentacled-sphere](https://github.com/harleycameron-rgb/Tentacled-sphere) | Eight-arm unit-sphere geometry (API + browser) | `GET /api/tentacled-sphere?seed=&delta=` | Local: `python -m unittest discover -s tests` · Geometry offline: scandoc geometry snapshot |
| [dynamic-invariant-benchmark](https://github.com/harleycameron-rgb/dynamic-invariant-benchmark) | Designed dynamics vs noise (MSE @ bit budget) | Synthetic field + POD | `python -B src/benchmark.py --field designed` · `--field noise` |
| [cloudburner17](https://github.com/harleycameron-rgb/cloudburner17) | Stabiliser / multi-LLM council (when present) | Council scripts / Vercel app | Repo-local tests |

## Silhouette ↔ geometry

| Instance | Meaning |
|----------|---------|
| `sil_tentacle_8` | Outline: 1-based arm 8 = **lineage** (API index 7) |
| `sil_tentacled_geometry_default` | Sealed default frame: seed `1.0`, delta `0.1137`, 8 unit vectors |

## Layers inside scandoc-chaos-stubs

```text
stubs/          Module A — interference seeds (intentionally incomplete)
silhouette/     Outline layer (motif + scale + sentinel)
detune/         Module C — pure drift / detune transforms
moire-fields/   Module B — placeholder (not implemented)
quantum-access/ Dormant placeholders only (no performance claims)
```

## Uphold rule

A sealed unit is **upheld** iff integrity (sentinel match) ∧ pinned invariants under a declared `rule_version`.
