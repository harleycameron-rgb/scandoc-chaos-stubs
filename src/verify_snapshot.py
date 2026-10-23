#!/usr/bin/env python3
"""
verify_snapshot — uphold a sealed snapshot against pinned invariants over time.

Operational meaning of "invariance over time":
  1. Integrity: recomputed sentinel matches stored sentinel.
  2. Invariants: pure predicates on the carrier still hold under rule_version.
  3. Rules are versioned; changing rules is a new contract, not silent drift.

Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

RULE_VERSION = "scandoc-stub-invariants/v1"

REQUIRED_KEYS = (
    "id",
    "version",
    "created_at",
    "interference_seed",
    "completeness",
    "semantic_payload",
    "sentinel",
)
SEED_KEYS = ("phi", "gate_burn", "detune_drift_vector", "invariant_residue")


def make_sentinel(payload: Dict[str, Any]) -> str:
    body = dict(payload)
    body["sentinel"] = ""
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha512(canonical.encode("utf-8")).hexdigest()


def _ok(name: str, detail: str = "") -> Dict[str, Any]:
    return {"name": name, "pass": True, "detail": detail}


def _fail(name: str, detail: str) -> Dict[str, Any]:
    return {"name": name, "pass": False, "detail": detail}


def check_invariants(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    missing = [k for k in REQUIRED_KEYS if k not in data]
    if missing:
        results.append(_fail("required_keys", f"missing: {missing}"))
    else:
        results.append(_ok("required_keys"))

    if data.get("completeness") == "intentionally_incomplete":
        results.append(_ok("completeness"))
    else:
        results.append(
            _fail(
                "completeness",
                f"expected intentionally_incomplete, got {data.get('completeness')!r}",
            )
        )

    if data.get("semantic_payload") is None:
        results.append(_ok("semantic_payload_null"))
    else:
        results.append(
            _fail(
                "semantic_payload_null",
                f"expected null, got {type(data.get('semantic_payload')).__name__}",
            )
        )

    seed = data.get("interference_seed")
    if not isinstance(seed, dict):
        results.append(_fail("interference_seed", "not an object"))
    else:
        miss = [k for k in SEED_KEYS if k not in seed]
        if miss:
            results.append(_fail("interference_seed_keys", f"missing: {miss}"))
        else:
            results.append(_ok("interference_seed_keys"))

        phi = seed.get("phi")
        if isinstance(phi, list) and len(phi) == 7 and all(
            isinstance(x, (int, float)) for x in phi
        ):
            results.append(_ok("phi_length_7"))
        else:
            results.append(_fail("phi_length_7", f"phi={phi!r}"))

        drift = seed.get("detune_drift_vector")
        if isinstance(drift, list) and len(drift) == 3:
            results.append(_ok("detune_drift_vector_len_3"))
        else:
            results.append(_fail("detune_drift_vector_len_3", f"drift={drift!r}"))

        burn = seed.get("gate_burn")
        if isinstance(burn, str) and 8 <= len(burn) <= 64:
            results.append(_ok("gate_burn_format"))
        else:
            results.append(_fail("gate_burn_format", f"gate_burn={burn!r}"))

    sid = data.get("id")
    if isinstance(sid, str) and sid.startswith("stub_phi"):
        results.append(_ok("id_prefix"))
    else:
        results.append(_fail("id_prefix", f"id={sid!r}"))

    return results


def verify_one(path: Path) -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "path": str(path),
        "rule_version": RULE_VERSION,
        "integrity": {"pass": False, "stored_sentinel": None, "computed_sentinel": None},
        "invariants": [],
        "upheld": False,
    }

    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception as e:
        report["error"] = f"load_failed: {e}"
        return report

    if not isinstance(data, dict):
        report["error"] = "root_not_object"
        return report

    stored = data.get("sentinel")
    computed = make_sentinel(data)
    report["integrity"] = {
        "pass": isinstance(stored, str) and stored == computed,
        "stored_sentinel": stored,
        "computed_sentinel": computed,
    }

    inv = check_invariants(data)
    report["invariants"] = inv
    inv_ok = all(x["pass"] for x in inv)
    report["upheld"] = bool(report["integrity"]["pass"] and inv_ok)
    return report


def verify_path(path: Path) -> Dict[str, Any]:
    path = path.resolve()
    if path.is_file():
        reports = [verify_one(path)]
    elif path.is_dir():
        files = sorted(path.glob("stub_phi*.json"))
        if not files:
            files = sorted(p for p in path.glob("*.json") if p.name != "schema.json")
        reports = [verify_one(p) for p in files]
    else:
        return {
            "rule_version": RULE_VERSION,
            "error": f"path not found: {path}",
            "upheld": False,
            "reports": [],
        }

    upheld_n = sum(1 for r in reports if r.get("upheld"))
    summary = {
        "rule_version": RULE_VERSION,
        "target": str(path),
        "count": len(reports),
        "upheld_count": upheld_n,
        "all_upheld": upheld_n == len(reports) and len(reports) > 0,
        "reports": reports,
    }
    seal_body = {
        "rule_version": RULE_VERSION,
        "target": summary["target"],
        "count": summary["count"],
        "upheld_count": summary["upheld_count"],
        "paths": [r["path"] for r in reports],
        "upheld_flags": [r.get("upheld") for r in reports],
    }
    summary["verification_sentinel"] = hashlib.sha512(
        json.dumps(seal_body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return summary


def main() -> None:
    p = argparse.ArgumentParser(
        description="Verify sealed snapshot integrity + pinned invariants"
    )
    p.add_argument(
        "path",
        type=str,
        help="Stub JSON file or directory of stub_phi*.json",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Print full JSON report",
    )
    args = p.parse_args()
    summary = verify_path(Path(args.path))

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"rule_version: {summary.get('rule_version')}")
        print(f"target:       {summary.get('target')}")
        if summary.get("error"):
            print(f"error:        {summary['error']}")
            raise SystemExit(2)
        print(f"count:        {summary['count']}")
        print(f"upheld:       {summary['upheld_count']}/{summary['count']}")
        print(f"all_upheld:   {summary['all_upheld']}")
        for r in summary.get("reports", []):
            flag = "UPHELD" if r.get("upheld") else "FAIL"
            print(f"  [{flag}] {r.get('path')}")
            if not r.get("integrity", {}).get("pass"):
                print("         integrity: sentinel mismatch or missing")
            for inv in r.get("invariants", []):
                if not inv["pass"]:
                    print(f"         invariant {inv['name']}: {inv['detail']}")
        print(f"verification_sentinel: {summary.get('verification_sentinel', '')[:32]}...")

    raise SystemExit(0 if summary.get("all_upheld") else 1)


if __name__ == "__main__":
    main()
