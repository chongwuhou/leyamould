#!/usr/bin/env python3
"""Check traceable sources and non-generic content, no external requests."""
from pathlib import Path
import json,re,html
ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/"dist"
items=json.loads((ROOT/"data/editorial-evidence.json").read_text(encoding="utf-8"))
assert len(items)>=6
for slug,item in items.items():
    doc=(DIST/"blog"/slug/"index.html").read_text(encoding="utf-8")
    assert 'class="blog-evidence"' in doc,slug
    assert 'id="primary-sources"' in doc,slug
    assert html.escape(item["title"],quote=True) in doc,slug
    assert 'article:modified_time" content="2026-10-10"' in doc,slug
    for ref in item["sources"]:
        assert ref["url"] in doc,(slug,ref["url"])
        assert ref["url"].startswith(("https://www.fda.gov/","https://eur-lex.europa.eu/","https://www.iso.org/"))
    assert 'not product certification' in doc,slug
quality=(DIST/"quality-control/index.html").read_text(encoding="utf-8")
factory=(DIST/"manufacturing/index.html").read_text(encoding="utf-8")
about=(DIST/"about/index.html").read_text(encoding="utf-8")
for marker in ("SOURCE-CHECKED QUALITY GUIDANCE","ISO 2859-1:2026","2024/3190","FDA food-contact"):
    assert marker in quality,marker
for marker in ("PRODUCTION HANDOFF","Part and Material Record","Packing and Inspection Release"):
    assert marker in factory,marker
for marker in ("Four Traceable Model References","2501","2292","2508","501"):
    assert marker in about,marker
assert '<table class="spec">' in (DIST/"products/2501/index.html").read_text(encoding="utf-8")
print("XUYI_EDITORIAL_EVIDENCE_PASSED",len(items),"sourced buyer guides; 3 company/QA pages")