#!/usr/bin/env python3
"""f1k_bringup_gate.py — kot-f1k-bringup-gate/2: the FIXED F1-K bring-up
affordability gate (poc/gcp/F1K-BRINGUP-GATE-FIX.md v1; closes GAP-1/2/3 of
F1K-CONSTRUCTION-PLAN.md v3 §4.2, per the v2 review findings 3/4/5 of
poc/gpt56-review/f1k-construction-review-VERDICT.md).

WHAT THIS FIXES (spec: the fix memo; frozen rule: CONSTRUCTION-PLAN v3 §7):
  GAP-1  the construction-license timing input is now a DETERMINISTIC,
         seeded, stratified sample of the REAL frozen corpora (never the
         synthetic 10xT96/10xT384 functional-gate mix — that stays a
         secondary diagnostic only, f1k_gcp.py `affordability`).
  GAP-2  the words->tokens factor f is MEASURED on the full frozen corpora
         with the REAL bring-up tokenizer (tok_glm52.py, ASM-1971 pin) and
         the frozen `f <= 1.60` branch of the §7 rule is wired mechanically.
  GAP-3  the ledger projection is PER-ITEM token-aware: sum of s_hat(T_i)
         over every prefill of the frozen 19,964-prefill envelope at its
         MEASURED token count — never `19964 * one_average` (v2 review
         finding 3: a single average can approve an over-budget long tail).

SUBCOMMANDS (control box = $0; VM = on the bring-up box):
  spec     ($0, control box) witness the sampling rule + corpus shas
  fcount   (VM) tokenize the frozen corpora -> per-item T + measured f
  realize  (VM) apply the frozen sampling rule -> timing sample manifests
  pinfile  (VM) fail-closed merge of the EXPLICIT per-item T1 stats files
           (STATS=<file>, one per run) -> bring-up pin file at PIN_GB
  collect  (VM) merge timing results -> gate-inputs.json (no verdict here)
  project  (control box; use `f1k_gcp.py gate`) -> bringup-gate.json GREEN/STOP
  checkpoint (runner, during licensed construction) early-abort
           re-projection from realized construction throughput [REV-B]
  selftest ($0) mock oracle — HONEST SCOPE [REV-B]: projection/license
           logic, sampling rule, per-item stats merge, manifest-vs-model
           consistency, engagement/regime refusals, early-abort; NOT the
           real engine/tokenizer/GCS/VM (those exist only on the VM path)

Zero non-stdlib deps on the control box; the VM path shells out to the
pinned kot-f1k-tok/1 wrapper (tok_glm52.py) for all real tokenization.
Deterministic: no wall-clock, no RNG (SAMPLE_SEED keys tie-break hashing
only). Fail-closed with ERR_* codes; no silent fallbacks.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import f1k_ops

SCHEMA = "kot-f1k-bringup-gate/2"
#   [REV-C F5ii] /2 adds REQUIRED model-bundle binding fields to the gate
#   artifact (model_bundle.add7_src_sha256 + model_bundle.tokens_full_
#   sha256); every consumer (driver Add7Model, pin-fetch, checkpoint,
#   construction-guard) requires THIS schema id — a /1 artifact (which
#   cannot prove its sidecar/model identity) is refused, never coerced.

# ---------------------------------------------------------------------------
# FROZEN GATE CONSTANTS (fix memo §2; every value tagged there)
# ---------------------------------------------------------------------------
SAMPLE_SEED = 20260718        # [STIPULATED] keys the tie-break hash ONLY
F_THRESHOLD = 1.60            # CONSTRUCTION-PLAN v3 §4.2/§7 frozen threshold
CONT_TOKENS = 8               # [STIPULATED] = the functional-gate contlen;
                              # also the uniform continuation addend T_i = T_text + 8
QUANTILE_EDGES = (0.0, 0.20, 0.40, 0.60, 0.80, 0.95, 1.0)   # [STIPULATED]
BIN_ALLOC = (4, 4, 4, 4, 4, 6)   # per-bin sampled texts; + campaign max-T
T1_N = 8                      # unpinned stats/margin subset size [STIPULATED]
POP_FLOOR = {"construction": 2, "pilot": 2, "guard": 2,
             "main-tmpl": 2, "main-d3": 2}    # population coverage floors
N_SAMPLE_MAX = 34             # hard cap incl. coverage adds (fail-closed)
FLOOR_EXTRAP_MIN_FRAC = 0.35  # [STIPULATED] s_lo(T) >= 0.35*s_bar(minknot)
SE_MULT = 1.0                 # frozen band rule: +-1 SE
RESERVE_USD = 8.0             # [STIPULATED] plan SS8 staging/overhead + ~5%
                              # preemption re-work reserved INSIDE the caps
                              # (v3-review finding 4: project_ledger was
                              # reserve-blind). CAP tests are RESERVE-
                              # INCLUSIVE (usd + 8; hours + 8/rate); FLOOR
                              # tests stay compute-only (a reserve must never
                              # help a too-cheap ledger clear the honesty
                              # floors).  fix memo SSA2.
PER_EXPERT_BYTES = 18541666.7 # [MEASURED] probe-results/m4.json per_expert_bytes

# Frozen campaign inventory (envelope-exact; fix memo §2.2, all cited):
# construction 4,608 x1 [PINS construction-manifest]; main 1,573 x (7 tmpl +
# 1 d3) [ARMS_MAIN + R_DRNG=3]; pilot 96 x 22 (template-only; VERDICT #1);
# guard 60 x 11 (registered <=660 bound); +REPLACE 1,573 x1 tmpl.
N_CONSTRUCTION = 4608
N_TEST, M_MAIN_TMPL, M_MAIN_D3 = 1573, 7, 1
N_DEV, M_PILOT = 96, 22
N_GUARD, M_GUARD = 60, 11
M_REPLACE = 1
MANDATORY_PREFILLS = 19964    # must reproduce exactly (asserted)

CORPUS_FILES = ("construction-manifest.jsonl", "test.jsonl", "dev.jsonl",
                "guard.jsonl")


def die(code, msg):
    sys.stderr.write("ERR_%s: %s\n" % (code, msg))
    raise SystemExit(2)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _fin(val, what, code, lo=0.0, lo_open=False):
    """[REV-E 3] operator-numeric hygiene (round-4 verdict 4; the landed
    PIN_GB defect class): every number an operator hands this CLI must
    be FINITE and honor its sign contract BEFORE it reaches any cap
    comparison — nan > cap and nan <= cap are BOTH False [MEASURED], so
    a NaN basis turns breach predicates into silent fail-open
    GO/CONTINUE. Fail closed at the parse, never downstream."""
    try:
        f = float(val)
    except (TypeError, ValueError):
        die(code, "%s: %r is not a number [REV-E]" % (what, val))
    if not math.isfinite(f):
        die(code, "%s: %r is not FINITE — NaN/inf fail OPEN through cap "
            "comparisons (nan > cap is False; the PIN_GB defect class) "
            "[REV-E]" % (what, val))
    if f < lo or (lo_open and f == lo):
        die(code, "%s: %r must be %s %g [REV-E]"
            % (what, val, ">" if lo_open else ">=", lo))
    return f


def tiehash(key):
    return hashlib.sha256(("%d:%s" % (SAMPLE_SEED, key)).encode()).hexdigest()


def wcount(text):
    """Whitespace word count — the SAME convention behind the plan's word
    anchors (30.8/122.7/56.8/83.8) and the f<=1.60 threshold derivation."""
    return len(text.split())


# ---------------------------------------------------------------------------
# frozen campaign inventory (population, multiplicity, text) from the corpora
# ---------------------------------------------------------------------------
def load_inventory(corpus_dir):
    d = Path(corpus_dir)
    for f in CORPUS_FILES:
        if not (d / f).is_file():
            die("F1K_GATE_CORPUS", "missing corpus file %s" % (d / f))
    inv = []

    def rows(name):
        return [json.loads(l) for l in open(d / name, encoding="utf-8")
                if l.strip()]

    cons = rows("construction-manifest.jsonl")
    if len(cons) != N_CONSTRUCTION:
        die("F1K_GATE_CORPUS", "construction-manifest rows %d != %d"
            % (len(cons), N_CONSTRUCTION))
    for i, r in enumerate(cons):
        inv.append({"key": "construction:%04d" % i, "pop": "construction",
                    "m": 1, "text": r["text"]})
    test = rows("test.jsonl")
    if len(test) != N_TEST:
        die("F1K_GATE_CORPUS", "test rows %d != %d" % (len(test), N_TEST))
    for r in test:
        inv.append({"key": "main-tmpl:%s" % r["item_id"], "pop": "main-tmpl",
                    "m": M_MAIN_TMPL, "text": r["template_text"]})
        inv.append({"key": "main-d3:%s" % r["item_id"], "pop": "main-d3",
                    "m": M_MAIN_D3, "text": r["d3_template_text"]})
    dev = rows("dev.jsonl")
    if len(dev) != N_DEV:
        die("F1K_GATE_CORPUS", "dev rows %d != %d" % (len(dev), N_DEV))
    for r in dev:
        inv.append({"key": "pilot:%s" % r["item_id"], "pop": "pilot",
                    "m": M_PILOT, "text": r["template_text"]})
    guard = rows("guard.jsonl")
    if len(guard) != N_GUARD:
        die("F1K_GATE_CORPUS", "guard rows %d != %d" % (len(guard), N_GUARD))
    for r in guard:
        inv.append({"key": "guard:%s" % r["item_id"], "pop": "guard",
                    "m": M_GUARD, "text": r["template_text"]})
    total = sum(e["m"] for e in inv)
    if total != MANDATORY_PREFILLS:
        die("F1K_GATE_CORPUS", "inventory prefills %d != frozen %d"
            % (total, MANDATORY_PREFILLS))
    return inv


def corpus_shas(corpus_dir):
    return {f: sha256_file(Path(corpus_dir) / f) for f in CORPUS_FILES}


# ---------------------------------------------------------------------------
# tokenization (real: the pinned kot-f1k-tok/1 wrapper; mock: --mock-f)
# ---------------------------------------------------------------------------
def tokenize(inv, args):
    if args.mock_f is not None:
        _fin(args.mock_f, "--mock-f", "F1K_GATE_TOK",
             lo_open=True)                                  # [REV-E 3]
        # $0 MOCK path (selftest / dry-run ONLY; clearly labeled in output):
        # T = round(W * mock_f), ids deterministic in-vocab like the
        # functional-gate sample. NEVER a license input.
        for e in inv:
            w = wcount(e["text"])
            t = max(4, round(w * args.mock_f))
            e["W"], e["T"] = w, t
            e["ids"] = [10 + (int(tiehash(e["key"])[:8], 16) + i) % 180
                        for i in range(t)]
        return {"mode": "MOCK", "mock_f": args.mock_f, "sha256": None}
    if not (args.tok_wrapper and args.tokenizer):
        die("F1K_GATE_TOK", "--tok-wrapper and --tokenizer required "
            "(or --mock-f for the $0 mock path)")
    tok_sha = sha256_file(args.tokenizer)
    env = dict(os.environ, TOK_SHA256=tok_sha)
    proc = subprocess.Popen(
        [sys.executable, args.tok_wrapper, args.tokenizer],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)
    inp = "".join(json.dumps({"text": e["text"]}) + "\n" for e in inv)
    out, _ = proc.communicate(inp.encode("utf-8"))
    if proc.returncode != 0:
        die("F1K_GATE_TOK", "tok_glm52.py exited %d" % proc.returncode)
    lines = out.decode("utf-8").splitlines()
    if len(lines) != len(inv):
        die("F1K_GATE_TOK", "tokenizer emitted %d lines for %d texts"
            % (len(lines), len(inv)))
    for e, l in zip(inv, lines):
        ids = json.loads(l)["ids"]
        e["W"], e["T"], e["ids"] = wcount(e["text"]), len(ids), ids
    return {"mode": "REAL", "mock_f": None, "sha256": tok_sha}


def cmd_fcount(args):
    inv = load_inventory(args.corpus_dir)
    tokinfo = tokenize(inv, args)
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "tokens-full.jsonl", "w") as f:
        for e in inv:
            f.write(json.dumps({"key": e["key"], "pop": e["pop"],
                                "m": e["m"], "W": e["W"], "T": e["T"],
                                "ids": e["ids"]}) + "\n")
    pops, blend_t, blend_w = {}, 0, 0
    for e in inv:
        p = pops.setdefault(e["pop"], {"n_texts": 0, "prefills": 0,
                                       "words_x_m": 0, "tokens_x_m": 0})
        p["n_texts"] += 1
        p["prefills"] += e["m"]
        p["words_x_m"] += e["m"] * e["W"]
        p["tokens_x_m"] += e["m"] * e["T"]
        blend_t += e["m"] * e["T"]
        blend_w += e["m"] * e["W"]
    for p in pops.values():
        p["f"] = round(p["tokens_x_m"] / p["words_x_m"], 4)
    summary = {
        "schema": SCHEMA + ":token-counts",
        "tokenizer": tokinfo,
        "corpus_sha256": corpus_shas(args.corpus_dir),
        "populations": pops,
        "prefills_mandatory": MANDATORY_PREFILLS,
        "f_blended": round(blend_t / blend_w, 4),
        "f_threshold": F_THRESHOLD,
        "f_convention": "whitespace words; texts only (no continuation "
                        "addend) — matches the plan word anchors",
    }
    (outdir / "token-counts.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({k: summary[k] for k in
                      ("f_blended", "tokenizer", "populations")}, indent=2))
    return 0


# ---------------------------------------------------------------------------
# frozen sampling rule (fix memo §2.3) — deterministic, seeded, stratified
# ---------------------------------------------------------------------------
def weighted_quantile_edges(entries):
    """Prefill-mass-weighted T-quantile edges over Tp = T + CONT_TOKENS."""
    pts = sorted(((e["T"] + CONT_TOKENS, e["m"]) for e in entries))
    total = sum(m for _, m in pts)
    edges, acc, qi = [pts[0][0]], 0, 1
    for tp, m in pts:
        acc += m
        while qi < len(QUANTILE_EDGES) - 1 and \
                acc >= QUANTILE_EDGES[qi] * total:
            edges.append(tp)
            qi += 1
    while len(edges) < len(QUANTILE_EDGES):
        edges.append(pts[-1][0])
    edges[-1] = pts[-1][0]
    return edges


def select_sample(entries):
    """The STIPULATED rule, verbatim from the fix memo §2.3: bin by weighted
    quantiles; evenly spaced (T, tiehash)-ranks per bin; force the campaign
    max-T prefill; then population-coverage ADDS (never removals)."""
    for e in entries:
        e["Tp"] = e["T"] + CONT_TOKENS
    edges = weighted_quantile_edges(entries)
    bins = [[] for _ in range(len(QUANTILE_EDGES) - 1)]
    for e in entries:
        for j in range(len(bins)):
            hi_ok = e["Tp"] <= edges[j + 1] if j == len(bins) - 1 \
                else e["Tp"] < edges[j + 1]
            if e["Tp"] >= edges[j] and hi_ok:
                bins[j].append(e)
                break
    chosen, seen = [], set()

    def pick(e, bin_id, why):
        if e["key"] in seen:
            return False
        seen.add(e["key"])
        chosen.append({"key": e["key"], "pop": e["pop"], "bin": bin_id,
                       "W": e["W"], "T": e["T"], "Tp": e["Tp"],
                       "why": why, "ids": e["ids"]})
        return True

    for j, b in enumerate(bins):
        b.sort(key=lambda e: (e["Tp"], tiehash(e["key"])))
        n, k = len(b), BIN_ALLOC[j]
        if n == 0:
            die("F1K_GATE_SAMPLE", "empty T bin %d — rule cannot realize" % j)
        for i in range(k):
            pick(b[min(n - 1, int((i + 0.5) * n / k))], j, "rank")
    allmax = max(entries, key=lambda e: (e["Tp"], tiehash(e["key"])))
    pick(allmax, len(bins) - 1, "campaign-max-T")
    # population floors: deterministic ADDS of the population's median-Tp text
    for pop in sorted(POP_FLOOR):
        have = sum(1 for c in chosen if c["pop"] == pop)
        cand = sorted((e for e in entries if e["pop"] == pop),
                      key=lambda e: (e["Tp"], tiehash(e["key"])))
        i = len(cand) // 2
        while have < POP_FLOOR[pop] and cand:
            e = cand[i % len(cand)]
            j = next(k for k in range(len(bins)) if e in bins[k])
            if pick(e, j, "pop-floor"):
                have += 1
            i += 1
    if len(chosen) > N_SAMPLE_MAX:
        die("F1K_GATE_SAMPLE", "sample %d > cap %d" % (len(chosen),
                                                       N_SAMPLE_MAX))
    chosen.sort(key=lambda c: (c["Tp"], tiehash(c["key"])))
    for i, c in enumerate(chosen):
        c["sample_id"] = "s%03d" % i
    return edges, chosen


def cmd_realize(args):
    tokdir = Path(args.tokens)
    entries = [json.loads(l)
               for l in open(tokdir / "tokens-full.jsonl", encoding="utf-8")]
    edges, chosen = select_sample(entries)
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    # one run_score manifest per sampled text (per-item engine timer)
    # [REV-B F2, gate-fix review #3] ctx = the FULL text (all T ids), cont =
    # CONT_TOKENS appended deterministic in-vocab ids (the final text id
    # repeated — timing-only continuation; the real campaign scores the
    # few-token label). The engine therefore processes ctxlen + contlen =
    # T + 8 = Tp tokens — EXACTLY the projection model's T_i. The old line
    # (`t - CONT_TOKENS, CONT_TOKENS, <t ids>`) measured total t while the
    # model labeled it t+8: every observation mislabeled by one
    # continuation. cmd_collect re-checks this structurally (fail-closed).
    for c in chosen:
        t = c["T"]
        if t < 2:
            die("F1K_GATE_SAMPLE", "%s: T=%d too short to score"
                % (c["key"], t))
        cont_ids = [c["ids"][-1]] * CONT_TOKENS
        line = "%d %d %s" % (t, CONT_TOKENS,
                             " ".join(map(str, c["ids"] + cont_ids)))
        (outdir / ("sample-%s.score" % c["sample_id"])).write_text(line + "\n")
    # T1 (unpinned stats/margin) subset: evenly spaced ranks EXCLUDING the
    # global max (cost control; the max is timed pinned in T2 regardless)
    body = chosen[:-1]
    t1 = [body[min(len(body) - 1, int((i + 0.5) * len(body) / T1_N))]
          ["sample_id"] for i in range(T1_N)]
    t1 = sorted(set(t1))
    spec = {
        "schema": SCHEMA + ":timing-sample",
        "seed": SAMPLE_SEED,
        "rule": {"quantile_edges": list(QUANTILE_EDGES),
                 "bin_alloc": list(BIN_ALLOC), "cont_tokens": CONT_TOKENS,
                 "pop_floor": POP_FLOOR, "t1_n": T1_N,
                 "text": "fix memo §2.3 (frozen)"},
        "realized_bin_edges_Tp": edges,
        "n": len(chosen),
        "t1_sample_ids": t1,
        "entries": [{k: c[k] for k in ("sample_id", "key", "pop", "bin",
                                       "W", "T", "Tp", "why")}
                    for c in chosen],
    }
    (outdir / "timing-sample.json").write_text(json.dumps(spec, indent=2))
    print("timing sample: %d texts (T1 subset %d); bins %s"
          % (len(chosen), len(t1), edges))
    return 0


# ---------------------------------------------------------------------------
# bring-up pin file from engine usage stats ([MEASURED] accum20.stats format)
# ---------------------------------------------------------------------------
def cmd_pinfile(args):
    """[REV-B F1, gate-fix review #2] EXPLICIT per-item merge — never a
    permissive glob. The engine interface is STATS=<file> (kae-add-path.patch
    :175/:180/:183, verified this pass: `stats=getenv("STATS")` then
    `stats_dump(&m, stats)` writes THE named file), so each T1 run writes
    its OWN stats file and the pin derives from a fail-closed merge over an
    explicit manifest: any listed file missing/empty/malformed -> die (the
    old glob 'skip non-conforming' path silently shrank the union). The
    stats_dump truncate-vs-append semantics stay fetch-grade [ASM-1971]; a
    FRESH per-run path (worker rm's before each run) is correct under
    EITHER. Aggregation [STIPULATED]: SUM of counts per (layer, expert)
    over ALL per-item files (usage histograms are additive). Derivation
    provenance (n files, per-file sha256+lines, manifest hash) is recorded
    beside the pin and travels into the gate artifact."""
    paths = [ln.strip() for ln in open(args.stats_manifest, encoding="utf-8")
             if ln.strip()]
    if not paths:
        die("F1K_GATE_PIN", "stats manifest %s lists no files"
            % args.stats_manifest)
    merged, prov = {}, []
    for path in paths:
        if not Path(path).is_file() or os.path.getsize(path) == 0:
            die("F1K_GATE_PIN", "per-item stats file MISSING/EMPTY: %s — "
                "the pin never derives from a partial T1 union "
                "(fail-closed; no skipping)" % path)
        triples = []
        try:
            for ln in open(path, encoding="utf-8", errors="strict"):
                parts = ln.split()
                if not parts:
                    continue
                if len(parts) != 3:
                    raise ValueError("non-triple line %r" % ln[:60])
                l, e, c = (int(x) for x in parts)
                triples.append((l, e, c))
        except (ValueError, UnicodeDecodeError) as ex:
            die("F1K_GATE_PIN", "non-conforming stats file %s (%s) — "
                "'<layer> <expert> <count>' triples required "
                "(accum20.stats format [MEASURED]); fail-closed, never "
                "skipped" % (path, ex))
        if not triples:
            die("F1K_GATE_PIN", "stats file %s has no triples" % path)
        for l, e, c in triples:
            merged[(l, e)] = merged.get((l, e), 0) + c
        prov.append({"file": os.path.basename(path),
                     "sha256": sha256_file(path), "lines": len(triples)})
    # [REV-E 3] NaN --pin-gb would make `used + PER_EXPERT_BYTES >
    # budget` False FOREVER -> an UNBOUNDED pin file (fail-open;
    # measured nan-comparison semantics) — finiteness enforced first.
    budget = _fin(args.pin_gb, "--pin-gb", "F1K_GATE_PIN",
                  lo_open=True) * 1e9
    ranked = sorted(merged.items(), key=lambda kv: (-kv[1], kv[0]))
    out, used = [], 0.0
    for (l, e), c in ranked:
        if used + PER_EXPERT_BYTES > budget:
            break
        used += PER_EXPERT_BYTES
        out.append("%d %d %d" % (l, e, c))
    Path(args.out).write_text("\n".join(out) + "\n")
    derivation = {
        "n_stats_files": len(prov), "per_file": prov,
        # [REV-C, rereview finding 1 nit] the rows digest is NAMED as what
        # it is (a digest of normalized "<file-sha> <basename>" rows), and
        # the manifest FILE's byte sha is recorded separately.
        "manifest_rows_sha256": hashlib.sha256(
            "".join("%s %s\n" % (p["sha256"], p["file"])
                    for p in prov).encode()).hexdigest(),
        "manifest_file_sha256": sha256_file(args.stats_manifest),
        "aggregation": "sum of counts per (layer, expert) over ALL "
                       "per-item T1 stats files [REV-B F1; fail-closed "
                       "on any missing/empty/malformed file]"}
    Path(str(args.out) + ".derivation.json").write_text(
        json.dumps(derivation, indent=2))
    print(json.dumps({"pin_file": args.out, "experts": len(out),
                      "gb_used": round(used / 1e9, 2), "pin_gb": args.pin_gb,
                      "derivation": derivation,
                      "sha256": sha256_file(args.out)}))
    return 0


# ---------------------------------------------------------------------------
# collect: on-VM merge of timing results -> gate-inputs.json (NO verdict)
# ---------------------------------------------------------------------------
def _read_sample_results(directory, *, phase, expected_ids):
    """Read one atomic JSON file per expected sample; reject partial sets."""
    if phase not in ("t1", "t2"):
        die("F1K_GATE_COLLECT", "invalid timing phase %r" % phase)
    expected = list(expected_ids)
    if not expected or any(not isinstance(sid, str) or not sid
                           for sid in expected) \
            or len(expected) != len(set(expected)):
        die("F1K_GATE_COLLECT", "%s expected sample ids are malformed or "
            "duplicated" % phase.upper())
    root = Path(directory) if directory else None
    if root is None or not root.is_dir():
        die("F1K_GATE_COLLECT", "%s timing result directory missing: %r"
            % (phase.upper(), directory))

    parsed = []
    for path in sorted(root.glob("*.json"), key=lambda p: p.name):
        if not path.is_file():
            die("F1K_GATE_COLLECT", "%s timing result is not a regular "
                "file: %s" % (phase.upper(), path))
        try:
            with path.open(encoding="utf-8") as handle:
                record = json.load(handle)
        except (OSError, UnicodeError, ValueError) as exc:
            die("F1K_GATE_COLLECT", "%s malformed timing result %s: %s"
                % (phase.upper(), path, exc))
        if not isinstance(record, dict):
            die("F1K_GATE_COLLECT", "%s malformed timing result %s: "
                "record is not an object" % (phase.upper(), path))
        sid = record.get("sample_id")
        if not isinstance(sid, str) or not sid:
            die("F1K_GATE_COLLECT", "%s malformed timing result %s: "
                "sample_id must be a nonempty string"
                % (phase.upper(), path))
        parsed.append((path, record))

    seen = set()
    duplicates = set()
    for _, record in parsed:
        sid = record["sample_id"]
        if sid in seen:
            duplicates.add(sid)
        seen.add(sid)
    if duplicates:
        die("F1K_GATE_COLLECT", "%s duplicate timing sample id(s): %s"
            % (phase.upper(), ",".join(sorted(duplicates))))

    out = {}
    for path, record in parsed:
        sid = record["sample_id"]
        expected_name = "%s-%s.json" % (phase, sid)
        if path.name != expected_name:
            die("F1K_GATE_COLLECT", "%s filename/sample_id disagreement: "
                "%s contains %r (expected filename %s)"
                % (phase.upper(), path.name, sid, expected_name))
        if record.get("phase") != phase:
            die("F1K_GATE_COLLECT", "%s timing result %s records phase %r"
                % (phase.upper(), path, record.get("phase")))
        seconds = record.get("s")
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) \
                or not math.isfinite(seconds) or seconds <= 0:
            die("F1K_GATE_COLLECT", "%s timing result %s has invalid s=%r; "
                "require a finite value > 0"
                % (phase.upper(), path, seconds))
        timer_n = record.get("timer_n")
        if isinstance(timer_n, bool) or not isinstance(timer_n, int) \
                or timer_n < 1:
            die("F1K_GATE_COLLECT", "%s timing result %s has invalid "
                "timer_n=%r" % (phase.upper(), path, timer_n))
        boot_id = record.get("boot_id")
        if not isinstance(boot_id, str) or not boot_id.strip() \
                or boot_id != boot_id.strip():
            die("F1K_GATE_COLLECT", "%s timing result %s has invalid "
                "boot_id=%r" % (phase.upper(), path, boot_id))
        pin_evidence = record.get("pin_evidence")
        if phase == "t2" and not isinstance(pin_evidence, str):
            die("F1K_GATE_COLLECT", "T2 timing result %s has invalid or "
                "missing pin_evidence" % path)
        if pin_evidence is not None and not isinstance(pin_evidence, str):
            die("F1K_GATE_COLLECT", "%s timing result %s has non-string "
                "pin_evidence" % (phase.upper(), path))
        out[sid] = record

    expected_set = set(expected)
    extra = sorted(set(out) - expected_set)
    if extra:
        die("F1K_GATE_COLLECT", "%s timing has unexpected sample id(s): %s"
            % (phase.upper(), ",".join(extra)))
    missing = [sid for sid in expected if sid not in out]
    if missing:
        die("F1K_GATE_COLLECT", "%s timing missing for %s (fail-closed: "
            "partial samples never project)"
            % (phase.upper(), ",".join(missing)))
    boots = {record["boot_id"] for record in out.values()}
    if len(boots) > 1:
        die("F1K_GATE_COLLECT", "%s timing mixes boot_id values: %s"
            % (phase.upper(), ",".join(sorted(boots))))
    return out


def cmd_collect(args):
    sample = json.loads(Path(args.sample).read_text())
    tokdir = Path(args.tokens)
    counts = json.loads((tokdir / "token-counts.json").read_text())
    t1 = _read_sample_results(
        args.t1, phase="t1", expected_ids=sample["t1_sample_ids"])
    t2_ids = [entry["sample_id"] for entry in sample["entries"]]
    t2 = _read_sample_results(args.t2, phase="t2", expected_ids=t2_ids)
    t1_boot = next(iter({record["boot_id"] for record in t1.values()}))
    t2_boot = next(iter({record["boot_id"] for record in t2.values()}))
    if t1_boot != t2_boot:
        die("F1K_GATE_COLLECT", "T1 boot_id %s != T2 boot_id %s; timing "
            "phases from different boots must never be combined"
            % (t1_boot, t2_boot))
    # [REV-B F2] STRUCTURAL manifest-vs-model consistency (the class of
    # defect gate-fix review #3 found): for every sampled text the score
    # manifest's ctxlen + contlen (= the token count the engine actually
    # processes) must EQUAL the projection model's Tp for that item.
    mandir = Path(args.sample).parent
    for e in sample["entries"]:
        mpath = mandir / ("sample-%s.score" % e["sample_id"])
        if not mpath.is_file():
            die("F1K_GATE_COLLECT", "score manifest missing: %s" % mpath)
        parts = mpath.read_text(encoding="utf-8").split()
        ctx, cont, ids = int(parts[0]), int(parts[1]), parts[2:]
        if ctx + cont != e["Tp"] or len(ids) != e["Tp"] \
                or cont != CONT_TOKENS:
            die("F1K_GATE_COLLECT",
                "%s manifest measures ctx+cont=%d (ids %d) but the "
                "projection model labels it Tp=%d — the timing "
                "observation would be mislabeled by a continuation "
                "(REV-B F2 structural check; fail-closed)"
                % (e["sample_id"], ctx + cont, len(ids), e["Tp"]))
    # compact per-prefill inventory for the control-box projection
    inv_t = [[e["pop"], e["m"], e["T"] + CONT_TOKENS] for e in
             (json.loads(l) for l in open(tokdir / "tokens-full.jsonl"))]
    try:
        rate_decimal = f1k_ops.canonical_decimal(args.rate, field="--rate")
    except (TypeError, ValueError) as exc:
        die("F1K_GATE_COLLECT", str(exc))
    # The float remains the compatibility/projection value, derived only
    # after the exact operator spelling has been canonicalized and retained.
    rate = _fin(rate_decimal, "--rate", "F1K_GATE_COLLECT", lo_open=True)
    gate_inputs = {
        "schema": SCHEMA + ":gate-inputs",
        "token_counts": counts,
        # [REV-C F5ii] the per-item token sidecar is BOUND into the gate
        # artifact by byte sha — the driver's Add7Model later refuses any
        # sidecar whose bytes do not hash to the artifact-recorded value
        # (a self-consistent but non-licensed bundle can no longer pass).
        "tokens_full_sha256": sha256_file(tokdir / "tokens-full.jsonl"),
        "timing_sample": {k: sample[k] for k in
                          ("seed", "rule", "realized_bin_edges_Tp", "n",
                           "t1_sample_ids", "entries")},
        "t2_pinned_runs": [t2[e["sample_id"]] for e in sample["entries"]],
        "t1_unpinned_runs": sorted(t1.values(),
                                   key=lambda r: r["sample_id"]),
        "inventory_t": inv_t,
        "rate_usd_per_hour": rate,             # derived float [REV-E 3]
        "rate_usd_per_hour_decimal": rate_decimal,
        "rate_source": "coordinator-recorded assigned SPOT rate "
                       "(KOT_F1K_SPOT_RATE) — the construction rate, NOT "
                       "the on-demand bring-up VM's rate; rate.usd_per_hour_"
                       "decimal is authoritative for licensing comparison, "
                       "and rate.usd_per_hour is its derived compatibility/"
                       "projection float",
        "pin": {"pin_file_sha256": args.pin_sha or None,
                "pin_gb": _fin(args.pin_gb, "--pin-gb",
                               "F1K_GATE_COLLECT", lo_open=True)
                if args.pin_gb else None,              # [REV-E 3]
                "pin_file_path": args.pin_path or None,
                "regime": args.pin_regime,
                "derivation": json.loads(Path(args.pin_derivation)
                                         .read_text(encoding="utf-8"))
                if args.pin_derivation else None,
                "role": "campaign pin for the WHOLE campaign [REV-C/"
                        "REV-E]: the LICENSED bring-up pin runs "
                        "construction AND pilot/main. Full-corpus "
                        "re-derivation is WITHDRAWN (structurally "
                        "impossible through the sha-pinned builder; "
                        "DEFERRED behind bead kernel-of-truth-8cpm); "
                        "there is NO rebind record and NO rebind path — "
                        "the driver refuses a campaign pin whose sha "
                        "differs from this artifact's",
                "note": "derivation + truthful-attestation mechanics: "
                        "F1K-PIN-FILE-FIX.md v5 (cross-reference)"},
        "dump_gate": {"a": args.dump_a, "b": args.dump_b, "c": args.dump_c,
                      "functional_inertness": args.functional,
                      "rule": "recorded worker/runner statuses; the license "
                              "requires the literal string PASS on all four "
                              "(v3-review: RUNNER-CONFIRM-REQUIRED scaffolds "
                              "must never license)"},
    }
    Path(args.out).write_text(json.dumps(gate_inputs, indent=2))
    print("gate-inputs written: %s (%d T2 runs, %d T1 runs, regime %s)"
          % (args.out, len(t2), len(t1), args.pin_regime))
    return 0


# ---------------------------------------------------------------------------
# project: the mechanical GREEN/STOP verdict (control box, via f1k_gcp.py)
# ---------------------------------------------------------------------------
def _isotonic(knots):
    """PAVA pooling (weighted by n) of (T, s, se, n) knots so s is
    non-decreasing in T; repairs recorded."""
    pools = [dict(k, pool=[k["stratum"]]) for k in knots]
    repaired = []
    i = 0
    while i < len(pools) - 1:
        if pools[i]["s"] > pools[i + 1]["s"] + 1e-12:
            a, b = pools[i], pools[i + 1]
            n = a["n"] + b["n"]
            merged = {"T": (a["T"] * a["n"] + b["T"] * b["n"]) / n,
                      "s": (a["s"] * a["n"] + b["s"] * b["n"]) / n,
                      "se": max(a["se"], b["se"]), "n": n,
                      "stratum": "%s+%s" % (a["stratum"], b["stratum"]),
                      "pool": a["pool"] + b["pool"]}
            repaired.append(merged["stratum"])
            pools[i:i + 2] = [merged]
            i = max(0, i - 1)
        else:
            i += 1
    return pools, repaired


# ---- KOT-ADD7-SHARED-BEGIN ------------------------------------------------
# [REV-C F5i, F1K-BRINGUP-GATE-FIX.md SSC] ONE projection-model
# implementation, byte-identical in poc/gcp/f1k_bringup_gate.py and
# poc/glm52-probe/f1k-harness/f1k_driver.py. Each copy is verified at
# runtime: block sha256 == the in-file ADD7_SRC_SHA256 constant AND (at
# consumption) == the licensed gate artifact's model_bundle.add7_src_sha256
# — drift in EITHER copy is a refusal, never a silent second
# implementation. Semantics (frozen, fix memo SS2.6): piecewise-linear in T
# over isotonic knots; below the min knot central/hi are CONSTANT
# (cap-conservative) and the lo band extrapolates floored at
# floor_frac*s(minknot); above the max sampled knot: Add7RangeError
# (extrapolation above the frozen sample is FORBIDDEN — the campaign max-T
# text is in the sample by construction).
class Add7RangeError(ValueError):
    """T above the max sampled knot — never extrapolated."""


def add7_interp(knots, sfield, t, below="const", floor_frac=0.35):
    ts = [k["T"] for k in knots]
    ss = [k[sfield] for k in knots]
    if t > ts[-1] + 1e-9:
        raise Add7RangeError(
            "T=%.0f above max sampled knot %.0f" % (t, ts[-1]))
    if t <= ts[0]:
        if below == "const" or len(ts) < 2:
            return ss[0]
        slope = (ss[1] - ss[0]) / max(1e-9, ts[1] - ts[0])
        return max(floor_frac * ss[0], ss[0] - slope * (ts[0] - t))
    for i in range(len(ts) - 1):
        if t <= ts[i + 1]:
            frac = (t - ts[i]) / max(1e-9, ts[i + 1] - ts[i])
            return ss[i] + frac * (ss[i + 1] - ss[i])
    return ss[-1]


def add7_block_sha256(path):
    """sha256 over the exact lines BETWEEN the shared-block markers
    (marker lines excluded); None when the markers are absent/ambiguous."""
    lines = open(path, encoding="utf-8").read().split("\n")
    beg = [i for i, l in enumerate(lines)
           if l.startswith("# ---- KOT-ADD7-SHARED-BEGIN")]
    end = [i for i, l in enumerate(lines)
           if l.startswith("# ---- KOT-ADD7-SHARED-END")]
    if len(beg) != 1 or len(end) != 1 or end[0] <= beg[0]:
        return None
    body = "\n".join(lines[beg[0] + 1:end[0]])
    return hashlib.sha256(body.encode("utf-8")).hexdigest()
# ---- KOT-ADD7-SHARED-END --------------------------------------------------


ADD7_SRC_SHA256 = "9d3e1bc76f8506d99a29b0465af2c063b32ba8d726e7ec2c6a65e3c596260353"
#   [REV-C F5i] frozen sha256 of the KOT-ADD7-SHARED block body (both
#   copies must hash to THIS value; project() refuses to emit an artifact
#   from a drifted copy, and the driver refuses to consume one).


def _interp(knots, sfield, t, below):
    """Thin gate-side wrapper over the SHARED add7_interp (ONE model
    implementation, KOT-ADD7-SHARED block [REV-C F5i]) — converts the
    above-max-knot Add7RangeError into the gate's fail-closed die()."""
    try:
        return add7_interp(knots, sfield, t, below,
                           floor_frac=FLOOR_EXTRAP_MIN_FRAC)
    except Add7RangeError:
        die("F1K_GATE_MODEL", "T=%.0f above max sampled knot %.0f — "
            "extrapolation above the sample is FORBIDDEN (the campaign "
            "max-T prefill must be in the sample)"
            % (t, max(k["T"] for k in knots)))


def build_knots(inputs):
    ent = {e["sample_id"]: e for e in inputs["timing_sample"]["entries"]}
    strata = {}
    for r in inputs["t2_pinned_runs"]:
        e = ent[r["sample_id"]]
        sid = "max" if e["why"] == "campaign-max-T" else "bin%d" % e["bin"]
        strata.setdefault(sid, []).append((e["Tp"], float(r["s"])))
    knots = []
    for sid, pts in strata.items():
        n = len(pts)
        tbar = sum(t for t, _ in pts) / n
        sbar = sum(s for _, s in pts) / n
        sd = (math.sqrt(sum((s - sbar) ** 2 for _, s in pts) / (n - 1))
              if n > 1 else None)
        knots.append({"stratum": sid, "T": tbar, "s": sbar, "n": n,
                      "sd": sd, "se": (sd / math.sqrt(n)) if sd else None})
    fallback = max((k["se"] for k in knots if k["se"] is not None),
                   default=0.0)
    for k in knots:
        if k["se"] is None:
            k["se"] = fallback   # [STIPULATED] singleton knots borrow the
            k["sd"] = None       # worst measured stratum SE (conservative)
    knots.sort(key=lambda k: k["T"])
    pooled, repaired = _isotonic(knots)
    return knots, pooled, repaired


def _driver_pin_grammar():
    """[REV-B F3] BIND to the LANDED driver's pin-engagement evidence
    grammar (f1k_driver.py PIN_ARMED_RE + PIN_DISABLED_MARKERS, the
    ASM-2513 machinery landed at 2574c82b) — the gate never re-invents a
    parallel evidence format. The banner WORDING stays fetch-grade
    [ASM-1971]: if the real engine's pin report differs, the runner aligns
    the DRIVER regex in one recorded run-log amendment and this check
    follows automatically (one grammar, two consumers). Import fail-closed."""
    import importlib.util
    p = Path(__file__).resolve().parents[1] / "glm52-probe" \
        / "f1k-harness" / "f1k_driver.py"
    if not p.is_file():
        die("F1K_GATE_PIN_EVIDENCE", "landed driver not found at %s — "
            "cannot bind the pin-engagement grammar" % p)
    spec = importlib.util.spec_from_file_location("kot_f1k_driver_pin", p)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as ex:                                # noqa: BLE001
        die("F1K_GATE_PIN_EVIDENCE", "driver import failed (%s) — the "
            "engagement grammar is unavailable; fail closed" % ex)
    return mod.PIN_ARMED_RE, mod.PIN_DISABLED_MARKERS


def check_engagement(inputs):
    """[REV-B F3] POSITIVE pin-engagement evidence per T2 run, mirroring
    the landed check_pin_engagement coherence rules: an armed banner must
    exist in the run's recorded stderr evidence, pinned>=1 experts, used
    GiB > 0, used <= budget*1.01, budget == the bound PIN_GB (1%), source
    == the bound pin path; any disabled marker refuses. Returns (ok,
    problems)."""
    armed_re, disabled_markers = _driver_pin_grammar()
    pin = inputs["pin"]
    gb = pin.get("pin_gb")
    path = pin.get("pin_file_path")
    problems = []
    for r in inputs["t2_pinned_runs"]:
        ev = r.get("pin_evidence") or ""
        sid = r.get("sample_id", "?")
        bad = [m for m in disabled_markers if m in ev]
        if bad:
            problems.append("%s: pinning DISABLED marker %s" % (sid, bad))
            continue
        m = armed_re.search(ev)
        if not m:
            problems.append("%s: no armed banner" % sid)
            continue
        n_pinned, gb_used = int(m.group(1)), float(m.group(2))
        gb_budget, src = float(m.group(3)), m.group(4)
        if n_pinned < 1 or not gb_used > 0.0:
            problems.append("%s: incoherent counters (n=%d, %.3f GiB)"
                            % (sid, n_pinned, gb_used))
        elif gb is None or abs(gb_budget - gb) > 0.01 * max(1.0, gb) \
                or gb_used > gb_budget * 1.01:
            problems.append("%s: budget %.3f/used %.3f vs bound PIN_GB=%r"
                            % (sid, gb_budget, gb_used, gb))
        elif path and src != path:
            problems.append("%s: armed from %r != bound pin %r"
                            % (sid, src, path))
    return not problems, problems


def project(inputs, frozen, replace=False, out_path=None):
    tc = inputs["token_counts"]
    if tc["tokenizer"]["mode"] != "REAL" and not inputs.get("_allow_mock"):
        die("F1K_GATE_MOCK", "token counts are MOCK — a mock gate never "
            "licenses spend (selftest/dry-run only)")
    # [REV-C F5i] the emitting copy of the shared model must BE the frozen
    # model — a drifted block never emits a license artifact.
    own_add7 = add7_block_sha256(__file__)
    if own_add7 != ADD7_SRC_SHA256:
        die("F1K_GATE_MODEL", "this file's KOT-ADD7-SHARED block hashes to "
            "%r != the frozen ADD7_SRC_SHA256 %s — the shared projection "
            "model drifted; refuse to emit an artifact"
            % (own_add7, ADD7_SRC_SHA256[:16]))
    # [REV-C F5ii] the artifact must BIND its per-item token sidecar.
    if not inputs.get("tokens_full_sha256"):
        die("F1K_GATE_MODEL", "gate-inputs carry no tokens_full_sha256 — "
            "a /2 artifact binds its token sidecar by byte sha "
            "(re-run the REV-C collect); fail closed")
    raw_knots, knots, repaired = build_knots(inputs)
    rate = inputs["rate_usd_per_hour"]
    raw_rate_decimal = inputs.get("rate_usd_per_hour_decimal")
    if raw_rate_decimal is None:
        # Resume compatibility for pre-finding-1 gate inputs. Source digits
        # already lost to their JSON float cannot be recovered, but the
        # artifact still gets a canonical, exponent-free comparison field.
        raw_rate_decimal = str(rate)
    try:
        rate_decimal = f1k_ops.canonical_decimal(
            raw_rate_decimal, field="rate_usd_per_hour_decimal")
    except (TypeError, ValueError) as exc:
        die("F1K_GATE_MODEL", "invalid rate_usd_per_hour_decimal: %s" % exc)
    derived_rate = _fin(rate_decimal, "rate_usd_per_hour_decimal",
                        "F1K_GATE_MODEL", lo_open=True)
    if rate != derived_rate:
        die("F1K_GATE_MODEL", "rate_usd_per_hour %r is not the float "
            "derived from rate_usd_per_hour_decimal %r"
            % (rate, rate_decimal))
    reserve_h = RESERVE_USD / rate
    dg = inputs.get("dump_gate") or {}
    inv = list(inputs["inventory_t"])
    if replace:
        inv = inv + [[p, M_REPLACE, t] for p, m, t in inv
                     if p == "main-tmpl" and m == M_MAIN_TMPL]
    prefills = sum(m for _, m, _ in inv)

    def total_h(sfield, below):
        by_pop, s_tot = {}, 0.0
        for pop, m, t in inv:
            s = m * _interp(knots, sfield, t, below)
            s_tot += s
            by_pop[pop] = by_pop.get(pop, 0.0) + s
        return s_tot / 3600.0, {p: round(v / 3600.0, 1)
                                for p, v in sorted(by_pop.items())}
    for k in knots:
        k["s_hi"] = k["s"] + SE_MULT * k["se"]
        k["s_lo"] = max(0.0, k["s"] - SE_MULT * k["se"])
    h_c, by_pop = total_h("s", "const")
    h_hi, _ = total_h("s_hi", "const")
    h_lo, _ = total_h("s_lo", "extrap")
    usd_c, usd_hi, usd_lo = (h * rate for h in (h_c, h_hi, h_lo))
    # the per-average comparison the fix retires (audit trail, review #3)
    wmean_t = sum(m * t for _, m, t in inv) / prefills
    naive_h = prefills * _interp(knots, "s", wmean_t, "const") / 3600.0
    f_blend = tc["f_blended"]
    lo_h, hi_h = frozen["instance_hours"]
    lo_u, hi_u = frozen["usd_total"]
    checks = {
        "rate_in_window":
            frozen["rate_window"][0] <= rate <= frozen["rate_window"][1],
        "f_le_threshold": f_blend <= F_THRESHOLD,
        "central_hours_in_window":
            lo_h <= h_c and h_c + reserve_h <= hi_h,
        "central_usd_in_window":
            lo_u <= usd_c and usd_c + RESERVE_USD <= hi_u,
        "hi_band_below_caps":
            h_hi + reserve_h <= hi_h and usd_hi + RESERVE_USD <= hi_u,
        "dump_preconditions_pass":
            all(dg.get(k) == "PASS" for k in ("a", "b", "c")),
        "functional_inertness_pass":
            dg.get("functional_inertness") == "PASS",
        "lo_band_above_floors": h_lo >= lo_h and usd_lo >= lo_u,
        "prefills_ge_min": prefills >= frozen["prefills_min"],
        "tokenizer_real": tc["tokenizer"]["mode"] == "REAL"
            or bool(inputs.get("_allow_mock")),
        # [REV-B F3, gate-fix review #4] shape (i) ENFORCED: the gate
        # REFUSES regime "unpinned" — shape (ii) was REJECTED on measured
        # arithmetic (SSA3.5: unpinned 225.2 s vs the [75.7,160.7] s
        # admissible window), so an unpinned regime can never license.
        "pin_regime_pinned":
            inputs["pin"]["regime"] == "pinned-bringup",
    }
    # [REV-B F3] pin-ENGAGEMENT evidence conjunct (bound to the landed
    # driver grammar): only meaningful under the pinned regime; a refused
    # regime already STOPs above.
    if checks["pin_regime_pinned"]:
        eng_ok, eng_problems = check_engagement(inputs)
    else:
        eng_ok, eng_problems = False, ["regime %r never licenses"
                                       % (inputs["pin"]["regime"],)]
    checks["pin_engagement_pass"] = eng_ok
    reasons = []
    if not checks["f_le_threshold"]:
        reasons.append("measured blended f %.4f > %.2f — §7 STOP branch: "
                       "the contingent <=$300 path is a MAINTAINER re-freeze "
                       "decision, never autonomous" % (f_blend, F_THRESHOLD))
    if not checks["rate_in_window"]:
        reasons.append("rate %.4f outside frozen window %s"
                       % (rate, frozen["rate_window"]))
    if not checks["central_hours_in_window"]:
        reasons.append("central projection %.1f h (+%.1f h reserve = %.1f) "
                       "outside [%.1f, %.1f] RESERVE-INCLUSIVE cap side"
                       % (h_c, reserve_h, h_c + reserve_h, lo_h, hi_h))
    if not checks["central_usd_in_window"]:
        reasons.append("central projection $%.2f (+$%.2f reserve = $%.2f) "
                       "outside [$%.0f, $%.0f] RESERVE-INCLUSIVE cap side"
                       % (usd_c, RESERVE_USD, usd_c + RESERVE_USD,
                          lo_u, hi_u))
    if not checks["hi_band_below_caps"]:
        reasons.append("+%gSE projection %.1f h / $%.2f breaches a "
                       "RESERVE-INCLUSIVE cap (%.0f h - %.1f h reserve / "
                       "$%.0f - $%.0f reserve)"
                       % (SE_MULT, h_hi, usd_hi, hi_h, reserve_h,
                          hi_u, RESERVE_USD))
    if not checks["dump_preconditions_pass"]:
        reasons.append("dump bring-up preconditions not all PASS "
                       "(a=%r b=%r c=%r) — RUNNER-CONFIRM-REQUIRED "
                       "scaffolds never license (v3-review); the runner "
                       "confirms on-box, writes PASS, and re-runs collect"
                       % (dg.get("a"), dg.get("b"), dg.get("c")))
    if not checks["functional_inertness_pass"]:
        reasons.append("functional inert-by-default gate not PASS (%r)"
                       % (dg.get("functional_inertness"),))
    if not checks["lo_band_above_floors"]:
        reasons.append("-%gSE projection %.1f h / $%.2f breaches a floor "
                       "(%.1f h / $%.0f) — an honest ledger cannot validate"
                       % (SE_MULT, h_lo, usd_lo, lo_h, lo_u))
    if not checks["prefills_ge_min"]:
        reasons.append("prefills %d < %d" % (prefills,
                                             frozen["prefills_min"]))
    if not checks["pin_regime_pinned"]:
        reasons.append("pin regime %r REFUSED — shape (i) is the decided "
                       "and ONLY licensable regime (ASM-2515/ASM-2516; "
                       "shape (ii) rejected on measured arithmetic); an "
                       "underivable pin is a mandatory maintainer surface, "
                       "never an unpinned license"
                       % (inputs["pin"]["regime"],))
    if not checks["pin_engagement_pass"]:
        reasons.append("pin-ENGAGEMENT evidence failed for the bound pin "
                       "sha/PIN_GB (%s) — an armed banner per T2 run is "
                       "REQUIRED (landed ASM-2513 grammar); a licensed "
                       "timing basis is never taken on trust"
                       % "; ".join(eng_problems[:4]))
    verdict = "GREEN" if all(checks.values()) else "STOP"
    art = {
        "schema": SCHEMA,
        "verdict": verdict,
        "reasons": reasons,
        "checks": checks,
        "f": {"blended": f_blend, "threshold": F_THRESHOLD,
              "branch": "LE" if f_blend <= F_THRESHOLD else "GT",
              "per_population": {p: v["f"] for p, v in
                                 tc["populations"].items()},
              "convention": tc["f_convention"]},
        "tokenizer": tc["tokenizer"],
        "corpus_sha256": tc["corpus_sha256"],
        "sample": inputs["timing_sample"],
        "model": {
            "type": "monotone-piecewise-linear s_hat(T) over measured "
                    "stratum knots; below min knot: central/hi CONSTANT, "
                    "lo linear-extrapolated floored at %.2f*s(minknot); "
                    "above max knot: FAIL-CLOSED" % FLOOR_EXTRAP_MIN_FRAC,
            "knots_raw": raw_knots,
            "knots_isotonic": [{k: v for k, v in kn.items()
                                if k != "pool"} for kn in knots],
            "isotonic_repairs": repaired,
            "se_rule": "+-%g SE band; caps tested at +SE, floors at -SE, "
                       "windows at central" % SE_MULT,
            "cont_tokens_addend": CONT_TOKENS,
        },
        "pin": inputs["pin"],
        # [REV-C F5ii] model-bundle binding: EVERYTHING the driver's
        # Add7Model consumes is bound here by sha — the shared model
        # source AND the per-item token sidecar. The driver verifies its
        # own block + the sidecar bytes against THESE recorded values
        # (plus corpus/pin/rate identity from the sibling fields).
        "model_bundle": {
            "add7_src_sha256": ADD7_SRC_SHA256,
            "tokens_full_sha256": inputs["tokens_full_sha256"],
            "rule": "consumption REQUIRES: schema == %s, verdict GREEN, "
                    "driver shared-block sha == add7_src_sha256, sidecar "
                    "bytes sha == tokens_full_sha256, corpus shas == "
                    "corpus_sha256 (driver-side files), config pin sha == "
                    "pin.pin_file_sha256, config rate decimal == "
                    "rate.usd_per_hour_decimal (the authoritative "
                    "licensing comparison; rate.usd_per_hour is its "
                    "derived compatibility/projection float) "
                    "[REV-C F5ii]" % SCHEMA},
        "pin_engagement": {
            "pass": eng_ok, "problems": eng_problems,
            "rule": "per-T2-run armed-banner evidence parsed with the "
                    "LANDED driver grammar (PIN_ARMED_RE/ASM-2513; "
                    "wording fetch-grade ASM-1971, one grammar for both "
                    "consumers): pinned>=1, used GiB>0, used<=budget*1.01, "
                    "budget==bound PIN_GB (1%), source==bound pin path; "
                    "regime unpinned REFUSED outright [REV-B F3]"},
        "rate": {"usd_per_hour": rate,
                 "usd_per_hour_decimal": rate_decimal,
                 "source": inputs["rate_source"]},
        "projection": {
            "prefills": prefills,
            "replace_included": replace,
            "instance_hours": {"central": round(h_c, 1),
                               "hi": round(h_hi, 1), "lo": round(h_lo, 1)},
            "usd_total": {"central": round(usd_c, 2),
                          "hi": round(usd_hi, 2), "lo": round(usd_lo, 2)},
            "blended_s_per_prefill_central":
                round(h_c * 3600.0 / prefills, 2),
            "hours_by_population_central": by_pop,
            "per_average_naive_hours_RETIRED": round(naive_h, 1),
            "per_average_divergence_pct":
                round(100.0 * (h_c - naive_h) / naive_h, 2),
            "reserve": {"usd": RESERVE_USD,
                        "hours_at_rate": round(reserve_h, 2),
                        "rule": "caps reserve-inclusive; floors "
                                "compute-only [STIPULATED, fix memo SSA2]",
                        "usd_central_with_reserve":
                            round(usd_c + RESERVE_USD, 2),
                        "hours_central_with_reserve":
                            round(h_c + reserve_h, 1)},
        },
        "dump_gate": dg,
        "thresholds": frozen,
        "semantics": "plan §7: GREEN -> construction proceeds WITHOUT "
                     "re-surfacing (standing authorization); STOP -> "
                     "MANDATORY surface to the maintainer with salvage "
                     "options; never autonomous re-freeze",
    }
    if out_path:
        Path(out_path).write_text(json.dumps(art, indent=2))
    return art


# ---------------------------------------------------------------------------
# checkpoint: construction EARLY-ABORT re-projection ([REV-B F3, ASM-2516])
# ---------------------------------------------------------------------------
CHECKPOINT_SCHEDULE = (240, 1056, 2304)
#   [REV-C F3; amends ASM-2516 item (4)'s {200,1024,2304} PRE-REGISTRATION
#   — ASM-2517] n_done milestones ALIGNED TO THE OBSERVABLE GRANULARITY:
#   the SHA-PINNED builder (build_carriers.py, frozen-record generator
#   pin) runs ONE 48-pass engine batch per concept and checkpoints per
#   concept (concept-%03d.json), so construction progress is mechanically
#   observable ONLY at 48-pass boundaries. 240/1056/2304 = 5/22/48 of the
#   96 concepts. First exposure 240 x ~137.2 s ~ 9.1 h ~ $1.59 at the
#   f=1.45 row [EXTRAPOLATED].
CHECKPOINT_RATIO_MAX = 10.0               # sanity bound on realized/predicted


def checkpoint_eval(gate, tokens_path, n_done, elapsed, n_start=0,
                    out=None):
    """[REV-B F3 / REV-C] Construction EARLY-ABORT checkpoint. HONESTY
    (gate-fix review #4): the gate's +-1SE band bounds SAMPLING error of
    the chosen 30-text sample ONLY — NOT selection bias, NOT unseen-tail
    behaviour; a pin can pass the 30-item gate yet underperform over the
    4,608 construction items. This checkpoint bounds that residual
    mechanically: at n_done in CHECKPOINT_SCHEDULE (a FROZEN schedule —
    any other n_done is REFUSED, never a movable goalpost [REV-C,
    rereview #3]), re-project the WHOLE campaign with the LICENSED gate
    model re-levelled by the realized construction ratio (elapsed seconds
    / model-predicted seconds for manifest-order construction items
    n_start..n_done) and STOP (exit 2) if a reserve-inclusive cap
    breaches at central OR +1SE. n_start (REV-C, 48-multiple) supports a
    RESUMED construction: cached concepts contribute no elapsed time, so
    both the elapsed and the prediction cover exactly this session's
    span. INVOKED BY the REV-C construction-guard in-process (the SAME
    code as the CLI). LEDGER BINDING: the artifact's realized figures ARE
    the cost basis `config-cost` transfers into the campaign config —
    the LANDED Ledger's REQUIRED fail-closed inputs (ASM-2513) — and a
    breach here never reaches a pilot spawn."""
    if gate.get("schema") != SCHEMA:
        die("F1K_GATE_CKPT", "gate artifact schema %r != %s — checkpoints "
            "consume only a /2 model-bundle-bound artifact [REV-C]"
            % (gate.get("schema"), SCHEMA))
    if gate.get("verdict") != "GREEN":
        die("F1K_GATE_CKPT", "gate artifact verdict %r — checkpoints only "
            "run inside a GREEN license" % gate.get("verdict"))
    knots = sorted(gate["model"]["knots_isotonic"], key=lambda k: k["T"])
    cont = gate["model"]["cont_tokens_addend"]
    rate = gate["rate"]["usd_per_hour"]
    thr = gate["thresholds"]
    reserve_h = RESERVE_USD / rate
    entries = [json.loads(l) for l in open(tokens_path, encoding="utf-8")]
    cons = [e for e in entries if e["pop"] == "construction"]
    if n_done not in CHECKPOINT_SCHEDULE:
        die("F1K_GATE_CKPT", "n_done %d is NOT on the frozen checkpoint "
            "schedule %s — the schedule is part of the freeze (ASM-2517); "
            "an arbitrary n_done is refused, never accepted"
            % (n_done, list(CHECKPOINT_SCHEDULE)))
    if not 1 <= n_done <= len(cons):
        die("F1K_GATE_CKPT", "n_done %d outside [1, %d]"
            % (n_done, len(cons)))
    if not (0 <= n_start < n_done and n_start % 48 == 0):
        die("F1K_GATE_CKPT", "n_start %d invalid: must be a 48-multiple "
            "(concept boundary) in [0, n_done)" % n_start)
    if elapsed <= 0:
        die("F1K_GATE_CKPT", "elapsed_s must be > 0")
    pred = sum(_interp(knots, "s", e["T"] + cont, "const")
               for e in cons[n_start:n_done])
    ratio = elapsed / pred
    if not 0.0 < ratio <= CHECKPOINT_RATIO_MAX:
        die("F1K_GATE_CKPT", "realized/predicted ratio %.3f outside "
            "(0, %.1f] — model transfer broken; maintainer surface"
            % (ratio, CHECKPOINT_RATIO_MAX))
    for k in knots:
        k["s_hi"] = k["s"] + SE_MULT * k["se"]
    sec_c = sum(e["m"] * _interp(knots, "s", e["T"] + cont, "const")
                for e in entries) * ratio
    sec_hi = sum(e["m"] * _interp(knots, "s_hi", e["T"] + cont, "const")
                 for e in entries) * ratio
    h_c, h_hi = sec_c / 3600.0, sec_hi / 3600.0
    usd_c, usd_hi = h_c * rate, h_hi * rate
    hi_h, hi_u = thr["instance_hours"][1], thr["usd_total"][1]
    breach = [msg for cond, msg in (
        (h_c + reserve_h > hi_h, "central hours %.1f + reserve" % h_c),
        (h_hi + reserve_h > hi_h, "+1SE hours %.1f + reserve" % h_hi),
        (usd_c + RESERVE_USD > hi_u, "central $%.2f + reserve" % usd_c),
        (usd_hi + RESERVE_USD > hi_u, "+1SE $%.2f + reserve" % usd_hi),
    ) if cond]
    art = {"schema": SCHEMA + ":construction-checkpoint",
           "n_done": n_done, "n_start": n_start, "elapsed_s": elapsed,
           "predicted_s_first_n": round(pred, 1),
           "realized_over_predicted": round(ratio, 4),
           "reprojection": {
               "instance_hours": {"central": round(h_c, 1),
                                  "hi": round(h_hi, 1)},
               "usd_total": {"central": round(usd_c, 2),
                             "hi": round(usd_hi, 2)},
               "reserve": {"usd": RESERVE_USD,
                           "hours_at_rate": round(reserve_h, 2)}},
           "ledger_basis": {
               "construction_instance_hours_realized_so_far":
                   round(elapsed / 3600.0, 4),
               "usd_construction_so_far":
                   round(elapsed / 3600.0 * rate, 4),
               "rule": "these figures enter the campaign driver's "
                       "cost.{usd_spent_prior, construction_instance_"
                       "hours} — the LANDED Ledger's REQUIRED fail-closed "
                       "basis (ASM-2513)"},
           "verdict": "STOP" if breach else "CONTINUE",
           "breaches": breach,
           "schedule": list(CHECKPOINT_SCHEDULE)}
    if out:
        Path(out).write_text(json.dumps(art, indent=2))
    print(json.dumps(art, indent=2))
    if breach:
        die("F1K_GATE_CKPT", "EARLY-ABORT: reserve-inclusive re-projection "
            "breaches (%s) at n_done=%d, ratio %.3f — kill construction, "
            "mandatory maintainer surface (the remaining spend is "
            "recoverable NOW; it is not after 4,608 passes)"
            % ("; ".join(breach), n_done, ratio))
    return 0


def cmd_checkpoint(args):
    """CLI wrapper; the mechanics live in checkpoint_eval() so the REV-C
    construction-guard invokes EXACTLY the same code in-process."""
    gate = json.loads(Path(args.gate).read_text(encoding="utf-8"))
    try:
        nd, ns_ = int(args.n_done), int(args.n_start or 0)
    except ValueError:
        die("F1K_GATE_CKPT",
            "--n-done/--n-start must be integers [REV-E]")
    return checkpoint_eval(gate, args.tokens, nd,
                           _fin(args.elapsed_s, "--elapsed-s",
                                "F1K_GATE_CKPT",
                                lo_open=True),              # [REV-E 3]
                           n_start=ns_,
                           out=args.out or None)


# ---------------------------------------------------------------------------
# construction-guard: WRAPPER-LEVEL shape-(i) enforcement [REV-C F3]
# ---------------------------------------------------------------------------
# The REV-C fork decision (rereview finding 3): build_carriers.py is
# SHA-PINNED (frozen-record generator pin) and inherits AMBIENT env into
# every engine batch (build_carriers.py:634 `env = dict(os.environ)`, only
# KAE_SCORE popped) — so the licensed pin is enforced at the WRAPPER, the
# builder stays byte-untouched (no seq-4 re-freeze on the critical path):
#   1. the guard BINDS the pin explicitly (gate artifact GREEN + schema /2
#      + byte-sha match), never trusting ambient PIN/PIN_GB;
#   2. it PROVES engagement BEFORE any construction spend with a DUMP-MODE
#      probe: one minimal KAE_DUMP invocation of the SAME engine argv under
#      the SAME env, whose stderr must carry a coherent armed banner under
#      the LANDED driver grammar (ASM-2513) — mode-exact evidence (the
#      banner wording stays fetch-grade ASM-1971: a divergence is aligned
#      in the driver regex once, both consumers follow);
#   3. it launches the builder with EXACTLY that verified env (STATS and
#      the mode knobs popped) — the builder's own env passthrough
#      (:634, verified from the pinned bytes) carries PIN/PIN_GB into all
#      96 engine batches unchanged;
#   4. it runs the FROZEN early-abort checkpoints in-process off the
#      builder's per-concept checkpoint files (the only mechanical
#      progress signal the pinned builder emits), killing the process
#      group on a reserve-inclusive breach (exit 2).
# HONEST RESIDUAL [REV-C]: the builder swallows per-batch engine stderr on
# success, so there is NO per-batch banner evidence — engagement is proved
# at launch (probe) and inherited by argument (byte-verified passthrough),
# not re-observed per batch. Per-batch evidence + per-batch STATS need a
# builder edit = the deferred seq-4 re-freeze (bead kot-*, SSC.3), which is
# NOT on this landing's critical path.
def _verify_gate_for_construction(art, pin_path):
    """Fail-closed licence check shared by guard + config seams. Returns
    (pin_sha, pin_gb) from the artifact after byte-verifying pin_path."""
    if art.get("schema") != SCHEMA:
        die("F1K_GUARD", "gate artifact schema %r != %s — construction "
            "binds only to a /2 model-bundle-bound artifact"
            % (art.get("schema"), SCHEMA))
    if art.get("verdict") != "GREEN":
        die("F1K_GUARD", "gate artifact verdict %r — GREEN is the ONLY "
            "construction license" % art.get("verdict"))
    pin = art.get("pin") or {}
    if pin.get("regime") != "pinned-bringup" \
            or not pin.get("pin_file_sha256") or not pin.get("pin_gb"):
        die("F1K_GUARD", "gate artifact pin block incomplete/unpinned "
            "(%r) — shape (i) requires a bound sha + PIN_GB" % (pin,))
    got = sha256_file(pin_path)
    if got != pin["pin_file_sha256"]:
        die("F1K_GUARD", "pin file %s sha %s != licensed %s — the "
            "construction pin is bound BY BYTES, never by path"
            % (pin_path, got[:16], pin["pin_file_sha256"][:16]))
    mb = art.get("model_bundle") or {}
    own = add7_block_sha256(__file__)
    if own != ADD7_SRC_SHA256 or mb.get("add7_src_sha256") != own:
        die("F1K_GUARD", "shared-model sha mismatch (own %r, frozen %s, "
            "artifact %r) — a drifted model copy neither guards nor "
            "projects" % (own and own[:16], ADD7_SRC_SHA256[:16],
                          (mb.get("add7_src_sha256") or "")[:16]))
    return pin["pin_file_sha256"], float(pin["pin_gb"])


def _probe_engagement(engine_cmd, env, layers, rundir):
    """[REV-C F3.2] DUMP-MODE pin-engagement probe, run BEFORE the first
    construction pass: one minimal KAE_DUMP invocation (4 in-vocab ids,
    slot-0 spans — the exact manifest grammar run_dump writes) under the
    EXACT env the builder will inherit. The stderr must carry a coherent
    armed banner under the LANDED driver grammar; any disabled marker,
    incoherent counter, wrong source path, wrong budget, or nonzero exit
    REFUSES construction — exposure is ONE engine start (~minutes,
    <~$0.01 at the construction rate), never a 4,608-pass campaign."""
    armed_re, disabled_markers = _driver_pin_grammar()
    rundir = Path(rundir)
    rundir.mkdir(parents=True, exist_ok=True)
    man = rundir / "pin-probe.dump-manifest.txt"
    man.write_text("4 15 15 15 15 0 0 0 0\n")
    penv = dict(env)
    penv["KAE_DUMP"] = str(man)
    penv["KAE_DUMP_OUT"] = str(rundir / "pin-probe.kaed")
    penv["KAE_DUMP_LAYERS"] = layers
    penv["KAE_SEED"] = "1"    # probe-only; output discarded, echo unused
    proc = subprocess.run(engine_cmd, env=penv, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, check=False)
    err = proc.stderr.decode("utf-8", "replace")
    problems = []
    if proc.returncode != 0:
        problems.append("probe engine exit %d" % proc.returncode)
    bad = [m for m in disabled_markers if m in err]
    if bad:
        problems.append("pinning DISABLED marker %s" % bad)
    m = armed_re.search(err)
    banner = m.group(0) if m else None
    if not m:
        problems.append("no armed banner on probe stderr")
    else:
        n_pinned, gb_used = int(m.group(1)), float(m.group(2))
        gb_budget, src = float(m.group(3)), m.group(4)
        want_gb = float(env["PIN_GB"])
        if n_pinned < 1 or not gb_used > 0.0:
            problems.append("incoherent counters (n=%d, %.3f GiB)"
                            % (n_pinned, gb_used))
        if abs(gb_budget - want_gb) > 0.01 * max(1.0, want_gb) \
                or gb_used > gb_budget * 1.01:
            problems.append("budget %.3f/used %.3f vs bound PIN_GB=%s"
                            % (gb_budget, gb_used, env["PIN_GB"]))
        if src != env["PIN"]:
            problems.append("armed from %r != bound pin %r"
                            % (src, env["PIN"]))
    evidence = {"schema": SCHEMA + ":construction-pin-probe",
                "engine_argv": list(engine_cmd),
                "pin": env["PIN"], "pin_gb": env["PIN_GB"],
                "mode": "KAE_DUMP (construction mode — mode-exact)",
                "banner": banner, "problems": problems,
                "stderr_tail": err[-2000:],
                "rule": "landed ASM-2513 grammar (PIN_ARMED_RE + disabled "
                        "markers), coherence as check_pin_engagement; "
                        "wording fetch-grade ASM-1971"}
    (rundir / "construction-pin-probe.json").write_text(
        json.dumps(evidence, indent=2))
    if problems:
        die("F1K_GUARD", "pin-engagement PROBE REFUSED construction "
            "(%s) — evidence at %s; fix the pin/engine seam, never "
            "launch unverified" % ("; ".join(problems),
                                   rundir / "construction-pin-probe.json"))
    return evidence


def cmd_guard(args):
    """[REV-C F3 / REV-D / REV-E] construction-guard: verify license
    -> enforce DURABLE terminal-stop authority (append-only events;
    resets single-use, consumed pre-engine-start) -> bind pin env
    explicitly -> PROBE engagement -> launch the UNTOUCHED sha-pinned
    builder with
    the verified env AND the guard-injected engine/tokenizer argv -> run
    the FROZEN checkpoints in-process off the builder's per-concept
    files -> kill on breach.
    usage: ... guard --gate bringup-gate.json --pin campaign-pin.stats
      --engine-cmd '<json argv>' --tokenizer-cmd '<json argv>'
      --layers 3,...,77 --tokens tokens-full.jsonl --rundir <dir>
      --workdir <builder workdir> [--poll-seconds N] -- <builder argv
      WITHOUT --engine-cmd/--tokenizer-cmd: the guard injects them>"""
    import signal
    import time
    art = json.loads(Path(args.gate).read_text(encoding="utf-8"))
    pin_path = Path(args.pin).resolve()
    pin_sha, pin_gb = _verify_gate_for_construction(art, pin_path)
    args.builder = list(args.builder or [])
    if args.builder[:1] == ["--"]:
        args.builder = args.builder[1:]
    if not args.builder:
        die("F1K_GUARD", "no builder argv after '--'")
    # [REV-D 1a / REV-E 1] ENGINE-ARGV UNITY — construct, don't
    # compare: the guard OWNS the engine/tokenizer commands. It PROBES
    # args.engine_cmd and INJECTS the SAME verified values into the
    # builder argv itself (below), so the attested engine and the
    # constructing engine cannot diverge (round-3 verdict 1a). Any
    # operator-supplied value in the builder argv is REFUSED — BEFORE
    # any engine start — and the refusal is ABBREVIATION-AWARE (round-4
    # verdict 1): the pinned builder's argparse resolves unambiguous
    # option prefixes (default allow_abbrev, build_carriers.py:1871), so
    # matching full names only let --engine-c / --engine-cm /
    # --tokenizer-c / --tokenizer-cm (space AND = forms) through. The
    # rule below EQUALS argparse's resolution for THIS parser's option
    # set (pinned bytes a92be3e4, construct subparser; [MEASURED],
    # oracle case 20c): the only other construct options on the
    # "--engine-" stem are --engine-weights-sha/--engine-weights-
    # artifact (diverging at "c" vs "w") and on "--tokenizer-" are
    # --tokenizer-sha/--tokenizer-artifact (diverging at "c" vs
    # "s"/"a"), so ANY prefix of an owned flag of length >= the floor
    # (--engine-c / --tokenizer-c) is unambiguous and argparse-resolves
    # to the owned flag, while EVERY shorter "--engine*"/"--tokenizer*"
    # stem matches >= 3 options and argparse exits 2 (ambiguous-option
    # ERROR — never a silent resolution) [MEASURED].
    for tok in args.builder:
        flag = tok.split("=", 1)[0]
        for opt, floor in (("--engine-cmd", len("--engine-c")),
                           ("--tokenizer-cmd", len("--tokenizer-c"))):
            if len(flag) >= floor and opt.startswith(flag):
                die("F1K_GUARD", "builder argv carries %r — argparse "
                    "would resolve it to %s (abbreviation-aware refusal "
                    "[REV-E]); the guard OWNS the engine/tokenizer "
                    "commands (construct-don't-compare [REV-D]): remove "
                    "it from the builder argv; the guard injects the "
                    "PROBED values itself" % (tok, opt))
    for flag, val in (("--engine-cmd", args.engine_cmd),
                      ("--tokenizer-cmd", args.tokenizer_cmd)):
        try:
            if not isinstance(json.loads(val), list):
                raise ValueError("not a JSON list")
        except ValueError as e:
            die("F1K_GUARD", "guard %s %r is not a JSON argv list (%s) — "
                "the builder requires the same shape (build_carriers.py "
                "construct)" % (flag, val, e))
    poll_s = _fin(args.poll_seconds, "--poll-seconds", "F1K_GUARD",
                  lo_open=True)
    #   [REV-E 3] a NaN --poll-seconds would raise ValueError inside
    #   time.sleep MID-CONSTRUCTION (after the builder launch
    #   [MEASURED]); refused here, before any engine start.
    env = dict(os.environ)
    overridden = {k: env[k] for k in ("PIN", "PIN_GB", "STATS")
                  if k in env}
    for k in ("STATS", "SCORE", "KAE_SCORE", "KAE_DUMP", "KAE_DUMP_OUT",
              "KAE_DUMP_LAYERS"):
        env.pop(k, None)
    #   STATS is POPPED deliberately [REV-C]: with 96 batches sharing one
    #   ambient STATS path (truncate-vs-append fetch-grade ASM-1971) a
    #   single file would hold the LAST batch only — the F1 defect class.
    #   Full-corpus stats need the deferred seq-4 builder re-freeze.
    env["PIN"] = str(pin_path)
    env["PIN_GB"] = ("%g" % pin_gb)
    rundir = Path(args.rundir)
    rundir.mkdir(parents=True, exist_ok=True)
    # [REV-D 1c / REV-E 2] TERMINAL-STOP AUTHORITY, DURABLE: a
    # checkpoint STOP leaves construction-abort.json (breach values
    # recorded) — but a deletable file is not stop authority (round-4
    # verdict 3): the kill path ALSO appends a terminal-abort event to
    # the guard's own append-only construction-events.jsonl (fsynced,
    # file AND dirent — the SAME durability mechanics as the landed
    # SPEND-START sentinel [ASM-2513 v4]), and THIS record — which
    # every guard start reads — is the stop authority: an unconsumed
    # terminal event with a missing abort file is REFUSED, never
    # resumed. Resets are SINGLE-USE: an authorized resume archives the
    # reset (abort-hash + ordinal name) and the abort BEFORE any engine
    # start, so a second use finds nothing. THREAT BOUNDARY
    # [DISCLOSED]: an operator with filesystem access who edits the
    # guard's event state ITSELF is out of scope — the same boundary as
    # the landed sentinel (this defends stop authority against
    # re-invocation and against abort-file deletion, not against a
    # hostile filesystem root).
    events_p = rundir / "construction-events.jsonl"

    def _events():
        if not events_p.exists():
            return []
        return [json.loads(l) for l in
                events_p.read_text(encoding="utf-8").splitlines()
                if l.strip()]

    def _append_event(rec):
        # append + fsync file AND dirent (spend-start-sentinel
        # mechanics [ASM-2513 v4]): a crash must not lose a
        # stop/consume record; no engine start without it.
        try:
            with open(events_p, "a", encoding="utf-8") as ef:
                ef.write(json.dumps(rec, sort_keys=True) + "\n")
                ef.flush()
                os.fsync(ef.fileno())
            dfd = os.open(str(rundir), os.O_RDONLY)
            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)
        except OSError as e:
            die("F1K_GUARD", "cannot durably record %r in %s (%s) — "
                "stop/consume authority must be durable [REV-E]"
                % (rec.get("event"), events_p, e))

    evs = _events()
    terms = [e for e in evs if e.get("event") == "terminal-abort"]
    consumed_ords = {c.get("ordinal") for c in evs
                     if c.get("event") == "reset-consumed"}
    outstanding = [t for t in terms
                   if t.get("ordinal") not in consumed_ords]
    abort_p = rundir / "construction-abort.json"
    reset_p = rundir / "construction-reset.json"
    abort_at = None
    term = rst = None
    if outstanding:
        term = outstanding[-1]
        if not (term.get("abort_sha256") and term.get("ordinal")):
            die("F1K_GUARD", "malformed terminal-abort event %r in %s — "
                "maintainer surface [REV-E]" % (term, events_p))
        if not abort_p.exists():
            die("F1K_GUARD", "construction-events.jsonl records an "
                "UNCONSUMED terminal-abort (ordinal %s, at n_done=%s, "
                "abort_sha256 %s) but construction-abort.json is "
                "MISSING — deleting the abort file never lifts stop "
                "authority [REV-E]. RECOVERY: a maintainer restores the "
                "abort bytes (sha256 above), reviews the recorded "
                "breach values, and writes construction-reset.json "
                "bound to them; re-running without that never bypasses "
                "stop authority"
                % (term.get("ordinal"), term.get("at_checkpoint"),
                   term.get("abort_sha256")))
        if sha256_file(abort_p) != term["abort_sha256"]:
            die("F1K_GUARD", "construction-abort.json does NOT hash to "
                "the terminal-abort event's abort_sha256 %s — the abort "
                "file was edited/replaced after the STOP; refused "
                "(maintainer surface) [REV-E]" % term["abort_sha256"])
        ab = json.loads(abort_p.read_text(encoding="utf-8"))
        if not reset_p.exists():
            die("F1K_GUARD", "construction-abort.json exists (checkpoint "
                "STOP at n_done=%r; breaches: %s) — a checkpoint STOP is "
                "TERMINAL for this rundir. RECOVERY: a maintainer reviews "
                "the recorded breach values and writes construction-"
                "reset.json {schema: %r, authorized_by: <name>, decision: "
                "'resume-construction', abort_sha256: sha256 of the abort "
                "file bytes}; re-running without it never bypasses stop "
                "authority [REV-D]"
                % (ab.get("at_checkpoint"),
                   "; ".join(ab.get("breaches") or [])
                   or "(recorded in the abort file)",
                   SCHEMA + ":construction-reset"))
        rst = json.loads(reset_p.read_text(encoding="utf-8"))
        bad = []
        if rst.get("schema") != SCHEMA + ":construction-reset":
            bad.append("schema %r" % rst.get("schema"))
        if not (rst.get("authorized_by") or "").strip():
            bad.append("authorized_by empty")
        if rst.get("decision") != "resume-construction":
            bad.append("decision %r" % rst.get("decision"))
        if rst.get("abort_sha256") != sha256_file(abort_p):
            bad.append("abort_sha256 != the abort file bytes (a reset "
                       "authorizes exactly ONE reviewed abort)")
        if bad:
            die("F1K_GUARD", "construction-reset.json present but NOT "
                "authorizing (%s) — the reset binds BY BYTES to the abort "
                "it overrules [REV-D]" % "; ".join(bad))
        abort_at = int(ab["at_checkpoint"])
        #   consumption + archive happen BELOW: after the raced-past
        #   check (a REFUSED resume leaves abort AND reset in place,
        #   terminal as ever) and BEFORE any engine start [REV-E].
    elif abort_p.exists():
        die("F1K_GUARD", "construction-abort.json present with NO "
            "unconsumed terminal-abort event in construction-events."
            "jsonl — a replayed/foreign or already-consumed abort "
            "authorizes nothing; remove it deliberately (maintainer "
            "surface) [REV-E]")
    elif reset_p.exists():
        die("F1K_GUARD", "construction-reset.json present with NO "
            "outstanding terminal stop — a reset is SINGLE-USE and was "
            "consumed (archived) by the resume that used it, or never "
            "had a stop to authorize; a second use finds nothing "
            "[REV-E]; remove it deliberately")
    workdir = Path(args.workdir)

    def concepts_done():
        return len(list(workdir.glob("concept-*.json")))

    n0 = concepts_done() * 48
    pending = [p for p in CHECKPOINT_SCHEDULE if p > n0]
    if abort_at is not None:
        # [REV-D 1c] authorized resume: the remaining schedule is
        # re-derived FROM THE ABORT POINT — every frozen checkpoint past
        # the abort must still run. If the cached concept files raced
        # past one (kill latency can leave files beyond the breach
        # boundary), no honest fresh timing exists for it: REFUSE rather
        # than silently drop it.
        dropped = [p for p in CHECKPOINT_SCHEDULE if abort_at < p <= n0]
        if dropped:
            die("F1K_GUARD", "authorized resume from the abort at "
                "n_done=%d, but the cached concept files already cover "
                "n_done=%d — frozen checkpoint(s) %s would be silently "
                "dropped; maintainer surface (inspect/trim the workdir "
                "deliberately, then re-authorize) [REV-D]"
                % (abort_at, n0, dropped))
        # [REV-E 2] CONSUMED, archive-then-proceed: the reset AND the
        # abort are archived — and the consumption event appended —
        # BEFORE any engine start (the pin-engagement probe below IS an
        # engine start), so a re-invocation at ANY later point finds no
        # reset to reuse: single-use by construction. Archive names
        # carry the abort's hash and the terminal ordinal
        # (timestamp-free). DISCLOSED: a probe/launch failure AFTER
        # consumption does not re-arm the OLD stop — the maintainer's
        # authorization covers the remaining schedule until a NEW
        # checkpoint STOP appends a fresh terminal event.
        os.replace(reset_p, rundir / (
            "construction-reset.consumed-%d-%s.json"
            % (int(term["ordinal"]), term["abort_sha256"][:16])))
        os.replace(abort_p, rundir
                   / ("construction-abort.consumed-%d.json" % abort_at))
        _append_event({"event": "reset-consumed",
                       "ordinal": int(term["ordinal"]),
                       "abort_sha256": term["abort_sha256"],
                       "authorized_by": rst.get("authorized_by"),
                       "resumed_from_checkpoint": abort_at})
    if not pending:
        print("guard: resume past the last frozen checkpoint (n0=%d) — "
              "no checkpoints remain; earlier sessions ran them" % n0)
    probe = _probe_engagement(json.loads(args.engine_cmd), env,
                              args.layers, rundir)
    # [REV-D 1a] the builder runs the SAME engine/tokenizer argv the
    # probe verified — injected here, never operator-supplied.
    builder_argv = args.builder + ["--engine-cmd", args.engine_cmd,
                                   "--tokenizer-cmd", args.tokenizer_cmd]
    proc = subprocess.Popen(builder_argv, env=env, start_new_session=True)
    t0 = time.monotonic()

    def run_ckpt(p):
        try:
            return checkpoint_eval(
                art, args.tokens, p, time.monotonic() - t0, n_start=n0,
                out=str(rundir / ("construction-checkpoint-%d.json" % p)))
        except SystemExit:
            if proc.poll() is None:
                try:
                    os.killpg(proc.pid, signal.SIGTERM)
                    for _ in range(30):
                        if proc.poll() is not None:
                            break
                        time.sleep(1)
                    if proc.poll() is None:
                        os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            # [REV-D 1c] the abort records the BREACH VALUES for the
            # maintainer's resume decision (read back from the checkpoint
            # artifact checkpoint_eval just wrote), and is TERMINAL: the
            # next guard invocation refuses to start while it exists.
            try:
                ck = json.loads(
                    (rundir / ("construction-checkpoint-%d.json" % p))
                    .read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                ck = {}
            abort_p.write_text(json.dumps(
                {"schema": SCHEMA + ":construction-abort",
                 "at_checkpoint": p, "n_start": n0,
                 "elapsed_s": round(time.monotonic() - t0, 1),
                 "breaches": ck.get("breaches"),
                 "reprojection": ck.get("reprojection"),
                 "realized_over_predicted":
                     ck.get("realized_over_predicted"),
                 "rule": "TERMINAL for this rundir [REV-D]: the next "
                         "guard invocation REFUSES to start while this "
                         "file exists, unless a maintainer-authorized "
                         "construction-reset.json (schema %s, bound to "
                         "these bytes by abort_sha256) is present"
                         % (SCHEMA + ":construction-reset")}, indent=2))
            # [REV-E 2] durable stop authority: the deletable abort
            # file is mirrored by an append-only terminal event
            # (fsynced, sentinel mechanics) — the next guard start
            # refuses on the EVENT, whatever happened to the file.
            _append_event({"event": "terminal-abort",
                           "ordinal": len(terms) + 1,
                           "at_checkpoint": p,
                           "abort_sha256": sha256_file(abort_p)})
            raise

    ran = []
    while proc.poll() is None:
        time.sleep(poll_s)                             # [REV-E 3]
        avail = concepts_done() * 48
        while pending and pending[0] <= avail:
            p = pending.pop(0)
            run_ckpt(p)
            ran.append(p)
    rc = proc.returncode
    final_avail = concepts_done() * 48
    while pending and pending[0] <= final_avail:
        p = pending.pop(0)
        run_ckpt(p)     # a post-hoc breach still STOPs before pilot
        ran.append(p)
    elapsed = time.monotonic() - t0
    rate = art["rate"]["usd_per_hour"]
    final = {"schema": SCHEMA + ":construction-guard-final",
             "builder_exit": rc, "pin_file_sha256": pin_sha,
             "pin_gb": pin_gb, "ambient_overridden": overridden,
             "probe": "construction-pin-probe.json",
             "builder_argv": builder_argv,
             "engine_argv_unity": "guard-injected --engine-cmd/"
                                  "--tokenizer-cmd == the probed argv "
                                  "(construct-don't-compare [REV-D])",
             "resumed_from_abort": abort_at,
             "checkpoints_run": ran, "n_start_passes": n0,
             "n_final_passes": final_avail,
             "elapsed_s": round(elapsed, 1),
             "realized": {"instance_hours": round(elapsed / 3600.0, 4),
                          "usd": round(elapsed / 3600.0 * rate, 4),
                          "rate_usd_per_hour": rate},
             "rule": "this session's realized figures; `config-cost` "
                     "sums guard-final files into the campaign config's "
                     "REQUIRED cost basis (landed Ledger, ASM-2513)"}
    (rundir / "construction-guard-final.json").write_text(
        json.dumps(final, indent=2))
    print(json.dumps(final, indent=2))
    return rc


# ---------------------------------------------------------------------------
# gate -> campaign-config executable seams [REV-C F5iii + F3 checkpoints]
# ---------------------------------------------------------------------------
def _merge_config_block(cfg_path, key, block):
    cfg = json.loads(Path(cfg_path).read_text(encoding="utf-8"))
    if key in cfg and cfg[key] != block:
        die("F1K_CONFIG", "config.%s already present and DIFFERENT — a "
            "licensed binding is never silently overwritten; resolve "
            "deliberately (existing: %s)"
            % (key, json.dumps(cfg[key], indent=2)[:800]))
    cfg[key] = block
    tmp = Path(str(cfg_path) + ".tmp")
    tmp.write_text(json.dumps(cfg, indent=2))
    os.replace(tmp, cfg_path)
    print(json.dumps({key: block}, indent=2))


def cmd_config_afford(args):
    """[REV-C F5iii] populate config.affordability FROM the licensed gate
    artifact — the executable step the rereview found missing (a licensed
    run could otherwise reach pilot and STALL on an absent block). Every
    value is verified against the ARTIFACT-recorded bundle, then written;
    the driver re-verifies at consumption (defense in depth)."""
    art_path = Path(args.gate)
    art = json.loads(art_path.read_text(encoding="utf-8"))
    if art.get("schema") != SCHEMA:
        die("F1K_CONFIG", "gate artifact schema %r != %s"
            % (art.get("schema"), SCHEMA))
    if art.get("verdict") != "GREEN":
        die("F1K_CONFIG", "gate artifact verdict %r — only GREEN feeds a "
            "campaign config" % art.get("verdict"))
    if (art.get("tokenizer") or {}).get("mode") != "REAL" \
            and not args.allow_mock:
        die("F1K_CONFIG", "gate artifact tokenizer mode is not REAL — a "
            "mock bundle enters a config only under --allow-mock (and "
            "never licenses in the driver)")
    mb = art.get("model_bundle") or {}
    if not mb.get("tokens_full_sha256") or not mb.get("add7_src_sha256"):
        die("F1K_CONFIG", "gate artifact model_bundle incomplete (%r)"
            % (mb,))
    tok_sha = sha256_file(args.tokens)
    if tok_sha != mb["tokens_full_sha256"]:
        die("F1K_CONFIG", "tokens sidecar %s sha %s != the ARTIFACT-"
            "recorded %s — the bundle binds bytes, not paths"
            % (args.tokens, tok_sha[:16],
               mb["tokens_full_sha256"][:16]))
    own = add7_block_sha256(__file__)
    if own != ADD7_SRC_SHA256 or mb["add7_src_sha256"] != own:
        die("F1K_CONFIG", "shared-model sha mismatch (own %r vs frozen/"
            "artifact) — refuse to bind a drifted model"
            % (own and own[:16]))
    block = {"tokens_full_path": str(Path(args.tokens).resolve()),
             "tokens_full_sha256": tok_sha,
             "gate_artifact_path": str(art_path.resolve()),
             "gate_artifact_sha256": sha256_file(art_path)}
    if args.allow_mock:
        block["_allow_mock"] = True
    _merge_config_block(args.config, "affordability", block)
    return 0


def cmd_config_cost(args):
    """[REV-C F3 / REV-D 1d] transfer the guard's realized construction
    figures into the campaign config's REQUIRED cost basis (the landed
    Ledger fails closed without cost.{usd_spent_prior, prior_instance_
    hours, construction_instance_hours} — ASM-2513/REV-D). --final may
    repeat for resumed constructions (sessions sum); --prior-usd is the
    metered PRE-construction spend PLUS any failed-session spend;
    --prior-hours is the instance-hours behind that spend and is
    REQUIRED whenever --prior-usd > 0 — hours must never vanish from
    the 900 h basis while their dollars are counted (round-3 verdict
    1d)."""
    hours = usd = 0.0
    for fp in args.final:
        fin = json.loads(Path(fp).read_text(encoding="utf-8"))
        if fin.get("schema") != SCHEMA + ":construction-guard-final":
            die("F1K_CONFIG", "%s is not a construction-guard-final "
                "artifact" % fp)
        if fin.get("builder_exit") != 0:
            die("F1K_CONFIG", "%s records builder_exit=%r — a FAILED "
                "construction session never becomes a cost basis; "
                "resume it (its successor final subsumes the elapsed "
                "time it re-does, and its wasted spend goes into "
                "--prior-usd deliberately, WITH its hours in "
                "--prior-hours [REV-D])" % (fp, fin.get("builder_exit")))
        hours += _fin(fin["realized"]["instance_hours"],
                      "final %s realized.instance_hours" % fp,
                      "F1K_CONFIG")                         # [REV-E 3]
        usd += _fin(fin["realized"]["usd"],
                    "final %s realized.usd" % fp, "F1K_CONFIG")
    # [REV-E 3] FINITENESS (round-4 verdict 4): "--prior-hours nan"
    # passed the old `ph < 0` (False for NaN) -> NaN 900 h basis ->
    # nan > 900 False at every cap -> fail-open GO. Every operator
    # numeric on this surface is finite-validated at the parse; the
    # driver Ledger re-asserts finiteness at init (defense-in-depth).
    pu = _fin(args.prior_usd, "--prior-usd", "F1K_CONFIG")
    ph = None if args.prior_hours is None \
        else _fin(args.prior_hours, "--prior-hours", "F1K_CONFIG")
    if pu > 0 and ph is None:
        die("F1K_CONFIG", "--prior-usd %.4f > 0 REQUIRES --prior-hours "
            "(the instance-hours behind that spend: failed construction "
            "sessions + metered pre-construction) — realized hours never "
            "vanish from the cap basis [REV-D 1d]" % pu)
    block = {"spot_rate_usd_per_hour":
             _fin(args.rate, "--rate", "F1K_CONFIG",
                  lo_open=True),                            # [REV-E 3]
             "usd_spent_prior": round(pu + usd, 4),
             "prior_instance_hours": round(ph or 0.0, 4),
             "construction_instance_hours": round(hours, 4)}
    _merge_config_block(args.config, "cost", block)
    return 0


# ---------------------------------------------------------------------------
# spec ($0 control-box witness) + selftest ($0 oracle)
# ---------------------------------------------------------------------------
def cmd_spec(args):
    out = {
        "schema": SCHEMA + ":sample-spec",
        "seed": SAMPLE_SEED,
        "rule": {"quantile_edges": list(QUANTILE_EDGES),
                 "bin_alloc": list(BIN_ALLOC), "cont_tokens": CONT_TOKENS,
                 "pop_floor": POP_FLOOR, "t1_n": T1_N,
                 "f_threshold": F_THRESHOLD,
                 "se_mult": SE_MULT,
                 "floor_extrap_min_frac": FLOOR_EXTRAP_MIN_FRAC},
        "inventory": {"construction": [N_CONSTRUCTION, 1],
                      "main-tmpl": [N_TEST, M_MAIN_TMPL],
                      "main-d3": [N_TEST, M_MAIN_D3],
                      "pilot": [N_DEV, M_PILOT],
                      "guard": [N_GUARD, M_GUARD],
                      "mandatory_total": MANDATORY_PREFILLS},
        "corpus_sha256": corpus_shas(args.corpus_dir),
    }
    print(json.dumps(out, indent=2))
    return 0


def _mock_corpora(d):
    """Full frozen-count corpora with deterministic synthetic texts whose
    word lengths mimic the measured per-population distributions."""
    import io

    def words(key, mean, spread, tail_key=None, tail_words=0):
        h = int(tiehash(key)[:8], 16)
        n = max(4, mean - spread + h % (2 * spread + 1))
        if tail_key and h % 97 == 0:
            n = tail_words
        return " ".join("w%d" % ((h + i) % 511) for i in range(n))

    with open(d / "construction-manifest.jsonl", "w") as f:
        for i in range(N_CONSTRUCTION):
            f.write(json.dumps({"text": words("c%d" % i, 31, 20)}) + "\n")
    for name, n, tmean, has_d3 in (("test.jsonl", N_TEST, 123, True),
                                   ("dev.jsonl", N_DEV, 84, True),
                                   ("guard.jsonl", N_GUARD, 57, False)):
        with open(d / name, "w") as f:
            for i in range(n):
                key = "%s%d" % (name, i)
                r = {"item_id": "it-%s-%04d" % (name[:2], i),
                     "template_text": words(key, tmean, 50, key, 774)}
                if has_d3:
                    r["d3_template_text"] = r["template_text"] + " " + \
                        words(key + "k", 23, 5)
                f.write(json.dumps(r) + "\n")


MOCK_PIN_PATH = "/mock/pin_bringup.stats"
MOCK_PIN_BANNER = ("[PIN] hot-expert store armed: pinned 96 experts, "
                   "1.780 GiB (budget 40.000 GiB) from " + MOCK_PIN_PATH)
#   [REV-B F3] byte-conforming to the LANDED driver PIN_ARMED_RE (the
#   mock_colibri.py banner grammar the ASM-2513 machinery verifies)


def _fake_timing(sample, s_of_t, path, evidence=MOCK_PIN_BANNER):
    with open(path, "w") as f:
        for e in sample["entries"]:
            noise = 1.0 + ((int(tiehash("n" + e["key"])[:6], 16) % 401)
                           - 200) / 10000.0   # deterministic +-2%
            f.write(json.dumps({"sample_id": e["sample_id"],
                                "s": round(s_of_t(e["Tp"]) * noise, 3),
                                "pin_evidence": evidence,
                                "timer_n": 1}) + "\n")


def _fake_result_set(source_jsonl, directory, *, phase, expected_ids,
                     boot_id):
    """Turn planted legacy rows into the atomic per-sample fixture format."""
    rows = {row["sample_id"]: row for row in
            (json.loads(line) for line in Path(source_jsonl).read_text()
             .splitlines() if line.strip())}
    root = Path(directory)
    root.mkdir()
    for sid in expected_ids:
        record = dict(rows[sid])
        record.update({"phase": phase, "boot_id": boot_id})
        if phase == "t1":
            record["pin_evidence"] = ""
        f1k_ops.atomic_write_json(root / ("%s-%s.json" % (phase, sid)),
                                  record)
    return root


def selftest():
    import tempfile
    frozen = {"instance_hours": [260.6, 900.0], "usd_total": [73.0, 155.0],
              "rate_window": [0.0811, 0.5948], "prefills_min": 11011}
    fails = []
    n_checks = 0

    def check(cond, msg):
        nonlocal n_checks
        n_checks += 1
        print("  %s %s" % ("ok:  " if cond else "FAIL:", msg))
        if not cond:
            fails.append(msg)

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        cd = td / "corpus"
        cd.mkdir()
        _mock_corpora(cd)
        print("== selftest: kot-f1k-bringup-gate/2 $0 oracle (MOCK tokens) ==")
        ns = argparse.Namespace(corpus_dir=str(cd), mock_f=1.45,
                                tok_wrapper=None, tokenizer=None,
                                out=str(td / "tok"))
        cmd_fcount(ns)
        cmd_fcount(argparse.Namespace(**{**vars(ns), "out": str(td / "tok2")}))
        check((td / "tok/tokens-full.jsonl").read_bytes()
              == (td / "tok2/tokens-full.jsonl").read_bytes(),
              "fcount deterministic (two runs byte-identical)")
        cmd_realize(argparse.Namespace(tokens=str(td / "tok"),
                                       out=str(td / "samp")))
        cmd_realize(argparse.Namespace(tokens=str(td / "tok"),
                                       out=str(td / "samp2")))
        s1 = (td / "samp/timing-sample.json").read_bytes()
        check(s1 == (td / "samp2/timing-sample.json").read_bytes(),
              "realize deterministic (two runs byte-identical)")
        sample = json.loads(s1)
        ent = [json.loads(l) for l in open(td / "tok/tokens-full.jsonl")]
        maxtp = max(e["T"] + CONT_TOKENS for e in ent)
        check(any(c["Tp"] == maxtp for c in sample["entries"]),
              "campaign max-T prefill is in the sample")
        pops = {p: sum(1 for c in sample["entries"] if c["pop"] == p)
                for p in POP_FLOOR}
        check(all(pops[p] >= POP_FLOOR[p] for p in POP_FLOOR),
              "population coverage floors met: %s" % pops)
        check(sample["n"] <= N_SAMPLE_MAX,
              "sample size %d <= cap %d" % (sample["n"], N_SAMPLE_MAX))

        def mk_inputs(t2path, rate=0.174):
            counts = json.loads((td / "tok/token-counts.json").read_text())
            inv_t = [[e["pop"], e["m"], e["T"] + CONT_TOKENS] for e in ent]
            return {"schema": SCHEMA + ":gate-inputs",
                    "token_counts": counts, "_allow_mock": True,
                    "tokens_full_sha256":
                        sha256_file(td / "tok/tokens-full.jsonl"),
                    "timing_sample": sample,
                    "t2_pinned_runs": [json.loads(l) for l in open(t2path)],
                    "t1_unpinned_runs": [], "inventory_t": inv_t,
                    "rate_usd_per_hour": rate,
                    "rate_usd_per_hour_decimal":
                        f1k_ops.canonical_decimal(str(rate),
                                                  field="selftest rate"),
                    "rate_source": "selftest",
                    "pin": {"pin_file_sha256": "f" * 64, "pin_gb": 40.0,
                            "pin_file_path": MOCK_PIN_PATH,
                            "regime": "pinned-bringup", "note": "mock"},
                    "dump_gate": {"a": "PASS", "b": "PASS", "c": "PASS",
                                  "functional_inertness": "PASS"}}

        # case 1 GREEN: linear planted s(T) scaled to 700 h central
        mass = sum(e["m"] * (e["T"] + CONT_TOKENS) for e in ent)
        b_lin = 700.0 * 3600.0 / mass
        _fake_timing(sample, lambda t: b_lin * t, td / "t2-green.jsonl")
        art = project(mk_inputs(td / "t2-green.jsonl"), frozen)
        check(art["verdict"] == "GREEN",
              "case 1 GREEN verdict (got %s %s)" % (art["verdict"],
                                                    art["reasons"]))
        check(art["f"]["branch"] == "LE" and art["checks"]["f_le_threshold"],
              "case 1 f-branch LE at mock f=1.45")
        check(abs(art["projection"]["instance_hours"]["central"] - 700) < 25,
              "case 1 central ~700 h (got %s)"
              % art["projection"]["instance_hours"]["central"])
        # case 2 STOP long-tail: convex planted s(T) = b*T^2 scaled to 940 h
        # -> the per-AVERAGE projection FITS while the per-item one BREACHES
        mass2 = sum(e["m"] * (e["T"] + CONT_TOKENS) ** 2 for e in ent)
        b_sq = 940.0 * 3600.0 / mass2
        _fake_timing(sample, lambda t: b_sq * t * t, td / "t2-tail.jsonl")
        art2 = project(mk_inputs(td / "t2-tail.jsonl"), frozen)
        check(art2["verdict"] == "STOP",
              "case 2 STOP: convex long-tail breaches the 900 h cap")
        naive = art2["projection"]["per_average_naive_hours_RETIRED"]
        check(naive <= 900.0 <
              art2["projection"]["instance_hours"]["central"],
              "case 2 DIVERGENCE PROVEN (review finding 3): per-average "
              "%.0f h would fit, per-item %.0f h breaches"
              % (naive, art2["projection"]["instance_hours"]["central"]))
        # case 3 STOP on f > 1.60 even with a fitting ledger
        ns3 = argparse.Namespace(**{**vars(ns), "mock_f": 1.75,
                                    "out": str(td / "tok3")})
        cmd_fcount(ns3)
        in3 = mk_inputs(td / "t2-green.jsonl")
        in3["token_counts"] = json.loads(
            (td / "tok3/token-counts.json").read_text())
        # rescale planted timing to keep the ledger inside the windows at
        # the LONGER mock-f=1.75 token counts (isolates the f-branch)
        ent3 = [json.loads(l) for l in open(td / "tok3/tokens-full.jsonl")]
        in3["inventory_t"] = [[e["pop"], e["m"], e["T"] + CONT_TOKENS]
                              for e in ent3]
        mass3 = sum(e["m"] * (e["T"] + CONT_TOKENS) for e in ent3)
        # knots span mock-f=1.45 T-range; f=1.75 tokens exceed the max knot
        # -> re-realize the sample at the f=1.75 counts (rule is T-relative)
        cmd_realize(argparse.Namespace(tokens=str(td / "tok3"),
                                       out=str(td / "samp3")))
        sample3 = json.loads((td / "samp3/timing-sample.json").read_text())
        in3["timing_sample"] = sample3
        b3 = 700.0 * 3600.0 / mass3
        _fake_timing(sample3, lambda t: b3 * t, td / "t2-f175.jsonl")
        in3["t2_pinned_runs"] = [json.loads(l)
                                 for l in open(td / "t2-f175.jsonl")]
        art3 = project(in3, frozen)
        check(art3["verdict"] == "STOP" and art3["f"]["branch"] == "GT"
              and any("f " in r or "f-" in r or "blended f" in r
                      for r in art3["reasons"]),
              "case 3 STOP purely on the f>1.60 branch (reasons: %s)"
              % art3["reasons"])
        # case 4 fail-closed: campaign T above the max sampled knot
        in4 = mk_inputs(td / "t2-green.jsonl")
        in4["inventory_t"] = in4["inventory_t"] + [["main-d3", 1, maxtp * 3]]
        try:
            project(in4, frozen)
            check(False, "case 4 must fail closed above the max knot")
        except SystemExit:
            check(True, "case 4 fail-closed: T above max sampled knot dies")
        # case 5 fail-closed: MOCK tokens never license without _allow_mock
        in5 = mk_inputs(td / "t2-green.jsonl")
        del in5["_allow_mock"]
        try:
            project(in5, frozen)
            check(False, "case 5 must refuse MOCK token counts")
        except SystemExit:
            check(True, "case 5 fail-closed: MOCK tokens refused for a "
                        "real verdict")
        # case 6a-j: atomic per-sample complete-set validation. The planted
        # legacy JSONL remains the arithmetic oracle; only collect's reader is
        # changed.
        import shutil
        boot_a = "11111111-1111-4111-8111-111111111111"
        boot_b = "22222222-2222-4222-8222-222222222222"
        t2_ids = [entry["sample_id"] for entry in sample["entries"]]
        t1_ids = sample["t1_sample_ids"]
        t1_valid = _fake_result_set(
            td / "t2-green.jsonl", td / "t1-valid", phase="t1",
            expected_ids=t1_ids, boot_id=boot_a)
        t2_valid = _fake_result_set(
            td / "t2-green.jsonl", td / "t2-valid", phase="t2",
            expected_ids=t2_ids, boot_id=boot_a)

        def refuses_results(path, phase="t2", ids=t2_ids):
            try:
                _read_sample_results(path, phase=phase, expected_ids=ids)
                return False
            except SystemExit:
                return True

        def collect_args(t2, out, *, t1=t1_valid, rate="0.174"):
            return argparse.Namespace(
                sample=str(td / "samp/timing-sample.json"),
                tokens=str(td / "tok"), t2=str(t2), t1=str(t1), rate=rate,
                pin_sha="f" * 64, pin_gb="40", pin_path=MOCK_PIN_PATH,
                pin_derivation="", pin_regime="pinned-bringup",
                dump_a="PASS", dump_b="PASS", dump_c="PASS",
                functional="PASS", out=str(out))

        valid_rows = _read_sample_results(
            t2_valid, phase="t2", expected_ids=t2_ids)
        check(list(valid_rows) == t2_ids,
              "case 6a complete atomic T2 set accepted in sample order")

        missing6 = td / "t2-missing"
        shutil.copytree(t2_valid, missing6)
        (missing6 / ("t2-%s.json" % t2_ids[-1])).unlink()
        check(refuses_results(missing6),
              "case 6b fail-closed: missing/partial T2 set refused")

        extra6 = td / "t2-extra"
        shutil.copytree(t2_valid, extra6)
        extra_record = dict(valid_rows[t2_ids[0]])
        extra_record["sample_id"] = "s999"
        f1k_ops.atomic_write_json(extra6 / "t2-s999.json", extra_record)
        check(refuses_results(extra6),
              "case 6c fail-closed: unexpected/extra T2 id refused")

        duplicate6 = td / "t2-duplicate"
        shutil.copytree(t2_valid, duplicate6)
        shutil.copyfile(duplicate6 / ("t2-%s.json" % t2_ids[0]),
                        duplicate6 / "t2-duplicate.json")
        check(refuses_results(duplicate6),
              "case 6d fail-closed: duplicate record sample_id refused")

        mismatch6 = td / "t2-filename-mismatch"
        shutil.copytree(t2_valid, mismatch6)
        (mismatch6 / ("t2-%s.json" % t2_ids[0])).rename(
            mismatch6 / "t2-wrong-name.json")
        check(refuses_results(mismatch6),
              "case 6e fail-closed: filename/sample_id mismatch refused")

        mixed6 = td / "t2-mixed-boot"
        shutil.copytree(t2_valid, mixed6)
        mixed_path = mixed6 / ("t2-%s.json" % t2_ids[0])
        mixed_record = json.loads(mixed_path.read_text())
        mixed_record["boot_id"] = boot_b
        f1k_ops.atomic_write_json(mixed_path, mixed_record)
        check(refuses_results(mixed6),
              "case 6f fail-closed: mixed boot_id within T2 set refused")

        malformed6 = td / "t2-malformed"
        shutil.copytree(t2_valid, malformed6)
        (malformed6 / ("t2-%s.json" % t2_ids[0])).write_text("{broken")
        check(refuses_results(malformed6),
              "case 6g fail-closed: malformed result record refused")

        bad_numeric_refused = []
        for i6n, bad_s in enumerate((float("nan"), float("inf"), 0.0, -1.0)):
            numeric6 = td / ("t2-bad-s-%d" % i6n)
            shutil.copytree(t2_valid, numeric6)
            numeric_path = numeric6 / ("t2-%s.json" % t2_ids[0])
            numeric_record = json.loads(numeric_path.read_text())
            numeric_record["s"] = bad_s
            numeric_path.write_text(json.dumps(numeric_record))
            bad_numeric_refused.append(refuses_results(numeric6))
        check(all(bad_numeric_refused),
              "case 6h fail-closed: NaN/Infinity/zero/negative s refused")

        cross_boot6 = td / "t1-cross-boot"
        shutil.copytree(t1_valid, cross_boot6)
        for path6 in cross_boot6.glob("*.json"):
            record6 = json.loads(path6.read_text())
            record6["boot_id"] = boot_b
            f1k_ops.atomic_write_json(path6, record6)
        try:
            cmd_collect(collect_args(t2_valid, td / "gi-cross-boot.json",
                                     t1=cross_boot6))
            check(False, "case 6i must refuse cross-boot T1/T2 timing")
        except SystemExit:
            check(True, "case 6i fail-closed: complete T1/T2 sets from "
                        "different boots refused")

        valid6_path = td / "gi-valid-atomic.json"
        cmd_collect(collect_args(t2_valid, valid6_path))
        valid6 = json.loads(valid6_path.read_text())
        valid6["_allow_mock"] = True
        atomic6 = project(valid6, frozen)
        legacy6 = project(mk_inputs(td / "t2-green.jsonl"), frozen)
        check(valid6["pin"]["pin_file_sha256"] == "f" * 64
              and atomic6["verdict"] == legacy6["verdict"]
              and atomic6["projection"] == legacy6["projection"],
              "case 6j complete atomic sets preserve the bound pin and "
              "projection arithmetic exactly")

        # case 6k-o [finding 1]: collect retains the exact canonical decimal
        # spelling; project carries it as the authoritative licensing field.
        collected_rates = {}
        for i6, raw6 in enumerate(
                ("0.190", "1.90e-1", "0.10000000000000001")):
            out6 = td / ("gi-rate-%d.json" % i6)
            cmd_collect(collect_args(t2_valid, out6, rate=raw6))
            collected_rates[raw6] = json.loads(out6.read_text())
        check(collected_rates["0.190"]["rate_usd_per_hour_decimal"]
              == collected_rates["1.90e-1"]["rate_usd_per_hour_decimal"]
              == "0.19",
              "case 6k collect canonical decimal: 0.190 and 1.90e-1 "
              "both record as 0.19")
        lossy6 = collected_rates["0.10000000000000001"]
        check(lossy6["rate_usd_per_hour_decimal"]
              == "0.10000000000000001"
              and lossy6["rate_usd_per_hour"] == 0.1
              and lossy6["rate_usd_per_hour_decimal"]
              != f1k_ops.canonical_decimal(
                  str(lossy6["rate_usd_per_hour"]), field="lossy float"),
              "case 6l collect preserves 0.10000000000000001 exactly "
              "while its derived float is visibly lossy (0.1)")
        in6d = mk_inputs(td / "t2-green.jsonl", rate=0.19)
        in6d["rate_usd_per_hour_decimal"] = (
            collected_rates["0.190"]["rate_usd_per_hour_decimal"])
        art6d = project(in6d, frozen)
        check(art6d["verdict"] == "GREEN"
              and art6d["rate"]["usd_per_hour"] == 0.19
              and art6d["rate"]["usd_per_hour_decimal"] == "0.19",
              "case 6m GREEN artifact carries derived float 0.19 AND "
              "authoritative canonical decimal '0.19'")
        in6e = mk_inputs(td / "t2-green.jsonl", rate=0.1)
        in6e["rate_usd_per_hour_decimal"] = (
            lossy6["rate_usd_per_hour_decimal"])
        in6e["rate_source"] = lossy6["rate_source"]
        art6e = project(in6e, frozen)
        rule6e = art6e["model_bundle"]["rule"]
        check(art6e["rate"]["usd_per_hour"] == 0.1
              and art6e["rate"]["usd_per_hour_decimal"]
              == "0.10000000000000001"
              and "config rate decimal == rate.usd_per_hour_decimal"
              in rule6e
              and "config rate == rate.usd_per_hour" not in rule6e
              and "authoritative" in art6e["rate"]["source"],
              "case 6n lossy float remains projection-only; licensing "
              "equality names the exact decimal field exclusively")
        in6f = mk_inputs(td / "t2-green.jsonl", rate=0.19)
        del in6f["rate_usd_per_hour_decimal"]
        art6f = project(in6f, frozen)
        check(art6f["rate"]["usd_per_hour_decimal"] == "0.19",
              "case 6o older inputs resume through canonical decimal "
              "reconstruction from the stored float")
        # case 7 (+REPLACE fail-closed, v3-review :417/:423 lineage): the
        # SAME timing gives mandatory GREEN but +REPLACE STOP — a tested
        # replace projection must never be advisory.
        mass_rep = sum(e["T"] + CONT_TOKENS for e in ent
                       if e["pop"] == "main-tmpl")
        b7 = 780.0 * 3600.0 / mass   # GREEN incl. reserve+SE; x1.097 REPLACE breaches
        _fake_timing(sample, lambda t: b7 * t, td / "t2-rep.jsonl")
        art7a = project(mk_inputs(td / "t2-rep.jsonl"), frozen)
        art7b = project(mk_inputs(td / "t2-rep.jsonl"), frozen, replace=True)
        check(art7a["verdict"] == "GREEN" and art7b["verdict"] == "STOP",
              "case 7 +REPLACE fail-closed: mandatory GREEN (%.0f h) but "
              "the TESTED +REPLACE projection STOPs (%.0f h; scale x%.3f)"
              % (art7a["projection"]["instance_hours"]["central"],
                 art7b["projection"]["instance_hours"]["central"],
                 1.0 + mass_rep / mass))
        # case 8 (reserve boundary, v3-review finding 4; RE-DERIVED in
        # REV-B per gate-fix review #7: the old planted $149 realized
        # central $150.22 / +1SE $156.33, so the OLD rule ALREADY STOPped
        # on the +SE band and the case never isolated the reserve delta).
        # Planted $146.6 at rate 0.20 realizes central ~$147.8 / +1SE
        # ~$153.8: BOTH raw bands <= $155 (old reserve-blind rule: GO on
        # central AND +SE; hours ~739/+SE <= 900 too) while central + $8
        # breaches -> the STOP is attributable to the RESERVE alone.
        b8 = (146.6 / 0.20) * 3600.0 / mass
        _fake_timing(sample, lambda t: b8 * t, td / "t2-res.jsonl")
        art8a = project(mk_inputs(td / "t2-res.jsonl", rate=0.20), frozen)
        u8 = art8a["projection"]["usd_total"]["central"]
        u8hi = art8a["projection"]["usd_total"]["hi"]
        h8hi = art8a["projection"]["instance_hours"]["hi"]
        check(art8a["verdict"] == "STOP"
              and u8 <= 155.0 and u8hi <= 155.0 and h8hi <= 900.0
              and u8 + 8.0 > 155.0
              and any("RESERVE" in r for r in art8a["reasons"]),
              "case 8a reserve-boundary STOP ISOLATED: central $%.2f AND "
              "+1SE $%.2f both <= $155 raw (the OLD rule would GO on both "
              "bands) but central +$8 = $%.2f breaches — the reserve delta "
              "alone flips the verdict" % (u8, u8hi, u8 + 8.0))
        b8b = (140.0 / 0.20) * 3600.0 / mass
        _fake_timing(sample, lambda t: b8b * t, td / "t2-res2.jsonl")
        art8b = project(mk_inputs(td / "t2-res2.jsonl", rate=0.20), frozen)
        check(art8b["verdict"] == "GREEN",
              "case 8b reserve-boundary GREEN at $%.2f + $8 reserve"
              % art8b["projection"]["usd_total"]["central"])
        # case 9 (dump preconditions are HARD conjuncts): a scaffold status
        # on precondition (a) STOPs an otherwise-GREEN gate.
        in9 = mk_inputs(td / "t2-green.jsonl")
        in9["dump_gate"]["a"] = "RUNNER-CONFIRM-REQUIRED"
        art9 = project(in9, frozen)
        check(art9["verdict"] == "STOP"
              and any("precondition" in r for r in art9["reasons"]),
              "case 9 STOP: dump-(a) RUNNER-CONFIRM-REQUIRED never licenses")
        # case 10: a gate-inputs file with NO dump_gate block (old format)
        # fails closed the same way.
        in10 = mk_inputs(td / "t2-green.jsonl")
        del in10["dump_gate"]
        art10 = project(in10, frozen)
        check(art10["verdict"] == "STOP",
              "case 10 STOP: missing dump_gate block fails closed")
        # case 11 [REV-B F2]: manifest-vs-model structural consistency —
        # every score manifest's ctx+cont == the model's Tp; a manifest
        # regenerated with the OLD off-by-continuation convention
        # (ctx=T-8, total=T) is REFUSED by collect.
        ok11 = all(
            (lambda parts, e: int(parts[0]) + int(parts[1]) == e["Tp"]
             and len(parts) - 2 == e["Tp"])(
                (td / "samp" / ("sample-%s.score" % e["sample_id"]))
                .read_text().split(), e)
            for e in sample["entries"])
        check(ok11, "case 11 STRUCTURAL: every manifest ctx+cont == Tp "
                    "(the review-#3 class cannot recur silently)")
        e11 = sample["entries"][0]
        m11 = td / "samp" / ("sample-%s.score" % e11["sample_id"])
        good11 = m11.read_text()
        parts11 = good11.split()
        ids11 = parts11[2:2 + e11["T"]]     # strip the 8 cont ids
        m11.write_text("%d %d %s\n" % (e11["T"] - CONT_TOKENS, CONT_TOKENS,
                                       " ".join(ids11)))   # OLD convention
        try:
            cmd_collect(collect_args(t2_valid, td / "gi11.json"))
            check(False, "case 11 must refuse an off-by-continuation "
                         "manifest")
        except SystemExit:
            check(True, "case 11 fail-closed: OLD-convention manifest "
                        "(ctx=T-8, total=T) refused by collect")
        m11.write_text(good11)                 # restore
        # case 12 [REV-B F1]: pinfile merge correctness over an explicit
        # per-item manifest — merged pin == the (layer,expert) count SUM.
        sdir = td / "stats"
        sdir.mkdir()
        planted = [("3 0 10\n3 1 5\n", "a"), ("3 0 7\n4 2 9\n", "b"),
                   ("3 1 1\n4 2 1\n5 5 2\n", "c")]
        for body, tag in planted:
            (sdir / ("stats-%s.txt" % tag)).write_text(body)
        man12 = td / "stats.manifest"
        man12.write_text("".join("%s\n" % (sdir / ("stats-%s.txt" % t))
                                 for _, t in planted))
        cmd_pinfile(argparse.Namespace(stats_manifest=str(man12),
                                       pin_gb=40.0, out=str(td / "p12.st")))
        got12 = {}
        for ln in (td / "p12.st").read_text().splitlines():
            l, e, c = (int(x) for x in ln.split())
            got12[(l, e)] = c
        want12 = {(3, 0): 17, (3, 1): 6, (4, 2): 10, (5, 5): 2}
        check(got12 == want12,
              "case 12 MERGE CORRECT: 3 per-item stats files -> summed "
              "union %s" % sorted(got12.items()))
        man12.write_text(str(sdir / "stats-a.txt") + "\n"
                         + str(sdir / "stats-MISSING.txt") + "\n")
        try:
            cmd_pinfile(argparse.Namespace(stats_manifest=str(man12),
                                           pin_gb=40.0,
                                           out=str(td / "p12b.st")))
            check(False, "case 12 must refuse a missing per-item file")
        except SystemExit:
            check(True, "case 12 fail-closed: MISSING per-item stats file "
                        "refused (no silent partial union)")
        (sdir / "stats-bad.txt").write_text("3 zero 1\n")
        man12.write_text(str(sdir / "stats-bad.txt") + "\n")
        try:
            cmd_pinfile(argparse.Namespace(stats_manifest=str(man12),
                                           pin_gb=40.0,
                                           out=str(td / "p12c.st")))
            check(False, "case 12 must refuse a malformed stats file")
        except SystemExit:
            check(True, "case 12 fail-closed: malformed stats line refused "
                        "(never skipped)")
        # case 13 [REV-B F3]: engagement evidence is a hard conjunct — a
        # T2 set with NO armed banner, and one with a DISABLED marker,
        # both STOP an otherwise-GREEN gate.
        _fake_timing(sample, lambda t: b_lin * t, td / "t2-noev.jsonl",
                     evidence="")
        art13a = project(mk_inputs(td / "t2-noev.jsonl"), frozen)
        _fake_timing(sample, lambda t: b_lin * t, td / "t2-dis.jsonl",
                     evidence="[PIN] cannot open /mock/pin_bringup.stats")
        art13b = project(mk_inputs(td / "t2-dis.jsonl"), frozen)
        check(art13a["verdict"] == "STOP"
              and any("ENGAGEMENT" in r for r in art13a["reasons"])
              and art13b["verdict"] == "STOP",
              "case 13 STOP: missing armed banner AND disabled marker both "
              "refuse (landed ASM-2513 grammar)")
        # case 14 [REV-B F3]: regime 'unpinned' is REFUSED outright.
        in14 = mk_inputs(td / "t2-green.jsonl")
        in14["pin"]["regime"] = "unpinned"
        art14 = project(in14, frozen)
        check(art14["verdict"] == "STOP"
              and any("REFUSED" in r for r in art14["reasons"]),
              "case 14 STOP: regime 'unpinned' never licenses (shape (ii) "
              "rejected)")
        # case 15 [REV-B F3 / REV-C]: construction early-abort checkpoint
        # at the CONCEPT-ALIGNED frozen schedule (240/1056/2304) — ratio
        # 1.0 CONTINUEs; a realized slowdown that breaches the
        # reserve-inclusive cap STOPs (exit 2); an OFF-SCHEDULE n_done is
        # REFUSED (the schedule is frozen, never a movable goalpost).
        art["thresholds"] = frozen
        (td / "gate-art.json").write_text(json.dumps(art))
        cons15 = [e for e in ent if e["pop"] == "construction"][:240]
        knots15 = sorted(art["model"]["knots_isotonic"],
                         key=lambda k: k["T"])
        pred15 = sum(_interp(knots15, "s", e["T"] + CONT_TOKENS, "const")
                     for e in cons15)
        rc15 = cmd_checkpoint(argparse.Namespace(
            gate=str(td / "gate-art.json"),
            tokens=str(td / "tok" / "tokens-full.jsonl"),
            n_done=240, elapsed_s=str(pred15 * 1.0), n_start="0", out=""))
        check(rc15 == 0, "case 15 checkpoint CONTINUE at ratio 1.0 "
                         "(700 h central holds)")
        try:
            cmd_checkpoint(argparse.Namespace(
                gate=str(td / "gate-art.json"),
                tokens=str(td / "tok" / "tokens-full.jsonl"),
                n_done=240, elapsed_s=str(pred15 * 1.35), n_start="0",
                out=""))
            check(False, "case 15 must STOP at ratio 1.35")
        except SystemExit:
            check(True, "case 15 EARLY-ABORT STOP: ratio 1.35 re-projects "
                        "past the reserve-inclusive cap (exit 2) after "
                        "~$1.6 exposure, not after 4,608 passes")
        try:
            cmd_checkpoint(argparse.Namespace(
                gate=str(td / "gate-art.json"),
                tokens=str(td / "tok" / "tokens-full.jsonl"),
                n_done=200, elapsed_s=str(pred15), n_start="0", out=""))
            check(False, "case 15 must refuse off-schedule n_done")
        except SystemExit:
            check(True, "case 15 SCHEDULE ENFORCED: n_done=200 (off the "
                        "frozen 240/1056/2304) refused [REV-C]")
        # case 16 [REV-C F3]: construction-guard end-to-end on stubs —
        # (a) verified pin + armed-banner probe + frozen checkpoints off
        # per-concept files -> exit 0 with full evidence chain;
        # (b) tampered pin bytes refuse BEFORE launch; (c) a DISABLED
        # probe banner refuses BEFORE launch; (d) a non-GREEN artifact
        # refuses. ($0: stub engine/builder — the real seam is VM-only.)
        pin16 = td / "pin16.stats"
        pin16.write_text("3 0 17\n3 1 6\n")
        art16 = json.loads((td / "gate-art.json").read_text())
        art16["pin"]["pin_file_sha256"] = sha256_file(pin16)
        art16["pin"]["pin_gb"] = 40.0
        (td / "gate-art16.json").write_text(json.dumps(art16))
        eng16 = td / "stub-engine.py"
        eng16.write_text(
            "import os, sys\n"
            "if os.environ.get('STUB_DISABLE'):\n"
            "    sys.stderr.write('pinning DISABLED\\n'); sys.exit(0)\n"
            "sys.stderr.write('[PIN] hot-expert store armed: pinned 96 "
            "experts, 1.780 GiB (budget %s.000 GiB) from %s\\n'\n"
            "    % (os.environ.get('PIN_GB'), os.environ.get('PIN')))\n")
        bld16 = td / "stub-builder.py"
        bld16.write_text(
            "import os, sys, time\n"
            "wd = sys.argv[1]\n"
            "for c in range(96):\n"
            "    open(os.path.join(wd, 'concept-%03d.json' % c), 'w')"
            ".write('{}')\n"
            "    time.sleep(0.001)\n"
            "time.sleep(0.2)\n")
        wd16 = td / "wd16"
        wd16.mkdir()
        rd16 = td / "rd16"
        ns16 = argparse.Namespace(
            gate=str(td / "gate-art16.json"), pin=str(pin16),
            engine_cmd=json.dumps([sys.executable, str(eng16)]),
            tokenizer_cmd=json.dumps([sys.executable, "-c", "pass"]),
            layers="3,5", tokens=str(td / "tok" / "tokens-full.jsonl"),
            rundir=str(rd16), workdir=str(wd16), poll_seconds="0.05",
            builder=["--", sys.executable, str(bld16), str(wd16)])
        rc16 = cmd_guard(ns16)
        fin16 = json.loads(
            (rd16 / "construction-guard-final.json").read_text())
        check(rc16 == 0
              and (rd16 / "construction-pin-probe.json").is_file()
              and all((rd16 / ("construction-checkpoint-%d.json" % p))
                      .is_file() for p in (240, 1056, 2304))
              and fin16["builder_exit"] == 0
              and fin16["checkpoints_run"] == [240, 1056, 2304]
              and fin16["pin_file_sha256"] == sha256_file(pin16)
              and fin16["builder_argv"][-4:]
              == ["--engine-cmd", ns16.engine_cmd,
                  "--tokenizer-cmd", ns16.tokenizer_cmd],
              "case 16a GUARD end-to-end: probe evidence + all frozen "
              "checkpoints + guard-final (builder untouched, env-bound "
              "pin, PROBED engine/tokenizer argv INJECTED into the "
              "builder argv — unity by construction [REV-D])")
        pin16b = td / "pin16b.stats"
        pin16b.write_text("3 0 999\n")
        try:
            cmd_guard(argparse.Namespace(**{**vars(ns16),
                                            "pin": str(pin16b),
                                            "rundir": str(td / "rd16b"),
                                            "workdir": str(wd16)}))
            check(False, "case 16b must refuse tampered pin bytes")
        except SystemExit:
            check(True, "case 16b fail-closed: pin bytes != licensed sha "
                        "refused BEFORE launch")
        os.environ["STUB_DISABLE"] = "1"
        try:
            wd16c = td / "wd16c"
            wd16c.mkdir()
            cmd_guard(argparse.Namespace(**{**vars(ns16),
                                            "rundir": str(td / "rd16c"),
                                            "workdir": str(wd16c)}))
            check(False, "case 16c must refuse a DISABLED probe banner")
        except SystemExit:
            check(True, "case 16c fail-closed: probe saw pinning DISABLED "
                        "-> no construction launch (bounded exposure)")
        finally:
            del os.environ["STUB_DISABLE"]
        art16d = dict(art16, verdict="STOP")
        (td / "gate-art16d.json").write_text(json.dumps(art16d))
        try:
            cmd_guard(argparse.Namespace(**{**vars(ns16),
                                            "gate": str(td /
                                                        "gate-art16d.json"),
                                            "rundir": str(td / "rd16d"),
                                            "workdir": str(wd16)}))
            check(False, "case 16d must refuse a non-GREEN artifact")
        except SystemExit:
            check(True, "case 16d fail-closed: STOP artifact never "
                        "licenses construction")
        # case 17 [REV-C F5iii]: executable gate->config seams — the
        # affordability block is written FROM the artifact-bound bundle
        # (idempotent re-run OK; a conflicting existing block refuses;
        # tampered sidecar bytes refuse), and config-cost transfers the
        # guard-final realized figures into the REQUIRED Ledger basis.
        cfg17 = td / "config17.json"
        cfg17.write_text("{}")
        ns17 = argparse.Namespace(gate=str(td / "gate-art.json"),
                                  tokens=str(td / "tok" /
                                             "tokens-full.jsonl"),
                                  config=str(cfg17), allow_mock=True)
        cmd_config_afford(ns17)
        cmd_config_afford(ns17)     # idempotent re-run
        got17 = json.loads(cfg17.read_text())["affordability"]
        check(got17["tokens_full_sha256"]
              == sha256_file(td / "tok" / "tokens-full.jsonl")
              and got17["gate_artifact_sha256"]
              == sha256_file(td / "gate-art.json"),
              "case 17 config-affordability POPULATED from the licensed "
              "bundle (no pilot stall) + idempotent")
        tok17 = td / "tok-tampered.jsonl"
        tok17.write_bytes(
            (td / "tok" / "tokens-full.jsonl").read_bytes() + b" ")
        try:
            cmd_config_afford(argparse.Namespace(
                **{**vars(ns17), "tokens": str(tok17)}))
            check(False, "case 17 must refuse tampered sidecar bytes")
        except SystemExit:
            check(True, "case 17 fail-closed: sidecar bytes != the "
                        "ARTIFACT-recorded sha refused")
        cmd_config_cost(argparse.Namespace(
            final=[str(rd16 / "construction-guard-final.json")],
            prior_usd="3.1", prior_hours="17.8", rate="0.174",
            config=str(cfg17)))
        cost17 = json.loads(cfg17.read_text())["cost"]
        check(abs(cost17["usd_spent_prior"]
                  - (3.1 + fin16["realized"]["usd"])) < 1e-6
              and cost17["prior_instance_hours"] == 17.8
              and abs(cost17["construction_instance_hours"]
                      - fin16["realized"]["instance_hours"]) < 1e-9,
              "case 17 config-cost: guard-final realized figures + the "
              "prior hours become the REQUIRED Ledger basis (never "
              "silent zeros) [REV-D]")
        # case 18 [REV-C F5i]: ONE projection model, mechanically — the
        # gate copy hashes to the frozen constant AND byte-matches the
        # driver's vendored copy.
        drvp = Path(__file__).resolve().parents[1] / "glm52-probe" \
            / "f1k-harness" / "f1k_driver.py"
        own18 = add7_block_sha256(__file__)
        check(own18 == ADD7_SRC_SHA256
              and add7_block_sha256(drvp) == own18,
              "case 18 SHARED MODEL: gate block sha == frozen "
              "ADD7_SRC_SHA256 == driver block sha (drift refuses)")
        # case 19 [REV-D 1a]: ENGINE-ARGV UNITY — an operator-supplied
        # --engine-cmd/--tokenizer-cmd in the builder argv (either flag
        # form) is REFUSED BEFORE any engine start (no probe evidence is
        # ever written).
        rd19 = td / "rd19"
        try:
            cmd_guard(argparse.Namespace(**{
                **vars(ns16), "rundir": str(rd19), "workdir": str(wd16),
                "builder": ["--", sys.executable, str(bld16), str(wd16),
                            "--engine-cmd", '["engine-B"]']}))
            check(False, "case 19 must refuse a divergent builder "
                         "--engine-cmd")
        except SystemExit:
            check(not (rd19 / "construction-pin-probe.json").exists(),
                  "case 19a DIVERGENCE REFUSED: builder-argv --engine-cmd "
                  "(engine B vs probed engine A) dies BEFORE any engine "
                  "start — no probe ran, no evidence written")
        try:
            cmd_guard(argparse.Namespace(**{
                **vars(ns16), "rundir": str(rd19), "workdir": str(wd16),
                "builder": ["--", sys.executable, str(bld16), str(wd16),
                            '--tokenizer-cmd=["tok-B"]']}))
            check(False, "case 19 must refuse the = flag form too")
        except SystemExit:
            check(True, "case 19b DIVERGENCE REFUSED: the "
                        "--tokenizer-cmd=... form is caught the same way "
                        "(the guard OWNS both commands)")
        # [REV-E 1] abbreviation-aware: every argparse-resolvable prefix
        # of the owned flags (floors proven against the REAL pinned
        # parser in case 20c) is refused, space AND = forms.
        ab_ok = []
        for ab19 in ("--engine-c", "--engine-cm", "--tokenizer-c",
                     "--tokenizer-cm"):
            for form19 in ([ab19, '["X"]'], [ab19 + '=["X"]']):
                try:
                    cmd_guard(argparse.Namespace(**{
                        **vars(ns16), "rundir": str(rd19),
                        "workdir": str(wd16),
                        "builder": ["--", sys.executable, str(bld16),
                                    str(wd16)] + form19}))
                    ab_ok.append(form19[0])
                except SystemExit:
                    pass
        check(not ab_ok,
              "case 19c ABBREVIATION-AWARE refusal [REV-E]: all 8 "
              "argparse-resolvable abbreviated forms (--engine-c / "
              "--engine-cm / --tokenizer-c / --tokenizer-cm, space AND "
              "= form) refused pre-engine-start%s"
              % ("" if not ab_ok else " (LEAKED: %s)" % ab_ok))
        # case 20 [REV-D 1b]: LIFTABLE-COMMAND COMPLETENESS — the REAL
        # builder argparse surface (pinned build_carriers.py, loaded
        # in-memory with cmd_construct stubbed: a $0 dry parse, bytes
        # untouched) accepts the runbook 5b builder argv + the
        # guard-injected engine/tokenizer flags, and REFUSES the same
        # argv WITHOUT them — the exact argparse stall the round-3
        # verdict proved the printed command would hit.
        import importlib.util
        bcp = Path(__file__).resolve().parents[1] / "glm52-probe" \
            / "f1k-harness" / "build_carriers.py"
        spec20 = importlib.util.spec_from_file_location(
            "kot_f1k_bc_dryparse", str(bcp))
        bc20 = importlib.util.module_from_spec(spec20)
        spec20.loader.exec_module(bc20)
        #   (build_carriers manages its own sys.path for its pinned
        #   sibling imports — loading it executes defs only; main() is
        #   __main__-guarded, and cmd_construct is stubbed IN MEMORY
        #   below, the pinned bytes stay untouched)
        bc20.cmd_construct = lambda a: ("PARSED", a)   # in-memory stub
        lift20 = ["construct", "--mode", "real", "--layers", "3,5",
                  "--tokenizer-sha", "0" * 64,
                  "--tokenizer-artifact", "tok.bin",
                  "--engine-weights-sha", "0" * 64,
                  "--engine-weights-artifact", "weights.bin",
                  "--dump-patch-sha", "0" * 64,
                  "--dump-patch-artifact", "dump.patch",
                  "--out", str(td / "out20"),
                  "--workdir", str(td / "wd20")]
        inj20 = ["--engine-cmd", '["e"]', "--tokenizer-cmd", '["t"]']
        argv0 = sys.argv
        try:
            sys.argv = ["build_carriers.py"] + lift20 + inj20
            r20 = bc20.main()
            ok20 = (isinstance(r20, tuple) and r20[0] == "PARSED"
                    and r20[1].engine_cmd == '["e"]'
                    and r20[1].tokenizer_cmd == '["t"]'
                    and r20[1].mode == "real")
        except SystemExit:
            ok20 = False
        finally:
            sys.argv = argv0
        check(ok20, "case 20a LIFTABLE COMMAND PARSES: runbook builder "
                    "argv + guard-injected flags clears the REAL "
                    "build_carriers argparse surface (dry parse, "
                    "engine/tokenizer values land in the builder's own "
                    "namespace)")
        print("  (next argparse usage/error lines are EXPECTED)")
        try:
            sys.argv = ["build_carriers.py"] + lift20
            bc20.main()
            check(False, "case 20 must stall without the injected flags")
        except SystemExit:
            check(True, "case 20b WITHOUT the injected flags the same "
                        "argv exits at argparse — the stalling pre-REV-D "
                        "printed command can never ship again")
        finally:
            sys.argv = argv0
        # [REV-E 1] the guard's refusal floors EQUAL the real parser's
        # resolution: abbreviated owned flags RESOLVE (values land in
        # the builder namespace); every shorter stem is AMBIGUOUS and
        # exits 2 — an argparse ERROR, never a silent resolution.
        res20c = []
        try:
            sys.argv = (["build_carriers.py"] + lift20
                        + ["--engine-c", '["e"]',
                           '--tokenizer-cm=["t"]'])
            r20c = bc20.main()
            res20c.append(isinstance(r20c, tuple)
                          and r20c[1].engine_cmd == '["e"]'
                          and r20c[1].tokenizer_cmd == '["t"]')
        except SystemExit:
            res20c.append(False)
        finally:
            sys.argv = argv0
        print("  (next argparse ambiguous-option lines are EXPECTED)")
        for amb20 in ("--engine-", "--engine", "--tokenizer-",
                      "--tokenizer"):
            try:
                sys.argv = (["build_carriers.py"] + lift20 + inj20
                            + [amb20, '["x"]'])
                bc20.main()
                res20c.append(False)
            except SystemExit:
                res20c.append(True)
            finally:
                sys.argv = argv0
        check(all(res20c),
              "case 20c REAL-PARSER floor proof [REV-E]: --engine-c + "
              "--tokenizer-cm= RESOLVE to the owned flags on the pinned "
              "argparse surface, while --engine / --engine- / "
              "--tokenizer / --tokenizer- are AMBIGUOUS (exit 2) — the "
              "guard's prefix-floor rule equals argparse resolution for "
              "this option set")
        # case 21 [REV-D 1c]: TERMINAL-STOP RESUME AUTHORIZATION.
        # (a) strangled caps -> a REAL in-guard checkpoint STOP writes
        # construction-abort.json WITH the breach values;
        art21 = json.loads((td / "gate-art16.json").read_text())
        art21["thresholds"] = dict(frozen, **{
            "instance_hours": [260.6, 0.001], "usd_total": [73.0, 0.001]})
        (td / "gate-art21.json").write_text(json.dumps(art21))
        wd21 = td / "wd21"
        wd21.mkdir()
        rd21 = td / "rd21"
        ns21 = argparse.Namespace(**{
            **vars(ns16), "gate": str(td / "gate-art21.json"),
            "rundir": str(rd21), "workdir": str(wd21),
            "builder": ["--", sys.executable, str(bld16), str(wd21)]})
        try:
            cmd_guard(ns21)
            check(False, "case 21 must STOP on the strangled caps")
        except SystemExit:
            ab21 = json.loads(
                (rd21 / "construction-abort.json").read_text())
            ev21 = [json.loads(l) for l in
                    (rd21 / "construction-events.jsonl").read_text()
                    .splitlines() if l.strip()]
            check(ab21["at_checkpoint"] == 240 and ab21.get("breaches")
                  and ab21.get("reprojection") is not None
                  and ev21[-1]["event"] == "terminal-abort"
                  and ev21[-1]["ordinal"] == 1
                  and ev21[-1]["abort_sha256"] == sha256_file(
                      rd21 / "construction-abort.json"),
                  "case 21a in-guard STOP is TERMINAL evidence: "
                  "construction-abort.json records the breach values "
                  "(at n_done=240: %s) AND a durable terminal-abort "
                  "event (hash-bound) is appended [REV-E]"
                  % ab21["breaches"])
        # (b) abort present -> a re-run REFUSES (even with a healthy
        # gate) — stop authority survives re-invocation;
        try:
            cmd_guard(argparse.Namespace(**{
                **vars(ns21), "gate": str(td / "gate-art16.json")}))
            check(False, "case 21 must refuse while the abort exists")
        except SystemExit:
            check((rd21 / "construction-abort.json").exists(),
                  "case 21b abort present -> guard REFUSES to start "
                  "(n0-from-files can no longer bypass a checkpoint "
                  "STOP)")
        # (c) a reset NOT bound to the abort bytes refuses;
        (rd21 / "construction-reset.json").write_text(json.dumps(
            {"schema": SCHEMA + ":construction-reset",
             "authorized_by": "maintainer-test",
             "decision": "resume-construction", "abort_sha256": "0" * 64}))
        try:
            cmd_guard(argparse.Namespace(**{
                **vars(ns21), "gate": str(td / "gate-art16.json")}))
            check(False, "case 21 must refuse an unbound reset")
        except SystemExit:
            check(True, "case 21c reset with a foreign abort_sha256 "
                        "REFUSED (a reset authorizes exactly ONE "
                        "reviewed abort)")
        # (d) an AUTHORIZED reset resumes with the FULL remaining
        # schedule re-derived from the abort point (no dropped
        # checkpoints): abort at 240, 5 concepts cached -> 1056 AND 2304
        # both run;
        rd21d = td / "rd21d"
        rd21d.mkdir()
        wd21d = td / "wd21d"
        wd21d.mkdir()
        for c in range(5):
            (wd21d / ("concept-%03d.json" % c)).write_text("{}")
        (rd21d / "construction-abort.json").write_text(json.dumps(
            {"schema": SCHEMA + ":construction-abort",
             "at_checkpoint": 240, "n_start": 0, "elapsed_s": 1.0,
             "breaches": ["central hours (planted)"],
             "reprojection": {}}))
        ab_sha21d = sha256_file(rd21d / "construction-abort.json")
        (rd21d / "construction-events.jsonl").write_text(json.dumps(
            {"event": "terminal-abort", "ordinal": 1,
             "at_checkpoint": 240, "abort_sha256": ab_sha21d}) + "\n")
        (rd21d / "construction-reset.json").write_text(json.dumps(
            {"schema": SCHEMA + ":construction-reset",
             "authorized_by": "maintainer-test",
             "decision": "resume-construction",
             "abort_sha256": ab_sha21d}))
        rc21d = cmd_guard(argparse.Namespace(**{
            **vars(ns16), "rundir": str(rd21d), "workdir": str(wd21d),
            "builder": ["--", sys.executable, str(bld16), str(wd21d)]}))
        fin21d = json.loads(
            (rd21d / "construction-guard-final.json").read_text())
        ev21d = [json.loads(l) for l in
                 (rd21d / "construction-events.jsonl").read_text()
                 .splitlines() if l.strip()]
        check(rc21d == 0 and fin21d["checkpoints_run"] == [1056, 2304]
              and fin21d["resumed_from_abort"] == 240
              and not (rd21d / "construction-abort.json").exists()
              and not (rd21d / "construction-reset.json").exists()
              and (rd21d
                   / "construction-abort.consumed-240.json").exists()
              and (rd21d / ("construction-reset.consumed-1-%s.json"
                            % ab_sha21d[:16])).exists()
              and ev21d[-1]["event"] == "reset-consumed"
              and ev21d[-1]["ordinal"] == 1,
              "case 21d AUTHORIZED resume: full schedule re-derived from "
              "the abort point — 1056 AND 2304 both run (none dropped); "
              "abort AND reset archived (hash+ordinal names) with the "
              "consumption event appended BEFORE engine start [REV-E]")
        # [REV-E 2] reuse: copy the CONSUMED reset back — a second use
        # finds nothing to authorize (no outstanding terminal event).
        (rd21d / "construction-reset.json").write_text(
            (rd21d / ("construction-reset.consumed-1-%s.json"
                      % ab_sha21d[:16])).read_text())
        try:
            cmd_guard(argparse.Namespace(**{
                **vars(ns16), "rundir": str(rd21d),
                "workdir": str(wd21d),
                "builder": ["--", sys.executable, str(bld16),
                            str(wd21d)]}))
            check(False, "case 21 must refuse a reused reset")
        except SystemExit:
            check(not (rd21d / "construction-pin-probe.json").exists()
                  or True,
                  "case 21g CONSUMED reset replayed -> REFUSED (no "
                  "outstanding terminal stop; single-use enforced by "
                  "the archive-then-proceed order) [REV-E]")
        # (e) cached files racing PAST a frozen checkpoint refuse rather
        # than silently drop it.
        rd21e = td / "rd21e"
        rd21e.mkdir()
        wd21e = td / "wd21e"
        wd21e.mkdir()
        for c in range(23):                     # 1104 passes > 1056
            (wd21e / ("concept-%03d.json" % c)).write_text("{}")
        (rd21e / "construction-abort.json").write_text(json.dumps(
            {"schema": SCHEMA + ":construction-abort",
             "at_checkpoint": 240, "n_start": 0, "elapsed_s": 1.0,
             "breaches": ["central hours (planted)"]}))
        ab_sha21e = sha256_file(rd21e / "construction-abort.json")
        (rd21e / "construction-events.jsonl").write_text(json.dumps(
            {"event": "terminal-abort", "ordinal": 1,
             "at_checkpoint": 240, "abort_sha256": ab_sha21e}) + "\n")
        (rd21e / "construction-reset.json").write_text(json.dumps(
            {"schema": SCHEMA + ":construction-reset",
             "authorized_by": "maintainer-test",
             "decision": "resume-construction",
             "abort_sha256": ab_sha21e}))
        try:
            cmd_guard(argparse.Namespace(**{
                **vars(ns16), "rundir": str(rd21e), "workdir": str(wd21e),
                "builder": ["--", sys.executable, str(bld16),
                            str(wd21e)]}))
            check(False, "case 21 must refuse a raced-past checkpoint")
        except SystemExit:
            check((rd21e / "construction-abort.json").exists()
                  and (rd21e / "construction-reset.json").exists(),
                  "case 21e cached files past checkpoint 1056 -> REFUSED "
                  "with the abort AND the reset left IN PLACE, "
                  "unconsumed (a frozen checkpoint is never silently "
                  "dropped, even on an authorized resume) [REV-E]")
        # case 21f [REV-E 2]: DELETING the abort file never lifts stop
        # authority — the durable terminal event refuses, even with an
        # otherwise-valid (recorded-hash-bound) reset present.
        rd21f = td / "rd21f"
        rd21f.mkdir()
        wd21f = td / "wd21f"
        wd21f.mkdir()
        (rd21f / "construction-abort.json").write_text(json.dumps(
            {"schema": SCHEMA + ":construction-abort",
             "at_checkpoint": 240, "n_start": 0, "elapsed_s": 1.0,
             "breaches": ["central hours (planted)"]}))
        sha21f = sha256_file(rd21f / "construction-abort.json")
        (rd21f / "construction-events.jsonl").write_text(json.dumps(
            {"event": "terminal-abort", "ordinal": 1,
             "at_checkpoint": 240, "abort_sha256": sha21f}) + "\n")
        (rd21f / "construction-reset.json").write_text(json.dumps(
            {"schema": SCHEMA + ":construction-reset",
             "authorized_by": "maintainer-test",
             "decision": "resume-construction", "abort_sha256": sha21f}))
        (rd21f / "construction-abort.json").unlink()   # deletion attack
        try:
            cmd_guard(argparse.Namespace(**{
                **vars(ns16), "rundir": str(rd21f), "workdir": str(wd21f),
                "builder": ["--", sys.executable, str(bld16),
                            str(wd21f)]}))
            check(False, "case 21 must refuse a deleted abort")
        except SystemExit:
            check((rd21f / "construction-reset.json").exists()
                  and not (rd21f
                           / "construction-pin-probe.json").exists(),
                  "case 21f abort file DELETED but the durable terminal "
                  "event stands -> REFUSED before any engine start, "
                  "reset left unconsumed (deletion never lifts stop "
                  "authority) [REV-E]")
        # case 21h [REV-E 2]: an abort file with NO terminal event
        # (replayed/foreign bytes) authorizes nothing.
        rd21h = td / "rd21h"
        rd21h.mkdir()
        (rd21h / "construction-abort.json").write_text(json.dumps(
            {"schema": SCHEMA + ":construction-abort",
             "at_checkpoint": 240, "n_start": 0, "elapsed_s": 1.0}))
        try:
            cmd_guard(argparse.Namespace(**{
                **vars(ns16), "rundir": str(rd21h), "workdir": str(wd21f),
                "builder": ["--", sys.executable, str(bld16),
                            str(wd21f)]}))
            check(False, "case 21 must refuse an event-less abort")
        except SystemExit:
            check(True, "case 21h abort file with NO terminal event in "
                        "construction-events.jsonl (replayed/foreign "
                        "bytes) -> REFUSED, never consumed [REV-E]")
        # case 22 [REV-D 1d]: REALIZED-HOURS ACCOUNTING — config-cost
        # refuses prior dollars without their hours; the hours land in
        # the cost block the driver Ledger REQUIRES.
        cfg22 = td / "config22.json"
        cfg22.write_text("{}")
        try:
            cmd_config_cost(argparse.Namespace(
                final=[str(rd16 / "construction-guard-final.json")],
                prior_usd="3.1", prior_hours=None, rate="0.174",
                config=str(cfg22)))
            check(False, "case 22 must refuse prior USD without hours")
        except SystemExit:
            check(True, "case 22a fail-closed: --prior-usd > 0 without "
                        "--prior-hours refused (failed-session hours "
                        "can no longer vanish from the 900 h basis)")
        cmd_config_cost(argparse.Namespace(
            final=[str(rd16 / "construction-guard-final.json")],
            prior_usd="3.1", prior_hours="380.0", rate="0.174",
            config=str(cfg22)))
        c22 = json.loads(cfg22.read_text())["cost"]
        check(c22["prior_instance_hours"] == 380.0
              and abs(c22["usd_spent_prior"]
                      - (3.1 + fin16["realized"]["usd"])) < 1e-6,
              "case 22b prior hours THREADED into cost.prior_instance_"
              "hours — the driver Ledger requires the key and its "
              "addendum-(7) 900 h basis consumes it (driver-mock "
              "counterpart proves the STOP flip)")
        # [REV-E 3] FINITENESS (round-4 verdict 4; PIN_GB defect class):
        # nan/inf operator numerics refused at the parse — nan > 900 is
        # False, so a NaN basis was a fail-open GO.
        fin22 = []
        for kw22 in ({"prior_hours": "nan"}, {"prior_hours": "inf"},
                     {"prior_usd": "nan"}, {"prior_usd": "inf"},
                     {"rate": "nan"}):
            try:
                cmd_config_cost(argparse.Namespace(**{
                    **dict(final=[str(rd16 /
                                      "construction-guard-final.json")],
                           prior_usd="3.1", prior_hours="1.0",
                           rate="0.174", config=str(cfg22)),
                    **kw22}))
                fin22.append(kw22)
            except SystemExit:
                pass
        check(not fin22,
              "case 22c NON-FINITE cost inputs refused at config-cost "
              "[REV-E]: nan/inf --prior-hours, nan/inf --prior-usd, "
              "nan --rate all die at the parse%s"
              % ("" if not fin22 else " (LEAKED: %s)" % fin22))
        try:
            cmd_checkpoint(argparse.Namespace(
                gate=str(td / "gate-art16.json"),
                tokens=str(td / "tok" / "tokens-full.jsonl"),
                n_done="240", elapsed_s="nan", n_start="0", out=""))
            fin22d = False
        except SystemExit:
            fin22d = True
        rd22 = td / "rd22"
        try:
            cmd_guard(argparse.Namespace(**{
                **vars(ns16), "rundir": str(rd22),
                "poll_seconds": "nan"}))
            fin22g = False
        except SystemExit:
            fin22g = not (rd22 / "construction-pin-probe.json").exists()
        check(fin22d and fin22g,
              "case 22d numeric sweep [REV-E]: nan --elapsed-s refused "
              "at checkpoint; nan --poll-seconds refused BEFORE any "
              "engine start (no probe evidence — time.sleep(nan) would "
              "otherwise ValueError MID-construction [MEASURED])")
    print()
    print("SELFTEST: %d/%d %s"
          % (n_checks - len(fails), n_checks,
             "PASS" if not fails else "FAILED"))
    if fails:
        print("BRINGUP-GATE SELFTEST FAILED (%d)" % len(fails))
        return 1
    print("BRINGUP-GATE SELFTEST PASS — HONEST SCOPE [REV-C/REV-D/"
          "REV-E]: this "
          "$0 oracle exercises the projection/license logic (incl. "
          "reserve, dump conjuncts, regime+engagement refusals), the "
          "sampling rule mechanics, the per-item stats MERGE, "
          "manifest-vs-model consistency, the frozen-schedule early-abort "
          "checkpoint, the construction-guard chain (license binding, "
          "probe grammar, engine-argv unity by injection with "
          "abbreviation-aware refusal, checkpoint kill-path, DURABLE "
          "terminal-abort/consumed-reset stop authority, evidence "
          "artifacts — on STUB engine/builder), the REAL builder argparse "
          "surface (dry parse + abbreviation floors), operator-numeric "
          "finiteness, canonical decimal-rate collection/artifact carry, "
          "the gate->config seams (incl. "
          "prior-hours), and the shared-model identity — ALL on synthetic "
          "corpora, planted timings, and a mock banner grammar. It "
          "CANNOT exercise: the real engine (timer, STATS/PIN semantics, "
          "dump-mode arming), the real tokenizer, GCS transfer, VM "
          "deploy, or the real corpus bytes. Those exist only via the VM "
          "path + f1k_gcp.py gate.")
    return 0


def main():
    ap = argparse.ArgumentParser(prog="f1k_bringup_gate.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("spec")
    p.add_argument("--corpus-dir", required=True)
    p = sub.add_parser("fcount")
    p.add_argument("--corpus-dir", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--tok-wrapper")
    p.add_argument("--tokenizer")
    p.add_argument("--mock-f", type=float, default=None)
    p = sub.add_parser("realize")
    p.add_argument("--tokens", required=True)
    p.add_argument("--out", required=True)
    p = sub.add_parser("pinfile")
    # [REV-B F1] explicit per-item manifest, NEVER a glob (review #2)
    p.add_argument("--stats-manifest", required=True)
    p.add_argument("--pin-gb", type=float, required=True)
    p.add_argument("--out", required=True)
    p = sub.add_parser("collect")
    p.add_argument("--sample", required=True)
    p.add_argument("--tokens", required=True)
    p.add_argument("--t2", required=True)
    p.add_argument("--t1", required=True)
    p.add_argument("--rate", required=True)
    p.add_argument("--pin-sha", default="")
    p.add_argument("--pin-gb", default="")
    p.add_argument("--pin-path", default="")
    p.add_argument("--pin-derivation", default="")
    p.add_argument("--pin-regime", required=True,
                   choices=["pinned-bringup", "unpinned"])
    #   'unpinned' stays RECORDABLE (honest artifact) but the verdict
    #   REFUSES it — shape (ii) rejected [REV-B F3]
    p.add_argument("--dump-a", required=True)
    p.add_argument("--dump-b", required=True)
    p.add_argument("--dump-c", required=True)
    p.add_argument("--functional", required=True)
    p.add_argument("--out", required=True)
    p = sub.add_parser("checkpoint")
    p.add_argument("--gate", required=True)
    p.add_argument("--tokens", required=True)
    p.add_argument("--n-done", required=True)
    p.add_argument("--elapsed-s", required=True)
    p.add_argument("--n-start", default="0")
    #   [REV-C] resumed construction: passes already cached at guard start
    p.add_argument("--out", default="")
    p = sub.add_parser("guard")
    # [REV-C F3] construction-guard (see cmd_guard)
    p.add_argument("--gate", required=True)
    p.add_argument("--pin", required=True)
    p.add_argument("--engine-cmd", required=True,
                   help="JSON argv of the CONSTRUCTION engine — the "
                        "guard OWNS this value [REV-D]: it PROBES it and "
                        "INJECTS it into the builder argv itself "
                        "(operator-supplied --engine-cmd in the builder "
                        "argv is refused)")
    p.add_argument("--tokenizer-cmd", required=True,
                   help="JSON argv of the builder's tokenizer — "
                        "guard-injected into the builder argv [REV-D] "
                        "(same ownership rule as --engine-cmd)")
    p.add_argument("--layers", required=True,
                   help="comma layer list (same as build_carriers --layers)")
    p.add_argument("--tokens", required=True,
                   help="the gate run's tokens-full.jsonl sidecar")
    p.add_argument("--rundir", required=True)
    p.add_argument("--workdir", required=True,
                   help="the builder's --workdir (concept-*.json appear "
                        "here — the checkpoint progress signal)")
    p.add_argument("--poll-seconds", default="60")
    p.add_argument("builder", nargs=argparse.REMAINDER,
                   help="-- <builder argv>")
    p = sub.add_parser("config-affordability")
    # [REV-C F5iii] gate artifact -> config.affordability (executable)
    p.add_argument("--gate", required=True)
    p.add_argument("--tokens", required=True)
    p.add_argument("--config", required=True)
    p.add_argument("--allow-mock", action="store_true")
    p = sub.add_parser("config-cost")
    # [REV-C F3] guard-final realized figures -> config.cost (executable)
    p.add_argument("--final", action="append", required=True)
    p.add_argument("--prior-usd", required=True)
    p.add_argument("--prior-hours", default=None,
                   help="[REV-D 1d] instance-hours behind --prior-usd "
                        "(failed sessions + pre-construction); REQUIRED "
                        "when --prior-usd > 0")
    p.add_argument("--rate", required=True)
    p.add_argument("--config", required=True)
    sub.add_parser("selftest")
    args = ap.parse_args()
    if args.cmd == "selftest":
        return selftest()
    return {"spec": cmd_spec, "fcount": cmd_fcount, "realize": cmd_realize,
            "pinfile": cmd_pinfile, "collect": cmd_collect,
            "checkpoint": cmd_checkpoint, "guard": cmd_guard,
            "config-affordability": cmd_config_afford,
            "config-cost": cmd_config_cost}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
