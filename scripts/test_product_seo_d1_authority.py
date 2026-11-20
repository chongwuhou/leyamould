#!/usr/bin/env python3
"""D1 owns existing and future English + localized product SEO across builds."""
from pathlib import Path
from html import unescape
from copy import deepcopy
import json,re,sys,os

ROOT=Path(__file__).resolve().parent.parent
SNAPSHOT=ROOT/"_local_ops"/"build-snapshot.json"
if SNAPSHOT.is_file():os.environ["XUYI_BUILD_SNAPSHOT"]=str(SNAPSHOT)
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"scripts"))
from product_seo_d1_source import apply_d1_product_seo
from site_renderer import SERIES
from factory_catalog_locales import _source_products
from source_catalog_capacity_oz import catalog_volume_numbers,new_seo,new_seo_without_capacity,LOCALES,source_field_allowed
from cms_seo_curation_guard import snapshot

def get_meta(html):
    def find(p):
        match=re.search(p,html,re.S)
        assert match
        return unescape(match.group(1))
    return (find(r"<title>([^<]+)</title>"),
            find(r'<meta name="description" content="([^"]+)"'),
            find(r'<meta property="og:title" content="([^"]+)"'),
            find(r'<meta property="og:description" content="([^"]+)"'))

owner=snapshot()
assert owner and owner["site"]=="leyamould"
records=owner.get("productSeo",[])
seen=set()
checked=0
for loc in LOCALES:
    for model in SERIES.values():
        slug=model["slug"]
        file=ROOT/"dist"/("" if loc=="en" else loc)/"products"/slug/"index.html"
        is_new_factory = model.get("manualNew") is True and model.get("sourceDocument") in {"puyunsm(1).pdf", "水杯最新产品.pptx"}
        assert file.is_file(),file
        html=file.read_text("utf8")
        title,description,og,og_desc=get_meta(html)
        assert title==og and description==og_desc,(loc,slug,"HTML title/OG drift")
        expected=next((r for r in records if r.get("slug")==slug and r.get("locale")==loc),None)
        if expected:
            allow_title=source_field_allowed(loc,model,"title",owner)
            allow_desc=source_field_allowed(loc,model,"description",owner)
            numbers=catalog_volume_numbers(model)
            suggested_title,suggested_description=new_seo(loc,model,numbers) if numbers else new_seo_without_capacity(loc,model)
            if allow_title:
                assert title==suggested_title,(loc,slug,"baseline D1 title should receive source SEO refresh",title,suggested_title)
            else:
                assert title==expected["seoTitle"],(loc,slug,"owner D1 SEO title overwritten",title,expected["seoTitle"])
            if allow_desc:
                assert description==suggested_description,(loc,slug,"baseline D1 description should receive source SEO refresh",description,suggested_description)
            else:
                assert description==expected["metaDescription"],(loc,slug,"owner D1 description overwritten")
            assert apply_d1_product_seo(html,slug,loc,owner)==html,(loc,slug,"not idempotent")
            seen.add((slug,loc))
        assert '<link rel="canonical" href="https://leyamould.com/' in html
        if is_new_factory and not expected:
            numbers=catalog_volume_numbers(model)
            allow_title=source_field_allowed(loc,model,"title",owner)
            allow_desc=source_field_allowed(loc,model,"description",owner)
            if allow_title:
                suggested_title,suggested_description=new_seo(loc,model,numbers)
                assert "ml" in title.lower() and "oz" in title.lower(),(loc,slug,"mL/oz missing from source SEO title",title)
                assert title==suggested_title,(loc,slug,"source title differs from reviewed SKU/capacity",title,suggested_title)
            if allow_desc:
                suggested_title,suggested_description=new_seo(loc,model,numbers)
                assert "ml" in description.lower() and "oz" in description.lower(),(loc,slug,"mL/oz missing from source SEO description",description)
                assert description==suggested_description,(loc,slug,"source description differs from reviewed SKU/capacity",description,suggested_description)
        elif catalog_volume_numbers(model) and not expected:
            if source_field_allowed(loc,model,"title",owner):
                assert "oz" in title.lower() and "ml" in title.lower(),(loc,slug,title)
        checked+=1
assert checked==len(SERIES)*len(LOCALES),(checked,len(SERIES)*len(LOCALES))
if records:
    assert len(seen)>=505,"D1 schema migration incomplete or added approved SKUs unrecognized"
# Explicit owner-edited SEO must survive the next source-render invocation.
sample=(ROOT/"dist/pt/products/2292/index.html").read_text("utf8")
chosen=deepcopy(owner)
chosen["productSeo"]=[{"slug":"2292","locale":"pt",
    "seoTitle":"EDITOR: 3800ml classe 128 oz Jarro 2292 | XUYI",
    "metaDescription":"Owner approved custom Portuguese wholesale description with verified model 2292 and a real 3800ml capacity."}]
edited=apply_d1_product_seo(sample,"2292","pt",chosen)
assert get_meta(edited)[0]==chosen["productSeo"][0]["seoTitle"]
assert get_meta(edited)[1]==chosen["productSeo"][0]["metaDescription"]
assert apply_d1_product_seo(edited,"2292","pt",chosen)==edited
assert apply_d1_product_seo(sample,"2291","pt",chosen)==sample
# Source-import defaults may be refreshed; a later D1 owner edit must be preserved.
from copy import deepcopy as _copy
from source_catalog_capacity_oz import source_field_allowed
ppt_model=next(row for row in _source_products(SERIES) if row.get("sourceDocument")=="水杯最新产品.pptx")
edited_state=_copy(owner)
ppt_record=next(item for item in edited_state["products"] if str(item.get("model"))==ppt_model["slug"])
assert source_field_allowed("en",ppt_model,"description",edited_state)
ppt_record["content"]["seoDescription"]="Owner-edited PPT product SEO description."
assert not source_field_allowed("en",ppt_model,"description",edited_state)
assert source_field_allowed("en",ppt_model,"title",edited_state)
assert "href=\"https://leyamould.com/pt/products/2292/\"" in edited
assert 'hreflang="pt"' in edited
# Newly approved model/locale needs no historical 505-count allowlist:
sample_new='<html><head><title>Old Title</title><meta name="description" content="Old summary"><meta property="og:title" content="Old Title"><meta property="og:description" content="Old summary"></head><body><h1>Factory SKU NEW-2027</h1></body></html>'
extra={"productSeo":[{"slug":"new-2027","locale":"en","seoTitle":"Custom Factory Bottle New 2027 | XUYI","metaDescription":"New factory approved product details, to be confirmed with the responsible buyer."}]}
assert "Custom Factory Bottle New 2027 | XUYI" in apply_d1_product_seo(sample_new,"new-2027","en",extra)
print("XUYI_D1_PRODUCT_SEO_TITLE_DESCRIPTION_OG_OWNER_FINAL_5_LOCALES",
      "PAGES",checked,"D1_RECORDS",len(records),"PASS")