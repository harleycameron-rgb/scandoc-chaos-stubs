#!/usr/bin/env python3
"""Verify Module B moiré fields."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
RULE_VERSION="scandoc-moire-invariants/v1"
def make_sentinel(payload):
    body=dict(payload); body["sentinel"]=""
    return hashlib.sha512(json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def check(data):
    out=[]
    def ok(n): out.append({"name":n,"pass":True})
    def fail(n,d): out.append({"name":n,"pass":False,"detail":d})
    if data.get("kind")=="moire_field": ok("kind")
    else: fail("kind",str(data.get("kind")))
    if data.get("rule_version")==RULE_VERSION: ok("rule_version")
    else: fail("rule_version",str(data.get("rule_version")))
    if data.get("completeness")=="intentionally_incomplete": ok("completeness")
    else: fail("completeness","")
    if data.get("semantic_payload") is None: ok("semantic_payload_null")
    else: fail("semantic_payload_null","non-null")
    ids=data.get("input_stub_ids")
    if isinstance(ids,list) and len(ids)>=2: ok("inputs")
    else: fail("inputs","")
    if data.get("plate")=="pair":
        for k in ("overlap_phi","residue_phi"):
            if isinstance(data.get(k),list) and len(data[k])==7: ok(k)
            else: fail(k,"")
    elif data.get("plate")=="full_set":
        if isinstance(data.get("mean_phi"),list) and len(data["mean_phi"])==7: ok("mean_phi")
        else: fail("mean_phi","")
    else: fail("plate",str(data.get("plate")))
    return out
def verify_one(path):
    data=json.loads(Path(path).read_text())
    stored=data.get("sentinel"); computed=make_sentinel(data)
    inv=check(data); upheld=(stored==computed) and all(i["pass"] for i in inv)
    return {"path":str(path),"upheld":upheld,"integrity":stored==computed}
def main():
    p=argparse.ArgumentParser(); p.add_argument("path"); a=p.parse_args(); path=Path(a.path)
    files=sorted(path.glob("moire_*.json")) if path.is_dir() else [path]
    reps=[verify_one(f) for f in files]; u=sum(1 for r in reps if r["upheld"])
    print(f"upheld: {u}/{len(reps)}")
    for r in reps: print(" ", "UPHELD" if r["upheld"] else "FAIL", r["path"])
    raise SystemExit(0 if u==len(reps) and reps else 1)
if __name__=="__main__": main()
