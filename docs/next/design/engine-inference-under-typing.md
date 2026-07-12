# Engine Inference Under Typing (ENGINE-INF) — DESIGN

**Role: Fable DESIGN agent (designer-4), 2026-07-12. This is a DESIGN for the
maintainer to freeze — not a prereg, not an execution, and it issues no
feasibility conclusion on CORRECTNESS or EFFICIENCY. Nothing here modifies
the encoder pin, kernel-v0/kernel-v1, the RULES-1 certificate, any frozen
record, or any registered verdict. Maintainer acceptance: issue #26 items
D2+D3.** Assumption block:
`docs/next/design/asm-engineinf-1950-1969.json` (owner designer-4; range
1950–1969 verified free at emission — max registered id in
`registry/assumptions.jsonl` is ASM-1939; repo-wide grep for
`ASM-19[5-6][0-9]` empty).

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

### 1.3 The arms [STIPULATED — ASM-1955, ASM-1956]

All arms share: the same engine bytes, the same shared world-compiler, the
same scorer, the same item bank. They differ ONLY in the source module
compiled into the TBox (and, where the source lacks sense vocabulary, in
the source-side projection of sense relations — constructed exactly as the
rules-2-knull leg constructed its dictionary comparator).

| arm | source | sense-split? | typing | what it embodies |
|---|---|---|---|---|
| **K** | kernel-v1 Stage-A + `axioms-engineinf-v0` | yes (11 senses) | per-sense, explication-derived | the kernel |
| **D-word-dom** | plain dictionary | no — one relation per lemma | the SemCor-dominant sense's signature (tag_cnt from pinned `index.sense`) | the strongest committed word-level dictionary (the pi:011 shape) |
| **D-word-union** | plain dictionary | no | union / least-common-subsumer signature (effectively untyped) | the cautious word-level dictionary |
| **B-wn** | WordNet 3.1 bytes only, zero kernel authoring | yes (same sense URNs) | mechanical: WN verb sentence-frames (Somebody/Something slots) | **the kernel-specificity decider**: sense-structure without kernel authoring |
| **K-shuf** | K with per-sense domain/range assignments deranged across senses within lemma | yes | shuffled | mandatory shuffled-kernel control (typing content destroyed, byte bulk identical) |

The mandatory **kernel-as-text control is structurally N/A**: there is no
LLM/host consumer anywhere in the instrument — no prompt for the text to
enter. Recorded as an explicit `not_applicable` with structural reason per
the blocking-pilot protocol (downgrades the pilot verdict to
PASS-WITH-FLAGS, never a silent pass). [STIPULATED — ASM-1963]

**Why B-wn is load-bearing** [STIPULATED — ASM-1956]: beating only the
D-word arms licenses "sense-split typing beats word-level typing" —
real, but a claim about sense structure, which WordNet also has. The
kernel-SPECIFIC claim requires beating the best matched source constructible
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
tag (WN synset by attachment; SemCor sentence tags at E1). The K and B-wn
compilers map gold synset → their sense relation URN mechanically via the
pinned `wn31Synsets` field (or → NONE for `excludedSenses`, in which case
the arm's fail-closed behaviour is itself scored). The D-word compilers
**cannot** consume the tag — a dictionary has no sense vocabulary — and
collapse every occurrence to the lemma relation. This is the same
projection logic the rules-2-knull leg used and is the definition of the
matched comparison, not a handicap. [STIPULATED]

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

### 2.2 Scoring [STIPULATED — ASM-1959, ASM-1962]

Per item per arm, the engine emits a verdict in
`{CONSISTENT, ANOMALOUS(ERR_CONFLICT), REFUSE(code), typed-answer}` plus
derived class facts. Exact match against gold verdict; O1 cells
additionally exact-match the derived class against G2. Deterministic
engine ⇒ no seeds; double-run byte-identity required (certificate
discipline).

Two scores, pre-registered:
- **Primary: raw exact-match correctness** on the divergent set (below).
- **Secondary: honesty-weighted score** per the issue-#18 direction —
  wrong assertion costs 1, refusal costs 0.5, correct costs 0 (penalty
  form fixed at freeze). Reported for every arm; D-word-dom's confident
  wrongness vs K's fail-closed refusals is exactly what this separates.

### 2.3 The divergence certificate and the primary endpoint

**Divergence certificate (the ASM-1851 leg-1 analog, run before any
scoring):** for each baseline b, `Div(K,b)` = the set of items whose
engine verdict-or-derived-fact set differs between K and b — computed
mechanically, committed as a pinned artifact with per-op and per-lemma
composition. This artifact is the non-vacuousness proof the knull lineage
taught the programme to demand *before* interpreting any contrast.
[STIPULATED]

**Primary endpoint (kernel-specificity):** on `Div(K, B-wn)` — paired
exact contrast, K correctness − B-wn correctness. Deterministic outcomes
⇒ per-item 0/1; inference is over the item frame (all WN31 gloss-example
occurrences of the Stage-A lemmas — a finite, census-like frame; report
census numbers AND exact-binomial LB95 for the pre-registered
generalization to Stage-B lemmas, tagged EXTRAPOLATION).

Decision rule, verbatim [STIPULATED — ASM-1959/1960/1961]:

- **KILL-e1 (vacuity):** `|Div(K, D-word-dom)| < 25` at the operating
  point, or divergent cells span < 3 closure ops or < 3 lemmas ⇒ the
  instrument cannot ask; no verdict either direction. (Checked at pilot
  scale by PC-2 before freeze; the campaign-scale recheck is the
  registered kill.)
- **KILL-e2 (convergence-deflation):** `Div(K, B-wn)` empty or < 10 ⇒ the
  kernel-vs-mechanical-sense-typing question is unaskable at this
  inventory ⇒ recorded as a D3(b) input ("sense structure suffices;
  kernel authoring adds no divergent closure here"), no affirmative
  claim.
- **PASS-affirm (kernel-specific value, first datum):**
  K divergent-set correctness Wilson-LB95 ≥ 0.80, AND
  K − B-wn ≥ +0.20 on `Div(K, B-wn)` with exact-binomial LB95 > 0, AND
  K − b > 0 on `Div(K,b)` for BOTH D-word arms, AND K's correctness on
  the CONVERGENT set is not worse than any baseline's by > 0.02 (no
  net-harm clause).
- **FAIL-deflate (the D3(b) trigger):** B-wn matches or beats K on
  `Div(K, B-wn)` (point estimate ≤ 0), OR K's divergent-set correctness <
  D-word-dom's. Reading, pre-registered verbatim: *"where the kernel's
  closure diverges from matched non-kernel closures, it is not more
  correct; the kernel's distinctive contribution remains unlocated; the
  programme thesis reframes per D3(b) — grounded content + certified
  engine, not kernel-specific structure."* This is an honest, valuable
  outcome, not a failure of the instrument.
- Anything between the PASS and FAIL bands ⇒ INCONCLUSIVE at scope,
  named residual, no reframe and no affirmative claim.

Both readings are written into the record before any byte is scored. The
secondary endpoints (word-level contrast K vs D-word arms; honesty-weighted
deltas; per-op breakdown) are descriptive and capped: beating only D-word
arms licenses "sense-split typing beats word-level typing at this scope" —
never "kernel-specific value."

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

---

## 3. Kernel-specificity as the PRIMARY endpoint — what each outcome means

[STIPULATED — ASM-1961, load-bearing]

| outcome | licensed sentence (scoped) | programme consequence |
|---|---|---|
| PASS-affirm | "On this inventory, where kernel-v1's sense-split typing derives engine closures that matched non-kernel sources do not, the kernel's closures are the correct ones by third-party-derived gold." | **First kernel-specific-value datum** in programme history; the four-seam content-not-structure ledger gains its first structure-side entry; re-opens the attribution chain the knull byte-identity closed |
| KILL-e2 / FAIL-deflate | "Sense-structure (or nothing) suffices; kernel authoring adds no divergent-and-correct closure at this scope." | The honest **D3(b) reframe trigger**: the thesis candidate becomes grounded-content + certified-engine, with the kernel as one authoring pathway among several — a pre-registered maintainer decision input, not a designer's choice |
| KILL-e1 | instrument cannot ask at this inventory | extend inventory (Stage-B senses) or accept the question as closed-deflationary at kernel scale |
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

1. **K-shuf (mandatory shuffled kernel).** Derange per-sense domain/range
   assignments within lemma; byte bulk identical. Prediction: predicted
   wrong verdicts on divergent cells (false conflicts on attested items,
   missed anomalies). If K-shuf ≈ K, the typing content is inert and the
   design is dead — PC-3 checks this at pilot. [STIPULATED]
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

---

## 5. The mandatory blocking instrument pilot (pre-freeze, per ASM-1830/1831)

One CPU run, ~12–20 items, $0 model spend, minutes of wall clock; artifact
`poc/engine-inf/results/instrpilot-result.json` (kot-pilot/1, mode REAL)
pinned into the DRAFT record before freeze. Instantiation
[STIPULATED — ASM-1963]:

| check | ENGINE-INF operationalisation |
|---|---|
| **PC-1 no degenerate arm** | no baseline at 0 or 1.0 on the pilot divergent cells (K at 1.0 is certificate-normal and disclosed, not a failure — the contrast headroom lives in the baselines); refusal rate bounded on every arm except where gold IS refusal |
| **PC-2 separation non-vacuous** | `|Div(K, D-word-dom)| ≥ 6` and `|Div(K, B-wn)| ≥ 3` at pilot scale, spanning ≥ 2 closure ops and ≥ 2 lemmas; the pilot divergence certificate is committed — **this is the non-vacuous-divergence existence proof, the exact anti-knull gate** |
| **PC-3 controls non-degenerate** | K-shuf differs from K on ≥ half the pilot divergent cells with the predicted error signature; D-union not row-identical to D-dom; margins reported against replicate noise (deterministic ⇒ noise 0; margins are exact) |
| **PC-4 gate teeth** | planted mistyped axiom (range flip on one sense) ⇒ scorer + divergence certificate must fire on the predicted cells and nothing else (CF-2-style); poisoned-gold canary ⇒ all arm compilations byte-identical under gold perturbation; a planted compiler gold-read must trip the canary |
| **PC-5 elicitable gold** | the mechanical item extractor yields well-formed items with unique gold on ≥ 95% of candidate occurrences (rest excluded with logged reasons); the oracle arm (gold verdicts injected through the pinned scorer) scores 1.0 |

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
| **E0 — decisive first increment** | `axioms-engineinf-v0` module (~11 senses × 2–3 axioms + bridge classes, explicator role); mechanical item extractor over WN31 gloss examples (4 lemmas; est. 60–120 items: attested + cross-pair anomaly + excluded-sense refusal cells [EXTRAPOLATION — ASM-1964, resolved by the extractor's first run]); 5 arms + oracle; divergence certificate; blocking pilot; freeze; run; verdict-gen | **$0 model spend, CPU-only (2-core box fine, engine closes 958 worlds in <2 s [MEASURED certificate]); 2–4 agent-days** | pilot PASS → freeze → run |
| **E1 — instrument upgrades** | real SemCor sentence pin + VerbNet selectional-restriction pin (network fetch + sha-pin; fallback: stay on WN-only gold, disclosed); ~30-item human spot-audit of G3; grade-W items with the **R-DISAMB** engine extension (typed sense-elimination as a closure rule — engine version change: closed-inventory addition, twin+sparq-reason conformance rerun, CF-gate mini-certificate before any use) | $0 model spend + ~1h human; 2–3 agent-days | E0 verdict lands; R-DISAMB conformance 100% |
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
5. **Ambiguity of victory.** If K wins Div(K, D-word) but KILL-e2 fires on
   B-wn, the result is simultaneously affirmative-for-sense-structure and
   deflationary-for-kernel-authoring. The two-tier claim ladder (§2.3
   secondary caps) exists precisely so this lands as two scoped sentences,
   not one blurred one.
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
on G3. **No feasibility conclusion is stated or implied on CORRECTNESS or
EFFICIENCY.**

---

## Self-check gate (governance)

Every load-bearing claim above carries MEASURED / DERIVED / STIPULATED /
EXTRAPOLATION / ASSESSMENT; design choices and decision rules are
STIPULATED, never MEASURED; both result readings are pre-registered with
verbatim sentences; forward claims name their resolution path (pilot check,
E1 pin, Stage-B build). The engine, encoder pin, kernel-v0/v1 bytes, and
all frozen records are untouched. Assumption block
`docs/next/design/asm-engineinf-1950-1969.json` (owner designer-4, tags
MEASURED | STIPULATED | EXTRAPOLATION, range verified free at emission);
central registration is the coordinator's, with commit. No git actions in
this pass (design-role constraint); commit + push is the session
coordinator's handoff step.
