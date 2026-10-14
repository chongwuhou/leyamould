# XUYI About source-of-truth rewrite — implementation notes (internal only)

Date: 2026-10-14. Owner-confirmed facts and owner-supplied profile structure. Not rendered in public website.

## Authoritative content source
- `data/about-company-en.json` is the owner-approved English copy (legal entity, Taizhou/Huangyan, own facility + specialized partner network, five approval gates, manufacturing and quality checks, clear buyer CTAs).
- `data/about-company-es.json`, `pt.json`, `ru.json`, and `tr.json` are corresponding human-authored localized content records; the same shared `about_company_page.py` renders all five languages.
- The shared renderer is integrated directly with `resource_pages.about_page`, `site_renderer.build_url` and `scripts/render_locales.py`. This is source/template rendering, NOT modification of finished dist pages.
- Old generic About page markup and the legacy `/about/` postbuild SEO overwrite were removed. About page title and meta description now come from source content (subject to later owner D1 changes).
- Existing D1 About body and SEO are compared with pre-rewrite hashes in `data/about-company-d1-baselines.json`. The approved baseline gets the new source copy. If the owner changes the body/SEO later, source code does not override it. A future locale with no reviewed translation remains owned by its submitted D1 content.
- `resource_pages.schema_add` adds legalName to the existing Organization/WebPage/BreadcrumbList JSON-LD. No foundingDate, staff count or facility capacity is invented.

## Image and URL red lines
- The four photo sources are existing factory / QA image slots: `/media/group/factory-bottle-packing.webp`, `/media/group/factory-final-pack.webp`, `/media/group/qa-color-box.webp`, `/media/group/factory-shipment.webp`.
- `assets/about-company.css` scopes the design to the About profile; `scripts/fix_primary_image_placements.py` no longer mutates About after rendering.
- Product URLs, canonical URLs, six company/brand homepage logos, product images and database fields are unchanged.
- CTAs: `/products/`, `/request-sample/`, `/contact/#inquiry`; workflow deep links: `/manufacturing/`, `/quality-control/`, localized to each approved language.

## Release gates
- `scripts/test_about_company_source.py` validates the five localizations, four photos, real legal name, SEO, JSON-LD, all CTAs, wording, source rendering and later D1 editorial override behavior.
- The old editorial and generic image tests now assert the user-requested company profile rather than expecting removed About blocks.
- 60/60 Python release tests, repeated clean build hashes, and GitHub Actions production deployment must pass before completion is claimed.

## Important operational note
- These are source-rendered updates to public output, not a direct write to the D1 admin form. The website keeps rendering the owner-approved source while the stored D1 About body matches its original baseline. Later explicit admin changes to the About body take precedence. If editing About from the admin UI, review the stored content prior to saving.