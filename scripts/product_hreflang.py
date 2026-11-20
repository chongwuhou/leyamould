"""Source-rendered reciprocal hreflang for every publish-ready product locale in D1."""
from __future__ import annotations
import re

ORIGIN="https://leyamould.com"
PRODUCT_ROUTE=re.compile(r"/products/([a-z0-9_-]+)/",re.I)
ALT=re.compile(r'<link\s+rel="alternate"\s+hreflang="[^"]+"\s+href="[^"]*"\s*/?>',re.I)

def apply_to_document(markup,route,locale,languages):
    """Write reciprocal product alternates from the D1 language registry."""
    configured=[item for item in (languages or []) if item.get("code") and item.get("pathPrefix") is not None]
    configured=[{"code":str(item["code"]).strip().lower(),"pathPrefix":str(item.get("pathPrefix") or "").strip("/")} for item in configured]
    codes=[item["code"] for item in configured]
    if locale not in codes:return markup
    source=next((item for item in configured if not item["pathPrefix"]),configured[0] if configured else None)
    if not source:return markup
    base=str(route or "/")
    prefix="/"+next((item["pathPrefix"] for item in configured if item["code"]==locale),"")
    if prefix!="/" and base.startswith(prefix+"/"):base=base[len(prefix):]
    match=PRODUCT_ROUTE.fullmatch(base)
    if match:suffix="/products/"+match.group(1)+"/"
    elif base=="/products/":suffix="/products/"
    else:return markup
    urls={item["code"]:ORIGIN+("/"+item["pathPrefix"] if item["pathPrefix"] else "")+suffix for item in configured}
    tags="".join('<link rel="alternate" hreflang="'+item["code"]+'" href="'+urls[item["code"]]+'">' for item in configured)+'<link rel="alternate" hreflang="x-default" href="'+urls[source["code"]]+'">'
    head,separator,tail=markup.partition("</head>")
    if not separator:raise ValueError("Product page has no closing head: "+base)
    cleaned=ALT.sub("",head)
    if tags in cleaned:return markup
    return cleaned+tags+separator+tail
