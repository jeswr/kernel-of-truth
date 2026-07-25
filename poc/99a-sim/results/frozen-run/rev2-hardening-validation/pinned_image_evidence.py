"""Rev6 (review item 4): reproduce the 320-fit bit-identity + cap scan AND the
Rev6 hardening suite under the PAID-IMAGE numpy/scipy pins (NumPy 2.1.3 /
SciPy 1.14.1, Python 3.12) — the pass-cap behaviour depends on L-BFGS-B, so the
reviewer's local NumPy 2.0.2 / SciPy 1.13.1 reproduction is NOT sufficient.

This is a short CPU-only verification run on the PINNED numeric stack, NOT the
paid grid rerun.  It mounts the sim dir at its real local path so the harness's
absolute paths work unchanged, runs both scripts as subprocesses, captures
stdout, and returns it for the local evidence log.

PROVENANCE (2026-07-25): BOTH Modal workspaces were over their spend limit, so
the recorded evidence (evidence-pinned-image-rev6.log) was produced instead
with a LOCAL micromamba env pinned to the SAME numeric stack —
`micromamba create -n kot312 -c conda-forge python=3.12 numpy=2.1.3 scipy=1.14.1`
— then `.../envs/kot312/bin/python bitid_vs_original.py` + `rev2_tests.py`.
Identical pins (Python 3.12.13 / NumPy 2.1.3 / SciPy 1.14.1); the env was
removed after capture to protect the box disk.  This Modal script is the
canonical recipe for when Modal budget is available again.

Run:  ./venv/bin/python -m modal run \
        results/frozen-run/rev2-hardening-validation/pinned_image_evidence.py
"""
import modal

SIM_LOCAL = "/home/ec2-user/css/kernel/kernel-of-truth/poc/99a-sim"
REL = "results/frozen-run/rev2-hardening-validation"

# EXACT paid-image numeric pins (kot_99a_grid_v2.py image: numpy==2.1.3,
# scipy==1.14.1, add_python="3.12").  The R packages in the grid image are
# irrelevant to the estimator's numpy/scipy path, so this minimal image
# reproduces the load-bearing pins faithfully.
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("numpy==2.1.3", "scipy==1.14.1")
    .add_local_dir(
        SIM_LOCAL, remote_path=SIM_LOCAL,
        ignore=["venv/**", "__pycache__/**", "*.pyc", ".git/**",
                "results/frozen-run/grid-run*/**", "results/frozen-run/opus-runs/**"],
    )
)
app = modal.App("kot-99a-rev6-pinned-evidence", image=image)


@app.function(cpu=4.0, timeout=1800)
def run_evidence():
    import os, sys, subprocess
    import numpy, scipy
    hdr = ("[pinned-image] python=%s numpy=%s scipy=%s\n"
           % (sys.version.split()[0], numpy.__version__, scipy.__version__))
    out = [hdr]
    for script in ("bitid_vs_original.py", "rev2_tests.py"):
        path = os.path.join(SIM_LOCAL, REL, script)
        r = subprocess.run([sys.executable, path], capture_output=True, text=True)
        out.append("\n==================== %s (exit %d) ====================\n"
                   % (script, r.returncode))
        out.append(r.stdout)
        if r.stderr.strip():
            out.append("\n--- stderr ---\n" + r.stderr)
        out.append("\n[%s EXIT CODE = %d]\n" % (script, r.returncode))
    return "".join(out), {}


@app.local_entrypoint()
def main():
    text, _ = run_evidence.remote()
    outp = SIM_LOCAL + "/" + REL + "/evidence-pinned-image-rev6.log"
    with open(outp, "w") as fh:
        fh.write(text)
    print(text)
    print("\nWROTE", outp)
