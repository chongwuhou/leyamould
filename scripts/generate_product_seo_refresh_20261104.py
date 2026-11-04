#!/usr/bin/env python3
"""Generate a fixed, source-reviewed 2026-11-04 D1 SEO refresh allowlist.

The expected values are the exact prior reviewed SEO promotion, not values
read dynamically from production during the write. A later owner edit therefore
fails the conditional comparison and is preserved by the API.
"""
from __future__ import annotations
import json
import os
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "_local_ops" / "build-snapshot.json"
OLD_SOURCE = ROOT / "functions" / "_shared" / "reviewed-product-seo-20261020.js"
OUTPUT = ROOT / "functions" / "_shared" / "reviewed-product-seo-refresh-20261104.js"

if not SNAPSHOT.is_file():
    raise SystemExit("Missing current XUYI build snapshot")
state = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
if state.get("site") != "xuyi-drinkware-site":
    raise SystemExit("Refusing a non-XUYI D1 snapshot")
os.environ["XUYI_BUILD_SNAPSHOT"] = str(SNAPSHOT)

sys.path.insert(0, str(ROOT))
from site_renderer import SERIES  # noqa: E402
from scripts.source_catalog_capacity_oz import (  # noqa: E402
    LOCALES, catalog_volume_numbers, new_seo, new_seo_without_capacity
)

source_text = OLD_SOURCE.read_text(encoding="utf-8")
prefix = "export const REVIEWED_SEO_SOURCE="
if prefix not in source_text:
    raise SystemExit("Previous reviewed SEO source format changed")
old_rows = json.loads(source_text.split(prefix, 1)[1].strip().removesuffix(";"))
if len(old_rows) != 505:
    raise SystemExit("Previous reviewed source no longer contains exactly 505 rows")

products = {str(row.get("slug")): row for row in SERIES.values()}
current = {
    (row.get("slug"), row.get("locale")): row
    for row in state.get("productSeo", [])
}
if len(current) != 505:
    raise SystemExit("Current D1 snapshot does not contain the expected 505 SEO rows")

reviewed = []
for old in old_rows:
    slug = old["slug"]
    locale = old["locale"]
    product = products.get(slug)
    if product is None:
        raise SystemExit("Reviewed SKU is absent from the current catalog: " + slug)
    current_row = current.get((slug, locale))
    if current_row is None:
        raise SystemExit("Reviewed D1 SEO row is missing: " + slug + "/" + locale)
    if (current_row.get("seoTitle") != old["newTitle"] or
            current_row.get("metaDescription") != old["newDescription"]):
        raise SystemExit("D1 SEO changed since the previous reviewed promotion: " + slug + "/" + locale)

    numbers = catalog_volume_numbers(product)
    new_title, new_description = (
        new_seo(locale, product, numbers) if numbers
        else new_seo_without_capacity(locale, product)
    )
    if not 12 <= len(new_title) <= 90 or not 30 <= len(new_description) <= 240:
        raise SystemExit("New SEO copy is outside the D1 validation bounds: " + slug + "/" + locale)
    if len(new_title) > 60 or len(new_description) > 180:
        raise SystemExit("New SEO copy exceeds the reviewed search-snippet target: " + slug + "/" + locale)
    if "OEM" not in new_title or "XUYI" not in new_title:
        raise SystemExit("B2B/OEM brand qualifier missing: " + slug + "/" + locale)
    if numbers and not ("ml" in new_title.lower() and "oz" in new_title.lower()):
        raise SystemExit("Verified mL/oz pair missing from SEO title: " + slug + "/" + locale)
    if new_title == old["newTitle"] and new_description == old["newDescription"]:
        raise SystemExit("Refresh did not change reviewed SEO copy: " + slug + "/" + locale)

    reviewed.append({
        "slug": slug,
        "locale": locale,
        "twoWay": product.get("category") == "Two-Way Drinking Cups",
        "newTitle": new_title,
        "newDescription": new_description,
        "hasCapacity": bool(numbers),
    })
if len({(row["slug"], row["locale"]) for row in reviewed}) != 505:
    raise SystemExit("Duplicate reviewed product/locale key")
locale_counts = Counter(row["locale"] for row in reviewed)
if locale_counts != Counter({locale: 101 for locale in LOCALES}):
    raise SystemExit("Unexpected reviewed locale distribution: " + repr(locale_counts))
for locale in LOCALES:
    titles = [row["newTitle"] for row in reviewed if row["locale"] == locale]
    if len(titles) != len(set(titles)):
        raise SystemExit("Duplicate refreshed SEO titles in " + locale)

payload = ",\n".join(
    "  " + json.dumps(row, ensure_ascii=False, separators=(",", ":"))
    for row in reviewed
)
OUTPUT.write_text(
    "// Fixed source-reviewed refresh; expected values are the 2026-10-20 approved D1 copy.\n"
    "export const REVIEWED_SEO_REFRESH_SOURCE=[\n" + payload + "\n];\n",
    encoding="utf-8"
)
print("XUYI_REVIEWED_PRODUCT_SEO_REFRESH_SOURCE_GENERATED",
      "ROWS", len(reviewed),
      "LOCALES", dict(locale_counts),
      "CAPACITY_ROWS", sum(1 for row in reviewed if row["hasCapacity"]),
      "UNIQUE_TITLES_PER_LOCALE", True)
print("SAMPLE", reviewed[0]["slug"], reviewed[0]["locale"], reviewed[0]["newTitle"])
