#!/usr/bin/env python3
"""Verify silhouette integrity and pinned v1 invariants without network I/O."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Dict, List

from stub_factory import make_sentinel

RULE_VERSION = "scandoc-silhouette-invariants/v1"
REQUIRED_KEYS = {
    "id", "kind", "version", "rule_version", "outline",
    "completeness", "semantic_payload", "sentinel",
}
OPTIONAL_KEYS = {"created_at", "carrier_ref"}
OUTLINE_KEYS = {"motif", "scale", "axes", "residue_mark"}


def _result(name: str, passed: bool) -> Dict[str, Any]:
    return {"name": name, "pass": passed}


def check_invariants(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    version = data.get("version")
    results = [
        _result("required_keys", REQUIRED_KEYS <= data.keys()),
        _result("allowed_keys", data.keys() <= REQUIRED_KEYS | OPTIONAL_KEYS),
        _result("id", isinstance(data.get("id"), str) and bool(data["id"])),
        _result("kind", data.get("kind") == "silhouette"),
        _result("version", type(version) in (int, float)
                and version >= 1 and version % 1 == 0),
        _result("rule_version", data.get("rule_version") == RULE_VERSION),
        _result("completeness", data.get("completeness") == "intentionally_incomplete"),
        _result("semantic_payload_null", data.get("semantic_payload") is None),
    ]
    for key in OPTIONAL_KEYS:
        results.append(_result(
            key, key not in data or data[key] is None or isinstance(data[key], str)
        ))
    outline = data.get("outline")
    if not isinstance(outline, dict):
        results.append(_result("outline", False))
        return results
    results.extend([
        _result("outline_keys", outline.keys() <= OUTLINE_KEYS),
        _result("motif", isinstance(outline.get("motif"), str) and bool(outline["motif"])),
    ])
    if "scale" in outline:
        scale = outline["scale"]
        results.append(_result(
            "scale", type(scale) is int or
            (type(scale) is float and math.isfinite(scale))
        ))
    if "axes" in outline:
        axes = outline["axes"]
        results.append(_result(
            "axes", isinstance(axes, list) and all(isinstance(x, str) for x in axes)
        ))
    if "residue_mark" in outline:
        results.append(_result("residue_mark", isinstance(outline["residue_mark"], str)))
    return results


def _check_manifest(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    ids = data.get("ids")
    valid_ids = (
        isinstance(ids, list)
        and all(isinstance(sid, str) and sid for sid in ids)
        and len(set(ids)) == len(ids)
    )
    return [
        _result("manifest_keys", data.keys() == {
            "rule_version", "count", "ids", "schema", "completeness",
            "semantic_payload_policy", "sentinel",
        }),
        _result("rule_version", data.get("rule_version") == RULE_VERSION),
        _result("ids", valid_ids),
        _result("count", type(data.get("count")) is int
                and valid_ids and data["count"] == len(ids) and data["count"] > 0),
        _result("schema", data.get("schema") == "silhouette/schema.json"),
        _result("completeness", data.get("completeness") == "intentionally_incomplete"),
        _result("semantic_payload_policy", data.get("semantic_payload_policy") == "always_null"),
    ]


def _unique_object(pairs: list) -> dict:
    data = {}
    for key, value in pairs:
        if key in data:
            raise ValueError(f"duplicate key: {key}")
        data[key] = value
    return data


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-JSON number: {value}")


def _verify(path: Path, manifest: bool = False) -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "path": str(path),
        "rule_version": RULE_VERSION,
        "integrity": {"pass": False},
        "invariants": [],
        "upheld": False,
    }
    try:
        data = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
        if not isinstance(data, dict):
            raise ValueError("root is not an object")
        computed = make_sentinel(data)
    except (OSError, ValueError, RecursionError) as error:
        report["error"] = str(error)
        return report
    stored = data.get("sentinel")
    report["integrity"] = {
        "pass": isinstance(stored, str) and stored == computed,
        "stored_sentinel": stored,
        "computed_sentinel": computed,
    }
    report["invariants"] = _check_manifest(data) if manifest else check_invariants(data)
    report["upheld"] = report["integrity"]["pass"] and all(
        result["pass"] for result in report["invariants"]
    )
    report["id"] = data.get("id")
    if manifest:
        report["ids"] = data.get("ids")
    return report


def verify_one(path: Path) -> Dict[str, Any]:
    return _verify(path)


def verify_path(path: Path) -> Dict[str, Any]:
    path = path.resolve()
    summary: Dict[str, Any] = {
        "rule_version": RULE_VERSION, "target": str(path), "all_upheld": False,
    }
    if path.is_file():
        reports = [verify_one(path)]
    elif path.is_dir():
        reports = [verify_one(p) for p in sorted(path.glob("*.json"))
                   if p.name != "manifest.json"]
        manifest = _verify(path / "manifest.json", manifest=True)
        summary["manifest"] = manifest
        ids = [report.get("id") for report in reports]
        manifest["matches_instances"] = (
            manifest["upheld"]
            and all(report["upheld"] for report in reports)
            and sorted(manifest["ids"]) == sorted(ids)
            and all(Path(report["path"]).name == f"{report['id']}.json"
                    for report in reports)
        )
    else:
        summary["error"] = f"path not found: {path}"
        reports = []
    summary["reports"] = reports
    summary["count"] = len(reports)
    summary["upheld_count"] = sum(report["upheld"] for report in reports)
    summary["all_upheld"] = (
        bool(reports) and all(report["upheld"] for report in reports)
        and summary.get("manifest", {}).get("matches_instances", True)
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify sealed silhouette v1 invariants")
    parser.add_argument("path", type=Path, help="Silhouette JSON file or instances directory")
    parser.add_argument("--json", action="store_true", help="Print full JSON report")
    args = parser.parse_args()
    summary = verify_path(args.path)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"rule_version: {RULE_VERSION}")
        print(f"upheld: {summary['upheld_count']}/{summary['count']}")
        print(f"all_upheld: {summary['all_upheld']}")
        for report in summary["reports"] + (
            [summary["manifest"]] if "manifest" in summary else []
        ):
            if not report["upheld"]:
                print(f"FAIL {report['path']}: {report.get('error', '')}")
                if not report["integrity"]["pass"]:
                    print("  integrity: sentinel mismatch or missing")
                for result in report["invariants"]:
                    if not result["pass"]:
                        print(f"  invariant: {result['name']}")
        if summary.get("error"):
            print(summary["error"])
        if "manifest" in summary and not summary["manifest"]["matches_instances"]:
            print("FAIL manifest does not match instances")
    raise SystemExit(0 if summary["all_upheld"] else 1)


if __name__ == "__main__":
    main()
