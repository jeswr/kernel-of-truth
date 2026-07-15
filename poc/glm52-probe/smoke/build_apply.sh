#!/usr/bin/env bash
# =============================================================================
# build_apply.sh — clone colibri @ pinned commit, apply the read-only router
# TRACE patch (rtrace.h + rtrace-add-path.patch), build, and prove inert-by-
# default. Mirrors poc/glm52-probe/f1k-harness/bringup.sh, for the GLM-5.2
# backend-feasibility SMOKE. EXPLORATORY infra ($0 build; no model, no instance).
#
# The colibri clone URL is coordinator-supplied (COLIBRI_GIT_URL) — the repo
# pins the engine by commit sha only. Reference: github.com/JustVugg/colibri.
#
#   COLIBRI_GIT_URL=<url> ./build_apply.sh [workdir]
#
# Fail-closed throughout. Produces <workdir>/colibri/c/glm (+ iobench).
# =============================================================================
set -euo pipefail

COLIBRI_COMMIT="a78a06fc5acc4b0dc0f9ef03987c66b0559d1250"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK="${1:-${COLIBRI_WORK:-$HOME/colibri-smoke}}"
ARCH="${ARCH:-native}"

die(){ echo "ERR_SMOKE_BUILD: $*" >&2; exit 1; }
step(){ echo; echo "== $* =="; }

[ -n "${COLIBRI_GIT_URL:-}" ] || die "COLIBRI_GIT_URL unset (coordinator-supplied; ref github.com/JustVugg/colibri)"
for t in git gcc make objdump python3 sha256sum; do command -v "$t" >/dev/null || die "missing tool: $t"; done

step "1/5 clone colibri @ $COLIBRI_COMMIT"
mkdir -p "$WORK"
if [ ! -d "$WORK/colibri/.git" ]; then git clone "$COLIBRI_GIT_URL" "$WORK/colibri"; fi
cd "$WORK/colibri"
git fetch --all --quiet || true
git checkout --quiet "$COLIBRI_COMMIT" || die "pinned commit not found"
[ "$(git rev-parse HEAD)" = "$COLIBRI_COMMIT" ] || die "HEAD != pinned commit"
cp c/glm.c /tmp/glm_pristine_smoke.c   # snapshot for the equivalence proof

step "2/5 place rtrace.h + apply the glm.c/Makefile patch"
cp "$HERE/rtrace.h" c/rtrace.h
cp "$HERE/test_rtrace.c" c/tests/test_rtrace.c
git apply --check "$HERE/rtrace-add-path.patch" || die "patch does not apply cleanly at the pinned commit"
git apply "$HERE/rtrace-add-path.patch"
echo "patch applied"

step "3/5 build engine + iobench + C emitter unit tests"
( cd c && make -s glm ARCH="$ARCH" && make -s iobench ) || die "build failed"
( cd c && gcc -O2 -Wall -Wextra -Wno-unused-function -o /tmp/test_rtrace tests/test_rtrace.c -lm ) || die "test build failed"
OUT="$(/tmp/test_rtrace /tmp/rtrace_fixture.jsonl 2>&1)" || { echo "$OUT"; die "test_rtrace failed"; }
echo "$OUT" | grep -q "ALL TESTS PASSED" || { echo "$OUT"; die "test_rtrace not green"; }
echo "test_rtrace: ALL TESTS PASSED"

step "4/5 inert-by-default (RTRACE unset) machine-level equivalence"
cd c
gcc -O2 -march="$ARCH" -I. -c /tmp/glm_pristine_smoke.c -o /tmp/eqp.o || die "pristine compile failed"
gcc -O2 -march="$ARCH" -I. -c glm.c -o /tmp/eqq.o || die "patched compile failed"
objdump -d --no-show-raw-insn /tmp/eqp.o > /tmp/eqp.dis
objdump -d --no-show-raw-insn /tmp/eqq.o > /tmp/eqq.dis
python3 - <<'PYEOF'
import re,sys
def funcs(p):
    o,n={},None
    for l in open(p):
        m=re.match(r'^[0-9a-f]+ <(\w+)>:$',l)
        if m: n=m.group(1); o[n]=[]; continue
        if n and l.strip():
            s=re.sub(r'^\s*[0-9a-f]+:\s*','',l.rstrip()); s=re.sub(r'\b[0-9a-f]{2,}\b','A',s); s=re.sub(r'<[^>]*>','<S>',s); o[n].append(s)
    return o
a=funcs('/tmp/eqp.dis'); b=funcs('/tmp/eqq.dis'); sh=sorted(set(a)&set(b))
diff=[f for f in sh if a[f]!=b[f]]; allowed={"moe","layer_forward","main"}
bad=[f for f in diff if f not in allowed]
print("shared:",len(sh),"differing:",diff or "none")
sys.exit(1) if bad else print("INERT-BY-DEFAULT OK — only moe/layer_forward/main differ (RTRACE gated)")
PYEOF
cd "$WORK/colibri"

step "5/5 model fetch — DOCUMENTED ONLY (coordinator-owned)"
cat <<'EOF'
  The int4 estate fetch runs on the Modal worker (poc/modal/modal_glm52_smoke.py),
  staged directly onto LOCAL EPHEMERAL SSD (never a Volume). This host build is the
  $0 engine build + inert proof only. Next: run the Modal smoke.
EOF
echo; echo "BUILD OK: colibri@$COLIBRI_COMMIT + rtrace patch, engine+iobench built,"
echo "test_rtrace green, inert-by-default proven. Engine: $WORK/colibri/c/glm"
