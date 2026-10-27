# XUYI review publication times and sitemap (effective 2026-10-28 Beijing time)

- Leave every review already published on or before 2026-10-27 unchanged: no update to its D1 row, source text, author, rating, model, or existing date-only display.
- Keep selecting genuine Excel reviews by exact SKU with an immutable, append-only D1 publication ledger. The global daily maximum remains three, and any replay is idempotent.
- Instead of writing all three in one batch, schedule **one real publication per action run** at three different times: 09:17, 13:47 and 19:13 Beijing time (GitHub schedules may start later).
- For **new publications only** (D1 ledger day 2026-10-28 onward), display the actual ledger `recorded_at` UTC timestamp converted to Beijing time down to the minute and expose the corresponding timezone-aware ISO 8601 `datePublished` on the exact product. Never invent timestamps, retroactively randomize historical review dates, or backdate a review.
- Rebuilds get the new true timestamp through the authenticated D1 snapshot. Product pages with genuinely newly published reviews receive an updated sitemap `lastmod` derived from the review's true D1 publication date. Unchanged pages are not redated on deployment.
- An unrun/delayed GitHub schedule means fewer than three reviews on that day, not fabricated catch-up publication times. The original 24 reviews published by 2026-10-27 are unchanged.
