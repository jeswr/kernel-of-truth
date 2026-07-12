#!/usr/bin/env python3
"""CODEVERT G0 — dynamic trace probe (G1 §7 soundness-probe mini, mechanical).

Runs a repo's own test suite under sys.setprofile + a builtins.__import__
wrapper, recording (a) intra-repo Python call edges (caller frame -> callee
frame, both files under the repo root) and (b) import events attributed to
the importing repo file. NO annotation; extractor-independent observations.

Usage: probe_runner.py <repo_root> <test_path> <out_json>
"""
import builtins, json, os, sys


def main():
    repo_root = os.path.abspath(sys.argv[1])
    test_path = sys.argv[2]
    out_json = sys.argv[3]
    prefix = repo_root + os.sep
    call_edges = set()
    import_events = set()

    GEN_FLAGS = 0x20 | 0x80 | 0x200  # GENERATOR | COROUTINE | ASYNC_GENERATOR

    def prof(frame, event, arg):
        if event != "call":
            return
        co = frame.f_code
        fn = co.co_filename
        if not fn.startswith(prefix):
            return
        back = frame.f_back
        if back is None:
            return
        bco = back.f_code
        bfn = bco.co_filename
        if not bfn.startswith(prefix):
            return
        call_edges.add((bfn[len(prefix):], bco.co_name, bco.co_firstlineno,
                        fn[len(prefix):], co.co_name, co.co_firstlineno,
                        bool(co.co_flags & GEN_FLAGS)))

    orig_import = builtins.__import__

    def imp(name, globals=None, locals=None, fromlist=(), level=0):
        try:
            f = sys._getframe(1)
            fn = f.f_code.co_filename
            if fn.startswith(prefix):
                pkg = (globals or {}).get("__package__") or ""
                import_events.add((fn[len(prefix):], name, level, str(pkg),
                                   tuple(fromlist or ())))
        except Exception:
            pass
        return orig_import(name, globals, locals, fromlist, level)

    sys.path.insert(0, repo_root)
    if os.path.isdir(os.path.join(repo_root, "src")):
        sys.path.insert(0, os.path.join(repo_root, "src"))
    os.chdir(repo_root)

    builtins.__import__ = imp
    sys.setprofile(prof)
    import pytest
    rc = pytest.main([test_path, "-q", "-x" if False else "--continue-on-collection-errors",
                      "-p", "no:cacheprovider"])
    sys.setprofile(None)
    builtins.__import__ = orig_import

    with open(out_json, "w") as fh:
        json.dump({"repo_root": repo_root, "pytest_exit": int(rc),
                   "n_call_edges": len(call_edges),
                   "n_import_events": len(import_events),
                   "call_edges": sorted(call_edges),
                   "import_events": sorted(import_events)}, fh)
    print("edges:", len(call_edges), "imports:", len(import_events), "rc:", rc)


if __name__ == "__main__":
    main()
