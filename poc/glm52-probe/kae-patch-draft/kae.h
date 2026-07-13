#ifndef KAE_H
#define KAE_H
/* ============================================================================
 * KaE — Kernel-as-Expert (F1-K), ADD-path.  DRAFT FOR GATE-0 REVIEW, NOT DEPLOYED.
 *
 * Reviewable artifact for MAINTAINER GATE 0 of
 *   docs/next/design/glm52-followup-experiment.md (F1-K, through REVISION-6):
 * the code that would write a grounded per-concept content-vector into
 * GLM-5.2's MoE-block activations — a Law-1-amendment-gated action.  DRAFTED
 * for review; INERT unless the environment sets KAE=1; nothing here runs
 * against a governed model in this pass.
 *
 * Scope of THIS header (design §1.1 / §2.3 / §2.5 ADD, §R1.1 scoring):
 *   - the lexical concept GATE (G-lex): per-position concept ids arrive as a
 *     FROZEN, PER-ITEM sidecar (see kae_bind_spans) — the engine only reads
 *     them; zero learned components, deterministic, auditable byte-for-byte.
 *   - the per-concept per-layer CARRIER table K[c][l] (KAE_CARRIER).
 *   - the ADD splice (kae_apply_add): out += g*K[c][l] on gated tokens at
 *     splice layers, AFTER the routed sum + shared expert are accumulated and
 *     BEFORE the MoE block output re-enters the residual stream (native experts
 *     intact — pure ADD).
 *   - the frozen candidate-independent SCORING readout core (kae_argmax_label):
 *     argmax over the k answer-LABEL token logits of ONE shared prefill
 *     (design §R1.1).  Takes NO candidate/option/continuation argument, so the
 *     score of an item does not depend on which candidate is scored.
 *
 * REQUEST-AWARE gating: spans BIND PER ITEM via kae_bind_spans and are reset
 * between items (kae_reset_spans), so benchmark item N uses item N's spans and
 * never reuses item N-1's (positions are item-local).
 *
 * OUT OF SCOPE (documented stubs, deferred by the design):
 *   - REPLACE path (§2.5): kae_replace_note(); KAE_MODE=1 keeps ADD inert.
 *   - hidden-state DUMP mode (§2.4/§2.8) for carrier construction — harness-side.
 *   - G-emb cosine gate variant (§2.3) — budget-permitting, a later rung.
 *
 * Self-contained (no Model/Cfg dependency) so the mechanics unit-test against the
 * SAME source the engine links.  All symbols static-inline.  Fail-safe: any
 * malformed input or allocation failure yields NULL / a -1 return and DISABLES
 * KaE (the engine runs unmodified) — it never crashes or corrupts activations.
 *
 * File formats (host-endian; little-endian x86-64 assumed, documented in README):
 *   KAE_CARRIER : [4]="KAEC" | i32 nc | i32 nl | i32 D
 *                 | i32 layer_id[nl] (splice set L_KaE, ascending)
 *                 | f32 K[nc*nl*D]   (concept, then slot, then dim)
 *   KAE_SPANS   : ASCII ints, one per token position (index = position),
 *                 -1 = ungated.  Only the single-request default; the benchmark
 *                 scoring path binds spans per item (kae_bind_spans).
 * ==========================================================================*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <limits.h>

typedef struct KaE {
    int    nc;          /* number of concepts C                              */
    int    nl;          /* number of splice layers |L_KaE|                   */
    int    D;           /* carrier hidden dim (must equal model hidden)      */
    int   *layer;       /* [nl] splice layer ids (L_KaE), ascending          */
    float *carrier;     /* [nc*nl*D] K[c][slot][d], concept-major            */
    int   *span;        /* [span_n] position -> concept id (-1=off); PER-ITEM */
    int    span_n;      /* number of positions in the CURRENT item's sidecar */
    float  g;           /* blend weight (applied AFTER carrier norm), §2.3    */
    int    mode;        /* 0 = ADD (implemented); 1 = REPLACE (stub, §2.5)    */
} KaE;

/* checked size product: 0 on overflow, else *out = a*b. */
static inline int kae_szmul(size_t a, size_t b, size_t *out){
    if(a != 0 && b > SIZE_MAX / a) return 0;
    *out = a * b; return 1;
}

/* GATE readout: concept id at position `pos` (item-local), or -1 (ungated / out
 * of the current item's sidecar). The whole gate is this lookup. */
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

/* THE SPLICE (ADD path, §2.5). `out` is the MoE-block output [S*D] with the
 * routed sum + shared expert already accumulated. For each row s whose position
 * (pos_base+s) is gated to concept c at a splice layer, add g*K[c][slot]. Ungated
 * rows and non-splice layers are left bit-for-bit unchanged. No candidate arg. */
static inline void kae_apply_add(const KaE *k, int layer, int pos_base,
                                 int S, int D, float *out){
    if(!k || k->mode != 0) return;                 /* ADD path only          */
    int slot = kae_slot_of_layer(k, layer);
    if(slot < 0 || D != k->D) return;              /* not a splice layer / dim*/
    for(int s = 0; s < S; s++){
        int cid = kae_concept_at(k, pos_base + s);
        if(cid < 0 || cid >= k->nc) continue;      /* gate did not fire      */
        const float *Kcl = k->carrier + ((size_t)cid * k->nl + slot) * (size_t)D;
        float *os = out + (size_t)s * D;
        for(int d = 0; d < D; d++) os[d] += k->g * Kcl[d];
    }
}

/* FROZEN candidate-independent SCORING READOUT (design §R1.1). Given the
 * next-token logits of ONE shared prefill and the k single-token answer-LABEL
 * token ids in PUBLISHED order, return the argmax label index (deterministic
 * tie-break: lowest index, via strict >). The scored token set is exactly the
 * k labels — candidate-independent and length-invariant; there is NO
 * per-candidate continuation and NO option/candidate parameter. */
static inline int kae_argmax_label(const float *logits, const int *label_ids, int k){
    int best = 0; float bv = logits[label_ids[0]];
    for(int i = 1; i < k; i++){
        float v = logits[label_ids[i]];
        if(v > bv){ bv = v; best = i; }            /* strict > => lowest-index tie-break */
    }
    return best;
}

/* REQUEST-AWARE span binding: replace the current item's spans with `spans[0..n)`
 * (the item's frozen sidecar). Frees any previous item's spans (no reuse across
 * items). Validates every concept id in [-1, nc); on a bad id or allocation
 * failure returns -1 and leaves spans EMPTY (gate inert for this item). n==0
 * clears. No-op returning 0 when KaE is disabled (k==NULL). */
static inline int kae_bind_spans(KaE *k, const int *spans, int n){
    if(!k) return 0;
    int *dup = NULL;
    if(n > 0){
        size_t bytes;
        if(!kae_szmul((size_t)n, sizeof(int), &bytes)){ k->span_n = 0; return -1; }
        dup = (int*)malloc(bytes);
        if(!dup){ free(k->span); k->span = NULL; k->span_n = 0; return -1; }
        for(int i = 0; i < n; i++){
            int v = spans[i];
            if(v >= k->nc){ free(dup); free(k->span); k->span = NULL; k->span_n = 0; return -1; }
            dup[i] = (v < 0) ? -1 : v;
        }
    }
    free(k->span); k->span = dup; k->span_n = (n > 0) ? n : 0;
    return 0;
}

/* Clear the current item's spans (nothing gates until the next bind). */
static inline void kae_reset_spans(KaE *k){
    if(!k) return;
    free(k->span); k->span = NULL; k->span_n = 0;
}

/* REPLACE path (§2.5) — DOCUMENTED STUB, deferred behind a K-1 pass + its own NI
 * power gate (REVISION-4 §R-REV4.3). No-op here: REPLACE would skip the
 * lowest-sigmoid-weight native expert on gated tokens and add w_dropped*K in its
 * place, needing per-token dropped-weight bookkeeping in moe(). Not wired for
 * gate 0; KAE_MODE=1 makes kae_apply_add inert. */
static inline void kae_replace_note(void){ /* intentionally empty (stub) */ }

static inline void kae_free(KaE *k){
    if(!k) return;
    free(k->layer); free(k->carrier); free(k->span); free(k);
}

/* Load the carrier table (and, if spans_path != NULL, an optional default span
 * sidecar). Returns NULL (and prints why) on any malformed input, size overflow,
 * allocation failure, or hidden-dim mismatch — the caller treats NULL as
 * "KaE disabled". The benchmark scoring path passes spans_path=NULL and binds
 * spans per item (kae_bind_spans). hidden/n_layers validate the files. */
static inline KaE *kae_load(const char *carrier_path, const char *spans_path,
                            int hidden, int n_layers, float g, int mode){
    if(!carrier_path){
        fprintf(stderr, "[KAE] KAE=1 requires KAE_CARRIER=<file>\n");
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
    if(nl > n_layers){
        fprintf(stderr, "[KAE] nl=%d exceeds n_layers=%d\n", nl, n_layers); fclose(cf); return NULL; }
    KaE *k = (KaE*)calloc(1, sizeof(KaE));
    if(!k){ fprintf(stderr, "[KAE] alloc KaE failed\n"); fclose(cf); return NULL; }
    k->nc = nc; k->nl = nl; k->D = D; k->g = g; k->mode = mode;
    size_t lbytes;
    if(!kae_szmul((size_t)nl, sizeof(int), &lbytes)){ fprintf(stderr, "[KAE] layer-table size overflow\n"); fclose(cf); kae_free(k); return NULL; }
    k->layer = (int*)malloc(lbytes);
    if(!k->layer){ fprintf(stderr, "[KAE] alloc layer table failed\n"); fclose(cf); kae_free(k); return NULL; }
    if(fread(k->layer, sizeof(int), (size_t)nl, cf) != (size_t)nl){
        fprintf(stderr, "[KAE] short layer-id table\n"); fclose(cf); kae_free(k); return NULL; }
    for(int i = 0; i < nl; i++) if(k->layer[i] < 0 || k->layer[i] >= n_layers){
        fprintf(stderr, "[KAE] splice layer %d out of range [0,%d)\n", k->layer[i], n_layers);
        fclose(cf); kae_free(k); return NULL; }
    size_t ncar, tmp;
    if(!kae_szmul((size_t)nc, (size_t)nl, &tmp) || !kae_szmul(tmp, (size_t)D, &ncar) ||
       !kae_szmul(ncar, sizeof(float), &tmp)){
        fprintf(stderr, "[KAE] carrier size overflow (%d*%d*%d)\n", nc, nl, D); fclose(cf); kae_free(k); return NULL; }
    k->carrier = (float*)malloc(ncar * sizeof(float));
    if(!k->carrier){ fprintf(stderr, "[KAE] alloc carrier failed\n"); fclose(cf); kae_free(k); return NULL; }
    if(fread(k->carrier, sizeof(float), ncar, cf) != ncar){
        fprintf(stderr, "[KAE] short carrier body (want %zu floats)\n", ncar); fclose(cf); kae_free(k); return NULL; }
    fclose(cf);

    if(spans_path){
        FILE *sf = fopen(spans_path, "r");
        if(!sf){ fprintf(stderr, "[KAE] cannot open spans %s\n", spans_path); kae_free(k); return NULL; }
        int cap = 1024, n = 0, v, r;
        k->span = (int*)malloc((size_t)cap * sizeof(int));
        if(!k->span){ fprintf(stderr, "[KAE] alloc spans failed\n"); fclose(sf); kae_free(k); return NULL; }
        while((r = fscanf(sf, "%d", &v)) == 1){
            if(v >= nc){ fprintf(stderr, "[KAE] span concept id %d >= nc %d at pos %d\n", v, nc, n); fclose(sf); kae_free(k); return NULL; }
            if(n == cap){
                size_t ncap = (size_t)cap * 2;
                if(ncap > (size_t)INT_MAX){ fprintf(stderr, "[KAE] spans too large\n"); fclose(sf); kae_free(k); return NULL; }
                int *nsp = (int*)realloc(k->span, ncap * sizeof(int));
                if(!nsp){ fprintf(stderr, "[KAE] realloc spans failed\n"); fclose(sf); kae_free(k); return NULL; }
                k->span = nsp; cap = (int)ncap;
            }
            k->span[n++] = (v < 0) ? -1 : v;
        }
        if(r == 0){ fprintf(stderr, "[KAE] malformed (non-integer) span text\n"); fclose(sf); kae_free(k); return NULL; }
        fclose(sf);
        k->span_n = n;
    }
    return k;
}

#endif /* KAE_H */
