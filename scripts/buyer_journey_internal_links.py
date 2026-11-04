#!/usr/bin/env python3
"""Curated, locale-native contextual routes for XUYI buyer discovery.

Link only from semantically relevant catalog / buying-guide pages to existing
published application and bottle-feature pages. No sitewide keyword stuffing,
no D1 edits, no new URL creation, and no unreviewed product assertions.
"""
from pathlib import Path
import html
import json

ROOT = Path(__file__).resolve().parent.parent
LOCALES = ("en", "es", "pt", "ru", "tr")
BLOG_FEATURE_PATHWAYS=json.loads((ROOT/"data/blog-feature-pathways.json").read_text(encoding="utf8"))
if len(BLOG_FEATURE_PATHWAYS)!=6:
    raise ValueError("Unexpected reviewed blog feature pathway mapping")

# Six catalog and editorial contexts, selected for natural purchasing intent.
# The first four cover exactly the eight previously zero-body-inbound routes.
# Article cross-links add useful secondary reader journeys.
PATHWAYS = {
    "collections/sports-water-bottles": (
        "applications/everyday-hydration",
        "features/carry-handle",
        "features/gradient-colors",
    ),
    "collections/kids-water-bottles": (
        "applications/kids-school",
        "features/straw-lid",
    ),
    "collections/large-capacity-water-jugs": (
        "applications/outdoor-travel",
        "features/large-capacity",
    ),
    "capabilities/custom-logo": ("applications/promotional-gifts",),
    **BLOG_FEATURE_PATHWAYS,
}

TEXT = {
    "en": {
        "title": "Explore related buyer resources",
        "lead": "Compare relevant use cases, procurement guidance and bottle features before selecting a model.",
        "applications/everyday-hydration": "Everyday hydration applications",
        "applications/kids-school": "Kids and school bottle applications",
        "applications/outdoor-travel": "Outdoor and travel applications",
        "applications/promotional-gifts": "Promotional gift bottle applications",
        "features/large-capacity": "Large-capacity bottle designs",
        "features/carry-handle": "Carry-handle bottle options",
        "features/gradient-colors": "Gradient-color bottle options",
        "features/straw-lid": "Straw-lid bottle options",
        "blog/bulk-water-bottles-for-school-student-programs": "School and student-program bottle buying guide",
        "blog/corporate-wellness-water-bottle-bulk-sourcing": "Corporate wellness bottle sourcing guide",
        "blog/parks-recreation-water-bottle-bulk-procurement": "Parks and recreation bottle procurement guide",
    },
    "es": {
        "title": "Consulta recursos de compra relacionados",
        "lead": "Compara los usos, las recomendaciones de compra y las características de las botellas antes de elegir un modelo.",
        "applications/everyday-hydration": "Botellas para hidratación diaria",
        "applications/kids-school": "Botellas para niños y escuela",
        "applications/outdoor-travel": "Botellas para exteriores y viajes",
        "applications/promotional-gifts": "Botellas para regalos promocionales",
        "features/large-capacity": "Diseños de gran capacidad",
        "features/carry-handle": "Opciones con asa de transporte",
        "features/gradient-colors": "Opciones con colores degradados",
        "features/straw-lid": "Opciones con tapa y pajita",
        "blog/bulk-water-bottles-for-school-student-programs": "Guía de compra de botellas para escuelas y programas estudiantiles",
        "blog/corporate-wellness-water-bottle-bulk-sourcing": "Guía de abastecimiento de botellas para bienestar corporativo",
        "blog/parks-recreation-water-bottle-bulk-procurement": "Guía de compra de botellas para parques y recreación",
    },
    "pt": {
        "title": "Explore recursos de compra relacionados",
        "lead": "Compare aplicações, orientações de compra e características das garrafas antes de escolher um modelo.",
        "applications/everyday-hydration": "Garrafas para hidratação diária",
        "applications/kids-school": "Garrafas para crianças e escola",
        "applications/outdoor-travel": "Garrafas para atividades ao ar livre e viagens",
        "applications/promotional-gifts": "Garrafas para brindes promocionais",
        "features/large-capacity": "Modelos de grande capacidade",
        "features/carry-handle": "Modelos com alça de transporte",
        "features/gradient-colors": "Modelos com cores degradê",
        "features/straw-lid": "Modelos com tampa e palhinha",
        "blog/bulk-water-bottles-for-school-student-programs": "Guia de compra de garrafas para escolas e programas estudantis",
        "blog/corporate-wellness-water-bottle-bulk-sourcing": "Guia de fornecimento de garrafas para programas de bem-estar corporativo",
        "blog/parks-recreation-water-bottle-bulk-procurement": "Guia de compra de garrafas para parques e recreação",
    },
    "ru": {
        "title": "Полезные материалы по закупке бутылок",
        "lead": "Сравните сценарии использования, рекомендации по закупке и особенности бутылок перед выбором модели.",
        "applications/everyday-hydration": "Бутылки для ежедневного использования",
        "applications/kids-school": "Детские и школьные бутылки",
        "applications/outdoor-travel": "Бутылки для путешествий и отдыха",
        "applications/promotional-gifts": "Бутылки для рекламных подарков",
        "features/large-capacity": "Бутылки большой ёмкости",
        "features/carry-handle": "Модели с ручками для переноски",
        "features/gradient-colors": "Модели с градиентной окраской",
        "features/straw-lid": "Модели с крышкой и трубочкой",
        "blog/bulk-water-bottles-for-school-student-programs": "Руководство по закупке бутылок для школ и ученических программ",
        "blog/corporate-wellness-water-bottle-bulk-sourcing": "Руководство по закупке бутылок для корпоративных программ здоровья",
        "blog/parks-recreation-water-bottle-bulk-procurement": "Руководство по закупке бутылок для парков и досуга",
    },
    "tr": {
        "title": "İlgili satın alma kaynaklarını inceleyin",
        "lead": "Bir model seçmeden önce kullanım alanlarını, tedarik önerilerini ve şişe özelliklerini karşılaştırın.",
        "applications/everyday-hydration": "Günlük su tüketimi için şişeler",
        "applications/kids-school": "Çocuk ve okul su şişeleri",
        "applications/outdoor-travel": "Açık hava ve seyahat şişeleri",
        "applications/promotional-gifts": "Promosyon hediyesi şişeler",
        "features/large-capacity": "Büyük kapasiteli şişe modelleri",
        "features/carry-handle": "Taşıma saplı şişe seçenekleri",
        "features/gradient-colors": "Degrade renkli şişe seçenekleri",
        "features/straw-lid": "Pipet kapaklı şişe seçenekleri",
        "blog/bulk-water-bottles-for-school-student-programs": "Okullar ve öğrenci programları için şişe satın alma rehberi",
        "blog/corporate-wellness-water-bottle-bulk-sourcing": "Kurumsal sağlık programları için şişe tedarik rehberi",
        "blog/parks-recreation-water-bottle-bulk-procurement": "Parklar ve rekreasyon programları için şişe satın alma rehberi",
    },
}


def apply_to_document(markup,route,locale):
    """Render reviewed locale-native buyer pathways before writing a page."""
    if locale not in LOCALES:
        return markup,"not_applicable"
    base=str(route or "/")
    prefix="/"+locale
    if locale!="en" and base.startswith(prefix+"/"):
        base=base[len(prefix):]
    source=base.strip("/")
    targets=PATHWAYS.get(source)
    if not targets:
        return markup,"not_applicable"
    if markup.count("</main>")!=1:
        raise ValueError("Unexpected main/article layout on "+locale+base)
    if 'class="section buyer-pathways"' in markup:
        return markup,"preserved"
    main=markup.split("<main",1)[-1].split("</main>",1)[0]
    links=[]
    for target in targets:
        # English-only D1 buyer guides must not create unpublished locale URLs.
        if target.startswith("blog/") and locale!="en":
            continue
        href="/" + ("" if locale=="en" or target.startswith("blog/") else locale+"/") + target + "/"
        if 'href="'+href+'"' in main:
            continue
        if target not in TEXT[locale]:
            raise ValueError("Unreviewed contextual target "+target+" for "+locale)
        links.append('<a href="'+href+'">'+html.escape(TEXT[locale][target])+" →</a>")
    if not links:
        return markup,"preserved"
    words=TEXT[locale]
    block=(
        '<section class="section buyer-pathways" aria-label="'+
        html.escape(words["title"],quote=True)+'"><div class="shell">'
        '<h2>'+html.escape(words["title"])+'</h2><p>'+
        html.escape(words["lead"])+'</p><div class="buyer-pathways__links">'+
        "".join(links)+'</div></div></section>'
    )
    return markup.replace("</main>",block+"</main>",1),"generated"


def apply(dist):
    dist = Path(dist)
    changed = 0
    preserved = 0
    for lang in LOCALES:
        prefix = "" if lang == "en" else lang + "/"
        words = TEXT[lang]
        for source, targets in PATHWAYS.items():
            page = dist / prefix / source / "index.html"
            if not page.is_file():
                raise FileNotFoundError("Reviewed contextual source missing: " + str(page))
            markup = page.read_text(encoding="utf-8")
            if markup.count("</main>") != 1:
                raise ValueError("Unexpected main/article layout on " + str(page))
            if 'class="section buyer-pathways"' in markup:
                # An owner may have kept or customized this whole block in
                # CMS. Rebuilding must not append a second version.
                preserved += len(targets)
                continue
            main = markup.split("<main", 1)[-1].split("</main>", 1)[0]
            links = []
            for target in targets:
                # English-only D1 buyer guides are linked only from English source pages.
                if target.startswith("blog/") and lang!="en":
                    continue
                target_prefix = "" if lang=="en" or target.startswith("blog/") else prefix
                linked = dist / target_prefix / target / "index.html"
                if not linked.is_file():
                    raise FileNotFoundError("Contextual target not published: " + str(linked))
                href = "/" + target_prefix + target + "/"
                # The target previously had no incoming contextual link. Do
                # not create a second identical anchor inside the same source.
                if 'href="' + href + '"' in main:
                    preserved += 1
                    continue
                links.append('<a href="' + href + '">' + html.escape(words[target]) + " →</a>")
            if not links:
                continue
            block = (
                '<section class="section buyer-pathways" aria-label="' +
                html.escape(words["title"], quote=True) + '"><div class="shell">'
                '<h2>' + html.escape(words["title"]) + '</h2><p>' +
                html.escape(words["lead"]) + '</p><div class="buyer-pathways__links">' +
                "".join(links) + "</div></div></section>"
            )
            markup = markup.replace("</main>", block + "</main>", 1)
            page.write_text(markup, encoding="utf-8")
            changed += len(links)
    print("XUYI_CONTEXTUAL_BUYER_LINKS", changed, "added,",preserved,
          "existing CMS links preserved, five locales")
    return changed


if __name__ == "__main__":
    apply(ROOT / "dist")
