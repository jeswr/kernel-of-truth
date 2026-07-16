/* ============================================================================
 * test_kae_dump.c — mock unit tests for the kot-f1k-dump/1 moe()-input dump.
 * DRAFT FOR GATE-0 REVIEW, NOT DEPLOYED.  No model, no weights, no instance:
 * a synthetic tiny setup (D=6, dump layers {5,2,9} — deliberately NON-sorted
 * to pin slot order == KAE_DUMP_LAYERS order) that links the SAME kae_dump.h
 * (and, through it, the SAME kae.h span binding) the engine links, and
 * asserts the construction-dump properties:
 *   A. arming is fail-closed (bad/duplicate/out-of-range layer ids, missing
 *      out path, malformed csv all -> NULL; valid csv preserves order);
 *   B. the capture sums the moe() INPUT x over EXACTLY the gated positions
 *      (reused kae.h span binding; pos_base honoured; non-dump layers no-op;
 *      f64 accumulation matches an independent double re-derivation);
 *   C. the capture is READ-ONLY on x and errs closed on a hidden-dim
 *      mismatch;
 *   D. the ASM-2488 per-slot gated-count invariant fails closed (a dump
 *      layer that moe() never reached aborts the line);
 *   E. the KAED bytes are exactly the contract (magic, header, layer order,
 *      per-line gated_count + f32-cast sums);
 *   F. per-line bind/reset semantics (rebind replaces, reset disarms).
 * Exit 0 = all pass; nonzero = a failure (printed).
 * ==========================================================================*/
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include "../kae_dump.h"

static int fails = 0;
#define CHECK(cond, msg) do{ if(!(cond)){ printf("  FAIL: %s\n", msg); fails++; } \
                             else printf("  ok:   %s\n", msg); }while(0)

enum { D = 6, NLAYERS = 12, S = 5 };
static const char *CSV = "5,2,9";              /* NON-sorted: slot order = csv order */
static const int LAYERS[3] = { 5, 2, 9 };
/* spans: slot per absolute position; -1 = ungated */
static const int SPANS[S] = { -1, 7, 0, -1, 95 };

/* deterministic moe()-input fixture: exact in f32 (k/8 grid) */
static float Xval(int pos, int d){ return (float)(pos * 8 + d) / 8.0f - 2.0f; }
static void fill_x(float *x, int pos0, int n){
    for(int s = 0; s < n; s++) for(int d = 0; d < D; d++)
        x[s*D + d] = Xval(pos0 + s, d);
}

int main(void){
    const char *opath = "/tmp/kae_dump_test.kaed";

    printf("== Test A: fail-closed arming ==\n");
    printf("  (the [KAE-DUMP] arm-failure messages below are EXPECTED test output)\n");
    CHECK(kaed_arm(NULL,  opath, D, NLAYERS) == NULL, "missing KAE_DUMP_LAYERS -> NULL");
    CHECK(kaed_arm("",    opath, D, NLAYERS) == NULL, "empty KAE_DUMP_LAYERS -> NULL");
    CHECK(kaed_arm(CSV,   NULL,  D, NLAYERS) == NULL, "missing KAE_DUMP_OUT -> NULL");
    CHECK(kaed_arm("5,x", opath, D, NLAYERS) == NULL, "non-integer layer id -> NULL");
    CHECK(kaed_arm("5,5", opath, D, NLAYERS) == NULL, "duplicate layer id -> NULL");
    CHECK(kaed_arm("5,12",opath, D, NLAYERS) == NULL, "layer id >= n_layers -> NULL");
    CHECK(kaed_arm("-1",  opath, D, NLAYERS) == NULL, "negative layer id -> NULL");
    CHECK(kaed_arm("5,",  opath, D, NLAYERS) == NULL, "trailing comma -> NULL");
    CHECK(kaed_arm("5 2", opath, D, NLAYERS) == NULL, "space-separated csv -> NULL");
    KaEDump *kd = kaed_arm(CSV, opath, D, NLAYERS);
    if(!kd){ printf("FATAL: valid arm returned NULL\n"); return 2; }
    CHECK(kd->nl == 3 && kd->D == D, "valid arm: nl=3, D matches model");
    int order_ok = 1;
    for(int i = 0; i < 3; i++) if(kd->layer[i] != LAYERS[i]) order_ok = 0;
    CHECK(order_ok, "slot order == KAE_DUMP_LAYERS order (5,2,9 — NOT sorted)");
    CHECK(kaed_slot_of_layer(kd, 2) == 1, "layer 2 is slot 1 (csv order)");
    CHECK(kaed_slot_of_layer(kd, 3) == -1, "layer 3 is not a dump layer");

    printf("== Test B: capture sums exactly the gated positions (f64) ==\n");
    CHECK(kaed_write_header(kd, 2) == 0, "KAED header written");
    CHECK(kaed_bind_line(kd, SPANS, S) == 0, "bind line-0 spans (reused kae_bind_spans)");
    float x[S*D];
    fill_x(x, 0, S);
    /* one full-S call per dump layer + a non-dump layer (must be a no-op) */
    kaed_capture(kd, 5, 0, S, D, x);
    kaed_capture(kd, 3, 0, S, D, x);      /* not in the dump set */
    kaed_capture(kd, 2, 0, S, D, x);
    kaed_capture(kd, 9, 0, S, D, x);
    /* independent double re-derivation over gated positions {1,2,4} */
    int b_ok = 1;
    for(int slot = 0; slot < 3; slot++) for(int d = 0; d < D; d++){
        double want = 0.0;
        for(int p = 0; p < S; p++) if(SPANS[p] >= 0) want += (double)Xval(p, d);
        if(kd->acc[slot*D + d] != want) b_ok = 0;
    }
    CHECK(b_ok, "every slot's f64 sum == independent double re-derivation over gated rows");
    CHECK(kd->cnt[0] == 3 && kd->cnt[1] == 3 && kd->cnt[2] == 3,
          "per-slot gated count == 3 (positions 1,2,4)");
    CHECK(kaed_write_line(kd, 0, 3) == 0, "line 0 written (per-slot invariant holds)");

    printf("== Test C: read-only capture + hidden-dim fail-closed ==\n");
    kaed_reset_line(kd);
    CHECK(kaed_bind_line(kd, SPANS, S) == 0, "bind line-1 spans");
    float xref[S*D];
    fill_x(x, 0, S); memcpy(xref, x, sizeof x);
    /* CHUNKED prefill emulation: two calls with pos_base 0 and 3 must equal
     * one full-S call (absolute-position gating via the reused kae gate). */
    kaed_capture(kd, 5, 0, 3, D, x);
    kaed_capture(kd, 5, 3, 2, D, x + 3*D);
    kaed_capture(kd, 2, 0, S, D, x);
    kaed_capture(kd, 9, 0, S, D, x);
    CHECK(memcmp(x, xref, sizeof x) == 0, "capture left x byte-identical (read-only)");
    int chunk_ok = 1;
    for(int d = 0; d < D; d++){
        double want = 0.0;
        for(int p = 0; p < S; p++) if(SPANS[p] >= 0) want += (double)Xval(p, d);
        if(kd->acc[0*D + d] != want) chunk_ok = 0;
    }
    CHECK(chunk_ok && kd->cnt[0] == 3,
          "chunked capture (pos_base 0 then 3) == one full-S capture");
    printf("  (the [KAE-DUMP] capture/line error messages below are EXPECTED test output)\n");
    kaed_capture(kd, 9, 0, S, D + 1, x);   /* wrong hidden dim */
    CHECK(kd->err == 1, "hidden-dim mismatch sets the sticky error flag");
    CHECK(kaed_write_line(kd, 1, 3) != 0, "write_line fails closed on capture error");

    printf("== Test D: ASM-2488 per-slot count invariant ==\n");
    kaed_reset_line(kd);
    CHECK(kaed_bind_line(kd, SPANS, S) == 0, "bind line spans again");
    fill_x(x, 0, S);
    kaed_capture(kd, 5, 0, S, D, x);
    kaed_capture(kd, 2, 0, S, D, x);       /* layer 9 never reached */
    CHECK(kaed_write_line(kd, 2, 3) != 0, "a dump layer moe() never reached -> line fails closed");
    kaed_bind_line(kd, SPANS, S);
    fill_x(x, 0, S);
    kaed_capture(kd, 5, 0, S, D, x);
    kaed_capture(kd, 5, 0, S, D, x);       /* double visit */
    kaed_capture(kd, 2, 0, S, D, x);
    kaed_capture(kd, 9, 0, S, D, x);
    CHECK(kaed_write_line(kd, 3, 3) != 0, "a position visited twice -> line fails closed");

    printf("== Test E: KAED bytes are exactly the contract ==\n");
    /* re-arm cleanly and write a 2-line file, then read the bytes back */
    kaed_free(kd);
    kd = kaed_arm(CSV, opath, D, NLAYERS);
    CHECK(kd != NULL, "re-arm for the byte-layout check");
    CHECK(kaed_write_header(kd, 2) == 0, "header written");
    for(int line = 0; line < 2; line++){
        kaed_bind_line(kd, SPANS, S);
        fill_x(x, line, S);                 /* line 1 shifts positions by 1 */
        kaed_capture(kd, 5, 0, S, D, x);
        kaed_capture(kd, 2, 0, S, D, x);
        kaed_capture(kd, 9, 0, S, D, x);
        if(kaed_write_line(kd, line, 3) != 0){ printf("  FAIL: line %d write\n", line); fails++; }
        kaed_reset_line(kd);
    }
    CHECK(kaed_finish(kd) == 0, "finish flushed and closed the file");
    {
        FILE *f = fopen(opath, "rb");
        CHECK(f != NULL, "KAED file exists");
        char magic[4]; int32_t hdr[3], lay[3];
        CHECK(fread(magic, 1, 4, f) == 4 && memcmp(magic, "KAED", 4) == 0, "magic == KAED");
        CHECK(fread(hdr, 4, 3, f) == 3 && hdr[0] == 2 && hdr[1] == 3 && hdr[2] == D,
              "header n_lines=2, nl=3, D matches");
        CHECK(fread(lay, 4, 3, f) == 3 && lay[0] == 5 && lay[1] == 2 && lay[2] == 9,
              "layer ids in KAE_DUMP_LAYERS order");
        int e_ok = 1;
        for(int line = 0; line < 2; line++){
            int32_t gc; float sums[3*D];
            if(fread(&gc, 4, 1, f) != 1 || gc != 3) e_ok = 0;
            if(fread(sums, 4, 3*D, f) != 3*D) e_ok = 0;
            for(int slot = 0; slot < 3 && e_ok; slot++) for(int d = 0; d < D; d++){
                double want = 0.0;
                for(int p = 0; p < S; p++) if(SPANS[p] >= 0)
                    want += (double)Xval(line + p, d);
                if(sums[slot*D + d] != (float)want) e_ok = 0;
            }
        }
        CHECK(e_ok, "per line: i32 gated_count=3 then f32 casts of the f64 sums, cell-exact");
        char extra;
        CHECK(fread(&extra, 1, 1, f) == 0, "no trailing bytes");
        fclose(f);
    }

    printf("== Test F: per-line bind/reset semantics (reused kae.h binding) ==\n");
    kaed_free(kd);
    kd = kaed_arm(CSV, opath, D, NLAYERS);
    CHECK(kd != NULL, "arm for bind/reset checks");
    int spansA[3] = { 4, -1, -1 }, spansB[2] = { -1, 2 };
    CHECK(kaed_bind_line(kd, spansA, 3) == 0, "bind line A");
    CHECK(kae_concept_at(&kd->gate, 0) == 4, "line A: position 0 gated (slot 4)");
    CHECK(kaed_bind_line(kd, spansB, 2) == 0, "rebind line B replaces line A");
    CHECK(kae_concept_at(&kd->gate, 0) == -1 && kae_concept_at(&kd->gate, 1) == 2,
          "line B spans in force, no stale line-A tail");
    CHECK(kae_concept_at(&kd->gate, 2) == -1, "past line B's end: ungated");
    kaed_reset_line(kd);
    CHECK(kae_concept_at(&kd->gate, 0) == -1, "reset disarms the gate");
    fill_x(x, 0, S);
    kaed_capture(kd, 5, 0, S, D, x);
    CHECK(kd->cnt[0] == 0, "capture after reset accumulates nothing");
    kaed_free(kd);

    printf("\n%s (%d failure%s)\n", fails ? "TESTS FAILED" : "ALL TESTS PASSED",
           fails, fails == 1 ? "" : "s");
    return fails ? 1 : 0;
}
