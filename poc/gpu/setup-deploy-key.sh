#!/usr/bin/env bash
# One-time coordinator step: mint the kot-e2 deploy key.
# The PRIVATE key stays in ~/.ssh (NEVER in the repo, NEVER committed); the
# public half is registered as a WRITE deploy key on the repo so the GPU box
# can push its results branch. launch-e2.sh embeds the private key into the
# instance user-data AT LAUNCH TIME only.
#
# Security note (accepted, documented): user-data is readable from within the
# instance (IMDS). The key is write-scoped to this one public repo and should
# be REVOKED after the E2 campaign:  gh repo deploy-key list -R "$REPO"
set -euo pipefail

REPO="${KOT_E2_REPO:-jeswr/kernel-of-truth}"
KEY="${KOT_E2_DEPLOY_KEY:-$HOME/.ssh/kot-e2-deploy}"

if [ -f "$KEY" ]; then
  echo "deploy key already exists at $KEY — not overwriting" >&2
else
  ssh-keygen -t ed25519 -N "" -C "kot-e2-deploy" -f "$KEY"
  echo "generated $KEY (private) + $KEY.pub (public)"
fi

echo
echo "Register the PUBLIC key as a write deploy key (pick one):"
echo "  gh repo deploy-key add '$KEY.pub' --repo '$REPO' --title kot-e2-results --allow-write"
echo "  — or paste $KEY.pub at https://github.com/$REPO/settings/keys (tick 'Allow write access')"
echo
echo "After the E2 campaign, REVOKE it:"
echo "  gh repo deploy-key list --repo '$REPO'   # find the id"
echo "  gh repo deploy-key delete <id> --repo '$REPO'"
