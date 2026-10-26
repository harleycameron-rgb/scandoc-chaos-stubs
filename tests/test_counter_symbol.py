#!/usr/bin/env python3
import copy, json, math, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from counter_symbol import (
    CounterSymbolError, append_observation, build_counter_symbol,
    compute_commitment, correlate_pair, daemon_gate_allows_activation, validate_record,
)
class T(unittest.TestCase):
    def test_01_deterministic(self):
        a=build_counter_symbol(stub_id="t1", residual_vector=[1.,2.,3.])
        b=build_counter_symbol(stub_id="t1", residual_vector=[1.,2.,3.])
        self.assertEqual(a["commitment"], b["commitment"])
    def test_02_digest_changes(self):
        a=build_counter_symbol(stub_id="t1", residual_vector=[1.,0.])
        b=build_counter_symbol(stub_id="t1", residual_vector=[1.,0.1])
        self.assertNotEqual(a["commitment"], b["commitment"])
    def test_03_append_only(self):
        p=build_counter_symbol(stub_id="p", residual_vector=[0.5]); pb=json.dumps(p, sort_keys=True)
        c=append_observation(p, new_stub_id="c", residual_type="rejected_transition", residual_vector=[0.6])
        self.assertEqual(json.dumps(p, sort_keys=True), pb)
        self.assertEqual(c["parent_commitment"], p["commitment"])
    def test_04_missing_not_zero(self):
        r=build_counter_symbol(stub_id="m", residual_vector=None, residual_type="missing_measurement",
            missing_measurements=[{"name":"x","missing_reason":"n"}], evidence_status="INCOMPLETE")
        self.assertIsNone(r["residual_vector"])
    def test_05_reject_bad(self):
        with self.assertRaises(CounterSymbolError): build_counter_symbol(stub_id="b", residual_vector=[math.nan])
        with self.assertRaises(CounterSymbolError): build_counter_symbol(stub_id="b", logical_tick=-1)
    def test_06_gate_closed(self):
        r=build_counter_symbol(stub_id="g")
        self.assertEqual(r["live_gate"], "CLOSED"); self.assertFalse(daemon_gate_allows_activation(r))
        bad=copy.deepcopy(r); bad["live_gate"]="OPEN"
        with self.assertRaises(CounterSymbolError): validate_record(bad)
    def test_07_no_geometry_api(self):
        r=build_counter_symbol(stub_id="geo"); self.assertNotIn("tentacles", r)
    def test_08_no_temporal_rewrite(self):
        r=build_counter_symbol(stub_id="tmp"); self.assertNotIn("past", r)
    def test_09_correlation_safe(self):
        a=build_counter_symbol(stub_id="a", residual_vector=[1.,0.], logical_tick=0)
        b=build_counter_symbol(stub_id="b", residual_vector=[0.,1.], logical_tick=100)
        c=correlate_pair(a,b,max_tick_lag=5)
        self.assertTrue(c["insufficient_observations"]); self.assertFalse(c["causation_claimed"])
    def test_10_modality(self):
        s=build_counter_symbol(stub_id="s", source_modality="synthetic")
        o=build_counter_symbol(stub_id="o", source_modality="observed_classical")
        self.assertNotEqual(s["commitment"], o["commitment"])
    def test_11_rejected_auditable(self):
        p=build_counter_symbol(stub_id="acc")
        r=append_observation(p, new_stub_id="rej", residual_type="rejected_transition", residual_vector=[0.])
        self.assertEqual(r["residual_type"], "rejected_transition"); validate_record(r)
    def test_12_commitment_fields(self):
        r=build_counter_symbol(stub_id="cf")
        self.assertEqual(r["commitment"], compute_commitment(r))
if __name__=="__main__": unittest.main()
