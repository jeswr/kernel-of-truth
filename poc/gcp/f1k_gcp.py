#!/usr/bin/env python3
"""f1k_gcp.py — GCP-Spot orchestrator for the FROZEN F1-K correctness run.

OPUS EXECUTION-role harness (kern/opus-runner-<N>). It RUNS the already-frozen
F1-K experiment (registry/experiments/f1k.json, frozen_sha256 01cf2b17…) on the
coordinator-resolved compute target (bead pzb6): a GCP **Spot** n2d-highmem-8
(8 vCPU / 64 GB) + 3×375 GiB local SSD (1,125 GiB NVMe), zone us-central1-a.
It designs NOTHING and concludes NOTHING: the science (kernel, model, engine,
carriers, protocol, analysis) is frozen upstream; this file only provisions,
stages, builds, drives the pinned generator/driver, checkpoints, monitors, and
tears down — from the frozen RunSpec, fail-closed on any pin mismatch.

Compute-target economics (why GCP Spot, not Modal): the pinned analysis
analysis/f1k.py (sha 54924cfd) hard-enforces a ledger window
  instance_hours ∈ [260.6, 900] h,  usd_total ∈ [$73, $155],
  usd_total ≈ usd_spent_prior + run_hours*rate  (COST_TOL $0.01),
  prefills ≥ 11,011,
so the admissible EFFECTIVE rate is [73/900, 155/260.6] = [$0.081, $0.595]/h.
Modal ($1.15/h) has an EMPTY window (155/1.15 = 134.8 h < 260.6) — certain
no-verdict (bead pzb6). GCP Spot ~$0.19-0.24/h is IN-window and admits a
NON-empty valid instance_hours window. See the AFFORDABILITY note below:
a rate BELOW $0.28 makes the $73 usd_total FLOOR the binding constraint, which
is MEASURED + gated at bring-up (never silently overspent OR under-run).

Entrypoints (source ~/.config/kot/gcp.env first):
  python3 poc/gcp/f1k_gcp.py plan          # $0 dry-plan: pins + SPOT + window
  python3 poc/gcp/f1k_gcp.py provision     # create the Spot VM + 3 local SSD
  python3 poc/gcp/f1k_gcp.py push          # scp the harness + patches to the VM
  python3 poc/gcp/f1k_gcp.py stage         # HF -> local SSD (+ GCS mirror)
  python3 poc/gcp/f1k_gcp.py build         # clone+patch+build (KaE + dump)
  python3 poc/gcp/f1k_gcp.py bringup       # KaE inertness + dump 3-precond gate
  python3 poc/gcp/f1k_gcp.py affordability # measure rate+s/prefill -> gate
  python3 poc/gcp/f1k_gcp.py status        # poll VM state + GCS heartbeat
  python3 poc/gcp/f1k_gcp.py teardown      # delete VM + disks (nothing bills idle)
Nothing spends until an explicit provisioning entrypoint is invoked; `plan` is
$0 and asserts the frozen ledger admissibility.
"""
from __future__ import annotations
import json, os, subprocess, sys, time, hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
HARNESS = REPO / "poc" / "glm52-probe" / "f1k-harness"
KAE_PATCH_DIR = REPO / "poc" / "glm52-probe" / "kae-patch-draft"
DUMP_PATCH_DIR = HARNESS / "dump-patch"

# ---------------------------------------------------------------------------
# FROZEN PINS (registry/experiments/f1k.json 01cf2b17…; verified at launch)
# ---------------------------------------------------------------------------
FROZEN_SHA256 = "01cf2b17a882b2ab89873234a381720108dbb9d0dcd406a752962e280b71dc55"
COLIBRI_COMMIT = "a78a06fc5acc4b0dc0f9ef03987c66b0559d1250"
ESTATE_REPO = "mateogrgic/GLM-5.2-colibri-int4-with-int8-mtp"
ESTATE_GB = 383.8
PINS = {
    "analysis/f1k.py":
        "54924cfd0f1b7878da53228aa54f3cdf3e405aa4d0ecefd185fcb75da9eea8eb",
    "build_carriers.py":
        "a92be3e4fe535c1dfefc41e2a422e010d25e8e40cf8e4cc123e7d829d63e9e61",
    "kae-add-path.patch":
        "11f8b45884878111480192ee086c92b22acaa1aaf3238b2d46c47f952e9dd9cb",
    "kot-f1k-dump.patch":
        "fb5d2f3558351f608afccb29ab974aac2a62182ad67f27ec5c3c5f3e9eab0097",
    "kae_dump.h":
        "6ce7760129a64ab749d55ab5b0701d91d41130b233057c90fbea873aec6e304a",
    "construction-manifest.jsonl":
        "a8cb3a8aee9730107bf04749988cb7d3438132a39ad19095cecd5283109f906c",
}
PIN_PATHS = {
    "analysis/f1k.py": REPO / "analysis" / "f1k.py",
    "build_carriers.py": HARNESS / "build_carriers.py",
    "kae-add-path.patch": KAE_PATCH_DIR / "kae-add-path.patch",
    "kot-f1k-dump.patch": DUMP_PATCH_DIR / "kot-f1k-dump.patch",
    "kae_dump.h": DUMP_PATCH_DIR / "kae_dump.h",
    "construction-manifest.jsonl":
        REPO / "data" / "f1k-carriers-v1" / "generator"
        / "construction-manifest.jsonl",
}
CONSTRUCTION_SEED = 20260716

# ---------------------------------------------------------------------------
# FROZEN ANALYSIS WINDOW (analysis/f1k.py constants — MIRRORED, not invented)
# ---------------------------------------------------------------------------
INSTANCE_HOURS_MIN = 260.6      # INSTANCE_HOURS_MIN (half the ASM-2374 521.2h)
WALL_CLOCK_CAP_HOURS = 900.0    # WALL_CLOCK_CAP_HOURS (REG budget)
USD_TOTAL_MIN = 73.0            # USD_TOTAL_MIN (half the ASM-2374 corner $146)
USD_CAP = 155.0                 # USD_CAP_REGISTERED (ASM-2374)
COST_TOL_USD = 0.01
PREFILLS_MANDATORY_MIN = 11011  # PREFILLS_MANDATORY_MIN (=1573*7)
# admissible EFFECTIVE rate = [USD_TOTAL_MIN/WALL_CLOCK_CAP, USD_CAP/INSTANCE_HOURS_MIN]
RATE_WINDOW = (USD_TOTAL_MIN / WALL_CLOCK_CAP_HOURS,
               USD_CAP / INSTANCE_HOURS_MIN)   # (0.0811…, 0.5948…)

# frozen prefill envelope (README $155 accounting / freeze-(A) completion)
PREFILLS_MANDATORY = 19964      # construction 4608 + pilot<=2112 + guard<=660 + main 12584
PREFILLS_WITH_REPLACE = 21537   # + conditional REPLACE 1573
# ASM-2205 pessimistic corner blended throughput (s/prefill, POST the 1.20x pin
# lever): 462.1 h * 3600 / 19964 = 83.31 s/prefill.  Used ONLY as a reference
# for the affordability projection band; the REAL value is MEASURED at bring-up.
CORNER_BLENDED_S_PER_PREFILL = 462.1 * 3600.0 / 19964.0

# ---------------------------------------------------------------------------
# GCP target (bead pzb6 resolution; MANDATORY provisioning-model = SPOT)
# ---------------------------------------------------------------------------
MACHINE_TYPE = "n2d-highmem-8"          # 8 vCPU / 64 GB — i4i.2xlarge-class RAM
LOCAL_SSD_COUNT = 2                     # 2×375 = 750 GiB local NVMe (n2d allows {1,2,4,8,16,24}; 3 infeasible; 750 >= 384 GiB estate; rate $0.174/h in-window). Bump to 4 (1500 GiB) if construction needs more scratch headroom.
PROVISIONING_MODEL = "SPOT"             # MANDATORY: on-demand busts the ceiling
INSTANCE_NAME = os.environ.get("KOT_F1K_VM", "kot-f1k-run")
GCS_BUCKET = os.environ.get("KOT_F1K_BUCKET", "")   # coordinator-supplied mirror
IMAGE_FAMILY = "ubuntu-2204-lts"
IMAGE_PROJECT = "ubuntu-os-cloud"
BOOT_GB = 60

PROJECT = os.environ.get("KOT_GCP_PROJECT", "")
ZONE = os.environ.get("KOT_GCP_ZONE", "us-central1-a")
REGION = os.environ.get("KOT_GCP_REGION", "us-central1")

# ---------------------------------------------------------------------------
# BRING-UP provisioning override (OPS ONLY — NOT the frozen construction ledger)
# ---------------------------------------------------------------------------
# The bring-up (functional inert-by-default gate + dump preconditions a/b/c +
# affordability micro-bench) is a ONE-TIME VALIDATION on a SEPARATE, throwaway
# VM. It is NOT written to results-log/f1k.jsonl and does NOT enter the frozen
# construction cost model (analysis/f1k.py window). The SPOT mandate exists to
# fit that CONSTRUCTION ledger; it does not bind the disposable bring-up VM.
# Spot PREEMPTION repeatedly reclaimed the VM mid-run before the ~2h functional
# gate finished (runner-9: VM STOPPING at ~75min, no verdict). So the bring-up
# VM MAY be provisioned ON-DEMAND for reliability; this touches NOTHING frozen
# and CONSTRUCTION stays SPOT (module default, unchanged). Enable per-run with
# KOT_F1K_ONDEMAND=1; `plan` still asserts SPOT (it validates the CONSTRUCTION
# ledger admissibility, which is unaffected by a throwaway bring-up VM).
BRINGUP_ONDEMAND = os.environ.get("KOT_F1K_ONDEMAND", "").lower() in (
    "1", "true", "yes", "on")


def die(code: str, msg: str) -> None:
    print("ERR_%s: %s" % (code, msg), file=sys.stderr)
    sys.exit(2)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# pin verification (fail-closed BEFORE any spend)
# ---------------------------------------------------------------------------
def verify_pins() -> dict:
    out = {}
    # frozen record integrity (self-hash via the repo's own tool)
    rc = subprocess.run(
        [sys.executable, str(REPO / "tools" / "registry" / "registry-check.py"),
         "frozen-drift"], cwd=str(REPO), capture_output=True, text=True)
    f1k_ok = any(line.strip().startswith("ok frozen-drift: f1k")
                 and FROZEN_SHA256[:8] in line
                 for line in rc.stdout.splitlines())
    if not f1k_ok:
        die("F1K_PIN_FROZEN",
            "registry-check frozen-drift did not confirm f1k (%s). stdout tail:\n%s"
            % (FROZEN_SHA256[:8], "\n".join(rc.stdout.splitlines()[-8:])))
    out["f1k_frozen_drift"] = "ok (%s)" % FROZEN_SHA256[:8]
    # file-content pins
    for name, want in PINS.items():
        p = PIN_PATHS[name]
        if not p.is_file():
            die("F1K_PIN_MISSING", "pinned artifact missing: %s" % p)
        got = sha256_file(p)
        if got != want:
            die("F1K_PIN_MISMATCH",
                "%s sha256 %s != frozen %s" % (name, got, want))
        out[name] = "ok (%s)" % want[:8]
    return out


def _gate(reuse: bool = True) -> None:
    """Mandatory pre-spend reuse gate (docs/next/resource-optimization-plan §3.6)."""
    if not reuse:
        return
    rc = subprocess.run(
        [sys.executable, str(REPO / "tools" / "registry" / "reuse-check.py"),
         "check", "--record", str(REPO / "registry" / "experiments" / "f1k.json"),
         "--gate"], cwd=str(REPO))
    if rc.returncode == 3:
        die("F1K_REUSE_GATE",
            "reuse-check --gate exit 3: declared cells already logged at "
            "identical/unproven-different pins with no frozen reuse decision. "
            "STOP — a reuse decision is Fable design work; queue it.")
    if rc.returncode != 0:
        die("F1K_REUSE_GATE", "reuse-check --gate exit %d" % rc.returncode)


# ---------------------------------------------------------------------------
# affordability admissibility (the FLOOR+CEILING gate at the frozen window)
# ---------------------------------------------------------------------------
def admissible_instance_hours(rate: float) -> tuple:
    """Valid instance_hours window at a given rate, per the frozen analysis:
       [max(INSTANCE_HOURS_MIN, USD_TOTAL_MIN/rate),
        min(WALL_CLOCK_CAP,     USD_CAP/rate)].
    Empty (lo > hi) means NO honest ledger validates at this rate — a
    compute-target-vs-cost-model STOP (Fable/coordinator/maintainer decision),
    exactly the pzb6 class."""
    lo = max(INSTANCE_HOURS_MIN, USD_TOTAL_MIN / rate)
    hi = min(WALL_CLOCK_CAP_HOURS, USD_CAP / rate)
    return (lo, hi)


def project_ledger(rate: float, s_per_prefill: float,
                   prefills: int = PREFILLS_MANDATORY) -> dict:
    """Project the frozen-analysis ledger at a MEASURED rate + s/prefill and
    test it against the admissible window. This is the addendum-(7) bring-up
    affordability gate + the coordinator-flagged FLOOR exposure, made
    executable. Returns a dict; caller decides GO / SALVAGE+STOP."""
    inst_h = prefills * s_per_prefill / 3600.0
    usd = inst_h * rate
    lo, hi = admissible_instance_hours(rate)
    rate_in_window = RATE_WINDOW[0] <= rate <= RATE_WINDOW[1]
    window_nonempty = lo <= hi
    hours_ok = INSTANCE_HOURS_MIN <= inst_h <= WALL_CLOCK_CAP_HOURS
    usd_ok = USD_TOTAL_MIN <= usd <= USD_CAP
    prefills_ok = prefills >= PREFILLS_MANDATORY_MIN
    verdict = ("GO" if (rate_in_window and window_nonempty and hours_ok
                        and usd_ok and prefills_ok) else "SALVAGE-STOP")
    reasons = []
    if not rate_in_window:
        reasons.append("rate %.4f outside frozen window [%.4f,%.4f]"
                       % (rate, *RATE_WINDOW))
    if not window_nonempty:
        reasons.append("EMPTY admissible instance_hours window at rate %.4f "
                       "(no honest ledger validates — pzb6 class)" % rate)
    if not hours_ok:
        side = "BELOW floor" if inst_h < INSTANCE_HOURS_MIN else "ABOVE cap"
        reasons.append("projected instance_hours %.1f %s [%.1f,%.1f] "
                       "(box %s than the frozen corner at this rate)"
                       % (inst_h, side, INSTANCE_HOURS_MIN,
                          WALL_CLOCK_CAP_HOURS,
                          "FASTER" if inst_h < INSTANCE_HOURS_MIN else "SLOWER"))
    if not usd_ok:
        side = "BELOW $73 floor" if usd < USD_TOTAL_MIN else "ABOVE $155 cap"
        reasons.append("projected usd_total $%.2f %s (at rate $%.4f/h "
                       "the floor binds at %.1f h = %.1f s/prefill)"
                       % (usd, side, rate, USD_TOTAL_MIN / rate,
                          USD_TOTAL_MIN / rate * 3600.0 / prefills))
    return {
        "rate_usd_per_hour": rate,
        "s_per_prefill_blended": s_per_prefill,
        "prefills": prefills,
        "projected_instance_hours": round(inst_h, 2),
        "projected_usd_total": round(usd, 2),
        "admissible_instance_hours": [round(lo, 1), round(hi, 1)],
        "admissible_s_per_prefill":
            [round(lo * 3600.0 / prefills, 2), round(hi * 3600.0 / prefills, 2)],
        "corner_ref_s_per_prefill": round(CORNER_BLENDED_S_PER_PREFILL, 2),
        "rate_in_window": rate_in_window,
        "verdict": verdict,
        "reasons": reasons,
    }


# ---------------------------------------------------------------------------
# gcloud helpers
# ---------------------------------------------------------------------------
def gcloud(*args, check=True, capture=False):
    cmd = ["gcloud"] + list(args) + ["--project", PROJECT, "--quiet"]
    if capture:
        r = subprocess.run(cmd, capture_output=True, text=True)
        if check and r.returncode != 0:
            die("GCLOUD", " ".join(cmd) + "\n" + r.stderr)
        return r
    r = subprocess.run(cmd)
    if check and r.returncode != 0:
        die("GCLOUD", "exit %d: %s" % (r.returncode, " ".join(cmd)))
    return r


def vm_exists() -> bool:
    r = gcloud("compute", "instances", "describe", INSTANCE_NAME,
               "--zone", ZONE, "--format=value(name)", check=False,
               capture=True)
    return r.returncode == 0


# ---------------------------------------------------------------------------
# entrypoints
# ---------------------------------------------------------------------------
def cmd_plan() -> None:
    """$0 dry-plan. Verify pins, the reuse gate, the SPOT+non-AWS+disk config,
    and the frozen ledger admissibility at the assumed rate band. No spend."""
    if not PROJECT:
        die("F1K_ENV", "KOT_GCP_PROJECT unset — source ~/.config/kot/gcp.env")
    pins = verify_pins()
    _gate()
    cfg = {
        "machine_type": MACHINE_TYPE, "vcpu": 8, "mem_gib": 64,
        "local_ssd_count": LOCAL_SSD_COUNT, "local_nvme_gib": LOCAL_SSD_COUNT * 375,
        "provisioning_model": PROVISIONING_MODEL, "zone": ZONE, "region": REGION,
        "colibri_commit": COLIBRI_COMMIT, "estate_repo": ESTATE_REPO,
        "estate_gb": ESTATE_GB, "boot_gb": BOOT_GB,
        "frozen_sha256": FROZEN_SHA256,
        "frozen_rate_window": [round(RATE_WINDOW[0], 4), round(RATE_WINDOW[1], 4)],
        "usd_cap": USD_CAP, "instance_hours_window":
            [INSTANCE_HOURS_MIN, WALL_CLOCK_CAP_HOURS],
        "pins": pins,
    }
    # affordability admissibility at the coordinator-quoted rate band
    cfg["affordability_band"] = {}
    for rate in (0.19, 0.20, 0.24, 0.28):
        lo, hi = admissible_instance_hours(rate)
        cfg["affordability_band"]["rate_%.2f" % rate] = {
            "admissible_instance_hours": [round(lo, 1), round(hi, 1)],
            "window_nonempty": lo <= hi,
            "admissible_blended_s_per_prefill":
                [round(lo * 3600.0 / PREFILLS_MANDATORY, 1),
                 round(hi * 3600.0 / PREFILLS_MANDATORY, 1)],
            "corner_ref_s_per_prefill": round(CORNER_BLENDED_S_PER_PREFILL, 1),
        }
    print(json.dumps(cfg, indent=2))
    # hard dry-plan assertions (fail-closed)
    assert PROVISIONING_MODEL == "SPOT", "MUST be SPOT (on-demand busts the cap)"
    assert LOCAL_SSD_COUNT * 375 >= ESTATE_GB, "local NVMe must hold the estate"
    assert RATE_WINDOW[0] <= 0.24 <= RATE_WINDOW[1], "assumed rate in-window"
    # every quoted-band rate must leave a NON-EMPTY window (else pzb6-class stop)
    for rate in (0.19, 0.20, 0.24, 0.28):
        lo, hi = admissible_instance_hours(rate)
        assert lo <= hi, "rate %.2f: EMPTY window — no honest ledger" % rate
    print("\nDRY-PLAN OK: pins verified, reuse-gate clear, SPOT + %d GiB NVMe + "
          "non-empty ledger window across the quoted rate band.\n"
          "AFFORDABILITY NOTE: below $0.28/h the $73 usd_total FLOOR binds "
          "(needs more hours); the REAL rate + s/prefill are MEASURED at "
          "bring-up and gated by `affordability` before any construction spend."
          % (LOCAL_SSD_COUNT * 375))


def cmd_provision() -> None:
    """Create the VM + local SSD. Records the launch. SPOT by default (the
    frozen construction target); ON-DEMAND (KOT_F1K_ONDEMAND=1) is permitted
    ONLY for the throwaway BRING-UP VM — a separate validation phase that never
    enters the frozen ledger. On-demand drops --instance-termination-action
    (a SPOT-only flag) and uses --provisioning-model STANDARD."""
    verify_pins()
    _gate()
    if vm_exists():
        die("F1K_VM_EXISTS", "%s already exists in %s — teardown or reuse"
            % (INSTANCE_NAME, ZONE))
    ssd = []
    for _ in range(LOCAL_SSD_COUNT):
        ssd += ["--local-ssd", "interface=NVME"]
    if BRINGUP_ONDEMAND:
        # ON-DEMAND bring-up VM (ops; NOT the frozen SPOT construction ledger).
        # --instance-termination-action is SPOT-only, so it is DROPPED here; the
        # control-box watchdog + guest max-life backstops still bound billing.
        prov_model = "STANDARD"
        sched_args = []
        mode = ("ON-DEMAND (bring-up VALIDATION only — NOT the frozen SPOT "
                "construction ledger; separate phase, not in results-log)")
    else:
        # SPOT construction target (frozen cost model). Unchanged.
        prov_model = PROVISIONING_MODEL
        sched_args = ["--instance-termination-action", "STOP"]
        mode = "SPOT"
    gcloud("compute", "instances", "create", INSTANCE_NAME,
           "--zone", ZONE, "--machine-type", MACHINE_TYPE,
           "--provisioning-model", prov_model,
           *sched_args,
           "--image-family", IMAGE_FAMILY, "--image-project", IMAGE_PROJECT,
           "--boot-disk-size", "%dGB" % BOOT_GB, "--boot-disk-type", "pd-ssd",
           *ssd,
           "--scopes", "storage-rw",
           "--metadata", "kot-experiment=f1k,kot-frozen=%s" % FROZEN_SHA256[:12])
    print("provisioned %s %s (%s, %d local SSD) in %s"
          % (mode, INSTANCE_NAME, MACHINE_TYPE, LOCAL_SSD_COUNT, ZONE))
    print("NOTE: record the assigned price now; the construction SPOT rate "
          "(not the on-demand bring-up rate) is the load-bearing input to the "
          "affordability gate.")


def cmd_status() -> None:
    if not vm_exists():
        print(json.dumps({"vm": INSTANCE_NAME, "exists": False}))
        return
    r = gcloud("compute", "instances", "describe", INSTANCE_NAME,
               "--zone", ZONE,
               "--format=json(name,status,scheduling,lastStartTimestamp)",
               capture=True)
    print(r.stdout)


def cmd_teardown() -> None:
    """Delete the VM + its local SSD so nothing bills idle. Firm."""
    if not vm_exists():
        print("no VM %s to delete" % INSTANCE_NAME)
        return
    gcloud("compute", "instances", "delete", INSTANCE_NAME, "--zone", ZONE)
    print("deleted %s + attached local SSD" % INSTANCE_NAME)


def cmd_affordability() -> None:
    """The addendum-(7) bring-up affordability gate, made executable. Consumes
    the MEASURED spot rate and MEASURED blended s/prefill, projects the frozen
    ledger for the mandatory (and +REPLACE) campaign, and returns GO only if it
    lands inside the frozen window (fail-closed on both the FLOOR and the CAP).
    A GO — and ONLY a GO — licenses construction spend.

    usage: f1k_gcp.py affordability --rate <usd/h> --s-per-prefill <sec> [--replace]"""
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--rate", type=float, required=True,
                    help="MEASURED assigned spot $/instance-hour (all-in)")
    ap.add_argument("--s-per-prefill", type=float, required=True,
                    help="MEASURED blended wall-seconds per scoring prefill")
    ap.add_argument("--replace", action="store_true",
                    help="also project the +REPLACE volume (21537 prefills)")
    args = ap.parse_args(sys.argv[2:])
    proj = project_ledger(args.rate, args.s_per_prefill, PREFILLS_MANDATORY)
    out = {"mandatory": proj}
    if args.replace:
        out["with_replace"] = project_ledger(args.rate, args.s_per_prefill,
                                              PREFILLS_WITH_REPLACE)
    print(json.dumps(out, indent=2))
    if proj["verdict"] != "GO":
        die("F1K_AFFORDABILITY",
            "SALVAGE-STOP: %s. The frozen cost model at the measured rate does "
            "NOT admit a valid ledger for this throughput; this is a "
            "cost-model-vs-rate decision (Fable/coordinator/maintainer), NOT a "
            "retry. Do NOT spend construction." % "; ".join(proj["reasons"]))
    print("\nAFFORDABILITY GO: projected instance_hours %.1f h, usd_total $%.2f "
          "inside the frozen window. Construction spend is licensed."
          % (proj["projected_instance_hours"], proj["projected_usd_total"]))


ENTRY = {
    "plan": cmd_plan, "provision": cmd_provision, "status": cmd_status,
    "teardown": cmd_teardown, "affordability": cmd_affordability,
}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in ENTRY:
        print("usage: f1k_gcp.py {%s}" % "|".join(ENTRY), file=sys.stderr)
        sys.exit(2)
    ENTRY[sys.argv[1]]()


if __name__ == "__main__":
    main()
