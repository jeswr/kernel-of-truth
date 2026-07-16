#!/usr/bin/env python3
"""One-shot CARRIER RE-REVIEW ROUND-10 content-authentication fix pass over
registry/experiments/f1k.json (2026-07-16, TENTH lawful pre-final
reset-refreeze).

The F1-K carrier re-review (2026-07-16, round 10) CONFIRMED the round-9
metadata gates (mode-bound verify, cached-resume re-verification,
artifact-derived shas, the driver [R9-PROV] ingest gate) but returned HOLD
with FOUR CONCRETE content-authentication gaps — the last content-integrity
holes. All four are now CLOSED in the generator
poc/glm52-probe/f1k-harness/build_carriers.py + the (unpinned) run driver
f1k_driver.py + the harness README:

  gap 1  MOCK TABLES COULD SATISFY REAL CONSUMERS: `verify --expect-mode
         mock` passed the registered D=6144 / 8-layer mock fixture and
         nothing content-level separated a mock construction from a real
         one (mock geometry may legally rehearse 3..78 / D=6144, so a
         mode-relabeled mock report satisfied every geometric check). Now
         THE ONLY REAL-RUN VERIFY PATH is --expect-mode real, which
         enforces mode=real AND layers 3..78 AND D=6144 AND a MOCK-STACK
         DENYLIST (binding provenance shas must not equal any repo mock
         script's digest — a relabeled mock construction fails; the
         driver's REAL ingest gate enforces the same denylist). The
         mock-mode verify is kept for TESTING ONLY: it refuses anything
         real-claiming, refuses to aim at the registered production corpus
         dir data/f1k-carriers-v1 (which `construct --mode mock` equally
         refuses to write into), and stamps its PASS line MOCK SCOPE ONLY.
  gap 2  ALL-ZERO MODE-REAL CARRIERS WERE ACCEPTED: correctly-shaped
         all-zero (or degenerate/constant) mode=real bodies passed the
         driver provenance gate AND the generator verify end-to-end
         (0-norm tables norm-match, reconstruct, and d0-re-derive as
         0 == 0). Now EVERY (c,l) vector of EVERY table must pass the
         NON-DEGENERACY check (all-zero / near-constant / below the
         min-variance floor std >= 1e-3 x rms / < 1/1024 nonzero all fail
         closed) — enforced at construction assembly, on every cached
         resume, at `verify` over every written table, and INDEPENDENTLY
         at driver ingest (full-coverage streaming scan, ERR_F1K_
         CARRIERPROV). Floors registered as STIPULATED (see the ASM
         ledger round-10 entry); a real S2.4 mean-difference carrier sits
         orders of magnitude above them.
  gap 3  CHECKPOINT VECTOR CONTENTS WERE UNAUTHENTICATED: construction
         checkpoints were shape/binding/finiteness-checked only, so v_k/
         v_d2 could be replaced with arbitrary finite values and consumed
         on resume. Now every per-concept checkpoint carries
         content_sha256 = sha256(kot-f1k-ckpt-content/1 | slot | layers |
         D | the exact little-endian f64 bytes of v_k then v_d2), bound
         into the construction report as checkpoint_content_sha256[96];
         construct RE-DERIVES + compares it on every cached resume
         (content-tampered, slot-swapped, and hash-less checkpoints are
         rejected — legacy pre-round-10 checkpoints rebuild from scratch,
         proven live on the actual round-8/9 fixture), `verify` re-derives
         it from the workdir checkpoints when present, and the driver
         REQUIRES the 96-entry witness for any REAL ingest.
  gap 4  CAMPAIGN RESUME STATE WAS UNAUTHENTICATED: read_ckpt treated ANY
         well-formed rows.jsonl as completed work, so a pre-fabricated
         resume file could bypass carrier/engine execution entirely. Now
         every scoring checkpoint (pilot-rows, guard raws, test rows)
         carries <rows>.auth.json [R10-4]: a running content hash
         (kot-f1k-rows-auth/1 domain over the exact row lines, updated in
         lockstep with every fsync'd append) + a binding to the CURRENT
         run's pinned inputs (K table sha, construction-report sha, engine
         argv + engine file shas, eval-manifest sha, phase). A resume
         whose hash or binding does not match is REFUSED (ERR_F1K_RESUME);
         rows beyond the auth-covered prefix are DROPPED and re-scored,
         never trusted — resume can neither skip real execution nor inject
         foreign rows.

Changing build_carriers.py changes its pinned sha256 (harness_manifest AND
the A_pre_spend rider) — so this is the TENTH lawful pre-final
reset-refreeze (precedents: _f1k_runhold_fix_20260715.py through
_f1k_carrierrereview_fix_20260716.py; f1k is STILL not GNG-0-signed and
results-log/f1k.jsonl STILL does not exist). The (A)-time carrier-input
directory digest is UNCHANGED this pass (no data/f1k-carriers-v1 edit; the
regenerated mock fixture lives under the harness mock-out/, never the
corpus). This script resets the record to DRAFT and applies EXACTLY the
deltas; prereg-freeze re-freezes under the full lints. Build artifact,
never part of the frozen record.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kot_common as kc

ROOT = Path(__file__).resolve().parents[2]
REC = ROOT / "registry" / "experiments" / "f1k.json"
IDX = ROOT / "registry" / "frozen-index.json"
GENDIR = ROOT / "poc" / "glm52-probe" / "f1k-harness"
OLD_FROZEN = "88443975f615b663926571d48b0b39b55b4878bd2b4cc501c14bed9adfcce4dc"
OLD_GEN_SHA = ("75c951d3d85d997811efb3f753e298fb73c209ceb6227974281bcab5"
               "3a84cb37")
ANALYSIS_PIN = ("54924cfd0f1b7878da53228aa54f3cdf3e405aa4d0ecefd185fc"
                "b75da9eea8eb")

rec = json.loads(REC.read_text(encoding="utf-8"))
assert rec["status"] == "FROZEN" and rec["frozen_sha256"] == OLD_FROZEN
kill_before = rec["kill_criterion_verbatim"]
env_before = rec["extrapolation_envelope_verbatim"]

# lawful pre-final window re-verified a TENTH time (conjunctive)
gng0 = ROOT / "registry" / "gng0-signoff.json"
if gng0.exists():
    assert "f1k" not in (json.loads(gng0.read_text())
                         .get("frozen_records") or {}), "f1k GNG-0-signed"
assert not (ROOT / "results-log" / "f1k.jsonl").exists(), \
    "results-log/f1k.jsonl exists — reset-refreeze is UNLAWFUL"

# ---- current artifact digests (computed, never transcribed) -----------------
NEW_GEN_SHA = hashlib.sha256(
    (GENDIR / "build_carriers.py").read_bytes()).hexdigest()
assert NEW_GEN_SHA != OLD_GEN_SHA
# (A)-time digest UNCHANGED this pass — no data/f1k-carriers-v1 edit
ATIME_DIGEST = kc.corpus_hash(str(ROOT), "f1k-carriers-v1")
assert ATIME_DIGEST in rec["pins"]["corpus_hashes"]["f1k-carriers-v1"], \
    "(A)-time digest drifted — this pass must not touch the corpus"
# analysis script UNTOUCHED this round (asserted byte-identical)
got_ana = hashlib.sha256(
    (ROOT / "analysis" / "f1k.py").read_bytes()).hexdigest()
assert got_ana == ANALYSIS_PIN == rec["pins"]["analysis_script"]["sha256"]

# ---- reset to DRAFT (freeze re-stamps these) --------------------------------
rec["status"] = "DRAFT"
for k in ("frozen_at", "frozen_by", "frozen_sha256"):
    rec.pop(k, None)
idx = json.loads(IDX.read_text(encoding="utf-8"))
assert idx.pop("f1k", None) == OLD_FROZEN
kc.write_canonical_json(IDX, idx)

# ---- 1. harness_manifest: generator re-pin + ROUND-10 rider -----------------
hm = rec["pins"]["harness_manifest"]
assert hm.count(OLD_GEN_SHA) == 1
hm = hm.replace(OLD_GEN_SHA, NEW_GEN_SHA)
hm += (
    " CARRIER RE-REVIEW ROUND-10 CONTENT-AUTHENTICATION CLOSURE "
    "(2026-07-16, tenth lawful pass; the round-9 metadata gates CONFIRMED "
    "by the re-review, untouched): build_carriers.py re-pinned at the sha "
    "above with (1) the ONLY real-run verify path = --expect-mode real "
    "enforcing mode=real AND the A(iv) layers 3..78 AND D=6144 AND a "
    "MOCK-STACK DENYLIST (binding provenance shas != every repo mock "
    "script digest — a mode-relabeled mock construction fails; a real "
    "report can never be satisfied by a mock table), the mock-mode verify "
    "reduced to TESTING SCOPE ONLY (refuses real-claiming reports, "
    "refuses the registered production corpus dir data/f1k-carriers-v1 — "
    "which construct --mode mock equally refuses to write into — and "
    "stamps MOCK SCOPE on its pass line); (2) FULL-COVERAGE NON-"
    "DEGENERACY: every (c,l) vector of every table rejects all-zero/"
    "near-constant/below-min-variance/trivially-sparse bodies (floors "
    "std >= 1e-3 x rms, >= 1/1024 nonzero; STIPULATED — an all-zero set "
    "previously satisfied EVERY check since 0-norm tables norm-match, "
    "reconstruct and d0-re-derive as 0 == 0), enforced at assembly, on "
    "every cached resume, at verify, and independently at driver ingest; "
    "(3) CHECKPOINT CONTENT HASH: per-concept content_sha256 = "
    "sha256(kot-f1k-ckpt-content/1 | slot | layers | D | exact LE f64 "
    "v_k+v_d2 bytes) bound into checkpoint AND report "
    "(checkpoint_content_sha256[96]), re-derived+compared on every cached "
    "resume (content-tampered/slot-swapped/hash-less checkpoints "
    "rejected; legacy round-8/9 checkpoints proven REFUSED live, fixture "
    "rebuilt from scratch), re-derived by verify from the workdir "
    "checkpoints, REQUIRED by the driver for real ingest. The RUN DRIVER "
    "(f1k_driver.py, not sha-pinned here) additionally gained [R10-4] "
    "CAMPAIGN RESUME AUTHENTICATION closing gap (4): every scoring "
    "checkpoint (pilot-rows/guard-raws/test-rows) carries "
    "<rows>.auth.json — a running kot-f1k-rows-auth/1 content hash over "
    "the exact row lines updated in lockstep with every fsync'd append, "
    "bound to the run's pinned inputs (K table, construction report, "
    "engine argv+file shas, eval manifest, phase); a foreign/tampered/"
    "unauthenticated resume fails ERR_F1K_RESUME and uncovered tails are "
    "dropped+re-scored, so resume can neither skip real execution nor "
    "inject foreign rows. SELFTEST green 2026-07-16 ($0): 19/19 "
    "fail-closed probes (the 11 round-9 probes + replaced-vector/"
    "hash-less/all-zero-with-valid-hash checkpoints rejected, "
    "relabeled-mock-under-real rejected by the denylist, real-claiming-"
    "under-mock rejected, production-dir mock construct AND mock verify "
    "refused, all-zero 7-table set with a fully coherent report rejected "
    "by verify non-degeneracy). Mock construction REBUILT from scratch "
    "2026-07-16 ($0, the legacy checkpoints fail closed by design): "
    "generator verify green incl. non-degeneracy over every table, the "
    "checkpoint-content witness re-derived from all 96 workdir "
    "checkpoints, and the FULL d0 byte-exact re-derivation; verify "
    "--expect-mode real on the same mock set FAILS CLOSED (exit 2). "
    "Driver --mock green end-to-end incl. the round-10 batteries "
    "([R10-1/2/3]: all-zero real fixture REFUSED, mock-stack-relabel "
    "REFUSED, missing content witness REFUSED, the valid real-mode "
    "fixture now NON-DEGENERATE and PASSING; [R10-4]: tampered row / "
    "rows-without-auth / foreign-binding resume REFUSED, injected "
    "trailing row DROPPED, genuine state resumes cleanly, the live "
    "campaign resumed through the auth path after the forced "
    "interruption); mock_e2e_carriers.py DRIVER-ACCEPTANCE PASS with the "
    "SAME mock D=6144 tables REFUSED by the REAL-mode gate. Harness "
    "README updated with the round-10 audit rows. Geometry, power table, "
    "budget cap ($155, worst-case $129.40/$139.59 corner UNCHANGED), "
    "kill criterion, envelope ALL UNCHANGED by this pass; analysis/f1k.py "
    "BYTE-IDENTICAL at its pin.")
rec["pins"]["harness_manifest"] = hm

# ---- 2. A_pre_spend: generator re-pin + round-10 rider ----------------------
np_ = rec["design"]["n_planned"]
fm = np_["freeze_manifest"]
a = fm["A_pre_spend"]
assert a.count(OLD_GEN_SHA) == 1
a = a.replace(OLD_GEN_SHA, NEW_GEN_SHA)
a += (
    " CARRIER RE-REVIEW ROUND-10 CONTENT-AUTHENTICATION CLOSURE "
    "(2026-07-16, tenth lawful pass; latest revision governs on "
    "conflict): (i) the ONLY verify path that can bless a REAL "
    "construction/report is --expect-mode real (mode=real + A(iv) 3..78 "
    "+ D=6144 + the mock-stack sha denylist); the mock-mode verify is "
    "testing scope only — it can never satisfy a real report and never "
    "aims at the registered production corpus dir, which mock "
    "constructions can never write into; (ii) every (c,l) carrier vector "
    "must be NON-DEGENERATE (all-zero/near-constant/min-variance-floor/"
    "trivially-sparse bodies fail closed; STIPULATED floors std >= 1e-3 "
    "x rms and >= 1/1024 nonzero) at assembly, cached resume, verify, "
    "and driver ingest; (iii) per-concept checkpoint vector contents are "
    "CONTENT-HASHED (kot-f1k-ckpt-content/1, exact LE f64 bytes, "
    "slot/layers/D-bound), witnessed in the report "
    "(checkpoint_content_sha256[96]), re-derived on every cached resume "
    "and by verify from the workdir checkpoints, and REQUIRED by the "
    "driver for real ingest; (iv) campaign checkpoint/resume state is "
    "AUTHENTICATED ([R10-4] <rows>.auth.json: running kot-f1k-rows-auth/1 "
    "content hash + binding to the run's pinned inputs; foreign/tampered/"
    "unauthenticated resumes fail ERR_F1K_RESUME, uncovered tails are "
    "dropped+re-scored). The pinned analysis, all seeds, the pass "
    "accounting (4,608 EXACT construction / <= 2,112 pilot), corner "
    "economics ($129.40 mandatory / $139.59 +REPLACE vs the UNCHANGED "
    "$155 cap), geometry, power table, kill criterion and envelope are "
    "ALL UNCHANGED by this pass; the (A)-time carrier-input directory "
    "digest is UNCHANGED (no data/f1k-carriers-v1 edit).")
fm["A_pre_spend"] = a

# ---- 3. title rider ----------------------------------------------------------
rec["title"] += (
    " HOLD REFREEZE 10 (2026-07-16, carrier re-review round-10 "
    "content-authentication closure; registry/corrections/f1k/"
    "1-prefreeze-correction.json amended): mock-stack denylist + "
    "production-corpus exclusivity (a real report can never be satisfied "
    "by a mock table; mock verify = testing scope only), full-coverage "
    "carrier non-degeneracy (all-zero/near-constant/min-variance bodies "
    "refused at generator AND driver), checkpoint-content hashing "
    "(kot-f1k-ckpt-content/1, report-witnessed, resume re-derived), and "
    "the driver-side [R10-4] authenticated campaign resume "
    "(kot-f1k-rows-auth/1 content hash + pinned-input binding; "
    "foreign/tampered/unauthenticated resume refused). Analysis pin, "
    "geometry, power table, budget cap, kill criterion, envelope all "
    "unchanged.")

# ---- invariants ---------------------------------------------------------------
assert rec["kill_criterion_verbatim"] == kill_before
assert rec["extrapolation_envelope_verbatim"] == env_before
assert rec["budget"]["usd_cap"] == 155
assert "0.8043" in np_["mc_exact_power_confirmation"]
assert rec["pins"]["analysis_script"]["sha256"] == ANALYSIS_PIN
assert len(rec["pins"]["analysis_script"]["output_fields"]) == 50

kc.write_canonical_json(REC, rec)
print("f1k.json RESET to DRAFT + carrier round-10 content-authentication "
      "deltas applied;\n  generator sha %s -> %s\n  (A)-time digest "
      "UNCHANGED %s"
      % (OLD_GEN_SHA[:12], NEW_GEN_SHA[:12], ATIME_DIGEST[:12]))
