"""Fail-closed checks for the LEYA MOULD admin/backend boundary.

This is deliberately source-level: it prevents the water-cup project from
silently returning through defaults, route imports, or the disabled review
ingest while leaving the public HTML/CSS build untouched.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def source(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")

site_config = source("functions/api/admin/site-config.js")
assert "LEGACY_DEFAULT_NAVIGATION" not in site_config
for forbidden in (
    "/collections/sports-water-bottles/",
    "/collections/large-capacity-water-jugs/",
    "/collections/kids-water-bottles/",
    "/capabilities/custom-water-bottle/",
    "/why-us/",
):
    assert forbidden not in site_config, forbidden
assert "MOULD_ROUTES" in site_config
assert "Navigation URL is not a configured LEYA MOULD route" in site_config

route_modules = (
    "functions/api/admin/page-content.js",
    "functions/api/admin/page-translations.js",
    "functions/api/admin/product-content.js",
    "functions/api/admin/product-seo.js",
    "functions/api/admin/product-reviews.js",
    "functions/api/admin/blog.js",
    "functions/api/admin/daily-product-reviews.js",
    "functions/_shared/new-product.js",
)
for rel in route_modules:
    text = source(rel)
    assert "xuyi-routes.js" not in text, rel
    assert "mould-routes.js" in text, rel

page_content = source("functions/api/admin/page-content.js")
assert "EDITABLE_PAGE_ROUTES" in page_content
for required in ("/contact/", "/request-sample/", "/privacy-policy/"):
    assert required in page_content, required

product_content = source("functions/api/admin/product-content.js")
assert 'status==="published"&&!MANAGED_MODELS.has(model)' in product_content
assert "draft-only until its LEYA route and detail template are registered" in product_content

reviews = source("functions/api/admin/daily-product-reviews.js")
assert "LEYA_DAILY_REVIEW_IMPORT_ENABLED=false" in reviews
for legacy_source in ("101-zhenshipingjia.xlsx", "101-additional-reviews-only.xlsx", "2306-transparent"):
    assert legacy_source not in reviews, legacy_source
assert "daily review import is not configured" in reviews

# New Blog posts must use the mould detail route, never the old SKU route.
blog = source("functions/api/admin/blog.js")
assert "/products/<sku>/" in blog
assert re.search(r"matchAll\(/.*\\/product.*\\.html", blog)

security = source("functions/_shared/admin-security.js")
for legacy_path in ('"brands"', '"filter-types"', '"replacement-filters"', '"shipping-logistics"'):
    assert legacy_path not in security, legacy_path

# Historical one-time D1/R2 factory imports are gone; the dated seed alias is
# gone too.  A build snapshot is a reader only and must never initialize or
# alter a D1 table on GET.
auth = source("functions/_shared/build-auth.js")
assert "authorizedReviewedFactoryCatalog" not in auth
assert "/api/admin/mould-content-seed-20261124" not in auth
assert "LEYA_ALLOW_LEGACY_MIGRATIONS" not in auth
assert "authorizedSchedulerRunnerRequest" not in auth
assert not (ROOT / "functions/api/admin/content-seed.js").exists()
assert not (ROOT / "functions/api/admin/mould-content-seed-20261124.js").exists()
assert not (ROOT / "functions/api/admin/scheduler-runner.js").exists()
for removed in (
    "functions/api/admin/factory-catalog-20261103.js",
    "functions/api/admin/factory-catalog-images-20261103.js",
):
    assert not (ROOT / removed).exists(), removed
snapshot = source("functions/api/build-snapshot.js")
for forbidden in ("ensureLeyaSystemSchema", "ensureNavigationSchema", "ensureModelReferenceSchema", "ensureYoutubeVideos", "ALTER TABLE", "CREATE TABLE"):
    assert forbidden not in snapshot, forbidden
assert "source_url" in source("functions/_shared/product-reviews.js")
model_api = source("functions/api/admin/model-references.js")
assert "Published model references require an HTTPS source URL and source image" in model_api
assert "Published model references require an owner review timestamp" not in model_api

print("LEYA_MOULD_BACKEND_CONTRACT_PASSED")

