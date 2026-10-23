#!/usr/bin/env python3
"""
Artificial chaos stub factory for SCANDOC / CLOUDBURNER constellation.
Standard library only. Zero semantic payload. SHA-512 sentinel.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, List


def fib_phi(n: int = 7) -> List[int]:
    seq = [1, 1]
    while len(seq) < n:
        seq.append(seq[-1] + seq[-2])
    return seq[:n]


def make_sentinel(payload: Dict[str, Any]) -> str:
    """SHA-512 of canonical JSON with sentinel field zeroed."""
    body = dict(payload)
    body["sentinel"] = ""
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha512(canonical.encode("utf-8")).hexdigest()


def gate_burn(index: int, phi: List[int]) -> str:
    raw = f"stub_phi{index:02d}|" + ",".join(str(x) for x in phi)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def detune_drift_vector(index: int, phi: List[int]) -> List[float]:
    s = sum(phi) + index
    return [
        round(math.sin(s * 0.1137) * 0.01 * index, 8),
        round(math.cos(s * 0.0618) * 0.01 * index, 8),
        round(math.sin(s * 0.001) * 0.001 * index, 8),
    ]


def invariant_residue(index: int, burn: str) -> str:
    return hashlib.sha256(f"residue|{index}|{burn}".encode("utf-8")).hexdigest()[:24]


def build_stub(index: int) -> Dict[str, Any]:
    base_phi = fib_phi(7)
    phi = [base_phi[(i + index) % 7] + (index % 3) for i in range(7)]
    burn = gate_burn(index, phi)
    stub: Dict[str, Any] = {
        "id": f"stub_phi{index:02d}",
        "version": 1,
        "created_at": None,
        "interference_seed": {
            "phi": phi,
            "gate_burn": burn,
            "detune_drift_vector": detune_drift_vector(index, phi),
            "invariant_residue": invariant_residue(index, burn),
        },
        "completeness": "intentionally_incomplete",
        "semantic_payload": None,
        "sentinel": "",
    }
    stub["sentinel"] = make_sentinel(stub)
    return stub


def write_stubs(out_dir: Path, count: int) -> List[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    ids: List[str] = []
    for i in range(1, count + 1):
        stub = build_stub(i)
        path = out_dir / f"{stub['id']}.json"
        path.write_text(json.dumps(stub, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        ids.append(stub["id"])
    manifest = {
        "module": "A",
        "count": count,
        "ids": ids,
        "schema": "stubs/schema.json",
        "completeness": "intentionally_incomplete",
        "semantic_payload_policy": "always_null",
    }
    manifest["sentinel"] = make_sentinel({**manifest, "sentinel": ""})
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return ids


def verify_dir(out_dir: Path) -> int:
    errors = 0
    for path in sorted(out_dir.glob("stub_phi*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        expected = make_sentinel(data)
        if data.get("sentinel") != expected:
            print(f"FAIL sentinel {path.name}")
            errors += 1
        if data.get("semantic_payload") is not None:
            print(f"FAIL semantic_payload {path.name}")
            errors += 1
        if data.get("completeness") != "intentionally_incomplete":
            print(f"FAIL completeness {path.name}")
            errors += 1
        print(f"OK {path.name} sentinel={data['sentinel'][:16]}...")
    return errors


def main() -> None:
    p = argparse.ArgumentParser(description="SCANDOC artificial chaos stub factory")
    p.add_argument("--count", type=int, default=12)
    p.add_argument("--out", type=str, default="stubs")
    p.add_argument("--verify", type=str, default="", help="Directory to verify")
    args = p.parse_args()

    if args.verify:
        err = verify_dir(Path(args.verify))
        raise SystemExit(err)

    ids = write_stubs(Path(args.out), args.count)
    print(f"Wrote {len(ids)} stubs + manifest \u2192 {args.out}")
    for i in ids:
        print(" ", i)


if __name__ == "__main__":
    main()
