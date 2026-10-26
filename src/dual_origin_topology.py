"""Research-only dual historical nuclear reference topology.

Comparison is categorical annotation, not a physical simulation or evidence
of a new nuclear process, universal first event, or quantum-chaos substrate.
No live gate, no sphere writes, and no authoritative Sentinel firing.
"""
from __future__ import annotations
import hashlib
import json
from copy import deepcopy

VERSION = "scandoc-dual-reference/0.1"
FIELDS = ("projectile", "target", "process", "technology")
REFERENCES = {
    "A_1932": {
        "interval": "1932-04", "precision": "month",
        "label": "Cockcroft-Walton lithium disintegration",
        "features": {
            "projectile": "proton", "target": "lithium",
            "process": "induced_nuclear_disintegration",
            "technology": "charged_particle_accelerator",
        },
        "sources": [
            "https://collection.sciencemuseumgroup.org.uk/objects/co5130/cockroft-and-waltons-accelerator",
            "https://www.nature.com/articles/129649a0",
        ],
    },
    "B_1938": {
        "interval": "1938-12", "precision": "month",
        "label": "Hahn-Strassmann uranium fission discovery",
        "features": {
            "projectile": "neutron", "target": "uranium",
            "process": "nuclear_fission",
            "technology": "neutron_irradiation",
        },
        "sources": [
            "https://www.mpic.de/4469988/die-entdeckung-der-kernspaltung",
        ],
    },
    "OMEGA": {
        "interval": None, "precision": "unknown",
        "label": "Hypothesised earliest technological nuclear split in total history",
        "features": None, "sources": [],
    },
}
VALID_MODES = ("synthetic", "observed_classical", "hypothetical")


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(obj):
    return hashlib.sha512(b"SCANDOC-REFERENCE-TOPOLOGY-V0.1\\0" + canonical(obj)).hexdigest()


def topology():
    """Return an independent immutable-by-convention snapshot and digest."""
    nodes = deepcopy(REFERENCES)
    payload = {
        "schema_version": VERSION,
        "nodes": nodes,
        "edges": [
            {"source": "A_1932", "target": "B_1938",
             "relation": "distinct_documented_nuclear_mechanisms"},
            {"source": "A_1932", "target": "OMEGA",
             "relation": "identity_unresolved"},
            {"source": "B_1938", "target": "OMEGA",
             "relation": "identity_unresolved"},
        ],
        "gate": {"live_gate": "CLOSED", "sphere_writes": False,
                 "receipt_trust": "UNVERIFIED"},
    }
    return {"payload": payload, "sha512": digest(payload)}


def validate_topology(record):
    if not isinstance(record, dict) or set(record) != {"payload", "sha512"}:
        raise ValueError("invalid topology envelope")
    if record["payload"] != topology()["payload"]:
        raise ValueError("topology differs from pinned reference contract")
    if record["sha512"] != digest(record["payload"]):
        raise ValueError("topology digest mismatch")
    return True


def compare_model(model):
    """Categorical overlap; not quantitative physics or proof of existence.

    model = {"id": str, "modality": VALID_MODES member,
             "features": {name: categorical string in FIELDS slots},
             "evidence_refs": [nonempty identifiers or URLs]}

    categorical_overlap = matches / fields_compared among *supplied* slots only.
    coverage = fields_compared / len(FIELDS) so partial inputs cannot be read
    as a full-schema agreement. Descriptive annotation only — not a metric.
    """
    if not isinstance(model, dict) or set(model) != {
            "id", "modality", "features", "evidence_refs"}:
        raise ValueError("invalid candidate envelope")
    if not isinstance(model["id"], str) or not model["id"].strip():
        raise ValueError("candidate id required")
    if model["modality"] not in VALID_MODES:
        raise ValueError("unsupported modality")
    evidence = model["evidence_refs"]
    if (not isinstance(evidence, list)
            or any(not isinstance(x, str) or not x.strip() for x in evidence)):
        raise ValueError("invalid evidence_refs")
    if model["modality"] == "observed_classical" and not evidence:
        raise ValueError("observed claims require evidence references")
    features = model["features"]
    if (not isinstance(features, dict) or not set(features) <= set(FIELDS)
            or any(not isinstance(v, str) or not v.strip() for v in features.values())):
        raise ValueError("features must be declared categorical strings")

    fields_missing = sorted(f for f in FIELDS if f not in features)
    fields_compared = len(features)
    coverage = fields_compared / len(FIELDS)

    comparisons = {}
    for key in ("A_1932", "B_1938"):
        reference = REFERENCES[key]["features"]
        matches = {k: features[k] == reference[k] for k in features}
        comparisons[key] = {
            "status": "comparison_only" if matches else "insufficient_data",
            "matching_fields": sorted(k for k, v in matches.items() if v),
            "nonmatching_fields": sorted(k for k, v in matches.items() if not v),
            "fields_compared": fields_compared,
            "fields_missing": list(fields_missing),
            "coverage": coverage,
            "categorical_overlap": (
                sum(matches.values()) / fields_compared if fields_compared else None
            ),
        }
    comparisons["OMEGA"] = {
        "status": "indeterminate",
        "reason": "no observed universal reference",
        "fields_compared": fields_compared,
        "fields_missing": list(fields_missing),
        "coverage": coverage,
    }
    payload = {
        "schema_version": VERSION, "reference_sha512": topology()["sha512"],
        "candidate": deepcopy(model), "comparisons": comparisons,
        "claims": {"existence_established": False, "causation_established": False,
                   "shared_invariant_established": False,
                   "quantum_substrate_verified": False},
        "gate": {"live_gate": "CLOSED", "sphere_writes": False},
    }
    return {"payload": payload, "sha512": digest(payload)}


if __name__ == "__main__":
    print(json.dumps(topology(), indent=2, ensure_ascii=False))
