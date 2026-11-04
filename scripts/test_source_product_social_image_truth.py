#!/usr/bin/env python3
"""No Excel screenshot as Product.image, OG or Google image-sitemap photo.

Test source-generated 5-language details for reviewed factory products,
English-only fallback for unsupported sources, CMS owner precedence, and repeat rendering.
"""
from pathlib import Path
import copy
import json
import re
import sys
import os

ROOT=Path(__file__).resolve().parent.parent
snapshot=ROOT/"_local_ops"/"build-snapshot.json"
if snapshot.is_file():
    os.environ["XUYI_BUILD_SNAPSHOT"]=str(snapshot)
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from site_renderer import SERIES,SITE_ORIGIN
from product_share_source import CATEGORY_PREVIEWS,real_product_images,social_path,add_social_head
from product_image_sitemap import image_path,xml_image_for_product
from product_content import add_schema
from factory_product_locales import SOURCE_DOCUMENTS as FACTORY_SOURCE_DOCUMENTS

assert len(CATEGORY_PREVIEWS)==4
for category,src in CATEGORY_PREVIEWS.items():
    p=ROOT/src.lstrip("/")
    assert p.is_file() and 10000<p.stat().st_size<500000,(category,src)

dist=ROOT/"dist"
total=0
unverified=0
verified=0
langs=("","es","pt","ru","tr")
for entry in SERIES.values():
    model=entry["slug"]
    photos=real_product_images(entry)
    fallback=not photos
    if fallback:unverified+=1
    else:verified+=1
    selected=social_path(entry)
    if fallback:assert selected==CATEGORY_PREVIEWS[entry["category"]]
    else:assert selected==photos[0]
    source_generated=bool(entry.get("manualNew") and entry.get("sourceDocument") in FACTORY_SOURCE_DOCUMENTS)
    source_only=bool(entry.get("manualNew") and entry.get("sourceDocument") and not source_generated)
    if source_only:
        assert (dist/"products"/model/"index.html").is_file(),model
        for locale in ("es","pt","ru","tr"):
            assert not (dist/locale/"products"/model/"index.html").exists(),(locale,model)
    if source_generated:
        for locale in ("es","pt","ru","tr"):
            assert (dist/locale/"products"/model/"index.html").is_file(),(locale,model,"reviewed factory translation missing")
    for locale in langs:
        if locale and source_only:
            continue
        route=("/"+locale if locale else "")+"/products/"+model+"/"
        path=dist/route.lstrip("/")/"index.html"
        assert path.is_file(),route
        doc=path.read_text(encoding="utf8")
        head=doc.split("</head>",1)[0]
        og=re.findall(r'<meta property="og:image" content="([^"]+)"',head)
        twitter=re.findall(r'<meta name="twitter:image" content="([^"]+)"',head)
        assert len(og)==1 and twitter==og,(locale,model,"duplicate/missing social")
        assert og[0]==SITE_ORIGIN+selected,(locale,model,og,selected)
        assert "/excel/" not in og[0]
        product=[]
        for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',head,re.S):
            j=json.loads(raw)
            product.extend(x for x in j.get("@graph",[j]) if x.get("@type")=="Product")
        assert len(product)==1,(locale,model)
        images=product[0].get("image",[])
        assert images==[SITE_ORIGIN+x for x in photos],(locale,model,images,photos)
        assert all("/excel/" not in x for x in images)
        total+=1

assert total>=505 and unverified and verified
# A CMS owner uploading a genuine model-specific asset changes both source
# schema and OG the very next rebuild; the old Excel photo stays available
# in body for catalog reference without being elevated to Product.image.
changed=copy.deepcopy(SERIES["2106"])
owned="/media/product/owner-selected-2106.webp"
changed["images"]=[owned]+changed["images"]
assert real_product_images(changed)[0]==owned
base='<html><head><title>Owner image test</title></head><body></body></html>'
schema=add_schema(base,changed)
assert SITE_ORIGIN+owned in schema and "/media/excel/" not in schema
updated=add_social_head(schema,changed)
assert '<meta property="og:image" content="'+SITE_ORIGIN+owned+'">' in updated
assert add_social_head(updated,changed)==updated

# D1 owner-selected OG assets must survive even when they differ from
# source Product.image; only old Excel screenshots are force-downgraded.
own_og=SITE_ORIGIN+"/media/product/owner-special-social-2106.webp"
overridden=base.replace("</head>",'<meta property="og:image" content="'+own_og+'"></head>')
assert own_og in add_social_head(overridden,SERIES["2106"])
assert add_social_head(add_social_head(overridden,SERIES["2106"]),SERIES["2106"])==add_social_head(overridden,SERIES["2106"])

old_excel=base.replace("</head>",'<meta property="og:image" content="'+SITE_ORIGIN+'/media/excel/row-042.webp"></head>')
assert "/excel/" not in add_social_head(old_excel,SERIES["2106"]).split("</head>",1)[0]
assert image_path("/media/excel/row-042.webp") is None
assert "/media/excel/" not in xml_image_for_product("/products/2106/",SERIES)

future=copy.deepcopy(SERIES["2106"])
future["slug"]="future-uncaptured-image-model"
future["model"]="future-uncaptured-image-model"
future["images"]=["/media/excel/row-999.webp"]
assert social_path(future)==CATEGORY_PREVIEWS[future["category"]]
assert not real_product_images(future)
future["images"]=["/media/product/future-owner-verified.webp"]+future["images"]
assert social_path(future)=="/media/product/future-owner-verified.webp"

tree=ET.parse(dist/"sitemap.xml")
img_ns="{http://www.google.com/schemas/sitemap-image/1.1}"
image_count=0
for item in tree.getroot():
    for img in item.findall(img_ns+"image"):
        link=img.find(img_ns+"loc")
        assert link is not None and "/excel/" not in (link.text or ""),link.text if link is not None else None
        image_count+=1
assert image_count>=100,image_count
assert "apply_product_share_images(DIST)" not in (ROOT/"scripts/build_release.py").read_text(encoding="utf8")
print("XUYI_SOURCE_SOCIAL_IMAGE_TRUTH_CMS_OWNER_LOCALE_SITEMAP_PASSED",
      "products",len(SERIES),"locale_pages",total,"model_images",verified,
      "category_preview_only",unverified,"sitemap_images",image_count)