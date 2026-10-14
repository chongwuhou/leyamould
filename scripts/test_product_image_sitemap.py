#!/usr/bin/env python3
"""Existing sitemap receives ONLY accurate, stable source-backed main photos.

Validate all emitted URLs match the post-build public product pages, including
the six human-approved shaker HD aliases. No new sitemap, R2 rename or stale
D1 image overrides; later editor-selected images win.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import sys, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from site_renderer import SERIES,SITE_ORIGIN
from product_image_sitemap import (IMAGE_NAMESPACE,image_path,source_main_photo,
    image_for_product_route,xml_image_for_product,approved_shaker_image_aliases)
from sitemap_modification import source_lastmod
DIST=ROOT/"dist"
NS="{http://www.sitemaps.org/schemas/sitemap/0.9}"
IMG="{"+IMAGE_NAMESPACE+"}"
class MainPhoto(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.src=None
    def handle_starttag(self,tag,attrs):
        attributes=dict(attrs)
        if tag=="img" and attributes.get("id")=="main-photo" and self.src is None:
            self.src=attributes.get("src")

tree=ET.parse(DIST/"sitemap.xml")
urls=list(tree.getroot())
assert len(urls)>=755, "At least the existing sitemap's routes must remain"
count=0
english=localized=shared=0
for item in urls:
    url=item.find(NS+"loc").text
    assert url.startswith(SITE_ORIGIN+"/"),url
    local_path=url.removeprefix(SITE_ORIGIN)
    children=item.findall(IMG+"image")
    for image in children:
        assert len(image)==1 and image[0].tag==IMG+"loc","No deprecated image fields"
        assert urlsplit(image[0].text).netloc=="xuyibottles.com",image[0].text
        assert image_path(image[0].text)==image[0].text.removeprefix(SITE_ORIGIN)
    route=local_path
    for lang in ("es","pt","ru","tr"):
        prefix="/"+lang+"/"
        if local_path.startswith(prefix):
            route="/"+local_path[len(prefix):]
            break
    if not route.startswith("/products/") or route.count("/")!=3:
        assert not children,(url,"Image sitemap is deliberately scoped to product main photos")
        continue
    assert len(children)==1,(url,"Every published model must have one main photo")
    doc=(DIST/local_path.lstrip("/")/"index.html").read_text(encoding="utf8")
    parser=MainPhoto();parser.feed(doc)
    assert parser.src,(url,"missing visible main product photo")
    expected=SITE_ORIGIN+parser.src
    assert children[0][0].text==expected,(url,children[0][0].text,expected)
    if route==local_path:english+=1
    else:localized+=1
    count+=1
assert english>=101 and localized>=404,(english,localized)
assert len(approved_shaker_image_aliases())==6
assert image_for_product_route("/products/2095/",SERIES)=="/media/gallery/2095-01.webp"
assert image_for_product_route("/products/2100/",SERIES)=="/media/gallery/2099-01.webp"
assert image_for_product_route("/products/5247/",SERIES)=="/assets/sku-hd/slide-096-gpt-reviewed-20261013.webp"
# The source path does not mutate between rebuilds, and repeated calls are
# deterministic. Shared image URLs stay shared, without unique-SKU fiction.
for code in ("2095","2099","2100","5247","g-02"):
    route="/products/"+code+"/"
    x=xml_image_for_product(route,SERIES)
    assert x==xml_image_for_product(route,SERIES)
    assert x.count("<image:image>")==1 and x.count("<image:loc>")==1
# Simulated D1 admin change of localized product main image:
owner='<article><img id="main-photo" alt="Owner reviewed" src="/media/gallery/owner-new-2095.webp"></article>'
new=xml_image_for_product("/products/2095/",SERIES,owner)
assert SITE_ORIGIN+"/media/gallery/owner-new-2095.webp" in new
assert SITE_ORIGIN+"/media/gallery/2095-01.webp" not in new
assert xml_image_for_product("/products/2095/",SERIES,owner)==new
assert source_main_photo(SERIES["2095"],'<p>Editor removed the primary photo</p>') is None
assert xml_image_for_product("/products/2095/",SERIES,'<p>No product photograph</p>')==""
assert image_path("https://other.example/photo.webp") is None
assert image_path("/media/gallery/2095-01.webp?v=20261014") is None
assert image_path("/media/../secret.webp") is None
assert image_path("/media/gallery/2095-01.webp")=="/media/gallery/2095-01.webp"
# Future D1-approved SKU or locale follows the same source component.
future={**SERIES["2095"],"model":"TEST-NEW","slug":"future-photo-model",
        "images":["/media/gallery/future-approved.webp"]}
extra={**SERIES,"future-photo-model":future}
assert image_for_product_route("/products/future-photo-model/",extra)=="/media/gallery/future-approved.webp"
assert source_lastmod("/products/2095/")=="2026-10-14"
assert not (DIST/"sitemap-images.xml").exists(), "No separate sitemap was requested"
print("XUYI_EXISTING_IMAGE_SITEMAP_SOURCE_PASSED",count,"images",english,"EN",localized,"localized",len(urls),"URLs")