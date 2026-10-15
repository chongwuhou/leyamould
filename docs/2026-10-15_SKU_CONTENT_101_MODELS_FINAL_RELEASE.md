# XUYI Phase 8 — Last Three Buyer Guides Complete; Factory Facts Still Pending
Review date: 2026-10-15

## Editorial completion is not factory specification verification

- Source catalog currently has **101 factory/model product routes in each of five languages = 505 actual localized product detail pages**. This release adds exact-code introductions for models **2506, 5247 and 5248** (3×5 = 15 pages). Together with previous reviewed 98-model content, **101 of 101 models have distinct source-stage buyer introductions**.
- This does **not** mean all 101 factory specifications or photos are individually authenticated. Model 2506 still has anomalous source data; models 5247 and 5248 still share the same catalog photo and combined-size specification. Their written buyer instructions explicitly identify these limitations and request proof; the data layer and product specifications retain existing uncertainty markings.
- The marketing copy does not describe unverified lids, mixing balls, gasket quality, BPA-free certificates, exact 5247/5248 size assignment, corrected 2506 capacity, availability or MOQ.

## Checked primary inputs (no guesswork)
- `data/products.json` entry for **2506** records *60 ml* with approximate **8.3×26.8 cm**, PC+PP+ABS, color references blue/green/black/brown, OPP bags, and 60 per 60×43×55 cm carton. Existing product UI already renders the capacity as **“To be confirmed (catalog discrepancy)”**, without assigning oz size class. The raw 60ml source value is an unverified discrepancy, not an established commercial capacity.
- `data/products.json` entries for **5247** and **5248** both include a merged **450 ml/700 ml** reference, PP, and source image `/media/ppt/slide-096.webp`. `data/gpt-reviewed-shaker-hd-20261013.json` explicitly approves the same source image group for **both model codes** as merchandising photography, **not** evidence of different model-specific specifications. Both options may exist but factory confirmation is required to assign a capacity, lid and mixing parts to an individual code.
- No original PPTX or standalone signed factory specification file was available in the current project workspace; product-identifier/photo mapping cannot be resolved from existing evidence alone.

## Formal source work and protection
- `data/phase8-last3-buyer-intros-{en,es,pt,ru,tr}.json`: 15 independent and clearly limited buyer introductions, **100–150 words each**; distinguish their documentation needs, not imaginary physical differences.
- `data/phase8-last3-d1-baselines.json`: four existing localized D1 `mainHtml` fingerprints per SKU (12 source-body hashes). If the administrator modifies a translated product body, **that owner change wins** and previous source fallback is not reinserted.
- `sku_unique_openings_phase2.py`: merges Phase 8 copy into the authoritative source renderer before final HTML generation, with newly included `shakers` category. Neither `dist`, live HTML nor D1/R2 was directly edited.
- `scripts/test_phase8_last3_source_discrepancy_guides.py`: 15 routes, correct model IDs/categories, consistent source facts, idempotence, CMS edit simulation, native introduction replacement, future SKU allowance, and explicit tests that a completely empty remaining editorial cohort/CSV is supported.
- `scripts/audit_product_body_similarity.py`: empty remaining cohort now yields a JSON `null` median instead of throwing `StatisticsError`. `scripts/prepare_product_copy_queue.py` produces a valid header-only CSV when the remaining editorial queue is empty; technical factory evidence remains separate in `data/phase8-factory-fact-verification-pending.json`.
- The new Phase 8 test runs as a mandatory gate in `.github/workflows/publish-xuyi.yml`. No fixed 101-SKU upper bound was introduced.

## Measured copy variation (diagnostic, not Google penalty score)
- Method unchanged: digit-masked, visible 3-word shingle Jaccard nearest-neighbor within same category and language. An editorial difference metric, **not** a ranking score or algorithmic penalty threshold.
- On the exact three models × five languages, opening paragraph median **0.7746 → 0.0220**. Full main-body nearest-neighbor median **0.9739 → 0.7391**.
- Among all 101 English models, the overall nearest main median is **0.763**, nearest intro **0.044**. Five-language edited group counts 101 each; remaining group counts **0** and medians are `null`, never synthetic zeros.
- Previous audit backup: `_local_ops/product-body-similarity-before-phase8-2026-10-15.json`. Current audit: `_local_ops/product-body-similarity-2026-10-14.json` (historical script filename).

## QA and release
- Two full source rebuilds passed: **973 output files**, **757 HTML pages**, **505 product detail pages** and **755 sitemap URLs**. Site home, sitemap and all fifteen Phase 8 localized pages: **17/17 SHA256 hashes identical** across builds.
- **17/17 core regression suite passed** before the audit/CSV empty-cohort fixes. The new Phase 8 regression explicitly tests the corrected empty-cohort helpers; run all CI gates again before production.
- No broken internal links; CMS body mutation, no double injection, future growth, existing photo references and multilingual SEO are checked.
- **Only after** GitHub Actions succeeds, Cloudflare Pages deploys and the online SHA matches the submitted commit is the release complete.

## Three genuinely outstanding factory-documentation requests
See `data/phase8-factory-fact-verification-pending.json` (version-controlled) for per-model source images, known discrepancies and full supplier evidence checklist. These three items remain **pending_factory**, even though all 101 model buyer introductions are now editorially distinct.