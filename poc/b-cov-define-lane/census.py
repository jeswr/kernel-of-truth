#!/usr/bin/env python3
"""b-cov define-lane census (bead kernel-of-truth-hu10) — MEASURED-exploratory.

Measures per-benchmark kappa_B^engine = the DEFINE-checkable fraction after the
§C5 uniqueness filter, over the Tier-A definitional benchmarks that are AVAILABLE
on-box: OpenBookQA (in-repo d-ext control) + the six biomedical def-MMLU subjects
(canonical cais/mmlu, fetched). WiC is a data gap (canonical pilehvar/wic 401;
fail-closed sourcing declined mirrors) — reported, not run.

Pipeline (all ready, invoked as designed):
  leg 1 record  : onto-obo logicalDefinition (endorsed shards {go,so,mondo})
  leg 2 licence : data/axioms-definitional-v0/ endorsements (build_engine loads)
  leg 3 mapper  : mapper/dist/src/defineTemplates.js parseDefineQuestion (run_mapper.mjs)
  §C5 filter    : inverse-index collision count over the §2.2 DEFINE-MATCH canonical
                  form; item define-checkable iff n==1; dropped iff n>=2
                  (INELIGIBLE_DEFN_COLLISION); n==0 = candidate matches no licensed
                  concept. [ASM-0131, memo §6 C5]

NO verdict / NO interpretation / NO registry write. Opus (runner) reports mechanical
counts; Fable interprets. Every number tagged MEASURED-exploratory.
"""
import json, os, sys, hashlib, subprocess, collections, tempfile

ROOT = "."
HERE = os.path.join(ROOT, "poc", "b-cov-define-lane")
sys.path.insert(0, os.path.join(ROOT, "tools", "axiom"))
import kot_axiom as K  # noqa: E402

INDEX_JSON = os.path.join(HERE, "define-index.json")
ENDORSED_SHARDS = ["go.jsonl", "so.jsonl", "mondo.jsonl"]
METHOD_REF = ("docs/design-kot-query-define-op.md §6 C5 / §2.2 (ASM-0131); "
              "§7.2 (b-cov define-lane); mapper parseDefineQuestion (defineTemplates.ts)")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def canon_key(genus, diff_pairs):
    """The §2.2 DEFINE-MATCH canonical form, serialised deterministically.
    genus: iterable of urn; diff_pairs: iterable of (relation_urn, filler_urn)."""
    g = sorted(set(genus))
    d = sorted(set((p[0], p[1]) for p in diff_pairs))
    return json.dumps([g, [[r, f] for (r, f) in d]], ensure_ascii=False)


# ------------------------------------------------------------- benchmark loaders

def load_obqa():
    path = os.path.join(ROOT, "data", "d-ext", "source-jsonl", "test.jsonl")
    items = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            items.append({"id": "obqa-test-%s" % r.get("id"),
                          "text": r["question_stem"],
                          "options": list(r["choices"]["text"]),
                          "gold": r.get("answerKey")})
    return path, items


def load_mmlu_subject(cfg):
    path = os.path.join(HERE, "data", "mmlu-%s-test.jsonl" % cfg)
    items = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if not line.strip():
                continue
            r = json.loads(line)
            items.append({"id": "mmlu-%s-test-%d" % (cfg, i),
                          "text": r["question"],
                          "options": list(r["choices"]),
                          "gold": r.get("answer")})
    return path, items


# --------------------------------------------------------------- mapper subprocess

def run_mapper(items):
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False,
                                     dir=HERE, encoding="utf-8") as tf:
        for it in items:
            tf.write(json.dumps({"id": it["id"], "text": it["text"],
                                 "options": it["options"]}, ensure_ascii=False) + "\n")
        items_path = tf.name
    out_path = items_path + ".parses"
    subprocess.run(["node", os.path.join(HERE, "run_mapper.mjs"),
                    INDEX_JSON, items_path, out_path], check=True)
    parses = {}
    with open(out_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                parses[rec["id"]] = rec
    os.unlink(items_path)
    os.unlink(out_path)
    return parses


# ------------------------------------------------------------------------ census

def census_benchmark(name, src_path, items, eng, inv, detail_fh):
    parses = run_mapper(items)
    counts = collections.Counter()
    retr = collections.Counter()   # DEFINE-retrieve engine outcomes
    instrument_disagreements = 0

    for it in items:
        rec = parses[it["id"]]
        parse = rec["parse"]
        kind = parse["kind"]
        outcome = None
        n = None
        detail = {"id": it["id"], "benchmark": name, "parse_kind": kind}

        if kind == "unmapped":
            if parse.get("reason") == "no template matched":
                outcome = "UNMAPPED_NO_TEMPLATE"
            else:
                outcome = "UNMAPPED_SLOT_UNRESOLVED"
                detail["reason"] = parse.get("reason")
        elif kind == "abstain":
            outcome = "ABSTAIN_COLLISION"
            detail["slot"] = parse.get("slot")
        elif kind == "query" and "candidate" not in parse["query"]:
            # DEFINE retrieve ("what is X") — not the §C5 candidate slice.
            outcome = "DEFINE_RETRIEVE"
            subj = parse["query"]["subject"]
            detail["template"] = parse.get("template")
            res = eng.query({"op": "define", "subject": subj})
            code = "answer" if res.get("status") == "answer" else res.get("code")
            retr[code] += 1
            detail["engine"] = code
        else:
            # CANDIDATE-BEARING (DEFINE-MATCH query, or which-term-means stem).
            cand = (parse["query"]["candidate"] if kind == "query"
                    else parse["candidate"])
            diff_pairs = [(d["relation"], d["filler"]) for d in cand["differentiae"]]
            key = canon_key(cand["genus"], diff_pairs)
            members = inv.get(key, ())
            n = len(members)
            detail["candidate"] = cand
            detail["c5_n"] = n
            if n == 0:
                outcome = "C5_N0_NOMATCH"
            elif n == 1:
                outcome = "C5_N1_CHECKABLE"
                # instrument-validity: the unique licensed concept must DEFINE-MATCH true
                u = members[0]
                r = eng.query({"op": "define", "subject": u, "candidate": cand})
                ok = (r.get("status") == "answer" and r.get("value") is True)
                detail["instrument_match_true"] = ok
                if not ok:
                    instrument_disagreements += 1
            else:
                outcome = "C5_N2PLUS_COLLISION"  # INELIGIBLE_DEFN_COLLISION
                detail["collision_members"] = list(members)

        counts[outcome] += 1
        detail["outcome"] = outcome
        detail_fh.write(json.dumps(detail, ensure_ascii=False) + "\n")

    n_total = len(items)
    n_checkable = counts["C5_N1_CHECKABLE"]
    summary = {
        "benchmark": name,
        "epistemic_tag": "MEASURED-exploratory",
        "n_total": n_total,
        "n_checkable_C5_n1": n_checkable,
        "kappa_B_engine_mapper": (n_checkable / n_total) if n_total else 0.0,
        "c5_breakdown": {
            "n0_no_match": counts["C5_N0_NOMATCH"],
            "n1_checkable": counts["C5_N1_CHECKABLE"],
            "n2plus_collision_dropped_INELIGIBLE_DEFN_COLLISION": counts["C5_N2PLUS_COLLISION"],
        },
        "mapper_parse_outcomes": {
            "unmapped_no_template": counts["UNMAPPED_NO_TEMPLATE"],
            "unmapped_slot_unresolved": counts["UNMAPPED_SLOT_UNRESOLVED"],
            "abstain_slot_collision": counts["ABSTAIN_COLLISION"],
            "define_retrieve": counts["DEFINE_RETRIEVE"],
            "candidate_bearing_C5_population": (counts["C5_N0_NOMATCH"]
                                                + counts["C5_N1_CHECKABLE"]
                                                + counts["C5_N2PLUS_COLLISION"]),
        },
        "define_retrieve_engine_outcomes": dict(retr),
        "instrument_disagreements": instrument_disagreements,
        "input_sha256": sha256_file(src_path),
        "method_ref": METHOD_REF,
        "gold_parse_lane": "N/A for third-party items (no hand-authored grammar "
                           "queries; gold-parse = the internal define-op coverage "
                           "census poc/define-op-census). This lane is mapper-parse.",
    }
    return summary


def main():
    eng = K.build_engine(ROOT)

    # §C5 inverse index over the resolved definitional index (memo §6 C5 step 1).
    inv = collections.defaultdict(list)
    for x, entry in eng.defn.items():
        key = canon_key(entry["genus"], entry["differentiae"])
        inv[key].append(x)
    for k in inv:
        inv[k] = sorted(set(inv[k]))
    internal_collision_keys = sum(1 for v in inv.values() if len(v) > 1)
    internal_collision_concepts = sum(len(v) for v in inv.values() if len(v) > 1)

    detail_path = os.path.join(HERE, "detail", "census-detail.jsonl")
    with open(detail_path, "w", encoding="utf-8") as detail_fh:
        benches = []
        p, items = load_obqa()
        benches.append(census_benchmark("OpenBookQA-test", p, items, eng, inv, detail_fh))
        for cfg in ["college_biology", "college_chemistry", "medical_genetics",
                    "anatomy", "clinical_knowledge", "nutrition"]:
            p, items = load_mmlu_subject(cfg)
            benches.append(census_benchmark("MMLU-%s-test" % cfg, p, items,
                                            eng, inv, detail_fh))

    endorsement_shas = {s: "sha256:" + sha256_file(
        os.path.join(ROOT, "data", "onto-obo", s))[7:] for s in ENDORSED_SHARDS}

    out = {
        "census": "b-cov define-lane (kernel-of-truth-hu10)",
        "epistemic_tag": "MEASURED-exploratory",
        "runner_role": "Opus experiment-runner — mechanical counts only; NO verdict, "
                       "NO interpretation (Fable interprets); NO registry write.",
        "method_ref": METHOD_REF,
        "engine_definitional_index": {
            "defn_licensed": len(eng.defn_licensed),
            "defn_resolved": len(eng.defn),
            "defn_unresolved": len(eng.defn_unresolved),
            "distinct_definition_keys": len(inv),
            "internal_collision_keys_ge2": internal_collision_keys,
            "internal_collision_concepts": internal_collision_concepts,
        },
        "pins": {
            "endorsed_shards": ENDORSED_SHARDS,
            "endorsed_shard_sha256": endorsement_shas,
            "define_index_sha256": sha256_file(INDEX_JSON),
            "grammar": "kot-query/1 define-op (two-shape DEFINE / DEFINE-MATCH)",
        },
        "benchmarks_run": benches,
        "benchmarks_not_run": [{
            "benchmark": "WiC",
            "status": "DATA-GAP (not run)",
            "reason": "canonical source pilehvar/wic returns HTTP 401 unauthenticated; "
                      "programme fail-closed sourcing (data/d-ext/manifest.json) already "
                      "declined substituting an unauthenticated mirror to preserve source "
                      "provenance. Unblock = an HF credential for pilehvar/wic OR a "
                      "maintainer/Fable decision to accept a specific pinned mirror.",
        }],
    }
    summary_path = os.path.join(HERE, "census-summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=False, ensure_ascii=False)

    # console table
    print("\n=== b-cov define-lane census (MEASURED-exploratory) ===")
    print("engine defn: licensed=%d resolved=%d unresolved=%d | distinct-def-keys=%d "
          "internal-collision-keys(n>=2)=%d" % (
              len(eng.defn_licensed), len(eng.defn), len(eng.defn_unresolved),
              len(inv), internal_collision_keys))
    hdr = "%-28s %6s %7s %10s | %5s %5s %6s %5s %5s" % (
        "benchmark", "N", "check", "kappaB", "noT", "slot", "abst", "retr", "cand")
    print(hdr)
    for b in benches:
        mo = b["mapper_parse_outcomes"]
        print("%-28s %6d %7d %10.4f | %5d %5d %6d %5d %5d" % (
            b["benchmark"], b["n_total"], b["n_checkable_C5_n1"],
            b["kappa_B_engine_mapper"], mo["unmapped_no_template"],
            mo["unmapped_slot_unresolved"], mo["abstain_slot_collision"],
            mo["define_retrieve"], mo["candidate_bearing_C5_population"]))
    print("WiC: DATA-GAP (canonical pilehvar/wic 401; fail-closed sourcing declined mirror)")
    print("\nsummary -> %s\ndetail  -> %s" % (summary_path, detail_path))


if __name__ == "__main__":
    main()
