#ifndef RTRACE_H
#define RTRACE_H
/* ============================================================================
 * rtrace.h — per-token MoE ROUTER TRACE for the GLM-5.2 colibri backend-
 * feasibility SMOKE (Stage 1, docs/next/design/glm52-expert-profiling-plan-
 * sol-20260715.md).  EXPLORATORY infra — rigor relaxed vs a frozen experiment.
 *
 * PURPOSE.  Record, at the router, for every (item, token position, execution
 * site, layer) the SELECTED expert ids and their scores.  This is the direct,
 * per-item/per-token trace the plan requires ("§Required colibri trace"), and
 * the deliberate remedy for the session-cumulative STATS contamination bug
 * (poc/glm52-probe/CONTAMINATION-NOTE.md): the eusage/eheat histograms are
 * monotone across the whole session; THIS trace is reset per item and carries
 * nothing over.
 *
 * READ-ONLY.  The emitter never touches `out` or any activation.  When the
 * environment does not set RTRACE=<file> the engine holds g_rt==NULL and every
 * call here is a NULL-guarded no-op, so output is byte-identical to upstream
 * (the objdump per-function equivalence proof in build_apply.sh confirms it;
 * only moe/layer_forward/run path change, and only under g_rt!=NULL).
 *
 * WHAT IT READS (all already live inside moe() at emit time — no recompute):
 *   - idx[kk]  : the kk-th selected expert id (colibri's selection order).
 *   - w[kk]    : that expert's NORMALISED routed weight (post norm_topk ×
 *                routed_scale) — the weight actually used to combine experts.
 *   - gate[e]  : sigmoidf(router_logit[e]); colibri keeps this in `logit[]` for
 *                every expert e for the whole of moe() — the PRE-normalisation
 *                router score.
 *   - sel[e]   : gate[e] + router_bias[e] = choice[e]; colibri's selection
 *                criterion (topk_method=noaux_tc).  Ranking is by this.
 *   - raw[e]   : the pre-sigmoid router logit (captured before the sigmoid
 *                overwrite; NULL-tolerant).
 *   - margin   : the top-k / top-(k+1) separation for this token = min-over-kept
 *                sel  −  max-over-dropped sel.
 *
 * EXECUTION-SITE DISAMBIGUATION.  colibri runs the MTP head as layer index
 * == n_layers (main sparse layers are < n_layers).  rtrace_token() is passed
 * is_mtp = (layer == n_layers), so main-model experts (layers 3..77) and the
 * MTP layer-78 experts are never conflated (plan §Stage-1 requirement; the
 * main atlas runs DRAFT=0 so MTP does not fire, but the field is always right).
 *
 * PER-ITEM RESET (the anti-contamination invariant).  rtrace_begin_item()
 * zeroes the per-item row counter and RE-SEEDS the decision fingerprint, and
 * rtrace_end_item() flushes a per-item summary.  A route row can only be
 * attributed to the item named in the preceding `begin`.  The fingerprint is
 * an FNV-1a-64 over the routing DECISIONS ONLY — (pos, layer, rank, expert),
 * not the floats — so it is invariant to int4 kernel-family rounding: a
 * repeated probe is byte-identical on decisions (plan go/no-go).
 *
 * Self-contained (no Model/Cfg dependency) so the mechanics unit-test against
 * the SAME source the engine links (tests/test_rtrace.c).
 * ==========================================================================*/
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

typedef struct RTrace {
    FILE    *fp;            /* trace sink (JSONL)                              */
    int      n_layers;      /* model n_layers; layer==n_layers => MTP head     */
    long     cur_item;      /* current item id (-1 = between items)            */
    int      cur_n_prompt;  /* prompt length -> input-vs-target tag for io     */
    long     cur_rows;      /* route rows emitted for THIS item (reset each)   */
    uint64_t dh;            /* FNV-1a-64 over (pos,layer,rank,expert) decisions */
    int      in_item;       /* 1 between begin/end (fail-closed guard)         */
} RTrace;

#define RTRACE_FNV_OFFSET 1469598103934665603ULL
#define RTRACE_FNV_PRIME  1099511628211ULL

static inline void rtrace_mix(RTrace *rt, uint64_t v){
    for(int i=0;i<8;i++){ rt->dh ^= (v & 0xff); rt->dh *= RTRACE_FNV_PRIME; v >>= 8; }
}

/* Open a trace sink.  Returns NULL (KaE-style fail-safe: tracing simply
 * disabled) on a NULL path or an unopenable file — never aborts the engine. */
static inline RTrace *rtrace_open(const char *path, int n_layers){
    if(!path) return NULL;
    FILE *fp = fopen(path, "wb");
    if(!fp){ fprintf(stderr, "[RTRACE] cannot open %s -> tracing DISABLED\n", path); return NULL; }
    RTrace *rt = (RTrace*)calloc(1, sizeof(RTrace));
    if(!rt){ fclose(fp); return NULL; }
    rt->fp = fp; rt->n_layers = n_layers; rt->cur_item = -1; rt->in_item = 0;
    fprintf(fp,
        "{\"t\":\"hdr\",\"schema\":\"kot-rtrace/1\",\"n_layers\":%d,"
        "\"fields\":[\"item\",\"tok\",\"io\",\"site\",\"layer\",\"rank\",\"e\","
        "\"raw\",\"gate\",\"sel\",\"w\",\"mgn\"]}\n", n_layers);
    return rt;
}

static inline void rtrace_close(RTrace *rt){
    if(!rt) return;
    if(rt->fp){ fflush(rt->fp); fclose(rt->fp); }
    free(rt);
}

/* PER-ITEM RESET.  Start a fresh item: zero the row counter, re-seed the
 * decision fingerprint, bind the prompt length for io tagging.  Nothing from
 * item N-1 survives into item N (contra the cumulative STATS dumps). */
static inline void rtrace_begin_item(RTrace *rt, long item, int T, int n_prompt,
                                     int topk, int draft){
    if(!rt) return;
    rt->cur_item = item; rt->cur_n_prompt = n_prompt; rt->cur_rows = 0;
    rt->dh = RTRACE_FNV_OFFSET; rt->in_item = 1;
    fprintf(rt->fp,
        "{\"t\":\"begin\",\"item\":%ld,\"T\":%d,\"n_prompt\":%d,\"topk\":%d,\"draft\":%d}\n",
        item, T, n_prompt, topk, draft);
}

/* Close the item: emit its row count and decision fingerprint, flush. */
static inline void rtrace_end_item(RTrace *rt){
    if(!rt || !rt->in_item) return;
    fprintf(rt->fp,
        "{\"t\":\"end\",\"item\":%ld,\"rows\":%ld,\"decident_fnv1a64\":\"%016llx\"}\n",
        rt->cur_item, rt->cur_rows, (unsigned long long)rt->dh);
    fflush(rt->fp);
    rt->in_item = 0;
}

/* Emit the selected-expert rows for one token.  READ-ONLY.
 *   idx[kk]           = kk-th selected expert id (selection order).
 *   raw/gate/sel      = per-EXPERT arrays (length E), indexed by expert id.
 *   w[kk]             = kk-th normalised routed weight (selection order).
 *   is_mtp            = layer == n_layers (MTP head) else main.
 *   pos               = item-local token position (prefill starts at pos_base 0).
 *   Ke                = effective top-k for this token.
 *   margin            = min-over-kept sel − max-over-dropped sel (top-k/top-k+1). */
static inline void rtrace_token(RTrace *rt, int layer, int is_mtp, int pos, int Ke,
                                const int *idx, const float *raw, const float *gate,
                                const float *sel, const float *w, float margin){
    if(!rt || !rt->in_item) return;
    int io = (pos >= rt->cur_n_prompt) ? 1 : 0;   /* 0 = prompt/input, 1 = target */
    const char *site = is_mtp ? "mtp" : "main";
    for(int kk=0; kk<Ke; kk++){
        int e = idx[kk];
        fprintf(rt->fp,
          "{\"t\":\"r\",\"item\":%ld,\"tok\":%d,\"io\":%d,\"site\":\"%s\",\"layer\":%d,"
          "\"rank\":%d,\"e\":%d,\"raw\":%.6g,\"gate\":%.6g,\"sel\":%.6g,\"w\":%.6g,\"mgn\":%.6g}\n",
          rt->cur_item, pos, io, site, layer, kk, e,
          (double)(raw ? raw[e] : 0.0f), (double)(gate ? gate[e] : 0.0f),
          (double)(sel ? sel[e] : 0.0f), (double)(w ? w[kk] : 0.0f), (double)margin);
        /* fingerprint the DECISION only (rounding-invariant across kernels). */
        rtrace_mix(rt, ((uint64_t)(uint32_t)pos    << 40)
                     ^ ((uint64_t)(uint32_t)layer  << 24)
                     ^ ((uint64_t)(uint32_t)kk     << 16)
                     ^ ((uint64_t)(uint32_t)e));
        rt->cur_rows++;
    }
}

#endif /* RTRACE_H */
