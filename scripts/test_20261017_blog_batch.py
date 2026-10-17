#!/usr/bin/env python3
"""Editorial quality and owner-source contract for three October 17 XUYI blogs."""
import html,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from site_renderer import SERIES
from sitemap_modification import source_lastmod
from scripts.prepare_blog_release_20261017 import GUIDES,MATRICES,TRANS,SLUGS,LOCALES
models={str(x["slug"]) for x in SERIES.values()}
covers=[]
for slug in SLUGS:
 post=GUIDES[slug]
 assert source_lastmod("/blog/"+slug+"/")=="2026-10-17"
 assert len(post["related"])==3 and len(set(post["related"]))==3
 assert all(item!=slug and item in GUIDES for item in post["related"])
 assert len(post["product_notes"])==3
 assert len({note["sku"] for note in post["product_notes"]})==3
 assert all(note["sku"] in models for note in post["product_notes"])
 assert len(post["faqs"])==4 and len(post["sections"])==7
 assert len(post["intro"].split())+sum(len(v["paragraph"].split()) for v in post["sections"])>=600
 assert post["cover"].startswith("/assets/blog/") and (ROOT/"dist"/post["cover"].lstrip("/")).is_file()
 covers.append(post["cover"])
 assert len(MATRICES[slug]["rows"])>=6
 for locale in ["en",*LOCALES]:
  dest=ROOT/"dist"/("" if locale=="en" else locale)/"blog"/slug/"index.html"
  assert dest.is_file(),dest
  body=dest.read_text(encoding="utf8")
  main=body.split('<main id="main-content">',1)[1].split("</main>",1)[0]
  prefix="" if locale=="en" else "/"+locale
  assert main.count('class="blog-editorial__product-link"')==3,(locale,slug)
  assert main.count('class="blog-related__item"')==3,(locale,slug)
  assert main.count('class="blog-buyer-matrix"')==1,(locale,slug)
  assert main.count("<details>")==4,(locale,slug)
  assert all('href="'+prefix+'/products/'+note["sku"]+'/"' in main for note in post["product_notes"]),(locale,slug)
  assert all('href="'+prefix+'/blog/'+related+'/"' in main for related in post["related"]),(locale,slug)
  assert 'hreflang="es"' in body and 'hreflang="x-default"' in body
  assert '<meta property="og:image" content="https://xuyibottles.com'+post["cover"]+'"' in body
  if locale!="en":
   translated=TRANS[slug][locale]
   assert html.escape(translated["title"]) in main,(locale,slug,"title untranslated")
   for i in range(7):
    assert html.escape(translated[f"sections.{i}.heading"]) in main,(locale,slug,i)
   assert translated["intro"]!=post["intro"]
   assert all(len(translated[f"sections.{i}.paragraph"])>120 for i in range(7))
assert len(set(covers))==3
for locale in LOCALES:
 page=(ROOT/"dist"/locale/"blog"/"index.html").read_text(encoding="utf8")
 for slug in SLUGS:
  assert '/'+locale+'/blog/'+slug+'/' in page
  assert html.escape(TRANS[slug][locale]["title"]) in page
assert source_lastmod("/blog/")=="2026-10-17"
print("XUYI_20261017_THREE_BLOGS_FIVE_LOCALES_EDITORIAL_SEO_PASSED")
