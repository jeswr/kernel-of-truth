#!/usr/bin/env python3
"""f1k_generator_repin_splice.py — kot-correction/1 seq-4 generator re-pin.

COORDINATOR-ONLY, POST-REVIEW-GATE. Applies the frozen-record half of the
F1-K generator re-pin amendment (poc/gcp/F1K-GENERATOR-REPIN.md): splices the
carrier-construction generator pin a92be3e4… -> 91baba62… at BOTH embed sites
of registry/experiments/f1k.json (pins.harness_manifest + the FREEZE-(A)
COMPLETION clause of design.n_planned.freeze_manifest.A_pre_spend), installs
the seq-4 correction record, and re-freezes the frozen-index.

TRANSACTION MODEL (Rev2 blocker 2 — a partial apply must NOT be launchable):
the frozen-index is the SOLE completion marker and is written LAST. Write order
is record -> correction -> index, and ASM-2525 must ALREADY be registered as a
precondition. So `frozen-index[f1k] == POST` is reached only after the record,
the correction, and the ASM are all in place — the paid launch gate
(f1k_gcp._construction_launch_gate) keys off exactly that value plus a re-check
of the correction + ASM. Any exception mid-write ROLLS BACK record + index to
their pre-splice bytes and removes a freshly-created correction, so the tree is
left either fully pre-splice or fully applied — never a launchable half-state.

IDENTITY (Rev2 blocker 4): the draft correction is validated with the FULL
kot_common.check_identity_fields + require_no_account_strings before any write,
so an invalid author/account string cannot be copied into the registry.

FROZEN-DRIFT CHECK (Rev2 blocker 3): the post-write verification uses the flag
form `--frozen-drift`, checks the RETURN CODE (fail-closed on nonzero), and
binds the FULL expected hash from the on-disk frozen-index — never an 8-hex
prefix line alone.

DO NOT run this before the GPT-5.6 cross-vendor review of
poc/gcp/F1K-GENERATOR-REPIN.md passes (Rev2): landing it IS the freeze
amendment on the paid path. Until it lands, poc/gcp/f1k_gcp.py verify_pins()
dies F1K_PIN_FROZEN by design (its FROZEN_SHA256 already carries the
post-splice value) — the interim tree cannot license a launch.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "tools" / "registry"))
import kot_common as kc  # noqa: E402

OLD_BUILDER = "a92be3e4fe535c1dfefc41e2a422e010d25e8e40cf8e4cc123e7d829d63e9e61"
NEW_BUILDER = "91baba62649ad81217a4dd51cfcb57536c81b50e7f38ce8e622a161c1056835b"
PRE_FROZEN = "35372275354c7d3841dcf627b70edf64ffbe15190a0669658c5b6df082dc9b9c"
POST_FROZEN = "7897dd0a8fbb432768d70e959a77abdd80c16c78ab93702ff6f1671828bf7802"

RECORD = REPO / "registry" / "experiments" / "f1k.json"
INDEX = REPO / "registry" / "frozen-index.json"
ASSUMPTIONS = REPO / "registry" / "assumptions.jsonl"
DRAFT = HERE / "f1k-generator-repin" / "4-generator-repin.json"
CORRECTION = REPO / "registry" / "corrections" / "f1k" / "4-generator-repin.json"


def die(msg):
    print("ERR_F1K_SEQ4_SPLICE: %s" % msg, file=sys.stderr)
    sys.exit(2)


def _asm_registered(asm_path, asm_id):
    """Rev3/Rev4 blocker 2: fully fail-closed. True IFF the WHOLE ledger parses
    (every non-empty line a JSON OBJECT) AND EXACTLY ONE object has id==asm_id.
    A read error, a malformed/non-object line ANYWHERE (scanned in full, never
    an early return), zero matches, or a duplicate target id -> False. This
    matters MORE here than in the launcher: the splice has no preceding full
    registry-check, so it must never apply + report success against a malformed
    or ambiguous assumption ledger."""
    try:
        text = Path(asm_path).read_text(encoding="utf-8")
    except OSError:
        return False
    count = 0
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        try:
            obj = json.loads(s)
        except ValueError:
            return False
        if not isinstance(obj, dict):
            return False
        if obj.get("id") == asm_id:
            count += 1
    return count == 1


def main():
    if "--apply" not in sys.argv[1:]:
        die("refusing without --apply (coordinator-only, post-review-gate)")

    # ---- preconditions (NO writes) ---------------------------------------
    raw = RECORD.read_text(encoding="utf-8")
    rec = json.loads(raw)
    if raw != kc.canonical_dumps(rec) + "\n":
        die("f1k.json is not canonical — refusing to splice")
    if kc.frozen_hash(rec) != PRE_FROZEN or rec.get("frozen_sha256") != PRE_FROZEN:
        die("f1k.json is not at the expected pre-state %s…" % PRE_FROZEN[:8])
    if raw.count(OLD_BUILDER) != 2:
        die("expected exactly 2 builder-pin sites, found %d"
            % raw.count(OLD_BUILDER))
    if raw.count(NEW_BUILDER) != 0:
        die("new builder sha already present — record not at pre-state")

    iraw = INDEX.read_text(encoding="utf-8")
    idx = json.loads(iraw)
    if iraw != kc.canonical_dumps(idx) + "\n":
        die("frozen-index.json is not canonical — refusing")
    if idx.get("f1k") != PRE_FROZEN:
        die("frozen-index f1k != expected pre-state %s…" % PRE_FROZEN[:8])

    if CORRECTION.exists():
        die("seq-4 correction record already installed: %s" % CORRECTION)
    if not DRAFT.is_file():
        die("draft correction record missing: %s" % DRAFT)
    corr = json.loads(DRAFT.read_text(encoding="utf-8"))
    for key, want in (
        ("schema_version", "kot-correction/1"),
        ("experiment", "f1k"),
        ("seq", 4),
        ("supersedes_frozen_sha256", PRE_FROZEN),
        ("refrozen_sha256", POST_FROZEN),
    ):
        if corr.get(key) != want:
            die("draft correction %s != %r" % (key, want))
    # Rev2 blocker 4: FULL registry identity/account lint on the draft — the
    # same gate registry-check applies to registry/corrections/*/*.json — so an
    # invalid author or an account string can NEVER be copied into the registry.
    try:
        kc.check_identity_fields(corr)
        kc.require_no_account_strings(kc.canonical_bytes(corr), str(DRAFT))
    except kc.KotError as exc:
        die("draft correction fails registry identity/account lint: %s" % exc)

    # Rev2 blocker 2 / Rev3 blocker 2: ASM-2525 MUST be registered before the
    # index (the launch marker) is advanced, so a fully-applied index implies
    # the ASM is present. Registered = a JSONL ENTRY with id==ASM-2525, NOT a
    # raw substring (a foreign record quoting the string must not count).
    if not _asm_registered(ASSUMPTIONS, "ASM-2525"):
        die("no assumptions.jsonl entry with id==ASM-2525 — register the "
            "seq-4 re-freeze assumption (with this landing commit) BEFORE "
            "running the splice; the frozen-index is written last so a "
            "launchable state always implies the ASM is present")

    # deterministic splice + pinned post-hash
    new_rec = json.loads(raw.replace(OLD_BUILDER, NEW_BUILDER))
    got = kc.frozen_hash(new_rec)
    if got != POST_FROZEN:
        die("post-splice frozen hash %s != pinned expectation %s"
            % (got, POST_FROZEN))
    new_rec["frozen_sha256"] = POST_FROZEN

    # ---- transactional writes: record -> correction -> INDEX (last) ------
    # Rev3 blocker 3: rollback is INDEPENDENT per step, surfaces every failure,
    # and cleans a PARTIAL correction. The frozen-index is written last, so
    # until it flips to POST the state is non-launchable; on any failure we
    # restore record+index to pre-splice and remove ANY correction bytes that
    # reached disk (existence-based, not a post-copy flag), leaving the tree
    # fully pre-splice and safe to retry — or, if a rollback step itself fails,
    # STOP LOUDLY for hand inspection (never a silent half-state).
    record_backup = raw
    index_backup = iraw

    def _rollback():
        errs = []
        for label, path, content in (("record", RECORD, record_backup),
                                     ("index", INDEX, index_backup)):
            try:
                path.write_text(content, encoding="utf-8")
            except OSError as e:
                errs.append("%s restore FAILED: %s" % (label, e))
        # Existence-based: a create-then-fail leaves a partial correction that
        # MUST be removed regardless of how far the copy got.
        try:
            if CORRECTION.exists():
                CORRECTION.unlink()
        except OSError as e:
            errs.append("correction cleanup FAILED: %s" % e)
        return errs

    try:
        kc.write_canonical_json(RECORD, new_rec)          # 1. record
        CORRECTION.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(DRAFT, CORRECTION)                 # 2. correction
        idx["f1k"] = POST_FROZEN
        kc.write_canonical_json(INDEX, idx)                # 3. INDEX = marker
    except Exception as exc:  # noqa: BLE001 — rollback then fail-closed
        errs = _rollback()
        if errs:
            die("write failed (%s) AND rollback did NOT fully complete: %s — "
                "the tree may be inconsistent; INSPECT BY HAND and restore the "
                "pre-splice bytes before any retry" % (exc, "; ".join(errs)))
        die("write failed (%s); record+index restored to pre-splice and any "
            "correction removed — tree fully pre-splice, safe to retry" % exc)

    # ---- post-state verification from disk --------------------------------
    raw2 = RECORD.read_text(encoding="utf-8")
    rec2 = json.loads(raw2)
    assert raw2 == kc.canonical_dumps(rec2) + "\n"
    assert kc.frozen_hash(rec2) == POST_FROZEN == rec2["frozen_sha256"]
    assert raw2.count(NEW_BUILDER) == 2 and raw2.count(OLD_BUILDER) == 0
    assert json.loads(INDEX.read_text(encoding="utf-8"))["f1k"] == POST_FROZEN
    # Rev2 blocker 3: flag form + RETURN CODE + FULL hash bind.
    rc = subprocess.run(
        [sys.executable,
         str(REPO / "tools" / "registry" / "registry-check.py"),
         "--frozen-drift"],
        cwd=str(REPO), capture_output=True, text=True)
    if rc.returncode != 0:
        die("registry-check --frozen-drift exit %d after the splice — INSPECT "
            "BEFORE COMMITTING. tail:\n%s"
            % (rc.returncode, "\n".join(rc.stdout.splitlines()[-8:])))
    ok = any(line.strip().startswith("ok frozen-drift: f1k")
             and POST_FROZEN[:8] in line for line in rc.stdout.splitlines())
    if not ok:
        die("frozen-drift did not confirm f1k at %s… after the splice"
            % POST_FROZEN[:8])
    if json.loads(INDEX.read_text(encoding="utf-8")).get("f1k") != POST_FROZEN:
        die("frozen-index f1k != full %s after the splice" % POST_FROZEN)
    print("SPLICE OK: f1k re-frozen %s… -> %s… (generator %s… -> %s…); "
          "correction seq-4 installed; index advanced last; frozen-drift green"
          % (PRE_FROZEN[:8], POST_FROZEN[:8],
             OLD_BUILDER[:8], NEW_BUILDER[:8]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
