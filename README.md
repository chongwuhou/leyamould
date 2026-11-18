# XUYI Drinkware — B2B Static Frontend

> **唯一执行入口：** 具体操作统一按 [XUYI 网站统一执行手册](docs/XUYI_OPERATIONAL_RUNBOOK_ZH.md)。本文件的原则优先级不变；带日期的历史说明仅供追溯。

> **统一内容/翻译/AI/工具发布标准：** [项目圣经/统一内容发布与翻译审计标准.md](项目圣经/统一内容发布与翻译审计标准.md)。业务数据走 D1/CMS，媒体走 R2，禁止直接改 dist 或线上 HTML。

> **中文快速上手（换电脑 / 新同事用 AI 更新网站）：** [docs/AI_COLLABORATION_QUICKSTART_ZH.md](docs/AI_COLLABORATION_QUICKSTART_ZH.md)。说明 GitHub + localGPT + GitHub Actions + Cloudflare D1 的实际权限和操作方法。

> **P0 OWNER DIRECTIVE — READ BEFORE EVERY TASK:** `AGENTS.md` and `PROJECT_CHANGE_POLICY.md`. All batch content or UI changes must originate in **shared templates / authoritative source datasets / D1-CMS**, not manually patched pages, dist files, or post-render HTML rewrites. Testing generated pages is temporary only; finalize at the source and verify CMS owner edits survive subsequent rebuilds.


> **2026-10-09 architecture hardening:** The canonical build source is now
> `templates/site/` + the Python content modules + XUYI datasets.
> Run `python scripts/build_release.py` to produce a clean `dist/`, and
> `python scripts/test_release.py` before deploying **only `dist/`**.
> Never redeploy the repository root. The old root-as-Pages-output setup exposed
> non-public Python/JSON source files. See `项目圣经/目录.md` and
> `deployment/site.config.json`. XUYI D1/R2/credentials stay independent of
> Unrelated project resources remain untouched. GitHub Actions auto-publication requires XUYI-specific secrets and
> disabling Cloudflare's competing Git build trigger before activating it.

Production branch: main; Cloudflare Pages: xuyi-drinkware-site; GitHub: chongwuhou/xuyi-drinkware-site.

## Current operating status (2026-11-08)

- XUYI uses a D1/CMS-owned content model with Cloudflare Pages static builds as the default public delivery path. Pages Functions remain for Admin/API, inquiries, media access and explicitly configured dynamic fallback routes.
- Languages, products, categories, routes, pagination and editable fields are read from D1/config at runtime or build time. Do not treat a historical count or a README statement as the current total.
- Product, Blog, review, translation and media updates must use the formal D1/CMS and R2 paths, then bump publish revision and pass the standard GitHub Actions build and live verification.
- The current production status is established by `deployment/site.config.json`, D1 publish revision, GitHub Actions, `build-meta.json` and read-only live checks. Historical release notes below are not current status.
## Scope
Kreat-inspired original navigation and UI system: homepage; D1/config-driven product categories and model routes; capabilities; About; Manufacturing; Quality Control; Shipping; FAQ; Blog; buying guides; Contact; Privacy Policy and 404. Product photos are from XUYI catalogs. Relevant group-owned unwatermarked factory, QA, packing and logistics images are reused under owner-confirmed permission (docs/GROUP_MEDIA_USAGE.md).

## Technology
- GitHub -> Cloudflare Pages: static HTML/CSS/JS.
- R2 xuyi-drinkware-r2, binding XUYI_ASSETS, read-only media proxy /media/[kind]/[filename].
- D1 xuyi-drinkware-d1, binding XUYI_DB, published-only products API.
- KV xuyi-drinkware-kv reserved for site settings.
- Regenerate static HTML with: python build.py.
- Indexing, robots and sitemap inclusion are controlled by deployment configuration and approval; verify the current state from build-meta and the live response.

## Source
Versioned catalog records and R2 media are inputs for legacy/source rendering and audit only; exact current product and media status comes from D1/CMS and R2.
Never commit local source catalogs, _local_ops secrets or Wrangler credentials. Unrelated project resources remain untouched.

## Launch blockers
Verify SKU variants, 2506 anomalous capacity, official English legal name, company factory photography, product certificates, live email/WhatsApp and functional inquiry delivery, privacy/consent and local translations. No checkout.

## Responsive
Desktop, tablet and mobile templates, accessible mobile menu, mega menus, model search/filter and fixed mobile inquiry link. QA on 320–1440 px.

## Historical implementation notes (do not use as current counts or status)

The dated sections below record past implementation decisions and evidence. Current business values, languages, products and publication status come from D1/config and the active release pipeline.

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

## Target-order homepage correction
- Homepage section order now follows Kreat: hero > company intro > four-column photo categories > Why Choose (OEM/ODM/wholesale) > customization > materials > manufacturing capability > restrained approved-customer-logo slots > FAQ/inquiry > news/blog > footer.
- Removed the overlaid tile labels and large visual company-strength module that disrupted the reference site's spacing.
- Category labels sit under 1:1 source photos; desktop four-by-two grid, mobile two-column. Shaker short list uses an eighth category discovery card.
- No fabricated factory capacities or customer associations; logo wall is still awaiting verified, publishable logos.
- Product detail pages, D1/R2 bindings and unrelated projects remain untouched.


## Homepage News & Blogs fix
- The previous "Resources for Wholesale Buyers" section was a plain-text three-card panel that failed to match the Kreat homepage.
- Restored target's News and Blogs large headline with icon, explanatory text, left guide counter and arrows, and right image carousel; desktop displays two large photos, mobile is touch-scrollable.
- All six actual XUYI buyer-guide articles are linked. No unverified posting dates or external competitor images.
- /blog/ now has a six-article photo grid; all six /blog/{slug}/ detail pages include matching XUYI catalog illustration.
- Moved authorized-only customer logo wall to follow black inquiry/FAQ block and precede News & Blogs, matching the target's actual order.
- The actual inquiry form remains disabled pending verified company inbox, privacy notice and secure server-side delivery.

## Why Us SEO/GEO content upgrade
- Research references: Kreat (four Why Us pages); Everich (customization stages and material/quality inspection); GOX (SKU-level technical tables and packing); Diller (buyer-type use cases, drawing-to-tooling OEM/ODM process).
- Rebuilt /capabilities/oem-odm/, /manufacturing/, /quality-control/, /shipping-logistics/ in original English, focused on XUYI's plastic product families rather than copied stainless/glass claims.
- Each page: single descriptive H1, direct answer, unique intent-focused title/description, four feature/decision cards, six-step process, comparison/reference matrix, practical buyer checklist, seven unique FAQs, and deep links between categories and the Why Us content cluster.
- JSON-LD: Organization (registered Chinese company name), WebPage, BreadcrumbList, FAQPage matching visible Q&A. Added preview Open Graph metadata.
- Source images are real XUYI Excel/PPT catalog imagery, labeled as product illustrations (not factory photos).
- Do not publish unsupported: factory equipment and numbers, food-contact certifications, BPA-free claims, 24h quotes, sample/production lead times, fixed MOQ, DDP guarantee, client logos.
- Indexing remains controlled by deployment/site configuration and owner approval; do not use this historical note as the current indexing status.


## Four Why Us Pages - Distinct Group Photo Revision
- Group-approved reference images collected from Kreat OEM, manufacturing, quality, and shipping pages. Image source URL mapping: data/why-us-group-media.json.
- 20 compressed WebP images (~0.3 MB) uploaded into XUYI's existing R2 bucket at site-preview/group/ and served via /media/group/{allowlisted-file}.webp. No unrelated storage is touched.
- Distinct page compositions implemented in why_us_layouts.py and assets/why-us-v2.css.
- OEM / ODM: XUYI plastic hero with 5 group customization references (including metal examples clearly identified), approval stages, model selection.
- Manufacturing: group packing/warehouse workshop images, plastic-specific component map, manufacturing checkpoints. No metal-forming equipment passed off as plastic molding.
- Quality: 6 real group testing-equipment images, component-focused inspection matrix and destination-market document scope.
- Shipping: real group warehouse plus export freight scenario images, packing data, transport modes, Incoterms.
- Group reference imagery cannot substitute for test results and verified specific equipment ownership or availability for a plastic SKU.
- Unique SEO titles, H1s, descriptive FAQ, JSON-LD, breadcrumbs, noindex preserved until launch approval.


## Manufacturing FAQ and Three Why Us Layout Correction
- Measured the online issue: the 1440 px layout has a 1360 px shell, but an old FAQ max-width of 1000 px and heading max-width 910 px caused visible right-side blank space on manufacturing, quality, and logistics.
- All three FAQ headings and the accordion grid now use 100% of the shared content shell on desktop and mobile.
- Manufacturing FAQ is a numbered full-width horizontal accordion; QA FAQ uses a full-width two-column quality-check card layout; logistics FAQ uses a sea-green full-width two-column buyer section. All return to one column on mobile.
- Suppressed the duplicate generic page CTA and fixed mobile inquiry bar on these service pages, avoiding obstruction of questions.
- Added three plastic-specific process references (injection blow molding, extrusion blow molding, lid component handling) to manufacturing. Original sources and reference status are in data/why-us-group-media.json; images uploaded to XUYI R2 under site-preview/group.
- Content deliberately distinguishes group/reference processes from a specific XUYI production line, test report, or confirmed machine.


## Expanded buying guide and supporting information pages
- Redesigned FAQ (/faq/): 54 original model-aware buyer answers in seven topics with search, category navigation, helpful internal links and matching FAQPage JSON-LD.
- Rebuilt /about/ with legal Chinese company name, four plastic categories, sourcing capability, and original group-site pack/QA/warehouse reference photographs already in XUYI R2. Group images are captioned as references and do not automatically establish a SKU certificate or machine ownership.
- Rebuilt /why-us/ with buyer-type guidance, factory-backed sourcing and group visual resources, plus practical approvals and internal links.
- Rebuilt /request-sample/ as six-stage sampling workflow, stock vs printed vs prototype guidance, sample-review checklist and seven topical FAQs.
- Rebuilt /capabilities/ with seven customization workflows linking to actual existing capability detail pages, and OEM vs ODM decision guidance.
- Reference research provenance is recorded in data/support-content-sources.json and group photo origins in data/why-us-group-media.json.
- Five page titles/meta descriptions are unique. BreadcrumbList, Organization, WebPage schemas used; FAQPage only where the visible Q&A exists. Site remains noindex until approved launch and inquiry delivery.
- Never infer XUYI product materials, temperatures, BPA status, certifications, production quantities or stock from source group-brand pages. No live inquiry submissions enabled.

- Added a separately sourced Everich group-site capacity reference on /about/: 70,000+ m², 13 automated lines, 15 million pieces/year, 1,200+ personnel. Clearly attributed to Everich public profile and NOT claimed as XUYI Taizhou plant capacity.

## FAQ Search Layout Correction
- Search replaced by a full-width light-grey band directly under the FAQ statistics strip; search input is aligned to the main FAQ answer column rather than capped at an unrelated 1010px width.
- Desktop layout uses explanatory text at left and live-search input at right; mobile stacks them. Added functional popular-search chips for MOQ, Materials, Logo, Sample and Shipping.
- Kept all 54 FAQ answers, seven topics, JSON-LD, internal links and preview noindex unchanged.
- Local browser QA at 320/390/768/1024/1440px verified FAQ search, chip actions, clearing search and zero horizontal overflow.


## Production domain, original group-brand carousel and XUYI favicon
- The canonical origin and indexing state are controlled by deployment configuration. Confirm current status from the live response and build metadata before changing SEO settings.
- Six ORIGINAL Kreat homepage brand carousel image assets: Amazon, Walmart, Costco, eBay, Coca-Cola and Carrefour. Saved unchanged under assets/customer-logos with source URL/provenance in data/customer-logos.json. Displayed as group-site brand references; not represented as independently verified direct XUYI clients or endorsements.
- Carousel loops horizontally with color logos, pauses on pointer/focus, is static and horizontally scrollable for reduced-motion visitors; adapts from desktop to mobile.
- Favicon designed to match the existing red XUYI wordmark: red rounded-square background + bold white X. SVG, ICO (16/32/48), 16/32 PNG, 180 apple touch and 192/512 PWA icons.
- All generated HTML pages get favicon/manifest links, a canonical URL under https://xuyibottles.com, and matching og:url metadata; existing JSON-LD and sitemap base URLs updated.
- Banner bottom-right 01 / 03 means first of three slides; a visible SLIDE label and synchronized accessible description make it explicit.
- Other Cloudflare projects were not modified.