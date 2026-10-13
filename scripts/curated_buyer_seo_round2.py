#!/usr/bin/env python3
"""Human-curated bilingual category snippets and contextual Blog links.

Build-only static changes: no fabricated model attributes, certification,
pricing, MOQ, reviews or changes to D1/CMS records.
"""
from pathlib import Path
import html
import json
import re

ROOT=Path(__file__).resolve().parent.parent
LOCALES=("en","es","pt","ru","tr")
DESCRIPTIONS={
 "collections/sports-water-bottles":{
 "en":"Compare XUYI plastic sports water bottles by capacity, lid and carry style. Browse models, consider branding options and request a model-specific wholesale quote.",
 "es":"Compare botellas deportivas de plástico XUYI por capacidad, tapa y asa. Explore modelos, opciones de personalización y solicite una cotización por modelo.",
 "pt":"Compare garrafas esportivas de plástico XUYI por capacidade, tampa e alça. Explore modelos, personalização e solicite uma cotação por modelo.",
 "ru":"Сравните спортивные пластиковые бутылки XUYI по объему, крышке и ручке. Изучите модели, варианты оформления и запросите расчет для нужной модели.",
 "tr":"XUYI plastik spor şişelerini hacim, kapak ve taşıma sapına göre karşılaştırın. Modelleri inceleyin, özelleştirme ve teklif koşullarını sorun."},
 "collections/kids-water-bottles":{
 "en":"Explore XUYI plastic kids water bottles with different straw lids, handles and colors. Compare models and confirm samples, artwork and ordering details before buying.",
 "es":"Explore botellas infantiles de plástico XUYI con distintos tipos de pajita, asa y color. Compare modelos y consulte muestras, diseños y condiciones de pedido.",
 "pt":"Explore garrafas infantis de plástico XUYI com diferentes tampas, alças e cores. Compare modelos e consulte amostras, artes e condições de encomenda.",
 "ru":"Выберите детские пластиковые бутылки XUYI с разными трубочками, ручками и цветами. Сравните модели и уточните образцы, оформление и условия заказа.",
 "tr":"Farklı pipet kapakları, kulpları ve renkleriyle XUYI plastik çocuk şişelerini inceleyin. Modelleri karşılaştırın; numune ve sipariş ayrıntılarını sorun."},
 "collections/large-capacity-water-jugs":{
 "en":"Browse larger-capacity XUYI plastic water jugs for sports, travel and daily use. Compare capacities, handles and lids, then confirm the model and packing options.",
 "es":"Explore botellas de plástico XUYI de gran capacidad para deporte, viajes y uso diario. Compare volúmenes, asas y tapas antes de confirmar modelo y embalaje.",
 "pt":"Veja garrafas plásticas XUYI de grande capacidade para esporte, viagens e uso diário. Compare volumes, alças e tampas antes de confirmar modelo e embalagem.",
 "ru":"Выбирайте пластиковые бутылки XUYI большого объема для спорта, поездок и ежедневного использования. Сравните объем, ручки и крышки перед заказом.",
 "tr":"Spor, seyahat ve günlük kullanım için büyük hacimli XUYI plastik su şişelerini inceleyin. Hacim, kulp ve kapakları karşılaştırın."},
 "collections/plastic-shaker-bottles":{
 "en":"Compare XUYI plastic protein shaker bottles for fitness and sports nutrition. Review each model's lid, cup shape and components; ask about samples and branding options.",
 "es":"Compare vasos mezcladores de plástico XUYI para gimnasio y nutrición deportiva. Revise tapas, formas y componentes por modelo; consulte muestras y personalización.",
 "pt":"Compare copos shaker de plástico XUYI para academia e nutrição esportiva. Veja tampas, formatos e peças de cada modelo; consulte amostras e personalização.",
 "ru":"Сравните пластиковые шейкеры XUYI для фитнеса и спортивного питания. Проверьте крышки, форму и комплектацию моделей, запросите образцы и оформление.",
 "tr":"Fitness ve sporcu beslenmesi için XUYI plastik shaker modellerini karşılaştırın. Kapak, gövde ve parça seçeneklerini inceleyip numune bilgisi alın."}
}
BLOG_LINKS={
 "wholesale-plastic-water-bottle-buying-guide":"collections/sports-water-bottles",
 "plastic-bottle-material-selection":"capabilities/custom-water-bottle",
 "tritan-vs-pp-petg-pc":"capabilities/custom-water-bottle",
 "bpa-free-plastic-water-bottle-sourcing":"collections/kids-water-bottles",
 "custom-water-bottle-moq-pricing":"request-sample",
 "oem-vs-odm-plastic-water-bottles":"capabilities/custom-water-bottle",
 "water-bottle-quality-control-checklist":"features/straw-lid",
 "custom-water-bottle-export-packaging":"capabilities/oem-odm",
 "water-bottle-logo-printing-methods":"capabilities/custom-water-bottle",
}
WORDS={
 "en":("Continue your sourcing research","View this related product or buying guide"),
 "es":("Continúe su investigación de compras","Consulte esta guía o producto relacionado"),
 "pt":("Continue sua pesquisa de compras","Consulte este guia ou produto relacionado"),
 "ru":("Дополнительная информация для закупки","Изучите связанный товар или руководство"),
 "tr":("Tedarik araştırmanıza devam edin","İlgili ürünü veya satın alma rehberini inceleyin"),
}

def change_once(source,pattern,new,context):
    result,n=re.subn(pattern,lambda _ :new,source,count=1,flags=re.S)
    if n!=1:raise ValueError("Curated SEO context missing "+context+" "+str(n))
    return result

def apply(dist):
    dist=Path(dist); descriptions=0; links=0
    for locale in LOCALES:
        prefix="" if locale=="en" else locale+"/"
        for route,texts in DESCRIPTIONS.items():
            file=dist/prefix/route/"index.html"
            content=file.read_text(encoding="utf8")
            description=texts[locale]
            if not (85<=len(description)<=190) or any(x in description for x in "<>"):
                raise ValueError("Unsafe or implausible SEO description "+str(file))
            escaped=html.escape(description,quote=True)
            content=change_once(content,r'<meta name="description" content="[^"]*">',
                                '<meta name="description" content="'+escaped+'">',str(file))
            content=change_once(content,r'<meta property="og:description" content="[^"]*">',
                                '<meta property="og:description" content="'+escaped+'">',str(file))
            def update_schema(match):
                data=json.loads(match.group(1))
                for node in data.get("@graph",[data]):
                    if isinstance(node,dict) and node.get("@type")=="WebPage":
                        node["description"]=description
                return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False,separators=(",",":")).replace("<",r"\u003c")+'</script>'
            content=re.sub(r'<script type="application/ld\+json">([\s\S]*?)</script>',update_schema,content)
            file.write_text(content,encoding="utf8")
            descriptions+=1
        for article,target in BLOG_LINKS.items():
            file=dist/prefix/"blog"/article/"index.html"
            if not file.is_file() or not (dist/prefix/target/"index.html").is_file():
                raise FileNotFoundError(str(file)+" or "+target)
            content=file.read_text(encoding="utf8")
            before,separator,after=content.partition("</main>")
            if not separator or 'class="seo-next-buyer"' in before:
                raise ValueError("Unexpected article layout "+str(file))
            main=before.split("<main",1)[-1]
            href="/"+prefix+target+"/"
            if 'href="'+href+'"' in main:
                raise ValueError("Already has exact contextual link "+str(file)+" "+href)
            heading,lead=WORDS[locale]
            new='<section class="seo-next-buyer"><h2>'+html.escape(heading)+'</h2><p>'+html.escape(lead)+': <a href="'+href+'">'+html.escape(lead)+' →</a></p></section>'
            file.write_text(before+new+separator+after,encoding="utf8")
            links+=1
    if descriptions!=20 or links!=45:raise ValueError("Unexpected round2 count")
    print("XUYI_CURATED_BUYER_SEO_ROUND2",descriptions,"meta",links,"blog links")
    return descriptions,links

if __name__=="__main__":apply(ROOT/"dist")