# plain-spotcheck-current.json — CURRENT blind style spot-check for the knull plain arm

**File:** `poc/knull/inputs-v3/plain-spotcheck-current.json`
(sha256 `4bfe40d9ccc7ca06ea981da8496363ea4a7554bbab0fbe6aa588265940dee31a`, 10 items,
schema `kot-knull-spotcheck/1`).
**Purpose:** the maintainer blind style spot-check that gates
**kernel-of-truth-d0hq** (knull pre-freeze gates G-1..G-5) and hence the knull
GPU run **kernel-of-truth-1np7**. Prepared 2026-07-13 by the Fable designer
role (designer-15): **sampling + formatting only — no definition was authored
or edited**; every item is byte-identical to its entry in the accepted store.

> NOTE ON LOCATION: this file lives under `inputs-v3/` because that path was
> pre-specified by the tasking, but it samples the **v4** store — the
> accepted, current one (see next section). Do not read the directory name as
> a claim that v3 is current.

## 1. Which definition set is CURRENT, and why

**Current store: `poc/knull/inputs-v4/plain-authored.json` v4.0.0
(sha256 `97609abe17f87e10a384950a5d69d4e579e40935109573eaf782095bcb43c0d2`).**

Lineage (each step maintainer-visible):

1. **Maintainer decision issue 6** (ASM-0703 fork, closed 2026-07-11): ruled
   **"Option B, tighter, attribution-preserving"** — concise natural-length
   definitions (L-3 word band dropped, L-4 relaxed), with the token deficit
   handled in the analysis rather than by padding the prose. This obsoleted
   the v1 (`inputs/`) and v2 Option-A (`inputs-v2/`) stores. Design record:
   `docs/next/design/knull-optionb-analysis.md`.
2. **v3 store** (`inputs-v3/plain-authored.json` v3.0.0) implemented Option B;
   its blind two-family gate **failed** on one family (GPT-5.6 8/10 PASS,
   Haiku 4/10 FAIL on set-level template monotony) —
   `docs/next/analysis/knull-v3-quality-gate.md`.
3. **Maintainer issue 17** offered (A) frame-variation retry vs (B) re-rule
   the instrument; the retry (A) was run and produced the **v4 store**
   (`inputs-v4/plain-authored.json` v4.0.0), whose gate also failed, with the
   failure mode inverted (too-mannered rather than too-uniform) —
   `docs/next/analysis/knull-v4-quality-gate.md`.
4. **The deciding ruling** (issue 17 closing exchange): Fable recommended
   accepting a reasonable control store with its residual defects documented;
   the maintainer replied *"I am happy with your call here"*, and the thread
   closed with: **"proceeding with (B): the v4 control store is accepted with
   its residual naturalness-gate defects documented."**
5. Corroboration that v4 is the store used downstream: **ASM-1401**
   (2026-07-12) pins later definition provenance "byte-verbatim from the
   knull v4 plain-authored store (sha 97609abe…)".

So: v1 and v2 are superseded by the issue-6 Option-B ruling; v3 is superseded
by the issue-17 retry-and-accept sequence; **v4 is the accepted, current
plain-dict definition set**, and it is what this spot-check samples.

## 2. Did a current spot-check already exist? No.

Checked before building this one:

- `poc/knull/inputs/plain-spotcheck.json` — 2026-07-10, samples the ORIGINAL
  (pre-Option-B, 3/10-rated) store. STALE.
- `poc/knull/inputs-v2/plain-spotcheck.json` — samples the v2 Option-A store,
  superseded by the issue-6 ruling. STALE.
- `poc/knull/inputs-v3/` and `poc/knull/inputs-v4/` — contained **no**
  spot-check file before this one.

## 3. Sampling rule (deterministic, seeded, no wall-clock)

Byte-identical rule to the frozen builders' spot-check step
(`build_inputs.py` / `build_inputs_v2.py`):
`pick_k("plain-spotcheck", 108, 10)` under the pinned generator seed
`GEN_SEED = "knull/1|knull-content-injection-ablation|20260710"`, drawing
indices `sha256(GEN_SEED|"plain-spotcheck"|i) mod 108` over the 108 covered
labels in `load_covered()` order (sorted `data/kernel-v0/concepts/` then
sorted `data/molecules-v0/molecules/`). Nothing varies by wall-clock. By
construction this selects the **same 10 concepts** as the stale F-KN-A files
(hug, dead, visible, woman, dog, bookmark, father, make, wrong, begin), which
also gives the maintainer direct old-vs-new comparability. The definition
texts are copied byte-verbatim from the v4 store (verified programmatically
at generation).

## 4. How this differs from the stale F-KN-A version (Jul-10)

- **Store sampled:** v4 accepted store (concise, frame-varied Option-B
  register) instead of the original pre-Option-B store whose blind read
  measured 3/10 with named hard defects (semicolon-chain template, staged
  observers, consequence narration).
- **Instructions:** now cite the programme's scholarly-definition standard
  verbatim criteria (first-rate English scholar, proper conventions, most-apt
  word, no unnecessary information) alongside the original two questions, and
  name the d0hq gate this read feeds.
- **Provenance block added:** source-store sha, sampling rule, acceptance
  lineage, supersession list — so the artifact is self-describing.
- Same schema (`kot-knull-spotcheck/1`), same 10 concepts, same
  item/answer_key shape.

## 5. Maintainer action required (the d0hq gate)

1. Open `poc/knull/inputs-v3/plain-spotcheck-current.json` and read the 10
   `items` **without looking at `answer_key`**.
2. For each, record: (a) does it read as ordinary dictionary-register English
   to your scholarly standard (proper conventions, most-apt word, nothing
   unnecessary)? (b) is it a fair definition a general dictionary could
   print?
3. Unblind against `answer_key`, and post the verdicts (e.g. on the d0hq bead
   or a repo issue).
4. This — together with the RT-15 freeze-timestamp post — is the maintainer
   action `kernel-of-truth-d0hq` is blocked on; d0hq then unblocks the GPU
   run `kernel-of-truth-1np7`. (d0hq's description still references the stale
   path `poc/knull/inputs/plain-spotcheck.json`; the current artifact is THIS
   file.)

## 6. Style sign-off status of the current definitions

The v4 store carries the **issue-17 acceptance** ("accepted with its residual
naturalness-gate defects documented") — a maintainer ruling on the ASM-0703
two-family JUDGE gate (which v4 failed: GPT-5.6 4/10, Haiku 3/10;
`docs/next/analysis/knull-v4-quality-gate.md`). That acceptance is **not** the
same thing as the design's F-KN-A **maintainer blind style spot-check**
(design doc §2.3: "a maintainer sign-off step, not a designer step"), which
has only ever been performed against the stale Jul-10 file, if at all. The
maintainer's own blind read of the CURRENT store is therefore **still
outstanding** — this artifact exists to make it possible.

No new ASM is registered by this artifact (no registry writes this session);
the epistemics rest on the existing ASM-0703/ASM-0706 entries, the issue-6
and issue-17 maintainer rulings, and the v3/v4 gate readout docs cited above.
