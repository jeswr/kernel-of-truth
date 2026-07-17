#!/usr/bin/env bash
# =============================================================================
# bringup_gcp.sh — F1-K instance bring-up on the GCP Spot VM.
#
# This is the frozen poc/glm52-probe/f1k-harness/bringup.sh logic (same pins,
# same allowed-diff set) with the ONE authorized port that PATCH-NOTES.md open
# question 2 requires for the real runs: the §5 objdump function-label parser
# is made CLONE-AWARE ( <(\w+)>  ->  <([\w.]+)> , clone-suffix-aware allowed
# set), because gcc emits clone symbols like `moe.constprop.0` that the old
# regex mis-attributed (false-flagging layers_forward/read_arr). The frozen
# bringup.sh is left UNTOUCHED (frozen-experiment harness discipline); this GCP
# variant carries the documented fix for the AMD/gcc toolchain on the VM.
#
# Fail-closed throughout: clone+pin colibri, verify+apply the gate-0 KaE patch,
# build, assert 44/44 test_kae, prove inert-by-default per-function. Any failed
# check aborts bring-up (ERR_F1K_BRINGUP). The GLM-5.2 weight fetch is the
# separate staging step (f1k_worker.sh); this script only proves the ENGINE.
# =============================================================================
set -euo pipefail

COLIBRI_COMMIT="a78a06fc5acc4b0dc0f9ef03987c66b0559d1250"
PATCH_SHA256="11f8b45884878111480192ee086c92b22acaa1aaf3238b2d46c47f952e9dd9cb"
EXPECTED_UNIT_CHECKS=44
ALLOWED_DIFF_FUNCS="moe layer_forward main model_init"
ARCH="${ARCH:-native}"                    # AMD EPYC Milan on n2d — native tune
# OPS (bead kernel-of-truth-nf5n / docs/next/design/f1k-inertness-gate-resolution.md
# §3.1): the objdump machine-equivalence check is DEMOTED to a patch-shape check.
# It is FAIL-CLOSED ONLY at the pinned REFERENCE flags -O2 -march=x86-64-v3 (the
# exact basis the allowed sets were MEASURED on: ASM-2486 {moe,main}; the gate-0
# 88/92 proof {moe,layer_forward,main,model_init}; also real-checks.sh's default),
# and ADVISORY (never fatal) at the production-equivalent -O2 -march=native. This
# touches NOTHING frozen (registry/experiments/f1k.json 505165ee carries no
# objdump/allowed-diff obligation); the AUTHORITATIVE inertness gate is now the
# functional KAE-unset byte-identity gate in f1k_worker.sh.
CFLAGS_EQ="${BRINGUP_CFLAGS:--O2 -march=x86-64-v3}"   # fail-closed REFERENCE flags
CFLAGS_EQ_NATIVE="-O2 -march=native"                  # advisory-only, production-equivalent

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATCH_DIR="${KAE_PATCH_DIR:-$HERE/kae-patch-draft}"
WORK="${COLIBRI_WORK:-$HOME/colibri-f1k}"
GATE="${GATE:-$HOME/f1k-gate}"           # bring-up outputs (advisory objdump log); mirrored by the worker EXIT trap
mkdir -p "$GATE"

die() { echo "ERR_F1K_BRINGUP: $*" >&2; exit 1; }
step() { echo; echo "== $* =="; }

[ -n "${COLIBRI_GIT_URL:-}" ] || die "COLIBRI_GIT_URL is not set (coordinator-supplied)."

step "1/5 build dependencies"
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo apt-get install -y -qq git build-essential binutils python3
fi
for t in git gcc make objdump python3 sha256sum; do
  command -v "$t" >/dev/null 2>&1 || die "missing tool: $t"
done

step "2/5 clone colibri @ pinned commit $COLIBRI_COMMIT"
if [ ! -d "$WORK/.git" ]; then git clone "$COLIBRI_GIT_URL" "$WORK"; fi
cd "$WORK"
git fetch --all --quiet || true
git checkout --quiet "$COLIBRI_COMMIT" || die "pinned commit not found"
HEAD="$(git rev-parse HEAD)"
[ "$HEAD" = "$COLIBRI_COMMIT" ] || die "HEAD $HEAD != pinned $COLIBRI_COMMIT"
git diff --quiet || die "working tree not clean at the pinned commit"
echo "colibri pinned at $HEAD"

step "3/5 verify + apply the gate-0 KaE patch"
PATCH="$PATCH_DIR/kae-add-path.patch"
[ -f "$PATCH" ] || die "patch not found: $PATCH"
GOT="$(sha256sum "$PATCH" | awk '{print $1}')"
[ "$GOT" = "$PATCH_SHA256" ] || die "patch sha256 $GOT != registered $PATCH_SHA256"
cp c/glm.c /tmp/glm_pristine.c
# snapshot the ENTIRE pristine c/ tree (Makefile + headers) BEFORE the patch so
# the functional-gate reference engine glm_pristine builds at the SAME production
# flags via the base Makefile (the KaE patch edits the Makefile too) — bead nf5n.
rm -rf /tmp/glm_pristine_tree && cp -r c /tmp/glm_pristine_tree
git apply --check "$PATCH" || die "patch does not apply cleanly"
git apply "$PATCH"
echo "KaE patch applied (sha verified)"

step "4/5 build engine + run KaE unit suite (assert $EXPECTED_UNIT_CHECKS/$EXPECTED_UNIT_CHECKS)"
( cd c && make glm ARCH="$ARCH" ) || die "engine build failed"
( cd c && gcc -O2 -Wall -Wextra -Wno-unused-function -o /tmp/test_kae tests/test_kae.c -lm ) \
  || die "test_kae build failed"
TEST_OUT="$(/tmp/test_kae 2>&1)" || { echo "$TEST_OUT"; die "test_kae exited nonzero"; }
echo "$TEST_OUT" | grep -q "ALL TESTS PASSED" || { echo "$TEST_OUT"; die "test_kae did not pass"; }
N_OK="$(echo "$TEST_OUT" | grep -c '^  ok:' || true)"
[ "$N_OK" -eq "$EXPECTED_UNIT_CHECKS" ] || die "test_kae $N_OK != $EXPECTED_UNIT_CHECKS"
echo "test_kae: $N_OK/$EXPECTED_UNIT_CHECKS"

step "5/5 inert-by-default machine equivalence (KAE unset) — FAIL-CLOSED @ REFERENCE flags $CFLAGS_EQ (CLONE-AWARE parser)"
cd c
cp /tmp/glm_pristine.c /tmp/eq_pristine.c
cp glm.c /tmp/eq_patched.c
gcc $CFLAGS_EQ -I. -c /tmp/eq_pristine.c -o /tmp/eq_pristine.o || die "pristine compile failed"
gcc $CFLAGS_EQ -I. -c /tmp/eq_patched.c  -o /tmp/eq_patched.o  || die "patched compile failed"
objdump -d --no-show-raw-insn /tmp/eq_pristine.o > /tmp/eq_pristine.dis
objdump -d --no-show-raw-insn /tmp/eq_patched.o  > /tmp/eq_patched.dis
python3 - "$ALLOWED_DIFF_FUNCS" <<'PYEOF'
import re, sys
# clone-suffix-aware allowed set: `moe` also matches `moe.constprop.0` etc.
allowed_bases = set(sys.argv[1].split())
def base(name): return name.split('.', 1)[0]
def funcs(path):
    out, name = {}, None
    for line in open(path):
        # PATCH-NOTES OQ2 fix: <([\w.]+)> captures gcc clone symbols too
        m = re.match(r'^[0-9a-f]+ <([\w.]+)>:$', line)
        if m:
            name = m.group(1); out[name] = []
            continue
        if name is not None and line.strip():
            s = re.sub(r'^\s*[0-9a-f]+:\s*', '', line.rstrip())
            s = re.sub(r'\b[0-9a-f]{2,}\b', 'ADDR', s)
            s = re.sub(r'<[^>]*>', '<SYM>', s)
            out[name].append(s)
    return out
a = funcs('/tmp/eq_pristine.dis'); b = funcs('/tmp/eq_patched.dis')
shared = sorted(set(a) & set(b))
diff = [f for f in shared if a[f] != b[f]]
extra = sorted(set(b) - set(a))
print("shared: %d; differing: %s; patch-added: %s"
      % (len(shared), diff or "none", extra or "none"))
bad = [f for f in diff if base(f) not in allowed_bases]
if bad:
    print("ERR_F1K_BRINGUP: functions differ OUTSIDE allowed %s: %s"
          % (sorted(allowed_bases), bad), file=sys.stderr); sys.exit(1)
missing = [f for f in sorted(set(a) - set(b)) if base(f) not in allowed_bases]
if missing:
    print("ERR_F1K_BRINGUP: functions REMOVED by the patch: %s" % missing,
          file=sys.stderr); sys.exit(1)
print("inert-by-default: every shared function outside %s (clone-aware) is "
      "byte-identical" % sorted(allowed_bases))
PYEOF

# --- ADVISORY native-flags objdump pass (bead nf5n) — production-equivalent
#     -O2 -march=native, NEVER fatal. Logs the full differing/added/removed list
#     to $GATE for audit. On this toolchain (EPYC 7B13) it is EXPECTED to list
#     extra functions (attention/run_serve/tok_load + outlined kae_load); that is
#     codegen spill, and the AUTHORITATIVE inertness proof is the functional
#     KAE-unset byte-identity gate in f1k_worker.sh — NOT this advisory. ---
step "5a/5 ADVISORY objdump @ production flags $CFLAGS_EQ_NATIVE — never fatal"
ADV="$GATE/objdump-native-advisory.log"
: > "$ADV"
if gcc $CFLAGS_EQ_NATIVE -I. -c /tmp/eq_pristine.c -o /tmp/eqn_pristine.o 2>>"$ADV" \
   && gcc $CFLAGS_EQ_NATIVE -I. -c /tmp/eq_patched.c -o /tmp/eqn_patched.o 2>>"$ADV"; then
  objdump -d --no-show-raw-insn /tmp/eqn_pristine.o > /tmp/eqn_pristine.dis 2>>"$ADV" || true
  objdump -d --no-show-raw-insn /tmp/eqn_patched.o  > /tmp/eqn_patched.dis 2>>"$ADV" || true
  python3 - "$ALLOWED_DIFF_FUNCS" /tmp/eqn_pristine.dis /tmp/eqn_patched.dis >>"$ADV" 2>&1 <<'PYADV' || true
import re, sys
allowed = set(sys.argv[1].split())
def base(n): return n.split('.', 1)[0]
def funcs(path):
    out, name = {}, None
    for line in open(path):
        m = re.match(r'^[0-9a-f]+ <([\w.]+)>:$', line)
        if m:
            name = m.group(1); out[name] = []; continue
        if name is not None and line.strip():
            s = re.sub(r'^\s*[0-9a-f]+:\s*', '', line.rstrip())
            s = re.sub(r'\b[0-9a-f]{2,}\b', 'ADDR', s)
            s = re.sub(r'<[^>]*>', '<SYM>', s)
            out[name].append(s)
    return out
a = funcs(sys.argv[2]); b = funcs(sys.argv[3])
shared = sorted(set(a) & set(b))
diff = [f for f in shared if a[f] != b[f]]
added = sorted(set(b) - set(a)); removed = sorted(set(a) - set(b))
outside = [f for f in diff if base(f) not in allowed]
print("ADVISORY (-O2 -march=native): shared %d; differing %s; OUTSIDE-allowed %s; "
      "patch-added %s; removed %s"
      % (len(shared), diff or "none", outside or "none", added or "none",
         removed or "none"))
sys.exit(0)   # advisory: NEVER fatal
PYADV
else
  echo "advisory native compile failed (non-fatal; toolchain-specific)" >> "$ADV"
fi
echo "advisory objdump @ native ($CFLAGS_EQ_NATIVE):"; cat "$ADV" || true
cd "$WORK"

# --- build the PRISTINE (pre-patch) engine at the SAME production flags for the
#     functional inert-by-default gate in f1k_worker.sh (bead nf5n §3.1). ---
step "5b/5 build PRISTINE engine @ production flags (functional-gate reference)"
( cd /tmp/glm_pristine_tree && make glm ARCH="$ARCH" ) || die "pristine engine build failed"
[ -x /tmp/glm_pristine_tree/glm ] || die "pristine glm binary not produced"
cp /tmp/glm_pristine_tree/glm "$WORK/c/glm_pristine"
echo "pristine engine (KaE-free, production flags): $WORK/c/glm_pristine"

echo
echo "BRING-UP OK (KaE): colibri@$COLIBRI_COMMIT + KaE patch (sha verified),"
echo "build OK, test_kae $N_OK/$EXPECTED_UNIT_CHECKS, inert-by-default proven"
echo "(objdump fail-closed @ REFERENCE $CFLAGS_EQ; native pass advisory-only)."
echo "Scoring engine binary:  $WORK/c/glm"
echo "Pristine engine binary: $WORK/c/glm_pristine (functional-gate reference)"
