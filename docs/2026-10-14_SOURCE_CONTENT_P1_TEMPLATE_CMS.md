# XUYI content quality P1 — source template / D1-first delivery

2026-10-14. Scope: preserve all product URL slugs and all six existing customer-brand logos.

## Implemented in authoritative sources

- **16 articles**: `data/blog-buyer-decision-tables.json` contains a different model-specific buyer decision table per published English article, including choice factors, what to verify, and source-valid product/category links. Static source renderer is `blog_editorial.render_buyer_matrix`. D1-backed live English blog uses the same JSON through `functions/_shared/blog-cms.js`. The latter keeps current editor-authored text unchanged and honors a saved `buyerDecisionTable` override or `false` opt-out. No bulk post-render HTML replacement.
- **Five-language Applications/Features**: previously `scripts/curated_application_feature_answers.py::apply` edited each generated HTML file. The release builder NO LONGER calls it. Its `render_buyer_evidence` now runs at the template/CMS composition stage in `site_renderer.build_url` and `scripts/render_locales.py`. If a D1 body already contains the published module marker, it is preserved, not reinserted. All 50 routes retain their original localized decision checks.
- **10 English-topic grids**: data/topic-decision-grids-en.json provides 10 distinct application/feature purchase-decision tables, within the shared buyer-evidence source component. No automatically translated versions are asserted as reviewed.
- **B2B contact form**: the shared `templates/site/contact-form.html` tells buyers which three business fields are mandatory; consent is still required, with other fields optional. `data/contact-form-translations.json` supplies reviewed text for ES/PT/RU/TR. Form field names, client validation, D1 endpoint, spam honeypot and backend contract remain unchanged.
- **Dynamic D1 blog FAQ**: `BlogPosting` retains its factual publisher/author and the runtime emits `FAQPage` only for actually visible FAQ pairs. No promise of rich-result eligibility.
- **CI**: added `scripts/test_source_buyer_decision_content.py` and `scripts/test_blog_buyer_decisions_runtime.mjs` to the release gate, including D1 owner overrides, opt-out, existing URL integrity, accessible local link checks and five-language form fields.

## Real limitations — not to overclaim

- This first source-content upgrade does **not** mean all sixteen English posts now contain 1,800–2,500 genuinely researched words, or that there are client testimonials. Work toward long-form deep guides should be editorial and evidence-based, not word-count padding.
- Verified factory year, staffing, output, MOQ brackets, lead times, certified report IDs, named customer case studies and import-market counts were **not supplied**; therefore none were invented or copied from competitors.
- Source-retained Spanish/Portuguese/Russian/Turkish blogs were not bulk-overwritten by English tables. Human-reviewed in-language comparisons require separate canonical D1 records.
- Existing Applications/Features source has other legacy postprocessors, but the specific five-language buyer-answer injector was migrated to the shared rendering pipeline. All future bulk tasks remain bound by `AGENTS.md` P0.
- Product URLs, slugs, canonical/hreflang URL structure, R2 originals and the six logo section are unchanged.

## Local validation

- `python -B scripts/build_release.py` passed twice; 10 representative output SHA-256 hashes matched.
- 57/57 Python CI tests passed, including 16 buyer matrix data sources, 50 five-language topics, 5 translated contact forms and baseline URL checks.
- GitHub CI Node.js tests and deployment require the release run to pass before reporting production success.