#!/usr/bin/env python3
"""Publish 8 photo-reference bottle styles without pretending to know factory SKUs."""
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from gallery_catalog import GALLERY,LABELS
from site_renderer import SERIES
assert len(GALLERY)==8 and len(SERIES)==101
assert {p["sourceFolder"] for p in GALLERY}=={1,2,3,4,5,9,10,12}
assert sum(len(p["images"]) for p in GALLERY)==24
assert "Gemini" not in json.dumps(GALLERY)
lang=["en","es","pt","ru","tr"]
for loc in lang:
 prefix="" if loc=="en" else loc+"/"
 path=ROOT/"dist"/prefix/"products/index.html"
 listing=path.read_text(encoding="utf8")
 assert listing.count('data-product-card')==101,(loc,"catalog count")
 assert listing.count('data-gallery-reference="true"')==8,(loc,"photo refs in catalog")
 assert listing.count('class="product-card__reference"')==8,(loc,"reference labels")
 assert listing.count(LABELS[loc][10]+" · G")==8,(loc,"reference badges localized")
 urls=re.findall(r'<a\b(?=[^>]*\bdata-product-card\b)[^>]*\bhref="([^"]+)"',listing)
 assert len(set(urls))==101,loc
 assert [u.rsplit("/",2)[1] for u in urls[:16]][:8]==[f"lo-{i:03d}" for i in range(1,9)]
 assert [u.rsplit("/",2)[1] for u in urls[8:16]]==[p["slug"] for p in GALLERY]
 for p in GALLERY:
  f=ROOT/"dist"/prefix/"products"/p["slug"]/"index.html"
  assert f.is_file(),(loc,p["model"])
  text=f.read_text(encoding="utf8")
  assert p["locales"][loc] in text
  assert all(label in text for label in LABELS[loc][7:10]),(loc,p["model"],"localized parameter headings")
  assert p["model"] in text
  assert len(re.findall(r'data-main-photo=',text))==len(p["images"])
  assert 'id="material-performance"' in text
  assert "BPA-free certified" not in text and "100°C rated" not in text
  assert all(im in text for im in p["images"])
  assert 'rel="canonical"' in text and 'hreflang="'+loc+'"' in text
  assert 'noindex,nofollow' in text
site=json.loads((ROOT/"deployment/site.config.json").read_text(encoding="utf8"))
assert site["site"]["indexingApproved"] is False
urls=(ROOT/"dist/sitemap.xml").read_text(encoding="utf8")
assert urls.count("<loc>")==755
for p in GALLERY:
 for loc in lang:
  u=("https://xuyibottles.com/"+("" if loc=="en" else loc+"/")+"products/"+p["slug"]+"/")
  assert u in urls,u
for group in GALLERY:
 assert group["model"] in SERIES and SERIES[group["model"]]["galleryReference"] is True
print("XUYI_GALLERY_REFERENCE_LAUNCH_PASSED 8 photo references, 24 R2 assets, 5 languages, no fake factory specifications")