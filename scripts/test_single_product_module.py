#!/usr/bin/env python3
"""Reusable XUYI detail/card/list template regression for one manual D1 item."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from catalog_extensions import append_new_products,validate_new_product
import site_renderer as site
import build
from product_content import details,add_schema
BASE=len(site.SERIES)
model="bottle-qa-demo"
record={
 "newProduct":True,"name":"User-reviewed XUYI water bottle","description":"Sample synthetic bottle for regression testing only.",
 "category":"Plastic Sports Water Bottles","capacity":"750ml","material":"PP",
 "image":"/media/product/"+"a"*32+".webp","seoTitle":"Product QA | XUYI",
 "seoDescription":"A synthetic fixture never published in production.","colors":"","packing":""
}
assert model not in site.SERIES
try:
 assert append_new_products(site.SERIES,[{"model":model,"content":record}])==1
 assert len(site.SERIES)==BASE+1
 page=site.SERIES[model]
 assert page["model"]==page["slug"]==model
 assert page["variants"][0]["capacity"]=="750ml"
 card=site.product_card(page)
 assert "/products/"+model+"/" in card
 assert "User-reviewed XUYI water bottle" in card
 detail=details(page)
 assert "Submitted Capacity" in detail and "750ml" in detail
 assert "Sample synthetic bottle" in detail
 assert "original product catalog" not in detail
 seo=site.page("English QA title","Reviewed descriptive snippet",detail)
 structured=add_schema(seo,page)
 assert '"@type": "Product"' not in structured or '"@type"' in structured
 assert model in structured
 assert "/media/product/" in structured
 listing=build.catalog()
 assert "/products/"+model+"/" in listing
 for bad in [
    {"model":"../secret","content":record},
    {"model":"bottle-bad","content":{**record,"category":"Hydraulic filters"}},
    {"model":"bottle-bad","content":{**record,"image":"https://other.example/photo.png"}},
    {"model":"bottle-bad","content":{**record,"name":""}}
 ]:
  try:
   validate_new_product(bad["model"],bad["content"])
  except ValueError:pass
  else:raise AssertionError("Unsafe or unverified manual product was accepted")
 try:
  append_new_products(site.SERIES,[{"model":"2095","content":record}])
 except ValueError as error:assert "conflicts" in str(error)
 else:raise AssertionError("New D1 product could overwrite a legacy model")
 assert all("bottle-qa-demo" not in str(row.get("model","")) for row in site.BUILD_STATE.get("products",[]))
finally:
 site.SERIES.pop(model,None)
assert len(site.SERIES)==BASE
print("XUYI_ONE_PRODUCT_MODULE_TEST_PASSED",BASE,"legacy models preserved; no production writes")
