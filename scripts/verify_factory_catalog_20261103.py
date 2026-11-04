#!/usr/bin/env python3
"""Post-deploy live verification for the 58 reviewed XUYI factory catalog products."""
from __future__ import annotations

import concurrent.futures
import html
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://xuyibottles.com"
MANIFEST = json.loads((ROOT / "data/factory-catalog-manifest-2026-11-03.json").read_text(encoding="utf-8"))
BUNDLE = json.loads((ROOT / "scripts/fixtures/factory-catalog-import-2026-11-03.json").read_text(encoding="utf-8"))
LOCALES = ("es", "pt", "ru", "tr")


def fetch(path: str) -> tuple[int, str]:
    request = urllib.request.Request(
        ORIGIN + path,
        headers={"User-Agent": "XUYI-Factory-Catalog-Live-Verification/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return response.status, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", "replace")


def require_page(path: str) -> str:
    status, body = fetch(path)
    if status != 200:
        raise RuntimeError(f"{path} returned HTTP {status}")
    return body

def built_title(slug: str) -> str:
    """Use the exact fresh D1-derived artifact as the live title authority."""
    artifact = ROOT / "dist" / "products" / slug / "index.html"
    if not artifact.is_file():
        raise RuntimeError(f"{artifact} is missing from the fresh release build.")
    markup = artifact.read_text(encoding="utf-8")
    match = re.search(r"<title>(.*?)</title>", markup, re.I | re.S)
    if not match:
        raise RuntimeError(f"{artifact} has no HTML title.")
    return html.unescape(match.group(1).strip())


def verify_product(record: dict) -> str:
    model = record["model"].lower()
    content = record["content"]
    slug = model
    path = f"/products/{slug}/"
    body = require_page(path)
    if model.upper() not in body and str(content.get("factoryModel", "")) not in body:
        raise RuntimeError(f"{path} does not show its factory model.")
    image = f"/media/product/{record['imageSha256'][:32]}.webp"
    if image not in body:
        raise RuntimeError(f"{path} does not reference its verified R2 image.")
    if "Factory Catalog Source" not in body or "Factory Catalog Page" not in body:
        raise RuntimeError(f"{path} is missing source provenance.")
    if str(content.get("sourcePage")) not in body:
        raise RuntimeError(f"{path} is missing its PDF source page.")
    if content.get("qcStatus") == "needs_confirmation" and "Catalog Notes" not in body:
        raise RuntimeError(f"{path} is missing the required source-confirmation note.")
    title = re.search(r"<title>(.*?)</title>", body, re.I | re.S)
    if not title:
        raise RuntimeError(f"{path} has no HTML title.")
    live_title = html.unescape(title.group(1).strip())
    expected_title = built_title(slug)
    if live_title != expected_title:
        raise RuntimeError(f"{path} live title differs from the fresh D1-derived release artifact: {live_title!r} (expected {expected_title!r})")
    if model.upper() not in live_title.upper() or "XUYI" not in live_title.upper():
        raise RuntimeError(f"{path} title must retain its factory model and XUYI brand: {live_title!r}")
    canonical = f'<link rel="canonical" href="{ORIGIN}{path}"'
    if canonical not in body:
        raise RuntimeError(f"{path} canonical URL is missing or incorrect.")
    for locale in LOCALES:
        if f'hreflang="{locale}"' not in body:
            raise RuntimeError(f"{path} is missing its reviewed {locale} alternate.")
    return model


def verify_localized_product(record: dict, locale: str) -> str:
    model=record["model"].lower()
    content=record["content"]
    path=f"/{locale}/products/{model}/"
    body=require_page(path)
    if f'<html lang="{locale}">' not in body:
        raise RuntimeError(f"{path} has the wrong document language.")
    if str(content.get("factoryModel") or model) not in body:
        raise RuntimeError(f"{path} does not show its factory model.")
    if f'<link rel="canonical" href="{ORIGIN}{path}">' not in body:
        raise RuntimeError(f"{path} has a missing or incorrect canonical.")
    if f'hreflang="{locale}"' not in body or 'hreflang="x-default"' not in body:
        raise RuntimeError(f"{path} is missing its localized hreflang set.")
    if "Product" not in body or "Frequently asked questions" not in body and locale=="en":
        raise RuntimeError(f"{path} is missing product or visible FAQ content.")
    title=re.search(r"<title>(.*?)</title>",body,re.I|re.S)
    if not title or model.upper() not in html.unescape(title.group(1)).upper():
        raise RuntimeError(f"{path} has no model-specific localized title.")
    return model


def main() -> None:
    records = BUNDLE["records"]
    if len(records) != 58 or MANIFEST.get("recordCount") != 58:
        raise RuntimeError("Live verification fixture is not exactly 58 products.")
    models = {record["model"].lower() for record in records}
    if len(models) != 58:
        raise RuntimeError("Duplicate models in verification fixture.")

    # Every English detail route must be live and source-attributed.
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(verify_product, records))
    if set(results) != models:
        raise RuntimeError("Not all 58 English product pages were verified.")

    # The main English catalog and all six collection pages must expose the
    # complete source-reviewed product set in the correct categories.
    listing = require_page("/products/")
    for model in models:
        if f'href="/products/{model}/"' not in listing:
            raise RuntimeError(f"/products/ is missing model {model}.")

    by_category: dict[str, set[str]] = {}
    for row in MANIFEST["models"]:
        by_category.setdefault(row["categorySlug"], set()).add(row["model"])
    for slug, category_models in by_category.items():
        body = require_page(f"/collections/{slug}/")
        for model in category_models:
            if f'href="/products/{model}/"' not in body:
                raise RuntimeError(f"/collections/{slug}/ is missing model {model}.")

    # Every localized catalog and detail route now resolves natively.
    for locale in LOCALES:
        body = require_page(f"/{locale}/products/")
        for model in models:
            href=f'href="/{locale}/products/{model}/"'
            if href not in body:
                raise RuntimeError(f"/{locale}/products/ is missing its native detail card for {model}.")
            if f'href="/products/{model}/"' in body:
                raise RuntimeError(f"/{locale}/products/ still points to the English detail for {model}.")
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            localized_results=list(pool.map(lambda record:verify_localized_product(record,locale),records))
        if set(localized_results)!=models:
            raise RuntimeError(f"Not all localized {locale} product pages were verified.")

    sitemap = require_page("/sitemap.xml")
    for model in models:
        route = f"{ORIGIN}/products/{model}/"
        if route not in sitemap:
            raise RuntimeError(f"Sitemap is missing {route}.")
        for locale in LOCALES:
            localized_route=f"{ORIGIN}/{locale}/products/{model}/"
            if localized_route not in sitemap:
                raise RuntimeError(f"Sitemap is missing localized route {localized_route}.")

    print(json.dumps({
        "result": "PASS",
        "englishProductPages": len(models),
        "englishCatalogCards": len(models),
        "categoryPages": len(by_category),
        "localizedCatalogsWithNativeProductLinks": list(LOCALES),
        "localizedProductDetailPages": len(models)*len(LOCALES),
        "sitemapProductRoutes": len(models),
        "sourceSha256": MANIFEST["sourceSha256"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("FACTORY_CATALOG_LIVE_VERIFY_FAILED:", error, file=sys.stderr)
        raise