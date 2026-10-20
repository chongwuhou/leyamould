"""XUYI product image widths stay inside their shared header shell.

The customer observed LO-001 photo panels extending past the navigation:
the former 100vw + 50vw negative margin broke the site's 1360px shell.
Test every LO source SKU in all five locales without touching CMS media.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
CSS = (ROOT / "assets/site.css").read_text(encoding="utf8")
BUILT_CSS = (DIST / "assets/site.css").read_text(encoding="utf8")
LO = tuple("lo-%03d" % i for i in range(1, 9))
LOCALES = ("en", "es", "pt", "ru", "tr")

rule = r"\.lo-photo-details__stack\s*\{([^}]*)\}"
def check_css(text):
    match = re.search(rule, text)
    assert match, "LO photography source width rule missing"
    props = match.group(1)
    assert re.search(r"(?:^|;)\s*width:\s*100%;", props), "Must fit parent shell"
    assert re.search(r"(?:^|;)\s*max-width:\s*960px;", props), "Avoid 720px source photo over-scaling"
    assert re.search(r"(?:^|;)\s*margin-inline:\s*auto;", props), "Photos centered within site nav"
    assert "100vw" not in props and "50vw" not in props
    assert "margin-inline:calc" not in props, "No negative full-bleed breakout"
    assert re.search(r"\.lo-photo-details__figure img\s*\{[^}]*width:100%;height:auto;object-fit:contain", text)

check_css(CSS)
check_css(BUILT_CSS)

checked = 0
for loc in LOCALES:
    for sku in LO:
        rel = ("products/" if loc == "en" else loc + "/products/") + sku + "/index.html"
        path = DIST / rel
        assert path.is_file(), rel
        html = path.read_text(encoding="utf8")
        assert html.count('id="product-detail-photos"') == 1, rel
        assert html.count('class="lo-photo-details__stack"') == 1, rel
        assert html.count('class="lo-photo-details__figure"') == 2, rel
        assert re.search(r'<section class="section lo-photo-details"[^>]*><div class="shell">', html), rel
        # The actual SKU photography is still selected by the source/CMS,
        # never overwritten with placeholder images or a new file path.
        assert "/assets/lo/detail/" + sku + "-lifestyle.webp" in html, rel
        assert "/assets/lo/detail/" + sku + "-design.webp" in html, rel
        assert '<img id="main-photo"' in html, rel
        checked += 1

# Main photo thumbnails for every existing product page already use bounded
# 100%-width, overflow-hidden galleries. No other product pages need a
# broad CSS rewrite to address this particular 100vw breakout.
all_product_pages = list(DIST.rglob("products/*/index.html"))
assert len(all_product_pages) >= checked, "Missing existing product pages"
for page in all_product_pages:
    html = page.read_text(encoding="utf8")
    assert 'class="product-detail__main"' in html, page
    assert 'class="product-detail__thumbs"' in html, page
assert re.search(r"\.product-detail__main\s*\{[^}]*overflow:hidden", CSS)
assert re.search(r"\.product-detail__main img\s*\{[^}]*width:100%;height:100%;object-fit:contain", CSS)
print("XUYI_PRODUCT_IMAGES_IN_HEADER_WIDTH_40_LO_LOCALES",
      "ALL_PRODUCT_PAGES", len(all_product_pages), "PASS")
