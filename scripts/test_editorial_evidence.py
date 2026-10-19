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
    # Original Oct 10 primary-source annotations were independently expanded
    # on Oct 14. Read real source editorial ownership rather than freeze 2026-10-10.
    reviewed=json.loads((ROOT/"data/blog-depth-evidence-en.json").read_text(encoding="utf8"))["articles"]
    for batch in (1,2,3):
        reviewed.update(json.loads((ROOT/f"data/blog-deep-research-part{batch}.json").read_text(encoding="utf8"))["articles"])
    guides=json.loads((ROOT/"data/blog-guides.json").read_text(encoding="utf8"))
    post=next(item for item in guides if item["slug"]==slug)
    date=max(post["updated"],"2026-10-14" if slug in reviewed else "2026-10-10")
    assert f'article:modified_time" content="{date}"' in doc,slug
    for ref in item["sources"]:
        assert ref["url"] in doc,(slug,ref["url"])
        assert ref["url"].startswith(("https://www.fda.gov/","https://eur-lex.europa.eu/","https://www.iso.org/","https://www.eastman.com/","https://www.uspto.gov/","https://www.pantone.com/","https://health.clevelandclinic.org/"))
    assert 'not product certification' in doc,slug
quality=(DIST/"quality-control/index.html").read_text(encoding="utf-8")
factory=(DIST/"manufacturing/index.html").read_text(encoding="utf-8")
about=(DIST/"about/index.html").read_text(encoding="utf-8")
for marker in ("SOURCE-CHECKED QUALITY GUIDANCE","ISO 2859-1:2026","2024/3190","FDA food-contact"):
    assert marker in quality,marker
for marker in ("PRODUCTION HANDOFF","Part and Material Record","Packing and Inspection Release"):
    assert marker in factory,marker
for marker in ("Plastic Drinkware, Built Around Your Project","Company at a Glance","How We Work","Quality as Verification","Taizhou Xuyi Household Goods Co., Ltd."):
    assert marker in about,marker
assert '<table class="spec">' in (DIST/"products/2501/index.html").read_text(encoding="utf-8")
print("XUYI_EDITORIAL_EVIDENCE_PASSED",len(items),"sourced buyer guides; 3 company/QA pages")
