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
def effective_product_seo(product, locale):
    model = str(product.get("model") or "").lower()
    content = product.get("content") if isinstance(product.get("content"), dict) else {}
    suffix = "Es" if locale == "es" else ""
    title = content.get("seoTitle" + suffix) or content.get("titleEs" if locale == "es" else "title") or content.get("nameEs" if locale == "es" else "name")
    description = content.get("seoDescription" + suffix) or content.get("descriptionEs" if locale == "es" else "description") or content.get("shortEs" if locale == "es" else "short")
    if str(title or "").strip() and str(description or "").strip():
        return {"slug": model, "locale": locale, "seoTitle": str(title).strip(), "metaDescription": str(description).strip(), "source": "xuyi_product_content"}
    return None
missing = []
for product in products:
    model = str(product["model"]).lower()
    for locale in published:
        row = seo.get((model, locale)) or effective_product_seo(product, locale)
        if not row or not str(row.get("seoTitle") or "").strip() or not str(row.get("metaDescription") or "").strip():
            missing.append(f"{model}:{locale}")
if missing:
    raise SystemExit("D1 product SEO is incomplete: " + ", ".join(missing[:20]))

for post in state.get("blogPosts", []):
    if not isinstance(post, dict):
        continue
    if not str(post.get("titleEs") or "").strip() or not str(post.get("summaryEs") or "").strip():
        raise SystemExit("D1 Spanish News fields are incomplete: " + str(post.get("slug") or ""))

print("LEYA_MOULD_D1_COMPLETENESS_PASSED", f"products={len(products)}", f"seo={len(seo)}", f"locales={','.join(published)}")
