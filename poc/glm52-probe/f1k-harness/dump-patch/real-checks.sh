#!/usr/bin/env bash
# =============================================================================
# real-checks.sh — kot-f1k-dump/1 REAL-SOURCE checks ($0: compile-level only).
#
# Complements validate.py (the mock behavioural battery): proves the patch
# FILE itself against the real colibri source — applies on top of the pinned
# gate-0 KaE patch, builds, keeps the KaE unit suite green, and is INERT
# machine-level with KAE_DUMP unset (objdump per-function equivalence vs the
# KaE-only object; bringup.sh §5 method, with the parser extended to
# recognise gcc clone symbols like moe.constprop.0 — without that, a clone
# following a changed function is silently swallowed into its body).
#
# NO model, NO weights, NO instance, NO network: the caller supplies
#   COLIBRI_TREE = path to a colibri checkout whose c/glm.c is PRISTINE at
#                  the pinned base (verified by git blob hash below; the
#                  engine is pinned by content, no upstream org string).
# The input tree is copied; nothing in it is mutated.
#
# At Modal bring-up the same battery re-runs on the real box (bringup.sh
# flow) BEFORE any real dump; this script is the $0 preview of that gate.
# =============================================================================
set -euo pipefail

# c/glm.c blob hash at colibri base a78a06fc (the KaE patch pre-image id,
# kae-add-path.patch "index 1d74f78..90a4e15")
PRISTINE_GLM_BLOB="1d74f7886022baaf3fa936602f9db3a4d82f7f21"
KAE_PATCH_SHA256="11f8b45884878111480192ee086c92b22acaa1aaf3238b2d46c47f952e9dd9cb"
EXPECTED_KAE_CHECKS=44         # f1k.json pins.harness_manifest
EXPECTED_DUMP_CHECKS=64        # test_kae_dump.c (this patch, r3: +21 checks —
                               # Tests G strict-parse, H non-finite, I /dev/full)
ALLOWED_DIFF_FUNCS="moe main"  # ONLY functions the dump patch wires (ASM-2486:
                               # g_kdump is file-scope, so model_init and
                               # layer_forward stay identical, unlike the KaE
                               # patch's allowed set)
CFLAGS_EQ="${BRINGUP_CFLAGS:--O2 -march=x86-64-v3}"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KAE_DIR="$HERE/../../kae-patch-draft"
WORK="${DUMP_CHECK_WORK:-/tmp/kot-dump-realcheck}"

die() { echo "ERR_F1K_DUMP_CHECK: $*" >&2; exit 1; }
step() { echo; echo "== $* =="; }

[ -n "${COLIBRI_TREE:-}" ] || die "COLIBRI_TREE not set (path to a pristine colibri checkout)"
[ -f "$COLIBRI_TREE/c/glm.c" ] || die "no c/glm.c under COLIBRI_TREE"

step "1/6 pin the pristine source by content"
BLOB="$(git hash-object "$COLIBRI_TREE/c/glm.c")"
[ "$BLOB" = "$PRISTINE_GLM_BLOB" ] \
  || die "c/glm.c blob $BLOB != pinned pristine $PRISTINE_GLM_BLOB (tree not at base / already patched)"
rm -rf "$WORK"; mkdir -p "$WORK"
cp -r "$COLIBRI_TREE/c" "$WORK/c"
echo "pristine glm.c blob verified: $BLOB"

step "2/6 apply the gate-0 KaE patch (sha-verified), snapshot KaE-only glm.c"
GOT="$(sha256sum "$KAE_DIR/kae-add-path.patch" | awk '{print $1}')"
[ "$GOT" = "$KAE_PATCH_SHA256" ] || die "KaE patch sha $GOT != registered $KAE_PATCH_SHA256"
( cd "$WORK" && git apply --check "$KAE_DIR/kae-add-path.patch" \
  && git apply "$KAE_DIR/kae-add-path.patch" ) || die "KaE patch failed to apply"
cp "$WORK/c/glm.c" "$WORK/glm_kaeonly.c"
echo "KaE patch applied"

step "3/6 apply kot-f1k-dump.patch on top; reference copies must match"
( cd "$WORK" && git apply --check "$HERE/kot-f1k-dump.patch" \
  && git apply "$HERE/kot-f1k-dump.patch" ) || die "dump patch failed to apply on the KaE tree"
cmp -s "$WORK/c/kae_dump.h" "$HERE/kae_dump.h" \
  || die "patched c/kae_dump.h != reference copy dump-patch/kae_dump.h (drift)"
cmp -s "$WORK/c/tests/test_kae_dump.c" "$HERE/test_kae_dump.c" \
  || die "patched test_kae_dump.c != reference copy (drift)"
echo "dump patch applied; reference copies byte-identical to the patch payload"

step "4/6 build the patched engine"
( cd "$WORK/c" && nice -n 10 make glm ARCH=x86-64-v3 >/dev/null ) || die "engine build failed"
echo "engine built: $WORK/c/glm"

step "5/6 unit suites: KaE regression ($EXPECTED_KAE_CHECKS) + dump ($EXPECTED_DUMP_CHECKS)"
( cd "$WORK/c" && gcc -O2 -Wall -Wextra -Wno-unused-function -o "$WORK/test_kae" tests/test_kae.c -lm ) \
  || die "test_kae build failed"
OUT1="$("$WORK/test_kae" 2>&1)" || { echo "$OUT1"; die "test_kae exited nonzero"; }
N1="$(echo "$OUT1" | grep -c '^  ok:' || true)"
echo "$OUT1" | grep -q "ALL TESTS PASSED" && [ "$N1" -eq "$EXPECTED_KAE_CHECKS" ] \
  || die "test_kae: $N1/$EXPECTED_KAE_CHECKS (regression!)"
echo "test_kae: $N1/$EXPECTED_KAE_CHECKS (unchanged by the dump patch)"
( cd "$WORK/c" && gcc -O2 -Wall -Wextra -Wno-unused-function -o "$WORK/test_kae_dump" tests/test_kae_dump.c -lm ) \
  || die "test_kae_dump build failed"
OUT2="$("$WORK/test_kae_dump" 2>&1)" || { echo "$OUT2"; die "test_kae_dump exited nonzero"; }
N2="$(echo "$OUT2" | grep -c '^  ok:' || true)"
echo "$OUT2" | grep -q "ALL TESTS PASSED" && [ "$N2" -eq "$EXPECTED_DUMP_CHECKS" ] \
  || die "test_kae_dump: $N2/$EXPECTED_DUMP_CHECKS"
echo "test_kae_dump: $N2/$EXPECTED_DUMP_CHECKS"

step "6/6 inert-by-default machine-level equivalence (KAE_DUMP unset)"
cd "$WORK/c"
nice -n 10 gcc $CFLAGS_EQ -I. -c "$WORK/glm_kaeonly.c" -o "$WORK/eq_kaeonly.o" \
  || die "KaE-only object compile failed"
nice -n 10 gcc $CFLAGS_EQ -I. -c glm.c -o "$WORK/eq_dump.o" \
  || die "dump-patched object compile failed"
objdump -d --no-show-raw-insn "$WORK/eq_kaeonly.o" > "$WORK/eq_kaeonly.dis"
objdump -d --no-show-raw-insn "$WORK/eq_dump.o"    > "$WORK/eq_dump.dis"
python3 - "$ALLOWED_DIFF_FUNCS" "$WORK" <<'PYEOF'
import re, sys
allowed = set(sys.argv[1].split()); work = sys.argv[2]

def funcs(path):
    # bringup.sh §5 parser, EXTENDED: [\w.] also matches gcc clone symbols
    # (moe.constprop.0, x.isra.0) so a clone label is never swallowed into
    # the previous function's body.
    out, name = {}, None
    for line in open(path):
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

a = funcs(work + '/eq_kaeonly.dis')
b = funcs(work + '/eq_dump.dis')
shared = sorted(set(a) & set(b))
diff = [f for f in shared if a[f] != b[f]]
extra = sorted(set(b) - set(a))     # patch-added + newly-outlined: OK
missing = sorted(set(a) - set(b))
print("shared functions: %d; differing: %s; new symbols: %s; removed: %s"
      % (len(shared), diff or "none", extra or "none", missing or "none"))
base = lambda f: f.split('.')[0]    # moe.constprop.0 counts as moe
bad = [f for f in diff if base(f) not in allowed]
if bad:
    print("ERR_F1K_DUMP_CHECK: functions differ OUTSIDE the allowed set %s: %s"
          % (sorted(allowed), bad), file=sys.stderr)
    sys.exit(1)
if missing:
    print("ERR_F1K_DUMP_CHECK: functions REMOVED by the patch: %s" % missing,
          file=sys.stderr)
    sys.exit(1)
print("inert-by-default: every shared function outside %s is byte-identical"
      % sorted(allowed))
PYEOF

echo
echo "REAL-SOURCE CHECKS OK: dump patch applies on KaE tree, builds,"
echo "test_kae $N1/$EXPECTED_KAE_CHECKS + test_kae_dump $N2/$EXPECTED_DUMP_CHECKS, inertness proven at object level."
echo "(\$0 SCOPE: no model/weights — the same battery re-runs on Modal at bring-up.)"
