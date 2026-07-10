# truthstyle-2x2 — §7.3 blinding-audit clarification (hex-identifier false positive)

> STATUS: ratified 2026-07-10 by FABLE (experiment-designer role; record author
> pseudonym writer-1, register owner designer-1). Ratification record:
> `registry/corrections/truthstyle-2x2/1-blinding-audit-clarification.json`.
> Registered stipulations: ASM-0360 (clarified matching rule), ASM-0361
> (void-and-restart). The FROZEN record
> `registry/experiments/truthstyle-2x2.json` (frozen_sha256 `18893369…`) is
> byte-untouched. ALL 8 staged harness-manifest files (including
> `judges-invocation.md`) are byte-untouched — the one-shot pin discipline of
> amendment seq 1 is intact. The ONLY code change is to the UNPINNED mechanical
> executor `poc/truthstyle-2x2/run-dts-judges.py` (not one of the 8 staged
> files; not named in any pin), per §4 below.

## 1. What happened (measured)

- All three §8 preflights PASSED and the three main passes launched
  concurrently [MEASURED: poc/truthstyle-2x2/opus-runs/20260710T115128Z/
  preflight-status-p{1,2,3}.json, all `"pass": true`].
- judge-p3 ABORTED at position 16 of 808 with
  `ERR_DTS_BLINDING: token 'f2b' in events.jsonl (spec §7.3)`. The matched
  bytes are inside the machine-generated Claude Code session UUID
  `cdf6ab6f-ab88-4fc7-a1a8-f2b8d1b64df9` (final hex segment `f2b8d1b64df9`),
  repeated on every stream-json event line of that attempt
  [MEASURED: …/judge-p3-haiku45/items/pos-016/c1_t0/events.jsonl;
  …/judge-p3-stdout.log last line].
- judge-p1 and judge-p2 were stopped externally after ~69 and ~55 items with
  no blinding hit of their own [MEASURED: …/judge-p{1,2}-gpt56sol|gpt55/items/
  directory counts; main-progress.log tails].
- The per-item `user-prompt.txt` was byte-clean everywhere (structural
  blinding intact); the ONLY §7.3 matches anywhere are inside hexadecimal
  identifier runs [MEASURED: repo-wide grep over the run dir, 2026-07-10:
  exactly one matching file, the pos-016 events.jsonl above].
- NO label ever materialized: `data/d-ts-labels/` does not exist; the runner
  writes per-pass responses only at pass END, and no pass completed. The abort
  surfaced only the token name and file basename — no judgment content was
  read by any deciding agent. Unblinding state: pre.

## 2. The defect: a detector false-positive channel, not a leak

`f2b` is the only one of the four §7.3 tokens whose bytes are all valid
hexadecimal (`kernel`, `nsm`, `truthstyle` each contain letters outside
`[a-f]`, so they can NEVER occur inside a hex string). Vendor harnesses emit
hex identifiers on every call: codex writes a UUID `thread_id` per item
[MEASURED: …/judge-p1-gpt56sol/items/pos-001/c1_t0/events.jsonl,
`thread_id":"019f4bdf-1094-79f3-9620-00d4a44ee2d7"`]; Claude Code stream-json
repeats the session UUID on every event line plus a fresh per-event `uuid`.

A UUID's 32 hex characters contain ~22 3-character windows inside its five
segments, so P(`f2b` in one UUID) ≈ 22/4096 ≈ 0.5%. With ≥1 UUID per codex
item and ≥6 distinct UUIDs per p3 item, the expected number of coincidental
hits per 808-item pass is ≈ 4–6 (codex) and ≈ 25+ (p3): under a PERFECTLY
blind harness, the literal-substring scan aborts every campaign of this shape
with probability ≈ 1 (observed: p3 died at item 16). A control that fires
with near-certainty under the null detects nothing — the clarification below
RESTORES the §7.3 control's discriminative power; it does not relax it.
The runner behaved correctly in refusing to self-modify a pinned control
(boundary stop to Fable, per the frozen stage discipline).

## 3. The ratified rule (normative)

DECISION: §7.3 matching is clarified as follows [STIPULATED: ASM-0360]:

> The §7.3 scan remains a case-insensitive byte scan of `user-prompt.txt`,
> `events.jsonl`, and `stderr.log` for the four pinned tokens, abort-on-hit.
> A match of a token counts as a HIT unless BOTH: (i) the token consists
> entirely of hexadecimal characters `[0-9a-f]`, and (ii) the match lies
> strictly inside a longer maximal run of `[0-9a-f]` bytes (i.e. the byte
> immediately before or immediately after the match is itself in `[0-9a-f]`).
> Within the pinned token set this affects ONLY `f2b`; matching for `kernel`,
> `nsm`, and `truthstyle` is byte-identical to the original scan.

Why this preserves §7.3's intent (leak detection), stated against the two
leak classes the spec names:

- **A judge echoing a project term** or **a harness field surfacing project
  context**: every real spelling of the tokens in project artifacts —
  `f2b`, `f2b-transfer`, `f2b-replicate`, `f2b-errors`, path fragments like
  `kernel-of-truth` or `poc/truthstyle-2x2` — delimits the token with
  non-hex bytes (`-`, `/`, `_`, space, quote), so the clarified scan still
  fires on all of them. The three non-hex tokens (which carry the project
  name and the experiment name) are entirely unaffected.
- **Sensitivity witness**: the codex argv includes the repo-absolute
  `--output-schema` path (contains both `truthstyle` and the repo name); had
  either vendor surface echoed argv into captured events, the scan would have
  fired on a NON-hex token — 124 captured codex attempts show it did not,
  and that sensitivity is unchanged.

Why this option and not the two runner-proposed alternatives:

- (a) *excluding identifier-field values* (session_id/thread_id/uuid/…): would
  require JSON-parsing surfaces that are not JSON (stderr.log), pinning a
  vendor field-name list that drifts across CLI versions, and would blind the
  audit to a leak INSIDE an excluded field value — a strictly larger blind
  spot than the hex-run rule.
- naive *word-boundary matching* for all tokens: weakens matching for the
  three non-hex tokens too (e.g. `truthstyle2x2` would stop matching), where
  NO false-positive channel exists. The ratified rule is the narrowest edit
  that closes the coincidence channel: it modifies matching only where the
  channel is (fully-hex token embedded in a hex run) and leaves everything
  else byte-identical.

## 4. Exact `blinding_scan` change (the coordinator implements this verbatim)

In `poc/truthstyle-2x2/run-dts-judges.py`, replace the existing
`blinding_scan` function (and add the two helpers) with exactly:

```python
# §7.3 blinding audit tokens (case-insensitive)
BLIND_TOKENS = (b"kernel", b"nsm", b"truthstyle", b"f2b")
# §7.3 matching clarified per poc/truthstyle-2x2/blinding-audit-clarification.md
# + registry/corrections/truthstyle-2x2/1-blinding-audit-clarification.json
# (ASM-0360): a token that is itself entirely hexadecimal ("f2b") is a HIT only
# as a standalone token — NOT when embedded inside a longer maximal [0-9a-f]
# run, where it is arithmetic coincidence inside a machine-generated identifier
# (session/thread/request UUIDs, per-event ids). Tokens containing non-hex
# letters can never sit inside a hex run; their matching is byte-identical to
# the original scan.
_HEX_BYTES = frozenset(b"0123456789abcdef")


def _hex_embedded(data, i, n):
    """True iff data[i:i+n] sits inside a [0-9a-f] run longer than itself."""
    return ((i > 0 and data[i - 1] in _HEX_BYTES)
            or (i + n < len(data) and data[i + n] in _HEX_BYTES))


def blinding_scan(paths):
    for p in paths:
        if not os.path.exists(p):
            continue
        data = open(p, "rb").read().lower()
        for t in BLIND_TOKENS:
            pure_hex = all(c in _HEX_BYTES for c in t)
            i = data.find(t)
            while i >= 0:
                if not (pure_hex and _hex_embedded(data, i, len(t))):
                    return (os.path.basename(p), t.decode())
                i = data.find(t, i + 1)
    return None
```

Function signature, return contract, call sites (`do_attempt`), the abort
message, the token list, the scanned surfaces, and every other tripwire
(§7.1, §7.2, §7.4, §7.5) are unchanged. Nothing else in the runner changes.

## 5. Post-pass audit sweep (normative; mechanical)

After the three restarted passes complete and BEFORE the d-ts-labels ops
amendment is written, the coordinator commits
`poc/truthstyle-2x2/blinding-sweep.py` with exactly the logic below and runs
it over the completed run dir; its output `blinding-sweep.json` is committed
into the opus-run provenance dir. GREEN requires `clarified_hits == []`.
Every exclusion is listed with its surrounding maximal hex run, so the Codex
auditor can verify each one is a machine identifier by inspection — and can
independently re-run BOTH the strict and clarified scans over the retained
attempt bytes (nothing is deleted; the clarification is fully re-derivable).

```python
#!/usr/bin/env python3
"""blinding-sweep — post-pass §7.3 audit sweep (blinding-audit-clarification.md §5).
usage: blinding-sweep.py <run_dir>   -> writes <run_dir>/blinding-sweep.json"""
import importlib.util, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rdj", os.path.join(HERE, "run-dts-judges.py"))
rdj = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rdj)
HEX = rdj._HEX_BYTES

def hex_embedded_occurrences(data, token):
    out, i = [], data.find(token)
    while i >= 0:
        j0, j1 = i, i + len(token)
        while j0 > 0 and data[j0 - 1] in HEX:
            j0 -= 1
        while j1 < len(data) and data[j1] in HEX:
            j1 += 1
        if (j0, j1) != (i, i + len(token)):
            out.append({"offset": i, "hex_run": data[j0:j1].decode()})
        i = data.find(token, i + 1)
    return out

def main(run_dir):
    hits, exclusions = [], []
    for dirpath, _, names in sorted(os.walk(run_dir)):
        for name in sorted(names):
            if name not in ("user-prompt.txt", "events.jsonl", "stderr.log"):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, run_dir)
            if rdj.blinding_scan([path]):
                hits.append(rel)
            data = open(path, "rb").read().lower()
            for t in rdj.BLIND_TOKENS:
                if not all(c in HEX for c in t):
                    continue
                for occ in hex_embedded_occurrences(data, t):
                    occ.update({"file": rel, "token": t.decode()})
                    exclusions.append(occ)
    out = {"run_dir": os.path.basename(run_dir.rstrip("/")),
           "clarified_hits": hits, "n_exclusions": len(exclusions),
           "exclusions": exclusions,
           "verdict": "GREEN" if not hits else "RED"}
    with open(os.path.join(run_dir, "blinding-sweep.json"), "w") as f:
        f.write(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(out["verdict"], "hits=%d exclusions=%d" % (len(hits), len(exclusions)))
    sys.exit(0 if not hits else 1)

if __name__ == "__main__":
    main(sys.argv[1])
```

## 6. Residual risk (disclosed)

The clarified rule reduces sensitivity for exactly one shape: the literal
bytes `f2b` immediately adjacent to a hex character `[0-9a-f]`. Repo census
[MEASURED: repo-wide grep `[0-9a-f]f2b|f2b[0-9a-f]` over committed docs/,
registry/, poc/, tools/, analysis/, data/d-ts, 2026-07-10]: every such
adjacency in committed bytes lies inside a 40/64-char hex digest (e.g.
`28874f2b…`, `aee019c7ef2b…`) — digests name nothing a blind judge could
read as project context — except the single scratch filename
`f2be-mock-cells.jsonl` (an f2b-errors mock artifact name in the design doc),
which has no path into any truthstyle judge invocation surface. Accepted and
disclosed; the §11 structural blinding (empty out-of-repo workdir, no repo
strings in the judge-visible prompt bytes) is the primary control and is
unchanged.

## 7. Void-and-restart ruling

DECISION: the aborted run `opus-runs/20260710T115128Z` is VOID for labels and
retained as provenance; the campaign RESTARTS from item 1 for all three
judges (fresh full protocol: §8 preflight then §3-ordered main pass) in a new
run dir, under the clarified runner committed BEFORE launch
[STIPULATED: ASM-0361].

- No resume: the spec defines no resume mechanism, and inventing one would be
  runner improvisation over unpinned state. Void-whole-passes is the §7.5
  discipline's own shape (an aborted pass writes no responses by
  construction).
- No selection effect: no label from the void run was ever assembled, written,
  or read (§1) — restarting cannot condition on outcomes. The first ~69/55/16
  items are judged a second time with the first samples discarded UNREAD;
  this re-sampling is disclosed, and its magnitude is bounded by the
  ASM-0241 interface-maximal-determinism discharge and the frozen retest gate
  (agreement ≥ 0.85 over ≥ 48 duplicate judgments).
- The coordinator records `sha256(run-dts-judges.py)` in the new run dir
  before launch, so the audited pass is bound to the clarified executor
  bytes. Budget: the ~140 discarded calls are inside the frozen caps
  (usd_cap 40; measured p3 burn ≈ 0.0002–0.003 USD/call).

## 8. What is NOT changed

Abort-on-hit semantics; the four-token list; the three scanned surfaces; the
`user-prompt.txt` byte-equality requirement; tripwires §7.1/§7.2/§7.4/§7.5;
the frozen record and all its pins; all 8 staged harness-manifest files and
the amendment-1 harness_manifest value; item bytes, seeds, judge order, and
the analysis pipeline. This is a false-positive clarification of the audit's
matching predicate, ratified pre-data at the harness-executor level.
