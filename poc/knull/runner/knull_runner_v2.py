#!/usr/bin/env python3
"""knull-v2 CAMPAIGN runner — the verdict-bearing run harness for the FROZEN
record registry/experiments/knull-v2.json (frozen 2026-07-13T15:09:36Z,
present in registry/frozen-index.json).

CUSTODY: the v1 draft runner poc/knull/runner/knull_runner.py is pinned in
the frozen record's harness_manifest (sha 81e3684c...) and stays
byte-untouched; this is the anticipated runner-role harness the record
describes verbatim: "the real-mode HF harness is runner-role work that
re-points to the FROZEN knull-v2 + inputs-v4, adds the 6 plain-padded cells
of ASM-1086 (36 GPU cells total) and re-pins at campaign start, the f2b
pattern".

THE ONE DESIGN RULE (content-injection map, knull-v2.json design): arms
differ ONLY in records_root + item file. Enforced structurally by importing
the pinned f2b machinery byte-identical (poc/f2b/runner/f2b_runner.py at the
inputs-v4 manifest pin b62c3a72..., fail-closed KNULL2_ERR_PIN):
KernelVerifier, ShuffledKernelVerifier, run_alone, run_verify_retry,
build_prompt frames, HFLM/StubLM backends and the F0 flop accounting are the
byte-identical objects of the f2b-replicate run.

CELL PLAN — 36 GPU cells, every count cited to knull-v2.json:
  arm x cell grid (design.independent_vars store/cell levels):
    kernel        alone-R1, alone-R3, verify-retry-R1(k=4),
                  shuffled-verify-retry-R1(k=4)      x seeds {0,1,2} = 12
    plain         alone-R1, alone-R3, verify-retry-R1(k=4)  x seeds  =  9
    plain-padded  alone-R1, verify-retry-R1(k=4) ONLY (ASM-1086)     =  6
    opaque        alone-R1, alone-R3, verify-retry-R1(k=4)  x seeds  =  9
  matched-FLOP retry topology: retry_budget levels {0,4} — verify cells run
  the f2b verify->reject->resample loop at k=4; alone cells k=0; the
  shuffled bridge is the identical topology against the seed-pinned
  derangement (sap_prng_seed 20260710), the f2b-replicate control verbatim.

OUTPUT SCHEMA — exactly what the pinned SAP analysis/knull_v3.py (record
pins.analysis_script, sha verified fail-closed here) consumes:
  run-records.jsonl rows: {arm, cell, rung, seed, k, n, acc, cov,
      flops_per_query, extraction_failures*, extraction_calls*,
      perm_sha256*, metric_vector, mock*}   (* where applicable)
  item-meta.json: kernel.types + kernel.prompt_tokens + plain.prompt_tokens
      (+ all arms' uids/tokens) from the PINNED sidecar
      poc/knull/inputs-v4/prompt-tokens.json (KNULL_SAP_ERR_TOKEN_META
      contract), consumed-prefix order.
RAW metrics only — this runner computes NO verdict; the verdict belongs to
the pinned analysis/knull_v3.py + tools/registry/verdict-gen.py under
run-vs-audit separation.

CHECKPOINT/RESUME (per item): every completed item of every cell is appended
+ fsynced to <checkpoint-dir>/ckpt-<cellslug>.jsonl together with the
cumulative F0 meter accumulators; completed cells append their record to
run-records.jsonl immediately (the f2b correction-1 flush lesson). A killed
or preempted run resumes exactly where it stopped: finished cells are
re-emitted from checkpoint without touching a model; a part-done cell
resumes at its first missing item. Determinism note: HFLM attempt-0 is
greedy and attempts>0 draw from torch.Generator(SEED_BASE*10000+seed*100+
attempt) — per-item, no cross-item state — so a resumed cell's cov is
identical to an uninterrupted one; only latency percentiles are
within-session (disclosed via resumed_from_item).

MODES
  --mock       StubLM mechanics on CPU, $0, no torch, labelled MOCK
               end-to-end (NOTE the record's disclosed mock artifact: the
               StubLM chars-proxy makes /gates/flops_parity read FALSE on
               MOCK records — stipulated, carries no information about the
               real gate).
  --dry-plan   $0 cost plan for the 36 cells vs the frozen caps
               (usd_cap 60 / gpu_hours_cap 8 / wall_clock_cap_hours 24).
  --real       the campaign path (HFLM at the record-pinned revisions,
               requires --confirm-spend). Refuses unless the record is
               FROZEN + indexed and EVERY pin verifies.

Usage:
  python3 poc/knull/runner/knull_runner_v2.py --mock --out-dir /tmp/k2 \
      [--items 60] [--arms kernel,plain] [--checkpoint-dir /tmp/k2-ckpt]
  python3 poc/knull/runner/knull_runner_v2.py --dry-plan
  python3 poc/knull/runner/knull_runner_v2.py --real --confirm-spend \
      --device cuda --gpu-class A100 --out-dir <out> --checkpoint-dir <ckpt>
"""

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
POC = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOT = os.path.normpath(os.path.join(POC, ".."))
F2B_RUNNER_DIR = os.path.join(POC, "f2b", "runner")
for p in (POC, F2B_RUNNER_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

# Byte-identical pinned f2b machinery (sha verified fail-closed in verify_pins)
from f2b_runner import (                                    # noqa: E402
    HFLM, CellBudgetExceeded, CellGuard, KernelVerifier,
    ShuffledKernelVerifier, StubLM, run_alone, run_verify_retry, sha256_file)
from f0 import FlopMeter                                    # noqa: E402

# ---------------------------------------------------------------------------
# FROZEN-PROTOCOL CONSTANTS — every value cites registry/experiments/
# knull-v2.json (the FROZEN record). Changing any of these is an off-record
# run: mint a correction first.
# ---------------------------------------------------------------------------
RECORD_ID = "knull-v2"          # knull-v2.json id
ARMS = ("kernel", "plain", "plain-padded", "opaque")
                                # design.independent_vars store levels
R3_ARMS = ("kernel", "plain", "opaque")
                                # ASM-1086: plain-padded runs alone-R1 +
                                # verify-retry-R1 ONLY (design + SAP scope)
SEEDS = (0, 1, 2)               # design.seeds
K_RETRY = 4                     # design.independent_vars retry_budget {0,4}
N_ITEMS = 1000                  # design.n_planned.per_arm_items (rank-prefix)
PERM_SEED = 20260710            # design.sap_prng_seed; the seed-pinned
                                # derangement of the shuffled bridge (f2b
                                # mechanism verbatim; v1 runner pinned in
                                # pins.harness_manifest uses this value)
# pins.harness_manifest: "knull-v2 inputs manifest poc/knull/inputs-v4/
# manifest.json sha256 ae52862d...". The runtime typo-guard in verify_pins()
# asserts BOTH literals below appear verbatim in the frozen record's
# pins.harness_manifest, so a transcription error here fails closed.
MANIFEST_SHA = ("ae52862d9f95c83238230ed555628318"
                "140f69f9c456eb95fc82b25fcac2ebfe")
# pins.harness_manifest: "per-item prompt-token sidecar poc/knull/inputs-v4/
# prompt-tokens.json sha256 d9312f19..." (the knull_v3 item_meta MEASURED
# source, KNULL_SAP_ERR_TOKEN_META contract):
PROMPT_TOKENS_SHA = ("d9312f19a3a7338dbee1f5f711380354"
                     "4e38218c30524f9d226b05edf09aa179")

CAPS = {"usd_cap": 60, "gpu_hours_cap": 8, "wall_clock_cap_hours": 24}
                                # budget block (Tier-1 tier_cap_usd 60 too)
GPU_HARDWARE = "A100"           # runner_constraints.hardware: 1x A100-40GB
CELL_ALONE = "model-alone"      # SAP cell names (analysis/knull_v3.py)
CELL_VERIFY = "verify-retry"
CELL_SHUF = "shuffled-verify-retry"

GUARD_MAX_GEN = 16              # f2b MAX_GEN_PER_ITEM_DEFAULT (structural
                                # max here is k+1=5; 16 trips only a defect)
CELL_TIMEOUT_S = 7200.0         # 2x the f2b A100 default: n=1000 vs 250


def die(code, msg):
    sys.stderr.write("%s: %s\n" % (code, msg))
    sys.exit(1)


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# ---------------------------------------------------------------------------
# Fail-closed pin verification (the frozen-record + store-sha checks)
# ---------------------------------------------------------------------------
def load_frozen_record():
    rec_path = os.path.join(ROOT, "registry", "experiments", "knull-v2.json")
    if not os.path.isfile(rec_path):
        die("KNULL2_ERR_RECORD", "missing %s" % rec_path)
    rec = json.load(open(rec_path, encoding="utf-8"))
    if rec.get("id") != RECORD_ID:
        die("KNULL2_ERR_RECORD", "record id %r != %r" % (rec.get("id"), RECORD_ID))
    if rec.get("status") != "FROZEN":
        die("KNULL2_ERR_NOT_FROZEN",
            "knull-v2 status %r — this harness runs ONLY against the frozen "
            "record" % rec.get("status"))
    idx_path = os.path.join(ROOT, "registry", "frozen-index.json")
    if not (os.path.isfile(idx_path)
            and RECORD_ID in json.load(open(idx_path, encoding="utf-8"))):
        die("KNULL2_ERR_NOT_FROZEN",
            "knull-v2 missing from registry/frozen-index.json")
    return rec


def verify_pins(rec, log):
    """Every pin the campaign consumes, verified fail-closed BEFORE any model
    is touched. Returns the verified inputs-v4 manifest."""
    hm = rec["pins"]["harness_manifest"]
    # constants self-check: the literals above must appear verbatim in the
    # frozen record text (a typo in this file fails closed, never passes)
    for name, lit in (("MANIFEST_SHA", MANIFEST_SHA),
                      ("PROMPT_TOKENS_SHA", PROMPT_TOKENS_SHA)):
        if len(lit) != 64 or lit not in hm:
            die("KNULL2_ERR_CONST",
                "%s literal not found in pins.harness_manifest (typo guard)"
                % name)
    inputs = os.path.join(POC, "knull", "inputs-v4")
    man_path = os.path.join(inputs, "manifest.json")
    if sha256_file(man_path) != MANIFEST_SHA:
        die("KNULL2_ERR_PIN", "inputs-v4/manifest.json sha != the frozen "
            "harness_manifest pin %s" % MANIFEST_SHA[:12])
    man = json.load(open(man_path, encoding="utf-8"))
    if man.get("plain_store_placeholder", True):
        die("KNULL2_ERR_PLACEHOLDER", "plain store flagged placeholder")
    # SAP pin — the exact analysis this run's records must feed
    sap = rec["pins"]["analysis_script"]
    sap_path = os.path.join(ROOT, sap["path"])
    if sha256_file(sap_path) != sap["sha256"]:
        die("KNULL2_ERR_PIN", "%s sha != record pins.analysis_script"
            % sap["path"])
    # imported machinery pin (inputs-v4 manifest provenance)
    got = sha256_file(os.path.join(F2B_RUNNER_DIR, "f2b_runner.py"))
    want = man["provenance_pins"]["f2b_runner_py_sha256"]
    if got != want:
        die("KNULL2_ERR_PIN", "f2b_runner.py sha %s != inputs-v4 pin %s"
            % (got[:12], want[:12]))
    # item-file pins (all four arms)
    for a in ARMS:
        p = os.path.join(inputs, "items", "%s.jsonl" % a)
        if sha256_file(p) != man["pins"]["items_%s_sha256" % a]:
            die("KNULL2_ERR_PIN", "items/%s.jsonl sha != manifest pin" % a)
    # store-sha checks: every pinned store file byte-verified (kernel arm
    # records are additionally sha-pinned per item and re-verified at load
    # by KernelVerifier — the f2b ERR_RECORD_PIN path)
    for a in ("plain", "plain-padded", "opaque"):
        pins = man["pins"]["store_%s" % a]
        root = os.path.join(inputs, "stores", a)
        for fname, sha in sorted(pins.items()):
            fp = os.path.join(root, fname)
            if not os.path.isfile(fp) or sha256_file(fp) != sha:
                die("KNULL2_ERR_PIN", "store %s/%s sha != manifest pin"
                    % (a, fname))
        extra = set(os.listdir(root)) - set(pins)
        if extra:
            die("KNULL2_ERR_PIN", "unpinned files in store %s: %s"
                % (a, sorted(extra)[:5]))
    # prompt-token sidecar (the SAP item_meta MEASURED source)
    pt_path = os.path.join(inputs, "prompt-tokens.json")
    if sha256_file(pt_path) != PROMPT_TOKENS_SHA:
        die("KNULL2_ERR_PIN", "prompt-tokens.json sha != the frozen sidecar pin")
    log("pins OK: record FROZEN+indexed; SAP %s; f2b machinery %s; 4 item "
        "files; 3x%d store files; prompt-token sidecar"
        % (sap["sha256"][:12], want[:12], len(man["pins"]["store_plain"])))
    return man


def model_specs(rec):
    """rec pins.model_revisions 'repo@revision' -> {rung: (repo, revision)};
    cross-checked against the f2b manifest models block (same pins)."""
    mr = rec["pins"]["model_revisions"]
    out = {}
    for rung, key in (("R1", "SmolLM2-135M"), ("R3", "SmolLM2-1.7B")):
        repo, _, revision = mr[key].partition("@")
        if not repo or not revision:
            die("KNULL2_ERR_PIN", "unparseable model pin %r" % mr[key])
        out[rung] = (repo, revision)
    return out


# ---------------------------------------------------------------------------
# Items + pairing (fail-closed, identical to the pinned v1 runner semantics)
# ---------------------------------------------------------------------------
def load_items(n, log):
    inputs = os.path.join(POC, "knull", "inputs-v4")
    items = {}
    for a in ARMS:
        vec = load_jsonl(os.path.join(inputs, "items", "%s.jsonl" % a))
        vec.sort(key=lambda x: x["rank"])
        if len(vec) < n:
            die("KNULL2_ERR_ITEMS", "arm %s: %d items < requested %d"
                % (a, len(vec), n))
        items[a] = vec[:n]
    uids = [it["skeleton_uid"] for it in items["kernel"]]
    types = [it["type"] for it in items["kernel"]]
    for a in ARMS:
        if [it["skeleton_uid"] for it in items[a]] != uids:
            die("KNULL2_ERR_PAIRING", "skeleton prefix differs for arm %s" % a)
        if [it["type"] for it in items[a]] != types:
            die("KNULL2_ERR_TYPEMIX",
                "type mix differs for arm %s (record: REQUIRED IDENTICAL "
                "ACROSS ALL FOUR ARMS, enforced fail-closed)" % a)
    log("items OK: %d paired skeletons x 4 arms (rank-prefix; uid + type-mix "
        "identity enforced)" % n)
    return items


def arm_roots():
    inputs = os.path.join(POC, "knull", "inputs-v4")
    return {"kernel": ROOT,        # the pinned NSM records (manifest kernel_store)
            "plain": os.path.join(inputs, "stores", "plain"),
            "plain-padded": os.path.join(inputs, "stores", "plain-padded"),
            "opaque": os.path.join(inputs, "stores", "opaque")}


def build_item_meta(items, n):
    """The analysis/knull_v3.py item_meta contract: kernel.types +
    kernel.prompt_tokens + plain.prompt_tokens (KNULL_SAP_ERR_TOKEN_META),
    sourced from the PINNED sidecar in consumed rank-prefix order."""
    pt = json.load(open(os.path.join(POC, "knull", "inputs-v4",
                                     "prompt-tokens.json"), encoding="utf-8"))
    meta = {"_source": {"prompt_tokens": "poc/knull/inputs-v4/prompt-tokens.json "
                        "(pinned %s...)" % PROMPT_TOKENS_SHA[:12],
                        "order": "item-file rank-sorted, consumed prefix"}}
    for a in ARMS:
        arr = pt["arms"][a]
        if len(arr) < n:
            die("KNULL2_ERR_TOKEN_META", "sidecar arm %s shorter than n" % a)
        meta[a] = {"skeleton_uids": [it["skeleton_uid"] for it in items[a]],
                   "prompt_tokens": arr[:n]}
    meta["kernel"]["types"] = [it["type"] for it in items["kernel"]]
    return meta


# ---------------------------------------------------------------------------
# Cell plan — the 36 GPU cells (or a --arms slice for the account fan)
# ---------------------------------------------------------------------------
def cell_plan(arms):
    plan = []
    for a in arms:
        plan += [(a, CELL_ALONE, "R1", s) for s in SEEDS]
        if a in R3_ARMS:
            plan += [(a, CELL_ALONE, "R3", s) for s in SEEDS]
        plan += [(a, CELL_VERIFY, "R1", s) for s in SEEDS]
        if a == "kernel":
            plan += [(a, CELL_SHUF, "R1", s) for s in SEEDS]
    return plan


def cell_slug(arm, cell, rung, seed):
    return "%s__%s__%s__s%d" % (arm.replace("-", "_"), cell, rung, seed)


# ---------------------------------------------------------------------------
# Per-item checkpoint (append + fsync each item; meter accumulators carried)
# ---------------------------------------------------------------------------
class CellCheckpoint:
    METER_KEYS = ("model_flops", "verifier_cpu_s", "t_prefill", "t_decode",
                  "wall_s", "n_queries")

    def __init__(self, ckpt_dir, slug, n_expected):
        self.path = os.path.join(ckpt_dir, "ckpt-%s.jsonl" % slug) \
            if ckpt_dir else None
        self.rows = []
        if self.path and os.path.isfile(self.path):
            self.rows = load_jsonl(self.path)
            for i, r in enumerate(self.rows):
                if r["i"] != i:
                    die("KNULL2_ERR_CKPT", "%s: row %d has i=%s (corrupt "
                        "checkpoint — delete it to recompute the cell)"
                        % (self.path, i, r["i"]))
            if len(self.rows) > n_expected:
                die("KNULL2_ERR_CKPT", "%s: %d rows > n=%d (stale checkpoint "
                    "from a different item count — use a fresh --checkpoint-dir)"
                    % (self.path, len(self.rows), n_expected))
        self._fh = None

    @property
    def n_done(self):
        return len(self.rows)

    def cov_xf(self):
        return ([r["c"] for r in self.rows],
                sum(r.get("xf", 0) for r in self.rows))

    def restore_meter(self, meter):
        if self.rows:
            m = self.rows[-1]["m"]
            for k in self.METER_KEYS:
                setattr(meter, k, m[k])

    def append(self, i, c, xf, meter):
        row = {"i": i, "c": c,
               "m": {k: getattr(meter, k) for k in self.METER_KEYS}}
        if xf:
            row["xf"] = xf
        self.rows.append(row)
        if not self.path:
            return
        if self._fh is None:
            self._fh = open(self.path, "a", encoding="utf-8")
        self._fh.write(json.dumps(row, sort_keys=True) + "\n")
        self._fh.flush()
        os.fsync(self._fh.fileno())

    def close(self):
        if self._fh:
            self._fh.close()
            self._fh = None


class Emitter:
    """run-records.jsonl append+fsync at cell completion (f2b correction-1:
    a stopped run leaves every completed cell on disk)."""

    def __init__(self, out_dir):
        self.path = os.path.join(out_dir, "run-records.jsonl")
        self.records = []
        # do NOT truncate: a resumed run re-emits from checkpoint into a
        # fresh file only when starting clean
        if os.path.isfile(self.path):
            self.records = load_jsonl(self.path)
        else:
            with open(self.path, "w"):
                pass

    def have(self, arm, cell, rung, seed):
        return any(r["arm"] == arm and r["cell"] == cell
                   and r["rung"] == rung and r["seed"] == seed
                   for r in self.records)

    def emit(self, body):
        self.records.append(body)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(body, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())


def fpq(meter):
    """Per-query FLOPs: model + pinned-rate verifier CPU (F0 section 3.3) —
    the /gates/flops_ratio_* input of analysis/knull_v3.py."""
    n = max(1, meter.n_queries)
    return (meter.model_flops + meter.verifier_cpu_s * meter.cpu_rate) / n


# ---------------------------------------------------------------------------
# Cell execution: pinned f2b arm functions called per item (singleton lists)
# so every item is a checkpoint unit. run_alone/run_verify_retry hold no
# cross-item state, so the per-item calling is outcome-identical to the
# whole-list calling of the pinned v1 runner.
# ---------------------------------------------------------------------------
def run_cell(lm, frames, items, seed, meter, guard, ckpt, verifier=None, k=0):
    cov, xf = ckpt.cov_xf()
    ckpt.restore_meter(meter)
    for i in range(ckpt.n_done, len(items)):
        it = items[i]
        if verifier is None:
            c = run_alone(lm, frames, [it], seed, meter, guard)[0]
            x = 0
        else:
            cvec, x = run_verify_retry(lm, frames, [it], verifier, k, seed,
                                       meter, guard)
            c = cvec[0]
        cov.append(c)
        xf += x
        ckpt.append(i, c, x, meter)
    ckpt.close()
    return cov, xf


# ---------------------------------------------------------------------------
# --dry-plan: $0 estimate of the 36 cells vs the frozen caps
# ---------------------------------------------------------------------------
def dry_plan(rec, man, f2b_man, items, arms, log):
    pt = json.load(open(os.path.join(POC, "knull", "inputs-v4",
                                     "prompt-tokens.json"), encoding="utf-8"))
    n = len(items["kernel"])
    plan = f2b_man["planning"]
    tput = plan["throughput_tok_per_s"][GPU_HARDWARE]
    usd_h = f2b_man["flop_accounting"]["usd_per_hour"][GPU_HARDWARE]

    def cell_tokens(arm, k):
        """Worst-case scored tokens for one cell: per item, (k+1) attempts x
        n_options forced-choice scorings of the measured prompt length
        (pinned-tokenizer sidecar) + option tokens (~2/key)."""
        tot = 0.0
        for i, it in enumerate(items[arm]):
            keys = len(it["options"]) if it.get("options") else 2
            tot += (k + 1) * keys * (pt["arms"][arm][i] + 2)
        return tot

    cells = cell_plan(arms)
    hours = {"R1": 0.0, "R3": 0.0}
    per_arm_h = {}
    for (a, cell, rung, _s) in cells:
        k = K_RETRY if cell in (CELL_VERIFY, CELL_SHUF) else 0
        h = cell_tokens(a, k) / tput[rung] / 3600.0
        hours[rung] += h
        per_arm_h[a] = per_arm_h.get(a, 0.0) + h
    est = sum(hours.values())
    worst = est * plan["overhead_factor"]
    print("knull-v2 --dry-plan (ESTIMATES ONLY; $0; nothing launched)")
    print("  record: registry/experiments/knull-v2.json (FROZEN %s)"
          % rec["frozen_at"])
    print("  cells: %d over arms %s (full campaign = 36; n=%d, seeds %s, k=%d)"
          % (len(cells), ",".join(arms), n, list(SEEDS), K_RETRY))
    for a in arms:
        print("    arm %-13s %5.2f worst-case GPU-h (x%.1f overhead: %.2f)"
              % (a, per_arm_h[a], plan["overhead_factor"],
                 per_arm_h[a] * plan["overhead_factor"]))
    print("  GPU-h on %s (pinned planning tput %s): R1 %.2f + R3 %.2f = %.2f"
          % (GPU_HARDWARE, tput, hours["R1"], hours["R3"], est))
    print("  with %.1fx overhead: %.2f h -> $%.2f at pinned $%.2f/h"
          % (plan["overhead_factor"], worst, worst * usd_h, usd_h))
    print("  record planning estimate: 4-6 GPU-h / $15-30 (36 cells)")
    checks = [
        ("worst-case USD vs usd_cap ($%d)" % CAPS["usd_cap"],
         worst * usd_h <= CAPS["usd_cap"]),
        ("worst-case GPU-h vs gpu_hours_cap (%d h)" % CAPS["gpu_hours_cap"],
         worst <= CAPS["gpu_hours_cap"]),
        ("hard ceiling %dh x $%.2f vs usd_cap"
         % (CAPS["gpu_hours_cap"], usd_h),
         CAPS["gpu_hours_cap"] * usd_h <= CAPS["usd_cap"]),
    ]
    ok_all = True
    for name, ok in checks:
        ok_all &= ok
        print("  %-52s %s" % (name, "OK" if ok else "OVER — DO NOT LAUNCH"))
    log("dry-plan %s" % ("OK" if ok_all else "OVER CAPS"))
    return ok_all


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--real", action="store_true")
    ap.add_argument("--dry-plan", action="store_true")
    ap.add_argument("--confirm-spend", action="store_true",
                    help="required with --real (coordinator-only GPU spend)")
    ap.add_argument("--arms", default=",".join(ARMS),
                    help="comma subset for the Modal account fan "
                         "(default: all four)")
    ap.add_argument("--items", type=int, default=None,
                    help="mock-only override (real mode is frozen at %d)"
                         % N_ITEMS)
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--checkpoint-dir", default=None,
                    help="per-item checkpoint/resume directory (STRONGLY "
                         "recommended for real runs)")
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--gpu-class", default=GPU_HARDWARE,
                    choices=["T4", "A10G", "A100"],
                    help="F0 usd table key (record hardware: 1x A100-40GB)")
    ap.add_argument("--max-hours", type=float,
                    default=float(CAPS["gpu_hours_cap"]),
                    help="abort (checkpointed) between cells past this")
    ap.add_argument("--cell-timeout-s", type=float, default=CELL_TIMEOUT_S)
    ap.add_argument("--max-gen-per-item", type=int, default=GUARD_MAX_GEN)
    args = ap.parse_args()

    t0 = time.time()

    def log(msg):
        print("[knull2 %7.1fs] %s" % (time.time() - t0, msg), flush=True)

    modes = sum(1 for m in (args.mock, args.real, args.dry_plan) if m)
    if modes != 1:
        die("KNULL2_ERR_ARGS", "pick exactly one of --mock / --real / --dry-plan")
    arms = tuple(a.strip() for a in args.arms.split(",") if a.strip())
    bad = [a for a in arms if a not in ARMS]
    if bad or not arms:
        die("KNULL2_ERR_ARGS", "unknown arms %s (valid: %s)" % (bad, ARMS))

    rec = load_frozen_record()
    man = verify_pins(rec, log)
    f2b_man = json.load(open(os.path.join(POC, "f2b", "inputs",
                                          "f2b-manifest.json"),
                             encoding="utf-8"))

    if args.real:
        if not args.confirm_spend:
            die("KNULL2_ERR_SPEND",
                "--real without --confirm-spend refused: GPU spend is "
                "coordinator/runner-role work against the frozen record "
                "(caps: usd %d / gpu-h %d / wall %d h)"
                % (CAPS["usd_cap"], CAPS["gpu_hours_cap"],
                   CAPS["wall_clock_cap_hours"]))
        if args.items not in (None, N_ITEMS):
            die("KNULL2_ERR_ARGS", "real mode is frozen at n=%d "
                "(design.n_planned.per_arm_items)" % N_ITEMS)
        n = N_ITEMS
    else:
        n = args.items if args.items is not None else (60 if args.mock else N_ITEMS)

    items = load_items(n, log)

    if args.dry_plan:
        ok = dry_plan(rec, man, f2b_man, items, arms, log)
        sys.exit(0 if ok else 2)

    if not args.out_dir:
        die("KNULL2_ERR_ARGS", "--out-dir required")
    os.makedirs(args.out_dir, exist_ok=True)
    if args.checkpoint_dir:
        os.makedirs(args.checkpoint_dir, exist_ok=True)

    mock = args.mock
    frames = f2b_man["prompt_frames"]           # VERBATIM f2b frames
    fc = f2b_man["flop_accounting"]
    roots = arm_roots()

    # verifiers (fail-closed store load; per-item record sha re-verified)
    verifiers = {}
    for a in arms:
        v = KernelVerifier(roots[a])
        v.index_labels(items[a])
        verifiers[a] = v
    shuf = None
    if "kernel" in arms:
        shuf = ShuffledKernelVerifier(roots["kernel"], items["kernel"],
                                      PERM_SEED)
        shuf.index_labels(items["kernel"])
        with open(os.path.join(args.out_dir, "shuffle-map.json"), "w") as f:
            json.dump({"perm_seed": PERM_SEED,
                       "algorithm": "Sattolo cyclic derangement "
                                    "(f2b machinery verbatim)",
                       "n_concepts": len(shuf.perm),
                       "map_urn_to_record_of": shuf.perm,
                       "sha256_of_map": shuf.perm_sha256}, f,
                      indent=1, sort_keys=True)
            f.write("\n")
        log("shuffled bridge: seed=%d perm sha=%s"
            % (PERM_SEED, shuf.perm_sha256[:12]))

    # store bytes per arm (unique record files) for the F0 ledger
    store_bytes = {}
    for a in arms:
        store_bytes[a] = sum(
            os.path.getsize(os.path.join(roots[a], p))
            for p in sorted({it["record_path"] for it in items[a]}))

    # LM backends
    lms = {}

    def lm_for(rung):
        if rung not in lms:
            if mock:
                lms[rung] = StubLM(rung, f2b_man["mock"])
            else:
                repo, revision = model_specs(rec)[rung]
                log("loading %s@%s on %s ..." % (repo, revision[:12],
                                                 args.device))
                lms[rung] = HFLM(repo, revision, args.device)
        return lms[rung]

    emit = Emitter(args.out_dir)
    if emit.records:
        log("resume: %d completed cell records already on disk"
            % len(emit.records))

    plan = cell_plan(arms)
    log("mode=%s device=%s arms=%s n=%d cells=%d (full campaign 36)"
        % ("MOCK" if mock else "REAL", args.device, ",".join(arms), n,
           len(plan)))

    for (a, cell, rung, seed) in plan:
        if emit.have(a, cell, rung, seed):
            continue
        if (time.time() - t0) / 3600.0 > args.max_hours:
            die("KNULL2_ERR_TIME_BUDGET",
                "past --max-hours %.1f between cells; checkpoints + %d "
                "completed cell records preserved — relaunch to resume"
                % (args.max_hours, len(emit.records)))
        k = K_RETRY if cell in (CELL_VERIFY, CELL_SHUF) else 0
        ver = (shuf if cell == CELL_SHUF
               else verifiers[a] if cell == CELL_VERIFY else None)
        lm = lm_for(rung)
        slug = cell_slug(a, cell, rung, seed)
        ckpt = CellCheckpoint(args.checkpoint_dir, slug, n)
        resumed_from = ckpt.n_done
        guard = CellGuard(slug, args.cell_timeout_s, args.max_gen_per_item)
        meter = FlopMeter(fc, args.gpu_class)
        try:
            cov, xf = run_cell(lm, frames, items[a], seed, meter, guard,
                               ckpt, verifier=ver, k=k)
        except CellBudgetExceeded as e:
            # incident sidecar, NOT a run-record: the SAP consumes complete
            # cells only; the checkpoint holds this cell's completed items
            with open(os.path.join(args.out_dir, "incidents.jsonl"), "a") as f:
                f.write(json.dumps({
                    "cell": slug, "kind": e.kind, "item_id": e.item_id,
                    "elapsed_s": round(e.elapsed_s, 1),
                    "n_gen_on_item_at_breach": e.n_gen}) + "\n")
            die("KNULL2_ERR_CELL_TIMEOUT",
                "%s — aborted in bounded time; per-item checkpoint preserved; "
                "relaunch resumes at the first missing item" % e)
        body = {"arm": a, "cell": cell, "rung": rung, "seed": seed, "k": k,
                "n": len(cov), "acc": sum(cov) / len(cov), "cov": cov,
                "flops_per_query": fpq(meter),
                "metric_vector": meter.ledger(
                    [lm], store_bytes[a] if ver is not None else 0)}
        if ver is not None:
            body["extraction_failures"] = xf
            body["extraction_calls"] = len(cov)
        if cell == CELL_SHUF:
            body["perm_sha256"] = shuf.perm_sha256
            body["perm_seed"] = PERM_SEED
        if resumed_from:
            body["resumed_from_item"] = resumed_from
        if mock:
            body["mock"] = True
        emit.emit(body)
        log("cell %s done (%.1fs, acc=%.3f%s)"
            % (slug, guard.elapsed(), body["acc"],
               ", resumed@%d" % resumed_from if resumed_from else ""))

    # item-meta (the SAP contract) — full four-arm meta regardless of slice,
    # so any slice's copy is canonical and the merge can assert identity
    all_items = load_items(n, lambda m: None)
    meta = build_item_meta(all_items, n)
    with open(os.path.join(args.out_dir, "item-meta.json"), "w") as f:
        json.dump(meta, f, sort_keys=True)
        f.write("\n")

    hours = (time.time() - t0) / 3600.0
    results = {
        "experiment": RECORD_ID,
        "outcome": ("MOCK-HARNESS-COMPLETE" if mock else "HARNESS-COMPLETE"),
        "outcome_note": "RAW run-records only — NOT a verdict; the verdict is "
                        "computed by the pinned analysis/knull_v3.py + "
                        "tools/registry/verdict-gen.py (run != audit)",
        "mode": "MOCK" if mock else "REAL",
        "arms": list(arms),
        "n_items": n,
        "seeds": list(SEEDS),
        "k_retry": K_RETRY,
        "n_records": len(emit.records),
        "records_file": "run-records.jsonl",
        "item_meta_file": "item-meta.json",
        "device": args.device,
        "gpu_class_assumed_for_usd": args.gpu_class,
        "models": ({"note": "MOCK — StubLM, no models loaded"} if mock else
                   {r: "%s@%s" % model_specs(rec)[r] for r in ("R1", "R3")}),
        "frozen_record": "registry/experiments/knull-v2.json",
        "wallClockHours": hours,
    }
    with open(os.path.join(args.out_dir,
                           "results-knull2%s.json" % ("-mock" if mock else "")),
              "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)
        f.write("\n")
    log("OUTCOME: %s (%d cell records in %s)"
        % (results["outcome"], len(emit.records), emit.path))
    print("next: python3 analysis/knull_v3.py --records %s --item-meta %s "
          "--out <analysis.json>"
          % (emit.path, os.path.join(args.out_dir, "item-meta.json")))


if __name__ == "__main__":
    main()
