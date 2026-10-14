#!/usr/bin/env python3
"""Target reviewed plastic sports photos to only matching generic page slots."""
import re
from pathlib import Path
from reviewed_media_slot_guard import replace_if_original

ROOT=Path(__file__).resolve().parent.parent
LOCALES=("en","es","pt","ru","tr")
OLD="/media/ppt/slide-049.webp"
SQUARE="/assets/editorial/sports-bottles-category-20261013.webp"
WIDE="/assets/hero/sports-bottles-wide-20261013.webp"
ASSORTMENT="/assets/curated-hd/customizable-assortment.webp"
SMALL="/assets/curated-hd/outdoor-lifestyle.webp"
SPORTS_ALT={
 "en":"Colorful plastic sports water bottles with flip-top lids",
 "es":"Botellas deportivas de plástico de colores con tapas abatibles",
 "pt":"Garrafas esportivas de plástico coloridas com tampas articuladas",
 "ru":"Цветные пластиковые спортивные бутылки с откидными крышками",
 "tr":"Açılır kapaklı renkli plastik sporcu su şişeleri",
}

def once(markup,pattern,replace,context):
    newer,count=re.subn(pattern,replace,markup,count=1)
    if count!=1:raise ValueError("Image placement mismatch "+context+": "+str(count))
    return newer

def apply(dist):
    import html
    dist=Path(dist)
    for path in (SQUARE,WIDE,ASSORTMENT):
        if not (dist/path.lstrip("/")).is_file():raise FileNotFoundError(path)
    count=0
    for lang in LOCALES:
        loc="" if lang=="en" else lang+"/"
        home=dist/loc/"index.html"
        markup=home.read_text(encoding="utf-8")
        markup,changed=replace_if_original(markup,'<div class="kreat-intro__media"><img src="',SMALL,WIDE,lang+" home")
        home.write_text(markup,encoding="utf-8")
        count+=int(changed)
        about=dist/loc/"about/index.html"
        markup=about.read_text(encoding="utf-8")
        markup,changed=replace_if_original(markup,'<figure class="rs-photo"><img src="',OLD,ASSORTMENT,lang+" about overview")
        count+=int(changed)
        href="/"+loc+"collections/sports-water-bottles/"
        prefix_tag='<a href="'+href+'"><div><img src="'
        alt=html.escape(SPORTS_ALT[lang],quote=True)
        markup,changed=replace_if_original(markup,prefix_tag,OLD,SQUARE,lang+" about sports")
        if changed:
            pat=r'(<a href="'+re.escape(href)+r'"><div><img src="'+re.escape(SQUARE)+r'" alt=")[^"]*(")'
            markup,n=re.subn(pat,lambda m:m.group(1)+alt+m.group(2),markup,count=1)
            if n!=1:raise ValueError("Reviewed sports ALT binding mismatch "+lang)
        about.write_text(markup,encoding="utf-8")
        count+=int(changed)
    print("XUYI_PRIMARY_VISUAL_PLACEMENTS",count,"new, CMS image choices retained")
    return count

if __name__=="__main__":apply(ROOT/"dist")