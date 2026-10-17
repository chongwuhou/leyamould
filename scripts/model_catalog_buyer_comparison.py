#!/usr/bin/env python3
"""Add genuinely model-specific, source-catalog product comparisons to five locales.

No prices, availability, test results, certifications or unverified factory
models are invented. G-series factory models and LO manual records without source-catalog comparison data are excluded.
This is a non-destructive release enrichment of generated static HTML.
"""
from html import escape
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from site_renderer import SERIES
from product_content import capacity_en, material_en

LOCALES = ("en", "es", "pt", "ru", "tr")
SOURCE_LABELS={
    "en":"SOURCE CATALOG",
    "es":"CATÁLOGO DE ORIGEN",
    "pt":"CATÁLOGO ORIGINAL",
    "ru":"ИСХОДНЫЙ КАТАЛОГ",
    "tr":"KAYNAK KATALOG",
}
LANG = {
    "en": {
        "title":"Compare this model with catalog alternatives",
        "intro":"These entries are from the source catalog, not confirmed live inventory. Compare capacity and listed materials; request the exact finished-product specification before ordering.",
        "model":"Catalog model", "capacity":"Listed capacity", "material":"Listed materials",
        "carton":"Listed units/carton", "next":"Inspect model",
        "unknown":"Confirm with XUYI", "capacityUnknown":"Catalog figure disputed; confirm before quoting",
        "faqTitle":"Model-specific quotation checks",
        "known":"What the catalog already states",
        "unknownTitle":"What must be confirmed",
        "qty":"units per master carton",
        "packing":"unit packing",
        "colors":"available colors",
        "capacityLabel":"capacity",
        "materialLabel":"materials",
        "lead":"Use model {model} when asking for a quote. For a like-for-like offer, confirm sample revision, the complete lid/seal assembly, customization feasibility, carton quantities and destination-market documentation.",
        "disclaimer":"Dimensions, components, colors and packaging may vary by variant; listed catalog data are references, not a warranty, compliance certificate or stock confirmation."
        ,"verifyAssembly":"Also confirm the exact lid and seal revision, logo decoration, filled-product suitability, food-contact documents for your market and the agreed shipping terms."
    },
    "es": {
        "title":"Compare este modelo con alternativas del catálogo",
        "intro":"Datos del catálogo de origen, no disponibilidad de inventario. Compare capacidades y materiales y confirme las especificaciones del producto final antes del pedido.",
        "model":"Modelo", "capacity":"Capacidad del catálogo", "material":"Materiales del catálogo",
        "carton":"Unidades por caja", "next":"Ver modelo",
        "unknown":"Confirmar con XUYI", "capacityUnknown":"Capacidad no confirmada",
        "faqTitle":"Comprobaciones para cotizar este modelo", "known":"Datos del catálogo",
        "unknownTitle":"Datos que deben confirmarse", "qty":"unidades por caja",
        "packing":"embalaje unitario", "colors":"colores disponibles",
        "capacityLabel":"capacidad", "materialLabel":"materiales",
        "lead":"Indique el modelo {model} al solicitar precio. Confirme la muestra, tapa y junta, personalización, cajas y documentación del mercado de destino.",
        "disclaimer":"Los datos del catálogo son orientativos; no confirman existencias, certificaciones ni prestaciones del producto final."
        ,"verifyAssembly":"Confirme además la versión de tapa y junta, decoración, condiciones de uso, documentos de contacto alimentario y condiciones de envío."
    },
    "pt": {
        "title":"Compare este modelo com alternativas do catálogo",
        "intro":"Dados do catálogo original, não estoque confirmado. Compare capacidade e materiais e solicite a especificação do produto final antes de comprar.",
        "model":"Modelo", "capacity":"Capacidade do catálogo", "material":"Materiais do catálogo",
        "carton":"Unidades por caixa", "next":"Ver modelo", "unknown":"Confirmar com XUYI",
        "capacityUnknown":"Capacidade a confirmar",
        "faqTitle":"Verificações para cotar este modelo", "known":"Dados indicados no catálogo",
        "unknownTitle":"Informações a confirmar", "qty":"unidades por caixa",
        "packing":"embalagem unitária", "colors":"cores disponíveis",
        "capacityLabel":"capacidade", "materialLabel":"materiais",
        "lead":"Informe o modelo {model} ao pedir uma cotação. Confirme amostra, tampa e vedação, personalização, caixas e documentação para o mercado de destino.",
        "disclaimer":"As informações do catálogo são referências, não garantias de estoque, certificação ou desempenho do produto acabado."
        ,"verifyAssembly":"Confirme também a tampa e vedação, decoração, uso previsto, documentos de contacto alimentar e condições de transporte."
    },
    "ru": {
        "title":"Сравнение с другими моделями каталога",
        "intro":"Данные исходного каталога, а не наличие на складе. Сравните объем и материалы, затем запросите спецификацию готового изделия.",
        "model":"Модель", "capacity":"Объем по каталогу", "material":"Материалы по каталогу",
        "carton":"Штук в коробке", "next":"Модель", "unknown":"Уточнить у XUYI",
        "capacityUnknown":"Объем требует уточнения",
        "faqTitle":"Проверка условий заказа модели", "known":"Что указано в каталоге",
        "unknownTitle":"Что необходимо уточнить", "qty":"штук в коробке",
        "packing":"упаковка единицы", "colors":"доступные цвета",
        "capacityLabel":"объем", "materialLabel":"материалы",
        "lead":"Укажите модель {model} в запросе. Уточните утвержденный образец, крышку и уплотнения, нанесение логотипа, упаковку и документы для рынка назначения.",
        "disclaimer":"Данные каталога не подтверждают складские остатки, сертификацию или характеристики готового изделия."
        ,"verifyAssembly":"Дополнительно уточните версию крышки и уплотнения, нанесение логотипа, условия использования, пищевые документы и условия доставки."
    },
    "tr": {
        "title":"Bu modeli katalog alternatifleriyle karşılaştırın",
        "intro":"Bunlar stok bilgisi değil, kaynak katalog verileridir. Kapasite ve malzemeleri karşılaştırıp bitmiş ürün özelliklerini siparişten önce doğrulayın.",
        "model":"Model", "capacity":"Katalog kapasitesi", "material":"Katalog malzemesi",
        "carton":"Koli başına adet", "next":"Modeli incele", "unknown":"XUYI ile doğrulayın",
        "capacityUnknown":"Kapasite doğrulanmalı",
        "faqTitle":"Modele özel teklif kontrolleri", "known":"Katalogda belirtilenler",
        "unknownTitle":"Doğrulanması gerekenler", "qty":"koli başına adet",
        "packing":"tekli paketleme", "colors":"mevcut renkler",
        "capacityLabel":"kapasite", "materialLabel":"malzemeler",
        "lead":"Teklif talebinizde {model} modelini belirtin. Numune, kapak ve conta, özelleştirme, koli sayısı ve hedef pazar belgelerini doğrulayın.",
        "disclaimer":"Katalog verileri referanstır; stok, sertifika veya nihai ürün performansı garantisi değildir."
        ,"verifyAssembly":"Kapak ve conta sürümünü, baskıyı, kullanım koşullarını, gıda temas belgelerini ve teslimat şartlarını da doğrulayın."
    },
}

def raw_value(row, field):
    unique=[]
    for item in row["variants"]:
        value = str(item.get(field) or "").strip()
        if value and value not in unique:
            unique.append(value)
    return unique

def capacity_number(row):
    if str(row["model"])=="2506":
        return None
    numbers=[]
    for value in raw_value(row,"capacity"):
        m=re.search(r"(\d+(?:\.\d+)?)\s*ml\b",value,re.I)
        if m: numbers.append(float(m.group(1)))
    if not numbers or not all(50<=x<=10000 for x in numbers):
        return None
    return min(numbers)

def capacity_text(row, words):
    num = capacity_number(row)
    return (f"{num:g} mL" if num is not None else words["capacityUnknown"])

def material_text(row, words):
    vals=[material_en(x) for x in raw_value(row,"material")]
    return " / ".join(vals[:3]) if vals else words["unknown"]

def quantity_text(row, words):
    vals=raw_value(row,"carton_quantity")
    verified=[v for v in vals if re.fullmatch(r"\d{1,4}",v) and int(v)>0]
    return " / ".join(verified[:3]) if verified else words["unknown"]

def peers(row, models):
    category=row["category"]
    same=[r for r in models if r["category"]==category and r["model"]!=row["model"] and capacity_number(r) is not None]
    baseline=capacity_number(row)
    if baseline is None:
        return sorted(same,key=lambda r:(capacity_number(r),str(r["model"])))[:3]
    return sorted(same,key=lambda r:(abs(capacity_number(r)-baseline),capacity_number(r),str(r["model"])))[:3]

def html_for(row, selection, lang):
    words=LANG[lang]
    prefix="" if lang=="en" else lang+"/"
    info=[(words["capacityLabel"],capacity_text(row,words)),
          (words["materialLabel"],material_text(row,words)),
          (words["qty"],quantity_text(row,words))]
    known=[f"{label}: {value}" for label,value in info if value not in (words["unknown"],words["capacityUnknown"])]
    unknown=[label for label,value in info if value in (words["unknown"],words["capacityUnknown"])]
    for label,field in ((words["packing"],"packing"),(words["colors"],"colors")):
        if not raw_value(row,field): unknown.append(label)
    # Buyer calls are explicit rather than generic/unverifiable marketing.
    disclaimer='<p class="catalog-compare__disclaimer">'+escape(words["disclaimer"])+'</p>'
    details=(
        '<div class="catalog-compare__brief"><div><h3>'+escape(words["known"])+'</h3><p>'+
        escape("; ".join(known) if known else words["unknown"])+'</p></div>'+
        '<div><h3>'+escape(words["unknownTitle"])+'</h3><p>'+
        escape(("; ".join(unknown)+". " if unknown else "")+words["verifyAssembly"])+'</p></div></div>'
    )
    columns=(words["model"],words["capacity"],words["material"],words["carton"])
    table='<div class="catalog-compare__scroll"><table><thead><tr>'+''.join('<th scope="col">'+escape(x)+'</th>' for x in columns)+'</tr></thead><tbody>'
    for other in selection:
        route="/"+prefix+"products/"+escape(str(other["slug"]),quote=True)+"/"
        table+=('<tr><th scope="row"><a href="'+route+'">'+escape(str(other["model"]))+'</a></th>'+
                '<td>'+escape(capacity_text(other,words))+'</td><td>'+escape(material_text(other,words))+
                '</td><td>'+escape(quantity_text(other,words))+'</td></tr>')
    table+='</tbody></table></div>'
    intro=(words["intro"] if capacity_number(row) is not None
           else words["intro"]+" "+words["capacityUnknown"]+".")
    return (
        '<section class="section catalog-compare" id="catalog-comparison"><div class="shell">'
        '<div class="section__head"><div><span class="eyebrow">XUYI · '+escape(SOURCE_LABELS[lang])+'</span>'
        '<h2 class="section__title">'+escape(words["title"])+'</h2>'
        '<p>'+escape(intro)+'</p></div></div>'
        +table+'<h3 class="catalog-compare__check-title">'+escape(words["faqTitle"])+'</h3>'
        +details+'<p>'+escape(words["lead"].format(model=row["model"]))+'</p>'
        +disclaimer+'</div></section>'
    )

def apply(dist):
    dist=Path(dist)
    models=[r for r in SERIES.values() if not r.get("manualNew")]
    if len(models)<85:
        raise ValueError(f"Source-catalog baseline models missing: {len(models)}")
    edits=0
    for row in models:
        nearby=peers(row,models)
        if len(nearby)!=3:
            raise ValueError("Fewer than 3 approved model alternatives: "+str(row["model"]))
        for lang in LOCALES:
            prefix="" if lang=="en" else lang+"/"
            file=dist/prefix/"products"/str(row["slug"])/"index.html"
            source=file.read_text(encoding="utf8")
            # Existing comparison blocks may be a CMS owner revision or a
            # previous pass of this builder; never replace or duplicate them.
            existing=source.count('id="catalog-comparison"')
            if existing>1 or source.count("</main>")!=1:
                raise ValueError("Unexpected product body: "+str(file))
            if existing==1:
                continue
            content=html_for(row,nearby,lang)
            for other in nearby:
                path=dist/prefix/"products"/str(other["slug"])/"index.html"
                if not path.is_file():
                    raise FileNotFoundError(str(path))
            file.write_text(source.replace("</main>",content+"</main>",1),encoding="utf8")
            edits+=1
    print("XUYI_MODEL_FACT_BACKED_COMPARISONS",edits,"new;",len(models),"source-catalog models in five locales; existing editor blocks preserved")
    return edits

if __name__=="__main__":
    apply(ROOT/"dist")
