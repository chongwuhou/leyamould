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

seed = source("functions/api/admin/mould-content-seed-20261124.js")
for marker in ("mould-catalog.json", "mould-product-structured.json", "xuyi_product_content", "existingProducts", "productImagesRemainTemplateBound"):
    assert marker in seed, marker

catalog = json.loads((ROOT / "data/mould-catalog.json").read_text(encoding="utf-8"))
categories = catalog.get("categories") or []
assert len(categories) == 13
assert len({item["slug"] for item in categories}) == 13

renderer = source("mould_build.py")
for field in ("titleEs", "navTitleEs", "descriptionEs", "shortEs", "detailEs", "metaEs", "body", "sections", "faqs"):
    assert f'"{field}"' in renderer
assert "_catalog_from_state" in renderer and "STATE.get(" in renderer

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
            "faqs": [{"question": "Owner question?", "answer": "Owner answer."}],
        },
    }]
}
edited = next(row for row in mould_build._catalog_from_state() if row.get("slug") == "five-gallon-water-cap-mould")
assert edited["title"] == "OWNER EDITED 5 GALLON MOULD"
assert edited["titleEs"] == "Molde editado por el propietario"
assert edited["description"] == "Owner-controlled product description."
assert edited["body"] == "Owner-controlled structured product body."
assert edited["faqs"][0]["question"] == "Owner question?"

print(f"LEYA_MOULD_PRODUCT_D1_CONTRACT_PASSED categories={len(categories)}")