#!/usr/bin/env python3
"""Offline integrity and catalog-extension regression tests for the 58-model batch."""
from __future__ import annotations

import collections
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from catalog_extensions import append_new_products  # noqa: E402
from factory_catalog_locales import catalog_cards  # noqa: E402
from product_content import details as product_details, factory_catalog_seo_title  # noqa: E402

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

    # The four published non-English catalogs receive localized cards that
    # link to the English source-backed detail page until translations exist.
    empty_grid = '<div class="grid grid--4 product-grid"></div>'
    for locale in ("es", "pt", "ru", "tr"):
        localized = catalog_cards(empty_grid, locale, "/products/", set(), series)
        assert localized.count('data-new-product="true"') == 58
        for model in seen:
            assert f'href="/products/{model}/"' in localized
            assert f'href="/{locale}/products/{model}/"' not in localized
        category_slugs = {
            item["categorySlug"] for item in MANIFEST["models"]
        }
        for category_slug in category_slugs:
            category_count = sum(
                1 for item in MANIFEST["models"] if item["categorySlug"] == category_slug
            )
            category_html = catalog_cards(
                empty_grid, locale, f"/collections/{category_slug}/", set(), series
            )
            assert category_html.count('data-new-product="true"') == category_count

    print(f"PASS: {len(series)} new products, {len(hashes)} unique WebP images, {len(category_counts)} categories.")


if __name__ == "__main__":
    main()