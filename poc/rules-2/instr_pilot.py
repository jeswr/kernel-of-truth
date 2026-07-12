#!/usr/bin/env python3
"""RULES-2 BLOCKING INSTRUMENT PILOT (pre-freeze validity gate;
PROPOSED-ASM-1814..1819, poc/rules-2/asm-instrpilot-1814-1819.json).

WHY THIS EXISTS (docs/next/analysis/correctness-track-instrument-assessment.md
SS2.2 + SS4 item 1, the meta-recommendation): four instrument events in this
lane — capped by rules-1-c freezing and then grading INSTRUMENT-INVALID —
share one process gap: no gate channel was EXERCISED at the operating point
before freeze. This pilot is that gate for RULES-2 REWORK-3. It runs the
REAL instrument (real R1 host, real pinned-HP LoRA, real entity surface,
real twin engine for B4) on a TINY deterministic slice and reports,
fail-closed and mechanically, whether each measurement channel has dynamic
range BEFORE the coordinator freezes registry/experiments/rules-2.json.

THE SPECIFIC RISK IT GATES: the rules-1-c ENTITY frame is a 2-option
surface. On rules-1-c that surface made the A3 verify-retry arm VACUOUS
(every row attempts=1; A3=c1). RULES-2's train-time arms do not use
verify-retry, but a 2-option S-out could still make the trained-vs-base
contrast DEGENERATE (both arms floored at chance 0.5, or both saturated),
the c1p forced-flip control could collapse (to abstention or onto the
treatment), the c8 shortcut audit could be passing VACUOUSLY (a gate that
cannot fire is not a gate), and B4 inherits the rules-1-c vacuity outright
(PROPOSED-ASM-1808).

PILOT GATES (all mechanical; thresholds pre-declared below as constants):
  IP-1 separation   B2-pilot (LoRA on a deterministic ~27% family-stratified
                    subsample of the pinned entity corpus, pinned HPs, 1
                    seed) vs B0 on n=60 pilot S-out covered items, uniform
                    3-option decode. PASS iff (a) acc_B0 <= 0.90 (headroom;
                    not saturated), (b) acc_B2p clears the exact one-sided
                    binomial 95% bound vs chance 0.5 at the pilot n (not
                    floored), (c) acc_B2p - acc_B0 >= 0.05 (the contrast
                    moves), (d) covered-refusal rate <= 0.5 on both arms
                    (the channel is answers, not abstention).
  IP-2 audit teeth  the c8 train-bytes projection (duplicated semantics —
                    precedent: materialise_closure.query_pair_item) is run
                    on the pilot S-out slice twice: REAL train bytes must
                    recover <= the pinned ceiling (0.10), and a PLANTED
                    exploiter (pilot S-out (base, rel)->gold injected into
                    the lookup) must push recovered acc ABOVE the ceiling,
                    i.e. the gate predicate FIRES on a genuine shortcut.
                    A shortcut audit that cannot fire is INSTRUMENT-INVALID.
  IP-3 c1p control  the forced-flip derangement arm (same subsample, same
                    HPs) must be NON-DEGENERATE: covered-refusal rate <= 0.5
                    (no abstention collapse) AND acc_c1p <= acc_B2p - 0.05
                    (no collapse onto the treatment; the anti-correlated
                    construction PROPOSED-ASM-1803 predicts it lands at or
                    below the B0 floor).
  IP-4 B4 vacuity   RULES-1-C A3 verbatim (k=4, twin engine at inference)
                    on 24 pilot items: FLAG b4_vacuous=true iff every row
                    has attempts==1 (the rules-1-c vacuity, PROPOSED-ASM-
                    1808, inherited byte-identically). A FLAG, not a FAIL:
                    s3' is already conditional and B4's fate belongs to the
                    maintainer's issue #24 — but the flag must be MEASURED
                    at the operating point, not argued.
Verdict: PILOT-PASS (IP-1..3 pass, no flag), PILOT-PASS-WITH-FLAGS (IP-1..3
pass, b4_vacuous fired — expected), PILOT-FAIL otherwise. A PILOT-FAIL
BLOCKS the freeze pending redesign or an explicit coordinator override
record (PROPOSED-ASM-1814). This module states NO feasibility conclusion;
pilot rows are instrument-validation rows, NEVER campaign evidence.

WHAT THIS BUILD DOES NOT TOUCH: rules2_runner.py / materialise_closure.py /
merge_shards.py / inputs/ / data/ / modal_rules2.py — the pinned campaign
staged-bytes manifest sha (d37640b2... at build time) is byte-identical
before and after this build. The pilot is a STANDALONE runner precisely so
the validated campaign surface does not drift (the frozen-candidate mock
artifact stays green).

Usage:
  python3 instr_pilot.py --out-dir /tmp/ip --mock              # stub LM, $0
  python3 instr_pilot.py --out-dir /tmp/ip --mock --mock-degenerate
                                     # planted-degenerate stub: gates must FAIL
  python3 instr_pilot.py --out-dir /tmp/ip --dry-plan          # cost plan, $0
  python3 instr_pilot.py --out-dir /tmp/ip --device cuda       # real (Modal)

HARD RULES: --mock/--dry-plan spend $0, no GPU, no network; every mock
number is labelled MOCK; the $2 pilot cost cap is enforced fail-closed by
--dry-plan and by the modal wrapper's launch gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from math import comb

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import rules2_runner as r2  # noqa: E402  (pin gates + drivers, reused)

# ---------------------------------------------------------------------------
# Pre-declared pilot constants (PROPOSED-ASM-1815..1819). Changing ANY of
# these after a coordinator has read a pilot result requires a fresh pilot.
# ---------------------------------------------------------------------------
PILOT_USD_CAP = 2.0          # hard fail-closed cost cap (ASM-1819)
PILOT_N_SOUT = 60            # covered S-out pilot slice (deterministic sha order)
PILOT_N_CONTROL = 10         # engine-refusal control slice
PILOT_N_B4 = 24              # B4 verify-retry pilot slice (IP-4)
PILOT_TRAIN_N = 6000         # family-stratified train subsample (~27% of 21780)
PILOT_SEED = 0               # single pilot seed (ASM-1819: validity, not effect size)
IP1_B0_HEADROOM_MAX = 0.90   # (a) not saturated
IP1_ALPHA = 0.05             # (b) exact one-sided binomial vs chance 0.5
IP1_MIN_GAP = 0.05           # (c) contrast moves
IP1_REFUSAL_MAX = 0.50       # (d) no abstention collapse (both arms)
IP3_REFUSAL_MAX = 0.50       # c1p: no abstention collapse
IP3_MIN_GAP = 0.05           # c1p must sit >= this below B2-pilot
IP2_PLANT_MIN_RECOVERY = 0.90  # the planted exploiter must actually recover


def binom_min_k(n, p, alpha):
    """Smallest k with P(Bin(n,p) >= k) <= alpha (exact; stdlib only)."""
    for k in range(n + 1):
        tail = sum(comb(n, i) * (p ** i) * ((1 - p) ** (n - i))
                   for i in range(k, n + 1))
        if tail <= alpha:
            return k
    return n + 1


def sha_order(tag, ids):
    return sorted(ids, key=lambda i: hashlib.sha256(
        ("%s|%s" % (tag, i)).encode()).hexdigest())


# ---------------------------------------------------------------------------
# IP-2: c8 projection semantics, duplicated VERBATIM from
# materialise_closure.c8 (ent_key / qa+factline indexes / project) so the
# pilot does not depend on the internals of a nested closure — the same
# duplication precedent as materialise_closure.query_pair_item vs
# rules1_runner.query_pair. Any drift in the c8 semantics is caught by the
# pinned c8ResultSha256 artifact, which this runner verifies before running.
# ---------------------------------------------------------------------------
def _ent_key(q):
    if q.startswith("Who is the ") and " of " in q and q.endswith("?"):
        rel, base = q[len("Who is the "):-1].split(" of ", 1)
        return (base, rel)
    return None


def _build_lookup(train):
    qa, factline = {}, {}
    for e in train:
        k = _ent_key(e["question"])
        if k is not None:
            qa.setdefault(k, set()).add(e["answer"])
        else:
            qa.setdefault((e["question"], "#typing"), set()).add(e["answer"])
        for line in e["context"]:
            if " is " in line and "'s " in line and line.endswith("."):
                left, right = line[:-1].split(" is ", 1)
                if "'s " in right:
                    subj, word = right.rsplit("'s ", 1)
                    factline.setdefault((subj, word), set()).add(left)
    return qa, factline


def _project(qa, factline, base, rel):
    hits = qa.get((base, rel)) or factline.get((base, rel))
    if not hits:
        return None
    return sorted(hits)[0] if len(hits) == 1 else "AMBIG"


def _score_sout(qa, factline, pilot_cov, ctx):
    n = rec = corr = 0
    for it in pilot_cov:
        iid = it["item_id"]
        a, _b = ctx["pair"][iid]
        base = ctx["names"][iid].get(a, a)
        rel = ctx["rel_word"][iid]
        gold = ctx["ent_gold"][iid]
        p = _project(qa, factline, base, rel)
        n += 1
        if p not in (None, "AMBIG"):
            rec += 1
            corr += int(p == gold)
    return {"n": n, "recovered": rec, "recovered_correct": corr,
            "recovered_acc": (corr / n) if n else None}


def ip2_audit_teeth(corpus, pilot_cov, ctx, ceiling):
    """REAL train bytes must stay under the ceiling on the pilot slice AND a
    planted exploiter must push recovery over it (the gate can FIRE)."""
    train = [e for e in corpus if e["split"] == "train"]
    qa, factline = _build_lookup(train)
    real = _score_sout(qa, factline, pilot_cov, ctx)
    # plant: inject each pilot item's (base, rel) -> gold into the QA index
    # — exactly the shortcut the audit exists to catch. Eval names are
    # token-disjoint from training names (materialiser guard), so the plant
    # cannot collide into AMBIG.
    qa_planted = {k: set(v) for k, v in qa.items()}
    for it in pilot_cov:
        iid = it["item_id"]
        a, _b = ctx["pair"][iid]
        base = ctx["names"][iid].get(a, a)
        qa_planted.setdefault((base, ctx["rel_word"][iid]),
                              set()).add(ctx["ent_gold"][iid])
    planted = _score_sout(qa_planted, factline, pilot_cov, ctx)
    real_ok = (real["recovered_acc"] is not None
               and real["recovered_acc"] <= ceiling)
    fires = (planted["recovered_acc"] is not None
             and planted["recovered_acc"] > ceiling
             and planted["recovered_acc"] >= IP2_PLANT_MIN_RECOVERY)
    return {"pass": bool(real_ok and fires),
            "real_lookup": real, "planted_exploiter": planted,
            "ceiling": ceiling,
            "real_under_ceiling": bool(real_ok),
            "gate_fires_on_planted_exploiter": bool(fires),
            "note": "IP-2 (PROPOSED-ASM-1816): projection semantics "
                    "duplicated verbatim from materialise_closure.c8 "
                    "(qa+factline flat lookup, no joins, no inference); the "
                    "plant injects the pilot S-out (base, rel)->gold keys — "
                    "an audit that does not fire on that is vacuous"}


# ---------------------------------------------------------------------------
# Training subsample (deterministic, family-stratified; ASM-1819)
# ---------------------------------------------------------------------------
def pilot_subsample(corpus, n_target):
    train = [e for e in corpus if e["split"] == "train"]
    by_fam = {}
    for e in train:
        by_fam.setdefault(e["family"], []).append(e["id"])
    frac = n_target / float(len(train))
    keep = set()
    for fam, ids in sorted(by_fam.items()):
        take = max(1, int(round(frac * len(ids))))
        keep.update(sha_order("instrpilot-train", ids)[:take])
    sub = [e for e in corpus if e["split"] != "train" or e["id"] in keep]
    return sub, keep


# ---------------------------------------------------------------------------
def dry_plan(man, corpus, byid, shuf, ups, pilot_cov, pilot_ctl, pilot_b4,
             ctx, man1, gpu):
    """Char-accurate $0 cost plan for the pilot, mirroring its execution:
    2 LoRA trainings (subsample, pinned HPs) + 3 arm evals on the pilot
    slice (3-option decode) + B4 on the 2-option surface (attempt factor 2,
    conservative). Fail-closed at PILOT_USD_CAP."""
    plan = man["planning"]
    hp = man["lora"]
    frames = man["prompt_frames"]
    refusal = man["refusal_answer"]
    cpt = plan["chars_per_token_estimate"]
    usd = plan["usd_per_hour"][gpu]
    tput_e = plan["throughput_tok_per_s_eval"][gpu]["R1"]
    tput_t = plan["throughput_tok_per_s_train"][gpu]["R1"]

    sub, keep = pilot_subsample(corpus, PILOT_TRAIN_N)
    train_tok = {}
    for arm in ("B2", "c1p"):
        texts = r2.build_training_texts(arm, sub, shuf, ups, byid, frames,
                                        refusal)
        train_tok[arm] = sum(len(p) + len(c) for p, c in texts) / cpt \
            * hp["epochs"]

    sout = r2.sout_cells(pilot_cov, pilot_ctl, ctx, frames, refusal)
    eval_tok_one_arm = sum(
        len(r2.render_prompt(frames, c["lines"], c["question"])) / cpt * 3
        for c in sout)
    b4_tok = sum(len(r2.gap2_prompt(ctx, man1["prompt_frames"],
                                    it["item_id"])) / cpt * 2 * 2.0
                 for it in pilot_b4)  # 2 options x attempt factor 2

    hours = (sum(train_tok.values()) / tput_t
             + 3 * eval_tok_one_arm / tput_e     # B0, B2p, c1p
             + b4_tok / tput_e) / 3600.0
    worst_h = hours * plan["overhead_factor"]
    est_usd, worst_usd = hours * usd, worst_h * usd
    ok = worst_usd <= PILOT_USD_CAP
    print("\n".join([
        "rules-2 INSTRUMENT PILOT --dry-plan (ESTIMATES ONLY; $0 spent by "
        "this command; planning constants from rules2-manifest.json)",
        "",
        "pilot slice: %d covered + %d control S-out, %d B4 items; train "
        "subsample %d/%d examples x %d epochs (pinned HPs), 1 seed"
        % (len(pilot_cov), len(pilot_ctl), len(pilot_b4), len(keep),
           sum(1 for e in corpus if e["split"] == "train"), hp["epochs"]),
        "train tokens: %s | eval tokens/arm: %.2fM x 3 arms | B4: %.2fM"
        % ({a: "%.2fM" % (t / 1e6) for a, t in train_tok.items()},
           eval_tok_one_arm / 1e6, b4_tok / 1e6),
        "GPU-hours on %s: est %.3f h; with %.1fx overhead %.3f h"
        % (gpu, hours, plan["overhead_factor"], worst_h),
        ]))
    print("cost at Modal list $%.2f/h: est $%.2f / worst $%.2f"
          % (usd, est_usd, worst_usd))
    print("  %-52s %s" % ("worst case vs PILOT_USD_CAP ($%.2f)"
                          % PILOT_USD_CAP,
                          "OK" if ok else "OVER — DO NOT LAUNCH"))
    return ok


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs-dir", default=os.path.join(_HERE, "inputs"))
    ap.add_argument("--data-root", default=os.path.join(_ROOT, "data"))
    ap.add_argument("--corpus-dir",
                    default=os.path.join(_ROOT, "data", "rules2-train"))
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--gpu-class", default="A10G",
                    choices=["T4", "A10G", "A100"])
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--mock-degenerate", action="store_true",
                    help="mock ONLY: zero the planted stub gradient so the "
                         "pilot gates themselves are exercised on a "
                         "degenerate instrument (IP-1/IP-3 must FAIL)")
    ap.add_argument("--dry-plan", action="store_true")
    args = ap.parse_args()
    if args.mock_degenerate and not args.mock:
        raise SystemExit("ERR_ARGS: --mock-degenerate requires --mock "
                         "(the degenerate gradient is a stub-teeth check, "
                         "never a real run)")
    t0 = time.time()

    # G1 pin gates + pinned imports + frame-drift guards — REUSED VERBATIM
    # from rules2_runner (raw bytes hashed BEFORE import; certificate + c8
    # preconditions; ERR_PIN / ERR_CERT_PRECONDITION / ERR_C8_GATE /
    # ERR_FRAME_DRIFT all apply to the pilot unchanged).
    man, cert, c8res = r2.verify_pins_pre_import(args)
    r2._import_pinned()
    man1 = r2.load_inputs(args, man)
    corpus, byid, shuf, ups, samples, cman = r2.load_corpus(args)
    dc = man["design_constants_from_design_doc"]
    frames = man["prompt_frames"]
    refusal = man["refusal_answer"]
    hp = man["lora"]
    r1 = r2.r1

    class _A:
        data_root = args.data_root
    items, ctx = r1.build_context(_A, man1)
    covered = [i for i in items if i["stratum"] == "covered"]
    control = [i for i in items if i["stratum"] != "covered"]
    if len(covered) != dc["n_sout_covered"] or \
            len(control) != dc["n_sout_control"]:
        raise SystemExit("ERR_EVAL_COUNTS: %d/%d != %d/%d"
                         % (len(covered), len(control),
                            dc["n_sout_covered"], dc["n_sout_control"]))

    # deterministic pilot slices (sha order; disjoint concerns, may overlap
    # item-wise between S-out and B4 — same instrument, different channel)
    cov_by_id = {i["item_id"]: i for i in covered}
    ctl_by_id = {i["item_id"]: i for i in control}
    pilot_cov = [cov_by_id[i] for i in sha_order(
        "instrpilot-sout", list(cov_by_id))[:PILOT_N_SOUT]]
    pilot_ctl = [ctl_by_id[i] for i in sha_order(
        "instrpilot-ctl", list(ctl_by_id))[:PILOT_N_CONTROL]]
    pilot_b4 = [cov_by_id[i] for i in sha_order(
        "instrpilot-b4", list(cov_by_id))[:PILOT_N_B4]]

    if args.dry_plan:
        ok = dry_plan(man, corpus, byid, shuf, ups, pilot_cov, pilot_ctl,
                      pilot_b4, ctx, man1, args.gpu_class)
        sys.exit(0 if ok else 2)

    os.makedirs(args.out_dir, exist_ok=True)

    def log(msg):
        print("[instrpilot %7.1fs] %s" % (time.time() - t0, msg), flush=True)

    # ---- IP-2 first: $0 CPU, fail-closed before any GPU second is spent
    ceiling = c8res["gate"]["ceiling"]
    ip2 = ip2_audit_teeth(corpus, pilot_cov, ctx, ceiling)
    log("IP-2 audit-teeth: real %s <= %.2f: %s; planted fires: %s"
        % (ip2["real_lookup"]["recovered_acc"], ceiling,
           ip2["real_under_ceiling"],
           ip2["gate_fires_on_planted_exploiter"]))

    # ---- row plumbing (rules-1 RowEmitter, renamed like rules2_runner)
    suffix = ("-mock" if args.mock else "") + \
        ("-deg" if args.mock_degenerate else "")
    emitter = r1.RowEmitter(args.out_dir, suffix)
    stray = emitter.path
    emitter.path = os.path.join(args.out_dir,
                                "run-records-instrpilot%s.jsonl" % suffix)
    if os.path.exists(stray) and stray != emitter.path:
        os.remove(stray)
    with open(emitter.path, "w"):
        pass

    mockspec = None
    if args.mock:
        mockspec = json.loads(json.dumps(man["mock"]))  # deep copy
        if args.mock_degenerate:
            # planted-DEGENERATE stub: no content signal, no format signal,
            # c1p rides the same (zero) gradient => IP-1 and IP-3 must FAIL.
            # A stub-mechanics choice exercising the PILOT's own teeth;
            # never a measurement.
            mockspec["ft_content_bonus"] = 0.0
            mockspec["ft_format_bonus"] = 0.0
            mockspec["smem_lookup_bonus"] = 0.0
            mockspec["c1p_format_bonus"] = 0.0

    sout = r2.sout_cells(pilot_cov, pilot_ctl, ctx, frames, refusal)
    sout_prompt_sha = hashlib.sha256(json.dumps(
        [r2.render_prompt(frames, c["lines"], c["question"]) for c in sout],
        separators=(",", ":")).encode()).hexdigest()
    timeout = r2.CELL_TIMEOUT_S_DEFAULT[args.gpu_class]

    def eval_arm(lm, arm):
        guard = r2.CellGuard("instrpilot/%s" % arm, timeout,
                             r2.MAX_GEN_PER_ITEM)
        r2.eval_cells(lm, sout, arm, "R1", PILOT_SEED, frames, refusal,
                      emitter, guard)
        log("eval %s done (%.1fs)" % (arm, guard.elapsed()))

    def make_lm(arm):
        if args.mock:
            return r2.StubR2LM("R1", arm, mockspec, refusal)
        return r1.Rules1HFLM(man["model_revisions"]["R1"]["repo"],
                             man["model_revisions"]["R1"]["revision"],
                             args.device)

    # ---- B0 (base host)
    eval_arm(make_lm("B0"), "B0")

    # ---- B2-pilot + c1p-pilot (LoRA on the deterministic subsample,
    #      pinned HPs verbatim — ONLY the data volume is reduced, ASM-1819)
    sub, keep = pilot_subsample(corpus, PILOT_TRAIN_N)
    training_ledger = {}
    for arm in ("B2", "c1p"):
        texts = r2.build_training_texts(arm, sub, shuf, ups, byid, frames,
                                        refusal)
        if args.mock:
            lm = r2.StubR2LM("R1", arm, mockspec, refusal)
            training_ledger[arm] = {"mode": "MOCK", "n_examples": len(texts)}
        else:
            log("LoRA %s-pilot (%d examples, pinned HPs, seed %d)..."
                % (arm, len(texts), PILOT_SEED))
            lm, ledger = r2.train_lora(man["model_revisions"]["R1"], texts,
                                       hp, PILOT_SEED, args.device, log)
            ledger["mode"] = "REAL"
            training_ledger[arm] = ledger
        eval_arm(lm, arm)
        if not args.mock:
            del lm
            import torch
            if args.device == "cuda":
                torch.cuda.empty_cache()

    # ---- B4 (rules-1-c A3 verbatim, k=4, twin engine at inference) — IP-4
    b4_lm = (r1.StubRulesLM("R1", {
        "stub_skill": man["mock"]["b4_stub"]["stub_skill"],
        "stub_injection_bonus": man["mock"]["b4_stub"]
        ["stub_injection_bonus"],
        "stub_feedback_bonus": man["mock"]["b4_stub"]["stub_feedback_bonus"]})
        if args.mock else
        r1.Rules1HFLM(man["model_revisions"]["R1"]["repo"],
                      man["model_revisions"]["R1"]["revision"], args.device))
    guard = r2.CellGuard("instrpilot/B4", timeout, r2.MAX_GEN_PER_ITEM)
    r1.run_verify_retry_cell(b4_lm, "B4", man1["prompt_frames"], pilot_b4,
                             ctx, ctx["payload_true"], ctx["tbox_true"],
                             dc["k_retry_b4"], PILOT_SEED, emitter, guard)
    log("eval B4 done (%.1fs)" % guard.elapsed())

    # ---- gate arithmetic (mechanical; no model judgement anywhere)
    def arm_stats(arm):
        cov = [r for r in emitter.rows
               if r["arm"] == arm and r["cell"] == "entailed"]
        ctl = [r for r in emitter.rows
               if r["arm"] == arm and r["cell"] == "control"]
        return {"n": len(cov),
                "acc": (sum(r["item_correct_ext"] for r in cov)
                        / len(cov)) if cov else None,
                "refusal_rate_covered": (sum(r["refused"] for r in cov)
                                         / len(cov)) if cov else None,
                "control_refusal_rate": (sum(r["refused"] for r in ctl)
                                         / len(ctl)) if ctl else None}

    b0, b2p, c1p = arm_stats("B0"), arm_stats("B2"), arm_stats("c1p")
    min_k = binom_min_k(PILOT_N_SOUT, 0.5, IP1_ALPHA)
    ip1_floor_bound = min_k / float(PILOT_N_SOUT)
    ip1 = {
        "b0": b0, "b2_pilot": b2p,
        "binom_min_correct": min_k,
        "binom_min_acc": ip1_floor_bound,
        "cond_a_b0_headroom": bool(b0["acc"] <= IP1_B0_HEADROOM_MAX),
        "cond_b_b2p_above_floor": bool(b2p["acc"] >= ip1_floor_bound),
        "cond_c_gap": bool(b2p["acc"] - b0["acc"] >= IP1_MIN_GAP),
        "cond_d_refusal": bool(
            b0["refusal_rate_covered"] <= IP1_REFUSAL_MAX
            and b2p["refusal_rate_covered"] <= IP1_REFUSAL_MAX),
    }
    ip1["pass"] = bool(ip1["cond_a_b0_headroom"]
                       and ip1["cond_b_b2p_above_floor"]
                       and ip1["cond_c_gap"] and ip1["cond_d_refusal"])
    ip3 = {
        "c1p": c1p,
        "cond_no_abstention_collapse": bool(
            c1p["refusal_rate_covered"] <= IP3_REFUSAL_MAX),
        "cond_no_treatment_collapse": bool(
            c1p["acc"] <= b2p["acc"] - IP3_MIN_GAP),
    }
    ip3["pass"] = bool(ip3["cond_no_abstention_collapse"]
                       and ip3["cond_no_treatment_collapse"])
    b4_rows = [r for r in emitter.rows
               if r["arm"] == "B4" and r["cell"] == "entailed"]
    attempts = sorted({r["attempts"] for r in b4_rows})
    ip4 = {"n": len(b4_rows), "attempts_values": attempts,
           "b4_vacuous": bool(b4_rows and attempts == [1]),
           "note": "IP-4 (PROPOSED-ASM-1818): attempts==1 everywhere = the "
                   "rules-1-c A3 vacuity (PROPOSED-ASM-1808) inherited at "
                   "the operating point; a FLAG for the issue-#24 B4/s3' "
                   "disposition, not a pilot FAIL"}
    if not b4_rows:
        raise SystemExit("ERR_IP4_EMPTY: B4 emitted no entailed rows")

    gates_pass = ip1["pass"] and ip2["pass"] and ip3["pass"]
    verdict = ("PILOT-FAIL" if not gates_pass else
               ("PILOT-PASS-WITH-FLAGS" if ip4["b4_vacuous"]
                else "PILOT-PASS"))

    records_sha = r2.sha256_file(emitter.path)
    result = {
        "experiment": "rules-2 INSTRUMENT PILOT (pre-freeze validity gate)",
        "asm_block": "PROPOSED-ASM-1814..1819 "
                     "(poc/rules-2/asm-instrpilot-1814-1819.json)",
        "mode": "MOCK" if args.mock else "REAL",
        "mock_degenerate": bool(args.mock_degenerate),
        "verdict": verdict,
        "verdict_semantics": "instrument-validity ONLY — a PASS licenses "
                             "the coordinator to proceed to the freeze "
                             "checklist; it is NEVER evidence for any "
                             "rules-2 hypothesis, and MOCK verdicts "
                             "validate pilot mechanics only",
        "blocking_rule": "PROPOSED-ASM-1814: PILOT-FAIL blocks prereg-"
                         "freeze of registry/experiments/rules-2.json "
                         "pending redesign or an explicit coordinator "
                         "override record",
        "date": r2.utcnow(),
        "device": args.device,
        "seed": PILOT_SEED,
        "pilot_constants": {
            "n_sout": PILOT_N_SOUT, "n_control": PILOT_N_CONTROL,
            "n_b4": PILOT_N_B4, "train_subsample_n": len(keep),
            "train_total_n": sum(1 for e in corpus
                                 if e["split"] == "train"),
            "lora_hps": "pinned rules2-manifest values verbatim "
                        "(epochs=%d)" % hp["epochs"],
            "usd_cap": PILOT_USD_CAP},
        "gates": {"ip1_separation": ip1, "ip2_audit_teeth": ip2,
                  "ip3_c1p_control": ip3, "ip4_b4_vacuity_flag": ip4},
        "training_ledger": training_ledger,
        "sout_prompt_surface_sha256": sout_prompt_sha,
        "records_file": os.path.basename(emitter.path),
        "records_sha256": records_sha,
        "n_rows": len(emitter.rows),
        "pins": man["pins"],
        "pins_verified": True,
        "campaign_bytes_untouched_note": "the pilot stages/loads the pinned "
                                         "campaign bytes read-only; the "
                                         "campaign staged-bytes manifest "
                                         "(modal_rules2.py --print-manifest)"
                                         " is unchanged by the pilot build",
        "wallClockHours": (time.time() - t0) / 3600.0,
    }
    out = os.path.join(args.out_dir, "instrpilot-result%s.json" % suffix)
    with open(out, "w") as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write("\n")
    log("VERDICT: %s (IP-1 %s, IP-2 %s, IP-3 %s, B4-vacuous %s) -> %s"
        % (verdict, ip1["pass"], ip2["pass"], ip3["pass"],
           ip4["b4_vacuous"], out))
    sys.exit(0 if gates_pass else 3)


if __name__ == "__main__":
    main()
