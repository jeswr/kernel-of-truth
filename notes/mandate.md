# Programme mandate (from the maintainer, 2026-07-07)

Paraphrase of the commissioning brief from @jeswr; the hypothesis in README.md is the canonical statement.

## Inputs

1. **The concept-formalisation paper** — [gist 7499faa6…](https://gist.github.com/jeswr/7499faa6fcbfe8ee1e3192d05e82e9ad): content-addressed concepts, NSM-grounded explication grammar (profile-1), node-level hashing with SCC handling, the signed `(concept-hash → embedding)` annotation idea (§9). Authored by the PSS agent; working prototype `@jeswr/concept-hash` exists.
2. **sparq** — [sparq-org/sparq](https://github.com/sparq-org/sparq): node vectorisation and experiments with low-level ontologies (`sparq-vectors`, structure-aware-vectorisation design record), RDFC canonicalisation, ZK-over-SPARQL.
3. **Coordination** — [sparq-org/sparq#1683](https://github.com/sparq-org/sparq/issues/1683). Kern's introduction + takeover announcement: [comment](https://github.com/sparq-org/sparq/issues/1683#issuecomment-4898788294). PSS offline until ~02:00 GMT 2026-07-07; Kern has taken over the research streams PSS announced there. Do not block on other agents.

## The commission

Launch a research programme that:
1. understands the state-of-the-art literature in the relevant spaces;
2. develops properly worked-out architecture proposals from the maintainer's high-level ideas;
3. designs a small research programme that can prove the concept on small local models;
4. implements that programme.

Goal: prove the concept well enough to approach a frontier lab (OpenAI / Anthropic scale) to take it forward in a very large system.

## Maintainer's framing notes (recorded for fidelity)

- Not locked into NSM: other concept bases are admissible where needed (foundational mathematics, physical units).
- The kernel is small and definitional/abstract ("a person"); a larger layer above holds formally described world-facts ("Jesse as a person": birth, parents, …). For now, assume facts in the world layer are true; qualification/accuracy handling is deferred by explicit decision.
- Phrase→concept mapping: phrases / approximations of phrases / regions of token-space map to fixed concepts as an adjacent artefact; the kernel itself is language-independent via NSM.
- Claimed benefits to establish or refute: (1) can-never-misunderstand accuracy for kernel concepts; (2) training efficiency (concepts never learned); (3) train/inference efficiency via dense concept I/O; (4) possible GNN-style non-linear concept I/O; (5) longer-term: internal rules-based inference as a cheap path past weight evaluation — architecture-internal or not is an open question.
- The maintainer is explicitly not an ML specialist; where the brief uses approximate ML language ("the layer after tokenisers"), the programme should translate it into precise mechanisms rather than mirror it.

## Operating rules

- Everything persists in this public repo (jeswr/kernel-of-truth) — the EC2 box is ephemeral.
- Empirical honesty: cited claims, [established]/[claimed]/[speculative] tags, negative evidence reported at full strength.
- ≤5 concurrent agents (standing rate-limit constraint). Research agents do not spawn sub-agents.
- Coordinate via sparq#1683; SPARQ agent invited as prospectus co-reviewer; PSS re-syncs when back online.
