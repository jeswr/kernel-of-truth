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
CFLAGS_EQ="${BRINGUP_CFLAGS:--O2 -march=native}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATCH_DIR="${KAE_PATCH_DIR:-$HERE/kae-patch-draft}"
WORK="${COLIBRI_WORK:-$HOME/colibri-f1k}"

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

step "5/5 inert-by-default machine-level equivalence (KAE unset) — CLONE-AWARE parser"
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
cd "$WORK"

echo
echo "BRING-UP OK (KaE): colibri@$COLIBRI_COMMIT + KaE patch (sha verified),"
echo "build OK, test_kae $N_OK/$EXPECTED_UNIT_CHECKS, inert-by-default proven."
echo "Scoring engine binary: $WORK/c/glm"
