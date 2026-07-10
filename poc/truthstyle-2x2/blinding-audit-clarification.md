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
>
> AMENDED 2026-07-10 (same day, later session) by AMENDMENT A1 (§9 below;
> ratification record
> `registry/corrections/truthstyle-2x2/4-blinding-audit-amendment-a1.json`;
> stipulations ASM-0660 matching-rule extension, ASM-0661 p3-only re-run).
> A1 supersedes, IN PART, the §3 side-statement that matching for the three
> non-hex tokens "is byte-identical to the original scan" (it now carries one
> further exclusion, on the two harness-captured surfaces only) and supersedes
> the §4 and §5 normative code blocks with the §9.5 forms. Everything else in
> §§1–8 stands.

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

- DECISION: the aborted run `opus-runs/20260710T115128Z` is VOID for labels
  and retained as provenance; the campaign RESTARTS from item 1 for all three
  judges (fresh full protocol: §8 preflight then §3-ordered main pass) in a
  new run dir, under the clarified runner committed BEFORE launch
  [STIPULATED: ASM-0361]. (Reflowed to a hanging-indent bullet by amendment
  A1 for the epistemic-tag lint — words unchanged.)

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

---

## 9. AMENDMENT A1 (2026-07-10): base62 vendor-identifier coincidence — 'nsm' inside an Anthropic request_id

> Ratified 2026-07-10 by FABLE (experiment-designer role; record author
> pseudonym writer-1, register owner designer-1). Ratification record:
> `registry/corrections/truthstyle-2x2/4-blinding-audit-amendment-a1.json`.
> Registered stipulations: ASM-0660 (vendor-id-literal exclusion),
> ASM-0661 (p3-only re-run + pos-102 no-scrub). The frozen record and all 8
> staged harness-manifest files remain byte-untouched; the changed files are
> again ONLY the unpinned mechanical executor `run-dts-judges.py` and the
> coordinator-level audit tool `blinding-sweep.py`.

### 9.1 What happened (measured)

- The restarted campaign `opus-runs/20260710T151231Z` (per ASM-0361) ran
  judge-p1 and judge-p2 to COMPLETION, 808/808 each, with no blinding hit of
  their own [MEASURED: …/run-summary-p1.json, …/run-summary-p2.json;
  …/blinding-sweep.json exclusions list].
- judge-p3 ABORTED at position 102 of 808 with
  `ERR_DTS_BLINDING: token 'nsm' in events.jsonl (spec §7.3)`. The matched
  bytes are at offset 1959 of the pos-102 events.jsonl, inside the
  Anthropic-generated identifier `"request_id":"req_011Cctc1sK9P4SujinnsMiWU"`
  — lowercased, the base62 tail reads `…sujin`+`nsm`+`iwu` [MEASURED:
  …/judge-p3-haiku45/items/pos-102/c1_t0/events.jsonl, sha256
  `1b8d624be5118804d7027d0b58086e6aa6328a43afeb28ca827e1a0394dd72b7`].
- The item is byte-clean (`user-prompt.txt` = the "steamfitter" question
  bytes; no token anywhere in it); the model's whole answer was the single
  word `no`; the §7.2 identity fields are clean; p1 and p2 judged the same
  item without incident [MEASURED: the same events.jsonl init/assistant/
  result events; …/judge-p3-haiku45/items/pos-102/c1_t0/user-prompt.txt].
- No p3 label was ever assembled, written, or read: `data/d-ts-labels/`
  contains only the p1/p2 responses files (responses are written only at pass
  END, and the p3 pass never ended) [MEASURED: data/d-ts-labels/ directory
  listing 2026-07-10]. Unblinding state: pre. The abort happened at ~15:21,
  before any usage-cap event.
- The pre-A1 sweep over the dir shows exactly 5 tolerated `f2b` hex-run
  exclusions (2 in p2 thread UUIDs, 3 in p3 session/event UUIDs) and this ONE
  clarified hit [MEASURED: opus-runs/20260710T151231Z/blinding-sweep.json,
  verdict RED, n_exclusions 5].

### 9.2 The defect: ASM-0360's coincidence premise fails for base62 identifiers

ASM-0360 closed the coincidence channel for hex identifiers on the stated
ground that the other three tokens "contain letters outside `[a-f]`, so they
can NEVER occur inside a hex string" — true, and still true. But hex UUIDs
are not the only machine identifiers on the p3 surface: the Anthropic API
stamps every captured attempt with TWO base62 identifiers (`"id":"msg_…"`,
`"request_id":"req_…"`), each a lowercase 4-byte prefix plus a 24-character
mixed-case alphanumeric tail [MEASURED: every p3 events.jsonl in both run
dirs; all observed tails are exactly 24 chars]. Base62 tails can spell ANY
pinned token by arithmetic coincidence:

- `nsm` (3 letters, case-insensitive): p ≈ 22 windows × (2/62)³ ≈ 7.4e-4 per
  id; ≈ 1,620 such ids per 808-item pass ⇒ expected ≈ 1.2 coincidental hits
  per PERFECTLY BLIND p3 pass, i.e. the pre-A1 scan aborts a clean pass with
  probability ≈ 0.7 (observed: died once, at pos-102).
- `f2b` inside a base62 tail flanked by non-hex bytes escapes the ASM-0360
  hex-run exclusion (expected ≈ 0.25 per pass) — a second, latent channel of
  the same shape.
- `kernel` / `truthstyle` (6/10 letters): expected ≲ 4e-5 per pass —
  negligible, but the same rule covers them uniformly.

As in §2: a control that fires with high probability under the null detects
nothing. A1 restores the §7.3 control's discriminative power on this channel;
it does not relax the control. The runner again behaved correctly
(boundary stop to Fable; no self-modification of the predicate).

### 9.3 The amended rule (normative)

DECISION: §7.3 matching (as already clarified by ASM-0360) is extended as follows [STIPULATED: ASM-0660]:

> On the two HARNESS-CAPTURED surfaces `events.jsonl` and `stderr.log` — and
> NEVER on `user-prompt.txt` — a case-insensitive token match is additionally
> excluded from being a HIT iff, in the ORIGINAL (pre-lowercasing) bytes, it
> lies wholly inside the base62 TAIL of a maximal Anthropic-format vendor
> identifier literal, defined as a byte run matching
> `(req|msg)_[0-9A-Za-z]{20,48}` where (i) the 4-byte prefix `req_` or `msg_`
> is lowercase-exact, (ii) the byte immediately before the prefix and the
> byte immediately after the run are absent (file boundary) or outside
> `[0-9A-Za-z_]` (the literal is maximal, not part of a longer word or a
> longer alphanumeric run), and (iii) the token match lies wholly within the
> `[0-9A-Za-z]{20,48}` tail. The rule applies uniformly to all four pinned
> tokens. Every byte outside qualifying tails — including the rest of the
> same line and the same field — is scanned byte-identically to ASM-0360.

Bounds rationale: all observed tails are exactly 24 characters; 20–48
tolerates modest vendor format drift while refusing short English-word-shaped
runs and unbounded runs (a run longer than 48 fails the maximality byte-check
and is NOT excluded — fail-closed). Any future vendor id format outside this
shape that coincidentally spells a token will abort again and is its own
boundary stop.

### 9.4 Why this is leak-safe; rejected alternatives

- **`user-prompt.txt` is untouched by A1**: item contamination fires
  byte-identically to the original scan (and byte-equality with the item's
  `question` is separately required by §7.3).
- **Every real spelling still fires.** Project spellings (`nsm`, `NSM
  explication`, `nsm-lexicon`, `kernel-of-truth`, `poc/truthstyle-2x2`,
  `f2b-transfer`, …) contain delimiters or casing/format that fail the
  `(req|msg)_` + 20–48-base62 anchored shape; a judge ECHOING a token emits
  it in a `"text":"…"` content block, which is not inside any qualifying id
  tail, so it still trips. The exclusion excludes ONLY the tail bytes of a
  well-formed vendor id literal, never a field, a line, or a file.
- **Sensitivity witness (unchanged):** the §3 argv-echo witness holds — had
  any vendor surface echoed repo argv/paths, the scan fires on delimited
  non-hex tokens exactly as before.
- Rejected (b) *drop request_id/session_id from the scan surface*: strictly
  larger blind spot — a leak INSIDE those field values would become
  invisible, and identifying "the field" requires JSON-parsing surfaces that
  are not JSON (`stderr.log`).
- Rejected (c) *scrub id fields from captured provenance before the sweep*:
  destroys the §5 retained-bytes guarantee ("nothing is deleted; the
  clarification is fully re-derivable") — the auditor could no longer re-run
  the strict scan over the original bytes; scrubbing is provenance
  falsification in exchange for nothing the matching rule cannot do.
- Rejected (d) *change the p3 capture form*: `claude -p --output-format
  stream-json` is the PINNED §4.3 invocation (staged file, amendment seq 1);
  re-pinning a judge interface to work around a detector-side false positive
  inverts the control hierarchy and would re-open ASM-0240/0241 staging.
- Relation to §3's earlier rejection of "identifier-field-value exclusion":
  A1 is NOT that option. It parses nothing, pins no vendor FIELD-NAME list,
  works on non-JSON surfaces, and never excludes a whole field value — only
  token bytes wholly inside a format-anchored, maximality-checked base62
  tail. The §3 objections do not apply to this narrower shape.

### 9.5 Normative code

In `poc/truthstyle-2x2/run-dts-judges.py` (still the UNPINNED mechanical
executor; named in no pin), `import re` is added and the §4 code block is
superseded by: the unchanged `BLIND_TOKENS`/`_HEX_BYTES`/`_hex_embedded`
definitions, plus exactly:

```python
_VENDOR_ID_RE = re.compile(rb"(?:req|msg)_[0-9A-Za-z]{20,48}")
_WORD_BYTES = frozenset(b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                        b"abcdefghijklmnopqrstuvwxyz_")


def _vendor_id_tail_spans(raw):
    """Byte spans [s, e) of the base62 TAILS (prefix excluded) of maximal
    Anthropic-format vendor-id literals in the ORIGINAL bytes (ASM-0660)."""
    spans = []
    for m in _VENDOR_ID_RE.finditer(raw):
        s, e = m.span()
        if s > 0 and raw[s - 1] in _WORD_BYTES:
            continue                      # embedded in a longer word: no exclusion
        if e < len(raw) and raw[e] in _WORD_BYTES:
            continue                      # run continues (>48 chars): fail closed
        spans.append((s + 4, e))          # tail only; skip the 4-byte req_/msg_
    return spans


def blinding_scan(paths):
    for p in paths:
        if not os.path.exists(p):
            continue
        raw = open(p, "rb").read()
        data = raw.lower()
        # ASM-0660 exclusion NEVER applies to user-prompt.txt (item bytes):
        # item contamination fires byte-identically to the original scan.
        id_spans = ([] if os.path.basename(p) == "user-prompt.txt"
                    else _vendor_id_tail_spans(raw))
        for t in BLIND_TOKENS:
            pure_hex = all(c in _HEX_BYTES for c in t)
            i = data.find(t)
            while i >= 0:
                excluded = ((pure_hex and _hex_embedded(data, i, len(t)))
                            or any(s <= i and i + len(t) <= e
                                   for s, e in id_spans))
                if not excluded:
                    return (os.path.basename(p), t.decode())
                i = data.find(t, i + 1)
    return None
```

Function signature, return contract, call sites, abort message, token list,
scanned surfaces, and all other tripwires are unchanged. The §5 sweep is
updated in lockstep: `blinding-sweep.py` now derives vendor-id spans from the
SAME `rdj._vendor_id_tail_spans` the abort predicate uses (no drift possible)
and lists EVERY exclusion with a `kind` field — `"hex_run"` entries carry the
surrounding maximal hex run as before; new `"vendor_id"` entries carry the
full id literal (prefix included) — so the auditor can verify each one is a
machine identifier by inspection and can re-run strict, ASM-0360, and A1
scans independently over the retained bytes. GREEN still requires
`clarified_hits == []`. Amended-file integrity pins [MEASURED: sha256sum
2026-07-10]:

- `run-dts-judges.py`
  `1d6d7a396948414f886e0f4caea6557f54d90e31b74511cf656d6a9eba34a74f`
- `blinding-sweep.py`
  `b53b6d7a2f2e2cfe684c18eda896c73cce3390896aa4584287e96ad7960bdcea`

### 9.6 Residual risk (disclosed)

A1 reduces sensitivity for exactly one shape: a pinned token embedded within
an unbroken 20–48-character base62 run that immediately follows a lowercase
`req_`/`msg_` prefix and is delimiter-bounded on both sides, on the two
captured surfaces only. Census [MEASURED: repo-wide grep
`(req|msg)_[0-9A-Za-z]{20,48}` over docs/, registry/, poc/, analysis/,
tools/, data/d-ts, 2026-07-10]: `data/d-ts/items.jsonl` contains ZERO
vendor-id-shaped literals; of 244 distinct such literals in the tree, exactly
ONE contains a pinned token — `req_011Cctc1sK9P4SujinnsMiWU` itself, i.e. the
retained pos-102 provenance and its verbatim quotations in this amendment's
materials, none of which has a path into any judge-visible byte. A judge
could only EMIT such a string containing a real token if the token had
already leaked into its input — which the input-side scan catches
independently. The §11 structural blinding (empty out-of-repo workdir, no
repo strings in judge-visible prompt bytes) remains the primary control and
is unchanged.

### 9.7 Re-run ruling: p3 only; pos-102 retained, not scrubbed

DECISION: judge-p1 and judge-p2 passes of run 20260710T151231Z STAND as complete and blinding-clean; ONLY judge-p3 re-runs — fresh full protocol (§8 preflight, then the §3-ordered main pass over all 808 items in the frozen p3 seed order) in a NEW run dir under the A1 runner; the aborted p3 partial (pos-001–102) is VOID for labels and retained byte-verbatim as provenance; pos-102's captured bytes are NOT scrubbed and NOT re-captured in place [STIPULATED: ASM-0661].

- **Why not void p1/p2 too (the ASM-0361 shape):** ASM-0361 is expressly
  one-shot ("not a standing resume-or-restart policy"). Here, unlike then,
  two passes COMPLETED under the pinned protocol with zero incident and their
  responses were mechanically written at pass end; the p3 false positive is
  independent of their content, and the A1 predicate change is
  detector-side only — it alters no judge-visible byte, so label
  distributions cannot depend on it. The final gate is uniform anyway: the A1
  sweep re-applies the SAME predicate over the retained p1/p2 bytes.
- **Why not resume p3 at pos-103:** the pinned spec defines no resume
  mechanism, and none can be improvised (stage discipline). Concretely, the
  runner assembles labels in memory and writes them only at pass END — the
  void partial's labels were never persisted, so a resume would require NEW
  unpinned logic to re-ingest captured events as labels. Restarting p3
  re-runs only pinned mechanics; the ~102 discarded p3 calls cost
  ≈ 0.02–0.3 USD, inside the frozen caps.
- **No selection effect, with one disclosure:** no p3 label was assembled,
  written, or read (§9.1). Disclosure: during the boundary-stop diagnosis the
  coordinator READ the void pos-102 capture (item "steamfitter", raw answer
  bytes `no`) to localize the matched bytes. That void sample is discarded
  and enters no statistic; the re-run re-judges the item fresh;
  first-valid-answer-is-final (ASM-0241) bars outcome-conditioned re-rolls;
  and the re-run decision criterion (detector false positive) is structural,
  not outcome-dependent. One item's void raw answer seen by the mechanical
  coordinator does not touch the arm/style blinding of the analysis side.
- **Why pos-102 is not scrubbed:** under A1 its 'nsm' occurrence is a listed,
  auditor-inspectable `vendor_id` exclusion — the sweep goes GREEN over the
  retained bytes as they are [MEASURED: A1 self-test sweep-equivalent walk
  over opus-runs/20260710T151231Z, 2026-07-10: clarified hits = [], 6
  exclusions = 5 `f2b` hex-run + 1 `nsm` vendor-id at pos-102]. Scrubbing
  would destroy the §5 re-derivability guarantee for zero audit benefit.
- **Mechanics** (operational detail in `poc/truthstyle-2x2/p3-rerun-plan.md`):
  new run dir; sha256 of the A1 `run-dts-judges.py` and `blinding-sweep.py`
  recorded there BEFORE launch; after `MAIN_DONE p3`, the coordinator copies
  the byte-identical `run-summary-p1.json`, `run-summary-p2.json`, and
  `preflight-status-p{1,2}.json` from 20260710T151231Z into the new dir
  (shas recorded) and runs `finalize` there; the A1 sweep must be GREEN over
  BOTH run dirs before the d-ts-labels ops amendment is written.

### 9.8 What is NOT changed by A1

Everything in §8, again; plus: the ASM-0360 hex-run rule and its 5 tolerated
`f2b` exclusions (byte-identical logic, regression-tested); the ASM-0361
void ruling for 20260710T115128Z; the frozen judge pins, seeds, and order;
the p1/p2 corpus and responses bytes; `judges-invocation.md` and all staged
files. A1 is a second false-positive clarification of the same audit
predicate, ratified pre-data at the harness-executor level, with the p3
re-run scoped to the only pass the false positive interrupted.
