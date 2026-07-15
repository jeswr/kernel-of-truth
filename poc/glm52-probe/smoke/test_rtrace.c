/* ============================================================================
 * test_rtrace.c — unit tests for the GLM-5.2 backend-smoke router-trace emitter
 * (rtrace.h).  No model, no weights, no instance: it links the SAME rtrace.h the
 * engine links and drives the emitter with synthetic, GLM-5.2-shaped router
 * state (256-ish experts, top-8, main sparse layers + an MTP-head layer).
 *
 * It asserts the gate-invariants the plan requires, then WRITES a real trace
 * file (argv[1], default /tmp/rtrace_selftest.jsonl) so trace_analyze.py can run
 * the integrity + go/no-go logic end-to-end on genuine emitter output.  This is
 * the $0 on-box proof of the trace PIPELINE (the box has no torch and ~0 free
 * disk, so it cannot convert/hold even the tiny model — the Modal tiny-oracle
 * run is the optional real-model confirm; see README).
 *
 * Properties checked (map to the plan's trace requirements):
 *   A. PER-ITEM RESET — begin_item zeroes cur_rows and RE-SEEDS the decision
 *      fingerprint; nothing carries across items (the CONTAMINATION-NOTE bug).
 *   B. TOP-K — the emitter writes exactly Ke route rows per token.
 *   C. MAIN vs MTP — is_mtp routes to site "mtp" (layer==n_layers) else "main".
 *   D. BYTE-IDENTICAL DECISIONS — two items with identical (pos,layer,rank,e)
 *      decisions get identical fingerprints; a single changed decision differs.
 *   E. IO TAG — pos < n_prompt => io 0 (input), else io 1 (target).
 * Exit 0 = all pass.
 * ==========================================================================*/
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "../rtrace.h"

static int fails = 0;
#define CHECK(cond,msg) do{ if(!(cond)){ printf("  FAIL: %s\n", msg); fails++; } \
                            else printf("  ok:   %s\n", msg); }while(0)

enum { E = 32, KE = 8, NL = 8 };          /* experts, top-k, model n_layers (MTP head = layer 8) */
static const int MAIN_LAYERS[5] = { 3,4,5,6,7 };

/* Deterministic GLM-5.2-shaped routing for (item,pos,layer): pick KE distinct
 * experts, strictly-decreasing selection scores, weights normalised to sum 1,
 * a positive top-k/top-(k+1) margin.  Fills idx/raw/gate/sel/w and returns margin. */
static float make_token(long item, int pos, int layer,
                        int *idx, float *raw, float *gate, float *sel, float *w){
    int step = 3;                                  /* coprime with 32 -> distinct */
    int base = (int)((item*7 + pos*5 + layer*11) % E);
    for(int e=0;e<E;e++){ sel[e] = -100.0f; gate[e]=0.0f; raw[e]=0.0f; }
    float wsum = 0.f;
    for(int kk=0; kk<KE; kk++){
        int e = (base + kk*step) % E;
        idx[kk] = e;
        sel[e]  = 50.0f - (float)kk;               /* strictly decreasing by rank */
        gate[e] = 0.9f - 0.05f*(float)kk;          /* pre-norm sigmoid gate        */
        raw[e]  = 2.0f - 0.3f*(float)kk;           /* pre-sigmoid logit            */
        w[kk]   = (float)(KE - kk);                /* unnormalised, then normalise */
        wsum   += w[kk];
    }
    for(int kk=0; kk<KE; kk++) w[kk] /= wsum;      /* norm_topk: weights sum to 1  */
    /* best dropped sel is any non-selected expert = -100 (< min kept 43) -> margin>0 */
    return sel[idx[KE-1]] - (-100.0f);
}

/* Emit one full item (all main layers, T tokens) to a trace.  `seed` drives the
 * routing DECISIONS (so a repeat probe reuses another item's seed while being
 * written under its own item id -> genuinely byte-identical decisions). */
static void emit_item_seeded(RTrace *rt, long item, long seed, int T, int n_prompt){
    int idx[KE]; float raw[E], gate[E], sel[E], w[KE];
    rtrace_begin_item(rt, item, T, n_prompt, KE, /*draft*/0);
    for(int pos=0; pos<T; pos++)
        for(int li=0; li<5; li++){
            int layer = MAIN_LAYERS[li];
            float mgn = make_token(seed, pos, layer, idx, raw, gate, sel, w);
            rtrace_token(rt, layer, /*is_mtp*/0, pos, KE, idx, raw, gate, sel, w, mgn);
        }
    rtrace_end_item(rt);
}
static void emit_item(RTrace *rt, long item, int T, int n_prompt){
    emit_item_seeded(rt, item, item, T, n_prompt);
}

int main(int argc, char **argv){
    const char *out = argc>1 ? argv[1] : "/tmp/rtrace_selftest.jsonl";

    /* ---- mechanism assertions on an in-memory trace ---- */
    RTrace *rt = rtrace_open("/tmp/rtrace_unit.jsonl", NL);
    if(!rt){ printf("FATAL: rtrace_open NULL\n"); return 2; }

    printf("== A. per-item reset (no carry-over) ==\n");
    int idx[KE]; float raw[E], gate[E], sel[E], w[KE];
    rtrace_begin_item(rt, 0, 3, 2, KE, 0);
    CHECK(rt->cur_rows==0 && rt->cur_item==0 && rt->in_item==1, "begin item 0: rows=0, bound");
    uint64_t seed0 = rt->dh;
    float mgn = make_token(0,0,3,idx,raw,gate,sel,w);
    rtrace_token(rt,3,0,0,KE,idx,raw,gate,sel,w,mgn);
    CHECK(rt->cur_rows==KE, "one token emitted exactly KE rows");
    CHECK(rt->dh!=seed0, "fingerprint advanced by the token");
    rtrace_end_item(rt);
    rtrace_begin_item(rt, 1, 3, 2, KE, 0);
    CHECK(rt->cur_rows==0, "begin item 1: cur_rows RESET to 0");
    CHECK(rt->dh==RTRACE_FNV_OFFSET, "begin item 1: fingerprint RE-SEEDED (no carry-over)");
    rtrace_end_item(rt);

    printf("== B. top-k count ==\n");
    rtrace_begin_item(rt, 2, 1, 1, KE, 0);
    mgn = make_token(2,0,5,idx,raw,gate,sel,w);
    rtrace_token(rt,5,0,0,KE,idx,raw,gate,sel,w,mgn);
    CHECK(rt->cur_rows==KE, "emitter wrote exactly Ke rows for the token");
    rtrace_end_item(rt);

    printf("== C. main vs MTP disambiguation ==\n");
    /* fingerprint the same decision at a main layer vs the MTP head: site differs
     * in the row, and the emitter is handed is_mtp from layer==n_layers. */
    rtrace_begin_item(rt, 3, 1, 1, KE, 1);
    mgn = make_token(3,0,7,idx,raw,gate,sel,w);
    rtrace_token(rt,7,  /*is_mtp*/0, 0, KE, idx,raw,gate,sel,w, mgn);   /* main layer 7 */
    rtrace_token(rt,NL, /*is_mtp*/1, 0, KE, idx,raw,gate,sel,w, mgn);   /* MTP head layer 8 */
    CHECK(rt->cur_rows==2*KE, "main + mtp tokens both emitted");
    rtrace_end_item(rt);
    rtrace_close(rt);
    /* verify the site strings actually landed in the file */
    { FILE *f=fopen("/tmp/rtrace_unit.jsonl","r"); char line[512]; int seen_main=0, seen_mtp=0;
      while(fgets(line,sizeof line,f)){ if(strstr(line,"\"layer\":8,")&&strstr(line,"\"site\":\"mtp\"")) seen_mtp=1;
        if(strstr(line,"\"layer\":7,")&&strstr(line,"\"site\":\"main\"")) seen_main=1; }
      fclose(f);
      CHECK(seen_main && seen_mtp, "trace file carries site=main (layer 7) AND site=mtp (layer 8)"); }

    printf("== D. byte-identical decisions on a repeated probe ==\n");
    {
        RTrace *a = rtrace_open("/tmp/rtrace_a.jsonl", NL);
        RTrace *b = rtrace_open("/tmp/rtrace_b.jsonl", NL);
        emit_item(a, 100, 6, 4);
        emit_item(b, 100, 6, 4);            /* identical item -> identical decisions */
        uint64_t fa=a->dh, fb=b->dh;
        CHECK(fa==fb, "identical probe -> identical decision fingerprint");
        /* one changed decision -> different fingerprint */
        RTrace *cc = rtrace_open("/tmp/rtrace_c.jsonl", NL);
        rtrace_begin_item(cc,100,6,4,KE,0);
        int idx2[KE]; float raw2[E],gate2[E],sel2[E],w2[KE];
        for(int pos=0;pos<6;pos++) for(int li=0;li<5;li++){ int layer=MAIN_LAYERS[li];
            float m2=make_token(100,pos,layer,idx2,raw2,gate2,sel2,w2);
            if(pos==0&&li==0) idx2[0]=(idx2[0]+1)%E;  /* flip one selected expert */
            rtrace_token(cc,layer,0,pos,KE,idx2,raw2,gate2,sel2,w2,m2);
        }
        uint64_t fc=cc->dh;
        CHECK(fc!=fa, "one changed selection -> different fingerprint (detects drift)");
        rtrace_close(a); rtrace_close(b); rtrace_close(cc);
    }

    printf("== E. io tag (input vs target) ==\n");
    {
        RTrace *e = rtrace_open("/tmp/rtrace_io.jsonl", NL);
        rtrace_begin_item(e, 200, 4, 2, KE, 0);   /* n_prompt=2 */
        for(int pos=0;pos<4;pos++){ float m3=make_token(200,pos,3,idx,raw,gate,sel,w);
            rtrace_token(e,3,0,pos,KE,idx,raw,gate,sel,w,m3); }
        rtrace_end_item(e); rtrace_close(e);
        FILE *f=fopen("/tmp/rtrace_io.jsonl","r"); char line[512]; int in0=0,in1=0,tg0=0,tg1=0;
        while(fgets(line,sizeof line,f)){
            if(strstr(line,"\"tok\":0,")&&strstr(line,"\"io\":0")) in0=1;
            if(strstr(line,"\"tok\":1,")&&strstr(line,"\"io\":0")) in1=1;
            if(strstr(line,"\"tok\":2,")&&strstr(line,"\"io\":1")) tg0=1;
            if(strstr(line,"\"tok\":3,")&&strstr(line,"\"io\":1")) tg1=1;
        }
        fclose(f);
        CHECK(in0&&in1&&tg0&&tg1, "tok<n_prompt => io=0; tok>=n_prompt => io=1");
    }

    /* ---- write the end-to-end analyzer fixture: a GLM-5.2-shaped run ----
     * items 0,1,2 distinct; item 3 = EXACT repeat of item 0 (byte-identity pair);
     * item 4 short with an MTP-head token. */
    printf("== write analyzer fixture: %s ==\n", out);
    {
        RTrace *g = rtrace_open(out, NL);
        if(!g){ printf("FATAL: cannot open fixture %s\n", out); return 2; }
        emit_item(g, 0, 6, 4);
        emit_item(g, 1, 5, 3);
        emit_item(g, 2, 7, 5);
        emit_item_seeded(g, 3, /*seed=item 0*/0, 6, 4);   /* repeat pair 0:3: identical decisions */
        /* item 4: draft=1, one token, main layer 7 + MTP head layer 8 */
        rtrace_begin_item(g, 4, 1, 1, KE, 1);
        float m4=make_token(4,0,7,idx,raw,gate,sel,w);
        rtrace_token(g,7, 0, 0, KE, idx,raw,gate,sel,w, m4);
        m4=make_token(4,0,NL,idx,raw,gate,sel,w);
        rtrace_token(g,NL,1, 0, KE, idx,raw,gate,sel,w, m4);
        rtrace_end_item(g);
        rtrace_close(g);
        printf("  wrote fixture (items 0-4; repeat pair 0:3; item4 has an MTP row)\n");
    }

    printf("\n%s (%d failure%s)\n", fails?"TESTS FAILED":"ALL TESTS PASSED",
           fails, fails==1?"":"s");
    return fails ? 1 : 0;
}
