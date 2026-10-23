# Geometry snapshot silhouette — Tentacled Sphere

**File:** `silhouette/instances/sil_tentacled_geometry_default.json`  
**Purpose:** Offline, sealed record of the default eight-arm API geometry so integrity can be upheld **without** calling the live API.

## Contents

| Field | Meaning |
|--------|---------|
| `outline.motif` | `tentacled_sphere_geometry` |
| `geometry.model` | `api` (latitude + helical angle) |
| `geometry.seed` / `delta` | `1.0` / `0.1137` |
| `geometry.arms[0..7]` | index, app name, vector, curvature, norm |
| `geometry.arms[7]` | **lineage** = 1-based arm **8** |
| `semantic_payload` | `null` |
| `sentinel` | SHA-512 over full canonical object |

## Formulas (as stored)

```text
theta_i = seed + i * delta
z_i    = 1 - 2 * (i + 0.5) / 8
r_i    = sqrt(1 - z_i^2)
vector = [r*cos(theta), r*sin(theta), z]
curvature = 1 / r
```

All stored vectors are unit length (within float rounding to 12 decimals).

## Verify

```bash
python -B src/verify_silhouette.py silhouette/instances/sil_tentacled_geometry_default.json
python -B src/verify_geometry_snapshot.py silhouette/instances/sil_tentacled_geometry_default.json
```

## Relation to sil_tentacle_8

| Instance | Role |
|----------|------|
| `sil_tentacle_8` | Outline handle: arm 8 / lineage + carrier_ref |
| `sil_tentacled_geometry_default` | Full default frame: all 8 vectors + seed/delta sealed |

Neither replaces the live Tentacled-sphere API; both are archival outlines.
