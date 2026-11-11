#!/usr/bin/env python3
"""Guard the 2026-10-26 append-only CMS article batch and source ownership."""
import json,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from blog_media_source import blog_cover_from_cms_source,PHOTO_CONTEXT_LOCALIZED_REPAIRS
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
context_corrections=json.loads((ROOT/"data/blog-photo-context-corrections-20261026.json").read_text(encoding="utf8"))
media_source=(ROOT/"blog_media_source.py").read_text(encoding="utf8")
assert 'const DAY="2026-10-26"' in endpoint
assert all('"'+s+'"' in endpoint for s in SLUGS)
assert "ON CONFLICT(slug) DO NOTHING" in endpoint
assert "ON CONFLICT(resource_id,locale) DO NOTHING" in endpoint
assert "instr(json_extract(translated_json,'$.mainHtml'),?)=0" in endpoint
assert '"/api/admin/blog-batch"' in auth
assert "/api/admin/blog-batch-20261026" not in auth
from blog_catalog_source import load_guides
assert 'from blog_catalog_source import load_guides' in renderer
assert 'from blog_catalog_source import load_guides' in editorial
assert SLUGS.issubset({p["slug"] for p in load_guides(ROOT)}), "Published 2026-10-26 guides missing from authoritative dynamic source registry"
assert 'data/blog-buyer-decision-tables-20261026.json' in editorial
assert "_BLOG_20261026" in sitemap and 'data/blog-guides-20261026.json' in sitemap
assert "CLOUDFLARE_API_TOKEN" in publisher
assert set(corrections)==SLUGS
assert "data/blog-photo-corrections-20261026.json" in media_source
assert "PHOTO_20261026" in media_source
assert "data/blog-photo-context-corrections-20261026.json" in media_source
assert "PHOTO_CONTEXT_20261026" in media_source
assert "PHOTO_CONTEXT_LOCALIZED_REPAIRS" in media_source
assert all(corrections[p["slug"]]["photo"]==context_corrections[p["slug"]]["baseline"] for p in posts)
assert all(context_corrections[p["slug"]]["photo"]==p["cover"] for p in posts)
assert all(p["cover"].startswith("/assets/blog/") for p in posts)
assert len({p["cover"] for p in posts})==3
assert set(context_corrections)==SLUGS
assert all(context_corrections[p["slug"]]["baseline"]==corrections[p["slug"]]["photo"] for p in posts)
assert all(context_corrections[p["slug"]]["photo"]!=context_corrections[p["slug"]]["baseline"] for p in posts)
for post in posts:
 entry=context_corrections[post["slug"]]
 new=entry["photo"]
 photo=ROOT/new.lstrip("/")
 assert photo.is_file() and 20000<photo.stat().st_size<250000,photo
 with Image.open(photo) as img: assert img.format=="WEBP" and img.width>=960 and img.height>=640,(photo,img.size,img.format)
 assert PHOTO_CONTEXT_LOCALIZED_REPAIRS[post["slug"]]==(entry["localizedBaseline"],new)
 for old in (entry["baseline"],entry["localizedBaseline"]):
  for locale in ("en","es","pt","ru","tr"):
   index='<section class="section blog-listing"><div class="shell"><div class="blog-listing__grid"><a class="news-card__image" href="/blog/'+post["slug"]+'/"><img src="'+old+'" alt="Owner choice"></a></div></div></section>'
   detail='<div class="blog-detail__cover"><img src="'+old+'" alt="Owner article"></div>'
   for markup,route in ((index,"/blog/"),(detail,"/blog/"+post["slug"]+"/")):
    updated=blog_cover_from_cms_source(markup,route,locale)
    assert new in updated and old not in updated,(post["slug"],old,locale,route)
    assert entry["alt"] in updated,(post["slug"],old,locale,"reviewed ALT")
    assert updated==blog_cover_from_cms_source(updated,route,locale),(post["slug"],old,locale,"idempotence")
    edited=markup.replace(old,"/assets/blog/owner-new-choice.webp")
    assert blog_cover_from_cms_source(edited,route,locale)==edited,(post["slug"],old,locale,"CMS cover priority")
for p in posts:
 assert (ROOT/p["cover"].lstrip("/")).is_file()
 assert (ROOT/p["cover"].lstrip("/")).stat().st_size>30000
 assert len(p["sections"])==7 and len(p["checklist"])==10 and len(p["faqs"])==4
 assert len(p["related"])==3 and len(p["product_notes"])==3
 assert len({n["sku"] for n in p["product_notes"]})==3
 for note in p["product_notes"]: assert note["text"]["en"].count("{product}")==1
print("XUYI_20261026_APPEND_ONLY_CMS_OWNER_PRIORITY_AND_SOURCE_ROUTES_PASS",len(posts))

