"""Model-specific visible H1 and main-image descriptions during source rendering.

D1/CMS selected content is immutable unless it still matches a recognized
factory-default label. A photograph shared by multiple models is *never*
assigned to one exclusive SKU or material by implication.
"""
from collections import Counter
from html import escape,unescape
import re
import json,hashlib
from pathlib import Path
OWNER_BASELINES=json.loads((Path(__file__).parent/'data/product-identity-d1-baselines.json').read_text(encoding='utf8'))['locales']
def matches_owner_field(text,slug,locale,index):
    record=OWNER_BASELINES.get(locale,{}).get(slug)
    if not record:return True  # New template-owned catalog SKU
    return hashlib.sha256(text.strip().encode('utf8')).hexdigest().startswith(record[index])

LOCAL_MODEL={"en":"Model","es":"Modelo","pt":"Modelo","ru":"Модель","tr":"Model"}
GENERIC_ALT={
 "/assets/curated-hd/gradient-sports.webp":"Reusable plastic sports bottle collection",
 "/assets/curated-hd/feature-flip-top.webp":"Plastic bottle flip top lid collection",
 "/assets/curated-hd/outdoor-lifestyle.webp":"Outdoor reusable plastic water bottle collection",
 "/assets/curated-hd/customizable-assortment.webp":"Customizable plastic drinkware assortment",
}
def main_image_alt(row,image,owners,locale,materials,numbers):
    model=str(row["model"])
    categories={"en":{"Plastic Sports Water Bottles":"sports water bottle","Kids Plastic Water Bottles":"kids water bottle","Large Capacity Water Jugs":"large water jug","Plastic Shaker Bottles":"protein shaker"},"es":{"Plastic Sports Water Bottles":"botella deportiva","Kids Plastic Water Bottles":"botella infantil","Large Capacity Water Jugs":"garrafa grande","Plastic Shaker Bottles":"vaso mezclador"},"pt":{"Plastic Sports Water Bottles":"garrafa esportiva","Kids Plastic Water Bottles":"garrafa infantil","Large Capacity Water Jugs":"garrafão de água","Plastic Shaker Bottles":"coqueteleira"},"ru":{"Plastic Sports Water Bottles":"спортивная бутылка","Kids Plastic Water Bottles":"детская бутылка","Large Capacity Water Jugs":"большая бутылка для воды","Plastic Shaker Bottles":"шейкер"},"tr":{"Plastic Sports Water Bottles":"spor matarası","Kids Plastic Water Bottles":"çocuk matarası","Large Capacity Water Jugs":"büyük su bidonu","Plastic Shaker Bottles":"shaker şişesi"}}
    category=categories[locale].get(row["category"],"plastic bottle")
    if owners.get(image,0)!=1:
        return {"en":"Reusable plastic drinkware catalog photograph","es":"Foto de catálogo de botellas plásticas","pt":"Fotografia do catálogo de garrafas plásticas","ru":"Фото пластиковой бутылки из каталога","tr":"Plastik matara katalog fotoğrafı"}[locale]
    facts=[]
    if numbers:facts.append("/".join(f"{n:g}" for n in numbers)+"ml")
    if materials:facts.append(materials)
    facts.append(category)
    facts.append(LOCAL_MODEL[locale]+" "+model)
    return " ".join(facts)+" "+{"en":"product photograph","es":"foto del producto","pt":"foto do produto","ru":"фото товара","tr":"ürün fotoğrafı"}[locale]

def source_product_identity(body,row,locale,owners):
    from scripts.source_catalog_capacity_oz import catalog_volume_numbers,verified_source_material,add_to_heading
    model=str(row["model"])
    numbers=catalog_volume_numbers(row)
    material=verified_source_material(row)
    # Do not overwrite custom operator-written H1. Baseline catalog captions
    # contain the bottle category and no SKU. A changed H1 remains authoritative.
    match=re.search(r"(<h1\b[^>]*>)(.*?)(</h1>)",body,re.S|re.I)
    if match:
        inner=match.group(2)
        shown=unescape(re.sub(r"<[^>]+>"," ",inner)).strip()
        has_model=bool(re.search(r"(?<![A-Za-z0-9])"+re.escape(model)+r"(?![A-Za-z0-9])",shown,re.I))
        kinds={
         "en":("bottle","jug","shaker"),"es":("botella","garrafa","mezcladora","jarra"),
         "pt":("garrafa","shaker","coqueteleira","jarro"),"ru":("бутыл","шейкер","ёмкост","кувшин"),
         "tr":("şişe","matara","shaker","sürahi")}
        # Standard D1 product headlines are category + capacity. Skip
        # arbitrary custom headings instead of silently rewriting them.
        is_catalog=(any(w in shown.lower() for w in kinds[locale])
                    and matches_owner_field(shown,str(row["slug"]),locale,0))
        if is_catalog:
            # Source H1 preserves accurate milliliters and APPROXIMATE
            # overseas retail size class, never treats oz as an exact volume.
            revised=add_to_heading(inner,numbers,locale) if numbers and "oz" not in shown.lower() else inner
            if not has_model:
                label=LOCAL_MODEL[locale]+" "+model
                revised+=' <span class="product-h1-model">· '+escape(label)+'</span>'
            if revised!=inner:body=body[:match.start(2)]+revised+body[match.end(2):]
    # Exact main-image src comes from the already selected product body; D1
    # image choices remain untouched. Update only default, source-standard alt.
    img=re.search(r'<img\b(?=[^>]*\bid="main-photo")[^>]*>',body,re.I)
    if img:
        tag=img.group(0)
        src=re.search(r'\bsrc="([^"]+)"',tag)
        old=re.search(r'\balt="([^"]*)"',tag)
        if src and old:
            alt=unescape(old.group(1))
            # A manually authored descriptive ALT is never replaced.
            if (("model" in alt.lower() or "modelo" in alt.lower() or
                 "модель" in alt.lower() or
                 alt in ("XUYI Plastic Water Bottles catalog photo","Gradient Sports Bottles with Time Markers")) and
                 src.group(1) in row["images"] and
                 matches_owner_field(alt,str(row["slug"]),locale,1)):
                replacement=main_image_alt(row,src.group(1),owners,locale,material,numbers)
                new=tag[:old.start(1)]+escape(replacement,quote=True)+tag[old.end(1):]
                body=body[:img.start()]+new+body[img.end():]
    # Thumbnails repeat the main or gallery photo inside a control which
    # already has an accessible aria-label. Decorative alt="" avoids
    # assigning inconsistent alternative text to the identical image.
    def decorative_thumbnail(m):
        tag=m.group(0)
        if "aria-label=" not in tag:return tag
        return re.sub(r'(<img\b[^>]*\balt=")[^"]*(")',lambda x:x.group(1)+x.group(2),tag,count=1)
    body=re.sub(r'<button\b(?=[^>]*class="product-detail__thumb")[^>]*>.*?</button>',decorative_thumbnail,body,flags=re.S|re.I)
    return body
