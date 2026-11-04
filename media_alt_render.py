"""Apply manually reviewed, image-specific R2 ALT overrides in each locale.

No fabrication: if there is no translation for the requested language, retain
the existing contextual ALT. Never replace product photos from an unrelated
media source or a shared product/model illustration.
"""
import html
import re

_IMAGE=re.compile(r'<img\b[^>]*>',re.I)
_SRC=re.compile(r'\bsrc="([^"]+)"',re.I)
_ALT=re.compile(r'\balt="[^"]*"',re.I)
_ALLOWED=re.compile(r'^/media/(?:product|page|shared|ppt|excel|group|capability|gallery|blog)/[a-zA-Z0-9._-]+\.(?:png|jpg|jpeg|webp)$')

FAMILY_ALT={
    "en":"XUYI factory catalog family image for related plastic drinkware variants",
    "es":"Imagen familiar del catálogo de fábrica XUYI para variantes relacionadas de botellas plásticas",
    "pt":"Imagem de família do catálogo da fábrica XUYI para variantes relacionadas de garrafas plásticas",
    "ru":"Семейное фото пластиковых изделий из каталога фабрики XUYI для связанных вариантов",
    "tr":"XUYI fabrika kataloğunda ilişkili plastik matara varyantlarının aile görseli",
}

# Exact original D1-generated descriptions for three family-image records.
# Only untouched locale fields are upgraded; any CMS owner edit wins.
FAMILY_ALT_BASELINES={
    "/media/product/11feee2556e1dc60de01afdee3612f28.webp":{
        "en":"XUYI plastic sports water bottle model 2061, product photograph",
        "es":"Fotografía del producto XUYI botella deportiva de plástico, modelo 2061",
        "pt":"Foto do produto XUYI garrafa esportiva de plástico, modelo 2061",
        "ru":"Фотография товара XUYI: пластиковая спортивная бутылка, модель 2061",
        "tr":"XUYI plastik spor matarası ürün fotoğrafı, model 2061",
    },
    "/media/product/7505c01962b02ca579532dc7177bd1b7.webp":{
        "en":"XUYI plastic sports water bottle model 2080, product photograph",
        "es":"Fotografía del producto XUYI botella deportiva de plástico, modelo 2080",
        "pt":"Foto do produto XUYI garrafa esportiva de plástico, modelo 2080",
        "ru":"Фотография товара XUYI: пластиковая спортивная бутылка, модель 2080",
        "tr":"XUYI plastik spor matarası ürün fotoğrafı, model 2080",
    },
    "/media/product/a7e8888d5451448d25edf1c48f9f0f2a.webp":{
        "en":"XUYI large-capacity plastic water bottle model 2082, product photograph",
        "es":"Fotografía del producto XUYI botella de plástico de gran capacidad, modelo 2082",
        "pt":"Foto do produto XUYI garrafa plástica de grande capacidade, modelo 2082",
        "ru":"Фотография товара XUYI: пластиковая бутылка большого объёма, модель 2082",
        "tr":"XUYI büyük hacimli plastik matara ürün fotoğrafı, model 2082",
    },
}

def approved_alts(state):
    found={}
    for row in state.get("mediaAlts",[]):
        path=row.get("path","")
        values=row.get("translations",{})
        if not _ALLOWED.fullmatch(path) or not isinstance(values,dict):
            raise ValueError("Invalid reviewed R2 ALT entry")
        valid={}
        for language,value in values.items():
            if not re.fullmatch(r'[a-z]{2,3}(?:-[a-z0-9]{2,8})*',language):
                raise ValueError("Invalid R2 ALT locale")
            if not isinstance(value,str) or not value.strip() or len(value)>180 or "<" in value:
                raise ValueError("Invalid R2 ALT text")
            valid[language]=value.strip()
        if "en" not in valid:raise ValueError("Managed R2 ALT has no English source")
        found[path]=valid
    family_paths=set()
    for product in state.get("products",[]):
        content=product.get("content") or {}
        if isinstance(content,dict) and content.get("imageReviewStatus")=="visually_reviewed_source_family_image":
            path=content.get("image")
            if isinstance(path,str):family_paths.add(path)
    for path in family_paths:
        baseline=FAMILY_ALT_BASELINES.get(path)
        current=found.get(path)
        if not baseline or not current:continue
        for language,old_value in baseline.items():
            if current.get(language)==old_value:
                current[language]=FAMILY_ALT[language]
    return found

def apply_media_alts(markup,state,locale):
    lookup=approved_alts(state)
    if not lookup:return markup
    def patch(match):
        tag=match.group(0)
        source=_SRC.search(tag)
        if not source:return tag
        url=html.unescape(source.group(1)).split("?",1)[0]
        translated=lookup.get(url,{}).get(locale)
        if not translated:return tag
        attr='alt="'+html.escape(translated,quote=True)+'"'
        return _ALT.sub(lambda _:attr,tag,count=1) if _ALT.search(tag) else tag[:-1]+" "+attr+">"
    return _IMAGE.sub(patch,markup)
