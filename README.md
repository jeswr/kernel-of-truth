# A Kernel of Truth

**Research programme: an authoritative, training-free "kernel" of formalised concepts with canonical vector representations, as a component of future LLM/LCM architectures.**

Status: active research, launched 2026-07-07. Lead agent: **Kern** (Claude Fable 5), on behalf of [@jeswr](https://github.com/jeswr).
Coordination thread: [sparq-org/sparq#1683](https://github.com/sparq-org/sparq/issues/1683).

## The hypothesis

If concepts are formalised as structured explications over a small closed basis (NSM's ~65 semantic primes, per the [content-addressed concepts design](https://gist.github.com/jeswr/7499faa6fcbfe8ee1e3192d05e82e9ad)), then the same formal structure that yields a canonical **content-hash** for each concept can also yield a canonical, **deterministically computable vector representation** — a function of the concept's prime-decomposition, requiring no training.

A well-built kernel of such concepts could become central to the architecture of future LLMs, LCMs, and their descendants:

1. **Accuracy** — kernel concepts are built in, not learned; the model can never misunderstand them and their representation can never drift.
2. **Training efficiency** — the model never spends capacity or data learning what the kernel already fixes.
3. **Train/inference efficiency** — dense concept-level I/O: a single concept vector carries what many tokens carry today, both on input and output.
4. **Longer term** — GNN-style non-linear concept input/output, and cheap rules-based inference over kernel concepts inside the architecture as a shortcut past heavy weight evaluation.

Adjacent artefacts: a **phrase→concept mapping layer** (from tokens / token-space regions to fixed kernel concepts), and a **world layer** above the kernel — formally described facts about the state of the world expressed *in terms of* kernel concepts (the kernel holds "a person"; the world layer holds "Jesse as a person").

The near-term goal is a proof-of-concept on small local models rigorous enough to take to a frontier lab.

## Repository layout

| Path | Contents |
|---|---|
| `reports/` | Literature and estate-survey reports (wave 1: sparq estate, deterministic concept vectors, fixed-vectors-in-LLMs evidence, computational NSM + knowledge injection, architecture/PoC harness options) |
| `docs/` | Architecture proposals, the experiment-programme design, the prospectus |
| `poc/` | Proof-of-concept implementations and experiment results |
| `notes/` | Working notes, coordination log |

## Method

Multi-agent research under an empirical-honesty mandate: every load-bearing claim cited; `[established]` / `[claimed]` / `[speculative]` tags kept distinct; negative results reported; the programme is explicitly designed to find out whether the hypothesis is *seriously* right, partially right, or wrong.

## Related work in the estate

- [Content-addressed concepts design](https://gist.github.com/jeswr/7499faa6fcbfe8ee1e3192d05e82e9ad) (PSS agent) — the concept-hash formalism this builds on; prototype `@jeswr/concept-hash`.
- [sparq](https://github.com/sparq-org/sparq) — `sparq-vectors` (structure-aware vectorisation, grounding), RDFC canonicalisation, ZK-over-SPARQL; the `(concept-hash → embedding)` table seam.
