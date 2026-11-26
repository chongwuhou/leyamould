"""Regression guards for strict D1 production source ownership."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


renderer = read("mould_build.py")
category = read("mould_category_pages.py")
snapshot = read("functions/api/build-snapshot.js")
completeness = read("scripts/test_mould_d1_completeness.py")
product_admin = read("functions/api/admin/product-content.js")

assert "rows = [] if STRICT_D1" in renderer
assert "reviewed = [] if STRICT_D1" in renderer
assert "source = {} if STRICT_D1" in renderer
assert "if not STRICT_D1:" in renderer
assert "Strict D1 product SEO missing" in renderer
assert '"verified_reviews"' in renderer
assert "categoryCopyEs" in renderer
assert "strict_d1 = bool(helpers.get(\"strict_d1\"))" in category
assert "testimonial_rows = list(helpers.get(\"verified_reviews\") or [])" in category
assert "MOULD_CATALOG" not in snapshot
assert "mould-catalog" not in snapshot
assert "structured_modules" in completeness
assert "product structured fields are incomplete" in completeness
assert "function validatePublishedProductContent" in product_admin
assert "Published product requires Spanish title and description" in product_admin

# Inventory growth must not be blocked by the old historical totals.
for path in (
    "scripts/test_mould_d1_source_authority.py",
    "scripts/test_mould_product_d1_contract.py",
    "scripts/test_mould_news_editorial.py",
    "scripts/test_mould_release.py",
):
    source = read(path)
    assert "== 24" not in source and "== 13" not in source and "== 21" not in source, path

print("LEYA_MOULD_PRODUCTION_SOURCE_BOUNDARY_PASSED")
