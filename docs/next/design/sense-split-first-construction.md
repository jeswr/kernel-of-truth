# Sense-Split-First Construction (kernel-v1) — DESIGN

**Role: Fable DESIGN agent (designer-4), 2026-07-12. This is a DESIGN for the
maintainer to approve — not an experiment commitment, not a prereg, and it
issues no feasibility conclusion on CORRECTNESS or EFFICIENCY. Nothing here
modifies kernel-v0, the frozen g2 lineage, the v2.2 pilot decision
(adjudication §D), or any registered verdict.** Assumption block:
`docs/next/design/asm-sensesplit-1900-1909.json` (owner designer-4; range
1900–1909 verified free at emission — max registered id in
`registry/assumptions.jsonl` is 1897; repo-wide grep for `ASM-19[0-9][0-9]`
empty).

**Governing requirement.** [STIPULATED — maintainer decision, 2026-07-12,
recorded with provenance in ASM-1884] A kernel concept is a **sense**, not a
word. Polysemous surface words must be split into one concept per sense at
construction time — break-physical / break-sound / break-trust are distinct
concepts — and typing must answer to the concept's own meaning: a breakage,
in any sense, is an **event**, never a material entity. kernel-v0 (54
word-level concepts) does not sense-split; the g2:pi:011 unsoundness traced
to (a) an un-sense-split hand-authored `break` concept plus (b) an ontology
mapping that committed to the physical FrameNet frame while the concept layer
stayed word-scoped (adjudication §B.iii — frame selection *is* sense
selection). The adjudication (`docs/next/analysis/
g2-measurement-and-sense-splitting-adjudication.md` §C) rules "concept =
sense" the field norm and UFO typing a **dependent** of sense-splitting.

Epistemic tags: **[MEASURED]** read from committed bytes or a stated local
diagnostic this tick (arithmetic on such bytes folded in, steps shown);
**[LIT-BACKED]** published-literature grounding, provenance stated;
**[STIPULATED]** a design choice or ruling, never evidence;
**[EXTRAPOLATION]** a forward claim with its resolution path named.

**Sources verified at source this tick:**
`data/kernel-v0/{manifest.json,concepts/break.json,minted-urns.jsonl}`;
`data/lexical-wn31/{manifest.json,synsets-*.jsonl,alignment-kernel-v0.json}`
(WordNet 3.1, sha-pinned source files); `data/onto-framenet/{manifest.json,
frames.jsonl,alignment-kernel-v0.json}` (FrameNet 1.7);
`data/onto-softtype/soft-type-candidates.jsonl` (panel concept set);
the g2 adjudication + `asm-g2adj-1880-1889.json`;
`docs/next/design/{large-kernel-scale-track.md,g2-import-v22-rubric-iteration.md}`;
`registry/assumptions.jsonl` (847 rows, max id ASM-1897).

---

## 0. The measured shape of the problem

Three facts, now pinned locally rather than cited from training knowledge:

1. **Polysemy is the norm in kernel-v0, not the exception.** [MEASURED]
   51 of the 54 kernel-v0 words are single-lemma and matchable against the
   pinned WordNet 3.1 extraction (`part-of`, `has-part`, `maker-of`
   excluded as multiword relational coinages). Counting only **same-POS**
   synsets: 434 synsets across the 51 words; median 4; 42/51 words have ≥2
   senses; 24 have ≥5. The heavy tail: break 59 (verb), make 49, give 44,
   take 42, dead 17, find 16. The adjudication's [LIT-BACKED, unpinned]
   "commonly cited 59" for break is hereby MEASURED against
   `data/lexical-wn31/synsets-verb.jsonl` (59 verb synsets whose lemma set
   contains `break`; 75 across all POS). ASM-1900.

2. **FrameNet's lemma-in-frame inventory partitions break's coarse senses.**
   [MEASURED] Exactly 8 pinned frames carry a `break` lexical unit
   (`data/onto-framenet/frames.jsonl`): `Cause_to_fragment` (frame-414,
   agentive physical shatter), `Breaking_apart` (1862, inchoative physical),
   `Breaking_off` (1860), `Render_nonfunctional` (416, "broke the alarm
   clock"), `Cause_harm` (112) / `Experience_bodily_harm` (384, "broke his
   arm/foot"), `Compliance` (117, "break a promise / the law" — the
   norm-violation sense), `Opportunity` (2350, break.n). The adjudication's
   claim that FrameNet separates the physical from the norm-violating sense
   is confirmed at source. ASM-1901.

3. **The five g2 sense-channel items sit exactly on this tail.** [MEASURED,
   carried from ASM-1886] Items 011/036/037/070/071 are break (59 senses),
   make (49), find (16) — bare-valence parentheticals; the sense-fixed
   labels produced zero sense-channel disagreements. The g2 panel (39
   concepts, 84 slots) contains **24 words with ≥4 same-POS senses**
   [MEASURED this tick] — the polysemous subset any re-measure must split
   first.

---

## 1. Sense-inventory import

### 1.1 Sources and units

- **Atomic sense unit: the pinned WordNet 3.1 synset** (`data/lexical-wn31`,
  source tarball sha-pinned, 117,791 synsets). Rationale: it is the finest
  inventory we pin, it is already the scale track's backbone (§3.1), and at
  scale synsets simply *are* the concept records — so the small kernel and
  the large kernel use one unit. [STIPULATED]
- **Coarse/event-structural unit: the FrameNet 1.7 lexical unit**
  (lemma-in-frame, `data/onto-framenet`). A frame fixes the eventuality type
  and the valency (Core FEs) — exactly what a RelationalSchema explication
  needs, and exactly what UFO event-typing consumes. [STIPULATED; the
  existing framenet alignment file already states this correspondence]

### 1.2 Reconciliation and selection rule (the load-bearing stipulation)

WordNet is famously over-fine (59 break verb synsets); FrameNet is coarser
(8 break frames). The rule set, ASM-1902 [STIPULATED]:

- **R1 (enumerate, mechanical).** For each surface word, the candidate sense
  set = all same-POS WN31 synsets whose lemma set contains the word.
  Exhaustive, scripted, no judgment.
- **R2 (frame projection, mechanical where possible).** Each candidate
  synset is mapped to the FrameNet frame carrying that lemma's LU whose
  definition matches the synset gloss; unmappable synsets stay `frame:null`.
  (This step is hand-reviewed at kernel scale; at import scale it uses the
  published FN–WN mappings when pinned.)
- **R3 (cluster within frame only).** A kernel-v1 concept = a cluster of ≥1
  candidate synsets such that (a) **all share one FrameNet frame** (or all
  are frame-null), (b) all are truthfully covered by **one** NSM
  explication, and (c) all share argument structure (no clustering a
  causative with its inchoative — FN already separates `Cause_to_fragment`
  from `Breaking_apart`, and the rule holds for frame-null clusters too).
  **The frame boundary is a hard split criterion; within-frame clustering
  is permitted and disclosed** (member synsets listed). This absorbs WN's
  over-fineness without ever re-merging genuinely distinct senses.
- **R4 (selection + scope closure).** Mint only the senses the kernel
  actually needs: senses referenced by other kernel concepts/molecules,
  senses on the measurement panel, and the dominant sense(s) of each word.
  Every **non-minted** candidate synset is recorded in an explicit
  `excludedSenses` list on the lemma's sense-index record. A concept
  thereby claims its synset cluster, **not the word** — the scope ambiguity
  that produced the g2 sense channel is closed by construction, not by
  prose.
- **R5 (cross-resource dedup).** Where a FrameNet LU has no WN synset (or
  vice versa) the candidate still enters the inventory with single-source
  provenance; where both exist, the sense record carries both ids. No
  candidate is silently dropped.

### 1.3 Worked example: break (verb)

Candidate set: 59 WN31 verb synsets [MEASURED]; 7 verb frames + 1 noun frame
[MEASURED]. A plausible kernel-v1 mint list (illustrative — final clustering
is an authoring act, ASM-1902 governs the rule not the rows):

| kernel-v1 alias | FN frame | WN31 cluster (examples) | sense-fixing gloss |
|---|---|---|---|
| `break.shatter` | Cause_to_fragment (414) | v-00335806 ("destroy the integrity of… into pieces") | X causes Y to become many pieces — **the sense kernel-v0's explication already describes** |
| `break.shatter-become` | Breaking_apart (1862) | v-00334996 ("The figurine broke") | inchoative counterpart; distinct frame ⇒ distinct concept, cross-referenced |
| `break.malfunction` | Render_nonfunctional (416) | v-00259551 ("broke the alarm clock"), v-01372011 ("the lawn mower finally broke" — inchoative, clustered only if frame-null review allows; else split) | Y stops being able to do what it is for |
| `break.violate` | Compliance (117) | v-02572443 ("act in disregard of laws, rules, contracts, or promises") | X does not do what the words/law said — **object is a social/normative something, never material** |
| `break.interrupt` | (frame-null cluster) | v-00364717, v-02541382, v-02752324 ("break the silence / a streak / the cycle") | a continuing something stops |
| `break.dawn-news` | (frame-null) | v-00340274, v-00938019 ("news broke") | a happening becomes known / begins |
| excluded | — | remaining ~50 synsets (voice breaking, horse-breaking, circuit, alibi, stock prices, …) | listed in `excludedSenses`, unminted |

Every row is an **event** concept (maintainer clause); what varies per sense
is the *argument* typing — §3. The pi:011 defect decomposes cleanly: the
range preference "material entity" is attached to `break.shatter` where it
is defensible, and is unmintable for `break.violate` where it was false.

---

## 2. One concept per sense: minting, identity, migration

### 2.1 Minting rule (ASM-1903 [STIPULATED])

- **Alias URN:** `urn:kernel-v1:<lemma>.<senseTag>` — e.g.
  `urn:kernel-v1:break.shatter`, `urn:kernel-v1:break.violate`. The
  senseTag is a short stable mnemonic, unique per lemma, chosen at
  authoring time and registered in the corpus sense index; like all labels
  it is **annotation**, outside identity.
- **Identity is unchanged:** the content-addressed `urn:kot:` mint over the
  kot-ast/1 `explication` object, same pinned mint tool
  (`mintToolHash e07bc2ac…`), same identity payload rule ("Identity = the
  explication object"). **No encoder change, no schema change, no
  ALGORITHM_VERSION bump, no X0 golden regeneration** — kernel-v1 is a data
  corpus, the encoder pin is untouched. This keeps the whole exercise off
  the encoder-version critical path.
- **Sense record (annotation, manifest-gated):** every concept carries
  `sense: { senseTag, wn31Synsets: [urn…], framenetFrame: urn|null,
  glossQuote, excludedSiblingCount }`, and every lemma gets a **sense-index
  record** listing minted senses + `excludedSenses` (R4).
- **Fail-closed corpus gates** (in the corpus build, mirroring the
  no-silent-fallback convention):
  - **G1 — no shared identity:** `duplicateIdentityGroups` must remain 0.
    If two putative senses receive byte-identical explications they have
    not been split; either the explications are revised or the senses are
    **merged and the merge is reported** as a measured profile-1
    expressivity limit (a real and interesting number — how many WN sense
    distinctions profile-1 can carry), never silently absorbed.
  - **G2 — no unacknowledged polysemy:** every lemma with ≥2 same-POS WN31
    senses must have either ≥2 minted senses or 1 minted sense plus a
    non-empty `excludedSenses` list; otherwise the build fails with
    `ERR_SENSE_UNDERDETERMINED`.

### 2.2 Migration and deprecation of kernel-v0 (ASM-1904 [STIPULATED])

kernel-v0 is **frozen forever** — frozen experiments (g2 v1/v2.2, X-phase
goldens, alignments) reference it and their records must stay reproducible.
kernel-v1 is a new corpus at `data/kernel-v1/`. Each v0 concept gets exactly
one disposition, recorded in the v1 manifest (`supersedes` /
`supersededBy`):

- **CARRY** — already sense-fixed (the parenthetical is a sense
  description: `lie (the words)`, `birth (the event)`, `death (the
  event)`, …). The explication is carried byte-identical, so the
  content-addressed `urn:kot:` mint is **identical** — continuity for free;
  only the alias moves to `urn:kernel-v1:` and a sense record (WN synset,
  frame) is attached. The existing `alignment-kernel-v0.json` rows, which
  already picked a synset by hand, seed these sense records.
- **SEED** — word-level polysemous concept whose explication describes one
  sense: the v0 record is deprecated; its explication becomes the draft of
  the corresponding v1 sense (v0 `break` → `break.shatter`; its authoring
  note *already concedes* the many-small-pieces clause fits shattering).
  Sibling senses are authored fresh.
- **REVIEW** — latent cases flagged by the adjudication (`friend` — the
  material-entity over-commitment at 040/041; `broken`, whose 13 adj senses
  and downstream `repair` reference need a decision: `repair (X repairs Y)`
  semantically wants `broken.nonfunctional` → `break.malfunction`, not the
  shatter sense — a concrete demonstration that the reference DAG itself is
  sense-sensitive and must be re-pointed edge by edge).

Downstream artifacts re-emitted against v1: the WN/FN alignment files
(now near-trivial — the sense record *is* the alignment), the soft-type
records (per-sense, §3), and the molecules-v0 references (each molecule that
references a polysemous concept re-points to a specific sense; audit pass
required).

---

## 3. NSM explication + UFO typing per sense (ASM-1905 [STIPULATED])

### 3.1 What is imported vs authored

| Step | Mode |
|---|---|
| Sense enumeration (R1), frame projection candidates (R2) | **Mechanical** from pinned resources |
| Authoring brief per sense: WN gloss(es) + FN frame definition + Core FEs + example sentences | **Auto-assembled** |
| Valency skeleton: Core FEs → candidate referent list (Agent→SomeoneRef, Patient/Whole→SomethingRef, Time→TimeRef) | **Auto-suggested**, hand-confirmed |
| Concept-level ontic category candidate (frame ⇒ Event; adj sense ⇒ quality/mode; noun sense ⇒ per cascade) | **Rule-inferred candidate** (scale track §4.1 cascade), endorsed by review |
| The NSM explication body (clauses) | **Authored** (explicator role, encoder/validator loop). Never auto-promoted — scale-track §3.4 rule 7 holds: a suggested paraphrase is a review-queue item, not compiler input |
| Within-frame synset clustering (R3), senseTag choice | **Authored**, disclosed |
| Adequacy review, knownWeak notes | **Authored** |

### 3.2 Typing must match the sense — the two-level scheme

- **Concept level (CK-UFO sidecar, per sense).** `break.shatter`,
  `break.violate`, `break.interrupt` are all `ontic_category: event` — the
  maintainer's clause ("a breakage, in any sense, is an event, never a
  material entity") is satisfied *structurally*, because the category field
  now hangs off a sense whose frame is eventive, not off a word. `broken.*`
  senses are modes/qualities of the patient; `friend` senses are role/relator
  patterns. Assignment goes through the deterministic cascade (explicit
  commitment → endorsed crosswalk → rule inference → soft candidate →
  `underdetermined`), and `underdetermined` is a legal value, not an error.
- **Argument level.** Two layers, deliberately unequal in authority:
  - **Hard referent sorts stay inside the existing profile-1 3-sort grammar**
    (`SomeoneRef`/`SomethingRef`/`TimeRef`) — unchanged, hence no encoder
    bump. What changes is that the sort commitment is now made **per sense**
    and is therefore well-posed: "in `break.violate`, X is a someone" no
    longer fights "storms break windows", because storms live in
    `break.shatter`, whose agent slot can be authored as the broader sort.
    This is the surface whose word-scoped soundness measured 0.3929
    (ASM-1881) and whose **sense-scoped soundness is the load-bearing
    unmeasured quantity** — §5 measures it.
  - **Fine selectional typing is soft, rank-only, per sense** — same
    forbidden-effects discipline as the g2 import (`binding:false`,
    never compiling into domain/range): `break.shatter` patient →
    BFO material entity (defensible *within* that sense);
    `break.violate` object → social/normative object (promise, law, rule
    — never material); `break.interrupt` patient → process/state. The
    pi:011 class of defect — a sense-specific preference attached to a
    word-scoped concept — becomes unmintable: the record's subject *is*
    the sense.

---

## 4. Integration with the large-kernel scale track

**Sense-splitting and scaling are the same move.** [STIPULATED, grounded in
MEASURED inventory] The scale track's backbone unit is already the sense:
WordNet's 117,791 synsets *are* senses; FrameNet's LUs are senses; the OBO
records are (mostly) monosemous technical terms. What the track lacked was a
sense-disciplined **nucleus**: kernel-v1 becomes the `Explicated` tier keyed
by synset-cluster, and the semantic-status ladder (§2.2 of the scale track)
needs no new rungs.

Concrete pipeline changes (poc/scale ingestion):

1. **Unit of account:** concept records are keyed by sense (synset cluster),
   full stop. The 54→N "multiplier" exists only at the hand-authored
   nucleus: 51 matchable kernel words → 434 same-POS synsets is the raw
   ceiling (8.5×) [MEASURED]; under R4 selection the minted kernel-v1 is
   estimated at **~110–140 concepts** (heavy-tailed: break/make/give/take
   contribute 4–6 senses each, most words 1–2) [EXTRAPOLATION, ASM-1908 —
   resolved by the Stage-C build]. At the 10k+ stages there is no
   multiplier at all: importing by synset delivers sense-split concepts
   natively, and hand-NSM doesn't scale regardless (the track's premise).
2. **Sense-index records** (lemma → minted senses + excludedSenses) become a
   first-class corpus artifact; the natural-input mapper's word→concept
   fan-out reads this index, making its ambiguity set explicit and
   measurable (mapper retention/dangerous-error metrics already planned in
   the track gain a sense-resolution stratum).
3. **Alignment collapses into provenance:** `alignment-kernel-v0.json`-style
   hand bridges disappear for v1+ concepts — the sense record *is* the
   alignment, minted at construction rather than reverse-engineered after.
4. **Typing audits stratify per sense** (§4.3 of the track): the g2-style
   hard-typing rerun demanded by the track's audit list is only well-posed
   post-split (adjudication §C); the S1→S2 hard-typing precision gate
   (lower 95% CB > 0.95) inherits sense scope.
5. **G1 as an expressivity census at scale:** the count of WN sense
   distinctions that collapse to identical explications becomes a standing
   measured output (profile-1's sense resolution), reported per stage.

---

## 5. Cheap first validation (design only, costed — no commitment)

Two questions, one small build. Instrument note: whichever judgment channel
is live per the adjudication's §D pre-commitment — the v2.2 proxy pair if
its pilot passes AC1 ≥0.65, else the human panel. This design does not
re-litigate that decision and spends nothing before it resolves.

### V-A: do the g2 sense-channel disagreements resolve? (the 5/12 prediction)

- **Materials:** sense-split the three implicated verbs + the flagged noun:
  `break.{shatter,violate,malfunction}`, `make.{create,cause}` ("make a
  chair" vs "make trouble/someone sad"), `find.{locate,discover}` ("find
  the keys" vs "find a flaw / find that…"), `friend.{person,figurative}`
  (the 040/041 latent sibling) — **~10–12 sense concepts over 4 lemmas**,
  explications authored per §3, soft-type records rebuilt per sense
  (~30–36 slots), renders regenerated with the v2.2 template (whose
  parenthetical instruction now points at a real sense gloss instead of
  bare valence).
- **Readout (pre-stated expectation, not a gate):** the adjudication
  predicts the 5 sense-channel items (011, 036, 037, 070, 071) are
  sense-underdetermination that splitting fixes — expectation **≥4/5
  resolve** (judges agree, and per-sense verdicts are coherent:
  `break.shatter` range→material judged sound, `break.violate`
  range→material unmintable/absent). Falsifier: persistent disagreement on
  sense-split items would mean the defect is in the instrument or the
  typing content itself — a genuine, no-longer-artifactual correctness
  signal. [EXTRAPOLATION, ASM-1907]
- **Cost:** judge spend at measured v2.2 unit anchors (full 84-slot arm
  worst-case ≈ **$9.55**; pilot ≈ $1.06; ~$0.008–0.012/judgment)
  [MEASURED anchors, ASM-1906] → ~36 slots × 2 judges ≈ **$1–3 proxy**, or
  ~1–2 h human-panel labour. Authoring: **~2–3 agent-days** (10–12
  explications through the encoder/validator loop + soft-type rebuild +
  render regen).

### V-B: measure the load-bearing unmeasured quantity

- **What:** sense-scoped soundness of the **binding referent sorts** — the
  hard SomeoneRef/SomethingRef/TimeRef commitments inside the explications,
  the surface whose word-scoped lower bound is 0.3929 and whose sense-scoped
  value is, per ASM-1887, what an engine consumer is actually bound by.
- **How:** for each sense-split concept, render each referent-sort
  commitment as a per-sense ordinary-meaning claim ("in break.violate — X
  does not do what the words said — X is a person or people") and judge on
  the same yes/no channel. On the V-A materials this is ~30 additional
  slots (≈ **$1–3** proxy). The number this produces is the **first
  well-posed estimate of hard-typing soundness**, directly replacing the
  0.3929 as the quantity of record (the 0.3929 stands, re-labelled a
  word-scoped lower bound).
- **What neither V-A nor V-B licenses:** instrument validation (the pilot's
  job), soft-layer adoption (the frozen v2.2 arm's job), any feasibility
  conclusion. [STIPULATED]

---

## 6. Staging, cost, risks, go/no-go

### 6.1 Stages (each gated on the last; costs are planning bands, not commitments)

| Stage | Content | Cost band | Gate to proceed |
|---|---|---|---|
| **A — decisive first increment** | Sense-split break/make/find/friend (~10–12 senses); run V-A + V-B on them | **≤$10 model spend + 2–3 agent-days** | ≥4/5 sense-channel items resolve AND no new sense-channel disagreement on split items AND V-B is measurable (judges decisive) |
| **B — panel subset** | The 24 polysemous g2-panel words (≥4 same-POS senses [MEASURED]; the "~20" of the brief) → ~60–90 senses; full sense-scoped re-measure of the binding sorts on the panel | ~$25–40 proxy (or human panel) + 1–2 agent-weeks authoring | Sense-scoped hard-sort soundness number exists with disclosed CIs; per-sense typing audit clean of scope confounds |
| **C — kernel-v1** | Full 54-word migration (CARRY/SEED/REVIEW), ~110–140 concepts, molecules re-pointed, alignments re-emitted, manifest gates G1/G2 enforced | 2–4 agent-weeks, <$50 model spend | Corpus builds fail-closed clean; deprecation map total; G1 merge census reported |
| **D — scale handoff** | Scale-track S0 (10k) ingests synset-native; kernel-v1 is the Explicated nucleus; sense-index + per-sense audit strata wired into poc/scale | absorbed into the track's S0 band ($25–150) | Scale track's own S0→S1 gates |

Stage A is deliberately smaller than "split everything": it is the cheapest
build that can *refute* the adjudication's central empirical prediction and
that unblocks the load-bearing measurement. Stages B–D buy coverage, not new
information about whether the mechanism works.

### 6.2 Honest risks

1. **Clustering judgment reintroduces scope ambiguity.** WN's over-fineness
   forces within-frame clustering (R3), which is an authoring act. Mitigated
   by the hard frame-disjointness rule, listed member synsets, and
   `excludedSenses` closure — but a badly drawn cluster is still possible
   and would surface as a V-B disagreement. [STIPULATED mitigation]
2. **Profile-1 may not distinguish some sense pairs** (G1 merges). If
   frequent, the "one concept per sense" norm collides with the encoder's
   expressivity and the honest output is a measured merge census, not a
   silent workaround. Expected rare at kernel scale for the frame-distinct
   senses; unknown for within-frame near-neighbours. [EXTRAPOLATION —
   resolved by Stage A/C builds]
3. **Instrument risk is inherited, not solved.** Every judgment interface in
   this programme has failed at first contact; V-A/V-B ride on the v2.2
   pilot outcome or the human panel. Sense-splitting removes one construal
   channel (the one it targets); Opus-4.8's construal behaviour remains
   unmeasured until the pilot runs. [MEASURED history; STIPULATED sequencing]
4. **Authoring is the scarce resource.** If Stage A shows >3 minted senses
   per polysemous word are genuinely needed, Stage B/C authoring roughly
   doubles. The mitigation is R4's selection discipline — mint for need,
   close scope by exclusion lists. [EXTRAPOLATION]
5. **The deeper risk is that the typing is unsound *per sense*.**
   Sense-splitting fixes scope, not content. A bad V-B number after
   splitting would be the first genuine (non-artifactual) negative
   correctness signal on the binding sorts — that is a feature of the
   design, not a failure mode, and it is exactly what the programme should
   want to know early. [STIPULATED]
6. **Dangling deprecations.** Any consumer left pointing at a deprecated
   `urn:kernel-v0:` word concept re-imports the scope bug. Mitigated by the
   total deprecation map + a repo grep gate in the Stage-C build. [STIPULATED]

### 6.3 Go/no-go read (this designer's, offered for maintainer approval)

**GO on Stage A.** [STIPULATED ruling, ASM-1909; confidence 0.8] It is
maintainer-required direction regardless of outcome; it costs ≤$10 + 2–3
agent-days; it is decisive on the adjudication's 5/12 prediction in both
directions; it unblocks the one load-bearing quantity (sense-scoped binding
soundness) that both the correctness track and any future typing adoption
need; and it touches neither the encoder pin nor any frozen record. Stages
B–D are gated, not approved, by this document. Consistent with the
adjudication's §D: no further prose iteration or judgment spend on unsplit
polysemous concepts; the v2.2 pilot decision is untouched. **No feasibility
conclusion is stated or implied on CORRECTNESS or EFFICIENCY.**

---

## Self-check gate (governance)

Every load-bearing claim above carries MEASURED / LIT-BACKED / STIPULATED /
EXTRAPOLATION; design choices and rulings are STIPULATED, never MEASURED;
forward claims name their resolution path. Previously-unpinned
training-knowledge citations (break's 59 senses; FrameNet's
Compliance-vs-Cause_to_fragment split) are now pinned against
`data/lexical-wn31` and `data/onto-framenet` bytes. The assumption block
`docs/next/design/asm-sensesplit-1900-1909.json` uses the four registry tags
(MEASURED | LIT-BACKED | STIPULATED | EXTRAPOLATION), owner designer-4,
range verified free at emission (max registered id 1897); registration is
the coordinator's, with commit. No git actions in this pass. No mechanical
verdict is modified; kernel-v0 and all frozen lineages stand untouched.
