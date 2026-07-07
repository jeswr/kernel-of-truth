// Tarjan strongly-connected components, iterative (no recursion-depth limit;
// GO's is_a chains reach depth ~18 and the whole graph is ~39k nodes / ~84k
// edges, well within an explicit stack).
//
// Returns SCCs in *reverse topological order* of the condensation: a component
// appears before any component it depends on's dependents... precisely, Tarjan
// emits components in reverse topological order (a component is finalized only
// after all components it points to are finalized). That is exactly the order
// we need for Unison-style substitution (concept-hash-design.md s6 step 4:
// "process in reverse topological order"): every reference target is minted
// before the referrer.

export function tarjanSCC(
  nodes: readonly string[],
  edges: ReadonlyMap<string, readonly string[]>,
): string[][] {
  const index = new Map<string, number>();
  const low = new Map<string, number>();
  const onStack = new Set<string>();
  const stack: string[] = [];
  const out: string[][] = [];
  let counter = 0;

  for (const root of nodes) {
    if (index.has(root)) continue;
    // work stack of (node, neighborIndex)
    const work: Array<[string, number]> = [[root, 0]];
    while (work.length > 0) {
      const top = work[work.length - 1]!;
      const v = top[0];
      let pi = top[1];
      if (pi === 0) {
        index.set(v, counter);
        low.set(v, counter);
        counter++;
        stack.push(v);
        onStack.add(v);
      }
      const nbrs = edges.get(v) ?? [];
      let recursed = false;
      while (pi < nbrs.length) {
        const w = nbrs[pi]!;
        pi++;
        if (!index.has(w)) {
          top[1] = pi;
          work.push([w, 0]);
          recursed = true;
          break;
        } else if (onStack.has(w)) {
          low.set(v, Math.min(low.get(v)!, index.get(w)!));
        }
      }
      if (recursed) continue;
      // done with v
      if (low.get(v) === index.get(v)) {
        const comp: string[] = [];
        for (;;) {
          const w = stack.pop()!;
          onStack.delete(w);
          comp.push(w);
          if (w === v) break;
        }
        out.push(comp);
      }
      work.pop();
      if (work.length > 0) {
        const parent = work[work.length - 1]![0];
        low.set(parent, Math.min(low.get(parent)!, low.get(v)!));
      }
    }
  }
  return out;
}
