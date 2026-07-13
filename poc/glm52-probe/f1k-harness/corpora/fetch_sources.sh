#!/usr/bin/env bash
# fetch_sources.sh — stage the five pinned benchmark snapshots for
# build_corpora.py (OP-1). Revision-pinned URLs; sha256 verified here AND
# fail-closed again inside the builder. $0; public benchmark data only —
# no model, no tokenizer, no spend.
set -euo pipefail
DST=/tmp/f1k-src
mkdir -p "$DST"

fetch() { # name url sha256
  local out="$DST/$1.parquet"
  if [ ! -f "$out" ] || ! echo "$3  $out" | sha256sum -c --quiet 2>/dev/null; then
    curl -sL -o "$out" "$2"
  fi
  echo "$3  $out" | sha256sum -c
}

fetch mmlu \
  "https://huggingface.co/datasets/cais/mmlu/resolve/c30699e8356da336a370243923dbaf21066bb9fe/all/test-00000-of-00001.parquet" \
  74a41822ce7d3def56e1682f958469c04642a5336a5ce912fa375fdb90fb25d7
fetch arc-easy \
  "https://huggingface.co/datasets/allenai/ai2_arc/resolve/210d026faf9955653af8916fad021475a3f00453/ARC-Easy/test-00000-of-00001.parquet" \
  4160597d618ae851c7eb04e281574f3f654776216ac6b6641588d64527b47177
fetch arc-challenge \
  "https://huggingface.co/datasets/allenai/ai2_arc/resolve/210d026faf9955653af8916fad021475a3f00453/ARC-Challenge/test-00000-of-00001.parquet" \
  62f03257e737aed263f55c6abf87c7bb0028a44a6bdd2a26eb1279eb42c1d1e9
fetch openbookqa \
  "https://huggingface.co/datasets/allenai/openbookqa/resolve/388097ea7776314e93a529163e0fea805b8a6454/main/test-00000-of-00001.parquet" \
  cd5483e366daa230c1c87bbdc512d8b7229f14f6dd04d19fc8b1a3855aaaa8a3
fetch csqa \
  "https://huggingface.co/datasets/tau/commonsense_qa/resolve/94630fe30dad47192a8546eb75f094926d47e155/data/validation-00000-of-00001.parquet" \
  bdbd9bf9cc4d2349b24901038b2ab2f58e10e4e507ad2fd425dca55cd3cb6660

echo "sources staged under $DST (identical pinned copies also live in data/f1k-eval-v1/source/)"
