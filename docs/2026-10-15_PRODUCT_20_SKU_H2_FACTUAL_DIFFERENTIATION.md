# XUYI Phase 9 — source-level SKU Materials, Design and FAQ differentiation

**Date:** 2026-10-15 · **Scope:** 20 real models × five languages = 100 product-detail pages. Product index pages are **not** separate model routes; the site currently contains 101 models × 5 languages = 505 actual product-detail pages, alongside 757 HTML documents in the full site.

## Evidence reviewed and deliberate constraints

The user correctly identified remaining boilerplate in the product page's H2 sections. Earlier work differentiated H1-adjacent introductions, **not** the complete product body. This release makes the first **five models per collection** source-backed:
- Sports: 2095, 2099, 2100, 2501, 2511.
- Kids: 2106, 2108, 2319, 2408, 2410.
- Large jugs: 2280, 2290, 2281, 2302, 6252.
- Plastic shakers: 501, 502, 507, 509, 510.

Each of these 20 has three addressed H2 modules: **Materials and practical use; Design, Materials & Applications; Frequently Asked Questions**. The common OEM ordering process, related products, and general custom Tritan/BPA-free inquiry information remain deliberately shared.

Source facts are read from the CMS-aware authoritative `site_renderer.SERIES` values based on `data/products.json` and current approved source overrides: nominal ml capacity, catalog dimensions, material family list, existing color descriptions, unit packing and real carton figures where recorded. Shaker dimensions come only from the source-printed product-size field. Independently reviewed buyer angles in five languages explain *why a particular model should be compared with a named same-category model* using measured catalog differences. This does **not** verify component-level materials (body/lid/straw/gasket), factory cap types, BPA status, test certifications, fit of cupholders, usable volume, exact shade availability or MOQ. The user-supplied sample draft makes some additional lifestyle claims and individual component associations beyond the evidence; such claims were **not** copied without verification.

## Formal shared-source changes, not dist patches

- `data/product-20-module-source-baselines.json` records the precise source **Design and FAQ section fingerprints** for each SKU×locale. Fingerprints are based on the approved English template and native D1 localized source fields, and are checked separately for each module. If a later administrator changes one section, that entire section remains untouched; an unchanged neighboring section may still receive the approved improvement.
- `data/sku20-focus-{sports,kids,jugs,shakers}.json` are editorial model-specific, five-language comparisons grounded in the named catalog features. They are not random text rotation.
- `sku_factual_sections.py` contains reusable production-source renderers for model facts, local material evidence, translated design cards and **four visible SKU-specific FAQs**. Values are computed from the current authoritative model record at build time, not frozen old catalog values. Unknown input fields explicitly remain unverified. Applied modules are idempotent.
- `site_renderer.py` enriches only English default source product sections; **any English D1 BODY_OVERRIDE wins**.
- `scripts/render_locales.py` enriches approved D1/localized product body sections **before final output**, using each module's own baseline and preserving owner-modified source sections.
- `product_material_performance.py` uses a compact source-backed Materials card only for the selected 20, instead of the nearly identical generic polymer-trait block. The other 81 retain their original module. It still links to the material guide and exact model inquiry form.
- `assets/site.css` adds minimal responsive styles for the reviewed model evidence and design notes, retaining the existing palette and layout.
- `seo_structured_components.py` already derives **FAQPage JSON-LD from the visible questions and answers at source-render time**, so no schema hardcoding or post-render FAQ JSON edit was introduced. All 100 localized targeted pages were confirmed to have **exactly one FAQPage object** matching all four on-page FAQ answers in both text and order.
- `scripts/test_20_product_modules_and_faq_schema.py` is a mandatory GitHub Actions gate in `.github/workflows/publish-xuyi.yml`. It exercises 100 actual output pages, original versus updated section fingerprints, per-section owner mutations, source catalog consistency, repeated render stability, future model growth, visual material block persistence, schema parity and an explicitly owner-edited FAQ and Materials scenario.

## Similarity evidence on a fixed, comparable cohort

Use a **three-word shingle Jaccard nearest neighbor, numeric masking, restricted to five peers within the same collection and language**. This is an editorial diagnostic—not Google's algorithm, a penalty prediction, or a "safe SEO score". The initial Design and FAQ values come from the original upstream English template and actual localized D1 source fields, not reconstructed HTML; post-change scores come from the final rebuilt product pages.

| Reviewed module | Earlier nearest median | Updated nearest median across EN/ES/PT/RU/TR |
|---|---:|---:|
| Design / Materials / Applications | 1.000 | 0.588–0.626 |
| FAQ | 0.909–1.000 | 0.576–0.605 |
| Materials / practical use | Largely shared generic material copy; initial site analysis rated ~0.99 | 0.713–0.758 |

The Materials card retains an intentionally common safety disclosure about unknown component assignment and conditional market-specific testing. We **do not** seek arbitrary low similarity by fabricating differences or randomizing phrasing. In particular, two products can truthfully use the same PP+PC family while having different size, palette or packaging records.

## Release quality requirements

- No D1 write, R2 upload, image swap, product record override or customer inquiry change.
- Two clean full builds and SHA256 equivalence for 103 representative outputs (100 target product pages + homepage + sitemap + CSS).
- `scripts/test_20_product_modules_and_faq_schema.py`, all existing multilingual/body/source/material/schema/link tests, and GitHub's full release gate must pass.
- Publish only after GitHub Actions successful commit build, Cloudflare Pages production deployment, exact live revision verification and applicable search notification results. An outstanding cloud step means **not yet released**.
- This is a first batch of 20 SKU models/100 localized pages, **not** a claim that all 101 models' three H2 sections have been uniquely rewritten. Additional verified models can use the same source renderer after independent source review without requiring a fixed total count.
