# XUYI SKU Copy Uniqueness — Phase 5, 82 Models (2026-10-14)

## Scope
- Verified product catalog: 101 factory model routes, five locales, 505 product detail pages. The product directory index is not an extra SKU.
- Earlier phases: 68 models (340 localized product pages). This phase: 14 models × 5 locales = **70 pages**. Total: **82 models and 410 localized pages**. **19 models remain** for source verification or content work.
- Sports 10: 2470, 2400---, 2401---, 2212, 2400, 2099, 2100, 5299, 5340, 8563.
- Jugs 4: 2307---, 2306---, 2308---, 6252.
- Catalog-specific differences used: confirmed capacity in ml, assembled-body dimensions listed by source, material composition, reference colors, bag type, pieces per master carton and carton dimensions. No invented cap, straw, handle, certification, MOQ, inventory, compliance claim or exact-model photo substitutions.
- Explicit evidence limitations: **2099/2100 reuse the same reference gallery image**; **2306---/2307--- list identical dimensions/colors/materials/carton**, so do not assert different molds or lids. Source-confirmation instructions are embedded as buyer verification, not factually assumed distinctions.

## Canonical source ownership and files
- `data/phase5-next14-openings-{en,es,pt,ru,tr}.json`: 70 individual source-grounded buyer introductions, 100–150 whitespace-delimited words in each locale.
- `data/phase5-next14-locale-addenda.json`: locale-specific additional model-approval and source-check guidance.
- `data/phase5-next14-d1-baselines.json`: baseline SHA256 of existing D1 `mainHtml` for each model in ES/PT/RU/TR, scoped to this phase; only insert the reviewed introduction when the current CMS field still matches its original baseline. Any later owner edit keeps precedence.
- `sku_unique_openings_phase2.py`: formally merges the reviewed fifth batch upstream in the CMS-aware source renderer, retaining existing `sku_unique_openings.py` entry path. Not a dist HTML rewrite.
- `scripts/test_phase5_fourteen_unique_sku_openings.py`: five-language fact/length/route coverage, already-rendered idempotence, CMS owner-edit priority, future model growth and unique introduction tests; added to `.github/workflows/publish-xuyi.yml`.
- `scripts/prepare_product_copy_queue.py`: emits **19 remaining model rows** in `_local_ops/phase2-remaining-sku-priority.csv`; G-series verified factory model status retained. Holds for 2506 suspicious 60ml, shaker 5247/5248 same photo, and incomplete LO/G attributes. No fabricated source data.

## Quantitative audit, same metric as earlier phases
- Method: numeric-masked visible-product-body three-word-shingle Jaccard nearest neighbor among same-category peers within a locale. This is editorial diagnostics, *not* an exact duplicate-content Google penalty score.
- On the fixed 14-model × 5-locale sample, buyer-intro nearest-neighbor median **1.0000 → 0.0654**; whole-main visible copy nearest-neighbor median **0.9838 → 0.7758**.
- All edited English pages (82 models): closest-main median 0.769, closest-intro median 0.049; remaining English pages (19 models): closest-main median 0.969, closest-intro median 1.000.
- Five-language complete results `_local_ops/product-body-similarity-2026-10-14.json`; previous state `_local_ops/product-body-similarity-before-phase5-2026-10-14.json`.

## Validation gates
- **Two clean source-of-truth builds** passed, each outputting 973 files / 757 HTML / 505 model-detail routes / 755 sitemap URLs.
- Both builds produce identical SHA256 on **72 files**: home, sitemap and all 70 new localized product pages; no repeated copy insertion.
- **14/14 Python regression tests** passed, including existing first 68 SKU content, 5-locale metadata and hrefLang, link checker (zero broken internal links), SKU photo/sitemap checks, G-series identity preservation, real CMS edit simulation and new models.
- Cloudflare production D1/R2 original records, product photographs and inquiry data were not intentionally changed.
- Production release must pass GitHub Actions build and Cloudflare deployment + live revision verification to be declared complete. All CI/production claims should be verified against the actual new commit.