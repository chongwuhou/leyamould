"""Static editorial and cover gate for the reviewed mould-news registry."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
DATA = json.loads((ROOT / "data" / "mould-news-editorial.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((ROOT / "data" / "mould-news-image-manifest.json").read_text(encoding="utf-8"))

assert DATA.get("locales") == ["en", "es"]
items = DATA.get("items") or []
assert items
assert len({item["slug"] for item in items}) == len(items)
manifest = {item["slug"]: item for item in MANIFEST.get("items", [])}
assert set(manifest) == {item["slug"] for item in items}
hashes = set()
for item in items:
    assert len(item["title"]["en"]) >= 30 and len(item["title"]["es"]) >= 30
    assert len(item["description"]["en"]) >= 80 and len(item["description"]["es"]) >= 80
    assert len(item["sections"]["en"]) >= 7 and len(item["sections"]["es"]) >= 7
    assert all(len(part["paragraph"]) >= 650 for part in item["sections"]["en"])
    assert all(len(part["paragraph"]) >= 650 for part in item["sections"]["es"])
    assert len(item["checklist"]["en"]) >= 10 and len(item["checklist"]["es"]) >= 10
    assert len(item["faqs"]["en"]) >= 4 and len(item["faqs"]["es"]) >= 4
    assert 2 <= len(item["products"]) <= 5 and 2 <= len(item["related"]) <= 3
    cover = ROOT / item["cover"].lstrip("/")
    assert cover.is_file(), cover
    with Image.open(cover) as im:
        assert im.format == "WEBP" and im.size == (1200, 800), (item["slug"], im.format, im.size)
    size = cover.stat().st_size
    assert 30_000 <= size <= 350_000, (item["slug"], size)
    sha = hashlib.sha256(cover.read_bytes()).hexdigest()
    assert sha == manifest[item["slug"]]["sha256"] and sha not in hashes
    hashes.add(sha)
    assert manifest[item["slug"]]["review"]["status"] == "reviewed"

def check_page(prefix: str, item: dict) -> None:
    category = "news" if item["category"] == "news" else "Bottle-Cap-Machine"
    path = DIST / prefix / category / f"{item['slug']}.html" if prefix else DIST / category / f"{item['slug']}.html"
    html = path.read_text(encoding="utf-8")
    # A reviewed D1 owner edit is allowed to keep its own renderer/content. In
    # that case this source fallback must not fail the deployment; the registry
    # and cover gates above still remain mandatory. When the mould registry is
    # the active source fallback, enforce the complete seven-part contract.
    if 'data-editorial-source="mould-registry"' not in html:
        return
    body = html.split('<article class="blog-editorial__body"', 1)[1].split('</article>', 1)[0]
    for marker in ("blog-editorial__body", "blog-editorial__product-link", "blog-related__item", "blog-buyer-matrix", "primary-sources"):
        assert marker in html, (path, marker)
    assert body.count('class="blog-section"') == 7
    assert body.count('class="blog-editorial__product-link"') == 3
    assert body.count('class="blog-related__item"') == 3
    assert body.count("<details>") == 4
    assert "FAQPage" in html and "application/ld+json" in html

for item in items:
    check_page("", item)
    check_page("es", item)
print("MOULD_NEWS_EDITORIAL_OK", len(items), "articles", "unique covers", len(hashes))
