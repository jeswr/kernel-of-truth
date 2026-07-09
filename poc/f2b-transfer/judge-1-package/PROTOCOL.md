# f2b-transfer adjudication protocol (§4) — VERBATIM, FROZEN

> Verbatim copy of section 4 of `poc/f2b-transfer/design.md`
> (frozen prereg_doc, sha256 c4942eaf6c9914eb1392956a77c3ab24d1890678e869ea7cbe3f4e7b5db96c79).
> This copy is authoritative for judge-1's task; the wrapper lines above
> this rule are not part of §4.

---

## 4. Adjudication protocol (FROZEN with this note — the record pins this file's sha)

1. **Judges.** Two blind judges + a tie-break adjudicator, all recorded as
   pseudonyms (judge-1, judge-2, judge-3; RT-14 — no names/emails anywhere in
   hashed bytes). judge-1 MUST be a human who has never read any
   kernel-v0/molecules-v0 record. judge-2: a second such human if available;
   **pre-declared fallback** (E5 leak-checked-judge discipline): the
   cross-vendor Codex/GPT-5.5 model via the `codex` CLI, temperature 0,
   pinned prompt stored in d-adj-t, shown ONLY the item text below (a
   different vendor from both the host models and the designer — the §8
   auditor-identity rationale). judge-3 (tie-break only): may be the
   maintainer, blind-shuffled, disagreement items only. The judge sourcing
   actually used is recorded in d-adj-t and disclosed in every readout.
2. **Blinding.** Each judge sees, per item, ONLY: the question text and (for
   MCQ) the option texts, in the model's own rendering — never urn,
   record_path, membership gold, type labels, provenance, or which option is
   the kernel's own gloss. Item order is shuffled per judge with a pinned
   permutation seed (`dadjt/1|judge-<n>|20260710`).
3. **Escape hatch (mandatory).** MCQ items offer "NONE of these / cannot
   say"; claim items offer yes / no / cannot-say. Forced choice would
   fabricate agreement under H-CIRC; the escape makes "the kernel's content
   does not describe this concept" expressible. A concordant escape verdict
   makes the item CONTENT-UNDECIDED: it counts as **non-agreement** in the
   endorsement statistic A and is excluded from the Stage-2 eval set — it is
   evidence against endorsement, never an instrument event.
4. **Resolution.** gold_ext(item) = the concordant judge-1/judge-2 label
   (including concordant escape ⇒ undecided). Discordant pairs go to judge-3
   blind; judge-3's label resolves. Still-unresolvable items (judge-3
   escapes where the pair split label-vs-label) are UNRESOLVED — instrument
   events, capped by gate G-adj below.
5. **Order and immutability.** Adjudication completes and `d-adj-t` is
   hash-pinned (ops amendment) BEFORE the Stage-1 record is appended and
   before any GPU cell runs. Labels are never revisited after the pin; the
   Stage-2 runner fail-closes on the pin (ERR_PIN).
6. **Effort** [STIPULATED estimate]: 360 items × ~20 s ≈ 2 h per judge;
   tie-breaks ~15 min; LLM-judge fallback ≈ $1–3 API spend. Within O-3
   patterns (D-IR-N blind adjudication precedent).
