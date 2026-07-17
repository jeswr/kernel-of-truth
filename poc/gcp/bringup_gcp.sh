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
# build, assert 44/44 test_kae. Any failed check aborts bring-up
# (ERR_F1K_BRINGUP). The objdump inert-by-default check is ADVISORY-ONLY on this
# box (step 5; see the ops note below) — the AUTHORITATIVE inertness gate is the
# functional KAE-unset byte-identity gate in f1k_worker.sh. The GLM-5.2 weight
# fetch is the separate staging step (f1k_worker.sh); this script only proves
# the ENGINE builds and its unit suite passes.
# =============================================================================
set -euo pipefail

COLIBRI_COMMIT="a78a06fc5acc4b0dc0f9ef03987c66b0559d1250"
PATCH_SHA256="11f8b45884878111480192ee086c92b22acaa1aaf3238b2d46c47f952e9dd9cb"
EXPECTED_UNIT_CHECKS=44
ALLOWED_DIFF_FUNCS="moe layer_forward main model_init"
ARCH="${ARCH:-native}"                    # AMD EPYC Milan on n2d — native tune
# OPS (beads kernel-of-truth-nf5n + kernel-of-truth-f2uk /
# docs/next/design/f1k-inertness-gate-resolution.md §3.1 + §5 addendum): the
# objdump machine-equivalence check is ADVISORY-ONLY ON THIS BOX at BOTH flag
# sets — reference -O2 -march=x86-64-v3 AND production-equivalent -O2
# -march=native. Runner-8 MEASURED (run 20260717T015601Z, kae-bringup.log) that
# the VM's Ubuntu gcc spills [attention, run_serve, tok_load] outside the
# allowed set EVEN AT the reference flags: the allowed set (measured on the
# gate-0 gcc 11.5 — ASM-2486 {moe,main}; gate-0 88/92
# {moe,layer_forward,main,model_init}) is gcc-VERSION-brittle, not merely
# -march-brittle, so it only reproduces fail-closed on the toolchain that
# measured it. Per ASM-2503's pre-registered resolution_path, the FAIL-CLOSED
# reference-flags objdump pass moves OFF-BOX-ONLY (frozen bringup.sh +
# dump-patch/real-checks.sh on the gcc-11.5 basis — untouched); here the full
# diff lists are logged to $GATE for audit and NEVER fatal. This touches
# NOTHING frozen (registry/experiments/f1k.json 505165ee carries no
# objdump/allowed-diff obligation); the AUTHORITATIVE fail-closed inertness
# gate is the functional KAE-unset byte-identity gate in f1k_worker.sh
# (toolchain-independent, real binary, real weights).
CFLAGS_EQ="${BRINGUP_CFLAGS:--O2 -march=x86-64-v3}"   # reference flags — ADVISORY on this box
CFLAGS_EQ_NATIVE="-O2 -march=native"                  # production-equivalent — ADVISORY

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

# --- Step 5: ADVISORY objdump patch-shape check (bead f2uk) — clone-aware
#     parser run at BOTH the reference flags AND production-equivalent native,
#     NEVER fatal on this box. Full differing/OUTSIDE-allowed/added/removed
#     lists go to $GATE/objdump-<tag>-advisory.log for audit. On this toolchain
#     it is EXPECTED to list extra functions at BOTH flag sets
#     (attention/run_serve/tok_load + outlined kae_load/kae_free.part.0 —
#     MEASURED, runner-8 20260717T015601Z); that is gcc-version codegen spill.
#     The AUTHORITATIVE inertness proof is the functional KAE-unset
#     byte-identity gate in f1k_worker.sh — NOT these advisories. The
#     fail-closed reference-flags objdump lives OFF-BOX ONLY (frozen bringup.sh
#     + dump-patch/real-checks.sh on the gate-0 gcc-11.5 measurement basis). ---
step "5/5 ADVISORY objdump patch-shape check (KAE unset) — reference + native flags, never fatal on this box"
cd c
cp /tmp/glm_pristine.c /tmp/eq_pristine.c
cp glm.c /tmp/eq_patched.c
objdump_advisory() {  # $1 = tag; remaining args = cflags. NEVER returns nonzero.
  local tag="$1"; shift
  local adv="$GATE/objdump-$tag-advisory.log"
  : > "$adv"
  if gcc "$@" -I. -c /tmp/eq_pristine.c -o "/tmp/eq_${tag}_pristine.o" 2>>"$adv" \
     && gcc "$@" -I. -c /tmp/eq_patched.c -o "/tmp/eq_${tag}_patched.o" 2>>"$adv"; then
    objdump -d --no-show-raw-insn "/tmp/eq_${tag}_pristine.o" > "/tmp/eq_${tag}_pristine.dis" 2>>"$adv" || true
    objdump -d --no-show-raw-insn "/tmp/eq_${tag}_patched.o"  > "/tmp/eq_${tag}_patched.dis"  2>>"$adv" || true
    python3 - "$ALLOWED_DIFF_FUNCS" "$*" "/tmp/eq_${tag}_pristine.dis" "/tmp/eq_${tag}_patched.dis" >>"$adv" 2>&1 <<'PYADV' || true
import re, sys
# clone-suffix-aware allowed set: `moe` also matches `moe.constprop.0` etc.
# (PATCH-NOTES OQ2 fix: <([\w.]+)> captures gcc clone symbols too)
allowed = set(sys.argv[1].split()); flags = sys.argv[2]
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
a = funcs(sys.argv[3]); b = funcs(sys.argv[4])
shared = sorted(set(a) & set(b))
diff = [f for f in shared if a[f] != b[f]]
added = sorted(set(b) - set(a)); removed = sorted(set(a) - set(b))
outside = [f for f in diff if base(f) not in allowed]
print("ADVISORY (%s): shared %d; differing %s; OUTSIDE-allowed %s; "
      "patch-added %s; removed %s"
      % (flags, len(shared), diff or "none", outside or "none",
         added or "none", removed or "none"))
sys.exit(0)   # advisory: NEVER fatal on this box (bead f2uk / ASM-2503 resolution_path)
PYADV
  else
    echo "advisory compile failed at ($*) (non-fatal; toolchain-specific)" >> "$adv"
  fi
  echo "advisory objdump [$tag] ($*):"; cat "$adv" || true
  return 0
}
objdump_advisory reference $CFLAGS_EQ
objdump_advisory native    $CFLAGS_EQ_NATIVE
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
echo "build OK, test_kae $N_OK/$EXPECTED_UNIT_CHECKS."
echo "(objdump patch-shape checks ADVISORY-ONLY on this box — logs in $GATE/objdump-*-advisory.log;"
echo " AUTHORITATIVE inert-by-default gate = functional KAE-unset byte-identity in f1k_worker.sh.)"
echo "Scoring engine binary:  $WORK/c/glm"
echo "Pristine engine binary: $WORK/c/glm_pristine (functional-gate reference)"
