#!/usr/bin/env python3
"""DECONF/1 Stage A1 — the extensional-equivalence audit
(docs/next/design/DECONF.md §3, ASM-0962). CPU-only, ~$0, no model call.

QUESTION (the runtime channel): does the pinned deterministic verifier's
check() read ANYTHING from the kernel store that the aligned generic
answer-key store GS-A (a mechanical four-column projection — build_gsa.py,
ASM-0961) lacks?

PROCEDURE (DECONF §3.1): enumerate the FULL decision grid —
  the three pinned item corpora (d-qa 650 incl. its 150 control items,
  d-qa-r 1000, d-qa-t 360)
  x every admissible answer in the item's closed answer space (each MC option
    key; yes/no for claim items — exactly the IF-C constrained surface)
  x both verifier variants (true map; the seed-pinned shuffled derangement,
    REPLAYED via the pinned ShuffledKernelVerifier code and byte-checked
    against every recorded shuffle-map.json of the audited run, then applied
    identically to GS-A rows)
— and compute the decision triple (extract_ok, decidable, consistent) under
  (i) the PINNED KernelVerifier / ShuffledKernelVerifier over the kernel
      store (imported from poc/f2b/runner/f2b_runner.py at its harness pin,
      byte-verified — the kernel side runs the literal pinned code), and
  (ii) the same checker class over GS-A (GSAVerifier / GSAShuffledVerifier
      below: identical check() algorithm, identical norm_text, reading ONLY
      the four projected columns; no record file, no derivation function is
      touched at check time).

PRIMARY STATISTIC: C_dec = concordant triples / total grid size — an
exhaustive COUNT over the full reachable decision space (no sampling error,
no CI; ASM-0962). Discordances, if any, are emitted in full and classified by
check-path (def-match / term-match / claim / shuffled-composition).

SECONDARY (reachable-trajectory sub-grids, measured not argued): the grid
restricted to the REALIZED protocol of the audited f2b-replicate final run
(d-qa-r rank-prefix 250 — whose label-index domain spans only 102/108
concepts) and to the FROZEN f2b-transfer stage-2 plan (d-qa-t rank-prefix
250, 105/108 concepts), each with the verifier label index built exactly as
the runner builds it (index_labels over the scored items only).

SUPPLEMENTARY: the d-ext external slice (500 items, kernel_checkable=false)
through the same verify path — the store-independence of the off-coverage
abstention is measured, not asserted.

R_repro: under C_dec = 1.0 the §1 determinism lemma makes every F2-line
endpoint bit-for-bit invariant under kernel -> GS-A substitution, so
R_repro = lift(GS-A)/lift(kernel) == 1.0 IDENTICALLY (derived by invariance,
not a fresh model run; DECONF §3.2). The measured kernel lift it applies to
is restated from the audited log for context only.

Fail-closed on every pin (ERR_*). Deterministic. Zero writes outside
poc/deconf-a1/.

Usage:  python3 audit_a1.py            (paths repo-anchored; ~1 min CPU)
"""

from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
RUNNER_DIR = os.path.join(ROOT, "poc", "f2b", "runner")

# --- pins (all MEASURED provenance; see build_gsa.py docstring) -------------
RUNNER_SHA256_PIN = \
    "b62c3a72882b354f25b97a4b38251fb4863b1c3417220d1c942c84b24fc9b666"
F2B_MANIFEST_SHA256_PIN = \
    "da1fe9dddd9cbddc13143a7f7931ae3f0ced2548df8e36042244ee043fcb61f9"
# The recorded shuffle maps of the audited f2b-replicate campaign; the
# replayed permutation is byte-compared against ALL of them below.
RECORDED_SHUFFLE_MAPS = [
    os.path.join(ROOT, "poc", "f2b", "results-incoming", d, "shuffle-map.json")
    for d in ("20260709-013627-modal", "20260709-052739-modal",
              "20260709-114229-modal")
]

CORPORA = {
    # corpus -> list of item files (grid = full corpora per DECONF §3.1)
    "d-qa": [os.path.join(ROOT, "data", "d-qa", "items", "covered.jsonl"),
             os.path.join(ROOT, "data", "d-qa", "items", "control.jsonl")],
    "d-qa-r": [os.path.join(ROOT, "data", "d-qa-r", "items", "covered.jsonl")],
    "d-qa-t": [os.path.join(ROOT, "data", "d-qa-t", "items", "covered.jsonl")],
}
DEXT_ITEMS = os.path.join(ROOT, "data", "d-ext", "items", "external.jsonl")

# measured kernel-arm context, restated from results-log/f2b-replicate.jsonl
# final-phase run records (3-seed mean kernel-verify-retry 0.7507 vs
# R3-alone 0.600) and the audited verdict (+0.1507, BCa LB +0.1053).
MEASURED_LIFT_CONTEXT = {
    "kernel_verify_k4_3seed_mean": 0.7506666666666667,
    "r3_alone_3seed_mean": 0.6,
    "effect_size_vs_r3": 0.1507,
    "primary_lower_onesided95": 0.1053,
    "source": "results-log/f2b-replicate.jsonl + registry/verdicts/"
              "f2b-replicate.json (restated, [MEASURED])",
}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# --- import the PINNED harness code (the kernel side IS the pinned code) ----
runner_path = os.path.join(RUNNER_DIR, "f2b_runner.py")
got = sha256_file(runner_path)
if got != RUNNER_SHA256_PIN:
    raise SystemExit("ERR_RUNNER_PIN: %s sha %s != pinned %s"
                     % (runner_path, got, RUNNER_SHA256_PIN))
sys.path.insert(0, RUNNER_DIR)
from f2b_runner import (  # noqa: E402
    KernelVerifier, ShuffledKernelVerifier, norm_text, verify_answer,
)


# --- the same checker class over GS-A (DECONF §3.1 (ii)) --------------------
class GSAVerifier:
    """check()-identical semantics over the four-column GS-A rows ONLY.

    Mirrors KernelVerifier exactly: same decision logic, same norm_text,
    same lazy label indexing over the items it is told to index — but the
    store consulted is gs-a.jsonl and nothing else (no record files, no
    derivation at check time)."""

    def __init__(self, rows):
        self._rows = {r["concept_id"]: r for r in rows}
        self._by_label = {}

    def _load(self, item):
        row = self._rows[item["urn"]]
        for lab in row["term_labels"]:
            self._by_label[lab.lower()] = row
        return row

    def index_labels(self, items):
        for it in items:
            if it.get("kernel_checkable"):
                self._load(it)

    def shown_definition(self, item):
        return self._load(item)["canonical_text"]

    def check(self, record, item):
        if not item.get("kernel_checkable"):
            return False, False
        row = self._load(item)
        kind = record.get("kind")
        if kind == "definition":
            ok = norm_text(record["text"]) == norm_text(row["canonical_text"])
        elif kind == "term-for-definition":
            chosen = self._by_label.get(record["term"].lower())
            ok = (chosen is not None
                  and norm_text(chosen["canonical_text"])
                  == norm_text(record["definition"]))
        elif kind == "claim":
            member = any(norm_text(record["claim"]) == norm_text(c)
                         for c in row["claims"])
            ok = member == (record["verdict"] == "yes")
        else:
            raise SystemExit("ERR_RECORD_KIND: %r" % kind)
        return True, ok


class GSAShuffledVerifier:
    """The recorded derangement applied to GS-A rows — mirrors
    ShuffledKernelVerifier: belief lookups go through perm; the shown
    definition (an item-level fact) is NOT permuted."""

    def __init__(self, rows, covered_items, perm):
        self.rows = {r["concept_id"]: r for r in rows}
        self.perm = perm
        self.label_to_urn = {}
        for it in covered_items:
            if it.get("kernel_checkable"):
                self.label_to_urn.setdefault(it["label"].lower(), it["urn"])

    def index_labels(self, items):
        pass  # row map is total; mirror of ShuffledKernelVerifier.index_labels
              # (which only warms the base cache) — no decision state changes

    def shown_definition(self, item):
        return self.rows[item["urn"]]["canonical_text"]

    def check(self, record, item):
        if not item.get("kernel_checkable"):
            return False, False
        row = self.rows[self.perm[item["urn"]]]
        kind = record.get("kind")
        if kind == "definition":
            ok = norm_text(record["text"]) == norm_text(row["canonical_text"])
        elif kind == "term-for-definition":
            u = self.label_to_urn.get(record["term"].lower())
            chosen = self.rows[self.perm[u]] if u is not None else None
            ok = (chosen is not None
                  and norm_text(chosen["canonical_text"])
                  == norm_text(record["definition"]))
        elif kind == "claim":
            member = any(norm_text(record["claim"]) == norm_text(c)
                         for c in row["claims"])
            ok = member == (record["verdict"] == "yes")
        else:
            raise SystemExit("ERR_RECORD_KIND: %r" % kind)
        return True, ok


def admissible_answers(item):
    """The item's closed answer space = the IF-C constrained surface."""
    if item.get("options"):
        return [o["key"] for o in item["options"]]
    return ["yes", "no"]


def triple(verifier, item, ans):
    ok_ext, decidable, consistent, _cpu = verify_answer(verifier, item, ans)
    return (bool(ok_ext), bool(decidable), bool(consistent))


def enumerate_grid(items, kv, gv, sv, sgv, discordances, grid_label,
                   mix=None):
    """Both variants over items x admissible answers. Returns counters.
    `mix` (optional dict) accumulates the decision-space disclosure: triple
    distribution per variant, true-vs-shuffled divergence, and the
    accept<->gold contingency on decidable true-variant cells (the
    circularity signature, counted exhaustively)."""
    stats = {"cells": 0, "concordant": 0,
             "by_variant": {"true": [0, 0], "shuffled": [0, 0]},
             "by_type": {}}
    for it in items:
        answers = admissible_answers(it)
        for ans in answers:
            pair = {}
            for variant, a, b in (("true", kv, gv), ("shuffled", sv, sgv)):
                t_k = triple(a, it, ans)
                t_g = triple(b, it, ans)
                pair[variant] = t_k
                if mix is not None:
                    mix["triples"]["%s|%s" % (variant, t_k)] = \
                        mix["triples"].get("%s|%s" % (variant, t_k), 0) + 1
                stats["cells"] += 1
                stats["by_variant"][variant][1] += 1
                ty = stats["by_type"].setdefault(
                    (it.get("type"), variant), [0, 0])
                ty[1] += 1
                if t_k == t_g:
                    stats["concordant"] += 1
                    stats["by_variant"][variant][0] += 1
                    ty[0] += 1
                else:
                    discordances.append({
                        "grid": grid_label, "item_id": it["id"],
                        "urn": it.get("urn"), "type": it.get("type"),
                        "answer": ans, "variant": variant,
                        "kernel_triple": t_k, "gsa_triple": t_g,
                        "check_path": ("shuffled-composition"
                                       if variant == "shuffled"
                                       else {"def-match": "def-match",
                                             "term-match": "term-match"}.get(
                                           it.get("type"), "claim")),
                    })
            if mix is not None:
                if pair["true"] != pair["shuffled"]:
                    mix["true_vs_shuffled_divergent"] += 1
                mix["item_answer_pairs"] += 1
                _ext, dec, cons = pair["true"]
                if dec:
                    key = "accept|%s" % ("gold" if ans == it["answer"]
                                         else "nongold") if cons else \
                          "reject|%s" % ("gold" if ans == it["answer"]
                                         else "nongold")
                    mix["true_decidable_vs_gold"][key] = \
                        mix["true_decidable_vs_gold"].get(key, 0) + 1
    return stats


def main():
    # ---- pin gates ---------------------------------------------------------
    man_path = os.path.join(ROOT, "poc", "f2b", "inputs", "f2b-manifest.json")
    if sha256_file(man_path) != F2B_MANIFEST_SHA256_PIN:
        raise SystemExit("ERR_PIN: f2b-manifest.json drifted from the audited "
                         "run's staged bytes")
    with open(man_path, encoding="utf-8") as f:
        man = json.load(f)
    perm_seed = man["shuffle"]["perm_seed"]

    gsa_man = json.load(open(os.path.join(HERE, "gsa-manifest.json"),
                             encoding="utf-8"))
    gsa_path = os.path.join(HERE, "gs-a.jsonl")
    gsa_sha = sha256_file(gsa_path)
    if gsa_sha != gsa_man["gs_a_sha256"]:
        raise SystemExit("ERR_GSA_PIN: gs-a.jsonl sha %s != manifest %s"
                         % (gsa_sha, gsa_man["gs_a_sha256"]))
    gsa_rows = load_jsonl(gsa_path)

    # ---- corpora ------------------------------------------------------------
    items_by_corpus = {}
    for name, files in CORPORA.items():
        its = []
        for p in files:
            its.extend(load_jsonl(p))
        items_by_corpus[name] = its
    covered_r = sorted(items_by_corpus["d-qa-r"], key=lambda x: x["rank"])
    n_items = {k: len(v) for k, v in items_by_corpus.items()}
    if n_items != {"d-qa": 650, "d-qa-r": 1000, "d-qa-t": 360}:
        raise SystemExit("ERR_CORPUS_SIZE: %r" % n_items)

    # ---- the recorded derangement, replayed by the PINNED code --------------
    shuf_kernel = ShuffledKernelVerifier(ROOT, covered_r, perm_seed)
    replayed = shuf_kernel.perm
    recorded_shas = set()
    for p in RECORDED_SHUFFLE_MAPS:
        rec = json.load(open(p, encoding="utf-8"))
        if rec["map_urn_to_record_of"] != replayed:
            raise SystemExit("ERR_SHUFFLE_REPLAY: replayed perm != recorded "
                             "map %s" % p)
        recorded_shas.add(rec["sha256_of_map"])
    if recorded_shas != {shuf_kernel.perm_sha256}:
        raise SystemExit("ERR_SHUFFLE_SHA: recorded map shas %r != replayed %s"
                         % (recorded_shas, shuf_kernel.perm_sha256))
    print("shuffle replay OK: seed=%d sha=%s (matches all %d recorded maps)"
          % (perm_seed, shuf_kernel.perm_sha256[:12],
             len(RECORDED_SHUFFLE_MAPS)))

    discordances = []
    grids = {}
    mix = {"triples": {}, "true_vs_shuffled_divergent": 0,
           "item_answer_pairs": 0, "true_decidable_vs_gold": {}}

    # ---- PRIMARY grid: full corpora, per-corpus fresh verifier pairs -------
    for name in ("d-qa", "d-qa-r", "d-qa-t"):
        items = items_by_corpus[name]
        kv = KernelVerifier(ROOT)
        kv.index_labels(items)
        gv = GSAVerifier(gsa_rows)
        gv.index_labels(items)
        sv = ShuffledKernelVerifier(ROOT, covered_r, perm_seed)
        sv.index_labels(items)
        sgv = GSAShuffledVerifier(gsa_rows, covered_r, sv.perm)
        grids["primary:" + name] = enumerate_grid(
            items, kv, gv, sv, sgv, discordances, "primary:" + name, mix=mix)
        g = grids["primary:" + name]
        print("primary %-7s cells=%5d concordant=%5d" %
              (name, g["cells"], g["concordant"]))

    # ---- SECONDARY: realized/planned run protocols (restricted label index) -
    #   (a) f2b-replicate final run: d-qa-r rank-prefix 250 (index = 102 urns)
    #   (b) f2b-transfer stage-2 frozen plan: d-qa-t rank-prefix 250 (105 urns)
    dqat_sorted = sorted(items_by_corpus["d-qa-t"], key=lambda x: x["rank"])
    for label, sub in (("run-realized:f2b-replicate:d-qa-r[:250]",
                        covered_r[:250]),
                       ("run-planned:f2b-transfer-stage2:d-qa-t[:250]",
                        dqat_sorted[:250])):
        kv = KernelVerifier(ROOT)
        kv.index_labels(sub)
        gv = GSAVerifier(gsa_rows)
        gv.index_labels(sub)
        sv = ShuffledKernelVerifier(ROOT, covered_r, perm_seed)
        sv.index_labels(sub)
        sgv = GSAShuffledVerifier(gsa_rows, covered_r, sv.perm)
        grids[label] = enumerate_grid(sub, kv, gv, sv, sgv, discordances,
                                      label)
        g = grids[label]
        print("%-46s cells=%5d concordant=%5d n_index_urns=%d"
              % (label, g["cells"], g["concordant"],
                 len({it["urn"] for it in sub})))

    # ---- SUPPLEMENTARY: d-ext off-coverage abstention store-independence ----
    dext = sorted(load_jsonl(DEXT_ITEMS), key=lambda x: x["rank"])
    kv = KernelVerifier(ROOT)
    gv = GSAVerifier(gsa_rows)
    sv = ShuffledKernelVerifier(ROOT, covered_r, perm_seed)
    sgv = GSAShuffledVerifier(gsa_rows, covered_r, sv.perm)
    dext_disc = []
    dext_stats = enumerate_grid(dext, kv, gv, sv, sgv, dext_disc,
                                "supplementary:d-ext")
    print("supplementary d-ext cells=%d concordant=%d (off-coverage "
          "abstention path)" % (dext_stats["cells"], dext_stats["concordant"]))

    # ---- primary statistic ---------------------------------------------------
    primary_cells = sum(grids["primary:" + n]["cells"]
                        for n in ("d-qa", "d-qa-r", "d-qa-t"))
    primary_conc = sum(grids["primary:" + n]["concordant"]
                       for n in ("d-qa", "d-qa-r", "d-qa-t"))
    c_dec = primary_conc / primary_cells
    all_conc = (primary_conc == primary_cells
                and all(g["concordant"] == g["cells"] for g in grids.values())
                and dext_stats["concordant"] == dext_stats["cells"])
    r_repro = 1.0 if c_dec == 1.0 else None

    def fmt_stats(g):
        return {
            "cells": g["cells"], "concordant": g["concordant"],
            "by_variant": {k: {"concordant": v[0], "cells": v[1]}
                           for k, v in g["by_variant"].items()},
            "by_type_variant": {"%s|%s" % k: {"concordant": v[0],
                                              "cells": v[1]}
                                for k, v in sorted(g["by_type"].items(),
                                                   key=lambda kv: str(kv[0]))},
        }

    result = {
        "experiment": "DECONF/1 Stage A1 (P3-E-DECONF-0) — aligned-generic-"
                      "store extensional-equivalence audit",
        "design": "docs/next/design/DECONF.md §3 (ASM-0961/ASM-0962)",
        "status_tags": {
            "C_dec": "MEASURED (exhaustive count, no sampling error, no CI)",
            "R_repro": "MEASURED-BY-INVARIANCE (identically 1.0 iff "
                       "C_dec = 1.0, per the §1 determinism lemma; not a "
                       "fresh model run)",
            "interpretation": "NOT CONCLUDED HERE — the 'kernel adds nothing "
                              "at runtime' reading is the coordinator's/"
                              "maintainer's to draw (§6 verdict semantics)",
        },
        "C_dec": c_dec,
        "C_dec_exact": "%d/%d" % (primary_conc, primary_cells),
        "R_repro": r_repro,
        "n_discordant": len(discordances),
        "discordances": discordances,
        "dext_supplementary_discordances": dext_disc,
        "grids": {k: fmt_stats(g) for k, g in grids.items()},
        "dext_supplementary": fmt_stats(dext_stats),
        "all_grids_fully_concordant": all_conc,
        "decision_space_disclosure": {
            "note": "vacuity guard (no-silent-caps discipline): the grid "
                    "must exercise accepts, rejects, abstentions, AND "
                    "true-vs-shuffled divergence, else concordance would be "
                    "trivial; counted over the PRIMARY grid's kernel-side "
                    "triples",
            "kernel_triple_distribution": mix["triples"],
            "true_vs_shuffled_divergent_item_answer_pairs":
                "%d/%d" % (mix["true_vs_shuffled_divergent"],
                           mix["item_answer_pairs"]),
            "true_variant_decidable_accept_vs_gold": {
                "counts": mix["true_decidable_vs_gold"],
                "reading": "[MEASURED] exhaustive contingency of "
                           "verifier-accept vs membership gold on all "
                           "decidable (item, admissible-answer) pairs — the "
                           "f2b-replicate assessment's circularity note "
                           "('gold was DEFINED by the same equality "
                           "check() tests'), previously analytic, is "
                           "count-verified iff the off-diagonal cells "
                           "(accept|nongold, reject|gold) are zero",
            },
        },
        "decision_semantics": {
            "triple": "(extract_ok, decidable, consistent) per "
                      "f2b_runner.verify_answer",
            "kernel_side": "the literal pinned code: KernelVerifier / "
                           "ShuffledKernelVerifier imported from "
                           "poc/f2b/runner/f2b_runner.py at sha "
                           + RUNNER_SHA256_PIN[:12],
            "gsa_side": "same checker class over the four-column GS-A rows "
                        "only (GSAVerifier / GSAShuffledVerifier in this "
                        "file); no record file or derivation touched at "
                        "check time",
            "answer_space": "closed IF-C surface: MC option keys; yes/no "
                            "for claim items",
        },
        "measured_lift_context": MEASURED_LIFT_CONTEXT,
        "invariance_lemma_scope": {
            "licensed_iff": "C_dec == 1.0",
            "statement": "the store's runtime role in the answer->check->"
                         "resample topology is an aligned deterministic "
                         "answer key; every F2-line endpoint (the +0.1507 "
                         "lift, its CIs, the shuffled-control readings, and "
                         "every future output of the same topology) is "
                         "bit-for-bit invariant under replacement of the "
                         "kernel store by its four-column projection GS-A",
            "scoped_to": {
                "checker": "poc/f2b/runner/f2b_runner.py@"
                           + RUNNER_SHA256_PIN,
                "store_projection": "poc/deconf-a1/gs-a.jsonl@" + gsa_sha,
                "note": "any checker or store schema change invalidates the "
                        "lemma and requires an A1 re-run (DECONF §7.1)",
            },
            "not_licensed": "authored-content value (knull-v2), authoring "
                            "economics (A-F0), consumption channels (A-E2), "
                            "any architecture whose coupling is not "
                            "answer->check->resample (DECONF §9.1)",
        },
        "pins": {
            "runner_sha256": RUNNER_SHA256_PIN,
            "f2b_manifest_sha256": F2B_MANIFEST_SHA256_PIN,
            "gs_a_sha256": gsa_sha,
            "shuffle_perm_seed": perm_seed,
            "shuffle_perm_sha256": shuf_kernel.perm_sha256,
            "corpus_pins": gsa_man["corpus_pins_verified"],
        },
    }
    out = os.path.join(HERE, "a1-result.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    print()
    print("C_dec   = %.10f  (%s)  [MEASURED]" % (c_dec, result["C_dec_exact"]))
    print("R_repro = %s        [MEASURED-BY-INVARIANCE]"
          % ("1.0 identically" if r_repro == 1.0 else "UNDEFINED (C_dec < 1)"))
    print("discordances: %d (+ %d on the supplementary d-ext grid)"
          % (len(discordances), len(dext_disc)))
    print("result -> %s" % out)


if __name__ == "__main__":
    main()
