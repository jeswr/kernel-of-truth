#!/usr/bin/env bash
# run-codex-warm.sh -- context-CACHING codex runner for OVERFLOW design/interp/analysis work
# (the Fable-overflow lane). NOT for audits or independent reviews -- those MUST use the
# fresh/isolated run-review.sh so the auditor never inherits the run's context.
#
# Why: run-review.sh uses --ephemeral + a throwaway CODEX_HOME per call, so every codex run
# re-reads its whole context from scratch and burns plan usage. This runner instead keeps a
# PERSISTENT per-topic CODEX_HOME and RESUMES the topic's most recent session, so:
#   - files already read + prior reasoning stay in context (no re-reading),
#   - OpenAI's automatic prompt cache stays warm across calls on the same topic.
# Batch related questions onto ONE topic key; only start a --fresh topic when the subject changes.
#
# Never prints/commits secrets (auth.json chmod 600, copied into the topic home). Read-only sandbox.
# Usage: run-codex-warm.sh <topic-key> <brief-file> <out-dir> [--fresh]
#   <topic-key>  stable slug for the conversation to reuse (e.g. "ontology", "nsm-ufo")
#   --fresh      start a NEW conversation for this topic (ignore any prior session)
set -u
KEY="${1:-}"; BRIEF="${2:-}"; OUT_DIR="${3:-}"; MODE="${4:-}"
if [[ -z "$KEY" || -z "$BRIEF" || -z "$OUT_DIR" ]]; then
  echo "usage: $0 <topic-key> <brief-file> <out-dir> [--fresh]" >&2; exit 2
fi
[[ -f "$BRIEF" ]] || { echo "ERR: brief not found: $BRIEF" >&2; exit 2; }
mkdir -p "$OUT_DIR"

CODEX_PKG="@openai/codex@0.144.1"   # npx-pinned; must NOT touch the global 0.142.5
MODEL="gpt-5.6-sol"
EFFORT="high"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

[[ -f "$HOME/.codex/auth.json" ]] || { echo "ERR: $HOME/.codex/auth.json missing" >&2; exit 3; }
BASE="${CODEX_WARM_HOME_BASE:-$HOME/.codex-warm-homes}"
HOME_DIR="$BASE/topic.$KEY"
mkdir -p "$HOME_DIR"
cp "$HOME/.codex/auth.json" "$HOME_DIR/auth.json"; chmod 600 "$HOME_DIR/auth.json"
[[ -f "$HOME/.codex/config.toml" ]] && cp "$HOME/.codex/config.toml" "$HOME_DIR/config.toml"

# NOTE: 'codex exec resume' rejects the -s/-m/-c flags after the subcommand (arg-parse
# conflict, observed 2026-07-12), so session-RESUME is disabled. Caching still works:
# OpenAI auto-caches the shared system+repo prefix across burst-fired jobs (sparq's caching
# note) regardless of resume, and the persistent home keeps auth/config warm. Always fresh exec.
SUB=(exec)
echo "run-codex-warm: KEY=$KEY fresh exec in persistent home (prefix-cache via shared repo/prefix; resume disabled)" >&2

CODEX_HOME="$HOME_DIR" npx -y "$CODEX_PKG" "${SUB[@]}" \
  -m "$MODEL" \
  -c model_reasoning_effort="$EFFORT" \
  -s read-only \
  --skip-git-repo-check \
  --disable standalone_web_search \
  -C "$REPO" \
  --color never \
  --json \
  -o "$OUT_DIR/last-message.json" \
  - < "$BRIEF" \
  > "$OUT_DIR/events.jsonl" 2> "$OUT_DIR/stderr.log"
RC=$?
echo "run-codex-warm: exit=$RC (home persisted at $HOME_DIR for next resume)" >&2
exit $RC
