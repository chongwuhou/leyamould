# XUYI three-route search intent ownership — 2026-10-14

The owner directed that three pre-existing URLs should no longer compete for the same sports-water-bottle search intent.

| Page | Intent role | English title |
|---|---|---|
| `/` | Factory/manufacturer, multi-category brand, OEM/ODM | `Custom Plastic Drinkware Manufacturer & OEM \| XUYI` |
| `/collections/sports-water-bottles/` | Wholesale purchase / custom OEM quotes / real SKU listings | `Wholesale Sports Water Bottles & Custom OEM \| XUYI` |
| `/blog/sports-water-bottle-customization/` | How-to education: cap, size and logo selection | `How to Customize Sports Water Bottles: A Guide \| XUYI` |

SEO/title/description/H1 entries for English, Spanish, Portuguese, Russian and Turkish live in `data/search-intent-three-landing-roles.json`. Source pre-output renderers `site_renderer.py` and `scripts/render_locales.py` call `search_intent_roles.py` after D1 fields are merged. Exact original title and description must both match before curated metadata is applied. Owner alterations to either field leave the pair unchanged, and a manually written H1 is always respected.

Former `collections/sports-water-bottles` post-generated HTML description changes have been removed from `scripts/curated_buyer_seo_round2.py`; the other three collection descriptions are pre-existing technical debt, untouched in this task.

The English D1 dynamic article endpoint uses `functions/blog/[[path]].js::withInformationalIntent` using the very same reviewed source, with unchanged original D1 blog records and owner-edited titles/descriptions preserved. The static article still links to the transactional sports collection. No route, canonical, hreflang, product, customer brand logo, original photo, or inquiry table changes are part of this work.

Regression gates: `scripts/test_search_intent_three_routes.py` (15 static pages, JSON-LD, CMS updates, repeatability), `scripts/test_blog_search_intent_runtime.mjs` (D1 published Blog and owner edits), two complete clean builds, full publishing workflow.
