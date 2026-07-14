# FABLE ASSESSMENT — nsk1-r3 deviation D-1: AMT-paraphrase → synthetic-template surface shift (design-integrity)

- **Author:** Fable experiment-designer role, 2026-07-14. Commissioned by the
  coordinator on the runner's D-1 disclosure in
  `poc/nsk1/build_clutrr_r3_corpus.py` (module docstring). Assesses only;
  **nothing is built, frozen, committed, or run** by this document. No frozen
  record, registry entry, or manifest is edited. No account handles appear.
- **Scope:** does the surface shift threaten the nsk1-r3 construct
  (`docs/next/design/nsk1-r3-hardened.md`), and what should the maintainer do.
  Every judgment below is **STIPULATED-not-MEASURED** unless tagged otherwise.
- **Sources read at source this session:** the r3 design (§3, §5.1, §6.2),
  `data/nsk1-clutrr/manifest.json`, `data/clutrr-cache/manifest.json`, the
  r3 builder docstring, `poc/modal/modal_nsk1_g2.py` (`_build_specs_bprime2`
  donor construction), the B″ numbers via
  `docs/next/interpretations/nsk1-bprime.md` and the design's §2 table, the
  pinned release bytes (extracted to /tmp, read-only), and the generator's
  `relations_store.yaml` / `main.py` template pin.

---

## 1. BLUF

**The D-1 surface shift does not confound the r3 positive endpoint** — the
keyed-delivery construct's internal guards (coin, role, all within-run,
same-surface) are surface-invariant by construction — **but it is not
harmless**: it un-calibrates the 0.70 floor and the n=300 power plan, it
voids the "near-certain" headroom-gate premise, and it makes the
pre-registered **REFUTED branch ambiguous** (non-replication vs
surface-sensitivity). Surface-invariance of the effect SIZE is currently pure
stipulation with an **ambiguous sign** (§4). A byte-faithful replication of
B″'s substrate is **permanently impossible** (§2), so the option space really
is {synthetic surfaces, paraphrase approximation, park}.

**Recommendation: MITIGATE-THEN-ACCEPT** — a ≲$1 pre-freeze exploratory
**surface-bridge calibration** on the already-contacted items (same chains,
both surfaces, paired), then ACCEPT synthetic surfaces with the record
relabelled **"confirmatory on a fresh, structurally-identical,
synthetic-surface substrate"** — not "replication on fresh items" tout
court — and the REFUTED licensing text amended accordingly (§6).

---

## 2. D-1 verified at source; the exact-substrate path is closed

[MEASURED — provenance-only checks, this session:]

- `data/clutrr-cache/cleaned_placeholders.zip` on disk is **2,052 bytes of
  saved 404 HTML** ("Page not found", Hugo site), sha256 `390500fc…d425` —
  ≠ the generator's own pin `ed2264…f924` (`clutrr/main.py:38`). The runner's
  report (origin 404, no Wayback, no mirror, checked 2026-07-14) is
  consistent with this; I did not re-run the external search.
- The pinned release (`clutrr-emnlp-release.zip`, sha `b4029f68…228e`)
  contains **exactly six bundles** — the six already in
  `manifest.json.source.config_order`. The design §6.2 fallback ("drawing
  additional pinned release configs beyond the six") is therefore **dead**:
  there is no seventh config, and the covered pool is exhausted
  (`covered_pool_deduped = 958`, `remainder_unused = 0`).
- The released CSVs carry a `syn_story` column, but it is **empty in all
  10,094 rows** of the covered-slice source CSV
  (`data_089907f8/1.2,1.3_train.csv`) — no released same-row synthetic
  render exists.
- The generator's synthetic branch renders each edge from 2-item phrasing
  lists (`relations_store.yaml` `p`, e.g. "e_2 is the father of e_1" /
  "e_2 is e_1's father"). The AMT surfaces are materially richer: narrative
  filler and **inverse-phrasing renders of up-edges** (retained item
  clutrr-c0001: "[Michael] and his daughter [Jennifer] like to read poems
  together…" for an `edge_types = [father, father]` chain).

Consequence: fresh AMT-surface items **cannot be produced by any pinned
path**. B″'s exact substrate survives only as the 958 already-contacted
items retained in `data/nsk1-clutrr/items.jsonl`.

---

## 3. Where the story surface enters the r3 measurement (construct decomposition)

The B″/r3 measurement touches the story surface at exactly four points:

| entry point | surface-dependent? |
|---|---|
| **Donor sentences** `D_top`/`D_bridge` → Δ̂v | **No.** Fixed frame "Note: the `<rs>` of `<base>` is `<NAME>`." (`_build_specs_bprime2`, build-asserted to differ only in the name slot). Only names + the relation word enter; story prose never does. Δ̂v is invariant under D-1. |
| **Prompt context** → `h_p`, ‖h_p‖, pre-injection margin | **Yes.** The final-prompt-token residual, the norm the injection is matched to, and the host's prior over the two candidate names are all functions of the full prompt, story included. |
| **Text-only pass** → headroom gate + substrata | **Yes.** 0.7912 was measured on AMT surfaces; terser canonical-phrasing stories plausibly raise accuracy toward (or past) the 0.85 gate ceiling. |
| **Candidate tokens** (names) | No. Same pinned name store; teacher-forced margins on names, not prose. |

And the guards:

- **coin:** E[coin] ≤ 0.5 **by arithmetic** for any content-free perturbation
  on any surface — validity is surface-invariant.
- **role:** constructed from the deranged donor with fixed key→sign; its
  *level* (~0.58 in B″) may shift with surface, but it is measured in-run on
  the same surface as the real arm, so `real > role` remains an internally
  valid same-substrate comparison.
- **real vs coin/role:** all arms share each item's forwards on the same
  surface; no cross-surface comparison exists anywhere in the endpoint.

**Q1 answer, part 1 (internal validity):** the keyed-delivery signal, the
coin/role guards, and the `real>coin` / `real>role` endpoints are
**construct-valid on any surface** — the endpoint turns on chain structure +
the injected key + the name pair, and every comparison is within-surface.
D-1 cannot mint a false PASS through the guards.

---

## 4. What IS surface-dependent: effect size, with an ambiguous sign

[STIPULATED-not-MEASURED — mechanism plausibility, both directions:]

- **Pressure UP (easier keying).** (i) The synthetic story sentences ("A is
  the father of B.") are near-syntactic siblings of the donor frame ("Note:
  the father of X is NAME.") — **donor–story register convergence** that B″
  never had; the injected direction may align better with the context's name
  representations. (ii) Shorter, canonical-phrasing, filler-free contexts
  raise name salience and remove the inverse-phrasing parsing burden the AMT
  surfaces imposed.
- **Pressure DOWN (harder flipping).** Trivially-parsable stories strengthen
  the host's text prior over the correct name; a larger pre-injection
  |margin| resists a fixed-fraction (α·‖h_p‖) push, so keyacc can *fall*
  even as text-only accuracy rises. The same mechanism threatens the
  headroom gate directly (text-only > 0.85 → INSTRUMENT-INVALID).
- **Cell carry-over (ASM-2354).** (16,16)/(12,16) were selected on AMT input
  statistics. A no-search design on a shifted input distribution reads any
  cell drift as failure — this feeds the FAIL-ambiguity below, not a false
  PASS.

Net: B″'s 0.85/0.81 effect sizes, the 0.70 floor's comfort margin, and the
n=300 power plan (binding at planning keyacc 0.81) are **calibrated to a
surface that no longer exists**. If the true synthetic-surface keyacc is,
say, 0.75, r3 lands INCONCLUSIVE-or-REFUTED for surface reasons, not
delivery reasons.

**Q1 answer, part 2:** plausibly surface-sensitive in **magnitude**, with
unknown sign; surface-invariant in **internal validity**. The design's §6.2
"distributionally identical" stipulation (ASM-2357) is falsified as written
and must be amended regardless of the option chosen.

---

## 5. Q2 — acceptable substrate, confound, or redesign?

**A synthetic-surface corpus is an ACCEPTABLE confirmatory substrate for the
delivery-existence claim, with one honest relabel and one asymmetry
disclosed:**

- **A PASS is valid and meaningful.** All guards hold internally; a PASS
  demonstrates keyed delivery on a fresh, never-contacted,
  structurally-identical substrate — in fact a modest *generalization* of B″
  (new surface family), which is worth having. But it is **not** a
  byte-faithful replication of B″'s measurement, and the record must not say
  "replicates on fresh independent items" without the surface qualifier. The
  correct grade is **confirmatory-on-a-related-substrate**.
- **The decisive negative is degraded — this is the real cost of D-1.** The
  pre-registered REFUTED branch ("both cells UB < 0.70 ⇒ B″ did not
  replicate") now conflates two hypotheses: (a) B″ was a fluke; (b) delivery
  is real but surface-sensitive (or the cells drifted with the input
  statistics). A confirmatory design whose kill criterion cannot
  discriminate its target from a disclosed nuisance is weakened precisely
  where confirmatory designs earn their keep. A FAIL on synthetic surfaces
  must therefore license "did not replicate **on this substrate**" plus a
  maintainer surface-fork — it cannot, by itself, erase B″-on-AMT (which
  stays MEASURED-exploratory either way).
- **Not a redesign trigger.** The construct core is surface-tolerant; the
  guards are intact; the alternative substrates are worse (§6.b2) or
  nonexistent (§2). Parking the programme's one live kernel-specific
  positive over prose style, without first spending <$1 to measure the
  sensitivity, would be disproportionate.

---

## 6. Options and recommendation (Q3)

**(a) ACCEPT as-is (disclosure only).** Viable but leaves surface-invariance
a pure stipulation with ambiguous sign, the floor/power calibration
inherited from a vanished substrate, and the FAIL branch ambiguous.
Acceptable only if the maintainer declines all spend before freeze.

**(b) MITIGATE — three sub-options, one good:**

- **b1. Re-render B″'s retained surfaces:** the AMT surfaces exist only for
  the 958 **contacted** items — they cannot be fresh. Not viable for the
  confirmatory corpus; viable only as the bridge's AMT arm (below).
- **b2. Paraphrase model to approximate AMT style: REJECT.** It inserts an
  unpinnable modern-LLM substrate (its own stylistic priors, its own
  version drift) into a confirmatory record — strictly worse provenance
  than the deviation it patches, and it violates the fail-closed pin
  discipline everywhere else in the programme.
- **b3. Surface-bridge calibration (RECOMMENDED).** The contacted items
  retain full chain structure (`edge_types`, `genders`, lexicon,
  provenance — verified on clutrr-c0001). Re-render the SAME chains
  through the pinned synthetic templater (`relations_store.yaml` `p`
  lists, PYTHONHASHSEED=0) and measure keyacc at C1=(16,16), α=1.0,
  **paired same-item AMT-vs-synthetic**, on ~100–200 items.
  Exploratory-labelled, a disclosed further contact of items that are
  **already burned** (it cannot touch the fresh corpus or its seeds);
  ~6–13k forwards ≈ well under 0.1 GPU-h ≈ **≲ USD 1**. Output: a
  MEASURED-exploratory paired surface-sensitivity delta that (i) converts
  the invariance stipulation into a calibration, (ii) re-anchors the
  planning keyacc / power table on the actual substrate, (iii)
  pre-disambiguates a later FAIL.

**(c) REDESIGN / PARK.** Unwarranted on the evidence above; keep as the
branch if b3 shows a material shift (e.g., paired synthetic keyacc LB below
the planning value 0.81) and re-calibration cannot restore power within the
cost caps — then the maintainer forks between raising n / lowering the
declared floor pre-freeze (with the SESOI honestly re-argued) and parking.

**Recommended: b3 → a.** Run the bridge; if synthetic keyacc holds the B″
band (a designer-set, disclosed, non-gating comfort band around the 0.81
planning value), freeze with these amendments:

1. **ASM-2357 reworded** per the runner's own proposal: "structurally
   identical, surface-deviating (synthetic templating), headroom-gated
   in-run" — "distributionally identical" is falsified and may not survive.
2. **New ASM** registering D-1 itself + the bridge numbers as the
   calibration basis (registered by the coordinator at commit, per §10
   discipline).
3. **Claim relabel** in §1/§9 of the design and in the record:
   PASS licenses "the B″ keyed-delivery finding holds on a fresh,
   structurally-identical, **synthetic-surface** CLUTRR substrate" —
   confirmatory-on-a-related-substrate, never "byte-faithful replication".
4. **REFUTED text amended:** FAIL = non-replication **on this substrate**;
   mandates a maintainer surface-fork; does not by itself retire B″-on-AMT.
5. **Headroom premise downgraded** from "near-certain pass" to a live gate
   (§5.1) — terser surfaces make the 0.85 ceiling a real trip risk.
6. **Provenance lesson** (for `bd remember`, coordinator's call): pin AND
   CACHE substrate bytes at first fetch — the programme pinned
   `cleaned_placeholders.zip`'s sha inside the generator but never cached
   the bytes; the sha outlived the artifact.

---

## 7. Carried unknowns

[UNMEASURED] the actual paired surface delta (b3 measures it); whether the
keying-viable cells shift with input statistics; text-only accuracy on
synthetic surfaces vs the 0.85 gate ceiling; the role-control level on
synthetic surfaces; whether donor–story register convergence inflates
keyacc (a bridge PASS with *higher* synthetic keyacc would flag this — worth
reporting, never gating).

---

*Self-check: assessment only — no build, no freeze, no registry/manifest
edit, no git action, no GPU spend; every judgment tagged
STIPULATED-not-MEASURED, every checked fact tagged MEASURED with its check
named; no account handles; the recommendation is input to a maintainer
decision, not a decision.*
