#!/usr/bin/env bash
# Streams the official Stanford GloVe 6B archive (via the stanfordnlp
# HuggingFace mirror) and extracts ONLY what E2 needs, without ever writing
# the archive to disk (disk budget: 1 GB hard; this writes < 2 MB):
#
#   inputs/glove-slice-100d.txt   vectors for the 51 probe words (~65 KB)
#   inputs/glove-ranks-top100k.txt  "rank word" for the 100k most frequent
#                                   vocab entries (GloVe vocab is ordered by
#                                   corpus frequency; used as the frequency
#                                   proxy for the E2 random-word pools)
#   inputs/glove-slice-meta.json  provenance + found/missing bookkeeping
#
# Mechanics: glove.6B.zip's FIRST member is glove.6B.100d.txt (verified from
# the local file header); `funzip` decompresses only the first member from
# stdin, so curl streams ~170 MB and is SIGPIPE-terminated when funzip
# finishes — nothing else is downloaded, nothing large touches disk.
# NOTE (documented deviation from the "e.g. 50d" suggestion in the prep
# brief): 100d is used because it is the streamable first member; the
# word2vec-cosine baseline is dimension-agnostic.
#
# GloVe 6B: Pennington, Socher & Manning (2014), Wikipedia 2014 + Gigaword 5,
# 400k vocab, released under the Public Domain Dedication and License (PDDL).
# No pipefail: curl/funzip are EXPECTED to die of SIGPIPE (141) when awk has
# what it needs; awk's own exit status is checked via PIPESTATUS instead.
set -u

E2_DIR="$(cd "$(dirname "$0")/.." && pwd)"
INPUTS="$E2_DIR/inputs"
mkdir -p "$INPUTS"

URL="https://huggingface.co/stanfordnlp/glove/resolve/main/glove.6B.zip"
WORDS_FILE="$(mktemp)"
trap 'rm -f "$WORDS_FILE"' EXIT

node -e '
  const items = require(process.argv[1] + "/inputs/items.json");
  for (const it of items.items) console.log(it.word);
' "$E2_DIR" > "$WORDS_FILE" || { echo "run \`npm run items\` first (inputs/items.json missing)" >&2; exit 1; }

echo "streaming $URL (first member only; ~170 MB network, <2 MB disk)..." >&2

# curl exits 23 (write error) when funzip closes the pipe after member 1 — expected.
( curl -sL --retry 3 "$URL" || true ) | funzip 2>/dev/null | awk \
  -v wordfile="$WORDS_FILE" \
  -v slice_out="$INPUTS/glove-slice-100d.txt" \
  -v ranks_out="$INPUTS/glove-ranks-top100k.txt" \
  -v meta_out="$INPUTS/glove-slice-meta.json" '
  BEGIN {
    nwant = 0;
    while ((getline w < wordfile) > 0) { want[w] = 1; nwant++; }
    close(wordfile);
    found = 0;
  }
  {
    if (NR <= 100000) print NR, $1 > ranks_out;
    if ($1 in want) {
      print $0 > slice_out;
      rank[$1] = NR;
      found++;
      delete want[$1];
    }
    if (found == nwant && NR > 100000) exit 0;
  }
  END {
    printf "{\n  \"source\": \"stanfordnlp/glove glove.6B.zip, member glove.6B.100d.txt (streamed)\",\n" > meta_out;
    printf "  \"license\": \"PDDL (GloVe 6B)\",\n  \"linesScanned\": %d,\n  \"wordsRequested\": %d,\n  \"wordsFound\": %d,\n", NR, nwant, found > meta_out;
    printf "  \"ranks\": {" > meta_out;
    sep = "";
    for (w in rank) { printf "%s\n    \"%s\": %d", sep, w, rank[w] > meta_out; sep = ","; }
    printf "\n  },\n  \"missing\": [" > meta_out;
    sep = "";
    for (w in want) { printf "%s\"%s\"", sep, w > meta_out; sep = ", "; }
    printf "]\n}\n" > meta_out;
    if (length(want) > 0) {
      printf "MISSING from GloVe 400k vocab:" > "/dev/stderr";
      for (w in want) printf " %s", w > "/dev/stderr";
      printf "\n" > "/dev/stderr";
      exit 3;
    }
  }
'
rc=${PIPESTATUS[2]}
if [ "$rc" -ne 0 ]; then
  echo "fetch-glove-slice FAILED (awk rc=$rc)" >&2
  exit "$rc"
fi
# Validate: every requested word must be in the slice.
nwant=$(wc -l < "$WORDS_FILE")
ngot=$(wc -l < "$INPUTS/glove-slice-100d.txt")
if [ "$ngot" -ne "$nwant" ]; then
  echo "fetch-glove-slice FAILED: got $ngot vectors, wanted $nwant" >&2
  exit 4
fi
sort -o "$INPUTS/glove-slice-100d.txt" "$INPUTS/glove-slice-100d.txt"
echo "done:" >&2
wc -l "$INPUTS/glove-slice-100d.txt" "$INPUTS/glove-ranks-top100k.txt" >&2
