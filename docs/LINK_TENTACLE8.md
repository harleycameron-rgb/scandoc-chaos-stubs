# Link: Silhouette ↔ Tentacle 8

**Geometry carrier:** [Tentacled-sphere](https://github.com/harleycameron-rgb/Tentacled-sphere)  
**Constraint (from that repo):** API returns exactly **eight** arms (`tentacles.length === 8`).

## Silhouette instance

`silhouette/instances/sil_tentacle_8.json`

| Field | Value |
|--------|--------|
| `outline.motif` | `tentacle_arm` |
| `outline.axes` | `arm_index:8`, `geometry:tentacled_sphere` |
| `carrier_ref` | Tentacled-sphere repo URL |
| `semantic_payload` | `null` |
| `completeness` | `intentionally_incomplete` |

## What the link is

- **Outline** of arm 8 as a sealed silhouette (identity + integrity).
- **Pointer** to the geometry system that defines all eight arms.
- **Not** a copy of arm vectors or live API state (those stay in Tentacled-sphere).

## What it is not

- Not a ninth arm.
- Not a claim that arm 8 is privileged physics beyond index 8 in the eight-arm model.
- Not a substitute for `verify` on geometry snapshots inside Tentacled-sphere.

## Uphold

```bash
python -B src/verify_silhouette.py silhouette/instances/sil_tentacle_8.json
```

Integrity + silhouette invariants only. Geometry correctness remains Tentacled-sphere’s responsibility.
