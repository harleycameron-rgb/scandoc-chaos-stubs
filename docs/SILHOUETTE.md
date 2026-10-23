# Silhouette Layer — Specification v1

**Constellation:** SCANDOC / CLOUDBURNER / Daemongate-compatible  
**Rule family:** `scandoc-silhouette-invariants/v1`  
**Status:** Spec + minimal schema (implementable)

---

## 1. Definition

**Silhouette** = the minimal invariant carrier for a sealed unit of structure.

It preserves **outline** (identity, protocol shape, integrity hooks) and deliberately omits **interior** (semantic payload, full dynamics, interpretation).

| Keeps | Drops |
|--------|--------|
| Identity, version, rule pin | Narrative / semantic fill |
| Integrity receipt (sentinel) | Claims about unknown physics |
| Structural predicates | Full time-series or media blobs |
| Pointers to fuller carriers (optional) | Guaranteed future decode |

Silhouette is **not** empty. It is **intentionally incomplete by contract**.

---

## 2. Why it exists

| Problem | Silhouette role |
|---------|-----------------|
| Snapshots rot or drift in meaning | Outline + receipt stay re-checkable |
| Stubs accumulate detail creep | Hard ceiling: no semantic_payload |
| Scale transitions (Daemongate) | Same motif contour at every scale |
| “Uphold over time” | `verify` runs on silhouette alone |

Relation to Module A stubs:

- A **stub** is a kind of silhouette specialized for interference seeds.  
- A **silhouette** is the general layer: any sealed outline that obeys the same completeness policy.

```text
stub_phi*  ⊂  silhouette
```

---

## 3. Hard rules (contract)

1. `completeness` is always `intentionally_incomplete`.
2. `semantic_payload` is always `null`.
3. `sentinel` is SHA-512 over canonical JSON with `sentinel` zeroed (same discipline as stubs).
4. `rule_version` is pinned in the object or in the verifier (never silent).
5. No network I/O required to verify.
6. Optional `carrier_ref` may point to a fuller archive; the silhouette must still verify **without** fetching it.

---

## 4. One-sentence contract

**Silhouette is the sealed, re-verifiable outline of a structure: enough to uphold identity and integrity over time, never enough to smuggle unearned interior meaning.**
