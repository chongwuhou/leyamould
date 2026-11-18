#!/usr/bin/env python3
"""Source-template test for buyer decision tables and pre-output locale renderers.

All buyer content comes from canonical JSON and shared renderers, never patched
dist files. The test never writes to the owner's D1 database.
"""
from pathlib import Path
import json
import re
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"scripts"))
import blog_editorial
from curated_application_feature_answers import (
    TOPICS,LOCALES,TOPIC_GRIDS,render_buyer_evidence
)
from site_renderer import SERIES
from scripts.render_locales import CONTACT_FORM_TRANSLATIONS
DIST=ROOT/"dist"

guides=json.loads((ROOT/"data/blog-guides.json").read_text(encoding="utf8"))
buyer=json.loads((ROOT/"data/blog-buyer-decision-tables.json").read_text(encoding="utf8"))["articles"]
assert set(buyer)=={item["slug"] for item in guides}
assert len(buyer)>=16  # Historic reviewed baseline; new published blogs are allowed
blog_links=0
for slug,source_table in buyer.items():
    # D1 is authoritative. A CMS owner may have changed this table after the
    # source fixture was reviewed, so validate the effective D1 table rather
    # than requiring byte-for-byte equality with the old source HTML.
    table=blog_editorial.GUIDES[slug].get("buyerDecisionTable") or source_table
    assert len(table["head"])==3 and len(table["rows"])>=4
    for cells in table["rows"]:assert len(cells)==3 and all(len(str(x).strip())>=2 for x in cells)
    page=(DIST/"blog"/slug/"index.html").read_text(encoding="utf8")
    # The visible module is the stable contract. Its copy may be an
    # owner-maintained D1 value and therefore must not be compared with an old
    # source-fixture title byte-for-byte.
    assert page.count('id="buyer-decision-table"')==1,slug
    assert page.count('class="blog-buyer-matrix"')==1,slug
    assert "<table>" in page and "</table>" in page,slug
    html=blog_editorial.render_buyer_matrix(slug)
    assert 'class="blog-buyer-matrix"' in html
    for label,url in table["links"]:
        assert url.startswith("/") and not url.startswith("//")
        assert (DIST/url.split("#",1)[0].lstrip("/")/"index.html").is_file(),(slug,url)
        if re.fullmatch(r"/products/[A-Za-z0-9_-]+/",url):
            model=url.strip("/").split("/")[-1]
            assert any(v["slug"]==model for v in SERIES.values()),(slug,model)
        blog_links+=1

assert set(TOPIC_GRIDS["topics"])==set(TOPICS)
assert len(TOPICS)==10
for route in TOPICS:
    for locale in LOCALES:
        addition=render_buyer_evidence("/"+route+"/",locale,"<div>Approved CMS body</div>")
        assert addition.count('id="buyer-evidence-checks"')==1,(route,locale)
        assert render_buyer_evidence(route,locale,addition)=="",(route,locale,"CMS module override")
        path=DIST/(("" if locale=="en" else locale+"/")+route)/"index.html"
        doc=path.read_text(encoding="utf8")
        assert doc.count('id="buyer-evidence-checks"')==1,(route,locale)
        assert doc.count('class="topic-decision-grid"')==(1 if locale=="en" else 0),(route,locale)
        if locale=="en":
            assert TOPIC_GRIDS["topics"][route]["title"] in doc
            target=TOPIC_GRIDS["topics"][route]["link"][1]
            assert (DIST/target.split("#",1)[0].lstrip("/")/"index.html").is_file(),(route,target)

form_sources=(ROOT/"templates/site/contact-form.html").read_text(encoding="utf8")
assert form_sources.count('class="inquiry-required-note"')==1
for locale in ("en","es","pt","ru","tr"):
    folder=DIST/(locale if locale!="en" else ".")/"contact/index.html"
    doc=folder.read_text(encoding="utf8")
    assert doc.count('class="inquiry-required-note"')==1,locale
    match=re.search(r'<form class="form" id="inquiry"[^>]*>(.*?)</form>',doc,re.S)
    assert match,locale
    fields=re.findall(r'<(?:input|select|textarea)[^>]*\bname="([^"]+)"[^>]*>',match.group(1))
    assert set(fields)=={"company","email","model","quantity","country","type","material","requirements","consent","website"},(locale,fields)
    for field in ("company","email","requirements","consent"):
        tag=re.search(r'<(?:input|select|textarea)[^>]*\bname="'+field+r'"[^>]*>',match.group(1))
        assert tag and "required" in tag.group(0),(locale,field)
    for field in ("model","quantity","country","type","material"):
        tag=re.search(r'<(?:input|select|textarea)[^>]*\bname="'+field+r'"[^>]*>',match.group(1))
        assert tag and "required" not in tag.group(0),(locale,field)
    if locale!="en":
        en_text=next(x for x in CONTACT_FORM_TRANSLATIONS[locale] if x.startswith("Only company name"))
        assert CONTACT_FORM_TRANSLATIONS[locale][en_text] in doc,locale
for model in ("2095","2514","5247"):
    assert (DIST/"products"/model/"index.html").is_file(),model
assert (DIST/"sitemap.xml").read_text(encoding="utf8").count("<loc>")>=755

release=(ROOT/"scripts/build_release.py").read_text(encoding="utf8")
assert "improve_application_feature_answers(DIST)" not in release
source=(ROOT/"site_renderer.py").read_text(encoding="utf8")
locales=(ROOT/"scripts/render_locales.py").read_text(encoding="utf8")
assert 'render_buyer_evidence(route,"en",main)' in source
assert 'render_buyer_evidence(route,loc,body)' in locales
assert (ROOT/"functions/_shared/blog-cms.js").read_text(encoding="utf8").count("renderBuyerDecisionTable(post)")>=2
print("XUYI_REVIEWED_SOURCE_CONTENT_GATE_PASSED",len(buyer),"blog tables",len(TOPICS)*len(LOCALES),"locale modules",blog_links,"linked CTAs; prior URLs retained")