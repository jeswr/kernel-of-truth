#!/usr/bin/env bash
# LNT-E0 clean-human corpus prep — renders locally installed man pages
# (human-authored precise technical documentation) to plain text, for the
# false-alarm-floor slice (N-PL §5 LNT-E0(ii)).
#
# Corpus choice is STIPULATED for this Tier-0 feasibility run (see README):
# N-PL specifies the CLASS ("clean, human-authored precise text — good
# technical documentation"); these are the canonical human-authored technical
# documents available on this box. They are OFF the covered TinyStories
# domain — fine for the coverage-INDEPENDENT V/A false-alarm floor (U is
# informational and never counted as an alarm in mode P).
#
# Output: corpora/clean-human/<page>.txt (committed; sha256s recorded by the
# harness). Rendering pinned: MANWIDTH=80, col -bx (backspaces stripped).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p corpora/clean-human
for page in bash grep tar; do
  MANWIDTH=80 man -P cat "$page" | col -bx > "corpora/clean-human/${page}.txt"
  echo "$(sha256sum "corpora/clean-human/${page}.txt")"
done
