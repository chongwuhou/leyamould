# XUYI site — durable change rules

**The site owner requires all fixes to survive subsequent complete rebuilds.**

1. **Change the source of truth.** Prefer shared page templates, CMS/data inputs
   or versioned build functions. Do not hand-edit generated dist output, edit
   only production HTML, or treat temporary local outputs as a permanent fix.
2. **D1/CMS owner edits take precedence.** Only apply historic curation when
   the field still has the baseline value. New SEO titles, descriptions, photos,
   translated copy and content edited in admin must not be overwritten by
   older cleanup scripts. The cms_seo_curation_guard helper implements this
   policy for curated title/description transforms.
3. **Keep production sources immutable.** Never invent dimensions, materials,
   certifications, MOQ, inventory, manufacturing evidence or changed factory
   model identity. G-series codes are confirmed factory models. Do not replace
   a specific product image without exact source/model visual review.
4. **Guard growth, not a frozen count.** A new approved product, article or
   language page should not fail a release simply because previous totals were
   85, 101, 505 or 755. Detect missing baseline routes and actual broken links.
5. **Rebuild verification is mandatory.** Rebuild from source (the builder
   deletes and regenerates dist), run SEO/locale/Blog/media regressions and
   verify a second clean rebuild produces the same intended outputs. Test
   explicit CMS-edited data before deploying.
6. **No blind deployment.** Publish only when source changes and required tests
   pass; verify the deployed revision and representative production URLs.
7. **No unrequested new features.** Fix the proven defect only and preserve
   unrelated layouts, database, original R2 objects and customer inquiries.

This project policy stays in the repository for future maintainers and code
assistants independently of chat history.