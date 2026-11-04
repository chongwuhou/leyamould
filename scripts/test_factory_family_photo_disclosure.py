#!/usr/bin/env python3
"""Factory family images must be disclosed without claiming exact-SKU photography."""
from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from product_content import details as product_details  # noqa: E402
from media_alt_render import FAMILY_ALT, FAMILY_ALT_BASELINES, approved_alts, apply_media_alts  # noqa: E402
from product_source_identity import main_image_alt  # noqa: E402

FAMILY_IMAGE = "/media/product/4cd9463c130d77bdee9b825c2c61c8b3.webp"
FAMILY_NOTE = (
    "Factory catalog family image shared by related variants; it does not confirm "
    "the exact SKU appearance. Confirm the selected model, capacity and sample before ordering."
)


def sample_product(status: str) -> dict:
    variant = {
        "capacity": "1500ml",
        "material": "PP + PC",
        "dimensions": "1500ml:11.5×24 cm",
        "colors": "Custom colors available; confirm palette and MOQ",
        "packing": "OPP bag packaging",
        "carton_quantity": "60",
        "carton_size": "Confirm with sales",
        "sourceDocument": "水杯最新产品.pptx",
        "sourcePage": "51",
        "sourceNotes": "The factory catalog provides a shared family photo, not a separate SKU photo.",
    }
    return {
        "model": "5285",
        "factoryModel": "5285",
        "slug": "5285",
        "name": "Large-Capacity Plastic Water Bottle",
        "category": "Large Capacity Water Jugs",
        "manualNew": True,
        "sourceDocument": "水杯最新产品.pptx",
        "sourcePage": "51",
        "imageReviewStatus": status,
        "images": [FAMILY_IMAGE],
        "variants": [variant],
        "description": (
            "XUYI Model 5285 is a plastic drinkware product for wholesale sourcing "
            "and custom-branding projects. Confirm the exact variant and sample appearance."
        ),
    }


def main() -> None:
    row = {
        "model": "5285",
        "category": "Large Capacity Water Jugs",
        "imageReviewStatus": "visually_reviewed_source_family_image",
    }
    family_tokens = {"en": "family", "es": "familiar", "pt": "família", "ru": "семей", "tr": "aile"}
    for locale in ("en", "es", "pt", "ru", "tr"):
        alt = main_image_alt(row, FAMILY_IMAGE, {FAMILY_IMAGE: 1}, locale, "PP + PC", [1500])
        assert alt and "5285" not in alt and family_tokens[locale] in alt.lower(), (locale, alt)

    crop_row = {**row, "imageReviewStatus": "visually_reviewed_source_crop"}
    crop_alt = main_image_alt(crop_row, FAMILY_IMAGE, {FAMILY_IMAGE: 1}, "en", "PP + PC", [1500])
    assert "Model 5285" in crop_alt, crop_alt

    family_html = product_details(sample_product("visually_reviewed_source_family_image"))
    assert FAMILY_NOTE in family_html
    crop_html = product_details(sample_product("visually_reviewed_source_crop"))
    assert "Factory catalog image; confirm the exact variant and sample appearance before ordering." in crop_html
    assert FAMILY_NOTE not in crop_html

    family_paths = list(FAMILY_ALT_BASELINES)
    state = {
        "products": [
            {"model": "2061", "content": {"image": path, "imageReviewStatus": "visually_reviewed_source_family_image"}}
            for path in family_paths
        ],
        "mediaAlts": [
            {"path": path, "translations": dict(FAMILY_ALT_BASELINES[path])}
            for path in family_paths
        ],
    }
    rewritten = approved_alts(state)
    for path in family_paths:
        assert rewritten[path] == FAMILY_ALT
        markup = f'<img src="{path}" alt="{FAMILY_ALT_BASELINES[path]["en"]}">'
        assert FAMILY_ALT["en"] in apply_media_alts(markup, state, "en")

    owner_edit = deepcopy(state)
    owner_edit["mediaAlts"][0]["translations"]["en"] = "Owner-approved family image description"
    owner_alts = approved_alts(owner_edit)[family_paths[0]]
    assert owner_alts["en"] == "Owner-approved family image description"
    assert owner_alts["es"] == FAMILY_ALT["es"]

    non_family = deepcopy(state)
    for row in non_family["products"]:
        row["content"]["imageReviewStatus"] = "visually_reviewed_source_crop"
    assert approved_alts(non_family)[family_paths[0]] == FAMILY_ALT_BASELINES[family_paths[0]]

    print("XUYI_FACTORY_FAMILY_PHOTO_DISCLOSURE_AND_ALT_PASSED locales=5")


if __name__ == "__main__":
    main()