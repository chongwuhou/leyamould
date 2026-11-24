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

ROOT = Path(__file__).resolve().parent
# The supplied logo is kept as a source asset so the published header can scale it without stretching.
CONFIG = json.loads((ROOT / "deployment/site.config.json").read_text(encoding="utf-8"))
ORIGIN = CONFIG["site"]["origin"]
INDEXING_APPROVED = CONFIG["site"].get("indexingApproved") is True
OUTPUT = ROOT / (os.environ.get("LEYA_OUTPUT_DIR") or ".")
CATALOG = json.loads((ROOT / "data/mould-catalog.json").read_text(encoding="utf-8"))
MODEL_DATA = json.loads((ROOT / "data/mould-models.json").read_text(encoding="utf-8")) if (ROOT / "data/mould-models.json").is_file() else {"models": []}
STATIC_HMOULD_MODELS = [row for row in MODEL_DATA.get("models", []) if isinstance(row, dict)]
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
    translations = row.get("translations")
    value["translations"] = translations if isinstance(translations, dict) else {}
    return value

_SNAPSHOT_MODEL_REFERENCES = [
    _normalise_model_reference(row) for row in STATE.get("modelReferences", [])
    if isinstance(row, dict) and row.get("slug") and row.get("family") and row.get("image")
]
# D1/CMS is authoritative only when it supplies a published, reviewed set.
# Empty or unavailable snapshots never blank the public catalogue.
HMOULD_MODELS = _SNAPSHOT_MODEL_REFERENCES or STATIC_HMOULD_MODELS
MODEL_REFERENCE_SOURCE = "cloudflare-d1:leya_model_references" if _SNAPSHOT_MODEL_REFERENCES else "source-fallback:data/mould-models.json"

# The static renderer remains the visual source of truth.  These small
# adapters make its business inputs data-driven in the same way as the
# water-cup project: a reviewed D1 snapshot can override content, while a
# clean checkout still has an auditable source fallback.  No CSS or layout is
# selected from D1, so a CMS edit cannot silently redesign the public site.
BRAND_CONFIG = STATE.get("brand") if isinstance(STATE.get("brand"), dict) else {}
CONTACT_CONFIG = STATE.get("contacts") if isinstance(STATE.get("contacts"), dict) else {}
NAVIGATION = [row for row in STATE.get("navigation", []) if isinstance(row, dict)]
COMMON_COPY = STATE.get("commonCopy") if isinstance(STATE.get("commonCopy"), dict) else {}
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
    return next((row for row in contacts if isinstance(row, dict) and row.get("enabled", True) and row.get("is