#!/usr/bin/env python3
"""XUYI shared, repeatable volume and customization enrichment.

Explicit D1 product SEO rows are applied after these source recommendations.

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

def source_field_allowed(locale,row,field,data=None):
    """Allow source SEO when a D1 field is absent or still matches its owner baseline."""
    route="/products/"+str(row.get("slug") or "")+"/"
    value=current_field(locale,route,field,data)
    if not isinstance(value,str) or not value.strip():return True
    try:
        from scripts.cms_seo_curation_guard import may_curate
        return may_curate(locale,route,field,data)
    except (ImportError,KeyError,TypeError):
        return current_baseline(locale,row,data)

def verified_source_material(row):
    """Catalog/CMS component list, not an inferred single body resin."""
    raw=str(row.get("material") or "").strip()
    parts=[piece.strip().upper() for piece in raw.replace("/","+").split("+")]
    permitted={"PC","PP","ABS","PE","PETG","TRITAN"}
    if not parts or len(parts)>3 or any(part not in permitted for part in parts):
        return ""
    return "/".join(dict.fromkeys(parts))

_COLOR_TERMS = {
    "en": {"multi":"Multi-Color","gradient":"Gradient","light_blue":"Light Blue","blue":"Blue","black":"Black","white":"White","brown":"Brown","green":"Green","purple":"Purple","pink":"Pink","yellow":"Yellow","red":"Red","transparent":"Transparent","gray":"Gray"},
    "es": {"multi":"Multicolor","gradient":"Degradado","light_blue":"Azul claro","blue":"Azul","black":"Negro","white":"Blanco","brown":"Marrón","green":"Verde","purple":"Morado","pink":"Rosa","yellow":"Amarillo","red":"Rojo","transparent":"Transparente","gray":"Gris"},
    "pt": {"multi":"Multicolor","gradient":"Degradê","light_blue":"Azul-claro","blue":"Azul","black":"Preto","white":"Branco","brown":"Marrom","green":"Verde","purple":"Roxo","pink":"Rosa","yellow":"Amarelo","red":"Vermelho","transparent":"Transparente","gray":"Cinza"},
    "ru": {"multi":"Разноцветный","gradient":"Градиентный","light_blue":"Светло-синий","blue":"Синий","black":"Чёрный","white":"Белый","brown":"Коричневый","green":"Зелёный","purple":"Фиолетовый","pink":"Розовый","yellow":"Жёлтый","red":"Красный","transparent":"Прозрачный","gray":"Серый"},
    "tr": {"multi":"Çok Renkli","gradient":"Degrade","light_blue":"Açık Mavi","blue":"Mavi","black":"Siyah","white":"Beyaz","brown":"Kahverengi","green":"Yeşil","purple":"Mor","pink":"Pembe","yellow":"Sarı","red":"Kırmızı","transparent":"Şeffaf","gray":"Gri"},
}
_COLOR_TOKENS = (
    ("light blue","light_blue"),("浅蓝","light_blue"),
    ("gradient","gradient"),("渐变","gradient"),
    ("transparent","transparent"),("clear","transparent"),("透明","transparent"),
    ("blue","blue"),("蓝","blue"),("black","black"),("黑","black"),
    ("white","white"),("白","white"),("brown","brown"),("棕","brown"),
    ("green","green"),("绿","green"),("purple","purple"),("紫","purple"),
    ("pink","pink"),("粉","pink"),("yellow","yellow"),("黄","yellow"),
    ("red","red"),("红","red"),("gray","gray"),("grey","gray"),("灰","gray"),
)


def verified_source_color_term(locale,row):
    """Return one concise, source-confirmed color modifier; never infer missing colors."""
    raw=row.get("colors")
    if isinstance(raw,(list,tuple,set)):
        raw=" / ".join(str(value) for value in raw)
    text=str(raw or "").strip()
    if not text or re.search(r"not specified|not provided|unknown|tbd|to be confirmed|confirm|unspecified|待确认|待核对|未注明|未指定",text,re.I):
        return ""
    lowered=text.casefold()
    found=[]
    for token,key in _COLOR_TOKENS:
        matched=(token in text) if any(ord(char)>127 for char in token) else bool(re.search(r"\b"+re.escape(token)+r"\b",lowered))
        if matched and key not in found:
            found.append(key)
    if "light_blue" in found and "blue" in found:
        found.remove("blue")
    if not found:
        return ""
    if "gradient" in found:
        key="gradient"
    elif len(found)>1:
        key="multi"
    else:
        key=found[0]
    return _COLOR_TERMS.get(locale,_COLOR_TERMS["en"]).get(key,"")


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

def _seo_kind(locale,row):
    category=row.get("category","")
    if (re.search(r"gradient|渐变",str(row.get("colors",""))+" "+str(row.get("name","")),re.I)
            and category=="Plastic Sports Water Bottles"):
        return {"en":"Gradient Sports Bottle","es":"Botella degradada","pt":"Garrafa degradê","ru":"Градиентная бутылка","tr":"Degrade spor şişesi"}[locale]
    return KIND[locale].get(category,{"en":"Drinkware","es":"Botella","pt":"Garrafa","ru":"Посуда","tr":"Matara"}[locale])

TITLE_KIND={
 "en":{"Plastic Sports Water Bottles":"Sports Bottle","Kids Plastic Water Bottles":"Kids Bottle","Large Capacity Water Jugs":"Water Jug","Plastic Shaker Bottles":"Shaker","Spray Water Bottles":"Spray Bottle","Two-Way Drinking Cups":"Two-Way Cup","Titanium Vacuum Cups":"Titanium Cup"},
 "es":{"Plastic Sports Water Bottles":"Botella","Kids Plastic Water Bottles":"Botella infantil","Large Capacity Water Jugs":"Garrafa","Plastic Shaker Bottles":"Shaker","Spray Water Bottles":"Botella spray","Two-Way Drinking Cups":"Vaso doble","Titanium Vacuum Cups":"Vaso titanio"},
 "pt":{"Plastic Sports Water Bottles":"Garrafa","Kids Plastic Water Bottles":"Garrafa infantil","Large Capacity Water Jugs":"Garrafão","Plastic Shaker Bottles":"Coqueteleira","Spray Water Bottles":"Garrafa spray","Two-Way Drinking Cups":"Copo duplo","Titanium Vacuum Cups":"Copo titânio"},
 "ru":{"Plastic Sports Water Bottles":"Спортбутылка","Kids Plastic Water Bottles":"Детская бутылка","Large Capacity Water Jugs":"Большая бутылка","Plastic Shaker Bottles":"Шейкер","Spray Water Bottles":"Бутылка-распылитель","Two-Way Drinking Cups":"Кружка 2-в-1","Titanium Vacuum Cups":"Титановая кружка"},
 "tr":{"Plastic Sports Water Bottles":"Spor matara","Kids Plastic Water Bottles":"Çocuk matara","Large Capacity Water Jugs":"Büyük matara","Plastic Shaker Bottles":"Shaker","Spray Water Bottles":"Spreyli matara","Two-Way Drinking Cups":"Çift içimli bardak","Titanium Vacuum Cups":"Titanyum bardak"},
}
TWO_WAY_SEO_KIND={
 "en":("Dual-Mode Cup","Travel Cup","Seal-Design Cup","Daily-Use Cup","Dual-Drink Cup"),
 "es":("Vaso doble","Vaso de viaje","Vaso con sello","Vaso diario","Vaso de doble uso"),
 "pt":("Copo duplo","Copo de viagem","Copo com vedação","Copo diário","Copo de dupla função"),
 "ru":("Кружка 2-в-1","Дорожная кружка","Кружка с уплотнением","Повседневная кружка","Кружка с двумя режимами"),
 "tr":("Çift içimli bardak","Seyahat bardağı","Contalı bardak","Günlük bardak","İki içimli bardak"),
}

def _two_way_seo_kind(locale,row):
    model=str(row.get("factoryModel") or row.get("model") or row.get("slug") or "")
    match=re.search(r"(\d+)$",model)
    ordinal=int(match.group(1)) if match else 1
    options=TWO_WAY_SEO_KIND[locale]
    return options[(ordinal-1)%len(options)]

PLASTIC_CATEGORIES={"Plastic Sports Water Bottles","Kids Plastic Water Bottles","Large Capacity Water Jugs","Plastic Shaker Bottles","Spray Water Bottles"}
PLASTIC_LABEL={"en":"Plastic","es":"Plástico","pt":"Plástico","ru":"Пластик","tr":"Plastik"}
CUSTOM_PLASTIC_H1={"en":"Custom Plastic","es":"Plástico personalizable","pt":"Plástico personalizável","ru":"Пластик с индивидуальным подбором","tr":"Özelleştirilebilir plastik"}
TITANIUM_LABEL={"en":"Titanium","es":"Titanio","pt":"Titânio","ru":"Титан","tr":"Titanyum"}
CUSTOM_LABEL={"en":"Custom Material","es":"Material a medida","pt":"Material sob medida","ru":"Материалы на заказ","tr":"Özel malzeme"}

def title_material(locale,row):
    actual=verified_source_material(row)
    if actual:return actual
    category=row.get("category","")
    if category in PLASTIC_CATEGORIES:return PLASTIC_LABEL[locale]
    if category=="Titanium Vacuum Cups":return ""
    if category=="Two-Way Drinking Cups":return CUSTOM_LABEL[locale]
    return ""

def _title_volume(numbers,locale):
    if not numbers:return ""
    # Keep every exact mL value in H1/specs. The title uses the lead capacity
    # plus a variant count when multiple sizes would exceed search-title width.
    if len(numbers)==1:return seo_title_volume(numbers,locale)
    return seo_title_volume((numbers[0],),locale)+f" +{len(numbers)-1}"

def _short_model(row,locale):
    model=slug_label(row,locale)
    if "透明款" in str(row.get("model","")):
        numeric=re.match(r"^\d+",str(row.get("model","")))
        if numeric:
            suffix={"en":"Clear","es":"transp.","pt":"transp.","ru":"прозр.","tr":"Şeffaf"}[locale]
            return numeric.group(0)+" "+suffix
    return model

def _description(locale,row,numbers):
    kind=_seo_kind(locale,row)
    model=slug_label(row,locale)
    volume=(_title_volume(numbers,locale) if len(numbers)>1 else volume_terms(numbers,locale)) if numbers else {
        "en":"capacity to be confirmed","es":"capacidad por confirmar","pt":"capacidade a confirmar",
        "ru":"объём уточняется","tr":"kapasite doğrulanacak"}[locale]
    category=row.get("category","")
    material=verified_source_material(row)
    if category=="Titanium Vacuum Cups":
        templates={
          "en":f"Wholesale titanium cup manufacturer for B2B buyers. {volume}; model {model}. Confirm titanium grade, lid, finish and thermal tests; ask about OEM branding.",
          "es":f"Fabricante B2B mayorista de vasos de titanio. {volume}; modelo {model}. Confirme grado, tapa y pruebas térmicas; consulte marca OEM.",
          "pt":f"Fabricante B2B de copos de titânio para atacado. {volume}; modelo {model}. Confirme grau, tampa e testes térmicos; consulte marca OEM.",
          "ru":f"Производитель титановых термокружек для оптовых B2B-поставок. {volume}; модель {model}. Уточните марку, крышку и испытания; запросите OEM.",
          "tr":f"B2B toptan titanyum bardak üreticisi. {volume}; model {model}. Titanyum kalitesini, kapağı ve testleri doğrulayın; OEM markalamayı sorun.",
        }
    elif category=="Two-Way Drinking Cups":
        angle=_two_way_seo_kind(locale,row)
        templates={
          "en":f"Wholesale {angle.lower()} manufacturer for B2B buyers. {volume}; model {model}. Confirm body, lid and seal materials; ask about OEM logo and bulk packing.",
          "es":f"Fabricante B2B mayorista de {angle.lower()}. {volume}; modelo {model}. Confirme cuerpo, tapa y junta; consulte logotipo OEM y embalaje.",
          "pt":f"Fabricante B2B de {angle.lower()} para atacado. {volume}; modelo {model}. Confirme corpo, tampa e vedação; consulte logotipo OEM e embalagem.",
          "ru":f"Оптовый B2B-производитель: {angle.lower()}. {volume}; модель {model}. Уточните материалы корпуса и крышки, уплотнение и OEM-логотип.",
          "tr":f"B2B toptan {angle.lower()} üreticisi. {volume}; model {model}. Gövde, kapak ve conta malzemelerini doğrulayın; OEM logo ve koli seçeneklerini sorun.",
        }
    else:
        templates={
          "en":f"Wholesale {kind.lower()} manufacturer for B2B buyers. {volume}; model {model}. Ask about OEM logo, custom Tritan/BPA-free materials and colors; confirm resin by SKU.",
          "es":f"Fabricante de {kind.lower()} para mayoristas B2B. {volume}; modelo {model}. Consulte material Tritan/sin BPA a medida, logo OEM y colores; confirme resina por SKU.",
          "pt":f"Fabricante de {kind.lower()} para atacado B2B. {volume}; modelo {model}. Consulte materiais Tritan/sem BPA sob medida, logo OEM e cores; confirme a resina por SKU.",
          "ru":f"Производитель {kind.lower()} для оптовых B2B-поставок. {volume}; модель {model}. Уточните варианты Tritan/BPA-free, OEM-логотип и цвета; проверьте полимер по SKU.",
          "tr":f"B2B toptan {kind.lower()} üreticisi. {volume}; model {model}. Özel Tritan/BPA-free malzeme, OEM logo ve renk seçeneklerini sorun; reçineyi SKU bazında doğrulayın.",
        }
    result=templates[locale]
    if material and category not in {"Titanium Vacuum Cups","Two-Way Drinking Cups"}:
        # The exact component list remains visible on-page; metadata only adds
        # the verified short resin codes when they fit naturally.
        result=result.replace("Ask about OEM logo",f"Listed {material}; ask about OEM logo") if locale=="en" else result
    if len(result)>180:
        # Shorten only the buyer-language lead; preserve model and mL/oz facts.
        buyer_kind=_two_way_seo_kind(locale,row) if category=="Two-Way Drinking Cups" else kind
        result={
          "en":f"B2B wholesale {buyer_kind.lower()} OEM factory. {volume}; model {model}. Ask about custom Tritan/BPA-free materials, logo and packing; confirm components by SKU.",
          "es":f"Fabricante B2B OEM de {buyer_kind.lower()}. {volume}; modelo {model}. Consulte material, logo y embalaje; confirme piezas por SKU.",
          "pt":f"Fabricante B2B OEM de {buyer_kind.lower()} para atacado. {volume}; modelo {model}. Consulte materiais, logo e embalagem; confirme componentes por SKU.",
          "ru":f"Оптовый B2B OEM-производитель: {buyer_kind.lower()}. {volume}; модель {model}. Уточните материалы, логотип и упаковку по SKU.",
          "tr":f"B2B {buyer_kind.lower()} için OEM toptan üretici. {volume}; model {model}. Malzeme, logo ve koli seçeneklerini SKU bazında doğrulayın.",
        }[locale]
    if locale=="en" and category in PLASTIC_CATEGORIES:
        # Keep the source fallback buyer-facing and compact; explicit D1 rows
        # are applied later and remain authoritative.
        result=f"B2B wholesale {kind.lower()} OEM factory. {volume}; model {model}. Ask about custom Tritan/BPA-free materials, logo and packing."
    assert len(result)<=180,(locale,row.get("slug"),len(result),result)
    return result

def new_seo(locale,row,numbers):
    kind=_seo_kind(locale,row)
    model=_short_model(row,locale)
    volume=_title_volume(numbers[:1],locale)
    material=title_material(locale,row)
    base_kind=_two_way_seo_kind(locale,row) if row.get("category")=="Two-Way Drinking Cups" else TITLE_KIND[locale].get(row.get("category",""),kind)
    color=verified_source_color_term(locale,row)
    color_kind=base_kind
    if color and color.casefold() not in base_kind.casefold():
        color_kind=color+" "+base_kind
    # Keep OEM in every candidate; use the source-confirmed color only when
    # the 60-character title limit permits it. The H1 retains the full facts.
    options=[
        f"{volume} {material+' ' if material else ''}{color_kind} OEM {model} | XUYI",
        f"{volume} {color_kind} OEM {model} | XUYI",
        f"{volume} {material+' ' if material else ''}{base_kind} OEM {model} | XUYI",
        f"{volume} {base_kind} OEM {model} | XUYI",
        f"{volume} {model} OEM | XUYI",
    ]
    title=next((candidate for candidate in options if len(candidate)<=60),None)
    if title is None:
        first=seo_title_volume((numbers[0],),locale)
        title=f"{first} {model} OEM | XUYI"
    assert len(title)<=60,(locale,row.get("slug"),title)
    return title,_description(locale,row,numbers)

def new_seo_without_capacity(locale,row):
    kind=_seo_kind(locale,row)
    model=_short_model(row,locale)
    material=title_material(locale,row)
    base_kind=_two_way_seo_kind(locale,row) if row.get("category")=="Two-Way Drinking Cups" else TITLE_KIND[locale].get(row.get("category",""),kind)
    color=verified_source_color_term(locale,row)
    color_kind=base_kind
    if color and color.casefold() not in base_kind.casefold():
        color_kind=color+" "+base_kind
    options=[
        f"{material+' ' if material else ''}{color_kind} OEM {model} | XUYI",
        f"{color_kind} OEM {model} | XUYI",
        f"{material+' ' if material else ''}{base_kind} OEM {model} | XUYI",
        f"{base_kind} OEM {model} | XUYI",
        f"{model} OEM drinkware | XUYI",
    ]
    title=next((candidate for candidate in options if len(candidate)<=60),options[-1])
    desc=_description(locale,row,())
    assert len(title)<=60 and len(desc)<=180,(locale,row.get("slug"),title,desc)
    return title,desc

def social_meta(head,key,previous,replacement,kind="property"):
    pattern=r'(<meta '+kind+'="'+re.escape(key)+r'" content=")([^"]*)(")'
    def change(m):
        val=unescape(m.group(2))
        return m.group(1)+(escape(replacement,quote=True) if val==previous else m.group(2))+m.group(3)
    return re.sub(pattern,change,head,count=1)

def seo_head(head,locale,row,numbers,owner_override=None):
    allow_title=source_field_allowed(locale,row,"title",owner_override)
    allow_desc=source_field_allowed(locale,row,"description",owner_override)
    if not (allow_title or allow_desc):return head,False
    old=re.search(r"<title>([^<]*)</title>",head,re.S)
    desc=re.search(r'<meta name="description" content="([^"]*)"',head)
    if not old or not desc:return head,False
    current_title=unescape(old.group(1));current_desc=unescape(desc.group(1))
    suggested_title,suggested_desc=new_seo(locale,row,numbers)
    changed=False
    if allow_title:
        head=social_meta(head,"og:title",current_title,suggested_title)
        head=head[:old.start(1)]+escape(suggested_title)+head[old.end(1):]
        changed=changed or current_title!=suggested_title
    if allow_desc:
        head=social_meta(head,"og:description",current_desc,suggested_desc)
        desc=re.search(r'<meta name="description" content="([^"]*)"',head)
        head=head[:desc.start(1)]+escape(suggested_desc,quote=True)+head[desc.end(1):]
        changed=changed or current_desc!=suggested_desc
    return head,changed

def seo_head_without_capacity(head,locale,row,owner_override=None):
    allow_title=source_field_allowed(locale,row,"title",owner_override)
    allow_desc=source_field_allowed(locale,row,"description",owner_override)
    if not (allow_title or allow_desc):return head,False
    old=re.search(r"<title>([^<]*)</title>",head,re.S)
    desc=re.search(r'<meta name="description" content="([^"]*)"',head)
    if not old or not desc:return head,False
    current_title=unescape(old.group(1));current_desc=unescape(desc.group(1))
    suggested_title,suggested_desc=new_seo_without_capacity(locale,row)
    changed=False
    if allow_title:
        head=social_meta(head,"og:title",current_title,suggested_title)
        head=head[:old.start(1)]+escape(suggested_title)+head[old.end(1):]
        changed=changed or current_title!=suggested_title
    if allow_desc:
        head=social_meta(head,"og:description",current_desc,suggested_desc)
        desc=re.search(r'<meta name="description" content="([^"]*)"',head)
        head=head[:desc.start(1)]+escape(suggested_desc,quote=True)+head[desc.end(1):]
        changed=changed or current_desc!=suggested_desc
    return head,changed

def product_h1_text(locale,row):
    category=row.get("category","")
    kind=_seo_kind(locale,row)
    color=verified_source_color_term(locale,row)
    if color and color.casefold() not in kind.casefold():
        kind=color+" "+kind
    model=slug_label(row,locale)
    material=verified_source_material(row)
    if not material and category in PLASTIC_CATEGORIES:material=CUSTOM_PLASTIC_H1[locale]
    if category=="Titanium Vacuum Cups":material=""
    numbers=catalog_volume_numbers(row)
    volume=volume_terms(numbers,locale) if numbers else ""
    if category=="Two-Way Drinking Cups":
        # Reuse the exact per-SKU feature/size angle shown on the category card.
        # This keeps the H1 distinct without inventing colors or materials.
        from factory_catalog_locales import _card_title
        card_title=_card_title(row,locale)
        variant,buyer=card_title.split(" | ",1)
        if volume and variant.startswith(volume+" "):
            variant=variant[len(volume)+1:]
        if color and color.casefold() not in variant.casefold():
            variant=color+" "+variant
        if locale=="en":
            lead="Wholesale B2B "+(material+" " if material else "")+variant+" Manufacturer — Model "+model
        elif locale=="es":
            lead="Fabricante B2B mayorista de "+(material+" " if material else "")+variant+" — Modelo "+model
        elif locale=="pt":
            lead="Fabricante B2B de "+(material+" " if material else "")+variant+" para atacado — Modelo "+model
        elif locale=="ru":
            lead="Оптовый B2B-производитель "+(material+" " if material else "")+variant+" — модель "+model
        else:
            lead="Toptan B2B "+(material+" " if material else "")+variant+" üreticisi — Model "+model
        suffix={"en":" · custom material options","es":" · materiales a medida",
                "pt":" · materiais sob medida","ru":" · материалы на заказ",
                "tr":" · özel malzeme seçenekleri"}[locale]
        return lead+(" | "+volume if volume else "")+suffix+" | "+buyer
    if locale=="en":
        lead="Wholesale B2B "+(material+" " if material else "")+kind+" Manufacturer — Model "+model
    elif locale=="es":
        lead="Fabricante B2B mayorista de "+(material+" " if material else "")+kind+" — Modelo "+model
    elif locale=="pt":
        lead="Fabricante B2B de "+(material+" " if material else "")+kind+" para atacado — Modelo "+model
    elif locale=="ru":
        lead="Оптовый B2B-производитель "+(material+" " if material else "")+kind+" — модель "+model
    else:
        lead="Toptan B2B "+(material+" " if material else "")+kind+" üreticisi — Model "+model
    return lead+(" | "+volume if volume else "")
def material_panel(locale,row):
    category=row.get("category","")
    if category in PLASTIC_CATEGORIES:
        heading={"en":"Custom Plastic Materials for OEM Orders","es":"Materiales plásticos a medida para pedidos OEM","pt":"Materiais plásticos sob medida para pedidos OEM","ru":"Индивидуальные полимерные материалы для OEM-заказов","tr":"OEM siparişleri için özel plastik malzemeler"}[locale]
        body={
          "en":"For plastic models, ask about custom PP, PC, PETG, Tritan, PE or ABS options. Confirm the resin grade and the body, lid and seal components for the exact SKU. BPA-free status and food-contact suitability require model-specific evidence; this is a customization inquiry, not a certification claim.",
          "es":"Para modelos de plástico, consulte opciones PP, PC, PETG, Tritan, PE o ABS a medida. Confirme la resina y los componentes del cuerpo, la tapa y la junta del SKU exacto. El estado sin BPA y la aptitud alimentaria requieren pruebas del modelo; es una consulta de personalización, no una certificación.",
          "pt":"Para modelos de plástico, consulte opções PP, PC, PETG, Tritan, PE ou ABS sob medida. Confirme a resina e os componentes do corpo, da tampa e da vedação do SKU exato. A condição sem BPA e a adequação alimentar exigem evidências do modelo; trata-se de consulta de personalização, não de certificação.",
          "ru":"Для пластиковых моделей можно запросить варианты PP, PC, PETG, Tritan, PE или ABS. Уточните марку полимера и материалы корпуса, крышки и уплотнителя конкретного SKU. Статус BPA-free и пригодность для пищевого контакта требуют документов модели; это запрос на индивидуализацию, а не заявление о сертификации.",
          "tr":"Plastik modeller için özel PP, PC, PETG, Tritan, PE veya ABS seçeneklerini sorun. Kesin SKU için reçine sınıfını ve gövde, kapak, conta bileşenlerini doğrulayın. BPA içermeme ve gıda temas uygunluğu modele özel belge gerektirir; bu bir özelleştirme talebidir, sertifika iddiası değildir.",
        }[locale]
    elif category=="Titanium Vacuum Cups":
        heading={"en":"Titanium Grade and Component Options","es":"Grado de titanio y opciones de componentes","pt":"Grau de titânio e opções de componentes","ru":"Марка титана и варианты компонентов","tr":"Titanyum kalitesi ve bileşen seçenekleri"}[locale]
        body={
          "en":"For titanium models, request the exact grade and composition, lid and seal materials, vacuum construction details, finish options and test documents for the selected SKU. Do not infer purity or thermal performance from a family image.",
          "es":"Para modelos de titanio, solicite el grado y la composición exactos, los materiales de la tapa y la junta, la estructura de vacío, los acabados y los ensayos del SKU elegido. No deduzca pureza ni rendimiento térmico de una imagen de familia.",
          "pt":"Para modelos de titânio, solicite o grau e a composição exatos, os materiais da tampa e da vedação, a estrutura a vácuo, os acabamentos e os testes do SKU escolhido. Não presuma pureza ou desempenho térmico por uma imagem de família.",
          "ru":"Для титановых моделей запросите точную марку и состав титана, материалы крышки и уплотнителя, вакуумную конструкцию, отделку и протоколы испытаний выбранного SKU. Не делайте выводы о чистоте или теплоизоляции по общему фото серии.",
          "tr":"Titanyum modellerde seçilen SKU için kesin kaliteyi ve bileşimi, kapak ve conta malzemelerini, vakum yapısını, yüzey seçeneklerini ve test belgelerini isteyin. Seri görselinden saflık veya ısıl performans çıkarmayın.",
        }[locale]
    else:
        heading={"en":"Custom Body, Lid and Component Options","es":"Opciones de cuerpo, tapa y componentes a medida","pt":"Opções de corpo, tampa e componentes sob medida","ru":"Индивидуальные варианты корпуса, крышки и компонентов","tr":"Özel gövde, kapak ve bileşen seçenekleri"}[locale]
        body={
          "en":"Confirm body, lid, drinking valve and seal materials for the exact model. Custom component or material options can be reviewed against the project, sample and destination-market requirements.",
          "es":"Confirme los materiales del cuerpo, la tapa, la válvula y la junta del modelo exacto. Las opciones personalizadas se revisan según el proyecto, la muestra y los requisitos del mercado de destino.",
          "pt":"Confirme os materiais do corpo, da tampa, da válvula e da vedação do modelo exato. As opções personalizadas são avaliadas conforme o projeto, a amostra e os requisitos do mercado de destino.",
          "ru":"Уточните материалы корпуса, крышки, питьевого клапана и уплотнителя конкретной модели. Индивидуальные варианты рассматриваются с учётом проекта, образца и требований рынка.",
          "tr":"Kesin modelin gövde, kapak, içme valfi ve conta malzemelerini doğrulayın. Özel bileşen veya malzeme seçenekleri proje, numune ve hedef pazar gereksinimlerine göre değerlendirilir.",
        }[locale]
    return '<aside class="product-custom-material-options" data-model="'+escape(str(row.get("model","")),quote=True)+'"><h2>'+escape(heading)+'</h2><p>'+escape(body)+'</p></aside>'

DISPUTED_CAPACITY_WARNING={
 "en":"The original catalog lists 60ml for model 2506; this unusual capacity needs factory confirmation before ordering. No overseas oz class is claimed.",
 "es":"El catálogo indica 60ml para 2506; confirme este dato inusual con fábrica antes del pedido. No se declara una clase oz.",
 "pt":"O catálogo indica 60ml para 2506; confirme este dado invulgar com a fábrica antes do pedido. Nenhuma classe oz é declarada.",
 "ru":"В каталоге для модели 2506 указано 60 мл. Просим подтвердить нестандартный объём на заводе; класс oz не заявлен.",
 "tr":"2506 modeli için katalogda 60ml yazıyor. Siparişten önce bu olağandışı hacmi fabrikayla doğrulayın; oz sınıfı belirtilmez.",
}

def capacity_summary(locale,row):
    numbers=catalog_volume_numbers(row)
    if numbers:
        label={"en":"Overseas retail size class","es":"Clase comercial aproximada","pt":"Classe comercial aproximada","ru":"Примерный торговый размер","tr":"Yaklaşık satış boyutu"}[locale]
        return ('<p class="product-capacity-summary" data-volume-us="verified"><strong>'+escape(label)+':</strong> '
            +escape(volume_terms(numbers,locale))+'<small class="product-capacity-disclaimer">'+escape(SIZE_NOTE[locale])+'</small></p>')
    if str(row.get("model"))=="2506":
        return '<p class="product-capacity-warning">'+escape(DISPUTED_CAPACITY_WARNING[locale])+'</p>'
    return ""

def source_body_enrichment(body,locale,row):
    """In-memory source renderer for visible capacity, material and gradient facts."""
    summary=capacity_summary(locale,row)
    if summary and ('class="product-capacity-summary"' not in body and 'class="product-capacity-warning"' not in body):
        if "</table>" in body:body=body.replace("</table>","</table>"+summary,1)
        else:body+=summary
    try:
        from scripts.verified_capacity_gradient_en import render_note
        note=render_note(row,locale)
    except (ImportError,AttributeError):
        note=""
    if note and 'class="product-gradient-finish"' not in body:
        if "</table>" in body:body=body.replace("</table>","</table>"+note,1)
        else:body+=note
    if 'class="product-custom-material-options"' not in body:
        body+=material_panel(locale,row)
    try:
        from scripts.model_catalog_buyer_comparison import render_for_product
        comparison=render_for_product(row,locale)
    except (ImportError,AttributeError):
        comparison=""
    if comparison and 'id="catalog-comparison"' not in body:
        body+=comparison
    return body

CARD_LINK=re.compile(r'(<a\b(?=[^>]*class="product-card\b)[^>]*\bhref="(?P<href>/(?:en/|es/|pt/|ru/|tr/)?products/[^"]+/)"[^>]*>)(?P<body>.*?)</a>',re.S)
def enrich_catalog_body(body,locale,rows):
    """Add capacity and procurement search terms before the source page is written."""
    iterable=rows.values() if isinstance(rows,dict) else rows
    by_slug={str(r.get("slug") or "").strip("/"):r for r in iterable if r.get("slug")}
    def card(match):
        href=match.group("href")
        slug=href.strip("/").split("/")[-1]
        row=by_slug.get(slug)
        if row is None:return match.group(0)
        outer=match.group(1);inner=match.group("body")
        numbers=catalog_volume_numbers(row)
        if numbers and row.get("category")!="Two-Way Drinking Cups" and 'class="product-card__capacity"' not in inner:
            badge='<span class="product-card__capacity">'+escape(volume_terms(numbers,locale))+'</span>'
            inner,n=re.subn(r'(</h3>)',lambda m:m.group(1)+badge,inner,count=1)
        find=re.search(r'\bdata-search="([^"]*)"',outer)
        material=verified_source_material(row)
        terms=volume_terms(numbers,locale) if numbers else str(row.get("capacity") or "")
        procurement={
          "en":"wholesale B2B OEM factory manufacturer custom plastic material options",
          "es":"mayorista B2B fabricante OEM fábrica materiales plásticos a medida",
          "pt":"atacado B2B fabricante OEM fábrica materiais plásticos sob medida",
          "ru":"оптом B2B OEM производитель завод индивидуальные полимерные материалы",
          "tr":"toptan B2B OEM üretici fabrika özel plastik malzeme seçenekleri",
        }[locale]
        add=" "+terms+" "+material+" "+procurement
        if find:
            existing=unescape(find.group(1))
            if procurement not in existing:
                outer=outer[:find.start(1)]+escape((existing+add).strip(),quote=True)+outer[find.end(1):]
        else:
            outer=outer[:-1]+' data-search="' + escape((terms+" "+material+" "+procurement).strip(),quote=True) + '">' 
        return outer+inner+"</a>"
    return CARD_LINK.sub(card,body)

def add_to_heading(heading,numbers,locale="en"):
    if not numbers:return heading
    body=heading;found=set()
    def add(match):
        size=float(match.group(1))
        if size not in numbers or size in found:return match.group(0)
        found.add(size)
        return format_ml(size)+" ("+format_oz(size,locale)+")"
    modified=re.sub(r"(?<!\d)(\d+(?:\.\d+)?)\s*(?:ml|мл)\b",add,body,flags=re.I)
    if found==set(numbers):return modified
    return modified+' <small class="volume-heading-extra">('+escape(volume_terms(numbers,locale))+')</small>'
