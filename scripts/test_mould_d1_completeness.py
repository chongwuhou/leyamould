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
registry_rows = [row for row in state.get("pageRegistry", state.get("pages", [])) if isinstance(row, dict) and clean_text(row.get("route"))]
registry_routes = {clean_text(row.get("route")) for row in registry_rows}
if registry_routes != page_routes:
    missing = sorted(page_routes - registry_routes)
    extra = sorted(registry_routes - page_routes)
    raise SystemExit("D1 page registry mismatch: missing=" + ",".join(missing[:10]) + " extra=" + ",".join(extra[:10]))
page_translation = translation_map(state.get("translations", []))
page_missing = []

# LEYA news detail pages are owned by the published D1 Blog rows themselves.
# They are rendered from each row's localized editorial payload, not from the
# legacy shared water-cup `xuyi_translation_overrides` `/blog/.../` records.
# Keep the generic page gate strict for managed shell/pages, while validating
# every news article's Spanish fields in the dedicated Blog gate below.
blog_detail_routes = set()
for post in state.get("blogPosts", []):
    if not isinstance(post, dict):
        continue
    slug = clean_text(post.get("slug"))
    if not slug:
        continue
    editorial = post.get("editorial") if isinstance(post.get("editorial"), dict) else post
    category = clean_text(editorial.get("category") or post.get("category") or "news").lower()
    prefix = "/Bottle-Cap-Machine/" if category in {"machine", "machines", "cap-machine"} else "/news/"
    blog_detail_routes.add(prefix + slug + ".html")
    # Ignore legacy shared-template aliases if they still exist in an older
    # D1 registry; they are not emitted by the LEYA renderer.
    blog_detail_routes.add("/blog/" + slug + "/")

for row in page_rows:
    route = clean_text(row.get("route"))
    if not clean_text(row.get("seo_title")) or not clean_text(row.get("meta_description")):
        page_missing.append(route + ":source-seo")
for route in sorted(page_routes - blog_detail_routes):
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
def effective_product_seo(product, locale):
    model = str(product.get("model") or "").lower()
    content = product.get("content") if isinstance(product.get("content"), dict) else {}
    suffix = "Es" if locale == "es" else ""
    title = content.get("seoTitle" + suffix) or content.get("titleEs" if locale == "es" else "title") or content.get("nameEs" if locale == "es" else "name")
    description = content.get("seoDescription" + suffix) or content.get("descriptionEs" if locale == "es" else "description") or content.get("shortEs" if locale == "es" else "short")
    if str(title or "").strip() and str(description or "").strip():
        return {"slug": model, "locale": locale, "seoTitle": str(title).strip(), "metaDescription": str(description).strip(), "source": "d1-content"}
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

# Product-family pages are rendered from structured D1 fields.  A title/SEO
# row alone is not enough: otherwise the renderer can silently fall back to
# the checked-in category fixture.  Validate the module shape for every
# published locale without assuming any historical catalogue total.
def structured_modules(value, label):
    issues = []
    if not isinstance(value, dict):
        return [label + ":structured"]
    for key in ("hero", "products", "advantages", "technology", "samples", "quality"):
        row = value.get(key)
        if key in {"hero", "technology"}:
            if not isinstance(row, dict):
                issues.append(label + ":" + key)
                continue
            if key == "hero" and not str(row.get("title") or "").strip():
                issues.append(label + ":hero.title")
            if key == "technology" and not isinstance(row.get("items"), list):
                issues.append(label + ":technology.items")
        elif not isinstance(row, list) or not row:
            issues.append(label + ":" + key)
    brief = value.get("projectBrief")
    if not isinstance(brief, dict):
        issues.append(label + ":projectBrief")
    else:
        if not isinstance(brief.get("scenarios"), list) or len(brief["scenarios"]) < 2:
            issues.append(label + ":projectBrief.scenarios")
        if not isinstance(brief.get("parameters"), list) or len(brief["parameters"]) < 3:
            issues.append(label + ":projectBrief.parameters")
        if not isinstance(brief.get("quoteChecklist"), list) or len(brief["quoteChecklist"]) < 4:
            issues.append(label + ":projectBrief.quoteChecklist")
        if not isinstance(brief.get("sources"), list) or not brief["sources"]:
            issues.append(label + ":projectBrief.sources")
        if not clean_text(brief.get("evidenceNote")):
            issues.append(label + ":projectBrief.evidenceNote")
    return issues

product_fields_missing = []
for product in products:
    model = str(product.get("model") or "").lower()
    content = product.get("content") if isinstance(product.get("content"), dict) else {}
    if not str(content.get("route") or "").strip():
        product_fields_missing.append(model + ":route")
    for locale in published:
        suffix = "Es" if locale == "es" else ""
        title = content.get("title" + suffix) or content.get("name" + suffix)
        description = content.get("description" + suffix) or content.get("short" + suffix)
        if not str(title or "").strip():
            product_fields_missing.append(model + ":" + locale + ":title")
        if not str(description or "").strip():
            product_fields_missing.append(model + ":" + locale + ":description")
        for base in ("body", "sections", "faqs"):
            value = content.get(base + suffix)
            minimum = 4 if base == "faqs" else (2 if base == "sections" else 1)
            if (not isinstance(value, list) and base != "body") or (isinstance(value, list) and len(value) < minimum) or (base == "body" and not clean_text(value)):
                product_fields_missing.append(model + ":" + locale + ":" + base)
        structured = content.get("structured") if isinstance(content.get("structured"), dict) else content.get("category")
        if locale == source_locale:
            product_fields_missing.extend(model + ":" + issue for issue in structured_modules(structured, locale))
        else:
            localized = content.get("structuredEs") if isinstance(content.get("structuredEs"), dict) else content.get("categoryEs")
            product_fields_missing.extend(model + ":" + issue for issue in structured_modules(localized, locale))
if product_fields_missing:
    raise SystemExit("D1 product structured fields are incomplete: " + ", ".join(product_fields_missing[:40]))

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


