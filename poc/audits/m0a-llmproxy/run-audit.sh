#!/usr/bin/env bash
# run-audit.sh -- GATE-A cross-vendor Codex audit invocation for m0a-llmproxy.
#
# Pinned recipe reused EXACTLY from poc/truthstyle-2x2/judges-invocation.md
# section 4.1 (the codex-judge invocation form), adapted for a full-repo
# read-only AUDIT call (schema-constrained, high effort) per the truthstyle-2x2
# Gate-A audit precedent (registry/audits/truthstyle-2x2/1-gate-a-codex.json
# auditor_tooling: codex-cli 0.144.1 via isolated CODEX_HOME, gpt-5.6-sol,
# reasoning high, sandbox read-only) and the isolation mechanics of
# poc/gpt56-review/codex-invoke.sh (verified 2026-07-10): a FRESH per-invocation
# CODEX_HOME under $HOME, auth.json (+ config.toml if present) copied in so
# subscription auth carries over while session/rollout/memory state stays
# fully separate. Never touches or upgrades the GLOBAL codex-cli (must remain
# 0.142.5). Never prints/commits secrets. FOREGROUND / blocking.
#
# Usage: run-audit.sh <brief-file> <schema-file> <out-dir>

set -u

BRIEF="${1:-}"
SCHEMA="${2:-}"
OUT_DIR="${3:-}"
if [[ -z "$BRIEF" || -z "$SCHEMA" || -z "$OUT_DIR" ]]; then
  echo "usage: $0 <brief-file> <schema-file> <out-dir>" >&2
  exit 2
fi
[[ -f "$BRIEF" ]] || { echo "ERR: brief not found: $BRIEF" >&2; exit 2; }
[[ -f "$SCHEMA" ]] || { echo "ERR: schema not found: $SCHEMA" >&2; exit 2; }
mkdir -p "$OUT_DIR"

CODEX_PKG="@openai/codex@0.144.1"   # npx-pinned; NOT the global 0.142.5
MODEL="gpt-5.6-sol"
EFFORT="high"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

# --- isolated, auto-cleaned CODEX_HOME under $HOME ---
if [[ ! -f "$HOME/.codex/auth.json" ]]; then
  echo "ERR: $HOME/.codex/auth.json missing -- cannot carry auth into isolated home" >&2
  exit 3
fi
BASE="${CODEX_AUDIT_HOME_BASE:-$HOME/.codex-audit-homes}"
mkdir -p "$BASE"
ISO_HOME="$(mktemp -d "$BASE/home.XXXXXX")"
cleanup() { rm -rf "$ISO_HOME" 2>/dev/null; }
trap cleanup EXIT

cp "$HOME/.codex/auth.json" "$ISO_HOME/auth.json"
chmod 600 "$ISO_HOME/auth.json"
[[ -f "$HOME/.codex/config.toml" ]] && cp "$HOME/.codex/config.toml" "$ISO_HOME/config.toml"

echo "run-audit: isolated CODEX_HOME=$ISO_HOME model=$MODEL effort=$EFFORT pkg=$CODEX_PKG repo=$REPO" >&2
echo "run-audit: global codex version banner (must remain untouched):" >&2
codex --version >&2 2>&1 || true

CODEX_HOME="$ISO_HOME" npx -y "$CODEX_PKG" exec \
  -m "$MODEL" \
  -c model_reasoning_effort="$EFFORT" \
  -s read-only \
  --ignore-user-config \
  --skip-git-repo-check \
  --ephemeral \
  --disable memories \
  --disable standalone_web_search \
  -C "$REPO" \
  --color never \
  --json \
  --output-schema "$SCHEMA" \
  -o "$OUT_DIR/last-message.json" \
  - < "$BRIEF" \
  > "$OUT_DIR/events.jsonl" 2> "$OUT_DIR/stderr.log"
RC=$?

echo "run-audit: exit=$RC" >&2
echo "run-audit: global codex version banner AFTER (must be unchanged):" >&2
codex --version >&2 2>&1 || true
exit $RC
