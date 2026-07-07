"""
Seeded inclusion-minimal feedback-vertex-set sampler (PREREG §4.4).

One call = one grounding set for one seed. Operates on the kernel subgraph
reindexed to dense local ids [0..m). Degrees used in the heuristic are the
current H (kernel-induced) degrees, including cross-SCC edges, per §4.4.
"""
import random

import x1g_lib as L


def build_kernel_subgraph(kernel_ids, out_adj):
    """Reindex kernel to local ids; return (inv, loc, kout, kin) with sets."""
    kset = set(kernel_ids)
    inv = sorted(kernel_ids)                 # local id -> global id (sorted)
    loc = {g: i for i, g in enumerate(inv)}
    m = len(inv)
    kout = [set() for _ in range(m)]
    kin = [set() for _ in range(m)]
    for g in inv:
        i = loc[g]
        for w in out_adj[g]:
            if w in kset:
                kout[i].add(loc[w])
    for i in range(m):
        for j in kout[i]:
            kin[j].add(i)
    return inv, loc, kout, kin


def _kahn_acyclic_local(m, kout_static, removed):
    """Kahn over local kernel minus `removed` set. kout_static: list of sets."""
    alive = [v for v in range(m) if v not in removed]
    aset = set(alive)
    indeg = {v: 0 for v in alive}
    for v in alive:
        for w in kout_static[v]:
            if w in aset:
                indeg[w] += 1
    queue = [v for v in alive if indeg[v] == 0]
    seen = 0
    while queue:
        v = queue.pop()
        seen += 1
        for w in kout_static[v]:
            if w in aset:
                indeg[w] -= 1
                if indeg[w] == 0:
                    queue.append(w)
    return seen == len(alive)


def sample_fvs(inv, kout_static, kin_static, seed):
    """Return (F_global_sorted, F_local_set). PREREG §4.4 sampler."""
    m = len(inv)
    rng = random.Random(seed)
    # u_v ~ Uniform(0,1), drawn in local (== sorted-global) order.
    u = [rng.random() for _ in range(m)]

    # Mutable working copies (sets for O(1) removal).
    out = [set(s) for s in kout_static]
    inn = [set(s) for s in kin_static]
    alive = bytearray([1]) * m
    F = set()

    def remove(i):
        alive[i] = 0
        for w in out[i]:
            inn[w].discard(i)
        for w in inn[i]:
            out[w].discard(i)
        out[i].clear()
        inn[i].clear()

    def trim(seeds):
        stack = [x for x in seeds if alive[x]]
        while stack:
            v = stack.pop()
            if not alive[v]:
                continue
            if len(out[v]) == 0 or len(inn[v]) == 0:
                nb = list(out[v]) + list(inn[v])
                remove(v)
                stack.extend(nb)

    # step 1: self-loops -> F (none expected in a no-self-loop graph).
    for i in range(m):
        if i in out[i]:
            F.add(i)
            remove(i)

    # step 2 (initial global trim).
    trim(range(m))

    # component stack: nontrivial SCCs; process incrementally (§4.4 note).
    alive_ids = [v for v in range(m) if alive[v]]
    comps = [sorted(c) for c in L.tarjan_scc(alive_ids, out) if len(c) > 1]
    while comps:
        comp = [v for v in comps.pop() if alive[v]]
        if len(comp) < 2:
            continue
        # process sub-SCCs in a deterministic order (by min vertex) so the
        # cross-SCC trim cascades are reproducible; argmax below is unique (u
        # is continuous), so no per-SCC sort of the ~17k core is needed.
        subsccs = sorted((min(c), c) for c in L.tarjan_scc(comp, out))
        for _, scc in subsccs:
            scc = [v for v in scc if alive[v]]
            if len(scc) < 2:
                continue
            # greedy degree-product pick, randomized tie via u (§4.4 step 3).
            best = None
            best_key = None
            for v in scc:
                key = (len(inn[v]) + u[v]) * (len(out[v]) + u[v])
                if best_key is None or key > best_key:
                    best_key = key
                    best = v
            F.add(best)
            nb = list(out[best]) + list(inn[best])
            remove(best)
            trim(nb + [v for v in scc if v != best])
            comps.append([v for v in scc if alive[v]])

    # step 5: minimality pass in seeded-shuffled order (§4.4).
    order = sorted(F)
    rng.shuffle(order)
    Fmin = set(F)

    def creates_cycle(v):
        # cycle through v in (kernel \ (Fmin\{v})) iff v can reach v via alive.
        removed = Fmin - {v}
        stack = [w for w in kout_static[v] if w not in removed]
        seen = set()
        while stack:
            x = stack.pop()
            if x == v:
                return True
            if x in seen:
                continue
            seen.add(x)
            for y in kout_static[x]:
                if y not in removed:
                    stack.append(y)
        return False

    for v in order:
        if not creates_cycle(v):
            Fmin.discard(v)

    F_global = sorted(inv[i] for i in Fmin)
    return F_global, Fmin


def verify_grounding_and_minimal(m, kout_static, F_local):
    """Return (is_grounding, is_minimal). Independent check for smoke."""
    grounding = _kahn_acyclic_local(m, kout_static, F_local)
    if not grounding:
        return False, False
    minimal = True
    for v in F_local:
        # removing v must reintroduce a cycle (v is necessary).
        if _kahn_acyclic_local(m, kout_static, F_local - {v}):
            minimal = False
            break
    return grounding, minimal
