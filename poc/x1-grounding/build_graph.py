#!/usr/bin/env python3
"""
X1-grounding stage 1 (PREREG §2, §3): parse synset JSONL + Morphy-lite ->
directed definition graph. Emits graph.json.gz + graph-stats.json.

Orientation (PREREG §3): u -> w means "u is used in a definition of w".
No prime information is read or written here (no-peeking, PREREG §7).
"""
import argparse
import gzip
import json
import os
import sys
import time
from collections import Counter, defaultdict

import x1g_lib as L


def iter_synsets(pos_files, noun_limit=None):
    for pos, path in pos_files.items():
        if not os.path.exists(path):
            raise SystemExit(f"{L.ERR_SOURCE_MISSING}: {path}")
        limit = noun_limit if pos == "noun" else None
        with open(path, encoding="utf-8") as f:
            for i, line in enumerate(f):
                if limit is not None and i >= limit:
                    break
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                yield pos, rec


def build(noun_limit=None, pos_subset=None):
    t0 = time.time()
    per_pos, union = L.load_index()
    exc = L.load_exc()
    morphy = L.Morphy(per_pos, union, exc)

    # Node set V = index lemmas, lowercased, POS-collapsed (PREREG §3).
    nodes = sorted(union)
    node_id = {lem: i for i, lem in enumerate(nodes)}
    n = len(nodes)
    single_word = [("_" not in lem) for lem in nodes]

    out_sets = defaultdict(set)          # u -> set(w)
    usage = [0] * n                      # PREREG §3 sensitivity covariate
    senses_per_node = Counter()          # #synsets defining each node (for T4)

    self_ref_count = 0
    oov_token_count = 0
    oov_counter = Counter()
    empty_gloss_count = 0
    empty_defset_count = 0
    lemma_not_in_vocab = 0
    synset_count = 0

    pos_files = L.SYNSET_FILES if pos_subset is None else {
        p: L.SYNSET_FILES[p] for p in pos_subset}

    for pos, rec in iter_synsets(pos_files, noun_limit=noun_limit):
        synset_count += 1
        ann = rec.get("annotations", {})
        gloss = ann.get("gloss", "") or ""
        lemmas = ann.get("lemmas", []) or []
        # L(s): synset lemma nodes, lowercased.
        Ls_ids = set()
        for lem in lemmas:
            low = lem.lower()
            wid = node_id.get(low)
            if wid is None:
                lemma_not_in_vocab += 1
                continue
            Ls_ids.add(wid)
            senses_per_node[wid] += 1

        cleaned = L.clean_gloss(gloss)
        if not cleaned.strip():
            empty_gloss_count += 1
        # D(s): resolved gloss lemma-node ids.
        Ds_ids = set()
        for tok in L.tokenize(cleaned):
            resolved = morphy.resolve_token(tok)
            if not resolved:
                oov_token_count += 1
                oov_counter[tok] += 1
                continue
            for lem in resolved:
                rid = node_id.get(lem)
                if rid is not None:
                    Ds_ids.add(rid)
        # D'(s) = D(s) \ L(s)  (remove self-reference, PREREG §3).
        self_ids = Ds_ids & Ls_ids
        self_ref_count += len(self_ids)
        Dp_ids = Ds_ids - Ls_ids
        if not Dp_ids:
            empty_defset_count += 1
        # Edges u -> w for u in D'(s), w in L(s).
        for u in Dp_ids:
            usage[u] += 1
            ou = out_sets[u]
            for w in Ls_ids:
                ou.add(w)

    # Materialise adjacency (sorted for determinism).
    out_adj = [[] for _ in range(n)]
    in_deg = [0] * n
    edge_count = 0
    for u, ws in out_sets.items():
        lst = sorted(ws)
        out_adj[u] = lst
        edge_count += len(lst)
        for w in lst:
            in_deg[w] += 1
    out_deg = [len(out_adj[v]) for v in range(n)]

    n_sw = sum(1 for v in range(n) if single_word[v])
    undefined_nodes = sum(1 for v in range(n) if in_deg[v] == 0)

    senses_dist = Counter(senses_per_node.values())

    stats = {
        "schema": "x1g-graph-stats/1",
        "builtAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sliceNounLimit": noun_limit,
        "posSubset": sorted(pos_files.keys()),
        "synsetCount": synset_count,
        "V": n,
        "V_sw": n_sw,
        "edgeCount": edge_count,
        "selfRefCount": self_ref_count,
        "emptyGlossCount": empty_gloss_count,
        "emptyDefSetCount": empty_defset_count,
        "oovTokenCount": oov_token_count,
        "undefinedNodeCount": undefined_nodes,
        "lemmaNotInVocabCount": lemma_not_in_vocab,
        "distinctOovTypes": len(oov_counter),
        "oovTop100": [[t, c] for t, c in oov_counter.most_common(100)],
        "sensesPerNodeDist": {str(k): v for k, v in sorted(senses_dist.items())},
        "buildSeconds": round(time.time() - t0, 2),
    }
    graph = {
        "schema": "x1g-graph/1",
        "nodes": nodes,
        "single_word": [1 if s else 0 for s in single_word],
        "out": out_adj,
        "outdeg": out_deg,
        "indeg": in_deg,
        "usage": usage,
    }
    return graph, stats


def input_shas():
    shas = {}
    for pos, path in L.SYNSET_FILES.items():
        shas["synsets-%s.jsonl" % pos] = L.sha256_file(path)
    for pos, path in L.INDEX_FILES.items():
        shas["index.%s" % pos] = L.sha256_file(path)
    for pos, path in L.EXC_FILES.items():
        shas["%s.exc" % pos] = L.sha256_file(path)
    return shas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=L.HERE)
    ap.add_argument("--noun-limit", type=int, default=None)
    ap.add_argument("--pos", default=None, help="comma list, e.g. 'noun' for slice")
    ap.add_argument("--graph-name", default="graph.json.gz")
    ap.add_argument("--stats-name", default="graph-stats.json")
    ap.add_argument("--no-sha", action="store_true")
    args = ap.parse_args()

    pos_subset = args.pos.split(",") if args.pos else None
    graph, stats = build(noun_limit=args.noun_limit, pos_subset=pos_subset)
    stats["inputsSha256"] = {} if args.no_sha else input_shas()
    graph["inputsSha256"] = stats["inputsSha256"]

    gpath = os.path.join(args.out_dir, args.graph_name)
    with gzip.open(gpath, "wt") as f:
        f.write(json.dumps(graph, sort_keys=True, separators=(",", ":")))
        f.write("\n")
    L.dump_json_pretty(stats, os.path.join(args.out_dir, args.stats_name))
    print("build_graph: V=%d V_sw=%d edges=%d kernel-input synsets=%d (%.1fs)" % (
        stats["V"], stats["V_sw"], stats["edgeCount"], stats["synsetCount"],
        stats["buildSeconds"]), file=sys.stderr)


if __name__ == "__main__":
    main()
