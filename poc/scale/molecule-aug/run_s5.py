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
                          shape on synthetic candidates, McNemar/Wilson units.

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
GO_THRESHOLD_PP = 15.0  # STIPULATED (DESIGN §7.2)


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
    d = RUN / ("stage%d" % stage)
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
    (HERE / "s5-prompt.md").write_text(s5)
    jbase = (AST / "judge_prompt.md").read_text()
    jadd = (HERE / "judge-addendum.md").read_text()
    (HERE / "s5-judge-prompt.md").write_text(jbase + "\n" + jadd)
    out = {
        "s5_prompt_sha256": sha256(s5),
        "s5_judge_prompt_sha256": sha256(jbase + "\n" + jadd),
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


def cmd_sample(args):
    if args.stage != 2:
        die("sample is only needed for --stage 2 (stage 1 reuses ast-pipeline/sample.json)")
    manifest = load_manifest()
    lex_slugs = {r["id"].split(":")[-1] for r in manifest["records"]}
    used_urns = {r["urn"] for r in c100_rows()}
    pool = json.load(open(POOL))["candidates"]
    elig = []
    for x in sorted(pool, key=lambda r: r["urn"]):
        if x["urn"] in used_urns:
            continue
        concept = x["lemmas"][0]
        slugs = {dc.slugify(l) for l in x["lemmas"]} | {dc.slugify(concept)}
        if slugs & lex_slugs:
            continue  # lexicon collision (DESIGN §3.4)
        elig.append({"concept": concept, "bucket": "held-out", "urn": x["urn"],
                     "pos": x["pos"], "lemmas": x["lemmas"], "wn31_gloss": x["gloss"],
                     "self_flags": {}})
    n = len(elig)
    picked = [elig[(i * n) // HELD_OUT_N] for i in range(HELD_OUT_N)]
    out = {"built": "S5 stage-2 held-out sample (DESIGN §7.2)",
           "rule": ("candidate-pool.json sorted by URN byte order; exclude the 100 "
                    "consensus-100 URNs and any candidate with a lemma-slug in the "
                    "85-id lexicon; stride indices floor(i*n/%d)" % HELD_OUT_N),
           "lexiconSetHash": manifest["lexiconSetHash"],
           "n_eligible": n, "concepts": picked}
    RUN.mkdir(exist_ok=True)
    (RUN / "stage2-heldout.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print("wrote s5-run/stage2-heldout.json: %d concepts from %d eligible" % (len(picked), n))
    print("NOTE: re-run `node lexicon/build_manifest.mjs` so the anti-leakage gate "
          "also checks the held-out sample (it reads this file when present).")


def stage2_rows():
    ho = RUN / "stage2-heldout.json"
    if not ho.exists():
        die("s5-run/stage2-heldout.json missing (run: run_s5.py sample --stage 2)")
    return c100_rows(), json.load(open(ho))["concepts"]


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


def cmd_gen(args):
    manifest = load_manifest()
    sp = HERE / "s5-prompt.md"
    if not sp.exists():
        die("s5-prompt.md missing (run: run_s5.py compose)")
    base = stage_dir(args.stage)
    man = {"stage": args.stage, "lexiconSetHash": manifest["lexiconSetHash"],
           "s5_prompt_sha256": sha256(sp.read_text()),
           "base_prompt_sha256": sha256((CDA / "concept-def-prompt.md").read_text())}
    if args.stage == 1:
        rows = stage1_rows()
        man["s5"] = gen_arm(rows, sp, base / "gen-s5", GEN_MODELS, "s5")
    else:
        insample, heldout = stage2_rows()
        man["s5_insample"] = gen_arm(insample, sp, base / "gen-s5", GEN_MODELS, "s5")
        man["s5_heldout"] = gen_arm(heldout, sp, base / "gen-s5-heldout", GEN_MODELS, "s5")
        man["flat_heldout"] = gen_arm(heldout, CDA / "concept-def-prompt.md",
                                      base / "gen-flat-heldout", GEN_MODELS, "flat")
    (base / "gen-manifest.json").write_text(json.dumps(man, indent=2, ensure_ascii=False) + "\n")
    new = sum(1 for k, v in man.items() if isinstance(v, dict) and k.startswith(("s5", "flat"))
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
    sub.add_parser("compose")
    p = sub.add_parser("sample")
    p.add_argument("--stage", type=int, required=True, choices=(2,))
    for verb in ("gen", "prep", "score"):
        p = sub.add_parser(verb)
        p.add_argument("--stage", type=int, required=True, choices=(1, 2))
        if verb == "prep":
            p.add_argument("--seed", type=int, default=DEFAULT_SEED)
    p = sub.add_parser("judge")
    p.add_argument("--stage", type=int, required=True, choices=(1, 2))
    p.add_argument("--judge", choices=list(rp.JUDGES), required=True)
    p.add_argument("--i-am-the-coordinator", action="store_true")
    sub.add_parser("dryrun")
    sub.add_parser("selftest")
    args = ap.parse_args()
    {"compose": cmd_compose, "sample": cmd_sample, "gen": cmd_gen, "prep": cmd_prep,
     "judge": cmd_judge, "score": cmd_score, "dryrun": cmd_dryrun,
     "selftest": cmd_selftest}[args.cmd](args)


if __name__ == "__main__":
    main()
