"""Source-rendered reciprocal hreflang for the five complete product locales."""
from __future__ import annotations
import re

ORIGIN="https://xuyibottles.com"
LOCALES=("en","es","pt","ru","tr")
PRODUCT_ROUTE=re.compile(r"/products/([a-z0-9_-]+)/",re.I)
ALT=re.compile(r'<link\s+rel="alternate"\s+hreflang="(?:en|es|pt|ru|tr|x-default)"\s+href="[^"]*"\s*/?>',re.I)

def apply_to_document(markup,route,locale):
    """Write all five reciprocal product-detail or product-index alternates."""
    if locale not in LOCALES:return markup
    base=str(route or "/")
    prefix="/"+locale
    if locale!="en" and base.startswith(prefix+"/"):
        base=base[len(prefix):]
    match=PRODUCT_ROUTE.fullmatch(base)
    if match:
        suffix="/products/"+match.group(1)+"/"
    elif base=="/products/":
        suffix="/products/"
    else:
        return markup
    urls={
        "en":ORIGIN+suffix,
        "es":ORIGIN+"/es"+suffix,
        "pt":ORIGIN+"/pt"+suffix,
        "ru":ORIGIN+"/ru"+suffix,
        "tr":ORIGIN+"/tr"+suffix,
    }
    tags="".join(
        '<link rel="alternate" hreflang="'+lang+'" href="'+urls[lang]+'">'
        for lang in LOCALES
    )+'<link rel="alternate" hreflang="x-default" href="'+urls["en"]+'">'
    head,separator,tail=markup.partition("</head>")
    if not separator:raise ValueError("Product page has no closing head: "+base)
    cleaned=ALT.sub("",head)
    if tags in cleaned:return markup
    return cleaned+tags+separator+tail