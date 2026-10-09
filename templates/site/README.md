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

The content/data variables live in `site_renderer.py`, `data/`, and D1 runtime settings. `{{NAV_DESKTOP}}`, `{{PRODUCT_LINKS}}`, and SVG placeholders are strictly replaced during build. Unknown/unfilled placeholders fail the build.

`python scripts/build_release.py` writes a clean `dist/` artifact. Do not deploy repository root. Do not manually edit generated `index.html` copies.

This is a XUYI-specific layout. Never import Demalong's filtration logos, contacts, catalog, database, or CI credentials.