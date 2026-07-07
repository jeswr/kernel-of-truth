# poc/gpu — E2 GPU box automation

Two ways to get E2 results off the GPU box. **Option B (pull) is the default**:
it needs no standing credentials anywhere — nothing in the repo, nothing in
user-data, nothing registered on GitHub.

| | **A: deploy-key push** | **B: pull (no credentials)** |
|---|---|---|
| launch | `launch-e2.sh` | `launch-e2-pull.sh` |
| results | box pushes branch `results/e2-<stamp>` with a **write deploy key** embedded in user-data | box writes `/opt/e2/results/` + `DONE` marker; coordinator runs `collect-e2.sh <iid>` to scp them off and terminate |
| standing credential | GitHub write deploy key (revoke after campaign) | none |
| user-data secret | private key (readable via IMDS on-box — accepted risk) | none (launcher refuses to launch if the rendered user-data matches credential patterns) |
| network inbound | none | 22/tcp from the coordinator's **private** IP /32 only (same VPC), SG `kot-e2-sg` |
| unattended? | yes — box pushes and dies on its own | needs the coordinator (or a loop) to run `collect-e2.sh` within the 4 h failsafe window |
| when to use | coordinator box will be offline during the run | everything else (default) |

## Option B usage (pull path)

```bash
poc/gpu/launch-e2-pull.sh --dry-run   # validate everything, launch nothing
poc/gpu/launch-e2-pull.sh             # spot g4dn.xlarge; prints <instance-id>
poc/gpu/collect-e2.sh <instance-id>   # poll DONE, scp results, terminate box
```

`launch-e2-pull.sh` idempotently (a) mints a LOCAL ed25519 key
`~/.ssh/kot-e2-ephemeral` and imports the public half as EC2 key pair
`kernel-of-truth-e2` (delete+reimport if fingerprints diverge); (b) creates SG
`kot-e2-sg` (tagged `Project=kernel-of-truth`, default VPC) allowing 22/tcp
ONLY from this box's IMDSv2-fetched private IP /32; (c) launches the same
DLAMI/user-data structure as Option A but with the git-push section replaced
by "write `/opt/e2/results/`, `touch /opt/e2/results/DONE`, wait". The 4 h
failsafe poweroff (+ `shutdown-behavior=terminate`) still caps a wedged or
never-collected run.

`collect-e2.sh <iid>` polls `describe-instances` + ssh (ephemeral key,
per-run known_hosts) for the DONE marker, scps `/opt/e2/results/` into
`poc/e2/results-incoming/<UTC stamp>/`, verifies `results-e2*.json` parses and
echoes its `OUTCOME:` line, then terminates the instance. It does **not**
git-commit — the coordinator reviews and commits deliberately. Flags:
`--cleanup` (afterwards delete the EC2 key pair + SG), `--cleanup-only`
(just delete them), `--timeout-mins N` (default 240).

**Failure trace:** if DONE never appears, collect-e2.sh pulls
`/var/log/cloud-init-output.log`, `/var/log/kot-e2-userdata.log`,
`/var/log/kot-e2-run.log` (+ any partial results) over ssh — or
`aws ec2 get-console-output` if ssh is unreachable — into the same incoming
dir BEFORE terminating, so a failed run always leaves a diagnosable trace.

## Option A usage (deploy-key push path)

```bash
poc/gpu/setup-deploy-key.sh           # once; register printed key w/ write access
poc/gpu/launch-e2.sh                  # box pushes results/e2-<stamp>, self-terminates
```

## Files

- `launch-e2-pull.sh` / `user-data-e2-pull.sh.tpl` / `collect-e2.sh` — Option B
  (above). Env overrides: `KOT_E2_REGION`, `KOT_E2_REPO`, `KOT_E2_BRANCH`,
  `KOT_E2_EPHEMERAL_KEY`.
- `launch-e2.sh` — Option A launcher. Flags: `--dry-run`, `--on-demand`,
  `--fallback` (spot -> on-demand), `--no-push`, `--key-name <ec2 keypair>`,
  `--az <az>`, `--branch <src branch>`. Env: `KOT_E2_REGION`, `KOT_E2_REPO`,
  `KOT_E2_BRANCH`, `KOT_E2_DEPLOY_KEY`. (`--dry-run`, `--az`, `--branch`
  also exist on `launch-e2-pull.sh`.)
- `user-data-e2.sh.tpl` — Option A first-boot template. The deploy key is
  substituted AT LAUNCH TIME from `~/.ssh/kot-e2-deploy`; no secret exists in
  the repo, ever.
- `setup-deploy-key.sh` — Option A one-time key mint; prints the
  `gh repo deploy-key add --allow-write` command. Revoke after the campaign.
  Accepted risk (documented): user-data is readable via IMDS from within the
  instance; the key is write-scoped to this single public repo.
- `terminate.sh [--yes]` — terminates everything tagged `Name=kot-e2`
  (both options tag instances identically).

## Networking / IAM

Default VPC, a `default-for-az` subnet (auto-picked), no instance profile.
Tags on instance + volume: `Project=kernel-of-truth`, `Name=kot-e2`.
Option A uses the default SG (no inbound); Option B creates `kot-e2-sg`
(inbound 22 from the coordinator's private /32 only; default all-egress).
Option B stays entirely inside the approved IAM policy: RunInstances
(g4dn/g5/t3.micro, tagged at launch), key pairs named `kernel-of-truth-*`,
security groups tagged `Project=kernel-of-truth`, `Describe*`,
`GetConsoleOutput`, Terminate/Stop on Project-tagged instances — all
eu-west-2.

## Cost note

g4dn.xlarge (1x T4) eu-west-2: ~$0.615/h on-demand; spot historically
~$0.18–0.30/h (poc-design.md's source-report figure: down to ~$0.06/h
marketplace). E2 wall-clock estimate: 30–60 min model extraction (3 small
models x ~120k short contexts each for the random sets) + ~15 min statistics
=> **well under $1 spot, <= ~$1.50 on-demand**, matching the ~$1 E2 line in
docs/poc-design.md. The 4 h failsafe caps a wedged run at ~$2.50 (or ~$0.90
spot). EBS: 100 GB gp3 for the DLAMI root ≈ $0.01/h, deleted on termination.
Option B adds idle time between DONE and collection (poll interval 60 s —
negligible).

## Validation status

**Option A dry-run (2026-07-07):** `describe-images` + `describe-subnets`
validated for real; `launch-e2.sh --dry-run` exercises the exact
`run-instances` request via EC2 DryRun (see session log note re IAM).

**Option B (2026-07-07, this box, all free-tier API calls — no instance
launched):** IMDSv2 private-IP fetch real (172.31.2.135); `import-key-pair`
as `kernel-of-truth-e2` (Project-tagged) real, fingerprint normalisation
verified against the live AWS response format (AWS pads base64, no `SHA256:`
prefix); `kot-e2-sg` create + tag + 22/tcp-from-/32 authorize real; full
`launch-e2-pull.sh --dry-run` re-run proved idempotency (no dupes);
`run-instances --dry-run` (spot, key+SG attached) returned `DryRunOperation`
= request would have succeeded; `get-console-output` real (fetched this box's
own console); `collect-e2.sh --cleanup-only` deleted the key pair + SG for
real and both verified gone. AMI resolved to an Ubuntu 24.04 DLAMI (ssh user
`ubuntu`; collect-e2.sh tries `ubuntu` then `ec2-user`).
