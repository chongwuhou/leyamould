# XUYI Phase 14 — Homepage image layout, blog product paths, buyer Why Us

**Date:** 2026-10-15. This release concerns **source templates and reviewed data only**, not post-build HTML patching, live D1 writes or R2 changes. CMS edits always win.

## Baseline facts from full source output

- The English homepage actually had **65 `img` tags and all 65 lacked `width`/`height` attributes**. Missing intrinsic dimensions are a CLS *risk*, not proof of a measured failing Core Web Vitals score. No unverified Lighthouse/field CLS metric is claimed.
- The 16 buyer blog articles were **not fully isolated**: each already linked 3–4 other posts via reviewed related-guides content. Several lacked direct real product links (and others had just one or two), so we **preserve** the existing related-article network and add naturally situated model links within the article intro rather than build a second duplicate 3-card recommendation list.
- English Why Us was about **394 visible words** in our extracted HTML (the audit estimated 387). The new version from the complete source build is **about 1,100 words**, including clear focused product scope, five approval gates, a compact six-row quality verification matrix, honest sourcing principles and specific model-sample enquiry CTA.

## Homepage source geometry (all five locales)

The source renderer now reserves each of the 65 home image elements; known intrinsic pixel width/height from the **actual local assets or exact Excel image catalog metadata** are in `data/home-image-intrinsic-sizes.json` (45 unique image URLs reviewed). Multiple usages yield more than 45 `img` elements.

- `home_source_image_geometry.py` supplies genuine integer `width`/`height` values for those confirmed local assets; it also uses **pre-approved replacement HD images** in `data/gpt-reviewed-shaker-hd-20261013.json` as provenance when the build is already approved to replace an old PPT image with a specific photographed HQ asset.
- A handful of R2-hosted original images have no verified pixel header available locally. They receive a **CSS-only `aspect-ratio:4/3` layout reservation**, not fabricated intrinsic dimensions.
- The shared `site_renderer.header()` now reserves the eight mega-menu/mobile navigation images that appear **outside** the page `<main>`. The English and localized home body source rendering likewise reserve actual image positions.
- Existing `home_intro_source_photo.py` now selects the previously approved wide marketing image **before source image geometry**, with exact source-slot/CMS protection. The old postbuilt `fix_primary_image_placements` call has been removed from `scripts/build_release.py` to prevent false stale width/height after the image URL changed.
- The reviewed homepage slide configuration on translated pages is finalized **before** the dimension helper runs, avoiding wrong ratios. The original R2 files and real SKU photos are untouched. Future unfamiliar CMS image URLs do **not** inherit outdated dimensions.

Layout reservations reduce the risk of unexpected layout shifts, but a real **Core Web Vitals CLS improvement still needs browser/lab + field measurement after deployment**. We do not claim a Lighthouse score without measuring it.

## Buyer-centric blog links instead of additional duplicated clusters

`data/blog-product-proof-source.json` maps **all 16 actual published articles** to two source-catalog model IDs that suit the buying decision described by the article. They are not randomly rotated keywords or nonexistent models. The source-stage module `blog_source_product_bridges.py` inserts a short evidence-qualification paragraph **after the article introduction**, before the real buying checklist. It includes context-specific wording in EN/ES/PT/RU/TR, routes to actual localized product pages, and avoids duplicating product links already in the body. It neither guesses model certifications/material assignment nor rewrites approved article copy.

For the four D1-managed translations of each blog, exact `mainHtml` source hashes are stored in the canonical JSON. If the CMS owner modifies the article, no historical bridge is injected. English owner-managed body overrides also block the module. A new article without a reviewed mapping is untouched; adding one is not constrained by an old blog count. The existing 3–4 manually reviewed related-guide links are preserved.

## Why Us: decision-oriented content rather than manufactured performance claims

`data/why-us-buyer-comparison-five-locales.json` contains additional real-world buyer evaluation guidance for all five languages, with no invented MOQ, production capacity, certificates, lab results, lead time or leak-proof guarantees. `why_us_source.py` renders a separate proof section before the existing CTA:

1. Focused reusable plastic drinkware product scope (sports, kids, jugs and shakers).
2. Five sequential gates: procurement brief, model/sample verification, customization sign-off, agreed test/inspection scope, export/document reconciliation.
3. Six-row quality matrix: model identity, individual material/components, capacity/size, cap sealing, branding/finish, packaging/export.
4. Honest supplier commitments, exact model sample/quote CTA.

The **English Why Us source is D1 owner-managed too**, unlike English product pages. Its addition is allowed only while the known published English D1 body matches the carefully reviewed original source hash. ES/PT/RU/TR use independent exact D1 source fingerprints. Later owner changes to the body skip any rewrite and remain live. Responsive spacing for the decision blocks and article prose is in `assets/site.css`, the actual common stylesheet.

## Quality gates

`scripts/test_home_blog_why_us_buyer_quality.py` is wired into the GitHub Actions publish workflow. It validates 5×65 home image layout reservations (confirmed pixel dimensions or CSS ratio), absence of stale image-hint guessing on changed CMS images, all 16×5 blog article bridges with at least 2 actual model links and previously approved related reading, valid localized product destinations, independent CMS article edit preservation, source idempotence, future article growth, all five About/Why Us locale body modules, English Why Us ≥800 visible words, and 6-row QC matrix. Historical image placement, SEO, owner policy, locale, all 101 SKUs, 505 five-locale product pages, images, inquiry and full site tests must still pass.

The standard builder generates **973 release assets / 757 HTML files / 755 sitemap URLs**, and two independent clean source builds should yield matching file hashes for 5 home pages + 80 article details + 5 Why Us pages + 5 Blog listings + sitemap + stylesheet, plus representative 5-locale product details. GitHub CI production head SHA must match the verified deployed live revision. IndexNow submission does not guarantee indexing.
