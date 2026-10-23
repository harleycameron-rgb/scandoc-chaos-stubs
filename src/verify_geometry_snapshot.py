#!/usr/bin/env python3
"""Offline checks for tentacled geometry snapshot silhouettes."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


def check(data: dict) -> list:
    out = []
    g = data.get("geometry")
    if not isinstance(g, dict):
        return [("geometry_object", False, "missing geometry")]

    arms = g.get("arms")
    n = g.get("arm_count")
    out.append((
        "arm_count_8",
        n == 8 and isinstance(arms, list) and len(arms) == 8,
        f"count={n} len={len(arms) if isinstance(arms, list) else None}",
    ))

    if not isinstance(arms, list):
        return out

    for a in arms:
        v = a.get("vector")
        if not (isinstance(v, list) and len(v) == 3):
            out.append((f"vector_{a.get('app')}", False, "bad vector"))
            continue
        norm = math.sqrt(sum(float(x) * float(x) for x in v))
        ok = abs(norm - 1.0) <= 1e-6
        out.append((f"unit_{a.get('app')}", ok, f"norm={norm}"))

    if len(arms) >= 8:
        lin = arms[7]
        out.append((
            "arm8_lineage",
            lin.get("app") == "lineage" and lin.get("index_1based") == 8,
            f"app={lin.get('app')} index_1based={lin.get('index_1based')}",
        ))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    args = ap.parse_args()
    data = json.loads(Path(args.path).read_text(encoding="utf-8"))
    results = check(data)
    all_ok = True
    for name, ok, detail in results:
        print(f"  [{'OK' if ok else 'FAIL'}] {name}: {detail}")
        all_ok = all_ok and ok
    print("all_ok:" if all_ok else "FAILED", all_ok)
    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
