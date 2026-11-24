"""Source renderer for the LEYA MOULD product site.

The water-cup project supplied the backend contracts, admin routes and Pages
Functions.  This module deliberately owns only the new mould site's public
source pages.  It never reads or writes the water-cup repository or its data.
"""
from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path

from locale_registry import approved_locales
from mould_category_pages import render_category_page

ROOT = Path(__file__).resolve().parent
# The supplied logo is kept as a source asset so the published header can scale it without stretching.
CONFIG = json.loads((ROOT / "deployment/site.config.json").read_text(encoding="utf-8"))
ORIGIN = CONFIG["site"]["origin"]
INDEXING_APPROVED = CONFIG["site"].get("indexingApproved") is True
OUTPUT = ROOT / (os.environ.get("LEYA_OUTPUT_DIR") or ".")
CATALOG = json.loads((ROOT / "data/mould-catalog.json").read_text(encoding="utf-8"))
EDITORIAL_DATA = json.loads((ROOT / "data/mould-news-editorial.json").read_text(encoding="utf-8")) if (ROOT / "data/mould-news-editorial.json").is_file() else {"items": []}
EDITORIAL_BY_SLUG = {str(row.get("slug")): row for row in EDITORIAL_DATA.get("items", []) if isinstance(row, dict) and row.get("slug")}
SNAPSHOT = ROOT / "_local_ops/build-snapshot.json"

# Only images that contain identifiable people are replaced with compressed
# LEYA-specific assets. All other About-page media continues to use the
# reference site's non-portrait images, preserving the approved page design.
ABOUT_MEDIA = {
    "team": "/assets/about/about-team-generated.webp",
    "assembly": "/assets/about/about-assembly-generated.webp",
}
STATE = {}
if SNAPSHOT.is_file():
    candidate = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    if candidate.get("site") == "leyamould":
        STATE = candidate

# The static renderer remains the visual source of truth.  These small
# adapters make its business inputs data-driven in the same way as the
# water-cup project: a reviewed D1 snapshot can override content, while a
# clean checkout still has an auditable source fallback.  No CSS or layout is
# selected from D1, so a CMS edit cannot silently redesign the public site.
BRAND_CONFIG = STATE.get("brand") if isinstance(STATE.get("brand"), dict) else {}
CONTACT_CONFIG = STATE.get("contacts") if isinstance(STATE.get("contacts"), dict) else {}
NAVIGATION = [row for row in STATE.get("navigation", []) if isinstance(row, dict)]
def _normalise_page_row(row: dict) -> dict:
    """Accept the D1 snapshot's snake_case fields and the admin API's camelCase.

    The build snapshot is deliberately a thin D1 export, so it currently carries
    ``seo_title``/``meta_description``/``sitemap_enabled``.  Normalising here
    keeps the renderer independent from the storage naming convention and makes
    the page SEO controls authoritative at build time.
    """
    value = dict(row)
    def boolish(raw):
        if isinstance(raw, str):
            return raw.strip().lower() not in {"", "0", "false", "no", "off"}
        return bool(raw)
    value["seoTitle"] = str(row.get("seoTitle") or row.get("seo_title") or "")
    value["metaDescription"] = str(row.get("metaDescription") or row.get("meta_description") or "")
    value["robots"] = str(row.get("robots") or "")
    if "sitemapEnabled" in row:
        value["sitemapEnabled"] = boolish(row.get("sitemapEnabled"))
    elif "sitemap_enabled" in row:
        value["sitemapEnabled"] = boolish(row.get("sitemap_enabled"))
    else:
        value["sitemapEnabled"] = None
    return value


PAGE_OVERRIDES = {
    str(row.get("route")): _normalise_page_row(row)
    for row in STATE.get("pages", [])
    if isinstance(row, dict) and row.get("route")
}
PRODUCT_SEO_OVERRIDES = {}
for _seo in STATE.get("productSeo", []):
    if not isinstance(_seo, dict) or not _seo.get("slug"):
        continue
    _slug = str(_seo.get("slug")).strip().lower()
    _locale = str(_seo.get("locale") or "en").strip().lower()
    _title = str(_seo.get("seoTitle") or _seo.get("seo_title") or "").strip()
    _description = str(_seo.get("metaDescription") or _seo.get("meta_description") or "").strip()
    if _title or _description:
        PRODUCT_SEO_OVERRIDES[(_slug, _locale)] = {
            "seoTitle": _title,
            "metaDescription": _description,
        }

# Reviewed source fallback for the two currently published locales. D1 rows
# remain authoritative and replace these values as soon as an editor saves a
# locale-specific product SEO record.
PRODUCT_FALLBACK_SEO = {
    "mineral-water-closure-cap-molds": {"seoTitle": "Molde de tapón para agua y bebidas", "metaDescription": "Moldes de alta precisión para cierres de agua mineral, bebidas carbonatadas y zumos."},
    "oil-bottle-cap-mould": {"seoTitle": "Molde de tapón para aceite comestible", "metaDescription": "Soluciones de molde para cierres con anilla y evidencia de manipulación en envases de aceite."},
    "flip-top-caps-mould": {"seoTitle": "Molde de tapón cosmético flip-top", "metaDescription": "Moldes con bisagra viva para envases de champú, acondicionador y cuidado personal."},
    "engine-oil-cap-mould": {"seoTitle": "Molde de tapón para aceite de motor", "metaDescription": "Moldes resistentes para cierres de lubricantes de automoción y envases industriales."},
    "food-packaging-cap-mould": {"seoTitle": "Molde de tapón para envases alimentarios", "metaDescription": "Moldes para cierres roscados y a presión de salsas, lácteos y alimentos secos."},
    "medical-cap-mould": {"seoTitle": "Molde de tapón médico", "metaDescription": "Moldes de precisión para frascos farmacéuticos, jarabes y envases de diagnóstico."},
    "personal-care-cap-mould": {"seoTitle": "Molde de tapón para cuidado personal", "metaDescription": "Moldes para cierres disc-top, tubos y lociones con opciones de orificio personalizado."},
    "functional-cap-mould": {"seoTitle": "Molde de tapón funcional combinado", "metaDescription": "Moldes para mecanismos de seguridad infantil, apertura fácil y evidencia de manipulación."},
    "plastic-handle-cap-mould": {"seoTitle": "Molde de asa de plástico", "metaDescription": "Moldes de asas ergonómicas para botellas PET de 5 a 20 litros, aceite y bidones químicos."},
    "five-gallon-water-cap-mould": {"seoTitle": "Molde de tapón para garrafón de 5 galones", "metaDescription": "Moldes para cierres de garrafón de 18,9 litros con sellado, banda de seguridad y compatibilidad con dispensadores."},
    "wine-cap-mould": {"seoTitle": "Molde de tapón para vino y licores", "metaDescription": "Moldes de precisión para cierres de vino, licores, vertedores y superficies decorativas."},
    "pet-preform-mould": {"seoTitle": "Molde de preformas PET", "metaDescription": "Moldes multicavidad para preformas PET y PP con control de peso, cuello y proceso de soplado."},
    "blow-bottle-mould": {"seoTitle": "Molde de soplado para botellas", "metaDescription": "Moldes de soplado para botellas PET y envases personalizados con control de pared, cuello y refrigeración."},
}

CANONICAL_ALIASES = {
    "/about/about_us.html", "/about/ABOUT_US.html", "/machine/Cap-Auxiliary-Machines.html",
    "/contact/contact_us.html", "/cap-samples/Sample.html", "/news/news.html",
    "/videolist/Cap-Mold-Video.html", "/about/FAQs.html",
}
BODY_OVERRIDES = {str(row.get("route")): str(row.get("mainHtml", "")) for row in STATE.get("pageBodies", []) if isinstance(row, dict) and row.get("route")}
TRANSLATION_OVERRIDES = {(str(row.get("resourceId")), str(row.get("locale"))): row.get("content") for row in STATE.get("translations", []) if isinstance(row, dict)}
BANNER_CONFIG = STATE.get("banners") if isinstance(STATE.get("banners"), dict) else {}

def _first_contact() -> dict:
    contacts = CONTACT_CONFIG.get("contacts", []) if isinstance(CONTACT_CONFIG, dict) else []
    return next((row for row in contacts if isinstance(row, dict) and row.get("enabled", True) and row.get("isDefault")), None) or next((row for row in contacts if isinstance(row, dict) and row.get("enabled", True)), {})

_brand_identity = BRAND_CONFIG.get("identity", {}) if isinstance(BRAND_CONFIG, dict) else {}
_brand_contact = BRAND_CONFIG.get("contact", {}) if isinstance(BRAND_CONFIG, dict) else {}
_default_contact = _first_contact()
ADDRESS = str(_brand_contact.get("address") or "4-55,Xicheng New Village,Huangyan Taizhou,Zhejiang Province, China")
EMAIL = str(_brand_contact.get("email") or _default_contact.get("email") or "amyhu@leyamould.com")
WHATSAPP = str(_brand_contact.get("phoneDisplay") or _brand_contact.get("phoneE164") or _default_contact.get("phoneDisplay") or _default_contact.get("phoneE164") or "+8613606727715")
_wa_candidate = str(_brand_contact.get("whatsappShortUrl") or _brand_contact.get("whatsappUrl") or _default_contact.get("whatsappUrl") or "https://wa.me/8613606727715")
WA_URL = _wa_candidate if _wa_candidate.startswith(("https://", "http://")) else "https://wa.me/8613606727715"
BRAND_DISPLAY = str(_brand_identity.get("displayName") or "LEYA MOULD")
BRAND_LEGAL = str(_brand_identity.get("legalName") or "LEYA MOULD Co.,Ltd")
_social_config = BRAND_CONFIG.get("social", {}) if isinstance(BRAND_CONFIG, dict) else {}
SOCIAL_URLS = {
    "tiktok": str(_social_config.get("tiktok") or "https://www.tiktok.com/"),
    "youtube": str(_social_config.get("youtube") or "https://www.youtube.com/"),
    "facebook": str(_social_config.get("facebook") or "https://www.facebook.com/"),
}
for _social_key, _social_value in list(SOCIAL_URLS.items()):
    if not _social_value.startswith(("https://", "http://")):
        SOCIAL_URLS[_social_key] = "https://www." + _social_key + ".com/"

TOPBAR_ICONS = {
    "email": "M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z",
    "phone": "M6.62 10.79a15.05 15.05 0 006.59 6.59l2.2-2.2a1 1 0 011.01-.24 11.36 11.36 0 003.58.57 1 1 0 011 1V20a1 1 0 01-1 1A17 17 0 013 4a1 1 0 011-1h3.5a1 1 0 011 1 11.36 11.36 0 00.57 3.58 1 1 0 01-.25 1.01l-2.2 2.2z",
    "pin": "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5S10.62 6.5 12 6.5s2.5 1.12 2.5 2.5S13.38 11.5 12 11.5z",
    "tiktok": "M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z",
    "youtube": "M23.5 6.19a3.02 3.02 0 00-2.12-2.14C19.5 3.5 12 3.5 12 3.5s-7.5 0-9.38.55A3.02 3.02 0 00.5 6.19 31.6 31.6 0 000 12a31.6 31.6 0 00.5 5.81 3.02 3.02 0 002.12 2.14c1.88.55 9.38.55 9.38.55s7.5 0 9.38-.55a3.02 3.02 0 002.12-2.14A31.6 31.6 0 0024 12a31.6 31.6 0 00-.5-5.81zM9.55 15.57V8.43L15.82 12l-6.27 3.57z",
    "facebook": "M24 12.07C24 5.41 18.63 0 12 0S0 5.4 0 12.07C0 18.1 4.39 23.1 10.13 24v-8.44H7.08v-3.49h3.05V9.41c0-3.02 1.8-4.7 4.54-4.7 1.31 0 2.68.24 2.68.24v2.97h-1.51c-1.49 0-1.96.93-1.96 1.89v2.26h3.33l-.53 3.49h-2.8V24C19.61 23.1 24 18.1 24 12.07z",
}

def topbar_icon(name: str) -> str:
    return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="' + TOPBAR_ICONS[name] + '" fill="currentColor"></path></svg>'

def _published_content(row: object) -> dict:
    if not isinstance(row, dict):
        return {}
    content = row.get("content")
    return content if isinstance(content, dict) else {}

def _catalog_from_state() -> list[dict]:
    """Overlay only mould category records; never import water-cup models."""
    rows = json.loads(json.dumps(CATALOG.get("categories", [])))
    by_slug = {str(item.get("slug")): item for item in rows}
    for row in STATE.get("products", []):
        if not isinstance(row, dict):
            continue
        model = str(row.get("model") or "")
        content = _published_content(row)
        item = by_slug.get(model)
        if item is None:
            item = by_slug.get(str(content.get("slug") or ""))
        if item is None or not content:
            continue
        for field in ("title", "navTitle", "description", "short", "detail", "meta", "image", "route"):
            if isinstance(content.get(field), str) and content[field].strip():
                item[field] = content[field].strip()
        if isinstance(content.get("checks"), list):
            item["checks"] = [str(value).strip() for value in content["checks"] if str(value).strip()][:12]
    return rows

CATALOG["categories"] = _catalog_from_state()
_header_logo = (BRAND_CONFIG.get("logos", {}).get("header", {}) if isinstance(BRAND_CONFIG, dict) else {})
LOGO_SRC = str(_header_logo.get("src") or "/assets/leyamould-logo.svg?v=logo1")
if not (LOGO_SRC.startswith("/") or LOGO_SRC.startswith("https://")):
    LOGO_SRC = "/assets/leyamould-logo.svg?v=logo1"
LOGO_ALT = str(_header_logo.get("alt") or BRAND_DISPLAY)

def navigation_label(url: str, fallback: str) -> str:
    """Use D1's reviewed label without changing the frozen menu structure."""
    rows = [row for row in NAVIGATION if str(row.get("url") or "") == url]
    rows.sort(key=lambda row: (int(row.get("sort_order", row.get("sortOrder", 999)) or 999), str(row.get("id", ""))))
    return str(rows[0].get("label") or fallback) if rows else fallback

def localized_override(locale: str, route: str) -> dict:
    value = TRANSLATION_OVERRIDES.get(("page:" + route, locale))
    return value if isinstance(value, dict) else {}


def product_slug_for_route(route: str) -> str:
    """Resolve a public product route to the catalogue's canonical slug."""
    for item in CATALOG.get("categories", []):
        if not isinstance(item, dict):
            continue
        if str(item.get("route") or "") == route:
            return str(item.get("slug") or "").strip().lower()
    match = re.fullmatch(r"/product/([^/]+)\.html", route)
    return match.group(1).strip().lower() if match else ""


def page_override_for(locale: str, route: str) -> dict:
    """Return route metadata, preferring the product SEO row for this locale."""
    value = dict(PAGE_OVERRIDES.get(route, {}))
    slug = product_slug_for_route(route)
    if slug:
        product = PRODUCT_SEO_OVERRIDES.get((slug, locale)) or PRODUCT_SEO_OVERRIDES.get((slug, "en"))
        if not product and locale == "es":
            product = PRODUCT_FALLBACK_SEO.get(slug)
        if product:
            value.update(product)
    return value


def effective_robots(route: str) -> str:
    """Keep the entire site blocked until launch approval, then honour D1."""
    if not INDEXING_APPROVED:
        return "noindex,nofollow"
    if route in CANONICAL_ALIASES:
        return "noindex,follow"
    value = str(PAGE_OVERRIDES.get(route, {}).get("robots") or "index,follow")
    return value if value in {"index,follow", "noindex,follow", "noindex,nofollow"} else "index,follow"


def sitemap_enabled(route: str) -> bool:
    """Use the page registry when present; generated routes default to included."""
    if not INDEXING_APPROVED:
        return False
    if route in CANONICAL_ALIASES:
        return False
    row = PAGE_OVERRIDES.get(route)
    if isinstance(row, dict) and row.get("sitemapEnabled") is not None:
        return bool(row.get("sitemapEnabled"))
    return True


def canonical_route_from_localized(route: str) -> str:
    """Strip a configured locale prefix from a generated public URL."""
    value = str(route or "")
    for lang in LOCALES:
        prefix = str(lang.get("pathPrefix") or "").strip("/")
        if prefix and value.startswith("/" + prefix + "/"):
            return value[len(prefix) + 1 :]
    return value

def effective_banners(locale: str) -> list[dict]:
    slides = BANNER_CONFIG.get("slides", []) if isinstance(BANNER_CONFIG, dict) else []
    if not isinstance(slides, list) or len(slides) != 3:
        return []
    result = []
    for slide in slides:
        if not isinstance(slide, dict):
            return []
        value = dict(slide)
        translated = slide.get("translations", {}).get(locale, {}) if isinstance(slide.get("translations"), dict) else {}
        if isinstance(translated, dict):
            value.update({key: translated[key] for key in ("title", "highlight", "description", "alt", "cta") if isinstance(translated.get(key), str) and translated[key].strip()})
        if not all(isinstance(value.get(key), str) and value[key].strip() for key in ("img", "link", "title", "highlight", "description", "alt", "cta")):
            return []
        result.append({key: value[key] for key in ("img", "link", "title", "highlight", "description", "alt", "cta")})
    return result

LOCALES = approved_locales(STATE, require_resources=False)
if not LOCALES:
    # A clean GitHub checkout may not contain the read-only D1 snapshot. Keep
    # the deployment-configured public locales in the static source build so
    # a missing snapshot cannot silently drop the Spanish route tree.
    names = {"en": "English", "es": "Español", "pt": "Português", "ru": "Русский", "tr": "Türkçe"}
    configured = CONFIG["site"].get("publishedLocales") or ["en"]
    LOCALES = [{"code": "en", "pathPrefix": "", "nativeName": "English", "sortOrder": 10}]
    for index, code in enumerate(configured, start=20):
        if code == "en":
            continue
        LOCALES.append({"code": code, "pathPrefix": code, "nativeName": names.get(code, code), "sortOrder": index})

TEXT = {
    "en": {
        "home": "Home", "about": "About us", "products": "Products", "capabilities": "Capabilities",
        "process": "How We Work", "news": "News", "samples": "Samples", "video": "Video", "cap_mould": "Cap Mould", "machine": "Machine", "contact_us": "Contact Us", "contact": "Contact", "quote": "Request a Quote",
        "hero_eyebrow": "PRECISION MOULDING · ENGINEERING · SUPPORT",
        "hero_title": "Your Trusted Plastic Cap Mould Manufacturer",
        "hero_text": "15+ years of precision moulding experience for global packaging projects, with clear engineering review from design through trial and handover.",
        "hero_primary": "Explore Mould Categories →", "hero_secondary": "Tell Us About Your Project",
        "hero_note": "LEYA MOULD · Huangyan, Taizhou, Zhejiang, China",
        "categories_eyebrow": "MOULD CATEGORIES", "categories_title": "Tooling directions for packaging and product makers.",
        "categories_text": "Start with a product family. We will confirm the drawing, material, cavity plan, machine interface and evidence required for a responsible quotation.",
        "why_eyebrow": "WHY LEYA MOULD", "why_title": "A practical engineering conversation before steel is cut.",
        "why_text": "A mould project is easier to control when the product drawing, resin, machine, quality points and sample plan are discussed together. LEYA MOULD keeps the workflow clear and project-specific.",
        "advantages": [("Design review", "Part geometry, parting line, cooling and ejection are checked against the intended process."), ("Project matching", "The tooling brief records the mould family, material, machine interface and target output information supplied by the buyer."), ("Sample-led decisions", "Trial parts and agreed inspection points guide optimisation before production handover."), ("Clear communication", "Drawings, PDFs, photos and revision notes stay attached to the enquiry." )],
        "process_eyebrow": "HOW WE WORK", "process_title": "From drawing to a controlled tooling handover.",
        "process_steps": [("01", "Share Design", "Send your drawing or sample for an initial technical review."), ("02", "DFM Analysis", "Review mould flow, parting, cooling and optimisation opportunities."), ("03", "Manufacturing", "Coordinate precision machining, EDM, fitting and heat treatment."), ("04", "Trial & Inspection", "Complete trial runs, dimensional checks and agreed inspection evidence."), ("05", "Delivery & Support", "Keep approved files, delivery notes and technical support connected.")],
        "technical_eyebrow": "TECHNICAL CONTENT", "technical_title": "Built around evidence, not generic promises.",
        "technical_text": "Product drawings, high-resolution images and PDFs will be added to the relevant category as they are approved. Until then, category pages clearly show which information is still to be confirmed.",
        "technical_cta": "Send a Drawing or PDF →", "resources_title": "Mould project resources", "resources_text": "Share the part drawing, target resin, expected cavities, machine model, sample or PDF. We will return with the questions needed for a useful quotation.",
        "footer_tagline": "Bottle, cap, preform and custom product mould support for international buyers.", "footer_products": "Products", "footer_capabilities": "Capabilities", "footer_contact": "Contact Us", "footer_design": "Mould Design & Engineering", "footer_manufacturing": "Precision Manufacturing", "footer_quality": "Quality & Inspection", "footer_support": "Trial & Technical Support", "footer_quote": "Request a Quote →", "footer_faq": "FAQs", "footer_privacy": "Privacy Policy", "footer_sticky": "Mould Project Enquiries", "footer_cta_title": "Ready to discuss your mould project?", "footer_cta_text": "Send your drawing, sample or PDF and tell us the production target.", "footer_eyebrow": "LEYA MOULD · ENGINEERING · MANUFACTURING", "form_required": "Company name, work email and project requirements are required. Technical drawings, samples and documents can be attached later by email or WhatsApp.", "form_company": "Company Name", "form_email": "Work Email", "form_category": "Mould Category", "form_quantity": "Estimated Quantity", "form_country": "Destination Country", "form_type": "Inquiry Type", "form_quote": "Request a Quote", "form_new": "New Mould Design", "form_review": "Existing Mould Review", "form_tech": "Technical Consultation", "form_material": "Target Material", "form_advise": "Please advise", "form_other": "Other / to be confirmed", "form_requirements": "Your Requirements", "form_consent": "I agree to the", "form_privacy": "privacy policy", "form_submit": "Send Project Enquiry →", "form_aria": "Mould project enquiry form", "back": "Back to Home →", "learn": "Learn More →", "view": "View Category →", "category_note": "Technical specifications, images and PDF references are added after project review.", "contact_title": "Tell us about your mould project.", "contact_intro": "Send the part drawing, sample, target material, cavity plan, machine information and delivery market. We will reply with the next technical questions.", "faq_title": "Mould project questions", "faq_intro": "A short starting point for buyers preparing a tooling enquiry.", "about_title": "About LEYA MOULD", "about_text": "LEYA MOULD Co.,Ltd is a mould-project brand based in Huangyan, Taizhou, Zhejiang Province, China. The site is being prepared around an evidence-led catalogue for packaging and product tooling.", "privacy_title": "Privacy & enquiry data", "privacy_text": "We use the information you submit to respond to mould project enquiries, technical questions and quotation requests. Contact amyhu@leyamould.com for data questions.", "blog_title": "Mould project resources", "blog_text": "Technical articles and approved project resources will be added as the mould catalogue is reviewed.",
    },
    "es": {}, "pt": {}, "ru": {}, "tr": {}
}
TEXT["es"] = {**TEXT["en"], "home":"Inicio", "about":"Sobre nosotros", "products":"Productos", "capabilities":"Capacidades", "process":"Cómo trabajamos", "news":"Recursos", "contact":"Contacto", "quote":"Solicitar cotización", "hero_eyebrow":"MOLDES DE PRECISIÓN · INGENIERÍA · SOPORTE", "hero_title":"Moldes preparados para su próxima producción.", "hero_text":"LEYA MOULD acompaña proyectos de moldes para preformas, tapones, botellas y cubiertos desde la revisión del diseño hasta las pruebas.", "hero_primary":"Explorar categorías →", "hero_secondary":"Cuéntenos su proyecto", "categories_eyebrow":"CATEGORÍAS DE MOLDES", "categories_title":"Direcciones de utillaje para fabricantes de envases y productos.", "categories_text":"Comience con una familia de productos. Confirmaremos el plano, material, cavidades, máquina y evidencias necesarias.", "why_eyebrow":"POR QUÉ LEYA MOULD", "why_title":"Una conversación técnica antes de fabricar el acero.", "why_text":"Un proyecto de moldes se controla mejor cuando se revisan juntos el plano, la resina, la máquina, los puntos de calidad y el plan de muestras.", "technical_eyebrow":"CONTENIDO TÉCNICO", "technical_title":"Basado en evidencias, no en promesas genéricas.", "technical_text":"Las imágenes de alta resolución y los PDF aprobados se añadirán a cada categoría cuando estén disponibles.", "technical_cta":"Enviar plano o PDF →", "resources_title":"Recursos del proyecto", "resources_text":"Comparta el plano, resina, cavidades, máquina, muestra o PDF. Responderemos con las preguntas necesarias.", "footer_tagline":"Soporte para moldes de botellas, tapones, preformas y productos a medida.", "footer_products":"Productos", "footer_capabilities":"Capacidades", "footer_contact":"Contacto", "footer_design":"Diseño e ingeniería", "footer_manufacturing":"Fabricación de precisión", "footer_quality":"Calidad e inspección", "footer_support":"Pruebas y soporte técnico", "footer_quote":"Solicitar cotización →", "footer_faq":"Preguntas frecuentes", "footer_privacy":"Privacidad", "footer_sticky":"Consultas de moldes", "footer_cta_title":"¿Hablamos de su proyecto?", "footer_cta_text":"Envíe su plano, muestra o PDF y el objetivo de producción.", "footer_eyebrow":"LEYA MOULD · INGENIERÍA · FABRICACIÓN", "contact_title":"Cuéntenos su proyecto de moldes.", "contact_intro":"Envíe el plano, muestra, material, cavidades, máquina y mercado de destino.", "faq_title":"Preguntas sobre moldes", "faq_intro":"Puntos iniciales para preparar una consulta técnica.", "about_title":"Sobre LEYA MOULD", "about_text":"LEYA MOULD Co.,Ltd es una marca de proyectos de moldes con sede en Huangyan, Taizhou, Zhejiang, China.", "privacy_title":"Privacidad y consultas", "privacy_text":"Usamos los datos enviados para responder consultas técnicas y solicitudes de cotización. Contacte con amyhu@leyamould.com.", "blog_title":"Recursos de moldes", "blog_text":"Los artículos técnicos y recursos aprobados se añadirán al revisar el catálogo."}
TEXT["pt"] = {**TEXT["en"], "home":"Início", "about":"Sobre nós", "products":"Produtos", "capabilities":"Capacidades", "process":"Como trabalhamos", "news":"Recursos", "contact":"Contato", "quote":"Solicitar cotação", "hero_eyebrow":"MOLDES DE PRECISÃO · ENGENHARIA · SUPORTE", "hero_title":"Moldes preparados para a sua próxima produção.", "hero_text":"A LEYA MOULD apoia projetos de moldes para pré-formas, tampas, garrafas e talheres desde a revisão do desenho até os testes.", "hero_primary":"Explorar categorias →", "hero_secondary":"Fale sobre o seu projeto", "categories_eyebrow":"CATEGORIAS DE MOLDES", "categories_title":"Soluções de ferramentaria para fabricantes de embalagens e produtos.", "categories_text":"Comece por uma família de produtos. Confirmaremos desenho, material, cavidades, máquina e evidências necessárias.", "why_eyebrow":"POR QUE LEYA MOULD", "why_title":"Uma conversa de engenharia antes de cortar o aço.", "why_text":"Um projeto de moldes é mais controlável quando desenho, resina, máquina, qualidade e amostras são analisados juntos.", "technical_eyebrow":"CONTEÚDO TÉCNICO", "technical_title":"Construído com evidências, não promessas genéricas.", "technical_text":"Imagens em alta resolução e PDFs aprovados serão adicionados a cada categoria quando disponíveis.", "technical_cta":"Enviar desenho ou PDF →", "resources_title":"Recursos do projeto", "resources_text":"Envie desenho, resina, cavidades, máquina, amostra ou PDF. Retornaremos com as perguntas técnicas necessárias.", "footer_tagline":"Suporte para moldes de garrafas, tampas, pré-formas e produtos personalizados.", "footer_products":"Produtos", "footer_capabilities":"Capacidades", "footer_contact":"Contato", "footer_design":"Projeto e engenharia", "footer_manufacturing":"Fabricação de precisão", "footer_quality":"Qualidade e inspeção", "footer_support":"Testes e suporte técnico", "footer_quote":"Solicitar cotação →", "footer_faq":"Perguntas frequentes", "footer_privacy":"Privacidade", "footer_sticky":"Consultas de moldes", "footer_cta_title":"Vamos conversar sobre o seu projeto?", "footer_cta_text":"Envie desenho, amostra ou PDF e a meta de produção.", "footer_eyebrow":"LEYA MOULD · ENGENHARIA · FABRICAÇÃO", "contact_title":"Fale sobre o seu projeto de moldes.", "contact_intro":"Envie desenho, amostra, material, cavidades, máquina e mercado de destino.", "faq_title":"Perguntas sobre moldes", "faq_intro":"Pontos iniciais para preparar uma consulta técnica.", "about_title":"Sobre a LEYA MOULD", "about_text":"A LEYA MOULD Co.,Ltd é uma marca de projetos de moldes sediada em Huangyan, Taizhou, Zhejiang, China.", "privacy_title":"Privacidade e consultas", "privacy_text":"Usamos os dados enviados para responder consultas técnicas e pedidos de cotação. Contacte amyhu@leyamould.com.", "blog_title":"Recursos de moldes", "blog_text":"Artigos técnicos e recursos aprovados serão adicionados após a revisão do catálogo."}
TEXT["ru"] = {**TEXT["en"], "home":"Главная", "about":"О компании", "products":"Продукция", "capabilities":"Возможности", "process":"Как мы работаем", "news":"Ресурсы", "contact":"Контакты", "quote":"Запросить расчёт", "hero_eyebrow":"ПРЕЦИЗИОННЫЕ ПРЕСС-ФОРМЫ · ИНЖИНИРИНГ · ПОДДЕРЖКА", "hero_title":"Пресс-формы для вашего следующего производства.", "hero_text":"LEYA MOULD сопровождает проекты пресс-форм для преформ, крышек, бутылок и столовых приборов от проверки чертежа до испытаний.", "hero_primary":"Категории пресс-форм →", "hero_secondary":"Обсудить проект", "categories_eyebrow":"КАТЕГОРИИ ПРЕСС-ФОРМ", "categories_title":"Оснастка для производителей упаковки и изделий.", "categories_text":"Выберите семейство изделий. Мы уточним чертёж, материал, число гнёзд, машину и необходимые подтверждения.", "why_eyebrow":"ПОЧЕМУ LEYA MOULD", "why_title":"Практический инженерный диалог до изготовления стали.", "why_text":"Проект проще контролировать, когда чертёж, полимер, машина, контроль качества и образцы рассматриваются вместе.", "technical_eyebrow":"ТЕХНИЧЕСКИЕ МАТЕРИАЛЫ", "technical_title":"Опора на подтверждённые данные, а не общие обещания.", "technical_text":"Одобренные изображения высокого разрешения и PDF будут добавлены к категориям после проверки.", "technical_cta":"Отправить чертёж или PDF →", "resources_title":"Материалы проекта", "resources_text":"Отправьте чертёж, полимер, число гнёзд, данные машины, образец или PDF. Мы вернёмся с необходимыми вопросами.", "footer_tagline":"Пресс-формы для бутылок, крышек, преформ и изделий по индивидуальному проекту.", "footer_products":"Продукция", "footer_capabilities":"Возможности", "footer_contact":"Контакты", "footer_design":"Проектирование и инжиниринг", "footer_manufacturing":"Прецизионное производство", "footer_quality":"Качество и контроль", "footer_support":"Испытания и техническая поддержка", "footer_quote":"Запросить расчёт →", "footer_faq":"Вопросы", "footer_privacy":"Конфиденциальность", "footer_sticky":"Запрос по пресс-форме", "footer_cta_title":"Обсудим ваш проект пресс-формы?", "footer_cta_text":"Отправьте чертёж, образец или PDF и цель производства.", "footer_eyebrow":"LEYA MOULD · ИНЖИНИРИНГ · ПРОИЗВОДСТВО", "contact_title":"Расскажите о проекте пресс-формы.", "contact_intro":"Отправьте чертёж, образец, материал, число гнёзд, данные машины и рынок.", "faq_title":"Вопросы о пресс-формах", "faq_intro":"Краткая основа для подготовки технического запроса.", "about_title":"О компании LEYA MOULD", "about_text":"LEYA MOULD Co.,Ltd — бренд проектов пресс-форм из Хуанъяня, Тайчжоу, провинция Чжэцзян, Китай.", "privacy_title":"Конфиденциальность и запросы", "privacy_text":"Мы используем отправленные данные для ответа на технические запросы и расчёты. Свяжитесь с amyhu@leyamould.com.", "blog_title":"Ресурсы по пресс-формам", "blog_text":"Технические статьи и одобренные материалы будут добавлены после проверки каталога."}
TEXT["tr"] = {**TEXT["en"], "home":"Ana Sayfa", "about":"Hakkımızda", "products":"Ürünler", "capabilities":"Yetenekler", "process":"Nasıl Çalışıyoruz", "news":"Kaynaklar", "contact":"İletişim", "quote":"Teklif İste", "hero_eyebrow":"HASSAS KALIPLAMA · MÜHENDİSLİK · DESTEK", "hero_title":"Bir sonraki üretiminiz için kalıplar.", "hero_text":"LEYA MOULD; preform, kapak, şişe ve çatal-bıçak kalıp projelerine tasarım incelemesinden denemeye kadar destek verir.", "hero_primary":"Kalıp Kategorilerini Gör →", "hero_secondary":"Projenizi Anlatın", "categories_eyebrow":"KALIP KATEGORİLERİ", "categories_title":"Ambalaj ve ürün üreticileri için kalıp yönleri.", "categories_text":"Bir ürün ailesi seçin. Çizim, malzeme, göz sayısı, makine ve gerekli kanıtları birlikte netleştirelim.", "why_eyebrow":"NEDEN LEYA MOULD", "why_title":"Çelik işlenmeden önce pratik mühendislik görüşmesi.", "why_text":"Çizim, reçine, makine, kalite noktaları ve numune planı birlikte incelendiğinde proje daha iyi kontrol edilir.", "technical_eyebrow":"TEKNİK İÇERİK", "technical_title":"Genel vaatler yerine kanıta dayalı çalışma.", "technical_text":"Onaylanan yüksek çözünürlüklü görseller ve PDF'ler inceleme sonrasında ilgili kategoriye eklenir.", "technical_cta":"Çizim veya PDF Gönder →", "resources_title":"Proje kaynakları", "resources_text":"Çizim, reçine, göz sayısı, makine, numune veya PDF gönderin. Gerekli teknik sorularla geri dönelim.", "footer_tagline":"Şişe, kapak, preform ve özel ürün kalıpları için uluslararası proje desteği.", "footer_products":"Ürünler", "footer_capabilities":"Yetenekler", "footer_contact":"İletişim", "footer_design":"Kalıp tasarımı ve mühendislik", "footer_manufacturing":"Hassas üretim", "footer_quality":"Kalite ve kontrol", "footer_support":"Deneme ve teknik destek", "footer_quote":"Teklif İste →", "footer_faq":"SSS", "footer_privacy":"Gizlilik", "footer_sticky":"Kalıp proje talepleri", "footer_cta_title":"Kalıp projenizi görüşelim mi?", "footer_cta_text":"Çiziminizi, numunenizi veya PDF'inizi ve üretim hedefinizi gönderin.", "footer_eyebrow":"LEYA MOULD · MÜHENDİSLİK · ÜRETİM", "contact_title":"Kalıp projenizi anlatın.", "contact_intro":"Parça çizimini, numuneyi, malzemeyi, göz sayısını, makineyi ve hedef pazarı gönderin.", "faq_title":"Kalıp projesi soruları", "faq_intro":"Teknik bir talep hazırlayan alıcılar için kısa başlangıç bilgileri.", "about_title":"LEYA MOULD Hakkında", "about_text":"LEYA MOULD Co.,Ltd, Huangyan, Taizhou, Zhejiang, Çin merkezli bir kalıp proje markasıdır.", "privacy_title":"Gizlilik ve talepler", "privacy_text":"Gönderdiğiniz bilgileri teknik sorulara ve teklif taleplerine yanıt vermek için kullanırız. amyhu@leyamould.com adresinden ulaşabilirsiniz.", "blog_title":"Kalıp proje kaynakları", "blog_text":"Teknik makaleler ve onaylı proje kaynakları katalog incelendikçe eklenecektir."}

TEXT["es"].update({"samples": "Muestras", "video": "Vídeo"})
TEXT["pt"].update({"samples": "Amostras", "video": "Vídeo"})
TEXT["ru"].update({"samples": "Образцы", "video": "Видео"})
TEXT["tr"].update({"samples": "Numuneler", "video": "Video"})
TEXT["es"].update({"cap_mould": "Moldes de tapones", "machine": "Máquina", "contact_us": "Contacto"})

def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)

def text(locale: str, key: str) -> str:
    return str(TEXT.get(locale, TEXT["en"]).get(key, TEXT["en"].get(key, key)))

def data(locale: str, key: str):
    return TEXT.get(locale, TEXT["en"]).get(key, TEXT["en"].get(key, []))

def route_for(locale: str, route: str) -> str:
    prefix = next((row["pathPrefix"] for row in LOCALES if row["code"] == locale), "")
    return route if not prefix else "/" + prefix + route

def local_link(locale: str, route: str) -> str:
    return route_for(locale, route)

def localized_href(locale: str, route: str) -> str:
    return local_link(locale, route)

def catalog_text(locale: str, item: dict, key: str) -> str:
    """Return the reviewed Spanish catalogue field when one exists."""
    if locale == "es":
        translated = item.get(key + "Es")
        if isinstance(translated, str) and translated.strip():
            return translated.strip()
    return str(item.get(key) or "")

def image(path: str, alt: str, loading: str = "lazy") -> str:
    return '<img src="' + esc(path) + '" alt="' + esc(alt) + '" loading="' + loading + '" decoding="async">'

def render_template(name: str, **values: str) -> str:
    content = (ROOT / "templates/site" / (name + ".html")).read_text(encoding="utf-8").rstrip("\n")
    for key, value in values.items():
        content = content.replace("{{" + key + "}}", str(value))
    if "{{" in content:
        raise ValueError("Unfilled mould template placeholder: " + name)
    return content

TEXT["en"].update({"contact_title": "Contact LEYA MOULD", "contact_intro": "Your trusted partner for high-quality plastic cap moulds. Send your project details and we will reply promptly."})

# The samples page follows the reference site's editorial list: one product at a
# time, with its image, application notes and the mould used to make it.
SAMPLE_ITEMS = [
    {"image": "water-cap.jpg", "alt": "29/25mm water bottle cap sample", "name": "29/25mm Water Bottle Cap", "description": "This lightweight, tamper-evident cap is the industry standard for still and mineral water bottles. It features a clean break-ring for consumer safety, a smooth top surface for high-speed inkjet coding, and a reliable inner plug seal. The cap is injection molded from food-grade PP with a precise thread profile that fits all standard 29/25mm neck finishes.", "mold": "Manufactured with: 96-Cavity High-Speed Water Cap Mold (Model SH-W96)", "applications": ["Mineral water", "Flavored water", "Sparkling water", "Small PET bottles"]},
    {"image": "csd-cap.jpg", "alt": "PCO 1881 carbonated soft drink cap sample", "name": "PCO 1881 Carbonated Soft Drink Cap", "description": "Designed to safely contain pressurized beverages, this PCO 1881 cap combines a deep tamper-evident band with a triple-seal design that prevents gas escape. The cap is molded in a vibrant blue using UV-resistant pigments that will not fade. The knurled sidewall offers a secure grip, and the venting slots prevent blow-off during capping.", "mold": "Manufactured with: 72-Cavity PCO 1881 High-Pressure Cap Mold (Model SH-CSD72)", "applications": ["Cola & lemonade", "Sparkling juice", "Soda water", "Energy drinks"]},
    {"image": "hotfill-cap.jpg", "alt": "38mm hot fill cap sample", "name": "38mm Hot Fill Cap with Tapered Seal", "description": "Engineered for juices and teas filled at up to 90°C, this cap uses a thick, flexible sealing plug that compensates for vacuum build-up as the liquid cools. The tamper-evident band includes six break points that snap evenly, leaving no sharp edges. The top is recessed to accommodate a foil induction seal, and the side ribs provide a confident grip.", "mold": "Manufactured with: 48-Cavity Hot Fill Cap Mold (Model SH-HF48)", "applications": ["Fruit juices", "Iced tea", "Sports drinks", "Flavored milk"]},
    {"image": "oil-cap.jpg", "alt": "Pull-ring edible oil cap sample", "name": "Pull-Ring Edible Oil Cap with Pourer", "description": "A convenient two-piece closure combining a tamper-evident pull-ring and an integrated hinged pourer. Once the ring is removed, the pourer can be flipped open to allow smooth, drip-free dispensing. The cap body is molded in FDA-compliant PP, while the pourer hinge uses a living-hinge design tested for over 10,000 cycles.", "mold": "Manufactured with: 32-Cavity Oil Cap Mold with Integrated Pourer (Model SH-OC32)", "applications": ["Olive oil", "Sunflower oil", "Soybean oil", "Canola oil"]},
    {"image": "soysauce-cap.jpg", "alt": "Soy sauce dispensing cap sample", "name": "Dispensing Cap for Soy Sauce & Condiments", "description": "A compact flip-top cap featuring a silicone valve that opens under slight pressure and closes instantly to prevent dripping. The transparent PP body allows users to see the remaining sauce level, while the over-cap provides hygiene protection. The orifice is precisely laser-drilled for consistent flow, and the snap-fit hinge is robust enough for daily use.", "mold": "Manufactured with: 24-Cavity Condiment Dispensing Cap Mold (Model SH-CD24)", "applications": ["Soy sauce", "Vinegar", "Ketchup", "Hot sauce"]},
    {"image": "pharma-cap.jpg", "alt": "Child-resistant medical cap sample", "name": "Child-Resistant Pharma Cap with Desiccant Chamber", "description": "A dual-function closure requiring simultaneous push and turn to open, preventing accidental child access. The integrated desiccant chamber holds a silica gel canister that absorbs moisture, keeping tablets dry. The cap is molded in medical-grade PP and meets USP <671> and ISO 8317 standards.", "mold": "Manufactured with: 16-Cavity Child-Resistant Medical Cap Mold (Model SH-CR16)", "applications": ["Pharmaceutical tablets", "Vitamins & supplements", "Effervescent tubes", "Diagnostic kits"]},
    {"image": "disc-top-cap.jpg", "alt": "High-gloss disc-top cap sample", "name": "High-Gloss Disc-Top Cap for Shampoo Bottles", "description": "An elegant disc-top closure with a mirror-polished surface achieved through diamond-polished mold cavities. The actuator opens with a light press and snaps back into place silently, thanks to a spring-loaded mechanism. The cap is molded in crystal-clear PETG, offering glass-like transparency and scratch resistance.", "mold": "Manufactured with: 8-Cavity Cosmetic Disc-Top Cap Mold (Model SH-CT8)", "applications": ["Shampoo & conditioner", "Body wash", "Hand soap", "Lotions & creams"]},
    {"image": "flip-top-cap.jpg", "alt": "Living-hinge flip-top cap sample", "name": "Living-Hinge Flip-Top Cap for Household Products", "description": "A robust flip-top cap with a living hinge that has been tested to withstand more than 50,000 open-close cycles without failure. The cap features an audible snap when closed and a wide dispensing orifice for easy pouring of thick liquids. The top surface is flat and smooth, suitable for labeling or hot-foil stamping.", "mold": "Manufactured with: 32-Cavity Flip-Top Cap Mold (Model SH-FT32)", "applications": ["Hand sanitizer", "Dish soap", "Shampoo", "Liquid detergent"]},
    {"image": "tamper-evident-cap.jpg", "alt": "Tamper-evident cap sample", "name": "Break-Ring Tamper-Evident Cap for Beverage", "description": "This cap features a clearly visible break-ring that separates upon opening, providing immediate evidence of tampering. The bridges are precisely molded to ensure a uniform break force of 12-18 N·m, compliant with beverage industry standards. The cap is designed for high-speed capping lines and includes internal knurling for a secure grip during application.", "mold": "Manufactured with: 72-Cavity Tamper-Evident Cap Mold (Model SH-TE72)", "applications": ["Juice bottles", "Water bottles", "Milk bottles", "Sauce jars"]},
    {"image": "push-pull-cap.jpg", "alt": "Push-pull sports cap sample", "name": "Push-Pull Sports Cap with Dust Shield", "description": "A convenient push-pull cap that allows one-hand drinking without removing the closure. The soft PE poppet provides a smooth, quiet action, while the rigid PP base ensures a tight seal on the bottle neck. The dust cover snaps over the nozzle to keep it clean during outdoor activities.", "mold": "Manufactured with: 24-Cavity Two-Shot Sports Cap Mold (Model SH-SC24)", "applications": ["Sports water bottles", "Bike bottles", "Juice bottles", "Kids' water bottles"]},
    {"image": "pull-ring-cap.jpg", "alt": "Pull-ring cap sample", "name": "Tamper-Evident Pull-Ring Cap for Dairy", "description": "An easy-open cap that requires no tool — simply pull the ring to break the tamper band and lift the cap off. The ring is molded with a textured grip for comfortable use, and the break path is designed to leave a smooth, safe edge. The HDPE material provides toughness and a secure seal even on wide-mouth dairy bottles.", "mold": "Manufactured with: 16-Cavity Pull-Ring Cap Mold (Model SH-PR16)", "applications": ["Milk bottles", "Yogurt drinks", "Olive oil", "Jam & sauce jars"]},
    {"image": "two-shot-cap.jpg", "alt": "Two-shot overmold cap sample", "name": "Two-Shot Soft-Touch Overmold Cap", "description": "A premium cap that combines a transparent PP body with a soft TPE overmold on the grip area. The two materials are chemically bonded during the injection cycle, creating a seamless surface that is both visually striking and highly functional. The transparent core allows branding elements to show through, while the soft-touch exterior provides a luxurious feel.", "mold": "Manufactured with: 8-Cavity Bi-Injection Overmold Cap Mold (Model SH-BI8)", "applications": ["Premium cosmetics", "Luxury water bottles", "Perfume bottles", "Car care products"]},
    {"image": "wide-mouth-cap.jpg", "alt": "Wide-mouth jar cap sample", "name": "Wide-Mouth Jar Cap (110mm)", "description": "This large-diameter cap is designed for wide-mouth PET jars used for snacks, pickles, and instant food. It features a deep thread engagement that ensures an airtight seal even after repeated opening. The ribbed sidewall provides excellent grip for consumers, and the top can be hot-foil stamped for branding. Molded from clear PET or PP, the cap offers excellent clarity and chemical resistance.", "mold": "Manufactured with: 12-Cavity Wide-Mouth Cap Mold (Model SH-WM12)", "applications": ["Pickle jars", "Snack containers", "Instant food jars", "Candy & nut jars"]},
    {"image": "squeeze-sports-cap.jpg", "alt": "Squeeze-type sports cap sample", "name": "Squeeze-Type Sports Cap with Valve", "description": "Unlike standard push-pull caps, this squeeze-type sports cap dispenses liquid when the bottle is squeezed, thanks to a silicone slit valve. It automatically seals when pressure is released, preventing leaks even when the bottle is upside down. The cap is molded in two components — a rigid PP base and a soft silicone valve — assembled in-mold for a permanent bond. Ideal for cycling, running, and gym bottles.", "mold": "Manufactured with: 16-Cavity Squeeze Sports Cap Mold (Model SH-SQ16)", "applications": ["Cycling bottles", "Running flasks", "Gym water bottles", "Outdoor hydration packs"]},
    {"image": "motor-oil-cap.jpg", "alt": "Motor oil cap sample", "name": "Heavy-Duty Motor Oil Cap with Pouring Spout", "description": "Designed for automotive lubricant bottles, this cap features an integrated extendable pouring spout that allows precise filling without spillage. The cap body is molded from high-density polyethylene (HDPE) for excellent chemical resistance, while the tamper-evident band provides product security. The spout retracts neatly after use, and the dust cap keeps the opening clean. Suitable for 1-liter and 4-liter oil containers.", "mold": "Manufactured with: 24-Cavity Motor Oil Cap Mold with Spout (Model SH-MO24)", "applications": ["Engine oil bottles", "Transmission fluid containers", "Coolant bottles", "Diesel exhaust fluid (DEF) jugs"]},
    {"image": "5-gallon-cap.jpg", "alt": "5-gallon water bottle cap sample", "name": "Tamper-Evident 5-Gallon Water Bottle Cap", "description": "This heavy-gauge cap is specifically engineered for reusable 5-gallon (18.9L) polycarbonate water bottles. It features a dual tamper-evident system — an outer tear-band and an inner plug seal — ensuring water quality until first use. The cap is molded from high-strength PP with UV stabilizers to withstand repeated sanitization cycles. A flat top allows easy stacking and storage in water coolers.", "mold": "Manufactured with: 8-Cavity 5-Gallon Water Cap Mold (Model SH-5G8)", "applications": ["Water cooler bottles", "Dispenser jugs", "Beverage syrup containers", "Bulk water storage"]},
    {"image": "bottle-handle.jpg", "alt": "Oil bottle handle sample", "name": "Integrated Oil Bottle Handle (Carry Handle)", "description": "This ergonomic handle is molded as a separate part that snaps onto the neck of edible oil or chemical bottles. It provides a comfortable carrying grip, reducing the risk of slipping. The handle is injection molded from high-strength PP, with a textured finish for a secure hold. The design includes a tamper-evident break-tab that locks the handle onto the bottle during filling, preventing removal without evidence.", "mold": "Manufactured with: 32-Cavity Bottle Handle Mold (Model SH-BH32)", "applications": ["5L edible oil bottles", "Chemical jugs", "Large vinegar containers", "Laundry detergent bottles"]},
    {"image": "custom-cap.jpg", "alt": "Custom cap sample", "name": "Custom Closure — Your Design, Our Mold", "description": "This sample represents our ability to produce entirely custom caps based on unique client specifications. Whether you need a proprietary thread profile, a child-proof mechanism, a dispensing valve, or a multi-material assembly, our engineering team will design and manufacture the precise mold to bring your concept to life.", "mold": "Manufactured with: Fully Custom Mold (cavitation & features according to your design)", "applications": ["Proprietary closures", "Multi-functional caps", "Any shape or function", "Small & large volumes"]},
]

AUXILIARY_MACHINES = [
    {"image": "202105282235237950.jpg", "alt": "Automated Assembly Machine for Wine Bottle Cap", "name": "Automated Assembly Machine for Wine Bottle Cap", "description": "LEYA MOULD supplies automated cap cutting and assembly equipment for stable, repeatable post-moulding production.", "model": "machine802"},
    {"image": "202105282229313184.jpg", "alt": "Automated Assembly Machine for Wine Bottle Cap", "name": "Automated Assembly Machine for Wine Bottle Cap", "description": "A cost-effective automated assembly solution for high output. The machine can replace the manual work of several operators while keeping the process consistent.", "model": "machine801"},
    {"image": "202105282218332662.jpg", "alt": "Cap Assembling Machine", "name": "Cap Assembling Machine", "description": "Automatically inserts gaskets into bottle caps, improving work efficiency, seating accuracy, product safety and production consistency.", "model": "machine800"},
    {"image": "202105282203156019.jpg", "alt": "Cap lining machine", "name": "Cap Lining Machine", "description": "A precision-built automatic wad inserting and cap lining machine on a sturdy enclosed stainless-steel frame for reliable servicing and operation.", "model": "machine799"},
    {"image": "202105282144214354.jpg", "alt": "Cap Assembling Machine", "name": "Cap Assembling Machine", "description": "Three-part plastic sport-cap assembly equipment for bottle, gasket, pharmaceutical, food, daily chemical and oil production lines.", "model": "machine798"},
    {"image": "202105282109294423.jpg", "alt": "5 Gallon Cap Labeling Machine", "name": "5 Gallon Cap Labeling Machine", "description": "A non-spill five-gallon water-cap labeling and sealing solution for stable, clean and efficient cap production.", "model": "machine797"},
]

# The reference site separates the News archive from its two topic archives.
# Keep the catalogue static and auditable here; article pages are lightweight
# technical briefs until the corresponding approved content is entered in CMS.
NEWS_ITEMS = [
    {"slug": "case-study-cap-line-expansion-southeast-asia", "title": "Case Study: Supporting a Beverage Manufacturer's Cap Line Expansion in Southeast Asia", "date": "2026/11/20", "image": "https://www.cap-molds.com/Upload/20261121/202611210157599346.jpg", "summary": "A practical review of closure tooling, output targets and engineering support for a growing beverage line."},
    {"slug": "cap-mold-demand-growth-global-markets", "title": "Cap Mold Demand Growth in Asia-Pacific, Europe, and North America: Key Drivers and Opportunities", "date": "2026/11/19", "image": "https://www.cap-molds.com/Upload/20261120/202611200131467551.jpg", "summary": "The tooling decisions that help packaging makers respond to regional demand and shorter product cycles."},
    {"slug": "global-bottle-cap-mould-market-outlook", "title": "Global Bottle Cap Mould Market Outlook 2026-2032: Regional Demand Analysis", "date": "2026/11/18", "image": "https://www.cap-molds.com/Upload/20261120/202611200049441288.png", "summary": "A market-oriented view of high-cavity, lightweight and sustainable closure tooling requirements."},
    {"slug": "reducing-cap-weight-seal-performance", "title": "Case Study: Reducing Cap Weight Without Compromising Seal Performance", "date": "2026/11/13", "image": "https://www.cap-molds.com/Upload/20261114/202611140248174335.png", "summary": "How part design, cooling and inspection evidence work together when a closure is lightweighted."},
    {"slug": "micro-conformal-cooling-lightweight-caps", "title": "How Micro-Conformal Cooling Prevents Thin Spots and Gas Permeability", "date": "2026/11/12", "image": "https://www.cap-molds.com/Upload/20261113/202611130229253875.png", "summary": "Cooling layout and steel decisions that protect sealing surfaces in thin-wall cap production."},
    {"slug": "ultra-thin-wall-cap-molding", "title": "Ultra-Thin Wall Cap Molding: Cooling Efficiency and Warpage Control", "date": "2026/11/11", "image": "https://www.cap-molds.com/Upload/20261112/202611120102046095.jpg", "summary": "A checklist for balancing cycle time, dimensional stability and structural integrity."},
    {"slug": "cap-mold-service-life-maintenance", "title": "Case Study: Extending Cap Mold Service Life Through Structured Maintenance", "date": "2026/11/06", "image": "https://www.cap-molds.com/Upload/20261107/202611070255255345.jpg", "summary": "Maintenance evidence and replacement planning that keep high-cavity tooling production-ready."},
    {"slug": "wear-part-management-high-cavity-caps", "title": "Wear Part Management in High-Cavity Cap Molds", "date": "2026/11/05", "image": "https://www.cap-molds.com/Upload/20261106/202611060127336688.jpg", "summary": "Inspection intervals, interchangeable components and planned replacement for stable uptime."},
    {"slug": "snap-in-bushing-replacement-design", "title": "Snap-In Bushing Replacement Design: Reducing Maintenance Downtime", "date": "2026/11/04", "image": "https://www.cap-molds.com/Upload/20261105/202611050142583314.jpg", "summary": "A service-friendly component approach for faster changeovers on high-volume lines."},
    {"slug": "running-pcr-content-cap-molds", "title": "Case Study: Running PCR Content Without Seal Lip Quality Degradation", "date": "2026/10/30", "image": "https://www.cap-molds.com/Upload/20261031/202610311025284403.jpg", "summary": "Material variability, runner design and inspection controls for recycled resin programs."},
    {"slug": "larger-runners-recycled-plastics", "title": "How Larger Runners and Gates Improve Recycled Plastic Moldability", "date": "2026/10/29", "image": "https://www.cap-molds.com/Upload/20261029/202610292147119624.jpg", "summary": "Design considerations that reduce shear and improve repeatability with PCR materials."},
    {"slug": "processing-pcr-hdpe-pp-cap-molds", "title": "Processing PCR HDPE and PP in Cap Molds: Managing Variation", "date": "2026/10/28", "image": "https://www.cap-molds.com/Upload/20261028/202610282257247265.jpg", "summary": "A production brief on shrinkage variation, contamination risk and process windows."},
]

MACHINE_NEWS_ITEMS = [
    {"slug": "cooling-water-quality-cap-mold-performance", "title": "The Role of Cooling Water Quality in Cap Mold Performance and Longevity", "titleEs": "El papel de la calidad del agua de refrigeración en el rendimiento y la vida útil del molde de tapas", "date": "2026/07/09", "image": "https://www.cap-molds.com/Upload/20260709/202607092228540366.jpg", "summary": "Water treatment and circuit checks that protect cycle stability and mould life.", "summaryEs": "Tratamiento del agua y comprobaciones de los circuitos para proteger la estabilidad del ciclo y la vida útil del molde."},
    {"slug": "mold-temperature-cap-mechanical-properties", "title": "The Effect of Mold Temperature on Cap Mechanical Properties", "titleEs": "Efecto de la temperatura del molde en las propiedades mecánicas de las tapas", "date": "2026/07/08", "image": "https://www.cap-molds.com/Upload/20260708/202607081642531107.jpg", "summary": "How temperature balance affects shrinkage, stiffness and sealing performance.", "summaryEs": "Cómo el equilibrio térmico afecta la contracción, la rigidez y el rendimiento del sellado."},
    {"slug": "controlling-cap-sink-marks", "title": "Understanding and Controlling Cap Sink Marks", "titleEs": "Cómo entender y controlar las marcas de hundimiento en las tapas", "date": "2026/07/03", "image": "https://www.cap-molds.com/Upload/20260703/202607032047427871.jpg", "summary": "Root causes and practical tooling adjustments for a cleaner top surface.", "summaryEs": "Causas principales y ajustes prácticos del molde para obtener una superficie superior más limpia."},
    {"slug": "injection-speed-cap-quality-cycle-time", "title": "The Impact of Injection Speed on Cap Quality and Cycle Time", "titleEs": "Impacto de la velocidad de inyección en la calidad de las tapas y el tiempo de ciclo", "date": "2026/06/27", "image": "https://www.cap-molds.com/Upload/20260627/202606270247389305.jpg", "summary": "A process window for balancing fill consistency, weld lines and output.", "summaryEs": "Una ventana de proceso para equilibrar el llenado, las líneas de soldadura y la producción."},
    {"slug": "cap-ejection-pin-placement", "title": "The Science of Cap Ejection Pin Placement", "titleEs": "Criterios para colocar los pasadores de expulsión de las tapas", "date": "2026/06/20", "image": "/assets/mould-news-placeholder.svg", "summary": "Ejection layout decisions that avoid deformation and protect cosmetic surfaces.", "summaryEs": "Criterios de distribución que evitan deformaciones y protegen las superficies visibles."},
    {"slug": "integrated-liner-cap-solutions", "title": "Solutions for Caps with Integrated Liners", "titleEs": "Soluciones para tapas con liner integrado", "date": "2026/06/04", "image": "https://www.cap-molds.com/Upload/20260604/202606042146375936.jpg", "summary": "Combining closure geometry, liner placement and downstream assembly requirements.", "summaryEs": "Cómo coordinar la geometría del cierre, la colocación del liner y los requisitos de montaje posteriores."},
    {"slug": "preventing-cap-short-shots", "title": "Preventing Cap Short Shots: Root Cause Analysis and Solutions", "titleEs": "Cómo evitar piezas cortas en tapas: causas y soluciones", "date": "2026/05/30", "image": "https://www.cap-molds.com/Upload/20260530/202605300010394598.jpg", "summary": "A troubleshooting guide covering venting, balance, material and process settings.", "summaryEs": "Guía de diagnóstico sobre ventilación, equilibrado, material y ajustes del proceso."},
    {"slug": "multi-start-thread-cap-design", "title": "An Approach to Caps with Multi-Start Threads", "titleEs": "Criterios de diseño para tapas con roscas de varias entradas", "date": "2026/05/27", "image": "https://www.cap-molds.com/Upload/20260527/202605272130057637.jpg", "summary": "Thread-start alignment and mould details for fast, reliable capping.", "summaryEs": "Alineación de las entradas de rosca y detalles del molde para un taponado rápido y fiable."},
    {"slug": "linerless-vs-liner-based-sealing", "title": "The Science of Cap Sealing: Linerless vs. Liner-Based Designs", "titleEs": "Sellado de tapas: diseños sin liner frente a diseños con liner", "date": "2026/05/22", "image": "https://www.cap-molds.com/Upload/20260522/202605220110087521.jpg", "summary": "A comparison of sealing architectures, inspection points and tooling implications.", "summaryEs": "Comparación de arquitecturas de sellado, puntos de inspección e implicaciones para el molde."},
    {"slug": "zero-defect-cap-production-quality-system", "title": "Quality Management for Zero-Defect Cap Production", "titleEs": "Gestión de calidad para producir tapas sin defectos", "date": "2026/05/15", "image": "https://www.cap-molds.com/Upload/20260515/202605150027085266.jpg", "summary": "How documented checks connect mould trials, dimensional control and production release.", "summaryEs": "Cómo los controles documentados conectan las pruebas del molde, el control dimensional y la liberación de producción."},
    {"slug": "managing-cap-shrinkage", "title": "Managing Cap Shrinkage from Mold Design to Production", "titleEs": "Control de la contracción de las tapas desde el diseño del molde hasta la producción", "date": "2026/05/08", "image": "/assets/mould-news-placeholder.svg", "summary": "Material, cooling and measurement controls for predictable cap dimensions.", "summaryEs": "Controles de material, refrigeración y medición para obtener dimensiones previsibles."},
    {"slug": "zero-defect-cap-sealing-surfaces", "title": "Achieving Zero-Defect Cap Sealing Surfaces", "titleEs": "Cómo lograr superficies de sellado de tapas sin defectos", "date": "2026/05/01", "image": "https://www.cap-molds.com/Upload/20260501/202605010148488510.jpg", "summary": "A practical inspection sequence for threads, plugs and sealing lips.", "summaryEs": "Secuencia práctica de inspección para roscas, tapones y labios de sellado."},
]

def editorial_news_items(category: str) -> list[dict]:
    """Flatten the reviewed bilingual registry for the existing card component."""
    result = []
    for row in EDITORIAL_DATA.get("items", []):
        if not isinstance(row, dict) or row.get("category") != category:
            continue
        title = row.get("title") if isinstance(row.get("title"), dict) else {}
        description = row.get("description") if isinstance(row.get("description"), dict) else {}
        alt = row.get("alt") if isinstance(row.get("alt"), dict) else {}
        result.append({
            "slug": str(row.get("slug")), "title": str(title.get("en") or ""), "titleEs": str(title.get("es") or ""),
            "date": str(row.get("date") or "").replace("-", "/"), "image": str(row.get("cover") or "/assets/mould-news-placeholder.svg"),
            "summary": str(description.get("en") or ""), "summaryEs": str(description.get("es") or ""),
            "alt": str(alt.get("en") or title.get("en") or "LEYA MOULD technical reference"),
            "altEs": str(alt.get("es") or title.get("es") or "Referencia técnica de LEYA MOULD"),
            "editorial": row,
        })
    return result

# One canonical list in data/mould-catalog.json drives the aggregate page,
# home cards, navigation, footer and every dedicated product route.  The
# explicit order keeps the reference cap menu first, then the adjacent bottle
# and preform product families added from the HMould catalogue review.
CAP_MOULD_ORDER = [
    "mineral-water-closure-cap-molds",
    "five-gallon-water-cap-mould",
    "oil-bottle-cap-mould",
    "flip-top-caps-mould",
    "engine-oil-cap-mould",
    "food-packaging-cap-mould",
    "medical-cap-mould",
    "personal-care-cap-mould",
    "functional-cap-mould",
    "plastic-handle-cap-mould",
    "wine-cap-mould",
    "pet-preform-mould",
    "blow-bottle-mould",
]
CAP_MOULD_SERIES = sorted(CATALOG["categories"], key=lambda item: CAP_MOULD_ORDER.index(item["slug"]))

def header(locale: str, route: str) -> str:
    # Keep the desktop navigation aligned with the reference: the Cap mold
    # label opens the aggregate page, while the caret exposes all nine routes.
    product_links = ''.join('<a href="' + localized_href(locale, item["route"]) + '">' + esc(navigation_label(item["route"], catalog_text(locale, item, "navTitle") or catalog_text(locale, item, "title"))) + '</a>' for item in CAP_MOULD_SERIES)
    nav = ['<a class="nav__link" href="' + local_link(locale, "/") + '">' + esc(text(locale, "home")) + '</a>']
    about_menu = '<div class="nav__drop"><button class="nav__toggle" data-mega-toggle type="button" aria-controls="menu-about" aria-expanded="false">' + esc(text(locale, "about")) + '<svg class="chevron" viewBox="0 0 24 24" aria-hidden="true"><path d="m5 9 7 7 7-7"/></svg></button><div class="mini-menu" id="menu-about"><a href="' + localized_href(locale, "/about/") + '">About us</a><a href="' + localized_href(locale, "/faq/") + '">FAQs</a></div></div>'
    cap_nav_label = "Cap mold" if locale == "en" else text(locale, "cap_mould")
    product_menu = '<div class="nav__drop nav__drop--products"><a class="nav__link nav__link--direct" href="' + localized_href(locale, "/Plastic-cap-mold.html") + '">' + esc(cap_nav_label) + '</a><button class="nav__toggle nav__toggle--caret" data-mega-toggle type="button" aria-label="Open Cap Mould menu" aria-controls="menu-products" aria-expanded="false"><svg class="chevron" viewBox="0 0 24 24" aria-hidden="true"><path d="m5 9 7 7 7-7"/></svg></button><div class="mini-menu" id="menu-products">' + product_links + '</div></div>'
    nav.append(about_menu)
    nav.append(product_menu)
    nav.append('<a class="nav__link" href="' + localized_href(locale, "/capabilities/") + '">' + esc(text(locale, "machine")) + '</a>')
    sample_label = "Sample" if locale == "en" else text(locale, "samples")
    nav.append('<a class="nav__link" href="' + localized_href(locale, "/samples/") + '">' + esc(sample_label) + '</a>')
    resources_menu = '<div class="nav__drop nav__drop--resources"><a class="nav__link nav__link--direct" href="' + localized_href(locale, "/news/") + '">' + esc(text(locale, "news")) + '</a><button class="nav__toggle nav__toggle--caret" data-mega-toggle type="button" aria-label="Open News menu" aria-controls="menu-resources" aria-expanded="false"><svg class="chevron" viewBox="0 0 24 24" aria-hidden="true"><path d="m5 9 7 7 7-7"/></svg></button><div class="mini-menu" id="menu-resources"><a href="' + localized_href(locale, "/news/Bottle-cap-molds.html") + '">Bottle cap molds</a><a href="' + localized_href(locale, "/Bottle-Cap-Machine/Bottle-Cap-Machine.html") + '">Bottle Cap Machine</a></div></div>'
    nav.append(resources_menu)
    nav.append('<a class="nav__link" href="' + localized_href(locale, "/video/") + '">' + esc(text(locale, "video")) + '</a>')
    nav.append('<a class="nav__link" href="' + localized_href(locale, "/contact/") + '">' + esc(text(locale, "contact_us")) + '</a>')
    mobile = '<a href="' + local_link(locale, "/") + '">' + esc(text(locale, "home")) + '</a><a href="' + localized_href(locale, "/about/") + '">' + esc(text(locale, "about")) + '</a><a href="' + localized_href(locale, "/capabilities/") + '">' + esc(text(locale, "machine")) + '</a><a href="' + localized_href(locale, "/samples/") + '">' + esc(sample_label) + '</a><a href="' + localized_href(locale, "/video/") + '">' + esc(text(locale, "video")) + '</a><a href="' + localized_href(locale, "/contact/") + '">' + esc(text(locale, "contact_us")) + '</a>'
    mobile += '<details><summary>' + esc(text(locale, "cap_mould")) + '</summary>' + product_links + '</details><a href="' + localized_href(locale, "/news/") + '">' + esc(text(locale, "news")) + '</a><details><summary>' + esc(text(locale, "news")) + ' categories</summary><a href="' + localized_href(locale, "/news/Bottle-cap-molds.html") + '">Bottle cap molds</a><a href="' + localized_href(locale, "/Bottle-Cap-Machine/Bottle-Cap-Machine.html") + '">Bottle Cap Machine</a></details>'
    options = ''.join('<option value="' + esc(route_for(lang["code"], route)) + '"' + (' selected' if lang["code"] == locale else '') + '>' + esc(lang["nativeName"]) + '</option>' for lang in LOCALES)
    phone_digits = re.sub(r"[^0-9+]", "", WHATSAPP)
    logo = '<a href="' + local_link(locale, "/") + '" class="logo" aria-label="' + esc(BRAND_DISPLAY) + ' home"><img class="logo__image" src="' + esc(LOGO_SRC) + '" alt="' + esc(LOGO_ALT) + '" width="260" height="51" decoding="async"></a>'
    actions = '<div class="header__actions"><a class="nav-phone-desktop" href="tel:' + esc(phone_digits) + '"><span class="phone-text">' + esc(WHATSAPP) + '</span><span class="phone-icon-wrap"><svg class="phone-icon-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M6.62 10.79a15.05 15.05 0 006.59 6.59l2.2-2.2a1 1 0 011.01-.24 11.36 11.36 0 003.58.57 1 1 0 011 1V20a1 1 0 01-1 1A17 17 0 013 4a1 1 0 011-1h3.5a1 1 0 011 1 11.36 11.36 0 00.57 3.58 1 1 0 01-.25 1.01l-2.2 2.2z" fill="currentColor"></path></svg></span></a><select class="language-switch" data-language-switch aria-label="Choose language">' + options + '</select><button class="icon-button" id="search-toggle" aria-label="Search products" aria-expanded="false" type="button"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m16 16 5 5"/></svg></button><a class="button header__quote" href="' + localized_href(locale, "/contact/#inquiry") + '">' + esc(text(locale, "quote")) + '</a><button class="icon-button menu-button" id="mobile-menu" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-navigation"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg><span class="menu-label">Menu</span></button></div>'
    search = '<div id="search-panel" class="search-panel"><form class="shell search-panel__form" action="' + localized_href(locale, "/products/") + '" method="get"><input type="search" name="q" placeholder="Search mould category or application…" aria-label="Search mould category or application"><button class="button" type="submit">Search →</button></form></div>'
    top_left = '<div class="top-bar-left"><a href="mailto:' + esc(EMAIL) + '" class="info-item" title="Email us"><span class="info-icon">' + topbar_icon("email") + '</span><span>' + esc(EMAIL) + '</span></a><span class="info-separator"></span><a href="tel:' + esc(phone_digits) + '" class="info-item" title="Call us"><span class="info-icon">' + topbar_icon("phone") + '</span><span>' + esc(WHATSAPP) + '</span></a><span class="info-separator"></span><span class="info-item" title="Our address"><span class="info-icon">' + topbar_icon("pin") + '</span><span>' + esc(ADDRESS) + '</span></span></div>'
    top_right = '<div class="top-bar-right"><a href="' + esc(SOCIAL_URLS["tiktok"]) + '" target="_blank" rel="noopener noreferrer" class="social-link tiktok" title="TikTok" aria-label="TikTok">' + topbar_icon("tiktok") + '</a><a href="' + esc(SOCIAL_URLS["youtube"]) + '" target="_blank" rel="noopener noreferrer" class="social-link youtube" title="YouTube" aria-label="YouTube">' + topbar_icon("youtube") + '</a><a href="' + esc(SOCIAL_URLS["facebook"]) + '" target="_blank" rel="noopener noreferrer" class="social-link facebook" title="Facebook" aria-label="Facebook">' + topbar_icon("facebook") + '</a></div>'
    top = '<div class="topbar top-bar" id="topBar"><div class="shell topbar__inner top-bar-inner">' + top_left + top_right + '</div></div>'
    return render_template("header", TOPBAR=top, LOGO=logo, NAV_DESKTOP=''.join(nav), ACTIONS=actions, SEARCH=search, NAV_MOBILE=mobile)

def footer(locale: str) -> str:
    links = ''.join('<p><a href="' + localized_href(locale, item["route"]) + '">' + esc(navigation_label(item["route"], catalog_text(locale, item, "title"))) + '</a></p>' for item in CAP_MOULD_SERIES)
    quick = ''.join('<p><a href="' + localized_href(locale, route) + '">' + esc(label) + '</a></p>' for label, route in ((text(locale, "about"), "/about/"), (text(locale, "samples"), "/samples/"), (text(locale, "video"), "/video/"), (text(locale, "news"), "/news/"), (text(locale, "faq_title"), "/faq/"), (text(locale, "contact_us"), "/contact/")))
    footer_config = BRAND_CONFIG.get("footer", {}) if isinstance(BRAND_CONFIG, dict) else {}
    vals = {"PRODUCT_LINKS": links, "QUICK_LINKS": quick, "WHATSAPP_NUMBER": esc(WHATSAPP), "FOOTER_EYEBROW": esc(text(locale, "footer_eyebrow")), "FOOTER_CTA_TITLE": esc(text(locale, "footer_cta_title")), "FOOTER_CTA_TEXT": esc(text(locale, "footer_cta_text")), "FOOTER_CTA_BUTTON": esc(text(locale, "quote")), "FOOTER_TAGLINE": esc(footer_config.get("about") or text(locale, "footer_tagline")), "FOOTER_ADDRESS": esc(ADDRESS), "FOOTER_PRODUCTS_TITLE": esc(text(locale, "footer_products")), "FOOTER_CONTACT_TITLE": esc(footer_config.get("contactHeading") or text(locale, "footer_contact")), "FOOTER_QUOTE": esc(text(locale, "footer_quote")), "FOOTER_PRIVACY": esc(text(locale, "footer_privacy")), "FOOTER_STICKY": esc(text(locale, "footer_sticky"))}
    return render_template("footer", **vals)

def _absolute_social_image(route: str) -> str:
    detail = re.fullmatch(r"/(?:news|Bottle-Cap-Machine)/([a-z0-9-]+)\.html", str(route or ""))
    if detail and detail.group(1) in EDITORIAL_BY_SLUG:
        cover = str(EDITORIAL_BY_SLUG[detail.group(1)].get("cover") or "")
        if cover.startswith("/"):
            return ORIGIN + cover
    row = page_override_for("en", route)
    candidate = str(row.get("ogImage") or row.get("og_image") or "").strip()
    if candidate.startswith("https://"):
        return candidate
    if candidate.startswith("/"):
        return ORIGIN + candidate
    # A stable, compressed LEYA-specific image is preferable to a remote
    # reference-site asset and is available on every generated locale route.
    return ORIGIN + "/assets/about/about-hero-generated.webp"


def _json_ld(locale: str, title: str, description: str, route: str, canonical: str, image_url: str) -> str:
    organization_id = ORIGIN + "/#organization"
    graph = [
        {
            "@type": "Organization",
            "@id": organization_id,
            "name": BRAND_LEGAL,
            "alternateName": BRAND_DISPLAY,
            "url": ORIGIN + "/",
            "email": EMAIL,
            "telephone": WHATSAPP,
            "logo": {"@type": "ImageObject", "url": ORIGIN + LOGO_SRC.split("?", 1)[0]},
            "address": {
                "@type": "PostalAddress",
                "streetAddress": ADDRESS,
                "addressLocality": "Taizhou",
                "addressRegion": "Zhejiang",
                "addressCountry": "CN",
            },
        },
        {
            "@type": "WebSite",
            "@id": ORIGIN + "/#website",
            "url": ORIGIN + "/",
            "name": BRAND_DISPLAY,
            "publisher": {"@id": organization_id},
            "inLanguage": locale,
        },
    ]
    detail = re.fullmatch(r"/(?:news|Bottle-Cap-Machine)/([a-z0-9-]+)\.html", str(route or ""))
    page_type = "Article" if detail and detail.group(1) in EDITORIAL_BY_SLUG else ("CollectionPage" if route in {"/products/", "/Plastic-cap-mold.html", "/news/", "/video/"} else "WebPage")
    page = {
        "@type": page_type,
        "@id": canonical + "#webpage",
        "url": canonical,
        "name": title,
        "description": description,
        "inLanguage": locale,
        "isPartOf": {"@id": ORIGIN + "/#website"},
        "about": {"@id": organization_id},
        "primaryImageOfPage": {"@type": "ImageObject", "url": image_url},
    }
    if route.startswith("/product/"):
        page["mainEntity"] = {
            "@type": "Product",
            "name": title,
            "description": description,
            "image": [image_url],
            "brand": {"@type": "Brand", "name": BRAND_DISPLAY},
            "category": "Plastic mould tooling",
        }
    elif detail and detail.group(1) in EDITORIAL_BY_SLUG:
        editorial = EDITORIAL_BY_SLUG[detail.group(1)]
        page["author"] = {"@type": "Organization", "name": BRAND_DISPLAY}
        page["datePublished"] = str(editorial.get("date") or "").replace("/", "-")
        page["dateModified"] = editorial.get("lastReviewed")
        page["headline"] = title
        page["image"] = [image_url]
    graph.append(page)
    crumbs = [{"@type": "ListItem", "position": 1, "name": "Home", "item": ORIGIN + route_for(locale, "/")}]
    if route != "/":
        crumbs.append({"@type": "ListItem", "position": 2, "name": title, "item": canonical})
        graph.append({"@type": "BreadcrumbList", "@id": canonical + "#breadcrumb", "itemListElement": crumbs})
    payload = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    return payload.replace("</", "<\\/")


def head(locale: str, title: str, description: str, route: str) -> str:
    robots = effective_robots(route)
    canonical = ORIGIN + route_for(locale, route)
    alternates = ''.join('<link rel="alternate" hreflang="' + esc(lang["code"]) + '" href="' + esc(ORIGIN + route_for(lang["code"], route)) + '">' for lang in LOCALES)
    default_locale = next((lang for lang in LOCALES if lang["code"] == CONFIG["site"].get("defaultLocale", "en")), LOCALES[0])
    alternates += '<link rel="alternate" hreflang="x-default" href="' + esc(ORIGIN + route_for(default_locale["code"], route)) + '">'
    image_url = _absolute_social_image(route)
    structured_data = _json_ld(locale, title, description, route, canonical, image_url)
    # Bump the asset version whenever shared header/topbar CSS changes so live
    # browsers do not keep an older cached stylesheet during visual acceptance.
    base = render_template("head", TITLE=esc(title), DESCRIPTION=esc(description)[:240], ASSET_VERSION="mould-v49")
    if route.startswith("/product/"):
        base = base.replace('</head>', '<link rel="stylesheet" href="/assets/mould-category.css?v=mould-detail-7"></head>', 1)
    seo = ('<link rel="canonical" href="' + esc(canonical) + '">' + alternates +
           '<meta property="og:type" content="website"><meta property="og:url" content="' + esc(canonical) + '">' +
           '<meta property="og:title" content="' + esc(title) + '"><meta property="og:description" content="' + esc(description) + '">' +
           '<meta property="og:image" content="' + esc(image_url) + '"><meta property="og:image:alt" content="' + esc(BRAND_DISPLAY) + '">' +
           '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="' + esc(title) + '">' +
           '<meta name="twitter:description" content="' + esc(description) + '"><meta name="twitter:image" content="' + esc(image_url) + '">' +
           '<script type="application/ld+json">' + structured_data + '</script>')
    base = base.replace('<html lang="en">', '<html lang="' + esc(locale) + '">', 1).replace('noindex,nofollow', robots, 1)
    return base.replace('</head>', seo + '</head>', 1)

def rail(locale: str) -> str:
    phone_digits = re.sub(r"[^0-9+]", "", WHATSAPP)
    phone = '<a href="tel:' + esc(phone_digits) + '" class="rail-float rail-float--phone" title="Call us" aria-label="Call us"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7.1 4.5 9.7 4c.5-.1 1 .2 1.2.7l1.2 2.8c.2.4.1.9-.2 1.2l-1.4 1.4a13.4 13.4 0 0 0 3.4 3.4l1.4-1.4c.3-.3.8-.4 1.2-.2l2.8 1.2c.5.2.8.7.7 1.2l-.5 2.6c-.1.5-.5.8-1 .8C11.8 17.7 6.3 12.2 6.3 5.5c0-.5.3-.9.8-1Z"/></svg><span class="floating-tooltip">Call</span></a>'
    whatsapp = '<a href="' + WA_URL + '" target="_blank" rel="noopener noreferrer" class="rail-float rail-float--whatsapp" title="Chat on WhatsApp" aria-label="Chat on WhatsApp"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.5 11.2a8.4 8.4 0 0 1-12.4 7.4L4 20l1.4-4A8.4 8.4 0 1 1 20.5 11.2Z"/><path d="M9.2 8.8c.2-.4.4-.4.7-.4h.5c.2 0 .4.1.5.4l.6 1.4c.1.2.1.4-.1.6l-.5.6c.6 1.1 1.5 2 2.6 2.6l.6-.5c.2-.2.4-.2.6-.1l1.4.6c.3.1.4.3.4.5v.5c0 .3 0 .5-.4.7-.5.3-1.1.4-1.7.2-2.1-.6-4.7-3.2-5.3-5.3-.2-.6-.1-1.2.1-1.8Z"/></svg><span class="floating-tooltip">WhatsApp</span></a>'
    wechat = '<a href="' + localized_href(locale, "/contact/") + '" class="rail-float rail-float--wechat" title="WeChat contact" aria-label="WeChat contact"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10.5 6.3C6.9 6.3 4 8.5 4 11.2c0 1.6 1 3 2.5 3.9L6 17l2.2-1.1c.7.2 1.5.3 2.3.3 3.6 0 6.5-2.2 6.5-4.9S14.1 6.3 10.5 6.3Z"/><path d="M14.2 10.1c3.2 0 5.8 1.9 5.8 4.4 0 1.3-.7 2.5-1.9 3.3l.4 1.5-1.8-.9c-.6.2-1.3.3-2 .3-3.2 0-5.8-1.8-5.8-4.2"/></svg><span class="floating-tooltip">WeChat</span></a>'
    return '<aside class="rail" role="complementary" aria-label="Quick contact">' + phone + whatsapp + wechat + '</aside>'

def shell(locale: str, title: str, description: str, route: str, body: str) -> str:
    return render_template("shell", HEAD=head(locale, title, description, route), HEADER=header(locale, route), SIDEBAR=rail(locale), BODY=body, FOOTER=footer(locale))

def intro(locale: str, title: str, subtitle: str, route: str) -> str:
    banner_map = {
        "/about/": "/upload/Banner/pheader-About.jpg",
        "/products/": "/upload/Banner/Plastic-flip-top-mold.jpg",
        "/capabilities/": "/upload/Banner/machine.jpg",
        "/samples/": "/upload/Banner/Cap-Samples.jpg",
        "/news/": "/upload/Banner/pheader-news.jpg",
        "/video/": "/upload/Banner/pheader-news.jpg",
        "/contact/": "/upload/Banner/pheader-contact.jpg",
        "/faq/": "/upload/Banner/pheader-faq.jpg",
    }
    banner = banner_map.get(route, "/upload/Banner/Plastic-flip-top-mold.jpg")
    if route.startswith("/news/") or route.startswith("/Bottle-Cap-Machine/"):
        banner = "/upload/Banner/pheader-news.jpg"
    banner_mod = " reference-banner--contact" if route == "/contact/" else (" reference-banner--compact" if route in {"/capabilities/", "/news/", "/video/", "/faq/"} or route.startswith("/news/") or route.startswith("/Bottle-Cap-Machine/") else "")
    cap = "https://www.cap-molds.com"
    banner_src = banner if banner.startswith("/assets/") else cap + banner
    page_header_mod = " reference-page-header--samples" if route == "/samples/" else ""
    if route == "/capabilities/":
        page_eyebrow = "AUXILIARY EQUIPMENT"
        page_title = "Cap <span class=\"reference-title-accent\">Auxiliary Machines</span>"
    elif route == "/video/":
        page_eyebrow = "EXPLORE OUR WORK"
        page_title = "Video <span class=\"reference-title-accent\">Gallery</span>" if locale == "en" else "Galería de <span class=\"reference-title-accent\">vídeos</span>"
    elif route == "/about/":
        page_eyebrow = "OUR STORY" if locale == "en" else "NUESTRA HISTORIA"
        page_title = ("About <span class=\"reference-title-accent\">LEYA MOULD</span>" if locale == "en" else "Sobre <span class=\"reference-title-accent\">LEYA MOULD</span>")
    else:
        page_eyebrow = "LEYA MOULD · PRECISION TOOLING"
        page_title = esc(title)
    if route == "/contact/":
        crumb = '<nav class="reference-breadcrumb reference-breadcrumb--overlay" aria-label="Breadcrumb"><div class="shell"><a href="' + local_link(locale, "/") + '">' + esc(text(locale, "home")) + '</a><span>›</span><span>' + esc(title) + '</span></div></nav>'
        return '<section class="reference-banner' + banner_mod + '"><img src="' + esc(banner_src) + '" alt="LEYA MOULD reference banner" loading="eager" decoding="async">' + crumb + '</section><header class="reference-page-header"><span class="eyebrow">' + page_eyebrow + '</span><h1>' + page_title + '</h1><p>' + esc(subtitle) + '</p></header>'
    return '<section class="reference-banner' + banner_mod + '"><img src="' + esc(banner_src) + '" alt="LEYA MOULD reference banner" loading="eager" decoding="async"></section><nav class="reference-breadcrumb" aria-label="Breadcrumb"><div class="shell"><a href="' + local_link(locale, "/") + '">' + esc(text(locale, "home")) + '</a><span>›</span><span>' + esc(title) + '</span></div></nav><header class="reference-page-header' + page_header_mod + '"><span class="eyebrow">' + page_eyebrow + '</span><h1>' + page_title + '</h1><p>' + esc(subtitle) + '</p></header>'
def section_heading(locale: str, eyebrow: str, title: str, description: str = "") -> str:
    return '<div class="section__head"><div><span class="eyebrow">' + esc(eyebrow) + '</span><h2 class="section__title">' + esc(title) + '</h2>' + (('<p class="copy-muted">' + esc(description) + '</p>') if description else '') + '</div></div>'

def cap_series_card(locale: str, item: dict) -> str:
    href = localized_href(locale, item["route"])
    title = catalog_text(locale, item, "title")
    description = catalog_text(locale, item, "description")
    meta = catalog_text(locale, item, "meta")
    return '<a class="cap-series-card" href="' + href + '"><div class="cap-series-card__image">' + image(item["image"], title + " reference image") + '</div><div class="cap-series-card__body"><h3>' + esc(title) + '</h3><p>' + esc(description) + '</p><div class="cap-series-card__meta"><span>' + esc(meta) + '</span><strong>' + esc(text(locale, "view")) + '</strong></div></div></a>'

def home(locale: str) -> str:
    cap = "https://www.cap-molds.com"
    managed_banners = effective_banners(locale)
    first_banner = managed_banners[0] if managed_banners else {
        "img": cap + "/upload/Banner/Plastic-flip-top-mold.jpg",
        "link": localized_href(locale, "/products/"),
        "title": "Your Trusted", "highlight": "Plastic Cap Mould",
        "description": text(locale, "hero_text"), "alt": "LEYA MOULD precision machining reference",
        "cta": text(locale, "hero_primary")
    }
    hero_img = first_banner["img"]
    steel_img = cap + "/upload/Home/steel-quality.jpg"
    samples = ["water-cap", "csd-cap", "hotfill-cap", "oil-cap", "soysauce-cap", "pharma-cap", "disc-top-cap", "flip-top-cap", "tamper-evident-cap", "push-pull-cap", "pull-ring-cap", "two-shot-cap", "custom-cap", "wide-mouth-cap", "squeeze-sports-cap", "motor-oil-cap", "5-gallon-cap", "bottle-handle"]
    hero_tail = "" if managed_banners else " Manufacturer"
    hero = '<section class="hero hero-slider" data-hero tabindex="0" aria-label="' + esc(BRAND_DISPLAY) + '"><div class="hero__backdrop"></div><div class="hero__inner shell"><div class="hero__copy"><span class="eyebrow">' + esc(text(locale, "hero_eyebrow")) + '</span><h1 id="hero-title">' + esc(first_banner["title"]) + ' <span>' + esc(first_banner["highlight"]) + '</span>' + esc(hero_tail) + '</h1><p id="hero-description">' + esc(first_banner["description"]) + '</p><div class="actions"><a id="hero-cta" class="button button--round" href="' + esc(first_banner["link"]) + '">' + esc(first_banner["cta"]) + '</a><a class="button button--outline button--round" href="' + localized_href(locale, "/contact/#inquiry") + '">' + esc(text(locale, "hero_secondary")) + '</a></div><p class="hero__note">' + esc(text(locale, "hero_note")) + '</p></div><div class="hero__art"><a class="hero__art-link" href="' + esc(first_banner["link"]) + '" aria-label="' + esc(first_banner["alt"]) + '"><img id="hero-image" src="' + esc(hero_img) + '" alt="' + esc(first_banner["alt"]) + '" loading="eager" decoding="async"></a></div></div><button class="hero__arrow hero__arrow--prev" type="button" data-hero-nav="-1" aria-label="Previous slide">‹</button><button class="hero__arrow hero__arrow--next" type="button" data-hero-nav="1" aria-label="Next slide">›</button><div class="hero__controls"><button class="hero__dot active" data-hero-go="0" aria-pressed="true" type="button">01</button><button class="hero__dot" data-hero-go="1" aria-pressed="false" type="button">02</button><button class="hero__dot" data-hero-go="2" aria-pressed="false" type="button">03</button><span id="hero-status" class="sr-only" aria-live="polite">Slide 1 of 3</span></div></section>'
    if managed_banners:
        managed_json = json.dumps(managed_banners, ensure_ascii=False).replace("</", "<\\/")
        hero += '<script type="application/json" id="xuyi-home-banners">' + managed_json + '</script>'
    advantages = ''.join('<article class="advantage-card"><span class="advantage-card__number">0' + str(i + 1) + '</span><h3>' + esc(title) + '</h3><p>' + esc(desc) + '</p></article>' for i, (title, desc) in enumerate(data(locale, "advantages")))
    advantages_section = '<section class="section section--advantages"><div class="shell">' + section_heading(locale, "WHY CHOOSE US", "Core Advantages of LEYA MOULD", "From mould design to trial delivery, we deliver value through engineering excellence and strict quality control.") + '<div class="advantage-grid">' + advantages + '</div></div></section>'
    catalog_count = len(CAP_MOULD_SERIES)
    cap_products = '<section class="section cap-series-section"><div class="shell">' + section_heading(locale, "OUR PRODUCTS", "Mould Product Families", "Explore " + str(catalog_count) + " specialized mould product families engineered for high-volume production, dimensional accuracy and long service life.") + '<div class="cap-series-grid">' + ''.join(cap_series_card(locale, item) for item in CAP_MOULD_SERIES) + '</div></div></section>'
    sample_cards = ''.join('<a class="sample-card" href="' + localized_href(locale, "/samples/") + '"><img src="' + cap + '/images/samples/' + s + '.jpg" alt="' + esc(s.replace("-", " ").title() + " reference sample") + '" loading="lazy" decoding="async"><span>' + esc(s.replace("-", " ").title()) + '</span></a>' for s in samples)
    samples_section = '<section class="section samples-section"><div class="shell">' + section_heading(locale, "SAMPLES GALLERY", "Plastic Cap Samples", "A wide variety of cap samples for beverage, food, pharma, personal-care and industrial closures. Use the arrows to browse the collection.") + '<div class="samples-track-wrap"><button class="samples-scroll samples-scroll--prev" type="button" data-samples-scroll="-1" aria-label="Previous samples">‹</button><div class="samples-track" data-samples-track>' + sample_cards + '</div><button class="samples-scroll samples-scroll--next" type="button" data-samples-scroll="1" aria-label="Next samples">›</button></div><div class="section__more"><a class="text-link" href="' + localized_href(locale, "/samples/") + '">' + esc(text(locale, "samples")) + ' →</a></div></div></section>'
    technology = '<section class="section technology-section"><div class="shell"><div class="section__head tech-section-head"><div><span class="eyebrow">OUR TECHNOLOGY</span><h2 class="section__title">Engineering Excellence Behind Every Mould</h2><div class="section-line"></div></div></div><div class="tech-grid"><div class="tech-img">' + image(cap + "/upload/Home/precision-machining.jpg", "5-axis CNC machining", "lazy") + '</div><div class="tech-text"><h3>Precision Manufacturing &amp; Strict QC</h3><p>5-axis CNC and EDM achieve ±0.005mm tolerances. Every mould undergoes CMM inspection, trial runs, and leak tests with documented reports.</p><ul class="tech-list"><li>Moldflow simulation before manufacturing</li><li>100% CMM inspection per cavity</li></ul></div></div><div class="tech-grid tech-grid--second"><div class="tech-text"><h3>Premium Steel &amp; Modular Design</h3><p>ASSAB S136, NAK80, H13 steels with vacuum heat treatment (HRC 48–52). Modular inserts enable fast cavity expansion and quick product changeovers.</p><ul class="tech-list"><li>Full material traceability with mill certificates</li><li>Standard delivery in 30–45 days</li></ul></div><div class="tech-img">' + image(cap + "/upload/Home/steel-quality.jpg", "Premium mould steel", "lazy") + '</div></div></div></section>'
    steps = ''.join('<article class="process-step"><div class="step-num">' + esc(num.lstrip("0") or "0") + '</div><h4>' + esc(title) + '</h4><p>' + esc(desc.replace(" →", "")) + '</p></article>' for num, title, desc in data(locale, "process_steps"))
    process = '<section class="section workflow-section"><div class="shell">' + section_heading(locale, "HOW WE WORK", "Your Cap Mould Journey", "From your first drawing to delivery and technical support.") + '<div class="steps">' + steps + '</div></div></section>'
    testimonials = '<section class="section testimonial-section"><div class="shell">' + section_heading(locale, "TESTIMONIALS", "Trusted by Packaging Leaders Worldwide", "Hear what our global customers say about the quality, precision, and reliability of LEYA MOULD cap moulds.") + '<div class="testimonial-grid"><article class="testimonial-card"><p>“LEYA MOULD\'s water cap mould has been running over 3 million shots with zero defects.”</p><div><img src="https://flagcdn.com/w40/in.png" alt="India reference"><span>Production Head · India</span></div></article><article class="testimonial-card"><p>“From DFM to delivery, consistent quality and on-time support.”</p><div><img src="https://flagcdn.com/w40/br.png" alt="Brazil reference"><span>Technical Manager · Brazil</span></div></article><article class="testimonial-card"><p>“The tooling is robust, maintainable and ready for repeatable production.”</p><div><img src="https://flagcdn.com/w40/de.png" alt="Germany reference"><span>Plant Director · Germany</span></div></article></div></div></section>'
    references = '<section class="section reference-section"><div class="shell">' + section_heading(locale, "ENGINEERING REFERENCE", "Built for repeatable production decisions.", "Mould structure, steel selection, inspection evidence and trial feedback stay connected through the project.") + '<div class="reference-grid"><article><span>01</span><h3>Precision manufacturing</h3><p>Machining, EDM, fitting and assembly follow the approved tooling brief.</p></article><article><span>02</span><h3>Premium steel & modular design</h3><p>Material traceability and modular inserts keep future changes practical.</p></article><article><span>03</span><h3>Trial & inspection</h3><p>Sample results, dimensional checks and agreed revisions guide handover.</p></article></div></div></section>'
    resources = '<section class="section section--soft resource-section"><div class="shell">' + section_heading(locale, "NEWS & INSIGHTS", "Latest from LEYA MOULD", "Project notes, tooling updates and practical engineering guidance.") + '<div class="resource-grid"><a class="resource-card" href="' + localized_href(locale, "/news/") + '"><span class="eyebrow">NEWS</span><h3>Cap mould project notes</h3><p>Follow new category material, sample references and production lessons.</p><span class="text-link">Read updates →</span></a><a class="resource-card" href="' + localized_href(locale, "/news/") + '"><span class="eyebrow">ENGINEERING</span><h3>Lightweight closure design</h3><p>Review the design questions that influence sealing, cooling and cycle goals.</p><span class="text-link">Read updates →</span></a><a class="resource-card" href="' + localized_href(locale, "/news/") + '"><span class="eyebrow">QUALITY</span><h3>Inspection evidence</h3><p>Keep dimensions, trial results and approved revisions connected.</p><span class="text-link">Read updates →</span></a><a class="resource-card" href="' + localized_href(locale, "/faq/") + '"><span class="eyebrow">FAQ</span><h3>Prepare a useful tooling enquiry</h3><p>See the drawing, resin, machine and sample information that helps a quotation move faster.</p><span class="text-link">View FAQs →</span></a><a class="resource-card" href="' + localized_href(locale, "/video/") + '"><span class="eyebrow">VIDEO</span><h3>Mould trial and review</h3><p>Use the video area for future machine, trial and inspection media.</p><span class="text-link">View video →</span></a><a class="resource-card" href="' + localized_href(locale, "/contact/#inquiry") + '"><span class="eyebrow">CONTACT</span><h3>Send your project brief</h3><p>Tell LEYA MOULD what you are making and where the tooling must run.</p><span class="text-link">Start a conversation →</span></a></div></div></section>'
    return hero + advantages_section + cap_products + samples_section + technology + testimonials + process + resources

def catalog_support_sections(locale: str) -> str:
    """Render the supporting modules that exist on the reference catalogue page.

    The catalogue route used to stop after the product cards and video strip.
    Keep these modules in one renderer so the aggregate page stays complete,
    while the individual routes and the shared shell remain untouched.
    """
    cap = "https://www.cap-molds.com"
    es = locale == "es"
    advantages_title = "Ventajas clave de LEYA MOULD" if es else "Core Advantages of LEYA MOULD"
    advantages_desc = "Desde el diseño del molde hasta la prueba, entregamos valor con excelencia de ingeniería y control de calidad estricto." if es else "From mould design to trial delivery, we deliver value through engineering excellence and strict quality control."
    samples_title = "Muestras de tapas de plástico" if es else "Plastic Cap Samples"
    samples_desc = "Una amplia variedad de muestras para bebidas, alimentos, farmacia, cuidado personal y cierres industriales. Use las flechas para explorar la colección." if es else "A wide variety of cap samples for beverage, food, pharma, personal-care and industrial closures. Use the arrows to browse the collection."
    technology_title = "Excelencia de ingeniería detrás de cada molde" if es else "Engineering Excellence Behind Every Mould"
    technology_desc = "Fabricación de precisión, acero premium y controles documentados para una producción repetible." if es else "Precision manufacturing, premium steel and documented controls for repeatable production."
    quality_title = "Control de calidad e inspección" if es else "Quality Control & Inspection"
    quality_desc = "Cada molde se revisa antes, durante y después de la prueba para que la entrega sea verificable." if es else "Every mould is reviewed before, during and after trial so the handover is measurable and traceable."
    workflow_title = "Su recorrido de molde" if es else "Your Cap Mould Journey"
    workflow_desc = "Desde su primer plano hasta la entrega y el soporte técnico." if es else "From your first drawing to delivery and technical support."
    faq_title = "Preguntas frecuentes" if es else "Common Questions"
    faq_desc = "Respuestas rápidas sobre diseño, pruebas, plazos y soporte." if es else "Quick answers about design, trials, lead times and support."
    testimonial_title = "Opiniones de clientes" if es else "Client Feedback"
    testimonial_desc = "Lo que compradores de packaging valoran en la calidad, precisión y soporte de LEYA MOULD." if es else "What packaging buyers value in LEYA MOULD quality, precision and support."

    advantage_items = [
        ("Premium Steel", "ASSAB, DAIDO certified steel for millions of cycles."),
        ("Micron Precision", "±0.01mm tolerances with high-speed CNC and EDM."),
        ("Fast Cycles", "Conformal cooling reduces cycle time, boosting output."),
        ("Custom Solutions", "Tailored designs from simple caps to complex combinations."),
        ("Lifetime Support", "Remote guidance, maintenance tips, and spare parts service."),
        ("On-Time Delivery", "Efficient project management to meet your deadlines."),
    ]
    if es:
        advantage_items = [
            ("Acero premium", "Acero certificado ASSAB y DAIDO para millones de ciclos."),
            ("Precisión micrométrica", "Tolerancias de ±0,01 mm con CNC y EDM de alta velocidad."),
            ("Ciclos rápidos", "La refrigeración conformada reduce el ciclo y aumenta la producción."),
            ("Soluciones a medida", "Diseños adaptados desde tapas simples hasta combinaciones complejas."),
            ("Soporte continuo", "Guía remota, mantenimiento y servicio de repuestos."),
            ("Entrega a tiempo", "Gestión eficiente para cumplir sus fechas objetivo."),
        ]
    advantages = ''.join('<article class="advantage-card"><span class="advantage-card__number">0' + str(i + 1) + '</span><h3>' + esc(title) + '</h3><p>' + esc(desc) + '</p></article>' for i, (title, desc) in enumerate(advantage_items))
    advantages_section = '<section id="catalog-advantages" class="section section--advantages"><div class="shell">' + section_heading(locale, "WHY CHOOSE US" if not es else "POR QUÉ ELEGIRNOS", advantages_title, advantages_desc) + '<div class="advantage-grid catalog-advantage-grid">' + advantages + '</div></div></section>'

    # Match the source gallery: 21 images, a clean grid and a click-to-enlarge
    # lightbox. These are the same compressed public sample assets used by the
    # reference page, so no placeholder cards are silently introduced.
    sample_cards = ''.join('<button class="catalog-sample-item" type="button" data-sample-img="' + cap + '/upload/caps/Bottle-cap-sample' + str(i).zfill(2) + '.jpg" aria-label="' + esc(("Ampliar muestra de tapa " if es else "Enlarge bottle cap sample ") + str(i)) + '"><img src="' + cap + '/upload/caps/Bottle-cap-sample' + str(i).zfill(2) + '.jpg" alt="' + esc(("Muestra de tapa " if es else "Bottle cap sample ") + str(i)) + '" loading="lazy" decoding="async"></button>' for i in range(1, 22))
    samples_section = '<section id="catalog-samples" class="section samples-section"><div class="shell">' + section_heading(locale, "CAP SAMPLES" if not es else "MUESTRAS DE TAPAS", "Bottle Cap Sample Gallery" if not es else "Galería de muestras de tapas", "Click on any image to enlarge. All samples are produced from our moulds and represent the quality you can expect for your own production." if not es else "Haga clic en cualquier imagen para ampliarla. Todas las muestras se producen con nuestros moldes y representan la calidad que puede esperar.") + '<div class="catalog-sample-grid" id="catalogSampleGrid">' + sample_cards + '</div></div></section><div class="catalog-lightbox" id="catalogLightbox" aria-hidden="true"><button type="button" class="catalog-lightbox__close" data-sample-close aria-label="Close sample">×</button><img id="catalogLightboxImg" src="" alt=""></div><script>(()=>{const grid=document.getElementById("catalogSampleGrid"),box=document.getElementById("catalogLightbox"),img=document.getElementById("catalogLightboxImg");if(!grid||!box||!img)return;const close=()=>{box.classList.remove("is-open");box.setAttribute("aria-hidden","true");img.src=""};grid.addEventListener("click",e=>{const b=e.target.closest("[data-sample-img]");if(!b)return;img.src=b.dataset.sampleImg;box.classList.add("is-open");box.setAttribute("aria-hidden","false")});box.addEventListener("click",e=>{if(e.target===box||e.target.closest("[data-sample-close]"))close()});document.addEventListener("keydown",e=>{if(e.key==="Escape")close()})})();</script>'

    technical_items = [
        ("3D Design & Simulation", "Advanced CAD/CAE for optimal gate location and cooling layout."),
        ("Precision Machining", "High-speed CNC, wire EDM, and jig grinding for micron accuracy."),
        ("Heat Treatment", "Vacuum heat treatment ensures uniform hardness and stability."),
        ("Conformal Cooling", "3D-printed inserts reduce cycle time by up to 30%."),
        ("Automated Polishing", "Robotic cells deliver mirror finishes for perfect part release."),
        ("Material Expertise", "Optimized for PP, HDPE, LDPE, PET, and specialty polymers."),
    ]
    if es:
        technical_items = [
            ("Diseño 3D y simulación", "CAD/CAE avanzado para optimizar la entrada y la refrigeración."),
            ("Mecanizado de precisión", "CNC de alta velocidad, EDM de hilo y rectificado para precisión micrométrica."),
            ("Tratamiento térmico", "El tratamiento al vacío garantiza dureza uniforme y estabilidad."),
            ("Refrigeración conformada", "Insertos impresos en 3D reducen el ciclo hasta un 30 %."),
            ("Pulido automatizado", "Celdas robotizadas entregan acabados espejo para una expulsión perfecta."),
            ("Experiencia en materiales", "Optimizado para PP, HDPE, LDPE, PET y polímeros especiales."),
        ]
    tech_cards = ''.join('<article class="tech-card"><div class="tech-icon">' + str(i + 1).zfill(2) + '</div><div><h4>' + esc(title) + '</h4><p>' + esc(desc) + '</p></div></article>' for i, (title, desc) in enumerate(technical_items))
    technology = '<section id="catalog-technology" class="technical-section"><div class="shell"><div class="section-header"><div class="section-tag">' + ("TECNOLOGÍA" if es else "TECHNOLOGY") + '</div><h2 class="section-title">' + esc("Fortaleza técnica y proceso" if es else "Technical Strength & Process") + '</h2><p class="section-sub">' + esc("Desde la simulación inicial del flujo 3D hasta el pulido automatizado final, nuestra fabricación integrada garantiza calidad constante y plazos más cortos." if es else "From initial 3D mould flow simulation to final automated polishing, our vertically integrated manufacturing ensures consistent quality and shorter lead times.") + '</p><div class="section-line"></div></div><div class="tech-grid">' + tech_cards + '</div></div></section>'

    quality_items = [
        ("01", "Steel inspection", "Material certificates and heat-treatment records are checked before machining."),
        ("02", "In-process measurement", "Critical dimensions, cooling circuits and fitting points are measured during production."),
        ("03", "Pre-shipment trial", "Trial parts, cycle notes and agreed inspection points are reviewed before handover."),
        ("04", "Documented support", "Drawings, reports and approved revisions stay attached to the project for future service."),
    ]
    if es:
        quality_items = [("01", "Inspección del acero", "Análisis de espectrómetro para cada lote."), ("02", "Medición en proceso", "CMM y escaneo láser durante el mecanizado."), ("03", "Prueba previa al envío", "Prueba completa con informe de inspección."), ("04", "Certificación ISO 9001", "Sistema de gestión de calidad implantado.")]
    quality_cards = ''.join('<article class="quality-item"><div class="quality-icon">' + num + '</div><h4>' + esc(title) + '</h4><p>' + esc(desc) + '</p></article>' for num, title, desc in quality_items)
    quality = '<section id="catalog-quality" class="quality-section"><div class="shell"><div class="section-header"><div class="section-tag">' + ("CALIDAD" if es else "QUALITY") + '</div><h2 class="section-title">' + esc(quality_title) + '</h2><p class="section-sub">' + esc("Cada molde pasa por un proceso de inspección de varias etapas, desde el acero hasta la prueba final, para garantizar un rendimiento conforme a los estándares internacionales." if es else "Every mould undergoes a rigorous multi-stage inspection process, from raw steel to final trial, guaranteeing performance that meets international standards.") + '</p><div class="section-line"></div></div><div class="quality-list">' + quality_cards + '</div></div></section>'

    steps = ''.join('<article class="step"><strong>' + esc(num) + '</strong><h3>' + esc(title) + '</h3><p>' + esc(desc) + '</p></article>' for num, title, desc in data(locale, "process_steps"))
    process = '<section id="catalog-workflow" class="process-section"><div class="shell"><div class="section-header"><div class="section-tag">' + ("FLUJO DE TRABAJO" if es else "WORKFLOW") + '</div><h2 class="section-title">' + esc("Proceso de cooperación" if es else "Cooperation Process") + '</h2><p class="section-sub">' + esc("Un enfoque transparente, paso a paso, desde la consulta inicial hasta la entrega final mantiene su proyecto en el camino correcto." if es else "A transparent, step-by-step approach from initial inquiry to final delivery keeps your project on track and meets your expectations.") + '</p><div class="section-line"></div></div><div class="process-steps">' + steps + '</div></div></section>'

    faq_pairs = [
        ("What information should I send for a quotation?", "Please share the cap drawing or sample, material, cavity count, machine interface and target output."),
        ("Can you make a custom cap mould?", "Yes. We review the part geometry, sealing surfaces, cooling, ejection and trial requirements before confirming the design."),
        ("What is the normal lead time?", "A standard sample mould often takes 15–25 days; production tooling is normally 35–55 days depending on complexity."),
        ("Do you test samples before shipment?", "Yes. Trial parts, dimensional checks and approved revision notes are kept with the handover package."),
        ("Which steels are available?", "S136, NAK80, H13 and equivalent grades can be selected according to resin, cycle and service-life targets."),
        ("Do you support international buyers?", "Yes. We coordinate export packing, documentation and delivery for international projects."),
        ("Can you supply auxiliary machines?", "Yes. Lining, assembly, folding, slitting and other auxiliary equipment can be coordinated for a complete cell."),
        ("How do I start a project?", "Send the drawing, sample, resin, cavities, machine information and destination market by email or WhatsApp."),
    ]
    if es:
        faq_pairs = [
            ("¿Qué información debo enviar para una cotización?", "Comparta el plano o muestra, material, número de cavidades, interfaz de máquina y producción prevista."),
            ("¿Pueden fabricar un molde de tapa personalizado?", "Sí. Revisamos la geometría, las superficies de sellado, la refrigeración, la expulsión y las pruebas antes de confirmar el diseño."),
            ("¿Cuál es el plazo normal?", "Un molde de muestra suele tardar 15–25 días; el molde de producción normalmente 35–55 días según la complejidad."),
            ("¿Prueban las muestras antes del envío?", "Sí. Las piezas de prueba, comprobaciones dimensionales y revisiones aprobadas quedan en el paquete de entrega."),
            ("¿Qué aceros están disponibles?", "Seleccionamos S136, NAK80, H13 y equivalentes según la resina, el ciclo y la vida útil prevista."),
            ("¿Atienden a compradores internacionales?", "Sí. Coordinamos embalaje de exportación, documentación y entrega para proyectos internacionales."),
            ("¿Pueden suministrar máquinas auxiliares?", "Sí. Podemos coordinar máquinas de lining, ensamblaje, plegado, corte y otras soluciones auxiliares."),
            ("¿Cómo comienzo un proyecto?", "Envíe el plano, muestra, resina, cavidades, información de máquina y mercado por correo o WhatsApp."),
        ]
    faq_rows = ''.join('<details' + (' open' if i == 0 else '') + '><summary>' + esc(question) + '</summary><p class="faq-answer">' + esc(answer) + '</p></details>' for i, (question, answer) in enumerate(faq_pairs))
    testimonials = '<div id="catalog-testimonials" class="testimonials"><h3><span class="testimonial-star">★</span> ' + esc(testimonial_title) + '</h3><article class="testimonial-card"><div class="quote">"LEYA MOULD delivered our high-cavity water cap mould ahead of schedule. The precision and cycle time exceeded expectations."</div><div class="author">Production Head · India</div><div class="company">International Beverage Producer</div></article><article class="testimonial-card"><div class="quote">"The flip-top moulds run flawlessly on our injection lines. Excellent after-sales support."</div><div class="author">Technical Manager · Brazil</div><div class="company">Personal Care Packaging Group</div></article><article class="testimonial-card"><div class="quote">"The cooling design helped us increase output while keeping cap quality stable."</div><div class="author">Plant Director · Germany</div><div class="company">Industrial Packaging Company</div></article></div>'
    faq = '<section id="catalog-faq" class="faq-section"><div class="shell"><div class="faq-grid"><div class="faq-list"><h3 id="faq-heading"><span class="faq-star">?</span> ' + esc(faq_title) + '</h3>' + faq_rows + '</div>' + testimonials + '</div></div></section>'

    cta_title = "Empiece su proyecto de moldes" if es else "Start Your Cap Mould Project"
    cta_desc = "Envíenos su dibujo, muestra o requisitos de producción. Responderemos con las siguientes preguntas técnicas y un camino claro." if es else "Send your drawing, sample or production requirements. We will reply with the next technical questions and a clear path forward."
    contact = '<section id="catalog-contact" class="cta-section"><div class="shell"><div class="cta-box"><h2><span class="cta-star">✦</span> ' + esc(cta_title) + '</h2><p>' + esc("Contact us for a quote and technical consultation — we will reply within 24 hours" if not es else "Contáctenos para una cotización y consulta técnica; responderemos en 24 horas.") + '</p><div class="cta-contact-row"><a href="tel:+8613606727715" class="cta-contact-item phone-link">☎ <span>+86 136 0672 7715</span></a><a href="mailto:' + EMAIL + '" class="cta-contact-item">✉ <span>' + EMAIL + '</span></a><a href="' + WA_URL + '" class="cta-contact-item whatsapp-link">◉ <span>WhatsApp</span></a></div></div></div></section>'

    # Order follows the reference page: products → advantages → samples →
    # trials → technology → quality → workflow → FAQ → testimonials → CTA.
    return advantages_section + samples_section + catalog_video_section(locale) + technology + quality + process + faq + testimonials + contact

def products_page(locale: str) -> str:
    catalog_count = len(CAP_MOULD_SERIES)
    hero = '<section class="catalog-hero"><div class="shell"><h1>Precision <span>MOULDING</span><br>Across ' + str(catalog_count) + ' Product Families</h1><p>Professional plastic mould manufacturer with 15+ years of experience. From closures and preforms to bottle tooling, we deliver high-precision, long-life mould solutions.</p><a class="button button--round" href="' + localized_href(locale, "/contact/#inquiry") + '">' + esc(text(locale, "quote")) + ' →</a><div class="catalog-stats"><div><strong>15+</strong><span>YEARS EXPERIENCE</span></div><div><strong>' + str(catalog_count) + '</strong><span>PRODUCT FAMILIES</span></div><div><strong>40+</strong><span>COUNTRIES SERVED</span></div><div><strong>2000+</strong><span>MOULDS DELIVERED</span></div></div></div></section>'
    crumb = '<nav class="reference-breadcrumb" aria-label="Breadcrumb"><div class="shell"><a href="' + local_link(locale, "/") + '">' + esc(text(locale, "home")) + '</a><span>›</span><span>' + esc(text(locale, "products")) + '</span></div></nav>'
    cards = ''.join(cap_series_card(locale, c) for c in CAP_MOULD_SERIES)
    products = '<section class="section cap-series-section"><div class="shell">' + section_heading(locale, "OUR PRODUCTS", "Mould Product Families", "Explore our comprehensive range of " + str(len(CAP_MOULD_SERIES)) + " specialized mould product families. Each mould is engineered for high-volume production, dimensional accuracy and extended service life.") + '<div class="cap-series-grid">' + cards + '</div></div></section>'
    return hero + crumb + products + catalog_support_sections(locale)

def cap_product_page(locale: str, item: dict) -> str:
    helpers = {"esc": esc, "image": image, "localized_href": localized_href}
    return render_category_page(locale, item, helpers)

def about_page(locale: str) -> str:
    # The reference About page is a long, editorial company page rather than a
    # short text card. Keep the structure local to this route so the shared
    # water-cup/template pages remain untouched.
    es = locale == "es"
    if es:
        story, title, subtitle = "Nuestra historia", "Sobre LEYA MOULD", "LEYA MOULD es una marca de proyectos de moldes con sede en Huangyan, Taizhou, Zhejiang, China. Acompañamos a compradores internacionales con precisión, claridad técnica y soporte durante todo el proyecto."
        who = "Quiénes somos"
        who_paras = [
            "LEYA MOULD desarrolla proyectos de moldes para tapones, preformas, botellas y componentes de packaging. Nuestro trabajo conecta el diseño de la pieza, el acero, la refrigeración, la expulsión y las pruebas de producción.",
            "Revisamos moldes de agua, bebidas, aceite, alimentación, medicina, cuidado personal y cierres funcionales. El alcance se adapta al material, el cuello, las cavidades, la máquina y el objetivo de ciclo del comprador.",
            "El equipo mantiene una comunicación de proyecto clara: dibujo, muestra, revisión DFM, informe de prueba y cambios aprobados permanecen conectados hasta la entrega."
        ]
        journey, why, facility, certs, production, together = "Nuestro recorrido", "Por qué elegir LEYA MOULD", "Instalaciones y equipos", "Certificaciones y calidad", "Nuestras instalaciones de producción", "Trabajemos juntos"
        together_text = "¿Tiene un proyecto de moldes? Póngase en contacto con nuestro equipo para una conversación técnica y una cotización."
    else:
        story, title, subtitle = "Our Story", "About LEYA MOULD", "LEYA MOULD is a mould-project brand based in Huangyan, Taizhou, Zhejiang Province, China. We support international buyers with precision, clear engineering communication and practical project support."
        who = "Who We Are"
        who_paras = [
            "LEYA MOULD develops mould projects for caps, preforms, bottles and packaging components. Our work connects part design, steel, cooling, ejection and production trials.",
            "We review water, beverage, oil, food, medical, personal-care and functional closures. The scope is matched to the material, neck finish, cavity plan, machine interface and cycle target supplied by the buyer.",
            "The team keeps the project conversation clear: drawing, sample, DFM review, trial report and approved revisions stay connected through handover."
        ]
        journey, why, facility, certs, production, together = "Our Journey", "Why Choose LEYA MOULD", "Our Facility & Equipment", "Certifications & Quality", "Our Production Facilities", "Let's Work Together"
        together_text = "Have a mould project? Contact our team for a practical technical conversation and quotation."

    timeline = [
        ("01", "Design foundation", "A clear product brief connects the drawing, material, neck finish and intended production process."),
        ("02", "Project matching", "Mould family, cavity plan, machine interface and target output are confirmed before steel is cut."),
        ("03", "Technology review", "Cooling, hot runner, parting line and ejection are reviewed against the part geometry."),
        ("04", "Precision manufacturing", "Machining, EDM, polishing, fitting and inspection follow the approved tooling brief."),
        ("05", "Trial and validation", "Trial samples, dimensional checks and agreed changes guide the final handover."),
        ("06", "Global project support", "Approved files, delivery notes and technical support stay available after shipment.")
    ]
    advantages = [
        ("Precision Engineering", "CAD/CAM review, CNC machining and inspection keep critical closure dimensions under control.", '<path d="M12 2l3.09 6.26L22 9.27l-5 4.87L18.18 22 12 18.56 5.82 22 7 14.14l-5-4.87 6.91-1.01L12 2z"></path>'),
        ("Custom Solutions", "We adapt the mould structure to the closure design, resin, machine and production requirements.", '<path d="M3 18v-6a9 9 0 1 1 18 0v6h-2v-6a7 7 0 1 0-14 0v6H3zm6 2h6v2H9v-2zm-4-2h2v-2H5v2zm12 0h2v-2h-2v2z"></path>'),
        ("Quality Assurance", "Trial runs, dimensional checks and sample approval create a documented handover.", '<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"></path>'),
        ("Fast Delivery", "A staged tooling plan keeps machining, fitting, trial and delivery milestones visible.", '<path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7z"></path>'),
        ("Integrated Solutions", "Mould design, production evidence and auxiliary-process requirements remain in one project conversation.", '<path d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"></path>'),
        ("Lifetime Support", "Approved drawings, inspection records and technical notes make future support easier.", '<path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"></path>')
    ]
    equipment = ["5-Axis CNC Machining Centers", "High-Speed EDM Machines", "Wire-Cut EDM Machines", "Precision Grinding Machines", "CNC Lathes & Milling Machines", "Injection Molding Trial Machines", "3D Coordinate Measuring Machines (CMM)", "Hardness Testers & Spectrometers"]
    certifications = ["ISO 9001:2015 Quality System", "CE-ready machine documentation", "Food-contact material review", "Medical mould quality records"]
    reference_images = "https://www.cap-molds.com/images/"
    facility_images = [
        (reference_images + "CNC-machining-workshop.jpg", "CNC machining workshop"),
        (ABOUT_MEDIA["assembly"], "EDM machine area"),
        (reference_images + "Quality-inspection-room.jpg", "Quality inspection room"),
        (ABOUT_MEDIA["assembly"], "Mould assembly area"),
        (reference_images + "Injection-trial-machine.jpg", "Injection trial machine"),
        (reference_images + "Warehouse-and-shipping-area.jpg", "Warehouse and shipping area"),
        (ABOUT_MEDIA["assembly"], "5-axis machining center"),
        (reference_images + "Engineering-design-office.jpg", "Engineering design office"),
        (reference_images + "Showroom01.jpg", "Showroom 01"),
        (reference_images + "Showroom02.jpg", "Showroom 02"),
        (reference_images + "Showroom03.jpg", "Showroom 03"),
        (reference_images + "Showroom04.jpg", "Showroom 04"),
        (reference_images + "Showroom05.jpg", "Showroom 05"),
        (reference_images + "Showroom06.jpg", "Showroom 06"),
        (reference_images + "Showroom07.jpg", "Showroom 07"),
        (reference_images + "Showroom08.jpg", "Showroom 08"),
    ]
    intro_body = intro(locale, title, subtitle, "/about/")
    overview = '<section class="mould-about-block"><div class="mould-about-overview"><div class="mould-about-overview-image"><img src="' + ABOUT_MEDIA["team"] + '" alt="LEYA MOULD engineering team reviewing a mould project" loading="eager" decoding="async"></div><div><h2>' + esc(who) + '</h2>' + ''.join('<p>' + esc(p) + '</p>' for p in who_paras) + '</div></div><div class="mould-about-stats">' + ''.join('<div class="mould-about-stat"><span class="number">' + n + '</span><span class="label">' + esc(label) + '</span></div>' for n, label in [("15+", "Years of Experience"), ("60+", "Countries Served"), ("500+", "Moulds Delivered"), ("80+", "Skilled Team Members")]) + '</div></section>'
    journey_html = '<section class="mould-about-block"><h2>' + esc(journey) + '</h2><div class="mould-about-timeline">' + ''.join('<div class="mould-about-timeline-item"><span class="year">' + esc(year) + '</span><div><h3>' + esc(head) + '</h3><p>' + esc(desc) + '</p></div></div>' for year, head, desc in timeline) + '</div></section>'
    advantages_html = '<section class="mould-about-block"><h2>' + esc(why) + '</h2><div class="mould-about-advantages">' + ''.join('<article><div class="icon"><svg viewBox="0 0 24 24" aria-hidden="true">' + icon + '</svg></div><h3>' + esc(head) + '</h3><p>' + esc(desc) + '</p></article>' for head, desc, icon in advantages) + '</div></section>'
    equipment_html = '<section class="mould-about-block"><h2>' + esc(facility) + '</h2><p>Our manufacturing references use modern machining, inspection and trial equipment so every tooling decision can be checked against the production brief.</p><ul class="mould-about-equipment">' + ''.join('<li><span>✓</span>' + esc(item) + '</li>' for item in equipment) + '</ul></section>'
    cert_html = '<section class="mould-about-block"><h2>' + esc(certs) + '</h2><p>Quality evidence is kept with the project and reviewed before shipment. The final documentation follows the confirmed buyer requirements.</p><div class="mould-about-certifications">' + ''.join('<span>' + esc(item) + '</span>' for item in certifications) + '</div></section>'
    facilities_html = '<section class="mould-about-block"><h2>' + esc(production) + '</h2><p>LEYA MOULD production references show the engineering, inspection and sample-review work behind each tooling project.</p><div class="mould-about-facilities">' + ''.join('<figure><img src="' + esc(file_name) + '" alt="' + esc(alt) + '" loading="lazy" decoding="async"></figure>' for file_name, alt in facility_images) + '</div></section>'
    contact_html = '<section class="mould-about-contact"><h2>' + esc(together) + '</h2><p>' + esc(together_text) + '</p><div class="mould-about-contact-cards"><a href="tel:+8613606727715"><span class="icon">☎</span><span><strong>Phone / WhatsApp</strong><small>+86 136 0672 7715</small></span></a><a href="mailto:' + EMAIL + '"><span class="icon">✉</span><span><strong>Email</strong><small>' + EMAIL + '</small></span></a><a href="' + WA_URL + '" target="_blank" rel="noopener"><span class="icon">↗</span><span><strong>WhatsApp</strong><small>Chat with LEYA MOULD</small></span></a></div></section>'
    return '<div class="mould-about-page">' + intro_body + overview + journey_html + advantages_html + equipment_html + cert_html + facilities_html + contact_html + '</div>'

def capabilities_page(locale: str) -> str:
    title = "Cap Auxiliary Machines" if locale == "en" else ("Máquinas auxiliares para tapas" if locale == "es" else text(locale, "capabilities"))
    subtitle = "Complete your cap production line with our specialized auxiliary machines. Designed to work seamlessly with our plastic cap molds, these machines handle critical post-molding operations such as lining, folding, slitting, printing, and wadding."
    intro_image = "https://www.cap-molds.com/images/plastic-bottle-caps.jpg"
    intro_copy = (
        "<p>While injection molds produce the basic cap shape, many modern closures require additional processing to achieve full functionality. "
        "Tamper-evident bands must be precisely folded or slit to break cleanly upon opening. Induction seal liners need to be inserted accurately "
        "to create leak-proof containers. Brand logos and date codes are often printed on the cap surface for traceability and marketing. "
        "These operations demand dedicated auxiliary machines that ensure every cap meets strict quality standards.</p>"
        "<p>At LEYA MOULD, we not only manufacture the molds that shape your caps but also offer a comprehensive range of auxiliary machines "
        "to complete your production. By providing both mold and post-molding equipment, we help you build a fully integrated manufacturing cell "
        "with consistent quality, faster changeovers, and simplified after-sales support. Below are six popular cap auxiliary machines.</p>"
    )
    machine_cards = ''.join(
        '<article class="machine-card"><img class="machine-card-image" src="https://www.cap-molds.com/upload/product/month_2105/' + esc(item["image"]) + '" alt="' + esc(item["alt"]) + '" loading="lazy" decoding="async">'
        '<div class="machine-card-body"><h2 class="machine-card-name">' + esc(item["name"]) + '</h2><p class="machine-card-desc">' + esc(item["description"]) + '</p>'
        '<a href="' + localized_href(locale, "/contact/?model=" + item["model"] + "#inquiry") + '" class="machine-link">Learn More <span aria-hidden="true">→</span></a></div></article>'
        for item in AUXILIARY_MACHINES
    )
    contact = (
        '<section class="contact-section"><h2>Need Auxiliary Equipment for Your Cap Line?</h2>'
        '<p class="section-subtitle">Contact LEYA MOULD to discuss your cap size, production volume and the auxiliary operations you require. We will recommend a practical machine setup for your factory.</p>'
        '<div class="contact-cards"><a href="tel:+8613606727715" class="contact-card"><span class="icon-circle">☎</span><div class="info"><span class="label">Phone</span><span class="value">+86 136 0672 7715</span></div></a>'
        '<a href="mailto:amyhu@leyamould.com" class="contact-card"><span class="icon-circle">✉</span><div class="info"><span class="label">Email</span><span class="value">amyhu@leyamould.com</span></div></a>'
        '<a href="' + localized_href(locale, "/contact/#inquiry") + '" class="contact-card"><span class="icon-circle whatsapp">↗</span><div class="info"><span class="label">Project Enquiry</span><span class="value">Tell us about your line</span></div></a></div></section>'
    )
    body = intro(locale, title, subtitle, "/capabilities/")
    body += '<section class="aux-page"><section class="intro-section"><div class="intro-image"><img src="' + intro_image + '" alt="Various plastic bottle caps produced by LEYA MOULD" loading="lazy" decoding="async"></div><div class="intro-content"><h2>Why Cap Auxiliary Machines Are Essential</h2>' + intro_copy + '</div></section><div class="machine-grid">' + machine_cards + '</div>' + contact + '</section>'
    return body

def service_page(locale: str, service: dict) -> str:
    body = intro(locale, service["title"], service["text"], "/capabilities/" + service["slug"] + "/")
    body += '<section class="section"><div class="shell"><div class="split"><div><h2 class="section__title">' + esc(service["title"]) + '</h2><p class="copy-muted">' + esc(service["text"]) + '</p><p class="copy-muted">' + esc(text(locale, "technical_text")) + '</p></div><div class="split__placeholder"><strong>PROJECT FILES TO BE REVIEWED</strong><p>Drawing · sample · PDF · revision notes</p></div></div><p style="margin-top:28px"><a class="button" href="' + localized_href(locale, "/contact/#inquiry") + '">' + esc(text(locale, "quote")) + ' →</a></p></div></section>'
    return body

def contact_page(locale: str) -> str:
    labels = {"FORM_ARIA": text(locale, "form_aria"), "FORM_NAME": "Full Name" if locale == "en" else "Nombre completo", "FORM_PHONE": "Phone / WhatsApp" if locale == "en" else "Teléfono / WhatsApp", "FORM_COMPANY": text(locale, "form_company"), "FORM_EMAIL": text(locale, "form_email"), "FORM_CATEGORY": "Cap Mould Type" if locale == "en" else "Tipo de molde de tapa", "FORM_CATEGORY_PLACEHOLDER": "— Select cap mould type —" if locale == "en" else "— Seleccione el tipo de molde —", "FORM_REQUIREMENTS": "Your Message" if locale == "en" else "Su mensaje", "FORM_PRIVACY_NOTE": "Your information is secure." if locale == "en" else "Su información está protegida.", "FORM_PRIVACY": text(locale, "form_privacy"), "FORM_SUBMIT": "Send Inquiry Now" if locale == "en" else "Enviar consulta"}
    form = render_template("contact-form", **{key: esc(value) for key, value in labels.items()})
    body = intro(locale, text(locale, "contact_title"), text(locale, "contact_intro"), "/contact/")
    stats_labels = ["Years Experience", "Countries Served", "Molds Delivered", "Quote Response"] if locale == "en" else ["Años de experiencia", "Países atendidos", "Moldes entregados", "Respuesta de cotización"]
    stats = '<div class="trust-row" aria-label="LEYA MOULD at a glance">' + ''.join('<div class="trust-badge"><span class="badge-number">' + value + '</span><span class="badge-label">' + esc(label) + '</span></div>' for value, label in zip(["15+", "60+", "500+", "24h"], stats_labels)) + '</div>'
    info = '<div class="contact-info-card"><div class="contact-info-block"><span class="contact-info-icon">⌖</span><h3>Factory Address</h3><strong>LEYA MOULD Co.,Ltd</strong><p>' + esc(ADDRESS) + '</p></div><div class="contact-info-block"><h3>Contact Methods</h3><dl class="contact-methods"><div><dt>PHONE / WHATSAPP</dt><dd><a href="tel:+8613606727715">+86 136 0672 7715</a></dd></div><div><dt>EMAIL</dt><dd><a href="mailto:' + EMAIL + '">' + EMAIL + '</a></dd></div><div><dt>WEBSITE</dt><dd><a href="https://leyamould.com/">leyamould.com</a></dd></div></dl></div>' + stats + '</div>'
    quick_answers = [("⏱️ How fast can I get a quote?", "We respond within 24 hours. Use WhatsApp/WeChat for urgent requests."), ("📐 What info do I need to provide?", "Share cap design, material, cavity count, and production volume."), ("🌍 Do you ship internationally?", "Yes, we serve 60+ countries worldwide."), ("📱 How do I add you on WhatsApp/WeChat?", "Scan the QR codes on this page or click to enlarge them.")]
    if locale == "es":
        quick_answers = [("⏱️ ¿Cuánto tardan en enviar una cotización?", "Respondemos en 24 horas. Use WhatsApp/WeChat para solicitudes urgentes."), ("📐 ¿Qué información debo proporcionar?", "Comparta el diseño de la tapa, material, número de cavidades y volumen de producción."), ("🌍 ¿Realizan envíos internacionales?", "Sí, atendemos a más de 60 países."), ("📱 ¿Cómo puedo añadirles en WhatsApp/WeChat?", "Escanee los códigos QR de esta página o haga clic para ampliarlos.")]
    quick_title = "Quick Answers" if locale == "en" else "Respuestas rápidas"
    quick = '<section class="faq-teaser" aria-labelledby="quick-answers-title"><h2 id="quick-answers-title">' + quick_title + '</h2><div class="faq-list">' + ''.join('<div class="faq-item"><p class="faq-q">' + esc(question) + '</p><p class="faq-a">' + esc(answer) + '</p></div>' for question, answer in quick_answers) + '</div></section>'
    body += '<section class="section contact-section"><div class="shell"><div class="contact-layout">' + info + '<div class="contact-form-panel"><h2>Send Us Your Inquiry</h2><p>Fill out the form and we will reply as soon as possible.</p>' + form + '</div></div>' + quick + '</div></section>'
    return body

def faq_page(locale: str) -> str:
    cap = "https://www.cap-molds.com"
    if locale == "es":
        page_eyebrow = "CENTRO DE AYUDA"
        page_title = "Preguntas <span class=\"reference-title-accent\">frecuentes</span>"
        page_subtitle = "Encuentre respuestas rápidas sobre nuestros moldes de tapas, máquinas auxiliares, proceso de pedido y soporte técnico. Si no encuentra lo que busca, contacte con nosotros directamente."
        groups = [
            ("Productos y capacidades", [
                ("¿Qué tipos de moldes para tapas de plástico fabrica LEYA MOULD?", "Fabricamos moldes para tapas de agua y bebidas, tapas hot-fill, aceite comestible, salsas y condimentos, tapas médicas, cosméticas, flip-top, precintos, deportivas, bicomponente, boca ancha, aceite de motor, garrafas y diseños de cierre personalizados."),
                ("¿También suministran máquinas auxiliares para tapas?", "Sí. Podemos coordinar máquinas de lining, plegado, corte, impresión, wadding y soluciones combinadas para completar una célula de producción integrada."),
                ("¿Pueden diseñar un molde personalizado para mi cierre?", "Sí. Envíe un plano 2D/3D o una muestra y revisaremos la geometría, el material, las cavidades, la máquina y las necesidades de prueba antes de confirmar el diseño.")
            ]),
            ("Pedidos y entrega", [
                ("¿Qué información necesito para recibir una cotización?", "Necesitamos el tipo de tapa, planos 2D/3D, material, número de cavidades, especificaciones de la máquina, volumen previsto y requisitos especiales como precinto o hot runner."),
                ("¿Cuál es el plazo habitual para un molde nuevo?", "Depende de la complejidad y de las cavidades. Los moldes de muestra sencillos suelen requerir 15–25 días y los moldes de producción multicavidad normalmente 35–55 días. El calendario se confirma con la cotización."),
                ("¿Realizan pruebas y validación de muestras antes del envío?", "Sí. Realizamos pruebas, comprobaciones dimensionales y revisión de muestras antes del envío, y mantenemos conectados el informe de prueba y las revisiones aprobadas."),
                ("¿Qué condiciones de pago aceptan?", "Las condiciones se confirman en la cotización según el proyecto, el alcance y la relación comercial. Nuestro equipo puede revisar una estructura adecuada para cada pedido.")
            ]),
            ("Técnica y soporte", [
                ("¿Qué materiales utilizan para los moldes?", "Seleccionamos aceros de molde de calidad, como S136, NAK80, H13 y equivalentes, según la resina, el ciclo, la cavidad y la vida útil esperada."),
                ("¿Qué garantía ofrecen para los moldes?", "La garantía y el alcance de soporte se definen en la oferta del proyecto. También mantenemos disponibles los registros técnicos para facilitar el mantenimiento posterior."),
                ("¿Realizan envíos internacionales?", "Sí. Coordinamos embalaje y transporte internacional según el destino y el calendario del comprador, con documentación del proyecto para la entrega."),
                ("¿Cómo comienzo un proyecto con LEYA MOULD?", "Envíe el plano, muestra, material, cavidades, máquina y mercado de destino por correo electrónico o WhatsApp. Responderemos con las siguientes preguntas técnicas.")
            ])
        ]
        contact_title, contact_text = "¿Todavía tiene preguntas?", "Nuestro equipo está listo para ayudarle. Escríbanos y responderemos en un plazo de 24 horas."
        labels = ("Teléfono", "Correo electrónico", "WhatsApp", "WeChat")
        values = ("+86 136 0672 7715", EMAIL, "Chat con LEYA MOULD", "Consulte por WeChat")
    else:
        page_eyebrow = "HELP CENTER"
        page_title = "Frequently Asked <span class=\"reference-title-accent\">Questions</span>"
        page_subtitle = "Find quick answers to common questions about our plastic cap molds, auxiliary machines, ordering process, and more. Can't find what you're looking for? Contact us directly."
        groups = [
            ("Products & Capabilities", [
                ("What types of plastic cap molds does LEYA MOULD manufacture?", "We specialize in water and beverage cap molds, hot fill caps, edible oil caps, soy sauce and condiment closures, medical and cosmetic caps, flip-top, tamper-evident, sports, two-color, wide-mouth, motor oil, 5-gallon, pull-ring and fully custom closure molds."),
                ("Do you provide auxiliary machines along with cap molds?", "Yes. We can coordinate cap lining, folding, slitting, pad printing, wadding and combined folding and slitting machines to complete an integrated production cell."),
                ("Can you design a custom cap mold for my unique closure design?", "Absolutely. Provide your 2D/3D drawings or a sample cap and our engineering team will review the geometry, material, cavity plan, machine interface and trial requirements before confirming the design.")
            ]),
            ("Ordering & Delivery", [
                ("What information do I need to provide to get a mold quotation?", "To prepare an accurate quotation, we typically need the cap type, 2D/3D design drawings, material, cavity number, injection machine specifications, target production volume and any special requirements such as tamper-evident features or hot runner preferences."),
                ("What is the typical lead time for a new cap mold?", "Lead times depend on mold complexity and cavity count. A standard sample mold often requires 15–25 days, while multi-cavity production molds typically require 35–55 days. A detailed timeline is confirmed with your quotation."),
                ("Do you offer mold trials and sample testing before shipment?", "Yes. Every project includes trial planning, dimensional checks and sample review before shipment. Approved trial results and revision notes remain connected to the tooling handover."),
                ("What payment terms do you accept?", "Payment terms are confirmed in the project quotation according to scope, schedule and commercial requirements. Our team can discuss a practical structure for each order.")
            ]),
            ("Technical & Support", [
                ("What materials are used for your cap molds?", "We select quality mold steels such as S136, NAK80, H13 and equivalent grades according to the resin, cycle target, cavity plan and expected service life."),
                ("What is the warranty on your cap molds?", "Warranty scope and support terms are defined in the project quotation. We also keep technical records available to make maintenance and future support practical."),
                ("Do you ship molds internationally?", "Yes. We coordinate export packing and international shipping according to the destination and schedule, with the approved project documentation prepared for handover."),
                ("How do I start a project with LEYA MOULD?", "Contact us by email or WhatsApp with the drawing, sample, material, cavity plan, machine information and destination market. We will reply with the next technical questions.")
            ])
        ]
        contact_title, contact_text = "Still Have Questions?", "Our team is ready to help. Reach out and we'll respond within 24 hours."
        labels = ("Phone", "Email", "WhatsApp", "WeChat")
        values = ("+86 136 0672 7715", EMAIL, "Chat with LEYA MOULD", "Ask about WeChat")

    prefix = '<section class="reference-banner reference-banner--compact"><img src="' + cap + '/upload/Banner/pheader-faq.jpg" alt="LEYA MOULD FAQ" loading="eager" decoding="async"></section>'
    prefix += '<nav class="reference-breadcrumb faq-breadcrumb" aria-label="Breadcrumb"><div class="shell"><a href="' + local_link(locale, "/") + '">' + esc(text(locale, "home")) + '</a><span>›</span><span>' + esc("FAQs" if locale == "en" else "Preguntas frecuentes") + '</span></div></nav>'
    header_html = '<header class="page-header"><span class="badge">' + esc(page_eyebrow) + '</span><h1>' + page_title + '</h1><p class="subtitle">' + esc(page_subtitle) + '</p></header>'
    item_index = 0
    groups_html = []
    for group_title, pairs in groups:
        rows = []
        for question, answer in pairs:
            item_index += 1
            answer_id = "faq-answer-" + str(item_index)
            rows.append('<div class="faq-item"><button class="faq-question" type="button" aria-expanded="false" aria-controls="' + answer_id + '">' + esc(question) + '<span class="icon" aria-hidden="true">+</span></button><div class="faq-answer" id="' + answer_id + '"><p>' + esc(answer) + '</p></div></div>')
        groups_html.append('<section class="faq-group"><h2 class="faq-group-title">' + esc(group_title) + '</h2><div class="faq-list">' + ''.join(rows) + '</div></section>')
    phone_svg = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.62 10.79a15.05 15.05 0 0 0 6.59 6.59l2.2-2.2a1 1 0 0 1 1.02-.24 11.36 11.36 0 0 0 3.57.57 1 1 0 0 0 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1 11.36 11.36 0 0 0 .57 3.57 1 1 0 0 0-.24 1.02z"></path></svg>'
    mail_svg = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 4-8 5-8-5V6l8 5 8-5v2z"></path></svg>'
    chat_svg = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.5 11.2a8.4 8.4 0 0 1-12.4 7.4L4 20l1.4-4A8.4 8.4 0 1 1 20.5 11.2Z"></path></svg>'
    contact_cards = ''.join('<a class="contact-card" href="' + href + '"><span class="icon-circle' + (' whatsapp' if index == 2 else (' wechat' if index == 3 else '')) + '">' + icon + '</span><div class="info"><span class="label">' + esc(label) + '</span><span class="value">' + esc(value) + '</span></div></a>' for index, (label, value, href, icon) in enumerate(((labels[0], values[0], "tel:+8613606727715", phone_svg), (labels[1], values[1], "mailto:" + EMAIL, mail_svg), (labels[2], values[2], WA_URL, chat_svg), (labels[3], values[3], localized_href(locale, "/contact/"), chat_svg))))
    contact_html = '<section class="faq-contact-section"><h2>' + esc(contact_title) + '</h2><p class="section-subtitle">' + esc(contact_text) + '</p><div class="contact-cards">' + contact_cards + '</div></section>'
    script = '<script>(()=>{const root=document.querySelector("[data-faq-page]");if(!root)return;const items=[...root.querySelectorAll(".faq-item")];items.forEach(item=>{const button=item.querySelector(".faq-question");button.addEventListener("click",()=>{const active=item.classList.contains("active");items.forEach(other=>{other.classList.remove("active");const b=other.querySelector(".faq-question");if(b)b.setAttribute("aria-expanded","false")});if(!active){item.classList.add("active");button.setAttribute("aria-expanded","true")}})});})();</script>'
    return '<div class="faq-route">' + prefix + '<div class="faq-page" data-faq-page>' + header_html + ''.join(groups_html) + contact_html + '</div>' + script + '</div>'

def samples_page(locale: str) -> str:
    cap = "https://www.cap-molds.com"
    title = "Plastic Cap Samples" if locale == "en" else ("Muestras de tapas de plástico" if locale == "es" else text(locale, "samples"))
    subtitle = "Explore a wide variety of plastic bottle caps that we manufacture using our high-precision injection molds. Each cap is a sample of what our molds can produce — from standard water closures to complex tamper-evident designs."
    cards = []
    for item in SAMPLE_ITEMS:
        applications = ''.join('<li>' + esc(app) + '</li>' for app in item["applications"])
        cards.append(
            '<article class="sample-card">'
            '<img class="sample-image" src="' + cap + '/images/samples/' + esc(item["image"]) + '" alt="' + esc(item["alt"]) + '" loading="lazy" decoding="async">'
            '<div class="sample-body"><h2 class="sample-name">' + esc(item["name"]) + '</h2>'
            '<p class="sample-desc">' + esc(item["description"]) + '</p>'
            '<div class="sample-mold">🛠️ ' + esc(item["mold"]) + '</div>'
            '<div class="sample-applications"><h4>Applications</h4><ul>' + applications + '</ul></div></div></article>'
        )
    contact = (
        '<section class="samples-contact-section"><h2>Want to See More Samples or Request a Quote?</h2>'
        '<p class="section-subtitle">Contact LEYA MOULD today. We will send you the right samples and a practical proposal for your project.</p>'
        '<div class="sample-contact-cards">'
        '<a class="sample-contact-card" href="tel:+8613606727715"><span class="sample-contact-icon">☎</span><span><strong>Phone / WhatsApp</strong><small>+86 136 0672 7715</small></span></a>'
        '<a class="sample-contact-card" href="mailto:amyhu@leyamould.com"><span class="sample-contact-icon">✉</span><span><strong>Email</strong><small>amyhu@leyamould.com</small></span></a>'
        '<a class="sample-contact-card sample-contact-card--accent" href="' + localized_href(locale, "/contact/#inquiry") + '"><span class="sample-contact-icon">↗</span><span><strong>Request a Quote</strong><small>Tell us about your mould</small></span></a>'
        '</div></section>'
    )
    return intro(locale, title, subtitle, "/samples/") + '<section class="samples-page"><div class="sample-list">' + ''.join(cards) + '</div>' + contact + '</section>'

VIDEO_SEED = [
    {"videoId": "elkadaPoBHc", "titleEn": "Video of 5 gallon cap trial mold", "titleEs": "Vídeo de prueba del molde de tapa de garrafón", "description": "", "publishedAt": "2021-10-07T00:57:36Z"},
    {"videoId": "wMPqPOKdnf4", "titleEn": "8cavity flip top cap mold with cold runner", "titleEs": "Molde de tapa abatible de 8 cavidades con colada fría", "description": "", "publishedAt": "2021-10-07T00:58:46Z"},
    {"videoId": "E0M3IwYBsGw", "titleEn": "16cavity cap mold with slitting machine and cold runner", "titleEs": "Molde de tapas de 16 cavidades con máquina de corte y colada fría", "description": "", "publishedAt": "2021-10-07T00:59:24Z"},
    {"videoId": "y1NrJ4GUOO4", "titleEn": "28mm high speed cap mould", "titleEs": "Molde de tapas de alta velocidad de 28 mm", "description": "", "publishedAt": "2021-10-07T00:59:54Z"},
    {"videoId": "YLNnJWATMB4", "titleEn": "28 drops plastic cover (24 cavity)", "titleEs": "Tapa plástica de 28 puntos (24 cavidades)", "description": "", "publishedAt": "2021-10-09T07:30:01Z"},
    {"videoId": "t-I5OczexGc", "titleEn": "32-cavity cap mold", "titleEs": "Molde de tapas de 32 cavidades", "description": "", "publishedAt": "2021-10-09T07:32:51Z"},
    {"videoId": "1VO69jVYxgY", "titleEn": "32-cavity bottle cap injection molding (hot runner)", "titleEs": "Inyección de tapas de botella de 32 cavidades (canal caliente)", "description": "", "publishedAt": "2021-10-12T03:05:54Z"},
    {"videoId": "03FybMF9qCE", "titleEn": "48-cavity cap mold", "titleEs": "Molde de tapas de 48 cavidades", "description": "", "publishedAt": "2021-10-12T03:06:30Z"},
    {"videoId": "LpWp3_8S2c0", "titleEn": "48 cavity cap mold", "titleEs": "Molde de tapas de 48 cavidades", "description": "", "publishedAt": "2021-10-13T10:20:32Z"},
    {"videoId": "eJCq4OYiR68", "titleEn": "48mm cap mold", "titleEs": "Molde de tapas de 48 mm", "description": "", "publishedAt": "2021-10-13T10:21:23Z"},
    {"videoId": "2AnfOabyI10", "titleEn": "cap molds flip top cap mould", "titleEs": "Molde de tapas abatibles", "description": "", "publishedAt": "2021-10-13T10:22:15Z"},
    {"videoId": "5AaCsTX7W2s", "titleEn": "Bottle Cap Mould-Oil Cap Trial Video", "titleEs": "Vídeo de prueba del molde de tapa para aceite", "description": "", "publishedAt": "2021-10-19T00:36:22Z"}
    ,{"videoId": "_NQOLYk86pg", "titleEn": "Bottle cap mold injection process", "description": "", "publishedAt": "2021-10-19T00:40:24Z"}
    ,{"videoId": "q7jK4xlw69I", "titleEn": "5 gallon handle trial video", "description": "", "publishedAt": "2021-10-25T13:17:08Z"}
    ,{"videoId": "Wq8C6vaYx2M", "titleEn": "Flip Top Caps Mould Combination Video", "description": "", "publishedAt": "2021-10-27T00:07:52Z"}
    ,{"videoId": "Wd34XWe7GW0", "titleEn": "Clamshell mold inner lid", "description": "", "publishedAt": "2021-10-30T00:31:17Z"}
    ,{"videoId": "4WGtdJ0RbKs", "titleEn": "38 handle mould (video)", "description": "", "publishedAt": "2021-11-09T05:39:50Z"}
    ,{"videoId": "oO1s-x2Toak", "titleEn": "Bottle cap assembly machine", "description": "", "publishedAt": "2021-11-09T05:43:28Z"}
    ,{"videoId": "IykcO0ub3tY", "titleEn": "PET bottle cap mould", "description": "", "publishedAt": "2021-11-10T23:53:23Z"}
    ,{"videoId": "DquWhXWBscE", "titleEn": "PET bottle handle mould", "description": "", "publishedAt": "2021-11-10T23:54:58Z"}
    ,{"videoId": "eiUVBe98Pxo", "titleEn": "PET48 mouth bottle cap mould", "description": "", "publishedAt": "2021-11-10T23:55:55Z"}
    ,{"videoId": "aL9L1gSqusA", "titleEn": "Automatic beverage bottle cap folding and cutting machine", "description": "", "publishedAt": "2021-11-24T01:45:01Z"}
    ,{"videoId": "1WSPN8xIu-Y", "titleEn": "Mineral water bottle cap cutting machine", "description": "", "publishedAt": "2022-01-06T07:49:02Z"}
    ,{"videoId": "x46eR9ULJ84", "titleEn": "Nucleic acid extraction tube mold", "description": "", "publishedAt": "2022-02-11T00:32:27Z"}
    ,{"videoId": "fOju6mXi_aU", "titleEn": "5 Gallon Smart Cap Bottle Cap Mold", "description": "", "publishedAt": "2022-02-16T08:34:56Z"}
    ,{"videoId": "O81wopvbPrY", "titleEn": "1 out of 24 cavities 29/21 edible oil cap mould, edible oil cap mould, plastic cap mould", "description": "", "publishedAt": "2022-03-24T05:45:44Z"}
    ,{"videoId": "XjPrI73RTPM", "titleEn": "Cap cutting machine Cap ring cutting machine Cap electrostatic precipitator", "description": "", "publishedAt": "2022-03-29T00:30:50Z"}
    ,{"videoId": "v-Xx2AR6dkU", "titleEn": "Nucleic acid cap mould, sampling tube cap, virus tube cap mould", "description": "", "publishedAt": "2022-04-02T00:18:00Z"}
    ,{"videoId": "6j8loGkHg-E", "titleEn": "Oil cap mould, 4 liter Mobil oil cap", "description": "", "publishedAt": "2022-04-06T09:02:42Z"}
    ,{"videoId": "lMzPKjPUW10", "titleEn": "29/21 oil cap mould, olive oil cap mould, cooking oil cap mould", "description": "", "publishedAt": "2022-04-07T04:36:00Z"}
    ,{"videoId": "Wz3ieeKzUZA", "titleEn": "Anti-theft bottle cap, bottle cap mould - outer anti-theft bottle cap mould", "description": "", "publishedAt": "2022-04-08T09:30:25Z"}
    ,{"videoId": "4YHOguWhg4I", "titleEn": "38 bottle caps, juice caps and beverage caps - capping machine - bottle cap folding machine", "description": "", "publishedAt": "2022-04-13T05:09:50Z"}
    ,{"videoId": "fVs3yAMm8mE", "titleEn": "Motor cap off, automatic cap off mould, anti-theft cap, anti-theft oil cap", "description": "", "publishedAt": "2022-04-14T01:54:54Z"}
    ,{"videoId": "L0QfA_EfSAk", "titleEn": "16-cavity 28-port flip mold, 28-410 oil motor flip, automatic flip off, butterfly flip molds", "description": "", "publishedAt": "2022-04-15T07:10:21Z"}
    ,{"videoId": "4ThJj0Gnggs", "titleEn": "Virus tube cap mould, 60 cavity nucleic acid tube cap mould, sampling tube cap mould", "description": "", "publishedAt": "2022-04-18T00:45:21Z"}
    ,{"videoId": "RNQh1bI8xEQ", "titleEn": "18-410 inner plug cap, flat cap inner plug cap mould manufacturing", "description": "", "publishedAt": "2022-04-19T05:43:05Z"}
    ,{"videoId": "cYTcA_nSda4", "titleEn": "5 gallon lid mould, pure water bucket lid mould, smart lid mould", "description": "", "publishedAt": "2022-04-21T00:50:43Z"}
    ,{"videoId": "YNh3qCmpI9E", "titleEn": "48 mouth water cap 5L water cap mould 1-3L gallon bucket cap water cap mould oil cap mould", "description": "", "publishedAt": "2022-04-25T01:24:34Z"}
    ,{"videoId": "go2N0k8XrjY", "titleEn": "55 mouth bucket cap 18.9 liter bucket cap mould 3-5 gallon bucket cap water bottle cap mould", "description": "", "publishedAt": "2022-04-28T01:07:18Z"}
    ,{"videoId": "2Rzi5JjJvRI", "titleEn": "Wide mouth pet bottle cap mould, high transparent bottle cap, crystal bottle cap", "description": "", "publishedAt": "2022-05-05T10:11:19Z"}
    ,{"videoId": "134e25e9b3k", "titleEn": "cap folding and slitting machine + gasket mounting machine", "description": "", "publishedAt": "2022-05-10T02:45:17Z"}
    ,{"videoId": "q9mPWB1wczM", "titleEn": "Automatic combination bottle Cap lining machine", "description": "", "publishedAt": "2022-05-11T07:19:14Z"}
    ,{"videoId": "zeGz5MY-y5A", "titleEn": "20/24/28/32/38mm flat cover mold, flat top cover mold", "description": "", "publishedAt": "2022-05-13T09:49:13Z"}
    ,{"videoId": "kvJDFZTXIP8", "titleEn": "24-410 28-410, 32-410 Cosmetic bottle caps, health care product caps Syrup bottle caps moulds", "description": "", "publishedAt": "2022-05-16T04:38:53Z"}
    ,{"videoId": "SIuGaN4zxbQ", "titleEn": "29-21 flip lid cooking oil flip lid mold olive oil lid mold sunflower oil lid mold maker", "description": "", "publishedAt": "2022-05-17T09:53:11Z"}
    ,{"videoId": "M-aQ8iZRAPE", "titleEn": "Engine oli cap mould manufacture", "description": "", "publishedAt": "2022-05-19T03:21:07Z"}
    ,{"videoId": "O4bCwhfPM24", "titleEn": "Bottle cap folding +cutting machine, 28 ports, 30/25 29/25 38 45 48mm water cap beverage cap oil cap", "description": "", "publishedAt": "2022-05-27T00:24:12Z"}
    ,{"videoId": "DYZ73vH_iCU", "titleEn": "Anti-theft cap Tear cap Pull ear cap Tear edge cover cap mold", "description": "", "publishedAt": "2022-06-01T06:02:43Z"}
    ,{"videoId": "m2OA8-PdONU", "titleEn": "55mm bucket cover five gallon smart cover, disposable gallon bucket cover large bucket cover", "description": "", "publishedAt": "2022-06-13T02:26:12Z"}
    ,{"videoId": "eNRJgBfNKmk", "titleEn": "Bottle cap folding and cutting machine", "description": "", "publishedAt": "2022-06-22T06:47:25Z"}
]

def video_card(item: dict, locale: str) -> str:
    title = esc(item.get("titleEs" if locale == "es" else "titleEn", item.get("titleEn", "LEYA MOULD video")))
    description = esc(item.get("description", ""))
    video_id = esc(item.get("videoId", ""))
    published = esc(item.get("publishedAt", ""))
    date_text = "" if not item.get("publishedAt") else item["publishedAt"][:10]
    if locale == "es" and date_text:
        try:
            year, month, day = date_text.split("-")
            date_text = f"{day}/{month}/{year}"
        except ValueError:
            pass
    return ('<article class="video-card" data-video-id="' + video_id + '">'
        '<div class="video-thumb" data-video-id="' + video_id + '" role="button" tabindex="0" aria-label="Play ' + title + '">'
        '<img src="https://i.ytimg.com/vi/' + video_id + '/mqdefault.jpg" alt="' + title + '" loading="lazy" decoding="async">'
        '<span class="play-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"></path></svg></span></div>'
        '<div class="video-body"><time class="video-date" datetime="' + published + '"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-.75-1.23-4.5-2.67V7z"></path></svg>' + esc(date_text) + '</time>'
        '<h2 class="video-title"><button type="button" class="video-title-link" data-video-id="' + video_id + '">' + title + '</button></h2>'
        '<p class="video-desc">' + description + '</p></div></article>')

def video_page(locale: str) -> str:
    title = "Video Gallery" if locale == "en" else "Galería de vídeos"
    subtitle = ("Watch our latest mould demonstrations, factory tours, and technical insights. See LEYA MOULD in action."
                if locale == "en" else "Vea nuestras demostraciones de moldes, recorridos de fábrica y conocimientos técnicos. Descubra LEYA MOULD en acción.")
    videos = STATE.get("youtubeVideos") if isinstance(STATE.get("youtubeVideos"), list) else []
    videos = [item for item in videos if isinstance(item, dict) and re.fullmatch(r"[A-Za-z0-9_-]{11}", str(item.get("videoId") or ""))]
    if not videos:
        videos = VIDEO_SEED
    cards = ''.join(video_card(item, locale) for item in videos)
    empty = "No videos found yet." if locale == "en" else "Todavía no hay vídeos."
    labels = {"close": "Close video" if locale == "en" else "Cerrar vídeo", "play": "Play video" if locale == "en" else "Reproducir vídeo"}
    payload = json.dumps(videos, ensure_ascii=False).replace("</", "<\\/")
    body = ('<section class="video-gallery-page" data-video-gallery data-public-api="/api/youtube-videos">'
        '<div class="video-grid" id="videoGrid">' + cards + '</div>'
        '<p class="video-empty" id="videoEmpty" hidden>' + empty + '</p>'
        '<div class="video-modal" id="videoModal" aria-hidden="true"><div class="video-modal-inner" role="dialog" aria-modal="true" aria-label="' + esc(title) + '">'
        '<button type="button" class="close-modal" id="closeVideoModal" aria-label="' + esc(labels["close"]) + '">×</button><iframe id="videoIframe" title="' + esc(labels["play"]) + '" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe></div></div>'
        '<script type="application/json" id="videoSeed">' + payload + '</script>'
        '<script>(()=>{const root=document.querySelector("[data-video-gallery]");if(!root)return;const grid=document.getElementById("videoGrid"),empty=document.getElementById("videoEmpty"),modal=document.getElementById("videoModal"),frame=document.getElementById("videoIframe"),close=document.getElementById("closeVideoModal");const lang=document.documentElement.lang||"en";const esc=v=>String(v??"").replace(/[&<>"\']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",\"":"&quot;","\'":"&#39;"}[c]));const date=v=>{try{return new Intl.DateTimeFormat(lang,{year:"numeric",month:"long",day:"numeric"}).format(new Date(v))}catch{return v||""}};const card=v=>{const id=esc(v.videoId||"");if(!/^[A-Za-z0-9_-]{11}$/.test(id))return "";const title=v.title||((lang==="es"?v.titleEs:v.titleEn)||"LEYA MOULD video");return `<article class="video-card" data-video-id="${id}"><div class="video-thumb" data-video-id="${id}" role="button" tabindex="0" aria-label="Play video"><img src="https://i.ytimg.com/vi/${id}/mqdefault.jpg" alt="${esc(title)}" loading="lazy" decoding="async"><span class="play-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"></path></svg></span></div><div class="video-body"><time class="video-date" datetime="${esc(v.publishedAt||"")}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-.75-1.23-4.5-2.67V7z"></path></svg>${date(v.publishedAt)}</time><h2 class="video-title"><button type="button" class="video-title-link" data-video-id="${id}">${esc(title)}</button></h2><p class="video-desc">${esc(v.description||"")}</p></div></article>`};const render=items=>{grid.innerHTML=(items||[]).map(card).join("");empty.hidden=Boolean(items&&items.length);};const play=id=>{if(!/^[A-Za-z0-9_-]{11}$/.test(id))return;frame.src="https://www.youtube.com/embed/"+id+"?autoplay=1&rel=0";modal.classList.add("active");modal.setAttribute("aria-hidden","false");};const stop=()=>{modal.classList.remove("active");modal.setAttribute("aria-hidden","true");frame.src="";};grid.addEventListener("click",e=>{const t=e.target.closest("[data-video-id]");if(t)play(t.dataset.videoId)});grid.addEventListener("keydown",e=>{if((e.key==="Enter"||e.key===" ")&&e.target.closest("[data-video-id]")){e.preventDefault();play(e.target.closest("[data-video-id]").dataset.videoId)}});close.addEventListener("click",stop);modal.addEventListener("click",e=>{if(e.target===modal)stop()});document.addEventListener("keydown",e=>{if(e.key==="Escape")stop()});fetch(root.dataset.publicApi+"?locale="+encodeURIComponent(lang),{cache:"no-store"}).then(r=>r.ok?r.json():Promise.reject()).then(d=>render(d.items||[])).catch(()=>{});})();</script></section>')
    return intro(locale, title, subtitle, "/video/") + body

def catalog_video_section(locale: str) -> str:
    """Show the five current trial videos on the catalogue page.

    The cards are seeded from the same build snapshot as /video/ and then
    refreshed from the public YouTube-video endpoint, so an admin edit appears
    here without maintaining a second catalogue-specific video list.
    """
    videos = STATE.get("youtubeVideos") if isinstance(STATE.get("youtubeVideos"), list) else []
    videos = [item for item in videos if isinstance(item, dict) and re.fullmatch(r"[A-Za-z0-9_-]{11}", str(item.get("videoId") or ""))]
    if not videos:
        videos = VIDEO_SEED
    videos = videos[:5]
    cards = ''.join(video_card(item, locale) for item in videos)
    payload = json.dumps(videos, ensure_ascii=False).replace("</", "<\\/")
    title = "Cap Mould Trial Videos" if locale == "en" else "Vídeos de pruebas de moldes"
    description = ("Watch the latest mould trial videos managed from the YouTube video module."
                   if locale == "en" else "Vea los últimos vídeos de pruebas gestionados desde el módulo de vídeos de YouTube.")
    close_label = "Close video" if locale == "en" else "Cerrar vídeo"
    play_label = "Play video" if locale == "en" else "Reproducir vídeo"
    empty_label = "No videos found yet." if locale == "en" else "Todavía no hay vídeos."
    script = '''<script>(()=>{const root=document.querySelector("[data-catalog-videos]");if(!root)return;const grid=document.getElementById("catalogVideoGrid"),empty=document.getElementById("catalogVideoEmpty"),modal=document.getElementById("catalogVideoModal"),frame=document.getElementById("catalogVideoIframe"),close=document.getElementById("catalogVideoClose"),lang=document.documentElement.lang||"en";const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\\\"":"&quot;","'":"&#39;"}[c]));const date=v=>{try{return new Intl.DateTimeFormat(lang,{year:"numeric",month:"long",day:"numeric"}).format(new Date(v))}catch{return v||""}};const card=v=>{const id=String(v.videoId||"");if(!/^[A-Za-z0-9_-]{11}$/.test(id))return "";const title=(lang==="es"?v.titleEs:v.titleEn)||v.title||"LEYA MOULD video";return `<article class="video-card" data-video-id="${esc(id)}"><div class="video-thumb" data-video-id="${esc(id)}" role="button" tabindex="0" aria-label="${esc(lang==="es"?"Reproducir vídeo":"Play video")}"><img src="https://i.ytimg.com/vi/${esc(id)}/mqdefault.jpg" alt="${esc(title)}" loading="lazy" decoding="async"><span class="play-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"></path></svg></span></div><div class="video-body"><time class="video-date" datetime="${esc(v.publishedAt||"")}">${date(v.publishedAt)}</time><h3 class="video-title"><button type="button" class="video-title-link" data-video-id="${esc(id)}">${esc(title)}</button></h3><p class="video-desc">${esc(v.description||"")}</p></div></article>`};const render=items=>{const visible=(items||[]).slice(0,5);grid.innerHTML=visible.map(card).join("");empty.hidden=visible.length>0};const play=id=>{if(!/^[A-Za-z0-9_-]{11}$/.test(id))return;frame.src="https://www.youtube.com/embed/"+id+"?autoplay=1&rel=0";modal.classList.add("active");modal.setAttribute("aria-hidden","false")};const stop=()=>{modal.classList.remove("active");modal.setAttribute("aria-hidden","true");frame.src=""};grid.addEventListener("click",e=>{const target=e.target.closest("[data-video-id]");if(target)play(target.dataset.videoId)});grid.addEventListener("keydown",e=>{if((e.key==="Enter"||e.key===" ")&&e.target.closest("[data-video-id]")){e.preventDefault();play(e.target.closest("[data-video-id]").dataset.videoId)}});close.addEventListener("click",stop);modal.addEventListener("click",e=>{if(e.target===modal)stop()});document.addEventListener("keydown",e=>{if(e.key==="Escape")stop()});fetch(root.dataset.publicApi+"?locale="+encodeURIComponent(lang),{cache:"no-store"}).then(r=>r.ok?r.json():Promise.reject()).then(d=>render(d.items||[])).catch(()=>{});})();</script>'''
    return ('<section class="section catalog-video-section" data-catalog-videos data-public-api="/api/youtube-videos"><div class="shell">'
        + section_heading(locale, "MOULD TRIALS", title, description)
        + '<div class="video-gallery-page catalog-video-gallery"><div class="video-grid" id="catalogVideoGrid">' + cards + '</div><p class="video-empty" id="catalogVideoEmpty" hidden>' + esc(empty_label) + '</p></div>'
        + '<div class="video-modal" id="catalogVideoModal" aria-hidden="true"><div class="video-modal-inner" role="dialog" aria-modal="true" aria-label="' + esc(title) + '"><button type="button" class="close-modal" id="catalogVideoClose" aria-label="' + esc(close_label) + '">×</button><iframe id="catalogVideoIframe" title="' + esc(play_label) + '" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe></div></div>'
        + '<script type="application/json" id="catalogVideoSeed">' + payload + '</script>' + script + '</div></section>')

def localized_item_text(item: dict, locale: str, field: str) -> str:
    """Read an article's translated field without replacing CMS-owned values."""
    if locale == "es":
        return item.get(field + "Es") or item.get(field, "")
    return item.get(field, "")

def effective_news_items(category: str = "news") -> list[dict]:
    """Project reviewed mould editorial (or a matching D1 row) into cards.

    The registry is the auditable source fallback for this site. A D1 row only
    replaces it when it carries the same reviewed rich article payload; an
    unrelated water-cup Blog snapshot must never erase mould news.
    """
    reviewed = editorial_news_items(category)
    rows = STATE.get("blogPosts") if isinstance(STATE.get("blogPosts"), list) else []
    mapped = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        slug = str(row.get("slug") or "")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            continue
        title = str(row.get("title") or "").strip()
        summary = str(row.get("summary") or row.get("description") or "").strip()
        if not title or not summary:
            continue
        date = str(row.get("date") or row.get("published_at") or row.get("updated_at") or "")[:10].replace("-", "/")
        image_src = str(row.get("image") or "/assets/mould-news-placeholder.svg")
        if slug not in EDITORIAL_BY_SLUG:
            continue
        mapped.append({
            "slug": slug, "title": title, "titleEs": str(row.get("titleEs") or row.get("title_es") or ""),
            "date": date, "image": image_src, "summary": summary,
            "summaryEs": str(row.get("summaryEs") or row.get("summary_es") or ""),
            "alt": str(row.get("alt") or title), "altEs": str(row.get("altEs") or row.get("alt_es") or title),
            "editorial": EDITORIAL_BY_SLUG.get(slug),
        })
    if reviewed:
        # Keep the full 24-article registry in the archive. A partial D1
        # snapshot may contain owner-edited rows for only some slugs; those
        # rows override their own fields, while the remaining reviewed items
        # must not silently disappear from the list or routes.
        overrides = {row["slug"]: row for row in mapped}
        merged = []
        for base in reviewed:
            value = dict(base)
            if base["slug"] in overrides:
                value.update({key: overrides[base["slug"]][key] for key in ("title", "titleEs", "date", "image", "summary", "summaryEs", "alt", "altEs") if overrides[base["slug"]].get(key)})
                value["editorial"] = base.get("editorial")
            merged.append(value)
        return merged
    return mapped or (NEWS_ITEMS if category == "news" else MACHINE_NEWS_ITEMS)

def news_card(locale: str, item: dict, detail_prefix: str, category_label: str) -> str:
    detail_route = detail_prefix + item["slug"] + ".html"
    read_more = "Read More" if locale == "en" else "Leer más"
    title = localized_item_text(item, locale, "title")
    summary = localized_item_text(item, locale, "summary")
    alt = item.get("altEs" if locale == "es" else "alt") or title
    return ('<article class="news-card">'
        '<a class="news-card__media" href="' + localized_href(locale, detail_route) + '"><img src="' + esc(item["image"]) + '" alt="' + esc(alt) + '" loading="lazy" decoding="async"></a>'
        '<div class="news-card__content"><span class="eyebrow">' + esc(category_label) + '</span><time datetime="' + esc(item["date"]) + '">' + esc(item["date"]) + '</time>'
        '<h2><a href="' + localized_href(locale, detail_route) + '">' + esc(title) + '</a></h2><p>' + esc(summary) + '</p>'
        '<a class="news-card__link" href="' + localized_href(locale, detail_route) + '">' + esc(read_more) + ' →</a></div></article>')

def news_listing_page(locale: str, route: str, title: str, subtitle: str, items: list[dict], detail_prefix: str, category_label: str) -> str:
    cards = ''.join(news_card(locale, item, detail_prefix, category_label) for item in items)
    return intro(locale, title, subtitle, route) + '<section class="section news-listing-page"><div class="shell"><div class="blog-listing__grid">' + cards + '</div></div></section>'

def _editorial_route(slug: str) -> str:
    row = EDITORIAL_BY_SLUG.get(slug) or {}
    return "/news/" if row.get("category") == "news" else "/Bottle-Cap-Machine/"

def rich_news_body(locale: str, item: dict, category_label: str) -> str:
    """Render the seven-part GEO article without changing the shared shell."""
    editorial = item.get("editorial") if isinstance(item.get("editorial"), dict) else {}
    lang = "es" if locale == "es" else "en"
    title = localized_item_text(item, locale, "title")
    summary = localized_item_text(item, locale, "summary")
    cover_alt = item.get("altEs" if lang == "es" else "alt") or title
    sections = (editorial.get("sections") or {}).get(lang, [])
    checklist = (editorial.get("checklist") or {}).get(lang, [])
    faqs = (editorial.get("faqs") or {}).get(lang, [])
    matrix = editorial.get("matrix") or {}
    products = editorial.get("products") or []
    related_slugs = editorial.get("related") or []
    if not sections:
        return '<p>' + esc(summary) + '</p>'
    section_html = []
    for number, section in enumerate(sections, 1):
        section_html.append('<section class="blog-section"><h2><span class="blog-section__number">0' + str(number) + '</span>' + esc(section.get("heading") or "") + '</h2><p>' + esc(section.get("paragraph") or "") + '</p></section>')
    checklist_title = "Buyer checklist" if lang == "en" else "Lista de comprobación del comprador"
    checklist_html = '<section class="blog-checklist"><h2>' + checklist_title + '</h2><ol>' + ''.join('<li>' + esc(value) + '</li>' for value in checklist) + '</ol></section>'
    matrix_title = "Decision matrix" if lang == "en" else "Matriz de decisión"
    headers = (matrix.get("headers") or {}).get(lang, [])
    rows = matrix.get("rows") or []
    matrix_html = '<section class="blog-buyer-matrix"><h2>' + matrix_title + '</h2><div class="blog-buyer-matrix__scroll"><table><thead><tr>' + ''.join('<th>' + esc(value) + '</th>' for value in headers) + '</tr></thead><tbody>'
    for row in rows:
        cells = (row or {}).get(lang, [])
        matrix_html += '<tr>' + ''.join('<td>' + esc(value) + '</td>' for value in cells) + '</tr>'
    matrix_html += '</tbody></table></div></section>'
    faq_title = "Frequently asked questions" if lang == "en" else "Preguntas frecuentes"
    faq_html = '<section class="blog-faq"><h2>' + faq_title + '</h2>' + ''.join('<details><summary>' + esc(faq.get("question") or "") + '</summary><p>' + esc(faq.get("answer") or "") + '</p></details>' for faq in faqs) + '</section>'
    product_title = "Relevant mould categories" if lang == "en" else "Categorías de moldes relacionadas"
    product_html = '<section class="blog-products"><h2>' + product_title + '</h2><div class="blog-product-links">' + ''.join('<a class="blog-editorial__product-link" href="' + localized_href(locale, product.get("route") or "/products/") + '"><strong>' + esc((product.get("label") or {}).get(lang) or "") + '</strong><span>' + esc((product.get("reason") or {}).get(lang) or "") + '</span></a>' for product in products[:3]) + '</div></section>'
    related_title = "Related reading" if lang == "en" else "Lecturas relacionadas"
    related_cards = []
    for slug in related_slugs[:3]:
        related = EDITORIAL_BY_SLUG.get(str(slug))
        if not related:
            continue
        rtitle = (related.get("title") or {}).get(lang) or (related.get("title") or {}).get("en")
        rsummary = (related.get("description") or {}).get(lang) or (related.get("description") or {}).get("en")
        related_cards.append('<a class="blog-related__item" href="' + localized_href(locale, _editorial_route(str(slug)) + str(slug) + ".html") + '"><img src="' + esc(str(related.get("cover") or "/assets/mould-news-placeholder.svg")) + '" alt="' + esc(rtitle) + '" loading="lazy" decoding="async"><span><strong>' + esc(rtitle) + '</strong><small>' + esc(rsummary) + '</small></span></a>')
    related_html = '<section class="blog-related"><h2>' + related_title + '</h2><div class="blog-related__grid">' + ''.join(related_cards) + '</div></section>'
    sources_title = "Sources and disclosure" if lang == "en" else "Fuentes y transparencia"
    sources = editorial.get("evidenceSources") or []
    disclosure = (editorial.get("imageDisclosure") or {}).get(lang) or ""
    sources_html = '<section id="primary-sources" class="blog-sources"><h2>' + sources_title + '</h2><ul>' + ''.join('<li>' + esc(value) + '</li>' for value in sources) + '</ul><p>' + esc(disclosure) + '</p></section>'
    cta = (editorial.get("cta") or {}).get(lang) or ("Send your project brief" if lang == "en" else "Envíe su brief de proyecto")
    schema = {"@context": "https://schema.org", "@graph": [{"@type": "Article", "headline": title, "description": summary, "datePublished": item.get("date", "").replace("/", "-"), "dateModified": editorial.get("lastReviewed"), "inLanguage": lang, "image": [ORIGIN + str(item.get("image") or "")], "mainEntityOfPage": ORIGIN + localized_href(locale, ("/news/" if editorial.get("category") == "news" else "/Bottle-Cap-Machine/") + str(item.get("slug")) + ".html")}, {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": faq.get("question"), "acceptedAnswer": {"@type": "Answer", "text": faq.get("answer")}} for faq in faqs]}]}
    schema_html = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace("</", "<\\/") + '</script>'
    return ('<article class="blog-editorial__body" data-editorial-source="mould-registry">' + '<p class="blog-editorial__intro">' + esc(editorial.get("intro", {}).get(lang) or summary) + '</p>' + ''.join(section_html) + checklist_html + matrix_html + faq_html + product_html + related_html + sources_html + '<p class="blog-editorial__cta"><a class="button" href="' + localized_href(locale, "/contact/#inquiry") + '">' + esc(cta) + ' →</a></p>' + schema_html + '</article>')

def news_detail_page(locale: str, route: str, item: dict, category_route: str, category_label: str) -> str:
    back = "Back to News" if locale == "en" else "Volver a noticias"
    title = localized_item_text(item, locale, "title")
    summary = localized_item_text(item, locale, "summary")
    editorial_body = rich_news_body(locale, item, category_label)
    body = ('<section class="section news-detail-page"><div class="shell"><article class="article">'
        '<img class="news-detail-image" src="' + esc(item["image"]) + '" alt="' + esc(item.get("altEs" if locale == "es" else "alt") or title) + '" loading="eager" decoding="async">'
        '<div class="news-detail-meta"><span class="eyebrow">' + esc(category_label) + '</span><time datetime="' + esc(item["date"]) + '">' + esc(item["date"]) + '</time></div>'
        '<h1>' + esc(title) + '</h1><p class="news-detail-summary">' + esc(summary) + '</p>' + editorial_body +
        '<p><a class="text-link" href="' + localized_href(locale, category_route) + '">← ' + esc(back) + '</a></p>'
        '</article></div></section>')
    return intro(locale, title, summary, route) + body

def simple_page(locale: str, route: str, title: str, description: str, body: str) -> str:
    return intro(locale, title, description, route) + '<section class="section"><div class="shell"><div class="article">' + body + '</div></div></section>'

def write(path: str, content: str) -> None:
    target = OUTPUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

def add_alias_page(locale: str, alias_route: str, canonical_route: str, title: str, description: str, body: str, routes: dict[str, str]) -> None:
    """Emit a reference-site URL alias while keeping the clean route canonical."""
    localized_alias = route_for(locale, alias_route)
    if localized_alias.endswith(".html"):
        file_path = localized_alias.strip("/")
    else:
        file_path = localized_alias.strip("/") + "/index.html"
    write(file_path, shell(locale, title + " | " + BRAND_DISPLAY, description, canonical_route, body))
    routes[localized_alias] = title

def generate() -> dict:
    routes: dict[str, str] = {}
    news_items = effective_news_items("news")
    machine_news_items = effective_news_items("machine")
    def add(locale: str, route: str, title: str, description: str, body: str) -> None:
        localized = route_for(locale, route)
        if localized == "/":
            file_path = "index.html"
        elif localized.endswith(".html"):
            file_path = localized.strip("/")
        else:
            file_path = localized.strip("/") + "/index.html"
        page_override = page_override_for(locale, route)
        translated = localized_override(locale, route)
        final_title = str(translated.get("title") or page_override.get("seoTitle") or title)
        final_description = str(translated.get("description") or page_override.get("metaDescription") or description)
        final_body = str(translated.get("mainHtml") or BODY_OVERRIDES.get(route) or body)
        write(file_path, shell(locale, final_title + " | " + BRAND_DISPLAY if route != "/" else final_title + " | " + BRAND_DISPLAY, final_description, route, final_body))
        routes[localized] = title
    for locale in LOCALES:
        code = locale["code"]
        add(code, "/", text(code, "hero_title"), text(code, "hero_text"), home(code))
        add(code, "/products/", text(code, "products"), text(code, "categories_text"), products_page(code))
        # Reference-compatible aggregate route; keep /products/ as a stable alias.
        add(code, "/Plastic-cap-mold.html", text(code, "products"), text(code, "categories_text"), products_page(code))
        for cap_item in CAP_MOULD_SERIES:
            add(code, cap_item["route"], catalog_text(code, cap_item, "title"), catalog_text(code, cap_item, "description"), cap_product_page(code, cap_item))
        about_body = about_page(code)
        add(code, "/about/", text(code, "about_title"), text(code, "about_text"), about_body)
        add_alias_page(code, "/about/about_us.html", "/about/", text(code, "about_title"), text(code, "about_text"), about_body, routes)
        add_alias_page(code, "/about/ABOUT_US.html", "/about/", text(code, "about_title"), text(code, "about_text"), about_body, routes)
        add(code, "/capabilities/", text(code, "capabilities"), text(code, "technical_text"), capabilities_page(code))
        capabilities_body = capabilities_page(code)
        add_alias_page(code, "/machine/Cap-Auxiliary-Machines.html", "/capabilities/", "Cap Auxiliary Machines" if code == "en" else text(code, "capabilities"), text(code, "technical_text"), capabilities_body, routes)
        for service in CATALOG["services"]:
            add(code, "/capabilities/" + service["slug"] + "/", service["title"], service["text"], service_page(code, service))
        add(code, "/manufacturing/", text(code, "process"), text(code, "process_title"), simple_page(code, "/manufacturing/", text(code, "process"), text(code, "process_title"), '<p>' + esc(text(code, "process_title")) + '</p><p>' + esc(text(code, "technical_text")) + '</p>'))
        add(code, "/quality-control/", text(code, "footer_quality"), text(code, "technical_text"), simple_page(code, "/quality-control/", text(code, "footer_quality"), text(code, "technical_text"), '<p>' + esc(text(code, "technical_text")) + '</p>'))
        add(code, "/request-sample/", text(code, "quote"), text(code, "resources_text"), contact_page(code))
        contact_body = contact_page(code)
        add(code, "/contact/", text(code, "contact"), text(code, "contact_intro"), contact_body)
        add_alias_page(code, "/contact/contact_us.html", "/contact/", text(code, "contact"), text(code, "contact_intro"), contact_body, routes)
        samples_title = "Plastic Cap Samples" if code == "en" else ("Muestras de tapas de plástico" if code == "es" else text(code, "samples"))
        samples_body = samples_page(code)
        add(code, "/samples/", samples_title, "Explore plastic bottle cap samples manufactured with precision moulds.", samples_body)
        add_alias_page(code, "/cap-samples/Sample.html", "/samples/", samples_title, "Explore plastic bottle cap samples manufactured with precision moulds.", samples_body, routes)
        news_title = "News & Updates" if code == "en" else "Noticias y novedades"
        news_description = "Stay informed with LEYA MOULD mould technology, project notes and engineering insights." if code == "en" else "Conozca las novedades técnicas y los proyectos de LEYA MOULD."
        news_body = news_listing_page(code, "/news/", news_title, news_description, news_items, "/news/", "NEWS & INSIGHTS")
        add(code, "/news/", news_title, news_description, news_body)
        add_alias_page(code, "/news/news.html", "/news/", news_title, news_description, news_body, routes)
        add(code, "/news/Bottle-cap-molds.html", "Bottle Cap Mould News" if code == "en" else "Noticias sobre moldes de tapas", "Bottle cap mould project notes, market observations and practical production guidance." if code == "en" else "Notas de proyectos y orientación práctica sobre moldes de tapas.", news_listing_page(code, "/news/Bottle-cap-molds.html", "Bottle Cap Mould News" if code == "en" else "Noticias sobre moldes de tapas", "Bottle cap mould project notes, market observations and practical production guidance." if code == "en" else "Notas de proyectos y orientación práctica sobre moldes de tapas.", news_items, "/news/", "BOTTLE CAP MOULDS"))
        add(code, "/Bottle-Cap-Machine/Bottle-Cap-Machine.html", "Bottle Cap Machine" if code == "en" else "Máquinas para tapas de botella", "Machine, process and quality notes for complete bottle-cap production lines." if code == "en" else "Notas de máquinas, procesos y calidad para líneas de tapas.", news_listing_page(code, "/Bottle-Cap-Machine/Bottle-Cap-Machine.html", "Bottle Cap Machine" if code == "en" else "Máquinas para tapas de botella", "Machine, process and quality notes for complete bottle-cap production lines." if code == "en" else "Notas de máquinas, procesos y calidad para líneas de tapas.", machine_news_items, "/Bottle-Cap-Machine/", "BOTTLE CAP MACHINE"))
        for item in news_items:
            detail_route = "/news/" + item["slug"] + ".html"
            add(code, detail_route, localized_item_text(item, code, "title"), localized_item_text(item, code, "summary"), news_detail_page(code, detail_route, item, "/news/Bottle-cap-molds.html", "BOTTLE CAP MOULDS"))
        for item in machine_news_items:
            detail_route = "/Bottle-Cap-Machine/" + item["slug"] + ".html"
            add(code, detail_route, localized_item_text(item, code, "title"), localized_item_text(item, code, "summary"), news_detail_page(code, detail_route, item, "/Bottle-Cap-Machine/Bottle-Cap-Machine.html", "BOTTLE CAP MACHINE"))
        video_title = "Video Gallery" if code == "en" else "Galería de vídeos"
        video_description = "Watch our latest mould demonstrations, factory tours, and technical insights." if code == "en" else "Vea nuestras demostraciones de moldes y conocimientos técnicos."
        video_body = video_page(code)
        add(code, "/video/", video_title, video_description, video_body)
        add_alias_page(code, "/videolist/Cap-Mold-Video.html", "/video/", video_title, video_description, video_body, routes)
        add(code, "/faq/", text(code, "faq_title"), text(code, "faq_intro"), faq_page(code))
        add_alias_page(code, "/about/FAQs.html", "/faq/", text(code, "faq_title"), text(code, "faq_intro"), faq_page(code), routes)
        add(code, "/blog/", text(code, "blog_title"), text(code, "blog_text"), simple_page(code, "/blog/", text(code, "blog_title"), text(code, "blog_text"), '<p>' + esc(text(code, "blog_text")) + '</p><p><a class="button" href="' + localized_href(code, "/contact/#inquiry") + '">' + esc(text(code, "quote")) + ' →</a></p>'))
        add(code, "/privacy-policy/", text(code, "privacy_title"), text(code, "privacy_text"), simple_page(code, "/privacy-policy/", text(code, "privacy_title"), text(code, "privacy_text"), '<p>' + esc(text(code, "privacy_text")) + '</p>'))
    not_found = shell("en", "Page Not Found | LEYA MOULD", "The requested page could not be found.", "/404.html", intro("en", "Page Not Found", "The requested page could not be found.", "/404.html") + '<section class="section"><div class="shell"><a class="button" href="/">Back to Home →</a></div></section>')
    write("404.html", not_found)
    write("robots.txt", "User-agent: *\n" + ("Allow: /\nSitemap: " + ORIGIN + "/sitemap.xml\n" if INDEXING_APPROVED else "Disallow: /\n"))
    sitemap = ['<?xml version="1.0" encoding="utf-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for route in sorted(routes):
        # A pre-launch build intentionally emits an empty sitemap. Once
        # indexing is approved, only routes enabled in the page registry (or
        # generated routes without an explicit registry row) are listed.
        if INDEXING_APPROVED and sitemap_enabled(canonical_route_from_localized(route)):
            sitemap.append("  <url><loc>" + esc(ORIGIN + route) + "</loc></url>")
    sitemap.append("</urlset>")
    write("sitemap.xml", "\n".join(sitemap) + "\n")
    manifest = {"schemaVersion": 1, "locales": [{**row, "enabled": True, "publishReady": True} for row in LOCALES], "routes": sorted(routes)}
    write("locale-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return {"routes": routes, "locales": LOCALES}

if __name__ == "__main__":
    result = generate()
    print("LEYA_MOULD_SOURCE_BUILD_OK", "HTML_FILES", len(result["routes"]), "LOCALES", ",".join(x["code"] for x in result["locales"]))



