import copy
import json
import tempfile
import unittest
from pathlib import Path

from src import counter_symbol as cs


def make(**kw):
    args = dict(record_id="r1", logical_tick=0, vector=[0.1, 0.2],
                measurements=[{"name": "m", "value": 1.0, "expected": 0.5}])
    args.update(kw)
    return cs.build_counter_symbol(**args)


class CounterSymbolTests(unittest.TestCase):
    def test_valid_record(self):
        self.assertEqual(make()["schema"], "scandoc-counter-symbol/0.1")
        self.assertEqual(cs.validate_record(make()), [])

    def test_commitment_is_sha512(self):
        self.assertEqual(len(make()["commitment"]), 128)

    def test_commitment_fields_only(self):
        r = make()
        r2 = cs.append_observation(r, {"logical_tick": 1})
        self.assertEqual(r["commitment"], r2["commitment"])
        self.assertEqual(cs.validate_record(r2), [])

    def test_tamper_detected(self):
        r = make()
        r["vector"][0] = 0.9
        self.assertIn("commitment mismatch", cs.validate_record(r))

    def test_append_only(self):
        r = make()
        before = copy.deepcopy(r)
        r2 = cs.append_observation(r, {"logical_tick": 1})
        self.assertEqual(r, before)
        self.assertEqual(len(r2["observations"]), 1)
        with self.assertRaises(cs.CounterSymbolError):
            cs.append_observation(r2, {"logical_tick": 0})

    def test_gates(self):
        r = make()
        self.assertFalse(cs.daemon_gate_allows_activation())
        self.assertFalse(r["gates"]["daemon_gate_allows_activation"])
        self.assertEqual(r["gates"]["live_gate"], "CLOSED")
        self.assertFalse(r["gates"]["sphere_writes"])
        r["gates"]["live_gate"] = "OPEN"
        self.assertTrue(cs.validate_record(r))

    def test_reject_non_finite(self):
        for bad in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(cs.CounterSymbolError):
                make(vector=[0.1, bad])

    def test_reject_negative_tick(self):
        with self.assertRaises(cs.CounterSymbolError):
            make(logical_tick=-1)

    def test_missing_requires_reason(self):
        with self.assertRaises(cs.CounterSymbolError):
            make(measurements=[{"name": "m"}])
        r = make(measurements=[{"name": "m", "missing_reason": "offline"}])
        self.assertEqual(cs.validate_record(r), [])

    def test_no_zero_fill_residuals(self):
        r = make(measurements=[{"name": "m", "missing_reason": "offline"}])
        self.assertEqual(r["residuals"], {})

    def test_correlate_pair_experimental(self):
        out = cs.correlate_pair(make(vector=[1, 2, 3]), make(record_id="r2", vector=[2, 4, 6]))
        self.assertTrue(out["experimental"])
        self.assertFalse(out["causation_claim"])
        self.assertAlmostEqual(out["pearson_r"], 1.0)

    def test_cli_examples(self):
        with tempfile.TemporaryDirectory() as d:
            paths = cs.write_examples(Path(d))
            self.assertEqual(len(paths), 3)
            for p in paths:
                self.assertEqual(cs.validate_record(json.loads(p.read_text())), [])


if __name__ == "__main__":
    unittest.main()
