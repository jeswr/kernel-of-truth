#!/usr/bin/env python3
"""
run_pipeline.py -- AST-generation escalation/ensemble pipeline + blind
assessment harness (exploratory methodology R&D; see DESIGN.md).

NO prereg, NO registry write, NO git commit. Author: fable (lead designer).
The builder runs only `sample` and `dryrun`; the coordinator (Opus) runs
`gen`, `prep`, `judge`, `score` -- judging is independent of generation.

Subcommands (all resumable; every step skips work whose output file exists):

  sample                     write sample.json (deterministic stratified 24)
  gen                        S3 forcing-retry (luna) + S4 ensemble-merge (luna)
                             new calls; S0/S1/S2 reuse consensus-100 gens
  prep [--seed 34]           build blind judge inputs: candidates.json,
                             judge-key.json, strategies.json, judge-inputs/
  judge --judge A|B|T --i-am-the-coordinator
                             run one blind judge over judge-inputs/ (T only
                             re-judges concepts where A and B disagree)
  score                      aggregate judgments -> results.json + results.md
  dryrun                     2 NON-sample concepts end-to-end generation +
                             prep smoke test (claude -p AND codex paths);
                             writes under dryrun/, never touches the real run

Reuses define_concept.py verbatim (subprocess for generation; imported
run_claude/run_codex/extract_json for judge calls) so every new record passes
the identical strict-JSON + mechanical-check + encoder gate, and every call
leaves the identical provenance/report trail. Fail-closed; costs recorded.
"""
import argparse
import hashlib
import json
import pathlib
import re
import statistics
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
SCALE = HERE.parent
C100 = SCALE / "consensus-100"
CDA = SCALE / "concept-def-agent"
sys.path.insert(0, str(CDA))
import define_concept as dc  # noqa: E402  (pinned runner; reused, not modified)

MODELS = ["claude-opus-4-8", "claude-fable-5", "claude-haiku-4-5",
          "gpt-5.6-sol", "gpt-5.6-luna", "gpt-5.6-terra"]
SHORT = dc.MODEL_SHORT
LUNA, FABLE = "gpt-5.6-luna", "claude-fable-5"
# S4 merge-input priority: first 3 gate-clean records in this order (DESIGN §3)
MERGE_PRIORITY = ["claude-fable-5", "claude-opus-4-8", "gpt-5.6-sol",
                  "claude-haiku-4-5", "gpt-5.6-terra", "gpt-5.6-luna"]
JUDGES = {"A": "gpt-5.6-sol", "B": "claude-opus-4-8", "T": "gpt-5.6-terra"}
STRATA = {"unanimous-faithful": 4, "split": 12, "unanimous-lossy": 8}
DEFAULT_SEED = 34


def sha256(s):
    return hashlib.sha256(s.encode("utf-8") if isinstance(s, str) else s).hexdigest()


def load_rows():
    d = json.load(open(C100 / "concepts-100.json"))
    return {c["concept"]: c for c in d["concepts"]}


def load_flags():
    """concept -> {model: faithful|lossy}; from the consensus-100 reports."""
    flags = {}
    for p in sorted(C100.glob("gen/*.report.json")):
        r = json.load(open(p))
        flags.setdefault(r["concept"], {})[r["model"]] = r.get("ast_adequacy_self_flag")
    return flags


def bucket_of(fl):
    v = [x for x in fl.values() if x]
    if len(v) < 6:
        return "incomplete"
    s = set(v)
    return ("unanimous-faithful" if s == {"faithful"}
            else "unanimous-lossy" if s == {"lossy"} else "split")


def consensus_paths(label, model):
    slug = dc.slugify(label)
    return (C100 / "gen" / f"{slug}.{SHORT[model]}.json",
            C100 / "gen" / f"{slug}.{SHORT[model]}.report.json")


def record_ok(label, model, base=None, sub=None):
    """(ok, record_path, report) for an existing record; base/sub override for
    pipeline-generated records (gen-s3/gen-s4 dirs)."""
    if base is None:
        rec, rep = consensus_paths(label, model)
    else:
        slug = dc.slugify(label)
        rec = base / sub / f"{slug}.{SHORT[model]}.json"
        rep = base / sub / f"{slug}.{SHORT[model]}.report.json"
    if not rep.exists():
        return None, rec, None
    report = json.load(open(rep))
    return bool(report.get("ok")), rec, report


# ---------------------------------------------------------------------------
# sample
# ---------------------------------------------------------------------------
def cmd_sample(_args):
    rows, flags = load_rows(), load_flags()
    buckets = {}
    for c, fl in flags.items():
        buckets.setdefault(bucket_of(fl), []).append(c)
    out = {"built": "ast-pipeline stratified sample (exploratory; DESIGN.md §4)",
           "rule": ("buckets from the 6 self-flags in consensus-100 reports "
                    "(incomplete-flag concepts excluded); within each bucket sort "
                    "by URN byte order, take stride indices floor(i*n/k)"),
           "stratum_counts": STRATA, "concepts": []}
    for b, k in STRATA.items():
        xs = sorted(buckets[b], key=lambda c: rows[c]["urn"])
        n = len(xs)
        for i in range(k):
            c = xs[(i * n) // k]
            r = rows[c]
            out["concepts"].append({
                "concept": c, "bucket": b, "urn": r["urn"], "pos": r["pos"],
                "lemmas": r["lemmas"], "wn31_gloss": r["wn31_gloss"],
                "self_flags": {m: flags[c].get(m) for m in MODELS}})
    (HERE / "sample.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print("wrote sample.json: %d concepts (%s)" % (
        len(out["concepts"]), ", ".join("%s=%d" % kv for kv in STRATA.items())))


def load_sample():
    return json.load(open(HERE / "sample.json"))["concepts"]


# ---------------------------------------------------------------------------
# gen -- S3 forcing-retry + S4 merge (all new calls are gpt-5.6-luna / codex)
# ---------------------------------------------------------------------------
def compose_forcing_prompt(base_dir):
    base = (CDA / "concept-def-prompt.md").read_text()
    add = (HERE / "forcing-addendum.md").read_text()
    p = base_dir / "forcing-prompt.md"
    p.write_text(base + "\n" + add)
    return p


def compose_merge_prompt(base_dir, label):
    """base prompt + merge addendum + the first 3 gate-clean candidate records
    (priority order, anonymised) for this concept."""
    cands = []
    for m in MERGE_PRIORITY:
        ok, rec, _ = record_ok(label, m)
        if ok:
            cands.append((m, json.load(open(rec))))
        if len(cands) == 3:
            break
    if len(cands) < 2:
        return None, []
    blocks = []
    for i, (_m, r) in enumerate(cands, 1):
        shown = {k: r.get(k) for k in ("gloss", "pattern", "explication", "notes")}
        blocks.append("--- CANDIDATE-%d (anonymised) ---\n%s"
                      % (i, json.dumps(shown, indent=1, ensure_ascii=False)))
    text = ((CDA / "concept-def-prompt.md").read_text() + "\n"
            + (HERE / "merge-addendum.md").read_text()
            + "\n### Candidates for this concept\n\n" + "\n\n".join(blocks) + "\n")
    d = base_dir / "merge-prompts"
    d.mkdir(parents=True, exist_ok=True)
    p = d / (dc.slugify(label) + ".md")
    p.write_text(text)
    return p, [m for m, _ in cands]


def run_define(row, model, prompt_path, outdir):
    """One define_concept.py subprocess; resumable (skips if report exists)."""
    slug = dc.slugify(row["concept"])
    rep = outdir / f"{slug}.{SHORT[model]}.report.json"
    if rep.exists():
        old = json.load(open(rep))
        # Resume rule: a written record (even gate-failing) is NEVER retried --
        # that is a capability signal. But a report whose every attempt died at
        # the TRANSPORT layer (meta.error set: rc!=0 / auth outage / no reply)
        # is process noise: preserve it as .failed-N and retry on this resume.
        transport_only = (not old.get("record")
                          and old.get("attempts")
                          and all(a.get("meta", {}).get("error")
                                  for a in old["attempts"]))
        if not transport_only:
            return {"skipped": True, "report": str(rep)}
        n = 1
        while (fp := rep.with_suffix(".failed-%d.json" % n)).exists():
            n += 1
        rep.rename(fp)
        print("  retrying %s [%s]: prior report was transport-failure-only "
              "(preserved as %s)" % (row["concept"], model, fp.name), flush=True)
    outdir.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(CDA / "define_concept.py"), row["concept"], row["urn"],
           "--model", model, "--prompt", str(prompt_path), "--out", str(outdir),
           "--gloss", row["wn31_gloss"], "--pos", row["pos"],
           "--lemmas", ",".join(row["lemmas"])]
    print("  -> define_concept %s [%s]" % (row["concept"], model), flush=True)
    p = subprocess.run(cmd, capture_output=True, text=True)
    if not rep.exists():  # transport-level failure; keep evidence, fail closed
        (outdir / f"{slug}.{SHORT[model]}.launchfail.txt").write_text(
            "rc=%d\n--stdout--\n%s\n--stderr--\n%s" % (p.returncode, p.stdout[-4000:], p.stderr[-4000:]))
        return {"skipped": False, "rc": p.returncode, "ok": False, "launchfail": True}
    report = json.load(open(rep))
    return {"skipped": False, "rc": p.returncode, "ok": report.get("ok"),
            "self_flag": report.get("ast_adequacy_self_flag"),
            "cost_usd": (report.get("attempts") or [{}])[-1].get("meta", {}).get("cost_usd"),
            "usage": (report.get("attempts") or [{}])[-1].get("meta", {}).get("usage")}


def gen_for(sample, base_dir, s3_model=LUNA, claude_check=None):
    """Run the new-generation phase for a concept list. Returns manifest."""
    fp = compose_forcing_prompt(base_dir)
    manifest = {"forcing_prompt_sha256": sha256(fp.read_text()),
                "base_prompt_sha256": sha256((CDA / "concept-def-prompt.md").read_text()),
                "s3": {}, "s4": {}, "claude_path_check": {}}
    for row in sample:
        c = row["concept"]
        fl = row["self_flags"]
        if fl.get(LUNA) == "lossy":  # S3 forcing-retry (luna; quota note DESIGN §3)
            manifest["s3"][c] = run_define(row, s3_model, fp, base_dir / "gen-s3")
        if fl.get(LUNA) == "lossy" and fl.get(FABLE) == "lossy":  # S4 merge
            mp, inputs = compose_merge_prompt(base_dir, c)
            if mp is None:
                manifest["s4"][c] = {"ok": False, "error": "fewer than 2 gate-clean merge inputs"}
            else:
                r = run_define(row, LUNA, mp, base_dir / "gen-s4")
                r["merge_inputs"] = inputs
                r["merge_prompt_sha256"] = sha256(mp.read_text())
                manifest["s4"][c] = r
        if claude_check and c == claude_check:  # dryrun only: prove claude -p path
            manifest["claude_path_check"][c] = run_define(
                row, "claude-haiku-4-5", fp, base_dir / "gen-claude")
    (base_dir / "gen-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    return manifest


def cmd_gen(_args):
    m = gen_for(load_sample(), HERE)
    n3 = sum(1 for v in m["s3"].values() if not v.get("skipped"))
    n4 = sum(1 for v in m["s4"].values() if not v.get("skipped"))
    print("gen done: %d/%d S3 calls new, %d/%d S4 calls new (rest resumed); "
          "manifest -> gen-manifest.json" % (n3, len(m["s3"]), n4, len(m["s4"])))


# ---------------------------------------------------------------------------
# prep -- blind judge inputs + strategy selections
# ---------------------------------------------------------------------------
def candidate_pool(row, base_dir):
    """Gate-clean candidates for one concept: (source, model, record_path)."""
    pool = []
    for m in MODELS:
        ok, rec, _ = record_ok(row["concept"], m)
        if ok:
            pool.append(("consensus", m, rec))
    for src, sub in (("s3", "gen-s3"), ("s4", "gen-s4")):
        ok, rec, _ = record_ok(row["concept"], LUNA, base=base_dir, sub=sub)
        if ok:
            pool.append((src, LUNA, rec))
    return pool


def cmd_prep(args, base_dir=None, sample=None):
    base_dir = base_dir or HERE
    sample = sample or load_sample()
    seed = args.seed
    key, cands, strategies = {}, {"seed": seed, "concepts": {}}, {}
    jdir = base_dir / "judge-inputs"
    jdir.mkdir(parents=True, exist_ok=True)
    for row in sample:
        c = row["concept"]
        slug = dc.slugify(c)
        pool = candidate_pool(row, base_dir)
        # dedupe identical explications (keep first provenance as representative)
        uniq, by_ast, membership = [], {}, {}
        for src, m, rec in pool:
            ast = json.dumps(json.load(open(rec))["explication"],
                             sort_keys=True, separators=(",", ":"))
            h = sha256(ast)
            if h not in by_ast:
                by_ast[h] = len(uniq)
                uniq.append((src, m, rec, h))
            membership[(src, m)] = h
        # blind letter assignment: seeded deterministic shuffle
        order = sorted(uniq, key=lambda t: sha256("%s|%s|%s" % (seed, slug, t[3])))
        letters = {}
        key[slug] = {}
        for i, (src, m, rec, h) in enumerate(order):
            L = chr(ord("A") + i)
            letters[h] = L
            key[slug][L] = {"source": src, "model": m, "record": str(rec),
                            "explication_sha256": h}
        letter_of = {sm: letters[h] for sm, h in membership.items()}
        # blind judge input file (bare explications only; DESIGN §5)
        lines = ["concept: %s" % c, "synset: %s" % row["urn"], "pos: %s" % row["pos"],
                 "lemmas: %s" % ", ".join(row["lemmas"]),
                 "wn31-gloss (sense-fixing only): %s" % row["wn31_gloss"], ""]
        for _src, _m, rec, h in order:
            lines.append("=== CANDIDATE %s ===" % letters[h])
            lines.append(json.dumps(json.load(open(rec))["explication"],
                                    indent=1, ensure_ascii=False))
            lines.append("")
        (jdir / (slug + ".txt")).write_text("\n".join(lines))
        # strategy selections (DESIGN §3); GATE-FAIL when the rule's pick is absent
        fl = row["self_flags"]
        s0 = letter_of.get(("consensus", LUNA), "GATE-FAIL")
        s1sel = LUNA if fl.get(LUNA) == "faithful" else FABLE
        s1 = letter_of.get(("consensus", s1sel), "GATE-FAIL")
        s3 = (letter_of.get(("s3", LUNA), "GATE-FAIL")
              if fl.get(LUNA) == "lossy" else s0)
        s4 = (letter_of.get(("s4", LUNA), "GATE-FAIL")
              if (fl.get(LUNA) == "lossy" and fl.get(FABLE) == "lossy") else s1)
        strategies[slug] = {
            "concept": c, "bucket": row["bucket"],
            "S0": {"letter": s0, "new_calls": 0},
            "S1": {"letter": s1, "selected_model": s1sel, "new_calls": 0},
            "S2": {"letters": sorted({letter_of[k] for k in letter_of
                                      if k[0] == "consensus"}), "new_calls": 0},
            "S3": {"letter": s3, "new_calls": int(fl.get(LUNA) == "lossy")},
            "S4": {"letter": s4, "new_calls": int(fl.get(LUNA) == "lossy"
                                                  and fl.get(FABLE) == "lossy")}}
        cands["concepts"][slug] = {"concept": c, "bucket": row["bucket"],
                                   "n_pool": len(pool), "n_unique": len(uniq),
                                   "letters": sorted(key[slug].keys())}
    (base_dir / "judge-key.json").write_text(json.dumps(key, indent=2) + "\n")
    (base_dir / "candidates.json").write_text(json.dumps(cands, indent=2) + "\n")
    (base_dir / "strategies.json").write_text(json.dumps(strategies, indent=2) + "\n")
    tot = sum(v["n_unique"] for v in cands["concepts"].values())
    print("prep done: %d concepts, %d unique blind candidates -> judge-inputs/, "
          "judge-key.json (NEVER show the key to a judge), strategies.json"
          % (len(strategies), tot))


# ---------------------------------------------------------------------------
# judge -- COORDINATOR-RUN blind judging (builder never invokes this)
# ---------------------------------------------------------------------------
def judge_one(judge, model, slug, sys_prompt, user_msg, jdir):
    prov = jdir / "provenance" / slug
    verdicts, attempts = None, []
    for k in range(1, dc.MAX_CONTENT + 1):
        adir = prov / ("attempt-%d" % k)
        if model in dc.CLAUDE_MODELS:
            raw, meta = dc.run_claude(model, sys_prompt, user_msg, adir)
        else:
            raw, meta = dc.run_codex(model, sys_prompt, user_msg, adir)
        obj, _warn, perr = dc.extract_json(raw)
        err = perr
        if obj is not None:
            err = validate_verdicts(obj, user_msg)
            if err is None:
                verdicts = obj
        attempts.append({"n": k, "meta": meta, "error": err})
        if verdicts is not None:
            break
    out = {"judge": judge, "model": model, "slug": slug, "attempts": attempts,
           "ok": verdicts is not None,
           "verdicts": {v["candidate"]: {kk: v.get(kk) for kk in
                        ("verdict", "missing", "quality", "reason")}
                        for v in (verdicts or {}).get("verdicts", [])}}
    (jdir / (slug + ".json")).write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    return out


def validate_verdicts(obj, user_msg):
    want = set(re.findall(r"=== CANDIDATE ([A-Z]) ===", user_msg))
    vs = obj.get("verdicts")
    if not isinstance(vs, list):
        return "no verdicts list"
    got = [v.get("candidate") for v in vs]
    if sorted(got) != sorted(want):
        return "candidates judged %s != shown %s" % (sorted(got), sorted(want))
    for v in vs:
        if v.get("verdict") not in ("FAITHFUL", "LOSSY"):
            return "bad verdict %r" % v.get("verdict")
        if not isinstance(v.get("quality"), int) or not 0 <= v["quality"] <= 3:
            return "bad quality %r" % v.get("quality")
    return None


def disagreement_slugs(base_dir):
    out = []
    for pa in sorted((base_dir / "judgments" / "A").glob("*.json")):
        pb = base_dir / "judgments" / "B" / pa.name
        if not pb.exists():
            continue
        a, b = json.load(open(pa)), json.load(open(pb))
        if not (a.get("ok") and b.get("ok")):
            out.append(pa.stem)
            continue
        for L, va in a["verdicts"].items():
            vb = b["verdicts"].get(L)
            if vb and va["verdict"] != vb["verdict"]:
                out.append(pa.stem)
                break
    return out


def cmd_judge(args):
    if not args.i_am_the_coordinator:
        sys.exit("REFUSING: judging is coordinator-run (builder/judge separation, "
                 "DESIGN.md §5). Re-run with --i-am-the-coordinator.")
    base_dir = HERE
    model = JUDGES[args.judge]
    jdir = base_dir / "judgments" / args.judge
    jdir.mkdir(parents=True, exist_ok=True)
    sys_prompt = (HERE / "judge_prompt.md").read_text()
    slugs = sorted(p.stem for p in (base_dir / "judge-inputs").glob("*.txt"))
    if args.judge == "T":
        slugs = disagreement_slugs(base_dir)
        print("tie-break judge T: %d concept(s) with A/B disagreement" % len(slugs))
    done = skipped = failed = 0
    for slug in slugs:
        if (jdir / (slug + ".json")).exists():
            skipped += 1
            continue
        user_msg = (base_dir / "judge-inputs" / (slug + ".txt")).read_text()
        print("judge %s [%s] <- %s" % (args.judge, model, slug), flush=True)
        r = judge_one(args.judge, model, slug, sys_prompt, user_msg, jdir)
        done += 1
        failed += 0 if r["ok"] else 1
    print("judge %s done: %d new, %d resumed, %d failed-structural"
          % (args.judge, done, skipped, failed))


# ---------------------------------------------------------------------------
# score -- aggregate blind verdicts into per-strategy results
# ---------------------------------------------------------------------------
def cmd_score(_args):
    base_dir = HERE
    strategies = json.load(open(base_dir / "strategies.json"))
    J = {}
    for j in "ABT":
        J[j] = {p.stem: json.load(open(p))
                for p in (base_dir / "judgments" / j).glob("*.json")} \
            if (base_dir / "judgments" / j).exists() else {}

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

    res = {"strategies": {}, "per_concept": {}, "unresolved": []}
    names = ["S0", "S1", "S2", "S3", "S4"]
    agg = {s: {"faithful": 0, "lossy": 0, "gate_fail": 0, "unresolved": 0,
               "qualities": [], "new_calls": 0,
               "by_bucket": {b: [0, 0] for b in STRATA}} for s in names}
    for slug, st in strategies.items():
        row = {"bucket": st["bucket"]}
        for s in names:
            if s == "S2":
                best_v, best_q, votes = "LOSSY", None, []
                for L in st["S2"]["letters"]:
                    v, q = final(slug, L)
                    votes.append((L, v, q))
                    if v == "FAITHFUL" and (best_q is None or best_v != "FAITHFUL"
                                            or q > best_q):
                        best_v, best_q = "FAITHFUL", q
                    elif v == "UNRESOLVED" and best_v == "LOSSY":
                        best_v = "UNRESOLVED"
                    if q is not None and best_q is None:
                        best_q = q
                    elif q is not None and best_v != "FAITHFUL":
                        best_q = max(best_q, q)
                v, q, detail = best_v, best_q, votes
            else:
                L = st[s]["letter"]
                if L == "GATE-FAIL":
                    v, q, detail = "GATE-FAIL", None, L
                else:
                    v, q = final(slug, L)
                    detail = L
                    v = v or "UNJUDGED"
            row[s] = {"verdict": v, "quality": q, "detail": detail}
            a = agg[s]
            a["new_calls"] += st[s].get("new_calls", 0)
            if v == "FAITHFUL":
                a["faithful"] += 1
                a["by_bucket"][st["bucket"]][0] += 1
            elif v == "LOSSY":
                a["lossy"] += 1
            elif v == "GATE-FAIL":
                a["gate_fail"] += 1
            else:
                a["unresolved"] += 1
                res["unresolved"].append((slug, s, v))
            a["by_bucket"][st["bucket"]][1] += 1
            if q is not None:
                a["qualities"].append(q)
        res["per_concept"][slug] = row
    lines = ["# ast-pipeline results (exploratory; n=%d concepts)" % len(strategies), "",
             "| strategy | judged FAITHFUL | mean quality | gate-fail | unresolved | new calls | "
             + " | ".join(STRATA) + " |", "|" + "---|" * (6 + len(STRATA))]
    for s in names:
        a = agg[s]
        n = len(strategies)
        mq = ("%.2f" % statistics.mean(a["qualities"])) if a["qualities"] else "-"
        cells = ["%d/%d" % tuple(a["by_bucket"][b]) for b in STRATA]
        lines.append("| %s | %d/%d | %s | %d | %d | %d | %s |"
                     % (s, a["faithful"], n, mq, a["gate_fail"], a["unresolved"],
                        a["new_calls"], " | ".join(cells)))
        a["mean_quality"] = mq
        a.pop("qualities")
    res["aggregate"] = agg
    (base_dir / "results.json").write_text(json.dumps(res, indent=2) + "\n")
    (base_dir / "results.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    if res["unresolved"]:
        print("\nWARNING: %d unresolved/unjudged cells -- run the missing judge(s)."
              % len(res["unresolved"]))


# ---------------------------------------------------------------------------
# dryrun -- 2 non-sample concepts; prove nested claude -p AND codex invocation
# ---------------------------------------------------------------------------
def cmd_dryrun(args):
    rows, flags = load_rows(), load_flags()
    sample_names = {r["concept"] for r in load_sample()}
    elig = sorted((c for c, fl in flags.items()
                   if c not in sample_names and bucket_of(fl) != "incomplete"
                   and fl.get(LUNA) == "lossy"),
                  key=lambda c: rows[c]["urn"])
    merge_c = next(c for c in elig if flags[c].get(FABLE) == "lossy")
    other_c = next(c for c in elig if c != merge_c)
    base = HERE / "dryrun"
    base.mkdir(exist_ok=True)
    dsample = []
    for c in (merge_c, other_c):
        r = rows[c]
        dsample.append({"concept": c, "bucket": bucket_of(flags[c]), "urn": r["urn"],
                        "pos": r["pos"], "lemmas": r["lemmas"],
                        "wn31_gloss": r["wn31_gloss"],
                        "self_flags": {m: flags[c].get(m) for m in MODELS}})
    (base / "dryrun-sample.json").write_text(json.dumps(dsample, indent=2) + "\n")
    print("DRY RUN concepts (non-sample): %s (S3+S4+codex), %s (S3-codex + claude-path check)"
          % (merge_c, other_c))
    manifest = gen_for(dsample, base, claude_check=other_c)
    ns = argparse.Namespace(seed=args.seed)
    cmd_prep(ns, base_dir=base, sample=dsample)
    checks = {
        "codex_s3": {c: v for c, v in manifest["s3"].items()},
        "codex_s4_merge": {c: v for c, v in manifest["s4"].items()},
        "claude_p": {c: v for c, v in manifest["claude_path_check"].items()},
    }
    ok = all(v.get("ok") or v.get("skipped")
             for group in checks.values() for v in group.values()) and bool(
        list((base / "judge-inputs").glob("*.txt")))
    summary = ["# DRY RUN result", "",
               "concepts (deliberately OUTSIDE the 24-concept sample): %s, %s" % (merge_c, other_c),
               "", "```json", json.dumps(checks, indent=2), "```", "",
               "judge-inputs built: %s" % sorted(p.name for p in (base / 'judge-inputs').glob('*.txt')),
               "", "**VERDICT: %s** -- nested `codex exec` and `claude -p` invocation %s"
               % ("PASS" if ok else "FAIL", "both work end-to-end from inside run_pipeline.py"
                  if ok else "FAILED; see gen-manifest.json + provenance dirs")]
    (base / "DRYRUN.md").write_text("\n".join(summary) + "\n")
    print("\n".join(summary))


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("sample")
    sub.add_parser("gen")
    p = sub.add_parser("prep")
    p.add_argument("--seed", type=int, default=DEFAULT_SEED)
    p = sub.add_parser("judge")
    p.add_argument("--judge", choices=list(JUDGES), required=True)
    p.add_argument("--i-am-the-coordinator", action="store_true")
    sub.add_parser("score")
    p = sub.add_parser("dryrun")
    p.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = ap.parse_args()
    {"sample": cmd_sample, "gen": cmd_gen, "prep": cmd_prep,
     "judge": cmd_judge, "score": cmd_score, "dryrun": cmd_dryrun}[args.cmd](args)


if __name__ == "__main__":
    main()
