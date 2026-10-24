#!/usr/bin/env python3
"""Verify Module C detune records under scandoc-detune-invariants/v1."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

RULE_VERSION = "scandoc-detune-invariants/v1"
TRANSFORM_ID = "linear_scale_v1"


def make_sentinel(payload: Dict[str, Any]) -> str:
    body = dict(payload)
    body["sentinel"] = ""
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha512(canonical.encode("utf-8")).hexdigest()


def check(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    def ok(n: str, d: str = "") -> None:
        out.append({"name": n, "pass": True, "detail": d})

    def fail(n: str, d: str) -> None:
        out.append({"name": n, "pass": False, "detail": d})

    if data.get("kind") == "detune_record":
        ok("kind")
    else:
        fail("kind", f"got {data.get('kind')!r}")

    if data.get("rule_version") == RULE_VERSION:
        ok("rule_version")
    else:
        fail("rule_version", f"got {data.get('rule_version')!r}")

    if data.get("transform_id") == TRANSFORM_ID:
        ok("transform_id")
    else:
        fail("transform_id", f"got {data.get('transform_id')!r}")

    if data.get("completeness") == "intentionally_incomplete":
        ok("completeness")
    else:
        fail("completeness", str(data.get("completeness")))

    if data.get("semantic_payload") is None:
        ok("semantic_payload_null")
    else:
        fail("semantic_payload_null", "non-null")

    for key in ("input_drift", "output_drift"):
        v = data.get(key)
        if isinstance(v, list) and len(v) == 3 and all(isinstance(x, (int, float)) for x in v):
            ok(f"{key}_len_3")
        else:
            fail(f"{key}_len_3", repr(v))

    params = data.get("params") or {}
    scale = float(params.get("scale", 1.0))
    bias = params.get("bias") or [0.0, 0.0, 0.0]
    inp = data.get("input_drift")
    outd = data.get("output_drift")
    if isinstance(inp, list) and len(inp) == 3 and isinstance(outd, list) and len(outd) == 3:
        expected = []
        for i in range(3):
            x = float(inp[i]) * scale + float(bias[i])
            x = -1.0 if x < -1.0 else 1.0 if x > 1.0 else x
            expected.append(x)
        match = all(abs(expected[i] - float(outd[i])) < 1e-12 for i in range(3))
        if match:
            ok("transform_recompute")
        else:
            fail("transform_recompute", f"expected {expected} got {outd}")

    return out


def verify_one(path: Path) -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "path": str(path),
        "rule_version": RULE_VERSION,
        "integrity": {"pass": False},
        "invariants": [],
        "upheld": False,
    }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        report["error"] = str(e)
        return report

    stored = data.get("sentinel")
    computed = make_sentinel(data)
    report["integrity"] = {
        "pass": isinstance(stored, str) and stored == computed,
        "stored_sentinel": stored,
        "computed_sentinel": computed,
    }
    inv = check(data)
    report["invariants"] = inv
    report["upheld"] = report["integrity"]["pass"] and all(i["pass"] for i in inv)
    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=str, help="detune record file or directory")
    args = ap.parse_args()
    path = Path(args.path)
    if path.is_dir():
        files = sorted(path.glob("detune_*.json"))
    else:
        files = [path]
    reports = [verify_one(f) for f in files]
    upheld = sum(1 for r in reports if r.get("upheld"))
    print(f"rule_version: {RULE_VERSION}")
    print(f"upheld: {upheld}/{len(reports)}")
    for r in reports:
        print(f"  [{'UPHELD' if r.get('upheld') else 'FAIL'}] {r['path']}")
        if not r.get("upheld"):
            if not r.get("integrity", {}).get("pass"):
                print("         integrity fail")
            for inv in r.get("invariants", []):
                if not inv["pass"]:
                    print(f"         {inv['name']}: {inv['detail']}")
    raise SystemExit(0 if upheld == len(reports) and reports else 1)


if __name__ == "__main__":
    main()
