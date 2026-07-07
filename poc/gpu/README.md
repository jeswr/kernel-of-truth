# poc/gpu — E2 GPU box automation

One command runs E2 once a deploy key exists (see below):

```bash
poc/gpu/launch-e2.sh              # g4dn.xlarge SPOT in eu-west-2, self-terminating
```

The instance boots the current PyTorch DLAMI (queried live via
`aws ec2 describe-images`, never hardcoded), clones the public repo, runs
`poc/e2/runner/e2_runner.py --device cuda` (the full pre-registered E2:
3 model families, 10^4 Mantel permutations, k=100 frequency-matched random
sets), commits `poc/e2/results/` to a branch `results/e2-<UTC stamp>`, pushes
it with the deploy key, and powers off (`shutdown-behavior=terminate`, plus a
4 h failsafe poweroff).

## Files

- `launch-e2.sh` — launcher. Flags: `--dry-run` (validate via EC2 DryRun,
  launch nothing), `--on-demand`, `--fallback` (spot -> on-demand), `--no-push`,
  `--key-name <ec2 keypair>` (optional SSH), `--az <az>`, `--branch <src branch>`.
  Env overrides: `KOT_E2_REGION`, `KOT_E2_REPO`, `KOT_E2_BRANCH`,
  `KOT_E2_DEPLOY_KEY`.
- `user-data-e2.sh.tpl` — first-boot bootstrap template. The deploy key is
  substituted in AT LAUNCH TIME from `~/.ssh/kot-e2-deploy`; no secret exists
  in the repo, ever.
- `setup-deploy-key.sh` — coordinator runs ONCE: mints an ed25519 keypair in
  `~/.ssh/` and prints the `gh repo deploy-key add --allow-write` command for
  the public half. Revoke after the campaign (instructions in the script).
  Accepted risk (documented): user-data is readable via IMDS from within the
  instance; the key is write-scoped to this single public repo.
- `terminate.sh [--yes]` — terminates everything tagged `Name=kot-e2`.

## Networking / IAM

Default VPC, a `default-for-az` subnet (auto-picked), default security group
(no inbound needed — the box only makes outbound HTTPS/SSH), no instance
profile. Tags on instance + volume: `Project=kernel-of-truth`, `Name=kot-e2`.

## Cost note

g4dn.xlarge (1x T4) eu-west-2: ~$0.615/h on-demand; spot historically
~$0.18–0.30/h (poc-design.md's source-report figure: down to ~$0.06/h
marketplace). E2 wall-clock estimate: 30–60 min model extraction (3 small
models x ~120k short contexts each for the random sets) + ~15 min statistics
=> **well under $1 spot, <= ~$1.50 on-demand**, matching the ~$1 E2 line in
docs/poc-design.md. The 4 h failsafe caps a wedged run at ~$2.50 (or ~$0.90
spot). EBS: 100 GB gp3 for the DLAMI root ≈ $0.01/h, deleted on termination.

## Dry-run status (2026-07-07, this box)

`describe-images` (DLAMI resolution) and `describe-subnets` (default-for-az
auto-pick) validated for real in eu-west-2. `launch-e2.sh --dry-run` exercises
the exact `run-instances` request with `--dry-run`; result recorded in the
session log — if this box's IAM role lacks `ec2:RunInstances`, the dry run
reports `UnauthorizedOperation` (checked without secrets) instead of
`DryRunOperation`, and the launch must be run from a role that has it.
