#!/usr/bin/env python3
"""CODEVERT G1-FORWARD annotation sample + context bundles + prompts.

Per DESIGN-PIN.md sect 4 [PROPOSED-ASM: ASM-1114/1115]: 2 queries per
(family x repo) cell, families = FL-4 + callees_of sensitivity, seed
20260716; 120 KB context cap with pinned next-index replacement (logged).
Bundles are built from RAW REPO SOURCE ONLY — no extractor/engine output
enters any prompt byte (annotator blindness, auditable via saved prompts).
"""
import ast, json, os, random, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
SEED = 20260716
FAMILIES = ["contains", "contained_in", "imports_of", "where_defined",
            "callees_of"]
CAP = 120 * 1024


def numbered(src_bytes):
    lines = src_bytes.decode("utf-8", "replace").splitlines()
    return "\n".join("%5d| %s" % (i + 1, l) for i, l in enumerate(lines))


def py_listing(root):
    out = []
    for dp, dn, fn in os.walk(root):
        dn[:] = sorted(d for d in dn if d != ".git")
        for f in sorted(fn):
            if f.endswith(".py"):
                out.append(os.path.relpath(os.path.join(dp, f), root))
    return out


class ScopeMap(ast.NodeVisitor):
    """lineno -> enclosing def/class chain (syntactic only, for excerpts)."""

    def __init__(self):
        self.spans = []  # (start, end, chain)
        self.stack = []

    def _v(self, node):
        chain = ".".join(self.stack + [node.name])
        self.spans.append((node.lineno, getattr(node, "end_lineno", node.lineno),
                           chain, type(node).__name__))
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    visit_FunctionDef = visit_AsyncFunctionDef = visit_ClassDef = _v

    def chain_at(self, lineno):
        best = None
        for a, b, c, k in self.spans:
            if a <= lineno <= b:
                if best is None or (b - a) < (best[1] - best[0]):
                    best = (a, b, c, k)
        return best


def where_defined_bundle(root, listing, name, scopemaps):
    rx = re.compile(r"\b%s\b" % re.escape(name))
    parts = []
    for rel in listing:
        try:
            src = open(os.path.join(root, rel), "rb").read().decode("utf-8", "replace")
        except OSError:
            continue
        hits = []
        for i, line in enumerate(src.splitlines(), 1):
            if rx.search(line):
                sm = scopemaps.get(rel)
                ch = sm.chain_at(i) if sm else None
                scope = ("enclosing=%s(%s)" % (ch[2], ch[3])
                         if ch and not (ch[0] == i) else
                         ("HEADER-LINE-OF=%s" % ch[2] if ch else "module-level"))
                if ch and ch[0] != i:
                    pass
                elif not ch:
                    scope = "module-level"
                hits.append("  line %d [%s]: %s" % (i, scope, line.rstrip()))
        if hits:
            parts.append("FILE %s (all lines containing the token):\n%s"
                         % (rel, "\n".join(hits)))
    return ("WHERE-DEFINED EXCERPTS for token %r — every line in every .py "
            "file that contains the token, with line numbers and the "
            "enclosing def/class scope. [%s] marks the syntactic context: "
            "module-level = not inside any def/class; enclosing=X(kind) = the "
            "line sits inside X; HEADER-LINE-OF=X = the line IS the def/class "
            "header of X.\n\n" % (name, "scope")) + "\n\n".join(parts)


def main():
    census = json.load(open(os.path.join(BASE, "results", "census-g1.json")))
    lock = json.load(open(os.path.join(BASE, "repos.lock.json")))
    repos = [r["name"] for r in lock["selected"]]
    rng = random.Random(SEED)
    sample = {"seed": SEED, "cap_bytes": CAP, "queries": [],
              "replacements": [], "shortfalls": []}
    prompts_dir = os.path.join(BASE, "annotation", "prompts")
    os.makedirs(prompts_dir, exist_ok=True)
    instr = open(os.path.join(BASE, "annotation-instructions.md")).read()

    for repo in repos:
        root = os.path.join(BASE, "corpus", repo)
        listing = py_listing(root)
        scopemaps = {}
        for rel in listing:
            try:
                t = ast.parse(open(os.path.join(root, rel), "rb").read())
                sm = ScopeMap()
                sm.visit(t)
                scopemaps[rel] = sm
            except (SyntaxError, ValueError):
                pass
        cdata = census["repos"][repo]
        for fam in FAMILIES:
            u = cdata["universes"][fam]
            idx = list(range(len(u)))
            rng.shuffle(idx)
            chosen, ctxs, ptr = [], {}, 0
            while len(chosen) < 2 and ptr < len(idx):
                i = idx[ptr]
                ptr += 1
                tgt = u[i]
                # build this query's context
                if fam == "where_defined":
                    key = "wd::" + tgt["name"]
                    ctx = where_defined_bundle(root, listing, tgt["name"],
                                               scopemaps)
                else:
                    key = "file::" + tgt["file"]
                    try:
                        ctx = "FILE %s:\n%s" % (tgt["file"], numbered(
                            open(os.path.join(root, tgt["file"]), "rb").read()))
                    except OSError:
                        ctx = "FILE %s: <unreadable>" % tgt["file"]
                # cap check: existing chosen ctxs + this one
                total = sum(len(c) for c in ctxs.values()) \
                    + (len(ctx) if key not in ctxs else 0)
                if total > CAP:
                    sample["replacements"].append(
                        {"repo": repo, "family": fam, "skipped_index": i,
                         "reason": "bundle-cap"})
                    continue
                ctxs[key] = ctx
                qid = "g1q-%s-%s-%d" % (repo, fam, i)
                chosen.append({"query_id": qid, "repo": repo, "family": fam,
                               "census_index": i, "target": tgt})
            if len(chosen) < 2:
                sample["shortfalls"].append({"repo": repo, "family": fam,
                                             "n": len(chosen)})
            sample["queries"].extend(chosen)
            # ---- prompt assembly (byte-identical for both annotators) ----
            qtxt = []
            for q in chosen:
                t = q["target"]
                if fam == "where_defined":
                    qtxt.append("QUERY %s: family=where_defined name=%s"
                                % (q["query_id"], t["name"]))
                elif fam in ("imports_of",):
                    qtxt.append("QUERY %s: family=imports_of module=%s"
                                % (q["query_id"], t["file"]))
                else:
                    qual = t.get("qual")
                    qtxt.append("QUERY %s: family=%s target=%s%s"
                                % (q["query_id"], fam, t["file"],
                                   ("::" + qual) if qual else ""))
            prompt = (instr
                      + "\n\n=== REPOSITORY: %s ===\n" % repo
                      + "PY FILE LISTING (repo-root-relative; authoritative):\n"
                      + "\n".join(listing)
                      + "\n\n=== QUERIES (%d) ===\n" % len(chosen)
                      + "\n".join(qtxt)
                      + "\n\n=== CONTEXT ===\n\n"
                      + "\n\n".join(ctxs.values())
                      + "\n\nAnswer now with ONE JSON array containing one "
                        "object per query, in query order.\n")
            fn = os.path.join(prompts_dir, "%s--%s.txt" % (repo, fam))
            with open(fn, "w") as f:
                f.write(prompt)
    with open(os.path.join(BASE, "annotation", "sample.json"), "w") as f:
        json.dump(sample, f, indent=1, sort_keys=True)
    print("queries:", len(sample["queries"]),
          "replacements:", len(sample["replacements"]),
          "shortfalls:", sample["shortfalls"])
    sizes = sorted((os.path.getsize(os.path.join(prompts_dir, p)), p)
                   for p in os.listdir(prompts_dir))
    print("largest prompts:", sizes[-3:])


if __name__ == "__main__":
    main()
