#!/usr/bin/env python3
"""Proof that new high-resolution imagery is only used in generic components."""
import json,re,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
dist=ROOT/"dist"
manifest=json.loads((ROOT/"data/curated-hd-manifest.json").read_text(encoding="utf8"))
items=manifest["assets"]
assert len(items)==4
approved=[item["target"] for item in items]
assert len(set(approved))==4
for item in items:
 p=ROOT/item["target"].lstrip("/")
 raw=p.read_bytes()
 assert raw[:4]==b"RIFF" and raw[8:12]==b"WEBP"
 assert 10000<len(raw)<650000
 assert min(item["sourceDimensions"])>=1000
 assert "do not use as an identified product model" in item["restrictions"]
main_sources={
 "gradient-sports":"/assets/curated-hd/gradient-sports.webp",
 "feature-flip-top":"/assets/curated-hd/feature-flip-top.webp",
 "outdoor-lifestyle":"/assets/curated-hd/outdoor-lifestyle.webp",
 "customizable-assortment":"/assets/curated-hd/customizable-assortment.webp"
}
checked=0
for locale in ("", "es", "pt", "ru", "tr"):
 name=f"/{locale}/" if locale else "/"
 page=(dist/locale/"index.html" if locale else dist/"index.html")
 html=page.read_text(encoding="utf8")
 for src in approved:
  assert html.count(src)>=1,(name,"Missing managed HQ menu/hero image",src)
  assert (dist/src.lstrip("/")).is_file(),(name,"missing local image asset",src)
 banner=re.search(r'<script type="application/json" id="xuyi-home-banners">([^<]+)</script>',html)
 assert banner,("Missing approved homepage banner settings",name)
 expected=json.loads(banner.group(1))[0]["img"]
 assert re.search(r'<img\b(?=[^>]*\bid="hero-image")(?=[^>]*\bsrc="'+re.escape(expected)+r'")[^>]*>',html),(name,"First-frame image differs from the D1 approved banner")
 assert "src=\"/media/ppt/slide-091.webp\" id=\"hero-image\"" not in html
 checked+=1
# Original catalog model photos must be unchanged. New images are exclusively
# in common header and homepage, never in the details section of a model.
for model_page in dist.glob("products/*/index.html"):
 text=model_page.read_text(encoding="utf8")
 main=text.split('<main id="main-content">',1)[1].split("</main>",1)[0]
 assert not any(src in main for src in approved),(str(model_page),"new marketing image used as identified model")
 checked+=1
for lang in ("es","pt","ru","tr"):
 for model_page in (dist/lang/"products").glob("*/index.html"):
  text=model_page.read_text(encoding="utf8")
  main=text.split('<main id="main-content">',1)[1].split("</main>",1)[0]
  assert not any(src in main for src in approved),(str(model_page),"marketing image replaced model photo")
  checked+=1
site_js=(dist/"assets/site.js").read_text(encoding="utf8")
for src in (main_sources["gradient-sports"],main_sources["outdoor-lifestyle"],main_sources["customizable-assortment"]):
 assert src in site_js,("JS slideshow missing high resolution asset",src)
print("XUYI_HIGH_RESOLUTION_IMAGE_TESTS_PASSED","assetCount",len(items),"pagesChecked",checked)