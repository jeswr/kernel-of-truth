#!/usr/bin/env python3
"""mock_colibri_dump.py — deterministic STUB of the colibri engine's
kot-f1k-dump/1 hidden-state DUMP path (the DES §2.8 item-3 construction
mode; see build_carriers.py module docstring for the full contract).

MOCK ONLY — never part of a real run. build_carriers.py points its
--engine-cmd here so the ENTIRE carrier-construction pipeline (manifest ->
tokenize -> forward-pass dump -> §2.4 mean difference -> .kaec masters ->
norms -> driver acceptance) validates end-to-end for $0: no model, no
weights, no instance, no spend. The REAL engine is the pinned colibri build
plus the runner's bring-up construction-only dump patch.

Interface (exactly kot-f1k-dump/1):
  env  KAE_DUMP=<manifest> | KAE_DUMP_OUT=<path> | KAE_DUMP_LAYERS=<csv>
       | KAE_SEED (echoed to stderr, consulted by NO arithmetic — the real
       dump path is sampling-free)
  in   one line per pass:  T  t_0..t_{T-1}  s_0..s_{T-1}   (KAE_SCORE span
       convention: -1 = ungated)
  out  "KAED" | i32 n_lines | i32 nl | i32 D | i32 layer_id[nl] | per line:
       i32 gated_count | f32 sum[nl*D]  (little-endian; sum over gated
       positions of the moe()-input hidden state per layer)
  stdout: startup banners exactly like the scoring engine (results never on
       stdout — codex blocker-1 discipline); stderr: progress.

Determinism (the property the real engine supplies via fixed weights +
greedy prefill): the stub hidden state at (layer, position p) is a pure
SHA-256 function of (salt, layer, the FULL TOKEN PREFIX t_0..t_p, p) —
CAUSAL, so prepending an explication changes the states at the (shifted)
gated positions, giving non-trivial §2.4 mean differences, while the
matched context without the prepend yields different states. D = 6144
(the frozen kaec_format hidden dim). No wall clock, no global PRNG state.
"""
import hashlib
import os
import random
import struct
import sys

D = 6144   # frozen kaec_format hidden dim [PATCH kae.h; generator-spec]


def hidden(salt, layer, prefix_key, pos):
    seed = int.from_bytes(
        hashlib.sha256(("%s|dump|l=%d|p=%d|%s"
                        % (salt, layer, pos, prefix_key)).encode()).digest()[:8],
        "big")
    r = random.Random(seed)
    return [r.uniform(-1.0, 1.0) for _ in range(D)]


def main():
    man = os.environ.get("KAE_DUMP")
    out = os.environ.get("KAE_DUMP_OUT")
    lay = os.environ.get("KAE_DUMP_LAYERS")
    if not (man and out and lay):
        print("mock_colibri_dump: KAE_DUMP/KAE_DUMP_OUT/KAE_DUMP_LAYERS "
              "required", file=sys.stderr)
        return 1
    layers = [int(x) for x in lay.split(",")]
    salt = os.environ.get("MOCK_SALT", "f1k-mock-v1")
    print("== GLM C engine (glm_moe_dsa), cache=64 experts/layer | "
          "experts@4-bit dense@8-bit | idot: mock ==")
    print("loaded in 0.01s | resident dense: 0.00 MB | layers=%d "
          "experts=64 | MTP off (draft=0)" % max(layers))
    sys.stdout.flush()
    print("[KAE-DUMP] armed: %d layers, D=%d, seed=%s (provenance echo; "
          "dump path consults no RNG)"
          % (len(layers), D, os.environ.get("KAE_SEED", "-")),
          file=sys.stderr)
    lines = []
    with open(man) as f:
        for raw in f:
            toks = raw.split()
            if not toks:
                continue
            T = int(toks[0])
            ids = [int(x) for x in toks[1:1 + T]]
            spans = [int(x) for x in toks[1 + T:1 + 2 * T]]
            if len(ids) != T or len(spans) != T:
                print("[KAE-DUMP] malformed line -> abort", file=sys.stderr)
                return 1
            lines.append((ids, spans))
    with open(out, "wb") as f:
        f.write(b"KAED")
        f.write(struct.pack("<iii", len(lines), len(layers), D))
        f.write(struct.pack("<%di" % len(layers), *layers))
        for n, (ids, spans) in enumerate(lines):
            gated = [p for p, s in enumerate(spans) if s >= 0]
            if not gated:
                print("[KAE-DUMP] line %d has zero gated positions -> "
                      "abort" % n, file=sys.stderr)
                return 1
            f.write(struct.pack("<i", len(gated)))
            for layer in layers:
                acc = [0.0] * D
                for p in gated:
                    # causal prefix key: states depend on the full prefix
                    pk = hashlib.sha256(
                        (",".join(map(str, ids[:p + 1]))).encode()
                    ).hexdigest()
                    h = hidden(salt, layer, pk, p)
                    for i in range(D):
                        acc[i] += h[i]
                f.write(struct.pack("<%df" % D, *acc))
            if (n + 1) % 16 == 0:
                print("[kae-dump %d line | 0.0s | RSS 0.00 GB]" % (n + 1),
                      file=sys.stderr)
                sys.stderr.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
