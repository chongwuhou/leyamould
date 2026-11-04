#!/usr/bin/env python3
"""All product index and SKU detail routes have reciprocal five-locale hreflang."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
from product_hreflang import apply_to_document,LOCALES,ORIGIN

routes=("/products/","/products/2501/","/products/2413/")
for route in routes:
    for locale in LOCALES:
        localized=route if locale=="en" else "/"+locale+route
        source='<html><head><link rel="alternate" hreflang="en" href="https://old.example/"></head><body></body></html>'
        rendered=apply_to_document(source,localized,locale)
        for lang in LOCALES:
            prefix="" if lang=="en" else "/"+lang
            expected=ORIGIN+prefix+route
            assert '<link rel="alternate" hreflang="'+lang+'" href="'+expected+'">' in rendered,(locale,route,lang)
        assert '<link rel="alternate" hreflang="x-default" href="'+ORIGIN+route+'">' in rendered
        assert rendered.count('rel="alternate" hreflang=')==6,(locale,route,"duplicate hreflang")
        assert apply_to_document(rendered,localized,locale)==rendered,(locale,route,"not idempotent")
assert apply_to_document("<html><head></head></html>","/collections/kids-water-bottles/","en")=="<html><head></head></html>"
print("XUYI_PRODUCT_INDEX_AND_DETAIL_HREFLANG_PASSED",len(routes)*len(LOCALES),"rendered pages")