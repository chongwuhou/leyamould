#!/usr/bin/env python3
"""XUYI shared, repeatable volume and customization enrichment.

All published Product routes share the same rules:
* verified mL paired with reviewed retail size classes, never exact equivalences;
* genuine multi-capacity variants retain every catalog volume;
* conditional custom Tritan/BPA-free buyer language, never a current material
  or finished-item certification claim;
* page titles and descriptions change ONLY when the versioned per-locale
  snapshot/source SHA confirms the owner has not revised their CMS SEO copy.
This is a source-owned build step, NOT a hand-edited dist artifact.
"""
from __future__ import annotations
from pathlib import Path
from html import escape, unescape
import hashlib
import json
import re
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from site_renderer import SERIES
from scripts.cms_seo_curation_guard import current_field
from scripts.verified_capacity_gradient_en import SOURCE_LO
from product_locale_seo import TRANSPARENT

LOCALES=("en","es","pt","ru","tr")
MILLILITERS_PER_US_FL_OZ=29.5735295625
RETAIL_CONFIG=json.loads((ROOT/"data/retail-oz-size-classes.json").read_text(encoding="utf8"))
if RETAIL_CONFIG.get("site")!="xuyi-drinkware-site" or RETAIL_CONFIG.get("schemaVersion")!=1:
    raise RuntimeError("Wrong website or retail-size lookup schema")
RETAIL_SIZES={float(k):v for k,v in RETAIL_CONFIG["classes"].items()}
MARKET_CLASS_MAX_DIFFERENCE=float(RETAIL_CONFIG["maxRelativeDifference"])
FAMILIAR_OZ_SIZES=(12,16,16.9,18,20,22,24,28,30,32,36,40,50,56,60,64,72,80,128)
SIZE_NOTE={
 "en":"Retail search class only: the catalog mL value is the actual capacity. This class is not an exact conversion.",
 "es":"Clase comercial aproximada; la capacidad real figura en mL, no es una conversión exacta.",
 "pt":"Classe comercial aproximada; a capacidade real é dada em mL, não uma conversão exata.",
 "ru":"Примерный торговый размер: фактический объём указан в мл. Это не точное равенство.",
 "tr":"Yaklaşık satış boyutu: gerçek kapasite mL ile verilir; bu kesin dönüşüm değildir.",
}

# Catalog says 60ml for 2506; other source checks identify that value as
# suspicious. Never manufacture a 2 fl oz claim until its SKU is verified.
DISPUTED_CAPACITY_MODELS={"2506"}
BASELINES={
 locale:json.loads((ROOT/"data"/f"volume-oz-cms-baseline-{locale}.json").read_text(encoding="utf8"))["hashes"]
 for locale in LOCALES
}
NO_CAPACITY_META_DIGESTS=json.loads(
    (ROOT/"data/no-volume-source-seo-baseline.json").read_text(encoding="utf8")
)["descriptionSha256"]
NO_CAPACITY_MARKETING={
    "en":"{model} XUYI factory bottle. Capacity to confirm. Ask about custom Tritan or BPA-free materials; check resin, components and finished-product testing.",
    "es":"Modelo de fábrica {model} XUYI. Capacidad por confirmar. Consulte Tritan o materiales sin BPA (BPA-free) a medida; verifique componentes y pruebas.",
    "pt":"Modelo de fábrica {model} XUYI. Capacidade a confirmar. Consulte Tritan ou materiais sem BPA (BPA-free) personalizados; confirme os testes.",
    "ru":"Заводская модель XUYI {model}. Объём уточняется. Tritan и материалы без BPA (BPA-free) под заказ: подтвердите состав и испытания.",
    "tr":"XUYI fabrika modeli {model}. Kapasite doğrulanmalıdır. Özel Tritan ve BPA içermeyen (BPA-free) malzeme seçenekleri için testleri sorun.",
}

KIND={
 "en":{"Plastic Sports Water Bottles":"Sports Water Bottle","Kids Plastic Water Bottles":"Kids Water Bottle",
       "Large Capacity Water Jugs":"Large Water Jug","Plastic Shaker Bottles":"Protein Shaker",
       "Spray Water Bottles":"Spray Water Bottle","Two-Way Drinking Cups":"Two-Way Drinking Cup",
       "Titanium Vacuum Cups":"Titanium Vacuum Cup"},
 "es":{"Plastic Sports Water Bottles":"Botella deportiva","Kids Plastic Water Bottles":"Botella infantil",
       "Large Capacity Water Jugs":"Botella de gran capacidad","Plastic Shaker Bottles":"Vaso mezclador",
       "Spray Water Bottles":"Botella con atomizador","Two-Way Drinking Cups":"Vaso de doble uso",
       "Titanium Vacuum Cups":"Vaso térmico de titanio"},
 "pt":{"Plastic Sports Water Bottles":"Garrafa esportiva","Kids Plastic Water Bottles":"Garrafa infantil",
       "Large Capacity Water Jugs":"Garrafa grande","Plastic Shaker Bottles":"Coqueteleira",
       "Spray Water Bottles":"Garrafa com spray","Two-Way Drinking Cups":"Copo de dupla função",
       "Titanium Vacuum Cups":"Copo térmico de titânio"},
 "ru":{"Plastic Sports Water Bottles":"Спортивная бутылка","Kids Plastic Water Bottles":"Детская бутылка",
       "Large Capacity Water Jugs":"Большая бутылка","Plastic Shaker Bottles":"Шейкер",
       "Spray Water Bottles":"Бутылка с распылителем","Two-Way Drinking Cups":"Чашка с двумя способами питья",
       "Titanium Vacuum Cups":"Титановый термостакан"},
 "tr":{"Plastic Sports Water Bottles":"Spor su şişesi","Kids Plastic Water Bottles":"Çocuk su şişesi",
       "Large Capacity Water Jugs":"Büyük su şişesi","Plastic Shaker Bottles":"Protein shaker",
       "Spray Water Bottles":"Spreyli su şişesi","Two-Way Drinking Cups":"Çift kullanımlı bardak",
       "Titanium Vacuum Cups":"Titanyum vakumlu bardak"},
}
COPY={
 "en":{
  "description":"{volume} {kind}, model {model}. Ask about custom Tritan and BPA-free material options; confirm resin, parts and testing before ordering.",
  "heading":"Custom Tritan and BPA-Free Options — Ask for a Quote",
  "body":"Ask whether a Tritan copolyester body and BPA-free material specification can be customized for this exact model. The catalog material shown above remains the current reference, not a certified Tritan specification. Confirm resin availability, lids, seals, samples and finished-product testing before approval.",
  "capacity":"Capacity in US fluid ounces",
 },
 "es":{
  "description":"{kind} {volume}, modelo {model}. Consulte opciones a medida Tritan y sin BPA (BPA-free). Confirme material, piezas y ensayos antes del pedido.",
  "heading":"Tritan y opciones sin BPA a medida — consultar",
  "body":"Consulte si el modelo admite cuerpo Tritan y materiales libres de BPA (BPA-free). El material del catálogo sigue siendo la referencia actual; confirme resina, tapa, junta, muestra y ensayos del producto final antes de aprobar.",
  "capacity":"Capacidad en onzas líquidas estadounidenses",
 },
 "pt":{
  "description":"{kind} {volume}, modelo {model}. Consulte opções personalizadas Tritan e sem BPA (BPA-free); confirme resina, peças e testes antes do pedido.",
  "heading":"Tritan e opções sem BPA sob consulta",
  "body":"Consulte a possibilidade de corpo em Tritan e materiais sem BPA (BPA-free) para este modelo. O material do catálogo continua a referência; confirme resina, tampa, vedação, amostra e testes do produto final.",
  "capacity":"Capacidade em onças fluidas americanas",
 },
 "ru":{
  "description":"{kind} {volume}, модель {model}. Узнайте о заказном Tritan и вариантах без BPA (BPA-free); уточните полимер, детали и испытания.",
  "heading":"Tritan и материалы без BPA под заказ — по запросу",
  "body":"Уточните возможность изготовления корпуса из Tritan и использования материалов без BPA (BPA-free) для этой модели. Исходные материалы каталога не меняются; согласуйте смолу, крышку, уплотнение, образец и испытания изделия.",
  "capacity":"Объём в американских жидких унциях",
 },
 "tr":{
  "description":"{volume} {kind}, model {model}. Tritan ve BPA içermeyen (BPA-free) özel malzeme seçeneklerini sorun; reçine, kapak ve testleri onaylayın.",
  "heading":"Özel Tritan ve BPA İçermeyen Seçenekleri Sorun",
  "body":"Bu model için Tritan gövde ve BPA içermeyen (BPA-free) malzeme seçeneğini sorun. Katalog malzemesi halen referanstır; reçine, kapak, conta, numune ve nihai ürün testlerini onaylayın.",
  "capacity":"ABD sıvı onsu cinsinden kapasite",
 },
}
VOLUME=re.compile(r"(?<!\d)(\d+(?:\.\d+)?)\s*ml\b",re.I)

def catalog_volume_numbers(row):
    if (str(row.get("model")) in DISPUTED_CAPACITY_MODELS and
        str(row.get("capacity","")).strip().lower() in ("60ml","60 ml")):
        return ()  # Corrected owner/CMS values automatically re-enter.
    values=[]
    # The current CMS-merged capacity is authoritative. Historic variants
    # still establish multiple genuine package-size options for shakers.
    content=str(row.get("capacity") or "")
    if not content or re.search("confirm|unknown|待确认|待核对",content,re.I):return ()
    for match in VOLUME.finditer(content):
        number=float(match.group(1))
        if 100<=number<=10000 and number not in values:values.append(number)
    return tuple(values)

def format_ml(num):
    return (str(int(num)) if float(num).is_integer() else f"{num:g}")+"ml"

def market_record(num):
    num=float(num)
    row=RETAIL_SIZES.get(num)
    if row is not None:
        oz=float(row["oz"])
        if abs(oz*MILLILITERS_PER_US_FL_OZ-num)/num>MARKET_CLASS_MAX_DIFFERENCE:
            raise RuntimeError("Misleading retail class mapping: "+str(num)+"ml/"+str(oz)+"oz")
        return row
    closest=min(FAMILIAR_OZ_SIZES,key=lambda oz:abs(oz*MILLILITERS_PER_US_FL_OZ-num))
    if abs(closest*MILLILITERS_PER_US_FL_OZ-num)/num<=MARKET_CLASS_MAX_DIFFERENCE:
        return {"oz":closest,"kind":"class"}
    # A new unusual size gets an explicitly approximate value, never a
    # false claim of being an established U.S. consumer bottle size.
    return {"oz":round(num/MILLILITERS_PER_US_FL_OZ,1),"kind":"approx"}

def oz_number(num):
    value=float(market_record(num)["oz"])
    return str(int(value)) if value.is_integer() else f"{value:g}"

def format_oz(num,locale="en"):
    oz=oz_number(num)
    if market_record(num)["kind"]=="approx":
        return {"en":f"approx. {oz} oz","es":f"aprox. {oz} oz",
                "pt":f"aprox. {oz} oz","ru":f"около {oz} oz",
                "tr":f"yaklaşık {oz} oz"}[locale]
    return {"en":f"{oz} oz class","es":f"clase {oz} oz",
            "pt":f"classe {oz} oz","ru":f"класс {oz} oz",
            "tr":f"{oz} oz sınıfı"}[locale]

def volume_terms(numbers,locale="en"):
    return " / ".join(format_ml(n)+" ("+format_oz(n,locale)+")" for n in numbers)

def short_oz(numbers,locale="en"):
    return volume_terms(numbers,locale)

def slug_label(row,locale):
    model=str(row["model"])
    if "透明款" in model:
        return re.match(r"\d+",model).group(0)+" ("+TRANSPARENT[locale]+")"
    return model

def current_baseline(locale,row,data=None):
    slug=row["slug"]
    expected=BASELINES[locale].get(slug)
    route="/products/"+slug+"/"
    title=current_field(locale,route,"title",data)
    desc=current_field(locale,route,"description",data)
    if not expected:
        # New approved source models receive ml/oz SEO automatically ONLY if
        # no editor-authored D1 title or description exists. Never overwrite
        # either half of an editor's newly created metadata pair.
        return not (isinstance(title,str) and title.strip() or
                    isinstance(desc,str) and desc.strip())
    if not (isinstance(title,str) and isinstance(desc,str) and title and desc):
        lo=SOURCE_LO.get(slug)
        if lo and locale in lo.get("locales",{}):
            local=lo["locales"][locale]
            title=local.get("seoTitle");desc=local.get("seoDescription")
    if not (isinstance(title,str) and isinstance(desc,str)):return False
    actual=hashlib.sha256((title+"\x1f"+desc).encode("utf8")).hexdigest()
    return actual==expected

def verified_source_material(row):
    """Catalog/CMS component list, not an inferred single body resin."""
    raw=str(row.get("material") or "").strip()
    parts=[piece.strip().upper() for piece in raw.replace("/","+").split("+")]
    permitted={"PC","PP","ABS","PE","PETG","TRITAN"}
    if not parts or len(parts)>3 or any(part not in permitted for part in parts):
        return ""
    return "/".join(dict.fromkeys(parts))

def pre_render_verified_meta(page,locale,row,owner_override=None):
    """Run BEFORE writing a CMS-reviewed template page; no dist HTML edit."""
    volumes=catalog_volume_numbers(row)
    if "</head>" not in page:return page
    head,body=page.split("</head>",1)
    if volumes:
        head,_=seo_head(head,locale,row,volumes,owner_override)
    else:
        # The prior postrender summary pass used to replace 2506's meta
        # description AFTER D1/source rendering. Move that fallback here so
        # a CMS SEO owner cannot be overwritten by later release steps.
        head,_=seo_head_without_capacity(head,locale,row,owner_override)
    return head+"</head>"+body

def seo_title_volume(numbers,locale):
    """The same reviewed ml/approximate-oz sizes as the visible H1, condensed
    for search-title width. For dual-size shakers pair both size classes in
    order, never imply an exact milliliter-to-fluid-ounce conversion.
    """
    if len(numbers)==1:
        return volume_terms(numbers,locale)
    ml="/".join(format_ml(n) for n in numbers)
    oz="/".join(oz_number(n) for n in numbers)
    approximate=any(market_record(n)["kind"]=="approx" for n in numbers)
    if approximate:
        qualifier={
            "en":f"approx. {oz} oz","es":f"aprox. {oz} oz",
            "pt":f"aprox. {oz} oz","ru":f"около {oz} oz",
            "tr":f"yaklaşık {oz} oz"
        }[locale]
    else:
        qualifier={
            "en":f"{oz} oz class","es":f"clase {oz} oz",
            "pt":f"classe {oz} oz","ru":f"класс {oz} oz",
            "tr":f"{oz} oz sınıfı"
        }[locale]
    return f"{ml} ({qualifier})"

def new_seo(locale,row,numbers):
    kind=KIND[locale][row["category"]]
    model=slug_label(row,locale)
    # Keep the retail search-size term consistent with the visible product
    # title, without calling the factory's exact milliliters an oz equivalence.
    vol=seo_title_volume(numbers,locale)
    if (re.search(r"渐变|gradient",str(row.get("colors",""))+" "+str(row.get("name","")),re.I)
            and row["category"]=="Plastic Sports Water Bottles"):
        kind=({"en":"Gradient Sports Bottle","es":"Botella degradada",
               "pt":"Garrafa degradê","ru":"Градиентная бутылка","tr":"Degrade spor şişesi"}[locale])
    material=verified_source_material(row)
    small={"en":"Bottle","es":"Botella","pt":"Garrafa","ru":"Бутылка","tr":"Şişe"}[locale]
    # Preserve the factory variant distinction, even where translated terms
    # would otherwise push the 60-character suggested SEO width limit.
    short_model=model
    if "透明款" in str(row["model"]):
        numeric=re.match(r"^\d+",str(row["model"]))
        if numeric:
            suffix={
                "en":"Clear","es":"transparente","pt":"transparente",
                "ru":"прозрачн.","tr":"şeffaf"
            }[locale]
            short_model=numeric.group(0)+" "+suffix
    # Prefer the actual category and evidence-backed materials; only shorten
    # them if necessary. Never omit model, real mL, retail oz qualification.
    options=[
        f"{vol} {material+' ' if material else ''}{kind} {model} | XUYI",
        f"{vol} {kind} {model} | XUYI",
        f"{vol} {small} {model} | XUYI",
        f"{vol} {kind} {short_model} | XUYI",
        f"{vol} {small} {short_model} | XUYI",
        f"{vol} {short_model} | XUYI",
    ]
    title=next((candidate for candidate in options if len(candidate)<=60),None)
    if title is None:
        # Future approved multi-size models may need a shorter snippet;
        # leave all exact sizes visible in the H1/spec table and never guess.
        first=format_ml(numbers[0])+" ("+format_oz(numbers[0],locale)+")"
        more=f" +{len(numbers)-1}" if len(numbers)>1 else ""
        title=f"{first}{more} {short_model} | XUYI"
    assert len(title)<=60,(locale,row["slug"],title)
    description=COPY[locale]["description"].format(
       volume=volume_terms(numbers,locale),kind=kind,model=model)
    if len(description)>180:
        # Only shorten the explanatory lead, never truncate the model,
        # accurate capacities or the custom-material qualification.
        description={
         "en":f"{volume_terms(numbers,locale)} model {model}. Ask about custom Tritan or BPA-free material options; confirm parts and testing.",
         "es":f"{volume_terms(numbers,locale)} modelo {model}. Consulte Tritan o materiales sin BPA (BPA-free) a medida; confirme pruebas.",
         "pt":f"{volume_terms(numbers,locale)} modelo {model}. Consulte Tritan ou opções sem BPA (BPA-free) sob medida; confirme testes.",
         "ru":f"{volume_terms(numbers,locale)} модель {model}. Tritan и варианты без BPA (BPA-free) на заказ: уточните испытания.",
         "tr":f"{volume_terms(numbers,locale)} model {model}. Özel Tritan veya BPA içermeyen (BPA-free) seçenekler için testleri doğrulayın.",
        }[locale]
    assert len(description)<=180,(locale,row["slug"],len(description))
    return title,description

def social_meta(head,key,previous,replacement,kind="property"):
    pattern=r'(<meta '+kind+'="'+re.escape(key)+r'" content=")([^"]*)(")'
    def change(m):
        val=unescape(m.group(2))
        return m.group(1)+(escape(replacement,quote=True) if val==previous else m.group(2))+m.group(3)
    return re.sub(pattern,change,head,count=1)

def seo_head(head,locale,row,numbers,owner_override=None):
    if not current_baseline(locale,row,owner_override):return head,False
    old=re.search(r"<title>([^<]*)</title>",head,re.S)
    desc=re.search(r'<meta name="description" content="([^"]*)"',head)
    if not old or not desc:return head,False
    current_title=unescape(old.group(1))
    current_desc=unescape(desc.group(1))
    suggested_title,suggested_desc=new_seo(locale,row,numbers)
    # Product WebPage/OG metadata remains consistent unless an owner set an
    # independent custom social title/description.
    head=social_meta(head,"og:title",current_title,suggested_title)
    head=social_meta(head,"og:description",current_desc,suggested_desc)
    head=head[:old.start(1)]+escape(suggested_title)+head[old.end(1):]
    desc=re.search(r'<meta name="description" content="([^"]*)"',head)