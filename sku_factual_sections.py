"""Source-backed SKU-specific materials, design notes and visible FAQs.

The same facts and buyer questions are composed from actual model catalog rows.
Only reviewed SKU cohorts receive these modules, and only when the
individual D1/native section is *byte-identical* to its approved baseline.
Do not infer the body's, lid's, straw's or seal's polymer from a combined list.
"""
from pathlib import Path
from hashlib import sha256
from html import escape
import json,re

ROOT=Path(__file__).resolve().parent
DATA=json.loads((ROOT/"data/product-20-module-source-baselines.json").read_text(encoding="utf8"))
FIRST20=DATA["models"]
NEXT20_DATA=json.loads((ROOT/"data/product-20-module-source-baselines-phase10.json").read_text(encoding="utf8"))
NEXT20=NEXT20_DATA["models"]
THIRD20_DATA=json.loads((ROOT/"data/product-20-module-source-baselines-phase11.json").read_text(encoding="utf8"))
THIRD20=THIRD20_DATA["models"]
assert not set(FIRST20).intersection(NEXT20) and not set(THIRD20).intersection(set(FIRST20)|set(NEXT20)), "SKU editorial releases overlap"
PEERS={**FIRST20,**NEXT20,**THIRD20}
BASE={**DATA["baselines"],**NEXT20_DATA["baselines"],**THIRD20_DATA["baselines"]}
LANGS=("en","es","pt","ru","tr")
FOCUS={}
for group in ("sports","kids","jugs","shakers"):
    FOCUS.update(json.loads((ROOT/f"data/sku20-focus-{group}.json").read_text(encoding="utf8")))
for group in ("sports","kids","jugs"):
    FOCUS.update(json.loads((ROOT/f"data/sku20-phase10-focus-{group}.json").read_text(encoding="utf8")))
for group in ("sports","kids","jugs"):
    FOCUS.update(json.loads((ROOT/f"data/sku20-phase11-focus-{group}.json").read_text(encoding="utf8")))
assert set(FOCUS)==set(PEERS)
assert all(set(item)==set(LANGS)|{"topic"} for item in FOCUS.values())
# Each locale has approved native questions and procurement-oriented wording,
# while all variable values are read from the CMS-aware catalog row.
T={
"en":{
"size":"Catalog size and comparable model","sizeA":"{sku} is listed at {cap}, with source dimensions {dims}. {peer} is listed at {pcap}, with source dimensions {pdims}. Compare real assembled samples; these figures are not guarantees of shared parts.",
"materials":"Material families and visual options","matA":"For {sku}, the source lists {mat}. The recorded finish is {colors}. The catalog does not identify which plastic forms each body, lid, straw or gasket. Confirm actual colors and components for the order.",
"packing":"Carton and ordering checklist","packA":"The {sku} catalog packing reference is {pack}; carton count {qty}, outer dimensions {carton}. Obtain the exact packaged sample and approved printing area before confirming freight or branding.",
"qcap":"How does {sku} compare with {peer} for capacity and dimensions?","acap":"The source lists {sku} at {cap} ({dims}) versus {peer} at {pcap} ({pdims}). Verify the assembled measurements and intended fit on actual samples.",
"qmat":"Which parts of {sku} use the catalog-listed {mat}?","amat":"{mat} is a combined catalog material list for {sku}, not a body/lid/straw/seal breakdown. Ask for a model-specific component bill and suitable food-contact evidence.",
"qcolor":"Which finishes can be discussed for {sku}?","acolor":"Source color references for {sku}: {colors}. Availability, accurate appearance, logo contrast and decoration process require a color and print proof.",
"qpack":"How is {sku} packed and what should I confirm?","apack":"Reference: {pack}; {qty} per carton, carton size {carton}. Where values are unlisted, the factory must supply them. Approve pack count, parts and carton dimensions before shipping.",
"materialNote":"{sku} catalog evidence: {cap}; dimensions {dims}; overall material families {mat}. This does not establish the polymers of the body, lid, straw or seal. Confirm each component and finished-product evidence for the destination market.",
"materialCompare":"For sourcing comparison, {peer} is documented at {pcap} with material families {pmat}; shared polymer names do not establish identical molds, caps or test results."
},
"es":{
"size":"Dimensiones y modelo comparable","sizeA":"El catálogo indica {sku} con {cap} y medidas {dims}; {peer} con {pcap} y medidas {pdims}. Compare muestras reales montadas, sin deducir piezas intercambiables.",
"materials":"Materiales y acabados de referencia","matA":"Para {sku} figuran {mat} y colores de catálogo {colors}. La lista no determina qué polímero se usa en cuerpo, tapa, pajita o junta. Confirme componentes y colores reales.",
"packing":"Embalaje y aprobación de compra","packA":"Referencia de embalaje de {sku}: {pack}; unidades por caja {qty} y dimensiones {carton}. Verifique el embalaje y el área de impresión antes de cotizar el transporte.",
"qcap":"¿En qué capacidad y tamaño difieren {sku} y {peer}?","acap":"El catálogo indica {sku}: {cap}, {dims}; y {peer}: {pcap}, {pdims}. Confirme las medidas en muestras reales.",
"qmat":"¿Qué partes de {sku} utilizan los materiales {mat}?","amat":"{mat} es una lista conjunta de materiales de {sku}, no una asignación a cuerpo, tapa, pajita o junta. Solicite documentación de cada componente.",
"qcolor":"¿Qué acabados aparecen para {sku}?","acolor":"Referencias de color para {sku}: {colors}. Confirme disponibilidad, aspecto real y contraste del logotipo mediante muestras.",
"qpack":"¿Qué embalaje necesita confirmar para {sku}?","apack":"Referencia {pack}; unidades por caja {qty}; tamaño de caja {carton}. Solicite confirmación escrita si falta algún dato.",
"materialNote":"Ficha de {sku}: capacidad {cap}, medidas {dims}, familias de materiales {mat}. No demuestra qué pieza usa cada polímero; compruebe los materiales y documentos del producto.",
"materialCompare":"Para comparar, {peer} registra {pcap} y {pmat}. Compartir una familia de materiales no acredita tapas, moldes o ensayos idénticos."
},
"pt":{
"size":"Dimensões e modelo de comparação","sizeA":"A fonte registra {sku} com {cap} e medidas {dims}; {peer} com {pcap} e medidas {pdims}. Compare amostras montadas; os números não demonstram peças compatíveis.",
"materials":"Famílias de materiais e cores","matA":"Para {sku}, o catálogo indica {mat} e cores {colors}. A combinação não informa a resina de corpo, tampa, palhinha ou vedação. Confirme componentes e tons.",
"packing":"Embalagem e aprovação do pedido","packA":"A referência de {sku} é {pack}; unidades por caixa {qty} e dimensões {carton}. Confirme embalagem, amostra e local de impressão antes do frete.",
"qcap":"Como comparar capacidade e dimensões de {sku} com {peer}?","acap":"O catálogo registra {sku} com {cap} ({dims}) e {peer} com {pcap} ({pdims}). Confirme no produto montado.",
"qmat":"Quais peças de {sku} utilizam os materiais {mat}?","amat":"{mat} são famílias gerais de {sku}, não materiais comprovados para corpo, tampa, palhinha ou vedação. Peça a lista de componentes.",
"qcolor":"Quais cores são referenciadas para {sku}?","acolor":"Cores da fonte de {sku}: {colors}. Disponibilidade e aplicação do logotipo exigem amostra física aprovada.",
"qpack":"Como confirmar a embalagem de {sku}?","apack":"Referência {pack}; peças por caixa {qty}; dimensões {carton}. Solicite documento escrito para qualquer dado ausente.",
"materialNote":"Dados da fonte para {sku}: capacidade {cap}, dimensões {dims}, materiais {mat}. Não há identificação de polímeros por componente; confirme documentos e amostra.",
"materialCompare":"O modelo {peer} registra {pcap} e {pmat}; listas iguais não significam moldes, tampas ou testes equivalentes."
},
"ru":{
"size":"Размеры и сопоставление моделей","sizeA":"Для {sku} указаны {cap} и размеры {dims}; для {peer} — {pcap} и размеры {pdims}. Сравните собранные образцы, не предполагая совместимость деталей.",
"materials":"Материалы и цвета по каталогу","matA":"Для {sku} записаны {mat} и цвета {colors}. Общий список не показывает состав корпуса, крышки, трубочки и уплотнителя. Уточните материалы и реальные оттенки.",
"packing":"Упаковка и подтверждение заказа","packA":"Упаковка {sku}: {pack}; штук в коробке {qty}, размер коробки {carton}. До расчёта доставки проверьте упаковку, образец и место печати.",
"qcap":"Чем отличаются объём и размеры {sku} и {peer}?","acap":"По каталогу {sku}: {cap}, {dims}; {peer}: {pcap}, {pdims}. Измерьте реальные образцы перед заказом.",
"qmat":"Из каких деталей модели {sku} состоят материалы {mat}?","amat":"{mat} — общий перечень для {sku}, а не подтверждённый состав корпуса, крышки, трубочки и уплотнителя. Запросите спецификацию деталей.",
"qcolor":"Какие цвета отмечены для {sku}?","acolor":"Цвета в исходной записи {sku}: {colors}. Доступность, оттенок и вид логотипа подтвердите печатным образцом.",
"qpack":"Какая транспортная упаковка указана для {sku}?","apack":"Источник: {pack}; штук в коробке {qty}; размеры {carton}. Все отсутствующие значения уточните письменно.",
"materialNote":"Каталог модели {sku}: объём {cap}, размеры {dims}, материалы {mat}. Состав корпуса, крышки, трубочки и уплотнителя не указан; проверьте документы.",
"materialCompare":"Для сравнения {peer} записана с {pcap} и {pmat}; совпадение полимеров не доказывает одинаковые крышки и испытания."
},
"tr":{
"size":"Ölçüler ve model karşılaştırması","sizeA":"Katalogda {sku} kapasitesi {cap}, ölçüleri {dims}; {peer} kapasitesi {pcap}, ölçüleri {pdims}. Montajlı numuneleri karşılaştırın; ortak parçaları varsaymayın.",
"materials":"Malzeme aileleri ve renkler","matA":"{sku} için {mat} ve kaynak renkler {colors} belirtilir. Liste gövde, kapak, pipet veya contanın ayrı malzemesini doğrulamaz. Parçaları ve renkleri teyit edin.",
"packing":"Paketleme ve satın alma kontrolü","packA":"{sku} için kaynak ambalaj {pack}; koli adedi {qty}, koli ölçüsü {carton}. Navlun ve logo onayından önce gerçek paketi inceleyin.",
"qcap":"{sku} ve {peer} kapasite ve ölçüler bakımından nasıl ayrılır?","acap":"Kaynakta {sku}: {cap}, {dims}; {peer}: {pcap}, {pdims}. Fiziksel örnekleri ölçerek doğrulayın.",
"qmat":"{sku} ürünündeki hangi parçalar {mat} malzemelerindendir?","amat":"{mat} birleşik kaynak listesidir; gövde, kapak, pipet ve contanın tek tek malzemesi değildir. Parça belgelerini isteyin.",
"qcolor":"{sku} için hangi renkler kaynakta yer alıyor?","acolor":"{sku} renk referansları: {colors}. Üretim bulunurluğunu ve logo baskısını gerçek numuneyle onaylayın.",
"qpack":"{sku} için koli bilgisi nasıl doğrulanır?","apack":"Katalog paketi {pack}; koli adedi {qty}; koli ölçüsü {carton}. Eksik değerleri yazılı olarak teyit ettirin.",
"materialNote":"{sku} kaynak bilgisi: kapasite {cap}, ölçüler {dims}, genel malzemeler {mat}. Her parçanın reçinesi bilinmez; gerçek numuneyi ve belgeleri doğrulayın.",
"materialCompare":"Karşılaştırma modeli {peer}: {pcap}, {pmat}. Malzeme ailesinin aynı olması kapak veya kalıp ortaklığını göstermez."
}}
# Catalog styling/color terms are localized as trade-color references, not
# interpreted as stock or certified finished product variants.
COLOR_WORDS={
"es":{"Pomegranate Red":"Rojo granada","Sakura Pink":"Rosa cerezo","Mint Green":"Verde menta","Light Blue":"Azul claro","Dark Green":"Verde oscuro","Navy Blue":"Azul marino","Violet":"Violeta","Yellow":"Amarillo","Pink":"Rosa","Green":"Verde","Black":"Negro","Gray":"Gris","Blue":"Azul","Orange":"Naranja","Purple":"Morado","White":"Blanco","Brown":"Marrón","Red":"Rojo","gradient":"degradado","variants":"variantes","to":"a","and":"y"},
"pt":{"Pomegranate Red":"Vermelho romã","Sakura Pink":"Rosa cerejeira","Mint Green":"Verde menta","Light Blue":"Azul claro","Dark Green":"Verde escuro","Navy Blue":"Azul marinho","Violet":"Violeta","Yellow":"Amarelo","Pink":"Rosa","Green":"Verde","Black":"Preto","Gray":"Cinza","Blue":"Azul","Orange":"Laranja","Purple":"Roxo","White":"Branco","Brown":"Marrom","Red":"Vermelho","gradient":"degradê","variants":"variantes","to":"para","and":"e"},
"ru":{"Pomegranate Red":"Гранатовый красный","Sakura Pink":"Розовый сакура","Mint Green":"Мятный зеленый","Light Blue":"Светло-синий","Dark Green":"Темно-зеленый","Navy Blue":"Темно-синий","Violet":"Фиолетовый","Yellow":"Желтый","Pink":"Розовый","Green":"Зеленый","Black":"Черный","Gray":"Серый","Blue":"Синий","Orange":"Оранжевый","Purple":"Пурпурный","White":"Белый","Brown":"Коричневый","Red":"Красный","gradient":"градиент","variants":"варианты","to":"к","and":"и"},
"tr":{"Pomegranate Red":"Nar kırmızısı","Sakura Pink":"Kiraz pembesi","Mint Green":"Nane yeşili","Light Blue":"Açık mavi","Dark Green":"Koyu yeşil","Navy Blue":"Lacivert","Violet":"Menekşe","Yellow":"Sarı","Pink":"Pembe","Green":"Yeşil","Black":"Siyah","Gray":"Gri","Blue":"Mavi","Orange":"Turuncu","Purple":"Mor","White":"Beyaz","Brown":"Kahverengi","Red":"Kırmızı","gradient":"gradyan","variants":"seçenekleri","to":"ile","and":"ve"}}
COLOR_PROMPTS={
"en":"catalog colors need source confirmation",
"es":"los colores del catálogo requieren confirmación",
"pt":"as cores do catálogo precisam de confirmação",
"ru":"цвета каталога требуют подтверждения",
"tr":"katalog renkleri doğrulanmalıdır"
}
PACK_TRANSLATIONS={
 "en":{"OPP袋":"OPP bag","磨砂束口袋混装":"mixed frosted drawstring pouches"},
 "es":{"OPP袋":"bolsa OPP","磨砂束口袋混装":"bolsas mate con cordón, colores mezclados","Bag packaging (type to be confirmed)":"bolsa (tipo pendiente de confirmar)"},
 "pt":{"OPP袋":"saco OPP","磨砂束口袋混装":"sacos foscos com cordão, cores misturadas","Bag packaging (type to be confirmed)":"saco (tipo a confirmar)"},
 "ru":{"OPP袋":"пакет OPP","磨砂束口袋混装":"смешанные матовые мешочки с завязками","Bag packaging (type to be confirmed)":"пакет (тип уточняется)"},
 "tr":{"OPP袋":"OPP poşet","磨砂束口袋混装":"karışık renkli mat büzgülü torba","Bag packaging (type to be confirmed)":"poşet (türü doğrulanmalı)"}
}
UNKNOWN={"en":"not listed; confirm","es":"sin datos; confirmar","pt":"não indicado; confirmar","ru":"не указано; уточнить","tr":"belirtilmedi; doğrulayın"}

def section(body,kind):
    if kind=="design":
        begin=body.find('<section class="section section--soft product-content">')
    elif kind=="faq":
        pos=body.find('<div class="faq-list">')
        begin=body.rfind('<section class="section section--soft">',0,pos) if pos>=0 else -1
    else:raise ValueError(kind)
    end=body.find('</section>',begin) if begin>=0 else -1
    return (begin,end+len('</section>'),body[begin:end+len('</section>')]) if end>=0 else None

def _source_capacity(row):
    from product_content import capacity_en
    return capacity_en(str(row.get("capacity") or ""),str(row.get("model") or ""))

def _source_dimensions(row,locale):
    raw=str(row.get("dimensions") or "").strip()
    if not raw:
        m=re.search(r'产品尺寸\s*\d+\s*ml\s*([\d.]+\s*[*×x]\s*[\d.]+)\s*cm',str(row.get("capacity") or ""),re.I)
        if m:raw=m.group(1)
    if re.fullmatch(r'[\d.]+\s*[*×x]\s*[\d.]+(?:\s*[*×x]\s*[\d.]+)?',raw):return raw.replace("*"," × ")+" cm"
    return UNKNOWN[locale]

def _value(v,locale):
    s=str(v or "").strip()
    return s if s and s not in ("To confirm","Confirm with sales") else UNKNOWN[locale]

def _finish(row,locale):
    from product_content import localize_colors
    raw=str(row.get("colors") or "")
    if not raw:return UNKNOWN[locale]
    # Use actual catalog translation for EN, and internationally recognized
    # English trade-color references on other pages rather than inventing a
    # color not encoded in the source row.
    text=localize_colors(raw)
    if "confirm" in text.casefold() and ("Color to be confirmed" in text or "Color option to be confirmed" in text):
        if locale!="en":
            return COLOR_PROMPTS[locale]
        return text
    if text=="Custom colors (confirm with sales)":
        return {"en":text,"es":"colores personalizados (confirmar con ventas)","pt":"cores personalizadas (confirmar com vendas)","ru":"индивидуальные цвета (уточнить у продавца)","tr":"özel renkler (satış ekibiyle doğrulayın)"}[locale]
    if locale=="en":return text
    words=COLOR_WORDS[locale]
    for key in sorted(words,key=len,reverse=True):
        text=re.sub(r"(?<![A-Za-z])"+re.escape(key)+r"(?![A-Za-z])",lambda _:words[key],text)
    return text

MATERIAL_VARIATION={
 "en":"For the sourcing brief, {sku} shows finish references {colors}, unit packing {pack}, and {qty} units per carton. Its nominal capacity is {relative} than {peer} in the catalog; these are not component-level test results.",
 "es":"Para compras, {sku} presenta colores {colors}, embalaje individual {pack} y {qty} unidades por caja. Su capacidad nominal es {relative} que la de {peer}; no son ensayos de componentes.",
 "pt":"Na compra, {sku} apresenta cores {colors}, embalagem {pack} e {qty} unidades por caixa. A capacidade nominal é {relative} à de {peer}; não são testes de componentes.",
 "ru":"Для заказа {sku} записаны цвета {colors}, упаковка {pack} и {qty} штук в коробке. Номинальный объём {relative} по сравнению с {peer}; это не испытания деталей.",
 "tr":"{sku} için kaynak renkler {colors}, tekli paket {pack} ve koli adedi {qty} belirtilir. Nominal kapasite {peer} ile karşılaştırıldığında {relative}; bu parça testi değildir."
}
RELATIVE={
 "en":("lower","equal","higher"),"es":("menor","igual","mayor"),
 "pt":("menor","igual","maior"),"ru":("меньше","равен","больше"),
 "tr":("daha düşük","eşit","daha yüksek")
}
def facts(row,locale,series):
    peer=series[PEERS[row["slug"]]]
    def numeric_capacity(product):
        m=re.search(r"(\d+(?:\.\d+)?)\s*ml",str(product.get("capacity") or ""),re.I)
        return float(m.group(1)) if m else None
    a=numeric_capacity(row);b=numeric_capacity(peer)
    relative=RELATIVE[locale][0 if a is not None and b is not None and a<b else 2 if a is not None and b is not None and a>b else 1]
    return dict(relative=relative,sku=str(row["model"]),peer=str(peer["model"]),
      cap=_source_capacity(row),pcap=_source_capacity(peer),
      dims=_source_dimensions(row,locale),pdims=_source_dimensions(peer,locale),
      mat=_value(row.get("material"),locale).replace("硅胶","silicone"),
      pmat=_value(peer.get("material"),locale).replace("硅胶","silicone"),
      colors=_finish(row,locale),pack=PACK_TRANSLATIONS[locale].get(str(row.get("packing") or ""),_value(row.get("packing"),locale)),
      qty=_value(row.get("carton_quantity"),locale),
      carton=(_value(row.get("carton_size"),locale).replace("*"," × ")+" cm" if row.get("carton_size") else UNKNOWN[locale]))

def _e(v):return escape(str(v),quote=True)

def material_annotation(row,locale):
    if row.get("slug") not in PEERS:return ""
    from site_renderer import SERIES
    f=facts(row,locale,SERIES);words=T[locale]
    return ('<div class="material-brief__sku-evidence" data-sku-material="'+_e(row["slug"])+'">'
       '<p>'+_e(words["materialNote"].format(**f))+'</p>'
       '<p>'+_e(words["materialCompare"].format(**f))+'</p></div>')

def _replacement(body,row,locale,kind):
    found=section(body,kind)
    if found is None:return body
    start,end,current=found
    baseline=BASE.get(row["slug"],{}).get(locale,{}).get(kind)
    if baseline is None or sha256(current.encode("utf8")).hexdigest()[:16]!=baseline:
        return body   # Owner edited this exact section: never restore template.
    f=facts(row,locale,__import__("site_renderer").SERIES)
    words=T[locale]
    if kind=="design":
        cut=current.find('<div class="grid grid--3">')
        if cut<0:return body
        head=current[:cut+len('<div class="grid grid--3">')]
        cards="".join('<article class="benefit"><h3>'+_e(words[t])+'</h3><p>'+_e(words[d].format(**f))+'</p></article>'
                      for t,d in (("size","sizeA"),("materials","matA"),("packing","packA")))
        note='<div class="sku-focus" data-sku-focus="'+_e(row["slug"])+'"><h3>'+_e(words["materials"])+'</h3><p>'+_e(FOCUS[row["slug"]][locale])+'</p></div>'
        updated=head+cards+'</div>'+note+'</div></section>'
    else:
        cut=current.find('<div class="faq-list">')
        if cut<0:return body
        head=current[:cut+len('<div class="faq-list">')]
        pairs=[(words[q].format(**f),words[a].format(**f)) for q,a in
               (("qcap","acap"),("qmat","amat"),("qcolor","acolor"))]
        special_questions={"en":"What must be verified in the specific {sku} buying brief?",
          "es":"¿Qué debe verificarse en la compra del modelo {sku}?",
          "pt":"O que precisa ser confirmado na compra do modelo {sku}?",
          "ru":"Что важно проверить перед закупкой модели {sku}?",
          "tr":"{sku} modeli satın alınmadan önce ne doğrulanmalı?"}
        pairs.append((special_questions[locale].format(**f),FOCUS[row["slug"]][locale]))
        updated=head+"".join('<details><summary>'+_e(q)+'</summary><p>'+_e(a)+'</p></details>' for q,a in pairs)+'</div></div></section>'
    return body[:start]+updated+body[end:]

def apply(body,row,locale):
    if locale not in T or row.get("slug") not in PEERS:return body
    for kind in ("design","faq"):body=_replacement(body,row,locale,kind)
    return body