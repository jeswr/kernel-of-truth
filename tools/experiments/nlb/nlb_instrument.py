#!/usr/bin/env python3
"""nlb_instrument — NL-boundary run (records l3a-parse / a5-nl, DRAFT).

    python3 tools/experiments/nlb/nlb_instrument.py --vertical l3a --mock
    python3 tools/experiments/nlb/nlb_instrument.py --vertical a5 \
        --arm mapper-parse --phrasings data/nlb-phrasings-a5/eval.jsonl \
        [--phase final]

RAW OUTPUT ONLY (P2 section 2.4): emits one kot-log/1 record BODY (counts,
pins, config) on stdout; renders NO verdict and knows nothing about the
pre-registered thresholds (DRAFT records registry/experiments/l3a-parse.json
and a5-nl.json; applied by verdict-gen through the pinned analysis scripts).

Arms (design doc docs/design-nl-boundary-l3a-parse-a5-nl.md section 6.4):
  mapper-parse      the pipeline under test: gazetteer + mapper a1-hybrid +
                    closed frame layer (nlb_frontend) -> byte-identical engine.
  gold-replication  measured-ceiling arm: the parent's FULL gold eval (incl.
                    malformed) on the byte-identical engine — instrument gate
                    G2 requires the parent-perfect outcome.
  deranged-lexicon  scramble control (gate G5): seed-0 fixed-point-free
                    rotation of concept bindings (nlb_map.mjs) and, on the a5
                    vertical, of the relational-op bindings (nlb_frontend).
  abstain-all       trivial policy: refuses every phrasing.
  answer-all        trivial policy: never refuses; parses, then fabricates
                    deterministically wherever the pipeline would refuse.

Scoring (pre-declared, design doc section 6): the NL leg uses the INCLUDED
slice (malformed stratum excluded, FK-NLB-5). Covered exact is scored EXACTLY
as the frozen parents (answer + expected value + provenance in world store +
non-empty license; provenance required on mapper-parse/deranged/gold arms).
Control 'acceptable' refusal = expected engine ERR_* code OR ERR_PARSE
(FK-NLB-6); strict engine-code match reported alongside. The fail-closed
split reports covered wrong-answers (dangerous, gated S2) separately from
refusals (safe), with ERR_PARSE stage tags for stage indictment.

Deterministic: no RNG anywhere; the full pass runs TWICE and is byte-compared
(metrics.deterministic_repeat_identical). --mock uses quarantined scaffold
phrasings (gen_mock_phrasings) and asserts MECHANICS ONLY ($0, no freeze).
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "axiom"))
sys.path.insert(0, os.path.join(_ROOT, "tools", "registry"))
sys.path.insert(0, _HERE)

import kot_axiom  # noqa: E402
import kot_code  # noqa: E402
import kot_common  # noqa: E402
import nlb_frontend  # noqa: E402
import gen_mock_phrasings  # noqa: E402

ARMS = ("mapper-parse", "gold-replication", "deranged-lexicon",
        "abstain-all", "answer-all")
GLOBAL_DEFAULT_GUESS = None


class L3aOracle(object):
    """Adapter giving the l3a engine the same surface as kot_code.CodeOracle."""

    def __init__(self, root):
        axioms, world = kot_axiom.load_corpora(root)
        self.engine = kot_axiom.Engine(axioms, world)

    def desugar(self, q):
        return q  # kot-query/1 is already core; engine validates fail-closed

    def query(self, q):
        return self.engine.query(q)


def build_oracle(root, vertical):
    return L3aOracle(root) if vertical == "l3a" else kot_code.build_code_oracle(root)


def load_eval(root, vertical):
    path = os.path.join(root, "data",
                        "l3a-eval" if vertical == "l3a" else "a5-eval",
                        "queries.jsonl")
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def fabricate(oracle, query):
    """answer-all fabrication, parents' policy carried over (deterministic)."""
    r = oracle.query(query)
    if r["status"] == "answer":
        return r
    core = oracle.desugar(query)
    value = GLOBAL_DEFAULT_GUESS
    if core.get("status") != "refuse":
        try:
            op = core.get("op")
            if op in ("unique", "lookup"):
                edges = oracle.engine._edges(core.get("rel", ""),
                                             core.get("subject", ""),
                                             core.get("direction", "forward"))
                objs = sorted(set(o for (o, _ref) in edges))
                value = ((objs[0] if objs else GLOBAL_DEFAULT_GUESS)
                         if op == "unique" else objs)
            elif op == "count":
                value = len(oracle.engine._qualified_edges(
                    core.get("rel", ""), core.get("subject", ""),
                    core.get("direction", "forward"), core.get("qualifier")))
            elif op == "instance":
                value = core.get("concept") in \
                    oracle.engine.classes.get(core.get("entity", ""), {})
        except Exception:
            value = GLOBAL_DEFAULT_GUESS
    return {"status": "answer", "value": value,
            "provenance": [], "license": ["fabricated"]}


def run_nl_arm(oracle, included, phrasing_by_qid, vertical, arm):
    """-> {qid: outcome}; outcome is a parse refusal (with .stage) or an
    engine/policy result dict."""
    if arm == "abstain-all":
        return {r["qid"]: {"status": "refuse", "code": "ABSTAIN",
                           "reason": "policy"} for r in included}
    phrasings = [{"qid": r["qid"], "text": phrasing_by_qid[r["qid"]]}
                 for r in included]
    parses = nlb_frontend.parse_all(
        phrasings, vertical, oracle.engine.entities,
        derange=(arm == "deranged-lexicon"))
    out = {}
    for r in included:
        p = parses[r["qid"]]
        if p["status"] == "refuse":
            if arm == "answer-all":  # unparseable: fabricate the global default
                out[r["qid"]] = {"status": "answer",
                                 "value": GLOBAL_DEFAULT_GUESS,
                                 "provenance": [], "license": ["fabricated"]}
            else:
                out[r["qid"]] = p
        else:
            q = p["query"]
            out[r["qid"]] = (fabricate(oracle, q) if arm == "answer-all"
                             else oracle.query(q))
    return out


def build_labelmap(root, vertical, ev):
    """qid -> the item's relation/concept label string for the descriptive
    label-verbatim vs paraphrase stratification (raw counts only; the rule is
    pre-declared in the design doc section 6 endnote): l3a items use the
    rel/concept sourceId; a5 instance items use the concept sourceId; a5
    relational-op items use the op's head keyword STEM (the op is carried by
    frame keywords on that vertical — registered honesty note)."""
    urn2label = nlb_frontend._load_labels(root)
    a5_head = {"callers-of": "call", "callees-of": "call",
               "imports-of": "import", "imported-by": "import",
               "contains": "contain", "contained-in": "contain",
               "where-defined": "defined"}
    out = {}
    for rec in ev:
        q = rec.get("query") or {}
        if vertical == "l3a":
            out[rec["qid"]] = urn2label.get(q.get("rel") or q.get("concept"))
        elif q.get("op") == "instance-of":
            out[rec["qid"]] = urn2label.get(q.get("concept"))
        else:
            out[rec["qid"]] = a5_head.get(q.get("op"))
    return out


def label_verbatim(text, label):
    """True iff the item's label surface form (spaced or raw sourceId; stem
    substring for the a5 op-head keywords) occurs in the phrasing."""
    if not label:
        return False
    low = text.lower()
    return (label.replace("-", " ") in low) or (label in low)


def score_nl(included, outcomes, arm, world_ids, labelmap=None, texts=None):
    require_prov = arm in ("mapper-parse", "deranged-lexicon")
    m = {"n_covered": 0, "n_covered_exact": 0,
         "n_covered_refused_parse": 0, "n_covered_refused_engine": 0,
         "n_covered_answered_wrong": 0,
         "n_control": 0, "n_control_refused_acceptable": 0,
         "n_control_refused_strict_engine_code": 0,
         "n_control_refused_parse": 0,
         "n_control_refused_other": 0, "n_control_answered": 0,
         "parse_stage_breakdown": {}, "by_family": {},
         "label_strata": {"verbatim": {"n": 0, "exact": 0},
                          "paraphrase": {"n": 0, "exact": 0}}}
    for rec in included:
        r = outcomes[rec["qid"]]
        fam = m["by_family"].setdefault(rec["family"], {"n": 0, "ok": 0})
        fam["n"] += 1
        exp = rec["expected"]
        is_parse_refusal = r.get("code") == "ERR_PARSE"
        if is_parse_refusal:
            st = r.get("stage", "unknown")
            m["parse_stage_breakdown"][st] = \
                m["parse_stage_breakdown"].get(st, 0) + 1
        if rec["class"] == "covered":
            m["n_covered"] += 1
            stratum = None
            if labelmap is not None and texts is not None:
                verb = label_verbatim(texts.get(rec["qid"], ""),
                                      labelmap.get(rec["qid"]))
                stratum = m["label_strata"]["verbatim" if verb
                                            else "paraphrase"]
                stratum["n"] += 1
            if r["status"] != "answer":
                if is_parse_refusal:
                    m["n_covered_refused_parse"] += 1
                else:
                    m["n_covered_refused_engine"] += 1
            else:
                exact = r["value"] == exp["value"]
                if require_prov:
                    exact = exact and bool(r.get("provenance")) and \
                        bool(r.get("license")) and \
                        all(p in world_ids for p in r["provenance"])
                if exact:
                    m["n_covered_exact"] += 1
                    fam["ok"] += 1
                    if stratum is not None:
                        stratum["exact"] += 1
                else:
                    m["n_covered_answered_wrong"] += 1
        else:
            m["n_control"] += 1
            if r["status"] == "answer":
                m["n_control_answered"] += 1
            elif is_parse_refusal or r.get("code") == "ABSTAIN":
                m["n_control_refused_acceptable"] += 1
                if is_parse_refusal:
                    m["n_control_refused_parse"] += 1
                fam["ok"] += 1
            elif r.get("code") == exp.get("code"):
                m["n_control_refused_acceptable"] += 1
                m["n_control_refused_strict_engine_code"] += 1
                fam["ok"] += 1
            else:
                m["n_control_refused_other"] += 1
    m["n_control_refused_any"] = (m["n_control_refused_acceptable"] +
                                  m["n_control_refused_other"])
    return m


def score_gold(queries, results, world_ids):
    """Parent-style scoring over the FULL eval (incl. malformed) — gate G2."""
    m = {"n_covered": 0, "n_covered_exact": 0, "n_covered_refused": 0,
         "n_covered_answered_wrong": 0, "n_control": 0,
         "n_control_refused_correct_code": 0,
         "n_control_refused_other_code": 0, "n_control_answered": 0}
    for rec, r in zip(queries, results):
        exp = rec["expected"]
        if rec["class"] == "covered":
            m["n_covered"] += 1
            if r["status"] != "answer":
                m["n_covered_refused"] += 1
            elif r["value"] == exp["value"] and bool(r.get("provenance")) and \
                    bool(r.get("license")) and \
                    all(p in world_ids for p in r["provenance"]):
                m["n_covered_exact"] += 1
            else:
                m["n_covered_answered_wrong"] += 1
        else:
            m["n_control"] += 1
            if r["status"] == "answer":
                m["n_control_answered"] += 1
            elif r["code"] == exp.get("code"):
                m["n_control_refused_correct_code"] += 1
            else:
                m["n_control_refused_other_code"] += 1
    return m


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run_once(root, vertical, arm, phrasing_by_qid):
    oracle = build_oracle(root, vertical)
    ev = load_eval(root, vertical)
    included = [r for r in ev if r["family"] != "malformed"]
    t0 = time.perf_counter_ns()
    if arm == "gold-replication":
        results = [oracle.query(rec["query"]) for rec in ev]
        t1 = time.perf_counter_ns()
        metrics = score_gold(ev, results, oracle.engine.world_ids)
        return metrics, results, t1 - t0
    outcomes = run_nl_arm(oracle, included, phrasing_by_qid, vertical, arm)
    t1 = time.perf_counter_ns()
    metrics = score_nl(included, outcomes, arm, oracle.engine.world_ids,
                       labelmap=build_labelmap(root, vertical, ev),
                       texts=phrasing_by_qid)
    return metrics, outcomes, t1 - t0


def corpus_dir(root, vertical):
    return os.path.join(root, "data", "nlb-phrasings-%s" % vertical)


def run_dev_pass(root, vertical, oracle):
    """G4 instrument quantity: front-end parse-failure rate on the committed
    DEV corpus (fresh identities disjoint from every scored item; gazetteer =
    world entities + the DEV-only entity list — never used by scored arms)."""
    base = corpus_dir(root, vertical)
    dev_path = os.path.join(base, "dev.jsonl")
    ent_path = os.path.join(base, "dev-entities.jsonl")
    if not (os.path.isfile(dev_path) and os.path.isfile(ent_path)):
        return None
    with open(dev_path, "r", encoding="utf-8") as f:
        dev = [json.loads(l) for l in f if l.strip()]
    with open(ent_path, "r", encoding="utf-8") as f:
        dev_ents = [json.loads(l)["urn"] for l in f if l.strip()]
    gaz = sorted(set(oracle.engine.entities) | set(dev_ents))
    parses = nlb_frontend.parse_all(
        [{"qid": r["qid"], "text": r["text"]} for r in dev],
        vertical, gaz, root=root)
    stage = {}
    refused = 0
    for r in dev:
        p = parses[r["qid"]]
        if p["status"] == "refuse":
            refused += 1
            st = p.get("stage", "unknown")
            stage[st] = stage.get(st, 0) + 1
    return {"dev_n": len(dev), "dev_parse_refused": refused,
            "dev_stage_breakdown": stage}


def run_probe_pass(root, vertical, oracle, included):
    """Synonym-boundary probe (descriptive ONLY, never gated, carved out of
    the envelope): second no-label phrasings over a covered-qid sample."""
    probe_path = os.path.join(corpus_dir(root, vertical), "probe.jsonl")
    if not os.path.isfile(probe_path):
        return None
    with open(probe_path, "r", encoding="utf-8") as f:
        probe = [json.loads(l) for l in f if l.strip()]
    by_qid = {r["qid"]: r for r in included}
    parses = nlb_frontend.parse_all(
        [{"qid": r["qid"], "text": r["text"]} for r in probe],
        vertical, oracle.engine.entities, root=root)
    n_ok = n_exact = 0
    for r in probe:
        p = parses[r["qid"]]
        rec = by_qid.get(r["qid"])
        if p["status"] != "parse" or rec is None:
            continue
        n_ok += 1
        res = oracle.query(p["query"])
        if res["status"] == "answer" and \
                res["value"] == rec["expected"]["value"] and \
                bool(res.get("provenance")) and bool(res.get("license")):
            n_exact += 1
    return {"probe_n": len(probe), "probe_parse_ok": n_ok,
            "probe_exact": n_exact}


def one_arm_body(root, vertical, arm, phrasing_by_qid, phase, phrasings_path):
    metrics, out1, elapsed = run_once(root, vertical, arm, phrasing_by_qid)
    _m2, out2, _e2 = run_once(root, vertical, arm, phrasing_by_qid)
    deterministic = (json.dumps(out1, sort_keys=True, default=str) ==
                     json.dumps(out2, sort_keys=True, default=str))
    metrics["frontend_total_ns"] = elapsed
    metrics["deterministic_repeat_identical"] = bool(deterministic)
    if arm == "mapper-parse":
        oracle = build_oracle(root, vertical)
        included = [r for r in load_eval(root, vertical)
                    if r["family"] != "malformed"]
        dev = run_dev_pass(root, vertical, oracle)
        if dev is not None:
            metrics.update(dev)
        probe = run_probe_pass(root, vertical, oracle, included)
        if probe is not None:
            metrics.update(probe)
    exp_id = "l3a-parse" if vertical == "l3a" else "a5-nl"
    corpora = (("axioms-v0", "world-v0", "l3a-eval", "kernel-v0",
                "molecules-v0") if vertical == "l3a" else
               ("code-axioms-v0", "code-world-v0", "a5-eval", "kernel-v0",
                "molecules-v0", "code-v0", "code-corpus-v0"))
    pins = {"_recipe": kot_common.CORPUS_RECIPE}
    for c in corpora:
        pins["corpus_%s" % c] = {"observed": kot_common.corpus_hash(root, c),
                                 "recipe": "kot-corpus-hash/1"}
    pins["engine"] = {"observed": file_sha256(
        os.path.join(root, "tools", "axiom", "kot_axiom.py"))}
    if vertical == "a5":
        pins["code_layer"] = {"observed": file_sha256(
            os.path.join(root, "tools", "axiom", "kot_code.py"))}
    for name in ("nlb_instrument.py", "nlb_frontend.py", "nlb_map.mjs"):
        pins[name] = {"observed": file_sha256(os.path.join(_HERE, name))}
    if phrasings_path and os.path.isfile(phrasings_path):
        pins["phrasings_file"] = {"observed": file_sha256(phrasings_path)}
    base = corpus_dir(root, vertical)
    for name in ("dev.jsonl", "dev-entities.jsonl", "probe.jsonl",
                 "eval.jsonl", "manifest.json"):
        p = os.path.join(base, name)
        if os.path.isfile(p):
            pins["corpus_file_%s" % name] = {"observed": file_sha256(p)}
    lint_path = os.path.join(base, "lint-receipt.json")
    if os.path.isfile(lint_path):
        with open(lint_path, "r", encoding="utf-8") as f:
            lint = json.load(f)
        pins["phrasings_lint"] = {"observed": file_sha256(lint_path),
                                  "green": bool(lint.get("green"))}
    return {
        "experiment": exp_id, "phase": phase, "arm": arm,
        "config": {"vertical": vertical, "arm": arm,
                   "phrasings": phrasings_path,
                   "frame_rules": "DRAFT-v0 (pre-freeze; see design doc 5.3)",
                   "host": platform.node()},
        "metrics": metrics, "pins_observed": pins,
    }


def load_phrasings(path):
    with open(path, "r", encoding="utf-8") as f:
        recs = [json.loads(l) for l in f if l.strip()]
    return {r["qid"]: r["text"] for r in recs}


def run_mock(root, vertical):
    """Green-mock: mechanics only, $0. Quarantined scaffold phrasings."""
    phr = gen_mock_phrasings.generate(root, vertical)
    mock_dir = os.path.join(root, "poc", "nlb-mock", vertical)
    os.makedirs(mock_dir, exist_ok=True)
    ppath = os.path.join(mock_dir, "phrasings.jsonl")
    with open(ppath, "w", encoding="utf-8") as f:
        for p in phr:
            f.write(json.dumps(p, sort_keys=True) + "\n")
    phrasing_by_qid = {p["qid"]: p["text"] for p in phr}

    ev = load_eval(root, vertical)
    included = [r for r in ev if r["family"] != "malformed"]
    n_cov = sum(1 for r in included if r["class"] == "covered")
    n_ctl = len(included) - n_cov
    want = {"l3a": (600, 270, 600, 300), "a5": (855, 106, 855, 122)}[vertical]

    checks, bodies = {}, {}
    for arm in ARMS:
        bodies[arm] = one_arm_body(root, vertical, arm, phrasing_by_qid,
                                   "mock", ppath)
    g = bodies["gold-replication"]["metrics"]
    mp = bodies["mapper-parse"]["metrics"]
    dr = bodies["deranged-lexicon"]["metrics"]
    ab = bodies["abstain-all"]["metrics"]
    aa = bodies["answer-all"]["metrics"]

    checks["counts_included"] = (n_cov, n_ctl) == (want[0], want[1])
    checks["gold_replication_parent_perfect"] = (
        g["n_covered_exact"] == want[2] and
        g["n_control_refused_correct_code"] == want[3])
    checks["mapper_parse_deterministic"] = \
        mp["deterministic_repeat_identical"]
    checks["deranged_collapses_below_0p10"] = \
        dr["n_covered_exact"] < 0.10 * mp["n_covered"]
    checks["abstain_all_bracket"] = (
        ab["n_covered_exact"] == 0 and
        ab["n_control_refused_acceptable"] == n_ctl)
    checks["answer_all_bracket"] = (
        aa["n_control_answered"] == n_ctl)
    # dev gate G4 runs against the REAL committed DEV corpus (fresh disjoint
    # identities, ASM-0145) even under --mock: parse-only, $0
    checks["dev_gate_computable"] = (
        mp.get("dev_n") == 60 and
        isinstance(mp.get("dev_parse_refused"), int) and
        mp["dev_parse_refused"] <= 0.20 * mp["dev_n"])

    green = all(checks.values())
    receipt = {
        "schema": "nlb-mock-receipt/1", "vertical": vertical,
        "green": green, "checks": checks,
        "mock_quarantine_note": ("scaffold phrasings, NON-BLIND, mechanics "
                                 "only; never eval material (design doc "
                                 "sections 5.6/10.6)"),
        "summary": {
            "mapper_parse": {k: mp[k] for k in sorted(mp) if k != "by_family"},
            "gold_replication": g,
            "deranged": {k: dr[k] for k in
                         ("n_covered_exact", "n_covered_refused_parse",
                          "n_covered_refused_engine",
                          "n_covered_answered_wrong")},
        },
    }
    rpath = os.path.join(mock_dir, "mock-receipt.json")
    with open(rpath, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps({"vertical": vertical, "green": green,
                      "checks": checks, "receipt": rpath}, indent=1,
                     sort_keys=True))
    return 0 if green else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vertical", required=True, choices=("l3a", "a5"))
    ap.add_argument("--arm", choices=ARMS)
    ap.add_argument("--phrasings", default=None)
    ap.add_argument("--phase", default="mock")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--root", default=None)
    args = ap.parse_args()
    root = args.root or _ROOT
    if args.mock:
        sys.exit(run_mock(root, args.vertical))
    if not args.arm or not args.phrasings:
        ap.error("--arm and --phrasings required outside --mock")
    body = one_arm_body(root, args.vertical, args.arm,
                        load_phrasings(args.phrasings), args.phase,
                        args.phrasings)
    print(json.dumps(body, sort_keys=True))


if __name__ == "__main__":
    main()
