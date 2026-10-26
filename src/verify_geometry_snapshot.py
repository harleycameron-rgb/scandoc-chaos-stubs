#!/usr/bin/env python3
"""Validate the sealed archive's eight-vector helical preview geometry."""
import argparse
import json
import math
from pathlib import Path

APPS = ('tap', 'surface', 'spiritlevel', 'gain', 'habitat', 'time', 'space', 'lineage')

def finite(x):
    return type(x) in (int, float) and math.isfinite(x)

def check(data):
    g = data.get('geometry')
    if not isinstance(g, dict):
        return [('geometry_object', False, 'missing geometry')]
    arms = g.get('arms')
    shape = (type(g.get('arm_count')) is int and g['arm_count'] == 8
             and isinstance(arms, list) and len(arms) == 8
             and finite(g.get('seed')) and finite(g.get('delta')))
    out = [('geometry_shape', shape, 'eight arms and finite seed/delta required')]
    if not shape:
        return out
    for i, arm in enumerate(arms):
        valid = isinstance(arm, dict)
        if valid:
            v = arm.get('vector')
            valid = (arm.get('app') == APPS[i] and type(arm.get('index_0based')) is int
                     and arm['index_0based'] == i and type(arm.get('index_1based')) is int
                     and arm['index_1based'] == i + 1 and isinstance(v, list)
                     and len(v) == 3 and all(finite(x) for x in v))
        if valid:
            theta = g['seed'] + i * g['delta']
            valid = math.isfinite(theta)
            if valid:
                z = 1 - 2 * (i + 0.5) / 8
                r = math.sqrt(1 - z*z)
                expected = (r*math.cos(theta), r*math.sin(theta), z)
                valid = (all(abs(a-b) <= 1e-6 for a,b in zip(v,expected))
                         and abs(math.hypot(*v)-1) <= 1e-6
                         and finite(arm.get('value')) and abs(arm['value']-theta) <= 1e-6
                         and finite(arm.get('curvature')) and abs(arm['curvature']-1/r) <= 1e-6
                         and finite(arm.get('norm')) and abs(arm['norm']-1) <= 1e-6)
        out.append((f'arm_{i+1}', valid, 'ordered app, formula, unit vector and curvature'))
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('path'); args = ap.parse_args()
    try:
        from verify_silhouette import verify_one
        report = verify_one(Path(args.path))
        results = check(json.loads(Path(args.path).read_text()))
        ok = report['upheld'] and all(item[1] for item in results)
    except (OSError, ValueError, TypeError, OverflowError, AttributeError):
        ok = False
    print('all_ok:', ok)
    raise SystemExit(0 if ok else 1)

if __name__ == '__main__': main()
