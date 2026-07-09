"""Ingest API clients for the Pillar-C lit-KB (N-C §4.1). Stdlib only.

Sources in priority order: OpenAlex (primary discovery/metadata), arXiv
(abstracts/full text; 1 req/3 s courtesy), Semantic Scholar Graph (citation
graph; free tier ~1 RPS — throttled in kb_common.http_get), Crossref (DOI
fallback). Keys come from the environment (source ~/.config/kot/lit-kb.env);
they are sent in headers/params and NEVER logged — kb_common error paths strip
query strings.
"""

import json
import os
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import kb_common as K  # noqa: E402

OPENALEX = "https://api.openalex.org"
S2 = "https://api.semanticscholar.org/graph/v1"
ARXIV = "https://export.arxiv.org/api/query"
MAILTO = "kot-lit-kb@invalid.example"  # etiquette param only; no real inbox is exposed

OPENALEX_SELECT = ",".join(
    [
        "id",
        "doi",
        "title",
        "display_name",
        "publication_year",
        "primary_location",
        "cited_by_count",
        "authorships",
        "abstract_inverted_index",
        "ids",
        "type",
    ]
)


def _openalex_url(path, params):
    p = dict(params)
    p["mailto"] = MAILTO
    key = K.api_keys()["openalex"]
    if key:
        p["api_key"] = key
    return "%s%s?%s" % (OPENALEX, path, urllib.parse.urlencode(p))


def _get_json(url, headers=None):
    data, _ = K.http_get(url, headers=headers)
    return json.loads(data.decode("utf-8"))


def invert_abstract(inv):
    """OpenAlex abstract_inverted_index -> plain text (None-safe)."""
    if not inv:
        return None
    pos = []
    for word, idxs in inv.items():
        for i in idxs:
            pos.append((i, word))
    pos.sort()
    return " ".join(w for _, w in pos) or None


def openalex_work_to_meta(w):
    """Normalise an OpenAlex work object into the queue-metadata shape."""
    ids = w.get("ids") or {}
    arxiv = None
    doi = (w.get("doi") or "").replace("https://doi.org/", "") or None
    if doi:
        m = re.match(r"^10\.48550/arxiv\.([0-9]{4}\.[0-9]{4,5})", doi.lower())
        if m:
            arxiv = m.group(1)
    loc = w.get("primary_location") or {}
    src = (loc.get("source") or {}).get("display_name")
    return {
        "title": w.get("title") or w.get("display_name") or "",
        "year": w.get("publication_year"),
        "venue": src,
        "doi": doi,
        "arxiv": arxiv,
        "openalex": (ids.get("openalex") or w.get("id") or "").rsplit("/", 1)[-1] or None,
        "s2": None,
        "abstract": invert_abstract(w.get("abstract_inverted_index")),
        "citation_count": {"value": w.get("cited_by_count", 0), "source": "openalex"},
        "authors": [
            (a.get("author") or {}).get("display_name")
            for a in (w.get("authorships") or [])[:12]
            if (a.get("author") or {}).get("display_name")
        ],
    }


def openalex_by_dois(dois, batch=40):
    """Batched DOI lookup via filter=doi:a|b|c. Yields work objects."""
    dois = [d for d in dois if d]
    for i in range(0, len(dois), batch):
        chunk = dois[i : i + batch]
        url = _openalex_url(
            "/works",
            {"filter": "doi:" + "|".join(chunk), "per-page": str(batch), "select": OPENALEX_SELECT},
        )
        for w in _get_json(url).get("results", []):
            yield w


def openalex_search(query, from_year=None, pages=2, per_page=50, sort="relevance_score:desc"):
    """Search discovery (N-C §4.2 `discover`). Yields work objects."""
    filters = ["type:article|preprint"]
    if from_year:
        filters.append("from_publication_date:%d-01-01" % from_year)
    for page in range(1, pages + 1):
        url = _openalex_url(
            "/works",
            {
                "search": query,
                "filter": ",".join(filters),
                "per-page": str(per_page),
                "page": str(page),
                "sort": sort,
                "select": OPENALEX_SELECT,
            },
        )
        results = _get_json(url).get("results", [])
        for w in results:
            yield w
        if len(results) < per_page:
            break


_ATOM = "{http://www.w3.org/2005/Atom}"
_ARXIV_NS = "{http://arxiv.org/schemas/atom}"


def arxiv_batch(ids, batch=100):
    """arXiv metadata by id_list (Atom). Yields normalised meta dicts."""
    ids = [i for i in ids if i]
    for i in range(0, len(ids), batch):
        chunk = ids[i : i + batch]
        url = "%s?%s" % (
            ARXIV,
            urllib.parse.urlencode({"id_list": ",".join(chunk), "max_results": str(len(chunk))}),
        )
        data, _ = K.http_get(url)
        root = ET.fromstring(data)
        for entry in root.findall(_ATOM + "entry"):
            raw_id = (entry.findtext(_ATOM + "id") or "").rsplit("/", 1)[-1]
            m = K.ARXIV_ID_RE.search(raw_id)
            if not m:
                continue  # arXiv returns a stub entry for unknown ids
            title = re.sub(r"\s+", " ", entry.findtext(_ATOM + "title") or "").strip()
            abstract = re.sub(r"\s+", " ", entry.findtext(_ATOM + "summary") or "").strip() or None
            published = entry.findtext(_ATOM + "published") or ""
            venue = entry.findtext(_ARXIV_NS + "journal_ref")
            yield {
                "title": title,
                "year": int(published[:4]) if published[:4].isdigit() else None,
                "venue": venue,
                "doi": entry.findtext(_ARXIV_NS + "doi"),
                "arxiv": m.group(1),
                "openalex": None,
                "s2": None,
                "abstract": abstract,
                "citation_count": None,
                "authors": [
                    a.findtext(_ATOM + "name")
                    for a in entry.findall(_ATOM + "author")[:12]
                    if a.findtext(_ATOM + "name")
                ],
            }


def arxiv_search(query, max_results=50, sort_by="relevance"):
    """arXiv full-text/abstract search (discovery side channel)."""
    url = "%s?%s" % (
        ARXIV,
        urllib.parse.urlencode(
            {"search_query": query, "max_results": str(max_results), "sortBy": sort_by}
        ),
    )
    data, _ = K.http_get(url)
    root = ET.fromstring(data)
    for entry in root.findall(_ATOM + "entry"):
        raw_id = (entry.findtext(_ATOM + "id") or "").rsplit("/", 1)[-1]
        m = K.ARXIV_ID_RE.search(raw_id)
        if not m:
            continue
        title = re.sub(r"\s+", " ", entry.findtext(_ATOM + "title") or "").strip()
        abstract = re.sub(r"\s+", " ", entry.findtext(_ATOM + "summary") or "").strip() or None
        published = entry.findtext(_ATOM + "published") or ""
        yield {
            "title": title,
            "year": int(published[:4]) if published[:4].isdigit() else None,
            "venue": entry.findtext(_ARXIV_NS + "journal_ref"),
            "doi": entry.findtext(_ARXIV_NS + "doi"),
            "arxiv": m.group(1),
            "openalex": None,
            "s2": None,
            "abstract": abstract,
            "citation_count": None,
            "authors": [],
        }


def _s2_headers():
    key = K.api_keys()["s2"]
    return {"x-api-key": key} if key else {}


S2_FIELDS = "title,year,venue,externalIds,citationCount,abstract,authors"


def s2_paper(paper_id, fields=S2_FIELDS):
    """paper_id: 'arXiv:2410.10450', 'DOI:10...', or an S2 sha."""
    url = "%s/paper/%s?%s" % (S2, urllib.parse.quote(paper_id), urllib.parse.urlencode({"fields": fields}))
    return _get_json(url, headers=_s2_headers())


def s2_neighbourhood(paper_id, direction="citations", limit=50):
    """Citation neighbourhood for `kb related`, cached under kb/graph/ by the CLI."""
    assert direction in ("citations", "references")
    url = "%s/paper/%s/%s?%s" % (
        S2,
        urllib.parse.quote(paper_id),
        direction,
        urllib.parse.urlencode({"fields": "title,year,venue,externalIds,citationCount", "limit": str(limit)}),
    )
    return _get_json(url, headers=_s2_headers())
