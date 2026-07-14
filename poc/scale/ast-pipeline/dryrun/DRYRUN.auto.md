# DRY RUN result

concepts (deliberately OUTSIDE the 24-concept sample): pull, dig

```json
{
  "codex_s3": {
    "pull": {
      "skipped": false,
      "rc": 2,
      "ok": false,
      "self_flag": null,
      "cost_usd": null,
      "usage": null
    },
    "dig": {
      "skipped": false,
      "rc": 2,
      "ok": false,
      "self_flag": null,
      "cost_usd": null,
      "usage": null
    }
  },
  "codex_s4_merge": {
    "pull": {
      "skipped": false,
      "rc": 2,
      "ok": false,
      "self_flag": null,
      "cost_usd": null,
      "usage": null,
      "merge_inputs": [
        "claude-fable-5",
        "claude-opus-4-8",
        "gpt-5.6-sol"
      ],
      "merge_prompt_sha256": "64461487a5e4da416651ebf6a9cdb47d4043b425e918769136841f87809f4d3f"
    },
    "dig": {
      "skipped": false,
      "rc": 2,
      "ok": false,
      "self_flag": null,
      "cost_usd": null,
      "usage": null,
      "merge_inputs": [
        "claude-fable-5",
        "claude-opus-4-8",
        "gpt-5.6-sol"
      ],
      "merge_prompt_sha256": "57dbbd545207e5ea8999d777ce8fb7ea780eff7726a8f4e5ba86bd1a3a370ee5"
    }
  },
  "claude_p": {
    "dig": {
      "skipped": true,
      "report": "/home/ec2-user/css/kernel/kernel-of-truth/poc/scale/ast-pipeline/dryrun/gen-claude/dig.haiku45.report.json"
    }
  }
}
```

judge-inputs built: ['dig.txt', 'pull.txt']

**VERDICT: FAIL** -- nested `codex exec` and `claude -p` invocation FAILED; see gen-manifest.json + provenance dirs
