#!/usr/bin/env python3
"""One-shot register repair, 2026-07-12 (central-custody session).

1. Normalizes the malformed tail rows (PROPOSED-ASM-1360..1379, register lines
   458-477) to schema: id ASM-NNNN, owner coordinator-1, per-tag backing
   (rationale for STIPULATED; sha-pinned refs for MEASURED). Source of truth:
   poc/ontology-import-g2/proposed-asm.json (the emitted block; the register
   append dropped its rationale fields).
2. Appends the emitted-but-unregistered blocks, deduped against the ledger:
   ASM-1240..1245  docs/next/feasibility-synthesis-v4.md appendix (verbatim JSON)
   ASM-1260..1279  docs/next/design/ontology-import-plan.md Appendix A (verbatim JSON)
   ASM-1320..1329  docs/next/analysis/f2b-errors.md §9 (prose block, rows authored here)
   ASM-1330..1339  docs/next/design/honesty-first-scoring.md §6 (table, rows authored here)
   ASM-1340..1343  docs/next/interpretations/nlb-0a.md PROPOSED-ASM block (prose)
Validates every touched row with claims-check's check_entry before writing.
"""
import json, os, re, sys

ROOT = "/home/ec2-user/css/kernel/kernel-of-truth"
REG = os.path.join(ROOT, "registry", "assumptions.jsonl")
DATE = "2026-07-12"

sys.path.insert(0, os.path.join(ROOT, "tools", "registry"))
cc = __import__("importlib.util", fromlist=["spec_from_file_location"])
import importlib.util
spec = importlib.util.spec_from_file_location("claims_check", os.path.join(ROOT, "tools/registry/claims-check.py"))
claims_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(claims_check)


class F:  # findings collector for check_entry
    def __init__(self):
        self.items = []
    def err(self, code, msg):
        self.items.append((code, msg))
    def ok(self, msg):
        pass


# ---------------- tail rows 1360..1379 ----------------
TAIL_RATIONALES = {
    "ASM-1362": "Freezes the unit and denominator so abstention or output sparsity can never shrink the primary score's denominator.",
    "ASM-1363": "Pins the go/no-go resolution rule as a maintainer-ratified engineering point-estimate gate and blocks any statistical-superiority over-read.",
    "ASM-1364": "Fixes the arm ladder and monotone-rendering rule so the comparison isolates the added soft-typing sources.",
    "ASM-1365": "Reuses the audited blind cross-family proxy protocol with fresh labels/seeds so proxy labels stay comparable to the frozen baseline instrument.",
    "ASM-1366": "Makes blinding a hard abort condition on every call surface rather than a best-effort convention.",
    "ASM-1367": "Pre-declares instrument-validity gates so an instrument failure can never be read as an experimental outcome.",
    "ASM-1368": "Defines the deranged-sort probe so soft-hedge false satisfaction is measured, not assumed.",
    "ASM-1369": "Mechanises vacuity so uninformative slots cannot count toward soundness.",
    "ASM-1371": "Machine-enforces SOFT-only routing so the import cannot silently acquire hard-typing authority.",
    "ASM-1372": "Closes generation to the pinned source estate so the build is reproducible with no hidden enrichment.",
    "ASM-1373": "Preserves alignment-kernel provenance and records conflicts instead of silently narrowing.",
    "ASM-1374": "Declares the bridge table experiment-only authored content and shields it from per-item baseline-label tuning.",
    "ASM-1375": "Keeps the judge rubric bytes unchanged so arm scores remain comparable to the frozen g2 instrument.",
    "ASM-1376": "Pre-commits to fresh runs so no logged proxy row is reused as an arm output.",
    "ASM-1378": "Pins the verdict-name mapping before any label exists.",
    "ASM-1379": "Records the role separation so design, registration, and execution stay in separate hands.",
}
# sha pins for the two MEASURED tail rows (restated from their own claim text /
# recomputed from the committed artifact on 2026-07-12):
TAIL_MEASURED_SHAS = {
    "ASM-1361": ("; pins: labels-proxy.jsonl sha256 93a124478b8dba411bfd1a9fd07cbc96e874def8e6ac"
                 "819202c54c1b121754b3, result.json sha256 96a23be5b85f1d20d3182c04af8928c34b6635"
                 "6ca10588ca141ebf34891ab94a"),
    "ASM-1370": ("; pin: generation-report.json sha256 b8874a2408ea4a241f9adb04201c4233ed5a90aa7c"
                 "9f578c2dbbf0b679f4d21b"),
}


def build_tail():
    rows = json.load(open(os.path.join(ROOT, "poc/ontology-import-g2/proposed-asm.json")))
    out = []
    for r in rows:
        r = dict(r)
        r["id"] = r["id"].replace("PROPOSED-ASM-", "ASM-")
        r["owner"] = "coordinator-1"
        # intra-block references track the registered ids
        for k in ("claim", "backing_ref", "notes", "rationale"):
            if isinstance(r.get(k), str):
                r[k] = r[k].replace("PROPOSED-ASM-", "ASM-")
        if r["tag"] == "STIPULATED" and not (r.get("rationale") or "").strip():
            r["rationale"] = TAIL_RATIONALES[r["id"]]
        if r["id"] in TAIL_MEASURED_SHAS:
            r["backing_ref"] = r["backing_ref"] + TAIL_MEASURED_SHAS[r["id"]]
        out.append(r)
    return out


# ---------------- extracted JSON appendix blocks ----------------
def extract_json_block(path, want_ids):
    text = open(os.path.join(ROOT, path)).read()
    rows = []
    for m in re.finditer(r"```json\n(.*?)```", text, re.DOTALL):
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(data, list):
            for r in data:
                if isinstance(r, dict) and r.get("id", "").replace("PROPOSED-", "") in want_ids:
                    rows.append(r)
    out = []
    for r in rows:
        r = dict(r)
        r["id"] = r["id"].replace("PROPOSED-ASM-", "ASM-")
        r["owner"] = "designer-1"  # registration owner (source owners were non-schema labels)
        for k in ("claim", "backing_ref", "notes", "rationale"):
            if isinstance(r.get(k), str):
                r[k] = r[k].replace("PROPOSED-ASM-", "ASM-")
        r["date"] = r.get("date") or DATE
        out.append(r)
    return out


# ---------------- authored blocks (prose sources) ----------------
F2B_REF = ("registry/experiments/f2b-errors.json; registry/verdicts/f2b-transfer.json; "
           "docs/next/analysis/f2b-errors.md section 9")


def row(id, tag, claim, backing_ref, lb, rationale=None, resolution_path=None, notes=None):
    r = {"id": id, "tag": tag, "claim": claim, "backing_ref": backing_ref,
         "load_bearing": lb, "status": "open", "owner": "designer-1", "date": DATE}
    if rationale:
        r["rationale"] = rationale
    if resolution_path:
        r["resolution_path"] = resolution_path
    if notes:
        r["notes"] = notes
    return r


AUTHORED = [
    # --- f2b-errors §9 (ASM-1320..1329) ---
    row("ASM-1320", "MEASURED",
        "Lift anatomy: the f2b-transfer stage-2 primary +0.25066666666666704 decomposes exactly as "
        "190 help - 2 harm = 188 net corrected item-seeds/750; net lift is 100% def-match (+98) + "
        "term-match (+90); both claim types net zero; zero MCQ harm.",
        F2B_REF, True, notes="DERIVED from pinned run-records; reproduces the frozen effect_size exactly."),
    row("ASM-1321", "MEASURED",
        "Baseline determinism: both alone arms are argmax-deterministic; per-item vectors "
        "byte-identical across seeds {0,1,2}; all seed variance is retry-sampling variance.",
        F2B_REF, True, notes="DERIVED from pinned run-records."),
    row("ASM-1322", "MEASURED",
        "Claim no-bias: R1 AND R3 answer 'no' on 101/101 claim items at attempt 0; at these rungs "
        "claim-type items measure a response prior, not content discrimination; claim-false's 0.968 "
        "and claim-true's 0.205 are the same constant behavior.",
        F2B_REF, True, notes="DERIVED from pinned run-records."),
    row("ASM-1323", "MEASURED",
        "Engaged-but-immovable: the verifier rejected all 39 claim-true attempt-0 answers on every "
        "seed (39 of the 157 aggregate rejects) yet finals flipped on 4/117 item-seeds; the k=4 "
        "retry channel cannot move a ~99% binary prior.",
        F2B_REF, True, notes="DERIVED from pinned run-records."),
    row("ASM-1324", "MEASURED",
        "Refuted-key asymmetry: all 10 kernel-key-vs-ext-gold disagreement eval items are claim-type "
        "(0 of 149 MCQ keys refuted); accept-path enforcement locked 2 items wrong 6/6 item-seeds; "
        "reject-path enforcement failed 20/24; net measured harm -2 item-seeds (-0.0027); "
        "counterfactual full-enforcement harm ~ -0.029.",
        F2B_REF, True, notes="DERIVED from pinned run-records; counterfactual figure is a recomputation, not a run."),
    row("ASM-1325", "MEASURED",
        "Residual attribution: of 265 kernel-arm wrong item-seeds, ~97% are host proposal failure "
        "under budget k=4 and ~3% kernel-content-attributable.",
        F2B_REF, True, notes="DERIVED from pinned run-records."),
    row("ASM-1326", "MEASURED",
        "Noninferiority localization: the noninferiority_vs_r3 FALSE is entirely term-match (-0.307); "
        "on def-match the R1+verifier arm exceeds R3-alone by +0.387 and repairs 59% of R3's own "
        "def-match errors.",
        F2B_REF, True, notes="DERIVED from pinned run-records."),
    row("ASM-1327", "MEASURED",
        "Forced-miss signature: shuffled-verify recovers 2.7% of the lift; term-match shuffled is "
        "identical to alone exactly at every seed; retrieval-miss degrades to model-alone, not below "
        "it, via budget exhaustion.",
        F2B_REF, True, notes="DERIVED from pinned run-records."),
    row("ASM-1328", "MEASURED",
        "Shared-quantile sampler: the retry multinomial generator is seeded (SEED_BASE, seed, "
        "attempt) without item - within-seed cross-item draw correlation exists; per-item-"
        "independence assumptions of the bootstrap are partially violated; no verdict-risk "
        "determination is made here.",
        F2B_REF, False, notes="Disclosed instrument limitation, flagged to the audit record."),
    row("ASM-1329", "STIPULATED",
        "Mechanism law (INTERPRETIVE class): at this scope, verify-retry lift is "
        "selection-not-injection - bounded by host tail mass on the key within k; harm from wrong "
        "keys bounded by the same steerability; value of the store concentrated in the stop rule's "
        "content.",
        "docs/next/analysis/f2b-errors.md sections 8-9", False,
        rationale="Interpretive mechanism reading adopted at this scope only, resting on the "
                  "document's sections 1-6 derived facts; licenses no verdict change and no wider claim."),
    # --- honesty-first-scoring §6 (ASM-1330..1339) ---
    row("ASM-1330", "STIPULATED",
        "KOT-HON/1 per-item utility is u_lambda = +1 correct / 0 explicit fail-closed abstention (a "
        "MISS: stays in the denominator) / -lambda wrong; a silent empty answer on an answerable "
        "item is WRONG, not an abstention; S_lambda = mean u_lambda over ALL in-scope items; "
        "abstentions are never removed from the denominator.",
        "docs/next/design/honesty-first-scoring.md section 1.1; maintainer issue-18 directive 2026-07-11",
        True, rationale="Defines the utility so abstention is priced explicitly and silent empties "
                        "cannot masquerade as abstentions."),
    row("ASM-1331", "STIPULATED",
        "The penalty band is lambda in [2, 5], default lambda = 3; lambda fixes the rational "
        "confidence threshold t* = lambda/(1+lambda) (2/3 ... 5/6), making sub-t* guessing strictly "
        "EV-negative while bounding single-item influence (1+lambda)/N at programme gold sizes; "
        "lambda is NOT set to precision-floor odds pi/(1-pi).",
        "docs/next/design/honesty-first-scoring.md section 1.3; maintainer issue-18 directive 2026-07-11",
        True, rationale="Fixes the penalty band from the rational-confidence-threshold argument "
                        "rather than post-hoc fit to any observed number."),
    row("ASM-1332", "STIPULATED",
        "lambda is pinned per surface at prereg-freeze, before any number exists - from a declared "
        "wrong:correct harm ratio clamped to [2, 5] where the surface declares one, else default 3; "
        "changing lambda after a readout is an endpoint version change (ASM-1116-class discipline: "
        "registered before any re-scored readout, as-written numbers carried beside in perpetuity); "
        "S_2 and S_5 are mandatory sensitivity co-reports.",
        "docs/next/design/honesty-first-scoring.md section 1.4; maintainer issue-18 directive 2026-07-11",
        True, rationale="Pins lambda at prereg-freeze so scoring can never be tuned to an observed readout."),
    row("ASM-1333", "STIPULATED",
        "The S_lambda scalar never travels without its vector: answer rate, precision-on-answered, "
        "abstention rate (reasoned vs reasonless split), wrong-rate, raw recall, and the S_2/S_5 "
        "pair; CIs by item-level (hierarchical) bootstrap per the ASM-0813 house rules, margin "
        "claims by LCB.",
        "docs/next/design/honesty-first-scoring.md section 1.5; maintainer issue-18 directive 2026-07-11",
        True, rationale="Prevents the scalar from travelling without its diagnostic vector."),
    row("ASM-1334", "STIPULATED",
        "Degenerate-abstention guard: abstain-always scores S_lambda = 0 and FAILS; every KOT-HON/1 "
        "endpoint carries a pre-registered answer-rate/coverage co-floor or a full risk-coverage "
        "curve; S_lambda prices answering honesty only - coverage remains a separate axis with its "
        "own endpoints.",
        "docs/next/design/honesty-first-scoring.md section 1.5; maintainer issue-18 directive 2026-07-11",
        True, rationale="Blocks abstention gaming as a route to a passing score."),
    row("ASM-1335", "STIPULATED",
        "Non-retroactivity: KOT-HON/1 amends no frozen floor, endpoint, or verdict; the CODEVERT G1 "
        "mechanical verdict on the ASM-1030 floors as written stands; applying KOT-HON/1 to any "
        "frozen result is an exploratory co-reading carried beside the as-written numbers; "
        "re-pinning any frozen surface onto KOT-HON/1 (the G1 option-(iii) route) is a maintainer + "
        "review-gate decision.",
        "docs/next/design/honesty-first-scoring.md section 2.1; maintainer issue-18 directive 2026-07-11",
        True, rationale="Keeps KOT-HON/1 non-retroactive over frozen floors, endpoints, and verdicts."),
    row("ASM-1336", "MEASURED",
        "The CODEVERT G1 asymmetric co-reading (DERIVED, exploratory, PROVISIONAL-ON-LLM-PROXY, void "
        "on human re-annotation): R_q leg (160 gold-answerable) C=123/A=37/W=0 gives S_lambda = "
        "0.7688 lambda-invariant vs 0.3063/0.0750/-0.3875 for a forced-answer system at identical "
        "raw R_q; precision leg (474 elements, 32 AnnAssign wrongs) S_3 = 0.7300 vs raw 0.9325; "
        "neg-validity leg 6/6 gives 1.0; it licenses no verdict change.",
        "poc/codevert-g1/results/g1-endpoints-proxygold.json sha256 "
        "eb580cdfcacecae44dd6f1947f5513020c586d247801c9f5273f350b2dd56ab0; "
        "docs/next/design/honesty-first-scoring.md section 7 arithmetic checks",
        False, notes="Exploratory co-reading of frozen numbers; PROVISIONAL-ON-LLM-PROXY; void on "
                     "human re-annotation; never a premise for a verdict change."),
    row("ASM-1337", "STIPULATED",
        "Dual-variant rule: S-HON (honesty-first, fail-closed reasoned abstention tuned to the "
        "pinned lambda) is the programme's default identity and the subject of all product/honesty "
        "claims; S-BENCH (non-penalised forced-answer, same architecture/store where possible) is "
        "the ONLY variant entered in AI-index/W1/G4 head-to-heads and external leaderboards and "
        "makes no honesty/provenance claim; variant identity is disclosed on every claim surface; "
        "numbers are never mixed; each prereg names which variant each endpoint binds.",
        "docs/next/design/honesty-first-scoring.md section 4.2; maintainer issue-18 directive 2026-07-11",
        True, rationale="Separates the honesty-first identity from the benchmark variant so numbers "
                        "are never mixed across claim surfaces."),
    row("ASM-1338", "STIPULATED",
        "Programme-3 integration: the KOT-AI-INDEX/2 headline stays raw-accuracy-normalised and W1 "
        "is fought by S-BENCH (no change to ASM-0810/0811); S_lambda (lambda=3, with S_2/S_5) is "
        "co-reported per domain in the index vector for abstention-capable arms as a diagnostic, "
        "never the headline; the section-1.5 answer-rate co-floor is the mechanised counter for the "
        "threat model's named abstention-gaming channel; the price-of-honesty delta INDEX(S-BENCH) - "
        "INDEX(S-HON) is a mandatory published figure wherever both variants run; landing these in "
        "the frozen framework goes through P3-D-INDEX's own review path.",
        "docs/next/design/honesty-first-scoring.md section 4.3; maintainer issue-18 directive 2026-07-11",
        True, rationale="Integrates S_lambda into programme-3 as a diagnostic co-report without "
                        "changing the frozen headline."),
    row("ASM-1339", "STIPULATED",
        "Scope: KOT-HON/1 applies to item-level answer/abstain/wrong surfaces (query answering, "
        "verifier-loop outputs, parse-or-abstain front-ends, store-backed QA); it does not apply to "
        "legs without an abstention action (coverage censuses, kappa agreement legs, determinism "
        "gates), which retain their own endpoints.",
        "docs/next/design/honesty-first-scoring.md section 2.1; maintainer issue-18 directive 2026-07-11",
        True, rationale="Bounds KOT-HON/1's scope to surfaces that actually have an abstention action."),
    # --- nlb-0a interpretation (ASM-1340..1343) ---
    row("ASM-1340", "STIPULATED",
        "The NLB-0-A readout's doc-note stipulations ASM-1090...ASM-1095 (generalised fail-closed "
        "frame/op-selection law; inventory-A ablation status; l3a co-report licence; l3a op-arity "
        "rule; section-7.1 arithmetic instantiation; post-outcome disclosure attachment) are "
        "registered as written in docs/next/analysis/nlb-0a.md section 7, retaining their original "
        "numbering.",
        "docs/next/interpretations/nlb-0a.md; docs/next/analysis/nlb-0a.md section 7",
        True, rationale="Adopts the readout's doc-note stipulations into the ledger without renumbering."),
    row("ASM-1341", "STIPULATED",
        "NLB.md section 2's a5 dangerous-class mechanism description ('direction-table flip') is "
        "superseded by the measured mechanism (same-orientation two-op substitution, contained-in "
        "vs where-defined, discriminating information absent from the surface); the next NLB.md "
        "revision must carry the corrected text and restate section 3.1's repair law in the "
        "ASM-1090 generalised form; until that revision lands, any citation of NLB.md section 2's "
        "mechanism line must carry this correction.",
        "docs/next/interpretations/nlb-0a.md; docs/next/analysis/nlb-0a.md section 1",
        True, rationale="Ensures the superseded mechanism description cannot be cited uncorrected."),
    row("ASM-1342", "STIPULATED",
        "Per NLB.md section 7.2 read strictly, the a5 vertical's NLB-0-B GO condition is "
        "unsatisfiable while the section-7.1 A-leg proceed condition stands NOT MET (measured "
        "2026-07-11); the a5 vertical is design-blocked pending a design-revision decision on the "
        "container-ask two-op ambiguity (annotation-channel vs distinguishable-phrasing protocol, "
        "or both - the 10% ambiguity cap of ASM-0942(3) is the binding constraint to check); the "
        "l3a vertical is NOT blocked by this; no registered redesign cycle is consumed "
        "(ASM-0904(4)/ASM-0944(4)).",
        "docs/next/interpretations/nlb-0a.md; docs/next/analysis/nlb-0a.md section 4",
        True, rationale="Records the mechanical design block without consuming a registered redesign cycle."),
    row("ASM-1343", "STIPULATED",
        "Any a5 NLB-0-B retention read must be decomposed against the container-ask frame-group "
        "before interpretation: the crossed-surface mass is information-absent for ANY parser tier, "
        "so retention shortfall attributable to it measures the known ambiguity, not Tier-1 recipe "
        "headroom; the decomposition is computed from the pilot's per-family counters, never "
        "assumed.",
        "docs/next/interpretations/nlb-0a.md; docs/next/analysis/nlb-0a.md section 2",
        True, rationale="Forces decomposition against the known two-op ambiguity before any retention read."),
]


def main():
    lines = open(REG).read().splitlines()
    entries = [json.loads(l) for l in lines if l.strip()]
    assert len(entries) == 477, len(entries)
    head = entries[:457]                       # untouched rows
    tail_old = entries[457:]
    assert all(e["id"].startswith("PROPOSED-ASM-13") for e in tail_old), "tail window mismatch"

    tail_new = build_tail()
    assert len(tail_new) == 20

    existing = {e["id"] for e in head} | {e["id"] for e in tail_new}

    appended = []
    fsv4 = extract_json_block("docs/next/feasibility-synthesis-v4.md",
                              {"ASM-%d" % n for n in range(1240, 1246)})
    plan = extract_json_block("docs/next/design/ontology-import-plan.md",
                              {"ASM-%d" % n for n in range(1260, 1280)})
    assert len(fsv4) == 6 and len(plan) == 20, (len(fsv4), len(plan))
    for r in fsv4 + plan + AUTHORED:
        if r["id"] in existing:
            print("dedup: %s already registered, skipping" % r["id"])
            continue
        existing.add(r["id"])
        appended.append(r)

    # validate every touched row
    f = F()
    for r in tail_new + appended:
        claims_check.check_entry(r, r["id"], f)
    if f.items:
        for code, msg in f.items:
            print("PRE-WRITE FAIL %s: %s" % (code, msg))
        sys.exit(1)

    out = head + tail_new + appended
    with open(REG, "w") as fh:
        for e in out:
            fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    print("wrote %d rows (tail normalized: 20; appended: %d)" % (len(out), len(appended)))
    for r in appended:
        print("  +", r["id"], r["tag"])


if __name__ == "__main__":
    main()
