#!/usr/bin/env python3
"""g8_fragment — profile-M pm-ast/1 fragment machinery for experiment g8 (HS8/NF3).

Library used by tools/experiments/g8_instrument.py. Implements, deterministically
and fail-closed, the four objects the frozen g8 record needs an instrument for
(docs/design-dl-from-nsm-and-lean-reconstruction.md §5.3; docs/design-math-sector.md §3):

  1. FORWARD MAP F (signature layer): doc-gen4 `signaturePretty` string ->
     canonical pm-ast/1 statement (de Bruijn, closed grammar, caps, sort-checked).
     Partial by design: any construct outside profile-M's closed two-sorted-PA
     grammar raises Reject(code) — the reason codes are the fragment-gate output.
  2. FRAGMENT GATE: membership = "F succeeds on this declaration's statement".
     Only statement-bearing kinds (theorem/axiom/lemma) can pass at this layer:
     a def/abbrev/instance body is NOT visible in doc-gen4 signatures, so def-kind
     declarations are counted OUT with reason `definiens-unavailable-at-layer`
     (conservative undercount of the fragment; see ASM notes in the instrument).
  3. DETERMINISTIC RENDERERS (backward map B, statement layer):
     render_lean  — pm-ast -> Lean-fragment surface syntax that F's own parser
                    re-consumes (round-trip F(B(K)) = K is checked through the
                    identical production parser, not a shadow one);
     render_neutral — pm-ast -> notation-neutral text for the LLM location
                    prompts (math-v0 slugs, no Mathlib names leaked).
  4. PROBE DERIVATION: each of the 39 math-v0 concepts -> its verification probe:
       AxiomDef              -> the statement itself;
       PredicateDef          -> forall-closure of  iff(const c(params), definiens);
       TermDef               -> forall-closure of  eq(const c(params), definiens);
       RecursiveFunctionDef  -> BOTH defining equations (base + step), each a
                                closed forall statement (all must be covered);
       Primitive             -> anchor mode: the pinned Lean face name
                                (weaker verification — instrument-authored table).
     Admissible-match set per statement = {canonical form, top-level eq/iff
     operand swap} and NOTHING else: the swap covers Mathlib's authorial
     orientation convention for characterisation lemmas; no other logical
     equivalence is admitted (design-math-sector §3.4: identity is the stated
     form; the swap is a pre-declared property of the location-verification
     PREDICATE, not of record identity).

Honesty pins (each a deliberate NON-canonicalisation, mirroring §3.4):
  * `n + 1` is add(n, one), never succ(n): defeq is not surface syntax.
  * iff != implies; A=B != B=A except the single pre-declared top-level swap.
  * unbridged constants (Nat.gcd, general `Prime`, coercions, typeclasses,
    Function.Injective, ...) reject — the fragment is exactly what the pinned
    face table + closed grammar reach, and every rejection carries its reason.

Zero dependencies beyond the stdlib. No RNG anywhere in this module. Every
canonical form is json.dumps(sort_keys=True, separators=(",", ":")) over the
same node shapes data/math-v0/validate.mjs checks; the sort checker mirrors
validate.mjs rule-for-rule (same caps, same vacuous-binder rejection).
"""

import json
import hashlib
import os
import unicodedata

# ---------------------------------------------------------------- caps (design-math-sector §3.3)
CAPS = {"maxNodes": 256, "maxBinderDepth": 12, "maxParams": 6,
        "maxSortDepth": 4, "maxRefs": 16}

PROP = "Prop"  # sentinel; never a legal pm-ast sort value ("N" / Set / Pair only)

U = "urn:math-v0:"  # concept URN prefix (data/math-v0)


class Reject(Exception):
    """Out-of-fragment (or malformed input). `.code` is the gate reason."""

    def __init__(self, code, msg=""):
        super().__init__("%s: %s" % (code, msg))
        self.code = code
        self.msg = msg


# ---------------------------------------------------------------- sorts

def sort_depth(s):
    if s == "N":
        return 1
    if isinstance(s, dict) and s.get("kind") == "Set":
        return 1 + sort_depth(s["of"])
    if isinstance(s, dict) and s.get("kind") == "Pair":
        return 1 + max(sort_depth(s["fst"]), sort_depth(s["snd"]))
    raise Reject("node-shape", "bad sort %r" % (s,))


def show_sort(s):
    if s == "N":
        return "N"
    if s.get("kind") == "Set":
        return "Set(%s)" % show_sort(s["of"])
    return "Pair(%s,%s)" % (show_sort(s["fst"]), show_sort(s["snd"]))


# ---------------------------------------------------------------- canonical form

def canonical(term):
    return json.dumps(term, sort_keys=True, separators=(",", ":"))


def content_sha(term):
    return hashlib.sha256(canonical(term).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- math-v0 corpus

def load_math_v0(root):
    """Load the 39 concept records; returns {urn: record} (insertion = sorted files)."""
    cdir = os.path.join(root, "data", "math-v0", "concepts")
    out = {}
    for fn in sorted(os.listdir(cdir)):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(cdir, fn), "r", encoding="utf-8") as f:
            rec = json.load(f)
        out[rec["id"]] = rec
    return out


def const_signature(rec):
    """(params, result) for const-referenceable frames; None if unreferenceable."""
    d = rec["definition"]
    frame = d["frame"]
    if frame == "TermDef":
        return d["params"], d["resultSort"]
    if frame == "PredicateDef":
        return d["params"], PROP
    if frame == "RecursiveFunctionDef":
        return d["params"], d["resultSort"]
    return None  # Primitive / AxiomDef: cannot be const-applied (validate.mjs)


# ---------------------------------------------------------------- checker (mirrors validate.mjs)

def check_statement(term, concepts):
    """Full profile-M check of a CLOSED Prop statement. Raises Reject on any
    violation; returns {"nodes": int, "refs": int} on success."""
    state = {"nodes": 0, "used": set(), "refs": set(), "maxdepth": 0}
    got = _check(term, [], state, concepts)
    if got is not PROP:
        raise Reject("sort", "statement is not Prop (got %s)"
                     % (show_sort(got) if got is not PROP else "Prop"))
    if state["nodes"] > CAPS["maxNodes"]:
        raise Reject("caps", "node count %d > %d" % (state["nodes"], CAPS["maxNodes"]))
    if len(state["refs"]) > CAPS["maxRefs"]:
        raise Reject("caps", "refs %d > %d" % (len(state["refs"]), CAPS["maxRefs"]))
    return {"nodes": state["nodes"], "refs": len(state["refs"])}


def _binary_prop(t, ctx, state, concepts):
    for side in ("left", "right"):
        a = _check(t[side], ctx, state, concepts)
        if a is not PROP:
            raise Reject("sort", "%s over non-Prop" % t["kind"])
    return PROP


def _check(t, ctx, state, concepts):
    if not isinstance(t, dict) or "kind" not in t:
        raise Reject("node-shape", "term is not a node: %r" % (t,))
    state["nodes"] += 1
    k = t["kind"]
    if k == "var":
        i = t.get("index")
        if not isinstance(i, int) or i < 0 or i >= len(ctx):
            raise Reject("node-shape", "var index %r out of scope" % (i,))
        state["used"].add(len(ctx) - 1 - i)  # absolute binder id (validate.mjs)
        return ctx[i]
    if k == "zero":
        return "N"
    if k == "succ":
        a = _check(t["arg"], ctx, state, concepts)
        if a != "N":
            raise Reject("sort", "succ needs N")
        return "N"
    if k == "eq":
        l = _check(t["left"], ctx, state, concepts)
        r = _check(t["right"], ctx, state, concepts)
        if l is PROP or r is PROP or l != r:
            raise Reject("sort", "eq operand sort mismatch")
        return PROP
    if k == "member":
        e = _check(t["element"], ctx, state, concepts)
        s = _check(t["set"], ctx, state, concepts)
        if s is PROP or s == "N" or s.get("kind") != "Set":
            raise Reject("sort", "member's set operand is not a Set sort")
        if e is PROP or s["of"] != e:
            raise Reject("sort", "member element/set sort mismatch")
        return PROP
    if k == "pair":
        a = _check(t["fst"], ctx, state, concepts)
        b = _check(t["snd"], ctx, state, concepts)
        if a is PROP or b is PROP:
            raise Reject("sort", "pair of Prop")
        s = {"kind": "Pair", "fst": a, "snd": b}
        if sort_depth(s) > CAPS["maxSortDepth"]:
            raise Reject("caps", "sort depth")
        return s
    if k in ("fst", "snd"):
        a = _check(t["arg"], ctx, state, concepts)
        if a is PROP or a == "N" or a.get("kind") != "Pair":
            raise Reject("sort", "%s needs a Pair sort" % k)
        return a["fst"] if k == "fst" else a["snd"]
    if k == "not":
        a = _check(t["arg"], ctx, state, concepts)
        if a is not PROP:
            raise Reject("sort", "not over non-Prop")
        return PROP
    if k in ("and", "or", "implies", "iff"):
        return _binary_prop(t, ctx, state, concepts)
    if k in ("forall", "exists", "comprehension"):
        s = t.get("sort")
        if sort_depth(s) > CAPS["maxSortDepth"]:
            raise Reject("caps", "sort depth")
        if len(ctx) + 1 > CAPS["maxBinderDepth"]:
            raise Reject("caps", "binder depth > %d" % CAPS["maxBinderDepth"])
        binder_id = len(ctx)
        body = _check(t["body"], [s] + ctx, state, concepts)
        if body is not PROP:
            raise Reject("sort", "%s body is not Prop" % k)
        if binder_id not in state["used"]:
            raise Reject("vacuous-binder", "%s binds no occurrence" % k)
        return {"kind": "Set", "of": s} if k == "comprehension" else PROP
    if k == "const":
        ref = t.get("ref")
        rec = concepts.get(ref)
        if rec is None:
            raise Reject("unknown-ref", "%r" % (ref,))
        sig = const_signature(rec)
        if sig is None:
            raise Reject("ref-frame", "%s cannot be const-applied" % ref)
        params, result = sig
        args = t.get("args")
        if not isinstance(args, list) or len(args) != len(params):
            raise Reject("node-shape", "const %s arity" % ref)
        for a, want in zip(args, params):
            got = _check(a, ctx, state, concepts)
            if got is PROP or got != want:
                raise Reject("sort", "const %s argument sort" % ref)
        state["refs"].add(ref)
        return result
    raise Reject("node-shape", "unknown node kind %r" % (k,))


# ---------------------------------------------------------------- de Bruijn utilities

def _shift(t, by, cutoff=0):
    k = t["kind"]
    if k == "var":
        i = t["index"]
        return {"kind": "var", "index": i + by} if i >= cutoff else t
    return _map_children(t, lambda c, extra: _shift(c, by, cutoff + extra))


def _map_children(t, f):
    """Apply f(child, binders_crossed) to each child term of t."""
    k = t["kind"]
    out = dict(t)
    if k == "succ" or k == "not" or k in ("fst", "snd"):
        out["arg"] = f(t["arg"], 0)
    elif k == "eq" or k in ("and", "or", "implies", "iff"):
        out["left"] = f(t["left"], 0)
        out["right"] = f(t["right"], 0)
    elif k == "member":
        out["element"] = f(t["element"], 0)
        out["set"] = f(t["set"], 0)
    elif k == "pair":
        out["fst"] = f(t["fst"], 0)
        out["snd"] = f(t["snd"], 0)
    elif k in ("forall", "exists", "comprehension"):
        out["body"] = f(t["body"], 1)
    elif k == "const":
        out["args"] = [f(a, 0) for a in t["args"]]
    return out


def subst_var0(t, repl, depth=0):
    """Substitute var(depth) := repl (repl expressed in the OUTER context),
    downshifting the remaining free vars above it."""
    k = t["kind"]
    if k == "var":
        i = t["index"]
        if i == depth:
            return _shift(repl, depth, 0)
        if i > depth:
            return {"kind": "var", "index": i - 1}
        return t
    return _map_children(t, lambda c, extra: subst_var0(c, repl, depth + extra))


# ---------------------------------------------------------------- probe derivation

def _forall_close(params, body):
    for s in reversed(params):
        body = {"kind": "forall", "sort": s, "body": body}
    return body


def _param_vars(k):
    """const args for params p0..p_{k-1} seen from inside k foralls."""
    return [{"kind": "var", "index": k - 1 - i} for i in range(k)]


# Pinned Lean face names for the 9 Primitive records (anchor-mode verification;
# instrument-authored — see ASM g8-primitive-anchor in the instrument docstring).
PRIM_ANCHORS = {
    U + "natural-number": ["Nat"],
    U + "zero": ["Nat.zero"],
    U + "successor": ["Nat.succ"],
    U + "equality": ["Eq"],
    U + "set-membership": ["Membership.mem"],
    U + "ordered-pair": ["Prod.mk"],
    U + "pair-first": ["Prod.fst"],
    U + "pair-second": ["Prod.snd"],
    U + "set-of": ["Set"],
}


def _swap_variants(stmt):
    """Admissible canonical shas: the statement + (iff/eq head under the forall
    prefix) operand-swapped. Nothing else."""
    shas = [content_sha(stmt)]
    # descend the forall prefix only
    spine = []
    t = stmt
    while t["kind"] == "forall":
        spine.append(t)
        t = t["body"]
    if t["kind"] in ("eq", "iff"):
        swapped = dict(t)
        swapped["left"], swapped["right"] = t["right"], t["left"]
        for q in reversed(spine):
            swapped = {"kind": "forall", "sort": q["sort"], "body": swapped}
        sha = content_sha(swapped)
        if sha not in shas:
            shas.append(sha)
    return shas


def probe_statements(rec, concepts):
    """The concept's verification statements (deterministic function of the
    record). Returns [] for Primitives (anchor mode)."""
    d = rec["definition"]
    frame = d["frame"]
    urn = rec["id"]
    if frame == "Primitive":
        return []
    if frame == "AxiomDef":
        return [d["statement"]]
    if frame == "PredicateDef":
        k = len(d["params"])
        head = {"kind": "const", "ref": urn, "args": _param_vars(k)}
        body = {"kind": "iff", "left": head, "right": d["definiens"]}
        return [_forall_close(d["params"], body)]
    if frame == "TermDef":
        k = len(d["params"])
        head = {"kind": "const", "ref": urn, "args": _param_vars(k)}
        body = {"kind": "eq", "left": head, "right": d["definiens"]}
        return [_forall_close(d["params"], body)]
    if frame == "RecursiveFunctionDef":
        params = d["params"]  # last is the recursion argument, sort N
        k = len(params)
        front = params[:-1]
        # base: forall p0..p_{k-2}, c(p..., 0) = baseCase   (baseCase ctx = front)
        base_lhs = {"kind": "const", "ref": urn,
                    "args": _param_vars(k - 1) + [{"kind": "zero"}]}
        base = _forall_close(front, {"kind": "eq", "left": base_lhs,
                                     "right": d["baseCase"]})
        # step: forall p0..p_{k-2} n, c(p..., succ n) = stepCase[rec := c(p..., n)]
        # target ctx [p0..p_{k-2}, n]: n = var0, p_i = var(k-1-i)
        pv = [{"kind": "var", "index": k - 1 - i} for i in range(k - 1)]
        step_lhs = {"kind": "const", "ref": urn,
                    "args": pv + [{"kind": "succ", "arg": {"kind": "var", "index": 0}}]}
        rec_call = {"kind": "const", "ref": urn, "args": pv + [{"kind": "var", "index": 0}]}
        step_rhs = subst_var0(d["stepCase"], rec_call)  # rec (idx 0) := c(p..., n)
        step = _forall_close(front + ["N"], {"kind": "eq", "left": step_lhs,
                                             "right": step_rhs})
        return [base, step]
    raise Reject("node-shape", "unknown frame %r" % frame)


def build_probes(concepts):
    """All 39 targets, sorted by URN. Each: {urn, frame, mode, statements,
    admissible (list-of-sha-lists, aligned with statements), anchors}."""
    out = []
    for urn in sorted(concepts):
        rec = concepts[urn]
        stmts = probe_statements(rec, concepts)
        for s in stmts:  # every derived probe must itself be legal profile-M
            check_statement(s, concepts)
        mode = "anchor" if rec["definition"]["frame"] == "Primitive" else "statement"
        out.append({
            "urn": urn,
            "frame": rec["definition"]["frame"],
            "mode": mode,
            "statements": stmts,
            "admissible": [_swap_variants(s) for s in stmts],
            "anchors": PRIM_ANCHORS.get(urn, []),
        })
    return out


# ---------------------------------------------------------------- Lean surface: faces

# const faces: pretty-name -> (urn, arity). NO defeq aliases (no "+1 = succ").
CONST_FACES = {
    "Nat.add": (U + "addition", 2),
    "Nat.mul": (U + "multiplication", 2),
    "Nat.pred": (U + "predecessor", 1),
    "Nat.le": (U + "less-or-equal", 2),
    "Nat.lt": (U + "less-than", 2),
    "Even": (U + "even", 1),
    "Odd": (U + "odd", 1),
    "Nat.Prime": (U + "prime-number", 1),
    "Dvd.dvd": (U + "divides", 2),
}
# synthetic faces for math-v0 consts with no honest Lean notation face; these
# exist ONLY so render_lean output is closed under the parser (round-trip).
# Real Mathlib signatures never contain "KOT." names.
_KOT_FACES = [
    "divides", "even", "odd", "less-or-equal", "less-than", "prime-number",
    "one", "two", "three", "predecessor", "addition", "multiplication",
    "empty-set-nat", "singleton-nat", "subset-nat", "union-nat",
    "intersection-nat", "function-on-nat", "injective-on-nat",
    "int-pair-equiv", "integer", "integer-zero", "integer-one",
    "integer-negation",
]

# infix operator -> ("const", urn) | ("eq",) | ("member",) | flavour markers
INFIX_CMP = {
    "=": ("eq",),
    "≠": ("ne",),
    "≤": ("const", U + "less-or-equal", False),
    "<": ("const", U + "less-than", False),
    "≥": ("const", U + "less-or-equal", True),   # a ≥ b is notation for b ≤ a
    ">": ("const", U + "less-than", True),       # a > b is notation for b < a
    "∣": ("const", U + "divides", False),
    "∈": ("member", False),
    "∉": ("member", True),
    "⊆": ("const", U + "subset-nat", False),
}
FORMER_IDENTS = {
    "Nat.succ": ("succ", 1),
    "Nat.zero": ("zero", 0),
    "Prod.fst": ("fst", 1),
    "Prod.snd": ("snd", 1),
    "Prod.mk": ("pair", 2),
    "Eq": ("eq", 2),
    "Ne": ("ne", 2),
    "Not": ("not", 1),
    "Iff": ("iff", 2),
    "And": ("and", 2),
    "Or": ("or", 2),
}
POSTFIX = {"succ": ("succ",), "pred": ("constref", U + "predecessor"),
           "fst": ("fst",), "snd": ("snd",), "1": ("fst",), "2": ("snd",)}

NUMERALS = {"0": lambda: {"kind": "zero"},
            "1": lambda: {"kind": "const", "ref": U + "one", "args": []},
            "2": lambda: {"kind": "const", "ref": U + "two", "args": []},
            "3": lambda: {"kind": "const", "ref": U + "three", "args": []}}

STATEMENT_KINDS = ("theorem", "axiom", "lemma")
DEF_KINDS = ("def", "abbrev", "instance", "opaque", "noncomputable def",
             "noncomputable instance", "noncomputable abbrev", "partial def",
             "unsafe def", "irreducible_def")
_SYM_CHARS = set("(){}[],:|∀∃∧∨¬→↔=≠≤<>≥∈∉⊆⊂∪∩∅∣+*×.⟨⟩⦃⦄↑↓⁻¹∑∏∘⊤⊥≈≡∞λ%^/-@⨆⨅≫≪⟶⥤")


def _is_ident_char(c):
    if c.isalnum() or c in "_'!?✝ₐₓᵢ":
        return True
    cat = unicodedata.category(c)
    return cat.startswith("L") or cat in ("No", "Mn")


def tokenize(text):
    toks = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
            continue
        if c.isdigit():
            j = i
            while j < n and text[j].isdigit():
                j += 1
            toks.append(("num", text[i:j]))
            i = j
            continue
        if _is_ident_char(c):
            j = i
            while j < n and (_is_ident_char(text[j])
                             or (text[j] == "." and j + 1 < n and _is_ident_char(text[j + 1])
                                 and not text[j + 1].isdigit())):
                j += 1
            toks.append(("ident", text[i:j]))
            i = j
            continue
        if c in _SYM_CHARS:
            toks.append(("sym", c))
            i += 1
            continue
        raise Reject("unsupported-token", repr(c))
    return toks


# ---------------------------------------------------------------- Lean surface: parser

class _P:
    """Recursive-descent parser over the fragment surface. env = binder names,
    innermost FIRST (env[0] = de Bruijn 0)."""

    def __init__(self, toks, concepts, env=None):
        self.t = toks
        self.i = 0
        self.concepts = concepts
        self.env = list(env or [])
        # '-' is not an identifier char in the surface lexer: synthetic faces
        # use '_' (KOT.less_or_equal <-> urn:math-v0:less-or-equal)
        self.kot_faces = {"KOT." + slug.replace("-", "_"): (U + slug,)
                          for slug in _KOT_FACES}

    # --- token helpers
    def peek(self, k=0):
        j = self.i + k
        return self.t[j] if j < len(self.t) else (None, None)

    def next(self):
        tok = self.peek()
        self.i += 1
        return tok

    def eat_sym(self, s):
        if self.peek() != ("sym", s):
            got = self.peek()[1]
            if got is not None and got in UNBRIDGED_OPS:
                raise Reject("unbridged-operator", "at token %r" % (got,))
            raise Reject("parse", "expected %r got %r" % (s, got))
        self.i += 1

    def at_sym(self, s):
        return self.peek() == ("sym", s)

    # --- sorts
    def parse_sort(self):
        left = self._sort_atom()
        if self.at_sym("×"):
            self.i += 1
            right = self.parse_sort()  # × is right-associative
            return {"kind": "Pair", "fst": left, "snd": right}
        return left

    def _sort_atom(self):
        typ, val = self.peek()
        if typ == "ident" and val in ("ℕ", "Nat"):
            self.i += 1
            return "N"
        if typ == "ident" and val == "Set":
            self.i += 1
            return {"kind": "Set", "of": self._sort_atom()}
        if typ == "sym" and val == "(":
            self.i += 1
            s = self.parse_sort()
            self.eat_sym(")")
            return s
        raise Reject("binder-sort", "not a fragment sort at %r" % (val,))

    # --- expressions (loosest to tightest)
    def parse_prop(self):
        return self._iff()

    def _iff(self):
        left = self._arrow()
        if self.at_sym("↔"):
            self.i += 1
            return {"kind": "iff", "left": left, "right": self._iff()}
        return left

    def _arrow(self):
        left = self._or()
        if self.at_sym("→"):
            self.i += 1
            return {"kind": "implies", "left": left, "right": self._arrow()}
        return left

    def _or(self):
        left = self._and()
        if self.at_sym("∨"):
            self.i += 1
            return {"kind": "or", "left": left, "right": self._or()}
        return left

    def _and(self):
        left = self._not()
        if self.at_sym("∧"):
            self.i += 1
            return {"kind": "and", "left": left, "right": self._and()}
        return left

    def _not(self):
        if self.at_sym("¬"):
            self.i += 1
            return {"kind": "not", "arg": self._not()}
        return self._cmp()

    def _cmp(self):
        left = self._union()
        typ, val = self.peek()
        if typ == "sym" and val in INFIX_CMP:
            self.i += 1
            right = self._union()
            return self._mk_cmp(val, left, right)
        return left

    def _mk_cmp(self, op, left, right):
        spec = INFIX_CMP[op]
        if spec[0] == "eq":
            return {"kind": "eq", "left": left, "right": right}
        if spec[0] == "ne":
            return {"kind": "not", "arg": {"kind": "eq", "left": left, "right": right}}
        if spec[0] == "member":
            node = {"kind": "member", "element": left, "set": right}
            return {"kind": "not", "arg": node} if spec[1] else node
        _, urn, flip = spec
        args = [right, left] if flip else [left, right]
        return {"kind": "const", "ref": urn, "args": args}

    def _union(self):
        left = self._inter()
        while self.at_sym("∪"):
            self.i += 1
            left = {"kind": "const", "ref": U + "union-nat",
                    "args": [left, self._inter()]}
        return left

    def _inter(self):
        left = self._add()
        while self.at_sym("∩"):
            self.i += 1
            left = {"kind": "const", "ref": U + "intersection-nat",
                    "args": [left, self._add()]}
        return left

    def _add(self):
        left = self._mul()
        while self.at_sym("+"):
            self.i += 1
            left = {"kind": "const", "ref": U + "addition",
                    "args": [left, self._mul()]}
        return left

    def _mul(self):
        left = self._app()
        while self.at_sym("*"):
            self.i += 1
            left = {"kind": "const", "ref": U + "multiplication",
                    "args": [left, self._app()]}
        return left

    def _app(self):
        head = self._primary()
        while True:
            if self.at_sym("."):  # postfix: (e).succ / p.1 ...
                self.i += 1
                typ, val = self.next()
                if typ not in ("ident", "num") or val not in POSTFIX:
                    raise Reject("unmapped-constant", "postfix .%s" % val)
                head = self._finish(head if isinstance(head, dict) else self._force(head))
                head = self._apply_postfix(head, val)
                continue
            if isinstance(head, tuple) and head[0] == "pending":
                # collect the pending face's args from following primaries
                _, builder, arity, got = head
                if len(got) < arity and self._starts_primary():
                    got = got + [self._force(self._app_arg())]
                    head = ("pending", builder, arity, got)
                    if len(got) == arity:
                        head = builder(got)
                    continue
                if len(got) < arity:
                    raise Reject("partial-application", "face missing arguments")
            elif self._starts_primary():
                raise Reject("application-of-non-face",
                             "cannot apply a fragment term to arguments")
            return self._finish(head)

    def _app_arg(self):
        """One application argument (tightest level: primary + its postfixes)."""
        arg = self._primary()
        while self.at_sym("."):
            self.i += 1
            typ, val = self.next()
            if typ not in ("ident", "num") or val not in POSTFIX:
                raise Reject("unmapped-constant", "postfix .%s" % val)
            arg = self._apply_postfix(self._force(arg), val)
        return arg

    def _finish(self, head):
        if isinstance(head, tuple):
            if head[0] == "pending":
                _, builder, arity, got = head
                if len(got) != arity:
                    raise Reject("partial-application", "face missing arguments")
                return builder(got)
        return head

    def _force(self, h):
        return self._finish(h)

    def _apply_postfix(self, base, val):
        spec = POSTFIX[val]
        if spec[0] == "succ":
            return {"kind": "succ", "arg": base}
        if spec[0] == "fst":
            return {"kind": "fst", "arg": base}
        if spec[0] == "snd":
            return {"kind": "snd", "arg": base}
        return {"kind": "const", "ref": spec[1], "args": [base]}

    def _starts_primary(self):
        typ, val = self.peek()
        if typ in ("ident", "num"):
            return True
        return typ == "sym" and val in ("(", "{", "∅")

    def _face_builder(self, name):
        """None, or ('pending', builder, arity, []) for a face identifier."""
        if name in CONST_FACES:
            urn, arity = CONST_FACES[name]
            return ("pending",
                    lambda args, u=urn: {"kind": "const", "ref": u, "args": args},
                    arity, [])
        if name in self.kot_faces:
            urn = self.kot_faces[name][0]
            params, _ = const_signature(self.concepts[urn])
            arity = len(params)
            if arity == 0:
                return {"kind": "const", "ref": urn, "args": []}
            return ("pending",
                    lambda args, u=urn: {"kind": "const", "ref": u, "args": args},
                    arity, [])
        if name in FORMER_IDENTS:
            former, arity = FORMER_IDENTS[name]
            def build(args, f=former):
                if f == "succ":
                    return {"kind": "succ", "arg": args[0]}
                if f == "zero":
                    return {"kind": "zero"}
                if f == "fst" or f == "snd":
                    return {"kind": f, "arg": args[0]}
                if f == "pair":
                    return {"kind": "pair", "fst": args[0], "snd": args[1]}
                if f == "eq":
                    return {"kind": "eq", "left": args[0], "right": args[1]}
                if f == "ne":
                    return {"kind": "not", "arg": {"kind": "eq", "left": args[0],
                                                   "right": args[1]}}
                if f == "not":
                    return {"kind": "not", "arg": args[0]}
                return {"kind": f, "left": args[0], "right": args[1]}
            if arity == 0:
                return build([])
            return ("pending", build, arity, [])
        return None

    def _primary(self):
        typ, val = self.peek()
        if typ == "num":
            self.i += 1
            if val in NUMERALS:
                return NUMERALS[val]()
            raise Reject("numeral-out-of-range", val)
        if typ == "ident":
            self.i += 1
            if val in self.env:
                return {"kind": "var", "index": self.env.index(val)}
            fb = self._face_builder(val)
            if fb is not None:
                return fb
            if "." in val:  # receiver.method dot-notation: n.succ, p.fst ...
                head, rest = val.split(".", 1)
                if head in self.env:
                    base = {"kind": "var", "index": self.env.index(head)}
                    for seg in rest.split("."):
                        if seg not in POSTFIX:
                            raise Reject("unmapped-constant", "postfix .%s" % seg)
                        base = self._apply_postfix(base, seg)
                    return base
            raise Reject("unmapped-constant", val)
        if typ == "sym" and val == "∅":
            self.i += 1
            return {"kind": "const", "ref": U + "empty-set-nat", "args": []}
        if typ == "sym" and val in ("∀", "∃"):
            return self._quantifier(val)
        if typ == "sym" and val == "(":
            self.i += 1
            inner = self._force(self.parse_prop())
            if self.at_sym(","):  # pair literal (a, b[, c ...]) right-folded
                self.i += 1
                snd = self._force(self.parse_prop())
                while self.at_sym(","):
                    self.i += 1
                    snd = {"kind": "pair", "fst": snd,
                           "snd": self._force(self.parse_prop())}
                inner = {"kind": "pair", "fst": inner, "snd": snd}
            elif self.at_sym(":"):  # type ascription — parse the sort, discard
                self.i += 1
                self.parse_sort()
            self.eat_sym(")")
            return inner
        if typ == "sym" and val == "{":
            return self._brace()
        raise Reject("parse", "unexpected token %r" % (val,))

    def _brace(self):
        self.eat_sym("{")
        # comprehension {x | P} / {x : S | P}, else singleton {e}
        typ, val = self.peek()
        if typ == "ident":
            nxt = self.peek(1)
            if nxt == ("sym", "|") or nxt == ("sym", ":"):
                name = val
                self.i += 1
                sort = "N"
                if self.at_sym(":"):
                    self.i += 1
                    sort = self.parse_sort()
                self.eat_sym("|")
                self.env.insert(0, name)
                body = self._force(self.parse_prop())
                self.env.pop(0)
                self.eat_sym("}")
                return {"kind": "comprehension", "sort": sort, "body": body}
        elem = self._force(self.parse_prop())
        self.eat_sym("}")
        return {"kind": "const", "ref": U + "singleton-nat", "args": [elem]}

    _BOUND_OPS = ("∈", "≤", "<", ">", "≥", "≠", "⊆")

    def _quantifier(self, q):
        self.i += 1
        groups = []  # (names, sort) in binder order
        bound = None  # (op, term) sugar: ∀ x ∈ s, P
        while True:
            typ, val = self.peek()
            if typ == "sym" and val in ("(", "{", "⦃"):
                close = {"(": ")", "{": "}", "⦃": "⦄"}[val]
                self.i += 1
                names = []
                while self.peek()[0] == "ident":
                    names.append(self.next()[1])
                if not names:
                    raise Reject("parse", "empty quantifier group")
                sort = "N"
                if self.at_sym(":"):
                    self.i += 1
                    sort = self.parse_sort()
                self.eat_sym(close)
                groups.append((names, sort))
                continue
            if typ == "ident":
                names = []
                while self.peek()[0] == "ident":
                    names.append(self.next()[1])
                sort = "N"
                if self.at_sym(":"):
                    self.i += 1
                    sort = self.parse_sort()
                elif self.peek()[0] == "sym" and self.peek()[1] in self._BOUND_OPS:
                    if len(names) != 1:
                        raise Reject("parse", "bounded quantifier with several names")
                    op = self.next()[1]
                    # bound term parsed in the OUTER env (binder not yet pushed)
                    bound = (op, self._force(self._union()))
                groups.append((names, sort))
                break  # bare-name groups terminate at ',' next
            break
        self.eat_sym(",")
        all_names = [n for names, _ in groups for n in names]
        for n in all_names:
            self.env.insert(0, n)
        body = self._force(self.parse_prop())
        for _ in all_names:
            self.env.pop(0)
        if bound is not None:
            op, bterm = bound
            # desugar: the bound term was parsed OUTSIDE the binder; shift it in
            b = _shift(bterm, 1)
            v = {"kind": "var", "index": 0}
            guard = self._mk_cmp(op, v, b)
            body = ({"kind": "implies", "left": guard, "right": body} if q == "∀"
                    else {"kind": "and", "left": guard, "right": body})
        flat = [(n, s) for names, s in groups for n in names]
        for _, s in reversed(flat):
            body = {"kind": "forall" if q == "∀" else "exists",
                    "sort": s, "body": body}
        return body


# operators that exist in Lean/Mathlib surface syntax but have NO math-v0
# bridge (truncated subtraction, division, mod, pow, coercions, ...): their
# rejections get a dedicated reason code for the gate histogram.
UNBRIDGED_OPS = set("-/%^↑↓⁻∘⊤⊥≈≡∞λ@⨆⨅≫≪⟶⥤∑∏⊂")


def _tok_reject(tok):
    return Reject("unbridged-operator" if tok in UNBRIDGED_OPS else "parse",
                  "at token %r" % (tok,))


def parse_prop_text(text, concepts, env=None):
    """Parse a bare fragment Prop (no declaration wrapper); checked, closed
    unless env names are supplied by the caller (declaration parsing)."""
    p = _P(tokenize(text), concepts, env=env)
    term = p._force(p.parse_prop())
    if p.i != len(p.t):
        raise _tok_reject(p.t[p.i][1])
    return term


# ---------------------------------------------------------------- declaration-level F

_KIND_WORDS = ("noncomputable", "partial", "unsafe", "protected", "private")


def split_declaration(sig):
    """'theorem Foo.bar (n : ℕ) ... : STMT' -> (kind, name, [group strings], result).
    Groups are the raw top-level bracketed binder groups (with their brackets)."""
    s = sig.strip()
    words = []
    rest = s
    while True:
        head = rest.split(None, 1)
        if len(head) < 2:
            raise Reject("signature-shape", "no declaration body")
        w, rest2 = head[0], head[1]
        words.append(w)
        rest = rest2
        if w not in _KIND_WORDS:
            break
    kind = " ".join(words)
    # name: up to whitespace or an opening bracket or the result colon
    j = 0
    while j < len(rest) and not rest[j].isspace() and rest[j] not in "({[⦃:":
        j += 1
    name = rest[:j]
    if not name:
        raise Reject("signature-shape", "no declaration name")
    rest = rest[j:]
    opens, closes = "({[⦃⟨", ")}]⦄⟩"
    depth = 0
    groups = []
    cur = []
    result = None
    k = 0
    while k < len(rest):
        c = rest[k]
        if c in opens:
            depth += 1
            cur.append(c)
        elif c in closes:
            depth -= 1
            cur.append(c)
            if depth == 0:
                groups.append("".join(cur).strip())
                cur = []
        elif depth == 0 and c == ":":
            result = rest[k + 1:].strip()
            break
        elif depth > 0:
            cur.append(c)
        elif not c.isspace():
            raise Reject("signature-shape", "unexpected %r outside binders" % c)
        k += 1
    if result is None:
        raise Reject("signature-shape", "no result type")
    return kind, name, groups, result


def lean_statement_to_pm(sig, concepts):
    """FORWARD MAP F at the signature layer: full declaration string ->
    (name, closed checked pm-ast Prop). Raises Reject with the gate reason."""
    kind, name, groups, result = split_declaration(sig)
    if kind not in STATEMENT_KINDS:
        if kind in DEF_KINDS or kind.endswith(("def", "abbrev", "instance")):
            raise Reject("definiens-unavailable-at-layer", kind)
        raise Reject("kind-not-statement-bearing", kind)
    items = []          # ("sort", name, sort) | ("hyp", term)
    sort_env = []       # innermost-first binder names
    dead = set()        # hypothesis names: never legal in later terms
    for g in groups:
        if not g:
            continue
        open_c, body = g[0], g[1:-1].strip()
        if open_c == "[":
            raise Reject("typeclass-binder", g)
        if open_c == "⟨":
            raise Reject("signature-shape", "anonymous-constructor binder")
        if ":=" in body:
            raise Reject("auto-param-binder", g)
        split = _top_level_colon_split(body)
        if len(split) == 2:
            names_part, type_part = split
        else:
            names_part, type_part = body, None
        names = names_part.split()
        if not names or not all(_ident_like(n) for n in names):
            raise Reject("signature-shape", "binder names in %r" % g)
        if type_part is None:
            for n in names:
                items.append(("sort", n, "N"))
                sort_env.insert(0, n)
            continue
        sort = _try_sort(type_part, concepts)
        if sort is not None:
            for n in names:
                items.append(("sort", n, sort))
                sort_env.insert(0, n)
            continue
        hyp = parse_prop_text(type_part, concepts, env=list(sort_env))
        for _ in names:
            items.append(("hyp", hyp))
        dead.update(names)
    for tok_typ, tok_val in tokenize(result):
        if tok_typ == "ident" and tok_val in dead:
            raise Reject("proof-term-dependency", tok_val)
    stmt = parse_prop_text(result, concepts, env=list(sort_env))
    for tag, *payload in reversed(items):
        if tag == "hyp":
            stmt = {"kind": "implies", "left": payload[0], "right": stmt}
        else:
            _, sort = payload
            stmt = {"kind": "forall", "sort": sort, "body": stmt}
    check_statement(stmt, concepts)  # sorts, caps, vacuous binders — fail closed
    return name, stmt


def _ident_like(s):
    return all(_is_ident_char(c) or c == "." for c in s)


def _top_level_colon_split(body):
    depth = 0
    for i, c in enumerate(body):
        if c in "({[⦃⟨":
            depth += 1
        elif c in ")}]⦄⟩":
            depth -= 1
        elif c == ":" and depth == 0:
            return body[:i].strip(), body[i + 1:].strip()
    return (body,)


def _try_sort(text, concepts):
    try:
        p = _P(tokenize(text), concepts)
        s = p.parse_sort()
        if p.i != len(p.t):
            return None
        return s
    except Reject:
        return None


# ---------------------------------------------------------------- renderers (backward map B)

_LEAN_INFIX_CONST = {
    U + "addition": "+", U + "multiplication": "*",
    U + "less-or-equal": "≤", U + "less-than": "<", U + "divides": "∣",
    U + "subset-nat": "⊆", U + "union-nat": "∪", U + "intersection-nat": "∩",
}
_LEAN_PREFIX_CONST = {
    U + "predecessor": "Nat.pred", U + "even": "Even", U + "odd": "Odd",
    U + "prime-number": "Nat.Prime",
}
_LEAN_NULLARY = {U + "one": "1", U + "two": "2", U + "three": "3",
                 U + "empty-set-nat": "∅"}


def _lean_sort(s):
    if s == "N":
        return "ℕ"
    if s.get("kind") == "Set":
        inner = _lean_sort(s["of"])
        return "Set %s" % (inner if s["of"] == "N" else "(%s)" % inner)
    return "%s × %s" % (_lean_sort(s["fst"]), _lean_sort(s["snd"]))


def render_lean(t, depth=0):
    """pm-ast -> Lean-fragment surface syntax; F's own parser re-consumes it
    (round-trip). Fully parenthesised; binder names x<absolute-id>."""
    k = t["kind"]
    if k == "var":
        return "x%d" % (depth - 1 - t["index"])
    if k == "zero":
        return "0"
    if k == "succ":
        return "Nat.succ (%s)" % render_lean(t["arg"], depth)
    if k == "eq":
        return "(%s = %s)" % (render_lean(t["left"], depth), render_lean(t["right"], depth))
    if k == "member":
        return "(%s ∈ %s)" % (render_lean(t["element"], depth), render_lean(t["set"], depth))
    if k == "pair":
        return "(%s, %s)" % (render_lean(t["fst"], depth), render_lean(t["snd"], depth))
    if k == "fst":
        return "Prod.fst (%s)" % render_lean(t["arg"], depth)
    if k == "snd":
        return "Prod.snd (%s)" % render_lean(t["arg"], depth)
    if k == "not":
        return "¬%s" % _paren(render_lean(t["arg"], depth))
    if k in ("and", "or", "implies", "iff"):
        op = {"and": "∧", "or": "∨", "implies": "→", "iff": "↔"}[k]
        return "(%s %s %s)" % (render_lean(t["left"], depth), op,
                               render_lean(t["right"], depth))
    if k in ("forall", "exists"):
        q = "∀" if k == "forall" else "∃"
        # parenthesised so a quantifier used as an operand cannot swallow the
        # enclosing connective's right-hand side on re-parse
        return "(%s (x%d : %s), %s)" % (q, depth, _lean_sort(t["sort"]),
                                        render_lean(t["body"], depth + 1))
    if k == "comprehension":
        return "{x%d : %s | %s}" % (depth, _lean_sort(t["sort"]),
                                    render_lean(t["body"], depth + 1))
    if k == "const":
        ref, args = t["ref"], t["args"]
        if ref in _LEAN_NULLARY and not args:
            return _LEAN_NULLARY[ref]
        if ref == U + "singleton-nat":
            return "{%s}" % render_lean(args[0], depth)
        if ref in _LEAN_INFIX_CONST:
            return "(%s %s %s)" % (render_lean(args[0], depth),
                                   _LEAN_INFIX_CONST[ref],
                                   render_lean(args[1], depth))
        if ref in _LEAN_PREFIX_CONST:
            return "%s (%s)" % (_LEAN_PREFIX_CONST[ref], render_lean(args[0], depth))
        # synthetic face — keeps B total over the fragment (round-trip closure)
        slug = ref[len(U):]
        head = "KOT.%s" % slug.replace("-", "_")
        return " ".join([head] + ["(%s)" % render_lean(a, depth) for a in args]) \
            if args else head
    raise Reject("node-shape", "render: unknown kind %r" % k)


def _paren(s):
    return s if s.startswith("(") else "(%s)" % s


def _neutral_sort(s):
    if s == "N":
        return "N"
    if s.get("kind") == "Set":
        return "Set(%s)" % _neutral_sort(s["of"])
    return "Pair(%s, %s)" % (_neutral_sort(s["fst"]), _neutral_sort(s["snd"]))


def render_neutral(t, depth=0):
    """pm-ast -> notation-neutral text (math-v0 slugs; no Lean/Mathlib names).
    Used verbatim in the LLM location prompts."""
    k = t["kind"]
    if k == "var":
        return "x%d" % (depth - 1 - t["index"])
    if k == "zero":
        return "0"
    if k == "succ":
        return "succ(%s)" % render_neutral(t["arg"], depth)
    if k == "eq":
        return "(%s = %s)" % (render_neutral(t["left"], depth),
                              render_neutral(t["right"], depth))
    if k == "member":
        return "(%s ∈ %s)" % (render_neutral(t["element"], depth),
                              render_neutral(t["set"], depth))
    if k == "pair":
        return "pair(%s, %s)" % (render_neutral(t["fst"], depth),
                                 render_neutral(t["snd"], depth))
    if k in ("fst", "snd"):
        return "%s(%s)" % (k, render_neutral(t["arg"], depth))
    if k == "not":
        return "not %s" % _paren(render_neutral(t["arg"], depth))
    if k in ("and", "or", "implies", "iff"):
        op = {"and": "and", "or": "or", "implies": "implies", "iff": "iff"}[k]
        return "(%s %s %s)" % (render_neutral(t["left"], depth), op,
                               render_neutral(t["right"], depth))
    if k in ("forall", "exists"):
        q = "for all" if k == "forall" else "there exists"
        return "%s x%d : %s . %s" % (q, depth, _neutral_sort(t["sort"]),
                                     render_neutral(t["body"], depth + 1))
    if k == "comprehension":
        return "{x%d : %s | %s}" % (depth, _neutral_sort(t["sort"]),
                                    render_neutral(t["body"], depth + 1))
    if k == "const":
        slug = t["ref"][len(U):]
        if not t["args"]:
            return slug
        return "%s(%s)" % (slug, ", ".join(render_neutral(a, depth)
                                           for a in t["args"]))
    raise Reject("node-shape", "render_neutral: unknown kind %r" % k)


# ---------------------------------------------------------------- gate + round-trip helpers

def gate_record(rec, concepts):
    """Fragment-gate one lean-ref/1 record.
    Returns (True, {name, sha, statement}) or (False, reason_code)."""
    # math-lean-sample (the reference corpus) predates the `extraction` field;
    # default it — mathlib-1000-sample records always carry it.
    if (rec.get("extraction", "doc-gen4-decl") != "doc-gen4-decl"
            or not rec.get("signaturePretty")):
        return False, "no-signature-at-layer"
    try:
        _, stmt = lean_statement_to_pm(rec["signaturePretty"], concepts)
    except Reject as e:
        return False, e.code
    return True, {"name": rec["name"], "sha": content_sha(stmt), "statement": stmt}


def roundtrip_fixed(stmt, concepts):
    """F(B(K)) = K through the production renderer + parser."""
    rendered = render_lean(stmt)
    back = parse_prop_text(rendered, concepts)
    check_statement(back, concepts)
    return canonical(back) == canonical(stmt)
