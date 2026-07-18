# F1-K LAYER-GEOMETRY RE-FREEZE AMENDMENT (exact diffs + ASM registration) — v3

**Author:** designer-20 (design pass, $0 — memo + exact diffs ONLY; no git action, no spend, no VM, no registry write performed by this pass; the coordinator applies everything below in ONE landing commit)
**Date:** 2026-07-17 (v3; v2/v1 2026-07-17)
**Version:** v3 — revised per the GPT-5.6 (xhigh) **RE-review** verdict **APPROVE-WITH-FIXES** (`poc/gpt56-review/f1k-layer-refreeze-rereview/last-message.json`): four of the six v2 fixes are RESOLVED (re-review pts 2/4/5/6 — re-pin inventory §1.5/§1.5a, floor gate §1.8-G4, ASM-2488 citation, blast-radius §2) and are PRESERVED UNCHANGED here, as is the approved core (§0, §1.1, §1.4 ASM-2504). Exactly TWO must-fixes remain, both closed in v3 (Revision log (v3) below): the v2 sidecar assertion `car["layers"] == 75` (re-review pt 1, NEW-ISSUE) and the FALSE v2 claim that no directory digest needs recomputing (re-review pt 3, NOT-RESOLVED). *(v2 provenance: revised per the first-round verdict `poc/gpt56-review/f1k-layer-refreeze-review-VERDICT.md`; that reviewer AGREED on points 1, 2, 5 — the 3..77 = 75 geometry, the two-universe distinction, and the $0 re-freeze posture. §0, §1.1(a)/(c), the ASM-2504 record, the −1.316% arithmetic, and the §1.5 frozen-record correction mechanics are preserved from v1.)*
**Corrects:** the confirmed F1-K FREEZE DEFECT (coordinator-verified 2026-07-17; `poc/gcp/F1K-CONSTRUCTION-PLAN.md` §"layer universe"): the frozen harness pins splice layers **3..78 = 76**, but the F1-K construction run is a live **DRAFT=0** MoE-input dump whose reachable MoE layers are **3..77 = 75**; layer 78 is the MTP head, excluded at DRAFT=0.
**Framing — stated plainly:** this is a **$0 correctness-only re-freeze**. It changes NOTHING scientific except the layer geometry: the 19,964 mandatory prefills, engine (colibri `a78a06fc5acc`), weights, tokenizer, protocol, endpoints, kill criterion, envelope, power table, $155 cap, and the affordability floors are ALL UNCHANGED. It makes the frozen artifact match **its own declared DRAFT=0 scope**. It is a defect correction, **not** a goalpost move: without it the run literally cannot execute (§1.3).

## Revision log (v3)

| # | Re-review pt | Fix | Where in v3 |
|---|---|---|---|
| 1 | pt 1 (NEW-ISSUE, introduced in v2) | **Pilot-aware sidecar gate.** v2's `assert car["layers"] == 75` was WRONG: the sidecar `car` describes the **frozen-L PILOT-SELECTED subset actually spliced**, not the 75-layer master — `f1k_driver.py:2330` sets `car["layers"] = km["nl"]` where `km` is read from the `frozen["layers"]` subset table (`load_frozen_lg` → `kaec_subset`, `:2291–2296`), so a legitimate green reports **1** (L1=[40]), **4** (L2=[40,52,65,77]) or **75** (L3=all) — a hard `== 75` FAILS legitimate L1/L2 pilot greens. `mock_e2e_carriers.py:151–155` already checks `params_added == 96*car["layers"]*6144` and `table_bytes == 16 + 4*car["layers"] + 4*params_added` PARAMETRICALLY. v3: (a) the `== 75` sidecar assertion is REMOVED; (b) the 75-layer / ids==3..77 hard check stays where it belongs — on the **MASTER** geometry (construction-report `/binding/layers` + master K table + `REGISTERED_SPLICE_LAYERS`, which the re-review confirmed already reject stale 3..78); (c) the sidecar is validated against the **SELECTED pilot subset**: `car["layers"] == len(frozen["layers"])` AND `set(frozen["layers"]) ⊆ {3..77}`. §1.8-G2 restated; §1.8-G1 unchanged. Corrected gate: GREEN for L1/L2/L3, RED on any id ≥ 78 or master len ≠ 75. |
| 2 | pt 3 (NOT-RESOLVED) | **There IS an A-time directory digest to recompute.** v2's "no digest recompute is needed now" was FALSE. `registry/experiments/f1k.json` embeds the ACTIVE **A-time DIRECTORY DIGEST** `513ed1964105347643d6b2c8339bcd1b101f7e11db4f6ab29fbd9dbfe0e0d3b1` over `data/f1k-carriers-v1/` (kot-corpus-hash/1 INPUT-tree digest, reproduced by `tools/registry/corpus-pin.py`) at TWO text sites, and the record's own text asserts "the (A)-time carrier-input directory digest is UNCHANGED (no data/f1k-carriers-v1 edit)" — exactly the condition the §1.3/§1.3b edits VIOLATE. This digest is DISTINCT from the `pins.corpus_hashes.f1k-carriers-v1` PINNED-AT-INPUTS placeholder (the post-construction REALIZED-tables digest, binds at B0 — that part of v2 stands; placeholder status untouched). v3: §1.3b reasoning corrected (two digests, one recompute-now); §1.5 gains the embedded-digest re-pin row + two correction-record `changes` entries; §1.8/§4 landing order fixed — corpus-pin.py runs AFTER the data edits and the new digest is spliced into `f1k.json` BEFORE `frozen_sha256`/frozen-index recompute. |

*(Everything else — the four RESOLVED v2 fixes and the approved core — is byte-preserved from v2 except the small consequential edits the two rows above require: §1.3b, §1.5 table+correction JSON, §1.8-G2, §3 rows 14/17 + new rows 19–20, §4 order, status lines.)*

## Revision log (v2)

| # | Review pt | Fix | Where in v2 |
|---|---|---|---|
| 1 | pt 3 | **Stale-oracle closure:** the $0 acceptance gate could go GREEN on the pre-built `mock-out/carriers-6144` whose committed report still records 76 layers 3..78 (`construction-report.json` `/binding/layers` len=76, verified). v2 (a) makes the gate REBUILD `carriers-6144` at the corrected 3..77 geometry before `mock_e2e_carriers.py` runs (exact command, §1.8-G1), (b) adds a HARD registered-geometry assertion to `mock_e2e_carriers.py`'s mock-positive path — a NEW edit site, not in v1 (§1.8-G2) *[v3: the SIDECAR clause of that assertion was wrong and is corrected — Revision log (v3) #1]*, and (c) NARROWS v1's "no literal 78 survives anywhere in the harness" claim to ACTIVE REQUEST/PIN SITES only; append-only historical records legitimately retain 78 (§1.1 confirmation, rewritten). |
| 2 | pt 4 (first half) | **Re-pin inventory completed — the decisive omission:** the live GCP orchestrator `poc/gcp/f1k_gcp.py` hard-pins the OLD `FROZEN_SHA256` (`505165ee…`, :51) and the OLD `build_carriers.py` sha (`cda62364…`, :59), both "verified at launch" (:49) — as frozen, it would have REJECTED the corrected run at launch and wasted the spend. Both added to the §1.5 re-pin inventory as REQUIRED code edits (§1.5a), plus an exhaustive re-scan of `f1k_gcp.py` / `f1k_worker.sh` / `bringup_gcp.sh` listing every embedded-sha site. |
| 3 | pt 4 (second half) | **Committed data tree:** `data/f1k-carriers-v1/README.md:44–47` and `manifest.json:10` still assert "ALL 76 MoE layers, engine ids 3..78". v1 edited only the harness README + generator-spec. v2 adds exact edits for both (§1.3b) and RESOLVES the corpus-digest question: `pins.corpus_hashes.f1k-carriers-v1` is a PINNED-AT-INPUTS placeholder (verified: literal value begins `"PINNED-AT-INPUTS:realized carrier tables…"`), the `_recipe` (`kot-corpus-hash/1`) digests every regular file under `data/f1k-carriers-v1/` recursively — so README/manifest/generator-spec are INSIDE the future digest scope but NO digest is recorded yet; editing pre-construction is lawful and the digest binds the corrected files at construction (§1.3b). *[v3 CORRECTION: the placeholder half of this row stands, but the "no digest recompute" conclusion was FALSE — a SECOND, ACTIVE A-time directory digest `513ed196…` is embedded in `f1k.json` and IS invalidated by these edits; see Revision log (v3) #2 and the corrected §1.3b.]* |
| 4 | pt 4 (floors) | **Floors confirmed by GATE, not inference:** v1 argued the [$73,$155] / [260.6,900] h floors are unmoved because the corrected run does less work. v2 keeps that as rationale but adds the executable arbiter to the §1.8 acceptance gate: `python3 poc/gcp/f1k_gcp.py plan` (the $0 floor+ceiling admissibility gate, `cmd_plan` :289–334 asserting non-empty windows over the frozen floors), with expected output stated (§1.8-G4). |
| 5 | pt 5 | **Citation correction ASM-2489 → ASM-2488:** the per-slot gated-count invariant is **ASM-2488** (`dump-patch/asm-f1k-dump-2485-2491.json:46`). Corrected at every occurrence (§0.1, §1.4 claim/backing_ref, §1.5 defect text, §2, self-check row 4). ASM-2488's OWN claim text reads "For the real A(iv) union 3..78 …" — a registered-ASM site carrying the wrong-universe phrase — so ASM-2488 is ADDED to ASM-2504's amends-by-citation list (§1.4) and to the §2 blast-radius table (registered ⇒ supersede-by-citation, no in-place edit). |
| 6 | pt 6 | **Blast-radius reclassification:** the stage-4 SPEED COHORT explicitly runs **DRAFT=1 with MTP ON** (`glm52-stage4-speed-cohort.md:208` — "this cohort's entire point"), so its live 3..78/76 geometry is LEGITIMATE; v1's FIX-RECOMMENDED verdict for `:62` is REVERSED to **LEAVE**. Every other stage-4 surface re-examined by ITS OWN DRAFT pin: drop-efficiency DRAFT=0 (:99, :182) ⇒ FIX; expert-drop DRAFT=0 (:698) ⇒ FIX (reviewer-confirmed); `build_masks.py`/`gen_mock_telemetry.py` deferred to stage-4's OWN re-freeze (78-handling is enumerate-then-reject in at least one path, `:502`; needs per-surface resolution). F1-K's landing depends on NO stage-4 edit (§2). |

---

## 0. Terminology: the two layer universes (the crux)

| Universe | Definition | Span | Count | Legitimate for |
|---|---|---|---|---|
| **A — committed-stats** | the committed routing-stats/trace files (earlier profiling; includes MTP-trace routing cells) | 3–78 | **76** (× 256 = 19,456 cells) | anything operating OVER the committed stats inventory (rosters, universal-cell counts, atlas cell inventories) |
| **B — live DRAFT=0 dump** | layers whose `moe()` input is reachable on the pinned model at DRAFT=0 (`num_hidden_layers=78` → main 0..77; `first_k_dense_replace=3` → dense 0,1,2; MTP head = layer 78, DRAFT≥1-only) | 3..77 | **75** (× 256 = 19,200 cells) | any experiment that RUNS the live engine at DRAFT=0 — **F1-K is exactly this** |

Sources: [MEASURED] `poc/gcp/probe-results/probe-results.json` `/M4/shape` = `m4.json` `/shape = {moe_layers:75, layer_min:3, layer_max:77}` (real GCP box, weights hash `19f1a3d0`); [MEASURED] `poc/glm52-probe/stage1-feasibility-manifest.md` B4 table (~:107–115): main_model sparse layers **3–77 (75)**, mtp_head **layer 78**, int8, "routed **MTP-only** — speculative; **excluded at DRAFT=0**"; [MEASURED] `glm52-expert-profiling-plan-sol-20260715.md:22` "committed traces expose 76 layer indices, 3-78" (Universe A). Both F1-K mock engines declare the mode: `mock_colibri.py:154` and `mock_colibri_dump.py:64` print "MTP off (draft=0)".

**The defect in one sentence:** ASM-2342 R3's Universe-A fact ("the committed stats files span MoE layers 3-78 = 76 layers") was WRONGLY transported into Universe B by ASM-2406(1) and the freeze, so the F1-K harness pins a 76-slot carrier whose slot for layer 78 can never receive a single DRAFT=0 MoE-input activation.

**A DRAFT-mode corollary (v2, from review pt 6):** which universe a LIVE surface belongs to is decided by that surface's OWN DRAFT pin, per surface — at DRAFT=1 the MTP layer 78 IS reachable and 3..78/76 is the legitimate live geometry (the stage-4 speed cohort is exactly this); at DRAFT=0 it is not. Neither blanket direction (76→75 everywhere, or review C1's 75→76 everywhere) is correct.

### 0.1 Why the run cannot execute as frozen (fail-closed, both branches)

- Loader: `poc/glm52-probe/kae-patch-draft/kae.h:194` — `for(i..nl) if(k->layer[i] < 0 || k->layer[i] >= n_layers) { "splice layer %d out of range" ... return NULL }`. If the engine's `n_layers==78` (main model), layer 78 is **hard-rejected** at load. If the MTP head makes `n_layers==79`, the slot loads but is **never routed** at DRAFT=0 — a permanently-dead splice slot, i.e. a false 76-layer splice attestation.
- Dump side, same outcome: the dump patch's own per-slot invariant (**ASM-2488**, `dump-patch/asm-f1k-dump-2485-2491.json:46`) requires every requested dump layer to accumulate EXACTLY `gated_count` rows or the engine **aborts nonzero** — "a requested dump layer that never reaches moe()" is precisely its named failure mode. At DRAFT=0, layer 78 never reaches `moe()`; construction aborts. *(v1 miscited this invariant as ASM-2489; corrected throughout — revision-log #5.)*

Either way: fail-closed halt or a wrong carrier. Hence this re-freeze.

---

## 1. PRIMARY DELIVERABLE — exact edits

All choices below are tagged. The corrected layer set is **[MEASURED]** (probe M4 75/3/77) **+ [PER-PROTOCOL]** (DRAFT=0 excludes the MTP head by the frozen protocol's own declared mode). The L2 pilot realization is **[STIPULATED]** (the registry's own registered realization rule re-evaluated at the corrected top layer — no new freedom exercised).

**v2 landing-set summary — every edit site in one list (new-in-v2 sites marked ★):**
1. `poc/glm52-probe/f1k-harness/build_carriers.py` (§1.1)
2. `poc/glm52-probe/f1k-harness/f1k_driver.py` (§1.2)
3. `data/f1k-carriers-v1/generator/generator-spec.json` (§1.3)
4. ★ `data/f1k-carriers-v1/README.md` + `data/f1k-carriers-v1/manifest.json` (§1.3b)
5. `registry/assumptions.jsonl` — ASM-2504 append (§1.4)
6. `registry/experiments/f1k.json` (incl. ★★ the recomputed A-time directory digest at BOTH `513ed196…` embed sites — §1.3b/§1.5) + `registry/frozen-index.json` + `registry/corrections/f1k/2-layer-geometry-refreeze.json` (§1.5)
7. ★ `poc/gcp/f1k_gcp.py` — launch-pin re-points (§1.5a) + comment echoes; `poc/gcp/bringup_gcp.sh:43` + `poc/gcp/README.md:5` comment echoes (§1.5a)
8. ★ `poc/glm52-probe/f1k-harness/mock_e2e_carriers.py` — registered-geometry hard gate (§1.8-G2; gate-adjacent code, low-risk, part of the landing commit)
9. Harness `README.md` + `dump-patch/PATCH-NOTES.md` (§1.7)

### 1.1 `poc/glm52-probe/f1k-harness/build_carriers.py`

**(a) :287 — the constant (the load-bearing edit; `REGISTERED_SPLICE_LAYERS = list(MOE_LAYERS)` at :293 and `L3` at :291 follow automatically):**
```
- MOE_LAYERS = tuple(range(3, 79))    # 76 MoE layers, ids 3..78 [ASM-2342]
+ MOE_LAYERS = tuple(range(3, 78))    # 75 MoE layers, ids 3..77 (DRAFT=0-
+                                     #  reachable set) [ASM-2342 amended:
+                                     #  ASM-2504]
```

**(b) :277–286 — the A(iv) comment block, rewritten to the corrected universe + the two-universe record (deliverable 3):**
```
- # ---- A(iv) RESOLUTION (carrier-HOLD fix 2; registered at the carrier-
- # pipeline hardening refreeze 2026-07-16) ------------------------------------
- # The pinned GLM-5.2 config (num_hidden_layers=78, first_k_dense_replace=3;
- # poc/glm52-probe/stage1-feasibility-manifest.md P0 config read) yields 76
- # MoE layers at ENGINE layer ids 3..78 INCLUSIVE — the id space of the
- # committed routing-stats files and of KAE_DUMP_LAYERS [MEASURED ASM-2342
- # R3-amended: "the committed stats files span MoE layers 3-78 = 76 layers"].
- # DES §2.3 pilot grid: L1 = one mid-stack MoE layer (~ layer 40), L2 = four
- # evenly spaced mid-to-late, L3 = ALL MoE layers. L3 = ALL, so the A(iv)
- # candidate splice union == the full MoE set, independent of L1/L2.
+ # ---- A(iv) RESOLUTION (carrier-HOLD fix 2; LAYER-GEOMETRY RE-FREEZE
+ # 2026-07-17 [ASM-2504]) ------------------------------------------------------
+ # The pinned GLM-5.2 config (num_hidden_layers=78, first_k_dense_replace=3;
+ # poc/glm52-probe/stage1-feasibility-manifest.md P0 config read) yields 75
+ # DRAFT=0-reachable MoE layers at ENGINE ids 3..77 INCLUSIVE [MEASURED:
+ # probe-results.json /M4/shape moe_layers=75 layer_min=3 layer_max=77;
+ # PER-PROTOCOL: layer 78 is the MTP head, DRAFT>=1-only, excluded at the
+ # frozen DRAFT=0 mode — stage1-feasibility-manifest.md B4]. TWO-UNIVERSE
+ # NOTE [ASM-2504]: the COMMITTED ROUTING-STATS files span 76 indices 3-78
+ # (they include an MTP-trace layer; ASM-2342 R3 is TRUE of that universe);
+ # the LIVE DRAFT=0 F1-K dump universe is 3..77 = 75 — this file pins the
+ # latter. DES §2.3 pilot grid: L1 = one mid-stack MoE layer (~ layer 40),
+ # L2 = four evenly spaced mid-to-late, L3 = ALL MoE layers. L3 = ALL, so
+ # the A(iv) candidate splice union == the full MoE set, independent of L1/L2.
```

**(c) :288–292 — the L2 pilot pin (deliverable 2).** The registered realization rule is `round(linspace(40, <top MoE layer>, 4))` [STIPULATED at ASM-2406(1) / `generator-spec.json .candidate_splice_layers`; realizing DES §2.3 "four evenly spaced mid-to-late" — `docs/next/design/glm52-followup-experiment.md:232`]. Re-evaluated at the DRAFT=0 top layer 77: `linspace(40, 77, 4) = [40, 52.33, 64.67, 77]` → **`[40, 52, 65, 77]`** (exact arithmetic shown; the old pin `[40, 53, 65, 78]` was `round(linspace(40, 78, 4))` — same rule, wrong top). **L1=[40] unaffected; L3=`list(MOE_LAYERS)` follows automatically.**
```
- PILOT_LAYER_SETS = {                # DES §2.3 realization [STIPULATED,
-     "L1": [40],                     #  registered A(iv)/pilot rider]: L1 =
-     "L2": [40, 53, 65, 78],         #  the DES's own "~ layer 40"; L2 =
-     "L3": list(MOE_LAYERS),         #  round(linspace(40, 78, 4)); L3 = ALL
- }
+ PILOT_LAYER_SETS = {                # DES §2.3 realization [STIPULATED,
+     "L1": [40],                     #  registered A(iv)/pilot rider]: L1 =
+     "L2": [40, 52, 65, 77],         #  the DES's own "~ layer 40"; L2 =
+     "L3": list(MOE_LAYERS),         #  round(linspace(40, 77, 4)) at the
+ }                                   #  DRAFT=0 top layer [ASM-2504]; L3 = ALL
```

**(d) Textual echoes in the same file (each cites the constants; edit for honesty — old → new fragment):**

| Line | Old fragment | New fragment |
|---|---|---|
| :49–50 (docstring) | `union (REGISTERED_SPLICE_LAYERS below — the 76 MoE layers` / `3..78; carrier-HOLD fix 2)` | `union (REGISTERED_SPLICE_LAYERS below — the 75 DRAFT=0 MoE layers` / `3..77; carrier-HOLD fix 2, ASM-2504)` |
| :174 (docstring) | `enforces mode=real AND the A(iv) layers 3..78 AND D=6144 AND a` | `enforces mode=real AND the A(iv) layers 3..77 AND D=6144 AND a` |
| :224 (usage example) | `--layers 3,4,...,78 \` | `--layers 3,4,...,77 \` |
| :312 (R10-1 comment) | `layers 3..78 AND D=6144 AND the mock-stack denylist below).` | `layers 3..77 AND D=6144 AND the mock-stack denylist below).` |
| :804 (fail msg) | `"splice union (the 76 MoE layers %d..%d of the pinned GLM-5.2 "` | `"splice union (the 75 DRAFT=0 MoE layers %d..%d of the pinned GLM-5.2 "` |
| :1213 (comment) | `# the real one (mode=real + A(iv) 3..78 + D=6144 + denylist).` | `# the real one (mode=real + A(iv) 3..77 + D=6144 + denylist).` |
| :1249 (comment) | `# relabeled mode=real (mock geometry can legally rehearse 3..78 /` | `# relabeled mode=real (mock geometry can legally rehearse 3..77 /` |
| :1264 (check label) | `"(76 MoE layers 3..78 [ASM-2342])",` | `"(75 MoE layers 3..77 [ASM-2342 amended: ASM-2504])",` |
| :1443 (verify msg) | `"the A(iv) layers 3..78 AND D=6144 AND the mock-stack "` | `"the A(iv) layers 3..77 AND D=6144 AND the mock-stack "` |
| :1447 (verify msg) | `"3..78, D=6144, mock-stack denylist, non-degeneracy, "` | `"3..77, D=6144, mock-stack denylist, non-degeneracy, "` |
| :1877 (argparse help) | `"registered A(iv) union 3..78 (carrier-HOLD fix 2)")` | `"registered A(iv) union 3..77 (carrier-HOLD fix 2)")` |

**Confirmation (v2 — NARROWED per review pt 3):** after (a)–(d) plus §1.2/§1.3/§1.3b/§1.7, no literal 78 survives as a splice/pin layer id at any **ACTIVE REQUEST OR PIN SITE**: the `build_carriers.py` / `f1k_driver.py` constants and their textual echoes (edited here), `generator-spec.json .candidate_splice_layers` (§1.3), the data-tree `README.md`/`manifest.json` (§1.3b — MISSED in v1), and the harness `README.md`/`PATCH-NOTES.md` (§1.7). **Append-only HISTORICAL records legitimately retain 78 and MUST NOT be edited:** `opus-runs/*/run-log.jsonl` (append-only run witnesses), `mock-out-*.log` (historical mock transcripts), and any prior `construction-report.json` — including the committed stale `mock-out/carriers-6144/construction-report.json` (which still records a 76-entry `layers` array, `/binding/layers` = 3..78; verified 2026-07-17). That stale artifact is not edited but **RETIRED by rebuild**: the §1.8-G1 gate regenerates `mock-out/carriers-6144` at the corrected geometry, so the post-land report carries 75. `poc/gcp/f1k_gcp.py` / `f1k_worker.sh` / `bringup_gcp.sh` contain no layer literals — but `f1k_gcp.py` DOES embed the old record/generator SHAs, which v1 missed; see §1.5a.

### 1.2 `poc/glm52-probe/f1k-harness/f1k_driver.py` (the [R9-PROV] ingest gate — same union, second copy)

| Line | Old | New |
|---|---|---|
| :400 | `REGISTERED_SPLICE_LAYERS = list(range(3, 79))` | `REGISTERED_SPLICE_LAYERS = list(range(3, 78))` |
| :401–403 (comment) | `#   the A(iv) candidate splice union: ALL 76 MoE layers of the pinned` / `#   GLM-5.2 config, ENGINE IDS 3..78 INCLUSIVE [MEASURED ASM-2342 R3;` / `#   STIPULATED ASM-2406; REG A_pre_spend carrier-pipeline hardening rider]` | `#   the A(iv) candidate splice union: the 75 DRAFT=0-reachable MoE layers` / `#   of the pinned GLM-5.2 config, ENGINE IDS 3..77 INCLUSIVE [MEASURED` / `#   probe M4 75/3/77 + PER-PROTOCOL DRAFT=0; ASM-2504 amending ASM-2342/` / `#   ASM-2406; REG A_pre_spend layer-geometry re-freeze rider 2026-07-17]` |
| :1037 (docstring) | `* layers == the REGISTERED A(iv) splice union (76 MoE layers 3..78` | `* layers == the REGISTERED A(iv) splice union (75 MoE layers 3..77` |
| :1119 (fail msg) | `"A(iv) splice union (76 MoE layers %d..%d [ASM-2342]); "` | `"A(iv) splice union (75 MoE layers %d..%d [ASM-2504]); "` |
| :3921 (mock check label) | `"real-mode fixture (nc=96, D=6144, layers 3..78, artifact-"` | `"real-mode fixture (nc=96, D=6144, layers 3..77, artifact-"` |

(The `%d..%d` values at :1119/:807 derive from the constant and correct themselves; the driver's mock fixtures build their layer lists from `REGISTERED_SPLICE_LAYERS` at `f1k_driver.py:3602`, so fixture GEOMETRY follows the constant with no separate edit — see §1.6.)

### 1.3 `data/f1k-carriers-v1/generator/generator-spec.json` — `.candidate_splice_layers`

Committed spec text; **lawful to edit now, but NOT a digest no-op** (v3): the edit changes the A-time directory digest `513ed196…`, recomputed at land — see the §1.3b digest resolution. Replace the field's value with:

> "RESOLVED + PINNED at the carrier-pipeline hardening refreeze (2026-07-16; carrier-HOLD fix 2), LAYER GEOMETRY CORRECTED at the layer-geometry re-freeze (2026-07-17; ASM-2504): A(iv) = the union of the pilot grid's layer sets L1/L2/L3 [DES §2.3] = the 75 DRAFT=0-REACHABLE MoE layers of the pinned GLM-5.2 config, ENGINE LAYER IDS 3..77 INCLUSIVE (num_hidden_layers=78, first_k_dense_replace=3 [poc/glm52-probe/stage1-feasibility-manifest.md P0 config read]; MEASURED on the construction box: probe-results.json /m4/shape = 75 layers, 3..77, weights 19f1a3d0; layer 78 is the MTP head, DRAFT>=1-only, excluded at the frozen DRAFT=0 mode [PER-PROTOCOL]. TWO-UNIVERSE NOTE: the committed routing-stats files span 76 indices 3-78 INCLUDING an MTP-trace layer [ASM-2342 R3, true of the stats universe]; the live DRAFT=0 dump universe pinned HERE is 3..77 = 75; L3 = ALL MoE layers forces the union regardless of L1/L2). Pilot-grid realization [STIPULATED]: L1 = [40] (the DES's own '~ layer 40' mid-stack), L2 = [40, 52, 65, 77] (round(linspace(40, 77, 4)), mid-to-late), L3 = all 75. ENFORCED fail-closed: build_carriers.py REGISTERED_SPLICE_LAYERS — construct --mode real and verify REFUSE any other layer list"

### 1.3b ★ `data/f1k-carriers-v1/README.md` + `manifest.json` (NEW in v2 — review pt 4, second half) + the corpus-digest resolution

Both committed data-tree files still assert the defective geometry; v1 edited only the harness README and generator-spec. Exact edits:

**`data/f1k-carriers-v1/README.md:44–47`** (the "Carrier-pipeline HARDENING refreeze" paragraph):
- :45–46 `the exact candidate splice-layer ids are now RESOLVED + PINNED (A(iv) = ALL 76 MoE layers, engine ids 3..78 inclusive [MEASURED ASM-2342 R3]; pilot realization` → `the exact candidate splice-layer ids are now RESOLVED + PINNED (A(iv) = the 75 DRAFT=0-reachable MoE layers, engine ids 3..77 inclusive [MEASURED probe M4 75/3/77; layer 78 = MTP head, excluded at DRAFT=0 — ASM-2504 amending ASM-2342 R3]; pilot realization`
- :47 `L1=[40] / L2=[40,53,65,78] / L3=all — see` → `L1=[40] / L2=[40,52,65,77] / L3=all [ASM-2504] — see`
- Append one line to the same paragraph: `LAYER-GEOMETRY RE-FREEZE (2026-07-17, ASM-2504): the 2026-07-16 pin transported the committed-stats universe (76 indices 3-78, incl. one MTP-trace layer) into the live DRAFT=0 dump universe (3..77 = 75); corrected here.`

**`data/f1k-carriers-v1/manifest.json:10`** (`"carrier_pipeline_hardening"` value): replace the fragment `A(iv) candidate splice-layer ids RESOLVED + PINNED (ALL 76 MoE layers, engine ids 3..78 [MEASURED ASM-2342 R3]; enforced fail-closed by build_carriers.py in real mode)` → `A(iv) candidate splice-layer ids RESOLVED + PINNED, LAYER GEOMETRY CORRECTED 2026-07-17 (the 75 DRAFT=0-reachable MoE layers, engine ids 3..77 [MEASURED probe M4 75/3/77; ASM-2504 amending ASM-2342 R3 — layer 78 = MTP head, DRAFT>=1-only]; enforced fail-closed by build_carriers.py in real mode)`.

**Corpus-digest resolution (v3 — CORRECTED per re-review pt 3; v2's "no digest recompute" was FALSE):** does editing this tree invalidate an already-recorded digest? **Yes — one of the TWO digests that govern it.** Distinguish them explicitly:

1. **The `pins.corpus_hashes.f1k-carriers-v1` PLACEHOLDER — binds at construction; LEAVE.** The field value is not a bare 64-hex digest; it begins `"PINNED-AT-INPUTS:realized carrier tables for every arm (K, 3 derangements, d0, d2) + raw and rescaled norms — the B0 pure-function addendum (SSR-REV3.3); kot-corpus-hash/1 over data/f1k-carriers-v1/ pinned after constru…"` (verified). This is the pin for the **post-construction REALIZED carrier tables**: it is digested only at the B0 addendum (after construction spend, before the pilot), so it will bind the CORRECTED file bytes; its PINNED-AT-INPUTS **status** is untouched by this re-freeze. `registry-check --corpus-pins` skips PINNED-AT-INPUTS placeholders (`tools/registry/registry-check.py:179`), so no mechanical check trips on it. *(This half of the v2 analysis stands.)*
2. **The ACTIVE A-time DIRECTORY DIGEST `513ed1964105347643d6b2c8339bcd1b101f7e11db4f6ab29fbd9dbfe0e0d3b1` — the INPUT-tree digest; RECOMPUTE NOW.** This is what v2 missed. It is a `kot-corpus-hash/1` digest over the **current** `data/f1k-carriers-v1/` tree (the (A)-time generator INPUTS — reconciled at the hardening pass to cover the construction-manifest plus the generator-spec/README/manifest rows), reproduced by `tools/registry/corpus-pin.py` (the recipe's reference implementation — "a pin that this tool cannot reproduce is wrong by definition", `corpus-pin.py:17`). It is EMBEDDED in `registry/experiments/f1k.json` (a single-line JSON file — cite by JSON path, not line) at **TWO text sites** (byte offsets as of 2026-07-17): **(i)** `/design/n_planned/freeze_manifest/A_pre_spend`, clause "(5) the (A)-time carrier-input directory digest RECONCILED …: the reconciled digest `513ed196…` additionally covers the (A)-time construction-manifest.jsonl …" (~byte 19768); **(ii)** INSIDE the `/pins/corpus_hashes/f1k-carriers-v1` placeholder text itself: "… are COMMITTED NOW at directory digest `513ed196…`" (~byte 53286). The record's own round-9/10 narrative asserts "**the (A)-time carrier-input directory digest is UNCHANGED (no data/f1k-carriers-v1 edit)**" (~byte 21833) — **exactly the condition the §1.3 + §1.3b edits VIOLATE**: `README.md`, `manifest.json`, and `generator/generator-spec.json` are all regular files under `data/f1k-carriers-v1/`, i.e. inside the recipe's scope, so the three edits CHANGE the A-time digest. Editing them pre-construction remains **lawful** (nothing has run; nothing is retroactively regraded), but it is **NOT a digest no-op**.

**Consequence (landing mechanics — §1.5 row + §4 step 2):** AFTER the three data-file edits, recompute via `python3 tools/registry/corpus-pin.py f1k-carriers-v1` and splice the new 64-hex value over **both** `513ed196…` embeds in `f1k.json` (keeping the placeholder's PINNED-AT-INPUTS prefix and binds-at-construction status intact at site ii) **BEFORE** recomputing `frozen_sha256`/frozen-index — the frozen hash covers the record bytes, so a digest spliced after it would drift. Historical carriers of `513ed196…` (`registry/corrections/f1k/1-prefreeze-correction.json`, opus run-logs, untracked mock seam fixtures) are witnesses of the pre-correction record — **LEAVE, never edit**; the seq-2 correction record documents the new value.

### 1.4 THE ASM AMENDMENT — registry/assumptions.jsonl (deliverable 4)

ASM-2342/2406/**2488** are centrally registered → in-place edits are forbidden; the discipline is **supersede-by-citation** (ASM-2352 precedent). *(v2: ASM-2488 — the per-slot gated-count invariant, `dump-patch/asm-f1k-dump-2485-2491.json:46` — replaces v1's miscited ASM-2489 AND is itself added to the amends list, because its own claim text carries the wrong-universe phrase "For the real A(iv) union 3..78 this doubles as the check that every requested layer is a genuine MoE layer".)* Append ONE new record, **ASM-2504** (next free id; verified 2026-07-17), **in the SAME commit that lands every edit in this memo** — no dangling id. Exact JSON line to append to `registry/assumptions.jsonl`:

```json
{"id": "ASM-2504", "tag": "MEASURED", "claim": "F1-K LAYER-GEOMETRY CORRECTION (amends-by-citation the layer-universe content of ASM-2342 R3, ASM-2406 clause (1), and ASM-2488's 'For the real A(iv) union 3..78' phrase; every other clause of those records stands — in particular ASM-2488's per-slot gated-count invariant itself is universe-agnostic and is exactly what enforces the corrected set): there are TWO distinct layer universes and each experiment must use its own. UNIVERSE A (committed routing-stats files): 76 indices 3-78 = 75 main MoE layers + 1 MTP-trace layer; ASM-2342 R3's 'committed stats files span MoE layers 3-78 = 76 layers' is TRUE of this universe and remains valid for anything operating over the committed stats inventory (universal-cell counts, rosters, 19,456-cell atlas inventories). UNIVERSE B (the live DRAFT=0 F1-K construction/campaign dump): the DRAFT=0-reachable MoE layers of the pinned GLM-5.2 config are 3..77 INCLUSIVE = 75 layers [MEASURED: poc/gcp/probe-results/probe-results.json key /M4/shape (= poc/gcp/probe-results/m4.json /shape) = {moe_layers:75, layer_min:3, layer_max:77}, real construction box, weights hash 19f1a3d0; PER-PROTOCOL: num_hidden_layers=78 puts main layers at 0..77, first_k_dense_replace=3 makes 0-2 dense, and layer 78 is the int8 MTP head, DRAFT>=1-only, 'excluded at DRAFT=0' per poc/glm52-probe/stage1-feasibility-manifest.md B4 - and F1-K's own mock engines declare 'MTP off (draft=0)']. LIVE-SURFACE RULE: a live surface's universe is decided by ITS OWN DRAFT pin - at DRAFT=1 the MTP layer 78 IS reachable and 3..78/76 is legitimate (e.g. the stage-4 speed cohort, DRAFT=1 MTP-ON by design); at DRAFT=0 it is not; neither blanket direction is correct. ASM-2406(1) WRONGLY transported the Universe-A count into Universe B; as frozen, the run could not execute in its own declared mode: the KaE loader fail-closes any splice id >= n_layers (kae.h:194), and the dump patch's per-slot gated-count invariant (ASM-2488) aborts on a requested layer that never reaches moe() - at DRAFT=0 layer 78 is exactly that. CORRECTED PINS: A(iv) candidate splice union = 75 MoE layers, ENGINE IDS 3..77 INCLUSIVE; pilot realization L1=[40] (unchanged), L2=[40, 52, 65, 77] (the registered rule round(linspace(40, top, 4)) re-evaluated at the DRAFT=0 top layer 77 [STIPULATED - no new freedom; the rule is ASM-2406's own]), L3 = all 75; carrier-table nl = 75; per-table .kaec size 16 + 4*75 + 4*(96*75*6144) = 176,947,516 bytes (was 179,306,816; -1.32%). SCOPE: this is a $0 correctness-only re-freeze - 19,964 mandatory prefills, engine, weights, tokenizer, protocol, endpoints, analysis pin (analysis/f1k.py 54924cfd... UNCHANGED), power, $155 cap, and the affordability floors ([73,155] USD / [260.6,900] h - functions of prefill count and throughput, not of nl; CONFIRMED post-correction by the executable gate poc/gcp/f1k_gcp.py plan, not by inference alone) are ALL UNCHANGED; the corrected run does strictly LESS work (75 dump slots per pass, not 76). Registered WITH the landing commit of poc/gcp/F1K-LAYER-REFREEZE.md (build_carriers.py/f1k_driver.py/generator-spec.json edits + data/f1k-carriers-v1 README+manifest edits + poc/gcp/f1k_gcp.py launch-pin re-points + the mock_e2e_carriers.py registered-geometry gate + registry/corrections/f1k/2-layer-geometry-refreeze.json).", "rationale": "The freeze transported a trace-universe layer count into the live DRAFT=0 dump universe, producing a frozen harness that fail-closes against its own engine (or, at n_layers=79, emits a false 76-layer splice attestation with one permanently-dead slot). Pinning the measured DRAFT=0-reachable set makes the frozen artifact match its own declared scope; recording the two-universe distinction PLUS the per-surface DRAFT rule prevents the same transport in either direction (review C1 had pushed stage-4 3-77 -> 3-78: correct ONLY for the DRAFT=1 speed cohort, wrong for the DRAFT=0 drop arms).", "backing_ref": "poc/gcp/probe-results/probe-results.json /M4/shape + poc/gcp/probe-results/m4.json /shape (MEASURED 75/3/77); poc/glm52-probe/stage1-feasibility-manifest.md B4 (MTP head layer 78, excluded at DRAFT=0); poc/glm52-probe/kae-patch-draft/kae.h:194 (fail-closed loader); poc/glm52-probe/f1k-harness/dump-patch/asm-f1k-dump-2485-2491.json:46 (ASM-2488 per-slot invariant); glm52-expert-profiling-plan-sol-20260715.md:22 (Universe A: committed traces expose 76 indices 3-78); docs/next/design/glm52-stage4-speed-cohort.md:208 (DRAFT=1 MTP-ON cohort: 3..78 legitimate live); ASM-2342 R3 (Universe-A statement, stands); ASM-2406 (the transport, amended); poc/gcp/F1K-CONSTRUCTION-PLAN.md (coordinator verification 2026-07-17); poc/gcp/F1K-LAYER-REFREEZE.md v3 (this amendment's exact diffs; GPT-5.6 xhigh review + re-review APPROVE-WITH-FIXES verdicts incorporated)", "load_bearing": true, "status": "open", "owner": "designer-20", "date": "2026-07-17"}
```

### 1.5 FROZEN-RECORD CORRECTION — `registry/experiments/f1k.json`

The geometry strings live in exactly THREE fields of the frozen record (exhaustive JSON-path scan): `/title`, `/pins/harness_manifest`, `/design/n_planned/freeze_manifest/A_pre_spend`. Frozen records are corrected via a `kot-correction/1` record (precedent: `registry/corrections/f1k/1-prefreeze-correction.json`), which edits the record in place, documents every change, and re-records the frozen hash. Create `registry/corrections/f1k/2-layer-geometry-refreeze.json`:

```json
{"schema_version": "kot-correction/1", "experiment": "f1k", "seq": 2,
 "date": "2026-07-17T00:00:00Z", "author": "designer-20",
 "kind": "pre-run defect correction (layer-geometry re-freeze)",
 "defect": "The frozen A(iv) splice union 3..78 (76 layers) includes layer 78, the DRAFT>=1-only MTP head, unreachable in the record's own declared DRAFT=0 mode; the run cannot execute as frozen (kae.h:194 fail-close / ASM-2488 abort). MEASURED: probe M4 shape 75/3/77 on the construction box.",
 "authorized_by": "Coordinator-verified freeze defect 2026-07-17 (poc/gcp/F1K-CONSTRUCTION-PLAN.md) + ASM-2504 (registered in this same commit) + GPT-5.6 xhigh review APPROVE-WITH-FIXES (poc/gpt56-review/f1k-layer-refreeze-review-VERDICT.md) + GPT-5.6 xhigh RE-review APPROVE-WITH-FIXES, both remaining must-fixes closed in v3 (poc/gpt56-review/f1k-layer-refreeze-rereview/last-message.json); surfaced to the maintainer as a GitHub issue per the NEXT-ACTION block of poc/gcp/F1K-LAYER-REFREEZE.md.",
 "changes": [
   "/title: every '76 MoE layers 3..78' -> '75 MoE layers 3..77 (DRAFT=0-reachable) [ASM-2504]'; 'layers-3..78 protocol' -> 'layers-3..77 protocol'",
   "/pins/harness_manifest: '76 MoE layers 3..78 [ASM-2342/ASM-2406]' -> '75 MoE layers 3..77 [ASM-2504 amending ASM-2342/ASM-2406]'; 'A(iv) union 3..78' -> 'A(iv) union 3..77' (2 sites); 'layers == 3..78' -> 'layers == 3..77'; 'A(iv) layers 3..78' -> 'A(iv) layers 3..77'; 'layers-3..78 protocol' -> 'layers-3..77 protocol'; build_carriers.py sha256 cda62364483559055feee2c355761abf748cdf8bbf8d4e4e1a4bc54958a2d624 -> <SHA256-OF-EDITED-build_carriers.py, COMPUTED AT LAND>",
   "/design/n_planned/freeze_manifest/A_pre_spend: 'ALL 76 MoE layers ... ENGINE LAYER IDS 3..78 INCLUSIVE (num_hidden_layers=78, first_k_dense_replace=3; the committed routing-stats files span MoE layers 3-78 = 76 layers [MEASURED ASM-2342 R3]; ...)' -> 'the 75 DRAFT=0-REACHABLE MoE layers ... ENGINE LAYER IDS 3..77 INCLUSIVE (probe M4 75/3/77 MEASURED; layer 78 = MTP head, excluded at DRAFT=0 PER-PROTOCOL; TWO-UNIVERSE NOTE: committed stats span 3-78=76 incl. an MTP-trace layer [ASM-2342 R3, stats universe]; the live DRAFT=0 dump universe is 3..77=75 [ASM-2504])'; 'L2=[40,53,65,78] (round(linspace(40,78,4)), mid-to-late), L3 = all 76' -> 'L2=[40,52,65,77] (round(linspace(40,77,4)), mid-to-late), L3 = all 75' (2 sites); 'A(iv) union 3..78' -> 'A(iv) union 3..77'; 'layers 3..78/seed 20260716' -> 'layers 3..77/seed 20260716'; 'A(iv) 3..78 + D=6144' -> 'A(iv) 3..77 + D=6144'; build_carriers.py sha256 cda62364... -> <SHA256-OF-EDITED-build_carriers.py, COMPUTED AT LAND>",
   "/design/n_planned/freeze_manifest/A_pre_spend clause (5) [v3, re-review pt 3]: A-time carrier-input directory digest 'the reconciled digest 513ed1964105347643d6b2c8339bcd1b101f7e11db4f6ab29fbd9dbfe0e0d3b1' -> '<A-TIME-DIRECTORY-DIGEST, COMPUTED AT LAND: tools/registry/corpus-pin.py f1k-carriers-v1 run AFTER the three data/f1k-carriers-v1 edits>'; the adjacent round-9 sentence 'the (A)-time carrier-input directory digest is UNCHANGED (no data/f1k-carriers-v1 edit)' remains as the (true) witness of THAT earlier pass — this correction supersedes its currency",
   "/pins/corpus_hashes/f1k-carriers-v1 [v3, re-review pt 3] PLACEHOLDER TEXT ONLY (the PINNED-AT-INPUTS prefix and binds-at-construction status are UNCHANGED): '... are COMMITTED NOW at directory digest 513ed1964105347643d6b2c8339bcd1b101f7e11db4f6ab29fbd9dbfe0e0d3b1' -> the SAME recomputed A-time digest as the clause-(5) entry above"
 ],
 "kill_criterion_status": "UNCHANGED verbatim (this correction touches layer geometry and the generator sha pin only; endpoints, TOST margins, power, caps, floors, envelope untouched).",
 "non_retroactivity": "No run, pilot, or construction has executed against the defective geometry (construction is pre-(B0); pins.corpus_hashes.f1k-carriers-v1 is still PINNED-AT-INPUTS). Nothing is retroactively regraded.",
 "legitimacy": "Correctness-only: makes the frozen artifact executable in its own declared DRAFT=0 mode; the corrected run does strictly LESS work. MEASURED basis probe M4 (75/3/77) + PER-PROTOCOL MTP exclusion (stage1-feasibility-manifest.md B4). Two-universe reconciliation in ASM-2504.",
 "refreeze_chain": "supersedes frozen_sha256 505165eebad647509bcb26bf6051deba16c3d400a0382c136ee6037d47a9fd41",
 "supersedes_frozen_sha256": "505165eebad647509bcb26bf6051deba16c3d400a0382c136ee6037d47a9fd41",
 "refrozen_sha256": "<COMPUTED AT LAND: kot_common.frozen_hash of the corrected record>",
 "build_artifacts": "poc/gcp/F1K-LAYER-REFREEZE.md v3 (this amendment); poc/gcp/f1k_gcp.py launch pins re-pointed in the SAME commit (FROZEN_SHA256 + PINS[build_carriers.py] — §1.5a); A-time data/f1k-carriers-v1 directory digest recomputed via tools/registry/corpus-pin.py and spliced at both f1k.json embed sites BEFORE the frozen hash (§1.3b); tools/registry/registry-check.py --frozen-drift green post-land"}
```

**Hash-pinned-input re-freeze — the input-pin manifest entries that change (exhaustive; v2 adds the ★ orchestrator rows — review pt 4, THE decisive omission):**

| Pin | Old | New | Why |
|---|---|---|---|
| `build_carriers.py` sha256 (in `/pins/harness_manifest` AND `/design/.../A_pre_spend`) | `cda62364...` | recompute at land | file edited (§1.1) |
| `registry/experiments/f1k.json` `frozen_sha256` + `registry/frozen-index.json["f1k"]` | `505165ee...` | recompute at land (`kot_common.frozen_hash`) | record corrected (§1.5); both MUST be updated in the same commit or `registry-check --frozen-drift` fails |
| ★ `poc/gcp/f1k_gcp.py:51` `FROZEN_SHA256` | `505165ee...` | the NEW `frozen_sha256` (same value written to `f1k.json`/`frozen-index` in landing step 3) | the live GCP orchestrator VERIFIES this at launch (`:49` "verified at launch"; `verify_pins()` :152–176 runs `registry-check frozen-drift` and dies on mismatch, ERR_F1K_PIN_FROZEN) — as frozen it would REJECT the corrected run and waste the spend |
| ★ `poc/gcp/f1k_gcp.py:59` `PINS["build_carriers.py"]` | `cda62364...` | the NEW `build_carriers.py` sha (same value as row 1) | `verify_pins()` re-derives the file sha and dies on mismatch (ERR_F1K_PIN_MISMATCH) before any spend |
| ★★ A-time `data/f1k-carriers-v1/` DIRECTORY DIGEST, embedded at TWO `f1k.json` text sites: `/design/.../A_pre_spend` clause (5) + inside the `/pins/corpus_hashes/f1k-carriers-v1` placeholder text ("COMMITTED NOW at directory digest …") — §1.3b *(v3 row; re-review pt 3 — v2 wrongly claimed no recompute)* | `513ed196...` | recompute at land: `python3 tools/registry/corpus-pin.py f1k-carriers-v1` AFTER the §1.3/§1.3b data edits; splice into BOTH embeds BEFORE the frozen_sha256 recompute (next row covers the record bytes) | the digest is `kot-corpus-hash/1` over the INPUT tree; `README.md`/`manifest.json`/`generator-spec.json` are inside its scope, so the three data edits change it — the record's "directory digest is UNCHANGED (no data/f1k-carriers-v1 edit)" premise no longer holds |
| **UNCHANGED:** `analysis/f1k.py` `54924cfd...` (no edit — it has NO layer-count literal; its KAEC arithmetic `16 + 4*nl + 4*C*nl*D` is parametric in `nl`, bound `KAEC_MAX_LAYERS=128` unaffected); KaE patch `11f8b458...` + `kae.h` reference sha; colibri base commit `a78a06fc...`; tokenizer/weights/dump-patch pins; `f1k_gcp.py` `PINS` rows for `kae-add-path.patch` `11f8b458`, `kot-f1k-dump.patch` `fb5d2f35`, `kae_dump.h` `6ce77601`, `construction-manifest.jsonl` `a8cb3a8a` (manifest is layer-free — §1.8, byte-identical); all corpus hashes (`f1k-eval-v1`, `f1k-contrast-v1`, `f1k-trigger-map-v1`, kernel-v0/v1); the `f1k-carriers-v1` placeholder **STATUS** (still PINNED-AT-INPUTS, binds at construction — but the A-time digest EMBEDDED in its text IS re-pinned, ★★ row above / §1.3b); construction seed 20260716; d0/kdrng/DRNG seeds. `f1k_driver.py` carries no sha pin in the frozen record OR in `f1k_gcp.py` (verified), so its §1.2 edits re-pin nothing. |

### 1.5a ★ Orchestrator + ops-script embedded-sha scan (NEW in v2 — review pt 4; exhaustive)

Full re-scan of `poc/gcp/f1k_gcp.py`, `poc/gcp/f1k_worker.sh`, `poc/gcp/bringup_gcp.sh` (plus `poc/gcp/README.md`) for `505165ee`, `cda62364`, and every ≥16-hex embedded literal. Every site, classified:

| Site | Content | Action |
|---|---|---|
| `f1k_gcp.py:51` `FROZEN_SHA256 = "505165ee…"` | **CODE pin, launch-verified** | **REQUIRED edit** → new frozen_sha256 (§1.5 table ★ row; spliced at land, step 3). Downstream uses `:159/:164/:165/:302/:372` reference the constant — no separate edits |
| `f1k_gcp.py:59` `PINS["build_carriers.py"] = "cda62364…"` | **CODE pin, launch-verified** | **REQUIRED edit** → new build_carriers sha (spliced at land, step 2) |
| `f1k_gcp.py:5` docstring "frozen_sha256 505165ee…"; `:49` comment "(registry/experiments/f1k.json 505165ee…; verified at launch)" | comment echoes | edit for honesty → new hash prefix (same commit) |
| `f1k_gcp.py:57` `PINS["analysis/f1k.py"] = "54924cfd…"` (+ `:14` comment) | pin of the UNTOUCHED analysis | **UNCHANGED** (analysis not edited — §1.6) |
| `f1k_gcp.py:61–67` `PINS` for kae-add-path.patch / kot-f1k-dump.patch / kae_dump.h / construction-manifest.jsonl | pins of untouched artifacts | **UNCHANGED** (none of these files is edited; construction-manifest is layer-free) |
| `bringup_gcp.sh:24` `COLIBRI_COMMIT="a78a06fc…"`; `:25` `PATCH_SHA256="11f8b458…"` (kae-add-path.patch) | pins of untouched artifacts | **UNCHANGED** |
| `bringup_gcp.sh:43` comment "(registry/experiments/f1k.json 505165ee carries no objdump/allowed-diff obligation)" | comment echo | edit for honesty → new hash prefix (same commit) |
| `poc/gcp/README.md:5` "frozen_sha256 505165ee…" | doc echo | edit for honesty → new hash prefix (same commit) |
| `f1k_worker.sh` | **ZERO embedded hashes** (verified: hex-literal grep = 0 hits) | none |
| `poc/gcp/F1K-AFFORDABILITY-DECISION.md:212, 267–268` "505165ee…" | dated decision memo — historical witness of the record version it decided against | **LEAVE — never edit** (append-only record discipline, same class as run-logs) |

### 1.6 MOCK-FIXTURE GEOMETRY (deliverable 5)

Finding after exhaustive search (`76`, `3..78`, `range(3, 79)`, layer-count assertions across the harness mocks, goldens, and `analysis/f1k.py`): **no committed mock fixture or golden hardcodes the 76-layer geometry independently of the two constants** — with the one v2-identified exception of the PRE-BUILT `mock-out/carriers-6144` artifact consumed by `mock_e2e_carriers.py`, which is a stale INPUT (not a fixture-generation surface) and is closed by the §1.8-G1 rebuild + §1.8-G2 hard gate. Every generated mock derives its layers parametrically, so the $0 oracle tracks §1.1(a)/§1.2(:400) automatically:

| Surface | Geometry source | Edit needed |
|---|---|---|
| driver `--mock` real-mode carrier fixture | `f1k_driver.py:3602` `lay = list(REGISTERED_SPLICE_LAYERS if layers is None else layers)` | none (follows constant); label text at :3921 edited (§1.2) |
| `build_carriers.py selftest` fixtures | `:1494/:1507/:1517` build from `REGISTERED_SPLICE_LAYERS` | none (follows constant) |
| `mock_colibri_dump.py` | takes layers from `KAE_DUMP_LAYERS` env csv; writes `nl = len(layers)`; `D = 6144` fixed at `:39` | none |
| `mock_colibri.py` | mock banner `layers=12` (deliberately non-real geometry); no splice-layer pin | none |
| `mock_e2e_carriers.py` | reads `K["layers"]` from the generator's own report; size check `16 + 4*car["layers"] + ...` parametric — **this self-consistency is exactly the stale-pass hole (review pt 3)** | ★ **edit — add the registered-geometry hard gate (§1.8-G2)** |
| `mock-out/carriers-6144` (pre-built oracle INPUT; git-untracked) | stale: report `/binding/layers` = 76 entries 3..78 (verified) | ★ **rebuilt by §1.8-G1 before the oracle runs** (never edited in place) |
| `analysis/f1k.py` | NO layer-count literal; `params_added == C*layers*D` divisibility + exact-size arithmetic parametric in `layers`; `KAEC_MAX_LAYERS = 128` sanity bound only | **none — pinned analysis untouched, sha `54924cfd` stands** |
| `mock-out/` incl. `fixtures/mock-config.json` | regenerable outputs, **git-untracked** (verified `git ls-files` = 0 entries) | regenerated by the §1.8 re-run |
| `mock-out-*.log` (top level) | historical mock transcripts, git-untracked | superseded by the §1.8 re-run's fresh logs; **never edited** |
| Textual echoes that DO hardcode `3..78`/`76` in tracked harness docs | `README.md:20, 48–49, 63, 103, 163, 177`; `dump-patch/PATCH-NOTES.md:132` | **edit** (§1.7) |

### 1.7 Harness documentation echoes (tracked files; same-commit edits)

`poc/glm52-probe/f1k-harness/README.md` — replace at each site (fragments):
- :20 `> **3..78** (the registered A(iv) union)` → `> **3..77** (the registered A(iv) union; 75 DRAFT=0 MoE layers [ASM-2504])`
- :48 `RESOLVED + PINNED = **all 76 MoE layers, engine ids 3..78 inclusive**` → `RESOLVED + PINNED = **the 75 DRAFT=0-reachable MoE layers, engine ids 3..77 inclusive**`
- :49 `(ASM-2342/ASM-2406; pilot realization L1=[40], L2=[40,53,65,78], L3=all).` → `(ASM-2504 amending ASM-2342/ASM-2406; pilot realization L1=[40], L2=[40,52,65,77], L3=all).`
- :63 `construct --mode real --layers 3,...,78` → `construct --mode real --layers 3,...,77`
- :103 `layers == 3..78` → `layers == 3..77`
- :163 table row: `**3..78 inclusive** (all 76 MoE layers); pilot L1=[40], L2=[40,53,65,78], L3=all` → `**3..77 inclusive** (the 75 DRAFT=0 MoE layers); pilot L1=[40], L2=[40,52,65,77], L3=all` (and cite `ASM-2504`)
- :177 table row: `layers 3..78, seed 20260716` → `layers 3..77, seed 20260716`

`poc/glm52-probe/f1k-harness/dump-patch/PATCH-NOTES.md:132` — `(real runs: 3..78)` → `(real runs: 3..77; layer 78 = MTP head, unreachable at DRAFT=0 [ASM-2504])`. (The dump patch/loader CODE needs no change — it is geometry-agnostic and its ASM-2488 invariant is exactly what enforces the corrected set.)

### 1.8 DOWNSTREAM QUANTITIES + acceptance gate (deliverables 6–7; gate STRENGTHENED in v2, G2 sidecar clause CORRECTED in v3)

**Carrier tensor:** `nc × nl × D × 4` bytes; `.kaec` file = `16 + 4·nl + 4·(96·nl·6144)`:
- nl=76: **179,306,816 B** (179.31 MB) per table → nl=75: **176,947,516 B** (176.95 MB); **Δ = −2,359,300 B = −1.316%** per table, across the 4 registered table basenames (`k-true.kaec`, `d0-seed7.kaec`, `d2-dict.kaec`, `k-drng-11.kaec`; derangement arms permute K's concept slots via `derangements.json` — no extra tables). None of these files exists yet (pre-construction), so no artifact hash is re-recorded — only the PROSPECTIVE sizes change.
- Each construction dump line carries 75 (not 76) `f32 sum[nl*D]` slots; construction pass count **4,608 = 96×16×3 UNCHANGED**; `construction-manifest.jsonl` (4,608 lines) is layer-free — **byte-identical, no regeneration** (its `a8cb3a8a` pin in `f1k.json` AND `f1k_gcp.py` stands).
- **Affordability floors — rationale (kept) + GATE (v2, the arbiter):** the floors `usd_total ∈ [$73, $155]`, `instance_hours ∈ [260.6, 900] h` are functions of the 19,964-prefill envelope, throughput, and rate — not of `nl` (`analysis/f1k.py:619–628`: `usd_total` min=`USD_TOTAL_MIN` / `instance_hours` min=`INSTANCE_HOURS_MIN`; the corrected geometry only REMOVES one dead dump/splice slot per pass, ~1.3% less carrier I/O — strictly less work). That inference stands as RATIONALE, but per review pt 4 the GATE decides: step **G4** below RUNS the affordability admissibility check post-correction and must CONFIRM the floors unchanged.

**Acceptance gate — MUST run GREEN before the correction lands** (round-4 lesson: the untouched driver's `--mock` is the emission-surface oracle). v2 hardens the v1 gate at three points (review pt 3 + pt 4): the stale-artifact rebuild (G1), the registered-geometry hard assertion (G2 — a ★ NEW code edit site), and the executable floor confirmation (G4). Exact commands, from repo root, run AFTER all §1 edits are applied in the working tree:

**G1 ★ — REBUILD the mock oracle input at the corrected geometry (closes the stale-pass hole).** `mock_e2e_carriers.py:39` takes `--carriers mock-out/carriers-6144` as a PRE-BUILT input and only rmtree's its own OUTPUT dirs; the committed stale artifact's `construction-report.json` still records `/binding/layers` = 76 entries 3..78 (verified 2026-07-17), so without this step the v1 gate could go green on the OLD geometry. Remove and regenerate (flags per `build_carriers.py` usage `:212–215`; `D=6144` is fixed by `mock_colibri_dump.py:39`; layers are passed through as `KAE_DUMP_LAYERS`):

```bash
cd poc/glm52-probe/f1k-harness
rm -rf mock-out/carriers-6144            # stale 76-layer artifact — RETIRED, not edited
python3 build_carriers.py construct --mode mock \
    --engine-cmd '["python3", "mock_colibri_dump.py"]' \
    --tokenizer-cmd '["python3", "mock_tokenizer.py"]' \
    --layers "$(python3 -c 'print(",".join(map(str, range(3, 78))))")" \
    --out mock-out/carriers-6144
python3 build_carriers.py verify --out mock-out/carriers-6144 --expect-mode mock
```
Expected: `construction complete: 4608 forward passes (mode=mock)`; the regenerated report's `/binding/layers` == 3..77 (75 entries); verify green. (Mock geometry may legally rehearse any layer list — we pass the corrected REGISTERED union explicitly so the rehearsal matches what G2 asserts.)

**G2 ★ — HARD registered-geometry assertion in `mock_e2e_carriers.py` (NEW edit site, gate-adjacent code, part of the landing commit; SIDECAR clause CORRECTED in v3, re-review pt 1).** The mock-positive path currently checks `table_bytes` against `car["layers"]` SELF-consistently (`:151–155` — `params_added == 96*car["layers"]*6144`, `table_bytes == 16 + 4*car["layers"] + 4*params_added`, both PARAMETRIC in `car["layers"]`; these stay) and never asserts the REGISTERED layer list — the second half of the stale-pass hole. **Semantics that v2 got wrong:** the sidecar `car` describes the **frozen-L PILOT-SELECTED subset actually spliced**, NOT the 75-layer master — `f1k_driver.py:2291–2296` does `frozen = load_frozen_lg(cfg, outdir)` → `kaec_subset(cfg["carriers"]["K"]["path"], frozen["layers"], …)` → `km = kaec_read(ksub)`, and `:2330` sets `car["layers"] = km["nl"]`, i.e. `len(frozen["layers"])`: **1** for L1=[40], **4** for L2=[40,52,65,77], **75** only for L3=all. v2's `assert car["layers"] == 75` would therefore FAIL a legitimate L1/L2 pilot green. The 75-layer / ids==3..77 hard check belongs on the **MASTER** geometry only (the construction-report master `layers` + master K table + `REGISTERED_SPLICE_LAYERS` — the re-review confirmed these already reject stale 3..78); the sidecar is validated against the SELECTED subset. Insert immediately after `K = drv.kaec_read(cfg["carriers"]["K"]["path"])` (currently `:141`; `frozen` is in scope from `drv.phase_pilot` at `:114`), before the `summary` dict:

```python
    # [ASM-2504] REGISTERED-GEOMETRY HARD GATE (layer re-freeze v3, re-review
    # pt 1): the oracle previously validated table_bytes against
    # car["layers"] self-consistently, so a STALE pre-built carriers dir
    # (76 layers, 3..78) could still pass. Bind the MASTER geometry
    # (construction report + master K table) to the registered union
    # EXACTLY (len==75, ids==3..77 — the real stale-76 guard); validate the
    # SIDECAR against the frozen-L PILOT-SELECTED subset actually spliced
    # (f1k_driver.py:2330 sets car["layers"] = km["nl"] of the
    # frozen["layers"] subset table — L1=1 / L2=4 / L3=75 are ALL
    # legitimate greens; a fixed ==75 here would be wrong).
    want_layers = list(drv.REGISTERED_SPLICE_LAYERS)
    assert want_layers == list(range(3, 78)) and len(want_layers) == 75, \
        "driver constant is not the ASM-2504 union 3..77 = 75"
    assert report["binding"]["layers"] == want_layers, \
        "STALE carriers dir: construction-report binding.layers != 3..77 (75)"
    assert K["layers"] == want_layers and K["nl"] == 75, \
        "STALE master table: .kaec layers != registered 3..77 (nl=75)"
    sel = list(frozen["layers"])   # pilot-selected splice subset (addendum 5)
    assert set(sel) <= set(want_layers) and car["layers"] == len(sel), \
        "sidecar carriers.layers != len(frozen-L pilot subset), or the " \
        "subset escapes the registered union 3..77"
```
This makes the oracle FAIL CLOSED on any pre-built artifact whose MASTER layer list ≠ `REGISTERED_SPLICE_LAYERS` — including a re-appearance of the 76-layer artifact — while staying GREEN for every legitimate pilot outcome: **L1 (car["layers"]==1), L2 (==4), L3 (==75) all pass; any splice id ≥ 78 (subset check vs 3..77) or a master `layers` of len ≠ 75 goes RED.** The `:151–155` parametric arithmetic then ties `params_added`/`table_bytes` to the same subset size. (Rejected alternative: a wrapper script outside `mock_e2e_carriers.py` — weaker, because the oracle itself would remain stale-passable when invoked directly.)

**G3 — the four v1 oracles (unchanged commands; G2's assertion now live inside the third):**
```bash
cd poc/glm52-probe/f1k-harness
python3 build_carriers.py selftest                       # 19 fail-closed generator probes
python3 f1k_driver.py --mock                              # full $0 end-to-end driver oracle
python3 mock_e2e_carriers.py                              # generator->driver acceptance + real-ingest refusal + G2 geometry gate
cd ../../.. && python3 tools/registry/registry-check.py   # ALL checks: frozen-drift, claims, account-lint, chain
```
Note: `f1k_driver.py --mock` and `mock_e2e_carriers.py` both end in the PINNED `analysis/f1k.py` ingest, whose cost schema (`:619–628`) already executes the ledger floors against the registered-scale mock figures (prior 146.0 / construction 521.2 h, ASM-2374 corner — round-6 precedent) — so the floors are exercised at the analysis surface here too.

**G4 ★ — affordability floors CONFIRMED by the executable gate (review pt 4).** The $0 floor+ceiling admissibility gate is `poc/gcp/f1k_gcp.py plan` (`cmd_plan` `:289–334`): it re-verifies EVERY launch pin (`verify_pins()` — including the ★ §1.5a re-pointed `FROZEN_SHA256` and `PINS["build_carriers.py"]`, so a botched re-pin fails HERE, not at VM launch), runs the reuse gate, then asserts a NON-EMPTY admissible `instance_hours` window `[max(260.6, 73/rate), min(900, 155/rate)]` at every quoted-band rate (0.19/0.20/0.24/0.28 $/h):

```bash
# requires KOT_GCP_PROJECT (source ~/.config/kot/gcp.env); $0 — no gcloud call, no spend
python3 poc/gcp/f1k_gcp.py plan
```
Expected output: exit 0; JSON with `"frozen_sha256": "<NEW hash>"`, `"usd_cap": 155.0`, `"instance_hours_window": [260.6, 900.0]`, `"frozen_rate_window": [0.0811, 0.5948]`, every `affordability_band.rate_*.window_nonempty == true`; final line `DRY-PLAN OK: pins verified, reuse-gate clear, SPOT + 750 GiB NVMe + non-empty ledger window across the quoted rate band.` — i.e. the floors **[$73, $155] / [260.6, 900] h print UNCHANGED post-correction**. Any moved floor, empty window, or pin mismatch exits nonzero and blocks landing.

**ALL of G1–G4 must exit 0.** `registry-check` passes first try only if the landing commit contains, together: the code/doc edits (incl. ★ `mock_e2e_carriers.py`, ★ `f1k_gcp.py`, ★ data-tree files), ★★ the recomputed A-time directory digest spliced over BOTH `513ed196…` embeds in `f1k.json` BEFORE the frozen hash was taken (§1.3b — else the record carries a stale self-assertion), the ASM-2504 append, the correction record, the corrected `f1k.json`, and the updated `frozen-index.json` (the recomputed `frozen_sha256` in BOTH places, and the SAME value in `f1k_gcp.py:51`).

---

## 2. SECONDARY DELIVERABLE — programme-wide blast-radius audit (RECOMMEND ONLY; no edits made)

Rule applied per site (v2, sharpened per review pt 6): a live surface's universe is decided by **that surface's OWN DRAFT pin** — live DRAFT=0 ⇒ Universe B (3..77/75); live DRAFT=1 (MTP ON) ⇒ 3..78/76 **legitimate**; over-committed-stats-inventory ⇒ Universe A (3-78/76) legitimate. **F1-K's own landing set (§1) depends on NO row below** — these are recommendations for other surfaces' own re-freezes.

| Site | Universe / DRAFT mode (own pin, cited) | Verdict | One-line basis | Frozen? |
|---|---|---|---|---|
| `docs/next/design/glm52-stage4-speed-cohort.md:62` "on 14 of the 76 MoE layers (3..78)" | **Live DRAFT=1, MTP ON** — `:208` "greedy decoding, **DRAFT=1 (MTP speculative decode ON — this cohort's entire point)**" | **LEAVE — v1's FIX-RECOMMENDED verdict REVERSED (review pt 6)** | at DRAFT=1 the MTP layer 78 IS reachable; 3..78/76 is this cohort's legitimate live geometry | working draft |
| `docs/next/design/glm52-stage4-drop-efficiency.md:20–21, 107, 427` (PREMISE "76 sparse MoE layers 3..78"; universe 19,456) | **Live DRAFT=0** — `:99` "All arms: DRAFT=0"; `:182` "MTP out of scope (DRAFT=0 everywhere). [STIPULATED: ASM-2390]" | **FIX-RECOMMENDED** (live-geometry statements → 3..77/75; keep 19,456 ONLY as a disclosed A-universe trace-inventory denominator) | its own :21 records the R1 builder correctly hard-coded 3..77 and was "corrected" the wrong way | working draft — lawful edit |
| `poc/glm52-probe/stage4/build_masks.py:77–79, 428, 471` `MAIN_LAYERS = range(3, 79)` + "layer 78 is a VALID MoE layer (review C1)"; `stage4/mock/gen_mock_telemetry.py:7, 17` `LAYERS = range(3, 79)` | Feeds the DRAFT=0 drop experiment, BUT has explicit special layer-78/MTP handling — `:502` the telemetry validator `expect_fail`-REJECTS an `"mtp\|78\|1"` cell ("rejects malformed cell id"), so 78 may be enumerated-then-rejected rather than actively spliced | **FIX at STAGE-4's OWN re-freeze** (needs DRAFT-mode + 78-handling resolution; **NOT part of F1-K's landing set — does not block**) *(v2 reclassified from v1's blanket FIX-RECOMMENDED)* | review C1's "layer 78 is a VALID MoE layer" is correct IFF the consuming surface is DRAFT=1 — resolve per-surface (speed cohort: yes; drop arms: no), don't blanket-invert in either direction [ASM-2504 live-surface rule] | working draft — stage-4 scope |
| `docs/next/design/glm52-expert-drop.md:323` (universal core ~139/layer across 76 layers) and :1709 (coverage over 76 MoE layers) | Committed-stats inventory (A) | **LEAVE** (optionally add a two-universe footnote) | counts cells of the committed trace roster — legitimately 76 | ASM-registered prose |
| `docs/next/design/glm52-expert-drop.md:1068, 1656` (bitmap ordering "76 MoE layers ascending 3…78, every layer present") + ASM-2344 R4 clause | Mask tables LOADED BY a live **DRAFT=0** engine — `:698` "DRAFT=0 (greedy, deterministic scoring)" — **load-bearing** | **FIX-RECOMMENDED at its own re-freeze** (reviewer pt 6 CONFIRMS: masks applied live at DRAFT=0 while serializing 76 bits): emit 3..77/75 per record (or explicitly declare the layer-78 row a disclosed dead entry — the clean fix is 75) | records are layer-KEYED (`<layer>:<64-hex>`), so no silent off-by-one, but "every layer present" + a 78 row is a false attestation of a splice surface the DRAFT=0 run cannot touch, and dose accounting (64/layer × 76) overstates by one layer | ASM-2344 registered ⇒ supersede-by-citation (new ASM), design NOT yet frozen (sequenced after F1-K freeze) |
| `docs/next/design/glm52-expert-drop.md:1474, 1517` ("76 MoE layers (3–78), not 75" correction notes) | Narrates the A-universe measurement | **LEAVE text, ADD note**: the "75→76 correction" was correct for Universe A only; cite ASM-2504 so it is not re-transported | registered prose |
| ★ **ASM-2488** claim text "For the real A(iv) union 3..78 this doubles as the check that every requested layer is a genuine MoE layer" (`dump-patch/asm-f1k-dump-2485-2491.json:46`) *(NEW row, v2 — review pt 5)* | The per-slot gated-count invariant itself is universe-AGNOSTIC (it is what enforces the corrected set); its "3..78" phrase is a B-universe misstatement | **NO in-place edit — registered ⇒ ASM-2504 amends by citation** (added to the §1.4 amends list) | append-only register discipline (ASM-2352) | registered |
| Registered ASM texts: ASM-2342 R3, ASM-2343 ("across 76 layers"), ASM-2344 R4, ASM-2406(1) in `registry/assumptions.jsonl` / `poc/glm52-probe/asm-glm-drop-r2-2340-2352.json` | 2342/2343: A (valid). 2406(1): B (wrong) | **NO in-place edit — ASM-2504 amends by citation** (this memo §1.4); expert-drop's own future re-freeze should supersede 2344's 76-layer clause | append-only register discipline (ASM-2352) | registered |
| `docs/next/design/glm52-followup-experiment.md` (F1-K DES §2.3) | States the grid QUALITATIVELY (no 76/78 literal found) | **LEAVE** | the DES never pinned a count; the realization lives in ASM-2406/generator-spec (fixed here) | frozen-adjacent |
| `poc/gcp/F1K-CONSTRUCTION-PLAN.md` | Documents the defect itself | **LEAVE** | it is the coordinator's verification record | memo |
| Historical run/mock logs (`opus-runs/*/run-log.jsonl`, `mock-out-*.log`), `F1K-AFFORDABILITY-DECISION.md` old-sha mentions | Historical witnesses | **LEAVE — never edit** | append-only run/decision records; mock logs untracked and regenerated | witnesses |

No other sites found (repo-wide search for `3..78`, `3-78`, `76 MoE`, `range(3, 79)`, `53,65,78`; remaining grep hits are unrelated ids/UUIDs). **Net (v2): the §1 landing set is complete without any stage-4 edit; stage-4's re-freeze owns its own resolution (bd follow-up, NEXT-ACTION step 7).**

---

## 3. Self-check table (mandatory; claim → citation)

| # | Claim | Citation |
|---|---|---|
| 1 | F1-K is a live DRAFT=0 MoE-input dump | `mock_colibri.py:154`, `mock_colibri_dump.py:64` ("MTP off (draft=0)"); frozen protocol mode |
| 2 | DRAFT=0-reachable MoE layers = 3..77 = 75; layer 78 = MTP head, excluded at DRAFT=0 | [MEASURED] `poc/gcp/probe-results/probe-results.json` + `m4.json` `/shape {75,3,77}` (weights `19f1a3d0`); [PER-PROTOCOL] `stage1-feasibility-manifest.md` B4 (~:112) |
| 3 | Frozen harness pins 3..78 = 76 | `build_carriers.py:287,290,293`; `f1k_driver.py:400`; `f1k.json` `/title`, `/pins/harness_manifest`, `/design/n_planned/freeze_manifest/A_pre_spend` |
| 4 | Run cannot execute as frozen (fail-closed both branches); the per-slot invariant is **ASM-2488** *(v1 miscited 2489)* | `kae-patch-draft/kae.h:194` (splice id ≥ n_layers → NULL); ASM-2488 per-slot gated-count invariant (`asm-f1k-dump-2485-2491.json:46` — claim names "a requested dump layer that never reaches moe()" as a fail-closed abort) |
| 5 | ASM-2342 R3 is true of Universe A only | `glm52-expert-profiling-plan-sol-20260715.md:22`; ASM-2342 R3 text (`registry/assumptions.jsonl:1148`) |
| 6 | The transport into Universe B happened at ASM-2406(1)/the freeze | ASM-2406 claim (1) (`registry/assumptions.jsonl:1217`); `generator-spec.json .candidate_splice_layers` |
| 7 | L2 = [40, 52, 65, 77] by the registered rule at top 77 | rule `round(linspace(40, top, 4))` [ASM-2406(1)]; arithmetic: 40, 52.33→52, 64.67→65, 77 |
| 8 | No committed mock/golden hardcodes 76 independently of the constants EXCEPT the pre-built `carriers-6144` oracle INPUT (stale; retired by rebuild); `analysis/f1k.py` untouched | §1.6 table; `f1k_driver.py:3602`; `build_carriers.py:1494–1517`; `analysis/f1k.py` (parametric KAEC arithmetic, `KAEC_MAX_LAYERS=128`); `git ls-files` mock-out = 0 |
| 9 | Table size 179,306,816 → 176,947,516 B (−1.316%); passes 4,608 unchanged; construction-manifest layer-free | `16+4·nl+4·96·nl·6144` arithmetic; `construction-manifest.jsonl` (4,608 text/span lines, no layer field) |
| 10 | Floors [$73,$155]/[260.6,900] h unmoved — by GATE, with the less-work argument as rationale only | ★ `f1k_gcp.py` `cmd_plan` `:289–334` (executable floor+window assertions, §1.8-G4, expected output stated); `analysis/f1k.py:619–628` floor schema executed in both mock oracles at registered-scale ledger figures; `F1K-AFFORDABILITY-DECISION.md` §2.2 |
| 11 | Changed pins = build_carriers sha (2 in-record sites) + frozen_sha256/frozen-index + ★ `f1k_gcp.py:51` `FROZEN_SHA256` + ★ `f1k_gcp.py:59` `PINS["build_carriers.py"]`; driver not sha-pinned anywhere | §1.5 table + §1.5a scan; grep of `f1k.json` and `f1k_gcp.py` `PINS` (no `f1k_driver` sha); analysis/KaE/corpus/seed pins byte-identical |
| 12 | ASM-2504 free; registered with landing commit; supersede-by-citation discipline; amends list includes ★ ASM-2488 | `registry/assumptions.jsonl` (last id ASM-2503, 2026-07-17); ASM-2352 amendment-discipline clause; `asm-f1k-dump-2485-2491.json:46` ("For the real A(iv) union 3..78" in ASM-2488's own claim) |
| 13 | No account-identifying strings in any proposed hashed byte range | this memo + §1.4/§1.5 JSON (pseudonymous owners only; registry-check `--account-lint` gate) |
| 14 | ★ The v1 oracle was stale-passable: `mock_e2e_carriers.py` consumes a PRE-BUILT carriers dir, rmtree's only its OWN output, and checks geometry self-consistently; the committed artifact still records 76 layers 3..78. **v3:** the G2 fix binds the MASTER geometry to 3..77/75 and the SIDECAR to the frozen-L pilot subset — v2's `car["layers"] == 75` clause would have FAILED legitimate L1/L2 greens (re-review pt 1) and is removed | `mock_e2e_carriers.py:39` (`--carriers` default = pre-built input), `:46` (rmtree outdir only), `:151–155` (self-consistent `table_bytes` arithmetic, no registered-list assert); `mock-out/carriers-6144/construction-report.json` `/binding/layers` len=76 min=3 max=78 (verified 2026-07-17); corrected assertion §1.8-G2 |
| 15 | ★ The GCP orchestrator hard-pins the OLD hashes and fail-closes at launch — the decisive re-pin omission | `f1k_gcp.py:49` ("verified at launch"), `:51` (`FROZEN_SHA256 = "505165ee…"`), `:59` (`PINS["build_carriers.py"] = "cda62364…"`), `:152–176` (`verify_pins()` dies ERR_F1K_PIN_FROZEN / ERR_F1K_PIN_MISMATCH) |
| 16 | ★ Exhaustive ops-script sha scan: `f1k_worker.sh` carries ZERO embedded hashes; `bringup_gcp.sh` carries only UNCHANGED pins (+1 comment echo) | hex-literal grep 2026-07-17: `f1k_worker.sh` 0 hits; `bringup_gcp.sh:24–25` (colibri commit `a78a06fc`, kae patch `11f8b458` — both untouched), `:43` (comment "505165ee") |
| 17 | ★ Data tree still asserts 76/3..78; TWO digests govern it *(v3 — v2's "no digest recompute" conclusion was FALSE, re-review pt 3)*: the `corpus_hashes` placeholder (realized-tables pin, PINNED-AT-INPUTS, binds at construction — status LEFT) and the ACTIVE **A-time INPUT-tree digest** `513ed196…` embedded in `f1k.json` — the §1.3/§1.3b edits INVALIDATE the latter, so pre-construction edits are lawful but NOT a digest no-op | `data/f1k-carriers-v1/README.md:45–47`, `manifest.json:10` ("ALL 76 MoE layers, engine ids 3..78 [MEASURED ASM-2342 R3]"); `f1k.json` `pins.corpus_hashes.f1k-carriers-v1` (value begins `"PINNED-AT-INPUTS:realized carrier tables…"`, verified) + `pins.corpus_hashes._recipe` (`kot-corpus-hash/1`, one line per regular file under `data/<corpus>/` recursive); the record's own "(A)-time carrier-input directory digest is UNCHANGED (no data/f1k-carriers-v1 edit)" sentence (violated by these edits — §1.3b) |
| 18 | ★ Stage-4 DRAFT modes read from each surface's OWN pin: speed-cohort DRAFT=1 (LEAVE); drop-efficiency DRAFT=0 (FIX); expert-drop DRAFT=0 (FIX); build_masks 78-handling ambiguous (deferred to stage-4 re-freeze) | `glm52-stage4-speed-cohort.md:208` (DRAFT=1, MTP ON, "this cohort's entire point"); `glm52-stage4-drop-efficiency.md:99` ("All arms: DRAFT=0") + `:182` (ASM-2390); `glm52-expert-drop.md:698` (DRAFT=0) + `:1068` (76-bit serialization); `build_masks.py:502` (`expect_fail` rejects `"mtp\|78\|1"` cell) |
| 19 | ★★ The sidecar `car["layers"]` is the frozen-L PILOT-SELECTED subset size (1 / 4 / 75), NOT the master 75 — the corrected G2 validates it against `frozen["layers"]` (len match + subset of 3..77), and stays GREEN on legitimate L1/L2/L3, RED on any id ≥ 78 or master len ≠ 75 | `f1k_driver.py:2291–2296` (`load_frozen_lg` → `kaec_subset(…, frozen["layers"], …)` → `km = kaec_read(ksub)`), `:2330` (`"layers": km["nl"]`); `mock_e2e_carriers.py:114` (`frozen = drv.phase_pilot(…)` in scope at the `:141` insert site), `:151–155` (parametric arithmetic ties `params_added`/`table_bytes` to the same subset size); pilot sets `build_carriers.py` §1.1(c) (L1=[40] nl=1, L2=[40,52,65,77] nl=4, L3=all nl=75) |
| 20 | ★★ A-time directory-digest re-pin mechanics: `513ed196…` lives at TWO `f1k.json` text sites (`A_pre_spend` clause (5), ~byte 19768; inside the `corpus_hashes` placeholder text, ~byte 53286 — single-line JSON, cite by path); recomputed by `python3 tools/registry/corpus-pin.py f1k-carriers-v1` (prints `{"_recipe": …, "f1k-carriers-v1": "<64-hex>"}`) AFTER the data edits and spliced BEFORE the `frozen_sha256` recompute; `registry-check --corpus-pins` skips PINNED-AT-INPUTS placeholders, so corpus-pin.py is the mechanical reproducer; seq-1 correction record + run-logs carrying `513ed196` are historical witnesses (LEAVE) | `registry/experiments/f1k.json` (both embeds + the "UNCHANGED (no data/f1k-carriers-v1 edit)" sentence, verified 2026-07-17); `tools/registry/corpus-pin.py:4–17` (usage + "this tool IS the recipe"); `tools/registry/registry-check.py:179` (placeholder skip); `registry/corrections/f1k/1-prefreeze-correction.json` (historical carrier) |

---

## 4. NEXT-ACTION (liftable; coordinator runs in order — ONE landing commit for steps 1–6; order CORRECTED in v3: the ★★ digest recompute (step 2) MUST follow the data edits and precede the frozen-hash recompute)

1. **Apply ALL edits (code + data):** `build_carriers.py` (§1.1 a–d), `f1k_driver.py` (§1.2), `generator-spec.json` (§1.3), ★ `data/f1k-carriers-v1/README.md` + `manifest.json` (§1.3b), ★ `mock_e2e_carriers.py` registered-geometry hard gate (§1.8-G2, v3 pilot-aware form), harness `README.md` + `PATCH-NOTES.md` (§1.7), ★ `poc/gcp/f1k_gcp.py` / `bringup_gcp.sh:43` / `poc/gcp/README.md:5` comment echoes (§1.5a; the two f1k_gcp.py CODE pins take the values computed in steps 3–4).
2. ★★ **Recompute the A-time directory digest** (v3; re-review pt 3 — AFTER step 1's three `data/f1k-carriers-v1/` edits, which change it): run `python3 tools/registry/corpus-pin.py f1k-carriers-v1` from repo root — it prints `{"_recipe": "<the kot-corpus-hash/1 recipe string>", "f1k-carriers-v1": "<new 64-hex digest>"}` (the recipe's reference implementation, `corpus-pin.py:4–17`). Splice the new digest over **BOTH** `513ed196…` embeds in `registry/experiments/f1k.json` — `/design/n_planned/freeze_manifest/A_pre_spend` clause (5) AND inside the `/pins/corpus_hashes/f1k-carriers-v1` placeholder text (PINNED-AT-INPUTS prefix/status untouched) — and fill the two ★★ digest entries in the correction record's `changes` (§1.5). MUST precede step 4: the frozen hash covers the record bytes.
3. **Recompute the build_carriers sha** (`sha256sum poc/glm52-probe/f1k-harness/build_carriers.py`) and splice it into **THREE code/record sites**: the two `registry/experiments/f1k.json` sites (§1.5 changes) **and ★ `poc/gcp/f1k_gcp.py:59` `PINS["build_carriers.py"]`**; apply the §1.5 text corrections to `/title`, `/pins/harness_manifest`, `/design/n_planned/freeze_manifest/A_pre_spend`.
4. **Re-record the frozen hash** (only AFTER steps 2–3 — all record-byte changes in): recompute `kot_common.frozen_hash` of the corrected record; write it to `f1k.json.frozen_sha256`, `registry/frozen-index.json["f1k"]`, **and ★ `poc/gcp/f1k_gcp.py:51` `FROZEN_SHA256`** (all three the SAME value, same commit); fill `refrozen_sha256` in `registry/corrections/f1k/2-layer-geometry-refreeze.json` (§1.5) and add that file.
5. **Register the ASM:** append the §1.4 ASM-2504 line to `registry/assumptions.jsonl` (same commit — no dangling id).
6. **Gate (§1.8, strengthened):** ★ G1 rebuild `mock-out/carriers-6144` at 3..77 (rm -rf + `construct --mode mock` + `verify --expect-mode mock`); G3 `build_carriers.py selftest`, `f1k_driver.py --mock`, `mock_e2e_carriers.py` (now enforcing the ★ G2 master+pilot-subset assertions), `tools/registry/registry-check.py`; ★ G4 `python3 poc/gcp/f1k_gcp.py plan` confirming the floors [$73,$155]/[260.6,900] h and rate windows UNCHANGED (`DRY-PLAN OK`). ALL must exit 0. If any fails, fix within the same commit before landing; nothing lands red.
7. **Land + push** per session protocol (`git pull --rebase && git push`), then **open the maintainer GitHub issue** for the record: title "F1-K v2: FREEZE DEFECT corrected — DRAFT=0 layer set re-frozen 3..78→3..77 (75), $0, all scientific pins preserved"; body = §0 table + §1.5/§1.5a changed-pin tables + §2 blast-radius table + a link to this memo; note the stage-4/expert-drop recommendations explicitly as OPEN (not auto-fixed) and the speed-cohort LEAVE reversal.
8. **File follow-up issues** (bd) for the §2 FIX/deferred sites: stage-4's own re-freeze — drop-efficiency live-geometry fix (DRAFT=0, `:99`), `build_masks.py`/`gen_mock_telemetry.py` DRAFT-mode + layer-78-handling resolution (enumerate-then-reject vs active splice, `:502`), speed-cohort verdict recorded as LEAVE (DRAFT=1 legitimate) — and expert-drop's bitmap ordering (needs its own supersede-by-citation ASM at its re-freeze, per `:1068`).

---

**STATUS:** core + 4 of 6 v2 fixes APPROVED (re-review pts 2/4/5/6 RESOLVED — re-pin inventory, floor gate, ASM-2488 citation, blast-radius reclassification; preserved unchanged); v3 closes the LAST TWO must-fixes (pilot-aware sidecar gate §1.8-G2, A-time directory-digest re-pin §1.3b/§1.5/§4-step-2), completing the landing set; the $0-mock oracle (§1.8 G1–G3) + `registry-check --frozen-drift` are the mechanical final gates.
