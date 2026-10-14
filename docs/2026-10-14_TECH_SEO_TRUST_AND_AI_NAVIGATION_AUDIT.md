# XUYI SEO / GEO technical audit — October 14, 2026

Applies only to xuyi-drinkware-site. Permanent source/CMS build flow, not one-off dist edits.

## Source-backed corrections
1. Product schema already contains actual name, SKU, image and product properties. No verified price, stock, MOQ number, or independently sourced reviews exist for all SKUs. Added quote CommunicateAction for each real SKU instead of fabricating Offer, InStock, AggregateRating or reviews. Google Product rich results are not guaranteed without required commerce fields.
2. English, Spanish, Portuguese, Russian and Turkish homepages each contain five visible FAQ pairs. FAQPage is generated directly from those visible pairs after CMS rendering, so content remains accurate. Google limits FAQ rich results; this markup does not guarantee traffic.
3. BlogPosting already identifies XUYI Bottles as Organization author; it was not authorless schema. Added visible linked organization editorial bylines to the 80 localized blog article pages and aligned author URL with the corresponding About page. No fabricated Person names or qualifications.
4. Real PNG/WebP/JPEG dimension headers provide truthful OG image width/height for 155 HTML pages with locally present assets. R2 image dimensions remain unclaimed unless independently verified. Existing CMS preview choices are preserved.
5. Added /llms.txt as an optional navigation reference to real official pages. No ranking, AI citation, or indexing guarantees are claimed.
6. English product SEO headlines now favor buyer-facing Custom Logo product terms when supported, alongside actual source ml, approximate overseas oz class and factory SKU. Never claim an unverified Tritan material, straw closure, certification or current inventory.
7. Existing clickable email and WhatsApp anchors were confirmed in built pages, contradicting the claim that no links exist. No tel: is introduced without evidence the number is available for calls.
8. Six large customer-brand marks are intentionally UNCHANGED at the user's express request. Their source manifest labels them group-site references, not independently verified direct XUYI customers.
9. Do not invent founding year, detailed factory address, certificates, capacities, customer testimonials or translation quality. Deep new market/language content remains a separate evidence-backed undertaking.

## Engineering evidence
- Main build hook: scripts/verified_trust_technical_seo.py invoked from scripts/build_release.py.
- Permanent regression: scripts/test_verified_trust_technical_seo.py and updated scripts/test_seo_multilingual_launch.py, in GitHub Actions release gates.
- Shared styling: assets/site.css, no direct dist-only edit.
- Local tests: 55 Python release gates passed; full source rebuild repeated twice; SHA256 stable across 9 representative artifacts.
- Production publication and Node tests must be verified from official GitHub Actions before claiming the site is live.