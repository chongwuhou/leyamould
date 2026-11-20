#!/usr/bin/env python3
"""Source-rendered product, FAQ, breadcrumb and crawlable ItemList schema gate."""
import json
import re
import sys
import os
from pathlib import Path
from copy import deepcopy

ROOT=Path(__file__).resolve().parent.parent
SNAPSHOT=ROOT/"_local_ops"/"build-snapshot.json"
if SNAPSHOT.is_file():os.environ["LEYA_BUILD_SNAPSHOT"]=str(SNAPSHOT)
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"scripts"))

from seo_structured_components import visible_faq,actual_product_cards,add_at_render,PROPERTY
from source_catalog_capacity_oz import (
    verified_source_material,current_baseline,pre_render_verified_meta,
    catalog_volume_numbers,volume_terms,format_ml,new_seo,product_h1_text
)
from site_renderer import SERIES,CAT
from cms_seo_curation_guard import snapshot

D=ROOT/"dist"
ORIGIN="https://leyamould.com"
owner=snapshot()
assert owner and owner["site"]=="leyamould"
countfaq=countlists=countproducts=countmaterials=0

def schema_nodes(page):
    result=[]
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',page,re.S):
        value=json.loads(raw)
        if isinstance(value,dict) and isinstance(value.get("@graph"),list):
            result.extend(node for node in value["@graph"] if isinstance(node,dict))
        elif isinstance(value,dict):
            result.append(value)
    return result

for lang in ("en","es","pt","ru","tr"):
    prefix="" if lang=="en" else lang+"/"
    for obj in SERIES.values():
        route="/"+prefix+"products/"+obj["slug"]+"/"
        file=D/route.lstrip("/")/"index.html"
        assert file.is_file(),(lang,obj["slug"],"missing localized detail")
        page=file.read_text(encoding="utf8")
        nodes=schema_nodes(page)
        products=[node for node in nodes if node.get("@type")=="Product"]
        webpages=[node for node in nodes if node.get("@type")=="WebPage"]
        breadcrumbs=[node for node in nodes if node.get("@type")=="BreadcrumbList"]
        assert len(products)==1,(lang,obj["slug"],"Product schema",len(products))
        assert len(webpages)==1,(lang,obj["slug"],"WebPage schema",len(webpages))
        assert len(breadcrumbs)==1,(lang,obj["slug"],"BreadcrumbList schema",len(breadcrumbs))
        product=products[0]
        canonical=ORIGIN+route
        assert product.get("url")==canonical,(lang,obj["slug"],product.get("url"))
        assert product.get("sku")==str(obj["model"]),(lang,obj["slug"],product.get("sku"))
        if product.get("name")==product_h1_text(lang,obj):
            assert str(obj["model"]).replace("透明款","") in product.get("name",""),(lang,obj["slug"],product.get("name"))
        assert product.get("brand",{}).get("name")=="XUYI Bottles"
        assert "offers" not in product,(lang,obj["slug"],"no unverified price/stock")
        assert product.get("potentialAction",{}).get("@type")=="CommunicateAction"
        assert product["potentialAction"]["target"]["urlTemplate"].startswith(ORIGIN+"/")
        assert webpages[0].get("inLanguage")==lang
        assert webpages[0].get("mainEntity")=={"@id":product.get("@id")}
        assert breadcrumbs[0].get("itemListElement")
        assert breadcrumbs[0]["itemListElement"][-1].get("item")==canonical
        props={item.get("name"):str(item.get("value","")) for item in product.get("additionalProperty",[]) if isinstance(item,dict)}
        numbers=catalog_volume_numbers(obj)
        if numbers:
            assert PROPERTY[lang]["capacity"] in props,(lang,obj["slug"],props)
            assert PROPERTY[lang]["oz"] in props,(lang,obj["slug"],props)
            for number in numbers:
                assert format_ml(number) in props[PROPERTY[lang]["capacity"]],(lang,obj["slug"],number)
            assert volume_terms(numbers,lang) in props[PROPERTY[lang]["oz"]],(lang,obj["slug"],props)
        material=verified_source_material(obj)
        if material:
            assert PROPERTY[lang]["material"] in props,(lang,obj["slug"],props)
            assert material in props[PROPERTY[lang]["material"]],(lang,obj["slug"],material,props)
            countmaterials+=1

        values=visible_faq(page)
        faqs=[node for node in nodes if node.get("@type")=="FAQPage"]
        assert len(faqs)==int(bool(values)),(lang,obj["slug"],"visible FAQ/schema mismatch",values)
        if values:
            entity=faqs[0]
            assert entity.get("inLanguage")==lang
            assert [item["name"] for item in entity["mainEntity"]]==[q for q,a in values]
            assert [item["acceptedAnswer"]["text"] for item in entity["mainEntity"]]==[a for q,a in values]
            countfaq+=1
        assert add_at_render(page,route,lang)==page,(lang,obj["slug"],"schema renderer not idempotent")

        title=re.search(r"<title>(.*?)</title>",page).group(1)
        if material and numbers and current_baseline(lang,obj,owner) and "透明款" not in str(obj["model"]):
            expected_title=new_seo(lang,obj,numbers)[0]
            assert title==expected_title,(lang,obj["slug"],title,expected_title)
        countproducts+=1

    collection_slugs=[value[1] for value in CAT.values()]
    available_collections=["/collections/"+slug+"/" for slug in collection_slugs
        if (D/(prefix+"collections/"+slug)/"index.html").is_file()]
    for route in ["/products/"]+available_collections:
        localized="/"+prefix+route.lstrip("/")
        page=(D/localized.lstrip("/")/"index.html").read_text(encoding="utf8")
        nodes=schema_nodes(page)
        lists=[node for node in nodes if node.get("@type")=="ItemList"]
        urls=actual_product_cards(page)
        assert len(lists)==1 and len(urls)==lists[0]["numberOfItems"],(lang,route,len(lists),len(urls))
        assert [item["url"] for item in lists[0]["itemListElement"]]==[ORIGIN+url for url in urls]
        assert add_at_render(page,localized,lang)==page,(lang,route,"ItemList renderer not idempotent")
        countlists+=1

# CMS writer wins: an edited title is not replaced by the source default.
editable=deepcopy(owner)
match=next(item for item in editable["pages"] if item.get("route")=="/products/2095/")
match["seo_title"]="OWNER selected product title"
row=SERIES["2095"]
sample='<html><head><title>OWNER selected product title</title><meta name="description" content="Approved owner summary"></head><body></body></html>'
assert not current_baseline("en",row,editable)
assert pre_render_verified_meta(sample,"en",row,editable)==sample

# A real product's owner-selected visible FAQ becomes the only FAQ schema source.
test='<html><head></head><body><main><div class="faq-list"><details><summary>What is the owner selected lid?</summary><p>The exact selection is checked by the product manager.</p></details></div></main></body></html>'
added=add_at_render(test,"/products/2095/","en")
nodes=schema_nodes(added)
faq=[node for node in nodes if node.get("@type")=="FAQPage"]
assert len(faq)==1 and "owner selected lid?" in faq[0]["mainEntity"][0]["name"]
assert add_at_render(added,"/products/2095/","en")==added

print("XUYI_PRODUCT_FAQ_BREADCRUMB_WEBPAGE_ITEMLIST_SCHEMA_PASSED",
      "products",countproducts,"FAQs",countfaq,"lists",countlists,"materialFacts",countmaterials)