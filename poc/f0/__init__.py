"""poc/f0 — the F0 measurement-standard package (design-efficiency-track.md
section 3): the shared metric-vector emitter every efficiency-track (F-*) run
uses, satisfying the `f0-harness` depends_on gate of the frozen records.

Public surface: FlopMeter (flop_meter.py). Its `ledger()` return value IS the
`metrics.metric_vector` contract consumed by the pinned analysis scripts
(params / memory / inference_compute / training_compute) — changing any key
here is an interface change to every pinned analysis and must not happen
casually.
"""

from .flop_meter import FlopMeter  # noqa: F401

__all__ = ["FlopMeter"]
