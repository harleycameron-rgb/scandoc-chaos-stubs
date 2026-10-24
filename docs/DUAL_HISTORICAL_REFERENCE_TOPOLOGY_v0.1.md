# Dual historical reference topology v0.1

**Status:** research-only synthetic/categorical comparison adapter. Not a nuclear physics model, not a historical proof of universal first occurrence, and not an authenticated Sentinel or quantum substrate.

## Reference nodes

| Node | Historical label | Granularity | Evidence |
| --- | --- | --- | --- |
| A_1932 | Cockcroft–Walton accelerator-driven proton bombardment of lithium nuclei | April 1932 | [Science Museum Group](https://collection.sciencemuseumgroup.org.uk/objects/co5130/cockroft-and-waltons-accelerator); [Nature original letter](https://www.nature.com/articles/129649a0) |
| B_1938 | Hahn–Strassmann neutron-induced uranium fission findings, subsequently explained by Meitner and Frisch | December 1938 | [Max Planck Institute for Chemistry](https://www.mpic.de/4469988/die-entdeckung-der-kernspaltung) |
| OMEGA | Earliest technological nuclear-splitting event in *total* history | Unknown | No observation; no date, place, actor, mechanism or identity claim |

**A and B are distinct historical experimental mechanisms.** This adapter does not assign universal priority to either. In particular, the 1938 fission discovery is not a second date for the 1932 proton-driven lithium disintegration. The status of hypothetical Ω relative to A or B is indeterminate; absence of counterevidence is not support for equivalence.

## Contract

The record contains three typed nodes, three edges, source URLs, month-level time bins, a version, and **CLOSED** gate / no sphere writes / UNVERIFIED trust. The SHA-512 digest commits a canonical, domain-separated byte representation. It verifies content equality under the pinned rules, **not** independent authenticity, historical completeness, experimental validity or accessibility of a dynamic topology.

The separate `compare_model` method accepts one candidate record and explicit qualitative `features` in four named slots: `projectile`, `target`, `process`, and `technology`. It returns the count of declared exact categorical matches with each node, reporting missing features as insufficient data. **These are descriptive matches only**, not scientific distances or similarity of mathematical dynamics. It does not verify external evidence URLs. Observed-classical submissions must at least declare one evidence reference, which is necessary but not sufficient for independent corroboration. No assertion of a new physical model or a quantum-chaos substrate is made.

Comparisons against Ω always yield `indeterminate`; never zero-similarity, perfect similarity, or a guessed timestamp. Every derived record refers to the versioned A/B/Ω reference digest. None confers authorization for DaemonGate activation.

## Design boundary for future meaningful comparisons

If comparing inferred dynamics or independent models (e.g. Scandoc's parabola gates, Sentinel, Chaos Stubs), develop separately validated common observables, units, measurement uncertainty, time alignment, transition rules, negative controls and operator definitions. A categorical analogy between experimental setups does **not** establish shared physics or model existence. Preserve the distinction between provenance graph, geometric state and causal mechanism. A truly physical similarity measure needs independent experimental evidence.

## Examples

```python
from src.dual_origin_topology import topology, compare_model
reference = topology()
candidate = {
    "id": "illustrative-proton-lithium",
    "modality": "synthetic",
    "features": {"projectile": "proton", "target": "lithium"},
    "evidence_refs": [],
}
result = compare_model(candidate)
assert result["payload"]["comparisons"]["OMEGA"]["status"] == "indeterminate"
assert result["payload"]["gate"]["live_gate"] == "CLOSED"
```

Tests: `python -m unittest discover -s tests -p 'test_dual_origin_topology.py' -v`.

## Integration notes

- Add as an **optional** Chaos Stub comparison adapter; no second Sentinel genesis event.
- Do not add a seventh spatial leg. The six launch legs and separate temporal references are unaffected.
- Proposed future work: align with Anticipatory Chaos Stub contract, add provenance graph references, declare comparable empirical operators, and inspect PRs #5–#7 before merging any new stub adapters.
- Existing runtime, HTML apps, Vercel deployment, gate writer and production routes are unchanged.
