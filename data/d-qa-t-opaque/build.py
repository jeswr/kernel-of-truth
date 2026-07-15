#!/usr/bin/env python3
"""build d-qa-t-opaque — thin shim over data/d-qa-t-plain/build.py.

The gsx0 store corpora (d-qa-t-plain, d-qa-t-opaque) are built by ONE
deterministic pass of data/d-qa-t-plain/build.py so their item skeletons are
identical across store conditions BY CONSTRUCTION (design
docs/next/design/generic-store-external-gold.md section 4.1, RULING G-2).
This shim exists so each corpus directory carries its declared builder entry
point; it simply executes the canonical builder, which writes BOTH corpora.
"""
import os
import runpy

runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            os.pardir, "d-qa-t-plain", "build.py"),
               run_name="__main__")
