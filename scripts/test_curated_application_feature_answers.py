#!/usr/bin/env python3
"""Review guard for context-specific answers across five application/feature locales."""
from pathlib import Path
import html
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
from curated_application_feature_answers import LOCALES,LABELS,TOPICS,EYEBROWS
from model_catalog_buyer_comparison import SERIES
DIST=ROOT/"dist"
assert len(TOPICS)==10 and len(LOCALES)==5
count=0
for route,locale_values in TOPICS.items():
    assert route.startswith(("applications/","features/"))
    for lang in LOCALES:
        prefix="" if lang=="en" else lang+"/"
        page=DIST/prefix/route/"index.html"
        text=page.read_text(encoding="utf8")
        assert text.count('id="buyer-evidence-checks"')==1,(route,lang)
        block=html.unescape(text.split('id="buyer-evidence-checks"',1)[1].split("</section>",1)[0])
        assert len(locale_values[lang])==2 and block.count("<li>")==2,(route,lang)
        for answer in locale_values[lang]:
            assert answer in block,(route,lang,answer)
        assert LABELS[lang][0] in block,(route,lang)
        assert EYEBROWS[lang] in block,(route,lang)
        href="/"+prefix+"contact/#inquiry"
        assert 'href="'+href+'"' in block,(route,lang,href)
        assert "guaranteed leakproof" not in block.lower()
        count+=1
assert count==50,count
print("XUYI_APPLICATION_FEATURE_SOURCE_REVIEW_50_LOCALIZED_PAGES_PASSED")