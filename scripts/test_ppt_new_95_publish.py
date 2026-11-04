from pathlib import Path
from copy import deepcopy
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import site_renderer as site
from catalog_extensions import append_new_products
from factory_catalog_locales import LABELS
from product_content import factory_catalog_seo_title

SOURCE = "水杯最新产品.pptx"
EXPECTED_PUBLISHED = {
    "5361", "5330-1", "2107", "2096", "5330", "2089", "5219", "5308",
    "2079", "356", "273", "5305", "5302", "5301", "5295-1", "5297",
    "333", "8620-1", "5227-2", "2059", "2060", "320", "321", "322",
    "313", "5259", "5261", "5260", "5240", "8181", "8595", "5520",
    "250", "247", "2033", "2018", "8835", "5283", "5216",
}
ppt_products = {
    str(model): product
    for model, product in site.SERIES.items()
    if product.get("manualNew") is True and product.get("sourceDocument") == SOURCE
}
assert set(ppt_products) == EXPECTED_PUBLISHED, {
    "missing": sorted(EXPECTED_PUBLISHED - set(ppt_products)),
    "unexpected": sorted(set(ppt_products) - EXPECTED_PUBLISHED),
}
assert site.BUILD_STATE.get("publishRevision", 0) >= 54

snapshot_rows = [
    row for row in site.BUILD_STATE.get("products", [])
    if isinstance(row, dict) and isinstance(row.get("content"), dict)
    and row["content"].get("newProduct") is True
    and row["content"].get("sourceDocument") == SOURCE
]
assert {str(row.get("model")) for row in snapshot_rows} == EXPECTED_PUBLISHED
assert len(snapshot_rows) == 39

for model, product in ppt_products.items():
    assert product.get("imageReviewStatus") == "visually_reviewed_source_crop", (model, product.get("imageReviewStatus"))
    assert product.get("qcStatus") == "source_read", (model, product.get("qcStatus"))
    assert "pending" not in str(product.get("imageReviewStatus", "")).lower()
    assert product.get("capacity") and product.get("dimensions") and product.get("images")
    assert "variant mapping pending" not in str(product.get("description", "")).lower()
    assert "variant mapping pending" not in str(product.get("dimensions", "")).lower()
    assert "variant mapping pending" not in str(product.get("carton_size", "")).lower()
    assert len(factory_catalog_seo_title(product)) <= 60
    detail = ROOT / "dist/products" / model / "index.html"
    assert detail.is_file(), (model, "missing English product detail")
    html = detail.read_text(encoding="utf8")
    for marker in ("Factory Catalog Source", "Factory Catalog Page", "Factory Catalog Capacity"):
        assert marker in html, (model, "missing", marker)
    assert product["images"][0] in html, (model, "source image missing from detail")
    assert product["factoryModel"] in html, (model, "factory model missing")
    assert SOURCE in html, (model, "PPT source marker missing")

# Explicitly verified source-table corrections.
assert ppt_products["356"]["dimensions"] == "1000ml:10×15×16 cm"
assert ppt_products["356"]["carton_size"] == "1000ml:68.5×47×49.5 cm"
assert ppt_products["356"]["carton_quantity"] == "48 or 60"
assert ppt_products["2033"]["dimensions"] == "1500ml:28×9.5 cm; 2000ml:31×10 cm"
assert ppt_products["2033"]["carton_size"] == "1500ml:62×42×58 cm; 2000ml:65×43.5×64 cm"
assert ppt_products["2033"]["carton_quantity"] == "48 or 60"
assert ppt_products["5295-1"]["dimensions"] == "650ml:7.5×19.5 cm"
assert "Not specified in source" in ppt_products["5295-1"]["carton_size"]
for model, carton in {
    "5361": "43×36×49 cm",
    "5330-1": "45.5×39×42.5 cm",
}.items():
    product = ppt_products[model]
    assert product["capacity"] == "600ml", (model, product["capacity"])
    assert product["category"] == "Plastic Sports Water Bottles", (model, product["category"])
    assert product["carton_size"] == carton, (model, product["carton_size"])
    assert "6000ml" not in product["capacity"] and "6000ml" not in product["carton_size"]

# Ambiguous source pages remain unpublished: each source cell also lists a second model code.
assert "2080" not in ppt_products and "2082" not in ppt_products
assert "2081" not in ppt_products and "2083" not in ppt_products

# Every published product image has all five localized ALT strings in the current D1 snapshot.
media_alts = {row.get("path"): row.get("translations", {}) for row in site.BUILD_STATE.get("mediaAlts", [])}
for model, product in ppt_products.items():
    image_path = product["images"][0]
    alts = media_alts.get(image_path)
    assert isinstance(alts, dict), (model, "missing D1 image ALT")
    assert all(isinstance(alts.get(locale), str) and alts[locale].strip() for locale in ("en", "es", "pt", "ru", "tr")), (model, alts)

# New products appear in each language's catalog with honest English-detail links.
for locale in ("es", "pt", "ru", "tr"):
    listing = ROOT / "dist" / locale / "products/index.html"
    assert listing.is_file(), (locale, "missing localized product listing")
    html = listing.read_text(encoding="utf8")
    for model, product in ppt_products.items():
        slug = product["slug"]
        href = f'href="/products/{slug}/"'
        assert html.count(href) == 1, (locale, model, "localized card missing/duplicated")
        start = html.index(href)
        card = html[start:html.find("</a>", start) + 4]
        assert LABELS[locale]["english"] in card, (locale, model, "English-detail disclosure missing")
        assert product["images"][0] in card, (locale, model, "localized card image missing")
        assert 'alt="' in card and 'alt=""' not in card, (locale, model, "localized image ALT missing")

# CMS owner-edit priority: a later owner SEO, copy and image choice must survive catalog expansion.
sample = deepcopy(next(row for row in snapshot_rows if row["model"] == "5361"))
sample["content"]["seoTitle"] = "OWNER APPROVED 600ml SPORTS BOTTLE 5361 | XUYI"
sample["content"]["description"] = "Owner-approved product description for model 5361."
sample["content"]["image"] = "/media/product/owner-approved-5361.webp"
owner_series = {}
assert append_new_products(owner_series, [sample]) == 1
assert owner_series["5361"]["seoTitle"] == sample["content"]["seoTitle"]
assert owner_series["5361"]["description"] == sample["content"]["description"]
assert owner_series["5361"]["images"] == [sample["content"]["image"]]

# A pending image review must still block build inclusion.
pending = deepcopy(sample)
pending["content"]["imageReviewStatus"] = "pending_owner_review"
try:
    append_new_products({}, [pending])
except ValueError as exc:
    assert "unreviewed" in str(exc).lower()
else:
    raise AssertionError("Pending image review was not blocked")

# Clean-build determinism for the 39 source-backed products.
series_a, series_b = {}, {}
assert append_new_products(series_a, snapshot_rows) == 39
assert append_new_products(series_b, snapshot_rows) == 39
assert json.dumps(series_a, sort_keys=True, ensure_ascii=False) == json.dumps(series_b, sort_keys=True, ensure_ascii=False)

print("XUYI_PPT_39_SOURCE_VERIFIED_PRODUCTS_RELEASE_TEST_PASSED",
      "products=39", "localized_catalogs=4", "English_details=39",
      "image_alts=5_languages", "pending_gate=PASS", "owner_override=PASS")