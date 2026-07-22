"""Modal app for the Rev10/R10a B2 fix validation + (gated) full frozen grid.

Same pinned image as kot_99a_modal.py (reused from cache, no rebuild):
CPython 3.12 + numpy 2.1.3 + scipy 1.14.1 + R 4.4.1 + lme4 1.1-35.5 + lmerTest 3.1-3.

Family (B) composite engine = reml_composite.CompositeREML (exact 6-component REML,
R10a).  Oracle for family (B) = lme4 6-component model WITH the reviewed-only
reviewer block (0 + rev | reviewer_id).  Families A/C/D unchanged.
"""
import modal

SIM_LOCAL = "/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim"

image = (
    modal.Image.from_registry("rocker/r-ver:4.4.1", add_python="3.12")
    .pip_install("numpy==2.1.3", "scipy==1.14.1")
    .run_commands(
        "R -q -e \"install.packages('remotes')\"",
        "R -q -e \"remotes::install_version('lme4', version='1.1-35.5', upgrade='never', dependencies=TRUE)\"",
        "R -q -e \"remotes::install_version('lmerTest', version='3.1-3', upgrade='never', dependencies=TRUE)\"",
    )
    .add_local_dir(
        SIM_LOCAL, remote_path="/root/sim",
        ignore=["venv/**", "__pycache__/**", "*.pyc", "results/**", ".git/**"],
    )
)
app = modal.App("kot-99a-r10a", image=image)


@app.function(cpu=2.0, timeout=3600)
def b2_fixture_r10a(n_reps: int = 50):
    """S4.2 fixture (R10a): config 0, reps 0..n_reps-1, all ledger families.
    UCT (A) = FamilyAnova vs 5-comp lme4; COMPOSITE (B) = exact-REML vs 6-comp lme4."""
    import sys, os, csv, tempfile, subprocess
    import numpy as np
    sys.path.insert(0, "/root/sim"); os.chdir("/root/sim")
    import pins, seeds, grid, dgm
    from inference import FamilyAnova
    from stats_util import t_cdf
    import reml_composite

    idx, t = grid.cell_by_label("F1", rho=0.0, n="base", regime="gaussian")
    assert idx == 0
    UCT = pins.UCT_ARMS; COMP = pins.COMP_ARMS
    uct_i = {a: i for i, a in enumerate(UCT)}; comp_i = {a: i for i, a in enumerate(COMP)}
    uct_contrasts = ([(uct_i[c], uct_i["T"]) for c in pins.CANDIDATES]
                     + [(uct_i[a], uct_i["S(%s)" % a]) for a in pins.SH_NAT_ARMS])
    comp_contrasts = ([(comp_i["H"], comp_i["A2IR"])]
                      + [(comp_i[a], comp_i["S(%s)" % a]) for a in pins.SH_NONCE_ARMS])
    rev_off = {COMP.index(a): off for off, a in enumerate(pins.REVIEWED_ARMS)}
    reviewed = set(rev_off.keys())

    CR = reml_composite.build_for_cell(t)
    CRu = reml_composite.build_for_uct(t)          # DIAGNOSTIC exact-REML for UCT
    wd = tempfile.mkdtemp()
    py = {}
    man = ["rep,fam,file"]
    for r in range(n_reps):
        ss = seeds.rep_substreams(0, r)
        Yuct = dgm.gen_uct(t, ss)
        Ycomp, _ = dgm.gen_composite_and_gate(t, ss, gate_thr=None)
        # ---- UCT engine = FamilyAnova (current, R10a-untouched) ----
        an = FamilyAnova(Yuct)
        for (xi, yi) in uct_contrasts:
            fit = an.contrast(xi, yi)
            p = t_cdf(fit.theta_hat / fit.se, fit.nu)
            py[(r, "UCT", xi, yi)] = (fit.theta_hat, fit.se, fit.nu, float(p))
        # ---- UCT DIAGNOSTIC engine = exact-REML (consumer block) ----
        CRu.fit(Yuct)
        for (xi, yi) in uct_contrasts:
            fit = CRu.contrast(xi, yi)
            p = t_cdf(fit.theta_hat / fit.se, fit.nu)
            py[(r, "UCT_REML", xi, yi)] = (fit.theta_hat, fit.se, fit.nu, float(p))
        A, I, S = Yuct.shape
        # consumer rotation (DGM gen_uct): consumer_id = (uct_arm_index + i) % N_CONSUMERS,
        # present on ALL 10 arms (a FULL block -> balanced across arms).
        with open(os.path.join(wd, f"rep{r}_UCT.csv"), "w") as fh:
            fh.write("arm,concept,seed,consumer_id,Y\n")
            for a in range(A):
                for i in range(I):
                    cid = (a + i) % pins.N_CONSUMERS
                    for s in range(S):
                        fh.write(f"{a},{i},{s},{cid},{float(Yuct[a,i,s])!r}\n")
        man.append(f"{r},UCT,{os.path.join(wd, f'rep{r}_UCT.csv')}")
        # ---- COMPOSITE engine = exact-REML ----
        CR.fit(Ycomp)
        for (xi, yi) in comp_contrasts:
            fit = CR.contrast(xi, yi)
            p = t_cdf(fit.theta_hat / fit.se, fit.nu)
            py[(r, "COMP", xi, yi)] = (fit.theta_hat, fit.se, fit.nu, float(p))
        A, I, S = Ycomp.shape
        with open(os.path.join(wd, f"rep{r}_COMP.csv"), "w") as fh:
            fh.write("arm,concept,seed,rev,reviewer_id,Y\n")
            for a in range(A):
                is_rev = 1 if a in reviewed else 0
                for i in range(I):
                    rid = (rev_off[a] + i) % pins.N_REVIEWERS if is_rev else 0
                    for s in range(S):
                        fh.write(f"{a},{i},{s},{is_rev},{rid},{float(Ycomp[a,i,s])!r}\n")
        man.append(f"{r},COMP,{os.path.join(wd, f'rep{r}_COMP.csv')}")
    with open(os.path.join(wd, "manifest.csv"), "w") as fh:
        fh.write("\n".join(man) + "\n")
    with open(os.path.join(wd, "uct_contrasts.csv"), "w") as fh:
        fh.write("xi,yi\n" + "\n".join(f"{x},{y}" for x, y in uct_contrasts) + "\n")
    with open(os.path.join(wd, "comp_contrasts.csv"), "w") as fh:
        fh.write("xi,yi\n" + "\n".join(f"{x},{y}" for x, y in comp_contrasts) + "\n")

    rscript = r'''
suppressMessages({library(lme4); library(lmerTest)})
args <- commandArgs(trailingOnly=TRUE); wd <- args[1]
man <- read.csv(file.path(wd,"manifest.csv"), colClasses=c("integer","character","character"))
uc <- read.csv(file.path(wd,"uct_contrasts.csv")); cc <- read.csv(file.path(wd,"comp_contrasts.csv"))
res <- data.frame(rep=integer(),fam=character(),xi=integer(),yi=integer(),
                  theta=double(),se=double(),nu=double(),p=double())
ctl <- lmerControl(check.conv.singular="ignore", optimizer="bobyqa", optCtrl=list(maxfun=2e5))
docontrasts <- function(fit, arms) {
  fe <- fixef(fit); nm <- names(fe); out <- list()
  for (k in seq_len(nrow(arms))) {
    xi <- arms$xi[k]; yi <- arms$yi[k]
    L <- setNames(numeric(length(fe)), nm)
    xn <- paste0("arm",xi); yn <- paste0("arm",yi)
    if (xn %in% nm) L[xn] <- L[xn]+1; if (yn %in% nm) L[yn] <- L[yn]-1
    ct <- tryCatch(contest1D(fit,L,ddf="Satterthwaite"), error=function(e) NULL)
    if (is.null(ct)) next
    est<-ct[["Estimate"]]; se<-ct[["Std. Error"]]; df<-ct[["df"]]
    out[[length(out)+1]] <- list(xi=xi,yi=yi,theta=est,se=se,nu=df,p=pt(est/se,df))
  }
  out
}
for (row in seq_len(nrow(man))) {
  rep<-man$rep[row]; fam<-man$fam[row]; d<-read.csv(man$file[row])
  d$arm<-factor(d$arm); d$concept<-factor(d$concept); d$seed<-factor(d$seed)
  d$ca<-interaction(d$concept,d$arm,drop=TRUE); d$sa<-interaction(d$seed,d$arm,drop=TRUE)
  if (fam=="UCT") {
    d$consumer_id<-factor(d$consumer_id)
    fit<-tryCatch(lmer(Y~arm+(1|concept)+(1|ca)+(1|seed)+(1|sa)+(1|consumer_id),data=d,REML=TRUE,control=ctl),error=function(e)NULL)
    arms<-uc
  } else {
    d$reviewer_id<-factor(d$reviewer_id)
    fit<-tryCatch(lmer(Y~arm+(1|concept)+(1|ca)+(1|seed)+(1|sa)+(0+rev|reviewer_id),
                       data=d,REML=TRUE,control=ctl),error=function(e)NULL)
    arms<-cc
  }
  if (is.null(fit)) next
  for (o in docontrasts(fit,arms))
    res<-rbind(res,data.frame(rep=rep,fam=fam,xi=o$xi,yi=o$yi,theta=o$theta,se=o$se,nu=o$nu,p=o$p))
}
write.csv(res, file.path(wd,"results.csv"), row.names=FALSE)
cat("R_OK rows=",nrow(res),"\n")
'''
    with open(os.path.join(wd, "fit.R"), "w") as fh:
        fh.write(rscript)
    proc = subprocess.run(["Rscript", os.path.join(wd, "fit.R"), wd],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        return {"error": "Rscript failed", "stderr": proc.stderr[-4000:], "stdout": proc.stdout[-1500:]}
    rres = {}
    with open(os.path.join(wd, "results.csv")) as fh:
        for row in csv.DictReader(fh):
            rres[(int(row["rep"]), row["fam"], int(row["xi"]), int(row["yi"]))] = (
                float(row["theta"]), float(row["se"]), float(row["nu"]), float(row["p"]))

    def summarize(fam, oracle_fam=None):
        oracle_fam = oracle_fam or fam
        md = mrs = mrn = mp = 0.0; n = 0; worst = None
        for k, (th, se, nu, p) in py.items():
            if k[1] != fam:
                continue
            ok = (k[0], oracle_fam, k[2], k[3])
            if ok not in rres:
                continue
            rt, rse, rnu, rp = rres[ok]
            dt = abs(th - rt); rs = abs(se - rse) / max(abs(rse), 1e-30)
            rn = abs(nu - rnu) / max(abs(rnu), 1e-30); dp = abs(p - rp)
            if rn > mrn or worst is None:
                worst = dict(key=k, py=(th, se, nu, p), r=(rt, rse, rnu, rp),
                             dt=dt, rs=rs, rn=rn, dp=dp)
            md = max(md, dt); mrs = max(mrs, rs); mrn = max(mrn, rn); mp = max(mp, dp); n += 1
        return dict(n=n, max_dtheta=md, max_relse=mrs, max_relnu=mrn, max_dp=mp, worst=worst)

    tol = {"dtheta": 1e-7, "relse": 1e-5, "relnu": 1e-3, "dp": 1e-6}
    out = {"n_reps": n_reps, "tolerances": tol, "families": {}}
    out["families"]["UCT"] = summarize("UCT")               # FamilyAnova vs 6-comp oracle
    out["families"]["UCT_REML"] = summarize("UCT_REML", oracle_fam="UCT")  # exact-REML vs same oracle
    out["families"]["COMP"] = summarize("COMP")             # exact-REML vs 6-comp oracle
    # PASS uses the ENGINES the frozen run would use: UCT=FamilyAnova, COMP=exact-REML
    allmd = allrs = allrn = allp = 0.0
    for fam in ("UCT", "COMP"):
        s = out["families"][fam]
        allmd = max(allmd, s["max_dtheta"]); allrs = max(allrs, s["max_relse"])
        allrn = max(allrn, s["max_relnu"]); allp = max(allp, s["max_dp"])
    out["overall_current_engines"] = {"max_dtheta": allmd, "max_relse": allrs,
                                      "max_relnu": allrn, "max_dp": allp}
    out["PASS"] = (allmd <= tol["dtheta"] and allrs <= tol["relse"]
                   and allrn <= tol["relnu"] and allp <= tol["dp"])
    # what PASS WOULD be if UCT also used exact-REML
    s = out["families"]["UCT_REML"]; c = out["families"]["COMP"]
    out["PASS_if_uct_exact_reml"] = (
        max(s["max_dtheta"], c["max_dtheta"]) <= tol["dtheta"]
        and max(s["max_relse"], c["max_relse"]) <= tol["relse"]
        and max(s["max_relnu"], c["max_relnu"]) <= tol["relnu"]
        and max(s["max_dp"], c["max_dp"]) <= tol["dp"])
    return out


@app.local_entrypoint()
def main(mode: str = "b2", n: int = 50):
    import json
    if mode == "b2":
        print(json.dumps(b2_fixture_r10a.remote(n), indent=2, default=str))
