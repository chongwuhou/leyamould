# XUYI Phase 11 — sixty models with source-grounded SKU H2 modules

**Date:** 2026-10-15. **Batch:** another 20 real catalog models, **100 five-language product pages** (EN/ES/PT/RU/TR). **Cumulative three-phase H2 coverage:** 60/101 real models = 300/505 localized product-detail pages. This is **not** a claim that all 101 have distinctive Materials/Design/FAQ: 41 remain on the old H2 templates, although all 101 have model-differentiated introductions from prior phases.

## Reviewed source models and scope

- Sports ×8: **2401, 2403, 2406, 2309, 2458, 2459, 2311, 2312**
- Kids ×6: **2317, 2318, 2315, 2316, 2412, 2411**
- Large jugs ×6: **2282, 2306, 2303, 2417, 2418, 2419**

These are **actual `site_renderer.SERIES` model keys whose production page slugs match**, each with a verified catalog record and locale-specific D1 body. During source review other transparent-variant items were found with product key `2307透明款` and slug `2307---`, etc. They were excluded from this batch because the generic `SERIES[slug]` lookup would confuse model keys and page slugs. This is an explicit next-stage identity-mapping investigation, not a reason to silently associate incorrect pages.

**All authored claims follow the real source**: catalog capacities, dimensions, material family lists (not per-component plastics), recorded gradients/colors, unit packing and master-carton quantities/dimensions. Exact factory materials for body/lid/straw/seal, tested leakproof claims, children's age conformity, BPA-free certification, interchangeable lids, exact decorations, production stock, and MOQs are not asserted. When two source records share every recorded spec (e.g. **2282 vs 2292**, **2316 vs 2318**), the buying text explicitly states **no proven mold/cap difference** and asks for separately labeled finished samples and factory documentation.

## Source ownership and implementation

1. `data/product-20-module-source-baselines-phase11.json` — 20 model-to-model comparison selections and 20×5 approved **Design/FAQ section source fingerprints**, derived from original English `product_content.details()` and existing D1 translated `mainHtml`. They are individual per-section guards rather than a brittle whole-body fingerprint.
2. `data/sku20-phase11-focus-{sports,kids,jugs}.json` — reviewed, distinctive, natural-language supplier decision notes in **five languages for each SKU**, addressing measurable difference or explicitly unverified physical difference. Not automatic text spinning.
3. `sku_factual_sections.py` — joins `FIRST20`, `NEXT20` and `THIRD20` into `PEERS` and independently protected `BASE` and `FOCUS`. This is one reusable renderer: the earlier 40 SKU cohorts remain unchanged and supported, while the third 20 use current CMS-aware product data. Future approved products are not frozen to an absolute site total.
4. `product_material_performance.py` automatically applies the existing source-backed compact Materials buying cards to the now 60 reviewed models; the remaining models keep the prior material section. The old product ordering, related items and conditional Tritan/BPA-free options remain shared.
5. `scripts/test_phase11_third20_sku_h2_sections.py` — new 100-page test for both altered sections, four SKU-specific visible FAQ per locale, exactly one FAQPage schema object with full question+answer parity, CMS owner module changes, independently updated D1 content, repeated injections, source material facts, and future/unselected SKU cases. Added to `.github/workflows/publish-xuyi.yml`.

**No direct D1, R2 or production HTML edits.** All content changes are made in official site templates/source before the builder generates HTML. Owner changes to the touched D1 section are authoritative; further unrelated CMS changes are not suppressed.

## Similarity audit (editorial diagnostic, not Google safe threshold)

Fixed third-cohort model list, same category, same language, nearest-neighbor three-word shingle Jaccard after number masking. The baseline is from original native English/D1 Design and FAQ source modules and from the default generic Materials renderer. The final score uses the newly built output sections.

| H2 section | Prior five-locale median range | New five-locale median range |
| --- | ---: | ---: |
| Design, Materials & Applications | 1.000 | **0.600–0.681** |
| Frequently Asked Questions | 0.959–1.000 | **0.587–0.644** |
| Materials and practical use | 1.000 | **0.772–0.796** |

`_local_ops/phase11-next20-similarity.json` holds all 15 diagnostic rows. The shared evidence disclaimer in Materials legitimately remains somewhat similar, and **we do not invent new polymer assignments to artificially lower this diagnostic score**.

## QA / release gate

- The full source builder regenerates 101×5=505 detail pages, 757 HTML pages, 973 files and 755 sitemap URLs.
- Repeat **two clean full builds**. Compare SHA256 of 300 selected H2 model-language page routes plus homepage, sitemap and site CSS = **303 files**.
- Run all core release, SEO, localization, old phase H2, new phase H2, image, schema, material, and owner-policy regressions.
- Declare production complete only when a new GitHub Actions run for the exact commit passes source build, Cloudflare production deploy, live revision match and release gates.

## Remaining work

After this batch: **41 / 101 SKUs** retain generic H2 sections. These include records with special model-key/slug aliases, native gallery templates with no verified capacities, LO records that require separate source checks, and factory-data holds **2506**, **5247**, **5248**. Reassess each group independently; never infer precise capacities, component materials, certifications or true mold differences from mixed catalog rows.