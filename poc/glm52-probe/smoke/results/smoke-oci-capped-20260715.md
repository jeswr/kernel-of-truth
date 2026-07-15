# GLM-5.2 capped backend smoke — GO-FULL-GLM52 (acct4/OCI, 2026-07-15)

RAM-capped re-run (RAM_GB=55, CAP_RAISE=0) of the PROXY-ONLY smoke. Resolves the sole failed gate.

- **RSS 45.73 GB** (was 245 GB) → rss_lt_60gb=True (~14 GB headroom). Root cause: unset RAM_GB auto-budgeted 88% of the instance's ~256 GB; explicit 55 GiB budget + disabled auto-raise fixed it.
- **disk 15.96 GB/s O_DIRECT** (buffered 1.69) ≥ 1 GB/s ✓ — the make-or-break B3: OCI local ephemeral NVMe is fast.
- 12/12 probes traced, integrity_clean, repeat_byte_identical, arch self-test 32/32 ✓
- s/prefill 16.4s (short probes); projected **Wave-A 2.19 h / $2.51** (caps 20 h / $25) ✓
- staging 383.76 GB / 453 files / 1370s (~22.8 min) straight to ephemeral SSD; manifest b21bb4a4
- total run ~27 min, est cost $0.52 (≤$1 authorization)
- **VERDICT: GO-FULL-GLM52 — the 480-item Wave-A is ready to dispatch on this OCI/RAM-capped config.**
- Flags: s/prefill measured on 7-30-token probes (Wave-A items may be longer → est ≤3× → ~6.5h/$7.5, still < $25); placement provider "unknown" (OCI IMDS unreachable — binding non-AWS = the cloud="oci" scheduling constraint); free_gb_after overflow is cosmetic.
