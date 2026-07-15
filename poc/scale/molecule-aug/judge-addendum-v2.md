# S5 judge addendum v2 — single-candidate, expanded-rendering fidelity instrument

> DESIGN ARTEFACT (DESIGN-v2.md §3). Composed at judge time onto the UNMODIFIED base
> `poc/scale/ast-pipeline/judge_prompt.md` to form `s5-judge-fidelity.md` — the
> PRIMARY instrument for the S5-v2 campaign. Applied identically to ALL candidates
> (both arms). Verdicts under this instrument are not comparable to verdicts under
> the base pooled prompt or the v1 conditional (gloss-credit) prompt.

## Protocol changes for this run

1. **Exactly ONE candidate per request.** You will receive one concept header and a
   single candidate labelled `=== CANDIDATE A ===`. Judge it against the concept on
   its own merits. Your `verdicts` array contains exactly one entry, for "A". You
   will never see other candidates for this concept; do not try to infer or compare.

2. **Candidates are fully expanded.** Every candidate has been mechanically rewritten
   so that it contains ONLY profile-1 prime material. Where an explication composed
   in another already-defined concept, that concept's own explication has been
   inlined in place as a nested block:

   ```
   {"kind": "subExplication", "frame": …, "referents": […], "clauses": […]}
   ```

   Read a `subExplication` block as a self-contained sub-definition whose full
   meaning applies at that position (its `referents` indices are local to the
   block). Judge the meaning the nested material ACTUALLY renders in primes — you
   are never asked to take any gloss or label on credit; none are shown.

3. **Do not penalize (or reward) size, nesting, or style of composition as such.**
   Some candidates are large or deeply nested because of inlining; others are flat.
   Both are legitimate. The question is unchanged: does the total rendered material
   carry THIS sense's genus and criterial differentia (FAITHFUL), or is criterial
   meaning dropped or wrong meaning asserted (LOSSY)? Nested material that adds
   nothing criterial is bloat exactly like any other idle clause; nested material
   that asserts wrong meaning for this sense makes the candidate LOSSY exactly like
   a wrong prime clause.

4. **No provenance, no comparison, no memory.** Requests are independent; judge each
   in isolation. Provenance is unknowable and irrelevant.

The verdict inventory (FAITHFUL/LOSSY), `missing`, the quality 0–3 scale, and the
STRICT-JSON output format are unchanged from the base prompt (with a single "A"
entry).
