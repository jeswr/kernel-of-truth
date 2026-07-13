# F1-K kernel-v1 — PILOT explication batch (human-review packet)

**Purpose.** Calibrate the §1.1 *scholarly explication gate* and the human-review
workflow on ~15 concepts **before** scaling to the ~96-concept large-kernel
rebuild (issue #33). This packet is what the maintainer's annotator reviews.

**Governance.** Benchmark-**blind** (item counts only, from the model-independent
`f1k-eligibility` screen; no gold answers, no model/KaE outcomes, no coverage
rank, no matched items were consulted). `$0`. No git, no registry write, no
freeze, no spend. colibri naming; no handles. Author: `designer-31`.

**Artifacts.**
- Records (kernel-v0 shape + `provenance` sidecar): `data/kernel-v1-pilot/concepts/*.json`
- Reproducible selection + provenance: `poc/scale/f1k-explication/gen_pilot.py`, `pilot-manifest.json`
- Mechanical gate result (out-of-tree; touches nothing else): `poc/scale/f1k-explication/validate_pilot.mjs`

---

## 1. Deterministic selection rule (frozen; reproduced by `gen_pilot.py`)

1. **P1** — from `candidate-pool.json`, keep rows with `greedy_disjoint_m8 == true`
   **and** `header_cue_collision == false` (the disjoint-eligible, header-clean
   set: **2,397** concepts). Coverage gate §1.3 (`m_test ≥ 8`) and the header/cue
   cleanliness are thus already satisfied for every candidate.
2. **R — genus prefilter.** Keep rows whose WN gloss opens with a frozen
   genus-differentia template. This simultaneously (a) restricts to WN glosses
   already in *definitional* shape and (b) fixes the `kot-ast/1` frame family:
   - `AGENTIVE` = `^(someone|a person|one) who…` → InstanceSchema over an actor
   - `ACT` = `^(the|an) act of…`, `^an event…` → InstanceSchema over a happening
   - `STATE` = `^(a|the) state of…`, `^the quality of…`, `^a feeling of…` → WhenTrue/InstanceSchema over a quality
   
   R matches only **110 / 2,397 (4.6%)** — the first calibration signal (see §5).
3. Assign each candidate to its **first-matching** stratum.
4. Sort each stratum by **WN-3.1 synset URN byte order** (design §2.3 tiebreak 6).
5. **Round-robin** `[AGENTIVE, ACT, STATE]`, taking the URN-smallest unused row
   each cycle, until **15** are selected.

Stratum sizes after R: AGENTIVE 29, ACT 64, STATE 15 → selection is 5/5/5.
No model outcome, baseline, K, or pilot score exists or was read at any step.

---

## 2. Review table

For each concept the annotator sees: **label · proposed definition (K) · aligned
WN-3.1 gloss + synset · source · authored-vs-reused · uncertainty flag**. They do
**not** see coverage rank, matched items, or any model output (§1.1 human check).
The four binary review questions (same sense · intension accurate ·
scholarly/self-contained · AST↔prose consistent) are recorded per row downstream.

| # | Concept (slug) | Str | WN-3.1 synset | Proposed definition (K / `gloss`) | Aligned WN gloss (d2 anchor) | Mode | Bar | AST |
|---|---|---|---|---|---|---|---|---|
| 1 | lover | AGT | `n-09645472` | Someone who feels deep affection or romantic love toward another person, or who is the object of such love; especially a person with whom one shares an intimate romantic attachment. | a person who loves someone or is loved by someone | **authored** | meets | lossy |
| 2 | appearance | ACT | `n-00051015` | The event of someone or something coming to be seen, especially by coming before other people in a public place; a becoming-present to view. | the act of appearing in public view; "…" | **authored** | meets | faithful |
| 3 | cheerfulness | STA | `n-04638046` | A disposition marked by good spirits and evident gladness, such that one readily feels contentment and lifts the mood of those nearby. | the quality of being cheerful and dispelling gloom; "…" | **authored** | meets | faithful |
| 4 | peer | AGT | `n-09649426` | A person who holds the same rank, standing, or status as another within a group, being neither above nor below them in position or authority. | a person who is of equal standing with another in a group | light-edit | meets | lossy |
| 5 | apparition | ACT | `n-00051304` | An occasion on which something comes suddenly into view when no one expected to see it, so that those present are taken by surprise; a sudden, unlooked-for becoming-visible. | an act of appearing or becoming visible unexpectedly; "…" | **authored** | **borderline** | lossy |
| 6 | changelessness | STA | `n-04745174` | The quality of remaining the same through time, such that a thing stays as it is and does not come to be other than it was. | the quality of being unchangeable; having a marked tendency to remain unchanged | **authored** | **borderline** | lossy |
| 7 | wrongdoer | AGT | `n-09657157` | A person who does what moral standards or the law forbid; one who commits an offence, wrong, or misdeed against others or against established rules. | a person who transgresses moral or civil law | light-edit | meets | faithful |
| 8 | exit | ACT | `n-00059339` | The act of going out of a place; a movement by which someone or something passes from inside an enclosure or space to a position outside it. | the act of going out | light-edit | meets | faithful |
| 9 | fidelity | STA | `n-04884180` | Steadfast faithfulness in keeping one's promises and obligations to another, so that one continues to act as one has undertaken and does not betray the trust placed in one. | the quality of being faithful | **authored** | meets | faithful |
| 10 | artist's model | AGT | `n-09832624` | A person who poses, keeping still in a chosen attitude, so that a painter or sculptor can observe them and make a picture or figure of them. | a person who poses for a painter or sculptor | light-edit | meets | lossy |
| 11 | ransom | ACT | `n-00097671` | The act of securing the release of a captive by paying the price demanded for it; also the sum so paid, or the freeing thereby obtained. | the act of freeing from captivity or punishment | **authored** | **borderline** | lossy |
| 12 | continuousness | STA | `n-05059738` | The quality of a thing that goes on without break or pause, continuing as one unbroken whole through time rather than stopping and starting. | the quality of something that continues without end or interruption | **authored** | meets | faithful |
| 13 | bill poster | AGT | `n-09873916` | Someone whose work is to fix printed notices, posters, or placards onto walls, boards, and other public surfaces, so that many people will see them. | someone who pastes up bills or placards on walls or billboards | light-edit | **borderline** | lossy |
| 14 | throw | ACT | `n-00105359` | The act of sending something through the air by a rapid movement of the arm and hand, releasing it so that it travels away from the thrower. | the act of throwing (propelling something with a rapid movement of the arm and wrist); "…" | light-edit | meets | faithful |
| 15 | wealth | STA | `n-05123428` | A great abundance of some valued thing, such that there is far more of it present than is usual or than could be needed. | the quality of profuse abundance; "…" | **authored** | **borderline** | faithful |

`Str` = stratum · `Bar` = my honest self-assessment of the scholarly bar ·
`AST` = whether the `kot-ast/1` rendering is *faithful* to the gloss or *lossy*
(profile-1's 65-prime metalanguage cannot carry the differentia). Full hashes,
lemmas, POS, `m_test` screen value, and per-record `bar_note` are in each
record's `provenance` block and in `pilot-manifest.json`.

---

## 3. Concepts I flag as uncertain (annotator: look here first)

- **apparition (5)** — deliberately near-synonymous with **appearance (2)**; they
  share a genus and differ only in the *sudden / unexpected* differentia. This is
  a **sense-discrimination probe**: does the review process catch that two
  distinct synsets got two glosses that must not collapse? Both rendered lossily
  (surprise ≈ "people did not know they would see it").
- **ransom (11)** — the eligible **synset gloss under-specifies** the concept
  ("the act of freeing from captivity or punishment" omits the defining
  *payment*). Authoring the true intension in restores accuracy but arguably
  **narrows the synset** — a §1.2 alignment judgment (same referent/construal?)
  the human must make, not the author.
- **wealth (15)** — the eligible synset `n-05123428` is the **abundance** sense,
  **not** the riches/money sense a reviewer instinctively expects. The gloss is
  written to make the sense unmistakable; the alignment check must confirm the
  reviewer reads the *abundance* sense.
- **changelessness (6)** — "change" is not among the 65 primes, so **both** the
  prose and the AST lean on the SAME/OTHER contrast. Meaning is carried, but the
  reviewer should check this is faithful rather than merely the available move.
- **bill poster (13)** — clean prose, but the AST cannot carry "printed notices /
  words". A reviewer enforcing strict AST↔prose parity (question 4) may fail it
  even though the prose is sound; flagged so the calibration captures how strict
  that fourth question should be.

---

## 4. Self-assessment (honest)

**Reuse-vs-author split.** 0 verbatim-reuse · **6 light-edit** · **9 authored-fresh**.
No WN gloss in the eligible pool passed the scholarly gate *verbatim*: every one
was either circular (`lover`/loves, `appearance`/appearing, `cheerfulness`/cheerful,
`continuousness`/continues, `fidelity`/faithful…), carried embedded examples
(the `"…"` fragments), or was sub-length (`exit` = 4 words, `fidelity` = 4 words).
The design's §3.3 planning band (15–30 *verbatim* reuses) presumed **OBO/SUMO**
sources; the WN-only eligible screen supplies essentially **zero** verbatim reuse.

**Scholarly bar met.** I judge **10 / 15** genuinely meet the first-rate-scholar
bar; **5 / 15 borderline** (apparition, changelessness, ransom, bill-poster,
wealth — §3). None are, in my judgement, below the bar as *prose*; the five are
borderline on *sense/alignment* or on *AST↔prose parity*, which is exactly what
the human gate exists to adjudicate.

**AST adequacy** (separate axis, per §1.1 criterion 8). **8 faithful · 7 lossy**.
All **15/15 pass the mechanical gate** — `validateExplication` (grammar / valency
/ referent / caps) and whole-corpus `encodeConceptSet` (→ D=8192, finite,
positive-norm). But "encodes cleanly" ≠ "means the same": profile-1's 65 NSM
primes render the genus/skeleton reliably while dropping domain differentiae
(painter, walls, money, moral law, romantic). **Lossy-AST is the true bottleneck,
not mechanical validity** — the reviewer's question 4 (AST↔prose consistency) is
where most rebuild attrition will occur.

**d2/K collision (§3.2).** Because the aligned WN gloss is the corpus builder's
d2, K must differ. All 15 authored/edited glosses diverge from their WN source
string — `gloss_sha256 ≠ source_gloss_sha256` for every record (see
`pilot-manifest.json`). This is *necessary but not sufficient*: the builder must
still re-check `sha256(K_text) ≠ sha256(d2_text)` at F1 and never resolve a
collision after seeing outcomes.

**Authoring effort per concept (this session, one author).**
- Definition prose: ~5–15 min (fast once the eligible synset's sense is fixed).
- `kot-ast/1` authoring + validate loop: ~15–35 min, dominated by the *lossy*
  cases where one iterates to find a primes-only paraphrase that both validates
  *and* the author can defend as faithful.
- Sense/alignment adjudication for the borderline cases: ~10–20 min each.
- **Blended ≈ 30–45 min / concept** for author-side work (excludes human review).

**What did NOT run here** (deferred to the builder, by design): the 8-token
gloss↔eval-item leakage check (needs eval items; benchmark-blind here), the
in-tree `data/validate.mjs --kernel data/kernel-v1` parameterization, the
`kot-lex-align/1` alignment file + confidence, and the human 4-binary-question
pass. This packet supplies exactly the inputs those steps consume.

---

## 5. Projection to the ~96-concept rebuild

- **Coverage is not the constraint; definability × renderability is.** 2,404
  disjoint-eligible concepts exist, but only ~4.6% have a WN gloss already in
  genus-differentia shape, and of those a further ~½ render *lossily* in
  profile-1. Selecting 96 concepts that clear **both** the scholarly gate **and**
  a faithful `kot-ast/1` rendering will require reaching well past the top of the
  coverage ranking, or accepting lossy-AST concepts with an explicit carried
  weakness note (as kernel-v0 did with its `KNOWN-WEAK` marks).
- **Author-side effort.** At ≈30–45 min/concept blended, 96 concepts ≈ **48–72
  author-hours** (≈ 6–10 Fable agent-days) — consistent with the design's "5–10
  Fable agent-days … dominated by 45–70 fresh records", but skewed **more fresh**
  than planned because verbatim WN reuse is ~0. Expect ≈ **60–90 fresh/light**
  and ≈ **0–5 verbatim** unless an OBO/SUMO crosswalk is added to the pool first.
- **Human review.** The design's 20–35 h for 96 looks right *for prose*, but this
  pilot suggests the **AST↔prose (question 4)** sub-check is where reviewers will
  spend disproportionate time and reject most; budget review time around that
  question, and pre-triage lossy-AST concepts so reviewers aren't surprised.
- **Recommendation for the gate.** (i) Add a mechanical *pre-flag* that marks a
  candidate `lossy-AST-suspected` when its differentia uses vocabulary outside a
  primes-coverable set, so the human queue is ordered. (ii) Decide, before F0,
  whether lossy-AST concepts are admissible with a weakness note or excluded —
  this single policy choice moves the reachable-96 depth by hundreds of ranks.
  (iii) If verbatim reuse is wanted, seed the pool with reviewed OBO/SUMO
  crosswalks *before* selection; the WN-only pool will not supply it.

---

## Self-check (governance)

- **15 pilot concepts selected by a deterministic, benchmark-blind rule** —
  P1(disjoint_m8 ∧ header-clean) → genus prefilter R → stratify AGENTIVE/ACT/STATE
  → URN byte order → round-robin to 15 (reproduced by `gen_pilot.py`).
- **Reuse-vs-author split:** 0 verbatim · 6 light-edit · 9 authored-fresh.
- **Bar met:** 10 / 15 meet · 5 / 15 borderline (apparition, changelessness,
  ransom, bill-poster, wealth — all flagged in §3).
- **Mechanical AST gate:** 15 / 15 pass `validateExplication` + `encodeConceptSet`
  (D=8192, finite, positive-norm). AST *semantic* adequacy: 8 faithful / 7 lossy.
- **Review table:** `poc/scale/f1k-explication/pilot-review.md` (this file).
- **Projected ~100-scale effort:** ≈ 48–72 author-hours (6–10 Fable agent-days),
  ~60–90 fresh/light + ~0–5 verbatim; human review ≈ 20–35 h, concentrated on the
  AST↔prose question.
- **Constraints honoured:** benchmark-blind · scholarly bar (no templated prose;
  every gloss authored/edited to genus-differentia) · colibri naming · no handles
  · **no git · no registry write · no freeze · no spend ($0)** · exactly one
  WN-3.1 synset pinned per record (§1.2).
