#!/usr/bin/env python3
"""selftest.py — validate the LOCAL atlas pipeline ($0, no Modal) before spend.

Generates a synthetic kot-rtrace/1 trace over the real 480-item corpus with
KNOWN injected specialists, then runs atlas_agg.py + build_atlas.py and asserts
the atlas recovers them and computes the coverage gates. This is the mock/dry
check that de-risks the in-container aggregation math and the whole local flow.
"""
from __future__ import annotations
import hashlib, json, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus" / "wave_a_corpus.json"
MANIFEST = HERE / "corpus" / "corpus_manifest.json"
LEDGER = HERE.parent / "expert_ledger.csv"

# synthetic layers (subset; real run has 3..77) and injected specialists
LAYERS = [3, 4, 5, 6, 7]
TOPK = 8
NEXP = 256

# injected specialists: (layer, expert) -> (predicate on item-labels, boost)
def is_math(m):     return m["semantic_domain"] == "math"
def is_format(m):   return m["semantic_domain"] in ("structured", "tool_schema")
def is_copy(m):     return m["semantic_domain"] == "copy"
def is_arith(m):    return m["operation"] == "arithmetic"
def is_zh(m):       return m["language"] == "zh"

SPECIALISTS = {
    (3, 100): (is_math, 3.0),     # math domain specialist (fires broadly, enriched math)
    (4, 101): (is_math, 3.0),
    (3, 50):  (is_format, 3.0),   # structured/schema format specialist
    (5, 51):  (is_format, 3.0),
    (3, 200): (is_copy, 3.5),     # copy specialist
    (4, 77):  (is_arith, 3.0),    # arithmetic-operation specialist
    (6, 33):  (is_zh, 3.0),       # chinese-language specialist
}
RARE_EXPERT = (7, 250)            # deliberately fires seldom -> must end up "rare"/"unseen"


def h(*xs):
    return int(hashlib.sha256("|".join(map(str, xs)).encode()).hexdigest(), 16)


def fnv_word(pos, layer, rank, e):
    return (((pos & 0xffffffff) << 40) ^ ((layer & 0xffffffff) << 24)
            ^ ((rank & 0xffffffff) << 16) ^ (e & 0xffffffff)) & ((1 << 64)-1)


def gen_trace(corpus, out_path):
    FNV_OFF = 1469598103934665603; FNV_P = 1099511628211; MASK = (1 << 64)-1
    probes = corpus["probes"]
    rep_off = corpus.get("repeat_id_offset", 10000)
    rep_ids = set(corpus.get("repeat_probe_ids", []))
    with open(out_path, "w") as f:
        f.write('{"t":"hdr","schema":"kot-rtrace/1","n_layers":78,'
                '"fields":["item","tok","io","site","layer","rank","e","raw","gate","sel","w","mgn"]}\n')
        emit_items = list(probes)
        # append repeat duplicates (byte-identical decisions) for two items
        for rid in rep_ids:
            src = next(p for p in probes if p["id"] == rid)
            dup = dict(src); dup["id"] = rid + rep_off
            emit_items.append(dup)
        for it in emit_items:
            m = it
            T = len(it["tiny_ids"]); npr = it["tiny_n_prompt"]
            # compact (no spaces) to mirror the engine's rtrace.h output exactly
            f.write('{"t":"begin","item":%d,"T":%d,"n_prompt":%d,"topk":%d,"draft":0}\n'
                    % (it["id"], T, npr, TOPK))
            dh = FNV_OFF; rows = 0
            for tok in range(T):
                io = 1 if tok >= npr else 0
                for layer in LAYERS:
                    # score every expert; static per-expert popularity (long tail,
                    # like real routing) + pseudo-random jitter + domain boosts
                    scores = []
                    for e in range(NEXP):
                        pop = (h(layer, e) % 1000) / 1000.0            # static popularity
                        s = 0.8*pop + 0.4*((h(it["id"], tok, layer, e) % 100000)/100000.0)
                        pred = SPECIALISTS.get((layer, e))
                        if pred and pred[0](m):
                            s += pred[1]
                        scores.append((s, e))
                    scores.sort(reverse=True)
                    topk = scores[:TOPK]
                    ninth = scores[TOPK][0]
                    ssum = sum(max(1e-6, s) for s, _ in topk)
                    for rank, (s, e) in enumerate(topk):
                        gate = 1.0/(1.0+pow(2.718281828, -s))
                        w = max(1e-6, s)/ssum
                        mgn = topk[-1][0] - ninth
                        f.write('{"t":"r","item":%d,"tok":%d,"io":%d,"site":"main","layer":%d,'
                                '"rank":%d,"e":%d,"raw":%.4f,"gate":%.5f,"sel":%.5f,"w":%.5f,"mgn":%.5f}\n'
                                % (it["id"], tok, io, layer, rank, e, s-1.0, gate, gate, w, mgn))
                        dh ^= 0
                        vv = fnv_word(tok, layer, rank, e)
                        for _ in range(8):
                            dh ^= (vv & 0xff); dh = (dh*FNV_P) & MASK; vv >>= 8
                        rows += 1
            f.write('{"t":"end","item":%d,"rows":%d,"decident_fnv1a64":"%016x"}\n'
                    % (it["id"], rows, dh))


def main():
    corpus = json.loads(CORPUS.read_text())
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        trace = td / "rtrace.jsonl"
        agg = td / "agg.json"
        outd = td / "atlas"
        print("[selftest] generating synthetic trace ...")
        gen_trace(corpus, trace)
        print(f"[selftest] trace size = {trace.stat().st_size/1e6:.1f} MB")
        print("[selftest] running atlas_agg ...")
        subprocess.run([sys.executable, str(HERE/"atlas_agg.py"),
                        "--trace", str(trace), "--corpus", str(CORPUS),
                        "--out", str(agg)], check=True)
        print("[selftest] running build_atlas ...")
        subprocess.run([sys.executable, str(HERE/"build_atlas.py"),
                        "--agg", str(agg), "--corpus", str(CORPUS),
                        "--corpus-manifest", str(MANIFEST), "--ledger", str(LEDGER),
                        "--out-dir", str(outd)], check=True)
        # ---- assertions ----
        import pyarrow.parquet as pq
        t = pq.read_table(str(outd/"expert_atlas.parquet")).to_pylist()
        by_cell = {(r["execution_site"], r["layer"], r["expert_id"]): r for r in t}
        assert len(t) == 19200, f"expected 19200 enumerated cells, got {len(t)}"
        print(f"[selftest] enumerated cells: {len(t)}")

        def chk(cell, dom=None, dom_in=None, kind=None, labelled=False):
            r = by_cell[cell]
            print(f"  cell {cell}: class={r['label_class']} dom={r['primary_domain']} "
                  f"enr={r['primary_domain_enr_log2']} cand={r['candidate_kind']} "
                  f"ev={r['events_total']} fam={r['n_families']} repro={r['bootstrap_reproducibility']}")
            if dom:
                assert r["primary_domain"] == dom, f"{cell}: expected domain {dom}, got {r['primary_domain']}"
            if dom_in:
                assert r["primary_domain"] in dom_in, f"{cell}: expected domain in {dom_in}, got {r['primary_domain']}"
            if kind:
                assert r["candidate_kind"] == kind, f"{cell}: expected kind {kind}, got {r['candidate_kind']}"
            if labelled:
                assert r["label_class"] in ("stable", "polysemantic"), f"{cell}: expected labelled, got {r['label_class']}"
            return r

        print("[selftest] injected-specialist recovery:")
        chk(("main",3,100), dom="math", kind="arithmetic", labelled=True)   # single-domain -> stable
        assert by_cell[("main",3,100)]["label_class"] == "stable"
        chk(("main",4,101), dom="math", labelled=True)
        # (3,50) boosted for BOTH structured+tool_schema -> honestly polysemantic across them
        chk(("main",3,50), dom_in=("structured","tool_schema"), kind="format", labelled=True)
        chk(("main",3,200), dom="copy", kind="copy", labelled=True)
        assert by_cell[("main",3,200)]["label_class"] == "stable"           # copy is single-domain
        chk(("main",4,77), kind="arithmetic", labelled=True)                # arithmetic-op enrichment
        chk(("main",6,33))  # zh specialist -> language enrichment (multiling domain)
        # an unseen cell (layer never present in the synthetic trace)
        r_unseen = by_cell[("main",40,10)]
        assert r_unseen["label_class"] == "unseen", r_unseen["label_class"]

        gates = json.loads((outd/"coverage_gates.json").read_text())
        counts = gates["label_class_counts"]
        print("[selftest] label-class census:", json.dumps(counts))
        print("[selftest] gates:", json.dumps({k:v for k,v in gates.items()
              if k not in ("trace_invariants_source","label_class_counts")}, indent=1))
        assert gates["n_stable_labels"] >= 4, gates["n_stable_labels"]
        # honesty machinery: multiple label branches must be reachable
        assert counts.get("unseen", 0) > 0, "no unseen cells enumerated"
        assert counts.get("generalist", 0) > 0, "no generalist cells (enr~0 branch)"
        assert (counts.get("rare", 0) + counts.get("unresolved", 0)) > 0, "no rare/unresolved cells"
        assert gates["discovery_heldout_spearman_median"] is not None
        print("\n[selftest] PASS — atlas recovers injected specialists, enumerates all "
              "19,200 cells, and exercises stable/generalist/rare/unseen honestly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
