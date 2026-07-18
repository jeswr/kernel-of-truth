#!/usr/bin/env python3
"""f1k_gcp.py — GCP-Spot orchestrator for the FROZEN F1-K correctness run.

OPUS EXECUTION-role harness (kern/opus-runner-<N>). It RUNS the already-frozen
F1-K experiment (registry/experiments/f1k.json, frozen_sha256 35372275…) on the
coordinator-resolved compute target (bead pzb6): a GCP **Spot** n2d-highmem-8
(8 vCPU / 64 GB) + 2×375 GiB local SSD (750 GiB NVMe), zone us-central1-a.
It designs NOTHING and concludes NOTHING: the science (kernel, model, engine,
carriers, protocol, analysis) is frozen upstream; this file only provisions,
stages, builds, drives the pinned generator/driver, checkpoints, monitors, and
tears down — from the frozen RunSpec, fail-closed on any pin mismatch.

Compute-target economics (why GCP Spot, not Modal): the pinned analysis
analysis/f1k.py (sha 126129b9) hard-enforces a ledger window
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
  python3 poc/gcp/f1k_gcp.py provision     # create the Spot VM + 2 local SSD
  python3 poc/gcp/f1k_gcp.py gate          # bring-up gate VERDICT (GREEN is
                                           #   the ONLY construction license;
                                           #   --selftest = $0 mock oracle)
  python3 poc/gcp/f1k_gcp.py affordability # SECONDARY synthetic diagnostic
                                           #   ONLY — licenses NOTHING
  python3 poc/gcp/f1k_gcp.py bringup-deploy# RAID+mount NVMe, push the worker
                                           #   bundle + frozen gate corpora,
                                           #   launch f1k_worker.sh detached,
                                           #   arm the GUEST max-life backstop
  python3 poc/gcp/f1k_gcp.py watchdog --max-hours H
                                           # box-side teardown watchdog loop
                                           #   (nohup it; verify with pgrep)
  python3 poc/gcp/f1k_gcp.py pin-fetch     # fetch + BYTE-VERIFY the licensed
                                           #   campaign pin; prints the exact
                                           #   PIN/PIN_GB exports [REV-B]
  python3 poc/gcp/f1k_gcp.py status        # poll VM state + GCS heartbeat
  python3 poc/gcp/f1k_gcp.py teardown      # delete VM + disks (nothing bills idle)
(stage/build/KaE+dump bring-up run ON the VM via f1k_worker.sh — they were
never control-box entrypoints; the retired push/stage/build/bringup docstring
advertisement was CONSTRUCTION-PLAN v3 GAP-4.)
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
WORKER_FLAT_FILES = (
    "f1k_worker.sh", "bringup_gcp.sh", "f1k_bringup_gate.py", "f1k_ops.py",
)

# ---------------------------------------------------------------------------
# FROZEN PINS (registry/experiments/f1k.json 35372275…; verified at launch)
# ---------------------------------------------------------------------------
FROZEN_SHA256 = "35372275354c7d3841dcf627b70edf64ffbe15190a0669658c5b6df082dc9b9c"
COLIBRI_COMMIT = "a78a06fc5acc4b0dc0f9ef03987c66b0559d1250"
ESTATE_REPO = "mateogrgic/GLM-5.2-colibri-int4-with-int8-mtp"
ESTATE_GB = 383.8
PINS = {
    "analysis/f1k.py":
        "126129b9ce78e398122b3d3bf0855b7e551a892ba43d7d1a8d072a1245fb3326",
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
GCE_ACCESS_SCOPE = "cloud-platform"
DEFAULT_GUEST_MAXLIFE_MIN = 900

PROJECT = os.environ.get("KOT_GCP_PROJECT", "")
ZONE = os.environ.get("KOT_GCP_ZONE", "us-central1-a")
REGION = os.environ.get("KOT_GCP_REGION", "us-central1")

# The environment spelling is retained only so provision can reject the old
# override explicitly.  B is a single-VM-SPOT flow; a STANDARD VM can never
# satisfy construction-ready's live SPOT identity check.
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


def _is_construction_run_output(rel: Path) -> bool:
    """True for run products that must never enter the tracked payload."""
    output_dirs = {"opus-runs", "mock-out", "probe-results",
                   "results-incoming", "run-outputs"}
    output_names = {"run-log.jsonl", "construction-report.json",
                    "worker.log", "launcher.log",
                    "failed-heartbeat.json", "FAILED"}
    return (any(part in output_dirs for part in rel.parts)
            or rel.suffix == ".log"
            or rel.name.startswith("mock-out-")
            or rel.name in output_names)


def _construction_payload_files() -> list[Path]:
    """Resolve the reviewed, tracked construction subset, fail-closed."""
    required = (
        Path("poc/glm52-probe/f1k-harness/build_carriers.py"),
        Path("poc/glm52-probe/f1k-harness/f1k_driver.py"),
        Path("poc/glm52-probe/f1k-harness/tok_glm52.py"),
        Path("poc/gcp/f1k_gcp.py"),
        Path("poc/gcp/f1k_worker.sh"),
        Path("poc/gcp/bringup_gcp.sh"),
        Path("poc/gcp/f1k_bringup_gate.py"),
        Path("poc/gcp/f1k_ops.py"),
        Path("analysis/f1k.py"),
        Path("registry/experiments/f1k.json"),
        Path("registry/frozen-index.json"),
    )
    tree_prefixes = [
        Path("poc/glm52-probe/kae-patch-draft"),
        Path("tools/registry"),
        Path("registry/schema"),
        Path("data/f1k-eval-v1"),
        Path("data/f1k-trigger-map-v1"),
    ]
    optional_carriers = Path("data/f1k-carriers-v1")
    if (REPO / optional_carriers).exists():
        if not (REPO / optional_carriers).is_dir():
            die("F1K_CONSTRUCTION_PAYLOAD",
                "%s exists but is not a directory" % optional_carriers)
        tree_prefixes.append(optional_carriers)
    pathspecs = ([str(p) for p in required]
                 + [str(p) for p in tree_prefixes]
                 + ["poc/glm52-probe/f1k-harness/mock*.py"])
    try:
        rc = subprocess.run(["git", "ls-files", "-z", "--", *pathspecs],
                            cwd=str(REPO), capture_output=True)
    except OSError as exc:
        die("F1K_CONSTRUCTION_PAYLOAD",
            "cannot resolve tracked payload with git ls-files (%s)" % exc)
    if rc.returncode != 0:
        die("F1K_CONSTRUCTION_PAYLOAD",
            "git ls-files failed: %s"
            % rc.stderr.decode("utf-8", "replace").strip())
    rels = sorted({Path(os.fsdecode(raw))
                   for raw in rc.stdout.split(b"\0") if raw})
    unsafe = [str(rel) for rel in rels
              if rel.is_absolute() or ".." in rel.parts]
    if unsafe:
        die("F1K_CONSTRUCTION_PAYLOAD",
            "git returned unsafe paths: %s" % ", ".join(unsafe))
    rels = [rel for rel in rels
            if not _is_construction_run_output(rel)]
    if not rels:
        die("F1K_CONSTRUCTION_PAYLOAD",
            "reviewed git ls-files subset is empty")
    missing_required = [str(rel) for rel in required if rel not in rels]
    empty_prefixes = [str(prefix) for prefix in tree_prefixes
                      if not any(rel == prefix or prefix in rel.parents
                                 for rel in rels)]
    harness = Path("poc/glm52-probe/f1k-harness")
    has_mock = any(rel.parent == harness
                   and rel.name.startswith("mock")
                   and rel.suffix == ".py" for rel in rels)
    if missing_required or empty_prefixes or not has_mock:
        problems = []
        if missing_required:
            problems.append("required files absent/untracked: %s"
                            % ", ".join(missing_required))
        if empty_prefixes:
            problems.append("reviewed prefixes empty: %s"
                            % ", ".join(empty_prefixes))
        if not has_mock:
            problems.append("tracked harness mock*.py subset empty")
        die("F1K_CONSTRUCTION_PAYLOAD", "; ".join(problems))
    missing_files = [str(rel) for rel in rels
                     if not (REPO / rel).is_file()]
    if missing_files:
        die("F1K_CONSTRUCTION_PAYLOAD",
            "tracked payload files missing: %s" % ", ".join(missing_files))
    return [REPO / rel for rel in rels]


def _provision_plan(*, on_demand: bool, max_life_min: int) -> dict:
    """Pure executable provisioning contract, shared with the local oracle."""
    if on_demand:
        raise ValueError(
            "KOT_F1K_ONDEMAND is forbidden: B requires one SPOT VM and "
            "construction-ready refuses every non-SPOT instance"
        )
    if isinstance(max_life_min, bool) or not isinstance(max_life_min, int) \
            or max_life_min < 1:
        raise ValueError("KOT_F1K_GUEST_MAXLIFE_MIN must be a positive integer")
    return {
        "provisioning_model": PROVISIONING_MODEL,
        "scope": GCE_ACCESS_SCOPE,
        "guest_max_life_min": max_life_min,
        "startup_script": (
            "#!/usr/bin/env bash\n"
            "shutdown -P +%d 'kot-f1k guest max-life backstop'\n"
            % max_life_min
        ),
    }


def _bringup_deploy_selftest() -> int:
    """$0 staging-plan oracle: local files + git only, never GCP."""
    payload = _construction_payload_files()
    rels = [p.relative_to(REPO) for p in payload]
    relset = set(rels)
    builder = Path("poc/glm52-probe/f1k-harness/build_carriers.py")
    builder_sha = sha256_file(REPO / builder)
    worker_layout = (
        *WORKER_FLAT_FILES,
        "f1k_launch.sh (generated)", "tok_glm52.py",
        "kae-patch-draft/", "dump-patch/",
        "gate-corpus/construction-manifest.jsonl",
        "gate-corpus/test.jsonl", "gate-corpus/dev.jsonl",
        "gate-corpus/guard.jsonl", "bundle-manifest.json (generated)",
    )
    plan_bytes = ("\n".join(str(rel) for rel in rels) + "\n").encode()
    print("SELFTEST SCOPE: $0 local bringup-deploy staging plan; "
          "NO gcloud, SSH, GCS, VM, worker, or construction launch.")
    print("BRINGUP-DEPLOY STAGING PLAN:")
    print("  worker-layout: %s" % ", ".join(worker_layout))
    print("  construction-payload: %d tracked repo-relative files"
          % len(rels))
    print("  construction-plan-sha256: %s"
          % hashlib.sha256(plan_bytes).hexdigest())
    provision_plan = _provision_plan(
        on_demand=False, max_life_min=DEFAULT_GUEST_MAXLIFE_MIN
    )
    print("  build_carriers.py-sha256: %s" % builder_sha)
    print("  provision: model=%s, scope=%s, guest-max-life=%d min "
          "(startup-script armed)"
          % (provision_plan["provisioning_model"], provision_plan["scope"],
             provision_plan["guest_max_life_min"]))
    for rel in (
            "poc/glm52-probe/f1k-harness/build_carriers.py",
            "poc/glm52-probe/f1k-harness/f1k_driver.py",
            "poc/glm52-probe/f1k-harness/tok_glm52.py",
            "poc/gcp/f1k_bringup_gate.py", "poc/gcp/f1k_ops.py"):
        print("    required: %s" % rel)
    print("  exclusions: opus-runs/, *.log, mock/probe/results run outputs")
    passed = 0
    total = 0

    def check(cond: bool, label: str) -> None:
        nonlocal passed, total
        total += 1
        if cond:
            passed += 1
        print("  %s %s" % ("ok:  " if cond else "FAIL:", label))

    check(bool(rels) and all(p.is_file() for p in payload),
          "construction payload is nonempty and every listed file exists")
    check(builder in relset and builder_sha == PINS["build_carriers.py"],
          "build_carriers.py present and sha a92be3e4...")
    check(Path("poc/glm52-probe/f1k-harness/f1k_driver.py") in relset,
          "f1k_driver.py present")
    check(Path("poc/gcp/f1k_bringup_gate.py") in relset,
          "f1k_bringup_gate.py present")
    check(Path("poc/gcp/f1k_ops.py") in relset, "f1k_ops.py present")
    check(Path("poc/glm52-probe/f1k-harness/tok_glm52.py") in relset,
          "tok_glm52.py present")
    check(not any("opus-runs" in rel.parts for rel in rels),
          "opus-runs/ excluded from construction payload")
    check(not any(_is_construction_run_output(rel) for rel in rels),
          "run outputs excluded from construction payload")
    items = REPO / "data" / "f1k-eval-v1" / "items"
    worker_sources = tuple(HERE / name for name in WORKER_FLAT_FILES) + (
        HARNESS / "tok_glm52.py", PIN_PATHS["construction-manifest.jsonl"],
        items / "test.jsonl", items / "dev.jsonl", items / "guard.jsonl",
    )
    check(all(p.is_file() for p in worker_sources)
          and "f1k_ops.py" in WORKER_FLAT_FILES
          and KAE_PATCH_DIR.is_dir() and DUMP_PATCH_DIR.is_dir(),
          "flat worker-layout sources, including f1k_ops.py, remain present")
    try:
        _provision_plan(on_demand=True,
                        max_life_min=DEFAULT_GUEST_MAXLIFE_MIN)
    except ValueError:
        on_demand_refused = True
    else:
        on_demand_refused = False
    check(on_demand_refused, "KOT_F1K_ONDEMAND is refused by provision")
    check(provision_plan["provisioning_model"] == "SPOT"
          and provision_plan["scope"] == "cloud-platform"
          and provision_plan["guest_max_life_min"] > 0
          and "shutdown -P +" in provision_plan["startup_script"],
          "provision plan is cloud-platform SPOT with a guest max-life bound")
    print("SELFTEST: %d/%d %s"
          % (passed, total, "PASS" if passed == total else "FAILED"))
    return 0 if passed == total else 2


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
    """Create the single B SPOT VM + local SSDs and arm its max-life at boot."""
    try:
        provision = _provision_plan(
            on_demand=BRINGUP_ONDEMAND,
            max_life_min=int(os.environ.get(
                "KOT_F1K_GUEST_MAXLIFE_MIN",
                str(DEFAULT_GUEST_MAXLIFE_MIN),
            )),
        )
    except ValueError as exc:
        die("F1K_SINGLE_VM_SPOT", str(exc))
    verify_pins()
    _gate()
    if vm_exists():
        die("F1K_VM_EXISTS", "%s already exists in %s — teardown or reuse"
            % (INSTANCE_NAME, ZONE))
    ssd = []
    for _ in range(LOCAL_SSD_COUNT):
        ssd += ["--local-ssd", "interface=NVME"]
    metadata = (
        "kot-experiment=f1k,kot-frozen=%s,startup-script=%s"
        % (FROZEN_SHA256[:12], provision["startup_script"])
    )
    # cloud-platform is the OAuth ceiling only: the service account still needs
    # compute.instances.get and Billing Catalog read via least-privilege IAM.
    gcloud("compute", "instances", "create", INSTANCE_NAME,
           "--zone", ZONE, "--machine-type", MACHINE_TYPE,
           "--provisioning-model", provision["provisioning_model"],
           "--instance-termination-action", "STOP",
           "--image-family", IMAGE_FAMILY, "--image-project", IMAGE_PROJECT,
           "--boot-disk-size", "%dGB" % BOOT_GB, "--boot-disk-type", "pd-ssd",
           *ssd,
           "--scopes", provision["scope"],
           "--metadata", metadata)
    print("provisioned SPOT %s (%s, %d local SSD) in %s; guest max-life "
          "%d min armed by startup script"
          % (INSTANCE_NAME, MACHINE_TYPE, LOCAL_SSD_COUNT, ZONE,
             provision["guest_max_life_min"]))
    print("NOTE: record the assigned SPOT price now; it is the load-bearing "
          "input to the affordability gate.")


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
    """SECONDARY DIAGNOSTIC ONLY (F1K-BRINGUP-GATE-FIX.md v1, GAP-1): projects
    the frozen ledger from ONE blended s/prefill (historically the synthetic
    functional-gate mix). It LICENSES NOTHING — the v2 review (finding 4)
    showed the synthetic blend mis-prices the gate in both directions. The
    construction license is `f1k_gcp.py gate` (kot-f1k-bringup-gate/2:
    real-corpus stratified sample + measured f + PER-ITEM token-aware
    projection) and ONLY that.

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
    # v3-review fix (:417/:423 lineage): EVERY tested projection must be GO,
    # or this exits nonzero — the +REPLACE verdict is never advisory. And a
    # clean diagnostic still exits 3: this blended path can NEVER license.
    bad = {name: p for name, p in out.items() if p["verdict"] != "GO"}
    if bad:
        die("F1K_AFFORDABILITY",
            "SALVAGE-STOP (%s): %s. The frozen cost model at the measured "
            "rate does NOT admit a valid ledger for EVERY tested projection; "
            "this is a cost-model-vs-rate decision (Fable/coordinator/"
            "maintainer), NOT a retry. Do NOT spend construction."
            % (", ".join(sorted(bad)),
               " | ".join("%s: %s" % (n, "; ".join(p["reasons"]))
                          for n, p in sorted(bad.items()))))
    print("\nAFFORDABILITY DIAGNOSTIC: every tested projection inside the "
          "frozen window — SECONDARY diagnostic only, NEVER a license "
          "(exit 3); the construction license is `f1k_gcp.py gate` (GREEN, "
          "reserve-inclusive, dump-preconditions conjoined).")
    sys.exit(3)


def cmd_gate() -> None:
    """The FIXED bring-up affordability gate verdict (kot-f1k-bringup-gate/2;
    poc/gcp/F1K-BRINGUP-GATE-FIX.md v1, closing CONSTRUCTION-PLAN v3 §4.2
    GAP-1/2/3). Consumes the on-VM gate-inputs.json (f1k_worker.sh step 5/5:
    real-corpus stratified per-item timing + measured f + per-item token
    counts), re-verifies the launch pins + corpus bytes, projects the frozen
    ledger PER-ITEM via f1k_bringup_gate.project, and emits bringup-gate.json
    with the MECHANICAL plan-§7 verdict:
      GREEN -> construction proceeds WITHOUT re-surfacing (standing auth);
      STOP  -> exit 2 ERR_F1K_BRINGUP_GATE, MANDATORY maintainer surface.

    usage: f1k_gcp.py gate --inputs <gate-inputs.json> [--out <path>] [--replace]
           f1k_gcp.py gate --selftest        # $0 mock oracle, no VM"""
    sys.path.insert(0, str(HERE))
    import f1k_bringup_gate as bg
    if "--selftest" in sys.argv[2:]:
        sys.exit(bg.selftest())
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--out", default=str(HERE / "bringup-gate.json"))
    ap.add_argument("--replace", action="store_true")
    args = ap.parse_args(sys.argv[2:])
    verify_pins()
    _gate()
    frozen = {"instance_hours": [INSTANCE_HOURS_MIN, WALL_CLOCK_CAP_HOURS],
              "usd_total": [USD_TOTAL_MIN, USD_CAP],
              "rate_window": [RATE_WINDOW[0], RATE_WINDOW[1]],
              "prefills_min": PREFILLS_MANDATORY_MIN}
    inputs = json.loads(Path(args.inputs).read_text(encoding="utf-8"))
    # corpus-drift check: the VM must have tokenized the SAME bytes this repo
    # pins (construction-manifest via PINS; eval items are covered by the
    # frozen record's f1k-eval-v1 corpus digest)
    items = REPO / "data" / "f1k-eval-v1" / "items"
    local = {"construction-manifest.jsonl":
             sha256_file(PIN_PATHS["construction-manifest.jsonl"]),
             "test.jsonl": sha256_file(items / "test.jsonl"),
             "dev.jsonl": sha256_file(items / "dev.jsonl"),
             "guard.jsonl": sha256_file(items / "guard.jsonl")}
    got = inputs["token_counts"]["corpus_sha256"]
    for name, want in local.items():
        if got.get(name) != want:
            die("F1K_GATE_CORPUS_DRIFT", "%s sha on the VM %s != repo %s"
                % (name, got.get(name), want))
    art = bg.project(inputs, frozen, replace=args.replace, out_path=args.out)
    print(json.dumps(art, indent=2))
    if art["verdict"] != "GREEN":
        die("F1K_BRINGUP_GATE",
            "STOP: %s. MANDATORY maintainer surface with salvage options "
            "(plan §7.3): (a) the <=$300 contingent re-freeze [maintainer "
            "decision, never autonomous]; (b) SSR6 degradation within the "
            "original windows; (c) stop-and-hold. Do NOT spend construction."
            % "; ".join(art["reasons"]))
    print("\nBRING-UP GATE GREEN (artifact: %s): measured f %.4f <= 1.60 AND "
          "the PER-ITEM projected ledger (%.1f h central / $%.2f) lands "
          "inside the frozen windows. Construction proceeds under the plan "
          "§7 standing authorization (report-after, no re-surface)."
          % (args.out, art["f"]["blended"],
             art["projection"]["instance_hours"]["central"],
             art["projection"]["usd_total"]["central"]))


def cmd_bringup_deploy() -> None:
    """Bind the bring-up plumbing the v3 review found UNBOUND (`provision`
    creates only the VM; the historical run-dir wrappers vm_setup.sh
    aa6504d6 / watchdog.sh 8efa0f65 are hard-coded and uncommitted): RAID0 +
    mount the 2 local NVMe, push the worker bundle in the layout
    f1k_worker.sh expects ($HERE/{kae-patch-draft,dump-patch,gate-corpus},
    f1k_bringup_gate.py + tok_glm52.py + bringup_gcp.sh alongside), launch
    the worker detached (setsid nohup), and arm the GUEST max-life backstop
    (root `shutdown -P`; default 900 min via KOT_F1K_GUEST_MAXLIFE_MIN).

    MANUAL PREREQS (verify, never assume):
      gsutil ls "$KOT_F1K_BUCKET"          # bucket reachable
      env: KOT_F1K_BUCKET, COLIBRI_GIT_URL, KOT_F1K_SPOT_RATE set
    MANUAL FOLLOW-UP (box-side, NEVER agent-held — plan v3 SS9 rule 1):
      nohup python3 poc/gcp/f1k_gcp.py watchdog --max-hours 8 \
        > watchdog.log 2>&1 &
      verify: pgrep -f 'f1k_gcp.py watchdog'
      guest max-life verify: gcloud compute ssh ... 'sudo shutdown --show'"""
    import shutil, tempfile
    if "--selftest" in sys.argv[2:]:
        sys.exit(_bringup_deploy_selftest())
    verify_pins()
    construction_files = _construction_payload_files()
    if not vm_exists():
        die("F1K_DEPLOY", "no VM %s in %s — run provision first"
            % (INSTANCE_NAME, ZONE))
    for var in ("KOT_F1K_BUCKET", "COLIBRI_GIT_URL", "KOT_F1K_SPOT_RATE"):
        if not os.environ.get(var):
            die("F1K_DEPLOY", "%s unset (f1k_worker.sh env contract)" % var)
    max_life_min = int(os.environ.get(
        "KOT_F1K_GUEST_MAXLIFE_MIN", str(DEFAULT_GUEST_MAXLIFE_MIN)
    ))
    # 1. remote prep [REV-B F4, gate-fix review #5]:
    #    - DEPENDENCIES the worker actually needs, VERIFIED on a fresh
    #      image: google-cloud-cli (gsutil — chosen over curl+signed URLs
    #      because the worker performs MANY dynamic writes: estate rsync,
    #      heartbeats, gate mirrors; per-object URL minting is unworkable,
    #      and the VM's service account auths gsutil natively) +
    #      python3-pip (tokenizers/HF staging). Most GCE images ship both
    #      — verify, never assume.
    #    - RAID by STATE, not directory existence: `mountpoint -q` decides;
    #      a reboot re-assembles /dev/md0 and re-MOUNTS (mkfs ONLY on
    #      first creation) — a bare /mnt/nvme dir on the boot disk can
    #      never silently swallow the ~384 GB estate.
    remote = (
        "set -euo pipefail\n"
        "sudo apt-get update -qq\n"
        "command -v gsutil >/dev/null 2>&1"
        " || sudo apt-get install -y -qq google-cloud-cli\n"
        "command -v gsutil >/dev/null 2>&1"
        " || { echo 'ERR: gsutil unavailable (google-cloud-cli install"
        " failed)'; exit 2; }\n"
        "command -v pip3 >/dev/null 2>&1"
        " || sudo apt-get install -y -qq python3-pip\n"
        "command -v pip3 >/dev/null 2>&1"
        " || { echo 'ERR: pip3 unavailable'; exit 2; }\n"
        "if ! mountpoint -q /mnt/nvme; then\n"
        "  sudo apt-get install -y -qq mdadm\n"
        "  if [ ! -e /dev/md0 ]; then\n"
        "    sudo mdadm --assemble /dev/md0 2>/dev/null || true\n"
        "  fi\n"
        "  if [ ! -e /dev/md0 ]; then\n"
        "    DEVS=$(ls /dev/disk/by-id/google-local-nvme-ssd-* 2>/dev/null)\n"
        "    N=$(echo \"$DEVS\" | wc -w)\n"
        "    [ \"$N\" -eq %d ] || { echo \"ERR: $N local NVMe != %d\"; exit 2; }\n"
        "    sudo mdadm --create /dev/md0 --level=0 --raid-devices=%d $DEVS\n"
        "    sudo mkfs.ext4 -F /dev/md0\n"
        "  fi\n"
        "  sudo mkdir -p /mnt/nvme\n"
        "  sudo mount /dev/md0 /mnt/nvme && sudo chown \"$USER\" /mnt/nvme\n"
        "  mountpoint -q /mnt/nvme"
        " || { echo 'ERR: /mnt/nvme still not a mountpoint'; exit 2; }\n"
        "fi\n"
        "sudo shutdown -c 'kot-f1k deploy max-life re-arm' 2>/dev/null || true\n"
        "sudo shutdown -P +%d 'kot-f1k guest max-life backstop'\n"
        % (LOCAL_SSD_COUNT, LOCAL_SSD_COUNT, LOCAL_SSD_COUNT, max_life_min))
    gcloud("compute", "ssh", INSTANCE_NAME, "--zone", ZONE,
           "--command", remote)
    # 2. assemble the bundle locally in the worker's expected layout
    stage = Path(tempfile.mkdtemp(prefix="kot-f1k-bundle-"))
    bundle = stage / "f1k"
    bundle.mkdir()
    for f in WORKER_FLAT_FILES:
        shutil.copy2(HERE / f, bundle / f)
    # [REV-B F4] failure-visible launcher: ANY worker exit != 0 — incl.
    # `set -e` deaths that bypass die() and its heartbeat — writes a
    # FAILED heartbeat the watchdog acts on promptly (no max-life wait).
    # [REV-C, rereview finding 4 residual] the GCS upload is no longer a
    # single `|| true` shot: (1) a LOCAL on-disk FAILED marker is written
    # FIRST (unconditional — visible to the watchdog's SSH-side probe even
    # when GCS/auth/network is down), then (2) the upload retries 5x with
    # exponential backoff. HONEST RESIDUAL: if GCS is unreachable AND the
    # VM is not SSH-reachable (dead sshd/network), the failure stays
    # invisible until the guest max-life backstop — stated, not hidden.
    (bundle / "f1k_launch.sh").write_text(
        "#!/usr/bin/env bash\n"
        "# generated by f1k_gcp.py bringup-deploy [REV-B F4 + REV-C]\n"
        "cd \"$(dirname \"$0\")\"\n"
        "bash f1k_worker.sh > worker.log 2>&1\n"
        "rc=$?\n"
        "if [ \"$rc\" -ne 0 ]; then\n"
        "  printf '{\"ts\":\"%s\",\"stage\":\"FAILED: worker exit rc=%d\","
        "\"rc\":%d}\\n' \"$(date -u +%FT%TZ)\" \"$rc\" \"$rc\" "
        "> failed-heartbeat.json\n"
        "  cp failed-heartbeat.json FAILED   # local marker, ALWAYS [REV-C]\n"
        "  for i in 1 2 3 4 5; do\n"
        "    gsutil -q cp failed-heartbeat.json "
        "\"$KOT_F1K_BUCKET/f1k/bringup/heartbeat.json\" && break\n"
        "    echo \"heartbeat upload attempt $i failed; retrying\" >&2\n"
        "    sleep $((2**i))\n"
        "  done\n"
        "fi\n"
        "exit \"$rc\"\n")
    shutil.copy2(HARNESS / "tok_glm52.py", bundle / "tok_glm52.py")
    shutil.copytree(KAE_PATCH_DIR, bundle / "kae-patch-draft")
    shutil.copytree(DUMP_PATCH_DIR, bundle / "dump-patch")
    gc = bundle / "gate-corpus"
    gc.mkdir()
    shutil.copy2(PIN_PATHS["construction-manifest.jsonl"],
                 gc / "construction-manifest.jsonl")
    items = REPO / "data" / "f1k-eval-v1" / "items"
    for f in ("test.jsonl", "dev.jsonl", "guard.jsonl"):
        shutil.copy2(items / f, gc / f)
    builder_sha = sha256_file(PIN_PATHS["build_carriers.py"])
    if builder_sha != PINS["build_carriers.py"]:
        die("F1K_DEPLOY_CONSTRUCTION_PIN",
            "build_carriers.py sha %s != pinned %s — refuse staging"
            % (builder_sha, PINS["build_carriers.py"]))
    # STAGE ONLY: guard remains the sole construction launcher. Add the
    # reviewed subset without changing the worker layout or launch above.
    for src in construction_files:
        dst = bundle / src.relative_to(REPO)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    manifest = {str(p.relative_to(bundle)): sha256_file(p)
                for p in sorted(bundle.rglob("*")) if p.is_file()}
    (bundle / "bundle-manifest.json").write_text(json.dumps(manifest,
                                                            indent=1))
    print("bundle: %d files; manifest sha %s"
          % (len(manifest),
             hashlib.sha256(json.dumps(manifest,
                                       sort_keys=True).encode())
             .hexdigest()[:16]))
    gcloud("compute", "scp", "--recurse", "--zone", ZONE,
           str(bundle), "%s:~/" % INSTANCE_NAME)
    # 3. launch the worker detached VIA THE LAUNCHER (FAILED-heartbeat
    #    wrapper) with the env contract [REV-B F4]
    launch = ("cd ~/f1k && setsid nohup env KOT_F1K_BUCKET='%s' "
              "COLIBRI_GIT_URL='%s' KOT_F1K_SPOT_RATE='%s' "
              "bash f1k_launch.sh > launcher.log 2>&1 & echo LAUNCHED-$!"
              % (os.environ["KOT_F1K_BUCKET"],
                 os.environ["COLIBRI_GIT_URL"],
                 os.environ["KOT_F1K_SPOT_RATE"]))
    gcloud("compute", "ssh", INSTANCE_NAME, "--zone", ZONE,
           "--command", launch)
    print("bringup-deploy DONE: RAID+mount, bundle pushed (manifest above), "
          "worker launched detached, guest max-life %d min armed. NOW start "
          "the box-side watchdog (docstring) and verify with pgrep."
          % max_life_min)


def cmd_watchdog() -> None:
    """Box-side teardown watchdog (plan v3 SS9 rule 1: long runs are driven
    by the box-side watchdog + the autonomous on-VM worker, NEVER an
    agent-held monitor). Parameterized promotion of the proven runner-10
    run-dir watchdog (8efa0f65). Polls every --poll-seconds; deletes the VM
    on (a) the --max-hours deadline or (b) a FAILED GCS heartbeat when
    KOT_F1K_BUCKET is set. Run it under nohup on the control box."""
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-hours", type=float, required=True)
    ap.add_argument("--poll-seconds", type=int, default=180)
    args = ap.parse_args(sys.argv[2:])
    deadline = time.time() + args.max_hours * 3600.0
    bucket = os.environ.get("KOT_F1K_BUCKET", "")
    while True:
        if not vm_exists():
            print("watchdog: VM %s gone; exiting clean." % INSTANCE_NAME)
            return
        failed_hb = False
        if bucket:
            r = subprocess.run(
                ["gsutil", "-q", "cat",
                 bucket + "/f1k/bringup/heartbeat.json"],
                capture_output=True, text=True)
            failed_hb = r.returncode == 0 and '"FAILED' in r.stdout
        if not failed_hb:
            # [REV-C, rereview finding 4 residual] SSH-side probe for the
            # launcher's LOCAL FAILED marker — covers the window where the
            # worker died but the GCS heartbeat upload could not land
            # (GCS/auth/network trouble). A probe FAILURE is INCONCLUSIVE
            # (VM booting/ssh flake), never a teardown trigger by itself;
            # a VM unreachable via BOTH GCS and SSH stays covered only by
            # the max-life backstop (stated residual).
            try:
                pr = gcloud("compute", "ssh", INSTANCE_NAME,
                            "--zone", ZONE, "--command",
                            "test -f ~/f1k/FAILED "
                            "&& echo KOT-F1K-FAILED-LOCAL; true",
                            check=False, capture=True)
                if pr.returncode == 0 and "KOT-F1K-FAILED-LOCAL" \
                        in pr.stdout:
                    failed_hb = True
                    print("watchdog: local FAILED marker seen via SSH "
                          "(GCS heartbeat absent/stale)")
            except Exception as ex:                        # noqa: BLE001
                print("watchdog: SSH probe inconclusive (%s)" % ex)
        if time.time() >= deadline or failed_hb:
            print("watchdog: %s -> teardown"
                  % ("FAILED heartbeat" if failed_hb else
                     "max-life deadline"))
            cmd_teardown()
            return
        time.sleep(args.poll_seconds)


def cmd_pin_fetch() -> None:
    """[REV-B F3, gate-fix review #4] Fetch + BYTE-VERIFY the licensed
    campaign pin and print the exact construction env exports — the
    construction command NEVER inherits ambient PIN/PIN_GB (the carrier
    builder would silently use whatever the environment happened to hold,
    build_carriers.py:634 lineage). Fail-closed at every step:
      - the gate artifact must be verdict GREEN, regime pinned-bringup;
      - the fetched GCS bytes must sha256-match pin.pin_file_sha256;
      - PIN_GB is echoed FROM THE ARTIFACT (the licensed value).
    usage: f1k_gcp.py pin-fetch --gate <bringup-gate.json> --out <dir>"""
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(sys.argv[2:])
    bucket = os.environ.get("KOT_F1K_BUCKET", "")
    if not bucket:
        die("F1K_PIN_FETCH", "KOT_F1K_BUCKET unset")
    art = json.loads(Path(args.gate).read_text(encoding="utf-8"))
    if art.get("schema") != "kot-f1k-bringup-gate/2":
        # [REV-C F5ii] literal (no gate-module import on the control box):
        # only the /2 model-bundle-bound artifact licenses construction.
        die("F1K_PIN_FETCH", "gate artifact schema %r != "
            "kot-f1k-bringup-gate/2 — refuse" % art.get("schema"))
    if art.get("verdict") != "GREEN":
        die("F1K_PIN_FETCH", "gate artifact verdict %r — only a GREEN "
            "license carries a construction pin" % art.get("verdict"))
    pin = art.get("pin") or {}
    if pin.get("regime") != "pinned-bringup" \
            or not pin.get("pin_file_sha256") or not pin.get("pin_gb"):
        die("F1K_PIN_FETCH", "gate artifact pin block incomplete/unpinned "
            "(%r) — shape (i) requires a bound sha + PIN_GB" % (pin,))
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    dest = outdir / "campaign-pin.stats"
    rc = subprocess.run(["gsutil", "-q", "cp",
                         bucket + "/f1k/bringup/campaign-pin.stats",
                         str(dest)])
    if rc.returncode != 0 or not dest.is_file():
        die("F1K_PIN_FETCH", "gsutil fetch of campaign-pin.stats failed")
    got = sha256_file(dest)
    if got != pin["pin_file_sha256"]:
        die("F1K_PIN_FETCH", "fetched pin sha %s != licensed %s — the "
            "persisted bytes are NOT the licensed pin; fail closed"
            % (got, pin["pin_file_sha256"]))
    # [REV-C] eval-safe split: exports alone on stdout (so
    # `eval "$(... pin-fetch ...)"` is exact), diagnostics on stderr.
    sys.stderr.write("campaign pin verified: %s (sha %s...)\n"
                     % (dest, got[:16]))
    print("export PIN=%s" % dest)
    print("export PIN_GB=%s" % pin["pin_gb"])


ENTRY = {
    "plan": cmd_plan, "provision": cmd_provision, "status": cmd_status,
    "teardown": cmd_teardown, "affordability": cmd_affordability,
    "gate": cmd_gate,
    "bringup-deploy": cmd_bringup_deploy, "watchdog": cmd_watchdog,
    "pin-fetch": cmd_pin_fetch,
}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in ENTRY:
        print("usage: f1k_gcp.py {%s}" % "|".join(ENTRY), file=sys.stderr)
        sys.exit(2)
    ENTRY[sys.argv[1]]()


if __name__ == "__main__":
    main()
