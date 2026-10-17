"""Safe, evidence-preserving SEO cleanup of catalog image ALT strings.

Only correct objectively broken source identifiers and gallery placeholders.
Never add unverified BPA claims, materials, certifications or sales adjectives.
"""
import html
import re
from product_locale_seo import TRANSPARENT

_IMG=re.compile(r'<img\b[^>]*>',re.I)
_ALT=re.compile(r'\balt="([^"]*)"',re.I)
_VARIANT=re.compile(r'(\d{3,4})\s*透明款')
_MODEL=re.compile(r'(?i)(?:model|modelo|modeli|модель)\s+(\d{3,4})')
_GENERIC_VIEW=re.compile(r'(?i)\b(?:view|visualizar|вид|görünüm)\s+(\d{1,2})\b')
_PHOTO={
    "en":"product catalog photo",
    "es":"foto del producto",
    "pt":"foto do produto",
    "ru":"фото товара",
    "tr":"ürün fotoğrafı"
}

def readable_alt(raw,language):
    text=html.unescape(raw)
    if language not in TRANSPARENT:return text
    text=_VARIANT.sub(lambda m:m.group(1)+" ("+TRANSPARENT[language]+")",text)
    if language=="ru":text=text.replace("СЮИ","XUYI")
    models=[m for m in _MODEL.finditer(text) if m.group(1)=="2506"]
    if len(models)>1:
        # Remove only the second occurrence of the *same* already stated SKU.
        m=models[-1]
        text=(text[:m.start()].rstrip(" ,–-")+
              text[m.end():]).strip()
    text=_GENERIC_VIEW.sub(lambda m:_PHOTO[language]+(
        " "+m.group(1) if int(m.group(1))>1 else ""),text)
    return re.sub(r"\s+"," ",text).strip()

def polish_image_alt(markup,language):
    def replace_tag(match):
        tag=match.group(0)
        alt=_ALT.search(tag)
        if not alt:return tag
        source=html.unescape(alt.group(1))
        corrected=readable_alt(source,language)
        if source==corrected:return tag
        replacement='alt="'+html.escape(corrected,quote=True)+'"'
        return tag[:alt.start()]+replacement+tag[alt.end():]
    return _IMG.sub(replace_tag,markup)
