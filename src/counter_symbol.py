#!/usr/bin/env python3
"""
Counter-Symbol Chaos Stub (scandoc-counter-symbol/0.1).
Standard library only. Synthetic, append-only, experimental.
Gates stay closed: no daemon activation, no sphere writes.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SCHEMA = "scandoc-counter-symbol/0.1"
COMMITMENT_FIELDS = ["schema", "record_id", "logical_tick", "vector", "measurements"]
LIVE_GATE_CLOSED = "CLOSED"
ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = ROOT / "counter-symbol" / "examples"


class CounterSymbolError(ValueError):
    pass


def daemon_gate_allows_activation(*_args: Any, **_kwargs: Any) -> bool:
    """Daemon activation is never allowed in this stub."""
    return False


def _canonical(obj: Any) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


def compute_commitment(record: Dict[str, Any]) -> str:
    """SHA-512 over commitment_fields only."""
    fields = record.get("commitment_fields", COMMITMENT_FIELDS)
    subset = {k: record[k] for k in fields}
    return hashlib.sha512(_canonical(subset)).hexdigest()


def _is_finite_number(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def _check_vector(vec: Any, label: str = "vector") -> None:
    if not isinstance(vec, list) or not vec:
        raise CounterSymbolError(f"{label} must be a non-empty list")
    for x in vec:
        if not _is_finite_number(x):
            raise CounterSymbolError(f"{label} contains non-finite or non-numeric value")


def _check_tick(tick: Any) -> None:
    if isinstance(tick, bool) or not isinstance(tick, int) or tick < 0:
        raise CounterSymbolError("logical_tick must be an integer >= 0")


def _check_measurement(m: Any) -> None:
    if not isinstance(m, dict) or not isinstance(m.get("name"), str) or not m["name"]:
        raise CounterSymbolError("measurement requires a non-empty name")
    if "value" in m and m["value"] is not None:
        if not _is_finite_number(m["value"]):
            raise CounterSymbolError("measurement value must be finite")
        if "expected" in m and not _is_finite_number(m["expected"]):
            raise CounterSymbolError("measurement expected must be finite")
    else:
        reason = m.get("missing_reason")
        if not isinstance(reason, str) or not reason:
            raise CounterSymbolError("missing measurement requires name and missing_reason")


def _residuals(measurements: List[Dict[str, Any]]) -> Dict[str, float]:
    """Residuals only for present measurements with an expected value; never zero-filled."""
    out: Dict[str, float] = {}
    for m in measurements:
        if m.get("value") is not None and "expected" in m:
            out[m["name"]] = m["value"] - m["expected"]
    return out


def build_counter_symbol(
    record_id: str,
    logical_tick: int,
    vector: List[float],
    measurements: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    _check_tick(logical_tick)
    _check_vector(vector)
    measurements = copy.deepcopy(measurements or [])
    for m in measurements:
        _check_measurement(m)
    record: Dict[str, Any] = {
        "schema": SCHEMA,
        "record_id": record_id,
        "logical_tick": logical_tick,
        "vector": list(vector),
        "measurements": measurements,
        "residuals": _residuals(measurements),
        "observations": [],
        "commitment_fields": list(COMMITMENT_FIELDS),
        "gates": {
            "daemon_gate_allows_activation": daemon_gate_allows_activation(),
            "live_gate": LIVE_GATE_CLOSED,
            "sphere_writes": False,
        },
        "experimental": True,
        "synthetic": True,
    }
    record["commitment"] = compute_commitment(record)
    return record


def validate_record(record: Dict[str, Any]) -> List[str]:
    """Return list of problems; empty means valid."""
    errs: List[str] = []
    if not isinstance(record, dict):
        return ["record must be an object"]
    if record.get("schema") != SCHEMA:
        errs.append("bad schema")
    if record.get("commitment_fields") != COMMITMENT_FIELDS:
        errs.append("bad commitment_fields")
    checks = [
        lambda: _check_tick(record.get("logical_tick")),
        lambda: _check_vector(record.get("vector")),
    ]
    ms = record.get("measurements")
    if not isinstance(ms, list):
        errs.append("measurements must be a list")
    else:
        checks += [lambda m=m: _check_measurement(m) for m in ms]
    for c in checks:
        try:
            c()
        except CounterSymbolError as e:
            errs.append(str(e))
    gates = record.get("gates", {})
    if gates.get("daemon_gate_allows_activation") is not False:
        errs.append("daemon_gate_allows_activation must be false")
    if gates.get("live_gate") != LIVE_GATE_CLOSED:
        errs.append("live_gate must be CLOSED")
    if gates.get("sphere_writes") is not False:
        errs.append("sphere_writes must be false")
    if isinstance(ms, list):
        missing = {m.get("name") for m in ms if isinstance(m, dict) and m.get("value") is None}
        res = record.get("residuals", {})
        if not isinstance(res, dict):
            errs.append("residuals must be an object")
        else:
            for k, v in res.items():
                if k in missing:
                    errs.append(f"residual present for missing measurement {k}")
                elif not _is_finite_number(v):
                    errs.append(f"residual {k} not finite")
    if not errs:
        try:
            if record.get("commitment") != compute_commitment(record):
                errs.append("commitment mismatch")
        except (KeyError, ValueError, TypeError):
            errs.append("commitment not computable")
    return errs


def append_observation(record: Dict[str, Any], observation: Dict[str, Any]) -> Dict[str, Any]:
    """Return a new record with the observation appended; existing data untouched."""
    errs = validate_record(record)
    if errs:
        raise CounterSymbolError("; ".join(errs))
    if not isinstance(observation, dict):
        raise CounterSymbolError("observation must be an object")
    tick = observation.get("logical_tick")
    _check_tick(tick)
    obs = record["observations"]
    if obs and tick < obs[-1]["logical_tick"]:
        raise CounterSymbolError("observation logical_tick must not decrease")
    if "vector" in observation:
        _check_vector(observation["vector"], "observation vector")
    new = copy.deepcopy(record)
    new["observations"].append(copy.deepcopy(observation))
    return new


def correlate_pair(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """Experimental Pearson correlation of two record vectors. No causation claim."""
    va, vb = a["vector"], b["vector"]
    _check_vector(va)
    _check_vector(vb)
    if len(va) != len(vb):
        raise CounterSymbolError("vectors must have equal length")
    n = len(va)
    ma, mb = sum(va) / n, sum(vb) / n
    da = [x - ma for x in va]
    db = [x - mb for x in vb]
    denom = math.sqrt(sum(x * x for x in da) * sum(x * x for x in db))
    r = sum(x * y for x, y in zip(da, db)) / denom if denom > 0 and n > 1 else None
    return {
        "pair": [a["record_id"], b["record_id"]],
        "pearson_r": r,
        "experimental": True,
        "causation_claim": False,
        "note": "correlation only; no causal inference",
    }


def example_records() -> List[Dict[str, Any]]:
    r1 = build_counter_symbol("cs_example_01", 0, [0.1, 0.2, 0.3],
                              [{"name": "m1", "value": 1.0, "expected": 0.9}])
    r2 = build_counter_symbol("cs_example_02", 1, [0.3, 0.2, 0.1],
                              [{"name": "m1", "missing_reason": "sensor offline"}])
    r3 = append_observation(
        build_counter_symbol("cs_example_03", 2, [0.5, 0.5, 0.6],
                             [{"name": "m1", "value": 2.0, "expected": 2.5}]),
        {"logical_tick": 3, "vector": [0.5, 0.6, 0.6]},
    )
    return [r1, r2, r3]


def write_examples(directory: Path = EXAMPLES_DIR) -> List[Path]:
    directory.mkdir(parents=True, exist_ok=True)
    paths = []
    for rec in example_records():
        p = directory / f"{rec['record_id']}.json"
        p.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        paths.append(p)
    return paths


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-examples", action="store_true")
    ap.add_argument("--validate", nargs="*", metavar="FILE",
                    help="validate files (default: example directory)")
    args = ap.parse_args(argv)
    if args.write_examples:
        for p in write_examples():
            print(f"wrote {p}")
    if args.validate is not None:
        files = [Path(f) for f in args.validate] or sorted(EXAMPLES_DIR.glob("*.json"))
        bad = 0
        for f in files:
            errs = validate_record(json.loads(f.read_text(encoding="utf-8")))
            print(f"{'OK  ' if not errs else 'FAIL'} {f}" + ("" if not errs else f": {errs}"))
            bad += bool(errs)
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
