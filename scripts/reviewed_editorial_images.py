#!/usr/bin/env python3
"""Exact, scoped replacements for reviewed generic plastic drinkware visuals.

Does not touch identified SKU photographs, R2 originals or factory evidence.
The pages retain normal category/product language and existing visible copy.
"""
from pathlib import Path

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

def replace_once(markup,old,new,context):
    count=markup.count(old)
    if count!=1:raise ValueError("Unexpected target in "+context+": "+str(count))
    return markup.replace(old,new,1)

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
            anchor=('<a class="category" href="'+href_prefix+'collections/'+collection+'/">'
                    '<div class="category__photo"><img src="'+old+'"')
            replacement=anchor.replace('src="'+old+'"','src="'+new+'"')
            doc=replace_once(doc,anchor,replacement,lang+" "+collection)
            count+=1
        general.write_text(doc,encoding="utf-8")

        oem=dist/prefix/"capabilities/oem-odm/index.html"
        doc=oem.read_text(encoding="utf-8")
        anchor='<div class="whyv2-oem-steps__sample"><img src="'+OEM_OLD+'"'
        doc=replace_once(doc,anchor,anchor.replace(OEM_OLD,OEM_NEW),lang+" oem-sampling")
        # A real plastic-bottle source photo replaces the unverified studio.
        import html
        import re
        pattern=r'(<div class="whyv2-oem-steps__sample"><img src="'+re.escape(OEM_NEW)+r'" alt=")[^"]*(")'
        doc,num=re.subn(pattern,lambda m:m.group(1)+html.escape(OEM_ALT[lang],quote=True)+m.group(2),doc,count=1)
        if num!=1:raise ValueError("OEM photo ALT context mismatch "+lang)
        oem.write_text(doc,encoding="utf-8")
        count+=1
    print("XUYI_EDITORIAL_IMAGES_REVIEWED",count,"exact page-image placements")
    return count

if __name__=="__main__":
    apply(ROOT/"dist")