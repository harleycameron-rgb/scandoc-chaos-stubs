"""Negative/positive tests for the research-only historical comparison topology."""
import copy
import math
import unittest
from src.dual_origin_topology import (
    FIELDS, REFERENCES, compare_model, digest, topology, validate_topology,
)


class DualOriginTests(unittest.TestCase):
    def example(self):
        return {
            "id": "synthetic-p",
            "modality": "synthetic",
            "features": {
                "projectile": "proton",
                "target": "lithium",
                "process": "induced_nuclear_disintegration",
            },
            "evidence_refs": [],
        }

    def test_reference_nodes_distinct(self):
        t = topology()["payload"]["nodes"]
        self.assertEqual(t["A_1932"]["interval"], "1932-04")
        self.assertEqual(t["B_1938"]["interval"], "1938-12")
        self.assertNotEqual(t["A_1932"]["features"], t["B_1938"]["features"])

    def test_omega_has_no_invented_history(self):
        self.assertIsNone(REFERENCES["OMEGA"]["interval"])
        self.assertIsNone(REFERENCES["OMEGA"]["features"])

    def test_deterministic_integrity(self):
        self.assertEqual(topology(), topology())
        self.assertTrue(validate_topology(topology()))
        self.assertEqual(len(topology()["sha512"]), 128)

    def test_tampering_rejected(self):
        t = topology()
        t["payload"]["nodes"]["A_1932"]["interval"] = "1932-01"
        with self.assertRaises(ValueError):
            validate_topology(t)
        t = topology()
        t["sha512"] = "0" * 128
        with self.assertRaises(ValueError):
            validate_topology(t)

    def test_no_shared_mutability(self):
        t = topology()
        t["payload"]["nodes"]["A_1932"]["label"] = "tampered"
        self.assertNotEqual(t["payload"], topology()["payload"])

    def test_matches_descriptive_A_only(self):
        result = compare_model(self.example())["payload"]["comparisons"]
        self.assertEqual(result["A_1932"]["categorical_overlap"], 1.0)
        self.assertEqual(result["B_1938"]["categorical_overlap"], 0.0)
        self.assertEqual(result["OMEGA"]["status"], "indeterminate")

    def test_missing_inputs_are_indeterminate(self):
        candidate = self.example()
        candidate["features"] = {}
        result = compare_model(candidate)["payload"]["comparisons"]
        self.assertIsNone(result["A_1932"]["categorical_overlap"])
        self.assertEqual(result["A_1932"]["status"], "insufficient_data")

    def test_missing_observational_evidence_rejected(self):
        c = self.example()
        c["modality"] = "observed_classical"
        with self.assertRaises(ValueError):
            compare_model(c)
        c["evidence_refs"] = ["https://example.invalid/record"]
        self.assertFalse(compare_model(c)["payload"]["claims"]["existence_established"])

    def test_refuses_nonfinite_or_unknown_features(self):
        for bad in [float("nan"), 3, None, ""]:
            c = self.example()
            c["features"] = {"projectile": bad}
            with self.assertRaises(ValueError):
                compare_model(c)
        c = self.example()
        c["features"] = {"new_invented_metric": "foo"}
        with self.assertRaises(ValueError):
            compare_model(c)

    def test_no_physical_or_gate_claim(self):
        r = compare_model(self.example())["payload"]
        self.assertEqual(r["gate"]["live_gate"], "CLOSED")
        self.assertFalse(r["gate"]["sphere_writes"])
        self.assertFalse(any(r["claims"].values()))

    def test_comparison_output_hash_changes_with_input(self):
        first = compare_model(self.example())
        c = self.example()
        c["features"]["target"] = "uranium"
        second = compare_model(c)
        self.assertNotEqual(first["sha512"], second["sha512"])

    def test_input_not_mutated(self):
        m = self.example()
        before = copy.deepcopy(m)
        compare_model(m)
        self.assertEqual(before, m)

    def test_unknown_modality_rejected(self):
        c = self.example()
        c["modality"] = "quantum_confirmed"
        with self.assertRaises(ValueError):
            compare_model(c)


if __name__ == "__main__":
    unittest.main()
