#!/usr/bin/env python3
"""Read-only Oct 28 cover integrity and future CMS-photo ownership guards."""
import json,hashlib,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from blog_media_source import blog_cover_from_cms_source
POSTS=json.loads((ROOT/"data/blog-guides-20261028.json").read_text(encoding="utf8"))
assert len(POSTS)==3
paths=set()
hashes=set()
for post in POSTS:
    cover=post["cover"]
    assert cover.startswith("/assets/blog/") and cover.endswith("-20261028.webp")
    assert cover not in paths,(post["slug"],"Duplicate photo")
    paths.add(cover)
    p=ROOT/cover.lstrip("/")
    assert p.is_file() and p.stat().st_size>30000,(p,"Missing image")
    with Image.open(p) as im: assert im.format=="WEBP" and im.size==(1200,800),(p,im.size)
    hashes.add(hashlib.sha256(p.read_bytes()).hexdigest())
    for loc in ("en","es","pt","ru","tr"):
        article='<div class="blog-detail__cover"><img src="/assets/blog/owner-new-20261028.webp" alt="Owner changed photo"></div>'
        route="/blog/"+post["slug"]+"/"
        assert blog_cover_from_cms_source(article,route,loc)==article,(post["slug"],loc,"CMS edited cover overwritten")
assert len(hashes)==3,"All articles must have distinct photo pixels"
payload=ROOT/"_local_ops/blog-batch-20261028/payload.json"
if payload.is_file():
    data=json.loads(payload.read_text(encoding="utf8"))
    assert len(data["posts"])==3 and len(data["translations"])==12 and len(data["indexCards"])==12
    by_slug={x["slug"]:x["post"]["cover"] for x in data["posts"]}
    for row in data["translations"]:
        slug=row["route"].strip("/").split("/")[-1]
        assert row["mainHtml"].count('src="'+by_slug[slug]+'"')>=1,(slug,row["locale"],"Wrong hero photo")
    for card in data["indexCards"]:
        assert card["html"].count('src="'+by_slug[card["slug"]]+'"')>=1,(card["slug"],card["locale"],"Wrong listing photo")
print("XUYI_20261028_THREE_COVERS_FIVE_LOCALE_SOURCE_AND_CMS_OVERRIDE_PASS")
