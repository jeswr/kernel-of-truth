#!/usr/bin/env python3
"""Reference weight-transform hooks for poc/pubeval (dimension-collapse
comparator arms).

Hook contract (the dimcollapse comparability guarantee):

    fn(model, **kwargs) -> model | None      # None means "modified in place"

The harness applies the hook ONCE, after loading and BEFORE any scoring;
prompts, seeds, few-shot exemplars and scoring code are identical across
variants, so any metric delta is attributable to the weight change alone.
Before/after parameter counts + a weight fingerprint are recorded in the
results JSON (pubeval_runner.apply_transform).

Reference implementations here are the survey-standard pruning BASELINES the
dimcollapse experiment compares against:

  identity          no-op (baseline arm; also the mock-path plumbing check)
  magnitude_prune   zero the smallest-|w| fraction per 2D+ tensor (classic
                    magnitude pruning, Han et al. 2015 lineage)
  random_drop       zero a seeded random fraction per 2D+ tensor (the
                    random-dropped control)

The kernel-normalised-dropped transform itself lives with the dimcollapse
experiment (it needs the kernel/encoder machinery); it plugs in through the
same contract:  --transform path/to/dimcollapse_transforms.py:kernel_drop

torch is imported inside functions only: this module must import cleanly on
the torch-less coordinator box (mock path).
"""

from __future__ import annotations


def identity(model):
    """No-op baseline arm. Works on any object (incl. the mock StubLM)."""
    return model


def magnitude_prune(model, fraction=0.5, min_dim=2):
    """Zero the smallest-magnitude `fraction` of weights, per tensor.
    Tensors with dim < min_dim (biases, norms) are left untouched."""
    import torch
    fraction = float(fraction)
    if not 0.0 <= fraction < 1.0:
        raise SystemExit("ERR_TRANSFORM_ARG: fraction must be in [0,1), got %r"
                         % fraction)
    with torch.no_grad():
        for _name, p in model.named_parameters():
            if p.dim() < min_dim:
                continue
            k = int(p.numel() * fraction)
            if k <= 0:
                continue
            thresh = p.detach().abs().flatten().float().kthvalue(k).values
            p.mul_((p.detach().abs().float() > thresh).to(p.dtype))
    return model


def random_drop(model, fraction=0.5, seed=20260712, min_dim=2):
    """Zero a seeded uniform-random `fraction` of weights, per tensor
    (control arm: same sparsity as magnitude_prune, no selection signal).
    Mask is generated on CPU from `seed` so it is device-independent."""
    import torch
    fraction = float(fraction)
    if not 0.0 <= fraction < 1.0:
        raise SystemExit("ERR_TRANSFORM_ARG: fraction must be in [0,1), got %r"
                         % fraction)
    g = torch.Generator(device="cpu").manual_seed(int(seed))
    with torch.no_grad():
        for _name, p in model.named_parameters():
            if p.dim() < min_dim:
                continue
            mask = (torch.rand(p.shape, generator=g) >= fraction)
            p.mul_(mask.to(p.device).to(p.dtype))
    return model
