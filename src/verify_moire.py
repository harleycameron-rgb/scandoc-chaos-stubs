#!/usr/bin/env python3
"""Verify Module B integrity, structural invariants, and manifest inventory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from moire_engine import FIELD_IDS, PARAMS, RULE_VERSION, STUB_IDS, derive, make_sentinel


def load_sealed(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("root must be an object")
    if data.get("sentinel") != make_sentinel(data):
        raise ValueError("sentinel mismatch or missing")
    return data


def check(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    results = []

    def check_value(key: str, expected: Any) -> None:
        passed = key in data and data[key] == expected
        results.append({"name": key, "pass": passed, "detail": "" if passed else "unexpected value"})

    check_value("kind", "moire_field")
    check_value("version", 1)
    check_value("rule_version", RULE_VERSION)
    check_value("completeness", "intentionally_incomplete")
    check_value("semantic_payload", None)
    check_value("params", PARAMS)
    field_id = data.get("id")
    if field_id not in FIELD_IDS:
        results.append({"name": "id", "pass": False, "detail": "unknown field"})
        return results
    index = FIELD_IDS.index(field_id)
    expected_ids = STUB_IDS if index == 6 else STUB_IDS[index * 2:index * 2 + 2]
    check_value("inputs", expected_ids)
    seeds = data.get("input_seeds")
    try:
        if not isinstance(seeds, list) or len(seeds) != len(expected_ids):
            raise ValueError("wrong input seed count")
        expected = derive(seeds)
        for key, value in expected.items():
            # Canonical JSON distinguishes booleans from numbers.
            passed = key in data and json.dumps(data[key], allow_nan=False) == json.dumps(
                value, allow_nan=False
            )
            results.append({"name": key, "pass": passed, "detail": "" if passed else "recompute mismatch"})
        pair_keys = {"overlap_phi", "residue_phi", "drift_mean", "drift_delta", "gate_xor"}
        full_keys = {"mean_phi", "mean_drift", "pair_residue_energy"}
        forbidden = pair_keys if index == 6 else full_keys
        results.append({
            "name": "field_shape",
            "pass": not forbidden.intersection(data),
            "detail": "pair and full-set quantities must not be mixed",
        })
    except (ValueError, TypeError, KeyError, OverflowError) as exc:
        results.append({"name": "derived_fields", "pass": False, "detail": str(exc)})
    return results


def verify_one(path: Path) -> Dict[str, Any]:
    report = {"path": str(path), "upheld": False, "invariants": []}
    try:
        data = load_sealed(path)
        report["invariants"] = check(data)
        if data.get("id") != path.stem:
            raise ValueError("filename must match field id")
        report["upheld"] = all(item["pass"] for item in report["invariants"])
    except (OSError, ValueError, TypeError, KeyError, OverflowError) as exc:
        report["error"] = str(exc)
    return report


def verify_path(path: Path) -> Dict[str, Any]:
    errors = []
    if path.is_dir():
        files = sorted(path.glob("moire_*.json"))
        if [p.stem for p in files] != sorted(FIELD_IDS):
            errors.append("expected six consecutive pairs and moire_full_set")
        try:
            manifest = load_sealed(path / "manifest.json")
            expected = {
                "module": "B",
                "rule_version": RULE_VERSION,
                "count": 7,
                "ids": FIELD_IDS,
                "params_default": PARAMS,
                "semantic_payload_policy": "always_null",
            }
            if any(manifest.get(key) != value for key, value in expected.items()):
                errors.append("manifest invariants or inventory mismatch")
        except (OSError, ValueError, TypeError, OverflowError) as exc:
            errors.append(f"manifest: {exc}")
    else:
        files = [path]
    reports = [verify_one(p) for p in files]
    if path.is_dir() and not errors and all(r["upheld"] for r in reports):
        full = load_sealed(path / "moire_full_set.json")
        for index, field_id in enumerate(FIELD_IDS[:-1]):
            pair = load_sealed(path / f"{field_id}.json")
            if pair["input_seeds"] != full["input_seeds"][index * 2:index * 2 + 2]:
                errors.append(f"{field_id}: inputs differ from full-set inputs")
    upheld = sum(r["upheld"] for r in reports)
    return {
        "reports": reports,
        "errors": errors,
        "upheld_count": upheld,
        "all_upheld": bool(reports) and upheld == len(reports) and not errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="moiré field file or directory")
    args = parser.parse_args()
    summary = verify_path(Path(args.path))
    print(f"rule_version: {RULE_VERSION}")
    print(f"upheld: {summary['upheld_count']}/{len(summary['reports'])}")
    for report in summary["reports"]:
        print(f"  [{'UPHELD' if report['upheld'] else 'FAIL'}] {report['path']}")
        if report.get("error"):
            print(f"         {report['error']}")
        for invariant in report["invariants"]:
            if not invariant["pass"]:
                print(f"         {invariant['name']}: {invariant['detail']}")
    for error in summary["errors"]:
        print(f"  FAIL: {error}")
    raise SystemExit(0 if summary["all_upheld"] else 1)


if __name__ == "__main__":
    main()

