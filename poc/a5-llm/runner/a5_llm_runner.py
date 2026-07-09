#!/usr/bin/env python3
"""a5_llm_runner — the ONLY thing the GPU runs for the a5-llm head-to-head
(registry record registry/experiments/a5-llm.json; prereg anchor
docs/design-a5-llm.md sections 2-3).

RAW OUTPUT ONLY. This runner GENERATES the six LLM cells' free-form model
outputs and emits them in the `a5-llm-raw/1` runner contract:

  header line: {schema:"a5-llm-raw/1", experiment, arm, rung, model_revision,
                pack_sha256, decode_pins, gpu_class, batch_size,
                gpu_wall_seconds, usd, deterministic_repeat_identical}
  977 rows   : {qid, output_text, latency_ms, truncated, tokens_prompt,
                tokens_decode}

The raw files are consumed (verified + scored) by the pinned instrument
tools/experiments/a5_llm_instrument.py --score, which re-emits the pack from
the pinned corpora and REFUSES on any pack-digest / model-revision / decode-pin
mismatch with the raw header. This runner computes NO score, applies NO
threshold, renders NO verdict — it is the model-generation leg only (Opus
execution; docs/next/opus-execution-practices.md). The CPU arms
(engine/abstain-all/answer-all) are NOT run here; they are $0 CPU cells run
directly by the instrument (--arm ...).

DECODE (design section 2.1, pinned; verified at --score): greedy
(do_sample=False, temperature 0), max_new_tokens 512, context window 8192,
chat template as shipped with the pinned revision. Greedy makes every cell
deterministic given the pins; seed 0 is the registered placeholder.

TRUNCATION (design section 3.3, TRUNCATION_RULE, pinned): if the chat-templated
prompt token length + max_new_tokens exceeds the 8192 context window, record
lines are dropped from the TAIL of the final user turn's CONTEXT block, one at
a time, until it fits; the query is marked truncated=true and the per-cell
count is emitted (design expectation: 0-few; disclosed, never a stop).

SAFETY (f2b CellGuard precedent, correction-1 discipline): every cell runs
under a per-cell wall-clock timeout AND a whole-run GPU-hours guard; every
emitted row is flushed to disk immediately (append), so a stopped / timed-out /
crashed run leaves every completed cell's partial raw on disk instead of
hanging a GPU container silently. A breach self-terminates as a logged
ERR_CELL_TIMEOUT / ERR_RUN_GPU_BUDGET with partials on disk.

Usage:
  python3 a5_llm_runner.py --pack <pack.jsonl> --out-dir /tmp/a5 --device cuda \
      --gpu-class A10G                         # real (Modal)
  python3 a5_llm_runner.py --pack <pack.jsonl> --out-dir /tmp/a5 --mock  # stub, CPU, $0
  python3 a5_llm_runner.py --pack <pack.jsonl> --dry-plan --gpu-class A10G  # cost plan
  python3 a5_llm_runner.py ... --cells llm-direct:R1,llm-rag:R3            # subset (testing)

HARD RULES: --mock and --dry-plan spend $0 and never touch a GPU or the
network; mock outputs are labelled MOCK end-to-end and are never measurements;
real runs fail closed on any missing pin (ERR_*). RAW rows only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

# ---------------------------------------------------------------------------
# Pins — MUST byte-match tools/experiments/a5_llm_instrument.py (verified at
# --score). Copied deliberately so the container needs neither the instrument
# nor the corpora at run time (the pack carries prompt identity; its digest is
# re-verified against the frozen pack_sha256 both here and at --score).
# ---------------------------------------------------------------------------
RAW_SCHEMA = "a5-llm-raw/1"
PACK_SCHEMA = "a5-llm-prompt-pack/1"
EXPERIMENT = "a5-llm"
LLM_ARMS = ("llm-direct", "llm-rag")
RUNGS = ("R1", "R2", "R3")
CELLS = [(arm, rung) for arm in LLM_ARMS for rung in RUNGS]

MODEL_REVISIONS = {
    "R1": "HuggingFaceTB/SmolLM2-135M-Instruct@12fd25f77366fa6b3b4b768ec3050bf629380bac",
    "R2": "HuggingFaceTB/SmolLM2-360M-Instruct@a10cc1512eabd3dde888204e902eca88bddb4951",
    "R3": "HuggingFaceTB/SmolLM2-1.7B-Instruct@31b70e2e869a7173562077fd711b654946d38674",
}

# Byte-identical to a5_llm_instrument.DECODE_PINS (header equality is checked at
# --score via _json_roundtrip(DECODE_PINS)).
DECODE_PINS = {
    "do_sample": False,
    "temperature": 0.0,
    "max_new_tokens": 512,
    "context_window": 8192,
    "chat_template": "as shipped with the pinned revision",
}

GPU_USD_PER_HOUR = {"T4": 0.59, "A10G": 1.10, "A100": 2.10}  # analysis/a5_llm.py pins

# The final-user-turn CONTEXT marker the truncation rule drops lines from
# (byte-identical to a5_llm_instrument.context_block's non-empty header).
CTX_MARKER = "CONTEXT (records for the entities in this question):\n"
QUESTION_SEP = "\n\nQuestion: "

# SAFETY BOUNDS (f2b correction-1 analogue). Per-cell wall-clock budget by GPU
# class (~generous vs the dry-plan point estimate, far below the Modal function
# timeout); whole-run GPU-hours guard defaults to the registry gpu_hours_cap.
CELL_TIMEOUT_S_DEFAULT = {"A100": 3000.0, "A10G": 3600.0, "T4": 9000.0, "cpu": 600.0}
RUN_GPU_HOURS_GUARD_DEFAULT = 4.0  # == registry budget.gpu_hours_cap


class CellBudgetExceeded(Exception):
    def __init__(self, kind, cell, done, elapsed_s):
        super().__init__("%s in cell %s after %d rows, %.1fs"
                         % (kind, cell, done, elapsed_s))
        self.kind = kind
        self.cell = cell
        self.done = done
        self.elapsed_s = elapsed_s


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def utcnow():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _json_roundtrip(obj):
    return json.loads(json.dumps(obj))


# ---------------------------------------------------------------------------
# Pack loading (a5-llm-prompt-pack/1): header + per-(arm,qid) message lists.
# ---------------------------------------------------------------------------
def load_pack(pack_path, expect_sha=None):
    got = sha256_file(pack_path)
    if expect_sha and got != expect_sha:
        raise SystemExit("ERR_PACK_PIN: pack %s sha256 %s != expected %s"
                         % (pack_path, got, expect_sha))
    with open(pack_path, "r", encoding="utf-8") as f:
        lines = [ln for ln in f if ln.strip()]
    header = json.loads(lines[0])
    if header.get("schema") != PACK_SCHEMA:
        raise SystemExit("ERR_PACK_SCHEMA: %r != %s"
                         % (header.get("schema"), PACK_SCHEMA))
    if header.get("model_revisions") != MODEL_REVISIONS:
        raise SystemExit("ERR_PACK_MODELS: pack model_revisions != runner pins")
    if header.get("decode_pins") != _json_roundtrip(DECODE_PINS):
        raise SystemExit("ERR_PACK_DECODE: pack decode_pins != runner pins")
    by_arm = {a: [] for a in LLM_ARMS}
    for ln in lines[1:]:
        rec = json.loads(ln)
        arm = rec["arm"]
        if arm in by_arm:
            by_arm[arm].append(rec)
    for arm in LLM_ARMS:
        if not by_arm[arm]:
            raise SystemExit("ERR_PACK_ARM: no prompts for arm %s" % arm)
    return header, got, by_arm


# ---------------------------------------------------------------------------
# Truncation — design section 3.3 TRUNCATION_RULE, applied to the messages
# BEFORE chat-templating (the runner is the only place this rule executes; the
# instrument scores output_text only and records `truncated` from the row).
# ---------------------------------------------------------------------------
def encode_with_truncation(tok, messages, context_window, max_new_tokens):
    """Return (input_ids:list[int], truncated:bool, n_prompt_tokens:int)."""
    budget = context_window - max_new_tokens

    def enc(msgs):
        return tok.apply_chat_template(msgs, add_generation_prompt=True,
                                       tokenize=True)

    ids = enc(messages)
    if len(ids) <= budget:
        return ids, False, len(ids)

    # Locate the final user turn and its CONTEXT block (rag-with-records only).
    msgs = [dict(m) for m in messages]
    fu = len(msgs) - 1
    while fu >= 0 and msgs[fu].get("role") != "user":
        fu -= 1
    if fu < 0:
        return ids, True, len(ids)
    content = msgs[fu]["content"]
    if not content.startswith(CTX_MARKER):
        # No truncatable final-turn CONTEXT block (direct / empty-retrieval);
        # the rule has no lever here (these prompts are short in practice).
        return ids, True, len(ids)
    sep_idx = content.find(QUESTION_SEP, len(CTX_MARKER))
    if sep_idx == -1:
        return ids, True, len(ids)
    head = content[:len(CTX_MARKER)]            # includes trailing '\n'
    lines_block = content[len(CTX_MARKER):sep_idx]
    tail = content[sep_idx:]                     # '\n\nQuestion: ...'
    rec_lines = lines_block.split("\n")

    truncated = False
    while len(ids) > budget and rec_lines:
        rec_lines.pop()                          # drop TAIL record line
        truncated = True
        msgs[fu]["content"] = head + "\n".join(rec_lines) + tail
        ids = enc(msgs)
    return ids, truncated, len(ids)


# ---------------------------------------------------------------------------
# Backends — one interface: encode(messages)->(ids,trunc,ntok);
# generate_batch(list[ids])->list[(output_text, n_decode)].
# ---------------------------------------------------------------------------
class StubLM:
    """SYNTHETIC mechanics-only stand-in (mock; no torch). Deterministic
    output per qid; exercises the emit + a5-llm-raw contract end-to-end so the
    instrument's --score header/row checks are validated at $0. NEVER a
    measurement (labelled MOCK)."""

    name = "stub"

    def __init__(self, rung):
        self.rung = rung

    def count_tokens(self, text):
        return max(1, len(text) // 4)

    def encode(self, messages):
        toks = sum(self.count_tokens(m["content"]) for m in messages) + 8
        # emulate the truncation trigger deterministically on the biggest prompts
        trunc = toks + DECODE_PINS["max_new_tokens"] > DECODE_PINS["context_window"]
        return messages, trunc, toks

    _CHOICES = (
        '{"answer": ["urn:kotw:v0:code-fn-mock--x"]}',
        '{"refuse": "mock: unknown entity"}',
        '{"answer": true}',
        '{"answer": false}',
        'I cannot answer this question (mock).',
        'qwerty zzz',
    )

    def generate_batch(self, batch):
        out = []
        for ids in batch:
            messages = ids  # StubLM.encode returns messages as "ids"
            qkey = messages[-1]["content"]
            h = int(hashlib.sha256(("%s\x1f%s" % (self.rung, qkey)).encode()
                                   ).hexdigest()[:8], 16)
            text = self._CHOICES[h % len(self._CHOICES)]
            out.append((text, max(1, self.count_tokens(text))))
        return out


class HFLM:
    """Real path: SmolLM2 at the PINNED revision, greedy free-form generation
    over the pinned chat template. Left-padded batched decode; per-sequence
    greedy is deterministic given the pins (batching disclosed, design 3.5)."""

    def __init__(self, repo_at_rev, device):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        if "@" not in repo_at_rev:
            raise SystemExit("ERR_UNPINNED_MODEL: %r has no @revision" % repo_at_rev)
        repo, revision = repo_at_rev.split("@", 1)
        self.tok = AutoTokenizer.from_pretrained(repo, revision=revision)
        if self.tok.pad_token_id is None:
            self.tok.pad_token = self.tok.eos_token
        self.tok.padding_side = "left"
        self.model = AutoModelForCausalLM.from_pretrained(
            repo, revision=revision, torch_dtype=torch.float16)
        self.model.to(device)
        self.model.eval()
        for p in self.model.parameters():
            p.requires_grad_(False)
        self.device = device
        self.torch = torch
        self.name = "%s@%s" % (repo, revision[:8])
        self.max_new = DECODE_PINS["max_new_tokens"]

    def count_tokens(self, text):
        return len(self.tok.encode(text, add_special_tokens=False))

    def encode(self, messages):
        return encode_with_truncation(self.tok, messages,
                                      DECODE_PINS["context_window"], self.max_new)

    def generate_batch(self, batch):
        """batch: list[list[int]] (already-encoded, possibly-truncated prompts).
        Returns list[(output_text, n_decode_tokens)] in the same order."""
        torch = self.torch
        pad_id = self.tok.pad_token_id
        eos_id = self.tok.eos_token_id
        maxlen = max(len(ids) for ids in batch)
        input_ids = torch.full((len(batch), maxlen), pad_id, dtype=torch.long)
        attn = torch.zeros((len(batch), maxlen), dtype=torch.long)
        for i, ids in enumerate(batch):
            input_ids[i, maxlen - len(ids):] = torch.tensor(ids, dtype=torch.long)
            attn[i, maxlen - len(ids):] = 1
        input_ids = input_ids.to(self.device)
        attn = attn.to(self.device)
        with torch.no_grad():
            out = self.model.generate(
                input_ids=input_ids, attention_mask=attn,
                do_sample=False, num_beams=1, max_new_tokens=self.max_new,
                pad_token_id=pad_id)
        gen = out[:, maxlen:]  # left-padding => new tokens start at maxlen
        results = []
        for i in range(gen.shape[0]):
            row = gen[i].tolist()
            # decode length = up to and including the first eos (else full)
            if eos_id is not None and eos_id in row:
                n_dec = row.index(eos_id) + 1
            else:
                n_dec = len(row)
            text = self.tok.decode(gen[i], skip_special_tokens=True).strip()
            results.append((text, n_dec))
        return results


# ---------------------------------------------------------------------------
# Batching — group prompts so padded (batch_size x max_len) stays under a token
# budget; sort by length descending so an OOM shows on the first (largest)
# batch. Emission order is irrelevant (the instrument keys rows by qid).
# ---------------------------------------------------------------------------
def make_batches(encoded, batch_size, token_budget):
    """encoded: list[(qid, ids, truncated, n_tok)] -> list[list[same]]."""
    items = sorted(encoded, key=lambda e: len(e[1]), reverse=True)
    batches, cur, cur_max = [], [], 0
    for it in items:
        L = len(it[1])
        nxt_max = max(cur_max, L)
        if cur and (len(cur) >= batch_size or (len(cur) + 1) * nxt_max > token_budget):
            batches.append(cur)
            cur, cur_max = [], 0
            nxt_max = L
        cur.append(it)
        cur_max = nxt_max
    if cur:
        batches.append(cur)
    return batches


# ---------------------------------------------------------------------------
# One cell -> one a5-llm-raw/1 file (header + 977 rows), flushed per batch.
# ---------------------------------------------------------------------------
def run_cell(lm, arm, rung, prompts, pack_sha, gpu_class, batch_size,
             token_budget, out_dir, mock, cell_timeout_s, det_check_n, log,
             run_deadline_mono):
    cell = "%s/%s" % (arm, rung)
    raw_path = os.path.join(out_dir, "a5-llm-raw-%s-%s.jsonl" % (arm, rung))
    # encode (+ truncate) every prompt first
    encoded, n_trunc = [], 0
    for rec in prompts:
        ids, trunc, ntok = lm.encode(rec["messages"])
        n_trunc += 1 if trunc else 0
        encoded.append((rec["qid"], ids, trunc, ntok))
    batches = make_batches(encoded, batch_size, token_budget)

    t0 = time.monotonic()
    rows_by_qid = {}
    header = {
        "schema": RAW_SCHEMA, "experiment": EXPERIMENT, "arm": arm, "rung": rung,
        "model_revision": MODEL_REVISIONS[rung], "pack_sha256": pack_sha,
        "decode_pins": _json_roundtrip(DECODE_PINS), "gpu_class": gpu_class,
        "batch_size": batch_size, "seed": 0,
        "runner": "a5_llm_runner", "mock": bool(mock),
    }
    # write a provisional header first so partials are self-describing; the
    # header is rewritten with gpu_wall_seconds/usd/determinism at the end.
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(dict(header, gpu_wall_seconds=0.0, usd=0.0,
                                deterministic_repeat_identical=None,
                                status="in-progress"), sort_keys=True) + "\n")

    done = 0
    for bi, batch in enumerate(batches):
        if time.monotonic() - t0 > cell_timeout_s:
            _flush_timeout(raw_path, header, cell, done, time.monotonic() - t0,
                           "ERR_CELL_TIMEOUT")
            raise CellBudgetExceeded("wall-clock timeout (%.0fs)" % cell_timeout_s,
                                     cell, done, time.monotonic() - t0)
        if run_deadline_mono is not None and time.monotonic() > run_deadline_mono:
            _flush_timeout(raw_path, header, cell, done, time.monotonic() - t0,
                           "ERR_RUN_GPU_BUDGET")
            raise CellBudgetExceeded("whole-run GPU-hours guard", cell, done,
                                     time.monotonic() - t0)
        tb = time.monotonic()
        outs = lm.generate_batch([ids for (_q, ids, _t, _n) in batch])
        dt = time.monotonic() - tb
        per = dt / max(1, len(batch))
        with open(raw_path, "a", encoding="utf-8") as f:
            for (qid, ids, trunc, ntok), (text, ndec) in zip(batch, outs):
                row = {"qid": qid, "output_text": text,
                       "latency_ms": round(per * 1000.0, 3),
                       "truncated": bool(trunc),
                       "tokens_prompt": int(ntok), "tokens_decode": int(ndec)}
                rows_by_qid[qid] = row
                f.write(json.dumps(row, sort_keys=True) + "\n")
                f.flush()
            os.fsync(f.fileno())
        done += len(batch)
        if bi % 10 == 0 or done == len(encoded):
            log("cell %s: %d/%d rows (%.1fs, %d trunc so far)"
                % (cell, done, len(encoded), time.monotonic() - t0, n_trunc))

    gpu_wall = time.monotonic() - t0
    # determinism spot-check: regenerate a small fixed subset twice, identically,
    # and compare (a run-to-run reproducibility signal for greedy decode; the
    # field is descriptive for LLM cells, not a verdict gate).
    det_ok, det_n = _determinism_check(lm, encoded, det_check_n)

    usd = gpu_wall * GPU_USD_PER_HOUR.get(gpu_class, 0.0) / 3600.0
    final_header = dict(header, gpu_wall_seconds=round(gpu_wall, 3),
                        usd=round(usd, 6),
                        deterministic_repeat_identical=det_ok,
                        determinism_check_n=det_n,
                        truncation_count_runner=n_trunc)
    # rewrite the file with the finalized header + all rows in pack order
    order = [rec["qid"] for rec in prompts]
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(final_header, sort_keys=True) + "\n")
        for qid in order:
            f.write(json.dumps(rows_by_qid[qid], sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())
    log("cell %s DONE: %d rows, %d truncated, gpu_wall=%.1fs, usd~%.4f, det=%s"
        % (cell, len(order), n_trunc, gpu_wall, usd, det_ok))
    return {"arm": arm, "rung": rung, "raw_file": os.path.basename(raw_path),
            "n_rows": len(order), "truncation_count": n_trunc,
            "gpu_wall_seconds": round(gpu_wall, 3), "usd": round(usd, 6),
            "deterministic_repeat_identical": det_ok}


def _determinism_check(lm, encoded, n):
    if n <= 0 or not encoded:
        return None, 0
    subset = [ids for (_q, ids, _t, _nt) in encoded[:n]]
    try:
        a = lm.generate_batch(subset)
        b = lm.generate_batch(subset)
    except Exception:  # noqa: BLE001 — determinism probe never aborts a cell
        return None, 0
    return ([t for t, _ in a] == [t for t, _ in b]), len(subset)


def _flush_timeout(raw_path, header, cell, done, elapsed, code):
    marker = os.path.join(os.path.dirname(raw_path), "RUNNER_ERROR.json")
    with open(marker, "w", encoding="utf-8") as f:
        json.dump({"code": code, "cell": cell, "rows_flushed": done,
                   "elapsed_s": round(elapsed, 1),
                   "note": "INSTRUMENT event: cell self-terminated at its safety "
                           "bound; partial rows are on disk, nothing fabricated"},
                  f, indent=2, sort_keys=True)
        f.write("\n")


# ---------------------------------------------------------------------------
# --dry-plan: real-run cost plan vs caps. Stdlib only; data-driven off the pack
# (actual prompt_chars per arm); ESTIMATES only, never a measurement.
# ---------------------------------------------------------------------------
def dry_plan(pack_path, manifest, gpu):
    header, _sha, by_arm = load_pack(pack_path)
    pl = manifest["planning"]
    cpt = pl["chars_per_token_estimate"]
    avg_dec = pl["avg_decode_tokens_estimate"]
    prefill = pl["prefill_tok_per_s"][gpu]
    decode = pl["decode_tok_per_s"][gpu]
    overhead = pl["overhead_factor"]
    usd_h = manifest["flop_accounting"]["usd_per_hour"][gpu]
    cap = manifest["budget"]
    n = header["n_queries"]

    prompt_tok = {a: sum(r["prompt_chars"] for r in by_arm[a]) / cpt for a in LLM_ARMS}
    hours = 0.0
    rows = []
    for arm, rung in CELLS:
        pt = prompt_tok[arm]
        dt = n * avg_dec
        h = pt / prefill[rung] / 3600.0 + dt / decode[rung] / 3600.0
        hours += h
        rows.append((arm, rung, pt, dt, h))
    worst = hours * overhead
    lines = [
        "a5-llm --dry-plan (ESTIMATES ONLY — planning constants from",
        "a5-llm-manifest.json; no GPU, no network, $0 spent by this command)",
        "",
        "pack: %s prompts (%d queries x 2 arms), avg_decode est %d tok, cap %d"
        % (header["n_prompts"], n, avg_dec, DECODE_PINS["max_new_tokens"]),
        "prompt tokens/cell (est): llm-direct %.0f, llm-rag %.0f"
        % (prompt_tok["llm-direct"], prompt_tok["llm-rag"]),
        "",
        "GPU-hours estimate on %s (prefill %s, decode %s tok/s):"
        % (gpu, prefill, decode),
    ]
    for arm, rung, pt, dt, h in rows:
        lines.append("  %-11s %s  %.3f h" % (arm, rung, h))
    lines += [
        "  total point estimate            %.3f h" % hours,
        "  with %.1fx overhead             %.3f h" % (overhead, worst),
        "",
        "cost at Modal list $%.2f/h (%s):" % (usd_h, gpu),
        "  point estimate  $%.2f" % (hours * usd_h),
        "  worst case      $%.2f" % (worst * usd_h),
        "  hard ceiling    $%.2f  (gpu_hours_cap %d h x $%.2f/h)"
        % (cap["gpu_hours_cap"] * usd_h, cap["gpu_hours_cap"], usd_h),
        "",
        "caps: usd_cap $%d, gpu_hours_cap %d h, wall_clock_cap %d h, tier_cap $%d"
        % (cap["usd_cap"], cap["gpu_hours_cap"], cap["wall_clock_cap_hours"],
           cap["tier_cap_usd"]),
        "",
    ]
    checks = [
        ("worst case vs usd_cap ($%d)" % cap["usd_cap"], worst * usd_h <= cap["usd_cap"]),
        ("hard ceiling vs tier_cap ($%d)" % cap["tier_cap_usd"],
         cap["gpu_hours_cap"] * usd_h <= cap["tier_cap_usd"]),
        ("worst case vs gpu_hours_cap (%d h)" % cap["gpu_hours_cap"],
         worst <= cap["gpu_hours_cap"]),
    ]
    for name, ok in checks:
        lines.append("  %-40s %s" % (name, "OK" if ok else "OVER — DO NOT LAUNCH"))
    lines.append("")
    lines.append("NOTE: max_new_tokens=512 + the per-cell CellGuard + the whole-run")
    lines.append("GPU-hours guard bound the worst case even if decode over-runs.")
    print("\n".join(lines))
    return all(ok for _n, ok in checks)


# ---------------------------------------------------------------------------
def parse_cells(spec):
    if not spec:
        return list(CELLS)
    out = []
    for tok in spec.split(","):
        arm, rung = tok.split(":")
        if (arm, rung) not in CELLS:
            raise SystemExit("ERR_CELLS: %r not a valid arm:rung" % tok)
        out.append((arm, rung))
    return out


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--pack", default=os.path.join(here, "..", "inputs",
                                                    "a5-llm-pack.jsonl"))
    ap.add_argument("--manifest", default=os.path.join(here, "..", "inputs",
                                                       "a5-llm-manifest.json"))
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--gpu-class", default="A10G", choices=["T4", "A10G", "A100"])
    ap.add_argument("--cells", default="", help="subset, e.g. llm-direct:R1,llm-rag:R3")
    ap.add_argument("--batch-size", type=int, default=None)
    ap.add_argument("--token-budget", type=int, default=None)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--dry-plan", action="store_true")
    ap.add_argument("--cell-timeout-s", type=float, default=None)
    ap.add_argument("--max-gpu-hours", type=float, default=None,
                    help="whole-run GPU-hours guard (default: manifest budget)")
    ap.add_argument("--det-check-n", type=int, default=8)
    args = ap.parse_args()

    with open(args.manifest, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    if args.dry_plan:
        ok = dry_plan(args.pack, manifest, args.gpu_class)
        sys.exit(0 if ok else 2)

    if not args.out_dir:
        raise SystemExit("ERR_ARGS: --out-dir required (unless --dry-plan)")
    os.makedirs(args.out_dir, exist_ok=True)
    t_start = time.time()

    def log(msg):
        print("[a5-llm %7.1fs] %s" % (time.time() - t_start, msg), flush=True)

    expect_sha = manifest.get("pack_sha256")
    header, pack_sha, by_arm = load_pack(args.pack, expect_sha)
    cells = parse_cells(args.cells)
    batch_size = args.batch_size or manifest["batching"]["default_batch_size"]
    token_budget = args.token_budget or manifest["batching"]["token_budget"]
    cell_timeout = (args.cell_timeout_s
                    if args.cell_timeout_s is not None
                    else CELL_TIMEOUT_S_DEFAULT["cpu" if args.mock else args.gpu_class])
    max_gpu_h = (args.max_gpu_hours if args.max_gpu_hours is not None
                 else manifest["budget"].get("gpu_hours_cap", RUN_GPU_HOURS_GUARD_DEFAULT))
    run_deadline = None if args.mock else time.monotonic() + max_gpu_h * 3600.0

    label = "MOCK" if args.mock else "FULL"
    log("mode=%s device=%s gpu_class=%s cells=%d batch=%d token_budget=%d "
        "pack_sha=%s..." % (label, args.device, args.gpu_class, len(cells),
                            batch_size, token_budget, pack_sha[:12]))
    if not args.mock and args.device != "cuda":
        log("WARNING: real run requested on CPU — allowed but slow")

    summaries = []
    lms = {}

    def lm_for(rung):
        if rung not in lms:
            lms[rung] = StubLM(rung) if args.mock else HFLM(MODEL_REVISIONS[rung],
                                                            args.device)
            log("loaded backend for %s: %s" % (rung, lms[rung].name))
        return lms[rung]

    try:
        # group cells by rung so each model loads once (R1 then R2 then R3)
        for rung in RUNGS:
            rung_cells = [(a, r) for (a, r) in cells if r == rung]
            if not rung_cells:
                continue
            lm = lm_for(rung)
            for arm, _r in rung_cells:
                summaries.append(run_cell(
                    lm, arm, rung, by_arm[arm], pack_sha, args.gpu_class,
                    batch_size, token_budget, args.out_dir, args.mock,
                    cell_timeout, args.det_check_n, log, run_deadline))
            # free the model before the next rung (bound peak GPU memory)
            if not args.mock:
                try:
                    import torch
                    del lms[rung]
                    lms.pop(rung, None)
                    torch.cuda.empty_cache()
                except Exception:  # noqa: BLE001
                    pass
    except CellBudgetExceeded as e:
        log("ERR: %s — run aborted in bounded time; partial raws on disk in %s"
            % (e, args.out_dir))
        _write_results(args, manifest, header, pack_sha, summaries, t_start,
                       outcome="ABORTED-SAFETY-BOUND", label=label)
        raise SystemExit("ERR_CELL_TIMEOUT: %s" % e)

    _write_results(args, manifest, header, pack_sha, summaries, t_start,
                   outcome=("MOCK-HARNESS-COMPLETE" if args.mock
                            else "HARNESS-COMPLETE"), label=label)
    log("OUTCOME: %s (%d cells)"
        % ("MOCK-HARNESS-COMPLETE" if args.mock else "HARNESS-COMPLETE",
           len(summaries)))


def _write_results(args, manifest, header, pack_sha, summaries, t_start,
                   outcome, label):
    res = {
        "experiment": EXPERIMENT,
        "outcome": outcome,
        "outcome_note": "raw a5-llm-raw/1 cells only — NO score/verdict; the "
                        "verdict is computed by the pinned instrument --score + "
                        "analysis/a5_llm.py + verdict-gen under run-vs-audit "
                        "separation",
        "mode": label,
        "date": utcnow(),
        "device": args.device,
        "gpu_class": args.gpu_class,
        "pack_sha256": pack_sha,
        "model_revisions": (MODEL_REVISIONS if not args.mock
                            else {"note": "MOCK — synthetic stub, no models loaded"}),
        "decode_pins": DECODE_PINS,
        "cells": summaries,
        "n_cells": len(summaries),
        "total_gpu_wall_seconds": round(sum(s["gpu_wall_seconds"] for s in summaries), 3),
        "total_usd_est": round(sum(s["usd"] for s in summaries), 6),
        "wall_clock_seconds": round(time.time() - t_start, 3),
    }
    suffix = "-mock" if args.mock else ""
    with open(os.path.join(args.out_dir, "results-a5-llm%s.json" % suffix),
              "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    main()
