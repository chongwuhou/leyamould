"""Small five-language material block, sourced from the actual SKU catalog.

No backend fields, prices, heat limits, food-contact or BPA certifications are
inferred. A combined PC+PP+ABS material list is NOT a bill of materials.
"""
import html
import re
from urllib.parse import quote
from sku_factual_sections import material_annotation, PEERS, FOCUS, MATERIAL_VARIATION, facts as sku_facts

GUIDE="/blog/plastic-bottle-material-selection/"
TEXT={
 "en":("MATERIALS & PERFORMANCE","Materials and practical use",
 "Catalog-listed materials","Listed polymers do not identify which material forms the bottle body, lid or seal.",
 "Material characteristics to discuss","General resin-family characteristics, not verified performance claims for this finished bottle.",
 "Component and safety checks","Confirm body, lid and gasket materials; BPA-free status, temperature limits, dishwasher suitability and destination-market food-contact documents for the exact SKU.",
 "Request materials & samples","Material comparison guide"),
 "es":("MATERIALES Y RENDIMIENTO","Materiales y uso práctico",
 "Materiales del catálogo","La lista no identifica el material del cuerpo, la tapa o la junta.",
 "Propiedades de materiales a consultar","Características generales de las resinas; no son prestaciones verificadas de esta botella.",
 "Componentes y seguridad","Confirme cuerpo, tapa y junta; ausencia de BPA, límites térmicos, lavavajillas y documentos de contacto alimentario del modelo exacto.",
 "Consultar materiales y muestras","Guía comparativa de materiales"),
 "pt":("MATERIAIS E DESEMPENHO","Materiais e uso prático",
 "Materiais do catálogo","A lista não identifica o material do corpo, da tampa ou da vedação.",
 "Características dos materiais","Características gerais das resinas; não são desempenho verificado desta garrafa.",
 "Componentes e segurança","Confirme corpo, tampa e vedação; estado livre de BPA, limites térmicos, lavagem na máquina e documentos de contacto alimentar do modelo exato.",
 "Consultar materiais e amostras","Guia de comparação de materiais"),
 "ru":("МАТЕРИАЛЫ И СВОЙСТВА","Материалы и применение",
 "Материалы по каталогу","Общий список материалов не показывает состав корпуса, крышки и уплотнителя.",
 "Особенности материалов","Общие свойства полимеров, а не подтверждённые характеристики готовой бутылки.",
 "Состав и безопасность","Уточните материалы корпуса, крышки и уплотнителя, отсутствие BPA, температуру, посудомоечную машину и документы для пищевого контакта именно этой модели.",
 "Запросить материалы и образцы","Сравнение материалов"),
 "tr":("MALZEMELER VE PERFORMANS","Malzemeler ve kullanım",
 "Katalog malzemeleri","Birleşik liste gövdenin, kapağın veya contanın malzemesini belirtmez.",
 "Malzeme özellikleri","Genel polimer özellikleridir; bu şişenin doğrulanmış performansı değildir.",
 "Bileşenler ve güvenlik","Bu model için gövde, kapak ve contayı; BPA durumunu, sıcaklık sınırını, bulaşık makinesini ve gıda temas belgelerini doğrulayın.",
 "Malzeme ve numune iste","Malzeme karşılaştırma rehberi")
}
TRAITS={
 "PC":{
  "en":"PC: often chosen for clarity and toughness; check BPA-related resin chemistry.",
  "es":"PC: transparencia y tenacidad; compruebe la composición relacionada con BPA.",
  "pt":"PC: transparência e resistência; confirme a composição relacionada com BPA.",
  "ru":"PC: прозрачность и прочность; уточните состав с учётом BPA.",
  "tr":"PC: şeffaflık ve tokluk; BPA ile ilgili reçine bileşimini kontrol edin."},
 "PP":{
  "en":"PP: a lightweight polyolefin; grade and component use must be confirmed.",
  "es":"PP: poliolefina ligera; confirme el grado y la pieza.",
  "pt":"PP: poliolefina leve; confirme o grau e a peça.",
  "ru":"PP: лёгкий полиолефин; уточните марку и применяемую деталь.",
  "tr":"PP: hafif poliolefin; reçine sınıfını ve kullanıldığı parçayı doğrulayın."},
 "ABS":{
  "en":"ABS: often used for rigid molded parts; do not assume food-contact suitability.",
  "es":"ABS: habitual en piezas rígidas; no presuponga aptitud alimentaria.",
  "pt":"ABS: comum em peças rígidas; não presuma aptidão alimentar.",
  "ru":"ABS: для жёстких деталей; пригодность для пищевого контакта не подразумевается.",
  "tr":"ABS: sert kalıplanmış parçalar için; gıda temas uygunluğunu varsaymayın."},
 "PE":{
  "en":"PE: a polyolefin family whose flexibility and use depend on grade.",
  "es":"PE: poliolefina con propiedades según el grado.",
  "pt":"PE: poliolefina com propriedades conforme o grau.",
  "ru":"PE: свойства полиолефина зависят от марки.",
  "tr":"PE: özellikleri reçine sınıfına bağlı poliolefin."},
 "silicone":{
  "en":"Silicone: may be used in flexible parts; verify the actual component.",
  "es":"Silicona: posible material flexible; confirme la pieza real.",
  "pt":"Silicone: possível material flexível; confirme a peça.",
  "ru":"Силикон: для гибких деталей; уточните компонент.",
  "tr":"Silikon: esnek parçalarda kullanılabilir; bileşeni doğrulayın."},
 "PETG":{
  "en":"PETG: clear copolyester; verify grade-specific temperature limits.",
  "es":"PETG: copoliéster transparente; confirme límites térmicos del grado.",
  "pt":"PETG: copoliéster transparente; confirme os limites térmicos do grau.",
  "ru":"PETG: прозрачный сополиэфир; уточните температурный предел марки.",
  "tr":"PETG: şeffaf kopolyester; reçine sınıfının sıcaklık sınırını doğrulayın."},
 "Tritan":{
  "en":"Tritan: transparent copolyester; check the exact grade and supplier evidence.",
  "es":"Tritan: copoliéster transparente; confirme el grado y los documentos.",
  "pt":"Tritan: copoliéster transparente; confirme o grau e os documentos.",
  "ru":"Tritan: прозрачный сополиэфир; уточните марку и документы.",
  "tr":"Tritan: şeffaf kopolyester; reçine sınıfını ve belgeleri doğrulayın."}
}

def material_codes(product):
    variants=product.get("variants") or []
    sources=list(dict.fromkeys(str(v.get("material","")).strip() for v in variants if isinstance(v,dict) and v.get("material")))
    raw=" / ".join(sources)
    codes=[]
    for family in TRAITS:
        if family=="silicone":
            found="硅胶" in raw or bool(re.search(r"\bsilicone\b",raw,re.I))
        else:
            found=bool(re.search(r"(?<![A-Za-z])"+re.escape(family)+r"(?![A-Za-z])",raw,re.I))
        if found:codes.append(family)
    return sources,codes

FACT_LABELS={
 "en":("Source catalog: model-specific buying facts","Capacity listed","Carton pack listed","Carton size listed","Figures are catalog references; confirm the exact variant, sample and final packing before ordering."),
 "es":("Datos de compra del modelo según catálogo","Capacidad indicada","Unidades por caja","Medidas de caja","Datos del catálogo; confirme la variante, la muestra y el embalaje final antes del pedido."),
 "pt":("Dados de compra por modelo no catálogo","Capacidade indicada","Unidades por caixa","Dimensões da caixa","Dados do catálogo; confirme a variante, a amostra e a embalagem final antes de encomendar."),
 "ru":("Данные по конкретной модели из каталога","Объём по каталогу","Штук в коробке","Размер коробки","Данные каталога: перед заказом уточните вариант, образец и конечную упаковку."),
 "tr":("Katalogda modele özel satın alma bilgileri","Katalog kapasitesi","Koli adedi","Koli ölçüleri","Katalog verileridir; siparişten önce seçeneği, numuneyi ve ambalajı doğrulayın.")
}

def catalog_purchase_facts(product, locale):
    """Distinct real catalog values, never performance claims or invented specs."""
    if product.get("galleryReference"):
        return ""
    variants=product.get("variants") or []
    labels=FACT_LABELS[locale]
    def values(field, pattern):
        found=[]
        for item in variants:
            raw=str(item.get(field) or "").strip()
            value=re.fullmatch(pattern,raw,re.I)
            if value and raw not in found:found.append(raw)
        return found[:3]
    # Shaker slides combine a capacity and Chinese product-size annotation
    # in one source field. Only take the part BEFORE 产品尺寸; keep 2506's
    # documented anomalous capacity entirely out of the new prose.
    capacities=[]
    if str(product.get("model"))!="2506":
        for item in variants:
            head=str(item.get("capacity") or "").split("产品尺寸",1)[0]
            for value in re.findall(r"\d+(?:\.\d+)?\s*ml\b",head,re.I):
                normalized=re.sub(r"\s+","",value)
                if normalized not in capacities:capacities.append(normalized)
        capacities=capacities[:3]
    quantities=values("carton_quantity",r"\d{1,4}")
    cartons=values("carton_size",r"\d+(?:\.\d+)?\s*[*×x]\s*\d+(?:\.\d+)?\s*[*×x]\s*\d+(?:\.\d+)?")
    facts=[(labels[1]," / ".join(capacities)),
           (labels[2]," / ".join(x+" pcs" for x in quantities)),
           (labels[3]," / ".join(x+" cm" for x in cartons))]
    facts=[(k,v) for k,v in facts if v]
    if not facts:return ""
    esc=lambda s:html.escape(str(s),quote=True)
    model=esc(product.get("model",""))
    rows="".join('<li><strong>'+esc(k)+':</strong> '+esc(v)+'</li>' for k,v in facts)
    return ('<div class="material-brief__catalog-facts"><h3>'+esc(labels[0])+' · '+model+
            '</h3><ul>'+rows+'</ul><p class="material-brief__note">'+esc(labels[4])+
            '</p></div>')

def render(product,locale,route,approved_routes=None):
    if locale not in TEXT:raise ValueError("Missing reviewed material copy for "+locale)
    words=TEXT[locale]
    escape=lambda s:html.escape(str(s),quote=True)
    sources,codes=material_codes(product)
    raw=" / ".join(sources[:4]) if sources else "—"
    overview="<ul class=\"material-brief__traits\">"+"".join(
        "<li>"+escape(TRAITS[key][locale])+"</li>" for key in codes)+"</ul>" if codes else ""
    prefix="" if locale=="en" else "/"+locale
    guide=GUIDE if locale!="en" and approved_routes is not None and GUIDE not in approved_routes else prefix+GUIDE
    contact=prefix+"/contact/?model="+quote(str(product["model"]),safe="")+"#inquiry"
    def item(heading,content):
        return '<div class="material-brief__item"><h3>'+escape(heading)+'</h3>'+content+'</div>'
    # Curated 20-SKU material briefs replace generic resin-family boilerplate
    # with verified model facts. The combined material field NEVER assigns
    # body/lid/seal chemistry, nor establishes certification or test results.
    if product.get("slug") in PEERS:
        from site_renderer import SERIES
        specific=sku_facts(product,locale,SERIES)
        source_variation=MATERIAL_VARIATION[locale].format(**specific)
        model_focus=FOCUS[product["slug"]][locale].split(". ",1)[0].rstrip(".")+"."
        evidence=material_annotation(product,locale)
        return (
         '<section class="section material-brief" id="material-performance" aria-labelledby="material-performance-title">'
         '<div class="shell"><div class="section__head"><div>'
         '<span class="eyebrow">'+escape(words[0])+'</span>'
         '<h2 class="section__title" id="material-performance-title">'+escape(words[1])+'</h2>'
         '</div></div><div class="material-brief__grid">'
         +item(words[2]+' · '+str(product["model"]),'<strong class="material-brief__source">'+escape(raw.replace("硅胶","silicone"))+'</strong><p>'+escape(source_variation)+'</p>')
         +item(words[4]+' · '+str(product["model"]),'<p>'+escape(model_focus)+'</p><p>'+escape(words[3])+'</p>')
         +'</div>'+evidence
         +'<div class="material-brief__bottom"><div><h3>'+escape(words[6])+'</h3><p>'+escape(words[7])+'</p></div>'
         '<div class="material-brief__links"><a href="'+escape(guide)+'">'+escape(words[9])+' →</a>'
         '<a class="button" href="'+escape(contact)+'">'+escape(words[8])+' →</a></div>'
         '</div></div></section>')
    return (
        '<section class="section material-brief" id="material-performance" aria-labelledby="material-performance-title">'
        '<div class="shell"><div class="section__head"><div>'
        '<span class="eyebrow">'+escape(words[0])+'</span>'
        '<h2 class="section__title" id="material-performance-title">'+escape(words[1])+'</h2>'
        '</div></div><div class="material-brief__grid">'
        +item(words[2],'<strong class="material-brief__source">'+escape(raw.replace("硅胶","silicone"))+'</strong><p>'+escape(words[3])+'</p>')
        +item(words[4],overview+'<p class="material-brief__note">'+escape(words[5])+'</p>')
        +'</div>'+catalog_purchase_facts(product,locale)
        +material_annotation(product,locale)
         +'<div class="material-brief__bottom"><div><h3>'+escape(words[6])+'</h3><p>'+escape(words[7])+'</p></div>'
        '<div class="material-brief__links"><a href="'+escape(guide)+'">'+escape(words[9])+' →</a>'
        '<a class="button" href="'+escape(contact)+'">'+escape(words[8])+' →</a></div>'
        '</div></div></section>')

def inject(body,product,locale,route,approved_routes=None):
    if 'id="material-performance"' in body:return body
    anchor='</section><section class="section section--soft product-content">'
    if body.count(anchor)!=1:raise ValueError("Missing unique product-section insertion marker: "+route)
    return body.replace(anchor,'</section>'+render(product,locale,route,approved_routes)+
                        '<section class="section section--soft product-content">',1)