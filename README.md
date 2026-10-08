# XUYI Drinkware — B2B Static Frontend

Production branch: main; Cloudflare Pages: xuyi-drinkware-site; GitHub: chongwuhou/xuyi-drinkware-site.

## Scope
Kreat-inspired original navigation and UI system: homepage; 4 categories; 79 model pages; 5 capabilities subpages; About; Manufacturing; Quality Control; Shipping; FAQ; Blog; 6 buying guides; Contact; Privacy Policy and 404. All photos are from XUYI source catalogs.

## Technology
- GitHub -> Cloudflare Pages: static HTML/CSS/JS.
- R2 xuyi-drinkware-r2, binding XUYI_ASSETS, read-only media proxy /media/[kind]/[filename].
- D1 xuyi-drinkware-d1, binding XUYI_DB, published-only products API.
- KV xuyi-drinkware-kv reserved for site settings.
- Regenerate static HTML with: python build.py.
- Noindex/robots blocked until verification. Sitemap for preview only, not submitted to Google.

## Source
76 Excel catalog row-specific images served from R2 site-preview/excel/.
79 non-glass PPT catalog photos served from R2 catalog-staging/ppt/.
Never commit local source catalogs, _local_ops secrets or Wrangler credentials. Original Demalong resources remain untouched.

## Launch blockers
Verify SKU variants, 2506 anomalous capacity, official English legal name, company factory photography, product certificates, live email/WhatsApp and functional inquiry delivery, privacy/consent and local translations. No checkout.

## Responsive
Desktop, tablet and mobile templates, accessible mobile menu, mega menus, model search/filter and fixed mobile inquiry link. QA on 320–1440 px.
