"""Modal staging app for the 99a frozen simulation run — SETUP + VALIDATION ONLY.

Pinned stack (SIM-SPEC S2/R8g): CPython 3.12 + numpy 2.1.3 + scipy 1.14.1
Reference stack (B2 fixture only): R 4.4.1 + lme4 1.1-35.5 + lmerTest 3.1-3.

This app does NOT run the full grid. It:
  versions()        -> report ACTUAL installed versions vs pins
  b2_fixture()      -> S4.2 balanced closed-form ANOVA vs lme4/lmerTest REML
  run_fwer_slice()  -> a small-R FWER cell on the pinned image
  run_gatecal_slice()-> a small-R gate-cal cell on the pinned image
  bench_timing()    -> per-rep ms on Modal hardware for the cost estimate
"""
import modal

SIM_LOCAL = "/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim"

image = (
    modal.Image.from_registry("rocker/r-ver:4.4.1", add_python="3.12")
    .pip_install("numpy==2.1.3", "scipy==1.14.1")
    .run_commands(
        # remotes for exact-version pinning of the R reference stack
        "R -q -e \"install.packages('remotes')\"",
        # exact pins (S4.2 / R8b). install_version grabs the binary if the RSPM
        # snapshot's current == requested, else compiles from source.
        "R -q -e \"remotes::install_version('lme4', version='1.1-35.5', upgrade='never', dependencies=TRUE)\"",
        "R -q -e \"remotes::install_version('lmerTest', version='3.1-3', upgrade='never', dependencies=TRUE)\"",
    )
    .add_local_dir(
        SIM_LOCAL, remote_path="/root/sim",
        ignore=["venv/**", "__pycache__/**", "*.pyc", "results/**", ".git/**"],
    )
)

app = modal.App("kot-99a-frozen-setup", image=image)


# ----------------------------------------------------------------------------
@app.function(cpu=1.0)
def versions():
    import subprocess, sys, numpy, scipy, platform
    rver = subprocess.run(["R", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    pk = subprocess.run(
        ["Rscript", "-e",
         "cat(as.character(getRversion()),'|',"
         "as.character(packageVersion('lme4')),'|',"
         "as.character(packageVersion('lmerTest')),'|',"
         "as.character(packageVersion('Matrix')))"],
        capture_output=True, text=True).stdout.strip()
    return {
        "python": sys.version.split()[0],
        "python_impl": platform.python_implementation(),
        "numpy": numpy.__version__,
        "scipy": scipy.__version__,
        "R_version_line": rver,
        "R_pkgs (Rver|lme4|lmerTest|Matrix)": pk,
    }


# ----------------------------------------------------------------------------
@app.function(cpu=1.0)
def run_fwer_slice(label: str, rho: float, R: int, nlevel: str = "base",
                   regime: str = "gaussian", want_paths: bool = False):
    import sys, os
    sys.path.insert(0, "/root/sim"); os.chdir("/root/sim")
    import grid, driver
    idx, t = grid.cell_by_label(label, rho=rho, n=nlevel, regime=regime)
    out = driver.run_cell(idx, t, R=R, want_paths=want_paths)
    # trim to essentials
    return {
        "label": label, "config_index": idx, "rho": rho, "nlevel": nlevel,
        "regime": regime, "R": R,
        "fwer_hat": out["fwer_hat"], "fwer_cp_upper95": out["fwer_cp_upper95"],
        "fwer_events": out["fwer_events"], "truth_set_size": len(out["truth_set"]),
        "stage2_rate": out["stage2_rate"], "sec_per_rep": out["sec_per_rep"],
        "claim_rej_rate": out["claim_rej_rate"],
        "paths": out.get("paths"),
    }


# ----------------------------------------------------------------------------
@app.function(cpu=1.0)
def run_gatecal_slice(rho: float, n_nonce: int, R: int):
    import sys, os
    sys.path.insert(0, "/root/sim"); os.chdir("/root/sim")
    import gate_cal_battery as gcb
    res = gcb.run_cell(rho, n_nonce, R)
    all_pass, any_sd_flag = gcb.cell_verdict(res)
    # summarise worst-case across arms/gammas
    worst = {"0.02500": 0.0, "0.00625": 0.0}
    min_sd = 1e9
    for a, rec in res["arms"].items():
        min_sd = min(min_sd, rec["sd_ratio"])
        for g in ("0.02500", "0.00625"):
            worst[g] = max(worst[g], rec["gamma"][g]["cp_upper95"])
    return {"rho": rho, "n_nonce": n_nonce, "R": R, "all_pass": all_pass,
            "any_sd_flag": any_sd_flag, "min_sd_ratio": min_sd,
            "worst_cp_upper": worst, "config_index": res["config_index"]}


# ----------------------------------------------------------------------------
@app.function(cpu=1.0, timeout=1800)
def bench_timing():
    """Measure per-rep wall time on Modal hardware for the full-grid cost model."""
    import sys, os, time
    sys.path.insert(0, "/root/sim"); os.chdir("/root/sim")
    import grid, driver
    out = {}
    # FWER base (F3, rho .1) and escalated (F3, rho .1 esc), plus power esc (P3)
    for tag, (label, rho, nlevel, kind, R) in {
        "fwer_base": ("F3", 0.1, "base", "fwer", 120),
        "fwer_esc": ("F3", 0.1, "esc", "fwer", 80),
        "power_esc": ("P3", 0.5, "esc", "power", 80),
        "gatecal": ("GATECAL", 0.1, "base", "gatecal", 120),
    }.items():
        if kind == "gatecal":
            import gate_cal_battery as gcb
            t0 = time.time(); gcb.run_cell(rho, 96, R); el = time.time() - t0
            out[tag] = {"sec_per_rep": el / R, "R": R}
        else:
            idx, t = grid.cell_by_label(label, rho=rho, n=nlevel, regime="gaussian")
            o = driver.run_cell(idx, t, R=R, want_paths=(kind == "power"))
            out[tag] = {"sec_per_rep": o["sec_per_rep"], "R": R}
    import platform, subprocess
    cpuinfo = ""
    try:
        cpuinfo = subprocess.run(["bash", "-c", "grep -m1 'model name' /proc/cpuinfo"],
                                 capture_output=True, text=True).stdout.strip()
    except Exception:
        pass
    out["_cpu"] = cpuinfo
    return out


# ----------------------------------------------------------------------------
@app.function(cpu=2.0, timeout=3600)
def b2_fixture(n_reps: int = 50):
    """S4.2 fixture-equivalence: balanced closed-form ANOVA (inference.FamilyAnova,
    the pipeline's operative estimator) vs lme4/lmerTest REML on config_index 0
    (F1, gaussian, rho=0, base n), replication_index 0..n_reps-1, every ledger
    family (UCT 10-arm, composite 8-arm).  Tolerances (S4.2): |Dtheta| <= 1e-7,
    rel SE <= 1e-5, rel nu <= 1e-3, |Dp| <= 1e-6.
    """
    import sys, os, json, tempfile, subprocess
    import numpy as np
    sys.path.insert(0, "/root/sim"); os.chdir("/root/sim")
    import pins, seeds, grid, dgm
    from inference import FamilyAnova
    from stats_util import t_cdf

    idx, t = grid.cell_by_label("F1", rho=0.0, n="base", regime="gaussian")
    assert idx == 0, f"fixture config_index expected 0, got {idx}"

    UCT = pins.UCT_ARMS; COMP = pins.COMP_ARMS
    uct_i = {a: i for i, a in enumerate(UCT)}
    comp_i = {a: i for i, a in enumerate(COMP)}
    # registered contrasts as (family, xi, yi, theta0_for_p) ; theta0=0 canonical
    uct_contrasts = ([("UCT", uct_i[c], uct_i["T"], 0.0) for c in pins.CANDIDATES]
                     + [("UCT", uct_i[a], uct_i["S(%s)" % a], 0.0) for a in pins.SH_NAT_ARMS])
    comp_contrasts = ([("COMP", comp_i["H"], comp_i["A2IR"], 0.0)]
                      + [("COMP", comp_i[a], comp_i["S(%s)" % a], 0.0) for a in pins.SH_NONCE_ARMS])

    workdir = tempfile.mkdtemp()
    # ---- generate fixture data + python closed-form; dump long CSVs for R ----
    py = {}  # (rep, fam, xi, yi) -> dict(theta, se, nu, p)
    manifest_lines = ["rep,fam,file"]
    for r in range(n_reps):
        ss = seeds.rep_substreams(0, r)
        Yuct = dgm.gen_uct(t, ss)
        Ycomp, _gate = dgm.gen_composite_and_gate(t, ss, gate_thr=None)
        for fam, Y, contrasts in (("UCT", Yuct, uct_contrasts),
                                  ("COMP", Ycomp, comp_contrasts)):
            an = FamilyAnova(Y)
            for (_f, xi, yi, th0) in contrasts:
                fit = an.contrast(xi, yi)
                p = t_cdf((fit.theta_hat - th0) / fit.se, fit.nu)  # lower-tail one-sided
                py[(r, fam, xi, yi)] = {"theta": fit.theta_hat, "se": fit.se,
                                        "nu": fit.nu, "p": float(p)}
            # dump long form: arm(int), concept(int), seed(int), Y
            A, I, S = Y.shape
            rows = []
            for a in range(A):
                for i in range(I):
                    for s in range(S):
                        rows.append(f"{a},{i},{s},{float(Y[a,i,s])!r}")
            csv = "arm,concept,seed,Y\n" + "\n".join(rows) + "\n"
            fn = os.path.join(workdir, f"rep{r}_{fam}.csv")
            with open(fn, "w") as fh:
                fh.write(csv)
            manifest_lines.append(f"{r},{fam},{fn}")
    with open(os.path.join(workdir, "manifest.csv"), "w") as fh:
        fh.write("\n".join(manifest_lines) + "\n")
    # contrast spec per family (fam,xi,yi) as plain CSV — no jsonlite needed
    cspec_lines = ["fam,xi,yi"]
    for (_f, xi, yi, _t) in uct_contrasts:
        cspec_lines.append(f"UCT,{xi},{yi}")
    for (_f, xi, yi, _t) in comp_contrasts:
        cspec_lines.append(f"COMP,{xi},{yi}")
    with open(os.path.join(workdir, "contrasts.csv"), "w") as fh:
        fh.write("\n".join(cspec_lines) + "\n")

    # ---- R script: fit lmer REML per (rep,fam), contest1D each contrast ----
    #      pure base-R + lme4 + lmerTest CSV I/O (no jsonlite dependency).
    rscript = r'''
suppressMessages({library(lme4); library(lmerTest)})
args <- commandArgs(trailingOnly=TRUE)
wd <- args[1]
man <- read.csv(file.path(wd, "manifest.csv"), colClasses=c("integer","character","character"))
csp <- read.csv(file.path(wd, "contrasts.csv"), colClasses=c("character","integer","integer"))
res <- data.frame(rep=integer(), fam=character(), xi=integer(), yi=integer(),
                  theta=double(), se=double(), nu=double(), p=double())
for (row in seq_len(nrow(man))) {
  rep <- man$rep[row]; fam <- man$fam[row]; f <- man$file[row]
  d <- read.csv(f)
  d$arm <- factor(d$arm); d$concept <- factor(d$concept); d$seed <- factor(d$seed)
  d$ca <- interaction(d$concept, d$arm, drop=TRUE)
  d$sa <- interaction(d$seed, d$arm, drop=TRUE)
  fit <- tryCatch(
    lmer(Y ~ arm + (1|concept) + (1|ca) + (1|seed) + (1|sa),
         data=d, REML=TRUE,
         control=lmerControl(check.conv.singular="ignore",
                             optimizer="bobyqa", optCtrl=list(maxfun=2e5))),
    error=function(e) NULL)
  if (is.null(fit)) next
  fe <- fixef(fit); nm <- names(fe)
  fam_c <- csp[csp$fam==fam, ]
  for (k in seq_len(nrow(fam_c))) {
    xi <- fam_c$xi[k]; yi <- fam_c$yi[k]
    L <- setNames(numeric(length(fe)), nm)
    xn <- paste0("arm", xi); yn <- paste0("arm", yi)
    if (xn %in% nm) L[xn] <- L[xn] + 1
    if (yn %in% nm) L[yn] <- L[yn] - 1
    ct <- tryCatch(contest1D(fit, L, ddf="Satterthwaite"), error=function(e) NULL)
    if (is.null(ct)) next
    est <- ct[["Estimate"]]; se <- ct[["Std. Error"]]; df <- ct[["df"]]
    p_lower <- pt(est/se, df)
    res <- rbind(res, data.frame(rep=rep, fam=fam, xi=xi, yi=yi,
                                 theta=est, se=se, nu=df, p=p_lower))
  }
}
write.csv(res, file.path(wd, "results.csv"), row.names=FALSE)
cat("R_OK rows=", nrow(res), "\n")
'''
    rs_path = os.path.join(workdir, "fit.R")
    with open(rs_path, "w") as fh:
        fh.write(rscript)
    proc = subprocess.run(["Rscript", rs_path, workdir],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        return {"error": "Rscript failed", "stderr": proc.stderr[-4000:],
                "stdout": proc.stdout[-2000:]}
    # ---- read R results.csv back ----
    import csv as _csv
    rres = {}
    with open(os.path.join(workdir, "results.csv")) as fh:
        for row in _csv.DictReader(fh):
            k = (int(row["rep"]), row["fam"], int(row["xi"]), int(row["yi"]))
            rres[k] = {"theta": float(row["theta"]), "se": float(row["se"]),
                       "nu": float(row["nu"]), "p": float(row["p"])}

    # ---- compare ----
    rows = []
    max_dtheta = max_relse = max_relnu = max_dp = 0.0
    n_cmp = 0
    for (r, fam, xi, yi), pv in py.items():
        key = (r, fam, xi, yi)
        if key not in rres:
            continue
        rv = rres[key]
        dtheta = abs(pv["theta"] - rv["theta"])
        relse = abs(pv["se"] - rv["se"]) / max(abs(rv["se"]), 1e-30)
        relnu = abs(pv["nu"] - rv["nu"]) / max(abs(rv["nu"]), 1e-30)
        dp = abs(pv["p"] - rv["p"])
        max_dtheta = max(max_dtheta, dtheta)
        max_relse = max(max_relse, relse)
        max_relnu = max(max_relnu, relnu)
        max_dp = max(max_dp, dp)
        n_cmp += 1
        rows.append({"rep": r, "fam": fam, "xi": xi, "yi": yi,
                     "dtheta": dtheta, "relse": relse, "relnu": relnu, "dp": dp,
                     "py": pv, "r": rv})
    tol = {"dtheta": 1e-7, "relse": 1e-5, "relnu": 1e-3, "dp": 1e-6}
    passed = (max_dtheta <= tol["dtheta"] and max_relse <= tol["relse"]
              and max_relnu <= tol["relnu"] and max_dp <= tol["dp"])
    # worst offenders
    rows.sort(key=lambda x: -x["relnu"])
    return {"n_compared": n_cmp, "n_reps": n_reps,
            "max_dtheta": max_dtheta, "max_relse": max_relse,
            "max_relnu": max_relnu, "max_dp": max_dp,
            "tolerances": tol, "PASS": passed,
            "worst_relnu": rows[:5],
            "worst_relse": sorted(rows, key=lambda x: -x["relse"])[:5],
            "worst_dtheta": sorted(rows, key=lambda x: -x["dtheta"])[:3]}


@app.local_entrypoint()
def main(mode: str = "versions"):
    import json
    if mode == "versions":
        print(json.dumps(versions.remote(), indent=2))
    elif mode == "b2":
        print(json.dumps(b2_fixture.remote(50), indent=2, default=str))
    elif mode == "bench":
        print(json.dumps(bench_timing.remote(), indent=2))
    elif mode == "slices":
        import json as _j
        res = {}
        res["F11_globalnull"] = run_fwer_slice.remote("F11", 0.1, 600, "base", "gaussian")
        res["F3_strongfwer"] = run_fwer_slice.remote("F3", 0.1, 600, "base", "gaussian")
        res["F5_binding"] = run_fwer_slice.remote("F5", 0.1, 600, "base", "gaussian")
        res["P3_power"] = run_fwer_slice.remote("P3", 0.5, 500, "base", "gaussian", True)
        res["gatecal_r01_n96"] = run_gatecal_slice.remote(0.1, 96, 2000)
        print(_j.dumps(res, indent=2, default=str))
