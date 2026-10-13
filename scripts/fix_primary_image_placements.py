#!/usr/bin/env python3
"""Target reviewed plastic sports photos to only matching generic page slots."""
import re
from pathlib import Path

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
        pat=r'(<div class="kreat-intro__media"><img src=")'+re.escape(SMALL)+r'(")'
        markup=once(markup,pat,lambda m:m.group(1)+WIDE+m.group(2),lang+" home")
        home.write_text(markup,encoding="utf-8")
        count+=1
        about=dist/loc/"about/index.html"
        markup=about.read_text(encoding="utf-8")
        pat=r'(<figure class="rs-photo"><img src=")'+re.escape(OLD)+r'(")'
        markup=once(markup,pat,lambda m:m.group(1)+ASSORTMENT+m.group(2),lang+" about overview")
        count+=1
        href="/"+loc+"collections/sports-water-bottles/"
        pat=r'(<a href="'+re.escape(href)+r'"><div><img src=")'+re.escape(OLD)+r'" alt="[^"]*"'
        alt=html.escape(SPORTS_ALT[lang],quote=True)
        markup=once(markup,pat,lambda m:m.group(1)+SQUARE+'" alt="'+alt+'"',lang+" about sports")
        about.write_text(markup,encoding="utf-8")
        count+=1
    print("XUYI_PRIMARY_VISUAL_PLACEMENTS",count)
    return count

if __name__=="__main__":apply(ROOT/"dist")