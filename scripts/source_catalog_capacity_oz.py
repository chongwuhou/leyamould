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
       "Large Capacity Water Jugs":"Large Water Jug","Plastic Shaker Bottles":"Protein Shaker"},
 "es":{"Plastic Sports Water Bottles":"Botella deportiva","Kids Plastic Water Bottles":"Botella infantil",
       "Large Capacity Water Jugs":"Botella de gran capacidad","Plastic Shaker Bottles":"Vaso mezclador"},
 "pt":{"Plastic Sports Water Bottles":"Garrafa esportiva","Kids Plastic Water Bottles":"Garrafa infantil",
       "Large Capacity Water Jugs":"Garrafa grande","Plastic Shaker Bottles":"Coqueteleira"},
 "ru":{"Plastic Sports Water Bottles":"Спортивная бутылка","Kids Plastic Water Bottles":"Детская бутылка",
       "Large Capacity Water Jugs":"Большая бутылка","Plastic Shaker Bottles":"Шейкер"},
 "tr":{"Plastic Sports Water Bottles":"Spor su şişesi","Kids Plastic Water Bottles":"Çocuk su şişesi",
       "Large Capacity Water Jugs":"Büyük su şişesi","Plastic Shaker Bottles":"Protein shaker"},
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
    head=head[:desc.start(1)]+escape(suggested_desc,quote=True)+head[desc.end(1):]
    return head,(current_title!=suggested_title or current_desc!=suggested_desc)

def seo_head_without_capacity(head,locale,row,owner_override=None):
    """Polish conditional material SEO without claiming an unknown capacity.

    The source description SHA protects later G-series template author edits;
    the CMS snapshot hash independently guards later D1 SEO changes.
    """
    if not current_baseline(locale,row,owner_override):return head,False
    desc=re.search(r'<meta name="description" content="([^"]*)"',head)
    if not desc:return head,False
    current=unescape(desc.group(1))
    slug=row["slug"]
    previous=NO_CAPACITY_META_DIGESTS.get(slug,{}).get(locale)
    if not previous or hashlib.sha256(current.encode("utf8")).hexdigest()!=previous:
        return head,False
    updated=NO_CAPACITY_MARKETING[locale].format(model=str(row["model"]))
    assert len(updated)<=180,(locale,slug,len(updated))
    head=social_meta(head,"og:description",current,updated)
    desc=re.search(r'<meta name="description" content="([^"]*)"',head)
    head=head[:desc.start(1)]+escape(updated,quote=True)+head[desc.end(1):]
    return head,True


def add_to_heading(heading,numbers,locale="en"):
    if not numbers:return heading
    body=heading
    found=set()
    def add(m):
        size=float(m.group(1))
        if size not in numbers or size in found:
            return m.group(0)
        if re.match(r"\s*\(\d+\s*(?:US\s*fl\s*oz|fl\s*oz|oz)\)",body[m.end():],re.I):
            found.add(size)
            return m.group(0)
        found.add(size)
        return format_ml(size)+" ("+format_oz(size,locale)+")"
    # Russian product headings use the Cyrillic abbreviation «мл».
    heading_volume=re.compile(r"(?<!\d)(\d+(?:\.\d+)?)\s*(?:ml|мл)\b",re.I)
    modified=heading_volume.sub(add,body)
    if found==set(numbers):return modified
    # Common shaker headings omit capacity. Leave the approved heading intact
    # and display the correctly sourced available capacities next to it.
    return modified+' <small class="volume-heading-extra">('+escape(volume_terms(numbers,locale))+')</small>'

def material_panel(locale,row):
    copy=COPY[locale]
    return ('<aside class="product-custom-material-options" data-model="'
       +escape(str(row["model"]),quote=True)+'">'
       '<h2>'+escape(copy["heading"])+'</h2><p>'+escape(copy["body"])+'</p></aside>')

DISPUTED_CAPACITY_WARNING={
  "en":"The original catalog lists 60ml for model 2506; this unusual capacity needs factory confirmation before ordering. No overseas oz class is claimed.",
  "es":"El catálogo indica 60ml para 2506; confirme este dato inusual con fábrica antes del pedido. No se declara una clase oz.",
  "pt":"O catálogo indica 60ml para 2506; confirme este dado invulgar com a fábrica antes do pedido. Nenhuma classe oz é declarada.",
  "ru":"В каталоге для модели 2506 указано 60 мл. Просим подтвердить нестандартный объём на заводе; класс oz не заявлен.",
  "tr":"2506 modeli için katalogda 60ml yazıyor. Siparişten önce bu olağandışı hacmi fabrikayla doğrulayın; oz sınıfı belirtilmez.",
}

def enrich_detail(path,locale,row,owner_override=None):
    source=path.read_text(encoding="utf8")
    old=source
    numbers=catalog_volume_numbers(row)
    head,sep,body=source.partition("</head>")
    if not sep:raise ValueError("Missing product HTML head: "+str(path))
    if numbers:
        # Titles and H1 are now owned by pre_render_verified_meta and the
        # source product identity component before page output. The remaining
        # legacy summary is not allowed to rewrite either field.
        if 'class="product-capacity-summary"' not in body:
            summary=('<p class="product-capacity-summary" data-volume-us="verified"><strong>'
                     +escape({"en":"Overseas size class","es":"Clase comercial aproximada","pt":"Classe de tamanho comercial","ru":"Примерный торговый размер","tr":"Yaklaşık satış boyutu"}[locale])+':</strong> '
                     +escape(volume_terms(numbers,locale))+'<small class="product-capacity-disclaimer">'
                     +escape(SIZE_NOTE[locale])+'</small></p>')
            # Insert after the specification table (unmodified original SKU data).
            body,n=re.subn(r'(</table>)',lambda m:m.group(1)+summary,body,count=1)
            if not n:body=body.replace("</main>",summary+"</main>",1)
    # SEO metadata is now strictly pre-render or D1-owned; this detail
    # enrichment may add only source-checked visible body content.
    # Flag the actual doubtful source field and clear this flag automatically
    # if the owner later supplies a verified corrected capacity through D1.
    if str(row.get("model"))=="2506" and not numbers and 'class="product-capacity-warning"' not in body:
        flag='<p class="product-capacity-warning">'+escape(DISPUTED_CAPACITY_WARNING[locale])+'</p>'
        body,n=re.subn(r'(</table>)',lambda m:m.group(1)+flag,body,count=1)
        if not n:body=body.replace('</main>',flag+'</main>',1)
    # ALL factory-model detail pages, including G-series with unknown volume,
    # may invite a *custom-material feasibility inquiry*. No factual material
    # claim or existing D1-edited panel is ever removed.
    if 'class="product-custom-material-options"' not in body:
        panel=material_panel(locale,row)
        if "</main>" not in body:raise ValueError("Missing Product main element: "+str(path))
        body=body.replace("</main>",panel+"</main>",1)
    result=head+sep+body
    if result!=old:path.write_text(result,encoding="utf8")
    return int(result!=old),int(bool(numbers))

CARD_LINK=re.compile(r'(<a\b(?=[^>]*class="product-card\b)[^>]*\bhref="(?P<href>/[^"]+/products/[^"]+/|/products/[^"]+/)"[^>]*>)(?P<body>.*?)</a>',re.S)
def enrich_cards(page,rows):
    source=page.read_text(encoding="utf8")
    changes=[0]
    def card(m):
        slug=m.group("href").strip("/").split("/")[-1]
        row=rows.get(slug)
        if row is None:return m.group(0)
        numbers=catalog_volume_numbers(row)
        if not numbers:return m.group(0)
        outer=m.group(1)
        inner=m.group("body")
        if 'class="product-card__capacity"' in inner:return m.group(0)
        locale=next((loc for loc in LOCALES if m.group("href").startswith('/'+loc+'/')),"en")
        badge='<span class="product-card__capacity">'+escape(volume_terms(numbers,locale))+'</span>'
        inner,n=re.subn(r'(</h3>)',lambda x:x.group(1)+badge,inner,count=1)
        if not n:return m.group(0)
        find=re.search(r'\bdata-search="([^"]*)"',outer)
        if find:
            to_add=" "+ " ".join(oz_number(v)+"oz-class" for v in numbers)
            # Search corpus also includes accurate conditional *custom* inquiry.
            to_add+=" custom Tritan BPA-free material options"
            outer=outer[:find.end(1)]+escape(to_add,quote=True)+outer[find.end(1):]
        changes[0]+=1
        return outer+inner+"</a>"
    result=CARD_LINK.sub(card,source)
    if result!=source:page.write_text(result,encoding="utf8")
    return changes[0]

def apply(dist,owner_override=None):
    dist=Path(dist)
    rows={r["slug"]:r for r in SERIES.values()}
    modified=with_volume=0
    for slug,row in rows.items():
        for locale in LOCALES:
            prefix="" if locale=="en" else locale+"/"
            file=dist/prefix/"products"/slug/"index.html"
            if not file.is_file():
                # Future overflow products are served separately in R2, not
                # silently implied to be present in the Pages static build.
                continue
            changed,has_volume=enrich_detail(file,locale,row,owner_override)
            modified+=changed;with_volume+=has_volume
    cards=0
    for file in dist.rglob("index.html"):
        if file.relative_to(dist).parts[0]=="admin":continue
        cards+=enrich_cards(file,rows)
    print("XUYI_SOURCE_VOLUME_US_FL_OZ",with_volume,"product locale pages with verified capacity;",
          len(rows),"factory models;",modified,"details enriched;",
          cards,"catalog cards updated; all 5 languages; Tritan/BPA-free strictly conditional")
    return with_volume,modified,cards

if __name__=="__main__":apply(ROOT/"dist")
