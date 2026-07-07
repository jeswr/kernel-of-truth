#!/usr/bin/env bash
# E4 data-pipeline smoke (bead kernel-of-truth-73u): CPU end-to-end MECHANICS
# check of the emission-data builder — mock corpus -> REAL poc/e1 vocab
# builder (read-only) -> build_emission.py (--smoke subset) -> independent
# assertions (check_smoke.py). NEVER a result; data-side only (no model).
#
# Usage: [E4_WORK=...] [PYTHON=...] bash run_smoke.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
E4="$(dirname "$HERE")"
E1="$E4/../e1"
export E4_WORK="${E4_WORK:-/tmp/e4work-smoke}"
PYTHON="${PYTHON:-python3}"

mkdir -p "$E4_WORK"

# 1. Mock corpus (generic simple-English sentences; NO gloss text — glosses
#    must never enter the LM-corpus side, even in a smoke).
nice -n 10 "$PYTHON" - "$E4_WORK/corpus.txt" <<'EOF'
import sys
sents = []
subj = ["the little dog", "a happy child", "the old man", "mom", "tom", "the bird",
        "a small cat", "the teacher", "grandma", "the boy"]
verb = ["saw", "found", "made", "took", "gave", "liked", "helped", "wanted", "heard", "knew"]
obj = ["a big red ball", "the shiny stone", "some sweet cake", "a new toy", "the open door",
       "a warm blanket", "the tall tree", "some cold water", "a funny hat", "the green book"]
tail = ["in the park", "at home", "near the river", "after lunch", "one sunny day",
        "before bed", "with a smile", "very fast", "again and again", "for a while"]
for i in range(240):
    sents.append(f"{subj[i % 10]} {verb[(i // 10) % 10]} {obj[(i // 100) % 10]} {tail[i % 7]} .")
stories = []
for i in range(0, len(sents), 4):
    stories.append(" ".join(sents[i:i + 4]))
with open(sys.argv[1], "w") as f:
    f.write("\n<|endoftext|>\n".join(stories) + "\n")
print(f"mock corpus: {len(stories)} stories")
EOF

# 2. REAL e1 vocab builder on the mock corpus (poc/e1 is read-only; outputs
#    land in E4_WORK). Produces the schema-true vocab.json E4 extends.
nice -n 10 "$PYTHON" "$E1/pipeline/build_data.py" \
  --corpus "$E4_WORK/corpus.txt" --out "$E4_WORK/e1data" --seeds 0 --vocab-size 4000

# 3. E4 emission builder, smoke subset, 2 seeds.
nice -n 10 "$PYTHON" "$E4/pipeline/build_emission.py" \
  --e1-vocab "$E4_WORK/e1data/vocab.json" --out "$E4_WORK/e4data" \
  --seeds 0,1 --exposure-per-concept 2 --smoke 30

# 4. Independent assertions.
nice -n 10 "$PYTHON" "$HERE/check_smoke.py" "$E4_WORK/e4data" "$E4/inputs" "$E4/results"

echo "smoke work dir: $E4_WORK (delete when done: rm -rf $E4_WORK)"
