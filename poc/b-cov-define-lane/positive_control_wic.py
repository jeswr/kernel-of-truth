#!/usr/bin/env python3
"""Instrument-validity positive control for the b-cov define-lane WiC CELL.

Proves the WiC cell's 0.0000 headline κ_B and its 0 breadth-checkable count are
REAL MEASURED nulls, not a broken harness:

  (A) HEADLINE-PATH control — re-runs hu10's committed positive_control.py verbatim
      (subprocess). It feeds three questions that DO target an endorsed onto-obo
      definition through the SAME mapper -> engine -> §C5 pipeline the WiC cell
      uses, and requires §C5 n==1 + engine DEFINE-MATCH True. PASS => the pipeline
      yields a define-checkable when one exists.

  (B) BREADTH-PATH control — feeds the WiC-cell breadth diagnostic a synthetic
      item whose target 'word' IS a licensed onto-obo term carrying a
      logicalDefinition ('regulation of DNA recombination', GO:0000018). Requires
      resolved_unique>=1 and a DEFINE-retrieve 'answer'. PASS => the breadth
      diagnostic yields a positive when the target vocabulary IS in-substrate; so
      the 615/638 unresolved + 21/21 ERR_NO_DEFINITION on real WiC is the measured
      absence of biomedical-definitional vocabulary, not an instrument failure.

Run: python3 poc/b-cov-define-lane/positive_control_wic.py
"""
import os, sys, subprocess, collections

ROOT = "."
HERE = os.path.join(ROOT, "poc", "b-cov-define-lane")
sys.path.insert(0, os.path.join(ROOT, "tools", "axiom"))
sys.path.insert(0, HERE)
import kot_axiom as K  # noqa: E402
import census_wic as CW  # noqa: E402


def main():
    ok = True

    # (A) reuse hu10's committed instrument verbatim
    print("--- (A) HEADLINE-PATH control: hu10 positive_control.py ---")
    r = subprocess.run([sys.executable, os.path.join(HERE, "positive_control.py")],
                       capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    a_pass = (r.returncode == 0 and "POSITIVE CONTROL: PASS" in r.stdout)
    ok = ok and a_pass
    print("(A) %s" % ("PASS" if a_pass else "FAIL"))

    # (B) breadth-path control through the WiC-cell breadth_diagnostic
    print("\n--- (B) BREADTH-PATH control: in-substrate target word ---")
    eng = K.build_engine(ROOT)
    pc_item = [{
        "id": "pc-wic-breadth",
        "text": "Regulation of DNA recombination occurs. It also occurred yesterday.",
        "options": ["regulation of DNA recombination"],
        "word": "regulation of DNA recombination",
    }]
    detail = []

    class _Sink:
        def write(self, s):
            detail.append(s)
    b = CW.breadth_diagnostic(pc_item, eng, _Sink())
    resolved = b["resolution"].get("resolved_unique", 0)
    answered = b["define_retrieve_engine_outcomes_over_resolved_unique"].get("answer", 0)
    b_pass = (resolved >= 1 and answered >= 1)
    ok = ok and b_pass
    print("resolved_unique=%d define-retrieve answer=%d -> %s" % (
        resolved, answered, "PASS" if b_pass else "FAIL"))

    print("\nWIC-CELL POSITIVE CONTROL:",
          "PASS (instrument valid)" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
