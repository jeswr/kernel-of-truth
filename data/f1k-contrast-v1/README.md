# f1k-contrast-v1 — the certified F1-K kernel-vs-dictionary contrast corpus

Byte-identical copy of `poc/f1k-askability/contrast/` (designer-31 askability
screen, 2026-07-15, $0/blind), promoted to a pinned corpus for the F1-K
REVISION-6 freeze (maintainer-approved geometry C=96 / n=1573 / mu*=+4.09 pts
/ R=(1,3,1), 2026-07-15).

Contents: one directory per concept, `<rank>-<slug>/`:

- `kernel.txt`        — the kernel explication text (the K-arm carrier text
                        and the d3-text prompt payload), UTF-8 exact bytes.
- `kernel.ast.json`   — the kot-ast/1 explication, JCS-canonical bytes.
- `dictionary.txt`    — the VERBATIM matched WordNet-3.1 dictionary gloss for
                        the same synset (the d2 knull payload).

Ranks 001–096 = the frozen selected 96 concepts (45 kernel-v0 + 51 kernel-v1);
ranks 097–116 = the fixed 20-deep reserve (drawn only under the pre-declared
substitution rule; any use is a logged protocol amendment).

Certification (condition iv, kernel-vs-generic distinctness — screen Part 2,
`poc/f1k-askability/reports/{distinctness,hash}-report.json`): per-pair
sha256 differ; NLD >= 0.20 (min 0.387, median 0.738); production prepend
render on every assigned item gives prompt-hash-difference rate 1.00 with
outside-payload differences 0. Redacted-input hash frozen before screening:
4f7cf1c6a5b5e92655581ba901ea35ce3c6781e3f5279a7b4181b2d4bafc0359.

VALIDITY BAR (condition i, stated so it cannot be overclaimed): these
explications come from the existing kernel-v0 (explicator-authored) and
kernel-v1 (pipeline-minted, stage A) records. Both passed the encoder/
validator loop and LLM-proxy checks only — NO human fidelity validation of
explication-to-concept faithfulness exists. They are a PROXY instrument;
any F1-K PASS that rides on them is PROXY-PROVISIONAL until a human
fidelity pass over these 96 texts (ASM-2373).

Pinned in `registry/experiments/f1k.json` `pins.corpus_hashes` under
kot-corpus-hash/1 (tools/registry/corpus-pin.py). Do not edit in place —
any change is a new corpus version + re-freeze.
