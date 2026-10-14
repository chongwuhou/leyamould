# 2026-10-14 — IndexNow, verified organization schema, llms.txt

## IndexNow — incremental, gated, secure
- The existing `scripts/search_submission.py` is now called by `.github/workflows/publish-xuyi.yml` after a successful Cloudflare Pages deploy **and** live source-revision check. Git pushes run the workflow; CMS publication revision changes are detected by the existing twice-hourly schedule (not instantaneous for CMS updates).
- Keep using the **one** official `https://api.indexnow.org/indexnow` POST endpoint which shares submissions with participating engines including Bing and Yandex. It does not notify Google.
- Before making any HTTP POST: check the public indexability gate, `robots.txt`, live `build-meta.json`, deployed version, project identity, and the root key file `/{XUYI_INDEXNOW_KEY}.txt`. Prefer a dedicated per-project GitHub Actions secret `XUYI_INDEXNOW_KEY`. If absent but the protected existing Cloudflare deployment token is configured, the workflow derives a stable 32-hex-character, domain-scoped verification key with HMAC-SHA256 (it masks the derived verification key in CI logs and never exposes the original credential). Token rotation changes the derived key, requiring IndexNow revalidation. If neither credential is configured, do not claim an accepted submission.
- The previous released `search-submission-manifest.json` is fetched prior to deployment. Submit only canonical URL HTML hashes that genuinely changed (including the current D1 Blog publish revision). Never ping all URLs merely because a previous manifest is missing. The protocol's HTTP 200/202 is receipt/acceptance, not guaranteed crawling, indexing or AI citations.
- Failure of IndexNow delivery is logged but cannot roll back a healthy site deployment. No new Workers or D1 write costs.

## Organization — source schema
- `organization_source_schema.py` enriches the existing Organization node in `site_renderer.py` (homepage) and `resource_pages.py` (About, FAQ). The source is shared automatically with four published localized pages and preserves user-selected verified contact/subject fields.
- `contactPoint`: sales department points to the real `/contact/` page. **No unverified telephone or email** has been fabricated.
- `knowsAbout`: ten supported topics on plastic drinkware, reusable sports bottles, kids bottles, jugs, shakers, OEM/ODM and logo printing.
- **No SearchAction markup**: the site has no real website-wide search result endpoint. In addition, Google stopped showing sitelinks-searchbox rich results in November 2024. Claiming a nonexistent search action would be inaccurate.

## llms.txt — source-generated
- `data/llms-verified-facts.json` owns the verified legal entity, Taizhou origin, plastic-only scope and substantial review date (stable, **not** the build timestamp).
- `scripts/verified_trust_technical_seo.py::build_llms` reads eight existing English FAQs from the canonical `data/faq-expanded.json`, includes brief fact-preserving answers plus the official FAQ source page, and skips questions that are no longer displayed in the published FAQ after an owner CMS update.
- This file is an optional navigation aid, not an API, indexing directive or guarantee that generative search engines will read or cite it.
- All source changes only, no direct `dist` or online HTML mutation as implementation, no fake materials/compliance/pricing/staffing numbers.