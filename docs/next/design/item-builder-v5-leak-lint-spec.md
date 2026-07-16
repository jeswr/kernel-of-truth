# item-builder v5 — leak-lint SPEC (codes V5-L1..V5-L9, fail-closed)

> **Status: [EXP-DESIGN] companion to
> `docs/next/design/item-builder-v5-contract.md` (epic
> kernel-of-truth-0f0y.2). Author: Fable (kern/fable-designer), 2026-07-16.
> This file is the IMPLEMENTABLE lint contract for
> `data/d-qa-t-plainv5/build.py` — enforced IN-PROCESS during the build,
> fail-closed: any violation aborts with the named `IV5_ERR_*` code and
> nothing is written. Design only; no builder exists yet.
> [STIPULATED: ASM-2444; reference-set choice ASM-2449]**
>
> The gsx0 lint analogues (LC1-s/LC2/LC3-s/LC4/LC5/LC7/G-LC8p in
> `data/d-qa-t-plain/build.py`) are NOT ported — each rule below is
> re-derived for multi-segment natural glosses; lineage is annotated so the
> re-derivation is auditable.

## 1. Shared definitions

Inherited byte-for-byte from `docs/next/design/plain-v5-register-lint-spec.md`
§1: `segments()` (split `[.;]`, strip, ≥15 chars, no double quote, dedup),
`toks()` (`[a-z]+` lowercase), `norm()`, token-set Jaccard, word-boundary
matching (`\b<word>\b`, case-insensitive), the NSM-legal surface vocabulary,
RT-14. Additional here:

- `qhash(question, options)` — UNSALTED sha256 over
  `question + "||" + "|".join(option texts)`, the build-dqat.py/gsx0
  construction, so hashes are comparable across every reference corpus.
- **headword(label)** — first whitespace token of the label (the PV5-2
  convention).
- **content token** — a token outside the NSM-legal surface vocabulary.
- **target** — the item's own concept; **donor** — the claim-false
  `claim_source` concept; **E-CT / E-CF** — the claim-eligibility
  predicates of contract §4.1 / §5 (E-CF's full definition lives in the
  contract; V5-L3 below is its lint restatement).

## 2. Per-item checks

**V5-L1 — the LC1 family (headword/label leaks), re-derived.** Natural
vocabulary makes label-token collisions a live channel that NSM-rendered
kernel surfaces almost never had; the family therefore grows from one check
(gsx0 LC1-s) to four:

- **V5-L1a (term-match, answer side; lineage LC1/LC1-s).** Neither the
  target's full label nor its headword occurs (word-boundary) in the shown
  definition. Guaranteed upstream by PV5-2; re-asserted at the rendered
  item surface. Abort `IV5_ERR_LEAK` (never substitute-to-def-match: the
  skeleton type is frozen; an upstream PV5-2 pass makes failure here a
  build bug, not an authoring event).
- **V5-L1b (term-match, distractor side; NEW).** No distractor label's
  headword occurs (word-boundary) in the shown definition. Enforced as an
  ADMISSIBILITY rule (inadmissible distractor labels are redrawn, seeded,
  disclosed, pairing-marked — contract §6.2), then re-asserted on the final
  surface; a final-surface hit aborts `IV5_ERR_LEAK`.
- **V5-L1c (def-match; NEW).** The target's label/headword occurs
  (word-boundary) in NO option text. Answer option: guaranteed by PV5-2,
  asserted. Distractor options: admissibility rule D-DM with seeded
  disclosed redraw (contract §6.1), then final-surface assertion.
- **V5-L1d (claim-false; NEW — "LC1-f").** The target's label/headword
  occurs (word-boundary) in NO claim-false claim text. Part of E-CF
  admissibility; re-asserted on the final surface. (Claim-true claims
  cannot contain the own headword: PV5-2 on the own definition; asserted.)

**V5-L2 — answer text not in question (lineage LC2).** For def-match: the
answer option's text does not occur (case-insensitive substring) in the
question. Abort `IV5_ERR_LEAK`.

**V5-L3 — claim-false admissibility (lineage LC3-s, re-derived as E-CF).**
Every built claim-false claim satisfies ALL of:

1. it is an admissible segment of the pinned donor record's definition
   (verbatim);
2. `norm(claim)` is not a substring of `norm(target's plain-v5 definition)`;
3. Jaccard(`toks(claim)`, `toks(target's plain-v5 definition)`) < 0.5;
4. Jaccard(`toks(claim)`, `toks(target's canonical gloss)`) < 0.5
   (NEW dual bound);
5. ≥ 1 **foreign-witness** token: a content token of the claim absent from
   BOTH `toks(target's plain-v5 definition)` AND `toks(target's canonical
   gloss)` (NEW);
6. V5-L1d;
7. specificity tier recorded (tier-1: ≥ 2 content tokens; tier-2 fallback:
   ≥ 1 = the PV5-7 floor), same tier system as claim-true.

Rejected-candidate and donor-redraw counts are disclosed in
`leak-check.json`. Exhaustion aborts `IV5_ERR_INJ`.

**V5-L4 — options distinct, answer present exactly once (lineage LC4).**
Option texts pairwise distinct (bytes); exactly one option equals the pinned
answer text; the answer key letter carried byte-identically from the
skeleton. Additionally (NEW, discriminability floor): every def-match
distractor definition has Jaccard < 0.5 vs the target's plain-v5 definition
(D-DM). Abort `IV5_ERR_INJ`.

**V5-L6 — claim-true verbatim from record (lineage LC6).** Every claim-true
claim is a verbatim admissible segment of the target's pinned plain-v5
store record (byte-substring after the store record's own normalization),
and its `claim_tier` is recorded. Abort `IV5_ERR_INJ`.

## 3. Set-level checks

**V5-L5 — uniqueness (lineage LC5, extended).**

- item ids unique, all inside the `dqatp5:` namespace, no collision with
  `dqa:`/`dqar:`/`dqat:`/`dqatp:`/`dqato:` namespaces;
- prompt surfaces (`qhash`) unique within the corpus;
- store-text distinctness (NEW): the 108 plain-v5 definitions are pairwise
  distinct after `norm` (PV5-5 re-run), distinct from every canonical gloss
  (PV5-5), AND distinct from every knull-v2 store text (plain-authored
  concise, plain-padded, opaque — the `poc/knull/inputs-v4` tree, byte-
  pinned as in the gsx0 builder). The last clause closes a gap PV5-5 does
  not cover: PV5-5 checks canonical glosses only, but LC8p comparability
  arguments assume no cross-STORE text identity either. Abort
  `IV5_ERR_LEAK`.

**V5-L7 — polarity and balance (lineage LC7, re-derived).**

- **V5-L7a** yes/no census: neither answer > 0.75 of yes+no items
  (inherited bound; with zero flips the census is the kernel skeleton's
  56/88, no-share 0.611 — still asserted on BUILT counts, never assumed).
- **V5-L7b** option-position balance: no letter A–D holds > ½ of
  multiple-choice answers (inherited; carried keys make this the skeleton's
  own distribution — still asserted).
- **V5-L7c (NEW — the pairing invariant):** ZERO polarity substitutions:
  for every claim skeleton, built `type` and `answer` equal the skeleton's
  `type` and `answer`; for every option skeleton, built `answer` key equals
  the skeleton's. One failing item aborts `IV5_ERR_PAIR`.
- **V5-L7d (NEW — length polarity cue):** median word count of yes-claims
  divided by median word count of no-claims lies in [2/3, 3/2]. Rationale:
  with claims drawn from two different segment populations (own vs donor),
  length is the crudest surface statistic a judge or host could exploit as
  a polarity cue; the band is deliberately loose (natural clause-length
  variance) and fail-closed (a breach means the admissibility filters
  skewed the populations — a design event, not noise). Abort
  `IV5_ERR_LEAK`.
- **V5-L7e (NEW — disclosure, non-blocking):** `leak-check.json` publishes,
  per polarity: full claim word-count distributions (min/quartiles/max),
  claim first-token distribution, segment-tier counts, and donor-redraw
  counts — the numeric surface on which any residual polarity cue must
  show up for pre-freeze inspection.

**V5-L8p — cross-corpus prompt-surface disjointness (lineage G-LC8p,
re-derived reference set [STIPULATED: ASM-2449]).** No item's `qhash` may
collide with:

1. **the five hard-pinned QA reference corpora** (load-bearing, byte-pinned
   by kot-corpus-hash/1, abort on pin drift `IV5_ERR_REFPIN`):
   d-qa (650, covered+control), d-qa-r (1000), d-qa-t (360),
   d-qa-t-plain (360), d-qa-t-opaque (360) — the last two are NEW in the
   reference set relative to gsx0 (which predated them);
2. **the inventory sweep** (NEW): every `data/*/items/*.jsonl` file present
   at build time whose rows expose `question` (+ optional `options`) is
   enumerated, hashed into the reference set, and LISTED with per-file
   sha256 in `leak-check.json` — so current and future item corpora
   (including the stage-3 input corpora living under `data/`) are covered
   mechanically rather than by curation, and the realized inventory is
   auditable;
3. earlier items of this corpus (intra-corpus), and any sibling arm corpus
   built in the same pass (cross-arm).

Documented exclusion: non-item artifact trees (probe caches, expert
atlases, carrier manifests, adjudication transcripts) carry no QA prompt
surfaces in the item schema and are excluded; any future experiment that
renders plain-v5 SURFACES into a new prompt family must extend this
reference set BEFORE building (consumer obligation, contract §8). Working
set discipline: initialized with all reference hashes; every built item's
hash inserted before the next draw (freshness doubles as per-concept
segment disjointness, contract §4.1). Any collision aborts `IV5_ERR_LEAK`.

**V5-L9 — hygiene.** No unrendered markup (`{urn:`, `[m]`) in any question
or option; ASCII-only surfaces; RT-14 account-string pattern list clean over
every emitted file. Abort `IV5_ERR_MARKUP` / `IV5_ERR_LEAK`.

## 4. Ordering and reporting

Pin checks (`IV5_ERR_REFPIN`) → source loads + PV5/S store lint re-run →
mapping (V5-1) → per-item rendering with admissibility (E-CT/E-CF/D-DM)
enforced at draw time → final-surface re-assertion of every V5-L1..L6 →
set-level V5-L5/L7/L8p/L9 → skeleton-identity and pairing-map assertions
(V5-L7c) → write. Rendering-time admissibility PLUS final-surface
re-assertion is deliberate redundancy: the assertions catch builder bugs
the admissibility path would mask. `leak-check.json` carries, per code:
pass status, counts, disclosure lists (redraws, tiers, rejected candidates,
inventory), and the thresholds used. The thresholds (0.5, 0.75, [2/3, 3/2],
15 chars, tier floors, 5% screen bound) are part of the pinned contract:
changing ANY of them is a builder-contract version change — new corpus,
fresh pre-committed seed, full re-run of lints, screens, and the consumer's
pre-freeze audit. No silent threshold edits, ever.

## 5. What is deliberately NOT a lint

- **Semantic truth/falsity and single-correctness** — measured by the
  non-steering screens (contract §7) and the consumer's stage-1 per-family
  endorsement gate (contract §11 O-3); a mechanical rule cannot decide
  them, and pretending otherwise would be a fake guarantee.
- **Item difficulty** — builder statistics are descriptive only (contract
  §11); no lint encodes a difficulty target.
- **Token-band parity (G-TOK analogue)** — the store's PV5-3 word band
  bounds definition length, but exact host-tokenizer parity of the RENDERED
  surfaces vs the kernel arm is an experiment-level gate: the consumer runs
  a pinned gtok-style check on the actual corpora at its pinned tokenizer
  before freeze (the gsx0 precedent), because the tokenizer is a property
  of the consumer's host, not of this corpus.
