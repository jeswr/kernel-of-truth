#!/usr/bin/env python3
"""validate.py — $0 MOCK VALIDATION of the kot-f1k-dump/1 patch.

Proves, against the tiny mock engine (mock_glm_dump.c) that links the SAME
kae_dump.h + kae.h the patched glm.c links, the load-bearing dump properties
(a wrong moe()-input dump silently corrupts every carrier, so V1/V2 are the
checks that MUST be measured green before any real construction run):

  V1  KAE_DUMP-unset BYTE-IDENTITY: the dump-patched engine's forward output
      is byte-identical to the pre-dump reference engine's; arming the dump
      does not perturb the forward either (read-only capture).
  V2  f64 RE-DERIVATION: every dumped sum cell equals an INDEPENDENT Python
      float64 re-derivation of the mock hidden states over gated positions,
      BIT-EXACT after the f32 cast (the mock grid is exact in f32/f64, so
      equality is exact, never approximate).
  V3  PROVENANCE ECHO: the '[KAE-DUMP] armed: ... seed=<KAE_SEED>' stderr
      line fires, matches build_carriers.py's ECHO_RE verbatim, and echoes
      the exact KAE_SEED (registered CONSTRUCTION_SEED); the seed-absent
      echo is detected as a mismatch by the harness comparison.
  V4  GATED-ONLY + POSITION SEMANTICS: sums cover exactly the span>=0
      positions (single-gated line == that one position's hidden vector,
      bit-exact); a CHUNKED prefill (CHUNK=3, pos_base advancing) yields a
      byte-identical .kaed (absolute-position gating).
  V5  FAIL-CLOSED battery: phase-separation (KAE_DUMP+KAE_SCORE,
      KAE_DUMP+KAE=1), missing KAE_DUMP_OUT/LAYERS, duplicate layer,
      out-of-range layer, zero-gated line, malformed token, a dump
      layer moe() never reaches (dense layer), a wholly non-numeric
      GARBAGE manifest line (must NOT be silently skipped), TRAILING
      JUNK after the required 2T+1 integers, and the r3 (gate-0
      re-review finding 3) integer-hardening negatives — a span slot of
      2147483648 (the exact int-wrap that r2 silently UNGATED with exit
      0), a long-overflowing (ERANGE) span, a long-overflowing token id,
      an int-overflowing pass-1 T, and a manifest READ ERROR (directory
      path) — ALL exit nonzero; plus a boundary POSITIVE control (span
      slot 2147483646 = INT_MAX-1 still accepted and gated — the
      hardening does not over-reject).
  V6  UNIT SUITE: tests/test_kae_dump.c (the copy that rides IN the patch)
      builds and passes, plain and under ASan+UBSan+LSan — now including
      the r3 Tests G (strict-parse negatives), H (NaN/Inf/f32-cast-
      overflow fail-closed, finding 4) and I (/dev/full output failure).

Everything runs from the repo copies; no model, no weights, no network, no
spend. Real-tree checks (patch applies on the pinned KaE tree, engine
compiles, objdump per-function inertness) live in real-checks.sh.
Exit 0 iff every check passes.
"""
import os
import re
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS = HERE.parent
KAEPATCH = HARNESS.parent / "kae-patch-draft"
OUT = HERE / "mock-out"
NLAYERS = 12
VOCAB = 100000

fails = 0
def check(cond, msg):
    global fails
    print("  %s %s" % ("ok:  " if cond else "FAIL:", msg))
    if not cond:
        fails += 1

def run(binary, manifest, fwd, env_extra=None, expect_rc=0, label=""):
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("KAE", "MOCK", "CHUNK"))}
    if env_extra:
        env.update({k: str(v) for k, v in env_extra.items()})
    p = subprocess.run([str(binary), str(manifest), str(fwd)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    if expect_rc == 0 and p.returncode != 0:
        sys.stderr.write(p.stderr.decode())
        check(False, "%s exited %d (want 0)" % (label, p.returncode))
    return p

# ---------------------------------------------------------------------------
# independent f64 re-derivation of the mock hidden states (pure Python;
# mirrors mock_glm_dump.c hid()/fnv1a_ids() from the SPEC, not the binary)
# ---------------------------------------------------------------------------
M32 = 0xffffffff
def fnv1a_ids(ids):
    h = 2166136261
    for t in ids:
        for b in range(4):
            h ^= (t >> (8 * b)) & 0xff
            h = (h * 16777619) & M32
    return h

def hid(pfx, layer, pos, d):
    v = (pfx ^ ((2654435761 * (layer + 1)) & M32)
             ^ ((40503 * (pos + 1)) & M32)
             ^ ((2246822519 * (d + 1)) & M32)) & M32
    v ^= v >> 13
    v = (v * 2654435761) & M32
    v ^= v >> 16
    return ((v & 0xffff) - 32768) / 256.0     # exact in f32 and f64

def rederive(lines, layers, D):
    """per line: (gated_count, f64 sums[nl*D]) over span>=0 positions."""
    out = []
    for ids, spans in lines:
        gated = [p for p, s in enumerate(spans) if s >= 0]
        sums = []
        for layer in layers:
            for d in range(D):
                acc = 0.0
                for p in gated:                     # ascending position order
                    acc += hid(fnv1a_ids(ids[:p + 1]), layer, p, d)
                sums.append(acc)
        out.append((len(gated), sums))
    return out

def parse_kaed(path):
    raw = Path(path).read_bytes()
    assert raw[:4] == b"KAED", "bad magic"
    n_lines, nl, D = struct.unpack_from("<iii", raw, 4)
    layers = list(struct.unpack_from("<%di" % nl, raw, 16))
    off = 16 + 4 * nl
    per = []
    for _ in range(n_lines):
        (gc,) = struct.unpack_from("<i", raw, off); off += 4
        sums = list(struct.unpack_from("<%df" % (nl * D), raw, off))
        off += 4 * nl * D
        per.append((gc, sums))
    assert off == len(raw), "trailing bytes"
    return n_lines, nl, D, layers, per

def f32(x):
    return struct.unpack("<f", struct.pack("<f", x))[0]

def main():
    OUT.mkdir(exist_ok=True)
    D = 16
    LAYERS = [5, 2, 9]        # deliberately NON-sorted: pins slot order
    SEED = None
    src = (HARNESS / "build_carriers.py").read_text(encoding="utf-8")
    m = re.search(r"^CONSTRUCTION_SEED\s*=\s*(\d+)", src, re.M)
    assert m, "CONSTRUCTION_SEED not found in build_carriers.py"
    SEED = int(m.group(1))
    # the EXACT echo regex the pinned generator enforces (fail if it drifts)
    lit = r'ECHO_RE = re.compile(r"^\[KAE-DUMP\] armed:.*?\bseed=([0-9-]+)", re.M)'
    check(lit in src, "build_carriers.py still enforces the pinned ECHO_RE literal")
    ECHO_RE = re.compile(r"^\[KAE-DUMP\] armed:.*?\bseed=([0-9-]+)", re.M)

    print("== build: reference (pre-dump) + dump-patched mock engines ==")
    ref = OUT / "mock_ref"
    eng = OUT / "mock_dump"
    inc = ["-I", str(HERE), "-I", str(KAEPATCH)]
    # -Wno-misleading-indentation matches the colibri Makefile CFLAGS (the
    # manifest loop mirrors run_kae_score's upstream single-line style)
    for out_bin, extra in ((ref, []), (eng, ["-DKOT_DUMP_PATCH"])):
        p = subprocess.run(["gcc", "-O2", "-Wall", "-Wextra", "-Wno-unused-function",
                            "-Wno-misleading-indentation",
                            *extra, *inc, "-o", str(out_bin),
                            str(HERE / "mock_glm_dump.c"), "-lm"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        check(p.returncode == 0 and not p.stderr,
              "gcc %s: clean build, zero warnings" % out_bin.name)
        if p.returncode:
            sys.stderr.write(p.stderr.decode()); return 1

    # ---- fixed toy manifest (mixed T, -1 spans, arbitrary slot ids) ----
    LINES = [
        ([17, 4021, 9, 88371, 5, 6, 7],        [-1, 0, 0, -1, 95, -1, 7]),
        ([3, 3, 3, 99999, 12],                  [7, -1, -1, -1, 7]),
        ([500, 501, 502, 503, 504, 505, 506, 507, 508],
                                                [-1, -1, 42, -1, -1, -1, -1, 42, -1]),
        ([12000, 42],                           [-1, 3]),   # single gated position
    ]
    man = OUT / "man_main.txt"
    man.write_text("".join(
        "%d %s %s\n" % (len(ids), " ".join(map(str, ids)), " ".join(map(str, sp)))
        for ids, sp in LINES))
    denv = {"MOCK_D": D, "KAE_DUMP": man, "KAE_DUMP_OUT": OUT / "main.kaed",
            "KAE_DUMP_LAYERS": ",".join(map(str, LAYERS)), "KAE_SEED": SEED}

    print("== V1: KAE_DUMP-unset byte-identity vs the pre-dump engine ==")
    run(ref, man, OUT / "fwd_ref.bin", {"MOCK_D": D}, label="ref")
    run(eng, man, OUT / "fwd_unset.bin", {"MOCK_D": D}, label="dump-unset")
    a = (OUT / "fwd_ref.bin").read_bytes(); b = (OUT / "fwd_unset.bin").read_bytes()
    check(len(a) == sum(len(i) for i, _ in LINES) * D * 4 and a == b,
          "[MEASURED] dump binary, KAE_DUMP unset: forward BYTE-IDENTICAL to pre-dump engine")
    p = run(eng, man, OUT / "fwd_armed.bin", denv, label="dump-armed")
    check((OUT / "fwd_armed.bin").read_bytes() == a,
          "[MEASURED] dump ARMED: forward STILL byte-identical (capture is read-only)")

    print("== V2: dumped sums == independent f64 re-derivation, cell-exact ==")
    n_lines, nl, gD, layers, per = parse_kaed(OUT / "main.kaed")
    check(n_lines == len(LINES) and nl == len(LAYERS) and gD == D,
          "KAED header: n_lines=%d nl=%d D=%d" % (n_lines, nl, gD))
    check(layers == LAYERS, "KAED layer ids in KAE_DUMP_LAYERS order %s" % LAYERS)
    want = rederive(LINES, LAYERS, D)
    cells = bad = 0
    for (gc, sums), (wgc, wsums), (ids, sp) in zip(per, want, LINES):
        check(gc == wgc, "gated_count %d == expected %d" % (gc, wgc))
        for got, w in zip(sums, wsums):
            cells += 1
            if got != f32(w):
                bad += 1
    check(bad == 0, "[MEASURED] every dumped cell (%d) == f64 re-derivation cast to f32, bit-exact"
          % cells)

    print("== V3: provenance echo (carrier-HOLD fix 5) ==")
    err = p.stderr.decode()
    m = ECHO_RE.search(err)
    check(m is not None, "[MEASURED] '[KAE-DUMP] armed:' echo fires on stderr (pinned ECHO_RE)")
    check(m and m.group(1) == str(SEED),
          "[MEASURED] echoed seed == KAE_SEED == registered CONSTRUCTION_SEED %d" % SEED)
    check(err.index(m.group(0)) < err.index("[kae-dump done"),
          "echo precedes results (parsed before any dump byte is consumed)")
    p2 = run(eng, man, OUT / "fwd_noseed.bin",
             {k: v for k, v in denv.items() if k != "KAE_SEED"}, label="no-seed")
    m2 = ECHO_RE.search(p2.stderr.decode())
    check(m2 is not None and m2.group(1) != str(SEED),
          "KAE_SEED absent -> echo seed '-' != registered seed (harness fails closed)")

    print("== V4: gated-positions-only + chunked-prefill equivalence ==")
    gc4, sums4 = per[3]
    ids4, sp4 = LINES[3]
    single = [hid(fnv1a_ids(ids4[:2]), layer, 1, d) for layer in LAYERS for d in range(D)]
    check(gc4 == 1 and all(g == f32(w) for g, w in zip(sums4, single)),
          "[MEASURED] single-gated line: sum == exactly that position's hidden state")
    denv_c = dict(denv); denv_c["KAE_DUMP_OUT"] = OUT / "chunk.kaed"; denv_c["CHUNK"] = 3
    run(eng, man, OUT / "fwd_chunk.bin", denv_c, label="chunked")
    check((OUT / "chunk.kaed").read_bytes() == (OUT / "main.kaed").read_bytes(),
          "[MEASURED] CHUNK=3 prefill (advancing pos_base): .kaed byte-identical")

    print("== V5: fail-closed battery (every case must exit nonzero) ==")
    man_zero = OUT / "man_zero.txt"
    man_zero.write_text("3 5 6 7 -1 -1 -1\n")
    man_badtok = OUT / "man_badtok.txt"
    man_badtok.write_text("3 5 xx 7 0 -1 -1\n")
    # gate-0 item-5 negatives: a wholly non-numeric line and trailing junk
    # after the 2T+1 required integers must ABORT, never be silently skipped
    man_garbage = OUT / "man_garbage.txt"
    man_garbage.write_text("2 5 6 -1 3\nthis line is garbage not integers\n")
    man_trail = OUT / "man_trail.txt"
    man_trail.write_text("2 5 6 -1 3 99\n")
    # r3 (gate-0 re-review finding 3) integer-hardening negatives: the r2
    # parser cast long->int unchecked, so 2147483648 wrapped negative and
    # kae_bind_spans normalised it to -1 — the line SUCCEEDED with the
    # malformed position silently ungated. Every case below must abort.
    man_spanwrap = OUT / "man_spanwrap.txt"
    man_spanwrap.write_text("2 5 6 -1 2147483648\n")
    man_spanrange = OUT / "man_spanrange.txt"
    man_spanrange.write_text("2 5 6 -1 99999999999999999999\n")
    man_tokrange = OUT / "man_tokrange.txt"
    man_tokrange.write_text("2 5 99999999999999999999 -1 3\n")
    man_bigT = OUT / "man_bigT.txt"
    man_bigT.write_text("2147483648 5 6\n")
    cases = [
        ("KAE_DUMP + KAE_SCORE (phase separation)", man, dict(denv, KAE_SCORE="x")),
        ("KAE_DUMP + KAE=1 (phase separation)",     man, dict(denv, KAE=1)),
        ("missing KAE_DUMP_OUT",  man, {k: v for k, v in denv.items() if k != "KAE_DUMP_OUT"}),
        ("missing KAE_DUMP_LAYERS", man, {k: v for k, v in denv.items() if k != "KAE_DUMP_LAYERS"}),
        ("duplicate dump layer",  man, dict(denv, KAE_DUMP_LAYERS="5,5")),
        ("dump layer out of range", man, dict(denv, KAE_DUMP_LAYERS="5,%d" % NLAYERS)),
        ("zero gated positions",  man_zero, dict(denv, KAE_DUMP=man_zero)),
        ("malformed token id",    man_badtok, dict(denv, KAE_DUMP=man_badtok)),
        ("dump layer never reaches moe() (dense layer 1)", man,
         dict(denv, KAE_DUMP_LAYERS="5,1")),
        ("[MEASURED] garbage manifest line (wholly non-numeric, not skipped)",
         man_garbage, dict(denv, KAE_DUMP=man_garbage)),
        ("[MEASURED] trailing junk after the required 2T+1 integers",
         man_trail, dict(denv, KAE_DUMP=man_trail)),
        ("[MEASURED] span slot 2147483648 (int wrap) aborts, never a "
         "silently ungated position (r3 finding 3)",
         man_spanwrap, dict(denv, KAE_DUMP=man_spanwrap)),
        ("[MEASURED] long-overflowing (ERANGE) span slot aborts (r3)",
         man_spanrange, dict(denv, KAE_DUMP=man_spanrange)),
        ("[MEASURED] long-overflowing (ERANGE) token id aborts (r3)",
         man_tokrange, dict(denv, KAE_DUMP=man_tokrange)),
        ("[MEASURED] pass-1 T=2147483648 (unrepresentable as int) aborts "
         "before kv sizing (r3)",
         man_bigT, dict(denv, KAE_DUMP=man_bigT)),
        ("[MEASURED] manifest READ ERROR (directory path) aborts (r3)",
         OUT, dict(denv, KAE_DUMP=OUT)),
    ]
    for label, mpath, env in cases:
        pr = run(eng, mpath, OUT / "fwd_probe.bin", env, expect_rc=1, label=label)
        check(pr.returncode != 0, "%s -> nonzero exit" % label)
    # boundary POSITIVE control (r3): the hardening must not over-reject —
    # span slot 2147483646 (= INT_MAX-1, the largest representable slot)
    # still parses, binds and gates its position.
    man_big = OUT / "man_bigslot.txt"
    man_big.write_text("2 100 200 -1 2147483646\n")
    denv_b = dict(denv)
    denv_b["KAE_DUMP"] = man_big
    denv_b["KAE_DUMP_OUT"] = OUT / "bigslot.kaed"
    run(eng, man_big, OUT / "fwd_bigslot.bin", denv_b, label="bigslot")
    nb, nlb, Db, layb, perb = parse_kaed(OUT / "bigslot.kaed")
    check(nb == 1 and perb[0][0] == 1,
          "[MEASURED] boundary span slot 2147483646 ACCEPTED and gated "
          "(gc==1) — no over-rejection (r3)")

    print("== V6: in-patch unit suite (plain + ASan/UBSan/LSan) ==")
    with tempfile.TemporaryDirectory() as td:
        c = Path(td) / "c"; (c / "tests").mkdir(parents=True)
        (c / "kae.h").write_bytes((KAEPATCH / "kae.h").read_bytes())
        (c / "kae_dump.h").write_bytes((HERE / "kae_dump.h").read_bytes())
        (c / "tests" / "test_kae_dump.c").write_bytes(
            (HERE / "test_kae_dump.c").read_bytes())
        for tag, extra in (("plain", ["-O2"]),
                           ("asan", ["-O1", "-g", "-fsanitize=address,undefined",
                                     "-fno-omit-frame-pointer"])):
            tb = Path(td) / ("t_" + tag)
            pb = subprocess.run(["gcc", *extra, "-Wall", "-Wextra",
                                 "-Wno-unused-function", "-o", str(tb),
                                 str(c / "tests" / "test_kae_dump.c"), "-lm"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            check(pb.returncode == 0 and not pb.stderr,
                  "test_kae_dump %s build: clean, zero warnings" % tag)
            if pb.returncode:
                continue
            pt = subprocess.run([str(tb)], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
            out = pt.stdout.decode() + pt.stderr.decode()
            n_ok = out.count("\n  ok:")
            check(pt.returncode == 0 and "ALL TESTS PASSED" in out,
                  "[MEASURED] test_kae_dump (%s): ALL TESTS PASSED (%d checks)"
                  % (tag, n_ok))
            if tag == "asan":
                check("Sanitizer" not in out and "runtime error" not in out,
                      "ASan/UBSan/LSan: no diagnostics")

    print()
    if fails:
        print("MOCK VALIDATION FAILED (%d failing check%s)"
              % (fails, "" if fails == 1 else "s"))
        return 1
    print("MOCK VALIDATION PASS — kot-f1k-dump/1 mock battery green "
          "(MOCK SCOPE ONLY: mechanics, not feasibility; the real-engine "
          "objdump inertness proof re-runs on Modal at bring-up)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
