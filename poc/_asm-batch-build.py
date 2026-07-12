#!/usr/bin/env python3
"""Assemble poc/_asm-batch-pending.jsonl — every EMITTED-but-UNREGISTERED
PROPOSED-ASM row, registry schema, dedup'd against registry/assumptions.jsonl.
PREP artifact only: does NOT touch registry/assumptions.jsonl.
Sources (verbatim JSON extraction):
  docs/next/arch/world-model-rules-engine.md      ASM-1120..1139 (Appendix A) + 1160..1164 (GPT-5.6 fold-in §5)
  docs/next/arch/foundational-ontology-import.md  ASM-1210..1218 (Appendix)
  docs/next/arch/expressivity-analysis.md         ASM-1230..1238 (Appendix A)
Sources (prose blocks, rows authored here from the doc's verbatim entries):
  docs/next/design/knull-optionb-analysis.md      ASM-1080..1088
  docs/next/analysis/nlb-0a.md                    ASM-1090..1095
  poc/codevert-g1/DESIGN-PIN.md                   ASM-1110..1119
NSM-UFO bridge (poc/gpt56-review/nsm-ufo-bridge/last-message.json): emits NO ASM rows; block 1220-29 unused.
"""
import json, re, sys, collections

ROOT = "/home/ec2-user/css/kernel/kernel-of-truth"
VALID_TAGS = {"MEASURED", "LIT-BACKED", "STIPULATED", "EXTRAPOLATION"}
DATE = "2026-07-11"

# ---------- registered ids (dedup set) ----------
registered = set()
with open(f"{ROOT}/registry/assumptions.jsonl") as f:
    for line in f:
        line = line.strip()
        if line:
            registered.add(json.loads(line)["id"])

# ---------- extract verbatim JSON rows from the three arch docs ----------
def extract_json_rows(path):
    rows = []
    with open(path) as f:
        for line in f:
            s = line.strip().rstrip(",")
            if s.startswith('{"id":"PROPOSED-ASM-'):
                rows.append(json.loads(s))
    return rows

extracted = []
for p in ("docs/next/arch/world-model-rules-engine.md",
          "docs/next/arch/foundational-ontology-import.md",
          "docs/next/arch/expressivity-analysis.md"):
    extracted += extract_json_rows(f"{ROOT}/{p}")

# targeted fixes on extracted rows (documented in notes)
FIXES = {
    # EXTRAPOLATION row emitted without resolution_path
    "PROPOSED-ASM-1134": {"resolution_path":
        "The RULES-1 run-log's actual Modal cost ledger ($ per leg) converts each band to "
        "MEASURED or refutes it; any leg whose measured cost exceeds its band forces a re-price "
        "before approval of the next leg."},
    # EXTRAPOLATION row emitted with empty rationale
    "PROPOSED-ASM-1218": {"rationale":
        "Names the directional expectation behind the PROPOSED-ASM-1217 gate so it is a recorded, "
        "falsifiable projection rather than an implicit hope; premises nothing while open."},
}

rows = []
for r in extracted:
    rid = r["id"]
    r = dict(r)
    for k, v in FIXES.get(rid, {}).items():
        note = f"[batch-prep fix: {k} supplied; doc emission lacked it]"
        r[k] = v
        r["notes"] = (r.get("notes", "") + " " + note).strip()
    # strip PROPOSED- prefix
    r["id"] = rid.replace("PROPOSED-ASM-", "ASM-")
    r["claim"] = r["claim"].replace("PROPOSED-ASM-", "ASM-")
    for k in ("backing_ref", "rationale", "notes", "resolution_path"):
        if k in r and isinstance(r[k], str):
            r[k] = r[k].replace("PROPOSED-ASM-", "ASM-")
    # EXTRAPOLATION convention: load_bearing must be false + non-empty resolution_path
    if r["tag"] == "EXTRAPOLATION":
        if r.get("load_bearing") is not False:
            r["load_bearing"] = False
            r["notes"] = (r.get("notes", "") + " [batch-prep fix: load_bearing forced false "
                          "per register convention for EXTRAPOLATION rows; doc emitted true]").strip()
        assert r.get("resolution_path"), f"{r['id']}: EXTRAPOLATION without resolution_path"
    # owner pseudonym repair
    if r.get("owner") != "designer-1":
        r["notes"] = (r.get("notes", "") + f" [batch-prep fix: owner '{r.get('owner')}' -> designer-1]").strip()
        r["owner"] = "designer-1"
    r["status"] = "open"
    rows.append(r)

# ---------- authored rows: knull ASM-1080..1088 (prose block, all STIPULATED) ----------
KNULL_REF = "docs/next/design/knull-optionb-analysis.md"
def row(id, tag, claim, backing_ref, rationale, load_bearing, notes, resolution_path=None):
    r = {"id": id, "tag": tag, "claim": claim, "backing_ref": backing_ref,
         "rationale": rationale, "load_bearing": load_bearing, "status": "open",
         "owner": "designer-1", "date": DATE, "notes": notes}
    if resolution_path:
        r["resolution_path"] = resolution_path
    return r

rows += [
 row("ASM-1080","STIPULATED",
  "Option-B ruling adopted (maintainer decision issue 6, 2026-07-11): the knull plain arm is authored at natural concise dictionary length; G-1 clause L-3 (the +/-25% word band) is DROPPED and L-4 is RELAXED to >=1 admissible claim segment for the plain store; all other G-1 clauses unchanged; the ASM-0703 blind quality gate is re-run on the v3 store as a freeze precondition. Store: poc/knull/inputs-v3/plain-authored.json v3.0.0.",
  f"{KNULL_REF} §1; maintainer ruling issue 6 (2026-07-11); poc/knull/inputs-v3/plain-authored.json v3.0.0",
  "Adopts the maintainer's ruling as the named governing premise for the knull-v2 plain arm so the relaxed authoring gate is a recorded stipulation, not a silent change to G-1.",
  True,"Emitted in the knull option-B analysis PROPOSED-ASM block; block ASM-1080..1089 reserved to that deliverable, 1089 unused."),
 row("ASM-1081","STIPULATED",
  "Length-confound control: the verdict-bearing control is the experimental length-matched plain-padded arm; token-count covariate/regression adjustment is DESCRIPTIVE only (no within-concept identification; intercept-at-parity is an extrapolation premise), never verdict-bearing.",
  f"{KNULL_REF} §3-4",
  "Preserves the no-extrapolation-as-premise discipline: regressing to token parity projects outside the design and may not carry a verdict; only an actually-run matched arm may.",
  True,"Knull option-B block."),
 row("ASM-1082","STIPULATED",
  "plain-padded generator: cyclic whole-own-segment repetition joined by '; ' into the kernel-gloss word band [0.75*wc, max(1.25*wc, wc+8)]; degenerate no-pad allowed in-band; fail-closed (band landing, segment-set equality, LC1, uniqueness); deterministic transform, no authoring gate; feasibility MEASURED 108/108 on v3.0.0; disclosed bias direction: any answer-key-repetition effect favors the padded arm — conservative against the content claim.",
  f"{KNULL_REF} §3; poc/knull/inputs-v3/",
  "A deterministic fail-closed transform (opaque-generator precedent) supplies the length-matched control without a second authoring gate; the disclosed bias direction runs against the kernel claim, so the control is conservative.",
  True,"Knull option-B block; feasibility leg is MEASURED, the design choice is the stipulated part."),
 row("ASM-1083","STIPULATED",
  "Superiority guard (IUT): kernel_superior_beyond_margin = [LB95_1s(D_full) > +0.05] AND [LB95_1s(D_matched) > +0.05], D_matched vs the eligible token-matched arm (plain-padded, else opaque) with larger point lift; conjunction at fixed margin — no Holm resize; no eligible token-matched arm => length_guard_available=false and superiority forced false.",
  f"{KNULL_REF} §4",
  "Intersection-union conjunction at fixed margin keeps the superiority claim honest against both the full and matched comparisons without alpha resizing; forcing false when the guard is unavailable fails closed.",
  True,"Knull option-B block."),
 row("ASM-1084","STIPULATED",
  "NULL and FAIL readings are unchanged in form and licensed a fortiori under the plain arm's smaller budget; the NULL relabel adopts the clause 'at no greater token budget'; the extrapolation envelope gains the natural-length scope sentence.",
  f"{KNULL_REF} §4",
  "A null or fail found against a cheaper comparator is at least as strong as the pre-registered reading; the added clauses keep the envelope exact about the natural-length scope.",
  True,"Knull option-B block."),
 row("ASM-1085","STIPULATED",
  "Gate scope: flops-parity (run-time +/-20%; pre-freeze G-3 +/-10%) binds plain-padded and opaque vs kernel; the concise plain arm is exempt by design, its ratio metered and reported DESCRIPTIVE (/gates/flops_ratio_plain); difficulty-band and extraction gates extend to plain-padded.",
  f"{KNULL_REF} §5",
  "Parity gates bind only the arms that claim parity; the concise arm's budget advantage is the design's point, so its ratio is metered for disclosure rather than gated.",
  True,"Knull option-B block."),
 row("ASM-1086","STIPULATED",
  "plain-padded cell budget: alone-R1 + verify-retry-R1, seeds {0,1,2}, same 1000 paired skeletons; excluded from the alone-R3 bridge and the shuffled control (role-limited length control).",
  f"{KNULL_REF} §5-6",
  "The padded arm exists solely to control length on the verdict-bearing cells; excluding it from bridge and shuffled cells caps cost without weakening the control's role.",
  True,"Knull option-B block."),
 row("ASM-1087","STIPULATED",
  "Quality-gate scope: ASM-0703 applies to the authored concise store only; the padded arm is disclosed REAL non-authored arm content (deterministic transform; opaque-generator precedent).",
  f"{KNULL_REF} §5,§7",
  "The blind quality gate certifies authored content; a deterministic transform of already-gated content needs disclosure, not a second gate — the opaque-generator precedent.",
  True,"Knull option-B block."),
 row("ASM-1088","STIPULATED",
  "Pre-freeze token evidence status: the substitution projection (poc/knull/inputs-v3/token-projection.json — plain 0.626, plain-padded 0.931 of kernel mean prompt tokens; gloss-level plain 0.309 MEASURED) is pre-freeze evidence only; binding resolution = the v3-build G-3 artifact and the run-time F0 FLOPs ledger.",
  f"{KNULL_REF} §2,§7; poc/knull/inputs-v3/token-projection.json",
  "Names the projection's evidentiary ceiling so pre-freeze token arithmetic is never quoted as the binding parity evidence; the built artifact and run-time ledger decide.",
  True,"Knull option-B block; ASM-1089 reserved unused."),
]

# ---------- authored rows: NLB ASM-1090..1095 (doc-note block, all STIPULATED) ----------
NLB_REF = "docs/next/analysis/nlb-0a.md"
rows += [
 row("ASM-1090","STIPULATED",
  "NLB-0-A applies NLB §3.1's fail-closed rule to frame/op-selection evidence generally (the measured dangerous class is same-orientation op substitution, not direction flip); 'orientation cues absent or conflicting -> no parse' reads 'frame-selection evidence absent, conflicting, or non-discriminating -> no parse'.",
  f"{NLB_REF} §1,§7; docs/next/design/NLB.md §3.1",
  "Generalises the fail-closed rule to the mechanism the diagnostic actually measured, so the repair targets the real dangerous class instead of the anticipated one.",
  True,"NLB-0-A doc-note block; ASM-1096..1099 remain free."),
 row("ASM-1091","STIPULATED",
  "The inventory-A own-label ablation arm is a diagnostic co-report quantifying the wrong-leg counterfactual; never a candidate Tier-0.",
  f"{NLB_REF} §2,§7",
  "Keeps the ablation arm in its diagnostic role: it quantifies the counterfactual without ever competing for Tier-0 status, so the acceptance is never silently broadened.",
  True,"NLB-0-A doc-note block."),
 row("ASM-1092","STIPULATED",
  "The l3a legacy re-run is a supplementary diagnostic co-report under ASM-0904(2) semantics; not part of the NLB §7.1 proceed condition.",
  f"{NLB_REF} §3,§7; ASM-0904",
  "Scopes the legacy re-run as diagnostic colour so the proceed condition stays exactly the pre-stated §7.1 test.",
  True,"NLB-0-A doc-note block."),
 row("ASM-1093","STIPULATED",
  "The l3a imperative/number op-arity rule (head-noun grammatical number decides unique-vs-lookup under list/name/find starts; conflict -> refuse) joins the l3a inventory.",
  f"{NLB_REF} §2,§7",
  "A design-faithful repair of the measured op-arity miss class: mechanical, refusal-on-conflict, and added to the inventory rather than patched ad hoc.",
  True,"NLB-0-A doc-note block."),
 row("ASM-1094","STIPULATED",
  "NLB §7.1 arithmetic instantiation: dangerous-wrong <= 4 (count), retention floor = 356/855 - 0.02 = 0.396374..., point estimates.",
  f"{NLB_REF} §4,§7",
  "Fixes the exact arithmetic of the pre-stated proceed condition so the evaluation is a mechanical comparison, not a post-hoc reading.",
  True,"NLB-0-A doc-note block."),
 row("ASM-1095","STIPULATED",
  "Post-outcome disclosure of NLB-0-A §6 (scope limits: legacy corpora, K=1, point estimates, design-phase diagnostic) attaches to every artifact and any quotation of these numbers.",
  f"{NLB_REF} §6,§7",
  "Binds the scope-limit disclosure to the numbers themselves so no later quotation strips the diagnostic, point-estimate, legacy-corpus caveats.",
  True,"NLB-0-A doc-note block."),
]

# ---------- authored rows: codevert ASM-1110..1119 (design-pin table, all STIPULATED) ----------
CV_REF = "poc/codevert-g1/DESIGN-PIN.md"
rows += [
 row("ASM-1110","STIPULATED",
  "CODEVERT-FL/1 = primary families {contains, contained_in, imports_of, where_defined} (FL-4); callees_of = disclosed sensitivity slice (annotated and reported identically, never in the primary aggregate); callers_of/imported_by/instance_of excluded from the re-scoped product claim (PY-STAT/2 territory); the maintainer-gloss 'kappa~=0.72' vs G0-option-(a) family ambiguity resolved as pinned in §1, not post-hoc.",
  f"{CV_REF} §1,§6; maintainer decision issue 16 (2026-07-11)",
  "Pins the scored universe before any G1 data exists and records the resolution of the maintainer-gloss ambiguity at pin time, so the primary aggregate cannot drift toward whichever family set performs.",
  True,"CODEVERT G1-forward design pin; block ASM-1110..1119; entire instrument PROVISIONAL-ON-LLM-PROXY."),
 row("ASM-1111","STIPULATED",
  "G1 pool: the §2.1 pinned-before-looking 20+5 repo list (names and order fixed at design-pin time, disjoint from the G0 six), size band [300,120000] analyzed *.py LOC, mechanical backup substitution in pinned order on clone/license/band failure, shallow-HEAD SHAs recorded; agent-selected disclosure — every cross-repo band is a resampling sensitivity band, never a generalization CI; all-*.py analyzed scope + package-source-only co-report.",
  f"{CV_REF} §2,§2.1,§6; repos.lock.json",
  "Pinning the pool by name and order before any repo content is seen removes selection-after-looking; the agent-selected honesty clause keeps cross-repo bands from being read as population CIs.",
  True,"CODEVERT G1 design pin."),
 row("ASM-1112","STIPULATED",
  "G1 census = G0 census.py generator logic (content-hash-pinned, extractor-independent) with fresh pinned seed 20260716, generated and hashed before the extractor runs; extractor PY-STAT/1 byte-identical to poc/codevert-g0/extractor.py (any edit = extractor version change per ASM-1031, voiding the run); FL-4 primary aggregate (query-pooled + family-macro), all-8 families co-reported; repo-cluster bootstrap (seed 20260716, 10k) = sensitivity band only.",
  f"{CV_REF} §3,§6; freeze-manifest.json; ASM-1031; ASM-1052",
  "Census-before-extraction ordering and a byte-identical extractor make the G1 measurement a pure new-data replication of the pinned instrument.",
  True,"CODEVERT G1 design pin."),
 row("ASM-1113","STIPULATED",
  "Proxy gold: two LLM annotators (fable-a Claude-family; gpt56-b gpt-5.6-sol via pinned codex@0.144.1 invocation, effort medium — a disclosed deviation from the judge-1p 'low'), blind and independent, byte-identical instructions and context bundles; disagreements adjudicated by the Fable main agent with per-item logged rationale (annotation/adjudication.jsonl); ALL gold-dependent endpoints PROVISIONAL-ON-LLM-PROXY, void the moment a human Pass-B annotation of the same sample lands.",
  f"{CV_REF} §4,§6; maintainer decision issue 16",
  "LLM stand-in gold is the maintainer-approved instrument for this leg; the blindness, logged adjudication, and void-on-human-gold clause keep it honestly provisional rather than silently authoritative.",
  True,"CODEVERT G1 design pin; g3-humangold pattern."),
 row("ASM-1114","STIPULATED",
  "Sample: 2 queries per (family x repo) cell over 5 measured families x 20 repos = 200 queries, seed-pinned (20260716) from the frozen census universes; cells smaller than 2 take all and log the shortfall; 120 KB context-bundle cap with pinned next-index replacement rule (logged, never silently dropped); no-label >10% per endpoint => instrument-invalid for that endpoint.",
  f"{CV_REF} §4,§6",
  "A seed-pinned cell design with mechanical replacement and a pre-stated invalidity threshold makes the proxy-gold sample auditable and fail-closed.",
  True,"CODEVERT G1 design pin."),
 row("ASM-1115","STIPULATED",
  "Element normalization rules of §4: contains/contained_in and repo-internal callees compared as relpath::qualpath symbols (module target = relpath); imports_of as repo:relpath for repo-internal (with parent-package closure + self-edges per ASM-1058) and ext:<base> for external per the PY-STAT/1 emission rule; where_defined as (relpath, lineno) sites with engine spans mapped to lines mechanically; callees_of precision/R_q computed on repo-internal elements only (disclosed).",
  f"{CV_REF} §4,§6; ASM-1058",
  "Pinned normalization removes scorer discretion at comparison time; the repo-internal-only callee scoring is the one disclosed narrowing, taken because external-callee naming is not reliably normalizable.",
  True,"CODEVERT G1 design pin."),
 row("ASM-1116","STIPULATED",
  "Answerability protocol + endpoint definitions: each annotator marks answerable-static yes/no + gold set (possibly empty) + conditional/lazy flags; on adjudicated proxy gold, precision = element-level correctness of proved listings, R_q = fraction of gold-answerable queries returned proved with the FULL gold set, negative-answer validity = fraction of gold-empty queries answered proved-empty; floors quoted from ASM-1030 (kappa_q^indep >= 0.5, R_q >= 0.90, precision >= 0.95, neg-validity >= 0.90); the mechanical verdict is the coordinator's step — this run produces verdict-INPUT only.",
  f"{CV_REF} §4,§6; ASM-1030",
  "Endpoint definitions and floors are fixed at pin time and the verdict is mechanically the coordinator's, preserving run-vs-verdict separation.",
  True,"CODEVERT G1 design pin."),
 row("ASM-1117","STIPULATED",
  "PY-STAT/2-SPIKE scope: D1 local-alias, D2 parametrized-decorator return analysis, D3 call-result return analysis — bounded local dataflow, candidates-only (NO proved upgrades), non-scored, measured on the pinned G0 corpus against the FROZEN G0 census; any full PY-STAT/2 build is an extractor version change per ASM-1031 (new inventory, new census freeze, new spike); spike output is a build/no-build verdict-INPUT only.",
  f"{CV_REF} §5,§6; pystat2-spike/; ASM-1031",
  "Candidates-only scoping lets the spike price the excluded-family territory without contaminating the scored instrument or upgrading anything to proved.",
  True,"CODEVERT G1 design pin."),
 row("ASM-1118","STIPULATED",
  "Spike metrics: '*'-mass conversion by mechanism, per-family kappa recovery vs the G0 ablation ceiling, and probe-trace candidate-narrowing exclusion count as the soundness guard.",
  f"{CV_REF} §5,§6",
  "Names the spike's three read-outs in advance so the build/no-build input is a pre-stated measurement, not a post-hoc selection.",
  True,"CODEVERT G1 design pin."),
 row("ASM-1119","STIPULATED",
  "Session governance for the G1 leg: no git/bd/kb operations by the experiment agent; no @-handle strings in artifacts; every measured number tagged [MEASURED]; every gold-dependent number additionally PROVISIONAL-ON-LLM-PROXY; nothing produced is a scored verdict — the coordinator runs the mechanical verdict against the pinned floors.",
  f"{CV_REF} preamble,§6",
  "Records the role separation and tagging discipline the leg ran under, so provenance and the provisional status of every gold-dependent number are auditable.",
  True,"CODEVERT G1 design pin; auditability caveat: pin-before-clone is filesystem-time-consistent only (no git object at pin time), disclosed verbatim from G0."),
]

# ---------- validate + dedup + emit ----------
REQUIRED = ("id","tag","claim","backing_ref","rationale","load_bearing","status","owner","date","notes")
errors, out, seen = [], [], set()
for r in rows:
    rid = r["id"]
    if rid in registered:
        errors.append(f"{rid}: ALREADY REGISTERED — dropped"); continue
    if rid in seen:
        errors.append(f"{rid}: DUPLICATE in batch"); continue
    seen.add(rid)
    for k in REQUIRED:
        if k not in r: errors.append(f"{rid}: missing field {k}")
    if r["tag"] not in VALID_TAGS: errors.append(f"{rid}: bad tag {r['tag']}")
    if r["status"] != "open": errors.append(f"{rid}: status != open")
    if r["owner"] != "designer-1": errors.append(f"{rid}: owner {r['owner']}")
    if not isinstance(r["load_bearing"], bool): errors.append(f"{rid}: load_bearing not bool")
    if not r["rationale"].strip(): errors.append(f"{rid}: empty rationale")
    if r["tag"] == "EXTRAPOLATION":
        if r["load_bearing"] is not False: errors.append(f"{rid}: EXTRAPOLATION with load_bearing != false")
        if not r.get("resolution_path","").strip(): errors.append(f"{rid}: EXTRAPOLATION without resolution_path")
    if "PROPOSED" in rid: errors.append(f"{rid}: PROPOSED prefix not stripped")
    out.append(r)

out.sort(key=lambda r: int(r["id"].split("-")[1]))
if errors:
    print("VALIDATION ERRORS:"); [print(" -", e) for e in errors]; sys.exit(1)

with open(f"{ROOT}/poc/_asm-batch-pending.jsonl", "w") as f:
    for r in out:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

blocks = collections.Counter()
for r in out:
    n = int(r["id"].split("-")[1])
    for name, lo, hi in (("knull 1080-89",1080,1089),("nlb 1090-99",1090,1099),
                         ("codevert 1110-19",1110,1119),("wmre 1120-39",1120,1139),
                         ("wmre-foldin 1160-64",1160,1164),("onto-import 1210-18",1210,1229),
                         ("expressivity 1230-39",1230,1239)):
        if lo <= n <= hi: blocks[name] += 1
print(f"TOTAL rows: {len(out)}")
for k in sorted(blocks): print(f"  {k}: {blocks[k]}")
print("ids:", ", ".join(r["id"] for r in out))
print("EXTRAPOLATION rows:", [r["id"] for r in out if r["tag"]=="EXTRAPOLATION"])
