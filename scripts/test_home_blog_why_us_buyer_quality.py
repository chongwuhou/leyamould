#!/usr/bin/env python3
"""P0 source-only homepage CLS hints, blog/model bridges and Why Us QA."""
from pathlib import Path
from html.parser import HTMLParser
from html import unescape
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from home_source_image_geometry import source_image_geometry,KNOWN
from why_us_source import augment,DATA,LOCALE_BASELINES
from site_renderer import SERIES
SNAP=json.loads((ROOT/"_local_ops/build-snapshot.json").read_text(encoding="utf8"))
D1={(x["resourceId"][5:],x["locale"]):x["content"] for x in SNAP["translations"]
 if x.get("resourceId","").startswith("page:")}
LANGS=("en","es","pt","ru","tr")
class Parse(HTMLParser):
 def __init__(self):super().__init__();self.images=[];self.links=[]
 def handle_starttag(self,t,attrs):
  d=dict(attrs)
  if t=="img":self.images.append(d)
  if t=="a":self.links.append(d.get("href",""))
# The source builder (not dist rewrites) reserves every homepage image.
for loc in LANGS:
 page=(ROOT/"dist"/("" if loc=="en" else loc)/"index.html").read_text(encoding="utf8")
 h=Parse();h.feed(page)
 assert len(h.images)>=65,(loc,len(h.images))
 assert all(("width" in x and "height" in x) or "aspect-ratio:" in x.get("style","") for x in h.images),(loc,"unreserved image")
 for x in h.images:
  src=x.get("src")
  if src in KNOWN:
   expected=[str(v) for v in KNOWN[src]]
   assert [x.get("width"),x.get("height")]==expected,(loc,src,"bad verified image size")
 assert "width=" in page
# Current user edits to image URLs must never be replaced by a historic URL.
original='<div><img src="/assets/curated-hd/gradient-sports.webp" alt="bottle"></div>'
assert source_image_geometry(original,"/","en")==source_image_geometry(source_image_geometry(original,"/","en"),"/","en")
change='<img src="/media/editor/new-owner-image.webp" alt="owner-selected">'
owner=source_image_geometry(change,"/","en")
assert 'src="/media/editor/new-owner-image.webp"' in owner and ' width=' not in owner and 'aspect-ratio:' in owner
sized='<img src="/assets/curated-hd/gradient-sports.webp" width="800" height="900">'
assert source_image_geometry(sized,"/","en")==sized
assert source_image_geometry(original,"/blog/","en")==original
assert source_image_geometry('<img src="/editor-owned/new.webp">',"/","en")=='<img src="/editor-owned/new.webp">'
# Blog link acceptance now belongs to strict per-article paragraph-and-end checks.
# This is deliberately NOT a whole-page anchor count or an intro-only callout.
from blog_editorial_inline import POSTS as EDITED_GUIDES
assert len(EDITED_GUIDES)==16
for slug,notes in EDITED_GUIDES.items():
 assert len(notes)==2
 for loc in LANGS:
  root=ROOT/"dist"/("" if loc=="en" else loc)
  page=(root/"blog"/slug/"index.html").read_text(encoding="utf8")
  main=page.split('<main id="main-content">',1)[1].split("</main>",1)[0]
  sections=re.findall(r'<section class="blog-section"[^>]*>.*?</section>',main,re.S)
  assert len(sections)==6
  assert all(sections[n["section"]].count('data-editorial-model="'+n["sku"]+'"')==1 for n in notes)
  assert main.count('class="section section--soft blog-related"')==1
  assert 'class="blog-product-proof"' not in main

# Why Us: verified source, complete buyer decision content, all 5 locales.
for loc in LANGS:
 page=(ROOT/"dist"/("" if loc=="en" else loc)/"why-us/index.html").read_text(encoding="utf8")
 body=page.split('<main id="main-content">',1)[1].split('</main>',1)[0]
 assert body.count('id="supplier-comparison-evidence"')==1,loc
 assert DATA[loc]["heading"] in unescape(body)
 assert body.count('class="xuyi-why-explainer"')==3
 assert body.count("<dt>")>=6
 words=len(re.sub(r'<[^>]+>',' ',body).split())
 if loc=="en":assert words>=800,words
 if loc!="en":
  orig=D1[("/why-us/",loc)]["mainHtml"]
  assert hashlib.sha256(orig.encode()).hexdigest()==LOCALE_BASELINES[loc]
  assert augment(orig,loc)!=orig
  user=orig+"<p>Owner approved supplier description.</p>"
  assert augment(user,loc)==user
 else:
  original="<section class=\"rs-footer-cta\"></section>"
  assert augment(original,"en")!=original
  owner=original+"<p>Owner approved.</p>"
  assert augment(owner,"en",owner_override=True)==owner
 assert augment(body,loc)==body
assert augment("<p>A new locale body</p>","it")=="<p>A new locale body</p>"
assert augment("<p>A new Why Us from CMS</p>","es")=="<p>A new Why Us from CMS</p>"
print("XUYI_HOME_65_IMAGES_BLOG16X5_PRODUCT_LINKS_WHYUS5_CMS_OWNER_SOURCE_PASSED")