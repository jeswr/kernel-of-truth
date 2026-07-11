#!/usr/bin/env python3
"""ntp-gate probe — the NTP "engine-emits-traces" oracle/API gate (CPU, ~$0).

Question under test (docs/next/lit/NTP.md §8 oracle/API gate; flagged
ASSERTED-not-shown by docs/next/analysis/round1-fable-subjective.md §3.6):
does the deterministic kot-axiom/1 v0 engine, on covered concepts, actually
EMIT (a) the set of admissible continuations for a partial query and (b) a
replayable proof/derivation trace for an accept/reject — or is that capability
assumed by the verifier-loop / continuation-mask / trace-distillation
architectures (round1-critique-synthesis P3/P5/P6)?

Four measured legs, all deterministic, all read-only over pinned corpora:

  1. EMISSION INVENTORY — run the full pinned l3a-eval (900) and a5-eval (977)
     query sets through the unmodified engine / code oracle; census the exact
     key-shape of every emitted object; capture verbatim examples per family.
  2. CERTIFICATE REPLAY — for every covered query the engine ANSWERS, rebuild
     a minimal store containing ONLY the records the answer cites (provenance
     world ids + license axiom files), re-run the query on that store, and
     check the same value comes back. This operationalises "replayable
     derivation trace": a trace is closed iff the emission alone names every
     record the derivation consumed.
  3. CONTINUATION SETS — (i) verify by API inspection that the engine exposes
     no continuation/enumeration/trace surface; (ii) demonstrate that EXACT
     admissible-continuation sets are nevertheless derivable outside the
     engine from its public state + brute-force completion at closed-grammar
     scale, and measure the cost (engine calls, wall ns) per worked partial.
     Grades: G1 = licensed-vocabulary continuations (index read);
     G2 = answer-admissible continuations (some completion yields
     status=answer).
  4. TRACE GAPS — show what the engine computes internally but does not emit:
     ERR_CONFLICT refusals carry no pointer into the structured violation
     objects the CWA pass builds; inverseOf canonicalisation flips are
     invisible in the emission; refusals carry code+reason prose, not the
     terminating validation step.

Plus per-query latency context (raw ns; this box, 2 shared cores; context
only, no verdict) and a doubled-pass byte-determinism check.

Diagnostic probe: licenses interface-existence findings only; renders no
experiment verdict; touches no registry object, no results-log, no frozen
corpus. Zero runtime deps; stdlib only; no RNG anywhere; every collection is
sorted before emission.

Output: out/ntp-gate-probe.json (machine) + out/summary.txt (human), with the
JSON's sha256 printed and embedded in the summary.
"""

import hashlib
import json
import os
import re
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "axiom"))

import kot_axiom  # noqa: E402
import kot_code   # noqa: E402

OUT_DIR = os.path.join(HERE, "out")


# --------------------------------------------------------------- shared utils


def load_queries(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def key_shape_census(results):
    """Count the exact key-sets of emitted objects, by status."""
    shapes = {}
    for r in results:
        k = "%s:%s" % (r.get("status"), ",".join(sorted(r)))
        shapes[k] = shapes.get(k, 0) + 1
    return dict(sorted(shapes.items()))


def timed_run(query_fn, queries):
    """Run each query once, individually timed. Returns (results, ns_list)."""
    results, ns = [], []
    for rec in queries:
        t0 = time.perf_counter_ns()
        r = query_fn(rec["query"])
        t1 = time.perf_counter_ns()
        results.append(r)
        ns.append(t1 - t0)
    return results, ns


def latency_stats(ns):
    s = sorted(ns)
    return {
        "n": len(s),
        "mean_us": sum(s) / len(s) / 1000.0,
        "median_us": statistics.median(s) / 1000.0,
        "p95_us": s[int(0.95 * (len(s) - 1))] / 1000.0,
        "max_us": s[-1] / 1000.0,
    }


# ------------------------------------------------- leg 2: certificate replay


def replay_certificate(axioms_by_file, world_by_id, query, result):
    """Rebuild a store from ONLY the records the answer cites; re-run.

    license refs look like "<corpus>/<file>.json#<i>" (axiom constraint refs)
    or the literal "asserted"; provenance entries are world-record ids. A
    closed certificate replays to the same value; any refusal / mismatch /
    build error is a measured closure failure.
    """
    lic_files = sorted({l.split("#")[0] for l in result["license"] if "/" in l})
    ax = [(ref, rec) for ref, rec in axioms_by_file if ref in lic_files]
    missing_prov = [p for p in result["provenance"] if p not in world_by_id]
    world = [world_by_id[p] for p in result["provenance"] if p in world_by_id]
    if missing_prov:
        return {"outcome": "provenance-not-in-world", "detail": missing_prov}
    try:
        mini = kot_axiom.Engine(ax, world)
        r2 = mini.query(query)
    except kot_axiom.KotAxiomError as e:
        return {"outcome": "build-error", "detail": e.code}
    if r2["status"] == "answer" and r2["value"] == result["value"]:
        return {"outcome": "exact"}
    if r2["status"] == "answer":
        return {"outcome": "wrong-value", "detail": r2["value"]}
    return {"outcome": "refused", "detail": r2["code"]}


def replay_leg(queries, results, axioms_by_file, world_by_id, desugar=None):
    """Replay every covered ANSWER; tally by family x outcome."""
    tally, examples = {}, {}
    for rec, r in zip(queries, results):
        if rec["class"] != "covered" or r.get("status") != "answer":
            continue
        q = rec["query"] if desugar is None else desugar(rec["query"])
        out = replay_certificate(axioms_by_file, world_by_id, q, r)
        key = (rec["family"], out["outcome"])
        tally[key] = tally.get(key, 0) + 1
        if key not in examples:
            examples[key] = {"qid": rec["qid"], "query": rec["query"],
                             "emitted": r, "replay": out}
    flat = {"%s|%s" % k: v for k, v in sorted(tally.items())}
    return flat, examples


# --------------------------------------------- leg 3: continuation adapter


FIELD_ORDER = {
    "unique": ("rel", "direction", "subject"),
    "lookup": ("rel", "direction", "subject"),
    "count": ("rel", "direction", "subject", "qualifier"),
    "instance": ("entity", "concept"),
    "define": ("subject",),
}


class ContinuationAdapter(object):
    """Derives EXACT admissible-continuation sets for a partial kot-query/1
    query from the engine's public state. Lives OUTSIDE the engine on purpose:
    its existence at this line count, over only public attributes, is the
    gate's measurement of how far the engine is from emitting continuations
    itself. G1 = licensed vocabulary for the next field (index read).
    G2 = values for which SOME completion of the remaining fields yields
    status=answer (brute-force over the closed grammar, early-exit)."""

    def __init__(self, engine):
        self.engine = engine
        self.calls = 0

    def vocab(self, op, field):
        e = self.engine
        if field == "rel":
            return sorted(e.licensed_rels)
        if field == "direction":
            return list(kot_axiom.DIRECTIONS)
        if field in ("subject", "entity") and op != "define":
            return sorted(e.entities)
        if field == "subject":  # define
            return sorted(e.defn_licensed)
        if field == "concept":
            return sorted(e.licensed_classes)
        if field == "qualifier":
            return [None] + sorted(e.licensed_classes)
        raise ValueError(field)

    def _exists_answer(self, q, order):
        missing = [f for f in order if f not in q]
        if not missing:
            qq = {k: v for k, v in q.items() if v is not None}
            self.calls += 1
            return self.engine.query(qq)["status"] == "answer"
        f = missing[0]
        for v in self.vocab(q["op"], f):
            q2 = dict(q)
            q2[f] = v
            if self._exists_answer(q2, order):
                return True
        return False

    def admissible_ops(self):
        out = []
        for op in kot_axiom.QUERY_OPS:
            if self._exists_answer({"op": op}, FIELD_ORDER[op]):
                out.append(op)
        return out

    def admissible_next(self, partial):
        op = partial["op"]
        order = FIELD_ORDER[op]
        nxt = [f for f in order if f not in partial][0]
        g1 = self.vocab(op, nxt)
        g2 = []
        for v in g1:
            q = dict(partial)
            q[nxt] = v
            if self._exists_answer(q, order):
                g2.append(v)
        return nxt, g1, g2


def worked_partial(adapter, label, partial):
    adapter.calls = 0
    t0 = time.perf_counter_ns()
    if partial == {}:
        field, g1, g2 = "op", list(kot_axiom.QUERY_OPS), adapter.admissible_ops()
    else:
        field, g1, g2 = adapter.admissible_next(partial)
    t1 = time.perf_counter_ns()
    return {
        "label": label,
        "partial": {k: v for k, v in sorted(partial.items())},
        "next_field": field,
        "g1_licensed_size": len(g1),
        "g2_admissible_size": len(g2),
        "g2_examples": [v for v in g2[:3]],
        "engine_calls": adapter.calls,
        "wall_ns": t1 - t0,
    }


# ---------------------------------------------------------------------- main


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    report = {"probe": "ntp-gate", "date": "2026-07-11",
              "engine_source": "tools/axiom/kot_axiom.py",
              "root": "<repo>", "legs": {}}

    # ---- build both engines exactly as the pinned instruments build them
    engine = kot_axiom.build_engine(ROOT)               # family/world + define
    oracle = kot_code.build_code_oracle(ROOT)           # code vertical
    l3a = load_queries(os.path.join(ROOT, "data", "l3a-eval", "queries.jsonl"))
    a5 = load_queries(os.path.join(ROOT, "data", "a5-eval", "queries.jsonl"))

    # ---- leg 0: API-absence check (code inspection, mechanised)
    pat = re.compile(r"continu|legal|admiss|enum|next_|trace|proof|deriv|expla",
                     re.IGNORECASE)
    api_hits = sorted(n for n in dir(kot_axiom.Engine) if pat.search(n))
    src = open(os.path.join(ROOT, "tools", "axiom", "kot_axiom.py"),
               encoding="utf-8").read()
    src_defs = sorted(set(re.findall(r"def (\w+)", src)))
    src_hits = sorted(n for n in src_defs if pat.search(n))
    report["legs"]["api_absence"] = {
        "engine_attrs_matching_continuation_or_trace": api_hits,
        "source_defs_matching_continuation_or_trace": src_hits,
        "engine_public_attrs_consumed_by_adapter": [
            "licensed_rels", "licensed_classes", "entities", "defn_licensed",
            "defn", "query"],
    }

    # ---- leg 1: emission inventory (+ latency + determinism)
    res_l3a, ns_l3a = timed_run(engine.query, l3a)
    res_a5, ns_a5 = timed_run(oracle.query, a5)
    res_l3a_2 = [engine.query(rec["query"]) for rec in l3a]
    res_a5_2 = [oracle.query(rec["query"]) for rec in a5]
    det = (json.dumps(res_l3a, sort_keys=True) == json.dumps(res_l3a_2, sort_keys=True)
           and json.dumps(res_a5, sort_keys=True) == json.dumps(res_a5_2, sort_keys=True))

    examples = {}
    for rec, r in zip(l3a, res_l3a):
        k = "l3a/%s/%s" % (rec["class"], rec["family"])
        examples.setdefault(k, {"qid": rec["qid"], "query": rec["query"], "emitted": r})
    for rec, r in zip(a5, res_a5):
        k = "a5/%s/%s" % (rec["class"], rec["family"])
        examples.setdefault(k, {"qid": rec["qid"], "query": rec["query"], "emitted": r})

    # define-op emissions on covered (minted+endorsed) concepts
    defined = sorted(engine.defn)
    define_examples = []
    for s in defined[:2]:
        define_examples.append({"query": {"op": "define", "subject": s},
                                "emitted": engine.query({"op": "define", "subject": s})})
    unresolved = sorted(engine.defn_unresolved)
    if unresolved:
        s = unresolved[0]
        define_examples.append({"query": {"op": "define", "subject": s},
                                "emitted": engine.query({"op": "define", "subject": s})})
    no_def = sorted(engine.defn_licensed - set(engine.defn) - engine.defn_unresolved)
    if no_def:
        s = no_def[0]
        define_examples.append({"query": {"op": "define", "subject": s},
                                "emitted": engine.query({"op": "define", "subject": s})})

    report["legs"]["emission_inventory"] = {
        "l3a_n": len(l3a), "a5_n": len(a5),
        "l3a_key_shapes": key_shape_census(res_l3a),
        "a5_key_shapes": key_shape_census(res_a5),
        "deterministic_repeat_identical": det,
        "family_examples": {k: examples[k] for k in sorted(examples)},
        "define_examples": define_examples,
        "define_index_sizes": {
            "defn_licensed": len(engine.defn_licensed),
            "defn_resolved": len(engine.defn),
            "defn_unresolved": len(engine.defn_unresolved)},
        "latency_context_raw": {
            "l3a_per_query": latency_stats(ns_l3a),
            "a5_per_query": latency_stats(ns_a5),
            "note": "this box, 2 shared cores, single-threaded CPython; "
                    "context only, no verdict"},
    }

    # ---- leg 2: certificate replay
    fam_axioms = kot_axiom.load_corpora(ROOT)[0] + \
        kot_axiom.load_definitional_endorsements(ROOT)
    fam_world = {r["id"]: r for r in kot_axiom.load_corpora(ROOT)[1]}
    code_axioms, code_world_list = kot_code.load_code_corpora(ROOT)
    code_world = {r["id"]: r for r in code_world_list}

    l3a_tally, l3a_ex = replay_leg(l3a, res_l3a, fam_axioms, fam_world)
    a5_tally, a5_ex = replay_leg(a5, res_a5, code_axioms, code_world,
                                 desugar=oracle.desugar)

    # define-op replay: endorsement axiom + the single cited obo record +
    # the pinned mint bridge (NB the bridge is consulted from the pinned
    # corpus, not named by the certificate — measured caveat, see doc).
    define_replays = []
    for s in defined[:3]:
        q = {"op": "define", "subject": s}
        r = engine.query(q)
        lic_files = sorted({l.split("#")[0] for l in r["license"]})
        ax = [(ref, rec) for ref, rec in fam_axioms if ref in lic_files]
        shards = {}
        for _ref, rec in ax:
            for c in rec.get("constraints", []):
                if c.get("kind") == "definitional":
                    shards[c["source"]["shard"]] = [
                        rr for rr in engine.obo_shards.get(c["source"]["shard"], [])
                        if rr.get("id") in r["provenance"]]
        try:
            mini = kot_axiom.Engine(ax, [], obo_shards=shards,
                                    mint_bridge=engine.mint_bridge)
            r2 = mini.query(q)
            outcome = ("exact" if r2["status"] == "answer"
                       and r2["value"] == r["value"] else
                       "refused:%s" % r2.get("code") if r2["status"] == "refuse"
                       else "wrong-value")
        except kot_axiom.KotAxiomError as e:
            outcome = "build-error:%s" % e.code
        define_replays.append({"subject": s, "outcome": outcome,
                               "license": r["license"], "provenance": r["provenance"]})

    report["legs"]["certificate_replay"] = {
        "definition": "closed certificate := (provenance world ids + license "
                      "axiom files) alone rebuild a store on which the same "
                      "query returns the same value",
        "l3a_tally_family|outcome": l3a_tally,
        "a5_tally_family|outcome": a5_tally,
        "l3a_failure_examples": {"%s|%s" % k: v for k, v in sorted(l3a_ex.items())
                                 if k[1] != "exact"},
        "a5_failure_examples": {"%s|%s" % k: v for k, v in sorted(a5_ex.items())
                                if k[1] != "exact"},
        "define_replays": define_replays,
        "refusals_have_no_certificate": "refusal objects carry only "
                                        "{status, code, reason} - nothing to replay",
    }

    # ---- leg 3: continuation sets (worked partials, both verticals)
    ad = ContinuationAdapter(engine)
    mother_rel = None
    maker_rel = None
    for rec in l3a:
        if rec["family"] == "unique-mother" and mother_rel is None:
            mother_rel = rec["query"]["rel"]
        if rec["family"] == "count-maker" and maker_rel is None:
            maker_rel = rec["query"]["rel"]
    partials = [
        worked_partial(ad, "W1 ops from empty partial", {}),
        worked_partial(ad, "W2 rel continuations of {op:unique}",
                       {"op": "unique"}),
        worked_partial(ad, "W3 subject continuations of {op:unique, rel:mother, "
                           "direction:forward}",
                       {"op": "unique", "rel": mother_rel, "direction": "forward"}),
        worked_partial(ad, "W4 concept continuations of {op:instance, "
                           "entity:elvis}",
                       {"op": "instance", "entity": "urn:kotw:v0:elvis-presley"}),
        worked_partial(ad, "W5 subject continuations of {op:count, rel:maker, "
                           "direction:inverse}",
                       {"op": "count", "rel": maker_rel, "direction": "inverse"}),
        worked_partial(ad, "W6 subject continuations of {op:define}",
                       {"op": "define"}),
    ]
    # code vertical: named-op grammar {op, of} — admissible `of` for callers-of
    ce = oracle.engine
    t0 = time.perf_counter_ns()
    calls = 0
    g2_of = []
    for ent in sorted(ce.entities):
        calls += 1
        if oracle.query({"op": "callers-of", "of": ent})["status"] == "answer":
            g2_of.append(ent)
    t1 = time.perf_counter_ns()
    partials.append({
        "label": "W7 (code) of-continuations of {op:callers-of}",
        "partial": {"op": "callers-of"}, "next_field": "of",
        "g1_licensed_size": len(ce.entities),
        "g2_admissible_size": len(g2_of), "g2_examples": g2_of[:3],
        "engine_calls": calls, "wall_ns": t1 - t0})

    report["legs"]["continuation_sets"] = {
        "worked_partials": partials,
        "semantics": "G1 = licensed vocabulary for the next field (engine "
                     "index read); G2 = exists-completion-with-status-answer "
                     "(exact, brute force over the closed grammar, early exit)",
    }

    # ---- leg 4: trace gaps
    conflict_example = None
    for rec, r in zip(l3a, res_l3a):
        if rec["family"] == "conflict" and r.get("code") == "ERR_CONFLICT":
            conflict_example = {"qid": rec["qid"], "query": rec["query"],
                                "emitted": r}
            break
    matching_violations = []
    if conflict_example:
        subj = conflict_example["query"].get("subject") \
            or conflict_example["query"].get("entity")
        for v in engine.violations:
            if any(e == subj for (e, _t) in v["implicated"]):
                matching_violations.append(v)
    canon_pairs = sorted(engine.canonical.items())
    canon_demo = None
    for rec, r in zip(l3a, res_l3a):
        rel = rec["query"].get("rel")
        if rel in engine.canonical and engine.canonical[rel] != rel \
                and r.get("status") == "answer":
            canon_demo = {"qid": rec["qid"], "query": rec["query"], "emitted": r,
                          "note": "answered via inverseOf canonicalisation "
                                  "(rel stored under %s); the flip is not "
                                  "visible in the emission" % engine.canonical[rel]}
            break
    report["legs"]["trace_gaps"] = {
        "n_store_violations_l3a": len(engine.violations),
        "n_store_violations_a5": len(oracle.engine.violations),
        "violation_object_shape": sorted(engine.violations[0]) if engine.violations else [],
        "conflict_refusal_example": conflict_example,
        "internal_violations_matching_that_subject": matching_violations,
        "gap": "the ERR_CONFLICT refusal names no violation object; the "
               "structured {code, detail, implicated} objects exist only "
               "in-memory (engine.violations)",
        "inverseOf_canonical_map_size": len(canon_pairs),
        "canonicalisation_demo": canon_demo,
    }

    # ---- write outputs
    payload = json.dumps(report, indent=1, sort_keys=True) + "\n"
    json_path = os.path.join(OUT_DIR, "ntp-gate-probe.json")
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(payload)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    lines = []
    lines.append("ntp-gate probe summary (%s)" % report["date"])
    lines.append("json sha256 %s" % digest)
    lines.append("")
    li = report["legs"]["emission_inventory"]
    lines.append("[1] emission shapes l3a: %s" % json.dumps(li["l3a_key_shapes"]))
    lines.append("    emission shapes a5 : %s" % json.dumps(li["a5_key_shapes"]))
    lines.append("    deterministic double pass: %s" % li["deterministic_repeat_identical"])
    lines.append("    latency l3a per query: %s" % json.dumps(li["latency_context_raw"]["l3a_per_query"]))
    lines.append("    latency a5  per query: %s" % json.dumps(li["latency_context_raw"]["a5_per_query"]))
    lines.append("")
    lr = report["legs"]["certificate_replay"]
    lines.append("[2] replay tally l3a: %s" % json.dumps(lr["l3a_tally_family|outcome"]))
    lines.append("    replay tally a5 : %s" % json.dumps(lr["a5_tally_family|outcome"]))
    lines.append("    define replays  : %s" % json.dumps(
        [(d["subject"][:24], d["outcome"]) for d in lr["define_replays"]]))
    lines.append("")
    la = report["legs"]["api_absence"]
    lines.append("[3] engine attrs matching continuation/trace pattern: %s"
                 % la["engine_attrs_matching_continuation_or_trace"])
    for w in report["legs"]["continuation_sets"]["worked_partials"]:
        lines.append("    %s -> next=%s G1=%d G2=%d calls=%d wall_us=%.0f"
                     % (w["label"], w["next_field"], w["g1_licensed_size"],
                        w["g2_admissible_size"], w["engine_calls"],
                        w["wall_ns"] / 1000.0))
    lines.append("")
    lg = report["legs"]["trace_gaps"]
    lines.append("[4] store violations l3a=%d a5=%d; conflict refusal carries "
                 "no violation pointer; canonical map size=%d"
                 % (lg["n_store_violations_l3a"], lg["n_store_violations_a5"],
                    lg["inverseOf_canonical_map_size"]))
    summary = "\n".join(lines) + "\n"
    with open(os.path.join(OUT_DIR, "summary.txt"), "w", encoding="utf-8") as f:
        f.write(summary)
    sys.stdout.write(summary)


if __name__ == "__main__":
    main()
