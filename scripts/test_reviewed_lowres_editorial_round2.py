#!/usr/bin/env python3
"""Scoped generic images must never appear in identified SKU detail pages."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
from reviewed_lowres_editorial_round2 import LANGS,APPLICATIONS,SHAKER_NEW,SHAKER_OLD,DESIGN_NEW,DESIGN_OLD,DESIGN_ALT
DIST=ROOT/"dist"
for path in (SHAKER_NEW,DESIGN_NEW):
    data=(DIST/path.lstrip("/")).read_bytes()
    assert len(data)>30000 and data[:4]==b"RIFF" and data[8:12]==b"WEBP",path
checked=0
for lang in LANGS:
    prefix="" if lang=="en" else lang+"/"
    href="/" if lang=="en" else "/"+lang+"/"
    for app in APPLICATIONS:
        body=(DIST/prefix/"applications"/app/"index.html").read_text(encoding="utf8")
        anchor='<a class="category" href="'+href+'collections/plastic-shaker-bottles/"><div class="category__photo"><img src="'+SHAKER_NEW+'"'
        assert body.count(anchor)==1,(lang,app)
        assert SHAKER_OLD not in body,(lang,app)
        assert "ai-concept-disclosure" not in body
        checked+=1
    body=(DIST/prefix/"manufacturing/index.html").read_text(encoding="utf8")
    assert body.count('<div class="whyv2-factory-detail__image"><img src="'+DESIGN_NEW+'"')==1
    assert DESIGN_OLD not in body
    assert DESIGN_ALT[lang] in body,lang
    assert "ai-concept-disclosure" not in body
    checked+=1
assert checked==30,checked
for file in DIST.glob("**/products/*/index.html"):
    body=file.read_text(encoding="utf8")
    assert SHAKER_NEW not in body and DESIGN_NEW not in body,("SKU substitution",str(file))
print("XUYI_ROUND2_IMAGE_SCOPE_PASSED",checked,"placements, no SKU edits")
