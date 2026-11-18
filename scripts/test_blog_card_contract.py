"""Regression guard for current and legacy Blog card image contracts.

The renderer emits news-card__image. Older D1/CMS page bodies can still
contain news-card__media, so both contracts remain supported until those
owner-edited bodies are migrated through the normal CMS path.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "assets" / "site.css").read_text(encoding="utf-8")
RENDERER = (ROOT / "site_renderer.py").read_text(encoding="utf-8")
HEAD = (ROOT / "templates" / "site" / "head.html").read_text(encoding="utf-8")

def fail(message):
    print("::error::" + message)
    sys.exit(1)

for selector in (".news-card__image", ".news-card__image img", ".news-card__media", ".news-card__media img"):
    if selector not in CSS:
        fail("missing Blog card compatibility selector: " + selector)
if not re.search(r"object-fit\\s*:\\s*cover", CSS):
    fail("Blog card images must use object-fit: cover")
if 'class="news-card__image"' not in RENDERER:
    fail("canonical Blog renderer no longer emits news-card__image")
if "{{ASSET_VERSION}}" not in HEAD or "/assets/site.css?v={{ASSET_VERSION}}" not in HEAD:
    fail("shared CSS must use the renderer asset version")

dist = ROOT / "dist"
if dist.exists():
    card_re = re.compile(r'<article\b[^>]*class="[^"]*\bnews-card\b[^"]*"[^>]*>[\s\S]*?</article>', re.I)
    for html_path in sorted(dist.rglob("*.html")):
        if any(part in {"admin", "api"} for part in html_path.relative_to(dist).parts):
            continue
        html = html_path.read_text(encoding="utf-8", errors="ignore")
        for card in card_re.findall(html):
            if not re.search(r'class="[^"]*(?:news-card__image|news-card__media)[^"]*"', card):
                fail("Blog card has no supported image wrapper: " + html_path.relative_to(dist).as_posix())

print("XUYI_BLOG_CARD_CONTRACT_PASSED")
