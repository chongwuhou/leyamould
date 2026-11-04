#!/usr/bin/env python3
"""Offline integrity and catalog-extension regression tests for the 58-model batch."""
from __future__ import annotations

import collections
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from catalog_extensions import append_new_products, is_factory_catalog_source_default  # noqa: E402
from factory_catalog_locales import LABELS, catalog_cards  # noqa: E402
from gallery_catalog import catalog_cards as gallery_catalog_cards  # noqa: E402
from lo_catalog import catalog_cards as lo_catalog_cards  # noqa: E402
from product_content import details as product_details, factory_catalog_seo_title  # noqa: E402
from scripts.cms_seo_curation_guard import current_field  # noqa: E402
from scripts.source_catalog_capacity_oz import KIND, catalog_volume_numbers, new_seo  # noqa: E402

BUNDLE = json.loads((ROOT / "scripts/fixtures/factory-catalog-import-2026-11-03.json").read_text(encoding="utf-8"))
IMAGES_ZIP = ROOT / "scripts/fixtures/factory-catalog-images-2026-11-03.zip"
MANIFEST = json.loads((ROOT / "data/factory-catalog-manifest-2026-11-03.json").read_text(encoding="utf-8"))
LANGUAGES = {"en", "es", "pt", "ru", "tr"}


def models_from(path: Path, key: str | None = None) -> set[str]:
    value = json.loads(path.read_text(encoding="utf-8"))
    rows = value if isinstance(value, list) else value.get(key or "products", [])
    return {str(row.get("model") or "").lower() for row in rows if row.get("model")}


def main() -> None:
    assert MANIFEST["site"] == "xuyi-drinkware-site"
    assert MANIFEST["recordCount"] == 58
    assert len(MANIFEST["models"]) == 58
    assert len(BUNDLE["records"]) == 58
    assert BUNDLE["sourceSha256"] == MANIFEST["sourceSha256"]

    expected = {row["model"]: row for row in MANIFEST["models"]}
    seen: set[str] = set()
    hashes: set[str] = set()
    category_counts: collections.Counter[str] = collections.Counter()
    extension_rows = []
    images = zipfile.ZipFile(IMAGES_ZIP, "r")

    for record in BUNDLE["records"]:
        model = record["model"].lower()
        assert model in expected and model not in seen
        seen.add(model)
        spec = expected[model]
        content = dict(record["content"])
        assert record["status"] == "published"
        assert content["newProduct"] is True
        assert is_factory_catalog_source_default(model,content,"seoTitle")
        assert is_factory_catalog_source_default(model,content,"seoDescription")
        owner_edited={**content,"seoTitle":content["seoTitle"]+" | Owner edit"}
        assert not is_factory_catalog_source_default(model,owner_edited,"seoTitle")
        snapshot_data={"products":[{"model":model,"content":content}]}
        route="/products/"+model+"/"
        assert current_field("en",route,"title",snapshot_data) is None
        assert current_field("en",route,"description",snapshot_data) is None
        edited_snapshot={"products":[{"model":model,"content":owner_edited}]}
        assert current_field("en",route,"title",edited_snapshot)==owner_edited["seoTitle"]
        assert content["factoryModel"] == spec["factoryModel"]
        assert content["category"] == spec["category"]
        assert str(content["sourcePage"]) == str(spec["sourcePage"])
        assert content["sourceDocument"] == MANIFEST["sourceDocument"]
        assert content["sourceSha256"] == MANIFEST["sourceSha256"]
        assert content["sourceImageSha256"] == spec["imageSha256"]
        assert content["imageReviewStatus"] == "visually_reviewed_source_crop"
        assert content["qcStatus"] in {"source_read", "needs_confirmation"}
        assert record["imageMime"] == "image/webp"

        image = images.read(model + ".webp")
        digest = hashlib.sha256(image).hexdigest()
        assert digest == record["imageSha256"] == spec["imageSha256"]
        assert image[:4] == b"RIFF" and image[8:12] == b"WEBP"
        assert 200 <= len(image) <= 6 * 1024 * 1024
        assert digest not in hashes
        hashes.add(digest)

        alt = record["imageAlt"]
        assert set(alt) == LANGUAGES
        assert all(isinstance(alt[code], str) and 0 < len(alt[code]) <= 180 for code in LANGUAGES)
        if content["qcStatus"] == "needs_confirmation":
            assert content.get("sourceNotes")
            assert any(word in content.get("description", "").lower() for word in ("confirm", "verify", "catalog"))
        if content["category"] == "Titanium Vacuum Cups":
            assert "pure titanium" not in content.get("name", "").lower()
            assert "confirm exact sku" in content.get("material", "").lower()

        content["image"] = f"/media/product/{digest[:32]}.webp"
        extension_rows.append({"model": model, "content": content, "publication_status": "published"})
        category_counts[content["category"]] += 1

    images.close()

    assert seen == set(expected)
    assert len(hashes) == 58
    assert dict(sorted(category_counts.items())) == dict(sorted(MANIFEST["categories"].items()))

    static_models = set()
    static_models |= models_from(ROOT / "data/products.json")
    static_models |= models_from(ROOT / "data/lo-products.json")
    static_models |= models_from(ROOT / "data/gallery-reference-products.json", "items")
    assert not (seen & static_models), "The new PDF batch overlaps the existing static catalog."

    series = {}
    append_new_products(series, extension_rows)
    assert len(series) == 58
    assert set(MANIFEST["categories"]).issubset(KIND["en"])
    for locale in LANGUAGES:
        assert set(MANIFEST["categories"]).issubset(KIND[locale]), locale
    for model, product in series.items():
        numbers = catalog_volume_numbers(product)
        if numbers:
            for locale in LANGUAGES:
                title, description = new_seo(locale, product, numbers)
                assert len(title) <= 60, (locale, model, title)
                assert len(description) <= 180, (locale, model, description)
    for model, product in series.items():
        assert product.get("manualNew") is True
        assert product.get("slug") == model
        assert product.get("images") == [f"/media/product/{expected[model]['imageSha256'][:32]}.webp"]
        assert product.get("category") in MANIFEST["categories"]
        seo_title = factory_catalog_seo_title(product)
        assert len(seo_title) <= 60, (model, len(seo_title), seo_title)
        assert str(product.get("factoryModel") or model).upper() in seo_title.upper(), (model, seo_title)
        assert "XUYI" in seo_title, (model, seo_title)
        rendered = product_details(product)
        assert "Factory Catalog Source" in rendered, model
        assert MANIFEST["sourceDocument"] in rendered, model
        assert "Factory Catalog Page" in rendered, model
        assert f"Page {expected[model]['sourcePage']}" in rendered, model
        if product.get("qcStatus") == "needs_confirmation":
            assert "Catalog Notes" in rendered, model

    # The source fragment uses root-relative detail routes. Since native
    # translations now exist, card labels must point to the localized detail pages;
    # render_locales applies the locale prefix after this component is composed.
    empty_grid = '<div class="grid grid--4 product-grid"></div>'
    for locale in ("es", "pt", "ru", "tr"):
        # The production renderer inserts gallery cards, hoists LO, then adds
        # factory cards. Both established groups must remain ahead of the batch.
        gallery_first = gallery_catalog_cards(empty_grid, locale, "/products/")
        lo_first = lo_catalog_cards(gallery_first, locale, "/products/")
        translated_routes={f"/products/{row['slug']}/" for row in series.values()}
        localized = catalog_cards(lo_first, locale, "/products/", translated_routes, series)
        assert localized.count('data-new-product="true"') == 66
        card_urls = [
            re.search(r'\bhref="([^"]+)"', match.group(0)).group(1)
            for match in re.finditer(r'<a\b[^>]*\bdata-product-card\b[^>]*>', localized, re.I)
        ]
        priority_urls = [
            re.search(r'\bhref="([^"]+)"', match.group(0)).group(1)
            for match in re.finditer(r'<a\b[^>]*\bdata-product-card\b[^>]*>', lo_first, re.I)
        ]
        expected_lo = [f'/{locale}/products/lo-{number:03d}/' for number in range(1, 9)]
        assert priority_urls[:8] == expected_lo, (locale, "LO products must be first")
        assert len(priority_urls) == 16, (locale, "expected eight LO and eight gallery priority cards")
        assert card_urls[:16] == priority_urls, (locale, "LO and gallery priority groups must precede factory cards")
        assert all(f'href="/products/{model}/"' in localized for model in seen), (locale, "factory cards missing after priority groups")
        render_source = (ROOT / "scripts/render_locales.py").read_text(encoding="utf-8")
        gallery_at = render_source.index("body=gallery_catalog_cards(body,loc,route)")
        lo_at = render_source.index("body=catalog_cards(body,loc,route)", gallery_at)
        factory_at = render_source.index("body=factory_catalog_cards(body,loc,route,routes_by_locale[loc])")
        assert gallery_at < lo_at < factory_at, "factory catalog must preserve the established LO priority pass"
        for model in seen:
            assert f'href="/products/{model}/"' in localized
            assert f'href="/{locale}/products/{model}/"' not in localized
            card = re.search(r'<a\b(?=[^>]*data-product-card\b)(?=[^>]*href="/products/'+re.escape(model)+r'/")[^>]*>.*?</a>',localized,re.I|re.S)
            assert card and LABELS[locale]["details"] in card.group(0),(locale,model,"native detail label")
        category_slugs = {
            item["categorySlug"] for item in MANIFEST["models"]
        }
        for category_slug in category_slugs:
            category_count = sum(
                1 for item in MANIFEST["models"] if item["categorySlug"] == category_slug
            )
            category_route = f"/collections/{category_slug}/"
            gallery_category_first = gallery_catalog_cards(empty_grid, locale, category_route)
            lo_category_first = lo_catalog_cards(gallery_category_first, locale, category_route)
            category_html = catalog_cards(lo_category_first, locale, category_route, translated_routes, series)
            expected_priority_category = [
                re.search(r'\bhref="([^"]+)"', match.group(0)).group(1)
                for match in re.finditer(r'<a\b[^>]*\bdata-product-card\b[^>]*>', lo_category_first, re.I)
            ]
            expected_lo_category_count = sum("/products/lo-" in url for url in expected_priority_category)
            category_urls = [
                re.search(r'\bhref="([^"]+)"', match.group(0)).group(1)
                for match in re.finditer(r'<a\b[^>]*\bdata-product-card\b[^>]*>', category_html, re.I)
            ]
            assert category_urls[:len(expected_priority_category)] == expected_priority_category, (
                locale, category_slug, "LO/gallery category cards must remain first"
            )
            assert category_html.count('data-new-product="true"') == category_count + expected_lo_category_count

    print(f"PASS: {len(series)} new products, {len(hashes)} unique WebP images, {len(category_counts)} categories.")


if __name__ == "__main__":
    main()