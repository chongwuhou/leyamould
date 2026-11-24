"""Source-level checks for the LEYA MOULD admin UI/API contract.

The public renderer is intentionally out of scope here. These checks catch
admin-only regressions such as an editor calling a removed route variable or
rendering controls that the save payload silently ignores.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def source(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")

index = source("admin/index.html")
for module in (
    "admin-forms.js", "admin-blog.js", "admin-media.js", "admin-media-replace.js",
    "admin-youtube-videos.js", "admin-security.js", "admin-site-settings.js",
    "admin-content.js", "admin-reviews.js", "admin-scheduler.js",
    "admin-product-seo.js", "admin-model-references.js", "admin-publish.js",
):
    assert f'/assets/{module}' in index, module

content = source("assets/admin-content.js")
for endpoint in (
    '"brand-config"', '"site-config"', '"site-settings"', '"pages"',
    '"product-content"', '"page-translations"', '"page-content"',
    '"home-banners"',
):
    assert endpoint in content, endpoint
for stale in ("Why Us", "drinkware", '"/products/"', "旭一", "XUYI Bottles Website"):
    assert stale not in content, stale

page_content = source("functions/api/admin/page-content.js")
assert "MOULD_ROUTES" in page_content
assert "MANAGED_ROUTES" not in page_content

settings = source("assets/admin-site-settings.js")
assert '"#translation-mode"' not in settings
assert "autoTranslate" in settings and "requireHumanReview" in settings

forms = source("assets/admin-forms.js")
assert "LEYA MOULD Website" in forms
assert "XUYI Bottles Website" not in forms

for rel in ("assets/admin-blog.js", "assets/admin-media.js", "assets/admin-security.js", "assets/admin-publish.js"):
    text = source(rel)
    assert "旭一" not in text and "XUYI" not in text, rel

print("LEYA_MOULD_ADMIN_CONTRACT_PASSED")
