#!/usr/bin/env python3
"""Guard the 2026-10-26 append-only CMS article batch and source ownership."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
SLUGS={"coffee-shop-branded-water-bottles-wholesale","museum-gift-shop-custom-water-bottles-wholesale","auto-dealership-branded-water-bottles-bulk"}
posts=json.loads((ROOT/"data/blog-guides-20261026.json").read_text(encoding="utf8"))
assert {p["slug"] for p in posts}==SLUGS and len(posts)==3
assert all(p["updated"]=="2026-10-26" for p in posts)
endpoint=(ROOT/"functions/api/admin/blog-batch-20261026.js").read_text(encoding="utf8")
auth=(ROOT/"functions/_shared/build-auth.js").read_text(encoding="utf8")
renderer=(ROOT/"site_renderer.py").read_text(encoding="utf8")
editorial=(ROOT/"blog_editorial.py").read_text(encoding="utf8")
sitemap=(ROOT/"sitemap_modification.py").read_text(encoding="utf8")
publisher=(ROOT/"scripts/publish_blog_batch_20261026_d1.py").read_text(encoding="utf8")
corrections=json.loads((ROOT/"data/blog-photo-corrections-20261026.json").read_text(encoding="utf8"))
worker=(ROOT/"functions/blog/[[path]].js").read_text(encoding="utf8")
assert 'const DAY="2026-10-26"' in endpoint
assert all('"'+s+'"' in endpoint for s in SLUGS)
assert "ON CONFLICT(slug) DO NOTHING" in endpoint
assert "ON CONFLICT(resource_id,locale) DO NOTHING" in endpoint
assert "instr(json_extract(translated_json,'$.mainHtml'),?)=0" in endpoint
assert "/api/admin/blog-batch-20261026" in auth
assert 'data/blog-guides-20261026.json' in renderer and 'data/blog-guides-20261026.json' in editorial
assert 'data/blog-buyer-decision-tables-20261026.json' in editorial
assert "_BLOG_20261026" in sitemap and 'data/blog-guides-20261026.json' in sitemap
assert "CLOUDFLARE_API_TOKEN" in publisher
assert set(corrections)==SLUGS
assert "PHOTO_20261026" in worker
assert all(corrections[p["slug"]]["photo"]==p["cover"] for p in posts)
assert len({p["cover"] for p in posts})==3
for p in posts:
 assert (ROOT/p["cover"].lstrip("/")).is_file()
 assert (ROOT/p["cover"].lstrip("/")).stat().st_size>30000
 assert len(p["sections"])==7 and len(p["checklist"])==10 and len(p["faqs"])==4
 assert len(p["related"])==3 and len(p["product_notes"])==3
 assert len({n["sku"] for n in p["product_notes"]})==3
 for note in p["product_notes"]: assert note["text"]["en"].count("{product}")==1
print("XUYI_20261026_APPEND_ONLY_CMS_OWNER_PRIORITY_AND_SOURCE_ROUTES_PASS",len(posts))
