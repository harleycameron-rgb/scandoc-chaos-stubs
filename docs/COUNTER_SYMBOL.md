# Counter-Symbol Chaos Stub v0.1

**Status:** experimental / opt-in research record  
**Gate:** `live_gate=CLOSED` always  
**Sphere writes:** `false` always  
**Schema:** `scandoc-counter-symbol/0.1`

## Purpose

Preserve **unresolved** information for later cross-correlation:

- Residual disagreement after accept/reject
- Rejected or incomplete transitions
- Post-separation drift references
- Missing measurements (explicit slots, never zero-filled)
- Topology / parent commitment references

Does **not** authorise DaemonGate transitions.

## Commitment

SHA-512 over canonical JSON of `commitment_fields` only (see `src/counter_symbol.py`).  
Field `commitment` is excluded from the digest input.

Append-only: later observations are **new** records with `parent_commitment` set. Historical files are never rewritten.

## Integration boundaries

| System | Boundary |
|--------|----------|
| Tentacled Sphere | Does not change eight-vector preview API; does not redefine six spatial legs or past/future tentacles |
| DaemonGate | `daemon_gate_allows_activation` always returns false |
| Module A stubs | Optional `related_stub_ids` / `sentinel_reference` only |
| Correlation | Experimental; no causation or invariant claims |

## Commands

```bash
python -B src/counter_symbol.py --write-examples counter-symbol/examples
python -B src/counter_symbol.py --validate counter-symbol/examples/cs-synthetic-001.json
python -m unittest tests.test_counter_symbol -v
```

Compatible with Anticipatory Chaos Stub Contract v0.1 (gate closed, sphere writes disabled, missing data explicit).
