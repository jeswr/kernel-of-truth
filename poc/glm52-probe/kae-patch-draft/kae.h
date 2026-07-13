#ifndef KAE_H
#define KAE_H
/* ============================================================================
 * KaE — Kernel-as-Expert (F1-K), ADD-path.  DRAFT FOR GATE-0 REVIEW, NOT DEPLOYED.
 *
 * This is the reviewable artifact for MAINTAINER GATE 0 of
 *   docs/next/design/glm52-followup-experiment.md (F1-K, through REVISION-6):
 * it is the code that would write a grounded per-concept content-vector into
 * GLM-5.2's MoE-block activations — a Law-1-amendment-gated action.  It is
 * DRAFTED here for review; it is INERT unless the environment sets KAE=1, and
 * NOTHING in this header runs against a governed model in this pass.
 *
 * Scope of THIS header (the design's first rung, §1.1 / §2.3 / §2.5 ADD):
 *   - the lexical concept GATE (G-lex, computed harness-side): per-position
 *     concept ids are supplied to the engine as a frozen sidecar (KAE_SPANS);
 *     the engine only READS them — zero learned components, deterministic.
 *   - the per-concept per-layer CARRIER table K[c][l] (KAE_CARRIER).
 *   - the ADD splice: for a gated token at a splice layer, out += g * K[c][l],
 *     applied AFTER the routed top-8 sum + shared expert are accumulated and
 *     BEFORE the MoE block output is added back to the residual stream
 *     (native experts left fully intact — pure ADD, §2.5).
 *
 * OUT OF SCOPE here (documented stubs, deferred by the design):
 *   - REPLACE path (§2.5): admitted only after ADD passes K-1; kae_replace_note().
 *   - hidden-state DUMP mode (§2.4/§2.8) for carrier construction — harness-side.
 *   - G-emb cosine gate variant (§2.3) — budget-permitting, not this rung.
 *
 * The gate/splice functions take NO candidate/option/label argument: the
 * intervention is a pure function of the FROZEN sidecar (spans+carrier), the
 * layer, and the absolute token position.  That is the engine-level meaning of
 * REVISION-1 §R1.1's "candidate-independent scoring": the spliced activations
 * an item receives do not depend on which answer candidate is later scored off
 * the single shared prefill.  (See test_kae.c, Test D.)
 *
 * Deliberately self-contained (no Model/Cfg dependency) so the mechanics can be
 * unit-tested against the SAME source the engine links.  All symbols are
 * static-inline; both glm.c and test_kae.c include this header.
 *
 * File formats (host-endian; x86-64 little-endian assumed, documented in README):
 *   KAE_CARRIER : [4]="KAEC" magic | i32 nc | i32 nl | i32 D
 *                 | i32 layer_id[nl] (the splice set L_KaE, ascending)
 *                 | f32 K[nc*nl*D]   (row-major: concept, then slot, then dim)
 *   KAE_SPANS   : ASCII, whitespace-separated ints, one per absolute token
 *                 position (index = position); value = concept id, -1 = ungated.
 * ==========================================================================*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct KaE {
    int    nc;          /* number of concepts C                              */
    int    nl;          /* number of splice layers |L_KaE|                   */
    int    D;           /* carrier hidden dim (must equal model hidden)      */
    int   *layer;       /* [nl] splice layer ids (L_KaE), ascending          */
    float *carrier;     /* [nc*nl*D] K[c][slot][d], row-major                */
    int   *span;        /* [span_n] absolute-position -> concept id (-1 = off)*/
    int    span_n;      /* number of positions covered by the sidecar        */
    float  g;           /* blend weight (applied AFTER carrier norm), §2.3    */
    int    mode;        /* 0 = ADD (implemented); 1 = REPLACE (stub, §2.5)    */
} KaE;

/* GATE (G-lex readout): concept id at absolute position `pos`, or -1 (ungated /
 * out of the frozen sidecar's range). The whole gate is this table lookup —
 * the phrase->concept matching is done harness-side and frozen into the sidecar. */
static inline int kae_concept_at(const KaE *k, int pos){
    if(!k || pos < 0 || pos >= k->span_n) return -1;
    return k->span[pos];
}

/* Is `layer` a splice layer? Return its carrier slot in [0,nl), else -1. */
static inline int kae_slot_of_layer(const KaE *k, int layer){
    if(!k) return -1;
    for(int i = 0; i < k->nl; i++) if(k->layer[i] == layer) return i;
    return -1;
}

/* THE SPLICE (ADD path, §2.5).  out is the MoE-block output [S*D] with the
 * routed sum + shared expert already accumulated.  For each batch row s whose
 * absolute position (pos_base+s) is gated to concept c, at a splice layer,
 * add g*K[c][slot] to out[s].  Ungated rows and non-splice layers are left
 * bit-for-bit unchanged (that is the off-concept / inert invariant, §2.5).
 * No candidate/label parameter exists: the effect is candidate-independent. */
static inline void kae_apply_add(const KaE *k, int layer, int pos_base,
                                 int S, int D, float *out){
    if(!k || k->mode != 0) return;                 /* ADD path only          */
    int slot = kae_slot_of_layer(k, layer);
    if(slot < 0) return;                           /* not a splice layer     */
    if(D != k->D) return;                          /* dim guard (also at load)*/
    for(int s = 0; s < S; s++){
        int cid = kae_concept_at(k, pos_base + s);
        if(cid < 0 || cid >= k->nc) continue;      /* gate did not fire      */
        const float *Kcl = k->carrier + ((size_t)cid * k->nl + slot) * (size_t)D;
        float *os = out + (size_t)s * D;
        for(int d = 0; d < D; d++) os[d] += k->g * Kcl[d];
    }
}

/* REPLACE path (§2.5) — DOCUMENTED STUB, deferred by the design behind a K-1
 * pass and its own NI power gate (REVISION-4 §R-REV4.3). Intentionally a no-op
 * in this draft: REPLACE would skip the lowest-sigmoid-weight native expert on
 * gated tokens and add w_dropped*K in its place, which requires the moe() expert
 * loop to expose per-token dropped-weight bookkeeping. Not wired for gate 0. */
static inline void kae_replace_note(void){ /* intentionally empty (stub) */ }

static inline void kae_free(KaE *k){
    if(!k) return;
    free(k->layer); free(k->carrier); free(k->span); free(k);
}

/* Load the carrier table + span sidecar. Returns NULL (and prints why) on any
 * malformed input or a hidden-dim mismatch — callers treat NULL as "disabled".
 * hidden/n_layers are the model's, used only to validate the files. */
static inline KaE *kae_load(const char *carrier_path, const char *spans_path,
                            int hidden, int n_layers, float g, int mode){
    if(!carrier_path || !spans_path){
        fprintf(stderr, "[KAE] KAE=1 requires KAE_CARRIER=<file> and KAE_SPANS=<file>\n");
        return NULL;
    }
    FILE *cf = fopen(carrier_path, "rb");
    if(!cf){ fprintf(stderr, "[KAE] cannot open carrier %s\n", carrier_path); return NULL; }
    char magic[4]; int32_t nc = 0, nl = 0, D = 0;
    if(fread(magic, 1, 4, cf) != 4 || memcmp(magic, "KAEC", 4) != 0){
        fprintf(stderr, "[KAE] bad carrier magic (want KAEC)\n"); fclose(cf); return NULL; }
    if(fread(&nc, 4, 1, cf) != 1 || fread(&nl, 4, 1, cf) != 1 || fread(&D, 4, 1, cf) != 1){
        fprintf(stderr, "[KAE] short carrier header\n"); fclose(cf); return NULL; }
    if(nc <= 0 || nl <= 0 || D <= 0){
        fprintf(stderr, "[KAE] non-positive carrier dims %d/%d/%d\n", nc, nl, D); fclose(cf); return NULL; }
    if(D != hidden){
        fprintf(stderr, "[KAE] carrier D=%d != model hidden=%d\n", D, hidden); fclose(cf); return NULL; }
    KaE *k = (KaE*)calloc(1, sizeof(KaE));
    k->nc = nc; k->nl = nl; k->D = D; k->g = g; k->mode = mode;
    k->layer = (int*)malloc((size_t)nl * sizeof(int));
    if(fread(k->layer, sizeof(int), (size_t)nl, cf) != (size_t)nl){
        fprintf(stderr, "[KAE] short layer-id table\n"); fclose(cf); kae_free(k); return NULL; }
    for(int i = 0; i < nl; i++) if(k->layer[i] < 0 || k->layer[i] >= n_layers){
        fprintf(stderr, "[KAE] splice layer %d out of range [0,%d)\n", k->layer[i], n_layers);
        fclose(cf); kae_free(k); return NULL; }
    size_t ncar = (size_t)nc * nl * D;
    k->carrier = (float*)malloc(ncar * sizeof(float));
    if(fread(k->carrier, sizeof(float), ncar, cf) != ncar){
        fprintf(stderr, "[KAE] short carrier body (want %zu floats)\n", ncar); fclose(cf); kae_free(k); return NULL; }
    fclose(cf);

    FILE *sf = fopen(spans_path, "r");
    if(!sf){ fprintf(stderr, "[KAE] cannot open spans %s\n", spans_path); kae_free(k); return NULL; }
    int cap = 1024, n = 0, v;
    k->span = (int*)malloc((size_t)cap * sizeof(int));
    while(fscanf(sf, "%d", &v) == 1){
        if(n == cap){ cap *= 2; k->span = (int*)realloc(k->span, (size_t)cap * sizeof(int)); }
        if(v >= nc){ fprintf(stderr, "[KAE] span concept id %d >= nc %d at pos %d\n", v, nc, n); fclose(sf); kae_free(k); return NULL; }
        k->span[n++] = (v < 0) ? -1 : v;
    }
    fclose(sf);
    k->span_n = n;
    return k;
}

#endif /* KAE_H */
