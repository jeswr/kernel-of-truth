# knull v4 plain store — blind STYLE spot-check RESULT (maintainer §2.3 sign-off)

Human maintainer verdicts on the 10-definition blind style spot-check
(`poc/knull/inputs-v3/plain-spotcheck-current.json`, samples the accepted **v4** plain store,
sha256 `97609abe…`). Source: the maintainer's completed workbook
(`kernel-of-truth-human-review-2026-07-13.xlsx`, Google Drive id `1KS_5h3jZbPumHnR6w3aBFwUSV0Oa_FuJ`,
the fill of the issue #32 gist workbook). Recorded 2026-07-13 by the coordinator.

## Verdict: SIGN-OFF GRANTED — 10/10 appropriate

Every one of the 10 definitions was judged **(a) yes** (ordinary dictionary-register English, to the
scholarly-definition standard) **and (b) yes** (a fair definition a general dictionary could print):

| id | concept (unblinded) | (a) style | (b) fair | note |
|---|---|---|---|---|
| 0 | hug | yes | yes | |
| 1 | dead | yes | yes | |
| 2 | visible | yes | yes | |
| 3 | woman | yes | yes | |
| 4 | dog | yes | yes | |
| 5 | bookmark | yes | yes | **"uncertain whether this might be defining *archive* rather than bookmark"** |
| 6 | father | yes | yes | |
| 7 | make | yes | yes | |
| 8 | wrong | yes | yes | |
| 9 | begin | yes | yes | |

This is the design-§2.3 **maintainer blind style sign-off** — the human gate on the knull plain-dictionary
CONTROL arm (distinct from the #17 ASM-0703 *judge*-gate acceptance, which was proxy-graded). The control
arm's definitional quality is now **human-confirmed**, strengthening the knull experiment's validity.

## The one flagged observation (non-blocking)
Item 5 (bookmark): *"a record kept of a web page's address so that the page can be found again at will."*
The maintainer still marked it yes/yes but noted possible ambiguity with **archive**. It passes the
sign-off. Carry-forward caveat: if the knull matched-FLOP control-arm result turns out sensitive to item 5,
revisit this definition for tighter bookmark-vs-archive disambiguation; otherwise it stands.

## Unblock
This satisfies the **maintainer** portion of pre-freeze gate `kernel-of-truth-d0hq`. Remaining d0hq steps
are coordinator-mechanical (G-1..G-5: FLOPs re-check, pinned SAP, checklists, `prereg-freeze.py`, and the
RT-15 external timestamp). On d0hq completion → knull prereg-freeze → the GPU run `kernel-of-truth-1np7`
(matched-FLOP retry topology, GPU-authorized) is launchable on Modal.
