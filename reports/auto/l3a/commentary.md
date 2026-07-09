Runner note (runner-2, 2026-07-09, non-binding): `claims-check` on the pinned
prereg doc reports 3 `ERR_ASM_UNTAGGED_PREMISE` findings for the PREMISE items
in section 0. The epistemic tags ARE present in the document content
([MEASURED]/[LIT-BACKED], with refs) but sit on the markdown continuation line
below the `PREMISE:` marker, and the lint is line-granular. The doc is pinned
in the frozen record (sha 002afa81), so it is deliberately NOT edited
post-freeze; the formatting-only fix belongs to any successor record's prereg
doc. Process lesson recorded: run `claims-check` on the prereg doc BEFORE
`prereg-freeze`. Also for the auditor (per ASM-0006): the audit should
independently re-derive a sample of l3a-eval expected answers from
data/world-v0 records; abstain-all's control_refused_correct_code=0 is by
design (its blanket ABSTAIN code never matches the expected ERR_* code under
the strict-code scoring rule).
