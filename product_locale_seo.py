"""Translate source catalog's transparent-variant labels in SEO metadata.

Stable part numbers, source specifications and URL slugs are never changed.
"""
import re

TRANSPARENT={
 "en":"Transparent Variant",
 "es":"variante transparente",
 "pt":"versão transparente",
 "ru":"прозрачный вариант",
 "tr":"şeffaf model",
}
VARIANT_ROUTES={"2306---","2307---","2308---","2400---","2401---"}
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
    if locale=="tr" and slug=="2401---":
        head=re.sub(r"2401(?:'|&#x27;|&#39;)de",
                    lambda _:"2401 ("+label+")",head,flags=re.I)
    return head+"</head>"+body