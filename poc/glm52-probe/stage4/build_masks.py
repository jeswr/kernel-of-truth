#!/usr/bin/env python3
"""build_masks.py — glm-s4drop-0 mask construction (PURE FUNCTION, pinned).

Consumes exactly three hash-pinned inputs plus registered constants/seeds and
emits the seven Stage-4 mask tables + an audit manifest. Byte-identical
across reruns (no RNG state, no time; SHA-256 DRBG only). Every threshold is
STIPULATED and registered (glm-s4drop-0 record; design doc SS3).

Inputs
  --telemetry  kot-s4tel/1 JSON: T-build decode telemetry (per-cell selection
               counts + cache-miss bytes under the pinned cache config).
               PINNED-AT-INPUTS at freeze; produced by the runner's telemetry
               phase; its sha256 enters the run sidecar.
  --stage3     data/glm-s4drop-stage3-inputs-v1/stage3_analysis.json (frozen
               copy; 16-cell skiplist + SAFE/LOAD-BEARING/CHARACTERISE labels)
  --atlas     data/glm-s4drop-stage3-inputs-v1/expert_atlas_index.json
               (frozen copy; per-cell label_class for the tier-2 ranking)

Cost model (design doc SS4.1): the value of dropping a cell is the I/O it
stops causing, NOT its cell count. c(cell) =
  tier "M": telemetry per-cell miss_bytes / decode_tokens   (preferred)
  tier "P": telemetry per-cell sel * bytes  / decode_tokens (registered
            fallback when the engine cannot attribute misses per cell; a
            pessimistic upper bound, DISCLOSED; the SAME tier is used for
            every mask so matched-I/O comparisons stay internally valid).
The telemetry file declares its tier; this builder never silently degrades.

Masks (design doc SS3.2; arms carry these exact names)
  s4-sem16    the 16-cell Stage-3 causal skiplist, DROP-only (joint-safety
              cohort — the ASM-2383 simultaneity gap).
  s4-remap16  same 16 cells; the 9 cells with a Stage-3 swap_to get
              SWAP <dst> (CACHE_ROUTE-analog substitution), the 7 others
              DROP. SEPARATE arm — drop and remap are never confounded.
  s4-semd     the PRIMARY semantic mask at the registered dose (DOSE_FRAC of
              total expert miss-bytes/token). Greedy, cost-weighted, tiered:
                tier-0 skiplist (desc causal_confidence),
                tier-1 the 6 SAFE-but-below-SKIP_MIN_CONF cells,
                tier-2 atlas label_class in {rare, unseen} or absent from the
                       atlas index, EXCLUDING Stage-3 LOAD-BEARING /
                       CHARACTERISE-MORE cells, desc c(cell).
              If tiers exhaust below the dose, the mask is CAPPED at the
              achieved dose (recorded; the kill criterion prices a cap
              below IO_MIN_FRAC).
  s4-bldf-d   the PRIMARY blind comparator: EXPERT_BUDGET-analog frequency
              heuristic — every main cell ranked ASCENDING selection count
              (no causal/atlas knowledge), greedily added until its removed
              I/O matches s4-semd within MATCH_TOL.
  s4-bldr-d-r1..r3  secondary random-blind: cells sampled without
              replacement with probability proportional to c(cell) (seeded
              DRBG), matched to s4-semd within MATCH_TOL.

Serialization (canonical, fail-closed at engine load): ASCII, LF; '#' header
lines carrying schema id, arm, params, input sha256s; then one line per cell
"main|L|E DROP" or "main|L|E SWAP <dst>", sorted by (L,E); layers 3..78,
experts 0..255 only. Whole-file sha256s land in masks_manifest.json.

Degenerate-instrument handling (cross-model review 2026-07-16, findings B4):
a ZERO achievable semantic dose emits a REGISTERED construction-kill manifest
(kot-s4mask-manifest/1 with construction_kill set; exit 0; no blind arms) —
never a division-by-zero crash; and any blind mask IDENTICAL to s4-semd is a
fail-closed refusal (ERR_S4_MASK_IDENTICAL) in the production build path,
because a matched pair with zero symmetric difference makes the primary
contrast vacuous (d_i identically 0 could otherwise masquerade as a real tie).

    python3 build_masks.py --telemetry T.json --stage3 S.json --atlas A.json --out DIR
    python3 build_masks.py --selftest          # synthetic-fixture green mock
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys

# Registered constants (STIPULATED; glm-s4drop-0 design doc SS3.3 / ASM-2386).
DOSE_FRAC = 0.10        # target removed fraction of total expert miss-bytes/token
MATCH_TOL = 0.02        # blind-vs-semantic projected removed-I/O relative tolerance
IO_MIN_FRAC = 0.02      # below this achievable semantic dose the lever is dead (kill trigger 2)
PASS_DOSE_FRAC = 0.08   # PASS additionally requires at least this achieved dose
BLIND_SEEDS = (20260803, 20260804, 20260805)
MAIN_LAYERS = range(3, 79)   # 76 sparse MoE layers, 3..78 INCLUSIVE — the registered MEASURED
                             # correction (ASM-2342 R3 amendment: committed stats files span MoE
                             # layers 3-78 = 76 layers). The pre-review revision hard-coded 3..77
                             # (75 layers), silently dropping layer 78 from the dose denominator
                             # and every mask universe (cross-model review 2026-07-16, finding C1).
N_EXPERTS = 256
SKIP_MIN_CONF = 0.5     # stage-3 stipulated skiplist confidence floor (stage3_analyze.py)


def die(code: str, msg: str):
    print("%s: %s" % (code, msg), file=sys.stderr)
    sys.exit(1)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def drbg_ints(seed: int, n_max: int):
    """Deterministic uniform ints in [0, n_max) from SHA-256(seed||counter)."""
    ctr = 0
    while True:
        d = hashlib.sha256(("glm-s4drop-0:%d:%d" % (seed, ctr)).encode()).digest()
        yield int.from_bytes(d[:8], "big") % n_max
        ctr += 1


def cell_key(cell: str):
    _, layer, expert = cell.split("|")
    return int(layer), int(expert)


def load_telemetry(path: str) -> dict:
    tel = json.load(open(path, encoding="utf-8"))
    if tel.get("_schema") != "kot-s4tel/1":
        die("ERR_S4_TEL_SCHEMA", "telemetry _schema %r != kot-s4tel/1" % tel.get("_schema"))
    if tel.get("tier") not in ("M", "P"):
        die("ERR_S4_TEL_TIER", "telemetry tier %r not in M/P" % tel.get("tier"))
    if not isinstance(tel.get("decode_tokens"), int) or tel["decode_tokens"] <= 0:
        die("ERR_S4_TEL_TOKENS", "decode_tokens must be a positive int")
    if not isinstance(tel.get("cells"), dict) or not tel["cells"]:
        die("ERR_S4_TEL_CELLS", "telemetry carries no cells")
    for cell, rec in tel["cells"].items():
        parts = cell.split("|")
        if len(parts) != 3 or parts[0] != "main":
            die("ERR_S4_TEL_CELLS", "non-main or malformed cell id %r" % cell)
        L, E = int(parts[1]), int(parts[2])
        if L not in MAIN_LAYERS or not (0 <= E < N_EXPERTS):
            die("ERR_S4_TEL_CELLS", "cell %r outside main layer/expert range" % cell)
        need = ("sel", "bytes") if tel["tier"] == "P" else ("sel", "bytes", "miss_bytes")
        for k in need:
            if not isinstance(rec.get(k), int) or rec[k] < 0:
                die("ERR_S4_TEL_CELLS", "cell %r missing/invalid field %r (tier %s)"
                    % (cell, k, tel["tier"]))
    return tel


def cost_map(tel: dict) -> dict:
    """cell -> projected removed miss-bytes per decode token (the registered
    cost model, tier-consistent for every mask)."""
    T = tel["decode_tokens"]
    if tel["tier"] == "M":
        return {c: r["miss_bytes"] / T for c, r in tel["cells"].items()}
    return {c: (r["sel"] * r["bytes"]) / T for c, r in tel["cells"].items()}


def load_stage3(path: str):
    s3 = json.load(open(path, encoding="utf-8"))
    skip = [(s["cell"], s.get("swap_to"), float(s["causal_confidence"])) for s in s3["skiplist"]]
    if len(skip) != s3.get("skiplist_size"):
        die("ERR_S4_STAGE3", "skiplist length %d != skiplist_size %s"
            % (len(skip), s3.get("skiplist_size")))
    labels = {e["cell"]: e["label"] for e in s3["experts"]}
    safe_non_skip = [(e["cell"], float(e["causal_confidence"])) for e in s3["experts"]
                     if e["label"] == "SAFE-TO-DROP"
                     and e["cell"] not in {c for c, _, _ in skip}]
    excluded = {c for c, l in labels.items() if l in ("LOAD-BEARING", "CHARACTERISE-MORE")}
    return skip, safe_non_skip, excluded


def load_atlas_classes(path: str) -> dict:
    idx = json.load(open(path, encoding="utf-8")).get("index")
    if not isinstance(idx, dict):
        die("ERR_S4_ATLAS", "atlas index missing")
    return {c: (v or {}).get("label_class") for c, v in idx.items()}


def universe():
    return ["main|%d|%d" % (L, E) for L in MAIN_LAYERS for E in range(N_EXPERTS)]


def greedy_fill(ordered, cost, target, lo_frac, hi_frac):
    """Add POSITIVE-COST cells in the given order until the summed cost lands
    in [target*lo_frac, target*hi_frac]; a cell whose addition would overshoot
    the upper edge is skipped. ZERO-COST CELLS ARE NEVER ADDED (skeptic-4
    finding 1: free-appending unobserved cells lets a mask silently drop
    experts the telemetry never priced). Returns (cells, achieved). If the
    order exhausts below the lower edge, returns what was achieved (caller
    decides whether a cap is lawful)."""
    got, tot = [], 0.0
    lo, hi = target * lo_frac, target * hi_frac
    for c in ordered:
        w = cost.get(c, 0.0)
        if w <= 0 or tot + w > hi:
            continue
        got.append(c)
        tot += w
        if tot >= lo:
            break
    return got, tot


def build_masks(tel, skip, safe_non_skip, excluded, atlas_classes):
    cost = cost_map(tel)
    total_io = sum(cost.values())
    if total_io <= 0:
        die("ERR_S4_TEL_TOTAL", "total projected expert miss-bytes/token is zero")

    # --- fixed 16-cell masks -------------------------------------------------
    sem16 = {c: "DROP" for c, _, _ in skip}
    remap16 = {c: ("SWAP %d" % swap if swap is not None else "DROP")
               for c, swap, _ in skip}
    io_sem16 = sum(cost.get(c, 0.0) for c in sem16)

    # --- s4-semd: tiered, cost-weighted, greedy to the dose ------------------
    tier0 = [c for c, _, conf in sorted(skip, key=lambda t: (-t[2], cell_key(t[0])))]
    tier1 = [c for c, conf in sorted(safe_non_skip, key=lambda t: (-t[1], cell_key(t[0])))]
    t01 = set(tier0) | set(tier1)
    tier2 = [c for c in universe()
             if c not in t01 and c not in excluded
             and cost.get(c, 0.0) > 0
             and atlas_classes.get(c) in ("rare", "unseen", None)]
    tier2.sort(key=lambda c: (-cost.get(c, 0.0),) + cell_key(c))

    target = DOSE_FRAC * total_io
    # tier-0/1 enter unconditionally (they ARE the causal evidence, zero-cost
    # or not); the tier-2 EXTENSION adds positive-cost cells only.
    semd_cells = list(tier0) + list(tier1)
    io_semd = sum(cost.get(c, 0.0) for c in semd_cells)
    hi = target * (1 + MATCH_TOL)
    for c in tier2:
        w = cost.get(c, 0.0)
        if io_semd + w > hi:
            continue
        semd_cells.append(c)
        io_semd += w
        if io_semd >= target * (1 - MATCH_TOL):
            break
    dose_capped = io_semd < target * (1 - MATCH_TOL)
    semd = {c: "DROP" for c in semd_cells}

    # ZERO achievable dose => a REGISTERED construction-kill result, never a
    # division-by-zero crash (cross-model review 2026-07-16, finding B4): the
    # blind arms are unbuildable (nothing to match), so the manifest records
    # the kill and the runner pipes a phase:"construction" meta to the pinned
    # analysis, which fires kill trigger 2 from telemetry+masks alone.
    if io_semd <= 0:
        audit = {
            "tier": tel["tier"], "decode_tokens": tel["decode_tokens"],
            "total_expert_miss_bytes_per_tok": total_io,
            "dose_frac_target": DOSE_FRAC, "match_tol": MATCH_TOL,
            "io_min_frac": IO_MIN_FRAC, "pass_dose_frac": PASS_DOSE_FRAC,
            "dose_capped": True,
            "construction_kill": {"fired": True, "reason": "dose-zero",
                                   "achieved_frac": 0.0},
            "arms": {
                "s4-sem16": {"cells": len(sem16), "removed_bytes_per_tok": io_sem16,
                              "removed_frac": io_sem16 / total_io},
                "s4-remap16": {"cells": len(remap16), "removed_bytes_per_tok": io_sem16,
                                "removed_frac": io_sem16 / total_io,
                                "swaps": sum(1 for v in remap16.values() if v.startswith("SWAP"))},
                "s4-semd": {"cells": len(semd), "removed_bytes_per_tok": 0.0,
                             "removed_frac": 0.0,
                             "tier0_used": sum(1 for c in semd if c in set(tier0)),
                             "tier1_used": sum(1 for c in semd if c in set(tier1))},
            },
        }
        return {"s4-sem16": sem16, "s4-remap16": remap16, "s4-semd": semd}, audit

    # --- s4-bldf-d: frequency-heuristic blind, matched to io_semd ------------
    # Positive-cost cells only (finding 1); window +-1% inside the registered
    # 2% projected gate so telemetry granularity cannot knife-edge the gate
    # (skeptic-4 finding 11).
    sel = {c: tel["cells"].get(c, {}).get("sel", 0) for c in universe()}
    freq_order = sorted(universe(), key=lambda c: (sel[c],) + cell_key(c))
    bldf_cells, io_bldf = greedy_fill(freq_order, cost, io_semd, 0.99, 1.01)
    if io_bldf < io_semd * (1 - MATCH_TOL):
        die("ERR_S4_BLIND_MATCH", "s4-bldf-d cannot reach the semantic removed-I/O "
            "within tolerance (%.3g < %.3g)" % (io_bldf, io_semd * (1 - MATCH_TOL)))
    bldf = {c: "DROP" for c in bldf_cells}
    # PRODUCTION-PATH identity refusal (review finding B4): a blind mask equal
    # to s4-semd makes the matched primary contrast vacuous (d_i == 0 always).
    if set(bldf) == set(semd):
        die("ERR_S4_MASK_IDENTICAL", "s4-bldf-d selected exactly the s4-semd cell set "
            "(%d cells) — the primary contrast would be vacuous" % len(bldf))

    # --- s4-bldr-d-r1..r3: cost-proportional random blind --------------------
    positive = [c for c in sorted(cost, key=cell_key) if cost[c] > 0]
    weights = [cost[c] for c in positive]
    bldr = []
    for seed in BLIND_SEEDS:
        gen = drbg_ints(seed, 1 << 62)
        chosen, tot, avail, w = [], 0.0, list(positive), list(weights)
        lo, hi_r = io_semd * 0.99, io_semd * 1.01
        guard = 0
        while tot < lo:
            guard += 1
            if not avail or guard > 500000:
                die("ERR_S4_BLIND_MATCH", "random blind (seed %d) exhausted the pool "
                    "below the matching window" % seed)
            total_w = sum(w)
            r = (next(gen) / float(1 << 62)) * total_w
            acc, k = 0.0, 0
            for k, wk in enumerate(w):
                acc += wk
                if acc >= r:
                    break
            c = avail.pop(k); wk = w.pop(k)
            if tot + wk > hi_r:
                continue  # skip-if-overshoot; cell stays excluded (drawn without replacement)
            chosen.append(c); tot += wk
        if set(chosen) == set(semd):
            die("ERR_S4_MASK_IDENTICAL", "random blind (seed %d) selected exactly the "
                "s4-semd cell set — the arm would be vacuous" % seed)
        # skeptic-5 R2 finding 5: refuse mutual identity too (bldf and every
        # earlier realization) — degenerate draws fail closed in production.
        if set(chosen) == set(bldf_cells):
            die("ERR_S4_MASK_IDENTICAL", "random blind (seed %d) selected exactly the "
                "s4-bldf-d cell set" % seed)
        for prev, _, prev_seed in bldr:
            if set(chosen) == set(prev):
                die("ERR_S4_MASK_IDENTICAL", "random blinds (seeds %d, %d) selected "
                    "identical cell sets" % (prev_seed, seed))
        bldr.append(({c: "DROP" for c in chosen}, tot, seed))

    audit = {
        "tier": tel["tier"], "decode_tokens": tel["decode_tokens"],
        "total_expert_miss_bytes_per_tok": total_io,
        "dose_frac_target": DOSE_FRAC, "match_tol": MATCH_TOL,
        "io_min_frac": IO_MIN_FRAC, "pass_dose_frac": PASS_DOSE_FRAC,
        "dose_capped": dose_capped,
        "construction_kill": None,
        "arms": {
            "s4-sem16": {"cells": len(sem16), "removed_bytes_per_tok": io_sem16,
                          "removed_frac": io_sem16 / total_io},
            "s4-remap16": {"cells": len(remap16), "removed_bytes_per_tok": io_sem16,
                            "removed_frac": io_sem16 / total_io,
                            "swaps": sum(1 for v in remap16.values() if v.startswith("SWAP"))},
            "s4-semd": {"cells": len(semd), "removed_bytes_per_tok": io_semd,
                         "removed_frac": io_semd / total_io,
                         "tier0_used": sum(1 for c in semd if c in set(tier0)),
                         "tier1_used": sum(1 for c in semd if c in set(tier1))},
            "s4-bldf-d": {"cells": len(bldf), "removed_bytes_per_tok": io_bldf,
                           "removed_frac": io_bldf / total_io,
                           "match_rel_err": abs(io_bldf - io_semd) / io_semd},
        },
    }
    for (m, tot, seed), i in zip(bldr, range(1, 4)):
        audit["arms"]["s4-bldr-d-r%d" % i] = {
            "cells": len(m), "removed_bytes_per_tok": tot,
            "removed_frac": tot / total_io, "seed": seed,
            "match_rel_err": abs(tot - io_semd) / io_semd}

    masks = {"s4-sem16": sem16, "s4-remap16": remap16, "s4-semd": semd, "s4-bldf-d": bldf}
    for (m, _, _), i in zip(bldr, range(1, 4)):
        masks["s4-bldr-d-r%d" % i] = m
    return masks, audit


def serialize(arm: str, mask: dict, input_shas: dict) -> bytes:
    lines = ["# kot-s4mask/1 arm=%s" % arm,
             "# params dose_frac=%s match_tol=%s io_min_frac=%s" % (DOSE_FRAC, MATCH_TOL, IO_MIN_FRAC),
             "# inputs telemetry=%s stage3=%s atlas=%s" % (
                 input_shas["telemetry"], input_shas["stage3"], input_shas["atlas"]),
             "# builder=poc/glm52-probe/stage4/build_masks.py"]
    for cell in sorted(mask, key=cell_key):
        lines.append("%s %s" % (cell, mask[cell]))
    return ("\n".join(lines) + "\n").encode("ascii", "strict")


def run(telemetry_path, stage3_path, atlas_path, outdir):
    tel = load_telemetry(telemetry_path)
    skip, safe_non_skip, excluded = load_stage3(stage3_path)
    atlas_classes = load_atlas_classes(atlas_path)
    masks, audit = build_masks(tel, skip, safe_non_skip, excluded, atlas_classes)
    input_shas = {"telemetry": sha256_file(telemetry_path),
                  "stage3": sha256_file(stage3_path),
                  "atlas": sha256_file(atlas_path)}
    os.makedirs(outdir, exist_ok=True)
    manifest = {"_schema": "kot-s4mask-manifest/1", "inputs": input_shas,
                "audit": audit, "files": {}}
    for arm in sorted(masks):
        blob = serialize(arm, masks[arm], input_shas)
        path = os.path.join(outdir, arm + ".mask")
        with open(path, "wb") as f:
            f.write(blob)
        manifest["files"][arm + ".mask"] = hashlib.sha256(blob).hexdigest()
    mblob = json.dumps(manifest, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    with open(os.path.join(outdir, "masks_manifest.json"), "w", encoding="utf-8") as f:
        f.write(mblob)
    print(json.dumps({"manifest_sha256": hashlib.sha256(mblob.encode()).hexdigest(),
                      "audit": audit}, indent=1, sort_keys=True))


# --------------------------------------------------------------- selftest
def selftest():
    """Green mock on synthetic fixtures: exercises tier ordering, exclusions,
    dose targeting, blind matching, cap + fail-closed branches, and
    byte-determinism, without any real telemetry."""
    import tempfile
    tmp = tempfile.mkdtemp(prefix="s4mask-selftest-")

    # Synthetic stage3: 4-cell skiplist (2 swappable), 1 SAFE-non-skip,
    # 1 LOAD-BEARING + 1 CHARACTERISE-MORE to exclude.
    s3 = {"skiplist_size": 4, "skiplist": [
            {"cell": "main|3|1", "swap_to": 7, "causal_confidence": 0.8},
            {"cell": "main|3|2", "swap_to": None, "causal_confidence": 0.7},
            {"cell": "main|4|1", "swap_to": 9, "causal_confidence": 0.6},
            {"cell": "main|4|2", "swap_to": None, "causal_confidence": 0.51}],
          "experts": [
            {"cell": "main|3|1", "label": "SAFE-TO-DROP", "causal_confidence": 0.8},
            {"cell": "main|3|2", "label": "SAFE-TO-DROP", "causal_confidence": 0.7},
            {"cell": "main|4|1", "label": "SAFE-TO-DROP", "causal_confidence": 0.6},
            {"cell": "main|4|2", "label": "SAFE-TO-DROP", "causal_confidence": 0.51},
            {"cell": "main|5|1", "label": "SAFE-TO-DROP", "causal_confidence": 0.4},
            {"cell": "main|5|2", "label": "LOAD-BEARING", "causal_confidence": 0.9},
            {"cell": "main|5|3", "label": "CHARACTERISE-MORE", "causal_confidence": 0.5}]}
    # Synthetic atlas: everything rare except two 'stable' cells.
    atl = {"index": {}}
    for L in range(3, 8):
        for E in range(0, 12):
            atl["index"]["main|%d|%d" % (L, E)] = {"label_class": "rare"}
    atl["index"]["main|6|1"] = {"label_class": "stable"}
    atl["index"]["main|6|2"] = {"label_class": "stable"}
    # Synthetic telemetry, tier M: skiplist cells carry modest I/O; a rare
    # tail carries the bulk; excluded cells carry big I/O (must not be taken).
    cells = {}
    for L in range(3, 8):
        for E in range(0, 12):
            c = "main|%d|%d" % (L, E)
            # cost DECORRELATED from sel so the ascending-frequency fill always
            # has small cells available at the window tail (granularity guard)
            cells[c] = {"sel": 5 * (E + 1) + L, "bytes": 19000000,
                        "miss_bytes": 19000000 * (((E * 7 + L) % 13) + 1)}
    cells["main|5|2"]["miss_bytes"] = 19000000 * 400   # LOAD-BEARING, excluded from SEM
    cells["main|5|3"]["miss_bytes"] = 19000000 * 300   # CHARACTERISE-MORE, excluded from SEM
    cells["main|7|11"] = {"sel": 0, "bytes": 19000000, "miss_bytes": 0}  # zero-cost: never fillable
    # layer 78 is a VALID MoE layer (ASM-2342: 76 layers, 3..78; review finding C1):
    # atlas-absent, lowest nonzero sel + modest cost, so the ascending-frequency
    # blind fill MUST price and take it (proves layer 78 is mask-eligible).
    cells["main|78|3"] = {"sel": 1, "bytes": 19000000, "miss_bytes": 19000000 * 3}
    tel = {"_schema": "kot-s4tel/1", "tier": "M", "decode_tokens": 1000, "cells": cells}

    paths = {}
    for name, obj in (("tel", tel), ("s3", s3), ("atl", atl)):
        p = os.path.join(tmp, name + ".json")
        json.dump(obj, open(p, "w"))
        paths[name] = p

    tel2 = load_telemetry(paths["tel"])
    skip, sns, excl = load_stage3(paths["s3"])
    classes = load_atlas_classes(paths["atl"])
    masks, audit = build_masks(tel2, skip, sns, excl, classes)

    checks = []

    def ck(name, cond):
        checks.append((name, bool(cond)))

    ck("sem16 is exactly the skiplist", set(masks["s4-sem16"]) ==
       {"main|3|1", "main|3|2", "main|4|1", "main|4|2"})
    ck("remap16 swaps where swap_to set", masks["s4-remap16"]["main|3|1"] == "SWAP 7"
       and masks["s4-remap16"]["main|3|2"] == "DROP")
    semd = masks["s4-semd"]
    ck("semd contains tier0 first", all(c in semd for c in ("main|3|1",)))
    ck("semd excludes LOAD-BEARING", "main|5|2" not in semd)
    ck("semd excludes CHARACTERISE-MORE", "main|5|3" not in semd)
    ck("semd excludes atlas-stable", "main|6|1" not in semd and "main|6|2" not in semd)
    a = audit["arms"]
    ck("semd dose in window", abs(a["s4-semd"]["removed_frac"] - DOSE_FRAC) <= DOSE_FRAC * MATCH_TOL
       or audit["dose_capped"])
    ck("bldf matched within tol", a["s4-bldf-d"]["match_rel_err"] <= MATCH_TOL)
    for i in (1, 2, 3):
        ck("bldr r%d matched within tol" % i,
           a["s4-bldr-d-r%d" % i]["match_rel_err"] <= MATCH_TOL)
    ck("blind arms differ from semd", set(masks["s4-bldf-d"]) != set(semd))
    ck("random realizations differ", set(masks["s4-bldr-d-r1"]) != set(masks["s4-bldr-d-r2"]))
    ck("zero-cost cell never enters any dose mask",
       all("main|7|11" not in masks[a] for a in
           ("s4-semd", "s4-bldf-d", "s4-bldr-d-r1", "s4-bldr-d-r2", "s4-bldr-d-r3")))
    ck("universe spans 76 MoE layers 3..78 (ASM-2342, review C1)",
       len(universe()) == 76 * 256 and "main|78|255" in universe())
    ck("layer-78 cell is priced and mask-eligible", "main|78|3" in masks["s4-bldf-d"])

    # Byte-determinism: rebuild and compare serializations.
    masks_b, audit_b = build_masks(tel2, skip, sns, excl, classes)
    shas_a = {arm: hashlib.sha256(serialize(arm, m, {"telemetry": "x", "stage3": "y",
              "atlas": "z"})).hexdigest() for arm, m in masks.items()}
    shas_b = {arm: hashlib.sha256(serialize(arm, m, {"telemetry": "x", "stage3": "y",
              "atlas": "z"})).hexdigest() for arm, m in masks_b.items()}
    ck("byte-deterministic rebuild", shas_a == shas_b and audit == audit_b)

    # Fail-closed branches (each must die with the named code).
    import subprocess
    def expect_fail(mutate, code):
        bad = json.loads(json.dumps(tel))
        mutate(bad)
        p = os.path.join(tmp, "bad.json")
        json.dump(bad, open(p, "w"))
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--telemetry", p,
                            "--stage3", paths["s3"], "--atlas", paths["atl"],
                            "--out", os.path.join(tmp, "out-bad")],
                           capture_output=True, text=True)
        return r.returncode != 0 and code in r.stderr

    ck("rejects wrong schema", expect_fail(lambda t: t.update(_schema="nope"), "ERR_S4_TEL_SCHEMA"))
    ck("rejects bad tier", expect_fail(lambda t: t.update(tier="X"), "ERR_S4_TEL_TIER"))
    ck("rejects zero tokens", expect_fail(lambda t: t.update(decode_tokens=0), "ERR_S4_TEL_TOKENS"))
    ck("rejects missing miss_bytes in tier M",
       expect_fail(lambda t: t["cells"]["main|3|1"].pop("miss_bytes"), "ERR_S4_TEL_CELLS"))
    ck("rejects malformed cell id",
       expect_fail(lambda t: t["cells"].update({"mtp|78|1": {"sel": 1, "bytes": 1, "miss_bytes": 1}}),
                   "ERR_S4_TEL_CELLS"))
    ck("rejects zero total I/O",
       expect_fail(lambda t: [t["cells"][c].update(miss_bytes=0) for c in t["cells"]],
                   "ERR_S4_TEL_TOTAL"))

    # Degenerate-instrument branches (cross-model review 2026-07-16, finding B4).
    # (a) ZERO achievable dose (only EXCLUDED cells carry I/O => io_semd == 0):
    #     must emit a REGISTERED construction-kill manifest (exit 0, no blind
    #     arms), never a division-by-zero crash.
    tel_zero = json.loads(json.dumps(tel))
    for c in tel_zero["cells"]:
        tel_zero["cells"][c]["miss_bytes"] = 0
    tel_zero["cells"]["main|5|2"]["miss_bytes"] = 19000000 * 400   # LOAD-BEARING only
    pz = os.path.join(tmp, "tel-zero.json")
    json.dump(tel_zero, open(pz, "w"))
    outdir_z = os.path.join(tmp, "out-zero")
    rz = subprocess.run([sys.executable, os.path.abspath(__file__), "--telemetry", pz,
                         "--stage3", paths["s3"], "--atlas", paths["atl"], "--out", outdir_z],
                        capture_output=True, text=True)
    man_z = {}
    mz_path = os.path.join(outdir_z, "masks_manifest.json")
    if rz.returncode == 0 and os.path.isfile(mz_path):
        man_z = json.load(open(mz_path))
    ck_kill = ((man_z.get("audit") or {}).get("construction_kill") or {})
    ck("zero achievable dose => registered construction-kill, not a crash",
       rz.returncode == 0 and ck_kill.get("fired") is True
       and ck_kill.get("reason") == "dose-zero"
       and "s4-bldf-d.mask" not in (man_z.get("files") or {}))
    # (b) blind mask identical to s4-semd (only the tier-0 cells carry positive
    #     cost; no tier-1 cell exists): fail-closed refusal in the build path.
    s3_id = {"skiplist_size": 4, "skiplist": s3["skiplist"],
             "experts": [e for e in s3["experts"] if e["cell"] != "main|5|1"]}
    tel_id = json.loads(json.dumps(tel))
    for c in tel_id["cells"]:
        tel_id["cells"][c]["miss_bytes"] = 0
    for cell, _, _ in skip:
        tel_id["cells"][cell]["miss_bytes"] = 19000000
    pi = os.path.join(tmp, "tel-ident.json")
    json.dump(tel_id, open(pi, "w"))
    ps3 = os.path.join(tmp, "s3-ident.json")
    json.dump(s3_id, open(ps3, "w"))
    ri = subprocess.run([sys.executable, os.path.abspath(__file__), "--telemetry", pi,
                         "--stage3", ps3, "--atlas", paths["atl"], "--out",
                         os.path.join(tmp, "out-ident")], capture_output=True, text=True)
    ck("identical blind/semd cell set refused fail-closed",
       ri.returncode != 0 and "ERR_S4_MASK_IDENTICAL" in ri.stderr)

    failed = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print(("PASS " if ok else "FAIL ") + n)
    if failed:
        print("selftest: %d/%d FAILED" % (len(failed), len(checks)))
        sys.exit(1)
    print("selftest: %d/%d PASS" % (len(checks), len(checks)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--telemetry"); ap.add_argument("--stage3"); ap.add_argument("--atlas")
    ap.add_argument("--out"); ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest(); return
    if not all([args.telemetry, args.stage3, args.atlas, args.out]):
        die("ERR_S4_ARGS", "--telemetry/--stage3/--atlas/--out are all required")
    run(args.telemetry, args.stage3, args.atlas, args.out)


if __name__ == "__main__":
    main()
