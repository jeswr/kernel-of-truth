# kot-rtrace/1 — GLM-5.2 backend-smoke router trace schema

Read-only per-token MoE router trace emitted by the patched colibri engine
(`rtrace.h`, wired into `moe()`), consumed by `trace_analyze.py`. JSONL, one JSON
object per line. The direct per-item/per-token remedy for the session-cumulative
STATS contamination (`poc/glm52-probe/CONTAMINATION-NOTE.md`).

## Line types

| `t` | meaning | fields |
|---|---|---|
| `hdr` | file header (once) | `schema`, `n_layers`, `fields` |
| `begin` | start of an item — **per-item reset point** | `item`, `T`, `n_prompt`, `topk`, `draft` |
| `r` | one selected expert at one token | see below |
| `end` | end of an item | `item`, `rows`, `decident_fnv1a64` |

## `r` (route) row — one per selected expert

| field | type | meaning |
|---|---|---|
| `item` | int | probe id (must equal the enclosing `begin.item` — no carry-over) |
| `tok` | int | item-local token position (prefill starts at pos_base 0) |
| `io` | int | 0 = prompt/input (`tok < n_prompt`), 1 = teacher-forced target |
| `site` | str | `main` (layer < n_layers) or `mtp` (layer == n_layers, the MTP head) |
| `layer` | int | engine layer index (main sparse 3..77; MTP 78) |
| `rank` | int | selection rank, 0 = top (selection is by `sel`, colibri noaux_tc) |
| `e` | int | selected expert id (0..255) |
| `raw` | float | pre-sigmoid router logit |
| `gate` | float | `sigmoid(raw)` = **pre-normalisation** router score |
| `sel` | float | `gate + router_bias` = selection criterion (ranking) |
| `w` | float | **normalised** routed weight (post `norm_topk` × `routed_scale`) |
| `mgn` | float | top-k / top-(k+1) margin = min-over-kept `sel` − max-over-dropped `sel` |

## Invariants checked by `trace_analyze.py`

1. **Framing** — every item has `begin`+`end`; `end.rows` == emitted `r` rows.
2. **No carry-over** — every `r` row's `item` == the enclosing `begin.item`
   (the reset re-seeds per item; nothing leaks across items).
3. **Top-k** — per `(item,tok,layer)`: ranks `0..Ke-1` contiguous+distinct,
   expert ids distinct, `sel` non-increasing by rank, `mgn ≥ 0`, weights finite `>0`.
4. **Fingerprint** — `decident_fnv1a64` is an FNV-1a-64 over the routing
   DECISIONS only `(tok,layer,rank,e)` — NOT the floats — so it is invariant to
   int4 kernel-family rounding. The analyzer recomputes and matches it.
5. **Site policy** — `draft=0` items are all `main`; `mtp` rows only in `draft≥1`.
6. **Byte-identity** — a repeated probe (same tokens) yields an identical
   fingerprint (deterministic routing decisions).

## Engine invocation

```
RTRACE=<trace.jsonl>  TRACE_SCORE=<manifest.txt>  DRAFT=0  SNAP=<model>  ./glm <cap> <ebits> <dbits>
```
`TRACE_SCORE` manifest, one item per line: `item_id  T  n_prompt  t_0 .. t_{T-1}`
(host pre-tokenises text with the model tokenizer; tiny oracle uses raw ids).
Per item the engine calls `rtrace_begin_item` (RESET), ONE teacher-forced prefill
(`moe()` emits `r` rows), then `rtrace_end_item`. Without `RTRACE` the engine holds
`g_rt==NULL` and every `rtrace_*` call is a no-op → output byte-identical to upstream.
