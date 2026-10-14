# XUYI source-photo LO series differentiation — Phase 6 (2026-10-15)

## Verified scope
- **8 factory-catalog LO models × 5 locales = 40 product detail pages**: lo-001 through lo-008.
- Prior 82 distinct introductions → **90 of 101 SKU routes and 450 of 505 locale pages** covered. The remaining **11** lack enough independent verified factory specifications to satisfy the same standard.
- Source evidence: user-supplied LO-水杯1 through LO-水杯8 original parameter-photo panels, persisted in `data/lo-products.json`, `lo_catalog.py` and `assets/lo/`. Each model has three source photographs, two detail panels, source-listed ml capacity and approximate dimensions, PC + PP combined material families, and a source-backed distinguishing presentation in the existing title.
- 2000 ml handled gradient lo-001; clear 800 ml carry-loop lo-002; 1300 ml handled gradient compact lo-003; illustrated transparent handled compact lo-004; 1000 ml gradient with time markings lo-005; transparent with time markings lo-006; flip-top with time markings lo-007; 1300 ml gradient compact with carrying strap lo-008.
- **Caution:** photo-backed styling names describe the catalog variant, not performance tests, child safety, current color inventory, finished-product material certification, leakproof ratings, tooling interchangeability or exact packing counts. Dimensions are approximate as originally sourced.

## Correct source ownership (important LO distinction)
- English LO body originates in `lo_catalog.detail` via the canonical `site_renderer.py` / `build.py` source renderer, unless an English D1/CMS body override exists.
- In ES/PT/RU/TR the LO source has native-language product content in `lo_catalog.detail`. It is used **only where a reviewed D1 translation does not exist**. `scripts/render_locales.py` already gives any D1 translation precedence.
- Unlike earlier D1-owned SKU batches, original LO translated bodies have **no D1 `mainHtml` source**. The new frozen fingerprint file hashes the exact approved native locale source template instead of pretending the data is from D1. Any later CMS-managed replacement with a different body hash wins.
- New source-of-truth files: `data/phase6-lo8-openings-{en,es,pt,ru,tr}.json` (40 independent, 100–150-word introductions), `data/phase6-lo8-locale-addenda.json`, and `data/phase6-lo8-template-baselines.json`.
- Shared source renderer `sku_unique_openings_phase2.py` merges these before final HTML generation through `sku_unique_openings.editor_intro`; this remains the existing template/CMS-aware entrypoint. No production edits were made to `dist`, Cloudflare D1 or R2.
- Reviewed model identifiers are case-fold matched in the editorial validator because the source model display is `LO-001` while its URL slug is `lo-001`, without weakening the actual SKU-specific check.
- New `scripts/test_phase6_lo8_unique_sku_openings.py` checks 8×5 finished pages, native source-template fingerprints for four locales, category, exact introduction text, length, idempotence, simulated owner update precedence, and tolerance for additional future LO SKUs. Added to `.github/workflows/publish-xuyi.yml`.
- Older D1-specific `scripts/test_phase2_six_unique_sku_openings.py` is now scoped to its D1-owned products; it no longer misinterprets LO native-source pages as absent D1 records. Both independent coverage gates are required for release.

## Measured duplicate-content improvement
- Same numeric-masked visible-content three-token-shingle Jaccard nearest-neighbor method as prior phases; editorial diagnostic, **not a Google penalty/ranking threshold**.
- Fixed LO 8×5 sample: initial intro nearest-neighbor median **1.0000**, after **0.0421**; visible main body median **0.9812 → 0.6488**.
- All edited English 90-model pages: main median **0.768**, intro median **0.047**. Remaining 11 English pages: main median **0.961**, intro median **1.000**.
- Complete five-language report: `_local_ops/product-body-similarity-2026-10-14.json`; prior state backup: `_local_ops/product-body-similarity-before-phase6-2026-10-15.json`.

## Quality checks
- Two full clean source builds completed, each producing **973 files, 757 HTML, 505 five-locale product detail pages and 755 sitemap URLs**.
- Home, sitemap, eight models × five locales: **42 generated files identical SHA256 between builds**.
- **15/15 project Python smoke/regression tests** including source-of-truth, all historical cohorts, LO-native translations, CMS owner-priority, sitemap/hreflang, 505 product metadata, links (0 broken), and G-series factory identity passed.
- Original product photos, D1 records, R2 objects, inquiry submissions and unrelated site UI were not modified.
- GitHub CI plus Cloudflare Pages deployment **must finish successfully** and verify its exact deployed SHA to count as published.

## Remaining 11: evidence-first, do not invent
- **8 true factory G-series models:** g-01, g-02, g-03, g-04, g-05, g-09, g-10, g-12. Product photos exist, but no per-SKU verified capacity, physical dimensions, material breakdown or packing data. Obtain exact specification panels, model/photo association and factory sample confirmation before writing technical advantages. Keep each G code labeled as a factory model.
- **2506:** source capacity field says 60 ml but its nominal dimensions 8.3×26.8 cm make this record suspect. Factory must confirm authentic ml capacity before any product-size class, conversion or capacity-driven sales text.
- **5247 and 5248 plastic shaker models:** both currently reference `/media/ppt/slide-096.webp` and a combined 450/700 ml source specification. Ask factory for separate clearly labeled SKU photos, capacity-to-model mapping, and independently confirmed closure/strainer/mixing components to avoid made-up product differences.
- New current source-coverage queue: `_local_ops/phase2-remaining-sku-priority.csv` (11 rows). Do not publish unique-sounding but evidence-free text just to claim full completion.