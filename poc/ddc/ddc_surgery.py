#!/usr/bin/env python3
"""DDC weights-touching module — SliceGPT-style rotate-and-slice surgery
plus the two magnitude controls (docs/next/design/DDC.md §2.5, ASM-1653;
§4 matched compression, ASM-1657).

LAW-1 ISOLATION (DDC.md §1.2; enforced, not narrated). This is the ONLY
module in poc/ddc that touches model weights, and it is mechanically
kernel-blind:

  * it imports NOTHING from the kernel estate (no encoder tree, no
    codebook, no kernel data, no selection module) — validate_mock.py
    asserts this statically over the module source;
  * every basis enters through `BasisSpec` and `assert_basis_provenance`
    below: only bases whose provenance names the MODEL's own activation
    space (or seeded Haar randomness) are accepted; anything else —
    including anything carrying a `taint` marker, which the selection
    estate stamps on any array derived from kernel codebook vectors —
    raises ERR_DDC_LAW1_TAINT and no weight is touched.

  Kernel vectors therefore participate only OUTSIDE the model, in
  SELECTING which of the model's own activation directions are kept (the
  selection module and the G0 runner); no kernel vector can reach a
  weight matrix through this seam.

Surgery scheme (ASM-1653, every step cited):
  1. fuse RMSNorm per-channel gains into adjacent matrices, leaving
     parameter-free (unit-gain) RMSNorm — precondition for rotation
     commutation RMSNorm(XQ) = RMSNorm(X)Q [SURG §2.1, arXiv:2404.00456];
  2. per-block Q_l with an explicit residual bridge matrix Q_{l+1}^T Q_l
     in the attention skip connection (the MLP skip's bridge is identity
     because both MLP read and write sit in the block's OUTPUT basis —
     one basis per residual boundary, the §2.2 boundary convention;
     disclosed) [SliceGPT, arXiv:2401.15024 §3.3];
  3. slice to r = ceil(rho * d) columns;
  4. tied embedding sliced ONCE in the boundary-0 basis; ONE r x r bridge
     Q_0^T diag(g_final) Q_{L-1} (final-RMSNorm gain folded into it) is
     inserted before the unembedding read, so tying is preserved and the
     r = d construction is exactly logit-preserving — verified by gate
     I-1 (`i1_check`), never argued.
  Untouched: attention head dims, RoPE, KV cache, tokenizer, MLP inner
  dims [SURG §2.1].

Boundary convention (harness-level mechanical pin, also in
inputs/ddc-manifest.json): L residual boundaries per donor — l = 0 is the
embedding output, l = 1..L-1 are the post-residual outputs of blocks
0..L-2; the segment after the final block shares the basis of boundary
L-1. This makes the surgery grid coincide 1:1 with the ddc0 statistics
boundaries (layers 0..29 on the 135M donor).

fp32 everywhere (ASM-1653). torch is imported lazily; the module parses
and its provenance guard runs with NO torch installed (the $0 mock path).

Fail-closed codes: ERR_DDC_LAW1_TAINT, ERR_DDC_BASIS_SHAPE,
ERR_DDC_BASIS_NOT_ORTHONORMAL, ERR_DDC_ARCH (unexpected architecture),
ERR_DDC_I1 (rotation-validity check failure is reported, the caller
decides per §8 kill (a)).
"""

from __future__ import annotations

import math

# The ONLY provenances a basis may carry to touch weights (LAW-1 seam).
BASIS_PROVENANCE_ALLOWED = (
    "model-activation-basis",   # uncentred activation PCA / admitted model-
                                # space directions + complement top-up
    "haar-random-basis",        # R1: QR of seeded Gaussian
)

ORTHONORMALITY_TOL = 1e-6      # gate I-1 precondition (ASM-1661)


class Law1Error(SystemExit):
    pass


def assert_basis_provenance(spec):
    """LAW-1 mechanical gate. `spec` is a BasisSpec dict:
      {"provenance": str, "bases": [per-boundary matrices (d x r)],
       "meta": {...}}   (+ optional "taint": truthy = REFUSED)
    Raises ERR_DDC_LAW1_TAINT unless provenance is explicitly allowed and
    no taint marker is present. Pure-python; runs without torch/numpy."""
    if not isinstance(spec, dict):
        raise Law1Error("ERR_DDC_LAW1_TAINT: basis spec must be a dict, "
                        "got %r" % type(spec).__name__)
    prov = spec.get("provenance")
    if prov not in BASIS_PROVENANCE_ALLOWED:
        raise Law1Error(
            "ERR_DDC_LAW1_TAINT: basis provenance %r is not an allowed "
            "model-side provenance %r — kernel vectors select directions, "
            "they NEVER enter the weights (DDC.md section 1.2 LAW-1)"
            % (prov, BASIS_PROVENANCE_ALLOWED))
    if spec.get("taint"):
        raise Law1Error(
            "ERR_DDC_LAW1_TAINT: basis spec carries a taint marker %r — "
            "an array derived from kernel codebook vectors reached the "
            "surgery seam; refusing to touch any weight" % (spec["taint"],))
    meta = spec.get("meta")
    if not isinstance(meta, dict):
        raise Law1Error("ERR_DDC_LAW1_TAINT: basis spec has no meta block "
                        "(provenance is undocumented)")
    return True


# --------------------------------------------------------------------------
# torch-side helpers (lazy import; nothing below runs on the mock path)
# --------------------------------------------------------------------------

def _torch():
    import torch
    return torch


def _blocks(model):
    """The Llama-family decoder blocks; fail closed on anything else."""
    m = getattr(model, "model", None)
    layers = getattr(m, "layers", None)
    if layers is None or not hasattr(m, "embed_tokens") \
            or not hasattr(m, "norm"):
        raise SystemExit("ERR_DDC_ARCH: expected a Llama-family "
                         "AutoModelForCausalLM (model.model.{embed_tokens,"
                         "layers,norm}); got %r" % type(model).__name__)
    return m, list(layers)


def check_orthonormal(mat, tol=ORTHONORMALITY_TOL):
    """max |Q^T Q - I| <= tol (gate I-1 precondition). mat: torch (d x r)."""
    torch = _torch()
    q = mat.to(torch.float64)
    gram = q.T @ q
    eye = torch.eye(gram.shape[0], dtype=torch.float64)
    return float((gram - eye).abs().max())


def _validate_bases(spec, d, n_boundaries):
    torch = _torch()
    assert_basis_provenance(spec)
    bases = spec["bases"]
    if len(bases) != n_boundaries:
        raise SystemExit("ERR_DDC_BASIS_SHAPE: %d bases for %d boundaries"
                         % (len(bases), n_boundaries))
    out = []
    for i, b in enumerate(bases):
        q = torch.as_tensor(b, dtype=torch.float32)
        if q.dim() != 2 or q.shape[0] != d:
            raise SystemExit("ERR_DDC_BASIS_SHAPE: boundary %d basis shape "
                             "%r != (d=%d, r)" % (i, tuple(q.shape), d))
        err = check_orthonormal(q)
        if err > ORTHONORMALITY_TOL:
            raise SystemExit(
                "ERR_DDC_BASIS_NOT_ORTHONORMAL: boundary %d max|QtQ-I|="
                "%.3e > %g (gate I-1 precondition, ASM-1661)"
                % (i, err, ORTHONORMALITY_TOL))
        out.append(q)
    r = out[0].shape[1]
    if any(q.shape[1] != r for q in out):
        raise SystemExit("ERR_DDC_BASIS_SHAPE: v1 allocation is uniform "
                         "(ASM-1654); mixed r_l seen")
    return out, r


def fuse_rmsnorm_gains(model):
    """Step 1 (ASM-1653): fold every RMSNorm per-channel gain into the
    adjacent READING matrices; RMSNorm modules become unit-gain. The final
    norm's gain is RETURNED (folded into the unembedding bridge by
    rotate_and_slice, preserving embedding tying) [SURG §2.1,
    arXiv:2404.00456]."""
    torch = _torch()
    m, layers = _blocks(model)
    with torch.no_grad():
        for lyr in layers:
            g1 = lyr.input_layernorm.weight.data.clone()
            for name in ("q_proj", "k_proj", "v_proj"):
                w = getattr(lyr.self_attn, name).weight
                w.data = w.data * g1.unsqueeze(0)
            lyr.input_layernorm.weight.data.fill_(1.0)
            g2 = lyr.post_attention_layernorm.weight.data.clone()
            for name in ("up_proj", "gate_proj"):
                w = getattr(lyr.mlp, name).weight
                w.data = w.data * g2.unsqueeze(0)
            lyr.post_attention_layernorm.weight.data.fill_(1.0)
        g_final = m.norm.weight.data.clone()
        m.norm.weight.data.fill_(1.0)
    return g_final


def _make_bridged_block_class():
    """Define the wrapper lazily so the module imports without torch."""
    torch = _torch()

    class _BridgedBlock(torch.nn.Module):
        """Llama decoder block with an explicit residual bridge on the
        attention skip (SliceGPT scheme, arXiv:2401.15024 §3.3). Reads in
        the block's INPUT basis, writes in its OUTPUT basis; the MLP skip
        bridge is identity by the boundary convention (module docstring).
        Mirrors transformers.LlamaDecoderLayer.forward (v4.53) and fails
        closed on signature drift via gate I-1."""

        def __init__(self, layer, bridge):
            super().__init__()
            self.layer = layer
            # bridge: (r_out x r_in) = Q_out^T Q_in, or None (identity)
            if bridge is None:
                self.bridge = None
            else:
                self.register_buffer("bridge", bridge)

        def forward(self, hidden_states, **kwargs):
            lyr = self.layer
            residual = (hidden_states if self.bridge is None
                        else hidden_states @ self.bridge.T)
            x = lyr.input_layernorm(hidden_states)
            attn_out = lyr.self_attn(x, **kwargs)
            rest = ()
            if isinstance(attn_out, tuple):
                attn_out, rest = attn_out[0], tuple(attn_out[1:])
            h = residual + attn_out
            h = h + lyr.mlp(lyr.post_attention_layernorm(h))
            return (h,) + rest

    return _BridgedBlock


def _make_unembed_class():
    torch = _torch()

    class UnembedBridge(torch.nn.Module):
        """logits = (E Q_0) [Q_0^T diag(g_final) Q_{L-1}] h_rot — the ONE
        r x r bridge before the tied unembedding read (ASM-1653). The
        embedding weight tensor is SHARED with model.embed_tokens (tying
        preserved; bytes compress once)."""

        def __init__(self, embed_module, bridge):
            super().__init__()
            self.embed = embed_module          # shared sliced E (V x r)
            self.register_buffer("bridge", bridge)

        @property
        def weight(self):                       # HF save/tie compatibility
            return self.embed.weight

        def forward(self, h):
            return (h @ self.bridge.T) @ self.embed.weight.T

    return UnembedBridge


def rotate_and_slice(model, spec, rho):
    """Steps 2-4 (ASM-1653): per-block rotation folded permanently into
    the weights, residual bridges inserted, slice to r = ceil(rho*d).
    `spec` MUST pass assert_basis_provenance (LAW-1 seam). Returns an info
    dict {r, d, bridges, params_retained}."""
    torch = _torch()
    m, layers = _blocks(model)
    d = m.embed_tokens.weight.shape[1]
    L = len(layers)
    qs, r_full = _validate_bases(spec, d, L)  # boundaries 0..L-1
    r = int(math.ceil(rho * d))
    if r > r_full:
        raise SystemExit("ERR_DDC_BASIS_SHAPE: need r=%d columns, bases "
                         "carry %d" % (r, r_full))
    qs = [q[:, :r].contiguous() for q in qs]
    g_final = fuse_rmsnorm_gains(model)
    Block = _make_bridged_block_class()
    Unembed = _make_unembed_class()

    def q_in(s):                     # input basis of block s
        return qs[min(s, L - 1)]

    def q_out(s):                    # output basis of block s
        return qs[min(s + 1, L - 1)]

    with torch.no_grad():
        # tied embedding sliced ONCE in the boundary-0 basis
        m.embed_tokens.weight.data = (m.embed_tokens.weight.data.double()
                                      @ qs[0].double()).float()
        new_layers = []
        n_bridges = 0
        for s, lyr in enumerate(layers):
            qi, qo = q_in(s).double(), q_out(s).double()
            for name in ("q_proj", "k_proj", "v_proj"):
                w = getattr(lyr.self_attn, name).weight
                w.data = (w.data.double() @ qi).float()
                getattr(lyr.self_attn, name).in_features = r
            wo = lyr.self_attn.o_proj.weight
            wo.data = (qo.T @ wo.data.double()).float()
            lyr.self_attn.o_proj.out_features = r
            for name in ("up_proj", "gate_proj"):
                w = getattr(lyr.mlp, name).weight
                w.data = (w.data.double() @ qo).float()
                getattr(lyr.mlp, name).in_features = r
            wd = lyr.mlp.down_proj.weight
            wd.data = (qo.T @ wd.data.double()).float()
            lyr.mlp.down_proj.out_features = r
            for ln in (lyr.input_layernorm, lyr.post_attention_layernorm):
                ln.weight.data = torch.ones(r)
            if torch.equal(qi, qo):
                bridge = None                    # identity (shared basis)
            else:
                bridge = (qo.T @ qi).float()
                n_bridges += 1
            new_layers.append(Block(lyr, bridge))
        m.layers = torch.nn.ModuleList(new_layers)
        m.norm.weight.data = torch.ones(r)
        # unembedding: ONE r x r bridge Q_0^T diag(g_final) Q_{L-1}
        ub = (qs[0].double().T @ torch.diag(g_final.double())
              @ qs[L - 1].double()).float()
        model.lm_head = Unembed(m.embed_tokens, ub)
        n_bridges += 1
        if hasattr(model.config, "hidden_size"):
            model.config.hidden_size = r
    return {"r": r, "d": d, "bridges": n_bridges,
            "params_retained": count_params(model)}


def magnitude_structured(model, target_params):
    """M1 (ASM-1657): keep the r' coordinate dimensions with the largest
    summed squared weight mass across ALL residual-coupled matrices; no
    rotation, no bridges; r' = smallest count whose retained parameters
    >= target_params (conservative in M1's favour). Data-free."""
    torch = _torch()
    m, layers = _blocks(model)
    d = m.embed_tokens.weight.shape[1]
    with torch.no_grad():
        mass = torch.zeros(d, dtype=torch.float64)
        mass += (m.embed_tokens.weight.data.double() ** 2).sum(0)
        for lyr in layers:
            for mod, axis in ((lyr.self_attn.q_proj, 1),
                              (lyr.self_attn.k_proj, 1),
                              (lyr.self_attn.v_proj, 1),
                              (lyr.self_attn.o_proj, 0),
                              (lyr.mlp.up_proj, 1),
                              (lyr.mlp.gate_proj, 1),
                              (lyr.mlp.down_proj, 0)):
                w = mod.weight.data.double() ** 2
                mass += w.sum(0) if axis == 1 else w.sum(1)
        order = torch.argsort(mass, descending=True)

        def params_at(rp):
            idx = order[:rp]
            n = m.embed_tokens.weight.shape[0] * rp
            for lyr in layers:
                n += (lyr.self_attn.q_proj.weight.shape[0] * rp) * 3
                n += rp * lyr.self_attn.o_proj.weight.shape[1]
                n += (lyr.mlp.up_proj.weight.shape[0] * rp) * 2
                n += rp * lyr.mlp.down_proj.weight.shape[1]
                n += rp * 2                      # the two RMSNorm gains
            n += rp                              # final norm gain
            del idx
            return n

        rp = 1
        lo, hi = 1, d
        while lo < hi:                            # smallest r' meeting target
            mid = (lo + hi) // 2
            if params_at(mid) >= target_params:
                hi = mid
            else:
                lo = mid + 1
        rp = lo
        keep = torch.sort(order[:rp]).values
        m.embed_tokens.weight.data = \
            m.embed_tokens.weight.data[:, keep].contiguous()
        for lyr in layers:
            for name in ("q_proj", "k_proj", "v_proj"):
                mod = getattr(lyr.self_attn, name)
                mod.weight.data = mod.weight.data[:, keep].contiguous()
                mod.in_features = rp
            lyr.self_attn.o_proj.weight.data = \
                lyr.self_attn.o_proj.weight.data[keep, :].contiguous()
            lyr.self_attn.o_proj.out_features = rp
            for name in ("up_proj", "gate_proj"):
                mod = getattr(lyr.mlp, name)
                mod.weight.data = mod.weight.data[:, keep].contiguous()
                mod.in_features = rp
            lyr.mlp.down_proj.weight.data = \
                lyr.mlp.down_proj.weight.data[keep, :].contiguous()
            lyr.mlp.down_proj.out_features = rp
            lyr.input_layernorm.weight.data = \
                lyr.input_layernorm.weight.data[keep].contiguous()
            lyr.post_attention_layernorm.weight.data = \
                lyr.post_attention_layernorm.weight.data[keep].contiguous()
        m.norm.weight.data = m.norm.weight.data[keep].contiguous()
        if hasattr(model.config, "hidden_size"):
            model.config.hidden_size = rp
    return {"r_prime": rp, "d": d, "bridges": 0,
            "params_retained": count_params(model)}


def magnitude_unstructured(model, target_params):
    """M2 (ASM-1657): global weight-magnitude mask to the identical
    retained-parameter count (dense storage; the sparse-CSR byte figure is
    reported separately). Data-free."""
    torch = _torch()
    with torch.no_grad():
        tensors = [p for _n, p in sorted(model.named_parameters())]
        total = sum(p.numel() for p in tensors)
        n_zero = max(0, total - int(target_params))
        if n_zero:
            flat = torch.cat([p.data.abs().flatten() for p in tensors])
            thresh = torch.kthvalue(flat, n_zero).values
            zeroed = 0
            for p in tensors:
                mask = p.data.abs() <= thresh
                zeroed += int(mask.sum())
                p.data[mask] = 0.0
        else:
            zeroed = 0
    return {"d": None, "bridges": 0, "masked_to_zero": zeroed,
            "params_retained": total - zeroed,
            "dense_param_count": total}


def count_params(model):
    return sum(p.numel() for _n, p in model.named_parameters()) + sum(
        b.numel() for _n, b in model.named_buffers()
        if _n.endswith("bridge"))


def packed_bytes_fp32(model):
    """Measured artifact-size figure (Appendix B discipline: width != bytes):
    fp32 packed bytes of every parameter + bridge buffer."""
    return 4 * count_params(model)


def i1_check(donor, rotated, token_batches, kl_median_max=1e-5):
    """Gate I-1 (ASM-1661): end-to-end logit equivalence of the
    rotation-only (r = d) model over the pinned probe corpus — median
    KL(donor||rotated) <= 1e-5 AND greedy top-1 agreement == 100%.
    token_batches: list of 1 x T LongTensors. Returns the gate dict; the
    CALLER records failure (kill (a) needs one debugging iteration)."""
    torch = _torch()
    kls = []
    agree = 0
    total = 0
    with torch.no_grad():
        for ids in token_batches:
            ld = donor(ids).logits[0].float()
            lr = rotated(ids).logits[0].float()
            pd = torch.log_softmax(ld, dim=-1)
            pr = torch.log_softmax(lr, dim=-1)
            kl = (pd.exp() * (pd - pr)).sum(-1)
            kls.extend(kl.tolist())
            agree += int((ld.argmax(-1) == lr.argmax(-1)).sum())
            total += ld.shape[0]
    kls.sort()
    med = kls[len(kls) // 2] if len(kls) % 2 else \
        0.5 * (kls[len(kls) // 2 - 1] + kls[len(kls) // 2])
    ok = med <= kl_median_max and agree == total
    return {"median_kl": med, "top1_agreement": agree / max(total, 1),
            "n_positions": total, "pass": bool(ok)}
