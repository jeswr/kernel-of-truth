# f2b-transfer — Opus-runner execution log (STAGE-1 adjudication PREP)

- run-ts (UTC): 20260709T171156Z
- runner_agent_id: kern/opus-runner-3
- role: experiment-runner (Opus execution) — EXECUTE a Fable-frozen design; never design, never conclude
- experiment: f2b-transfer (registry/experiments/f2b-transfer.json, status **FROZEN**)
- bounded task: stage-1 adjudication PREP — (1) assemble the blind judge-1 HUMAN
  package; (2) run judge-2 (GPT-5.5) per §4; STOP before endorsement A / the
  stage-1 verdict (those need judge-1's returned HUMAN labels + the tie-break).
- outcome: **judge-1 package assembled + committed. judge-2 BOUNDARY-STOPPED
  (Fable-needed — see §"judge-2").** No endorsement A, no d-adj-t assembly, no
  stage-1 verdict, no GPU, no codex spend. Nothing concluded about the numbers.

## Pin verification (fail-closed — all PASS before any artifact was written)

- prereg_doc `poc/f2b-transfer/design.md`
  sha256 = `c4942eaf6c9914eb1392956a77c3ab24d1890678e869ea7cbe3f4e7b5db96c79`
  == record `prereg_doc.sha256` → **MATCH** (the §4 read here is exactly the frozen one).
- registry frozen-drift: `python3 tools/registry/registry-check.py --frozen-drift`
  → `ok frozen-drift: f2b-transfer (f00fd28f)`; overall `registry-check: PASS`.
- corpus d-qa-t: `python3 tools/registry/corpus-pin.py d-qa-t`
  = `7179ee6791bd0af643c410872925ff594945c29b563192f6d7c4a872397cee27`
  == record `pins.corpus_hashes["d-qa-t"]` → **MATCH**.
- input items: `data/d-qa-t/items/covered.jsonl`, 360 items (216 MCQ keys A–D +
  144 claim yes/no); types def-match 108 / term-match 108 / claim-true 56 /
  claim-false 88 (matches the frozen build).

## 1. judge-1 HUMAN package — ASSEMBLED (§11.3, task step 1)

Builder (reproducible, stdlib-only, deterministic — no wall-clock / urandom / hash()):
`poc/f2b-transfer/opus-runs/20260709T171156Z/build-judge1-package.py`.
Command: `python3 poc/f2b-transfer/opus-runs/20260709T171156Z/build-judge1-package.py`.

Rendering follows the FROZEN §4 verbatim:
- **Blind (§4.2):** each item keeps ONLY its `question` text and (MCQ) the
  option `{key,text}` pairs. Every provenance/membership field is dropped:
  `id, label, urn, record_path, record_sha256, gloss_doc_id, type, answer,
  claim, claim_source, source, slice, kernel_checkable, rank`.
- **Mandatory escape (§4.3):** MCQ items offer `A/B/C/D/NONE` ("NONE of these /
  cannot say"); claim items offer `yes / no / cannot say`.
- **Pinned order (§4.2):** judge-1's items are presented in judge-1's pinned-seed
  order, seed `dadjt/1|judge-1|20260710`.
  - DETERMINISM NOTE (flagged, science-neutral): §4.2 pins the permutation SEED
    but not the permutation ALGORITHM. This run uses the repo's CANONICAL
    seeded-sort idiom — identical to `data/d-qa-t/build-dqat.py`'s pinned rank
    order (sort by `sha256(seed | item_id)`). Presentation order does NOT enter
    the frozen endorsement statistic A or the judge-pair-agreement gate (both are
    computed per item id; `analysis/f2b_transfer.py` reads only the
    order-independent summary record). The full position→id map is written to
    provenance (below), so labels re-key regardless of the permutation. If Fable
    pins a different construction, re-ordering is trivial and changes no science.

Human-facing package — `poc/f2b-transfer/judge-1-package/` (BLIND; no ids, no
provenance; pseudonym "judge-1" only, RT-14 clean — zero names/emails/`@`):
- `README.md`               sha256 `55fd5cf75a49e27e12e6327a1f3269c5631afd03415a9d383add3b77d0ac50ce`
- `PROTOCOL.md`             sha256 `dae135175f8371246af38e0af64d63e19eda70a78144b81a08e23a02473235be`
  (verbatim copy of design.md §4; body byte-identical to the design.md §4 slice —
  verified; a 5-line wrapper header notes the source sha and is marked not-part-of-§4)
- `items-judge-1.md`        sha256 `872f2bafe7c03f0300178cb38c95aedead8da24ca1bd116d4f21c0025ff8de49`
  (360 numbered blind items in judge-1 order; per item: question + options + escape + blank answer)
- `items-judge-1.jsonl`     sha256 `57070307f85a0137157143c2b3706ebb2b88e2cfd00706f8f4946c773487add5`
  (machine-readable blind mirror; keys = [allowed, format, options, position, question] — no id/answer/type/label)
- `response-template.csv`   sha256 `d09d30bb60d7696f41b1891cafeb890d25cae1ad3e0406ddc48600c770ec44a8`
  (360 rows: position,answer,optional_note)

Provenance (NOT in the human package — contains ids; opus-run dir):
- `judge-1-position-map.jsonl` sha256 `c9adccff8dece3191e5297f00946163dc3d54bb59bc576f9c82dca0b7ee6e068`
  (position → dqat id + frozen rank; the PRIVATE re-keying map for judge-1's returned labels)
- `blind-items-by-id.jsonl`    sha256 `ce820483336e6e25c607fa72e2591022f192d9e0eddc9a6689e02b4796af42cc`
  (order-neutral canonical blind rendering keyed by id — helper for a later judge-2 assembly)

VERIFIED: byte-identical on re-run (deterministic); item files carry ZERO
provenance tokens; PROTOCOL.md §4 body == design.md §4 slice; 360 positions in
items md == 360 template rows == 360 map rows == 360 blind-by-id rows.

WHAT THE HUMAN MUST DO: a kernel-naive person (never read any kernel-v0 /
molecules-v0 record) reads `README.md` + `PROTOCOL.md`, answers all 360 items in
`items-judge-1.md` from their own everyday understanding (MCQ → A/B/C/D/NONE;
yes/no → yes/no/cannot-say; the escape is a valid expected answer), and records
answers by position in `response-template.csv`. No name/email anywhere. ~2 h.
The returned CSV is re-keyed to item ids via `judge-1-position-map.jsonl`.
NO judge-1 responses were fabricated by this run.

## 2. judge-2 (GPT-5.5) — BOUNDARY STOP (task step 2 guard fired; Fable-needed)

Per the task guard ("If the §4 LLM-judge mechanism is not fully determined by the
frozen protocol (e.g. the exact prompt or the codex invocation shape is
unspecified), STOP and report it as Fable-needed rather than inventing it"), Opus
did NOT run judge-2 and spent $0 on codex.

Determined / not the blocker: judge-2's pinned shuffle seed is `dadjt/1|judge-2|20260710`
(§4.2); the codex CLI is present on the box (`codex-cli 0.142.5`); the blind
item rendering is done (order-neutral copy committed, above).

NOT determined by the frozen protocol (the blocker):
1. The judge-2 **pinned prompt**. §4.1 says judge-2 = "the cross-vendor
   Codex/GPT-5.5 model via the codex CLI, temperature 0, pinned prompt stored in
   d-adj-t, shown ONLY the item text". But `data/d-adj-t/` does not exist and NO
   verbatim prompt text exists in the frozen record, design.md, or the repo
   (searched). The operative wording is load-bearing (task framing; how the model
   expresses the §4.3 cannot-say/NONE escape; the parseable output contract) and
   must faithfully encode the SAME §4 protocol the judge-1 human package presents,
   so both judges adjudicate one instrument (needed for endorsement A and the raw
   two-judge agreement gate). Authoring it is FABLE design work (Fable/Opus
   boundary: instruction/context prompts for a judging agent are Fable's).
2. The **codex invocation shape**: per-item vs batched; exact stdin/prompt
   structure; temperature-0 enforcement/verification; the machine-parseable
   answer contract and refusal mapping; RT-14-clean recording by pseudonym judge-2.

Queued: bead `kernel-of-truth-67m` (P1, FABLE-NEEDED). Once frozen, Opus runs
judge-2 from `blind-items-by-id.jsonl` under judge-2's shuffle.

## 3. Boundary — STOP (as instructed)

NOT done (all gated on judge-1's returned HUMAN labels + judge-2 + tie-break):
d-adj-t assembly/pin; endorsement A / `external_endorsement_lb`; the stage-1
adjudication-instrument final-phase record; `verdict-gen`; the stage-1 verdict.
No GPU touched. No API keys touched. No `git push`. No FROZEN record edited.
No interpretation of any number.

## Artifacts written by this run

- `poc/f2b-transfer/opus-runs/20260709T171156Z/build-judge1-package.py` (builder)
- `poc/f2b-transfer/opus-runs/20260709T171156Z/run-log.md` (this log)
- `poc/f2b-transfer/opus-runs/20260709T171156Z/judge-1-position-map.jsonl` (private re-keying map)
- `poc/f2b-transfer/opus-runs/20260709T171156Z/blind-items-by-id.jsonl` (order-neutral blind rendering)
- `poc/f2b-transfer/judge-1-package/{README.md,PROTOCOL.md,items-judge-1.md,items-judge-1.jsonl,response-template.csv}`
- bead `kernel-of-truth-67m` (judge-2 prompt + invocation shape — FABLE-NEEDED)
