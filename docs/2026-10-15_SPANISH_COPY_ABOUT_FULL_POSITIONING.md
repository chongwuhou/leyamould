# XUYI Spanish microcopy and About differentiation — owner-safe source update

**Date:** 2026-10-15. Source-only edition, no production D1 or R2 writes, no manual `dist` edits.

## Spanish wording at its actual D1 source ownership boundary

Reviewed the authentic D1 snapshot's `page:/` and `page:/blog/` Spanish `mainHtml` along with all sixteen `page:/blog/<slug>/` articles.

- The home hero's **“Vasos de plástico”** becomes **“Botellas de plástico”**.
- The homepage manufacturer H2, originally **“Confiable Botella de plástico Socio fabricante.”**, is now exactly **“Socio fabricante confiable de botellas de plástico.”** in visible text, preserving existing `<em>` emphasis only around **“botellas de plástico”**.
- The shared Spanish Blog eyebrow **“XUYI · VASOS DE PLÁSTICO”** becomes **“XUYI · BOTELLAS DE PLÁSTICO”** in the blog listing **and all 16 blog article pages**; ordinary article text, titles, excerpts and SEO metadata remain untouched.
- Homepage conditional materials question **“SIN BPA?”** becomes **“¿Sin BPA?”**, and continues to explicitly request material and test verification for the chosen model. It **does not** claim that any existing product is certified BPA-free.

`spanish_reviewed_copy.py` owns the exact approved HTML-element substitutions at the D1-aware locale **source-render stage**, called from `scripts/render_locales.py` *before final HTML generation*. The substitutions are narrow enough to preserve any later owner replacement of the hero note, H2, blog eyebrow, or full D1 body. Future blog articles automatically get the same wording when they use the same unchanged Spanish source element. There is **no broad replacement of all “vasos” terms** across the site.

`home_bpa_source.py` renders all five localized conditional material enquiry tags as a reusable source component at the English home template in `site_renderer.py` and the D1-aware `scripts/render_locales.py` locale pages. Its guarded source `hero__note` must precisely match a reviewed original. An owner-edited note or newly approved locale is left alone. The obsolete **post-generation home badge mutation** was removed from `scripts/verified_capacity_gradient_en.py`. This does **not** remove unrelated legacy verified gradient annotations; they remain outside the scope of this change. `scripts/build_release.py` documents the correct owner of the new badge.

## About's differentiation retained and expanded

The existing `what-you-wont-find-here` section was found live in English and the four other locales. It was never removed; only the English explanatory paragraphs were previously shorter. The user-supplied full English section has now been incorporated into **`data/about-company-en.json`**, including the introductory sentence and three complete claims:

- **No metal. No glass.** — only actual reusable plastic drinkware, specifically the four recognized bottle categories.
- **No stock photography.** — source catalog model photography, not speculative renderings.
- **No unverified numbers.** — measurements/capacities/timelines require physical sample and purchase-order specification confirmation.

The shared About template `about_company_page.py` displays an optional source `noClaimsIntro` only when present; all five About locales retain their original three-claim section, with the D1 owner override still taking precedence. No invented factory performance figures or third-party certifications.

## QA and publication gates

- `scripts/test_spanish_microcopy_about_source.py` tests all three Spanish source corrections, all 17 Spanish Blog eyebrow locations, conditional BPA labels on five homepage routes, exact idempotence, simulated owner-edited D1 source elements, About source body and all five published About pages. New permanent CI check in `.github/workflows/publish-xuyi.yml`.
- Updated existing `scripts/test_verified_capacity_gradient.py` to validate the new source-owned badge and CMS hero override, rather than invoke the removed dist mutator.
- Updated old About page test's three English assertions to match the new full buyer statement while retaining all other tests.
- Full build still generates 973 artifacts, 757 HTML, 505 actual five-locale model pages and 755 sitemap URLs. Run two complete source builds and compare homepage×5, Blog listing+article×17 (Spanish), About×5, 3 representative products, sitemap and CSS; no generated HTML edits.
- Full regression suite and GitHub release validation must pass, Cloudflare production deploy and live SHA verification are mandatory. IndexNow notification is not a guarantee of Google indexing.
