"""Small five-language material block, sourced from the actual SKU catalog.

No backend fields, prices, heat limits, food-contact or BPA certifications are
inferred. A combined PC+PP+ABS material list is NOT a bill of materials.
"""
import html
import re
from urllib.parse import quote

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
    return (
        '<section class="section material-brief" id="material-performance" aria-labelledby="material-performance-title">'
        '<div class="shell"><div class="section__head"><div>'
        '<span class="eyebrow">'+escape(words[0])+'</span>'
        '<h2 class="section__title" id="material-performance-title">'+escape(words[1])+'</h2>'
        '</div></div><div class="material-brief__grid">'
        +item(words[2],'<strong class="material-brief__source">'+escape(raw.replace("硅胶","silicone"))+'</strong><p>'+escape(words[3])+'</p>')
        +item(words[4],overview+'<p class="material-brief__note">'+escape(words[5])+'</p>')
        +'</div><div class="material-brief__bottom"><div><h3>'+escape(words[6])+'</h3><p>'+escape(words[7])+'</p></div>'
        '<div class="material-brief__links"><a href="'+escape(guide)+'">'+escape(words[9])+' →</a>'
        '<a class="button" href="'+escape(contact)+'">'+escape(words[8])+' →</a></div>'
        '</div></div></section>')

def inject(body,product,locale,route,approved_routes=None):
    if 'id="material-performance"' in body:return body
    anchor='</section><section class="section section--soft product-content">'
    if body.count(anchor)!=1:raise ValueError("Missing unique product-section insertion marker: "+route)
    return body.replace(anchor,'</section>'+render(product,locale,route,approved_routes)+
                        '<section class="section section--soft product-content">',1)