# XUYI 16 buyer guides — externally researched source release

Date: 2026-10-14. Owner rule: edit only shared templates, canonical JSON and D1-aware renderers; do not patch dist HTML.

## Scope completed in canonical sources

- 15 individual guides have six dedicated substantive paragraphs each (no common interchangeable filler), plus individually reviewed comparison tables already maintained in the canonical source.
- Source data lives in data/blog-deep-research-part1.json, part2.json and part3.json. The previously completed six-section material guide remains in data/blog-depth-evidence-en.json.
- These fifteen guides include 43 topic-matched links to authoritative regulatory, standards, intellectual property, material-supplier and shipping sources, including FDA, European Commission/EUR-Lex, CPSC, ISO 2859-1:2026, ICC, ISTA, ECHA, FTC and USPTO.
- Every expanded English article is rendered via blog_editorial.py at original template-time and functions/_shared/blog-cms.js at Cloudflare's D1 dynamic blog runtime, with source-specific heading and visible reference bibliography.
- Live D1 introductory copy for all 16 articles matched the canonical source before this release. A subsequent operator-edited article introduction or explicit depthEvidence:false suppresses the source extension rather than reverting the editor's content.
- The original factory data and product source URL paths remain unchanged, as do the six existing homepage logo marks and the G-series factory-model identity.

## G-series material capability

- All eight existing G-series source models and future matching G-xx/xxx factory codes share a translated material-options component in g_series_material_options.py, used directly by site_renderer.py and scripts/render_locales.py. The component names custom PP, PC, PETG, Tritan copolyester, PE and ABS options where suitable to the part, rather than claiming any unverified present stock resin or product certification.
- product_content.py displays a corresponding buyer-facing material-option specification on genuine G-series product source pages, guarded by the original D1 body precedence.
- Existing G-series capacity and real exact component material are still unverified and must not be guessed or inferred from unrelated SKUs.

## Quality / delivery conditions

- Primary-source references teach market obligations; they do not establish XUYI factory certificates, actual output, MOQ figures, customer contracts, or delivery guarantees.
- No German/French/Arabic new pages have been fabricated; the original reviewed Spanish/Portuguese/Russian/Turkish body copy is preserved and the G material module has reviewed translations.
- Site editorial source full-page count target is 1,800–2,500 English words per existing guide without templated filler. Proof is obtained by counting real generated article pages, not only new JSON paragraphs.
- Source gates include scripts/test_researched_blog_depth_g_series.py and scripts/test_researched_blog_depth_runtime.mjs, CMS override tests, duplicate module checks, source links, full clean builds and GitHub Actions deployment verification.

## Unverified claims specifically prohibited

Do not invent a fixed factory MOQ, sample lead time, shipment lead time, exact grade on unknown G models, bulk food-contact certification, 'FDA approved products', 'leakproof' certification, true-person blog identity or direct well-known brand customer status.
