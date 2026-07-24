#ifndef KAE_DUMP_H
#define KAE_DUMP_H
/* ============================================================================
 * kot-f1k-dump/1 — construction-only moe()-INPUT hidden-state dump (F1-K).
 * DRAFT FOR GATE-0 REVIEW, NOT DEPLOYED.
 *
 * Implements the ENGINE HIDDEN-STATE DUMP CONTRACT frozen in
 * build_carriers.py (kernel-of-truth poc/glm52-probe/f1k-harness, generator
 * pin cda62364; DES glm52-followup-experiment.md §2.4 / §2.8 item-3):
 * for each construction pass (one manifest line), SUM the hidden state x at
 * the moe() INPUT over the GATED positions (span slot >= 0), per requested
 * dump layer, and emit the KAED binary. The mean-difference arithmetic that
 * turns these sums into carriers is HARNESS-SIDE (build_carriers.py,
 * "REGISTERED MEAN-DIFFERENCE ARITHMETIC") — this file only records sums.
 *
 * PHASE SEPARATION (scoring binary stays gate-0-KaE-patch-only):
 *   - This mode is ADDITIVE and CONSTRUCTION-ONLY. With KAE_DUMP unset the
 *     engine forward is byte-identical to the gate-0 KaE-patched engine:
 *     the only added executed code is NULL getenv checks in main() and one
 *     `if(g_kdump)` false branch at the head of moe().
 *   - KAE_DUMP is mutually exclusive with KAE_SCORE and with KAE=1 (enforced
 *     fail-closed in main() BEFORE model load, ASM-2487): a dump of the
 *     spliced model would silently corrupt every carrier.
 *   - The capture is READ-ONLY (const float *x): arming the dump cannot
 *     perturb the forward pass it observes.
 *
 * SPAN BINDING IS REUSED from kae.h (kae_bind_spans / kae_concept_at /
 * kae_reset_spans on an embedded KaE struct used ONLY for its span fields):
 * the dump gates positions with the exact same per-item, absolute-position
 * (pos_base + s) semantics the gate-0-reviewed KAE_SCORE path uses.
 *
 * ARITHMETIC (ASM-2485): the summands are the engine's own f32 hidden-state
 * components, untouched; accumulation is IEEE-754 float64 in ascending
 * absolute-position order; sums are cast to f32 only at write. This matches
 * mock_colibri_dump.py (Python float == C double; struct '<f' == (float)
 * cast) cell-for-cell, so the mock and the real engine share one contract.
 *
 * FAIL-CLOSED invariants (any violation => nonzero process exit, no dump):
 *   - arm: KAE_DUMP_OUT + KAE_DUMP_LAYERS required; every layer id in
 *     [0, n_layers), no duplicates; output file must open.
 *   - per line: zero gated positions is an ERROR (contract: the generator
 *     never emits one); ANY malformed line (garbage line, bad T/token/span,
 *     an integer that overflows long (ERANGE) or is not exactly
 *     representable as int, trailing junk after the required 2T+1 ints)
 *     ABORTS (construction integrity over availability, ASM-2489 — unlike
 *     KAE_SCORE's per-item skip, a silently dropped construction pass would
 *     corrupt §2.4 means). r3 (gate-0 re-review finding 3): manifest
 *     integers are parsed ONLY via kaed_parse_int below — the r2 long->int
 *     cast let a span like 2147483648 wrap negative and become a silently
 *     UNGATED position with exit 0.
 *   - per line, per slot: the number of gated rows actually accumulated
 *     must equal the manifest's gated count (ASM-2488). This catches a
 *     requested layer that never reaches moe() (dense layer, layer never
 *     executed), a chunked prefill visiting a position twice, and a
 *     hidden-dim mismatch — each of which would otherwise corrupt sums
 *     silently.
 *   - per line, per cell (r3, gate-0 re-review finding 4): every f64
 *     accumulator must be FINITE, and its f32 cast must be FINITE, at
 *     write time — a NaN/Inf hidden state (or an f64 sum that overflows
 *     f32) previously reached the KAED bytes with exit 0 and would have
 *     surfaced only at carrier non-degeneracy, after more paid batches.
 *     The immediate consumer (build_carriers.py run_dump) re-checks both
 *     finiteness and gated_count independently.
 *
 * KAED format (little-endian, same x86-64 assumption as kae.h's KAEC,
 * ASM-2491):
 *   [4]="KAED" | i32 n_lines | i32 nl | i32 D | i32 layer_id[nl]
 *   then per line: i32 gated_count | f32 sum[nl*D]
 * layer_id order == KAE_DUMP_LAYERS order (slot order; harness verifies).
 * ==========================================================================*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <limits.h>
#include <errno.h>
#include <math.h>
#include "kae.h"

typedef struct KaEDump {
    int    nl;          /* number of dump layers (KAE_DUMP_LAYERS)            */
    int    D;           /* model hidden dim (validated at capture)            */
    int   *layer;       /* [nl] dump layer ids, KAE_DUMP_LAYERS order = slots */
    double*acc;         /* [nl*D] per-line f64 accumulators (ASM-2485)        */
    long  *cnt;         /* [nl] gated rows accumulated this line, per slot    */
    float *tmpf;        /* [nl*D] f32 staging buffer for the line write       */
    KaE    gate;        /* REUSED kae.h span binding; only span/span_n/nc used*/
    FILE  *out;         /* KAE_DUMP_OUT stream                                */
    int    err;         /* sticky capture error -> write_line fails closed    */
} KaEDump;

/* slot of `layer` in the dump set, in KAE_DUMP_LAYERS order; -1 if absent. */
static inline int kaed_slot_of_layer(const KaEDump *kd, int layer){
    for(int i = 0; i < kd->nl; i++) if(kd->layer[i] == layer) return i;
    return -1;
}

/* r3 (gate-0 re-review finding 3) — STRICT manifest integer parse.
 * Reads one whitespace-led base-10 integer at *pp and requires ALL of:
 * digits present (e != p), no strtol overflow (errno != ERANGE), and
 * lo <= v <= hi. Callers pass hi <= INT_MAX-1, so a 0-return guarantees
 * the (int) cast of *out is EXACT — the r2 code cast long->int unchecked,
 * so 2147483648 wrapped negative and kae_bind_spans normalised it to -1:
 * a malformed span became a silently UNGATED position on a line that then
 * SUCCEEDED (contradicting ASM-2489). 0 on success (*pp advanced, *out
 * set); -1 on ANY malformed/overflowing/out-of-range integer — the caller
 * MUST abort the line (nonzero process exit, never skip). */
static inline int kaed_parse_int(char **pp, long lo, long hi, long *out){
    char *e;
    errno = 0;
    long v = strtol(*pp, &e, 10);
    if(e == *pp || errno == ERANGE || v < lo || v > hi) return -1;
    *pp = e; *out = v;
    return 0;
}

/* Arm the dump: parse KAE_DUMP_LAYERS (csv), validate against the model
 * geometry, allocate accumulators, open KAE_DUMP_OUT. Returns NULL on ANY
 * failure (caller must treat NULL as fatal — fail closed, never a partial
 * dump; contrast kae_load, whose NULL degrades to "KaE disabled": a scoring
 * run without the splice is a valid arm, a construction run without the
 * dump is not). */
static inline KaEDump *kaed_arm(const char *layers_csv, const char *out_path,
                                int hidden, int n_layers){
    if(!layers_csv || !*layers_csv){
        fprintf(stderr, "[KAE-DUMP] KAE_DUMP requires KAE_DUMP_LAYERS=<csv>\n");
        return NULL; }
    if(!out_path || !*out_path){
        fprintf(stderr, "[KAE-DUMP] KAE_DUMP requires KAE_DUMP_OUT=<path>\n");
        return NULL; }
    KaEDump *kd = (KaEDump*)calloc(1, sizeof(KaEDump));
    if(!kd){ fprintf(stderr, "[KAE-DUMP] alloc failed\n"); return NULL; }
    kd->D = hidden;
    /* the embedded gate reuses kae_bind_spans verbatim; dump span slots are
     * template char-span slot ids (any non-negative int gates), so the only
     * binding-time constraint is v < nc: set nc to INT_MAX. layer/carrier
     * stay NULL — only the span fields of the reused KaE struct are used. */
    kd->gate.nc = INT_MAX;
    int cap = 16;
    kd->layer = (int*)malloc((size_t)cap * sizeof(int));
    if(!kd->layer){ fprintf(stderr, "[KAE-DUMP] alloc layer list failed\n"); free(kd); return NULL; }
    const char *p = layers_csv;
    while(*p){
        /* overflow-closed WITHOUT kaed_parse_int: ERANGE clamps to
         * LONG_MIN/LONG_MAX, and n_layers < INT_MAX, so the [0, n_layers)
         * range check below already rejects every overflowing value —
         * unlike the manifest span parse (finding 3), no wrapped value can
         * pass it. */
        char *e; long v = strtol(p, &e, 10);
        if(e == p || v < 0 || v >= n_layers){
            fprintf(stderr, "[KAE-DUMP] bad dump layer id in '%s' (want ints in [0,%d))\n",
                    layers_csv, n_layers);
            free(kd->layer); free(kd); return NULL; }
        for(int i = 0; i < kd->nl; i++) if(kd->layer[i] == (int)v){
            fprintf(stderr, "[KAE-DUMP] duplicate dump layer %ld\n", v);
            free(kd->layer); free(kd); return NULL; }
        if(kd->nl == cap){
            cap *= 2;
            int *nl2 = (int*)realloc(kd->layer, (size_t)cap * sizeof(int));
            if(!nl2){ fprintf(stderr, "[KAE-DUMP] realloc layer list failed\n");
                      free(kd->layer); free(kd); return NULL; }
            kd->layer = nl2; }
        kd->layer[kd->nl++] = (int)v;
        p = e;
        if(*p == ','){ p++; if(!*p){ fprintf(stderr, "[KAE-DUMP] trailing comma in KAE_DUMP_LAYERS\n");
                                     free(kd->layer); free(kd); return NULL; } }
        else if(*p){ fprintf(stderr, "[KAE-DUMP] malformed KAE_DUMP_LAYERS '%s'\n", layers_csv);
                     free(kd->layer); free(kd); return NULL; }
    }
    if(kd->nl < 1){ fprintf(stderr, "[KAE-DUMP] empty KAE_DUMP_LAYERS\n");
                    free(kd->layer); free(kd); return NULL; }
    size_t cells, bytes;
    if(!kae_szmul((size_t)kd->nl, (size_t)kd->D, &cells) ||
       !kae_szmul(cells, sizeof(double), &bytes)){
        fprintf(stderr, "[KAE-DUMP] accumulator size overflow (%d*%d)\n", kd->nl, kd->D);
        free(kd->layer); free(kd); return NULL; }
    kd->acc  = (double*)calloc(cells, sizeof(double));
    kd->tmpf = (float*) malloc(cells * sizeof(float));
    kd->cnt  = (long*)  calloc((size_t)kd->nl, sizeof(long));
    if(!kd->acc || !kd->tmpf || !kd->cnt){
        fprintf(stderr, "[KAE-DUMP] accumulator alloc failed\n");
        free(kd->acc); free(kd->tmpf); free(kd->cnt); free(kd->layer); free(kd); return NULL; }
    kd->out = fopen(out_path, "wb");
    if(!kd->out){ fprintf(stderr, "[KAE-DUMP] cannot open KAE_DUMP_OUT %s\n", out_path);
                  free(kd->acc); free(kd->tmpf); free(kd->cnt); free(kd->layer); free(kd); return NULL; }
    return kd;
}

/* Bind THIS line's spans (REUSES kae_bind_spans: per-item, replaces the
 * previous line's) and zero the line accumulators. -1 on bind failure. */
static inline int kaed_bind_line(KaEDump *kd, const int *spans, int n){
    if(kae_bind_spans(&kd->gate, spans, n) != 0) return -1;
    memset(kd->acc, 0, (size_t)kd->nl * (size_t)kd->D * sizeof(double));
    memset(kd->cnt, 0, (size_t)kd->nl * sizeof(long));
    kd->err = 0;
    return 0;
}

/* THE CAPTURE — called at the HEAD of moe() on its INPUT x [S*D] (glm.c:1277;
 * DES §2.4 "hidden states recorded at gated positions at the moe() input").
 * READ-ONLY on x. For each row s whose absolute position (pos_base+s) is
 * gated (reused kae_concept_at >= 0) at a dump layer, accumulate x row into
 * the slot's f64 accumulator (ascending position order: rows in s order,
 * chunks in pos_base order). Rows/layers outside the dump set do nothing. */
static inline void kaed_capture(KaEDump *kd, int layer, int pos_base,
                                int S, int D, const float *x){
    if(!kd || kd->err) return;
    int slot = kaed_slot_of_layer(kd, layer);
    if(slot < 0) return;
    if(D != kd->D){ kd->err = 1; /* surfaces at kaed_write_line, fail closed */
        fprintf(stderr, "[KAE-DUMP] capture D=%d != armed D=%d at layer %d\n",
                D, kd->D, layer);
        return; }
    double *a = kd->acc + (size_t)slot * (size_t)D;
    for(int s = 0; s < S; s++){
        if(kae_concept_at(&kd->gate, pos_base + s) < 0) continue;  /* reused gate */
        const float *xs = x + (size_t)s * (size_t)D;
        for(int d = 0; d < D; d++) a[d] += (double)xs[d];
        kd->cnt[slot]++;
    }
}

/* Write the KAED header. 0 on success. */
static inline int kaed_write_header(KaEDump *kd, int n_lines){
    int32_t hdr[3]; hdr[0] = n_lines; hdr[1] = kd->nl; hdr[2] = kd->D;
    if(fwrite("KAED", 1, 4, kd->out) != 4 ||
       fwrite(hdr, 4, 3, kd->out) != 3 ||
       fwrite(kd->layer, 4, (size_t)kd->nl, kd->out) != (size_t)kd->nl){
        fprintf(stderr, "[KAE-DUMP] header write failed\n"); return -1; }
    return 0;
}

/* Close out the line: enforce the ASM-2488 per-slot invariant (every dump
 * slot accumulated EXACTLY gated_expected rows) and the r3 finiteness
 * invariant (gate-0 re-review finding 4: every f64 accumulator AND its f32
 * cast must be finite — NaN/Inf previously reached the KAED bytes with
 * exit 0), then emit i32 gated_count | f32 sum[nl*D]. 0 on success;
 * nonzero must abort the run. */
static inline int kaed_write_line(KaEDump *kd, int line_no, long gated_expected){
    if(kd->err){
        fprintf(stderr, "[KAE-DUMP] line %d: capture error (see above) -> abort\n", line_no);
        return -1; }
    for(int i = 0; i < kd->nl; i++) if(kd->cnt[i] != gated_expected){
        fprintf(stderr, "[KAE-DUMP] line %d: layer %d accumulated %ld gated rows, "
                "manifest has %ld — dump layer not reached by moe() or position "
                "visited twice -> abort (ASM-2488)\n",
                line_no, kd->layer[i], kd->cnt[i], gated_expected);
        return -1; }
    size_t cells = (size_t)kd->nl * (size_t)kd->D;
    for(size_t z = 0; z < cells; z++){
        if(!isfinite(kd->acc[z])){
            fprintf(stderr, "[KAE-DUMP] line %d: NON-FINITE f64 sum at layer %d "
                    "dim %d -> abort (finding-4 fail-closed: a NaN/Inf dump "
                    "would corrupt every carrier downstream)\n",
                    line_no, kd->layer[z / (size_t)kd->D], (int)(z % (size_t)kd->D));
            return -1; }
        kd->tmpf[z] = (float)kd->acc[z];
        if(!isfinite(kd->tmpf[z])){
            fprintf(stderr, "[KAE-DUMP] line %d: f64 sum %g OVERFLOWS f32 at "
                    "layer %d dim %d -> abort (finding-4 fail-closed)\n",
                    line_no, kd->acc[z], kd->layer[z / (size_t)kd->D],
                    (int)(z % (size_t)kd->D));
            return -1; }
    }
    int32_t gc = (int32_t)gated_expected;
    if(fwrite(&gc, 4, 1, kd->out) != 1 ||
       fwrite(kd->tmpf, sizeof(float), cells, kd->out) != cells){
        fprintf(stderr, "[KAE-DUMP] line %d: write failed\n", line_no); return -1; }
    return 0;
}

/* Reset between lines: clear the reused spans so nothing gates until the
 * next bind (mirrors run_kae_score's kae_reset_spans discipline). */
static inline void kaed_reset_line(KaEDump *kd){
    kae_reset_spans(&kd->gate);
}

/* Flush + close; 0 iff every byte landed. */
static inline int kaed_finish(KaEDump *kd){
    if(fflush(kd->out) != 0 || ferror(kd->out) || fclose(kd->out) != 0){
        fprintf(stderr, "[KAE-DUMP] output flush/close failed\n");
        kd->out = NULL; return -1; }
    kd->out = NULL;
    return 0;
}

static inline void kaed_free(KaEDump *kd){
    if(!kd) return;
    if(kd->out) fclose(kd->out);
    kae_reset_spans(&kd->gate);
    free(kd->layer); free(kd->acc); free(kd->cnt); free(kd->tmpf); free(kd);
}

#endif /* KAE_DUMP_H */
