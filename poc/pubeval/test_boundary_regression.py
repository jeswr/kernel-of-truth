#!/usr/bin/env python3
"""Regression test for the JOINT context+continuation encoding fix
(cross-vendor review 2026-07-12 finding #1, FIX-BEFORE-USE).

THE BUG BEING GUARDED: the original HFLM.loglikelihood tokenised context and
continuation SEPARATELY and concatenated the id lists (f2bt pattern). BPE can
merge characters across the split point, so the concatenated sequence can be
one the tokenizer would NEVER produce for the joint string — the model is
then scored on off-distribution boundary tokens and every downstream metric
(acc, acc_norm, gold ppl) silently drifts. The fix is the lm-evaluation-
harness `_encode_pair` convention: shift trailing context whitespace onto the
continuation, encode the WHOLE string once, and take the continuation ids as
the suffix of the joint encoding.

Parts:
  A (stdlib only — runs on the torch-less coordinator box):
    brute-force check of HFLM._encode_pair against a synthetic greedy
    longest-match tokenizer engineered to merge across the boundary,
    asserting (i) ctx_ids + cont_ids reproduces the joint encoding exactly
    and (ii) the OLD separate-encode scheme provably drifts on the same
    input (i.e. this test FAILS against the pre-fix code).
  B (needs torch; SKIPs cleanly without it — run in the pinned Modal image
    or any torch env):
    brute-force MULTI-TOKEN loglikelihood check through the real
    HFLM.loglikelihood path with a tiny deterministic causal LM: the summed
    logprob must equal a hand-computed sum over the joint encoding's
    continuation positions, and the old scheme's token sequence must differ.
  C (needs transformers + a cached real tokenizer; SKIPs cleanly):
    prefix-consistency sweep of _encode_pair over ARC/GSM8K-shaped pairs
    with the pinned SmolLM2 tokenizer.

Exit 0 = all executed parts passed. Any assertion failure exits non-zero.
Stdlib only in part A; Python 3.9 compatible. NOT a benchmark; no data, no
network (part C uses only an already-cached tokenizer), no registry writes.
"""

from __future__ import annotations

import math
import os
import sys
from types import SimpleNamespace

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from pubeval_runner import HFLM  # noqa: E402  (torch imports are lazy)


# ---------------------------------------------------------------------------
# Synthetic tokenizer: greedy longest-match over an explicit vocab. Models
# the real BPE failure mode: a boundary character sequence ("Answer: " + "
# True") tokenises differently split vs joint.
# ---------------------------------------------------------------------------
class GreedyTok:
    def __init__(self, vocab):
        # Longest-match-first; every single char of the test strings must be
        # covered so encoding is total.
        self.vocab = sorted(set(vocab), key=len, reverse=True)
        self.id_of = {t: i for i, t in enumerate(self.vocab)}

    def encode(self, text, add_special_tokens=False):
        assert add_special_tokens is False
        ids, i = [], 0
        while i < len(text):
            for t in self.vocab:
                if text.startswith(t, i):
                    ids.append(self.id_of[t])
                    i += len(t)
                    break
            else:
                raise AssertionError("GreedyTok: no vocab entry at %r"
                                     % text[i:i + 8])
        return ids


VOCAB = (["Answer:", " True", " Tr", "True", "ue", " ", "x", "y"]
         + list("Answer: Truexy"))
TOK = GreedyTok(VOCAB)


def old_separate_encode(tok, context, continuation):
    """The PRE-FIX scheme (encode separately, concatenate) — kept here only
    to prove the drift this test guards against."""
    pre = tok.encode(context, add_special_tokens=False)
    oids = tok.encode(continuation, add_special_tokens=False)
    return pre, oids


def encode_pair(tok, context, continuation):
    """Call the fixed HFLM._encode_pair without constructing an HFLM (no
    torch needed: the method touches only self.tok)."""
    return HFLM._encode_pair(SimpleNamespace(tok=tok), context, continuation)


def shifted(context, continuation):
    """The whitespace shift _encode_pair applies before joint encoding."""
    n = len(context) - len(context.rstrip())
    if n > 0:
        return context[:-n], context[-n:] + continuation
    return context, continuation


def part_a():
    cases = [
        # (context, continuation) — case 1 is the classic trailing-space
        # boundary: "Answer: " + "True" joint-encodes as ["Answer:", " True"]
        # but separate-encodes as ["Answer:", " ", "True"].
        ("Answer: ", "True"),
        # case 2: MULTI-token continuation across the same boundary
        # (joint: ["Answer:", " True", "x", "y"]; old: 5 ids) — the
        # brute-force multi-token shape used again in part B.
        ("Answer: ", "Truexy"),
        # case 3: no drift expected — joint must still equal separate here.
        ("Answer:", " True"),
    ]
    drift_seen = 0
    for context, continuation in cases:
        ctx_ids, cont_ids = encode_pair(TOK, context, continuation)
        s_ctx, s_cont = shifted(context, continuation)
        joint = TOK.encode(s_ctx + s_cont, add_special_tokens=False)
        # (i) the fixed path reproduces the JOINT encoding exactly.
        assert ctx_ids + cont_ids == joint, (
            "FIXED path drifted from joint encoding: %r + %r -> %r vs %r"
            % (context, continuation, ctx_ids + cont_ids, joint))
        assert cont_ids, "empty continuation ids for %r" % continuation
        # (ii) brute force the old scheme; count real drift cases.
        pre, oids = old_separate_encode(TOK, context, continuation)
        if pre + oids != joint:
            drift_seen += 1
        print("  A ok: %r + %r -> joint %s (old scheme %s)"
              % (context, continuation, joint,
                 "DRIFTED (caught)" if pre + oids != joint else "agrees"))
    # The test must actually exercise the bug: at least the two engineered
    # cases have to drift under the old scheme, else the fixture is dead.
    assert drift_seen >= 2, (
        "fixture no longer exhibits boundary drift (%d cases) — test is dead"
        % drift_seen)
    print("PART A PASS: _encode_pair == joint encoding on all %d cases; "
          "old separate-encode scheme drifts on %d (would fail pre-fix)"
          % (len(cases), drift_seen))


# ---------------------------------------------------------------------------
# Part B — brute-force multi-token loglikelihood through HFLM.loglikelihood
# with a tiny deterministic causal LM (no randomness: closed-form weights).
# ---------------------------------------------------------------------------
def part_b():
    try:
        import torch
        import torch.nn as nn
    except ImportError:
        print("PART B SKIP: torch not installed on this box — run inside "
              "the pinned Modal image (or any torch env) for full coverage")
        return False

    V, D = len(TOK.vocab), 8

    class TinyLM(nn.Module):
        """Deterministic causal toy LM: embedding -> causal cumulative mean
        -> tied-shape output head. Closed-form sin/cos weights (no RNG —
        harness det_u discipline applies to tests too)."""

        def __init__(self):
            super().__init__()
            emb = torch.tensor([[math.sin(0.7 * i + 1.3 * j)
                                 for j in range(D)] for i in range(V)],
                               dtype=torch.float32)
            self.emb = nn.Embedding.from_pretrained(emb, freeze=True)
            self.out = nn.Linear(D, V, bias=False)
            with torch.no_grad():
                self.out.weight.copy_(torch.tensor(
                    [[math.cos(0.3 * i + 0.9 * j) for j in range(D)]
                     for i in range(V)], dtype=torch.float32))

        def forward(self, ids):
            h = self.emb(ids)
            denom = torch.arange(1, ids.shape[1] + 1,
                                 dtype=h.dtype).view(1, -1, 1)
            causal = torch.cumsum(h, dim=1) / denom  # position t sees <= t
            return SimpleNamespace(logits=self.out(causal))

    lm = HFLM.from_model(TinyLM(), TOK, name="tinylm-boundary-test",
                         device="cpu")

    # Both cases drift under the old scheme AND have multi-token
    # continuations (3 and 4 ids) — double-space case exercises a shift of
    # more than one boundary character.
    for context, continuation in [("Answer: ", "Truexy"),
                                  ("Answer:  ", "Truexy")]:
        got_lp, got_n = lm.loglikelihood(context, continuation)

        # Brute force over the JOINT encoding, independently of the runner.
        s_ctx, s_cont = shifted(context, continuation)
        whole = TOK.encode(s_ctx + s_cont, add_special_tokens=False)
        ctx_ids = TOK.encode(s_ctx, add_special_tokens=False)
        assert whole[:len(ctx_ids)] == ctx_ids, "fixture prefix broken"
        with torch.no_grad():
            logits = lm.model(torch.tensor([whole])).logits[0]
            lp = torch.log_softmax(logits[:-1].float(), dim=-1)
        want_lp = sum(float(lp[t - 1, whole[t]])
                      for t in range(len(ctx_ids), len(whole)))
        want_n = len(whole) - len(ctx_ids)

        assert want_n >= 2, "fixture must be MULTI-token (got %d)" % want_n
        assert got_n == want_n, ("token count %d != brute force %d"
                                 % (got_n, want_n))
        assert abs(got_lp - want_lp) < 1e-5, (
            "sum logprob %.8f != brute force %.8f" % (got_lp, want_lp))

        # And the OLD scheme scores a DIFFERENT token sequence here — the
        # exact drift the fix removes.
        pre, oids = old_separate_encode(TOK, context, continuation)
        assert pre + oids != whole, "fixture stopped exhibiting drift"
        print("  B ok: %r + %r lp=%.6f n=%d matches brute force; old "
              "scheme token seq differs (%s vs %s)"
              % (context, continuation, got_lp, got_n, pre + oids, whole))
    print("PART B PASS: HFLM.loglikelihood == brute-force joint-encoding "
          "sum on multi-token continuations")
    return True


# ---------------------------------------------------------------------------
# Part C — prefix-consistency sweep with the real pinned SmolLM2 tokenizer
# (cache-only; SKIPs without transformers or without a cached tokenizer).
# ---------------------------------------------------------------------------
def part_c():
    try:
        from transformers import AutoTokenizer
    except ImportError:
        print("PART C SKIP: transformers not installed")
        return False
    from pubeval_runner import MODEL_REGISTRY
    spec = MODEL_REGISTRY["smollm2-135m"]
    try:
        tok = AutoTokenizer.from_pretrained(spec["repo"],
                                            revision=spec["revision"])
    except Exception as e:  # noqa: BLE001 — no cache/network: skip, not fail
        print("PART C SKIP: tokenizer unavailable (%s)" % e)
        return False
    pairs = [("Question: Which gas do plants absorb?\nAnswer:",
              " carbon dioxide"),
             ("Question: 2+2?\nAnswer: ", "4"),
             ("Premises:\nAll blints are cromed.\nConclusion: Tuk is "
              "cromed.\nAnswer:", " Uncertain"),
             ("Question: Pat has 3 pens and buys 4 more.\nAnswer:",
              " Pat has 3+4=7 pens.\n#### 7")]
    for context, continuation in pairs:
        ctx_ids, cont_ids = encode_pair(tok, context, continuation)
        s_ctx, s_cont = shifted(context, continuation)
        joint = tok.encode(s_ctx + s_cont, add_special_tokens=False)
        assert ctx_ids + cont_ids == joint, (
            "real-tokenizer drift: %r + %r" % (context, continuation))
        assert len(cont_ids) >= 1
    print("PART C PASS: real SmolLM2 tokenizer prefix-consistent on %d pairs"
          % len(pairs))
    return True


if __name__ == "__main__":
    print("boundary-token drift regression (review finding #1)")
    part_a()
    ran_b = part_b()
    ran_c = part_c()
    print("RESULT: PASS (A%s%s)" % ("+B" if ran_b else "",
                                    "+C" if ran_c else ""))
