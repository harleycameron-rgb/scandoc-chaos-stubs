#!/usr/bin/env python3
"""Module B — Moiré field engine."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any, Dict, List, Sequence
RULE_VERSION = "scandoc-moire-invariants/v1"
def make_sentinel(payload):
    body=dict(payload); body["sentinel"]=""
    return hashlib.sha512(json.dumps(body, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()).hexdigest()
def load_stubs(d):
    out={}
    for p in sorted(Path(d).glob("stub_phi*.json")):
        data=json.loads(p.read_text()); out[data["id"]]=data
    return out
def _phi(s): return [float(x) for x in s["interference_seed"]["phi"]]
def _drift(s): return [float(x) for x in s["interference_seed"]["detune_drift_vector"]]
def _burn(s): return str(s["interference_seed"]["gate_burn"])
def xor_hex(a,b):
    n=min(len(a),len(b)); a,b=a[:n-(n%2)],b[:n-(n%2)]; out=[]
    for i in range(0,len(a),2): out.append(f"{int(a[i:i+2],16)^int(b[i:i+2],16):02x}")
    return "".join(out)
def field_from_pair(a,b,fid):
    pa,pb=_phi(a),_phi(b); da,db=_drift(a),_drift(b)
    rec={"id":fid,"kind":"moire_field","version":1,"rule_version":RULE_VERSION,"plate":"pair","input_stub_ids":[a["id"],b["id"]],"overlap_phi":[min(pa[i],pb[i]) for i in range(len(pa))],"residue_phi":[abs(pa[i]-pb[i]) for i in range(len(pa))],"drift_mean":[(da[i]+db[i])/2 for i in range(3)],"drift_delta":[da[i]-db[i] for i in range(3)],"gate_xor":xor_hex(_burn(a),_burn(b)),"completeness":"intentionally_incomplete","semantic_payload":None,"sentinel":""}
    rec["sentinel"]=make_sentinel(rec); return rec
def field_full_set(stubs,fid):
    n=len(stubs); pl=len(_phi(stubs[0])); mp=[0.0]*pl; md=[0.0,0.0,0.0]
    for s in stubs:
        p=_phi(s); d=_drift(s)
        for i in range(pl): mp[i]+=p[i]
        for i in range(3): md[i]+=d[i]
    mp=[x/n for x in mp]; md=[x/n for x in md]; re=0.0
    for i in range(0,n-1,2):
        pa,pb=_phi(stubs[i]),_phi(stubs[i+1]); re+=sum(abs(pa[j]-pb[j]) for j in range(pl))
    rec={"id":fid,"kind":"moire_field","version":1,"rule_version":RULE_VERSION,"plate":"full_set","input_stub_ids":[s["id"] for s in stubs],"mean_phi":mp,"mean_drift":md,"pair_residue_energy":re,"stub_count":n,"completeness":"intentionally_incomplete","semantic_payload":None,"sentinel":""}
    rec["sentinel"]=make_sentinel(rec); return rec
def run(stubs_dir,out_dir):
    out_dir=Path(out_dir); out_dir.mkdir(parents=True,exist_ok=True)
    ordered=[load_stubs(stubs_dir)[k] for k in sorted(load_stubs(stubs_dir))]; ids=[]
    for i in range(0,len(ordered)-1,2):
        a,b=ordered[i],ordered[i+1]; fid=f"moire_{a['id']}_{b['id']}"
        rec=field_from_pair(a,b,fid); (out_dir/f"{fid}.json").write_text(json.dumps(rec,indent=2)+"\n"); ids.append(fid)
    full=field_full_set(ordered,"moire_full_set"); (out_dir/"moire_full_set.json").write_text(json.dumps(full,indent=2)+"\n"); ids.append(full["id"])
    man={"module":"B","rule_version":RULE_VERSION,"count":len(ids),"ids":ids,"semantic_payload_policy":"always_null"}; man["sentinel"]=make_sentinel({**man,"sentinel":""})
    (out_dir/"manifest.json").write_text(json.dumps(man,indent=2)+"\n"); return ids
def main():
    p=argparse.ArgumentParser(); p.add_argument("--stubs",default="stubs"); p.add_argument("--out",default="moire-fields"); a=p.parse_args()
    print("Wrote", len(run(Path(a.stubs),Path(a.out))), "→", a.out)
if __name__=="__main__": main()
