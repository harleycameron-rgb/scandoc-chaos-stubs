#!/usr/bin/env python3
"""Module C — Detune engine. Pure drift-vector transforms; sealed records; stdlib only."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence

RULE_VERSION = "scandoc-detune-invariants/v1"
TRANSFORM_ID = "linear_scale_v1"


def make_sentinel(payload: Dict[str, Any]) -> str:
    body = dict(payload)
    body["sentinel"] = ""
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha512(canonical.encode("utf-8")).hexdigest()


def clamp(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return lo if x < lo else hi if x > hi else x


def linear_scale(
    drift: Sequence[float],
    scale: float = 1.0,
    bias: Sequence[float] | None = None,
) -> List[float]:
    b = list(bias) if bias is not None else [0.0, 0.0, 0.0]
    if len(drift) != 3 or len(b) != 3:
        raise ValueError("drift and bias must have length 3")
    return [clamp(float(drift[i]) * float(scale) + float(b[i])) for i in range(3)]


def build_record(
    stub: Dict[str, Any],
    scale: float = 1.0,
    bias: Sequence[float] | None = None,
) -> Dict[str, Any]:
    seed = stub.get("interference_seed") or {}
    drift = seed.get("detune_drift_vector")
    if not isinstance(drift, list) or len(drift) != 3:
        raise ValueError(f"stub {stub.get('id')} missing detune_drift_vector length 3")

    out_drift = linear_scale(drift, scale=scale, bias=bias)
    rec: Dict[str, Any] = {
        "id": f"detune_{stub['id']}",
        "kind": "detune_record",
        "version": 1,
        "rule_version": RULE_VERSION,
        "transform_id": TRANSFORM_ID,
        "input_stub_id": stub["id"],
        "params": {
            "scale": scale,
            "bias": list(bias) if bias is not None else [0.0, 0.0, 0.0],
        },
        "input_drift": [float(x) for x in drift],
        "output_drift": out_drift,
        "completeness": "intentionally_incomplete",
        "semantic_payload": None,
        "sentinel": "",
    }
    rec["sentinel"] = make_sentinel(rec)
    return rec


def run(stubs_dir: Path, out_dir: Path, scale: float = 1.0) -> List[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    ids: List[str] = []
    for path in sorted(stubs_dir.glob("stub_phi*.json")):
        stub = json.loads(path.read_text(encoding="utf-8"))
        rec = build_record(stub, scale=scale)
        out_path = out_dir / f"{rec['id']}.json"
        out_path.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
        ids.append(rec["id"])

    manifest = {
        "module": "C",
        "rule_version": RULE_VERSION,
        "transform_id": TRANSFORM_ID,
        "count": len(ids),
        "ids": ids,
        "params_default": {"scale": scale, "bias": [0.0, 0.0, 0.0]},
        "semantic_payload_policy": "always_null",
    }
    manifest["sentinel"] = make_sentinel({**manifest, "sentinel": ""})
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return ids


def main() -> None:
    p = argparse.ArgumentParser(description="SCANDOC Module C detune engine")
    p.add_argument("--stubs", type=str, default="stubs")
    p.add_argument("--out", type=str, default="detune/records")
    p.add_argument("--scale", type=float, default=1.0)
    args = p.parse_args()
    ids = run(Path(args.stubs), Path(args.out), scale=args.scale)
    print(f"Wrote {len(ids)} detune records → {args.out}")
    for i in ids:
        print(" ", i)


if __name__ == "__main__":
    main()
