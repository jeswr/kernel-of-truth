#!/usr/bin/env bash
# run-skeptic.sh -- independent-skeptic pre-freeze re-attack invocation.
#
# Adapts the pinned judges-invocation.md sec4.1 codex recipe (isolated
# CODEX_HOME, npx-pinned codex-cli 0.144.1, gpt-5.6-sol, --ignore-user-config,
# read-only sandbox) to an AUDIT rather than a blind judge call:
#   - reasoning effort HIGH (not low) -- this is depth review, not a fast
#     single-word label;
#   - NO --output-schema / --json -- free-form adversarial prose, not a
#     schema-constrained yes/no/cannot-say answer;
#   - -C points at the REAL repo root (not an empty out-of-repo workdir) --
#     Codex is explicitly tasked to read the design doc / registry / scorer
#     files itself; no blinding constraint applies to an audit.
# Isolation is otherwise identical to poc/gpt56-review/codex-invoke.sh: a
# fresh per-invocation CODEX_HOME under $HOME carrying ONLY auth.json (+
# config.toml if present), --ephemeral, memories/web-search disabled. Never
# touches the global codex-cli (must stay 0.142.5); never prints/commits
# auth.json. FOREGROUND / blocking; exit code is the codex exit code.
#
# Usage: run-skeptic.sh <prompt-file> <repo-root> <output-file>

set -u

PROMPT_FILE="${1:-}"
REPO="${2:-}"
OUT_FILE="${3:-}"
if [[ -z "$PROMPT_FILE" || -z "$REPO" || -z "$OUT_FILE" ]]; then
  echo "usage: $0 <prompt-file> <repo-root> <output-file>" >&2
  exit 2
fi
if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "ERR: prompt file not found: $PROMPT_FILE" >&2
  exit 2
fi
if [[ ! -d "$REPO" ]]; then
  echo "ERR: repo root not found: $REPO" >&2
  exit 2
fi

# --- pins ---
CODEX_PKG="@openai/codex@0.144.1"   # npx-pinned; NOT the global 0.142.5
MODEL="gpt-5.6-sol"
EFFORT="high"

# --- isolated CODEX_HOME under $HOME ---
if [[ ! -f "$HOME/.codex/auth.json" ]]; then
  echo "ERR: $HOME/.codex/auth.json missing -- cannot carry auth into isolated home" >&2
  exit 3
fi
BASE="${CODEX_SKEPTIC_HOME_BASE:-$HOME/.codex-skeptic-homes}"
mkdir -p "$BASE"
ISO_HOME="$(mktemp -d "$BASE/home.XXXXXX")"
cleanup() { rm -rf "$ISO_HOME" 2>/dev/null; }
trap cleanup EXIT

cp "$HOME/.codex/auth.json" "$ISO_HOME/auth.json"
chmod 600 "$ISO_HOME/auth.json"
[[ -f "$HOME/.codex/config.toml" ]] && cp "$HOME/.codex/config.toml" "$ISO_HOME/config.toml"

echo "run-skeptic: preflight -- npx pinned version check" >&2
NPX_VER="$(npx -y "$CODEX_PKG" --version 2>&1)"
echo "run-skeptic: npx pinned version: $NPX_VER" >&2
GLOBAL_VER_BEFORE="$(codex --version 2>&1 || true)"
echo "run-skeptic: global codex version (must stay untouched): $GLOBAL_VER_BEFORE" >&2

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
  - < "$PROMPT_FILE" \
  > "$OUT_FILE" 2> "${OUT_FILE}.err"
RC=$?

GLOBAL_VER_AFTER="$(codex --version 2>&1 || true)"
echo "run-skeptic: exit=$RC model=$MODEL effort=$EFFORT pkg=$CODEX_PKG home(isolated)=$ISO_HOME" >&2
echo "run-skeptic: global codex version after (must match before): $GLOBAL_VER_AFTER" >&2
if [[ "$GLOBAL_VER_BEFORE" != "$GLOBAL_VER_AFTER" ]]; then
  echo "run-skeptic: WARNING -- global codex version CHANGED ($GLOBAL_VER_BEFORE -> $GLOBAL_VER_AFTER)" >&2
fi
exit $RC
