#!/usr/bin/env python3
"""Generate sealed, non-semantic silhouettes using only the standard library."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from stub_factory import make_sentinel

RULE_VERSION = "scandoc-silhouette-invariants/v1"
MOTIFS = (
    "chaos_line",
    "dual_state",
    "pulse_sphere",
    "convergent_projection",
    "complete_gate",
)
SCALES = (1, 0.1, 0.01)


def build_silhouette(motif: str, scale: float) -> Dict[str, Any]:
    silhouette: Dict[str, Any] = {
        "id": f"sil_{motif}_{scale:g}",
        "kind": "silhouette",
        "version": 1,
        "rule_version": RULE_VERSION,
        "created_at": None,
        "outline": {"motif": motif, "scale": scale},
        "completeness": "intentionally_incomplete",
        "semantic_payload": None,
        "sentinel": "",
    }
    silhouette["sentinel"] = make_sentinel(silhouette)
    return silhouette


def write_silhouettes(out_dir: Path) -> List[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    ids: List[str] = []
    for motif in MOTIFS:
        for scale in SCALES:
            silhouette = build_silhouette(motif, scale)
            (out_dir / f"{silhouette['id']}.json").write_text(
                json.dumps(silhouette, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            ids.append(silhouette["id"])
    manifest = {
        "rule_version": RULE_VERSION,
        "count": len(ids),
        "ids": ids,
        "schema": "silhouette/schema.json",
        "completeness": "intentionally_incomplete",
        "semantic_payload_policy": "always_null",
    }
    manifest["sentinel"] = make_sentinel(manifest)
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return ids


def main() -> None:
    parser = argparse.ArgumentParser(description="SCANDOC silhouette factory")
    parser.add_argument("--out", type=Path, default=Path("silhouette/instances"))
    args = parser.parse_args()
    ids = write_silhouettes(args.out)
    print(f"Wrote {len(ids)} silhouettes + manifest → {args.out}")


if __name__ == "__main__":
    main()
