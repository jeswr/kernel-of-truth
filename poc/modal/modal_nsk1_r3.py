#!/usr/bin/env python3
"""modal_nsk1_r3 — the nsk1-r3 CONFIRMATORY real-mode Modal entrypoint.

EXECUTES the FROZEN record registry/experiments/nsk1-r3.json (design
docs/next/design/nsk1-r3-hardened.md §6.4 step 2-5, §7 row schema) on the
pinned harness: SmolLM2-1.7B-Instruct @ the B″/Stage-1 commit pin, additive
norm-matched contrastive injection at α = 1.0, teacher-forced margin
read-out — the B″ instrument VERBATIM (byte-mirrors of
modal_nsk1_g2._bprime2_body_impl's add_pre_hook / _chat_ids / _pad_batch /
_gen_plain / _tf_lp / donor harvest, as already re-validated on GPU by
modal_nsk1_r3bridge.py, commit 8b23a083).

CONFIRMATORY DESIGN (verbatim from the record; no knob is free here):
  * Corpus: data/nsk1-clutrr-r3 (fresh, held-out, synthetic-surface per D-1;
    kot-corpus-hash/1 digest re-verified against the frozen pin before ANY
    GPU call). Partition A (266 items) -> C1 = (16,16) ONLY; partition B
    (266 items) -> C2 = (12,16) ONLY; disjoint by construction (S9).
  * Derangement-seed families (three Sattolo derangements per partition,
    fixed-point-free ASSERT): A = {20260720, 20260721, 20260722},
    B = {20260723, 20260724, 20260725}. Coin bit per (drg-seed, item, cell) =
    g2._bprime2_coin_bit(item_id, lh, lt, seed=drg_seed).
  * Per item x its own cell: 1 text-only greedy gen (headroom gate) +
    real ± (2 tf forwards x 2 signs? no — 2 candidates x 2 signs = 4) +
    deranged ± x 3 seeds (12) + unhooked baseline (2) = 16 tf forwards
    + 2 donor forwards + 1 gen  ->  ~11.2k GPU calls total (§8.1).
  * Rows: phase:"final", gate:"NSK1-R3", host:"R3", prereg_hash = the
    record's frozen_sha256 — the §7 schema the pinned analysis/nsk1_r3.py
    consumes. The analysis FAILS CLOSED on anything short of the complete
    3-seed / 266-item endpoint, so a partial run cannot PASS.

FAIL-CLOSED REAL-MODE GATE (runner_constraints; design-stage refusal): real
mode runs ONLY if ALL hold, else the entrypoint prints the failure and exits:
  1. the record's status == "FROZEN" and its frozen_sha256 recomputes over
     the canonical bytes AND matches registry/frozen-index.json;
  2. pins.corpus_hashes["nsk1-clutrr-r3"] reproduces from data/ (kot-corpus-hash/1);
  3. pins.analysis_script.sha256 matches analysis/nsk1_r3.py's bytes;
  4. THIS FILE's own sha256 appears in pins.harness_manifest (the real-mode
     entrypoint pin) — an edited entrypoint refuses to run;
  5. NSK1_R3_RUN_AUTHORIZED=1 in the environment (Tier-2 maintainer GPU
     sign-off; never set by this repo's tooling).
Mock and dry-plan modes run the same checks in REPORT mode ($0, no GPU) and
tolerate a DRAFT record (pre-freeze green-mock use, §8.4 step 5).

Caps ENFORCED IN-RUNNER (record budget): USD 25 / 10 GPU-h (in-container
hard stop 36000 s) / 12 h wall (Modal timeout); expected spend is the §8.1
envelope 0.13-0.45 GPU-h ~ USD 0.18-1.35, padded ceiling <= USD 3.

    # green mock ($0, CPU stub, full 532-item pipeline -> pinned analysis):
    poc/modal/.venv/bin/python poc/modal/modal_nsk1_r3.py --mock
    # dry plan ($0):
    poc/modal/.venv/bin/modal run poc/modal/modal_nsk1_r3.py::r3 --dry-plan
    # real (runner role; AFTER prereg-freeze + Tier-2 sign-off):
    NSK1_R3_RUN_AUTHORIZED=1 poc/modal/.venv/bin/modal run poc/modal/modal_nsk1_r3.py::r3
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import modal

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1] if len(_HERE.parents) > 1 else _HERE
sys.path.insert(0, str(_HERE))

# ---- VERBATIM reuse of the B" instrument's builders/scorers/helpers ----
import modal_nsk1_g2 as g2  # noqa: E402  (single-file module, container-safe import)

R3_MODEL = g2.STAGE1_MODEL                 # SmolLM2-1.7B-Instruct (R3)
R3_PIN = g2.STAGE1_PIN                     # commit pin (ABORT otherwise)
R3_ALPHA = 1.0                             # record: fixed, the only measured keying strength
CELLS = {"A": {"cell": (16, 16), "seeds": (20260720, 20260721, 20260722)},   # C1 PRIMARY
         "B": {"cell": (12, 16), "seeds": (20260723, 20260724, 20260725)}}   # C2 replication
N_PARTITION = 266                          # complete partition size (count-gate MEASURED)
R3_BATCH = 16                              # B" GPU mini-batch (OOM auto-halves)
R3_GPU_S_CAP = 36000                       # HARD in-container stop = the 10 GPU-h record cap
R3_WALL_S_CAP = 43200                      # 12 h wall (also the Modal timeout)
RECORD_PATH = _ROOT / "registry/experiments/nsk1-r3.json"
FROZEN_INDEX = _ROOT / "registry/frozen-index.json"
ANALYSIS_PATH = _ROOT / "analysis/nsk1_r3.py"
CORPUS = "nsk1-clutrr-r3"
OUT_DIR = _ROOT / "poc/nsk1/out/r3"

app = modal.App("kot-nsk1-r3")
image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install(*g2._image_pins())
         .add_local_python_source("modal_nsk1_g2"))
hf_cache = modal.Volume.from_name("kot-hf-cache", create_if_missing=True)


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# ============================================== freeze / pin verification
def _verify_freeze(require_frozen: bool):
    """All real-mode gates (fail-closed). Returns (record, prereg_hash,
    failures) — failures is [] iff every gate holds. Mock/dry-plan call with
    require_frozen=False (a DRAFT record reports, never blocks the $0 path);
    real mode calls with True and REFUSES on any failure."""
    sys.path.insert(0, str(_ROOT / "tools/registry"))
    import kot_common as kc  # noqa: E402
    failures = []
    record = json.loads(RECORD_PATH.read_text())
    prereg_hash = record.get("frozen_sha256")

    if record.get("status") != "FROZEN":
        failures.append("record status=%r != FROZEN (design-stage harness refuses "
                        "real mode; run prereg-freeze first)" % record.get("status"))
    elif prereg_hash != kc.frozen_hash(record):
        failures.append("frozen_sha256 does not recompute over the canonical record bytes")
    idx = json.loads(FROZEN_INDEX.read_text()) if FROZEN_INDEX.is_file() else {}
    if record.get("status") == "FROZEN" and idx.get("nsk1-r3") != prereg_hash:
        failures.append("frozen-index.json entry missing or != record frozen_sha256")

    want_corpus = record["pins"]["corpus_hashes"].get(CORPUS)
    got_corpus = kc.corpus_hash(str(_ROOT), CORPUS)
    if got_corpus != want_corpus:
        failures.append("corpus pin mismatch: recomputed %s != pinned %s"
                        % (got_corpus, want_corpus))

    want_an = record["pins"]["analysis_script"]["sha256"]
    got_an = _sha(ANALYSIS_PATH.read_bytes())
    if got_an != want_an:
        failures.append("analysis pin mismatch: %s sha %s != pinned %s"
                        % (record["pins"]["analysis_script"]["path"], got_an, want_an))

    self_sha = _sha(Path(__file__).resolve().read_bytes())
    if self_sha not in record["pins"]["harness_manifest"]:
        failures.append("ENTRYPOINT pin mismatch: this file's sha %s is not in "
                        "pins.harness_manifest — an edited entrypoint refuses to run"
                        % self_sha)

    if R3_PIN not in record["pins"]["model_revisions"]["R3"]:
        failures.append("model pin drift: record model_revisions.R3 does not carry %s" % R3_PIN)

    if require_frozen and os.environ.get("NSK1_R3_RUN_AUTHORIZED") != "1":
        failures.append("NSK1_R3_RUN_AUTHORIZED != 1 (Tier-2 maintainer GPU "
                        "sign-off env gate)")
    return record, prereg_hash, failures


# ===================================================================== build
def _build_specs_r3():
    """Per-partition specs from data/nsk1-clutrr-r3 (532 covered items),
    prompt + donor construction BYTE-IDENTICAL to g2._build_specs_bprime2
    (form-2 prompt 'Story:\\n<story>\\nQuestion: Who is the <rel> of
    <base>?\\n<INSTRUCTION_ENTITY>'; donors 'Note: the <rs> of <base> is
    <NAME>.' differing ONLY in the answer-slot name). Every B" build assert
    is live. Returns {partition: [spec, ...]} in items.jsonl file order."""
    lex = json.loads((_ROOT / "data" / CORPUS / "lexicon.json").read_text())
    rel_surface = {v: k for k, v in lex["relations"].items()}  # URN -> mother/father
    by_part = {"A": [], "B": []}
    seen_ids = set()
    for line in (_ROOT / "data" / CORPUS / "items.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        it = json.loads(line)
        assert it.get("stratum") == "covered", "ABORT: non-covered item %s" % it.get("item_id")
        part = it["partition"]
        assert part in by_part, "ABORT: unknown partition %r (%s)" % (part, it["item_id"])
        assert it["item_id"] not in seen_ids, "ABORT: duplicate item %s" % it["item_id"]
        seen_ids.add(it["item_id"])
        item_lex = it["lexicon"]
        surfaces = list(item_lex.values())
        assert len(item_lex) == 3 and len({s.lower() for s in surfaces}) == 3, \
            "ABORT: item %s not 3-name pairwise-distinct" % it["item_id"]
        subj_urn = it["hop1"]["subject"]
        bridge_urn = it["hop1_bridge"]
        base_surface = item_lex[subj_urn]
        top_urns = [u for u in item_lex if u not in (subj_urn, bridge_urn)]
        assert len(top_urns) == 1, "ABORT: item %s no unique chain-top" % it["item_id"]
        top_surface = item_lex[top_urns[0]]
        bridge_surface = item_lex[bridge_urn]
        story = "\n".join(it["context"])
        q2 = "Who is the %s of %s?" % (it["gold_surface"], base_surface)
        prompt = "Story:\n%s\nQuestion: %s\n%s" % (story, q2, g2.INSTRUCTION_ENTITY)
        rs = rel_surface[it["hop1"]["rel"]]
        prefix = "Note: the %s of %s is " % (rs, base_surface)
        d_top, d_bridge = prefix + top_surface + ".", prefix + bridge_surface + "."
        # donors differ ONLY in the name slot; gold never in D_bridge (S9-3/4 re-assert)
        assert d_top[:len(prefix)] == d_bridge[:len(prefix)] and d_top[-1] == d_bridge[-1] == "."
        assert top_surface.lower() not in d_bridge.lower(), \
            "ABORT: gold name in D_bridge (%s)" % it["item_id"]
        by_part[part].append({
            "item_id": it["item_id"], "prompt": prompt,
            "d_top": d_top, "d_bridge": d_bridge,
            "top_surface": top_surface, "bridge_surface": bridge_surface,
            "gold_top": top_surface, "base": base_surface, "surfaces": surfaces,
        })
    for part in ("A", "B"):
        assert len(by_part[part]) == N_PARTITION, \
            "ABORT: partition %s n=%d != %d" % (part, len(by_part[part]), N_PARTITION)
    assert not ({s["item_id"] for s in by_part["A"]}
                & {s["item_id"] for s in by_part["B"]}), "ABORT: A∩B non-empty"
    return by_part


def _sigmas(n, seeds):
    """Three independent Sattolo derangements over partition-local file order
    (g2._bp_sattolo VERBATIM); fixed-point-free ASSERT per seed."""
    out = {}
    for sd in seeds:
        p = g2._bp_sattolo(n, sd)
        assert all(p[k] != k for k in range(n)), "ABORT: sigma seed=%d fixed point" % sd
        out[sd] = p
    return out


# ============================================================ shared compute
class _CapStop(Exception):
    """Raised when the in-runner hard caps trip (hard stop)."""


def _mini(items, batch):
    for a in range(0, len(items), batch):
        yield items[a:a + batch]


def _row(prereg_hash, **kw):
    base = {"phase": "final", "gate": "NSK1-R3", "host": "R3", "model": R3_MODEL,
            "form": "2", "prereg_hash": prereg_hash,
            "item_id": None, "probe": None, "cell": None, "arm": None,
            "sign": None, "seed": None, "coin": None, "alpha": None,
            "lp_top": None, "lp_bridge": None, "gen": None, "correct": None,
            "gold": None, "config": None}
    base.update(kw)
    return base


def _r3_compute(part, specs, sigma_by_seed, ctx, prereg_hash, batch=R3_BATCH, log=print):
    """The FULL confirmatory measurement for ONE partition/cell over a ctx
    (real GPU closures or the mock stub): text-only gen, real ± margins,
    deranged ± x 3 seeds (+ coin bit), unhooked baseline. Emits the §7 row
    schema the pinned analysis consumes. ABORT on non-finite (fail-closed)."""
    lh, lt = CELLS[part]["cell"]
    seeds = CELLS[part]["seeds"]
    n = len(specs)
    order = list(range(n))
    rows = []
    cfg = {"cell": [lh, lt], "partition": part}

    # ---- text-only pass (headroom gate + substratum labels) ----
    n_ok = 0
    for mb in _mini(order, batch):
        gens = ctx.gen(part, mb)
        for i, gtxt in zip(mb, gens):
            s = specs[i]
            ok = bool(g2._score_entity(gtxt, s["gold_top"], s["base"], s["surfaces"]))
            n_ok += int(ok)
            rows.append(_row(prereg_hash, item_id=s["item_id"], probe="text-only",
                             gen=gtxt, correct=ok, gold=s["gold_top"],
                             config=dict(cfg)))
    log("[r3] %s text-only acc=%.4f" % (part, n_ok / n))

    # ---- teacher-forced margins: real ± and deranged ± x 3 seeds ----
    def _pair(mb, sign, src_of):
        lpt = ctx.tf_lp(part, mb, "top", sign, src_of)
        lpb = ctx.tf_lp(part, mb, "bridge", sign, src_of)
        return lpt, lpb

    k_real = 0
    for mb in _mini(order, batch):
        rp = _pair(mb, 1, None)      # real: item's OWN donor
        rm = _pair(mb, -1, None)
        drg = {sd: (_pair(mb, 1, sigma_by_seed[sd]),
                    _pair(mb, -1, sigma_by_seed[sd])) for sd in seeds}
        for r_idx, i in enumerate(mb):
            s = specs[i]
            rp_t, rp_b = rp[0][r_idx], rp[1][r_idx]
            rm_t, rm_b = rm[0][r_idx], rm[1][r_idx]
            vals = [rp_t, rp_b, rm_t, rm_b]
            for sd in seeds:
                vals += [drg[sd][0][0][r_idx], drg[sd][0][1][r_idx],
                         drg[sd][1][0][r_idx], drg[sd][1][1][r_idx]]
            if not all(math.isfinite(v) for v in vals):
                raise g2._B2Abort("NAN_MARGINS item=%s cell=%s" % (s["item_id"], (lh, lt)))
            k_real += int((rp_t - rp_b) > (rm_t - rm_b))
            rows.append(_row(prereg_hash, item_id=s["item_id"], probe="margin",
                             cell=[lh, lt], arm="real", sign=1, alpha=R3_ALPHA,
                             lp_top=rp_t, lp_bridge=rp_b, gold=s["gold_top"],
                             config=dict(cfg)))
            rows.append(_row(prereg_hash, item_id=s["item_id"], probe="margin",
                             cell=[lh, lt], arm="real", sign=-1, alpha=R3_ALPHA,
                             lp_top=rm_t, lp_bridge=rm_b, gold=s["gold_top"],
                             config=dict(cfg)))
            for sd in seeds:
                b = g2._bprime2_coin_bit(s["item_id"], lh, lt, seed=sd)
                (dp_t, dp_b), (dm_t, dm_b) = \
                    (drg[sd][0][0][r_idx], drg[sd][0][1][r_idx]), \
                    (drg[sd][1][0][r_idx], drg[sd][1][1][r_idx])
                rows.append(_row(prereg_hash, item_id=s["item_id"], probe="margin",
                                 cell=[lh, lt], arm="drg", sign=1, seed=sd, coin=b,
                                 alpha=R3_ALPHA, lp_top=dp_t, lp_bridge=dp_b,
                                 gold=s["gold_top"], config=dict(cfg, seed=sd)))
                rows.append(_row(prereg_hash, item_id=s["item_id"], probe="margin",
                                 cell=[lh, lt], arm="drg", sign=-1, seed=sd, coin=b,
                                 alpha=R3_ALPHA, lp_top=dm_t, lp_bridge=dm_b,
                                 gold=s["gold_top"], config=dict(cfg, seed=sd)))
    log("[r3] %s cell=%s keyacc_real=%.4f" % (part, (lh, lt), k_real / n))

    # ---- unhooked baselines (reported) ----
    for mb in _mini(order, batch):
        lpt = ctx.tf_lp(part, mb, "top", None, None)
        lpb = ctx.tf_lp(part, mb, "bridge", None, None)
        for r_idx, i in enumerate(mb):
            s = specs[i]
            if not (math.isfinite(lpt[r_idx]) and math.isfinite(lpb[r_idx])):
                raise g2._B2Abort("NAN_BASELINE item=%s" % s["item_id"])
            rows.append(_row(prereg_hash, item_id=s["item_id"], probe="baseline",
                             lp_top=lpt[r_idx], lp_bridge=lpb[r_idx],
                             gold=s["gold_top"], config=dict(cfg)))
    return rows


def _validate_rows(rows, prereg_hash):
    """Fail-closed schema + completeness pre-check BEFORE the rows are handed
    to verdict-gen: exact key set, phase/gate/prereg_hash tags, and the full
    pre-registered census — per partition 266 items x (1 text-only + 1
    baseline + 2 real + 6 drg) = 2660 rows, every declared seed present.
    (The pinned analysis re-enforces completeness independently.)"""
    req = {"phase", "gate", "host", "model", "form", "prereg_hash", "item_id",
           "probe", "cell", "arm", "sign", "seed", "coin", "alpha", "lp_top",
           "lp_bridge", "gen", "correct", "gold", "config"}
    census = {p: {} for p in CELLS}
    for r in rows:
        assert set(r.keys()) == req, "ROW_SCHEMA: keys drift: %s" % sorted(set(r) ^ req)
        assert r["phase"] == "final" and r["gate"] == "NSK1-R3", "ROW_SCHEMA: phase/gate"
        assert r["prereg_hash"] == prereg_hash, "ROW_SCHEMA: prereg_hash drift"
        assert r["probe"] in ("text-only", "baseline", "margin"), "ROW_SCHEMA: probe"
        part = r["config"]["partition"]
        c = census[part].setdefault(r["item_id"], [])
        if r["probe"] == "margin":
            assert tuple(r["cell"]) == CELLS[part]["cell"], "ROW_SCHEMA: cell/partition"
            assert r["arm"] in ("real", "drg") and r["sign"] in (1, -1), "ROW_SCHEMA: margin"
            assert (r["seed"] in CELLS[part]["seeds"]) == (r["arm"] == "drg"), "ROW_SCHEMA: seed"
            c.append((r["arm"], r["sign"], r["seed"]))
        else:
            c.append((r["probe"], None, None))
    for part, items in census.items():
        assert len(items) == N_PARTITION, \
            "CENSUS: partition %s items=%d != %d" % (part, len(items), N_PARTITION)
        want = {("text-only", None, None), ("baseline", None, None),
                ("real", 1, None), ("real", -1, None)} | \
               {("drg", sg, sd) for sg in (1, -1) for sd in CELLS[part]["seeds"]}
        for iid, got in items.items():
            assert set(got) == want and len(got) == len(want), \
                "CENSUS: item %s incomplete (%d/%d rows)" % (iid, len(got), len(want))
    return len(rows)


# ============================================================== GPU (remote)
def _r3_body(model_id, specs_by_part, sigma_lists_by_part, prereg_hash,
             batch_size, gpu_s_cap):
    import traceback
    try:
        return _r3_body_impl(model_id, specs_by_part, sigma_lists_by_part,
                             prereg_hash, batch_size, gpu_s_cap)
    except Exception as e:  # noqa: BLE001
        tb = traceback.format_exc()
        print("R3 ERROR:", repr(e))
        print(tb)
        return {"aborted": True, "abort_reason": "EXCEPTION: %s" % repr(e),
                "traceback": tb, "rows": []}


def _r3_body_impl(model_id, specs_by_part, sigma_lists_by_part, prereg_hash,
                  batch_size, gpu_s_cap):
    """GPU body. The injection + teacher-forced read-out is a BYTE-MIRROR of
    modal_nsk1_g2._bprime2_body_impl (B"), as already GPU-revalidated by
    modal_nsk1_r3bridge._bridge_body_impl; the only structural changes are
    (i) one partition per cell with its own derangement family, (ii) donor
    harvest at the partition's own ℓh, (iii) the record hard caps."""
    import time
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(model_id, revision=R3_PIN)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(
        model_id, revision=R3_PIN, torch_dtype=torch.float32)
    model.to("cuda").eval()
    L = int(model.config.num_hidden_layers)
    commit = getattr(model.config, "_commit_hash", None)
    if commit is not None and commit != R3_PIN:
        return {"aborted": True, "abort_reason":
                "COMMIT_PIN_MISMATCH got=%s want=%s" % (commit, R3_PIN), "rows": []}
    if L != 24:
        return {"aborted": True, "abort_reason": "L_NOT_24 got=%d" % L, "rows": []}
    layers = model.model.layers
    calls = {"tf": 0, "gen": 0, "donor": 0}
    print("[r3] model=%s L=%d commit=%s alpha=%s" % (model_id, L, commit, R3_ALPHA))

    def _caps():
        el = time.time() - t0
        if el > gpu_s_cap:
            raise _CapStop("HARD_CAP gpu_s=%.0f > %d (10 GPU-h record cap)"
                           % (el, gpu_s_cap))

    # ---- additive norm-matched pre-hook: BYTE-MIRROR of B" add_pre_hook ----
    hook_state = {"vec": None, "wpos": None}

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
        u = st["vec"].to(hs.dtype)
        wpos = st["wpos"]
        bs = hs.shape[0]
        rows_ = torch.arange(bs, device=hs.device)
        cur = hs[rows_, wpos, :]
        nrm = cur.norm(dim=-1, keepdim=True)
        hs[rows_, wpos, :] = cur + nrm * u
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

    all_rows = []
    aborted, abort_reason = False, None
    try:
        for part in ("A", "B"):
            specs = specs_by_part[part]
            n = len(specs)
            lh, lt = CELLS[part]["cell"]
            sigma_by_seed = {int(sd): list(p) for sd, p in sigma_lists_by_part[part]}

            prompt_ids = [ _chat_ids(s["prompt"]) for s in specs ]
            cand_ids = []
            for s in specs:
                d = {}
                for key, name in (("top", s["top_surface"]), ("bridge", s["bridge_surface"])):
                    cid = tok(" " + name, add_special_tokens=False).input_ids
                    assert len(cid) >= 1, "ABORT: empty cand ids (%s)" % s["item_id"]
                    d[key] = list(cid)
                cand_ids.append(d)

            def _tf_lp(mb, cand_key, lt_, vec_for):
                try:
                    id_lists = [prompt_ids[i] + cand_ids[i][cand_key] for i in mb]
                    clens = [len(cand_ids[i][cand_key]) for i in mb]
                    ii, am, maxlen = _pad_batch(id_lists)
                    wrows = [maxlen - clens[r] - 1 for r in range(len(mb))]
                    for r, i in enumerate(mb):
                        if int(ii[r, wrows[r]].item()) != prompt_ids[i][-1]:
                            raise g2._B2Abort("WRITE_INDEX_MISMATCH item=%s"
                                              % specs[i]["item_id"])
                    handle = None
                    if lt_ is not None and vec_for is not None:
                        u = torch.stack([vec_for(i) for i in mb]).to("cuda")
                        hook_state["vec"] = u
                        hook_state["wpos"] = torch.tensor(wrows, device="cuda",
                                                          dtype=torch.long)
                        handle = layers[lt_].register_forward_pre_hook(
                            add_pre_hook, with_kwargs=True)
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
                    return _tf_lp(mb[:h], cand_key, lt_, vec_for) + \
                        _tf_lp(mb[h:], cand_key, lt_, vec_for)

            # donor harvest: Δ̂v per item at this partition's ℓh (B" Step 4)
            dhat = {}
            for i, s in enumerate(specs):
                _caps()
                hv = {}
                for key, name, text in (("top", s["top_surface"], s["d_top"]),
                                        ("bridge", s["bridge_surface"], s["d_bridge"])):
                    enc = tok(text, return_offsets_mapping=True)
                    ti = _last_name_tok(text, name, enc["offset_mapping"])
                    if ti is None:
                        raise g2._B2Abort("NAME_LOCATION donor=%s item=%s"
                                          % (key, s["item_id"]))
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
            print("[r3] %s donors harvested n=%d t=%.0fs" % (part, n, time.time() - t0))

            class _Ctx:
                def gen(self, _part, mb):
                    _caps()
                    calls["gen"] += len(mb)
                    return _gen_plain([prompt_ids[i] for i in mb])

                def tf_lp(self, _part, mb, cand_key, sign, src_of):
                    _caps()
                    calls["tf"] += len(mb)
                    if sign is None:
                        return _tf_lp(mb, cand_key, None, None)
                    if src_of is None:
                        vf = (lambda i, sgn=sign: R3_ALPHA * sgn * dhat[i])
                    else:
                        vf = (lambda i, sgn=sign, p=src_of: R3_ALPHA * sgn * dhat[p[i]])
                    return _tf_lp(mb, cand_key, lt, vf)

            all_rows += _r3_compute(part, specs, sigma_by_seed, _Ctx(),
                                    prereg_hash, batch_size)
    except (_CapStop, g2._B2Abort) as e:
        aborted, abort_reason = True, str(e)
        print("[r3] HARD STOP:", abort_reason)

    import time as _t
    return {"aborted": aborted, "abort_reason": abort_reason,
            "rows": [json.loads(json.dumps(r, default=str)) for r in all_rows],
            "model_commit": commit, "L": L, "calls": calls,
            "elapsed_s": _t.time() - t0}


@app.function(image=image, gpu="A10G", volumes={g2.HF_CACHE_MOUNT: hf_cache},
              timeout=R3_WALL_S_CAP)
def r3_a10g(model_id, specs_by_part, sigma_lists_by_part, prereg_hash,
            batch_size, gpu_s_cap):
    r = _r3_body(model_id, specs_by_part, sigma_lists_by_part, prereg_hash,
                 batch_size, gpu_s_cap)
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
    Same call signature as the GPU ctx so _r3_compute runs the FULL pipeline
    through the identical code path. Mock numbers are FAKE mechanism-check
    values, never evidence."""

    def __init__(self, specs):
        self.specs = specs

    def gen(self, part, mb):
        out = []
        for i in mb:
            s = self.specs[i]
            u = _h01("gen|%s|%s" % (part, s["item_id"]))
            out.append("The answer is %s." % (s["gold_top"] if u < 0.79 else s["base"]))
        return out

    def tf_lp(self, part, mb, cand_key, sign, src_of):
        out = []
        for i in mb:
            s = self.specs[i]
            if sign is None:
                out.append(-2.0 - 4.0 * _h01("base|%s|%s" % (s["item_id"], cand_key)))
                continue
            donor_item = s["item_id"] if src_of is None else \
                self.specs[src_of[i]]["item_id"]
            arm = "real" if src_of is None else "drg"
            key = "lp|%s|%s|%s|%s|%d" % (s["item_id"], donor_item, arm, cand_key, sign)
            lp = -2.0 - 4.0 * _h01(key)
            if arm == "real" and _h01("works|%s" % s["item_id"]) < 0.86:
                lp += 0.9 * sign * (1 if cand_key == "top" else -1)
            out.append(lp)
        return out


def _run_mock():
    """GREEN MOCK (§8.4 step 5): the FULL 532-item pipeline on the CPU stub,
    schema + census validation, then the rows are piped through the PINNED
    analysis (analysis/nsk1_r3.py) exactly as verdict-gen will — proving row
    schema x analysis compatibility INCLUDING the fail-closed completeness
    guard (endpoint_complete must come back true on the complete mock world,
    and the analysis --selftest proves the incomplete worlds are rejected)."""
    print("=== nsk1-r3 MOCK VALIDATION (stubbed forward, $0, no GPU) ===")
    record, prereg_hash, failures = _verify_freeze(require_frozen=False)
    prereg_hash = prereg_hash or "MOCK-UNFROZEN"
    print("freeze-gate report (real mode requires ALL green):")
    if failures:
        for f in failures:
            print("  [would-refuse] %s" % f)
    else:
        print("  all real-mode gates green")

    specs_by_part = _build_specs_r3()
    rows = []
    for part in ("A", "B"):
        sigma = _sigmas(len(specs_by_part[part]), CELLS[part]["seeds"])
        rows += _r3_compute(part, specs_by_part[part], sigma,
                            _MockCtx(specs_by_part[part]), prereg_hash, batch=32)
    nrows = _validate_rows(rows, prereg_hash)
    print("row schema + full census: PASS (%d rows = 2x266x10)" % nrows)

    proc = subprocess.run([sys.executable, str(ANALYSIS_PATH)],
                          input="\n".join(json.dumps(r) for r in rows),
                          capture_output=True, text=True, check=True)
    out = json.loads(proc.stdout)
    assert out["gates"]["endpoint_complete"] is True, "MOCK: completeness guard tripped"
    assert out["gates"]["instrument_valid"] is True, "MOCK: instrument gate tripped"
    assert isinstance(out["analysis"]["primary_confirmed"], bool)
    st = subprocess.run([sys.executable, str(ANALYSIS_PATH), "--selftest"],
                        capture_output=True, text=True)
    assert st.returncode == 0 and "SELFTEST_PASS" in st.stdout, \
        "MOCK: analysis --selftest failed"
    print("pinned analysis on mock rows: endpoint_complete=true instrument_valid=true "
          "primary_confirmed=%s (FAKE mock number, never evidence)"
          % out["analysis"]["primary_confirmed"])
    print("analysis --selftest (fail-closed guard proof): PASS")

    mock_dir = OUT_DIR / "mock"
    mock_dir.mkdir(parents=True, exist_ok=True)
    with open(mock_dir / "mock_rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    with open(mock_dir / "mock_analysis.json", "w") as f:
        json.dump({"mode": "MOCK (stubbed forward; numbers are fake and meaningless "
                           "— validation of pipeline only)",
                   "freeze_gate_failures_would_refuse_real": failures,
                   "analysis_output": out}, f, indent=1, sort_keys=True)
    print("mock rows -> %s" % (mock_dir / "mock_rows.jsonl"))
    print("MOCK_VALIDATION_PASS = True")
    return True


# ============================================================== entrypoints
def _print_plan(specs_by_part, prereg_hash):
    print("=== nsk1-r3 CONFIRMATORY PLAN (phase:final, gate:NSK1-R3) ===")
    for part in ("A", "B"):
        print("partition %s -> cell %s, n=%d, drg seeds %s"
              % (part, CELLS[part]["cell"], len(specs_by_part[part]),
                 list(CELLS[part]["seeds"])))
    n = sum(len(v) for v in specs_by_part.values())
    print("model      : %s @ %s (pin ABORT on drift; L==24 ABORT)" % (R3_MODEL, R3_PIN))
    print("prereg_hash: %s" % prereg_hash)
    print("GPU calls  : donors %d + teacher-forced %d + gens %d (§8.1 envelope "
          "0.13-0.45 GPU-h ~ USD 0.18-1.35; padded ceiling <= USD 3)"
          % (n * 2, n * 18, n))
    print("hard caps  : USD 25 / 10 GPU-h (in-container stop %ds) / 12 h wall "
          "(Modal timeout) / 1xA10G" % R3_GPU_S_CAP)


@app.local_entrypoint()
def r3(mock: bool = False, dry_plan: bool = False):
    if mock:
        _run_mock()
        return
    record, prereg_hash, failures = _verify_freeze(require_frozen=not dry_plan)
    if dry_plan:
        specs_by_part = _build_specs_r3()
        _print_plan(specs_by_part, prereg_hash or "(record not frozen yet)")
        if failures:
            print("\nreal-mode gates that WOULD refuse:")
            for f in failures:
                print("  - %s" % f)
        print("\nDRY-PLAN ONLY — no GPU launched, $0 spent. All build asserts passed.")
        return
    if failures:
        print("REAL MODE REFUSED (fail-closed):")
        for f in failures:
            print("  - %s" % f)
        raise SystemExit(1)

    specs_by_part = _build_specs_r3()
    _print_plan(specs_by_part, prereg_hash)
    sigma_lists_by_part = {
        part: [[sd, _sigmas(len(specs_by_part[part]), CELLS[part]["seeds"])[sd]]
               for sd in CELLS[part]["seeds"]]
        for part in ("A", "B")}
    res = r3_a10g.remote(R3_MODEL, specs_by_part, sigma_lists_by_part,
                         prereg_hash, R3_BATCH, R3_GPU_S_CAP)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if res.get("aborted"):
        with open(OUT_DIR / "r3_abort.json", "w") as f:
            json.dump({"aborted": True, "abort_reason": res.get("abort_reason"),
                       "traceback": res.get("traceback"), "calls": res.get("calls"),
                       "phase": "final", "gate": "NSK1-R3",
                       "prereg_hash": prereg_hash}, f, indent=1)
        print("ABORTED (INSTRUMENT-INVALID path):", res.get("abort_reason"))
        raise SystemExit(1)
    rows = res["rows"]
    _validate_rows(rows, prereg_hash)
    with open(OUT_DIR / "r3_rows.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    with open(OUT_DIR / "r3_run_meta.json", "w") as f:
        json.dump({"mode": "REAL", "phase": "final", "gate": "NSK1-R3",
                   "prereg_hash": prereg_hash,
                   "model_commit_resolved": res["model_commit"],
                   "calls_made": res["calls"], "elapsed_s": res["elapsed_s"]},
                  f, indent=1, sort_keys=True)
    print("rows -> %s (sha256 %s)" % (OUT_DIR / "r3_rows.jsonl",
                                      _sha((OUT_DIR / "r3_rows.jsonl").read_bytes())))
    print("NEXT: non-runner verdict-gen over the rows (run != audit); "
          "PASS resolves to PASS-PENDING-AUDIT until a non-runner audit CONFIRMS.")


if __name__ == "__main__":
    if "--mock" in sys.argv:
        _run_mock()
    else:
        print("usage: modal run poc/modal/modal_nsk1_r3.py::r3 [--mock|--dry-plan]  "
              "(or: python modal_nsk1_r3.py --mock)")
