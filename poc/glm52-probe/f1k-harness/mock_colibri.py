#!/usr/bin/env python3
"""mock_colibri.py — deterministic STUB of the colibri engine's KAE_SCORE path.

MOCK ONLY. Never used in a real run; f1k_driver.py --mock points its engine at
this stub so the ENTIRE protocol wiring (arm construction, manifest format,
scorer readout, guard byte-identity, checkpoint/resume, analysis-input schema)
is validated end-to-end for $0 — no model, no weights, no instance, no spend.

It speaks the EXACT interface of the patched colibri engine
(poc/glm52-probe/kae-patch-draft/kae-add-path.patch, run_kae_score),
INCLUDING the real engine's out-of-band chatter (codex review blocker 1: the
driver must never assume "first stdout line = result"):

  stdout STARTUP BANNERS (mirroring glm.c main()):
      "== GLM C engine (glm_moe_dsa), cache=... =="
      "loaded in ...s | resident dense: ... | layers=... experts=..."
  stderr KaE LOAD SIGNALS (mirroring glm.c main() / kae_load):
      armed  : "[KAE] ADD-path armed (DRAFT/gate-0): <nc> concepts, <nl>
                splice layers, g=<%.3f>; spans per-item (none at load)
                (KAE_SCORE binds per item)"
      failed : "[KAE] load failed -> KaE DISABLED (running unmodified)"
  stderr PROGRESS (mirroring run_kae_score's per-5-item line):
      "[kae-score N item | ...]"

  input  (env KAE_SCORE=<manifest>): one item per line, whitespace ints:
      T K  t_0..t_{T-1}  l_0..l_{K-1}  s_0..s_{T-1}
      (frozen-template tokens, K single-token answer-LABEL token ids in
       PUBLISHED order, per-position concept-id spans, -1 = ungated —
       design §R1.1 / patch README "Scoring")
  output (stdout, one line per item):
      "<pred_label_index> <pred_token_id> <logit_l0> .. <logit_lK-1>"
      argmax over the K label logits, deterministic tie-break = lowest label
      index (mirrors kae_argmax_label in kae.h: strict > comparison)
  env    KAE / KAE_CARRIER / KAE_G / KAE_MODE honoured with the engine's
      semantics: the splice can influence output ONLY at gated positions —
      an item whose spans are all -1 (the off-concept guard set, design
      §2.5) produces BYTE-IDENTICAL output whether or not KAE=1, exactly
      like the real engine's `if(g_kae && m->kae) kae_apply_add(...)` no-op
      on ungated rows. A span concept-id >= the carrier's nc yields
      "ERR item" exactly like run_kae_score's parse validation.

  KAE_MODE=1 (REPLACE) — MOCK-ONLY DIVERGENCE, DOCUMENTED: the real gate-0
      patch stubs REPLACE (kae_apply_add returns early on mode!=0), which
      f1k_driver's dev-96 stub-detection catches fail-closed. THIS stub
      implements a distinct REPLACE effect (slightly different planted
      accuracy + mode-keyed logits) precisely so the driver's conditional-
      REPLACE gate (§R-REV4.3 delta_R measurement -> RUN/DEFER -> scheduled
      pass) is exercisable end-to-end for $0.

Determinism: every "logit" is a pure SHA-256 function of (salt, template
tokens, label ids, and — only when the gate fires — the carrier file bytes,
g, and mode). No wall clock, no PRNG state, no filesystem side effects.

MOCK-ONLY side channels (documented deviations, not part of the real
interface):
  MOCK_GOLD=<file>  one gold label index per manifest line. Lets the stub
      plant a per-arm accuracy so the mock campaign reaches a non-trivial
      verdict shape in analysis/f1k.py (mirroring that script's own
      --selftest planted-lift campaign). The KAE_SCORE manifest bytes stay
      EXACTLY the real format; the real engine never sees MOCK_GOLD.
  MOCK_KAE_FORCE_LOAD_FAIL=1  fault injection: report the engine's
      carrier-load-failure path (KaE DISABLED, runs unmodified) so
      f1k_driver's fail-closed engagement check is provably exercised.
  Planted accuracies (per carrier-family basename; the same per-item uniform
  draw u is shared across arms with the same template, so b0/d0/d1-drng score
  identically item-by-item and K adds a clean +10-pt lift — the analysis
  mock-A shape):
      no splice or ungated : p = 0.70   (b0, d3-text, guard items)
      *d0*, *drng*         : p = 0.70   (placebo / derangements == b0 draws)
      *d2*                 : p = 0.78
      *k-true* / other K   : p = 0.80   (0.79 under KAE_MODE=1 REPLACE, so
                                         dev delta_R is small -> gate RUN)
"""
import hashlib
import os
import struct
import sys


def unit(*parts):
    """Deterministic uniform in [0,1) from SHA-256 over the parts."""
    h = hashlib.sha256("|".join(str(p) for p in parts).encode()).digest()
    return int.from_bytes(h[:8], "big") / 2.0 ** 64


def family_p(carrier_path, mode):
    b = os.path.basename(carrier_path or "").lower()
    if "drng" in b or "d0" in b:
        p = 0.70
    elif "d2" in b:
        p = 0.78
    else:
        p = 0.80  # K family
    if mode == 1:
        p -= 0.01  # REPLACE: slightly different planted effect (mock-only)
    return p


def kaec_dims(path):
    """nc/nl from the KAEC header (for the armed banner + span validation,
    mirroring kae_load/run_kae_score)."""
    with open(path, "rb") as f:
        raw = f.read(16)
    if len(raw) < 16 or raw[:4] != b"KAEC":
        return None
    nc, nl, _d = struct.unpack_from("<iii", raw, 4)
    if nc <= 0 or nl <= 0:
        return None
    return nc, nl


def main():
    manifest = os.environ.get("KAE_SCORE")
    if not manifest:
        print("mock_colibri: KAE_SCORE=<manifest> required", file=sys.stderr)
        return 1
    kae = os.environ.get("KAE", "0") == "1"
    carrier = os.environ.get("KAE_CARRIER")
    g = os.environ.get("KAE_G", "1.0")
    mode = int(os.environ.get("KAE_MODE", "0") or 0)

    # --- startup banners on STDOUT, exactly where the real engine prints
    # them (before any KAE_SCORE result line) ---
    print("== GLM C engine (glm_moe_dsa), cache=64 experts/layer | "
          "experts@4-bit dense@8-bit | idot: mock ==")
    sys.stdout.flush()

    nc = nl = None
    if kae:
        dims = None
        forced_fail = os.environ.get("MOCK_KAE_FORCE_LOAD_FAIL") == "1"
        if carrier and os.path.exists(carrier) and not forced_fail:
            dims = kaec_dims(carrier)
        if dims is None:
            # engine behaviour: load failure -> KaE DISABLED, unmodified run
            print("[KAE] load failed -> KaE DISABLED (running unmodified)",
                  file=sys.stderr)
            sys.stderr.flush()
            kae = False
        else:
            nc, nl = dims
            print("[KAE] ADD-path armed (DRAFT/gate-0): %d concepts, %d "
                  "splice layers, g=%.3f; spans per-item (none at load) "
                  "(KAE_SCORE binds per item)" % (nc, nl, float(g)),
                  file=sys.stderr)
            sys.stderr.flush()
    print("loaded in 0.01s | resident dense: 0.00 MB | layers=12 "
          "experts=64 | MTP off (draft=0)")
    sys.stdout.flush()

    carrier_tag = ""
    if kae and carrier:
        with open(carrier, "rb") as f:
            carrier_tag = hashlib.sha256(f.read()).hexdigest()
    salt = os.environ.get("MOCK_SALT", "f1k-mock-v1")
    golds = None
    gp = os.environ.get("MOCK_GOLD")
    if gp and os.path.exists(gp):
        with open(gp) as f:
            golds = [int(x) for x in f.read().split()]

    lineno = -1
    with open(manifest) as f:
        for raw in f:
            toks = raw.split()
            if not toks:
                continue
            lineno += 1
            try:
                T, K = int(toks[0]), int(toks[1])
                ids = [int(x) for x in toks[2:2 + T]]
                labs = [int(x) for x in toks[2 + T:2 + T + K]]
                spans = [int(x) for x in toks[2 + T + K:2 + T + K + T]]
                if len(ids) != T or len(labs) != K or len(spans) != T:
                    raise ValueError("short line")
            except (ValueError, IndexError):
                print("ERR item")           # engine emits ERR on a bad line
                sys.stdout.flush()
                continue
            if kae and nc is not None and any(s >= nc for s in spans):
                # mirrors run_kae_score's span validation (v >= m->kae->nc)
                print("ERR item")
                sys.stdout.flush()
                continue
            gated = kae and any(s >= 0 for s in spans)
            tmpl = ",".join(map(str, ids))
            lstr = ",".join(map(str, labs))
            # base logits: carrier/g/mode may shift them ONLY when gated
            mix = (carrier_tag, g, str(mode)) if gated else ("", "", "")
            logits = [4.0 * unit(salt, "logit", i, tmpl, lstr, *mix) - 2.0
                      for i in range(K)]
            if golds is not None and lineno < len(golds):
                gold = golds[lineno] % K
                # per-item draw SHARED across arms (template-keyed, not
                # carrier-keyed) so paired diffs are clean
                u = unit(salt, "u", tmpl, lstr)
                p = family_p(carrier, mode) if gated else 0.70
                win = gold if u < p else (gold + 1) % K
                logits[win] = max(logits) + 3.0
            # readout mirrors kae_argmax_label: strict > (lowest-index ties)
            best = 0
            for i in range(1, K):
                if logits[i] > logits[best]:
                    best = i
            sys.stdout.write("%d %d" % (best, labs[best]))
            for v in logits:
                sys.stdout.write(" %.6f" % v)
            sys.stdout.write("\n")
            sys.stdout.flush()              # engine flushes per item too
            if (lineno + 1) % 5 == 0:
                # mirrors run_kae_score's per-5-item stderr progress line
                print("[kae-score %d item | 0.0s | RSS 0.00 GB | hit 0%%]"
                      % (lineno + 1), file=sys.stderr)
                sys.stderr.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
