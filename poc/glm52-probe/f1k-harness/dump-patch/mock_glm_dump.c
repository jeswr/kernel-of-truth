/* ============================================================================
 * mock_glm_dump.c — TINY MOCK ENGINE for the kot-f1k-dump/1 mock validation.
 * MOCK ONLY — never part of a real run; no model, no weights, no instance.
 *
 * Purpose: prove the dump patch's load-bearing properties at $0 by linking
 * the SAME kae_dump.h (and, through it, the SAME kae.h span binding) that
 * the patched glm.c links, wired into a toy forward pass whose hidden
 * states are an EXACT, independently re-derivable function of the token
 * prefix:
 *
 *   pfx    = FNV-1a over token ids t_0..t_p (4 LE bytes each)  — CAUSAL:
 *            a hidden state depends on the full prefix, so a capture at the
 *            wrong position/layer cannot alias the right one.
 *   hid(pfx, layer, pos, d) -> a value on the k/256 grid in [-128, 128):
 *            EXACT in f32 and f64, so the Python re-derivation in
 *            validate.py must match the dumped sums CELL-FOR-CELL, bit-equal
 *            (any gating/indexing/accumulation defect shows as a mismatch,
 *            never as tolerable noise).
 *
 * Build modes (validate.py builds both from this one source):
 *   gcc                       -> the "pre-dump" reference engine (KaE-only
 *                                stand-in): NO dump code compiled in.
 *   gcc -DKOT_DUMP_PATCH      -> the dump-patched engine: the moe() hook,
 *                                arming, echo and manifest loop are wired
 *                                EXACTLY as in the kot-f1k-dump.patch glm.c
 *                                (same env contract, same fail-closed
 *                                aborts, same call shapes).
 *
 * Geometry: NLAYERS=12, layers 0,1 DENSE (never call moe — mirrors GLM's
 * dense-first layout), layers 2..11 sparse. D from MOCK_D (default 16).
 * CHUNK=<n> splits each layer's moe() calls into n-position chunks with
 * increasing pos_base — validating absolute-position gating (pos_base+s).
 *
 * Usage: mock_glm_dump <manifest> <fwd_out>
 *   manifest: kot-f1k-dump/1 lines  "T t_0..t_{T-1} s_0..s_{T-1}"
 *   fwd_out:  raw f32 final activations, all lines concatenated — the
 *             byte-identity witness (ref vs dump-unset vs dump-armed).
 * Dump mode env: KAE_DUMP/KAE_DUMP_OUT/KAE_DUMP_LAYERS/KAE_SEED as in the
 * real engine; KAE / KAE_SCORE trigger the same phase-separation abort.
 * ==========================================================================*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#ifdef KOT_DUMP_PATCH
#include "kae_dump.h"                 /* the SAME header the patched glm.c links */
static KaEDump *g_kdump = NULL;       /* mirrors the glm.c file-scope global */
#endif

enum { NLAYERS = 12, VOCAB = 100000, MAXT = 4096 };
static int D = 16;                    /* MOCK_D override */

static int layer_is_sparse(int layer){ return layer >= 2; }   /* 0,1 dense */

static uint32_t fnv1a_ids(const int *ids, int n){
    uint32_t h = 2166136261u;
    for(int i = 0; i < n; i++){
        uint32_t t = (uint32_t)ids[i];
        for(int b = 0; b < 4; b++){ h ^= (t >> (8*b)) & 0xffu; h *= 16777619u; }
    }
    return h;
}

/* exact-grid hidden state: (v & 0xffff - 32768)/256 in [-128, 128) */
static float hid(uint32_t pfx, int layer, int pos, int d){
    uint32_t v = pfx ^ (2654435761u * (uint32_t)(layer + 1))
                     ^ (40503u      * (uint32_t)(pos + 1))
                     ^ (2246822519u * (uint32_t)(d + 1));
    v ^= v >> 13; v *= 2654435761u; v ^= v >> 16;
    return (float)((int)(v & 0xffffu) - 32768) / 256.0f;
}

/* the mock moe(): contains the EXACT hook line the patch adds to glm.c's
 * moe() head, then a trivial deterministic transform x -> out. */
static void mock_moe(int layer, float *x, int S, int pos_base, float *out){
#ifdef KOT_DUMP_PATCH
    /* kot-f1k-dump/1: READ-ONLY capture of the moe() INPUT x (S x D) —
     * the same one-line hook as the patched glm.c moe() head. */
    if(g_kdump) kaed_capture(g_kdump, layer, pos_base, S, D, x);
#endif
    for(int s = 0; s < S; s++) for(int d = 0; d < D; d++)
        out[(size_t)s*D + d] = x[(size_t)s*D + d] * 0.5f + (float)layer;
    (void)pos_base;
}

/* one toy prefill: per layer, hidden = hid(prefix,...); sparse layers go
 * through mock_moe (optionally chunked); fwd accumulates the outputs. */
static void forward(const int *ids, int T, float *fwd, int chunk){
    float *nrm = malloc((size_t)T * D * sizeof(float));
    float *out = malloc((size_t)T * D * sizeof(float));
    if(!nrm || !out){ fprintf(stderr, "mock: alloc failed\n"); exit(1); }
    for(int i = 0; i < T * D; i++) fwd[i] = 0.f;
    for(int layer = 0; layer < NLAYERS; layer++){
        for(int p = 0; p < T; p++){
            uint32_t pfx = fnv1a_ids(ids, p + 1);      /* causal prefix */
            for(int d = 0; d < D; d++) nrm[(size_t)p*D + d] = hid(pfx, layer, p, d);
        }
        if(layer_is_sparse(layer)){
            int step = (chunk > 0) ? chunk : T;
            for(int base = 0; base < T; base += step){
                int S = (base + step <= T) ? step : (T - base);
                mock_moe(layer, nrm + (size_t)base*D, S, base, out + (size_t)base*D);
            }
        } else {
            for(int i = 0; i < T * D; i++) out[i] = nrm[i] * 0.25f - (float)layer;
        }
        for(int i = 0; i < T * D; i++) fwd[i] += out[i];
    }
    free(nrm); free(out);
}

int main(int argc, char **argv){
    if(argc != 3){ fprintf(stderr, "usage: %s <manifest> <fwd_out>\n", argv[0]); return 1; }
    if(getenv("MOCK_D")) D = atoi(getenv("MOCK_D"));
    if(D < 1 || D > 8192){ fprintf(stderr, "mock: bad MOCK_D\n"); return 1; }
    int chunk = getenv("CHUNK") ? atoi(getenv("CHUNK")) : 0;
    int g_kae = getenv("KAE") ? atoi(getenv("KAE")) : 0;

#ifdef KOT_DUMP_PATCH
    /* phase separation, EXACTLY as the patched glm.c main() (ASM-2487) */
    if(getenv("KAE_DUMP") && (getenv("KAE_SCORE") || g_kae)){
        fprintf(stderr, "[KAE-DUMP] KAE_DUMP is construction-only and mutually exclusive "
                        "with KAE_SCORE / KAE=1 (phase separation) -> abort\n");
        return 1;
    }
#else
    (void)g_kae;
#endif

    /* startup banners exactly like the scoring engine (results never on
     * stdout — codex blocker-1 discipline) */
    printf("== GLM C engine (glm_moe_dsa), cache=64 experts/layer | "
           "experts@4-bit dense@8-bit | idot: mock ==\n");
    printf("loaded in 0.01s | resident dense: 0.00 MB | layers=%d experts=64 "
           "| MTP absent (draft=0)\n", NLAYERS);
    fflush(stdout);

#ifdef KOT_DUMP_PATCH
    if(getenv("KAE_DUMP")){
        g_kdump = kaed_arm(getenv("KAE_DUMP_LAYERS"), getenv("KAE_DUMP_OUT"),
                           D, NLAYERS);
        if(!g_kdump){ fprintf(stderr, "[KAE-DUMP] arm failed -> abort (fail closed; no partial dump)\n"); return 1; }
        fprintf(stderr, "[KAE-DUMP] armed: %d layers, D=%d, seed=%s (provenance echo; "
                        "dump path consults no RNG)\n",
                g_kdump->nl, g_kdump->D, getenv("KAE_SEED") ? getenv("KAE_SEED") : "-");
    }
    int dump_mode = getenv("KAE_DUMP") != NULL;
#else
    int dump_mode = 0;
#endif

    FILE *f = fopen(argv[1], "rb"); if(!f){ perror(argv[1]); return 1; }
    FILE *fo = fopen(argv[2], "wb"); if(!fo){ perror(argv[2]); return 1; }

    /* pass 1: n_lines + maxT (mirrors run_kae_dump) */
    int maxT = 1, n_lines = 0; { char *ln = NULL; size_t cp = 0;
        while(getline(&ln, &cp, f) > 0){ long t; char *e; t = strtol(ln, &e, 10);
            if(e == ln){ fprintf(stderr, "[KAE-DUMP] manifest line %d: no leading integer (garbage/blank line) -> abort\n", n_lines); return 1; }
            n_lines++; if(t > maxT) maxT = (int)t; }
        free(ln); }
    if(dump_mode && n_lines < 1){ fprintf(stderr, "[KAE-DUMP] empty manifest %s -> abort\n", argv[1]); return 1; }
    if(maxT > MAXT){ fprintf(stderr, "mock: T too large\n"); return 1; }

#ifdef KOT_DUMP_PATCH
    if(dump_mode && kaed_write_header(g_kdump, n_lines)) return 1;
#endif

    float *fwd = malloc((size_t)maxT * D * sizeof(float));
    int *ids = malloc((size_t)maxT * sizeof(int)), *spans = malloc((size_t)maxT * sizeof(int));
    if(!fwd || !ids || !spans){ fprintf(stderr, "mock: alloc failed\n"); return 1; }

    rewind(f); char *ln = NULL; size_t cp = 0; int nreq = 0;
    while(getline(&ln, &cp, f) > 0){
        char *p = ln, *e;
        long T = strtol(p, &e, 10);
        if(e == p){ fprintf(stderr, "[KAE-DUMP] line %d: no leading integer (garbage/blank line) -> abort\n", nreq); return 1; }
        p = e;
        if(T < 1 || T > maxT){ fprintf(stderr, "[KAE-DUMP] line %d: bad T=%ld -> abort\n", nreq, T); return 1; }
        for(long i = 0; i < T; i++){ long v = strtol(p, &e, 10);
            if(e == p || v < 0 || v >= VOCAB){ fprintf(stderr, "[KAE-DUMP] line %d: bad token id -> abort\n", nreq); return 1; }
            p = e; ids[i] = (int)v; }
        long gated = 0;
        for(long i = 0; i < T; i++){ long v = strtol(p, &e, 10);
            if(e == p || v < -1){ fprintf(stderr, "[KAE-DUMP] line %d: bad span slot -> abort\n", nreq); return 1; }
            p = e; spans[i] = (v < 0) ? -1 : (int)v; if(spans[i] >= 0) gated++; }
        /* the line must be EXACTLY the 2T+1 integers: only whitespace may
         * follow the last span; anything else is trailing junk (ASM-2489) */
        while(*p == ' ' || *p == '\t' || *p == '\r' || *p == '\n') p++;
        if(*p){ fprintf(stderr, "[KAE-DUMP] line %d: trailing junk after the required 2T+1 integers -> abort\n", nreq); return 1; }
#ifdef KOT_DUMP_PATCH
        if(dump_mode){
            if(!gated){ fprintf(stderr, "[KAE-DUMP] line %d has zero gated positions -> abort\n", nreq); return 1; }
            if(kaed_bind_line(g_kdump, spans, (int)T)){ fprintf(stderr, "[KAE-DUMP] line %d: span bind failed -> abort\n", nreq); return 1; }
        }
#else
        (void)gated;
#endif
        forward(ids, (int)T, fwd, chunk);
        if(fwrite(fwd, sizeof(float), (size_t)T * D, fo) != (size_t)T * D){
            fprintf(stderr, "mock: fwd write failed\n"); return 1; }
#ifdef KOT_DUMP_PATCH
        if(dump_mode){
            if(kaed_write_line(g_kdump, nreq, gated)) return 1;
            kaed_reset_line(g_kdump);
        }
#endif
        nreq++;
    }
#ifdef KOT_DUMP_PATCH
    if(dump_mode){
        if(nreq != n_lines){ fprintf(stderr, "[KAE-DUMP] processed %d lines != header %d -> abort\n", nreq, n_lines); return 1; }
        if(kaed_finish(g_kdump)) return 1;
        fprintf(stderr, "[kae-dump done: %d lines, %d layers, D=%d | 0.0s]\n",
                nreq, g_kdump->nl, g_kdump->D);
        kaed_free(g_kdump); g_kdump = NULL;
    }
#endif
    free(ln); free(ids); free(spans); free(fwd); fclose(f);
    if(fclose(fo) != 0){ fprintf(stderr, "mock: fwd close failed\n"); return 1; }
    return 0;
}
