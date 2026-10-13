#!/usr/bin/env python3
"""Fix overly verbose localized catalog SKU search snippets from source facts.

Only 85 real, source-catalog entries. G-series factory models and LO records
remain unchanged; nothing is guessed from photo references.
"""
from pathlib import Path
from html import escape,unescape
import re
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from site_renderer import SERIES
from scripts.model_catalog_buyer_comparison import capacity_number,raw_value
from cms_seo_curation_guard import may_curate

LOCALES=("es","pt","ru","tr")
PRODUCT_NAMES={
 "es":{
  "Plastic Sports Water Bottles":"botella deportiva de plástico",
  "Kids Plastic Water Bottles":"botella infantil de plástico",
  "Large Capacity Water Jugs":"jarra de agua plástica",
  "Plastic Shaker Bottles":"shaker de proteína de plástico",
 },
 "pt":{
  "Plastic Sports Water Bottles":"garrafa esportiva de plástico",
  "Kids Plastic Water Bottles":"garrafa infantil de plástico",
  "Large Capacity Water Jugs":"garrafão de água de plástico",
  "Plastic Shaker Bottles":"shaker de proteína de plástico",
 },
 "ru":{
  "Plastic Sports Water Bottles":"спортивная пластиковая бутылка",
  "Kids Plastic Water Bottles":"детская пластиковая бутылка",
  "Large Capacity Water Jugs":"пластиковая бутылка большого объёма",
  "Plastic Shaker Bottles":"пластиковый шейкер",
 },
 "tr":{
  "Plastic Sports Water Bottles":"plastik spor su şişesi",
  "Kids Plastic Water Bottles":"plastik çocuk su şişesi",
  "Large Capacity Water Jugs":"büyük hacimli plastik su şişesi",
  "Plastic Shaker Bottles":"plastik protein shaker",
 }
}

def copy(locale,model,kind,capacity,material):
    material=material or "-"
    if locale=="es":
        title=f"{kind.title()}"+(f" {capacity:g} mL" if capacity else "")+f" | {model} | XUYI"
        desc=f"Modelo {model}: {kind}"+(f", {capacity:g} mL" if capacity else "")+f". Material del catálogo: {material}. Compare tapa y embalaje; solicite muestra y cotización."
    elif locale=="pt":
        title=f"{kind.capitalize()}"+(f" {capacity:g} mL" if capacity else "")+f" | {model} | XUYI"
        desc=f"Modelo {model}: {kind}"+(f", {capacity:g} mL" if capacity else "")+f". Material no catálogo: {material}. Compare tampa e embalagem; peça amostra e cotação."
    elif locale=="ru":
        title=f"{kind.capitalize()}"+(f" {capacity:g} мл" if capacity else "")+f" | {model} | XUYI"
        desc=f"Модель {model}: {kind}"+(f", {capacity:g} мл" if capacity else "")+f". Материал по каталогу: {material}. Уточните крышку и упаковку; запросите образец и оптовый расчёт."
    else:
        title=f"{kind.capitalize()}"+(f" {capacity:g} mL" if capacity else "")+f" | {model} | XUYI"
        desc=f"Model {model}: {kind}"+(f", {capacity:g} mL" if capacity else "")+f". Katalog malzemesi: {material}. Kapak ve paketlemeyi doğrulayın; numune ve teklif isteyin."
    return title,desc

def rewrite_meta(head,attribute,new,path):
    pattern=r'<meta '+re.escape(attribute)+r' content="[^"]*"'
    hits=list(re.finditer(pattern,head))
    if len(hits)!=1:raise ValueError("Expected one "+attribute+" in "+str(path))
    return re.sub(pattern,lambda _: '<meta '+attribute+' content="'+escape(new,quote=True)+'"',head,count=1)

def apply(dist):
    dist=Path(dist)
    models=[row for row in SERIES.values() if not row.get("manualNew")]
    if len(models)<85:raise ValueError("Catalog source models unexpectedly missing")
    changed_titles=changed_descriptions=0
    for model in models:
        sku=str(model["model"])
        category=model["category"]
        material_values=raw_value(model,"material")
        material=" / ".join(material_values[:3])
        cap=capacity_number(model) # Suspicious or unverified figures remain absent.
        for locale in LOCALES:
            file=dist/locale/"products"/str(model["slug"])/"index.html"
            original=file.read_text(encoding="utf8")
            head,sep,tail=original.partition("</head>")
            if not sep:raise ValueError("Missing head: "+str(file))
            m=re.search(r'<title>(.*?)</title>',head,re.S)
            n=re.search(r'<meta name="description" content="([^"]*)"',head,re.S)
            if not m or not n:raise ValueError("Missing search metadata: "+str(file))
            old_title=unescape(m.group(1))
            old_description=unescape(n.group(1))
            candidate_title,candidate_desc=copy(locale,sku,PRODUCT_NAMES[locale][category],cap,material)
            if sku not in candidate_title or sku not in candidate_desc or (cap and f"{cap:g}" not in candidate_title):
                raise ValueError("Model identity lost: "+sku)
            allowed_title=may_curate(locale,"/products/"+str(model["slug"])+"/","title")
            allowed_desc=may_curate(locale,"/products/"+str(model["slug"])+"/","description")
            if len(old_title)>70 and allowed_title:
                if len(candidate_title)>=len(old_title) or len(candidate_title)>70:
                    raise ValueError("Proposed title not an improvement: "+str(file))
                head=head[:m.start(1)]+escape(candidate_title)+head[m.end(1):]
                # Existing share headline, if present, should not contradict it.
                if 'property="og:title"' in head:
                    head=re.sub(r'<meta property="og:title" content="[^"]*"',
                        lambda _: '<meta property="og:title" content="'+escape(candidate_title,quote=True)+'"',head,count=1)
                changed_titles+=1
            if len(old_description)>180 and allowed_desc:
                if len(candidate_desc)>=len(old_description) or not 85<=len(candidate_desc)<=180:
                    raise ValueError("Proposed description not an improvement: "+str(file))
                head=rewrite_meta(head,'name="description"',candidate_desc,file)
                if 'property="og:description"' in head:
                    head=rewrite_meta(head,'property="og:description"',candidate_desc,file)
                changed_descriptions+=1
            file.write_text(head+sep+tail,encoding="utf8")
    print("XUYI_SOURCE_BACKED_LOCALIZED_PRODUCT_META",changed_titles,"titles",changed_descriptions,"descriptions")
    return changed_titles,changed_descriptions

if __name__=="__main__":
    apply(ROOT/"dist")