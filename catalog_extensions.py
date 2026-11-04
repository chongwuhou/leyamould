"""Append explicitly reviewed, single-item XUYI products to the shared catalog.

Legacy Excel/PPT products remain unchanged. New products are only accepted
from the published D1 snapshot, never from draft or fabricated placeholders.
"""
import re
import json
from functools import lru_cache
from pathlib import Path

ROOT=Path(__file__).resolve().parent

@lru_cache(maxsize=1)
def factory_catalog_seo_defaults():
 manifest=json.loads((ROOT/"data/factory-catalog-manifest-2026-11-03.json").read_text(encoding="utf-8"))
 bundle=json.loads((ROOT/"scripts/fixtures/factory-catalog-import-2026-11-03.json").read_text(encoding="utf-8"))
 if manifest.get("site")!="xuyi-drinkware-site" or manifest.get("recordCount")!=58:
  raise ValueError("Factory catalog SEO baseline belongs to another site or batch")
 if bundle.get("sourceDocument")!=manifest.get("sourceDocument") or bundle.get("sourceSha256")!=manifest.get("sourceSha256"):
  raise ValueError("Factory catalog SEO baseline source fingerprint mismatch")
 rows={}
 for record in bundle.get("records",[]):
  model=str(record.get("model") or "").lower()
  content=record.get("content")
  if not model or not isinstance(content,dict) or model in rows:
   raise ValueError("Invalid or duplicate factory catalog SEO baseline row")
  rows[model]={field:content.get(field) for field in ("seoTitle","seoDescription")}
 if len(rows)!=58:
  raise ValueError("Factory catalog SEO baseline must contain exactly 58 models")
 return rows,manifest

@lru_cache(maxsize=1)
def ppt_factory_catalog_manifest():
 manifest=json.loads((ROOT/"scripts/fixtures/ppt-new-95-source-models.json").read_text(encoding="utf-8"))
 if (manifest.get("site")!="xuyi-drinkware-site" or
     manifest.get("sourceDocument")!="水杯最新产品.pptx" or manifest.get("modelCount")!=95 or
     not re.fullmatch(r"[0-9a-f]{64}",str(manifest.get("sourceSha256","")))):
  raise ValueError("PPT factory catalog source manifest is invalid")
 rows={}
 for record in manifest.get("models",[]):
  model=str(record.get("model") or "").lower()
  page=record.get("sourcePage")
  if not model or model in rows or not isinstance(page,int):
   raise ValueError("Invalid or duplicate PPT factory catalog source row")
  rows[model]=page
 if len(rows)!=95:
  raise ValueError("PPT factory catalog source manifest must contain exactly 95 models")
 return rows,manifest

PPT_DESCRIPTION_KINDS={
 "Plastic Sports Water Bottles":"sports water bottle",
 "Large Capacity Water Jugs":"large-capacity water bottle",
 "Plastic Shaker Bottles":"sports shaker bottle",
 "Spray Water Bottles":"spray water bottle",
 "Two-Way Drinking Cups":"two-way drinking cup",
 "Titanium Vacuum Cups":"titanium vacuum cup",
}

def _ppt_source_description_default(model,content):
 capacity=str(content.get("capacity") or "")
 material=str(content.get("material") or "")
 if not capacity or not material:return False
 kind=PPT_DESCRIPTION_KINDS.get(str(content.get("category") or ""))
 candidates=[]
 if kind:
  candidates.append(
   f"XUYI Model {model} {kind}: {material}, {capacity} options, source-listed dimensions and carton packing. "
   "Wholesale supply; request a quote."
  )
 candidates.append(
  f"Wholesale {capacity} plastic drinkware, model {model}, with {material}. "
  f"Factory-listed dimensions {content.get('dimensions')}; {content.get('carton_quantity')} pcs/carton, "
  f"{content.get('carton_size')}. Contact XUYI for samples and custom branding."
 )
 candidates.append(
  f"Model {model}: {capacity} plastic sports bottle, {material}. "
  "Source-listed dimensions and carton sizes are included for both variants. "
  "Contact XUYI for samples and custom branding."
  )
 return content.get("seoDescription") in candidates
def is_factory_catalog_source_default(model,content,field):
 if field not in ("seoTitle","seoDescription") or not isinstance(content,dict):
  return False
 if content.get("newProduct") is not True:
  return False
 source=content.get("sourceDocument")
 if source=="水杯最新产品.pptx":
  rows,manifest=ppt_factory_catalog_manifest()
  slug=str(model).lower()
  if (content.get("sourceSha256")!=manifest.get("sourceSha256") or
      str(content.get("sourcePage") or "")!=str(rows.get(slug) or "")):
   return False
  if field=="seoTitle":
   from product_content import factory_catalog_seo_title
   expected=factory_catalog_seo_title({**content,"model":slug})
   return isinstance(expected,str) and bool(expected.strip()) and content.get(field)==expected
  return _ppt_source_description_default(slug,content)
 if source:
  rows,manifest=factory_catalog_seo_defaults()
  if (source!=manifest.get("sourceDocument") or
      content.get("sourceSha256")!=manifest.get("sourceSha256") or
      not content.get("sourcePage")):
   return False
  expected=rows.get(str(model).lower(),{}).get(field)
  return isinstance(expected,str) and bool(expected.strip()) and content.get(field)==expected
 return False


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
 source_document=entry.get("sourceDocument")
 if source_document:
  if not isinstance(source_document,str) or not source_document.strip():
   raise ValueError("Invalid factory catalog source document")
  if not re.fullmatch(r"\d{1,3}",str(entry.get("sourcePage",""))):
   raise ValueError("Factory catalog product requires its source page")
  if not re.fullmatch(r"[0-9a-f]{64}",str(entry.get("sourceSha256","")),re.I):
   raise ValueError("Factory catalog product requires verified sourceSha256")
 source_image_sha=entry.get("sourceImageSha256","")
 if source_image_sha and not re.fullmatch(r"[0-9a-f]{64}",str(source_image_sha),re.I):
  raise ValueError("Factory catalog product has invalid sourceImageSha256")
 return entry

def append_new_products(series,rows):
 count=0
 for row in rows:
  if not isinstance(row,dict):raise ValueError("Invalid XUYI D1 product snapshot")
  model=str(row.get("model",""))
  content=row.get("content")
  if not isinstance(content,dict) or content.get("newProduct") is not True:continue
  if "pending" in str(content.get("imageReviewStatus","")).lower():
   raise ValueError("Refusing to build a product with an unreviewed replacement image")
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