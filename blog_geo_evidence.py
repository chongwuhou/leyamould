"""Shared, source-backed Blog GEO evidence module.

The module reads the final D1-rendered article text, never invents a factory
claim, and only exposes exact figures already present in the article. New D1
articles and configured locales receive the same structured evidence boundary.
"""
from __future__ import annotations

from html import escape, unescape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
_EDITORIAL = json.loads((ROOT / "data/editorial-evidence.json").read_text(encoding="utf-8"))
DETAIL_ROUTE = re.compile(r"^/(?:es/|pt/|ru/|tr/)?blog/([a-z0-9-]+)/$", re.I)
TAG = re.compile(r"<[^>]+>")
FACT = re.compile(
    r"\b\d{2,5}\s?(?:ml|mL|oz|fl\s?oz)\b"
    r"|\b\d+(?:\.\d+)?\s?%\b"
    r"|\b\d+(?:\.\d+)?\s?(?:mm|cm|in|days?|weeks?|pcs?|pieces?|cartons?|colors?|colours?|units?)\b"
    r"|\b\d+\s*[x×]\s*\d+(?:\s*[x×]\s*\d+)?\s*(?:cm|mm|in)?\b",
    re.I,
)

SOURCES = {
    "materials": [
        ("US FDA: food-contact material components", "https://www.fda.gov/food/packaging-food-contact-substances-fcs/determining-regulatory-status-components-food-contact-material"),
        ("EU: plastic food-contact materials, Regulation 10/2011", "https://eur-lex.europa.eu/eli/reg/2011/10"),
        ("ECHA: substances in articles and supply-chain communication", "https://echa.europa.eu/en-GB/regulations/reach/candidate-list-substances-in-articles/communication-in-the-supply-chain"),
    ],
    "food_contact": [
        ("US FDA: food-contact conditions of use", "https://www.fda.gov/food/packaging-food-contact-substances-fcs/food-types-conditions-use-food-contact-substances"),
        ("European Commission: food-contact materials legislation", "https://food.ec.europa.eu/food-safety/chemical-safety/food-contact-materials/legislation_en"),
        ("EU Regulation 2024/3190 on BPA in food-contact materials", "https://eur-lex.europa.eu/eli/reg/2024/3190/oj"),
    ],
    "packaging": [
        ("GS1: GTINs for products with many sizes and colours", "https://support.gs1.org/support/solutions/articles/43000734083-how-many-gs1-gtins-do-i-need-when-i-have-a-product-with-many-sizes-and-colours-"),
        ("ICC: Incoterms rules for delivery costs and risks", "https://iccwbo.org/business-solutions/incoterms-rules/"),
        ("ISTA: transport package testing procedures", "https://www.ista.org/test_procedures.php"),
    ],
    "branding": [
        ("USPTO: trademarks and brand ownership basics", "https://www.uspto.gov/trademarks/basics"),
        ("Pantone: Plastic Standard Chips", "https://www.pantone.com/products/fashion-home-interiors/pantone-plastic-standard-chips"),
        ("FTC: substantiating environmental and product claims", "https://www.ftc.gov/business-guidance/resources/environmental-claims-summary-green-guides"),
    ],
    "quality": [
        ("ISO 2859-1: sampling schemes indexed by acceptance quality limit", "https://www.iso.org/standard/2859-1"),
        ("ISTA: sample condition and documentation in test planning", "https://www.ista.org/transit-tested_program.php"),
        ("US FDA: food-contact material components", "https://www.fda.gov/food/packaging-food-contact-substances-fcs/determining-regulatory-status-components-food-contact-material"),
    ],
    "children": [
        ("CPSC: Children's Product Certificate", "https://www.cpsc.gov/Business--Manufacturing/Testing-Certification/Childrens-Product-Certificate"),
        ("CPSC: small-parts and choking-hazard guidance", "https://www.cpsc.gov/Business--Manufacturing/Business-Education/Business-Guidance/Small-Parts-for-Toys-and-Childrens-Products"),
        ("US FDA: food-contact conditions of use", "https://www.fda.gov/food/packaging-food-contact-substances-fcs/food-types-conditions-use-food-contact-substances"),
    ],
    "retail": [
        ("GS1: GTINs for products with many sizes and colours", "https://support.gs1.org/support/solutions/articles/43000734083-how-many-gs1-gtins-do-i-need-when-i-have-a-product-with-many-sizes-and-colours-"),
        ("Pantone: plastics standards explained", "https://www.pantone.com/hk/en-hk/articles/uses-and-best-practices/did-you-know-pantone-plastics-standards-explained"),
        ("FTC: substantiating environmental and product claims", "https://www.ftc.gov/business-guidance/resources/environmental-claims-summary-green-guides"),
    ],
    "hygiene": [
        ("US FDA Food Code: cleanability reference", "https://www.fda.gov/media/164194/download"),
        ("Cleveland Clinic: reusable-bottle hygiene guidance", "https://health.clevelandclinic.org/mold-in-water-bottle"),
        ("US FDA: food-contact conditions of use", "https://www.fda.gov/food/packaging-food-contact-substances-fcs/food-types-conditions-use-food-contact-substances"),
    ],
    "sourcing": [
        ("ICC: Incoterms rules for delivery costs and risks", "https://iccwbo.org/business-solutions/incoterms-rules/"),
        ("ISO 2859-1: sampling schemes indexed by acceptance quality limit", "https://www.iso.org/standard/2859-1"),
        ("GS1: GTINs for products with many sizes and colours", "https://support.gs1.org/support/solutions/articles/43000734083-how-many-gs1-gtins-do-i-need-when-i-have-a-product-with-many-sizes-and-colours-"),
    ],
}

LABELS = {
    "en": {"eyebrow": "SOURCE-CHECKED BUYER NOTES", "references": "Authoritative references", "facts": "Figures already stated in this guide", "caveat": "These references support the buyer's verification process. They do not certify an XUYI product, factory, material or test result. Confirm the exact SKU, destination market and current rule before purchase."},
    "es": {"eyebrow": "NOTAS DE COMPRA CON FUENTES", "references": "Referencias autorizadas", "facts": "Cifras ya indicadas en esta guía", "caveat": "Estas referencias apoyan la verificación del comprador. No certifican ningún producto, fábrica, material ni ensayo de XUYI. Confirme el SKU exacto, el mercado de destino y la norma vigente antes de comprar."},
    "pt": {"eyebrow": "NOTAS DE COMPRA COM FONTES", "references": "Referências oficiais", "facts": "Números já indicados neste guia", "caveat": "Estas referências apoiam a verificação do comprador. Não certificam qualquer produto, fábrica, material ou ensaio da XUYI. Confirme o SKU exato, o mercado de destino e a regra vigente antes da compra."},
    "ru": {"eyebrow": "ЗАМЕТКИ ДЛЯ ПОКУПАТЕЛЯ С ИСТОЧНИКАМИ", "references": "Авторитетные источники", "facts": "Цифры, уже указанные в руководстве", "caveat": "Эти источники помогают покупателю провести проверку. Они не подтверждают сертификацию продукта, фабрики, материала или испытаний XUYI. Перед закупкой подтвердите точный SKU, рынок назначения и действующие требования."},
    "tr": {"eyebrow": "KAYNAKLI ALICI NOTLARI", "references": "Yetkili kaynaklar", "facts": "Bu rehberde zaten belirtilen ölçümler", "caveat": "Bu kaynaklar alıcının doğrulama sürecini destekler. Herhangi bir XUYI ürünü, fabrikası, malzemesi veya testi için sertifika anlamına gelmez. Satın almadan önce gerçek SKU'yu, hedef pazarı ve güncel kuralı doğrulayın."},
}

THEMES = {
    "materials": {"en": "Material and food-contact evidence", "es": "Evidencia de materiales y contacto alimentario", "pt": "Evidências de materiais e contato com alimentos", "ru": "Доказательства по материалам и контакту с пищей", "tr": "Malzeme ve gıda teması kanıtları"},
    "food_contact": {"en": "Food-contact and use-condition checks", "es": "Controles de contacto alimentario y uso", "pt": "Verificações de contato com alimentos e uso", "ru": "Проверка контакта с пищей и условий применения", "tr": "Gıda teması ve kullanım koşulu kontrolleri"},
    "packaging": {"en": "Packaging, logistics and item identity", "es": "Embalaje, logística e identidad del artículo", "pt": "Embalagem, logística e identidade do item", "ru": "Упаковка, логистика и идентификация товара", "tr": "Ambalaj, lojistik ve ürün kimliği"},
    "branding": {"en": "Brand, colour and claim verification", "es": "Verificación de marca, color y afirmaciones", "pt": "Verificação de marca, cor e alegações", "ru": "Проверка бренда, цвета и заявлений", "tr": "Marka, renk ve iddia doğrulaması"},
    "quality": {"en": "Sampling, inspection and acceptance evidence", "es": "Evidencia de muestreo, inspección y aceptación", "pt": "Evidências de amostragem, inspeção e aceitação", "ru": "Доказательства выборки, проверки и приемки", "tr": "Numune, denetim ve kabul kanıtları"},
    "children": {"en": "Children's-use and safety checks", "es": "Controles de uso infantil y seguridad", "pt": "Verificações de uso infantil e segurança", "ru": "Проверки детского применения и безопасности", "tr": "Çocuk kullanımı ve güvenlik kontrolleri"},
    "retail": {"en": "Retail assortment and product identity", "es": "Surtido minorista e identidad del producto", "pt": "Sortimento de varejo e identidade do produto", "ru": "Розничный ассортимент и идентификация товара", "tr": "Perakende ürün karması ve kimlik"},
    "hygiene": {"en": "Cleaning and care evidence", "es": "Evidencia de limpieza y cuidado", "pt": "Evidências de limpeza e cuidados", "ru": "Доказательства очистки и ухода", "tr": "Temizlik ve bakım kanıtları"},
    "sourcing": {"en": "Sourcing, RFQ and delivery evidence", "es": "Evidencia de abastecimiento, RFQ y entrega", "pt": "Evidências de fornecimento, RFQ e entrega", "ru": "Доказательства закупки, RFQ и поставки", "tr": "Tedarik, RFQ ve teslimat kanıtları"},
}

def _plain(markup):
    value = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", str(markup or ""))
    value = TAG.sub(" ", value)
    return re.sub(r"\s+", " ", unescape(value)).strip()

def _profile(slug, text):
    haystack = (slug + " " + text).casefold()
    if any(term in haystack for term in ("kid", "child", "children", "school", "university")):
        return "children"
    if any(term in haystack for term in ("bpa", "food-contact", "food contact", "tritan", "petg", "polycarbonate", "polypropylene", "material")):
        return "materials"
    if any(term in haystack for term in ("dishwasher", "cleaning", "care", "hygiene", "smell", "mold")):
        return "hygiene"
    if any(term in haystack for term in ("packaging", "carton", "incoterm", "shipping", "export", "barcode", "3pl", "label")):
        return "packaging"
    if any(term in haystack for term in ("logo", "brand", "artwork", "pantone", "colour", "color", "trademark")):
        return "branding"
    if any(term in haystack for term in ("leak", "inspection", "quality", "sample", "testing", "reorder", "replacement")):
        return "quality"
    if any(term in haystack for term in ("retail", "shelf", "assortment", "distributor", "marketplace", "ecommerce")):
        return "retail"
    if any(term in haystack for term in ("food", "hot", "compliance", "bpa-free")):
        return "food_contact"
    return "sourcing"

def _facts(text):
    clean = _plain(text)
    facts=[]
    for match in FACT.finditer(clean):
        start=max(0,match.start()-55)
        end=min(len(clean),match.end()+75)
        snippet=re.sub(r"\s+"," ",clean[start:end]).strip(" ,.;:|-")
        if snippet not in facts:
            facts.append(snippet)
        if len(facts)>=4:
            break
    return facts

def payload(route, page, locale):
    match=DETAIL_ROUTE.fullmatch(route or "")
    if not match:
        return None
    slug=match.group(1)
    text=_plain(page)
    profile=_profile(slug,text)
    explicit=_EDITORIAL.get(slug)
    sources=[{"label":item[0],"url":item[1]} for item in SOURCES[profile]]
    if explicit and explicit.get("sources"):
        sources=[{"label":str(item["label"]),"url":str(item["url"])} for item in explicit["sources"]]
    return {"slug":slug,"profile":profile,"theme":THEMES[profile].get(locale,THEMES[profile]["en"]),"sources":sources,"facts":_facts(page)}

def render(page, route, locale):
    if not DETAIL_ROUTE.fullmatch(route or "") or "id=\"blog-geo-evidence\"" in page:
        return page
    if "id=\"primary-sources\"" in page or "id=\"source-reviewed-deep-dive\"" in page:
        return page
    item=payload(route,page,locale)
    if not item:
        return page
    labels=LABELS.get(locale,LABELS["en"])
    out='<section class="blog-geo-evidence" id="blog-geo-evidence"><span class="eyebrow">'+escape(labels["eyebrow"])+"</span><h2>"+escape(item["theme"])+"</h2>"
    out+='<p>Verification scope: '+escape(item["theme"])+'. Use the references below to check the exact product, market and purchase condition.</p>'
    if item["facts"]:
        out+='<h3>'+escape(labels["facts"])+"</h3><ul>"
        out+="".join("<li>"+escape(fact)+"</li>" for fact in item["facts"])
        out+="</ul>"
    out+='<h3>'+escape(labels["references"])+"</h3><ul>"
    out+="".join('<li><a href="'+escape(source["url"],quote=True)+'" target="_blank" rel="noopener noreferrer">'+escape(source["label"])+" ↗</a></li>" for source in item["sources"])
    out+='</ul><p class="blog-geo-evidence__caveat">'+escape(labels["caveat"])+"</p></section>"
    anchor='<section class="section section--soft blog-related">'
    return page.replace(anchor,out+anchor,1) if anchor in page else page+out
