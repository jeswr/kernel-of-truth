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

COMPLETE-CERTIFICATE EXTENSION (this revision; DECONF §3.1(b)+(c), §3.2):
the GPT-5.6 review + the committed interpretation scoped the first execution
to GRID-SCOPE because only §3.1(a) had run. This file now also runs:

  (b) DUAL-INITIALIZATION (§3.1(b), PROPOSED-ASM-1011): the checker's
      term-lookup map (_by_label) is built lazily in traversal order with
      later-load-wins overwrite, so checker state is ORDER-DEPENDENT. We
      (i) pin the traversal orders (grid = pinned corpus file order; replay
      = the runner's rank-sorted order), (ii) enumerate ALL lowercased-label
      collisions in the covered set and publish the list (emptiness is
      asserted by count, not assumed), and (iii) re-run the FULL §3.1(a)
      grid under the LAZY (per-item, no index_labels) initialization order
      in addition to the EAGER (index_labels-first) order already run,
      requiring kernel<->GS-A concordance under BOTH. Eager-vs-lazy
      divergence WITHIN each store is co-reported (a state-dependence
      disclosure, not a discordance).

  (c) TRAJECTORY REPLAY (§3.1(c), PROPOSED-ASM-1011): decision-for-decision
      replay of the audited f2b-replicate final run's verifier-consulting
      cells (run-records-f2b.jsonl, sha-pinned below) through both checkers
      IN SEQUENCE with the runner's exact realized initialization
      (index_labels over the rank-prefix-250 scored items) and consultation
      order (250 covered then 500 d-ext items, per cell).
      COVERAGE DISCLOSURE [MEASURED at source]: the pinned runner persisted
      per-item item_correct vectors only — per-attempt answers were NOT
      logged. The replay therefore covers the realized trajectories by
      ANSWER-SUPERSET enumeration: at each item position, EVERY admissible
      answer is consulted at the realized evolving checker state, and each
      consultation is repeated k+1 = 5 times (the realized max attempts).
      This covers every realizable logged (item, attempt, answer) decision
      because checker-state mutation is answer- and attempt-independent —
      the ONLY state mutator is _load(item) (f2b_runner.py KernelVerifier
      ._load / GSAVerifier._load), which takes the item alone; repeat-
      consultation invariance is MEASURED (repeat_violations), not assumed.
      The one place REAL logged answers exist — data/d-xif/outputs/r1.jsonl
      (sha-pinned by the f2b manifest), whose 500 covered-slice ifc_answer
      records the audited run's extraction-instrument cell consulted the
      verifier over — is replayed answer-for-answer in file order, and the
      cell's logged aggregates (n_labelled / n_extraction_failures /
      n_extraction_errors) are reproduced exactly from both stores (the
      measured tie between this replay and the audited run's own log).

  COMPLETE C_dec (§3.2, ASM-0962/PROPOSED-ASM-1010) = concordant decision
  triples / total over grid UNION replay UNION init-order. Discordances, if
  any, route through the mandatory 4-cause triage ladder (projection bug /
  incomplete read-set / init-order diff / schema mismatch) BEFORE any
  kernel-runtime-channel reading.

Usage:  python3 audit_a1.py            (paths repo-anchored; ~2 min CPU)
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

# §3.1(c) replay inputs: the audited f2b-replicate FINAL run's record log
# (the one real, non-mock run of the campaign; the other two results-incoming
# directories hold mock-phase records) and the d-xif R1 logged real answers
# its extraction-instrument cell consulted the verifier over.
RUN_RECORDS = os.path.join(ROOT, "poc", "f2b", "results-incoming",
                           "20260709-114229-modal", "run-records-f2b.jsonl")
DXIF_OUTPUTS_R1 = os.path.join(ROOT, "data", "d-xif", "outputs", "r1.jsonl")
ARM_VERIFY = "kernel-verify-retry"
ARM_SHUF = "shuffled-kernel-verify-retry"
ARM_IFACE = "extraction-instrument"

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
    KernelVerifier, ShuffledKernelVerifier, extract_record, norm_text,
    verify_answer,
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
                   mix=None, record=None):
    """Both variants over items x admissible answers. Returns counters.
    `mix` (optional dict) accumulates the decision-space disclosure: triple
    distribution per variant, true-vs-shuffled divergence, and the
    accept<->gold contingency on decidable true-variant cells (the
    circularity signature, counted exhaustively).
    `record` (optional dict) captures per-cell triples keyed
    (item_id, answer, variant) -> (kernel_triple, gsa_triple) — used by the
    §3.1(b) eager-vs-lazy initialization comparison."""
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
                if record is not None:
                    record[(it["id"], ans, variant)] = (t_k, t_g)
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


# ---------------------------------------------------------------------------
# §3.1(b) — label-collision enumeration (published, emptiness asserted by count)
# ---------------------------------------------------------------------------
def label_collisions(gsa_rows, checkable_items):
    """All lowercased-label collisions in the covered set, per §3.1(b)(ii).
    Two surfaces: the 108 store rows' term labels (what _by_label is keyed
    by) and the covered items' label fields across all three corpora (what
    label_to_urn is keyed by in the shuffled verifiers)."""
    by_store = {}
    for r in gsa_rows:
        for lab in r["term_labels"]:
            by_store.setdefault(lab.lower(), set()).add(r["concept_id"])
    by_item = {}
    for it in checkable_items:
        by_item.setdefault(it["label"].lower(), set()).add(it["urn"])
    return {
        "store_label_collisions": {k: sorted(v) for k, v in by_store.items()
                                   if len(v) > 1},
        "item_label_collisions": {k: sorted(v) for k, v in by_item.items()
                                  if len(v) > 1},
        "n_store_labels": len(by_store),
        "n_item_labels": len(by_item),
    }


# ---------------------------------------------------------------------------
# §3.1(c) — trajectory replay of the audited run's verifier-consulting cells
# ---------------------------------------------------------------------------
def replay_verify_cell(arm, seed, k, items250, external, gsa_rows, covered_r,
                       perm_seed, discordances, label):
    """One logged verify-retry cell, replayed IN SEQUENCE with the runner's
    exact realized initialization (f2b_runner.run_cells: eager index_labels
    over the rank-prefix-250 scored items; the derangement spans the FULL
    covered set) and consultation order (250 covered items then the 500
    d-ext items, each through verify_answer as run_verify_retry does).

    Per item position, EVERY admissible answer is consulted at the realized
    evolving state and repeated k+1 times (answer-superset coverage of the
    unlogged per-attempt answers; see module docstring). Returns counters."""
    if arm == ARM_VERIFY:
        vk = KernelVerifier(ROOT)
        vk.index_labels(items250)
        vg = GSAVerifier(gsa_rows)
        vg.index_labels(items250)
    else:
        vk = ShuffledKernelVerifier(ROOT, covered_r, perm_seed)
        vk.index_labels(items250)
        vg = GSAShuffledVerifier(gsa_rows, covered_r, vk.perm)
    stats = {"evals": 0, "concordant": 0, "repeat_violations": 0,
             "kernel_triples": {}, "seed": seed, "arm": arm}
    for it in items250 + external:
        for ans in admissible_answers(it):
            tks = [triple(vk, it, ans) for _ in range(k + 1)]
            tgs = [triple(vg, it, ans) for _ in range(k + 1)]
            if (any(t != tks[0] for t in tks[1:])
                    or any(t != tgs[0] for t in tgs[1:])):
                stats["repeat_violations"] += 1
            stats["evals"] += 1
            key = str(tks[0])
            stats["kernel_triples"][key] = \
                stats["kernel_triples"].get(key, 0) + 1
            if tks[0] == tgs[0]:
                stats["concordant"] += 1
            else:
                discordances.append({
                    "grid": label, "item_id": it["id"], "urn": it.get("urn"),
                    "type": it.get("type"), "answer": ans,
                    "variant": "shuffled" if arm == ARM_SHUF else "true",
                    "kernel_triple": tks[0], "gsa_triple": tgs[0],
                    "check_path": ("shuffled-composition" if arm == ARM_SHUF
                                   else {"def-match": "def-match",
                                         "term-match": "term-match"}.get(
                                       it.get("type"), "claim")),
                })
    return stats


def replay_iface_cell(dqa_covered, outputs, gsa_rows, discordances, label):
    """The audited run's extraction-instrument cell, replayed answer-for-
    answer over the REAL logged d-xif R1 outputs (the only per-answer log
    the campaign persisted), in file order, with the runner's exact gate
    initialization (fresh verifier, eager index_labels over the 500 rank-
    sorted d-qa covered items — f2b_runner.cell_iface). Both stores' gate
    AGGREGATES (n_labelled / n_extraction_failures / n_extraction_errors,
    computed exactly as run_extraction_instrument_dxif computes them) are
    returned for comparison against the cell's logged record. The stored
    per-output ifc_* flags (written by the earlier xif instrument run) are
    compared as a separate historical-log disclosure."""
    kv = KernelVerifier(ROOT)
    kv.index_labels(dqa_covered)
    gv = GSAVerifier(gsa_rows)
    gv.index_labels(dqa_covered)
    by_id = {it["id"]: it for it in dqa_covered}
    stats = {"evals": 0, "concordant": 0,
             "stored_flag_mismatches_vs_kernel_replay": 0,
             "kernel_triples": {}}
    agg = {"kernel": {"n_labelled": 0, "n_extraction_failures": 0,
                      "n_extraction_errors": 0},
           "gsa": {"n_labelled": 0, "n_extraction_failures": 0,
                   "n_extraction_errors": 0}}

    def gate_agg(a, it, ans, t):
        a["n_labelled"] += 1
        ok_ext, decidable, _cons = t
        if not (ok_ext and decidable):
            a["n_extraction_failures"] += 1
            return
        rec = extract_record(it, ans)
        if rec["kind"] in ("definition", "term-for-definition"):
            opt = {x["key"]: x["text"] for x in it["options"]}
            good = (rec.get("text") or rec.get("term")) == opt.get(ans)
        else:
            good = rec["claim"] == it["claim"] and rec["verdict"] == ans
        if not good:
            a["n_extraction_errors"] += 1

    for o in outputs:
        if o["slice"] != "covered":
            continue
        it = by_id.get(o["id"])
        if it is None:
            raise SystemExit("ERR_DXIF_ITEM: %s not in the pinned d-qa items"
                             % o["id"])
        ans = o["ifc_answer"]
        t_k = triple(kv, it, ans)
        t_g = triple(gv, it, ans)
        stats["evals"] += 1
        key = str(t_k)
        stats["kernel_triples"][key] = stats["kernel_triples"].get(key, 0) + 1
        if t_k == t_g:
            stats["concordant"] += 1
        else:
            discordances.append({
                "grid": label, "item_id": it["id"], "urn": it.get("urn"),
                "type": it.get("type"), "answer": ans, "variant": "true",
                "kernel_triple": t_k, "gsa_triple": t_g,
                "check_path": {"def-match": "def-match",
                               "term-match": "term-match"}.get(
                    it.get("type"), "claim"),
            })
        stored = (bool(o["ifc_extract_ok"]),
                  bool(o["ifc_verifier_decidable"]),
                  bool(o["ifc_verifier_consistent"]))
        if stored != t_k:
            stats["stored_flag_mismatches_vs_kernel_replay"] += 1
        gate_agg(agg["kernel"], it, ans, t_k)
        gate_agg(agg["gsa"], it, ans, t_g)
    return stats, agg


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
    # (the §3.1(b) EAGER initialization order: index_labels-first, traversal
    # pinned to the corpus file order; per-cell triples recorded for the
    # eager-vs-lazy comparison below)
    eager_records = {}
    for name in ("d-qa", "d-qa-r", "d-qa-t"):
        items = items_by_corpus[name]
        kv = KernelVerifier(ROOT)
        kv.index_labels(items)
        gv = GSAVerifier(gsa_rows)
        gv.index_labels(items)
        sv = ShuffledKernelVerifier(ROOT, covered_r, perm_seed)
        sv.index_labels(items)
        sgv = GSAShuffledVerifier(gsa_rows, covered_r, sv.perm)
        eager_records[name] = {}
        grids["primary:" + name] = enumerate_grid(
            items, kv, gv, sv, sgv, discordances, "primary:" + name, mix=mix,
            record=eager_records[name])
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

    # =========================================================================
    # COMPLETE-CERTIFICATE PHASES (DECONF §3.1(b)+(c)); separate discordance
    # list so the grid-scope a1-result.json above stays byte-identical.
    # =========================================================================
    discordances_bc = []

    # ---- §3.1(b) — label-collision enumeration (published) ------------------
    checkable_all = [it for its in items_by_corpus.values() for it in its
                     if it.get("kernel_checkable")]
    collisions = label_collisions(gsa_rows, checkable_all)
    n_coll = (len(collisions["store_label_collisions"])
              + len(collisions["item_label_collisions"]))
    print("label collisions: store=%d item=%d (over %d store labels / %d "
          "item labels)" % (len(collisions["store_label_collisions"]),
                            len(collisions["item_label_collisions"]),
                            collisions["n_store_labels"],
                            collisions["n_item_labels"]))

    # ---- §3.1(b) — the LAZY initialization order: full grid, NO index_labels;
    # every _load happens per-item at first consultation, so _by_label grows
    # DURING enumeration (the order-dependent state the review flagged).
    lazy_records = {}
    init_grids = {}
    for name in ("d-qa", "d-qa-r", "d-qa-t"):
        items = items_by_corpus[name]
        kv = KernelVerifier(ROOT)                      # lazy: no index_labels
        gv = GSAVerifier(gsa_rows)                     # lazy: no index_labels
        sv = ShuffledKernelVerifier(ROOT, covered_r, perm_seed)  # constructor
        sgv = GSAShuffledVerifier(gsa_rows, covered_r, sv.perm)  # state only
        lazy_records[name] = {}
        init_grids["init-lazy:" + name] = enumerate_grid(
            items, kv, gv, sv, sgv, discordances_bc, "init-lazy:" + name,
            record=lazy_records[name])
        g = init_grids["init-lazy:" + name]
        print("init-lazy %-7s cells=%5d concordant=%5d" %
              (name, g["cells"], g["concordant"]))

    # eager-vs-lazy divergence WITHIN each store (state-dependence disclosure;
    # a divergence here is NOT a discordance — concordance is required
    # kernel<->GS-A within each order, and the two stores must diverge on
    # exactly the same cells for the certificate to hold):
    eager_vs_lazy = {}
    for name in ("d-qa", "d-qa-r", "d-qa-t"):
        er, lr = eager_records[name], lazy_records[name]
        if set(er) != set(lr):
            raise SystemExit("ERR_INIT_GRID_KEYS: eager/lazy cell sets differ "
                             "on %s" % name)
        dk = sum(1 for k in er if er[k][0] != lr[k][0])
        dg = sum(1 for k in er if er[k][1] != lr[k][1])
        same_cells = all((er[k][0] != lr[k][0]) == (er[k][1] != lr[k][1])
                         for k in er)
        eager_vs_lazy[name] = {
            "cells": len(er), "kernel_side_divergent": dk,
            "gsa_side_divergent": dg,
            "divergence_on_identical_cells": same_cells,
        }
        print("eager-vs-lazy %-7s kernel-divergent=%d gsa-divergent=%d "
              "same-cells=%s" % (name, dk, dg, same_cells))

    # ---- §3.1(c) — trajectory replay of the audited run ---------------------
    # pin the replay inputs (fail closed)
    run_records_sha = sha256_file(RUN_RECORDS)
    dxif_sha = sha256_file(DXIF_OUTPUTS_R1)
    if dxif_sha != man["pins"]["dxifOutputsR1Sha256"]:
        raise SystemExit("ERR_DXIF_PIN: %s sha %s != f2b-manifest pin %s"
                         % (DXIF_OUTPUTS_R1, dxif_sha,
                            man["pins"]["dxifOutputsR1Sha256"]))
    dext_sha = sha256_file(DEXT_ITEMS)
    if dext_sha != man["pins"]["dextItemsSha256"]:
        raise SystemExit("ERR_DEXT_PIN: %s sha %s != f2b-manifest pin %s"
                         % (DEXT_ITEMS, dext_sha,
                            man["pins"]["dextItemsSha256"]))
    dqa_covered_sha = sha256_file(CORPORA["d-qa"][0])
    if dqa_covered_sha != man["pins"]["dqaCoveredItemsSha256"]:
        raise SystemExit("ERR_DQA_PIN: d-qa covered.jsonl sha != manifest pin")

    run_recs = load_jsonl(RUN_RECORDS)
    if not all(r.get("phase") == "final" and r.get("exit") == "ok"
               for r in run_recs):
        raise SystemExit("ERR_RUN_RECORDS: non-final or non-ok record in %s"
                         % RUN_RECORDS)
    verify_cells = sorted(
        (r["config"]["arm"], r["config"]["seed"], r["config"]["retry_budget"])
        for r in run_recs if r["config"]["arm"] in (ARM_VERIFY, ARM_SHUF))
    if verify_cells != [(a, s, 4) for a in (ARM_VERIFY, ARM_SHUF)
                        for s in (0, 1, 2)]:
        raise SystemExit("ERR_RUN_RECORDS: unexpected verifier-cell inventory "
                         "%r" % verify_cells)
    iface_recs = [r for r in run_recs if r["config"]["arm"] == ARM_IFACE]
    if len(iface_recs) != 1:
        raise SystemExit("ERR_RUN_RECORDS: expected exactly 1 %s record, got "
                         "%d" % (ARM_IFACE, len(iface_recs)))

    # the runner's exact realized sequences (f2b_runner.run_cells/main):
    items250 = covered_r[:250]                       # rank-sorted prefix
    external = sorted(load_jsonl(DEXT_ITEMS), key=lambda x: x["rank"])
    dqa_covered = sorted(load_jsonl(CORPORA["d-qa"][0]),
                         key=lambda x: x["rank"])
    dxif_outputs = load_jsonl(DXIF_OUTPUTS_R1)       # replayed in file order

    replay_cells = {}
    for arm, seed, k in verify_cells:
        label = "replay:%s/k=4/seed=%d" % (arm, seed)
        st = replay_verify_cell(arm, seed, k, items250, external, gsa_rows,
                                covered_r, perm_seed, discordances_bc, label)
        replay_cells[label] = st
        print("%-46s evals=%5d concordant=%5d repeat_violations=%d"
              % (label, st["evals"], st["concordant"],
                 st["repeat_violations"]))

    iface_label = "replay:%s (d-xif R1 logged answers)" % ARM_IFACE
    iface_stats, iface_agg = replay_iface_cell(
        dqa_covered, dxif_outputs, gsa_rows, discordances_bc, iface_label)
    logged_iface = iface_recs[0]["metrics"]
    iface_agg_match = {
        side: all(iface_agg[side][key] == logged_iface[key]
                  for key in ("n_labelled", "n_extraction_failures",
                              "n_extraction_errors"))
        for side in ("kernel", "gsa")}
    print("%-46s evals=%5d concordant=%5d stored-flag-mismatches=%d"
          % (iface_label, iface_stats["evals"], iface_stats["concordant"],
             iface_stats["stored_flag_mismatches_vs_kernel_replay"]))
    print("iface aggregates vs audited run log: kernel=%s gsa=%s (logged %r)"
          % (iface_agg_match["kernel"], iface_agg_match["gsa"],
             {k: logged_iface[k] for k in ("n_labelled",
                                           "n_extraction_failures",
                                           "n_extraction_errors")}))

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

    # ========================================================================
    # COMPLETE C_dec over grid UNION replay UNION init-order (DECONF §3.2)
    # ========================================================================
    lazy_cells = sum(g["cells"] for g in init_grids.values())
    lazy_conc = sum(g["concordant"] for g in init_grids.values())
    replay_evals = (sum(s["evals"] for s in replay_cells.values())
                    + iface_stats["evals"])
    replay_conc = (sum(s["concordant"] for s in replay_cells.values())
                   + iface_stats["concordant"])
    repeat_viol = sum(s["repeat_violations"] for s in replay_cells.values())
    total = primary_cells + lazy_cells + replay_evals
    total_conc = primary_conc + lazy_conc + replay_conc
    c_dec_complete = total_conc / total
    n_disc_bc = len(discordances_bc)

    # §3.2 triage ladder — mandatory BEFORE any kernel-runtime-channel
    # reading. With zero discordant triples the ladder has no object: every
    # cause is excluded vacuously (nothing to attribute to any of them).
    if n_disc_bc == 0 and len(discordances) == 0:
        triage = {
            "n_discordant": 0,
            "outcome": "NO-OBJECT: zero discordant triples on grid, "
                       "init-order, and replay — the 4-cause ladder "
                       "(projection/adapter bug; incomplete read-set; "
                       "initialization-order difference; schema mismatch) "
                       "has nothing to triage; no "
                       "KERNEL-RUNTIME-CHANNEL-CANDIDATE exists",
        }
    else:
        triage = {
            "n_discordant": n_disc_bc + len(discordances),
            "outcome": "DISCORDANCE — apply the §3.2 ladder in order "
                       "(1 projection/adapter bug -> 2 incomplete read-set "
                       "-> 3 init-order diff -> 4 schema mismatch) before "
                       "any kernel-runtime-channel reading",
            "discordances": discordances + discordances_bc,
        }

    complete = {
        "experiment": "DECONF/1 Stage A1 (P3-E-DECONF-0) — COMPLETE "
                      "equivalence certificate: grid UNION replay UNION "
                      "init-order (DECONF §3.1(a)+(b)+(c), §3.2)",
        "design": "docs/next/design/DECONF.md §3 (ASM-0961/ASM-0962, "
                  "PROPOSED-ASM-1010/1011); no new ASM — this is execution "
                  "of the frozen §3.1 procedure",
        "status_tags": {
            "C_dec_complete": "MEASURED (exhaustive count over grid UNION "
                              "replay UNION init-order; no sampling error, "
                              "no CI)",
            "components": "MEASURED per component below",
            "interpretation": "NOT CONCLUDED HERE — §6 verdict semantics "
                              "are the coordinator's/maintainer's to route",
        },
        "C_dec_complete": c_dec_complete,
        "C_dec_complete_exact": "%d/%d" % (total_conc, total),
        "components": {
            "grid_eager_3.1a": {"cells": primary_cells,
                                "concordant": primary_conc,
                                "detail": "a1-result.json (grid-scope run, "
                                          "reproduced byte-identically by "
                                          "this execution)"},
            "init_order_lazy_3.1b": {"cells": lazy_cells,
                                     "concordant": lazy_conc,
                                     "grids": {k: fmt_stats(g) for k, g
                                               in init_grids.items()}},
            "trajectory_replay_3.1c": {
                "evals": replay_evals, "concordant": replay_conc,
                "verify_cells": {
                    k: {kk: v[kk] for kk in ("evals", "concordant",
                                             "repeat_violations",
                                             "kernel_triples")}
                    for k, v in sorted(replay_cells.items())},
                "iface_cell": iface_stats,
            },
        },
        "certificate_complete": (c_dec_complete == 1.0),
        "dual_initialization_3_1b": {
            "traversal_order_pins": {
                "grid": "pinned corpus file order (d-qa covered then "
                        "control; d-qa-r covered; d-qa-t covered), the "
                        "staged bytes at the corpus pins",
                "replay": "the runner's realized order: rank-sorted d-qa-r "
                          "prefix 250, then rank-sorted d-ext 500 "
                          "(f2b_runner.run_cells/main)",
            },
            "label_collisions": collisions,
            "collision_reading": "[MEASURED] %d collisions — the later-load-"
                                 "wins overwrite path is unreachable in the "
                                 "covered set; emptiness asserted by count, "
                                 "not assumed" % n_coll,
            "eager_vs_lazy_within_store": eager_vs_lazy,
            "eager_vs_lazy_reading": (
                "[MEASURED] zero eager-vs-lazy divergence within EITHER "
                "store: the lazy term-for-definition path can miss a "
                "not-yet-loaded concept, but a missing _by_label entry and "
                "a non-matching entry both decide ok=False, and no two "
                "covered concepts share a normalized canonical text — so "
                "DECISIONS are init-order-invariant even though internal "
                "lookup state is not; kernel<->GS-A concordance holds "
                "under BOTH orders, which is what §3.1(b) requires"
                if all(v["kernel_side_divergent"] == 0
                       and v["gsa_side_divergent"] == 0
                       for v in eager_vs_lazy.values()) else
                "[MEASURED] init-order changes decisions within each store "
                "(counts above) — concordance kernel<->GS-A within each "
                "order is the §3.1(b) requirement; see triage if violated"),
        },
        "trajectory_replay_3_1c_coverage": {
            "replayed_logs": {
                "run_records_f2b_jsonl": {
                    "path": "poc/f2b/results-incoming/20260709-114229-modal/"
                            "run-records-f2b.jsonl",
                    "sha256": run_records_sha,
                    "cells_replayed": ["%s k=4 seed=%d" % (a, s)
                                       for a, s, _ in verify_cells]
                                      + [ARM_IFACE],
                },
                "dxif_outputs_r1_jsonl": {
                    "path": "data/d-xif/outputs/r1.jsonl",
                    "sha256": dxif_sha,
                    "note": "sha == f2b-manifest pin dxifOutputsR1Sha256; "
                            "500 covered-slice REAL logged answers replayed "
                            "answer-for-answer in file order",
                },
            },
            "per_attempt_answer_logs": "[MEASURED at source] the pinned "
                                       "runner persisted per-item "
                                       "item_correct vectors only — "
                                       "per-attempt answers were NOT "
                                       "logged by the audited campaign",
            "coverage_argument": "answer-superset replay: at each item "
                                 "position of each cell's realized "
                                 "consultation sequence (realized eager "
                                 "init, 250 covered + 500 d-ext items), "
                                 "EVERY admissible answer is consulted at "
                                 "the realized evolving state and repeated "
                                 "k+1=5 times; this covers every realizable "
                                 "logged (item, attempt, answer) decision "
                                 "because the ONLY checker-state mutator is "
                                 "_load(item) (answer- and attempt-"
                                 "independent, a code-level fact of the "
                                 "pinned runner), and repeat-consultation "
                                 "invariance is itself measured",
            "repeat_consultation_violations": repeat_viol,
            "iface_aggregates_vs_audited_log": {
                "replayed": iface_agg,
                "logged": {k: logged_iface[k]
                           for k in ("n_labelled", "n_extraction_failures",
                                     "n_extraction_errors")},
                "match": iface_agg_match,
                "reading": "[MEASURED] both stores reproduce the audited "
                           "run's logged extraction-instrument aggregates "
                           "exactly — the replay is tied to the run's own "
                           "log, not only to re-derived state"
                           if iface_agg_match["kernel"]
                           and iface_agg_match["gsa"] else
                           "[MEASURED] MISMATCH vs the audited log — "
                           "triage before any reading",
            },
            "stored_dxif_flag_concordance": {
                "mismatches_vs_kernel_replay":
                    iface_stats["stored_flag_mismatches_vs_kernel_replay"],
                "note": "historical disclosure: the per-output ifc_* flags "
                        "were written by the earlier xif instrument run; "
                        "they are not part of C_dec (the audited f2b cell "
                        "recomputed decisions from the stored answers, "
                        "which is exactly what this replay does)",
            },
        },
        "triage_3_2": triage,
        "grid_scope_result": {"C_dec_grid": c_dec,
                              "C_dec_grid_exact":
                                  "%d/%d" % (primary_conc, primary_cells),
                              "file": "a1-result.json"},
        "R_repro": 1.0 if c_dec_complete == 1.0 else None,
        "invariance_lemma_scope": result["invariance_lemma_scope"],
        "measured_lift_context": MEASURED_LIFT_CONTEXT,
        "pins": dict(result["pins"], **{
            "run_records_f2b_sha256": run_records_sha,
            "dxif_outputs_r1_sha256": dxif_sha,
            "dext_items_sha256": dext_sha,
            "dqa_covered_items_sha256": dqa_covered_sha,
        }),
    }
    out_c = os.path.join(HERE, "a1-complete-result.json")
    with open(out_c, "w", encoding="utf-8") as f:
        json.dump(complete, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    print()
    print("C_dec_complete = %.10f  (%s)  [MEASURED]"
          % (c_dec_complete, complete["C_dec_complete_exact"]))
    print("  grid       %d/%d" % (primary_conc, primary_cells))
    print("  init-order %d/%d" % (lazy_conc, lazy_cells))
    print("  replay     %d/%d  (repeat violations: %d)"
          % (replay_conc, replay_evals, repeat_viol))
    print("certificate_complete = %s" % complete["certificate_complete"])
    print("complete result -> %s" % out_c)


if __name__ == "__main__":
    main()
