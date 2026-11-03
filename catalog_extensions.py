"""Append explicitly reviewed, single-item XUYI products to the shared catalog.

Legacy Excel/PPT products remain unchanged. New products are only accepted
from the published D1 snapshot, never from draft or fabricated placeholders.
"""
import re

CATEGORIES=frozenset((
 "Plastic Sports Water Bottles","Large Capacity Water Jugs",
 "Kids Plastic Water Bottles","Plastic Shaker Bottles",
 "Spray Water Bottles","Two-Way Drinking Cups","Titanium Vacuum Cups"
))
SLUG=re.compile(r"[a-z0-9][a-z0-9-]{1,63}$")
IMAGE=re.compile(r"/media/(?:product|page|shared|ppt|excel|group|gallery|capability|blog)/[a-zA-Z0-9._-]{3,140}\.(?:webp|jpg|png)$")
def validate_new_product(model,entry):
 if not isinstance(model,str) or not SLUG.fullmatch(model) or ".." in model:
  raise ValueError("Invalid new-product model/URL")
 if not isinstance(entry,dict) or entry.get("newProduct") is not True:
  raise ValueError("Not an approved single-product record")
 if entry.get("category") not in CATEGORIES:
  raise ValueError("Unsupported XUYI bottle category")
 for key,max_chars in (("name",180),("material",200),("capacity",120),("description",1300)):
  value=entry.get(key)
  if not isinstance(value,str) or not (2<=len(value.strip())<=max_chars):
   raise ValueError("Missing verified new-product field: "+key)
 img=entry.get("image")
 if not isinstance(img,str) or not IMAGE.fullmatch(img) or ".." in img:
  raise ValueError("New products require a valid XUYI R2 image path")
 if len(entry.get("seoTitle",""))>90 or len(entry.get("seoDescription",""))>240:
  raise ValueError("SEO metadata length exceeded")
 return entry

def append_new_products(series,rows):
 count=0
 for row in rows:
  if not isinstance(row,dict):raise ValueError("Invalid XUYI D1 product snapshot")
  model=str(row.get("model",""))
  content=row.get("content")
  if not isinstance(content,dict) or content.get("newProduct") is not True:continue
  if model in series:raise ValueError("New product conflicts with an existing XUYI model")
  validate_new_product(model,content)
  display_model=str(content.get("factoryModel") or model).strip() or model
  info={key:content.get(key,"") for key in (
        "factoryModel","name","description","capacity","material","colors","packing",
        "dimensions","unit_weight","temperature_range","retail_box_size",
        "carton_quantity","carton_size","carton_gross_weight","catalogOunceLabel",
        "sourceDocument","sourcePage","sourceNotes","qcStatus","imageReviewStatus",
        "seoTitle","seoDescription")}
  series[model]={
    **info,"model":display_model,"factoryModel":display_model,"slug":model,"category":content["category"],
    "images":[content["image"]],"variants":[{**info,"model":display_model,"factoryModel":display_model}],
    "manualNew":True
  }
  count+=1
 return count
