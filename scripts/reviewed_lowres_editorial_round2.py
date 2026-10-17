#!/usr/bin/env python3
"""Scoped, reviewed generic illustrations only; never alter SKU or factory photos."""
import html
import re
from pathlib import Path
from reviewed_media_slot_guard import replace_if_original

ROOT=Path(__file__).resolve().parent.parent
LANGS=("en","es","pt","ru","tr")
APPLICATIONS=("everyday-hydration","gym-sports","kids-school",
              "outdoor-travel","promotional-gifts")
SHAKER_NEW="/assets/editorial/shaker-category-smoke.webp"
SHAKER_OLD="/media/ppt/slide-094.webp"
DESIGN_NEW="/assets/editorial/plastic-bottles-lid-styles.webp"
DESIGN_OLD="/media/ppt/slide-037.webp"
DESIGN_ALT={
 "en":"Assortment of reusable plastic water bottle shapes, handles and lids",
 "es":"Variedad de botellas de plástico reutilizables con asas y tapas",
 "pt":"Variedade de garrafas plásticas reutilizáveis com pegas e tampas",
 "ru":"Разнообразные пластиковые бутылки для воды с крышками и ручками",
 "tr":"Farklı kapak ve taşıma kulplarına sahip yeniden kullanılabilir plastik su şişeleri",
}

def once(text,pattern,fn,context):
    output,count=re.subn(pattern,fn,text,count=1)
    if count!=1:raise ValueError("Image context differs: "+context+" count="+str(count))
    return output

def apply(dist):
    dist=Path(dist)
    for source in (SHAKER_NEW,DESIGN_NEW):
        blob=(dist/source.lstrip("/")).read_bytes()
        if len(blob)<30000 or blob[:4]!=b"RIFF" or blob[8:12]!=b"WEBP":
            raise ValueError("Reviewed image invalid: "+source)
    modified=0
    for lang in LANGS:
        prefix="" if lang=="en" else lang+"/"
        href="/" if lang=="en" else "/"+lang+"/"
        for app in APPLICATIONS:
            file=dist/prefix/"applications"/app/"index.html"
            body=file.read_text(encoding="utf8")
            prefix_tag='<a class="category" href="'+href+'collections/plastic-shaker-bottles/"><div class="category__photo"><img src="'
            body,changed=replace_if_original(body,prefix_tag,SHAKER_OLD,SHAKER_NEW,lang+" applications/"+app)
            file.write_text(body,encoding="utf8")
            modified+=int(changed)
        file=dist/prefix/"manufacturing/index.html"
        body=file.read_text(encoding="utf8")
        prefix_tag='<div class="whyv2-factory-detail__image"><img src="'
        alt=html.escape(DESIGN_ALT[lang],quote=True)
        body,changed=replace_if_original(body,prefix_tag,DESIGN_OLD,DESIGN_NEW,lang+" manufacturing")
        if changed:
            pattern=(r'(<div class="whyv2-factory-detail__image"><img src="'
                     +re.escape(DESIGN_NEW)+r'" alt=")[^"]*(")')
            body,count=re.subn(pattern,lambda m:m.group(1)+alt+m.group(2),body,count=1)
            if count!=1:raise ValueError("Review ALT binding mismatch "+lang)
        file.write_text(body,encoding="utf8")
        modified+=int(changed)
    print("XUYI_ROUND2_REVIEWED_EDITORIAL_PLACEMENTS",modified,"new; CMS edits retained")
    return modified

if __name__=="__main__":
    apply(ROOT/"dist")
