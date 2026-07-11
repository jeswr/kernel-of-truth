#!/usr/bin/env bash
# run-p3-review.sh -- GPT-5.6 (codex) design review of the Programme-3
# neurosymbolic-architecture design doc. Free-text review (NO output schema).
#
# Isolation mechanics reused EXACTLY from poc/audits/m0a-llmproxy/run-audit.sh:
# a FRESH per-invocation CODEX_HOME under $HOME with auth.json (+config.toml)
# copied in so subscription auth carries over while session/memory state stays
# separate. Never touches or upgrades the GLOBAL codex-cli (must stay 0.142.5).
# Never prints/commits secrets. Read-only sandbox. FOREGROUND / blocking.
#
# Usage: run-p3-review.sh <brief-file> <out-dir>
set -u
BRIEF="${1:-}"
OUT_DIR="${2:-}"
if [[ -z "$BRIEF" || -z "$OUT_DIR" ]]; then
  echo "usage: $0 <brief-file> <out-dir>" >&2; exit 2
fi
[[ -f "$BRIEF" ]] || { echo "ERR: brief not found: $BRIEF" >&2; exit 2; }
mkdir -p "$OUT_DIR"

CODEX_PKG="@openai/codex@0.144.1"   # npx-pinned; NOT the global 0.142.5
MODEL="gpt-5.6-sol"
EFFORT="high"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [[ ! -f "$HOME/.codex/auth.json" ]]; then
  echo "ERR: $HOME/.codex/auth.json missing -- cannot carry auth into isolated home" >&2; exit 3
fi
BASE="${CODEX_REVIEW_HOME_BASE:-$HOME/.codex-review-homes}"
mkdir -p "$BASE"
ISO_HOME="$(mktemp -d "$BASE/home.XXXXXX")"
cleanup() { rm -rf "$ISO_HOME" 2>/dev/null; }
trap cleanup EXIT

cp "$HOME/.codex/auth.json" "$ISO_HOME/auth.json"
chmod 600 "$ISO_HOME/auth.json"
[[ -f "$HOME/.codex/config.toml" ]] && cp "$HOME/.codex/config.toml" "$ISO_HOME/config.toml"

echo "run-p3-review: isolated CODEX_HOME=$ISO_HOME model=$MODEL effort=$EFFORT pkg=$CODEX_PKG repo=$REPO" >&2
echo "run-p3-review: global codex version banner (must remain untouched):" >&2
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
  -o "$OUT_DIR/last-message.json" \
  - < "$BRIEF" \
  > "$OUT_DIR/events.jsonl" 2> "$OUT_DIR/stderr.log"
RC=$?
echo "run-p3-review: exit=$RC" >&2
echo "run-p3-review: global codex version banner AFTER (must be unchanged):" >&2
codex --version >&2 2>&1 || true
exit $RC
