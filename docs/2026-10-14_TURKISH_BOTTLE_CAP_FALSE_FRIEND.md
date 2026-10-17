# Turkish bottle-cap translation correction — 2026-10-14

Owner reported a serious false-friend translation: `spor şapkalar` means sports hats, not water-bottle caps.

Approved Turkish replacement:
`Şeffaf su şişeleri, spor şişesi kapakları ve ekonomik plastik içecek ürünlerini değerlendiren OEM alıcıları için Tritan, PP, PETG ve PC karşılaştırması.`

The legacy D1 translation repeats the same source phrase in five distinct **fields** across four routes: `/blog/`, `/blog/tritan-vs-pp-petg-pc/`, `/blog/bpa-free-plastic-water-bottle-sourcing/`, and `/blog/plastic-bottle-material-selection/`. The main article has its own metadata `description` and body `mainHtml`. Three others carry the old article abstract in a related-card block.

Permanent fix: `data/turkish-bottle-cap-review.json` contains reviewed field hashes and the approved Turkish text. `turkish_bottle_cap_source.py` checks only this exact known D1 baseline and replaces the false friend in source values **before** `scripts/render_locales.py` creates a page, structured data, Open Graph or meta descriptions. A future owner edit in D1 no longer matches the historic field hash and remains untouched, including future new model/language content. Never directly rewrite `dist` or the live HTML. Repeat build is idempotent and all five languages are validated.

`scripts/test_turkish_bottle_cap_terminology.py` covers all four routes, all five source fields, canonical article description/meta/OG/BlogPosting schema, the Turkish HTML language set, owner-edited field preservation and new-route compatibility; included in release CI.
