#!/usr/bin/env bash
# Re-fetch + verify the CLUTRR cache (the raw data is gitignored; this script +
# manifest.json are the committed, sha256-pinned re-fetch record). CC-BY-NC 4.0
# (non-commercial; attribute Sinha et al., EMNLP 2019, arXiv:1908.06177).
#
#   bash data/clutrr-cache/fetch.sh          # clone generator + download release
#   bash data/clutrr-cache/fetch.sh --verify # re-check shas + the k=2 slice counts
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

GEN_URL="https://github.com/facebookresearch/clutrr"
GEN_COMMIT="d045fae289d3746503677ceed7631c999202501e"
GDRIVE_ID="1SEq_e1IVCDDzsBIBhoUQ5pOVH5kxRoZF"
ZIP="clutrr-emnlp-release.zip"
ZIP_SHA256="b4029f68e555ba89dd5836d5f1d9049ca97fc54ed71ed880a5f5351f6c40228e"

if [[ "${1:-}" != "--verify" ]]; then
  [[ -d clutrr ]] || git clone "$GEN_URL" clutrr
  ( cd clutrr && git fetch --depth 50 origin && git checkout "$GEN_COMMIT" 2>/dev/null || true )
  [[ -f "$ZIP" ]] || curl -sL "https://drive.google.com/uc?export=download&id=${GDRIVE_ID}" -o "$ZIP"
fi

echo "== sha256 check =="
echo "${ZIP_SHA256}  ${ZIP}" | sha256sum -c -

echo "== k=2 up-edge grandparent slice (data_089907f8, clean Task 1) =="
python3 - <<'PY'
import zipfile, io, csv, collections
outer = zipfile.ZipFile("clutrr-emnlp-release.zip")
inner = zipfile.ZipFile(io.BytesIO(outer.read("data_emnlp_final/data_089907f8.zip")))
up = {"mother", "father"}
for fn in ("1.2,1.3_train.csv", "1.2_test.csv"):
    rows = list(csv.DictReader(io.StringIO(inner.read(fn).decode(errors="replace"))))
    fc = collections.Counter()
    n = 0
    for r in rows:
        parts = [p for p in r.get("f_comb", "").split("-") if p]
        if len(parts) == 2 and set(parts) <= up and r.get("target") in ("grandmother", "grandfather"):
            fc[r["f_comb"] + "->" + r["target"]] += 1
            n += 1
    print(f"  {fn}: {n} up-edge grandparent k=2 items  {dict(fc)}")
print("  EXPECT 1.2,1.3_train.csv -> 332 (83 x4); 1.2_test.csv -> 0 (holdout split)")
PY
echo "OK"
