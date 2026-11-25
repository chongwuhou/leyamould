#!/usr/bin/env python3
"""Fail the release when the published D1 snapshot is incomplete.

This is intentionally a local snapshot check: it never calls Cloudflare or a
translation service.  The workflow fetches the authenticated snapshot first;
local visual builds without that file remain usable.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mould_build import ES_SEO  # noqa: E402
snapshot_path = ROOT / "_local_ops" / "build-snapshot.json"
if not snapshot_path.is_file():
    if os.environ.get("LEYA_REQUIRE_D1_SNAPSHOT") in {"1", "true", "yes"}:
        raise SystemExit("D1 snapshot is required for a production completeness check")
    print("LEYA_MOULD_D1_COMPLETENESS_SKIPPED no snapshot")
    raise SystemExit(0)

state = json.loads(snapshot_path.read_text(encoding="utf-8"))
if state.get("site") != "leyamould":
    raise SystemExit("unexpected build snapshot site")

languages = state.get("languages") or {}
published = [str(row.get("code") or "").lower() for row in languages.get("languages", []) if row.get("enabled") and row.get("publishReady")]
published = published or ["en", "es"]
if not {"en", "es"}.issubset(set(published)):
    raise SystemExit("LEYA requires reviewed English and Spanish publish locales")
source_locale = str(languages.get("sourceLocale") or "en").lower()
if source_locale not in published:
    raise SystemExit(f"source locale is not publish-ready: {source_locale}")

def clean_text(value):
    return str(value or "").strip()

def translation_map(rows):
    result = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        resource = clean_text(row.get("resourceId"))
        locale = clean_text(row.get("locale")).lower()
        content = row.get("content") if isinstance(row.get("content"), dict) else {}
        if resource and locale:
            result[(resource, locale)] = content
    return result

# Production cannot silently ship source-language fallback as a translated
# page. Every managed page therefore needs a complete reviewed D1 override per
# publish locale.  The renderer fallback is intentionally not accepted here.
page_rows = [row for row in state.get("pages", []) if isinstance(row, dict) and clean_text(row.get("route"))]
page_routes = {clean_text(row.get("route")) for row in page_rows}
page_routes.update(clean_text(row.get("route")) for row in state.get("pageBodies", []) if isinstance(row, dict) and clean_text(row.get("route")))
page_translation = translation_map(state.get("translations", []))
page_missing = []

for row in page_rows:
    route = clean_text(row.get("route"))
    if not clean_text(row.get("seo_title")) or not clean_text(row.get("meta_description")):
        page_missing.append(route + ":source-seo")
for route in sorted(page_routes):
    has_body = any(isinstance(item, dict) and clean_text(item.get("route")) == route and len(clean_text(item.get("mainHtml"))) >= 100 for item in state.get("pageBodies", []))
    for locale in published:
        if locale == source_locale:
            continue
        content = page_translation.get(("page:" + route, locale))
        if not content or not clean_text(content.get("title")) or not clean_text(content.get("description")):
            page_missing.append(f"{route}:{locale}:title-description")
        if not content or len(clean_text(content.get("mainHtml"))) < 120:
            page_missing.append(f"{route}:{locale}:mainHtml")
if page_missing:
    raise SystemExit("D1 page language/SEO completeness is incomplete: " + ", ".join(page_missing[:40]))

products = [row for row in state.get("products", []) if isinstance(row, dict) and re.fullmatch(r"[a-z0-9][a-z0-9-]{1,63}", str(row.get("model") or ""))]
seo = {(str(row.get("slug") or "").lower(), str(row.get("locale") or "").lower()): row for row in state.get("productSeo", []) if isinstance(row, dict)}
catalog = {}
catalog_path = ROOT / "data" / "mould-catalog.json"
if catalog_path.is_file():
    try:
        catalog = {str(row.get("slug") or "").lower(): row for row in (json.loads(catalog_path.read_text(encoding="utf-8")).get("categories") or []) if isinstance(row, dict)}
    except (OSError, ValueError):
        catalog = {}
def effective_product_seo(product, locale):
    model = str(product.get("model") or "").lower()
    content = product.get("content") if isinstance(product.get("content"), dict) else {}
    suffix = "Es" if locale == "es" else ""
    title = content.get("seoTitle" + suffix) or content.get("titleEs" if locale == "es" else "title") or content.get("nameEs" if locale == "es" else "name")
    description = content.get("seoDescription" + suffix) or content.get("descriptionEs" if locale == "es" else "description") or content.get("shortEs" if locale == "es" else "short")
    if not str(title or "").strip() or not str(description or "").strip():
        baseline = catalog.get(model) or {}
        title = title or baseline.get("titleEs" if locale == "es" else "title")
        description = description or baseline.get("descriptionEs" if locale == "es" else "description")
    if str(title or "").strip() and str(description or "").strip():
        return {"slug": model, "locale": locale, "seoTitle": str(title).strip(), "metaDescription": str(description).strip(), "source": "d1-content-or-reviewed-catalog"}
    return None
missing = []
effective_count = 0
for product in products:
    model = str(product["model"]).lower()
    for locale in published:
        row = seo.get((model, locale)) if locale != source_locale else (seo.get((model, locale)) or effective_product_seo(product, locale))
        if not row or not str(row.get("seoTitle") or "").strip() or not str(row.get("metaDescription") or "").strip():
            missing.append(f"{model}:{locale}")
        else:
            effective_count += 1
if missing:
    raise SystemExit("D1 product SEO is incomplete: " + ", ".join(missing[:20]))

product_routes = set()
for product in products:
    content = product.get("content") if isinstance(product.get("content"), dict) else {}
    route = str(content.get("route") or "").strip()
    if route:
        product_routes.add(route)

def localized_value(value, locale):
    if isinstance(value, dict):
        return value.get(locale)
    return value

blog_checked = 0
for post in state.get("blogPosts", []):
    if not isinstance(post, dict):
        continue
    editorial = post.get("editorial") if isinstance(post.get("editorial"), dict) else post
    slug = str(post.get("slug") or "")
    for locale in published:
        title = post.get("title") if locale == "en" else post.get("titleEs")
        summary = post.get("summary") if locale == "en" else post.get("summaryEs")
        sections = localized_value(editorial.get("sections"), locale)
        checklist = localized_value(editorial.get("checklist"), locale)
        faqs = localized_value(editorial.get("faqs"), locale)
        products_in_post = localized_value(editorial.get("products"), locale)
        related = editorial.get("related")
        if not str(title or "").strip() or not str(summary or "").strip():
            raise SystemExit(f"D1 Blog localized title/summary is incomplete: {slug}:{locale}")
        if not isinstance(sections, list) or len(sections) < 7:
            raise SystemExit(f"D1 Blog requires 7 sections: {slug}:{locale}")
        if not isinstance(checklist, list) or len(checklist) < 10:
            raise SystemExit(f"D1 Blog requires 10 checklist items: {slug}:{locale}")
        if not isinstance(faqs, list) or len(faqs) < 4:
            raise SystemExit(f"D1 Blog requires 4 FAQs: {slug}:{locale}")
        if not isinstance(products_in_post, list) or not 2 <= len(products_in_post) <= 5:
            raise SystemExit(f"D1 Blog requires 2-5 product links: {slug}:{locale}")
        for item in products_in_post:
            route = str(item.get("route") if isinstance(item, dict) else item).strip()
            if route and product_routes and route not in product_routes:
                raise SystemExit(f"D1 Blog product link is not a published product route: {slug}:{locale}:{route}")
        if not isinstance(related, list) or not 2 <= len(related) <= 3 or len(set(str(item) for item in related)) != len(related):
            raise SystemExit(f"D1 Blog requires 2-3 unique related articles: {slug}")
    blog_checked += 1

model_checked = 0
model_missing = []
model_slugs = set()
for row in state.get("modelReferences", []):
    if not isinstance(row, dict):
        continue
    slug = clean_text(row.get("slug")).lower()
    if not slug or slug in model_slugs:
        model_missing.append(slug or "unknown:duplicate-slug")
    model_slugs.add(slug)
    required = ("slug", "family", "title", "alt", "image")
    if any(not str(row.get(key) or "").strip() for key in required):
        model_missing.append(str(row.get("slug") or "unknown"))
    if row.get("sourceUrl") and not str(row.get("sourceUrl")).startswith(("https://", "http://")):
        model_missing.append(str(row.get("slug") or "unknown") + ":source")
    if not clean_text(row.get("sourceUrl")).startswith("https://") or not clean_text(row.get("sourceImage")).startswith("https://"):
        model_missing.append(str(row.get("slug") or "unknown") + ":verified-source")
    if not clean_text(row.get("image")).startswith("/media/"):
        model_missing.append(str(row.get("slug") or "unknown") + ":r2-image")
    translations = row.get("translations") if isinstance(row.get("translations"), dict) else {}
    source_description = clean_text(row.get("description"))
    for locale in published:
        if locale == source_locale:
            continue
        localized = translations.get(locale) if isinstance(translations.get(locale), dict) else {}
        if not clean_text(localized.get("title")) or not clean_text(localized.get("alt")):
            model_missing.append(str(row.get("slug") or "unknown") + ":" + locale + ":title-alt")
        if source_description and not clean_text(localized.get("description")):
            model_missing.append(str(row.get("slug") or "unknown") + ":" + locale + ":description")
    if clean_text(row.get("pdfUrl")) and (len(clean_text(row.get("pdfSha256"))) != 64 or int(row.get("pdfPages") or 0) < 1):
        model_missing.append(str(row.get("slug") or "unknown") + ":pdf-metadata")
    model_checked += 1
if model_missing:
    raise SystemExit("Published model reference fields are incomplete: " + ", ".join(model_missing[:20]))
if os.environ.get("LEYA_REQUIRE_D1_SNAPSHOT") in {"1", "true", "yes"} and model_checked == 0:
    raise SystemExit("Production D1 snapshot contains no published model references")

for review in state.get("productReviews", []):
    if not isinstance(review, dict) or not clean_text(review.get("sourceUrl")).startswith("https://"):
        raise SystemExit("Published product reviews require a verified HTTPS source URL")

for post in state.get("blogPosts", []):
    if not isinstance(post, dict):
        continue
    if not str(post.get("titleEs") or "").strip() or not str(post.get("summaryEs") or "").strip():
        raise SystemExit("D1 Spanish News fields are incomplete: " + str(post.get("slug") or ""))

print("LEYA_MOULD_D1_COMPLETENESS_PASSED", f"products={len(products)}", f"effectiveSeo={effective_count}", f"explicitSeo={len(seo)}", f"blogPosts={blog_checked}", f"modelReferences={model_checked}", f"locales={','.join(published)}")


