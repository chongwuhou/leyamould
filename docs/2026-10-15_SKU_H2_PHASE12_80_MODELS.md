# XUYI Phase 12 — four H2 editorial cohorts, 80 of 101 factory product records

Date: **2026-10-15**. Fourth H2 round adds **20 model records × 5 locales × 3 source modules = 300 localized Materials/Design/FAQ blocks**. After four rounds, **80/101 true catalog products, or 400/505 product-language pages**, have source-grounded H2 differentiation. All 101 already have individualized opening introductions from preceding releases; do **not** confuse intros with all H2 blocks being unique.

## Source selection and the special model-key/page-slug distinction

Phase 12 reviewed these **20** authentic factory source records:
- **Sports (17):** 2502, 2505, 2507, 2515, 2516, 2517, 2470, 2212, 2400, 2407, 2405, 2310, 5299, 5340, 8563, **2400透明款 → /products/2400---/**, **2401透明款 → /products/2401---/**.
- **Kids (2):** 2350, 2487.
- **Jugs (1):** **2307透明款 → /products/2307---/**.

`site_renderer.SERIES` is keyed by the factory model, **not always page slug**. The three suffix-bearing transparent records have a distinct source model key, production page slug and approved localized D1 `mainHtml`. At the renderer boundary we preserve their slug identity while displaying a localized human-readable **“transparent variant”** label in the new SKU FAQ and Materials/Design comparisons. All comparison peers resolve by the **actual source model key**, while the template and CMS baselines use the **page slug**. In particular, factory row `2307透明款` claims **1600ml**, while the separate ordinary `2307` has a **different catalog nominal capacity**: never merge them or present shared caps/molds as fact. User-selected and previously verified images are untouched.

Original source `capacity`, `dimensions`, `material`, `colors`, `packing`, `carton_quantity`, `carton_size` were each verified for all 20, including separate snapshots in **all five languages**. The 17 regular rows have individual source capacities and packing; the other three transparent rows have the same type of source evidence under distinct keys. No inferred body/lid/gasket polymer, child-age rating, food-contact certificate, BPA-free certification, leakproof guarantee, available inventory, MOQ, or confirmed interchangeable parts was introduced. `2310` records a rubber-coated component but not its physical assignment; copy requires a real component drawing instead of claiming a soft-touch handle.

## Changes at upstream source, with D1/CMS authority

- `data/product-20-module-source-baselines-phase12.json`: 20 model comparisons and **100 exact localized source section baselines**, each with separately hashed **Design** and **FAQ** source markup. These are reviewed against `product_content.details()` for EN and localized D1 `mainHtml` for ES/PT/RU/TR. A changed owner paragraph/section bypasses that module individually and is never forced back to historical copy.
- `data/sku20-phase12-focus-sports-{a,b,c}.json`, `data/sku20-phase12-focus-kids.json`, `data/sku20-phase12-focus-jugs.json`: 20 unique sourcing decision notes × five natural-language variants, with actual catalog comparisons. We did **not** simply rotate 3–4 generic paragraphs.
- `sku_factual_sections.py`: merges `FOURTH20` into the prior 60 cohorts for the same reusable source renderers. Both exact identity (source factory model for peer lookups versus URL slug for D1 source owner and `data-sku-focus`) and language-specific “transparent variant” labeling are preserved. Also repairs an old English “equal than” materials-line grammar defect: the reviewed comparison now says “Catalog nominal capacity compared with …: equal/lower/higher”.
- `scripts/test_phase12_fourth20_alias_aware_h2_sections.py`: 100 rendered pages, unique source-staged updates, CMS editor overwrite simulation per independent section, idempotence, unaffected factory hold `2506`, exact source material references, visible 4-item FAQ / single FAQPage JSON-LD answer parity and special source alias-capacity mismatch regression.
- Historic Phase 9/10/11 tests used `2407` as a sample non-curated product. This model **is now curated**, so those three tests correctly use source-held model `2506` as their untouched sample. The tests continue to verify future new SKU growth and no forced injection.
- `.github/workflows/publish-xuyi.yml`: new Phase 12 source/regression test required for every release. No post-built `dist/**/*.html` mutation or production D1/R2 writes.

## Similarity measurements, qualified

Method: numeric-masked 3-word shingle Jaccard from extracted visible H2 content. For each one of **20** newly reviewed SKUs × five languages, the nearest-neighbor comparison includes **all other 79 currently curated same-category model pages**. The *before* sources are untouched original English/D1 modules and reconstructed generic Materials template, and *after* from the full clean source build. Diagnostic only; **not a Google duplicate-content penalty rule, indexation promise or ranking threshold**.

| H2 module | Before, five-language median | After, five-language median |
|---|---:|---:|
| Design, Materials & Applications | 1.000 | **0.612–0.678** |
| Frequently Asked Questions | 0.978–1.000 | **0.593–0.648** |
| Materials and practical use | 1.000 | **0.733–0.799** |

The Materials module properly retains a common legal/safety-oriented disclaimer that the factory catalog lists material **families** but does not prove component assignment or destination market test documents. Some legitimately identical dimension/capacity records will remain closer than others; do not invent product features for a lower similarity score. The detailed audit JSON is saved locally in `_local_ops/phase12-fourth20-80peer-H2-similarity.json`.

## QA and production release checklist

1. Two complete standard source builds (`python -B scripts/build_release.py`), each generates 973 artifacts, 757 HTML documents including 505 true five-language product pages and 755 sitemap URLs.
2. SHA256 equality for **403** selected outputs: all **400** reviewed H2 product-locale pages, homepage, sitemap and site CSS. Exact page hashes must match across both clean rebuilds.
3. Full source/CMS/SEO/product-material/image/sitemap/canonical/hreflang/release/visible FAQ JSON-LD regression suite plus unchanged prior 60 H2 models.
4. GitHub Actions success on exact commit, actual Cloudflare Pages production deploy, exact live revision validation and applicable IndexNow result. Do not claim live before the run passes.

## Remaining 21 models requiring independent review

After this round exactly **21/101** products retain generic H2 source modules: **8 LO-*** provenance/sizing review records, **8 genuine G-*** factory models whose exact capacities and component materials remain to confirm, **two additional transparent aliases 2306透明款/2308透明款** (slugs `2306---`, `2308---`) requiring matched source/visual comparison, and **three factory-spec holds 2506, 5247, 5248**. These groups already have earlier model-intro copy. It is more accurate to preserve their technical uncertainty than force a claim of 101/101 fact-checked H2 coverage.
