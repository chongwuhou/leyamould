#!/usr/bin/env python3
"""Audit every actual XUYI <img> in five languages plus reviewed D1 ALT flow."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import json,re,sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from media_alt_render import apply_media_alts,approved_alts
from image_alt_quality import readable_alt
DIST=ROOT/"dist"

class ImageTags(HTMLParser):
    def __init__(self):super().__init__();self.images=[]
    def handle_starttag(self,tag,attrs):
        if tag=="img":self.images.append(dict(attrs))

counts=Counter()
for file in DIST.rglob("*.html"):
    if "admin" in file.relative_to(DIST).parts:continue
    parser=ImageTags()
    parser.feed(file.read_text(encoding="utf-8"))
    for item in parser.images:
        counts["total"]+=1
        if "alt" not in item:counts["missing"]+=1
        value=item.get("alt","")
        if not value.strip():counts["empty"]+=1
        if re.search(r"[\u4e00-\u9fff]",value):counts["untranslated_cjk"]+=1
        if re.search(r"(?i)(?:view|visualizar|вид|görünüm)\s+1\b",value):
            counts["unhelpful_gallery_view"]+=1
        if value.count("2506")>1:counts["duplicated_sku"]+=1
        if len(value)>180:counts["editorial_over_180"]+=1
assert counts["total"]>10000,counts
for key in ("missing","empty","untranslated_cjk","unhelpful_gallery_view","duplicated_sku"):
    assert counts[key]==0,(key,counts[key])

image='<img src="/media/product/0123456789abcdef0123456789abcdef.webp" alt="Original product-specific photo" loading="lazy">'
state={"mediaAlts":[{"path":"/media/product/0123456789abcdef0123456789abcdef.webp",
 "translations":{"en":"550 ml plastic sports water bottle model 2501, product photo",
                 "es":"Botella deportiva de plástico de 550 ml, modelo 2501"}}]}
assert 'alt="550 ml plastic sports water bottle model 2501, product photo"' in apply_media_alts(image,state,"en")
assert 'alt="Botella deportiva de plástico de 550 ml, modelo 2501"' in apply_media_alts(image,state,"es")
assert apply_media_alts(image,state,"tr")==image, "Never show English as fabricated Turkish translation"
assert apply_media_alts('<img src="/media/excel/row-003.webp" alt="Existing variant title">',state,"en").endswith('alt="Existing variant title">')
legacy={"mediaAlts":[{"path":"/media/ppt/slide-059.webp","translations":{
 "en":"Plastic water bottle collection from source catalog"}}]}
assert 'Plastic water bottle collection from source catalog' in apply_media_alts(
 '<img src="/media/ppt/slide-059.webp" alt="Old generic title">',legacy,"en")
assert 'Transparent Variant' in readable_alt("Model 2306透明款 plastic bottle","en")
assert "variante transparente" in readable_alt("Modelo 2306透明款","es")
assert readable_alt("Plastic Sports Water Bottle Model 2506 model 2506","en").count("2506")==1
try:approved_alts({"mediaAlts":[{"path":"/media/product/good.webp",
 "translations":{"en":"<img src=x onerror=alert(1)>"}}]})
except ValueError:pass
else:raise AssertionError("Malformed reviewed ALT must be rejected")
print("XUYI_IMAGE_ALT_SEO_PASSED",dict(counts),"and D1 5-locale image metadata rendering")