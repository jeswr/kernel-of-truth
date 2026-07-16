#!/usr/bin/env python3
"""build_corpora_96.py — F1-K REVISION-6 input-corpora rebuild ($0, no model).

Successor of build_corpora.py (2026-07-13 kernel-v0-only pass, 49 clusters /
n=1440). REPLACES the model-independent bytes of the three corpora

    data/f1k-trigger-map-v1/   data/f1k-eval-v1/   data/f1k-carriers-v1/

at the FROZEN REVISION-6 geometry (maintainer-approved 2026-07-15):

    C = 96 concepts (45 kernel-v0 + 51 kernel-v1, the askability-screen
    selection, ranks 1..96 of poc/f1k-askability/reports/candidate-report.json),
    n_test = 1573 (the approved raise of the registered 1440 cap),
    per-cluster test counts pinned as geometry.m_list_by_rank of
    poc/f1k-askability/reports/power-report-n1573.json (m_min 10,
    m_mean 16.3854, m_max 18, sum 1573).

CONSTRUCTION DISCIPLINE — reuse, do not re-derive:
  [SC96] poc/f1k-askability/screen.py — the frozen deterministic machinery
         (load_kernel_records, ast_parseable, load_items_redacted,
         raw_candidates, resolve, allocate) and its constants.
  [PWR]  poc/f1k-askability/power_n1573.py — the exact pipeline this builder
         mirrors byte-for-byte to rebuild the Part-1 state, re-verify the
         frozen redacted-input hash, re-derive the selection, and allocate at
         N_TEST=1573.  The ONLY addition here is ITEM-IDENTITY tracking in the
         allocation (screen.allocate returns counts only); the identity
         allocator is cross-checked count-for-count against screen.allocate
         AND element-by-element against the pinned m_list_by_rank (fail
         closed on any difference).
  [BC]   build_corpora.py (this directory) — parse_wn_dict, build_triggers,
         compile_matchers, render_template, HEADER/CUE/LABEL_ALPHABET,
         SOURCES pins, seeded_derangement, build_contexts/CONTEXT_FRAMES,
         MATCHING_RULE, the row shapes and the OP-1..OP-9 operationalisation
         register (OP-3 is SUPERSEDED by the REVISION-6 universe decision).
  [CON]  data/f1k-contrast-v1/ — the certified kernel/dictionary texts; the
         concept texts emitted here MUST be byte-identical (fail closed).

Fidelity checks (ALL fail-closed, reported on stdout):
  1. pinned benchmark parquet sha256 == [BC] SOURCES (+ sources.lock.json)
  2. redacted-input hash == the frozen pre-screen pin (hash-report.json)
  3. re-derived selection == candidate-report.json ranks/urns (96)
  4. all 96 selected pass contrast (distinctness-report.json)
  5. identity allocation counts == screen.allocate counts (dev AND test)
  6. per-cluster test counts == power-report-n1573.json m_list_by_rank,
     element-by-element in rank order; totals test=1573 dev=96
  7. concept texts byte-identical to data/f1k-contrast-v1/<rank>-<slug>/
     (kernel.txt, dictionary.txt, kernel.ast.json)
  8. derangements (seeds 11/101/102/103) are fixed-point-free permutations
     over the 96 carrier slots
  9. guard = 60 zero-trigger items; every guard template has zero candidates
 10. construction contexts disjoint from every eval template
 11. clusters_with_m_ge_8 == 96/96

$0, no GPU, no network, no model call.  Deterministic: byte-identical on
re-run (only PRNG uses = the registered derangement seeds).  Token-level
fields remain BLOCKED exactly as the 2026-07-13 manifest records (they are
pure functions of this corpus + the tokenizer pinned at bring-up).
source/ parquets, sources.lock.json and template-spec.json are CARRIED OVER
unchanged (universe-independent); everything else is regenerated.
"""

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]                      # repo root (kernel-of-truth/)
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "poc" / "f1k-askability"))
sys.path.insert(0, str(ROOT / "tools" / "registry"))

import build_corpora as bc                  # [BC] frozen builder machinery
import screen as sc                         # [SC96] frozen screen machinery
import kot_common as kc                     # kot-corpus-hash/1 + JCS bytes

PASS_STAMP = "2026-07-15 fable REVISION-6 data-construction pass ($0)"
SUPERSEDES = ("supersedes the 2026-07-13 designer-23 kernel-v0-only pass "
              "(49 clusters, n=1440) — REVISION-6 frozen geometry C=96 / "
              "n_test=1573, maintainer-approved 2026-07-15")

N_TEST = 1573                # [PWR] maintainer-approved raise of the 1440 cap
C_APPROVED = 96              # [PWR] approved operating C
DEV_N = sc.DEV_N             # 96  [REG n_planned.dev_split_items]
GUARD_N = bc.GUARD_N         # 60  [REG n_planned.off_concept_guard_items]

ASK = ROOT / "poc" / "f1k-askability"
CONTRAST = ROOT / "data" / "f1k-contrast-v1"

ERR = "ERR_F1K_CORPORA96"
CHECKS = []


def fail(msg):
    print("%s: %s" % (ERR, msg), file=sys.stderr)
    sys.exit(2)


def check(name, ok, note=""):
    CHECKS.append({"check": name, "ok": bool(ok), "note": note})
    print("  CHECK %-4s %s%s" % ("OK" if ok else "FAIL", name,
                                 (" — " + note) if note else ""))
    if not ok:
        fail("fidelity check failed: %s (%s)" % (name, note))


# ---------------------------------------------------------------------------
# gold-index sidecar loader — the SAME parquet bytes + admission rule as
# [SC96] load_items_redacted (which drops gold for blindness); this data-
# construction pass needs gold_index/subject/native_id back on each item.
# ---------------------------------------------------------------------------
def load_gold_map():
    import pyarrow.parquet as pq
    src_dir = ROOT / "data" / "f1k-eval-v1" / "source"
    lock = json.load(open(src_dir / "sources.lock.json", encoding="utf-8"))
    lock_sha = {e["key"]: e["sha256"] for e in lock["sources"]}
    gold = {}
    for rank, (key, ds, rev, path, want, split) in enumerate(bc.SOURCES):
        if lock_sha.get(key) != want:
            fail("sources.lock.json sha for %s != [BC] SOURCES pin" % key)
        p = src_dir / ("%s.parquet" % key)
        got = bc.sha256_file(p)
        if got != want:
            fail("source %s sha256 %s != pinned %s" % (key, got, want))
        rows = pq.read_table(p).to_pylist()
        for ri, r in enumerate(rows):           # [BC]/[SC96] admission rule
            if key == "mmlu":
                opts = [o.strip() for o in r["choices"]]
                g = int(r["answer"])
                native = "%s/%d" % (r["subject"], ri)
                subject = r["subject"]
            else:
                ch = r["choices"]
                opts = [o.strip() for o in ch["text"]]
                labels_pub = list(ch["label"])
                if r["answerKey"] not in labels_pub:
                    continue
                g = labels_pub.index(r["answerKey"])
                native = str(r["id"])
                subject = None
            if not (3 <= len(opts) <= 5) or not (0 <= g < len(opts)):
                continue
            iid = "%s#%s" % (key, native)
            if iid in gold:
                fail("duplicate item_id %s" % iid)
            gold[iid] = {"gold_index": g, "subject": subject,
                         "native_id": native}
    return gold


# ---------------------------------------------------------------------------
# ITEM-IDENTITY allocation — the faithful equivalent of [SC96] sc.allocate
# (which returns counts only).  Same pool ordering, same dev-first round-
# robin, same test breadth-first-to-m=8 then round-robin.  Cross-checked
# count-for-count against sc.allocate in main().
# ---------------------------------------------------------------------------
def allocate_items(prefix_cidx, item_cands, items, q_end, n_test, dev_n):
    allowed = set(prefix_cidx)
    by_cluster = {c: [] for c in prefix_cidx}
    span_of = {}
    for ii, it in enumerate(items):
        cands = item_cands.get(ii)
        if not cands:
            continue
        spans = sc.resolve(cands, allowed)
        if not spans:
            continue
        span_of[ii] = spans
        cluster = spans[0][2]                 # [BC OP-6a] leftmost resolved
        stem = spans[0][0] < q_end[ii]
        by_cluster[cluster].append((0 if stem else 1, it["source_rank"],
                                    it["row_index"], ii))
    for c in by_cluster:
        by_cluster[c].sort()                  # stem-first, source, row
    used = {c: 0 for c in prefix_cidx}

    def take(c):
        if used[c] < len(by_cluster[c]):
            ii = by_cluster[c][used[c]][3]
            used[c] += 1
            return ii
        return None

    dev = []                                  # [(cluster_cidx, item_index)]
    while len(dev) < dev_n:
        progressed = False
        for c in prefix_cidx:
            if len(dev) >= dev_n:
                break
            ii = take(c)
            if ii is not None:
                dev.append((c, ii))
                progressed = True
        if not progressed:
            break
    test = []
    for _ in range(sc.POWER_GATE_MIN_M):      # breadth-first to m=8
        for c in prefix_cidx:
            if len(test) >= n_test:
                break
            ii = take(c)
            if ii is not None:
                test.append((c, ii))
    progressing = True                        # round-robin to the cap
    while len(test) < n_test and progressing:
        progressing = False
        for c in prefix_cidx:
            if len(test) >= n_test:
                break
            ii = take(c)
            if ii is not None:
                test.append((c, ii))
                progressing = True
    return dev, test, span_of


# ===========================================================================
def main():
    print("=" * 72)
    print("F1-K REVISION-6 corpora rebuild — %s" % PASS_STAMP)
    print("=" * 72)
    tm_dir = ROOT / "data" / "f1k-trigger-map-v1"
    ev_dir = ROOT / "data" / "f1k-eval-v1"
    ca_dir = ROOT / "data" / "f1k-carriers-v1"

    # ---- Part-1 state, byte-for-byte the [PWR] pipeline --------------------
    wn = bc.parse_wn_dict()
    recs, n_raw, n_dup = sc.load_kernel_records()
    bc.build_triggers(recs, wn)
    print("joined kernel-v0+v1 universe: %d raw -> %d synset-deduped "
          "(%d dropped)" % (n_raw, len(recs), n_dup))
    pool = []
    for r in recs:
        ok, ast_bytes = sc.ast_parseable(r["explication"])
        if not (r["gloss"] and r["gloss"].strip()) or not ok:
            continue
        if not (r.get("d2_gloss") and r["d2_gloss"].strip()) or not r["triggers"]:
            continue
        r["ast_bytes"] = ast_bytes
        pool.append(r)
    for i, r in enumerate(pool):
        r["index"] = i
    matchers = bc.compile_matchers(pool)
    hdr_cids = set()
    for text in (bc.HEADER, bc.CUE, " ".join(bc.LABEL_ALPHABET)):
        for (_s, _e, cidx) in sc.raw_candidates(text, matchers):
            hdr_cids.add(cidx)
    items = sc.load_items_redacted()          # sha-verifies parquets [SC96]
    gold = load_gold_map()                    # sha-verifies again + lock file
    check("sources: parquet sha256 == [BC] SOURCES pins (+ lock file)", True,
          "verified twice (screen loader + gold loader); source/ unchanged")
    miss = [it["item_id"] for it in items if it["item_id"] not in gold]
    check("gold sidecar covers every admitted item",
          not miss and len(gold) == len(items),
          "%d items" % len(items))

    # frozen redacted-input hash re-verification [PWR]
    redacted_view = [{"item_id": it["item_id"], "source": it["source"],
                      "question": it["question"], "options": it["options"]}
                     for it in sorted(items, key=lambda x: x["item_id"])]
    redacted_hash = sc.sha256_bytes(kc.canonical_bytes(redacted_view))
    want = json.load(open(ASK / "reports" / "hash-report.json",
                          encoding="utf-8"))[
        "redacted_input_hash_frozen_before_screen"]
    check("redacted-input hash == frozen pre-screen pin",
          redacted_hash == want, redacted_hash[:16] + "…")

    item_cands = {}
    q_end = {}
    for ii, it in enumerate(items):
        tpl = bc.render_template(it["question"], it["options"])
        it["template_text"] = tpl
        q_end[ii] = len(bc.HEADER) + len(it["question"])
        cands = sc.raw_candidates(tpl, matchers)
        if cands:
            item_cands[ii] = cands
    allowed_all = set(range(len(pool)))
    raw_match = [0] * len(pool)
    excl = [0] * len(pool)
    excl_stem = [0] * len(pool)
    for ii, cands in item_cands.items():
        for (_s, _e, cidx) in cands:
            raw_match[cidx] += 1
        spans = sc.resolve(cands, allowed_all)
        if spans:
            win = spans[0][2]
            excl[win] += 1
            if spans[0][0] < q_end[ii]:
                excl_stem[win] += 1
    for r in pool:
        i = r["index"]
        r["raw_match"] = raw_match[i]
        r["excl_total"] = excl[i]
        r["excl_stem"] = excl_stem[i]
        r["collision_fraction"] = (round((raw_match[i] - excl[i]) /
                                         raw_match[i], 6)
                                   if raw_match[i] else 0.0)
        r["projected_m_test"] = excl[i]
        r["header_cue_collision"] = i in hdr_cids
    survivors = [r for r in pool
                 if r["projected_m_test"] >= sc.POWER_GATE_MIN_M
                 and not r["header_cue_collision"]]
    survivors.sort(key=lambda r: (-r["projected_m_test"], -r["excl_stem"],
                                  -r["excl_total"], r["collision_fraction"],
                                  r["synset"].encode("utf-8")))
    for i, r in enumerate(survivors):
        r["rank"] = i + 1
    selected = survivors[:sc.SELECT_N]

    # selection cross-check vs the committed candidate report [PWR]
    cand = json.load(open(ASK / "reports" / "candidate-report.json",
                          encoding="utf-8"))
    want_sel = [(c["rank"], c["urn"]) for c in cand["selected"]]
    got_sel = [(r["rank"], r["urn"]) for r in selected]
    check("re-derived selection == candidate-report.json (rank, urn)",
          want_sel == got_sel, "96 concepts, ranks 1..96")

    dis = json.load(open(ASK / "reports" / "distinctness-report.json",
                         encoding="utf-8"))
    passed_urns = {c["urn"] for c in dis["concepts"]
                   if c["in_selected"] and c["contrast_pass"]}
    pass_selected = [r for r in selected if r["urn"] in passed_urns]
    check("all selected pass contrast (distinctness-report.json)",
          len(pass_selected) == C_APPROVED,
          "%d/%d" % (len(pass_selected), C_APPROVED))

    # ---- allocation at n=1573 with ITEM IDENTITY ---------------------------
    sc.N_TEST = N_TEST                        # the [PWR] departure, verbatim
    prefix = [r["index"] for r in pass_selected]        # rank order
    ref_test, ref_dev, ref_ntest, ref_ndev = sc.allocate(
        prefix, item_cands, items, q_end)     # counts-only frozen reference
    dev_pairs, test_pairs, span_of = allocate_items(
        prefix, item_cands, items, q_end, N_TEST, DEV_N)
    my_test = {c: 0 for c in prefix}
    for c, _ii in test_pairs:
        my_test[c] += 1
    my_dev = {c: 0 for c in prefix}
    for c, _ii in dev_pairs:
        my_dev[c] += 1
    check("identity allocator == screen.allocate (test counts, all 96)",
          my_test == ref_test)
    check("identity allocator == screen.allocate (dev counts, all 96)",
          my_dev == ref_dev)
    pwr = json.load(open(ASK / "reports" / "power-report-n1573.json",
                         encoding="utf-8"))
    m_want = pwr["geometry"]["m_list_by_rank"]
    m_got = [my_test[c] for c in prefix]
    check("per-cluster test counts == power-report m_list_by_rank "
          "(element-by-element, rank order)", m_got == m_want,
          "min %d mean %.4f max %d sum %d"
          % (min(m_got), sum(m_got) / len(m_got), max(m_got), sum(m_got)))
    check("totals: n_test == 1573, n_dev == 96 == screen n_dev",
          len(test_pairs) == N_TEST == ref_ntest
          and len(dev_pairs) == DEV_N == ref_ndev
          == pwr["geometry"]["n_dev"])
    check("clusters_with_m_ge_8 == 96/96",
          sum(1 for v in m_got if v >= sc.POWER_GATE_MIN_M) == 96)

    # guard: [BC OP-6] first 60 zero-trigger items (zero raw candidates over
    # the gate-pool matcher — 'match NOTHING anywhere in the template'), at
    # the new universe, in (source_rank, row_index) order.
    zero = [ii for ii in range(len(items)) if ii not in item_cands]
    zero.sort(key=lambda ii: (items[ii]["source_rank"],
                              items[ii]["row_index"]))
    guard_ii = zero[:GUARD_N]
    check("guard = 60 zero-trigger items (supply %d)" % len(zero),
          len(guard_ii) == GUARD_N and
          all(not sc.raw_candidates(items[ii]["template_text"], matchers)
              for ii in guard_ii))

    # ---- concept-text byte equality vs data/f1k-contrast-v1 [CON] ----------
    slot_by_cidx = {}
    n_eq = 0
    for r in pass_selected:
        slot_by_cidx[r["index"]] = r["rank"] - 1      # slot = rank-1
        d = CONTRAST / ("%03d-%s" % (r["rank"], sc.slug_of(r["urn"])))
        k_pin = open(d / "kernel.txt", "rb").read()
        d_pin = open(d / "dictionary.txt", "rb").read()
        a_pin = open(d / "kernel.ast.json", "rb").read()
        if (k_pin != r["gloss"].encode("utf-8")
                or d_pin != r["d2_gloss"].encode("utf-8")
                or a_pin != r["ast_bytes"]):
            fail("concept texts differ from pinned f1k-contrast-v1 at %s" % d)
        n_eq += 1
    check("concept texts byte-identical to f1k-contrast-v1 "
          "(kernel.txt + dictionary.txt + kernel.ast.json)",
          n_eq == C_APPROVED, "%d/96 concepts" % n_eq)

    # =======================================================================
    # 1. data/f1k-trigger-map-v1 — regenerated at the joined universe
    # =======================================================================
    kv0_pin = kc.corpus_hash(str(ROOT), "kernel-v0")
    kv1_pin = kc.corpus_hash(str(ROOT), "kernel-v1")
    rank_of_urn = {r["urn"]: r["rank"] for r in pass_selected}
    pool_urns = {r["urn"] for r in pool}
    univ = sorted(recs, key=lambda r: r["urn"])   # canonical index = URN order
    n_phrases = sum(len(r["triggers"]) for r in univ)
    tmap = {
        "name": "f1k-trigger-map-v1",
        "built": PASS_STAMP,
        "supersedes": SUPERSEDES,
        "recipe": "registry/experiments/f1k.json pins.corpus_hashes"
                  "[f1k-trigger-map-v1] + design §2.3 (G-lex) / §R4 (gate "
                  "precedence) / §R3.2, at the REVISION-6 universe: the "
                  "kernel-v0 + kernel-v1 synset-deduped join of the frozen "
                  "askability screen (poc/f1k-askability/screen.py "
                  "load_kernel_records + [BC] build_triggers)",
        "kernel_source": {
            "corpora": ["kernel-v0", "kernel-v1"],
            "kot_corpus_hash_v1": {"kernel-v0": kv0_pin, "kernel-v1": kv1_pin},
            "join": "synset-deduped (kernel-v1 preferred on collision); "
                    "records without a synset alignment are outside the "
                    "universe (WordNet-surface expansion rule)",
            "reading": "OP-3 SUPERSEDED: the REVISION-6 maintainer-approved "
                       "geometry (2026-07-15) fixes the universe to the "
                       "joined v0+v1 records of the askability screen; the "
                       "2026-07-13 kernel-v0-only reading (C<=54) is void",
        },
        "wordnet_source": {
            "corpus": "lexical-wn31 (in-repo WN3.1 source dict + "
                      "alignment-kernel-v0.json, kot-lex-align/1; kernel-v1 "
                      "records carry their synset inline)",
            "expansion": "aligned synset lemmas + derivationally-related "
                         "('+' pointer) word lemmas, lowercased, "
                         "underscores to spaces, syntactic markers stripped",
        },
        "matching_rule": bc.MATCHING_RULE,
        "gate_precedence": {
            "overlap": "longest trigger match, then earliest span start, "
                       "then lowest concept index [DES §R4]",
            "single_carrier_per_position": True,
            "label_tokens_never_triggers": True,
            "multi_concept_tag": "items with >1 distinct resolved concept "
                                 "are tagged 'multi-concept' (descriptive "
                                 "subgroup) [DES §R4]",
            "gate_pool": "matching/resolution runs over the retention-"
                         "filtered gate pool (gloss + parseable kot-ast/1 + "
                         "WN dictionary gloss + >=1 trigger), the screen's "
                         "frozen counting universe; concepts outside it "
                         "never gate (in_gate_pool per concept below)",
        },
        "counts": {
            "kernel_records_joined_raw": n_raw,
            "joined_universe_synset_deduped": len(recs),
            "dedup_dropped": n_dup,
            "concepts_with_triggers": sum(1 for r in univ if r["triggers"]),
            "gate_pool_retention_filtered": len(pool),
            "selected_ranks_1_to_96": C_APPROVED,
            "trigger_phrases": n_phrases,
        },
        "concepts": [{
            "index": i, "urn": r["urn"], "label": r["label"],
            "source": r["source"], "synset": r["synset"],
            "explication_gloss_sha256": (sc.sha256_bytes(
                r["gloss"].encode("utf-8")) if r.get("gloss") else None),
            "triggers": r["triggers"],
            "trigger_provenance": r["trigger_provenance"],
            "in_gate_pool": r["urn"] in pool_urns,
            "selected_rank": rank_of_urn.get(r["urn"]),
        } for i, r in enumerate(univ)],
    }
    bc.write_json(tm_dir / "trigger-map.json", tmap)

    # =======================================================================
    # 2. data/f1k-eval-v1 — items at the 96-concept geometry
    #    (source/ + sources.lock.json + template-spec.json CARRIED OVER)
    # =======================================================================
    pool_by_cidx = {r["index"]: r for r in pool}

    def emit_row(cluster_cidx, ii, split, with_d3):
        it = items[ii]
        g = gold[it["item_id"]]
        row = {
            "item_id": it["item_id"],
            "split": split,
            "source": {"key": it["source"], "row_index": it["row_index"],
                       "native_id": g["native_id"]},
            "question": it["question"],
            "options": it["options"],
            "labels": bc.LABEL_ALPHABET[:len(it["options"])],
            "gold_index": g["gold_index"],
            "template_text": it["template_text"],
            "template_sha256": sc.sha256_bytes(
                it["template_text"].encode("utf-8")),
        }
        if split == "guard":
            row["char_spans"] = []
            row["cluster"] = None
            row["tags"] = []
        else:
            spans = span_of[ii]
            if spans[0][2] != cluster_cidx:
                fail("span/cluster mismatch on %s" % it["item_id"])
            stem = spans[0][0] < q_end[ii]
            cset = sorted({s[2] for s in spans})
            row["char_spans"] = [[s, e, slot_by_cidx[c]]
                                 for (s, e, c) in spans]
            row["cluster"] = pool_by_cidx[cluster_cidx]["urn"]
            row["tags"] = ((["multi-concept"] if len(cset) > 1 else [])
                           + ([] if stem else ["option-trigger"]))
            if with_d3:
                # d3-text [DES §2.6]; OP-9 prepend = gloss + one blank line
                d3 = (pool_by_cidx[cluster_cidx]["gloss"] + "\n\n"
                      + it["template_text"])
                row["d3_template_text"] = d3
                row["d3_template_sha256"] = sc.sha256_bytes(
                    d3.encode("utf-8"))
        return row

    test_rows = [emit_row(c, ii, "test", True) for c, ii in test_pairs]
    dev_rows = [emit_row(c, ii, "dev", True) for c, ii in dev_pairs]
    guard_rows = [emit_row(None, ii, "guard", False) for ii in guard_ii]
    bc.write_jsonl(ev_dir / "items" / "test.jsonl", test_rows)
    bc.write_jsonl(ev_dir / "items" / "dev.jsonl", dev_rows)
    bc.write_jsonl(ev_dir / "items" / "guard.jsonl", guard_rows)

    coverage = {
        "built": PASS_STAMP,
        "supersedes": SUPERSEDES,
        "n_test": len(test_rows), "n_dev": len(dev_rows),
        "n_guard": len(guard_rows),
        "n_clusters_realized": sum(1 for v in m_got if v),
        "clusters_with_m_ge_8": sum(1 for v in m_got
                                    if v >= sc.POWER_GATE_MIN_M),
        "power_gate": "C>=%d each m>=%d (ASM-2271) at the approved "
                      "n_test=%d — SATISFIED at the REVISION-6 geometry"
                      % (bc.POWER_GATE_MIN_C, sc.POWER_GATE_MIN_M, N_TEST),
        "power_gate_satisfiable": True,
        "concept_universe_bound": len(recs),
        "geometry_pin": "poc/f1k-askability/reports/power-report-n1573.json "
                        "geometry.m_list_by_rank (verified element-by-"
                        "element by this build)",
        "m_list_by_rank": m_got,
        "m_per_cluster": {r["urn"]: my_test[r["index"]]
                          for r in pass_selected},
        "dev_per_cluster": {r["urn"]: my_dev[r["index"]]
                            for r in pass_selected},
        "composition_by_source": {},
        "composition_by_mmlu_subject": {},
    }
    for c, ii in test_pairs:
        it = items[ii]
        coverage["composition_by_source"][it["source"]] = \
            coverage["composition_by_source"].get(it["source"], 0) + 1
        subj = gold[it["item_id"]]["subject"]
        if subj:
            coverage["composition_by_mmlu_subject"][subj] = \
                coverage["composition_by_mmlu_subject"].get(subj, 0) + 1
    bc.write_json(ev_dir / "coverage-report.json", coverage)

    # =======================================================================
    # 3. data/f1k-carriers-v1 — generator components at 96 slots
    # =======================================================================
    nc = C_APPROVED
    carrier_index_map = [{"carrier_slot": r["rank"] - 1, "rank": r["rank"],
                          "urn": r["urn"], "source": r["source"],
                          "synset": r["synset"]} for r in pass_selected]
    derangements = {}
    for seed in (bc.PILOT_KDRNG_SEED,) + bc.DRNG_SEEDS:
        p = bc.seeded_derangement(nc, seed)
        if sorted(p) != list(range(nc)) or any(p[i] == i for i in range(nc)):
            fail("derangement seed %d not FPF over %d slots" % (seed, nc))
        derangements[str(seed)] = p
    check("derangements seeds 11/101/102/103 fixed-point-free over 96 slots",
          True, "[DRV seeded_derangement], OP-7")
    bc.write_json(ca_dir / "generator" / "derangements.json", {
        "built": PASS_STAMP,
        "supersedes": SUPERSEDES,
        "recipe": "DES SSR2 (§R2 d1-drng: seeded fixed-point-free "
                  "derangement over the concepts present in the test set, "
                  "layerwise norm-matched) + REG design.seeds / "
                  "freeze_manifest A(vii)",
        "algorithm": "OP-7: f1k_driver.py seeded_derangement — "
                     "random.Random(seed).shuffle(range(nc)) rejected until "
                     "fixed-point-free (the run harness's algorithm; "
                     "requires (A) adoption)",
        "domain": "carrier slots 0..%d = the frozen selected 96 concepts in "
                  "selection-rank order (slot = rank-1); every slot fires in "
                  ">=10 frozen test items (SSR2 'concepts present in the "
                  "test set'); see carrier-index-map.json" % (nc - 1),
        "nc": nc,
        "seeds": {"pilot_panel": bc.PILOT_KDRNG_SEED,
                  "main": list(bc.DRNG_SEEDS), "d0_table": bc.PILOT_D0_SEED},
        "derangements": derangements,
        "layerwise_norm_matched": "REQUIRED at realization: deranged "
                                  "carrier direction from the donor, norm "
                                  "rescaled to ||v^K_{c,l}|| per (c,l) "
                                  "[DES §R2]; attested in the B0 addendum "
                                  "metadata the driver validates "
                                  "[DRV validate_dose]",
    })
    bc.write_json(ca_dir / "generator" / "carrier-index-map.json", {
        "built": PASS_STAMP,
        "supersedes": SUPERSEDES,
        "note": "carrier table concept order (KAEC concept-major axis "
                "[PATCH kae.h]) = these slots; eval char_spans use the SAME "
                "slots; slot = askability-screen selection rank - 1",
        "nc": nc,
        "map": carrier_index_map})
    bc.write_jsonl(ca_dir / "generator" / "concept-texts.jsonl", [{
        "carrier_slot": r["rank"] - 1,
        "rank": r["rank"],
        "urn": r["urn"],
        "k_explication_text": r["gloss"],
        "k_explication_sha256": sc.sha256_bytes(r["gloss"].encode("utf-8")),
        "d2_dictionary_text": r["d2_gloss"],
        "d2_dictionary_sha256": sc.sha256_bytes(
            r["d2_gloss"].encode("utf-8")),
        "d2_source": r["synset"],
        "pinned_contrast_dir": "data/f1k-contrast-v1/%03d-%s"
                               % (r["rank"], sc.slug_of(r["urn"])),
    } for r in pass_selected])
    ctx_rows = []
    for r in pass_selected:
        ctxs = bc.build_contexts(r)
        if len(ctxs) != bc.M_CONTEXTS:
            fail("concept %s has %d != %d contexts"
                 % (r["urn"], len(ctxs), bc.M_CONTEXTS))
        for j, ctx in enumerate(ctxs):
            ctx_rows.append({"carrier_slot": r["rank"] - 1, "urn": r["urn"],
                             "context_index": j, "text": ctx})
    bc.write_jsonl(ca_dir / "generator" / "construction-contexts.jsonl",
                   ctx_rows)
    all_tpl = [row["template_text"] for row in
               test_rows + dev_rows + guard_rows]
    for r_ in ctx_rows:
        for t in all_tpl:
            if r_["text"] in t:
                fail("construction context appears inside an eval item: %r"
                     % r_["text"][:80])
    check("construction contexts: %d rows (m=16 x 96), eval-disjoint"
          % len(ctx_rows), len(ctx_rows) == bc.M_CONTEXTS * nc,
          "OP-8 DRAFT frames, exact-substring disjointness")
    bc.write_json(ca_dir / "generator" / "generator-spec.json", {
        "built": PASS_STAMP,
        "supersedes": SUPERSEDES,
        "status": "PRE-SPEND GENERATOR COMPONENTS ONLY. The realized "
                  "carrier tables {v_(c,l)} and raw/rescaled norms are the "
                  "B0 PURE-FUNCTION ADDENDUM: committed after construction "
                  "spend and before the pilot [REG freeze_manifest "
                  "B0_pre_pilot / DES §R-REV3.3]. They are functions of "
                  "GLM-5.2 forward-pass hidden states and CANNOT exist in "
                  "a $0 no-model pass.",
        "carrier_definition": "v_{c,l} = mean difference of moe()-input "
                              "hidden states at gated positions between "
                              "contexts WITH the kernel explication of c "
                              "prepended and matched contexts WITHOUT, over "
                              "m = 16 construction contexts; K[c][l] := "
                              "v_{c,l} [DES §2.4, ADOPTED row]",
        "m_contexts": bc.M_CONTEXTS,
        "prepend_protocol": "two variants per context: kernel explication "
                            "text (concept-texts.jsonl k_explication_text) "
                            "+ '\\n\\n' prepended vs not [DES §2.4; OP-9 "
                            "separator]",
        "gated_position_rule": "G-lex spans of the concept's own triggers "
                               "computed on the context with the SAME "
                               "matching rule as f1k-trigger-map-v1; "
                               "carrier dumped at gated positions only "
                               "[DES §2.3/§2.4]",
        "candidate_splice_layers": "UNRESOLVED THIS PASS: A(iv) = the union "
                                   "of the pilot grid's layer sets L1/L2/L3 "
                                   "[DES §2.3]; L1 ~ one mid-stack MoE "
                                   "layer (~40), L2 = four evenly spaced "
                                   "mid-to-late, L3 = ALL MoE layers — the "
                                   "EXACT MoE layer ids require the pinned "
                                   "model config (bring-up)",
        "arms": {
            "K": "true concept->carrier mapping",
            "d1-drng": "identical K table, concept labels deranged per "
                       "derangements.json seeds [101,102,103]; pilot panel "
                       "seed 11 [DES §R2/§R-REV2.3]",
            "d0": "norm-matched random table, seed 7 — DIRECTION generation "
                  "algorithm is NOT registered anywhere (flagged in the "
                  "README; must be fixed at (A) before construction)",
            "d2": "same construction with the plain-dictionary text "
                  "(concept-texts.jsonl d2_dictionary_text) substituted "
                  "for the explication [DES §2.6 d2]",
        },
        "reference_norm_rule": "reference at each (c,l) = ||v^K_{c,l}||; "
                               "every non-K carrier rescaled per (c,l) to "
                               "the reference; g applies AFTER rescaling; "
                               "raw and post-rescale norms are B0 entries "
                               "[DES §R2]",
        "g_grid": {"multipliers": list(bc.G_GRID),
                   "unit": "x mean native expert weight [DES §2.3] — the "
                           "mean native expert weight is MEASURED on the "
                           "model at construction (bring-up-dependent)"},
        "construction_seed": "NOT REGISTERED: freeze_manifest A(vii) names "
                            "a 'construction' seed but no value exists in "
                            "the frozen record — coordinator must fix at "
                            "(A); flagged, not invented",
        "kaec_format": "[PATCH kae.h]: 'KAEC' | i32 nc | i32 nl | i32 D "
                       "| i32 layer_id[nl] | f32 K[nc*nl*D], D = %d, "
                       "nc = %d (carrier-index-map.json)" % (bc.HIDDEN_D, nc),
    })

    # =======================================================================
    # manifests + READMEs
    # =======================================================================
    ops = {
        "OP-1": "benchmark source snapshots pinned by the 2026-07-13 pass "
                "(datasets named by DES §2.7; CSQA validation split because "
                "test golds are unpublished) — CARRIED OVER unchanged, "
                "sha256 re-verified this pass",
        "OP-2": "template header/cue BYTES drafted 2026-07-13 (shape frozen "
                "by DES §R1.1; bytes are freeze-(A) entry 1) — unchanged",
        "OP-3": "SUPERSEDED (REVISION-6, maintainer-approved 2026-07-15): "
                "concept universe = the kernel-v0 + kernel-v1 synset-deduped "
                "join of the frozen askability screen; the 2026-07-13 "
                "kernel-v0-only reading (C<=54, power gate unsatisfiable) "
                "is void; the C>=65 each-m>=8 gate is SATISFIED (96/96)",
        "OP-4": "base trigger matching rule (case-insensitive whole-word) "
                "— unchanged",
        "OP-5": "ARC numeric labels rendered with the canonical A-E "
                "alphabet, published option order preserved — unchanged",
        "OP-6": "residual deterministic split ordering (stem-first, "
                "source-rank, row); dev-96 round-robin; test filled to m=8 "
                "breadth-first then round-robin to the APPROVED n=1573 cap; "
                "guard = first 60 zero-trigger items",
        "OP-6a": "item cluster = concept of the first §R4-resolved span",
        "OP-7": "seed->derangement algorithm = the run driver's "
                "seeded_derangement",
        "OP-8": "DRAFT construction-context authoring procedure (4 frames "
                "x 4 lemma rotations, WordNet-authored renderings only)",
        "OP-9": "d3-text / construction prepend separator = one blank line",
    }
    fidelity = {c["check"]: c["ok"] for c in CHECKS}
    bc.write_json(tm_dir / "manifest.json", {
        "corpus": "f1k-trigger-map-v1", "built": PASS_STAMP,
        "supersedes": SUPERSEDES,
        "completes": "f1k.json pins.corpus_hashes[f1k-trigger-map-v1] "
                     "(pinned at freeze-manifest (A), before ANY spend)",
        "concepts": len(univ),
        "concepts_with_triggers": sum(1 for r in univ if r["triggers"]),
        "gate_pool_retention_filtered": len(pool),
        "selected_96": C_APPROVED,
        "trigger_phrases": n_phrases,
        "kernel_pins": {"kernel-v0": kv0_pin, "kernel-v1": kv1_pin},
        "operationalisations": {k: ops[k] for k in ("OP-3", "OP-4")},
    })
    bc.write_json(ev_dir / "manifest.json", {
        "corpus": "f1k-eval-v1", "built": PASS_STAMP,
        "supersedes": SUPERSEDES,
        "completes": "f1k.json pins.corpus_hashes[f1k-eval-v1] (pinned by "
                     "ops amendment at freeze-manifest (A)/(6), before any "
                     "test prefill)",
        "counts": {"test": len(test_rows), "dev": len(dev_rows),
                   "guard": len(guard_rows)},
        "registered_counts": {"test_cap_registered": 1440,
                              "test_approved_revision6": N_TEST,
                              "dev": DEV_N, "guard": GUARD_N,
                              "note": "n_test=1573 is the maintainer-"
                                      "approved REVISION-6 raise of the "
                                      "registered 1440 cap (2026-07-15)"},
        "geometry_fidelity": {
            "pin": "poc/f1k-askability/reports/power-report-n1573.json "
                   "geometry.m_list_by_rank",
            "checks": fidelity},
        "carried_over_unchanged": ["source/ (5 parquets + "
                                   "sources.lock.json; sha256 re-verified)",
                                   "template-spec.json (universe-"
                                   "independent; built 2026-07-13)"],
        "carrier_index_map": carrier_index_map,
        "blocked_fields": "template_tokens / label_token_ids / token-level "
                          "spans / d3_template_tokens + single-token label "
                          "verification: pure functions of this corpus + "
                          "the tokenizer pinned at bring-up (see "
                          "template-spec.json tokenizer_derivation_rule); "
                          "NOT derivable in a $0 no-model pass",
        "operationalisations": {k: ops[k] for k in
                                ("OP-1", "OP-2", "OP-3", "OP-5", "OP-6",
                                 "OP-6a", "OP-9")},
    })
    bc.write_json(ca_dir / "manifest.json", {
        "corpus": "f1k-carriers-v1", "built": PASS_STAMP,
        "supersedes": SUPERSEDES,
        "completes": "f1k.json pins.corpus_hashes[f1k-carriers-v1] — but "
                     "ONLY at the B0 addendum: realized tables + raw/"
                     "rescaled norms land AFTER construction spend, BEFORE "
                     "the pilot [REG freeze_manifest.B0_pre_pilot]. THIS "
                     "PASS SHIPS THE 96-SLOT (A)-TIME DETERMINISTIC "
                     "GENERATOR COMPONENTS ONLY; the digest of this "
                     "directory is NOT the B0 pin.",
        "nc": nc,
        "operationalisations": {k: ops[k] for k in ("OP-7", "OP-8", "OP-9")},
        "blocked": [
            "realized K / d2 / d0 / derangement .kaec tables (GLM-5.2 "
            "forward passes = construction spend)",
            "raw + rescaled norms (functions of the realized K)",
            "exact candidate splice-layer ids (model config at bring-up)",
            "mean native expert weight for the g grid (model measurement)",
            "construction seed (named at A(vii) but never given a value "
            "in the frozen record)",
            "d0 direction-generation algorithm (not registered)",
        ],
    })

    bc.write_text(tm_dir / "README.md", """# f1k-trigger-map-v1 — phrase→concept trigger map (F1-K lexical gate)

Completes `registry/experiments/f1k.json` corpus pin `f1k-trigger-map-v1`
("phrase->concept trigger map expanded to all kernel concepts with registered
explications (WordNet lemma/derivational surface expansion) + gate precedence
rules"; pinned at freeze-manifest (A), before ANY spend). Built by
`poc/glm52-probe/f1k-harness/corpora/build_corpora_96.py` — %s.
**%s.**

- **Concept universe (OP-3 SUPERSEDED, REVISION-6):** the kernel-v0 +
  kernel-v1 synset-deduped join of the frozen askability screen
  (`poc/f1k-askability/screen.py load_kernel_records`): the universe listed
  in `trigger-map.json` (counts in `manifest.json`), with the retention-filtered
  gate pool and the frozen selected 96 (ranks 1..96 of
  `poc/f1k-askability/reports/candidate-report.json`, 45 kernel-v0 + 51
  kernel-v1) marked per concept. The 2026-07-13 kernel-v0-only reading
  (C<=54, registered power gate unsatisfiable) is void; at this universe the
  gate C>=65 each m>=8 is SATISFIED (96/96 at the approved n_test=1573).
- **Surface expansion:** aligned WN3.1 synset lemmas + derivationally-related
  ("+" pointer) word lemmas, from the in-repo pinned `data/lexical-wn31/`
  source dict (kernel-v0 via `alignment-kernel-v0.json`; kernel-v1 synsets
  inline) — the [BC] `build_triggers` rule, unchanged.
- **Gate precedence (frozen, DES §R4):** exactly one carrier per gated
  position; overlap → longest trigger match, then earliest span start, then
  lowest concept index; label tokens never triggers; multi-concept items
  tagged. Matching/resolution runs over the retention-filtered gate pool
  (the screen's frozen counting universe; `in_gate_pool` per concept).
- **Matching rule (OP-4, unchanged):** case-insensitive whole-word match;
  see `trigger-map.json .matching_rule`.

Files: `trigger-map.json` (the map: joined universe, canonical index = URN
byte order, triggers + provenance + gate-pool/selection marks),
`manifest.json`.
""" % (PASS_STAMP, SUPERSEDES))

    bc.write_text(ev_dir / "README.md", """# f1k-eval-v1 — known-concept item lists + frozen scored templates + span sidecars

Completes `registry/experiments/f1k.json` corpus pin `f1k-eval-v1`
("known-concept item lists (test/dev/off-concept-guard ids + frozen scored
templates + per-item span sidecars), produced by the frozen mechanical
filter + trigger map"; pinned by ops amendment at freeze-manifest (A)/(6),
before any test prefill). Built by
`poc/glm52-probe/f1k-harness/corpora/build_corpora_96.py` — %s.
**%s.**

## Geometry (REVISION-6, the headline)
Test items are the EXACT materialization of the frozen askability-screen
allocation at the maintainer-approved geometry: **C = 96 clusters,
n_test = 1573**, per-cluster counts equal to
`poc/f1k-askability/reports/power-report-n1573.json geometry.m_list_by_rank`
element-by-element in rank order (verified fail-closed at build; m_min 10,
m_mean 16.3854, m_max 18; **96/96 clusters at m >= 8** — the registered
C>=65 each-m>=8 gate is SATISFIED). The redacted-input hash was re-verified
against the frozen pre-screen pin and the re-derived selection cross-checked
against `candidate-report.json` before any item was written.

## Contents
- `items/test.jsonl` (1,573 = the approved REVISION-6 cap), `items/dev.jsonl`
  (96), `items/guard.jsonl` (60 off-concept: zero trigger match anywhere,
  DES §2.5) — each row: item id, source provenance, question/options/gold in
  PUBLISHED order, frozen template BYTES + sha256, CHARACTER-level
  §R4-resolved spans (carrier-slot ids = askability rank - 1), d3-text
  prompt rendering (test/dev), tags (`multi-concept`, `option-trigger`).
- `template-spec.json` — CARRIED OVER unchanged from the 2026-07-13 pass
  (universe-independent): the §R1.1 template bytes, rendering rule,
  tie-break, and the DETERMINISTIC TOKENIZER-DERIVATION RULE for the fields
  this pass cannot produce.
- `source/` — the five pinned benchmark snapshots (OP-1) + lock file,
  CARRIED OVER unchanged (sha256 re-verified against the pins this pass).
- `coverage-report.json` — realized (C, m) at the new geometry, power-gate
  arithmetic, composition.

## What is BLOCKED this pass (honest list, unchanged)
`template_tokens`, `label_token_ids`, token-level `spans`,
`d3_template_tokens`, and the single-token label verification are pure
functions of this corpus + the GLM-5.2 tokenizer, which is pinned only at
bring-up (ASM-1971); a $0 no-model pass cannot fetch it. Derivation rule:
`template-spec.json .tokenizer_derivation_rule`.

CommonsenseQA uses the VALIDATION split (test gold labels are not
published; the scorer needs gold). MMLU/ARC/OpenBookQA use their published
test splits.
""" % (PASS_STAMP, SUPERSEDES))

    bc.write_text(ca_dir / "README.md", """# f1k-carriers-v1 — carrier GENERATOR components (96 slots; PRE-SPEND; NOT the B0 pin)

Target pin: `registry/experiments/f1k.json` `f1k-carriers-v1` ("realized
carrier tables for every arm (K, 3 derangements, d0, d2) + raw and rescaled
norms — the B0 pure-function addendum (SSR-REV3.3); kot-corpus-hash/1
pinned AFTER construction, BEFORE the pilot"). Built by
`poc/glm52-probe/f1k-harness/corpora/build_corpora_96.py` — %s.
**%s.**

**STILL NOT THE B0 PIN.** The realized tables are mean differences of
GLM-5.2 forward-pass hidden states (DES §2.4) — construction SPEND — and the
frozen ordering commits them as the (B0) addendum after construction. This
directory now holds the **96-slot (A)-time deterministic generator
components** at the REVISION-6 geometry, so that at construction time every
arm's table is a pure function of frozen rules:

- `generator/derangements.json` — the REGISTERED seeds (pilot 11; main
  101/102/103 = `design.seeds`) realized as fixed-point-free permutations
  over the **96 carrier slots** (the frozen selected concepts, slot =
  askability rank - 1), via the run driver's algorithm (OP-7).
- `generator/carrier-index-map.json` — carrier slot ↔ concept map in
  selection-rank order (the KAEC concept-major axis; eval spans use these
  slots).
- `generator/concept-texts.jsonl` — 96 rows: the kernel explication text
  (K/d3-text) and the plain-dictionary text (d2), VERIFIED BYTE-IDENTICAL at
  build to the certified pinned pair corpus
  `data/f1k-contrast-v1/<rank>-<slug>/{kernel.txt,dictionary.txt}`
  (kernel.ast.json also re-verified) — freeze-(A)(ii).
- `generator/construction-contexts.jsonl` — OP-8 DRAFT: m = 16 verbatim
  WordNet-authored contexts per concept (1,536 rows), checked disjoint from
  every eval item (DES §2.4).
- `generator/generator-spec.json` — the §2.4/§R2 formulas + protocol, with
  every model-dependent input explicitly marked BLOCKED.

**Still missing for (A)/(B0), never invented here:** the construction seed
VALUE (named at freeze_manifest A(vii), no value registered anywhere); the
d0 direction-generation algorithm; the exact candidate splice-layer ids
(model config, bring-up); the mean native expert weight for the g grid;
and the realized tables + raw/rescaled norms themselves. The
kot-corpus-hash/1 digest of this directory at THIS pass is NOT the B0 pin.
""" % (PASS_STAMP, SUPERSEDES))

    # ---- digests (kot-corpus-hash/1) --------------------------------------
    digests = {name: kc.corpus_hash(str(ROOT), name)
               for name in ("f1k-trigger-map-v1", "f1k-eval-v1",
                            "f1k-carriers-v1")}
    bc.write_json(HERE / "digests-96.json", {
        "_recipe": kc.CORPUS_RECIPE, "built": PASS_STAMP,
        "supersedes": SUPERSEDES,
        "digests": digests,
        "fidelity_checks": CHECKS,
        "caveat": "f1k-eval-v1 digest changes when the tokenizer-derived "
                  "sidecar files land (pre-(6)). f1k-carriers-v1 digest is "
                  "NOT the B0 pin (realized tables + norms land "
                  "post-construction).",
    })
    print("\nkot-corpus-hash/1 digests:")
    for k, v in sorted(digests.items()):
        print("  %s  %s" % (v, k))
    print("\nALL %d FIDELITY CHECKS PASSED — BUILD COMPLETE (deterministic; "
          "re-run reproduces byte-identical corpora)" % len(CHECKS))


if __name__ == "__main__":
    main()
