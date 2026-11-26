#!/usr/bin/env python3
"""Regression gate for the cap-molds-compatible floating contact rail."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
CSS = (ROOT / "assets/site.css").read_text(encoding="utf-8")

# The final source-of-truth rule must be the white outlined rail, not one of
# the historical colored-circle overrides that remain earlier in the stylesheet.
css_marker = "Floating contact rail parity with cap-molds.com"
assert css_marker in CSS
final_css = CSS[CSS.index(css_marker) :]
assert "right:20px" in final_css and "bottom:90px" in final_css
assert "background:#fff!important" in final_css
assert "border:1.5px solid #cbd5e1" in final_css
assert "fill:currentColor!important" in final_css

pages = sorted(DIST.rglob("*.html"))
assert pages, "dist is empty; run scripts/build_release.py first"
checked = 0
for path in pages:
    html = path.read_text(encoding="utf-8")
    if 'class="mould-site"' not in html:
        continue
    match = re.search(r'<aside class="rail"[^>]*>(.*?)</aside>', html, re.S)
    assert match, path
    rail = match.group(1)
    positions = [rail.index(f'rail-float--{name}') for name in ("whatsapp", "wechat", "phone")]
    assert positions == sorted(positions), (path, positions)
    assert 'viewBox="0 0 448 512"' in rail, path
    assert 'viewBox="0 0 576 512"' in rail, path
    assert 'viewBox="0 0 512 512"' in rail, path
    assert 'background:#353a8e' not in rail
    checked += 1

assert checked, "No mould pages found in dist"
print("MOULD_RAIL_PASSED", checked, "pages")
