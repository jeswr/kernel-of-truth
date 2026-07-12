#!/usr/bin/env python3
"""run-ontg2v2.py -- MECHANICAL executor of the ONT-TYPE-G2/1-v2 proxy
annotation re-mint (registry g2-import-v2). Faithful port of the audited
poc/ontology-import-g2/run-ontg2.py machinery (itself ported from
poc/g2/run-g2lp.py / g3-llmproxy-v3): identical invocation forms,
validity/retry/no-label contracts, blinding audit, checkpointing --
extended per docs/next/design/g2-import-v2-repair.md with (i) the v2
sentence-force prompt template, (ii) the STAGE-P PILOT block with
pilot-stop semantics (design section 4: NO full-arm call may precede a
green pilot), (iii) the hedge-flip probe phase (section 3b), and
(iv) a live dollar/call abort at a pinned conservative price bound
(review fix 5). DESIGNS NOTHING, CONCLUDES NOTHING. All v1 files are
consumed byte-identical BY PIN; regeneration is a pin break.

Protocol (maintainer directive #11, unchanged from v1):
  judge-pA  gpt-5.6-sol via npx-pinned openai codex CLI 0.144.1,
            reasoning effort low, read-only, ephemeral, server-side
            output schema (PRIMARY construction)
  judge-pB  claude-haiku-4-5-20251001 via headless claude CLI, tools
            disabled, no session persistence (SENSITIVITY judge;
            vendor-family overlap DISCLOSED, never sole gold)
Stateless per-item calls; the NEW v2 sentence-force rubric
(prompt-template-v2.txt, identical for every arm and both judges);
FRESH per-judge-per-arm-per-phase order seeds (materials/manifest.json);
{yes,no,cannot-say}; first valid answer final; full blinding scans.

A0 is NOT re-adjudicated (frozen 33/84). Pilot labels are instrument
evidence ONLY: discarded from all scoring; the full run re-adjudicates
all 84 items with fresh stateless calls (ASM re: pilot discipline).

Usage:
  run-ontg2v2.py preflight <pA|pB> <run_dir>          (2 v1-cal + 6 hedge-cal)
  run-ontg2v2.py pilot     <pA|pB> <run_dir>          (6 cal + 40 real + 8 flip)
  run-ontg2v2.py pilotgate <run_dir>                  (gate; on FAIL assembles
                                                       the pilot-only result)
  run-ontg2v2.py real      <pA|pB> <a1|a2|a3> <run_dir>
  run-ontg2v2.py probe     <pA|pB> <a1|a2|a3> <run_dir>
  run-ontg2v2.py hedgeflip <pA|pB> <a2|a3> <run_dir>
  run-ontg2v2.py assemble  <run_dir>
  run-ontg2v2.py mock      <run_dir> <go|nogo|instrument|pilotfail|breadth>
                                                       (no LLM calls)
Flags (append to any mode):
  --pa-proxy fable   PROVISIONAL pA proxy (kernel-of-truth-29nb); never frozen
  --rubric v22       v2.2 composite-hedge rubric iteration (DRAFT; successor
                     record required -- docs/next/design/
                     g2-import-v22-rubric-iteration.md); default = frozen v2
"""
import json
import os
import sys
import hashlib
import subprocess
import time

REPO = "/home/ec2-user/css/kernel/kernel-of-truth"
BASE = os.path.join(REPO, "poc/ontology-import-g2-v2")
MAT = os.path.join(BASE, "materials")
V1BASE = os.path.join(REPO, "poc/ontology-import-g2")
V1MAT = os.path.join(V1BASE, "materials")
G2MAT = os.path.join(REPO, "poc/g2/materials")
CODEX_HOME_ISO = "/tmp/ontg2v2-codex-home-iso"

sys.path.insert(0, os.path.join(REPO, "analysis"))
import g3_llmproxy_v3 as G   # pinned blinding-scan + fence-extraction impls

# ---- pinned inputs (fail-closed; ERR_ONTG2V2_PIN) ----
# v1-inherited pins are byte-identical to the g2-import frozen values;
# new v2 instrument files are pinned at their build hashes (design 9 step 2).
PINS = {
    "poc/ontology-import-g2/materials/arm-a1-bfo.jsonl":
        "e91c4cef43b9c685ab4223dbfda30c3577fdfc870017f9530da9ee20175aec4a",
    "poc/ontology-import-g2/materials/arm-a2-bfo-sumo.jsonl":
        "13ce9e116a44dca072a4e9b8f4103d4025c1fdc1527a67e321195b55a9c92bd7",
    "poc/ontology-import-g2/materials/arm-a3-bfo-sumo-framenet.jsonl":
        "4600941ae080991071e6ff4de2a97cd450b3ad4bc8ed8c63686729f78855d3e3",
    "poc/ontology-import-g2/materials/arm-a0-baseline.jsonl":
        "493c4b440d27ca10d5f17e5c2d102471cef6a1799447c2a848bf398bd3ef5300",
    "poc/ontology-import-g2/materials/probes-a1.jsonl":
        "c19576730437b1bdc3a4f95dd63892910aecf242d04fe4b3707277835af3aaa7",
    "poc/ontology-import-g2/materials/probes-a2.jsonl":
        "516efb1df208e57d3b32d1d5fb435d4e88c4aa3933a29b9038f39999154b540c",
    "poc/ontology-import-g2/materials/probes-a3.jsonl":
        "76c8d389d4980f99d088edb36e9b246b91cee3daf4f3df09de046ada9774a175",
    "poc/ontology-import-g2/materials/generation-report.json":
        "b8874a2408ea4a241f9adb04201c4233ed5a90aa7c9f578c2dbbf0b679f4d21b",
    "data/onto-softtype/soft-type-candidates.jsonl":
        "3a377cfc73b7e8a45c3a08ac98eed0a75d3f2b113928adfc00d5efad95c9fadb",
    "poc/g2/materials/items.jsonl":
        "7a4728840550227703338880a79f61491a3c93e5022f07215631f6caa7077008",
    "poc/g2/materials/judge-pB-system-prompt.txt":
        "be9198312e4d8e54b7ac8db5a0b9f0a2f50d96327a6cfb56f5c0a1acbee4f297",
    "poc/g2/materials/output-schema.json":
        "c43725989beb58f8e65f952e00dea9c0d2896148d732277bd50402708ed4b13f",
    "poc/g2/materials/calibration-items.jsonl":
        "a2ba97735a437f704f0dcc79af8a5efdc7cc4c549f394da4d973691f9afb9d59",
    "poc/g2/labels-proxy.jsonl":
        "93a124478b8dba411bfd1a9fd07cbc96e874def8e6ac819202c54c1b121754b3",
    # ---- new v2 instrument files (this record's build pass) ----
    "poc/ontology-import-g2-v2/prompt-template-v2.txt":
        "6ba9a6f4b686b11802739d8f62a3002d5169833201aca8806afe9e2ab83b69f6",
    "poc/ontology-import-g2-v2/calibration-hedge.jsonl":
        "f8d4e03b5547bc201acbbc1c194ac6d6e0103528e6467d28af2b869a6c2da488",
    "poc/ontology-import-g2-v2/probes-hedgeflip-a2.jsonl":
        "a1ccf05a78bfce955232829bf05fd28c4c26b6a2825c590937e7964ad50cf0ed",
    "poc/ontology-import-g2-v2/probes-hedgeflip-a3.jsonl":
        "7c8d782930e08a45c0f3f5b76aa140feffaba09a8338a8ab24c9ce517d075529",
    "poc/ontology-import-g2-v2/pilot-manifest.json":
        "e4ac7c9590507f44725419361cd4c310a931f169b6d934f87cf44b498d021d27",
    "poc/ontology-import-g2-v2/materials/manifest.json":
        "8b7ba7126dc303f5a53b82094e0afb88c4c8f80221b0a0a992807329b942dbbb",
    "analysis/ontg2v2.py":
        "cc5806fe19ebf89efc66f0184200897041f31a7c8c05e94a7a4e94d92591deec",
    "analysis/g3_llmproxy_v3.py":
        "fbaea0c0559962fed724cf1a94e3f7c7dccca68ddfbc364b6f05da4a3712d21e",
}
PATHS = {k: os.path.join(REPO, k) for k in PINS}

JUDGE_CFG = {
    "pA": {"id": "judge-pA-gpt56sol", "kind": "codex", "model": "gpt-5.6-sol"},
    "pB": {"id": "judge-pB-haiku45", "kind": "claude",
           "model": "claude-haiku-4-5-20251001"},
}

# ---- PROVISIONAL pA proxy (kernel-of-truth-29nb; NOT the frozen grade) ----
# 2026-07-12: the codex/GPT-5.6 pA path is usage-capped (~1h). Maintainer
# directive: `--pa-proxy fable` swaps judge-pA to claude-fable-5 via the SAME
# headless-claude machinery as judge-pB, for an EARLY-READ campaign labelled
# PROVISIONAL-ON-FABLE-PROXY-pA. The FROZEN codex pA path is byte-untouched
# when the flag is absent; when GPT-5.6 is back the frozen instrument
# (pA=GPT-5.6-Sol) re-runs the same 84 items and its grade GOVERNS on any
# material AC1/verdict difference. Proxy runs keep ALL response files inside
# their run_dir so the canonical BASE locations stay reserved for the frozen
# run.
PA_PROXY = None
HAIKU_MODEL = "claude-haiku-4-5-20251001"
FABLE_MODEL = "claude-fable-5"
# The headless claude CLI spawns a background haiku helper turn whose key
# appears in modelUsage alongside the requested model (observed 2026-07-12
# probe: init.model='claude-fable-5', modelUsage={fable, haiku}). Allowed
# ONLY under the proxy; the frozen pB exact-single-key check is unchanged.
FABLE_MU_ALLOWED = frozenset({FABLE_MODEL, HAIKU_MODEL})


def activate_pa_proxy(val):
    global PA_PROXY
    if val != "fable":
        die("ERR_ONTG2V2_PROXY: --pa-proxy supports only 'fable'")
    PA_PROXY = "fable"
    JUDGE_CFG["pA"] = {"id": "judge-pA-fable5-PROXY", "kind": "claude",
                       "model": FABLE_MODEL}


# ---- v2.2 rubric iteration (flag-guarded; DRAFT until a successor record
# freezes it -- docs/next/design/g2-import-v22-rubric-iteration.md) ----
# 2026-07-12: the frozen g2-import-v2 record consumed its sanctioned Stage-P
# pilot (runs/real-20260712-auth, AC1_A3 0.6222 < 0.65, INSTRUMENT-INVALID
# pilot channel). The located residual channel is one-sided judge-pB
# hedge-strictness on multi-claim hedged composites (9 persistent
# disagreements across both authoritative pilots; pB 0/40 cross-pilot
# flips). `--rubric v22` activates the v2.2 instrument: the composite-hedge
# scope clarification (prompt-template-v2.2.txt) + the 8-item calibration
# set (calibration-hedge-v22.jsonl, 2 new composite-hedge anchors exercised
# at the operating point). WITHOUT the flag every byte of frozen v2
# behaviour is untouched. PRE-COMMITMENT (recorded, ASM-1825): a second
# sanctioned AC1_A3 < 0.65 pilot fail RETIRES the GPT-5.6+Haiku proxy pair
# for the adoption arm; adoption authority passes to the two-human panel.
RUBRIC = "v2"
V22_PINS = {
    "poc/ontology-import-g2-v2/prompt-template-v2.2.txt":
        "60d3403721135410b51177545e637f8c12e44e5f18f4ccf8c2ade867dc4cfde1",
    "poc/ontology-import-g2-v2/calibration-hedge-v22.jsonl":
        "63c247a9e7e7edc8769739753ef3b4c33b502f1b93dd01e12e6a948a4f97f57f",
}


def activate_rubric(val):
    """v2.2: 8 hedge-cal items (16/16 gate), pilot 112 calls, total 796;
    796 x $0.012 = $9.552 <= the $10 usd_cap. All other gates unchanged
    (AC1 >= 0.65, decisive >= 36/40, hedge-flip <= 2/8)."""
    global RUBRIC, PILOT_CAL_MIN, BUDGET_MAX_CALLS
    if val != "v22":
        die("ERR_ONTG2V2_RUBRIC: --rubric supports only 'v22'")
    RUBRIC = "v22"
    PINS.update(V22_PINS)
    PATHS.update({k: os.path.join(REPO, k) for k in V22_PINS})
    PILOT_CAL_MIN = 16          # 8 hedge-calibration items x 2 judges
    BUDGET_MAX_CALLS = 796      # +4 pilot cal + 4 preflight cal vs 788


def _template_rel():
    return ("poc/ontology-import-g2-v2/prompt-template-v2.2.txt"
            if RUBRIC == "v22"
            else "poc/ontology-import-g2-v2/prompt-template-v2.txt")


def _hedge_cal_rel():
    return ("poc/ontology-import-g2-v2/calibration-hedge-v22.jsonl"
            if RUBRIC == "v22"
            else "poc/ontology-import-g2-v2/calibration-hedge.jsonl")
EXPECT_CODEX_VER = "codex-cli 0.144.1"
EFFORT = "low"
NPX_CODEX = ["npx", "-y", "@openai/codex@0.144.1"]
ARMS = ("a1", "a2", "a3")
HEDGED_ARMS = ("a2", "a3")
ARM_FILE = {"a1": "arm-a1-bfo.jsonl", "a2": "arm-a2-bfo-sumo.jsonl",
            "a3": "arm-a3-bfo-sumo-framenet.jsonl"}

BANNED_TYPE_SUBSTR = ["exec_command", "terminal_interaction", "unified_exec",
                      "tool_call", "web_search", "patch_apply", "view_image",
                      "image_generation", "collab_"]
TRANSPORT_TYPE_SUBSTR = ["stream_error", "rate_limit", "rate-limit"]
TRANSPORT_BACKOFF = [30, 60, 120, 300, 300, 300, 300, 300, 300, 300]
MAX_TRANSPORT = 10
MAX_CONTENT = 3
N_ITEMS = 84
N_PROBES = 20
N_HEDGEFLIP = 10
N_PILOT = 40
N_PILOTFLIP = 8                  # doubled 4 -> 8, design section 11.4
NOLABEL_ABORT_REAL = 5
NOLABEL_ABORT_PROBE = 3
NOLABEL_ABORT_PILOT = 4          # 0.90 decisive floor at n=40

# Budget (design sections 8 + 11.4, review fix 5): hard call ceiling AND a
# live dollar abort at a pinned CONSERVATIVE price bound. The v1 ledger
# measured 624 calls inside its $1-5 band (<= $0.008/call worst case); the
# pinned bound is 1.5x that: $0.012/call. 788 x 0.012 = $9.456 <= the $10
# usd_cap, so the bound-implied worst case can never cross the registry cap.
# (780 -> 788: the pilot hedge-flip block is doubled to 8 per judge.)
BUDGET_MAX_CALLS = 788
PRICE_BOUND_USD_PER_CALL = 0.012
USD_CAP = 10.0

# Stage-P pilot gate (design sections 4 + 11, kappa-paradox redesign
# 2026-07-12: the gated pair statistic is Gwet AC1, prevalence-robust;
# Cohen kappa is CO-REPORTED for cross-record continuity, NEVER gated --
# at the measured v2 operating prevalence pi ~ 0.83 kappa collapses for
# accurate judges with independent errors)
PILOT_CAL_MIN = 12               # 6 hedge-calibration items x 2 judges
PILOT_AC1_MIN = 0.65             # design 11.3 justification quadrangle
PILOT_DECISIVE_MIN = 36          # 0.90 of 40, per judge
PILOT_HF_FS_MAX = 0.25           # <= 2/8 hedge-flip false-sat per judge

CAP_PATTERNS = [
    "usage limit", "usage-limit", "rate limit reached", "quota",
    "session limit", "exceeded your", "too many requests",
    "resets at", "reset at", "try again later", "credit balance",
    "insufficient", "you've reached", "you have reached", "limit reached",
    "429", "upgrade to increase", "monthly limit", "weekly limit",
]


class AbortExperiment(Exception):
    pass


class StopCap(Exception):
    pass


def die(msg):
    sys.stderr.write("RUN_ONTG2V2_ABORT: %s\n" % msg)
    sys.exit(2)


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def file_sha(path):
    with open(path, "rb") as f:
        return sha_bytes(f.read())


def claude_version_tuple(s):
    tok = s.strip().split()[0]
    try:
        return tuple(int(x) for x in tok.split("."))
    except Exception:
        return None


def ensure_codex_home():
    if os.path.isdir(CODEX_HOME_ISO):
        return
    auth = os.path.expanduser("~/.codex/auth.json")
    if not os.path.exists(auth):
        die("ERR_ONTG2V2_PIN: ~/.codex/auth.json missing")
    os.makedirs(CODEX_HOME_ISO, mode=0o700, exist_ok=True)
    with open(auth, "rb") as f:
        data = f.read()
    dst = os.path.join(CODEX_HOME_ISO, "auth.json")
    with open(dst, "wb") as f:
        f.write(data)
    os.chmod(dst, 0o600)
    cfg = os.path.expanduser("~/.codex/config.toml")
    if os.path.exists(cfg):
        with open(cfg, "rb") as fi, \
                open(os.path.join(CODEX_HOME_ISO, "config.toml"), "wb") as fo:
            fo.write(fi.read())


def verify_pins(kind):
    for rel, want in PINS.items():
        got = file_sha(PATHS[rel])
        if got != want:
            die("ERR_ONTG2V2_PIN: %s sha %s != pinned %s" % (rel, got, want))
    if os.path.exists(os.path.expanduser("~/.claude/CLAUDE.md")):
        die("ERR_ONTG2V2_PIN: ~/.claude/CLAUDE.md exists (would inject context)")
    banners = {}
    if kind == "codex":
        ensure_codex_home()
        env = dict(os.environ)
        env["CODEX_HOME"] = CODEX_HOME_ISO
        ver = subprocess.run(NPX_CODEX + ["--version"], capture_output=True,
                             text=True, env=env).stdout.strip()
        if ver != EXPECT_CODEX_VER:
            die("ERR_ONTG2V2_PIN: npx codex version %r != %r"
                % (ver, EXPECT_CODEX_VER))
        banners = {"npx_codex": ver}
        gv = subprocess.run(["codex", "--version"], capture_output=True,
                            text=True).stdout.strip()
        banners["global_codex_untouched"] = gv
    elif kind == "claude":
        cv = subprocess.run(["claude", "--version"], capture_output=True,
                            text=True).stdout.strip()
        vt = claude_version_tuple(cv)
        if vt is None or vt < (2, 1, 201):
            die("ERR_ONTG2V2_PIN: claude version %r < 2.1.201" % cv)
        banners = {"claude": cv}
    return banners     # kind == "none": pins only (assemble / mock / gate)


def load_jsonl(rel):
    return [json.loads(l) for l in open(PATHS[rel], encoding="utf-8")
            if l.strip()]


def load_jsonl_abs(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def read_template():
    return open(PATHS[_template_rel()], encoding="utf-8").read()


def read_sysprompt():
    return open(PATHS["poc/g2/materials/judge-pB-system-prompt.txt"],
                encoding="utf-8").read().rstrip("\n")


def assemble_prompt(item_text, tmpl):
    if "{{ITEM}}" not in tmpl:
        die("ERR_ONTG2V2_PIN: template lacks {{ITEM}}")
    return tmpl.replace("{{ITEM}}", item_text)


# --------------- invocation (verbatim g2lp/ontg2 forms) ---------------
def run_codex(model, prompt_text, attempt_dir, workdir):
    os.makedirs(attempt_dir, exist_ok=True)
    up = os.path.join(attempt_dir, "user-prompt.txt")
    with open(up, "w", encoding="utf-8") as f:
        f.write(prompt_text)
    last_msg = os.path.join(attempt_dir, "last-message.json")
    events = os.path.join(attempt_dir, "events.jsonl")
    stderr = os.path.join(attempt_dir, "stderr.log")
    cmd = NPX_CODEX + ["exec", "-m", model,
                       "-c", 'model_reasoning_effort="%s"' % EFFORT,
                       "-s", "read-only", "--ignore-user-config",
                       "--skip-git-repo-check", "--ephemeral",
                       "--disable", "memories",
                       "--disable", "standalone_web_search",
                       "-C", workdir, "--color", "never", "--json",
                       "--output-schema",
                       PATHS["poc/g2/materials/output-schema.json"],
                       "-o", last_msg, "-"]
    env = dict(os.environ)
    env["CODEX_HOME"] = CODEX_HOME_ISO
    with open(up, "rb") as fin, open(events, "wb") as fout, \
            open(stderr, "wb") as ferr:
        p = subprocess.run(cmd, stdin=fin, stdout=fout, stderr=ferr, env=env)
    return p.returncode


def run_claude(prompt_text, attempt_dir, workdir, sys_prompt,
               model=HAIKU_MODEL):
    os.makedirs(attempt_dir, exist_ok=True)
    up = os.path.join(attempt_dir, "user-prompt.txt")
    with open(up, "w", encoding="utf-8") as f:
        f.write(prompt_text)
    events = os.path.join(attempt_dir, "events.jsonl")
    stderr = os.path.join(attempt_dir, "stderr.log")
    env = dict(os.environ)
    env.pop("ANTHROPIC_API_KEY", None)
    env.pop("ANTHROPIC_AUTH_TOKEN", None)
    env["MAX_THINKING_TOKENS"] = "0"
    env["DISABLE_AUTOUPDATER"] = "1"
    # --strict-mcp-config: only MCP servers from --mcp-config (none given)
    # may load. Without it, claude.ai MCP connectors nondeterministically
    # attached to 1/62 headless sessions in the 2026-07-12 AC1 pilot despite
    # --tools '' --setting-sources '', tripping the fail-closed tools==[]
    # contract on a semantically correct answer (design section 11.8,
    # kernel-of-truth-ewvh). The validator's tools==[] check is unchanged.
    cmd = ["claude", "-p", "--model", model,
           "--system-prompt", sys_prompt, "--tools", "",
           "--setting-sources", "", "--strict-mcp-config",
           "--no-session-persistence",
           "--output-format", "stream-json", "--verbose"]
    with open(up, "rb") as fin, open(events, "wb") as fout, \
            open(stderr, "wb") as ferr:
        p = subprocess.run(cmd, stdin=fin, stdout=fout, stderr=ferr,
                           cwd=workdir, env=env)
    return p.returncode


def collect_types(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "type" and isinstance(v, str):
                out.append(v)
            collect_types(v, out)
    elif isinstance(obj, list):
        for v in obj:
            collect_types(v, out)


def _cap_text(attempt_dir):
    txt = ""
    for fn in ("stderr.log", "events.jsonl"):
        p = os.path.join(attempt_dir, fn)
        if os.path.exists(p):
            try:
                txt += "\n" + open(p, encoding="utf-8",
                                   errors="replace").read()
            except Exception:
                pass
    return txt


def _cap_hit(text):
    low = text.lower()
    for pat in CAP_PATTERNS:
        if pat in low:
            return pat
    return None


def label_answer(obj):
    if not (isinstance(obj, dict) and list(obj.keys()) == ["answer"]):
        return None, "parse_failure"
    tok = G.normalize_token(obj["answer"])
    if tok not in G.VALID_TOKENS:
        return None, "parse_failure"
    return tok, None


def validate_codex(exit_code, attempt_dir):
    last_msg = os.path.join(attempt_dir, "last-message.json")
    events = os.path.join(attempt_dir, "events.jsonl")
    types = []
    if os.path.exists(events):
        for line in open(events, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            collect_types(ev, types)
    tool_use = any(any(b in t for b in BANNED_TYPE_SUBSTR) for t in types)
    transport = any(any(b in t for b in TRANSPORT_TYPE_SUBSTR) for t in types)
    raw = None
    if os.path.exists(last_msg):
        try:
            raw = open(last_msg, "rb").read().decode("utf-8")
        except Exception:
            raw = None
    if exit_code != 0:
        if raw is None:
            return ("transport", None, None, "transport")
        return ("content_invalid", None, raw, "parse_failure")
    if transport:
        return ("transport", None, raw, "transport")
    if tool_use:
        return ("content_invalid", None, raw, "tool_use_detected")
    obj = G.extract_answer_object(raw)
    if obj is None:
        return ("content_invalid", None, raw, "parse_failure")
    lab, reason = label_answer(obj)
    if lab is None:
        return ("content_invalid", None, raw, reason)
    return ("valid", {"answer": lab}, raw, None)


def validate_claude(exit_code, attempt_dir, model=HAIKU_MODEL):
    events = os.path.join(attempt_dir, "events.jsonl")
    init = result = None
    assistant_blocks = []
    if os.path.exists(events):
        for line in open(events, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            t, st = ev.get("type"), ev.get("subtype")
            if t == "system" and st == "init":
                init = ev
            elif t == "result":
                result = ev
            elif t == "assistant":
                for b in (ev.get("message", {}) or {}).get("content",
                                                           []) or []:
                    assistant_blocks.append(b.get("type"))
    if exit_code != 0:
        return ("transport", None, None, "transport")
    if result is None or result.get("subtype") != "success":
        return ("transport", None, None, "transport")
    mu = result.get("modelUsage") or {}
    # Frozen pB identity check: exact single-key modelUsage. Under the
    # PROVISIONAL fable proxy ONLY, the CLI's background haiku helper key is
    # tolerated alongside the requested model (kernel-of-truth-29nb).
    if model == FABLE_MODEL:
        mu_ok = (model in mu) and set(mu.keys()) <= FABLE_MU_ALLOWED
    else:
        mu_ok = set(mu.keys()) == {model}
    if not (init and init.get("model") == model
            and init.get("apiKeySource") == "none" and mu_ok):
        return ("abort", None, None,
                "identity_mismatch(model=%r apiKeySource=%r modelUsage=%r)"
                % (init.get("model") if init else None,
                   init.get("apiKeySource") if init else None,
                   sorted(mu.keys())))
    tools0 = init.get("tools") == []
    denials0 = (result.get("permission_denials") or []) == []
    turns1 = result.get("num_turns") == 1
    tooluse = "tool_use" in assistant_blocks
    if not (tools0 and denials0 and turns1) or tooluse:
        return ("content_invalid", None, result.get("result"),
                "tool_use_detected")
    raw = result.get("result")
    obj = G.extract_answer_object(raw)
    if obj is None:
        return ("content_invalid", None, raw, "parse_failure")
    lab, reason = label_answer(obj)
    if lab is None:
        return ("content_invalid", None, raw, reason)
    return ("valid", {"answer": lab}, raw, None)


def do_attempt(cfg, prompt, attempt_dir, workdir, sys_prompt):
    if cfg["kind"] == "codex":
        rc = run_codex(cfg["model"], prompt, attempt_dir, workdir)
        status, fields, raw, reason = validate_codex(rc, attempt_dir)
    else:
        rc = run_claude(prompt, attempt_dir, workdir, sys_prompt,
                        model=cfg["model"])
        status, fields, raw, reason = validate_claude(rc, attempt_dir,
                                                      model=cfg["model"])
    hit = G.blinding_scan([os.path.join(attempt_dir, "user-prompt.txt"),
                           os.path.join(attempt_dir, "events.jsonl"),
                           os.path.join(attempt_dir, "stderr.log")])
    if hit:
        raise AbortExperiment("BLINDING file hit token=%r surface=%s dir=%s"
                              % (hit[1], hit[0], attempt_dir))
    ahit = G.answer_blinding_hit(raw)
    if ahit:
        raise AbortExperiment("BLINDING answer-surface hit token=%r dir=%s"
                              % (ahit, attempt_dir))
    return status, fields, raw, reason


def process_item(cfg, prompt, position, base_dir, workdir, sys_prompt, log):
    n_content = 0
    n_transport = 0
    last_reason = None
    for content_k in range(1, MAX_CONTENT + 1):
        while True:
            call_dir = os.path.join(base_dir,
                                    "c%d_t%d" % (content_k, n_transport))
            status, fields, raw, reason = do_attempt(cfg, prompt, call_dir,
                                                     workdir, sys_prompt)
            if status == "abort":
                die("ERR_ONTG2V2_IDENTITY: pos %s %s" % (position, reason))
            if status == "transport":
                cap = _cap_hit(_cap_text(call_dir))
                if cap:
                    raise StopCap("pos %s: cap pattern %r; STOP (no retry). "
                                  "dir=%s" % (position, cap, call_dir))
                n_transport += 1
                if n_transport > MAX_TRANSPORT:
                    die("ERR_ONTG2V2_TRANSPORT: pos %s exceeded %d retries"
                        % (position, MAX_TRANSPORT))
                back = TRANSPORT_BACKOFF[min(n_transport - 1,
                                             len(TRANSPORT_BACKOFF) - 1)]
                log("  pos %s transport failure (try %d), backoff %ds"
                    % (position, n_transport, back))
                time.sleep(back)
                continue
            break
        n_content = content_k
        if status == "valid":
            return {"answer": fields["answer"], "flags": [],
                    "n_content_attempts": n_content,
                    "n_transport_retries": n_transport, "position": position}
        last_reason = reason
        log("  pos %s content attempt %d INVALID (%s)"
            % (position, content_k, reason))
    return {"answer": None,
            "flags": ["judge_no_label", last_reason or "parse_failure"],
            "n_content_attempts": n_content,
            "n_transport_retries": n_transport, "position": position}


def make_workdir(tag):
    out = subprocess.run(["mktemp", "-d",
                          "/tmp/ontg2v2judge%s-workdir.XXXXXX" % tag],
                         capture_output=True, text=True)
    wd = out.stdout.strip()
    if not wd or not os.path.isdir(wd):
        die("ERR_WORKDIR: mktemp failed")
    if os.listdir(wd):
        die("ERR_WORKDIR: workdir not empty: %s" % wd)
    chk = subprocess.run(["git", "-C", wd, "rev-parse",
                          "--is-inside-work-tree"],
                         capture_output=True, text=True)
    if chk.stdout.strip() == "true":
        die("ERR_WORKDIR: %s inside a git repo" % wd)
    return wd


def load_checkpoint(jdir, phase):
    cp = os.path.join(jdir, "checkpoint.jsonl")
    done = {}
    if os.path.exists(cp):
        for l in open(cp, encoding="utf-8"):
            l = l.strip()
            if not l:
                continue
            o = json.loads(l)
            if o.get("phase") == phase:
                done[o["id"]] = o["response"]
    return done


def append_checkpoint(jdir, phase, item_id, response):
    with open(os.path.join(jdir, "checkpoint.jsonl"), "a",
              encoding="utf-8") as f:
        f.write(json.dumps({"phase": phase, "id": item_id,
                            "response": response},
                           sort_keys=True, ensure_ascii=False) + "\n")


def logger(jdir):
    lf = open(os.path.join(jdir, "run-log.txt"), "a", encoding="utf-8")

    def log(m):
        ts = time.strftime("[%H:%M:%S]", time.gmtime())
        lf.write("%s %s\n" % (ts, m))
        lf.flush()
    return log


def _budget_check(run_dir, adding):
    """Hard 788-call ceiling AND live dollar abort at the pinned price bound
    (design section 8; review fix 5). Counts every recorded judge call; the
    bound-implied dollars can never cross the $10 registry usd_cap."""
    cpath = os.path.join(run_dir, "call-count.json")
    n = 0
    if os.path.exists(cpath):
        n = json.load(open(cpath))["n"]
    if n + adding > BUDGET_MAX_CALLS:
        die("ERR_ONTG2V2_BUDGET: %d + %d > %d call ceiling; STOP, no partial "
            "scoring" % (n, adding, BUDGET_MAX_CALLS))
    usd_bound = (n + adding) * PRICE_BOUND_USD_PER_CALL
    if usd_bound > USD_CAP:
        die("ERR_ONTG2V2_BUDGET: bound-implied $%.2f (= %d calls x $%.3f "
            "conservative price bound) > $%.2f hard stop; STOP, no partial "
            "scoring" % (usd_bound, n + adding, PRICE_BOUND_USD_PER_CALL,
                         USD_CAP))
    with open(cpath, "w") as f:
        f.write(json.dumps({"n": n + adding,
                            "usd_bound": usd_bound,
                            "price_bound_usd_per_call":
                                PRICE_BOUND_USD_PER_CALL}) + "\n")


# ---------------------------- phases ----------------------------
def _selftests():
    st = subprocess.run([sys.executable, PATHS["analysis/g3_llmproxy_v3.py"],
                         "--selftest"], capture_output=True, text=True)
    if st.returncode != 0 or "selftest OK" not in st.stdout:
        die("ERR_ONTG2V2_SELFTEST(g3lp helpers): %s%s" % (st.stdout, st.stderr))
    st2 = subprocess.run([sys.executable, PATHS["analysis/ontg2v2.py"],
                          "--selftest"], capture_output=True, text=True)
    if st2.returncode != 0 or "ontg2v2 selftest OK" not in st2.stdout:
        die("ERR_ONTG2V2_SELFTEST(pinned analysis): %s%s"
            % (st2.stdout, st2.stderr))


def _calibration_rows():
    """Preflight calibration: the 2 v1 items THEN the 6 hedge items (design
    section 3a; the v1 items are retained unchanged)."""
    return (load_jsonl("poc/g2/materials/calibration-items.jsonl")
            + load_jsonl(_hedge_cal_rel()))


def _run_cal_block(cfg, rows, jdir, workdir, sys_prompt, log, run_dir,
                   subdir, phase_tag):
    """Run a calibration block (expected answers known); returns results.

    Retry symmetry (design section 11.8, kernel-of-truth-ewvh): calibration
    items go through the SAME process_item retry ladder as real/probe items
    (MAX_TRANSPORT backoff + cap-stop + up to MAX_CONTENT=3 content
    attempts). The 2026-07-12 AC1 pilot lost a semantically correct pB
    answer (cal:hedge-6) to a single-attempt session flake -- the cal block
    was the only single-attempt channel in the harness, so one 1/62-rate
    process artifact could fail the 12/12 cal gate. The judged CONTENT
    contract is unchanged: first valid answer is final; pass iff that
    answer equals the pre-keyed expected label."""
    tmpl = read_template()
    done = load_checkpoint(jdir, phase_tag)
    _budget_check(run_dir, len([r for r in rows if r["id"] not in done]))
    results = []
    for i, cal in enumerate(rows, 1):
        if cal["id"] in done:
            r = done[cal["id"]]
        else:
            prompt = assemble_prompt(cal["item"], tmpl)
            base_dir = os.path.join(jdir, subdir, cal["id"].replace(":", "_"))
            pr = process_item(cfg, prompt, "%s%d" % (phase_tag, i), base_dir,
                              workdir, sys_prompt, log)
            got = pr["answer"]
            reason = (pr["flags"][1] if got is None and len(pr["flags"]) > 1
                      else None)
            r = {"id": cal["id"],
                 "status": "valid" if got is not None else "content_invalid",
                 "got": got, "expected": cal["expected"], "reason": reason,
                 "pass": (got is not None) and (got == cal["expected"]),
                 "n_content_attempts": pr["n_content_attempts"],
                 "n_transport_retries": pr["n_transport_retries"]}
            append_checkpoint(jdir, phase_tag, cal["id"], r)
        results.append(r)
        log("  %s %s got=%s expected=%s => %s"
            % (phase_tag.upper(), r["id"], r["got"], r["expected"],
               "PASS" if r["pass"] else "FAIL"))
    return results


def phase_preflight(pkey, run_dir):
    cfg = JUDGE_CFG[pkey]
    _selftests()
    banners = verify_pins(cfg["kind"])
    jdir = os.path.join(run_dir, cfg["id"])
    os.makedirs(jdir, exist_ok=True)
    workdir = make_workdir(pkey)
    with open(os.path.join(jdir, "workdir-path.txt"), "w") as f:
        f.write(workdir + "\n")
    log = logger(jdir)
    log("PREFLIGHT %s selftests=OK banners=%s workdir=%s"
        % (cfg["id"], json.dumps(banners), workdir))
    sys_prompt = read_sysprompt() if cfg["kind"] == "claude" else None
    results = _run_cal_block(cfg, _calibration_rows(), jdir, workdir,
                             sys_prompt, log, run_dir, "preflight",
                             "preflight-cal")
    ok = all(r["pass"] for r in results)
    status_obj = {"phase": "preflight", "judge": cfg["id"],
                  "rubric": RUBRIC,
                  "banners": banners, "workdir": workdir, "pass": ok,
                  "results": results}
    with open(os.path.join(jdir, "preflight-status.json"), "w") as f:
        f.write(json.dumps(status_obj, indent=2, sort_keys=True) + "\n")
    print("PREFLIGHT %s %s: %s" % (pkey, cfg["id"], "PASS" if ok else "FAIL"),
          flush=True)
    if not ok:
        die("preflight FAILED for %s" % pkey)


def _require_preflight(jdir, pkey):
    ps = os.path.join(jdir, "preflight-status.json")
    if not os.path.exists(ps):
        die("no preflight-status.json for %s; run preflight first" % pkey)
    pf = json.load(open(ps))
    if not pf.get("pass"):
        die("preflight %s did not PASS; refusing" % pkey)
    if pf.get("rubric", "v2") != RUBRIC:
        die("ERR_ONTG2V2_RUBRIC: preflight ran under rubric %r but this "
            "invocation is %r; rubrics may never mix within a run"
            % (pf.get("rubric", "v2"), RUBRIC))
    workdir = open(os.path.join(jdir, "workdir-path.txt")).read().strip()
    if not os.path.isdir(workdir):
        die("recorded workdir missing: %s" % workdir)
    return workdir


def _require_pilot_pass(run_dir):
    """Pilot-stop semantics (design section 4): NO full-arm call may precede
    a green pilot gate."""
    ps = os.path.join(run_dir, "pilot-status.json")
    if not os.path.exists(ps):
        die("ERR_ONTG2V2_PILOT: no pilot-status.json; run pilot + pilotgate "
            "first (no full-arm call may precede a green pilot)")
    st = json.load(open(ps))
    if not st.get("pass"):
        die("ERR_ONTG2V2_PILOT: pilot gate FAILED (%s); the full run is "
            "never launched" % st.get("channel", "unknown channel"))
    if st.get("rubric", "v2") != RUBRIC:
        die("ERR_ONTG2V2_RUBRIC: pilot gate passed under rubric %r but this "
            "invocation is %r; rubrics may never mix within a run"
            % (st.get("rubric", "v2"), RUBRIC))


def _run_block(pkey, arm, run_dir, phase, rows, n_expected, nolabel_cap,
               pos_prefix, out_base=None):
    if arm not in ARMS:
        die("ERR_ONTG2V2_ARM: %r" % arm)
    cfg = JUDGE_CFG[pkey]
    banners = verify_pins(cfg["kind"])
    jdir = os.path.join(run_dir, cfg["id"])
    workdir = _require_preflight(jdir, pkey)
    log = logger(jdir)
    manifest = json.load(open(os.path.join(MAT, "manifest.json")))
    key = "judge-%s|%s|%s" % (pkey, arm, phase)
    order = manifest["orders"][key]
    seed = manifest["seeds"][key]
    recomputed = sorted(order,
                        key=lambda i: sha_bytes(("%s|%s" % (seed, i))
                                                .encode()))
    if recomputed != order:
        die("ERR_ONTG2V2_ORDER: manifest %s order != recomputed" % key)
    if len(order) != n_expected:
        die("ERR_ONTG2V2_ORDER: %s has %d items != %d"
            % (key, len(order), n_expected))
    by_id = {r["id"]: r for r in rows}
    tmpl = read_template()
    sys_prompt = read_sysprompt() if cfg["kind"] == "claude" else None
    block = "%s-%s" % (arm, phase)
    done = load_checkpoint(jdir, block)
    _budget_check(run_dir, len([i for i in order if i not in done]))
    with open(os.path.join(jdir, "%s-position-map.jsonl" % block), "w",
              encoding="utf-8") as f:
        for i, iid in enumerate(order, 1):
            f.write(json.dumps({"position": "%s%d" % (pos_prefix, i),
                                "id": iid}, sort_keys=True) + "\n")
    log("%s %s start n=%d resume_done=%d banners=%s"
        % (block.upper(), cfg["id"], len(order), len(done),
           json.dumps(banners)))
    responses = {}
    n_nolabel = 0
    t0 = time.time()
    for i, iid in enumerate(order, 1):
        if iid in done:
            r = done[iid]
        else:
            base_dir = os.path.join(jdir, block, iid.replace(":", "_"))
            prompt = assemble_prompt(by_id[iid]["item"], tmpl)
            r = process_item(cfg, prompt, "%s%d" % (pos_prefix, i), base_dir,
                             workdir, sys_prompt, log)
            r["id"] = iid
            r["judge"] = cfg["id"]
            append_checkpoint(jdir, block, iid, r)
        responses[iid] = r
        if r.get("answer") is None:
            n_nolabel += 1
        if i % 10 == 0 or i == len(order):
            log("  %s %d/%d nolabel=%d elapsed=%.0fs"
                % (block, i, len(order), n_nolabel, time.time() - t0))
        if n_nolabel > nolabel_cap:
            die("ERR_ONTG2V2_NOLABEL: %d no-label > %d in %s %s; ABORT"
                % (n_nolabel, nolabel_cap, cfg["id"], block))
    banners_after = verify_pins(cfg["kind"])
    if banners_after != banners:
        die("ERR_ONTG2V2_PIN: banner drift")
    fld = ["id", "answer", "flags", "n_content_attempts",
           "n_transport_retries", "position", "judge"]
    rp = os.path.join(out_base or BASE, "judge-%s-%s-%s-responses.jsonl"
                      % (pkey, arm, phase))
    with open(rp, "w", encoding="utf-8") as f:
        for iid in sorted(responses):
            r = responses[iid]
            f.write(json.dumps({k: r.get(k) for k in fld}, sort_keys=True,
                               ensure_ascii=False) + "\n")
    log("%s %s done nolabel=%d -> %s"
        % (block.upper(), cfg["id"], n_nolabel, rp))
    print("%s_DONE %s nolabel=%d file=%s"
          % (block.upper(), pkey, n_nolabel, rp), flush=True)


def _proxy_out_base(run_dir):
    """Proxy runs keep response files in run_dir; frozen path uses BASE."""
    return run_dir if PA_PROXY else None


def phase_real(pkey, arm, run_dir):
    _require_pilot_pass(run_dir)
    _run_block(pkey, arm, run_dir, "real",
               load_jsonl("poc/ontology-import-g2/materials/%s"
                          % ARM_FILE[arm]),
               N_ITEMS, NOLABEL_ABORT_REAL, "",
               out_base=_proxy_out_base(run_dir))


def phase_probe(pkey, arm, run_dir):
    _require_pilot_pass(run_dir)
    _run_block(pkey, arm, run_dir, "probe",
               load_jsonl("poc/ontology-import-g2/materials/probes-%s.jsonl"
                          % arm),
               N_PROBES, NOLABEL_ABORT_PROBE, "p",
               out_base=_proxy_out_base(run_dir))


def phase_hedgeflip(pkey, arm, run_dir):
    if arm not in HEDGED_ARMS:
        die("ERR_ONTG2V2_ARM: hedgeflip probes exist only for a2|a3 (A1 has "
            "no hedges)")
    _require_pilot_pass(run_dir)
    _run_block(pkey, arm, run_dir, "hedgeflip",
               load_jsonl("poc/ontology-import-g2-v2/probes-hedgeflip-%s"
                          ".jsonl" % arm),
               N_HEDGEFLIP, NOLABEL_ABORT_PROBE, "h",
               out_base=_proxy_out_base(run_dir))


def phase_pilot(pkey, run_dir):
    """STAGE P (design section 4): 6 hedge-cal + 40 pinned stratified real
    A3 items + 4 hedge-flip probes, per judge. Runs BEFORE any full-arm
    call; labels are instrument evidence only."""
    cfg = JUDGE_CFG[pkey]
    banners = verify_pins(cfg["kind"])
    jdir = os.path.join(run_dir, cfg["id"])
    workdir = _require_preflight(jdir, pkey)
    log = logger(jdir)
    log("PILOT %s start banners=%s" % (cfg["id"], json.dumps(banners)))
    sys_prompt = read_sysprompt() if cfg["kind"] == "claude" else None
    # (a) hedge-calibration items, file order like preflight (6 under the
    # frozen v2 rubric; 8 under --rubric v22)
    cal_rows = load_jsonl(_hedge_cal_rel())
    cal_results = _run_cal_block(cfg, cal_rows, jdir, workdir, sys_prompt,
                                 log, run_dir, "pilotcal", "pilot-cal")
    with open(os.path.join(BASE if run_dir == BASE else run_dir,
                           "judge-%s-pilotcal-responses.jsonl" % pkey), "w",
              encoding="utf-8") as f:
        for r in cal_results:
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")
    # (b) 40 pinned stratified real A3 items (pilot-manifest order seed)
    pm = json.load(open(
        PATHS["poc/ontology-import-g2-v2/pilot-manifest.json"]))
    a3_rows = load_jsonl("poc/ontology-import-g2/materials/%s"
                         % ARM_FILE["a3"])
    pilot_rows = [r for r in a3_rows if r["id"] in set(pm["ids"])]
    if len(pilot_rows) != N_PILOT:
        die("ERR_ONTG2V2_PILOT: %d pilot rows != %d"
            % (len(pilot_rows), N_PILOT))
    _run_block(pkey, "a3", run_dir, "pilot", pilot_rows, N_PILOT,
               NOLABEL_ABORT_PILOT, "s",
               out_base=(run_dir if run_dir != BASE else BASE))
    # (c) 4 pinned hedge-flip probes
    hf_rows = load_jsonl("poc/ontology-import-g2-v2/probes-hedgeflip-a3"
                         ".jsonl")
    flip_rows = [r for r in hf_rows if r["id"] in set(pm["hedgeflip_probe_ids"])]
    if len(flip_rows) != N_PILOTFLIP:
        die("ERR_ONTG2V2_PILOT: %d pilot flip rows != %d"
            % (len(flip_rows), N_PILOTFLIP))
    _run_block(pkey, "a3", run_dir, "pilotflip", flip_rows, N_PILOTFLIP,
               1, "f", out_base=(run_dir if run_dir != BASE else BASE))
    print("PILOT_DONE %s" % pkey, flush=True)


def _kappa(t):
    """Cohen kappa -- CO-REPORTED ONLY (design section 11), never gated."""
    n = t["both_yes"] + t["both_no"] + t["a_yes_b_no"] + t["a_no_b_yes"]
    if n == 0:
        return None
    po = (t["both_yes"] + t["both_no"]) / n
    pa = (t["both_yes"] + t["a_yes_b_no"]) / n
    pb = (t["both_yes"] + t["a_no_b_yes"]) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    if pe == 1.0:
        return 1.0
    return (po - pe) / (1 - pe)


def _ac1(t):
    """Gwet AC1 -- THE GATED pair statistic (design section 11.2-11.3);
    byte-consistent with analysis/ontg2v2.py::agree_stats. pe_gamma =
    2*pi*(1-pi) <= 0.5, so no degenerate denominator for n > 0."""
    n = t["both_yes"] + t["both_no"] + t["a_yes_b_no"] + t["a_no_b_yes"]
    if n == 0:
        return None
    po = (t["both_yes"] + t["both_no"]) / n
    pa = (t["both_yes"] + t["a_yes_b_no"]) / n
    pb = (t["both_yes"] + t["a_no_b_yes"]) / n
    pi = (pa + pb) / 2.0
    pe_g = 2.0 * pi * (1.0 - pi)
    return (po - pe_g) / (1.0 - pe_g)


def _pilot_metrics(resp_dir):
    """Mechanical pilot block from the six pilot response files."""
    DEC = ("yes", "no")
    cal_correct = 0
    dec = {}
    hf = {}
    labels = {}
    for pk in ("pA", "pB"):
        calp = os.path.join(resp_dir, "judge-%s-pilotcal-responses.jsonl" % pk)
        if not os.path.exists(calp):
            die("missing %s" % calp)
        cal_correct += sum(1 for r in load_jsonl_abs(calp) if r.get("pass"))
        rp = os.path.join(resp_dir, "judge-%s-a3-pilot-responses.jsonl" % pk)
        if not os.path.exists(rp):
            die("missing %s" % rp)
        rows = {r["id"]: r for r in load_jsonl_abs(rp)}
        labels[pk] = rows
        dec[pk] = sum(1 for r in rows.values() if r.get("answer") in DEC)
        fp = os.path.join(resp_dir,
                          "judge-%s-a3-pilotflip-responses.jsonl" % pk)
        if not os.path.exists(fp):
            die("missing %s" % fp)
        frows = load_jsonl_abs(fp)
        hf[pk] = {"n_labelled": sum(1 for r in frows
                                    if r.get("answer") is not None),
                  "n_false_sat": sum(1 for r in frows
                                     if r.get("answer") == "yes")}
    if sorted(labels["pA"]) != sorted(labels["pB"]):
        die("ERR_ONTG2V2_PILOT: pilot id sets differ between judges")
    t = {"both_yes": 0, "both_no": 0, "a_yes_b_no": 0, "a_no_b_yes": 0}
    for iid in labels["pA"]:
        a = labels["pA"][iid].get("answer")
        b = labels["pB"][iid].get("answer")
        if a in DEC and b in DEC:
            if a == "yes" and b == "yes":
                t["both_yes"] += 1
            elif a == "no" and b == "no":
                t["both_no"] += 1
            elif a == "yes":
                t["a_yes_b_no"] += 1
            else:
                t["a_no_b_yes"] += 1
    return {"n_items": N_PILOT, "cal_correct": cal_correct, "table": t,
            "decisive_pA": dec["pA"], "decisive_pB": dec["pB"],
            "hedgeflip_pA": hf["pA"], "hedgeflip_pB": hf["pB"]}


def phase_pilotgate(run_dir, resp_dir=None, mock=False):
    """Evaluate the Stage-P gate (design section 4). GREEN -> the full run
    may proceed. ANY failure -> STOP: assemble the pilot-only result via the
    pinned analysis; the mechanical verdict is INSTRUMENT-INVALID (pilot
    channel named); the full run is NEVER launched."""
    verify_pins("none")
    resp_dir = resp_dir or run_dir
    pm = _pilot_metrics(resp_dir)
    g = _ac1(pm["table"])
    k = _kappa(pm["table"])           # co-reported only (design section 11)
    fs = {pk: (pm["hedgeflip_%s" % pk]["n_false_sat"]
               / pm["hedgeflip_%s" % pk]["n_labelled"]
               if pm["hedgeflip_%s" % pk]["n_labelled"] else 1.0)
          for pk in ("pA", "pB")}
    channels = []
    if pm["cal_correct"] < PILOT_CAL_MIN:
        channels.append("hedge-calibration %d/%d < %d"
                        % (pm["cal_correct"], PILOT_CAL_MIN, PILOT_CAL_MIN))
    if g is None or g < PILOT_AC1_MIN:
        channels.append("pilot AC1_A3 %s < 0.65 (table %s; kappa %s "
                        "co-reported, never gated)"
                        % ("%.4f" % g if g is not None else "undefined",
                           json.dumps(pm["table"], sort_keys=True),
                           "%.4f" % k if k is not None else "undefined"))
    if min(pm["decisive_pA"], pm["decisive_pB"]) < PILOT_DECISIVE_MIN:
        channels.append("decisive %d/40 < 36"
                        % min(pm["decisive_pA"], pm["decisive_pB"]))
    if max(fs.values()) > PILOT_HF_FS_MAX:
        channels.append("hedge-flip false-sat %.2f > 0.25" % max(fs.values()))
    ok = not channels
    status = {"phase": "pilotgate", "pass": ok, "pa_proxy": PA_PROXY,
              "rubric": RUBRIC,
              "ac1_a3": g, "kappa_a3_coreported": k, "metrics": pm,
              "hedgeflip_false_sat": fs,
              "channel": "; ".join(channels) if channels else None,
              "gate": {"cal_correct_min": PILOT_CAL_MIN,
                       "ac1_a3_min": PILOT_AC1_MIN,
                       "decisive_min_per_judge": PILOT_DECISIVE_MIN,
                       "hedgeflip_false_sat_max_per_judge": PILOT_HF_FS_MAX}}
    with open(os.path.join(run_dir, "pilot-status.json"), "w") as f:
        f.write(json.dumps(status, indent=2, sort_keys=True) + "\n")
    print("PILOTGATE %s%s" % ("GREEN" if ok else "FAIL",
                              "" if ok else " (%s)" % status["channel"]),
          flush=True)
    if not ok:
        # designed early stop: pilot-only assembly, INSTRUMENT-INVALID
        _assemble(resp_dir, run_dir, mock=mock, pilot_only=True)
        return False
    return True


# ---------------------------- assemble ----------------------------
def _assemble(resp_dir, out_dir, mock=False, pilot_only=False):
    """Pure counting + the pinned analysis (analysis/ontg2v2.py).
    Vacuity-zeroing per plan section 7.3; AC1/kappa on raw labels; pilot labels
    NEVER scored (instrument evidence only, design section 4)."""
    verify_pins("none")
    items = load_jsonl("poc/g2/materials/items.jsonl")
    ids = sorted(i["id"] for i in items)
    rule_of = {i["id"]: i["rule"] for i in items}
    soft = {r["position"]["g2_item"]: r for r in
            load_jsonl("data/onto-softtype/soft-type-candidates.jsonl")}
    a0 = {r["id"]: r for r in load_jsonl("poc/g2/labels-proxy.jsonl")}

    pilot = _pilot_metrics(resp_dir)
    metrics = {"n_items": N_ITEMS, "baseline_yes": 33, "pins_ok": True,
               "pilot": pilot}

    if pilot_only:
        metrics["pilot_only"] = True
        analysis_out = _run_analysis(metrics)
        return _write_result(out_dir, metrics, analysis_out, None, mock,
                             pilot_only=True)

    def load_resp(pk, arm, phase):
        p = os.path.join(resp_dir, "judge-%s-%s-%s-responses.jsonl"
                         % (pk, arm, phase))
        if not os.path.exists(p):
            die("missing %s" % p)
        return {r["id"]: r for r in load_jsonl_abs(p)}

    DEC = ("yes", "no")
    genrep = json.load(open(os.path.join(V1MAT, "generation-report.json")))
    metrics["forbidden_effects_ok"] = (
        genrep["hard_operational_axioms_emitted"] == 0)
    labels_all = {}
    for arm in ARMS:
        ra = load_resp("pA", arm, "real")
        rb = load_resp("pB", arm, "real")
        pa = load_resp("pA", arm, "probe")
        pb = load_resp("pB", arm, "probe")
        if sorted(ra) != ids or sorted(rb) != ids:
            die("ERR_ONTG2V2_IDS: %s response ids != item ids" % arm)
        t = {"both_yes": 0, "both_no": 0, "a_yes_b_no": 0, "a_no_b_yes": 0}
        yes_a = yes_b = dec_a = dec_b = 0
        pu = pc = 0
        r_yes = {"R1": 0, "R3": 0, "R4": 0}
        arm_labels = []
        for iid in ids:
            a = ra[iid].get("answer")
            b = rb[iid].get("answer")
            vac = soft[iid]["vacuous_by_arm"][arm]
            sa = (a == "yes") and not vac        # scored (plan 7.3)
            sb = (b == "yes") and not vac
            if a in DEC:
                dec_a += 1
            if b in DEC:
                dec_b += 1
            yes_a += int(sa)
            yes_b += int(sb)
            if sa:
                r_yes[rule_of[iid]] += 1
            if (sa or sb):
                pu += 1
            if (sa and sb):
                pc += 1
            if a in DEC and b in DEC:
                if a == "yes" and b == "yes":
                    t["both_yes"] += 1
                elif a == "no" and b == "no":
                    t["both_no"] += 1
                elif a == "yes":
                    t["a_yes_b_no"] += 1
                else:
                    t["a_no_b_yes"] += 1
            arm_labels.append({"id": iid, "arm": arm, "answer_pA": a,
                               "answer_pB": b, "vacuous": vac,
                               "scored_pA": int(sa), "scored_pB": int(sb)})
        labels_all[arm] = arm_labels

        def probe_stat(resp):
            lab = sum(1 for r in resp.values()
                      if r.get("answer") is not None)
            fs = sum(1 for r in resp.values() if r.get("answer") == "yes")
            return {"n_labelled": lab, "n_false_sat": fs}
        nv = sum(1 for iid in ids if not soft[iid]["vacuous_by_arm"][arm])
        nv3 = sum(1 for iid in ids if rule_of[iid] == "R3"
                  and not soft[iid]["vacuous_by_arm"][arm])
        metrics[arm] = {
            "yes_pA_scored": yes_a, "yes_pB_scored": yes_b,
            "decisive_pA": dec_a, "decisive_pB": dec_b,
            "agreement_raw": t,
            "probe_pA": probe_stat(pa), "probe_pB": probe_stat(pb),
            "nonvacuous": nv, "nonvacuous_r3": nv3,
            "pair_union_yes": pu, "pair_concordant_yes": pc,
            "r1_yes": r_yes["R1"], "r3_yes": r_yes["R3"],
            "r4_yes": r_yes["R4"],
        }
        if arm in HEDGED_ARMS:
            ha = load_resp("pA", arm, "hedgeflip")
            hb = load_resp("pB", arm, "hedgeflip")
            metrics[arm]["hedgeflip_pA"] = probe_stat(ha)
            metrics[arm]["hedgeflip_pB"] = probe_stat(hb)
    # paired McNemar cells vs frozen A0 (judge-pA labels; scored)
    for arm in ("a2", "a3"):
        b_cell = c_cell = 0
        scored = {r["id"]: r["scored_pA"] for r in labels_all[arm]}
        for iid in ids:
            base_yes = a0[iid]["answer_pA"] == "yes"
            arm_yes = scored[iid] == 1
            if base_yes and not arm_yes:
                b_cell += 1
            if (not base_yes) and arm_yes:
                c_cell += 1
        metrics["mcnemar_%s_b" % arm] = b_cell
        metrics["mcnemar_%s_c" % arm] = c_cell
    # paired A3-vs-A1 cells (overall + R3 slice; design section 5, reported)
    s1 = {r["id"]: r["scored_pA"] for r in labels_all["a1"]}
    s3 = {r["id"]: r["scored_pA"] for r in labels_all["a3"]}
    for tag, subset in (("a3_vs_a1", ids),
                        ("a3_vs_a1_r3",
                         [i for i in ids if rule_of[i] == "R3"])):
        b_cell = sum(1 for i in subset if s1[i] == 1 and s3[i] == 0)
        c_cell = sum(1 for i in subset if s1[i] == 0 and s3[i] == 1)
        metrics["mcnemar_%s_b" % tag] = b_cell
        metrics["mcnemar_%s_c" % tag] = c_cell

    analysis_out = _run_analysis(metrics)
    return _write_result(out_dir, metrics, analysis_out, labels_all, mock)


def _run_analysis(metrics):
    p = subprocess.run([sys.executable, PATHS["analysis/ontg2v2.py"]],
                       input=json.dumps({"metrics": metrics}) + "\n",
                       capture_output=True, text=True)
    if p.returncode != 0:
        die("ERR_ONTG2V2_ANALYSIS: %s" % p.stderr)
    return json.loads(p.stdout)


def _write_result(out_dir, metrics, analysis_out, labels_all, mock,
                  pilot_only=False):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "analysis-output.json"), "w") as f:
        f.write(json.dumps(analysis_out, indent=1, sort_keys=True) + "\n")
    labels_sha = None
    if labels_all is not None:
        lp = os.path.join(out_dir, "labels-ontg2v2.jsonl")
        with open(lp, "w", encoding="utf-8") as f:
            for arm in ARMS:
                for r in labels_all[arm]:
                    f.write(json.dumps(r, sort_keys=True, ensure_ascii=False)
                            + "\n")
        labels_sha = file_sha(lp)
    result = {
        "schema": "ontg2v2-result/1",
        "status": ("MOCK -- MECHANICS ONLY, NO EVIDENCE" if mock
                   else ("PROVISIONAL-ON-FABLE-PROXY-pA -- EARLY READ, NOT "
                         "THE FROZEN-INSTRUMENT GRADE" if PA_PROXY
                         else "PROVISIONAL-ON-LLM-PROXY")),
        "pa_proxy": ({"proxy": "fable", "judge_pA": JUDGE_CFG["pA"],
                      "frozen_pA": "judge-pA-gpt56sol (codex, usage-capped "
                                   "2026-07-12)",
                      "reconcile": "re-run the FROZEN instrument (pA="
                                   "GPT-5.6-Sol) over the same 84 items when "
                                   "the cap resets; on material AC1/verdict "
                                   "difference the GPT-5.6 frozen grade "
                                   "GOVERNS (kernel-of-truth-29nb)"}
                     if PA_PROXY else None),
        "experiment": "g2-import-v2",
        "pilot_only": pilot_only,
        "baseline": {"source": "poc/g2/labels-proxy.jsonl (FROZEN g2 "
                               "primary readout; no new A0 calls)",
                     "yes": 33, "n": 84},
        "metrics": metrics,
        "analysis": analysis_out,
        "labels_sha256": labels_sha,
        "disclosure": (
            ("PROVISIONAL-ON-FABLE-PROXY-pA: judge-pA here is claude-fable-5 "
             "via the pB headless-claude machinery (codex/GPT-5.6 capped "
             "2026-07-12) -- BOTH judges are Anthropic-family, so cross-"
             "vendor pair stability is NOT measured by this run; AC1/kappa "
             "here are same-family pair stability only. " if PA_PROXY
             else "") +
            "PROVISIONAL-ON-LLM-PROXY (directive #11): judge-pA GPT-5.6-Sol "
            "primary, judge-pB Claude Haiku 4.5 sensitivity (vendor-family "
            "overlap with the materials' authoring agents DISCLOSED, never "
            "sole gold). AC1/kappa are pair stability, never human-agreement "
            "evidence. Pilot labels are instrument evidence only, discarded "
            "from all scoring (v2 design section 4). v2 labels are minted "
            "under the v2 sentence-force rubric and are never row-merged or "
            "trend-compared with the quarantined v1 labels except as "
            "instrument-repair before/after evidence. The later two-human "
            "adjudicated gold remains the sole authority for any permanent "
            "scientific adoption; reconcile + re-run when it arrives. The "
            "primary gate is a point-estimate engineering gate (>=34/84), "
            "not a claim of statistical superiority."),
    }
    rpath = os.path.join(out_dir, "result.json")
    with open(rpath, "w") as f:
        f.write(json.dumps(result, indent=1, sort_keys=True) + "\n")
    summary = {"pilot_valid": analysis_out["gates"]["pilot_valid"],
               "instrument_valid":
                   analysis_out["gates"]["instrument_valid"],
               "informative_valid":
                   analysis_out["gates"]["informative_valid"]}
    if not pilot_only:
        summary.update({"a1_yes": metrics["a1"]["yes_pA_scored"],
                        "a2_yes": metrics["a2"]["yes_pA_scored"],
                        "a3_yes": metrics["a3"]["yes_pA_scored"],
                        "baseline": 33,
                        "primary_pass":
                            analysis_out["analysis"]["primary_pass"],
                        "sep_a3_pass":
                            analysis_out["analysis"]["sep_a3_pass"]})
    print(json.dumps(summary, sort_keys=True))
    print("ASSEMBLE_DONE -> %s" % rpath)
    return analysis_out


def phase_assemble(run_dir):
    _require_pilot_pass(run_dir)
    # pilot response files live in BASE for a real (frozen-path) run;
    # a PROVISIONAL proxy run keeps everything inside its run_dir.
    base = run_dir if PA_PROXY else BASE
    _assemble(base, base)


# ---------------------------- mock ----------------------------
def _mock_answer(scenario, pk, arm, iid, rule):
    h = int(hashlib.sha256(("mock|%s|%s|%s" % (pk, arm, iid))
                           .encode()).hexdigest(), 16)
    hA = int(hashlib.sha256(("mock|pA|%s|%s" % (arm, iid))
                            .encode()).hexdigest(), 16)
    if scenario in ("go", "pilotfail"):
        base = {"a1": 40, "a2": 55, "a3": 65}[arm]
    elif scenario == "nogo":
        base = {"a1": 15, "a2": 25, "a3": 30}[arm]
    elif scenario == "breadth":
        # v1-shaped reality: A1 matches/exceeds A3; the R3 edge vanishes
        if arm == "a1":
            base = 85
        elif arm == "a2":
            base = 30
        else:
            base = 50 if rule == "R3" else 70
    else:  # instrument: judges anti-correlated on real items
        if pk == "pA":
            return "yes" if (h % 2) == 0 else "no"
        return "no" if (hA % 2) == 0 else "yes"
    ans = "yes" if (hA % 100) < base else "no"
    if pk == "pB" and (h % 10) == 0:
        ans = "no" if ans == "yes" else "yes"
    return ans


def _mock_pilot_answer(scenario, pk, iid):
    """Pilot answers: green AC1 in every scenario except pilotfail
    (pB anti-correlated -> pair-agreement collapse, the v1 failure channel
    in its prevalence-robust reading; design section 11)."""
    hA = int(hashlib.sha256(("mockpilot|pA|%s" % iid)
                            .encode()).hexdigest(), 16)
    a = "yes" if (hA % 100) < 65 else "no"
    if pk == "pA":
        return a
    if scenario == "pilotfail":
        return "no" if a == "yes" else "yes"
    h = int(hashlib.sha256(("mockpilot|pB|%s" % iid)
                           .encode()).hexdigest(), 16)
    return ("no" if a == "yes" else "yes") if (h % 10) == 0 else a


MOCK_SCENARIOS = ("go", "nogo", "instrument", "pilotfail", "breadth")


def phase_mock(run_dir, scenario):
    """No-LLM end-to-end mechanics check: synthesizes deterministic judge
    response files for the PILOT and (except pilotfail) the full run, runs
    the REAL pilot gate + assemble + pinned analysis, then evaluates the
    DRAFT record's verdict_rules with the registry evaluator. MOCK output
    is mechanics evidence only."""
    if scenario not in MOCK_SCENARIOS:
        die("mock scenario must be %s" % "|".join(MOCK_SCENARIOS))
    verify_pins("none")
    _selftests()
    mdir = os.path.join(run_dir, "mock-%s" % scenario)
    os.makedirs(mdir, exist_ok=True)
    items = load_jsonl("poc/g2/materials/items.jsonl")
    rule_of = {i["id"]: i["rule"] for i in items}

    def wrow(f, iid, ans, pk):
        f.write(json.dumps({"id": iid, "answer": ans, "flags": [],
                            "n_content_attempts": 1,
                            "n_transport_retries": 0,
                            "position": "m", "judge": "mock-%s" % pk},
                           sort_keys=True) + "\n")

    # ---- pilot files (all scenarios) ----
    pm = json.load(open(
        PATHS["poc/ontology-import-g2-v2/pilot-manifest.json"]))
    cal_rows = load_jsonl(_hedge_cal_rel())
    for pk in ("pA", "pB"):
        with open(os.path.join(mdir, "judge-%s-pilotcal-responses.jsonl"
                               % pk), "w") as f:
            for r in cal_rows:
                f.write(json.dumps({"id": r["id"], "status": "valid",
                                    "got": r["expected"],
                                    "expected": r["expected"],
                                    "reason": None, "pass": True},
                                   sort_keys=True) + "\n")
        with open(os.path.join(mdir, "judge-%s-a3-pilot-responses.jsonl"
                               % pk), "w") as f:
            for iid in pm["ids"]:
                wrow(f, iid, _mock_pilot_answer(scenario, pk, iid), pk)
        with open(os.path.join(mdir, "judge-%s-a3-pilotflip-responses.jsonl"
                               % pk), "w") as f:
            for iid in pm["hedgeflip_probe_ids"]:
                wrow(f, iid, "no", pk)

    # ---- REAL pilot gate mechanics (pilot-stop semantics) ----
    gate_green = phase_pilotgate(mdir, resp_dir=mdir, mock=True)
    if scenario == "pilotfail":
        if gate_green:
            die("MOCK pilotfail: pilot gate unexpectedly GREEN")
        out = json.load(open(os.path.join(mdir, "analysis-output.json")))
    else:
        if not gate_green:
            die("MOCK %s: pilot gate unexpectedly FAILED" % scenario)
        # ---- full-run files ----
        for arm in ARMS:
            rows = load_jsonl("poc/ontology-import-g2/materials/%s"
                              % ARM_FILE[arm])
            probes = load_jsonl("poc/ontology-import-g2/materials/"
                                "probes-%s.jsonl" % arm)
            for pk in ("pA", "pB"):
                with open(os.path.join(mdir,
                                       "judge-%s-%s-real-responses.jsonl"
                                       % (pk, arm)), "w") as f:
                    for r in rows:
                        wrow(f, r["id"], _mock_answer(scenario, pk, arm,
                                                      r["id"],
                                                      rule_of[r["id"]]), pk)
                with open(os.path.join(mdir,
                                       "judge-%s-%s-probe-responses.jsonl"
                                       % (pk, arm)), "w") as f:
                    for pr in probes:
                        ans = ("yes" if scenario == "instrument" and
                               int(hashlib.sha256(pr["id"].encode())
                                   .hexdigest(), 16) % 2 == 0 else "no")
                        wrow(f, pr["id"], ans, pk)
            if arm in HEDGED_ARMS:
                hrows = load_jsonl("poc/ontology-import-g2-v2/"
                                   "probes-hedgeflip-%s.jsonl" % arm)
                for pk in ("pA", "pB"):
                    with open(os.path.join(
                            mdir, "judge-%s-%s-hedgeflip-responses.jsonl"
                            % (pk, arm)), "w") as f:
                        for pr in hrows:
                            ans = ("yes" if scenario == "instrument" and
                                   int(hashlib.sha256(pr["id"].encode())
                                       .hexdigest(), 16) % 2 == 0
                                   else "no")
                            wrow(f, pr["id"], ans, pk)
        out = _assemble(mdir, mdir, mock=True)

    # evaluate the DRAFT record's verdict_rules mechanically
    sys.path.insert(0, os.path.join(REPO, "tools/registry"))
    import kot_common
    rec = json.load(open(os.path.join(
        REPO, "registry/experiments/g2-import-v2.json")))
    doc = {"gates": out["gates"], "analysis": out["analysis"]}
    fired = None
    for rule in rec["verdict_rules"]:
        if kot_common.eval_expr(rule["when"], doc):
            fired = rule["verdict"]
            break
    expected = {"go": "PASS", "nogo": "FAIL",
                "instrument": "INSTRUMENT-INVALID",
                "pilotfail": "INSTRUMENT-INVALID",
                "breadth": "FAIL"}[scenario]
    ok = fired == expected
    detail = ""
    if scenario == "breadth" and ok:
        ok = bool(out["analysis"]["breadth_confound"])
        detail = " breadth_confound=%s" % out["analysis"]["breadth_confound"]
    if scenario == "pilotfail" and ok:
        ok = out["gates"]["pilot_valid"] is False
        detail = " pilot_valid=%s" % out["gates"]["pilot_valid"]
    print("MOCK scenario=%s fired=%s expected=%s%s => %s"
          % (scenario, fired, expected, detail, "GREEN" if ok else "RED"))
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    try:
        if len(sys.argv) < 3:
            die("usage: preflight <pA|pB> <run_dir> | pilot <pA|pB> <run_dir>"
                " | pilotgate <run_dir> | real|probe <pA|pB> <a1|a2|a3> "
                "<run_dir> | hedgeflip <pA|pB> <a2|a3> <run_dir> | "
                "assemble <run_dir> | "
                "mock <run_dir> <go|nogo|instrument|pilotfail|breadth>")
        if "--pa-proxy" in sys.argv:
            i = sys.argv.index("--pa-proxy")
            if i + 1 >= len(sys.argv):
                die("--pa-proxy requires a value (fable)")
            activate_pa_proxy(sys.argv[i + 1])
            del sys.argv[i:i + 2]
        if "--rubric" in sys.argv:
            i = sys.argv.index("--rubric")
            if i + 1 >= len(sys.argv):
                die("--rubric requires a value (v22)")
            activate_rubric(sys.argv[i + 1])
            del sys.argv[i:i + 2]
        mode = sys.argv[1]
        if mode == "preflight":
            phase_preflight(sys.argv[2], sys.argv[3])
        elif mode == "pilot":
            phase_pilot(sys.argv[2], sys.argv[3])
        elif mode == "pilotgate":
            phase_pilotgate(sys.argv[2])
        elif mode == "real":
            phase_real(sys.argv[2], sys.argv[3], sys.argv[4])
        elif mode == "probe":
            phase_probe(sys.argv[2], sys.argv[3], sys.argv[4])
        elif mode == "hedgeflip":
            phase_hedgeflip(sys.argv[2], sys.argv[3], sys.argv[4])
        elif mode == "assemble":
            phase_assemble(sys.argv[2])
        elif mode == "mock":
            phase_mock(sys.argv[2], sys.argv[3])
        else:
            die("unknown mode %r" % mode)
    except StopCap as e:
        sys.stderr.write("RUN_ONTG2V2_STOPCAP: %s\n" % e)
        sys.exit(3)
    except AbortExperiment as e:
        sys.stderr.write("RUN_ONTG2V2_BLINDING_ABORT: %s\n" % e)
        sys.exit(4)
