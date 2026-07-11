#!/usr/bin/env bash
# f2b-transfer stage-2 MOCK check — $0, no GPU, no network.
# Runs the runner in --mock, pipes the mock records through the PINNED
# analysis (analysis/f2b_transfer.py), and asserts the analysis-consumable
# fields resolve (stage-1 fields + stage-2 arm fields + gates). This is the
# coordinator's pre-spend "green mock" gate (frozen stage_discipline:
# reuse-check + dry-plan + mock precede the final run).
#
# Run-vs-audit note: this script VALIDATES pipeline shape only; the analysis
# output on mock records is labelled MOCK and is never a measurement or a
# verdict input.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
OUT="${1:-/tmp/f2bt-mock-$$}"

echo "== 1/3 pinned analysis selftest =="
python3 "$REPO/analysis/f2b_transfer.py" --selftest

echo "== 2/3 mock run =="
python3 "$HERE/f2bt_runner.py" --out-dir "$OUT" --mock

echo "== 3/3 mock records through the PINNED analysis =="
python3 - "$OUT" "$REPO" <<'EOF'
import json, subprocess, sys
out, repo = sys.argv[1], sys.argv[2]
recs = open(out + "/run-records-f2bt-mock.jsonl", "rb").read()
p = subprocess.run([sys.executable, repo + "/analysis/f2b_transfer.py"],
                   input=recs, capture_output=True)
if p.returncode != 0:
    sys.exit("ANALYSIS FAILED on mock records:\n" + p.stderr.decode())
a = json.loads(p.stdout)
need_analysis = ["external_endorsement", "external_endorsement_lb",
                 "stage1_endorsement_fail", "n_eval_items",
                 "engagement_decidable_fraction",
                 "engagement_attempt0_reject_rate",
                 "engagement_final_differs_attempt0",
                 "acc_ext_alone_r1", "acc_ext_alone_r3", "acc_ext_verify_k4",
                 "acc_ext_shuffled_k4", "acc_ext_gloss_k4",
                 "acc_mem_alone_r1", "acc_mem_verify_k4", "effect_size",
                 "primary_lower_onesided95", "primary_reject", "lift_mem",
                 "dual_scoring_gap", "shuffled_recovery_fraction",
                 "seed_sign_consistent", "tost_equivalence_pass"]
need_gates = ["adjudication_valid", "instrument_valid", "engagement_valid",
              "headroom_valid", "separation_valid"]
missing = ([k for k in need_analysis if k not in a["analysis"]]
           + [k for k in need_gates if k not in a["gates"]])
if missing:
    sys.exit("MOCK ANALYSIS INCOMPLETE — unresolved fields: %s" % missing)
holm = a["analysis"]["holm"]
for k in ("beats_gloss_self_verify", "shuffled_low_recovery",
          "noninferiority_vs_r3"):
    assert k in holm and k + "_p" in holm, "missing Holm member " + k
print("MOCK-ANALYSIS-CONSUMABLE: all stage-1 + stage-2 fields resolved (MOCK, never a measurement)")
print(json.dumps({"gates": a["gates"],
                  "n_eval_items": a["analysis"]["n_eval_items"],
                  "engagement_decidable_fraction":
                      a["analysis"]["engagement_decidable_fraction"],
                  "engagement_attempt0_reject_rate":
                      a["analysis"]["engagement_attempt0_reject_rate"]},
                 indent=1, sort_keys=True))
EOF
echo "GREEN MOCK: $OUT"
