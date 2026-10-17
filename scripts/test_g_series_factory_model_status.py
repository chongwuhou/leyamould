#!/usr/bin/env python3
"""Eight G-series numbers are factory models in all five languages.

Only capacity / materials / packing are unknown until the factory spec is
confirmed. Regression must never restore an incorrect non-factory label.
"""
from pathlib import Path
import html
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from gallery_catalog import GALLERY,LABELS

BAD={
 "en":("not a factory model","style reference only","photo reference"),
 "es":("no es modelo de fábrica","referencia visual","referencia de foto"),
 "pt":("não é modelo de fábrica","referência visual","referência de foto"),
 "ru":("не заводская модель","не модель завода","фотоартикул"),
 "tr":("fabrika modeli değil","fabrika modeli değildir","fotoğraf referansı")
}
assert len(GALLERY)==8 and all(x.get("factoryModel") is True and "referenceOnly" not in x for x in GALLERY)
count=0
for lang in ("en","es","pt","ru","tr"):
    for label in LABELS[lang]:
        assert not any(term in label.lower() for term in BAD[lang]),(lang,label)
    prefix="" if lang=="en" else lang+"/"
    catalog=html.unescape((ROOT/"dist"/prefix/"products/index.html").read_text(encoding="utf8"))
    for item in GALLERY:
        slug=item["slug"]
        file=ROOT/"dist"/prefix/"products"/slug/"index.html"
        page=html.unescape(file.read_text(encoding="utf8"))
        for phrase in BAD[lang]:
            assert phrase not in page.lower(),(lang,slug,phrase)
        assert LABELS[lang][0] in page and LABELS[lang][10] in catalog,(lang,slug)
        assert "hreflang=\""+lang+"\"" in page
        assert item["model"] in page
        assert 'href="/'+prefix+"products/"+slug+'/"' in catalog
        count+=1
assert count==40,count
print("XUYI_G_SERIES_FACTORY_MODEL_STATUS_8_MODELS_5_LANGUAGES_PASSED")
