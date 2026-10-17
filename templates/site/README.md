# XUYI shared templates (ported from Demalong V1.4 structure)

These are the only sources for the shared structural shell. The production output is pre-rendered HTML, NOT JavaScript-based client-side assembly.

| File | Responsibility |
| --- | --- |
| shell.html | HTML shell and assembly of generated head/body/partials |
| header.html | Shared header, navigation positions, responsive menu, search |
| footer.html | Shared CTA/footer structure; products come from category data |
| sidebar.html | Shared inquiry/email/WhatsApp/back-to-top rail |
| home.html | Homepage section placement |
| listing.html | Catalog/listing section placement |
| content.html | Product/Blog detail section placement |
| static.html | Company/capability content placement |
| product-card.html | Shared model card fields and semantic markup |
| category-card.html | Shared category card fields and semantic markup |
| head.html | Shared page HEAD, robots, metadata, favicon and JS/CSS references |
| contact-form.html | Single English inquiry form structure and field names |
| section-heading.html | Shared heading/eyebrow/description for common sections |
| process-step.html | Shared numbered buying/manufacturing process steps |
| product-overview.html | Shared product detail gallery, properties and CTA for old/new single products |
| product-benefit.html | Reusable benefit/feature card across catalog, home, details and services |
| product-spec.html / product-thumbnails.html | Structured spec table and image thumbnail markup |
| catalog-filter.html / catalog-pagination.html | Shared listing controls |
| page-intro.html / faq-list.html | Shared hero intro and FAQ markup |

The four-column nav defaults now live in `data/site-navigation-defaults.json` (shared by desktop and mobile), with live D1 navigation settings layered on top. Single new products use `catalog_extensions.py`, the existing product templates, and D1 status review. Do not copy a product HTML page to create a new SKU.

The content/data variables live in `site_renderer.py`, `data/`, and D1 runtime settings. `{{NAV_DESKTOP}}`, `{{PRODUCT_LINKS}}`, and SVG placeholders are strictly replaced during build. Unknown/unfilled placeholders fail the build.

`python scripts/build_release.py` writes a clean `dist/` artifact. Do not deploy repository root. Do not manually edit generated `index.html` copies.

This is a XUYI-specific layout. Never import Demalong's filtration logos, contacts, catalog, database, or CI credentials.
