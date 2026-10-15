# XUYI Phase 7: G-series buyer introductions, 98-model coverage (2026-10-15)

## Verified models, scope, and source provenance

- Previously reviewed introductions: **90 models, 450 product-language pages**. Phase 7 adds **8 × 5 = 40** localized introductions across genuine XUYI factory codes **G-01, G-02, G-03, G-04, G-05, G-09, G-10, G-12**. Total **98 / 101 product models and 490 / 505 product-language pages**; **3 actual product models remain on hold**.
- Factory model status and matching photo groups are established by `data/gallery-reference-products.json`, `gallery_catalog.py`, and `media/gallery/xuyi-gXX-*.webp`. Approved catalog styling categories are transparent flip-top/straw, gradient with time markers, compact handled jug, fitness handled jug, gradient with carry loop, clear carry-ring, compact gradient flip-top, and clear carry-ring respectively.
- These **are factory model IDs, not mere gallery category IDs**. Photo-backed descriptions are not evidence of exact capacity, physical dimensions, resin grades, gasket design, food-contact certification, tested leak performance, stock, MOQ, loading limit, or packaging. Every new introduction distinguishes verified visual presentation from per-SKU manufacturing attributes still requiring written confirmation.
- No invented ml, oz, length values, precise part compatibility, delivery promises, new images, source files or certifications. Five-language copy includes explicit procurement requests for model-labeled samples, source photos, artwork approval and supplier confirmation.

## Source-of-truth edits and D1/CMS precedence

- `data/phase7-g8-buyer-guides-{en,es,pt,ru,tr}.json`: 40 distinct, native-language 100–150-word buyer introductions.
- `data/phase7-g8-buyer-guides-addenda.json`: individual RU/TR source-verification additions for coverage.
- `data/phase7-g8-gallery-template-baselines.json`: baseline SHA256 of the *native* G-series localized page template from `gallery_catalog.detail`; **these are not D1 document hashes**.
- `sku_unique_openings_phase2.py`: merges approved G buyer guides before final HTML rendering and maintains exact source-content fingerprints. `sku_unique_openings.editor_intro` is the existing CMS-aware entry; it changes the first generic buyer-intro paragraph, not D1 records or `dist` output after rendering.
- `site_renderer.py` uses native G templates unless English D1/CMS has a body override. `scripts/render_locales.py` first accepts valid D1 localized content, and only falls back to the reviewed `gallery_catalog.detail` native template when no D1 field exists. This ensures future D1 admin updates take precedence.
- `scripts/test_phase7_g8_unique_factory_model_guides.py` now enforces existing factory code and category identity, source photo path, *no invented ml/oz/dimension quantities*, five languages, exact page marker content, template baseline, idempotence, simulated owner modification, and future growth not gated by existing SKU counts; added to `.github/workflows/publish-xuyi.yml`.
- `scripts/test_phase2_six_unique_sku_openings.py` now correctly restricts its checks to D1-owned translated products; LO- and G-series native-template translations each have independent guard tests.
- Source product photos, D1/R2 original data, inquiry records and unrelated design modules untouched.

## Measured improvement

- The static `scripts/audit_product_body_similarity.py` compares 3-word Jaccard shingles after masking numbers, on visible main-body and first H1-adjacent paragraph text, among same-category products and same locale. It is an editorial diagnostic **not a Google ranking or duplicate penalty threshold**.
- Fixed eight G factory models × five locales: introduction nearest-neighbor similarity median **1.0000 → 0.0130**; visible product-main-body median **0.9609 → 0.4863**.
- All 98 English reviewed models: nearest-main median **0.767**, intro median **0.044**; 3 held models: nearest-main **1.000**, intro **1.000**.
- Audit baseline `_local_ops/product-body-similarity-before-phase7-2026-10-15.json`; final `_local_ops/product-body-similarity-2026-10-14.json`. Last name is retained by established audit script despite the current review date.

## Builds and quality gates

- Two clean full source builds both passed: **973 files, 757 HTML, 101 true product-detail routes × five locales = 505, 755 sitemap URLs**.
- Site homepage, sitemap and all 8×5 new localized pages: **42 files SHA256 identical** across both builds; repeat insertion did not occur.
- **16/16 Python source/release regressions passed**, covering initial through seventh copy batches, CMS precedence, identity, G original images, locale content, canonicals/hreflang, schema, sitemap, SEO, future growth, and 0 broken internal links.
- No generated `dist` HTML is committed as a fix, no production D1 or R2 values intentionally changed. Production release must pass GitHub Actions, Cloudflare Pages deployment and deployed revision match before being called successful.

## Remaining three models — factory evidence required before unique technical text

1. **2506**: original factory source lists 60 ml with body dimensions of approximately 8.3×26.8 cm. Request a photo of the true model/spec panel and verified ml capacity, cap, materials and color data; do not convert 60ml into an assumed larger bottle or assign oz size classes until verified.
2. **5247** and **5248**: both shaker models share a `/media/ppt/slide-096.webp` source reference and combined 450/700 ml capacity information; confirm model-to-volume identity, separate matching photographs, opening/strainer and mixing-component distinctions, packaging and materials. Do not swap product images or invent lid differences.
3. Current local review queue: `_local_ops/phase2-remaining-sku-priority.csv`, exactly three records. Since those source distinctions are unresolved, the appropriate quality gate is to **hold them**, not to force 101/101 marketing-copy completion.

## Release trace
- Deployment must carry new committed source copy, editorial renderer, baseline hashes, source-of-truth regressions, release documentation, and workflow gate together. Production run SHA and success are appended in the final handoff after external verification.