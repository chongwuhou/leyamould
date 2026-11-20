#!/usr/bin/env python3
"""Offline integrity and catalog-extension regression tests for the 58-model batch."""
from __future__ import annotations

import collections
import hashlib
import html
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from catalog_extensions import append_new_products, is_factory_catalog_source_default  # noqa: E402
from factory_catalog_locales import LABELS, catalog_cards, _card_title  # noqa: E402
from factory_product_locales import localized_name  # noqa: E402
from site_renderer import product_card as english_product_card, CAT  # noqa: E402
from gallery_catalog import catalog_cards as gallery_catalog_cards  # noqa: E402
from lo_catalog import catalog_cards as lo_catalog_cards  # noqa: E402
from product_content import details as product_details, factory_catalog_seo_title  # noqa: E402
from scripts.cms_seo_curation_guard import current_field  # noqa: E402
from scripts.source_catalog_capacity_oz import KIND, catalog_volume_numbers, new_seo, volume_terms, product_h1_text, verified_source_color_term  # noqa: E402

BUNDLE = json.loads((ROOT / "scripts/fixtures/factory-catalog-import-2026-11-03.json").read_text(encoding="utf-8"))
IMAGES_ZIP = ROOT / "scripts/fixtures/factory-catalog-images-2026-11-03.zip"
MANIFEST = json.loads((ROOT / "data/factory-catalog-manifest-2026-11-03.json").read_text(encoding="utf-8"))
LANGUAGES = {"en", "es", "pt", "ru", "tr"}


def models_from(path: Path, key: str | None = None) -> set[str]:
    value = json.loads(path.read_text(encoding="utf-8"))
    rows = value if isinstance(value, list) else value.get(key or "products", [])
    return {str(row.get("model") or "").lower() for row in rows if row.get("model")}


def main() -> None:
    assert MANIFEST["site"] == "leyamould"
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
        numbers = catalog_volume_numbers(product)
        assert product.get("manualNew") is True
        assert product.get("slug") == model
        assert product.get("images") == [f"/media/product/{expected[model]['imageSha256'][:32]}.webp"]
        assert product.get("category") in MANIFEST["categories"]
        seo_title = factory_catalog_seo_title(product)
        assert len(seo_title) <= 60, (model, len(seo_title), seo_title)
        assert str(product.get("factoryModel") or model).upper() in seo_title.upper(), (model, seo_title)
        assert "XUYI" in seo_title, (model, seo_title)
        if product.get("category") != "Two-Way Drinking Cups":
            expected_card_title=product_h1_text("en",product)
            assert _card_title(product,"en")==expected_card_title,(model,"English B2B card title",_card_title(product,"en"),expected_card_title)
            assert "B2B" in expected_card_title and "Manufacturer" in expected_card_title,(model,expected_card_title)
            if numbers:
                assert volume_terms(numbers,"en") in expected_card_title,(model,"card title missing mL/oz",expected_card_title)
            color=verified_source_color_term("en",product)
            if color:
                assert color.casefold() in expected_card_title.casefold(),(model,"card title missing verified color",color,expected_card_title)
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
            row=series[model]
            if row.get("category") != "Two-Way Drinking Cups":
                heading=re.search(r"<h3>(.*?)</h3>",card.group(0),re.I|re.S)
                assert heading,(locale,model,"factory card missing title")
                title=html.unescape(heading.group(1)).strip()
                assert title==product_h1_text(locale,row),(locale,model,"localized B2B card title",title)
                color=verified_source_color_term(locale,row)
                if color:
                    assert color.casefold() in title.casefold(),(locale,model,"localized card title missing color",color,title)
        two_way_rows = [row for row in series.values() if row.get("category") == "Two-Way Drinking Cups"]
        assert len(two_way_rows) == 20, ("expected all 20 two-way models", len(two_way_rows))
        two_way_route = "/collections/two-way-drinking-cups/"
        two_way_gallery = gallery_catalog_cards(empty_grid, locale, two_way_route)
        two_way_lo = lo_catalog_cards(two_way_gallery, locale, two_way_route)
        two_way_html = catalog_cards(two_way_lo, locale, two_way_route, translated_routes, series)
        two_way_titles = []
        for row in two_way_rows:
            model = str(row["model"]).lower()
            card = re.search(
                r'<a\b(?=[^>]*href="/products/' + re.escape(model) + r'/")[^>]*>.*?</a>',
                two_way_html, re.I | re.S
            )
            assert card, (locale, model, "missing two-way card")
            heading = re.search(r"<h3>(.*?)</h3>", card.group(0), re.I | re.S)
            assert heading, (locale, model, "missing product-card title")
            title = html.unescape(heading.group(1)).strip()
            small = re.search(r'<span class="product-card__small">(.*?)</span>', card.group(0), re.I | re.S)
            assert small and str(row.get("factoryModel") or model).upper() in html.unescape(small.group(1)).upper(), (locale, model, small.group(1) if small else None)
            assert volume_terms(catalog_volume_numbers(row), locale) in title, (locale, model, title)
            assert title.lower() != "two-way drinking cup", (locale, model, title)
            assert 'class="product-card__capacity"' not in card.group(0), (locale, model, "duplicate capacity badge")
            two_way_titles.append(title)
        assert len(set(two_way_titles)) == 20, (locale, "two-way card titles are not unique")

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

    two_way_rows = [row for row in series.values() if row.get("category") == "Two-Way Drinking Cups"]
    assert len(two_way_rows) == 20, ("expected all 20 two-way models", len(two_way_rows))
    english_titles = []
    for row in two_way_rows:
        model = str(row["model"]).lower()
        card = english_product_card(row)
        heading = re.search(r"<h3>(.*?)</h3>", card, re.I | re.S)
        small = re.search(r'<span class="product-card__small">(.*?)</span>', card, re.I | re.S)
        assert heading and small, ("English source card missing title/model", model)
        title = html.unescape(heading.group(1)).strip()
        factory_model = str(row.get("factoryModel") or model).upper()
        assert factory_model in html.unescape(small.group(1)).upper(), ("English model label", model, small.group(1))
        assert volume_terms(catalog_volume_numbers(row), "en") in title, ("English card capacity", model, title)
        assert title == _card_title(row, "en"), ("English card title mismatch", model, title)
        assert title.lower() != "two-way drinking cup", ("generic English card title", model)
        assert 'class="product-card__capacity"' not in card, ("duplicate English capacity badge", model)
        english_titles.append(title)
    assert len(set(english_titles)) == 20, ("English source card titles are not unique", english_titles)
    assert any("Manufacturer" in title for title in english_titles)
    assert any("Custom Colors" in title for title in english_titles)
    assert any("Custom Materials" in title for title in english_titles)

    # Existing D1 cards must be upgraded too, not merely newly inserted cards.
    for locale in sorted(LANGUAGES):
        existing_cards = []
        for row in two_way_rows:
            model = str(row["model"]).lower()
            factory_model = str(row.get("factoryModel") or model)
            existing_cards.append(
                f'<a class="product-card" data-product-card data-search="Two-Way Drinking Cup" '
                f'href="/products/{model}/"><div class="product-card__body">'
                f'<span class="product-card__small">MODEL {html.escape(factory_model)}</span>'
                f'<h3>Two-Way Drinking Cup</h3><span class="product-card__capacity">old capacity</span>'
                f'<span class="product-card__link">View Product ↗</span></div></a>'
            )
        existing_grid = '<div class="grid grid--4 product-grid">' + "".join(existing_cards) + "</div>"
        updated_grid = catalog_cards(existing_grid, locale, "/collections/two-way-drinking-cups/", translated_routes, series)
        updated_titles = []
        for row in two_way_rows:
            model = str(row["model"]).lower()
            card = re.search(
                r'<a\b(?=[^>]*href="/products/' + re.escape(model) + r'/")[^>]*>.*?</a>', 
                updated_grid, re.I | re.S
            )
            assert card, (locale, model, "existing card was lost")
            heading = re.search(r"<h3>(.*?)</h3>", card.group(0), re.I | re.S)
            small = re.search(r'<span class="product-card__small">(.*?)</span>', card.group(0), re.I | re.S)
            assert heading and small, (locale, model, "existing card title/model missing")
            title = html.unescape(heading.group(1)).strip()
            assert title == _card_title(row, locale), (locale, model, title)
            assert str(row.get("factoryModel") or model).upper() in html.unescape(small.group(1)).upper()
            assert 'class="product-card__capacity"' not in card.group(0)
            updated_titles.append(title)
        assert len(set(updated_titles)) == 20, (locale, "existing D1 card titles are not unique")
    # Non-two-way source cards are upgraded only while their heading is still
    # the generated default; an owner-authored heading remains untouched.
    non_two_way=next(row for row in series.values() if row.get("category")!="Two-Way Drinking Cups")
    collection_route="/collections/"+CAT[non_two_way["category"]][1]+"/"
    for locale in sorted(LANGUAGES):
        model=str(non_two_way["model"]).lower()
        slug=str(non_two_way["slug"])
        generic=localized_name(non_two_way,locale)
        existing=f'<a class="product-card" data-product-card data-search="{html.escape(generic)}" href="/products/{slug}/"><div class="product-card__body"><h3>{html.escape(generic)}</h3><span class="product-card__link">View Product ↗</span></div></a>'
        grid='<div class="grid grid--4 product-grid">'+existing+'</div>'
        updated=catalog_cards(grid,locale,collection_route,translated_routes,series)
        card=re.search(r'<a\b(?=[^>]*href="/products/'+re.escape(slug)+r'/")[^>]*>.*?</a>',updated,re.I|re.S)
        heading=re.search(r"<h3>(.*?)</h3>",card.group(0),re.I|re.S)
        assert heading and html.unescape(heading.group(1)).strip()==product_h1_text(locale,non_two_way),(locale,model,"generic source card not upgraded")
        owner_title="Owner selected card headline"
        owner_card=existing.replace("<h3>"+html.escape(generic)+"</h3>","<h3>"+owner_title+"</h3>")
        owner_grid='<div class="grid grid--4 product-grid">'+owner_card+'</div>'
        owner_updated=catalog_cards(owner_grid,locale,collection_route,translated_routes,series)
        owner_match=re.search(r'<a\b(?=[^>]*href="/products/'+re.escape(slug)+r'/")[^>]*>.*?</a>',owner_updated,re.I|re.S)
        owner_heading=re.search(r"<h3>(.*?)</h3>",owner_match.group(0),re.I|re.S)
        assert owner_heading and html.unescape(owner_heading.group(1)).strip()==owner_title,(locale,model,"owner card title overwritten")


    print(f"PASS: {len(series)} new products, {len(hashes)} unique WebP images, {len(category_counts)} categories.")


if __name__ == "__main__":
    main()
