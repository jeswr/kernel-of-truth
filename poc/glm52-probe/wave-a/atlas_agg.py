#!/usr/bin/env python3
"""atlas_agg.py — one-pass streaming aggregation of a kot-rtrace/1 trace into the
compact per-expert-cell sufficient statistics the Stage-2 atlas needs.

Pure stdlib. Runs BOTH in the Modal container (cheap cross-check + report) and
locally on the downloaded raw trace (authoritative). Deterministic.

The atlas matrix M_{e,d} (plan §"Activation matrix") is
   M_{e,d} = sum_{t in d} 1[e in TopK(t)] w_e(t)  /  sum_{t in d} sum_j w_j(t)
i.e. expert e's share of domain d's total routed weight AT e's layer. To support
that plus layer-normalised log-enrichment, per-(language/operation/format/io)
conditional matrices, and family-bootstrap CIs, we accumulate weight+event mass
keyed by (cell) x (template_family, is_counterpart) — a "subfamily" whose
(domain, operation, language, surface_format, answer_type, split) are all fixed —
and the matching per-(layer) subfamily totals (the denominators).

Reads item->subfamily from the corpus; SKIPS repeat items (id >= repeat_offset,
the determinism-check duplicates) so nothing is double-counted.

Emits agg JSON:
  meta   : schema, n_rows, n_items, topk_seen, layers_seen, repeat_offset, ...
  cells  : { "site|layer|e": {tot:[ev,ws,gate_sum,mgn_sum], rank:[c0..c7],
             io:[ev0,ws0,ev1,ws1], sf:{ "fam#iscp":[ev,ws] }, top:[[item,tok,gate]..] } }
  layers : { "site|layer": {tot:[ev,ws], sf:{ "fam#iscp":[ev,ws] }, n_tok:int } }
"""
from __future__ import annotations
import argparse, gzip, json, sys
from collections import defaultdict
from pathlib import Path

TOP_RESERVOIR = 6          # activation-max contexts kept per cell (Stage-3 seed)


def _open(path):
    return gzip.open(path, "rt") if str(path).endswith(".gz") else open(path, "r")


def load_item_map(corpus_path):
    corpus = json.loads(Path(corpus_path).read_text())
    repeat_offset = corpus.get("repeat_id_offset", 10000)
    imap = {}
    for it in corpus["probes"]:
        imap[it["id"]] = {
            "fam": it["prompt_family"],     # 240 prompt families = gate/bootstrap unit
            "iscp": 1 if it["is_counterpart"] else 0,
        }
    return imap, repeat_offset, corpus


def aggregate(trace_path, corpus_path, out_path):
    imap, repeat_offset, _ = load_item_map(corpus_path)
    cells = {}
    layers = {}
    n_rows = 0
    items_ended = set()
    topk_seen = set()
    layers_seen = set()
    skipped_items = set()
    cur_item = None
    cur_skip = False
    cur_fam_key = None
    layer_tokens = defaultdict(set)   # (site,layer) -> set of (item,tok) for n_tok

    with _open(trace_path) as f:
        for ln in f:
            if not ln:
                continue
            # fast line-type dispatch, tolerant of optional whitespace after the
            # colon (the engine emits compact `"t":"r"` but stay robust).
            ti = ln.find('"t":')
            if ti < 0:
                continue
            j = ti + 4
            while j < len(ln) and ln[j] in ' "':
                j += 1
            tv = ln[j:j+3]
            if tv.startswith("beg"):
                o = json.loads(ln)
                cur_item = o["item"]
                cur_skip = cur_item >= repeat_offset or cur_item not in imap
                if cur_skip:
                    skipped_items.add(cur_item)
                    cur_fam_key = None
                else:
                    m = imap[cur_item]
                    cur_fam_key = f"{m['fam']}#{m['iscp']}"
                continue
            if tv.startswith("end"):
                o = json.loads(ln)
                if o["item"] < repeat_offset and o["item"] in imap:
                    items_ended.add(o["item"])
                cur_item = None
                cur_skip = False
                cur_fam_key = None
                continue
            if not tv.startswith("r"):
                continue
            # route row
            if cur_skip or cur_fam_key is None:
                continue
            o = json.loads(ln)
            n_rows += 1
            site = o["site"]; layer = o["layer"]; e = o["e"]; rank = o["rank"]
            w = o["w"]; gate = o["gate"]; mgn = o["mgn"]; io = o["io"]; tok = o["tok"]
            topk_seen.add(rank)
            layers_seen.add(layer)
            ckey = f"{site}|{layer}|{e}"
            lkey = f"{site}|{layer}"
            c = cells.get(ckey)
            if c is None:
                c = {"tot": [0, 0.0, 0.0, 0.0], "rank": [0]*8,
                     "io": [0, 0.0, 0, 0.0], "sf": {}, "top": []}
                cells[ckey] = c
            c["tot"][0] += 1; c["tot"][1] += w; c["tot"][2] += gate; c["tot"][3] += mgn
            if 0 <= rank < 8:
                c["rank"][rank] += 1
            base = 0 if io == 0 else 2
            c["io"][base] += 1; c["io"][base+1] += w
            sf = c["sf"].get(cur_fam_key)
            if sf is None:
                sf = [0, 0.0]; c["sf"][cur_fam_key] = sf
            sf[0] += 1; sf[1] += w
            # activation-max reservoir (keep top by gate)
            top = c["top"]
            if len(top) < TOP_RESERVOIR:
                top.append([cur_item, tok, round(gate, 5)])
                if len(top) == TOP_RESERVOIR:
                    top.sort(key=lambda x: x[2])
            elif gate > top[0][2]:
                top[0] = [cur_item, tok, round(gate, 5)]
                top.sort(key=lambda x: x[2])
            # layer totals
            L = layers.get(lkey)
            if L is None:
                L = {"tot": [0, 0.0], "sf": {}}
                layers[lkey] = L
            L["tot"][0] += 1; L["tot"][1] += w
            lsf = L["sf"].get(cur_fam_key)
            if lsf is None:
                lsf = [0, 0.0]; L["sf"][cur_fam_key] = lsf
            lsf[0] += 1; lsf[1] += w
            layer_tokens[lkey].add((cur_item, tok))

    for lkey, L in layers.items():
        L["n_tok"] = len(layer_tokens[lkey])

    # round floats for compactness
    def rnd(x):
        return round(x, 6)
    for c in cells.values():
        c["tot"] = [c["tot"][0], rnd(c["tot"][1]), rnd(c["tot"][2]), rnd(c["tot"][3])]
        c["io"] = [c["io"][0], rnd(c["io"][1]), c["io"][2], rnd(c["io"][3])]
        c["sf"] = {k: [v[0], rnd(v[1])] for k, v in c["sf"].items()}
    for L in layers.values():
        L["tot"] = [L["tot"][0], rnd(L["tot"][1])]
        L["sf"] = {k: [v[0], rnd(v[1])] for k, v in L["sf"].items()}

    agg = {
        "meta": {
            "schema": "kot-atlas-agg/1",
            "trace": str(trace_path),
            "n_rows": n_rows,
            "n_items_ended": len(items_ended),
            "n_cells_active": len(cells),
            "n_layers_active": len(layers),
            "topk_seen": sorted(topk_seen),
            "layers_seen": sorted(layers_seen),
            "repeat_offset": repeat_offset,
            "n_repeat_items_skipped": len(skipped_items),
        },
        "cells": cells,
        "layers": layers,
    }
    out_path = str(out_path)
    if out_path.endswith(".gz"):
        with gzip.open(out_path, "wt") as f:
            json.dump(agg, f)
    else:
        Path(out_path).write_text(json.dumps(agg))
    return agg["meta"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trace", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    meta = aggregate(a.trace, a.corpus, a.out)
    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
