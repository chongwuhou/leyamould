"""Regression gate for the LEYA product-catalog D1 migration.

The test exercises the same renderer overlay used by the production build with
an owner-edited D1 row.  It deliberately does not render or mutate dist.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def source(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


routes = source("functions/_shared/mould-routes.js")
for slug in (
    "mineral-water-closure-cap-molds", "five-gallon-water-cap-mould",
    "oil-bottle-cap-mould", "flip-top-caps-mould", "engine-oil-cap-mould",
    "food-packaging-cap-mould", "medical-cap-mould", "personal-care-cap-mould",
    "functional-cap-mould", "plastic-handle-cap-mould", "wine-cap-mould",
    "pet-preform-mould", "blow-bottle-mould",
):
    assert f'"{slug}"' in routes, slug

snapshot = source("functions/api/build-snapshot.js")
assert "xuyi_product_content WHERE publication_status='published'" in snapshot
assert "onlyProducts=products.filter" in snapshot
assert "ensureYoutubeVideos(db)" not in snapshot
assert "ALTER TABLE" not in snapshot and "CREATE TABLE" not in snapshot
assert "effectiveProductSeoRows" in snapshot
assert "contentSchemaVersion" in snapshot and "structured" in snapshot

assert not (ROOT / "functions/api/admin/content-seed.js").exists()
assert not (ROOT / "functions/api/admin/mould-content-seed-20261124.js").exists()

catalog = json.loads((ROOT / "data/mould-catalog.json").read_text(encoding="utf-8"))
categories = catalog.get("categories") or []
assert len(categories) == 13
assert len({item["slug"] for item in categories}) == 13

renderer = source("mould_build.py")
for field in ("titleEs", "navTitleEs", "descriptionEs", "shortEs", "detailEs", "metaEs", "body", "sections", "faqs"):
    assert f'"{field}"' in renderer
assert "_catalog_from_state" in renderer and "STATE.get(" in renderer
assert "_structured_sections" in source("mould_category_pages.py")
page_data = json.loads((ROOT / "data/mould-page-structured.json").read_text(encoding="utf-8"))
for locale in ("en", "es"):
    sections = page_data[locale]["/Plastic-cap-mold.html"]["sections"]
    assert {row["id"] for row in sections} >= {"advantages", "samples", "technology", "quality", "workflow", "faq", "videos"}
    assert len(next(row for row in sections if row["id"] == "samples")["items"]) == 21
product_admin = source("functions/api/admin/product-content.js")
assert "function categoryCopy" in product_admin and "out.samples" in product_admin
assert '"seoTitleEs"' in product_admin and '"seoDescriptionEs"' in product_admin
assert '"structured"' in product_admin
new_product = source("functions/_shared/new-product.js")
assert 'seoTitleEs:clean("seoTitleEs",90)' in new_product

# Realistic owner-edit simulation: D1 content must win over the checked-in
# baseline on a clean renderer import, including a localized field.
import sys
sys.path.insert(0, str(ROOT))
import mould_build  # noqa: E402

mould_build.STATE = {
    "products": [{
        "model": "five-gallon-water-cap-mould",
        "content": {
            "title": "OWNER EDITED 5 GALLON MOULD",
            "titleEs": "Molde editado por el propietario",
            "description": "Owner-controlled product description.",
            "body": "Owner-controlled structured product body.",
            "sections": [{"title": "Owner technology section", "body": "Owner-controlled technical copy."}],
            "faqs": [{"question": "Owner question?", "answer": "Owner answer."}],
            "category": {"hero": {"title": "Owner category hero"}, "samples": [{"image": "/upload/owner/sample.jpg", "alt": "Owner sample"}]},
            "structured": {"hero": {"title": "Owner structured hero"}, "samples": [{"image": "/upload/owner/structured.jpg", "alt": "Owner structured sample"}]},
        },
    }]
}
edited = next(row for row in mould_build._catalog_from_state() if row.get("slug") == "five-gallon-water-cap-mould")
assert edited["title"] == "OWNER EDITED 5 GALLON MOULD"
assert edited["titleEs"] == "Molde editado por el propietario"
assert edited["description"] == "Owner-controlled product description."
assert edited["body"] == "Owner-controlled structured product body."
assert edited["sections"][0]["title"] == "Owner technology section"
assert edited["faqs"][0]["question"] == "Owner question?"
assert edited["categoryCopy"]["hero"]["title"] == "Owner structured hero"
assert edited["categoryCopy"]["samples"][0]["image"] == "/upload/owner/structured.jpg"

# A new published D1 family must enter the same safe category renderer without
# changing the checked-in catalogue or requiring a hardcoded route list.
mould_build.STATE = {
    "products": [{
        "model": "new-owner-mould-family",
        "content": {
            "route": "/product/new-owner-mould-family.html",
            "title": "New Owner Mould Family",
            "description": "A reviewed owner-managed mould family for packaging projects.",
        },
    }]
}
dynamic = next(row for row in mould_build._catalog_from_state() if row.get("slug") == "new-owner-mould-family")
assert dynamic["route"] == "/product/new-owner-mould-family.html"
assert dynamic["title"] == "New Owner Mould Family"
assert dynamic["description"].startswith("A reviewed owner-managed")

print(f"LEYA_MOULD_PRODUCT_D1_CONTRACT_PASSED categories={len(categories)}")


