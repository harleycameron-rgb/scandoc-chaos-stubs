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

`build_counter_symbol(stub_id, logical_tick=0, **fields)` returns a detached
record. `validate_record(record)` returns `True` or raises `ValueError` for
schema or digest failures. The default `commitment_fields` names every record
field except `commitment` and `commitment_fields`; canonical JSON uses sorted
keys, compact separators, and UTF-8 without ASCII escaping.

`append_observation(parent, stub_id, logical_tick, **observation)` copies the
parent, applies explicit observation fields, and seals a new parent-linked
record with a different ID. It does not mutate inputs or write files.
Observation ticks cannot precede their parent's tick, and observation
commitments must include the new ID, logical tick, and parent link.
Missing residuals remain `null`; missing-measurement entries require both a
nonempty `name` and `missing_reason`. Null residuals require an entry named
`residual_vector`; the builder explicitly labels an omitted residual as
`residual not supplied`.

`correlate_pair(left, right)` reports signed tick lag (`right - left`),
Euclidean residual distance, and topology commitment equality. Missing, empty,
or differently sized residual vectors yield `insufficient_data`, not a
zero distance; absent topology commitments yield an unknown (`null`) match.
The result preserves source modalities, labels the comparison experimental,
and makes no causation or invariant claims.

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

The CLI uses only the Python standard library. Validation exits nonzero for
invalid records. Example generation is deterministic and refuses to overwrite
an existing file with different contents.

Compatible with Anticipatory Chaos Stub Contract v0.1 (gate closed, sphere writes disabled, missing data explicit).
