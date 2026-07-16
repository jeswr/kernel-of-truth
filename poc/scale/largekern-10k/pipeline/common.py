#!/usr/bin/env python3
"""common.py — shared constants, hashing conventions, and pinned values for the
WordNet-10k drafting pipeline MOCK build (spec: docs/next/design/
gpt56-draft-pipeline-large-kernel.md, revision r5; reviewed GO-TO-FREEZE).

MOCK-FIRST, $0: nothing in this package ever opens a network connection.
The real run happens only after a prereg-freeze, separately (spec §10.6 P7).

Hashing/serialization reuses tools/registry/kot_common (canonical JSON =
sorted keys, compact separators) — never re-typed here.

Byte-serialization conventions [STIPULATED ASM-2497, designer-20]: where the
spec writes sha256(a ‖ b ‖ ...) the pinned mechanical reading is
sha256(canonical_dumps([a, b, ...]) UTF-8 bytes) — one convention everywhere,
collision-safe (no separator ambiguity), reproducible from the committed code.

Owner pseudonyms: pipeline-code ASMs designer-20; pipeline operator runner-1
(kb-pipeline-runner) per spec §8. Stdlib only (Python 3.9).
"""

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG_ROOT = os.path.abspath(os.path.join(HERE, ".."))                 # poc/scale/largekern-10k
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "registry"))
from kot_common import canonical_dumps, sha256_hex, canonical_sha256  # noqa: E402,F401
sys.path.insert(0, os.path.join(REPO_ROOT, "poc", "plainv5"))         # P8 machinery (a4f65edd)

# ---------------------------------------------------------------- pinned frame
# spec §1 / ASM-2493 [MEASURED 2026-07-16] + ASM-2474 (builder contract).
FRAME_SHA256 = "777c000ce60d1a83e11e6dd59c8e61f332e8c9ca16e003530b91dae0fac033f3"
FRAME_COUNT = 110049
CENSUS_TOTAL = 117791          # data/lexical-wn31/manifest.json totals.synsets
SAMPLE_N = 10000               # spec §10.1 worklist
# spec §1: "Seed registered at prereg-freeze; a re-draw is a new experiment id."
# This is the PINNED MOCK seed (recorded in the sample manifest); the operative
# seed is re-registered verbatim-or-replaced at prereg-freeze.
# [STIPULATED ASM-2498, designer-20]
SAMPLE_SEED = "largekern10k-sample-mock-v1"

WN31_DIR = os.path.join(REPO_ROOT, "data", "lexical-wn31")
WN31_SHARDS = ["synsets-noun.jsonl", "synsets-verb.jsonl", "synsets-adj.jsonl", "synsets-adv.jsonl"]
ALIGNMENT_PATH = os.path.join(WN31_DIR, "alignment-kernel-v0.json")   # §9.3 frozen-overlap denylist

# ---------------------------------------------------------------- mock outputs
# MOCK store root. The REAL run's store is data/kernel-v1-draft/ (spec §6.1);
# the mock never squats that path [STIPULATED ASM-2496, designer-20].
OUT_DIR = os.path.join(PKG_ROOT, "out")
STORE_DIR = os.path.join(OUT_DIR, "kernel-v1-draft")                  # mock mirror of the real layout
LEDGER_PATH = os.path.join(STORE_DIR, "ledger.sqlite")
LEDGER_EXPORT = os.path.join(STORE_DIR, "draft-ledger.jsonl")         # passive export (§6.1)
SEAT_LEDGER = os.path.join(STORE_DIR, "seat-ledger.jsonl")            # kot-seat-ledger/1 (§9.1)
RECORDS_DIR = os.path.join(STORE_DIR, "records")
TRANSCRIPTS_DIR = os.path.join(STORE_DIR, "transcripts")
PROVIDER_DIR = os.path.join(OUT_DIR, "mock-provider")                 # mock Batch backend state

FAMILY_MAP = os.path.join(REPO_ROOT, "poc", "plainv5", "family-map.json")

# ---------------------------------------------------------------- model + gen
# Exact dated snapshot id (MOCK placeholder; the real id is pinned at P6
# preflight). Must resolve to family "openai" under the pinned map (§8).
MODEL_SNAPSHOT_ID = "gpt-5.6-sol-20260601"
GEN_SETTINGS = {                       # §10.1: max_output_tokens frozen; rest
    "max_output_tokens": 2048,         # chosen at micro-pilot from the pinned
    "reasoning_effort": "medium",      # candidate set, frozen at prereg. MOCK
    "verbosity": "medium",             # uses one candidate, marked pending-P3.
    "_mock_note": "reasoning_effort/verbosity are the MOCK's candidate-set pick; frozen only at prereg (spec §5.3)",
}

# ---------------------------------------------------------------- budget (§10.2)
BUDGET_CAP_USD = 500.00
RESERVE_PER_REQUEST_USD = 0.0625       # Batch worst case per request (ASM-2473)
MAX_JOB_REQUESTS = 4000                # §3/§10.1: 200 MB bound -> <= 4,000/job
R_REPAIR = 2                           # §10.1: repair limit R = 2
PROVIDER_RETRY_LIMIT = 3               # §10.4
KILL_LADDER = [                        # §10.2 (evaluated at settlement)
    {"atUSD": 50.0, "minAttempted": 500, "minKappa": 0.50, "minAcceptRunning": 0.40},
    {"atUSD": 250.0, "minAttemptedFrac": 0.45},
]

# §5.2 price table [LIT-BACKED per spec; MOCK settlement uses these REGISTERED
# figures, never mock inventions — F1-K round-6 ledger-scale-floor lesson].
PRICE_PER_MTOK = {
    "input": 5.00, "cached_read": 0.50, "cache_write": 6.25, "output": 30.00,
    "batch_multiplier": 0.5,
}

# ---------------------------------------------------------------- gates (§10.3)
ALPHA_FLOOR = 0.70          # accept-rate Wilson 95% LB
KAPPA_FLOOR = 0.70          # cache-read input-token fraction (Batch usage sums)
COST_CEILING = 0.05         # $c per accepted record
PROVIDER_FAILED_MAX_FRAC = 0.02
# §7.1 P4a launch bounds
P4A_MAX_FULL10K_SECONDS = 3600.0
P4A_MAX_RSS_BYTES = 1 << 30
VALIDATOR_SHARD_B = 1000

# ---------------------------------------------------------------- lint (§4.1)
GLOSS_MIN_WORDS = 15
GLOSS_MAX_WORDS = 100
GLOSS_MAX_TOKENS = 128      # MOCK proxy: whitespace tokens (pinned tokenizer
                            # lands at P6 preflight) [STIPULATED ASM-2496]
LEAKAGE_SHINGLE = 8         # 8-token overlap hard reject (§2.3)


class PipelineError(Exception):
    """Fail-closed error with a named ERR_* code (CLAUDE.md: no silent fallbacks)."""

    def __init__(self, code, msg):
        self.code = code
        super().__init__("%s %s" % (code, msg))


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def spec_hash_list(items):
    """The ASM-2497 reading of the spec's sha256(a ‖ b ‖ ...)."""
    return sha256_hex(canonical_dumps(list(items)).encode("utf-8"))


def version_hash(source_row_sha256, prompt_hash, cache_prefix_hash,
                 model_snapshot_id, gen_settings_hash, validator_hash, lint_hash):
    """§6.1: versionHash = sha256(sourceRowSha256 ‖ promptHash ‖ cachePrefixHash
    ‖ modelSnapshotId ‖ genSettingsHash ‖ validatorHash ‖ lintHash)."""
    return spec_hash_list([source_row_sha256, prompt_hash, cache_prefix_hash,
                           model_snapshot_id, gen_settings_hash, validator_hash, lint_hash])


def idempotency_key(vhash):
    """§6.1: idempotencyKey = "kv1d-" + versionHash[:24]."""
    return "kv1d-" + vhash[:24]


def job_key(wave, attempt, member_idempotency_keys):
    """§6 (r5): jobKey = "kv1d-job-" + sha256(wave ‖ attempt ‖ sorted member
    idempotencyKeys)[:24]. The (wave, attempt) discriminator is load-bearing:
    identical membership across waves/retries must yield DISTINCT tokens."""
    digest = spec_hash_list([int(wave), int(attempt), sorted(member_idempotency_keys)])
    return "kv1d-job-" + digest[:24]


def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, obj):
    d = os.path.dirname(os.path.abspath(path))
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, ensure_ascii=True)
        f.write("\n")
