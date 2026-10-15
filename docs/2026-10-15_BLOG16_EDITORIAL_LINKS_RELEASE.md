# XUYI 既有 16 篇博客正文内链整改 — 逐篇编辑验收

Date: 2026-10-15. **Scope is the 16 existing published buyer articles**, not a rule for future-only articles.

## Actual editorial change

Prior Phase14 `blog_source_product_bridges.py` inserted the same two model references in a standalone paragraph immediately after the lead. That does **not** satisfy the owner’s definition of naturally distributed in-body links. The old module is no longer called from either source renderer.

Two specifically written buying-decision sentences for **each** of 16 articles (32 unique paragraph placements) are in `data/blog-inline-edits-reviewed-part1.json` and `part2.json`, with natural EN/ES/PT/RU/TR wording. Each sentence is embedded **inside an existing different `blog-section` body paragraph**, linking to a distinct, confirmed real catalog model URL. No body/lid material, BPA, leak test, MOQ or model certification is inferred. The placements are hand selected to match the section heading and procurement decision, rather than rotated across paragraphs or counted from navigation.

The existing **three carefully selected related-guide entries** per article already reside in the canonical English `data/blog-guides.json` and native-language D1 `mainHtml`. Previously the generic `blog-related` section appeared **after the outer article closing tag**. This release relocates that same 3-item **source-owned** set **inside the article, at its actual end**, after the article’s inquiry CTA. It neither adds a duplicate set nor destroys the photo/title/link metadata. The new responsive CSS prevents the 3-card section from overflowing the narrower article column.

| Published blog slug | Product model references (distinct body paragraphs) |
| --- | --- |
| wholesale-plastic-water-bottle-buying-guide | 2095 / 2281 |
| plastic-bottle-material-selection | 2501 / 2095 |
| custom-logo-water-bottle-checklist | 2095 / 2501 |
| sports-bottle-vs-water-jug | 2514 / 2281 |
| kids-water-bottle-procurement | 2106 / 2350 |
| shaker-bottle-wholesale | 501 / 502 |
| tritan-vs-pp-petg-pc | 2501 / 2095 |
| bpa-free-plastic-water-bottle-sourcing | 2501 / 2095 |
| water-bottle-lid-leakproof-testing | 2501 / 2106 |
| custom-water-bottle-moq-pricing | 2095 / 2501 |
| oem-vs-odm-plastic-water-bottles | 2095 / 2281 |
| water-bottle-quality-control-checklist | 2501 / 2106 |
| custom-water-bottle-export-packaging | 2501 / 2281 |
| how-to-start-private-label-water-bottle-brand | 2095 / 2501 |
| water-bottle-logo-printing-methods | 2095 / 2501 |
| sports-water-bottle-customization | 2095 / 2501 |

**Editorial definition of completion**: 2 distinct genuine product links in 2 different relevant article body paragraphs **plus 3 topically selected related guide article links at the article end**, validated at article-scope, not from whole-page nav/cross-sell counts. Across five languages this gives **80 localized articles / 160 distributed model references / 240 end-of-article related links**. Existing extra internal links elsewhere are not counted.

## Field ownership / persistent rebuild correctness

- English article body is generated from `data/blog-guides.json` + the 16 reviewed annotations through **`blog_editorial.render_article()`**. If an English D1 admin body override exists, the owner’s copy takes precedence, not the old annotations.
- ES/PT/RU/TR article body is **D1 CMS-owned `mainHtml`**. `blog_editorial_inline.reviewed_localized_article()` applies edits in the locale source renderer **only when the unmodified original D1 HTML SHA256 matches its previously reviewed exact per-route/per-language baseline**. Any user-modified D1 body is untouched. Existing reviewed Turkish lid and Spanish wording corrections run before the final editorial annotation while comparing against the original D1 source for owner protection.
- The D1 CMS database, inquiries, hero images and R2 are not written. These edits exist in canonical reviewed source records / shared renderers, **not generated HTML replacement scripts**. A normal CMS rebuild reproduces them while original D1 baseline remains unchanged. When a CMS user edits that body later, the new version wins and should be manually rechecked against the editorial checklist.
- Historical `blog_source_product_bridges.py` remains only as a dormant module for comparison and review, not an active source renderer path. No new article outside this reviewed set is forced into the historical 16 count.

## Critical production route correction (after checking live English HTML)

The English public `/blog/<slug>/` URLs are **served dynamically from the D1 `xuyi_blog_posts.content_json` rows by `functions/blog/[[path]].js` / `functions/_shared/blog-cms.js`**, even after the local static English article builds have passed. On the earlier successful GitHub run #150, the English *static artifact* contained the revised paragraphs but the true English *public D1 route* still did not. This caused misleading local-green vs production-red testing. The four translations were rendered from D1 `mainHtml` through the source builder and appeared correctly.

The correct, durable implementation now imports the **same two versioned paragraph-specific editorial records** in the actual D1-aware Worker template. `reviewedBlogParagraphNote(post,section,index)` only supplies a note if the **D1 post intro, section heading and original paragraph** still match the approved source. An administrator editing a paragraph, changing the article introduction, or selecting a new article is never replaced. The normalized owner D1 body is neither mutated nor posted from CI.

The Worker also renders **the D1 owner's own selected `post.related` list** (up to three valid, unique published-guide slugs) inside the article ending after the quote CTA; selecting a different order or clearing related picks is honored. The old initial live D1 layout had no article-end related section. A separate new Node test `scripts/test_blog16_live_d1_render.mjs` covers all 16 actual Worker article pages and realistic owner edits in the dynamic route, and is mandatory in GitHub CI. Production final acceptance **must HTTP GET actual public English routes**, not infer them from a successfully built static file.

Run #151/#152 attempted protected D1 article writes but were blocked by HTTP 401 due mismatched admin authority. Those failed writes must never be reported as a production article update. This source-template solution avoids secret workarounds, keeps the correct D1 ownership, and survives Cloudflare rebuilds.

## Release acceptance

`scripts/test_16_blog_editorial_internal_links.py` checks each of the 80 actual built pages, the two in-paragraph links in different sections, exact real model and locale URLs, all 3 selected related articles within the article, and simulated changed CMS source. No whole-document anchor-count shortcut. The Phase14 image/Why Us test is updated to distinguish true article-level link acceptance. Permanent CI gate added to `.github/workflows/publish-xuyi.yml`.

Final production release requires two independent clean site builds, checksum comparison for all 80 article pages plus home/sitemap, all source/CMS/security/SEO regressions, a GitHub commit and successful Cloudflare Pages production deployment with exact live revision. IndexNow submission does not guarantee indexing.