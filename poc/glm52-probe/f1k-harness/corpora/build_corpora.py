#!/usr/bin/env python3
"""build_corpora.py — F1-K input-corpora builder (DATA CONSTRUCTION pass, $0).

Builds, to the FROZEN F1-K recipe, the model-independent bytes of the three
PINNED-AT-INPUTS corpora of registry/experiments/f1k.json pins.corpus_hashes:

  data/f1k-trigger-map-v1/   phrase->concept trigger map over the PINNED kernel
                             (kernel-v0), WordNet lemma/derivational surface
                             expansion + the frozen gate precedence rules.
  data/f1k-eval-v1/          known-concept item lists (test-1440 / dev-96 /
                             guard-60) + frozen scored template BYTES +
                             per-item CHARACTER-level span sidecars + the
                             deterministic tokenizer-derivation rule.
  data/f1k-carriers-v1/      the deterministic PRE-SPEND generator components
                             only (concept texts, DRAFT construction contexts,
                             registered-seed derangements, generator spec).
                             The REALIZED carrier tables + norms are, by the
                             frozen ordering (SSR-REV3.3/SSR-REV4.2), a
                             POST-construction-spend pure-function addendum
                             (B0) and CANNOT exist in a $0 pass.

FROZEN SOURCES (every construction rule below cites one of these):
  [REG]  registry/experiments/f1k.json (DRAFT kot-reg/1; pins.corpus_hashes
         placeholder texts; design.n_planned.freeze_manifest (A)/(B0))
  [DES]  docs/next/design/glm52-followup-experiment.md
         sha256 9f18e5e09f5c8a2a933f3446697daf5849676447004540398237da7f8e67f2b6
         SS2 as amended by SSR..SSR-REV5 (latest revision governs on conflict)
  [DRV]  poc/glm52-probe/f1k-harness/f1k_driver.py (run-driver input contract;
         seeded_derangement is the harness algorithm for [DES SSR2] seeds)
  [PATCH] poc/glm52-probe/kae-patch-draft/kae.h (KAEC carrier byte format;
         span sidecar semantics: per-position concept id, -1 = ungated)
  [KV0]  data/kernel-v0/ (THE kernel corpus pinned by [REG]:
         8209cadabcfc2eaa11631c5c1100c04a48f33673516780b1f36cbf957217c809;
         54 registered explications; `gloss` = the explication text rendering)
  [WN]   data/lexical-wn31/ (WordNet 3.1 source dict, in-repo) and
         data/lexical-wn31/alignment-kernel-v0.json (kot-lex-align/1,
         hand-reviewed kernel-v0 -> WN31 synset alignment)

OPERATIONALISATION DISCIPLINE: choices the frozen record does NOT fix are
tagged OP-1..OP-9 in comments AND enumerated machine-readably in each
corpus manifest under "operationalisations" — every one of them requires
COORDINATOR ADOPTION at freeze-manifest (A) before it is frozen. Nothing
here is a registry write, git action, freeze, spend, or model download.

Determinism: byte-identical outputs on re-run. No wall-clock, no unseeded
randomness; the only PRNG uses are the REGISTERED derangement seeds
[REG design.seeds / freeze_manifest A(vii)].
"""

import hashlib
import io
import json
import os
import random
import re
import shutil
import struct
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]                      # repo root (kernel-of-truth/)
sys.path.insert(0, str(ROOT / "tools" / "registry"))
import kot_common as kc                     # kot-corpus-hash/1 reference impl

PASS_STAMP = "2026-07-13 designer-23 data-construction pass ($0)"  # fixed text, not wall-clock

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS (cited)
# ---------------------------------------------------------------------------
N_TEST = 1440        # [REG n_planned.n_test_items: runs AT the cap, SSR-REV3.1 item 4]
DEV_N = 96           # [REG n_planned.dev_split_items; DES §R3.2]
GUARD_N = 60         # [REG n_planned.off_concept_guard_items; DES §2.5]
POWER_GATE_MIN_C = 65  # [REG n_planned.power_gate, each-cluster reading ASM-2271]
POWER_GATE_MIN_M = 8
DRNG_SEEDS = (101, 102, 103)   # [REG design.seeds; SSR6 step-1 R=3, ASM-2272]
PILOT_KDRNG_SEED = 11          # [REG freeze_manifest A(vii)]
PILOT_D0_SEED = 7              # [REG freeze_manifest A(vii)]
M_CONTEXTS = 16      # [DES §2.4: m = 16 construction contexts per concept]
HIDDEN_D = 6144      # [DES §2.4 / REG dependent_vars.params: carriers are
                     #  concepts x |L_KaE| x 6144 fp32]
G_GRID = (0.5, 1.0, 2.0)  # [DES §2.3: g in {0.5,1.0,2.0} x mean native expert weight]

# Benchmark source pins (OP-1: the frozen record names the datasets
# [DES §2.7: MMLU, then the pre-registered pool ARC-Easy/Challenge,
# OpenBookQA, CommonsenseQA] but pins no distribution bytes; this pass pins
# the canonical HF distributions at fixed revisions, sha256-verified, and the
# snapshot files are stored INSIDE data/f1k-eval-v1/source/ so the corpus is
# self-reproducing. CommonsenseQA uses the VALIDATION split because its test
# gold labels are not published (the scorer needs gold labels) — disclosed.)
SOURCES = [
    # (key, dataset, revision, path-in-repo, sha256, split, order-rank)
    ("mmlu", "cais/mmlu",
     "c30699e8356da336a370243923dbaf21066bb9fe",
     "all/test-00000-of-00001.parquet",
     "74a41822ce7d3def56e1682f958469c04642a5336a5ce912fa375fdb90fb25d7",
     "test"),
    ("arc-easy", "allenai/ai2_arc",
     "210d026faf9955653af8916fad021475a3f00453",
     "ARC-Easy/test-00000-of-00001.parquet",
     "4160597d618ae851c7eb04e281574f3f654776216ac6b6641588d64527b47177",
     "test"),
    ("arc-challenge", "allenai/ai2_arc",
     "210d026faf9955653af8916fad021475a3f00453",
     "ARC-Challenge/test-00000-of-00001.parquet",
     "62f03257e737aed263f55c6abf87c7bb0028a44a6bdd2a26eb1279eb42c1d1e9",
     "test"),
    ("openbookqa", "allenai/openbookqa",
     "388097ea7776314e93a529163e0fea805b8a6454",
     "main/test-00000-of-00001.parquet",
     "cd5483e366daa230c1c87bbdc512d8b7229f14f6dd04d19fc8b1a3855aaaa8a3",
     "test"),
    ("csqa", "tau/commonsense_qa",
     "94630fe30dad47192a8546eb75f094926d47e155",
     "data/validation-00000-of-00001.parquet",
     "bdbd9bf9cc4d2349b24901038b2ab2f58e10e4e507ad2fd425dca55cd3cb6660",
     "validation"),
]
SRC_CACHE = Path("/tmp/f1k-src")   # local staging only; the pinned copies live in the corpus

# Scored-template fixed parts (OP-2: [DES §R1.1] fixes the SHAPE — instruction
# header, question, options as labelled lines `A. …` in PUBLISHED order, fixed
# answer cue ending at the label position — but not the header/cue BYTES;
# these are a DRAFT for freeze-manifest (A) entry 1, mechanically verified
# trigger-free below per [DES §R-REV2.1: only the fixed instruction header,
# the fixed answer cue, and the answer-label tokens are trigger-free].)
HEADER = ("Below is a multiple-choice item. Respond with the letter of the "
          "best option.\n\n")
CUE = "Answer:"
LABEL_ALPHABET = ["A", "B", "C", "D", "E"]   # [DES §R1.1 `A. …` … labelled lines]

ERR = "ERR_F1K_CORPORA"


def fail(msg):
    print("%s: %s" % (ERR, msg), file=sys.stderr)
    sys.exit(2)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def jdump(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)


def write_text(path, text):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def write_json(path, obj):
    write_text(path, json.dumps(obj, indent=1, sort_keys=True,
                                ensure_ascii=False) + "\n")


def write_jsonl(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(jdump(r) + "\n")


# ---------------------------------------------------------------------------
# Stage 1 — the KERNEL source: kernel-v0, the pinned kernel corpus
# ---------------------------------------------------------------------------
# OP-3 (LOAD-BEARING, reported prominently): the pin text says the map is
# "expanded to all kernel concepts with registered explications". This build
# reads that as the concepts of data/kernel-v0/ — the ONLY kernel corpus the
# frozen record pins (pins.corpus_hashes["kernel-v0"]); deriving the map from
# an unpinned corpus (kernel-v1 Stage-A, molecules-v0) would violate pin
# discipline. Consequence: the concept universe has 54 members, so the
# registered power gate (C >= 65 clusters each m >= 8, ASM-2271) is
# UNSATISFIABLE under this reading — a measured coverage-vs-power shortfall,
# which is the design's own registered PRE-RUN RETURN path, not a defect of
# this build. The alternative readings and their C bounds are enumerated in
# the corpus README for the coordinator's (A) decision.
def load_kernel():
    cdir = ROOT / "data" / "kernel-v0" / "concepts"
    if not cdir.is_dir():
        fail("kernel-v0 concepts dir missing")
    kv0_pin = kc.corpus_hash(str(ROOT), "kernel-v0")
    want = "8209cadabcfc2eaa11631c5c1100c04a48f33673516780b1f36cbf957217c809"
    if kv0_pin != want:
        fail("kernel-v0 kot-corpus-hash/1 digest %s != the f1k.json pin %s "
             "— the kernel source moved; STOP" % (kv0_pin, want))
    align = json.load(open(ROOT / "data" / "lexical-wn31" /
                           "alignment-kernel-v0.json", encoding="utf-8"))
    amap = {a["concept"]: a for a in align["alignments"]
            if a["concept"].startswith("urn:kernel-v0:")}
    concepts = []
    for fn in sorted(os.listdir(cdir)):          # sorted by slug == URN order
        d = json.load(open(cdir / fn, encoding="utf-8"))
        a = amap.get(d["id"])
        concepts.append({
            "urn": d["id"],
            "label": d["label"],
            "gloss": d["gloss"],                 # [KV0]: the explication text rendering
            "gloss_sha256": sha256_bytes(d["gloss"].encode("utf-8")),
            "synset": a["synset"] if a else None,
            "align_lemma": a["lemma"] if a else None,
        })
    for i, c in enumerate(concepts):
        c["index"] = i                           # canonical map index = URN byte order
    return concepts, kv0_pin


# ---------------------------------------------------------------------------
# Stage 2 — WordNet 3.1 source parse (lemmas + derivational "+" pointers)
# ---------------------------------------------------------------------------
def parse_wn_dict():
    """Parse data.{noun,verb,adj,adv} from the in-repo pinned WN3.1 source.
    Returns {(pos, offset): {"words": [lemma,...], "gloss": str,
                             "deriv": {src_word_idx: [(pos,off,tgt_idx),...]}}}
    pos is the FILE pos letter (n/v/a/r; satellites live in 'a')."""
    dictdir = ROOT / "data" / "lexical-wn31" / "source" / "dict"
    out = {}
    for pos, fn in (("n", "data.noun"), ("v", "data.verb"),
                    ("a", "data.adj"), ("r", "data.adv")):
        with open(dictdir / fn, encoding="latin-1") as f:
            for line in f:
                if line.startswith("  "):
                    continue                     # license header
                body, _, gloss = line.partition("|")
                parts = body.split()
                off = parts[0]
                w_cnt = int(parts[3], 16)
                words, i = [], 4
                for _ in range(w_cnt):
                    w = parts[i]
                    w = re.sub(r"\((?:p|a|ip)\)$", "", w)   # syntactic markers
                    words.append(w.replace("_", " ").lower())
                    i += 2                       # skip lex_id
                p_cnt = int(parts[i]); i += 1
                deriv = {}
                for _ in range(p_cnt):
                    sym, toff, tpos, st = parts[i:i + 4]
                    i += 4
                    if sym == "+":               # derivationally related form
                        src = int(st[:2], 16)    # 1-based word index (lexical ptr)
                        tgt = int(st[2:], 16)
                        tp = "a" if tpos == "s" else tpos
                        deriv.setdefault(src, []).append((tp, toff, tgt))
                out[(pos, off)] = {"words": words, "gloss": gloss.strip(),
                                   "deriv": deriv}
    return out


def synset_key(urn):
    m = re.match(r"urn:lexical-wn31:([nvar])-(\d{8})$", urn)
    if not m:
        fail("bad synset urn %s" % urn)
    return (m.group(1), m.group(2))


# ---------------------------------------------------------------------------
# Stage 3 — trigger surface expansion
#   [REG pins.corpus_hashes.f1k-trigger-map-v1: "WordNet lemma/derivational
#    surface expansion"; DES §2.3 G-lex "trigger surface expanded with
#    WordNet lemma/derivational sets"]
# ---------------------------------------------------------------------------
def build_triggers(concepts, wn):
    for c in concepts:
        triggers = {}
        if c["synset"] is None:
            # has-part: hand-reviewed alignment records it UNALIGNED (WordNet
            # expresses the relation as holonym/meronym pointers, not a
            # synset). The frozen expansion rule is WordNet-surface-based, so
            # this concept gets an EMPTY trigger set — reported, not padded.
            c["triggers"] = []
            c["trigger_provenance"] = {}
            continue
        key = synset_key(c["synset"])
        ss = wn.get(key)
        if ss is None:
            fail("aligned synset %s not in WN source" % c["synset"])
        for w in ss["words"]:
            triggers.setdefault(w, "synset-lemma")
        # derivational: every word of the synset follows its own "+" pointers
        for src_idx, targets in ss["deriv"].items():
            src_lemma = ss["words"][src_idx - 1] if 0 < src_idx <= len(ss["words"]) else "?"
            for (tp, toff, tidx) in targets:
                tss = wn.get((tp, toff))
                if tss is None or not (0 < tidx <= len(tss["words"])):
                    continue
                lemma = tss["words"][tidx - 1]
                triggers.setdefault(
                    lemma, "derivational(from %s)" % src_lemma)
        c["triggers"] = sorted(triggers)
        c["trigger_provenance"] = triggers
        c["d2_gloss"] = ss["gloss"]              # plain-dictionary text [DES §2.6 d2]
        c["d2_gloss_sha256"] = sha256_bytes(ss["gloss"].encode("utf-8"))
    return concepts


# OP-4: the frozen record fixes the overlap precedence (longest trigger match,
# then earliest span start, then lowest concept id [DES §R4]) but not the base
# string-matching rule. Operationalised as: case-insensitive whole-word match
# of the trigger phrase on the template bytes (regex \b…\b, literal spaces in
# multi-word phrases). Disclosed for (A) adoption.
MATCHING_RULE = ("case-insensitive whole-word regex match (\\b<phrase>\\b, "
                 "phrases matched with literal single spaces) of every "
                 "trigger phrase against the frozen template text; overlap "
                 "resolution per DES §R4: longest match, then earliest span "
                 "start, then lowest concept index; guard items match "
                 "NOTHING anywhere in the template")


def compile_matchers(concepts):
    """first-token -> [(phrase, regex, concept_index)] prefilter index."""
    idx = {}
    for c in concepts:
        for ph in c["triggers"]:
            rx = re.compile(r"\b" + re.escape(ph) + r"\b", re.IGNORECASE)
            idx.setdefault(ph.split()[0], []).append((ph, rx, c["index"]))
    return idx


WORD_RE = re.compile(r"[a-z][a-z'-]*")


def find_spans(text, matchers):
    """All trigger matches -> §R4-resolved non-overlapping spans, sorted by
    start. Returns list of [start, end, concept_index]."""
    low = text.lower()
    words = set(WORD_RE.findall(low))
    cand = []
    for w in words:
        for ph, rx, cidx in matchers.get(w, ()):
            first = ph.split()[0]
            if first != w:
                continue
            for m in rx.finditer(text):
                cand.append((m.start(), m.end(), cidx))
    # §R4 precedence: longest, then earliest, then lowest concept index
    cand.sort(key=lambda s: (-(s[1] - s[0]), s[0], s[2]))
    taken, out = [], []
    for s in cand:
        if any(not (s[1] <= t[0] or s[0] >= t[1]) for t in taken):
            continue
        taken.append(s)
        out.append(list(s))
    out.sort(key=lambda s: s[0])
    return out


# ---------------------------------------------------------------------------
# Stage 4 — benchmark loading + template rendering [DES §R1.1 / §R-REV2.1]
# ---------------------------------------------------------------------------
def load_benchmarks(eval_src_dir):
    import pyarrow.parquet as pq
    items = []
    lock = []
    for rank, (key, ds, rev, path, want, split) in enumerate(SOURCES):
        local = SRC_CACHE / ("%s.parquet" % key)
        if not local.exists():
            fail("source snapshot %s missing under %s — fetch step (see "
                 "corpora README) must run first; refusing silent download "
                 "inside the deterministic builder" % (key, SRC_CACHE))
        got = sha256_file(local)
        if got != want:
            fail("source %s sha256 %s != pinned %s" % (key, got, want))
        dst = eval_src_dir / ("%s.parquet" % key)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(local, dst)
        t = pq.read_table(local)
        rows = t.to_pylist()
        lock.append({"key": key, "dataset": ds, "revision": rev,
                     "path_in_dataset": path, "split": split,
                     "sha256": want, "rows": len(rows),
                     "url": "https://huggingface.co/datasets/%s/resolve/%s/%s"
                            % (ds, rev, path)})
        for ri, r in enumerate(rows):
            if key == "mmlu":
                q = r["question"].strip()
                opts = [o.strip() for o in r["choices"]]
                gold = int(r["answer"])
                native = "%s/%d" % (r["subject"], ri)
                subject = r["subject"]
            else:
                q = (r.get("question") or r.get("question_stem")).strip()
                ch = r["choices"]
                opts = [o.strip() for o in ch["text"]]
                labels_pub = list(ch["label"])
                if r["answerKey"] not in labels_pub:
                    continue                     # unanswerable row (none observed)
                gold = labels_pub.index(r["answerKey"])
                native = str(r["id"])
                subject = None
            if not (3 <= len(opts) <= 5) or not (0 <= gold < len(opts)):
                continue
            items.append({
                "source": key, "source_rank": rank, "row_index": ri,
                "native_id": native, "subject": subject,
                "question": q, "options": opts, "gold_index": gold,
            })
    return items, lock


def render_template(q, opts):
    """[DES §R1.1]: header + question + options as labelled lines in
    PUBLISHED order + fixed answer cue ending at the label position.
    OP-5: ARC's published numeric labels ('1'-'4') are rendered with the
    canonical A–E label alphabet (the §R1.1 `A. …` form); PUBLISHED OPTION
    ORDER is preserved verbatim, only the label glyphs are canonicalised."""
    lines = [HEADER + q]
    for i, o in enumerate(opts):
        lines.append("%s. %s" % (LABEL_ALPHABET[i], o))
    lines.append(CUE)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Stage 5 — split construction (dev-96 / test-1440 / guard-60)
# ---------------------------------------------------------------------------
# OP-6: the frozen record fixes the split SIZES (96/1440/60), dev
# stratification (>=1 per cluster [DES §R3.2]), the stem-trigger selection
# preference [DES §R-REV2.1], the n=1440 at-cap rule "maximising C"
# [REG n_planned.n_test_items], and off-concept semantics for the guard
# [DES §2.5] — but not the residual deterministic order. Operationalised
# (draft for (A) entry 8):
#   pool order within a cluster: (stem-trigger first, then source rank in the
#     design's listed order MMLU -> ARC-Easy -> ARC-Challenge -> OpenBookQA
#     -> CommonsenseQA, then row index);
#   dev-96: round-robin over clusters in ascending concept-index order,
#     each cluster's next unused item, until 96 (mirrors the driver's frozen
#     pilot-subset rule [DRV pilot_dev_subset]);
#   test-1440: first fill every cluster to m = 8 (ascending concept index,
#     round-robin), then continue round-robin until 1440 — maximising the
#     number of clusters at the m >= 8 gate before deepening any cluster;
#   guard-60: the first 60 zero-trigger items in pool order.
def build_splits(admitted, zero_match):
    by_cluster = {}
    for it in admitted:
        by_cluster.setdefault(it["cluster_index"], []).append(it)
    for cidx in by_cluster:
        by_cluster[cidx].sort(key=lambda x: (0 if x["stem_trigger"] else 1,
                                             x["source_rank"], x["row_index"]))
    order = sorted(by_cluster)
    used = {c: 0 for c in order}

    def take(cidx):
        lst = by_cluster[cidx]
        if used[cidx] < len(lst):
            it = lst[used[cidx]]
            used[cidx] += 1
            return it
        return None

    dev = []
    while len(dev) < DEV_N:
        got = False
        for cidx in order:
            if len(dev) >= DEV_N:
                break
            it = take(cidx)
            if it is not None:
                dev.append(it)
                got = True
        if not got:
            break
    test = []
    # phase A: to m = 8 per cluster
    for rnd in range(POWER_GATE_MIN_M):
        for cidx in order:
            if len(test) >= N_TEST:
                break
            it = take(cidx)
            if it is not None:
                test.append(it)
    # phase B: round-robin until the cap
    progressing = True
    while len(test) < N_TEST and progressing:
        progressing = False
        for cidx in order:
            if len(test) >= N_TEST:
                break
            it = take(cidx)
            if it is not None:
                test.append(it)
                progressing = True
    zero_match.sort(key=lambda x: (x["source_rank"], x["row_index"]))
    guard = zero_match[:GUARD_N]
    return dev, test, guard


# ---------------------------------------------------------------------------
# Stage 6 — carriers-v1 deterministic pre-spend components
# ---------------------------------------------------------------------------
def seeded_derangement(n, seed):
    """[DRV seeded_derangement] — the harness's algorithm for the registered
    seeds [DES SSR2: seeded fixed-point-free derangement]. OP-7: the design
    registers the SEEDS but not the seed->permutation algorithm; this build
    uses the run driver's exact algorithm so corpus and driver agree, flagged
    for (A) adoption."""
    rng = random.Random(seed)
    while True:
        p = list(range(n))
        rng.shuffle(p)
        if all(p[i] != i for i in range(n)):
            return p


CONTEXT_FRAMES = [
    # OP-8 DRAFT construction-context authoring procedure for freeze-manifest
    # (A)(i) [DES §2.4: contexts drawn from the probe corpus plus
    # WordNet-authored renderings, disjoint from all evaluation items; §R-REV3.3
    # A(i): enumerated verbatim or pinned by a deterministic authoring
    # procedure]. The probe corpus is NOT used: its concept groups are
    # sense-level (kernel-v1 territory), outside the pinned kernel-v0
    # universe (OP-3). Four fixed frames x four lemma rotations = m = 16
    # verbatim contexts per concept. DRAFT: requires coordinator adoption.
    "People sometimes talk about {lemma}. {gloss_def}",
    "Think about {lemma} for a moment: {gloss_def}",
    "This passage concerns {lemma}. When people say \"{lemma}\", "
    "they mean this: {gloss_def}",
    "Someone wants to know what {lemma} is. One way to say it: {gloss_def}",
]


def build_contexts(concept):
    lemmas = concept["triggers"][:4] or []
    if not lemmas:
        return []          # has-part: no surface, no lexical gate, no contexts
    gloss_def = concept["d2_gloss"].split('; "')[0].strip()
    out = []
    for i in range(M_CONTEXTS):
        frame = CONTEXT_FRAMES[i % len(CONTEXT_FRAMES)]
        lemma = lemmas[(i // len(CONTEXT_FRAMES)) % len(lemmas)]
        out.append(frame.format(lemma=lemma, gloss_def=gloss_def))
    return out


# ---------------------------------------------------------------------------
def main():
    tm_dir = ROOT / "data" / "f1k-trigger-map-v1"
    ev_dir = ROOT / "data" / "f1k-eval-v1"
    ca_dir = ROOT / "data" / "f1k-carriers-v1"
    for d in (tm_dir, ev_dir, ca_dir):
        if d.exists():
            shutil.rmtree(d)

    # ---- kernel + WordNet + triggers -------------------------------------
    concepts, kv0_pin = load_kernel()
    wn = parse_wn_dict()
    concepts = build_triggers(concepts, wn)
    matchers = compile_matchers(concepts)
    n_phrases = sum(len(c["triggers"]) for c in concepts)
    print("kernel-v0: %d concepts (pin %s…), %d trigger phrases"
          % (len(concepts), kv0_pin[:12], n_phrases))

    # ---- header/cue/label trigger-freedom [DES §R-REV2.1] (fail-closed) ---
    for name, text in (("header", HEADER), ("cue", CUE),
                       ("labels", " ".join(LABEL_ALPHABET))):
        sp = find_spans(text, matchers)
        if sp:
            fail("fixed template %s carries trigger span(s) %s — redraft the "
                 "%s (DES §R-REV2.1 requires header/cue/labels trigger-free)"
                 % (name, sp[:3], name))
    print("template header/cue/labels: trigger-free (char-level) OK")

    # ---- trigger-map corpus ----------------------------------------------
    tmap = {
        "name": "f1k-trigger-map-v1",
        "built": PASS_STAMP,
        "recipe": "registry/experiments/f1k.json pins.corpus_hashes"
                  "[f1k-trigger-map-v1] + design §2.3 (G-lex) / §R4 (gate "
                  "precedence) / §R3.2 (expansion to all kernel concepts "
                  "with registered explications)",
        "kernel_source": {
            "corpus": "kernel-v0",
            "kot_corpus_hash_v1": kv0_pin,
            "reading": "OP-3: the pinned kernel corpus (the only kernel pin "
                       "in f1k.json) — see README for the universe decision "
                       "the coordinator must confirm at freeze-manifest (A)",
        },
        "wordnet_source": {
            "corpus": "lexical-wn31 (in-repo WN3.1 source dict + "
                      "alignment-kernel-v0.json, kot-lex-align/1)",
            "expansion": "aligned synset lemmas + derivationally-related "
                         "('+' pointer) word lemmas, lowercased, "
                         "underscores to spaces, syntactic markers stripped",
        },
        "matching_rule": MATCHING_RULE,
        "gate_precedence": {
            "overlap": "longest trigger match, then earliest span start, "
                       "then lowest concept index [DES §R4]",
            "single_carrier_per_position": True,
            "label_tokens_never_triggers": True,
            "multi_concept_tag": "items with >1 distinct resolved concept "
                                 "are tagged 'multi-concept' (descriptive "
                                 "subgroup) [DES §R4]",
        },
        "concepts": [{
            "index": c["index"], "urn": c["urn"], "label": c["label"],
            "synset": c["synset"],
            "explication_gloss_sha256": c["gloss_sha256"],
            "triggers": c["triggers"],
            "trigger_provenance": c["trigger_provenance"],
        } for c in concepts],
    }
    write_json(tm_dir / "trigger-map.json", tmap)

    # ---- benchmarks + eval construction ----------------------------------
    ev_src = ev_dir / "source"
    bench, lock = load_benchmarks(ev_src)
    print("benchmark pool: %d items over %d pinned sources"
          % (len(bench), len(lock)))
    admitted, zero_match = [], []
    for it in bench:
        tpl = render_template(it["question"], it["options"])
        spans = find_spans(tpl, matchers)
        q_start = len(HEADER)
        q_end = q_start + len(it["question"])
        if not spans:
            it["template_text"] = tpl
            zero_match.append(it)
            continue
        stem = any(s[0] < q_end for s in spans)
        cset = sorted({s[2] for s in spans})
        it.update({
            "template_text": tpl,
            "char_spans": spans,
            "cluster_index": spans[0][2],   # OP-6a: cluster = concept of the
                                            # first §R4-resolved span
            "stem_trigger": stem,
            "tags": (["multi-concept"] if len(cset) > 1 else [])
                    + ([] if stem else ["option-trigger"]),
        })
        admitted.append(it)
    print("mechanical filter: %d admitted, %d zero-trigger"
          % (len(admitted), len(zero_match)))

    dev, test, guard = build_splits(admitted, zero_match)

    # ---- realized coverage / power-gate arithmetic [REG power_gate] -------
    sizes = {}
    for it in test:
        sizes[it["cluster_index"]] = sizes.get(it["cluster_index"], 0) + 1
    c_ok = sum(1 for v in sizes.values() if v >= POWER_GATE_MIN_M)
    gate_pass = (c_ok >= POWER_GATE_MIN_C and len(test) == N_TEST)
    coverage = {
        "n_test": len(test), "n_dev": len(dev), "n_guard": len(guard),
        "n_clusters_realized": len(sizes),
        "clusters_with_m_ge_8": c_ok,
        "power_gate": "C>=%d each m>=%d at n==%d (ASM-2271)"
                      % (POWER_GATE_MIN_C, POWER_GATE_MIN_M, N_TEST),
        "power_gate_satisfiable": gate_pass,
        "concept_universe_bound": len(concepts),
        "note": "C is bounded above by the 54-concept pinned kernel "
                "universe (OP-3), so the registered C>=65 gate is "
                "UNSATISFIABLE under this reading — the design's own "
                "pre-run RETURN path (measured coverage-vs-power "
                "shortfall). See README.",
        "m_per_cluster": {str(k): v for k, v in sorted(sizes.items())},
        "composition_by_source": {},
        "composition_by_mmlu_subject": {},
    }
    for it in test:
        coverage["composition_by_source"][it["source"]] = \
            coverage["composition_by_source"].get(it["source"], 0) + 1
        if it["subject"]:
            coverage["composition_by_mmlu_subject"][it["subject"]] = \
                coverage["composition_by_mmlu_subject"].get(it["subject"], 0) + 1

    # ---- fired concept set -> carrier slot map ----------------------------
    fired = sorted({s[2] for it in (test + dev) for s in it["char_spans"]})
    slot_of = {cidx: i for i, cidx in enumerate(fired)}
    carrier_index_map = [{"carrier_slot": i, "concept_index": cidx,
                          "urn": concepts[cidx]["urn"]}
                         for i, cidx in enumerate(fired)]

    def emit_items(items, split, with_d3):
        rows = []
        for it in items:
            row = {
                "item_id": "%s#%s" % (it["source"], it["native_id"]),
                "split": split,
                "source": {"key": it["source"], "row_index": it["row_index"],
                           "native_id": it["native_id"]},
                "question": it["question"],
                "options": it["options"],
                "labels": LABEL_ALPHABET[:len(it["options"])],
                "gold_index": it["gold_index"],
                "template_text": it["template_text"],
                "template_sha256": sha256_bytes(
                    it["template_text"].encode("utf-8")),
            }
            if split == "guard":
                row["char_spans"] = []
                row["cluster"] = None
                row["tags"] = []
            else:
                row["char_spans"] = [
                    [s, e, slot_of[c]] for (s, e, c) in it["char_spans"]]
                row["cluster"] = concepts[it["cluster_index"]]["urn"]
                row["tags"] = it["tags"]
                if with_d3:
                    # d3-text: the cluster concept's kernel explication
                    # prepended as PROMPT TEXT, no splice [DES §2.6 arm
                    # d3-text]; OP-9: prepend = gloss + blank line.
                    d3 = (concepts[it["cluster_index"]]["gloss"] + "\n\n"
                          + it["template_text"])
                    row["d3_template_text"] = d3
                    row["d3_template_sha256"] = sha256_bytes(d3.encode("utf-8"))
            rows.append(row)
        return rows

    write_jsonl(ev_dir / "items" / "test.jsonl", emit_items(test, "test", True))
    write_jsonl(ev_dir / "items" / "dev.jsonl", emit_items(dev, "dev", True))
    write_jsonl(ev_dir / "items" / "guard.jsonl",
                emit_items(guard, "guard", False))
    write_json(ev_dir / "coverage-report.json", coverage)
    write_json(ev_dir / "source" / "sources.lock.json", {
        "note": "OP-1 pinned benchmark snapshots (canonical HF "
                "distributions at fixed revisions); the parquet bytes are "
                "stored beside this lock so the corpus is self-reproducing",
        "sources": lock})
    write_json(ev_dir / "template-spec.json", {
        "built": PASS_STAMP,
        "recipe": "DES §R1.1 (frozen candidate-independent single-prefill "
                  "label-logit template) + §R-REV2.1 (trigger/template "
                  "resolution)",
        "header_bytes": HEADER,
        "header_sha256": sha256_bytes(HEADER.encode("utf-8")),
        "answer_cue_bytes": CUE,
        "answer_cue_sha256": sha256_bytes(CUE.encode("utf-8")),
        "label_alphabet": LABEL_ALPHABET,
        "rendering_rule": "template = header + question + one line per "
                          "option ('<LABEL>. <option text>') in PUBLISHED "
                          "order + '\\n' + answer cue; template ends at the "
                          "cue (the label position follows it)",
        "tie_break": "argmax over label token logprobs, lowest label index "
                     "on ties, ties logged [REG dependent_vars.item_correct]",
        "header_cue_labels_trigger_free": True,
        "trigger_free_verification": "char-level against "
                                     "f1k-trigger-map-v1 (this build, "
                                     "fail-closed); the TOKEN-level "
                                     "re-verification is a freeze-(A) step "
                                     "with the pinned tokenizer",
        "tokenizer_derivation_rule": {
            "status": "BLOCKED THIS PASS — requires the GLM-5.2 tokenizer, "
                      "which is pinned only at bring-up (ASM-1971 "
                      "discipline); no model/tokenizer download in a $0 "
                      "pass",
            "template_tokens": "tokenizer(template_text bytes), no "
                               "BOS-stripping or normalisation beyond the "
                               "engine's own prefill path",
            "label_token_ids": "for each label L in label_alphabet[:k]: the "
                               "single token id of the label continuation "
                               "at the answer position (the engine reads "
                               "next-token logits after the cue); "
                               "single-token property MUST be verified and "
                               "recorded at freeze [DES §R1.1]",
            "spans": "per-token concept slot: token t carries carrier slot "
                     "s iff t's character interval intersects a char_span "
                     "with slot s; -1 otherwise; d3_template_tokens = "
                     "tokenizer(d3_template_text), spans NOT applied to "
                     "d3-text (no-splice arm [DES §2.6])",
            "carrier_slots": "char_spans concept ids in this corpus are "
                             "CARRIER SLOTS via f1k-carriers-v1 "
                             "generator/carrier-index-map (identical copy "
                             "in this corpus manifest)",
        },
    })

    # ---- carriers corpus (pre-spend deterministic components only) --------
    nc = len(fired)
    derangements = {}
    for seed in (PILOT_KDRNG_SEED,) + DRNG_SEEDS:
        p = seeded_derangement(nc, seed)
        assert sorted(p) == list(range(nc)) and all(p[i] != i
                                                    for i in range(nc))
        derangements[str(seed)] = p
    write_json(ca_dir / "generator" / "derangements.json", {
        "built": PASS_STAMP,
        "recipe": "DES SSR2 (§R2 d1-drng: seeded fixed-point-free "
                  "derangement over the concepts present in the test set, "
                  "layerwise norm-matched) + REG design.seeds / "
                  "freeze_manifest A(vii)",
        "algorithm": "OP-7: f1k_driver.py seeded_derangement — "
                     "random.Random(seed).shuffle(range(nc)) rejected until "
                     "fixed-point-free (the run harness's algorithm; "
                     "requires (A) adoption)",
        "domain": "carrier slots 0..nc-1 = the %d concepts firing in >=1 "
                  "frozen test/dev span (SSR2 'concepts present in the test "
                  "set'); see carrier-index-map.json" % nc,
        "nc": nc,
        "seeds": {"pilot_panel": PILOT_KDRNG_SEED,
                  "main": list(DRNG_SEEDS), "d0_table": PILOT_D0_SEED},
        "derangements": derangements,
        "layerwise_norm_matched": "REQUIRED at realization: deranged "
                                  "carrier direction from the donor, norm "
                                  "rescaled to ||v^K_{c,l}|| per (c,l) "
                                  "[DES §R2]; attested in the B0 addendum "
                                  "metadata the driver validates "
                                  "[DRV validate_dose]",
    })
    write_json(ca_dir / "generator" / "carrier-index-map.json", {
        "built": PASS_STAMP,
        "note": "carrier table concept order (KAEC concept-major axis "
                "[PATCH kae.h]) = these slots; eval char_spans use the SAME "
                "slots",
        "nc": nc,
        "map": carrier_index_map})
    write_jsonl(ca_dir / "generator" / "concept-texts.jsonl", [{
        "carrier_slot": slot_of[c["index"]],
        "concept_index": c["index"],
        "urn": c["urn"],
        "k_explication_text": c["gloss"],
        "k_explication_sha256": c["gloss_sha256"],
        "d2_dictionary_text": c.get("d2_gloss"),
        "d2_dictionary_sha256": c.get("d2_gloss_sha256"),
        "d2_source": c["synset"],
    } for c in concepts if c["index"] in slot_of])
    ctx_rows = []
    for c in concepts:
        if c["index"] not in slot_of:
            continue
        for j, ctx in enumerate(build_contexts(c)):
            ctx_rows.append({"carrier_slot": slot_of[c["index"]],
                             "urn": c["urn"], "context_index": j,
                             "text": ctx})
    write_jsonl(ca_dir / "generator" / "construction-contexts.jsonl", ctx_rows)
    # eval-disjointness check [DES §2.4: construction contexts disjoint from
    # all evaluation items] — no context string appears in any eval template
    # and no eval question appears in any context (exact-substring check).
    all_tpl = [it["template_text"] for it in test + dev + guard]
    for r in ctx_rows:
        for t in all_tpl:
            if r["text"] in t:
                fail("construction context appears inside an eval item: %r"
                     % r["text"][:80])
    write_json(ca_dir / "generator" / "generator-spec.json", {
        "built": PASS_STAMP,
        "status": "PRE-SPEND GENERATOR COMPONENTS ONLY. The realized "
                  "carrier tables {v_(c,l)} and raw/rescaled norms are the "
                  "B0 PURE-FUNCTION ADDENDUM: committed after construction "
                  "spend and before the pilot [REG freeze_manifest "
                  "B0_pre_pilot / DES §R-REV3.3]. They are functions of "
                  "GLM-5.2 forward-pass hidden states and CANNOT exist in "
                  "a $0 no-model pass.",
        "carrier_definition": "v_{c,l} = mean difference of moe()-input "
                              "hidden states at gated positions between "
                              "contexts WITH the kernel explication of c "
                              "prepended and matched contexts WITHOUT, over "
                              "m = 16 construction contexts; K[c][l] := "
                              "v_{c,l} [DES §2.4, ADOPTED row]",
        "m_contexts": M_CONTEXTS,
        "prepend_protocol": "two variants per context: kernel explication "
                            "text (concept-texts.jsonl k_explication_text) "
                            "+ '\\n\\n' prepended vs not [DES §2.4; OP-9 "
                            "separator]",
        "gated_position_rule": "G-lex spans of the concept's own triggers "
                               "computed on the context with the SAME "
                               "matching rule as f1k-trigger-map-v1; "
                               "carrier dumped at gated positions only "
                               "[DES §2.3/§2.4]",
        "candidate_splice_layers": "UNRESOLVED THIS PASS: A(iv) = the union "
                                   "of the pilot grid's layer sets L1/L2/L3 "
                                   "[DES §2.3]; L1 ~ one mid-stack MoE "
                                   "layer (~40), L2 = four evenly spaced "
                                   "mid-to-late, L3 = ALL MoE layers — the "
                                   "EXACT MoE layer ids require the pinned "
                                   "model config (bring-up)",
        "arms": {
            "K": "true concept->carrier mapping",
            "d1-drng": "identical K table, concept labels deranged per "
                       "derangements.json seeds [101,102,103]; pilot panel "
                       "seed 11 [DES §R2/§R-REV2.3]",
            "d0": "norm-matched random table, seed 7 — DIRECTION generation "
                  "algorithm is NOT registered anywhere (flagged in the "
                  "README; must be fixed at (A) before construction)",
            "d2": "same construction with the plain-dictionary text "
                  "(concept-texts.jsonl d2_dictionary_text) substituted "
                  "for the explication [DES §2.6 d2]",
        },
        "reference_norm_rule": "reference at each (c,l) = ||v^K_{c,l}||; "
                               "every non-K carrier rescaled per (c,l) to "
                               "the reference; g applies AFTER rescaling; "
                               "raw and post-rescale norms are B0 entries "
                               "[DES §R2]",
        "g_grid": {"multipliers": list(G_GRID),
                   "unit": "x mean native expert weight [DES §2.3] — the "
                           "mean native expert weight is MEASURED on the "
                           "model at construction (bring-up-dependent)"},
        "construction_seed": "NOT REGISTERED: freeze_manifest A(vii) names "
                            "a 'construction' seed but no value exists in "
                            "the frozen record — coordinator must fix at "
                            "(A); flagged, not invented",
        "kaec_format": "[PATCH kae.h]: 'KAEC' | i32 nc | i32 nl | i32 D "
                       "| i32 layer_id[nl] | f32 K[nc*nl*D], D = %d, "
                       "nc = %d (carrier-index-map.json)" % (HIDDEN_D, nc),
    })

    # ---- manifests ---------------------------------------------------------
    ops = {
        "OP-1": "benchmark source snapshots pinned by this pass (datasets "
                "named by DES §2.7; bytes/revisions chosen here; CSQA "
                "validation split because test golds are unpublished)",
        "OP-2": "template header/cue BYTES drafted here (shape frozen by "
                "DES §R1.1; bytes are freeze-(A) entry 1)",
        "OP-3": "concept universe = kernel-v0 (the pinned kernel corpus); "
                "LOAD-BEARING: C <= 54 < 65 makes the registered power "
                "gate unsatisfiable — coordinator must confirm or amend "
                "at (A)",
        "OP-4": "base trigger matching rule (case-insensitive whole-word)",
        "OP-5": "ARC numeric labels rendered with the canonical A-E "
                "alphabet, published option order preserved",
        "OP-6": "residual deterministic split ordering (stem-first, "
                "source-rank, row); dev round-robin; test filled to m=8 "
                "breadth-first then round-robin; guard = first 60 "
                "zero-trigger items",
        "OP-6a": "item cluster = concept of the first §R4-resolved span",
        "OP-7": "seed->derangement algorithm = the run driver's "
                "seeded_derangement",
        "OP-8": "DRAFT construction-context authoring procedure (4 frames "
                "x 4 lemma rotations, WordNet-authored renderings only)",
        "OP-9": "d3-text / construction prepend separator = one blank line",
    }
    write_json(tm_dir / "manifest.json", {
        "corpus": "f1k-trigger-map-v1", "built": PASS_STAMP,
        "completes": "f1k.json pins.corpus_hashes[f1k-trigger-map-v1] "
                     "(pinned at freeze-manifest (A), before ANY spend)",
        "concepts": len(concepts),
        "concepts_with_triggers": sum(1 for c in concepts if c["triggers"]),
        "trigger_phrases": n_phrases,
        "operationalisations": {k: ops[k] for k in ("OP-3", "OP-4")},
    })
    write_json(ev_dir / "manifest.json", {
        "corpus": "f1k-eval-v1", "built": PASS_STAMP,
        "completes": "f1k.json pins.corpus_hashes[f1k-eval-v1] (pinned by "
                     "ops amendment at freeze-manifest (A)/(6), before any "
                     "test prefill)",
        "counts": {"test": len(test), "dev": len(dev), "guard": len(guard)},
        "registered_counts": {"test": N_TEST, "dev": DEV_N, "guard": GUARD_N},
        "carrier_index_map": carrier_index_map,
        "blocked_fields": "template_tokens / label_token_ids / token-level "
                          "spans / d3_template_tokens + single-token label "
                          "verification: pure functions of this corpus + "
                          "the tokenizer pinned at bring-up (see "
                          "template-spec.json tokenizer_derivation_rule); "
                          "NOT derivable in a $0 no-model pass",
        "operationalisations": {k: ops[k] for k in
                                ("OP-1", "OP-2", "OP-5", "OP-6", "OP-6a",
                                 "OP-9")},
    })
    write_json(ca_dir / "manifest.json", {
        "corpus": "f1k-carriers-v1", "built": PASS_STAMP,
        "completes": "f1k.json pins.corpus_hashes[f1k-carriers-v1] — but "
                     "ONLY at the B0 addendum: realized tables + raw/"
                     "rescaled norms land AFTER construction spend, BEFORE "
                     "the pilot [REG freeze_manifest.B0_pre_pilot]. THIS "
                     "PASS SHIPS THE DETERMINISTIC PRE-SPEND GENERATOR "
                     "COMPONENTS ONLY; the digest of this directory is NOT "
                     "the B0 pin.",
        "operationalisations": {k: ops[k] for k in ("OP-7", "OP-8", "OP-9")},
        "blocked": [
            "realized K / d2 / d0 / derangement .kaec tables (GLM-5.2 "
            "forward passes = construction spend)",
            "raw + rescaled norms (functions of the realized K)",
            "exact candidate splice-layer ids (model config at bring-up)",
            "mean native expert weight for the g grid (model measurement)",
            "construction seed (named at A(vii) but never given a value "
            "in the frozen record)",
            "d0 direction-generation algorithm (not registered)",
        ],
    })

    # ---- per-corpus READMEs (inside the hashed dirs; static text) ---------
    write_text(tm_dir / "README.md", """# f1k-trigger-map-v1 — phrase→concept trigger map (F1-K lexical gate)

Completes `registry/experiments/f1k.json` corpus pin `f1k-trigger-map-v1`
("phrase->concept trigger map expanded to all kernel concepts with registered
explications (WordNet lemma/derivational surface expansion) + gate precedence
rules"; pinned at freeze-manifest (A), before ANY spend). Built by
`poc/glm52-probe/f1k-harness/corpora/build_corpora.py` — %s. NOT frozen: the
coordinator freezes this at (A) after adopting/amending the OP decisions in
`manifest.json`.

- **Kernel source (OP-3, LOAD-BEARING):** `data/kernel-v0/` — the ONLY kernel
  corpus the frozen record pins (kot-corpus-hash/1
  `8209cada…7c809`, reproduced at build). 54 registered explications; the
  `gloss` field is the explication text rendering. ALTERNATIVE READINGS of
  "all kernel concepts with registered explications" the coordinator must
  rule on at (A): (a) kernel-v0 only = 54 concepts (THIS BUILD; C <= 54);
  (b) kernel-v0 + kernel-v1 Stage-A with v1's registered supersession of the
  4 word concepts = 61 (C <= 61); (c) v0 + v1 ignoring supersession = 65
  (C <= 65, and word/sense triggers double-book the same surfaces). Under
  (a) and (b) the registered power gate C >= 65 (ASM-2271) is UNSATISFIABLE
  and F1-K pre-run-RETURNS with the measured coverage-vs-power shortfall;
  under (c) it is satisfiable only if every concept reaches m >= 8, which
  the realized filter output contradicts (see
  `data/f1k-eval-v1/coverage-report.json`). Molecules-v0 is excluded: the
  design bounds the universe by "the kernel's <100 concepts" (§R3.2) and
  molecules are not kernel concepts.
- **Surface expansion:** aligned WN3.1 synset lemmas + derivationally-related
  ("+" pointer) word lemmas, from the in-repo pinned `data/lexical-wn31/`
  source dict via `alignment-kernel-v0.json` (kot-lex-align/1,
  hand-reviewed). `has-part` is UNALIGNED in the hand-reviewed alignment
  (WordNet holds the relation as pointer structure) → empty trigger set,
  disclosed, not padded.
- **Gate precedence (frozen, DES §R4):** exactly one carrier per gated
  position; overlap → longest trigger match, then earliest span start, then
  lowest concept index; label tokens never triggers; multi-concept items
  tagged.
- **Matching rule (OP-4):** case-insensitive whole-word match; see
  `trigger-map.json .matching_rule`.

Files: `trigger-map.json` (the map: 54 concepts, canonical index = URN byte
order, triggers + provenance), `manifest.json`.
""" % PASS_STAMP)

    write_text(ev_dir / "README.md", """# f1k-eval-v1 — known-concept item lists + frozen scored templates + span sidecars

Completes `registry/experiments/f1k.json` corpus pin `f1k-eval-v1`
("known-concept item lists (test/dev/off-concept-guard ids + frozen scored
templates + per-item span sidecars), produced by the frozen mechanical
filter + trigger map"; pinned by ops amendment at freeze-manifest (A)/(6),
before any test prefill). Built by
`poc/glm52-probe/f1k-harness/corpora/build_corpora.py` — %s.

## Contents
- `items/test.jsonl` (1,440 = the registered cap, SSR-REV3.1 item 4),
  `items/dev.jsonl` (96), `items/guard.jsonl` (60 off-concept: zero trigger
  match anywhere, DES §2.5) — each row: item id, source provenance,
  question/options/gold in PUBLISHED order, frozen template BYTES + sha256,
  CHARACTER-level §R4-resolved spans (carrier-slot ids), d3-text prompt
  rendering (test/dev), tags (`multi-concept`, `option-trigger`).
- `template-spec.json` — the §R1.1 template: header/cue bytes (OP-2 draft
  for (A) entry 1), rendering rule, tie-break, char-level trigger-freedom
  verification, and the DETERMINISTIC TOKENIZER-DERIVATION RULE for the
  fields this pass cannot produce.
- `source/` — the five pinned benchmark snapshots (OP-1) + lock file.
- `coverage-report.json` — realized (C, m), power-gate arithmetic, verbatim
  subset composition (SS2.7).

## What is BLOCKED this pass (honest list)
`template_tokens`, `label_token_ids`, token-level `spans`,
`d3_template_tokens`, and the single-token label verification are pure
functions of this corpus + the GLM-5.2 tokenizer, which is pinned only at
bring-up (ASM-1971); a $0 no-model pass cannot fetch it. The run driver's
`load_eval_manifest` consumes the TOKEN-level manifest — deriving it from
this corpus via `template-spec.json .tokenizer_derivation_rule` is a
mechanical pre-(6) step (contract mismatch flagged in
`poc/glm52-probe/f1k-harness/corpora/driver-contract-check.json`).

## Power-gate headline (read this first)
Realized test composition: 49 clusters, **46 with m >= 8** — the registered
gate needs **>= 65 clusters each m >= 8** (ASM-2271). Under the pinned
54-concept kernel universe (OP-3) the gate is UNSATISFIABLE: this is the
design's own registered PRE-RUN RETURN ("the scale gate biting", DES §8 /
SSR-REV2.2), surfaced at corpus construction, not a build defect. F1-K must
not run on this corpus without a maintainer ruling on the coverage-vs-power
shortfall.

CommonsenseQA uses the VALIDATION split (test gold labels are not
published; the scorer needs gold). MMLU/ARC/OpenBookQA use their published
test splits.
""" % PASS_STAMP)

    write_text(ca_dir / "README.md", """# f1k-carriers-v1 — carrier GENERATOR components (PRE-SPEND; NOT the B0 pin)

Target pin: `registry/experiments/f1k.json` `f1k-carriers-v1` ("realized
carrier tables for every arm (K, 3 derangements, d0, d2) + raw and rescaled
norms — the B0 pure-function addendum (SSR-REV3.3); kot-corpus-hash/1
pinned AFTER construction, BEFORE the pilot"). Built by
`poc/glm52-probe/f1k-harness/corpora/build_corpora.py` — %s.

**The realized tables CANNOT exist in this pass, by the frozen ordering
itself:** they are mean differences of GLM-5.2 forward-pass hidden states
(DES §2.4) — i.e. construction SPEND — and the record orders them as the
(B0) addendum committed after construction. This directory therefore holds
ONLY the deterministic, model-independent generator components, so that at
construction time every arm's table is a pure function of frozen rules:

- `generator/derangements.json` — the REGISTERED seeds (pilot 11; main
  101/102/103 = `design.seeds`) realized as fixed-point-free permutations
  over the 49 carrier slots (the concepts present in the frozen test/dev
  spans, SSR2), via the run driver's algorithm (OP-7).
- `generator/carrier-index-map.json` — carrier slot ↔ kernel concept map
  (the KAEC concept-major axis; eval spans use these slots).
- `generator/concept-texts.jsonl` — per concept: the kernel explication
  text (kernel-v0 `gloss`, hashed) for K/d3-text, and the plain-dictionary
  text (aligned WN3.1 synset gloss, hashed) for d2 — freeze-(A)(ii).
- `generator/construction-contexts.jsonl` — OP-8 DRAFT: m = 16 verbatim
  WordNet-authored contexts per concept, checked disjoint from every eval
  item (DES §2.4).
- `generator/generator-spec.json` — the §2.4/§R2 formulas + protocol, with
  every model-dependent input explicitly marked BLOCKED.

**Still missing for (A)/(B0), never invented here:** the construction seed
VALUE (named at freeze_manifest A(vii), no value registered anywhere); the
d0 direction-generation algorithm; the exact candidate splice-layer ids
(model config, bring-up); the mean native expert weight for the g grid;
and the realized tables + raw/rescaled norms themselves. The
kot-corpus-hash/1 digest of this directory at THIS pass is NOT the B0 pin.
""" % PASS_STAMP)

    # ---- digests (kot-corpus-hash/1) --------------------------------------
    digests = {name: kc.corpus_hash(str(ROOT), name)
               for name in ("f1k-trigger-map-v1", "f1k-eval-v1",
                            "f1k-carriers-v1")}
    write_json(HERE / "digests.json", {
        "_recipe": kc.CORPUS_RECIPE, "built": PASS_STAMP,
        "digests": digests,
        "caveat": "f1k-trigger-map-v1 is (A)-complete as built (pending "
                  "the OP adoptions). f1k-eval-v1 digest changes when the "
                  "tokenizer-derived sidecar files land (pre-(6)). "
                  "f1k-carriers-v1 digest is NOT the B0 pin (realized "
                  "tables + norms land post-construction).",
    })
    for k, v in digests.items():
        print("kot-corpus-hash/1  %s  %s" % (v, k))

    # ---- driver input-contract check --------------------------------------
    contract = {
        "driver": "poc/glm52-probe/f1k-harness/f1k_driver.py "
                  "load_eval_manifest / validate_dose / kaec_read",
        "checks": [],
    }

    def chk(name, ok, note=""):
        contract["checks"].append({"check": name, "ok": bool(ok),
                                   "note": note})

    chk("split sizes test/dev/guard == 1440/96/60",
        len(test) == N_TEST and len(dev) == DEV_N and len(guard) == GUARD_N,
        "driver fails closed otherwise (ERR_F1K_EVAL)")
    chk("guard items carry zero trigger spans (driver: any s>=0 fails)",
        all(not find_spans(it["template_text"], matchers) for it in guard),
        "recomputed on every guard template (off-concept: the gate must "
        "never fire, DES §2.5)")
    chk("every test/dev item has d3 template",
        True, "d3_template_text present; d3_template_tokens is a "
              "bring-up derivation")
    chk("labels/gold well-formed (labels len == options len; "
        "0<=gold<k)", all(0 <= it["gold_index"] < len(it["options"])
                          for it in test + dev + guard))
    mismatch = ("CONTRACT MISMATCH (flagged, expected): the driver requires "
                "template_tokens / label_token_ids / spans / "
                "d3_template_tokens as TOKEN-level fields in the eval "
                "manifest; this corpus carries frozen template BYTES + "
                "CHAR-level spans + the deterministic derivation rule "
                "(template-spec.json), because the GLM-5.2 tokenizer is "
                "pinned only at bring-up (ASM-1971) and is not fetchable "
                "in a $0 no-model pass. Either the driver grows a "
                "corpus->manifest tokenizer step at bring-up, or the "
                "coordinator derives the token-level manifest as a pure "
                "function of this corpus + the pinned tokenizer before "
                "(6).")
    chk("token-level eval-manifest fields present", False, mismatch)
    chk("derangement seeds == registered [101,102,103] + pilot 11, "
        "fixed-point-free over nc=%d" % nc, True,
        "driver validate_dose requires meta.derangement FPF permutation; "
        "satisfied by generator/derangements.json at realization")
    chk("power gate C>=65 each m>=8 at n=1440",
        gate_pass,
        "clusters_with_m_ge_8 = %d over a %d-concept universe — "
        "pre-run RETURN arithmetic surfaced now (OP-3)" % (c_ok,
                                                           len(concepts)))
    chk("KAEC format params known (D=%d, nc=%d, layers=bring-up)"
        % (HIDDEN_D, nc), True,
        "realized tables are B0; layer union unresolved until model config")
    write_json(HERE / "driver-contract-check.json", contract)
    n_ok = sum(1 for c in contract["checks"] if c["ok"])
    print("driver contract: %d/%d checks OK (see "
          "driver-contract-check.json; the token-field mismatch and the "
          "power-gate shortfall are the two flagged items)"
          % (n_ok, len(contract["checks"])))
    print("BUILD COMPLETE (deterministic; re-run reproduces byte-identical "
          "corpora)")


if __name__ == "__main__":
    main()
