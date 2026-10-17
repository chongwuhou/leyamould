# XUYI Phase 10 — another 20 source-backed SKU H2 module upgrades

**Release date:** 2026-10-15. **Scope:** 20 additional catalog models × 5 approved languages = 100 product detail pages. Together with Phase 9 this means **40/101 models (200/505 detail pages)** now have model-specific Materials, Design and FAQ modules, while all 101 already have differentiated opening introductions from earlier phases.

## Cohort and source evidence

The review started from `site_renderer.SERIES` and the approved five-language D1 translation snapshot. Three collections qualify for another evidence-backed phase. Shakers currently have only the two unreviewed 5247/5248 records with an unresolved 450/700ml-to-model mapping, so do not falsely invent five verifiable shaker candidates.

- **Sports, 5:** 2512, 2513, 2514, 2209, 2402.
- **Kids, 5:** 2508, 2509, 2109, 2409, 2413.
- **Large-capacity jugs, 10:** 2291, 2292, 2215, 2250, 2270, 2271, 2305, 2307, 2308, 2416.

Peer comparisons are based on the source `capacity`, `dimensions`, `material`, `colors`, `packing`, `carton_quantity` and `carton_size` fields. When two models have the same capacity or outline (e.g. **2508/2509** or **2307/2308**), the editorial focus explicitly says that matched figures **do not establish interchangeable closures/tooling or a verified component map**. Only a physical sample or signed factory component document can establish this. No new certifications, BPA-free status, child-age suitability, leakproof claims, cupholder fit, exact custom color availability, accessory kits or MOQ were invented. Existing pending **2506** and **5247/5248** factory-documentation holds remain.

## Source of truth

- `data/product-20-module-source-baselines-phase10.json`: 20 model-to-peer assignments and **100 locale-specific pairs of section fingerprints**, taken from authoritative English product template and original D1 localized `mainHtml`; Design and FAQ are checked separately, so owner edits to either independent section survive.
- `data/sku20-phase10-focus-{sports,kids,jugs}.json`: **20 distinct editorial buyer decision notes**, individually authored and reviewed in EN/ES/PT/RU/TR. They are source-grounded comparisons, not random phrase rotation.
- `sku_factual_sections.py`: retains `FIRST20` as the previous approved cohort, adds `NEXT20`, and merges 40 baseline records and five-language review notes into the existing source renderer. This drives two meaningful model-specific paragraph/cards and visible FAQ answers by currently approved catalog/CMS values. New unrelated SKUs are untouched; the owner of edited translated sections wins.
- `product_material_performance.py`: the same source-backed compact material section now covers the selected 40, and leaves the remaining 61 with their previous material template. Source material families are *not* a body/lid/straw/gasket bill of materials.
- `scripts/test_phase10_next20_sku_h2_sections.py`: new coverage for 100 localized pages, comparisons, source hashes, owner-changed FAQ, source Materials owner edit, replay idempotence, exact FAQ JSON-LD parity, unaffected generic SKUs and future model support.
- Existing Phase 9 test remains scoped explicitly to `FIRST20` and continues to validate all 100 earlier routes.
- New test is in `.github/workflows/publish-xuyi.yml`, so GitHub Actions must pass before production deployment.

## Fixed-cohort similarity diagnostic

Measured with the same numeric-masked, 3-word shingle Jaccard nearest-neighbor to other reviewed models **within the same collection and language**. These are editorial similarity numbers, **not** a Google safe threshold, penalty or ranking guarantee.

| H2 module | Prior default / native D1, five-language median range | Updated, five-language median range |
| --- | ---: | ---: |
| Design, Materials & Applications | 1.000 | 0.584–0.654 |
| Frequently Asked Questions | 0.934–1.000 | 0.565–0.622 |
| Materials and practical use | 1.000 (default unselected source Materials template) | 0.723–0.781 |

For the Materials baseline comparison, the old template was reconstructed by rendering a copy of each same catalog row with an unselected slug, to avoid accidentally comparing a new template with itself. The corrected baseline is a *module comparison*, not a claim of separately archived pre-release production HTML.

The other three user-identified H2 blocks — OEM ordering, related models, and conditional Tritan/BPA-free custom options — intentionally remain shared unless the CMS owner modifies them.

## QA and release gate

- Official builder `python -B scripts/build_release.py` deletes/rebuilds all of `dist/`; no patching post-built product HTML is part of this release.
- Full site consists of 101 models, 505 product detail routes, 757 HTML pages, 973 artifacts, and 755 published sitemap URLs. No D1/R2 production writes.
- Run two full source builds, compare SHA256 of all 200 selected five-language product pages plus homepage, sitemap and CSS. Run site, SEO, links, CMS owner, schema, locale, inquiry and source policy tests. No hard-coded 101-model maximum.
- Only mark released after GitHub CI succeeds, Cloudflare Pages deploys, and live production SHA is verified.

## Next eligible work

After this stage, **61 of 101 models** will still retain partially generic H2 modules, though all 101 still have distinct model introductions. The source-backed material and FAQ module can be expanded with further primary catalog verification; do not prematurely mark the two ambiguous Shaker models or 2506's source capacity as factory-verified.
