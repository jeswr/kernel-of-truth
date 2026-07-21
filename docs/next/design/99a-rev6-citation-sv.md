# 99a Rev6 — Multiplicity-citation [SV] (source verification)

**Verifier:** Haiku literature-researcher (Agent tool `model:haiku` — non-cap-coupled), 2026-07-21. **Verdict: ALL-HOLD** — all four multiplicity citations soundly ground the Rev6 procedure. Search-tier verification (suggestive; the pre-freeze re-confirm can deepen).

| Citation | Verdict | Load-bearing condition to respect |
|---|---|---|
| **Bretz, Maurer, Brannath & Posch (2009)** graphical procedure | SUPPORTS | strong FWER ≤ α under **arbitrary dependence** via closed-testing shortcut; requires **free-combination closure** (or documented restricted combinations), weights≤1, transition rows≤1 zero-diagonal, **valid (super-uniform) component p-values** |
| **Marcus, Peritz & Gabriel (1976)** closed testing | SUPPORTS | closed-testing strong-FWER; each intersection local test level-α; dependence-agnostic |
| **Berger (1982)** IUT (p=max) | SUPPORTS-WITH-CAVEAT | valid level-α union-null test, no α-split, **CONSERVATIVE (size ≤ α)** — do NOT claim exact size=α for the conjunctive IUT nulls |
| **Berger & Hsu (1996)** TOST-as-IUT | SUPPORTS | TOST exact size=α (perfect negative correlation of the two one-sided tests); requires correct equivalence bounds |

**Four binding conditions for the prereg (fold into Rev7):** (1) document free- vs restricted-combination closure; (2) every component/intersection test at its specified α; (3) component p-values valid/super-uniform under H₀ (no independence needed, but computed correctly); (4) IUT conjunctive nulls are conservative — reserve exact-α claims for TOST only.
