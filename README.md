# XUYI Drinkware — B2B Static Frontend

Production branch: main; Cloudflare Pages: xuyi-drinkware-site; GitHub: chongwuhou/xuyi-drinkware-site.

## Scope
Kreat-inspired original navigation and UI system: homepage; 4 product categories; 79 model pages; 7 capabilities subpages; About; Manufacturing; Quality Control; Shipping; FAQ; Blog; 6 buying guides; Contact; Privacy Policy and 404. All photos are from XUYI source catalogs.

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

## Target-style UI revision (October 8 2026)
- Main navigation: Home, Products (4-column photo mega menu), Capabilities (compact list), About, Why Us (compact list), Blog, Contact Us, Instant Quote.
- Products menu images: XUYI-owned R2 images in every menu column, not KREAT assets.
- Fully functional 3-slide hero and category tabbed model display; link + keyboard responsive test.
- Added 5 bottle feature landings, 5 use-case landings, Request Sample process, Why Us, Custom Water Bottle and Custom Molding pages; English only, no glass or stainless steel.
- Inspiration: Kreat visual/nav hierarchy, GOX model-category discovery, Everich sample/OEM flow, Diller buyer-side product specifications and FAQ. Competitor images and branding are not copied.
- The B2B quote form remains disabled until verified inbox/privacy/security are ready; draft catalog data is not published via API.

## October homepage refinement
- Preserved target-inspired four-photo Products menu and compact Capabilities / Why Us dropdowns.
- Reorganized homepage flow to match target's editorial rhythm without copying third-party media or unsupported factory claims.
- Replaced duplicative product and capabilities sections with genuine 4-tab product display and a working buyer-brief model preview.
- Added dark two-column procurement FAQ / inquiry-preview section. Live submissions remain explicitly disabled.
- Preserved existing material suitability and factory capability modules with no invented metrics.
- Responsive preview tested at 320px, 390px, 820px and 1440px with no horizontal overflow or missing image assets.


## Homepage collection, strengths and brand wall refinement
- Four switching categories now have eight editorial photo tiles per panel (four wide by two deep on desktop; two columns on mobile) using actual XUYI Excel/PPT images.
- Company strength presentation covers own manufacturing facility, coordinated partner models, OEM/custom options, verified-model quality review, and order logistics with no invented factory capacity or certifications.
- Customer logo wall has six reserved locations but **no customer names or logos are published without verifiable customer authorization**.
- To add authorized customer logos, put owned/authorized images at /assets/customer-logos/<filename> and add name, logo_path and authorization to data/customer-logos.json; rebuild with python build.py.
- Mobile responsiveness checked at 320, 390, 768, 1024, and 1440 px; all four tabs work with actual catalog photos; no overflow.
