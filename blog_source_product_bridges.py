"""Editorially selected, source-stage article-to-model buyer links.

The existing 3–4 related-post links/article are retained: this is NOT a
randomized SEO link carousel. Exact per-route D1 source fingerprints block
re-injection into later CMS-edited articles. New articles remain unrestricted.
"""
from pathlib import Path
from html import escape
import hashlib,json,re
ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/"data/blog-product-proof-source.json").read_text(encoding="utf8"))
LEDE=re.compile(r'(<p class="blog-lede">.*?</p>)',re.S)
TOPICS={
 "en":{"materials":"material evidence","branding":"custom logo artwork","packing":"export packing","sourcing":"supplier quotations","kids":"children's bottle suitability","shaker":"shaker specifications","comparison":"sports-bottle and water-jug formats","quality":"lid and quality checks"},
 "es":{"materials":"la documentación de materiales","branding":"el diseño de logotipos","packing":"el embalaje de exportación","sourcing":"las cotizaciones","kids":"las botellas infantiles","shaker":"los vasos mezcladores","comparison":"los formatos deportivos y grandes","quality":"los controles de tapas y calidad"},
 "pt":{"materials":"a comprovação dos materiais","branding":"a personalização de logótipos","packing":"a embalagem de exportação","sourcing":"as cotações","kids":"as garrafas infantis","shaker":"os copos misturadores","comparison":"as garrafas desportivas e jarros","quality":"a verificação das tampas e qualidade"},
 "ru":{"materials":"документы на материалы","branding":"нанесение логотипа","packing":"экспортную упаковку","sourcing":"расчет поставки","kids":"выбор детских бутылок","shaker":"шейкеры","comparison":"спортивные бутылки и большие емкости","quality":"проверку крышек и качества"},
 "tr":{"materials":"malzeme belgelerini","branding":"logo tasarımını","packing":"ihracat ambalajını","sourcing":"tedarik tekliflerini","kids":"çocuk şişesi seçimini","shaker":"shaker modellerini","comparison":"spor şişeleri ile büyük kapları","quality":"kapak ve kalite testlerini"}
}
SENTENCES={
 "en":("For {topic}, compare catalog "," as a concrete product reference. These are model-specific examples, not proof of a particular material certification or cap performance; confirm the physical samples before ordering."),
 "es":("Para revisar {topic}, compare en el catálogo "," como referencia concreta. Las fichas no sustituyen las pruebas de materiales, tapas ni las muestras físicas antes del pedido."),
 "pt":("Para avaliar {topic}, compare no catálogo "," como exemplos concretos. As fichas não substituem testes de materiais, tampas ou amostras antes da encomenda."),
 "ru":("Чтобы оценить {topic}, сравните каталожные модели "," как конкретные примеры. Каталог не заменяет испытания материалов, крышек и проверку образцов до заказа."),
 "tr":("{topic} değerlendirirken katalogdaki "," modellerini somut örnek olarak karşılaştırın. Model sayfaları malzeme, kapak testleri ve fiziksel numune onayının yerini tutmaz.")
}
def product_bridges(body,route,locale,owner_managed=False,source_original=None):
    if not route.startswith("/blog/") or route=="/blog/" or locale not in TOPICS:return body
    slug=route.removeprefix("/blog/").strip("/")
    selected=D["modelPairs"].get(slug)
    if not selected or 'data-blog-product-proof="' in body:return body
    if owner_managed:return body
    # The original D1 body owns the hash check; approved terminology fixes
    # must run before new links without invalidating owner protection.
    initial=body if source_original is None else source_original
    if locale!="en" and hashlib.sha256(initial.encode("utf8")).hexdigest()!=D["cmsLocaleSourceHashes"][slug][locale]:
        return body
    if len(LEDE.findall(body))!=1:return body
    first,second,topic=selected
    prefix="" if locale=="en" else "/"+locale
    already={x for x in (first,second) if re.search(r'href="'+re.escape(prefix+"/products/"+x+"/")+r'"',body)}
    models=[x for x in (first,second) if x not in already]
    if not models:return body
    anchors=[f'<a href="{prefix}/products/{escape(x)}/">Model {escape(x)}</a>' for x in models]
    if len(anchors)==2:
        joined=anchors[0]+(" and " if locale=="en" else " / ")+anchors[1]
    else:joined=anchors[0]
    begin,end=SENTENCES[locale]
    intro=begin.format(topic=TOPICS[locale][topic])
    paragraph=f'<p class="blog-product-proof" data-blog-product-proof="{escape(slug)}">'+intro+joined+end+'</p>'
    return LEDE.sub(lambda m:m.group(1)+paragraph,body,count=1)