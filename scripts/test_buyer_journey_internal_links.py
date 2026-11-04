#!/usr/bin/env python3
"""Buyer-journey links are source-rendered, locale-native and idempotent."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"scripts"))
from buyer_journey_internal_links import PATHWAYS,LOCALES,apply_to_document

DIST=ROOT/"dist"
checked=0
for locale in LOCALES:
    prefix="" if locale=="en" else locale+"/"
    for source,targets in PATHWAYS.items():
        route="/"+source+"/" if not source.startswith("/") else source
        localized=route if locale=="en" else "/"+locale+route
        page=DIST/prefix/source/"index.html"
        assert page.is_file(),(locale,source,"missing source route")
        markup=page.read_text(encoding="utf8")
        assert markup.count('class="section buyer-pathways"')==1,(locale,source,"duplicate/missing buyer-pathways section")
        main=markup.split("<main",1)[-1].split("</main>",1)[0]
        for target in targets:
            href="/"+prefix+target+"/"
            assert main.count('href="'+href+'"')==1,(locale,source,target,"missing or duplicate localized link")
            assert (DIST/prefix/target/"index.html").is_file(),(locale,target,"target page missing")
            checked+=1
        assert apply_to_document(markup,localized,locale)==(markup,"preserved") or apply_to_document(markup,localized,locale)[0]==markup
print("XUYI_SOURCE_BUYER_JOURNEY_LINKS_PASSED",checked,"locale-native links across",len(PATHWAYS),"source routes")