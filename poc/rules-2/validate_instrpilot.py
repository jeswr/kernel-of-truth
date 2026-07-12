#!/usr/bin/env python3
"""$0 validation of the RULES-2 INSTRUMENT PILOT (PROPOSED-ASM-1814..1819).

Produces poc/rules-2/results/instrpilot-mock-validation.json — the PINNED
artifact modal_instrpilot.py's launch gate requires (validate_mock.py
pattern). Three checks, all CPU, all $0:

  1. NORMAL mock (planted stub gradient): the pilot must resolve
     PILOT-PASS-WITH-FLAGS with IP-1/2/3 pass and the IP-4 B4-vacuity flag
     FIRING (the stub goes through the REAL imported licensed_rejection,
     which abstains unconditionally on the entity surface —
     PROPOSED-ASM-1808 — so attempts==1 everywhere; the flag firing in mock
     is the DETECTION channel working, not a measurement).
  2. DEGENERATE mock (--mock-degenerate zeroes the planted gradient): the
     pilot must resolve PILOT-FAIL with IP-1 failing and exit rc=3 — the
     pilot's own gates have teeth (a pilot that cannot fail is not a gate).
     IP-3 is NOT asserted here: under a fully degenerate stub its paired
     gap is noise-dominated, and IP-3 is only meaningful when IP-1 passes.
  3. --dry-plan green: worst-case cost <= the $2 pilot cap (rc=0).

The artifact pins the CURRENT pilot staged-bytes sha (modal_instrpilot.py
manifest) AND asserts the CAMPAIGN staged-bytes sha (modal_rules2.py
manifest) is unchanged by the pilot build — fail closed if the pilot ever
perturbs the frozen-candidate campaign surface.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable

# the campaign staged-bytes sha at REWORK-3 build time (README / DRAFT
# record pins.harness_manifest placeholder) — the pilot build must not
# change it.
CAMPAIGN_SHA_AT_BUILD = \
    "d37640b2fac8b14198a9f9db60e3f97e6abd84639cb34979e383abd3f7b892ce"


def run(args, expect_rc):
    p = subprocess.run([PY] + args, capture_output=True, text=True)
    sys.stdout.write(p.stdout)
    sys.stdout.write(p.stderr)
    if p.returncode != expect_rc:
        raise SystemExit("ERR_VALIDATE: %r exited rc=%d (want %d)"
                         % (" ".join(args), p.returncode, expect_rc))
    return p


def manifest_sha(wrapper):
    p = subprocess.run([PY, os.path.join(_HERE, "modal", wrapper),
                        "--print-manifest"], capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit("ERR_VALIDATE: %s --print-manifest failed:\n%s"
                         % (wrapper, p.stderr))
    return p.stdout.strip().rsplit(" ", 1)[-1]


def main():
    checks = {}
    with tempfile.TemporaryDirectory() as td:
        # 1. normal mock -> PASS-WITH-FLAGS, rc=0
        run([os.path.join(_HERE, "instr_pilot.py"), "--out-dir",
             os.path.join(td, "mock"), "--mock"], expect_rc=0)
        res = json.load(open(os.path.join(td, "mock",
                                          "instrpilot-result-mock.json")))
        g = res["gates"]
        assert res["mode"] == "MOCK"
        assert res["verdict"] == "PILOT-PASS-WITH-FLAGS", res["verdict"]
        assert g["ip1_separation"]["pass"] is True
        assert g["ip2_audit_teeth"]["pass"] is True
        assert g["ip2_audit_teeth"]["real_lookup"]["recovered"] == 0
        assert g["ip2_audit_teeth"]["gate_fires_on_planted_exploiter"] is True
        assert g["ip3_c1p_control"]["pass"] is True
        assert g["ip4_b4_vacuity_flag"]["b4_vacuous"] is True
        assert g["ip4_b4_vacuity_flag"]["attempts_values"] == [1]
        checks["mock_normal"] = {
            "verdict": res["verdict"],
            "ip1_pass": True, "ip2_pass": True, "ip3_pass": True,
            "ip4_b4_vacuous_flag_fired": True,
            "b0_acc_MOCK": g["ip1_separation"]["b0"]["acc"],
            "b2p_acc_MOCK": g["ip1_separation"]["b2_pilot"]["acc"],
            "c1p_acc_MOCK": g["ip3_c1p_control"]["c1p"]["acc"],
            "planted_recovered_acc": g["ip2_audit_teeth"]
            ["planted_exploiter"]["recovered_acc"],
            "sout_prompt_surface_sha256":
                res["sout_prompt_surface_sha256"]}

        # 2. degenerate mock -> PILOT-FAIL via IP-1, rc=3 (pilot teeth)
        run([os.path.join(_HERE, "instr_pilot.py"), "--out-dir",
             os.path.join(td, "deg"), "--mock", "--mock-degenerate"],
            expect_rc=3)
        deg = json.load(open(os.path.join(
            td, "deg", "instrpilot-result-mock-deg.json")))
        assert deg["verdict"] == "PILOT-FAIL", deg["verdict"]
        assert deg["gates"]["ip1_separation"]["pass"] is False
        checks["mock_degenerate_teeth"] = {
            "verdict": deg["verdict"], "ip1_failed_as_required": True,
            "note": "IP-3 deliberately unasserted here (noise-dominated "
                    "when IP-1 is degenerate; IP-3 is conditional on a "
                    "live IP-1 channel)"}

        # 3. dry-plan green under the $2 cap (default A10G)
        p = run([os.path.join(_HERE, "instr_pilot.py"), "--out-dir",
                 os.path.join(td, "dry"), "--dry-plan"], expect_rc=0)
        checks["dry_plan"] = {
            "rc": 0,
            "stdout_tail": p.stdout.strip().splitlines()[-3:]}

    pilot_sha = manifest_sha("modal_instrpilot.py")
    campaign_sha = manifest_sha("modal_rules2.py")
    if campaign_sha != CAMPAIGN_SHA_AT_BUILD:
        raise SystemExit("ERR_VALIDATE: the CAMPAIGN staged-bytes sha "
                         "changed (%s != %s) — the pilot build must not "
                         "perturb the frozen-candidate campaign surface"
                         % (campaign_sha[:16], CAMPAIGN_SHA_AT_BUILD[:16]))

    out = {
        "artifact": "rules-2 INSTRUMENT PILOT mock validation "
                    "(PROPOSED-ASM-1814..1819)",
        "green": True,
        "checks": checks,
        "pilot_harness_manifest_sha256": pilot_sha,
        "campaign_harness_manifest_sha256_unchanged": campaign_sha,
        "semantics": "mechanics validation ONLY — every number above is "
                     "MOCK and licenses nothing; the pinned sha gates the "
                     "modal_instrpilot.py GPU launch (validate_mock.py "
                     "pattern)",
    }
    path = os.path.join(_HERE, "results", "instrpilot-mock-validation.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print("\nGREEN -> %s\n  pilot sha    %s\n  campaign sha %s (unchanged)"
          % (path, pilot_sha, campaign_sha))


if __name__ == "__main__":
    main()
