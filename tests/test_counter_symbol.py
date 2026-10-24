import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.counter_symbol import (
    SCHEMA_VERSION,
    append_observation,
    build_counter_symbol,
    compute_commitment,
    correlate_pair,
    daemon_gate_allows_activation,
    validate_record,
)


class CounterSymbolTests(unittest.TestCase):
    def test_determinism(self):
        first = build_counter_symbol("test", residual_vector=[1, 2])
        self.assertEqual(first, build_counter_symbol("test", residual_vector=[1, 2]))
        self.assertEqual(first["schema_version"], SCHEMA_VERSION)
        self.assertTrue(validate_record(first))
        self.assertEqual(
            compute_commitment(first), compute_commitment(dict(reversed(list(first.items()))))
        )

    def test_digest_changes_with_committed_data(self):
        record = build_counter_symbol("test", residual_vector=[1])
        changed = copy.deepcopy(record)
        changed["residual_vector"] = [2]
        self.assertNotEqual(compute_commitment(record), compute_commitment(changed))
        with self.assertRaises(ValueError):
            validate_record(changed)

    def test_commitment_fields_only(self):
        record = build_counter_symbol("é", commitment_fields=["stub_id"])
        expected = hashlib.sha512('{"stub_id":"é"}'.encode("utf-8")).hexdigest()
        self.assertEqual(record["commitment"], expected)
        record["timestamp_utc"] = "2026-01-01T00:00:00Z"
        record["commitment"] = "ignored by compute"
        self.assertEqual(compute_commitment(record), expected)
        for fields in (["commitment"], ["unknown"], ["stub_id", "stub_id"], "stub_id"):
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                compute_commitment(dict(record, commitment_fields=fields))

    def test_append_is_immutable_and_linked(self):
        vector = [1, 2]
        parent = build_counter_symbol("parent", residual_vector=vector)
        original = copy.deepcopy(parent)
        child = append_observation(parent, "child", 1)
        self.assertEqual(parent, original)
        self.assertEqual(child["parent_commitment"], parent["commitment"])
        self.assertNotEqual(child["commitment"], parent["commitment"])
        child["residual_vector"][0] = 99
        vector[0] = 42
        self.assertEqual(parent, original)
        with self.assertRaises(ValueError):
            append_observation(parent, "parent", 1)
        partial = build_counter_symbol(
            "partial", residual_vector=[1], commitment_fields=["residual_vector"],
        )
        with self.assertRaises(ValueError):
            append_observation(partial, "child", 1)

    def test_missing_measurements_are_explicit(self):
        record = build_counter_symbol(
            "missing", residual_type="missing_measurement", evidence_status="INCOMPLETE",
            missing_measurements=[{"name": "residual_vector", "missing_reason": "offline"}],
        )
        self.assertIsNone(record["residual_vector"])
        self.assertTrue(validate_record(record))
        default = build_counter_symbol("default")
        self.assertEqual(default["missing_measurements"][0]["name"], "residual_vector")
        unexplained = dict(default, missing_measurements=[])
        unexplained["commitment"] = compute_commitment(unexplained)
        with self.assertRaises(ValueError):
            validate_record(unexplained)
        for missing in ([{"name": "sensor"}], [{"missing_reason": "offline"}],
                        [{"name": "", "missing_reason": "offline"}], None, [],
                        [{"name": "unrelated", "missing_reason": "offline"}]):
            with self.subTest(missing=missing), self.assertRaises(ValueError):
                build_counter_symbol("bad", missing_measurements=missing)

    def test_nonfinite_residuals_rejected(self):
        for value in (float("nan"), float("inf"), -float("inf"), True, "0"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                build_counter_symbol("bad", residual_vector=[value])
            record = build_counter_symbol("test")
            record["residual_vector"] = [value]
            with self.assertRaises(ValueError):
                validate_record(record)

    def test_negative_and_invalid_ticks_rejected(self):
        for tick in (-1, 0.5, True, "0"):
            with self.subTest(tick=tick), self.assertRaises(ValueError):
                build_counter_symbol("bad", logical_tick=tick)
        self.assertTrue(validate_record(build_counter_symbol("zero", logical_tick=0)))
        parent = build_counter_symbol("parent", logical_tick=10)
        with self.assertRaises(ValueError):
            append_observation(parent, "child", 9)

    def test_gates_permanently_closed(self):
        record = build_counter_symbol("closed")
        self.assertEqual(record["live_gate"], "CLOSED")
        self.assertIs(record["sphere_writes"], False)
        for value in (None, record, {"live_gate": "OPEN", "sphere_writes": True}):
            self.assertIs(daemon_gate_allows_activation(value), False)
        for changes in ({"live_gate": "OPEN"}, {"sphere_writes": True},
                        {"sphere_writes": 0}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                build_counter_symbol("bad", **changes)
            with self.assertRaises(ValueError):
                append_observation(record, "bad", 1, **changes)

    def test_correlation_insufficient_data(self):
        left = build_counter_symbol("left")
        for vector in (None, [], [1], [1, 2, 3]):
            right = build_counter_symbol("right", residual_vector=vector)
            result = correlate_pair(left, right)
            self.assertEqual(result["status"], "insufficient_data")
            self.assertIsNone(result["residual_distance"])
            self.assertIsNone(result["topology_match"])
        left = build_counter_symbol("left", residual_vector=[1, 2])
        right = build_counter_symbol("right", residual_vector=[1])
        self.assertEqual(correlate_pair(left, right)["status"], "insufficient_data")

    def test_synthetic_vs_observed_correlation(self):
        left = build_counter_symbol(
            "left", logical_tick=2, residual_vector=[0, 0], topology_commitment="shape",
        )
        right = build_counter_symbol(
            "right", logical_tick=5, residual_vector=[3, 4],
            topology_commitment="shape", source_modality="observed_classical",
        )
        result = correlate_pair(left, right)
        self.assertEqual(result["tick_lag"], 3)
        self.assertEqual(result["residual_distance"], 5)
        self.assertIs(result["topology_match"], True)
        self.assertIs(result["experimental"], True)
        self.assertIs(result["observed_pair"], False)
        self.assertEqual(result["source_modalities"], ["synthetic", "observed_classical"])
        self.assertIs(result["causation_claim"], False)
        self.assertIs(result["invariant_claim"], False)
        observed = build_counter_symbol(
            "observed", residual_vector=[1, 1], topology_commitment="other",
            source_modality="observed_classical",
        )
        self.assertIs(correlate_pair(observed, right)["observed_pair"], True)
        self.assertIs(correlate_pair(observed, right)["topology_match"], False)

    def test_rejected_transition_remains_auditable(self):
        parent = build_counter_symbol("parent", residual_vector=[1])
        rejected = append_observation(
            parent, "rejected", 1, residual_type="rejected_transition",
            evidence_status="REJECTED", residual_vector=[2],
        )
        self.assertTrue(validate_record(parent))
        self.assertTrue(validate_record(rejected))
        self.assertEqual(rejected["parent_commitment"], parent["commitment"])
        self.assertEqual(rejected["evidence_status"], "REJECTED")
        self.assertEqual(rejected["residual_type"], "rejected_transition")
        self.assertIs(daemon_gate_allows_activation(rejected), False)
        for changes in ({"extra": 1}, {"source_modality": "observed"},
                        {"evidence_status": "VERIFIED"}, {"stub_id": ""},
                        {"residual_type": "accepted"}, {"schema_version": "other"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_record(dict(rejected, **changes))

    def test_cli_examples_and_validation(self):
        script = Path(__file__).resolve().parents[1] / "src" / "counter_symbol.py"

        def run(*args):
            return subprocess.run(
                [sys.executable, "-B", str(script), *map(str, args)],
                capture_output=True, text=True,
            )

        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(run("--write-examples", directory).returncode, 0)
            paths = sorted(Path(directory).glob("*.json"))
            self.assertEqual(len(paths), 3)
            contents = [path.read_bytes() for path in paths]
            for path in paths:
                record = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(record["source_modality"], "synthetic")
                self.assertEqual(run("--validate", path).returncode, 0)
            self.assertEqual(run("--write-examples", directory).returncode, 0)
            self.assertEqual(contents, [path.read_bytes() for path in paths])
            paths[0].write_text("{}\n", encoding="utf-8")
            self.assertEqual(run("--validate", paths[0]).returncode, 1)
            self.assertEqual(run("--write-examples", directory).returncode, 1)
            self.assertEqual(paths[0].read_text(encoding="utf-8"), "{}\n")
            paths[0].write_text("{", encoding="utf-8")
            self.assertEqual(run("--validate", paths[0]).returncode, 1)
            self.assertEqual(run("--validate", Path(directory) / "absent.json").returncode, 1)


if __name__ == "__main__":
    unittest.main()
