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
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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
        row = seo.get((model, locale)) or effective_product_seo(product, locale)
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
for row in state.get("modelReferences", []):
    if not isinstance(row, dict):
        continue
    required = ("slug", "family", "title", "alt", "image")
    if any(not str(row.get(key) or "").strip() for key in required):
        model_missing.append(str(row.get("slug") or "unknown"))
    if row.get("sourceUrl") and not str(row.get("sourceUrl")).startswith(("https://", "http://")):
        model_missing.append(str(row.get("slug") or "unknown") + ":source")
    model_checked += 1
if model_missing:
    raise SystemExit("Published model reference fields are incomplete: " + ", ".join(model_missing[:20]))

for post in state.get("blogPosts", []):
    if not isinstance(post, dict):
        continue
    if not str(post.get("titleEs") or "").strip() or not str(post.get("summaryEs") or "").strip():
        raise SystemExit("D1 Spanish News fields are incomplete: " + str(post.get("slug") or ""))

print("LEYA_MOULD_D1_COMPLETENESS_PASSED", f"products={len(products)}", f"effectiveSeo={effective_count}", f"explicitSeo={len(seo)}", f"blogPosts={blog_checked}", f"modelReferences={model_checked}", f"locales={','.join(published)}")

