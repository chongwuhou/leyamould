"""Model-specific H1 and main-image descriptions during source rendering.

D1/CMS-selected copy is immutable unless it still matches a recognized
factory-default baseline. A shared photograph is never assigned to one
exclusive SKU or material by implication.
"""
from collections import Counter
from html import escape,unescape
import re
import json,hashlib
from pathlib import Path

OWNER_BASELINES=json.loads((Path(__file__).parent/'data/product-identity-d1-baselines.json').read_text(encoding='utf8'))['locales']
# No shared image path is allowed to override a model-specific ALT without a reviewed mapping.
GENERIC_ALT={}

def matches_owner_field(text,slug,locale,index,allow_unbaselined=False):
    record=OWNER_BASELINES.get(locale,{}).get(slug)
    if not record:
        return bool(allow_unbaselined)
    return hashlib.sha256(text.strip().encode('utf8')).hexdigest().startswith(record[index])

LOCAL_MODEL={"en":"Model","es":"Modelo","pt":"Modelo","ru":"Модель","tr":"Model"}
CATEGORY_ALT={
 "en":{"Plastic Sports Water Bottles":"sports water bottle","Kids Plastic Water Bottles":"kids water bottle","Large Capacity Water Jugs":"large-capacity water jug","Plastic Shaker Bottles":"sports shaker bottle","Spray Water Bottles":"spray water bottle","Two-Way Drinking Cups":"two-way drinking cup","Titanium Vacuum Cups":"titanium vacuum cup"},
 "es":{"Plastic Sports Water Bottles":"botella deportiva","Kids Plastic Water Bottles":"botella infantil","Large Capacity Water Jugs":"garrafa de gran capacidad","Plastic Shaker Bottles":"vaso mezclador deportivo","Spray Water Bottles":"botella con pulverizador","Two-Way Drinking Cups":"vaso de doble uso","Titanium Vacuum Cups":"vaso térmico de titanio"},
 "pt":{"Plastic Sports Water Bottles":"garrafa esportiva","Kids Plastic Water Bottles":"garrafa infantil","Large Capacity Water Jugs":"garrafão de grande capacidade","Plastic Shaker Bottles":"coqueteleira esportiva","Spray Water Bottles":"garrafa com borrifador","Two-Way Drinking Cups":"copo de dupla utilização","Titanium Vacuum Cups":"copo térmico de titânio"},
 "ru":{"Plastic Sports Water Bottles":"спортивная бутылка","Kids Plastic Water Bottles":"детская бутылка","Large Capacity Water Jugs":"бутылка большого объёма","Plastic Shaker Bottles":"спортивный шейкер","Spray Water Bottles":"бутылка с распылителем","Two-Way Drinking Cups":"кружка с двумя способами питья","Titanium Vacuum Cups":"титановая термокружка"},
 "tr":{"Plastic Sports Water Bottles":"spor matarası","Kids Plastic Water Bottles":"çocuk matarası","Large Capacity Water Jugs":"büyük hacimli matara","Plastic Shaker Bottles":"sporcu shaker şişesi","Spray Water Bottles":"spreyli su şişesi","Two-Way Drinking Cups":"iki içim seçenekli bardak","Titanium Vacuum Cups":"titanyum termos bardak"},
}

def main_image_alt(row,image,owners,locale,materials,numbers):
    model=str(row["model"])
    category=CATEGORY_ALT[locale].get(row.get("category"),{
        "en":"drinkware product","es":"producto para bebidas","pt":"produto para bebidas","ru":"посуда для напитков","tr":"içecek ürünü"}[locale])
    family={
      "en":f"Shared factory-family image of {category}; confirm the exact model variant and sample.",
      "es":f"Imagen compartida de variantes familiares de {category}; confirme el modelo exacto y la muestra.",
      "pt":f"Imagem compartilhada da família de {category}; confirme o modelo exato e a amostra.",
      "ru":f"Общее фото семейства моделей: {category}; уточните конкретную модель и образец.",
      "tr":f"{category} ürün ailesine ait ortak görsel; kesin modeli ve numuneyi doğrulayın.",
    }
    if row.get("imageReviewStatus")=="visually_reviewed_source_family_image":
        return family[locale]
    if owners.get(image,0)!=1:
        return {
          "en":f"Factory catalog photograph of {category}; exact variant to be confirmed.",
          "es":f"Fotografía de catálogo de {category}; variante exacta por confirmar.",
          "pt":f"Foto de catálogo de {category}; variante exata a confirmar.",
          "ru":f"Фото из каталога: {category}; точный вариант уточняется.",
          "tr":f"{category} katalog fotoğrafı; kesin varyant doğrulanmalıdır.",
        }[locale]
    from scripts.source_catalog_capacity_oz import volume_terms
    facts=[]
    if numbers:facts.append(volume_terms(numbers,locale))
    if materials:facts.append(materials)
    facts.extend((category,LOCAL_MODEL[locale]+" "+model))
    return " ".join(facts)+" "+{
      "en":"product photograph","es":"foto del producto","pt":"foto do produto","ru":"фото товара","tr":"ürün fotoğrafı"
    }[locale]

def source_product_identity(body,row,locale,owners,allow_unbaselined=False):
    from scripts.source_catalog_capacity_oz import product_h1_text,catalog_volume_numbers,verified_source_material
    model=str(row["model"])
    slug=str(row["slug"])
    numbers=catalog_volume_numbers(row)
    material=verified_source_material(row)
    gallery_owner=model.upper().startswith("G-") and not row.get("sourceDocument")
    match=re.search(r"(<h1\b[^>]*>)(.*?)(</h1>)",body,re.S|re.I)
    if match and not gallery_owner:
        inner=match.group(2)
        shown=unescape(re.sub(r"<[^>]+>"," ",inner)).strip()
        kinds={
          "en":("bottle","jug","shaker","cup"),
          "es":("botella","garrafa","jarra","mezcladora","vaso"),
          "pt":("garrafa","jarro","shaker","coqueteleira","copo"),
          "ru":("бутыл","кувшин","шейкер","круж","термокруж"),
          "tr":("şişe","matara","sürahi","shaker","bardak","termos"),
        }
        is_catalog=(any(word in shown.lower() for word in kinds[locale]) or bool(row.get("sourceDocument")))
        baseline=OWNER_BASELINES.get(locale,{}).get(slug)
        if baseline:
            source_h1=matches_owner_field(shown,slug,locale,0,False)
        else:
            # English pages have no separate D1 translation fingerprint: the
            # untouched product-name field is the template's source H1. Only
            # transform that exact default; preserve any distinct editor copy.
            source_h1=(shown==str(row.get("name") or "").strip() or
                       bool(allow_unbaselined and row.get("sourceDocument") and row.get("manualNew")))
        is_catalog=is_catalog and source_h1
        if is_catalog:
            revised=escape(product_h1_text(locale,row))
            if revised!=inner:
                body=body[:match.start(2)]+revised+body[match.end(2):]
    img=re.search(r'<img\b(?=[^>]*\bid="main-photo")[^>]*>',body,re.I)
    if img and not gallery_owner:
        tag=img.group(0)
        src=re.search(r'\bsrc="([^"]+)"',tag)
        old=re.search(r'\balt="([^"]*)"',tag)
        if src and old:
            alt=unescape(old.group(1))
            default_alt=("model" in alt.lower() or "modelo" in alt.lower() or "модель" in alt.lower() or
                alt in ("XUYI Plastic Water Bottles catalog photo","Gradient Sports Bottles with Time Markers"))
            if (default_alt and src.group(1) in row["images"] and
                matches_owner_field(alt,slug,locale,1,allow_unbaselined)):
                replacement=main_image_alt(row,src.group(1),owners,locale,material,numbers)
                new=tag[:old.start(1)]+escape(replacement,quote=True)+tag[old.end(1):]
                body=body[:img.start()]+new+body[img.end():]
    def decorative_thumbnail(match):
        tag=match.group(0)
        if "aria-label=" not in tag:return tag
        return re.sub(r'(<img\b[^>]*\balt=")[^"]*(")',lambda item:item.group(1)+item.group(2),tag,count=1)
    body=re.sub(r'<button\b(?=[^>]*class="product-detail__thumb")[^>]*>.*?</button>',decorative_thumbnail,body,flags=re.S|re.I)
    return body