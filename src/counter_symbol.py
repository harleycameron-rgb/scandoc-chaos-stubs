#!/usr/bin/env python3
"""Counter-Symbol Chaos Stub v0.1 — residual research records. Gate CLOSED."""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
SCHEMA_VERSION = "scandoc-counter-symbol/0.1"
COMMITMENT_FIELDS = ("schema_version","stub_id","source_modality","parent_commitment","sentinel_reference","logical_tick","timestamp_utc","residual_type","residual_vector","evidence_status","topology_commitment","related_stub_ids","missing_measurements","reserved_future_fields","live_gate","sphere_writes")
class CounterSymbolError(ValueError): pass
def _canonical(record):
    body = {k: record.get(k) for k in COMMITMENT_FIELDS}
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
def compute_commitment(record):
    return hashlib.sha512(_canonical(record).encode()).hexdigest()
def _vec(vec, name):
    if vec is None: return None
    out=[]
    for i,x in enumerate(vec):
        if not isinstance(x,(int,float)) or isinstance(x,bool): raise CounterSymbolError(f"{name}[{i}] bad")
        fx=float(x)
        if not math.isfinite(fx): raise CounterSymbolError(f"{name}[{i}] nonfinite")
        out.append(fx)
    return out
def validate_record(record, require_commitment_match=True):
    if record.get("schema_version")!=SCHEMA_VERSION: raise CounterSymbolError("schema")
    if not record.get("stub_id"): raise CounterSymbolError("stub_id")
    if record.get("source_modality") not in {"synthetic","observed_classical","hypothetical"}: raise CounterSymbolError("modality")
    tick=record.get("logical_tick")
    if not isinstance(tick,int) or isinstance(tick,bool) or tick<0: raise CounterSymbolError("tick")
    if record.get("residual_type") not in {"unresolved","rejected_transition","post_separation_drift","interpretation_claim","missing_measurement"}: raise CounterSymbolError("residual_type")
    if record.get("evidence_status") not in {"UNVERIFIED","REJECTED","INCOMPLETE"}: raise CounterSymbolError("evidence")
    if record.get("live_gate")!="CLOSED": raise CounterSymbolError("gate")
    if record.get("sphere_writes") is not False: raise CounterSymbolError("writes")
    _vec(record.get("residual_vector"),"residual_vector")
    for i,item in enumerate(record.get("missing_measurements") or []):
        if not item.get("name") or not item.get("missing_reason"): raise CounterSymbolError(f"missing[{i}]")
    if require_commitment_match:
        if record.get("commitment")!=compute_commitment(record): raise CounterSymbolError("commitment")
def build_counter_symbol(*, stub_id, source_modality="synthetic", residual_type="unresolved", residual_vector=None, logical_tick=0, timestamp_utc=None, parent_commitment=None, sentinel_reference=None, topology_commitment=None, related_stub_ids=None, missing_measurements=None, reserved_future_fields=None, evidence_status="UNVERIFIED"):
    rec={"schema_version":SCHEMA_VERSION,"stub_id":stub_id,"source_modality":source_modality,"parent_commitment":parent_commitment,"sentinel_reference":sentinel_reference,"logical_tick":logical_tick,"timestamp_utc":timestamp_utc,"residual_type":residual_type,"residual_vector":_vec(residual_vector,"residual_vector"),"evidence_status":evidence_status,"topology_commitment":topology_commitment,"related_stub_ids":list(related_stub_ids or []),"missing_measurements":list(missing_measurements or []),"reserved_future_fields":list(reserved_future_fields or []),"live_gate":"CLOSED","sphere_writes":False,"commitment_fields":list(COMMITMENT_FIELDS),"commitment":""}
    rec["commitment"]=compute_commitment(rec); validate_record(rec); return rec
def daemon_gate_allows_activation(record):
    validate_record(record); return False
def append_observation(parent, *, new_stub_id, residual_type, residual_vector=None, missing_measurements=None, logical_tick=None):
    validate_record(parent)
    tick=logical_tick if logical_tick is not None else int(parent["logical_tick"])+1
    return build_counter_symbol(stub_id=new_stub_id, source_modality=parent["source_modality"], residual_type=residual_type, residual_vector=residual_vector, logical_tick=tick, parent_commitment=parent["commitment"], sentinel_reference=parent.get("sentinel_reference"), topology_commitment=parent.get("topology_commitment"), related_stub_ids=list(parent.get("related_stub_ids") or [])+[parent["stub_id"]], missing_measurements=missing_measurements)
def correlate_pair(a,b,*,max_tick_lag=10**9):
    validate_record(a); validate_record(b)
    lag=abs(int(a["logical_tick"])-int(b["logical_tick"])); insuf=lag>max_tick_lag
    va,vb=a.get("residual_vector"),b.get("residual_vector")
    ok=isinstance(va,list) and isinstance(vb,list) and len(va)==len(vb)>0
    dist=math.sqrt(sum((float(va[i])-float(vb[i]))**2 for i in range(len(va)))) if ok and not insuf else None
    result={"schema_version":"scandoc-counter-symbol-correlation/0.1","kind":"experimental_correlation","input_stub_ids":[a["stub_id"],b["stub_id"]],"input_commitments":[a["commitment"],b["commitment"]],"tick_lag":lag,"insufficient_observations":insuf,"residual_compatible":ok,"residual_distance":dist,"topology_version_match":a.get("topology_commitment") is not None and a.get("topology_commitment")==b.get("topology_commitment"),"shared_related_stub_ids":sorted(set(a.get("related_stub_ids") or [])&set(b.get("related_stub_ids") or [])),"missing_data_present":bool(a.get("missing_measurements") or b.get("missing_measurements")),"causation_claimed":False,"invariant_claimed":False,"live_gate":"CLOSED","sphere_writes":False,"evidence_status":"UNVERIFIED"}
    result["commitment"]=hashlib.sha512(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest(); return result
def write_example_records(out_dir):
    out_dir=Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True); ids=[]
    r1=build_counter_symbol(stub_id="cs-synthetic-001", residual_vector=[0.1,-0.2,0.05], missing_measurements=[{"name":"post_separation_sample","missing_reason":"not_acquired"}], related_stub_ids=["stub_phi01"], reserved_future_fields=["quantum_slot_v1"])
    (out_dir/f"{r1['stub_id']}.json").write_text(json.dumps(r1,indent=2)+"\n"); ids.append(r1["stub_id"])
    r2=append_observation(r1, new_stub_id="cs-synthetic-001-b", residual_type="rejected_transition", residual_vector=[0.1,-0.2,0.06])
    (out_dir/f"{r2['stub_id']}.json").write_text(json.dumps(r2,indent=2)+"\n"); ids.append(r2["stub_id"])
    r3=build_counter_symbol(stub_id="cs-synthetic-missing-only", residual_type="missing_measurement", residual_vector=None, missing_measurements=[{"name":"leg_median","missing_reason":"six_leg_separation_not_run"}], evidence_status="INCOMPLETE")
    (out_dir/f"{r3['stub_id']}.json").write_text(json.dumps(r3,indent=2)+"\n"); ids.append(r3["stub_id"]); return ids
def main():
    p=argparse.ArgumentParser(); p.add_argument("--write-examples",default=""); p.add_argument("--validate",default=""); a=p.parse_args()
    if a.write_examples: print("wrote", write_example_records(Path(a.write_examples)))
    if a.validate:
        d=json.loads(Path(a.validate).read_text()); validate_record(d); print("OK", d["stub_id"], d["live_gate"])
if __name__=="__main__": main()
