#!/usr/bin/env python3
"""P0: real sitemap dates, concise title, SKU-distinct H1 and source-based media ALT."""
from pathlib import Path
from html import unescape
from collections import Counter
import os,sys,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent
SNAPSHOT=ROOT/"_local_ops"/"build-snapshot.json"
if SNAPSHOT.is_file():os.environ["XUYI_BUILD_SNAPSHOT"]=str(SNAPSHOT)
sys.path.insert(0,str(ROOT))
from site_renderer import SERIES,BUILD_STATE
from factory_product_locales import SOURCE_DOCUMENTS
from catalog_extensions import is_factory_catalog_source_default
from product_source_identity import source_product_identity,main_image_alt,matches_owner_field
from sitemap_modification import source_lastmod,BASELINE,review_change_dates
from scripts.source_catalog_capacity_oz import new_seo,catalog_volume_numbers,verified_source_material,source_field_allowed,product_h1_text,verified_source_color_term
DIST=ROOT/"dist"
D1_PRODUCT_SEO={(str(row.get("slug") or ""),str(row.get("locale") or "")):row
                for row in BUILD_STATE.get("productSeo",[]) if isinstance(row,dict)}
D1_PRODUCTS={str(row.get("model") or "").lower():row.get("content",{})
             for row in BUILD_STATE.get("products",[]) if isinstance(row,dict)}
REVIEW_DATE_CHANGES=review_change_dates(SERIES,BUILD_STATE.get("productReviews",[]))
ns="{http://www.sitemaps.org/schemas/sitemap/0.9}"
root=ET.parse(DIST/"sitemap.xml").getroot()
urls=list(root)
assert len(urls)>=755
dates=0
expected_dates=0
for item in urls:
    url=item.find(ns+"loc").text
    assert url.startswith("https://xuyibottles.com/")
    path=url.removeprefix("https://xuyibottles.com")
    date=item.find(ns+"lastmod")
    revision=next((x for x in BUILD_STATE.get("pages",[]) if x.get("route")==path),None)
    expected=source_lastmod(path,"en",revision,review_dates=REVIEW_DATE_CHANGES)
    assert (date.text if date is not None else None)==expected,(path,expected)
    if expected is not None:expected_dates+=1
    if date is not None:dates+=1
# Some valid routes (privacy/legal pages and source-new catalog pages) have no
# authoritative source date. Require exact source-backed coverage, not an
# arbitrary near-100% threshold that rejects legitimate undated routes.
assert dates==expected_dates,(dates,expected_dates,len(urls))
assert source_lastmod("/products/brand-new-model/") is None
assert source_lastmod("/privacy-policy/") is None
assert source_lastmod("/products/2095/")=="2026-10-20"

owners=Counter(row["images"][0] for row in SERIES.values())
seen_langs={}
for loc in ("en","es","pt","ru","tr"):
    path_prefix="" if loc=="en" else loc+"/"
    all_h1=[]
    all_main={}
    for row in SERIES.values():
        # Approved PDF/PPT source models now have native, source-generated
        # detail pages in all five languages. Unknown future source documents
        # remain English-only until added to the reviewed locale renderer.
        if loc!="en" and row.get("manualNew") and row.get("sourceDocument") and row.get("sourceDocument") not in SOURCE_DOCUMENTS:
            continue
        slug=row["slug"]
        route=DIST/path_prefix/"products"/slug/"index.html"
        assert route.is_file(),route
        doc=route.read_text(encoding="utf8")
        title=unescape(re.search(r"<title>(.*?)</title>",doc,re.S).group(1))
        # A D1 product-SEO row or a genuinely edited product-content field is
        # authoritative, even when its title is longer than the 60-char source target.
        # Otherwise, source defaults for this 58-SKU batch must use concise verified SEO.
        product_seo=D1_PRODUCT_SEO.get((slug,loc))
        product_content=D1_PRODUCTS.get(str(row.get("model") or "").lower(),{})
        source_seo_allowed=source_field_allowed(loc,row,"title",BUILD_STATE)
        owner_title=(product_seo or {}).get("seoTitle")
        if not owner_title and product_content.get("seoTitle"):
            if not is_factory_catalog_source_default(row.get("model"),product_content,"seoTitle"):
                owner_title=product_content["seoTitle"]
        if owner_title and not source_seo_allowed:
            assert title==owner_title,(loc,slug,"D1/product owner SEO overwritten",title,owner_title)
            assert len(title)<=90,(loc,slug,"owner SEO exceeds product metadata limit",len(title),title)
        else:
            assert len(title)<=(60 if catalog_volume_numbers(row) else 90),(loc,slug,len(title),title)
        h1=re.search(r"<h1[^>]*>(.*?)</h1>",doc,re.S)
        assert h1,(loc,slug,"missing H1")
        heading=unescape(re.sub(r"<[^>]+>"," ",h1.group(1))).strip()
        assert heading,(loc,slug,"empty H1")
        color=verified_source_color_term(loc,row)
        if color and (row.get("sourceDocument") in SOURCE_DOCUMENTS or heading==product_h1_text(loc,row)):
            assert color.casefold() in heading.casefold(),(loc,slug,"verified source color missing from H1",color,heading)
        all_h1.append(heading)
        if loc=="en" and row["images"][0]=="/media/gallery/2095-01.webp":
            assert "2095" in heading
        image=re.search(r'<img\\b(?=[^>]*\\bid="main-photo")[^>]*>',doc,re.I)
        if image:
            src=re.search(r'\\bsrc="([^"]+)"',image.group(0))
            alt=re.search(r'\\balt="([^"]*)"',image.group(0))
            if src and alt:
                imgpath=src.group(1)
                description=unescape(alt.group(1))
                assert description,(loc,slug,"empty alt")
                all_main.setdefault(imgpath,set()).add(description)
                if owners.get(imgpath,0)>1 and imgpath in (r["images"][0] for r in SERIES.values()):
                    assert "product photograph" not in description or str(row["model"]) not in description,(loc,slug,description)
        if loc=="en" and slug=="2095":
            # Actual 500ml + reviewed 16.9 oz retail class now take precedence
            # over listing all component resins in the concise search title.
            assert '500ml' in title and "16.9 oz" in title and "2095" in title
            assert "PP/PC" in doc
    assert len(all_h1)==len(set(all_h1)),(loc,len(set(all_h1)),len(all_h1))
    seen_langs[loc]={"products":len(all_h1),"distinctH1":len(set(all_h1))}
expected_products=sum(
    1 for row in SERIES.values()
    if not (row.get("manualNew") and row.get("sourceDocument") and row.get("sourceDocument") not in SOURCE_DOCUMENTS)
)
for loc in ("en","es","pt","ru","tr"):
    assert seen_langs[loc]["products"]==expected_products,(loc,seen_langs[loc],expected_products)
# A later CMS editor can replace both image alt and heading on a known D1
# product without a source fallback changing either of those fields.
row=SERIES["2095"]
custom='<h1>Owner selected product headline</h1><img id="main-photo" src="/media/gallery/2095-01.webp" alt="Owner describes the unique photograph" loading="eager">'
assert source_product_identity(custom,row,"es",owners)==custom
future={**row,"model":"FUTURE-995","slug":"future-model-995","images":["/media/gallery/future-model-995-01.webp"]}
source='<h1>500ml Plastic Sports Water Bottle</h1><img id="main-photo" src="/media/gallery/future-model-995-01.webp" alt="500ml Plastic Sports Water Bottle model FUTURE-995">'
changed=source_product_identity(source,future,"en",Counter({future["images"][0]:1}))
assert "FUTURE-995" in changed and "PP/PC" in changed and changed!=source
print("XUYI_SOURCE_SITEMAP_TITLES_H1_IMAGES_PASSED",dates,len(urls),seen_langs)
