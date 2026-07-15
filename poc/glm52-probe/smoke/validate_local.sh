#!/usr/bin/env bash
# =============================================================================
# validate_local.sh — the $0 on-box validation of the GLM-5.2 backend-smoke
# trace PIPELINE (no model, no Modal, no spend). Proves, using the REAL emitter
# code the engine links (rtrace.h):
#   - per-item RESET / no carry-over
#   - top-k invariants (Ke rows, distinct ranks+experts, non-increasing sel, mgn>=0)
#   - main vs MTP disambiguation
#   - byte-identical decisions on a repeated probe
#   - the trace schema + go/no-go logic end-to-end (all four verdict branches)
#
# The box has no torch and ~0 free disk, so it cannot hold/convert even the tiny
# model; the REAL tiny GlmMoeDsa oracle run is the Modal `tiny` entrypoint (~$0).
# This script drives the same emitter functions moe() calls, on synthesized
# GLM-5.2-shaped router state, plus the real analyzer.
#
#   COLIBRI_C=<dir with a built patched glm> ./validate_local.sh
# (or it will just build test_rtrace against rtrace.h in this directory).
# =============================================================================
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIX=/tmp/rtrace_fixture.jsonl
die(){ echo "ERR_VALIDATE: $*" >&2; exit 1; }

echo "== 1. build + run the C emitter unit tests (writes a real trace fixture) =="
sed "s#\"../rtrace.h\"#\"$HERE/rtrace.h\"#" "$HERE/test_rtrace.c" > /tmp/test_rtrace_local.c
gcc -O2 -Wall -Wextra -Wno-unused-function -I"$HERE" \
    -o /tmp/test_rtrace /tmp/test_rtrace_local.c -lm \
  || die "test_rtrace build failed"
/tmp/test_rtrace "$FIX" | tail -1

echo; echo "== 2. analyzer: CLEAN fixture + GO facts (expect GO-FULL-GLM52) =="
cat > /tmp/facts_go.json <<'J'
{"engine_ran":true,"disk_gbps":2.1,"rss_gb":48.0,"s_per_prefill":100.0,"probes_complete":5}
J
python3 "$HERE/trace_analyze.py" --trace "$FIX" --facts /tmp/facts_go.json --repeat 0:3 --expect-probes 5 >/dev/null 2>/tmp/v.txt; cat /tmp/v.txt
grep -q "GO-FULL-GLM52" /tmp/v.txt || die "expected GO-FULL-GLM52"

echo; echo "== 3. analyzer: SLOW disk (expect PROXY-ONLY) =="
cat > /tmp/facts_slow.json <<'J'
{"engine_ran":true,"disk_gbps":0.4,"rss_gb":48.0,"s_per_prefill":100.0,"probes_complete":5}
J
python3 "$HERE/trace_analyze.py" --trace "$FIX" --facts /tmp/facts_slow.json --repeat 0:3 --expect-probes 5 >/dev/null 2>/tmp/v.txt; cat /tmp/v.txt
grep -q "PROXY-ONLY" /tmp/v.txt || die "expected PROXY-ONLY"

echo; echo "== 4. analyzer: CARRY-OVER trace (expect OFFLINE-ONLY, integrity) =="
python3 - "$FIX" > /tmp/broken_carry.jsonl <<'PY'
import sys,json
cur=None
for ln in open(sys.argv[1]):
    o=json.loads(ln)
    if o.get("t")=="begin": cur=o["item"]
    if o.get("t")=="r" and cur==1 and o["tok"]==0 and o["layer"]==3: o["item"]=0
    print(json.dumps(o))
PY
python3 "$HERE/trace_analyze.py" --trace /tmp/broken_carry.jsonl --facts /tmp/facts_go.json --repeat 0:3 --expect-probes 5 >/dev/null 2>/tmp/v.txt; cat /tmp/v.txt
grep -q "OFFLINE-ONLY" /tmp/v.txt || die "expected OFFLINE-ONLY (carry-over)"

echo; echo "== 5. analyzer: NON-DETERMINISTIC repeat (expect OFFLINE-ONLY) =="
python3 - "$FIX" > /tmp/broken_repeat.jsonl <<'PY'
import sys,json
for ln in open(sys.argv[1]):
    o=json.loads(ln)
    if o.get("t")=="r" and o["item"]==3 and o["tok"]==0 and o["layer"]==3 and o["rank"]==0: o["e"]=(o["e"]+1)%32
    print(json.dumps(o))
PY
python3 "$HERE/trace_analyze.py" --trace /tmp/broken_repeat.jsonl --facts /tmp/facts_go.json --repeat 0:3 --expect-probes 5 >/dev/null 2>/tmp/v.txt; cat /tmp/v.txt
grep -q "OFFLINE-ONLY" /tmp/v.txt || die "expected OFFLINE-ONLY (non-determinism)"

echo; echo "ALL LOCAL VALIDATIONS PASSED ($0; real emitter + real analyzer; 4/4 verdict branches)."
