#!/usr/bin/env python3
"""nsk1_runner — two-stage harness for nsk1 (DRAFT registry/experiments/nsk1.json;
design docs/design-neurosym-kernel-internals.md).

Stage 0 (instrument gate, B5): back-patch diagnostic on kernel-covered 2-hop
failure slices — fraction of text-only failures rescuable by moving a
later-layer hidden state to an earlier layer. A pre-declared rescuable-fraction
floor is the FAMILY-LEVEL CHEAP KILL: below it, Stage 1 does not run.

Stage 1 (decisive): training-free forward-hook loop at the Stage-0-chosen layer:
  patchscope-decode hidden state -> EXACT lexicon match (X3: no kernel-space
  cosine/kNN anywhere) -> kot-axiom/1 engine resolves HOP-1 ONLY (never the
  2-hop gold; f2b oracle-leakage lesson) -> write-back via the kernel-keyed
  cached steering channel (B2). Compared against the STRONGEST matched
  baseline: the SAME engine hop-1 feedback rendered as text via an external
  F2-topology loop at matched token budget.

Arms (Stage 1):
  internal       kernel-keyed cached steering write-back (treatment)
  external-text  same engine feedback as appended text, matched budget (PRIMARY comparator)
  text-only      no feedback, no hook
  kernel-as-text static kernel/world records as text, no engine resolution
  shuffled       internal with seed-pinned DERANGED entity->vector map
  random-dir     random steering vector at matched norm
  noop-hook      hook installed, zero vector (prices plumbing)

Modes:
  --mock   $0, CPU-only, no model download. A deterministic MockHost stands in
           for the LLM; the ENGINE, the exact-match mapper, the steering-cache
           keying, the derangement, the budget ledger, the logging schema and
           the analysis pipeline are all REAL and exercised end-to-end.
           Mock accuracies are FAKE mechanism-check numbers, never evidence.
  real     GPU-gated (Tier 2). REFUSES to run unless NSK1_RUN_AUTHORIZED=1 and
           the record is FROZEN — this harness is design-stage; the final
           campaign belongs to the runner role, never the designer (run!=audit).

Corpora (--data, default data/nsk1-eval): any corpus in the nsk1 harness format
(items.jsonl / world.jsonl / axioms/ / lexicon.json). CLUTRR-derived corpora
(data/nsk1-clutrr, built per design section 5.1) additionally carry a per-item
"lexicon" field (the item's closed name lexicon - the read-channel match set) and
null hop1 on third-party uncovered controls; both are supported here so the build's
mock gate (section 5.1 S10) runs this same harness unchanged.

Zero deps beyond the stdlib in mock mode. Usage:
  python3 poc/nsk1/nsk1_runner.py --mock [--data data/nsk1-eval] [--out poc/nsk1/out/mock]
"""
import argparse
import hashlib
import json
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "axiom"))
from kot_axiom import Engine  # noqa: E402

DATA_DEFAULT = os.path.join(ROOT, "data", "nsk1-eval")
ARMS = ["internal", "external-text", "text-only", "kernel-as-text",
        "shuffled", "random-dir", "noop-hook"]
# Pre-declared mock behaviour profile (mechanics only — obviously fake):
MOCK_P = {"internal": 0.62, "external-text": 0.55, "text-only": 0.25,
          "kernel-as-text": 0.30, "shuffled": 0.27, "random-dir": 0.26,
          "noop-hook": 0.25}
MOCK_PATCHSCOPE_OK = 0.85    # extraction success prob in mock
MOCK_RESCUE = 0.35           # stage-0 per-failure rescue prob in mock
FEEDBACK_TOKEN_BUDGET = 24   # matched extra-token budget both loop arms honour
STAGE0_PATCH_GRID = [(20, 8), (24, 8), (24, 12), (28, 12), (28, 16), (16, 4)]


def load_inputs(data_dir):
    ax = []
    axdir = os.path.join(data_dir, "axioms")
    corpus = os.path.basename(os.path.normpath(data_dir))
    for n in sorted(os.listdir(axdir)):
        if n.endswith(".json"):
            with open(os.path.join(axdir, n)) as f:
                ax.append(("%s/axioms/%s" % (corpus, n), json.load(f)))
    with open(os.path.join(data_dir, "world.jsonl")) as f:
        world = [json.loads(l) for l in f if l.strip()]
    with open(os.path.join(data_dir, "items.jsonl")) as f:
        items = [json.loads(l) for l in f if l.strip()]
    with open(os.path.join(data_dir, "lexicon.json")) as f:
        lex = json.load(f)
    return Engine(ax, world), items, lex


class ExactMapper(object):
    """EXACT surface-form -> entity URN match over a closed lexicon
    ({urn: surface}). Abstains (returns None) on anything else. No similarity,
    no kNN — X3. Corpus-global for nsk1-eval (unique surfaces); PER-ITEM for
    CLUTRR-derived corpora (items carry their own closed name lexicon —
    design section 4.3/5.1 S8)."""

    def __init__(self, entities):
        self.by_surface = {v: k for k, v in entities.items()}
        if len(self.by_surface) != len(entities):
            raise RuntimeError("lexicon surface forms not unique")

    def match(self, text):
        return self.by_surface.get(text.strip())


def item_lexicon(it, lex):
    """The item's closed name lexicon if it carries one, else the corpus-global
    entity lexicon."""
    return it.get("lexicon") or lex.get("entities") or {}


class SteeringCache(object):
    """Kernel-keyed cached steering dictionary (B2 shape, mock geometry).

    Keys are EXACT world-entity URNs (stratum-4 record identities); values are
    model-native vectors. In real mode the value is extracted ONCE per
    (model, entity) by contrastive activation arithmetic over the model's OWN
    activations on carrier prompts (function-vector recipe) — kernel/encoder
    coordinates NEVER enter the model (Law 1). In mock mode the vector is a
    deterministic hash stub with the same addressing + arithmetic surface."""

    DIM = 16

    def __init__(self, entity_urns, seed, deranged=False):
        self.vec = {}
        for u in sorted(entity_urns):
            h = hashlib.sha256(("nsk1-steer|%d|%s" % (seed, u)).encode()).digest()
            self.vec[u] = [((b / 255.0) * 2 - 1) for b in h[:self.DIM]]
        self.key_map = {u: u for u in self.vec}
        if deranged:
            urns = sorted(self.vec)
            rot = urns[1:] + urns[:1]          # seed-pinned derangement (rotation)
            self.key_map = dict(zip(urns, rot))

    def lookup(self, urn):
        mapped = self.key_map.get(urn)
        return None if mapped is None else self.vec[mapped]


class MockHost(object):
    """Deterministic stand-in for the LLM. Every 'behaviour' is a pure function
    of (seed, item, arm) — reproducible, honest about being fake."""

    N_LAYERS = 30
    DIM = SteeringCache.DIM

    def __init__(self, seed):
        self.seed = seed

    def _u(self, *parts):
        h = hashlib.sha256(("|".join(str(p) for p in parts)).encode("utf-8"))
        return int.from_bytes(h.digest()[:8], "big") / 2.0 ** 64

    def hidden_state(self, item_id, layer):
        h = hashlib.sha256(("h|%d|%s|%d" % (self.seed, item_id, layer)).encode()).digest()
        return [((b / 255.0) * 2 - 1) for b in h[:self.DIM]]

    def patchscope_decode(self, item, layer):
        """Mock read channel: returns the bridge surface form on 'success',
        an out-of-lexicon string otherwise. Controls have no bridge -> always
        out-of-lexicon (the loop must abstain)."""
        if item["hop1_bridge"] is None:
            return "the librarian"
        ok = self._u("ps", self.seed, item["item_id"], layer) < MOCK_PATCHSCOPE_OK
        if not ok:
            return "somebody unclear"
        # surface of the bridge entity (what a good patchscope readout yields)
        return item["_bridge_surface"]

    def answer(self, item, arm, steer_vec=None):
        """Mock generation. steer_vec participates so the write-back arithmetic
        path is exercised; correctness is drawn from the arm profile."""
        base = MOCK_P[arm]
        if arm in ("internal", "shuffled", "random-dir") and steer_vec is None:
            base = MOCK_P["text-only"]      # loop failed to fire -> baseline
        correct = self._u("ans", self.seed, item["item_id"], arm) < base
        if item["gold_surface"] is None:
            return "I don't know", False
        return (item["gold_surface"] if correct else "Wrong Person"), correct

    def backpatch_rescues(self, item_id, src, tgt):
        return self._u("bp", self.seed, item_id, src, tgt) < (
            MOCK_RESCUE / len(STAGE0_PATCH_GRID) * 2.2)


def run_stage0(host, items, rows, rung):
    covered = [i for i in items if i["stratum"] == "covered"]
    failures = []
    for it in covered:
        _, correct = host.answer(it, "text-only")
        rows.append({"phase": "mock", "stage": 0, "rung": rung, "arm": "text-only",
                     "item_id": it["item_id"], "correct": bool(correct)})
        if not correct:
            failures.append(it)
    cap = failures[:300]                     # pre-declared sweep cap
    for it in cap:
        rescued = any(host.backpatch_rescues(it["item_id"], s, t)
                      for (s, t) in STAGE0_PATCH_GRID)
        rows.append({"phase": "mock", "stage": 0, "rung": rung,
                     "arm": "backpatch-sweep", "item_id": it["item_id"],
                     "rescued": bool(rescued)})
    return len(failures), len(cap)


def run_stage1(host, engine, mapper_global, items, lex, rows, rung, seed):
    # steering-cache universe = corpus-global entities plus every per-item lexicon
    ent_urns = set(lex.get("entities") or {})
    for it in items:
        ent_urns.update(it.get("lexicon") or {})
    ent_urns = sorted(ent_urns)
    cache_true = SteeringCache(ent_urns, seed)
    cache_shuf = SteeringCache(ent_urns, seed, deranged=True)
    rng_rand = random.Random(seed + 7)
    layer = 12   # mock stand-in for the Stage-0-selected layer L*

    for it in items:
        ilex = item_lexicon(it, lex)
        if not ilex:
            raise RuntimeError("item %s has no lexicon (neither per-item nor "
                               "corpus-global)" % it.get("item_id"))
        mapper = ExactMapper(ilex) if it.get("lexicon") else mapper_global
        # bridge surface available to the mock read channel
        it["_bridge_surface"] = (ilex.get(it["hop1_bridge"])
                                 if it["hop1_bridge"] else None)
        for arm in ARMS:
            fired, abstained, extraction_ok = False, False, True
            steer, extra_tokens = None, 0
            if arm in ("internal", "shuffled", "random-dir", "noop-hook",
                       "external-text"):
                decoded = host.patchscope_decode(it, layer)
                urn = mapper.match(decoded)          # EXACT match or None (X3)
                if urn is None:
                    abstained = True
                    extraction_ok = it["hop1_bridge"] is None  # controls: correct abstain
                elif it.get("hop1"):
                    q = dict(it["hop1"])
                    res = engine.query(q)            # REAL engine, hop-1 only
                    if res["status"] == "answer":
                        fired = True
                        bridge_urn = res["value"]
                        if arm == "internal":
                            steer = cache_true.lookup(bridge_urn)
                        elif arm == "shuffled":
                            steer = cache_shuf.lookup(bridge_urn)
                        elif arm == "random-dir":
                            v = cache_true.lookup(bridge_urn)
                            norm = sum(x * x for x in v) ** 0.5
                            r = [rng_rand.uniform(-1, 1) for _ in v]
                            rn = sum(x * x for x in r) ** 0.5 or 1.0
                            steer = [x / rn * norm for x in r]
                        elif arm == "noop-hook":
                            steer = [0.0] * SteeringCache.DIM
                        elif arm == "external-text":
                            fb = "Note: the %s of %s is %s." % (
                                REL_SURF(it), ilex[it["hop1"]["subject"]],
                                ilex[bridge_urn])
                            extra_tokens = len(fb.split())
                            if extra_tokens > FEEDBACK_TOKEN_BUDGET:
                                raise RuntimeError("budget breach")
                # else: a matched name but NO licensed query exists (third-party
                # uncovered control, null hop1): the loop no-ops; fired stays
                # False and feeds the false-fire gate.
                # write-back arithmetic (exercised even though host is mock)
                if steer is not None:
                    h = host.hidden_state(it["item_id"], layer)
                    _ = [a + 4.0 * b for a, b in zip(h, steer)]   # alpha=4 mock
            if arm in ("internal", "shuffled", "random-dir", "noop-hook"):
                extra_tokens = 8      # patchscope side-decode budget (mock ledger)
            _, correct = host.answer(it, arm, steer)
            rows.append({"phase": "mock", "stage": 1, "rung": rung, "arm": arm,
                         "item_id": it["item_id"], "stratum": it["stratum"],
                         "correct": bool(correct), "fired": fired,
                         "abstained": abstained, "extraction_ok": extraction_ok,
                         "extra_tokens": extra_tokens})


def REL_SURF(it):
    return {"forward": {"urn:kot:bciqdkz3mwjzgrbptwmryvvp5nwg7fuu6crj5e63i5y5cdkq4v2r6mua": "mother",
                        "urn:kot:bciqgs7ze663hfdaq7be4jnuuue5nywum6qhdciqgq7greuyyobz6jqi": "father"}}[
        it["hop1"]["direction"]][it["hop1"]["rel"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--data", default=DATA_DEFAULT,
                    help="corpus root in the nsk1 harness format "
                         "(default data/nsk1-eval; the CLUTRR-derived corpus "
                         "data/nsk1-clutrr once built per design section 5.1)")
    ap.add_argument("--out", default=os.path.join(HERE, "out", "mock"))
    args = ap.parse_args()

    if not args.mock:
        if os.environ.get("NSK1_RUN_AUTHORIZED") != "1":
            print("ERR_NSK1_GPU_GATED: real mode is Tier-2 GPU-gated and "
                  "freeze-gated; this harness runs --mock only at design stage.")
            return 2
        print("real mode not implemented in the design-stage harness "
              "(runner role implements HFHost against the frozen record)")
        return 2

    os.makedirs(args.out, exist_ok=True)
    engine, items, lex = load_inputs(args.data)
    mapper_global = (ExactMapper(lex["entities"])
                     if lex.get("entities") else None)
    host = MockHost(args.seed)
    rows = []
    rung = "R0-mock"

    n_fail, n_swept = run_stage0(host, items, rows, rung)
    run_stage1(host, engine, mapper_global, items, lex, rows, rung, args.seed)

    rows_path = os.path.join(args.out, "rows.jsonl")
    with open(rows_path, "w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    print("mock: %d rows (%d stage-0 failures, %d swept)" %
          (len(rows), n_fail, n_swept))

    # analysis is the pinned script — run it exactly as the verdict would
    out_json = os.path.join(args.out, "analysis.json")
    rc = subprocess.call([sys.executable, os.path.join(ROOT, "analysis", "nsk1.py"),
                          "--rows", rows_path, "--out", out_json])
    if rc != 0:
        print("MOCK RED: analysis failed")
        return 1
    with open(out_json) as f:
        a = json.load(f)
    required = ["/gates/instrument_valid", "/gates/stage0_rescuable_wilson_lb",
                "/analysis/delta_primary", "/analysis/delta_primary_bca_lb",
                "/analysis/delta_primary_bca_ub", "/analysis/tost_equivalent",
                "/analysis/spec_delta_abs_lb", "/analysis/falsefire_wilson_ub"]
    flat = flatten(a)
    missing = [k for k in required if k not in flat]
    if missing:
        print("MOCK RED: missing fields %s" % missing)
        return 1
    print("MOCK GREEN: all pinned endpoint fields present and decidable")
    for k in required:
        print("  %s = %s" % (k, flat[k]))
    return 0


def flatten(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(flatten(v, prefix + "/" + k))
    else:
        out[prefix] = obj
    return out


if __name__ == "__main__":
    sys.exit(main())
