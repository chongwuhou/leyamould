# XUYI Phase 13 — native LO8 and transparent alias2 H2 source upgrade

**Date:** 2026-10-15. New **10 factory catalog models × 5 locales** = **50 additional localized product detail pages** whose **Materials, Design, and FAQ** sections are now source-grounded. **Cumulative**: **90/101 product models = 450/505 localized details** with these three H2 modules. Do not confuse with already completed customized opening introductions for all 101 products.

## Eligibility and provenance

Two separate source catalog records with full factory nominal capacity, outline, materials, and packing:
- `2306透明款` → URL slug `2306---`, source **1600ml, 11.8×24cm, PC+PP+ABS**, transparent black/red/green/blue.
- `2308透明款` → URL slug `2308---`, source **2400ml, 12.3×24cm, PC+PP+ABS**, transparent black/red/green/blue.
These are distinct records from `2306` and `2308`; identical model family numbers do **not** establish a different cap or a shared mold. D1 already supplies translated mainHtml for four locales. Each one is guarded with its exact original D1 HTML section fingerprints and the factory source key is kept separate from slug.

Eight LO original catalog/photo records: `lo-001`–`lo-008`. LO is **not a full factory packing/BOM evidence set**. The source lists 2000ml for LO-001, 800ml for LO-002, 1300ml for LO-003/004/008, 1000ml for LO-005/006/007 and generic PC+PP families. Source dimensional figures are explicitly **approximate** and preserved as such in all five languages; color assortments shown in photos are not confirmed stock. **No carton count/box dimensions/approved body-lid-straw-seal map** were inferred for LO. LO-003/004/008 and LO-005/006/007 have near-identical source records, so purchasing copy specifically says there is **no verified lid/mold distinction** and requires two code-labeled physical samples when comparing.

LO source is `lo_catalog.detail(row, locale)` (native EN/ES/PT/RU/TR) because current D1 translated mainHtml has **no LO records**. DO NOT assume `product_content.details()` or D1 fields own LO by default. The live renderer injects source sections into native LO product body before markup emission, and whenever D1 supplies a future editor-owned LO section, the exact source hash mismatch **prevents overwritten content**. Two transparent aliases use English source `product_content.details()` plus D1 native-language content.

## Production source changes

- `data/product-10-module-source-baselines-phase13.json`: 10 SKU peer mappings and 50 locale/module individual source hashes from approved native LO source or English/D1 translated bodies. Materials, Design, and FAQ are applied from shared source render functions rather than altering built HTML.
- `data/sku10-phase13-focus-transparent.json`: two genuine model-to-model buyer decisions, individually reviewed in five languages, without claiming exact cap differences.
- `data/sku10-phase13-focus-lo.json`: eight LO code-specific buyer decision paragraphs each with EN/ES/PT/RU/TR natural wording, clearly stating unverified factory specs and physical sample requirements rather than fabricating differences to create copy.
- `sku_factual_sections.py` now includes `FIFTH10`, merges 90 distinct reviewed models, treats native LO `dimensions` as approximate with localized qualifier, translates LO color/packing *verification phrases* for five languages and retains source-verified material families. Existing 80 reviewed models unchanged.
- `scripts/test_phase13_lo8_alias2_h2_factual_owner.py` checks all **50 actual rebuilt outputs**, one source-backed Materials block, independent Design/FAQ module source hashes, editor replacement on a single module, a newly CMS-owned LO FAQ, other module independence, future products, exact visible 4×FAQ ↔ one FAQPage JSON-LD parity, and explicit holds for G/2506/5247/5248. CI workflow `.github/workflows/publish-xuyi.yml` includes it.

**No D1 writes, R2 image replacements, model identity edits, factory specification changes or post-generation HTML patches.** `AGENTS.md` and `PROJECT_CHANGE_POLICY.md` owner-first source rules followed.

## Phase 6 LO introduction compatibility, verified in Phase 13

Full historical phase6 LO native-body SHA fingerprints were no longer current, so their overly broad equality condition had silently prevented the **four localized LO buyer introductions** from applying to recent native source output. The phase13 release adds `data/phase13-lo8-native-intro-source-hashes.json` holding the exact current approved `lo_catalog.detail()` hashes for the 8×4 native LO locale pages. `sku_unique_openings_phase2.py` uses these **only when unchanged default LO native body** is present; later D1/editor changes still fail the hash guard, and are preserved. The older phase6 baseline file remains unchanged as history. `scripts/test_phase6_lo8_unique_sku_openings.py` now checks exact phase13-reviewed design/FAQ native source section fingerprints instead of rejecting all legitimate newer whole-page template versions, and explicitly verifies all **40 LO buyer intros** and owner-edit refusal. The original LO conditional customization notice has also been retained in all five locales: BPA-free materials and water at 100°C are **custom research/testing targets, NOT verified performance or standard existing PC+PP product properties**. The model must not be sold with these claims unless factory bills of materials and finished-product tests confirm them.

## 3-word shingle content audit — editorial diagnostic only

For each of the ten new products, compare its nearest peer in the **same category** among all 90 reviewed models within the same locale, with numbers masked. The original section is from native LO source or original D1 source; the new section is from a clean full build. Values are nearest-neighbor median across five locales (not Google penalties or ranking scores):

| Source module | Original | Current |
| --- | ---: | ---: |
| Design / Applications | 1.000 | **0.632–0.719** |
| FAQ | 1.000 | **0.620–0.679** |
| Materials | 1.000 | **0.859–0.941** |

The **high Materials similarity is real**, not a failed numeric mask. LO groups truly share the same approximate dimensions, combined PC+PP material family, and unknown packaging, so only model image/source provenance and buyer verification paths can be responsibly differentiated. Rewriting this to reduce a score would imply nonexistent distinctions; do **not** market it as unique chemistry or hardware.

Full diagnostic: `_local_ops/phase13-lo8-alias2-similarity.json` (internal only).

## Release quality

Full source build produces **973 files / 757 HTML / 505 model-locale detail pages / 755 sitemap URLs**. Two clean full builds must produce identical SHA256 for **453 files** (90×5 detail pages + home + sitemap + stylesheet). CI must run all historic source, locale, model, link, image, CMS, schema, material, and site validations; then Cloudflare production deploy and exact live revision check. IndexNow success indicates submission workflow success, **not a search-indexing guarantee**.

**Remaining 11:** eight G factory IDs with photos but no factory capacity/material dimensions, one `2506` anomaly and two shaker `5247/5248` ambiguous record/photo variants. See companion factory evidence request.
