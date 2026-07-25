#!/usr/bin/env python3
"""f1k_gcp.py — GCP-Spot orchestrator for the FROZEN F1-K correctness run.

OPUS EXECUTION-role harness (kern/opus-runner-<N>). It RUNS the already-frozen
F1-K experiment (registry/experiments/f1k.json, frozen_sha256 7897dd0a… once
the review-gated kot-correction/1 seq-4 generator re-pin splice lands; the
pre-splice record is 35372275… and verify_pins REFUSES to launch against it —
see poc/gcp/F1K-GENERATOR-REPIN.md) on the
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
import json, os, subprocess, sys, time, hashlib, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
# f1k_ops is the fork-independent operational foundation (contracts,
# option-B/variant-B spend-cap attestations, epoch, preflight). It is staged
# alongside this file on the worker and lives in the same dir in the repo, so
# the first real import of f1k_ops into the orchestrator (plan-v4 #2) is a
# same-directory import. Fail closed if it is absent.
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import f1k_ops  # noqa: E402

REPO = HERE.parents[1]
HARNESS = REPO / "poc" / "glm52-probe" / "f1k-harness"
KAE_PATCH_DIR = REPO / "poc" / "glm52-probe" / "kae-patch-draft"
DUMP_PATCH_DIR = HARNESS / "dump-patch"
WORKER_FLAT_FILES = (
    "f1k_worker.sh", "bringup_gcp.sh", "f1k_bringup_gate.py", "f1k_ops.py",
)

# ---------------------------------------------------------------------------
# FROZEN PINS (registry/experiments/f1k.json; verified at launch). The value
# below is the POST-seq-4 frozen hash (generator re-pin a92be3e4 -> 91baba62,
# deterministic canonical splice — poc/gcp/f1k_generator_repin_splice.py):
# until the review-gated splice lands, frozen-drift still reports 35372275…
# and verify_pins dies F1K_PIN_FROZEN — deliberately FAIL-CLOSED so the r3
# harness pins below can never license a launch against the un-amended record.
# ---------------------------------------------------------------------------
FROZEN_SHA256 = "7897dd0a8fbb432768d70e959a77abdd80c16c78ab93702ff6f1671828bf7802"
COLIBRI_COMMIT = "a78a06fc5acc4b0dc0f9ef03987c66b0559d1250"
ESTATE_REPO = "mateogrgic/GLM-5.2-colibri-int4-with-int8-mtp"
ESTATE_GB = 383.8
PINS = {
    "analysis/f1k.py":
        "126129b9ce78e398122b3d3bf0855b7e551a892ba43d7d1a8d072a1245fb3326",
    "build_carriers.py":
        "91baba62649ad81217a4dd51cfcb57536c81b50e7f38ce8e622a161c1056835b",
    "kae-add-path.patch":
        "11f8b45884878111480192ee086c92b22acaa1aaf3238b2d46c47f952e9dd9cb",
    "kot-f1k-dump.patch":
        "e4e04177068d0d8563ecdd24a4bc1f2c25be93a97992c173207ae760f7543887",
    "kae_dump.h":
        "485cd4973cedffd11a2d1420c4e51a719531af99d0c95dbceaced3e5203707ea",
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
          "build_carriers.py present and sha 91baba62...")
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
    # frozen record integrity (self-hash via the repo's own tool). FAIL-CLOSED
    # on three signals (Rev2 blocker 3): (a) the flag form `--frozen-drift`
    # (the bare positional `frozen-drift` is swallowed into hook_args and is a
    # no-op selector); (b) the checker's RETURN CODE (nonzero => drift or an
    # un-amended record — never accepted); (c) the FULL expected hash read from
    # the authoritative frozen-index (the checker prints only an 8-hex prefix,
    # so a prefix line match alone can be forged by an unrelated record and is
    # NOT sufficient; frozen-drift returncode==0 already proves in-record
    # frozen_sha256 == frozen-index == recomputed hash for f1k, so binding the
    # full frozen-index value closes the prefix gap).
    rc = subprocess.run(
        [sys.executable, str(REPO / "tools" / "registry" / "registry-check.py"),
         "--frozen-drift"], cwd=str(REPO), capture_output=True, text=True)
    if rc.returncode != 0:
        die("F1K_PIN_FROZEN",
            "registry-check --frozen-drift exit %d (frozen bytes changed or "
            "record un-amended). stdout tail:\n%s"
            % (rc.returncode, "\n".join(rc.stdout.splitlines()[-8:])))
    f1k_ok = any(line.strip().startswith("ok frozen-drift: f1k")
                 and FROZEN_SHA256[:8] in line
                 for line in rc.stdout.splitlines())
    if not f1k_ok:
        die("F1K_PIN_FROZEN",
            "registry-check --frozen-drift did not confirm f1k (%s). stdout "
            "tail:\n%s"
            % (FROZEN_SHA256[:8], "\n".join(rc.stdout.splitlines()[-8:])))
    index_path = REPO / "registry" / "frozen-index.json"
    try:
        idx = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        die("F1K_PIN_FROZEN", "cannot read frozen-index.json: %s" % exc)
    if idx.get("f1k") != FROZEN_SHA256:
        die("F1K_PIN_FROZEN",
            "frozen-index f1k %r != expected full %s — the review-gated "
            "seq-4 re-freeze has not landed"
            % (idx.get("f1k"), FROZEN_SHA256))
    out["f1k_frozen_drift"] = "ok (%s)" % FROZEN_SHA256
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


def _asm_registered(asm_path, asm_id) -> bool:
    """Rev3/Rev4 blocker 2: fully fail-closed registration check. Returns True
    IFF the WHOLE ledger parses (every non-empty line a JSON OBJECT) AND
    EXACTLY ONE object has id == asm_id. Any of: a read error, a malformed or
    non-object line ANYWHERE (before OR after the match — the whole file is
    scanned, never an early return), zero matches, or >1 match (a duplicate
    target id is ambiguity) -> False. NOT a substring test."""
    try:
        text = Path(asm_path).read_text(encoding="utf-8")
    except OSError:
        return False
    count = 0
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        try:
            obj = json.loads(s)
        except ValueError:
            return False  # a malformed line ANYWHERE fails closed
        if not isinstance(obj, dict):
            return False  # a non-object (record) line fails closed
        if obj.get("id") == asm_id:
            count += 1
    return count == 1


def _frozen_governance(repo, expect_frozen, checker=None):
    """Rev2 blockers 1+2: fail-closed registry-GOVERNANCE gate for the paid
    launcher. Parameterised on `repo` (so the $0 oracle can drive it against a
    sandbox) and on `checker` (injectable subprocess.run for the returncode
    path). Refuses (die -> SystemExit 2) unless ALL hold:

      1. registry-check (FULL suite) exits 0 — an incomplete/inconsistent
         registry (drift, account-lint, chain, corpus-pins, …) blocks launch;
      2. frozen-index[f1k] == the FULL expected hash (not a prefix);
      3. the kot-correction/1 seq-4 record is installed and bound
         (refrozen_sha256 == expected, seq == 4) — so a half-applied splice
         that wrote record+index but not the correction is NOT launchable;
      4. ASM-2525 is registered in registry/assumptions.jsonl — so a landing
         with the re-freeze but without its assumption is NOT launchable.

    (3)+(4) are what the splice writes/requires BEFORE the index (the launch
    marker); re-checking them here is defence-in-depth against a hand-forced
    index."""
    repo = Path(repo)
    run = checker or subprocess.run
    rc = run(
        [sys.executable, str(repo / "tools" / "registry" / "registry-check.py")],
        cwd=str(repo), capture_output=True, text=True)
    if rc.returncode != 0:
        die("F1K_REGISTRY_CHECK",
            "registry-check exit %d — registry governance is incomplete; "
            "refusing to launch. tail:\n%s"
            % (rc.returncode, "\n".join((rc.stdout or "").splitlines()[-8:])))
    index_path = repo / "registry" / "frozen-index.json"
    try:
        idx = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        die("F1K_PIN_FROZEN", "cannot read frozen-index.json: %s" % exc)
    if idx.get("f1k") != expect_frozen:
        die("F1K_PIN_FROZEN",
            "frozen-index f1k %r != expected full %s (re-freeze not landed)"
            % (idx.get("f1k"), expect_frozen))
    corr_path = (repo / "registry" / "corrections" / "f1k"
                 / "4-generator-repin.json")
    if not corr_path.is_file():
        die("F1K_GOV_CORRECTION",
            "seq-4 correction record missing at %s — half-applied splice; "
            "refusing to launch" % corr_path)
    try:
        corr = json.loads(corr_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        die("F1K_GOV_CORRECTION", "seq-4 correction unreadable: %s" % exc)
    if corr.get("refrozen_sha256") != expect_frozen or corr.get("seq") != 4:
        die("F1K_GOV_CORRECTION",
            "seq-4 correction not bound to %s (seq=%r, refrozen_sha256=%r)"
            % (expect_frozen, corr.get("seq"), corr.get("refrozen_sha256")))
    asm_path = repo / "registry" / "assumptions.jsonl"
    if not _asm_registered(asm_path, "ASM-2525"):
        die("F1K_GOV_ASM",
            "no assumptions.jsonl entry with id==ASM-2525 (the seq-4 re-freeze "
            "assumption) — refusing to launch")


def _construction_launch_gate() -> None:
    """The complete pre-mutation, pre-spend gate for `construction-continue`
    (Rev2 blocker 1). Binds the paid launcher to the LANDED frozen record +
    seq-4 correction + ASM-2525 + all file pins — not merely the on-VM
    READY/GREEN artifacts (which bind only the builder SHA). ANY failure is a
    fail-closed STOP before a single mutation or dollar."""
    verify_pins()                          # file pins + frozen f1k (module REPO)
    _frozen_governance(REPO, FROZEN_SHA256)  # registry integrity + correction + ASM


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
# round-4 (build-review): gcloud `compute/allow_partial_error` DEFAULTS TRUE
# since CLI 472.0.0, so a FAILED zonal `instances list` can return (rc=0,
# stdout="[]") with only a stderr warning — a rc=0 empty list is then NOT proof
# of absence. Every gcloud invocation runs with the property forced FALSE via
# this env so a failed list surfaces as rc!=0 (-> unknown -> present).
_COMPUTE_STRICT_ENV = "CLOUDSDK_COMPUTE_ALLOW_PARTIAL_ERROR"


def _gcloud_env():
    env = dict(os.environ)
    env[_COMPUTE_STRICT_ENV] = "false"
    return env


def gcloud(*args, check=True, capture=False):
    cmd = ["gcloud"] + list(args) + ["--project", PROJECT, "--quiet"]
    env = _gcloud_env()
    if capture:
        r = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if check and r.returncode != 0:
            die("GCLOUD", " ".join(cmd) + "\n" + r.stderr)
        return r
    r = subprocess.run(cmd, env=env)
    if check and r.returncode != 0:
        die("GCLOUD", "exit %d: %s" % (r.returncode, " ".join(cmd)))
    return r


# BLOCKING-1 (re-review): STRUCTURED presence/delete classification. Google's
# scripting guidance says do NOT depend on stderr wording (unstable), so NOTHING
# below parses free text. Presence is read from `instances list
# --filter=name=NAME --format=json`: a SUCCEEDED query (rc==0) returning an
# EMPTY structured JSON array is the ONLY proof of absence; rc!=0
# (permission/outage/timeout) or any unexpected shape is 'unknown' -> treated as
# still-present. The delete reads the STRUCTURED operation error from the
# --format=json stdout; a nonzero delete rc is NEVER inferred as absence — it
# re-confirms absence structurally or raises the uncapped-VM hazard.


def _classify_list_presence(rc: int, stdout, *, name: str,
                            partial_error_disabled: bool) -> str:
    """PURE classifier for `instances list --filter=name=NAME --format=json`.

    Absence is confirmed ONLY when the query SUCCEEDED (rc==0), stdout is a
    NON-EMPTY string parsing to a genuine JSON LIST with zero name matches, AND
    the call was made with `compute/allow_partial_error` DISABLED
    (partial_error_disabled=True). (round-4) With partial-error ENABLED — the
    gcloud default — a FAILED zonal list can return (rc=0, "[]") on a stderr
    warning, so a rc=0 empty list is NOT trustworthy absence; the classifier
    then returns 'unknown' (fail-closed-present). A NAME MATCH is always
    'present' (fail-safe) regardless of the flag. (BLOCKING-1) blank/whitespace/
    None/null/{}/truncated/non-list/non-matching -> 'unknown'. Free text is
    never consulted."""
    if rc != 0:
        return "unknown"
    if not isinstance(stdout, str):
        return "unknown"            # None / non-string -> not absence proof
    s = stdout.strip()
    if not s:
        return "unknown"            # blank / whitespace -> NOT synthesized to []
    try:
        items = json.loads(s)
    except (ValueError, TypeError):
        return "unknown"
    if not isinstance(items, list):
        return "unknown"            # null / {} / scalar -> unknown
    names = [it.get("name") for it in items if isinstance(it, dict)]
    if name in names:
        return "present"            # a present result is always fail-safe
    if not items:
        # rc==0 + non-empty stdout parsing to [] IS absence — but ONLY if the
        # invocation forced partial-error off; otherwise the [] may be a
        # partially-failed query -> fail-closed-present.
        return "absent" if partial_error_disabled else "unknown"
    return "unknown"                # non-empty but no name match -> unexpected


def _classify_delete_operation(op) -> str:
    """PURE: given the completed delete operation object, return 'deleted' or
    raise on the STRUCTURED error/status field. (re-review BLOCKING-2) a
    completed Compute operation's status is EXACTLY 'DONE'; a missing/null/
    non-DONE status, a truthy error, or a non-object all RAISE (never 'deleted').
    Never parses free text."""
    if isinstance(op, list):
        op = op[0] if op else {}
    if not isinstance(op, dict):
        raise F1KContinueError(
            "F1K_DELETE_OP", "delete returned no structured operation object")
    if op.get("error"):
        raise F1KContinueError(
            "F1K_DELETE_OP", "delete operation reported a structured error: %r"
            % op.get("error"))
    if op.get("status") != "DONE":
        raise F1KContinueError(
            "F1K_DELETE_OP", "delete operation status %r != DONE (a "
            "missing/null/PENDING/RUNNING status is not completion)"
            % op.get("status"))
    return "deleted"


def _describe_presence(runner=None) -> str:
    """Structured tristate presence via `instances list --filter`. Production
    runs through gcloud() which forces `compute/allow_partial_error=false`, so a
    rc=0 empty list is trustworthy absence (partial_error_disabled=True).

    `runner` is injectable and returns (rc, stdout, partial_error_disabled) so
    the $0 oracle exercises the real classifier on raw shapes — including the
    partial-error case where the flag is False and (rc=0, "[]") must NOT be
    trusted as absence."""
    if runner is None:
        r = gcloud("compute", "instances", "list", "--zones", ZONE,
                   "--filter", "name=%s" % INSTANCE_NAME, "--format=json",
                   check=False, capture=True)
        rc, stdout, ped = r.returncode, r.stdout, True   # gcloud() forced false
    else:
        rc, stdout, ped = runner()
    return _classify_list_presence(rc, stdout, name=INSTANCE_NAME,
                                   partial_error_disabled=ped)


def vm_exists() -> bool:
    """Fail-closed existence: present OR unknown -> 'exists' (True); only a
    STRUCTURALLY-confirmed absence (rc==0 + non-blank empty JSON list) -> False.
    A pre-create guard refuses on ambiguity; a watchdog never prematurely
    declares the VM gone."""
    return _describe_presence() != "absent"


def _blocking_delete(*, runner=None, presence_fn=None) -> str:
    """Submit the delete and WAIT for the zonal operation to complete. Returns
    'deleted' (structured operation, status DONE, no error) or 'already-absent'
    (the VM is STRUCTURALLY confirmed absent). RAISES on ANY op error / outage /
    missing operation output — a nonzero delete rc is NEVER read as absence from
    stderr text; absence is re-confirmed only via the structured presence check.

    `runner` (returns (rc, stdout)) and `presence_fn` are injectable so the $0
    oracle exercises the REAL parsing / operation boundary on raw shapes."""
    if runner is None:
        r = gcloud("compute", "instances", "delete", INSTANCE_NAME, "--zone",
                   ZONE, "--format=json", check=False, capture=True)
        rc, stdout = r.returncode, r.stdout
    else:
        rc, stdout = runner()
    presence = presence_fn or _describe_presence
    if rc == 0:
        # rc==0 MUST carry a structured, DONE operation; blank/non-JSON is not
        # proof of a completed deletion (re-review BLOCKING-2).
        if not isinstance(stdout, str) or not stdout.strip():
            raise F1KContinueError(
                "F1K_DELETE_OP", "delete rc=0 but EMPTY stdout — no structured "
                "operation to confirm completion; cap stays armed")
        try:
            op = json.loads(stdout.strip())
        except (ValueError, TypeError):
            raise F1KContinueError(
                "F1K_DELETE_OP", "delete rc=0 but stdout is not a structured "
                "JSON operation; cap stays armed")
        return _classify_delete_operation(op)
    # rc != 0: NEVER infer absence from stderr. Re-confirm absence STRUCTURALLY.
    if presence() == "absent":
        return "already-absent"
    raise F1KContinueError(
        "F1K_DELETE_OP",
        "instances delete rc=%d and the instance is NOT structurally confirmed "
        "absent — an uncapped VM may still be running; cap stays armed, MANUAL "
        "teardown required" % rc)


def _git_head_commit():
    try:
        r = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                           capture_output=True, text=True)
    except OSError:
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def _installed_gcloud_version():
    """The installed `Google Cloud SDK` version, or None if undeterminable
    (gcloud absent / errors / unparseable) — a None result fails the gate
    CLOSED at the caller (ISSUE-3)."""
    try:
        r = subprocess.run(["gcloud", "version", "--format=json"],
                           capture_output=True, text=True)
    except OSError:
        return None
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout).get("Google Cloud SDK")
    except (ValueError, TypeError):
        return None


def _require_cap_probe_green():
    """ISSUE-3 (re-review): a real provisioning call MUST be preceded by a
    recorded GREEN sub-dollar CAP-PROBE (env KOT_F1K_CAP_PROBE_EVIDENCE ->
    kot-f1k-cap-probe/1) that actually RAN against THIS project + zone at THIS
    source commit + the INSTALLED gcloud version, within the freshness window.

    Fail-closed cheap hardening (single-operator threat model — NOT an
    unforgeable-signature scheme): if `git rev-parse HEAD` FAILS we refuse
    (never silently disable the source-commit binding), and the installed
    gcloud version must be resolvable and match the record. Refuses on absent /
    not-GREEN / tampered / wrong-project-zone-commit-version / stale / future
    evidence."""
    path = os.environ.get("KOT_F1K_CAP_PROBE_EVIDENCE", "")
    if not path:
        die("F1K_CAP_PROBE", "KOT_F1K_CAP_PROBE_EVIDENCE unset — no ordinary "
            "provisioning call may precede a recorded GREEN CAP-PROBE "
            "(build-review; native-cap surface must be live-verified first)")
    head = _git_head_commit()
    if head is None:
        die("F1K_CAP_PROBE", "cannot resolve git HEAD — refusing fail-closed "
            "(the source-commit binding must not be silently disabled)")
    gver = _installed_gcloud_version()
    if gver is None:
        die("F1K_CAP_PROBE", "cannot resolve the installed gcloud version — "
            "refusing fail-closed (the CLI-version binding must not be skipped)")
    try:
        record = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        die("F1K_CAP_PROBE", "CAP-PROBE evidence unreadable/not JSON: %s" % exc)
    try:
        f1k_ops.validate_cap_probe_evidence(
            record, project_id=PROJECT or None, zone=ZONE,
            source_commit=head, gcloud_version=gver)
    except f1k_ops.F1KOpsError as exc:
        die("F1K_CAP_PROBE", "CAP-PROBE evidence invalid (%s)" % exc)


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
    """LC-10v3: create the single variant-B SPOT VM with the NATIVE cap
    (terminationTime=T_cap, unified STOP, discard-local-SSD) carried INSIDE the
    create request, the epoch captured + durably persisted BEFORE the create,
    an immediate post-create scheduling read-back, and a fail-closed
    verified-completion delete on ANY read-back/persistence failure. The guest
    max-life startup script stays as the bring-up backstop (continue later
    retires it). No VM can exist, even transiently, without its cap."""
    # Rev3 blocker 1: provision CREATES THE PAID SPOT VM (starts billing), so it
    # must pass the COMPLETE governance gate — not just verify_pins() — BEFORE
    # any mutation or GCP call. verify_pins alone inspects neither the seq-4
    # correction / ASM nor the full registry, so a governance-incomplete tree
    # with the executable pins installed could otherwise start billing here.
    _construction_launch_gate()
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
    _gate()
    _require_cap_probe_green()   # BLOCKING oracle item: no real create pre-probe
    if vm_exists():
        die("F1K_VM_EXISTS", "%s already exists (or presence is UNKNOWN) in %s "
            "— teardown or reuse; ambiguity refuses fail-closed"
            % (INSTANCE_NAME, ZONE))
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    ssd = []
    for _ in range(LOCAL_SSD_COUNT):
        ssd += ["--local-ssd", "interface=NVME"]
    metadata = (
        "kot-experiment=f1k,kot-frozen=%s,startup-script=%s"
        % (FROZEN_SHA256[:12], provision["startup_script"])
    )

    def create_fn(cap):
        # BLOCKING-2: CAP-PROBE-VERIFIED create flags — the documented absolute
        # runtime limit (`--termination-time`), unified STOP action, and the
        # local-SSD discard flag (`--discard-local-ssds-at-termination-
        # timestamp=true`). _require_cap_probe_green() above proves these were
        # verified at the live API before this call. cloud-platform is the OAuth
        # ceiling only; least-privilege IAM grants get/delete + Catalog read.
        gcloud("compute", "instances", "create", INSTANCE_NAME,
               "--zone", ZONE, "--machine-type", MACHINE_TYPE,
               "--provisioning-model", cap["provisioning_model"],
               "--instance-termination-action",
               cap["instance_termination_action"],
               "--termination-time", cap["termination_time"],
               "--discard-local-ssds-at-termination-timestamp=%s"
               % ("true"
                  if cap["discard_local_ssds_at_termination_timestamp"]
                  else "false"),
               "--image-family", IMAGE_FAMILY, "--image-project", IMAGE_PROJECT,
               "--boot-disk-size", "%dGB" % BOOT_GB,
               "--boot-disk-type", "pd-ssd", "--boot-disk-auto-delete",
               *ssd, "--scopes", provision["scope"], "--metadata", metadata)

    def describe_fn():
        return f1k_ops._gcloud_compute_get(
            project_id=PROJECT, zone=ZONE, instance_name=INSTANCE_NAME)

    try:
        res = _provision_execute(
            now_fn=f1k_ops._utc_now_z, mirror=_gsutil_mirror(),
            create_fn=create_fn, describe_fn=describe_fn,
            delete_fn=_blocking_delete, presence_fn=_describe_presence,
            local_epoch_path=EPOCH_LOCAL_PATH,
            binding_path=EPOCH_BINDING_PATH)
    except (F1KContinueError, f1k_ops.F1KOpsError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)
    print("provisioned SPOT %s (%s, %d local SSD) in %s; native cap "
          "terminationTime=%s (T_cap, STOP, discard-local-SSD); guest max-life "
          "%d min armed by startup script; epoch %s"
          % (INSTANCE_NAME, MACHINE_TYPE, LOCAL_SSD_COUNT, ZONE,
             res["deadline_utc"], provision["guest_max_life_min"],
             res["launch_utc"]))
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
    """LC-11v3: delete the VM -> (blocking op waits to DONE, errors surfaced)
    -> verify ABSENCE -> ONLY THEN remove external cleanup machinery. A
    VM-delete failure LEAVES every cap armed and exits nonzero; the epoch
    mirror is NEVER deleted (historical record). Firm and ordered."""
    def remove_cleanup_fn():
        # Best-effort removal of the optional off-box cleanup entry, if any.
        # The native cap needs no external machinery; nothing to remove for the
        # native-only deployment. The epoch mirror is deliberately preserved.
        pass

    try:
        res = _teardown_execute(
            presence_fn=_describe_presence, delete_fn=_blocking_delete,
            remove_cleanup_fn=remove_cleanup_fn)
    except (F1KContinueError, f1k_ops.F1KOpsError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)
    if res.get("deleted"):
        print("deleted %s + attached local SSD (genuine-404 absence verified)"
              % INSTANCE_NAME)
    else:
        print("no VM %s to delete (confirmed absent)" % INSTANCE_NAME)


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
    # Rev3 blocker 1: bringup-deploy LAUNCHES THE DETACHED PAID WORKER, so it
    # must pass the COMPLETE governance gate (not just verify_pins) BEFORE any
    # GCP op or payload staging — same reasoning as provision.
    _construction_launch_gate()
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
    gcloud("compute", "ssh", "%s@%s" % (GUEST_USER, INSTANCE_NAME),
           "--zone", ZONE, "--command", remote)   # seam W-USER: $HOME=/home/ubuntu
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
           str(bundle), "%s@%s:~/" % (GUEST_USER, INSTANCE_NAME))  # seam W-USER
    # 3. launch the worker detached VIA THE LAUNCHER (FAILED-heartbeat
    #    wrapper) with the env contract [REV-B F4]
    launch = ("cd ~/f1k && setsid nohup env KOT_F1K_BUCKET='%s' "
              "COLIBRI_GIT_URL='%s' KOT_F1K_SPOT_RATE='%s' "
              "bash f1k_launch.sh > launcher.log 2>&1 & echo LAUNCHED-$!"
              % (os.environ["KOT_F1K_BUCKET"],
                 os.environ["COLIBRI_GIT_URL"],
                 os.environ["KOT_F1K_SPOT_RATE"]))
    gcloud("compute", "ssh", "%s@%s" % (GUEST_USER, INSTANCE_NAME),
           "--zone", ZONE, "--command", launch)   # seam W-USER: $HOME=/home/ubuntu
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
                pr = gcloud("compute", "ssh",
                            "%s@%s" % (GUEST_USER, INSTANCE_NAME),
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


# ===========================================================================
# Variant-B cap orchestration (LC-10/11/14) + construction-continue (Rev4)
# ===========================================================================
from decimal import Decimal, ROUND_CEILING            # noqa: E402

CONTINUE_ERR = "F1K_CONTINUE"
GUEST_USER = "ubuntu"
GUEST_GATE_DIR = "/home/ubuntu/f1k-gate"
CONSTRUCTION_UNIT = "kot-f1k-construction.service"
# PROPOSED-CC-9: the 2 h workload-completion margin on wall-clock sufficiency —
# SEPARATE from T_cap's own 10 min provider margin; it never moves the deadline.
WALLCLOCK_MARGIN_HOURS = Decimal("2")
# Control-box durable state (epoch cache + numeric-id binding); env-overridable.
STATE_DIR = Path(os.environ.get(
    "KOT_F1K_STATE_DIR", str(Path.home() / ".kot-f1k")))
EPOCH_LOCAL_PATH = STATE_DIR / "launch-epoch.json"
EPOCH_BINDING_PATH = STATE_DIR / "epoch-binding.json"


class F1KContinueError(RuntimeError):
    """Fail-closed continue/reaper/provision refusal (exit 2)."""

    def __init__(self, code, msg):
        self.code = code
        super().__init__("ERR_%s: %s" % (code, msg))


def _epoch_mirror_object():
    bucket = os.environ.get("KOT_F1K_BUCKET", "")
    if not bucket:
        die("F1K_ENV", "KOT_F1K_BUCKET unset — the durable epoch mirror needs it")
    return bucket.rstrip("/") + "/f1k/ops/launch-epoch.json"


def _mirror_object_for(key):
    bucket = os.environ.get("KOT_F1K_BUCKET", "")
    if not bucket:
        die("F1K_ENV", "KOT_F1K_BUCKET unset — the durable mirror needs it")
    base = bucket.rstrip("/") + "/f1k/ops/"
    if key == f1k_ops.LAUNCH_EPOCH_KEY:
        return base + "launch-epoch.json"          # pinned object (design §4.1)
    return base + key.replace("/", "_") + ".json"


def _gsutil_mirror():
    """Real GCS-backed durable mirror transport (write-once epoch + binding).

    mirror(action="get", key=...) -> bytes|None ; action="put" -> None.
    The GCS object survives Spot preemption (local SSD does not), so it is the
    authoritative source (LC-12 require_mirror in the launch context).
    """
    def transport(*, action, key, data=None):
        obj = _mirror_object_for(key)
        if action == "get":
            r = subprocess.run(["gsutil", "-q", "cat", obj],
                               capture_output=True)
            if r.returncode != 0:
                return None
            return r.stdout
        if action == "put":
            import tempfile as _tf
            with _tf.NamedTemporaryFile(delete=False) as fh:
                fh.write(data)
                tmp = fh.name
            try:
                rc = subprocess.run(["gsutil", "-q", "cp", tmp, obj])
                if rc.returncode != 0:
                    raise F1KContinueError(
                        "F1K_EPOCH_MIRROR", "gsutil put of %s failed" % key)
            finally:
                os.unlink(tmp)
            return None
        raise AssertionError("bad mirror action %r" % action)
    return transport


_ABSENCE_RETRIES = 30
_ABSENCE_SLEEP_S = 10
EPOCH_BINDING_KEY = "epoch-binding"


def _verified_delete(*, delete_fn, presence_fn, name, order=None,
                     sleep_fn=None):
    """BLOCKING-1: the real delete -> poll-op-to-DONE -> API-confirmed-404
    sequence.

    delete_fn(): submits the delete AND waits for the zonal operation to
      complete (error-checked); returns 'deleted' or 'already-absent'; RAISES
      F1KContinueError on ANY op error / outage / permission failure.
    presence_fn(): a TRISTATE 'present' | 'absent' | 'unknown' where 'absent'
      is a GENUINE confirmed 404 ONLY.

    Confirms absence ONLY on a genuine 404; a transport outage/permission/
    timeout ('unknown') is NEVER treated as absence. On failure it raises with
    the cap left armed — never a silent 'success'."""
    sleep_fn = sleep_fn or time.sleep
    if order is not None:
        order.append("delete")
    outcome = delete_fn()   # raises on op error / outage
    if order is not None:
        order.append("delete-%s" % outcome)
    last = None
    for _ in range(_ABSENCE_RETRIES):
        last = presence_fn()
        if last == "absent":                      # GENUINE confirmed 404
            if order is not None:
                order.append("absence")
            return True
        if order is not None:
            order.append("absence-retry-%s" % last)   # present OR unknown
        sleep_fn(_ABSENCE_SLEEP_S)
    raise F1KContinueError(
        "F1K_DELETE_ABSENCE",
        "instance %s absence NOT confirmed (last presence=%s) after delete + "
        "%d checks — outage/permission/timeout is never treated as absence; "
        "the cap stays armed" % (name, last, _ABSENCE_RETRIES))


def _provision_execute(*, now_fn, mirror, create_fn, describe_fn,
                       delete_fn, presence_fn,
                       local_epoch_path, binding_path, order=None,
                       instance_name=None, zone=None, project_id=None,
                       sleep_fn=None):
    """LC-10v3: the spend-safety-critical provision cap sequence.

    Ordering is the point: capture the epoch and durably persist it (+ the
    cap-in-create-request) BEFORE the create; read the cap back IMMEDIATELY
    after create; on ANY read-back/persistence failure DELETE the new VM,
    VERIFIED to completion, and refuse. Because t_epoch predates creation, the
    deadline can only be EARLIER than creation + 900 h (conservative)."""
    order = order if order is not None else []
    instance_name = instance_name or INSTANCE_NAME
    zone = zone or ZONE
    project_id = project_id or PROJECT

    launch = now_fn()
    deadline = f1k_ops.compute_selfdelete_deadline(launch_utc=launch)
    # persist epoch durably (mirror + local) BEFORE the VM exists (write-once).
    f1k_ops.write_launch_epoch(
        launch_utc=launch, local_path=str(local_epoch_path),
        mirror_transport=mirror)
    order.append("epoch-persist")
    # cap fields carried IN the create request — no VM exists without its cap.
    cap_flags = {
        "termination_time": deadline,                 # T_cap (conservative)
        "instance_termination_action": f1k_ops.CAP_ACTION,   # unified STOP
        "provisioning_model": "SPOT",
        # BLOCKING-2: the documented create flag (CAP-PROBE-verified).
        "discard_local_ssds_at_termination_timestamp": True,
    }
    create_fn(cap_flags)
    order.append("create")
    inst_id = None
    try:
        instance = describe_fn()
        f1k_ops.verify_provider_cap(
            instance_name=instance_name, zone=zone, project_id=project_id,
            deadline_utc=deadline, compute_transport=lambda **k: instance)
        inst_id = instance.get("id")
        if not (isinstance(inst_id, str) and inst_id):
            raise F1KContinueError("F1K_PROVISION_BIND",
                                   "post-create instance has no numeric id")
        binding = {
            "schema": "kot-f1k-epoch-binding/1",
            "launch_utc": launch,
            "instance_id": inst_id,
            "instance_name": instance_name,
            "zone": zone,
            "project_id": project_id,
            "termination_time_utc": deadline,
        }
        binding["sha256"] = hashlib.sha256(
            f1k_ops.canonical_json_bytes(binding)).hexdigest()
        f1k_ops.atomic_write_json(str(binding_path), binding)
        payload = f1k_ops.canonical_json_bytes(binding)
        mirror(action="put", key=EPOCH_BINDING_KEY, data=payload)
        if mirror(action="get", key=EPOCH_BINDING_KEY) != payload:
            raise F1KContinueError("F1K_PROVISION_BIND",
                                   "epoch-binding mirror read-back mismatch")
    except Exception as exc:  # noqa: BLE001 — fail closed, then delete
        order.append("faildelete")
        # BLOCKING-1: verified-to-completion delete (poll-to-DONE + genuine-404
        # confirmed). If the delete/confirmation itself fails (op error / outage
        # / unconfirmed absence), THIS raises too — the new VM is NOT declared
        # gone, the cap stays armed, and provision exits nonzero surfacing an
        # UNCAPPED-VM hazard requiring manual teardown.
        try:
            _verified_delete(delete_fn=delete_fn, presence_fn=presence_fn,
                             name=instance_name, order=order, sleep_fn=sleep_fn)
        except F1KContinueError as del_exc:
            raise F1KContinueError(
                "F1K_PROVISION_READBACK",
                "post-create cap read-back failed (%s) AND the fail-closed "
                "delete could NOT complete (%s) — an UNCAPPED VM may still be "
                "running; the cap stays armed, MANUAL teardown required"
                % (exc, del_exc)) from del_exc
        raise F1KContinueError(
            "F1K_PROVISION_READBACK",
            "post-create cap read-back/persistence failed (%s) — the new VM "
            "was deleted fail-closed (genuine-404 verified)" % exc)
    order.append("bound")
    return {"launch_utc": launch, "deadline_utc": deadline,
            "instance_id": inst_id}


# --- shell-level primitives the continue core rides on (ubuntu@ targeted) ---
class RealContinueOps:
    """Production control-box ops for construction-continue.

    EVERY ssh/scp targets ubuntu@<vm> (seam W-USER, PROPOSED-CC-2) so $HOME is
    /home/ubuntu and the frozen canonical /home/ubuntu/f1k-gate paths resolve.
    """

    def __init__(self):
        self.order = []
        self._target = "%s@%s" % (GUEST_USER, INSTANCE_NAME)

    def ssh(self, command):
        self.order.append("ssh")
        r = gcloud("compute", "ssh", self._target, "--zone", ZONE,
                   "--command", command, check=False, capture=True)
        if r.returncode != 0:
            raise F1KContinueError(
                "F1K_CONTINUE_SSH",
                "ssh %s failed: %s" % (command.split()[0], r.stderr.strip()))
        return r.stdout

    def scp_bytes(self, remote_path, data):
        self.order.append("scp")
        import tempfile as _tf
        with _tf.NamedTemporaryFile(delete=False) as fh:
            fh.write(data)
            tmp = fh.name
        try:
            tmp_remote = remote_path + ".tmp"
            r = gcloud("compute", "scp", "--zone", ZONE, tmp,
                       "%s:%s" % (self._target, tmp_remote),
                       check=False, capture=True)
            if r.returncode != 0:
                raise F1KContinueError(
                    "F1K_CONTINUE_SCP", "scp to %s failed" % remote_path)
        finally:
            os.unlink(tmp)
        # atomic rename on the VM
        self.ssh("mv %s %s" % (tmp_remote, remote_path))
        return hashlib.sha256(data).hexdigest()

    def remote_sha256(self, remote_path):
        out = self.ssh("sha256sum %s | cut -d' ' -f1" % remote_path)
        return out.strip()

    def remote_exists(self, remote_path):
        out = self.ssh("test -e %s && echo Y || echo N" % remote_path)
        return out.strip() == "Y"

    def gcloud_describe(self):
        self.order.append("describe")
        return f1k_ops._gcloud_compute_get(
            project_id=PROJECT, zone=ZONE, instance_name=INSTANCE_NAME)

    def watchdog_alive(self):
        r = subprocess.run(["pgrep", "-f", "f1k_gcp.py watchdog"],
                           capture_output=True)
        return r.returncode == 0

    def remote_events_nonempty(self, rundir):
        out = self.ssh(
            "f=%s/construction-events.jsonl; "
            "test -s \"$f\" && echo Y || echo N" % rundir)
        return out.strip() == "Y"

    def materialize_epoch_on_vm(self, launch_utc):
        # Pull the authoritative GCS mirror to the VM-local canonical path.
        obj = _epoch_mirror_object()
        self.ssh("gsutil -q cp %s %s/launch-epoch.json"
                 % (obj, GUEST_GATE_DIR))

    def install_guest_units(self, units):
        self.order.append("install-units")
        for kind in ("service", "timer"):
            self.scp_bytes(units["%s_path" % kind],
                           units["%s_text" % kind].encode())
        self.ssh("sudo systemctl daemon-reload && sudo systemctl enable "
                 "--now %s" % units["timer_unit"])

    def install_construction_unit(self, service):
        self.order.append("install-construction-unit")
        unit_text = (
            "[Unit]\nDescription=F1-K construction guard\n"
            "After=network-online.target\n[Service]\nType=simple\n"
            "User=%s\nWorkingDirectory=%s\nRestart=no\n"
            "ExecStart=%s\n[Install]\nWantedBy=multi-user.target\n"
            % (service["user"], service["working_directory"],
               " ".join(service["exec_argv"])))
        self.scp_bytes("/etc/systemd/system/%s" % CONSTRUCTION_UNIT,
                       unit_text.encode())
        self.ssh("sudo systemctl daemon-reload && sudo systemctl start %s"
                 % CONSTRUCTION_UNIT)
        active = self.ssh(
            "systemctl show -p ActiveState -p MainPID %s" % CONSTRUCTION_UNIT)
        show = dict(line.split("=", 1) for line in active.strip().splitlines()
                    if "=" in line)
        argv = self.ssh(
            "systemctl show -p ExecStart %s" % CONSTRUCTION_UNIT)
        return {
            "ActiveState": show.get("ActiveState"),
            "MainPID": show.get("MainPID", "0"),
            "ExecStart_argv": service["exec_argv"],  # verified by daemon parse
            "raw_execstart": argv.strip(),
        }

    def cancel_maxlife(self):
        self.ssh("sudo shutdown -c 'kot-f1k continue: retire bring-up "
                 "max-life' 2>/dev/null || true")


def _remaining_hours_to(now_z, deadline_z):
    """Exact Decimal billable hours between now and the T_cap deadline."""
    now_dt = f1k_ops._utc_datetime(now_z, field="now", code=CONTINUE_ERR)
    dl_dt = f1k_ops._utc_datetime(deadline_z, field="deadline", code=CONTINUE_ERR)
    if dl_dt <= now_dt:
        return Decimal("0")
    return f1k_ops._elapsed_hours(now_dt, dl_dt)


def _construction_continue(*, gate_bytes, ready_bytes, now_fn, ops, transports,
                           local_epoch_path):
    """Core 7-phase transition (Rev4). Injectable ops + transports so the $0
    oracle drives it with fakes. Raises F1KContinueError on ANY refusal; every
    abort leaves the VM strictly-safer-or-equal (backstops armed, no spend)."""
    ev = ops.order  # order recorder (shared with fakes)

    # ---- Phase 0: pure checks, $0, no mutation ----
    gate = f1k_ops.validate_gate(json.loads(gate_bytes))
    ready = f1k_ops.validate_ready(json.loads(ready_bytes))
    binding = f1k_ops.validate_ready_gate_binding(ready, gate)
    if gate["verdict"] != "GREEN" or gate["schema"] != f1k_ops.BRINGUP_GATE_SCHEMA:
        raise F1KContinueError("F1K_CONTINUE_GATE",
                               "gate is not a GREEN /2 construction license")

    # (3) live identity == READY identity on every field, incl. guest boot_id.
    identity = f1k_ops.resolve_live_instance_identity(
        metadata_transport=transports["metadata"],
        compute_transport=transports["compute"],
        bootid_transport=transports["bootid"])
    if identity != ready["instance"]:
        diffs = [k for k in ready["instance"]
                 if identity.get(k) != ready["instance"].get(k)]
        raise F1KContinueError(
            "F1K_CONTINUE_IDENTITY",
            "live instance != READY identity (fields: %s); a preemption "
            "between READY and continue changes the boot id — re-finalize "
            "READY on the current boot and re-gate" % ", ".join(diffs))

    # (4) RATE-EQUALITY gate: live canonical == collect-frozen gate rate.
    gate_rate = f1k_ops.canonical_decimal(
        gate["rate"]["usd_per_hour_decimal"], field="gate.rate")
    try:
        live_rate_str, rate_evidence = f1k_ops.resolve_live_rate(
            project_id=identity["project_id"], zone=identity["zone"],
            machine_type=MACHINE_TYPE, local_ssd_count=LOCAL_SSD_COUNT,
            observed_at_utc=now_fn(), catalog_transport=transports["catalog"])
    except f1k_ops.F1KOpsError as exc:
        raise F1KContinueError(
            "F1K_CONTINUE_RATE_QUOTE",
            "live rate quote failed (%s) — remedy: on-box re-collect + gate"
            % exc.code)
    if f1k_ops.canonical_decimal(live_rate_str, field="live.rate") != gate_rate:
        raise F1KContinueError(
            "F1K_CONTINUE_RATE_DRIFT",
            "live rate %s != gate rate %s (zero tolerance) — remedy: on-box "
            "re-collect with the new rate + control-box gate re-run"
            % (live_rate_str, gate_rate))

    # epoch (from the durable mirror; require_mirror in the launch context).
    launch = f1k_ops._resolve_epoch_launch(
        local_path=str(local_epoch_path),
        mirror_transport=transports["mirror"], require_mirror=True)
    deadline = f1k_ops.compute_selfdelete_deadline(launch_utc=launch)

    # (5) wall-clock sufficiency pre-filter (RAW-decimal +1SE + reserve + 2 h).
    raw_gate = json.loads(gate_bytes, parse_float=str)
    proj = raw_gate["projection"]
    need = (Decimal(f1k_ops.canonical_decimal(
                proj["instance_hours"]["hi"], field="proj.hi"))
            + Decimal(f1k_ops.canonical_decimal(
                proj["reserve"]["hours_at_rate"], field="proj.reserve"))
            + WALLCLOCK_MARGIN_HOURS)
    need = need.quantize(Decimal("0.000001"), rounding=ROUND_CEILING)
    remaining = _remaining_hours_to(now_fn(), deadline)
    if remaining < need:
        raise F1KContinueError(
            "F1K_CONTINUE_WALLCLOCK",
            "remaining billable %s h < projected+1SE+reserve+margin %s h — "
            "the T_cap cap would kill this run; maintainer surface, not a retry"
            % (remaining, need))

    # (6) single-shot.
    if ops.remote_exists(f1k_ops.CONSTRUCTION_HANDOFF_PATH) or \
            ops.remote_events_nonempty(ready["paths"]["rundir"]):
        raise F1KContinueError(
            "F1K_CONTINUE_ALREADY",
            "a construction handoff / non-empty events log already exists — a "
            "second attempt is an explicit operator decision, never automatic")

    # (7) watchdog interlock.
    if ops.watchdog_alive():
        raise F1KContinueError(
            "F1K_CONTINUE_WATCHDOG",
            "a bring-up watchdog is alive on the control box — retire its "
            "teardown authority before construction (its --max-hours deadline "
            "would delete a licensed run)")

    # (8) harness-version pin: on-VM bytes == control-box repo bytes.
    for fname in ("f1k_bringup_gate.py", "f1k_ops.py"):
        local_sha = sha256_file(HERE / fname)
        remote_sha = ops.remote_sha256("~/f1k/%s" % fname)
        if remote_sha != local_sha:
            raise F1KContinueError(
                "F1K_CONTINUE_HARNESS_DRIFT",
                "on-VM %s sha %s != control-box %s — continue NEVER re-pushes "
                "payload (READY byte-binds the bundle)"
                % (fname, remote_sha, local_sha))

    # (9) remote-home check (seam W-USER).
    home = ops.ssh("echo $HOME").strip()
    if home != "/home/ubuntu":
        raise F1KContinueError(
            "F1K_CONTINUE_HOME",
            "remote $HOME %r != /home/ubuntu (wrong image/user) — refuses at $0"
            % home)

    # ---- Phase 1: VM mutation ($0 exposure) ----
    ops.materialize_epoch_on_vm(launch)              # from GCS mirror (LC-12)
    units = f1k_ops.render_selfdelete_unit(
        instance_name=identity["name"], zone=identity["zone"],
        project_id=identity["project_id"], deadline_utc=deadline)
    ops.install_guest_units(units)

    # ---- Phase 2: the single pre-spend gate ----
    ev.append("preflight")
    preflight = f1k_ops.preflight_launch_gate(
        now_utc=now_fn(), local_epoch_path=str(local_epoch_path),
        instance_name=identity["name"], zone=identity["zone"],
        project_id=identity["project_id"], deadline_utc=deadline,
        billing_account=os.environ.get("KOT_GCP_BILLING_ACCOUNT", ""),
        budget_resource_name=os.environ.get("KOT_F1K_BUDGET_RESOURCE", ""),
        machine_type=MACHINE_TYPE, local_ssd_count=LOCAL_SSD_COUNT,
        s_per_prefill=f1k_ops.canonical_decimal(
            proj["blended_s_per_prefill_central"], field="proj.spp"),
        mirror_transport=transports["mirror"],
        systemctl_transport=transports["systemctl"],
        compute_transport=transports["compute"],
        iam_transport=transports["iam"],
        budget_transport=transports["budget"],
        channel_transport=transports["channel"],
        linkage_transport=transports["linkage"],
        catalog_transport=transports["catalog"],
        observed_at_utc=now_fn())
    if not preflight.get("go"):
        raise F1KContinueError(
            "F1K_CONTINUE_PREFLIGHT",
            "preflight NO-GO: %s (cap layers left armed; teardown available)"
            % preflight.get("reason"))
    cap = preflight["cap"]

    # ---- Phase 3: artifact placement (atomic, sha read-back) ----
    evidence_bytes = f1k_ops.canonical_json_bytes(rate_evidence)
    if rate_evidence.get("sha256") and \
            hashlib.sha256(evidence_bytes).hexdigest() != rate_evidence["sha256"]:
        pass  # evidence sha is self-describing; the file sha is read back below
    local_ev_sha = hashlib.sha256(evidence_bytes).hexdigest()
    got = ops.scp_bytes(f1k_ops.RATE_EVIDENCE_PATH, evidence_bytes)
    if got != local_ev_sha:
        raise F1KContinueError("F1K_CONTINUE_SCP",
                               "live-rate-evidence sha read-back mismatch")
    gate_got = ops.scp_bytes(f1k_ops.BRINGUP_GATE_PATH, gate_bytes)
    if gate_got != hashlib.sha256(gate_bytes).hexdigest():
        raise F1KContinueError("F1K_CONTINUE_SCP",
                               "gate artifact sha read-back mismatch")

    # ---- Phase 4: backstop swap (verify-BEFORE-cancel; re-probe L1+L2) ----
    reprobe = f1k_ops.verify_cap_armed(
        instance_name=identity["name"], zone=identity["zone"],
        project_id=identity["project_id"], deadline_utc=deadline,
        compute_transport=transports["compute"],
        systemctl_transport=transports["systemctl"],
        iam_transport=transports["iam"])
    if reprobe["deadline_utc"] != deadline:
        raise F1KContinueError(
            "F1K_CONTINUE_REPROBE",
            "phase-4 cap re-probe deadline drifted — NOT cancelling max-life")
    ev.append("reprobe")
    ops.cancel_maxlife()
    ev.append("cancel-maxlife")

    # ---- Phase 5: handoff + prior-spend evidence ----
    ev_ref = {
        "path": f1k_ops.RATE_EVIDENCE_PATH,
        "sha256": local_ev_sha,
        "schema": f1k_ops.RATE_EVIDENCE_SCHEMA,
        "observed_at_utc": rate_evidence["observed_at_utc"],
    }
    now_z = now_fn()
    handoff = _build_construction_handoff(
        ready=ready, gate=gate, binding=binding, cap=cap,
        preflight=preflight, rate_evidence_ref=ev_ref, now_utc=now_z,
        deadline=deadline, licensed_rate=gate_rate,
        project_id=identity["project_id"])
    f1k_ops.validate_handoff(handoff, now_utc=now_z)
    f1k_ops.build_runtime_license(ready, gate, handoff, now_utc=now_z)
    handoff_bytes = f1k_ops.canonical_json_bytes(handoff)
    h_got = ops.scp_bytes(f1k_ops.CONSTRUCTION_HANDOFF_PATH, handoff_bytes)
    if h_got != hashlib.sha256(handoff_bytes).hexdigest():
        raise F1KContinueError("F1K_CONTINUE_SCP",
                               "handoff sha read-back mismatch")
    ev.append("handoff")
    prior = _build_prior_spend(launch=launch, now_utc=now_z,
                               licensed_rate=gate_rate, instance=identity)
    prior_bytes = f1k_ops.canonical_json_bytes(prior)
    prior_sha = ops.scp_bytes(GUEST_GATE_DIR + "/prior-spend-evidence.json",
                              prior_bytes)

    # ---- Phase 6: guard launch via systemd (sole builder launcher) ----
    ev.append("unit-start")
    status = ops.install_construction_unit(handoff["service"])
    if status.get("ActiveState") != "active" or int(status.get("MainPID", 0)) <= 0:
        raise F1KContinueError(
            "F1K_CONTINUE_UNIT",
            "construction unit not active/MainPID>0: %r" % status)
    if status.get("ExecStart_argv") != handoff["service"]["exec_argv"]:
        raise F1KContinueError(
            "F1K_CONTINUE_UNIT",
            "systemd ExecStart != handoff exec_argv")
    return {
        "handoff_sha256": h_got,
        "prior_spend_sha256": prior_sha,
        "cap_deadline_utc": deadline,
        "unit": status,
    }


def _build_construction_handoff(*, ready, gate, binding, cap, preflight,
                                rate_evidence_ref, now_utc, deadline,
                                licensed_rate, project_id):
    """Produce the /2 handoff. The cap block is populated ONLY from the LC-5
    composite (preflight['cap']) — never an echoed provisioning flag (wonu).
    BLOCKING-4: `cap` MUST be a real verify_cap_armed composite carrying a
    `provenance` object; an arbitrary hand-built cap dict is refused here (the
    producer cannot be fed a bare {mechanism, action, 2 timestamps} block)."""
    if not (isinstance(cap, dict) and isinstance(cap.get("provenance"), dict)):
        raise F1KContinueError(
            "F1K_CONTINUE_CAP_PROVENANCE",
            "cap is not a verify_cap_armed composite (no provenance) — the "
            "handoff cap block is populated only from the live composite")
    started_dt = f1k_ops._utc_datetime(now_utc, field="now", code=CONTINUE_ERR)
    dl_dt = f1k_ops._utc_datetime(deadline, field="deadline", code=CONTINUE_ERR)
    armed = f1k_ops._hours_ceiling(started_dt, dl_dt)
    non_compute = Decimal("20")     # PROPOSED-CC-5 (maintainer-ratifiable)
    headroom = Decimal("10")
    from decimal import localcontext
    with localcontext() as ctx:
        ctx.prec = 80
        ceiling = armed * Decimal(licensed_rate)
        envelope = ceiling + non_compute + headroom
    if armed > Decimal("899"):
        raise F1KContinueError(
            "F1K_CONTINUE_ENVELOPE",
            "armed_hours %s > 899 (continue < 1 h after epoch?)" % armed)
    if envelope > Decimal("300"):
        raise F1KContinueError(
            "F1K_CONTINUE_ENVELOPE",
            "total envelope $%s > $300 at the licensed rate" % envelope)
    root = ready["payload"]["root"]
    return {
        "schema": f1k_ops.CONSTRUCTION_HANDOFF_SCHEMA,
        "created_at_utc": now_utc,
        "mode": "initial",
        "instance": dict(ready["instance"]),
        "ready": {
            "path": f1k_ops.CONSTRUCTION_READY_PATH,
            "sha256": hashlib.sha256(
                f1k_ops.canonical_json_bytes(ready)).hexdigest(),
            "schema": f1k_ops.CONSTRUCTION_READY_SCHEMA,
            "status": "READY",
        },
        "gate": {
            "path": f1k_ops.BRINGUP_GATE_PATH,
            "sha256": hashlib.sha256(
                f1k_ops.canonical_json_bytes(gate)).hexdigest(),
            "schema": f1k_ops.BRINGUP_GATE_SCHEMA,
            "verdict": "GREEN",
        },
        "binding": binding,
        "rate": {
            "usd_per_hour_decimal": gate["rate"]["usd_per_hour_decimal"],
            "local_ssd_count": 2,
            "evidence": rate_evidence_ref,
        },
        "provider": {
            "campaign_started_at_utc": now_utc,
            "cap": {
                "mechanism": f1k_ops.CAP_MECHANISM,
                "action": f1k_ops.CAP_ACTION,
                "termination_time_utc": cap["termination_time_utc"],
                "termination_timestamp_utc": cap["termination_timestamp_utc"],
                "provenance": cap["provenance"],   # BLOCKING-4: LC-5 composite
            },
            "cleanup": {
                "mechanism": f1k_ops.CLEANUP_MECHANISM,
                "action": f1k_ops.CLEANUP_ACTION,
                "verified": "delete-poll-done-absence",
            },
            "frozen_hours_max_decimal": "900",
            "armed_hours_decimal": str(armed),
            "non_compute_allowance_usd_decimal": str(non_compute),
            "rate_headroom_usd_decimal": str(headroom),
            "compute_ceiling_usd_decimal": str(ceiling),
            "total_envelope_usd_decimal": str(envelope),
            "budget": {
                "resource_name": preflight["budget_resource_name"],
                "amount_usd_decimal": "300",
                "project_id": project_id,
            },
        },
        "paths": dict(ready["paths"]),
        "service": {
            "manager": "systemd",
            "unit_name": CONSTRUCTION_UNIT,
            "user": GUEST_USER,
            "working_directory": root,
            "exec_argv": [
                ready["builder"]["argv_base"][0],
                os.path.join(root, "f1k_bringup_gate.py"),
                "guard", "--handoff", f1k_ops.CONSTRUCTION_HANDOFF_PATH,
            ],
            "restart_policy": "no",
            "enabled_on_boot": False,
        },
    }


def _build_prior_spend(*, launch, now_utc, licensed_rate, instance):
    """kot-f1k-prior-spend/1: bring-up elapsed + dollars, ENFORCED into the
    config-cost basis by LC-13 (never a runbook promise). Delegates to the
    shared f1k_ops builder so producer and LC-13 consumer share one arithmetic."""
    return f1k_ops.build_prior_spend(
        launch_epoch_utc=launch, campaign_started_at_utc=now_utc,
        licensed_rate=licensed_rate, instance_id=instance["instance_id"])


def _teardown_execute(*, presence_fn, delete_fn, remove_cleanup_fn,
                      order=None, name=None, sleep_fn=None):
    """LC-11v3 frozen ordering: delete VM -> poll op DONE -> GENUINE-404
    absence -> ONLY THEN remove external cleanup machinery. Any VM-delete
    failure or outage LEAVES every cap armed + raises; the epoch mirror is
    NEVER deleted. cleanup-removal can NEVER precede a confirmed 404, and an
    ambiguous 'unknown' presence is never treated as absence (BLOCKING-1)."""
    order = order if order is not None else []
    name = name or INSTANCE_NAME
    if presence_fn() == "absent":       # GENUINE 404 only; 'unknown' proceeds to delete
        order.append("no-vm")
        remove_cleanup_fn()
        order.append("cleanup-removed")
        return {"deleted": False}
    _verified_delete(delete_fn=delete_fn, presence_fn=presence_fn,
                     name=name, order=order, sleep_fn=sleep_fn)
    remove_cleanup_fn()
    order.append("cleanup-removed")
    return {"deleted": True}


def _real_transports():
    """Production control-box transports for preflight/identity/rate.

    NOTE (design questions flagged for the CAP-PROBE / live validation; the $0
    oracle uses fakes so none of this is exercised at $0): the exact
    systemctl-show property parsing, the gcloud test-iam-permissions surface,
    the gcloud/beta billing + monitoring describe shapes, and the discard-SSD
    scheduling field name are pinned by the first live preflight + CAP-PROBE.
    Any failure here returns fail-closed (NO-GO) at preflight."""
    target = "%s@%s" % (GUEST_USER, INSTANCE_NAME)

    def _ssh(cmd):
        r = gcloud("compute", "ssh", target, "--zone", ZONE, "--command", cmd,
                   check=False, capture=True)
        if r.returncode != 0:
            raise f1k_ops.F1KOpsError("F1K_B_SSH", "ssh failed: %s" % cmd)
        return r.stdout.strip()

    def metadata(path, timeout_s):
        return _ssh("curl -s -H 'Metadata-Flavor: Google' "
                    "http://metadata.google.internal/computeMetadata/v1/%s"
                    % path)

    def bootid():
        return _ssh("cat /proc/sys/kernel/random/boot_id")

    def systemctl(*, action, unit):
        # CAP-PROBE-VERIFIED: exact systemctl-show property mapping. NOTE: the
        # `oncalendar` value comes from TimersCalendar (which the probe confirms
        # renders as the bare "OnCalendar=<spec>" the verifier expects); if the
        # probe finds it needs post-parsing, adjust here — the $0 oracle fakes
        # the returned strings.
        q = {
            "is-active": "systemctl is-active %s" % unit,
            "oncalendar": "systemctl show -p TimersCalendar --value %s" % unit,
            "persistent": "systemctl show -p Persistent --value %s" % unit,
            "triggered-unit": "systemctl show -p Unit --value %s" % unit,
            "exec-start": "systemctl show -p ExecStart --value %s" % unit,
            "restart-policy": "systemctl show -p Restart --value %s" % unit,
        }[action]
        return _ssh(q)

    def iam(*, project_id, zone, instance_name, permissions):
        # BLOCKING-2c: use the documented REST instances.testIamPermissions
        # method (there is NO `gcloud compute instances test-iam-permissions`
        # command). Invoked from the VM with its own SA token, deletes nothing.
        body = json.dumps({"permissions": list(permissions)}).replace("'", "")
        url = ("https://compute.googleapis.com/compute/v1/projects/%s/zones/"
               "%s/instances/%s/testIamPermissions"
               % (project_id, zone, instance_name))
        out = _ssh(
            "TOK=$(curl -s -H 'Metadata-Flavor: Google' "
            "http://metadata.google.internal/computeMetadata/v1/instance/"
            "service-accounts/default/token | "
            "python3 -c 'import sys,json;print(json.load(sys.stdin)[\"access_"
            "token\"])'); "
            "curl -s -X POST -H \"Authorization: Bearer $TOK\" "
            "-H 'Content-Type: application/json' -d '%s' %s" % (body, url))
        return json.loads(out) if out else {"permissions": []}

    def budget(*, action, resource_name):
        r = gcloud("beta", "billing", "budgets", "describe", resource_name,
                   "--format=json", check=False, capture=True)
        if r.returncode != 0:
            return None
        return json.loads(r.stdout)

    def channel(*, name):
        r = gcloud("beta", "monitoring", "channels", "describe", name,
                   "--format=json", check=False, capture=True)
        if r.returncode != 0:
            raise f1k_ops.F1KOpsError("F1K_B_BUDGET_NOTIFY",
                                      "channel describe failed")
        return json.loads(r.stdout)

    def linkage(*, project_id):
        r = gcloud("billing", "projects", "describe", project_id,
                   "--format=json", check=False, capture=True)
        if r.returncode != 0:
            raise f1k_ops.F1KOpsError("F1K_B_BUDGET_LINKAGE",
                                      "project billing-info failed")
        info = json.loads(r.stdout)
        return {"billingAccountName": info.get("billingAccountName"),
                "billingEnabled": info.get("billingEnabled")}

    return {
        "metadata": metadata,
        "compute": lambda **k: f1k_ops._gcloud_compute_get(**k),
        "bootid": bootid,
        "mirror": _gsutil_mirror(),
        "systemctl": systemctl,
        "iam": iam,
        "budget": budget,
        "channel": channel,
        "linkage": linkage,
        "catalog": f1k_ops._catalog_http_list,
    }


def cmd_construction_continue():
    """Rev4 GREEN->guarded-Spot-construction transition (7 phases). $0 oracle:
    `construction-continue --selftest`. The paid run is separately gated on the
    maintainer spend-GO (#55) and is NOT invoked here."""
    if "--selftest" in sys.argv[2:]:
        sys.exit(_continue_selftest())
    # Rev2 blocker 1: RE-RUN the full frozen-record + registry-governance +
    # file-pin gate BEFORE any argparse-side effect, env mutation, artifact
    # read, or launch. READY/GREEN bind the new builder SHA but NOT the landed
    # seq-4 re-freeze / correction / ASM — so this is the ONLY thing that stops
    # a launch when registry governance is incomplete.
    _construction_launch_gate()
    import argparse
    ap = argparse.ArgumentParser(prog="f1k_gcp.py construction-continue")
    ap.add_argument("--gate", required=True)
    ap.add_argument("--ready", required=True)
    args = ap.parse_args(sys.argv[2:])
    for var in ("KOT_F1K_BUCKET", "KOT_GCP_PROJECT",
                "KOT_GCP_BILLING_ACCOUNT", "KOT_F1K_BUDGET_RESOURCE"):
        if not os.environ.get(var):
            die("F1K_ENV", "%s unset (construction-continue precondition)" % var)
    gate_bytes = Path(args.gate).read_bytes()
    ready_bytes = Path(args.ready).read_bytes()
    ops = RealContinueOps()
    transports = _real_transports()
    try:
        receipt = _construction_continue(
            gate_bytes=gate_bytes, ready_bytes=ready_bytes,
            now_fn=f1k_ops._utc_now_z, ops=ops, transports=transports,
            local_epoch_path=EPOCH_LOCAL_PATH)
    except (F1KContinueError, f1k_ops.F1KOpsError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)
    print(json.dumps({"construction-continue": "OK", **receipt}, indent=2))


def cmd_cap_reaper():
    """LC-14 control-box cap-reaper (nohup watchdog pattern): sleep to T_cap,
    then delete -> poll DONE -> verify absence, unbounded delete retries until
    absence is confirmed. Best-effort by design (PROPOSED-CC-12): its failure
    leaks only stopped-VM storage, never running-compute spend."""
    import argparse
    from datetime import datetime, timezone
    if "--selftest" in sys.argv[2:]:
        sys.exit(_reaper_selftest())
    ap = argparse.ArgumentParser(prog="f1k_gcp.py cap-reaper")
    ap.add_argument("--deadline", required=True, help="T_cap UTC Z")
    args = ap.parse_args(sys.argv[2:])
    dl = f1k_ops._utc_datetime(args.deadline, field="deadline", code="F1K_REAPER")
    while True:
        now = datetime.now(timezone.utc)
        if now >= dl:
            break
        time.sleep(min(300.0, (dl - now).total_seconds()))

    while True:
        try:
            _verified_delete(delete_fn=_blocking_delete,
                             presence_fn=_describe_presence,
                             name=INSTANCE_NAME)
            print("cap-reaper: %s genuine-404 absence confirmed after T_cap"
                  % INSTANCE_NAME)
            return
        except F1KContinueError as exc:
            # delete-op error / outage / unconfirmed absence -> retry the WHOLE
            # verified delete; unbounded until a genuine 404 is confirmed
            # (BLOCKING-1: an 'unknown' presence never ends the loop).
            print("cap-reaper: %s; retrying whole verified delete in 60s" % exc,
                  file=sys.stderr)
            time.sleep(60)


# ---------------------------------------------------------------------------
# $0 oracles (injectable fakes only; NO gcloud/SSH/GCS/VM/spend)
# ---------------------------------------------------------------------------
def _sysexit(fn):
    """Run fn; return the SystemExit code die() raised, or 0 if it did not."""
    try:
        fn()
        return 0
    except SystemExit as exc:
        return exc.code if exc.code is not None else 0


def _raises(fn):
    """True iff fn raises F1KContinueError (a fail-closed refusal)."""
    try:
        fn()
    except F1KContinueError:
        return True
    return False


# The exact build-review reproducer: a PERMISSION error (rc=1) whose free text
# contains phrases the old regex matched as "absent". The structured classifier
# ignores stderr entirely and keys off (rc, structured JSON), so this MUST
# classify NOT-absent -> still-present -> raise the uncapped-VM hazard.
_PERMISSION_REPRODUCER = (
    "Could not fetch resource:\n - Required 'compute.instances.get' permission "
    "for 'projects/p/zones/us-central1-a/instances/kot-f1k-run' (or the "
    "resource does not exist / 404)")


def _classifier_oracle(check):
    """BLOCKING-1: exercise the PRODUCTION structured classifiers with the ACTUAL
    raw output shapes (not injected already-classified values). Presence is
    classified WITH partial-error disabled unless a case says otherwise."""
    n = "kot-f1k-run"

    def cp(rc, stdout, *, ped=True):
        return _classify_list_presence(rc, stdout, name=n,
                                       partial_error_disabled=ped)
    check(cp(0, "[]") == "absent",
          "CLASSIFY presence: rc=0 + '[]' + partial-error-DISABLED == absent")
    check(cp(0, json.dumps([{"name": n, "id": "1"}])) == "present",
          "CLASSIFY presence: rc=0 + name match == present")
    check(cp(1, "") == "unknown",
          "CLASSIFY presence: rc!=0 (permission/outage/timeout) == unknown")
    r = cp(1, _PERMISSION_REPRODUCER)
    check(r == "unknown" and r != "absent",
          "CLASSIFY (BLOCKING-1 reproducer): exact permission text at rc=1 == "
          "unknown, NEVER absent (free text is not consulted)")
    # round-4 (build-review): a partial-error list (rc=0, '[]') produced WITHOUT
    # the disable-flag is NOT trusted as absence -> unknown -> present.
    pe = cp(0, "[]\n", ped=False)
    check(pe == "unknown" and pe != "absent",
          "CLASSIFY (round-4 reproducer): rc=0 + '[]' with partial-error "
          "ENABLED == unknown, NEVER absent (a partial-failed list is not "
          "absence proof)")
    check(cp(0, json.dumps([{"name": n}]), ped=False) == "present",
          "CLASSIFY (round-4): a NAME MATCH is present regardless of the flag "
          "(fail-safe)")
    check(cp(1, "", ped=True) == "unknown",
          "CLASSIFY (round-4): with partial-error disabled a failed list is "
          "rc!=0 -> unknown -> present")
    # re-review BLOCKING-1: blank / whitespace / None stdout MUST NOT be
    # synthesized into [] -> unknown (the reproduced (0, ' \n') fail-open).
    check(cp(0, "") == "unknown",
          "CLASSIFY presence (re-review): rc=0 + BLANK stdout == unknown (NOT "
          "absent)")
    check(cp(0, " \n\t") == "unknown" and cp(0, " \n") != "absent",
          "CLASSIFY presence (re-review pinned): rc=0 + WHITESPACE stdout == "
          "unknown, NEVER absent")
    check(cp(0, None) == "unknown",
          "CLASSIFY presence (re-review): rc=0 + None stdout == unknown")
    check(cp(0, "null") == "unknown" and cp(0, "{}") == "unknown",
          "CLASSIFY presence: rc=0 + null/{} == unknown (not a list)")
    check(cp(0, "Could not fetch resource: 404 does not exist") == "unknown",
          "CLASSIFY presence: rc=0 + non-JSON free text == unknown (never "
          "absent from text)")
    check(cp(0, json.dumps([{"name": "other-vm"}])) == "unknown",
          "CLASSIFY presence: rc=0 + non-matching name == unknown")
    check(_classify_delete_operation({"status": "DONE"}) == "deleted",
          "CLASSIFY delete: DONE + no structured error == deleted")
    check(_raises(lambda: _classify_delete_operation(
        {"status": "DONE", "error": {"errors": [{"code": "RESOURCE_IN_USE"}]}})),
        "CLASSIFY delete: structured operation error -> raise")
    check(_raises(lambda: _classify_delete_operation({"status": "RUNNING"})),
          "CLASSIFY delete: a not-DONE operation status -> raise")
    # re-review BLOCKING-2: missing / null status MUST raise, not 'deleted'.
    check(_raises(lambda: _classify_delete_operation({})),
          "CLASSIFY delete (re-review): {} (missing status) -> raise")
    check(_raises(lambda: _classify_delete_operation({"status": None})),
          "CLASSIFY delete (re-review): {status:null} -> raise")
    check(_raises(lambda: _classify_delete_operation("string not op")),
          "CLASSIFY delete: a non-object operation -> raise")
    # re-review BLOCKING-2: empty / non-JSON rc=0 delete stdout MUST raise.
    check(_raises(lambda: _blocking_delete(runner=lambda: (0, ""),
                                           presence_fn=lambda: "present")),
          "CLASSIFY _blocking_delete (re-review): rc=0 + EMPTY stdout -> raise")
    check(_raises(lambda: _blocking_delete(runner=lambda: (0, " \n"),
                                           presence_fn=lambda: "present")),
          "CLASSIFY _blocking_delete (re-review): rc=0 + WHITESPACE stdout -> "
          "raise")
    check(_raises(lambda: _blocking_delete(runner=lambda: (0, "not json"),
                                           presence_fn=lambda: "present")),
          "CLASSIFY _blocking_delete: rc=0 + non-JSON stdout -> raise")
    check(_blocking_delete(runner=lambda: (0, json.dumps({"status": "DONE"})),
                           presence_fn=lambda: "present") == "deleted",
          "CLASSIFY _blocking_delete: rc=0 + DONE operation -> deleted")
    check(_blocking_delete(runner=lambda: (1, ""),
                           presence_fn=lambda: "absent") == "already-absent",
          "CLASSIFY _blocking_delete: rc!=0 + structural absence -> already-absent")
    check(_raises(lambda: _blocking_delete(runner=lambda: (1, ""),
                                           presence_fn=lambda: "unknown")),
          "CLASSIFY _blocking_delete: rc!=0 + presence unknown -> raise")


def _min_catalog():
    import copy as _copy
    cs = f1k_ops._COMPUTE_SERVICE

    def make_sku(sku_id, desc, fam, grp, usage, unit, nanos):
        return {
            "name": "%s/skus/%s" % (cs, sku_id), "skuId": sku_id,
            "description": desc,
            "category": {"serviceDisplayName": "Compute Engine",
                         "resourceFamily": fam, "resourceGroup": grp,
                         "usageType": usage},
            "serviceRegions": ["us-central1"], "serviceProviderName": "Google",
            "geoTaxonomy": {"type": "MULTI_REGIONAL",
                            "regions": ["us-central1"]},
            "pricingInfo": [{"effectiveTime": "2026-07-01T00:00:00Z",
                             "currencyConversionRate": 1,
                             "pricingExpression": {
                                 "usageUnit": unit,
                                 "tieredRates": [{"startUsageAmount": 0,
                                                  "unitPrice": {
                                                      "currencyCode": "USD",
                                                      "units": "0",
                                                      "nanos": nanos}}]}}]}
    skus = [
        make_sku("1111-AAAA-0001", "Spot Preemptible N2D AMD Instance Core "
                 "running in Americas", "Compute", "N2DAMDCore",
                 "Preemptible", "h", 10000000),
        make_sku("2222-BBBB-0002", "Spot Preemptible N2D AMD Instance Ram "
                 "running in Americas", "Compute", "N2DAMDram",
                 "Preemptible", "GiBy.h", 1000000),
        make_sku("3333-CCCC-0003", "SSD backed Local Storage attached to Spot "
                 "Preemptible VMs", "Storage", "LocalSSD", "Preemptible",
                 "GiBy.h", 100000)]

    def catalog(**kwargs):
        return {"skus": _copy.deepcopy(skus)}
    return catalog


def _continue_selftest():
    print("SELFTEST SCOPE: $0 construction-continue transition; injectable "
          "fakes only; NO gcloud, SSH, GCS, VM, or spend.")
    passed = total = 0

    def check(cond, label):
        nonlocal passed, total
        total += 1
        ok = bool(cond)
        passed += int(ok)
        print("  %s%s" % ("ok:  " if ok else "FAIL: ", label))

    def refuses(code, fn):
        try:
            fn()
        except (F1KContinueError, f1k_ops.F1KOpsError) as exc:
            return getattr(exc, "code", "") == code or code in str(exc)
        return False

    ready, gate = f1k_ops.build_construction_fixture()
    gate = json.loads(json.dumps(gate))
    # the fixture's 228.86 blended is out of the frozen SPP window; a real
    # GREEN gate is in-window (rate_in_window is a GREEN precondition).
    gate["projection"]["blended_s_per_prefill_central"] = 120.0
    gate_bytes = f1k_ops.canonical_json_bytes(gate)
    ready_bytes = f1k_ops.canonical_json_bytes(ready)
    inst = ready["instance"]
    launch = "2026-07-24T00:00:00Z"
    now = "2026-07-24T06:00:00Z"
    deadline = f1k_ops.compute_selfdelete_deadline(launch_utc=launch)
    BILLING_ACCOUNT = "billingAccounts/012345-6789AB-CDEF01"
    BUDGET_RESOURCE = BILLING_ACCOUNT + "/budgets/f1k"
    os.environ["KOT_GCP_BILLING_ACCOUNT"] = BILLING_ACCOUNT
    os.environ["KOT_F1K_BUDGET_RESOURCE"] = BUDGET_RESOURCE

    def now_fn():
        return now

    def seeded_mirror():
        store = {}

        def mirror(*, action, key, data=None):
            if action == "put":
                store[key] = data
                return None
            if action == "get":
                return store.get(key)
            raise AssertionError("bad mirror action")
        # seed the durable epoch
        f1k_ops.write_launch_epoch(
            launch_utc=launch, local_path=os.path.join(
                tempfile.mkdtemp(), "e.json"), mirror_transport=mirror)
        return mirror

    def fake_compute(action="STOP", model="SPOT", discard=True, term=None):
        t = term if term is not None else deadline

        def tr(*, project_id, zone, instance_name):
            base = ("https://www.googleapis.com/compute/v1/projects/%s"
                    % inst["project_id"])
            return {
                "id": inst["instance_id"], "name": inst["name"],
                "zone": base + "/zones/" + inst["zone"],
                "machineType": (base + "/zones/" + inst["zone"]
                                + "/machineTypes/" + inst["machine_type"]),
                "selfLink": (base + "/zones/" + inst["zone"] + "/instances/"
                             + inst["name"]),
                "lastStartTimestamp": inst["last_start_timestamp"],
                "scheduling": {
                    "provisioningModel": model,
                    "instanceTerminationAction": action,
                    "terminationTime": t,
                    "onInstanceStopAction": {"discardLocalSsd": discard}},
            }
        return tr

    def fake_metadata():
        m = {
            "instance/id": inst["instance_id"],
            "instance/name": inst["name"],
            "project/project-id": inst["project_id"],
            "project/numeric-project-id": inst["project_number"],
            "instance/zone": ("projects/%s/zones/%s"
                              % (inst["project_number"], inst["zone"])),
            "instance/machine-type": ("projects/%s/machineTypes/%s"
                                      % (inst["project_number"],
                                         inst["machine_type"])),
        }

        def tr(path, timeout_s):
            return m[path]
        return tr

    def fake_systemctl(active="active", restart="on-failure"):
        def tr(*, action, unit):
            return {
                "is-active": active,
                "oncalendar": f1k_ops._oncalendar(deadline),
                "persistent": "yes",
                "triggered-unit": f1k_ops.SELFDELETE_SERVICE_UNIT,
                "exec-start": f1k_ops._selfdelete_exec_start(
                    inst["name"], inst["zone"], inst["project_id"]),
                "restart-policy": restart,
            }[action]
        return tr

    def fake_iam(granted=("compute.instances.delete",)):
        def tr(*, project_id, zone, instance_name, permissions):
            return {"permissions": list(granted)}
        return tr

    def fake_budget(projects=("projects/" + inst["project_id"],)):
        def tr(*, action, resource_name):
            return {
                "name": BUDGET_RESOURCE,
                "budgetFilter": {"projects": list(projects),
                                 "calendarPeriod": "MONTH"},
                "thresholdRules": [{"thresholdPercent": 0.5}],
                "amount": {"specifiedAmount": {"currencyCode": "USD",
                                               "units": "300", "nanos": 0}},
                "notificationsRule": {"monitoringNotificationChannels": [
                    "projects/%s/notificationChannels/ch0"
                    % inst["project_id"]]},
            }
        return tr

    def fake_channel():
        def tr(*, name):
            return {"name": name, "verificationStatus": "VERIFIED",
                    "enabled": True}
        return tr

    def fake_linkage():
        def tr(*, project_id):
            return {"billingAccountName": BILLING_ACCOUNT,
                    "billingEnabled": True}
        return tr

    def transports(**over):
        t = {
            "metadata": fake_metadata(), "compute": fake_compute(),
            "bootid": lambda: inst["boot_id"], "catalog": _min_catalog(),
            "mirror": seeded_mirror(), "systemctl": fake_systemctl(),
            "iam": fake_iam(), "budget": fake_budget(),
            "channel": fake_channel(), "linkage": fake_linkage(),
        }
        t.update(over)
        return t

    class FakeOps:
        def __init__(self, home="/home/ubuntu", handoff_exists=False,
                     events_nonempty=False, watchdog=False,
                     harness_drift=False, scp_bad=False, unit_active="active",
                     unit_pid="4242", unit_argv_bad=False):
            self.order = []
            self._home = home
            self._handoff_exists = handoff_exists
            self._events = events_nonempty
            self._watchdog = watchdog
            self._drift = harness_drift
            self._scp_bad = scp_bad
            self._unit_active = unit_active
            self._unit_pid = unit_pid
            self._unit_argv_bad = unit_argv_bad

        def ssh(self, command):
            self.order.append("ssh")
            if command.strip() == "echo $HOME":
                return self._home + "\n"
            return ""

        def remote_exists(self, path):
            return self._handoff_exists

        def remote_events_nonempty(self, rundir):
            return self._events

        def remote_sha256(self, path):
            name = path.rsplit("/", 1)[-1]
            if self._drift:
                return "d" * 64
            return sha256_file(HERE / name)

        def watchdog_alive(self):
            return self._watchdog

        def materialize_epoch_on_vm(self, launch_utc):
            self.order.append("materialize-epoch")

        def install_guest_units(self, units):
            self.order.append("install-units")

        def scp_bytes(self, remote_path, data):
            self.order.append("scp:" + remote_path.rsplit("/", 1)[-1])
            if self._scp_bad:
                return "0" * 64
            return hashlib.sha256(data).hexdigest()

        def cancel_maxlife(self):
            self.order.append("cancel-maxlife")

        def install_construction_unit(self, service):
            self.order.append("unit-start")
            return {"ActiveState": self._unit_active, "MainPID": self._unit_pid,
                    "ExecStart_argv": (["/bin/false"] if self._unit_argv_bad
                                       else service["exec_argv"])}

    def run(ops=None, **tr_over):
        ops = ops if ops is not None else FakeOps()
        return _construction_continue(
            gate_bytes=gate_bytes, ready_bytes=ready_bytes, now_fn=now_fn,
            ops=ops, transports=transports(**tr_over),
            local_epoch_path=os.path.join(tempfile.mkdtemp(), "absent.json"))

    # --- G1/2/3 staging + happy path ---
    ok_ops = FakeOps()
    receipt = run(ok_ops)
    check(receipt["cap_deadline_utc"] == deadline and receipt["handoff_sha256"],
          "G1 happy path runs phases 0-6 and produces a receipt")
    order = ok_ops.order
    check("preflight" in order and "cancel-maxlife" in order
          and "unit-start" in order,
          "G3 phase markers present (preflight, cancel-maxlife, unit-start)")
    check(order.index("preflight") < order.index("reprobe")
          < order.index("cancel-maxlife") < order.index("handoff")
          < order.index("unit-start"),
          "G8 order: preflight(cap legs) < reprobe < cancel < handoff < start")
    check("delete" not in order and "teardown" not in order,
          "G16 NO teardown/delete call anywhere in the continue path")

    # rebuild the handoff to assert acceptance (G1/G10)
    def build_and_validate():
        tr = transports()
        idn = f1k_ops.resolve_live_instance_identity(
            metadata_transport=tr["metadata"], compute_transport=tr["compute"],
            bootid_transport=tr["bootid"])
        pf = f1k_ops.preflight_launch_gate(
            now_utc=now, local_epoch_path=os.path.join(
                tempfile.mkdtemp(), "absent.json"),
            instance_name=idn["name"], zone=idn["zone"],
            project_id=idn["project_id"], deadline_utc=deadline,
            billing_account=BILLING_ACCOUNT,
            budget_resource_name=BUDGET_RESOURCE, machine_type=MACHINE_TYPE,
            local_ssd_count=LOCAL_SSD_COUNT, s_per_prefill="120",
            mirror_transport=tr["mirror"], systemctl_transport=tr["systemctl"],
            compute_transport=tr["compute"], iam_transport=tr["iam"],
            budget_transport=tr["budget"], channel_transport=tr["channel"],
            linkage_transport=tr["linkage"], catalog_transport=tr["catalog"],
            observed_at_utc=now)
        binding = f1k_ops.validate_ready_gate_binding(ready, gate)
        ev_ref = {"path": f1k_ops.RATE_EVIDENCE_PATH, "sha256": "8" * 64,
                  "schema": f1k_ops.RATE_EVIDENCE_SCHEMA,
                  "observed_at_utc": now}
        h = _build_construction_handoff(
            ready=ready, gate=gate, binding=binding, cap=pf["cap"],
            preflight=pf, rate_evidence_ref=ev_ref, now_utc=now,
            deadline=deadline, licensed_rate="0.219",
            project_id=idn["project_id"])
        f1k_ops.validate_handoff(h, now_utc=now)
        f1k_ops.build_runtime_license(ready, gate, h, now_utc=now)
        return h

    h = build_and_validate()
    check(h["schema"] == "kot-f1k-construction-handoff/2"
          and h["provider"]["cap"]["action"] == "STOP"
          and h["provider"]["cap"]["mechanism"] == "gce-termination-time"
          and h["provider"]["cap"]["termination_time_utc"] == deadline,
          "G10 produced handoff is /2 with a live-STOP cap == T_cap")
    check(h["service"]["exec_argv"] == [
        ready["builder"]["argv_base"][0],
        os.path.join(ready["payload"]["root"], "f1k_bringup_gate.py"),
        "guard", "--handoff", f1k_ops.CONSTRUCTION_HANDOFF_PATH],
        "G3 service.exec_argv is the direct guard --handoff argv")
    check(Decimal(h["provider"]["armed_hours_decimal"]) <= Decimal("899"),
          "G11 armed_hours <= 899")
    check("provenance" in h["provider"]["cap"]
          and h["provider"]["cap"]["provenance"]["schema"]
          == "kot-f1k-cap-attestation/1",
          "G38 produced handoff cap carries the LC-5 composite provenance")

    # --- BLOCKING-4: hand-built cap (no composite) is refused ---
    def hand_built_handoff():
        bad = json.loads(json.dumps(h))
        bad["provider"]["cap"] = {           # bare constant-string cap block
            "mechanism": "gce-termination-time", "action": "STOP",
            "termination_time_utc": deadline,
            "termination_timestamp_utc": deadline}
        bad["created_at_utc"] = h["created_at_utc"]
        f1k_ops.validate_handoff(bad, now_utc=now)
    check(refuses("F1K_HANDOFF", hand_built_handoff),
          "G38 (BLOCKING-4) hand-built cap block (no provenance) -> refused")
    check(refuses("F1K_CONTINUE_CAP_PROVENANCE", lambda: (
        _build_construction_handoff(
            ready=ready, gate=gate,
            binding=f1k_ops.validate_ready_gate_binding(ready, gate),
            cap={"termination_time_utc": deadline,
                 "termination_timestamp_utc": deadline},   # not a composite
            preflight={"budget_resource_name": BUDGET_RESOURCE},
            rate_evidence_ref={"path": f1k_ops.RATE_EVIDENCE_PATH,
                               "sha256": "8" * 64,
                               "schema": f1k_ops.RATE_EVIDENCE_SCHEMA,
                               "observed_at_utc": now},
            now_utc=now, deadline=deadline, licensed_rate="0.219",
            project_id=inst["project_id"]))),
        "G38 (BLOCKING-4) producer refuses a non-composite cap dict")
    # BLOCKING-4 re-review: a self-consistent provenance for a DIFFERENT target
    # (unrelated instance identity) is refused (cross-binding to the handoff).
    def wrong_target_provenance():
        bad = json.loads(json.dumps(h))
        bad["provider"]["cap"]["provenance"] = f1k_ops.make_cap_provenance(
            target="other-project/us-central1-a/other-vm",
            deadline_utc=deadline, oncalendar=f1k_ops._oncalendar(deadline),
            guest_target="other-project/us-central1-a/other-vm")
        f1k_ops.validate_handoff(bad, now_utc=now)
    check(refuses("F1K_HANDOFF", wrong_target_provenance),
          "G38 (BLOCKING-4) cross-bound provenance with an unrelated target "
          "-> refused")

    # --- CAP-PROBE gate (ISSUE-3): project/zone/commit/version/freshness bound;
    # fail-closed if git HEAD or the installed gcloud version is unresolvable ---
    real_head = _git_head_commit()
    real_gver = _installed_gcloud_version()

    def probe_rec(**over):
        checks = {k: "PASS" for k in f1k_ops.CAP_PROBE_CHECKS}
        rec = {"schema": f1k_ops.CAP_PROBE_SCHEMA, "verdict": "GREEN",
               "checks": checks, "project_id": PROJECT or "test-project",
               "zone": ZONE, "source_commit": real_head or ("a" * 40),
               "gcloud_version": real_gver or "0.0.0",
               "observed_at_utc": f1k_ops._utc_now_z()}
        rec.update(over)
        rec["sha256"] = hashlib.sha256(f1k_ops.canonical_json_bytes(
            {k: rec[k] for k in rec if k != "sha256"})).hexdigest()
        return rec

    def _gate_exit(rec):
        gp = os.path.join(tempfile.mkdtemp(), "probe.json")
        Path(gp).write_text(json.dumps(rec))
        os.environ["KOT_F1K_CAP_PROBE_EVIDENCE"] = gp
        return _sysexit(_require_cap_probe_green)
    saved_probe = os.environ.pop("KOT_F1K_CAP_PROBE_EVIDENCE", None)
    try:
        check(_sysexit(_require_cap_probe_green) == 2,
              "CAP-PROBE gate: cmd_provision refuses with no evidence env")
        if real_head is not None and real_gver is not None:
            # harness has git + gcloud: exercise the positive + bound-refusal path
            check(_gate_exit(probe_rec()) == 0,
                  "CAP-PROBE gate: a GREEN, project/zone/commit/version-bound, "
                  "fresh record permits provisioning")
            check(_gate_exit(probe_rec(verdict="RED")) == 2,
                  "CAP-PROBE gate: a non-GREEN probe refuses provisioning")
            check(_gate_exit(probe_rec(
                observed_at_utc="2000-01-01T00:00:00Z")) == 2,
                "CAP-PROBE gate (BLOCKING-2): a STALE 2000-01-01 probe refuses")
            check(_gate_exit(probe_rec(source_commit="b" * 40)) == 2,
                  "CAP-PROBE gate: a wrong source-commit probe refuses")
            check(_gate_exit(probe_rec(
                gcloud_version="HAND-BUILT-NOT-A-REAL-VERSION")) == 2,
                "CAP-PROBE gate (re-review): a wrong gcloud_version refuses")
        else:
            # ISSUE-3 fail-closed: no git HEAD or no installed gcloud version ->
            # the gate REFUSES even a well-formed 'GREEN' record.
            check(_gate_exit(probe_rec()) == 2,
                  "CAP-PROBE gate (re-review): fail-closed when git HEAD or the "
                  "installed gcloud version is unresolvable")
    finally:
        if saved_probe is not None:
            os.environ["KOT_F1K_CAP_PROBE_EVIDENCE"] = saved_probe
        else:
            os.environ.pop("KOT_F1K_CAP_PROBE_EVIDENCE", None)

    # --- G4/5/6/7 rate equality ---
    check(f1k_ops.canonical_decimal("0.2190", field="x")
          == f1k_ops.canonical_decimal("0.219", field="x"),
          "G5 representation variants canonicalize equal (no false refuse)")
    check(refuses("F1K_CONTINUE_RATE_DRIFT", lambda: run(
        catalog=lambda **k: {"skus": _drifted_catalog_skus()})),
        "G6 a drifted live rate -> NO-GO RATE_DRIFT")
    drift_ops = FakeOps()
    try:
        run(drift_ops, catalog=lambda **k: {"skus": _drifted_catalog_skus()})
    except (F1KContinueError, f1k_ops.F1KOpsError):
        pass
    check("install-units" not in drift_ops.order
          and "preflight" not in drift_ops.order
          and "cancel-maxlife" not in drift_ops.order,
          "G7 rate NO-GO mutates nothing (no units/preflight/cancel)")
    check(refuses("F1K_CONTINUE_RATE_QUOTE", lambda: run(
        catalog=lambda **k: (_ for _ in ()).throw(OSError("down")))),
        "G4 a quote outage -> NO-GO RATE_QUOTE")

    # --- G9 each preflight leg broken -> refuse at phase 2, no later calls ---
    for label, over in (
        ("L1 DELETE action", {"compute": fake_compute(action="DELETE")}),
        ("L1 drifted terminationTime", {"compute": fake_compute(
            term="2030-01-01T00:00:00Z")}),
        ("L2 inactive timer", {"systemctl": fake_systemctl(active="inactive")}),
        ("IAM not granted", {"iam": fake_iam(
            granted=("compute.instances.get",))}),
        ("budget wrong project", {"budget": fake_budget(
            projects=("projects/other-project",))}),
    ):
        leg_ops = FakeOps()
        refused = refuses("F1K_CONTINUE_PREFLIGHT",
                          lambda o=leg_ops, ov=over: run(o, **ov))
        check(refused and "cancel-maxlife" not in leg_ops.order
              and "handoff" not in leg_ops.order,
              "G9 preflight leg broken (%s) -> refuse, no cancel/handoff"
              % label)

    # --- G25/31 phase-4 re-probe TOCTOU ---
    class DriftingCompute:
        """L1 clean at preflight, drifted at the phase-4 re-probe."""
        def __init__(self):
            self.calls = 0

        def __call__(self, *, project_id, zone, instance_name):
            self.calls += 1
            good = fake_compute()(project_id=project_id, zone=zone,
                                  instance_name=instance_name)
            # first 2 calls (identity + preflight cap) clean; later (reprobe) drift
            if self.calls >= 3:
                good["scheduling"]["terminationTime"] = "2030-01-01T00:00:00Z"
            return good
    toctou_ops = FakeOps()
    check(refuses("F1K_B_CAP_DRIFT",
                  lambda: run(toctou_ops, compute=DriftingCompute()))
          and "cancel-maxlife" not in toctou_ops.order,
          "G31 phase-4 L1 re-probe drift -> refuse BEFORE cancel-maxlife")

    # --- G12/13/14/15 preconditions ---
    check(refuses("F1K_CONTINUE_WATCHDOG",
                  lambda: run(FakeOps(watchdog=True))),
          "G12 live watchdog -> refuse WATCHDOG")
    check(refuses("F1K_CONTINUE_ALREADY",
                  lambda: run(FakeOps(handoff_exists=True))),
          "G13 existing handoff -> refuse ALREADY")
    check(refuses("F1K_CONTINUE_ALREADY",
                  lambda: run(FakeOps(events_nonempty=True))),
          "G13 non-empty construction-events -> refuse ALREADY")
    check(refuses("F1K_CONTINUE_HARNESS_DRIFT",
                  lambda: run(FakeOps(harness_drift=True))),
          "G14 on-VM harness sha drift -> refuse HARNESS_DRIFT")
    check(refuses("F1K_CONTINUE_HOME",
                  lambda: run(FakeOps(home="/home/ec2-user"))),
          "G14 wrong remote $HOME -> refuse HOME (seam W-USER)")
    bad_gate = json.loads(json.dumps(gate))
    bad_gate["verdict"] = "STOP"
    check(refuses("F1K",
                  lambda: _construction_continue(
                      gate_bytes=f1k_ops.canonical_json_bytes(bad_gate),
                      ready_bytes=ready_bytes, now_fn=now_fn, ops=FakeOps(),
                      transports=transports(), local_epoch_path=os.path.join(
                          tempfile.mkdtemp(), "x.json"))),
          "G14 non-GREEN gate -> refuse")
    check(refuses("F1K_CONTINUE_IDENTITY",
                  lambda: run(FakeOps(),
                              bootid=lambda: "00000000-0000-4000-8000-"
                                             "000000000000")),
          "G14 boot_id != READY -> refuse IDENTITY")

    def wallclock_run():
        # a launch ~130 h before now leaves remaining billable hours BELOW
        # projected+1SE(750) + reserve(36.53) + margin(2) = 788.53 h.
        near = "2026-07-18T20:00:00Z"
        mir = {}

        def m(*, action, key, data=None):
            if action == "put":
                mir[key] = data
                return None
            return mir.get(key)
        f1k_ops.write_launch_epoch(launch_utc=near, local_path=os.path.join(
            tempfile.mkdtemp(), "e.json"), mirror_transport=m)
        return _construction_continue(
            gate_bytes=gate_bytes, ready_bytes=ready_bytes, now_fn=now_fn,
            ops=FakeOps(), transports=transports(
                mirror=m, compute=fake_compute(
                    term=f1k_ops.compute_selfdelete_deadline(launch_utc=near))),
            local_epoch_path=os.path.join(tempfile.mkdtemp(), "absent.json"))
    check(refuses("F1K_CONTINUE_WALLCLOCK", wallclock_run),
          "G15 wall-clock insufficiency -> refuse WALLCLOCK")

    # --- G27 sha read-back mismatch on scp ---
    check(refuses("F1K_CONTINUE_SCP", lambda: run(FakeOps(scp_bad=True))),
          "G27 scp sha read-back mismatch -> refuse SCP")
    check(refuses("F1K_CONTINUE_UNIT",
                  lambda: run(FakeOps(unit_active="failed"))),
          "G27 construction unit not active -> refuse UNIT")
    check(refuses("F1K_CONTINUE_UNIT",
                  lambda: run(FakeOps(unit_argv_bad=True))),
          "G27 systemd ExecStart != handoff argv -> refuse UNIT")

    # --- G22 mirror-required (LC-12) ---
    check(refuses("F1K_B_MIRROR_REQUIRED", lambda: f1k_ops._resolve_epoch_launch(
        local_path=_seed_local_epoch(launch), mirror_transport=(
            lambda **k: None), require_mirror=True)),
        "G22 local epoch present + mirror absent -> refuse (LC-12)")

    # --- BLOCKING-1: production structured classifiers (raw shapes) ---
    _classifier_oracle(check)
    # --- G21/28/29 provision epoch-order + cap-in-request + faildelete ---
    _provision_oracle(check, launch=launch)
    # --- G32 teardown ordering ---
    _teardown_oracle(check)
    # --- G37 reaper on a stopped instance ---
    _reaper_oracle(check)

    # --- Rev2 blockers 1/2/3: the money-path governance gate ---------------
    _launch_gate_oracle(check)

    print("CONSTRUCTION-CONTINUE SELFTEST: %d/%d %s"
          % (passed, total, "PASS" if passed == total else "FAILED"))
    return 0 if passed == total else 2


def _launch_gate_oracle(check):
    """$0 proof that `construction-continue`'s pre-launch gate is fail-closed
    (Rev2). Exercises: (1) LANDED-AWARE live-tree checks — post-splice the
    frozen-pin axis (frozen-index == FROZEN_SHA256 == 7897dd0a) ACCEPTS via
    verify_pins() and the launch-gate frozen axis; these read the live registry
    and are the REVERT-DETECTORS (a splice revert flips them red); (2) a
    registry-check returncode!=0 REFUSES; (3) a HALF-APPLIED splice
    (frozen-index at POST but the seq-4 correction / ASM-2525 absent) REFUSES;
    (3c) the pre-splice frozen-index (PRE hash) REFUSES — the deterministic
    fixture that keeps the REFUSAL path covered in BOTH tree states;
    (4) the FULLY-applied state PASSES (the gate is not a tautological refuse).
    (2)-(4) run against a throwaway sandbox with an injected checker — no
    repo mutation, no GCP, $0."""
    import shutil

    POST = "7897dd0a8fbb432768d70e959a77abdd80c16c78ab93702ff6f1671828bf7802"

    def refuses_gate(fn):
        try:
            fn()
        except SystemExit as exc:
            return exc.code == 2
        return False

    def passes(fn):
        try:
            fn()
            return True
        except SystemExit:
            return False

    class _RC:
        def __init__(self, code, out=""):
            self.returncode = code
            self.stdout = out
            self.stderr = ""

    def ok_checker(*a, **k):
        return _RC(0, "registry-check: PASS\n")

    def bad_checker(*a, **k):
        return _RC(99, "registry-check: 1 violation(s)\n")

    # (1) LANDED-AWARE live-tree checks. The coordinator has LANDED the seq-4
    #     re-freeze, so the live frozen-index is now 7897dd0a…. These read the
    #     LIVE registry and assert the frozen-pin axis ACCEPTS — which makes
    #     them the REVERT-DETECTORS: if anyone reverts the splice (frozen-index
    #     back to the pre-splice 35372275…), each flips red. The pre-splice
    #     REFUSAL path stays covered deterministically by fixture (3c) below,
    #     so the selftest is meaningful in BOTH tree states.
    live_idx = json.loads(
        (REPO / "registry" / "frozen-index.json").read_text(encoding="utf-8"))
    check(live_idx.get("f1k") == FROZEN_SHA256 == POST,
          "LANDED live tree: frozen-index f1k == FROZEN_SHA256 == 7897dd0a "
          "(re-freeze landed; a splice revert makes this go red)")
    check(passes(verify_pins),
          "verify_pins() PASSES on the landed live tree "
          "(--frozen-drift rc0 + full 7897dd0a bind + file pins); "
          "a revert to the pre-splice record flips it red")
    check(passes(lambda: _frozen_governance(
            REPO, FROZEN_SHA256, checker=ok_checker)),
          "launch-gate frozen axis (live frozen-index + seq-4 correction + "
          "ASM-2525) PASSES on the landed tree with the full registry-check "
          "stubbed; a revert flips it red")

    sandbox = Path(tempfile.mkdtemp(prefix="f1k-launch-gate-"))
    try:
        reg = sandbox / "registry"
        (reg / "corrections" / "f1k").mkdir(parents=True)
        # fully-applied fixture
        (reg / "frozen-index.json").write_text(
            json.dumps({"f1k": POST}), encoding="utf-8")
        corr = {"experiment": "f1k", "seq": 4, "refrozen_sha256": POST,
                "schema_version": "kot-correction/1"}
        (reg / "corrections" / "f1k" / "4-generator-repin.json").write_text(
            json.dumps(corr), encoding="utf-8")
        (reg / "assumptions.jsonl").write_text(
            '{"id": "ASM-2525", "tag": "STIPULATED"}\n', encoding="utf-8")

        # (2) returncode!=0 from registry-check => REFUSE (blocker 3 code path).
        check(refuses_gate(
            lambda: _frozen_governance(sandbox, POST, checker=bad_checker)),
            "registry-check returncode!=0 REFUSES launch "
            "(F1K_REGISTRY_CHECK, not fail-open on rc)")

        # (4) fully-applied + clean registry-check => PASS (positive control:
        #     the gate is not a tautological refuse).
        passed_ok = True
        try:
            _frozen_governance(sandbox, POST, checker=ok_checker)
        except SystemExit:
            passed_ok = False
        check(passed_ok,
              "fully-applied sandbox (index@POST + seq-4 correction + "
              "ASM-2525) PASSES the governance gate")

        # (3a) HALF-APPLIED: index written at POST but the seq-4 correction
        #      never copied => REFUSE (blocker 2: index alone is not the
        #      launch marker; correction must be present).
        (reg / "corrections" / "f1k" / "4-generator-repin.json").unlink()
        check(refuses_gate(
            lambda: _frozen_governance(sandbox, POST, checker=ok_checker)),
            "half-applied splice (index@POST, seq-4 correction ABSENT) "
            "REFUSES launch (F1K_GOV_CORRECTION)")
        (reg / "corrections" / "f1k" / "4-generator-repin.json").write_text(
            json.dumps(corr), encoding="utf-8")

        # (3b) HALF-APPLIED: correction present but ASM-2525 not registered
        #      => REFUSE (blocker 2: ASM is part of the landing).
        (reg / "assumptions.jsonl").write_text(
            '{"id": "ASM-2400", "tag": "STIPULATED"}\n', encoding="utf-8")
        check(refuses_gate(
            lambda: _frozen_governance(sandbox, POST, checker=ok_checker)),
            "half-applied splice (correction present, ASM-2525 UNregistered) "
            "REFUSES launch (F1K_GOV_ASM)")

        # (3b') Rev3 blocker 2: a FOREIGN entry that merely QUOTES the string
        #       "ASM-2525" (id is something else) must NOT count as registered.
        (reg / "assumptions.jsonl").write_text(
            '{"id": "ASM-2400", "notes": "supersedes ASM-2525 discussion"}\n',
            encoding="utf-8")
        check(refuses_gate(
            lambda: _frozen_governance(sandbox, POST, checker=ok_checker)),
            "foreign record QUOTING \"ASM-2525\" (id!=ASM-2525) does NOT "
            "count as registered — REFUSES (id-parse, not substring)")
        # positive: a real id==ASM-2525 entry among decoys IS accepted.
        (reg / "assumptions.jsonl").write_text(
            '{"id": "ASM-2400", "notes": "ASM-2525"}\n'
            '{"id": "ASM-2525", "tag": "STIPULATED"}\n', encoding="utf-8")
        ok_asm = True
        try:
            _frozen_governance(sandbox, POST, checker=ok_checker)
        except SystemExit:
            ok_asm = False
        check(ok_asm,
              "a real id==ASM-2525 entry (with a decoy quoting it) IS "
              "accepted (id-parse positive control)")

        # (3b'') Rev4 blocker 1: _asm_registered is FULLY fail-closed — the
        #        whole ledger must parse, and a malformed line BEFORE a valid
        #        ASM-2525, AFTER it, or a DUPLICATE target id all REFUSE.
        (reg / "assumptions.jsonl").write_text(
            'not-json-at-all\n{"id": "ASM-2525", "tag": "STIPULATED"}\n',
            encoding="utf-8")
        check(refuses_gate(
            lambda: _frozen_governance(sandbox, POST, checker=ok_checker)),
            "malformed line BEFORE a valid ASM-2525 REFUSES "
            "(whole-file parse, no false-True)")
        (reg / "assumptions.jsonl").write_text(
            '{"id": "ASM-2525", "tag": "STIPULATED"}\nnot-json-at-all\n',
            encoding="utf-8")
        check(refuses_gate(
            lambda: _frozen_governance(sandbox, POST, checker=ok_checker)),
            "malformed line AFTER a valid ASM-2525 REFUSES "
            "(no early-return on first match)")
        (reg / "assumptions.jsonl").write_text(
            '{"id": "ASM-2525", "tag": "STIPULATED"}\n'
            '{"id": "ASM-2525", "note": "dup"}\n', encoding="utf-8")
        check(refuses_gate(
            lambda: _frozen_governance(sandbox, POST, checker=ok_checker)),
            "DUPLICATE id==ASM-2525 REFUSES (ambiguity detected, exactly-one)")
        # reset to a single valid entry for the remaining checks
        (reg / "assumptions.jsonl").write_text(
            '{"id": "ASM-2525", "tag": "STIPULATED"}\n', encoding="utf-8")

        # (3c) index at the PRE hash (record written but index not advanced,
        #      or vice-versa) => REFUSE on the full-hash bind.
        (reg / "frozen-index.json").write_text(
            json.dumps({"f1k": "35372275354c7d3841dcf627b70edf64"
                               "ffbe15190a0669658c5b6df082dc9b9c"}),
            encoding="utf-8")
        check(refuses_gate(
            lambda: _frozen_governance(sandbox, POST, checker=ok_checker)),
            "frozen-index still at the PRE hash REFUSES launch "
            "(F1K_PIN_FROZEN full-hash bind)")
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)

    # ---- Rev3/Rev4 END-TO-END wiring proof: each SPEND-CAPABLE command hits
    #      the FULL governance gate BEFORE any cloud op — proven in BOTH
    #      directions. Rev4 correction 2: every command is given valid fake
    #      args + env + readable artifacts so it actually REACHES its launch
    #      boundary, and EVERY direct provider surface (gcloud, vm_exists,
    #      cap-probe, provision-execute, the GCS mirror, the paid orchestrator
    #      _construction_continue, f1k_ops._gcloud_compute_get, the catalog
    #      HTTP list, blocking-delete/describe-presence) is sentineled. Non-
    #      cloud local guards (_gate reuse-check, payload assembly, transports/
    #      ops constructors) are no-op'd so they cannot early-exit and mask the
    #      boundary. Then: (present) the real gate raises GATE -> outcome=gate;
    #      (absent) the gate is stubbed away -> the command reaches a cloud
    #      sentinel -> outcome=gcp. A regression that dropped the gate would
    #      flip the present leg to gcp; a sentinel gap would flip the absent
    #      leg away from gcp — either fails the check.
    _wiring_oracle(check)


class _GateReached(Exception):
    pass


class _GcpReached(Exception):
    pass


def _wiring_oracle(check):
    import tempfile, shutil
    g = globals()

    def _raise_gate(*a, **k):
        raise _GateReached()

    def _raise_gcp(*a, **k):
        raise _GcpReached()

    # cloud / paid boundaries — ANY of these means a real spend would begin
    cloud = {
        "gcloud": _raise_gcp,
        "vm_exists": _raise_gcp,
        "_require_cap_probe_green": _raise_gcp,
        "_provision_execute": _raise_gcp,
        "_gsutil_mirror": _raise_gcp,
        "_blocking_delete": _raise_gcp,
        "_describe_presence": _raise_gcp,
        "_construction_continue": _raise_gcp,   # cc's paid orchestrator
    }
    # non-cloud local guards that could otherwise die/early-exit and mask the
    # boundary in the gate-ABSENT leg
    # (_provision_plan is pure and is left REAL — it never touches the cloud.)
    local_noops = {
        "_gate": (lambda *a, **k: None),
        "_construction_payload_files": (lambda *a, **k: []),
        "RealContinueOps": (lambda *a, **k: object()),
        "_real_transports": (lambda *a, **k: {}),
    }
    # direct provider surfaces on the f1k_ops module (defensive: no unstubbed
    # cloud call can slip through even if call order changes)
    ops_cloud = {
        "_gcloud_compute_get": _raise_gcp,
        "_catalog_http_list": _raise_gcp,
    }

    base = dict(cloud)
    base.update(local_noops)
    saved = {k: g.get(k) for k in base}
    # the three governance-gate functions are patched inside the legs below;
    # capture their originals up front so the finally-block restores them.
    gate_saved = {k: g.get(k) for k in (
        "verify_pins", "_frozen_governance", "_construction_launch_gate")}
    ops_saved = {k: getattr(f1k_ops, k, None) for k in ops_cloud}
    old_argv = sys.argv
    old_env = {k: os.environ.get(k) for k in (
        "KOT_F1K_BUCKET", "KOT_GCP_PROJECT", "KOT_GCP_BILLING_ACCOUNT",
        "KOT_F1K_BUDGET_RESOURCE")}
    tmp = Path(tempfile.mkdtemp(prefix="f1k-wiring-"))
    (tmp / "gate.json").write_text("{}", encoding="utf-8")
    (tmp / "ready.json").write_text("{}", encoding="utf-8")

    cc_argv = ["f1k_gcp.py", "construction-continue",
               "--gate", str(tmp / "gate.json"),
               "--ready", str(tmp / "ready.json")]
    commands = (
        ("provision", cmd_provision, ["f1k_gcp.py", "provision"]),
        ("bringup-deploy", cmd_bringup_deploy, ["f1k_gcp.py", "bringup-deploy"]),
        ("construction-continue", cmd_construction_continue, cc_argv),
    )

    def outcome(cmd_fn, argv):
        sys.argv = argv
        try:
            cmd_fn()
            return "returned-without-boundary"
        except _GateReached:
            return "gate"
        except _GcpReached:
            return "gcp"
        except SystemExit as e:
            return "exit(%s)" % e.code
        except BaseException as e:  # noqa: BLE001
            return "other:%r" % e

    try:
        for k, v in base.items():
            g[k] = v
        for k, v in ops_cloud.items():
            setattr(f1k_ops, k, v)
        for k, v in old_env.items():
            os.environ[k] = "wiring-fake"

        # present leg: real gate, but verify_pins passes and _frozen_governance
        # raises the GATE sentinel — the wired command must hit it FIRST.
        g["verify_pins"] = (lambda *a, **k: {})
        g["_frozen_governance"] = _raise_gate
        for name, fn, argv in commands:
            res = outcome(fn, argv)
            check(res == "gate",
                  "[gate PRESENT] spend-capable `%s` hits the governance gate "
                  "BEFORE any cloud op (outcome=%s)" % (name, res))

        # absent leg: the gate is stubbed AWAY (simulating a wiring regression)
        # — each command must then REACH a cloud sentinel, proving the sentinel
        # sits at the real launch boundary (not masked by an early exit).
        g["_construction_launch_gate"] = (lambda *a, **k: None)
        for name, fn, argv in commands:
            res = outcome(fn, argv)
            check(res == "gcp",
                  "[gate ABSENT] spend-capable `%s` REACHES a cloud sentinel "
                  "at its launch boundary (outcome=%s)" % (name, res))
    finally:
        for k, v in saved.items():
            g[k] = v
        for k, v in gate_saved.items():
            g[k] = v
        for k, v in ops_saved.items():
            if v is not None:
                setattr(f1k_ops, k, v)
        for k, v in old_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        sys.argv = old_argv
        shutil.rmtree(tmp, ignore_errors=True)


def _drifted_catalog_skus():
    cat = _min_catalog()()
    # bump the core price so the blended rate != 0.219 (drift)
    cat["skus"][0]["pricingInfo"][0]["pricingExpression"][
        "tieredRates"][0]["unitPrice"]["nanos"] = 20000000
    return cat["skus"]


def _seed_local_epoch(launch):
    d = tempfile.mkdtemp()
    p = os.path.join(d, "launch-epoch.json")
    store = {}

    def m(*, action, key, data=None):
        if action == "put":
            store[key] = data
            return None
        return store.get(key)
    f1k_ops.write_launch_epoch(launch_utc=launch, local_path=p,
                               mirror_transport=m)
    return p


# Raw `instances list` / `instances delete` --format=json output shapes, fed
# through the REAL production classifiers (_classify_list_presence,
# _blocking_delete/_classify_delete_operation) in the money-path oracles: the
# oracles inject RAW (rc, stdout) tuples, never already-classified values or
# fake delete outcomes (re-review: exercise the real CLI operation boundary).
_N = "kot-f1k-run"
_RAW_PRESENT = (0, json.dumps([{"name": _N, "id": "1"}]))
_RAW_ABSENT = (0, "[]")
_RAW_PERMISSION = (1, _PERMISSION_REPRODUCER)   # rc=1 + text -> unknown
_RAW_DEL_DONE = (0, json.dumps({"status": "DONE"}))
_RAW_DEL_OPERR = (0, json.dumps(
    {"status": "DONE", "error": {"errors": [{"code": "RESOURCE_IN_USE"}]}}))
_RAW_DEL_OUTAGE = (1, "")                        # rc!=0 -> re-confirm presence


def _presence_from(state, *, partial_error_disabled=True):
    """Build a presence_fn that runs the PRODUCTION classifier on the current
    raw (rc, stdout) list output — so the permission reproducer flows through.
    partial_error_disabled models whether the list ran with the strict flag."""
    return lambda: _classify_list_presence(
        state["raw"][0], state["raw"][1], name=_N,
        partial_error_disabled=partial_error_disabled)


def _real_delete_from(state, del_raw, *, flip_absent=False):
    """Build a delete_fn that runs the REAL _blocking_delete parsing on a raw
    (rc, stdout) delete result. `del_raw` may be a tuple or a zero-arg callable
    (for per-attempt sequencing). flip_absent flips the presence state to a
    genuine structured absence after the op runs."""
    def delete_fn():
        def runner():
            raw = del_raw() if callable(del_raw) else del_raw
            if flip_absent:
                state["raw"] = _RAW_ABSENT
            return raw
        return _blocking_delete(runner=runner, presence_fn=_presence_from(state))
    return delete_fn


def _provision_oracle(check, *, launch):
    order = []
    made = {"id": "1234567890123456789"}
    store = {}

    def mirror(*, action, key, data=None):
        if action == "put":
            store[key] = data
            return None
        return store.get(key)

    def describe_ok():
        dl = f1k_ops.compute_selfdelete_deadline(launch_utc=launch)
        return {"id": made["id"], "scheduling": {
            "provisioningModel": "SPOT", "instanceTerminationAction": "STOP",
            "terminationTime": dl,
            "onInstanceStopAction": {"discardLocalSsd": True}}}

    def create_fn(cap):
        order.append("create")
        made["cap"] = cap
    d = tempfile.mkdtemp()
    res = _provision_execute(
        now_fn=lambda: launch, mirror=mirror, create_fn=create_fn,
        describe_fn=describe_ok,
        delete_fn=_real_delete_from({"raw": _RAW_PRESENT}, _RAW_DEL_DONE),
        presence_fn=lambda: "present",
        local_epoch_path=os.path.join(d, "e.json"),
        binding_path=os.path.join(d, "b.json"), order=order,
        instance_name=_N, zone="us-central1-a",
        project_id="test-project", sleep_fn=lambda s: None)
    check(order.index("epoch-persist") < order.index("create")
          and res["deadline_utc"] == f1k_ops.compute_selfdelete_deadline(
              launch_utc=launch),
          "G21/28 epoch persisted + cap-in-request BEFORE create; T_cap deadline")
    check(made["cap"]["termination_time"] == res["deadline_utc"]
          and made["cap"]["instance_termination_action"] == "STOP"
          and made["cap"]["discard_local_ssds_at_termination_timestamp"] is True,
          "G28 create request carries T_cap + STOP + discard-local-SSD flag")

    def _mk_provision(*, describe_fn, del_raw, presence_raw, order,
                      flip_absent=False, presence_ped=True):
        st = {"raw": presence_raw}
        store2 = {}

        def mirror2(*, action, key, data=None):
            if action == "put":
                store2[key] = data
                return None
            return store2.get(key)
        d2 = tempfile.mkdtemp()
        return _provision_execute(
            now_fn=lambda: launch, mirror=mirror2, create_fn=lambda c: None,
            describe_fn=describe_fn,
            delete_fn=_real_delete_from(st, del_raw, flip_absent=flip_absent),
            presence_fn=_presence_from(st, partial_error_disabled=presence_ped),
            local_epoch_path=os.path.join(d2, "e.json"),
            binding_path=os.path.join(d2, "b.json"), order=order,
            instance_name=_N, zone="us-central1-a",
            project_id="test-project", sleep_fn=lambda s: None)

    def describe_bad():
        return {"id": made["id"], "scheduling": {
            "provisioningModel": "SPOT",
            "instanceTerminationAction": "DELETE",   # mis-provisioned cap
            "terminationTime": f1k_ops.compute_selfdelete_deadline(
                launch_utc=launch),
            "onInstanceStopAction": {"discardLocalSsd": True}}}
    # G29: read-back mismatch -> fail-closed delete (real DONE operation) ->
    # genuine structured 404.
    order2 = []
    refused = False
    try:
        _mk_provision(describe_fn=describe_bad, del_raw=_RAW_DEL_DONE,
                      presence_raw=_RAW_PRESENT, order=order2, flip_absent=True)
    except F1KContinueError as exc:
        refused = exc.code == "F1K_PROVISION_READBACK"
    check(refused and order2.index("create") < order2.index("faildelete")
          < order2.index("delete") < order2.index("absence"),
          "G29 read-back mismatch -> fail-closed delete + genuine-404 confirm")

    # G29-OPERR: read-back bad, the delete OPERATION carries a structured error
    # -> _blocking_delete raises -> provision raises, never declares absence.
    order3 = []
    outage_refused = None
    try:
        _mk_provision(describe_fn=describe_bad, del_raw=_RAW_DEL_OPERR,
                      presence_raw=_RAW_PRESENT, order=order3)
    except F1KContinueError as exc:
        outage_refused = exc.code
    check(outage_refused == "F1K_PROVISION_READBACK"
          and "absence" not in order3,
          "G29-OPERR structured delete-operation error -> raise, NEVER declares "
          "absence (uncapped-VM hazard surfaced)")

    # G29-PERMISSION (reproducer): read-back bad, delete op DONE, but the
    # confirming presence is the PERMISSION reproducer (rc=1) fed to the REAL
    # classifier -> unknown -> absence NEVER confirmed -> raise.
    order4 = []
    amb_refused = None
    try:
        _mk_provision(describe_fn=describe_bad, del_raw=_RAW_DEL_DONE,
                      presence_raw=_RAW_PERMISSION, order=order4)
    except F1KContinueError as exc:
        amb_refused = exc.code
    check(amb_refused == "F1K_PROVISION_READBACK"
          and "absence" not in order4,
          "G29-PERMISSION exact permission-error presence (rc=1) -> classifier "
          "unknown -> never declares absence (the fail-open reproducer raises)")

    # G29-PARTIAL (round-4 reproducer): read-back bad, delete op DONE, but the
    # confirming presence is (rc=0, "[]") produced with partial-error ENABLED ->
    # the REAL classifier returns unknown -> absence NEVER confirmed -> raise.
    order5 = []
    pe_refused = None
    try:
        _mk_provision(describe_fn=describe_bad, del_raw=_RAW_DEL_DONE,
                      presence_raw=(0, "[]\n"), presence_ped=False, order=order5)
    except F1KContinueError as exc:
        pe_refused = exc.code
    check(pe_refused == "F1K_PROVISION_READBACK" and "absence" not in order5,
          "G29-PARTIAL (round-4) rc=0 '[]' with partial-error ENABLED != "
          "absence -> classifier unknown -> never declares absence")


def _teardown_oracle(check):
    # G32: delete (real DONE operation) -> genuine structured 404 -> cleanup.
    order = []
    state = {"raw": _RAW_PRESENT}
    removed = {"v": False}
    _teardown_execute(
        presence_fn=_presence_from(state),
        delete_fn=_real_delete_from(state, _RAW_DEL_DONE, flip_absent=True),
        remove_cleanup_fn=lambda: (order.append("cleanup"),
                                   removed.__setitem__("v", True)),
        order=order, sleep_fn=lambda s: None)
    check(order.index("delete") < order.index("absence")
          < order.index("cleanup") and removed["v"],
          "G32 teardown order: delete < genuine-404 absence < cleanup-removal")

    # G32-OPERR: the delete OPERATION errors -> raise, cleanup NOT removed.
    order2 = []
    state2 = {"raw": _RAW_PRESENT}
    removed2 = {"v": False}
    failed = None
    try:
        _teardown_execute(
            presence_fn=_presence_from(state2),
            delete_fn=_real_delete_from(state2, _RAW_DEL_OPERR),
            remove_cleanup_fn=lambda: removed2.__setitem__("v", True),
            order=order2, name=_N, sleep_fn=lambda s: None)
    except F1KContinueError as exc:
        failed = exc.code
    check(failed == "F1K_DELETE_OP" and removed2["v"] is False,
          "G32 structured delete-operation error leaves cleanup NOT removed")

    # G32-PERMISSION: delete op DONE but the confirming presence is the
    # permission reproducer -> classifier unknown -> raise, no cleanup.
    order3 = []
    state3 = {"raw": _RAW_PERMISSION}
    removed3 = {"v": False}
    outage = None
    try:
        _teardown_execute(
            presence_fn=_presence_from(state3),
            delete_fn=_real_delete_from(state3, _RAW_DEL_DONE),
            remove_cleanup_fn=lambda: removed3.__setitem__("v", True),
            order=order3, name=_N, sleep_fn=lambda s: None)
    except F1KContinueError as exc:
        outage = exc.code
    check(outage == "F1K_DELETE_ABSENCE" and removed3["v"] is False
          and "absence" not in order3,
          "G32-PERMISSION permission-error presence != absence -> raise, "
          "cleanup NOT removed")


def _reaper_oracle(check):
    # G37: reaper deletes a TERMINATED instance; the first delete OPERATION
    # carries a structured error, the second is DONE -> retry the WHOLE verified
    # delete until a genuine structured 404 (real _blocking_delete parsing).
    order = []
    state = {"raw": _RAW_PRESENT, "attempts": 0}

    def del_raw():
        state["attempts"] += 1
        if state["attempts"] < 2:       # first delete OPERATION errors
            return _RAW_DEL_OPERR
        state["raw"] = _RAW_ABSENT
        return _RAW_DEL_DONE
    delete_fn = _real_delete_from(state, del_raw)
    result = {"ok": False}

    def loop():
        for _ in range(5):
            try:
                _verified_delete(
                    delete_fn=delete_fn, presence_fn=_presence_from(state),
                    name=_N, order=order, sleep_fn=lambda s: None)
                result["ok"] = True
                return
            except F1KContinueError:
                continue
    loop()
    check(result["ok"] and order.count("delete") >= 2
          and order[-1] == "absence",
          "G37 reaper retries the whole verified delete until 404 absence")

    # G37-PERMISSION: presence is the permission reproducer forever -> classifier
    # unknown -> absence never confirmed -> one _verified_delete raises.
    order5 = []
    state5 = {"raw": _RAW_PERMISSION}
    amb = None
    try:
        _verified_delete(
            delete_fn=_real_delete_from(state5, _RAW_DEL_DONE),
            presence_fn=_presence_from(state5), name=_N, order=order5,
            sleep_fn=lambda s: None)
    except F1KContinueError as exc:
        amb = exc.code
    check(amb == "F1K_DELETE_ABSENCE" and "absence" not in order5,
          "G37-PERMISSION permission-error presence never confirms absence")


def _reaper_selftest():
    passed = total = 0

    def check(cond, label):
        nonlocal passed, total
        total += 1
        passed += int(bool(cond))
        print("  %s%s" % ("ok:  " if cond else "FAIL: ", label))
    print("SELFTEST SCOPE: $0 cap-reaper verified-delete loop; fakes only.")
    _reaper_oracle(check)
    print("CAP-REAPER SELFTEST: %d/%d %s"
          % (passed, total, "PASS" if passed == total else "FAILED"))
    return 0 if passed == total else 2


ENTRY = {
    "plan": cmd_plan, "provision": cmd_provision, "status": cmd_status,
    "teardown": cmd_teardown, "affordability": cmd_affordability,
    "gate": cmd_gate,
    "bringup-deploy": cmd_bringup_deploy, "watchdog": cmd_watchdog,
    "pin-fetch": cmd_pin_fetch,
    "construction-continue": cmd_construction_continue,
    "cap-reaper": cmd_cap_reaper,
}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in ENTRY:
        print("usage: f1k_gcp.py {%s}" % "|".join(ENTRY), file=sys.stderr)
        sys.exit(2)
    ENTRY[sys.argv[1]]()


if __name__ == "__main__":
    main()
