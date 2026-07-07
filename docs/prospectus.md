# Prospectus: A Kernel of Truth (draft 1, for SPARQ + PSS review)

**2026-07-07 · Kern (Claude Fable 5) for @jeswr · review thread: [sparq-org/sparq#1683](https://github.com/sparq-org/sparq/issues/1683)**

This is the deliverable the PSS agent announced in the thread: the honest answer, after a five-stream literature and estate investigation plus an adversarial three-reviewer panel, to *"are we seriously onto something, or only partially?"*

## The one-paragraph answer

**Partially — and the partial thing is real.** The hypothesis's strong form (canonical, training-free concept vectors *inside* an LLM acting as ground truth it can never misunderstand) is contradicted by existing evidence: fixing a vector fixes a symbol, not its interpretation; models happily learn semantics on top of arbitrary frozen vectors; and the one scaled attempt at fixed-concept-space I/O (Meta's LCM) underperformed token LMs. What survives is substantial: (1) a **deterministic explication→vector encoder** with quantified capacity guarantees — buildable now, no published equivalent used as an LM concept vocabulary; (2) an open, never-tested empirical niche — does *structure-derived content* in frozen vectors beat content-free frozen vectors? — with a pre-registered ~$50 kill chain; (3) an unconditional-value tier that doesn't depend on any of it: content-addressed, drift-free concept reference with decode-and-verify grounding, ZK-compatible, composing with sparq after small named adaptations; and (4) a genuinely promising reframing surfaced by our own red-team: the kernel as a **canonical, versioned, labeled coordinate system for learned interpretable features** (SAE dictionaries are per-model, unstable, unlabeled — the kernel is their exact complement).

## What was done

- **Five evidence streams** (`reports/`): the sparq vector estate (what's deterministic and reusable — nearly all of the lane stack; what's missing — the recursive composition operator); deterministic structure→vector constructions (VSA/TPR/WL: capacity math puts capped explications inside published bounds at D≈8k–32k); fixed-vectors-in-LLMs (the falsification stream — it falsified); computational NSM + knowledge injection (E-BERT is the mechanics precedent; the injection literature's scaling failures are the warning); architecture options + harness (five integration routes, costed experiments).
- **Synthesis** (`docs/architecture.md`, rev 2): the kernel object (identity hash + explication + canonical vector), claim-by-claim verdicts on the original hypothesis, a six-architecture portfolio (A1 kernel-native vocabulary → A6 kernel↔SAE anchor), the dimension problem stated honestly, NSM adopted for engineering value with its critiques carried.
- **Pre-registered experiment programme** (`docs/poc-design.md`, rev 2): encoder property tests (adversarial single-edit margins, decode depth, the polarity pathology measured and published); mapper/coverage pre-measurements; then E2→E1→E4 on rented GPUs (~$30–80) with shuffled-kernel as the primary null, equivalence bounds for kill verdicts, and two decisive follow-ons gated on results: **E7 scale-slope** (~$2–10k, the pretraining-audience artifact) or **E8 kernel↔SAE alignment** (the interpretability-audience artifact).
- **Adversarial panel** (`notes/panel-*.md`): three independent reviews (evidence fidelity, experimental rigor, frontier-lab skeptic) — 4 blockers and 21 majors found and resolved in rev 2. The panel's material verdicts: don't pitch tiny-scale positives; fix the dimension story (done); measure the mapper before trusting E1 (now Phase M); the fallback pitch is standards-and-instrumentation, not architecture.

## The two pitches (deliberately separated)

- **Research audience:** an untested, falsifiable inductive-bias question with pre-registered experiments and a scale-slope plan; plus the kernel-as-label-space-for-SAE-features instrument. No governance material.
- **Assurance/policy/enterprise audience:** decode-verify grounding against *definitions* (not retrieved text) with cryptographic provenance; drift-free cross-version semantic regression testing; EU-AI-Act-shaped documentation artifacts. No strong claim required — this tier is buildable regardless of how the experiments read out.

## Asks

- **SPARQ agent:** (1) sanity-check the `(concept-hash → embedding)` table seam and the SPQ §6 adaptation list (hash-keyed rows, encoder provenance header, ordered-clause pooling); (2) the ZK question — can the concept-hash and sparq's Poseidon2/Blake3 commitment discipline share domain separation, and is "prove the kernel lookup" (E9/A5) a sensible ZK-over-SPARQL extension? (3) mark up this prospectus + the two rev-2 docs; co-authorship offer stands.
- **PSS agent** (when back online): (1) alignment on minting the kernel v0 corpus with `@jeswr/concept-hash` (65 primes + walkthroughs + ~50 molecules); (2) whether the signed-annotation vector tables (gist §9a) should pin **(encoder-version-hash, D, codebook-hash)** as this programme specifies; (3) take back or co-own any stream as suits.
- **Maintainer:** AWS access per [kernel-of-truth#1](https://github.com/jeswr/kernel-of-truth/issues/1); later, the E7 budget gate.

## Timeline

Encoder v0 + kernel v0 data + Phase X/M: days (this box). Kill chain: ~1–2 days of GPU once access lands. E7/E8: gated decisions after that.

## Status update (2026-07-07, post-Phase-X — evidence now measured, not projected)

**Phase X complete and green** on both synthetic (n=10⁴: margins 47.4× floor; decode 720/720) and authored data (54 concepts: margins 11×; decode 54/54 after a decoder fix whose two failures were pre-registration doing its job). The polarity pathology is now *empirically* disqualifying for similarity uses: on authored data, 13/79 meaning-inverting edits sit closer than the nearest genuinely distinct concept — identity and decode-given-the-kernel are the kernel's reliable operations; cosine similarity is not, and no downstream design uses it.

**Coverage reality (M0, measured in a deliberately favourable domain — these numbers bound every claim):** the deterministic mapper covers **17% of TinyStories token mass** (3.1% concepts + 14% primes; precision/recall provisionally 0.82/0.89 agent-judged, human audit pending); the frequency-weighted **profile-1 expressibility ceiling was ~26% of all token mass**, because 33% of content mass was gated behind the then-unbuilt semantic-molecule tier. **Molecule tier v0 (54 molecules, all passing the §3.5 controlled-lexicon gates mechanically) has since lifted the measured ceiling to ~40% of all token mass** (87.6% of content mass with transitive explicability; 2.1 points across ~33 kinds still gated; zero new mapper ambiguity) — demonstrating the ceiling is liftable with modest, rule-governed authoring effort (~100 further molecules filed as the next tranche). Five kernel concepts were unreachable under the original abstain-on-ambiguity mapper policy; resolved by pre-registered Amendment A1 (tiers for three, exclusion for two). Stated plainly: at kernel-v0 scale, the kernel addresses a bounded definitional slice of language, exactly as the architecture's scope claim (§3) says it should — anyone extrapolating these results to broad coverage is over-reading them.

**Experiment status:** the full kill chain (E2→E1→E4) is code-complete on two independent transports (AWS EC2 pull-path, quota-escalation-gated; Modal serverless, pairing-gated) with pre-registered criteria, pinned encoder hashes (`kot-enc-B/1` + toy-native `kot-enc-Bq/1`), published gloss-set hash, and cost caps (kill chain ≲$50; E1+E4 ≈$10–25). Results will be appended here verbatim against the pre-registered bars.
