#!/usr/bin/env python3
"""SCALE-1 S1 bounded first-ingest (kernel machinery, NOT an experiment).

Off-box (Modal CPU) validation of the full pipeline for ONE non-biological
domain — Wikidata "position" (wd:Q4164871, WDQS-measured 103,707 P279-backbone
classes) — per docs/next/design/scale-s1-position-ingest-prereg.md:

  download (WDQS paged) -> filter (P279* subtree = class layer)
    -> type (data/onto-wikidata crosswalk: position -> object/role/anti-rigid)
    -> decontaminate (exact external-ID join vs the 207,733-cluster union index)
    -> emit (typed concept records to a Modal Volume + manifest w/ contentHash).

The box only orchestrates; all HTTP + processing runs in the container.

    # smoke (tiny slice, pennies):
    .venv/bin/modal run poc/modal/modal_scale_wikidata.py --limit-pages 1 --page-size 500
    # full domain:
    .venv/bin/modal run poc/modal/modal_scale_wikidata.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import modal

_HERE = Path(__file__).resolve().parent
try:
    REPO_ROOT = _HERE.parents[1]
except IndexError:
    REPO_ROOT = _HERE  # container: local paths never dereferenced there
INDEX_LOCAL = REPO_ROOT / "poc" / "scale" / "out" / "wikidata-position" / "union-extid-index.json"
REMOTE_INDEX = "/root/union-extid-index.json"

WDQS = "https://query.wikidata.org/sparql"
UA = "KoT-scale-census/0.1 (research; large-kernel domain-balance ingest)"

# Per-domain crosswalk terminal (from data/onto-wikidata/p31-p279-ufo-crosswalk.json).
# STIPULATED terminal, reported separately from the source-asserted P279 chain.
ROOT_UFO = {
    "Q4164871": ("position", "object", "role", "anti-rigid"),
    "Q42889":   ("vehicle", "object", "kind", "rigid"),
    "Q43229":   ("organization", "social-object", "kind", "rigid"),
    "Q28640":   ("occupation", "object", "role", "anti-rigid"),
}

app = modal.App("kot-scale-wikidata-position")
image = modal.Image.debian_slim(python_version="3.11").pip_install("requests==2.34.2")
if INDEX_LOCAL.exists():  # only on the box at image-definition; skipped on container re-import
    image = image.add_local_file(INDEX_LOCAL, REMOTE_INDEX)
vol = modal.Volume.from_name("kot-scale-wikidata", create_if_missing=True)


def _wdqs(query: str, tries: int = 4) -> list[dict]:
    import requests
    last = None
    for i in range(tries):
        try:
            r = requests.get(WDQS, params={"query": query, "format": "json"},
                             headers={"User-Agent": UA, "Accept": "application/sparql-results+json"},
                             timeout=90)
            if r.status_code == 200:
                return r.json()["results"]["bindings"]
            last = f"HTTP {r.status_code}"
        except Exception as e:  # noqa: BLE001
            last = str(e)[:120]
        time.sleep(2 + 3 * i)
    raise RuntimeError(f"WDQS failed after {tries} tries: {last}")


def _norm_wn(p8814: str) -> str:
    # Wikidata P8814 is '<offset>-<pos>' already (e.g. 02084071-n) -> matches index keys.
    return p8814.strip()


@app.function(image=image, cpu=2.0, volumes={"/vol": vol}, timeout=3600)
def ingest_domain(root_qid: str, cap: int = 0, limit_pages: int = 0, page_size: int = 20000) -> dict:
    root_label, cat, sort, rig = ROOT_UFO[root_qid]
    idx = json.loads(Path(REMOTE_INDEX).read_text())
    wn = set(idx["wordnet_p8814"]); chebi = set(idx["chebi_p686"])
    taxon = set(idx["ncbitaxon_p685"]); mondo = set(idx["mondo_p5270"])

    t0 = time.time()
    # ---- Phase 1: fetch the flat set of subtree QIDs (cheap; no label/optionals,
    # no ORDER BY over the closure). Pull the whole QID set in ONE query (each
    # counted domain's closure is <=1e5 rows, well under WDQS's row cap for a
    # 1-column projection). ----
    qids: list[str] = []
    binds = _wdqs(f"SELECT ?item WHERE {{ ?item wdt:P279* wd:{root_qid} }}")
    for b in binds:
        q = b["item"]["value"].rsplit("/", 1)[-1]
        if q != root_qid:
            qids.append(q)
    qids = sorted(set(qids))
    subtree_total = len(qids)
    # Deterministic, benchmark-blind cap: first N QIDs by ascending QID string.
    if cap and len(qids) > cap:
        qids = qids[:cap]
    if limit_pages:  # smoke override
        qids = qids[: limit_pages * page_size]

    # ---- Phase 2: fetch label + external IDs + P279/P31 parents in VALUES
    # batches (no transitive; fast, bounded). ----
    rows: dict[str, dict] = {q: {"id": f"urn:onto-wikidata:{q}", "qid": q, "label": "",
                                 "p279_parents": set(), "p31": set(), "external_ids": {}}
                             for q in qids}
    BATCH = 300
    pages = 0
    for i in range(0, len(qids), BATCH):
        chunk = qids[i:i + BATCH]
        values = " ".join(f"wd:{q}" for q in chunk)
        q = f"""SELECT ?item ?itemLabel ?wn ?chebi ?taxon ?mondo ?p279 ?p31 WHERE {{
  VALUES ?item {{ {values} }}
  OPTIONAL {{ ?item wdt:P8814 ?wn }}
  OPTIONAL {{ ?item wdt:P686 ?chebi }}
  OPTIONAL {{ ?item wdt:P685 ?taxon }}
  OPTIONAL {{ ?item wdt:P5270 ?mondo }}
  OPTIONAL {{ ?item wdt:P279 ?p279 }}
  OPTIONAL {{ ?item wdt:P31 ?p31 }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" }}
}}"""
        for b in _wdqs(q):
            qid = b["item"]["value"].rsplit("/", 1)[-1]
            rec = rows.get(qid)
            if rec is None:
                continue
            if not rec["label"] and "itemLabel" in b:
                rec["label"] = b["itemLabel"]["value"]
            for k, pk in (("wn", "P8814"), ("chebi", "P686"), ("taxon", "P685"), ("mondo", "P5270")):
                if k in b:
                    rec["external_ids"][pk] = b[k]["value"]
            if "p279" in b:
                rec["p279_parents"].add(b["p279"]["value"].rsplit("/", 1)[-1])
            if "p31" in b:
                rec["p31"].add(b["p31"]["value"].rsplit("/", 1)[-1])
        pages += 1
        time.sleep(0.2)

    # type + decontaminate
    ufo = {"denotation_level": "type", "ontic_category": cat,
           "sortality": sort, "rigidity": rig,
           "warrant": [f"crosswalk:wd:{root_qid} {root_label} -> {cat}/{sort}/{rig} [STIPULATED terminal]",
                       f"P279* wd:{root_qid} (source-asserted structural)"]}
    out_lines = []
    n_new = 0; n_merge = 0
    ext_cov = {"P8814": 0, "P686": 0, "P685": 0, "P5270": 0}
    leaves = 0
    for qid in sorted(rows):
        rec = rows[qid]
        eid = rec["external_ids"]
        for pk in ext_cov:
            if pk in eid:
                ext_cov[pk] += 1
        matched = None
        if "P8814" in eid and _norm_wn(eid["P8814"]) in wn:
            matched = ("P8814", eid["P8814"])
        elif "P686" in eid and eid["P686"] in chebi:
            matched = ("P686", eid["P686"])
        elif "P685" in eid and eid["P685"] in taxon:
            matched = ("P685", eid["P685"])
        elif "P5270" in eid and eid["P5270"] in mondo:
            matched = ("P5270", eid["P5270"])
        status = "crosswalk-merge" if matched else "new"
        if matched:
            n_merge += 1
        else:
            n_new += 1
        if not rec["p279_parents"]:
            leaves += 1
        out_lines.append(json.dumps({
            "schema": "kot-wikidata/1", "id": rec["id"], "qid": qid,
            "label": rec["label"], "p279_parents": sorted(rec["p279_parents"]),
            "p31": sorted(rec["p31"]), "external_ids": eid, "ckufo": ufo,
            "decontam": {"status": status, "matched_key": (matched[0] + ":" + matched[1]) if matched else None},
            "provenance": {"source": "Wikidata (CC0)", "root": f"wd:{root_qid} ({root_label})",
                           "via": "P279* subtree", "snapshot": "live WDQS 2026-07-13"},
        }, ensure_ascii=False))

    # contentHash over sorted (id, ufo, decontam-status)
    h = hashlib.sha256()
    for ln in out_lines:
        d = json.loads(ln)
        h.update((d["id"] + "|" + d["ckufo"]["ontic_category"] + "/" + d["ckufo"]["sortality"]
                  + "|" + d["decontam"]["status"] + "\n").encode())
    content_hash = h.hexdigest()

    Path(f"/vol/{root_label}").mkdir(parents=True, exist_ok=True)
    Path(f"/vol/{root_label}/concepts.jsonl").write_text("\n".join(out_lines) + "\n")
    vol.commit()

    manifest = {
        "artifact": f"scale-s1 Wikidata '{root_label}' domain ingest (kernel machinery)",
        "root": f"wd:{root_qid} ({root_label})", "date": "2026-07-13",
        "epistemic_status": "MEASURED live-WDQS ingest; typing terminal STIPULATED (crosswalk); decontam via exact external-ID join vs the union index. NO feasibility conclusion.",
        "subtree_total_before_cap": subtree_total, "cap": cap,
        "counts": {
            "total_typed_concepts": len(rows),
            "decontam_new_genuinely_novel": n_new,
            "decontam_crosswalk_merges": n_merge,
            "leaf_classes_no_outgoing_P279": leaves,
        },
        "ufo_distribution": {f"{cat}/{sort}/{rig} ({root_label} terminal)": len(rows)},
        "external_id_coverage": ext_cov,
        "wdqs_pages": pages, "page_size": page_size, "limit_pages": limit_pages,
        "wall_seconds": round(time.time() - t0, 1),
        "contentHash": content_hash,
        "full_chunk_location": f"Modal Volume kot-scale-wikidata:/{root_label}/concepts.jsonl (off-box)",
    }
    Path(f"/vol/{root_label}/manifest.json").write_text(json.dumps(manifest, indent=2))
    vol.commit()
    manifest["_sample"] = [json.loads(x) for x in out_lines[:100]]
    return manifest


@app.local_entrypoint()
def main(root_qid: str = "Q4164871", cap: int = 0, limit_pages: int = 0, page_size: int = 20000):
    root_label = ROOT_UFO[root_qid][0]
    m = ingest_domain.remote(root_qid=root_qid, cap=cap, limit_pages=limit_pages, page_size=page_size)
    sample = m.pop("_sample", [])
    out_dir = REPO_ROOT / "poc" / "scale" / "results" / f"wikidata-{root_label}"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "manifest.json").write_text(json.dumps(m, indent=2))
    with (out_dir / "sample.jsonl").open("w") as f:
        for r in sample:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("MANIFEST:", json.dumps(m, indent=2))
    print(f"wrote {out_dir}/manifest.json + sample.jsonl ({len(sample)} records)")
