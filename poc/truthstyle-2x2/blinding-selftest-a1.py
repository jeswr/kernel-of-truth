#!/usr/bin/env python3
"""blinding-selftest-a1 — amendment A1 self-test (blinding-audit-clarification.md
§9.5; registry/corrections/truthstyle-2x2/4-blinding-audit-amendment-a1.json):
amended blinding_scan + sweep behavior. Read-only over the real run dir
(20260710T151231Z); synthetic leak/coincidence cases in a throwaway temp tree.
Exit 0 iff all checks pass."""
import importlib.util, json, os, shutil, subprocess, sys, tempfile

TS = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(TS, "opus-runs/20260710T151231Z")

spec = importlib.util.spec_from_file_location("rdj", os.path.join(TS, "run-dts-judges.py"))
rdj = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rdj)

fails, n_checks = [], [0]
def check(name, cond):
    n_checks[0] += 1
    print(("PASS" if cond else "FAIL"), name)
    if not cond:
        fails.append(name)

scratch = tempfile.mkdtemp(prefix="a1st.")

def scan_bytes(name, payload):
    p = os.path.join(scratch, name)
    with open(p, "wb") as f:
        f.write(payload)
    return rdj.blinding_scan([p])

# --- 1. the real pos-102 coincidence is now excluded; its prompt is clean ---
p102 = os.path.join(RUN, "judge-p3-haiku45/items/pos-102/c1_t0")
check("real pos-102 events.jsonl excluded (was the abort)",
      rdj.blinding_scan([os.path.join(p102, "events.jsonl")]) is None)
check("real pos-102 user-prompt.txt clean",
      rdj.blinding_scan([os.path.join(p102, "user-prompt.txt")]) is None)

# --- 2. regression: the 5 tolerated f2b hex-run exclusions still excluded ---
for rel in ["judge-p2-gpt55/items/pos-515", "judge-p2-gpt55/items/pos-702",
            "judge-p3-haiku45/items/pos-035", "judge-p3-haiku45/items/pos-054",
            "judge-p3-haiku45/items/pos-068"]:
    check("regression f2b hex-run excluded: %s" % rel,
          rdj.blinding_scan([os.path.join(RUN, rel, "c1_t0/events.jsonl")]) is None)

# --- 3. synthetic: real-leak shapes MUST still trip on events.jsonl ---
LEAKS = [
    (b'{"type":"assistant","text":"this is an NSM explication"}', "nsm in answer text"),
    (b'{"cwd":"/home/x/kernel-of-truth"}', "kernel in a path"),
    (b'poc/truthstyle-2x2 something', "truthstyle path fragment"),
    (b'{"x":"f2b-transfer"}', "f2b delimited spelling"),
    (b'"request_id":"req_aBcDnsmXy"', "nsm in too-short (9) tail"),
    (b'"request_id":"req_' + b'A' * 20 + b'nsm' + b'B' * 26 + b'"', "nsm in too-long (49) tail"),
    (b'"k":"xreq_011Cctc1sK9P4SujinnsMiWU"', "prefix embedded in longer word"),
    (b'"k":"REQ_011Cctc1sK9P4SujinnsMiWU"', "uppercase REQ_ prefix (case-sensitive rule)"),
    (b'"k":"ref_011Cctc1sK9P4SujinnsMiWU"', "wrong prefix ref_"),
    (b'req_011Cctc1sK9P4SujinnsMiWU-nsm delimited after the literal',
     "nsm delimited just OUTSIDE a maximal literal"),
    (b'"request_id":"req_011Cctc1sK9P4SujinnsMiWU" and nsm in prose',
     "nsm in prose next to a clean literal"),
]
for payload, name in LEAKS:
    check("leak still trips: " + name, scan_bytes("events.jsonl", payload) is not None)

# --- 4. synthetic: coincidence shapes now excluded on captured surfaces ---
COINC = [
    (b'"request_id":"req_011Cctc1sK9P4SujinnsMiWU"', "observed 'nsm' request_id"),
    (b'"id":"msg_abcKerNeLabcdefghijkl"', "kernel inside msg_ 21-char tail"),
    (b'"id":"req_xxxXf2bZyyyyyyyyyyyyy"', "f2b in base62 tail, non-hex neighbors"),
    (b'"request_id":"req_nsmABCDEFGHIJKLMNOPQ"', "token at tail start (20-char tail)"),
    (b'req_011Cctc1sK9P4SujinnsMiWU bare (stderr shape)', "bare literal, no JSON quoting"),
]
for payload, name in COINC:
    check("coincidence excluded: " + name, scan_bytes("events.jsonl", payload) is None)
    check("coincidence excluded on stderr.log too: " + name,
          scan_bytes("stderr.log", payload) is None)

# --- 5. user-prompt.txt gets NO vendor-id exclusion (fail-closed) ---
check("user-prompt.txt still trips on the same id-shaped bytes",
      scan_bytes("user-prompt.txt",
                 b'"request_id":"req_011Cctc1sK9P4SujinnsMiWU"') is not None)

# --- 6. sweep end-to-end on a synthetic mini run dir ---
mini = os.path.join(scratch, "mini-run")
d = os.path.join(mini, "judge-x/items/pos-001/c1_t0")
os.makedirs(d)
open(os.path.join(d, "user-prompt.txt"), "wb").write(b"Define chair.")
open(os.path.join(d, "events.jsonl"), "wb").write(
    b'{"request_id":"req_011Cctc1sK9P4SujinnsMiWU","session_id":'
    b'"cdf6ab6f-ab88-4fc7-a1a8-f2b8d1b64df9","text":"no"}\n')
open(os.path.join(d, "stderr.log"), "wb").write(b"")
r = subprocess.run([sys.executable, os.path.join(TS, "blinding-sweep.py"), mini],
                   capture_output=True, text=True)
sw = json.load(open(os.path.join(mini, "blinding-sweep.json")))
check("mini sweep GREEN", r.returncode == 0 and sw["verdict"] == "GREEN")
kinds = sorted((e["kind"], e["token"]) for e in sw["exclusions"])
check("mini sweep lists both exclusion kinds",
      kinds == [("hex_run", "f2b"), ("vendor_id", "nsm")])
check("mini sweep vendor_id literal recorded",
      sw["exclusions"][1].get("id_literal", sw["exclusions"][0].get("id_literal"))
      in ("req_011Cctc1sK9P4SujinnsMiWU",)
      or any(e.get("id_literal") == "req_011Cctc1sK9P4SujinnsMiWU" for e in sw["exclusions"]))

# --- 7. read-only sweep-equivalent walk over the REAL run dir (no writes) ---
hits, excl = [], []
for dirpath, _, names in sorted(os.walk(RUN)):
    for name in sorted(names):
        if name not in ("user-prompt.txt", "events.jsonl", "stderr.log"):
            continue
        path = os.path.join(dirpath, name)
        if rdj.blinding_scan([path]):
            hits.append(os.path.relpath(path, RUN))
        raw = open(path, "rb").read()
        data = raw.lower()
        spans = [] if name == "user-prompt.txt" else rdj._vendor_id_tail_spans(raw)
        for t in rdj.BLIND_TOKENS:
            i = data.find(t)
            while i >= 0:
                if any(s <= i and i + len(t) <= e for s, e in spans):
                    excl.append(("vendor_id", os.path.relpath(path, RUN), t.decode()))
                elif (all(c in rdj._HEX_BYTES for c in t)
                      and rdj._hex_embedded(data, i, len(t))):
                    excl.append(("hex_run", os.path.relpath(path, RUN), t.decode()))
                i = data.find(t, i + 1)
print("real run dir: clarified hits =", hits)
print("real run dir: exclusions =", json.dumps(excl, indent=1))
check("real run dir now GREEN-equivalent (no clarified hits)", hits == [])
check("real run dir: exactly 6 exclusions (5 f2b hex + 1 nsm vendor id)",
      sorted(e[0] for e in excl) == ["hex_run"] * 5 + ["vendor_id"]
      and [e for e in excl if e[0] == "vendor_id"][0][1:] ==
          ("judge-p3-haiku45/items/pos-102/c1_t0/events.jsonl", "nsm"))

shutil.rmtree(scratch)
print("\nSELFTEST:", "PASS (all %d checks)" % n_checks[0]
      if not fails else "FAIL: %s" % fails)
sys.exit(1 if fails else 0)
