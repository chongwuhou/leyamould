#!/usr/bin/env python3
"""Source-backed US fl-oz and gradient copy for reviewed XUYI models.

The factory model IDs and capacity/material data are never changed.
Only historically identified baseline metadata may be revised; any new D1/CMS
author edit of the title/description/name blocks the historical rewrite.
The official Pages build always invokes this script after rendering locales.
"""
from pathlib import Path
from html import escape, unescape
import json
import re
import sys
import hashlib

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from site_renderer import SERIES

SOURCE_CAPACITY = {
    "2505":(800,False),"2513":(800,True),"2514":(1000,True),
    "2515":(800,True),"2516":(1000,True),"2470":(800,False),
    "2212":(1000,True),"2209":(800,True),"2402":(800,True),
    "2403":(1000,True),"2406":(800,False),"2405":(800,False),
    "2309":(800,True),"2310":(1000,True),"2458":(800,False),
    "2459":(1000,False),"2311":(800,True),"2312":(1000,True),
    "5340":(1000,False),"lo-002":(800,False),
    "lo-005":(1000,True),"lo-006":(1000,False),"lo-007":(1000,False),
}
SOURCE_LO = {
    p["slug"]:p for p in
    json.loads((ROOT/"data/lo-products.json").read_text(encoding="utf8"))["products"]
}
LOCALES = ("en","es","pt","ru","tr")
# SHA256 of the actual reviewed 2026-10-14 LO title, SEO description and
# product name. A later owner edit of the authoritative source is NOT a new
# baseline for this historical rewrite.
LO_REVIEWED_SOURCE_DIGEST = {
    "lo-002":"979cad2052f0a5ecec5e376a942843402749725cadf52d7fbea7b02039b286f3",
    "lo-005":"4384f687efb0b8065034f869f1909f10866965933784480a486c577547fd54a7",
    "lo-006":"7e53fa0b23cf85aa95eebbc15c8a6d8a19a382d680089698fe498b136a47ad49",
    "lo-007":"fe2d0725f68cd62acdf22005545e1f9696b1ad039508cb838876b4b2481ea653",
}
GRADIENT_HINTS = {
    "2513":"blue, pink, black and cyan gradient selections",
    "2514":"blue, pink, black and cyan gradient selections",
    "2515":"blue, pink, black and purple gradient selections",
    "2516":"blue, pink, black and purple gradient selections",
    "2209":"purple-pink, blue-orange, pink-blue and gray-black gradients",
    "2212":"purple-pink, blue-orange, pink-blue and gray-black gradients",
    "2402":"black-gray, blue-pink, pink-green-blue and green-orange gradients",
    "2403":"black-gray, blue-pink, pink-green-blue and green-orange gradients",
    "2309":"black-gray, pink-blue, olive-green and blue-orange gradients",
    "2310":"black-gray, pink-blue, olive-green and blue-orange gradients",
    "2311":"purple-pink, blue-orange, green-pink and gray-black gradients",
    "2312":"purple-pink, blue-orange, green-pink and gray-black gradients",
    "lo-005":"a gradient-colored finish with time markers",
}

def actual_model(slug):
    found = [r for r in SERIES.values() if r.get("slug")==slug]
    return found[0] if len(found)==1 else None

def source_baseline(slug,ml):
    if slug in SOURCE_LO:
        loc = SOURCE_LO[slug]["locales"]["en"]
        original=(loc["seoTitle"],loc["seoDescription"],SOURCE_LO[slug]["name"])
        digest=hashlib.sha256("\x1f".join(original).encode("utf8")).hexdigest()
        if digest!=LO_REVIEWED_SOURCE_DIGEST.get(slug):
            return None,None,None  # CMS/source has changed since review.
        return original
    title = f"{ml}ml Plastic Sports Water Bottle — Model {slug} | XUYI Bottles"
    description = (f"{ml}ml Plastic Sports Water Bottle model {slug}: compare catalog "
                   "specifications, material, color and packing options; request a "
                   "product-specific wholesale quotation.")
    return title,description,f"{ml}ml Plastic Sports Water Bottle"

def seo_copy(slug,ml,gradient,row):
    """Legacy API: share the single authoritative overseas size-class lookup."""
    from scripts.source_catalog_capacity_oz import new_seo,catalog_volume_numbers
    return new_seo("en",row,catalog_volume_numbers(row))

def replace_meta(markup,field,old,new):
    pattern=(r'(<meta '+re.escape(field)+r' content=")([^"]*)(")')
    def update(m):
        return m.group(1)+(escape(new,quote=True) if unescape(m.group(2))==old else m.group(2))+m.group(3)
    return re.sub(pattern,update,markup,count=1)

def render_note(row,locale="en"):
    """Return a source-rendered, localized gradient note for verified models."""
    slug=str(row.get("slug") or "")
    source=SOURCE_CAPACITY.get(slug)
    if not source:return ""
    ml,gradient=source
    if not gradient or slug not in GRADIENT_HINTS:return ""
    from scripts.source_catalog_capacity_oz import catalog_volume_numbers
    numbers=catalog_volume_numbers(row)
    if not any(abs(float(value)-float(ml))<0.5 for value in numbers):return ""
    if not re.search(r"渐变|gradient",str(row.get("colors",""))+" "+str(row.get("name","")),re.I):
        return ""
    hint=GRADIENT_HINTS[slug]
    if locale=="en":
        text="Gradient color sports bottle: factory catalog options include "+hint+". Check the actual shade and finish on a physical sample before approving branding or a bulk order."
    else:
        text={
          "es":"El catálogo de fábrica confirma opciones de acabado degradado para este modelo. Verifique el tono y el acabado reales en una muestra antes de aprobar la marca o el pedido mayorista.",
          "pt":"O catálogo da fábrica confirma opções de acabamento em degradê para este modelo. Verifique a tonalidade e o acabamento reais em uma amostra antes de aprovar a marca ou o pedido de atacado.",
          "ru":"Каталог производителя подтверждает варианты градиентной расцветки этой модели. Проверьте фактический оттенок и отделку на образце до согласования брендинга и оптового заказа.",
          "tr":"Fabrika kataloğu bu model için degrade renk seçeneklerini doğrular. Markalama veya toptan siparişi onaylamadan önce gerçek tonu ve yüzeyi numunede kontrol edin.",
        }[locale]
    return '<p class="product-gradient-finish" data-verified-gradient-model="'+escape(str(row.get("model","")),quote=True)+'">'+escape(text)+'</p>'