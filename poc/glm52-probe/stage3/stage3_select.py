#!/usr/bin/env python3
"""stage3_select.py — pick the ~32-expert stratified causal shortlist and build
the Stage-3 ablation item pool, from the Stage-2 atlas ONLY ($0 local work).

Reads:  wave-a/atlas/expert_atlas.parquet  (labels, candidate_kind, activation-max
        contexts, per-domain routing mass) + wave-a/corpus/wave_a_corpus.json.
Writes: stage3/corpus/stage3_shortlist.json   (cells + strata + per-cell items + swap)
        stage3/corpus/stage3_corpus.json       (the referenced wave-A items, with text)

Strata (docs/next/design/glm52-expert-profiling-plan-sol-20260715.md §Stage-3 two-
tier design): the format/copy/arithmetic deterministic-replacement leads, the top
science/legal_fin/multiling domain specialists, apparent generalists, and negative
controls (rare/low-load + a random mid-load non-specialist).  Each cell gets its
activation-max on-domain items (top_contexts + label-matched) and MATCHED off-domain
controls (domains it routes ~zero mass to).  Replacement leads also get a generic
same-layer substitute expert (swap target) for the cheap module-swap arm.
EXPLORATORY infra — rigor relaxed vs a frozen experiment.
"""
import json, random
from pathlib import Path
import pyarrow.parquet as pq

HERE = Path(__file__).resolve().parent
WAVE = HERE.parent / "wave-a"
SEED = 20260715
N_ON, N_OFF = 10, 8          # activation-max on-domain + matched off-domain per expert
N_SWAP_ON = 10               # on-domain items given the module-swap arm (leads only)

random.seed(SEED)

# ---- load atlas ----
t = pq.read_table(WAVE / "atlas" / "expert_atlas.parquet")
cols = t.column_names
A = {c: t.column(c).to_pylist() for c in cols}
N = t.num_rows
def row(i): return {c: A[c][i] for c in cols}
def key(i): return f"{A['execution_site'][i]}|{A['layer'][i]}|{A['expert_id'][i]}"
idx_by_key = {key(i): i for i in range(N)}

# ---- load corpus ----
corpus = json.loads((WAVE / "corpus" / "wave_a_corpus.json").read_text())
probes = corpus["probes"]
item_by_id = {p["id"]: p for p in probes}
# token-length proxy (tiny_ids present for every item) for off-domain length matching
def ntok(pid): return len(item_by_id[pid]["tiny_ids"])

# helper: domain routing mass dict for a row
def dommass(i):
    try: return json.loads(A["domain_M_weighted_json"][i] or "{}")
    except Exception: return {}

# activation-max item ids for a cell (unique, order preserved) from top_contexts_json
def actmax_items(i):
    try: tc = json.loads(A["top_contexts_json"][i] or "[]")
    except Exception: tc = []
    out = []
    for rec in tc:
        pid = rec[0]
        if pid in item_by_id and pid not in out: out.append(pid)
    return out

# label-matched items: same semantic_domain (+ operation/format when set) as the cell
def label_matched(i, want_n):
    pd, op, sf = A["primary_domain"][i], A["top_operation"][i], A["top_surface_format"][i]
    scored = []
    for p in probes:
        s = 0
        if p.get("semantic_domain") == pd: s += 2
        if op and p.get("operation") == op: s += 1
        if sf and p.get("surface_format") == sf: s += 2
        if s: scored.append((s, p["id"]))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [pid for _, pid in scored[:want_n]]

# off-domain matched controls: domains the cell routes ~0 mass to; match length to on-set
def off_items(i, on_ids, want_n):
    dm = dommass(i)
    lo_doms = {d for d, m in dm.items() if m <= 1e-4}
    # include any domain never seen in dm as also-zero
    all_doms = {p.get("semantic_domain") for p in probes}
    lo_doms |= (all_doms - set(dm.keys()))
    med = sorted(ntok(p) for p in on_ids)[len(on_ids)//2] if on_ids else 20
    cands = [p["id"] for p in probes
             if p.get("semantic_domain") in lo_doms and p["id"] not in on_ids]
    cands.sort(key=lambda pid: abs(ntok(pid) - med))       # length-matched
    picked = cands[:want_n]
    if len(picked) < want_n:                               # fallback: any length-matched item off the on-set
        extra = [p["id"] for p in probes if p["id"] not in on_ids and p["id"] not in picked]
        extra.sort(key=lambda pid: abs(ntok(pid) - med))
        picked += extra[:want_n - len(picked)]
    return picked[:want_n]

# generic same-layer substitute expert for the module-swap arm: highest-load
# non-specialist ('none' candidate_kind) in the same layer, else highest-load other.
def swap_target(i):
    layer, e_self = A["layer"][i], A["expert_id"][i]
    same = [(A["events_total"][j], A["expert_id"][j], A["candidate_kind"][j])
            for j in range(N) if A["execution_site"][j]=="main" and A["layer"][j]==layer
            and A["expert_id"][j]!=e_self]
    none_k = [(ev, e) for ev, e, ck in same if ck == "none"]
    pool = none_k if none_k else [(ev, e) for ev, e, ck in same]
    if not pool: return None
    pool.sort(reverse=True)
    return int(pool[0][1])

# ---------------- shortlist selection ----------------
picked, seen = [], set()
def take(i, stratum, swap=False):
    k = key(i)
    if k in seen or A["execution_site"][i] != "main": return False
    seen.add(k)
    on = []
    for pid in actmax_items(i):                # activation-max first
        if pid not in on: on.append(pid)
    for pid in label_matched(i, N_ON*2):       # top up with label-matched
        if pid not in on: on.append(pid)
        if len(on) >= N_ON: break
    on = on[:N_ON]
    off = off_items(i, on, N_OFF)
    picked.append({
        "cell": k, "site": "main", "layer": int(A["layer"][i]), "expert": int(A["expert_id"][i]),
        "stratum": stratum, "candidate_kind": A["candidate_kind"][i],
        "primary_domain": A["primary_domain"][i], "label_class": A["label_class"][i],
        "events_total": int(A["events_total"][i]),
        "sel_token_fraction": round(float(A["sel_token_fraction"][i]), 6),
        "primary_domain_enr_log2": round(float(A["primary_domain_enr_log2"][i]), 3),
        "top_surface_format": A["top_surface_format"][i], "top_operation": A["top_operation"][i],
        "routing_confidence": round(float(A["routing_confidence"][i]), 3),
        "on_items": on, "off_items": off,
        "swap_to": swap_target(i) if swap else None,
    })
    return True

def leads(kind, n, swap):
    # rank candidate_kind cells by the relevant surface enrichment, stable+enough events
    rows = [(A["top_surface_format_enr_log2"][i] if kind in ("format",) else
             A["top_operation_enr_log2"][i], i)
            for i in range(N) if A["candidate_kind"][i]==kind
            and A["label_class"][i] in ("stable","polysemantic") and A["events_total"][i] >= 100]
    rows.sort(key=lambda x: -x[0])
    c=0
    for _, i in rows:
        if take(i, f"lead_{kind}", swap): c+=1
        if c>=n: break

def specialists(domain, n):
    rows = [(A["primary_domain_enr_log2"][i], i) for i in range(N)
            if A["primary_domain"][i]==domain and A["label_class"][i]=="stable"
            and A["events_total"][i] >= 100]
    rows.sort(key=lambda x: -x[0]); c=0
    for _, i in rows:
        if take(i, f"specialist_{domain}", False): c+=1
        if c>=n: break

def generalists(n):
    rows = [(A["events_total"][i], i) for i in range(N)
            if A["label_class"][i]=="generalist"]
    rows.sort(key=lambda x: -x[0]); c=0
    for _, i in rows:
        if take(i, "generalist", False): c+=1
        if c>=n: break

def controls_rare(n):
    # low-load cells that DID activate (>=20 events so items exist) but are 'rare':
    rows = [(A["events_total"][i], i) for i in range(N)
            if A["label_class"][i]=="rare" and 20 <= A["events_total"][i] <= 60
            and A["candidate_kind"][i]=="none"]
    random.shuffle(rows); c=0
    for _, i in rows:
        if take(i, "control_rare", False): c+=1
        if c>=n: break

def controls_random_mid(n):
    rows = [i for i in range(N) if A["label_class"][i]=="stable"
            and A["candidate_kind"][i]=="none" and 150 <= A["events_total"][i] <= 400]
    random.shuffle(rows); c=0
    for i in rows:
        if take(i, "control_mid_none", False): c+=1
        if c>=n: break

leads("format", 5, swap=True)
leads("copy", 5, swap=True)
leads("arithmetic", 5, swap=True)
specialists("science", 2)
specialists("legal_fin", 2)
specialists("multiling", 2)
generalists(5)
controls_rare(4)
controls_random_mid(2)

# ---------------- assemble corpus subset ----------------
used_ids = set()
for c in picked:
    used_ids |= set(c["on_items"]); used_ids |= set(c["off_items"])
sub = {pid: {k: item_by_id[pid][k] for k in
             ("id","semantic_domain","operation","language","surface_format",
              "text_prompt","text_target","tiny_ids","tiny_n_prompt")}
       for pid in sorted(used_ids)}

n_swap = sum(1 for c in picked if c["swap_to"] is not None)
# prefill budget estimate
n_base = len(used_ids)
n_abl = sum(len(c["on_items"])+len(c["off_items"]) for c in picked) * 2      # contrib + route
n_swp = sum(min(N_SWAP_ON, len(c["on_items"])) for c in picked if c["swap_to"] is not None)
total = n_base + n_abl + n_swp

out = {"_about": "GLM-5.2 Stage-3 causal shortlist + item pool (from Stage-2 atlas; $0)",
       "seed": SEED, "n_on": N_ON, "n_off": N_OFF, "n_swap_on": N_SWAP_ON,
       "n_experts": len(picked), "n_swap_experts": n_swap,
       "n_unique_items": len(used_ids),
       "prefill_budget": {"baseline": n_base, "ablation_contrib_route": n_abl,
                          "module_swap": n_swp, "total": total},
       "strata_counts": {s: sum(1 for c in picked if c["stratum"]==s)
                         for s in sorted({c["stratum"] for c in picked})},
       "experts": picked}
(HERE/"corpus"/"stage3_shortlist.json").write_text(json.dumps(out, indent=1))
(HERE/"corpus"/"stage3_corpus.json").write_text(json.dumps({"items": sub}, ensure_ascii=False))

print(f"experts={len(picked)}  swap_experts={n_swap}  unique_items={len(used_ids)}")
print("strata:", json.dumps(out["strata_counts"]))
print("prefill budget:", json.dumps(out["prefill_budget"]))
for c in picked:
    print(f"  {c['cell']:14s} {c['stratum']:20s} kind={str(c['candidate_kind']):14s} "
          f"dom={str(c['primary_domain']):10s} ev={c['events_total']:4d} on={len(c['on_items'])} "
          f"off={len(c['off_items'])} swap={c['swap_to']}")
