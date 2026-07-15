#!/usr/bin/env python3
"""screen.py — F1-K/K-3 askability + coverage screen ($0, blind).

Executes sol's 4-part executable spec
(docs/next/design/f1k-askability-screen-sol-20260715.md): a model-outcome-
BLIND and gold-label-BLIND feasibility GATE that decides whether the deciding
four-condition kernel-vs-generic CORRECTNESS experiment (F1-K rungs K-1/K-2/
K-3) is even BUILDABLE, BEFORE any explication authoring or GPU spend.

  Part 1  Pool + selection   — redacted-input allowlist scan of the 5 pinned
                               benchmarks x WordNet-3.1, join existing kernel
                               records, dedup by synset, retention filter,
                               rank, select 96 + a 30-reserve.  Freeze the
                               redacted-input hash + rules BEFORE screening.
  Part 2  Contrast (cond iv) — emit kernel.txt / kernel.ast.json (JCS) /
                               matched dictionary.txt per concept, render both
                               through the PRODUCTION prepend renderer on every
                               assigned item, CERTIFY hashes differ, NLD>=0.20,
                               prompt-hash-diff-rate == 1.00, outside-payload
                               diff == 0.
  Part 3  Coverage/power     — for every frozen prefix C in [65, min(100,
                               C_contrast)] allocate dev-96 + test to m=8 /
                               n=1440, run the K-1/K-2/K-3 EXACT sign-flip
                               power sim (N_sim=10000, delta=rho_U=0.10,
                               mu*=0.0409, seed 20260713, b=10000 add-one
                               corrected flips, fire p<0.05 AND T>=0.03,
                               R=1,3,1); require power >= 0.80 for every
                               contrast.
  Part 4  Verdict            — ASKABLE iff 80<=C<=100 AND every m_c>=8 AND all
                               pass contrast AND all 3 power gates pass; else
                               NEEDS-MORE-INVENTORY / NOT-ASKABLE-AT-SCALE.

REUSED (frozen) MACHINERY (every rule cites its source):
  [BC]  poc/glm52-probe/f1k-harness/corpora/build_corpora.py — WN3.1 dict
        parse, trigger surface expansion (synset lemmas + '+'-pointer
        derivational lemmas), §R4 overlap resolution, the §R1.1 scored
        template renderer, and the production d3-text PREPEND rule
        (payload + '\\n\\n' + template; [BC] OP-9).
  [SC]  poc/scale/f1k-eligibility/screen_candidates.py — the $0 benchmark-
        blind WordNet screen this extends (28,818 m>=8 candidates measured).
  [KV0] data/kernel-v0/  (54 concepts; gloss = NSM explication + kot-ast/1)
        + data/lexical-wn31/alignment-kernel-v0.json (kernel-v0 -> WN synset).
  [KV1] data/kernel-v1/  (100 concepts; gloss + kot-ast/1 + INLINE synset).
  [WN]  data/lexical-wn31/source/dict/  (WordNet 3.1 source; the matched
        dictionary gloss for each synset).
  [EV]  data/f1k-eval-v1/source/*.parquet — the 5 pinned benchmark snapshots,
        sha256-verified against [BC] SOURCES (fail closed).
  [REG] registry/experiments/f1k.json — K-1/K-2/K-3 endpoints, joint rule
        (lift >= +3 pts AND cluster sign-flip p < 0.05), power gate C>=65 each
        m>=8 at n=1440, SEED 20260713, B=10000. READ ONLY.
  [DES] docs/next/design/glm52-followup-experiment.md §R-REV5 — the frozen
        pre-spend Monte-Carlo EXACT-test joint-power procedure (mu*=+4.09 pts,
        rho_U=0.10, exchangeable within-cluster correlation, pass iff >=0.80).

BLIND / $0 GOVERNANCE: the screen reads item TEXT only. Gold indices pass
through the SAME well-formedness admission as [BC] (an item-admission rule,
not an outcome) and are DROPPED from the redacted view before any ranking,
selection, contrast, coverage or power step. No model call, no logit, no
accuracy, no prediction, no K/pilot/derangement field is ever read. No GPU,
no network, no spend, no git/registry/freeze. Deterministic: byte-identical
outputs on re-run (the only PRNG is the registered power seed 20260713).
colibri naming; no handles.
"""

import hashlib
import json
import os
import sys
import unicodedata
from array import array
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                        # repo root (kernel-of-truth/)

# reuse [BC] frozen machinery
sys.path.insert(0, str(ROOT / "poc" / "glm52-probe" / "f1k-harness" / "corpora"))
sys.path.insert(0, str(ROOT / "tools" / "registry"))
import build_corpora as bc                    # [BC] parse/triggers/spans/render
import kot_common as kc                       # JCS canonical bytes (kernel.ast.json)

PASS_STAMP = "2026-07-15 designer-31 f1k-askability screen ($0, blind)"  # fixed text, not wall-clock

# ---- frozen constants (cited) ---------------------------------------------
DEV_N = 96                 # [REG n_planned.dev_split_items]
N_TEST = 1440              # [REG n_planned.n_test_items — runs AT the cap]
POWER_GATE_MIN_M = 8       # [REG power_gate]
SELECT_N = 96              # [SPEC 1] select 96
RESERVE_N = 30             # [SPEC 1] retain the next 30 as a fixed reserve
NLD_MIN = 0.20             # [SPEC 2] distinctness bar
C_LO, C_HI = 80, 100       # [SPEC 4] ASKABLE band on the operating C
PREFIX_LO = 65             # [SPEC 3] sweep from the registered power gate C>=65

# power-sim constants [DES §R-REV5 / REG statistics]
POWER_SEED = 20260713      # [REG statistics global PRNG seed]
N_SIM = 10000              # [DES §R-REV5 N_sim]
B_FLIP = 10000             # [REG B / DES §R-REV5: 10,000 sign-flips]
DELTA = 0.10               # [DES §R-REV4.1(b): per-item paired-diff variance]
RHO_U = 0.10               # [DES §R-REV5: conservative planning rho_U]
MU_STAR = 0.0409           # [DES §R-REV4.1(b): mu* = +4.09 pts]
T_FIRE = 0.03              # [REG joint rule: observed lift >= +3.0 pts]
POWER_MIN = 0.80           # [DES §R-REV5 pass threshold]
# R = number of deflator/comparator passes per rung [REG endpoints]:
#   K-1 (K vs b0)                     R=1
#   K-2 (K vs mean over R=3 drng)     R=3
#   K-3 (K vs d2 plain dictionary)    R=1
CONTRASTS = [("K-1", 1), ("K-2", 3), ("K-3", 1)]

ERR = "ERR_F1K_ASK"


def fail(msg):
    print("%s: %s" % (ERR, msg), file=sys.stderr)
    sys.exit(2)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def write_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")


def write_text(path, text):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(text if isinstance(text, bytes) else text.encode("utf-8"))


def slug_of(urn):
    return urn.split(":")[-1].replace("/", "_")


# ---------------------------------------------------------------------------
# Levenshtein + NLD (NFC-normalised) [SPEC 2]
# ---------------------------------------------------------------------------
def levenshtein(a, b):
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1,
                           prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def nld(k, d):
    """NLD_c = Lev(NFC(K), NFC(D)) / max(|K|, |D|)  [SPEC 2]."""
    kn = unicodedata.normalize("NFC", k)
    dn = unicodedata.normalize("NFC", d)
    denom = max(len(kn), len(dn))
    if denom == 0:
        return 0.0
    return levenshtein(kn, dn) / denom


# ---------------------------------------------------------------------------
# Existing-kernel record join (kernel-v0 + kernel-v1) [SPEC 1 / KV0,KV1]
# ---------------------------------------------------------------------------
def ast_parseable(expl):
    """A kot-ast/1 explication is 'parseable' iff it is a JSON object bearing
    schema 'kot-ast/1', carries a non-empty clause list, and JCS-canonicalises
    without error (the exact bytes kernel.ast.json will ship)."""
    if not isinstance(expl, dict) or expl.get("schema") != "kot-ast/1":
        return False, None
    if not isinstance(expl.get("clauses"), list) or not expl["clauses"]:
        return False, None
    try:
        ast_bytes = kc.canonical_bytes(expl)
    except Exception:
        return False, None
    return True, ast_bytes


def load_kernel_records():
    """kernel-v0 (via alignment) + kernel-v1 (inline synset), deduped by
    synset (v1 preferred on any collision; disjoint in fact). Each record:
    urn, label, kernel gloss, kot-ast/1 explication, WN synset."""
    recs = []
    # kernel-v0: synset from the hand-reviewed alignment [KV0]
    align = json.load(open(ROOT / "data" / "lexical-wn31" /
                           "alignment-kernel-v0.json", encoding="utf-8"))
    v0syn = {a["concept"]: a["synset"] for a in align["alignments"]
             if a["concept"].startswith("urn:kernel-v0:")}
    cdir = ROOT / "data" / "kernel-v0" / "concepts"
    for fn in sorted(os.listdir(cdir)):
        d = json.load(open(cdir / fn, encoding="utf-8"))
        recs.append({"urn": d["id"], "label": d.get("label", ""),
                     "gloss": d.get("gloss", ""),
                     "explication": d.get("explication"),
                     "synset": v0syn.get(d["id"]), "source": "kernel-v0"})
    # kernel-v1: inline synset [KV1]
    cdir = ROOT / "data" / "kernel-v1" / "concepts"
    for fn in sorted(os.listdir(cdir)):
        d = json.load(open(cdir / fn, encoding="utf-8"))
        recs.append({"urn": d["id"], "label": d.get("label", ""),
                     "gloss": d.get("gloss", ""),
                     "explication": d.get("explication"),
                     "synset": d.get("synset"), "source": "kernel-v1"})
    # dedup by synset (deterministic: kernel-v1 wins, else lowest urn)
    by_syn = {}
    dup = 0
    for r in sorted(recs, key=lambda r: (0 if r["source"] == "kernel-v1"
                                         else 1, r["urn"])):
        s = r["synset"]
        if not s:
            continue
        if s in by_syn:
            dup += 1
            continue
        by_syn[s] = r
    return list(by_syn.values()), len(recs), dup


# ---------------------------------------------------------------------------
# Redacted benchmark loader [SPEC 1 / EV / BC admission]
#   returns the REDACTED view {item_id, source, question, options} only.
#   Gold is used for the [BC] well-formedness admission then DROPPED.
# ---------------------------------------------------------------------------
def load_items_redacted():
    import pyarrow.parquet as pq
    src_dir = ROOT / "data" / "f1k-eval-v1" / "source"
    items = []
    for rank, (key, ds, rev, path, want, split) in enumerate(bc.SOURCES):
        p = src_dir / ("%s.parquet" % key)
        if not p.exists():
            fail("pinned snapshot %s missing" % p)
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        if h.hexdigest() != want:
            fail("source %s sha256 mismatch vs [BC] pin — STOP" % key)
        rows = pq.read_table(p).to_pylist()
        for ri, r in enumerate(rows):
            if key == "mmlu":
                q = r["question"].strip()
                opts = [o.strip() for o in r["choices"]]
                gold = int(r["answer"])          # ADMISSION ONLY
                native = "%s/%d" % (r["subject"], ri)
            else:
                q = (r.get("question") or r.get("question_stem")).strip()
                ch = r["choices"]
                opts = [o.strip() for o in ch["text"]]
                labels_pub = list(ch["label"])
                if r["answerKey"] not in labels_pub:
                    continue
                gold = labels_pub.index(r["answerKey"])   # ADMISSION ONLY
                native = str(r["id"])
            if not (3 <= len(opts) <= 5) or not (0 <= gold < len(opts)):
                continue                          # [BC] well-formedness
            # gold DROPPED here — never stored on the redacted item
            items.append({"item_id": "%s#%s" % (key, native),
                          "source": key, "source_rank": rank, "row_index": ri,
                          "question": q, "options": opts})
    return items


# ---------------------------------------------------------------------------
# §R4 span helpers over an arbitrary concept subset [BC]
# ---------------------------------------------------------------------------
def raw_candidates(text, matchers):
    """All trigger matches (start, end, concept_index), UNRESOLVED [BC]."""
    low = text.lower()
    words = set(bc.WORD_RE.findall(low))
    cand = []
    for w in words:
        for ph, rx, cidx in matchers.get(w, ()):
            if ph.split()[0] != w:
                continue
            for m in rx.finditer(text):
                cand.append((m.start(), m.end(), cidx))
    return cand


def resolve(cands, allowed):
    """§R4 precedence over the cands whose concept is in `allowed`: longest,
    then earliest start, then lowest concept index; non-overlapping. Returns
    spans sorted by start. [BC find_spans]"""
    cand = [c for c in cands if c[2] in allowed]
    cand.sort(key=lambda s: (-(s[1] - s[0]), s[0], s[2]))
    taken, out = [], []
    for s in cand:
        if any(not (s[1] <= t[0] or s[0] >= t[1]) for t in taken):
            continue
        taken.append(s)
        out.append(s)
    out.sort(key=lambda s: s[0])
    return out


# ---------------------------------------------------------------------------
# Cluster allocation (dev-96 + test to m=8 / n=1440) over a prefix [BC OP-6]
# ---------------------------------------------------------------------------
def allocate(prefix_cidx, item_cands, items, q_end):
    """prefix_cidx: ordered list of concept indices (selection-rank order).
    Returns realized test m_c per concept index and dev counts.
    Mirrors [BC build_splits]: dev round-robin (>=1/cluster) first, then test
    filled breadth-first to m=8, then round-robin to the cap."""
    allowed = set(prefix_cidx)
    by_cluster = {c: [] for c in prefix_cidx}
    for ii, it in enumerate(items):
        cands = item_cands.get(ii)
        if not cands:
            continue
        spans = resolve(cands, allowed)
        if not spans:
            continue
        cluster = spans[0][2]                     # [BC OP-6a] leftmost resolved
        stem = spans[0][0] < q_end[ii]
        by_cluster[cluster].append((0 if stem else 1, it["source_rank"],
                                    it["row_index"], ii))
    for c in by_cluster:
        by_cluster[c].sort()                      # stem-first, source, row
    used = {c: 0 for c in prefix_cidx}

    def take(c):
        if used[c] < len(by_cluster[c]):
            used[c] += 1
            return True
        return False

    # dev-96 round-robin over prefix order
    dev = {c: 0 for c in prefix_cidx}
    ndev = 0
    while ndev < DEV_N:
        progressed = False
        for c in prefix_cidx:
            if ndev >= DEV_N:
                break
            if take(c):
                dev[c] += 1
                ndev += 1
                progressed = True
        if not progressed:
            break
    # test: breadth-first to m=8, then round-robin to N_TEST
    test = {c: 0 for c in prefix_cidx}
    ntest = 0
    for _ in range(POWER_GATE_MIN_M):
        for c in prefix_cidx:
            if ntest >= N_TEST:
                break
            if take(c):
                test[c] += 1
                ntest += 1
    progressing = True
    while ntest < N_TEST and progressing:
        progressing = False
        for c in prefix_cidx:
            if ntest >= N_TEST:
                break
            if take(c):
                test[c] += 1
                ntest += 1
                progressing = True
    return test, dev, ntest, ndev


# ---------------------------------------------------------------------------
# EXACT cluster sign-flip Monte-Carlo joint-power sim [DES §R-REV5]
# ---------------------------------------------------------------------------
def _seed(contrast, C):
    h = hashlib.sha256(("%d|%s|C%d" % (POWER_SEED, contrast, C)).encode())
    return int(h.hexdigest()[:16], 16)


def power_curve(m_list, contrast, mus, chunk=2500):
    """Joint power of the EXACT cluster sign-flip test (fire iff permutation
    p < 0.05 AND observed mean lift T >= +3 pts) at every mu in `mus`, under
    the [DES §R-REV5] exchangeable alternative: per cluster c the cluster mean
    D_c ~ N(mu, delta*(rho + (1-rho)/m_c)) (the exchangeable within-cluster
    correlation rho_U=0.10 enters exactly as this cluster-mean variance;
    SE^2 = (delta/C^2) sum_c[rho + (1-rho)/m_c], matching the registered
    planning model). The sign-flip acts on cluster means, so the cluster-mean
    law is the exact sufficient DGP. N_sim=10000 synthetic datasets; a single
    frozen b=10000-row +-1 sign-flip reference matrix per (contrast, C) is the
    exact licensing code path (the licensing test itself uses ONE deterministic
    sign-flip set, seeded 'SEED|name') applied with common random numbers
    across datasets (variance-reduction; the joint-power estimate is unbiased).
    add-one p = (1+ge)/(B+1); p<0.05  <=>  ge <= 499 at B=10000."""
    C = len(m_list)
    v = DELTA * (RHO_U + (1.0 - RHO_U) / np.asarray(m_list, dtype=np.float64))
    sd = np.sqrt(v)
    rng = np.random.default_rng(_seed(contrast, C))
    noise = rng.standard_normal((N_SIM, C)) * sd[None, :]     # (N_sim, C)
    noise_mean = noise.mean(axis=1)                           # (N_sim,)
    Z = (rng.integers(0, 2, size=(B_FLIP, C), dtype=np.int8).astype(np.float64)
         * 2.0 - 1.0)                                         # (B, C) +-1
    rowsum = Z.sum(axis=1)                                    # (B,)
    ge_cut = 499                   # (1+ge)/(B+1) < 0.05 <=> ge <= 499 at B=1e4
    fire = {mu: 0 for mu in mus}
    for start in range(0, N_SIM, chunk):
        end = min(start + chunk, N_SIM)
        nz = noise[start:end]                                 # (cs, C)
        zn = Z @ nz.T                                         # (B, cs)
        nm = noise_mean[start:end]                            # (cs,)
        for mu in mus:
            tb = (mu * rowsum[:, None] + zn) / C              # (B, cs)
            tobs = mu + nm                                    # (cs,)
            ge = (tb >= tobs[None, :]).sum(axis=0)            # (cs,)
            fired = (ge <= ge_cut) & (tobs >= T_FIRE)
            fire[mu] += int(fired.sum())
    return {mu: fire[mu] / N_SIM for mu in mus}


def mde_from_curve(mus, curve):
    """Smallest mu whose joint power >= 0.80, linearly interpolated between the
    bracketing grid points. None if the grid never reaches 0.80."""
    ordered = sorted(mus)
    prev_mu, prev_p = None, None
    for mu in ordered:
        p = curve[mu]
        if p >= POWER_MIN:
            if prev_mu is None or prev_p is None or prev_p >= POWER_MIN:
                return mu
            frac = (POWER_MIN - prev_p) / (p - prev_p)
            return prev_mu + frac * (mu - prev_mu)
        prev_mu, prev_p = mu, p
    return None


# ===========================================================================
def main():
    print("=" * 72)
    print("F1-K/K-3 askability + coverage screen ($0, blind) — %s" % PASS_STAMP)
    print("=" * 72)

    # ---------------------------------------------------------------------
    # PART 1 — Pool + selection
    # ---------------------------------------------------------------------
    print("\n[PART 1] pool + selection")
    wn = bc.parse_wn_dict()
    recs, n_raw, n_dup = load_kernel_records()
    print("  joined kernel-v0+v1 records: %d raw -> %d synset-deduped "
          "(%d dropped)" % (n_raw, len(recs), n_dup))

    # trigger surface + WN dictionary gloss per record [BC build_triggers]
    bc.build_triggers(recs, wn)

    # retention pre-filter (design-independent, per-concept):
    #   gloss + parseable kot-ast/1 + aligned WN dictionary gloss + triggers
    pool = []
    rej = {"no_gloss": 0, "no_ast": 0, "no_wn_gloss": 0, "no_triggers": 0}
    for r in recs:
        ok, ast_bytes = ast_parseable(r["explication"])
        if not (r["gloss"] and r["gloss"].strip()):
            rej["no_gloss"] += 1
            continue
        if not ok:
            rej["no_ast"] += 1
            continue
        if not (r.get("d2_gloss") and r["d2_gloss"].strip()):
            rej["no_wn_gloss"] += 1
            continue
        if not r["triggers"]:
            rej["no_triggers"] += 1
            continue
        r["ast_bytes"] = ast_bytes
        pool.append(r)
    for i, r in enumerate(pool):
        r["index"] = i
    print("  retention pre-filter: %d records pass gloss+ast+WNgloss+triggers "
          "(rej %s)" % (len(pool), rej))

    matchers = bc.compile_matchers(pool)

    # header/cue/label collision flags [BC §R-REV2.1 / SC SOP-3]
    hdr_cids = set()
    for text in (bc.HEADER, bc.CUE, " ".join(bc.LABEL_ALPHABET)):
        for (_s, _e, cidx) in raw_candidates(text, matchers):
            hdr_cids.add(cidx)
    print("  header/cue/label collisions: %d concepts flagged (excluded)"
          % len(hdr_cids))

    # redacted benchmark items + freeze the redacted-input hash BEFORE screening
    items = load_items_redacted()
    redacted_view = [{"item_id": it["item_id"], "source": it["source"],
                      "question": it["question"], "options": it["options"]}
                     for it in sorted(items, key=lambda x: x["item_id"])]
    redacted_hash = sha256_bytes(kc.canonical_bytes(redacted_view))
    rules = {
        "retention_filter": ["existing kernel gloss", "parseable kot-ast/1",
                             "aligned WordNet dictionary gloss",
                             "clean triggers (>=1, WORD_RE-valid)",
                             "no header/cue/label collision",
                             "projected m_test >= 8"],
        "ranking_keys": ["projected_m_test desc", "exclusive_stem_hits desc",
                         "exclusive_total_hits desc", "collision_fraction asc",
                         "synset_urn_bytes asc"],
        "select_n": SELECT_N, "reserve_n": RESERVE_N,
        "nld_min": NLD_MIN, "power_gate_min_m": POWER_GATE_MIN_M,
        "n_test": N_TEST, "dev_n": DEV_N,
        "prepend_renderer": "payload + '\\n\\n' + [BC §R1.1 template] "
                            "(the production d3-text rule, [BC] OP-9)",
        "power": {"seed": POWER_SEED, "n_sim": N_SIM, "b_flip": B_FLIP,
                  "delta": DELTA, "rho_u": RHO_U, "mu_star": MU_STAR,
                  "t_fire": T_FIRE, "power_min": POWER_MIN,
                  "R_per_contrast": {c: r for c, r in CONTRASTS}},
        "verdict_band_C": [C_LO, C_HI], "prefix_lo": PREFIX_LO,
    }
    rules_hash = sha256_bytes(kc.canonical_bytes(rules))
    print("  redacted-input FROZEN: %d items, hash %s… ; rules hash %s…"
          % (len(items), redacted_hash[:12], rules_hash[:12]))

    # counting pass: raw candidates per item over the pool matcher (once)
    item_cands = {}
    q_end = {}
    for ii, it in enumerate(items):
        tpl = bc.render_template(it["question"], it["options"])
        it["template_text"] = tpl
        q_end[ii] = len(bc.HEADER) + len(it["question"])
        cands = raw_candidates(tpl, matchers)
        if cands:
            item_cands[ii] = cands

    # per-concept raw match / exclusive (§R4 winner over the WHOLE pool) counts
    allowed_all = set(range(len(pool)))
    raw_match = [0] * len(pool)
    excl = [0] * len(pool)
    excl_stem = [0] * len(pool)
    for ii, cands in item_cands.items():
        for (_s, _e, cidx) in cands:
            raw_match[cidx] += 1
        spans = resolve(cands, allowed_all)
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
                                         raw_match[i], 6) if raw_match[i] else 0.0)
        r["projected_m_test"] = excl[i]
        r["header_cue_collision"] = i in hdr_cids

    # retention: projected m_test >= 8 AND header-clean
    survivors = [r for r in pool
                 if r["projected_m_test"] >= POWER_GATE_MIN_M
                 and not r["header_cue_collision"]]
    # rank per [SPEC 1]
    survivors.sort(key=lambda r: (-r["projected_m_test"], -r["excl_stem"],
                                  -r["excl_total"], r["collision_fraction"],
                                  r["synset"].encode("utf-8")))
    for i, r in enumerate(survivors):
        r["rank"] = i + 1
    n_surv = len(survivors)
    selected = survivors[:SELECT_N]
    reserve = survivors[SELECT_N:SELECT_N + RESERVE_N]
    print("  survivors (projected m>=8, header-clean): %d" % n_surv)
    print("  selected: %d ; reserve: %d" % (len(selected), len(reserve)))

    def cand_entry(r):
        return {"rank": r["rank"], "urn": r["urn"], "source": r["source"],
                "label": r["label"], "synset": r["synset"],
                "pos": bc.synset_key(r["synset"])[0],
                "projected_m_test": r["projected_m_test"],
                "raw_match": r["raw_match"], "excl_stem": r["excl_stem"],
                "collision_fraction": r["collision_fraction"],
                "n_triggers": len(r["triggers"])}

    write_json(HERE / "reports" / "candidate-report.json", {
        "part": "1 — pool + selection", "built": PASS_STAMP,
        "spec": "docs/next/design/f1k-askability-screen-sol-20260715.md",
        "kernel_records_joined_raw": n_raw,
        "synset_deduped_records": len(recs),
        "dedup_dropped": n_dup,
        "retention_pre_filter_pass": len(pool),
        "retention_pre_filter_rej": rej,
        "header_cue_collisions_flagged": len(hdr_cids),
        "redacted_items": len(items),
        "survivors_projected_m8_header_clean": n_surv,
        "selected_count": len(selected), "reserve_count": len(reserve),
        "selected": [cand_entry(r) for r in selected],
        "reserve": [cand_entry(r) for r in reserve],
        "source_mix_selected": {k: sum(1 for r in selected if r["source"] == k)
                                for k in ("kernel-v0", "kernel-v1")},
        "MEASURED": "counts are exact over the pinned corpora + benchmarks",
    })

    # ---------------------------------------------------------------------
    # PART 2 — Contrast (condition iv)
    # ---------------------------------------------------------------------
    print("\n[PART 2] contrast / distinctness certification")
    contrast_rows = []
    prompt_pairs_total = 0
    prompt_pairs_diff = 0
    outside_payload_diff_total = 0
    # per concept assigned items = its §R4-winner items over the SELECTED set
    sel_idx = [r["index"] for r in selected + reserve]
    sel_allowed = set(sel_idx)
    assigned = {c: [] for c in sel_idx}
    for ii, cands in item_cands.items():
        spans = resolve(cands, sel_allowed)
        if spans:
            assigned[spans[0][2]].append(ii)

    all_pass = True
    for r in selected + reserve:
        i = r["index"]
        k_text = r["gloss"]
        d_text = r["d2_gloss"]
        ast_bytes = r["ast_bytes"]
        k_bytes = k_text.encode("utf-8")
        d_bytes = d_text.encode("utf-8")
        k_hash = sha256_bytes(k_bytes)
        d_hash = sha256_bytes(d_bytes)
        ast_hash = sha256_bytes(ast_bytes)
        nld_c = nld(k_text, d_text)
        hashes_differ = (k_hash != d_hash)
        # render both through the production prepend renderer on EVERY item
        n_items = 0
        n_diff = 0
        opd = 0
        for ii in assigned[i]:
            tpl = items[ii]["template_text"]
            k_prompt = (k_text + "\n\n" + tpl).encode("utf-8")
            d_prompt = (d_text + "\n\n" + tpl).encode("utf-8")
            n_items += 1
            if sha256_bytes(k_prompt) != sha256_bytes(d_prompt):
                n_diff += 1
            # outside-payload diff: strip the leading payload; the remainder
            # ('\n\n' + template) MUST be byte-identical
            if k_prompt[len(k_bytes):] != d_prompt[len(d_bytes):]:
                opd += 1
        prompt_pairs_total += n_items
        prompt_pairs_diff += n_diff
        outside_payload_diff_total += opd
        phdr = (n_diff / n_items) if n_items else 1.0
        passed = (hashes_differ and nld_c >= NLD_MIN and phdr == 1.0
                  and opd == 0 and n_items > 0)
        r["contrast_pass"] = passed
        if r in selected and not passed:
            all_pass = False
        # emit per-concept artifacts
        d = HERE / "contrast" / ("%03d-%s" % (r["rank"], slug_of(r["urn"])))
        write_text(d / "kernel.txt", k_bytes)
        write_text(d / "kernel.ast.json", ast_bytes)
        write_text(d / "dictionary.txt", d_bytes)
        contrast_rows.append({
            "rank": r["rank"], "urn": r["urn"], "source": r["source"],
            "synset": r["synset"], "in_selected": r in selected,
            "kernel_sha256": k_hash, "kernel_ast_sha256": ast_hash,
            "dictionary_sha256": d_hash, "hashes_differ": hashes_differ,
            "kernel_len": len(k_text), "dictionary_len": len(d_text),
            "NLD_c": round(nld_c, 6), "nld_pass": nld_c >= NLD_MIN,
            "assigned_items": n_items,
            "prompt_hash_diff_rate": round(phdr, 6),
            "outside_payload_diff": opd, "contrast_pass": passed})

    sel_rows = [x for x in contrast_rows if x["in_selected"]]
    nlds = sorted(x["NLD_c"] for x in sel_rows)
    n_contrast_pass = sum(1 for x in sel_rows if x["contrast_pass"])
    C_contrast = n_contrast_pass
    global_phdr = (prompt_pairs_diff / prompt_pairs_total
                   if prompt_pairs_total else 0.0)
    print("  selected concepts passing contrast (C_contrast): %d/%d"
          % (C_contrast, len(sel_rows)))
    print("  NLD over selected: min %.3f  median %.3f  max %.3f"
          % (nlds[0], nlds[len(nlds) // 2], nlds[-1]))
    print("  prompt-hash-diff-rate (all rendered pairs): %.6f ; "
          "outside-payload-diff total: %d"
          % (global_phdr, outside_payload_diff_total))

    write_json(HERE / "reports" / "distinctness-report.json", {
        "part": "2 — contrast (condition iv)", "built": PASS_STAMP,
        "nld_min": NLD_MIN,
        "selected_pass_contrast": C_contrast,
        "selected_total": len(sel_rows),
        "nld_selected": {"min": nlds[0], "median": nlds[len(nlds) // 2],
                         "max": nlds[-1]},
        "nld_pass_rate": round(sum(1 for x in sel_rows
                                   if x["nld_pass"]) / len(sel_rows), 6),
        "concepts": contrast_rows,
        "MEASURED": "exact Levenshtein NLD over NFC-normalised bytes",
    })
    write_json(HERE / "reports" / "hash-report.json", {
        "part": "2 — contrast certification + input freeze", "built": PASS_STAMP,
        "redacted_input_hash_frozen_before_screen": redacted_hash,
        "rules_hash": rules_hash,
        "rules": rules,
        "prepend_renderer": rules["prepend_renderer"],
        "rendered_prompt_pairs_total": prompt_pairs_total,
        "prompt_hash_difference_rate": round(global_phdr, 8),
        "prompt_hash_difference_rate_is_1": global_phdr == 1.0,
        "outside_payload_diff_total": outside_payload_diff_total,
        "outside_payload_diff_is_0": outside_payload_diff_total == 0,
        "all_selected_hashes_differ": all(x["hashes_differ"] for x in sel_rows),
        "certification": ("PASS: hashes differ, NLD>=0.20, prompt-hash-diff-"
                          "rate==1.00, outside-payload-diff==0"
                          if (all_pass and global_phdr == 1.0
                              and outside_payload_diff_total == 0)
                          else "PARTIAL — see distinctness-report.json"),
    })

    # ---------------------------------------------------------------------
    # PART 3 — Coverage / power sweep
    # ---------------------------------------------------------------------
    print("\n[PART 3] coverage + exact-power sweep")
    pass_selected = [r for r in selected if r["contrast_pass"]]
    ranked_cidx = [r["index"] for r in pass_selected]      # rank order
    urn_of_cidx = {r["index"]: r["urn"] for r in pass_selected}
    prefix_hi = min(C_HI, C_contrast)
    # mu-grid brackets the 80%-power crossing (MDE ~0.040-0.048 pts over
    # C in [65,96]); one pass over chunks amortises the expensive ZN matmul
    mu_grid = sorted(set([round(x, 5) for x in np.arange(0.030, 0.05201, 0.002)]
                         + [MU_STAR]))

    coverage_rows = []
    power_rows = []
    smallest_passing = None
    for C in range(PREFIX_LO, prefix_hi + 1):
        prefix = ranked_cidx[:C]
        test, dev, ntest, ndev = allocate(prefix, item_cands, items, q_end)
        m_list = [test[c] for c in prefix]
        m_min = min(m_list)
        m_mean = round(sum(m_list) / C, 4)
        cov_ok = (m_min >= POWER_GATE_MIN_M and ntest == N_TEST)
        coverage_rows.append({
            "C": C, "n_test": ntest, "n_dev": ndev, "m_min": m_min,
            "m_mean": m_mean, "m_max": max(m_list),
            "every_m_ge_8": m_min >= POWER_GATE_MIN_M,
            "coverage_ok": cov_ok})
        prow = {"C": C, "m_min": m_min, "m_mean": m_mean,
                "coverage_ok": cov_ok, "contrasts": {}}
        all3 = cov_ok
        for name, R in CONTRASTS:
            curve = power_curve(m_list, name, mu_grid)
            p_star = curve[MU_STAR]
            mc_se = round((p_star * (1 - p_star) / N_SIM) ** 0.5, 5)
            mde = mde_from_curve(mu_grid, curve)
            prow["contrasts"][name] = {
                "R": R, "power_at_mu_star": round(p_star, 4),
                "mc_se": mc_se,
                "mde_80pct_power": (round(mde, 5) if mde is not None else None),
                "power_ge_0.80": p_star >= POWER_MIN}
            if p_star < POWER_MIN:
                all3 = False
        prow["all_three_power_ge_0.80"] = all3
        prow["prefix_passes"] = all3 and cov_ok
        power_rows.append(prow)
        if prow["prefix_passes"] and smallest_passing is None:
            smallest_passing = C
        print("  C=%2d m_min=%2d m_mean=%5.2f  K-1=%.3f K-2=%.3f K-3=%.3f  "
              "%s" % (C, m_min, m_mean,
                      prow["contrasts"]["K-1"]["power_at_mu_star"],
                      prow["contrasts"]["K-2"]["power_at_mu_star"],
                      prow["contrasts"]["K-3"]["power_at_mu_star"],
                      "PASS" if prow["prefix_passes"] else "-"))

    write_json(HERE / "reports" / "coverage-report.json", {
        "part": "3 — coverage allocation", "built": PASS_STAMP,
        "prefixes": coverage_rows,
        "note": "per prefix C: dev-96 round-robin then test breadth-first to "
                "m=8 then round-robin to n=1440 ([BC] OP-6), realized over the "
                "rank-ordered contrast-passing selected concepts",
    })
    write_json(HERE / "reports" / "power-report.json", {
        "part": "3 — exact sign-flip Monte-Carlo joint power", "built": PASS_STAMP,
        "procedure": "DES §R-REV5 exact cluster sign-flip joint-power sim "
                     "(fire iff perm p<0.05 AND observed lift >=+3 pts)",
        "params": {"seed": POWER_SEED, "n_sim": N_SIM, "b_flip": B_FLIP,
                   "delta": DELTA, "rho_u": RHO_U, "mu_star": MU_STAR,
                   "t_fire_pts": 3.0, "power_min": POWER_MIN,
                   "R_per_contrast": {c: r for c, r in CONTRASTS}},
        "prefix_range": [PREFIX_LO, prefix_hi],
        "C_contrast": C_contrast,
        "smallest_passing_prefix": smallest_passing,
        "prefixes": power_rows,
        "STIPULATED": "R=1,3,1 recorded as rung metadata; all three rungs "
                      "share the registered planning delta=0.10 (the record "
                      "assigns one per-item paired-diff variance to the F1-K "
                      "rungs) — for K-2 (R=3 deflator averaging) this is the "
                      "CONSERVATIVE choice (averaging only lowers variance). "
                      "One frozen b=10000 sign-flip matrix per (contrast,C), "
                      "common random numbers across the 10000 datasets "
                      "(unbiased power estimate).",
        "MEASURED": "Monte-Carlo joint power; MC-SE = sqrt(p(1-p)/N_sim)",
    })

    # ---------------------------------------------------------------------
    # PART 4 — Verdict
    # ---------------------------------------------------------------------
    print("\n[PART 4] verdict")
    # operating C: the smallest passing prefix, lifted into [80,100] if power
    # allows (power rises with C at fixed n, so any C in [smallest_passing,
    # prefix_hi] also passes).
    supply_ok = C_contrast >= C_LO
    operating_C = None
    if smallest_passing is not None:
        operating_C = max(C_LO, smallest_passing)
        if operating_C > prefix_hi:
            operating_C = None
    if operating_C is not None and C_LO <= operating_C <= C_HI:
        # confirm the chosen prefix passes coverage + all 3 power gates
        row = next(p for p in power_rows if p["C"] == operating_C)
        cov = next(c for c in coverage_rows if c["C"] == operating_C)
        askable = (row["prefix_passes"] and cov["every_m_ge_8"]
                   and all_pass and C_LO <= operating_C <= C_HI)
        verdict = "ASKABLE" if askable else "NOT-ASKABLE-AT-SCALE"
    elif not supply_ok:
        verdict = "NEEDS-MORE-INVENTORY"
    else:
        # supply >= 80 contrasting pairs exist, but no C<=100 geometry powers
        verdict = "NOT-ASKABLE-AT-SCALE"

    # the single most important number
    top = power_rows[-1] if power_rows else None
    headline_C = prefix_hi
    headline_power = (top["contrasts"]["K-3"]["power_at_mu_star"]
                      if top else None)

    verdict_obj = {
        "part": "4 — verdict", "built": PASS_STAMP,
        "verdict": verdict,
        "operating_C": operating_C,
        "C_contrast_selected_passing": C_contrast,
        "supply_contrasting_pairs_ge_80": supply_ok,
        "smallest_passing_prefix": smallest_passing,
        "prefix_hi_min100_Ccontrast": prefix_hi,
        "all_selected_pass_contrast": all_pass,
        "verdict_rule": ("ASKABLE iff 80<=C<=100 AND every m_c>=8 AND all "
                         "pass contrast AND all 3 power gates (K-1/K-2/K-3) "
                         ">=0.80; NEEDS-MORE-INVENTORY if <80 contrasting "
                         "pairs survive; NOT-ASKABLE-AT-SCALE if no C<=100 "
                         "geometry powers all contrasts"),
        "headline": {
            "note": "the single most important number",
            "C": headline_C,
            "K-3_joint_power_at_mu_star_+4.09pts": headline_power,
        },
        "reports": {
            "candidate": "poc/f1k-askability/reports/candidate-report.json",
            "distinctness": "poc/f1k-askability/reports/distinctness-report.json",
            "hash": "poc/f1k-askability/reports/hash-report.json",
            "coverage": "poc/f1k-askability/reports/coverage-report.json",
            "power": "poc/f1k-askability/reports/power-report.json",
        },
        "governance": {"gold_label_blind": True, "model_outcome_blind": True,
                       "gpu": "none", "spend_usd": 0.0, "network": "none",
                       "git_registry_freeze": "none",
                       "deterministic": "byte-identical on re-run"},
    }
    write_json(HERE / "reports" / "verdict-report.json", verdict_obj)

    print("  VERDICT: %s   (operating C=%s, C_contrast=%d, smallest passing "
          "prefix=%s)" % (verdict, operating_C, C_contrast, smallest_passing))
    print("  headline: K-3 joint power at mu*=+4.09 pts, C=%s -> %s"
          % (headline_C, headline_power))
    print("  reports under poc/f1k-askability/reports/")


if __name__ == "__main__":
    main()
