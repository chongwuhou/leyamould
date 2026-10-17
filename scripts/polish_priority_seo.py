"""Human-authored, narrow SEO corrections on four XUYI buyer landing routes.

Only final static HTML is changed. Original D1 records, approved translated
body text, product model names, canonical links and hreflang stay untouched.
No arbitrary trimming, translation service or synthetic keyword pages.
"""
import html
import json
import re
from pathlib import Path
from cms_seo_curation_guard import may_curate

# page route -> language -> (title, description). Confirmed services are
# invitations to discuss specifications, not promises of MOQ/certification.
PRIORITY={
 "/capabilities/":{
  "en":("Custom Plastic Bottles: OEM, Logos & Packaging | XUYI","Plan a custom plastic bottle project with XUYI: logo artwork, colors, lids, samples and packaging. Feasibility and minimum quantities depend on the exact model."),
  "es":("Botellas de plástico a medida: OEM y logotipos | XUYI","Planifique botellas de plástico personalizadas con XUYI: logotipo, colores, tapas, muestras y embalaje. La viabilidad y el pedido mínimo dependen del modelo."),
  "pt":("Garrafas plásticas personalizadas: OEM e logos | XUYI","Planeie garrafas plásticas personalizadas com a XUYI: logótipo, cores, tampas, amostras e embalagem. Viabilidade e pedido mínimo dependem do modelo."),
  "ru":("Пластиковые бутылки на заказ: OEM и логотипы | XUYI","Обсудите с XUYI логотип, цвета, крышки, образцы и упаковку пластиковых бутылок. Возможности OEM и минимальная партия зависят от выбранной модели."),
  "tr":("Özel Plastik Su Şişeleri: OEM ve Logo | XUYI","XUYI ile plastik şişe projenizi planlayın: logo, renk, kapak, numune ve ambalaj. OEM uygunluğu ve asgari sipariş miktarı seçilen modele bağlıdır.")
 },
 "/capabilities/oem-odm/":{
  "en":("Plastic Water Bottle OEM & ODM Services | XUYI","Compare OEM branding and ODM development for plastic water bottles. Discuss existing models, logo artwork, tooling feasibility, samples and packaging with XUYI."),
  "es":("Botellas de plástico OEM y ODM | XUYI","Compare la personalización OEM y el desarrollo ODM de botellas de plástico. Consulte modelos, logotipos, moldes, muestras y embalaje según su proyecto."),
  "pt":("Garrafas de plástico OEM e ODM | XUYI","Compare personalização OEM e desenvolvimento ODM de garrafas plásticas. Consulte modelos, logótipos, moldes, amostras e embalagens para o seu projeto."),
  "ru":("Пластиковые бутылки OEM и ODM | XUYI","Сравните OEM-брендинг и ODM-разработку пластиковых бутылок. Обсудите модели, логотип, пресс-формы, образцы и упаковку с командой XUYI."),
  "tr":("Plastik Şişe OEM ve ODM Hizmetleri | XUYI","Plastik şişelerde OEM markalama ve ODM geliştirme seçeneklerini karşılaştırın. XUYI ile modelleri, logoyu, kalıpları, numuneleri ve ambalajı görüşün.")
 },
 "/capabilities/custom-water-bottle/":{
  "en":("Custom Plastic Water Bottles for Brands | XUYI","Source custom plastic water bottles for your brand. Review existing models, logos, color options, components and packaging; request samples before confirming production."),
  "es":("Botellas de plástico personalizadas para marcas | XUYI","Botellas de plástico personalizadas para su marca: compare modelos, logotipos, colores, componentes y embalaje. Solicite muestras antes de aprobar la producción."),
  "pt":("Garrafas plásticas personalizadas para marcas | XUYI","Garrafas plásticas personalizadas para a sua marca: compare modelos, logótipos, cores, componentes e embalagem. Solicite amostras antes de aprovar a produção."),
  "ru":("Пластиковые бутылки под заказ для брендов | XUYI","Пластиковые бутылки с логотипом под ваш бренд. Сравните модели, цвета, комплектующие и упаковку; запросите образец перед согласованием производства."),
  "tr":("Markalara Özel Plastik Su Şişeleri | XUYI","Markanız için özel plastik su şişelerini inceleyin: model, logo, renk, parça ve ambalaj seçenekleri. Üretim onayından önce numune talep edin.")
 }
}


def _replace_one(markup,pattern,replacement,route,locale):
    updated,count=re.subn(pattern,lambda _:replacement,markup,count=1,flags=re.S)
    if count!=1:raise ValueError("Missing SEO field on "+locale+route)
    return updated


def polish(markup,route,locale):
    title,description=PRIORITY[route][locale]
    if not title or not description or len(title)>70 or len(description)>180:
        raise ValueError("Curated SEO length / empty check: "+locale+route)
    if any(char in title+description for char in '<>'):
        raise ValueError("Unsafe curated SEO text")
    title_encoded=html.escape(title)
    description_encoded=html.escape(description,quote=True)
    markup=_replace_one(markup,r'<title>[^<]*</title>',
                        '<title>'+title_encoded+'</title>',route,locale)
    for key,value in (("description",description_encoded),):
        markup=_replace_one(markup,r'<meta name="'+key+r'" content="[^"]*">',
                            '<meta name="'+key+'" content="'+value+'">',route,locale)
    for property_name,value in (("og:title",title_encoded),("og:description",description_encoded)):
        markup=_replace_one(markup,r'<meta property="'+property_name+r'" content="[^"]*">',
            '<meta property="'+property_name+'" content="'+value+'">',route,locale)
    # The WebPage description, if published, must not contradict meta.
    def structured(match):
        data=json.loads(match.group(1))
        nodes=data.get("@graph",[data])
        updated=False
        for node in nodes:
            if isinstance(node,dict) and node.get("@type")=="WebPage":
                node["description"]=description
                updated=True
        if not updated:return match.group()
        return '<script type="application/ld+json">'+json.dumps(
            data,ensure_ascii=False,separators=(",",":")).replace("<",r"\u003c")+'</script>'
    return re.sub(r'<script type="application/ld\+json">([\s\S]*?)</script>',structured,markup)


def apply(dist):
    dist=Path(dist)
    count=0
    for route,locales in PRIORITY.items():
        for locale in locales:
            # Honor new D1/CMS copy on future all-site rebuilds.
            if not (may_curate(locale,route,"title") and may_curate(locale,route,"description")):
                continue
            prefix="" if locale=="en" else locale+"/"
            file=dist/prefix/route.lstrip("/")/"index.html"
            if not file.is_file():raise FileNotFoundError(str(file))
            old=file.read_text(encoding="utf-8")
            new=polish(old,route,locale)
            if new==old:raise ValueError("Expected SEO polish to change "+locale+route)
            file.write_text(new,encoding="utf-8")
            count+=1
    print("XUYI_CURATED_PRIORITY_SEO_PAGES",count)
    return count


if __name__=="__main__":
    apply(Path(__file__).resolve().parent.parent/"dist")
