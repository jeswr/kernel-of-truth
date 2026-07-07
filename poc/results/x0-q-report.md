# X0-q — golden vectors / byte-determinism (toy-native variant kot-enc-Bq/1)

date: 2026-07-07T04:52:55.633Z
algorithm: kot-enc-Bq/1, D ∈ {512, 576}
encoder content-hash @ D=512: `3492799ed73b49a612bebca920421041edd31d7bd4098bcf55da52df127ab9ee`
encoder content-hash @ D=576: `6ad0b2bc01c06447aae8468f500e2a2178e9a40f0d95de048b0418afcaea77db`
golden vectors: 11@512, 11@576

**PASS** — all vectors byte-identical to the committed goldens.

Note: cross-PLATFORM determinism is asserted by re-running this harness on
other machines against the same committed fixture. D=576 exercises the
Bluestein chirp-z FFT path (Math.cos/Math.sin caveat, fft.ts), which is
exactly what these goldens witness operationally.