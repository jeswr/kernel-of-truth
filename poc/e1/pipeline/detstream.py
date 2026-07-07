"""Bit-exact python port of the encoder's deterministic primitives
(encoder/src/det.ts DetStream / detPermutation; domain `kot/enc/v1`).

Every draw is SHA-256 counter-mode over a fixed label, so python and
TypeScript produce IDENTICAL byte streams for identical labels — the E1
pipeline's seeded choices (story order, substitution draws) are therefore
reproducible from the committed labels alone, on any platform.
Ported for bead kernel-of-truth-bk0; verified against the TS side by
poc/e1/test/e1prep.test.ts (fixture `detstream-crosscheck` values).
"""

import hashlib

DET_DOMAIN = "kot/enc/v1"


class DetStream:
    """Deterministic byte stream: block i = SHA-256(f"{DOMAIN}/{label}/{i}")."""

    def __init__(self, label: str):
        self.label = label
        self.block = 0
        self.buf = b""
        self.pos = 0

    def _refill(self) -> None:
        msg = f"{DET_DOMAIN}/{self.label}/{self.block}".encode("utf-8")
        self.buf = hashlib.sha256(msg).digest()
        self.block += 1
        self.pos = 0

    def next_byte(self) -> int:
        if self.pos >= len(self.buf):
            self._refill()
        b = self.buf[self.pos]
        self.pos += 1
        return b

    def next_uint32(self) -> int:
        return (
            (self.next_byte() << 24)
            | (self.next_byte() << 16)
            | (self.next_byte() << 8)
            | self.next_byte()
        )

    def next_below(self, n: int) -> int:
        """Uniform integer in [0, n) by rejection sampling (unbiased)."""
        if n <= 0 or n > 0x100000000:
            raise ValueError(f"next_below({n})")
        limit = (0x100000000 // n) * n
        u = self.next_uint32()
        while u >= limit:
            u = self.next_uint32()
        return u % n

    def next_float(self) -> float:
        """Uniform float64 in [0, 1) with 53 bits of precision."""
        hi = self.next_uint32() >> 6  # 26 bits
        lo = self.next_uint32() >> 5  # 27 bits
        return (hi * 134217728 + lo) / 9007199254740992.0


def det_permutation(label: str, n: int) -> list:
    """Fisher-Yates permutation of [0, n) driven by DetStream(`perm/<label>`)."""
    stream = DetStream(f"perm/{label}")
    p = list(range(n))
    for i in range(n - 1, 0, -1):
        j = stream.next_below(i + 1)
        p[i], p[j] = p[j], p[i]
    return p
