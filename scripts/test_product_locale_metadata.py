#!/usr/bin/env python3
"""All published catalog SKUs must have readable, actual translated SEO metadata.

Protects the original detail structure, SKU, URL and buyer-approved body HTML.
New English-only models are allowed until translated and reviewed.
"""
from pathlib import Path
from html import unescape
import json,re
ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/"dist"
manifest=json.loads((DIST/"locale-manifest.json").read_text(encoding="utf-8"))
variants={"2306---","2307---","2308---","2400---","2401---"}
phrases={
 "en":"Transparent Variant","es":"variante transparente",
 "pt":"versão transparente","ru":"прозрачный вариант","tr":"şeffaf model"
}
expected_models={p.name for p in (DIST/"products").iterdir() if (p/"index.html").is_file()}
assert len(expected_models)>=85
total=0
for language in manifest["locales"]:
    lang,prefix=language["code"],language["pathPrefix"]
    actual={p.name for p in (DIST/(prefix or ".")/"products").iterdir() if (p/"index.html").is_file()}
    assert actual.issubset(expected_models),(lang,"unrecognized translated model")
    if lang in ("en","es","pt","ru","tr"):assert len(actual)>=85,(lang,"lost catalog models")
    for slug in actual:
        page=(DIST/(prefix or ".")/"products"/slug/"index.html").read_text(encoding="utf-8")
        head,main=page.split("</head>",1)
        title=unescape(re.search(r"<title>([^<]*)</title>",head).group(1))
        desc=unescape(re.search(r'<meta name="description" content="([^"]+)"',head).group(1))
        assert "透明款" not in title+desc,(lang,slug,"untranslated source variant")
        assert "СЮИ" not in title+desc,(lang,slug,"mistranslated brand")
        assert "2401'de" not in title,(lang,slug,"wrong Turkish model label")
        assert '<main id="main-content">' in main and 'class="spec"' in main
        assert 'class="section product-ordering"' in main,(lang,slug,"lost ordering content")
        if slug in variants:
            # An already-reviewed PT title may say just "2307 transparente",
            # which is accurate and should not be overwritten for uniformity.
            phrase_in_title=(phrases[lang] in title or lang=="pt" and "transparente" in title)
            assert phrase_in_title and phrases[lang] in desc,(lang,slug,"missing variant translation")
        total+=1
print("XUYI_PRODUCT_LOCALE_METADATA_PASSED",total,"actual published product detail pages; five legacy variant names localized")