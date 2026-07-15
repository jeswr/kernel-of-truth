#!/usr/bin/env python3
"""modal_nsk1_r3bridge — nsk1-r3 §6.5 REQUIRED pre-freeze b3 SURFACE-BRIDGE.

EXECUTES docs/next/design/nsk1-r3-hardened.md §6.5 (D-1 mitigation;
BLOCKER-0). EXPLORATORY CALIBRATION: every row is phase:"explore",
gate:"NSK1-R3-BRIDGE", carries confirmatory_eligible:false, and is NEVER
eligible for the confirmatory NSK1-R3 analysis; its numbers never gate the
frozen verdict. It converts the ASM-2357-old surface-invariance STIPULATION
into a MEASURED paired sensitivity number and re-anchors the §4 power plan
via the §6.5 branch rule.

QUESTION: how much does the keyed-delivery margin move between the AMT
surface B" measured on and the synthetic surface the confirmatory r3 corpus
uses — same items, same chains, same names, same cell, same operator?

DESIGN (verbatim from §6.5):
  * Items: n_bridge = 200 sampled WITHOUT replacement, fixed seed 20260714,
    from the 958 retained covered items B'/B"/Stage-1 measured (already
    burned; the fresh r3 corpus, its seeds 20260720/20260726 and the
    confirmatory derangement families {20260720-22}/{20260723-25} are never
    touched). Both text-only substrata eligible; substrata reported.
  * Arms (paired, same item): AMT = the item's original released
    AMT-paraphrase story (`context`, story_sha256-pinned); SYN = the SAME
    chain re-rendered through the pinned generator's synthetic templater by
    the committed script poc/nsk1/rerender_syn_bridge.py (generator commit
    d045fae2, PYTHONHASHSEED=0; renders consumed here sha-pinned). The two
    arms' prompts are ASSERTED to differ ONLY in the story bytes (question
    surface + candidate names identical); ONE shared donor pair
    D_top/D_bridge -> one shared unit direction v-hat per item (the donor
    frame is surface-independent, D-1 §3).
  * Cell/operator: C1 = (16,16) only, alpha = 1.0, the B" additive
    norm-matched injection + teacher-forced margin read-out VERBATIM
    (byte-mirrors of modal_nsk1_g2._bprime2_body_impl's add_pre_hook /
    _chat_ids / _pad_batch / _gen_plain / _tf_lp — the ONLY change is that
    prompt token ids are indexed by arm; any other divergence would
    invalidate AMT-arm comparability to B"). Derangement seeds = the
    B"/Stage-1 family {20260712, 20260713, 20260714} (already burned on
    these items). Host/model/commit pin identical to B"/Stage-1.
  * Primary paired statistic: per-item real-arm success bits on both
    surfaces; Delta_surface = keyacc_syn - keyacc_amt with the
    discordant-pair decomposition (b = AMT-only, c = SYN-only), point
    (c-b)/n, two-sided 95% Newcombe paired-difference CI (Newcombe 1998
    method 10), exact two-sided McNemar p reported DESCRIPTIVELY
    (calibration, NOT a hypothesis test).
  * Secondaries (reported, never gated): paired coin + role control levels
    per surface; paired text-only accuracy per surface (§5.1 headroom
    preview); register-convergence flag if syn keyacc materially > amt.
  * Branch-rule verdict written into the summary: syn >= 0.81 -> freeze
    as-is; 0.75 <= syn < 0.81 -> re-anchor planning keyacc + raise n;
    syn < 0.75 -> do not freeze, escalate per D-1 §6(c).
  * Caps ENFORCED IN-RUNNER: USD 2 / 0.5 GPU-h / 2 h wall, 1xA10G. The GPU
    body hard-stops at 1800 s GPU time (= the 0.5 GPU-h cap; also < USD 2 at
    any plausible A10G rate) and Modal timeout enforces the 2 h wall.
    ~8,000 GPU calls expected (donor 400 + teacher-forced 7,200 + 400 gens).

OUTPUT: poc/nsk1/out/r3bridge/ — r3bridge_summary.json (branch-rule verdict
+ paired stats + provenance: story shas both arms, generator commit, seeds)
+ r3bridge_rows.jsonl (per-item rows). Mock outputs go to .../r3bridge/mock/.

CODE REUSE (do NOT reimplement): imports VERBATIM from modal_nsk1_g2 —
_build_specs_bprime2 (the 958 B" specs + every build assert), _score_entity,
_bp_sattolo, _bp_wilson, _bprime2_coin_bit, _B2Abort, MAX_NEW_TOKENS; GPU
helpers are byte-mirrors (see above). The SYN templater lives in the
committed poc/nsk1/rerender_syn_bridge.py (pinned TemplatorSynthetic).

    # mock-validate, $0, no GPU, no Modal session needed:
    poc/modal/.venv/bin/python poc/modal/modal_nsk1_r3bridge.py --mock
    # dry plan ($0):
    poc/modal/.venv/bin/modal run poc/modal/modal_nsk1_r3bridge.py::bridge --dry-plan
    # real (coordinator; 1xA10G; caps USD 2 / 0.5 GPU-h / 2 h wall):
    PYTHONHASHSEED=0 python3 poc/nsk1/rerender_syn_bridge.py   # pinned SYN renders (idempotent)
    poc/modal/.venv/bin/modal run poc/modal/modal_nsk1_r3bridge.py::bridge
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import sys
from pathlib import Path

import modal

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1] if len(_HERE.parents) > 1 else _HERE
sys.path.insert(0, str(_HERE))

# ---- VERBATIM reuse of the B" instrument's builders/scorers/helpers ----
import modal_nsk1_g2 as g2  # noqa: E402  (single-file module, container-safe import)

BRIDGE_MODEL = g2.STAGE1_MODEL            # SmolLM2-1.7B-Instruct (R3)
BRIDGE_PIN = g2.STAGE1_PIN                # commit pin (ABORT otherwise), B"/Stage-1 identical
BRIDGE_CELL = (16, 16)                    # §6.5: C1 only
BRIDGE_ALPHA = 1.0                        # §6.5: fixed (no calibration ladder)
BRIDGE_SAMPLE_SEED = 20260714             # §6.5: n_bridge sample seed
BRIDGE_N = 200                            # §6.5: n_bridge
BRIDGE_DRG_SEEDS = [20260712, 20260713, 20260714]  # §6.5: B"/Stage-1 family
BRIDGE_BATCH = 16                         # GPU mini-batch (B" value; OOM auto-halves)
BRIDGE_GPU_S_CAP = 1800                   # HARD in-container stop = 0.5 GPU-h cap
BRIDGE_WALL_S_CAP = 7200                  # 2 h wall (also the Modal timeout)
BRIDGE_USD_CAP = 2.0                      # §6.5 hard $ cap (planning A10G ~USD 1.10/h
A10G_USD_PER_H = 1.10                     # => 0.5 GPU-h ~ USD 0.55 < 2; STIPULATED rate)
SURFACES = ("amt", "syn")
RENDERS_PATH = _ROOT / "poc/nsk1/out/r3bridge/syn_renders.jsonl"
RENDERS_MANIFEST = _ROOT / "poc/nsk1/out/r3bridge/syn_renders_manifest.json"
OUT_DIR = _ROOT / "poc/nsk1/out/r3bridge"
BPRIME2_ROWS = _ROOT / "poc/nsk1/out/bprime2/bprime2_rows.jsonl"  # substrata ref (report-only)

app = modal.App("kot-nsk1-r3bridge")
image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install(*g2._image_pins())
         .add_local_python_source("modal_nsk1_g2"))
hf_cache = modal.Volume.from_name("kot-hf-cache", create_if_missing=True)


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# ===================================================================== build
def _load_pool_items():
    """The 958 retained covered items, SAME source + order as
    g2._build_specs_bprime (covered rows of items.jsonl then headroom.jsonl).
    Needed locally for the raw AMT story bytes (the specs carry only the
    rendered prompt)."""
    src = []
    for path, stratum in (("data/nsk1-clutrr/items.jsonl", "covered"),
                          ("data/nsk1-clutrr/headroom.jsonl", None)):
        for line in (_ROOT / path).read_text().splitlines():
            if not line.strip():
                continue
            it = json.loads(line)
            if stratum is not None and it.get("stratum") != stratum:
                continue
            src.append(it)
    assert len(src) == 958, "ABORT: pool=%d != 958" % len(src)
    return src


def _sample_indices():
    """§6.5 sampler: sorted 200-of-958 WITHOUT replacement, seed 20260714.
    Drawn twice from fresh RNGs and compared (determinism assert)."""
    a = sorted(random.Random(BRIDGE_SAMPLE_SEED).sample(range(958), BRIDGE_N))
    b = sorted(random.Random(BRIDGE_SAMPLE_SEED).sample(range(958), BRIDGE_N))
    assert a == b, "ABORT: SAMPLER_NONDETERMINISTIC"
    assert len(set(a)) == BRIDGE_N, "ABORT: sample with replacement?"
    return a


def _build_bridge_specs():
    """Paired specs for the 200 sampled items. AMT prompt = the B" prompt
    VERBATIM (g2._build_specs_bprime2, all build asserts); SYN prompt =
    byte-identical except the story bytes (ASSERTED). Donors/candidates
    shared. Returns (specs, provenance-dict)."""
    base = g2._build_specs_bprime2()          # 958 B" specs, every assert live
    pool = _load_pool_items()
    idx = _sample_indices()

    renders = [json.loads(ln) for ln in RENDERS_PATH.read_text().splitlines()
               if ln.strip()]
    assert len(renders) == BRIDGE_N, "ABORT: renders n=%d != %d" % (len(renders), BRIDGE_N)
    manifest = json.loads(RENDERS_MANIFEST.read_text())
    assert manifest["generator_commit"].startswith("d045fae2"), \
        "ABORT: renders generator commit != d045fae2 pin"
    assert "PASS" in manifest["templater_fidelity_check"]["result"], \
        "ABORT: templater fidelity check not PASS"
    renders_sha = _sha(RENDERS_PATH.read_bytes())

    specs = []
    for rank, i in enumerate(idx):
        bs, it, rd = base[i], pool[i], renders[rank]
        assert bs["item_id"] == it["item_id"] == rd["item_id"], \
            "ABORT: sample/render order drift at rank %d" % rank
        assert rd["pool_index"] == i and rd["sample_rank"] == rank, \
            "ABORT: render rank/index drift (%s)" % rd["item_id"]
        story_amt = "\n".join(it["context"])
        # §6.5: AMT story story_sha256-pinned in provenance
        assert _sha(story_amt.encode()) == it["provenance"]["story_sha256"] \
            == rd["story_amt_sha256"], "ABORT: AMT story sha drift (%s)" % it["item_id"]
        story_syn = rd["story_syn"]
        assert _sha(story_syn.encode()) == rd["story_syn_sha256"], \
            "ABORT: SYN story sha drift (%s)" % it["item_id"]
        # arms differ ONLY in the story bytes: rebuild both prompts around the
        # SAME non-story remainder taken from the verbatim B" prompt
        head = "Story:\n" + story_amt
        assert bs["prompt"].startswith(head), \
            "ABORT: B\" prompt decomposition failed (%s)" % it["item_id"]
        rest = bs["prompt"][len(head):]     # "\nQuestion: Who is the X of Y?\n<instr>"
        assert rest.startswith("\nQuestion: Who is the %s of %s?" %
                               (it["gold_surface"], bs["base"])), \
            "ABORT: question surface drift (%s)" % it["item_id"]
        prompt_syn = "Story:\n" + story_syn + rest
        assert prompt_syn.replace(story_syn, story_amt, 1) == bs["prompt"], \
            "ABORT: arms differ beyond story bytes (%s)" % it["item_id"]
        # §6.5: candidate names identical in both arms
        for nm in (bs["top_surface"], bs["bridge_surface"], bs["base"]):
            assert "[%s]" % nm in story_syn, \
                "ABORT: candidate name %s missing from SYN story (%s)" % (nm, it["item_id"])
        specs.append({
            "item_id": bs["item_id"],
            "prompt": {"amt": bs["prompt"], "syn": prompt_syn},
            "story_sha256": {"amt": rd["story_amt_sha256"],
                             "syn": rd["story_syn_sha256"]},
            # ONE shared donor pair per item (surface-independent, D-1 §3)
            "d_top": bs["d_top"], "d_bridge": bs["d_bridge"],
            "top_surface": bs["top_surface"], "bridge_surface": bs["bridge_surface"],
            "gold_top": bs["gold_top"], "base": bs["base"], "surfaces": bs["surfaces"],
        })
    prov = {"sample_seed": BRIDGE_SAMPLE_SEED, "n_bridge": BRIDGE_N,
            "sample_indices_sha256": _sha(json.dumps(idx).encode()),
            "syn_renders_sha256": renders_sha,
            "syn_renders_manifest": manifest,
            "population": "958 retained covered items (858 covered rows of "
                          "data/nsk1-clutrr/items.jsonl + 100 headroom rows; the "
                          "B\" measurement set — operational reading disclosed in "
                          "poc/nsk1/rerender_syn_bridge.py)"}
    return specs, prov


def _sigmas(n):
    """Three independent Sattolo derangements over sample-rank ascending
    order, seeds = the B"/Stage-1 family (g2._bp_sattolo VERBATIM; mirrors
    Stage-1's construction)."""
    out = {}
    for sd in BRIDGE_DRG_SEEDS:
        p = g2._bp_sattolo(n, sd)
        assert all(p[k] != k for k in range(n)), "ABORT: sigma seed=%d fixed point" % sd
        out[sd] = p
    return out


# ============================================================ shared compute
class _CapStop(Exception):
    """Raised by a ctx when the in-runner hard caps trip (hard stop, §6.5)."""


def _mini(items, batch):
    for a in range(0, len(items), batch):
        yield items[a:a + batch]


def _row(**kw):
    base = {"phase": "explore", "gate": "NSK1-R3-BRIDGE", "host": "R3",
            "model": BRIDGE_MODEL, "form": "2", "confirmatory_eligible": False,
            "surface": None, "item_id": None, "probe": None, "cell": None,
            "arm": None, "sign": None, "seed": None, "coin": None,
            "alpha": None, "lp_top": None, "lp_bridge": None, "gen": None,
            "correct": None, "gold": None, "story_sha256": None}
    base.update(kw)
    return base


def _bridge_compute(specs, sigma_by_seed, ctx, batch=BRIDGE_BATCH, log=print):
    """The FULL bridge measurement over a ctx (real GPU closures or the mock
    stub). BOTH arms flow through the SAME code path: ctx.gen(surf, mb) for
    text-only and ctx.tf_lp(surf, mb, cand_key, sign, src_of) for every
    teacher-forced margin — identical call sites, only the `surf` tag (which
    selects the prompt token ids) differs. Success bit = m(+) > m(-) with
    m(s) = lp(top|s) - lp(bridge|s); ties/non-finite = failure (B" §3 Step 6
    semantics, coin/role transforms byte-matched to B")."""
    n = len(specs)
    lh, lt = BRIDGE_CELL
    order = list(range(n))
    rows = []
    per = {sf: {"text": [None] * n, "text_gen": [None] * n,
                "real": [None] * n, "real_ties": 0,
                "role": {sd: [None] * n for sd in BRIDGE_DRG_SEEDS},
                "coin": {sd: [None] * n for sd in BRIDGE_DRG_SEEDS},
                "drg_ties": {sd: 0 for sd in BRIDGE_DRG_SEEDS},
                "baseline_margin": [None] * n}
           for sf in SURFACES}

    # ---- text-only pass (1 gen / item / surface) ----
    for sf in SURFACES:
        for mb in _mini(order, batch):
            gens = ctx.gen(sf, mb)
            for i, gtxt in zip(mb, gens):
                s = specs[i]
                ok = bool(g2._score_entity(gtxt, s["gold_top"], s["base"], s["surfaces"]))
                per[sf]["text"][i] = ok
                per[sf]["text_gen"][i] = gtxt
                rows.append(_row(surface=sf, item_id=s["item_id"], probe="text-only",
                                 gen=gtxt, correct=ok, gold=s["gold_top"],
                                 story_sha256=s["story_sha256"][sf]))
        log("[bridge] text-only %s acc=%.4f" % (sf, sum(per[sf]["text"]) / n))

    # ---- teacher-forced margins: real +- and deranged +- x 3 seeds ----
    def _pair(sf, mb, sign, src_of):
        lpt = ctx.tf_lp(sf, mb, "top", sign, src_of)
        lpb = ctx.tf_lp(sf, mb, "bridge", sign, src_of)
        return lpt, lpb

    for sf in SURFACES:
        for mb in _mini(order, batch):
            rp = _pair(sf, mb, 1, None)     # real: item's OWN shared donor
            rm = _pair(sf, mb, -1, None)
            drg = {sd: (_pair(sf, mb, 1, sigma_by_seed[sd]),
                        _pair(sf, mb, -1, sigma_by_seed[sd]))
                   for sd in BRIDGE_DRG_SEEDS}
            for r_idx, i in enumerate(mb):
                s = specs[i]
                rp_t, rp_b = rp[0][r_idx], rp[1][r_idx]
                rm_t, rm_b = rm[0][r_idx], rm[1][r_idx]
                vals = [rp_t, rp_b, rm_t, rm_b]
                for sd in BRIDGE_DRG_SEEDS:
                    (dp_t, dp_b), (dm_t, dm_b) = \
                        (drg[sd][0][0][r_idx], drg[sd][0][1][r_idx]), \
                        (drg[sd][1][0][r_idx], drg[sd][1][1][r_idx])
                    vals += [dp_t, dp_b, dm_t, dm_b]
                if not all(math.isfinite(v) for v in vals):
                    raise g2._B2Abort("NAN_MARGINS item=%s surface=%s" % (s["item_id"], sf))
                mr_p, mr_m = rp_t - rp_b, rm_t - rm_b
                per[sf]["real"][i] = 1 if mr_p > mr_m else 0     # tie -> failure (B")
                if mr_p == mr_m:
                    per[sf]["real_ties"] += 1
                rows.append(_row(surface=sf, item_id=s["item_id"], probe="margin",
                                 cell=[lh, lt], arm="real", sign=1, alpha=BRIDGE_ALPHA,
                                 lp_top=rp_t, lp_bridge=rp_b, gold=s["gold_top"],
                                 story_sha256=s["story_sha256"][sf]))
                rows.append(_row(surface=sf, item_id=s["item_id"], probe="margin",
                                 cell=[lh, lt], arm="real", sign=-1, alpha=BRIDGE_ALPHA,
                                 lp_top=rm_t, lp_bridge=rm_b, gold=s["gold_top"],
                                 story_sha256=s["story_sha256"][sf]))
                for sd in BRIDGE_DRG_SEEDS:
                    dp_t, dp_b = drg[sd][0][0][r_idx], drg[sd][0][1][r_idx]
                    dm_t, dm_b = drg[sd][1][0][r_idx], drg[sd][1][1][r_idx]
                    md_p, md_m = dp_t - dp_b, dm_t - dm_b
                    b = g2._bprime2_coin_bit(s["item_id"], lh, lt, seed=sd)
                    role_bit = 1 if md_p > md_m else 0
                    coin_bit = (1 if md_p > md_m else 0) if b == 1 else \
                               (1 if md_m > md_p else 0)      # byte-match B"
                    per[sf]["role"][sd][i] = role_bit
                    per[sf]["coin"][sd][i] = coin_bit
                    if md_p == md_m:
                        per[sf]["drg_ties"][sd] += 1
                    rows.append(_row(surface=sf, item_id=s["item_id"], probe="margin",
                                     cell=[lh, lt], arm="drg", sign=1, seed=sd, coin=b,
                                     alpha=BRIDGE_ALPHA, lp_top=dp_t, lp_bridge=dp_b,
                                     gold=s["gold_top"],
                                     story_sha256=s["story_sha256"][sf]))
                    rows.append(_row(surface=sf, item_id=s["item_id"], probe="margin",
                                     cell=[lh, lt], arm="drg", sign=-1, seed=sd, coin=b,
                                     alpha=BRIDGE_ALPHA, lp_top=dm_t, lp_bridge=dm_b,
                                     gold=s["gold_top"],
                                     story_sha256=s["story_sha256"][sf]))
        log("[bridge] margins %s keyacc_real=%.4f" % (sf, sum(per[sf]["real"]) / n))

    # ---- unhooked baselines (2 tf forwards / item / surface) ----
    for sf in SURFACES:
        for mb in _mini(order, batch):
            lpt = ctx.tf_lp(sf, mb, "top", None, None)
            lpb = ctx.tf_lp(sf, mb, "bridge", None, None)
            for r_idx, i in enumerate(mb):
                s = specs[i]
                if not (math.isfinite(lpt[r_idx]) and math.isfinite(lpb[r_idx])):
                    raise g2._B2Abort("NAN_BASELINE item=%s surface=%s"
                                      % (s["item_id"], sf))
                per[sf]["baseline_margin"][i] = lpt[r_idx] - lpb[r_idx]
                rows.append(_row(surface=sf, item_id=s["item_id"], probe="baseline",
                                 lp_top=lpt[r_idx], lp_bridge=lpb[r_idx],
                                 gold=s["gold_top"],
                                 story_sha256=s["story_sha256"][sf]))
    return rows, per


# ================================================================ statistics
_Z95 = 1.959964  # two-sided 95%


def _paired_stats(bits_syn, bits_amt):
    """§6.5 primary: discordant-pair decomposition + Newcombe (1998) method-10
    paired-difference 95% CI + exact two-sided McNemar p (DESCRIPTIVE).
    2x2: a=both success, b=AMT-only, c=SYN-only, d=neither.
    Delta = keyacc_syn - keyacc_amt = (c-b)/n. Wilson bounds via
    g2._bp_wilson (VERBATIM) at z=1.959964."""
    assert len(bits_syn) == len(bits_amt)
    n = len(bits_syn)
    a = sum(1 for s_, t in zip(bits_syn, bits_amt) if s_ and t)
    b = sum(1 for s_, t in zip(bits_syn, bits_amt) if not s_ and t)
    c = sum(1 for s_, t in zip(bits_syn, bits_amt) if s_ and not t)
    d = n - a - b - c
    p1, p2 = (a + c) / n, (a + b) / n            # syn, amt
    delta = (c - b) / n
    l1, u1 = g2._bp_wilson(a + c, n, z=_Z95)
    l2, u2 = g2._bp_wilson(a + b, n, z=_Z95)
    # phi-hat with the Newcombe continuity adjustment (A = ad-bc; if A>0 use
    # max(A - n/2, 0)); phi = 0 when any marginal is degenerate
    n1p, n1m, n2p, n2m = a + c, b + d, a + b, c + d
    if min(n1p, n1m, n2p, n2m) == 0:
        phi = 0.0
    else:
        A = a * d - b * c
        if A > 0:
            A = max(A - n / 2.0, 0.0)
        phi = A / math.sqrt(n1p * n1m * n2p * n2m)
    dl = delta - math.sqrt(max(0.0, (p1 - l1) ** 2
                               - 2 * phi * (p1 - l1) * (u2 - p2) + (u2 - p2) ** 2))
    du = delta + math.sqrt(max(0.0, (u1 - p1) ** 2
                               - 2 * phi * (u1 - p1) * (p2 - l2) + (p2 - l2) ** 2))
    # exact two-sided McNemar on the discordant pairs (DESCRIPTIVE ONLY)
    m = b + c
    if m == 0:
        p_mcnemar = 1.0
    else:
        k = min(b, c)
        p_mcnemar = min(1.0, 2.0 * sum(math.comb(m, i) for i in range(k + 1)) / (2.0 ** m))
    return {"n": n, "both_success": a, "amt_only_b": b, "syn_only_c": c,
            "neither": d, "keyacc_syn": p1, "keyacc_amt": p2,
            "delta_surface_point": delta,
            "newcombe_ci95": [max(-1.0, dl), min(1.0, du)],
            "mcnemar_exact_p_DESCRIPTIVE": p_mcnemar,
            "mcnemar_note": "calibration readout, NOT a hypothesis test (§6.5)"}


def _branch(syn_keyacc):
    """§6.5 pre-freeze branch rule (disclosed calibration use)."""
    if syn_keyacc >= 0.81:
        return "FREEZE-AS-IS: syn keyacc >= 0.81 holds the B\" planning band; " \
               "§4/§6.3 plan unchanged"
    if syn_keyacc >= 0.75:
        return "RE-ANCHOR: 0.75 <= syn keyacc < 0.81 — re-anchor planning keyacc " \
               "to the bridge value and raise the §6.3 n target (power >= 0.90) " \
               "BEFORE freeze"
    return "DO-NOT-FREEZE: syn keyacc < 0.75 — escalate to the maintainer per " \
           "D-1 §6(c)"


def _acc(bits):
    bs = [x for x in bits if x is not None]
    return (sum(bs) / len(bs)) if bs else None


def _summarize(specs, per, prov, bp2_ref, extra):
    """Assemble the §6.5 summary: primary paired stat, branch verdict,
    secondaries (never gated), substrata, provenance."""
    n = len(specs)
    primary = _paired_stats(per["syn"]["real"], per["amt"]["real"])
    text_paired = _paired_stats(per["syn"]["text"], per["amt"]["text"])
    controls = {sf: {"coin": {str(sd): _acc(per[sf]["coin"][sd]) for sd in BRIDGE_DRG_SEEDS},
                     "coin_pooled": _acc([x for sd in BRIDGE_DRG_SEEDS
                                          for x in per[sf]["coin"][sd]]),
                     "role": {str(sd): _acc(per[sf]["role"][sd]) for sd in BRIDGE_DRG_SEEDS},
                     "role_pooled": _acc([x for sd in BRIDGE_DRG_SEEDS
                                          for x in per[sf]["role"][sd]]),
                     "ties": {"real": per[sf]["real_ties"],
                              "drg": {str(sd): per[sf]["drg_ties"][sd]
                                      for sd in BRIDGE_DRG_SEEDS}}}
                for sf in SURFACES}
    # substrata: B" reference text-only bit where available (report-only),
    # else the in-run AMT text-only bit
    strata = {}
    src = "bprime2_reference" if bp2_ref else "in_run_amt_text_only"
    for label, want in (("text_correct", True), ("text_fail", False)):
        sel = [i for i, s in enumerate(specs)
               if (bp2_ref.get(s["item_id"], per["amt"]["text"][i]) if bp2_ref
                   else per["amt"]["text"][i]) is want]
        strata[label] = {"n": len(sel),
                         "keyacc_amt": _acc([per["amt"]["real"][i] for i in sel]),
                         "keyacc_syn": _acc([per["syn"]["real"][i] for i in sel])}
    reg_flag = primary["delta_surface_point"] >= 0.05
    summary = {
        "phase": "explore", "gate": "NSK1-R3-BRIDGE",
        "spec_ref": "docs/next/design/nsk1-r3-hardened.md §6.5 (b3 surface-bridge; "
                    "D-1 mitigation; BLOCKER-0)",
        "quarantine": ("EXPLORATORY calibration: these rows/numbers are NEVER "
                       "eligible for the confirmatory NSK1-R3 analysis and never "
                       "gate the frozen verdict; disclosed further contact of "
                       "already-burned items only."),
        "question": "paired same-item AMT-vs-synthetic keyed-delivery sensitivity "
                    "at C1=(16,16), alpha=1.0, B\" operator verbatim",
        "model": BRIDGE_MODEL, "model_commit_pin": BRIDGE_PIN,
        "cell": list(BRIDGE_CELL), "alpha": BRIDGE_ALPHA,
        "seeds": {"sample": BRIDGE_SAMPLE_SEED,
                  "derangement_family": BRIDGE_DRG_SEEDS,
                  "coin_recipe": "int(sha256('<drg_seed>|item_id|16|16').hexdigest(),16)&1 "
                                 "(g2._bprime2_coin_bit, derangement seed in seed slot)"},
        "n_bridge": n,
        "primary_paired": primary,
        "branch_rule_verdict": _branch(primary["keyacc_syn"]),
        "branch_rule_thresholds": {"freeze_as_is": ">=0.81",
                                   "re_anchor": "[0.75,0.81)",
                                   "do_not_freeze": "<0.75"},
        "secondaries_never_gated": {
            "controls_per_surface": controls,
            "text_only_acc": {sf: _acc(per[sf]["text"]) for sf in SURFACES},
            "text_only_paired": text_paired,
            "baseline_margin_mean": {sf: (sum(per[sf]["baseline_margin"]) / n)
                                     for sf in SURFACES},
            "register_convergence_flag": {
                "flag": bool(reg_flag),
                "rule": "delta_surface_point >= 0.05 (syn materially above amt; "
                        "disclosed operational threshold ~ one CI half-width at "
                        "n=200; reported as a caution, never gating)"},
        },
        "substrata": {"source": src, "strata": strata},
        "provenance": prov,
        "caps": {"usd": BRIDGE_USD_CAP, "gpu_h": 0.5, "wall_h": 2.0,
                 "gpu": "1xA10G", "in_container_gpu_s_hard_stop": BRIDGE_GPU_S_CAP,
                 "planning_rate_usd_per_a10g_h_STIPULATED": A10G_USD_PER_H},
    }
    summary.update(extra)
    return summary


def _validate_rows(rows):
    """Schema + quarantine-tag check on EVERY row (mock clause 5; also run on
    real rows before write). Fail-closed."""
    req = {"phase", "gate", "host", "model", "form", "confirmatory_eligible",
           "surface", "item_id", "probe", "cell", "arm", "sign", "seed", "coin",
           "alpha", "lp_top", "lp_bridge", "gen", "correct", "gold", "story_sha256"}
    for r in rows:
        assert set(r.keys()) == req, "ROW_SCHEMA: keys drift: %s" % sorted(set(r) ^ req)
        assert r["phase"] == "explore", "ROW_SCHEMA: phase != explore"
        assert r["gate"] == "NSK1-R3-BRIDGE", "ROW_SCHEMA: gate drift"
        assert r["confirmatory_eligible"] is False, "ROW_SCHEMA: eligibility leak"
        assert r["surface"] in SURFACES, "ROW_SCHEMA: surface"
        assert r["probe"] in ("text-only", "baseline", "margin"), "ROW_SCHEMA: probe"
        if r["probe"] == "margin":
            assert r["cell"] == [16, 16] and r["arm"] in ("real", "drg") \
                and r["sign"] in (1, -1) and r["alpha"] == BRIDGE_ALPHA, "ROW_SCHEMA: margin"
            assert (r["seed"] in BRIDGE_DRG_SEEDS) == (r["arm"] == "drg"), "ROW_SCHEMA: seed"
        assert r["story_sha256"], "ROW_SCHEMA: story sha missing"
    return len(rows)


def _load_bp2_text_reference():
    """B" text-only correctness bits (report-only substrata reference)."""
    if not BPRIME2_ROWS.exists():
        return {}
    ref = {}
    for ln in BPRIME2_ROWS.read_text().splitlines():
        if not ln.strip():
            continue
        r = json.loads(ln)
        if r.get("probe") == "text-only":
            ref[r["item_id"]] = bool(r["correct"])
    return ref


# ============================================================== GPU (remote)
def _bridge_body(model_id, specs, sigma_lists, batch_size, gpu_s_cap):
    import traceback
    try:
        return _bridge_body_impl(model_id, specs, sigma_lists, batch_size, gpu_s_cap)
    except Exception as e:  # noqa: BLE001
        tb = traceback.format_exc()
        print("R3BRIDGE ERROR:", repr(e))
        print(tb)
        return {"aborted": True, "abort_reason": "EXCEPTION: %s" % repr(e),
                "traceback": tb, "rows": [], "per": None}


def _bridge_body_impl(model_id, specs, sigma_lists, batch_size, gpu_s_cap):
    """GPU body. The injection + teacher-forced read-out below is a BYTE-MIRROR
    of modal_nsk1_g2._bprime2_body_impl (B"): add_pre_hook / _chat_ids /
    _pad_batch / _gen_plain / _tf_lp / donor harvest (_last_name_tok) are
    copied verbatim; the ONLY changes are (i) prompt token ids indexed by
    surface arm, (ii) LH = {16} only, (iii) the §6.5 hard-cap guard. Any other
    divergence would invalidate AMT-arm comparability to B"."""
    import time
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    t0 = time.time()
    n = len(specs)
    sigma_by_seed = {int(sd): list(p) for sd, p in sigma_lists}
    tok = AutoTokenizer.from_pretrained(model_id, revision=BRIDGE_PIN)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        model_id, revision=BRIDGE_PIN, torch_dtype=torch.float32)
    model.to("cuda").eval()
    L = int(model.config.num_hidden_layers)
    commit = getattr(model.config, "_commit_hash", None)
    if commit is not None and commit != BRIDGE_PIN:
        return {"aborted": True, "abort_reason":
                "COMMIT_PIN_MISMATCH got=%s want=%s" % (commit, BRIDGE_PIN),
                "rows": [], "per": None}
    if L != 24:
        return {"aborted": True, "abort_reason": "L_NOT_24 got=%d" % L,
                "rows": [], "per": None}
    layers = model.model.layers
    lh, lt = BRIDGE_CELL
    calls = {"tf": 0, "gen": 0, "donor": 0}
    print("[r3b] model=%s L=%d commit=%s cell=%s alpha=%s" %
          (model_id, L, commit, BRIDGE_CELL, BRIDGE_ALPHA))

    def _caps():
        el = time.time() - t0
        if el > gpu_s_cap:
            raise _CapStop("HARD_CAP gpu_s=%.0f > %d (0.5 GPU-h §6.5 cap)"
                           % (el, gpu_s_cap))

    # ---- additive norm-matched pre-hook: BYTE-MIRROR of B" add_pre_hook ----
    hook_state = {"vec": None, "wpos": None}  # vec=[bs,d]=s·α·Δ̂v ; wpos=[bs] long

    def add_pre_hook(module, args, kwargs):
        st = hook_state
        if st["vec"] is None:
            return None
        hs = None
        where = None
        if len(args) > 0 and torch.is_tensor(args[0]) and args[0].dim() == 3:
            hs, where = args[0], "arg"
        elif torch.is_tensor(kwargs.get("hidden_states")):
            hs, where = kwargs["hidden_states"], "kw"
        if hs is None or hs.shape[1] <= 1:
            return None  # decode step (seq==1): prefill-only (B" spec §3 Step 5/6)
        hs = hs.clone()
        u = st["vec"].to(hs.dtype)          # [bs, d]
        wpos = st["wpos"]                    # [bs] long
        bs = hs.shape[0]
        rows_ = torch.arange(bs, device=hs.device)
        cur = hs[rows_, wpos, :]              # [bs, d]
        nrm = cur.norm(dim=-1, keepdim=True)  # [bs, 1] = ‖h_p‖
        hs[rows_, wpos, :] = cur + nrm * u   # h ← h + ‖h‖·(s·α·Δ̂v)
        if where == "arg":
            return ((hs,) + tuple(args[1:]), kwargs)
        nk = dict(kwargs)
        nk["hidden_states"] = hs
        return (args, nk)

    def _chat_ids(prompt):
        msgs = [{"role": "user", "content": prompt}]
        try:
            return list(tok.apply_chat_template(msgs, add_generation_prompt=True))
        except Exception:  # noqa: BLE001
            return list(tok(prompt).input_ids)

    def _pad_batch(id_lists):
        maxlen = max(len(x) for x in id_lists)
        ii, am = [], []
        for x in id_lists:
            pad = maxlen - len(x)
            ii.append([tok.pad_token_id] * pad + x)
            am.append([0] * pad + [1] * len(x))
        return (torch.tensor(ii, device="cuda"),
                torch.tensor(am, device="cuda"), maxlen)

    # prompt ids per ARM (the single deliberate divergence from B": two
    # surfaces of the same item share cand_ids + donor)
    prompt_ids = {sf: [None] * n for sf in SURFACES}
    for sf in SURFACES:
        for i, s in enumerate(specs):
            prompt_ids[sf][i] = _chat_ids(s["prompt"][sf])
    cand_ids = [None] * n
    for i, s in enumerate(specs):
        for key, name in (("top", s["top_surface"]), ("bridge", s["bridge_surface"])):
            cid = tok(" " + name, add_special_tokens=False).input_ids
            assert len(cid) >= 1, "ABORT: empty cand ids (%s)" % s["item_id"]
            if cand_ids[i] is None:
                cand_ids[i] = {}
            cand_ids[i][key] = list(cid)

    def _gen_plain(id_lists):
        try:
            ii, am, maxlen = _pad_batch(id_lists)
            with torch.no_grad():
                out = model.generate(input_ids=ii, attention_mask=am,
                                     max_new_tokens=g2.MAX_NEW_TOKENS, do_sample=False,
                                     num_beams=1, pad_token_id=tok.pad_token_id)
            return [tok.decode(out[r][maxlen:], skip_special_tokens=True)
                    for r in range(len(id_lists))]
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            if len(id_lists) == 1:
                raise
            h = len(id_lists) // 2
            return _gen_plain(id_lists[:h]) + _gen_plain(id_lists[h:])

    def _tf_lp(sf, mb, cand_key, lt_, vec_for):
        """BYTE-MIRROR of B" _tf_lp (write index w=maxlen−len(cand)−1, index
        ASSERT, prefill-only additive hook, per-token log_softmax sum,
        OOM->halve) with prompt ids taken from the arm sf."""
        try:
            id_lists = [prompt_ids[sf][i] + cand_ids[i][cand_key] for i in mb]
            clens = [len(cand_ids[i][cand_key]) for i in mb]
            ii, am, maxlen = _pad_batch(id_lists)
            wrows = [maxlen - clens[r] - 1 for r in range(len(mb))]
            for r, i in enumerate(mb):
                if int(ii[r, wrows[r]].item()) != prompt_ids[sf][i][-1]:
                    raise g2._B2Abort("WRITE_INDEX_MISMATCH item=%s" % specs[i]["item_id"])
            handle = None
            if lt_ is not None and vec_for is not None:
                u = torch.stack([vec_for(i) for i in mb]).to("cuda")
                hook_state["vec"] = u
                hook_state["wpos"] = torch.tensor(wrows, device="cuda", dtype=torch.long)
                handle = layers[lt_].register_forward_pre_hook(add_pre_hook, with_kwargs=True)
            try:
                with torch.no_grad():
                    out = model(input_ids=ii, attention_mask=am)
            finally:
                if handle is not None:
                    handle.remove()
                hook_state["vec"] = None
                hook_state["wpos"] = None
            logits = out.logits
            lps = []
            for r, i in enumerate(mb):
                w = wrows[r]
                cid = cand_ids[i][cand_key]
                lp = 0.0
                for j, tid in enumerate(cid):
                    lr = torch.log_softmax(logits[r, w + j, :].float(), dim=-1)
                    lp += float(lr[tid].item())
                lps.append(lp)
            del out, logits
            return lps
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            if len(mb) == 1:
                raise
            h = len(mb) // 2
            return _tf_lp(sf, mb[:h], cand_key, lt_, vec_for) + \
                _tf_lp(sf, mb[h:], cand_key, lt_, vec_for)

    # ---- donor harvest: ONE shared Δ̂v per item at ℓh=16 (B" Step 4 mirror) ----
    def _last_name_tok(text, name, offsets):
        cstart = text.rfind(name)
        if cstart < 0:
            return None
        cend = cstart + len(name)
        found = None
        for ti, (a, b) in enumerate(offsets):
            if a == b:
                continue
            if a < cend and b > cstart:
                found = ti
        return found

    dhat = {}
    for i, s in enumerate(specs):
        _caps()
        hv = {}
        for key, name, text in (("top", s["top_surface"], s["d_top"]),
                                ("bridge", s["bridge_surface"], s["d_bridge"])):
            enc = tok(text, return_offsets_mapping=True)
            ti = _last_name_tok(text, name, enc["offset_mapping"])
            if ti is None:
                raise g2._B2Abort("NAME_LOCATION donor=%s item=%s" % (key, s["item_id"]))
            idt = torch.tensor([enc["input_ids"]], device="cuda")
            with torch.no_grad():
                fwd = model(idt, output_hidden_states=True)
            hv[key] = fwd.hidden_states[lh][0, ti, :].detach().float().clone()
            calls["donor"] += 1
            del fwd
        d = hv["top"] - hv["bridge"]
        if not (float(d.norm()) > 0):
            raise g2._B2Abort("DELTA_ZERO item=%s lh=%d" % (s["item_id"], lh))
        dhat[i] = d / d.norm()
    print("[r3b] donors harvested for %d items t=%.0fs" % (n, time.time() - t0))

    # ---- ctx wiring the byte-mirrored closures into the shared compute ----
    class _Ctx:
        def gen(self, sf, mb):
            _caps()
            calls["gen"] += len(mb)
            return _gen_plain([prompt_ids[sf][i] for i in mb])

        def tf_lp(self, sf, mb, cand_key, sign, src_of):
            _caps()
            calls["tf"] += len(mb)
            if sign is None:                      # unhooked baseline
                return _tf_lp(sf, mb, cand_key, None, None)
            if src_of is None:                    # real arm: own shared donor
                vf = (lambda i, sgn=sign: BRIDGE_ALPHA * sgn * dhat[i])
            else:                                 # deranged donor sigma(i)
                vf = (lambda i, sgn=sign, p=src_of: BRIDGE_ALPHA * sgn * dhat[p[i]])
            return _tf_lp(sf, mb, cand_key, lt, vf)

    aborted, abort_reason = False, None
    rows, per = [], None
    try:
        rows, per = _bridge_compute(specs, sigma_by_seed, _Ctx(), BRIDGE_BATCH)
    except (_CapStop, g2._B2Abort) as e:
        aborted, abort_reason = True, str(e)
        print("[r3b] HARD STOP:", abort_reason)

    ser_per = None
    if per is not None:
        ser_per = {sf: {"text": per[sf]["text"], "real": per[sf]["real"],
                        "real_ties": per[sf]["real_ties"],
                        "role": {str(sd): per[sf]["role"][sd] for sd in BRIDGE_DRG_SEEDS},
                        "coin": {str(sd): per[sf]["coin"][sd] for sd in BRIDGE_DRG_SEEDS},
                        "drg_ties": {str(sd): per[sf]["drg_ties"][sd]
                                     for sd in BRIDGE_DRG_SEEDS},
                        "baseline_margin": per[sf]["baseline_margin"]}
                   for sf in SURFACES}
    return {"aborted": aborted, "abort_reason": abort_reason,
            "rows": [json.loads(json.dumps(r, default=str)) for r in rows],
            "per": ser_per, "model_commit": commit, "L": L,
            "calls": calls, "elapsed_s": time.time() - t0}


@app.function(image=image, gpu="A10G", volumes={g2.HF_CACHE_MOUNT: hf_cache},
              timeout=BRIDGE_WALL_S_CAP)
def bridge_a10g(model_id, specs, sigma_lists, batch_size, gpu_s_cap):
    r = _bridge_body(model_id, specs, sigma_lists, batch_size, gpu_s_cap)
    try:
        hf_cache.commit()
    except Exception:  # noqa: BLE001
        pass
    return r


# ==================================================================== mock
def _h01(key: str) -> float:
    return int(hashlib.sha256(key.encode()).hexdigest(), 16) / float(2 ** 256)


class _MockCtx:
    """Deterministic stubbed forward (fake logits; NO torch, NO GPU, $0).
    Same call signature as the GPU ctx, so _bridge_compute runs the FULL
    pipeline through the identical code path for both arms."""

    def __init__(self, specs):
        self.specs = specs

    def gen(self, sf, mb):
        out = []
        for i in mb:
            s = self.specs[i]
            u = _h01("gen|%s|%s" % (sf, s["item_id"]))
            out.append("The answer is %s." % (s["gold_top"] if u < 0.8 else s["base"]))
        return out

    def tf_lp(self, sf, mb, cand_key, sign, src_of):
        out = []
        for i in mb:
            s = self.specs[i]
            if sign is None:
                key = "base|%s|%s|%s" % (sf, s["item_id"], cand_key)
                out.append(-2.0 - 4.0 * _h01(key))
                continue
            donor_item = s["item_id"] if src_of is None else \
                self.specs[src_of[i]]["item_id"]
            arm = "real" if src_of is None else "drg"
            key = "lp|%s|%s|%s|%s|%s|%d" % (sf, s["item_id"], donor_item,
                                            arm, cand_key, sign)
            lp = -2.0 - 4.0 * _h01(key)
            # real arm: bias so the signed injection separates margins with
            # ~0.85 per-surface success (deterministic per item/surface)
            if arm == "real":
                works = _h01("works|%s|%s" % (sf, s["item_id"])) < 0.85
                if works:
                    lp += 0.9 * sign * (1 if cand_key == "top" else -1)
            out.append(lp)
        return out


def _run_mock(n_mock=12):
    print("=== r3bridge MOCK VALIDATION (stubbed forward, $0, no GPU) ===")
    checks = {}

    # (1) sampler determinism (seed 20260714) — double-draw assert inside
    # _sample_indices + rank agreement with the committed renders file,
    # both re-checked by _build_bridge_specs' asserts
    specs_all, prov = _build_bridge_specs()
    assert len(specs_all) == BRIDGE_N
    checks["sampler_determinism"] = (
        "PASS (double-draw identical; 200/200 rank+sha agreement with "
        "syn_renders.jsonl; indices sha256=%s)" % prov["sample_indices_sha256"][:16])

    # (2) SYN re-render matches the r3 templater on shared items (fidelity
    # check recorded by the committed re-render script; re-asserted here)
    fid = prov["syn_renders_manifest"]["templater_fidelity_check"]
    assert "PASS" in fid["result"]
    checks["syn_render_fidelity"] = "PASS (r3-corpus items %s byte-reproduced " \
        "by the pinned TemplatorSynthetic path)" % ",".join(fid["shared_items"])

    # (3) both arms score through the SAME B" readout: prompts asserted to
    # differ ONLY in story bytes (in _build_bridge_specs, all 200), and both
    # arms traverse the single ctx.tf_lp/_bridge_compute call path below
    checks["same_readout_both_arms"] = (
        "PASS (200/200 prompts differ only in story bytes; single "
        "_bridge_compute path; shared donor + identical candidate ids)")

    # ---- full pipeline on the mock subset ----
    specs = specs_all[:n_mock]
    sigma = _sigmas(n_mock)
    rows, per = _bridge_compute(specs, sigma, _MockCtx(specs), batch=4)
    rows2, per2 = _bridge_compute(specs, sigma, _MockCtx(specs), batch=4)
    assert json.dumps(rows, sort_keys=True) == json.dumps(rows2, sort_keys=True), \
        "MOCK: pipeline nondeterministic"
    exp_rows = n_mock * 2 * (1 + 1 + 2 + 6)  # text + baseline + real± + drg±×3
    assert len(rows) == exp_rows, "MOCK: row count %d != %d" % (len(rows), exp_rows)

    # (4) paired statistic + branch rule
    stats = _paired_stats(per["syn"]["real"], per["amt"]["real"])
    lo, hi = stats["newcombe_ci95"]
    assert lo <= stats["delta_surface_point"] <= hi and -1 <= lo <= hi <= 1
    assert 0 < stats["mcnemar_exact_p_DESCRIPTIVE"] <= 1
    ref = _paired_stats([1, 1, 1, 1, 1, 0, 0, 1, 0, 0],
                        [1, 1, 0, 0, 0, 1, 0, 1, 0, 1])  # b=2,c=5 discordant... recomputed below
    b_, c_ = ref["amt_only_b"], ref["syn_only_c"]
    m_, k_ = b_ + c_, min(b_, c_)
    expect = min(1.0, 2.0 * sum(math.comb(m_, i) for i in range(k_ + 1)) / 2.0 ** m_)
    assert abs(ref["mcnemar_exact_p_DESCRIPTIVE"] - expect) < 1e-12
    known = _paired_stats([1] * 5 + [0] * 2 + [0] * 3, [0] * 5 + [1] * 2 + [0] * 3)
    assert known["amt_only_b"] == 2 and known["syn_only_c"] == 5
    assert abs(known["mcnemar_exact_p_DESCRIPTIVE"] - 0.453125) < 1e-12, \
        "MOCK: exact McNemar drift (b=2,c=5 must give 0.453125)"
    zero = _paired_stats([1, 0], [1, 0])
    assert zero["delta_surface_point"] == 0 and zero["mcnemar_exact_p_DESCRIPTIVE"] == 1.0
    assert _branch(0.85).startswith("FREEZE-AS-IS")
    assert _branch(0.78).startswith("RE-ANCHOR")
    assert _branch(0.60).startswith("DO-NOT-FREEZE")
    checks["paired_statistic_and_branch"] = (
        "PASS (Newcombe CI brackets point; exact McNemar b=2,c=5 -> 0.453125; "
        "degenerate b=c=0 -> p=1; branch rule fires all three §6.5 branches)")

    # (5) output schema + gate tags on every row
    nrows = _validate_rows(rows)
    checks["schema_and_gate_tags"] = (
        "PASS (%d/%d rows: phase=explore, gate=NSK1-R3-BRIDGE, "
        "confirmatory_eligible=false, full key set, cell/arm/seed constraints)" % (nrows, nrows))

    bp2_ref = _load_bp2_text_reference()
    summary = _summarize(specs, per, prov, bp2_ref,
                         {"mode": "MOCK (stubbed forward; numbers are fake and "
                                  "meaningless — validation of pipeline only)",
                          "mock_n": n_mock, "mock_checks": checks,
                          "calls_expected_real_run": {
                              "donor_forwards": BRIDGE_N * 2,
                              "teacher_forced": BRIDGE_N * 2 * (16 + 2),
                              "generations": BRIDGE_N * 2,
                              "total": BRIDGE_N * 40}})
    mock_dir = OUT_DIR / "mock"
    mock_dir.mkdir(parents=True, exist_ok=True)
    with open(mock_dir / "mock_rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    with open(mock_dir / "mock_summary.json", "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True)
    print("\n=== MOCK RESULT ===")
    for k, v in checks.items():
        print("  %-28s %s" % (k + ":", v))
    print("mock rows=%d -> %s" % (len(rows), mock_dir / "mock_rows.jsonl"))
    print("mock summary -> %s" % (mock_dir / "mock_summary.json"))
    print("MOCK_VALIDATION_PASS = True")
    return checks


# ============================================================== entrypoints
def _print_plan(specs, prov):
    print("=== nsk1-r3 §6.5 SURFACE-BRIDGE — PLAN (phase:explore, gate:NSK1-R3-BRIDGE) ===")
    print("items (n_bridge)    : %d, seed %d, WITHOUT replacement from the 958 "
          "retained covered items (burned; fresh r3 corpus untouched)"
          % (len(specs), BRIDGE_SAMPLE_SEED))
    print("arms                : amt (released AMT story, sha-pinned) | syn "
          "(pinned d045fae2 synthetic templater re-render, sha %s...)"
          % prov["syn_renders_sha256"][:16])
    print("cell/operator       : C1=(16,16), alpha=1.0, B\" injection + "
          "teacher-forced margin readout verbatim; drg seeds %s" % BRIDGE_DRG_SEEDS)
    print("model               : %s @ %s (pin ABORT on drift; L==24 ABORT)"
          % (BRIDGE_MODEL, BRIDGE_PIN))
    print("GPU calls           : donors %d + teacher-forced %d + gens %d = %d "
          "(~8k; 0.08-0.15 GPU-h ~ USD 0.10-0.35 STIPULATED planning)"
          % (BRIDGE_N * 2, BRIDGE_N * 36, BRIDGE_N * 2, BRIDGE_N * 40))
    print("hard caps (enforced): USD %.0f / 0.5 GPU-h (in-container stop %ds) / "
          "2 h wall (Modal timeout) / 1xA10G" % (BRIDGE_USD_CAP, BRIDGE_GPU_S_CAP))
    print("output              : poc/nsk1/out/r3bridge/ (rows NEVER "
          "confirmatory-eligible)")


@app.local_entrypoint()
def bridge(mock: bool = False, dry_plan: bool = False):
    if mock:
        _run_mock()
        return
    specs, prov = _build_bridge_specs()
    _print_plan(specs, prov)
    if dry_plan:
        print("\nDRY-PLAN ONLY — no GPU launched, $0 spent. All build asserts passed.")
        s0 = specs[0]
        print("\n--- amt prompt (item %s) ---\n%s" % (s0["item_id"], s0["prompt"]["amt"][:500]))
        print("\n--- syn prompt (same item) ---\n%s" % s0["prompt"]["syn"][:500])
        print("\n--- shared donors ---\nD_top   : %s\nD_bridge: %s" % (s0["d_top"], s0["d_bridge"]))
        return

    sigma = _sigmas(len(specs))
    sigma_lists = [[sd, sigma[sd]] for sd in BRIDGE_DRG_SEEDS]
    res = bridge_a10g.remote(BRIDGE_MODEL, specs, sigma_lists,
                             BRIDGE_BATCH, BRIDGE_GPU_S_CAP)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if res.get("aborted") or res.get("per") is None:
        with open(OUT_DIR / "r3bridge_abort.json", "w") as f:
            json.dump({"aborted": True, "abort_reason": res.get("abort_reason"),
                       "traceback": res.get("traceback"), "calls": res.get("calls"),
                       "phase": "explore", "gate": "NSK1-R3-BRIDGE"}, f, indent=1)
        print("ABORTED:", res.get("abort_reason"))
        return

    # de-serialize per (json round-trip stringifies int seed keys)
    per = {sf: {"text": res["per"][sf]["text"], "real": res["per"][sf]["real"],
                "real_ties": res["per"][sf]["real_ties"],
                "role": {sd: res["per"][sf]["role"][str(sd)] for sd in BRIDGE_DRG_SEEDS},
                "coin": {sd: res["per"][sf]["coin"][str(sd)] for sd in BRIDGE_DRG_SEEDS},
                "drg_ties": {sd: res["per"][sf]["drg_ties"][str(sd)]
                             for sd in BRIDGE_DRG_SEEDS},
                "baseline_margin": res["per"][sf]["baseline_margin"]}
           for sf in SURFACES}
    rows = res["rows"]
    _validate_rows(rows)
    bp2_ref = _load_bp2_text_reference()
    summary = _summarize(specs, per, prov, bp2_ref,
                         {"mode": "REAL", "model_commit_resolved": res["model_commit"],
                          "calls_made": res["calls"], "elapsed_s": res["elapsed_s"]})
    with open(OUT_DIR / "r3bridge_rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    with open(OUT_DIR / "r3bridge_summary.json", "w") as f:
        json.dump(summary, f, indent=1, sort_keys=True)
    sha_rows = _sha((OUT_DIR / "r3bridge_rows.jsonl").read_bytes())
    sha_sum = _sha((OUT_DIR / "r3bridge_summary.json").read_bytes())
    print("\n=== r3bridge RESULT (phase:explore, gate:NSK1-R3-BRIDGE) ===")
    p = summary["primary_paired"]
    print("keyacc_amt=%.4f keyacc_syn=%.4f delta=%+.4f CI95=[%.4f,%.4f] "
          "McNemar(desc)=%.4g b=%d c=%d"
          % (p["keyacc_amt"], p["keyacc_syn"], p["delta_surface_point"],
             p["newcombe_ci95"][0], p["newcombe_ci95"][1],
             p["mcnemar_exact_p_DESCRIPTIVE"], p["amt_only_b"], p["syn_only_c"]))
    print("BRANCH-RULE VERDICT:", summary["branch_rule_verdict"])
    print("sha256 r3bridge_rows.jsonl    =", sha_rows)
    print("sha256 r3bridge_summary.json  =", sha_sum)


if __name__ == "__main__":
    if "--mock" in sys.argv:
        _run_mock()
    else:
        print("usage: modal run poc/modal/modal_nsk1_r3bridge.py::bridge "
              "[--mock|--dry-plan]  (or: python modal_nsk1_r3bridge.py --mock)")
