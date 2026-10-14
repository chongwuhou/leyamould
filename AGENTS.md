# XUYI website mandatory change policy

Before editing this project, read [PROJECT_CHANGE_POLICY.md](PROJECT_CHANGE_POLICY.md).
This applies to localGPT, Codex, other coding agents and human maintainers.

1. Make every correction in the **shared source template, CMS-aware data,
   reusable rendering function, or version-controlled build pipeline**.
   Never count editing dist output or already deployed HTML as a fix.
2. Cloudflare **D1/CMS owner edits are authoritative**. Later edits to SEO
   titles, translations, Blog text, links and product images must not be
   overwritten or rejected by earlier cleanup scripts.
3. Make source transformations **idempotent and tolerant of existing
   owner-selected content**. Do not require old image URLs or previous
   page totals to remain unchanged forever.
4. Rebuild the entire site from source and test a second rebuild; validate
   all five locales, canonical/hreflang, links, inquiry functionality and
   representative live URLs before declaring a production release complete.
5. Keep G-series factory model status intact. Never invent product data,
   certifications, physical factory evidence or exact-SKU photographs.
6. Make the smallest change that fixes the proven issue. Do not modify
   unrelated front-end design, D1 inquiries or R2 original media.

If a legacy script violates these rules, fix that script and add a regression
test reproducing a realistic owner/CMS update before publishing.