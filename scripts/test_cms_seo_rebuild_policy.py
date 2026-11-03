#!/usr/bin/env python3
"""Simulate future D1 edits and verify old SEO copy cannot overwrite them."""
from copy import deepcopy
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
from cms_seo_curation_guard import snapshot,baseline,may_curate,current_field
from catalog_extensions import factory_catalog_seo_defaults

current=snapshot()
assert current is not None and current.get("site")=="xuyi-drinkware-site"
old=baseline()
assert len(old)>=380
cases=[
    ("en","/about/","title"),
    ("es","/capabilities/","description"),
    ("pt","/collections/sports-water-bottles/","description"),
    ("ru","/collections/kids-water-bottles/","description"),
    ("tr","/products/2501/","title"),
    ("es","/products/501/","description"),
]
edited=deepcopy(current)
for lang,route,field in cases:
    # A real owner change may already exist when CI runs: it must not fail
    # merely because the older curation is no longer eligible.
    if lang=="en":
        entry=next(p for p in edited["pages"] if p.get("route")==route)
        entry["seo_title" if field=="title" else "meta_description"]="Owner-updated "+field+" on "+route
    else:
        entry=next(p["content"] for p in edited["translations"]
                   if p.get("locale")==lang and p.get("resourceId")=="page:"+route)
        entry[field]="Owner-updated "+field+" on "+route
    assert not may_curate(lang,route,field,edited),("Owner edit would be overwritten",lang,route,field)
    # The original snapshot's own eligibility is intentionally allowed to
    # vary; future owner changes should not require touching this test.

# A new SKU or article is not automatically rewritten based on older models.
assert not may_curate("es","/products/new-approved-model/","title",edited)
assert not may_curate("en","/about/","title",edited,baseline_data={})

# A factory import's unchanged SEO default must not hide a separately edited
# page-level title on that same product route.
factory_rows,factory_manifest=factory_catalog_seo_defaults()
factory_model="cp01001"
factory_snapshot={
    "site":"xuyi-drinkware-site",
    "pages":[{"route":"/products/cp01001/","seo_title":"400ml (approx. 14 oz) Protein Shaker CP01001 | XUYI"}],
    "products":[{"model":factory_model,"content":{
        "newProduct":True,
        "sourceDocument":factory_manifest["sourceDocument"],
        "sourceSha256":factory_manifest["sourceSha256"],
        "sourcePage":2,
        "seoTitle":factory_rows[factory_model]["seoTitle"],
    }}],
    "translations":[]
}
assert current_field("en","/products/cp01001/","title",factory_snapshot)=="400ml (approx. 14 oz) Protein Shaker CP01001 | XUYI"
# The dedicated productSeo row is applied after the general page/product
# defaults and must therefore win when resolving the live expected title.
product_seo_snapshot={**factory_snapshot,"productSeo":[{
    "slug":"cp01001","locale":"en",
    "seoTitle":"400ml (approx. 14 oz) Protein Shaker CP01001 | XUYI",
    "metaDescription":"Owner-maintained CP01001 product SEO description."
}]}
assert current_field("en","/products/cp01001/","title",product_seo_snapshot)==product_seo_snapshot["productSeo"][0]["seoTitle"]
assert current_field("en","/products/cp01001/","description",product_seo_snapshot)==product_seo_snapshot["productSeo"][0]["metaDescription"]
print("XUYI_CMS_FUTURE_EDITS_PROTECTED",len(cases),"simulated edits, unknown routes excluded")