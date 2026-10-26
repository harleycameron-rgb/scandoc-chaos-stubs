#!/usr/bin/env python3
"""Module B — deterministic, sealed structural moiré fields; stdlib only."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any, Dict, List

from stub_factory import make_sentinel

RULE_VERSION = "scandoc-moire-invariants/v1"
STUB_IDS = [f"stub_phi{i:02d}" for i in range(1, 13)]
FIELD_IDS = [f"moire_phi{i:02d}_{i + 1:02d}" for i in range(1, 13, 2)] + [
    "moire_full_set"
]
PARAMS = {
    "drift_delta_order": "first_minus_second",
    "gate_xor_hex_length": 32,
    "pair_residue_energy": "sum_squared_consecutive_pair_residues",
}


def validate_seed(seed: Any) -> None:
    if not isinstance(seed, dict):
        raise ValueError("input seed must be an object")
    for key, length in (("phi", 7), ("detune_drift_vector", 3)):
        values = seed.get(key)
        if not isinstance(values, list) or len(values) != length or not all(
            type(x) in (int, float) and math.isfinite(x) for x in values
        ):
            raise ValueError(f"{key} must contain {length} finite numbers")
    burn = seed.get("gate_burn")
    if not isinstance(burn, str) or re.fullmatch(r"[0-9a-f]{32}", burn) is None:
        raise ValueError("gate_burn must be 32 lowercase hex digits")


def derive(seeds: List[Dict[str, Any]]) -> Dict[str, Any]:
    for seed in seeds:
        validate_seed(seed)
    if len(seeds) not in (2, 12):
        raise ValueError("a field requires two or twelve seeds")
    phis = [s["phi"] for s in seeds]
    drifts = [s["detune_drift_vector"] for s in seeds]
    if len(seeds) == 2:
        return {
            "overlap_phi": [min(a, b) for a, b in zip(*phis)],
            "residue_phi": [abs(a - b) for a, b in zip(*phis)],
            "drift_mean": [(a + b) / 2 for a, b in zip(*drifts)],
            "drift_delta": [a - b for a, b in zip(*drifts)],
            "gate_xor": f"{int(seeds[0]['gate_burn'], 16) ^ int(seeds[1]['gate_burn'], 16):032x}",
        }
    return {
        "mean_phi": [sum(axis) / 12 for axis in zip(*phis)],
        "mean_drift": [sum(axis) / 12 for axis in zip(*drifts)],
        "pair_residue_energy": sum(
            (a - b) ** 2
            for i in range(0, 12, 2)
            for a, b in zip(phis[i], phis[i + 1])
        ),
    }


def build_record(stubs: List[Dict[str, Any]], field_id: str) -> Dict[str, Any]:
    seeds = [stub["interference_seed"] for stub in stubs]
    record = {
        "id": field_id,
        "kind": "moire_field",
        "version": 1,
        "rule_version": RULE_VERSION,
        "params": dict(PARAMS),
        "inputs": [stub["id"] for stub in stubs],
        "input_seeds": seeds,
        **derive(seeds),
        "completeness": "intentionally_incomplete",
        "semantic_payload": None,
        "sentinel": "",
    }
    record["sentinel"] = make_sentinel(record)
    return record


def run(stubs_dir: Path, out_dir: Path) -> List[str]:
    paths = sorted(stubs_dir.glob("stub_phi*.json"))
    if [p.stem for p in paths] != STUB_IDS:
        raise ValueError("expected exactly stub_phi01.json through stub_phi12.json")
    stubs = []
    for path in paths:
        stub = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(stub, dict) or stub.get("id") != path.stem:
            raise ValueError(f"{path}: invalid stub id")
        if stub.get("sentinel") != make_sentinel(stub):
            raise ValueError(f"{path}: invalid stub sentinel")
        if "semantic_payload" not in stub or stub["semantic_payload"] is not None:
            raise ValueError(f"{path}: semantic_payload must be null")
        if stub.get("completeness") != "intentionally_incomplete":
            raise ValueError(f"{path}: invalid completeness")
        validate_seed(stub.get("interference_seed"))
        stubs.append(stub)
    records = [
        build_record(stubs[i:i + 2], FIELD_IDS[i // 2]) for i in range(0, 12, 2)
    ]
    records.append(build_record(stubs, FIELD_IDS[-1]))
    manifest = {
        "module": "B",
        "rule_version": RULE_VERSION,
        "count": len(records),
        "ids": list(FIELD_IDS),
        "params_default": dict(PARAMS),
        "semantic_payload_policy": "always_null",
    }
    manifest["sentinel"] = make_sentinel(manifest)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in [(r["id"], r) for r in records] + [("manifest", manifest)]:
        (out_dir / f"{name}.json").write_text(
            json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
    return list(FIELD_IDS)


def main() -> None:
    parser = argparse.ArgumentParser(description="SCANDOC Module B moiré engine")
    parser.add_argument("--stubs", default="stubs")
    parser.add_argument("--out", default="moire-fields")
    args = parser.parse_args()
    try:
        ids = run(Path(args.stubs), Path(args.out))
    except (OSError, ValueError, KeyError, OverflowError) as exc:
        parser.exit(1, f"moire engine: {exc}\n")
    print(f"Wrote {len(ids)} moiré fields + manifest → {args.out}")


if __name__ == "__main__":
    main()

