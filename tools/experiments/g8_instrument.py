#!/usr/bin/env python3
"""g8_instrument — Lean-minting viability instrument (HS8 / NF3; frozen record
registry/experiments/g8.json; pinned analysis analysis/g8.py).

RAW OUTPUT ONLY (P2 §2.4): every scoring mode emits the 8-count metrics block
the frozen analysis contract consumes; it renders NO verdict, computes NO
derived statistic (no rates, no Wilson bounds — those are analysis/g8.py's),
and knows nothing about the pre-registered 1%/80% gates.

The four instrument legs (design docs: design-dl-from-nsm-and-lean-reconstruction.md
§5.3, design-math-sector.md §3, design-lean-route.md §2; machinery in
tools/experiments/g8_fragment.py):

  FRAGMENT GATE   in-fragment := forward map F succeeds on the declaration's
                  statement at the doc-gen4 signature layer.
  FORWARD MAP F   signaturePretty -> canonical pm-ast/1 (de Bruijn, closed
                  grammar, caps, sort-check, vacuous-binder rejection).
  LLM LOCALE      the 39 math-v0 concepts rendered notation-neutrally; an LLM
                  proposes <=5 Mathlib names per target; every candidate is
                  F-verified (canonical-content equality) — the LLM can fail
                  to find, it cannot silently mislocate (§5.3 step 3).
  ROUND-TRIP      F(B(K)) = K through the production renderer+parser, over
                  every minted in-fragment statement + all 33 probe statements.

Modes
  --selftest                      hand-computed parser/probe/renderer checks ($0)
  --emit-prompts --out P          deterministic 39-target prompt pack (JSONL);
                                  prints {"pack_sha256": ...}
  --gate --sample P [--details D] fragment gate only; counts JSON on stdout
  --run --sample P --raw P --candidates P[,P...] [--details D]
                                  full metrics block on stdout (the 8 contract
                                  keys + count-only breakdowns)
  --call-llm --prompts P --out P --base-url U --model M [--key-env VAR]
                                  OpenAI-compatible chat call, temperature 0;
                                  the runner's helper — never run at design time
  --fetch-candidates --raw P --out DIR [--site U] [--index P]
                                  final-run helper: resolve candidate names via
                                  the doc-gen4 index + module pages into a local
                                  archive (network; archives bytes + fetch log;
                                  fails closed on cross-module commit mismatch)
  --mock [--workdir D]            $0 offline end-to-end on SYNTHETIC fixtures
                                  (never touches data/mathlib-1000-sample), then
                                  pipes the metrics through analysis/g8.py and
                                  asserts the frozen output contract

BLINDING: the real d-ml sample (data/mathlib-1000-sample/records.jsonl) is
never a default path — every mode takes explicit --sample/--candidates, and
--mock generates its own fixture corpus. Pre-freeze/pre-run iteration touches
fixtures and the 70-record math-lean-sample REFERENCE corpus only (that corpus
is pinned in the g8 record as the extractor's reference, not the sample).

Verification-mode split (pre-declared; per-mode counts reported):
  statement mode (30 targets, 33 statements) — genuine content verification:
      candidate verified iff F(candidate statement) lands in the target's
      admissible set {canonical, top-level eq/iff operand swap}; a target is
      located iff EVERY probe statement is covered by some candidate.
  anchor mode (9 Primitive targets) — WEAKER, instrument-authored: candidate
      verified iff it equals the pinned Lean face name (PRIM_ANCHORS). This is
      a bridge-consistency check against F's own face table, not independent
      content proof (the oracle-leakage caveat is pre-declared, not hidden).

STIPULATED assumptions this instrument rests on (to be REGISTERED by the
coordinator; this file never writes registry/assumptions.jsonl):
  * signature-layer-F: F is defined on statement-bearing kinds only; def-kind
    bodies are invisible at the doc-gen4 layer, so def-kinds count OUT of the
    fragment (direction: undercounts n_in_fragment; the ntp-toolkit route is
    the resolution path).
  * orientation-swap: location verification admits the top-level eq/iff
    operand swap and no other equivalence (Mathlib characterisation lemmas
    choose orientation by authorial convention; both orientations derive
    deterministically from the same math-v0 record).
  * primitive-anchor: the 9 Primitive targets verify against the pinned
    anchor table (weaker than content equality; per-mode counts reported so
    the location endpoint is auditable by mode).
  * no-defeq-aliasing: `n + 1` is add(n, one), never succ n; pretty-printer
    output that renders succ as `+ 1` therefore misses — conservative
    (undercount) for both the gate and the locale.

House rules: stdlib only; fail closed with named reasons; deterministic
(seed-free — the only nondeterminism in the whole experiment is the LLM call,
which is quarantined in --call-llm and verified by F afterwards); API keys are
read from the environment and never printed or written.
"""

import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import g8_fragment as F  # noqa: E402

RAW_SCHEMA = "g8-locate-raw/1"
PACK_SCHEMA = "g8-locate-pack/1"
DOC_SITE = "https://leanprover-community.github.io/mathlib4_docs/"
MAX_CANDIDATES = 5


def fail(code, msg):
    print("%s: %s" % (code, msg), file=sys.stderr)
    sys.exit(1)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---------------------------------------------------------------- prompt pack

_STMT_PROMPT = (
    "You are locating declarations in Mathlib 4 (the Lean 4 mathematics "
    "library).\nThe formal statement(s) below characterise one concept over "
    "the natural numbers, written in a notation-neutral form (de Bruijn-free "
    "variable names x0, x1, ...; concept names are internal slugs, not Lean "
    "names).\n\n%s\n\nTask: propose up to 5 fully-qualified Lean 4 / Mathlib "
    "declaration names (e.g. Nat.add_zero) whose stated proposition exactly "
    "expresses one of the statements above, up to variable names and "
    "notation. If several statements are listed, try to cover every one of "
    "them within your 5 names. Exact formulation matters: an iff is not an "
    "implication, argument order matters.\n"
    'Reply with ONLY a JSON object: {"candidates": ["Name1", "Name2", ...]}'
)

_ANCHOR_PROMPT = (
    "You are locating declarations in Lean 4 core / Mathlib 4.\nThe concept "
    "is a basis primitive of a two-sorted Peano-arithmetic formalism over "
    "the natural numbers: %r (%s).\n\nTask: propose up to 5 fully-qualified "
    "Lean 4 declaration names for the canonical constant this primitive "
    "corresponds to (e.g. a structure, function, or relation name — not a "
    "lemma about it).\n"
    'Reply with ONLY a JSON object: {"candidates": ["Name1", "Name2", ...]}'
)


def build_prompt_pack(root):
    concepts = F.load_math_v0(root)
    probes = F.build_probes(concepts)
    lines = [json.dumps({"schema": PACK_SCHEMA, "n_targets": len(probes)},
                        sort_keys=True)]
    for p in probes:
        if p["mode"] == "statement":
            stmts = "\n".join("Statement %d: %s" % (i + 1, F.render_neutral(s))
                              for i, s in enumerate(p["statements"]))
            prompt = _STMT_PROMPT % stmts
        else:
            rec = concepts[p["urn"]]
            prompt = _ANCHOR_PROMPT % (p["urn"].split(":")[-1], rec.get("label", ""))
        lines.append(json.dumps({"target": p["urn"], "mode": p["mode"],
                                 "n_statements": len(p["statements"]),
                                 "prompt": prompt}, sort_keys=True))
    blob = "\n".join(lines) + "\n"
    return blob, hashlib.sha256(blob.encode("utf-8")).hexdigest(), probes, concepts


# ---------------------------------------------------------------- LLM raw handling

def read_raws(path):
    with open(path, "r", encoding="utf-8") as f:
        rows = [json.loads(l) for l in f if l.strip()]
    if not rows or rows[0].get("schema") != RAW_SCHEMA:
        fail("ERR_G8_RAW", "missing/wrong raw header schema (want %s)" % RAW_SCHEMA)
    return rows[0], rows[1:]


_NAME_RE = re.compile(r"^[A-Za-z_Ͱ-Ͽ][\w.'Ͱ-Ͽℕ]*$")


def extract_candidates(output_text):
    """Parse the LLM reply. Returns (candidates<=5, n_dropped_over_cap) or
    None on extraction failure (instrument event, never a hypothesis event)."""
    if not isinstance(output_text, str):
        return None
    start = output_text.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(output_text)):
        c = output_text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                try:
                    obj = json.loads(output_text[start:i + 1])
                except ValueError:
                    return None
                cands = obj.get("candidates")
                if not isinstance(cands, list):
                    return None
                clean = []
                for c2 in cands:
                    if isinstance(c2, str):
                        c2 = c2.strip().strip("`").strip()
                        if _NAME_RE.match(c2):
                            clean.append(c2)
                return clean[:MAX_CANDIDATES], max(0, len(clean) - MAX_CANDIDATES)
    return None


# ---------------------------------------------------------------- candidate resolution

def load_archives(paths):
    """name -> signaturePretty from one or more lean-ref-style JSONL files
    (first hit wins, in the given path order)."""
    table = {}
    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                name = rec.get("name")
                sig = rec.get("signaturePretty")
                if name and sig and name not in table:
                    table[name] = sig
    return table


# ---------------------------------------------------------------- gate + run

def run_gate(sample_path, concepts, details_path=None):
    counts = {"n_mathlib_decls": 0, "n_in_fragment": 0}
    reasons = {}
    mints = []  # (name, statement)
    internal = 0
    det = io.StringIO()
    with open(sample_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            counts["n_mathlib_decls"] += 1
            try:
                ok, res = F.gate_record(rec, concepts)
            except Exception as e:  # instrument failure, not a rejection
                internal += 1
                det.write(json.dumps({"name": rec.get("name"),
                                      "internal_error": type(e).__name__}) + "\n")
                continue
            if ok:
                counts["n_in_fragment"] += 1
                mints.append((res["name"], res["statement"]))
                det.write(json.dumps({"name": res["name"], "in_fragment": True,
                                      "content_sha256": res["sha"]},
                                     sort_keys=True) + "\n")
            else:
                reasons[res] = reasons.get(res, 0) + 1
                det.write(json.dumps({"name": rec.get("name"),
                                      "in_fragment": False, "reason": res},
                                     sort_keys=True) + "\n")
    if internal:
        fail("ERR_G8_INTERNAL",
             "%d internal parser errors — instrument refuses partial counts"
             % internal)
    if details_path:
        with open(details_path, "w", encoding="utf-8") as f:
            f.write(det.getvalue())
    return counts, reasons, mints


def score_location(probes, header, raws, archive, pack_sha, concepts):
    if header.get("pack_sha256") != pack_sha:
        fail("ERR_G8_PACK", "raw header pack_sha256 %r != emitted pack %s"
             % (header.get("pack_sha256"), pack_sha))
    by_target = {}
    for r in raws:
        by_target[r.get("target")] = r.get("output_text")
    n_top5 = n_cand = n_ver = 0
    n_extract_fail = n_unresolved = n_dropped = n_rejected = 0
    located_by_mode = {"anchor": 0, "statement": 0}
    targets_by_mode = {"anchor": 0, "statement": 0}
    detail = []
    for p in probes:
        targets_by_mode[p["mode"]] += 1
        ext = extract_candidates(by_target.get(p["urn"]))
        if ext is None:
            n_extract_fail += 1
            detail.append({"target": p["urn"], "located": False,
                           "extraction_failure": True})
            continue
        cands, dropped = ext
        n_dropped += dropped
        n_cand += len(cands)
        covered = set()
        verified_names = []
        for c in cands:
            if p["mode"] == "anchor":
                if c in p["anchors"]:
                    n_ver += 1
                    verified_names.append(c)
                    covered.add(0)
                continue
            sig = archive.get(c)
            if sig is None:
                n_unresolved += 1
                continue
            try:
                _, stmt = F.lean_statement_to_pm(sig, concepts)
            except F.Reject:
                n_rejected += 1
                continue
            sha = F.content_sha(stmt)
            hit = False
            for i, adm in enumerate(p["admissible"]):
                if sha in adm:
                    covered.add(i)
                    hit = True
            if hit:
                n_ver += 1
                verified_names.append(c)
            else:
                n_rejected += 1
        need = set(range(len(p["statements"]))) if p["mode"] == "statement" else {0}
        located = need.issubset(covered)
        if located:
            n_top5 += 1
            located_by_mode[p["mode"]] += 1
        detail.append({"target": p["urn"], "mode": p["mode"], "located": located,
                       "candidates": cands, "verified": verified_names})
    counts = {
        "n_location_targets": len(probes),
        "n_location_top5": n_top5,
        "n_llm_candidates": n_cand,
        "n_f_verified": n_ver,
    }
    breakdown = {
        "n_targets_anchor_mode": targets_by_mode["anchor"],
        "n_targets_statement_mode": targets_by_mode["statement"],
        "n_located_anchor_mode": located_by_mode["anchor"],
        "n_located_statement_mode": located_by_mode["statement"],
        "n_llm_extraction_failures": n_extract_fail,
        "n_candidates_unresolvable": n_unresolved,
        "n_candidates_f_rejected_or_mismatched": n_rejected,
        "n_candidates_over_cap_dropped": n_dropped,
    }
    return counts, breakdown, detail


def run_roundtrip(mints, probes, concepts):
    n = n_fixed = 0
    n_sample = 0
    for _, stmt in mints:
        n += 1
        n_sample += 1
        if F.roundtrip_fixed(stmt, concepts):
            n_fixed += 1
    for p in probes:
        for s in p["statements"]:
            n += 1
            if F.roundtrip_fixed(s, concepts):
                n_fixed += 1
    return {"n_roundtrip": n, "n_roundtrip_fixed": n_fixed}, \
        {"n_roundtrip_sample_mints": n_sample,
         "n_roundtrip_probe_statements": n - n_sample}


def compose_metrics(args, root):
    _, pack_sha, probes, concepts = build_prompt_pack(root)
    gate_counts, reasons, mints = run_gate(args.sample, concepts,
                                           args.details)
    rt_counts, rt_break = run_roundtrip(mints, probes, concepts)
    header, raws = read_raws(args.raw)
    archive = load_archives(args.candidates.split(","))
    loc_counts, loc_break, loc_detail = score_location(
        probes, header, raws, archive, pack_sha, concepts)
    metrics = {}
    metrics.update(gate_counts)
    metrics.update(loc_counts)
    metrics.update(rt_counts)
    metrics["gate_reject_reasons"] = reasons
    metrics["location_breakdown"] = loc_break
    metrics["roundtrip_breakdown"] = rt_break
    metrics["provenance"] = {
        "sample_file_sha256": sha256_file(args.sample),
        "prompt_pack_sha256": pack_sha,
        "raw_file_sha256": sha256_file(args.raw),
        "llm_model": header.get("model", ""),
        "n_candidate_archives": len(args.candidates.split(",")),
    }
    if args.details:
        with open(args.details, "a", encoding="utf-8") as f:
            for d in loc_detail:
                f.write(json.dumps(d, sort_keys=True) + "\n")
    return metrics


# ---------------------------------------------------------------- --call-llm (runner helper)

def call_llm(args):
    key = os.environ.get(args.key_env, "")
    if not key:
        fail("ERR_G8_KEY", "environment variable %s is empty/unset" % args.key_env)
    with open(args.prompts, "r", encoding="utf-8") as f:
        rows = [json.loads(l) for l in f if l.strip()]
    pack_sha = sha256_file(args.prompts)
    header = {"schema": RAW_SCHEMA, "pack_sha256": pack_sha,
              "model": args.model,
              "decode": {"temperature": 0, "max_tokens": args.max_tokens},
              "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    out = [json.dumps(header, sort_keys=True)]
    for row in rows[1:]:  # rows[0] is the pack header
        body = json.dumps({
            "model": args.model,
            "temperature": 0,
            "max_tokens": args.max_tokens,
            "messages": [{"role": "user", "content": row["prompt"]}],
        }).encode("utf-8")
        req = urllib.request.Request(
            args.base_url.rstrip("/") + "/chat/completions", data=body,
            headers={"Content-Type": "application/json",
                     "Authorization": "Bearer " + key})
        text, err = None, None
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
                text = payload["choices"][0]["message"]["content"]
                break
            except Exception as e:  # never print the key; record the class only
                err = type(e).__name__
                time.sleep(2 ** attempt)
        out.append(json.dumps({"target": row["target"], "output_text": text,
                               "error": err if text is None else None},
                              sort_keys=True))
        print("  %s %s" % (row["target"], "ok" if text is not None else err),
              file=sys.stderr)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print(json.dumps({"raw": args.out, "n": len(out) - 1}))


# ---------------------------------------------------------------- --fetch-candidates

def _http_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "kot-g8/1"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        return resp.read(), dict(resp.headers)


def _flat_text(fragment):
    detagged = re.sub(r"</?(?:div|p|li|ul|ol|details|summary|blockquote|br|h[1-6])\b[^>]*>",
                      " ", fragment)
    detagged = re.sub(r"<[^>]*>", "", detagged)
    ents = {"amp": "&", "lt": "<", "gt": ">", "quot": '"', "apos": "'", "nbsp": " "}

    def sub(m):
        body = m.group(1)
        if body.startswith("#"):
            try:
                cp = int(body[2:], 16) if body[1] in "xX" else int(body[1:])
                return chr(cp)
            except ValueError:
                return m.group(0)
        return ents.get(body, m.group(0))
    return re.sub(r"\s+", " ", re.sub(r"&(#x?[0-9a-fA-F]+|[a-zA-Z]+);", sub,
                                      detagged)).strip()


def _div_span_end(html, start):
    depth = 0
    for m in re.finditer(r"</?div\b", html[start:]):
        depth += 1 if m.group(0) == "<div" else -1
        if depth == 0:
            close = html.find(">", start + m.start())
            return close + 1
    raise ValueError("ERR_UNBALANCED_DIV")


_GH_RE = re.compile(
    r"https://github\.com/leanprover-community/mathlib4/blob/([0-9a-f]{40})/")


def extract_decl_signature(html, name):
    """Port of extract.mjs's decl parsing, single-declaration variant.
    Returns (signaturePretty, kind, commit) or None."""
    marker = '<div class="decl" id="%s"' % name
    at = html.find(marker)
    if at == -1:
        return None
    decl_html = html[at:_div_span_end(html, at)]
    kind_m = re.search(r'<span class="decl_kind">([a-z ]+)</span>', decl_html)
    gh_m = _GH_RE.search(decl_html)
    h_start = decl_html.find('<div class="decl_header">')
    if h_start == -1:
        return None
    header_html = decl_html[h_start:_div_span_end(decl_html, h_start)]
    return (_flat_text(header_html), kind_m.group(1) if kind_m else "",
            gh_m.group(1) if gh_m else "")


def fetch_candidates(args, root):
    header, raws = read_raws(args.raw)
    names = set()
    for r in raws:
        ext = extract_candidates(r.get("output_text"))
        if ext:
            names.update(ext[0])
    # skip names already resolvable from the pinned local corpora
    local = load_archives([
        os.path.join(root, "data", "mathlib-1000-sample", "records.jsonl"),
        os.path.join(root, "data", "math-lean-sample", "records.jsonl")])
    todo = sorted(n for n in names if n not in local)
    os.makedirs(args.out, exist_ok=True)
    if args.index:
        with open(args.index, "rb") as f:
            index_bytes = f.read()
    else:
        print("fetching declaration index (~66 MB) ...", file=sys.stderr)
        index_bytes, _ = _http_get(args.site.rstrip("/")
                                   + "/declarations/declaration-data.bmp")
    index_sha = hashlib.sha256(index_bytes).hexdigest()
    decls = json.loads(index_bytes.decode("utf-8"))["declarations"]
    by_page = {}
    missing = []
    for n in todo:
        info = decls.get(n)
        if not info:
            missing.append(n)
            continue
        page = info["docLink"].split("#")[0].lstrip("./")
        by_page.setdefault(page, []).append(n)
    archive_lines = []
    fetch_log = {"index_sha256": index_sha, "pages": {}, "unindexed": missing}
    commit_seen = set()
    for page in sorted(by_page):
        url = args.site.rstrip("/") + "/" + page
        try:
            html_bytes, headers = _http_get(url)
        except Exception as e:
            fetch_log["pages"][page] = {"error": type(e).__name__}
            continue
        html = html_bytes.decode("utf-8", "replace")
        fetch_log["pages"][page] = {
            "sha256": hashlib.sha256(html_bytes).hexdigest(),
            "bytes": len(html_bytes),
            "last_modified": headers.get("Last-Modified", "")}
        import gzip
        with gzip.open(os.path.join(
                args.out, page.replace("/", ".") + ".gz"), "wb") as gz:
            gz.write(html_bytes)
        for n in by_page[page]:
            got = extract_decl_signature(html, n)
            if got is None:
                continue
            sig, kind, commit = got
            if commit:
                commit_seen.add(commit)
            archive_lines.append(json.dumps(
                {"name": n, "kind": kind, "signaturePretty": sig,
                 "source": {"mathlibCommit": commit, "docPage": page}},
                sort_keys=True))
        time.sleep(args.throttle)
    if len(commit_seen) > 1:
        fail("ERR_G8_COMMIT", "cross-page commit mismatch: %s"
             % sorted(commit_seen))
    fetch_log["mathlib_commit"] = sorted(commit_seen)[0] if commit_seen else ""
    with open(os.path.join(args.out, "archive.jsonl"), "w", encoding="utf-8") as f:
        f.write("\n".join(archive_lines) + ("\n" if archive_lines else ""))
    with open(os.path.join(args.out, "fetch-log.json"), "w", encoding="utf-8") as f:
        json.dump(fetch_log, f, indent=1, sort_keys=True)
    print(json.dumps({"archive": os.path.join(args.out, "archive.jsonl"),
                      "n_resolved": len(archive_lines),
                      "n_unindexed": len(missing),
                      "mathlib_commit": fetch_log["mathlib_commit"]},
                     sort_keys=True))


# ---------------------------------------------------------------- mock fixtures

def _v(i):
    return {"kind": "var", "index": i}


def _num(j):
    return [{"kind": "zero"},
            {"kind": "const", "ref": F.U + "one", "args": []},
            {"kind": "const", "ref": F.U + "two", "args": []},
            {"kind": "const", "ref": F.U + "three", "args": []}][j % 4]


def _fixture_in_fragment(i):
    """30 distinct in-fragment pm-ast statements, index-deterministic."""
    add = lambda a, b: {"kind": "const", "ref": F.U + "addition", "args": [a, b]}
    mul = lambda a, b: {"kind": "const", "ref": F.U + "multiplication", "args": [a, b]}
    le = lambda a, b: {"kind": "const", "ref": F.U + "less-or-equal", "args": [a, b]}
    eq = lambda a, b: {"kind": "eq", "left": a, "right": b}
    fa = lambda s, b: {"kind": "forall", "sort": s, "body": b}
    op = add if i % 2 == 0 else mul
    k = i % 4
    variant = i % 5
    if variant == 0:      # ∀ a b, op(a+_k, b) = op(b, a+_k)  (comm-with-offset)
        return fa("N", fa("N", eq(op(add(_v(1), _num(k)), _v(0)),
                                  op(_v(0), add(_v(1), _num(k))))))
    if variant == 1:      # ∀ a, a ≤ a + numeral
        return fa("N", le(_v(0), add(_v(0), _num(k))))
    if variant == 2:      # ∀ a, ¬(succ (a + numeral) = 0)
        return fa("N", {"kind": "not", "arg": eq(
            {"kind": "succ", "arg": add(_v(0), _num(k))}, {"kind": "zero"})})
    if variant == 3:      # ∀ a s, a ∈ s → a ∈ (s ∪ {numeral})
        uni = {"kind": "const", "ref": F.U + "union-nat",
               "args": [_v(0), {"kind": "const", "ref": F.U + "singleton-nat",
                                "args": [_num(k)]}]}
        return fa("N", fa({"kind": "Set", "of": "N"},
                          {"kind": "implies",
                           "left": {"kind": "member", "element": _v(1), "set": _v(0)},
                           "right": {"kind": "member", "element": _v(1), "set": uni}}))
    # variant 4: ∃ b, a-free equality over numerals: ∀ a, ∃ b, a + b = a + b … keep used
    return fa("N", {"kind": "exists", "sort": "N",
                    "body": eq(add(_v(1), _v(0)), add(_v(1), _num(k)))})


_OUT_TEMPLATES = (
    "theorem G8Fix.o%d {α : Type u_1} [Monoid α] (a : α) : a * a = a",
    "def G8Fix.d%d (n : ℕ) : ℕ",
    "theorem G8Fix.p%d (n : ℕ) : n ^ 2 = n * n",
    "theorem G8Fix.s%d (s : Finset ℕ) : s = s",
    "theorem G8Fix.n%d : 7 = 7",
    "instance G8Fix.i%d : Monoid ℕ",
    "theorem G8Fix.f%d (f : ℕ → ℕ) : f 0 = f 0",
)


def build_mock(workdir, root):
    concepts = F.load_math_v0(root)
    probes = F.build_probes(concepts)
    os.makedirs(workdir, exist_ok=True)
    # ---- fixture sample: exactly 1000 records, exactly 30 in-fragment
    sample_path = os.path.join(workdir, "fixture-sample.jsonl")
    lines = []
    for i in range(30):
        stmt = _fixture_in_fragment(i)
        F.check_statement(stmt, concepts)
        sig = "theorem G8Fix.t%d : %s" % (i, F.render_lean(stmt))
        lines.append({"record": "lean-ref/1", "name": "G8Fix.t%d" % i,
                      "kind": "theorem", "extraction": "doc-gen4-decl",
                      "signaturePretty": sig})
    for i in range(968):
        lines.append({"record": "lean-ref/1", "name": "G8Fix.x%d" % i,
                      "kind": "theorem", "extraction": "doc-gen4-decl",
                      "signaturePretty": _OUT_TEMPLATES[i % len(_OUT_TEMPLATES)] % i})
    for i in range(2):
        lines.append({"record": "lean-ref/1", "name": "G8Fix.sub%d" % i,
                      "kind": "def", "extraction": "sub-declaration",
                      "signaturePretty": ""})
    with open(sample_path, "w", encoding="utf-8") as f:
        for l in lines:
            f.write(json.dumps(l, sort_keys=True) + "\n")
    # ---- prompt pack
    pack_path = os.path.join(workdir, "prompt-pack.jsonl")
    blob, pack_sha, _, _ = build_prompt_pack(root)
    with open(pack_path, "w", encoding="utf-8") as f:
        f.write(blob)
    # ---- fixture raws + candidate archive
    fail_targets = {F.U + "integer", F.U + "int-pair-equiv",
                    F.U + "integer-negation"}
    extraction_fail_target = F.U + "integer-negation"
    raw_path = os.path.join(workdir, "fixture-raw.jsonl")
    arch_path = os.path.join(workdir, "fixture-archive.jsonl")
    raw_lines = [json.dumps({"schema": RAW_SCHEMA, "pack_sha256": pack_sha,
                             "model": "fixture-offline-responder/0",
                             "decode": {"temperature": 0}}, sort_keys=True)]
    arch_lines = []
    swap_i = 0
    for p in probes:
        slug = p["urn"].split(":")[-1].replace("-", "_")
        if p["urn"] == extraction_fail_target:
            raw_lines.append(json.dumps(
                {"target": p["urn"],
                 "output_text": "I am fairly sure it is Nat.something."},
                sort_keys=True))
            continue
        if p["mode"] == "anchor":
            cands = list(p["anchors"]) + ["G8Fix.decoy.%s" % slug]
        elif p["urn"] in fail_targets:
            cands = ["G8Fix.wrong.%s.0" % slug, "G8Fix.missingsig.%s" % slug]
            # wrong candidate: a real in-fragment statement that matches nothing
            wrong = _fixture_in_fragment(0)
            arch_lines.append(json.dumps(
                {"name": cands[0],
                 "signaturePretty": "theorem %s : %s" % (cands[0],
                                                         F.render_lean(wrong))},
                sort_keys=True))
        else:
            cands = []
            for j, stmt in enumerate(p["statements"]):
                name = "G8Fix.loc.%s.%d" % (slug, j)
                cands.append(name)
                render = stmt
                # every 3rd statement-mode target: exercise the pre-declared
                # top-level orientation swap
                spine, t = [], stmt
                while t["kind"] == "forall":
                    spine.append(t)
                    t = t["body"]
                if t["kind"] in ("eq", "iff") and swap_i % 3 == 0:
                    sw = dict(t)
                    sw["left"], sw["right"] = t["right"], t["left"]
                    for q in reversed(spine):
                        sw = {"kind": "forall", "sort": q["sort"], "body": sw}
                    render = sw
                arch_lines.append(json.dumps(
                    {"name": name,
                     "signaturePretty": "theorem %s : %s"
                                        % (name, F.render_lean(render))},
                    sort_keys=True))
            swap_i += 1
            cands.append("G8Fix.offrag.%s" % slug)  # resolves out-of-fragment
            arch_lines.append(json.dumps(
                {"name": cands[-1],
                 "signaturePretty": "theorem G8Fix.offrag.%s (n : ℕ) : n - n = 0"
                                    % slug}, sort_keys=True))
        raw_lines.append(json.dumps(
            {"target": p["urn"],
             "output_text": json.dumps({"candidates": cands})}, sort_keys=True))
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write("\n".join(raw_lines) + "\n")
    with open(arch_path, "w", encoding="utf-8") as f:
        f.write("\n".join(arch_lines) + "\n")
    return sample_path, raw_path, arch_path


def run_mock(args, root):
    workdir = args.workdir or tempfile.mkdtemp(prefix="g8-mock-")
    sample, raw, arch = build_mock(workdir, root)

    class A:
        pass
    a = A()
    a.sample, a.raw, a.candidates = sample, raw, arch
    a.details = os.path.join(workdir, "details.jsonl")
    metrics = compose_metrics(a, root)
    # ---- feed the PINNED analysis script (contract check)
    analysis = os.path.join(root, "analysis", "g8.py")
    rec = json.dumps({"metrics": {k: v for k, v in metrics.items()
                                  if k.startswith("n_")}})
    out = subprocess.run([sys.executable, analysis], input=rec,
                         capture_output=True, text=True, check=True)
    result = json.loads(out.stdout)
    checks = {}
    a_ = result.get("analysis", {})
    g_ = result.get("gates", {})
    checks["instrument_valid_true"] = g_.get("instrument_valid") is True
    checks["eight_counts_wellformed"] = all(
        isinstance(metrics.get(k), int) and metrics.get(k) >= 0
        for k in ("n_mathlib_decls", "n_in_fragment", "n_location_targets",
                  "n_location_top5", "n_roundtrip", "n_roundtrip_fixed",
                  "n_llm_candidates", "n_f_verified"))
    for prefix in ("fragment", "location"):
        lb = a_.get("%s_wilson_lb" % prefix)
        ub = a_.get("%s_wilson_ub" % prefix)
        rate = a_.get("%s_rate" % prefix)
        checks["%s_wilson_sane" % prefix] = (
            lb is not None and ub is not None and rate is not None
            and 0.0 <= lb <= rate <= ub <= 1.0)
    checks["fragment_lb_matches_selftest_fixture"] = (
        abs(a_.get("fragment_wilson_lb", 0) - 0.02232) < 5e-5)
    checks["roundtrip_holds"] = a_.get("roundtrip_holds") is True
    checks["f_verification_rate_present"] = "f_verification_rate" in a_
    checks["all_analysis_output_fields_present"] = all(
        k in a_ for k in ("fragment_rate", "fragment_wilson_lb",
                          "fragment_wilson_ub", "location_rate",
                          "location_wilson_lb", "location_wilson_ub",
                          "roundtrip_holds", "f_verification_rate",
                          "n_mathlib_decls", "n_location_targets"))
    # forbidden derived-stat keys must not appear anywhere in raw metrics
    sys.path.insert(0, os.path.join(root, "tools", "registry"))
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "kot_common", os.path.join(root, "tools", "registry", "kot_common.py"))
    kc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kc)
    checks["no_forbidden_metric_keys"] = (
        kc.find_forbidden_metric_keys(metrics) == [])
    mock_ok = all(checks.values())
    print(json.dumps({"mock_ok": mock_ok, "workdir": workdir,
                      "checks": checks,
                      "metrics": {k: v for k, v in metrics.items()
                                  if isinstance(v, int)},
                      "analysis_output": result}, sort_keys=True, indent=1))
    sys.exit(0 if mock_ok else 1)


# ---------------------------------------------------------------- selftest

def selftest(root):
    C = F.load_math_v0(root)
    probes = F.build_probes(C)
    assert len(probes) == 39, "39 targets"
    n_stmts = sum(len(p["statements"]) for p in probes)
    assert n_stmts == 33, "33 probe statements (27 single + 3x2 recursive)"
    assert sum(1 for p in probes if p["mode"] == "anchor") == 9
    # every probe statement round-trips through the production renderer+parser
    for p in probes:
        for s in p["statements"]:
            assert F.roundtrip_fixed(s, C), "roundtrip %s" % p["urn"]
    # F on hand-written Lean surface == the actual frozen math-v0 content
    _, s = F.lean_statement_to_pm("theorem T.a : ∀ (n : ℕ), Nat.succ n ≠ 0", C)
    assert F.canonical(s) == F.canonical(
        C[F.U + "ax-succ-nonzero"]["definition"]["statement"])
    _, s = F.lean_statement_to_pm(
        "theorem T.b (n m : ℕ) (h : n.succ = m.succ) : n = m", C)
    assert F.canonical(s) == F.canonical(
        C[F.U + "ax-succ-injective"]["definition"]["statement"])
    add = next(p for p in probes if p["urn"] == F.U + "addition")
    _, s = F.lean_statement_to_pm("theorem T.c (n : ℕ) : n + 0 = n", C)
    assert F.content_sha(s) in add["admissible"][0]
    _, s = F.lean_statement_to_pm(
        "theorem T.d (n m : ℕ) : n + Nat.succ m = Nat.succ (n + m)", C)
    assert F.content_sha(s) in add["admissible"][1]
    ev = next(p for p in probes if p["urn"] == F.U + "even")
    for sig in ("theorem T.e (n : ℕ) : Even n ↔ 2 ∣ n",
                "theorem T.f (n : ℕ) : 2 ∣ n ↔ Even n"):
        _, s = F.lean_statement_to_pm(sig, C)
        assert F.content_sha(s) in ev["admissible"][0]
    # defeq is NOT aliased: n+1 is not succ n
    _, s = F.lean_statement_to_pm("theorem T.g : ∀ (n : ℕ), n + 1 ≠ 0", C)
    assert F.canonical(s) != F.canonical(
        C[F.U + "ax-succ-nonzero"]["definition"]["statement"])
    # rejects carry honest reasons
    for sig, code in (("def D (n : ℕ) : ℕ", "definiens-unavailable-at-layer"),
                      ("theorem V (n m : ℕ) : n = n", "vacuous-binder"),
                      ("theorem N : 4 = 4", "numeral-out-of-range"),
                      ("theorem S (n : ℕ) : n - n = 0", "unbridged-operator"),
                      ("theorem I [NeZero 1] : 1 = 1", "typeclass-binder")):
        try:
            F.lean_statement_to_pm(sig, C)
            raise AssertionError("accepted %r" % sig)
        except F.Reject as e:
            assert e.code == code, "%s -> %s (want %s)" % (sig, e.code, code)
    # prompt pack is deterministic
    b1, sha1, _, _ = build_prompt_pack(root)
    b2, sha2, _, _ = build_prompt_pack(root)
    assert b1 == b2 and sha1 == sha2
    print("g8 instrument selftest OK (39 targets / 33 statements / roundtrip green)")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="G8 instrument (raw counts only; no verdicts).")
    ap.add_argument("--root", default=None)
    m = ap.add_mutually_exclusive_group(required=True)
    m.add_argument("--selftest", action="store_true")
    m.add_argument("--emit-prompts", action="store_true")
    m.add_argument("--gate", action="store_true")
    m.add_argument("--run", action="store_true")
    m.add_argument("--call-llm", action="store_true")
    m.add_argument("--fetch-candidates", action="store_true")
    m.add_argument("--mock", action="store_true")
    ap.add_argument("--sample", help="lean-ref/1 records.jsonl (EXPLICIT always; "
                                     "the real d-ml sample only in the final run)")
    ap.add_argument("--raw", help="g8-locate-raw/1 file")
    ap.add_argument("--candidates", help="comma-separated candidate-archive JSONL paths")
    ap.add_argument("--details", help="per-record/per-target detail JSONL out")
    ap.add_argument("--out", help="output path (prompts/raw/fetch dir)")
    ap.add_argument("--prompts", help="prompt pack path (--call-llm)")
    ap.add_argument("--base-url", help="OpenAI-compatible API base URL")
    ap.add_argument("--model", help="model id for --call-llm")
    ap.add_argument("--key-env", default="G8_LLM_API_KEY")
    ap.add_argument("--max-tokens", type=int, default=300)
    ap.add_argument("--site", default=DOC_SITE)
    ap.add_argument("--index", help="pre-downloaded declaration-data.bmp (JSON)")
    ap.add_argument("--throttle", type=float, default=1.0)
    ap.add_argument("--workdir", help="mock working dir (default: fresh temp dir)")
    args = ap.parse_args()
    root = args.root or repo_root()

    if args.selftest:
        selftest(root)
        return
    if args.emit_prompts:
        if not args.out:
            fail("ERR_G8_ARGS", "--emit-prompts needs --out")
        blob, sha, _, _ = build_prompt_pack(root)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(blob)
        print(json.dumps({"pack_sha256": sha, "path": args.out}))
        return
    if args.gate:
        if not args.sample:
            fail("ERR_G8_ARGS", "--gate needs an explicit --sample")
        concepts = F.load_math_v0(root)
        counts, reasons, _ = run_gate(args.sample, concepts, args.details)
        counts["gate_reject_reasons"] = reasons
        print(json.dumps(counts, sort_keys=True))
        return
    if args.run:
        for need in ("sample", "raw", "candidates"):
            if not getattr(args, need):
                fail("ERR_G8_ARGS", "--run needs --" + need)
        print(json.dumps(compose_metrics(args, root), sort_keys=True))
        return
    if args.call_llm:
        for need in ("prompts", "out", "base_url", "model"):
            if not getattr(args, need):
                fail("ERR_G8_ARGS", "--call-llm needs --" + need.replace("_", "-"))
        call_llm(args)
        return
    if args.fetch_candidates:
        if not args.raw or not args.out:
            fail("ERR_G8_ARGS", "--fetch-candidates needs --raw and --out")
        fetch_candidates(args, root)
        return
    if args.mock:
        run_mock(args, root)


if __name__ == "__main__":
    main()
