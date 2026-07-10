#!/usr/bin/env bash
# codex-invoke.sh -- free-form, high-effort GPT-5.6-Sol review invocation helper.
#
# Fills the "external reviewer" role for the gpt56-review packet. This is the
# NON-schema-constrained, reasoning-effort=HIGH sibling of the pinned judge-1p
# recipe (data/d-adj-t-llmproxy/judge-1p-invocation.md sections 0 + 3), which
# runs effort=low, --json, --output-schema. Here we want DEPTH and free-form
# prose, so: no --output-schema, no --json (plain stdout), effort HIGH.
#
# ISOLATION (mode=isolated, VERIFIED 2026-07-10): the live f2b-transfer judge-1p
# run uses gpt-5.6-sol through the DEFAULT CODEX_HOME (~/.codex). This helper
# creates a FRESH per-invocation CODEX_HOME under $HOME, copies ONLY auth.json
# (+ config.toml if present) so auth/config carry over while session/rollout/
# memory state stays fully separate, and runs --ephemeral. It never reads,
# prints, or commits auth.json contents. It does NOT touch the global codex
# (must stay codex-cli 0.142.5); model access is via the npx pin @0.144.1.
#
# Usage:  codex-invoke.sh <prompt-file> <output-file>
#   <prompt-file>  UTF-8 review prompt (packet + reviewer framing), fed on stdin.
#   <output-file>  plain-text stdout (the free-form review) is written here.
#                  stderr is written next to it as <output-file>.err.
# Exit code is the codex exit code. FOREGROUND / blocking.

set -u

PROMPT_FILE="${1:-}"
OUT_FILE="${2:-}"
if [[ -z "$PROMPT_FILE" || -z "$OUT_FILE" ]]; then
  echo "usage: $0 <prompt-file> <output-file>" >&2
  exit 2
fi
if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "ERR: prompt file not found: $PROMPT_FILE" >&2
  exit 2
fi

# --- pins (must match the verified recipe) ---
CODEX_PKG="@openai/codex@0.144.1"   # npx-pinned; NOT the global 0.142.5
MODEL="gpt-5.6-sol"
EFFORT="high"                        # depth; judge-1p uses low

# --- isolated CODEX_HOME under $HOME (avoids the /tmp PATH-alias warning) ---
if [[ ! -f "$HOME/.codex/auth.json" ]]; then
  echo "ERR: $HOME/.codex/auth.json missing -- cannot carry auth into isolated home" >&2
  exit 3
fi
BASE="${CODEX_REVIEW_HOME_BASE:-$HOME/.codex-review-homes}"
mkdir -p "$BASE"
ISO_HOME="$(mktemp -d "$BASE/home.XXXXXX")"
WORKDIR="$(mktemp -d "$BASE/workdir.XXXXXX")"   # empty, out-of-repo, read-only sandbox root
cleanup() { rm -rf "$ISO_HOME" "$WORKDIR" 2>/dev/null; }
trap cleanup EXIT

# carry auth + (if present) config; auth stays 0600 and is never printed
cp "$HOME/.codex/auth.json" "$ISO_HOME/auth.json"
chmod 600 "$ISO_HOME/auth.json"
[[ -f "$HOME/.codex/config.toml" ]] && cp "$HOME/.codex/config.toml" "$ISO_HOME/config.toml"

# --- the verified free-form high-effort invocation (FOREGROUND) ---
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
  - < "$PROMPT_FILE" \
  > "$OUT_FILE" 2> "${OUT_FILE}.err"
RC=$?

echo "codex-invoke: exit=$RC model=$MODEL effort=$EFFORT pkg=$CODEX_PKG home(isolated)=$ISO_HOME" >&2
exit $RC
