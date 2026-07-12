#!/usr/bin/env python3
"""UFO-CHECK-0 GPU runner (design §8; registry/experiments/ufo-check-0.json).

Five-arm verify-retry over PRE-MATERIALISED checker fixtures: the GPU path
does ZERO symbolic work — every checker decision is a byte lookup in
inputs/fixtures/accept-tables.jsonl (PROPOSED-ASM-1483; NO sparq anywhere).

  A0 no-checker | AG gUFO-taxonomy | AU UFO-SN3 | AD deranged | AN rep-null

MECHANISM (design §3): greedy first pass computed ONCE per (item, host) and
SHARED across all five arms (exact pairing by construction); k=1 licensed
rejection -> ONE seeded retry with the rejection message appended; the retry
answer is final. Seeds {0,1,2} govern retry sampling only.

REUSE: HFLM forced-choice scorer + seeded retry sampler imported READ-ONLY
from poc/f2b-transfer/runner/f2bt_runner.py at its PINNED sha
(ERR_SCORER_PIN; the f2b-transfer tree is byte-untouched). Retry sampling
therefore uses the f2bt pinned sampler's generator discipline verbatim.

MODES:
  --mock      StubLM mechanics check on CPU; $0; labelled MOCK end-to-end
  --dry-plan  FIXTURE-TOKENIZED cost plan vs the registry caps (review
              fix 8): every prompt, retry frame and rejection message is
              tokenized with the PINNED tokenizer — no chars-per-token
              guessing; $0, runs nothing
  real        REQUIRES: the record FROZEN (ERR_RUNNER_ROLE), fixtures
              re-verified in-run (ERR_FIXTURES_PRECONDITION /
              ERR_FIXTURE_SHA), every manifest pin matching (ERR_PIN)

BUDGET HARD STOPS (review fix 8): a BudgetGuard enforces the registry caps
(usd_cap $20 at the gpu-class list rate, gpu_hours_cap 6, wall_clock 12 h)
DURING the run — breach flushes all completed rows and exits with a named
ERR_BUDGET_* code; nothing is fabricated.

Checkpointing: per (host, arm, seed) cell; completed cells are skipped on
restart (2-shared-core box discipline / Modal reruns).

Outputs (out-dir): run-records-ufo0[-mock].jsonl, run-sidecar[-mock].json,
results-ufo0[-mock].json. RAW metrics only — verdicts belong to the pinned
analysis/ufo_check_0.py + verdict-gen under run-vs-audit separation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.normpath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, _HERE)
import twin_ufo as tw  # noqa: E402  (asserts the rules-1 twin pin)

ANSWERS = ("ENTAILED", "CONTRADICTED", "UNDERDETERMINED")
EXTRACT_RE = re.compile(r"^\s*(ENTAILED|CONTRADICTED|UNDERDETERMINED)\b")
ARMS = ("A0", "AG", "AU", "AD", "AN")
HOSTS = ("r135", "r360")
SEEDS = (0, 1, 2)
RETRY_FRAME = ("%s\n\nYour first answer was: %s.\n%s\nAnswer with exactly "
               "one word: ENTAILED, CONTRADICTED, or UNDERDETERMINED.")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def det_u(*keys):
    raw = "\x1f".join(str(k) for k in keys)
    h = hashlib.sha256(raw.encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big") / 2.0 ** 64


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(ln) for ln in f if ln.strip()]


# ---------------------------------------------------------------------------
# Pinned f2bt scorer import (ERR_SCORER_PIN) — READ-ONLY reuse.
# ---------------------------------------------------------------------------
def load_f2bt(pin):
    path = os.path.join(_REPO, "poc", "f2b-transfer", "runner",
                        "f2bt_runner.py")
    got = sha256_file(path)
    if got != pin:
        raise SystemExit("ERR_SCORER_PIN: f2bt_runner.py sha %s != manifest "
                         "pin %s — refusing (READ-ONLY reuse contract)"
                         % (got, pin))
    sys.path.insert(0, os.path.dirname(path))
    import f2bt_runner  # noqa: PLC0415
    return f2bt_runner


# ---------------------------------------------------------------------------
class BudgetGuard:
    """Hard stops at the REGISTRY caps (review fix 8): usd, gpu-hours,
    wall-clock. Breach => flush + named exit; never converted into data."""

    def __init__(self, caps, usd_per_hour, on_gpu):
        self.t0 = time.monotonic()
        self.usd_cap = float(caps["usd_cap"])
        self.gpu_cap_h = float(caps["gpu_hours_cap"])
        self.wall_cap_h = float(caps["wall_clock_cap_hours"])
        self.rate = float(usd_per_hour) if on_gpu else 0.0
        self.on_gpu = on_gpu

    def hours(self):
        return (time.monotonic() - self.t0) / 3600.0

    def usd(self):
        return self.hours() * self.rate

    def check(self):
        h = self.hours()
        if h > self.wall_cap_h:
            raise SystemExit("ERR_BUDGET_WALL_CLOCK: %.2fh > cap %.1fh "
                             "(completed cells are flushed)"
                             % (h, self.wall_cap_h))
        if self.on_gpu and h > self.gpu_cap_h:
            raise SystemExit("ERR_BUDGET_GPU_HOURS: %.2fh > cap %.1fh"
                             % (h, self.gpu_cap_h))
        if self.usd() > self.usd_cap:
            raise SystemExit("ERR_BUDGET_USD: $%.2f > cap $%.2f"
                             % (self.usd(), self.usd_cap))


# ---------------------------------------------------------------------------
class StubLM:
    """SYNTHETIC mechanics-only stand-in (mock; no torch). Deterministic
    sha-driven answers with a planted skill toward the fixture gold plus a
    planted retry gain — exists ONLY so the analysis contract's gates and
    denominators resolve during mock validation. Never a measurement
    (knull mock precedent)."""

    def __init__(self, host, gold_by_item, spec):
        self.host = host
        self.gold = gold_by_item
        self.skill = spec["stub_skill"][host]
        self.retry_skill = spec["stub_retry_skill"][host]
        self.xfail = spec["stub_extraction_fail_rate"]
        self.n_active = spec["stub_n_active"][host]
        self.name = "stub-%s" % host

    def choose(self, item_id, seed, attempt):
        gold = self.gold[item_id]
        if gold not in ANSWERS:  # OOP probes have no three-way gold
            gold = "UNDERDETERMINED"
        if det_u("xfail", self.host, item_id, seed, attempt) < self.xfail:
            return "MALFORMED"
        p = self.skill if attempt == 0 else self.retry_skill
        if det_u("ans", self.host, item_id, seed, attempt) < p:
            return gold
        wrong = [a for a in ANSWERS if a != gold]
        return wrong[int(det_u("wr", self.host, item_id, seed, attempt)
                         * len(wrong))]


class HflmAdapter:
    """Thin adapter over the pinned f2bt HFLM: three-way forced choice on
    the FULL prompt bytes; attempt 0 greedy, attempt >0 the f2bt seeded
    sampler (its pinned generator discipline, verbatim)."""

    def __init__(self, f2bt, repo, revision, device):
        self.lm = f2bt.HFLM(repo, revision, device)
        self.name = self.lm.name
        self.n_active = self.lm.n_active

    def choose(self, prompt, seed, attempt):
        ans, _conf = self.lm.choose({"id": "x"}, list(ANSWERS), None, seed,
                                    attempt, prompt=prompt)
        return ans


# ---------------------------------------------------------------------------
def verify_pins(man, args):
    checks = {
        "items": (args.items, man["pins"]["items_sha256"]),
        "gold": (os.path.join(args.fixtures_dir, "gold.jsonl"),
                 man["pins"]["gold_sha256"]),
        "accept-tables": (os.path.join(args.fixtures_dir,
                                       "accept-tables.jsonl"),
                          man["pins"]["accept_tables_sha256"]),
        "floors": (os.path.join(args.fixtures_dir, "floors.jsonl"),
                   man["pins"]["floors_sha256"]),
        "fixtures-meta": (os.path.join(args.fixtures_dir,
                                       "fixtures-meta.json"),
                          man["pins"]["fixtures_meta_sha256"]),
        "fixtures-sha": (os.path.join(args.fixtures_dir,
                                      "fixtures-sha.json"),
                         man["pins"]["fixtures_sha_json_sha256"]),
    }
    for name, (path, want) in sorted(checks.items()):
        got = sha256_file(path)
        if got != want:
            raise SystemExit("ERR_PIN: %s: %s sha %s != manifest pin %s"
                             % (name, path, got, want))


def find_tokenizer(args, man):
    cands = [args.tokenizer] if args.tokenizer else []
    cands += [os.path.expanduser(p) for p in man["tokenizer"]["paths"]]
    for p in cands:
        if p and os.path.isfile(p):
            got = sha256_file(p)
            if got != man["tokenizer"]["sha256"]:
                raise SystemExit("ERR_TOKENIZER_PIN: %s sha %s != pin %s"
                                 % (p, got, man["tokenizer"]["sha256"]))
            from tokenizers import Tokenizer
            return Tokenizer.from_file(p), p
    raise SystemExit("ERR_TOKENIZER_PIN: no pinned tokenizer.json found "
                     "(pass --tokenizer)")


def reverify_fixtures(args, tok_path, committed):
    """In-run re-verification (design §4.3): re-materialise ONCE and compare
    against the committed double-run proof; ERR_FIXTURE_SHA on drift."""
    import materialise as mz  # noqa: PLC0415
    mz.self_test()
    tok, _sha = mz.tokenizer_or_die(tok_path, None)
    items = mz.load_items(args.items)
    fixtures, meta = mz.materialise(items, tok,
                                    committed["derange_attempt"])
    got = mz.canonical_fixture_sha(fixtures, meta)
    if got != committed["fixtures_sha_run1"]:
        raise SystemExit("ERR_FIXTURE_SHA: in-run recompute %s != committed "
                         "%s" % (got, committed["fixtures_sha_run1"]))
    return got


# ---------------------------------------------------------------------------
def dry_plan(man, items, tables, tok, gpu):
    """FIXTURE-TOKENIZED cost plan (review fix 8): exact token counts of
    every prompt (x3 forced-choice options) and every worst-case retry
    frame, at the PINNED tokenizer; compared against the registry caps."""
    plan = man["planning"]
    caps = man["caps"]
    tput = plan["throughput_tok_per_s"][gpu]  # per-host tok/s table
    usd_h = plan["usd_per_hour"][gpu]
    opt_toks = sum(len(tok.encode(" %s" % a).ids) for a in ANSWERS)

    per_host_first = 0
    for it in items:
        t = len(tok.encode(it["prompt"]).ids)
        per_host_first += t * 3 + opt_toks  # forced choice scores 3 options

    # worst case: EVERY rejectable cell rejects -> one retry per scored item
    # x checker arm x seed (per host) whose accept table rejects >=1 answer.
    per_host_retry = 0
    n_retry_cells = 0
    by_key = {(r["item_id"], r["arm"]): r for r in tables}
    for it in items:
        for arm in ("AG", "AU", "AD", "AN"):
            row = by_key[(it["item_id"], arm)]
            worst = 0
            for ans in ANSWERS:
                cell = row["table"][ans]
                if cell["accept"]:
                    continue
                frame = RETRY_FRAME % (it["prompt"], ans, cell["message"])
                worst = max(worst, len(tok.encode(frame).ids) * 3 + opt_toks)
            if worst:
                per_host_retry += worst * len(SEEDS)
                n_retry_cells += len(SEEDS)
    per_host_total = per_host_first + per_host_retry
    hours = sum(per_host_total / tput[h] for h in HOSTS) / 3600.0
    total = per_host_total * len(HOSTS)
    worst_h = hours * plan["overhead_factor"]
    lines = [
        "ufo-check-0 --dry-plan (FIXTURE-TOKENIZED at the pinned tokenizer;",
        "$0, no GPU, no network; planning throughput is an ESTIMATE)",
        "",
        "items: %d (first pass shared across arms, %d hosts)"
        % (len(items), len(HOSTS)),
        "first-pass forced-choice tokens per host: %d" % per_host_first,
        "worst-case retry tokens per host: %d (%d retry cells)"
        % (per_host_retry, n_retry_cells),
        "total worst-case tokens: %d" % total,
        "",
        "GPU-hours on %s (tok/s %s): %.3f h; with %.1fx overhead: %.3f h"
        % (gpu, tput, hours, plan["overhead_factor"], worst_h),
        "cost at $%.2f/h: point $%.2f, worst $%.2f"
        % (usd_h, hours * usd_h, worst_h * usd_h),
        "caps: usd %.0f, gpu-hours %.0f, wall %.0f h"
        % (caps["usd_cap"], caps["gpu_hours_cap"],
           caps["wall_clock_cap_hours"]),
    ]
    checks = [
        ("worst-case $ vs usd_cap", worst_h * usd_h <= caps["usd_cap"]),
        ("worst-case h vs gpu_hours_cap", worst_h <= caps["gpu_hours_cap"]),
        ("worst-case h vs wall_clock_cap",
         worst_h <= caps["wall_clock_cap_hours"]),
    ]
    for name, ok in checks:
        lines.append("  %-34s %s" % (name, "OK" if ok
                                     else "OVER — DO NOT LAUNCH"))
    print("\n".join(lines))
    return all(ok for _n, ok in checks)


# ---------------------------------------------------------------------------
def run(args, man, items, gold_by_item, tables, floors, tok, guard, log):
    mock = args.mock
    by_key = {(r["item_id"], r["arm"]): r for r in tables}
    fl_key = {(r["item_id"], r["arm"]): r["floors"] for r in floors}
    hosts = args.hosts.split(",") if args.hosts else list(HOSTS)
    seeds = [int(x) for x in args.seeds.split(",")] if args.seeds \
        else list(SEEDS)
    arms = args.arms.split(",") if args.arms else list(ARMS)

    os.makedirs(args.out_dir, exist_ok=True)
    suffix = "-mock" if mock else ""
    rec_path = os.path.join(args.out_dir, "run-records-ufo0%s.jsonl" % suffix)
    done_path = os.path.join(args.out_dir, "cells-done%s.json" % suffix)
    done = json.load(open(done_path)) if os.path.isfile(done_path) else []
    if not done and os.path.exists(rec_path):
        os.remove(rec_path)

    def mark_done(cell):
        done.append(cell)
        with open(done_path, "w") as f:
            json.dump(done, f)

    def emit_rows(rows):
        with open(rec_path, "a", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())

    n_ext_fail = 0
    n_gen = 0
    lms = {}

    def lm_for(host):
        if host not in lms:
            if mock:
                lms[host] = StubLM(host, gold_by_item, man["mock"])
            else:
                f2bt = load_f2bt(man["pins"]["f2bt_runner_sha256"])
                spec = man["models"][host]
                lms[host] = HflmAdapter(f2bt, spec["repo"],
                                        spec["revision"], args.device)
        return lms[host]

    def gen(lm, item, seed, attempt, prompt):
        nonlocal n_gen, n_ext_fail
        guard.check()
        n_gen += 1
        if mock:
            raw = lm.choose(item["item_id"], seed, attempt)
        else:
            raw = lm.choose(prompt, seed, attempt)
        m = EXTRACT_RE.match(raw or "")
        ok = bool(m)
        if not ok:
            n_ext_fail += 1
        return (m.group(1) if ok else raw), ok

    # ---- shared greedy first pass per (item, host), checkpointed ---------
    firstpass = {}
    for host in hosts:
        fp_path = os.path.join(args.out_dir,
                               "firstpass-%s%s.json" % (host, suffix))
        if os.path.isfile(fp_path):
            firstpass[host] = json.load(open(fp_path))
            log("first pass %s: loaded checkpoint (%d items)"
                % (host, len(firstpass[host])))
            continue
        lm = lm_for(host)
        fp = {}
        for it in items:
            ans, ok = gen(lm, it, 0, 0, it["prompt"])
            fp[it["item_id"]] = {"answer": ans, "extracted_ok": int(ok),
                                 "prompt_tokens":
                                     len(tok.encode(it["prompt"]).ids)}
        firstpass[host] = fp
        with open(fp_path, "w") as f:
            json.dump(fp, f, sort_keys=True)
        log("first pass %s: %d items (greedy, shared across arms)"
            % (host, len(fp)))

    # ---- arm x host x seed cells (lookup + k=1 retry) ---------------------
    opt_out_tokens = 1  # forced-choice answer = one option emission
    for host in hosts:
        lm = lm_for(host)
        for arm in arms:
            for seed in seeds:
                cell = "%s/%s/%s" % (host, arm, seed)
                if cell in done:
                    log("cell %s: checkpointed, skipping" % cell)
                    continue
                rows = []
                for it in items:
                    fp = firstpass[host][it["item_id"]]
                    first, ext_ok = fp["answer"], fp["extracted_ok"]
                    gold = gold_by_item[it["item_id"]]
                    rejected = retried = 0
                    final = first
                    msg_tokens = 0
                    checker_us = 0.0
                    if arm != "A0" and ext_ok:
                        t0 = time.perf_counter()
                        trow = by_key[(it["item_id"], arm)]
                        cellt = trow["table"][first]
                        checker_us = (time.perf_counter() - t0) * 1e6
                        if not cellt["accept"]:
                            rejected = 1
                            msg = cellt["message"]
                            hits = tw.lint_message(msg)
                            if hits:
                                raise SystemExit(
                                    "ERR_MESSAGE_DISCIPLINE: %s/%s: %s"
                                    % (it["item_id"], arm, hits))
                            msg_tokens = len(tok.encode(msg).ids)
                            retry_prompt = RETRY_FRAME % (it["prompt"],
                                                          first, msg)
                            final, r_ok = gen(lm, it, seed, 1, retry_prompt)
                            ext_ok = ext_ok and int(r_ok)
                            retried = 1
                    correct = int(ext_ok and final == gold)
                    dw = int(ext_ok and (
                        (final == "ENTAILED" and gold == "CONTRADICTED")
                        or (final in ("ENTAILED", "CONTRADICTED")
                            and gold == "UNDERDETERMINED")))
                    if arm == "A0":
                        fl = {"uniform": float(correct),
                              "always_u": float(correct),
                              "cycle": float(correct)}
                    elif first in ANSWERS:
                        fl = fl_key[(it["item_id"], arm)].get(
                            first, {"uniform": 0.0, "always_u": 0.0,
                                    "cycle": 0.0})
                    else:
                        fl = {"uniform": 0.0, "always_u": 0.0, "cycle": 0.0}
                    prompt_toks = fp["prompt_tokens"]
                    tokens_in = prompt_toks * 3 + (msg_tokens * 3
                                                   if retried else 0)
                    rows.append({
                        "item_id": it["item_id"], "family": it["family"],
                        "gold": gold, "host": host, "arm": arm,
                        "seed": seed, "first_answer": first,
                        "rejected": rejected, "retried": retried,
                        "final_answer": final, "correct": correct,
                        "dangerous_wrong": dw, "extracted_ok": int(ext_ok),
                        "floor_uniform": fl["uniform"],
                        "floor_always_u": fl["always_u"],
                        "floor_cycle": fl["cycle"],
                        "tokens_in": tokens_in,
                        "tokens_out": opt_out_tokens * (2 if retried
                                                        else 1),
                        "rejection_msg_tokens": msg_tokens,
                        "flops_formula": 2 * lm.n_active * tokens_in,
                        "checker_us": checker_us,
                        "scored": it["scored"],
                    })
                emit_rows(rows)
                mark_done(cell)
                log("cell %s done (%d rows; %.2f h, $%.2f)"
                    % (cell, len(rows), guard.hours(), guard.usd()))
    return rec_path, n_ext_fail, n_gen


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs-dir", default=os.path.join(_HERE, "inputs"))
    ap.add_argument("--items", default=os.path.join(
        _REPO, "data", "ufo-sn3-items-v0", "items.jsonl"))
    ap.add_argument("--fixtures-dir", default=None)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--gpu-class", default="A10G",
                    choices=["T4", "A10G", "A100"])
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--dry-plan", action="store_true")
    ap.add_argument("--arms", default=None)
    ap.add_argument("--hosts", default=None)
    ap.add_argument("--seeds", default=None)
    ap.add_argument("--tokenizer", default=None)
    ap.add_argument("--frozen-record", default=os.path.join(
        _REPO, "registry", "experiments", "ufo-check-0.json"))
    ap.add_argument("--skip-inrun-fixture-check", action="store_true",
                    help="mock-only convenience; REFUSED in real mode")
    args = ap.parse_args()
    if args.fixtures_dir is None:
        args.fixtures_dir = os.path.join(args.inputs_dir, "fixtures")
    t0 = time.time()

    def log(msg):
        print("[ufo0 %7.1fs] %s" % (time.time() - t0, msg), flush=True)

    with open(os.path.join(args.inputs_dir, "manifest.json"),
              encoding="utf-8") as f:
        man = json.load(f)
    verify_pins(man, args)
    tok, tok_path = find_tokenizer(args, man)

    items = load_jsonl(args.items)
    tables = load_jsonl(os.path.join(args.fixtures_dir,
                                     "accept-tables.jsonl"))
    floors = load_jsonl(os.path.join(args.fixtures_dir, "floors.jsonl"))
    gold_rows = load_jsonl(os.path.join(args.fixtures_dir, "gold.jsonl"))
    gold_by_item = {r["item_id"]: r["gold"] for r in gold_rows}
    fmeta = json.load(open(os.path.join(args.fixtures_dir,
                                        "fixtures-meta.json")))
    committed = json.load(open(os.path.join(args.fixtures_dir,
                                            "fixtures-sha.json")))

    if args.dry_plan:
        ok = dry_plan(man, items, tables, tok, args.gpu_class)
        sys.exit(0 if ok else 2)

    # message-discipline re-lint at load (review fix 5, machine-enforced
    # end-to-end): every rejection-message byte, every arm.
    n_msgs = 0
    for row in tables:
        for ans in ANSWERS:
            cell = row["table"][ans]
            if not cell["accept"]:
                n_msgs += 1
                hits = tw.lint_message(cell["message"])
                if hits:
                    raise SystemExit("ERR_MESSAGE_DISCIPLINE: %s/%s/%s: %s"
                                     % (row["item_id"], row["arm"], ans,
                                        hits))
    log("message discipline: %d rejection messages lint-clean" % n_msgs)

    if not args.mock:
        # ERR_RUNNER_ROLE: real mode only on a FROZEN record.
        rec = json.load(open(args.frozen_record))
        if rec.get("id") != "ufo-check-0" or rec.get("status") != "FROZEN":
            raise SystemExit("ERR_RUNNER_ROLE: registry record status %r — "
                             "the runner refuses real mode until the record "
                             "is FROZEN" % rec.get("status"))
        if args.skip_inrun_fixture_check:
            raise SystemExit("ERR_FIXTURES_PRECONDITION: the in-run fixture "
                             "re-check cannot be skipped in real mode")
    if args.skip_inrun_fixture_check:
        sha_run2 = committed["fixtures_sha_run2"]
        log("MOCK: in-run fixture re-check SKIPPED (flagged)")
    else:
        sha_run2 = reverify_fixtures(args, tok_path, committed)
        log("in-run fixture re-check OK: %s" % sha_run2[:16])

    guard = BudgetGuard(man["caps"],
                        man["planning"]["usd_per_hour"][args.gpu_class],
                        on_gpu=(args.device == "cuda"))
    rec_path, n_ext_fail, n_gen = run(args, man, items, gold_by_item,
                                      tables, floors, tok, guard, log)

    hosts = args.hosts.split(",") if args.hosts else list(HOSTS)
    seeds = [int(x) for x in args.seeds.split(",")] if args.seeds \
        else list(SEEDS)
    arms = args.arms.split(",") if args.arms else list(ARMS)
    suffix = "-mock" if args.mock else ""
    sidecar = {
        "fixtures_sha_run1": committed["fixtures_sha_run1"],
        "fixtures_sha_run2": sha_run2,
        "expected": {
            "hosts": hosts, "arms": arms, "seeds": seeds,
            "n_items": fmeta["n_items"], "n_scored": fmeta["n_scored"],
            "all_item_ids_sha256": fmeta["all_item_ids_sha256"],
            "scored_item_ids_sha256": fmeta["scored_item_ids_sha256"],
        },
        "an_representation_match":
            (fmeta["representation_census"]["per_item_equal"]
             and fmeta["representation_census"]["totals_equal"]),
        "representation_census": fmeta["representation_census"],
        "an_nondegenerate": fmeta["an_stats"]["nondegenerate"],
        "an_stats": fmeta["an_stats"],
        "ad_coincidence_ok": fmeta["ad"]["ok"],
        "ad_coincidence_rate": fmeta["ad"]["coincidence_rate"],
        "rejection_message_clean": True,  # re-linted fail-closed above
        "oop_probe_refusal_correctness":
            fmeta["oop"]["refusal_correctness"],
        "extraction_counts": {"n_generations": n_gen,
                              "n_extraction_failures": n_ext_fail},
        "model_revisions": ({"note": "MOCK — stub LM"} if args.mock
                            else {h: man["models"][h] for h in hosts}),
        "gpu_hours": guard.hours() if args.device == "cuda" else 0.0,
        "usd_total": guard.usd(),
        "mode": "MOCK" if args.mock else "FULL",
    }
    with open(os.path.join(args.out_dir, "run-sidecar%s.json" % suffix),
              "w", encoding="utf-8") as f:
        json.dump(sidecar, f, indent=1, sort_keys=True)
        f.write("\n")
    results = {
        "experiment": "ufo-check-0",
        "outcome": ("MOCK-HARNESS-COMPLETE" if args.mock
                    else "HARNESS-COMPLETE"),
        "outcome_note": "NOT a hypothesis verdict — raw run-records only; "
                        "the verdict is computed by the pinned "
                        "analysis/ufo_check_0.py + verdict-gen under "
                        "run-vs-audit separation",
        "mode": sidecar["mode"],
        "records_file": os.path.basename(rec_path),
        "n_generations": n_gen,
        "wall_clock_hours": guard.hours(),
        "pins": man["pins"],
    }
    with open(os.path.join(args.out_dir, "results-ufo0%s.json" % suffix),
              "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, sort_keys=True)
    log("OUTCOME: %s (records %s)" % (results["outcome"], rec_path))


if __name__ == "__main__":
    main()
