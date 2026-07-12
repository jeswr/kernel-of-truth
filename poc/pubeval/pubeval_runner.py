#!/usr/bin/env python3
"""poc/pubeval — reusable public-benchmark evaluation harness for small HFLM
models (SmolLM2 family), serving BOTH the dimension-collapse compression
experiment and the 2026-07-12 maintainer directive "use existing human-built
benchmarks".

Benchmarks wired (survey top picks, docs/next/analysis/existing-benchmarks-
survey.md §4): FOLIO (MIT, HUMAN-AUTHORED), ARC-Easy/-Challenge (CC BY-SA 4.0,
HUMAN-SOURCED exam), GSM8K (MIT, HUMAN-AUTHORED). No LLM-PROXY gold.

Scorer: self-contained few-shot loglikelihood forced-choice + generative
exact-match. lm-evaluation-harness is deliberately NOT wired: the pinned Modal
image (poc/modal/requirements-image.txt, sha 0fac7243…) contains only
numpy/torch/transformers/bitsandbytes/accelerate, and image-reuse discipline
(PROPOSED-ASM-1106 lineage) bars new deps. The forced-choice logprob math is
the f2bt HFLM scoring pattern (poc/f2b-transfer/runner/f2bt_runner.py
HFLM._option_logprobs) generalised to (context, continuation).

WEIGHT-TRANSFORM HOOK (the dimcollapse seam): --transform applies a callable
fn(model, **kwargs) -> model|None to the loaded model BEFORE eval, so
baseline / kernel-normalised-dropped / magnitude-pruned / random-dropped
variants run through byte-identical prompts, seeds and scoring. Programmatic
callers may instead pass an ALREADY-MODIFIED model via HFLM.from_model(...).

Metrics: per-benchmark acc (sum-logprob argmax) + acc_norm (choice-string-
length normalised — the lm-eval multiple_choice convention) + gold-
continuation perplexity; GSM8K
greedy-decode exact match on the final number + gold-solution perplexity;
macro-average aggregate. Numbers are INTERNAL-RELATIVE (fixed shots/prompts)
— not leaderboard-comparable without matching harness conventions; relative
deltas across weight variants are the designed use.

Usage:
  python3 pubeval_runner.py --mock --n 8                       # CPU, $0, no torch
  python3 pubeval_runner.py --model smollm2-135m --device cuda # real eval
  python3 pubeval_runner.py --model smollm2-1.7b --device cuda \
      --transform poc/pubeval/transforms.py:magnitude_prune \
      --transform-kwargs '{"fraction":0.5}'

Exploratory infrastructure: NOT a frozen experiment; no registry writes.
Python 3.9 / stdlib-only in --mock (the coordinator box has no torch).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
import json
import math
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import benchmarks as B  # noqa: E402

SCHEMA = "kot-pubeval-result/1"
SEED_BASE = 20260712  # this harness's published seed (f2bt SEED_BASE pattern)

# Pinned SmolLM2 revisions — provenance chain: R1/R3 verbatim from
# poc/rules-1/inputs/rules1-manifest.json model_revisions (FROZEN carriers
# f2b-replicate/f2b-transfer); R2 (360M) verbatim from
# poc/f2/inputs/f2-manifest.json (registry/amendments/f2/2-pin-model-
# revisions-r1-r2.json). Fail closed on unpinned loads (ERR_UNPINNED_MODEL,
# f2bt discipline).
MODEL_REGISTRY = {
    "smollm2-135m": {"repo": "HuggingFaceTB/SmolLM2-135M-Instruct",
                     "revision": "12fd25f77366fa6b3b4b768ec3050bf629380bac"},
    "smollm2-360m": {"repo": "HuggingFaceTB/SmolLM2-360M-Instruct",
                     "revision": "a10cc1512eabd3dde888204e902eca88bddb4951"},
    "smollm2-1.7b": {"repo": "HuggingFaceTB/SmolLM2-1.7B-Instruct",
                     "revision": "31b70e2e869a7173562077fd711b654946d38674"},
    # DDC surgery donors (docs/next/design/DDC.md §2.5 / §5.1 T0 mechanical
    # addition 2, ASM-1655): BASE checkpoints, NOT Instruct — base-not-
    # instruct avoids the chat-template confound in likelihood scoring.
    # Revisions pinned at T0 ops (2026-07-12) from the HF model API
    # (api/models/<repo> "sha" = the main-branch commit at pin time);
    # config.json re-verified at these revisions: 135M d_model=576,
    # 30 layers; 360M d_model=960, 32 layers (DDC.md §2.5 re-pin).
    "smollm2-135m-base": {
        "repo": "HuggingFaceTB/SmolLM2-135M",
        "revision": "93efa2f097d58c2a74874c7e644dbc9b0cee75a2"},
    "smollm2-360m-base": {
        "repo": "HuggingFaceTB/SmolLM2-360M",
        "revision": "f8027fd0eaeea54caa13c31d31b9fdc459c38b49"},
}

GEN_STOP = "\nQuestion:"  # few-shot frame delimiter doubles as stop string


def det_u(*keys):
    """Deterministic uniform in [0,1) from sha256 over the key tuple
    (f2bt_runner.det_u convention — no RNG state anywhere in the harness)."""
    h = hashlib.sha256(("|".join(str(k) for k in keys)).encode()).digest()
    return int.from_bytes(h[:8], "big") / 2.0 ** 64


def utcnow():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ---------------------------------------------------------------------------
# Weight-transform hook
# ---------------------------------------------------------------------------
def resolve_transform(spec):
    """'path/to/file.py:func' or 'pkg.module:func' -> callable."""
    if ":" not in spec:
        raise SystemExit("ERR_TRANSFORM_SPEC: expected 'file.py:func' or "
                         "'module:func', got %r" % spec)
    mod_part, fn_name = spec.rsplit(":", 1)
    if mod_part.endswith(".py") or os.path.sep in mod_part:
        path = os.path.abspath(mod_part)
        if not os.path.exists(path):
            raise SystemExit("ERR_TRANSFORM_SPEC: no such file %s" % path)
        name = "pubeval_transform_" + hashlib.sha256(
            path.encode()).hexdigest()[:8]
        s = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(s)
        s.loader.exec_module(mod)
    else:
        mod = importlib.import_module(mod_part)
    fn = getattr(mod, fn_name, None)
    if not callable(fn):
        raise SystemExit("ERR_TRANSFORM_SPEC: %s has no callable %r"
                         % (mod_part, fn_name))
    return fn


def apply_transform(lm, spec, kwargs_json):
    """Apply the hook to lm.model; record before/after provenance."""
    kwargs = json.loads(kwargs_json) if kwargs_json else {}
    if not isinstance(kwargs, dict):
        raise SystemExit("ERR_TRANSFORM_KWARGS: --transform-kwargs must be a "
                         "JSON object")
    fn = resolve_transform(spec)
    before = {"param_count": lm.param_count(),
              "weight_fingerprint": lm.weight_fingerprint()}
    out = fn(lm.model, **kwargs)
    if out is not None:
        lm.model = out
    after = {"param_count": lm.param_count(),
             "weight_fingerprint": lm.weight_fingerprint()}
    return {"spec": spec, "kwargs": kwargs, "before": before, "after": after,
            "changed_weights": before["weight_fingerprint"]
            != after["weight_fingerprint"]}


# ---------------------------------------------------------------------------
# Real model — HFLM (SmolLM2 via transformers; f2bt loader pattern)
# ---------------------------------------------------------------------------
class HFLM:
    """Forced-choice loglikelihood + greedy generation over a causal LM.
    Loglikelihood math is f2bt_runner.HFLM._option_logprobs generalised to
    (context, continuation); fp16 default (f2bt default dtype)."""

    def __init__(self, repo, revision, device, dtype="float16",
                 local_path=None):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.torch = torch
        if local_path:
            src, rev_kw = local_path, {}
            self.name = "local:%s" % os.path.basename(os.path.normpath(local_path))
        else:
            if not revision:
                raise SystemExit("ERR_UNPINNED_MODEL: %s has no pinned "
                                 "revision" % repo)
            src, rev_kw = repo, {"revision": revision}
            self.name = "%s@%s" % (repo, revision[:8])
        self.tok = AutoTokenizer.from_pretrained(src, **rev_kw)
        self.model = AutoModelForCausalLM.from_pretrained(
            src, torch_dtype=getattr(torch, dtype), **rev_kw)
        self.model.to(device)
        self.model.eval()
        for p in self.model.parameters():
            p.requires_grad_(False)
        self.device = device

    @classmethod
    def from_model(cls, model, tokenizer, name, device=None):
        """Wrap an ALREADY-LOADED (possibly weight-modified) model — the
        programmatic dimcollapse entry point: modify weights however you
        like, then eval through the identical scoring path."""
        import torch
        self = cls.__new__(cls)
        self.torch = torch
        self.model = model
        self.tok = tokenizer
        self.model.eval()
        self.device = device or next(model.parameters()).device
        self.name = name
        return self

    def param_count(self):
        return sum(p.numel() for p in self.model.parameters())

    def weight_fingerprint(self):
        """Cheap deterministic fingerprint distinguishing weight variants:
        sha256 over (name, shape, float64 sum, float64 abs-sum) per tensor.
        Not a full byte hash (1.7B fp16 = 3.4 GB); collisions across the
        variants under comparison are vanishingly unlikely."""
        h = hashlib.sha256()
        with self.torch.no_grad():
            for name, p in sorted(self.model.named_parameters()):
                t = p.detach().double()
                h.update(("%s|%s|%.17g|%.17g" % (
                    name, tuple(p.shape), float(t.sum()),
                    float(t.abs().sum()))).encode())
        return h.hexdigest()

    def _encode_pair(self, context, continuation):
        """JOINT context+continuation tokenisation (lm-evaluation-harness
        `_encode_pair` convention, lm_eval/models/huggingface.py). Encoding
        the two strings SEPARATELY and concatenating (the old f2bt pattern)
        can score a boundary token sequence the model would never assign to
        the joint string, because BPE merges across the split point —
        cross-vendor review 2026-07-12 finding #1 (FIX-BEFORE-USE).

        Reference recipe: move any trailing context whitespace onto the
        continuation (so the context prefix tokenises stably), encode the
        WHOLE string once, encode the context alone, and take the
        continuation ids as the suffix of the joint encoding."""
        n_spaces = len(context) - len(context.rstrip())
        if n_spaces > 0:
            continuation = context[-n_spaces:] + continuation
            context = context[:-n_spaces]
        whole = self.tok.encode(context + continuation,
                                add_special_tokens=False)
        ctx = self.tok.encode(context, add_special_tokens=False)
        return ctx, whole[len(ctx):]

    def loglikelihood(self, context, continuation):
        """(sum logprob of continuation tokens | context, n_cont_tokens).
        Continuation ids come from the JOINT encoding via _encode_pair —
        NOT from tokenising the continuation alone (boundary-drift fix;
        regression: poc/pubeval/test_boundary_regression.py)."""
        torch = self.torch
        pre, oids = self._encode_pair(context, continuation)
        if not pre:
            # This harness always supplies a non-empty context (few-shot
            # prefix + "Question: … Answer:"); fail closed rather than
            # silently score an unconditioned continuation.
            raise SystemExit("ERR_EMPTY_CONTEXT: %r" % context[:40])
        if not oids:
            raise SystemExit("ERR_EMPTY_CONTINUATION: %r" % continuation[:40])
        with torch.no_grad():
            ids = torch.tensor([pre + oids], device=self.device)
            logits = self.model(ids).logits[0]
            lp = torch.log_softmax(logits[:-1].float(), dim=-1)
            tgt = ids[0, 1:]
            start = len(pre) - 1
            total = float(lp[start:, :].gather(1, tgt[start:, None]).sum())
        return total, len(oids)

    def score_options(self, context, options, gold, item_id):
        """Per-option (sum_lp, n_tokens). `gold`/`item_id` are accepted for
        interface parity with the mock stub and NEVER read here (gold-leak
        guard by construction — f2bt discipline)."""
        return [self.loglikelihood(context, " %s" % opt) for opt in options]

    def generate_answer(self, context, item, max_new_tokens):
        """Greedy decode (deterministic); cut at the few-shot frame stop."""
        torch = self.torch
        ids = self.tok.encode(context, add_special_tokens=False)
        inp = torch.tensor([ids], device=self.device)
        with torch.no_grad():
            out = self.model.generate(
                inp, max_new_tokens=max_new_tokens, do_sample=False,
                pad_token_id=(self.tok.pad_token_id
                              if self.tok.pad_token_id is not None
                              else self.tok.eos_token_id))
        text = self.tok.decode(out[0][len(ids):], skip_special_tokens=True)
        return text.split(GEN_STOP)[0] if GEN_STOP in text else text


# ---------------------------------------------------------------------------
# Mock model — SYNTHETIC mechanics-only stand-in (f2bt StubLM discipline:
# deterministic sha-driven outputs, planted skill so gates/denominators
# resolve; NEVER a measurement). No torch anywhere on this path.
# ---------------------------------------------------------------------------
class StubLM:
    SKILL = 0.75

    def __init__(self, seed):
        self.seed = seed
        self.name = "stub-pubeval"
        self.model = {"stub": True}  # transform hook plumbing target

    def param_count(self):
        return 0

    def weight_fingerprint(self):
        return "stub-" + hashlib.sha256(str(self.model).encode()).hexdigest()[:16]

    def score_options(self, context, options, gold, item_id):
        pick = gold if det_u("mc", self.seed, item_id) < self.SKILL else (
            (gold + 1) % len(options))
        outs = []
        for i, opt in enumerate(options):
            n = max(1, len(opt.split()))
            base = -2.0 - 3.0 * det_u("lp", self.seed, item_id, i)
            if i == pick:
                base += 2.5
            outs.append((base * n, n))
        return outs

    def generate_answer(self, context, item, max_new_tokens):
        gold = item["gold_answer"]
        if det_u("gen", self.seed, item["id"]) < self.SKILL:
            return " Working it through. #### %s" % gold
        return " Working it through. #### %s" % (
            B.normalize_number(str(int(float(gold)) + 7)))

    def loglikelihood(self, context, continuation):
        n = max(1, len(continuation.split()))
        return (-1.5 - det_u("ll", self.seed, continuation[:64])) * n, n


# ---------------------------------------------------------------------------
# Evaluation core (identical across real/mock and across weight variants)
# ---------------------------------------------------------------------------
def subsample(items, n, seed, bench):
    """Deterministic subsample: rank by det_u, take first n (0 = all)."""
    if n <= 0 or n >= len(items):
        return items
    ranked = sorted(items, key=lambda it: det_u("sub", bench, seed, it["id"]))
    return ranked[:n]


def eval_mc(lm, bench, items, prefix, log, item_log=None):
    n = len(items)
    acc = acc_norm = 0
    nll_sum = tok_sum = 0.0
    t0 = time.time()
    for i, it in enumerate(items):
        ctx = prefix + it["context"]
        scored = lm.score_options(ctx, it["options"], it["gold"], it["id"])
        lps = [s[0] for s in scored]
        # acc_norm: length-normalise by the CHOICE STRING length, exactly as
        # lm-evaluation-harness does for multiple_choice tasks (process_
        # results: completion_len = float(len(choice)); argmax(lls/len)).
        # The previous per-TOKEN normalisation (lp/n_tokens) was NOT the
        # lm-eval convention — cross-vendor review 2026-07-12 finding #2.
        norm = [lps[j] / float(len(it["options"][j]))
                for j in range(len(lps))]
        it_acc = int(max(range(len(lps)), key=lambda j: lps[j]) == it["gold"])
        it_norm = int(max(range(len(norm)), key=lambda j: norm[j])
                      == it["gold"])
        acc += it_acc
        acc_norm += it_norm
        g_lp, g_n = scored[it["gold"]]
        nll_sum += -g_lp
        tok_sum += g_n
        if item_log is not None:
            # per-item record emission (DDC.md §5.1 T0 mechanical addition
            # 1, ASM-1655): the ddc1 paired statistics are impossible
            # without per-item correctness records — gate I-5 discipline.
            item_log({"bench": bench, "item_id": it["id"], "kind": "mc",
                      "acc": it_acc, "acc_norm": it_norm,
                      "option_logprobs": [round(x, 6) for x in lps],
                      "option_tokens": [s[1] for s in scored],
                      "gold": it["gold"]})
        if (i + 1) % 50 == 0 or i + 1 == n:
            log("  %s %d/%d (%.1fs)" % (bench, i + 1, n, time.time() - t0))
    nll_tok = nll_sum / max(tok_sum, 1.0)
    return {"kind": "mc", "n": n, "acc": acc / n, "acc_norm": acc_norm / n,
            "gold_nll_per_token": nll_tok,
            "gold_ppl": math.exp(min(nll_tok, 50.0)),
            "elapsed_s": round(time.time() - t0, 2)}


def eval_gen(lm, bench, items, prefix, max_new_tokens, log, item_log=None):
    n = len(items)
    em = 0
    nll_sum = tok_sum = 0.0
    t0 = time.time()
    for i, it in enumerate(items):
        ctx = prefix + it["context"]
        out = lm.generate_answer(ctx, it, max_new_tokens)
        it_em = int(B.extract_final_number(out) == it["gold_answer"])
        em += it_em
        lp, ntok = lm.loglikelihood(ctx, " %s" % it["gold_solution"])
        nll_sum += -lp
        tok_sum += ntok
        if item_log is not None:
            # per-item record emission (ASM-1655 addition 1; see eval_mc)
            item_log({"bench": bench, "item_id": it["id"], "kind": "gen",
                      "em": it_em,
                      "gold_solution_logprob": round(lp, 6),
                      "gold_solution_tokens": ntok})
        if (i + 1) % 25 == 0 or i + 1 == n:
            log("  %s %d/%d (%.1fs)" % (bench, i + 1, n, time.time() - t0))
    nll_tok = nll_sum / max(tok_sum, 1.0)
    return {"kind": "gen", "n": n, "exact_match": em / n,
            "gold_solution_nll_per_token": nll_tok,
            "gold_solution_ppl": math.exp(min(nll_tok, 50.0)),
            "elapsed_s": round(time.time() - t0, 2)}


def evaluate(lm, bench_names, data_dir, n, shots, seed, mock,
             max_new_tokens=256, log=print, item_log=None):
    """Programmatic entry point. `lm` is an HFLM (possibly wrapping a
    weight-modified model via HFLM.from_model) or a StubLM. `item_log`, if
    given, is called once per scored item with a per-item record dict
    (ASM-1655 per-item emission; aggregates are byte-identical whether or
    not it is supplied)."""
    results = {}
    for name in bench_names:
        if name not in B.BENCHMARKS:
            raise SystemExit("ERR_BENCH_UNKNOWN: %r (have: %s)"
                             % (name, ",".join(sorted(B.BENCHMARKS))))
        bench = B.BENCHMARKS[name]
        if mock:
            items = bench.mock_items("eval")
            pool = bench.mock_items("fewshot")
        else:
            items = bench.load(data_dir, "eval")
            pool = bench.load(data_dir, "fewshot")
        items = subsample(items, n, seed, name)
        prefix = B.build_fewshot_prefix(name, pool, shots, seed, det_u)
        log("[%s] %d items, %d-shot (%s, %s)"
            % (name, len(items), shots, B.LICENSES[name]["license"],
               B.LICENSES[name]["provenance"]))
        if bench.kind == "mc":
            results[name] = eval_mc(lm, name, items, prefix, log,
                                    item_log=item_log)
        else:
            results[name] = eval_gen(lm, name, items, prefix,
                                     max_new_tokens, log, item_log=item_log)
        results[name].update(B.LICENSES[name])

    # Aggregate: unweighted macro-average of the headline metric per
    # benchmark (acc_norm for MC — lm-eval multiple_choice convention,
    # choice-string-length normalised — EM for gen).
    heads = {k: (v["acc_norm"] if v["kind"] == "mc" else v["exact_match"])
             for k, v in results.items()}
    aggregate = {"macro_acc": sum(heads.values()) / len(heads),
                 "per_benchmark_headline": heads,
                 "headline_metric": "acc_norm (mc) / exact_match (gen)"}
    return results, aggregate


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--model", default="smollm2-135m",
                    help="registry key: %s" % ",".join(sorted(MODEL_REGISTRY)))
    ap.add_argument("--model-path", default="",
                    help="local checkpoint dir (e.g. a weight-modified dump);"
                         " overrides --model repo/revision")
    ap.add_argument("--revision", default="",
                    help="override the pinned revision (recorded; use "
                         "deliberately)")
    ap.add_argument("--benchmarks", default=B.DEFAULT_BENCHMARKS)
    ap.add_argument("--n", type=int, default=0,
                    help="per-benchmark item cap, 0 = full split "
                         "(deterministic seeded subsample)")
    ap.add_argument("--shots", type=int, default=5)
    ap.add_argument("--seed", type=int, default=SEED_BASE)
    ap.add_argument("--device", default="cpu", choices=("cpu", "cuda"))
    ap.add_argument("--dtype", default="float16")
    ap.add_argument("--max-gen-tokens", type=int, default=256)
    ap.add_argument("--data-dir", default=os.path.join(_HERE, "data"))
    ap.add_argument("--out-dir", default=os.path.join(_HERE, "results"))
    ap.add_argument("--mock", action="store_true",
                    help="SYNTHETIC mechanics-only validation: StubLM + "
                         "embedded fixtures, no torch, no network, $0")
    ap.add_argument("--transform", default="",
                    help="weight-transform hook 'file.py:func' or "
                         "'module:func' applied to the loaded model before "
                         "eval (dimcollapse seam)")
    ap.add_argument("--transform-kwargs", default="",
                    help='JSON object of kwargs for --transform')
    ap.add_argument("--log-items", default="",
                    help="write one JSON line per scored item to this path "
                         "(per-item emission sidecar, DDC ASM-1655; "
                         "aggregates unchanged)")
    args = ap.parse_args()

    bench_names = [b.strip() for b in args.benchmarks.split(",") if b.strip()]
    started = utcnow()
    t0 = time.time()

    if args.mock:
        lm = StubLM(args.seed)
        model_info = {"name": lm.name, "mock": True}
    else:
        spec = MODEL_REGISTRY.get(args.model)
        if not spec and not args.model_path:
            raise SystemExit("ERR_MODEL_UNKNOWN: %r (have: %s; or use "
                             "--model-path)" % (args.model,
                                                ",".join(sorted(MODEL_REGISTRY))))
        lm = HFLM(spec["repo"] if spec else "",
                  args.revision or (spec["revision"] if spec else ""),
                  args.device, dtype=args.dtype,
                  local_path=args.model_path or None)
        model_info = {"name": lm.name, "mock": False,
                      "param_count": lm.param_count(), "dtype": args.dtype,
                      "device": args.device}

    transform_info = None
    if args.transform:
        transform_info = apply_transform(lm, args.transform,
                                         args.transform_kwargs)
        print("transform applied: %s changed_weights=%s"
              % (transform_info["spec"], transform_info["changed_weights"]))

    item_fh = None
    item_log = None
    if args.log_items:
        os.makedirs(os.path.dirname(os.path.abspath(args.log_items)),
                    exist_ok=True)
        item_fh = open(args.log_items, "w")

        def item_log(rec, _fh=item_fh):
            _fh.write(json.dumps(rec, sort_keys=True) + "\n")

    results, aggregate = evaluate(
        lm, bench_names, args.data_dir, args.n, args.shots, args.seed,
        args.mock, max_new_tokens=args.max_gen_tokens, item_log=item_log)
    if item_fh is not None:
        item_fh.close()
        print("per-item records -> %s" % args.log_items)

    out = {
        "schema": SCHEMA,
        "mock": bool(args.mock),
        "mock_disclosure": ("SYNTHETIC mechanics-only stub outputs — never a "
                            "measurement" if args.mock else None),
        "model": model_info,
        "transform": transform_info,
        "config": {"benchmarks": bench_names, "n": args.n,
                   "shots": args.shots, "seed": args.seed,
                   "max_gen_tokens": args.max_gen_tokens,
                   "scorer": "self-contained few-shot loglikelihood + "
                             "greedy exact-match (f2bt HFLM pattern); "
                             "lm-evaluation-harness NOT used (pinned-image "
                             "discipline)"},
        "benchmarks": results,
        "aggregate": aggregate,
        "comparability_note": ("numbers are internal-relative (fixed "
                               "prompts/shots/seed); use for baseline-vs-"
                               "transformed deltas, not leaderboards"),
        "started_utc": started, "finished_utc": utcnow(),
        "elapsed_s": round(time.time() - t0, 2),
    }
    os.makedirs(args.out_dir, exist_ok=True)
    name = "results-pubeval-mock.json" if args.mock else "results-pubeval.json"
    path = os.path.join(args.out_dir, name)
    with open(path, "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print("\nwrote %s" % path)
    print("aggregate macro_acc = %.4f over %s"
          % (aggregate["macro_acc"], ",".join(bench_names)))
    for k, v in results.items():
        head = v["acc_norm"] if v["kind"] == "mc" else v["exact_match"]
        print("  %-14s n=%-5d headline=%.4f" % (k, v["n"], head))


if __name__ == "__main__":
    main()
