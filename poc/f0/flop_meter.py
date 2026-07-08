"""F0 flop-meter — the efficiency-track accounting standard's metric-vector
emitter (design-efficiency-track.md section 3; the `f0-harness` dependency of
the frozen efficiency-track records).

Built once, versioned in-repo here, used by every F-run: formula FLOPs
(F0 section 3.3: 2*N_active*T_total + 2*L*T^2*d_attn per sequence) + measured
wall-clock + memory ledger + $/query. RAW numbers only — no derived
statistics; verdicts belong to the pinned per-experiment analysis scripts
under run-vs-audit separation.

Airtight-ness principle (F0 section 3): every number is either measured on
pinned hardware or computed from a formula stated in F0, and every arm's
total includes its own machinery (encoder, adapter, verifier, store,
retrieval) — nothing is waived.

Promoted VERBATIM (byte-identical class body) from poc/f2/runner/f2_runner.py
on 2026-07-08, where it was built and mock-validated; f2 imports it back from
here. Stdlib-only by design: importable in --mock/--dry-plan paths with no
torch present (the optional torch probe for CUDA peak memory is guarded).

An LM object passed to `seq`/`ledger` must expose: n_active (int), layers
(int), d_attn (int), weight_bytes (int) — see f2_runner.StubLM / HFLM.
"""

from __future__ import annotations

import resource


class FlopMeter:
    def __init__(self, flop_cfg, gpu):
        self.cpu_rate = flop_cfg["cpu_flops_per_s_pinned"]
        self.usd_per_hour = flop_cfg["usd_per_hour"].get(gpu, 0.0)
        self.reset()

    def reset(self):
        self.model_flops = 0.0
        self.verifier_cpu_s = 0.0
        self.latencies_ms = []
        self.t_prefill = 0
        self.t_decode = 0
        self.wall_s = 0.0
        self.n_queries = 0

    def seq(self, lm, t_prefill, t_decode=0):
        """F0 section 3.3: 2*N_active*T_total + 2*L*T^2*d_attn per sequence."""
        t = t_prefill + t_decode
        self.model_flops += 2.0 * lm.n_active * t + 2.0 * lm.layers * t * t * lm.d_attn
        self.t_prefill += t_prefill
        self.t_decode += t_decode

    def verifier(self, cpu_s):
        self.verifier_cpu_s += cpu_s

    def query_done(self, latency_s):
        self.latencies_ms.append(latency_s * 1000.0)
        self.wall_s += latency_s
        self.n_queries += 1

    def _pct(self, p):
        if not self.latencies_ms:
            return None
        s = sorted(self.latencies_ms)
        return s[min(len(s) - 1, int(p * len(s)))]

    def ledger(self, lm_list, store_bytes):
        n = max(1, self.n_queries)
        total = self.model_flops + self.verifier_cpu_s * self.cpu_rate
        weights = sum(lm.weight_bytes for lm in lm_list)
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
        cuda_peak = 0
        try:
            import torch
            if torch.cuda.is_available():
                cuda_peak = torch.cuda.max_memory_allocated()
        except Exception:  # noqa: BLE001
            pass
        return {
            "params": {
                "n_total": int(sum(lm.n_active for lm in lm_list)),
                "n_active": int(sum(lm.n_active for lm in lm_list)),
                "n_trained": 0,
            },
            "memory": {
                "weights_bytes": int(weights),
                "store_bytes": int(store_bytes),
                "process_peak_rss_bytes": int(rss),
                "cuda_peak_bytes": int(cuda_peak),
                "peak_bytes_total": int(weights + store_bytes + max(rss, cuda_peak)),
            },
            "inference_compute": {
                "flops_per_query": total / n,
                "model_flops_per_query": self.model_flops / n,
                "verifier_cpu_s_per_query": self.verifier_cpu_s / n,
                "verifier_flops_per_query_at_pinned_rate":
                    self.verifier_cpu_s * self.cpu_rate / n,
                "tokens_prefill_per_query": self.t_prefill / n,
                "tokens_decode_per_query": self.t_decode / n,
                "latency_ms_p50": self._pct(0.50),
                "latency_ms_p95": self._pct(0.95),
                "usd_per_query": self.wall_s / 3600.0 * self.usd_per_hour / n,
            },
            "training_compute": {"flops": 0, "steps": 0, "tokens": 0,
                                 "note": "inference-only experiment"},
        }
