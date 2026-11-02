# XUYI product-review publication system — multi-review per SKU

Updated: 2026-11-02

## Authoritative private source files

Only these two owner-provided workbooks are approved sources:

| Workbook | Workbook SHA-256 | Original rows | Eligible rows |
|---|---|---:|---:|
| \`101-zhenshipingjia.xlsx\` | \`1cce3652003a78d3e175a2c02a07caf08bda136dc63bea9e246b0006ae2f3163\` | 101 | 101 |
| \`101-additional-reviews-only.xlsx\` | \`ebd5f045fc476d429dcf2c6c68f6fb49c3983b145701fe4587e2e9936b771aa8\` | 101 | 100 |

Private JSON files under \`review_import_private/\` are derived, validated payloads, not additional source workbooks. Never copy them into \`dist/\`, R2 public storage, or public endpoints.

The second workbook's row 59 (Beatriz Santos, model 2319) is excluded because the first workbook row 59 has the same customer name and model. The texts differ, but it is treated as a possible duplicate customer/SKU attribution and is not published.

Total eligible unique source reviews: **201 across 101 product models**.

## Publication rules

- A product model may have multiple different customer reviews.
- Every review has its own UUID in \`xuyi_product_reviews.id\`.
- The publication ledger is keyed by review UUID and unique source fingerprint, not product model.
- Source identity is \`(source_file, source_row)\`; row 2 in each workbook is a different source record.
- SHA-256 fingerprint: \`model + newline + rating + newline + author + newline + original review text\`.
- Fingerprints already in the ledger or already published in D1 are never published again.
- The same model may appear more than once in a batch; the same source row or fingerprint may not.
- Maximum **3 new review records per Beijing calendar date**, across both workbooks.
- The original model-unique \`xuyi_review_publication_ledger\` remains read-only as the migration source. New rows go to \`xuyi_review_publication_ledger_v2\`.
- The v2 migration copies every legacy ledger row with \`source_file='legacy-unmapped'\`; it is additive and idempotent. Existing published reviews and review IDs are preserved.
- The product renderer already supports multiple visible review cards and JSON-LD Review arrays plus AggregateRating. The build snapshot already reads all published D1 reviews.

## Expected reconciliation after migration

The verified D1 baseline on 2026-11-02 was 42 published review records:
- 40 exact source fingerprints from the first workbook.
- 2 exact source fingerprints from the second workbook.
- 42 unique review IDs and 42 occupied product models.
- No extra D1 draft rows or unledgered model placeholders.

The 42 old ledger fingerprints map to the two source payloads. Therefore **159 of the 201 eligible source reviews remain unpublished**. The first workbook has 61 not yet published; the second has 98 eligible reviews not yet published. This is a source-review count, not a SKU count.

The regular publisher samples up to three unused review fingerprints each day. Do not bypass this limit with a bulk import or one-time batch unless the owner explicitly changes that rule.

## Deployment and data safety

1. Deploy the v2 endpoint/schema code first; the first authorized GET performs the idempotent legacy-ledger migration and verifies all old rows.
2. Run publisher dry-run and verify the 201/101/two-source reconciliation.
3. Rebuild from the authenticated D1 snapshot and confirm multiple review cards for a same-SKU fixture in all five locales.
4. Only after tests and migration read-back succeed should the feature branch be merged/deployed.
5. Do not publish new reviews as part of schema deployment; the daily publisher remains a separate, explicit workflow action.

## Production rollout completed — 2026-11-02

- PR #18 was merged to main (merge commit `171e9dce44590f043faf773d06303e7b11237952`).
- Cloudflare Pages deployment and live revision verification succeeded in GitHub Actions run `41409913675` (successful retry/attempt 2; deployed source commit `b0d5eddca3ce15927e04173a08d9887dda27baff`).
- The production endpoint's authenticated, GET-only v2 migration completed successfully after deployment.
- All 42 legacy publication-ledger rows were preserved in the v2 ledger; all 42 published review fingerprints still match published review records.
- D1 `publishRevision` remained `50` before and after migration.
- The migration did not publish, edit, or delete any customer review. Production still contains 42 published reviews.
- The independent daily publisher remains capped at three new reviews per Beijing date. The 2026-11-02 daily cap was already reached; next scheduled run is 2026-11-03 at 09:17 Asia/Shanghai.
- Remaining eligible source reviews: 159 (61 from the first workbook, 98 from the second). The second workbook's row 59 remains excluded.

The first production workflow attempt encountered transient HTTP 503 responses from the build-snapshot endpoint and did not deploy. The redundant dry-run snapshot fetches were reduced; the subsequent workflow completed successfully. A separate read-only snapshot health check confirmed revision 50, 119 pages, 85 products, 42 reviews, and 756 translations.
