#!/usr/bin/env python3
"""build_carriers.py — the F1-K CARRIER-CONSTRUCTION GENERATOR (DES §2.4).

THE (A)->construction->(B0) instrument. This is the runnable, deterministic
software that freeze-manifest (A) requires ("the COMPLETE carrier GENERATOR
... Given (A), every arm's carrier table and realized norm is a deterministic
function of frozen rules — no free choice after the first dollar" [REG
design.n_planned.freeze_manifest.A_pre_spend]). It takes the (A)-time
generator components under data/f1k-carriers-v1/generator/ (construction
contexts, concept texts, carrier-index map, registered derangements), runs
GLM-5.2 (colibri) FORWARD PASSES on the construction contexts in hidden-state
dump mode, computes the DES §2.4 MEAN DIFFERENCE, and writes the realized
.kaec master tables for EVERY arm (K, d0, d2, the 3 main derangements, the
pilot-panel derangement) plus the raw/rescaled norms — the (B0) pure-function
addendum completing corpus pin f1k-carriers-v1 [REG freeze_manifest
B0_pre_pilot / DES §R-REV3.3].

FABLE-side artifact (kernel-construction design; the software that
deterministically generates the kernel). The run driver f1k_driver.py only
LOADS the tables this generator writes (cfg[carriers][*][path]); it never
constructs them. Bead kernel-of-truth-hh2d gap (3).

PHASE SEPARATION (the freeze ordering (A) -> construction spend -> (B0)):

  manifest   [$0, (A)-time]   deterministic construction MANIFEST: per
             concept slot, m = 16 contexts x 3 sequence variants (WITHOUT /
             WITH-K-explication / WITH-d2-dictionary) with char-level gated
             spans. Pure function of the (A) components; no model, no
             tokenizer, no spend. 96 x 16 x 3 = 4,608 rows.
  construct  [construction SPEND — or the $0 mock] verify the manifest
             CONTENT against a fresh (A)-spec re-derivation (byte-for-byte;
             count+seed alone are NOT accepted — carrier-HOLD fix 3),
             tokenize each sequence (kot-f1k-tok/1 contract), map char
             spans -> token positions (the template-spec.json intersection
             rule), run the engine's hidden-state dump (kot-f1k-dump/1
             contract) = the GLM-5.2 forward passes, VERIFY the engine's
             KAE_SEED provenance echo (carrier-HOLD fix 5), accumulate the
             §2.4 mean difference, generate d0 (kot-f1k-d0/1, seed 7) and
             the derangement tables, write the .kaec masters + norms + the
             run-config carriers fragment. Requires --mode {mock,real}
             (carrier-HOLD fix 1): every per-concept checkpoint and the
             construction report are BOUND to (mode, manifest_sha256,
             tokenizer_sha256, engine_weights_sha256, dump_patch_sha256,
             construction_seed, layers); a checkpoint whose binding differs
             from the current run in ANY field is REFUSED fail-closed, and
             a mode=mock checkpoint is categorically UNUSABLE in a
             mode=real construction (see `selftest`). In --mode real the
             layer list MUST equal the REGISTERED A(iv) candidate splice
             union (REGISTERED_SPLICE_LAYERS below — the 76 MoE layers
             3..78; carrier-HOLD fix 2); any other list fails closed.
             CACHED-RESUME re-checks (carrier RE-REVIEW 2026-07-16): a
             cached per-concept checkpoint is held to the SAME engine-echo
             requirement as a fresh batch — its stored engine_echo is
             RE-PARSED and the seed re-verified (item 5) — and its stored
             content (D == 6144, n_passes == 48, v_k/v_d2 shape +
             finiteness) is schema/integrity-checked, never consumed
             verbatim (item 8). REAL provenance shas are DERIVED from the
             --*-artifact bytes and compared to the asserted --*-sha pins
             (item 8); a bare 64-hex assertion is never accepted.
  verify     [$0] re-read the written tables and check EVERY bind the
             consumers enforce: KAEC format/geometry (kaec_format: D=6144,
             nc=96), the analysis's carriers arithmetic (params_added ==
             C*layers*D; table_bytes == 16 + 4*layers + 4*params_added ==
             actual file size [ANA sidecar.carriers coherence]), per-(c,l)
             norm matching within the driver's NORM_MATCH_RTOL, the
             seed-derangement reconstruction identity the driver's
             validate_panel enforces, the construction report's provenance
             BINDING (mode + manifest sha re-computed + fresh (A)-spec
             manifest re-derivation + table shas; --expect-mode is
             REQUIRED — carrier RE-REVIEW item 2: verify never runs
             mode-blind, so a mock table can never pass a real verify;
             a report claiming OR expected real is UNCONDITIONALLY held
             to the registered A(iv) layer set), and a FULL
             byte-for-byte re-derivation of the d0 table from kot-f1k-d0/1
             (every (c,l,dim) cell, exact f32 equality on the pinned
             toolchain — carrier-HOLD fix 6; the earlier 6-spot rtol check
             is superseded).
  selftest   [$0] fail-closed probes for the carrier-HOLD fixes + the
             carrier RE-REVIEW items (2026-07-16): a MOCK checkpoint
             (identical binding except mode) is REJECTED by a REAL
             construction end-to-end (subprocess, exit 2); a non-A(iv)
             layer list is REJECTED in real mode; a content-tampered
             manifest with unchanged row count and seed is REJECTED; a
             wrong / absent engine seed echo is REJECTED (fresh batch);
             a REAL asserted sha != the DERIVED artifact digest is
             REJECTED; a cached-resume checkpoint with a matching binding
             but wrong-seed / absent stored echo or tampered content
             (D != 6144) is REJECTED; verify without --expect-mode is
             REFUSED.

REGISTERED CONSTANTS (freeze-manifest (A) completion, 2026-07-16; every
value cites its source):

  CONSTRUCTION_SEED = 20260716   [REG freeze_manifest A(vii) "construction";
      registered at the freeze-(A) completion refreeze. The §2.4 pipeline's
      arithmetic is sampling-free (forward passes + means) and its only PRNG
      uses are the SEPARATELY-registered d0/derangement seeds, so this
      seed's registered role is DETERMINISM PROVENANCE: it is stamped into
      the construction manifest, exported to every engine invocation
      (KAE_SEED), and carried into the B0 addendum; any construction
      artifact carrying a different value fails closed at verify.]
  D0 DIRECTION ALGORITHM = kot-f1k-d0/1 (seed 7)   [REG A(vii) "d0 table 7"
      + the freeze-(A) completion registration; DES §2.6 d0 "norm-matched
      random vector"; the exact algorithm is d0_direction() below and the
      registered text in the frozen record — SHA-256 counter stream,
      Box-Muller normals, unit-normalized, scaled to ||v^K_{c,l}||.]
  M_CONTEXTS = 16, PREPEND separator = one blank line   [DES §2.4; OP-9]
  D_EXPECTED = 6144, NC = 96   [generator-spec kaec_format; PATCH kae.h]
  PASSES = 96 x 16 x 3 = 4,608 (WITHOUT shared between K and d2)
      [freeze-(A) completion: the §2.6 "same construction with substituted
      content" for d2 requires its own WITH-dictionary passes; the earlier
      3,072 figure counted K's 2 variants only]

ENGINE HIDDEN-STATE DUMP CONTRACT — kot-f1k-dump/1
(the DES §2.8 item-3 dump mode, ~50 lines in glm.c moe(); OUT OF SCOPE of
the gate-0 scoring patch [PATCH kae.h "harness-side"] — the runner
implements it at bring-up as a SEPARATE construction-only patch on top of
the pinned engine; all SCORING phases run the binary built from the pinned
gate-0 patch ONLY):

  env  KAE_DUMP=<manifest>     activates dump mode (mutually exclusive with
                               KAE_SCORE); KAE_DUMP_OUT=<path> output file;
                               KAE_DUMP_LAYERS=<csv of layer ids> = the
                               candidate splice-layer union [A(iv)];
                               KAE_SEED=<int> = CONSTRUCTION_SEED (provenance
                               echo; the dump path consults no RNG).
  echo (REQUIRED, carrier-HOLD fix 5): the engine MUST emit on stderr,
       before results, one line matching
         [KAE-DUMP] armed: <nl> layers, D=<D>, seed=<KAE_SEED> ...
       echoing the KAE_SEED value it actually received. construct CAPTURES
       stderr, parses this echo, and FAILS CLOSED if the line is absent or
       the echoed seed != the registered CONSTRUCTION_SEED; the verified
       echo line is recorded in every per-concept checkpoint and
       summarized in construction-report.json. (The mock engine already
       emits it; the runner's bring-up dump patch must too.)
  in   one line per pass, whitespace ints:  T  t_0..t_{T-1}  s_0..s_{T-1}
       (token ids then per-position span slots, -1 = ungated — the same
       span convention as KAE_SCORE [PATCH README "Scoring"]).
  out  (KAE_DUMP_OUT, little-endian):
         [4]="KAED" | i32 n_lines | i32 nl | i32 D | i32 layer_id[nl]
         then per line: i32 gated_count | f32 sum[nl*D]
       where sum[l*D + d] = the SUM over gated positions (s >= 0) of the
       moe()-INPUT hidden state component d at splice layer l, in the
       engine's own f32 [DES §2.4 "hidden states recorded at gated
       positions at the moe() input"]. A line with zero gated positions is
       an ERROR (the generator never emits one).
  stdout/stderr: startup banners exactly like the scoring path; results
       never travel on stdout (codex blocker-1 discipline).

TOKENIZER CONTRACT — kot-f1k-tok/1 (mirrors the template-spec.json
tokenizer_derivation_rule; the runner wraps the pinned GLM-5.2 tokenizer at
bring-up [ASM-1971]):

  subprocess argv; stdin JSONL {"text": <str>}; stdout JSONL
  {"ids": [<int>], "offsets": [[start, end], ...]} — Python-str character
  offsets, end-exclusive, one pair per token, no BOS-stripping or
  normalisation beyond the engine's own prefill path. Token t is GATED for
  slot s iff [start, end) intersects a char span with slot s
  [template-spec.json .tokenizer_derivation_rule.spans — the SAME rule].

REGISTERED MEAN-DIFFERENCE ARITHMETIC (bit-reproducible given the engine's
dump bytes): per line, mean-over-gated = sum / gated_count in IEEE-754
float64; per (concept, variant, layer): sequential float64 accumulation of
the 16 per-line means in context_index order, / 16; v_{c,l} =
mean_WITH[c,l] - mean_WITHOUT[c,l] componentwise in float64; every non-K
carrier rescaled per (c,l) to ||v^K_{c,l}|| (reference-norm rule, DES §R2)
in float64; values cast to f32 only at kaec_write. No other arithmetic.

ROUND-10 CONTENT AUTHENTICATION (carrier re-review concrete content gaps,
2026-07-16 — the round-9 metadata gates were confirmed sound; these close
the CONTENT-integrity holes):

  gap 1  THE ONLY REAL-RUN VERIFY PATH IS --expect-mode real, which
         enforces mode=real AND the A(iv) layers 3..78 AND D=6144 AND a
         MOCK-STACK DENYLIST (binding provenance shas must not equal any
         repo mock script's digest — a mock construction relabeled
         mode=real fails; a real report can never be satisfied by a mock
         table). The mock-mode verify is kept for TESTING ONLY: it refuses
         anything real-claiming, refuses to aim at the registered
         production corpus dir (data/f1k-carriers-v1 — which `construct
         --mode mock` equally refuses to write into), and stamps its PASS
         line MOCK SCOPE ONLY.
  gap 2  NON-DEGENERACY: every (c,l) vector of every table must pass
         drv.vector_degeneracy (all-zero / near-constant / below-min-
         variance / trivially-sparse bodies fail closed) — enforced at
         assembly, on every cached resume, at verify over every written
         table (an all-zero set previously satisfied EVERY verify check:
         0-norm tables norm-match, reconstruct and d0-re-derive as 0==0),
         and independently at driver ingest ([R10-2]).
  gap 3  CHECKPOINT CONTENT HASH: every per-concept checkpoint carries
         content_sha256 = sha256(kot-f1k-ckpt-content/1 | slot | layers |
         D | exact LE f64 bytes of v_k then v_d2), bound into the report
         as checkpoint_content_sha256[96]. construct RE-DERIVES it on
         every cached resume (content-tampered/slot-swapped/hashless
         checkpoints rejected); verify re-derives it from the workdir
         checkpoints when present; the driver requires the witness for
         any REAL ingest.
  gap 4  (driver-side, f1k_driver.py [R10-4]) campaign rows.jsonl resume
         state is content-hashed + bound to the run's pinned inputs, so a
         resume can never skip engine execution or inject foreign rows.

$0 GUARANTEE OF THIS FILE: nothing here contacts a model unless YOU point
--engine-cmd at one. The repo's mock pair (mock_colibri_dump.py +
mock_tokenizer.py) green-runs the ENTIRE pipeline for $0.

Usage:
  # (A)-time, $0 — write the deterministic construction manifest:
  python3 build_carriers.py manifest

  # $0 mock construction (mock geometry allowed; artifacts BOUND mode=mock,
  # categorically unusable in a real construction):
  python3 build_carriers.py construct --mode mock \
      --engine-cmd '["python3", "mock_colibri_dump.py"]' \
      --tokenizer-cmd '["python3", "mock_tokenizer.py"]' \
      --layers 1,2,3,5,7,8,9,11 --out <dir> [--workdir <ckpt dir>]

  # REAL construction (spend; layers MUST be the registered A(iv) union;
  # all three provenance shas AND the artifacts they are derived from are
  # REQUIRED — carrier RE-REVIEW item 8 (2026-07-16): each sha is
  # RE-DERIVED from the named artifact's actual bytes and compared to the
  # caller's asserted pin; a bare 64-hex assertion is never accepted):
  python3 build_carriers.py construct --mode real \
      --engine-cmd '[...]' --tokenizer-cmd '[...]' \
      --layers 3,4,...,78 \
      --tokenizer-sha <64hex> --tokenizer-artifact <path> \
      --engine-weights-sha <64hex> --engine-weights-artifact <path> \
      --dump-patch-sha <64hex> --dump-patch-artifact <path> \
      --out <dir> [--workdir <ckpt dir>]

  # $0 — re-verify a written table set against every consumer bind.
  # --expect-mode is REQUIRED (carrier RE-REVIEW item 2, 2026-07-16):
  # verify never runs mode-blind, so a mock artifact set can never
  # satisfy a caller who needed real:
  python3 build_carriers.py verify --out <dir> --expect-mode mock|real \
      [--layers ...]

  # $0 — fail-closed probes for the carrier-HOLD fixes:
  python3 build_carriers.py selftest
"""
import argparse
import hashlib
import json
import math
import os
import re
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "corpora"))
sys.path.insert(0, str(ROOT / "tools" / "registry"))

import f1k_driver as drv            # kaec_write/kaec_read/seeded_derangement
import build_corpora as bc          # [BC] OP-4 matcher + §R4 span resolution
import kot_common as kc             # kot-corpus-hash/1

GEN = ROOT / "data" / "f1k-carriers-v1" / "generator"
TRIGGER_MAP = ROOT / "data" / "f1k-trigger-map-v1" / "trigger-map.json"

# ---- registered constants (sources in the module docstring) ----------------
CONSTRUCTION_SEED = 20260716        # [REG freeze_manifest A(vii); registered
                                    #  at the freeze-(A) completion refreeze]
D0_SEED = drv.PILOT_D0_SEED         # 7    [REG A(vii) "d0 table 7"]
KDRNG_SEED = drv.PILOT_KDRNG_SEED   # 11   [REG A(vii) pilot-panel]
DRNG_SEEDS = list(drv.DRNG_SEEDS)   # [101, 102, 103]  [REG design.seeds]
NC = 96                             # [REG C_REGISTERED; carrier-index-map]
M_CONTEXTS = 16                     # [DES §2.4; generator-spec m_contexts]
D_EXPECTED = 6144                   # [generator-spec kaec_format "D = 6144"]
SEPARATOR = "\n\n"                  # OP-9: one blank line
VARIANTS = ("without", "with_k", "with_d2")   # 3 passes per (concept, ctx)
D0_DOMAIN = "kot-f1k-d0/1"          # versioned domain string, registered

# ---- A(iv) RESOLUTION (carrier-HOLD fix 2; registered at the carrier-
# pipeline hardening refreeze 2026-07-16) ------------------------------------
# The pinned GLM-5.2 config (num_hidden_layers=78, first_k_dense_replace=3;
# poc/glm52-probe/stage1-feasibility-manifest.md P0 config read) yields 76
# MoE layers at ENGINE layer ids 3..78 INCLUSIVE — the id space of the
# committed routing-stats files and of KAE_DUMP_LAYERS [MEASURED ASM-2342
# R3-amended: "the committed stats files span MoE layers 3-78 = 76 layers"].
# DES §2.3 pilot grid: L1 = one mid-stack MoE layer (~ layer 40), L2 = four
# evenly spaced mid-to-late, L3 = ALL MoE layers. L3 = ALL, so the A(iv)
# candidate splice union == the full MoE set, independent of L1/L2.
MOE_LAYERS = tuple(range(3, 79))    # 76 MoE layers, ids 3..78 [ASM-2342]
PILOT_LAYER_SETS = {                # DES §2.3 realization [STIPULATED,
    "L1": [40],                     #  registered A(iv)/pilot rider]: L1 =
    "L2": [40, 53, 65, 78],         #  the DES's own "~ layer 40"; L2 =
    "L3": list(MOE_LAYERS),         #  round(linspace(40, 78, 4)); L3 = ALL
}
REGISTERED_SPLICE_LAYERS = list(MOE_LAYERS)   # the ENFORCED A(iv) union
MODES = ("mock", "real")
HEX64_RE = re.compile(r"[0-9a-f]{64}\Z")
# kot-f1k-dump/1 REQUIRED provenance echo (carrier-HOLD fix 5)
ECHO_RE = re.compile(r"^\[KAE-DUMP\] armed:.*?\bseed=([0-9-]+)", re.M)
# binding fields every checkpoint/report carries (carrier-HOLD fix 1)
BINDING_FIELDS = ("mode", "manifest_sha256", "tokenizer_sha256",
                  "engine_weights_sha256", "dump_patch_sha256",
                  "construction_seed", "layers")

# ---- ROUND-10 CONTENT AUTHENTICATION (carrier re-review concrete content
# gaps, 2026-07-16) -----------------------------------------------------------
REAL_CORPUS_DIR = ROOT / "data" / "f1k-carriers-v1"
#   [R10-1] the REGISTERED production corpus location (corpus pin
#   f1k-carriers-v1; the (B0) addendum lands here). Mock-mode artifacts may
#   NEVER occupy it and a mock-scoped verify may never bless it: `construct
#   --mode mock` refuses an --out/--workdir under it, and `verify
#   --expect-mode mock` refuses an --out under it — the only verify path
#   that can bless the production location is the real one (mode=real AND
#   layers 3..78 AND D=6144 AND the mock-stack denylist below).
CKPT_CONTENT_DOMAIN = "kot-f1k-ckpt-content/1"
#   [R10-3] per-concept checkpoint CONTENT hash domain: sha256 over
#   (domain | slot | layers | D) + the exact little-endian f64 bytes of
#   v_k then v_d2. Bound into every checkpoint AND the construction
#   report; construct re-derives + compares it on every cached resume
#   (a content-tampered/slot-swapped checkpoint is rejected), and verify
#   re-derives it from the workdir checkpoints when they are present.
# [R10-1]/[R10-2] the mock-stack denylist + non-degeneracy floors are the
# DRIVER's (single implementation): drv.MOCK_STACK_SCRIPTS /
# drv.mock_stack_shas() / drv.vector_degeneracy() — see f1k_driver.py
# [R10] block for the registered floor values and their rationale.

ERR = "ERR_F1K_CARRIERGEN"

# arm table file names — the SAME basenames the driver's mock fixtures use
# (mock_colibri family_p keys off these; run-config carriers block points
# at them)
TABLES = {
    "K": "k-true.kaec",
    "d0": "d0-seed7.kaec",
    "d2": "d2-dict.kaec",
    "kdrng": "k-drng-11.kaec",
}


def fail(msg):
    print("%s: %s" % (ERR, msg), file=sys.stderr)
    raise SystemExit(2)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def under_real_corpus(path):
    """[R10-1] True iff path resolves inside the REGISTERED production
    corpus dir (data/f1k-carriers-v1)."""
    try:
        Path(path).resolve().relative_to(REAL_CORPUS_DIR.resolve())
        return True
    except ValueError:
        return False


def ckpt_content_sha256(slot, layers, v_k, v_d2):
    """[R10-3] The per-concept checkpoint CONTENT hash: sha256 over the
    exact little-endian f64 bytes of the §2.4 mean-difference vectors,
    domain-bound to (slot, layers, D) so a checkpoint can neither be
    content-tampered NOR swapped between concept slots/layer sets without
    detection. JSON round-trips Python floats exactly (repr), so the
    cached vectors re-hash byte-identically on resume."""
    h = hashlib.sha256()
    h.update(("%s|slot=%d|layers=%s|D=%d|" % (
        CKPT_CONTENT_DOMAIN, slot, ",".join(str(x) for x in layers),
        D_EXPECTED)).encode("utf-8"))
    h.update(struct.pack("<%dd" % len(v_k), *v_k))
    h.update(struct.pack("<%dd" % len(v_d2), *v_d2))
    return h.hexdigest()


def check_table_nondegeneracy(name, m, layers):
    """[R10-2] Full-coverage non-degeneracy over a loaded KAEC table (every
    (c, l) cell through drv.vector_degeneracy — all-zero / near-constant /
    below-min-variance / trivially-sparse bodies fail closed)."""
    nc, nl, D = m["nc"], m["nl"], m["D"]
    vals = m["vals"]
    for c in range(nc):
        for li in range(nl):
            base = (c * nl + li) * D
            reason = drv.vector_degeneracy(vals[base:base + D])
            if reason:
                fail("%s: DEGENERATE vector at (slot=%d, layer=%d): %s — "
                     "a real §2.4 mean-difference carrier is non-"
                     "degenerate; degenerate bodies are never written/"
                     "verified (carrier re-review round-10 gap 2)"
                     % (name, c, layers[li], reason))


# ---------------------------------------------------------------------------
# (A)-time inputs — loaded fail-closed against their registered shapes
# ---------------------------------------------------------------------------
def load_components():
    cim = json.loads((GEN / "carrier-index-map.json").read_text("utf-8"))
    if cim["nc"] != NC or len(cim["map"]) != NC:
        fail("carrier-index-map nc != %d" % NC)
    slots = {r["carrier_slot"]: r for r in cim["map"]}
    texts = {}
    for line in (GEN / "concept-texts.jsonl").read_text("utf-8").splitlines():
        r = json.loads(line)
        # re-verify the freeze-(A)(ii) text pins [ASM-2375]: sha over bytes
        for k in ("k_explication", "d2_dictionary"):
            got = hashlib.sha256(r[k + "_text"].encode("utf-8")).hexdigest()
            if got != r[k + "_sha256"]:
                fail("%s sha mismatch at slot %d (freeze-(A)(ii) text pin)"
                     % (k, r["carrier_slot"]))
        texts[r["carrier_slot"]] = r
    ctxs = {}
    for line in (GEN / "construction-contexts.jsonl") \
            .read_text("utf-8").splitlines():
        r = json.loads(line)
        ctxs.setdefault(r["carrier_slot"], []).append(r)
    for c in range(NC):
        got = sorted(x["context_index"] for x in ctxs.get(c, []))
        if got != list(range(M_CONTEXTS)):
            fail("slot %d: construction contexts != m=%d [DES §2.4]"
                 % (c, M_CONTEXTS))
        ctxs[c].sort(key=lambda x: x["context_index"])
    ders = json.loads((GEN / "derangements.json").read_text("utf-8"))
    # cross-check the registered realization against the OP-7 algorithm
    for seed in [KDRNG_SEED] + DRNG_SEEDS:
        want = drv.seeded_derangement(NC, seed)
        if ders["derangements"][str(seed)] != want:
            fail("derangements.json seed %d != OP-7 seeded_derangement "
                 "(registered realization drifted)" % seed)
    tmap = json.loads(TRIGGER_MAP.read_text("utf-8"))
    by_synset = {c["synset"]: c for c in tmap["concepts"]}
    triggers = {}
    for c in range(NC):
        syn = slots[c]["synset"]
        if syn not in by_synset:
            fail("slot %d synset %s absent from f1k-trigger-map-v1" % (c, syn))
        triggers[c] = by_synset[syn]["triggers"]
    return slots, texts, ctxs, ders, triggers


def own_trigger_spans(text, trig_list, slot):
    """G-lex spans of the concept's OWN triggers on the context text —
    the SAME matching rule as f1k-trigger-map-v1 (OP-4 case-insensitive
    whole-word + §R4 longest/earliest/lowest precedence), via the frozen
    [BC] matcher restricted to this one concept [generator-spec
    gated_position_rule; DES §2.3/§2.4]."""
    matchers = bc.compile_matchers(
        [{"triggers": trig_list, "index": slot}])
    return bc.find_spans(text, matchers)


# ---------------------------------------------------------------------------
# manifest — the (A)-time [$0] deterministic construction manifest
# ---------------------------------------------------------------------------
def build_manifest_rows():
    """The (A)-time deterministic construction rows — a pure function of the
    frozen generator components [REG A_pre_spend]. Shared by `manifest`
    (which writes them) and by construct/verify's CONTENT verification
    (carrier-HOLD fix 3: the on-disk manifest must equal this fresh
    re-derivation byte-for-byte; count+seed alone are never accepted)."""
    slots, texts, ctxs, _ders, triggers = load_components()
    rows = []
    for c in range(NC):
        k_text = texts[c]["k_explication_text"]
        d2_text = texts[c]["d2_dictionary_text"]
        for ctx in ctxs[c]:
            spans = own_trigger_spans(ctx["text"], triggers[c], c)
            if not spans:
                fail("slot %d ctx %d: zero own-trigger spans — the §2.4 "
                     "gated-position rule has nothing to dump at"
                     % (c, ctx["context_index"]))
            for variant in VARIANTS:
                if variant == "without":
                    prep = ""
                elif variant == "with_k":
                    prep = k_text + SEPARATOR       # OP-9 separator
                else:
                    prep = d2_text + SEPARATOR
                off = len(prep)
                rows.append({
                    "carrier_slot": c,
                    "context_index": ctx["context_index"],
                    "variant": variant,
                    "text": prep + ctx["text"],
                    "char_spans": [[s + off, e + off, slot]
                                   for s, e, slot in spans],
                    "construction_seed": CONSTRUCTION_SEED,
                })
    if len(rows) != NC * M_CONTEXTS * len(VARIANTS):
        fail("manifest row count %d != %d" % (len(rows), NC * M_CONTEXTS * 3))
    return rows


def check_manifest_against_spec(man_path, derived_rows=None):
    """Carrier-HOLD fix 3: the construction manifest is verified against a
    FRESH (A)-spec re-derivation, line by line, byte-for-byte. An altered
    text/span/seed with the same row count is REJECTED. Returns the rows."""
    if not man_path.exists():
        fail("construction-manifest.jsonl missing — run `manifest` first "
             "(the (A)-time step)")
    derived = derived_rows if derived_rows is not None \
        else build_manifest_rows()
    lines = man_path.read_text("utf-8").splitlines()
    if len(lines) != len(derived):
        fail("manifest row count %d != the (A)-spec derivation's %d"
             % (len(lines), len(derived)))
    for i, (line, want) in enumerate(zip(lines, derived)):
        if line != json.dumps(want, sort_keys=True):
            fail("construction-manifest row %d does not match the fresh "
                 "(A)-spec derivation (content drift — same row count is "
                 "NOT sufficient; carrier-HOLD fix 3)" % i)
    return derived


def cmd_manifest(_args):
    rows = build_manifest_rows()
    out = GEN / "construction-manifest.jsonl"
    with open(out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    print("construction manifest: %d rows (= %d concepts x m=%d x %d "
          "variants; WITHOUT shared between K and d2) -> %s\n"
          "sha256 %s" % (len(rows), NC, M_CONTEXTS, len(VARIANTS), out,
                         sha256_file(out)))
    return 0


# ---------------------------------------------------------------------------
# d0 — the REGISTERED placebo direction algorithm  [kot-f1k-d0/1]
# ---------------------------------------------------------------------------
def d0_direction(slot, layer_id, dim):
    """kot-f1k-d0/1 (REGISTERED at the freeze-(A) completion refreeze;
    seed = 7 [REG A(vii) 'd0 table 7']; DES §2.6 d0 'norm-matched random
    vector'). For carrier slot c and SPLICE LAYER ID l (the engine layer
    id, not the slot index — invariant to layer-set ordering):

      stream:  digest_j = SHA-256(utf8("kot-f1k-d0/1|seed=7|slot=<c>|"
               "layer=<l>|blk=<j>")), j = 0, 1, 2, ...
      uniforms: each 8-byte big-endian block of digest_j / 2^64 -> u in
               [0, 1); 4 uniforms per digest.
      normals (Box-Muller, both branches; float64):
               r = sqrt(-2 ln(1 - u1)); z1 = r cos(2 pi u2);
               z2 = r sin(2 pi u2)   — 4 normals per digest; take the
               first D in stream order.
      direction = z / ||z||_2 (float64); the d0 table entry at (c, l) is
      ||v^K_{c,l}|| * direction (reference-norm rule DES §R2; g applies
      after), cast to f32 only at kaec_write.

    Deterministic and stdlib-only; isotropic on the (D-1)-sphere. Raw
    (pre-rescale) d0 norm == 1.0 by construction and is recorded as such
    in the B0 norms artifact.

    REPRODUCIBILITY SCOPE (carrier-HOLD fix 6; supersedes the earlier
    'platform-independent byte-identical' over-claim): the SHA-256 stream
    and the uniforms are platform-independent, but math.log/cos/sin/sqrt
    delegate to the platform libm, whose last-ulp rounding is NOT
    standardized — so byte-identical reproduction is CLAIMED ONLY ON THE
    PINNED TOOLCHAIN (same CPython + libm as the construction run), where
    `verify` re-derives the ENTIRE d0 table cell-by-cell and requires
    exact f32 equality. Cross-platform reproduction is expected to agree
    to ~1 ulp per transcendental but is NOT claimed byte-exact."""
    z = []
    j = 0
    while len(z) < dim:
        dg = hashlib.sha256(("%s|seed=%d|slot=%d|layer=%d|blk=%d"
                             % (D0_DOMAIN, D0_SEED, slot, layer_id, j))
                            .encode("utf-8")).digest()
        for off in (0, 16):
            u1 = int.from_bytes(dg[off:off + 8], "big") / 2.0 ** 64
            u2 = int.from_bytes(dg[off + 8:off + 16], "big") / 2.0 ** 64
            r = math.sqrt(-2.0 * math.log(1.0 - u1))
            z.append(r * math.cos(2.0 * math.pi * u2))
            z.append(r * math.sin(2.0 * math.pi * u2))
        j += 1
    z = z[:dim]
    n = math.sqrt(sum(x * x for x in z))
    if n == 0.0:                       # measure-zero; fail closed anyway
        fail("d0 direction degenerate at (slot=%d, layer=%d)"
             % (slot, layer_id))
    return [x / n for x in z]


# ---------------------------------------------------------------------------
# construct — tokenize -> dump forward passes -> §2.4 means -> tables
# ---------------------------------------------------------------------------
def tokenize_all(tok_cmd, rows):
    """kot-f1k-tok/1: one subprocess, JSONL in/out, order-preserving."""
    inp = "".join(json.dumps({"text": r["text"]}) + "\n" for r in rows)
    proc = subprocess.run(tok_cmd, input=inp.encode("utf-8"),
                          stdout=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        fail("tokenizer-cmd failed (exit %d)" % proc.returncode)
    outs = proc.stdout.decode("utf-8").splitlines()
    if len(outs) != len(rows):
        fail("tokenizer returned %d lines for %d texts" % (len(outs),
                                                           len(rows)))
    toks = []
    for r, line in zip(rows, outs):
        t = json.loads(line)
        ids, offs = t["ids"], t["offsets"]
        if len(ids) != len(offs):
            fail("tokenizer ids/offsets length mismatch")
        spans = [-1] * len(ids)
        for i, (s, e) in enumerate(offs):
            for cs, ce, slot in r["char_spans"]:
                if s < ce and cs < e:      # template-spec intersection rule
                    spans[i] = slot
                    break
        if not any(s >= 0 for s in spans):
            fail("slot %d ctx %d %s: char spans map to zero gated tokens"
                 % (r["carrier_slot"], r["context_index"], r["variant"]))
        toks.append({"ids": ids, "spans": spans})
    return toks


def run_dump(engine_cmd, layers, manifest_rows, token_rows, dump_dir, tag):
    """One engine invocation over a batch of passes -> per-line
    (gated_count, f32 sums). Returns list of (count, list[f64] sums)."""
    dump_dir.mkdir(parents=True, exist_ok=True)
    man = dump_dir / ("%s.dump-manifest.txt" % tag)
    with open(man, "w", encoding="utf-8") as f:
        for tr in token_rows:
            parts = [str(len(tr["ids"]))] + [str(x) for x in tr["ids"]] \
                    + [str(x) for x in tr["spans"]]
            f.write(" ".join(parts) + "\n")
    out = dump_dir / ("%s.kaed" % tag)
    env = dict(os.environ)
    env["KAE_DUMP"] = str(man)
    env["KAE_DUMP_OUT"] = str(out)
    env["KAE_DUMP_LAYERS"] = ",".join(str(x) for x in layers)
    env["KAE_SEED"] = str(CONSTRUCTION_SEED)   # provenance echo, registered
    env.pop("KAE_SCORE", None)
    proc = subprocess.run(engine_cmd, env=env, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr.decode("utf-8", "replace")[-2000:])
        fail("engine dump failed (exit %d) for %s" % (proc.returncode, tag))
    # ---- kot-f1k-dump/1 REQUIRED provenance echo (carrier-HOLD fix 5) ----
    # KAE_SEED is exported above; the engine MUST echo the seed it actually
    # received on stderr. Absent or mismatched echo => fail closed BEFORE
    # any dump byte is consumed.
    err_text = proc.stderr.decode("utf-8", "replace")
    m = ECHO_RE.search(err_text)
    if not m:
        fail("engine provenance echo ABSENT for %s — kot-f1k-dump/1 "
             "requires '[KAE-DUMP] armed: ... seed=<KAE_SEED>' on stderr "
             "(carrier-HOLD fix 5)" % tag)
    if m.group(1) != str(CONSTRUCTION_SEED):
        fail("engine provenance echo MISMATCH for %s: engine echoed "
             "seed=%s but KAE_SEED=%d was exported [REG A(vii)] — the "
             "engine did not receive/acknowledge the registered "
             "construction seed" % (tag, m.group(1), CONSTRUCTION_SEED))
    echo_line = m.group(0).strip()
    raw = out.read_bytes()
    if len(raw) < 16 or raw[:4] != b"KAED":
        fail("bad KAED magic in %s" % out)
    n_lines, nl, D = struct.unpack_from("<iii", raw, 4)
    got_layers = list(struct.unpack_from("<%di" % nl, raw, 16))
    if got_layers != list(layers):
        fail("KAED layer ids %s != requested %s" % (got_layers, layers))
    if n_lines != len(token_rows):
        fail("KAED n_lines %d != %d" % (n_lines, len(token_rows)))
    if D != D_EXPECTED:
        fail("engine hidden dim D=%d != the frozen kaec_format D=%d"
             % (D, D_EXPECTED))
    off = 16 + 4 * nl
    per_line = []
    stride = nl * D
    for i in range(n_lines):
        (gc,) = struct.unpack_from("<i", raw, off)
        off += 4
        if gc <= 0:
            fail("KAED line %d gated_count %d <= 0" % (i, gc))
        sums = struct.unpack_from("<%df" % stride, raw, off)
        off += 4 * stride
        per_line.append((gc, sums))
    if off != len(raw):
        fail("KAED trailing bytes in %s" % out)
    # keep dump manifests (provenance); delete bulky dump bytes after read
    out.unlink()
    return per_line, D, echo_line


def cmd_script_sha(cmd_argv, what):
    """Mock-mode provenance derivation: sha256 of the LAST argv element
    that is an existing regular file (the mock script itself). Real mode
    never uses this — the runner supplies explicit pinned shas."""
    for a in reversed(cmd_argv):
        p = Path(a)
        if p.is_file():
            return sha256_file(p)
    fail("cannot derive a %s provenance sha from argv %r — no argv "
         "element is an existing file" % (what, cmd_argv))


def resolve_binding_shas(args, engine_cmd, tok_cmd):
    """Carrier-HOLD fix 1 + carrier RE-REVIEW item 8 (2026-07-16): the
    three engine-side provenance shas. real: --tokenizer-sha/
    --engine-weights-sha/--dump-patch-sha AND the matching --*-artifact
    paths are ALL REQUIRED; each sha is RE-DERIVED from the named
    artifact's actual bytes and must EQUAL the caller's asserted pin —
    a caller assertion of mere 64-hex syntax is never accepted (re-review
    item 8). mock: derived from the mock scripts' own bytes unless
    explicitly overridden — so editing a mock invalidates its checkpoints
    too."""
    tok_sha, eng_sha, patch_sha = (args.tokenizer_sha,
                                   args.engine_weights_sha,
                                   args.dump_patch_sha)
    if args.mode == "real":
        missing = [n for n, v in (("--tokenizer-sha", tok_sha),
                                  ("--engine-weights-sha", eng_sha),
                                  ("--dump-patch-sha", patch_sha),
                                  ("--tokenizer-artifact",
                                   args.tokenizer_artifact),
                                  ("--engine-weights-artifact",
                                   args.engine_weights_artifact),
                                  ("--dump-patch-artifact",
                                   args.dump_patch_artifact))
                   if not v]
        if missing:
            fail("--mode real requires %s (pinned provenance DERIVED from "
                 "the actual artifacts; fail-closed — carrier-HOLD fix 1 + "
                 "re-review item 8)" % ", ".join(missing))
        # re-review item 8: DERIVE each sha from the artifact bytes and
        # compare to the asserted pin — never accept 64-hex syntax alone
        for name, asserted, art in (
                ("tokenizer", tok_sha, args.tokenizer_artifact),
                ("engine-weights", eng_sha, args.engine_weights_artifact),
                ("dump-patch", patch_sha, args.dump_patch_artifact)):
            p = Path(art)
            if not p.is_file():
                fail("--%s-artifact %s is not a readable file — the real "
                     "provenance sha must be DERIVED from the actual "
                     "artifact bytes (re-review item 8)" % (name, art))
            derived = sha256_file(p)
            if derived != asserted:
                fail("--%s-sha %s does not match sha256(%s) = %s — the "
                     "asserted pin is not the artifact's actual digest; "
                     "refusing the caller assertion (re-review item 8)"
                     % (name, asserted, art, derived))
    else:
        tok_sha = tok_sha or cmd_script_sha(tok_cmd, "tokenizer")
        eng_sha = eng_sha or cmd_script_sha(engine_cmd, "engine")
        # the mock engine script IS the stand-in for the dump patch
        patch_sha = patch_sha or cmd_script_sha(engine_cmd, "dump-patch")
    for name, v in (("tokenizer_sha256", tok_sha),
                    ("engine_weights_sha256", eng_sha),
                    ("dump_patch_sha256", patch_sha)):
        if not HEX64_RE.fullmatch(v or ""):
            fail("%s %r is not 64 lowercase hex" % (name, v))
    return tok_sha, eng_sha, patch_sha


def make_binding(mode, man_path, layers, tok_sha, eng_sha, patch_sha):
    """The checkpoint/report provenance binding (carrier-HOLD fix 1):
    every construction artifact is bound to ALL of these; construct
    REFUSES any checkpoint whose binding differs in ANY field."""
    return {"mode": mode,
            "manifest_sha256": sha256_file(man_path),
            "tokenizer_sha256": tok_sha,
            "engine_weights_sha256": eng_sha,
            "dump_patch_sha256": patch_sha,
            "construction_seed": CONSTRUCTION_SEED,
            "layers": list(layers)}


def check_checkpoint_binding(ck_path, cached, binding):
    """Fail-closed checkpoint acceptance (carrier-HOLD fix 1). A mode
    mismatch gets its own explicit refusal: a MOCK checkpoint is
    categorically UNUSABLE in a REAL construction (and vice versa)."""
    got = cached.get("binding")
    if not isinstance(got, dict):
        fail("checkpoint %s carries NO provenance binding (legacy/unbound "
             "artifact) — refusing fail-closed; rebuild from scratch "
             "(carrier-HOLD fix 1)" % ck_path)
    if got.get("mode") != binding["mode"]:
        fail("checkpoint %s is a mode=%s artifact but this is a mode=%s "
             "construction — a MOCK checkpoint is UNUSABLE in a REAL "
             "construction (fail-closed; carrier-HOLD fix 1)"
             % (ck_path, got.get("mode"), binding["mode"]))
    bad = [k for k in BINDING_FIELDS if got.get(k) != binding[k]]
    if bad:
        fail("checkpoint %s binding mismatch on %s (checkpoint %r != "
             "current run %r) — it was built under different registered "
             "inputs; refusing to mix (carrier-HOLD fix 1)"
             % (ck_path, ",".join(bad),
                {k: got.get(k) for k in bad},
                {k: binding[k] for k in bad}))


def cmd_construct(args):
    engine_cmd = json.loads(args.engine_cmd)
    tok_cmd = json.loads(args.tokenizer_cmd)
    if args.mode not in MODES:
        fail("--mode must be one of %s" % (MODES,))
    layers = [int(x) for x in args.layers.split(",")]
    if layers != sorted(layers) or len(set(layers)) != len(layers):
        fail("--layers must be strictly ascending unique layer ids "
             "(kaec_format 'ascending' [PATCH kae.h])")
    # ---- A(iv) enforcement (carrier-HOLD fix 2) ---------------------------
    if args.mode == "real" and layers != REGISTERED_SPLICE_LAYERS:
        fail("--mode real: --layers != the REGISTERED A(iv) candidate "
             "splice union (the 76 MoE layers %d..%d of the pinned GLM-5.2 "
             "config [ASM-2342]); got %d ids %s... — any other list fails "
             "closed (carrier-HOLD fix 2)"
             % (REGISTERED_SPLICE_LAYERS[0], REGISTERED_SPLICE_LAYERS[-1],
                len(layers), layers[:6]))
    # ---- [R10-1] mock artifacts can never occupy the REGISTERED
    # production corpus location (data/f1k-carriers-v1): a mock table set
    # sitting where the real corpus pin resolves could otherwise be
    # blessed in place by a mock-scoped verify.
    if args.mode == "mock":
        for flag, p in (("--out", args.out), ("--workdir", args.workdir)):
            if p and under_real_corpus(p):
                fail("--mode mock: %s %s is inside the REGISTERED "
                     "production corpus dir %s — mock artifacts can NEVER "
                     "occupy the production location (carrier re-review "
                     "round-10 gap 1)" % (flag, p, REAL_CORPUS_DIR))
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    work = Path(args.workdir) if args.workdir else (outdir / "work")
    work.mkdir(parents=True, exist_ok=True)

    # ---- manifest CONTENT verification (carrier-HOLD fix 3) ---------------
    man_path = GEN / "construction-manifest.jsonl"
    rows = check_manifest_against_spec(man_path)
    tok_sha, eng_sha, patch_sha = resolve_binding_shas(args, engine_cmd,
                                                       tok_cmd)
    binding = make_binding(args.mode, man_path, layers, tok_sha, eng_sha,
                           patch_sha)
    _slots, _texts, _ctxs, ders, _trigs = load_components()

    nl, D = len(layers), None
    by_key = {}
    for r in rows:
        by_key.setdefault((r["carrier_slot"], r["variant"]), []).append(r)

    # ---- forward passes + §2.4 means, checkpointed per concept ------------
    # v[c][variant] = list of nl*D float64 (mean over m=16 context means)
    mdiff = {}     # (slot) -> {"K": [...], "d2": [...]}  (mean DIFFERENCES)
    content_shas = {}   # slot -> checkpoint content hash [R10-3]
    n_passes = 0
    echo_sample = None
    echo_verified = 0
    for c in range(NC):
        ck = work / ("concept-%03d.json" % c)
        if ck.exists():
            cached = json.loads(ck.read_text("utf-8"))
            # carrier-HOLD fix 1: full provenance binding, fail-closed;
            # mode=mock artifacts are UNUSABLE in a real construction
            check_checkpoint_binding(ck, cached, binding)
            # ---- cached-resume echo RE-VERIFICATION (carrier RE-REVIEW
            # item 5, 2026-07-16): a cached batch previously incremented
            # echo_verified and accepted the stored echo VERBATIM, so a
            # binding-matching checkpoint with no echo (or seed=999) was
            # accepted on resume. Now the stored engine_echo is RE-PARSED
            # and its seed re-verified against the registered
            # CONSTRUCTION_SEED — the SAME check a fresh batch gets in
            # run_dump; missing/unparseable/mismatched => reject.
            stored_echo = cached.get("engine_echo")
            m = ECHO_RE.search(stored_echo) \
                if isinstance(stored_echo, str) else None
            if not m:
                fail("checkpoint %s: stored engine provenance echo is "
                     "ABSENT/unparseable (%r) — a cached batch is held to "
                     "the same kot-f1k-dump/1 echo requirement as a fresh "
                     "one (cached-resume re-check, re-review item 5)"
                     % (ck, stored_echo))
            if m.group(1) != str(CONSTRUCTION_SEED):
                fail("checkpoint %s: stored engine echo seed=%s != the "
                     "registered construction seed %d [REG A(vii)] — "
                     "refusing the cached batch (cached-resume re-check, "
                     "re-review item 5)"
                     % (ck, m.group(1), CONSTRUCTION_SEED))
            # ---- cached-content schema/integrity (carrier RE-REVIEW
            # item 8, 2026-07-16): the stored payload (D, n_passes, v_k,
            # v_d2) is schema/shape/finiteness-checked, never consumed
            # verbatim — run_dump enforces D == D_EXPECTED and 48 passes
            # per concept for a fresh batch, so a cached one must carry
            # exactly the same.
            if cached.get("D") != D_EXPECTED:
                fail("checkpoint %s: D %r != the frozen kaec_format D=%d "
                     "(cached-content integrity, re-review item 8)"
                     % (ck, cached.get("D"), D_EXPECTED))
            if cached.get("n_passes") != M_CONTEXTS * len(VARIANTS):
                fail("checkpoint %s: n_passes %r != the per-concept %d "
                     "(= m=%d x %d variants; cached-content integrity, "
                     "re-review item 8)"
                     % (ck, cached.get("n_passes"),
                        M_CONTEXTS * len(VARIANTS), M_CONTEXTS,
                        len(VARIANTS)))
            for vname in ("v_k", "v_d2"):
                vv = cached.get(vname)
                if not isinstance(vv, list) or len(vv) != nl * D_EXPECTED:
                    fail("checkpoint %s: %s is not a list of nl*D = %d "
                         "floats (got %s of length %s; cached-content "
                         "integrity, re-review item 8)"
                         % (ck, vname, nl * D_EXPECTED,
                            type(vv).__name__,
                            len(vv) if isinstance(vv, list) else "n/a"))
                for x in vv:
                    if isinstance(x, bool) or \
                            not isinstance(x, (int, float)) or \
                            not math.isfinite(x):
                        fail("checkpoint %s: %s carries a non-finite/"
                             "non-numeric cell (%r) — refusing the cached "
                             "batch (cached-content integrity, re-review "
                             "item 8)" % (ck, vname, x))
            # ---- [R10-3] checkpoint CONTENT authentication (carrier
            # re-review round-10 gap 3): shape/finiteness alone accepted
            # ARBITRARY finite vector values on resume. The stored
            # content_sha256 (domain-bound to slot+layers+D over the exact
            # f64 bytes) is now RE-DERIVED from the stored vectors and
            # compared — a content-tampered or slot-swapped checkpoint is
            # rejected; a checkpoint without the hash predates content
            # authentication and is rebuilt, never trusted.
            stored_cs = cached.get("content_sha256")
            if not (isinstance(stored_cs, str)
                    and HEX64_RE.fullmatch(stored_cs)):
                fail("checkpoint %s carries NO content_sha256 — its vector "
                     "contents are unauthenticated (legacy/stripped "
                     "artifact); refusing fail-closed, rebuild from "
                     "scratch (round-10 gap 3)" % ck)
            want_cs = ckpt_content_sha256(c, layers, cached["v_k"],
                                          cached["v_d2"])
            if stored_cs != want_cs:
                fail("checkpoint %s: stored content_sha256 %s != the "
                     "re-derived hash %s over the stored v_k/v_d2 bytes "
                     "(slot=%d, layers, D bound) — the checkpoint's vector "
                     "CONTENT was tampered with/replaced; refusing the "
                     "cached batch (round-10 gap 3)"
                     % (ck, stored_cs[:16], want_cs[:16], c))
            # ---- [R10-2] cached vectors must be NON-DEGENERATE per
            # (variant, layer) cell — an all-zero/constant body with a
            # coherent hash is still never consumed.
            for vname in ("v_k", "v_d2"):
                vv = cached[vname]
                for li in range(nl):
                    reason = drv.vector_degeneracy(
                        vv[li * D_EXPECTED:(li + 1) * D_EXPECTED])
                    if reason:
                        fail("checkpoint %s: %s DEGENERATE at layer %d: "
                             "%s — a real §2.4 mean-difference carrier is "
                             "non-degenerate (round-10 gap 2)"
                             % (ck, vname, layers[li], reason))
            content_shas[c] = stored_cs
            mdiff[c] = {"K": cached["v_k"], "d2": cached["v_d2"]}
            D = cached["D"]
            n_passes += cached["n_passes"]
            echo_verified += 1
            echo_sample = echo_sample or stored_echo
            continue
        batch = []
        for variant in VARIANTS:
            vs = sorted(by_key[(c, variant)],
                        key=lambda r: r["context_index"])
            if len(vs) != M_CONTEXTS:
                fail("slot %d %s: %d rows" % (c, variant, len(vs)))
            batch.extend(vs)
        toks = tokenize_all(tok_cmd, batch)
        per_line, D, echo_line = run_dump(engine_cmd, layers, batch, toks,
                                          work, "concept-%03d" % c)
        echo_verified += 1
        echo_sample = echo_sample or echo_line
        n_passes += len(batch)
        # registered arithmetic: per-line mean = sum/count (f64); per
        # (variant, layer): sequential f64 accumulation in context order
        acc = {v: [0.0] * (nl * D) for v in VARIANTS}
        for row, (gc, sums) in zip(batch, per_line):
            a = acc[row["variant"]]
            inv = 1.0 / gc
            for i, s in enumerate(sums):
                a[i] += s * inv
        for v in VARIANTS:
            acc[v] = [x / M_CONTEXTS for x in acc[v]]
        v_k = [w - wo for w, wo in zip(acc["with_k"], acc["without"])]
        v_d2 = [w - wo for w, wo in zip(acc["with_d2"], acc["without"])]
        mdiff[c] = {"K": v_k, "d2": v_d2}
        # [R10-3] content hash bound at write time (exact f64 bytes,
        # domain-bound to slot+layers+D); re-derived on every resume
        content_shas[c] = ckpt_content_sha256(c, layers, v_k, v_d2)
        tmp = ck.with_suffix(".tmp")
        tmp.write_text(json.dumps(
            {"binding": binding,                 # carrier-HOLD fix 1
             "engine_echo": echo_line,           # carrier-HOLD fix 5
             "content_sha256": content_shas[c],  # [R10-3]
             "construction_seed": CONSTRUCTION_SEED, "layers": layers,
             "D": D, "n_passes": len(batch), "v_k": v_k, "v_d2": v_d2}),
            "utf-8")
        tmp.rename(ck)                     # atomic per-concept checkpoint
        print("concept %03d/%d: %d passes, D=%d" % (c + 1, NC, len(batch),
                                                    D), flush=True)
    if D is None:
        fail("no dump output")

    # ---- assemble the arm tables (float64; f32 only at kaec_write) --------
    def vec(table, c, li):
        base = li * D
        return table[c][base:base + D]

    K = {c: mdiff[c]["K"] for c in range(NC)}
    knorm = {}
    for c in range(NC):
        for li in range(nl):
            v = vec(K, c, li)
            n = math.sqrt(sum(x * x for x in v))
            if n == 0.0:
                fail("||v^K|| == 0 at (slot=%d, layer=%d) — the reference-"
                     "norm rule (§R2) is undefined; construction anomaly"
                     % (c, layers[li]))
            # [R10-2] non-degeneracy at assembly: a degenerate mean
            # difference (near-constant/min-variance) is a construction
            # anomaly and is never written
            reason = drv.vector_degeneracy(v)
            if reason:
                fail("v^K DEGENERATE at (slot=%d, layer=%d): %s "
                     "(round-10 gap 2)" % (c, layers[li], reason))
            knorm[(c, li)] = n

    norms = {"reference_rule": "reference at each (c,l) = ||v^K_{c,l}||; "
                               "every non-K carrier rescaled per (c,l) to "
                               "the reference; g applies AFTER rescaling "
                               "[DES §R2]",
             "construction_seed": CONSTRUCTION_SEED,
             # exact float64 reference norms (c-major, then layer index) —
             # carrier-HOLD fix 6: lets `verify` re-derive the ENTIRE d0
             # table byte-exactly (f32(knorm_f64 * direction_f64)) on the
             # pinned toolchain, since the f32-cast K table alone cannot
             # reproduce the f64 scale factor construction used
             "k_reference_norm_f64_hex": [
                 knorm[(c, li)].hex()
                 for c in range(NC) for li in range(nl)],
             "layers": layers, "D": D, "nc": NC, "arms": {}}

    def flat(table):
        out = []
        for c in range(NC):
            out.extend(table[c])
        return out

    def record_norms(arm, raw_fn, rescaled_table):
        a = {"raw": [], "rescaled": []}
        for c in range(NC):
            for li in range(nl):
                a["raw"].append(round(raw_fn(c, li), 9))
                v = rescaled_table[c][li * D:(li + 1) * D]
                a["rescaled"].append(
                    round(math.sqrt(sum(x * x for x in v)), 9))
        norms["arms"][arm] = a

    # K (the reference itself)
    drv.kaec_write(outdir / TABLES["K"], NC, layers, D, flat(K))
    record_norms("K", lambda c, li: knorm[(c, li)], K)

    # d0 — registered kot-f1k-d0/1 (unit direction * K reference norm)
    d0 = {}
    for c in range(NC):
        row = []
        for li in range(nl):
            d = d0_direction(c, layers[li], D)
            s = knorm[(c, li)]
            row.extend(x * s for x in d)
        d0[c] = row
    drv.kaec_write(outdir / TABLES["d0"], NC, layers, D, flat(d0))
    record_norms("d0", lambda c, li: 1.0, d0)   # raw ||direction|| == 1

    # d2 — same construction, dictionary content, rescaled to the K ref
    d2raw_norm = {}
    d2 = {}
    for c in range(NC):
        row = []
        for li in range(nl):
            v = mdiff[c]["d2"][li * D:(li + 1) * D]
            n = math.sqrt(sum(x * x for x in v))
            if n == 0.0:
                fail("||v^d2|| == 0 at (slot=%d, layer=%d)" % (c, layers[li]))
            reason = drv.vector_degeneracy(v)      # [R10-2]
            if reason:
                fail("v^d2 DEGENERATE at (slot=%d, layer=%d): %s "
                     "(round-10 gap 2)" % (c, layers[li], reason))
            d2raw_norm[(c, li)] = n
            s = knorm[(c, li)] / n
            row.extend(x * s for x in v)
        d2[c] = row
    drv.kaec_write(outdir / TABLES["d2"], NC, layers, D, flat(d2))
    record_norms("d2", lambda c, li: d2raw_norm[(c, li)], d2)

    # derangements — identical K table, labels deranged, layerwise
    # norm-matched to ||v^K_{c,l}|| [DES §R2 d1-drng; REG design.seeds]
    def deranged(perm):
        t = {}
        for c in range(NC):
            row = []
            for li in range(nl):
                src = vec(K, perm[c], li)
                s = knorm[(c, li)] / knorm[(perm[c], li)]
                row.extend(x * s for x in src)
            t[c] = row
        return t

    arm_cfg = {"K": {"path": str(outdir / TABLES["K"])},
               "d0": {"path": str(outdir / TABLES["d0"]),
                      "meta": {"seed": D0_SEED, "algorithm": D0_DOMAIN}},
               "d2": {"path": str(outdir / TABLES["d2"])},
               "d1-drng": {}}
    for seed in DRNG_SEEDS:
        perm = ders["derangements"][str(seed)]
        t = deranged(perm)
        p = outdir / ("d1-drng-%d.kaec" % seed)
        drv.kaec_write(p, NC, layers, D, flat(t))
        record_norms("d1-drng-%d" % seed,
                     lambda c, li, s_=seed, p_=perm:
                     knorm[(p_[c], li)], t)
        arm_cfg["d1-drng"][str(seed)] = {
            "path": str(p),
            "meta": {"seed": seed, "derangement": perm,
                     "layerwise_norm_matched": True}}
    pperm = ders["derangements"][str(KDRNG_SEED)]
    kd = deranged(pperm)
    drv.kaec_write(outdir / TABLES["kdrng"], NC, layers, D, flat(kd))
    record_norms("k-drng-%d" % KDRNG_SEED,
                 lambda c, li: knorm[(pperm[c], li)], kd)

    panel_cfg = {
        "members": {
            "panel-0": {"path": str(outdir / TABLES["K"])},
            "panel-1": {"path": str(outdir / TABLES["kdrng"]),
                        "meta": {"seed": KDRNG_SEED, "derangement": pperm}},
            "panel-2": {"path": str(outdir / TABLES["d2"])},
            "panel-3": {"path": str(outdir / TABLES["d0"]),
                        "meta": {"seed": D0_SEED}}},
        "families": {"fam-a": ["panel-0", "panel-1"], "fam-b": ["panel-2"],
                     "fam-c": ["panel-3"]},
        "k_true_member": "panel-0", "placebo_family": "fam-c"}

    with open(outdir / "norms.json", "w", encoding="utf-8") as f:
        json.dump(norms, f, indent=1, sort_keys=True)
        f.write("\n")
    report = {
        "binding": binding,                       # carrier-HOLD fix 1
        "mode": binding["mode"],
        "engine_provenance_echo": {               # carrier-HOLD fix 5
            "expected_seed": CONSTRUCTION_SEED,
            "verified_batches": echo_verified,
            "sample": echo_sample},
        "registered_splice_layers_enforced": binding["mode"] == "real",
        "construction_seed": CONSTRUCTION_SEED,
        "d0_algorithm": D0_DOMAIN,
        "d0_reproducibility_scope": (
            "byte-exact on the pinned toolchain (libm transcendentals; "
            "carrier-HOLD fix 6) — verify re-derives the FULL table"),
        "seeds": {"d0_table": D0_SEED, "pilot_panel": KDRNG_SEED,
                  "main": DRNG_SEEDS},
        "layers": layers, "D": D, "nc": NC,
        "forward_passes": n_passes,
        "forward_passes_expected": NC * M_CONTEXTS * len(VARIANTS),
        # [R10-3] the per-concept checkpoint CONTENT witness: sha256 over
        # the exact f64 v_k/v_d2 bytes, domain-bound (slot, layers, D) —
        # construct re-derives it on every cached resume; verify
        # re-derives it from the workdir checkpoints when present; the
        # driver requires its presence for any REAL ingest
        "checkpoint_content_sha256": [content_shas[c] for c in range(NC)],
        # [R10-2] non-degeneracy disclosure (floors registered in
        # f1k_driver.py [R10]; enforced at assembly, on every cached
        # resume, at verify over every written table, and at driver ingest)
        "nondegeneracy": {
            "min_std_over_rms": drv.NONDEGEN_MIN_STD_OVER_RMS,
            "min_nonzero_frac": drv.NONDEGEN_MIN_NONZERO_FRAC},
        "manifest_sha256": sha256_file(man_path),
        "tables": {p.name: {"sha256": sha256_file(p),
                            "bytes": p.stat().st_size}
                   for p in sorted(outdir.glob("*.kaec"))},
        "carriers_config_fragment": arm_cfg,
        "pilot_panel_config_fragment": panel_cfg,
    }
    with open(outdir / "construction-report.json", "w",
              encoding="utf-8") as f:
        json.dump(report, f, indent=1, sort_keys=True)
        f.write("\n")
    print("construction complete: %d forward passes (mode=%s); tables + "
          "norms + report -> %s" % (n_passes, binding["mode"], outdir))
    return cmd_verify(argparse.Namespace(out=str(outdir),
                                         layers=args.layers,
                                         expect_mode=args.mode,
                                         workdir=str(work)))


# ---------------------------------------------------------------------------
# verify — every consumer bind, re-checked from the written bytes
# ---------------------------------------------------------------------------
def cmd_verify(args):
    outdir = Path(args.out)
    checks = []

    def ck(name, ok, note=""):
        checks.append((name, ok))
        print("  [%s] %s%s" % ("PASS" if ok else "FAIL", name,
                               (" — " + note) if note else ""))
        if not ok:
            fail("verify failed: %s" % name)

    # ---- carrier RE-REVIEW item 2 (2026-07-16): verify NEVER runs
    # mode-blind. --expect-mode is REQUIRED at the CLI (argparse) and
    # re-asserted here fail-closed for programmatic callers, so a mock
    # table set can never PASS a verify whose caller needed real.
    expect_mode = getattr(args, "expect_mode", None)
    ck("--expect-mode supplied (verify is never mode-blind)",
       expect_mode in MODES, "re-review item 2")
    if expect_mode == "mock":
        # [R10-1] a mock-scoped verify can never bless the REGISTERED
        # production corpus location — the ONLY verify path that can is
        # the real one (mode=real + A(iv) 3..78 + D=6144 + denylist).
        ck("mock-scoped verify is NOT aimed at the production corpus dir",
           not under_real_corpus(outdir),
           "[R10-1] %s is real-verify-only" % REAL_CORPUS_DIR)

    K = drv.kaec_read(str(outdir / TABLES["K"]))
    nc, nl, D, layers = K["nc"], K["nl"], K["D"], K["layers"]
    ck("kaec geometry nc=%d nl=%d D=%d" % (nc, nl, D),
       nc == NC and D == D_EXPECTED and nl >= 1,
       "frozen kaec_format: nc=96, D=6144")
    if args.layers:
        want = [int(x) for x in args.layers.split(",")]
        ck("layer ids == caller's --layers", layers == want)

    # ---- provenance binding (carrier-HOLD fixes 1/2/3) ---------------------
    rep_path = outdir / "construction-report.json"
    ck("construction-report.json present", rep_path.exists())
    rep = json.loads(rep_path.read_text("utf-8"))
    binding = rep.get("binding")
    ck("report carries a provenance binding with all fields",
       isinstance(binding, dict)
       and all(k in binding for k in BINDING_FIELDS),
       "carrier-HOLD fix 1")
    ck("binding mode is mock|real", binding["mode"] in MODES)
    ck("binding mode == --expect-mode %s" % expect_mode,
       binding["mode"] == expect_mode,
       "a mock artifact set can never satisfy --expect-mode real; a "
       "real-claiming report never passes a mock-scoped verify")
    ck("report mode == binding mode",
       rep.get("mode") == binding["mode"], "[R10-1] no split-mode reports")
    ck("binding layers == written table layers",
       binding["layers"] == layers)
    if binding["mode"] == "real" or expect_mode == "real":
        # ---- [R10-1] a REAL report can NEVER be satisfied by a mock
        # table/toolchain: binding provenance shas are denylisted against
        # the repo mock stack's CURRENT digests — a mock construction
        # relabeled mode=real (mock geometry can legally rehearse 3..78 /
        # D=6144, so geometry alone cannot tell them apart) fails here.
        mstack = drv.mock_stack_shas()
        hits = ["%s == %s" % (f, mstack[binding[f]])
                for f in ("tokenizer_sha256", "engine_weights_sha256",
                          "dump_patch_sha256") if binding.get(f) in mstack]
        ck("REAL binding provenance shas are NOT repo mock-stack digests",
           not hits,
           ("[R10-1] relabeled mock construction refused: %s"
            % "; ".join(hits)) if hits else
           "[R10-1] mock-stack denylist (a real report can never be "
           "satisfied by a mock table)")
        # UNCONDITIONAL for anything claiming (or expected to be) real:
        # the registered A(iv) union, no other list (re-review item 2)
        ck("REAL construction layers == the REGISTERED A(iv) splice union "
           "(76 MoE layers 3..78 [ASM-2342])",
           layers == REGISTERED_SPLICE_LAYERS, "carrier-HOLD fix 2")
    else:
        print("  [note] mode=mock artifact set: mock geometry permitted; "
              "UNUSABLE in a real construction (binding-enforced) and "
              "NEVER a substitute for the real verify path [R10-1]")
    man_path = GEN / "construction-manifest.jsonl"
    ck("binding manifest sha == committed construction manifest",
       man_path.exists()
       and binding["manifest_sha256"] == sha256_file(man_path))
    check_manifest_against_spec(man_path)     # fresh (A)-spec re-derivation
    ck("construction manifest == fresh (A)-spec re-derivation "
       "(byte-for-byte)", True, "carrier-HOLD fix 3")
    for sha_field in ("tokenizer_sha256", "engine_weights_sha256",
                      "dump_patch_sha256"):
        ck("binding %s is 64-hex" % sha_field,
           bool(HEX64_RE.fullmatch(str(binding[sha_field]))))
    echo = rep.get("engine_provenance_echo") or {}
    ck("engine provenance echo captured + verified for every batch "
       "(seed %d)" % CONSTRUCTION_SEED,
       echo.get("expected_seed") == CONSTRUCTION_SEED
       and echo.get("verified_batches") == NC
       and bool(echo.get("sample")), "carrier-HOLD fix 5")
    tables_rep = rep.get("tables") or {}
    for p in sorted(outdir.glob("*.kaec")):
        ent = tables_rep.get(p.name) or {}
        ck("%s bytes match the construction report's pinned sha" % p.name,
           ent.get("sha256") == sha256_file(p)
           and ent.get("bytes") == p.stat().st_size)
    # the analysis's sidecar.carriers arithmetic [ANA round-3b item 5]
    params_added = nc * nl * D
    want_bytes = 16 + 4 * nl + 4 * params_added
    names = [TABLES["K"], TABLES["d0"], TABLES["d2"], TABLES["kdrng"]] + \
            ["d1-drng-%d.kaec" % s for s in DRNG_SEEDS]
    for name in names:
        p = outdir / name
        m = drv.kaec_read(str(p))
        ck("%s geometry identical to K" % name,
           (m["nc"], m["nl"], m["D"], m["layers"]) == (nc, nl, D, layers))
        ck("%s table_bytes == exact KAEC fp32 size %d" % (name, want_bytes),
           p.stat().st_size == want_bytes,
           "params_added=%d == C*layers*D" % params_added)
        # [R10-2] FULL-coverage non-degeneracy: every (c,l) cell of every
        # table (all-zero/near-constant/min-variance bodies fail closed —
        # an all-zero set previously satisfied EVERY check below, since
        # 0-norm tables norm-match and reconstruct trivially)
        check_table_nondegeneracy(name, m, layers)
        ck("%s non-degenerate at every (c,l) cell" % name, True,
           "[R10-2] round-10 gap 2")
    ck("params_added %% (C_REGISTERED*layers) == 0 with integer D",
       params_added % (NC * nl) == 0 and params_added // (NC * nl) == D)

    # ---- [R10-3] checkpoint-content witness --------------------------------
    cks_list = rep.get("checkpoint_content_sha256")
    ck("report carries the %d-entry checkpoint_content_sha256 witness"
       % NC,
       isinstance(cks_list, list) and len(cks_list) == NC
       and all(isinstance(x, str) and HEX64_RE.fullmatch(x)
               for x in cks_list), "[R10-3] round-10 gap 3")
    wdir = Path(args.workdir) if getattr(args, "workdir", None) \
        else (outdir / "work")
    cpaths = [wdir / ("concept-%03d.json" % c) for c in range(NC)]
    if all(cp.exists() for cp in cpaths):
        ok = True
        bad = None
        for c, cp in enumerate(cpaths):
            cached = json.loads(cp.read_text("utf-8"))
            got = ckpt_content_sha256(c, layers,
                                      cached.get("v_k") or [],
                                      cached.get("v_d2") or [])
            if not (cached.get("content_sha256") == cks_list[c]
                    == got):
                ok = False
                bad = c
                break
        ck("workdir checkpoints RE-DERIVE the report's content witness "
           "(%d concepts, exact f64 bytes)" % NC, ok,
           "[R10-3]" if ok else "first mismatch at slot %s" % bad)
    else:
        print("  [note] workdir %s does not carry all %d construction "
              "checkpoints — checkpoint-content witness verified for "
              "SHAPE here; construct re-derives it fail-closed on every "
              "cached resume (pass --workdir to re-derive now) [R10-3]"
              % (wdir, NC))

    def vecs(m, c, li):
        base = (c * nl + li) * D
        return m["vals"][base:base + D]

    knorm = {(c, li): math.sqrt(sum(x * x for x in vecs(K, c, li)))
             for c in range(nc) for li in range(nl)}
    rtol = drv.NORM_MATCH_RTOL
    for name in names[1:]:
        m = drv.kaec_read(str(outdir / name))
        worst = 0.0
        for c in range(nc):
            for li in range(nl):
                nm = math.sqrt(sum(x * x for x in vecs(m, c, li)))
                nk = knorm[(c, li)]
                worst = max(worst, abs(nm - nk) / max(nk, 1e-9))
        ck("%s norm-matched per (c,l) within rtol %g" % (name, rtol),
           worst <= rtol, "worst rel dev %.3g" % worst)
    ders = json.loads((GEN / "derangements.json").read_text("utf-8"))
    for seed, name in [(KDRNG_SEED, TABLES["kdrng"])] + \
            [(s, "d1-drng-%d.kaec" % s) for s in DRNG_SEEDS]:
        perm = ders["derangements"][str(seed)]
        m = drv.kaec_read(str(outdir / name))
        ok = True
        for c in range(nc):
            for li in range(nl):
                src = vecs(K, perm[c], li)
                scale = knorm[(c, li)] / max(knorm[(perm[c], li)], 1e-12)
                got = vecs(m, c, li)
                tol = rtol * max(knorm[(c, li)], 1e-9)
                if any(abs(g - x * scale) > tol for g, x in zip(got, src)):
                    ok = False
                    break
            if not ok:
                break
        ck("%s reconstructs as the seed-%d derangement of K "
           "(validate_panel identity)" % (name, seed), ok)
    # ---- d0 FULL byte-for-byte re-derivation (carrier-HOLD fix 6) ---------
    # Every (c, l, dim) cell of the written d0 table must equal, EXACTLY at
    # f32, f32(knorm_f64 * direction_f64) re-derived from the registered
    # kot-f1k-d0/1 text. Byte-exactness is claimed ON THE PINNED TOOLCHAIN
    # (libm transcendentals — the registered scope; the superseded 6-spot
    # rtol check and the 'platform-independent' over-claim are WITHDRAWN).
    nj = json.loads((outdir / "norms.json").read_text("utf-8"))
    kf64_hex = nj.get("k_reference_norm_f64_hex")
    ck("norms.json carries the exact f64 reference norms (%d cells)"
       % (nc * nl),
       isinstance(kf64_hex, list) and len(kf64_hex) == nc * nl,
       "carrier-HOLD fix 6 prerequisite")
    kf64 = [float.fromhex(h) for h in kf64_hex]
    worst = 0.0
    for c in range(nc):
        for li in range(nl):
            s = kf64[c * nl + li]
            dev = abs(s - knorm[(c, li)]) / max(knorm[(c, li)], 1e-9)
            worst = max(worst, dev)
    ck("f64 reference norms coherent with the written f32 K table",
       worst <= 1e-5, "worst rel dev %.3g (f32-cast rounding only)" % worst)

    def f32(x):
        return struct.unpack("<f", struct.pack("<f", x))[0]

    d0 = drv.kaec_read(str(outdir / TABLES["d0"]))
    ok = True
    bad = None
    for c in range(nc):
        for li in range(nl):
            direction = d0_direction(c, layers[li], D)
            s = kf64[c * nl + li]
            got = vecs(d0, c, li)
            for i, w in enumerate(direction):
                if got[i] != f32(s * w):
                    ok = False
                    bad = (c, layers[li], i)
                    break
            if not ok:
                break
        if not ok:
            break
    ck("d0 FULL byte-for-byte re-derivation from kot-f1k-d0/1 (seed %d): "
       "all %d x %d x %d cells exact at f32 (pinned-toolchain scope)"
       % (D0_SEED, nc, nl, D), ok,
       "first mismatch at (slot,layer,dim)=%s" % (bad,) if bad else
       "carrier-HOLD fix 6")
    ck("construction_seed stamp == registered %d" % CONSTRUCTION_SEED,
       rep["construction_seed"] == CONSTRUCTION_SEED
       and binding["construction_seed"] == CONSTRUCTION_SEED)
    ck("forward passes == 96 x 16 x 3 = %d" % (NC * M_CONTEXTS * 3),
       rep["forward_passes"] == NC * M_CONTEXTS * 3)
    ck("norms artifact present (B0 addendum component)",
       (outdir / "norms.json").exists())
    if expect_mode == "mock":
        print("verify: %d/%d checks PASS — MOCK SCOPE ONLY: this verify "
              "can NEVER satisfy a real construction/report; the only "
              "real-run verify path is --expect-mode real (mode=real AND "
              "the A(iv) layers 3..78 AND D=6144 AND the mock-stack "
              "denylist) [R10-1]" % (len(checks), len(checks)))
    else:
        print("verify: %d/%d checks PASS (REAL scope: mode=real, A(iv) "
              "3..78, D=6144, mock-stack denylist, non-degeneracy, "
              "checkpoint-content witness)" % (len(checks), len(checks)))
    return 0


# ---------------------------------------------------------------------------
# selftest — fail-closed probes for the carrier-HOLD fixes  [$0]
# ---------------------------------------------------------------------------
def cmd_selftest(_args):
    import tempfile
    n_pass = 0

    def probe(name, ok, note=""):
        nonlocal n_pass
        print("  [%s] selftest: %s%s" % ("PASS" if ok else "FAIL", name,
                                         (" — " + note) if note else ""))
        if not ok:
            fail("selftest probe failed: %s" % name)
        n_pass += 1

    man_path = GEN / "construction-manifest.jsonl"
    derived = build_manifest_rows()

    with tempfile.TemporaryDirectory(prefix="f1k-carriergen-selftest-") \
            as td:
        tmp = Path(td)
        # artifact stand-ins whose BYTES hash to the asserted pins — real
        # mode now DERIVES each sha from the artifact and compares
        # (re-review item 8), so the probes carry both.
        arts = {}
        for k, payload in (("tok", b"selftest-tok"),
                           ("eng", b"selftest-eng"),
                           ("patch", b"selftest-patch")):
            p = tmp / ("artifact-%s.bin" % k)
            p.write_bytes(payload)
            arts[k] = p
        dummy_sha = {
            "tok": hashlib.sha256(b"selftest-tok").hexdigest(),
            "eng": hashlib.sha256(b"selftest-eng").hexdigest(),
            "patch": hashlib.sha256(b"selftest-patch").hexdigest()}
        real_binding = {
            "mode": "real",
            "manifest_sha256": sha256_file(man_path),
            "tokenizer_sha256": dummy_sha["tok"],
            "engine_weights_sha256": dummy_sha["eng"],
            "dump_patch_sha256": dummy_sha["patch"],
            "construction_seed": CONSTRUCTION_SEED,
            "layers": list(REGISTERED_SPLICE_LAYERS)}

        # ---- probe 1 (carrier-HOLD fix 1, THE critical one): a checkpoint
        # whose binding is IDENTICAL to the current real run in every field
        # EXCEPT mode=mock must be REFUSED by a real construction, end to
        # end (subprocess), before any engine invocation.
        work = tmp / "seeded-work"
        work.mkdir()
        nlr = len(REGISTERED_SPLICE_LAYERS)
        mock_ck = dict(real_binding, mode="mock")
        (work / "concept-000.json").write_text(json.dumps(
            {"binding": mock_ck, "engine_echo": "[KAE-DUMP] armed: mock",
             "construction_seed": CONSTRUCTION_SEED,
             "layers": list(REGISTERED_SPLICE_LAYERS), "D": D_EXPECTED,
             "n_passes": M_CONTEXTS * len(VARIANTS),
             "v_k": [0.0] * (nlr * 4), "v_d2": [0.0] * (nlr * 4)}),
            "utf-8")
        argv = [sys.executable, str(Path(__file__).resolve()), "construct",
                "--mode", "real",
                "--engine-cmd", json.dumps(
                    [sys.executable, str(HERE / "mock_colibri_dump.py")]),
                "--tokenizer-cmd", json.dumps(
                    [sys.executable, str(HERE / "mock_tokenizer.py")]),
                "--layers", ",".join(map(str, REGISTERED_SPLICE_LAYERS)),
                "--tokenizer-sha", dummy_sha["tok"],
                "--engine-weights-sha", dummy_sha["eng"],
                "--dump-patch-sha", dummy_sha["patch"],
                "--tokenizer-artifact", str(arts["tok"]),
                "--engine-weights-artifact", str(arts["eng"]),
                "--dump-patch-artifact", str(arts["patch"]),
                "--out", str(tmp / "out1"), "--workdir", str(work)]
        proc = subprocess.run(argv, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        err = proc.stderr.decode("utf-8", "replace")
        probe("MOCK checkpoint REJECTED in REAL construction (e2e, "
              "fail-closed)",
              proc.returncode == 2 and "UNUSABLE in a REAL construction"
              in err and not list((tmp / "out1").glob("*.kaec")),
              "exit %d; no table written" % proc.returncode)

        # ---- probe 2 (carrier-HOLD fix 2): a non-A(iv) layer list in real
        # mode fails closed.
        argv2 = list(argv)
        argv2[argv2.index("--layers") + 1] = "1,2,3"
        argv2[argv2.index("--out") + 1] = str(tmp / "out2")
        argv2[argv2.index("--workdir") + 1] = str(tmp / "work2")
        proc = subprocess.run(argv2, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        err = proc.stderr.decode("utf-8", "replace")
        probe("non-A(iv) layer list REJECTED in REAL mode",
              proc.returncode == 2 and "A(iv)" in err,
              "exit %d" % proc.returncode)

        # ---- probe 3 (carrier-HOLD fix 3): a content-tampered manifest
        # with UNCHANGED row count and seed is rejected; the committed
        # manifest passes (positive control).
        check_manifest_against_spec(man_path, derived)   # must not raise
        probe("committed manifest == fresh (A)-spec derivation "
              "(positive control)", True)
        tampered = tmp / "tampered-manifest.jsonl"
        lines = man_path.read_text("utf-8").splitlines()
        row0 = json.loads(lines[0])
        row0["text"] = row0["text"] + " "     # same count, same seed
        lines[0] = json.dumps(row0, sort_keys=True)
        tampered.write_text("\n".join(lines) + "\n", "utf-8")
        try:
            check_manifest_against_spec(tampered, derived)
            ok = False
        except SystemExit as e:
            ok = e.code == 2
        probe("content-tampered manifest (same count+seed) REJECTED", ok)

        # ---- probe 4 (carrier-HOLD fix 5): wrong / absent engine seed
        # echo fails closed.
        bad_echo = tmp / "bad_echo_engine.py"
        bad_echo.write_text(
            "import os, runpy, sys\n"
            "os.environ['KAE_SEED'] = '999'\n"
            "sys.argv = [sys.argv[0]]\n"
            "runpy.run_path(%r, run_name='__main__')\n"
            % str(HERE / "mock_colibri_dump.py"), "utf-8")
        one_row = [derived[0]]
        toks = tokenize_all(
            [sys.executable, str(HERE / "mock_tokenizer.py")], one_row)
        try:
            run_dump([sys.executable, str(bad_echo)], [3], one_row, toks,
                     tmp / "dump4", "probe4")
            ok = False
        except SystemExit as e:
            ok = e.code == 2
        probe("engine echo seed MISMATCH (999 != %d) REJECTED"
              % CONSTRUCTION_SEED, ok)
        no_echo = tmp / "no_echo_engine.py"
        no_echo.write_text("import sys; sys.exit(0)\n", "utf-8")
        try:
            run_dump([sys.executable, str(no_echo)], [3], one_row, toks,
                     tmp / "dump4b", "probe4b")
            ok = False
        except SystemExit as e:
            ok = e.code == 2
        probe("engine echo ABSENT rejected", ok)

        # ---- probe 5 (re-review item 8): a REAL construct whose asserted
        # sha does NOT equal the artifact's derived digest is rejected —
        # 64-hex syntax alone is never accepted.
        wrong_art = tmp / "artifact-eng-wrong.bin"
        wrong_art.write_bytes(b"NOT-the-pinned-engine")
        argv5 = list(argv)
        argv5[argv5.index("--engine-weights-artifact") + 1] = str(wrong_art)
        argv5[argv5.index("--out") + 1] = str(tmp / "out5")
        argv5[argv5.index("--workdir") + 1] = str(tmp / "work5")
        proc = subprocess.run(argv5, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        err = proc.stderr.decode("utf-8", "replace")
        probe("REAL provenance sha asserted != DERIVED artifact digest "
              "REJECTED (re-review item 8)",
              proc.returncode == 2 and "does not match sha256" in err,
              "exit %d" % proc.returncode)

        # ---- probes 6/6b/7 (re-review items 5 + 8): cached-resume
        # checkpoints with a MATCHING binding but (6) a wrong stored echo
        # seed, (6b) no stored echo at all, or (7) tampered content
        # (D != 6144) are each rejected on resume, before any engine
        # invocation. The binding is derived exactly as a mock run would
        # derive it, so ONLY the probed field differs.
        mock_tok_sha = sha256_file(HERE / "mock_tokenizer.py")
        mock_eng_sha = sha256_file(HERE / "mock_colibri_dump.py")
        probe_layers = [1, 2, 3]
        mock_binding = {
            "mode": "mock",
            "manifest_sha256": sha256_file(man_path),
            "tokenizer_sha256": mock_tok_sha,
            "engine_weights_sha256": mock_eng_sha,
            "dump_patch_sha256": mock_eng_sha,
            "construction_seed": CONSTRUCTION_SEED,
            "layers": probe_layers}
        nlp = len(probe_layers)

        def cached_probe(tag, echo, D_val, content="omit", vec_val=0.0):
            wdir = tmp / ("work-%s" % tag)
            wdir.mkdir()
            v_k = [vec_val] * (nlp * D_EXPECTED)
            v_d2 = [vec_val] * (nlp * D_EXPECTED)
            ckd = {"binding": mock_binding,
                   "construction_seed": CONSTRUCTION_SEED,
                   "layers": probe_layers, "D": D_val,
                   "n_passes": M_CONTEXTS * len(VARIANTS),
                   "v_k": v_k, "v_d2": v_d2}
            if content == "valid":       # hash over the STORED vectors
                ckd["content_sha256"] = ckpt_content_sha256(
                    0, probe_layers, v_k, v_d2)
            elif content == "stale":     # hash over DIFFERENT vectors —
                # the round-10 gap-3 exploit: vectors replaced after the
                # checkpoint was written
                ckd["content_sha256"] = ckpt_content_sha256(
                    0, probe_layers, [vec_val + 1.0] * (nlp * D_EXPECTED),
                    v_d2)
            if echo is not None:
                ckd["engine_echo"] = echo
            (wdir / "concept-000.json").write_text(json.dumps(ckd),
                                                   "utf-8")
            argvp = [sys.executable, str(Path(__file__).resolve()),
                     "construct", "--mode", "mock",
                     "--engine-cmd", json.dumps(
                         [sys.executable,
                          str(HERE / "mock_colibri_dump.py")]),
                     "--tokenizer-cmd", json.dumps(
                         [sys.executable, str(HERE / "mock_tokenizer.py")]),
                     "--layers", ",".join(map(str, probe_layers)),
                     "--out", str(tmp / ("out-%s" % tag)),
                     "--workdir", str(wdir)]
            p = subprocess.run(argvp, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
            return p.returncode, p.stderr.decode("utf-8", "replace")

        rc, err = cached_probe(
            "echo999",
            "[KAE-DUMP] armed: %d layers, D=%d, seed=999"
            % (nlp, D_EXPECTED), D_EXPECTED)
        probe("cached-resume checkpoint with MATCHING binding but stored "
              "echo seed=999 REJECTED (re-review item 5)",
              rc == 2 and "re-review item 5" in err and "999" in err,
              "exit %d" % rc)
        rc, err = cached_probe("noecho", None, D_EXPECTED)
        probe("cached-resume checkpoint with NO stored echo REJECTED "
              "(re-review item 5)",
              rc == 2 and "ABSENT/unparseable" in err, "exit %d" % rc)
        rc, err = cached_probe(
            "wrongD",
            "[KAE-DUMP] armed: %d layers, D=%d, seed=%d"
            % (nlp, D_EXPECTED, CONSTRUCTION_SEED), 8)
        probe("cached-resume checkpoint with tampered content (D=8) "
              "REJECTED (re-review item 8)",
              rc == 2 and "cached-content integrity" in err,
              "exit %d" % rc)

        # ---- probes 9/9b/10 (ROUND-10 gaps 3 + 2): checkpoint vector
        # CONTENTS are now authenticated — (9) a checkpoint whose vectors
        # were REPLACED with arbitrary finite values (stored content hash
        # no longer re-derives; the prior code accepted ANY finite values)
        # is rejected; (9b) a checkpoint WITHOUT a content hash is
        # rejected; (10) an ALL-ZERO body with a perfectly VALID content
        # hash is rejected by non-degeneracy.
        good_echo = ("[KAE-DUMP] armed: %d layers, D=%d, seed=%d"
                     % (nlp, D_EXPECTED, CONSTRUCTION_SEED))
        rc, err = cached_probe("tampered-vectors", good_echo, D_EXPECTED,
                               content="stale", vec_val=0.5)
        probe("cached-resume checkpoint with REPLACED vector contents "
              "(finite, shape-valid; stale content hash) REJECTED "
              "(round-10 gap 3)",
              rc == 2 and "round-10 gap 3" in err
              and "tampered with/replaced" in err, "exit %d" % rc)
        rc, err = cached_probe("no-content-hash", good_echo, D_EXPECTED,
                               content="omit", vec_val=0.5)
        probe("cached-resume checkpoint WITHOUT content_sha256 REJECTED "
              "(round-10 gap 3)",
              rc == 2 and "NO content_sha256" in err, "exit %d" % rc)
        rc, err = cached_probe("all-zero-valid-hash", good_echo,
                               D_EXPECTED, content="valid", vec_val=0.0)
        probe("cached-resume checkpoint with ALL-ZERO vectors and a VALID "
              "content hash REJECTED by non-degeneracy (round-10 gap 2)",
              rc == 2 and "round-10 gap 2" in err and "all-zero" in err,
              "exit %d" % rc)

        # ---- probe 8 (re-review item 2): verify REFUSES to run
        # mode-blind — --expect-mode is required at the CLI.
        p = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "verify",
             "--out", str(tmp / "nonexistent")],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        err = p.stderr.decode("utf-8", "replace")
        probe("verify WITHOUT --expect-mode REFUSED (mode-blind verify "
              "banned, re-review item 2)",
              p.returncode != 0 and "--expect-mode" in err,
              "exit %d" % p.returncode)

        # ---- probes 11-14 (ROUND-10 gap 1 + gap 2 on the verify path) ---
        import contextlib
        import io

        def run_verify_expect_fail(ns):
            """In-process cmd_verify, capturing the fail-closed message."""
            buf = io.StringIO()
            try:
                with contextlib.redirect_stderr(buf), \
                        contextlib.redirect_stdout(io.StringIO()):
                    cmd_verify(ns)
                return None, buf.getvalue()
            except SystemExit as e:
                return e.code, buf.getvalue()

        def vns(out, mode):
            return argparse.Namespace(out=str(out), layers=None,
                                      expect_mode=mode, workdir=None)

        # probe 11: a MOCK construction RELABELED mode=real (binding
        # provenance shas == the repo mock stack's own digests) must be
        # REJECTED by the real verify path's mock-stack denylist — a real
        # report can never be satisfied by a mock table.
        relab = tmp / "relabel-real"
        relab.mkdir()
        hdr3 = b"KAEC" + struct.pack("<iii", NC, nlp, D_EXPECTED) + \
            struct.pack("<%di" % nlp, *probe_layers)
        size3 = 16 + 4 * nlp + 4 * NC * nlp * D_EXPECTED
        with open(relab / TABLES["K"], "wb") as f:
            f.write(hdr3)
            f.truncate(size3)
        (relab / "construction-report.json").write_text(json.dumps(
            {"mode": "real",
             "binding": dict(mock_binding, mode="real")}), "utf-8")
        code, err = run_verify_expect_fail(vns(relab, "real"))
        probe("MOCK construction RELABELED mode=real REJECTED by the "
              "real verify path (mock-stack sha denylist; round-10 "
              "gap 1)",
              code == 2 and "mock-stack" in err, "exit %s" % code)

        # probe 12: the SAME real-claiming artifact set under a
        # mock-scoped verify is equally REFUSED — mock-under-mock verify
        # can never bless anything real-claiming.
        code, err = run_verify_expect_fail(vns(relab, "mock"))
        probe("real-claiming report under verify --expect-mode mock "
              "REFUSED (mock verify never satisfies a real report; "
              "round-10 gap 1)",
              code == 2 and "--expect-mode mock" in err,
              "exit %s" % code)

        # probe 13: mock artifacts can never OCCUPY (construct) or be
        # BLESSED IN (verify) the registered production corpus location.
        global REAL_CORPUS_DIR
        saved_prod = REAL_CORPUS_DIR
        fake_prod = tmp / "fake-production-corpus"
        (fake_prod / "sub").mkdir(parents=True)
        try:
            REAL_CORPUS_DIR = fake_prod
            buf = io.StringIO()
            code = None
            try:
                with contextlib.redirect_stderr(buf), \
                        contextlib.redirect_stdout(io.StringIO()):
                    cmd_construct(argparse.Namespace(
                        mode="mock", layers="1,2,3",
                        engine_cmd=json.dumps(
                            [sys.executable,
                             str(HERE / "mock_colibri_dump.py")]),
                        tokenizer_cmd=json.dumps(
                            [sys.executable,
                             str(HERE / "mock_tokenizer.py")]),
                        tokenizer_sha=None, engine_weights_sha=None,
                        dump_patch_sha=None, tokenizer_artifact=None,
                        engine_weights_artifact=None,
                        dump_patch_artifact=None,
                        out=str(fake_prod / "sub"), workdir=None))
            except SystemExit as e:
                code = e.code
            probe("construct --mode mock into the production corpus dir "
                  "REFUSED (round-10 gap 1)",
                  code == 2 and "production" in buf.getvalue(),
                  "exit %s" % code)
            code, err = run_verify_expect_fail(vns(fake_prod / "sub",
                                                   "mock"))
            probe("verify --expect-mode mock aimed at the production "
                  "corpus dir REFUSED (round-10 gap 1)",
                  code == 2 and "production corpus" in err,
                  "exit %s" % code)
        finally:
            REAL_CORPUS_DIR = saved_prod

        # probe 14: an ALL-ZERO table set with a fully coherent report
        # (pinned shas, echo, manifest, witness list) is REJECTED by
        # verify's full-coverage non-degeneracy — round-10 gap 2: zero
        # tables previously norm-matched, reconstructed and d0-re-derived
        # trivially (0 == 0), so EVERY pre-round-10 check passed.
        az = tmp / "all-zero-mock"
        az.mkdir()
        names7 = [TABLES["K"], TABLES["d0"], TABLES["d2"],
                  TABLES["kdrng"]] + \
                 ["d1-drng-%d.kaec" % s for s in DRNG_SEEDS]
        tbl7 = {}
        sha7 = None
        for nm in names7:
            with open(az / nm, "wb") as f:
                f.write(hdr3)
                f.truncate(size3)
            sha7 = sha7 or sha256_file(az / nm)
            tbl7[nm] = {"sha256": sha7, "bytes": size3}
        (az / "construction-report.json").write_text(json.dumps(
            {"mode": "mock", "binding": mock_binding,
             "construction_seed": CONSTRUCTION_SEED,
             "layers": probe_layers, "D": D_EXPECTED, "nc": NC,
             "engine_provenance_echo": {
                 "expected_seed": CONSTRUCTION_SEED,
                 "verified_batches": NC,
                 "sample": "[KAE-DUMP] armed: %d layers, D=%d, seed=%d"
                           % (nlp, D_EXPECTED, CONSTRUCTION_SEED)},
             "checkpoint_content_sha256": [
                 hashlib.sha256(b"selftest-az-%d" % c).hexdigest()
                 for c in range(NC)],
             "tables": tbl7}), "utf-8")
        code, err = run_verify_expect_fail(vns(az, "mock"))
        probe("ALL-ZERO table set with a coherent report REJECTED by "
              "verify non-degeneracy (round-10 gap 2)",
              code == 2 and "DEGENERATE" in err and "all-zero" in err,
              "exit %s" % code)

    print("SELFTEST: %d/%d probes PASS (carrier-HOLD fixes 1/2/3/5 + "
          "re-review items 2/5/8 + round-10 content gaps 1/2/3)"
          % (n_pass, n_pass))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("manifest", help="(A)-time $0 construction manifest")
    c = sub.add_parser("construct", help="forward passes -> .kaec tables")
    c.add_argument("--engine-cmd", required=True,
                   help='JSON argv, e.g. \'["python3","mock_colibri_dump.py"]\'')
    c.add_argument("--tokenizer-cmd", required=True, help="JSON argv")
    c.add_argument("--mode", required=True, choices=list(MODES),
                   help="mock|real — binds every artifact fail-closed "
                        "(carrier-HOLD fix 1)")
    c.add_argument("--layers", required=True,
                   help="csv splice-layer ids; --mode real REQUIRES the "
                        "registered A(iv) union 3..78 (carrier-HOLD fix 2)")
    c.add_argument("--tokenizer-sha", default=None,
                   help="pinned tokenizer artifact sha256 (REQUIRED real)")
    c.add_argument("--engine-weights-sha", default=None,
                   help="pinned engine+weights sha256 (REQUIRED real)")
    c.add_argument("--dump-patch-sha", default=None,
                   help="kot-f1k-dump/1 bring-up patch sha256 "
                        "(REQUIRED real)")
    c.add_argument("--tokenizer-artifact", default=None,
                   help="path to the pinned tokenizer artifact — its "
                        "sha256 is DERIVED and compared to --tokenizer-sha "
                        "(REQUIRED real; re-review item 8)")
    c.add_argument("--engine-weights-artifact", default=None,
                   help="path to the pinned engine+weights artifact "
                        "(sha DERIVED + compared; REQUIRED real)")
    c.add_argument("--dump-patch-artifact", default=None,
                   help="path to the bring-up kot-f1k-dump/1 patch "
                        "(sha DERIVED + compared; REQUIRED real)")
    c.add_argument("--out", required=True)
    c.add_argument("--workdir", default=None)
    v = sub.add_parser("verify", help="$0 consumer-bind re-verification")
    v.add_argument("--out", required=True)
    v.add_argument("--layers", default=None)
    v.add_argument("--expect-mode", required=True, choices=list(MODES),
                   help="REQUIRED (re-review item 2): verify never runs "
                        "mode-blind; fail closed unless the report "
                        "binding carries this mode. mock is TESTING "
                        "SCOPE ONLY and never blesses the production "
                        "corpus dir [R10-1]")
    v.add_argument("--workdir", default=None,
                   help="construction checkpoint dir (default <out>/work) "
                        "— when the per-concept checkpoints are present, "
                        "the report's checkpoint_content_sha256 witness "
                        "is RE-DERIVED from their exact f64 vector bytes "
                        "[R10-3]")
    sub.add_parser("selftest",
                   help="$0 fail-closed probes (carrier-HOLD fixes)")
    args = ap.parse_args()
    if args.cmd == "manifest":
        return cmd_manifest(args)
    if args.cmd == "construct":
        return cmd_construct(args)
    if args.cmd == "selftest":
        return cmd_selftest(args)
    return cmd_verify(args)


if __name__ == "__main__":
    sys.exit(main())
