"""
X1-grounding shared library (stdlib only).

Implements the frozen preprocessing pipeline (PREREG §2), graph primitives
(iterative Tarjan SCC, Kahn acyclicity, Kernel peel) and canonical JSON I/O.

Every function here is a mechanical transcription of a PREREG section; the
section is cited in the docstring/comment. No analyst-chosen behaviour.
"""
import hashlib
import json
import os
import re

# ---------------------------------------------------------------------------
# Canonical JSON I/O (PREREG §7: sorted keys, newline-terminated, byte-determ.)
# ---------------------------------------------------------------------------

def dump_json(obj, path):
    with open(path, "w") as f:
        f.write(json.dumps(obj, sort_keys=True, separators=(",", ":")))
        f.write("\n")


def dump_json_pretty(obj, path):
    with open(path, "w") as f:
        f.write(json.dumps(obj, sort_keys=True, indent=2))
        f.write("\n")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


# ---------------------------------------------------------------------------
# Data paths (relative to repo root, resolved from this file's location).
# ---------------------------------------------------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
DATA = os.path.join(REPO, "data", "lexical-wn31")
DICT = os.path.join(DATA, "source", "dict")

SYNSET_FILES = {
    "noun": os.path.join(DATA, "synsets-noun.jsonl"),
    "verb": os.path.join(DATA, "synsets-verb.jsonl"),
    "adj": os.path.join(DATA, "synsets-adj.jsonl"),
    "adv": os.path.join(DATA, "synsets-adv.jsonl"),
}
INDEX_FILES = {
    "noun": os.path.join(DICT, "index.noun"),
    "verb": os.path.join(DICT, "index.verb"),
    "adj": os.path.join(DICT, "index.adj"),
    "adv": os.path.join(DICT, "index.adv"),
}
EXC_FILES = {
    "noun": os.path.join(DICT, "noun.exc"),
    "verb": os.path.join(DICT, "verb.exc"),
    "adj": os.path.join(DICT, "adj.exc"),
    "adv": os.path.join(DICT, "adv.exc"),
}

ERR_SOURCE_MISSING = "ERR_X1G_SOURCE_MISSING"

# ---------------------------------------------------------------------------
# Closed-class definer stoplist (PREREG §9 Amendment 3, 2026-07-07).
# STANDARD published English stopword list, transcribed VERBATIM: the NLTK
# `stopwords` English list (179 entries; articles, prepositions, coordinating/
# subordinating conjunctions, pronouns, auxiliary/modal verbs, particles,
# high-frequency determiners). Chosen ONCE, blind to any downstream statistic.
# Applied to DEFINER (definition) tokens only; the node vocabulary is unchanged.
# GUARDRAIL: the 51 frozen evaluable-prime node forms are subtracted before use,
# so the filter can never remove a node under test (asserted in definer_stoplist).
# ---------------------------------------------------------------------------

STOPLIST_STANDARD = [
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you",
    "you're", "you've", "you'll", "you'd", "your", "yours", "yourself",
    "yourselves", "he", "him", "his", "himself", "she", "she's", "her", "hers",
    "herself", "it", "it's", "its", "itself", "they", "them", "their", "theirs",
    "themselves", "what", "which", "who", "whom", "this", "that", "that'll",
    "these", "those", "am", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an",
    "the", "and", "but", "if", "or", "because", "as", "until", "while", "of",
    "at", "by", "for", "with", "about", "against", "between", "into", "through",
    "during", "before", "after", "above", "below", "to", "from", "up", "down",
    "in", "out", "on", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "any",
    "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor",
    "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can",
    "will", "just", "don", "don't", "should", "should've", "now", "d", "ll",
    "m", "o", "re", "ve", "y", "ain", "aren", "aren't", "couldn", "couldn't",
    "didn", "didn't", "doesn", "doesn't", "hadn", "hadn't", "hasn", "hasn't",
    "haven", "haven't", "isn", "isn't", "ma", "mightn", "mightn't", "mustn",
    "mustn't", "needn", "needn't", "shan", "shan't", "shouldn", "shouldn't",
    "wasn", "wasn't", "weren", "weren't", "won", "won't", "wouldn", "wouldn't",
]

# The 51 frozen evaluable-prime node forms (PREREG §5.1). Single source of truth;
# prime_map.py cross-checks its target column against this set.
EVALUABLE_PRIME_NODES = frozenset([
    "someone", "thing", "people", "body", "kind", "part", "same", "other",
    "one", "two", "some", "all", "much", "little", "good", "bad", "big",
    "small", "think", "know", "want", "feel", "see", "hear", "say", "word",
    "true", "do", "happen", "move", "live", "die", "time", "now", "before",
    "after", "moment", "place", "here", "above", "below", "far", "near",
    "side", "inside", "touch", "not", "maybe", "very", "more", "like",
])


def definer_stoplist():
    """Applied stoplist = STOPLIST_STANDARD minus the 51 evaluable-prime nodes.
    Asserts the guardrail (PREREG §9 Amendment 3 spec item 2)."""
    applied = frozenset(STOPLIST_STANDARD) - EVALUABLE_PRIME_NODES
    assert applied.isdisjoint(EVALUABLE_PRIME_NODES), \
        "GUARDRAIL VIOLATION: stoplist would remove a node under test"
    return applied


def stoplist_guardrail_removed():
    """Prime node forms that were present in the standard list and protected."""
    return sorted(frozenset(STOPLIST_STANDARD) & EVALUABLE_PRIME_NODES)


# ---------------------------------------------------------------------------
# Index vocabulary (PREREG §3: nodes = index lemmas, lowercased, POS-collapsed).
# License lines start with whitespace; data lines' first field is the lemma.
# ---------------------------------------------------------------------------

def load_index():
    """Return (per_pos: {pos->set(lemma)}, union: set(lemma))."""
    per_pos = {}
    union = set()
    for pos, path in INDEX_FILES.items():
        if not os.path.exists(path):
            raise SystemExit(f"{ERR_SOURCE_MISSING}: {path}")
        s = set()
        with open(path, encoding="latin-1") as f:
            for line in f:
                if not line or line[0].isspace():
                    continue  # license line
                lemma = line.split(" ", 1)[0].lower()
                if lemma:
                    s.add(lemma)
        per_pos[pos] = s
        union |= s
    return per_pos, union


def load_exc():
    """Return {pos -> {inflected -> [base,...]}} from the .exc files."""
    exc = {}
    for pos, path in EXC_FILES.items():
        d = {}
        if os.path.exists(path):
            with open(path, encoding="latin-1") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        d[parts[0].lower()] = [p.lower() for p in parts[1:]]
        exc[pos] = d
    return exc


# ---------------------------------------------------------------------------
# Morphy-lite (PREREG §2.3). Detachment rules verbatim from §2.3 step 3.
# ---------------------------------------------------------------------------

DETACH = {
    "noun": [("s", ""), ("ses", "s"), ("xes", "x"), ("zes", "z"),
             ("ches", "ch"), ("shes", "sh"), ("men", "man"), ("ies", "y")],
    "verb": [("s", ""), ("ies", "y"), ("es", "e"), ("es", ""),
             ("ed", "e"), ("ed", ""), ("ing", "e"), ("ing", "")],
    "adj": [("er", ""), ("est", ""), ("er", "e"), ("est", "e")],
}
_DETACH_POS_ORDER = ["noun", "verb", "adj"]
_EXC_POS_ORDER = ["noun", "verb", "adj", "adv"]


class Morphy:
    """PREREG §2.3: exact -> exception -> detachment -> drop (first hit wins)."""

    def __init__(self, per_pos, union, exc):
        self.per_pos = per_pos
        self.union = union
        self.exc = exc

    def resolve(self, token):
        """Resolve a single (already lowercased, [a-z'-], len>=2) token.

        Returns a lemma string in the index vocabulary, or None (OOV)."""
        # 1. Exact match in union index vocabulary.
        if token in self.union:
            return token
        # 2. Exception lists, POS order noun,verb,adj,adv; base accepted if in union.
        for pos in _EXC_POS_ORDER:
            bases = self.exc[pos].get(token)
            if bases:
                for b in bases:
                    if b in self.union:
                        return b
        # 3. Detachment rules, POS order noun->verb->adj; candidate in THAT POS index.
        for pos in _DETACH_POS_ORDER:
            idx = self.per_pos[pos]
            for suf, rep in DETACH[pos]:
                if token.endswith(suf):
                    cand = token[: len(token) - len(suf)] + rep
                    if cand and cand in idx:
                        return cand
        # 4. Drop.
        return None

    def resolve_token(self, token):
        """Full token resolution incl. §2.2 hyphen fallback.

        Returns list of lemma strings (0..n). Empty list => fully OOV."""
        lem = self.resolve(token)
        if lem is not None:
            return [lem]
        if "-" in token:
            out = []
            for part in token.split("-"):
                if len(part) < 2:
                    continue
                pl = self.resolve(part)
                if pl is not None:
                    out.append(pl)
            return out
        return []


# ---------------------------------------------------------------------------
# Gloss cleaning + tokenization (PREREG §2.1, §2.2).
# ---------------------------------------------------------------------------

_QUOTED_SPAN = re.compile(r'"[^"]*"')
_SPLIT = re.compile(r"[^a-z'-]+")


def clean_gloss(gloss):
    """PREREG §2.1. Returns cleaned gloss string (may be empty)."""
    kept = []
    for seg in gloss.split(";"):
        if seg.lstrip().startswith('"'):
            continue  # usage example segment
        kept.append(_QUOTED_SPAN.sub("", seg))  # drop any inline quoted span
    return " ".join(kept)


def tokenize(cleaned):
    """PREREG §2.2. Returns list of raw tokens (lowercased, len>=2, no digit).

    Possessive/trailing apostrophe stripped per token (equivalent to the
    listed order; possessive only occurs at token boundaries)."""
    toks = []
    for t in _SPLIT.split(cleaned.lower()):
        if not t:
            continue
        if t.endswith("'s"):
            t = t[:-2]
        elif t.endswith("'"):
            t = t[:-1]
        if len(t) < 2:
            continue
        if any(c.isdigit() for c in t):  # defensive; digits already are separators
            continue
        toks.append(t)
    return toks


# ---------------------------------------------------------------------------
# Graph primitives (all iterative; PREREG §4.1, §4.2, §4.4, §7).
# Graphs are int-interned: out_adj/in_adj are lists indexed by node id.
# ---------------------------------------------------------------------------

def tarjan_scc(nodes, out_adj, alive=None):
    """Iterative Tarjan SCC (PREREG §4.2). 10^5 nodes exceed recursion limit.

    `nodes`      : iterable of node ids to consider.
    `out_adj`    : full out-adjacency (list of lists); neighbours outside the
                   considered/alive set are skipped.
    `alive`      : optional set restricting which node ids are in the subgraph.
    Returns list of components (each a list of ids). Order is deterministic
    given the iteration order of `nodes`."""
    consider = set(nodes) if alive is None else (set(nodes) & alive)
    index_of = {}
    low = {}
    on_stack = set()
    stack = []
    result = []
    counter = 0
    for root in nodes:
        if root in index_of or root not in consider:
            continue
        # work stack of (node, neighbour-iterator-position)
        work = [(root, 0)]
        neigh_cache = {}
        while work:
            v, pi = work[-1]
            if pi == 0:
                index_of[v] = counter
                low[v] = counter
                counter += 1
                stack.append(v)
                on_stack.add(v)
                # SCC partition is canonical regardless of neighbour order; skip
                # the O(deg log deg) sort (hot path over the ~17k-node core).
                neigh_cache[v] = [w for w in out_adj[v] if w in consider]
            neigh = neigh_cache[v]
            if pi < len(neigh):
                work[-1] = (v, pi + 1)
                w = neigh[pi]
                if w not in index_of:
                    work.append((w, 0))
                elif w in on_stack:
                    if index_of[w] < low[v]:
                        low[v] = index_of[w]
            else:
                if low[v] == index_of[v]:
                    comp = []
                    while True:
                        u = stack.pop()
                        on_stack.discard(u)
                        comp.append(u)
                        if u == v:
                            break
                    result.append(comp)
                work.pop()
                if work:
                    parent = work[-1][0]
                    if low[v] < low[parent]:
                        low[parent] = low[v]
        neigh_cache.clear()
    return result


def is_acyclic(nodes, out_adj, alive=None):
    """Kahn's algorithm (PREREG §4.4 step 5 / §4.2). True iff DAG on subset."""
    consider = set(nodes) if alive is None else (set(nodes) & alive)
    indeg = {v: 0 for v in consider}
    for v in consider:
        for w in out_adj[v]:
            if w in consider:
                indeg[w] += 1
    queue = [v for v in consider if indeg[v] == 0]
    removed = 0
    while queue:
        v = queue.pop()
        removed += 1
        for w in out_adj[v]:
            if w in consider:
                indeg[w] -= 1
                if indeg[w] == 0:
                    queue.append(w)
    return removed == len(consider)


def kernel_peel(n, out_adj, in_adj):
    """PREREG §4.1. Repeatedly delete out-degree-0 vertices to fixpoint.

    Returns set of kernel node ids. O(V+E) worklist."""
    outdeg = [len(out_adj[v]) for v in range(n)]
    removed = bytearray(n)
    queue = [v for v in range(n) if outdeg[v] == 0]
    while queue:
        w = queue.pop()
        if removed[w]:
            continue
        removed[w] = 1
        for u in in_adj[w]:
            if not removed[u]:
                outdeg[u] -= 1
                if outdeg[u] == 0:
                    queue.append(u)
    return {v for v in range(n) if not removed[v]}
