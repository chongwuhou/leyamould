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
from mould_category_pages import render_category_page, render_model_reference_section
from mould_localization import ES_COMMON_COPY, ES_SEO, ES_SHARED_CTA, spanish_editorial_copy, spanish_html_text, spanish_model_description, spanish_model_text, spanish_ui_copy, spanish_ui_text

ROOT = Path(__file__).resolve().parent
# The supplied logo is kept as a source asset so the published header can scale it without stretching.
CONFIG = json.loads((ROOT / "deployment/site.config.json").read_text(encoding="utf-8"))
ORIGIN = CONFIG["site"]["origin"]
INDEXING_APPROVED = CONFIG["site"].get("indexingApproved") is True
STRICT_D1 = os.environ.get("LEYA_REQUIRE_D1_SNAPSHOT", "").strip().lower() in {"1", "true", "yes"}
OUTPUT = ROOT / (os.environ.get("LEYA_OUTPUT_DIR") or ".")
CATALOG = json.loads((ROOT / "data/mould-catalog.json").read_text(encoding="utf-8"))
MODEL_DATA = json.loads((ROOT / "data/mould-models.json").read_text(encoding="utf-8")) if (ROOT / "data/mould-models.json").is_file() else {"models": []}
STATIC_HMOULD_MODELS = [row for row in MODEL_DATA.get("models", []) if isinstance(row, dict)]
EDITORIAL_DATA = json.loads((ROOT / "data/mould-news-editorial.json").read_text(encoding="utf-8")) if (ROOT / "data/mould-news-editorial.json").is_file() else {"items": []}
EDITORIAL_BY_SLUG = {str(row.get("slug")): row for row in EDITORIAL_DATA.get("items", []) if isinstance(row, dict) and row.get("slug")}
LEGACY_MEDIA_MANIFEST = json.loads((ROOT / "data/mould-legacy-media-manifest.json").read_text(encoding="utf-8")) if (ROOT / "data/mould-legacy-media-manifest.json").is_file() else {"items": []}
LEGACY_MEDIA_MAP = {str(row.get("source")): str(row.get("target")) for row in LEGACY_MEDIA_MANIFEST.get("items", []) if isinstance(row, dict) and row.get("source") and row.get("target")}
def legacy_media_url(path: str) -> str:
    value = str(path or "")
    full = value if value.startswith(("http://", "https://")) else "https://www.cap-molds.com" + (value if value.startswith("/") else "/" + value)
    return LEGACY_MEDIA_MAP.get(full, full)
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

def _normalise_model_reference(row: dict) -> dict:
    """Normalise the D1 snapshot without allowing it to change layout code.

    D1 owns reviewed business fields; the checked-in HMould catalogue remains
    the deterministic fallback until the first published R2-backed snapshot.
    """
    value = dict(row)
    value["slug"] = str(row.get("slug") or "").strip().lower()
    value["family"] = str(row.get("family") or "").strip().lower()
    value["title"] = str(row.get("title") or "").strip()
    value["alt"] = str(row.get("alt") or value["title"]).strip()
    value["sourceUrl"] = str(row.get("sourceUrl") or row.get("source_url") or "").strip()
    value["sourceImage"] = str(row.get("sourceImage") or row.get("source_image") or "").strip()
    value["image"] = str(row.get("image") or row.get("imagePath") or row.get("image_path") or "").strip()
    value["description"] = str(row.get("description") or "").strip()
    value["reviewedAt"] = str(row.get("reviewedAt") or row.get("reviewed_at") or "").strip()
    value["pdfUrl"] = str(row.get("pdfUrl") or row.get("pdf_url") or "").strip()
    value["pdfSha256"] = str(row.get("pdfSha256") or row.get("pdf_sha256") or "").strip().lower()
    try:
        value["pdfPages"] = int(row.get("pdfPages") or row.get("pdf_pages") or 0)
    except (TypeError, ValueError):
        value["pdfPages"] = 0
    translations = row.get("translations")
    value["translations"] = translations if isinstance(translations, dict) else {}
    # Published D1 rows may predate the Spanish model fields.  Add a
    # deterministic translation only when the owner has not supplied one;
    # source numbers, family and verified media remain unchanged.
    if not isinstance(value["translations"].get("es"), dict):
        value["translations"]["es"] = {}
    es = value["translations"]["es"]
    es.setdefault("title", spanish_model_text(value["title"]))
    es.setdefault("alt", spanish_model_text(value["alt"]))
    es.setdefault("description", spanish_model_description(value["description"]))
    return value

STATIC_HMOULD_MODELS = [_normalise_model_reference(row) for row in STATIC_HMOULD_MODELS]
_SNAPSHOT_MODEL_REFERENCES = [
    _normalise_model_reference(row) for row in STATE.get("modelReferences", [])
    if isinstance(row, dict) and row.get("slug") and row.get("family") and row.get("image")
]
# D1/CMS is authoritative in production.  An authenticated production
# snapshot that contains no reviewed rows must not silently repopulate the
# public catalogue from the checked-in import.  The source catalogue remains a
# deterministic fallback only for local clean-checkout work.
HMOULD_MODELS = _SNAPSHOT_MODEL_REFERENCES if STRICT_D1 else (_SNAPSHOT_MODEL_REFERENCES or STATIC_HMOULD_MODELS)
MODEL_REFERENCE_SOURCE = "cloudflare-d1:leya_model_references" if STRICT_D1 or _SNAPSHOT_MODEL_REFERENCES else "source-fallback:data/mould-models.json"

# The static renderer remains the visual source of truth.  These small
# adapters make its business inputs data-driven in the same way as the
# water-cup project: a reviewed D1 snapshot can override content, while a
# clean checkout still has an auditable source fallback.  No CSS or layout is
# selected from D1, so a CMS edit cannot silently redesign the public site.
BRAND_CONFIG = STATE.get("brand") if isinstance(STATE.get("brand"), dict) else {}
CONTACT_CONFIG = STATE.get("contacts") if isinstance(STATE.get("contacts"), dict) else {}
NAVIGATION = [row for row in STATE.get("navigation", []) if isinstance(row, dict)]
COMMON_COPY = STATE.get("commonCopy") if isinstance(STATE.get("commonCopy"), dict) else {}
PAGE_COPY = STATE.get("pageCopy") if isinstance(STATE.get("pageCopy"), dict) else {}
try:
    _PAGE_SOURCE = json.loads((ROOT / "data" / "mould-page-structured.json").read_text(encoding="utf-8"))
except (OSError, ValueError):
    _PAGE_SOURCE = {}

def _merge_copy(base: dict, override: dict) -> dict:
    result = json.loads(json.dumps(base)) if isinstance(base, dict) else {}
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge_copy(result[key], value)
        else:
            result[key] = value
    return result

def structured_page_copy(locale: str, route: str) -> dict:
    """Return the reviewed structured copy for one route and locale.

    D1 owns the editable words, while this renderer continues to own the DOM,
    spacing and responsive layout. Local development may use the checked-in
    fixture; production never falls back to it.
    """
    # In a production snapshot the translated page override is the only
    # accepted locale source.  Checked-in Spanish copy remains available for a
    # local clean checkout, but it must never silently fill a production page.
    # A production snapshot is the only business-copy source.  The checked-in
    # page JSON is intentionally available only to a local, non-production
    # checkout; otherwise a missing D1 field would silently reappear online.
    source = {} if STRICT_D1 else (_PAGE_SOURCE.get("en", {}) if isinstance(_PAGE_SOURCE.get("en", {}), dict) else {})
    source_locale = {} if STRICT_D1 else (_PAGE_SOURCE.get(locale, {}) if isinstance(_PAGE_SOURCE.get(locale, {}), dict) else {})
    d1_source = PAGE_COPY.get("en", {}) if isinstance(PAGE_COPY.get("en", {}), dict) else {}
    d1_localized = PAGE_COPY.get(locale, {}) if isinstance(PAGE_COPY.get(locale, {}), dict) else {}
    row = source.get(route) if isinstance(source.get(route), dict) else {}
    row = _merge_copy(row, source_locale.get(route) if isinstance(source_locale.get(route), dict) else {})
    # A source-language D1 row must not overwrite the reviewed Spanish branch.
    # In production both branches are D1-owned; a missing field is handled by
    # the completeness gate instead of a checked-in locale baseline.
    if locale == "en":
        row = _merge_copy(row, d1_source.get(route) if isinstance(d1_source.get(route), dict) else {})
    row = _merge_copy(row, d1_localized.get(route) if isinstance(d1_localized.get(route), dict) else {})
    return row

def structured_page_value(locale: str, route: str, key: str, fallback: str = "") -> str:
    value = structured_page_copy(locale, route).get(key)
    if isinstance(value, str) and value.strip():
        value = value.strip()
        return spanish_ui_text(value) if locale == "es" else value
    return "" if STRICT_D1 else fallback

def structured_section(locale: str, route: str, section_id: str, fallback_title: str = "", fallback_body: str = "", fallback_eyebrow: str = "") -> dict:
    """Read one small, text-only section override from D1.

    Older About rows use an object keyed by section id while newer editors use
    an array of ``{id,title,body,eyebrow}`` rows.  Accept both shapes so the
    public templates remain backwards compatible without storing HTML/CSS in
    the CMS.
    """
    raw = structured_page_copy(locale, route).get("sections")
    row = {}
    if isinstance(raw, dict):
        candidate = raw.get(section_id)
        row = candidate if isinstance(candidate, dict) else {}
    elif isinstance(raw, list):
        for candidate in raw:
            if isinstance(candidate, dict) and str(candidate.get("id") or "").strip() == section_id:
                row = candidate
                break
    result = {
        "eyebrow": str(row.get("eyebrow") or ("" if STRICT_D1 else fallback_eyebrow)).strip(),
        "title": str(row.get("title") or ("" if STRICT_D1 else fallback_title)).strip(),
        "body": str(row.get("body") or ("" if STRICT_D1 else fallback_body)).strip(),
        "bullets": [str(item).strip() for item in row.get("bullets", []) if str(item).strip()][:8] if isinstance(row.get("bullets"), list) else [],
        "items": [item for item in row.get("items", []) if isinstance(item, dict)][:48] if isinstance(row.get("items"), list) else [],
    }
    return spanish_ui_copy(result) if locale == "es" else result

def structured_section_items(locale: str, route: str, section_id: str, fallback: list[dict] | None = None) -> list[dict]:
    """Return editable text-only cards/steps for a D1 structured section."""
    section = structured_section(locale, route, section_id)
    items = section.get("items") if isinstance(section, dict) else []
    if isinstance(items, list) and items:
        rows = [item for item in items if isinstance(item, dict)][:48]
        return spanish_ui_copy(rows) if locale == "es" else rows
    rows = [] if STRICT_D1 else list(fallback or [])
    return spanish_ui_copy(rows) if locale == "es" else rows
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

# Reviewed source fallback for the two currently published locales. This is
# derived from the canonical catalogue only when D1 has no row; an editor's
# D1 value always replaces it.
PRODUCT_FALLBACK_SEO = {
    str(item.get("slug")): {"seoTitle": str(item.get("titleEs") or "").strip(), "metaDescription": str(item.get("descriptionEs") or "").strip()}
    for item in CATALOG.get("categories", [])
    if isinstance(item, dict) and item.get("slug") and item.get("titleEs") and item.get("descriptionEs")
}

CANONICAL_ALIASES = {
    "/about/about_us.html", "/about/ABOUT_US.html", "/machine/Cap-Auxiliary-Machines.html",
    "/contact/contact_us.html", "/cap-samples/Sample.html", "/news/news.html",
    "/videolist/Cap-Mold-Video.html", "/about/FAQs.html",
}
def migrate_legacy_media_urls(value: str) -> str:
    result = str(value or "")
    for source, target in LEGACY_MEDIA_MAP.items():
        result = result.replace(source, target)
    return result

BODY_OVERRIDES = {str(row.get("route")): migrate_legacy_media_urls(str(row.get("mainHtml", ""))) for row in STATE.get("pageBodies", []) if isinstance(row, dict) and row.get("route")}
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
    """Build the public category registry from D1, with a clean source fallback.

    The checked-in catalogue supplies only the visual fallback for a clean
    checkout. Published D1 rows own the structured family content and may also
    introduce a new safe
    family; it receives the same category template instead of disappearing
    from menus and generated routes.
    """
    # Static catalogue data is useful for a clean local checkout only.  A
    # production build must not keep a deleted/unpublished family alive by
    # starting from the repository catalogue and overlaying D1 rows.
    rows = [] if STRICT_D1 else json.loads(json.dumps(CATALOG.get("categories", [])))
    by_slug = {str(item.get("slug")): item for item in rows}
    for row in STATE.get("products", []):
        if not isinstance(row, dict):
            continue
        model = str(row.get("model") or "")
        content = _published_content(row)
        item = by_slug.get(model)
        if item is None:
            item = by_slug.get(str(content.get("slug") or ""))
        if item is None and content:
            route = str(content.get("route") or f"/product/{model}.html").strip()
            # D1 stores the canonical product route with title-case family
            # slugs (for example /product/PET-Preform-Mould.html).  Route
            # ownership is still the D1 row; matching must therefore be
            # case-insensitive instead of silently dropping every family in
            # strict production builds.
            if re.fullmatch(r"/product/[a-z0-9][a-z0-9-]{1,63}\.html", route, re.IGNORECASE) and re.fullmatch(r"[a-z0-9][a-z0-9-]{1,63}", model, re.IGNORECASE):
                title = str(content.get("title") or content.get("name") or model.replace("-", " ").title()).strip()
                description = str(content.get("description") or content.get("short") or "Custom mould family for plastic packaging projects.").strip()
                item = {"slug": model, "title": title, "navTitle": str(content.get("navTitle") or title), "description": description,
                        "short": str(content.get("short") or description), "detail": str(content.get("detail") or description),
                        "meta": str(content.get("meta") or description), "route": route, "image": str(content.get("image") or ""),
                        "checks": content.get("checks") if isinstance(content.get("checks"), list) else []}
                rows.append(item)
                by_slug[model] = item
        if item is None or not content:
            continue
        for field in ("title", "titleEs", "navTitle", "navTitleEs", "description", "descriptionEs", "short", "shortEs", "detail", "detailEs", "meta", "metaEs", "body", "bodyEs", "sections", "sectionsEs", "faqs", "faqsEs", "image", "route"):
            if isinstance(content.get(field), str) and content[field].strip():
                item[field] = content[field].strip()
        for field in ("sections", "sectionsEs", "faqs", "faqsEs"):
            if isinstance(content.get(field), list):
                item[field] = content[field]
        if isinstance(content.get("checks"), list):
            item["checks"] = [str(value).strip() for value in content["checks"] if str(value).strip()][:12]
        structured = content.get("structured") if isinstance(content.get("structured"), dict) else content.get("category")
        if isinstance(structured, dict):
            item["categoryCopy"] = structured
        structured_es = content.get("structuredEs") if isinstance(content.get("structuredEs"), dict) else content.get("categoryEs")
        if isinstance(structured_es, dict):
            item["categoryCopyEs"] = structured_es
    return rows

CATALOG["categories"] = _catalog_from_state()
_header_logo = (BRAND_CONFIG.get("logos", {}).get("header", {}) if isinstance(BRAND_CONFIG, dict) else {})
LOGO_SRC = str(_header_logo.get("src") or "/assets/leyamould-logo.svg?v=logo1")
if not (LOGO_SRC.startswith("/") or LOGO_SRC.startswith("https://")):
    LOGO_SRC = "/assets/leyamould-logo.svg?v=logo1"
LOGO_ALT = str(_header_logo.get("alt") or BRAND_DISPLAY)

def navigation_label(url: str, fallback: str, locale: str = "en") -> str:
    """Use D1's reviewed source-language label without changing menu structure.

    The navigation table is intentionally source-language/global. Localized
    labels continue to come from the D1 common-copy map and the reviewed
    catalogue fields, so an English admin edit cannot leak into Spanish.
    """
    if locale == "es":
        route_labels = {
            "/about/": text("es", "about"), "/faq/": text("es", "faq_title"),
            "/capabilities/": text("es", "machine"), "/samples/": text("es", "samples"),
            "/news/": text("es", "news"), "/video/": text("es", "video"),
            "/contact/": text("es", "contact_us"),
            "/news/Bottle-cap-molds.html": "Noticias sobre moldes de tapas",
            "/Bottle-Cap-Machine/Bottle-Cap-Machine.html": "Máquinas para tapas de botella",
        }
        if url in route_labels:
            return route_labels[url]
        for item in CATALOG.get("categories", []):
            if isinstance(item, dict) and str(item.get("route") or "") == url:
                return spanish_ui_text(str(item.get("navTitleEs") or item.get("titleEs") or fallback))
    rows = [row for row in NAVIGATION if str(row.get("url") or "") == url]
    rows.sort(key=lambda row: (int(row.get("sort_order", row.get("sortOrder", 999)) or 999), str(row.get("id", ""))))
    if not rows:
        return fallback
    row = rows[0]
    translations = row.get("translations") if isinstance(row.get("translations"), dict) else {}
    localized = translations.get(locale) if isinstance(translations, dict) else None
    if locale == "es" and not localized:
        # Older D1 navigation rows have no translations_json column value yet.
        # Use the reviewed catalogue fields and shared labels until the seed
        # migration fills the missing D1 translations.
        route_labels = {
            "/about/": text("es", "about"), "/faq/": text("es", "faq_title"),
            "/capabilities/": text("es", "machine"), "/samples/": text("es", "samples"),
            "/news/": text("es", "news"), "/video/": text("es", "video"),
            "/contact/": text("es", "contact_us"),
            "/news/Bottle-cap-molds.html": "Noticias sobre moldes de tapas",
            "/Bottle-Cap-Machine/Bottle-Cap-Machine.html": "Máquinas para tapas de botella",
        }
        localized = route_labels.get(url)
        if not localized:
            for item in CATALOG.get("categories", []):
                if isinstance(item, dict) and str(item.get("route") or "") == url:
                    localized = item.get("navTitleEs") or item.get("titleEs")
                    break
    value = str(localized or row.get("label") or fallback)
    return spanish_ui_text(value) if locale == "es" else value

def product_navigation_items() -> list[dict]:
    """Merge D1 product children with the checked-in visual catalogue.

    D1 controls additions, order and labels; the catalogue keeps existing
    families visible when an older database has not yet been seeded with every
    child row.
    """
    by_route = {str(item.get("route") or ""): item for item in CAP_MOULD_SERIES if isinstance(item, dict)}
    children = [row for row in NAVIGATION if str(row.get("parent_id") or row.get("parentId") or "") == "products" and str(row.get("url") or "").startswith("/")]
    children.sort(key=lambda row: (int(row.get("sort_order", row.get("sortOrder", 999)) or 999), str(row.get("id", ""))))
    result = []
    seen = set()
    for row in children:
        route = str(row.get("url") or "")
        item = by_route.get(route)
        if item is None:
            match = re.fullmatch(r"/product/([a-z0-9][a-z0-9-]{1,63})\.html", route)
            if match:
                item = {"slug": match.group(1), "route": route, "title": str(row.get("label") or match.group(1).replace("-", " ").title()), "navTitle": str(row.get("label") or "")}
        if item and route not in seen:
            item = dict(item)
            item["_navLabel"] = row.get("label") or ""
            result.append(item)
            seen.add(route)
    for item in CAP_MOULD_SERIES:
        route = str(item.get("route") or "")
        if route not in seen:
            result.append(item)
    return result

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
    if locale == "es" and route in ES_SEO:
        # site_pages stores the source-language SEO row.  Until a localized
        # page override exists, the reviewed Spanish SEO registry is the
        # correct locale-specific value; it must not inherit English metadata.
        title, description = ES_SEO[route]
        value["seoTitle"] = title
        value["metaDescription"] = description
    slug = product_slug_for_route(route)
    if slug:
        product = PRODUCT_SEO_OVERRIDES.get((slug, locale)) or PRODUCT_SEO_OVERRIDES.get((slug, "en"))
        if not product:
            # Older published product rows were seeded with reviewed localized
            # title/description fields before xuyi_product_seo was introduced.
            # They are still D1-owned values, so use them as the effective SEO
            # record rather than falling back to a source-only string.
            for row in STATE.get("products", []):
                if not isinstance(row, dict) or str(row.get("model") or "").strip().lower() != slug:
                    continue
                content = row.get("content") if isinstance(row.get("content"), dict) else {}
                suffix = "Es" if locale == "es" else ""
                title = str(content.get("seoTitle" + suffix) or content.get("titleEs" if locale == "es" else "title") or content.get("nameEs" if locale == "es" else "name") or "").strip()
                description = str(content.get("seoDescription" + suffix) or content.get("descriptionEs" if locale == "es" else "description") or content.get("shortEs" if locale == "es" else "short") or "").strip()
                if title and description:
                    product = {"seoTitle": title, "metaDescription": description}
                break
        if not product:
            if not STRICT_D1:
                fallback = PRODUCT_FALLBACK_SEO.get(slug) if locale == "es" else None
                if fallback:
                    product = fallback
                else:
                    for item in CATALOG.get("categories", []):
                        if not isinstance(item, dict) or str(item.get("slug") or "").strip().lower() != slug:
                            continue
                        title = str(item.get("title") or "").strip()
                        description = str(item.get("description") or "").strip()
                        if title and description:
                            product = {"seoTitle": title, "metaDescription": description}
                        break
            elif not product:
                raise RuntimeError("Strict D1 product SEO missing for " + slug + ":" + locale)
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
        if locale == "es":
            # Keep the D1 banner row authoritative while cleaning legacy
            # English shells when an older row has no reviewed Spanish branch.
            for key in ("title", "highlight", "description", "alt", "cta"):
                if isinstance(value.get(key), str):
                    value[key] = spanish_ui_text(value[key])
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
        "footer_tagline": "Bottle, cap, preform and custom product mould support for international buyers.", "footer_products": "Products", "footer_capabilities": "Capabilities", "footer_contact": "Contact Us", "footer_quick_links": "Quick Links", "footer_sitemap": "Sitemap", "footer_design": "Mould Design & Engineering", "footer_manufacturing": "Precision Manufacturing", "footer_quality": "Quality & Inspection", "footer_support": "Trial & Technical Support", "footer_quote": "Request a Quote →", "footer_faq": "FAQs", "footer_privacy": "Privacy Policy", "footer_sticky": "Mould Project Enquiries", "footer_cta_title": "Ready to discuss your mould project?", "footer_cta_text": "Send your drawing, sample or PDF and tell us the production target.", "footer_eyebrow": "LEYA MOULD · ENGINEERING · MANUFACTURING", "form_required": "Company name, work email and project requirements are required. Technical drawings, samples and documents can be attached later by email or WhatsApp.", "form_company": "Company Name", "form_email": "Work Email", "form_category": "Mould Category", "form_quantity": "Estimated Quantity", "form_country": "Destination Country", "form_type": "Inquiry Type", "form_quote": "Request a Quote", "form_new": "New Mould Design", "form_review": "Existing Mould Review", "form_tech": "Technical Consultation", "form_material": "Target Material", "form_advise": "Please advise", "form_other": "Other / to be confirmed", "form_requirements": "Your Requirements", "form_consent": "I agree to the", "form_privacy": "privacy policy", "form_submit": "Send Project Enquiry →", "form_aria": "Mould project enquiry form", "back": "Back to Home →", "learn": "Learn More →", "view": "View Category →", "category_note": "Technical specifications, images and PDF references are added after project review.", "contact_title": "Tell us about your mould project.", "contact_intro": "Send the part drawing, sample, target material, cavity plan, machine information and delivery market. We will reply with the next technical questions.", "faq_title": "Mould project questions", "faq_intro": "A short starting point for buyers preparing a tooling enquiry.", "about_title": "About LEYA MOULD", "about_text": "LEYA MOULD Co.,Ltd is a mould-project brand based in Huangyan, Taizhou, Zhejiang Province, China. The site is being prepared around an evidence-led catalogue for packaging and product tooling.", "privacy_title": "Privacy & enquiry data", "privacy_text": "We use the information you submit to respond to mould project enquiries, technical questions and quotation requests. Contact amyhu@leyamould.com for data questions.", "blog_title": "Mould project resources", "blog_text": "Technical articles and approved project resources will be added as the mould catalogue is reviewed.",
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
# The D1 common-copy row remains authoritative for owner-edited values, but a
# missing value or the old English baseline must never leak into the Spanish
# build.  This is also the clean-checkout fallback used before the first D1
# snapshot is available.
for _key, _value in ES_COMMON_COPY.items():
    if not TEXT["es"].get(_key) or TEXT["es"].get(_key) == TEXT["en"].get(_key):
        TEXT["es"][_key] = _value
TEXT["es"].update({"samples": "Muestras", "video": "Vídeo", "news": "Noticias", "contact": "Contacto", "cap_mould": "Moldes de tapones", "machine": "Máquina", "contact_us": "Contacto"})

def _repair_d1_spanish_copy() -> None:
    """Repair only known English baseline values in the in-memory D1 copy."""
    if not isinstance(COMMON_COPY, dict):
        return
    current = COMMON_COPY.setdefault("es", {})
    if not isinstance(current, dict):
        COMMON_COPY["es"] = current = {}
    for key, value in ES_COMMON_COPY.items():
        if not current.get(key) or current.get(key) == TEXT["en"].get(key):
            current[key] = value
    ctas = current.setdefault("shared_cta", {})
    if not isinstance(ctas, dict):
        COMMON_COPY["es"]["shared_cta"] = ctas = {}
    for variant, value in ES_SHARED_CTA.items():
        row = ctas.setdefault(variant, {})
        if not isinstance(row, dict):
            ctas[variant] = row = {}
        for key, localized in value.items():
            if not row.get(key) or row.get(key) == COMMON_COPY.get("en", {}).get("shared_cta", {}).get(variant, {}).get(key):
                row[key] = localized

_repair_d1_spanish_copy()

def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)

def text(locale: str, key: str) -> str:
    localized = COMMON_COPY.get(locale) if isinstance(COMMON_COPY.get(locale), dict) else {}
    source = COMMON_COPY.get("en") if isinstance(COMMON_COPY.get("en"), dict) else {}
    value = localized.get(key) if key in localized else None
    if isinstance(value, str) and value.strip():
        return spanish_ui_text(value) if locale == "es" else value
    if locale != "en" and STRICT_D1:
        raise RuntimeError("Strict D1 common copy missing for " + locale + ":" + key)
    if locale != "en":
        fallback_value = TEXT.get(locale, {}).get(key)
        if isinstance(fallback_value, str) and fallback_value.strip():
            return fallback_value
    value = source.get(key)
    if isinstance(value, str) and value.strip():
        return value
    if STRICT_D1:
        raise RuntimeError("Strict D1 common copy missing for " + locale + ":" + key)
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
            return spanish_ui_text(translated.strip())
    value = str(item.get(key) or "")
    return spanish_ui_text(value) if locale == "es" else value

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

# The reference catalogue contains long English sample descriptions.  Keep an
# explicit Spanish branch for these public cards instead of applying a word
# substitution to technical prose; this prevents mixed-language sentences and
# keeps the claims bounded to the reviewed sample data.
SAMPLE_ITEMS_ES = {
    "water-cap.jpg": {"alt": "Muestra de tapa de botella de agua de 29/25 mm", "name": "Tapa de botella de agua de 29/25 mm", "description": "Tapa ligera con precinto para botellas de agua mineral y otros envases PET. El anillo de rotura, el sellado interior y la rosca se revisan para el acabado de cuello aprobado.", "mold": "Fabricada con: molde de tapas de agua de alta velocidad de 96 cavidades (modelo SH-W96)", "applications": ["Agua mineral", "Agua saborizada", "Agua con gas", "Botellas PET pequeñas"]},
    "csd-cap.jpg": {"alt": "Muestra de tapa PCO 1881 para bebidas carbonatadas", "name": "Tapa PCO 1881 para bebidas carbonatadas", "description": "Cierre para bebidas presurizadas con banda de precinto profunda y sellado múltiple. El moleteado lateral facilita el agarre y las ranuras de ventilación ayudan a evitar el desprendimiento durante el taponado.", "mold": "Fabricada con: molde de tapas PCO 1881 de alta presión de 72 cavidades (modelo SH-CSD72)", "applications": ["Refrescos", "Zumos con gas", "Agua con gas", "Bebidas energéticas"]},
    "hotfill-cap.jpg": {"alt": "Muestra de tapa hot-fill de 38 mm", "name": "Tapa hot-fill de 38 mm con sellado cónico", "description": "Diseñada para zumos y tés llenados hasta 90 °C. El tapón de sellado, los puntos de rotura y el alojamiento para sello de inducción se ajustan al proceso de llenado en caliente.", "mold": "Fabricada con: molde de tapas hot-fill de 48 cavidades (modelo SH-HF48)", "applications": ["Zumos", "Té frío", "Bebidas deportivas", "Leche saborizada"]},
    "oil-cap.jpg": {"alt": "Muestra de tapa de aceite comestible con anilla", "name": "Tapa de aceite comestible con anilla y vertedor", "description": "Cierre de dos piezas con anilla de precinto y vertedor abatible integrado. La geometría de la bisagra, el sellado y el vertido sin goteo se revisan con el material y el envase del comprador.", "mold": "Fabricada con: molde de tapas de aceite de 32 cavidades con vertedor integrado (modelo SH-OC32)", "applications": ["Aceite de oliva", "Aceite de girasol", "Aceite de soja", "Aceite de colza"]},
    "soysauce-cap.jpg": {"alt": "Muestra de tapa dosificadora para salsa de soja", "name": "Tapa dosificadora para salsa de soja y condimentos", "description": "Tapa abatible compacta con válvula de silicona para abrir con una ligera presión y cerrar sin goteo. El cuerpo transparente, la abertura y la bisagra a presión se ajustan al producto.", "mold": "Fabricada con: molde de tapas dosificadoras para condimentos de 24 cavidades (modelo SH-CD24)", "applications": ["Salsa de soja", "Vinagre", "Kétchup", "Salsa picante"]},
    "pharma-cap.jpg": {"alt": "Muestra de tapa médica resistente a niños", "name": "Tapa farmacéutica resistente a niños con cámara desecante", "description": "Cierre de seguridad que requiere presionar y girar simultáneamente. La cámara desecante, el material médico y los requisitos USP e ISO se confirman con el comprador.", "mold": "Fabricada con: molde de tapas médicas resistentes a niños de 16 cavidades (modelo SH-CR16)", "applications": ["Comprimidos farmacéuticos", "Vitaminas y suplementos", "Tubos efervescentes", "Kits de diagnóstico"]},
    "disc-top-cap.jpg": {"alt": "Muestra de tapa disc-top de alto brillo", "name": "Tapa disc-top de alto brillo para champú", "description": "Cierre de superficie pulida con actuador de presión y retorno silencioso. El acabado de la cavidad y la resistencia al rayado se revisan para el envase de cuidado personal.", "mold": "Fabricada con: molde de tapas disc-top cosméticas de 8 cavidades (modelo SH-CT8)", "applications": ["Champú y acondicionador", "Gel de baño", "Jabón de manos", "Lociones y cremas"]},
    "flip-top-cap.jpg": {"alt": "Muestra de tapa abatible con bisagra integrada", "name": "Tapa abatible con bisagra integrada para productos domésticos", "description": "Tapa abatible con bisagra de larga duración, cierre audible y abertura amplia para líquidos espesos. La superficie superior admite etiquetado o estampado en caliente.", "mold": "Fabricada con: molde de tapas abatibles de 32 cavidades (modelo SH-FT32)", "applications": ["Gel hidroalcohólico", "Lavavajillas", "Champú", "Detergente líquido"]},
    "tamper-evident-cap.jpg": {"alt": "Muestra de tapa con anillo de precinto", "name": "Tapa con anillo de precinto para bebidas", "description": "El anillo visible se separa al abrir el envase y proporciona evidencia inmediata de manipulación. Los puentes y el moleteado se diseñan para líneas de taponado de alta velocidad.", "mold": "Fabricada con: molde de tapas con precinto de 72 cavidades (modelo SH-TE72)", "applications": ["Botellas de zumo", "Botellas de agua", "Botellas de leche", "Tarros de salsa"]},
    "push-pull-cap.jpg": {"alt": "Muestra de tapa deportiva push-pull", "name": "Tapa deportiva push-pull con protección contra polvo", "description": "Cierre para beber con una sola mano sin retirar la tapa. La base rígida, el obturador flexible y la cubierta antipolvo se revisan para un sellado seguro en actividades al aire libre.", "mold": "Fabricada con: molde deportivo bicomponente de 24 cavidades (modelo SH-SC24)", "applications": ["Botellas deportivas", "Botellas de bicicleta", "Botellas de zumo", "Botellas infantiles"]},
    "pull-ring-cap.jpg": {"alt": "Muestra de tapa con anilla de apertura", "name": "Tapa con anilla de apertura para productos lácteos", "description": "Tapa de apertura fácil que rompe la banda al tirar de la anilla. El recorrido de rotura deja un borde seguro y el material HDPE mantiene la resistencia y el sellado.", "mold": "Fabricada con: molde de tapas con anilla de 16 cavidades (modelo SH-PR16)", "applications": ["Botellas de leche", "Bebidas de yogur", "Aceite de oliva", "Tarros de mermelada y salsa"]},
    "two-shot-cap.jpg": {"alt": "Muestra de tapa sobremoldeada de tacto suave", "name": "Tapa sobremoldeada bicomponente de tacto suave", "description": "Cuerpo transparente de PP con sobremoldeado de TPE en la zona de agarre. La unión de materiales y el acabado exterior se ajustan a envases premium y productos de cuidado del automóvil.", "mold": "Fabricada con: molde de sobremoldeo por biinyección de 8 cavidades (modelo SH-BI8)", "applications": ["Cosmética premium", "Botellas de agua de lujo", "Frascos de perfume", "Productos de cuidado del automóvil"]},
    "wide-mouth-cap.jpg": {"alt": "Muestra de tapa para tarro de boca ancha de 110 mm", "name": "Tapa para tarro de boca ancha (110 mm)", "description": "Cierre de gran diámetro para tarros PET de aperitivos, encurtidos y alimentos instantáneos. La rosca profunda, el agarre lateral y el sellado se revisan para aperturas repetidas.", "mold": "Fabricada con: molde de tapas de boca ancha de 12 cavidades (modelo SH-WM12)", "applications": ["Tarros de encurtidos", "Envases de aperitivos", "Tarros de alimentos instantáneos", "Tarros de caramelos y frutos secos"]},
    "squeeze-sports-cap.jpg": {"alt": "Muestra de tapa deportiva de compresión con válvula", "name": "Tapa deportiva de compresión con válvula", "description": "La válvula de silicona dosifica el líquido al comprimir la botella y se cierra al liberar la presión. La base de PP y la válvula se revisan como un conjunto para evitar fugas.", "mold": "Fabricada con: molde de tapas deportivas de compresión de 16 cavidades (modelo SH-SQ16)", "applications": ["Botellas de ciclismo", "Frascos para correr", "Botellas de gimnasio", "Mochilas de hidratación"]},
    "motor-oil-cap.jpg": {"alt": "Muestra de tapa para aceite de motor con vertedor", "name": "Tapa de aceite de motor con vertedor", "description": "Tapa para lubricantes de automoción con vertedor extensible para llenar sin derrames. El HDPE, la banda de precinto y la protección contra polvo se seleccionan para el envase de aceite.", "mold": "Fabricada con: molde de tapas de aceite de motor con vertedor de 24 cavidades (modelo SH-MO24)", "applications": ["Botellas de aceite de motor", "Envases de fluido de transmisión", "Envases de refrigerante", "Garrafas de DEF"]},
    "5-gallon-cap.jpg": {"alt": "Muestra de tapa de garrafón de agua de cinco galones", "name": "Tapa con precinto para garrafón de cinco galones", "description": "Tapa robusta para botellas reutilizables de policarbonato de 18,9 litros. La banda exterior, el sellado interior y la resistencia a los ciclos de sanitización se revisan antes de la entrega.", "mold": "Fabricada con: molde de tapas de agua de cinco galones de 8 cavidades (modelo SH-5G8)", "applications": ["Botellas de dispensador", "Garrafones de agua", "Envases de jarabe", "Almacenamiento de agua a granel"]},
    "bottle-handle.jpg": {"alt": "Muestra de asa para botella de aceite", "name": "Asa integrada para botella de aceite", "description": "Asa ergonómica que encaja en el cuello de botellas de aceite comestible o productos químicos. La geometría, la resistencia y la pestaña de precinto se comprueban con la botella real.", "mold": "Fabricada con: molde de asas para botellas de 32 cavidades (modelo SH-BH32)", "applications": ["Botellas de aceite de 5 L", "Garrafas químicas", "Envases grandes de vinagre", "Botellas de detergente"]},
    "custom-cap.jpg": {"alt": "Muestra de tapa personalizada", "name": "Cierre personalizado: su diseño, nuestro molde", "description": "Referencia de nuestra capacidad para desarrollar cierres a partir de especificaciones del cliente. La rosca, el mecanismo de seguridad, la válvula y la combinación de materiales se definen mediante revisión de ingeniería.", "mold": "Fabricada con: molde totalmente personalizado (cavidades y funciones según su diseño)", "applications": ["Cierres propios", "Tapas multifunción", "Cualquier forma o función", "Volúmenes pequeños y grandes"]},
}

def spanish_sample_items() -> list[dict]:
    rows = []
    for item in SAMPLE_ITEMS:
        row = dict(item)
        translated = SAMPLE_ITEMS_ES.get(str(item.get("image") or ""))
        if translated:
            row.update(translated)
        rows.append(row)
    return rows

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
    {"slug": "case-study-cap-line-expansion-southeast-asia", "title": "Case Study: Supporting a Beverage Manufacturer's Cap Line Expansion in Southeast Asia", "date": "2026/11/20", "image": "/media/page/be686954eb4b9c536d45de2870376df4.webp", "summary": "A practical review of closure tooling, output targets and engineering support for a growing beverage line."},
    {"slug": "cap-mold-demand-growth-global-markets", "title": "Cap Mold Demand Growth in Asia-Pacific, Europe, and North America: Key Drivers and Opportunities", "date": "2026/11/19", "image": "/media/page/63e2d1b48d595c11784ef8b9ad16fb0a.webp", "summary": "The tooling decisions that help packaging makers respond to regional demand and shorter product cycles."},
    {"slug": "global-bottle-cap-mould-market-outlook", "title": "Global Bottle Cap Mould Market Outlook 2026-2032: Regional Demand Analysis", "date": "2026/11/18", "image": "/media/page/48702e17e5e3e48a5faa299c28edc4c9.webp", "summary": "A market-oriented view of high-cavity, lightweight and sustainable closure tooling requirements."},
    {"slug": "reducing-cap-weight-seal-performance", "title": "Case Study: Reducing Cap Weight Without Compromising Seal Performance", "date": "2026/11/13", "image": "/media/page/75b9f3d934eb062e6b0f2e90006860ab.webp", "summary": "How part design, cooling and inspection evidence work together when a closure is lightweighted."},
    {"slug": "micro-conformal-cooling-lightweight-caps", "title": "How Micro-Conformal Cooling Prevents Thin Spots and Gas Permeability", "date": "2026/11/12", "image": "/media/page/cc83af4ddc8f461772bc048a85114609.webp", "summary": "Cooling layout and steel decisions that protect sealing surfaces in thin-wall cap production."},
    {"slug": "ultra-thin-wall-cap-molding", "title": "Ultra-Thin Wall Cap Molding: Cooling Efficiency and Warpage Control", "date": "2026/11/11", "image": "/media/page/5e007052eb9c45715e2c00d364fdf675.webp", "summary": "A checklist for balancing cycle time, dimensional stability and structural integrity."},
    {"slug": "cap-mold-service-life-maintenance", "title": "Case Study: Extending Cap Mold Service Life Through Structured Maintenance", "date": "2026/11/06", "image": "/media/page/24c644d20765717870fa3bad921c728b.webp", "summary": "Maintenance evidence and replacement planning that keep high-cavity tooling production-ready."},
    {"slug": "wear-part-management-high-cavity-caps", "title": "Wear Part Management in High-Cavity Cap Molds", "date": "2026/11/05", "image": "/media/page/7d29be14045b8dec05afec9d094344b5.webp", "summary": "Inspection intervals, interchangeable components and planned replacement for stable uptime."},
    {"slug": "snap-in-bushing-replacement-design", "title": "Snap-In Bushing Replacement Design: Reducing Maintenance Downtime", "date": "2026/11/04", "image": "/media/page/6e0c267ed555cc04b82cb825265f6733.webp", "summary": "A service-friendly component approach for faster changeovers on high-volume lines."},
    {"slug": "running-pcr-content-cap-molds", "title": "Case Study: Running PCR Content Without Seal Lip Quality Degradation", "date": "2026/10/30", "image": "/media/page/3dcda362ede87a732da88a8727f0e751.webp", "summary": "Material variability, runner design and inspection controls for recycled resin programs."},
    {"slug": "larger-runners-recycled-plastics", "title": "How Larger Runners and Gates Improve Recycled Plastic Moldability", "date": "2026/10/29", "image": "/media/page/14b24b801b9d78225732c7a1f56c7420.webp", "summary": "Design considerations that reduce shear and improve repeatability with PCR materials."},
    {"slug": "processing-pcr-hdpe-pp-cap-molds", "title": "Processing PCR HDPE and PP in Cap Molds: Managing Variation", "date": "2026/10/28", "image": "/media/page/74fe329efc19dfcb4d95700cc640ba63.webp", "summary": "A production brief on shrinkage variation, contamination risk and process windows."},
]

MACHINE_NEWS_ITEMS = [
    {"slug": "cooling-water-quality-cap-mold-performance", "title": "The Role of Cooling Water Quality in Cap Mold Performance and Longevity", "titleEs": "El papel de la calidad del agua de refrigeración en el rendimiento y la vida útil del molde de tapas", "date": "2026/07/09", "image": "/media/page/46b0f8965aa376613adb468d666c8e48.webp", "summary": "Water treatment and circuit checks that protect cycle stability and mould life.", "summaryEs": "Tratamiento del agua y comprobaciones de los circuitos para proteger la estabilidad del ciclo y la vida útil del molde."},
    {"slug": "mold-temperature-cap-mechanical-properties", "title": "The Effect of Mold Temperature on Cap Mechanical Properties", "titleEs": "Efecto de la temperatura del molde en las propiedades mecánicas de las tapas", "date": "2026/07/08", "image": "/media/page/efb7a6c796f3658f7e9803cec7df97a4.webp", "summary": "How temperature balance affects shrinkage, stiffness and sealing performance.", "summaryEs": "Cómo el equilibrio térmico afecta la contracción, la rigidez y el rendimiento del sellado."},
    {"slug": "controlling-cap-sink-marks", "title": "Understanding and Controlling Cap Sink Marks", "titleEs": "Cómo entender y controlar las marcas de hundimiento en las tapas", "date": "2026/07/03", "image": "/media/page/da8a5786232ca3d9d9277d62ec5f063c.webp", "summary": "Root causes and practical tooling adjustments for a cleaner top surface.", "summaryEs": "Causas principales y ajustes prácticos del molde para obtener una superficie superior más limpia."},
    {"slug": "injection-speed-cap-quality-cycle-time", "title": "The Impact of Injection Speed on Cap Quality and Cycle Time", "titleEs": "Impacto de la velocidad de inyección en la calidad de las tapas y el tiempo de ciclo", "date": "2026/06/27", "image": "/media/page/6a1505c063d8bbc718fc23621928692d.webp", "summary": "A process window for balancing fill consistency, weld lines and output.", "summaryEs": "Una ventana de proceso para equilibrar el llenado, las líneas de soldadura y la producción."},
    {"slug": "cap-ejection-pin-placement", "title": "The Science of Cap Ejection Pin Placement", "titleEs": "Criterios para colocar los pasadores de expulsión de las tapas", "date": "2026/06/20", "image": "/assets/mould-news-placeholder.svg", "summary": "Ejection layout decisions that avoid deformation and protect cosmetic surfaces.", "summaryEs": "Criterios de distribución que evitan deformaciones y protegen las superficies visibles."},
    {"slug": "integrated-liner-cap-solutions", "title": "Solutions for Caps with Integrated Liners", "titleEs": "Soluciones para tapas con liner integrado", "date": "2026/06/04", "image": "/media/page/5b380918f3eb13dee478c523f109d56e.webp", "summary": "Combining closure geometry, liner placement and downstream assembly requirements.", "summaryEs": "Cómo coordinar la geometría del cierre, la colocación del liner y los requisitos de montaje posteriores."},
    {"slug": "preventing-cap-short-shots", "title": "Preventing Cap Short Shots: Root Cause Analysis and Solutions", "titleEs": "Cómo evitar piezas cortas en tapas: causas y soluciones", "date": "2026/05/30", "image": "/media/page/86324077c14c8902039a0f03d0870d2c.webp", "summary": "A troubleshooting guide covering venting, balance, material and process settings.", "summaryEs": "Guía de diagnóstico sobre ventilación, equilibrado, material y ajustes del proceso."},
    {"slug": "multi-start-thread-cap-design", "title": "An Approach to Caps with Multi-Start Threads", "titleEs": "Criterios de diseño para tapas con roscas de varias entradas", "date": "2026/05/27", "image": "/media/page/b1c23b277d5e2f5ab0577fe5ecaaea2d.webp", "summary": "Thread-start alignment and mould details for fast, reliable capping.", "summaryEs": "Alineación de las entradas de rosca y detalles del molde para un taponado rápido y fiable."},
    {"slug": "linerless-vs-liner-based-sealing", "title": "The Science of Cap Sealing: Linerless vs. Liner-Based Designs", "titleEs": "Sellado de tapas: diseños sin liner frente a diseños con liner", "date": "2026/05/22", "image": "/media/page/456fd5eb3ea438b47edb24a541324c81.webp", "summary": "A comparison of sealing architectures, inspection points and tooling implications.", "summaryEs": "Comparación de arquitecturas de sellado, puntos de inspección e implicaciones para el molde."},
    {"slug": "zero-defect-cap-production-quality-system", "title": "Quality Management for Zero-Defect Cap Production", "titleEs": "Gestión de calidad para producir tapas sin defectos", "date": "2026/05/15", "image": "/media/page/0e504923549734a620c583a4dba3ac10.webp", "summary": "How documented checks connect mould trials, dimensional control and production release.", "summaryEs": "Cómo los controles documentados conectan las pruebas del molde, el control dimensional y la liberación de producción."},
    {"slug": "managing-cap-shrinkage", "title": "Managing Cap Shrinkage from Mold Design to Production", "titleEs": "Control de la contracción de las tapas desde el diseño del molde hasta la producción", "date": "2026/05/08", "image": "/assets/mould-news-placeholder.svg", "summary": "Material, cooling and measurement controls for predictable cap dimensions.", "summaryEs": "Controles de material, refrigeración y medición para obtener dimensiones previsibles."},
    {"slug": "zero-defect-cap-sealing-surfaces", "title": "Achieving Zero-Defect Cap Sealing Surfaces", "titleEs": "Cómo lograr superficies de sellado de tapas sin defectos", "date": "2026/05/01", "image": "/media/page/4615de874a47d710336a20072fc3760f.webp", "summary": "A practical inspection sequence for threads, plugs and sealing lips.", "summaryEs": "Secuencia práctica de inspección para roscas, tapones y labios de sellado."},
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
CAP_MOULD_SERIES = sorted(CATALOG["categories"], key=lambda item: (CAP_MOULD_ORDER.index(item["slug"]) if item.get("slug") in CAP_MOULD_ORDER else 1000, str(item.get("slug") or "")))

def header(locale: str, route: str) -> str:
    # Keep the desktop navigation aligned with the reference: the Cap Mould
    # label opens the aggregate page, while the caret exposes every item in
    # the canonical 13-family catalogue (the same source used by the footer
    # and the product grid).
    product_items = product_navigation_items()
    product_links = ''.join('<a href="' + localized_href(locale, item["route"]) + '">' + esc(navigation_label(item["route"], catalog_text(locale, item, "navTitle") or catalog_text(locale, item, "title"), locale)) + '</a>' for item in product_items)
    nav = ['<a class="nav__link" href="' + local_link(locale, "/") + '">' + esc(text(locale, "home")) + '</a>']
    about_menu = '<div class="nav__drop"><button class="nav__toggle" data-mega-toggle type="button" aria-controls="menu-about" aria-expanded="false">' + esc(text(locale, "about")) + '<svg class="chevron" viewBox="0 0 24 24" aria-hidden="true"><path d="m5 9 7 7 7-7"/></svg></button><div class="mini-menu" id="menu-about"><a href="' + localized_href(locale, "/about/") + '">' + esc(navigation_label("/about/", text(locale, "about"), locale)) + '</a><a href="' + localized_href(locale, "/faq/") + '">' + esc(navigation_label("/faq/", text(locale, "faq_title"), locale)) + '</a></div></div>'
    cap_nav_label = "Cap mold" if locale == "en" else text(locale, "cap_mould")
    cap_menu_aria = "Abrir menú de moldes de tapas" if locale == "es" else "Open Cap Mould menu"
    news_menu_aria = "Abrir menú de noticias" if locale == "es" else "Open News menu"
    product_menu = '<div class="nav__drop nav__drop--products"><a class="nav__link nav__link--direct" href="' + localized_href(locale, "/Plastic-cap-mold.html") + '">' + esc(cap_nav_label) + '</a><button class="nav__toggle nav__toggle--caret" data-mega-toggle type="button" aria-label="' + esc(cap_menu_aria) + '" aria-controls="menu-products" aria-expanded="false"><svg class="chevron" viewBox="0 0 24 24" aria-hidden="true"><path d="m5 9 7 7 7-7"/></svg></button><div class="mini-menu" id="menu-products">' + product_links + '</div></div>'
    nav.append(about_menu)
    nav.append(product_menu)
    nav.append('<a class="nav__link" href="' + localized_href(locale, "/capabilities/") + '">' + esc(navigation_label("/capabilities/", text(locale, "machine"), locale)) + '</a>')
    sample_label = navigation_label("/samples/", "Sample" if locale == "en" else text(locale, "samples"), locale)
    nav.append('<a class="nav__link" href="' + localized_href(locale, "/samples/") + '">' + esc(sample_label) + '</a>')
    resources_menu = '<div class="nav__drop nav__drop--resources"><a class="nav__link nav__link--direct" href="' + localized_href(locale, "/news/") + '">' + esc(navigation_label("/news/", text(locale, "news"), locale)) + '</a><button class="nav__toggle nav__toggle--caret" data-mega-toggle type="button" aria-label="' + esc(news_menu_aria) + '" aria-controls="menu-resources" aria-expanded="false"><svg class="chevron" viewBox="0 0 24 24" aria-hidden="true"><path d="m5 9 7 7 7-7"/></svg></button><div class="mini-menu" id="menu-resources"><a href="' + localized_href(locale, "/news/Bottle-cap-molds.html") + '">' + esc(navigation_label("/news/Bottle-cap-molds.html", "Bottle cap molds", locale)) + '</a><a href="' + localized_href(locale, "/Bottle-Cap-Machine/Bottle-Cap-Machine.html") + '">' + esc(navigation_label("/Bottle-Cap-Machine/Bottle-Cap-Machine.html", "Bottle Cap Machine", locale)) + '</a></div></div>'
    nav.append(resources_menu)
    nav.append('<a class="nav__link" href="' + localized_href(locale, "/video/") + '">' + esc(text(locale, "video")) + '</a>')
    nav.append('<a class="nav__link" href="' + localized_href(locale, "/contact/") + '">' + esc(text(locale, "contact_us")) + '</a>')
    mobile = '<a href="' + local_link(locale, "/") + '">' + esc(text(locale, "home")) + '</a><a href="' + localized_href(locale, "/about/") + '">' + esc(text(locale, "about")) + '</a><a href="' + localized_href(locale, "/capabilities/") + '">' + esc(text(locale, "machine")) + '</a><a href="' + localized_href(locale, "/samples/") + '">' + esc(sample_label) + '</a><a href="' + localized_href(locale, "/video/") + '">' + esc(text(locale, "video")) + '</a><a href="' + localized_href(locale, "/contact/") + '">' + esc(text(locale, "contact_us")) + '</a>'
    news_category_label = "categorías de noticias" if locale == "es" else "categories"
    bottle_news_label = "Noticias sobre moldes de tapas" if locale == "es" else "Bottle cap molds"
    bottle_machine_label = "Máquinas para tapas de botella" if locale == "es" else "Bottle Cap Machine"
    mobile += '<details><summary>' + esc(text(locale, "cap_mould")) + '</summary>' + product_links + '</details><a href="' + localized_href(locale, "/news/") + '">' + esc(text(locale, "news")) + '</a><details><summary>' + esc(text(locale, "news")) + ' ' + news_category_label + '</summary><a href="' + localized_href(locale, "/news/Bottle-cap-molds.html") + '">' + bottle_news_label + '</a><a href="' + localized_href(locale, "/Bottle-Cap-Machine/Bottle-Cap-Machine.html") + '">' + bottle_machine_label + '</a></details>'
    options = ''.join('<option value="' + esc(route_for(lang["code"], route)) + '"' + (' selected' if lang["code"] == locale else '') + '>' + esc(lang["nativeName"]) + '</option>' for lang in LOCALES)
    phone_digits = re.sub(r"[^0-9+]", "", WHATSAPP)
    logo = '<a href="' + local_link(locale, "/") + '" class="logo" aria-label="' + esc(BRAND_DISPLAY) + ' home"><img class="logo__image" src="' + esc(LOGO_SRC) + '" alt="' + esc(LOGO_ALT) + '" width="260" height="51" decoding="async"></a>'
    choose_language = "Elegir idioma" if locale == "es" else "Choose language"
    search_label = "Buscar productos" if locale == "es" else "Search products"
    open_menu = "Abrir menú" if locale == "es" else "Open menu"
    menu_label = "Menú" if locale == "es" else "Menu"
    search_placeholder = "Buscar categoría de molde o aplicación…" if locale == "es" else "Search mould category or application…"
    search_submit = "Buscar →" if locale == "es" else "Search →"
    actions = '<div class="header__actions"><a class="nav-phone-desktop" href="tel:' + esc(phone_digits) + '"><span class="phone-text">' + esc(WHATSAPP) + '</span><span class="phone-icon-wrap"><svg class="phone-icon-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M6.62 10.79a15.05 15.05 0 006.59 6.59l2.2-2.2a1 1 0 011.01-.24 11.36 11.36 0 003.58.57 1 1 0 011 1V20a1 1 0 01-1 1A17 17 0 013 4a1 1 0 011-1h3.5a1 1 0 011 1 11.36 11.36 0 00.57 3.58 1 1 0 01-.25 1.01l-2.2-2.2z" fill="currentColor"></path></svg></span></a><select class="language-switch" data-language-switch aria-label="' + esc(choose_language) + '">' + options + '</select><button class="icon-button" id="search-toggle" aria-label="' + esc(search_label) + '" aria-expanded="false" type="button"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m16 16 5 5"/></svg></button><a class="button header__quote" href="' + localized_href(locale, "/contact/#inquiry") + '">' + esc(text(locale, "quote")) + '</a><button class="icon-button menu-button" id="mobile-menu" aria-label="' + esc(open_menu) + '" aria-expanded="false" aria-controls="mobile-navigation"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg><span class="menu-label">' + esc(menu_label) + '</span></button></div>'
    search = '<div id="search-panel" class="search-panel"><form class="shell search-panel__form" action="' + localized_href(locale, "/products/") + '" method="get"><input type="search" name="q" placeholder="' + esc(search_placeholder) + '" aria-label="' + esc(search_placeholder.rstrip("…")) + '"><button class="button" type="submit">' + esc(search_submit) + '</button></form></div>'
    top_left = '<div class="top-bar-left"><a href="mailto:' + esc(EMAIL) + '" class="info-item" title="Email us"><span class="info-icon">' + topbar_icon("email") + '</span><span>' + esc(EMAIL) + '</span></a><span class="info-separator"></span><a href="tel:' + esc(phone_digits) + '" class="info-item" title="Call us"><span class="info-icon">' + topbar_icon("phone") + '</span><span>' + esc(WHATSAPP) + '</span></a><span class="info-separator"></span><span class="info-item" title="Our address"><span class="info-icon">' + topbar_icon("pin") + '</span><span>' + esc(ADDRESS) + '</span></span></div>'
    top_right = '<div class="top-bar-right"><a href="' + esc(SOCIAL_URLS["tiktok"]) + '" target="_blank" rel="noopener noreferrer" class="social-link tiktok" title="TikTok" aria-label="TikTok">' + topbar_icon("tiktok") + '</a><a href="' + esc(SOCIAL_URLS["youtube"]) + '" target="_blank" rel="noopener noreferrer" class="social-link youtube" title="YouTube" aria-label="YouTube">' + topbar_icon("youtube") + '</a><a href="' + esc(SOCIAL_URLS["facebook"]) + '" target="_blank" rel="noopener noreferrer" class="social-link facebook" title="Facebook" aria-label="Facebook">' + topbar_icon("facebook") + '</a></div>'
    top = '<div class="topbar top-bar" id="topBar"><div class="shell topbar__inner top-bar-inner">' + top_left + top_right + '</div></div>'
    return render_template("header", TOPBAR=top, LOGO=logo, NAV_DESKTOP=''.join(nav), ACTIONS=actions, SEARCH=search, NAV_MOBILE=mobile)

def footer(locale: str) -> str:
    links = ''.join('<p><a href="' + localized_href(locale, item["route"]) + '">' + esc(navigation_label(item["route"], catalog_text(locale, item, "title"), locale)) + '</a></p>' for item in product_navigation_items())
    quick = ''.join('<p><a href="' + localized_href(locale, route) + '">' + esc(label) + '</a></p>' for label, route in ((text(locale, "about"), "/about/"), (text(locale, "samples"), "/samples/"), (text(locale, "video"), "/video/"), (text(locale, "news"), "/news/"), (text(locale, "faq_title"), "/faq/"), (text(locale, "contact_us"), "/contact/")))
    footer_config = BRAND_CONFIG.get("footer", {}) if isinstance(BRAND_CONFIG, dict) else {}
    footer_logo = (BRAND_CONFIG.get("logos", {}).get("footer", {}) if isinstance(BRAND_CONFIG, dict) else {})
    footer_logo_src = str(footer_logo.get("src") or LOGO_SRC)
    footer_logo_alt = str(footer_logo.get("alt") or LOGO_ALT)
    footer_logo = '<a class="footer__logo" href="' + esc(localized_href(locale, "/")) + '" aria-label="' + esc(BRAND_DISPLAY + " home") + '"><img class="footer__logo-image" src="' + esc(footer_logo_src) + '" alt="' + esc(footer_logo_alt) + '" width="260" height="51" loading="lazy" decoding="async"></a>'
    footer_email = str(_brand_contact.get("email") or EMAIL)
    footer_wa_url = WA_URL
    footer_copy = str(footer_config.get("copyright") or ("© 2026 " + BRAND_DISPLAY))
    footer_about = str(footer_config.get("about") or text(locale, "footer_tagline"))
    footer_contact_heading = str(footer_config.get("contactHeading") or text(locale, "footer_contact"))
    if locale == "es":
        footer_about = spanish_ui_text(footer_about)
        footer_contact_heading = spanish_ui_text(footer_contact_heading)
    vals = {"PRODUCT_LINKS": links, "QUICK_LINKS": quick, "WHATSAPP_NUMBER": esc(WHATSAPP), "FOOTER_EYEBROW": esc(text(locale, "footer_eyebrow")), "FOOTER_CTA_TITLE": esc(text(locale, "footer_cta_title")), "FOOTER_CTA_TEXT": esc(text(locale, "footer_cta_text")), "FOOTER_CTA_BUTTON": esc(text(locale, "quote")), "FOOTER_TAGLINE": esc(footer_about), "FOOTER_ADDRESS": esc(ADDRESS), "FOOTER_PRODUCTS_TITLE": esc(text(locale, "footer_products")), "FOOTER_CONTACT_TITLE": esc(footer_contact_heading), "FOOTER_QUOTE": esc(text(locale, "footer_quote")), "FOOTER_PRIVACY": esc(text(locale, "footer_privacy")), "FOOTER_STICKY": esc(text(locale, "footer_sticky")), "FOOTER_EMAIL_LABEL": esc("CORREO" if locale == "es" else "EMAIL"), "FOOTER_WHATSAPP_LABEL": esc("WHATSAPP"), "FOOTER_INQUIRY_LABEL": esc("CONSULTA" if locale == "es" else "INQUIRY")}
    vals.update({"FOOTER_LOGO": footer_logo, "FOOTER_EMAIL": esc(footer_email), "FOOTER_WA_URL": esc(footer_wa_url), "FOOTER_CONTACT_HREF": esc(localized_href(locale, "/contact/#inquiry")), "FOOTER_HOME_HREF": esc(localized_href(locale, "/")), "FOOTER_PRIVACY_HREF": esc(localized_href(locale, "/privacy-policy/")), "FOOTER_SITE_URL": esc(ORIGIN + localized_href(locale, "/")), "FOOTER_COPYRIGHT": esc(footer_copy), "FOOTER_QUICK_LINKS": esc(text(locale, "footer_quick_links")), "FOOTER_SITEMAP": esc(text(locale, "footer_sitemap"))})
    return render_template("footer", **vals)

def _product_item_for_route(route: str) -> dict | None:
    """Return the D1-backed product-family row for a canonical route.

    Product-family pages are not SKU detail pages.  The row is still the
    authoritative source for the family slug and approved hero image, so the
    structured data must not fall back to the generic About image.
    """
    slug = product_slug_for_route(str(route or ""))
    if not slug:
        return None
    return next((item for item in CATALOG.get("categories", [])
                 if isinstance(item, dict) and str(item.get("slug") or "").strip().lower() == slug), None)


def _product_image_url(item: dict | None) -> str:
    """Resolve a product-family image without inventing or borrowing a SKU."""
    if not isinstance(item, dict):
        return ""
    path = str(item.get("image") or "").strip()
    if not path:
        structured = item.get("categoryCopy") if isinstance(item.get("categoryCopy"), dict) else {}
        hero = structured.get("hero") if isinstance(structured.get("hero"), dict) else {}
        path = str(hero.get("image") or "").strip()
    if not path:
        return ""
    if path.startswith(("https://", "http://")):
        return path if path.startswith(ORIGIN + "/") else ""
    if path.startswith(("/media/", "/assets/")):
        return ORIGIN + path
    # Legacy reference paths are resolved only through the reviewed media map;
    # an unmapped path is deliberately rejected so Product schema never labels
    # a source-site image as a LEYA-owned upload.
    # The checked-in media manifest is keyed by the reference origin, not the
    # LEYA public origin.  Resolve that reviewed source path before allowing
    # it into Product/OG schema; never fall back to the generic About image.
    mapped = LEGACY_MEDIA_MAP.get(path) or LEGACY_MEDIA_MAP.get("https://www.cap-molds.com" + (path if path.startswith("/") else "/" + path))
    if mapped and str(mapped).startswith(("/media/", "/assets/")):
        return ORIGIN + str(mapped)
    return ""


def _absolute_social_image(route: str) -> str:
    product_item = _product_item_for_route(route)
    product_image = _product_image_url(product_item)
    if product_image:
        return product_image
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


def _product_faq_pairs(item: dict | None, locale: str) -> list[tuple[str, str]]:
    if not isinstance(item, dict):
        return []
    field = "faqsEs" if locale == "es" else "faqs"
    rows = item.get(field)
    if not isinstance(rows, list):
        return []
    result = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        question = str(row.get("question") or "").strip()
        answer = str(row.get("answer") or "").strip()
        if locale == "es":
            question, answer = spanish_ui_text(question), spanish_ui_text(answer)
        if len(question) >= 8 and len(answer) >= 15:
            result.append((question, answer))
    return result[:8]


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
        item = _product_item_for_route(route)
        product_id = canonical + "#product"
        product_image = _product_image_url(item) or image_url
        product = {
            "@type": "Product",
            "@id": product_id,
            "name": title,
            "description": description,
            "url": canonical,
            "image": [product_image],
            "inLanguage": locale,
            "brand": {"@type": "Brand", "name": BRAND_DISPLAY},
            "category": str((item or {}).get("titleEs" if locale == "es" else "title") or (item or {}).get("title") or "Plastic mould tooling"),
        }
        if not product_image:
            product.pop("image", None)
        page["mainEntity"] = {"@id": product_id}
        if product_image:
            page["primaryImageOfPage"] = {"@type": "ImageObject", "url": product_image}
        faq_pairs = _product_faq_pairs(item, locale)
        if faq_pairs:
            graph.append(product)
            graph.append({
                "@type": "FAQPage",
                "@id": canonical + "#faq",
                "url": canonical,
                "inLanguage": locale,
                "mainEntity": [
                    {"@type": "Question", "name": question,
                     "acceptedAnswer": {"@type": "Answer", "text": answer}}
                    for question, answer in faq_pairs
                ],
            })
        else:
            graph.append(product)
    elif detail and detail.group(1) in EDITORIAL_BY_SLUG:
        editorial = EDITORIAL_BY_SLUG[detail.group(1)]
        page["author"] = {"@type": "Organization", "name": BRAND_DISPLAY}
        page["datePublished"] = str(editorial.get("date") or "").replace("/", "-")
        page["dateModified"] = editorial.get("lastReviewed")
        page["headline"] = title
        page["image"] = [image_url]
    graph.append(page)
    crumbs = [{"@type": "ListItem", "position": 1, "name": text(locale, "home"), "item": ORIGIN + route_for(locale, "/")}]
    if route != "/":
        if route.startswith("/product/"):
            crumbs.append({"@type": "ListItem", "position": 2, "name": text(locale, "products"), "item": ORIGIN + route_for(locale, "/products/")})
            crumbs.append({"@type": "ListItem", "position": 3, "name": title, "item": canonical})
        else:
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
    base = render_template("head", TITLE=esc(title), DESCRIPTION=esc(description)[:240], ASSET_VERSION="mould-v55")
    if route.startswith("/product/"):
        base = base.replace('</head>', '<link rel="stylesheet" href="/assets/mould-category.css?v=mould-detail-8"></head>', 1)
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
    # Match cap-molds' filled Font Awesome silhouettes and order: WhatsApp,
    # WeChat, then the orange phone action. Inline SVG keeps this independent
    # from a CDN while preserving the same icon geometry.
    phone = '<a href="tel:' + esc(phone_digits) + '" class="rail-float rail-float--phone" title="Call us" aria-label="Call us"><svg viewBox="0 0 512 512" aria-hidden="true"><path d="M164.9 24.6c-7.7-18.6-28-28.5-47.4-23.2l-88 24C12.1 30 0 46 0 64 0 311.4 200.6 512 448 512c18 0 33.8-12.1 38.6-29.5l24-88c5.3-19.4-4.6-39.7-23.2-47.4l-96-40c-16.3-6.8-35.2-2.1-46.3 11.6L304.7 368C234.3 334.7 177.3 277.7 144 207.3L193.3 167c13.7-11.2 18.4-30 11.6-46.3l-40-96z"/></svg><span class="floating-tooltip">Call</span></a>'
    whatsapp = '<a href="' + WA_URL + '" target="_blank" rel="noopener noreferrer" class="rail-float rail-float--whatsapp" title="Chat on WhatsApp" aria-label="Chat on WhatsApp"><svg viewBox="0 0 448 512" aria-hidden="true"><path d="M380.9 97.1C339 55.1 283.2 32 223.9 32c-122.4 0-222 99.6-222 222 0 39.1 10.2 77.3 29.6 111L0 480l117.7-30.9c32.4 17.7 68.9 27 106.1 27h.1c122.3 0 224.1-99.6 224.1-222 0-59.3-25.2-115-67.1-157zm-157 341.6c-33.2 0-65.7-8.9-94-25.7l-6.7-4-69.8 18.3L72 359.2l-4.4-7c-18.5-29.4-28.2-63.3-28.2-98.2 0-101.7 82.8-184.5 184.6-184.5 49.3 0 95.6 19.2 130.4 54.1 34.8 34.9 56.2 81.2 56.1 130.5 0 101.8-84.9 184.6-186.6 184.6zm101.2-138.2c-5.5-2.8-32.8-16.2-37.9-18-5.1-1.9-8.8-2.8-12.5 2.8-3.7 5.6-14.3 18-17.6 21.8-3.2 3.7-6.5 4.2-12 1.4-32.6-16.3-54-29.1-75.5-66-5.7-9.8 5.7-9.1 16.3-30.3 1.8-3.7.9-6.9-.5-9.7-1.4-2.8-12.5-30.1-17.1-41.2-4.5-10.8-9.1-9.3-12.5-9.5-3.2-.2-6.9-.2-10.6-.2-3.7 0-9.7 1.4-14.8 6.9-5.1 5.6-19.4 19-19.4 46.3 0 27.3 19.9 53.7 22.6 57.4 2.8 3.7 39.1 59.7 94.8 83.8 35.2 15.2 49 16.5 66.6 13.9 10.7-1.6 32.8-13.4 37.4-26.4 4.6-13 4.6-24.1 3.2-26.4-1.3-2.5-5-3.9-10.5-6.6z"/></svg><span class="floating-tooltip">WhatsApp</span></a>'
    wechat = '<a href="' + localized_href(locale, "/contact/") + '" class="rail-float rail-float--wechat" title="WeChat contact" aria-label="WeChat contact"><svg viewBox="0 0 576 512" aria-hidden="true"><path d="M385.2 167.6c6.4 0 12.6.3 18.8 1.1C387.4 90.3 303.3 32 207.7 32 100.5 32 13 104.8 13 197.4c0 53.4 29.3 97.5 77.9 131.6l-19.3 58.6 68-34.1c24.4 4.8 43.8 9.7 68.2 9.7 6.2 0 12.1-.3 18.3-.8-4-12.9-6.2-26.6-6.2-40.8-.1-84.9 72.9-154 165.3-154zm-104.5-52.9c14.5 0 24.2 9.7 24.2 24.4 0 14.5-9.7 24.2-24.2 24.2-14.8 0-29.3-9.7-29.3-24.2.1-14.7 14.6-24.4 29.3-24.4zm-136.4 48.6c-14.5 0-29.3-9.7-29.3-24.2 0-14.8 14.8-24.4 29.3-24.4 14.8 0 24.4 9.7 24.4 24.4 0 14.6-9.6 24.2-24.4 24.2zM563 319.4c0-77.9-77.9-141.3-165.4-141.3-92.7 0-165.4 63.4-165.4 141.3S305 460.7 397.6 460.7c19.3 0 38.9-5.1 58.6-9.9l53.4 29.3-14.8-48.6C534 402.1 563 363.2 563 319.4zm-219.1-24.5c-9.7 0-19.3-9.7-19.3-19.6 0-9.7 9.7-19.3 19.3-19.3 14.8 0 24.4 9.7 24.4 19.3 0 10-9.7 19.6-24.4 19.6zm107.1 0c-9.7 0-19.3-9.7-19.3-19.6 0-9.7 9.7-19.3 19.3-19.3 14.5 0 24.4 9.7 24.4 19.3.1 10-9.9 19.6-24.4 19.6z"/></svg><span class="floating-tooltip">WeChat</span></a>'
    if locale == "es":
        phone = phone.replace('title="Call us"', 'title="Llamar"').replace('aria-label="Call us"', 'aria-label="Llamar"').replace('>Call</span>', '>Llamar</span>')
        whatsapp = whatsapp.replace('title="Chat on WhatsApp"', 'title="Chat por WhatsApp"').replace('aria-label="Chat on WhatsApp"', 'aria-label="Chat por WhatsApp"')
        wechat = wechat.replace('title="WeChat contact"', 'title="Contacto por WeChat"').replace('aria-label="WeChat contact"', 'aria-label="Contacto por WeChat"')
    rail_label = "Contacto rápido" if locale == "es" else "Quick contact"
    return '<aside class="rail" role="complementary" aria-label="' + esc(rail_label) + '">' + whatsapp + wechat + phone + '</aside>'

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
    banner_src = banner if banner.startswith("/assets/") else legacy_media_url(banner)
    page_header_mod = " reference-page-header--samples" if route == "/samples/" else ""
    structured_eyebrow = structured_page_value(locale, route, "eyebrow", "")
    structured_title = structured_page_value(locale, route, "title", "")
    structured_subtitle = structured_page_value(locale, route, "subtitle", "")
    if route == "/capabilities/":
        page_eyebrow = "EQUIPOS AUXILIARES" if locale == "es" else "AUXILIARY EQUIPMENT"
        page_title = ("Máquinas auxiliares para <span class=\"reference-title-accent\">tapas</span>" if locale == "es" else "Cap <span class=\"reference-title-accent\">Auxiliary Machines</span>")
    elif route == "/video/":
        page_eyebrow = "EXPLORE NUESTRO TRABAJO" if locale == "es" else "EXPLORE OUR WORK"
        page_title = "Video <span class=\"reference-title-accent\">Gallery</span>" if locale == "en" else "Galería de <span class=\"reference-title-accent\">vídeos</span>"
    elif route == "/about/":
        page_eyebrow = "OUR STORY" if locale == "en" else "NUESTRA HISTORIA"
        page_title = ("About <span class=\"reference-title-accent\">LEYA MOULD</span>" if locale == "en" else "Sobre <span class=\"reference-title-accent\">LEYA MOULD</span>")
    else:
        page_eyebrow = "LEYA MOULD · UTILLAJE DE PRECISIÓN" if locale == "es" else "LEYA MOULD · PRECISION TOOLING"
        page_title = esc(title)
    if structured_eyebrow:
        page_eyebrow = structured_eyebrow
    if structured_title:
        page_title = esc(structured_title)
    if structured_subtitle:
        subtitle = structured_subtitle
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


# One shared CTA component is used by the catalogue, sample, machine, About,
# FAQ and every dedicated product page.  The copy varies by page purpose, but
# the DOM, contact actions and accessibility labels stay identical so a CMS
# edit cannot make one route drift away from the others.
SHARED_CTA_COPY = {
    "catalog": {
        "en": ("Start Your Cap Mould Project", "Send your drawing, sample or production requirements. We will reply with the next technical questions and a clear path forward.", "Contact us for a quote and technical consultation — we will reply within 24 hours."),
        "es": ("Empiece su proyecto de moldes", "Envíenos su dibujo, muestra o requisitos de producción. Responderemos con las siguientes preguntas técnicas y un camino claro.", "Contáctenos para una cotización y consulta técnica; responderemos en 24 horas."),
    },
    "samples": {
        "en": ("Want to See More Samples or Request a Quote?", "Contact LEYA MOULD today. We will send you the right samples and a practical proposal for your project.", "Tell us about your mould"),
        "es": ("¿Quiere ver más muestras o solicitar una cotización?", "Contacte hoy con LEYA MOULD. Le enviaremos las muestras adecuadas y una propuesta práctica para su proyecto.", "Cuéntenos sobre su molde"),
    },
    "auxiliary": {
        "en": ("Need Auxiliary Equipment for Your Cap Line?", "Contact LEYA MOULD to discuss your cap size, production volume and the auxiliary operations you require. We will recommend a practical machine setup for your factory.", "Tell us about your line"),
        "es": ("¿Necesita equipos auxiliares para su línea de tapas?", "Contacte con LEYA MOULD para hablar del tamaño de la tapa, el volumen de producción y las operaciones auxiliares que necesita. Le recomendaremos una configuración práctica.", "Cuéntenos sobre su línea"),
    },
    "about": {
        "en": ("Let's Work Together", "Share your drawing, sample or production brief and we will help shape the next technical step.", "Chat with LEYA MOULD"),
        "es": ("Trabajemos juntos", "Comparta su plano, muestra o requisitos de producción y le ayudaremos a definir el siguiente paso técnico.", "Hable con LEYA MOULD"),
    },
    "faq": {
        "en": ("Still Have Questions?", "Our team is ready to help. Reach out and we'll respond within 24 hours.", "Ask about your project"),
        "es": ("¿Todavía tiene preguntas?", "Nuestro equipo está listo para ayudarle. Escríbanos y responderemos en un plazo de 24 horas.", "Consulte su proyecto"),
    },
    "category": {
        "en": ("Start Your Cap Mould Project", "Send us your drawing, sample, target material, cavity plan and delivery market. We will reply with the next technical questions.", "Tell us about your mould"),
        "es": ("Inicie su proyecto de moldes", "Envíenos el plano, la muestra, el material, las cavidades y el mercado de destino. Responderemos con las siguientes preguntas técnicas.", "Cuéntenos sobre su molde"),
    },
}


def shared_cta(locale: str, variant: str = "catalog", element_id: str = "", title_override: str = "", text_override: str = "") -> str:
    """Render the canonical contact CTA used at the bottom of public pages."""
    lang = "es" if locale == "es" else "en"
    fallback = SHARED_CTA_COPY.get(variant, SHARED_CTA_COPY["catalog"]).get(lang, SHARED_CTA_COPY["catalog"][lang])
    d1_locale = COMMON_COPY.get(lang, {}) if isinstance(COMMON_COPY.get(lang, {}), dict) else {}
    d1_ctas = d1_locale.get("shared_cta", {}) if isinstance(d1_locale.get("shared_cta", {}), dict) else {}
    d1_copy = d1_ctas.get(variant) if isinstance(d1_ctas.get(variant), dict) else {}
    if STRICT_D1 and any(not str(d1_copy.get(key) or "").strip() for key in ("title", "description", "note")):
        raise RuntimeError("Strict D1 shared CTA missing for " + lang + ":" + variant)
    copy = (
        str(d1_copy.get("title") or fallback[0]),
        str(d1_copy.get("description") or fallback[1]),
        str(d1_copy.get("note") or fallback[2]),
    )
    if lang == "es":
        copy = tuple(spanish_ui_text(value) for value in copy)
    title = title_override or copy[0]
    description = text_override or copy[1]
    id_attr = ' id="' + esc(element_id) + '"' if element_id else ""
    quote_label = str(d1_copy.get("quoteLabel") or ("Solicitar cotización" if lang == "es" else "Request a Quote"))
    phone_label = str(d1_copy.get("phoneLabel") or ("Teléfono / WhatsApp" if lang == "es" else "Phone / WhatsApp"))
    email_label = str(d1_copy.get("emailLabel") or ("Correo electrónico" if lang == "es" else "Email"))
    whatsapp_label = str(d1_copy.get("whatsappLabel") or "WhatsApp")
    eyebrow = str(d1_copy.get("eyebrow") or ("LEYA MOULD · INGENIERÍA · SOPORTE" if lang == "es" else "LEYA MOULD · ENGINEERING · SUPPORT"))
    if lang == "es":
        quote_label, phone_label, email_label, whatsapp_label, eyebrow = tuple(spanish_ui_text(value) for value in (quote_label, phone_label, email_label, whatsapp_label, eyebrow))
    return (
        '<section' + id_attr + ' class="mould-shared-cta mould-shared-cta--' + esc(variant) + '">'
        '<div class="mould-shared-cta__inner">'
        '<div class="mould-shared-cta__copy"><span class="mould-shared-cta__eyebrow">' + esc(eyebrow) + '</span>'
        '<h2><span aria-hidden="true">✦</span> ' + esc(title) + '</h2><p>' + esc(description) + '</p></div>'
        '<div class="mould-shared-cta__actions">'
        '<a class="mould-shared-cta__item mould-shared-cta__item--phone" href="tel:+8613606727715"><span class="mould-shared-cta__icon" aria-hidden="true">☎</span><span><strong>' + phone_label + '</strong><small>+86 136 0672 7715</small></span></a>'
        '<a class="mould-shared-cta__item" href="mailto:' + esc(EMAIL) + '"><span class="mould-shared-cta__icon" aria-hidden="true">✉</span><span><strong>' + email_label + '</strong><small>' + esc(EMAIL) + '</small></span></a>'
        '<a class="mould-shared-cta__item mould-shared-cta__item--whatsapp" href="' + esc(WA_URL) + '" target="_blank" rel="noopener"><span class="mould-shared-cta__icon" aria-hidden="true">↗</span><span><strong>' + whatsapp_label + '</strong><small>' + esc(copy[2]) + '</small></span></a>'
        '<a class="mould-shared-cta__button" href="' + localized_href(locale, "/contact/#inquiry") + '">' + esc(quote_label) + ' <span aria-hidden="true">→</span></a>'
        '</div></div></section>'
    )

def _review_rows(locale: str, model: str | None = None) -> list[dict]:
    """Return only explicitly published D1 reviews with real text."""
    rows = []
    for raw in STATE.get("productReviews", []):
        if not isinstance(raw, dict) or str(raw.get("status") or "").lower() != "published":
            continue
        if model and str(raw.get("model") or "").strip().lower() != str(model).strip().lower():
            continue
        content = raw.get("content") if isinstance(raw.get("content"), dict) else raw
        quote = str(content.get("quote") or content.get("content") or "").strip()
        author = str(content.get("author") or "").strip()
        if not quote or not author:
            continue
        if locale == "es":
            # Never present an English review as a completed Spanish
            # translation.  Only the explicitly reviewed Spanish fields are
            # eligible for the Spanish page; otherwise the review stays out of
            # the public locale until its translation is approved.
            quote = str(content.get("quoteEs") or content.get("contentEs") or "").strip()
            author = str(content.get("authorEs") or "").strip()
            if not quote or not author:
                continue
            quote, author = spanish_ui_text(quote), spanish_ui_text(author)
        rows.append({"quote": quote, "author": author, "company": str(content.get("company") or "").strip()})
    return rows[:12]

def home(locale: str) -> str:
    cap = "https://www.cap-molds.com"
    managed_banners = effective_banners(locale)
    first_banner = managed_banners[0] if managed_banners else {
        "img": legacy_media_url("/upload/Banner/Plastic-flip-top-mold.jpg"),
        "link": localized_href(locale, "/products/"),
        "title": "Su fabricante de" if locale == "es" else "Your Trusted", "highlight": "moldes de tapas" if locale == "es" else "Plastic Cap Mould",
        "description": text(locale, "hero_text"), "alt": "LEYA MOULD precision machining reference",
        "cta": text(locale, "hero_primary")
    }
    hero_img = first_banner["img"]
    steel_img = legacy_media_url("/upload/Home/steel-quality.jpg")
    samples = ["water-cap", "csd-cap", "hotfill-cap", "oil-cap", "soysauce-cap", "pharma-cap", "disc-top-cap", "flip-top-cap", "tamper-evident-cap", "push-pull-cap", "pull-ring-cap", "two-shot-cap", "custom-cap", "wide-mouth-cap", "squeeze-sports-cap", "motor-oil-cap", "5-gallon-cap", "bottle-handle"]
    hero_tail = "" if managed_banners or locale == "es" else " Manufacturer"
    previous_slide = "Diapositiva anterior" if locale == "es" else "Previous slide"
    next_slide = "Diapositiva siguiente" if locale == "es" else "Next slide"
    slide_status = "Diapositiva 1 de 3" if locale == "es" else "Slide 1 of 3"
    hero = '<section class="hero hero-slider" data-hero tabindex="0" aria-label="' + esc(BRAND_DISPLAY) + '"><div class="hero__backdrop"></div><div class="hero__inner shell"><div class="hero__copy"><span class="eyebrow">' + esc(text(locale, "hero_eyebrow")) + '</span><h1 id="hero-title">' + esc(first_banner["title"]) + ' <span>' + esc(first_banner["highlight"]) + '</span>' + esc(hero_tail) + '</h1><p id="hero-description">' + esc(first_banner["description"]) + '</p><div class="actions"><a id="hero-cta" class="button button--round" href="' + esc(first_banner["link"]) + '">' + esc(first_banner["cta"]) + '</a><a class="button button--outline button--round" href="' + localized_href(locale, "/contact/#inquiry") + '">' + esc(text(locale, "hero_secondary")) + '</a></div><p class="hero__note">' + esc(text(locale, "hero_note")) + '</p></div><div class="hero__art"><a class="hero__art-link" href="' + esc(first_banner["link"]) + '" aria-label="' + esc(first_banner["alt"]) + '"><img id="hero-image" src="' + esc(hero_img) + '" alt="' + esc(first_banner["alt"]) + '" loading="eager" decoding="async"></a></div></div><button class="hero__arrow hero__arrow--prev" type="button" data-hero-nav="-1" aria-label="' + esc(previous_slide) + '">‹</button><button class="hero__arrow hero__arrow--next" type="button" data-hero-nav="1" aria-label="' + esc(next_slide) + '">›</button><div class="hero__controls"><button class="hero__dot active" data-hero-go="0" aria-pressed="true" type="button">01</button><button class="hero__dot" data-hero-go="1" aria-pressed="false" type="button">02</button><button class="hero__dot" data-hero-go="2" aria-pressed="false" type="button">03</button><span id="hero-status" class="sr-only" aria-live="polite">' + esc(slide_status) + '</span></div></section>'
    if managed_banners:
        managed_json = json.dumps(managed_banners, ensure_ascii=False).replace("</", "<\\/")
        hero += '<script type="application/json" id="xuyi-home-banners">' + managed_json + '</script>'
    advantage_fallback = [{"title": title, "body": desc} for title, desc in data(locale, "advantages")]
    advantage_items = structured_section_items(locale, "/", "advantages", advantage_fallback)
    advantages = ''.join('<article class="advantage-card"><span class="advantage-card__number">0' + str(i + 1) + '</span><h3>' + esc(str(item.get("title") or item.get("label") or "")) + '</h3><p>' + esc(str(item.get("body") or "")) + '</p></article>' for i, item in enumerate(advantage_items))
    adv = structured_section(locale, "/", "advantages", "Core Advantages of LEYA MOULD", "From mould design to trial delivery, we deliver value through engineering excellence and strict quality control.", "WHY CHOOSE US")
    advantages_section = '<section class="section section--advantages"><div class="shell">' + section_heading(locale, adv["eyebrow"], adv["title"], adv["body"]) + '<div class="advantage-grid">' + advantages + '</div></div></section>'
    # The homepage keeps the product-family showcase focused on the first
    # twelve families. The full catalogue and navigation continue to expose
    # every approved family, including the remaining bottle-tooling route.
    home_series = CAP_MOULD_SERIES[:12]
    catalog_count = len(home_series)
    products_copy = structured_section(locale, "/", "products", "Mould Product Families", "Explore " + str(catalog_count) + " specialized mould product families engineered for high-volume production, dimensional accuracy and long service life.", "OUR PRODUCTS")
    cap_products = '<section class="section cap-series-section"><div class="shell">' + section_heading(locale, products_copy["eyebrow"], products_copy["title"], products_copy["body"]) + '<div class="cap-series-grid">' + ''.join(cap_series_card(locale, item) for item in home_series) + '</div></div></section>'
    sample_items = structured_section_items(locale, "/", "samples", [{"id": s, "title": s.replace("-", " ").title(), "image": "/images/samples/" + s + ".jpg", "alt": s.replace("-", " ").title() + " reference sample"} for s in samples])
    sample_cards = ''.join('<a class="sample-card" href="' + localized_href(locale, str(item.get("link") or "/samples/")) + '"><img src="' + legacy_media_url(str(item.get("image") or "")) + '" alt="' + esc(str(item.get("alt") or item.get("title") or "LEYA MOULD sample")) + '" loading="lazy" decoding="async"><span>' + esc(str(item.get("title") or item.get("label") or "")) + '</span></a>' for item in sample_items)
    samples_copy = structured_section(locale, "/", "samples", "Plastic Cap Samples", "A wide variety of cap samples for beverage, food, pharma, personal-care and industrial closures. Use the arrows to browse the collection.", "SAMPLES GALLERY")
    previous_samples = "Muestras anteriores" if locale == "es" else "Previous samples"
    next_samples = "Muestras siguientes" if locale == "es" else "Next samples"
    samples_section = '<section class="section samples-section"><div class="shell">' + section_heading(locale, samples_copy["eyebrow"], samples_copy["title"], samples_copy["body"]) + '<div class="samples-track-wrap"><button class="samples-scroll samples-scroll--prev" type="button" data-samples-scroll="-1" aria-label="' + esc(previous_samples) + '">‹</button><div class="samples-track" data-samples-track>' + sample_cards + '</div><button class="samples-scroll samples-scroll--next" type="button" data-samples-scroll="1" aria-label="' + esc(next_samples) + '">›</button></div><div class="section__more"><a class="text-link" href="' + localized_href(locale, "/samples/") + '">' + esc(text(locale, "samples")) + ' →</a></div></div></section>'
    tech = structured_section(locale, "/", "technology", "Engineering Excellence Behind Every Mould", "Precision manufacturing, premium steel and documented controls for repeatable production.", "OUR TECHNOLOGY")
    tech_items = structured_section_items(locale, "/", "technology", [{"title": "Precision Manufacturing & Strict QC", "body": "Machining, EDM, inspection and trial evidence are reviewed against the approved tooling brief.", "bullets": ["Process review before manufacturing", "Documented inspection per approved scope"]}, {"title": "Material & Modular Design", "body": "Steel selection, heat treatment and modular inserts are matched to the part, machine and changeover requirements confirmed for the project.", "bullets": ["Material traceability where included in the project brief", "Delivery timing confirmed against the approved schedule"]}])
    first_tech = tech_items[0] if tech_items else {}
    second_tech = tech_items[1] if len(tech_items) > 1 else first_tech
    tech_list = lambda item: ''.join('<li>' + esc(str(bullet)) + '</li>' for bullet in (item.get("bullets") or [])[:8])
    first_tech_image = str(first_tech.get("image") or legacy_media_url("/upload/Home/precision-machining.jpg"))
    second_tech_image = str(second_tech.get("image") or legacy_media_url("/upload/Home/steel-quality.jpg"))
    technology = '<section class="section technology-section"><div class="shell"><div class="section__head tech-section-head"><div><span class="eyebrow">' + esc(tech["eyebrow"]) + '</span><h2 class="section__title">' + esc(tech["title"]) + '</h2><p class="copy-muted">' + esc(tech["body"]) + '</p><div class="section-line"></div></div></div><div class="tech-grid"><div class="tech-img">' + image(legacy_media_url(first_tech_image), str(first_tech.get("alt") or "Precision machining"), "lazy") + '</div><div class="tech-text"><h3>' + esc(str(first_tech.get("title") or "Precision Manufacturing & Strict QC")) + '</h3><p>' + esc(str(first_tech.get("body") or "")) + '</p><ul class="tech-list">' + tech_list(first_tech) + '</ul></div></div><div class="tech-grid tech-grid--second"><div class="tech-text"><h3>' + esc(str(second_tech.get("title") or "Material & Modular Design")) + '</h3><p>' + esc(str(second_tech.get("body") or "")) + '</p><ul class="tech-list">' + tech_list(second_tech) + '</ul></div><div class="tech-img">' + image(legacy_media_url(second_tech_image), str(second_tech.get("alt") or "Mould steel"), "lazy") + '</div></div></div></section>'
    process_fallback = [{"label": num, "title": title, "body": desc.replace(" →", "")} for num, title, desc in data(locale, "process_steps")]
    process_items = structured_section_items(locale, "/", "process", process_fallback)
    steps = ''.join('<article class="process-step"><div class="step-num">' + esc(str(item.get("label") or str(i + 1)).lstrip("0") or "0") + '</div><h4>' + esc(str(item.get("title") or "")) + '</h4><p>' + esc(str(item.get("body") or "")) + '</p></article>' for i, item in enumerate(process_items))
    process_copy = structured_section(locale, "/", "process", "Your Cap Mould Journey", "From your first drawing to delivery and technical support.", "HOW WE WORK")
    process = '<section class="section workflow-section"><div class="shell">' + section_heading(locale, process_copy["eyebrow"], process_copy["title"], process_copy["body"]) + '<div class="steps">' + steps + '</div></div></section>'
    # Keep the homepage testimonial module in the same compact three-card
    # carousel rhythm as the reference site. Nine reviews are available in
    # three slides instead of making the section into a tall nine-card stack.
    testimonial_rows = _review_rows(locale)
    testimonial_slides = []
    for slide_index in range(0, len(testimonial_rows), 3):
        cards = []
        for review in testimonial_rows[slide_index:slide_index + 3]:
            company = (' · ' + review["company"]) if review.get("company") else ''
            cards.append('<article class="testimonial-card"><p class="quote">&quot;' + esc(review["quote"]) + '&quot;</p><div class="author"><span>' + esc(review["author"] + company) + '</span></div></article>')
        active = " is-active" if slide_index == 0 else ""
        testimonial_slides.append('<div class="testimonial-slide' + active + '"><div class="testimonial-grid">' + ''.join(cards) + '</div></div>')
    testimonial_dots = ''.join('<button class="tdot' + (" active" if i == 0 else "") + '" type="button" data-testimonial-go="' + str(i) + '" aria-label="Go to review group ' + str(i + 1) + '" aria-pressed="' + ("true" if i == 0 else "false") + '"></button>' for i in range(len(testimonial_slides)))
    testimonial_script = '<script>(()=>{const root=document.querySelector("[data-testimonial-carousel]");if(!root)return;const track=root.querySelector(".testimonial-track"),dots=[...root.querySelectorAll("[data-testimonial-go]")];let index=0,timer;const go=i=>{index=(i+dots.length)%dots.length;track.style.transform="translateX(-"+(index*100)+"%)";dots.forEach((dot,n)=>{dot.classList.toggle("active",n===index);dot.setAttribute("aria-pressed",n===index?"true":"false")})};const start=()=>{clearInterval(timer);timer=setInterval(()=>go(index+1),6500)};dots.forEach((dot,n)=>dot.addEventListener("click",()=>{go(n);start()}));root.addEventListener("mouseenter",()=>clearInterval(timer));root.addEventListener("mouseleave",start);root.addEventListener("focusin",()=>clearInterval(timer));root.addEventListener("focusout",start);go(0);start()})();</script>'
    testimonial_copy = structured_section(locale, "/", "testimonials", "Trusted by Packaging Leaders Worldwide", "Reviewed customer feedback will appear here after source and publication review.", "TESTIMONIALS")
    if testimonial_rows:
        testimonials = '<section class="section testimonial-section"><div class="shell">' + section_heading(locale, testimonial_copy["eyebrow"], testimonial_copy["title"], testimonial_copy["body"]) + '<div class="testimonial-carousel" data-testimonial-carousel aria-label="Customer testimonials"><div class="testimonial-track">' + ''.join(testimonial_slides) + '</div><div class="testimonial-dots">' + testimonial_dots + '</div></div></div></section>' + testimonial_script
    else:
        testimonials = '<section class="section testimonial-section testimonial-section--empty"><div class="shell">' + section_heading(locale, testimonial_copy["eyebrow"], testimonial_copy["title"], testimonial_copy["body"]) + '</div></section>'
    ref_copy = structured_section(locale, "/", "references", "Built for repeatable production decisions.", "Mould structure, steel selection, inspection evidence and trial feedback stay connected through the project.", "ENGINEERING REFERENCE")
    ref_fallback = [{"label": "01", "title": "Precision manufacturing", "body": "Machining, EDM, fitting and assembly follow the approved tooling brief."}, {"label": "02", "title": "Material & modular design", "body": "Material traceability and modular inserts keep future changes practical."}, {"label": "03", "title": "Trial & inspection", "body": "Sample results, dimensional checks and agreed revisions guide handover."}]
    ref_items = structured_section_items(locale, "/", "references", ref_fallback)
    references = '<section class="section reference-section"><div class="shell">' + section_heading(locale, ref_copy["eyebrow"], ref_copy["title"], ref_copy["body"]) + '<div class="reference-grid">' + ''.join('<article><span>' + esc(str(item.get("label") or str(i + 1).zfill(2))) + '</span><h3>' + esc(str(item.get("title") or "")) + '</h3><p>' + esc(str(item.get("body") or "")) + '</p></article>' for i, item in enumerate(ref_items)) + '</div></div></section>'
    res_copy = structured_section(locale, "/", "resources", "Latest from LEYA MOULD", "Project notes, tooling updates and practical engineering guidance.", "NEWS & INSIGHTS")
    res_fallback = [{"label": "NEWS", "title": "Cap mould project notes", "body": "Follow new category material, sample references and production lessons.", "link": "/news/"}, {"label": "ENGINEERING", "title": "Lightweight closure design", "body": "Review the design questions that influence sealing, cooling and cycle goals.", "link": "/news/"}, {"label": "QUALITY", "title": "Inspection evidence", "body": "Keep dimensions, trial results and approved revisions connected.", "link": "/news/"}, {"label": "FAQ", "title": "Prepare a useful tooling enquiry", "body": "See the drawing, resin, machine and sample information that helps a quotation move faster.", "link": "/faq/"}, {"label": "VIDEO", "title": "Mould trial and review", "body": "Use the video area for future machine, trial and inspection media.", "link": "/video/"}, {"label": "CONTACT", "title": "Send your project brief", "body": "Tell LEYA MOULD what you are making and where the tooling must run.", "link": "/contact/#inquiry"}]
    res_items = structured_section_items(locale, "/", "resources", res_fallback)
    resources = '<section class="section section--soft resource-section"><div class="shell">' + section_heading(locale, res_copy["eyebrow"], res_copy["title"], res_copy["body"]) + '<div class="resource-grid">' + ''.join('<a class="resource-card" href="' + localized_href(locale, str(item.get("link") or "/news/")) + '"><span class="eyebrow">' + esc(str(item.get("label") or "")) + '</span><h3>' + esc(str(item.get("title") or "")) + '</h3><p>' + esc(str(item.get("body") or "")) + '</p><span class="text-link">' + esc(text(locale, "learn")) + '</span></a>' for item in res_items) + '</div></div></section>'
    return hero + advantages_section + cap_products + samples_section + technology + testimonials + process + resources

def catalog_support_sections(locale: str) -> str:
    """Render the supporting modules that exist on the reference catalogue page.

    The catalogue route used to stop after the product cards and video strip.
    Keep these modules in one renderer so the aggregate page stays complete,
    while the individual routes and the shared shell remain untouched.
    """
    route = "/Plastic-cap-mold.html"
    es = locale == "es"
    advantages_copy = structured_section(locale, route, "advantages")
    samples_copy = structured_section(locale, route, "samples")
    technology_copy = structured_section(locale, route, "technology")
    quality_copy = structured_section(locale, route, "quality")
    workflow_copy = structured_section(locale, route, "workflow")
    faq_copy = structured_section(locale, route, "faq")
    testimonial_copy = structured_section(locale, route, "testimonials")
    video_copy = structured_section(locale, route, "videos")
    if es:
        advantages_copy = spanish_ui_copy(advantages_copy)
        samples_copy = spanish_ui_copy(samples_copy)
        technology_copy = spanish_ui_copy(technology_copy)
        quality_copy = spanish_ui_copy(quality_copy)
        workflow_copy = spanish_ui_copy(workflow_copy)
        faq_copy = spanish_ui_copy(faq_copy)
        testimonial_copy = spanish_ui_copy(testimonial_copy)
        video_copy = spanish_ui_copy(video_copy)
    advantages_title, advantages_desc = advantages_copy["title"], advantages_copy["body"]
    samples_title, samples_desc = samples_copy["title"], samples_copy["body"]
    technology_title, technology_desc = technology_copy["title"], technology_copy["body"]
    quality_title, quality_desc = quality_copy["title"], quality_copy["body"]
    workflow_title, workflow_desc = workflow_copy["title"], workflow_copy["body"]
    faq_title, faq_desc = faq_copy["title"], faq_copy["body"]
    testimonial_title, testimonial_desc = testimonial_copy["title"], testimonial_copy["body"]

    advantage_items = [row for row in advantages_copy.get("items", []) if isinstance(row, dict)]
    advantages = ''.join('<article class="advantage-card"><span class="advantage-card__number">' + str(i + 1).zfill(2) + '</span><h3>' + esc(str(row.get("title") or row.get("label") or "")) + '</h3><p>' + esc(str(row.get("body") or "")) + '</p></article>' for i, row in enumerate(advantage_items))
    advantages_section = '<section id="catalog-advantages" class="section section--advantages"><div class="shell">' + section_heading(locale, advantages_copy.get("eyebrow") or ("WHY CHOOSE US" if not es else "POR QUÉ ELEGIRNOS"), advantages_title, advantages_desc) + '<div class="advantage-grid catalog-advantage-grid">' + advantages + '</div></div></section>'

    sample_rows = [row for row in samples_copy.get("items", []) if isinstance(row, dict)]
    sample_cards = ''.join('<button class="catalog-sample-item" type="button" data-sample-img="' + legacy_media_url(str(row.get("image") or "")) + '" aria-label="' + esc(str(row.get("alt") or row.get("title") or ("Muestra de tapa " if es else "Bottle cap sample"))) + '"><img src="' + legacy_media_url(str(row.get("image") or "")) + '" alt="' + esc(str(row.get("alt") or row.get("title") or "LEYA MOULD cap sample")) + '" loading="lazy" decoding="async"></button>' for row in sample_rows if row.get("image"))
    samples_section = '<section id="catalog-samples" class="section samples-section"><div class="shell">' + section_heading(locale, samples_copy.get("eyebrow") or ("CAP SAMPLES" if not es else "MUESTRAS DE TAPAS"), samples_title, samples_desc) + '<div class="catalog-sample-grid" id="catalogSampleGrid">' + sample_cards + '</div></div></section><div class="catalog-lightbox" id="catalogLightbox" aria-hidden="true"><button type="button" class="catalog-lightbox__close" data-sample-close aria-label="Close sample">×</button><img id="catalogLightboxImg" src="" alt=""></div><script>(()=>{const grid=document.getElementById("catalogSampleGrid"),box=document.getElementById("catalogLightbox"),img=document.getElementById("catalogLightboxImg");if(!grid||!box||!img)return;const close=()=>{box.classList.remove("is-open");box.setAttribute("aria-hidden","true");img.src=""};grid.addEventListener("click",e=>{const b=e.target.closest("[data-sample-img]");if(!b)return;img.src=b.dataset.sampleImg;box.classList.add("is-open");box.setAttribute("aria-hidden","false")});box.addEventListener("click",e=>{if(e.target===box||e.target.closest("[data-sample-close]"))close()});document.addEventListener("keydown",e=>{if(e.key==="Escape")close()})})();</script>'

    technical_items = [row for row in technology_copy.get("items", []) if isinstance(row, dict)]
    tech_cards = ''.join('<article class="tech-card"><div class="tech-icon">' + str(i + 1).zfill(2) + '</div><div><h4>' + esc(str(row.get("title") or "")) + '</h4><p>' + esc(str(row.get("body") or "")) + '</p></div></article>' for i, row in enumerate(technical_items))
    technology = '<section id="catalog-technology" class="technical-section"><div class="shell"><div class="section-header"><div class="section-tag">' + esc(technology_copy.get("eyebrow") or ("TECNOLOGÍA" if es else "TECHNOLOGY")) + '</div><h2 class="section-title">' + esc(technology_title) + '</h2><p class="section-sub">' + esc(technology_desc) + '</p><div class="section-line"></div></div><div class="tech-grid">' + tech_cards + '</div></div></section>'

    quality_items = [row for row in quality_copy.get("items", []) if isinstance(row, dict)]
    quality_cards = ''.join('<article class="quality-item"><div class="quality-icon">' + esc(str(row.get("label") or str(i + 1).zfill(2))) + '</div><h4>' + esc(str(row.get("title") or "")) + '</h4><p>' + esc(str(row.get("body") or "")) + '</p></article>' for i, row in enumerate(quality_items))
    quality = '<section id="catalog-quality" class="quality-section"><div class="shell"><div class="section-header"><div class="section-tag">' + esc(quality_copy.get("eyebrow") or ("CALIDAD" if es else "QUALITY")) + '</div><h2 class="section-title">' + esc(quality_title) + '</h2><p class="section-sub">' + esc(quality_desc) + '</p><div class="section-line"></div></div><div class="quality-list">' + quality_cards + '</div></div></section>'

    workflow_items = [row for row in workflow_copy.get("items", []) if isinstance(row, dict)]
    steps = ''.join('<article class="step"><strong>' + esc(str(row.get("label") or str(i + 1).zfill(2))) + '</strong><h3>' + esc(str(row.get("title") or "")) + '</h3><p>' + esc(str(row.get("body") or "")) + '</p></article>' for i, row in enumerate(workflow_items))
    process = '<section id="catalog-workflow" class="process-section"><div class="shell"><div class="section-header"><div class="section-tag">' + esc(workflow_copy.get("eyebrow") or ("FLUJO DE TRABAJO" if es else "WORKFLOW")) + '</div><h2 class="section-title">' + esc(workflow_title) + '</h2><p class="section-sub">' + esc(workflow_desc) + '</p><div class="section-line"></div></div><div class="process-steps">' + steps + '</div></div></section>'

    faq_pairs = [(str(row.get("question") or ""), str(row.get("answer") or "")) for row in faq_copy.get("items", []) if isinstance(row, dict) and row.get("question") and row.get("answer")]
    faq_rows = ''.join('<details' + (' open' if i == 0 else '') + '><summary>' + esc(question) + '</summary><p class="faq-answer">' + esc(answer) + '</p></details>' for i, (question, answer) in enumerate(faq_pairs))
    # Never invent customer names, countries or performance claims. The
    # catalogue may show only reviews explicitly approved in D1; otherwise it
    # keeps the reference section compact and transparently empty.
    catalog_reviews = _review_rows(locale)
    if catalog_reviews:
        review_cards = ''.join('<article class="testimonial-card"><div class="quote">&quot;' + esc(row["quote"]) + '&quot;</div><div class="author">' + esc(row["author"]) + '</div>' + ('<div class="company">' + esc(row["company"]) + '</div>' if row.get("company") else '') + '</article>' for row in catalog_reviews[:3])
        testimonials = '<div id="catalog-testimonials" class="testimonials"><h3><span class="testimonial-star">★</span> ' + esc(testimonial_title) + '</h3>' + review_cards + '</div>'
    else:
        testimonials = '<div id="catalog-testimonials" class="testimonials testimonials--empty"><h3><span class="testimonial-star">★</span> ' + esc(testimonial_title) + '</h3><p>' + esc(testimonial_desc) + '</p></div>'
    faq = '<section id="catalog-faq" class="faq-section"><div class="shell"><div class="faq-grid"><div class="faq-list"><h3 id="faq-heading"><span class="faq-star">?</span> ' + esc(faq_title) + '</h3>' + faq_rows + '</div>' + testimonials + '</div></div></section>'

    contact = shared_cta(locale, "catalog", element_id="catalog-contact")

    # Order follows the reference page: products → advantages → samples →
    # trials → technology → quality → workflow → FAQ → testimonials → CTA.
    return advantages_section + samples_section + catalog_video_section(locale) + technology + quality + process + faq + contact

def products_page(locale: str) -> str:
    catalog_count = len(CAP_MOULD_SERIES)
    hero_title = "Precisión <span>MOLDEADO</span><br>En " + str(catalog_count) + " familias de productos" if locale == "es" else "Precision <span>MOULDING</span><br>Across " + str(catalog_count) + " Product Families"
    hero_text = "Fabricante profesional de moldes de plástico con más de 15 años de experiencia. Desde cierres y preformas hasta moldes para botellas, ofrecemos soluciones de alta precisión y larga vida útil." if locale == "es" else "Professional plastic mould manufacturer with 15+ years of experience. From closures and preforms to bottle tooling, we deliver high-precision, long-life mould solutions."
    stat_labels = ("AÑOS DE EXPERIENCIA", "FAMILIAS DE PRODUCTOS", "PAÍSES ATENDIDOS", "MOLDES ENTREGADOS") if locale == "es" else ("YEARS EXPERIENCE", "PRODUCT FAMILIES", "COUNTRIES SERVED", "MOULDS DELIVERED")
    hero = '<section class="catalog-hero"><div class="shell"><h1>' + hero_title + '</h1><p>' + hero_text + '</p><a class="button button--round" href="' + localized_href(locale, "/contact/#inquiry") + '">' + esc(text(locale, "quote")) + ' →</a><div class="catalog-stats"><div><strong>15+</strong><span>' + stat_labels[0] + '</span></div><div><strong>' + str(catalog_count) + '</strong><span>' + stat_labels[1] + '</span></div><div><strong>40+</strong><span>' + stat_labels[2] + '</span></div><div><strong>2000+</strong><span>' + stat_labels[3] + '</span></div></div></div></section>'
    crumb = '<nav class="reference-breadcrumb" aria-label="Breadcrumb"><div class="shell"><a href="' + local_link(locale, "/") + '">' + esc(text(locale, "home")) + '</a><span>›</span><span>' + esc(text(locale, "products")) + '</span></div></nav>'
    cards = ''.join(cap_series_card(locale, c) for c in CAP_MOULD_SERIES)
    products_eyebrow = "NUESTROS PRODUCTOS" if locale == "es" else "OUR PRODUCTS"
    products_title = "Familias de productos de moldes" if locale == "es" else "Mould Product Families"
    products_body = "Explore nuestra gama completa de " + str(len(CAP_MOULD_SERIES)) + " familias especializadas de productos de moldes. Cada molde está diseñado para producción de gran volumen, precisión dimensional y una vida útil prolongada." if locale == "es" else "Explore our comprehensive range of " + str(len(CAP_MOULD_SERIES)) + " specialized mould product families. Each mould is engineered for high-volume production, dimensional accuracy and extended service life."
    products = '<section class="section cap-series-section"><div class="shell">' + section_heading(locale, products_eyebrow, products_title, products_body) + '<div class="cap-series-grid">' + cards + '</div></div></section>'
    model_helpers = {"esc": esc, "image": image, "localized_href": localized_href}
    general_models = [row for row in HMOULD_MODELS if row.get("family") == "general-cap-mould"]
    model_references = render_model_reference_section(locale, general_models, model_helpers, "Referencias adicionales de modelos de tapas" if locale == "es" else "Additional Cap Model References")
    return hero + crumb + products + model_references + catalog_support_sections(locale)

def cap_product_page(locale: str, item: dict) -> str:
    helpers = {"esc": esc, "image": image, "localized_href": localized_href, "shared_cta": shared_cta,
               "hmould_models": HMOULD_MODELS, "strict_d1": STRICT_D1,
               "verified_reviews": _review_rows(locale, item.get("slug")),
               # Keep the visible FAQ list on the exact same D1-backed rows
               # used by Product/FAQPage JSON-LD.
               "d1_faqs": _product_faq_pairs(item, locale)}
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
            "LEYA MOULD desarrolla proyectos de moldes para tapones, preformas, botellas y componentes de envases. Nuestro trabajo conecta el diseño de la pieza, el acero, la refrigeración, la expulsión y las pruebas de producción.",
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

    structured = structured_page_copy(locale, "/about/")
    structured_sections = structured.get("sections", {}) if isinstance(structured.get("sections", {}), dict) else {}
    def section_title(key: str, fallback: str) -> str:
        row = structured_sections.get(key, {})
        value = str(row.get("title") or fallback) if isinstance(row, dict) else fallback
        return spanish_ui_text(value) if es else value
    story = structured_page_value(locale, "/about/", "story", story)
    title = structured_page_value(locale, "/about/", "title", title)
    subtitle = structured_page_value(locale, "/about/", "subtitle", subtitle)
    who = section_title("overview", who)
    journey = section_title("journey", journey)
    why = section_title("advantages", why)
    facility = section_title("facility", facility)
    certs = section_title("quality", certs)
    production = section_title("production", production)

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
    # Do not publish named certifications or regulatory claims until a reviewed
    # D1 evidence record is attached to this site. These labels describe the
    # evidence workflow without claiming an unverified certificate.
    certifications = ["Project quality records", "Material traceability", "Trial and inspection evidence", "Buyer-specific documentation"]
    if es:
        timeline = [
            ("01", "Base de diseño", "Un documento técnico claro conecta el plano, el material, el acabado del cuello y el proceso de producción previsto."),
            ("02", "Asignación del proyecto", "La familia del molde, el plan de cavidades, la interfaz de máquina y la producción objetivo se confirman antes de cortar el acero."),
            ("03", "Revisión tecnológica", "La refrigeración, los canales calientes, la línea de partición y la expulsión se revisan frente a la geometría de la pieza."),
            ("04", "Fabricación de precisión", "El mecanizado, EDM, pulido, ajuste e inspección siguen el documento técnico de utillaje aprobado."),
            ("05", "Prueba y validación", "Las muestras de prueba, las comprobaciones dimensionales y los cambios acordados guían la entrega final."),
            ("06", "Soporte de proyectos internacionales", "Los archivos aprobados, las notas de entrega y el soporte técnico permanecen disponibles después del envío."),
        ]
        advantages = [
            ("Ingeniería de precisión", "La revisión CAD/CAM, el mecanizado CNC y la inspección mantienen bajo control las dimensiones críticas del cierre.", advantages[0][2]),
            ("Soluciones personalizadas", "Adaptamos la estructura del molde al diseño del cierre, la resina, la máquina y los requisitos de producción.", advantages[1][2]),
            ("Garantía de calidad", "Las pruebas, las comprobaciones dimensionales y la aprobación de muestras crean una entrega documentada.", advantages[2][2]),
            ("Entrega rápida", "Un plan de utillaje escalonado mantiene visibles los hitos de mecanizado, ajuste, prueba y entrega.", advantages[3][2]),
            ("Soluciones integradas", "El diseño del molde, la evidencia de producción y los requisitos de procesos auxiliares permanecen en una sola conversación del proyecto.", advantages[4][2]),
            ("Soporte durante toda la vida útil", "Los planos aprobados, los registros de inspección y las notas técnicas facilitan el soporte futuro.", advantages[5][2]),
        ]
        equipment = ["Centros de mecanizado CNC de 5 ejes", "Máquinas EDM de alta velocidad", "Máquinas EDM de corte por hilo", "Máquinas rectificadoras de precisión", "Tornos y fresadoras CNC", "Máquinas de prueba de moldeo por inyección", "Máquinas de medición por coordenadas 3D (CMM)", "Durómetros y espectrómetros"]
        certifications = ["Registros de calidad del proyecto", "Trazabilidad del material", "Evidencia de pruebas e inspección", "Documentación específica del comprador"]
    reference_images = "https://www.cap-molds.com/images/"
    facility_images = [
        (legacy_media_url("/images/CNC-machining-workshop.jpg"), "CNC machining workshop"),
        (ABOUT_MEDIA["assembly"], "EDM machine area"),
        (legacy_media_url("/images/Quality-inspection-room.jpg"), "Quality inspection room"),
        (ABOUT_MEDIA["assembly"], "Mould assembly area"),
        (legacy_media_url("/images/Injection-trial-machine.jpg"), "Injection trial machine"),
        (legacy_media_url("/images/Warehouse-and-shipping-area.jpg"), "Warehouse and shipping area"),
        (ABOUT_MEDIA["assembly"], "5-axis machining center"),
        (legacy_media_url("/images/Engineering-design-office.jpg"), "Engineering design office"),
        (legacy_media_url("/images/Showroom01.jpg"), "Showroom 01"),
        (legacy_media_url("/images/Showroom02.jpg"), "Showroom 02"),
        (legacy_media_url("/images/Showroom03.jpg"), "Showroom 03"),
        (legacy_media_url("/images/Showroom04.jpg"), "Showroom 04"),
        (legacy_media_url("/images/Showroom05.jpg"), "Showroom 05"),
        (legacy_media_url("/images/Showroom06.jpg"), "Showroom 06"),
        (legacy_media_url("/images/Showroom07.jpg"), "Showroom 07"),
        (legacy_media_url("/images/Showroom08.jpg"), "Showroom 08"),
    ]
    intro_body = intro(locale, title, subtitle, "/about/")
    about_stats = structured_page_copy(locale, "/about/").get("stats")
    if not isinstance(about_stats, list) or not about_stats:
        about_stats = [{"label": value, "title": label} for value, label in [("15+", "Years of Experience"), ("60+", "Countries Served"), ("500+", "Moulds Delivered"), ("80+", "Skilled Team Members")]]
    if es:
        # D1 may contain the English baseline for a statistic row.  Keep the
        # number but always pass the visible label through the reviewed UI
        # glossary before rendering the Spanish page.
        about_stats = spanish_ui_copy(about_stats)
    team_alt = "Equipo de ingeniería de LEYA MOULD revisando un proyecto de moldes" if es else "LEYA MOULD engineering team reviewing a mould project"
    overview = '<section class="mould-about-block"><div class="mould-about-overview"><div class="mould-about-overview-image"><img src="' + ABOUT_MEDIA["team"] + '" alt="' + esc(team_alt) + '" loading="eager" decoding="async"></div><div><h2>' + esc(who) + '</h2>' + ''.join('<p>' + esc(p) + '</p>' for p in who_paras) + '</div></div><div class="mould-about-stats">' + ''.join('<div class="mould-about-stat"><span class="number">' + esc(str(item.get("label") or "")) + '</span><span class="label">' + esc(str(item.get("title") or "")) + '</span></div>' for item in about_stats[:4] if isinstance(item, dict)) + '</div></section>'
    journey_html = '<section class="mould-about-block"><h2>' + esc(journey) + '</h2><div class="mould-about-timeline">' + ''.join('<div class="mould-about-timeline-item"><span class="year">' + esc(year) + '</span><div><h3>' + esc(head) + '</h3><p>' + esc(desc) + '</p></div></div>' for year, head, desc in timeline) + '</div></section>'
    advantages_html = '<section class="mould-about-block"><h2>' + esc(why) + '</h2><div class="mould-about-advantages">' + ''.join('<article><div class="icon"><svg viewBox="0 0 24 24" aria-hidden="true">' + icon + '</svg></div><h3>' + esc(head) + '</h3><p>' + esc(desc) + '</p></article>' for head, desc, icon in advantages) + '</div></section>'
    equipment_intro = "Nuestros recursos de fabricación utilizan mecanizado, inspección y equipos de prueba modernos para que cada decisión de utillaje pueda comprobarse frente al documento técnico de producción." if es else "Our manufacturing references use modern machining, inspection and trial equipment so every tooling decision can be checked against the production brief."
    equipment_html = '<section class="mould-about-block"><h2>' + esc(facility) + '</h2><p>' + equipment_intro + '</p><ul class="mould-about-equipment">' + ''.join('<li><span>✓</span>' + esc(item) + '</li>' for item in equipment) + '</ul></section>'
    cert_intro = "La evidencia de calidad se conserva con el proyecto y se revisa antes del envío. La documentación final sigue los requisitos confirmados por el comprador." if es else "Quality evidence is kept with the project and reviewed before shipment. The final documentation follows the confirmed buyer requirements."
    facility_intro = "Las referencias de producción de LEYA MOULD muestran el trabajo de ingeniería, inspección y revisión de muestras que respalda cada proyecto de utillaje." if es else "LEYA MOULD production references show the engineering, inspection and sample-review work behind each tooling project."
    if es:
        cert_intro = spanish_ui_text(cert_intro)
        facility_intro = spanish_ui_text(facility_intro)
    cert_html = '<section class="mould-about-block"><h2>' + esc(certs) + '</h2><p>' + esc(cert_intro) + '</p><div class="mould-about-certifications">' + ''.join('<span>' + esc(item) + '</span>' for item in certifications) + '</div></section>'
    facilities_html = '<section class="mould-about-block"><h2>' + esc(production) + '</h2><p>' + esc(facility_intro) + '</p><div class="mould-about-facilities">' + ''.join('<figure><img src="' + esc(file_name) + '" alt="' + esc(spanish_ui_text(alt) if es else alt) + '" loading="lazy" decoding="async"></figure>' for file_name, alt in facility_images) + '</div></section>'
    contact_html = shared_cta(locale, "about", title_override=together, text_override=together_text)
    return '<div class="mould-about-page">' + intro_body + overview + journey_html + advantages_html + equipment_html + cert_html + facilities_html + contact_html + '</div>'

def capabilities_page(locale: str) -> str:
    title = "Cap Auxiliary Machines" if locale == "en" else ("Máquinas auxiliares para tapas" if locale == "es" else text(locale, "capabilities"))
    subtitle = "Complete su línea de producción de tapas con nuestras máquinas auxiliares especializadas. Diseñadas para trabajar con nuestros moldes de tapas de plástico, realizan operaciones posteriores críticas como revestimiento, plegado, corte, impresión y colocación de juntas." if locale == "es" else "Complete your cap production line with our specialized auxiliary machines. Designed to work seamlessly with our plastic cap molds, these machines handle critical post-molding operations such as lining, folding, slitting, printing, and wadding."
    intro_image = "/media/page/e60d307101686212f51ca482b73b56cf.webp"
    intro_copy = (
        ("<p>Aunque los moldes de inyección producen la forma básica de la tapa, muchos cierres modernos necesitan procesos adicionales para funcionar correctamente. Las bandas de precinto deben plegarse o cortarse con precisión para romperse limpiamente al abrirse. Los revestimientos de sellado por inducción deben insertarse con exactitud para crear envases estancos. Los logotipos y códigos de fecha se imprimen a menudo en la superficie para trazabilidad y marketing. Estas operaciones requieren máquinas auxiliares dedicadas que ayuden a mantener una calidad estricta.</p>"
        "<p>En LEYA MOULD no solo fabricamos los moldes que dan forma a sus tapas; también ofrecemos una gama completa de máquinas auxiliares para completar la producción. Al proporcionar el molde y el equipo posterior, ayudamos a crear una célula integrada con calidad constante, cambios más rápidos y soporte posventa simplificado. A continuación se muestran seis máquinas habituales.</p>") if locale == "es" else
        "<p>While injection molds produce the basic cap shape, many modern closures require additional processing to achieve full functionality. "
        "Tamper-evident bands must be precisely folded or slit to break cleanly upon opening. Induction seal liners need to be inserted accurately "
        "to create leak-proof containers. Brand logos and date codes are often printed on the cap surface for traceability and marketing. "
        "These operations demand dedicated auxiliary machines that ensure every cap meets strict quality standards.</p>"
        "<p>At LEYA MOULD, we not only manufacture the molds that shape your caps but also offer a comprehensive range of auxiliary machines "
        "to complete your production. By providing both mold and post-molding equipment, we help you build a fully integrated manufacturing cell "
        "with consistent quality, faster changeovers, and simplified after-sales support. Below are six popular cap auxiliary machines.</p>"
    )
    machine_rows = spanish_ui_copy(AUXILIARY_MACHINES) if locale == "es" else AUXILIARY_MACHINES
    machine_cards = ''.join(
        '<article class="machine-card"><img class="machine-card-image" src="' + legacy_media_url('/upload/product/month_2105/' + str(item["image"])) + '" alt="' + esc(spanish_ui_text(item["alt"]) if locale == "es" else item["alt"]) + '" loading="lazy" decoding="async">'
        '<div class="machine-card-body"><h2 class="machine-card-name">' + esc(item["name"]) + '</h2><p class="machine-card-desc">' + esc(item["description"]) + '</p>'
        '<a href="' + localized_href(locale, "/contact/?model=" + item["model"] + "#inquiry") + '" class="machine-link">Learn More <span aria-hidden="true">→</span></a></div></article>'
        for item in machine_rows
    )
    contact = shared_cta(locale, "auxiliary")
    body = intro(locale, title, subtitle, "/capabilities/")
    machine_heading = "Por qué son esenciales las máquinas auxiliares para tapas" if locale == "es" else "Why Cap Auxiliary Machines Are Essential"
    body = '<section class="aux-page"><section class="intro-section"><div class="intro-image"><img src="' + intro_image + '" alt="' + ("Tapas de plástico producidas por LEYA MOULD" if locale == "es" else "Various plastic bottle caps produced by LEYA MOULD") + '" loading="lazy" decoding="async"></div><div class="intro-content"><h2>' + machine_heading + '</h2>' + intro_copy + '</div></section><div class="machine-grid">' + machine_cards.replace('>Learn More <span', '>Ver más <span' if locale == "es" else '>Learn More <span') + '</div>' + contact + '</section>'
    return body

def service_page(locale: str, service: dict) -> str:
    # Keep the three capability pages fully authored in Spanish.  These are
    # high-intent landing pages, so a word glossary alone is not sufficient:
    # it can leave English sentence order in the public copy.  The English
    # source remains the canonical reference; this map is the reviewed locale
    # owner copy used by the static build and the D1 snapshot gate.
    service_es = {
        "mould-design": (
            "Diseño e ingeniería de moldes",
            "Revisamos planos, líneas de partición, refrigeración, expulsión e interfaz de la máquina de producción antes de aprobar el utillaje."
        ),
        "precision-manufacturing": (
            "Fabricación de precisión",
            "El mecanizado, EDM, ajuste e inspección siguen el documento técnico de utillaje aprobado y los puntos de control acordados."
        ),
        "trial-sampling": (
            "Pruebas, muestras y optimización",
            "Las pruebas de molde, las muestras, las comprobaciones dimensionales y las revisiones acordadas guían la entrega final."
        ),
    }
    if locale == "es" and service.get("slug") in service_es:
        service_title, service_text = service_es[service["slug"]]
    else:
        service_title = service["title"]
        service_text = service["text"]
    body = intro(locale, service_title, service_text, "/capabilities/" + service["slug"] + "/")
    body += '<section class="section"><div class="shell"><div class="split"><div><h2 class="section__title">' + esc(service_title) + '</h2><p class="copy-muted">' + esc(service_text) + '</p><p class="copy-muted">' + esc(text(locale, "technical_text")) + '</p></div><div class="split__placeholder"><strong>' + esc("ARCHIVOS DEL PROYECTO POR REVISAR" if locale == "es" else "PROJECT FILES TO BE REVIEWED") + '</strong><p>' + esc("Plano · muestra · PDF · notas de revisión" if locale == "es" else "Drawing · sample · PDF · revision notes") + '</p></div></div><p style="margin-top:28px"><a class="button" href="' + localized_href(locale, "/contact/#inquiry") + '">' + esc(text(locale, "quote")) + ' →</a></p></div></section>'
    return body

def contact_page(locale: str) -> str:
    labels = {"FORM_ARIA": text(locale, "form_aria"), "FORM_NAME": "Full Name" if locale == "en" else "Nombre completo", "FORM_PHONE": "Phone / WhatsApp" if locale == "en" else "Teléfono / WhatsApp", "FORM_COMPANY": text(locale, "form_company"), "FORM_EMAIL": text(locale, "form_email"), "FORM_CATEGORY": "Cap Mould Type" if locale == "en" else "Tipo de molde de tapa", "FORM_CATEGORY_PLACEHOLDER": "— Select cap mould type —" if locale == "en" else "— Seleccione el tipo de molde —", "FORM_REQUIREMENTS": "Your Message" if locale == "en" else "Su mensaje", "FORM_PRIVACY_NOTE": "Your information is secure." if locale == "en" else "Su información está protegida.", "FORM_PRIVACY": text(locale, "form_privacy"), "FORM_SUBMIT": "Send Inquiry Now" if locale == "en" else "Enviar consulta", "FORM_COMPANY_PLACEHOLDER": "Your company" if locale == "en" else "Su empresa", "FORM_REQUIREMENTS_PLACEHOLDER": "Share cap design, material, cavity count and production volume." if locale == "en" else "Comparta el diseño de la tapa, el material, el número de cavidades y el volumen de producción.", "FORM_MINERAL_WATER": "Mineral Water Cap Mould" if locale == "en" else "Molde de tapas de agua mineral", "FORM_BEVERAGE": "Beverage Bottle Cap Mould" if locale == "en" else "Molde de tapas para botellas de bebidas", "FORM_EDIBLE_OIL": "Edible Oil Bottle Cap Mould" if locale == "en" else "Molde de tapas para aceite comestible", "FORM_MEDICAL": "Medical Bottle Cap Mould" if locale == "en" else "Molde de tapas médicas", "FORM_COSMETIC": "Cosmetic Cap Mould" if locale == "en" else "Molde de tapas cosméticas", "FORM_FLIP_TOP": "Flip Top Cap Mould" if locale == "en" else "Molde de tapas abatibles", "FORM_TAMPER": "Tamper-Evident Cap Mould" if locale == "en" else "Molde de tapas con precinto", "FORM_CUSTOM": "Custom Closure Mould" if locale == "en" else "Molde de cierres personalizados", "FORM_OTHER": "Other / Not Sure" if locale == "en" else "Otro / No estoy seguro"}
    form = render_template("contact-form", **{key: esc(value) for key, value in labels.items()})
    body = intro(locale, text(locale, "contact_title"), text(locale, "contact_intro"), "/contact/")
    stats_rows = structured_page_copy(locale, "/contact/").get("stats")
    if not isinstance(stats_rows, list) or not stats_rows:
        labels_fallback = ["Years Experience", "Countries Served", "Moulds Delivered", "Quote Response"] if locale == "en" else ["Años de experiencia", "Países atendidos", "Moldes entregados", "Respuesta de cotización"]
        stats_rows = [{"label": value, "title": label} for value, label in zip(["15+", "60+", "500+", "24h"], labels_fallback)]
    if locale == "es":
        stats_rows = spanish_ui_copy(stats_rows)
    stats = '<div class="trust-row" aria-label="LEYA MOULD at a glance">' + ''.join('<div class="trust-badge"><span class="badge-number">' + esc(str(item.get("label") or "")) + '</span><span class="badge-label">' + esc(str(item.get("title") or "")) + '</span></div>' for item in stats_rows[:4] if isinstance(item, dict)) + '</div>'
    info_labels = ("Dirección de fábrica", "Métodos de contacto", "TELÉFONO / WHATSAPP", "CORREO", "SITIO WEB") if locale == "es" else ("Factory Address", "Contact Methods", "PHONE / WHATSAPP", "EMAIL", "WEBSITE")
    info = '<div class="contact-info-card"><div class="contact-info-block"><span class="contact-info-icon">⌖</span><h3>' + info_labels[0] + '</h3><strong>LEYA MOULD Co.,Ltd</strong><p>' + esc(ADDRESS) + '</p></div><div class="contact-info-block"><h3>' + info_labels[1] + '</h3><dl class="contact-methods"><div><dt>' + info_labels[2] + '</dt><dd><a href="tel:+8613606727715">+86 136 0672 7715</a></dd></div><div><dt>' + info_labels[3] + '</dt><dd><a href="mailto:' + EMAIL + '">' + EMAIL + '</a></dd></div><div><dt>' + info_labels[4] + '</dt><dd><a href="https://leyamould.com/">leyamould.com</a></dd></div></dl></div>' + stats + '</div>'
    quick_answers = [("⏱️ How fast can I get a quote?", "We respond within 24 hours. Use WhatsApp/WeChat for urgent requests."), ("📐 What info do I need to provide?", "Share cap design, material, cavity count, and production volume."), ("🌍 Do you ship internationally?", "Yes, we serve 60+ countries worldwide."), ("📱 How do I add you on WhatsApp/WeChat?", "Scan the QR codes on this page or click to enlarge them.")]
    if locale == "es":
        quick_answers = [("⏱️ ¿Cuánto tardan en enviar una cotización?", "Respondemos en 24 horas. Use WhatsApp/WeChat para solicitudes urgentes."), ("📐 ¿Qué información debo proporcionar?", "Comparta el diseño de la tapa, material, número de cavidades y volumen de producción."), ("🌍 ¿Realizan envíos internacionales?", "Sí, atendemos a más de 60 países."), ("📱 ¿Cómo puedo añadirles en WhatsApp/WeChat?", "Escanee los códigos QR de esta página o haga clic para ampliarlos.")]
    structured_answers = structured_page_copy(locale, "/contact/").get("quickAnswers")
    if isinstance(structured_answers, list) and structured_answers:
        reviewed = []
        for entry in structured_answers[:8]:
            if not isinstance(entry, dict):
                continue
            question = str(entry.get("question") or "").strip()
            answer = str(entry.get("answer") or "").strip()
            if question and answer:
                reviewed.append((question, answer))
        if reviewed:
            quick_answers = [(spanish_ui_text(q), spanish_ui_text(a)) for q, a in reviewed] if locale == "es" else reviewed
    quick_title = "Quick Answers" if locale == "en" else "Respuestas rápidas"
    quick = '<section class="faq-teaser" aria-labelledby="quick-answers-title"><h2 id="quick-answers-title">' + quick_title + '</h2><div class="faq-list">' + ''.join('<div class="faq-item"><p class="faq-q">' + esc(question) + '</p><p class="faq-a">' + esc(answer) + '</p></div>' for question, answer in quick_answers) + '</div></section>'
    form_title = "Envíenos su consulta" if locale == "es" else "Send Us Your Inquiry"
    form_intro = "Complete el formulario y le responderemos lo antes posible." if locale == "es" else "Fill out the form and we will reply as soon as possible."
    body += '<section class="section contact-section"><div class="shell"><div class="contact-layout">' + info + '<div class="contact-form-panel"><h2>' + form_title + '</h2><p>' + form_intro + '</p>' + form + '</div></div>' + quick + '</div></section>'
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

    structured = structured_page_copy(locale, "/faq/")
    structured_groups = structured.get("groups")
    if isinstance(structured_groups, list) and structured_groups:
        reviewed_groups = []
        for group in structured_groups[:8]:
            if not isinstance(group, dict):
                continue
            group_title = str(group.get("title") or "").strip()
            if locale == "es":
                group_title = spanish_ui_text(group_title)
            pairs = []
            for entry in (group.get("items") if isinstance(group.get("items"), list) else [])[:12]:
                if not isinstance(entry, dict):
                    continue
                question = str(entry.get("question") or "").strip()
                answer = str(entry.get("answer") or "").strip()
                if locale == "es":
                    question, answer = spanish_ui_text(question), spanish_ui_text(answer)
                if question and answer:
                    pairs.append((question, answer))
            if group_title and pairs:
                reviewed_groups.append((group_title, pairs))
        if reviewed_groups:
            groups = reviewed_groups
    if structured.get("eyebrow"):
        page_eyebrow = spanish_ui_text(str(structured["eyebrow"])) if locale == "es" else str(structured["eyebrow"])
    if structured.get("title"):
        page_title = esc(str(structured["title"]))
    if structured.get("subtitle"):
        page_subtitle = spanish_ui_text(str(structured["subtitle"])) if locale == "es" else str(structured["subtitle"])

    prefix = '<section class="reference-banner reference-banner--compact"><img src="' + legacy_media_url('/upload/Banner/pheader-faq.jpg') + '" alt="LEYA MOULD FAQ" loading="eager" decoding="async"></section>'
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
    contact_html = shared_cta(locale, "faq", title_override=contact_title, text_override=contact_text)
    script = '<script>(()=>{const root=document.querySelector("[data-faq-page]");if(!root)return;const items=[...root.querySelectorAll(".faq-item")];items.forEach(item=>{const button=item.querySelector(".faq-question");button.addEventListener("click",()=>{const active=item.classList.contains("active");items.forEach(other=>{other.classList.remove("active");const b=other.querySelector(".faq-question");if(b)b.setAttribute("aria-expanded","false")});if(!active){item.classList.add("active");button.setAttribute("aria-expanded","true")}})});})();</script>'
    return '<div class="faq-route">' + prefix + '<div class="faq-page" data-faq-page>' + header_html + ''.join(groups_html) + contact_html + '</div>' + script + '</div>'

def samples_page(locale: str) -> str:
    cap = "https://www.cap-molds.com"
    title = "Plastic Cap Samples" if locale == "en" else ("Muestras de tapas de plástico" if locale == "es" else text(locale, "samples"))
    subtitle = ("Explore una amplia variedad de tapas de plástico fabricadas con nuestros moldes de inyección de alta precisión. Cada tapa muestra lo que pueden producir nuestros moldes, desde cierres estándar de agua hasta diseños complejos con precinto." if locale == "es" else "Explore a wide variety of plastic bottle caps that we manufacture using our high-precision injection molds. Each cap is a sample of what our molds can produce — from standard water closures to complex tamper-evident designs.")
    cards = []
    sample_rows = spanish_sample_items() if locale == "es" else SAMPLE_ITEMS
    for item in sample_rows:
        applications = ''.join('<li>' + esc(app) + '</li>' for app in item["applications"])
        cards.append(
            '<article class="sample-card">'
            '<img class="sample-image" src="' + legacy_media_url('/images/samples/' + str(item["image"])) + '" alt="' + esc(item["alt"]) + '" loading="lazy" decoding="async">'
            '<div class="sample-body"><h2 class="sample-name">' + esc(item["name"]) + '</h2>'
            '<p class="sample-desc">' + esc(item["description"]) + '</p>'
            '<div class="sample-mold">🛠️ ' + esc(item["mold"]) + '</div>'
            '<div class="sample-applications"><h4>' + ("Aplicaciones" if locale == "es" else "Applications") + '</h4><ul>' + applications + '</ul></div></div></article>'
        )
    contact = shared_cta(locale, "samples")
    return intro(locale, title, subtitle, "/samples/") + '<section class="samples-page"><div class="sample-list">' + ''.join(cards) + '</div>' + contact + '</section>'

VIDEO_SEED = json.loads((ROOT / "data/leya-youtube-seed.json").read_text(encoding="utf-8"))
def video_card(item: dict, locale: str) -> str:
    raw_title = item.get("titleEs" if locale == "es" else "titleEn") or item.get("titleEn", "LEYA MOULD video")
    raw_description = item.get("descriptionEs" if locale == "es" else "description") or item.get("description", "")
    if locale == "es":
        raw_title = spanish_ui_text(raw_title)
        raw_description = spanish_ui_text(raw_description)
    title = esc(raw_title)
    description = esc(raw_description)
    video_id = esc(item.get("videoId", ""))
    published = esc(item.get("publishedAt", ""))
    date_text = "" if not item.get("publishedAt") else item["publishedAt"][:10]
    if locale == "es" and date_text:
        try:
            year, month, day = date_text.split("-")
            date_text = f"{day}/{month}/{year}"
        except ValueError:
            pass
    play_label = "Reproducir vídeo" if locale == "es" else "Play video"
    return ('<article class="video-card" data-video-id="' + video_id + '">'
        '<div class="video-thumb" data-video-id="' + video_id + '" role="button" tabindex="0" aria-label="' + esc(play_label + ': ' + raw_title) + '">'
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
    if locale == "es":
        videos = [dict(item, titleEs=spanish_ui_text(item.get("titleEs") or item.get("titleEn") or item.get("title") or "LEYA MOULD video"), descriptionEs=spanish_ui_text(item.get("descriptionEs") or item.get("description") or "")) for item in videos]
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
    if locale == "es":
        videos = [dict(item, titleEs=spanish_ui_text(item.get("titleEs") or item.get("titleEn") or item.get("title") or "LEYA MOULD video"), descriptionEs=spanish_ui_text(item.get("descriptionEs") or item.get("description") or "")) for item in videos]
    videos = videos[:5]
    cards = ''.join(video_card(item, locale) for item in videos)
    payload = json.dumps(videos, ensure_ascii=False).replace("</", "<\\/")
    video_copy = structured_section(locale, "/Plastic-cap-mold.html", "videos", "Cap Mould Trial Videos", "Watch the latest mould trial videos managed from the YouTube video module.", "MOULD TRIALS")
    title = video_copy["title"] or ("Cap Mould Trial Videos" if locale == "en" else "Vídeos de pruebas de moldes")
    description = video_copy["body"] or ("Watch the latest mould trial videos managed from the YouTube video module."
                   if locale == "en" else "Vea los últimos vídeos de pruebas gestionados desde el módulo de vídeos de YouTube.")
    close_label = "Close video" if locale == "en" else "Cerrar vídeo"
    play_label = "Play video" if locale == "en" else "Reproducir vídeo"
    empty_label = "No videos found yet." if locale == "en" else "Todavía no hay vídeos."
    script = '''<script>(()=>{const root=document.querySelector("[data-catalog-videos]");if(!root)return;const grid=document.getElementById("catalogVideoGrid"),empty=document.getElementById("catalogVideoEmpty"),modal=document.getElementById("catalogVideoModal"),frame=document.getElementById("catalogVideoIframe"),close=document.getElementById("catalogVideoClose"),lang=document.documentElement.lang||"en";const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\\\"":"&quot;","'":"&#39;"}[c]));const date=v=>{try{return new Intl.DateTimeFormat(lang,{year:"numeric",month:"long",day:"numeric"}).format(new Date(v))}catch{return v||""}};const card=v=>{const id=String(v.videoId||"");if(!/^[A-Za-z0-9_-]{11}$/.test(id))return "";const title=(lang==="es"?v.titleEs:v.titleEn)||v.title||"LEYA MOULD video";return `<article class="video-card" data-video-id="${esc(id)}"><div class="video-thumb" data-video-id="${esc(id)}" role="button" tabindex="0" aria-label="${esc(lang==="es"?"Reproducir vídeo":"Play video")}"><img src="https://i.ytimg.com/vi/${esc(id)}/mqdefault.jpg" alt="${esc(title)}" loading="lazy" decoding="async"><span class="play-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"></path></svg></span></div><div class="video-body"><time class="video-date" datetime="${esc(v.publishedAt||"")}">${date(v.publishedAt)}</time><h3 class="video-title"><button type="button" class="video-title-link" data-video-id="${esc(id)}">${esc(title)}</button></h3><p class="video-desc">${esc(v.description||"")}</p></div></article>`};const render=items=>{const visible=(items||[]).slice(0,5);grid.innerHTML=visible.map(card).join("");empty.hidden=visible.length>0};const play=id=>{if(!/^[A-Za-z0-9_-]{11}$/.test(id))return;frame.src="https://www.youtube.com/embed/"+id+"?autoplay=1&rel=0";modal.classList.add("active");modal.setAttribute("aria-hidden","false")};const stop=()=>{modal.classList.remove("active");modal.setAttribute("aria-hidden","true");frame.src=""};grid.addEventListener("click",e=>{const target=e.target.closest("[data-video-id]");if(target)play(target.dataset.videoId)});grid.addEventListener("keydown",e=>{if((e.key==="Enter"||e.key===" ")&&e.target.closest("[data-video-id]")){e.preventDefault();play(e.target.closest("[data-video-id]").dataset.videoId)}});close.addEventListener("click",stop);modal.addEventListener("click",e=>{if(e.target===modal)stop()});document.addEventListener("keydown",e=>{if(e.key==="Escape")stop()});fetch(root.dataset.publicApi+"?locale="+encodeURIComponent(lang),{cache:"no-store"}).then(r=>r.ok?r.json():Promise.reject()).then(d=>render(d.items||[])).catch(()=>{});})();</script>'''
    return ('<section class="section catalog-video-section" data-catalog-videos data-public-api="/api/youtube-videos"><div class="shell">'
        + section_heading(locale, video_copy.get("eyebrow") or "MOULD TRIALS", title, description)
        + '<div class="video-gallery-page catalog-video-gallery"><div class="video-grid" id="catalogVideoGrid">' + cards + '</div><p class="video-empty" id="catalogVideoEmpty" hidden>' + esc(empty_label) + '</p></div>'
        + '<div class="video-modal" id="catalogVideoModal" aria-hidden="true"><div class="video-modal-inner" role="dialog" aria-modal="true" aria-label="' + esc(title) + '"><button type="button" class="close-modal" id="catalogVideoClose" aria-label="' + esc(close_label) + '">×</button><iframe id="catalogVideoIframe" title="' + esc(play_label) + '" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe></div></div>'
        + '<script type="application/json" id="catalogVideoSeed">' + payload + '</script>' + script + '</div></section>')

def localized_item_text(item: dict, locale: str, field: str) -> str:
    """Read an article's translated field without replacing CMS-owned values."""
    if locale == "es":
        value = item.get(field + "Es") or ("" if STRICT_D1 else item.get(field, ""))
        # D1 summaries/titles can contain the same legacy mixed-language
        # fragments as the rich editorial branch.  Apply the reviewed Spanish
        # glossary at the final render boundary so listing cards and the
        # Article schema cannot expose an English fallback.
        return spanish_ui_text(value)
    return item.get(field, "")

def effective_news_items(category: str = "news") -> list[dict]:
    """Project reviewed mould editorial (or a matching D1 row) into cards.

    The registry is the auditable source fallback for this site. A D1 row only
    replaces it when it carries the same reviewed rich article payload; an
    unrelated water-cup Blog snapshot must never erase mould news.
    """
    # The checked-in editorial registry is a local fixture only.  In a strict
    # production build the published D1 rows are the complete list; no deleted
    # or unpublished article may be resurrected from the repository.
    reviewed = [] if STRICT_D1 else editorial_news_items(category)
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
        d1_editorial = row.get("editorial") if isinstance(row.get("editorial"), dict) else None
        editorial = d1_editorial or EDITORIAL_BY_SLUG.get(slug)
        d1_category = str((editorial or {}).get("category") or row.get("category") or "news")
        if d1_category != category:
            continue
        if not editorial:
            # New D1 articles do not need a Python registry entry.  The shared
            # detail template can still render a safe structured brief until
            # the editor adds richer sections.
            editorial = {"slug": slug, "category": category, "intro": {"en": summary, "es": str(row.get("summaryEs") or summary)}, "sections": {"en": [], "es": []}, "checklist": {"en": [], "es": []}, "faqs": {"en": [], "es": []}, "products": [], "related": [], "evidenceSources": []}
        mapped.append({
            "slug": slug, "title": title, "titleEs": str(row.get("titleEs") or row.get("title_es") or ""),
            "date": date, "image": image_src, "summary": summary,
            "summaryEs": str(row.get("summaryEs") or row.get("summary_es") or ""),
            "alt": str(row.get("alt") or title), "altEs": str(row.get("altEs") or row.get("alt_es") or title),
            "editorial": editorial,
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
                value["editorial"] = overrides[base["slug"]].get("editorial") or base.get("editorial")
            merged.append(value)
        known = {row["slug"] for row in merged}
        merged.extend(row for row in mapped if row["slug"] not in known)
        merged.sort(key=lambda row: (str(row.get("date") or ""), str(row.get("slug") or "")), reverse=True)
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
    if not row:
        for candidate in STATE.get("blogPosts", []) if isinstance(STATE.get("blogPosts"), list) else []:
            if str(candidate.get("slug") or "") != str(slug):
                continue
            row = candidate.get("editorial") if isinstance(candidate.get("editorial"), dict) else candidate
            break
    return "/news/" if row.get("category") == "news" else "/Bottle-Cap-Machine/"

def rich_news_body(locale: str, item: dict, category_label: str) -> str:
    """Render the seven-part GEO article without changing the shared shell."""
    editorial = item.get("editorial") if isinstance(item.get("editorial"), dict) else {}
    lang = "es" if locale == "es" else "en"
    if lang == "es":
        # Existing D1/editorial rows remain authoritative, but their Spanish
        # branches may contain the old mixed English baseline. Clean only the
        # Spanish-facing branches at render time so English/owner content is
        # preserved only for local preview; production requires translated D1 content.
        editorial = spanish_editorial_copy(editorial)
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
    product_links = []
    for product in products[:3]:
        label = (product.get("label") or {}).get(lang) or ("" if lang == "es" else (product.get("label") or {}).get("en") or "")
        reason = (product.get("reason") or {}).get(lang) or ("" if lang == "es" else (product.get("reason") or {}).get("en") or "")
        if label and reason:
            product_links.append('<a class="blog-editorial__product-link" href="' + localized_href(locale, product.get("route") or "/products/") + '"><strong>' + esc(label) + '</strong><span>' + esc(reason) + '</span></a>')
    product_html = '<section class="blog-products"><h2>' + product_title + '</h2><div class="blog-product-links">' + ''.join(product_links) + '</div></section>'
    related_title = "Related reading" if lang == "en" else "Lecturas relacionadas"
    related_cards = []
    for slug in related_slugs[:3]:
        related = EDITORIAL_BY_SLUG.get(str(slug))
        if not related:
            continue
        if lang == "es":
            related = spanish_editorial_copy(related)
        rtitle = (related.get("title") or {}).get(lang) or ("" if lang == "es" else (related.get("title") or {}).get("en"))
        rsummary = (related.get("description") or {}).get(lang) or ("" if lang == "es" else (related.get("description") or {}).get("en"))
        if not rtitle or not rsummary:
            continue
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
    redirects: list[str] = []
    legacy_aliases = (
        ("/about/about_us.html", "/about/"),
        ("/about/ABOUT_US.html", "/about/"),
        ("/machine/Cap-Auxiliary-Machines.html", "/capabilities/"),
        ("/contact/contact_us.html", "/contact/"),
        ("/cap-samples/Sample.html", "/samples/"),
        ("/news/news.html", "/news/"),
        ("/videolist/Cap-Mold-Video.html", "/video/"),
        ("/about/FAQs.html", "/faq/"),
    )
    for locale in LOCALES:
        code = locale["code"]
        for source_route, target_route in legacy_aliases:
            redirects.append(route_for(code, source_route) + " " + route_for(code, target_route) + " 301")
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
        if STRICT_D1 and locale != "en":
            required = ("title", "description", "mainHtml")
            missing = [key for key in required if not str(translated.get(key) or "").strip()]
            if missing:
                raise RuntimeError("Strict D1 translation missing for " + route + ":" + locale + ":" + ",".join(missing))
        final_title = str(translated.get("title") or page_override.get("seoTitle") or title)
        final_description = str(translated.get("description") or page_override.get("metaDescription") or description)
        # D1 translation rows are authoritative, but older rows may have been
        # seeded from the English SEO baseline.  Keep the D1 value while
        # applying the same reviewed Spanish boundary glossary used by the
        # visible renderer; otherwise an English title/description can leak
        # into <title>, Open Graph and JSON-LD even when the page body is
        # localized.
        if locale == "es":
            final_title = spanish_ui_text(final_title)
            final_description = spanish_ui_text(final_description)
        # xuyi_page_content stores the reviewed source-language body. A
        # localized D1 override wins for that locale; otherwise Spanish keeps
        # the renderer's translated baseline instead of silently showing an
        # English body from the source-language CMS row.
        source_body = BODY_OVERRIDES.get(route) if locale == "en" else ""
        localized_body = str(translated.get("mainHtml") or "")
        if locale == "es" and localized_body:
            # D1 page overrides are owner-authored HTML fragments.  Normalize
            # only their visible text nodes so stale English fragments cannot
            # bypass the structured renderer, while URLs, media attributes and
            # embedded scripts remain byte-for-byte intact.
            localized_body = spanish_html_text(localized_body)
        if locale == "es" and localized_body:
            # The first D1 translation seed stored the English reference HTML
            # in several Spanish overrides. Keep a genuinely Spanish owner
            # edit, but reject that known baseline so the structured renderer
            # can supply the reviewed locale page instead.
            plain = re.sub(r"<[^>]+>", " ", localized_body)
            # These are headings and sentence fragments from the first seed
            # that accidentally copied the English body into the Spanish D1
            # override.  Any one of them is enough to discard that stale
            # snapshot; the structured renderer below is the reviewed locale
            # fallback and keeps genuine Spanish owner edits intact.
            english_markers = (
                "OUR STORY", "PRECISION TOOLING", "OUR PRODUCTS", "Mould Product Families",
                "Factory Address", "Trial samples", "BOTTLE CAP MOULDS", "EXPLORE OUR WORK",
                "Quality Assurance", "What Buyers Say", "Common Questions", "Mould Trials",
                "Quality Control & Inspection", "Trial and validation", "Our Journey",
                "Why Choose LEYA MOULD", "Our Facility & Equipment", "Certifications & Quality",
                "Our Production Facilities", "Let's Work Together", "Plastic Cap Samples",
                "Engineering Excellence Behind Every Mould", "Start Your Cap Mould Project",
                "Want to See More Samples or Request a Quote", "Need Auxiliary Equipment for Your Cap Line?",
                "Mould Design & Engineering", "Mould Design and Engineering", "PROJECT FILES TO BE REVIEWED",
                "Drawing · sample · PDF · revision notes", "review drawings, parting lines, cooling",
            )
            if any(marker.lower() in plain.lower() for marker in english_markers):
                localized_body = ""
        final_body = str(localized_body or source_body or body)
        if locale == "es":
            # Apply one last visible-text pass to the selected body as well.
            # This covers legacy D1 fragments and source-rendered sections that
            # were assembled after the earlier override check, without
            # translating URLs, attributes or embedded script payloads.
            final_body = spanish_html_text(final_body)
        rendered = shell(locale, final_title + " | " + BRAND_DISPLAY if route != "/" else final_title + " | " + BRAND_DISPLAY, final_description, route, final_body)
        if locale == "es":
            # Final shell boundary: shared header/footer, title text and any
            # owner-authored fragment must use the same Spanish visible-text
            # rules. Attributes and embedded scripts remain untouched.
            rendered = spanish_html_text(rendered)
            # A legacy D1 row may place one isolated technical label in an
            # attribute or malformed fragment where the text-node splitter
            # cannot see it. Keep this single known label localized without
            # touching URLs or executable payloads.
            rendered = re.sub(r"(?i)(?<![A-Za-z])specification(?![A-Za-z])", "especificación", rendered)
        write(file_path, rendered)
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
        add(code, "/capabilities/", text(code, "capabilities"), text(code, "technical_text"), capabilities_page(code))
        capabilities_body = capabilities_page(code)
        for service in CATALOG["services"]:
            add(code, "/capabilities/" + service["slug"] + "/", service["title"], service["text"], service_page(code, service))
        add(code, "/manufacturing/", text(code, "process"), text(code, "process_title"), simple_page(code, "/manufacturing/", text(code, "process"), text(code, "process_title"), '<p>' + esc(text(code, "process_title")) + '</p><p>' + esc(text(code, "technical_text")) + '</p>'))
        add(code, "/quality-control/", text(code, "footer_quality"), text(code, "technical_text"), simple_page(code, "/quality-control/", text(code, "footer_quality"), text(code, "technical_text"), '<p>' + esc(text(code, "technical_text")) + '</p>'))
        add(code, "/request-sample/", text(code, "quote"), text(code, "resources_text"), contact_page(code))
        contact_body = contact_page(code)
        add(code, "/contact/", text(code, "contact"), text(code, "contact_intro"), contact_body)
        samples_title = "Plastic Cap Samples" if code == "en" else ("Muestras de tapas de plástico" if code == "es" else text(code, "samples"))
        samples_body = samples_page(code)
        add(code, "/samples/", samples_title, "Explore plastic bottle cap samples manufactured with precision moulds.", samples_body)
        news_title = "News & Updates" if code == "en" else "Noticias y novedades"
        news_description = "Stay informed with LEYA MOULD mould technology, project notes and engineering insights." if code == "en" else "Conozca las novedades técnicas y los proyectos de LEYA MOULD."
        news_category_label = "NOTICIAS Y NOVEDADES" if code == "es" else "NEWS & INSIGHTS"
        machine_category_label = "MÁQUINAS PARA TAPAS" if code == "es" else "BOTTLE CAP MACHINE"
        bottle_news_category_label = "NOTICIAS SOBRE MOLDES DE TAPAS" if code == "es" else "BOTTLE CAP MOULDS"
        news_body = news_listing_page(code, "/news/", news_title, news_description, news_items, "/news/", news_category_label)
        add(code, "/news/", news_title, news_description, news_body)
        add(code, "/news/Bottle-cap-molds.html", "Bottle Cap Mould News" if code == "en" else "Noticias sobre moldes de tapas", "Bottle cap mould project notes, market observations and practical production guidance." if code == "en" else "Notas de proyectos y orientación práctica sobre moldes de tapas.", news_listing_page(code, "/news/Bottle-cap-molds.html", "Bottle Cap Mould News" if code == "en" else "Noticias sobre moldes de tapas", "Bottle cap mould project notes, market observations and practical production guidance." if code == "en" else "Notas de proyectos y orientación práctica sobre moldes de tapas.", news_items, "/news/", bottle_news_category_label))
        add(code, "/Bottle-Cap-Machine/Bottle-Cap-Machine.html", "Bottle Cap Machine" if code == "en" else "Máquinas para tapas de botella", "Machine, process and quality notes for complete bottle-cap production lines." if code == "en" else "Notas de máquinas, procesos y calidad para líneas de tapas.", news_listing_page(code, "/Bottle-Cap-Machine/Bottle-Cap-Machine.html", "Bottle Cap Machine" if code == "en" else "Máquinas para tapas de botella", "Machine, process and quality notes for complete bottle-cap production lines." if code == "en" else "Notas de máquinas, procesos y calidad para líneas de tapas.", machine_news_items, "/Bottle-Cap-Machine/", machine_category_label))
        for item in news_items:
            detail_route = "/news/" + item["slug"] + ".html"
            add(code, detail_route, localized_item_text(item, code, "title"), localized_item_text(item, code, "summary"), news_detail_page(code, detail_route, item, "/news/Bottle-cap-molds.html", bottle_news_category_label))
        for item in machine_news_items:
            detail_route = "/Bottle-Cap-Machine/" + item["slug"] + ".html"
            add(code, detail_route, localized_item_text(item, code, "title"), localized_item_text(item, code, "summary"), news_detail_page(code, detail_route, item, "/Bottle-Cap-Machine/Bottle-Cap-Machine.html", machine_category_label))
        video_title = "Video Gallery" if code == "en" else "Galería de vídeos"
        video_description = "Watch our latest mould demonstrations, factory tours, and technical insights." if code == "en" else "Vea nuestras demostraciones de moldes y conocimientos técnicos."
        video_body = video_page(code)
        add(code, "/video/", video_title, video_description, video_body)
        add(code, "/faq/", text(code, "faq_title"), text(code, "faq_intro"), faq_page(code))
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
    write("_redirects", "\n".join(redirects) + "\n")
    return {"routes": routes, "locales": LOCALES}

if __name__ == "__main__":
    result = generate()
    print("LEYA_MOULD_SOURCE_BUILD_OK", "HTML_FILES", len(result["routes"]), "LOCALES", ",".join(x["code"] for x in result["locales"]))



