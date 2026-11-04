#!/usr/bin/env python3
"""Exact, scoped replacements for reviewed generic plastic drinkware visuals.

Does not touch identified SKU photographs, R2 originals or factory evidence.
The pages retain normal category/product language and existing visible copy.
"""
from pathlib import Path
import html
import re
try:
    from scripts.reviewed_media_slot_guard import replace_if_original
except ModuleNotFoundError:
    from reviewed_media_slot_guard import replace_if_original

ROOT=Path(__file__).resolve().parent.parent
LOCALES=("en","es","pt","ru","tr")
EDITORIAL_IMAGES={
    "sports-water-bottles":(
        "/media/ppt/slide-059.webp",
        "/assets/editorial/sports-plastic-bottle.webp"
    ),
    "large-capacity-water-jugs":(
        "/media/ppt/slide-055.webp",
        "/assets/editorial/large-capacity-plastic-jug.webp"
    ),
    "kids-water-bottles":(
        "/media/ppt/slide-030.webp",
        "/assets/editorial/kids-plastic-bottle.webp"
    ),
}
OEM_OLD="/media/group/oem-sampling.webp"
OEM_NEW="/assets/curated-hd/customizable-assortment.webp"
OEM_ALT={
 "en":"Plastic bottle samples in different body colors and lid styles",
 "es":"Muestras de botellas de plástico de distintos colores y tapas",
 "pt":"Amostras de garrafas plásticas com várias cores e tampas",
 "ru":"Образцы пластиковых бутылок разных цветов и с разными крышками",
 "tr":"Farklı renk ve kapak modellerinde plastik şişe örnekleri",
}

def apply_to_document(markup,route,locale):
    """Apply only reviewed generic illustration slots in the shared renderer."""
    base=str(route or "/")
    prefix="/"+locale
    if locale!="en" and base.startswith(prefix+"/"):
        base=base[len(prefix):]
    if base=="/applications/everyday-hydration/":
        href_prefix="/" if locale=="en" else "/"+locale+"/"
        for collection,(old,new) in EDITORIAL_IMAGES.items():
            prefix_tag=('<a class="category" href="'+href_prefix+'collections/'+collection+'/">'
                        '<div class="category__photo"><img src="')
            markup,_=replace_if_original(markup,prefix_tag,old,new,locale+" "+collection)
    if base=="/capabilities/oem-odm/":
        prefix_tag='<div class="whyv2-oem-steps__sample"><img src="'
        markup,changed=replace_if_original(markup,prefix_tag,OEM_OLD,OEM_NEW,locale+" oem-sampling")
        if changed:
            pattern=(r'(<div class="whyv2-oem-steps__sample"><img src="'
                     +re.escape(OEM_NEW)+r'" alt=")[^"]*(")')
            markup,count=re.subn(pattern,lambda m:m.group(1)+html.escape(OEM_ALT[locale],quote=True)+m.group(2),markup,count=1)
            if count!=1:raise ValueError("OEM photo ALT context mismatch "+locale)
    return markup


def apply(dist):
    dist=Path(dist)
    for image in [*map(lambda pair:pair[1],EDITORIAL_IMAGES.values()),OEM_NEW]:
        if not (dist/image.lstrip("/")).is_file():
            raise FileNotFoundError("Missing approved editorial media: "+image)
    count=0
    for lang in LOCALES:
        prefix="" if lang=="en" else lang+"/"
        href_prefix="/" if lang=="en" else "/"+lang+"/"
        general=dist/prefix/"applications/everyday-hydration/index.html"
        doc=general.read_text(encoding="utf-8")
        for collection,(old,new) in EDITORIAL_IMAGES.items():
            prefix_tag=('<a class="category" href="'+href_prefix+'collections/'+collection+'/">'
                        '<div class="category__photo"><img src="')
            doc,changed=replace_if_original(doc,prefix_tag,old,new,lang+" "+collection)
            count+=int(changed)
        general.write_text(doc,encoding="utf-8")

        oem=dist/prefix/"capabilities/oem-odm/index.html"
        doc=oem.read_text(encoding="utf-8")
        prefix_tag='<div class="whyv2-oem-steps__sample"><img src="'
        doc,changed=replace_if_original(doc,prefix_tag,OEM_OLD,OEM_NEW,lang+" oem-sampling")
        # A real plastic-bottle source photo replaces the unverified studio.
        import html
        import re
        pattern=r'(<div class="whyv2-oem-steps__sample"><img src="'+re.escape(OEM_NEW)+r'" alt=")[^"]*(")'
        if changed:
            doc,num=re.subn(pattern,lambda m:m.group(1)+html.escape(OEM_ALT[lang],quote=True)+m.group(2),doc,count=1)
            if num!=1:raise ValueError("OEM photo ALT context mismatch "+lang)
        oem.write_text(doc,encoding="utf-8")
        count+=int(changed)
    print("XUYI_EDITORIAL_IMAGES_REVIEWED",count,"new placements; owner-edited slots retained")
    return count

if __name__=="__main__":
    apply(ROOT/"dist")