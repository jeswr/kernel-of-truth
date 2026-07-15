#!/usr/bin/env python3
"""
run_s5.py -- S5 (reference-augmented generation) driver for the molecule-aug
experiment (DESIGN.md §§4-8). Exploratory methodology R&D: NO prereg, NO
registry write, NO git commit. Builder runs only `compose`/`selftest` (and a
2-concept `dryrun` once codex auth is back); the coordinator runs `gen`,
`prep`, `judge`, `score`. Author: fable (lead designer/explicator).

Subcommands (all resumable; steps skip work whose output exists):

  compose                 s5-prompt.md   = concept-def-prompt.md + ref-addendum.md
                                           + lexicon/listing.txt   (DESIGN §4)
                          s5-judge-prompt.md = ast-pipeline judge_prompt.md
                                           + judge-addendum.md     (DESIGN §6)
  sample  --stage 2       stage-2 held-out 30 (deterministic stride over
                          candidate-pool URN order, excluding the 100 and
                          lexicon collisions; DESIGN §7.2) -> s5-run/stage2-heldout.json
  gen     --stage 1|2     S5 arm: 1 call per generator (gpt-5.6-luna,
                          claude-fable-5) per concept via define_concept.py
                          --prompt s5-prompt.md; held-out concepts also get
                          fresh FLAT calls with the pinned prompt. Every
                          written record is post-gated by validate-record-ref.mjs
                          (the pinned in-runner gate rejects references by
                          design; the variant gate is authoritative for S5).
  prep    --stage 1|2     merged blind judge inputs under s5-run/stageN/:
                          ast-pipeline pool (stage 1) or flat records (stage 2)
                          + gate-clean S5 records; dedup, seeded letter
                          shuffle, judge-key held back, per-concept
                          REFERENCED CONCEPTS block appended (DESIGN §6).
  judge   --stage N --judge A|B|T --i-am-the-coordinator
                          blind judging with the COMPOSED variant judge prompt
                          over s5-run/stageN/judge-inputs (same judge_one code
                          path, panel and verdict format as ast-pipeline).
                          NOTE (delta vs DESIGN §8 command sketch): judging
                          runs from here, not run_pipeline.py, because §6
                          requires the variant prompt for ALL candidates and
                          run_pipeline.py reads its own judge_prompt.md; the
                          ast-pipeline harness files are not touched.
  score   --stage N       paired per-concept judged-FAITHFUL deltas (S5 vs
                          flat, per generator), exact McNemar + Wilson CI,
                          self-flag/quality/reference-usage/gate secondaries,
                          stage-1 GO/NO-GO vs the STIPULATED +15pp threshold.
  dryrun                  2 NON-sample concepts end-to-end (gen S5 arm both
                          model families + prep); requires codex auth.
  selftest                OFFLINE plumbing check -- no model calls, no codex:
                          compose, variant-gate positive/negative vectors,
                          flat-record superset behaviour, prep + judge-input
                          shape on synthetic candidates, McNemar/Wilson units,
                          plus the v2 checks (expander goldens, Tango CI,
                          blind-id determinism, ITT/E2 truth table, freeze-pin
                          mismatch dies).

v2 subcommands (DESIGN-v2.md §9; supersede v1 stage-2 -- the campaign is
adjudicate -> compose --v2 -> sample --stage 3 -> calibrate -> freeze ->
pilot (stage 1) -> main (stage 3), see DESIGN-v2 §10):

  adjudicate-lexicon --judge F1|F2|F3 --i-am-the-coordinator
                          proxy adjudication of all 31 bridges + their
                          kernel-v0 reference closure against the frozen
                          bridge-review-rubric.md (ACCEPT/REPAIR/REJECT;
                          F3 on F1/F2 disagreement). --summarize builds the
                          final-verdict + chain-lossiness tables and relabels
                          ACCEPTed bridges 'provisional/model-authored
                          (proxy-adjudicated)' (DESIGN-v2 §4).
  compose [--v2]          also writes s5-judge-fidelity.md (base judge prompt
                          + judge-addendum-v2.md) and s5-judge-conditional.md
                          (base + v1 judge-addendum.md + single-candidate
                          note) (DESIGN-v2 §3.2).
  sample --stage 3        n=200 fresh sample by the frozen §5 rule (URN-order
                          stride over candidate-pool; exclude consensus-100
                          URNs, ALL-lemma lexicon slug collisions -- this
                          mechanically resolves initiation/institution -- and
                          the calibration concepts) -> s5-run/stage3-fresh.json
  calibrate --i-am-the-coordinator
                          6 deterministic consensus-100 concepts (never in
                          the fresh sample, never in the pilot): gen mol
                          cells, expand, prep, judge F1/F2/F3, agreement
                          report. Pre-freeze ONLY (rubric edits allowed only
                          before freeze; DESIGN-v2 §3.3).
  freeze                  writes FREEZE-v2.json (DESIGN-v2 §7) pinning
                          lexiconSetHash, prompts, expander code, the fresh
                          sample, rules and stats; every later stage-1/3 verb
                          verifies the pins and dies on mismatch.
  gen --stage 1|3         stage 1 (pilot n=24): mol cells fresh, flat cells
                          reuse consensus-100 (disclosed, Sol-permitted).
                          stage 3 (main n=200): all FOUR cells fresh,
                          per-concept INTERLEAVED inner loop over
                          flat-luna/flat-fable/mol-luna/mol-fable, matched
                          attempt budgets (identical pinned runner).
  expand --stage 1|3      deterministic recursive memoised ConceptRef ->
                          subExplication inliner (fail-closed: unresolved id,
                          cycle, depth>6); ids/labels/notes/references
                          stripped; flat records byte-identical; sha256s to
                          expanded-manifest.json (DESIGN-v2 §3.1).
  prep --stage 1|3 --instrument fidelity|conditional
                          ONE blind judge-input file per candidate
                          (judge-inputs-<instrument>/<blindid>.txt, seeded
                          6-hex blind ids, seeded global queue order, key
                          held back in judge-key-v2.json). fidelity = header
                          + expanded rendering; conditional = header + raw
                          AST + REFERENCED CONCEPTS gloss block, ref-bearing
                          mol cells only (DESIGN-v2 §3.2).
  judge --stage 1|3 --instrument fidelity|conditional --judge F1|F2|F3
        --i-am-the-coordinator
                          single-candidate blind judging over the queue order
                          (F1 gpt-5.6-sol annotator-proxy, F2 claude-opus-4-8,
                          F3 gpt-5.6-terra on F1/F2 disagreement only);
                          resumable per blindid; same judge_one plumbing.
  score --stage 1|3 --v2  ITT per-cell verdicts (gate-fail/missing/unjudged
                          => NOT-FAITHFUL, counts reported) -> Flat-E2/Mol-E2
                          -> exact McNemar + Tango(1998) score 95% CI;
                          PROXY-PASS = p<.05 & delta>0 & delta>=+15pp (stage
                          3); pilot futility gate (stage 1: STOP iff
                          Mol-E2-Flat-E2 <= 0pp OR mol zero-ref share >= 0.8);
                          cascade + per-generator secondaries; kappa + Gwet
                          AC1 + seeded bootstrap CIs; conditional-vs-expanded
                          credit gap; human-rejudge kit (stage 3).

Fail-closed everywhere; provenance (prompt hashes + lexiconSetHash) embedded
in every gen manifest. Costs are whatever define_concept.py reports.
"""
import argparse
import hashlib
import json
import math
import pathlib
import statistics
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
SCALE = HERE.parent
AST = SCALE / "ast-pipeline"
CDA = SCALE / "concept-def-agent"
C100 = SCALE / "consensus-100"
LEX = HERE / "lexicon"
RUN = HERE / "s5-run"
POOL = SCALE / "f1k-eligibility/candidate-pool.json"
sys.path.insert(0, str(CDA))
sys.path.insert(0, str(AST))
import define_concept as dc  # noqa: E402  (pinned runner; reused, not modified)
import run_pipeline as rp    # noqa: E402  (ast-pipeline harness; reused, not modified)

LUNA, FABLE = "gpt-5.6-luna", "claude-fable-5"
GEN_MODELS = [LUNA, FABLE]
DEFAULT_SEED = 34
HELD_OUT_N = 30
GO_THRESHOLD_PP = 15.0  # STIPULATED (DESIGN §7.2; v1 pilot rule, superseded by v2 futility gate)

# ---- v2 campaign constants (DESIGN-v2.md; all STIPULATED there) --------------
V2_JUDGES = {"F1": "gpt-5.6-sol",      # annotator-proxy leg (DESIGN-v2 §3.3)
             "F2": "claude-opus-4-8",  # cross-vendor leg
             "F3": "gpt-5.6-terra"}    # adjudicator, F1/F2 disagreements only
CELLS = ("flat-luna", "flat-fable", "mol-luna", "mol-fable")  # DESIGN-v2 §2
CELL_MODEL = {"flat-luna": LUNA, "flat-fable": FABLE,
              "mol-luna": LUNA, "mol-fable": FABLE}
FRESH_N = 200            # DESIGN-v2 §5 (frozen)
CALIB_N = 6              # DESIGN-v2 §3.3
MCID = 0.15              # DESIGN-v2 §2 (MATERIAL iff delta >= +15pp)
FUTILITY_ZERO_REF_SHARE = 0.8  # DESIGN-v2 §5 pilot gate (b)
MAX_EXPAND_DEPTH = 6     # DESIGN-v2 §9.3 (fail closed beyond)
Z95 = 1.959963984540054
STAGE_DIR_NAMES = {0: "calibration", 1: "stage1", 2: "stage2", 3: "stage3"}
BRIDGE_STATUS = "provisional/model-authored (proxy-adjudicated)"  # DESIGN-v2 §4.2
INSTRUMENTS = ("fidelity", "conditional")
# Verified freeze pins (DESIGN-v2 §7): any mismatch => the run is exploratory.
VERIFIED_PINS = ("lexiconSetHash", "encoderContentHash", "s5_prompt_sha256",
                 "s5_judge_fidelity_sha256", "s5_judge_conditional_sha256",
                 "bridge_rubric_sha256", "expander_sha256", "fresh_sample_sha256")
# Single-candidate note appended to the composed CONDITIONAL prompt
# (DESIGN-v2 §3.2: v1 gloss-credit protocol, single-candidate delivery).
SINGLE_CAND_NOTE = """
## Single-candidate protocol (S5-v2)

For this run you will receive exactly ONE candidate per request, labelled
`=== CANDIDATE A ===`, followed by its `REFERENCED CONCEPTS` block. Judge it
against the concept on its own merits; your `verdicts` array contains exactly
one entry, for "A". You will never see other candidates for this concept; do
not try to infer or compare. Requests are independent: no comparison, no
memory across requests. The verdict inventory, quality scale, and STRICT-JSON
output format are unchanged (with a single "A" entry).
"""


def sha256(s):
    return hashlib.sha256(s.encode("utf-8") if isinstance(s, str) else s).hexdigest()


def die(msg):
    sys.stderr.write("RUN_S5_ABORT: %s\n" % msg)
    sys.exit(2)


def load_manifest():
    p = LEX / "manifest.json"
    if not p.exists():
        die("lexicon/manifest.json missing -- run `node lexicon/build_manifest.mjs` first")
    return json.load(open(p))


def lexicon_glosses(manifest):
    """id -> (label, gloss) read from the record files the manifest pins."""
    root = HERE.parents[2]
    out = {}
    for r in manifest["records"]:
        d = json.load(open(root / r["file"]))
        out[r["id"]] = (d["label"], d["gloss"])
    return out


def stage_dir(stage):
    d = RUN / STAGE_DIR_NAMES.get(stage, "stage%d" % stage)
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---------------------------------------------------------------------------
# compose
# ---------------------------------------------------------------------------
def cmd_compose(_args):
    manifest = load_manifest()
    listing = (LEX / "listing.txt").read_text()
    if len(listing.strip().splitlines()) != manifest["conceptCount"]:
        die("listing.txt lines != manifest conceptCount (regenerate via build_manifest.mjs)")
    base = (CDA / "concept-def-prompt.md").read_text()
    ref_add = (HERE / "ref-addendum.md").read_text()
    s5 = base + "\n" + ref_add + "\n### LEXICON LISTING\n\n" + listing
    # v2 instruments (DESIGN-v2 §3.2): PRIMARY fidelity = base + addendum-v2
    # (single-candidate, expanded rendering); SECONDARY conditional = base +
    # v1 gloss-credit addendum + single-candidate note.
    jbase = (AST / "judge_prompt.md").read_text()
    jadd = (HERE / "judge-addendum.md").read_text()
    jadd2 = (HERE / "judge-addendum-v2.md").read_text()
    jfid = jbase + "\n" + jadd2
    jcond = jbase + "\n" + jadd + "\n" + SINGLE_CAND_NOTE
    fzp = HERE / "FREEZE-v2.json"
    if fzp.exists():  # post-freeze recompose must be a byte-identical no-op (§7)
        pins = json.load(open(fzp)).get("pins", {})
        for k, v in (("s5_prompt_sha256", s5), ("s5_judge_fidelity_sha256", jfid),
                     ("s5_judge_conditional_sha256", jcond)):
            if pins.get(k) != sha256(v):
                die("FREEZE-v2.json exists and recomposing would CHANGE %s -- "
                    "post-freeze prompt change makes the run exploratory "
                    "(DESIGN-v2 §7); refusing to overwrite" % k)
    (HERE / "s5-prompt.md").write_text(s5)
    (HERE / "s5-judge-prompt.md").write_text(jbase + "\n" + jadd)
    (HERE / "s5-judge-fidelity.md").write_text(jfid)
    (HERE / "s5-judge-conditional.md").write_text(jcond)
    out = {
        "s5_prompt_sha256": sha256(s5),
        "s5_judge_prompt_sha256": sha256(jbase + "\n" + jadd),
        "s5_judge_fidelity_sha256": sha256(jfid),
        "s5_judge_conditional_sha256": sha256(jcond),
        "base_prompt_sha256": sha256(base),
        "base_judge_prompt_sha256": sha256(jbase),
        "lexiconSetHash": manifest["lexiconSetHash"],
        "encoderContentHash": manifest["encoderContentHash"],
    }
    (HERE / "compose-manifest.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


# ---------------------------------------------------------------------------
# samples
# ---------------------------------------------------------------------------
def stage1_rows():
    p = AST / "sample.json"
    if not p.exists():
        die("ast-pipeline/sample.json missing (run run_pipeline.py sample)")
    return json.load(open(p))["concepts"]


def c100_rows():
    rows, flags = rp.load_rows(), rp.load_flags()
    out = []
    for c, r in rows.items():
        out.append({"concept": c, "bucket": rp.bucket_of(flags.get(c, {})),
                    "urn": r["urn"], "pos": r["pos"], "lemmas": r["lemmas"],
                    "wn31_gloss": r["wn31_gloss"],
                    "self_flags": {m: flags.get(c, {}).get(m) for m in rp.MODELS}})
    return sorted(out, key=lambda x: x["urn"])


def eligible_fresh(manifest, extra_excluded_urns=()):
    """Frozen eligibility rule (DESIGN §3.4 / DESIGN-v2 §4.3): candidate-pool
    sorted by URN byte order; drop consensus-100 URNs, any extra URNs, and any
    candidate ANY of whose lemma slugs matches a lexicon id slug (this
    mechanically excludes 'initiation', whose lemma list contains
    'institution')."""
    lex_slugs = {r["id"].split(":")[-1] for r in manifest["records"]}
    used_urns = {r["urn"] for r in c100_rows()} | set(extra_excluded_urns)
    pool = json.load(open(POOL))["candidates"]
    elig = []
    for x in sorted(pool, key=lambda r: r["urn"]):
        if x["urn"] in used_urns:
            continue
        concept = x["lemmas"][0]
        slugs = {dc.slugify(l) for l in x["lemmas"]} | {dc.slugify(concept)}
        if slugs & lex_slugs:
            continue  # lexicon collision (DESIGN §3.4, DESIGN-v2 §4.3)
        elig.append({"concept": concept, "bucket": "fresh", "urn": x["urn"],
                     "pos": x["pos"], "lemmas": x["lemmas"], "wn31_gloss": x["gloss"],
                     "self_flags": {}})
    return elig


def cmd_sample(args):
    manifest = load_manifest()
    if args.stage == 2:  # v1 held-out sampler -- superseded by v2, kept green
        elig = eligible_fresh(manifest)
        for r in elig:
            r["bucket"] = "held-out"
        n = len(elig)
        picked = [elig[(i * n) // HELD_OUT_N] for i in range(HELD_OUT_N)]
        out = {"built": "S5 stage-2 held-out sample (DESIGN §7.2; SUPERSEDED by DESIGN-v2)",
               "rule": ("candidate-pool.json sorted by URN byte order; exclude the 100 "
                        "consensus-100 URNs and any candidate with a lemma-slug in the "
                        "85-id lexicon; stride indices floor(i*n/%d)" % HELD_OUT_N),
               "lexiconSetHash": manifest["lexiconSetHash"],
               "n_eligible": n, "concepts": picked}
        RUN.mkdir(exist_ok=True)
        (RUN / "stage2-heldout.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
        print("wrote s5-run/stage2-heldout.json: %d concepts from %d eligible" % (len(picked), n))
        print("NOTE: stage 2 is SUPERSEDED by DESIGN-v2; the v2 campaign uses --stage 3.")
        return
    # --stage 3: the PRIMARY fresh sample (DESIGN-v2 §5, frozen rule)
    if (HERE / "FREEZE-v2.json").exists():
        die("FREEZE-v2.json exists -- the fresh sample is pinned; resampling "
            "post-freeze makes the run exploratory (DESIGN-v2 §7)")
    calib_urns, calib_note = [], "calibration sample not yet drawn (it is consensus-100-only, already excluded by URN)"
    cs = RUN / "calibration" / "calibration-sample.json"
    if cs.exists():
        calib_urns = [r["urn"] for r in json.load(open(cs))["concepts"]]
        calib_note = "calibration URNs explicitly excluded (all are consensus-100 members)"
    elig = eligible_fresh(manifest, extra_excluded_urns=calib_urns)
    n = len(elig)
    if n < FRESH_N:
        die("only %d eligible candidates < n=%d" % (n, FRESH_N))
    picked = [elig[(i * n) // FRESH_N] for i in range(FRESH_N)]
    if len({r["urn"] for r in picked}) != FRESH_N:
        die("stride produced duplicate URNs -- eligibility pool too small")
    out = {"built": "S5-v2 stage-3 fresh PRIMARY sample (DESIGN-v2 §5; prospectively frozen)",
           "rule": ("f1k-eligibility/candidate-pool.json sorted by URN byte order; "
                    "exclude consensus-100 URNs (which subsumes the 6 calibration "
                    "concepts), and any candidate ANY of whose lemma slugs matches "
                    "any of the 85 lexicon id slugs (DESIGN-v2 §4.3 frozen collision "
                    "rule -- mechanically excludes 'initiation' via its lemma "
                    "'institution'); stride indices floor(i*n_elig/%d); %s"
                    % (FRESH_N, calib_note)),
           "lexiconSetHash": manifest["lexiconSetHash"],
           "n_eligible": n, "n": FRESH_N, "concepts": picked}
    RUN.mkdir(exist_ok=True)
    (RUN / "stage3-fresh.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print("wrote s5-run/stage3-fresh.json: %d concepts from %d eligible" % (len(picked), n))
    print("NOTE: re-run `node lexicon/build_manifest.mjs` so the anti-leakage gate "
          "also covers the fresh sample (DESIGN-v2 §4.3), then `run_s5.py freeze` "
          "pins this file.")


def stage2_rows():
    ho = RUN / "stage2-heldout.json"
    if not ho.exists():
        die("s5-run/stage2-heldout.json missing (run: run_s5.py sample --stage 2)")
    return c100_rows(), json.load(open(ho))["concepts"]


def stage3_rows():
    p = RUN / "stage3-fresh.json"
    if not p.exists():
        die("s5-run/stage3-fresh.json missing (run: run_s5.py sample --stage 3)")
    return json.load(open(p))["concepts"]


def rows_for_stage(stage):
    if stage == 0:
        p = stage_dir(0) / "calibration-sample.json"
        if not p.exists():
            die("calibration sample missing (run: run_s5.py calibrate --i-am-the-coordinator)")
        return json.load(open(p))["concepts"]
    if stage == 1:
        return stage1_rows()
    if stage == 3:
        return stage3_rows()
    die("v2 verbs support stages 0 (calibration), 1 (pilot) and 3 (fresh main) only")


# ---------------------------------------------------------------------------
# gen -- S5 arm (+ fresh flat arms for held-out); post-gated by the variant gate
# ---------------------------------------------------------------------------
def s5_gate(record_path, row):
    """validate-record-ref.mjs + pinned mechanical checks minus the flat-only
    'references must be []' rule (DESIGN §5.1-5.2). Returns the s5gate dict."""
    p = subprocess.run(["node", str(HERE / "validate-record-ref.mjs"), str(record_path)],
                       capture_output=True, text=True)
    try:
        gate = json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:
        gate = {"ok": False, "code": "ERR_GATE_CRASH", "error": (p.stderr or p.stdout)[-500:]}
    obj = json.load(open(record_path))
    errs, warns, adequacy = dc.check_record(obj, row["concept"], row["urn"], row["wn31_gloss"])
    errs = [e for e in errs if e != "references must be []"]  # S5 override (§5.2 R2)
    return {"gate": gate, "mechanical_check_errors": errs, "warnings": warns,
            "ast_adequacy_self_flag": adequacy,
            "references": obj.get("references"),
            "s5_ok": bool(gate.get("ok")) and not errs}


def gen_arm(rows, prompt_path, outdir, models, arm):
    results = {}
    for row in rows:
        for m in models:
            r = rp.run_define(row, m, prompt_path, outdir)
            slug = dc.slugify(row["concept"])
            rec = outdir / ("%s.%s.json" % (slug, dc.MODEL_SHORT[m]))
            if arm == "s5" and rec.exists():
                gpath = outdir / ("%s.%s.s5gate.json" % (slug, dc.MODEL_SHORT[m]))
                g = s5_gate(rec, row)
                gpath.write_text(json.dumps(g, indent=2, ensure_ascii=False) + "\n")
                r = dict(r, s5_ok=g["s5_ok"],
                         gate_code=g["gate"].get("code"),
                         n_refs=len(g.get("references") or []))
            results["%s|%s" % (row["concept"], m)] = r
    return results


def gen_cells_interleaved(rows, base, sp):
    """DESIGN-v2 §2: per-concept INNER loop over the 4 matched cells, all fresh,
    so arms share the generation period; identical pinned runner and attempt
    budget both arms (only the system prompt + post-gate differ)."""
    flat_prompt = CDA / "concept-def-prompt.md"
    results = {}
    for row in rows:
        slug = dc.slugify(row["concept"])
        for cell in CELLS:
            m = CELL_MODEL[cell]
            if cell.startswith("flat-"):
                r = rp.run_define(row, m, flat_prompt, base / "gen-flat-fresh")
            else:
                r = rp.run_define(row, m, sp, base / "gen-s5-fresh")
                rec = base / "gen-s5-fresh" / ("%s.%s.json" % (slug, dc.MODEL_SHORT[m]))
                if rec.exists():
                    gpath = base / "gen-s5-fresh" / ("%s.%s.s5gate.json" % (slug, dc.MODEL_SHORT[m]))
                    if not gpath.exists() or not r.get("skipped"):
                        g = s5_gate(rec, row)
                        gpath.write_text(json.dumps(g, indent=2, ensure_ascii=False) + "\n")
                    g = json.load(open(gpath))
                    r = dict(r, s5_ok=g["s5_ok"], gate_code=g["gate"].get("code"),
                             n_refs=len(g.get("references") or []))
            results["%s|%s" % (row["concept"], cell)] = r
    return results


def cmd_gen(args):
    manifest = load_manifest()
    sp = HERE / "s5-prompt.md"
    if not sp.exists():
        die("s5-prompt.md missing (run: run_s5.py compose)")
    base = stage_dir(args.stage)
    man = {"stage": args.stage, "lexiconSetHash": manifest["lexiconSetHash"],
           "s5_prompt_sha256": sha256(sp.read_text()),
           "base_prompt_sha256": sha256((CDA / "concept-def-prompt.md").read_text()),
           "attempt_budget": {"MAX_CONTENT": dc.MAX_CONTENT,
                              "note": "identical pinned runner + budget both arms (DESIGN-v2 §2)"}}
    if args.stage in (1, 3):  # v2 campaign stages run post-freeze only (§10)
        fz = verify_freeze()
        man["freeze_sha256"] = sha256(json.dumps(fz, sort_keys=True))
    if args.stage == 1:
        # v2 pilot (DESIGN-v2 §5): mol cells fresh (48 calls); flat cells reuse
        # the existing consensus-100 records (0 calls; budget mismatch DISCLOSED,
        # Sol-permitted for the exploratory pilot).
        rows = stage1_rows()
        man["s5"] = gen_arm(rows, sp, base / "gen-s5", GEN_MODELS, "s5")
    elif args.stage == 3:
        rows = stage3_rows()
        man["cells"] = gen_cells_interleaved(rows, base, sp)
    else:
        print("WARNING: stage 2 is SUPERSEDED by DESIGN-v2 and will not be scored "
              "by the v2 campaign (kept only for v1 compatibility).")
        insample, heldout = stage2_rows()
        man["s5_insample"] = gen_arm(insample, sp, base / "gen-s5", GEN_MODELS, "s5")
        man["s5_heldout"] = gen_arm(heldout, sp, base / "gen-s5-heldout", GEN_MODELS, "s5")
        man["flat_heldout"] = gen_arm(heldout, CDA / "concept-def-prompt.md",
                                      base / "gen-flat-heldout", GEN_MODELS, "flat")
    (base / "gen-manifest.json").write_text(json.dumps(man, indent=2, ensure_ascii=False) + "\n")
    new = sum(1 for k, v in man.items() if isinstance(v, dict) and k.startswith(("s5", "flat", "cells"))
              for r in v.values() if isinstance(r, dict) and not r.get("skipped"))
    print("gen done (stage %d): %d call-slots processed this run; manifest -> %s"
          % (args.stage, new, base / "gen-manifest.json"))


# ---------------------------------------------------------------------------
# prep -- merged blind judge inputs (+ REFERENCED CONCEPTS block)
# ---------------------------------------------------------------------------
def s5_record(base, sub, row, model):
    slug = dc.slugify(row["concept"])
    rec = base / sub / ("%s.%s.json" % (slug, dc.MODEL_SHORT[model]))
    gp = base / sub / ("%s.%s.s5gate.json" % (slug, dc.MODEL_SHORT[model]))
    if rec.exists() and gp.exists() and json.load(open(gp)).get("s5_ok"):
        return rec
    return None


def flat_fresh_record(base, row, model):
    slug = dc.slugify(row["concept"])
    rec = base / "gen-flat-heldout" / ("%s.%s.json" % (slug, dc.MODEL_SHORT[model]))
    rep = base / "gen-flat-heldout" / ("%s.%s.report.json" % (slug, dc.MODEL_SHORT[model]))
    if rep.exists() and json.load(open(rep)).get("ok"):
        return rec
    return None


def pool_for(row, stage, base):
    """[(source, model, record_path)] -- flat arms + gate-clean S5 arms."""
    pool = []
    if row.get("bucket") == "held-out":
        for m in GEN_MODELS:
            rec = flat_fresh_record(base, row, m)
            if rec:
                pool.append(("flat-fresh", m, rec))
        sub = "gen-s5-heldout"
    elif stage == 1:
        pool.extend(rp.candidate_pool(row, rp.HERE))  # full ast-pipeline pool (§7.1)
        sub = "gen-s5"
    else:
        for m in GEN_MODELS:  # stage-2 in-sample: 2 flat + 2 S5 (§7.2)
            ok, rec, _ = rp.record_ok(row["concept"], m)
            if ok:
                pool.append(("consensus", m, rec))
        sub = "gen-s5"
    for m in GEN_MODELS:
        rec = s5_record(base, sub, row, m)
        if rec:
            pool.append(("s5", m, rec))
    return pool


def cmd_prep(args):
    manifest = load_manifest()
    glosses = lexicon_glosses(manifest)
    base = stage_dir(args.stage)
    if args.stage == 1:
        rows = stage1_rows()
    else:
        insample, heldout = stage2_rows()
        rows = insample + heldout
    seed = args.seed
    jdir = base / "judge-inputs"
    jdir.mkdir(parents=True, exist_ok=True)
    key, cands, strategies = {}, {"seed": seed, "lexiconSetHash": manifest["lexiconSetHash"],
                                  "concepts": {}}, {}
    for row in rows:
        c = row["concept"]
        slug = dc.slugify(c)
        pool = pool_for(row, args.stage, base)
        uniq, by_ast, membership, refs_union = [], {}, {}, set()
        for src, m, rec in pool:
            doc = json.load(open(rec))
            refs_union.update(doc.get("references") or [])
            ast = json.dumps(doc["explication"], sort_keys=True, separators=(",", ":"))
            h = sha256(ast)
            if h not in by_ast:
                by_ast[h] = len(uniq)
                uniq.append((src, m, rec, h))
            membership[(src, m)] = h
        order = sorted(uniq, key=lambda t: sha256("%s|%s|%s" % (seed, slug, t[3])))
        letters = {h: chr(ord("A") + i) for i, (_s, _m, _r, h) in enumerate(order)}
        key[slug] = {letters[h]: {"source": s, "model": m, "record": str(r),
                                  "explication_sha256": h}
                     for s, m, r, h in order}
        letter_of = {sm: letters[h] for sm, h in membership.items()}
        lines = ["concept: %s" % c, "synset: %s" % row["urn"], "pos: %s" % row["pos"],
                 "lemmas: %s" % ", ".join(row["lemmas"]),
                 "wn31-gloss (sense-fixing only): %s" % row["wn31_gloss"], ""]
        for _s, _m, rec, h in order:
            lines.append("=== CANDIDATE %s ===" % letters[h])
            lines.append(json.dumps(json.load(open(rec))["explication"],
                                    indent=1, ensure_ascii=False))
            lines.append("")
        if refs_union:  # per-concept REFERENCED CONCEPTS block (DESIGN §6)
            lines.append("=== REFERENCED CONCEPTS ===")
            for rid in sorted(refs_union):
                if rid not in glosses:
                    die("%s: candidate references %r which is not in the pinned lexicon" % (c, rid))
                lines.append("%s — %s: %s" % (rid, glosses[rid][0], glosses[rid][1]))
            lines.append("")
        (jdir / (slug + ".txt")).write_text("\n".join(lines))
        flat_luna = ("consensus", LUNA) if row.get("bucket") != "held-out" else ("flat-fresh", LUNA)
        flat_fable = ("consensus", FABLE) if row.get("bucket") != "held-out" else ("flat-fresh", FABLE)
        strategies[slug] = {
            "concept": c, "bucket": row.get("bucket"),
            "FLAT-luna": {"letter": letter_of.get(flat_luna, "GATE-FAIL")},
            "FLAT-fable": {"letter": letter_of.get(flat_fable, "GATE-FAIL")},
            "S5-luna": {"letter": letter_of.get(("s5", LUNA), "GATE-FAIL"), "new_calls": 1},
            "S5-fable": {"letter": letter_of.get(("s5", FABLE), "GATE-FAIL"), "new_calls": 1}}
        cands["concepts"][slug] = {"concept": c, "n_pool": len(pool),
                                   "n_unique": len(uniq),
                                   "referenced_ids": sorted(refs_union),
                                   "letters": sorted(key[slug])}
    (base / "judge-key.json").write_text(json.dumps(key, indent=2) + "\n")
    (base / "candidates.json").write_text(json.dumps(cands, indent=2) + "\n")
    (base / "strategies.json").write_text(json.dumps(strategies, indent=2) + "\n")
    print("prep done (stage %d): %d concepts -> %s (judge-key held back from judges)"
          % (args.stage, len(strategies), jdir))


# ---------------------------------------------------------------------------
# judge -- coordinator-run, COMPOSED variant prompt, same judge_one code path
# ---------------------------------------------------------------------------
def cmd_judge(args):
    if not args.i_am_the_coordinator:
        sys.exit("REFUSING: judging is coordinator-run (builder/judge separation; "
                 "ast-pipeline DESIGN §5). Re-run with --i-am-the-coordinator.")
    jp = HERE / "s5-judge-prompt.md"
    if not jp.exists():
        die("s5-judge-prompt.md missing (run: run_s5.py compose)")
    base = stage_dir(args.stage)
    model = rp.JUDGES[args.judge]
    jdir = base / "judgments" / args.judge
    jdir.mkdir(parents=True, exist_ok=True)
    sys_prompt = jp.read_text()
    slugs = sorted(p.stem for p in (base / "judge-inputs").glob("*.txt"))
    if args.judge == "T":
        slugs = rp.disagreement_slugs(base)
        print("tie-break judge T: %d concept(s) with A/B disagreement" % len(slugs))
    done = skipped = failed = 0
    for slug in slugs:
        if (jdir / (slug + ".json")).exists():
            skipped += 1
            continue
        user_msg = (base / "judge-inputs" / (slug + ".txt")).read_text()
        print("judge %s [%s] <- %s" % (args.judge, model, slug), flush=True)
        r = rp.judge_one(args.judge, model, slug, sys_prompt, user_msg, jdir)
        done += 1
        failed += 0 if r["ok"] else 1
    print("judge %s done: %d new, %d resumed, %d failed-structural" % (args.judge, done, skipped, failed))


# ---------------------------------------------------------------------------
# score -- paired stats (McNemar exact, Wilson CI) + secondaries + GO/NO-GO
# ---------------------------------------------------------------------------
def mcnemar_exact(b, c):
    """Two-sided exact binomial McNemar p over the discordant pairs."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / 2.0 ** n
    return min(1.0, 2.0 * tail)


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def cmd_score(args):
    base = stage_dir(args.stage)
    strategies = json.load(open(base / "strategies.json"))
    J = {j: {p.stem: json.load(open(p)) for p in (base / "judgments" / j).glob("*.json")}
         if (base / "judgments" / j).exists() else {} for j in "ABT"}

    def final(slug, L):
        a = J["A"].get(slug, {}).get("verdicts", {}).get(L)
        b = J["B"].get(slug, {}).get("verdicts", {}).get(L)
        if not a or not b:
            return None, None
        q = statistics.mean([a["quality"], b["quality"]])
        if a["verdict"] == b["verdict"]:
            return a["verdict"], q
        t = J["T"].get(slug, {}).get("verdicts", {}).get(L)
        if not t:
            return "UNRESOLVED", q
        votes = [a["verdict"], b["verdict"], t["verdict"]]
        return max(set(votes), key=votes.count), q

    res = {"stage": args.stage, "per_concept": {}, "paired": {}, "unresolved": []}
    gens = [("luna", "FLAT-luna", "S5-luna"), ("fable", "FLAT-fable", "S5-fable")]
    for slug, st in strategies.items():
        row = {"bucket": st.get("bucket")}
        for name in ("FLAT-luna", "FLAT-fable", "S5-luna", "S5-fable"):
            L = st[name]["letter"]
            if L == "GATE-FAIL":
                v, q = "GATE-FAIL", None
            else:
                v, q = final(slug, L)
                v = v or "UNJUDGED"
            if v in ("UNRESOLVED", "UNJUDGED"):
                res["unresolved"].append((slug, name, v))
            row[name] = {"letter": L, "verdict": v, "quality": q}
        res["per_concept"][slug] = row

    lines = ["# S5 results (stage %d, exploratory; n=%d concepts)" % (args.stage, len(strategies)), "",
             "| generator | flat FAITHFUL | S5 FAITHFUL | delta pp | discordant b/c | McNemar p | Wilson95(c/(b+c)) | mean q flat -> S5 |",
             "|---|---|---|---|---|---|---|---|"]
    go = False
    for gname, fk, sk in gens:
        n = fF = sF = b = c = 0
        qf, qs = [], []
        for slug, row in res["per_concept"].items():
            fv, sv = row[fk]["verdict"], row[sk]["verdict"]
            if fv in ("GATE-FAIL", "UNJUDGED", "UNRESOLVED") or sv in ("GATE-FAIL", "UNJUDGED", "UNRESOLVED"):
                continue  # GATE-FAIL counts as not-faithful only in the gate secondary; paired test needs both judged
            n += 1
            fF += fv == "FAITHFUL"
            sF += sv == "FAITHFUL"
            b += fv == "FAITHFUL" and sv == "LOSSY"
            c += sv == "FAITHFUL" and fv == "LOSSY"
            if row[fk]["quality"] is not None:
                qf.append(row[fk]["quality"])
            if row[sk]["quality"] is not None:
                qs.append(row[sk]["quality"])
        delta = 100.0 * (sF - fF) / n if n else 0.0
        p = mcnemar_exact(b, c)
        lo, hi = wilson(c, b + c)
        res["paired"][gname] = {"n_pairs": n, "flat_faithful": fF, "s5_faithful": sF,
                                "delta_pp": round(delta, 1), "discordant_flat_only": b,
                                "discordant_s5_only": c, "mcnemar_exact_p": round(p, 5),
                                "wilson95_c_over_discordant": [round(lo, 3), round(hi, 3)],
                                "mean_quality_flat": round(statistics.mean(qf), 2) if qf else None,
                                "mean_quality_s5": round(statistics.mean(qs), 2) if qs else None}
        go = go or delta >= GO_THRESHOLD_PP
        lines.append("| %s | %d/%d | %d/%d | %+.1f | %d/%d | %.4f | [%.2f, %.2f] | %s -> %s |"
                     % (gname, fF, n, sF, n, delta, b, c, p, lo, hi,
                        res["paired"][gname]["mean_quality_flat"],
                        res["paired"][gname]["mean_quality_s5"]))

    # secondaries: gate pass + reference usage from the S5 gen dirs
    gate_stats = {"s5_ok": 0, "s5_fail": 0, "err_codes": {}, "refs_per_record": [],
                  "zero_ref_share": None, "ref_id_histogram": {}}
    gate_files = sorted({p for d in base.glob("gen-s5*") for p in d.rglob("*.s5gate.json")})
    for gp in gate_files:
        g = json.load(open(gp))
        if g.get("s5_ok"):
            gate_stats["s5_ok"] += 1
        else:
            gate_stats["s5_fail"] += 1
            code = (g.get("gate") or {}).get("code") or "MECHANICAL"
            gate_stats["err_codes"][code] = gate_stats["err_codes"].get(code, 0) + 1
        refs = g.get("references") or []
        gate_stats["refs_per_record"].append(len(refs))
        for r in refs:
            gate_stats["ref_id_histogram"][r] = gate_stats["ref_id_histogram"].get(r, 0) + 1
    if gate_stats["refs_per_record"]:
        rr = gate_stats["refs_per_record"]
        gate_stats["zero_ref_share"] = round(sum(1 for x in rr if x == 0) / len(rr), 3)
        gate_stats["mean_refs_per_record"] = round(statistics.mean(rr), 2)
    res["gate_and_reference_usage"] = gate_stats
    if args.stage == 1:
        res["go_no_go"] = {"threshold_pp": GO_THRESHOLD_PP, "GO": go,
                           "rule": "GO iff pilot delta >= +15pp judged-FAITHFUL on either generator (STIPULATED, DESIGN §7.2)"}
        lines += ["", "**Stage-1 %s** (threshold %+.0fpp on either generator; n=24 pilot is directional only, ±10pp noise)"
                  % ("GO" if go else "NO-GO", GO_THRESHOLD_PP)]
    if gate_stats["refs_per_record"]:
        lines += ["", "reference usage: mean %.2f refs/record, zero-ref share %s; gate %d ok / %d fail %s"
                  % (gate_stats["mean_refs_per_record"], gate_stats["zero_ref_share"],
                     gate_stats["s5_ok"], gate_stats["s5_fail"], gate_stats["err_codes"] or "")]
    if res["unresolved"]:
        lines += ["", "WARNING: %d unresolved/unjudged/gate-fail cells excluded from pairing -- run missing judges or inspect gate" % len(res["unresolved"])]
    (base / "results-s5.json").write_text(json.dumps(res, indent=2) + "\n")
    (base / "results-s5.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


# ===========================================================================
# v2 (DESIGN-v2.md) -- expander, single-candidate blind prep/judge, E2 scoring,
# lexicon adjudication, calibration, freeze. Everything below fails closed.
# ===========================================================================

# ---------------------------------------------------------------------------
# v2: arm-neutral recursive expander (DESIGN-v2 §3.1 / §9.3)
# ---------------------------------------------------------------------------
class ExpandError(Exception):
    def __init__(self, code, detail=""):
        super().__init__("%s: %s" % (code, detail))
        self.code = code
        self.detail = detail


def load_lexicon_docs(manifest):
    """id -> full pinned record doc for every lexicon record."""
    root = HERE.parents[2]
    return {r["id"]: json.load(open(root / r["file"])) for r in manifest["records"]}


def _blk_depth(node):
    """Max subExplication nesting depth contained in (and including) node."""
    if isinstance(node, dict):
        d = max([_blk_depth(v) for v in node.values()] or [0])
        return d + (1 if node.get("kind") == "subExplication" else 0)
    if isinstance(node, list):
        return max([_blk_depth(x) for x in node] or [0])
    return 0


def expand_ast(doc, lex_docs, max_depth=MAX_EXPAND_DEPTH):
    """DESIGN-v2 §3.1: rewrite doc's explication so every ConceptRef /
    ConceptHead node ({"kind":"concept"|"conceptHead","id":...}) is replaced by
    a self-contained {"kind":"subExplication",frame,referents,clauses} block
    holding the referenced record's explication, RECURSIVELY, memoised,
    fail-closed on unresolved ids, cycles, and nesting depth > max_depth
    (mirrors encodeConceptSet resolution semantics: the rendering shows what is
    actually encoded, not the gloss). All ids/labels/notes/references/self-flags
    are stripped by construction (only frame/referents/clauses are copied).
    Records with no concept nodes pass through structurally identical, so their
    serialization is byte-identical."""
    memo = {}

    def walk(node, stack, depth):
        if isinstance(node, list):
            return [walk(x, stack, depth) for x in node]
        if isinstance(node, dict):
            if node.get("kind") in ("concept", "conceptHead") and "id" in node:
                return sub_block(node["id"], stack, depth + 1)
            return {k: walk(v, stack, depth) for k, v in node.items()}
        return node

    def sub_block(cid, stack, depth):
        if cid in stack:
            raise ExpandError("ERR_CYCLIC_CONCEPT_REF", cid)
        if depth > max_depth:
            raise ExpandError("ERR_EXPAND_DEPTH", "%s at depth %d > %d" % (cid, depth, max_depth))
        if cid in memo:
            blk, bd = memo[cid]
            if depth - 1 + bd > max_depth:
                raise ExpandError("ERR_EXPAND_DEPTH", "%s (memoised block depth %d at level %d)"
                                  % (cid, bd, depth))
            return json.loads(json.dumps(blk))  # deep copy, key order preserved
        tgt = lex_docs.get(cid)
        if tgt is None:
            raise ExpandError("ERR_CONCEPT_UNRESOLVED", cid)
        ex = tgt["explication"]
        nstack = stack | {cid}
        blk = {"kind": "subExplication",
               "frame": walk(ex["frame"], nstack, depth),
               "referents": walk(ex["referents"], nstack, depth),
               "clauses": walk(ex["clauses"], nstack, depth)}
        memo[cid] = (blk, _blk_depth(blk))
        return json.loads(json.dumps(blk))

    ex = doc["explication"]
    return {k: walk(v, frozenset(), 0) for k, v in ex.items()}


def rendering_text(exp):
    """Byte-stable serialization (same params as every judge-input AST dump)."""
    return json.dumps(exp, indent=1, ensure_ascii=False)


# ---------------------------------------------------------------------------
# v2: per-cell record resolution (ITT: a None here counts NOT-FAITHFUL, §2)
# ---------------------------------------------------------------------------
def cell_record_path(stage, base, row, cell):
    """Gate-clean record path for one cell, or None (ITT gate-fail)."""
    m = CELL_MODEL[cell]
    if cell.startswith("mol-"):
        sub = "gen-s5-fresh" if stage == 3 else "gen-s5"
        return s5_record(base, sub, row, m)
    if stage == 3:
        ok, rec, _ = rp.record_ok(row["concept"], m, base=base, sub="gen-flat-fresh")
        return rec if ok else None
    ok, rec, _ = rp.record_ok(row["concept"], m)  # pilot/calibration: consensus-100
    return rec if ok else None


def cell_self_flag(stage, base, row, cell):
    """Generator self-flag for the cascade secondary (DESIGN-v2 §2(a))."""
    m = CELL_MODEL[cell]
    slug = dc.slugify(row["concept"])
    if cell.startswith("mol-"):
        sub = "gen-s5-fresh" if stage == 3 else "gen-s5"
        gp = base / sub / ("%s.%s.s5gate.json" % (slug, dc.MODEL_SHORT[m]))
        return json.load(open(gp)).get("ast_adequacy_self_flag") if gp.exists() else None
    if stage == 3:
        _, _, rep = rp.record_ok(row["concept"], m, base=base, sub="gen-flat-fresh")
    else:
        _, _, rep = rp.record_ok(row["concept"], m)
    return (rep or {}).get("ast_adequacy_self_flag")


def expand_stage(stage, base, rows, manifest):
    """cmd_expand core: write expanded/<slug>.<cell>.json + expanded-manifest."""
    lex = load_lexicon_docs(manifest)
    edir = base / "expanded"
    edir.mkdir(parents=True, exist_ok=True)
    eman = {"stage": stage, "lexiconSetHash": manifest["lexiconSetHash"],
            "max_depth": MAX_EXPAND_DEPTH, "cells": {}}
    n_ok = n_fail = 0
    for row in rows:
        slug = dc.slugify(row["concept"])
        for cell in CELLS:
            keyname = "%s.%s" % (slug, cell)
            rec = cell_record_path(stage, base, row, cell)
            if rec is None:
                eman["cells"][keyname] = {"status": "GATE-FAIL"}
                n_fail += 1
                continue
            doc = json.load(open(rec))
            try:
                exp = expand_ast(doc, lex)
            except ExpandError as e:
                die("expand FAILED CLOSED for %s (%s): %s -- a gate-clean record "
                    "must expand; inspect the record/lexicon" % (keyname, rec, e))
            txt = rendering_text(exp)
            if cell.startswith("flat-"):
                raw = rendering_text(doc["explication"])
                if txt != raw:
                    die("flat record %s did NOT pass through byte-identically "
                        "(DESIGN-v2 §9.3) -- it contains concept nodes?" % keyname)
            (edir / (keyname + ".json")).write_text(txt + "\n")
            eman["cells"][keyname] = {
                "status": "ok", "record": str(rec),
                "rendering_sha256": sha256(txt),
                "n_refs": len(doc.get("references") or []),
                "self_flag": cell_self_flag(stage, base, row, cell)}
            n_ok += 1
    (base / "expanded-manifest.json").write_text(
        json.dumps(eman, indent=2, ensure_ascii=False) + "\n")
    return n_ok, n_fail


def cmd_expand(args):
    manifest = load_manifest()
    base = stage_dir(args.stage)
    if args.stage in (1, 3):
        verify_freeze()
    rows = rows_for_stage(args.stage)
    n_ok, n_fail = expand_stage(args.stage, base, rows, manifest)
    print("expand done (stage %d): %d renderings, %d ITT gate-fail cells -> %s"
          % (args.stage, n_ok, n_fail, base / "expanded-manifest.json"))


# ---------------------------------------------------------------------------
# v2: single-candidate blind prep (DESIGN-v2 §9.4)
# ---------------------------------------------------------------------------
def blind_id(seed, stage, instrument, slug, cell):
    """Seeded deterministic 6-hex blind id (candidate-label blinding, §3.1)."""
    return sha256("blind|%s|%s|%s|%s|%s" % (seed, stage, instrument, slug, cell))[:6]


def header_lines(row):
    return ["concept: %s" % row["concept"], "synset: %s" % row["urn"],
            "pos: %s" % row["pos"], "lemmas: %s" % ", ".join(row["lemmas"]),
            "wn31-gloss (sense-fixing only): %s" % row["wn31_gloss"], ""]


def prep_stage(stage, base, rows, manifest, seed, instrument):
    """cmd_prep core: ONE judge-input file per candidate; seeded queue order;
    blind key held back in judge-key-v2.json."""
    if instrument not in INSTRUMENTS:
        die("unknown instrument %r" % instrument)
    emanp = base / "expanded-manifest.json"
    if not emanp.exists():
        die("expanded-manifest.json missing (run: run_s5.py expand --stage %s)" % stage)
    eman = json.load(open(emanp))["cells"]
    glosses = lexicon_glosses(manifest)
    jdir = base / ("judge-inputs-%s" % instrument)
    jdir.mkdir(parents=True, exist_ok=True)
    key = {}
    for row in rows:
        slug = dc.slugify(row["concept"])
        for cell in CELLS:
            keyname = "%s.%s" % (slug, cell)
            ent = eman.get(keyname)
            if not ent or ent["status"] != "ok":
                continue
            if instrument == "conditional" and not (cell.startswith("mol-") and ent["n_refs"] > 0):
                continue  # conditional instrument: ref-bearing mol cells ONLY (§3.2)
            bid = blind_id(seed, stage, instrument, slug, cell)
            if bid in key:
                die("blind-id collision on %s (%s vs %s) -- change --seed" %
                    (bid, keyname, key[bid]["cell_key"]))
            if instrument == "fidelity":
                cand = (base / "expanded" / (keyname + ".json")).read_text().rstrip("\n")
                lines = header_lines(row) + ["=== CANDIDATE A ===", cand, ""]
            else:
                doc = json.load(open(ent["record"]))
                cand = rendering_text(doc["explication"])
                lines = header_lines(row) + ["=== CANDIDATE A ===", cand, ""]
                lines.append("=== REFERENCED CONCEPTS ===")
                for rid in sorted(doc.get("references") or []):
                    if rid not in glosses:
                        die("%s references %r not in the pinned lexicon" % (keyname, rid))
                    lines.append("%s — %s: %s" % (rid, glosses[rid][0], glosses[rid][1]))
                lines.append("")
            (jdir / (bid + ".txt")).write_text("\n".join(lines))
            key[bid] = {"slug": slug, "cell": cell, "cell_key": keyname,
                        "concept": row["concept"], "record": ent["record"],
                        "rendering_sha256": ent["rendering_sha256"],
                        "n_refs": ent["n_refs"]}
    queue = sorted(key, key=lambda b: sha256("queue|%s|%s" % (seed, b)))
    (base / ("queue-order-%s.json" % instrument)).write_text(json.dumps(queue, indent=2) + "\n")
    kp = base / "judge-key-v2.json"
    keyall = json.load(open(kp)) if kp.exists() else {"seed": seed}
    if keyall.get("seed") != seed:
        die("judge-key-v2.json seed %r != --seed %r (one seed per stage)" % (keyall.get("seed"), seed))
    keyall[instrument] = key
    kp.write_text(json.dumps(keyall, indent=2, ensure_ascii=False) + "\n")
    return len(key)


def cmd_prep_v2(args):
    manifest = load_manifest()
    base = stage_dir(args.stage)
    if args.stage in (1, 3):
        verify_freeze()
    rows = rows_for_stage(args.stage)
    n = prep_stage(args.stage, base, rows, manifest, args.seed, args.instrument)
    print("prep done (stage %d, %s): %d single-candidate blind inputs -> %s "
          "(judge-key-v2.json held back from judges)"
          % (args.stage, args.instrument, n, base / ("judge-inputs-%s" % args.instrument)))


# ---------------------------------------------------------------------------
# v2: judging (DESIGN-v2 §9.5) -- same judge_one plumbing, pool-of-one inputs
# ---------------------------------------------------------------------------
def v2_disagreements(jroot):
    """Blind-ids where F1 and F2 disagree on candidate A (or a leg failed)."""
    out = []
    for pa in sorted((jroot / "F1").glob("*.json")):
        pb = jroot / "F2" / pa.name
        if not pb.exists():
            continue
        a, b = json.load(open(pa)), json.load(open(pb))
        if not (a.get("ok") and b.get("ok")):
            out.append(pa.stem)
            continue
        va = (a.get("verdicts") or {}).get("A", {}).get("verdict")
        vb = (b.get("verdicts") or {}).get("A", {}).get("verdict")
        if va != vb:
            out.append(pa.stem)
    return out


def judge_v2(base, stage, instrument, judge):
    prompt = HERE / ("s5-judge-%s.md" % instrument)
    if not prompt.exists():
        die("s5-judge-%s.md missing (run: run_s5.py compose --v2)" % instrument)
    qp = base / ("queue-order-%s.json" % instrument)
    if not qp.exists():
        die("queue order missing (run: run_s5.py prep --stage %s --instrument %s)"
            % (stage, instrument))
    model = V2_JUDGES[judge]
    jroot = base / ("judgments-%s" % instrument)
    jdir = jroot / judge
    jdir.mkdir(parents=True, exist_ok=True)
    queue = json.load(open(qp))
    if judge == "F3":
        queue = v2_disagreements(jroot)
        print("adjudicator F3: %d candidate(s) with F1/F2 disagreement" % len(queue))
    sys_prompt = prompt.read_text()
    done = skipped = failed = 0
    for bid in queue:
        if (jdir / (bid + ".json")).exists():
            skipped += 1
            continue
        user_msg = (base / ("judge-inputs-%s" % instrument) / (bid + ".txt")).read_text()
        print("judge %s [%s] <- %s/%s" % (judge, model, instrument, bid), flush=True)
        r = rp.judge_one(judge, model, bid, sys_prompt, user_msg, jdir)
        done += 1
        failed += 0 if r["ok"] else 1
    print("judge %s done (%s): %d new, %d resumed, %d failed-structural"
          % (judge, instrument, done, skipped, failed))


def cmd_judge_v2(args):
    if not args.i_am_the_coordinator:
        sys.exit("REFUSING: judging is coordinator-run (builder/judge separation). "
                 "Re-run with --i-am-the-coordinator.")
    base = stage_dir(args.stage)
    if args.stage in (1, 3):
        verify_freeze()
    judge_v2(base, args.stage, args.instrument, args.judge)


def final_v2(jroot, bid):
    """(final verdict, mean quality) for candidate A of one blind id:
    F1==F2 -> that verdict; else F3 majority; missing F3 -> UNRESOLVED."""
    def leg(j):
        p = jroot / j / (bid + ".json")
        if not p.exists():
            return None
        d = json.load(open(p))
        return (d.get("verdicts") or {}).get("A") if d.get("ok") else None
    a, b = leg("F1"), leg("F2")
    if not a or not b:
        return "UNJUDGED", None
    q = statistics.mean([a["quality"], b["quality"]])
    if a["verdict"] == b["verdict"]:
        return a["verdict"], q
    t = leg("F3")
    if not t:
        return "UNRESOLVED", q
    votes = [a["verdict"], b["verdict"], t["verdict"]]
    return max(set(votes), key=votes.count), q


# ---------------------------------------------------------------------------
# v2: stats -- Tango (1998) score CI, Cohen kappa, Gwet AC1, seeded bootstrap
# ---------------------------------------------------------------------------
def tango_z(b, c, n, d):
    """Tango (1998) score statistic for H0: delta = d, where delta is the
    paired risk difference p_mol - p_flat, b = flat-only-success discordant
    count, c = mol-only-success discordant count. Constrained MLE of the
    b-cell probability from the standard quadratic; at d=0 this reduces
    EXACTLY to the McNemar statistic (c-b)/sqrt(b+c) (checked in selftest)."""
    A = 2.0 * n
    B = -b - c + (2 * n - b + c) * d
    C = -b * d * (1.0 - d)
    disc = B * B - 4 * A * C
    p21 = (math.sqrt(max(disc, 0.0)) - B) / (2 * A)
    var = n * (2 * p21 + d * (1 - d))
    if var <= 0:
        var = 1e-12
    return (c - b - n * d) / math.sqrt(var)


def tango_ci(b, c, n, z=Z95):
    """Tango asymptotic score 95% CI for the paired difference (DESIGN-v2 §2;
    replaces v1's Wilson-on-discordant per readiness-review item 2)."""
    if n == 0:
        return (-1.0, 1.0)
    dhat = (c - b) / n

    def solve(target, lo, hi):
        for _ in range(200):
            mid = (lo + hi) / 2
            if tango_z(b, c, n, mid) > target:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    eps = 1e-12
    return (solve(z, -1 + eps, dhat), solve(-z, dhat, 1 - eps))


def agreement_stats(pairs):
    """pairs: [(bool_a, bool_b)] -> raw agreement, Cohen kappa, Gwet AC1."""
    n = len(pairs)
    if n == 0:
        return {"n": 0, "raw": None, "kappa": None, "ac1": None}
    po = sum(1 for a, b in pairs if a == b) / n
    pa = sum(1 for a, _ in pairs if a) / n
    pb = sum(1 for _, b in pairs if b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    kappa = (po - pe) / (1 - pe) if pe < 1 else None
    pi = (pa + pb) / 2
    peg = 2 * pi * (1 - pi)
    ac1 = (po - peg) / (1 - peg) if peg < 1 else None
    return {"n": n, "raw": round(po, 4),
            "kappa": round(kappa, 4) if kappa is not None else None,
            "ac1": round(ac1, 4) if ac1 is not None else None}


def bootstrap_ci(pairs, stat, seed, B=1000):
    """Seeded percentile bootstrap 95% CI for stat(pairs) (DESIGN-v2 §3.3)."""
    import random
    if not pairs:
        return None
    rng = random.Random("boot|%s" % seed)
    vals = []
    n = len(pairs)
    for _ in range(B):
        rs = [pairs[rng.randrange(n)] for _ in range(n)]
        v = agreement_stats(rs).get(stat)
        if v is not None:
            vals.append(v)
    if not vals:
        return None
    vals.sort()
    return [vals[int(0.025 * len(vals))], vals[min(len(vals) - 1, int(0.975 * len(vals)))]]


# ---------------------------------------------------------------------------
# v2: scoring (DESIGN-v2 §2 / §9.6) -- ITT, E2, McNemar+Tango, secondaries
# ---------------------------------------------------------------------------
def e2_of(cells):
    """(Flat-E2, Mol-E2) for one concept under ITT: only a judged FAITHFUL
    counts; GATE-FAIL/UNJUDGED/UNRESOLVED/LOSSY are all NOT-FAITHFUL."""
    flat = any(cells[c]["verdict"] == "FAITHFUL" for c in ("flat-luna", "flat-fable"))
    mol = any(cells[c]["verdict"] == "FAITHFUL" for c in ("mol-luna", "mol-fable"))
    return flat, mol


def paired_counts(pairs):
    """pairs: [(flat_bool, mol_bool)] -> (b = flat-only, c = mol-only, n)."""
    b = sum(1 for f, m in pairs if f and not m)
    c = sum(1 for f, m in pairs if m and not f)
    return b, c, len(pairs)


def cascade_pick(cells, arm):
    """Frozen S1-mirror selector (DESIGN-v2 §2(a)): take the Luna cell if it
    gate-passed AND self-flags faithful, else the Fable cell."""
    lc = cells["%s-luna" % arm]
    if lc["verdict"] != "GATE-FAIL" and lc.get("self_flag") == "faithful":
        return "%s-luna" % arm
    return "%s-fable" % arm


def paired_block(pairs):
    b, c, n = paired_counts(pairs)
    delta = (c - b) / n if n else 0.0
    lo, hi = tango_ci(b, c, n)
    return {"n": n, "b_flat_only": b, "c_mol_only": c,
            "delta": round(delta, 4), "delta_pp": round(100 * delta, 1),
            "mcnemar_exact_p": round(mcnemar_exact(b, c), 6),
            "tango95_ci": [round(lo, 4), round(hi, 4)],
            "tango95_ci_pp": [round(100 * lo, 1), round(100 * hi, 1)]}


def cmd_score_v2(args):
    base = stage_dir(args.stage)
    if args.stage in (1, 3):
        verify_freeze()
    rows = rows_for_stage(args.stage)
    eman = json.load(open(base / "expanded-manifest.json"))["cells"]
    keyall = json.load(open(base / "judge-key-v2.json"))
    fkey = keyall.get("fidelity") or die("no fidelity key in judge-key-v2.json (run prep)")
    seed = keyall.get("seed", DEFAULT_SEED)
    bid_of = {(v["slug"], v["cell"]): k for k, v in fkey.items()}
    jroot = base / "judgments-fidelity"

    itt_counts = {"GATE-FAIL": 0, "UNJUDGED": 0, "UNRESOLVED": 0}
    per = {}
    for row in rows:
        slug = dc.slugify(row["concept"])
        cells = {}
        for cell in CELLS:
            ent = eman.get("%s.%s" % (slug, cell)) or {"status": "GATE-FAIL"}
            if ent["status"] != "ok":
                v, q = "GATE-FAIL", None
            else:
                bid = bid_of.get((slug, cell))
                v, q = final_v2(jroot, bid) if bid else ("UNJUDGED", None)
            if v in itt_counts:
                itt_counts[v] += 1
            cells[cell] = {"verdict": v, "quality": q,
                           "n_refs": ent.get("n_refs"), "self_flag": ent.get("self_flag")}
        per[slug] = cells

    # -- PRIMARY: paired ensemble E2 (ITT; every concept analyzable, §2) --
    e2 = [e2_of(c) for c in per.values()]
    primary = paired_block(e2)
    primary["flat_e2"] = sum(1 for f, _ in e2 if f)
    primary["mol_e2"] = sum(1 for _, m in e2 if m)

    # -- secondaries (nominal p-values, no multiplicity claim, §2) --
    cascade = [(per[s][cascade_pick(per[s], "flat")]["verdict"] == "FAITHFUL",
                per[s][cascade_pick(per[s], "mol")]["verdict"] == "FAITHFUL") for s in per]
    per_gen = {}
    for gname, fcell, mcell in (("luna", "flat-luna", "mol-luna"),
                                ("fable", "flat-fable", "mol-fable")):
        per_gen[gname] = paired_block([(per[s][fcell]["verdict"] == "FAITHFUL",
                                        per[s][mcell]["verdict"] == "FAITHFUL") for s in per])
    q_arm, sf_lossy = {}, {}
    for arm, arm_cells in (("flat", ("flat-luna", "flat-fable")),
                           ("mol", ("mol-luna", "mol-fable"))):
        qs = [per[s][c]["quality"] for s in per for c in arm_cells
              if per[s][c]["quality"] is not None]
        q_arm[arm] = round(statistics.mean(qs), 3) if qs else None
        fl = [per[s][c]["self_flag"] for s in per for c in arm_cells
              if per[s][c]["self_flag"] is not None]
        sf_lossy[arm] = round(sum(1 for x in fl if x == "lossy") / len(fl), 3) if fl else None

    # -- gate + reference usage over the mol gen dirs (zero-ref share, §2(e)) --
    gate_stats = {"s5_ok": 0, "s5_fail": 0, "err_codes": {}, "refs_per_record": [],
                  "zero_ref_share": None, "ref_id_histogram": {}}
    for gp in sorted({p for d in base.glob("gen-s5*") for p in d.rglob("*.s5gate.json")}):
        g = json.load(open(gp))
        if g.get("s5_ok"):
            gate_stats["s5_ok"] += 1
        else:
            gate_stats["s5_fail"] += 1
            code = (g.get("gate") or {}).get("code") or "MECHANICAL"
            gate_stats["err_codes"][code] = gate_stats["err_codes"].get(code, 0) + 1
        refs = g.get("references") or []
        gate_stats["refs_per_record"].append(len(refs))
        for r in refs:
            gate_stats["ref_id_histogram"][r] = gate_stats["ref_id_histogram"].get(r, 0) + 1
    rr = gate_stats.pop("refs_per_record")
    if rr:
        gate_stats["zero_ref_share"] = round(sum(1 for x in rr if x == 0) / len(rr), 3)
        gate_stats["mean_refs_per_record"] = round(statistics.mean(rr), 2)

    # -- judge agreement: overall / by arm / by reference status (§3.3) --
    def f1f2_pairs(pred):
        out = []
        for bid, meta in fkey.items():
            if not pred(meta):
                continue
            pa, pb = jroot / "F1" / (bid + ".json"), jroot / "F2" / (bid + ".json")
            if not (pa.exists() and pb.exists()):
                continue
            a, b = json.load(open(pa)), json.load(open(pb))
            if not (a.get("ok") and b.get("ok")):
                continue
            out.append(((a["verdicts"].get("A") or {}).get("verdict") == "FAITHFUL",
                        (b["verdicts"].get("A") or {}).get("verdict") == "FAITHFUL"))
        return out

    agreement = {}
    for gname, pred in (("overall", lambda m: True),
                        ("arm_flat", lambda m: m["cell"].startswith("flat-")),
                        ("arm_mol", lambda m: m["cell"].startswith("mol-")),
                        ("ref_bearing", lambda m: m["n_refs"] > 0),
                        ("zero_ref", lambda m: m["n_refs"] == 0)):
        prs = f1f2_pairs(pred)
        st = agreement_stats(prs)
        st["kappa_boot95"] = bootstrap_ci(prs, "kappa", "%s|%s" % (seed, gname))
        st["ac1_boot95"] = bootstrap_ci(prs, "ac1", "%s|%s" % (seed, gname))
        agreement[gname] = st

    # -- conditional credit gap (§3.2: conditional-FAITHFUL & expanded-not) --
    ckey = keyall.get("conditional") or {}
    croot = base / "judgments-conditional"
    credit = {"n_conditional_judged": 0, "credit_gap": 0, "reverse_gap": 0, "items": []}
    for bid, meta in ckey.items():
        cv, _ = final_v2(croot, bid)
        if cv in ("UNJUDGED",):
            continue
        fv = per.get(meta["slug"], {}).get(meta["cell"], {}).get("verdict")
        credit["n_conditional_judged"] += 1
        if cv == "FAITHFUL" and fv != "FAITHFUL":
            credit["credit_gap"] += 1
            credit["items"].append({"slug": meta["slug"], "cell": meta["cell"],
                                    "conditional": cv, "expanded": fv})
        elif cv != "FAITHFUL" and fv == "FAITHFUL":
            credit["reverse_gap"] += 1

    res = {"stage": args.stage, "design": "DESIGN-v2.md §2 (PROXY-PROVISIONAL)",
           "n_concepts": len(per), "itt_cell_counts": itt_counts,
           "primary_e2": primary, "cascade_secondary": paired_block(cascade),
           "per_generator_secondary": per_gen,
           "mean_quality_by_arm": q_arm, "self_flag_lossy_share_by_arm": sf_lossy,
           "gate_and_reference_usage": gate_stats, "judge_agreement": agreement,
           "conditional_credit_gap": credit, "per_concept": per}

    lines = ["# S5-v2 results (stage %d; n=%d concepts; PROXY-PROVISIONAL -- DESIGN-v2 §6)"
             % (args.stage, len(per)), "",
             "| endpoint | Flat | Mol | delta pp | b/c | McNemar p | Tango95 pp |",
             "|---|---|---|---|---|---|---|",
             "| **E2 (PRIMARY)** | %d/%d | %d/%d | %+.1f | %d/%d | %.5f | [%+.1f, %+.1f] |"
             % (primary["flat_e2"], primary["n"], primary["mol_e2"], primary["n"],
                primary["delta_pp"], primary["b_flat_only"], primary["c_mol_only"],
                primary["mcnemar_exact_p"], *primary["tango95_ci_pp"])]
    for gname in ("luna", "fable"):
        g = per_gen[gname]
        lines.append("| %s (secondary) | - | - | %+.1f | %d/%d | %.5f | [%+.1f, %+.1f] |"
                     % (gname, g["delta_pp"], g["b_flat_only"], g["c_mol_only"],
                        g["mcnemar_exact_p"], *g["tango95_ci_pp"]))
    cc = res["cascade_secondary"]
    lines.append("| cascade (secondary) | - | - | %+.1f | %d/%d | %.5f | [%+.1f, %+.1f] |"
                 % (cc["delta_pp"], cc["b_flat_only"], cc["c_mol_only"],
                    cc["mcnemar_exact_p"], *cc["tango95_ci_pp"]))
    lines += ["", "ITT fail-closed cell counts (counted NOT-FAITHFUL): %s" % itt_counts,
              "zero-ref share (mol records): %s; gate %d ok / %d fail %s"
              % (gate_stats["zero_ref_share"], gate_stats["s5_ok"],
                 gate_stats["s5_fail"], gate_stats["err_codes"] or ""),
              "credit gap (conditional-FAITHFUL & expanded-not): %d/%d (reverse %d)"
              % (credit["credit_gap"], credit["n_conditional_judged"], credit["reverse_gap"]),
              "F1/F2 agreement overall: %s" % agreement["overall"]]

    if args.stage == 1:
        # Pilot futility gate (DESIGN-v2 §5, frozen): direction-only kill.
        zr = gate_stats["zero_ref_share"]
        stop_dir = primary["delta_pp"] <= 0.0
        stop_zr = zr is not None and zr >= FUTILITY_ZERO_REF_SHARE
        res["futility_gate"] = {
            "rule": ("STOP iff pilot Mol-E2 - Flat-E2 <= 0pp (direction-only kill) "
                     "OR mol-arm zero-ref share >= %.0f%% (uptake failure)"
                     % (100 * FUTILITY_ZERO_REF_SHARE)),
            "delta_pp": primary["delta_pp"], "zero_ref_share": zr,
            "STOP": bool(stop_dir or stop_zr),
            "verdict": "STOP" if (stop_dir or stop_zr) else "PROCEED to Step B (stage 3)"}
        lines += ["", "**PILOT FUTILITY GATE: %s** (delta %+.1fpp; zero-ref share %s; "
                  "n=24 is exploratory -- can kill, never confirm)"
                  % (res["futility_gate"]["verdict"], primary["delta_pp"], zr)]
    if args.stage == 3:
        significant = primary["mcnemar_exact_p"] < 0.05 and primary["delta"] > 0
        material = primary["delta"] >= MCID
        res["decision"] = {
            "rule": "PROXY-PASS = SIGNIFICANT (exact McNemar p<0.05 & delta>0) AND MATERIAL (delta >= +15pp MCID); frozen (DESIGN-v2 §2)",
            "significant": significant, "material": material,
            "verdict": ("PROXY-PASS" if (significant and material) else
                        "SIGNIFICANT-BUT-SUBMATERIAL" if significant else
                        "REVERSAL" if (primary["mcnemar_exact_p"] < 0.05 and primary["delta"] < 0)
                        else "PROXY-FAIL")}
        lines += ["", "**DECISION: %s** (PROXY-PROVISIONAL; what this does and does not "
                  "license: DESIGN-v2 §6 -- read it before quoting)" % res["decision"]["verdict"]]

    (base / "results-s5-v2.json").write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n")
    (base / "results-s5-v2.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    if args.stage == 3:
        write_rejudge_kit(base, res)


def write_rejudge_kit(base, res):
    """DESIGN-v2 §6: package the frozen artefacts as a human-adjudication kit
    (hashes + procedure; the blind key stays held back until human verdicts
    are in). Pure re-judging -- zero regeneration."""
    kit = base / "human-rejudge-kit"
    kit.mkdir(parents=True, exist_ok=True)
    entries = {}
    def add(p):
        rel = str(p.relative_to(base))
        entries[rel] = sha256(p.read_bytes())
    for name in ("expanded-manifest.json", "queue-order-fidelity.json", "results-s5-v2.json"):
        p = base / name
        if p.exists():
            add(p)
    for sub in ("expanded", "judge-inputs-fidelity"):
        for p in sorted((base / sub).glob("*")):
            add(p)
    for p in sorted((base / "judgments-fidelity").rglob("*.json")):
        add(p)
    sample = RUN / "stage3-fresh.json"
    if sample.exists():
        entries["../stage3-fresh.json"] = sha256(sample.read_bytes())
    (kit / "kit-manifest.json").write_text(json.dumps(
        {"built_from": "DESIGN-v2.md §6 upgrade path", "files": entries}, indent=2) + "\n")
    (kit / "README.md").write_text("""# Human re-judge kit (S5-v2, stage 3)

Every proxy verdict in results-s5-v2.json is PROXY-PROVISIONAL (DESIGN-v2 §6).
To UPGRADE this run to confirmatory WITHOUT regenerating anything, two human
fidelity judges independently re-judge the SAME frozen inputs:

1. Instrument: s5-judge-fidelity.md (frozen; sha in FREEZE-v2.json), one
   candidate per sitting, in the order of queue-order-fidelity.json.
2. Inputs: judge-inputs-fidelity/<blindid>.txt (arm-neutral expanded
   renderings; candidate-label blind). Verdict format: the STRICT-JSON single
   "A" entry of the base rubric.
3. The blind key (judge-key-v2.json, one directory up) stays HELD BACK until
   both humans finish; a human adjudicator resolves disagreements.
4. Scoring re-runs `run_s5.py score --stage 3 --v2` semantics over the human
   verdict files (drop-in replacement for judgments-fidelity/F1,F2,F3).

kit-manifest.json pins the sha256 of every artefact this kit refers to.
""")
    print("human-rejudge kit -> %s (%d artefacts pinned)" % (kit, len(entries)))


# ---------------------------------------------------------------------------
# v2: bridge-lexicon adjudication (DESIGN-v2 §4 / §9.7)
# ---------------------------------------------------------------------------
ADJ = LEX / "adjudication"
ADJ_VERDICTS = ("ACCEPT", "REPAIR", "REJECT")
ADJ_BOOLS = ("gloss_scholarly", "explication_carries_gloss",
             "self_flag_correct", "sense_collision_free")


def bridge_closure(manifest):
    """All 31 bridge ids + every kernel-v0 record in their reference closure."""
    recs = {r["id"]: r for r in manifest["records"]}
    todo = sorted(r["id"] for r in manifest["records"] if r["tier"] == "molaug-v0")
    seen = set()
    while todo:
        rid = todo.pop()
        if rid in seen:
            continue
        seen.add(rid)
        todo.extend(recs[rid]["references"])
    return sorted(seen), recs


def adj_slug(rid):
    return rid.replace("urn:", "").replace(":", "-")


def adjudication_input(doc, lex_docs, glosses, lemma_warnings):
    """Review input: the record's public face + its OWN expanded rendering
    (DESIGN-v2 §4.1(b): the explication is judged on what it actually encodes)."""
    exp = expand_ast(doc, lex_docs)
    warns = [w for w in lemma_warnings if doc["id"] in w]
    lines = ["record id: %s" % doc["id"], "label: %s" % doc["label"],
             "gloss: %s" % doc["gloss"], "notes (self-flag): %s" % (doc.get("notes") or "(none)"),
             "references: %s" % (", ".join(sorted(doc.get("references") or [])) or "(none)"),
             "mechanical lemma-collision warnings: %s" % ("; ".join(warns) or "(none)"), ""]
    refs = sorted(doc.get("references") or [])
    if refs:
        lines.append("REFERENCED GLOSSES:")
        lines += ["%s — %s: %s" % (r, glosses[r][0], glosses[r][1]) for r in refs]
        lines.append("")
    lines += ["=== EXPANDED RENDERING (judge THIS: recursively inlined, prime-only) ===",
              rendering_text(exp)]
    return "\n".join(lines)


def validate_adjudication(obj, rid):
    if obj.get("id") != rid:
        return "id %r != %r" % (obj.get("id"), rid)
    if obj.get("verdict") not in ADJ_VERDICTS:
        return "bad verdict %r" % obj.get("verdict")
    for k in ADJ_BOOLS:
        if not isinstance(obj.get(k), bool):
            return "missing/non-bool %r" % k
    if not isinstance(obj.get("reason"), str) or not obj["reason"].strip():
        return "missing reason"
    return None


def adjudicate_one(judge, model, rid, sys_prompt, user_msg, jdir):
    """rp.judge_one's plumbing with the bridge-review validator."""
    prov = jdir / "provenance" / adj_slug(rid)
    review, attempts = None, []
    for k in range(1, dc.MAX_CONTENT + 1):
        adir = prov / ("attempt-%d" % k)
        if model in dc.CLAUDE_MODELS:
            raw, meta = dc.run_claude(model, sys_prompt, user_msg, adir)
        else:
            raw, meta = dc.run_codex(model, sys_prompt, user_msg, adir)
        obj, _warn, perr = dc.extract_json(raw)
        err = perr
        if obj is not None:
            err = validate_adjudication(obj, rid)
            if err is None:
                review = obj
        attempts.append({"n": k, "meta": meta, "error": err})
        if review is not None:
            break
    out = {"judge": judge, "model": model, "record": rid, "attempts": attempts,
           "ok": review is not None, "review": review}
    (jdir / (adj_slug(rid) + ".json")).write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    return out


def adj_disagreements(closure):
    out = []
    for rid in closure:
        pa, pb = ADJ / "F1" / (adj_slug(rid) + ".json"), ADJ / "F2" / (adj_slug(rid) + ".json")
        if not (pa.exists() and pb.exists()):
            continue
        a, b = json.load(open(pa)), json.load(open(pb))
        if not (a.get("ok") and b.get("ok")):
            out.append(rid)
        elif a["review"]["verdict"] != b["review"]["verdict"]:
            out.append(rid)
    return out


def adj_final(rid):
    def leg(j):
        p = ADJ / j / (adj_slug(rid) + ".json")
        if not p.exists():
            return None
        d = json.load(open(p))
        return d.get("review") if d.get("ok") else None
    a, b = leg("F1"), leg("F2")
    if not a or not b:
        return "UNRESOLVED"
    if a["verdict"] == b["verdict"]:
        return a["verdict"]
    t = leg("F3")
    if not t:
        return "UNRESOLVED"
    votes = [a["verdict"], b["verdict"], t["verdict"]]
    return max(set(votes), key=votes.count)


def record_self_lossy(doc):
    import re as _re
    m = _re.match(r"^AST adequacy: (faithful|lossy)", doc.get("notes") or "")
    return m.group(1) == "lossy" if m else False


def cmd_adjudicate_lexicon(args):
    manifest = load_manifest()
    closure, recs = bridge_closure(manifest)
    lex_docs = load_lexicon_docs(manifest)
    if args.summarize:
        return adj_summarize(manifest, closure, recs, lex_docs)
    if not args.judge:
        die("need --judge F1|F2|F3 (or --summarize)")
    if not args.i_am_the_coordinator:
        sys.exit("REFUSING: adjudication calls are coordinator-run. "
                 "Re-run with --i-am-the-coordinator.")
    rub = HERE / "bridge-review-rubric.md"
    if not rub.exists():
        die("bridge-review-rubric.md missing")
    sys_prompt = rub.read_text()
    glosses = lexicon_glosses(manifest)
    warns = manifest.get("slugCollisionGate", {}).get("lemmaWarnings", [])
    model = V2_JUDGES[args.judge]
    jdir = ADJ / args.judge
    jdir.mkdir(parents=True, exist_ok=True)
    targets = closure
    if args.judge == "F3":
        targets = adj_disagreements(closure)
        print("adjudicator F3: %d record(s) with F1/F2 disagreement" % len(targets))
    done = skipped = failed = 0
    for rid in targets:
        if (jdir / (adj_slug(rid) + ".json")).exists():
            skipped += 1
            continue
        user_msg = adjudication_input(lex_docs[rid], lex_docs, glosses, warns)
        print("adjudicate %s [%s] <- %s" % (args.judge, model, rid), flush=True)
        r = adjudicate_one(args.judge, model, rid, sys_prompt, user_msg, jdir)
        done += 1
        failed += 0 if r["ok"] else 1
    print("adjudicate %s done: %d new, %d resumed, %d failed-structural "
          "(closure size %d)" % (args.judge, done, skipped, failed, len(closure)))


def adj_summarize(manifest, closure, recs, lex_docs):
    if (HERE / "FREEZE-v2.json").exists():
        die("FREEZE-v2.json exists -- relabelling/adjudication changes post-freeze "
            "make the run exploratory (DESIGN-v2 §7)")
    finals = {rid: adj_final(rid) for rid in closure}
    lossy_self = {rid: record_self_lossy(lex_docs[rid]) for rid in closure}
    lossy_any = {rid: (lossy_self[rid] or finals[rid] in ("REPAIR", "REJECT"))
                 for rid in closure}

    def per_bridge_closure(bid):
        seen, todo = set(), [bid]
        while todo:
            rid = todo.pop()
            if rid in seen:
                continue
            seen.add(rid)
            todo.extend(recs[rid]["references"])
        return seen

    bridges = sorted(r["id"] for r in manifest["records"] if r["tier"] == "molaug-v0")
    chain = {}
    for bid in bridges:
        cl = per_bridge_closure(bid)
        offenders = sorted(r for r in cl if lossy_any[r])
        chain[bid] = {"chain_lossy": bool(offenders), "lossy_members": offenders}

    # Relabel ACCEPTed bridges (DESIGN-v2 §4.2); REPAIR/REJECT go back through
    # the explicator loop first and get relabelled on a later summarize.
    relabelled = []
    for bid in bridges:
        if finals[bid] != "ACCEPT":
            continue
        slug = bid.split(":")[-1]
        p = LEX / "records" / (slug + ".json")
        doc = json.load(open(p))
        if doc.get("status") != BRIDGE_STATUS:
            doc["status"] = BRIDGE_STATUS
            p.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
            relabelled.append(bid)

    counts = {}
    for v in finals.values():
        counts[v] = counts.get(v, 0) + 1
    out = {"design": "DESIGN-v2.md §4", "closure_size": len(closure),
           "verdict_counts": counts, "finals": finals,
           "self_lossy": {k: v for k, v in lossy_self.items() if v},
           "chain_status": chain, "relabelled_now": relabelled,
           "relabel": BRIDGE_STATUS}
    ADJ.mkdir(parents=True, exist_ok=True)
    (ADJ / "summary.json").write_text(json.dumps(out, indent=2) + "\n")
    lines = ["# Bridge adjudication summary (proxy panel; DESIGN-v2 §4)", "",
             "closure: %d records; verdicts: %s" % (len(closure), counts), "",
             "| bridge | final | self-flag | chain-lossy | lossy members |", "|---|---|---|---|---|"]
    for bid in bridges:
        lines.append("| %s | %s | %s | %s | %s |" % (
            bid.split(":")[-1], finals[bid], "lossy" if lossy_self[bid] else "faithful",
            "YES" if chain[bid]["chain_lossy"] else "no",
            ", ".join(m.split(":")[-1] for m in chain[bid]["lossy_members"]) or "-"))
    pending = sorted(r for r in closure if finals[r] != "ACCEPT")
    if pending:
        lines += ["", "**PENDING (REPAIR/REJECT/UNRESOLVED -- explicator loop, then "
                  "re-run judges + summarize):** %s" % ", ".join(pending)]
    if relabelled:
        lines += ["", "relabelled now -> '%s': %d records. RE-RUN `node lexicon/"
                  "build_manifest.mjs` then `run_s5.py compose --v2` (lexiconSetHash "
                  "changed)." % (BRIDGE_STATUS, len(relabelled))]
    (ADJ / "adjudication-summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


# ---------------------------------------------------------------------------
# v2: calibration (DESIGN-v2 §3.3) -- 6 non-eval concepts, pre-freeze only
# ---------------------------------------------------------------------------
def select_calibration():
    base = stage_dir(0)
    p = base / "calibration-sample.json"
    if p.exists():
        return json.load(open(p))["concepts"]
    pilot = {r["concept"] for r in stage1_rows()}
    elig = [r for r in c100_rows() if r["concept"] not in pilot]  # URN-sorted
    n = len(elig)
    picked = [dict(elig[(i * n) // CALIB_N], bucket="calibration") for i in range(CALIB_N)]
    p.write_text(json.dumps(
        {"built": "S5-v2 calibration sample (DESIGN-v2 §3.3)",
         "rule": ("consensus-100 rows minus the 24 pilot concepts, sorted by URN "
                  "byte order, stride indices floor(i*n/%d); never in the fresh "
                  "sample (consensus-100 URNs are excluded there wholesale)" % CALIB_N),
         "concepts": picked}, indent=2, ensure_ascii=False) + "\n")
    return picked


def cmd_calibrate(args):
    if not args.i_am_the_coordinator:
        sys.exit("REFUSING: calibration makes model calls (coordinator-run). "
                 "Re-run with --i-am-the-coordinator.")
    if (HERE / "FREEZE-v2.json").exists():
        die("FREEZE-v2.json exists -- calibration (and any rubric edit) is "
            "pre-freeze ONLY (DESIGN-v2 §3.3)")
    manifest = load_manifest()
    sp = HERE / "s5-prompt.md"
    if not sp.exists() or not (HERE / "s5-judge-fidelity.md").exists():
        die("composed prompts missing (run: run_s5.py compose --v2)")
    base = stage_dir(0)
    rows = select_calibration()
    print("calibration concepts: %s" % ", ".join(r["concept"] for r in rows))
    gen_arm(rows, sp, base / "gen-s5", GEN_MODELS, "s5")          # 12 mol calls
    expand_stage(0, base, rows, manifest)
    prep_stage(0, base, rows, manifest, args.seed, "fidelity")
    for j in ("F1", "F2", "F3"):
        judge_v2(base, 0, "fidelity", j)
    fkey = json.load(open(base / "judge-key-v2.json"))["fidelity"]
    jroot = base / "judgments-fidelity"
    pairs, per_cand = [], {}
    for bid in sorted(fkey):
        pa, pb = jroot / "F1" / (bid + ".json"), jroot / "F2" / (bid + ".json")
        if pa.exists() and pb.exists():
            a, b = json.load(open(pa)), json.load(open(pb))
            if a.get("ok") and b.get("ok"):
                va = (a["verdicts"].get("A") or {}).get("verdict")
                vb = (b["verdicts"].get("A") or {}).get("verdict")
                pairs.append((va == "FAITHFUL", vb == "FAITHFUL"))
                per_cand[bid] = {"F1": va, "F2": vb,
                                 "final": final_v2(jroot, bid)[0]}
    st = agreement_stats(pairs)
    st["kappa_boot95"] = bootstrap_ci(pairs, "kappa", "calib|%s" % args.seed)
    st["ac1_boot95"] = bootstrap_ci(pairs, "ac1", "calib|%s" % args.seed)
    transcripts = {str(p.relative_to(base)): sha256(p.read_bytes())
                   for p in sorted(jroot.rglob("*.json"))}
    rep = {"design": "DESIGN-v2.md §3.3", "n_candidates": len(fkey),
           "agreement": st, "per_candidate": per_cand,
           "transcript_hashes": transcripts,
           "note": ("rubric edits are allowed ONLY before freeze; if agreement is "
                    "unacceptable, edit judge-addendum-v2.md, recompose, re-run "
                    "calibrate (judgments dirs must be cleared deliberately), THEN freeze")}
    (base / "calibration-report.json").write_text(json.dumps(rep, indent=2) + "\n")
    print("calibration agreement: %s -> %s" % (st, base / "calibration-report.json"))


# ---------------------------------------------------------------------------
# v2: freeze (DESIGN-v2 §7) -- pins; later verbs verify and die on mismatch
# ---------------------------------------------------------------------------
def expander_hash():
    import inspect
    return sha256(inspect.getsource(expand_ast) + inspect.getsource(_blk_depth)
                  + inspect.getsource(rendering_text))


def current_pins():
    manifest = load_manifest()
    pins = {"lexiconSetHash": manifest["lexiconSetHash"],
            "encoderContentHash": manifest["encoderContentHash"],
            "expander_sha256": expander_hash()}
    for k, p in (("s5_prompt_sha256", HERE / "s5-prompt.md"),
                 ("s5_judge_fidelity_sha256", HERE / "s5-judge-fidelity.md"),
                 ("s5_judge_conditional_sha256", HERE / "s5-judge-conditional.md"),
                 ("bridge_rubric_sha256", HERE / "bridge-review-rubric.md"),
                 ("fresh_sample_sha256", RUN / "stage3-fresh.json")):
        pins[k] = sha256(p.read_bytes()) if p.exists() else None
    return pins


def freeze_mismatches(fz):
    """Names of VERIFIED_PINS that are missing or differ from the live tree."""
    pins = current_pins()
    fzp = fz.get("pins", {})
    return [k for k in VERIFIED_PINS
            if fzp.get(k) is None or pins.get(k) is None or fzp[k] != pins[k]]


def verify_freeze_dict(fz):
    mism = freeze_mismatches(fz)
    if mism:
        die("freeze-pin MISMATCH on %s -- a pinned input changed post-freeze; "
            "the run is exploratory, full stop (DESIGN-v2 §7)" % mism)
    return fz


def verify_freeze():
    p = HERE / "FREEZE-v2.json"
    if not p.exists():
        die("FREEZE-v2.json missing -- the v2 campaign stages run POST-freeze "
            "only (run: run_s5.py freeze; DESIGN-v2 §7/§10)")
    return verify_freeze_dict(json.load(open(p)))


def cmd_freeze(_args):
    if (HERE / "FREEZE-v2.json").exists():
        die("FREEZE-v2.json already exists -- refusing to re-freeze (delete it "
            "ONLY if you accept the run becomes exploratory)")
    manifest = load_manifest()
    # gates: adjudication complete + clean, sample drawn, calibration done
    summ_p = ADJ / "summary.json"
    if not summ_p.exists():
        die("lexicon adjudication summary missing (run: adjudicate-lexicon ... "
            "--summarize; DESIGN-v2 §4 comes BEFORE the freeze)")
    summ = json.load(open(summ_p))
    pending = sorted(r for r, v in summ["finals"].items() if v != "ACCEPT")
    if pending:
        die("adjudication not clean -- non-ACCEPT records: %s (explicator repairs, "
            "rebuild manifest, recompose, re-adjudicate, re-summarize first)" % pending)
    bad_status = [r["id"] for r in manifest["records"] if r["tier"] == "molaug-v0"
                  and json.load(open(HERE.parents[2] / r["file"])).get("status") != BRIDGE_STATUS]
    if bad_status:
        die("bridge records not relabelled '%s': %s (run --summarize, then rebuild "
            "manifest + recompose)" % (BRIDGE_STATUS, bad_status))
    sample_p = RUN / "stage3-fresh.json"
    if not sample_p.exists():
        die("s5-run/stage3-fresh.json missing (run: run_s5.py sample --stage 3)")
    sample = json.load(open(sample_p))
    if sample.get("lexiconSetHash") != manifest["lexiconSetHash"]:
        die("stage3-fresh.json was drawn against lexiconSetHash %s but the manifest "
            "now has %s -- re-run sample --stage 3 (post-relabel manifest)"
            % (sample.get("lexiconSetHash"), manifest["lexiconSetHash"]))
    calib_p = stage_dir(0) / "calibration-report.json"
    if not calib_p.exists():
        die("calibration-report.json missing (run: run_s5.py calibrate "
            "--i-am-the-coordinator; DESIGN-v2 §3.3 comes BEFORE the freeze)")
    pins = current_pins()
    missing = [k for k in VERIFIED_PINS if pins.get(k) is None]
    if missing:
        die("cannot freeze -- missing pinned artefacts: %s" % missing)
    fz = {
        "design": "DESIGN-v2.md §7 (kot S5-v2 campaign freeze)",
        "pins": pins,
        "run_s5_sha256_informational": sha256(pathlib.Path(__file__).read_bytes()),
        "fresh_sample": {"file": "s5-run/stage3-fresh.json", "n": sample["n"],
                         "rule": sample["rule"], "sha256": pins["fresh_sample_sha256"]},
        "collision_rule": ("candidate eligible iff NO lemma slug matches any of the "
                           "85 lexicon id slugs (DESIGN-v2 §4.3; mechanically excludes "
                           "'initiation' via lemma 'institution')"),
        "adjudicated_lemma_warnings": manifest.get("slugCollisionGate", {}).get("lemmaWarnings", []),
        "adjudication_summary_sha256": sha256(summ_p.read_bytes()),
        "generators": GEN_MODELS,
        "decoding_and_retry_budget": {"runner": "define_concept.py pinned defaults",
                                      "MAX_CONTENT": dc.MAX_CONTENT,
                                      "note": "identical both arms (DESIGN-v2 §2)"},
        "judges": V2_JUDGES,
        "majority_rule": "final = F1==F2 verdict, else majority(F1,F2,F3); no F3 -> UNRESOLVED (ITT NOT-FAITHFUL)",
        "ensemble_rule": "Arm-E2 = 1 iff any of the arm's two cells has final verdict FAITHFUL",
        "cascade_rule": "take the Luna cell if it gate-passed AND self-flags faithful, else the Fable cell (S1-mirror)",
        "itt_rule": ("a cell that gate-fails, returns no record, or is unjudgeable "
                     "after retries counts NOT-FAITHFUL for its ensemble; counts reported; no exclusions"),
        "mcid_pp": 15.0, "n": FRESH_N,
        "primary_test": "exact two-sided McNemar on the 200 (Flat-E2, Mol-E2) pairs; Tango (1998) asymptotic score 95% CI",
        "decision_rule": "PROXY-PASS = (p<0.05 & delta>0) AND (delta >= +15pp)",
        "multiplicity": "exactly one primary endpoint; all secondaries nominal",
        "stopping_rule": "fixed n=200, no interim looks at stage-3 data; only gate is the pre-stage-3 pilot futility gate",
        "pilot_futility_gate": ("STOP iff pilot Mol-E2 - Flat-E2 <= 0pp OR mol-arm "
                                "zero-ref share >= %.2f" % FUTILITY_ZERO_REF_SHARE),
        "prep_seed": DEFAULT_SEED,
        "calibration": {"report_sha256": sha256(calib_p.read_bytes()),
                        "transcript_hashes": json.load(open(calib_p))["transcript_hashes"]},
        "note": "any post-freeze change to a pinned input => the run is exploratory, full stop",
    }
    (HERE / "FREEZE-v2.json").write_text(json.dumps(fz, indent=2, ensure_ascii=False) + "\n")
    print("FROZEN -> FREEZE-v2.json")
    print(json.dumps(pins, indent=2))


# ---------------------------------------------------------------------------
# dryrun -- 2 non-sample concepts end-to-end (coordinator; needs codex auth)
# ---------------------------------------------------------------------------
def cmd_dryrun(args):
    sp = HERE / "s5-prompt.md"
    if not sp.exists():
        die("s5-prompt.md missing (run: run_s5.py compose)")
    rows, flags = rp.load_rows(), rp.load_flags()
    sample_names = {r["concept"] for r in stage1_rows()}
    elig = sorted((c for c, fl in flags.items()
                   if c not in sample_names and rp.bucket_of(fl) == "unanimous-lossy"),
                  key=lambda c: rows[c]["urn"])
    picks = elig[:2]
    base = RUN / "dryrun"
    base.mkdir(parents=True, exist_ok=True)
    drows = [{"concept": c, "bucket": rp.bucket_of(flags[c]), "urn": rows[c]["urn"],
              "pos": rows[c]["pos"], "lemmas": rows[c]["lemmas"],
              "wn31_gloss": rows[c]["wn31_gloss"],
              "self_flags": {m: flags[c].get(m) for m in rp.MODELS}} for c in picks]
    (base / "dryrun-sample.json").write_text(json.dumps(drows, indent=2) + "\n")
    print("DRY RUN concepts (non-sample, unanimous-lossy): %s" % ", ".join(picks))
    results = gen_arm(drows, sp, base / "gen-s5", GEN_MODELS, "s5")
    ok = all(v.get("s5_ok") or v.get("skipped") for v in results.values())
    (base / "DRYRUN.md").write_text(
        "# S5 dry run\n\n```json\n%s\n```\n\nVERDICT: %s\n"
        % (json.dumps(results, indent=2), "PASS" if ok else "SEE gen-s5/ provenance"))
    print(json.dumps(results, indent=2))
    print("VERDICT:", "PASS" if ok else "FAIL/PARTIAL -- see s5-run/dryrun/")


# ---------------------------------------------------------------------------
# selftest -- OFFLINE plumbing check (no model calls; codex NOT required)
# ---------------------------------------------------------------------------
def cmd_selftest(_args):
    checks, base = [], RUN / "selftest"
    (base / "records").mkdir(parents=True, exist_ok=True)

    def check(name, ok, detail=""):
        checks.append({"check": name, "ok": bool(ok), "detail": str(detail)[:300]})
        print("  [%s] %s %s" % ("PASS" if ok else "FAIL", name, detail if not ok else ""))

    print("S5 selftest (offline; no model calls)")
    # 1. compose
    cmd_compose(None)
    s5p = (HERE / "s5-prompt.md").read_text()
    manifest = load_manifest()
    check("compose: base prompt embedded", "kernel-v1 single-concept definition agent" in s5p)
    check("compose: ref-addendum embedded", "6.1 The vocabulary is now the 65 primes" in s5p)
    check("compose: 85-line lexicon listing embedded",
          sum(1 for l in s5p.splitlines() if l.startswith(("urn:kernel-v0:", "urn:molaug-v0:"))) == 85)
    jp = (HERE / "s5-judge-prompt.md").read_text()
    check("compose: judge addendum embedded", "Additional rule: concept references" in jp)

    # 2. variant gate: positive ref-bearing synthetic record
    def gate(doc):
        p = base / "records" / "cand.json"
        p.write_text(json.dumps(doc))
        r = subprocess.run(["node", str(HERE / "validate-record-ref.mjs"), str(p)],
                           capture_output=True, text=True)
        try:
            return json.loads(r.stdout.strip().splitlines()[-1])
        except Exception:
            return {"ok": False, "code": "ERR_GATE_CRASH", "error": (r.stderr or r.stdout)[-300:]}

    def synth(refs, ast_ids):
        clauses = [{"type": "pred", "pred": "BE-SPEC",
                    "roles": {"undergoer": {"kind": "ref", "index": 1},
                              "attribute": {"kind": "sp", "head": {"kind": "kindFrame",
                                            "of": {"kind": "concept", "id": i}}}}}
                   for i in ast_ids] or [{"type": "pred", "pred": "LIVE",
                                          "roles": {"undergoer": {"kind": "ref", "index": 1}}}]
        return {"id": "urn:kernel-v1:selftest-candidate", "label": "selftest-candidate",
                "synset": "urn:lexical-wn31:n-00000001", "pattern": "selftest",
                "gloss": "a synthetic candidate used only by the offline selftest",
                "explication": {"schema": "kot-ast/1", "frame": "InstanceSchema",
                                "referents": [{"index": 1, "refKind": "SomeoneRef"}],
                                "clauses": clauses},
                "references": refs, "status": "draft",
                "notes": "AST adequacy: lossy — synthetic."}

    g = gate(synth(["urn:kernel-v0:teacher", "urn:molaug-v0:money"],
                   ["urn:kernel-v0:teacher", "urn:molaug-v0:money"]))
    check("gate: ref-bearing record resolves (kernel + bridge), unit-norm D=8192",
          g.get("ok") and g.get("D") == 8192 and abs(g.get("norm", 0) - 1) < 1e-6, g)
    g = gate(synth([], []))
    check("gate: flat record still passes (R3 superset)", g.get("ok"), g)
    g = gate(synth(["urn:molaug-v0:nonexistent"], ["urn:molaug-v0:nonexistent"]))
    check("gate: unknown id -> ERR_REF_NOT_IN_LEXICON", g.get("code") == "ERR_REF_NOT_IN_LEXICON", g)
    g = gate(synth([], ["urn:kernel-v0:teacher"]))
    check("gate: field/AST mismatch -> ERR_REF_MISMATCH", g.get("code") == "ERR_REF_MISMATCH", g)
    g = gate(synth(["urn:kernel-v1:selftest-candidate"], ["urn:kernel-v1:selftest-candidate"]))
    check("gate: self-reference -> ERR_SELF_REF", g.get("code") == "ERR_SELF_REF", g)
    many = manifest["planOrder"][:9]
    ids9 = ["urn:molaug-v0:%s" % s for s in many]
    g = gate(synth(sorted(ids9), ids9))
    check("gate: 9 distinct refs -> ERR_REF_CAP", g.get("code") == "ERR_REF_CAP", g)

    # 3. flat consensus-100 record through the variant gate (real artefact)
    real = sorted(C100.glob("gen/*.fable5.json"))[0]
    r = subprocess.run(["node", str(HERE / "validate-record-ref.mjs"), str(real)],
                       capture_output=True, text=True)
    g = json.loads(r.stdout.strip().splitlines()[-1])
    check("gate: real consensus-100 flat record passes unchanged (%s)" % real.name, g.get("ok"), g)

    # 4. prep plumbing on synthetic S5 candidates built from real flat records
    rows, flags = rp.load_rows(), rp.load_flags()
    picks = sorted(rows)[:2]
    st = RUN / "selftest"
    gen_dir = st / "gen-s5"
    gen_dir.mkdir(parents=True, exist_ok=True)
    srows = []
    for cpt in picks:
        row = {"concept": cpt, "bucket": "selftest", "urn": rows[cpt]["urn"],
               "pos": rows[cpt]["pos"], "lemmas": rows[cpt]["lemmas"],
               "wn31_gloss": rows[cpt]["wn31_gloss"],
               "self_flags": {m: flags.get(cpt, {}).get(m) for m in rp.MODELS}}
        srows.append(row)
        slug = dc.slugify(cpt)
        src, _ = rp.consensus_paths(cpt, FABLE)
        doc = json.load(open(src))
        doc["references"] = []  # keep flat; prep only needs shape
        for m in GEN_MODELS:
            rec = gen_dir / ("%s.%s.json" % (slug, dc.MODEL_SHORT[m]))
            rec.write_text(json.dumps(doc, indent=1, ensure_ascii=False))
            (gen_dir / ("%s.%s.s5gate.json" % (slug, dc.MODEL_SHORT[m]))).write_text(
                json.dumps(s5_gate(rec, row), indent=1))
    # run the prep core against the selftest dir via a stage-like namespace
    glosses = lexicon_glosses(manifest)
    jdir = st / "judge-inputs"
    jdir.mkdir(exist_ok=True)
    n_cand = 0
    for row in srows:
        slug = dc.slugify(row["concept"])
        pool = [("consensus", m, rp.consensus_paths(row["concept"], m)[0])
                for m in GEN_MODELS if rp.record_ok(row["concept"], m)[0]]
        pool += [("s5", m, s5_record(st, "gen-s5", row, m)) for m in GEN_MODELS
                 if s5_record(st, "gen-s5", row, m)]
        txt_lines = ["concept: %s" % row["concept"], ""]
        for i, (_s, _m, rec) in enumerate(pool):
            txt_lines.append("=== CANDIDATE %s ===" % chr(ord("A") + i))
            txt_lines.append(json.dumps(json.load(open(rec))["explication"], indent=1))
        refs_union = sorted({r for _s, _m, rec in pool
                             for r in (json.load(open(rec)).get("references") or [])})
        if refs_union:
            txt_lines.append("=== REFERENCED CONCEPTS ===")
            txt_lines += ["%s — %s: %s" % (i, glosses[i][0], glosses[i][1]) for i in refs_union]
        (jdir / (slug + ".txt")).write_text("\n".join(txt_lines))
        n_cand += len(pool)
    check("prep plumbing: judge-inputs built from mixed pool", n_cand >= 4 and
          len(list(jdir.glob("*.txt"))) == 2, "%d candidates over 2 concepts" % n_cand)
    check("prep plumbing: s5gate written & ok for synthetic flat-shaped records",
          all(json.load(open(p)).get("s5_ok") for p in gen_dir.glob("*.s5gate.json")))

    # 5. stats units
    check("stats: McNemar exact b=1,c=9 -> p=0.0215", abs(mcnemar_exact(1, 9) - 0.021484375) < 1e-9)
    check("stats: McNemar exact b=0,c=0 -> p=1", mcnemar_exact(0, 0) == 1.0)
    lo, hi = wilson(9, 10)
    check("stats: Wilson 9/10 CI sane", 0.55 < lo < 0.61 and 0.98 < hi <= 1.0, (lo, hi))

    # =======================================================================
    # v2 checks (DESIGN-v2 §9.9) -- all offline
    # =======================================================================
    # 6. composed v2 instruments
    check("compose v2: fidelity prompt embeds judge-addendum-v2",
          "Candidates are fully expanded" in (HERE / "s5-judge-fidelity.md").read_text())
    check("compose v2: conditional prompt = v1 addendum + single-candidate note",
          "Single-candidate protocol" in (HERE / "s5-judge-conditional.md").read_text()
          and "Additional rule: concept references" in (HERE / "s5-judge-conditional.md").read_text())

    # 7. expander goldens
    lexd = load_lexicon_docs(manifest)
    tdoc = synth(["urn:kernel-v0:teacher"], ["urn:kernel-v0:teacher"])
    try:
        t1 = rendering_text(expand_ast(tdoc, lexd))
        t2 = rendering_text(expand_ast(tdoc, lexd))
        ok_exp = ('"subExplication"' in t1 and '"kind": "concept"' not in t1
                  and '"kind": "conceptHead"' not in t1 and t1 == t2)
    except ExpandError as e:
        ok_exp, t1 = False, str(e)
    check("expand: teacher-ref -> subExplication inlined, deterministic, no concept nodes left",
          ok_exp, t1[:160])
    fdoc = json.load(open(real))
    check("expand: flat record passes through byte-identically",
          rendering_text(expand_ast(fdoc, lexd)) == rendering_text(fdoc["explication"]))
    kexp = rendering_text(expand_ast(lexd["urn:molaug-v0:kill"], lexd))
    check("expand: bridge record (kill->death) expands recursively",
          kexp.count('"subExplication"') >= 1 and '"kind": "concept"' not in kexp)

    def fake_rec(cid, ref):
        cls = ([{"type": "pred", "pred": "BE-SPEC",
                 "roles": {"undergoer": {"kind": "ref", "index": 1},
                           "attribute": {"kind": "sp", "head": {"kind": "kindFrame",
                                         "of": {"kind": "concept", "id": ref}}}}}]
               if ref else
               [{"type": "pred", "pred": "LIVE",
                 "roles": {"undergoer": {"kind": "ref", "index": 1}}}])
        return {"id": cid, "label": cid,
                "explication": {"schema": "kot-ast/1", "frame": "InstanceSchema",
                                "referents": [{"index": 1, "refKind": "SomeoneRef"}],
                                "clauses": cls}}

    lexd2 = dict(lexd)
    lexd2["urn:molaug-v0:cyc-a"] = fake_rec("urn:molaug-v0:cyc-a", "urn:molaug-v0:cyc-b")
    lexd2["urn:molaug-v0:cyc-b"] = fake_rec("urn:molaug-v0:cyc-b", "urn:molaug-v0:cyc-a")
    code = None
    try:
        expand_ast(synth(["urn:molaug-v0:cyc-a"], ["urn:molaug-v0:cyc-a"]), lexd2)
    except ExpandError as e:
        code = e.code
    check("expand: synthetic cycle fails closed", code == "ERR_CYCLIC_CONCEPT_REF", code)
    code = None
    try:
        expand_ast(synth(["urn:molaug-v0:ghost"], ["urn:molaug-v0:ghost"]), lexd)
    except ExpandError as e:
        code = e.code
    check("expand: unresolved id fails closed", code == "ERR_CONCEPT_UNRESOLVED", code)
    lexd3 = dict(lexd)
    for i in range(8):
        lexd3["urn:molaug-v0:d%d" % i] = fake_rec(
            "urn:molaug-v0:d%d" % i, "urn:molaug-v0:d%d" % (i + 1) if i < 7 else None)
    code = None
    try:
        expand_ast(synth(["urn:molaug-v0:d0"], ["urn:molaug-v0:d0"]), lexd3)
    except ExpandError as e:
        code = e.code
    check("expand: depth > %d fails closed" % MAX_EXPAND_DEPTH, code == "ERR_EXPAND_DEPTH", code)

    # 8. Tango (1998) score CI units
    check("stats: Tango score stat at delta=0 == McNemar z (b=1,c=9,n=24)",
          abs(tango_z(1, 9, 24, 0.0) - 8 / math.sqrt(10)) < 1e-12)
    lo, hi = tango_ci(0, 0, 20)
    anal = Z95 * Z95 / (20 + Z95 * Z95)
    check("stats: Tango CI b=c=0,n=20 == analytic +-z^2/(n+z^2)",
          abs(lo + anal) < 1e-6 and abs(hi - anal) < 1e-6, (lo, hi, anal))
    lo, hi = tango_ci(1, 9, 24)
    check("stats: Tango CI golden (1,9,24) + score self-consistency at endpoints",
          abs(lo - 0.116948) < 1e-4 and abs(hi - 0.541976) < 1e-4
          and abs(tango_z(1, 9, 24, lo) - Z95) < 1e-6
          and abs(tango_z(1, 9, 24, hi) + Z95) < 1e-6, (lo, hi))
    lo, hi = tango_ci(150, 86, 1600)  # Agresti approval-rating pairs: near-Wald here
    check("stats: Tango CI (150,86,1600) sane vs Wald", -0.061 < lo < -0.056 and -0.024 < hi < -0.019, (lo, hi))
    st_ag = agreement_stats([(True, True), (False, False), (True, False), (False, True)])
    check("stats: kappa/AC1 unit (po=.5, .5 marginals -> 0/0)",
          st_ag["kappa"] == 0.0 and st_ag["ac1"] == 0.0, st_ag)

    # 9. ITT/E2 scoring truth table on synthetic verdicts
    def V(fl, ff, ml, mf):
        return {"flat-luna": {"verdict": fl}, "flat-fable": {"verdict": ff},
                "mol-luna": {"verdict": ml}, "mol-fable": {"verdict": mf}}
    cases = [V("FAITHFUL", "LOSSY", "LOSSY", "LOSSY"),           # flat-only -> b
             V("LOSSY", "GATE-FAIL", "FAITHFUL", "GATE-FAIL"),   # mol-only  -> c
             V("GATE-FAIL", "UNJUDGED", "UNRESOLVED", "LOSSY"),  # neither (ITT fail-closed)
             V("FAITHFUL", "FAITHFUL", "LOSSY", "FAITHFUL")]     # both
    e2s = [e2_of(x) for x in cases]
    check("score: ITT/E2 truth table + paired counts",
          e2s == [(True, False), (False, True), (False, False), (True, True)]
          and paired_counts(e2s) == (1, 1, 4), e2s)
    cc = {"flat-luna": {"verdict": "LOSSY", "self_flag": "faithful"},
          "flat-fable": {"verdict": "FAITHFUL", "self_flag": "lossy"},
          "mol-luna": {"verdict": "GATE-FAIL", "self_flag": None},
          "mol-fable": {"verdict": "FAITHFUL", "self_flag": "lossy"}}
    check("score: cascade S1-mirror selector",
          cascade_pick(cc, "flat") == "flat-luna" and cascade_pick(cc, "mol") == "mol-fable")

    # 10. v2 expand/prep plumbing on the selftest records (+1 synthetic ref-bearing mol cell)
    fr = {"concept": "selftest-candidate", "bucket": "selftest",
          "urn": "urn:lexical-wn31:n-00000001", "pos": "n",
          "lemmas": ["selftest-candidate"],
          "wn31_gloss": "a synthetic candidate used only by the offline selftest",
          "self_flags": {}}
    frec = gen_dir / ("selftest-candidate.%s.json" % dc.MODEL_SHORT[LUNA])
    frec.write_text(json.dumps(synth(["urn:kernel-v0:teacher"], ["urn:kernel-v0:teacher"]),
                               indent=1, ensure_ascii=False))
    (gen_dir / ("selftest-candidate.%s.s5gate.json" % dc.MODEL_SHORT[LUNA])).write_text(
        json.dumps({"gate": {"ok": True}, "mechanical_check_errors": [],
                    "ast_adequacy_self_flag": "lossy",
                    "references": ["urn:kernel-v0:teacher"], "s5_ok": True}, indent=1))
    vrows = srows + [fr]
    n_ok, n_fail = expand_stage(1, st, vrows, manifest)
    check("expand v2: gate-fail cells recorded for ITT (fake row flat cells + mol-fable)",
          n_fail >= 3, "%d ok / %d gate-fail" % (n_ok, n_fail))
    prep_n = prep_stage(1, st, vrows, manifest, DEFAULT_SEED, "fidelity")
    cond_n = prep_stage(1, st, vrows, manifest, DEFAULT_SEED, "conditional")
    fkey = json.load(open(st / "judge-key-v2.json"))["fidelity"]
    check("prep v2: ONE blind 6-hex input per candidate",
          len(list((st / "judge-inputs-fidelity").glob("*.txt"))) >= prep_n == n_ok == len(fkey)
          and all(len(b) == 6 and set(b) <= set("0123456789abcdef") for b in fkey))
    check("prep v2: blind ids deterministic (seeded)",
          all(blind_id(DEFAULT_SEED, 1, "fidelity", v["slug"], v["cell"]) == b
              for b, v in fkey.items()))
    sample_bid = sorted(fkey)[0]
    jtxt = (st / "judge-inputs-fidelity" / (sample_bid + ".txt")).read_text()
    check("prep v2: single-candidate shape (one CANDIDATE A, no REFERENCED CONCEPTS)",
          jtxt.count("=== CANDIDATE") == 1 and "=== CANDIDATE A ===" in jtxt
          and "REFERENCED CONCEPTS" not in jtxt)
    vobj = {"concept": "x", "verdicts": [{"candidate": "A", "verdict": "FAITHFUL",
                                          "missing": "", "quality": 2, "reason": "r"}]}
    check("prep v2: pool-of-one input validates under rp.validate_verdicts",
          rp.validate_verdicts(vobj, jtxt) is None)
    fb = blind_id(DEFAULT_SEED, 1, "fidelity", "selftest-candidate", "mol-luna")
    check("prep v2: mol candidate is judged on its EXPANDED rendering",
          '"subExplication"' in (st / "judge-inputs-fidelity" / (fb + ".txt")).read_text())
    ckey = json.load(open(st / "judge-key-v2.json"))["conditional"]
    check("prep v2: conditional instrument = ref-bearing mol cells only",
          cond_n == 1 == len(ckey) and list(ckey.values())[0]["cell"] == "mol-luna")
    ctxt = (st / "judge-inputs-conditional" / (list(ckey)[0] + ".txt")).read_text()
    check("prep v2: conditional input carries raw AST + REFERENCED CONCEPTS gloss block",
          "=== REFERENCED CONCEPTS ===" in ctxt and '"subExplication"' not in ctxt)
    qorder = json.load(open(st / "queue-order-fidelity.json"))
    check("prep v2: seeded global queue order covers all candidates",
          sorted(qorder) == sorted(fkey)
          and qorder == sorted(fkey, key=lambda b: sha256("queue|%s|%s" % (DEFAULT_SEED, b))))

    # 11. adjudication plumbing (offline)
    closure, _recs = bridge_closure(manifest)
    check("adjudicate: closure = 31 bridges + their kernel-v0 reference closure",
          sum(1 for r in closure if r.startswith("urn:molaug-v0:")) == 31
          and len(closure) > 31
          and all(r.startswith(("urn:molaug-v0:", "urn:kernel-v0:")) for r in closure),
          "closure=%d" % len(closure))
    good = {"id": "urn:molaug-v0:kill", "verdict": "ACCEPT", "gloss_scholarly": True,
            "explication_carries_gloss": True, "self_flag_correct": True,
            "sense_collision_free": True, "reason": "ok"}
    check("adjudicate: review validator accepts good / rejects bad JSON",
          validate_adjudication(good, "urn:molaug-v0:kill") is None
          and validate_adjudication({"id": "urn:molaug-v0:kill", "verdict": "MAYBE"},
                                    "urn:molaug-v0:kill") is not None)
    ain = adjudication_input(lexd["urn:molaug-v0:kill"], lexd, glosses,
                             manifest.get("slugCollisionGate", {}).get("lemmaWarnings", []))
    check("adjudicate: review input renders the record's OWN expanded rendering, offline",
          "EXPANDED RENDERING" in ain and '"subExplication"' in ain)

    # 12. freeze pins: live pins verify; tampering dies
    pins = current_pins()
    fz_good = {"pins": {k: v for k, v in pins.items() if v is not None}}
    mism = freeze_mismatches(fz_good)
    check("freeze: live pins verify (only not-yet-built artefacts may be open)",
          set(mism) <= {"fresh_sample_sha256"}, mism)
    fz_bad = json.loads(json.dumps(fz_good))
    fz_bad["pins"]["s5_prompt_sha256"] = "0" * 64
    check("freeze: tampered pin detected", "s5_prompt_sha256" in freeze_mismatches(fz_bad))
    died = False
    try:
        verify_freeze_dict(fz_bad)
    except SystemExit:
        died = True
    check("freeze: pin mismatch DIES (fail closed)", died)

    ok = all(c["ok"] for c in checks)
    (st / "SELFTEST.md").write_text(
        "# S5 offline selftest\n\nNo model calls; codex not required.\n\n```json\n%s\n```\n\n**VERDICT: %s**\n"
        % (json.dumps(checks, indent=2), "PASS" if ok else "FAIL"))
    print("selftest VERDICT: %s (%d/%d checks) -> s5-run/selftest/SELFTEST.md"
          % ("PASS" if ok else "FAIL", sum(c["ok"] for c in checks), len(checks)))
    sys.exit(0 if ok else 1)


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("compose")
    p.add_argument("--v2", action="store_true",
                   help="no-op: compose always writes the v2 prompts too")
    p = sub.add_parser("sample")
    p.add_argument("--stage", type=int, required=True, choices=(2, 3))
    p = sub.add_parser("gen")
    p.add_argument("--stage", type=int, required=True, choices=(1, 2, 3))
    p = sub.add_parser("expand")
    p.add_argument("--stage", type=int, required=True, choices=(1, 3))
    p = sub.add_parser("prep")
    p.add_argument("--stage", type=int, required=True, choices=(1, 2, 3))
    p.add_argument("--seed", type=int, default=DEFAULT_SEED)
    p.add_argument("--instrument", choices=list(INSTRUMENTS),
                   help="v2 single-candidate prep (fidelity|conditional); omit for the v1 pooled prep")
    p = sub.add_parser("judge")
    p.add_argument("--stage", type=int, required=True, choices=(1, 2, 3))
    p.add_argument("--judge", choices=list(rp.JUDGES) + list(V2_JUDGES), required=True)
    p.add_argument("--instrument", choices=list(INSTRUMENTS),
                   help="v2 single-candidate judging; omit for the v1 pooled path")
    p.add_argument("--i-am-the-coordinator", action="store_true")
    p = sub.add_parser("score")
    p.add_argument("--stage", type=int, required=True, choices=(1, 2, 3))
    p.add_argument("--v2", action="store_true",
                   help="v2 scoring (E2 primary, ITT, McNemar+Tango, futility/decision)")
    p = sub.add_parser("adjudicate-lexicon")
    p.add_argument("--judge", choices=list(V2_JUDGES))
    p.add_argument("--summarize", action="store_true")
    p.add_argument("--i-am-the-coordinator", action="store_true")
    p = sub.add_parser("calibrate")
    p.add_argument("--seed", type=int, default=DEFAULT_SEED)
    p.add_argument("--i-am-the-coordinator", action="store_true")
    sub.add_parser("freeze")
    sub.add_parser("dryrun")
    sub.add_parser("selftest")
    args = ap.parse_args()
    if args.cmd == "prep":
        return (cmd_prep_v2 if args.instrument else cmd_prep)(args)
    if args.cmd == "judge":
        if args.instrument:
            if args.judge not in V2_JUDGES:
                die("v2 judging uses --judge F1|F2|F3")
            return cmd_judge_v2(args)
        if args.judge not in rp.JUDGES:
            die("v1 judging uses --judge A|B|T (v2 needs --instrument)")
        return cmd_judge(args)
    if args.cmd == "score":
        return (cmd_score_v2 if args.v2 else cmd_score)(args)
    {"compose": cmd_compose, "sample": cmd_sample, "gen": cmd_gen,
     "expand": cmd_expand, "adjudicate-lexicon": cmd_adjudicate_lexicon,
     "calibrate": cmd_calibrate, "freeze": cmd_freeze,
     "dryrun": cmd_dryrun, "selftest": cmd_selftest}[args.cmd](args)


if __name__ == "__main__":
    main()
