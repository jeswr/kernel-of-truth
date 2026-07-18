# F1-K driver `PIN=<stats-file>` FIX — exact diffs + re-freeze mechanics (kot-correction/1 seq 3)

**Author:** designer-20 (design memo only — NO spend, NO VM, NO git action, NO registry write performed by this pass; the coordinator applies everything below through the review-gate in ONE landing commit)
**Version:** v4 (2026-07-18) — v2 closed the round-1 NEEDS-FIX items (`poc/gpt56-review/f1k-pin-fix-review-VERDICT.md`); v3 closed the 3 remaining round-2 findings (`poc/gpt56-review/f1k-pin-fix-rereview-VERDICT.md`); v4 closes the 2 remaining round-3 findings (`poc/gpt56-review/f1k-pin-fix-round3-VERDICT.md`, APPROVE-WITH-FIXES): (2) the spawn-to-checkpoint crash window in the missing-ledger predicate — closed by a durable SPEND-START sentinel fsynced BEFORE `Popen` (§1d2, §1e), and (3) §7-B1n was not a valid negative gate (`! python3` accepted ANY nonzero exit; the printed B1 commands carried a non-executable placeholder) — closed by the reusable exact splice implementation `poc/gcp/f1k_repin_splice.py` + branch-specific assert-message/exit-code assertions (§4, §7). Round-3 CLOSED items — the descriptor-bound evidence (#1), the splice guards themselves (#3 first half, independently exercised by the reviewer), and the regression sweep (#4) — are untouched except where a v4 fix necessarily intersects (the §1e predicate gains the sentinel; the §4 splice moves verbatim into file form, guards byte-stable). Logged in the Revision log (v4 table)
**Date:** 2026-07-18
**Status:** DRAFT v4 for coordinator review-gate → apply → LOCAL working-tree re-pin recompute (splice-guard negative probe first) → $0-mock oracle → land (ONE commit) → registry-check green
**Framing — stated plainly:** this is the **lawful, truthful-pinning PREREQUISITE for the GCP construction — NOT a science change.** The frozen DESIGN defines `PIN=<stats-file>` (`docs/next/design/glm52-followup-experiment.md` §7.1, lines 638–639); the code as written cannot run it and can ONLY emit a **false pinning attestation** (`f1k_driver.py:711–741` accepts the literal `"1"`; `analysis/f1k.py:648–651` schema-locks the ledger to it). Fixing this makes the implementation CONFORM to the freeze (`F1K-AFFORDABILITY-DECISION.md` §5.1 reading, endorsed; `F1K-CONSTRUCTION-PLAN.md` §5). It changes NO window, cap, endpoint, protocol step, power number, seed, or claim envelope — but it edits the sha-pinned `analysis/f1k.py`, so it re-freezes via the same kot-correction/1 mechanics the layer re-freeze used (seq 2 precedent: `registry/corrections/f1k/2-layer-geometry-refreeze.json`; `poc/gcp/F1K-LAYER-REFREEZE.md` §1.5).

---

## 0. The frozen mandate: `PIN=<path>` ONLY — the legacy literal `"1"` is REFUSED

**Which semantics does the frozen design mandate?** `PIN=<stats-file>` ONLY. Grounds:

1. **The design of record** pins the knob table verbatim: `PIN=<file>` — "per-arm pin list (the routing intervention)"; `PIN_GB` — "value fixed at bring-up from measured free RAM after dense weights + OS; recorded in the run manifest" (`glm52-followup-experiment.md` §7.1:638–639). No `PIN=1` form appears anywhere in the frozen design. [PER-PROTOCOL]
2. **The engine's own semantics** (the integration point the design cites) are file-based: the pinned hot set is "loadable from a stats file `PIN=stats.txt`" (`docs/next/design/glm52-kernel-integration-northstar.md:92`). [STIPULATED — fetch-grade upstream semantics, ASM-1971 rider: re-verified from the checkout at bring-up]
3. **Therefore `PIN="1"` was never a lawful value.** To the engine it is (at best) a stats-file path named `1` — it pins nothing, while the driver/ledger attest pinning. Accepting BOTH forms would preserve exactly the false-attestation channel this fix closes (`F1K-AFFORDABILITY-DECISION.md` §3 F4/v3-fix-5). So the fix accepts `PIN=<path>` **only** and REFUSES the literal `"1"` with a named error.

**Scope honesty (vs `F1K-CONSTRUCTION-PLAN.md` §5 items 6–7):** item 6's per-arm pin map is realized at its own admissible MINIMUM — one shared bring-up-derived pin for all arms, **recorded as such** (`pin_scope: "shared-all-arms"`, the §7.1 matched-budget discipline; per-arm derivation, if pilot routing counters show arm drift, is a separate future lawful extension with its own schema correction). Item 7 (realized `h_pin ≥ 0.60` floor) is an addendum-(7)/affordability-gate consumption with its own registered-floor decision — **out of scope here**, deliberately: this fix adds no new science gate, only truthful provenance. [STIPULATED scope decision]

**The pin-file reality (stated honestly):** the M4 dev-item pin (`pin_50gb.stats`, sha `6802cc97…` — `poc/gcp/probe-results/pin_50gb.sha256`, `m4.json /pin`) lives on GCS (`gs://kot-f1k-estate-85e2ca29/f1k/probe/`), NOT in this repo, and it **does NOT transfer**: h_pin is a property of model × item distribution, so the campaign pin is **RE-DERIVED on the REAL construction corpus at bring-up** (`STATS=on` over the real prefills; `F1K-CONSTRUCTION-PLAN.md` §5.4). The driver fix therefore accepts *whatever bring-up-produced stats-file the config names* and pins its content hash; the $0-mock oracle exercises the accept+hash+verify path with a **MOCK pin-file** (§6) and never requires the GCS artifact. [MEASURED: the pin-file line format `<layer> <expert> <count>` int triples — `poc/gcp/probe-results/accum20.stats` (16,184 lines, real engine STATS output on the GCP box); format re-verified at bring-up per ASM-1971.]

---

## 1. PRIMARY DIFF — `poc/glm52-probe/f1k-harness/f1k_driver.py` (NOT sha-pinned; see §4)

### 1a. Header `[FIX-5]` note (:48–50)

```diff
-  [FIX-5] Expert pinning ENFORCED + RECORDED: engine env must carry PIN=1
-          and PIN_GB>0 (glm52-f1k-cost-reduction.md lever 2); realized
-          pinning semantics enter the resume-safe ledger and the sidecar.
+  [FIX-5] Expert pinning ENFORCED + RECORDED (as corrected by the
+          ASM-2513 PIN=<stats-file> fix, 2026-07-18): engine env must
+          carry PIN=<bring-up-derived hot-expert stats-file> and
+          PIN_GB>0 (frozen semantics glm52-followup-experiment.md
+          §7.1:638-639; cost lever 2 glm52-f1k-cost-reduction.md /
+          ASM-2205); the stats-file is validated + content-hashed FROM
+          BYTES, engine arming is verified from the pin banner/counters
+          (never trusted from the flag), and hash + PIN_GB + realized
+          experts_pinned enter the resume-safe ledger, the sidecar, and
+          the [R10-4] resume-auth binding. The legacy literal PIN="1"
+          is REFUSED (it was never engine semantics and could only emit
+          a false pinning attestation).
```

### 1b. `validate_pinning` (:711–741) — full replacement (preceded by the new `PIN_BASENAME_RE` module constant [v2, review #3]), plus a new `attested_pinning` helper immediately after it (before `def validate_power`, :744)

Old (verbatim, :711–741):

```python
def validate_pinning(cfg):
    """[FIX-5] ENFORCE + RECORD expert pinning [COST lever 2 / ASM-2205:
    'expert-pinning + warm page-cache, priced conservatively at 1.20x';
    bringup.sh step 6: configured via the engine's PIN= / PIN_GB env].
    Optional pass-through is not enough: an unpinned run silently voids the
    $155 ceiling arithmetic [R6-3/ASM-2374]. Realized values are recorded
    in the ledger and sidecar so the metered speedup resolves ASM-2205."""
    env = (cfg.get("engine") or {}).get("env") or {}
    pin = env.get("PIN")
    pin_gb = env.get("PIN_GB")
    if str(pin) != "1":
        fail("ERR_F1K_PINNING",
             "engine.env.PIN must be \"1\" (expert pinning ENFORCED — the "
             "$155 ceiling prices the 1.20x pinning lever; COST item 2 / "
             "ASM-2205/ASM-2374; got %r)" % (pin,))
    try:
        gb = float(pin_gb)
    except (TypeError, ValueError):
        gb = -1.0
    if gb <= 0:
        fail("ERR_F1K_PINNING",
             "engine.env.PIN_GB must be a positive GB budget (got %r) — "
             "realized pinning semantics are a recorded cost-model input "
             "[COST item 2]" % (pin_gb,))
    return {"PIN": "1", "PIN_GB": gb,
            "semantics": "PIN=1 pins the hot expert working set resident; "
                         "PIN_GB = pinned budget in GB. The 1.20x-"
                         "pessimistic throughput lever of the $155 ceiling "
                         "[glm52-f1k-cost-reduction.md item 2 / ASM-2205; "
                         "REVISION-6 cap ASM-2374]; realized speedup "
                         "resolves ASM-2205 from the metered ledger."}
```

New:

```python
PIN_BASENAME_RE = re.compile(r"(?!1\Z)[A-Za-z0-9._+-]{1,255}")
# [v2, review #3] VERBATIM mirror of the PINNED analysis schema's
# expert_pinning.PIN pattern (analysis/f1k.py §2a:
# r"^(?!1\Z)[A-Za-z0-9._+-]{1,255}\Z", applied via re.fullmatch — the
# schema side is the AUTHORITATIVE copy; this driver-side constant must
# stay textually identical to it, checked by the §1i pin_badname probe).
# Enforced at CONFIG LOAD so a basename the pinned schema would reject
# can never run first and be rejected only AFTER spend.


def validate_pinning(cfg):
    """[FIX-5]+[ASM-2513] ENFORCE + RECORD expert pinning [COST lever 2 /
    ASM-2205: 'expert-pinning + warm page-cache, priced conservatively at
    1.20x'; bringup.sh step 6: configured via the engine's PIN= / PIN_GB
    env]. FROZEN SEMANTICS (glm52-followup-experiment.md §7.1:638-639):
    PIN=<stats-file> — the hot-expert pin list — with PIN_GB fixed at
    bring-up from measured free RAM and recorded in the manifest; the
    engine loads the pinned hot set FROM a stats file
    (glm52-kernel-integration-northstar.md:92 "pin[layer] ... loadable
    from a stats file PIN=stats.txt"). The pre-fix literal PIN=="1" was
    NEVER the frozen (or engine) semantics: the engine would treat it as
    a stats-file path named '1', pin nothing, and the ledger would still
    attest pinning — the false pinning attestation this fix closes
    (F1K-AFFORDABILITY-DECISION.md §3/§5.1). Optional pass-through is
    still not enough: an unpinned run silently voids the $155 ceiling
    arithmetic [R6-3/ASM-2374]. The stats-file is validated (exists,
    non-empty UTF-8, M4-measured '<layer> <expert> <count>' int-triple
    lines — poc/gcp/probe-results/accum20.stats; format re-verified at
    bring-up per ASM-1971) and its content sha256 is DERIVED FROM BYTES
    and recorded in ledger + sidecar + the [R10-4] resume-auth binding,
    so the metered speedup resolves ASM-2205 against a NAMED, HASHED
    pin. Engine-side arming is separately verified fail-closed from the
    pin banner/counters (check_pin_engagement). NOTE: the M4 dev-item
    pin (pin_50gb.stats, 6802cc97...) does NOT transfer — the campaign
    pin is RE-DERIVED on the real construction corpus at bring-up
    (F1K-CONSTRUCTION-PLAN.md §5.4); this function accepts whatever
    bring-up-produced stats-file the config names and pins its hash."""
    env = (cfg.get("engine") or {}).get("env") or {}
    pin = env.get("PIN")
    pin_gb = env.get("PIN_GB")
    if pin is None or str(pin).strip() in ("", "0", "1"):
        fail("ERR_F1K_PINNING",
             "engine.env.PIN must be the PATH of the bring-up-derived "
             "hot-expert stats-file (frozen semantics PIN=<stats-file>, "
             "glm52-followup-experiment.md §7.1:638; the legacy literal "
             "\"1\" is REFUSED — it was never engine semantics and could "
             "only emit a false pinning attestation [ASM-2513]. The $155 "
             "ceiling prices the 1.20x pinning lever; COST item 2 / "
             "ASM-2205/ASM-2374; got %r)" % (pin,))
    ap = os.path.abspath(str(pin))
    if not PIN_BASENAME_RE.fullmatch(os.path.basename(ap)):
        fail("ERR_F1K_PINNING",
             "engine.env.PIN basename %r violates the PINNED ledger "
             "schema's rule [A-Za-z0-9._+-]{1,255} excluding \"1\" "
             "(analysis/f1k.py cost.expert_pinning.PIN) — enforced HERE "
             "at config load so a run can never spend first and be "
             "schema-rejected after [ASM-2513 v2 review #3]"
             % (os.path.basename(ap),))
    try:
        raw = Path(ap).read_bytes()
    except OSError as e:
        fail("ERR_F1K_PINNING",
             "engine.env.PIN stats-file %s is not readable (%s) — a pin "
             "that cannot be loaded would leave the run UNPINNED while "
             "the ledger attests pinned [ASM-2513]" % (ap, e))
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        fail("ERR_F1K_PINNING",
             "engine.env.PIN stats-file %s is not UTF-8 text (%s) — not "
             "an engine stats file [ASM-2513]" % (ap, e))
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        fail("ERR_F1K_PINNING",
             "engine.env.PIN stats-file %s is EMPTY — pins nothing "
             "[ASM-2513]" % ap)
    for i, ln in enumerate(lines):
        parts = ln.split()
        if len(parts) != 3 or not all(p.isascii() and p.isdigit()
                                      for p in parts):
            # [v2, review #2] ASCII digits ONLY: bare str.isdigit()
            # admits Unicode digit codepoints — int() silently ACCEPTS
            # some (Arabic-Indic '٣' -> 3) and CRASHES on others
            # (superscript '²' -> ValueError) [MEASURED, python3
            # 2026-07-18]; neither is the M4-measured ASCII format.
            fail("ERR_F1K_PINNING",
                 "engine.env.PIN stats-file %s line %d is not the "
                 "M4-measured '<layer> <expert> <count>' non-negative "
                 "ASCII int triple (%r) — malformed pin lists are "
                 "refused, never silently skipped [ASM-1971 fetch-grade "
                 "rider: format re-verified at bring-up; a semantic "
                 "surprise halts for a protocol amendment BEFORE data "
                 "collection]" % (ap, i + 1, ln[:80]))
    try:
        gb = float(pin_gb)
    except (TypeError, ValueError):
        gb = -1.0
    if not 0.0 < gb < float("inf"):
        # [v2, review #2] FINITE positive only: float('nan') <= 0 is
        # False and float('inf') > 0 is True [MEASURED, python3
        # 2026-07-18], so the v1 `gb <= 0` check let NaN/inf through to
        # fail only at the post-spawn banner-budget comparison — i.e.
        # AFTER spend. NaN fails every comparison here; inf fails the
        # upper bound; both are refused at config load.
        fail("ERR_F1K_PINNING",
             "engine.env.PIN_GB must be a FINITE positive GB budget "
             "(got %r; NaN/inf REFUSED — a non-finite budget can never "
             "coherently match an engine banner and must fail BEFORE "
             "spend) — fixed at bring-up from measured free RAM and "
             "recorded [DES §7.1:639; COST item 2; ASM-2513 v2]"
             % (pin_gb,))
    env["PIN"] = ap          # engine receives the resolved absolute path
    return {"PIN": os.path.basename(ap),
            "pin_file_sha256": hashlib.sha256(raw).hexdigest(),
            "pin_file_lines": len(lines),
            "PIN_GB": gb,
            "pin_scope": "shared-all-arms",
            "semantics": "PIN=<stats-file> pins the hot expert working "
                         "set resident (top experts by count under the "
                         "PIN_GB budget); PIN_GB fixed at bring-up from "
                         "measured free RAM [DES §7.1:638-639]. One "
                         "shared bring-up-derived pin across all arms, "
                         "recorded as such (matched-budget discipline; "
                         "F1K-CONSTRUCTION-PLAN.md §5 item 6 minimum "
                         "realization). The 1.20x-pessimistic throughput "
                         "lever of the $155 ceiling [glm52-f1k-cost-"
                         "reduction.md item 2 / ASM-2205; REVISION-6 cap "
                         "ASM-2374]; realized speedup resolves ASM-2205 "
                         "from the metered ledger; engine arming "
                         "verified from the pin banner/counters "
                         "[ASM-2513]."}


def attested_pinning(ledger):
    """[ASM-2513] The expert_pinning record is emitted ONLY once engine
    arming was POSITIVELY verified this run (check_pin_engagement
    recorded experts_pinned from the pin banner/counters). A sidecar
    attesting pinning without an engine attestation would re-open the
    false-attestation channel this fix closes — fail closed instead."""
    ep = dict(ledger.d.get("expert_pinning") or {})
    n = ep.get("experts_pinned")
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        fail("ERR_F1K_PINNING",
             "emission without a verified engine pin attestation "
             "(expert_pinning.experts_pinned=%r) — the pin banner/"
             "counters were never positively verified this run; a "
             "pinning attestation is never emitted on trust [ASM-2513]"
             % (n,))
    return ep
```

(`os`, `hashlib`, `Path` are already imported at module top — no import diff. Note `validate_pinning` deliberately resolves `env["PIN"]` to the absolute path in-place so `arm_env`'s `cfg["engine"]["env"]` pass-through hands the engine the resolved path.)

### 1c. Pin-engagement verification — INSERT immediately BEFORE `def run_scoring_pass` (:1682), mirroring the `[FIX-2]` `check_kae_engagement` pattern (:1615–1680)

```python
PIN_ARMED_RE = re.compile(
    r"\[PIN\] hot-expert store armed: pinned (\d+) experts?, "
    r"([0-9.]+) GiB \(budget ([0-9.]+) GiB\) from (\S+)")
#   [MOCK mock_colibri.py pin banner. The REAL colibri pin-report wording
#    is FETCH-GRADE (ASM-1971) — re-verified from the checkout at the
#    bring-up knob-semantics re-verification (DES §7.1: "any semantic
#    surprise ... halts the run for a protocol amendment BEFORE data
#    collection, never after"). This driver is NOT sha-pinned (frozen
#    record: "f1k_driver.py, not sha-pinned here"), so aligning this
#    regex to the verified real banner is a recorded run-log amendment,
#    not a re-freeze; the PINNED analysis carries only the pin-file HASH
#    + counters, never the banner format — deliberately, so bring-up
#    format alignment cannot touch the frozen surface.]
PIN_DISABLED_MARKERS = (
    "[PIN] cannot open", "[PIN] malformed", "[PIN] no experts",
    "pinning DISABLED",
)
PIN_CHECKS = {"n": 0}


def check_pin_engagement(stderr_file, stderr_path, banner_text, env,
                         where, ledger=None, *, stderr_start):
    """[ASM-2513] POSITIVE pin-engagement verification: PIN=<stats-file>
    in the env REQUIRES a pin-armed banner (on captured stderr or the
    pre-result stdout banners) whose COUNTERS confirm a hot store
    actually loaded — verify, never trust the env flag [F4/
    F1K-AFFORDABILITY-DECISION.md §3; CONSTRUCTION-PLAN §5]. Mirrors
    [FIX-2]: called BEFORE the first scored item is accepted. Coherence:
    1 <= experts_pinned <= pin-file lines; the banner's used GiB is
    strictly positive; the banner's budget equals the validated PIN_GB
    (1% tolerance); the banner's source file is the validated pin file;
    the file bytes still hash to the ledger's pin_file_sha256 (no
    mid-run swap). Realized experts_pinned is recorded in the
    resume-safe ledger (and thence the sidecar via attested_pinning).
    [v2, review #2 — SECURITY] `stderr_start` is the BYTE OFFSET of the
    stderr log captured by run_scoring_pass AFTER opening the log and
    BEFORE spawning the engine: the log has a DETERMINISTIC filename
    and is opened in APPEND mode, so after an interruption it still
    holds a PRIOR invocation's armed banner — v1's whole-file scan let
    that stale banner authorize a NEW process that never armed (a false
    attestation, the exact channel this fix closes). Only the slice
    [stderr_start:] — bytes this invocation's engine wrote — plus this
    invocation's freshly collected stdout banners may satisfy the
    check. A log shorter than stderr_start (truncated under us) is
    refused outright.
    [v3, re-review #1 — SECURITY] The evidence is DESCRIPTOR-BOUND:
    `stderr_file` is the very file object whose descriptor the child
    inherited (Popen(stderr=errf) dups it), and the slice is read with
    os.fstat + os.pread ON THAT DESCRIPTOR — a rotation/replacement of
    the PATHNAME between spawn and check cannot substitute evidence
    (the v2 by-name Path.read_bytes() re-open could: a replacement of
    length >= stderr_start carrying a stale banner after the offset
    passed the short-file guard). `stderr_path` is retained for error
    messages ONLY. `stderr_start` is a REQUIRED keyword-only argument
    (the permissive =0 default is REMOVED): no call site can silently
    fall back to whole-file semantics. Concurrent-ownership honesty
    [best-effort, tagged]: §1d holds a non-blocking exclusive flock on
    the log descriptor for the whole invocation, which REFUSES a
    second cooperating driver instance on the same path (the realistic
    double-resume race, incl. same-inode openers); an UNCOOPERATIVE
    same-box writer appending a forged banner to the same inode is
    invisible to advisory locking — that residue is outside the threat
    model (such a writer could equally forge the pin file itself
    before hashing) and is named here, not hidden."""
    if not env.get("PIN"):
        fail("ERR_F1K_PINNING",
             "%s: engine env carries NO PIN at engagement time — "
             "pinning is MANDATORY (validate_pinning already passed at "
             "config load, so a missing PIN here means the env was "
             "corrupted between load and spawn); the engagement check "
             "is never silently skipped [ASM-2513 v2 review #2]" % where)
    PIN_CHECKS["n"] += 1
    # [v3, re-review #1] fstat + pread on the RETAINED descriptor —
    # never a by-name re-open (see docstring; requires the §1d "a+"
    # open mode: os.pread on a write-only "a" descriptor raises EBADF
    # [MEASURED, this box 2026-07-18])
    st = os.fstat(stderr_file.fileno())
    if stderr_start > st.st_size:
        fail("ERR_F1K_PINNING",
             "%s: stderr log %s (%d bytes at the retained descriptor) "
             "is SHORTER than the pre-spawn offset %d — the log was "
             "truncated under this invocation; no banner in it is "
             "attributable [ASM-2513 v2 review #2 / v3 re-review #1]"
             % (where, stderr_path, st.st_size, stderr_start))
    # ONLY the current invocation's slice of the SAME file object the
    # child wrote to — never a prior run's banner, never a pathname
    # decoy's bytes
    raw_slice = os.pread(stderr_file.fileno(),
                         st.st_size - stderr_start, stderr_start)
    text = raw_slice.decode("utf-8", errors="replace")
    text = text + "\n" + (banner_text or "")
    disabled = [m for m in PIN_DISABLED_MARKERS if m in text]
    if disabled:
        fail("ERR_F1K_PINNING",
             "%s: engine reported pinning DISABLED (%s) with PIN=%s — "
             "the run would stream UNPINNED while the ledger attests "
             "pinned (voids the ASM-2205/ASM-2374 $155 lever); fail "
             "closed [ASM-2513]" % (where, disabled, env.get("PIN")))
    m = PIN_ARMED_RE.search(text)
    if not m:
        fail("ERR_F1K_PINNING",
             "%s: no positive pin-armed banner for PIN=%s (stderr: %s) "
             "— a hot store was never verifiably loaded; a pinning "
             "attestation is never emitted on trust [ASM-2513]"
             % (where, env.get("PIN"), stderr_path))
    n_pinned, gb_used = int(m.group(1)), float(m.group(2))
    gb_budget, src = float(m.group(3)), m.group(4)
    if not gb_used > 0.0:
        # [v2, review #2] a banner attesting 0.000 GiB resident pinned
        # NOTHING regardless of its expert count — refuse (NaN also
        # fails this comparison)
        fail("ERR_F1K_PINNING",
             "%s: engine pin banner reports %.3f GiB used — a hot "
             "store holding zero bytes resident is not a pinned store; "
             "a pinning attestation is never emitted for it "
             "[ASM-2513 v2]" % (where, gb_used))
    rec = validate_pinning({"engine": {"env": dict(env)}})
    if src != rec["PIN"]:
        fail("ERR_F1K_PINNING",
             "%s: engine pinned from %r != the validated stats-file %r "
             "— wrong pin loaded [ASM-2513]" % (where, src, rec["PIN"]))
    if not 1 <= n_pinned <= rec["pin_file_lines"]:
        fail("ERR_F1K_PINNING",
             "%s: engine reports %d pinned experts vs a stats-file "
             "listing %d — incoherent counters (a zero or over-listed "
             "pin is not a verified hot store) [ASM-2513]"
             % (where, n_pinned, rec["pin_file_lines"]))
    if abs(gb_budget - rec["PIN_GB"]) > 0.01 * max(1.0, rec["PIN_GB"]) \
            or gb_used > gb_budget * 1.01:
        fail("ERR_F1K_PINNING",
             "%s: engine pin budget %.3f GiB / used %.3f GiB vs the "
             "validated PIN_GB=%.3f — budget mismatch (matched-budget "
             "discipline DES §7.1) [ASM-2513]"
             % (where, gb_budget, gb_used, rec["PIN_GB"]))
    if ledger is not None:
        lp = ledger.d["expert_pinning"].get("pin_file_sha256")
        if lp != rec["pin_file_sha256"]:
            fail("ERR_F1K_PINNING",
                 "%s: pin stats-file content hash %s != the ledger's "
                 "%s — the pin file changed MID-RUN; a campaign never "
                 "silently swaps its pin [ASM-2513/R10-4]"
                 % (where, rec["pin_file_sha256"], lp))
        ledger.d["expert_pinning"]["experts_pinned"] = n_pinned
        ledger._write()
```

### 1d. `run_scoring_pass` — capture the pre-spawn stderr offset; write the SPEND-START sentinel BEFORE spawn [v4]; retain skipped stdout banners; verify pin at first result (5 hunks)

First hunk (at the stderr open, :1732–1733) — [v2, review #2] the per-invocation evidence boundary; [v3, re-review #1] descriptor-bound: `"a+"` open mode, invocation-scoped flock, fstat-derived offset. (One module-top import diff: add `import fcntl` between `import array` :200 and `import hashlib` :201 — POSIX-only, like the box this driver targets; verified NOT currently imported, repo grep 2026-07-18.)

```diff
     stderr_path = sdir / ("%s.%s.pass%d.log" % (phase, arm, pass_no))
-    errf = open(stderr_path, "a", encoding="utf-8")
+    errf = open(stderr_path, "a+", encoding="utf-8")
+    # [ASM-2513 v3, re-review #1] "a+" (O_RDWR|O_APPEND), not "a":
+    # check_pin_engagement reads its evidence back through THIS
+    # descriptor (os.pread — which raises EBADF on a write-only "a"
+    # fd [MEASURED, this box 2026-07-18]); append semantics for the
+    # child are unchanged.
+    try:
+        fcntl.flock(errf.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
+    except OSError:
+        fail("ERR_F1K_PINNING",
+             "%s/%s pass %d: stderr log %s is flock-held by ANOTHER "
+             "LIVE invocation — concurrent ownership of the evidence "
+             "log is REFUSED (the double-resume race); wait for or "
+             "stop the other driver [ASM-2513 v3 re-review #1; "
+             "advisory lock = cooperating-writer guarantee ONLY — "
+             "honesty note in §1c docstring]"
+             % (phase, arm, pass_no, stderr_path))
+    # [ASM-2513 v2, review #2 / v3 re-review #1] pre-spawn BYTE
+    # offset: the log filename is DETERMINISTIC and the file is opened
+    # in APPEND mode, so after an interruption a PRIOR invocation's
+    # armed banner is still in the file. Captured after open (which
+    # creates the file) and BEFORE Popen — the engine's first byte
+    # lands at exactly this offset — so check_pin_engagement can only
+    # be satisfied by evidence THIS invocation's engine produced.
+    # (v3: os.fstat on the DESCRIPTOR, not os.path.getsize(name) —
+    # getsize re-binds to the pathname, the exact channel re-review #1
+    # closes; not errf.tell(): text-mode tell() is an opaque cookie,
+    # not a byte offset. The driver itself never writes to errf; the
+    # flock above spans the child's lifetime because Popen dups this
+    # fd — child and driver share ONE open file description.)
+    err_start = os.fstat(errf.fileno()).st_size
```

New second hunk [v4, round-3 #2] — immediately before the `Popen` (:1738), after the label-log open (:1736):

```diff
     llog = open(workdir / ("label-logits.%s.jsonl" % phase), "a",
                 encoding="utf-8")
+    if ledger is not None:
+        # [ASM-2513 v4, round-3 #2] durable SPEND-START sentinel,
+        # fsynced BEFORE Popen: from the spawn onward the child can
+        # SPEND before ANY of the seven §1e artifact/checkpoint paths
+        # exists (the selected-rows checkpoint opens only at :1755) —
+        # a hard interruption in that window previously left only
+        # manifests (:1702) and logs (:1733/:1736), none of them
+        # predicate sentinels, so a subsequently missing
+        # cost-ledger.json fresh-inited silently. Now every METERED
+        # spawn (ledger is not None — every campaign pass call site
+        # carries ledger=ledger: :2123/:2180/:2676/:2741/:2745/
+        # :2749/:2755; only unmetered mock/probe spawns pass None and
+        # have no ledger basis to protect) is preceded by a durable
+        # mark the §1e missing-ledger predicate includes. The helper
+        # fails closed on OSError: no spawn without a durable sentinel.
+        write_spend_start(ledger, phase, arm, pass_no)
     proc = subprocess.Popen(argv, env=env, stdout=subprocess.PIPE,
                             stderr=errf, text=True)
```

```diff
     n = 0
     first_seen = False
-    banners_here = 0
+    banners_here, banners_txt = 0, []
     t_last = time.monotonic()
```
```diff
                     banners_here += 1
+                    banners_txt.append(line)     # [ASM-2513] pin banner
+                    #   may legally ride the pre-result stdout banners
                     BANNERS_SKIPPED["n"] += 1
```
```diff
                 if not first_seen:
                     first_seen = True
                     errf.flush()
                     check_kae_engagement(stderr_path, env, where)  # [FIX-2]
+                    check_pin_engagement(errf, stderr_path,        # [ASM-
+                                         "\n".join(banners_txt),   #  2513]
+                                         env, where, ledger=ledger,
+                                         stderr_start=err_start)   # [v3 #1]
```

(Scope note, honest: `check_kae_engagement` still scans the whole file BY NAME — the analogous KAE stale-banner/rotation exposure is NOT flagged by this review and is NOT silently changed here; it stays a tracked follow-up. [v3] The descriptor mechanics CHANGE that follow-up's shape and shrink it: the `"a+"` open, the invocation flock, and `err_start` now already exist at the shared `errf`/log, so the KAE fix reduces to giving `check_kae_engagement` the same `(errf, stderr_start=err_start)` fd-slice read — no new state, just the same plumbing; NEXT-ACTION follow-up (ii) updated accordingly.)

### 1d2. SPEND-START sentinel — the durable pre-spawn mark ([v4, round-3 #2]; INSERT constant + helper immediately BEFORE the `class Ledger` section separator (:1420))

**Semantics:** "an engine spawn was ATTEMPTED under this outdir's ledger basis." Coverage argument (why this closes the window): spend requires a spawn; every metered spawn is preceded — durably, fsynced — by this sentinel (§1d second hunk); therefore *spend occurred* ∧ *`cost-ledger.json` missing* ⟹ *sentinel present* ⟹ the §1e predicate fails closed. Manifests (:1702) and stderr/label logs (:1733/:1736) stay OFF the predicate — they can precede the sentinel, but only by instants in which no spawn (hence no spend) has yet occurred and the just-written `cost-ledger.json` basis is trivially reconstructible from config; the moment spend becomes possible, the sentinel already exists on disk.

```python
SPEND_START_NAME = "spend-start.jsonl"


def write_spend_start(ledger, phase, arm, pass_no):
    """[ASM-2513 v4, round-3 #2] Durable SPEND-START sentinel: appended
    + fsynced (file AND directory entry) to the ledger's outdir BEFORE
    every metered engine Popen. Semantics: an engine spawn was
    ATTEMPTED under this outdir's ledger basis — so a hard interruption
    in the spawn-to-first-checkpoint window (child spent; only
    manifests/logs persisted) can never be followed by a silent
    fresh-ledger re-init (§1e predicate includes this file). Presence,
    not content, drives the predicate; the recorded line (phase/arm/
    pass + pin/cost basis) is forensics for the recovery decision.
    Fails closed: no spawn without a durable sentinel."""
    sp = ledger.path.parent / SPEND_START_NAME
    line = json.dumps({
        "event": "engine-spawn-attempt",
        "phase": phase, "arm": arm, "pass": pass_no,
        "ledger_basis": dict(
            {"pin_file_sha256":
                 ledger.d["expert_pinning"]["pin_file_sha256"],
             "PIN_GB": ledger.d["expert_pinning"]["PIN_GB"]},
            **{k: ledger.d[k] for k in ledger.COST_KEYS})},
        sort_keys=True)
    try:
        with open(sp, "a", encoding="utf-8") as sf:
            sf.write(line + "\n")
            sf.flush()
            os.fsync(sf.fileno())
        dfd = os.open(str(ledger.path.parent), os.O_RDONLY)
        try:
            os.fsync(dfd)      # the DIRENT too: a crash must not lose
        finally:               # a freshly created sentinel [MEASURED:
            os.close(dfd)      # file+dir fsync demo, this box
    except OSError as e:       # 2026-07-18]
        fail("ERR_F1K_COST",
             "cannot durably record the SPEND-START sentinel %s (%s) — "
             "an engine spawn without a durable spend mark would re-open "
             "the spawn-to-checkpoint crash window; no spawn without it "
             "[ASM-2513 v4 round-3 #2]" % (sp, e))
```

(`json`, `os`, `Path`, `fail` all in scope at module level — no import diff. The helper reads `ledger.COST_KEYS` off the instance, so its placement before `class Ledger` resolves at call time.)

**Lifecycle [STIPULATED — the round-3 prescription's required decision]:** ONE append-only JSONL per campaign outdir (beside `cost-ledger.json`), one line per metered engine spawn attempt; NEVER deleted, rotated, truncated, or per-pass superseded by the campaign path. Exactly two lawful removals: (1) the mock's deterministic clean-slate reset — the $0 oracle re-runs from scratch by design (:3399 comment) and already unlinks `cost-ledger.json` (:3407), so it removes the sentinel WITH the ledger it guards (diff below); (2) the maintainer-authorized archiving reset already named in the §1e recovery text (the sentinel is archived with the artifacts). **Why it cannot false-positive-block the ordinary virgin-outdir fresh start** (the round-3-confirmed property, preserved): the sentinel is written only by metered spawns, and every `Ledger` is constructed BEFORE the first spawn of its outdir — `Ledger(args.outdir, cfg)` at :4007 (real) and :3425 (mock) precede every `run_scoring_pass` call — so at virgin-outdir `Ledger.__init__` time no sentinel can exist and the fresh init proceeds. Proven POSITIVELY by the §1i `pin_virgin` probe. And explicitly NOT the rejected "any outdir artifact" predicate: `carrier-provenance.json` is legitimately written BEFORE fresh-ledger construction (:4004 real / :3422 mock) and stays off the predicate.

Mock clean-slate diff (`mock_main`, after the `cost-ledger.json` unlink :3406–3409):

```diff
     try:
         (outdir / "cost-ledger.json").unlink()
     except OSError:
         pass
+    try:
+        # [ASM-2513 v4] the clean slate removes the SPEND-START
+        # sentinel WITH the ledger it guards — the deterministic $0
+        # oracle re-runs from scratch by design; one of exactly two
+        # lawful removals (the other: the maintainer-authorized
+        # archiving reset, §1e recovery text). The REAL campaign path
+        # never deletes it.
+        (outdir / SPEND_START_NAME).unlink()
+    except OSError:
+        pass
```

### 1e. `Ledger.__init__` resume branch (:1456) — carry the realized attestation ONLY under the same pin AND the same PIN_GB; refuse either swap at the ledger — this IS the cross-phase seam

**[v2, review #5] Why this site is load-bearing across phases:** the [R10-4] rows-auth bindings are deliberately per-phase — `campaign_resume_binding` puts `phase` in the binding (`f1k_driver.py:1927`) and pilot/guard/test each build their own (e.g. `gbind = campaign_resume_binding(cfg, "guard")`, `:2116`) — so binding equality can never compare pilot's `pin_gb` against guard's. The ONLY state that persists ACROSS phase boundaries is this cost ledger (its own docstring: "spans pilot + guard + test", `:1427`). v1 compared only `pin_file_sha256` here, so `PIN_GB` could silently change at a phase boundary (same pin file, different budget = a different matched-budget condition, DES §7.1). v2 compares BOTH fields:

```diff
-            self.d["expert_pinning"] = base["expert_pinning"]
+            # [ASM-2513] resume: the realized engine attestation
+            # (experts_pinned) carries over ONLY under the SAME pin
+            # file AND the SAME PIN_GB; a changed pin OR budget at
+            # resume is refused here — this ledger is the ONLY state
+            # spanning pilot+guard+test, so this comparison (not the
+            # per-phase [R10-4] bindings, which carry `phase` and never
+            # compare across it) is what closes the phase-boundary
+            # swap [v2, review #5]. A campaign never silently swaps
+            # its pin or its budget mid-run.
+            prev = self.d.get("expert_pinning") or {}
+            if prev.get("pin_file_sha256") not in (
+                    None, base["expert_pinning"]["pin_file_sha256"]):
+                fail("ERR_F1K_PINNING",
+                     "resume with a CHANGED pin stats-file: ledger "
+                     "pin_file_sha256=%r vs config-derived %r — amend "
+                     "the ledger deliberately, never silently "
+                     "[ASM-2513/R10-4]"
+                     % (prev.get("pin_file_sha256"),
+                        base["expert_pinning"]["pin_file_sha256"]))
+            if prev.get("PIN_GB") is not None and \
+                    float(prev["PIN_GB"]) != \
+                    base["expert_pinning"]["PIN_GB"]:
+                fail("ERR_F1K_PINNING",
+                     "resume with a CHANGED PIN_GB: ledger %r vs "
+                     "config-derived %r — PIN_GB is fixed ONCE at "
+                     "bring-up (DES §7.1:639) and may not drift at a "
+                     "phase boundary (pilot/guard/test share THIS "
+                     "ledger; the per-phase [R10-4] bindings cannot "
+                     "see across it) [ASM-2513 v2 review #5]"
+                     % (prev.get("PIN_GB"),
+                        base["expert_pinning"]["PIN_GB"]))
+            self.d["expert_pinning"] = base["expert_pinning"]
+            if isinstance(prev.get("experts_pinned"), int) \
+                    and not isinstance(prev.get("experts_pinned"), bool):
+                self.d["expert_pinning"]["experts_pinned"] = \
+                    prev["experts_pinned"]
```

(Both values compare exactly: `prev` and `base` are each produced by `float()` in `validate_pinning` from the same config field, so `!=` on floats is the correct no-tolerance identity here — the frozen figure either round-trips through JSON identically or was changed.)

**Second hunk [v3, re-review #3; v4, round-3 #2] — the `else` (MISSING-ledger) branch (:1457–1459).** v2's comparison only fires when `cost-ledger.json` EXISTS; the untouched `else` silently created a FRESH ledger, so after pilot, deleting/losing ONLY the ledger let guard/test initialize under a changed budget/pin with no comparison at all. Fail closed when the ledger is absent while campaign evidence exists. **Exact existence predicate:** the §1d2 **SPEND-START sentinel** (`spend-start.jsonl`, first in the list — [v4] it alone covers the spawn-to-checkpoint crash window, where a hard interruption leaves only manifests/logs and NONE of the seven persisted-progress paths) plus every campaign artifact/checkpoint path this driver writes under `outdir` (verified by repo grep 2026-07-18): `pilot/pilot-rows.jsonl` (:2649), `pilot/pilot-gates.json` (:2990), `pilot/addendum-5-frozen-lg.json` (:2728), `pilot/addendum-6-inputs.json` (:2969), `pilot/addendum-7-affordability.json` (:2936), `guard/raw.*.jsonl` (:2119), `test/rows.jsonl` (:2171) — ANY one existing ⇒ a campaign already progressed (or spend was already attempted) here ⇒ a fresh ledger is a cross-phase/basis reset, refused. Deliberately NOT "any outdir artifact": `carrier-provenance.json` is legitimately written before fresh-ledger construction (:4004/:3422) and stays off the list. (The §1i probe dirs are their own `outdir`s — the only ones that acquire a sentinel or artifacts are probes that then either deliberately expect the refusal (`pin_noledger`, `pin_spendstart`) or retain their ledger (`pin_hashswap`); `--mock` starts from a clean slate (:3399 — [v4] sentinel unlinked with the ledger, §1d2 diff) — nothing trips the predicate outside the probes that prove it.)

```diff
         else:
+            # [ASM-2513 v3, re-review #3] MISSING-LEDGER fail-closed:
+            # this ledger is the ONLY state spanning pilot+guard+test
+            # (§1e first hunk), so its ABSENCE while campaign evidence
+            # exists means the cross-phase pin/budget comparison basis
+            # was lost or deleted — re-initializing would let a changed
+            # PIN_GB/pin enter guard/test uncompared. Refuse with the
+            # recovery path named; a fresh ledger is legal ONLY on a
+            # virgin outdir.
+            # [v4, round-3 #2] the SPEND-START sentinel leads the
+            # predicate: it is fsynced BEFORE every metered engine
+            # spawn (§1d2), so even a hard interruption in the
+            # spawn-to-first-checkpoint window — which persists only
+            # manifests/logs, none of the seven artifact paths below —
+            # leaves it behind; spend can never have occurred here
+            # without it. NOT "any outdir artifact":
+            # carrier-provenance.json legitimately precedes fresh-
+            # ledger construction and is excluded.
+            ev = [Path(outdir) / SPEND_START_NAME]     # [v4]
+            ev += [Path(outdir) / "pilot" / q for q in
+                   ("pilot-rows.jsonl", "pilot-gates.json",
+                    "addendum-5-frozen-lg.json", "addendum-6-inputs.json",
+                    "addendum-7-affordability.json")]
+            ev.append(Path(outdir) / "test" / "rows.jsonl")
+            found = [str(q) for q in ev if q.exists()]
+            found += [str(q) for q in
+                      sorted((Path(outdir) / "guard").glob("raw.*.jsonl"))]
+            if found:
+                fail("ERR_F1K_COST",
+                     "cost-ledger.json is MISSING but campaign evidence "
+                     "(SPEND-START sentinel and/or artifacts/"
+                     "checkpoints) exists under %s (%s%s) — a "
+                     "fresh ledger here would re-initialize the "
+                     "cross-phase pin/budget basis silently. RECOVERY: "
+                     "restore the atomic-replace-persisted "
+                     "cost-ledger.json from the interrupted run, or "
+                     "obtain a maintainer-authorized reset that "
+                     "ARCHIVES the listed evidence first "
+                     "[ASM-2513 v3 re-review #3 / v4 round-3 #2]"
+                     % (outdir, "; ".join(found[:3]),
+                        ", ..." if len(found) > 3 else ""))
             self.d = base
             self._write()
```

### 1e2. Addendum-7 pre-test consumption — bind the THIRD cross-phase state ([v3, re-review #3]; INSERT helper immediately BEFORE `def enforce_pretest_commits` (:2194), one-line call inside it after the `d3_deferred` read (:2240–2241))

The addendum (:2902/:2912 region) already RECORDS `expert_pinning` (attested via §1f), but pre-test consumption (`enforce_pretest_commits`, :2215/:2235 region) never COMPARED it against the current config/ledger — a pilot-time pin or budget could silently diverge from the test-time one through the addendum channel. Same equality semantics as the §1e ledger seam: exact string equality on the sha, exact `float` inequality on `PIN_GB` (no tolerance — the figure either round-trips or was changed). Ledger↔config is already enforced at `Ledger.__init__` in this same invocation (§1e), so addendum↔config here transitively closes addendum↔ledger.

```python
def check_addendum_pinning(add7, cfg):
    """[ASM-2513 v3, re-review #3] The pilot addendum-7 is the THIRD
    cross-phase pin state (beside the cost ledger and the per-phase
    [R10-4] bindings): it records expert_pinning at PILOT time and is
    consumed at PRE-TEST time, so it must be compared, not trusted.
    A mismatch = the pilot ran under a different pin stats-file or a
    different matched-budget condition (DES §7.1) — no test spend."""
    ep = (add7.get("expert_pinning") or {})
    cur = validate_pinning(cfg)
    if ep.get("pin_file_sha256") != cur["pin_file_sha256"]:
        fail("ERR_F1K_PINNING",
             "pre-test: addendum-7 expert_pinning.pin_file_sha256=%r "
             "vs the current config's %s — the pilot ran under a "
             "DIFFERENT pin stats-file; a swapped pin never enters "
             "test [ASM-2513 v3 re-review #3]"
             % (ep.get("pin_file_sha256"), cur["pin_file_sha256"]))
    try:
        agb = float(ep.get("PIN_GB"))
    except (TypeError, ValueError):
        agb = float("nan")     # NaN != x for all x -> refused below
    if agb != cur["PIN_GB"]:
        fail("ERR_F1K_PINNING",
             "pre-test: addendum-7 expert_pinning.PIN_GB=%r vs the "
             "current config's %r — PIN_GB is fixed ONCE at bring-up "
             "(DES §7.1:639); a pilot/test budget divergence is a "
             "DIFFERENT matched-budget condition, refused "
             "[ASM-2513 v3 re-review #3]"
             % (ep.get("PIN_GB"), cur["PIN_GB"]))
```

Call-site diff (inside `enforce_pretest_commits`, current bytes :2240–2241):

```diff
     d3_deferred = attest_bool(add7.get("d3_text_deferred"),
                               "addendum-7 d3_text_deferred")
+    check_addendum_pinning(add7, cfg)     # [ASM-2513 v3 re-review #3]
```

### 1f. Sidecar + addendum-7 emission — attested, never trusted (2 one-line hunks)

`build_sidecar` (:2347) and the addendum-7 block (:2912):

```diff
-            "expert_pinning": ledger.d["expert_pinning"],     # [FIX-5]
+            "expert_pinning": attested_pinning(ledger),  # [FIX-5+ASM-2513]
```
```diff
-        "expert_pinning": ledger.d["expert_pinning"],         # [FIX-5]
+        "expert_pinning": attested_pinning(ledger),      # [FIX-5+ASM-2513]
```

### 1g. `gen_mock_fixtures` — deterministic MOCK pin stats-file + env (INSERT after the ASM-1971 mock-attestation block ending :3173; REPLACE env lines :3178–3181)

Insert (between :3173 and the `cfg = {` at :3175):

```python
    # [ASM-2513] deterministic MOCK hot-expert stats-file: the $0 oracle
    # exercises the accept+hash+verify+record path with a SHAPED mock
    # pin (M4-measured '<layer> <expert> <count>' triples — accum20.stats
    # format), NEVER the real GCS-resident dev pin (pin_50gb.stats
    # 6802cc97..., which in any case does NOT transfer: the campaign pin
    # is re-derived on the real construction corpus at bring-up,
    # F1K-CONSTRUCTION-PLAN.md §5.4). Deterministic literals — seeded by
    # nothing, like every fixture here.
    pin_path = fx / "mock-pin.stats"
    pin_path.write_text(
        "".join("%d %d %d\n" % (3 + (i % 12), i, 4096 - 17 * i)
                for i in range(128)),
        encoding="utf-8")
```

Env replacement:

```diff
-            "env": {"MOCK_SALT": "f1k-mock-v1",
-                    # [FIX-5] pinning ENFORCED even in the mock so the same
-                    # validation path runs (values are mock placeholders)
-                    "PIN": "1", "PIN_GB": "96"},
+            "env": {"MOCK_SALT": "f1k-mock-v1",
+                    # [FIX-5]+[ASM-2513] pinning ENFORCED even in the
+                    # mock so the SAME validate+hash+verify path runs:
+                    # PIN = the mock stats-file above (frozen semantics
+                    # PIN=<stats-file> — never the legacy literal "1");
+                    # PIN_GB = mock placeholder in the M4-measured
+                    # 40-50 GB pinnable-headroom band (m4.json
+                    # h_pin_by_G; the REAL value is fixed at bring-up
+                    # from measured free RAM, DES §7.1:639)
+                    "PIN": str(pin_path), "PIN_GB": "48"},
```

### 1h. `mock_colibri.py` — mock pin banner + fault injection (INSERT between :152 `sys.stderr.flush()` end of the KAE-armed block and :153 `print("loaded in ...")`)

```python
    # --- [ASM-2513] pin load report (mirrors the engine's hot-store
    # arming; the REAL banner wording is fetch-grade — re-verified at
    # bring-up per ASM-1971) ---
    pin = os.environ.get("PIN")
    rot = os.environ.get("MOCK_PIN_ROTATE_LOG")
    if pin and rot:
        # [v3, re-review #1] MOCK_PIN_ROTATE_LOG=<path> fault knob: the
        # rotation/replacement attack — this engine stays SILENT on its
        # REAL (fd-inherited) stderr and instead plants a decoy file AT
        # the log's PATHNAME: pad bytes (MOCK_PIN_ROTATE_PAD, >= the
        # driver's pre-spawn offset so the short-file guard passes) +
        # a stale armed banner after the offset. A NAME-based verifier
        # (v2's Path.read_bytes()) reads the decoy and goes GREEN; the
        # v3 descriptor-bound verifier never sees it. The §1i
        # pin_rotate probe proves the refusal.
        pad = int(os.environ.get("MOCK_PIN_ROTATE_PAD", "0") or 0)
        with open(rot + ".rot", "w", encoding="utf-8") as rf:
            rf.write(" " * pad)
            rf.write("[PIN] hot-expert store armed: pinned 128 "
                     "experts, 2.210 GiB (budget 48.00 GiB) from "
                     "mock-pin.stats\n")
        os.replace(rot + ".rot", rot)
    elif pin and os.environ.get("MOCK_PIN_SILENT") != "1":
        # [v2, review #2] MOCK_PIN_SILENT=1 fault knob: an engine that
        # says NOTHING about its pin state this invocation — the
        # stale-banner-resume exploit needs exactly this (a silent new
        # process riding a PRIOR invocation's armed banner in the
        # append-mode log); the §1i pin_stale probe proves the driver
        # now refuses it.
        pin_ok = os.path.exists(pin) and \
            os.environ.get("MOCK_PIN_FORCE_LOAD_FAIL") != "1"
        if not pin_ok:
            print("[PIN] cannot open %s -> pinning DISABLED" % pin,
                  file=sys.stderr)
            sys.stderr.flush()
        else:
            with open(pin, encoding="utf-8") as pf:
                n_pin = sum(1 for ln in pf if ln.strip())
            budget = float(os.environ.get("PIN_GB", "0") or 0)
            gb_used = round(min(budget, n_pin * 18541666.7 / 2 ** 30), 3)
            print("[PIN] hot-expert store armed: pinned %d experts, "
                  "%.3f GiB (budget %.2f GiB) from %s"
                  % (n_pin, gb_used, budget, os.path.basename(pin)),
                  file=sys.stderr)
            sys.stderr.flush()
```

(128 mock experts × 18,541,666.7 B [MEASURED per-expert bytes, `m4.json`] = 2.210 GiB ≤ budget 48 — the coherence checks of §1c pass; `mock_e2e_carriers.py` needs NO edit: it calls `drv.gen_mock_fixtures(outdir)` itself (:50) and `drv.load_config` (:86), so it inherits the mock pin file + validation path automatically.)

### 1i. Mock fail-closed probes — INSERT after :3772 (`ra_closed = (...)`, end of the 5b3 [R10-4] block; `_copy`, `expect_stop`, `cfg`, `ev`, `frozen`, `gold_dir`, `tbind`, `_ra_fixture` all in scope)

```python
    # 5b4. [ASM-2513, v4 probe set] pinning fail-closed probes — the
    # false-attestation exploit class: the legacy literal "1", a missing
    # stats-file, a malformed stats-file, a schema-illegal basename, a
    # non-ASCII "digit" triple, a non-finite PIN_GB, an engine that
    # never armed the hot store, a PRIOR invocation's stale armed banner
    # riding the append-mode log, a ROTATED/REPLACED log pathname
    # carrying a planted banner [v3], a mid-run pin-file/ledger-hash
    # mismatch, a PIN_GB swap at the cross-phase ledger seam, a MISSING
    # ledger beside existing campaign artifacts [v3], a MISSING ledger
    # beside ONLY the SPEND-START sentinel (the spawn-to-checkpoint
    # crash window) [v4], an addendum-7 pin/budget mismatch at pre-test
    # consumption [v3], and a resume under a swapped pin must ALL
    # refuse — while a VIRGIN outdir (no sentinel, no artifacts) must
    # still fresh-init [v4, positive probe] and a same-basis ledger+
    # sentinel pair must still RESUME cleanly [v5, positive probe].
    print("probe: [ASM-2513] pinning fail-closed probes — the next "
          "ERR_F1K_PINNING lines are EXPECTED")
    # [v2] the validated mock pin file, FROM the loaded config (the
    # gen_mock_fixtures local `pin_path` is not in scope at this
    # insertion point) — validate_pinning already resolved it absolute
    pin_path = Path(cfg["engine"]["env"]["PIN"])

    def _pin_cfg(val, gb=None):
        c = _copy.deepcopy(cfg)
        c["engine"]["env"]["PIN"] = val
        if gb is not None:
            c["engine"]["env"]["PIN_GB"] = gb
        return c

    pin_legacy = expect_stop(lambda: validate_pinning(_pin_cfg("1")))
    pin_missing = expect_stop(lambda: validate_pinning(
        _pin_cfg(str(outdir / "fixtures" / "no-such.stats"))))
    badp = outdir / "fixtures" / "malformed-pin.stats"
    badp.write_text("3 0 not-an-int\n", encoding="utf-8")
    pin_malformed = expect_stop(
        lambda: validate_pinning(_pin_cfg(str(badp))))
    # [v2, review #3] basename the PINNED schema would reject (space is
    # outside [A-Za-z0-9._+-]) — must fail AT CONFIG LOAD, before spend,
    # even though the file itself is valid and readable
    badn = outdir / "fixtures" / "bad name.stats"
    badn.write_text("3 0 7\n", encoding="utf-8")
    pin_badname = expect_stop(
        lambda: validate_pinning(_pin_cfg(str(badn))))
    # [v2, review #2] Unicode-digit triple: '٣'.isdigit() is True and
    # int('٣') == 3 [MEASURED], so v1 would have hashed+accepted a
    # non-ASCII pin list the engine cannot parse
    badu = outdir / "fixtures" / "nonascii-pin.stats"
    badu.write_text("٣ 0 7\n", encoding="utf-8")   # Arabic-Indic 3
    pin_nonascii = expect_stop(
        lambda: validate_pinning(_pin_cfg(str(badu))))
    # [v2, review #2] non-finite PIN_GB: NaN slides past `gb <= 0`
    pin_nangb = expect_stop(lambda: validate_pinning(
        _pin_cfg(str(pin_path), gb="nan")))
    pin_infgb = expect_stop(lambda: validate_pinning(
        _pin_cfg(str(pin_path), gb="inf")))
    print("probe: fault-injecting a pin load failure — the next "
          "ERR_F1K_PINNING line is EXPECTED")
    pprobe_dir = outdir / "pilot" / "pin-failclosed-probe"
    pprobe_dir.mkdir(parents=True, exist_ok=True)
    penv = arm_env(cfg, "b0", None, str(pprobe_dir), frozen)
    penv["MOCK_PIN_FORCE_LOAD_FAIL"] = "1"
    pin_unarmed = expect_stop(lambda: run_scoring_pass(
        cfg, ev["guard"][:1], "probe:b0", 0, None, penv,
        pprobe_dir / "rows.jsonl", set(), mock_gold_dir=gold_dir,
        phase="probe"))
    pin_rows = pprobe_dir / "rows.jsonl"
    pin_unarmed = pin_unarmed and (
        not pin_rows.exists() or not pin_rows.read_text().strip())
    # [v2, review #2 — SECURITY] STALE-BANNER-RESUME probe: pre-seed the
    # DETERMINISTIC append-mode stderr log with a byte-perfect armed
    # banner from a "prior invocation", then run an engine that stays
    # SILENT about its pin (MOCK_PIN_SILENT=1). v1's whole-file scan
    # would have gone GREEN on the stale banner — a newly UNPINNED
    # process authorized by a prior run's attestation; v2's pre-spawn
    # offset slice must see NO banner and refuse with zero rows scored.
    print("probe: stale-banner resume — the next ERR_F1K_PINNING line "
          "is EXPECTED (a prior run's banner must authorize NOTHING)")
    sprobe_dir = outdir / "pilot" / "pin-staleban-probe"
    (sprobe_dir / "stderr").mkdir(parents=True, exist_ok=True)
    stale_log = sprobe_dir / "stderr" / "probe.probe:b0.pass0.log"
    stale_log.write_text(
        "[PIN] hot-expert store armed: pinned 128 experts, 2.210 GiB "
        "(budget 48.00 GiB) from mock-pin.stats\n", encoding="utf-8")
    senv = arm_env(cfg, "b0", None, str(sprobe_dir), frozen)
    senv["MOCK_PIN_SILENT"] = "1"
    pin_stale = expect_stop(lambda: run_scoring_pass(
        cfg, ev["guard"][:1], "probe:b0", 0, None, senv,
        sprobe_dir / "rows.jsonl", set(), mock_gold_dir=gold_dir,
        phase="probe"))
    stale_rows = sprobe_dir / "rows.jsonl"
    pin_stale = pin_stale and (
        not stale_rows.exists() or not stale_rows.read_text().strip())
    # [v3, re-review #1] LOG-ROTATION/REPLACEMENT probe: pre-seed the
    # deterministic log (so the pre-spawn offset > 0), then run an
    # engine that is SILENT on its real (fd-inherited) stderr but
    # plants a decoy AT THE PATHNAME — pad bytes >= the offset + a
    # stale armed banner (MOCK_PIN_ROTATE_LOG/_PAD, §1h). The decoy
    # passes the v2 short-file guard and carries a valid banner after
    # the offset, so a NAME-based read goes GREEN on it [MEASURED:
    # decoy-rotation demo, this box 2026-07-18]; the v3 descriptor-
    # bound read sees NO banner on the true file object -> RED, zero
    # rows.
    print("probe: log rotation/replacement swap — the next "
          "ERR_F1K_PINNING line is EXPECTED (a pathname decoy must "
          "authorize NOTHING)")
    rprobe_dir = outdir / "pilot" / "pin-rotate-probe"
    (rprobe_dir / "stderr").mkdir(parents=True, exist_ok=True)
    rot_log = rprobe_dir / "stderr" / "probe.probe:b0.pass0.log"
    rot_log.write_text("prior invocation noise\n", encoding="utf-8")
    renv = arm_env(cfg, "b0", None, str(rprobe_dir), frozen)
    renv["MOCK_PIN_ROTATE_LOG"] = str(rot_log)
    renv["MOCK_PIN_ROTATE_PAD"] = str(rot_log.stat().st_size)
    pin_rotate = expect_stop(lambda: run_scoring_pass(
        cfg, ev["guard"][:1], "probe:b0", 0, None, renv,
        rprobe_dir / "rows.jsonl", set(), mock_gold_dir=gold_dir,
        phase="probe"))
    rot_rows = rprobe_dir / "rows.jsonl"
    pin_rotate = (pin_rotate
                  and (not rot_rows.exists()
                       or not rot_rows.read_text().strip())
                  and b"[PIN] hot-expert store armed"
                  in rot_log.read_bytes())
    #   ^ third conjunct: the decoy really IS at the pathname (the bait
    #     was live) — ONLY the descriptor-bound read refused it
    # [v2, review #6 probe (a)] EXPECTED-HASH mismatch: the ledger's
    # pin_file_sha256 no longer matches the file BYTES (the file grew
    # after ledger init = a mid-run swap) — check_pin_engagement must
    # re-derive from bytes and go RED, zero rows scored.
    print("probe: ledger pin-hash vs file-bytes mismatch — the next "
          "ERR_F1K_PINNING line is EXPECTED")
    hprobe_dir = outdir / "pilot" / "pin-hashswap-probe"
    hprobe_dir.mkdir(parents=True, exist_ok=True)
    pin2 = outdir / "fixtures" / "hashswap-pin.stats"
    pin2.write_text(pin_path.read_text(encoding="utf-8"),
                    encoding="utf-8")
    hcfg = _pin_cfg(str(pin2))
    hled = Ledger(str(hprobe_dir), hcfg)     # hashes pin2 AS IT IS NOW
    with open(pin2, "a", encoding="utf-8") as pf:
        pf.write("3 999 1\n")                # ...then the bytes change
    henv = arm_env(hcfg, "b0", None, str(hprobe_dir), frozen)
    pin_hashswap = expect_stop(lambda: run_scoring_pass(
        hcfg, ev["guard"][:1], "probe:b0", 0, None, henv,
        hprobe_dir / "rows.jsonl", set(), ledger=hled,
        mock_gold_dir=gold_dir, phase="probe"))
    hs_rows = hprobe_dir / "rows.jsonl"
    pin_hashswap = pin_hashswap and (
        not hs_rows.exists() or not hs_rows.read_text().strip())
    # [v2, review #5] PIN_GB swap at the CROSS-PHASE ledger seam: a
    # ledger written under PIN_GB=48 must refuse a re-init (= a phase
    # boundary or resume) whose config carries a different budget.
    print("probe: cross-phase PIN_GB swap — the next ERR_F1K_PINNING "
          "line is EXPECTED")
    gprobe_dir = outdir / "pilot" / "pin-gbswap-probe"
    gprobe_dir.mkdir(parents=True, exist_ok=True)
    Ledger(str(gprobe_dir), cfg)             # ledger under PIN_GB=48
    gb_ledgerswap = expect_stop(
        lambda: Ledger(str(gprobe_dir), _pin_cfg(str(pin_path),
                                                 gb="32")))
    # [v3, re-review #3] MISSING-LEDGER phase-transition probe:
    # campaign evidence exists (a pilot artifact) but cost-ledger.json
    # does NOT — Ledger init must REFUSE to re-initialize (the
    # cross-phase comparison basis is gone; §1e second hunk), naming
    # the recovery path.
    print("probe: missing ledger beside campaign artifacts — the next "
          "ERR_F1K_COST line is EXPECTED")
    mprobe_dir = outdir / "pilot" / "pin-noledger-probe"
    (mprobe_dir / "pilot").mkdir(parents=True, exist_ok=True)
    (mprobe_dir / "pilot" / "pilot-gates.json").write_text(
        "{}", encoding="utf-8")            # evidence present, no ledger
    pin_noledger = expect_stop(lambda: Ledger(str(mprobe_dir), cfg))
    # [v4, round-3 #2] SPAWN-TO-CHECKPOINT CRASH-WINDOW probe: a spawn
    # was attempted (sentinel written, exactly as run_scoring_pass does
    # BEFORE Popen) but the run was interrupted before ANY of the seven
    # artifact/checkpoint paths existed, and cost-ledger.json was then
    # lost — the ONLY evidence is the sentinel. v3's predicate saw
    # nothing here and fresh-inited silently; v4 must refuse.
    print("probe: SPEND-START sentinel beside a missing ledger (spawn-"
          "to-checkpoint crash window) — the next ERR_F1K_COST line is "
          "EXPECTED")
    wprobe_dir = outdir / "pilot" / "pin-spendstart-probe"
    wprobe_dir.mkdir(parents=True, exist_ok=True)
    write_spend_start(Ledger(str(wprobe_dir), cfg), "probe", "b0", 0)
    # [v5, round-4 #1] NORMAL-RESUME positive assertion, BEFORE the
    # unlink: while ledger AND sentinel COEXIST (exactly the state an
    # ordinary interrupted run leaves behind), a SAME-config
    # Ledger(...) is a lawful resume and must PROCEED — a wrong
    # fail-closed here dies loudly (not wrapped in expect_stop), the
    # positive-probe signal, as pin_virgin — reporting the SAME basis:
    # the config-derived pin sha + PIN_GB carried through the §1e
    # resume comparison (exact equality; §1e semantics). With
    # pin_virgin and the post-unlink crash assertion below, this
    # sequence now distinguishes all THREE states: virgin /
    # normal-resume / crash-window.
    wexp = validate_pinning(cfg)
    wres = Ledger(str(wprobe_dir), cfg)          # must NOT stop
    pin_spendresume = (
        (wprobe_dir / "cost-ledger.json").exists()      # the state
        and (wprobe_dir / SPEND_START_NAME).exists()    # under test
        #   really held: ledger + sentinel COEXIST at resume time ^
        and wres.d["expert_pinning"]["pin_file_sha256"]
        == wexp["pin_file_sha256"]
        and float(wres.d["expert_pinning"]["PIN_GB"]) == wexp["PIN_GB"])
    (wprobe_dir / "cost-ledger.json").unlink()   # ...then the ledger is
    #   lost; NO artifact/checkpoint path exists in this outdir
    pin_spendstart = expect_stop(lambda: Ledger(str(wprobe_dir), cfg))
    pin_spendstart = pin_spendstart and \
        (wprobe_dir / SPEND_START_NAME).exists()
    #   ^ second conjunct: the sentinel really IS the only evidence
    #     present — the refusal came from it, not from an artifact
    # [v4, round-3 #2] VIRGIN-OUTDIR fresh-start PRESERVED (positive
    # probe, per the round-3 prescription): no sentinel, no artifacts
    # -> Ledger init must PROCEED (not raise) and persist a fresh
    # ledger. A wrong fail-closed here dies loudly (not wrapped in
    # expect_stop) — the correct signal for a positive probe.
    vprobe_dir = outdir / "pilot" / "pin-virgin-probe"
    vprobe_dir.mkdir(parents=True, exist_ok=True)
    Ledger(str(vprobe_dir), cfg)                 # must NOT stop
    pin_virgin = (vprobe_dir / "cost-ledger.json").exists() and \
        not (vprobe_dir / SPEND_START_NAME).exists()
    # [v3, re-review #3] ADDENDUM-MISMATCH probes: a pilot addendum
    # whose recorded pin sha (or PIN_GB) differs from the CURRENT
    # config must refuse at pre-test consumption (§1e2 helper, exact
    # equality semantics of the ledger seam).
    print("probe: addendum-7 pin/budget mismatch — the next TWO "
          "ERR_F1K_PINNING lines are EXPECTED")
    cur_ep = validate_pinning(cfg)
    pin_addsha = expect_stop(lambda: check_addendum_pinning(
        {"expert_pinning": {"pin_file_sha256": "e" * 64,
                            "PIN_GB": cur_ep["PIN_GB"]}}, cfg))
    pin_addgb = expect_stop(lambda: check_addendum_pinning(
        {"expert_pinning": {"pin_file_sha256": cur_ep["pin_file_sha256"],
                            "PIN_GB": 32.0}}, cfg))
    # [R10-4] pin-swap resume: a binding whose pin-file hash differs is
    # a FOREIGN run — refused like any other binding mismatch.
    pswap = json.loads(json.dumps(tbind))
    pswap["pin_file_sha256"] = "f" * 64
    ra_pinswap = expect_stop(
        lambda: read_ckpt_authed(_ra_fixture("pin-swap"), pswap))
    pin_closed = (pin_legacy and pin_missing and pin_malformed
                  and pin_badname and pin_nonascii and pin_nangb
                  and pin_infgb and pin_unarmed and pin_stale
                  and pin_rotate and pin_hashswap and gb_ledgerswap
                  and pin_noledger and pin_spendstart
                  and pin_spendresume and pin_virgin
                  and pin_addsha and pin_addgb and ra_pinswap)
```

### 1j. Self-check line `[5]` (:3840–3843) — truthful-provenance assertion

```diff
-        ("[5] expert pinning ENFORCED + RECORDED: PIN=1 PIN_GB=%s in "
-         "ledger + sidecar cost.expert_pinning [%s]"
-         % (led["expert_pinning"]["PIN_GB"], ref(5)),
-         led.get("expert_pinning", {}).get("PIN") == "1"),
+        ("[5] expert pinning ENFORCED + RECORDED (ASM-2513 "
+         "PIN=<stats-file>): PIN=%s sha256=%.12s... PIN_GB=%s "
+         "experts_pinned=%s (%d engine pin verifications, descriptor-"
+         "bound evidence) in ledger + sidecar cost.expert_pinning; "
+         "legacy \"1\" / missing / malformed / bad-basename / "
+         "non-ASCII-digits / non-finite-PIN_GB / unarmed-engine / "
+         "STALE-BANNER-RESUME / LOG-ROTATION-SWAP / ledger-hash-"
+         "vs-bytes / cross-phase-PIN_GB-swap / MISSING-LEDGER-REINIT / "
+         "SPEND-START-CRASH-WINDOW / ADDENDUM-PIN-MISMATCH / "
+         "pin-swap-resume ALL "
+         "REFUSED (ERR_F1K_PINNING / ERR_F1K_COST); virgin-outdir "
+         "fresh init AND same-basis ledger+sentinel NORMAL-RESUME "
+         "PRESERVED; spend-start sentinel written by every "
+         "metered spawn [%s]"
+         % (led["expert_pinning"]["PIN"],
+            led["expert_pinning"]["pin_file_sha256"],
+            led["expert_pinning"]["PIN_GB"],
+            led["expert_pinning"].get("experts_pinned"),
+            PIN_CHECKS["n"], ref(5)),
+         led.get("expert_pinning", {}).get("PIN") == "mock-pin.stats"
+         and len(led["expert_pinning"].get("pin_file_sha256", "")) == 64
+         and led["expert_pinning"].get("experts_pinned") == 128
+         and PIN_CHECKS["n"] > 0 and pin_closed
+         and (outdir / SPEND_START_NAME).exists()),
+        #   ^ [v4] final conjunct: the mock campaign's own metered
+        #     spawns really wrote the sentinel at the outdir root —
+        #     the pre-Popen write is proven on the REAL code path,
+        #     not only by the direct-call probe
```

### 1k. Harness doc echo — `poc/glm52-probe/f1k-harness/README.md:146`

```diff
-pinning is ENFORCED (`PIN=1` + positive `PIN_GB`, recorded in ledger +
+pinning is ENFORCED (`PIN=<bring-up stats-file>` validated + content-
+hashed + engine-arming-verified [ASM-2513] + positive `PIN_GB`, recorded in ledger +
```

---

## 2. `analysis/f1k.py` — the SHA-PINNED schema (the re-freezing edit; 4 sites, minimal)

### 2a. The `expert_pinning` schema (:648–651) — the load-bearing diff

```diff
-            "expert_pinning": _obj({
-                "PIN": _c("1"),
-                "PIN_GB": _t("number", min_ex=0),
-                "semantics": _t("string", min_len=1)}),
+            # [ASM-2513 PIN=<stats-file> conformance fix, 2026-07-18;
+            # kot-correction/1 seq 3]: the frozen design's pinning knob
+            # is PIN=<stats-file> with PIN_GB fixed at bring-up
+            # (glm52-followup-experiment.md §7.1:638-639); the prior
+            # _c("1") locked this ledger to a constant the engine
+            # cannot realize — a FALSE pinning attestation. TRUTHFUL
+            # provenance now required: the pin stats-file BASENAME
+            # (never the literal "1" — pattern-excluded), its content
+            # sha256, its line count, the bring-up PIN_GB, and the
+            # ENGINE-attested pinned-expert count (>= 1: a hot store
+            # verifiably loaded, driver check_pin_engagement). The
+            # engine banner FORMAT is deliberately NOT schema-locked
+            # (fetch-grade, ASM-1971; it lives in the unpinned driver)
+            # — only the hash + counters are. [v2, review #3] The PIN
+            # pattern below is mirrored VERBATIM by the driver's
+            # PIN_BASENAME_RE and enforced there at CONFIG LOAD
+            # (fail-closed BEFORE spend); THIS schema copy is the
+            # authoritative one — the two must stay textually
+            # identical (driver §1b cross-cite; oracle pin_badname
+            # probe exercises the agreement).
+            "expert_pinning": _obj({
+                "PIN": _t("string",
+                          pattern=r"^(?!1\Z)[A-Za-z0-9._+-]{1,255}\Z"),
+                "pin_file_sha256": _HEX64,
+                "pin_file_lines": _t("int", min=1),
+                "PIN_GB": _t("number", min_ex=0),
+                "experts_pinned": _t("int", min=1),
+                "pin_scope": _c("shared-all-arms"),
+                "semantics": _t("string", min_len=1)}),
```

(Pattern discipline honored: `\Z`-anchored, applied via `re.fullmatch` — the round-6 "never `$`" rule at :495–498. `_HEX64` is defined at :540, above this site. The full-depth schema sweep (:2235 ff.) walks the schema declaratively, so every new required key is automatically covered by the pop-key/type-swap/unknown-key rejection probes.)

### 2b. Docstring surface list (:247)

```diff
-expert_pinning {PIN, PIN_GB, semantics}, resume_safe_ledger,
+expert_pinning {PIN (stats-file basename, never "1"), pin_file_sha256,
+pin_file_lines, PIN_GB, experts_pinned, pin_scope, semantics
+[ASM-2513]}, resume_safe_ledger,
```

### 2c. Selftest fixture `_mock_sidecar` (:1959–1962) — new shape, measured-band figures (round-6 lesson: registered/measured planning figures, not mock inventions)

```diff
-                 "expert_pinning": {"PIN": "1", "PIN_GB": 40.0,
-                                    "semantics": "PIN=1 pins the hot "
-                                    "expert working set resident; PIN_GB "
-                                    "= pinned budget in GB."},
+                 # [ASM-2513] fixture in the M4-measured band (m4.json:
+                 # G40 -> 2157 experts pinned of a 2696-line G50 list);
+                 # sha256 is a schema-shape fixture value only
+                 "expert_pinning": {"PIN": "pin-bringup.stats",
+                                    "pin_file_sha256": "d0c5" * 16,
+                                    "pin_file_lines": 2696,
+                                    "PIN_GB": 40.0,
+                                    "experts_pinned": 2157,
+                                    "pin_scope": "shared-all-arms",
+                                    "semantics": "PIN=<stats-file> pins "
+                                    "the hot expert working set resident "
+                                    "under the bring-up PIN_GB budget "
+                                    "[ASM-2513]."},
```

### 2d. Selftest rejection probe (:2387–2388) — the constant-"1" probe becomes the truthful-provenance probe set

```diff
-    probe_struct('cost.expert_pinning.PIN = "0" (!= pinned "1")',
-                 _set(("cost", "expert_pinning", "PIN"), "0"))
+    probe_struct('cost.expert_pinning.PIN = "1" (the SUPERSEDED literal '
+                 'is schema-REJECTED: a pinning attestation without a '
+                 'named stats-file — ASM-2513)',
+                 _set(("cost", "expert_pinning", "PIN"), "1"))
+    probe_struct("cost.expert_pinning.pin_file_sha256 = 'deadbeef' "
+                 "(short — not a derived content hash)",
+                 _set(("cost", "expert_pinning", "pin_file_sha256"),
+                      "deadbeef"))
+    probe_struct("cost.expert_pinning.experts_pinned = 0 (no hot store "
+                 "verifiably loaded — an unverified pin never validates)",
+                 _set(("cost", "expert_pinning", "experts_pinned"), 0))
```

Nothing else in `analysis/f1k.py` changes: the KAEC/layer arithmetic, floors (`USD_TOTAL_MIN 73` :458, `INSTANCE_HOURS_MIN 260.6` :465), `RUN_PHASES`, power pins, statistics, and every other schema node are byte-identical.

---

## 3. [R10-4] resume-authorization binding — a resumed/multi-VM run can never silently swap the pin OR its PIN_GB (within-phase here; cross-phase at the §1e ledger seam [v2])

**Where [R10-4] lives:** `f1k_driver.py:449` (header), `:1899–1942` (mechanism comment + `campaign_resume_binding`), `:1945–2034` (`RowsAuth` / `read_ckpt_authed`); frozen-record narrative: `f1k.json /pins/harness_manifest` "[R10-4] CAMPAIGN RESUME AUTHENTICATION … (f1k_driver.py, not sha-pinned here)". The binding spec for the pin is `F1K-CONSTRUCTION-PLAN.md` §5 item 5 verbatim: "`pin_file_sha256` + `PIN_GB` … enter the R10-4 resume-authentication payload … any resumed campaign re-derives the pin-file hash from bytes and compares; mismatch = fail closed."

**Exact diff — `campaign_resume_binding` (insert before `return b`, after the `engine_file_sha256` lines :1940–1941):**

```diff
     b["engine_argv"] = argv
     b["engine_file_sha256"] = {a: sha256_file(a) for a in argv
                                if Path(a).is_file()}
+    # [ASM-2513 / R10-4 extension; F1K-CONSTRUCTION-PLAN.md §5 item 5]:
+    # the pin identity is a pinned input of the run — every resume (and
+    # any future multi-VM shard) re-derives the pin-file hash FROM BYTES
+    # via validate_pinning and must MATCH the auth state, so a swapped
+    # pin can never silently resume; mismatch fails closed exactly like
+    # a foreign engine (ERR_F1K_RESUME binding mismatch).
+    ep = validate_pinning(cfg)
+    b["pin_file_sha256"] = ep["pin_file_sha256"]
+    b["pin_gb"] = ep["PIN_GB"]
     return b
```

The generic binding-equality check in `read_ckpt_authed` (:1994–2002) then enforces it with no further edit; the §1i `ra_pinswap` probe proves the refusal in the $0 oracle. **[v2, review #5 — seam honesty]:** this binding carries BOTH `pin_file_sha256` and `pin_gb`, but it is a **WITHIN-phase** guarantee only — `campaign_resume_binding` deliberately includes `phase` (`:1927`) and pilot/guard/test each construct their own binding (`:2116` and peers), so binding equality never compares one phase's `pin_gb` against another's. The **CROSS-phase** guarantee (a `PIN_GB` or pin swap at a pilot→guard→test boundary) lives at the only state that spans phases: the resume-safe cost ledger — the §1e v2 diff compares BOTH `pin_file_sha256` AND `PIN_GB` there, and the §1i `gb_ledgerswap` probe proves the refusal. Together the two seams close both the within-phase and phase-boundary swap. **[v3, re-review #3]:** two residual cross-phase holes are closed on top: the ledger seam only fired when the ledger EXISTED — the §1e second hunk now fails closed on a MISSING ledger beside existing campaign artifacts (deleting only `cost-ledger.json` no longer re-initializes the comparison basis) — and the pilot addendum-7, the THIRD cross-phase pin state, is now compared (sha + `PIN_GB`, §1e2) at pre-test consumption instead of merely recorded. **[v4, round-3 #2]:** the missing-ledger predicate's residual blind spot — the spawn-to-checkpoint crash window (`Popen` :1738 precedes the selected-rows checkpoint open :1755; an interruption there persists only manifests/logs, none of the seven artifact paths) — is closed by the durable SPEND-START sentinel (§1d2): fsynced BEFORE every metered spawn, first in the §1e predicate, lifecycle stipulated (append-only, never deleted on the campaign path), so "spend attempted + ledger missing" always fails closed while the ordinary virgin-outdir fresh start is preserved and positively probed (§1i `pin_spendstart` / `pin_virgin`). (Multi-VM sharding proper remains scoped OUT of the mandatory path per `F1K-CONSTRUCTION-PLAN.md` §6 — this binding is its prerequisite, not its implementation.)

---

## 4. RE-FREEZE MECHANICS — every pin/hash that moves (exhaustive, seq-2 style)

`analysis/f1k.py` is sha-pinned at `54924cfd0f1b7878da53228aa54f3cdf3e405aa4d0ecefd185fcb75da9eea8eb` in **exactly two verifying sites** (verified by repo grep 2026-07-18): `registry/experiments/f1k.json` `/pins/analysis_script/sha256` (the single in-record occurrence) and `poc/gcp/f1k_gcp.py:57` `PINS["analysis/f1k.py"]` (launch-verified, `verify_pins()` :152–176 dies `ERR_F1K_PIN_MISMATCH`). Changing it re-derives the frozen record hash (current `frozen_sha256` = `01cf2b17a882b2ab89873234a381720108dbb9d0dcd406a752962e280b71dc55`).

| # | Pin / site | Old | New | Why |
|---|---|---|---|---|
| 1 | `f1k.json` `/pins/analysis_script/sha256` | `54924cfd…` | `<SHA256-OF-EDITED-analysis/f1k.py, COMPUTED AT LAND>` | §2 edits the file (the ONLY frozen-record field change) |
| 2 | `f1k.json` `/frozen_sha256` | `01cf2b17…` | `<COMPUTED AT LAND: kot_common.frozen_hash of the corrected record>` | record bytes changed (row 1); frozen hash covers them |
| 3 | `registry/frozen-index.json["f1k"]` | `01cf2b17…` | same NEW value as row 2 | index must match in the SAME commit or `registry-check frozen-drift` fails |
| 4 | `poc/gcp/f1k_gcp.py:51` `FROZEN_SHA256` | `01cf2b17…` | same NEW value as row 2 | launch-verified (`:49` "verified at launch"; `ERR_F1K_PIN_FROZEN` on mismatch) — as-is it would REJECT the corrected run |
| 5 | `poc/gcp/f1k_gcp.py:57` `PINS["analysis/f1k.py"]` | `54924cfd…` | same NEW value as row 1 | launch-verified file pin (`ERR_F1K_PIN_MISMATCH`) |
| 6 | Comment/doc echoes of `01cf2b17`: `f1k_gcp.py:5` (docstring), `:49` (header comment); `poc/gcp/bringup_gcp.sh:43`; `poc/gcp/README.md:5` | `01cf2b17…` | new hash prefix | edit for honesty, same commit (seq-2 precedent §1.5a) |
| 7 | Comment echo of `54924cfd`: `f1k_gcp.py:14` ("analysis/f1k.py (sha 54924cfd)") | `54924cfd…` | new sha prefix | edit for honesty, same commit |
| 8 | `registry/corrections/f1k/3-pin-file-fix.json` | — (new file) | §5.2 record with `refrozen_sha256 = <row 2>` | kot-correction/1 chain, seq 3 |
| — | **UNCHANGED (verified):** `build_carriers.py` `a92be3e4…`; `kae-add-path.patch` `11f8b458…`; `kot-f1k-dump.patch` `fb5d2f35…`; `kae_dump.h` `6ce77601…`; `construction-manifest.jsonl` `a8cb3a8a…`; colibri base commit `a78a06fc5acc…`; weights placeholder (PINNED-AT-INPUTS); prereg/analysis-plan doc sha `9f18e5e0…`; ALL corpus hashes incl. the **A-time `data/f1k-carriers-v1/` directory digest `e53622e3…`** (NO file under `data/` is touched — unlike seq 2, no corpus-pin recompute) and the `f1k-carriers-v1` PINNED-AT-INPUTS placeholder status; **science pins in full**: layer geometry 3..77 = 75 (ASM-2504), 19,964 mandatory prefills (ASM-2405), n=1573 / C=96 / mu*=4.09 / ASM-2371 power table, endpoints, kill criterion + envelope verbatim, $155 cap + 900 h cap (ASM-2374), floors [$73 / 260.6 h], rate window, seeds (20260713 / 20260716 / d0 seed 7 / DRNG 101-103), SSR6 order | | | |
| — | **Edited/created but NOT pinned anywhere** (so they re-pin NOTHING — verified: frozen record says "f1k_driver.py, not sha-pinned here" twice; `f1k_gcp.py` `PINS` has no driver/mock/tool rows): `f1k_driver.py`, `mock_colibri.py`, harness `README.md`, [v4] `poc/gcp/f1k_repin_splice.py` (new — the §4 reusable splice) | | | driver-side/tooling edits are review-gated, not hash-gated |
| — | **LEAVE — historical witnesses (never edit):** `54924cfd`/`505165ee`/`01cf2b17` mentions in dated memos (`F1K-AFFORDABILITY-DECISION.md`, `F1K-CONSTRUCTION-PLAN.md`, `poc/gpt56-review/*`, `docs/next/design/f1k-runhold-refreeze-2026-07-15.md`), opus run-logs, mock logs; the frozen record's own "analysis/f1k.py BYTE-IDENTICAL at its pin" sentences (witnesses of THEIR passes — currency superseded by the seq-3 record, seq-2 precedent) | | | append-only record discipline |

**Re-pin splice mechanics ([v2, review #6] — RE-RUNNABLE, and run BEFORE the $0 oracle as a WORKING-TREE-ONLY recompute; seq-2/`_f1k_carrierauth_fix_20260716.py` precedent. Why before: the official seam copies the edited `analysis/f1k.py` beside `f1k.json`, and verdict-gen verifies the record's analysis pin against the file bytes — with the OLD sha still in the record the oracle can NEVER go green, so v1's "oracle before re-pin" order was unrunnable. The re-pin *recompute* is a local working-tree edit; the re-FREEZE is the landing COMMIT, which still happens only after the oracle is green — the round-4 "oracle before refreezing" lesson is honored in substance. Re-runnable: a red oracle iteration re-edits `analysis/f1k.py`, so the splice moves `<current record pin> → <current file sha>` each time, guarded — [v3, re-review #5] — by RECOMPUTED record/index consistency asserts plus the ORIG-counterfactual assert, both run BEFORE either exit path.**

**[v4, round-3 #3] The splice is ONE reusable exact implementation, materialized as a FILE:** in step §7-A the coordinator materializes the block below verbatim to **`poc/gcp/f1k_repin_splice.py`** (new file, part of the landing working set; like the driver it is NOT sha-pinned anywhere, so it re-pins nothing — table row below). BOTH the real §7-B1 splice AND every §7-B1n negative-probe variant invoke this same file — the memo contains NO verbatim-placeholder duplication of it, and every §7 command is executable as printed. Guard logic and assert messages are byte-stable from v3 (round-3 CLOSED — independently exercised by the reviewer); the only file-form deltas are the shebang/docstring and the `ROOT` default `"."`. [MEASURED, this box 2026-07-18: `python3 -m py_compile` clean on a materialized copy; pristine-scratch positive control exits 0 with the no-op line (both guards pass on the real committed record — ORIG hashes re-verified live); dirty variant exits 1 with the assert-(i) message; forged-consistent variant exits 1 with the assert-(ii) message; scratch registry pair byte-identical (sha256-verified) after both refusals.]

```python
#!/usr/bin/env python3
"""[ASM-2513 v4, round-3 #3] The SS4 re-pin splice — the ONE exact,
reusable implementation (spec: poc/gcp/F1K-PIN-FILE-FIX.md SS4). Run
from the REPO ROOT. Used verbatim by BOTH the live SS7-B1 splice
(ROOT=".") and the SS7-B1n negative-probe variants (ROOT=<scratch
copy>) — no verbatim-placeholder duplication. ROOT roots ONLY the
registry pair; the analysis bytes are always the working tree's.
Guards ([v3, re-review #5], CLOSED round 3 — logic and assert messages
byte-stable): (i) recomputed record/index consistency, then (ii) the
ORIG-counterfactual, BOTH before either exit path; writes come only
after both asserts."""
import copy, json, sys, hashlib
sys.path.insert(0, "tools/registry")
import kot_common as kc
ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
ORIG_ANA = "54924cfd0f1b7878da53228aa54f3cdf3e405aa4d0ecefd185fcb75da9eea8eb"
ORIG_FRZ = "01cf2b17a882b2ab89873234a381720108dbb9d0dcd406a752962e280b71dc55"
NEW_ANA = hashlib.sha256(open("analysis/f1k.py", "rb").read()).hexdigest()
p = ROOT + "/registry/experiments/f1k.json"
raw = open(p, encoding="utf-8").read()
rec = json.loads(raw)
cur = rec["pins"]["analysis_script"]["sha256"]
assert raw.count(cur) == 1, "expected exactly one analysis-pin site"
idx = json.loads(open(ROOT + "/registry/frozen-index.json",
                      encoding="utf-8").read())
# [v3, re-review #5] BEFORE either the no-op exit OR the update path:
# (i) RECOMPUTED consistency — index, STORED record hash, and the
#     freshly RECOMPUTED frozen hash of the record AS IT IS must all
#     agree. A mismatch is a dirty/corrupt record, NOT a resume. (v2
#     compared only index == stored hash and the cur==NEW_ANA no-op
#     exited before any recomputation at all.)
assert idx["f1k"] == rec["frozen_sha256"] == kc.frozen_hash(rec), \
    "record/index/recompute desync — dirty or corrupt record; STOP"
# (ii) ORIG-COUNTERFACTUAL — normalizing ONLY the analysis pin back to
#     ORIG_ANA in a deep copy must reproduce ORIG_FRZ: the analysis
#     pin is PROVEN the SOLE delta being re-frozen. This also kills a
#     "forged-consistent" dirty record whose frozen_sha256 was
#     recomputed over unrelated edits — (i) alone passes that case
#     [MEASURED: both the pass and both refusal branches demoed on the
#     real committed record, this box 2026-07-18]. Subsumes v2's
#     first-pass-only chain-head check on every pass.
cf = copy.deepcopy(rec)
cf["pins"]["analysis_script"]["sha256"] = ORIG_ANA
assert kc.frozen_hash(cf) == ORIG_FRZ, \
    "record carries edits BEYOND the analysis pin — refusing to " \
    "re-freeze them; diff the record against the committed bytes"
if cur == NEW_ANA:
    print("no-op: record already pins the current analysis bytes")
    sys.exit(0)
rec["pins"]["analysis_script"]["sha256"] = NEW_ANA
new_frz = kc.frozen_hash(rec)          # status + frozen_sha256 excluded
rec["frozen_sha256"] = new_frz
kc.write_canonical_json(p, rec)
idx["f1k"] = new_frz
kc.write_canonical_json(ROOT + "/registry/frozen-index.json", idx)
print("NEW_ANALYSIS_SHA =", NEW_ANA)
print("NEW_FROZEN_SHA   =", new_frz)
```

**[v3, re-review #5] What the hardened guards make IMPOSSIBLE: re-freezing unrelated edits.** Every pass — including the `cur == NEW_ANA` no-op, which now sits BELOW both asserts and can no longer skip recomputation — proves (i) the record/index pair is exactly what its own stored hash claims (recomputed, not trusted) and (ii) the record differs from the COMMITTED frozen state (`ORIG_FRZ`) in the analysis pin ALONE. A rerun over a record carrying any other dirty edit dies at (i); a record whose dirt was hash-laundered into a self-consistent `frozen_sha256` dies at (ii). Negative probe: §7-B1n (pure local file copies — fits the $0 gate; both refusal branches exercised, [v4] each asserted by its EXPECTED exit code (1, the Python `AssertionError` exit [MEASURED, this box 2026-07-18]) AND its branch-specific assert message on stderr — `record/index/recompute desync` for (i), `carries edits BEYOND the analysis pin` for (ii) — with the scratch registry pair sha-verified byte-identical after each refusal; any nonzero exit alone no longer passes).

Then splice `NEW_ANALYSIS_SHA` into `f1k_gcp.py:57` (+ `:14` echo) and `NEW_FROZEN_SHA` into `f1k_gcp.py:51` (+ `:5`/`:49` echoes, `bringup_gcp.sh:43`, `poc/gcp/README.md:5`), and both into the seq-3 record (§5.2). ALL of this stays UNCOMMITTED until the §7 oracle is green; everything then lands in the SAME landing commit (§4 rows 1–8 together — the registry-check first-try condition is unchanged).

---

## 5. REGISTRATIONS

### 5.1 ASM-2513 — append ONE line to `registry/assumptions.jsonl` (next free id — last is ASM-2512, verified 2026-07-18), in the SAME landing commit (register-ASM-with-commit; no dangling id)

```json
{"id": "ASM-2513", "tag": "STIPULATED", "claim": "F1-K PIN=<stats-file> CONFORMANCE FIX (lawful bug-fix TOWARD the frozen design; NOT a science change; kot-correction/1 seq 3): the frozen F1-K design defines the pinning knob as PIN=<stats-file> (the hot-expert pin list) with PIN_GB fixed at bring-up from measured free RAM and recorded in the manifest [docs/next/design/glm52-followup-experiment.md SS7.1 lines 638-639], matching the engine's own file-based pin semantics [glm52-kernel-integration-northstar.md:92, fetch-grade per ASM-1971, re-verified at bring-up]. The pre-fix implementation could not run it and could ONLY emit a FALSE pinning attestation: f1k_driver.py validate_pinning accepted solely the literal PIN==\"1\" (to the engine, a stats-file path named '1' that pins nothing) and analysis/f1k.py:648-651 schema-locked the ledger's expert_pinning.PIN to the constant \"1\" - so any 'pinned' run would attest a hot store no engine verified, silently voiding the ASM-2205 1.20x lever the ASM-2374 $155 ceiling prices. TRUTHFUL-PINNING REQUIREMENT (this fix): (a) PIN=<path> ONLY - the literal \"1\" is REFUSED (ERR_F1K_PINNING; accepting both would preserve the false-attestation channel); (b) the stats-file is validated (exists, non-empty, basename conforming to the pinned schema's rule [A-Za-z0-9._+-]{1,255} excluding \"1\" ENFORCED AT CONFIG LOAD so no schema-rejectable path ever spends first, ASCII-only '<layer> <expert> <count>' int triples - MEASURED format poc/gcp/probe-results/accum20.stats; Unicode 'digits' and non-finite PIN_GB REFUSED) and its sha256 DERIVED FROM BYTES; (c) engine arming is POSITIVELY verified from the CURRENT invocation's evidence ONLY, DESCRIPTOR-BOUND [v3]: check_pin_engagement reads the deterministic append-mode stderr log via os.fstat+os.pread ON THE RETAINED DESCRIPTOR the child wrote through (opened a+; NEVER a by-name re-open, so a rotated/replaced pathname carrying a planted banner substitutes nothing), from a byte offset captured after open and BEFORE spawn that is a REQUIRED argument (no whole-file fallback exists at any call site), with a non-blocking exclusive flock held for the invocation refusing a second cooperating writer on the log (advisory - best-effort vs an uncooperative same-box writer, stated, outside the threat model) - so neither a PRIOR invocation's stale armed banner nor a pathname decoy can ever authorize a newly unpinned process; missing PIN at engagement time and zero gb_used likewise REFUSED - before the first scored item (banner WORDING is fetch-grade and lives only in the unpinned driver - the pinned analysis schema carries hash+counters, never the format); (d) ledger/sidecar expert_pinning carries {PIN basename (pattern-excludes \"1\"), pin_file_sha256, pin_file_lines, PIN_GB, engine-attested experts_pinned >= 1, pin_scope shared-all-arms (SS7.1 matched budget; F1K-CONSTRUCTION-PLAN.md SS5 item 6 minimum realization), semantics}; (e) [R10-4] the resume-auth binding carries pin_file_sha256 + pin_gb re-derived from bytes (within-phase), AND the cross-phase seam - the resume-safe cost ledger, the only state spanning pilot/guard/test (the per-phase bindings carry `phase` and never compare across it) - compares BOTH pin_file_sha256 AND PIN_GB on every resume/re-init, REFUSES re-initialization when the ledger is MISSING while campaign evidence exists - the evidence predicate LEADS with a durable SPEND-START sentinel (spend-start.jsonl: appended + fsynced, file AND directory entry, to the outdir BEFORE every metered engine Popen; append-only, NEVER deleted/rotated/superseded by the campaign path, lifecycle stipulated in the fix memo SS1d2 with exactly two lawful removals: the mock's clean-slate reset and the maintainer-authorized archiving reset; no spawn without a durable sentinel, fail closed on OSError) so even a hard interruption in the spawn-to-first-checkpoint window (child spent; only manifests/logs persisted, none of them predicate paths) cannot be followed by a silent fresh-ledger re-init, while the ordinary VIRGIN-outdir fresh start (no sentinel, no artifacts - every Ledger is constructed before its outdir's first spawn) is preserved and POSITIVELY probed [v4]; exact predicate in the fix memo SS1e (carrier-provenance.json, legitimately written pre-ledger, deliberately excluded) - restoring the ledger or a maintainer-authorized archiving reset is the named recovery [v3] - and the pilot addendum-7 - the THIRD cross-phase pin state, which records expert_pinning at pilot time - is COMPARED (pin sha + PIN_GB, same exact-equality semantics as the ledger seam) at pre-test consumption instead of trusted [v3], so a resumed, multi-VM, ledger-deleted, or phase-boundary run can never silently swap the pin or its budget (CONSTRUCTION-PLAN SS5 item 5). PIN-FILE PROVENANCE: the M4 dev-item pin (pin_50gb.stats sha 6802cc97..., GCS-resident, only the .sha256 witness in-repo) does NOT transfer - the campaign pin is RE-DERIVED on the real construction corpus at bring-up (STATS=on over the real prefills, CONSTRUCTION-PLAN SS5.4); the $0 --mock oracle exercises the accept+hash+verify path with a deterministic MOCK stats-file, never the GCS artifact. RE-FREEZE SCOPE: the ONLY frozen-surface change is the analysis/f1k.py expert_pinning schema (sha 54924cfd... -> re-pinned at land; f1k.json /pins/analysis_script/sha256 + frozen_sha256 + frozen-index + f1k_gcp.py:51/:57 re-recorded together, kot-correction/1 seq 3); EVERY science pin is byte-identical - geometry 3..77=75 [ASM-2504], 19,964 prefills [ASM-2405], engine a78a06fc, weights, endpoints, kill criterion, envelope, ASM-2371 power table, $155/900h caps [ASM-2374], [73,155]/[260.6,900] floors, rate window, seeds. This fix is the PREREQUISITE for ANY pinned execution (probe M5 and the PINNED construction/campaign) per F1K-AFFORDABILITY-DECISION.md SS4/SS5.1. Registered WITH the landing commit of poc/gcp/F1K-PIN-FILE-FIX.md (f1k_driver.py + mock_colibri.py + harness README edits, the materialized reusable re-pin splice poc/gcp/f1k_repin_splice.py, analysis/f1k.py schema fix, registry/corrections/f1k/3-pin-file-fix.json, f1k.json+frozen-index+f1k_gcp.py re-pins, $0 --mock oracle green).", "rationale": "The affordability review (F4/v3 fix 5, endorsed) established that PIN=1 without a hashed real stats-file is 'a false pinning attestation waiting to be emitted', and SS5.1 established the lawfulness reading: the literal-\"1\" driver check and the _c(\"1\") schema constant are an INCOMPLETE IMPLEMENTATION of the frozen PIN=<stats-file> semantics - fixing them to accept, validate, hash, engine-verify, and truthfully record the pin makes the implementation CONFORM to the freeze while changing no window, cap, protocol step, endpoint, or claim envelope. Because the fix touches the sha-pinned grading arbiter it is NOT a designer's unilateral act: it lands through the coordinator review-gate with the $0 --mock emission-surface oracle re-run green against the extended schema (f1-k round-4 lesson) with registered-scale cost figures (round-6 lesson), and the touched pins re-recorded via the same kot-correction/1 mechanics as the seq-2 layer re-freeze.", "backing_ref": "docs/next/design/glm52-followup-experiment.md SS7.1:638-639 (frozen PIN=<stats-file>/PIN_GB semantics); docs/next/design/glm52-kernel-integration-northstar.md:92 (engine pin-from-stats-file); poc/glm52-probe/f1k-harness/f1k_driver.py:711-741 pre-fix literal check + analysis/f1k.py:648-651 pre-fix _c(\"1\") lock; poc/gcp/F1K-AFFORDABILITY-DECISION.md SS3/SS4/SS5.1 (F4, execution gap, lawful-bug-fix reading); poc/gcp/F1K-CONSTRUCTION-PLAN.md SS5 items 1-7 + SS5.4 (beefed spec; pin non-transfer); poc/gcp/probe-results/m4.json + accum20.stats + pin_50gb.sha256 (MEASURED stats format, h_pin band, dev-pin hash 6802cc97); registry/corrections/f1k/2-layer-geometry-refreeze.json (re-freeze mechanics precedent); poc/gcp/F1K-PIN-FILE-FIX.md (this fix's exact diffs)", "load_bearing": true, "status": "open", "owner": "designer-20", "date": "2026-07-18"}
```

### 5.2 `registry/corrections/f1k/3-pin-file-fix.json` — the kot-correction/1 seq-3 record (create at land; placeholders computed per §4)

```json
{"schema_version": "kot-correction/1", "experiment": "f1k", "seq": 3,
 "date": "2026-07-18T00:00:00Z", "author": "coordinator-1",
 "kind": "pre-run conformance correction (PIN=<stats-file> truthful-pinning fix)",
 "defect": "The frozen design defines PIN=<stats-file> with PIN_GB fixed at bring-up (glm52-followup-experiment.md SS7.1:638-639), but f1k_driver.py validate_pinning accepted ONLY the literal PIN==\"1\" and analysis/f1k.py:648-651 schema-locked the ledger's expert_pinning.PIN to the constant \"1\" - an implementation that cannot execute the frozen semantics and can only emit a FALSE pinning attestation (the engine pins nothing from a stats-file path named '1' while the ledger attests the ASM-2205 1.20x lever). Coordinator-verified execution gap: F1K-AFFORDABILITY-DECISION.md v3 fix 5 / F1K-CONSTRUCTION-PLAN.md SS5.",
 "authorized_by": "Maintainer authorization to advance F1-K (2026-07-18) + the endorsed SS5.1 lawful-bug-fix reading (F1K-AFFORDABILITY-DECISION.md; review-gated because it touches the pinned analysis) + ASM-2513 (registered in this same commit) + the $0 --mock emission-surface oracle re-run GREEN against the extended expert_pinning schema before landing (f1-k round-4/round-6 lessons), per poc/gcp/F1K-PIN-FILE-FIX.md.",
 "changes": [
   "/pins/analysis_script/sha256: 54924cfd0f1b7878da53228aa54f3cdf3e405aa4d0ecefd185fcb75da9eea8eb -> <SHA256-OF-EDITED-analysis/f1k.py, COMPUTED AT LAND>. The analysis edit is CONFINED to the cost.expert_pinning schema node + its docstring line + its own selftest fixture/probes (analysis/f1k.py :247, :648-651, :1959-1962, :2387-2388 per poc/gcp/F1K-PIN-FILE-FIX.md SS2): PIN _c(\"1\") -> {PIN basename (pattern-excludes \"1\"), pin_file_sha256 HEX64, pin_file_lines>=1, PIN_GB>0, experts_pinned>=1 (engine-attested), pin_scope _c(\"shared-all-arms\"), semantics}. NO statistical, floor, window, phase, power, or verdict logic changed.",
   "NO other frozen-record field changes. The harness_manifest's historical 'analysis/f1k.py BYTE-IDENTICAL at its pin' sentences remain as (true) witnesses of THEIR passes - this correction supersedes their currency (seq-2 precedent for the directory-digest sentence).",
   "Same-commit launch-pin re-points (code, outside the record): poc/gcp/f1k_gcp.py:51 FROZEN_SHA256 01cf2b17... -> <NEW frozen_sha256>; poc/gcp/f1k_gcp.py:57 PINS[analysis/f1k.py] 54924cfd... -> <NEW analysis sha>; comment echoes f1k_gcp.py:5/:14/:49, bringup_gcp.sh:43, poc/gcp/README.md:5."
 ],
 "kill_criterion_status": "UNCHANGED verbatim (this correction touches the expert_pinning provenance schema and the analysis sha pin only; endpoints, TOST margins, power, caps, floors, rate window, envelope untouched).",
 "non_retroactivity": "No pilot, construction, or campaign has executed (no results-log/f1k.jsonl run record exists); no ledger was ever emitted under the superseded PIN=\"1\" schema. Nothing is retroactively regraded.",
 "legitimacy": "Truthful-pinning conformance repair TOWARD the frozen design (SS5.1 reading, endorsed): the frozen semantics are PIN=<stats-file> ONLY; the literal \"1\" was never engine semantics, so the pre-fix surfaces could only attest pinning that never happened. The fix adds provenance the frozen design already presumes (a named, hashed, engine-verified pin; PIN_GB recorded from bring-up) and binds it into the [R10-4] resume auth so a resumed/multi-VM run cannot silently swap the pin. Prerequisite for ANY pinned run (probe M5 + the PINNED construction/campaign); the campaign pin itself is RE-DERIVED on the real construction corpus at bring-up (the M4 dev pin 6802cc97... does not transfer, F1K-CONSTRUCTION-PLAN.md SS5.4).",
 "refreeze_chain": "supersedes frozen_sha256 01cf2b17a882b2ab89873234a381720108dbb9d0dcd406a752962e280b71dc55",
 "supersedes_frozen_sha256": "01cf2b17a882b2ab89873234a381720108dbb9d0dcd406a752962e280b71dc55",
 "refrozen_sha256": "<COMPUTED AT LAND: kot_common.frozen_hash of the corrected record>",
 "build_artifacts": "poc/gcp/F1K-PIN-FILE-FIX.md v4 (exact diffs; GPT-5.6 round-1 THROUGH round-3 review fixes incorporated); f1k_driver.py + mock_colibri.py + harness README edits (driver NOT sha-pinned - re-pins nothing); poc/gcp/f1k_repin_splice.py (the ONE reusable SS4 re-pin splice, py_compile-checked, used by the live SS7-B1 splice AND the SS7-B1n negative probes - each B1n variant asserts exit code 1 + its branch-specific assert message + scratch bytes unchanged, never merely nonzero); $0 --mock oracle green AGAINST the locally recomputed record/index pins (working tree, pre-commit - the official seam verifies the record's analysis pin, so the recompute must precede the oracle; the SS7-B1n splice-guard NEGATIVE probe runs on scratch copies first) incl. the ASM-2513 v4 fail-closed probe set (legacy \"1\", missing, malformed, bad basename, non-ASCII digits, non-finite PIN_GB, unarmed engine, STALE-BANNER-RESUME, LOG-ROTATION-SWAP pathname decoy, ledger-hash-vs-bytes EXPECTED-HASH mismatch, cross-phase PIN_GB swap, MISSING-LEDGER re-init beside campaign artifacts, SPEND-START-sentinel-beside-missing-ledger spawn-to-checkpoint crash window + VIRGIN-outdir fresh-start positive probe, addendum-7 pin/PIN_GB mismatch at pre-test consumption, [R10-4] pin-swap resume) and the mock pin stats-file; build_carriers.py selftest green (generator untouched, regression guard); poc/gcp/f1k_gcp.py plan green at the re-pointed pins; tools/registry/registry-check.py green post-land."}
```

---

## 6. THE $0-MOCK ORACLE — spec (round-4 lesson: the driver's `--mock` IS the emission-surface oracle; run it against the touched schema BEFORE re-freezing)

**[v2, review #6 — ordering prerequisite]:** the oracle's official seam copies the edited `analysis/f1k.py` beside `f1k.json` and verdict-gen verifies the record's `/pins/analysis_script/sha256` against the file bytes — so the §4 LOCAL working-tree re-pin recompute (new analysis sha → `f1k.json` + frozen-index + `f1k_gcp.py`, new `frozen_sha256`) MUST run before the oracle, with NOTHING committed until the oracle is green (the re-FREEZE is the landing commit, not the recompute — round-4 lesson honored in substance). §7 carries the exact command order.

**The mock pin-file** (`mock-out/fixtures/mock-pin.stats`, regenerated by every `--mock` run; §1g): 128 lines `"{3+(i%12)} {i} {4096-17*i}"`, i = 0..127 — deterministic literals, seeded by nothing, in the MEASURED stats format (3-int triples, `accum20.stats`). Env `PIN=<abs path to it>`, `PIN_GB=48` (mock placeholder in the M4-measured 40–50 GB headroom band — DISCLOSED placeholder; the real value is fixed at bring-up). The mock engine reports `[PIN] hot-expert store armed: pinned 128 experts, 2.210 GiB (budget 48.00 GiB) from mock-pin.stats`, which the driver's `check_pin_engagement` verifies (basename match, 1 ≤ 128 ≤ 128, budget == PIN_GB, used ≤ budget) and records. **The oracle never touches the GCS dev pin.** Cost config keeps the registered planning-scale figures (prior 146.0 / construction 521.2 h, ASM-2374 corner — round-6 lesson, unchanged at :3276–3278).

**What GREEN attests (truthful ledger provenance end-to-end):** ledger + sidecar `cost.expert_pinning` = `{PIN: "mock-pin.stats", pin_file_sha256: <derived 64-hex>, pin_file_lines: 128, PIN_GB: 48.0, experts_pinned: 128, pin_scope: "shared-all-arms", semantics: …}` flows through build_sidecar → kot-log/1 record → the OFFICIAL seam (log-append → verdict-gen → **pinned analysis**) → `PASS-PENDING-AUDIT`, with the direct supplementary ingest also exit 0 — i.e. the EDITED schema accepts exactly what the EDITED driver truthfully emits. Fail-closed probes proven in the same run (§1i, v4 set): legacy `"1"` REFUSED, missing file REFUSED, malformed file REFUSED, schema-illegal basename REFUSED at config load (review #3 — never after spend), non-ASCII "digit" triples REFUSED, non-finite `PIN_GB` (NaN and inf) REFUSED, unarmed engine (fault-injected `MOCK_PIN_FORCE_LOAD_FAIL=1`) ABORTED with zero rows scored, **STALE-BANNER-RESUME REFUSED** (review #6 probe (b): a byte-perfect armed banner pre-seeded from a "prior invocation" into the deterministic append-mode log + a `MOCK_PIN_SILENT=1` engine → the pre-spawn-offset slice sees no banner → RED, zero rows — the exact case v1's whole-file scan would have wrongly passed), **LOG-ROTATION-SWAP REFUSED** (v3 re-review #1: a `MOCK_PIN_ROTATE_LOG` engine, silent on its true fd-inherited stderr, plants a pathname decoy of length ≥ the pre-spawn offset carrying a stale banner after it — the case v2's by-name read would have wrongly passed; the descriptor-bound read sees no banner on the true file object → RED, zero rows, decoy verified present at the pathname), **EXPECTED-HASH MISMATCH REFUSED** (review #6 probe (a): the pin file's bytes change after ledger init → `check_pin_engagement` re-derives from bytes, ledger `pin_file_sha256` ≠ file bytes → RED, zero rows), cross-phase `PIN_GB` swap at the ledger seam REFUSED (review #5), **MISSING-LEDGER RE-INIT REFUSED** (v3 re-review #3: a pilot artifact exists but `cost-ledger.json` does not → `Ledger.__init__` fails closed naming the recovery path), **SPEND-START CRASH-WINDOW REFUSED** (v4 round-3 #2: the sentinel is the ONLY thing in the outdir — a spawn was attempted, the run died before any checkpoint, the ledger was then lost → `Ledger.__init__` fails closed; the exact case where v3's seven-path predicate saw nothing), **VIRGIN-OUTDIR FRESH START PRESERVED** (v4 positive probe: no sentinel, no artifacts → fresh init proceeds and persists; plus the self-check `[5]` conjunct proving the mock campaign's own metered spawns wrote the sentinel at the outdir root), **ADDENDUM-7 PIN/PIN_GB MISMATCH REFUSED** (v3 re-review #3: `check_addendum_pinning` on a pilot-recorded sha or budget differing from the current config → RED, both variants probed), pin-swap resume REFUSED ([R10-4]). The analysis's own selftest additionally proves the schema REJECTS `PIN="1"`, a short hash, and `experts_pinned=0` (§2d).

**Speed note (per the acceptance-gate instruction):** `f1k_driver.py --mock` builds its own small fixtures (fast, minutes on this box) — the slow 75-layer `mock-out/carriers-6144` rebuild is NOT required for this gate. `mock_e2e_carriers.py` is RECOMMENDED as a second emission-surface pass (it re-runs `gen_mock_fixtures` + ends in the pinned-analysis ingest and needs NO edit, §1h note); it consumes the pre-built `mock-out/carriers-6144` — if absent on the applying box, rebuild per `F1K-LAYER-REFREEZE.md` §1.8-G1 or skip for this gate.

---

## 7. ACCEPTANCE GATE — exact commands the coordinator runs (ALL exit 0; order matters — [v2, review #6] corrected: local re-pin recompute BEFORE the oracle, commit only after green)

```bash
# A. apply SS1 + SS2 + SS3 edits AND materialize the SS4 splice script
#    VERBATIM to poc/gcp/f1k_repin_splice.py (working tree only; the
#    script lands in the same commit — [v4, round-3 #3] ONE reusable
#    exact implementation, used by BOTH B1n and B1 below; no
#    verbatim-placeholder duplication anywhere in this gate)

# B. LOCAL PRE-ORACLE RE-PIN RECOMPUTE (ALL of SS7-B runs at the REPO
#    ROOT; working tree ONLY — NOTHING is committed in this step; v2
#    gate-order fix, review #6). The official seam copies the edited
#    analysis/f1k.py beside f1k.json and verdict-gen verifies the
#    record's analysis pin against file bytes: with the OLD sha in the
#    record the oracle CANNOT go green.
# B0: [v4] the materialized splice must be BYTE-VALID python BEFORE any
#     probe interprets its exit status
python3 -m py_compile poc/gcp/f1k_repin_splice.py
# B1n: [v3, re-review #5 / v4, round-3 #3] splice-guard NEGATIVE probe
#      ($0, scratch copies; run BEFORE the live splice; BOTH refusal
#      branches). Variant (a): dirty an UNRELATED record field -> the
#      splice must die at assert (i). Variant (b): additionally forge
#      frozen_sha256 = kot_common.frozen_hash(dirty rec) + frozen-index
#      to match, so (i) passes -> the splice must die at assert (ii).
#      [v4] Each variant asserts its EXPECTED failure, not merely
#      nonzero: exit code EXACTLY 1 (the Python AssertionError exit)
#      AND the branch-specific assert message on stderr — a syntax
#      error, bad import, or wrong path also exits nonzero but cannot
#      print the expected message, so it can no longer fake a pass —
#      and the scratch registry pair must be byte-identical after each
#      refusal (the splice's writes come only AFTER its asserts).
#      [MEASURED: this exact command sequence run on a materialized
#      copy against copies of the real committed record, this box
#      2026-07-18 — pristine control exit 0 "no-op", (a) exit 1 +
#      message (i), (b) exit 1 + message (ii), shas unchanged]
T=$(mktemp -d); mkdir -p "$T/registry/experiments"
cp registry/experiments/f1k.json "$T/registry/experiments/"
cp registry/frozen-index.json    "$T/registry/"
python3 - "$T" <<'EOF'                # (a) dirty an unrelated field
import json, sys
p = sys.argv[1] + "/registry/experiments/f1k.json"
rec = json.load(open(p, encoding="utf-8"))
rec["schema_version"] = str(rec["schema_version"]) + " DIRTY"
json.dump(rec, open(p, "w", encoding="utf-8"))
EOF
sha256sum "$T/registry/experiments/f1k.json" \
          "$T/registry/frozen-index.json" > "$T/pre-a.sum"
rc=0; python3 poc/gcp/f1k_repin_splice.py "$T" 2>"$T/err-a" || rc=$?
test "$rc" -eq 1                      # AssertionError exit, EXACTLY
grep -q "record/index/recompute desync" "$T/err-a"   # died at assert (i)
sha256sum -c --quiet "$T/pre-a.sum"   # refused WITHOUT writing
python3 - "$T" <<'EOF'                # (b) forge-consistent dirt
import json, sys
sys.path.insert(0, "tools/registry"); import kot_common as kc
r = sys.argv[1]
p = r + "/registry/experiments/f1k.json"
rec = json.load(open(p, encoding="utf-8"))
rec["frozen_sha256"] = kc.frozen_hash(rec)
kc.write_canonical_json(p, rec)
idx = json.loads(open(r + "/registry/frozen-index.json",
                      encoding="utf-8").read())
idx["f1k"] = rec["frozen_sha256"]
kc.write_canonical_json(r + "/registry/frozen-index.json", idx)
EOF
sha256sum "$T/registry/experiments/f1k.json" \
          "$T/registry/frozen-index.json" > "$T/pre-b.sum"
rc=0; python3 poc/gcp/f1k_repin_splice.py "$T" 2>"$T/err-b" || rc=$?
test "$rc" -eq 1                      # AssertionError exit, EXACTLY
grep -q "carries edits BEYOND the analysis pin" "$T/err-b"  # assert (ii)
sha256sum -c --quiet "$T/pre-b.sum"   # refused WITHOUT writing
rm -rf "$T"

python3 poc/gcp/f1k_repin_splice.py "${SPLICE_ROOT:-.}"
                                      # B1: SS4 splice (RE-RUNNABLE; live
                                      #     tree, ROOT=".") — new analysis
                                      #     sha -> f1k.json + frozen-index,
                                      #     new frozen_sha256
# B2: splice NEW_ANALYSIS_SHA into f1k_gcp.py:57 (+ :14 echo) and
#     NEW_FROZEN_SHA into f1k_gcp.py:51 (+ :5/:49 echoes,
#     bringup_gcp.sh:43, poc/gcp/README.md:5)

# C. the $0 emission-surface oracle, against the RECOMPUTED working tree
cd poc/glm52-probe/f1k-harness
python3 f1k_driver.py --mock          # C1: PIN=<mock-file> path + truthful
                                      #     provenance + the ASM-2513 v4 probe
                                      #     set: legacy "1" / missing /
                                      #     malformed / bad-basename /
                                      #     non-ASCII-digits / non-finite-
                                      #     PIN_GB / unarmed / STALE-BANNER-
                                      #     RESUME / LOG-ROTATION-SWAP /
                                      #     EXPECTED-HASH mismatch /
                                      #     cross-phase PIN_GB swap /
                                      #     MISSING-LEDGER re-init /
                                      #     SPEND-START crash window +
                                      #     VIRGIN-outdir fresh start
                                      #     preserved [v4] /
                                      #     addendum-7 pin+PIN_GB mismatch /
                                      #     [R10-4]
                                      #     pin-swap; expect self-check [5]
                                      #     green (incl. the spend-start
                                      #     sentinel at the mock outdir
                                      #     root) + official seam verdict
                                      #     PASS-PENDING-AUDIT + tampered
                                      #     fixture INSTRUMENT-INVALID; exit 0
python3 build_carriers.py selftest    # C2: generator untouched — regression
                                      #     guard; exit 0
python3 mock_e2e_carriers.py          # C3 (recommended; needs mock-out/
                                      #     carriers-6144 at 3..77 — rebuild
                                      #     per F1K-LAYER-REFREEZE SS1.8-G1
                                      #     if absent); exit 0
python3 -c "import sys; sys.path.insert(0,'.'); import f1k_driver as d; \
print(d.json.dumps(d.validate_pinning({'engine':{'env':{'PIN':'mock-out/fixtures/mock-pin.stats','PIN_GB':'48'}}}), indent=1))"
                                      # C4: spot-check the derived record shape
cd ../../..

# D. ANY red: fix the SS1/SS2 edits, re-run B1/B2 (the splice is
#    re-runnable — it moves <current record pin> -> <current file sha>),
#    re-run C until green. NOTHING is committed while red.

# E. registrations (working tree): seq-3 record (SS5.2, refrozen_sha256
#    filled from B1) + ASM-2513 append (SS5.1)

# F. post-recompute mechanical gates
python3 tools/registry/registry-check.py            # F1: ALL checks - frozen-drift
                                                    #     (f1k @ NEW hash), corpus pins,
                                                    #     claims, account-lint, chain;
                                                    #     corrections/*/3-pin-file-fix.json
                                                    #     linted; exit 0 FIRST TRY iff SS4
                                                    #     rows 1-8 land together
python3 tools/registry/registry-check.py frozen-drift   # F2: explicit drift line
                                                    #     "ok frozen-drift: f1k (<NEW8>)"
python3 poc/gcp/f1k_gcp.py plan                     # F3: $0 dry-plan (needs
                                                    #     KOT_GCP_PROJECT from
                                                    #     ~/.config/kot/gcp.env): verifies
                                                    #     the re-pointed FROZEN_SHA256 +
                                                    #     PINS incl. the NEW analysis sha,
                                                    #     reuse gate, SPOT config, and the
                                                    #     UNCHANGED windows - expect
                                                    #     "frozen_sha256": "<NEW>",
                                                    #     usd_cap 155.0, instance_hours
                                                    #     [260.6, 900.0], rate window
                                                    #     [0.0811, 0.5948], DRY-PLAN OK

# G. ONE landing commit: SS1+SS2+SS3 edits + SS4 rows 1-8 + SS5 records
#    — the re-FREEZE happens HERE, after the oracle went green (round-4
#    lesson honored: nothing was frozen/committed before the oracle).
```

Any red = fix within the same working set before landing; nothing lands red and nothing is committed red. `registry-check` passes first try only because §4 rows 1–8 (record + index + orchestrator pins + seq-3 record + ASM-2513) land TOGETHER in step G.

---

## 8. Self-check table (claim → citation)

| # | Claim | Citation |
|---|---|---|
| 1 | Frozen semantics = `PIN=<stats-file>` + `PIN_GB` fixed at bring-up; no `PIN=1` form in the frozen design | `glm52-followup-experiment.md` §7.1:638–639 (knob table read 2026-07-18) |
| 2 | Engine pin semantics are file-based ("loadable from a stats file PIN=stats.txt"); wording fetch-grade | `glm52-kernel-integration-northstar.md:92`; ASM-1971 rider (§7.1:648–650: semantic surprise → halt for amendment BEFORE data collection) |
| 3 | Driver accepts only literal `"1"`; analysis locks `PIN` to `_c("1")` | `f1k_driver.py:711–741` (`if str(pin) != "1"`); `analysis/f1k.py:648–651` (verbatim quoted in §1b/§2a) |
| 4 | Lawful-bug-fix reading; prerequisite for ANY pinned run; review-gate + $0-mock oracle + re-record | `F1K-AFFORDABILITY-DECISION.md` §5.1 (grounds 1–3), §4 M5 prerequisite; `F1K-CONSTRUCTION-PLAN.md` §5 |
| 5 | Pin-file format `<layer> <expert> <count>` int triples | [MEASURED] `poc/gcp/probe-results/accum20.stats` (16,184 lines, real engine STATS on the GCP box) |
| 6 | M4 dev pin sha `6802cc97…`, GCS-resident, does NOT transfer; re-derived at bring-up | `pin_50gb.sha256`, `m4.json /pin`, `probe-results.json /M4`; `F1K-CONSTRUCTION-PLAN.md` §5.4 [EXTRAPOLATION checked at pilot per its §5.7] |
| 7 | `f1k_driver.py` (and `mock_colibri.py`) are NOT sha-pinned — their edits re-pin nothing | `f1k.json /pins/harness_manifest` "(f1k_driver.py, not sha-pinned here)" ×2; `f1k_gcp.py:55–68` `PINS` (no driver/mock rows); `F1K-LAYER-REFREEZE.md` §1.5 row "driver not sha-pinned anywhere" |
| 8 | `54924cfd` verifying sites = exactly 2 (`/pins/analysis_script/sha256`; `f1k_gcp.py:57`) + 1 comment echo (`:14`); frozen hash `01cf2b17` sites = record + index + `f1k_gcp.py:51` + echoes `:5`/`:49`/`bringup_gcp.sh:43`/`poc/gcp/README.md:5` | repo grep 2026-07-18 (memos/run-logs excluded as historical witnesses); `frozen-index.json["f1k"]` read |
| 9 | The frozen record contains NO `PIN=1`/`expert_pinning` text — the ONLY record change is the analysis sha | raw-text grep of `f1k.json` for `PIN`/`expert_pinning`/`validate_pinning`/`PIN_GB` (5 hits, all cost-lever prose, none semantic) |
| 10 | No `data/` tree edit ⇒ A-time directory digest `e53622e3…` and all corpus pins UNCHANGED (unlike seq 2) | §1/§2 edit list (no `data/` path); seq-2 record (digest history) |
| 11 | Frozen-hash mechanics: `kot_common.frozen_hash` excludes `status`+`frozen_sha256`; canonical write; index must match same-commit | `tools/registry/kot_common.py:142–152`; `_f1k_carrierauth_fix_20260716.py` precedent; `f1k_gcp.py verify_pins` :152–176 |
| 12 | Schema pattern discipline: `\Z` + `re.fullmatch`, never `$` | `analysis/f1k.py:493–503` (round-6 fix note), `:816` |
| 13 | Mock cost config keeps registered figures 146.0/521.2 (round-6 lesson) — untouched | `f1k_driver.py:3265–3278`; bd memory `f1-k-round-6-scale-floor-mock-lesson` |
| 14 | Oracle-first ordering (mock against the touched schema BEFORE refreezing) | bd memory `f1-k-round-4-lesson…`; §7 order A→B→C |
| 15 | ASM-2513 free (last registered = ASM-2512); correction seq 3 free (existing: 1, 2) | `registry/assumptions.jsonl` tail; `registry/corrections/f1k/` listing (2026-07-18) |
| 16 | [R10-4] location + mechanism; binding is pure function of config + pinned artifacts; generic equality check enforces new fields with no further edit | `f1k_driver.py:449, 1899–1942, 1968–2034` |
| 17 | Mock arithmetic: 128×18,541,666.7 B = 2.210 GiB ≤ 48; counts coherent; regex matches the emitted banner | §1c/§1g/§1h construction; [MEASURED] per-expert bytes `m4.json` |
| 18 | Per-arm pin map + h_pin≥0.60 floor consciously OUT of scope (shared realization recorded as such) | `F1K-CONSTRUCTION-PLAN.md` §5 items 6–7 (§0 scope note) [STIPULATED] |
| 19 | No @handle/account strings in any proposed hashed byte range (registry-check account-lint covers corrections/*.json) | this memo + §5 JSON (pseudonymous owners only); `registry-check.py:219` |
| 20 | [v2 #2] Stderr log is a DETERMINISTIC filename opened APPEND (stale prior-invocation banner survives); v1 whole-file scan = stale-banner authorization hole; closed by the pre-spawn byte offset (§1c/§1d) | [MEASURED] `f1k_driver.py:1732–1733` (`"%s.%s.pass%d.log"`, `open(..., "a")`); review #2 |
| 21 | [v2 #2] `str.isdigit()` admits Unicode digits (`int('٣')==3`, `int('²')` raises); `float('nan')<=0` is False and `float('inf')>0` is True — v1 checks passed NaN/inf and Unicode triples | [MEASURED] python3 one-liners, this box 2026-07-18 (§1b comments carry the results verbatim) |
| 22 | [v2 #3] Resolution chosen: DRIVER enforces the schema's basename rule at config load (schema unchanged, stays strict); `PIN_BASENAME_RE` is a verbatim mirror of the §2a pattern, cross-cited both sides; probe `pin_badname` proves fail-BEFORE-spend | §1b constant + §2a pattern (textually identical `(?!1\Z)[A-Za-z0-9._+-]{1,255}` fullmatch, [MEASURED] via re.fullmatch checks 2026-07-18); review #3 |
| 23 | [v2 #5] [R10-4] bindings are per-phase (`phase` in the binding, separate pilot/guard/test constructions) so they can NEVER compare PIN_GB across a phase boundary; the cost ledger is the only cross-phase state and now compares BOTH pin sha AND PIN_GB | `f1k_driver.py:1927` (binding carries `phase`), `:2116` (`gbind` per-phase), `:1421–1427` (ledger "spans pilot + guard + test"); §1e v2 diff; review #5 |
| 24 | [v2 #6] v1's "oracle before re-pin" could not go green: the official seam verifies the record's analysis pin against the edited file's bytes; v2 order = local recompute (uncommitted) → oracle → land; splice made re-runnable for red-oracle iterations | §4 (re-runnable splice + guards), §6 prerequisite note, §7 A–G order; review #6 |
| 25 | [v2 #6] Both mandated negative probes are IN the $0 oracle: EXPECTED-HASH mismatch (`pin_hashswap`: ledger pin-hash ≠ file bytes → RED, zero rows) and STALE-BANNER-RESUME (`pin_stale`: prior-invocation banner + `MOCK_PIN_SILENT=1` engine → RED, zero rows) | §1i v2 probes; §1h `MOCK_PIN_SILENT` knob; §6 GREEN definition; self-check line [5] gates on both (§1j) |
| 26 | [v3 #1] A by-name re-open reads a DIFFERENT file after pathname rotation: a decoy of length ≥ the offset with a stale banner after it fools the name-read but NOT `os.fstat`+`os.pread` on the retained descriptor; `os.pread` on a write-only `"a"` fd raises EBADF (hence the `"a+"` open); `flock` LOCK_EX\|LOCK_NB refuses a second same-inode opener while held | [MEASURED] python3 decoy-rotation + EBADF + flock demos, this box 2026-07-18; §1c/§1d diffs; re-review #1 |
| 27 | [v3 #3] The Ledger `else` branch silently re-initialized on a MISSING ledger; the §1e existence predicate names the COMPLETE set of campaign artifact/checkpoint writers under `outdir` (pilot-rows, 4 pilot addendum/gate files, guard raw shards, test rows) ([v4]: the predicate now additionally LEADS with the SPEND-START sentinel — rows 30–31) | `f1k_driver.py:1457–1459` (else branch); writer sites `:2649/:2990/:2728/:2969/:2936/:2119/:2171` (repo grep 2026-07-18); re-review #3 |
| 28 | [v3 #3] Addendum-7 RECORDS `expert_pinning` at pilot time but pre-test consumption never COMPARED it — the third cross-phase pin state; §1e2 binds sha + `PIN_GB` at consumption with the ledger seam's exact-equality semantics (NaN-safe: unparseable `PIN_GB` → NaN → `!=` → refused) | `f1k_driver.py:2902–2912` (emission), `:2215–2241` (consumption, comparison absent pre-v3); §1e2; re-review #3 |
| 29 | [v3 #5] v2's splice never RECOMPUTED (the `cur == NEW_ANA` no-op exited first; the guard compared index to the STORED hash only); the v3 chained recompute + ORIG-counterfactual pass on the committed record and refuse BOTH dirty variants — plain dirt at assert (i), forged-consistent dirt (frozen_sha256 recomputed over the dirt) at assert (ii) | [MEASURED] `kot_common.frozen_hash` chained-equality + counterfactual + both refusal branches on the real committed record, this box 2026-07-18; §4 script; §7-B1n; re-review #5 |
| 30 | [v4 #2] The spawn-to-checkpoint crash window is REAL and was uncovered: `run_scoring_pass` writes the manifest (:1702), opens stderr (:1733) + the label log (:1736), `Popen`s the engine (:1738), and opens the selected-rows checkpoint only at :1755 — the child can spend in between, and none of those artifacts was among the 7 predicate sentinels. Closed by the SPEND-START sentinel: fsynced (file + dirent) BEFORE `Popen`, first in the §1e predicate; coverage argument — spend requires a spawn, every metered spawn is sentinel-preceded, so "spend + missing ledger ⟹ sentinel present ⟹ refuse" | `f1k_driver.py:1702/:1732–1733/:1736/:1738/:1755` (read this pass); §1d2 + §1d second hunk + §1e diff; [MEASURED] file-append+fsync then O_RDONLY-directory-fd fsync demo, this box 2026-07-18; round-3 #2 |
| 31 | [v4 #2] The virgin-outdir fresh start (round-3-confirmed property) is preserved BY CONSTRUCTION and proven: every `Ledger` is constructed BEFORE its outdir's first spawn (`:4007` real, `:3425` mock precede every `run_scoring_pass` call) and ALL campaign pass call sites are metered (`ledger=ledger` at `:2123/:2180/:2676/:2741/:2745/:2749/:2755`; only probe spawns pass None) — so no sentinel can exist at virgin-init time; NOT "any outdir artifact": `carrier-provenance.json` precedes fresh-ledger construction (`:4004/:3422`) and is excluded; the mock clean slate (`:3399–3409`) unlinks the sentinel WITH `cost-ledger.json` (`:3407`), so `--mock` re-runs stay green | call-site grep + driver reads, this pass 2026-07-18; §1d2 lifecycle stipulation; positive probe §1i `pin_virgin`; crash-window probe §1i `pin_spendstart` ([v5, round-4 #1]: its sequence FIRST asserts the same-basis NORMAL-RESUME positively — ledger+sentinel coexisting, a same-config `Ledger` proceeds reporting the config-derived pin sha + `PIN_GB` (`pin_spendresume`, gated by `pin_closed`) — so the probes distinguish all THREE states: virgin / normal-resume / crash-window); round-3 #2 |
| 32 | [v4 #3] B1n now discriminates: a Python `assert` failure exits EXACTLY 1, and each B1n variant requires that exit code AND its branch-unique stderr message (`record/index/recompute desync` for (i); `carries edits BEYOND the analysis pin` for (ii)) AND sha-verified no-write on the scratch pair — a syntax error, bad import, wrong path, or placeholder also exits nonzero (SyntaxError/ImportError exit 1 too) but cannot print the expected assert message, so exit code alone is deliberately NOT the gate; one reusable splice file serves B1 and B1n, so no placeholder can reappear | [MEASURED] this box 2026-07-18: `python3 -m py_compile` clean on the materialized copy; the exact §7-B1n sequence run against copies of the real committed record — pristine control exit 0 + "no-op" line, variant (a) exit 1 + message (i), variant (b) exit 1 + message (ii), `sha256sum -c` clean after both; `assert False` exit-code demo = 1; §4 file; §7 B0/B1n/B1; round-3 #3 |

---

## Revision log (v2)

v2, 2026-07-18, designer-20 — per the GPT-5.6 review verdict (`poc/gpt56-review/f1k-pin-fix-review-VERDICT.md`, APPROVE-WITH-FIXES). **Preserved unchanged (review AGREE):** the §0 `PIN=<path>`-only reading (verdict #1) and the §4 exhaustive re-pin inventory (verdict #4), plus the ASM-2513 + seq-3 correction mechanics and the analysis-schema-changes-no-science claim.

| Review # | Defect (v1) | v2 fix | Where |
|---|---|---|---|
| #2 (SECURITY) | Pin-engagement verifier scanned the WHOLE deterministic append-mode stderr log — after an interruption a PRIOR invocation's stale armed banner could authorize a NEWLY UNPINNED process (a false attestation, the exact channel this fix exists to close) | Per-invocation evidence only: `run_scoring_pass` captures the log's byte size after open/before `Popen` (`err_start`, `os.path.getsize` — not text-mode `tell()`), and `check_pin_engagement(stderr_start=...)` reads ONLY `bytes[err_start:]` + this invocation's freshly collected stdout banners; a log shorter than the offset is refused. Additionally REFUSED: missing `PIN` at engagement time (was a silent `return`), zero `gb_used`, non-finite `PIN_GB` (NaN slid past `gb <= 0` [MEASURED]), non-ASCII "digits" in triples (`isdigit()` admits Unicode [MEASURED]) | §1b, §1c, §1d hunk 1+4; probes §1i `pin_stale`/`pin_nangb`/`pin_infgb`/`pin_nonascii` |
| #3 | Driver accepted ANY basename; pinned schema permits only `[A-Za-z0-9._+-]{1,255}` excluding `"1"` — a valid path could RUN and be schema-rejected only AFTER spend | Resolution: DRIVER enforces the IDENTICAL rule at config load (schema unchanged — it stays the strict, authoritative copy): `PIN_BASENAME_RE`, a verbatim mirror of the §2a pattern, fails closed in `validate_pinning` before any spend | §1b; probe §1i `pin_badname`; self-check row 22 |
| #5 | Ledger resume compared only the prior pin SHA, not prior `PIN_GB`; [R10-4] bindings are per-phase (`phase` in the binding, `:1927`; separate pilot/guard/test constructions, `:2116`) → `PIN_GB` could silently change at a phase boundary | The cross-phase seam — the resume-safe cost ledger, the only state spanning pilot/guard/test — now compares BOTH `pin_file_sha256` AND `PIN_GB` on every resume/re-init; §3 states the within-phase vs cross-phase seam split honestly | §1e v2 diff, §3 note; probe §1i `gb_ledgerswap` |
| #6 | "Oracle before re-pin" could not go green: the official seam copies the edited analysis beside `f1k.json` still carrying the OLD sha → verdict-gen rejects; splice script was one-shot | Gate order corrected to: apply → LOCAL working-tree re-pin recompute (§4 splice, now RE-RUNNABLE; NOTHING committed) → $0 oracle → registrations → mechanical gates → ONE landing commit (re-freeze = the commit, after green; round-4 lesson honored in substance). Two negative probes added INSIDE the oracle: (a) EXPECTED-HASH mismatch (`pin_hashswap`) and (b) STALE-BANNER-RESUME (`pin_stale`, via the new `MOCK_PIN_SILENT=1` knob) | §4, §6, §7 A–G, §1h, §1i |
| #7 (roll-up) | The three risks above had to close before registry landing or GCP spend | All closed above; the §1j self-check line `[5]` now gates on the FULL v2 probe set, and §5.1/§5.2 registration texts updated to describe the v2 mechanics | §1j, §5 |

Out-of-scope note (named, not silently changed): `check_kae_engagement` retains its v1 whole-file by-name scan — the analogous KAE stale-banner/rotation exposure was not flagged by either review round and is left for its own tracked follow-up (NEXT-ACTION, follow-ups). [v3] The descriptor mechanics CHANGE that follow-up's shape and shrink it: the `"a+"` open, the invocation flock, and `err_start` now already exist at the shared `errf`/log, so the KAE fix reduces to passing `(errf, stderr_start=err_start)` and reading the same fd-bound slice — same plumbing, no new state.

---

## Revision log (v3)

v3, 2026-07-18, designer-20 — per the GPT-5.6 round-2 verdict (`poc/gpt56-review/f1k-pin-fix-rereview-VERDICT.md`, APPROVE-WITH-FIXES). **Preserved unchanged (round-2 CLOSED — not touched):** #3 basename mechanics (§1b/§2a) and #6 oracle ordering + the `pin_stale`/`pin_hashswap` probes and A–G gate order — intersected only where the v3 evidence plumbing requires (the §1d engagement call now passes `errf`; the §4 splice guards are strengthened in place, order intact).

| Re-review # | Defect (v2) | v3 fix | Where |
|---|---|---|---|
| 1 (remaining slice of the false-attestation channel) | The child writes through the open `errf` descriptor but verification re-opened `stderr_path` BY NAME (`Path.read_bytes()`) — a rotated/replaced pathname of length ≥ `stderr_start` carrying a stale banner after the offset passed the short-file guard; concurrent ownership unaddressed; the permissive `stderr_start=0` default allowed silent whole-file fallback | Descriptor-bound evidence: log opened `"a+"` (`os.pread` raises EBADF on a write-only fd [MEASURED]); invocation-scoped `fcntl.flock` LOCK_EX\|LOCK_NB refuses a second cooperating writer (advisory — tagged best-effort vs an uncooperative same-box writer, honesty note in §1c); offset from `os.fstat(errf.fileno())`; slice via `os.pread` on the RETAINED descriptor (rotation-immune [MEASURED]); `stderr_start` now a REQUIRED keyword-only argument — the `=0` default is REMOVED | §1c, §1d hunks 1+4 (+ `import fcntl`); probe §1i `pin_rotate` via §1h `MOCK_PIN_ROTATE_LOG/_PAD`; §1j `[5]`; §5.1 (c) |
| 3 | The ledger comparison fired only when `cost-ledger.json` EXISTED — the `else` branch silently re-initialized after ledger loss/deletion, voiding the cross-phase basis; addendum-7 RECORDED `expert_pinning` but pre-test consumption never COMPARED it (third cross-phase state unbound) | Missing-ledger fail-closed on an exact campaign-evidence predicate (all 7 artifact/checkpoint writer paths named, §8 row 27) with the recovery path in the error (restore the ledger / maintainer-authorized archiving reset); new `check_addendum_pinning` (§1e2) binds addendum sha AND `PIN_GB` at consumption, ledger-seam equality semantics, transitively binding addendum↔ledger | §1e second hunk, §1e2, §3 v3 note; probes §1i `pin_noledger` + `pin_addsha`/`pin_addgb`; §5.1 (e) |
| 5 | The re-runnable splice asserted only record==index on the STORED hash — never recomputed; the `cur == NEW_ANA` no-op exited before ANY check that would recompute, and a rerun over a record carrying unrelated dirty edits would silently re-freeze them | Before EITHER exit path: chained `assert index == record.frozen_sha256 == kot_common.frozen_hash(record)` (recomputed, fail-closed = dirty/corrupt record, not a resume) + the ORIG-counterfactual (deep-copy with ONLY the analysis pin normalized to `ORIG_ANA` must reproduce `ORIG_FRZ` — the analysis pin is PROVEN the sole re-frozen delta; also kills forged-consistent dirt that passes (i)) [MEASURED, both refusal branches, real record]; no-op exit moved BELOW the asserts; §4 states the impossibility (re-freezing unrelated edits); §7-B1n negative probe, both variants | §4 script + prose; §7 B1n; §8 row 29 |

All three route into the aggregate: `pin_closed` gains `pin_rotate`/`pin_noledger`/`pin_addsha`/`pin_addgb` (§1i), self-check `[5]` text + gate updated (§1j), §5.1 ASM-2513 clauses (c)/(e) and §5.2 build_artifacts re-worded to the v3 mechanics, §6 GREEN definition extended, §7 gains B1n and the v3 C1 probe list. The `check_kae_engagement` out-of-scope note above is retained with its v3 follow-up shape.

---

## Revision log (v4)

v4, 2026-07-18, designer-20 — per the GPT-5.6 round-3 verdict (`poc/gpt56-review/f1k-pin-fix-round3-VERDICT.md`, APPROVE-WITH-FIXES). **Preserved unchanged (round-3 CLOSED — not touched):** the descriptor-bound stderr evidence (§1c/§1d hunk 1, finding #1), the splice guard logic and assert messages (finding #3 first half — independently exercised by the reviewer on the real record; byte-stable in the §4 file form), and everything the regression sweep confirmed (finding #4: fd slice, basename rule, A–G ordering, re-pin inventory, seq-3 propagation, ASM-2513 wording, virgin-outdir non-blocking) — intersected only where a v4 fix requires (the §1e predicate gains the sentinel as its leading entry; the §4 splice moves verbatim into `poc/gcp/f1k_repin_splice.py`).

| Round-3 # | Defect (v3) | v4 fix | Where |
|---|---|---|---|
| 2 (missing-ledger predicate incomplete) | Real spawn-to-checkpoint crash window: `run_scoring_pass` writes a manifest (:1702), opens stderr/label logs (:1733/:1736), `Popen`s the engine (:1738); the selected-rows checkpoint opens only at :1755 — the child can SPEND in between, a hard interruption there persists only manifests/logs (none among the 7 predicate sentinels), and a subsequently missing `cost-ledger.json` fresh-inited a new pin/budget basis silently | Durable SPEND-START sentinel (`spend-start.jsonl`), appended + fsynced (file AND directory entry [MEASURED]) to the ledger's outdir BEFORE every metered `Popen`; semantics "engine spawn attempted under this ledger basis"; lifecycle STIPULATED (§1d2): append-only, one per campaign outdir, never deleted/rotated/superseded on the campaign path — only the mock clean-slate reset (unlinked WITH the ledger, new diff) and the maintainer archiving reset remove it; leads the §1e missing-ledger predicate; explicitly NOT "any outdir artifact" (`carrier-provenance.json` pre-ledger at :4004/:3422, excluded); virgin-outdir fresh start preserved by construction (Ledger precedes first spawn: :4007/:3425; all campaign passes metered) and POSITIVELY probed | §1d2 (new), §1d second hunk, §1e second-hunk prose+diff, §3 v4 note; probes §1i `pin_spendstart` (sentinel-only outdir + missing ledger → refuse) + `pin_virgin` (fresh init proceeds); §1j `[5]` (+ sentinel-at-outdir-root conjunct); §5.1 (e); §6; §8 rows 30–31 |
| 3 (B1n not a valid negative gate) | `! python3 ...` passed on ANY nonzero exit — a syntax error, bad import, wrong path, or the literal `...SS4 splice script verbatim...` placeholder went green without exercising either assertion; the printed B1 "exact commands" contained that same non-executable placeholder | The splice is ONE reusable exact implementation materialized to `poc/gcp/f1k_repin_splice.py` (§4; guards byte-stable, only shebang/docstring + `ROOT` default added; py_compile-checked [MEASURED]); §7-B0 syntax-checks it before any probe interprets its exit status; each B1n variant asserts its EXPECTED failure — exit code EXACTLY 1 (AssertionError) AND the branch-specific message on stderr ((i) `record/index/recompute desync`, (ii) `carries edits BEYOND the analysis pin`) AND sha-verified no-write on the scratch pair; B1 invokes the same file on the live tree; every §7 command executable as printed [MEASURED: full B1n sequence + pristine no-op control run on this box] | §4 (file form + prose), §7 A/B0/B1n/B1; §5.2 build_artifacts; §8 row 32 |

Both route into the bookkeeping: `pin_closed` gains `pin_spendstart`/`pin_virgin` (§1i), self-check `[5]` text + gate updated (§1j), §5.1 clause (e) and the landing file list re-worded to the v4 mechanics, §5.2 updated (v4, splice file, probe list), §6 GREEN definition extended, §7 gains A-materialization/B0 and the executable B1n, §8 gains rows 30–32 (row 27 annotated), NEXT-ACTION steps 1–3/6 updated. All other v3 text — including every round-3 CLOSED mechanic — is stable.

---

## Revision log (v5)

v5, 2026-07-18, designer-20 — per the GPT-5.6 round-4 verdict (`poc/gpt56-review/f1k-pin-fix-round4-VERDICT.md`, APPROVE-WITH-FIXES, exactly ONE item; findings 2–3 CLOSED and untouched, all other mechanics stable): §1i `pin_spendstart` now asserts the NORMAL-RESUME state POSITIVELY before its unlink — while ledger+sentinel coexist, a same-config `Ledger(...)` must proceed (not raise) reporting the config-derived pin sha + `PIN_GB` (`pin_spendresume`, wired into `pin_closed`) — so the probe sequence distinguishes all THREE states: virgin (`pin_virgin`) / normal-resume (new) / crash-window (existing post-unlink fail-closed); bookkeeping only: §1j `[5]` wording + §8 row 31 annotated; amended §1i block rehearsed [MEASURED: full block materialized to `/tmp/f1k_probe_5b4_v5.py`, `py_compile` clean + resume<unlink<expect_stop order asserted, this box 2026-07-18]. Nothing else touched.

---

## NEXT-ACTION block (liftable into the coordinator issue — ONE landing commit for steps 1–5; NO spend, NO VM anywhere in this fix)

```
TITLE: F1-K driver PIN=<stats-file> fix (ASM-2513, kot-correction/1 seq 3):
       truthful-pinning prerequisite for ANY pinned run — apply + re-freeze

FACTS
- Frozen semantics: PIN=<stats-file>, PIN_GB fixed at bring-up
  (glm52-followup-experiment.md SS7.1:638-639; engine pins from a stats
  file, northstar:92). Driver accepts ONLY literal PIN=="1"
  (f1k_driver.py:711-741); analysis/f1k.py:648-651 schema-locks PIN to
  "1" -> a pinned run can currently emit ONLY a false pinning attestation.
- Lawful bug-fix TOWARD the freeze (AFFORDABILITY SS5.1, endorsed), but it
  edits the sha-pinned analysis -> kot-correction/1 seq-3 re-freeze
  (seq-2 layer-refreeze mechanics). Science pins ALL byte-identical
  (3..77/75 ASM-2504, 19,964 prefills, engine a78a06fc, weights, power,
  endpoints, kill/envelope, $155/900h, floors, seeds).
- The M4 dev pin (pin_50gb.stats 6802cc97..., GCS) does NOT transfer; the
  campaign pin is RE-DERIVED at bring-up (CONSTRUCTION-PLAN SS5.4). The $0
  oracle uses a deterministic MOCK stats-file (128 measured-format lines).

STEPS (coordinator, review-gate then ONE landing commit — [v2 review #6]
corrected order: local re-pin recompute BEFORE the oracle; commit only
after green)
1. Apply poc/gcp/F1K-PIN-FILE-FIX.md SS1 (f1k_driver.py 1a-1j — v3:
   descriptor-bound 1c/1d + import fcntl, 1e second hunk
   missing-ledger, 1e2 addendum binding; v4: 1d2 SPEND-START sentinel
   constant+helper + the pre-Popen 1d hunk + the mock clean-slate
   sentinel unlink, 1e predicate led by the sentinel — + mock_colibri.py
   1h incl. MOCK_PIN_SILENT + MOCK_PIN_ROTATE_LOG/_PAD + harness README
   1k) and SS2 (analysis/f1k.py :247/:648-651/:1959-1962/:2387-2388) +
   SS3 ([R10-4] binding), and MATERIALIZE the SS4 splice verbatim to
   poc/gcp/f1k_repin_splice.py (v4 round-3 #3 — the ONE reusable
   implementation; lands with the commit). Working tree only.
2. LOCAL RE-PIN RECOMPUTE (SS7-B, all at the REPO ROOT; working tree
   ONLY, NOTHING committed): FIRST SS7-B0 (python3 -m py_compile on the
   materialized splice), THEN the SS7-B1n splice-guard NEGATIVE probe
   (scratch copies; each refusal variant must exit EXACTLY 1 — the
   AssertionError exit — AND print its branch-specific assert message
   on stderr, (i) "record/index/recompute desync" / (ii) "carries
   edits BEYOND the analysis pin", AND leave the scratch registry pair
   sha-verified byte-identical; any-nonzero no longer passes — v4
   round-3 #3), THEN the SAME splice file on the live tree
   (RE-RUNNABLE, recompute + counterfactual guards) - new analysis
   sha ->
   f1k.json /pins/analysis_script/sha256 + frozen_sha256 + frozen-index;
   same values into f1k_gcp.py:51/:57 (+ echoes :5/:14/:49,
   bringup_gcp.sh:43, poc/gcp/README.md:5). Required BEFORE the oracle:
   the official seam verifies the record's analysis pin against the
   edited file's bytes - with the OLD sha the oracle can never go green.
3. Oracle (SS7-C): f1k_driver.py --mock GREEN (PIN=<mock-file> path,
   truthful ledger provenance, ASM-2513 v3 fail-closed probes: legacy
   "1" / missing / malformed / bad-basename / non-ASCII-digits /
   non-finite-PIN_GB / unarmed / cross-phase-PIN_GB-swap / [R10-4]
   pin-swap, PLUS the negative probes:
     (a) EXPECTED-HASH mismatch - pin file bytes changed after ledger
         init, ledger pin-hash != file bytes -> RED, zero rows;
     (b) STALE-BANNER-RESUME - a prior invocation's armed banner
         pre-seeded in the append-mode log + a MOCK_PIN_SILENT=1 engine
         must NOT satisfy the new unpinned run -> RED, zero rows;
     (c) [v3] LOG-ROTATION-SWAP - a MOCK_PIN_ROTATE_LOG engine plants
         a pathname decoy (pad >= offset + stale banner) while silent
         on its true fd stderr; the descriptor-bound read must refuse
         -> RED, zero rows, decoy verified present;
     (d) [v3] MISSING-LEDGER re-init - campaign artifact present,
         cost-ledger.json absent -> Ledger init REFUSES, recovery
         path named;
     (e) [v3] addendum-7 mismatch - pilot-recorded pin sha OR PIN_GB
         differing from current config -> pre-test consumption
         REFUSES, both variants;
     (f) [v4] SPEND-START crash window - the sentinel alone (spawn
         attempted, no checkpoint ever written) beside a missing
         cost-ledger.json -> Ledger init REFUSES (v3's predicate saw
         nothing here);
     (g) [v4] VIRGIN outdir positive probe - no sentinel, no
         artifacts -> fresh init PROCEEDS; self-check [5] also gates
         on the sentinel existing at the mock outdir root, proving
         the pre-Popen write on the real code path);
   build_carriers.py selftest GREEN. (Driver --mock builds its own small
   mock - the slow 75-layer carrier rebuild is NOT required.) Red? Fix,
   re-run step 2 (splice is re-runnable), repeat step 3. Commit NOTHING
   while red.
4. Register (SS5): append ASM-2513 to registry/assumptions.jsonl; create
   registry/corrections/f1k/3-pin-file-fix.json (refrozen_sha256 filled).
5. Gates (SS7-F): tools/registry/registry-check.py (+ frozen-drift line
   "ok frozen-drift: f1k (<NEW8>)"); poc/gcp/f1k_gcp.py plan -> DRY-PLAN
   OK with the UNCHANGED windows [$73,$155]/[260.6,900]h/[0.0811,0.5948].
   ALL exit 0; nothing lands red.
6. Land in ONE commit (SS1+SS2+SS3 edits + poc/gcp/f1k_repin_splice.py
   + SS4 rows 1-8 + SS5 records - the re-freeze IS this commit, after
   the green oracle) + push per
   session protocol; note in the maintainer thread: the PIN=<file>
   prerequisite for pinned M5 / PINNED construction is CLOSED and every
   emitted pinning attestation now describes the CURRENTLY-EXECUTING,
   verified-armed process; at bring-up: derive the real pin (STATS=on
   over the real prefills), set PIN_GB from measured free RAM, and
   re-verify the REAL engine pin banner wording (ASM-1971) - if it
   differs from PIN_ARMED_RE, HALT and amend the unpinned driver regex
   (recorded amendment, no re-freeze).
COST: $0. Follow-ups: (i) per-arm pin map + the h_pin >= 0.60 realized
floor (CONSTRUCTION-PLAN SS5 items 6-7) stay with the affordability/
addendum-(7) surface, NOT this fix; (ii) NEW, file as its own issue at
land: check_kae_engagement still scans the whole append-mode stderr log
BY NAME - the analogous KAE stale-banner/rotation exposure (not flagged
by either review round, not silently changed here) should get the SAME
descriptor-bound slice; v3 SHRINKS this follow-up: the a+ open, the
invocation flock, and err_start already exist at the shared errf/log,
so the fix reduces to passing (errf, stderr_start=err_start) and
pread-slicing - same plumbing, no new state.
```

*No @handle/account strings appear in this memo. No git, spend, VM, or registry write was performed by any pass (v1, v2, v3, v4, or v5). Working tree only: this file (v4's/v5's [MEASURED] checks ran on scratch copies under /tmp and read-only repo bytes).*

**Status (one line):** with the v4 fixes, every emitted pinning attestation describes the CURRENTLY-EXECUTING, actually-armed process, evidenced through the very descriptor it wrote, and every dollar of spend is preceded by a durable spend-start mark — no stale banner, rotated log, swapped/lost cross-phase pin state (ledger, binding, or addendum), spawn-window ledger loss, dirty re-freeze, placeholder-green probe, or post-spend schema rejection can produce or survive one.
