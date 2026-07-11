<!-- verbatim copy of poc/f2b-transfer/design.md §4 (adjudication protocol); d-adj-t §3.2 requirement. -->

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
7. **Adjudication standards (pre-data clarification; correction 1).** Added
   by `registry/corrections/f2b-transfer/1-prefreeze-correction.json` BEFORE
   any adjudication datum existed (judge-1 not started, judge-2 not run);
   items 1–6 above and the blind item bytes are unchanged. These standards
   define "correctly gives the meaning" (MCQ) and "true of X" (claims) for
   both judges under ONE protocol. Each is the principled reading of
   ordinary-understanding endorsement, chosen so the escape fires exactly
   when the kernel's content does not describe the concept (§2) — never to
   tune A; the A-direction of every rule is disclosed at the end
   [STIPULATED design rulings].
   - **S1 — MCQ correctness = fit + identification.** An option correctly
     gives the meaning iff (a) **fit**: everything it says fits the concept
     as ordinarily understood, each clause read as a typical-case (generic)
     characterization that honors its own hedges ("at some times", "can",
     "many", "some"); AND (b) **identification**: taken as a whole it says
     what the word means — the definitional core is present and picks out
     this concept rather than a different one. A clause TRUE of the concept
     but not needed to define it NEVER disqualifies (surplus truth is not
     error: the kernel's NSM explication style carries prototypical
     non-essential clauses by design, so rejecting them would measure
     lexicographic minimality — a style question §2 scopes OUT — not
     content). A clause FALSE of the concept under the typical-case reading
     ALWAYS disqualifies. Degrees: minor or even dominant surplus with the
     core present → still correct; a pile of true facts that never says what
     the thing is → fails (b) → not correct; any misfitting clause → not
     correct.
   - **S2 — best fit before NONE.** If more than one option passes S1, the
     judge picks the one that best and most specifically gives the meaning
     of the asked word itself, not of a related word (the event of dying is
     not the meaning of "dead"). NONE iff no option passes S1 or the judge
     cannot decide; both readings are one token (§4.3), optionally
     distinguished in the comment field.
   - **S3 — term-match mirror.** The judge picks the word an ordinary
     speaker could be defining with the stem text (the S1 test in reverse;
     extra true clauses in the stem do not break fit). A parenthetical
     attached to a headword or option word ("find (X finds Y)", "right (of a
     doable something)", "kind (gufo:Kind, sortal type)") only disambiguates
     which sense/use of the word is meant; unfamiliar notation inside it is
     ignored beyond sense-picking and is never itself a ground for NONE. If
     the stem fits none of the four words → NONE; if it loosely fits two →
     the better fit.
   - **S4 — claims are judged at the generic standard, about what X means.**
     "According to the definition of X, is S true of X?" asks whether S is
     part of, or directly follows from, what X means as ordinarily
     understood — including X's typical-case picture. **yes**: S holds in
     the normal case / of normal instances ("birds fly"-style; exceptions do
     not make it false), or S's own hedge holds. **no**: S misdescribes X
     (not true even as a typical-case characterization; true only rarely or
     accidentally), OR S has nothing to do with what X means — a statement
     that X's definition neither says nor implies is answered no, including
     statements so generic they say nothing about X in particular. **cannot
     say**: inability only — S cannot be understood well enough to judge
     even charitably, or the judge genuinely cannot decide; never merely
     because S is oddly worded, partial, or only typically true, and never
     as a soft no.
   - **S5 — fragments, deixis, participants.** Claim statements are
     fragments extracted from a longer description: unresolved "this
     someone / this something / these parts / it", stray quote marks
     (quoted-thought fragments), and bracketed clarifiers ("[the bookmark]")
     are read charitably as pieces of a description of X's normal scenario;
     the judged question is whether the fragment could belong to describing
     X. X/Y letters name the participants given with the word's own title
     ("break (X breaks Y)": X breaks, Y gets broken); a statement whose X/Y
     match nothing in what the asked word means is not true of it → no.
   - **S6 — register immunity (reading key).** The deliberately simplified
     register is never a ground for NONE / no / cannot-say: "something of
     kind K" reads as "a K" ("a something of kind event" = "an event";
     "somethings of kind take happen" = "acts of taking happen"). Odd
     grammar is simplification, not error and not a trick. The key is
     constant across all items, options, and claim polarities, so it carries
     zero bits about any answer (§2 style-constancy argument unchanged).
   - **S7 — item independence.** Identical statements recur under different
     words; each item is judged only against its own word, never by pattern,
     recall, or reuse of an earlier answer.
   - **A-direction disclosure [STIPULATED, honest].** Relative to the terse
     pre-clarification judge wording ("close but not quite right → NONE"),
     S1, S4 and S6 RAISE A by removing minimality- and style-driven escapes
     that would fire under BOTH hypotheses (pure noise: under H-CIRC the
     clauses are false/misfitting and S1(a)/S4-no still force the escape or
     the disagreeing label, so no H-CIRC signal is lost). S4's
     irrelevance→no clause raises agreement on donor claims under H-TRANSFER
     AND lowers A under H-CIRC (arbitrary own-record content reads as
     no-against-membership-yes) — sharpening kill (d) in both directions.
     Two honest costs are accepted rather than patched: (i) contentless
     own-record segments lose credit (no / cannot-say against
     membership-yes); (ii) donor segments that genuinely belong to the
     target's meaning (e.g. rabbit ← tree "a living thing of one kind") must
     be answered yes and count as disagreement — an item-construction cost
     of membership gold, disclosed here, not an adjudicator error, expected
     order ~1% of items. No rule conditions on provenance or membership;
     every rule is applicable by a kernel-blind judge from ordinary
     understanding alone.
