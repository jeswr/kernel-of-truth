#!/usr/bin/env bash
# =============================================================================
# bringup.sh — F1-K instance bring-up: colibri @ pinned commit + KaE ADD patch.
#
# RUN BY THE COORDINATOR on the freshly launched Ubuntu spot i4i.2xlarge
# (docs/next/design/glm52-f1k-cost-reduction.md: spot + expert-pinning + R=3,
# $149 ceiling). THIS SCRIPT IS NOT RUN IN THE BUILD PASS: the build pass
# launches no instance, clones nothing, downloads no model, spends $0.
#
# What it does (ALL fail-closed; any failed check aborts bring-up):
#   1. install build deps (gcc/make/binutils/python3)
#   2. clone colibri and hard-pin the base commit
#        a78a06fc5acc4b0dc0f9ef03987c66b0559d1250
#      [registry/experiments/f1k.json pins.model_revisions.colibri-base-commit]
#   3. verify the gate-0 KaE patch bytes against the registered sha256
#      [f1k.json pins.harness_manifest], snapshot the pristine glm.c,
#      apply the patch, build
#   4. run the KaE unit suite test_kae.c and ASSERT 44/44 checks pass
#      [f1k.json pins.harness_manifest: "44/44 unit checks"]
#   5. prove INERT-BY-DEFAULT (KAE unset) at the machine level: compile
#      pristine vs patched glm.c to objects, disassemble, address-normalize,
#      compare PER FUNCTION; the ONLY functions allowed to differ are the
#      ones the patch wires — moe, layer_forward, main — plus model_init
#      (sizeof(Model) immediate for the appended KaE* field)
#      [kae-patch-draft/README.md "Inert-by-default" / build-test.log §3]
#   6. DOCUMENT the model-fetch step (does NOT fetch: coordinator-owned,
#      weight content-hash pinned at bring-up per ASM-1971 ->
#      f1k.json pins.model_revisions.glm52-weights PINNED-AT-INPUTS)
#
# Engine naming: the C engine is referred to as "colibri" throughout this
# harness. The clone URL is NOT hard-coded here (third-party repo; the base
# is referenced by sha only, per the kae-patch-draft README etiquette):
# the coordinator supplies it via COLIBRI_GIT_URL.
# =============================================================================
set -euo pipefail

COLIBRI_COMMIT="a78a06fc5acc4b0dc0f9ef03987c66b0559d1250"
PATCH_SHA256="11f8b45884878111480192ee086c92b22acaa1aaf3238b2d46c47f952e9dd9cb"
KAEH_SHA256="e2574873115b5109ca87123e29286ea89ce8955655a31fc158225be52fb21ddd"
EXPECTED_UNIT_CHECKS=44          # f1k.json pins.harness_manifest: 44/44
ALLOWED_DIFF_FUNCS="moe layer_forward main model_init"
ARCH="${ARCH:-x86-64-v3}"        # kae-patch-draft README reproduce line
CFLAGS_EQ="${BRINGUP_CFLAGS:--O2 -march=x86-64-v3}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATCH_DIR="$HERE/../kae-patch-draft"
WORK="${COLIBRI_WORK:-$HOME/colibri-f1k}"

die() { echo "ERR_F1K_BRINGUP: $*" >&2; exit 1; }
step() { echo; echo "== $* =="; }

[ -n "${COLIBRI_GIT_URL:-}" ] || die \
  "COLIBRI_GIT_URL is not set. The colibri clone URL is coordinator-supplied
   (the repo pins the engine by base commit sha only). Export it and re-run."

step "1/6 build dependencies"
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo apt-get install -y -qq git build-essential binutils python3
fi
for t in git gcc make objdump python3 sha256sum; do
  command -v "$t" >/dev/null 2>&1 || die "missing tool: $t"
done

step "2/6 clone colibri @ pinned commit $COLIBRI_COMMIT"
if [ ! -d "$WORK/.git" ]; then
  git clone "$COLIBRI_GIT_URL" "$WORK"
fi
cd "$WORK"
git fetch --all --quiet || true
git checkout --quiet "$COLIBRI_COMMIT" \
  || die "pinned commit $COLIBRI_COMMIT not found in the clone"
HEAD="$(git rev-parse HEAD)"
[ "$HEAD" = "$COLIBRI_COMMIT" ] || die "HEAD $HEAD != pinned $COLIBRI_COMMIT"
git diff --quiet || die "working tree not clean at the pinned commit"
echo "colibri pinned at $HEAD"

step "3/6 verify + apply the gate-0 KaE patch"
PATCH="$PATCH_DIR/kae-add-path.patch"
[ -f "$PATCH" ] || die "patch not found: $PATCH"
GOT="$(sha256sum "$PATCH" | awk '{print $1}')"
[ "$GOT" = "$PATCH_SHA256" ] \
  || die "patch sha256 $GOT != registered $PATCH_SHA256 (f1k.json pins.harness_manifest)"
GOT_H="$(sha256sum "$PATCH_DIR/kae.h" | awk '{print $1}')"
[ "$GOT_H" = "$KAEH_SHA256" ] \
  || die "kae.h reference sha256 $GOT_H != registered $KAEH_SHA256"
# snapshot the PRISTINE glm.c for the equivalence proof (step 5)
cp c/glm.c /tmp/glm_pristine.c
git apply --check "$PATCH" || die "patch does not apply cleanly at the pinned commit"
git apply "$PATCH"
echo "patch applied (sha256 verified)"

step "4/6 build engine + run KaE unit suite (assert $EXPECTED_UNIT_CHECKS/$EXPECTED_UNIT_CHECKS)"
( cd c && make glm ARCH="$ARCH" ) || die "engine build failed"
( cd c && gcc -O2 -Wall -Wextra -Wno-unused-function -o /tmp/test_kae tests/test_kae.c -lm ) \
  || die "test_kae build failed"
TEST_OUT="$(/tmp/test_kae 2>&1)" || { echo "$TEST_OUT"; die "test_kae exited nonzero"; }
echo "$TEST_OUT" | grep -q "ALL TESTS PASSED" || { echo "$TEST_OUT"; die "test_kae did not pass"; }
N_OK="$(echo "$TEST_OUT" | grep -c '^  ok:' || true)"
[ "$N_OK" -eq "$EXPECTED_UNIT_CHECKS" ] \
  || die "test_kae passed $N_OK checks, expected $EXPECTED_UNIT_CHECKS (pin: f1k.json harness_manifest)"
echo "test_kae: $N_OK/$EXPECTED_UNIT_CHECKS checks passed"

step "5/6 inert-by-default machine-level equivalence (KAE unset)"
# Method mirrors kae-patch-draft/build-test.log §3: compile pristine and
# patched glm.c to objects, disassemble, address-normalize, compare per
# function. Only $ALLOWED_DIFF_FUNCS may differ; anything else fails closed.
cd c
cp /tmp/glm_pristine.c /tmp/eq_pristine.c
cp glm.c /tmp/eq_patched.c
# compile both FROM THIS DIRECTORY so both see identical headers (kae.h is
# additive; the pristine source never includes it)
gcc $CFLAGS_EQ -I. -c /tmp/eq_pristine.c -o /tmp/eq_pristine.o \
  || die "pristine object compile failed (set BRINGUP_CFLAGS to the Makefile's flags if needed)"
gcc $CFLAGS_EQ -I. -c /tmp/eq_patched.c  -o /tmp/eq_patched.o \
  || die "patched object compile failed"
objdump -d --no-show-raw-insn /tmp/eq_pristine.o > /tmp/eq_pristine.dis
objdump -d --no-show-raw-insn /tmp/eq_patched.o  > /tmp/eq_patched.dis
python3 - "$ALLOWED_DIFF_FUNCS" <<'PYEOF'
import re, sys
allowed = set(sys.argv[1].split())

def funcs(path):
    out, name = {}, None
    for line in open(path):
        m = re.match(r'^[0-9a-f]+ <(\w+)>:$', line)
        if m:
            name = m.group(1); out[name] = []
            continue
        if name is not None and line.strip():
            # address-normalize: strip offsets, absolute addrs, jump targets
            s = re.sub(r'^\s*[0-9a-f]+:\s*', '', line.rstrip())
            s = re.sub(r'\b[0-9a-f]{2,}\b', 'ADDR', s)
            s = re.sub(r'<[^>]*>', '<SYM>', s)
            out[name].append(s)
    return out

a = funcs('/tmp/eq_pristine.dis')
b = funcs('/tmp/eq_patched.dis')
shared = sorted(set(a) & set(b))
diff = [f for f in shared if a[f] != b[f]]
extra = sorted(set(b) - set(a))     # patch-added (run_kae_score, kae_*): OK
print("shared functions: %d; differing: %s; patch-added: %s"
      % (len(shared), diff or "none", extra or "none"))
bad = [f for f in diff if f not in allowed]
if bad:
    print("ERR_F1K_BRINGUP: functions differ OUTSIDE the allowed set %s: %s"
          % (sorted(allowed), bad), file=sys.stderr)
    sys.exit(1)
missing = sorted(set(a) - set(b))
if missing:
    print("ERR_F1K_BRINGUP: functions REMOVED by the patch: %s" % missing,
          file=sys.stderr)
    sys.exit(1)
print("inert-by-default: every shared function outside %s is byte-identical"
      % sorted(allowed))
PYEOF
cd "$WORK"

step "6/6 model fetch — DOCUMENTED ONLY (NOT executed by this script)"
cat <<'EOF'
  The GLM-5.2 weight fetch is a COORDINATOR action, deliberately not
  automated here (this script must be runnable in review without spend):

    a. stage the GLM-5.2 snapshot onto the instance NVMe (same weight set
       as the P0 probe box);
    b. pin the weight CONTENT HASH at bring-up, BEFORE any test prefill:
       this resolves registry/experiments/f1k.json
       pins.model_revisions.glm52-weights (PINNED-AT-INPUTS, ASM-1971
       discipline);
    c. re-verify colibri knob semantics on the fetched snapshot (ASM-1971;
       design §R-REV4.2 step 3 runs this alongside the pilot);
    d. only after (a)-(c): pilot.sh (the (L,g) pilot + bring-up gates).

  Expert-pinning + warm page-cache (the 1.20x cost lever,
  glm52-f1k-cost-reduction.md item 2) is configured via the engine's PIN=
  / PIN_GB env at run time — see README.md; the f1k_driver passes engine
  env through verbatim. XCACHE (glm52-expert-cache.md) is a pass-through
  seam and may stay OFF for the pilot; the off-concept guard ALWAYS runs
  cache-off (ASM-2306).
EOF

echo
echo "BRING-UP OK: colibri@$COLIBRI_COMMIT + KaE patch (sha verified), build OK,"
echo "test_kae $N_OK/$EXPECTED_UNIT_CHECKS, inert-by-default equivalence proven."
echo "Engine binary: $WORK/c/glm"
