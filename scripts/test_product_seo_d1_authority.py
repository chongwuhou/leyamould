#!/usr/bin/env python3
"""D1 owns existing and future English + localized product SEO across builds."""
from pathlib import Path
from html import unescape
from copy import deepcopy
import json,re,sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"scripts"))
from product_seo_d1_source import apply_d1_product_seo
from site_renderer import SERIES
from source_catalog_capacity_oz import catalog_volume_numbers,new_seo,LOCALES
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
assert owner and owner["site"]=="xuyi-drinkware-site"
records=owner.get("productSeo",[])
seen=set()
checked=0
for loc in LOCALES:
    for model in SERIES.values():
        slug=model["slug"]
        file=ROOT/"dist"/("" if loc=="en" else loc)/"products"/slug/"index.html"
        assert file.is_file(),file
        html=file.read_text("utf8")
        title,description,og,og_desc=get_meta(html)
        assert title==og and description==og_desc,(loc,slug,"HTML title/OG drift")
        expected=next((r for r in records if r.get("slug")==slug and r.get("locale")==loc),None)
        if expected:
            assert title==expected["seoTitle"],(loc,slug,"D1 SEO title overwritten",title,expected["seoTitle"])
            assert description==expected["metaDescription"],(loc,slug,"D1 description overwritten")
            assert apply_d1_product_seo(html,slug,loc,owner)==html,(loc,slug,"not idempotent")
            seen.add((slug,loc))
        assert '<link rel="canonical" href="https://xuyibottles.com/' in html
        if catalog_volume_numbers(model) and not expected:
            suggested=new_seo(loc,model,catalog_volume_numbers(model))[0]
            assert "oz" in title and "ml" in title,(loc,slug,title)
        checked+=1
assert checked>=505
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
assert "href=\"https://xuyibottles.com/pt/products/2292/\"" in edited
assert 'hreflang="pt"' in edited
# Newly approved model/locale needs no historical 505-count allowlist:
sample_new='<html><head><title>Old Title</title><meta name="description" content="Old summary"><meta property="og:title" content="Old Title"><meta property="og:description" content="Old summary"></head><body><h1>Factory SKU NEW-2027</h1></body></html>'
extra={"productSeo":[{"slug":"new-2027","locale":"en","seoTitle":"Custom Factory Bottle New 2027 | XUYI","metaDescription":"New factory approved product details, to be confirmed with the responsible buyer."}]}
assert "Custom Factory Bottle New 2027 | XUYI" in apply_d1_product_seo(sample_new,"new-2027","en",extra)
print("XUYI_D1_PRODUCT_SEO_TITLE_DESCRIPTION_OG_OWNER_FINAL_5_LOCALES",
      "PAGES",checked,"D1_RECORDS",len(records),"PASS")
