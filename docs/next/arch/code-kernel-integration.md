# P3-D-CKI — CKI/1: four maintainer-proposed code↔kernel integration directions (issue #16), developed as design

> **Status: [DESIGN] — maintainer-proposed architectural directions, developed
> seriously by the chief-architect role as candidates connected to the CASC/1
> cascade and the EFFICIENCY thesis. Nothing here is frozen, pre-registered,
> scheduled, or run; no verdict, audit, frozen object, or registry record is
> touched; no bead is created by this document. This document is written FOR
> the bidirectional design loop: it goes to GPT-5.6 for external critique
> next, and every assumption is stated explicitly so the critique can attack
> it.** Author: Fable, chief-architect role (`kern/fable-designer`),
> 2026-07-11.
>
> **Provenance of the proposals — the maintainer, issue #16, verbatim:**
> 1. *"See if the lexical subset can be mapped on top of concepts in the
>    kernel."*
> 2. *"See if additional concepts can be built on top of the lexical concepts
>    that would be 'higher up' or sets of nodes in an AST; e.g. for common
>    logic and functions there is a node which defines a set of syntax that
>    would be put together. That way a large amount of syntax could be
>    described as a single concept internally and then output by the decoder
>    in a normalised way."*
> 3. *"Have a 'world' or similar plug-in which is brought into the kernel
>    specifically when it is working on code."*
> 4. *"Have a model trained specifically for code generation so it can be
>    invoked just for generating the code part of a response in a 'mixture of
>    models' type framework. That way the decoder could possibly be written
>    in a way such that only valid code is output from the model."*
>
> This document is the serious development of those proposals, not a critique
> of them; the critique round is GPT-5.6's (bidirectional).
>
> **Inputs read at source, in full:**
> `docs/next/arch/cascade-naturalisation.md` (CASC/1 — H-CN, seams V-C2/V-DEC/
> V-LL, mechanisms M1–M5); `docs/next/arch/cascade-synthesis.md` (the upheld
> GPT-5.6 critique: corrected M2 register, CASC-0 withdrawn, CASC-0′
> specified, the §4 break-even inequality, renderer/fid_R seam split and
> deferred); `docs/next/interpretations/codevert-g0.md` +
> `poc/codevert-g0/RESULT.md` (the measured G0 spike); `docs/next/design/
> CODEVERT.md` rev 2 (ASM-1000 licence space; the `instance-of(symbol,
> concept)` stratum as the single future kernel seam; §2.2 completeness
> semantics); `docs/next/arch/codevert-arch-critique.md` (CASK-PY/1
> adjudication); `docs/next/interpretations/deconf-a1.md` figures as restated
> in CASC/1 §3.2 and the synthesis §1.1.
>
> **Steering-note compliance, stated up front:** round-2 steering says STOP
> further design cycles because results, not designs, are the scarce resource.
> This document is inside the named exception: MAINTAINER-directed
> architecture (issue #16) requires a developed design before it can be
> critiqued, beaded, or declined. It proposes exactly ONE cheap experiment
> (CODE-W0, §6), attaches everything else to already-specified gates
> (CASC-0′, the G0 re-scope decision), and displaces no dispatched work.
>
> **Tag convention (house discipline):** `[MEASURED: ref]` = a registry
> verdict/assessment/artifact restated strictly inside its envelope;
> `[STIPULATED: id]` = a design choice made here or inherited — every design
> CHOICE in this document is STIPULATED, never MEASURED; `[PROPOSED-ASM: id]`
> = a design choice pending coordinator registration; `[ESTIMATED]` = a
> planning number with no measurement behind it; `[DERIVED]` = an analytic
> computation from cited measured inputs, disclosed as such;
> `[EXTRAPOLATION: id]` = a registered forward projection, **never a
> premise**; `[established, memory]` = a literature-level technique claim
> from model memory, flagged for source-verification before any load-bearing
> use. New stipulations live in the fresh block **PROPOSED-ASM
> ASM-1110…ASM-1117** (registry high-water observed at authoring time
> ASM-1109, claimed by the DECONF stage-B spec; the coordinator registers
> this block append-only at commit and rebases the ids if a concurrent wave
> has claimed them — this document performs no registry edit).

---

## 0. One-paragraph summary and the ranking

The four issue-#16 directions are not four rival architectures; they are four
SEAMS of one composite, and each maps onto a component the CASC/1 cascade
already names [STIPULATED: ASM-1110]. **D3 (code world plug-in)** is the
substrate: it is the already-built CODEVERT stack (fail-closed extractor +
typed store + µs engine) productised as a mountable stratum-4 world, and it
composes ONLY measured parts — the strongest evidence position of the four.
**D1 (lexical subset → kernel concepts)** is a representation mapping of that
substrate into kernel URNs — cheap, feasibility-supported by G0's
forward/lexical clear (κ≈0.72), but its VALUE-ADDED claim is exactly the
kernel-vs-plain-dialect attribution question on which every measured contrast
so far reads ≈0. **D2 (AST-node-set macro concepts + normalising decoder)**
is the V-DEC minted-vocabulary consumption channel plus the naturaliser-out,
specialised to code — both halves unmeasured (a-e2 gives only a prefill
UPPER BOUND; the reasoning-over-macros half is M2-shaped with adverse
neighbours), and V-DEC is already registered as deferred behind a positive
M2 sign. **D4 (mixture-of-models code head with constrained decoding)** IS
the cascade decoder seam for the code vertical; its enabling technique
(grammar-constrained decoding) is established, and it has one genuine
structural advantage no NL vertical has — the outbound-fidelity seam the
CASC synthesis flagged as unmeasured-programme-wide becomes MECHANICALLY
checkable for code (parse/type/test) — but its "small specialised model"
premise inherits the adverse f2b-transfer noninferiority result and its
build cost is the highest of the four. **Ranking by evidence-supported
promise: D3 > D4 > D1 > D2** (§5; the SPEND ordering differs and is stated
there too — D3 and D1 share one ~free probe; D4's cheap half needs no
training; D2 gets a $0 census only). The single cheapest experiment is
**CODE-W0** (§6): a G2-class, oracle-inbound transfer probe of the f2b
verify-retry loop onto the G0 code substrate, ≤5 GPU-h + local CPU + $0
annotation, with a D1 dialect-attribution rider arm — it tests the
most-promising direction (D3) directly and prices D1 for free. No cheap rung
is decisive (ASM-1039 discipline inherited verbatim); CODE-W0 is a screen
with pre-registered stop-signals [STIPULATED: ASM-1110].

---

## 1. D1 — map the lexical subset onto kernel concepts

### 1.1 What it concretely is

Mint kernel concept URNs for the code-domain vocabulary that G0 measured as
covered — the entity kinds (module, class, function, name-binding) and the
forward/lexical relation families (contains, contained-in, imports-of,
callees-of, where-defined) — and re-express the CODEVERT typed store's
records as stratum-3/4 kernel records (kot-axiom/1 sidecar + world-layer
shapes), so that a code fact IS a kernel fact: same URN space, same record
grammar, same µs engine checking it, composable with non-code kernel content
in one query [STIPULATED: ASM-1111]. Two explicit NON-goals, to keep the
critique aimed at the real object: (a) this is NOT an NSM explication of
Python semantics — the coverage record (m0b 0.3542; define-lane 0/1,550
[MEASURED: programme §0 restated per CASC/1 §8]) says explication-grade
authoring of a programming language is a wall, and D1 deliberately maps only
the RELATIONAL vocabulary, not operational semantics; (b) this is NOT a new
extractor — PY-STAT/1 facts pass through unchanged; only their serialization
and identity layer moves into the kernel's namespace.

### 1.2 Fit with the kernel and the cascade

This is CODEVERT's own registered future seam made load-bearing: rev 2 keeps
`instance-of(symbol, concept)` as "the single seam where kernel concept
content could later enter", explicitly excluded from every G1–G5 licence
[STIPULATED: ASM-1000, consumed]. In CASC/1 terms, D1 upgrades the code
store from a domain-local IR-hard island dialect (kot-query-code/1) to the
KERNEL's IR-hard island class inside the IR-soft medium (CASC/1 §1.1) — the
reasoner's covered code claims become checkable in the same island grammar
as everything else. Note the honest asymmetry this creates: D1 is the ONLY
direction of the four that could ever move kernel-CONTENT attribution
(ASM-1000 walls the other three into architecture-family claims), and it is
also the direction the measured record most deflates.

### 1.3 Measured evidence

**For (feasibility):** the exact subset the maintainer names is the subset
that CLEARS on real repos — forward/lexical pooled κ ≈ 0.72, lexical
families exact at 1.0000, on the full extractor-independent census of six
real repos [MEASURED: poc/codevert-g0/RESULT.md §1 via interpretations/
codevert-g0.md §2]; the instrument (census + fail-closed extractor + probe)
validated at ~$0 with zero contradictions of 1,415 dynamically-exercised
proved facts [MEASURED: RESULT.md §3]. The engine that would check the
mapped records is measured at 5.29–7.82 µs/query [MEASURED: registry/
verdicts/l3a.json + a5.json, restated per CASC/1]. G0's inverse/exhaustive
zeros (callers-of 0/3,783; instance-of 0/503, structural, annotation-proof
[MEASURED]) bound what D1 can carry but do not touch the forward subset.

**Against (value):** every measured kernel-vs-plain contrast reads ≈0 or
adverse at its scope: DECONF-A1 certified kernel runtime structure INERT at
the pinned F2 checker seam (C_dec = 1.0, 40,576/40,576) — the value that
survives is the AUTHORED, aligned, canonical, checkable answer key, which a
plain typed dialect also provides [MEASURED: interpretations/deconf-a1.md,
restated per synthesis §1.1]; the corrected M2 register (binding on
downstream CASC documents, adopted here) records the deflationary prior on
kernel-specific attribution as "strong" [STIPULATED: synthesis §1.1]. So the
honest expected value of D1's mapping, per the record: canonicalisation and
cross-domain composability [EXTRAPOLATION: ASM-1116 — unmeasured; no
workload containing mixed code+non-code queries exists in the programme],
plus ~0 measured advantage over the native typed dialect at any existing
seam. D1's attribution question is exactly CASC's rung-2 ladder
(kernel dialect vs plain dialect) and is priced for free as CODE-W0's A5
arm (§6).

---

## 2. D2 — AST-node-set macro concepts, normalised by the decoder

### 2.1 What it concretely is

A macro tier ABOVE D1's lexical concepts [STIPULATED: ASM-1112]: each macro
concept is a named parametric AST schema — a "set of nodes in an AST", the
maintainer's words — e.g. iterate-and-accumulate, guard-clause-early-return,
context-managed-resource, dataclass-with-defaults. Each macro carries two
deterministic artifacts:

- a **detector**: AST-subgraph match → macro instance with slot bindings
  (fail-closed: no match → no macro, the code stays at the lexical tier);
- a **normalising expander**: macro + slots → ONE canonical concrete syntax
  (pinned style, deterministic, idempotent under re-detection:
  `detect(expand(m)) = m` is a checkable contract).

Internally, a large span of surface syntax is carried as a single macro
token + slots; the decoder expands it "in a normalised way" — precisely the
maintainer's sentence. The macro inventory is a finite, versioned,
content-hashed codebook (an encoder-version-class object: changing it is an
ALGORITHM_VERSION-style bump with regenerated goldens, per house convention).

### 2.2 Fit with the cascade — two seams, named separately

D2 is not one mechanism; it is BOTH deferred CASC seams at once, and the
design must keep them apart because their evidence differs
[STIPULATED: ASM-1112]:

- **Inbound (consumption): D2 = V-DEC for code.** Macro tokens in the
  reasoner's input are exactly the minted-vocabulary consumption channel
  CASC/1 names V-DEC and the synthesis keeps DEFERRED behind a positive M2
  sign (synthesis §2: "V-DEC/V-LL do not unlock" on a K1′ kill). The
  measured ceiling transfers: a-e2's prefill-savings MEMBERSHIP UPPER BOUND
  18.5–24.0% (Qwen2.5) / 33.4–41.7% (SmolLM2), consumption channel
  UNMEASURED [MEASURED: registry/assessments/a-e2-census.json, upper bound
  only]. Whether a reasoner reasons BETTER-per-cost over macro tokens is
  M2-shaped, and the corrected register applies verbatim: no direct support;
  the nearest honest-gold size test (f2b-transfer `noninferiority_vs_r3` =
  FALSE, audit pending [MEASURED: registry/verdicts/f2b-transfer.json per
  synthesis §1.1]) and the nearest text-delivery test (nsk1 0.76→0.43, 0/24
  rescues, exploratory [MEASURED]) are both adverse.
- **Outbound (rendering): D2's expander IS the naturaliser-out (R) of
  CASC/1 §2, specialised to code.** "Internal concept → normalised output"
  is the naturalisation move with the renderer replaced by a DETERMINISTIC
  expander — which is a genuine improvement over the NL renderer on exactly
  the axis the synthesis flagged: fid_R for a deterministic expander is a
  property you PROVE (round-trip idempotence + parse equivalence), not a
  rate you measure on an untuned model. γ (core/output token ratio),
  [ESTIMATED] and unmeasured in CASC/1's M3 ledger row, becomes mechanically
  measurable for code at $0: realised macro-token count / expanded-token
  count over a corpus.

### 2.3 Measured evidence

**For:** the a-e2 upper bound exists and is real money IF consumption works
[MEASURED: upper bound only]; code is the one domain where "normalised
output" is well-defined and checkable (formatters/canonicalisers are
standard practice; idempotence and parse-equivalence are mechanical)
[established, memory — verify at source before load-bearing use]; G0's
validated AST tooling means detectors are buildable on the existing
substrate at low cost.

**Against:** (a) the macro-coverage question — what fraction of real code
mass falls under any finite macro inventory — is UNMEASURED and plausibly
Zipf-shaped with a long tail (the g8/define-lane precedent: every measured
"author a codebook over an open domain" number in this programme has come
back brutal [MEASURED: g8 0/1,000; define-lane 0/1,550]); (b) the inbound
half is registry-deferred behind CASC-0′'s M2 sign and this document does
not un-defer it [STIPULATED: ASM-1112, adopting the synthesis routing];
(c) stock checkpoints have never seen macro tokens — the OOD/tuning cost is
charged by ASM-0852's symmetric-tuning rule. The cheap ungated fragment of
D2 is a **$0 macro-coverage census** (detector prototypes over the G0 repo
pool: % of AST node mass / % of functions covered by a top-K inventory,
K ∈ {10, 30, 100}), which converts (a) into a number before anything else is
spent — named here as a rider, not proposed as a bead [STIPULATED: ASM-1112].

---

## 3. D3 — a code world plug-in

### 3.1 What it concretely is

Package the already-built CODEVERT substrate — PY-STAT/1 fail-closed
extractor, typed 4-state fact store, candidate-name `unknown`s,
UNKNOWN-INCOMPLETE(partial_lower_bound, blocking_count) semantics, µs query
engine — as a mountable **stratum-4 world module** with a pinned activation
contract [STIPULATED: ASM-1113]:

- **mount(repo, content_hash)** → a per-repo world instance: extraction is
  run (or a cached, content-hash-pinned store is loaded), and the world's
  IR-hard island grammar (kot-query-code/1) becomes available to whatever
  consumes it — today the f2b-shape verify-retry checker; under H-CN, the
  cascade reasoner's engine seam (CASC/1 §2's E);
- **staleness rule**: the store is valid only for the pinned tree hash;
  any source change fail-closes to re-extraction (no silent drift);
- **unmount** → the islands vanish; queries in the code grammar return a
  typed NOT-MOUNTED error, never an unchecked guess.

Honesty first: D3 is ~90% a RE-DESCRIPTION of what CODEVERT already is —
the new design content is only the lifecycle contract (mount/staleness/
unmount, per-repo instancing, multi-world coexistence rules) and the
explicit positioning as the island-supplier for CASC's IR-soft-with-islands
medium. The risk named in advance for the critique: re-badging without a
new claim. The new CLAIM D3 does make is transfer — that the one measured
positive mechanism in the programme (M4, verify-retry against an aligned
store) transfers from its measured vertical to the code vertical's
forward-family islands. That claim is what CODE-W0 (§6) prices.

### 3.2 Fit with the kernel and the cascade

D3 is the DECONF-A1 value story instantiated: A1 left standing exactly
"authored, aligned, canonical, checkable answer key" as the kernel-side
value at a checker seam [MEASURED: deconf-a1 restated per synthesis §1.1] —
and a world plug-in is precisely an authored-by-extraction, aligned,
checkable answer key, mounted on demand. In CASC/1's architecture it is the
supplier of IR-hard islands for the code vertical (CASC/1 §3.3 already
names CODEVERT "the friendliest first vertical for a full cascade
instance"). It is also the DEPENDENCY of the other three directions: D1 maps
ITS store into kernel URNs; D2's detectors run over ITS ASTs; D4's
constraint tables (symbol existence, arities, import surface) are read from
ITS store. That dependency structure is itself a ranking argument (§5).

### 3.3 Measured evidence

**For — the strongest position of the four:** every component is measured.
Verify-retry loop: +0.1507 lift at 0.103 cost (LB +0.1053), the programme's
only audited efficiency sign, at its narrow formal/self-authored scope
[MEASURED: registry/verdicts/f2b-replicate.json]. Engine: 5.29–7.82 µs
[MEASURED]. Store economics on real repos: 6.05 MB store, 82 MB RSS,
µs-class queries — the symbolic side is ≈ free [MEASURED: codevert-g0
RESULT.md]. Coverage of the mountable islands: forward/lexical κ ≈ 0.72
[MEASURED]. Soundness stand-ins: zero contradictions of 1,415 dynamically
exercised proved facts; 0/5,718 probe completeness violations (with
disclosed vacuity) [MEASURED].

**Against / bounding:** (a) TRANSFER is unmeasured — f2b's loop was
measured on its own vertical against its own aligned store; no measurement
says the shape survives the move to code-domain tasks and the code store's
UNKNOWN-INCOMPLETE answer surface; (b) the coverage wall bounds the
routable share: κ_q^indep 0.4361 overall, inverse/exhaustive families
0.0000–0.14 structurally [MEASURED] — on 1−s of code questions the mounted
world is pure overhead, the CASC §5.1 routing-bound logic applied
per-vertical; (c) the G0 re-scope decision (forward/lexical subset vs
UNKNOWN-INCOMPLETE-as-product vs PY-STAT/2) is maintainer-gated and OPEN —
D3's island surface is whichever universe that decision picks, and nothing
here preempts it [STIPULATED: ASM-1113; ref interpretations/codevert-g0.md
§3]; (d) ASM-1000: no D3 outcome in either direction is kernel-content
evidence.

---

## 4. D4 — mixture-of-models code head with constrained decoding

### 4.1 What it concretely is

A router + a code-generation model invoked only for the code spans of a
response, whose decoder is CONSTRAINED so that emitted code is valid by
construction [STIPULATED: ASM-1114]:

- **Grammar constraint**: token masking against the target language's
  grammar — emitted text always parses. Grammar-constrained decoding is an
  established technique with known properties [established, memory —
  verify at source before load-bearing use]: it guarantees syntactic
  well-formedness; it does NOT guarantee semantic correctness; and it can
  distort the model's output distribution (locally-valid prefixes forcing
  globally-poor completions), a measured-in-the-literature quality tax that
  any prereg must carry as a named risk.
- **World constraint (the integration that makes this OURS)**: masking
  against the mounted D3 world's symbol store — only identifiers that
  exist, only imports the repo can resolve, arity-consistent calls where
  the store proves arity. This is where the maintainer's "only valid code"
  gets its honest scope [STIPULATED: ASM-1114]: the guaranteeable property
  is **parseable + reference-resolved-against-the-mounted-world**, not
  "correct". Semantic correctness stays where it always was — tests and the
  engine's checkable islands — and the design says so on every readout.
- **Mixture-of-models routing**: a span-classifier hands code spans to the
  head and prose to the main path. The router is a new error surface (a
  third boundary), charged like every boundary.

### 4.2 Fit with the cascade — this IS the decoder seam

D4 is not adjacent to CASC; it is CASC's rear seam (the naturaliser-out R)
specialised to the code vertical, with the renderer's two gate quantities
transformed [STIPULATED: ASM-1114]:

- **fid_R becomes partially MECHANICAL.** The synthesis ruled the outbound
  seam "unmeasured programme-wide" and split it into a separate deferred
  instrument because NL prose needs semantic adjudication (synthesis §1.5).
  For code, the adjudicators are machines: parse-check, reference-check
  (against the world), type-check where available, test execution. The
  code vertical is therefore the ONE place the programme can measure a
  rendering-fidelity seam without human annotation — a structural argument
  for building the rear-seam instrument HERE first, whatever the vertical
  ordering elsewhere.
- **The dangerous-render analogue is real and specific**: fluent, valid,
  normalised code that does something the structured core never asserted
  is MORE dangerous than broken code, because it passes review heuristics.
  Constrained decoding makes output look trustworthy; the anti-l3a/a5 rule
  (renderer failures count against the system) applies with extra force.

### 4.3 Measured evidence

**For:** the enabling technique is established (grammar-constrained
decoding guarantees grammaticality [established, memory]); the constraint
TABLES come from a measured substrate (D3's store, κ≈0.72 forward
families, µs lookups — mask computation is engine-speed); and the value
target is real — invalid/unresolved code is a genuine failure mode of small
models, and eliminating it is a mechanical guarantee, not a bet.

**Against:** (a) the "model trained specifically for code so a smaller
specialised head suffices" premise is the M2/f2b-transfer-shaped bet, and
the closest honest-gold measurement came back adverse (`noninferiority_vs_
r3` = FALSE, +0.2507 lift over host alone notwithstanding, audit pending
[MEASURED]); (b) TRAINING a code head is the most expensive build of the
four directions and is exactly the "renderer instrument" class the
synthesis routes BEHIND CASC-0′'s M2 sign — this document adopts that
routing for the trained-head form [STIPULATED: ASM-1114]; (c) the
constraint-induced quality tax is unmeasured on our rigs; (d) router error
is a new unmeasured boundary. The cheap UNGATED fragment of D4 — named as a
rider, not beaded — is constrained-vs-unconstrained decoding on a STOCK
small checkpoint with masks fed by the D3 world (no training, no mixture):
it prices the validity gain and the quality tax in one paired contrast, and
it only needs D3 mounted, which is another reason D3 goes first.

---

## 5. Ranking by evidence-supported promise

**D3 > D4 > D1 > D2** [STIPULATED: ASM-1115; the reasoning is the ranking's
content, so it is spelled out]:

| Rank | Direction | Promise | Evidence position | What kills it cheapest |
|---|---|---|---|---|
| 1 | **D3 world plug-in** | modest but concrete: mount-on-demand checkable islands for code; the M4 mechanism's new vertical | composes ONLY measured parts (f2b loop +0.1507@0.103; engine µs; store ≈free; forward κ≈0.72); the one unmeasured link is transfer | CODE-W0 K-W1 (§6): no lift on the code vertical |
| 2 | **D4 constrained code head** | high if the premise holds: mechanically-guaranteed valid code + the programme's only annotation-free rear-seam instrument | enabling technique established; constraint tables measured (via D3); BUT the specialised-small-model premise has an adverse honest-gold neighbour (f2b-transfer NI FALSE) and the trained form is gated behind CASC-0′ | the stock-checkpoint constrained-decoding rider showing the quality tax exceeds the validity gain |
| 3 | **D1 lexical→kernel mapping** | canonical URNs + cross-domain composition | feasibility measured (the named subset clears at κ≈0.72); VALUE deflated by every measured kernel-vs-plain contrast (DECONF-A1 inert; the corrected M2 register's "strongly deflationary prior") | CODE-W0 A5 TOST within band (§6): attribution dead at scope |
| 4 | **D2 AST macro concepts** | large if BOTH halves work (prefill compression + deterministic normalising decoder) | weakest: inbound = V-DEC, registry-deferred behind an unmeasured M2 sign with adverse neighbours; macro coverage unmeasured with a bad codebook-authoring precedent (g8, define-lane); only the a-e2 UPPER BOUND is measured | the $0 macro-coverage census returning a small top-K mass |

Two honest annotations on the ranking:

1. **Promise-rank ≠ spend-rank.** The dependency structure (§3.2) and the
   gates make the SPEND ordering: (i) CODE-W0 — tests D3, prices D1 as a
   rider, ~free; (ii) the $0 D2 macro-coverage census and the D4
   stock-checkpoint constrained-decoding rider, both on the mounted D3
   substrate, both annotation-free; (iii) NOTHING trained or built for
   D2-inbound or D4-trained-head until CASC-0′ reports the M2 sign
   (synthesis routing adopted verbatim) [STIPULATED: ASM-1115].
2. **D4's rank-2 is conditional on its scope discipline.** Ranked as
   "constrained decoding + world-fed masks + mechanical rear-seam
   instrument". If read as "train a code model now", it drops below D1:
   that form is gated, expensive, and rests on the adverse premise.

---

## 6. CODE-W0 — the single cheapest experiment (tests D3; prices D1 free)

**Honesty first, ASM-1039's rule inherited verbatim: no cheap rung is
decisive. CODE-W0 is a SCREEN with pre-registered stop-signals; it cannot
establish any matched-budget win (G4-class) or any kernel-content claim
(ASM-1000). What it CAN do is convert the one unmeasured link in the
best-evidenced direction — M4 transfer to the code vertical — into a number,
at ≈ zero marginal cost** [STIPULATED: ASM-1117].

**Class:** G2 `oracle-diagnostic`, oracle-inbound (blind NL phrasings parsed
by a pinned oracle protocol; no learned front-end exercised — the NL wall is
NLB's problem and stays there [MEASURED context: a5-nl 41.6% + S2 kill;
l3a-parse 47.6%]). Self-authored/covered riders ride verbatim. Non-scored
against any G1 floor; it does NOT preempt the maintainer's G0 re-scope
decision — it runs on the forward/lexical islands under EXPLICIT disclosure
that this presupposes re-scope option (a)'s universe without deciding it.

**Substrate:** the G0 six-repo pool + its already-built PY-STAT/1 stores
(zero new extraction), mounted per the D3 contract — CODE-W0 doubles as the
first exercise of mount/staleness semantics. Host: the R-1 135M class (the
f2b loop's measured host). Items: forward/lexical-family questions with
engine-derivable gold; circularity partially countered by cross-checking
gold against the dynamic probe's 1,415 dynamically-confirmed facts and by
held-out repos for phrasing authorship; the self-authored rider rides
regardless. n ≈ 300–500 items; power sized by the pinned analysis script at
freeze; statistics per house rules (paired hierarchical cluster bootstrap at
repo level — six clusters is an honestly wide CI and is disclosed as such).

**Arms** (paired, same items; decoding/stop/max-tokens pinned; KOT-COST/2
vector measured per arm on the pinned rig):

| Arm | System | What it prices |
|---|---|---|
| A1 | 135M host alone, NL→answer | the floor |
| A2 | host + mounted world, f2b-shape verify-retry (k pinned) on IR-hard islands | **D3's transfer claim (M4 on code)** |
| A3 | A2 with seed-pinned deranged store | house control; expected collapse |
| A4 | host + world serialized as prepended TEXT (no loop, no engine) | seam-class control — the nsk1-analogue delivery; separates "checked seam" from "kernel text in context" |
| A5 | A2 with the store serialized in the D1 kernel-URN dialect vs A2's native typed dialect, content/token-matched | **D1's attribution rider** — kernel-vs-plain at this seam, TOST at a pinned margin, deflationary prior disclosed in advance |

**Endpoints:** primary — paired LCB95(acc(A2) − acc(A1)) > 0, with the full
cost vector co-reported (no cost-headline claim; the §4-inequality
publication rule from the cascade synthesis applies). Secondaries —
Δ(A2−A4) (the seam-class contrast); A3 collapse check; A5 TOST (within band
→ D1 attribution dead at scope, feeding the knull-v2/issue-#12 channel
exactly as CASC K3′ does); realised routable share s on the item universe
(feeds the per-vertical G1 routing bound).

**Pre-registered stop-signals** [STIPULATED: ASM-1117]:

- **K-W1 (transfer kill):** primary LCB95 ≤ 0 → M4 does not transfer to the
  code vertical at this scope → D3 demoted from "most promising" to
  re-badging; D4's world-fed constraint story loses its measured substrate
  argument; the four-direction ranking is re-issued.
- **K-W2 (seam-class kill):** A2 ≈ A4 within a pinned band → the effect (if
  any) is context-text, not the checked seam — the nsk1-adverse reading
  extends to code and the plug-in's engine seam adds nothing.
- **K-W3 (attribution kill, non-fatal):** A5 within TOST band → D1's
  kernel-dialect value dead at this seam and scope; D1 survives only as a
  namespace-hygiene choice, and the kernel-content question routes entirely
  to knull-v2/A-F0.

**Cost [ESTIMATED]:** ≤5 GPU-h free pool (135M inference only) + local-CPU
engine legs under standing nice/checkpoint discipline; $0 annotation
(engine-derivable gold; phrasing authorship is parents'-scale authoring
spend); ≤$10 API-class incidentals. The two $0 riders (D2 macro-coverage
census; D4 stock-checkpoint constrained-decoding contrast) can share the
mounted substrate in the same session but are severable and carry their own
disclosures.

---

## 7. Honest risks and what nothing here licenses

1. **ASM-1000 walls the licence space.** No outcome of D2/D3/D4 in any
   direction is evidence about kernel CONTENT; D1 is the single seam where
   content attribution could enter, and its prior is measured-deflationary.
   Neither programme thesis moves on anything in this document.
2. **The composite could blur gates (the CASC §7.8 dilution risk, inherited
   verbatim).** Each direction keeps its own gate: D3's transfer claim at
   CODE-W0; D1's attribution at A5/knull-v2; D2-inbound and D4-trained
   behind CASC-0′'s M2 sign; the G0 re-scope stays maintainer-gated. No
   direction grants another a licence [STIPULATED: ASM-1115].
3. **Coverage bounds everything.** The routable share on real code work is
   κ-class (0.4361 overall; forward-only universe smaller still), and the
   inverse zeros are structural. A plug-in, a mapping, a macro tier, and a
   constrained head all inherit 1−s dead weight; per-vertical G1 routing
   bounds must be computed from the census numbers, not asserted.
4. **"Only valid code" must never be uttered unscoped.** The guaranteeable
   property is parseable + reference-resolved-against-the-mounted-world;
   claiming more re-imports the S2-style wrong-with-provenance hazard on
   the output side, in its most reviewer-fooling form.
5. **Circularity is the standing threat to CODE-W0.** Items derived from
   the same store the loop consults flatter A2; the dynamic-probe
   cross-check and held-out repos counter it partially; the rider rides on
   every readout, and a CODE-W0 "pass" is a screen result, not a family
   verdict.
6. **How a false win would most likely be manufactured:** covered-only item
   universe presented as "code QA" (rider + s co-reported); an A4 arm
   starved by context-window truncation making the seam contrast trivial
   (token-matched serialization pinned); A5 dialects unmatched on tokens
   (content/token matching pinned); oracle-inbound flattery (disclosed; G3
   composition stays behind G-NLB) [STIPULATED: ASM-1117].

---

## 8. Epistemic register

- **MEASURED (restated strictly in-envelope):** codevert-g0 — κ_q^indep
  0.4361 [0.3610, 0.5364]; forward/lexical pooled κ≈0.72, lexical 1.0000;
  callers-of 0/3,783 and instance-of 0/503 structural zeros; store 6.05 MB,
  82 MB RSS, µs queries; 1,415 dynamically-confirmed facts, zero
  contradictions; 0/5,718 probe violations (disclosed vacuity).
  f2b-replicate +0.1507 at 0.103 (LB +0.1053), does_not_license scope.
  f2b-transfer +0.2507 external-gold lift with noninferiority_vs_r3 FALSE,
  audit PENDING. DECONF-A1 C_dec = 1.0 (40,576/40,576), runtime structure
  inert at the pinned checker seam. nsk1 0.76→0.43, 0/24 rescues
  (exploratory). a-e2 prefill membership UPPER BOUND 18.5–24.0% / 33.4–41.7%,
  consumption UNMEASURED. Engine 5.29–7.82 µs. NL wall: a5-nl 41.6% + S2
  kill; l3a-parse 47.6%. Coverage walls: m0b 0.3542; g8 0/1,000; define-lane
  0/1,550.
- **[established, memory], flagged for source verification before any
  load-bearing use:** grammar-constrained decoding guarantees syntactic
  well-formedness, not semantic correctness, with a known
  distribution-distortion quality tax; code formatters/canonicalisers as
  standard, checkable practice.
- **STIPULATED / PROPOSED-ASM (this document's design choices; coordinator
  registers append-only at commit, rebasing if the block is taken):**
  ASM-1110 (four-directions-as-seams framing; ranking discipline; ASM-1039
  no-cheap-decisive rule inherited); ASM-1111 (D1 = relational-vocabulary
  mapping only, non-goals pinned); ASM-1112 (D2 split into V-DEC-inbound
  [deferred behind CASC-0′] and deterministic-expander-outbound; macro
  codebook is a versioned content-hashed object; $0 coverage census rider);
  ASM-1113 (D3 world lifecycle contract: mount/content-hash/staleness/
  unmount; no preemption of the G0 re-scope decision); ASM-1114 (D4 scope
  discipline: guarantee = parseable + reference-resolved; trained-head form
  gated behind CASC-0′; stock-checkpoint rider ungated); ASM-1115 (the
  D3>D4>D1>D2 ranking + promise-rank vs spend-rank separation + no
  cross-direction licences); ASM-1116 registered as EXTRAPOLATION (below);
  ASM-1117 (CODE-W0 arms/endpoints/stop-signals/threat entries). Inherited
  in force: ASM-1000, ASM-0852, ASM-0814, ASM-1039's honesty rule, the
  synthesis's corrected-M2-register wording and CASC-0′ routing.
- **EXTRAPOLATION (registered, never premises):** ASM-1116 — cross-domain
  composition value of D1's kernel mapping (mixed code+non-code queries);
  resolver: a workload census that does not yet exist, then A5-class
  contrasts. The M2 extrapolation stays ASM-1078 with resolver CASC-0′ —
  this document adds no new resolver and no new confidence.
- **ESTIMATED (planning only):** all §6 costs; macro-inventory sizes (K
  values); the "~90% re-description" characterisation of D3.
- **DERIVED:** none new — this document deliberately reuses the synthesis's
  corrected cost algebra rather than re-deriving worked points.

**Self-check gate (performed before hand-off):** every design choice is
tagged STIPULATED or PROPOSED-ASM, never MEASURED; every forward bet is
EXTRAPOLATION or ESTIMATED and none is used as a premise; every MEASURED
figure names its artifact and stays inside its envelope (upper bounds called
upper bounds, exploratory called exploratory, pending-audit called pending);
memory-sourced literature claims are flagged for verification; no registry,
verdict, or frozen object is edited; the PROPOSED-ASM block is disjoint from
the observed high-water mark (ASM-1109) and its registration is delegated to
the coordinator at commit.

This document changes no frozen object, no verdict, no audit, no registry
entry; it proposes one bead-able experiment (CODE-W0), names two $0
severable riders, and defers D2-inbound and D4-trained behind the
already-specified CASC-0′ gate. Next step per the standing loop: GPT-5.6
external critique (bidirectional), then coordinator synthesis, then the
maintainer's routing on issue #16.
