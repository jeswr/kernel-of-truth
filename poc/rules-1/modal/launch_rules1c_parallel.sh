#!/usr/bin/env bash
# launch_rules1b_parallel.sh — PARALLELIZED rules-1-b full-run launcher
# (registry/experiments/rules-1-c.json; maintainer directive 2026-07-12:
# fan the GPU cell grid across the 4 Modal accounts instead of one serial
# campaign — the voided rules-1 run took ~4.59 h serial on one A10G).
#
# WHAT IT DOES
#   1. Partitions the (arm x seed) cell grid {A1,A3,A5,A7,c1} x {0,1,2}
#      into up to 4 DISJOINT slices by deterministic LPT bin-packing over
#      the pinned planning weights (rules1-manifest.json: A3/c1 = k+1 = 5
#      R1-attempt units; A5 = tput_R1/tput_R3 units — the 1.7B arm; A1/A7 =
#      1). On A10G this yields slice loads ~13.7/13.7/13.7/15.0 of 56
#      units, i.e. a ~1.2-1.4 h critical path vs 4.59 h serial.
#   2. --launch: one BACKGROUND Modal job per account (set -a; source
#      ~/.config/kot/modal{,2,3,4}.env; nohup setsid modal run
#      modal_rules1.py --gpu a10g --cells <slice> --out-root
#      <campaign>/slice-N). nohup+setsid per the standing bd memory (E5
#      lesson): the harness timeout can never orphan an attached client.
#   3. --collect: merges the 4 slice run-records into ONE canonical
#      run-records-rules1b.jsonl via merge_rules1b_slices.py (dedup-safe,
#      deterministic order, per-cell provenance for verdict-gen).
#
# VALIDATION (this box, $0, no Modal, no network):
#   ./launch_rules1b_parallel.sh --dry-plan   # partition + caps + manifest
#   ./launch_rules1b_parallel.sh --mock       # 4 local --cells mock slices
#                                             # + merge, end-to-end green
#
# THE REAL RUN (coordinator ONLY, after the CPU pilot passes + the freeze):
#   poc/rules-1/modal/launch_rules1b_parallel.sh --launch \
#       --pilot-results <dir-with-results-rules1-pilot.json>
#   ...wait for the 4 slice logs to finish (RUNNER_EXIT rc=0), then:
#   poc/rules-1/modal/launch_rules1b_parallel.sh --collect --campaign <dir>
#
# FAIL-CLOSED LAUNCH GATES (--launch refuses otherwise):
#   * registry/experiments/rules-1-c.json status == FROZEN;
#   * the mandatory real-model CPU pilot artifact exists, completed, and
#     CLEARS the frozen host-validity floors (acc(A7) >= 0.30 AND
#     acc(A5) >= 0.15 on its entailed rows — sec-host-validity-gate);
#   * all 4 env files + the modal venv binary exist;
#   * the partition is verified disjoint + complete.
# The ops amendment (pins.harness_manifest = modal_rules1.py
# --print-manifest sha; pins.model_revisions) and maintainer sign-off remain
# the coordinator's responsibility — this script cannot check sign-off.
#
# MODAL HYGIENE (standing bd memory): after killing ANY attached client run
# `modal app stop ap-<id>` UNDER THAT ACCOUNT'S env (source its env file
# first) — a killed client does NOT stop the remote task.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../../.." && pwd)"
RULES1="$REPO_ROOT/poc/rules-1"
WRAPPER="$HERE/modal_rules1.py"
MERGER="$HERE/merge_rules1b_slices.py"
RUNNER="$RULES1/rules1_runner.py"
MANIFEST="$RULES1/inputs/rules1-manifest.json"
RECORD="$REPO_ROOT/registry/experiments/rules-1-c.json"
MODAL_BIN="$REPO_ROOT/poc/modal/.venv/bin/modal"
ENV_DIR="${KOT_ENV_DIR:-$HOME/.config/kot}"
ENV_FILES=("$ENV_DIR/modal.env" "$ENV_DIR/modal2.env"
           "$ENV_DIR/modal3.env" "$ENV_DIR/modal4.env")
INCOMING="$RULES1/results-incoming"

MODE="" GPU="a10g" CAMPAIGN="" PILOT_RESULTS=""
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-plan|--mock|--launch|--collect) MODE="${1#--}";;
    --gpu) GPU="$2"; shift;;
    --campaign) CAMPAIGN="$2"; shift;;
    --pilot-results) PILOT_RESULTS="$2"; shift;;
    -h|--help) sed -n '2,50p' "$0"; exit 0;;
    *) echo "ERR_ARGS: unknown arg $1 (see --help)" >&2; exit 2;;
  esac
  shift
done
[ -n "$MODE" ] || { echo "ERR_ARGS: pick one of --dry-plan / --mock / --launch / --collect" >&2; exit 2; }

# ---------------------------------------------------------------------------
# partition: deterministic LPT over the pinned planning weights.
# stdout lines: "<slice>\t<cells-csv>\t<load-fraction>"
# ---------------------------------------------------------------------------
partition() {  # $1 = full|mock
  python3 - "$MANIFEST" "$GPU" "$1" <<'PY'
import json, sys
man = json.load(open(sys.argv[1])); gpu = sys.argv[2].upper(); mode = sys.argv[3]
dc = man["design_constants_from_frozen_record"]
arms, k, rungs = dc["arms_built_here"], dc["k_retry"], dc["rungs"]
seeds = dc["seeds"] if mode == "full" else man["mock"]["seeds"]
tput = man["planning"]["throughput_tok_per_s"][gpu]

def w(a):  # relative worst-case cost of one (arm, seed) cell in R1-units
    attempts = (k + 1) if a in ("A3", "c1") else 1
    return attempts * tput["R1"] / tput[rungs[a]]

cells = [(a, s) for a in arms for s in seeds]
# LPT: heaviest first, deterministic tie-break (arm order, then seed)
order = sorted(cells, key=lambda c: (-w(c[0]), arms.index(c[0]), c[1]))
bins = [[0.0, []] for _ in range(4)]
for c in order:
    b = min(range(4), key=lambda i: (bins[i][0], i))
    bins[b][0] += w(c[0]); bins[b][1].append(c)
# verify disjoint + complete before printing anything
flat = [c for _, cs in bins for c in cs]
assert len(flat) == len(set(flat)) == len(cells) and set(flat) == set(cells), \
    "ERR_PARTITION: slices not a disjoint cover of the grid"
total = sum(w(a) for a, _ in cells)
for i, (load, cs) in enumerate(bins, 1):
    cs = sorted(cs, key=lambda c: (arms.index(c[0]), c[1]))  # serial order
    print("%d\t%s\t%.4f" % (i, ",".join("%s:%d" % c for c in cs), load / total))
PY
}

print_partition() {  # $1 = full|mock
  echo "== disjoint slice partition ($1 grid, LPT on pinned $GPU planning weights) =="
  while IFS=$'\t' read -r idx cells frac; do
    printf '  slice %s -> %-14s  cells: %s  (%.1f%% of grid load)\n' \
      "$idx" "$(basename "${ENV_FILES[$((idx-1))]}")" "$cells" \
      "$(python3 -c "print(float('$frac')*100)")"
  done < <(partition "$1")
}

check_prereqs() {
  [ -x "$MODAL_BIN" ] || { echo "ERR_PREREQ: $MODAL_BIN missing" >&2; exit 1; }
  for f in "${ENV_FILES[@]}"; do
    [ -f "$f" ] || { echo "ERR_PREREQ: env file $f missing" >&2; exit 1; }
  done
  echo "prereqs OK: modal venv binary + 4 account env files present"
}

# ---------------------------------------------------------------------------
case "$MODE" in

dry-plan)
  echo "=== rules-1-b PARALLEL launcher --dry-plan (\$0, no Modal, no network) ==="
  check_prereqs
  print_partition full
  echo
  echo "== staged-bytes manifest (the pins.harness_manifest ops-amendment value) =="
  python3 "$WRAPPER" --print-manifest
  echo
  echo "== runner cost plan vs frozen caps (whole campaign; slices split the same spend 4 ways) =="
  python3 "$RUNNER" --dry-plan --gpu-class "$(echo "$GPU" | tr a-z A-Z)" \
    --out-dir /tmp/rules1b-dry-plan
  echo
  echo "== exact launch commands the coordinator will fire (background, one per account) =="
  while IFS=$'\t' read -r idx cells _frac; do
    echo "  ( set -a; . ${ENV_FILES[$((idx-1))]}; set +a; \\"
    echo "    exec nohup setsid $MODAL_BIN run $WRAPPER \\"
    echo "      --gpu $GPU --cells $cells --out-root <campaign>/slice-$idx \\"
    echo "  ) > <campaign>/slice-$idx.launch.log 2>&1 &"
  done < <(partition full)
  echo
  echo "DRY-PLAN OK (partition disjoint+complete; nothing launched)"
  ;;

mock)
  echo "=== rules-1-b PARALLEL launcher --mock (\$0, LOCAL stub-LM slices + merge; no Modal) ==="
  MOCK_DIR="${CAMPAIGN:-/tmp/rules1b-parallel-mock}"
  rm -rf "$MOCK_DIR"; mkdir -p "$MOCK_DIR"
  print_partition mock
  SLICE_DIRS=()
  while IFS=$'\t' read -r idx cells _frac; do
    echo "-- mock slice $idx (cells $cells) --"
    python3 "$RUNNER" --mock --cells "$cells" --out-dir "$MOCK_DIR/slice-$idx" \
      > "$MOCK_DIR/slice-$idx.log" 2>&1 \
      || { echo "ERR_MOCK: slice $idx failed — see $MOCK_DIR/slice-$idx.log" >&2
           tail -5 "$MOCK_DIR/slice-$idx.log" >&2; exit 1; }
    tail -2 "$MOCK_DIR/slice-$idx.log" | sed 's/^/   /'
    SLICE_DIRS+=("$MOCK_DIR/slice-$idx")
  done < <(partition mock)
  echo "-- merging ${#SLICE_DIRS[@]} mock slices --"
  python3 "$MERGER" --slices "${SLICE_DIRS[@]}" --out-dir "$MOCK_DIR/merged"
  echo "MOCK GREEN: disjoint slicing + dedup-safe deterministic merge validated end-to-end at \$0"
  ;;

launch)
  echo "=== rules-1-b PARALLEL launch (REAL GPU SPEND — coordinator only) ==="
  check_prereqs
  # GATE 1: the record must be FROZEN (prereg-freeze.py sets status=FROZEN)
  python3 - "$RECORD" <<'PY' || { echo "ERR_GATE_FREEZE: rules-1-b is not FROZEN — run tools/registry/prereg-freeze.py first (coordinator role)" >&2; exit 1; }
import json, sys
sys.exit(0 if json.load(open(sys.argv[1])).get("status") == "FROZEN" else 1)
PY
  echo "gate: rules-1-b status FROZEN — OK"
  # GATE 2: the mandatory real-model CPU pilot passed the host-validity floors
  [ -n "$PILOT_RESULTS" ] || { echo "ERR_GATE_PILOT: --pilot-results <dir> is mandatory (the rules-1 void lesson: no GPU spend before the pilot clears the floors)" >&2; exit 1; }
  python3 - "$PILOT_RESULTS" <<'PY' || exit 1
import glob, json, os, sys
d = sys.argv[1]
res = glob.glob(os.path.join(d, "results-rules1-pilot.json"))
if len(res) != 1:
    sys.exit("ERR_GATE_PILOT: want exactly one results-rules1-pilot.json in %s" % d)
j = json.load(open(res[0]))
if j.get("outcome") != "PILOT-HARNESS-COMPLETE":
    sys.exit("ERR_GATE_PILOT: pilot outcome %r" % j.get("outcome"))
rows = [json.loads(l) for l in open(os.path.join(d, j["records_file"])) if l.strip()]
acc = {}
for arm in ("A7", "A5"):
    ent = [r for r in rows if r["arm"] == arm and r["cell"] == "entailed"]
    if not ent:
        sys.exit("ERR_GATE_PILOT: no entailed %s rows in the pilot — floors unevaluable" % arm)
    acc[arm] = sum(r["item_correct_ext"] for r in ent) / len(ent)
floors = {"A7": 0.85, "A5": 0.75}  # frozen sec-host-validity-gate floors
for arm, floor in floors.items():
    print("pilot acc(%s) = %.4f (floor %.2f, n=%d)"
          % (arm, acc[arm], floor, len([r for r in rows if r["arm"] == arm and r["cell"] == "entailed"])))
    if acc[arm] < floor:
        sys.exit("ERR_GATE_PILOT: pilot acc(%s)=%.4f below the frozen host-validity floor %.2f — DO NOT SPEND GPU" % (arm, acc[arm], floor))
print("gate: pilot host-validity floors cleared — OK")
PY
  # campaign dir + plan record
  STAMP="$(date -u +%Y%m%d-%H%M%S)"
  CAMPAIGN="${CAMPAIGN:-$INCOMING/$STAMP-rules1b-parallel}"
  mkdir -p "$CAMPAIGN"
  print_partition full | tee "$CAMPAIGN/partition.txt"
  MAN_SHA="$(python3 "$WRAPPER" --print-manifest | tail -1)"
  echo "$MAN_SHA" | tee "$CAMPAIGN/staged-manifest-sha.txt"
  echo "REMINDER: the sha above MUST equal the ops-amended pins.harness_manifest in the FROZEN record."
  PIDS=()
  while IFS=$'\t' read -r idx cells _frac; do
    envf="${ENV_FILES[$((idx-1))]}"
    mkdir -p "$CAMPAIGN/slice-$idx"
    (
      set -a; . "$envf"; set +a
      exec nohup setsid "$MODAL_BIN" run "$WRAPPER" \
        --gpu "$GPU" --cells "$cells" --out-root "$CAMPAIGN/slice-$idx"
    ) > "$CAMPAIGN/slice-$idx.launch.log" 2>&1 &
    pid=$!
    PIDS+=("$pid")
    echo "launched slice $idx: account $(basename "$envf") pid $pid cells $cells"
    echo "{\"slice\": $idx, \"env\": \"$(basename "$envf")\", \"pid\": $pid, \"gpu\": \"$GPU\", \"cells\": \"$cells\"}" >> "$CAMPAIGN/launch-state.jsonl"
  done < <(partition full)
  echo
  echo "all 4 slices launched in the background (nohup+setsid)."
  echo "  watch:   tail -f $CAMPAIGN/slice-*.launch.log"
  echo "  collect: $0 --collect --campaign $CAMPAIGN"
  echo "  HYGIENE: if you kill any client, run 'modal app stop ap-<id>' under"
  echo "           THAT account's env (grep ap- from its launch.log) — a dead"
  echo "           client does NOT stop the remote task (bd memory, E5 lesson)."
  ;;

collect)
  [ -n "$CAMPAIGN" ] || { echo "ERR_ARGS: --collect requires --campaign <dir>" >&2; exit 2; }
  echo "=== rules-1-b PARALLEL collect/merge ($CAMPAIGN) ==="
  SLICE_DIRS=()
  for i in 1 2 3 4; do
    # newest <stamp>-modal unpack inside the slice root (modal_rules1.py wrote it)
    d="$(ls -d "$CAMPAIGN/slice-$i"/*-modal 2>/dev/null | sort | tail -1 || true)"
    [ -n "$d" ] || { echo "ERR_COLLECT: no *-modal result dir under $CAMPAIGN/slice-$i (slice still running or failed — see slice-$i.launch.log)" >&2; exit 1; }
    rc="$(cat "$d/RUNNER_EXIT" 2>/dev/null || echo missing)"
    [ "$rc" = "rc=0" ] || { echo "ERR_COLLECT: slice $i RUNNER_EXIT '$rc' != rc=0 ($d)" >&2; exit 1; }
    SLICE_DIRS+=("$d")
  done
  python3 "$MERGER" --slices "${SLICE_DIRS[@]}" --out-dir "$CAMPAIGN/merged"
  echo
  echo "canonical rows for the grade: $CAMPAIGN/merged/run-records-rules1b.jsonl"
  echo "per-cell provenance:          $CAMPAIGN/merged/merge-manifest-rules1b.json"
  echo "results are NOT auto-committed — review, then hand to verdict-gen/analyst."
  ;;
esac
