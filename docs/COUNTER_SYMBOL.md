# Counter-Symbol Chaos Stub (`scandoc-counter-symbol/0.1`)

Synthetic, experimental, append-only records. Standard library only.

- **Commitment**: SHA-512 over `commitment_fields` only (`schema`, `record_id`,
  `logical_tick`, `vector`, `measurements`). Observations and residuals are outside the commitment.
- **Append-only**: `append_observation` returns a new record; ticks never decrease.
- **Gates**: `daemon_gate_allows_activation` is always `false`, `live_gate` is `CLOSED`,
  `sphere_writes` is `false`. Validation rejects anything else.
- **Validation**: vectors must be finite; `logical_tick >= 0`. Missing measurements need
  `name` + `missing_reason`; residuals are never zero-filled.
- **`correlate_pair`**: experimental Pearson correlation; makes no causation claims.

CLI:

    python src/counter_symbol.py --write-examples
    python src/counter_symbol.py --validate [FILE ...]

Tests: `python -m unittest tests.test_counter_symbol -v`

Schema: `counter-symbol/schema/counter_symbol_v0.1.json`; examples in `counter-symbol/examples/`.
