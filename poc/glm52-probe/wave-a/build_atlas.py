#!/usr/bin/env python3
"""build_atlas.py — Stage-2 expert atlas from the Wave-A aggregation.

Consumes atlas_agg.py output + the corpus + ledger and produces, per the plan
(docs/next/design/glm52-expert-profiling-plan-sol-20260715.md §"Stage 2"):
  expert_atlas.parquet   one row per stored routed cell (execution_site, layer,
                         expert_id) — EVERY main cell enumerated (unseen ones too)
  expert_atlas_index.json compact index + summary + coverage gates
  atlas_summary.md       human summary
  coverage_gates.json    the decision-gate results

Matrix + labels are ROUTING-AFFINITY evidence only (evidence_level 0). Per the
plan, routing affinity is evidence about the GATE, not proof of expert FUNCTION;
labels are capped and tagged accordingly. "Enumerate all" must not become "invent
a speciality for all": cells below the coverage bar are marked unseen/rare/
unresolved honestly.

$0 local, deterministic (fixed bootstrap seed). numpy + pyarrow; no pandas.
"""
from __future__ import annotations
import argparse, csv, gzip, json, math, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

ALPHA = 0.5              # enrichment pseudo-count (events)
B_BOOT = 200             # family-bootstrap resamples
STABLE_MIN_EVENTS = 100  # plan: >=100 events ...
STABLE_MIN_FAMILIES = 20 # ... across >=20 prompt families
ENR_MIN = 0.585          # log2(1.5): min top-enrichment to call a specialisation
REPRO_MIN = 0.70         # plan: top-domain reproduces in >=70% of family bootstraps
RNG_SEED = 20260715


def _open(p):
    return gzip.open(p, "rt") if str(p).endswith(".gz") else open(p, "r")


def load_agg(path):
    with _open(path) as f:
        return json.load(f)


def load_subfam_meta(corpus_path, manifest_path):
    corpus = json.loads(Path(corpus_path).read_text())
    manifest = json.loads(Path(manifest_path).read_text())
    fam_split = {fam: m["split"] for fam, m in manifest["families"].items()}
    # subfamily "prompt_family#iscp" -> labels (each is exactly one corpus item)
    sfmeta = {}
    for it in corpus["probes"]:
        key = f"{it['prompt_family']}#{1 if it['is_counterpart'] else 0}"
        if key not in sfmeta:
            sfmeta[key] = {
                "family": it["prompt_family"],
                "domain": it["semantic_domain"],
                "operation": it["operation"],
                "language": it["language"],
                "surface_format": it["surface_format"],
                "answer_type": it["answer_type"],
                "split": fam_split[it["prompt_family"]],
            }
    vocab = manifest["label_vocab"]
    return sfmeta, vocab, manifest


def group_masses(sf_dict, sfmeta, key):
    """sum [events, wsum] over subfamilies grouped by label `key`."""
    ev = defaultdict(float); ws = defaultdict(float)
    for sfk, (e, w) in sf_dict.items():
        m = sfmeta.get(sfk)
        if not m:
            continue
        g = m[key]
        ev[g] += e; ws[g] += w
    return ev, ws


def enrichment(cell_ev_by_g, layer_ev_by_g, E_c, E_L, groups):
    """log2( p_cell(g) / p_layer(g) ) with ALPHA smoothing over `groups`."""
    K = len(groups)
    enr = {}
    Mfrac = {}
    for g in groups:
        p_cell = (cell_ev_by_g.get(g, 0.0) + ALPHA) / (E_c + ALPHA * K)
        p_lay = (layer_ev_by_g.get(g, 0.0) + ALPHA) / (E_L + ALPHA * K)
        enr[g] = math.log2(p_cell / p_lay) if p_lay > 0 else 0.0
        Mfrac[g] = cell_ev_by_g.get(g, 0.0) / E_c if E_c else 0.0
    return enr, Mfrac


def fam_domain_mass(sf_dict, sfmeta):
    """family -> (domain, events) collapsing base+cp (same domain)."""
    out = {}
    for sfk, (e, w) in sf_dict.items():
        m = sfmeta.get(sfk)
        if not m:
            continue
        fam = m["family"]; dom = m["domain"]
        if fam not in out:
            out[fam] = [dom, 0.0]
        out[fam][1] += e
    return out


def bootstrap_domain(cell_fdm, layer_fdm, families, domains, rng, B=B_BOOT):
    """Family bootstrap of the domain argmax. Returns (reproducibility, ci_lo,
    ci_hi, point_argmax, point_top_enr)."""
    fam_arr = np.array(families)
    nF = len(fam_arr)
    dom_idx = {d: i for i, d in enumerate(domains)}
    K = len(domains)
    # per-family domain index + cell/layer event mass
    fdi = np.zeros(nF, dtype=np.int32)
    cmass = np.zeros(nF); lmass = np.zeros(nF)
    for i, fam in enumerate(fam_arr):
        if fam in cell_fdm:
            fdi[i] = dom_idx[cell_fdm[fam][0]]; cmass[i] = cell_fdm[fam][1]
        else:
            fdi[i] = dom_idx[layer_fdm[fam][0]] if fam in layer_fdm else 0
        lmass[i] = layer_fdm[fam][1] if fam in layer_fdm else 0.0

    # point estimate
    cd0 = np.zeros(K); ld0 = np.zeros(K)
    np.add.at(cd0, fdi, cmass); np.add.at(ld0, fdi, lmass)
    pc0 = (cd0 + ALPHA) / (cd0.sum() + ALPHA*K)
    pl0 = (ld0 + ALPHA) / (ld0.sum() + ALPHA*K)
    point = np.log2(pc0 / pl0)
    p_arg = int(np.argmax(point))
    # B resamples vectorised: (B,nF) family picks -> (B,K) accumulators in one add.at
    sel = rng.integers(0, nF, size=(B, nF))
    rows = np.repeat(np.arange(B), nF)
    dcol = fdi[sel].ravel()
    cd = np.zeros((B, K)); ld = np.zeros((B, K))
    np.add.at(cd, (rows, dcol), cmass[sel].ravel())
    np.add.at(ld, (rows, dcol), lmass[sel].ravel())
    pc = (cd + ALPHA) / (cd.sum(1, keepdims=True) + ALPHA*K)
    pl = (ld + ALPHA) / (ld.sum(1, keepdims=True) + ALPHA*K)
    ev = np.log2(pc / pl)                          # (B,K)
    wins = int((np.argmax(ev, axis=1) == p_arg).sum())
    top_enrs = ev[:, p_arg]
    lo, hi = np.percentile(top_enrs, [10, 90])
    return wins / B, float(lo), float(hi), domains[p_arg], float(point[p_arg])


def candidate_kind(dom, op, fmt, dom_enr, op_enr, fmt_enr, events):
    """Stage-4 deterministic-replacement lead heuristic from routing enrichment."""
    if events < STABLE_MIN_EVENTS:
        return "none"
    fmt_structural = {"json", "xml", "csv", "markdown", "table", "whitespace"}
    cands = []
    if dom == "copy" and dom_enr >= ENR_MIN:
        cands.append(("copy", dom_enr))
    if op == "copy" and op_enr >= ENR_MIN:
        cands.append(("copy", op_enr))
    if dom == "math" and dom_enr >= ENR_MIN:
        cands.append(("arithmetic", dom_enr))
    if op == "arithmetic" and op_enr >= ENR_MIN:
        cands.append(("arithmetic", op_enr))
    if fmt in fmt_structural and fmt_enr >= ENR_MIN:
        cands.append(("format", fmt_enr))
    if dom in ("structured", "tool_schema") and dom_enr >= ENR_MIN:
        cands.append(("format", dom_enr))
    if dom == "factual" and dom_enr >= ENR_MIN:
        cands.append(("semantic_lookup", dom_enr))
    if op == "lookup" and op_enr >= ENR_MIN:
        cands.append(("semantic_lookup", op_enr))
    if not cands:
        return "none"
    cands.sort(key=lambda x: -x[1])
    return cands[0][0]


def spearman(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    if len(x) < 3:
        return float("nan")
    rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
    rx = rx - rx.mean(); ry = ry - ry.mean()
    d = math.sqrt((rx*rx).sum() * (ry*ry).sum())
    return float((rx*ry).sum() / d) if d > 0 else float("nan")


def load_ledger_main_cells(ledger_path):
    """All main routed cells (site,layer,e) from expert_ledger.csv."""
    cells = []
    with open(ledger_path) as f:
        for row in csv.DictReader(f):
            if row["main_or_mtp"] != "main":
                continue
            layer = int(row["layer"])
            lo = int(row["expert_id_min"]); hi = int(row["expert_id_max"])
            for e in range(lo, hi + 1):
                cells.append(("main", layer, e))
    return cells


def build(agg, sfmeta, vocab, manifest, ledger_cells, integrity, out_dir):
    rng = np.random.default_rng(RNG_SEED)
    cells = agg["cells"]; layers = agg["layers"]
    domains = vocab["semantic_domain"]; ops = vocab["operation"]
    langs = vocab["language"]; fmts = vocab["surface_format"]
    all_families = sorted(manifest["families"].keys())
    disc_fams = {f for f, m in manifest["families"].items() if m["split"] == "discovery"}
    held_fams = {f for f, m in manifest["families"].items() if m["split"] == "held_out"}

    # precompute layer group masses (events) + fam-domain mass, per layer
    layer_cache = {}
    for lkey, L in layers.items():
        ev_d, _ = group_masses(L["sf"], sfmeta, "domain")
        ev_o, _ = group_masses(L["sf"], sfmeta, "operation")
        ev_l, _ = group_masses(L["sf"], sfmeta, "language")
        ev_f, _ = group_masses(L["sf"], sfmeta, "surface_format")
        E_L = float(L["tot"][0])
        layer_cache[lkey] = {
            "E_L": E_L, "dom": ev_d, "op": ev_o, "lang": ev_l, "fmt": ev_f,
            "fdm": fam_domain_mass(L["sf"], sfmeta),
        }

    rows = []
    active_keys = set()
    # for the Spearman gate: per layer collect (disc_enr, held_enr) over cells x domains
    layer_spear = defaultdict(lambda: [[], []])

    total_mass_all = 0.0
    mass_ge100 = 0.0

    for ckey, c in cells.items():
        site, layer_s, e_s = ckey.split("|")
        layer = int(layer_s); e = int(e_s)
        active_keys.add((site, layer, e))
        lkey = f"{site}|{layer}"
        lc = layer_cache[lkey]
        E_c = float(c["tot"][0]); W_c = float(c["tot"][1])
        total_mass_all += E_c
        n_families = len({k.split("#")[0] for k in c["sf"].keys()})
        n_subfam = len(c["sf"])

        cev_d, cws_d = group_masses(c["sf"], sfmeta, "domain")
        cev_o, _ = group_masses(c["sf"], sfmeta, "operation")
        cev_l, _ = group_masses(c["sf"], sfmeta, "language")
        cev_f, _ = group_masses(c["sf"], sfmeta, "surface_format")
        enr_d, M_d = enrichment(cev_d, lc["dom"], E_c, lc["E_L"], domains)
        enr_o, _ = enrichment(cev_o, lc["op"], E_c, lc["E_L"], ops)
        enr_l, _ = enrichment(cev_l, lc["lang"], E_c, lc["E_L"], langs)
        enr_f, _ = enrichment(cev_f, lc["fmt"], E_c, lc["E_L"], fmts)

        # weighted M_{e,d}: cell domain wsum / layer domain wsum
        _, lws_d = group_masses(layers[lkey]["sf"], sfmeta, "domain")
        M_weighted = {d: (cws_d.get(d, 0.0) / lws_d[d]) if lws_d.get(d) else 0.0 for d in domains}

        top_dom = max(domains, key=lambda d: enr_d[d])
        top_op = max(ops, key=lambda g: enr_o[g])
        top_lang = max(langs, key=lambda g: enr_l[g])
        top_fmt = max(fmts, key=lambda g: enr_f[g])

        eligible = (E_c >= STABLE_MIN_EVENTS and n_families >= STABLE_MIN_FAMILIES)
        if E_c >= STABLE_MIN_EVENTS:
            mass_ge100 += E_c

        repro = ci_lo = ci_hi = float("nan")
        if eligible:
            cell_fdm = fam_domain_mass(c["sf"], sfmeta)
            repro, ci_lo, ci_hi, _, _ = bootstrap_domain(
                cell_fdm, lc["fdm"], all_families, domains, rng)

        # label class (routing-affinity only)
        if E_c < STABLE_MIN_EVENTS:
            label_class = "rare"
        elif n_families < STABLE_MIN_FAMILIES:
            label_class = "unresolved"
        elif enr_d[top_dom] < ENR_MIN:
            label_class = "generalist"
        elif repro >= REPRO_MIN and ci_lo > 0:
            label_class = "stable"
        else:
            label_class = "polysemantic"

        # routing confidence in [0,1] (Level-0 capped): coverage, split-stability
        # (bootstrap repro), label-margin. NO local/causal channel here.
        cov = min(1.0, (min(E_c, 400) / 400) * (min(n_families, 40) / 40))
        margin = 0.0
        sorted_enr = sorted(enr_d.values(), reverse=True)
        if len(sorted_enr) >= 2:
            margin = max(0.0, sorted_enr[0] - sorted_enr[1])
        label_margin = min(1.0, margin / 2.0)
        split_stab = repro if repro == repro else 0.0
        routing_conf = round(0.34*cov + 0.33*split_stab + 0.33*label_margin, 4)

        cand = candidate_kind(top_dom, top_op, top_fmt,
                              enr_d[top_dom], enr_o[top_op], enr_f[top_fmt], E_c)

        rank = c["rank"]; rank0_frac = rank[0] / E_c if E_c else 0.0
        io = c["io"]; io_tgt = io[2] / E_c if E_c else 0.0
        mean_gate = c["tot"][2] / E_c if E_c else 0.0
        mean_mgn = c["tot"][3] / E_c if E_c else 0.0

        # Spearman collector: cell contributes its per-domain enrichment computed
        # on discovery-only and held_out-only subfamilies
        cev_d_disc = defaultdict(float); cev_d_held = defaultdict(float)
        for sfk, (ev, ws) in c["sf"].items():
            m = sfmeta.get(sfk)
            if not m:
                continue
            if m["family"] in disc_fams:
                cev_d_disc[m["domain"]] += ev
            elif m["family"] in held_fams:
                cev_d_held[m["domain"]] += ev
        Ec_disc = sum(cev_d_disc.values()); Ec_held = sum(cev_d_held.values())
        if Ec_disc >= 20 and Ec_held >= 20:
            ed_disc, _ = enrichment(cev_d_disc, lc["dom"], Ec_disc, lc["E_L"], domains)
            ed_held, _ = enrichment(cev_d_held, lc["dom"], Ec_held, lc["E_L"], domains)
            for d in domains:
                layer_spear[layer][0].append(ed_disc[d])
                layer_spear[layer][1].append(ed_held[d])

        rows.append({
            "execution_site": site, "layer": layer, "expert_id": e,
            "events_total": int(E_c), "wsum_total": round(W_c, 4),
            "sel_token_fraction": round(E_c / lc["E_L"], 6) if lc["E_L"] else 0.0,
            "n_families": n_families, "n_subfamilies": n_subfam,
            "label_class": label_class,
            "primary_domain": top_dom if label_class in ("stable", "polysemantic") else None,
            "primary_domain_enr_log2": round(enr_d[top_dom], 4),
            "primary_domain_M_weighted": round(M_weighted[top_dom], 6),
            "routing_confidence": routing_conf,
            "evidence_level": 0,
            "bootstrap_reproducibility": None if repro != repro else round(repro, 4),
            "enr_ci_lo": None if ci_lo != ci_lo else round(ci_lo, 4),
            "enr_ci_hi": None if ci_hi != ci_hi else round(ci_hi, 4),
            "top_operation": top_op, "top_operation_enr_log2": round(enr_o[top_op], 4),
            "top_surface_format": top_fmt, "top_surface_format_enr_log2": round(enr_f[top_fmt], 4),
            "top_language": top_lang, "top_language_enr_log2": round(enr_l[top_lang], 4),
            "candidate_kind": cand,
            "mean_gate": round(mean_gate, 5), "mean_margin": round(mean_mgn, 5),
            "rank0_frac": round(rank0_frac, 4), "io_target_frac": round(io_tgt, 4),
            "domain_enr_json": json.dumps({d: round(enr_d[d], 3) for d in domains}),
            "domain_M_weighted_json": json.dumps({d: round(M_weighted[d], 5) for d in domains}),
            "top_contexts_json": json.dumps(sorted(c["top"], key=lambda x: -x[2])),
        })

    # enumerate inactive (unseen) main cells
    n_active = len(active_keys)
    for (site, layer, e) in ledger_cells:
        if (site, layer, e) in active_keys:
            continue
        rows.append({
            "execution_site": site, "layer": layer, "expert_id": e,
            "events_total": 0, "wsum_total": 0.0, "sel_token_fraction": 0.0,
            "n_families": 0, "n_subfamilies": 0, "label_class": "unseen",
            "primary_domain": None, "primary_domain_enr_log2": 0.0,
            "primary_domain_M_weighted": 0.0, "routing_confidence": 0.0,
            "evidence_level": 0, "bootstrap_reproducibility": None,
            "enr_ci_lo": None, "enr_ci_hi": None,
            "top_operation": None, "top_operation_enr_log2": 0.0,
            "top_surface_format": None, "top_surface_format_enr_log2": 0.0,
            "top_language": None, "top_language_enr_log2": 0.0,
            "candidate_kind": "none", "mean_gate": 0.0, "mean_margin": 0.0,
            "rank0_frac": 0.0, "io_target_frac": 0.0,
            "domain_enr_json": "{}", "domain_M_weighted_json": "{}",
            "top_contexts_json": "[]",
        })

    rows.sort(key=lambda r: (r["execution_site"], r["layer"], r["expert_id"]))

    # ---- coverage gates ----
    layer_spear_vals = {}
    for layer, (xs, ys) in layer_spear.items():
        if len(xs) >= 12:
            layer_spear_vals[layer] = spearman(xs, ys)
    spear_ok_layers = [v for v in layer_spear_vals.values() if v == v and v >= 0.8]
    spear_frac = (len(spear_ok_layers) / len(layer_spear_vals)) if layer_spear_vals else 0.0
    median_spear = float(np.median([v for v in layer_spear_vals.values() if v == v])) if layer_spear_vals else float("nan")

    mass_cov = (mass_ge100 / total_mass_all) if total_mass_all else 0.0
    n_stable = sum(1 for r in rows if r["label_class"] == "stable")
    n_rows_labelclass = defaultdict(int)
    for r in rows:
        n_rows_labelclass[r["label_class"]] += 1

    gates = {
        "trace_invariants_100pct": bool(integrity.get("integrity_clean", None)),
        "trace_invariants_source": integrity,
        "mass_on_ge100_event_experts": round(mass_cov, 4),
        "mass_coverage_ge_0p95": mass_cov >= 0.95,
        "n_stable_labels": n_stable,
        "stable_requires": f">={STABLE_MIN_EVENTS} events across >={STABLE_MIN_FAMILIES} families",
        "discovery_heldout_spearman_median": None if median_spear != median_spear else round(median_spear, 4),
        "discovery_heldout_spearman_frac_layers_ge_0p8": round(spear_frac, 4),
        "spearman_gate_ge_0p8": (median_spear == median_spear and median_spear >= 0.8),
        "n_cells_active": n_active,
        "n_cells_enumerated": len(rows),
        "label_class_counts": dict(n_rows_labelclass),
    }

    # ---- write parquet ----
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist(rows)
    pq.write_table(table, str(out_dir / "expert_atlas.parquet"))

    # ---- index json ----
    index = {}
    for r in rows:
        if r["label_class"] in ("unseen",):
            continue
        index[f"{r['execution_site']}|{r['layer']}|{r['expert_id']}"] = {
            "label_class": r["label_class"],
            "primary_domain": r["primary_domain"],
            "candidate_kind": r["candidate_kind"],
            "events": r["events_total"],
            "routing_confidence": r["routing_confidence"],
            "enr": r["primary_domain_enr_log2"],
        }
    # top specialised (stable, highest enr, ci_lo>0)
    stable_rows = [r for r in rows if r["label_class"] == "stable"]
    stable_rows.sort(key=lambda r: -r["primary_domain_enr_log2"])
    top_specialised = [{
        "cell": f"{r['execution_site']}|{r['layer']}|{r['expert_id']}",
        "primary_domain": r["primary_domain"], "enr_log2": r["primary_domain_enr_log2"],
        "reproducibility": r["bootstrap_reproducibility"], "enr_ci_lo": r["enr_ci_lo"],
        "events": r["events_total"], "n_families": r["n_families"],
        "routing_confidence": r["routing_confidence"],
    } for r in stable_rows[:40]]
    # candidate leads by kind
    leads = {}
    for kind in ("format", "copy", "arithmetic", "semantic_lookup"):
        krows = [r for r in rows if r["candidate_kind"] == kind and r["label_class"] in ("stable", "polysemantic")]
        krows.sort(key=lambda r: -max(r["primary_domain_enr_log2"], r["top_surface_format_enr_log2"], r["top_operation_enr_log2"]))
        leads[kind] = [{
            "cell": f"{r['execution_site']}|{r['layer']}|{r['expert_id']}",
            "primary_domain": r["primary_domain"], "top_op": r["top_operation"],
            "top_format": r["top_surface_format"], "events": r["events_total"],
            "dom_enr": r["primary_domain_enr_log2"], "op_enr": r["top_operation_enr_log2"],
            "fmt_enr": r["top_surface_format_enr_log2"], "label_class": r["label_class"],
        } for r in krows[:15]]

    index_out = {
        "schema": "kot-expert-atlas/1",
        "meta": agg["meta"],
        "coverage_gates": gates,
        "top_specialised": top_specialised,
        "deterministic_replacement_leads": leads,
        "index": index,
    }
    (out_dir / "expert_atlas_index.json").write_text(json.dumps(index_out, indent=1))
    (out_dir / "coverage_gates.json").write_text(json.dumps(gates, indent=2))

    write_summary_md(out_dir, agg, gates, n_rows_labelclass, top_specialised, leads,
                     layer_spear_vals)
    return gates, top_specialised, leads


def lc_sf(layer_obj):
    return layer_obj["sf"]


def write_summary_md(out_dir, agg, gates, lc_counts, top_specialised, leads, layer_spear):
    m = agg["meta"]
    L = []
    L.append("# GLM-5.2 Wave-A expert atlas — Stage-2 summary\n")
    L.append("EXPLORATORY infra (rigor relaxed vs a frozen experiment). Routing-affinity "
             "evidence only (evidence_level 0): this maps what routes WHERE, not what an "
             "expert DOES. Functional/causal labels require Stage 3.\n")
    L.append("## Run\n")
    L.append(f"- trace rows aggregated: {m['n_rows']:,} (repeat items skipped: {m['n_repeat_items_skipped']})")
    L.append(f"- items ended: {m['n_items_ended']}  ·  active cells: {m['n_cells_active']:,} / 19,200 main")
    L.append(f"- topk_seen: {m['topk_seen']}  ·  layers active: {m['n_layers_active']}\n")
    L.append("## Coverage gates (Stage-2 decision gate)\n")
    L.append(f"- trace invariants 100%: **{gates['trace_invariants_100pct']}**")
    L.append(f"- routing mass on experts with >=100 events: **{gates['mass_on_ge100_event_experts']:.3f}** "
             f"(gate >=0.95 -> {'PASS' if gates['mass_coverage_ge_0p95'] else 'FAIL'})")
    L.append(f"- discovery-vs-held-out layer Spearman (median): "
             f"**{gates['discovery_heldout_spearman_median']}** "
             f"(gate >=0.8 -> {'PASS' if gates['spearman_gate_ge_0p8'] else 'FAIL'}; "
             f"frac layers>=0.8={gates['discovery_heldout_spearman_frac_layers_ge_0p8']})")
    L.append(f"- stable-labelled cells: **{gates['n_stable_labels']}** "
             f"({gates['stable_requires']})\n")
    L.append("## Label-class census (all 19,200 main cells enumerated)\n")
    for k in ("stable", "polysemantic", "generalist", "unresolved", "rare", "unseen"):
        L.append(f"- {k}: {lc_counts.get(k,0):,}")
    L.append("")
    L.append("## Top routing-specialised experts (stable; highest layer-normalised log2 enrichment)\n")
    L.append("| cell (site\\|layer\\|expert) | domain | enr log2 | repro | ci_lo | events | families |")
    L.append("|---|---|---|---|---|---|---|")
    for r in top_specialised[:20]:
        L.append(f"| {r['cell']} | {r['primary_domain']} | {r['enr_log2']:.2f} | "
                 f"{r['reproducibility']} | {r['enr_ci_lo']} | {r['events']} | {r['n_families']} |")
    L.append("")
    L.append("## Deterministic-replacement leads (Stage-4 candidates, routing-shaped)\n")
    for kind in ("format", "copy", "arithmetic", "semantic_lookup"):
        rows = leads.get(kind, [])
        L.append(f"### {kind}: {len(rows)} candidate cell(s)")
        for r in rows[:8]:
            L.append(f"- {r['cell']} — dom={r['primary_domain']} op={r['top_op']} "
                     f"fmt={r['top_format']} · enr(dom/op/fmt)={r['dom_enr']:.2f}/"
                     f"{r['op_enr']:.2f}/{r['fmt_enr']:.2f} · n={r['events']} · {r['label_class']}")
        L.append("")
    L.append("## Honesty note\n")
    L.append("Cells below the coverage bar are marked rare/unresolved/unseen, NOT given a "
             "speciality. A routing-affinity label is evidence about the GATE, capped at "
             "evidence_level 0; it is not a functional claim and does not by itself justify "
             "replacement. Stage 3 (activation-max contrasts, local functional signatures, "
             "causal ablation) is required before any expert is called replaceable.\n")
    (out_dir / "atlas_summary.md").write_text("\n".join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agg", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--corpus-manifest", required=True)
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--integrity", help="trace_summary.json for the invariant-pass flag")
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()

    agg = load_agg(a.agg)
    sfmeta, vocab, manifest = load_subfam_meta(a.corpus, a.corpus_manifest)
    ledger_cells = load_ledger_main_cells(a.ledger)
    integrity = {}
    if a.integrity and Path(a.integrity).exists():
        ts = json.loads(Path(a.integrity).read_text())
        gg = ts.get("go_no_go", {})
        integrity = {"integrity_clean": gg.get("integrity_clean"),
                     "repeat_byte_identical": gg.get("repeat_byte_identical"),
                     "n_integrity_errors": len(ts.get("integrity_errors", [])),
                     "n_repeat_errors": len(ts.get("repeat_errors", []))}
    gates, top_specialised, leads = build(agg, sfmeta, vocab, manifest, ledger_cells,
                                          integrity, a.out_dir)
    print(json.dumps(gates, indent=2))
    print(f"\ntop specialised (first 5): {json.dumps(top_specialised[:5], indent=1)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
