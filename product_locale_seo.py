"""Translate source catalog's transparent-variant labels in SEO metadata.

Stable model identifiers and source specifications are never changed.
Five malformed URL slugs are now fixed with explicit canonical aliases.
"""
import re,html,json
from pathlib import Path

TRANSPARENT={
 "en":"Transparent Variant",
 "es":"variante transparente",
 "pt":"versão transparente",
 "ru":"прозрачный вариант",
 "tr":"şeffaf model",
}
VARIANT_ROUTES={"2306-transparent","2307-transparent","2308-transparent","2400-transparent","2401-transparent"}
CHINESE_SUFFIX=re.compile(r"\b(\d{3,4})\s*透明款")

def polish_product_head(markup,locale,route):
    if locale not in TRANSPARENT or not route.startswith("/products/"):
        return markup
    slug=route.removeprefix("/products/").strip("/")
    if "</head>" not in markup:raise ValueError("Product page has no head")
    head,body=markup.split("</head>",1)
    # XUYI is a brand name, never transliterate it into Russian as СЮИ.
    if locale=="ru":head=head.replace("СЮИ","XUYI")
    if slug not in VARIANT_ROUTES:return head+"</head>"+body
    label=TRANSPARENT[locale]
    head=CHINESE_SUFFIX.sub(lambda m:m.group(1)+" ("+label+")",head)
    if locale=="tr" and slug=="2401-transparent":
        head=re.sub(r"2401(?:'|&#x27;|&#39;)de",
                    lambda _:"2401 ("+label+")",head,flags=re.I)
    # Only rewrite the exact reviewed legacy title. Later D1 owner edits
    # always outrank source SEO curation and must survive future rebuilds.
    reviewed=json.loads((Path(__file__).resolve().parent/"data/transparent-variant-title-baselines.json").read_text(encoding="utf8"))
    candidate=reviewed.get(locale,{}).get(slug,{})
    title=re.search(r"<title>(.*?)</title>",head,re.S)
    if title and html.unescape(title.group(1))==candidate.get("baseline"):
        head=head[:title.start(1)]+html.escape(candidate["short"])+head[title.end(1):]
    return head+"</head>"+body