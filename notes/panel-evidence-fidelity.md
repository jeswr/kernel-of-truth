# Panel review — evidence fidelity of docs/architecture.md and docs/poc-design.md vs the five wave-1 reports

Reviewer: adversarial panel (evidence-fidelity brief). Date: 2026-07-07.
Method: every load-bearing claim in the two synthesis documents was checked against
`reports/sparq-estate.md` (SPQ), `reports/deterministic-concept-vectors.md` (DCV),
`reports/fixed-vectors-in-llms.md` (FVL), `reports/nsm-and-knowledge-injection.md` (NSM),
`reports/architecture-and-poc-options.md` (APO).

**Verified clean (one line each):**
- arch §1.2 encoder construction (TPR-within-clause, unitary HRR across clauses, reference-not-inline, kernel-as-cleanup, C-as-proof-lens, NOT-flip ~1/s statement) — faithful to DCV §7.2–§7.4 including the limitation language.
- arch §1.1 capacity numbers (D ≈ 8k–32k, ~200 atoms, s ≈ 100–200, ~2–4 kbit, 0.2–0.5 bits/dim) — match DCV §7.2 (but see finding 11).
- arch §2 C1, C2, C4 verdicts and tags — match FVL verdicts (CONTRADICTED / MOSTLY CONTRADICTED / UNTESTED-SPECULATIVE) at the right strength, including the 5–10× slowdown and the "fixes a symbol, not its meaning" framing; the synthesis correctly does NOT repeat the discredited MMLU headline from 2507.04886 that APO §1.3 uncritically relays.
- arch §1.3 / §3 sparq claims (canon, typed lanes, hashing discipline, store/ANN, grounding modalities, three gaps) — match SPQ §1–§6.
- poc-design experiment specs E1–E6 (methods, controls, metrics, success/failure criteria, GPU-hours, dollar figures, kill-chain ~$30) — match APO §2.3 essentially verbatim (see findings 8, 10 for the exceptions); random-frozen and shuffled-kernel controls carried with correct load-bearing status.
- arch §4 portfolio A1–A5 claim-to-experiment mapping — matches APO §1.2 including each route's "cannot test" caveats.

---

## Findings

**1. MAJOR — LCM scaling exponents misattributed to Meta's LCM and upgraded from [claimed] to flat fact.**
- Synthesis (arch §2, C3): "Meta's LCM — the closest existing test — scales *worse* than token LMs (exponent ~0.5 vs ~0.79) in a frozen learned sentence space", underwriting the "[contradicted at scale]" verdict.
- Report: FVL §4 sources the exponents to **SONAR-LLM (arXiv:2508.05305), tagged [claimed]** — a community follow-up's re-measurement ("token-level LLM α ≈ 0.791 vs SONAR-LLM ≈ 0.569, MSE-LCM ≈ 0.515, diffusion-LCM ≈ 0.485"), not Meta's own LCM paper. What Meta's LCM paper itself establishes (FVL: [established paper, claims mixed]) is the non-numeric finding that it "did not surpass same-size token LLMs" on core English quality, plus SONAR-space fragility.
- Fix: attribute the exponents to SONAR-LLM with its [claimed] tag; rest the "[contradicted at scale]" verdict on the LCM paper's own [established] negatives, with the exponents as corroborating [claimed] evidence.

**2. MAJOR — the NSM foundational critiques are dropped wholesale.**
- Synthesis: architecture.md builds the kernel on "65 prime records + sanctioned molecules" (§3) and nowhere mentions any critique of NSM itself; the only NSM negative carried is DeepNSM's 24/100 (§4).
- Report: NSM §1.3 devotes a full section to [established] critiques — Riemer's circularity of the substitutability criterion ("the weakest link"), von Fintel & Matthewson ("remarkably few convincing semantic universals... the prime inventory's empirical status is unproven"), Bohnemeyer's Yucatec counterexample (no lexical exponents of BEFORE/AFTER) — and issues an explicit instruction: "A kernel built on NSM should claim the [engineering value], not the [scientific claims]."
- Fix: add a short foundations caveat to arch §1/§3 citing NSM §1.3 and adopting the engineering-not-science posture explicitly; the document's own honesty contract ("says so plainly") demands it.

**3. MAJOR — novelty claims exceed what any report established, and contradict the doc's own tag.**
- Synthesis (arch §0.1): "nothing like it has been published" (flat), in the same bullet tagged "[established feasibility, **open novelty**]"; arch §1.1 tags the geometry row "[... construction novel]".
- Reports: the open-niche verdicts are narrower — APO §1.3: "no published attempt to build fixed, human-designed (NSM-style) concept coordinates **into an LM's vocabulary**... [established, **to the limit of several web searches**]"; NSM §5: the unoccupied slot is canonical vectors "**as the entity vocabulary**". Neither covers the encoder construction itself. DCV never claims construction B is unpublished — it is the report's own assembly of published pieces, and DCV §1.3 cites GrapHD as "the closest existing artifact to 'decode the structure from the vector'" (a published deterministic graph→hypervector encoder with demonstrated reconstruction).
- Fix: scope the claim to what the reports say ("no published system uses structure-derived training-free vectors as an LM concept vocabulary; the specific encoder assembly is, to the limit of our searches, unpublished"), and reconcile "nothing like it has been published" with the "[open novelty]" tag.

**4. MINOR — "prototype exists" is real but cited to sources that don't contain it.**
- Synthesis (arch §0.1: "the identity layer (concept-hash) already has a working prototype in the estate"; §1.1 identity row: "(PSS concept-hash design; prototype exists)" under [established] citing "reports/deterministic-concept-vectors.md §5.3, gist §6"; poc X0: "@jeswr/concept-hash's golden-vector discipline").
- Reports: none of the five wave-1 reports mentions a prototype; DCV §5.3 covers only the Bellare–Micciancio/LtHash mathematics; SPQ (the estate survey) cites only the *design doc* and says the minting pipeline "**can be built**" on sparq-canon. The claim is in fact true — but its evidence lives in the gist's orchestrator note / §12 (D4 prototype spec, 77 golden vectors), not in the cited report section.
- Fix: cite the gist orchestrator note / §12 (or the `@jeswr/concept-hash` repo) for the prototype claim; do not shelter it under a DCV citation.

**5. MINOR — convergence-literature tag inflated to [established] over two [claimed] items, and a load-bearing caveat dropped.**
- Synthesis (arch §2): "The cross-model convergence literature cuts in our favour [established]: relative representations, model stitching, vec2vec, and the Platonic Representation Hypothesis all say...".
- Report: FVL §3 tags PRH "[claimed — position paper]" and vec2vec "[claimed, replicated once]"; only relative representations and stitching are [established]. FVL's bottom line also carries the caveat the synthesis drops: "in every convergence result, the shared geometry is the *product of training on data*... precisely the resource the kernel proposes to skip."
- Fix: tag the cluster honestly (established for relative-reps/stitching; claimed for vec2vec/PRH) and carry the trained-geometry caveat — it bears directly on A2/E5.

**6. MINOR — "composes with the sparq estate today" / "unconditionally deliverable" overstates readiness.**
- Synthesis (arch §0.3: "with verification, endorsement, and ZK-compatible commitments — is unconditionally deliverable and composes with the sparq estate today"; §4 A5: "composes with sparq/ZK today").
- Report: SPQ requires real (if small) work first: hash-keyed rows are "a small format fork, not a rewrite" (§3), encoder provenance must be added to the header, ordered-clause pooling must replace permutation-invariant pooling (§4), and the ZK reuse needs the leaf hash "re-target[ed] from sha2-256 to Poseidon2(type_code, blake3(·))" (§5). Endorsement/federation is design-doc material, not surveyed code.
- Fix: replace "today"/"unconditionally" with "after the named small adaptations (SPQ §6)".

**7. MINOR — poc-design hardware numbers not in the source report.**
- Synthesis (poc Hardware): "one T4 spot (g4dn.xlarge, ~$0.16–0.26/hr spot)"; "A10G (g5.xlarge, ~$0.4–0.6/hr spot)"; "encoder is TypeScript on node 22".
- Report: APO §2.2/§2.4 gives T4 "~$0.06/hr (marketplace spot) to ~$0.53/hr (AWS g4dn.xlarge **on-demand**)" and "a marketplace T4 at ~$0.06–0.25/hr"; A10G "$0.43–1.01/hr (g5.xlarge on-demand $1.006/hr)". No g4dn spot range of $0.16–0.26 appears anywhere; the box audit (APO §2.1) never records node or its version.
- Fix: either restore the report's figures or mark the spot ranges as fresh estimates; verify node version on the box before pinning it in a pre-registered doc.

**8. MINOR — E1 spec drops the report's small-vocab condition (and the Adam-momentum caveat).**
- Synthesis (poc E1): "GPT-2-style 5–15M non-embedding params; three embedding conditions...; AdamW weight-decay masked off frozen rows".
- Report: APO E1 specifies "small vocab", and §2.2 explains why it is load-bearing: "Use a **small vocab (4–8k BPE or word-level)** so ~65–500 kernel rows are a meaningful fraction." APO §1.1 also warns beyond weight decay: "if a row ever received gradient before masking was attached, **Adam momentum keeps moving it**."
- Fix: add the vocab-size condition to E1 (it directly affects effect size) and extend the freezing note to cover optimizer momentum state.

**9. MINOR — one of construction B's stated failure modes is omitted from the "known unsolved weakness" disclosure.**
- Synthesis (arch §1.2): the weakness paragraph covers only the NOT-flip/polarity pathology.
- Report: DCV §7.3B lists a second failure mode of equal rank: "superposition weighting is a free design parameter that **silently determines whether root or leaf differences dominate similarity** (the TreeESN suffix-bias lesson in reverse)." poc X3 tests polarity variants but never mentions weighting sensitivity either.
- Fix: add the weighting free-parameter to the arch §1.2 weakness statement and to X3's measurement list.

**10. MINOR — kill-chain pivot targets silently changed from the source's recommendation.**
- Synthesis (poc Kill chain; arch §0): on strong-hypothesis death, "Programme pivots to **A2/A5**".
- Report: APO §2.3 kill-chain logic says "the programme pivots to **(b)/(d)**" — adapter (A2) and **graph-input (A4)**, not external-memory A5.
- Fix: legitimate to re-decide (the report's kill chain is [speculative but recommended]), but the deviation from the source recommendation should be flagged as a decision, since poc-design presents itself as "derived from" APO §2.3.

**11. MINOR — internally inconsistent storage arithmetic, copied uncorrected from the report.**
- Synthesis (arch §1.2): "D ≈ 8k–32k... 16–64 kB per concept fp16, **3–6 GB** for a 10⁵-concept kernel [established]".
- Report: DCV §7.2 says the same — but 16–64 kB × 10⁵ is **1.6–6.4 GB**; "3 GB" matches neither endpoint. The synthesis repeats both figures in one sentence under [established] without noticing the mismatch.
- Fix: state 1.6–6.4 GB (or pick a nominal D and give one number); flag the correction back to DCV.

---

**Totals: 0 BLOCKER · 3 MAJOR (1–3) · 8 MINOR (4–11).**
Overall: the synthesis is unusually faithful on numbers, controls, and verdict strength — the failures cluster around attribution (finding 1), omitted foundational counter-evidence (finding 2), and novelty scoping (finding 3), all fixable without changing the programme's structure.
