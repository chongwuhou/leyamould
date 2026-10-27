# XUYI review date-only publication policy — effective 2026-10-28 Beijing time

- Google Search's Review structured data recommends `datePublished` in ISO 8601 **date** format; hours and minutes are not mandatory.
- The website and structured data keep showing only `YYYY-MM-DD` for reviews. Do not display or synthesize hour/minute timestamps.
- All 24 reviews published through 2026-10-27 are immutable: original customer text, rating, author, date and model remain untouched.
- The Excel source contains no verified original review dates. To keep future **displayed dates** distinct without fabricating them, automatically publish at most **one** authentic review on each real Beijing calendar date, beginning 2026-10-28. The standing scheduled run is around 09:17 Beijing time. Delayed/missed GitHub runs do not create backdated records.
- Keep the original D1 ledger and exact-model anti-duplication protections. Repeated CI/manual runs on one Beijing day publish no further rows if that day already contains any reviewed entries.
- Genuine new product review additions may update the corresponding product sitemap `lastmod` to the latest real change date. Unchanged URLs stay unchanged; no automatic redeclaration just because the site rebuilt.
