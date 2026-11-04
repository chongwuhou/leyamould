from pathlib import Path
from copy import deepcopy
import json
import os
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "_local_ops" / "build-snapshot.json"
if SNAPSHOT.is_file():
    os.environ["XUYI_BUILD_SNAPSHOT"] = str(SNAPSHOT)
    _snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    os.environ["XUYI_PUBLISH_REVISION"] = str(int(_snapshot.get("publishRevision", 0)))
sys.path.insert(0, str(ROOT))

import site_renderer as site
from catalog_extensions import append_new_products, is_factory_catalog_source_default
from product_content import factory_catalog_seo_title

SOURCE = "水杯最新产品.pptx"
MANIFEST = json.loads((ROOT / "scripts/fixtures/ppt-new-95-source-models.json").read_text(encoding="utf-8"))
EXPECTED_SOURCE_PAGES = {str(row["model"]): int(row["sourcePage"]) for row in MANIFEST["models"]}
EXPECTED_PUBLISHED = set(EXPECTED_SOURCE_PAGES)
assert len(EXPECTED_PUBLISHED) == MANIFEST["modelCount"] == 95
ppt_products = {
    str(model): product
    for model, product in site.SERIES.items()
    if product.get("manualNew") is True and product.get("sourceDocument") == SOURCE
}
assert EXPECTED_PUBLISHED.issubset(set(ppt_products)), {
    "missing": sorted(EXPECTED_PUBLISHED - set(ppt_products)),
}
assert site.BUILD_STATE.get("publishRevision", 0) >= 56

snapshot_rows = [
    row for row in site.BUILD_STATE.get("products", [])
    if isinstance(row, dict) and isinstance(row.get("content"), dict)
    and row["content"].get("newProduct") is True
    and row["content"].get("sourceDocument") == SOURCE
]
snapshot_models = {str(row.get("model")) for row in snapshot_rows}
assert EXPECTED_PUBLISHED.issubset(snapshot_models)
assert len(snapshot_rows) >= len(EXPECTED_PUBLISHED)
snapshot_by_model = {str(row["model"]): row["content"] for row in snapshot_rows}

for model in EXPECTED_PUBLISHED:
    product = ppt_products[model]
    assert product.get("imageReviewStatus") in {
        "visually_reviewed_source_crop", "visually_reviewed_source_family_image"
    }, (model, product.get("imageReviewStatus"))
    assert str(product.get("sourcePage")) == str(EXPECTED_SOURCE_PAGES[model]), (model, product.get("sourcePage"))
    source_content = snapshot_by_model[model]
    assert source_content.get("sourceSha256") == MANIFEST["sourceSha256"], (model, "source SHA mismatch")
    assert re.fullmatch(r"[a-f0-9]{64}", str(source_content.get("sourceImageSha256", ""))), (model, "source image SHA missing")
    assert not re.search(r"glass|stainless", str(product.get("category", "")) + " " + str(product.get("material", "")), re.I), (model, "non-plastic product")
    if product.get("imageReviewStatus") == "visually_reviewed_source_family_image":
        assert "family" in str(product.get("sourceNotes", "")).lower(), (model, "family image note missing")
    assert product.get("qcStatus") == "source_read", (model, product.get("qcStatus"))
    assert "pending" not in str(product.get("imageReviewStatus", "")).lower()
    assert product.get("capacity") and product.get("dimensions") and product.get("images")
    assert "variant mapping pending" not in str(product.get("description", "")).lower()
    assert "variant mapping pending" not in str(product.get("dimensions", "")).lower()
    assert "variant mapping pending" not in str(product.get("carton_size", "")).lower()
    assert len(factory_catalog_seo_title(product)) <= 60
    assert is_factory_catalog_source_default(model,source_content,"seoTitle"),(model,"source title must be recognized as an unchanged import default")
    assert is_factory_catalog_source_default(model,source_content,"seoDescription"),(model,"source description must be recognized as an unchanged import default")
    owner_seo=deepcopy(source_content)
    owner_seo["seoDescription"]+=" Owner-approved edit."
    assert not is_factory_catalog_source_default(model,owner_seo,"seoDescription"),(model,"owner SEO edit must remain authoritative")
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

# Pages 24 and 25 each contain one model code with multiple factory-listed capacity variants.
# Keep each model as one product page with all source-listed options.
assert {"2080", "2082"}.issubset(ppt_products)
assert "850ml" in ppt_products["2080"]["capacity"] and "1200ml" in ppt_products["2080"]["capacity"]
assert "1600ml" in ppt_products["2082"]["capacity"] and "2200ml" in ppt_products["2082"]["capacity"]
assert ppt_products["2080"]["carton_quantity"] == "60"
assert ppt_products["2082"]["carton_quantity"] == "30"
assert "2081" not in ppt_products and "2083" not in ppt_products
assert ppt_products["5285"]["carton_quantity"] == "30"
assert ppt_products["5286"]["carton_quantity"] == "24"

# Every published product image has all five localized ALT strings in the current D1 snapshot.
media_alts = {row.get("path"): row.get("translations", {}) for row in site.BUILD_STATE.get("mediaAlts", [])}
for model in EXPECTED_PUBLISHED:
    product = ppt_products[model]
    image_path = product["images"][0]
    alts = media_alts.get(image_path)
    assert isinstance(alts, dict), (model, "missing D1 image ALT")
    assert all(isinstance(alts.get(locale), str) and alts[locale].strip() for locale in ("en", "es", "pt", "ru", "tr")), (model, alts)

# The 95 PPT products now have native localized detail pages and model-specific metadata.
for locale in ("es","pt","ru","tr"):
    listing = ROOT / "dist" / locale / "products/index.html"
    assert listing.is_file(), (locale, "missing localized product listing")
    html = listing.read_text(encoding="utf8")
    for model in EXPECTED_PUBLISHED:
        product = ppt_products[model]
        href = f'href="/{locale}/products/{product["slug"]}/"'
        assert href in html, (locale, model, "localized catalogue card missing its native detail link")
        assert f'href="/products/{product["slug"]}/"' not in html, (locale, model, "localized card still points to English")
        localized_detail = ROOT / "dist" / locale / "products" / product["slug"] / "index.html"
        assert localized_detail.is_file(), (locale, model, "native localized detail page missing")
        markup = localized_detail.read_text(encoding="utf8")
        assert f'<html lang="{locale}">' in markup, (locale, model, "wrong document language")
        assert product["factoryModel"] in markup, (locale, model, "factory model missing from localized detail")
        assert "B2B" in markup, (locale, model, "localized buyer content missing")
        assert 'rel="alternate" hreflang="' + locale + '"' in markup, (locale, model, "self hreflang missing")

# English and all four translated details must remain independently crawlable.
for model in EXPECTED_PUBLISHED:
    product = ppt_products[model]
    for locale in ("en","es","pt","ru","tr"):
        prefix="" if locale=="en" else locale+"/"
        detail=ROOT/"dist"/prefix/"products"/product["slug"]/"index.html"
        assert detail.is_file(), (locale,model,"detail page missing")
        markup=detail.read_text(encoding="utf8")
        assert 'rel="canonical"' in markup
        assert 'rel="alternate" hreflang="x-default"' in markup

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

# Clean-build determinism for the source-backed 95-model baseline.
expected_rows = [row for row in snapshot_rows if str(row.get("model")) in EXPECTED_PUBLISHED]
series_a, series_b = {}, {}
assert append_new_products(series_a, expected_rows) == len(EXPECTED_PUBLISHED)
assert append_new_products(series_b, expected_rows) == len(EXPECTED_PUBLISHED)
assert json.dumps(series_a, sort_keys=True, ensure_ascii=False) == json.dumps(series_b, sort_keys=True, ensure_ascii=False)

print("XUYI_PPT_95_SOURCE_VERIFIED_PRODUCTS_RELEASE_TEST_PASSED",
      "products=" + str(len(EXPECTED_PUBLISHED)), "localized_catalogs=English-only-until-translated",
      "English_details=" + str(len(EXPECTED_PUBLISHED)),
      "image_alts=5_languages", "pending_gate=PASS", "owner_override=PASS")