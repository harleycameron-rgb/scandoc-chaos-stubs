#!/usr/bin/env python3
"""Offline, append-only counter-symbol research records. No activation authority."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
from pathlib import Path

SCHEMA_VERSION = "scandoc-counter-symbol/0.1"
COMMITMENT_FIELDS = (
    "schema_version", "stub_id", "source_modality", "parent_commitment",
    "sentinel_reference", "logical_tick", "timestamp_utc", "residual_type",
    "residual_vector", "evidence_status", "topology_commitment",
    "related_stub_ids", "missing_measurements", "reserved_future_fields",
    "live_gate", "sphere_writes",
)
REQUIRED_FIELDS = {
    "schema_version", "stub_id", "source_modality", "logical_tick",
    "residual_type", "evidence_status", "live_gate", "sphere_writes",
    "commitment",
}


def compute_commitment(record: dict) -> str:
    """Hash only the named fields, excluding the digest and field list itself."""
    fields = record.get("commitment_fields", list(COMMITMENT_FIELDS))
    if (not isinstance(fields, list) or not fields
            or any(not isinstance(key, str) or key not in COMMITMENT_FIELDS
                   for key in fields)
            or len(set(fields)) != len(fields)):
        raise ValueError("commitment_fields must be unique record field names")
    payload = {key: record[key] for key in fields if key in record}
    canonical = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    )
    return hashlib.sha512(canonical.encode("utf-8")).hexdigest()


def validate_record(record: dict) -> bool:
    """Validate schema constraints and integrity; raise ValueError on failure."""
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    allowed = set(COMMITMENT_FIELDS) | {"commitment", "commitment_fields"}
    if not REQUIRED_FIELDS.issubset(record) or set(record) - allowed:
        raise ValueError("missing required fields or unknown record fields")
    if record["schema_version"] != SCHEMA_VERSION:
        raise ValueError("unsupported schema_version")
    if not isinstance(record["stub_id"], str) or not record["stub_id"]:
        raise ValueError("stub_id must be a nonempty string")
    for key, choices in (
        ("source_modality", ("synthetic", "observed_classical", "hypothetical")),
        ("residual_type", ("unresolved", "rejected_transition",
                           "post_separation_drift", "interpretation_claim",
                           "missing_measurement")),
        ("evidence_status", ("UNVERIFIED", "REJECTED", "INCOMPLETE")),
    ):
        if record[key] not in choices:
            raise ValueError(f"invalid {key}")
    tick = record["logical_tick"]
    if type(tick) is not int or tick < 0:
        raise ValueError("logical_tick must be a nonnegative integer")
    if record["live_gate"] != "CLOSED" or record["sphere_writes"] is not False:
        raise ValueError("live_gate must be CLOSED and sphere_writes false")
    for key in ("parent_commitment", "sentinel_reference", "timestamp_utc",
                "topology_commitment"):
        if record.get(key) is not None and not isinstance(record[key], str):
            raise ValueError(f"{key} must be a string or null")
    vector = record.get("residual_vector")
    if vector is not None:
        if not isinstance(vector, list) or any(
            type(value) not in (int, float)
            or (isinstance(value, float) and not math.isfinite(value))
            for value in vector
        ):
            raise ValueError("residual_vector must contain finite numbers or be null")
    for key in ("related_stub_ids", "reserved_future_fields"):
        if key in record and (
            not isinstance(record[key], list)
            or any(not isinstance(value, str) for value in record[key])
        ):
            raise ValueError(f"{key} must be an array of strings")
    missing = record.get("missing_measurements", [])
    if not isinstance(missing, list):
        raise ValueError("missing_measurements must be an array")
    for measurement in missing:
        if (not isinstance(measurement, dict)
                or any(not isinstance(measurement.get(key), str)
                       or not measurement[key].strip()
                       for key in ("name", "missing_reason"))
                or (measurement.get("slot") is not None
                    and not isinstance(measurement["slot"], str))):
            raise ValueError("missing measurements require name and missing_reason")
    if vector is None and not any(
        measurement["name"] == "residual_vector" for measurement in missing
    ):
        raise ValueError("null residual_vector requires an explicit missing reason")
    commitment = record["commitment"]
    if (not isinstance(commitment, str)
            or re.fullmatch(r"[0-9a-f]{128}", commitment) is None
            or commitment != compute_commitment(record)):
        raise ValueError("invalid or mismatched commitment")
    return True


def build_counter_symbol(
    stub_id: str, logical_tick: int = 0, *, source_modality: str = "synthetic",
    residual_type: str = "unresolved", residual_vector: list | None = None,
    evidence_status: str = "UNVERIFIED", **fields,
) -> dict:
    """Build a detached record; absent residuals remain null, never zero-filled."""
    record = {
        "schema_version": SCHEMA_VERSION,
        "stub_id": stub_id,
        "source_modality": source_modality,
        "parent_commitment": None,
        "sentinel_reference": None,
        "logical_tick": logical_tick,
        "timestamp_utc": None,
        "residual_type": residual_type,
        "residual_vector": residual_vector,
        "evidence_status": evidence_status,
        "topology_commitment": None,
        "related_stub_ids": [],
        "missing_measurements": (
            [{"name": "residual_vector", "missing_reason": "residual not supplied"}]
            if residual_vector is None else []
        ),
        "reserved_future_fields": [],
        "live_gate": "CLOSED",
        "sphere_writes": False,
        "commitment_fields": list(COMMITMENT_FIELDS),
    }
    record.update(fields)
    record = copy.deepcopy(record)
    record["commitment"] = compute_commitment(record)
    validate_record(record)
    return record


def append_observation(
    parent: dict, stub_id: str, logical_tick: int, **observation,
) -> dict:
    """Return a new linked record without modifying the parent or any files."""
    validate_record(parent)
    if stub_id == parent["stub_id"]:
        raise ValueError("an observation requires a new stub_id")
    record = copy.deepcopy(parent)
    record.update(copy.deepcopy(observation))
    record.update(
        stub_id=stub_id, logical_tick=logical_tick,
        parent_commitment=parent["commitment"],
    )
    record["commitment"] = compute_commitment(record)
    validate_record(record)
    if logical_tick < parent["logical_tick"]:
        raise ValueError("an observation cannot precede its parent logical_tick")
    if not {"stub_id", "logical_tick", "parent_commitment"}.issubset(
        record.get("commitment_fields", COMMITMENT_FIELDS)
    ):
        raise ValueError("observations must commit their identity, tick, and parent link")
    if record["commitment"] == parent["commitment"]:
        raise ValueError("an observation must have a new commitment")
    return record


def daemon_gate_allows_activation(*args, **kwargs) -> bool:
    """Research records never grant activation, regardless of their contents."""
    return False


def correlate_pair(left: dict, right: dict) -> dict:
    """Describe experimental similarity only, never causation or invariants."""
    validate_record(left)
    validate_record(right)
    a, b = left.get("residual_vector"), right.get("residual_vector")
    distance = None
    if a and b and len(a) == len(b):
        try:
            candidate = math.dist(a, b)
            if math.isfinite(candidate):
                distance = candidate
        except OverflowError:
            pass
    topology_a = left.get("topology_commitment")
    topology_b = right.get("topology_commitment")
    return {
        "experimental": True,
        "status": "insufficient_data" if distance is None else "experimental",
        "tick_lag": right["logical_tick"] - left["logical_tick"],
        "residual_distance": distance,
        "topology_match": (
            topology_a == topology_b
            if topology_a is not None and topology_b is not None else None
        ),
        "source_modalities": [left["source_modality"], right["source_modality"]],
        "observed_pair": (
            left["source_modality"] == right["source_modality"] == "observed_classical"
        ),
        "causation_claim": False,
        "invariant_claim": False,
        "live_gate": "CLOSED",
        "sphere_writes": False,
    }


def write_examples(directory: Path) -> None:
    """Write deterministic synthetic examples without overwriting history."""
    first = build_counter_symbol(
        "cs-synthetic-001", residual_vector=[0.25, -0.5, 0.125],
        topology_commitment="synthetic-topology",
    )
    rejected = append_observation(
        first, "cs-synthetic-002", 1, residual_type="rejected_transition",
        residual_vector=[0.5, -0.25, 0.125], evidence_status="REJECTED",
    )
    missing = append_observation(
        rejected, "cs-synthetic-003", 2, residual_type="missing_measurement",
        residual_vector=None, evidence_status="INCOMPLETE",
        missing_measurements=[{
            "name": "residual_vector", "missing_reason": "synthetic sensor unavailable",
            "slot": "tick-2",
        }],
    )
    directory.mkdir(parents=True, exist_ok=True)
    for record in (first, rejected, missing):
        path = directory / f"{record['stub_id']}.json"
        content = json.dumps(record, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        if path.exists():
            if path.read_text(encoding="utf-8") != content:
                raise ValueError(f"refusing to rewrite historical record: {path}")
        else:
            with path.open("x", encoding="utf-8") as stream:
                stream.write(content)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_mutually_exclusive_group(required=True)
    commands.add_argument("--write-examples", type=Path, metavar="DIRECTORY")
    commands.add_argument("--validate", type=Path, metavar="FILE")
    args = parser.parse_args()
    try:
        if args.write_examples is not None:
            write_examples(args.write_examples)
            print("Wrote three synthetic examples (live_gate=CLOSED, sphere_writes=false)")
        else:
            validate_record(json.loads(args.validate.read_text(encoding="utf-8")))
            print(f"VALID: {args.validate}")
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
