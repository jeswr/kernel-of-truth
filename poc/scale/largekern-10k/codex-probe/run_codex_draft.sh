#!/usr/bin/env bash
# run_codex_draft.sh -- probe harness: invoke codex (GPT-5.6-sol) as the DRAFTING
# transport for one WordNet-synset explication. Isolation mechanics copied EXACTLY
# from poc/gpt56-review/run-review.sh (fresh per-invocation CODEX_HOME with auth.json
# carried in; global codex-cli untouched; read-only; never prints/commits secrets).
#
# Difference vs the review runner: the working dir (-C) is a NEUTRAL EMPTY temp dir,
# not the repo, so the agent has nothing to explore -- the drafting prompt is fully
# self-contained. reasoning_effort matches the FROZEN pilot GEN_SETTINGS ("medium",
# common.py), so the measured wall-clock represents the real 10k pilot, not an
# inflated xhigh review setting.
#
# Usage: run_codex_draft.sh <prompt-file> <out-dir>
set -u
PROMPT="${1:-}"; OUT_DIR="${2:-}"
if [[ -z "$PROMPT" || -z "$OUT_DIR" ]]; then echo "usage: $0 <prompt-file> <out-dir>" >&2; exit 2; fi
[[ -f "$PROMPT" ]] || { echo "ERR: prompt not found: $PROMPT" >&2; exit 2; }
mkdir -p "$OUT_DIR"

CODEX_PKG="@openai/codex@0.144.1"          # npx-pinned; NOT the global 0.142.5
MODEL="gpt-5.6-sol"
EFFORT="${CODEX_DRAFT_EFFORT:-medium}"      # frozen GEN_SETTINGS.reasoning_effort (common.py)

if [[ ! -f "$HOME/.codex/auth.json" ]]; then
  echo "ERR: $HOME/.codex/auth.json missing" >&2; exit 3
fi
BASE="${CODEX_DRAFT_HOME_BASE:-$HOME/.codex-draft-homes}"
mkdir -p "$BASE"
ISO_HOME="$(mktemp -d "$BASE/home.XXXXXX")"
WORKDIR="$(mktemp -d "$BASE/work.XXXXXX")"   # neutral empty cwd: nothing to explore
cleanup() { rm -rf "$ISO_HOME" "$WORKDIR" 2>/dev/null; }
trap cleanup EXIT

cp "$HOME/.codex/auth.json" "$ISO_HOME/auth.json"; chmod 600 "$ISO_HOME/auth.json"
[[ -f "$HOME/.codex/config.toml" ]] && cp "$HOME/.codex/config.toml" "$ISO_HOME/config.toml"

CODEX_HOME="$ISO_HOME" npx -y "$CODEX_PKG" exec \
  -m "$MODEL" \
  -c model_reasoning_effort="$EFFORT" \
  -s read-only \
  --ignore-user-config \
  --skip-git-repo-check \
  --ephemeral \
  --disable memories \
  --disable standalone_web_search \
  -C "$WORKDIR" \
  --color never \
  --json \
  -o "$OUT_DIR/last-message.json" \
  - < "$PROMPT" \
  > "$OUT_DIR/events.jsonl" 2> "$OUT_DIR/stderr.log"
RC=$?
echo "run_codex_draft: exit=$RC effort=$EFFORT" >&2
exit $RC
