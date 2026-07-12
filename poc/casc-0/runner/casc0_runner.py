#!/usr/bin/env python3
"""CASC-0' runner — the STATIC-CASE / M2-isolator factorial probe
(registry/experiments/casc-0.json, DRAFT at authoring; design source
docs/next/arch/cascade-synthesis.md section 3; prereg doc
poc/casc-0/design.md).

ADAPTED FROM poc/f2b-transfer/runner/f2bt_runner.py per the record's
runner_constraints.harness. poc/f2b and poc/f2b-transfer are left
BYTE-IDENTICAL to their pins — this is a new module. Carried over with
byte-identical semantics: the CellGuard safety instrument, the Emitter
(append+flush), the F0 FlopMeter, the HF forced-choice logprob backend, the
det_u/sha256 pin discipline. New here is exactly what the design mandates:
the three-medium rendering, the step-grain intermediate-claim verifier, the
TTC cost-matched deflator, and the deranged-closure house control.

WHY THIS EXPERIMENT EXISTS (maintainer issue-#15 follow-up, the static
case): f2b-transfer measured a real +0.2507 external-gold verifier-offload
lift for a 135M host over an ALIGNED AUTHORED store, and simultaneously
FAILED noninferiority vs the 1.7B host (pending audit). DECONF-A1 certified
the kernel's runtime structure INERT at the checker. The open question M2:
does a structured canonical medium (the kernel's authored content,
naturalised INTO the model's input) let a SMALLER reasoner close on a larger
one — a positive size x medium interaction — or is any lift just purchased
compute / verifier-against-answer-key? This factorial isolates that sign.

FACTORS (cells; all paired on the same 300-item engine-derivable eval set):
  size      R2 (SmolLM2-360M) x R3 (SmolLM2-1.7B)      [sign, not slope]
  medium    nl (naturalised prose, content-matched)
            gloss (raw-kernel Option-A structured gloss)
            plain (distilled knull-grade typed dialect)
  verifier  off | on (structured mediums ONLY — NL has no IR-hard islands)
plus: ttc-deflator (R2/nl + self-consistency, cost-matched to the FIXED
reference cell R2/gloss/verifier-on — the K2' purchased-compute kill) and
deranged-control (R2/gloss/verifier-on against a Sattolo-deranged closure;
reported-only house control).

ANTI-ORACLE RULE (PROPOSED-ASM-1144): the verifier checks the model's
ASSERTED INTERMEDIATE cumulative relations against the engine closure and
NEVER the final answer — a verifier that checked the final hop against the
engine-derivable gold would manufacture an oracle-structured win (the exact
defect that killed CASC-0; cascade-synthesis section 1.2).

Usage:
  python3 casc0_runner.py --out-dir /tmp/casc0 --device cuda   # real (Modal)
  python3 casc0_runner.py --out-dir /tmp/casc0 --mock          # stub LM, $0
  python3 casc0_runner.py --out-dir /tmp/casc0 --dry-plan      # cost plan

HARD RULES: --mock and --dry-plan spend $0 and never touch a GPU or the
network; mock numbers are labelled MOCK end-to-end and are never
measurements; real runs fail closed on any missing/mismatched pin (ERR_*).
RAW metrics only — the verdict belongs to the pinned analysis/casc_0.py +
tools/registry/verdict-gen.py under run-vs-audit separation. Every verdict
sentence downstream carries the SELF-AUTHORED / kernel-STYLE /
engine-derived-gold rider (kernel-STYLE per the executed ASM-1158 mapping,
poc/casc-0/kernel-coverage.md).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

# F0 flop-meter — shared poc/f0/ package (the f0-harness dependency).
_POC_DIR = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", ".."))
if _POC_DIR not in sys.path:
    sys.path.insert(0, _POC_DIR)
from f0 import FlopMeter  # noqa: E402

# ---------------------------------------------------------------------------
# Constants — names MUST equal analysis/casc_0.py + the registry IV levels
# ---------------------------------------------------------------------------
ARM_FACT = "factorial"
ARM_TTC = "ttc-deflator"
ARM_DER = "deranged-control"
RUNGS = ("R2", "R3")
MEDIUMS = ("nl", "gloss", "plain")
STRUCTURED = ("gloss", "plain")

SEED_BASE = 20260711  # published fixed base seed (== the casc-0 SAP PRNG seed)

# SAFETY BOUNDS (f2b-replicate correction 1, carried over unchanged).
# Structural per-item max generations: depth-4 verifier-on = 3 queries x
# (k+1)=3 attempts = 9; TTC = 3 queries x N<=9 = 27 -> cap 32.
MAX_GEN_PER_ITEM_DEFAULT = 32
CELL_TIMEOUT_S_DEFAULT = {"A100": 5400.0, "A10G": 5400.0, "T4": 10800.0}


class CellBudgetExceeded(Exception):
    def __init__(self, kind, cell, item_id, elapsed_s, n_gen):
        super().__init__("%s in cell %s at item %r after %.1fs (%d generations)"
                         % (kind, cell, item_id, elapsed_s, n_gen))
        self.kind, self.cell, self.item_id = kind, cell, item_id
        self.elapsed_s, self.n_gen = elapsed_s, n_gen


class CellGuard:
    """Per-cell safety instrument (verbatim semantics from poc/f2b-transfer):
    wall-clock timeout + max-generations-per-item cap; a breach becomes a
    flushed exit:"timeout" record, never a hang, never data."""

    def __init__(self, cell, timeout_s, max_gen_per_item):
        self.cell = cell
        self.timeout_s = float(timeout_s)
        self.max_gen = int(max_gen_per_item)
        self.t0 = time.monotonic()
        self.item_id = None
        self.n_gen = 0

    def elapsed(self):
        return time.monotonic() - self.t0

    def _wall(self):
        el = self.elapsed()
        if el > self.timeout_s:
            raise CellBudgetExceeded("wall-clock timeout (%.0fs)" % self.timeout_s,
                                     self.cell, self.item_id, el, self.n_gen)

    def start_item(self, item):
        self.item_id = item.get("id")
        self.n_gen = 0
        self._wall()

    def gen(self):
        self.n_gen += 1
        if self.n_gen > self.max_gen:
            raise CellBudgetExceeded("max-generations-per-item cap (%d)" % self.max_gen,
                                     self.cell, self.item_id, self.elapsed(), self.n_gen)
        self._wall()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def corpus_kot_hash(base):
    """kot-corpus-hash/1 digest (recipe verbatim from tools/registry/
    kot_common.py CORPUS_RECIPE; reimplemented — the staged container has no
    tools/ tree)."""
    lines = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames.sort()
        for name in filenames:
            full = os.path.join(dirpath, name)
            if os.path.islink(full) or not os.path.isfile(full):
                continue
            rel = os.path.relpath(full, base).replace(os.sep, "/")
            lines.append((rel.encode("utf-8"), sha256_file(full)))
    if not lines:
        raise SystemExit("ERR_P2_CORPUS_PIN: %s contains no regular files" % base)
    lines.sort(key=lambda t: t[0])
    payload = b"".join(d.encode("ascii") + b"  " + r + b"\n" for r, d in lines)
    return hashlib.sha256(payload).hexdigest()


def utcnow():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def det_u(*keys):
    raw = "\x1f".join(str(k) for k in keys)
    h = hashlib.sha256(raw.encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big") / 2.0 ** 64


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# ---------------------------------------------------------------------------
# The ENGINE — deterministic derivation from the authored store (the aligned
# authored answer-key analogue). CPU-only; REAL code in mock and full.
# ---------------------------------------------------------------------------
class Engine:
    def __init__(self, table, derange_map=None):
        self.compose = {tuple(k.split("|")): v for k, v in table["compose"].items()}
        self.surface = {k: tuple(v) for k, v in table["surface"].items()}
        self.atomic = list(table["atomic"])
        self.derange = derange_map  # rel_core -> rel_core, or None

    def closure(self, item):
        """Cumulative states rel(X0,Xt) for t=1..d from the item's FACTS (the
        store), NOT from the committed states_core. Returns None where the
        (possibly deranged) fold is undefined."""
        rels = [(self.derange[f["rel_core"]] if self.derange else f["rel_core"])
                for f in item["facts"]]
        states = [rels[0]]
        for r in rels[1:]:
            prev = states[-1]
            nxt = self.compose.get((prev, r)) if prev is not None else None
            states.append(nxt)
        return states

    def surface_of(self, core, gender):
        return self.surface[core][0 if gender == "F" else 1]

    def core_of_surface(self, text, gender):
        for core, (f, m) in self.surface.items():
            if (f if gender == "F" else m) == text:
                return core
        return None

    def check_intermediate(self, item, t, asserted_key):
        """Verify the asserted cumulative relation rel(X0,Xt) (t is 1-based
        state index, 2 <= t <= depth-1) against the closure.
        Returns (decidable, consistent). NEVER called on the final state
        (anti-oracle rule, PROPOSED-ASM-1144)."""
        if t >= item["depth"]:
            raise SystemExit("ERR_ORACLE_CHECK: verifier asked to check the "
                             "final relation of %s — forbidden by design" % item["id"])
        t0 = time.perf_counter()
        states = self.closure(item)
        derived = states[t - 1]
        self.last_cpu_s = time.perf_counter() - t0
        if derived is None:
            return False, False  # deranged fold undefined -> abstain
        g0 = item["entities"][0]["gender"]
        text = {o["key"]: o["text"] for o in item["options_final"]}.get(asserted_key)
        if text is None:
            return False, False
        core = self.core_of_surface(text, g0)
        return True, core == derived


def assert_engine_gold(engine, items):
    """Fail-closed: the committed states_core must equal the engine's own
    derivation from facts + composition table (ERR_ENGINE_GOLD), and the
    committed answer key must be the derived final relation's surface."""
    for it in items:
        states = engine.closure(it)
        if states != it["states_core"] or states[-1] is None:
            raise SystemExit("ERR_ENGINE_GOLD: %s states_core %r != engine "
                             "derivation %r" % (it["id"], it["states_core"], states))
        g0 = it["entities"][0]["gender"]
        want = engine.surface_of(states[-1], g0)
        by_key = {o["key"]: o["text"] for o in it["options_final"]}
        if by_key.get(it["answer"]) != want or it["gold_surface"] != want:
            raise SystemExit("ERR_ENGINE_GOLD: %s answer surface mismatch" % it["id"])


def make_derange_map(engine, perm_seed):
    """Sattolo cyclic permutation over the sorted ATOMIC relation types — a
    derangement by construction (map recorded; deranged-control arm only)."""
    import random
    atoms = sorted(engine.atomic)
    shuffled = list(atoms)
    rng = random.Random(perm_seed)
    for i in range(len(shuffled) - 1, 0, -1):
        j = rng.randrange(i)
        shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
    perm = dict(zip(atoms, shuffled))
    if any(u == v for u, v in perm.items()):
        raise SystemExit("ERR_SHUFFLE: fixed point in derangement (bug)")
    blob = json.dumps(perm, sort_keys=True, separators=(",", ":")).encode()
    return perm, hashlib.sha256(blob).hexdigest()


# ---------------------------------------------------------------------------
# Medium rendering — the FACTOR under test. Templates pinned in the manifest;
# identical protocol, identical content, identical answer surface per item.
# ---------------------------------------------------------------------------
class Renderer:
    def __init__(self, frames, medium):
        self.f = frames[medium]
        self.shared = frames["shared"]
        self.medium = medium

    def _frame(self, name, key):
        """A frame entry is either a single template string or a dict keyed
        by rel_surface (per-relation explicator-authored variants — the
        ASM-1158 pre-freeze gloss upgrade; avoids set-level template
        monotony). Fail closed on a missing key: no silent fallbacks."""
        entry = self.f[name]
        if isinstance(entry, dict):
            if key not in entry:
                raise SystemExit("ERR_FRAME: medium %r has no %s entry for "
                                 "surface %r" % (self.medium, name, key))
            return entry[key]
        return entry

    def _fact(self, fact, gender_by_urn):
        g = gender_by_urn[fact["subj_urn"]]
        return self._frame("fact_line", fact["rel_surface"]).format(
            subj=fact["subj_label"], obj=fact["obj_label"],
            rel_surface=fact["rel_surface"], rel_core=fact["rel_core"],
            rel_core_upper=fact["rel_core"].upper(),
            subj_urn=fact["subj_urn"], obj_urn=fact["obj_urn"],
            gender_word="female" if g == "F" else "male",
            gender_atom="female" if g == "F" else "male")

    def _claim(self, item, t, surface):
        return self._frame("claim_line", surface).format(
            subj=item["question_subj"], obj=item["entities"][t]["label"],
            rel_surface=surface,
            rel_core=surface)  # claim lines carry the asserted SURFACE form

    def context(self, item, asserted):
        gender_by_urn = {e["urn"]: e["gender"] for e in item["entities"]}
        parts = [self._fact(f, gender_by_urn) for f in item["facts"]]
        for t, surface in asserted:
            parts.append(self._claim(item, t, surface))
        return "".join(parts)

    def question(self, item, t=None):
        tmpl = self.f["final_question" if t is None else "intermediate_question"]
        obj = (item["question_obj"] if t is None
               else item["entities"][t]["label"])
        return tmpl.format(subj=item["question_subj"], obj=obj)

    def options_block(self, item):
        lines = [self.shared["option_line"].format(key=o["key"], text=o["text"])
                 for o in item["options_final"]]
        return "\n" + "\n".join(lines) + self.shared["answer_cue"]

    def exemplar_block(self, ex):
        return (self.context(ex, []) + self.question(ex)
                + self.options_block(ex).rstrip()
                + self.shared["exemplar_answer"].format(key=ex["answer"]))

    def prompt(self, exemplars, item, asserted, t=None):
        parts = [self.f["qa_prefix"]]
        for ex in exemplars:
            parts.append(self.exemplar_block(ex))
        parts.append(self.context(item, asserted))
        parts.append(self.question(item, t))
        parts.append(self.options_block(item))
        return "".join(parts)


# ---------------------------------------------------------------------------
# LM backends — one interface, two implementations (HFLM carried from
# poc/f2b-transfer; forced-choice sequence-logprob, the IF-C surface).
# ---------------------------------------------------------------------------
class StubLM:
    """SYNTHETIC mechanics-only stand-in (mock mode; no torch). The planted
    skill surface (base + medium bonus + verifier bonus, larger at R2) exists
    ONLY so the analysis contract's gates and contrasts resolve during mock
    validation. Never a measurement."""

    def __init__(self, rung, mock_spec):
        self.rung = rung
        self.spec = mock_spec
        dims = mock_spec["stub_dims"][rung]
        self.n_active = dims["n_active"]
        self.layers = dims["layers"]
        self.d_attn = dims["d_attn"]
        self.name = "stub-%s" % rung
        self.weight_bytes = int(self.n_active * 2)
        self.cell_medium = "nl"
        self.cell_verifier_bonus = False

    def count_tokens(self, text):
        return max(1, len(text.split()))

    def _p(self, intermediate):
        if intermediate:
            return self.spec["stub_intermediate_skill"]
        p = (self.spec["stub_skill"][self.rung]
             + self.spec["stub_medium_bonus"][self.cell_medium][self.rung])
        if self.cell_verifier_bonus:
            p += self.spec["stub_verifier_bonus"][self.rung]
        return min(0.98, p)

    def choose(self, item, keys, gold, seed, attempt, prompt="", tag="f"):
        p = self._p(intermediate=(tag != "f"))
        u = det_u("ans", self.name, self.cell_medium, item["id"], tag, seed, attempt)
        if u < p:
            return gold, 1.0
        wrong = [k for k in keys if k != gold]
        return wrong[int(det_u("wr", self.name, item["id"], tag, seed, attempt)
                        * len(wrong))], 0.0


class HFLM:
    """Real path: SmolLM2 at the PINNED revision, forced-choice logprob
    scoring. Never touched by --mock. Carried from poc/f2b-transfer
    (SEED_BASE differs by design: this experiment's published seed)."""

    def __init__(self, repo, revision, device):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        if not revision:
            raise SystemExit("ERR_UNPINNED_MODEL: %s has no pinned revision" % repo)
        self.tok = AutoTokenizer.from_pretrained(repo, revision=revision)
        self.model = AutoModelForCausalLM.from_pretrained(
            repo, revision=revision, torch_dtype=torch.float16)
        self.model.to(device)
        self.model.eval()
        for p in self.model.parameters():
            p.requires_grad_(False)
        self.device = device
        self.torch = torch
        self.name = "%s@%s" % (repo, revision[:8])
        cfg = self.model.config
        self.n_active = sum(p.numel() for p in self.model.parameters())
        self.layers = cfg.num_hidden_layers
        self.d_attn = cfg.hidden_size
        self.weight_bytes = int(self.n_active * 2)

    def count_tokens(self, text):
        return len(self.tok.encode(text, add_special_tokens=False))

    def _option_logprobs(self, prompt, options):
        torch = self.torch
        pre = self.tok.encode(prompt, add_special_tokens=False)
        outs = []
        with torch.no_grad():
            for opt in options:
                oids = self.tok.encode(opt, add_special_tokens=False)
                ids = torch.tensor([pre + oids], device=self.device)
                logits = self.model(ids).logits[0]
                lp = torch.log_softmax(logits[:-1].float(), dim=-1)
                tgt = ids[0, 1:]
                start = len(pre) - 1
                outs.append(float(lp[start:, :].gather(1, tgt[start:, None]).sum()))
        return outs

    def choose(self, item, keys, gold, seed, attempt, prompt="", tag="f"):
        lps = self._option_logprobs(prompt, [" %s" % k for k in keys])
        if attempt == 0:
            i = max(range(len(keys)), key=lambda j: lps[j])
        else:
            torch = self.torch
            g = torch.Generator().manual_seed(
                (SEED_BASE * 100000 + seed * 1000 + attempt * 10
                 + (0 if tag == "f" else int(tag[1:]) + 1)) % (2 ** 31))
            probs = torch.softmax(torch.tensor(lps), dim=0)
            i = int(torch.multinomial(probs, 1, generator=g))
        return keys[i], lps[i]


# ---------------------------------------------------------------------------
# Item protocol — IDENTICAL in every cell; cells differ only in (size,
# medium, verifier). Returns (final_key, asserted_list, gen_count).
# ---------------------------------------------------------------------------
def item_keys(item):
    return [o["key"] for o in item["options_final"]]


def gold_key_for_state(engine, item, t):
    g0 = item["entities"][0]["gender"]
    text = engine.surface_of(item["states_core"][t - 1], g0)
    return next(o["key"] for o in item["options_final"] if o["text"] == text)


def run_item_once(lm, rend, exemplars, item, engine_gold, seed, attempt,
                  meter, guard):
    """One full attempt: assert each intermediate (t = 2..depth-1), then the
    final. Asserted claims are appended to the context in the CELL'S OWN
    medium. Verification (if any) is the CALLER's job — this function never
    sees a verifier."""
    keys = item_keys(item)
    by_key = {o["key"]: o["text"] for o in item["options_final"]}
    asserted = []   # [(t, surface_text)]
    picks = []      # [(t_or_None, key)]
    for t in range(2, item["depth"]):
        prompt = rend.prompt(exemplars, item, asserted, t=t)
        gold = engine_gold(item, t)
        t0 = time.perf_counter()
        key, _c = lm.choose(item, keys, gold, seed, attempt, prompt=prompt,
                            tag="i%d" % t)
        guard.gen()
        meter.seq(lm, lm.count_tokens(prompt) * len(keys)
                  + sum(lm.count_tokens(" %s" % k) for k in keys))
        meter.query_done(time.perf_counter() - t0)
        asserted.append((t, by_key[key]))
        picks.append((t, key))
    prompt = rend.prompt(exemplars, item, asserted, t=None)
    t0 = time.perf_counter()
    key, _c = lm.choose(item, keys, item["answer"], seed, attempt,
                        prompt=prompt, tag="f")
    guard.gen()
    meter.seq(lm, lm.count_tokens(prompt) * len(keys)
              + sum(lm.count_tokens(" %s" % k) for k in keys))
    meter.query_done(time.perf_counter() - t0)
    picks.append((None, key))
    return key, picks


def run_cell_plain(lm, rend, exemplars, items, engine, seed, meter, guard):
    """Verifier-OFF cell (k=0): one attempt per item."""
    gold_fn = lambda it, t: gold_key_for_state(engine, it, t)
    finals = []
    for it in items:
        guard.start_item(it)
        final, _p = run_item_once(lm, rend, exemplars, it, gold_fn, seed, 0,
                                  meter, guard)
        finals.append(final)
    return finals


def run_cell_verify(lm, rend, exemplars, items, engine, verifier, k, seed,
                    meter, guard):
    """Verifier-ON cell: check each asserted INTERMEDIATE against the
    closure; ANY rejection => reject the attempt => resample the whole item
    (fresh per-attempt sampling), max k retries; final answer = last attempt
    (pre-declared). The FINAL relation is NEVER checked (anti-oracle,
    PROPOSED-ASM-1144). Emits the RT-7a engagement block."""
    gold_fn = lambda it, t: gold_key_for_state(engine, it, t)
    finals = []
    eng = {"n_items": 0, "n_decidable": 0, "n_attempt0_rejected": 0,
           "n_final_differs_attempt0": 0}
    for it in items:
        guard.start_item(it)
        eng["n_items"] += 1
        final = final0 = None
        for attempt in range(k + 1):
            final, picks = run_item_once(lm, rend, exemplars, it, gold_fn,
                                         seed, attempt, meter, guard)
            if attempt == 0:
                final0 = final
            rejected = False
            any_decidable = False
            for t, key in picks:
                if t is None:
                    continue  # the final relation is never checked
                decidable, consistent = verifier.check_intermediate(it, t, key)
                meter.verifier(getattr(verifier, "last_cpu_s", 0.0))
                if decidable:
                    any_decidable = True
                    if not consistent:
                        rejected = True
            if attempt == 0:
                if any_decidable:
                    eng["n_decidable"] += 1
                    if rejected:
                        eng["n_attempt0_rejected"] += 1
            if not rejected:
                break  # accepted (or nothing decidable)
        if final != final0:
            eng["n_final_differs_attempt0"] += 1
        finals.append(final)
    return finals, eng


def run_cell_ttc(lm, rend, exemplars, items, engine, n_samples, seed, meter,
                 guard):
    """TTC deflator (K2' instrument): R2/nl + self-consistency majority vote
    over n_samples fresh full-protocol samples (temperature-1 analogue via
    the seeded resample path); ties broken by pinned option order."""
    gold_fn = lambda it, t: gold_key_for_state(engine, it, t)
    finals = []
    for it in items:
        guard.start_item(it)
        votes = {}
        for s in range(n_samples):
            # sample index rides the attempt slot (attempt>0 => sampling path)
            final, _p = run_item_once(lm, rend, exemplars, it, gold_fn, seed,
                                      s + 1, meter, guard)
            votes[final] = votes.get(final, 0) + 1
        order = {o["key"]: i for i, o in enumerate(it["options_final"])}
        finals.append(max(votes, key=lambda k: (votes[k], -order[k])))
    return finals


def score(items, finals):
    return [1 if a == it["answer"] else 0 for it, a in zip(items, finals)]


# ---------------------------------------------------------------------------
# Emitter — kot-log/1 record BODIES (verbatim from poc/f2b-transfer:
# append + flush at emit time).
# ---------------------------------------------------------------------------
class Emitter:
    def __init__(self, out_dir, mock):
        self.records = []
        self.path = os.path.join(
            out_dir, "run-records-casc0%s.jsonl" % ("-mock" if mock else ""))
        self.phase = "mock" if mock else "final"
        with open(self.path, "w"):
            pass

    def emit(self, arm, rung, medium, verifier, retry_budget, seed, metrics,
             exit_status="ok"):
        body = {
            "event": "run",
            "phase": self.phase,
            "config": {"arm": arm, "rung": rung, "medium": medium,
                       "verifier": verifier, "retry_budget": retry_budget,
                       "seed": seed},
            "metrics": metrics,
            "exit": exit_status,
        }
        self.records.append(body)
        with open(self.path, "a") as f:
            f.write(json.dumps(body, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return body


def cell_metrics(items, finals, meter, lms, store_bytes, engagement=None,
                 extra=None):
    m = {"item_correct": score(items, finals),
         "n_items": len(items),
         "flops_total": meter.model_flops + meter.verifier_cpu_s * meter.cpu_rate,
         "tokens_prefill_total": meter.t_prefill,
         "wall_s_total": meter.wall_s,
         "metric_vector": meter.ledger(lms, store_bytes)}
    if engagement is not None:
        m["verifier_engagement"] = engagement
    if extra:
        m.update(extra)
    return m


# ---------------------------------------------------------------------------
# Input loading + fail-closed pins
# ---------------------------------------------------------------------------
def load_inputs(args):
    with open(os.path.join(args.inputs_dir, "casc0-manifest.json"),
              encoding="utf-8") as f:
        man = json.load(f)
    pins = man["pins"]
    checks = {
        "dcasc0ItemsSha256": os.path.join(args.dcasc0_dir, "items", "eval.jsonl"),
        "dcasc0ExemplarsSha256": os.path.join(args.dcasc0_dir, "items", "exemplars.jsonl"),
        "dcasc0StoreSha256": os.path.join(args.dcasc0_dir, "store", "facts.jsonl"),
        "dcasc0TableSha256": os.path.join(args.dcasc0_dir, "composition-table.json"),
    }
    for key, path in checks.items():
        if sha256_file(path) != pins[key]:
            raise SystemExit("ERR_PIN: %s: %s sha != casc0-manifest pin" % (key, path))
    if "dcasc0CorpusKotHash" in pins:
        got = corpus_kot_hash(args.dcasc0_dir)
        if got != pins["dcasc0CorpusKotHash"]:
            raise SystemExit("ERR_PIN: dcasc0CorpusKotHash %s != pin %s"
                             % (got, pins["dcasc0CorpusKotHash"]))
    items = load_jsonl(checks["dcasc0ItemsSha256"])
    exemplars = load_jsonl(checks["dcasc0ExemplarsSha256"])
    with open(checks["dcasc0TableSha256"], encoding="utf-8") as f:
        table = json.load(f)
    items.sort(key=lambda x: x["rank"])
    exemplars.sort(key=lambda x: x["rank"])
    return man, items, exemplars[:2], table  # 2 exemplars, pinned choice


def build_eval_set(man, items, mock):
    dc = man["design_constants_from_registry_record"]
    floor = int(dc["eval_floor"])
    if len(items) < floor:
        raise SystemExit("ERR_EVAL_FLOOR: %d items < floor %d" % (len(items), floor))
    eval_items = items[:int(dc["per_arm_items"])]
    for it in eval_items:
        keys = item_keys(it)
        if it["answer"] not in keys or it["gold_surface"] not in \
                [o["text"] for o in it["options_final"]]:
            raise SystemExit("ERR_GOLD_SURFACE: %s gold not on the answer "
                             "surface" % it["id"])
    if mock:
        eval_items = eval_items[:man["mock"]["n_eval_items"]]
    return eval_items


# ---------------------------------------------------------------------------
# --dry-plan: the real-run cost plan vs the caps. Stdlib only; ESTIMATES.
# Prompts are ACTUALLY RENDERED per medium so the per-medium token ratio
# (rho_in) enters the plan honestly.
# ---------------------------------------------------------------------------
def dry_plan(man, eval_items, exemplars, gpu):
    plan = man["planning"]
    dc = man["design_constants_from_registry_record"]
    frames = man["prompt_frames"]
    cpt = plan["chars_per_token_estimate"]
    tput = plan["throughput_tok_per_s"][gpu]
    usd = man["flop_accounting"]["usd_per_hour"][gpu]
    seeds = dc["seeds"]
    k = dc["retry_budget_verifier_on"]
    n_opts = 7

    def cell_tokens(medium):
        rend = Renderer(frames, medium)
        tok = 0.0
        for it in eval_items:
            asserted = []
            for t in range(2, it["depth"]):
                tok += len(rend.prompt(exemplars, it, asserted, t=t)) / cpt * n_opts
                asserted.append((t, it["gold_surface"]))
            tok += len(rend.prompt(exemplars, it, asserted)) / cpt * n_opts
        return tok

    per_medium = {m: cell_tokens(m) for m in MEDIUMS}
    infl = plan["retry_inflation_verifier_on"]
    ttc_n = plan["ttc_n_planning"]
    cells = []
    for _s in seeds:
        for rung in RUNGS:
            for m in MEDIUMS:
                cells.append((rung, per_medium[m]))               # verifier off
            for m in STRUCTURED:
                cells.append((rung, per_medium[m] * infl))        # verifier on
        cells.append(("R2", per_medium["nl"] * ttc_n))            # ttc deflator
        cells.append(("R2", per_medium["gloss"] * infl))          # deranged
    hours = {"R2": 0.0, "R3": 0.0}
    for rung, toks in cells:
        hours[rung] += toks / tput[rung] / 3600.0
    est_h = sum(hours.values())
    worst_h = est_h * plan["overhead_factor"]
    cap = dc["budget"]
    lines = [
        "CASC-0' --dry-plan (ESTIMATES ONLY — planning constants from",
        "casc0-manifest.json; no GPU, no network, $0 spent by this command)",
        "",
        "eval set: %d items (rank prefix of d-casc0; per_arm_items %d, floor %d)"
        % (len(eval_items), dc["per_arm_items"], dc["eval_floor"]),
        "cells inventoried: %d GPU cells (10 factorial + ttc + deranged, x%d seeds)"
        % (len(cells), len(seeds)),
        "measured-template token ratios (rho_in planning read): nl=1.00 "
        "gloss=%.2f plain=%.2f"
        % (per_medium["gloss"] / per_medium["nl"],
           per_medium["plain"] / per_medium["nl"]),
        "",
        "GPU-hours estimate on %s:" % gpu,
        "  R2 %.2f h   R3 %.2f h   total %.2f h" % (hours["R2"], hours["R3"], est_h),
        "  with %.1fx overhead factor: %.2f h" % (plan["overhead_factor"], worst_h),
        "",
        "cost at Modal list $%.2f/h (%s):" % (usd, gpu),
        "  point estimate  $%.2f" % (est_h * usd),
        "  worst case      $%.2f  (overhead-inflated)" % (worst_h * usd),
        "  hard ceiling    $%.2f  (gpu_hours_cap %d h x $%.2f/h)"
        % (cap["gpu_hours_cap"] * usd, cap["gpu_hours_cap"], usd),
        "",
        "caps (registry/experiments/casc-0.json): usd_cap $%d, gpu_hours_cap "
        "%d h, wall_clock_cap %d h; Tier-1 cap $%d"
        % (cap["usd_cap"], cap["gpu_hours_cap"], cap["wall_clock_cap_hours"],
           cap["tier_cap_usd"]),
        "",
    ]
    verdicts = [
        ("worst case vs usd_cap ($%d)" % cap["usd_cap"], worst_h * usd <= cap["usd_cap"]),
        ("estimate vs gpu_hours_cap (%d h)" % cap["gpu_hours_cap"],
         worst_h <= cap["gpu_hours_cap"]),
        ("hard ceiling vs Tier-1 cap ($%d)" % cap["tier_cap_usd"],
         cap["gpu_hours_cap"] * usd <= cap["tier_cap_usd"]),
    ]
    for name, ok in verdicts:
        lines.append("  %-42s %s" % (name, "OK" if ok else "OVER — DO NOT LAUNCH"))
    lines.append("")
    lines.append("frozen-design cost note: the TTC deflator is the K2' kill's")
    lines.append("instrument and the deranged control is house — neither is cut.")
    print("\n".join(lines))
    return all(ok for _n, ok in verdicts)


# ---------------------------------------------------------------------------
# Cell driver
# ---------------------------------------------------------------------------
def run_cells(args, man, eval_items, exemplars, table, log):
    mock = args.mock
    dc = man["design_constants_from_registry_record"]
    frames = man["prompt_frames"]
    seeds = man["mock"]["seeds"] if mock else dc["seeds"]
    k = int(dc["retry_budget_verifier_on"])
    ttc_cfg = dc["ttc"]

    engine = Engine(table)
    assert_engine_gold(engine, eval_items)
    perm, perm_sha = make_derange_map(engine, man["deranged_control"]["perm_seed"])
    deranged = Engine(table, derange_map=perm)
    with open(os.path.join(args.out_dir, "deranged-map.json"), "w") as f:
        json.dump({"perm_seed": man["deranged_control"]["perm_seed"],
                   "map_rel_core": perm, "sha256_of_map": perm_sha,
                   "algorithm": man["deranged_control"]["algorithm"]},
                  f, indent=1, sort_keys=True)
        f.write("\n")
    log("deranged closure permutation: seed=%d sha=%s map=%s"
        % (man["deranged_control"]["perm_seed"], perm_sha[:12], perm))

    store_bytes = os.path.getsize(os.path.join(args.dcasc0_dir, "store",
                                               "facts.jsonl")) + \
        os.path.getsize(os.path.join(args.dcasc0_dir, "composition-table.json"))

    lms = {}

    def lm_for(rung):
        if rung not in lms:
            if mock:
                lms[rung] = StubLM(rung, man["mock"])
            else:
                spec = man["models"][rung]
                lms[rung] = HFLM(spec["repo"], spec["revision"], args.device)
        return lms[rung]

    emit = Emitter(args.out_dir, mock)
    fc = man["flop_accounting"]
    measured_flops = {}  # (rung, medium, verifier, seed) -> flops_total

    def drive(arm, rung, medium, verifier, kk, seed, fn, extra=None):
        guard = CellGuard("%s/%s/%s/v=%d/seed=%d" % (arm, rung, medium, verifier, seed),
                          args.cell_timeout_s, args.max_gen_per_item)
        lm = lm_for(rung)
        if mock:  # plant the labelled-MOCK skill surface for this cell
            lm.cell_medium = medium
            lm.cell_verifier_bonus = (arm == ARM_FACT and verifier == 1)
        meter = FlopMeter(fc, args.gpu_class)
        try:
            metrics = fn(lm, meter, guard)
        except CellBudgetExceeded as e:
            emit.emit(arm, rung, medium, verifier, kk, seed, {
                "cell_budget_exceeded": {
                    "kind": e.kind, "item_id": e.item_id,
                    "elapsed_s": round(e.elapsed_s, 1),
                    "n_gen_on_item_at_breach": e.n_gen},
                "note": "INSTRUMENT event: cell self-terminated at its safety "
                        "bound; exit!=ok so this record can never be an "
                        "eligible run record"}, exit_status="timeout")
            raise SystemExit("ERR_CELL_TIMEOUT: %s — run aborted in bounded "
                             "time; completed cells flushed in %s" % (e, emit.path))
        if extra:
            metrics.update(extra)
        emit.emit(arm, rung, medium, verifier, kk, seed, metrics)
        measured_flops[(arm, rung, medium, verifier, seed)] = metrics["flops_total"]
        log("cell %s %s/%s v=%d seed=%d done (%.1fs, acc-raw=%.3f)"
            % (arm, rung, medium, verifier, seed, guard.elapsed(),
               sum(metrics["item_correct"]) / max(1, metrics["n_items"])))
        return metrics

    # ---- factorial cells ----------------------------------------------------
    for seed in seeds:
        for rung in RUNGS:
            for medium in MEDIUMS:
                def cell(lm, meter, guard, medium=medium, seed=seed):
                    rend = Renderer(frames, medium)
                    finals = run_cell_plain(lm, rend, exemplars, eval_items,
                                            engine, seed, meter, guard)
                    return cell_metrics(eval_items, finals, meter, [lm], store_bytes)
                drive(ARM_FACT, rung, medium, 0, 0, seed, cell)
            for medium in STRUCTURED:
                def cell(lm, meter, guard, medium=medium, seed=seed):
                    rend = Renderer(frames, medium)
                    finals, eng = run_cell_verify(lm, rend, exemplars,
                                                  eval_items, engine, engine,
                                                  k, seed, meter, guard)
                    return cell_metrics(eval_items, finals, meter, [lm],
                                        store_bytes, engagement=eng)
                drive(ARM_FACT, rung, medium, 1, k, seed, cell)

    # ---- TTC deflator (K2' instrument): N from SEED-0 measured cells --------
    ref = measured_flops[(ARM_FACT, "R2", "gloss", 1, seeds[0])]
    nl0 = measured_flops[(ARM_FACT, "R2", "nl", 0, seeds[0])]
    ttc_n = max(int(ttc_cfg["n_min"]),
                min(int(ttc_cfg["n_max"]), int(round(ref / max(nl0, 1.0)))))
    log("ttc-deflator: N=%d (ref_flops=%.3e, nl_flops=%.3e; pinned reference "
        "cell %s)" % (ttc_n, ref, nl0, ttc_cfg["reference_cell"]))
    for seed in seeds:
        def cell(lm, meter, guard, seed=seed):
            rend = Renderer(frames, "nl")
            finals = run_cell_ttc(lm, rend, exemplars, eval_items, engine,
                                  ttc_n, seed, meter, guard)
            return cell_metrics(eval_items, finals, meter, [lm], store_bytes,
                                extra={"ttc_n_samples": ttc_n,
                                       "ttc_ref_flops_seed0": ref,
                                       "ttc_nl_flops_seed0": nl0})
        drive(ARM_TTC, "R2", "nl", 0, 0, seed, cell)

    # ---- deranged-closure house control (reported-only) ---------------------
    for seed in seeds:
        def cell(lm, meter, guard, seed=seed):
            rend = Renderer(frames, "gloss")
            finals, eng = run_cell_verify(lm, rend, exemplars, eval_items,
                                          engine, deranged, k, seed, meter,
                                          guard)
            return cell_metrics(eval_items, finals, meter, [lm], store_bytes,
                                engagement=eng,
                                extra={"deranged_map_sha256": perm_sha,
                                       "deranged_perm_seed":
                                           man["deranged_control"]["perm_seed"]})
        drive(ARM_DER, "R2", "gloss", 1, k, seed, cell)

    return emit


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    root3 = os.path.join(here, "..", "..", "..")
    ap.add_argument("--inputs-dir", default=os.path.join(here, "..", "inputs"))
    ap.add_argument("--dcasc0-dir", default=os.path.join(root3, "data", "d-casc0"))
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--gpu-class", default="A10G", choices=["T4", "A10G", "A100"])
    ap.add_argument("--mock", action="store_true",
                    help="stub-LM mechanics check on CPU; $0; labelled MOCK")
    ap.add_argument("--dry-plan", action="store_true",
                    help="print the real-run cost plan vs caps; runs nothing")
    ap.add_argument("--max-hours", type=float, default=30.0)
    ap.add_argument("--cell-timeout-s", type=float, default=None)
    ap.add_argument("--max-gen-per-item", type=int, default=MAX_GEN_PER_ITEM_DEFAULT)
    args = ap.parse_args()
    if args.cell_timeout_s is None:
        args.cell_timeout_s = CELL_TIMEOUT_S_DEFAULT[args.gpu_class]
    t0 = time.time()

    man, items, exemplars, table = load_inputs(args)
    eval_items = build_eval_set(man, items, args.mock)

    if args.dry_plan:
        full_eval = build_eval_set(man, items, mock=False)
        ok = dry_plan(man, full_eval, exemplars, args.gpu_class)
        sys.exit(0 if ok else 2)

    os.makedirs(args.out_dir, exist_ok=True)

    def log(msg):
        print("[casc0 %7.1fs] %s" % (time.time() - t0, msg), flush=True)

    label = "MOCK" if args.mock else "FULL"
    log("mode=%s device=%s eval_items=%d (d-casc0 rank prefix of %d)"
        % (label, args.device, len(eval_items), len(items)))
    if not args.mock and args.device != "cuda":
        log("WARNING: real run requested on CPU — allowed but slow")

    emit = run_cells(args, man, eval_items, exemplars, table, log)

    hours = (time.time() - t0) / 3600.0
    if hours > args.max_hours:
        raise SystemExit("ERR_TIME_BUDGET: exceeded %.1fh" % args.max_hours)

    suffix = "-mock" if args.mock else ""
    results = {
        "experiment": "casc-0",
        "outcome": ("MOCK-HARNESS-COMPLETE" if args.mock else "HARNESS-COMPLETE"),
        "outcome_note": "NOT a hypothesis verdict — raw run-records only; the "
                        "verdict is computed by the pinned analysis/casc_0.py "
                        "+ tools/registry/verdict-gen.py under run-vs-audit "
                        "separation; every verdict sentence carries the "
                        "SELF-AUTHORED / kernel-STYLE / engine-derived-gold "
                        "rider (kernel-STYLE per the executed ASM-1158 "
                        "mapping, poc/casc-0/kernel-coverage.md)",
        "mode": label,
        "date": utcnow(),
        "device": args.device,
        "gpu_class_assumed_for_usd": args.gpu_class,
        "pins": man["pins"],
        "models": ({"note": "MOCK — synthetic stub LM, no models loaded"}
                   if args.mock else
                   {r: man["models"][r] for r in RUNGS}),
        "n_records": len(emit.records),
        "n_eval_items": len(eval_items),
        "records_file": os.path.basename(emit.path),
        "seeds": man["mock"]["seeds"] if args.mock else
                 man["design_constants_from_registry_record"]["seeds"],
        "wallClockHours": hours,
    }
    with open(os.path.join(args.out_dir, "results-casc0%s.json" % suffix), "w") as f:
        json.dump(results, f, indent=2, sort_keys=True)
    print("[casc0] OUTCOME: %s (%d run-record bodies in %s)"
          % (results["outcome"], len(emit.records), emit.path))


if __name__ == "__main__":
    main()
