# Counter-Symbol Chaos Stub v0.1

**Status:** experimental / opt-in research record  
**Gate:** `live_gate=CLOSED` always  
**Sphere writes:** `false` always  
**Schema:** `scandoc-counter-symbol/0.1`

## Purpose

Preserve unresolved information for later cross-correlation without authorising DaemonGate.

## Commands

```bash
python -B src/counter_symbol.py --write-examples counter-symbol/examples
python -B src/counter_symbol.py --validate counter-symbol/examples/cs-synthetic-001.json
python -m unittest tests.test_counter_symbol -v
```

Compatible with Anticipatory Chaos Stub Contract v0.1.
