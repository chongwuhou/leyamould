#!/usr/bin/env python3
"""Product hreflang regression test driven by the generated D1 locale manifest."""
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
from product_hreflang import apply_to_document,ORIGIN

def load_languages():
    manifest=ROOT/"dist/locale-manifest.json"
    if manifest.is_file():
        data=json.loads(manifest.read_text(encoding="utf-8"))
        return data.get("locales") or []
    snapshot=ROOT/"_local_ops/build-snapshot.json"
    if snapshot.is_file():
        data=json.loads(snapshot.read_text(encoding="utf-8"))
        config=data.get("languages") or {}
        return [
            {"code":row["code"],"pathPrefix":row.get("pathPrefix") or ""}
            for row in config.get("languages",[])
            if row.get("enabled") and row.get("publishReady")
        ]
    raise SystemExit("XUYI_PRODUCT_HREFLANG_TEST_REQUIRES_D1_LOCALE_MANIFEST")

LANGUAGES=load_languages()
CODES=[row["code"] for row in LANGUAGES]
PREFIXES={row["code"]:row.get("pathPrefix") or "" for row in LANGUAGES}
SOURCE=next((row["code"] for row in LANGUAGES if not row.get("pathPrefix")),CODES[0])
routes=("/products/","/products/2501/","/products/2413/")

for route in routes:
    for locale in CODES:
        localized=route if not PREFIXES[locale] else "/"+PREFIXES[locale]+route
        source='<html><head><link rel="alternate" hreflang="'+SOURCE+'" href="https://old.example/"></head><body></body></html>'
        rendered=apply_to_document(source,localized,locale,LANGUAGES)
        for lang in CODES:
            prefix="" if not PREFIXES[lang] else "/"+PREFIXES[lang]
            expected=ORIGIN+prefix+route
            assert '<link rel="alternate" hreflang="'+lang+'" href="'+expected+'">' in rendered,(locale,route,lang)
        assert '<link rel="alternate" hreflang="x-default" href="'+ORIGIN+route+'">' in rendered
        assert rendered.count('rel="alternate" hreflang=')==len(CODES)+1,(locale,route,"duplicate hreflang")
        assert apply_to_document(rendered,localized,locale,LANGUAGES)==rendered,(locale,route,"not idempotent")

assert apply_to_document("<html><head></head></html>","/collections/kids-water-bottles/",SOURCE,LANGUAGES)=="<html><head></head></html>"
print("XUYI_PRODUCT_INDEX_AND_DETAIL_HREFLANG_PASSED",len(routes)*len(CODES),"rendered pages","LOCALES",len(CODES))
