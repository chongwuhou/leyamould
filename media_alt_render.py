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
