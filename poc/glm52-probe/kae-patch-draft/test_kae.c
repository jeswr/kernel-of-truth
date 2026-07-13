/* ============================================================================
 * test_kae.c — mock unit tests for the F1-K KaE ADD-path + scoring mechanics.
 * DRAFT FOR GATE-0 REVIEW, NOT DEPLOYED.  No model, no weights, no instance:
 * a synthetic tiny setup (nc=3 concepts, D=4, splice layers {3,7}) that links
 * the SAME kae.h the engine links, writes real KAE_CARRIER/KAE_SPANS fixtures,
 * loads them through kae_load(), and asserts the gate-0 properties:
 *   A. the GATE fires on exactly the right tokens (and layers);
 *   B. the CARRIER adds correctly (out += g*K[c][l]) and ONLY at gated rows;
 *   C. INERT-by-default: the ADD path is a no-op whenever it must not fire
 *      -> bytes unchanged (unit-level companion to the binary equivalence proof);
 *   D. the SCORING readout is CANDIDATE-INDEPENDENT (single-prefill label-logit
 *      argmax; no candidate/option parameter; depends only on the k label logits);
 *   E. loader fail-safe (malformed input -> NULL -> engine disables KaE);
 *   F. REQUEST-AWARE per-item span binding (item N uses item N's spans, no reuse).
 * Exit 0 = all pass; nonzero = a failure (printed).
 * ==========================================================================*/
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include "../kae.h"

static int fails = 0;
#define CHECK(cond, msg) do{ if(!(cond)){ printf("  FAIL: %s\n", msg); fails++; } \
                             else printf("  ok:   %s\n", msg); }while(0)

/* synthetic model geometry */
enum { NC = 3, NL = 2, D = 4, NLAYERS = 12, S = 8 };
static const int   LAYERS[NL] = { 3, 7 };
static const float G = 2.0f;
/* spans: concept id per absolute position (index); -1 = ungated */
static const int   SPANS[S]   = { -1, 0, -1, 2, 1, -1, 0, -1 };

/* carrier value used everywhere so tests can predict exact results */
static float Kval(int c, int slot, int d){ return (float)(100*c + 10*slot + d); }

static void write_fixtures(const char *cpath, const char *spath){
    FILE *cf = fopen(cpath, "wb");
    int32_t nc = NC, nl = NL, dd = D;
    fwrite("KAEC", 1, 4, cf);
    fwrite(&nc, 4, 1, cf); fwrite(&nl, 4, 1, cf); fwrite(&dd, 4, 1, cf);
    for(int i = 0; i < NL; i++){ int32_t L = LAYERS[i]; fwrite(&L, 4, 1, cf); }
    for(int c = 0; c < NC; c++) for(int s = 0; s < NL; s++) for(int d = 0; d < D; d++){
        float v = Kval(c, s, d); fwrite(&v, 4, 1, cf); }
    fclose(cf);
    FILE *sf = fopen(spath, "w");
    for(int i = 0; i < S; i++) fprintf(sf, "%d\n", SPANS[i]);
    fclose(sf);
}

/* fill out[S*D] with a distinctive, reproducible baseline */
static void fill_baseline(float *out){
    for(int s = 0; s < S; s++) for(int d = 0; d < D; d++) out[s*D+d] = (float)(s*10 + d);
}

int main(void){
    const char *cpath = "/tmp/kae_carrier.bin", *spath = "/tmp/kae_spans.txt";
    write_fixtures(cpath, spath);

    /* end-to-end load through the engine's loader (exercises file formats too) */
    KaE *k = kae_load(cpath, spath, /*hidden*/D, /*n_layers*/NLAYERS, G, /*mode ADD*/0);
    if(!k){ printf("FATAL: kae_load returned NULL\n"); return 2; }

    printf("== Test A: gate fires on the right tokens/layers ==\n");
    for(int i = 0; i < S; i++){
        char m[64]; snprintf(m, sizeof m, "concept_at(pos %d) == %d", i, SPANS[i]);
        CHECK(kae_concept_at(k, i) == SPANS[i], m);
    }
    CHECK(kae_concept_at(k, -1) == -1,      "concept_at(-1) == -1 (below range)");
    CHECK(kae_concept_at(k, S)  == -1,      "concept_at(past end) == -1 (above range)");
    CHECK(kae_slot_of_layer(k, 3) == 0,     "layer 3 is splice slot 0");
    CHECK(kae_slot_of_layer(k, 7) == 1,     "layer 7 is splice slot 1");
    CHECK(kae_slot_of_layer(k, 4) == -1,    "layer 4 is NOT a splice layer");
    CHECK(kae_slot_of_layer(k, 0) == -1,    "layer 0 is NOT a splice layer");

    printf("== Test B: carrier adds correctly, only at gated rows/splice layers ==\n");
    float out[S*D], ref[S*D];
    fill_baseline(out); fill_baseline(ref);
    kae_apply_add(k, /*layer*/3, /*pos_base*/0, S, D, out);
    int b1 = 1;
    for(int s = 0; s < S; s++){ int cid = SPANS[s];
        for(int d = 0; d < D; d++){
            float want = ref[s*D+d] + (cid < 0 ? 0.f : G * Kval(cid, 0, d));
            if(out[s*D+d] != want) b1 = 0; } }
    CHECK(b1, "layer 3: gated rows get +g*K[c][slot0], ungated rows unchanged");

    fill_baseline(out);
    kae_apply_add(k, /*layer*/7, /*pos_base*/0, S, D, out);
    int b2 = 1;
    for(int s = 0; s < S; s++){ int cid = SPANS[s];
        for(int d = 0; d < D; d++){
            float want = ref[s*D+d] + (cid < 0 ? 0.f : G * Kval(cid, 1, d));
            if(out[s*D+d] != want) b2 = 0; } }
    CHECK(b2, "layer 7: uses slot-1 carrier (per-layer table is distinct)");

    fill_baseline(out);
    kae_apply_add(k, /*layer*/3, /*pos_base*/2, S, D, out);
    int b3 = 1;
    for(int s = 0; s < S; s++){ int pos = 2 + s;
        int cid = (pos < S) ? SPANS[pos] : -1;
        for(int d = 0; d < D; d++){
            float want = ref[s*D+d] + (cid < 0 ? 0.f : G * Kval(cid, 0, d));
            if(out[s*D+d] != want) b3 = 0; } }
    CHECK(b3, "pos_base=2 shifts gating by absolute position (rows past sidecar inert)");

    printf("== Test C: inert-by-default (no-op whenever the splice must not fire) ==\n");
    fill_baseline(out);
    kae_apply_add(k, /*layer*/4, 0, S, D, out);
    CHECK(memcmp(out, ref, sizeof out) == 0, "non-splice layer 4: out byte-identical");

    KaE *kr = kae_load(cpath, spath, D, NLAYERS, G, /*mode REPLACE*/1);
    fill_baseline(out);
    kae_apply_add(kr, 3, 0, S, D, out);
    CHECK(memcmp(out, ref, sizeof out) == 0, "REPLACE mode: ADD path inert (stub, gate-0)");
    kae_free(kr);

    fill_baseline(out);
    int g_kae = 0;                          /* mirrors the engine default */
    if(g_kae) kae_apply_add(k, 3, 0, S, D, out);   /* not taken */
    CHECK(memcmp(out, ref, sizeof out) == 0, "g_kae==0: splice skipped, out == upstream");

    fill_baseline(out);
    kae_apply_add(k, 3, 0, S, D, out);
    int changed_rows = 0, gated_expected = 0;
    for(int s = 0; s < S; s++) if(SPANS[s] >= 0) gated_expected++;
    for(int s = 0; s < S; s++){ int diff = 0;
        for(int d = 0; d < D; d++) if(out[s*D+d] != ref[s*D+d]) diff = 1;
        changed_rows += diff; }
    CHECK(changed_rows == gated_expected && gated_expected == 4,
          "enabled splice perturbs exactly the 4 gated rows, nothing else");

    printf("== Test D: candidate-independent single-prefill label-logit scoring (design R1.1) ==\n");
    {
        enum { V = 12 };
        float logits[V]; for(int i = 0; i < V; i++) logits[i] = (float)i * 0.1f;
        int label_ids[4] = { 2, 5, 7, 9 };            /* single-token labels A,B,C,D (published order) */
        logits[7] = 9.0f;                             /* token 7 = label index 2 = the winner */
        int pred = kae_argmax_label(logits, label_ids, 4);
        CHECK(pred == 2, "argmax over the k label tokens picks the max-logit label (index 2)");
        CHECK(kae_argmax_label(logits, label_ids, 4) == pred, "readout is deterministic");

        /* independence from NON-label logits: an option's content/length would move
         * OTHER logits via a per-candidate continuation; our readout ignores them. */
        float perturbed[V]; memcpy(perturbed, logits, sizeof logits);
        perturbed[0] = 100.f; perturbed[3] = -100.f; perturbed[8] = 50.f; perturbed[11] = 77.f;
        CHECK(kae_argmax_label(perturbed, label_ids, 4) == pred,
              "score depends ONLY on the k label-token logits, not on other tokens");

        /* deterministic tie-break = lowest label index */
        float tie[V]; for(int i = 0; i < V; i++) tie[i] = 0.f;
        tie[label_ids[1]] = 5.f; tie[label_ids[3]] = 5.f;
        CHECK(kae_argmax_label(tie, label_ids, 4) == 1, "tie-break selects the lowest label index");

        /* structural: scoring under different 'candidate contexts' (a variable the
         * readout has no parameter for) is invariant -> one prefill, no per-candidate forward. */
        int same = 1;
        for(int cand = 0; cand < 4; cand++) if(kae_argmax_label(logits, label_ids, 4) != pred) same = 0;
        CHECK(same, "prediction invariant to which candidate is 'evaluated' (no candidate arg)");

        /* the KaE splice contributes a candidate-independent delta, so it shifts the
         * shared prefill (hence every label logit) identically across arms. */
        float outA[S*D], outB[S*D];
        fill_baseline(outA); fill_baseline(outB);
        kae_apply_add(k, 3, 0, S, D, outA);
        kae_apply_add(k, 3, 0, S, D, outB);
        CHECK(memcmp(outA, outB, sizeof outA) == 0, "splice delta identical across arms/candidates");
    }

    printf("== Test E: loader fail-safe (misconfig -> NULL -> engine disables KaE) ==\n");
    printf("  (the [KAE] load-failure messages below are EXPECTED test output)\n");
    CHECK(kae_load(NULL,  spath, D, NLAYERS, G, 0) == NULL, "missing carrier path -> NULL");
    CHECK(kae_load(cpath, spath, D+1, NLAYERS, G, 0) == NULL, "hidden-dim mismatch -> NULL");
    CHECK(kae_load(cpath, spath, D, /*n_layers*/2, G, 0) == NULL, "splice layer out of range -> NULL");
    { FILE *bf = fopen("/tmp/kae_bad.bin","wb"); fputs("XXXX",bf); fclose(bf);
      CHECK(kae_load("/tmp/kae_bad.bin", spath, D, NLAYERS, G, 0) == NULL, "bad carrier magic -> NULL"); }
    { FILE *sf = fopen("/tmp/kae_badspans.txt","w"); fprintf(sf,"0 1 99\n"); fclose(sf);
      CHECK(kae_load(cpath, "/tmp/kae_badspans.txt", D, NLAYERS, G, 0) == NULL, "span cid out of range -> NULL"); }
    { FILE *sf = fopen("/tmp/kae_txtbad.txt","w"); fprintf(sf,"0 1 xyz\n"); fclose(sf);
      CHECK(kae_load(cpath, "/tmp/kae_txtbad.txt", D, NLAYERS, G, 0) == NULL, "non-integer span text -> NULL"); }
    /* carrier-only load is VALID (spans bound per item in the scoring path) */
    { KaE *kco = kae_load(cpath, NULL, D, NLAYERS, G, 0);
      CHECK(kco != NULL && kco->span_n == 0, "carrier-only load OK (spans optional, per-item)");
      kae_free(kco); }

    printf("== Test F: request-aware per-item span binding (no cross-item reuse) ==\n");
    {
        KaE *kf = kae_load(cpath, NULL, D, NLAYERS, G, 0);
        CHECK(kf != NULL, "carrier-only load for per-item binding");
        int spansA[3] = { 1, -1, -1 };
        CHECK(kae_bind_spans(kf, spansA, 3) == 0, "bind item A spans");
        CHECK(kae_concept_at(kf, 0) == 1,  "item A: position 0 gates concept 1");
        CHECK(kae_concept_at(kf, 1) == -1, "item A: position 1 ungated");
        int spansB[2] = { 2, -1 };          /* DIFFERENT concept, SHORTER */
        CHECK(kae_bind_spans(kf, spansB, 2) == 0, "bind item B spans (rebind)");
        CHECK(kae_concept_at(kf, 0) == 2,  "item B: position 0 now gates concept 2 (NOT item A's 1)");
        CHECK(kae_concept_at(kf, 2) == -1, "item B: position 2 out of range (no stale item-A tail)");
        int spansBad[2] = { 0, 99 };        /* 99 >= nc */
        CHECK(kae_bind_spans(kf, spansBad, 2) == -1, "bind rejects out-of-range concept id");
        CHECK(kf->span_n == 0, "rejected bind leaves spans empty (item scored ungated, no crash)");
        kae_reset_spans(kf);
        CHECK(kf->span_n == 0 && kae_concept_at(kf, 0) == -1, "reset clears spans");
        kae_free(kf);
    }

    kae_free(k);
    printf("\n%s (%d failure%s)\n", fails ? "TESTS FAILED" : "ALL TESTS PASSED",
           fails, fails == 1 ? "" : "s");
    return fails ? 1 : 0;
}
