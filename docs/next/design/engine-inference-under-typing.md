# Engine Inference Under Typing (ENGINE-INF) — DESIGN

**Role: Fable DESIGN agent (designer-4), 2026-07-12; REVISION-1 by the same
design role, 2026-07-13, in response to the cross-vendor codex FIX-FIRST
freeze review (3 blockers; `poc/gpt56-review/e0-freeze/REVIEW-SUMMARY.md`).
This is a DESIGN for the maintainer to freeze — not a prereg, not an
execution, and it issues no feasibility conclusion on CORRECTNESS or
EFFICIENCY. Nothing here modifies the encoder pin, kernel-v0/kernel-v1, the
RULES-1 certificate, any frozen record, or any registered verdict.
Maintainer acceptance: issue #26 items D2+D3.** Assumption blocks:
`docs/next/design/asm-engineinf-1950-1969.json` (original, owner designer-4)
and `docs/next/design/asm-engineinf-r1-2034-2049.json` (REVISION-1, owner
designer-4; range 2034–2049 verified free at emission — max ASM id found
registered or reserved anywhere in the repo is ASM-2033; repo-wide grep for
`ASM-20[3-9][0-9]` returns nothing above 2033). Amendments below are marked
**[R1]**; where REVISION-1 conflicts with 2026-07-12 text, REVISION-1
governs.

Epistemic tags: **[MEASURED]** read from committed bytes this tick;
**[DERIVED]** follows from measured bytes by stated reading/arithmetic;
**[STIPULATED]** a design choice or pre-registration, never evidence;
**[EXTRAPOLATION]** forward claim with its resolution path named;
**[ASSESSMENT]** this designer's judgment, one model's opinion.

**Sources verified at source this tick:**
`poc/rules-1/{twin_engine.py,certificate.py}` (the certified deterministic
engine + the inverted-DECONF certificate, 858/858 vs third-party CLUTRR
gold); `docs/next/analysis/rules2-interpretation.md` + `registry/
assumptions.jsonl` rows ASM-1851/1933/1939 (the deflationary knull
byte-identity and its pre-registered re-activation condition);
`data/kernel-v1/` (Stage-A sense-split corpus: 11 sense concepts,
`typing/ck-ufo-sidecar.jsonl`, `typing/soft-type-per-sense.jsonl`,
`concepts/break.{violate,shatter,…}.json`);
`docs/next/design/sense-split-first-construction.md` (ASM-1884/1900–1909);
`docs/next/protocol/blocking-pilot-before-freeze.md` (ASM-1830..1836);
`docs/next/feasibility-synthesis-v6.md`; `data/lexical-wn31/manifest.json`
(WN 3.1 pinned, sha `3f7d8be8…`, incl. `index.sense` SemCor tag counts and
structural axiom extraction); `docs/next/arch/sparq-estate-landscape.md`
(sparq-reason typed-inference path).

---

## R1. REVISION-1 (2026-07-13) — blocker → fix ledger

Cross-vendor review verdict: **FIX-FIRST, 3 BLOCKERS**
(`poc/gpt56-review/e0-freeze/REVIEW-SUMMARY.md`, codex/GPT-5.6, reviewing
this design plus the quarantined 2026-07-12 exploratory execution). Each
blocker, and where its fix now lives:

| # | blocker (reviewer's finding) | fix | where |
|---|---|---|---|
| B1 | **Instrument validity.** The K / B-wn vs D-word contrasts change typing SOURCE and sense-tag ACCESS together, not sense-splitting alone; no arm pair isolates sense-splitting per se. | A genuinely matched pair: **K vs K-lemma-dom / K-lemma-union** — the SAME pinned kernel axiom module, the SAME compiler input (including the gold sense tag), the same engine/scorer/items; the collapsed arms differ from K ONLY in that their relation inventory is one-per-lemma, with signatures derived from K's own per-sense constraint sets by pinned mechanical collapse rules. Endpoint EP-A (co-primary) is scored on this pair. K vs B-wn (EP-B, co-primary) is retained and relabelled for what it isolates: typing-source content GIVEN sense-split structure and identical tag access. D-word arms are demoted to descriptive context. | §1.3, §1.3.1, §2.3 [R1]; ASM-2101/2036 |
| B2 | **K-shuf control.** A single fixed rotation is insufficient; "K beats K-shuf" is not a binding PASS. | The single rotation is retired. The control is the **exhaustive family of composite within-lemma derangements** of the per-sense domain/range constraint sets — D(5)·D(2)³ = 44 members from the measured 5/2/2/2 sense inventory [DERIVED] — with a prespecified binding superiority gate **C-SHUF**: on typing-active confirmatory cells, K's cell-level correctness must strictly exceed EVERY family member's (the 100th percentile of the derangement distribution), with the derangement-null empirical quantile p = 1/(|S|+1) ≈ 0.0222 ≤ 0.05 reported; family extension rule pinned if |S| < 19. C-SHUF failure caps the verdict at INCONCLUSIVE with a pre-registered CONTENT-INERT reading. | §4 item 1 [R1]; §2.3; ASM-2103 |
| B3 | **Freeze-readiness.** The deterministic 212-item outcome is already known — a "rerun" cannot be pre-registered confirmation; item-level CIs ignore lemma/cross-pair dependence; §2.2 prose conflicted with the implemented G4 scoring rule. | (i) The seen frames (212-item exploratory execution + 17-item pilot slice) are **exploratory-only, permanently**. The confirmatory set is an **unseen holdout H** (SemCor-attested items + mechanically constructed cross-pairs + excluded-sense cells) whose items and gold are constructed and pinned pre-freeze but on which **no engine or scorer execution occurs before the registered run**, with mechanical custody enforcement; because the instrument is deterministic, the binding confirmatory frame is further restricted to **novel outcome-equivalence cells** (cell key not realized in any seen frame) — for items in already-seen cells the outcome is inferable, and counting them as confirmation would be a rerun in disguise. (ii) All interval statements move from item-level i.i.d. binomials to **cell-level analysis with a stratified cluster bootstrap** plus a drop-one-lemma jackknife sensitivity — measured on the seen frame, 56 G1∪G3 items collapse to 19 outcome-equivalence cells, so the dependence is real, not hypothetical. (iii) §2.2 prose now states the implemented set-valued G4 rule (ASM-1997) verbatim; the conflict is resolved in favour of the pinned implementation. | §2.5 (new), §2.2, §2.3 [R1]; ASM-2104/2039/2040/2041 |

**Narrowed exploratory statement (reviewer's CONCERN, adopted verbatim as
the ONLY licensed sentence about the 2026-07-12 exploratory execution):**
*"Exploratorily, given gold sense IDs on the 56 G1/G3 items, K had higher
exact-match (46/56) than B-wn (27/56), D-word-dom (26/56), and D-word-union
(21/56), under partly-constructed gold. This does not isolate
sense-splitting and does not generalize. The registered analysis remains
INCONCLUSIVE until the confirmatory holdout runs."* [MEASURED numbers —
`poc/engine-inference/results/rows.jsonl` sha `8a21d5a3…`, run-result
decision-payload sha `6a2d9561…`, double-run match true; STIPULATED
scope — ASM-2108/2043.] Any prior broader reading (including any
"sense-split signal" phrasing) is superseded; the reviewer's own retraction
of an over-stated read is noted in the review artifact.

**ASM supersession map [STIPULATED — ASM-2100]:** ASM-1996 (single-rotation
K-shuf) superseded by ASM-2103; the decision-rule and kill-criteria content
of ASM-1959/1960 and the frame/interval content of ASM-1999/2000 superseded
by ASM-2102/2039/2040 (the divergence-certificate-before-scoring and
double-run disciplines they carry are retained); ASM-1955/1956/1963/1966
amended by ASM-2101/2036/2045/2046. All original ASMs otherwise stand.

**Registry deltas required at re-pin (coordinator action, central custody):**
arms list +K-lemma-dom, +K-lemma-union, K-shuf → derangement family
(control-evaluation set, not an arm); endpoints → EP-A/EP-B co-primary with
new `/analysis/*` fields (delta_k_minus_klemdom_pri, delta_k_minus_klemun_pri,
their cluster LB95s, cshuf_p, cshuf_n_ge_k, n_cells_confirmatory,
kill_e1_fired/e2a/e2b, holdout custody gate); kill_criterion_verbatim
replaced per §2.3 [R1]; n_planned updated after the pre-freeze H extraction;
new pins (SemCor corpus hash, holdout extractor, K-lemma modules, derangement
manifest, items-H/gold-H); analysis script and prereg_doc shas recomputed;
blocking pilot re-run artifact (§5 [R1]). Status remains DRAFT until the
re-run pilot passes and the maintainer freezes.

---

## 0. The question, and why it is the missing load-bearing experiment

Two facts define the hole this design fills.

**Fact 1 — the programme has never asked whether the kernel's TYPING makes
the ENGINE draw CORRECT conclusions.** [MEASURED absence] The RULES-1
certificate established that the engine is *non-inert and exact at scope*
(858/858 vs third-party gold; entailed decisions irreproducible from stated
bytes) — over a kinship TBox whose typing content is thin (gendered
domain/range on two relations). The typing lane (g2) has measured *judge
agreement about prose renderings* of typing records, never *engine closure
correctness under those records*. The two lanes have never met: no
experiment has ever put the kernel's distinctive typing content through the
deterministic engine and scored the engine's conclusions against
third-party gold. That is the correctness thesis's most direct question,
and it is unasked.

**Fact 2 — every kernel-specificity probe has come out
content-not-structure because the sources it compared derive the SAME
closure.** [MEASURED] Four seams, four deflations: f2b-transfer (lift
carried by authored answer-bearing content), DECONF-B (GS-A projected
store ≡ kernel arm, identity 1.0), CASC-0′ (gloss ≡ plain), and — the
sharpest — rules-2-knull (kernel TBox and plain-dictionary TBox derive a
**byte-identical** training corpus, 21,780/21,780; the GPU contrast is 0
identically and prohibited, ASM-1851/1933). The controls kept coming out
byte-identical *because on the closed kinship inventory a flat dictionary
already contains everything the kernel's structure contributes*. ASM-1939(a)
pre-registers the only forward path: **kernel-specific value is askable
only where the two sources derive DIVERGENT closures.**

This design constructs that divergence seam deliberately and makes one
experiment answer both questions at once:

> **ENGINE-INF asks: on inputs where kernel-v1's sense-split typing and a
> matched non-kernel source derive divergent engine closures, whose closure
> is correct by third-party gold?** If the kernel's — that is the
> programme's first kernel-specific-value datum, measured through its only
> 6-for-6-valid channel (deterministic engine vs third-party gold, no LLM
> judge anywhere). If not — closures converge, or a non-kernel baseline
> matches — that is the honest, pre-registered trigger for the D3(b)
> thesis reframe (grounded-content + engine, not kernel-specific
> structure). [STIPULATED — ASM-1950, ASM-1961]
>
> **[R1]** This question decomposes into two co-primary matched contrasts —
> sense-splitting per se (K vs its own lemma-collapses, EP-A) and
> kernel-authored content given splitting (K vs B-wn, EP-B) — scored on an
> unseen holdout only (§2.3, §2.5). The affirmative reading above requires
> BOTH.

The construction insight [ASSESSMENT, grounded in MEASURED bytes]:
**sense-splitting with correct per-sense typing is exactly what a
word-level source cannot replicate.** kernel-v1 Stage-A exists precisely
here (ASM-1884: a concept is a sense, not a word): `break.violate`'s own
identity-bearing explication says the object *is words* ("Y is words; these
words say: people cannot do some things…" [MEASURED,
`data/kernel-v1/concepts/break.violate.json`]), while `break.shatter`'s
says the object comes apart into many small pieces. A word-level `break`
relation must carry ONE type signature and therefore either over-derives
(flags "X broke a promise" as a category error) or under-derives (cannot
flag "the promise shattered into pieces"). The divergence is structural,
not incidental — and unlike the kinship inventory, it cannot close to
byte-identity, because the dictionary side has no vocabulary in which to
state the per-sense axioms at all.

---

## 1. The divergence seam — construction

### 1.1 The inference substrate (engine unchanged in E0)

The reasoner is the **certified RULES-1 engine** at its frozen closed
inventory — `poc/rules-1/twin_engine.py` (Python twin, conformance-agreed
with sparq-reason on 1,207/1,207 cases [MEASURED certificate]) — used
exactly as certificate.py uses it: compile a TBox from `kot-axiom/1`
records, close small stated worlds, read facts/conflicts/refusal codes.
Closure operations consumed, all inside the certified inventory
[STIPULATED — ASM-1958]:

| op | rule | ENGINE-INF role |
|---|---|---|
| O1 typed entailment | R-DOM / R-RNG | derive the class of an argument from the sense relation's signature |
| O2 typed disjointness | CAX-DW | detect category-error worlds ("the promise shattered") as ERR_CONFLICT |
| O3 refusal | ERR_INSUFFICIENT_PREMISES / ERR_RULE_UNIMPLEMENTED | fail closed on excluded senses and un-inventoried structure |
| O4 subsumption (secondary, descriptive in E0) | R-SUBP | per-sense coarse-event subproperty entailments |

No new rule kind, no engine version change, no encoder touch in Stage E0.
Class-hierarchy reasoning (cax-sco) is NOT in the certified inventory;
noun-class memberships are therefore **precomputed mechanically** from
pinned WN31 hypernym axioms into flat stated `cls` facts by a compiler
**shared byte-identically by all arms** (§1.4). The E1 in-engine
disambiguation rule (§5, R-DISAMB) IS an engine version change and is
staged behind its own conformance + mini-certificate gate.

### 1.2 The typed axiom modules — where each arm's "source" lives

The soft-type sidecar (`typing/soft-type-per-sense.jsonl`) is
`binding:false` with `forbidden_effects` including `derive-disjointness`
and `assert-type` [MEASURED]. **It is NOT consumed.** Consuming it as
axioms would violate its own contract and taint the arm. Instead
[STIPULATED — ASM-1952]:

- **The kernel arm's hard module** (`data/axioms-engineinf-v0/`, new,
  experiment-scoped, kot-axiom/1) is authored by the explicator role from
  the **identity-bearing explication clause content** — the kernel proper,
  not the annotation layer. `break.violate` range → `C_words` because the
  explication's first clause types Y as WORDS; `break.shatter` /
  `break.malfunction` range → `C_material` (many-small-pieces / device
  clauses); `find.discover` object → `C_info`; etc. Bridge classes
  (`C_words`, `C_material`, `C_info`, …) are minted classDeclarations with
  `disjointWith` pairs anchored on WN31's third-party physical/abstraction
  top split. Every axiom cites its explication clause in a comment; the
  module is hash-pinned and is itself part of "the kernel source" for this
  experiment — the shuffled control permutes exactly it.
- This promotion (explication clause → binding domain/range for the
  experiment's closed world) is a **disclosed experimental stipulation**,
  not a change to the kernel's authority discipline: the sidecar's
  rank-only status in the corpus is untouched; the module lives under the
  experiment, is consumed only by it, and dies with it.

### 1.3 The arms [STIPULATED — ASM-1955, ASM-1956; amended by ASM-2101/2036/2037 [R1]]

All arms share: the same engine bytes, the same shared world-compiler, the
same scorer, the same item bank, **and the same compiler input record per
item, including the gold sense tag [R1]**. They differ ONLY in the source
module compiled into the TBox and in whether that module's relation
inventory is per-sense or per-lemma (a per-lemma inventory is constitutively
constant in the sense tag — the tag is received but has nowhere to route).

| arm | source | sense-split? | typing | what it embodies |
|---|---|---|---|---|
| **K** | kernel-v1 Stage-A + `axioms-engineinf-v0` | yes (11 senses) | per-sense, explication-derived | the kernel |
| **K-lemma-dom** [R1] | **the same** `axioms-engineinf-v0` per-sense constraint sets, lemma-collapsed by the pinned dominant-sense rule (§1.3.1) | no — one relation per lemma | the dominant minted sense's kernel signature applied lemma-wide | **the sense-split isolator (committed collapse)**: everything K has, minus the split |
| **K-lemma-union** [R1] | the same module, lemma-collapsed by the pinned agreement rule (§1.3.1) | no | a slot constraint survives iff ALL minted senses of the lemma carry the identical constraint | **the sense-split isolator (cautious collapse)** |
| **D-word-dom** | plain dictionary | no — one relation per lemma | the SemCor-dominant sense's signature (tag_cnt from pinned `index.sense`) | descriptive context [R1]: the strongest committed word-level dictionary (the pi:011 shape) |
| **D-word-union** | plain dictionary | no | union / least-common-subsumer signature (effectively untyped) | descriptive context [R1]: the cautious word-level dictionary |
| **B-wn** | WordNet 3.1 bytes only, zero kernel authoring | yes (same sense URNs) | mechanical: WN verb sentence-frames (Somebody/Something slots) | **the kernel-source decider**: given sense-split structure and identical tag access, does kernel-authored typing content beat the best mechanical non-kernel content? |
| **K-shuf family** [R1] | K with per-sense domain/range constraint-set assignments deranged within lemma — the FULL composite derangement family (§4 item 1), not one rotation | yes | deranged | mandatory shuffled-kernel control family (typing content destroyed, structure and byte bulk preserved) |

**What each pairwise contrast isolates [STIPULATED — ASM-2101/2036 [R1]]:**
K vs K-lemma-{dom,union} isolates **sense-splitting per se** (same source
content, same tag access, same everything else — the collapse rules are
deterministic functions of K's own pinned module). K vs B-wn isolates
**typing-source content given sense splitting** (both split, both routed by
the same tag, different authoring). K vs D-word arms isolates nothing by
itself (source and split vary together) and is retained only as descriptive
continuity with pi:011 and the rules-2-knull comparator construction. No
single-contrast sentence may blur these scopes.

#### 1.3.1 The lemma-collapse rules (the B1 fix, mechanical) [STIPULATED — ASM-2101 [R1]]

Both collapsed arms are compiled from the pinned
`data/axioms-engineinf-v0/kernel/sense-*.json` constraint sets by a pinned
collapse compiler — no new authoring act anywhere; a fresh authoring pass
here would reopen the very confound the pair exists to close.

- **K-lemma-dom:** the lemma relation's domain/range constraint set := that
  of the lemma's **dominant minted sense**, where dominance = the maximum
  sum of pinned `index.sense` tag_cnt over the concept's `wn31Synsets`
  (concepts map to one or more synsets, e.g. break.interrupt covers three);
  ties break to the lexicographically smallest concept URN. This is the
  identical third-party ranking rule D-word-dom already uses — no new
  source enters. The winning sense per lemma is a build-time MEASURED
  constant recorded in the arm manifest.
- **K-lemma-union:** a domain (resp. range) constraint survives iff every
  minted sense of the lemma carries the identical constraint class on that
  slot; otherwise the slot is unconstrained. (In the flat bridge-class
  vocabulary, distinct classes have no common subsumer below top, so
  agreement-or-nothing IS the least-common-subsumer rule.) From the pinned
  module bytes this yields, e.g., no break/find/make constraints (their
  senses disagree or refuse) and a surviving `range person` on friend
  [DERIVED from the committed constraint sets; confirmed at build].
- **Everything else byte-shared:** classDeclarations, disjointness pairs,
  and the `any-<lemma>` coarse relations are inherited unchanged; only the
  per-sense relation axioms are replaced by the collapsed per-lemma axioms.
  The collapsed relation covers every occurrence of the lemma — including
  excluded senses (a lemma-level source cannot mark coverage; that is part
  of what sense-splitting is). To keep EP-A a pure TYPING contrast, its
  frame is restricted to G1∪G3 cells (§2.3); the refusal-vs-assertion
  consequence of splitting is reported separately in the honesty secondary,
  never inside EP-A.
- **Matched tag access, proven mechanically:** all compilers receive the
  identical item record (with `gold_synset`). The pilot's **sense-tag
  insensitivity canary** (§5 PC-4′) perturbs the gold sense tag and
  requires: K-lemma and D-word compiled worlds byte-identical (they may not
  use the tag), and K / B-wn relation URNs changed on remapped items (they
  must route by it). Both directions have teeth.
- **Disclosed residual:** the collapsed arms carry fewer relation-typing
  axioms than K (one per lemma vs one per sense) — byte bulk is not
  identical across this pair. Content-vs-bulk is the derangement family's
  burden (§4 item 1), which preserves bulk exactly; the pair and the family
  jointly cover what neither covers alone.

The mandatory **kernel-as-text control is structurally N/A**: there is no
LLM/host consumer anywhere in the instrument — no prompt for the text to
enter. Recorded as an explicit `not_applicable` with structural reason per
the blocking-pilot protocol (downgrades the pilot verdict to
PASS-WITH-FLAGS, never a silent pass). [STIPULATED — ASM-1963]

**Why B-wn is load-bearing** [STIPULATED — ASM-1956, amended by ASM-2102
[R1]]: beating only the D-word arms licenses nothing under REVISION-1 —
that contrast varies source and split together (B1); the sense-structure
question now belongs exclusively to the matched K vs K-lemma pair (EP-A).
The kernel-SPECIFIC claim requires beating the best matched source constructible
*without kernel authoring*. If B-wn matches K, the honest reading is
"sense-structure-specific, not kernel-specific" — a refined deflation and a
direct D3(b) input. Scale-S0 measured WN-only typing at 0% coverage on
identity/dependence categories [MEASURED, synthesis v6 §4], so B-wn is not
a strawman in either direction: it plausibly matches K on coarse
physical/abstract cells and plausibly cannot express the finer per-sense
commitments.

### 1.4 Items and the input grade (the honesty seam, stated plainly)

An item = one attested (or constructed-anomaly, or excluded-sense)
occurrence of a Stage-A lemma with its argument nouns:

```
item: "break a promise"  (from WN31 gloss example of v-02572443)
world: rel(x, <arm's relation URN>, p) + cls(p, <WN-derived class facts>)
       + una(...)
gold:  sense = urn:kernel-v1:break.violate (by attachment: the example
       belongs to that synset); verdict = CONSISTENT; entailed typing of
       p per WN hypernym top-split = abstraction-side
```

**Input grade S (Stage E0):** the item carries its third-party gold sense
tag (WN synset by attachment; SemCor sentence tags on the confirmatory
holdout [R1]). The K and B-wn compilers map gold synset → their sense
relation URN mechanically via the pinned `wn31Synsets` field (or → NONE for
`excludedSenses`, in which case the arm's fail-closed behaviour is itself
scored). **[R1] Every compiler — including the lemma-level ones — receives
the identical item record with the tag**; a lemma-level relation inventory
is constant in the tag by construction (verified by the sense-tag
insensitivity canary, §5 PC-4′), so access is matched and only the split
varies within the K vs K-lemma pair. The D-word arms' lemma collapse is the
same projection logic the rules-2-knull leg used and is the definition of
that (descriptive) comparison, not a handicap. [STIPULATED — ASM-2101]

Disclosure, verbatim, to be carried into the record: **grade-S tests typed
closure correctness DOWNSTREAM of sense identification.** The E0 claim, if
affirmative, is scoped "given third-party sense identification, the
kernel's per-sense typing makes the engine's closure correct where matched
non-kernel sources' closures are wrong." In-engine sense identification
(grade W: word-level input, sense resolved by the engine's own typed
elimination) is the E1 increment, not smuggled into E0's claim.

### 1.5 Worked example — the money contrast [DERIVED from the bytes cited]

Worlds (nouns typed by the shared compiler from WN31 hypernyms:
`promise` → abstraction-side → `cls(p, C_words)`; `glass` →
physical-side → `cls(g, C_material)`; `C_words disjointWith C_material`):

- **W1 "X broke a promise"** — gold sense break.violate, verdict
  CONSISTENT.
  K: `range(break.violate)=C_words` ⇒ R-RNG derives `cls(p, C_words)` —
  concordant with stated; no conflict. **Correct.**
  D-word-dom (`range(break.word)=C_material`, shatter-dominant): derives
  `cls(p, C_material)` ⇒ CAX-DW fires against `C_words` ⇒ flags a category
  error on a perfectly fine sentence. **Wrong (over-derivation — the
  pi:011 defect, now measurable as an engine error, not a prose
  disagreement).**
  D-word-union: derives nothing. Correct here, by vacuity.
- **W2 "the promise shattered into pieces"** — constructed cross-pair,
  gold verdict ANOMALOUS (per the §2 gold rule).
  K: `range(break.shatter)=C_material` ⇒ derives `cls(p, C_material)` ⇒
  CAX-DW vs `C_words` ⇒ **ERR_CONFLICT = ANOMALOUS. Correct** — "you can
  break a promise, but a promise cannot shatter into pieces."
  D-word-dom: flags it — but it flags W1 identically: it cannot separate
  the two. D-word-union: silent. **Wrong (under-derivation).**
  B-wn: sentence frames type both senses "Somebody ----s something" ⇒ no
  disjointness derivable ⇒ silent on W2. [EXTRAPOLATION at pilot
  resolution — this is precisely what PC-2/PC-3 verify on real bytes.]
- **W3 "his voice broke"** — gold sense in `excludedSenses` (53 excluded
  break siblings [MEASURED]).
  K: compiler maps to NONE ⇒ engine refuses (fail-closed). **Correct =
  REFUSE** (the kernel does not cover the sense and says so).
  D-word-dom: happily derives `cls(voice, C_material)` — a confident wrong
  assertion, exactly what honesty-first scoring exists to punish.

The word-level engine either over- or under-derives on every such pair;
only sense-split correct typing separates them. K is NOT correct by
construction: any attested WN example object whose hypernym class
contradicts the kernel's authored range (candidate stress cells: "break
the speed limit / the record / his spirit") makes K fire a false
ANOMALOUS — a genuine, wanted, per-sense typing-unsoundness signal
(sense-split design risk 5). The instrument can find the kernel wrong.

---

## 2. The deterministic channel — gold, scoring, endpoints

### 2.1 Gold sources — third-party bytes, mechanical rules, no LLM judge

[STIPULATED — ASM-1954; substrate MEASURED — ASM-1953]

| gold | source | independence status |
|---|---|---|
| **G1 sense-by-attachment** | WN31 gloss example sentences (pinned, sha `3f7d8be8…`, Princeton, predates kernel-v1) — an example attached to a synset carries that synset as its sense label; E1 adds real SemCor sentence tags (new pin) | third-party bytes; kernel-v1 keys senses on the same synset ids (identity shared, disclosed), but the TYPE content under test is kernel-authored |
| **G2 argument typing** | WN31 hypernym closure to the physical_entity / abstraction top split (pinned structural axioms) | third-party structure; not consumed by kernel authoring (explications cite NSM primes, sidecar cites BFO/SUMO anchors) — verified at pilot by grep over authoring provenance |
| **G3 anomaly labels** | constructed by a pre-registered mechanical rule over G1+G2: a world is ANOMALOUS iff the verb-sense's attested example-object class and the item's object class fall on opposite sides of the WN top split | the BYTES are third-party; the RULE is stipulated — disclosed as constructed-rule gold, upgraded at E1 by a VerbNet selectional-restriction pin (third-party published restrictions, e.g. break-45.1 Patient [+concrete]) and a ~30-item human spot-audit |
| **G4 refusal gold** | excludedSenses membership (mechanical from the pinned sense-index) + un-inventoried structure | mechanical; correct answer = REFUSE |

**Provenance-separation rule** [STIPULATED — ASM-1957, load-bearing
against self-rigging]: B-wn's typing may consume WN **sentence frames
only**; gold G2/G3 consume **hypernym paths and example objects only**. No
arm's compiler may read any gold field; enforced by the poisoned-gold
canary (perturb gold bytes → every arm's compiled TBox+worlds must remain
byte-identical; a diff fires the gate). This is the PC-4 planted-violation
discipline applied to the seam where circularity could hide.

### 2.2 Scoring [STIPULATED — ASM-1959, ASM-1962; amended by ASM-2106/2041 [R1]]

Per item per arm, the engine emits a verdict in
`{CONSISTENT, ANOMALOUS(ERR_CONFLICT), REFUSE(code), typed-answer}` plus
derived class facts. On G1/G3 cells: exact match against gold verdict; O1
cells additionally exact-match the derived class against G2. **[R1] On G4
(excluded-sense) cells the gold is set-valued, per the implemented and
pinned scorer (ASM-1997): REFUSE(code) is correct AND vacuous CONSISTENT
(no conflict, no derived class assertion) is correct; ANOMALOUS or any
confident derived assertion is wrong.** The 2026-07-12 prose here read
"exact match against gold verdict" without the G4 qualification, in
conflict with the implementation; the conflict is resolved in favour of the
implementation, whose rationale stands: scoring bare REFUSE as the only
correct G4 answer would gift K wins purely for coverage gaps, and scoring
vacuous CONSISTENT as wrong would punish broader-coverage arms for covering
more. Deterministic engine ⇒ no seeds; double-run byte-identity required
(certificate discipline).

**[R1] Effective sample unit — the outcome-equivalence cell (ASM-2106).**
Because the whole instrument is deterministic, every item in the same
**cell** — the tuple `(gold sense synset, undergoer top-split side class,
undergoer wn-kind class, item kind)`, i.e. the full arm-input equivalence
class up to entity renaming — produces byte-identical worlds and therefore
identical verdicts in every arm. Item counts overstate information:
measured on the seen frame, the 56 G1∪G3 items collapse to 19 distinct
cells. All registered inference is therefore at CELL level (one observation
per cell, census item counts reported descriptively alongside); interval
statements use a stratified (by item kind) percentile cluster bootstrap
over cells, B = 10,000, pinned seed 20260713, plus a drop-one-lemma
jackknife reported as a sensitivity (disclosed as coarse — 4 lemmas). Any
co-primary frame with fewer than 8 cells is INSUFFICIENT-CLUSTERS: that
endpoint cannot PASS and is reported descriptively only.

Two scores, pre-registered:
- **Primary: raw exact-match correctness** on the divergent set (below).
- **Secondary: honesty-weighted score** per the issue-#18 direction —
  wrong assertion costs 1, refusal costs 0.5, correct costs 0 (penalty
  form fixed at freeze). Reported for every arm; D-word-dom's confident
  wrongness vs K's fail-closed refusals is exactly what this separates.

### 2.3 The divergence certificate and the co-primary endpoints [R1]

**Divergence certificate (the ASM-1851 leg-1 analog, run before any
scoring):** for each baseline b, `Div(K,b)` = the set of items whose
engine verdict-or-derived-fact set differs between K and b — computed
mechanically, committed as a pinned artifact with per-op and per-lemma
composition. This artifact is the non-vacuousness proof the knull lineage
taught the programme to demand *before* interpreting any contrast.
[STIPULATED]

**[R1] Co-primary endpoints (ASM-2102; superseding the single-primary
form).** All registered contrasts are computed at CELL level (§2.2) on the
**confirmatory novel-cell holdout frame** `(G1∪G3)_H*` (§2.5); the seen
frames are exploratory-only. Frames:

- `F_A^dom` = cells of `Div_dec(K, K-lemma-dom) ∩ (G1∪G3)_H*`;
  `F_A^un` likewise for K-lemma-union.
- `F_B` = cells of `Div_dec(K, B-wn) ∩ (G1∪G3)_H*`.

**EP-A (sense-splitting per se):** paired cell-level contrast K −
K-lemma-x on `F_A^x`, for each x ∈ {dom, union}. The pair shares source,
tag access, compiler, engine, scorer, items; only the split differs
(§1.3.1) — this endpoint, and only this endpoint, licenses a sentence about
sense-splitting.

**EP-B (kernel-authored content, given splitting):** paired cell-level
contrast K − B-wn on `F_B`. Both arms are sense-split and tag-routed; only
the typing-content source differs — this endpoint, and only this endpoint,
licenses a sentence about kernel authoring vs mechanical non-kernel
content.

Decision rule, verbatim [STIPULATED — ASM-2102/2037/2039/2040 [R1];
supersedes the 2026-07-12 bands]:

- **KILL-e1 (holdout adequacy; verdict CONSTRUCTION-ANOMALY):** the
  confirmatory frame `(G1∪G3)_H*` has < 30 items or < 12 cells, or spans
  < 2 closure ops or < 2 lemmas. Checkable PRE-FREEZE at $0 from the
  pinned holdout items+gold alone (no outcomes needed); if it fires
  pre-freeze, the freeze does not proceed and the inventory is extended
  (E2) first.
- **KILL-e2a (sense-split idle; verdict NULL):** `|F_A^dom ∪ F_A^un| < 6`
  cells — K's own per-sense signatures are too homogeneous within lemma to
  diverge from their own collapse; pre-registered reading: *"sense-splitting
  adds no divergent closure at this inventory; the split is idle here."*
  No claim either direction about splitting's value.
- **KILL-e2b (kernel-vs-mechanical unaskable; verdict NULL):** `|F_B| < 6`
  cells or < 10 items — recorded as a D3(b) input (*"sense structure
  suffices; kernel authoring adds no divergent closure here"*), no
  affirmative claim.
- **Gate C-SHUF (binding for PASS-affirm):** over the pinned derangement
  family S (§4 item 1; exhaustive |S| = 44 at this inventory), on the
  typing-active `(G1∪G3)_H*` cells: `#{π ∈ S : corr(π) ≥ corr(K)} = 0`
  — K strictly above the family maximum (the 100th percentile), with the
  derangement-null empirical quantile p = 1/(|S|+1) ≈ 0.0222 reported. If
  C-SHUF fails, the verdict is capped at INCONCLUSIVE with the
  pre-registered flag CONTENT-INERT: *"a kernel with deranged typing
  content matches the kernel; the typing content is not demonstrably
  load-bearing at this inventory."*
- **PASS-A:** for EACH x ∈ {dom, union}: cell-level delta (K −
  K-lemma-x) ≥ +0.20 on `F_A^x` AND its cluster-bootstrap LB95 > 0; AND
  K's cell-level correctness on `F_A^dom ∪ F_A^un` has cluster-bootstrap
  LB95 ≥ 0.80.
- **PASS-B:** cell-level delta (K − B-wn) ≥ +0.20 on `F_B` AND its
  cluster-bootstrap LB95 > 0; AND K's cell-level correctness on `F_B` has
  cluster-bootstrap LB95 ≥ 0.80.
- **No-net-harm (binding for PASS-affirm):** K's cell-level correctness on
  the CONVERGENT `(G1∪G3)_H*` cells is not worse than any arm's by > 0.02.
- **PASS-affirm (full) = PASS-A ∧ PASS-B ∧ C-SHUF ∧ no-net-harm.**
  Licensed sentence fixed in §3.
- **FAIL-A (sense-split deflation):** min over x of the EP-A point delta
  ≤ 0 — K fails to beat at least one of its own lemma-collapses where they
  diverge. Pre-registered reading: *"where per-sense typing derives
  closures its own lemma-collapse does not, it is not more correct;
  sense-splitting per se is not supported at this scope."*
- **FAIL-B (the D3(b) trigger):** EP-B point delta ≤ 0. Reading,
  pre-registered verbatim: *"where the kernel's closure diverges from
  matched non-kernel closures, it is not more correct; the kernel's
  distinctive contribution remains unlocated; the programme thesis
  reframes per D3(b) — grounded content + certified engine, not
  kernel-specific structure."* Honest, valuable, not an instrument
  failure. FAIL-A and FAIL-B can co-fire; each fires only its own
  sentence.
- Anything between the PASS and FAIL bands, or a partial pass (exactly one
  of PASS-A/PASS-B), ⇒ INCONCLUSIVE at scope with the passing endpoint's
  scoped intermediate sentence (§3 ladder) and no affirmative headline.
- **INSUFFICIENT-CLUSTERS (§2.2):** any co-primary frame with < 8 cells
  cannot PASS; reported descriptively.

Both readings of every endpoint are written into the record before any
holdout byte is scored. The secondary endpoints (K vs D-word arms;
honesty-weighted penalties incl. the K vs K-lemma refusal/assertion
contrast on G4; per-op breakdown) are descriptive and capped: beating only
D-word arms licenses NOTHING beyond continuity bookkeeping with pi:011 —
under REVISION-1 not even the old "sense-split typing beats word-level
typing" sentence, since that contrast confounds source and split (B1).

### 2.4 Why this channel and not a host [ASSESSMENT, grounded in the measured ledger]

The programme is 6-for-6 valid on deterministic measurement channels and
0-for-5 on runtime-judgment interfaces (synthesis v6 §2.3; rules-2
interpretation §4). ENGINE-INF has **no host, no judge, no elicitation, no
verifier dialogue** — the entire instrument is: pinned bytes → certified
engine → string-equality scoring vs third-party-derived gold. Every
interface it keeps is one the programme has already instrumented cleanly;
every interface class that has ever failed is absent by construction. It
is also the cheapest possible venue for the kernel-specificity question:
the seam is created in the TBox, where authoring is days, not in a
training corpus, where the same divergence costs a GPU campaign.

### 2.5 [R1] The confirmatory unseen holdout H (the B3 fix) [STIPULATED — ASM-2104/2039; expectation ASM-2110]

The 2026-07-12 exploratory execution computed every outcome on the 212-item
gloss-example census, and the 17-item pilot slice is likewise seen. A
"registered rerun" of those bytes would confirm nothing — deterministic
instruments make reruns free and evidentially empty. REVISION-1 therefore
splits the record permanently:

- **Exploratory frames (seen, closed):** the 212-item census + the 17-item
  pilot slice. Reported under the §R1 narrowed sentence only. No registered
  verdict consumes them.
- **Confirmatory frame H (unseen):** constructed as below, scored for the
  first time inside the registered run.

**Construction (all mechanical; no human item authoring; no new kernel
authoring; $0 model spend):**

- **H1 (attested):** occurrences of the 4 Stage-A lemmas in **SemCor**
  (brown1/brown2/brownv sentence corpus — a NEW third-party pin: network
  fetch + sha-pin; the corpus predates the programme). SemCor sense keys
  map to WN3.1 synsets mechanically via the pinned `index.sense` (sense
  keys are version-stable; unmappable keys → logged exclusion). The
  extractor applies the ASM-1991 argument rules to the SemCor sentence.
  This pulls the E1 "real SemCor sentence tags" upgrade forward into E0,
  where the confirmatory set needs it.
- **H2 (constructed-anomaly):** the pre-registered G3 cross-pair rule
  applied to H1 objects (sense-side unanimity assessed over the union of
  seen gloss-example objects and H1 objects; pairs generated from H1
  objects only).
- **H3 (refusal):** SemCor occurrences of the 4 lemmas tagged to
  `excludedSenses` (feeds the honesty secondary and full-divergence
  bookkeeping; excluded from the co-primary frames as before).
- **Decontamination rule:** any H item whose (predicate synset, object noun
  lemma) pair occurs in ANY seen item is excluded, logged.
- **Novel-cell restriction `H*`:** determinism means an H item whose CELL
  (§2.2 key) was realized in a seen frame has an inferable outcome — scoring
  it as confirmation would be a rerun in disguise. The binding confirmatory
  frame `(G1∪G3)_H*` is the H cells whose key occurs in NO seen frame.
  Full-H numbers are co-reported descriptively.

**Custody (mechanically enforced, not promised):** (1) build order pins the
K-lemma modules and derangement manifest — deterministic functions of
already-pinned bytes — BEFORE the SemCor extraction, and the kernel module
predates SemCor's entry into the repo by commit history [MEASURED at
freeze]; (2) the holdout extractor is a separate entrypoint that does not
import the engine or scorer — items-H + gold-H are constructed and
sha-pinned pre-freeze WITHOUT computing any outcome (gold is a function of
third-party bytes + pinned rules, not of engine behaviour); (3) at freeze,
a mechanical repo scan asserts no results file contains any H item id;
(4) the frozen runner refuses to start if rows for any H id already exist,
and emits the H divergence certificates before scoring, inside the same
frozen pipeline; (5) KILL-e1 (holdout adequacy) is evaluated pre-freeze
from items-H + gold-H alone — counting items and cells requires no
outcomes. Machinery validation without peeking is PC-6: the full pipeline,
engine included, runs end-to-end on three pinned DECOY lemmas (draw, hold,
cut — verified members of neither Stage-A nor the kernel-v0 39-concept
panel), whose outcomes touch no endpoint and are quarantined.

**What H costs [ASSESSMENT]:** one third-party corpus pin (network fetch +
sha), an extractor extension, and CPU-trivial engine runs — $0 model spend
throughout; no human authoring anywhere on the critical path. The one open
empirical risk is H1 yield (ASM-2110, EXTRAPOLATION: SemCor's tag_cnt mass
on these lemmas — e.g. make v-02566500 alone carries 508 tags — makes ≥ 30
eligible items plausible); the risk is resolved pre-freeze by the KILL-e1
count at $0, and a shortfall stops the freeze rather than weakening the
record.

---

## 3. The two co-primary endpoints — what each outcome means [R1]

[STIPULATED — ASM-1961 as amended by ASM-2102/2042, load-bearing]

The claim ladder, fixed before any holdout byte is scored (each rung
licenses exactly its own sentence, never a rung above it):

| outcome | licensed sentence (scoped) | programme consequence |
|---|---|---|
| PASS-affirm (PASS-A ∧ PASS-B ∧ C-SHUF ∧ no-net-harm) | "On this inventory, on unseen items, sense-splitting the kernel's own typing content makes the engine's closures more correct than lemma-collapsing it, AND the kernel-authored per-sense content makes them more correct than matched mechanical non-kernel content — both by third-party-derived gold." | **First kernel-specific-value datum** in programme history, now with sense-splitting isolated per se; the four-seam content-not-structure ledger gains its first structure-side entry; re-opens the attribution chain the knull byte-identity closed |
| PASS-A alone | "Sense-splitting per se improves closure correctness given the kernel source, at this scope." — nothing about kernel authoring vs other sources | INCONCLUSIVE overall; EP-B residual named |
| PASS-B alone | "Kernel-authored typing content beats mechanical WN-frame content among sense-split sources, at this scope." — nothing about splitting per se | INCONCLUSIVE overall; EP-A residual named |
| FAIL-A | "Where per-sense typing derives closures its own lemma-collapse does not, it is not more correct; sense-splitting per se is not supported at this scope." | direct input to the sense-split lane (ASM-1884 line) |
| KILL-e2b / FAIL-B | "Sense-structure (or nothing) suffices; kernel authoring adds no divergent-and-correct closure at this scope." | The honest **D3(b) reframe trigger**: the thesis candidate becomes grounded-content + certified-engine, with the kernel as one authoring pathway among several — a pre-registered maintainer decision input, not a designer's choice |
| KILL-e2a | "Sense-splitting is idle at this inventory (its own collapse derives the same closures)." | extend inventory before re-asking EP-A |
| C-SHUF fail (CONTENT-INERT) | "Deranged typing content matches the kernel; content not demonstrably load-bearing here." | verdict capped INCONCLUSIVE; design treated as dead at this inventory pending redesign |
| KILL-e1 | instrument cannot ask at this holdout (adequacy) | stop pre-freeze at $0; extend inventory (Stage-B senses / E2) |
| K loses to gold outright on divergent cells | first genuine per-sense typing-unsoundness signal through a valid instrument | feeds the sense-split lane's V-B question with engine-grade (not judge-grade) evidence |

**Relation to ASM-1851/1939(a):** a committed divergence certificate over
this inventory is exactly the "fresh leg-1 artifact showing divergence"
that ASM-1851 names as the mechanical re-activation condition for the
rules-2 knull GPU leg. ENGINE-INF therefore doubles as the gatekeeper for
the train-time kernel-specificity twin (E3 below): if closures diverge
here, a future rules-2-shaped campaign on THIS inventory would have
non-byte-identical kernel vs dictionary corpora — the contrast rules-2
could not buy at any price. [EXTRAPOLATION — ASM-1965; direction only,
its own record when it comes.]

---

## 4. Controls and threat model

1. **[R1] K-shuf derangement FAMILY (mandatory; supersedes the single
   fixed rotation, which was insufficient — B2).** The family S is the
   EXHAUSTIVE set of composite within-lemma index-derangements of the
   per-sense domain/range constraint-set assignment (each lemma's senses
   URN-sorted; every sense receives another sense's constraint set;
   `subPropertyOf` links and classDeclarations untouched; byte bulk
   preserved). From the measured inventory (break 5, find 2, friend 2,
   make 2 senses) |S| = D(5)·D(2)³ = 44 [DERIVED; count re-verified at
   build]. Disclosed structure: make's two senses both carry empty
   constraint sets, so its swap is functionally idle, and three of break's
   five senses share `range material` — but every member of S changes
   break.interrupt's range (no other sense carries `happening`), so no
   member compiles byte-identical to K [DERIVED; asserted mechanically at
   build]. The binding gate C-SHUF (§2.3) requires K strictly above the
   family maximum on typing-active confirmatory cells — a prespecified
   quantile threshold (100th percentile) over the derangement distribution,
   with the derangement-null empirical quantile p = 1/(|S|+1) ≈ 0.0222 ≤
   0.05 reported. Extension rule, pinned now: if a future inventory makes
   |S| < 19 (empirical p floor above 0.05), the family is extended with
   pinned seeded global cross-lemma derangements to ≥ 199 members (seed
   fixed at freeze). Cost: |S|+1 arm evaluations of a CPU-trivial pipeline
   — minutes, $0. [STIPULATED — ASM-2103]
2. **Kernel-as-text: structurally N/A** (no prompt surface exists);
   recorded with reason per protocol §2; the shuffle + source-projection
   arms carry the content-vs-structure burden here. [STIPULATED]
3. **Gold circularity.** The single biggest threat. Mitigations, all
   pre-freeze-checkable: provenance-separation rule (§2.1) with the
   poisoned-gold canary; G3's constructed-rule status disclosed in every
   claim sentence; E1 upgrades (SemCor sentences, VerbNet restrictions,
   human spot-audit ~30 items ≈ 1h). Residual: G3's rule and K's
   disjointness axioms both descend from the same WN top split —
   disclosed; the sharpest cells (K wrong on attested objects) are immune,
   since they score K *against* attested third-party usage. [STIPULATED +
   ASSESSMENT]
4. **Divergence-by-construction ≠ win-by-construction.** The D-word
   projection follows the rules-2-knull comparator construction
   [MEASURED precedent]; B-wn exists so that the headline claim can never
   rest on beating a strawman; the no-net-harm clause blocks a K that wins
   divergent cells by spraying conflicts everywhere. [STIPULATED]
5. **Compiler asymmetry.** All arms share one world-compiler; only the
   source→TBox module differs, plus the sense-projection step that is the
   *definition* of each source. Compiler code is pinned; the PC-4 planted
   tests include a deliberately mistyped axiom (scorer must catch the flip)
   and the poisoned-gold canary. [STIPULATED]
6. **Tiny inventory.** 11 senses, 4 lemmas, ~10² items. Every claim is
   scoped to it; Stage-B (24 polysemous panel words → ~60–90 senses) is
   the pre-named scale-out, gated on E0. No NL robustness claim (items are
   compiled worlds, not parsed text; the l3a parse wall stands). No host,
   scale, or deployment claim of any kind. [STIPULATED — ASM-1967]
7. **[R1] Determinism leaks outcomes through cells.** Any holdout item
   whose outcome-equivalence cell was realized in a seen frame has an
   inferable outcome before it is "run" — a threat no custody rule can
   remove, because it is a property of deterministic instruments, not of
   process. Answered structurally: the binding confirmatory frame is
   novel cells only (§2.5 `H*`), and inference is at cell level (§2.2), so
   already-inferable observations can neither pad n nor masquerade as
   confirmation. Full-H numbers are co-reported, descriptively labelled.
   [STIPULATED — ASM-2104/2040]

---

## 5. The mandatory blocking instrument pilot (pre-freeze, per ASM-1830/1831)

One CPU run, ~12–20 items, $0 model spend, minutes of wall clock; artifact
`poc/engine-inf/results/instrpilot-result.json` (kot-pilot/1, mode REAL)
pinned into the DRAFT record before freeze. **[R1] The 2026-07-12 pilot
(PILOT-PASS-WITH-FLAGS, ASM-2002) predates REVISION-1's arms and checks and
does NOT satisfy this gate for the revised design: a full pilot RE-RUN with
all 7 arms + oracle, the amended checks below, and PC-6/PC-7 is mandatory
before freeze. Pilot checks execute on the exploratory frames and decoy
lemmas only — never on H (ASM-2111).** Instantiation
[STIPULATED — ASM-1963, amended by ASM-2111]:

| check | ENGINE-INF operationalisation |
|---|---|
| **PC-1 no degenerate arm** | no baseline at 0 or 1.0 on the pilot divergent cells (K at 1.0 is certificate-normal and disclosed, not a failure — the contrast headroom lives in the baselines); refusal rate bounded on every arm except where gold IS refusal |
| **PC-2′ separation non-vacuous [R1]** | `|Div(K, D-word-dom)| ≥ 6` and `|Div(K, B-wn)| ≥ 3` at pilot scale, spanning ≥ 2 closure ops and ≥ 2 lemmas, **plus the EP-A existence check: `|Div_dec(K, K-lemma-x) ∩ (G1∪G3)| ≥ 3` on the exploratory frame for at least one x ∈ {dom, union}** — if K's own collapses cannot diverge from K even exploratorily, EP-A is stillborn and the redesign stops pre-freeze at $0; the pilot divergence certificate is committed — **this is the non-vacuous-divergence existence proof, the exact anti-knull gate** |
| **PC-3′ control family non-degenerate [R1]** | the FULL derangement family compiles; |S| equals the build-derived count (44 at this inventory); every member's compiled module differs byte-wise from K's; family scores computable end-to-end on the pilot slice; the single-rotation ≥-half check is retired (its job now belongs to the binding C-SHUF gate at the registered run); D-union not row-identical to D-dom |
| **PC-4′ gate teeth [R1]** | planted mistyped axiom (range flip on one sense) ⇒ scorer + divergence certificate must fire on the predicted cells and nothing else (CF-2-style); poisoned-gold canary ⇒ all arm compilations (including K-lemma and derangement-family compilers) byte-identical under gold perturbation; a planted compiler gold-read must trip the canary; **sense-tag insensitivity canary: perturbing the item's gold sense tag leaves K-lemma and D-word compiled worlds byte-identical AND changes the K / B-wn relation URN on remapped items** |
| **PC-5 elicitable gold** | the mechanical item extractor yields well-formed items with unique gold on ≥ 95% of candidate occurrences (rest excluded with logged reasons); the oracle arm (gold verdicts injected through the pinned scorer) scores 1.0 |
| **PC-6 holdout machinery on decoys [R1]** | the SemCor pipeline (pin → sense-key mapping → extraction → gold → compile → engine → score) runs end-to-end on the three pinned decoy lemmas (draw, hold, cut — in neither Stage-A nor the kernel-v0 panel); decoy outcomes quarantined, touching no endpoint; mapping-failure and exclusion reasons logged |
| **PC-7 holdout custody [R1]** | mechanical repo scan finds no H item id in any results artifact; items-H + gold-H exist, sha-pinned, with no corresponding rows; the runner's refuse-if-H-rows-exist assertion demonstrated (plant a fake H row → runner must refuse); KILL-e1 adequacy count evaluated from items-H + gold-H alone and reported |

Additional pre-freeze mechanical checks: double-run determinism sha;
WN-frames field availability for B-wn verified in the pinned extraction
(if absent, extractor extension is a build task, not a design change);
provenance grep for G2-independence (§2.1). PILOT-FAIL blocks the freeze,
per protocol; the kernel-as-text N/A makes the best verdict
PILOT-PASS-WITH-FLAGS, printed by the freeze tool.

---

## 6. Staging, cost, risks, go/no-go

### 6.1 Stages [STIPULATED — ASM-1966; costs are planning bands, not commitments]

| stage | content | cost | gate |
|---|---|---|---|
| **E0 — decisive first increment [R1-amended]** | `axioms-engineinf-v0` module (built, pinned); mechanical item extractor over WN31 gloss examples (built; 212 items measured, now EXPLORATORY-ONLY); **[R1] + K-lemma-dom/-union collapse compiler; + exhaustive derangement family (44 members); + SemCor pin (pulled forward from E1) and holdout extractor → items-H/gold-H pinned without outcomes; + cell-level cluster-bootstrap analysis; 7 arms + oracle + family; H divergence certificates; re-run blocking pilot (PC-1..PC-7); freeze; registered run scores H; verdict-gen** | **$0 model spend, CPU-only (2-core box fine, engine closes 958 worlds in <2 s [MEASURED certificate]); +1–2 agent-days over the original 2–4 band [STIPULATED — ASM-2112]** | re-run pilot PASS → KILL-e1 adequacy holds → freeze → run |
| **E1 — instrument upgrades [R1-amended]** | VerbNet selectional-restriction pin (network fetch + sha-pin; fallback: stay on WN-only gold, disclosed); ~30-item human spot-audit of G3; grade-W items with the **R-DISAMB** engine extension (typed sense-elimination as a closure rule — engine version change: closed-inventory addition, twin+sparq-reason conformance rerun, CF-gate mini-certificate before any use). (SemCor sentence pin moved into E0 by REVISION-1 — the confirmatory holdout needs it.) | $0 model spend + ~1h human; 2–3 agent-days | E0 verdict lands; R-DISAMB conformance 100% |
| **E2 — Stage-B scale-out** | the 24 polysemous g2-panel words (~60–90 senses per the sense-split design), full re-run; the census frame stops being 4 lemmas | 1–2 agent-weeks authoring (dominated by explication authoring, shared with sense-split Stage B — the marginal ENGINE-INF cost is the axiom module + items) | E0 PASS-affirm or maintainer direction after deflate |
| **E3 — named follow-on, NOT this record** | divergent inventory ⇒ ASM-1851 re-activation: a rules-2-shaped train-time campaign where kernel vs dictionary corpora genuinely differ | ~$7–18 GPU (rules-2 anchors) | its own record, own pilot, maintainer authorization |

### 6.2 Honest risks [ASSESSMENT unless tagged]

1. **G3 constructed-rule gold is the weakest plank.** A skeptic can say
   the anomaly labels encode the same intuition the kernel encodes.
   Answer: disclosed in every claim; the E1 upgrades exist; and the
   deflationary direction (K wrong on *attested* items) is immune. If the
   maintainer wants the affirmative claim stronger before freeze, swap
   G3-primary to VerbNet at E0 (adds the pin to the E0 critical path).
2. **B-wn may be under-informative** (frames are only Somebody/Something)
   ⇒ K beats it trivially on fine cells. Then the honest headline shrinks
   toward "kernel typing beats the best *mechanical* WN typing" — still
   the pre-registered question, but the D3(b)-relevant competitor becomes
   "a better non-kernel source" (e.g. VerbNet-typed senses), which E1 can
   add as arm B-vn. Pre-registered now as the named extension so a K win
   over B-wn is not oversold. [STIPULATED]
3. **Explication→axiom promotion is an authoring act** — a bad promotion
   is a K defect by construction and will be measured as one (that is the
   experiment working); the shuffle plus per-axiom clause citations keep
   it auditable.
4. **The engine's class machinery is thin** (no cax-sco): precomputed
   hypernym-closure facts inflate stated worlds slightly; budgets are
   generous (certificate worlds already carry UNA fact sets). Mechanical
   risk only.
5. **Ambiguity of victory.** [R1-amended] The co-primary split makes mixed
   outcomes first-class: PASS-A with FAIL-B (splitting helps, kernel
   authoring doesn't beat mechanical content) and FAIL-A with PASS-B (the
   content wins, the split per se doesn't) are each a pair of scoped
   sentences on the §3 ladder, never one blurred headline.
6. **Scope temptation.** The result, either way, will be quotable. Claim
   caps are pre-registered (ASM-1967): no NL, no host, no scale, no
   deployment, no thesis verdict — this is one seam, made askable for the
   first time.

### 6.3 Go/no-go read (this designer's, for the maintainer)

**GO on E0.** [STIPULATED ruling — ASM-1966; confidence 0.85 [ASSESSMENT]]
It is the cheapest experiment on the board that can produce either the
programme's first kernel-specific-value datum or the honest D3(b) reframe
trigger; it runs entirely on the programme's only never-failed channel;
it consumes the Stage-A corpus the maintainer already commissioned; it
costs $0 in model spend and days not weeks; its blocking pilot is
CPU-trivial; and its divergence certificate has a second life as the
ASM-1851 re-activation artifact. The main pre-freeze decision the
maintainer owns: whether G3 anomaly gold at E0 is WN-rule-constructed
(faster, disclosed-weaker) or waits for the VerbNet pin (slower,
stronger). This designer recommends WN-rule at E0 with VerbNet at E1 —
the deflationary readings, which are the risk-bearing ones, do not depend
on G3. **[R1] The GO recommendation survives REVISION-1 unchanged in kind —
the revised E0 is still the cheapest experiment on the board and still $0
model spend — but it is now conditional on the re-run pilot (PC-1..PC-7)
and the pre-freeze KILL-e1 holdout-adequacy count, both $0 stops. The
2026-07-12 exploratory numbers play no part in this recommendation beyond
the §R1 narrowed sentence.** **No feasibility conclusion is stated or
implied on CORRECTNESS or EFFICIENCY.**

---

## Self-check gate (governance)

Every load-bearing claim above carries MEASURED / DERIVED / STIPULATED /
EXTRAPOLATION / ASSESSMENT; design choices and decision rules are
STIPULATED, never MEASURED; both result readings of every endpoint are
pre-registered with verbatim sentences; forward claims name their
resolution path (pilot check, pre-freeze extraction count, E1 pin, Stage-B
build). The engine, encoder pin, kernel-v0/v1 bytes, and all frozen records
are untouched. Assumption blocks
`docs/next/design/asm-engineinf-1950-1969.json` (original) and
`docs/next/design/asm-engineinf-r1-2034-2049.json` (REVISION-1; owner
designer-4, tags MEASURED | STIPULATED | EXTRAPOLATION, range verified free
at emission); central registration is the coordinator's, with commit.
REVISION-1 states no feasibility conclusion: the exploratory numbers are
licensed only through the §R1 narrowed sentence, and the registered
analysis remains INCONCLUSIVE until the confirmatory holdout runs. No git
actions in this pass (design-role constraint); commit + push is the session
coordinator's handoff step.
