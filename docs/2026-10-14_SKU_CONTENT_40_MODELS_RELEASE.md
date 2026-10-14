# XUYI Product body differentiation — 40-model rollout, 2026-10-14

## Scope and authoritative data
- **101** product detail routes × **5** locales = **505** public product detail pages; the Products index is not a 102nd SKU.
- First approved round: 20 unique factory SKU introductions × 5 locales.
- Second source-controlled round: 20 unique verified-model introductions × 5 locales, including 6 previous local edits and 14 completed in this session.
- **40 models / 200 pages differentiated**; 61 models / 305 pages remain for evidence-backed editorial improvements.
- New 14 models: sports **2512, 2513, 2514, 2209, 2311, 2402**; kids **2109, 2409, 2413, 2350**; jugs **2250, 2270, 2416, 2305**.
- All second-round paragraphs are individually drafted with 100–150 whitespace-delimited words in each locale; design, sizes, material composition and master-carton details are derived from the XUYI D1/catalog snapshot. Unconfirmed closures, accessories, certifications, child safety and spill ratings are explicitly not asserted.
- The existing shaker models 5247/5248 are not guessed into artificial differentiation; 2506 anomalous 60ml and G-series unknown capacity remain subject to factory verification.

## Authoritative implementation
- `data/phase2-6-sku-openings-en.json`, `data/phase2-6-sku-openings-locales.json`, `data/phase2-6-sku-locale-addenda.json`, `data/phase2-6-sku-d1-body-baselines.json`: earlier six-model addition.
- `data/phase2-next14-openings-{en,es,pt,ru,tr}.json`, `data/phase2-next14-d1-baselines.json` and `data/phase2-next14-locale-addenda.json`: newly reviewed 14-model copy plus immutable, source-stage D1 body fingerprints.
- `sku_unique_openings_phase2.py` merges both approved sets before rendering and is called from existing `sku_unique_openings.py` and main CMS-aware source renderers. No direct `dist` edits to implement SKU introductions.
- Exact D1 `mainHtml` SHA-256 guard prevents the automatic copy from overwriting any later CMS owner edit. No duplicate insertion; later new SKUs are not blocked by a fixed SKU count.
- Production CI gate `scripts/test_phase2_six_unique_sku_openings.py` (historic path, now 20 second-wave models), original first-20 test and `scripts/test_source_of_truth_policy.py` test the ownership constraint.

## Audit results and verification
- `scripts/audit_product_body_similarity.py` scans rendered pages, masking numbers and using 3-token Jaccard against closest in-category product for each language. This is **not** a Google spam/Panda penalty score, not necessarily comparable to third-party 82% figures.
- Local result at 40 optimized models: English optimized pages nearest-neighbor visible-main similarity median **0.804**, remaining generic pages **1.000**. English buyer-opening medians: optimized **0.005** vs remaining **1.000**. Other locales: optimized main medians **ES 0.808, PT 0.802, RU 0.791, TR 0.790**.
- Product content split in second round: 20 new models / 100 pages; first 20 still stable.
- First full source build: `python -B scripts/build_release.py` succeeded, generated **973 assets/files including 757 HTML**; original **755 sitemap URLs**, no new invented product pages.
- Second independent clean full source build also succeeded. **72 output files** including new 14 × 5 product pages and homepage/sitemap have identical SHA-256 between builds.
- `scripts/test_release.py` reports zero broken links; 11 local regression tests including pilot/phase2 100 localized pages, 5-language SEO, schema/sitemap, G-series model status, rebuild survival, and CMS owner protections passed.
- The GitHub Actions Node.js / JS test gates and live Cloudflare publish **must still pass before declaring deployment complete**.
- Queue `_local_ops/phase2-remaining-sku-priority.csv` contains the **61 remaining** product IDs; 14 more source-backed candidates are prioritized without fabricated cap details.

## Release boundary
- Neither live D1 content nor R2 product images were overwritten by these copy updates.
- Production release requires committing all source/runtime/test/data files, successfully completing official GitHub Actions and verifying live `build-meta.json` plus sample updated SKU intros after publish.