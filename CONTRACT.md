# CONTRACT — scandoc-chaos-stubs

## Hard rules

1. **No semantic payload.** `semantic_payload` is always `null`.
2. **Intentionally incomplete.** `completeness` is always `intentionally_incomplete`.
3. **Sentinel required.** Every stub JSON must include a SHA-512 `sentinel` over its canonical form (sorted keys, no whitespace variance).
4. **No runtime filesystem side effects** beyond explicit generation of stub files when the factory is invoked with `--out`.
5. **Quantum-access is dormant.** Files under `quantum-access/` are placeholders only; they do not implement entanglement or decoding.
6. **No claim of physical quantum readout.** Detune and moiré layers are classical parameter and structure tools until a future module is explicitly activated.

## Allowed content

- Interference seeds (φ sequences)
- Gate burn signatures
- Detune drift vectors
- Invariant residue markers
- Manifests and schemas
- Factory / verify code

## Forbidden

- Storing user text, model answers, or narrative semantics inside stubs
- Claiming a stub "contains" a future timeline as fact
- Network calls from the factory
- Silent mutation of existing stubs without a new version field
