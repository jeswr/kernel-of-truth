"""S2 RNG discipline: Philox + SeedSequence, named substreams, draw ordering.

Per S2/R8g: ONE base seed; per-(config,rep) stream
SeedSequence([BASE_SEED, config_index, replication_index]); split ONCE by
.spawn(13) into the fixed-purpose named children (indices in pins.SS_*).
Each child seeds a numpy.random.Generator over Philox — the ONE pinned
generator.
"""
import numpy as np
import pins


def rep_substreams(config_index: int, replication_index: int):
    """Return the 13 named Philox Generators for one (config, rep).

    Zero-based config_index and replication_index (S2).  The spawn order is
    normative (pins.SS_*).  Any single replication is reproducible in isolation
    and independent of execution order / parallelism.
    """
    ss = np.random.SeedSequence([pins.BASE_SEED, int(config_index), int(replication_index)])
    children = ss.spawn(pins.N_SUBSTREAMS)
    return [np.random.Generator(np.random.Philox(c)) for c in children]


def beta_cal_stream(config_index: int):
    """Dedicated per-cell bounded-Beta gate-threshold calibration stream
    (S4.4): SeedSequence([BASE_SEED, config_index, 999_999_999])."""
    ss = np.random.SeedSequence([pins.BASE_SEED, int(config_index), pins.BETA_CAL_STREAM_TAG])
    return np.random.Generator(np.random.Philox(ss))
