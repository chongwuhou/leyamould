#!/usr/bin/env python3
"""Real release-page replay: preserve CMS image edits and avoid double swaps."""
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
from reviewed_media_slot_guard import replace_if_original
from reviewed_editorial_images import apply as editorial,EDITORIAL_IMAGES,OEM_NEW,OEM_OLD
from reviewed_lowres_editorial_round2 import apply as round2,SHAKER_OLD,SHAKER_NEW,DESIGN_OLD,DESIGN_NEW
from fix_primary_image_placements import apply as primary,WIDE,SMALL,ASSORTMENT,OLD,SQUARE

DIST=ROOT/"dist"
OWNER="/assets/curated-hd/outdoor-lifestyle.webp"

sample='<figure class="rs-photo"><img src="/media/ppt/slide-049.webp"><figure class="rs-photo"><img src="/assets/test-custom.webp">'
changed,done=replace_if_original(sample,'<figure class="rs-photo"><img src="',OLD,ASSORTMENT,"test")
assert done and ASSORTMENT in changed and 'src="/assets/test-custom.webp"' in changed
same,done=replace_if_original(changed,'<figure class="rs-photo"><img src="',OLD,ASSORTMENT,"repeat")
assert not done and same==changed
edited,done=replace_if_original(sample.replace(OLD,OWNER),'<figure class="rs-photo"><img src="',OLD,ASSORTMENT,"CMS")
assert not done and edited==sample.replace(OLD,OWNER)

with TemporaryDirectory(prefix="xuyi-cms-images-") as tmp:
    target=Path(tmp)
    routes=[
        "applications/everyday-hydration/index.html",
        "capabilities/oem-odm/index.html",
        "applications/gym-sports/index.html","applications/kids-school/index.html",
        "applications/outdoor-travel/index.html","applications/promotional-gifts/index.html",
        "manufacturing/index.html","index.html","about/index.html"
    ]
    for locale in ("","es/","pt/","ru/","tr/"):
        for route in routes:
            src=DIST/locale/route
            dest=target/locale/route
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(src,dest)
    sources=[*map(lambda pair:pair[1],EDITORIAL_IMAGES.values()),OEM_NEW,
             SHAKER_NEW,DESIGN_NEW,WIDE,SQUARE,ASSORTMENT]
    for img in sources:
        source=DIST/img.lstrip("/")
        dest=target/img.lstrip("/")
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,dest)
    # Three distinct source changes: a human-edited category photo, an
    # ordinary old source requiring repair, and an already-upgraded slot.
    en=target/"applications/everyday-hydration/index.html"
    html=en.read_text(encoding="utf8")
    brand_photo=EDITORIAL_IMAGES["sports-water-bottles"][1]
    assert html.count(brand_photo)>0
    en.write_text(html.replace(brand_photo,OWNER,1),encoding="utf8")
    pt=target/"pt/applications/everyday-hydration/index.html"
    html=pt.read_text(encoding="utf8")
    old,new=EDITORIAL_IMAGES["kids-water-bottles"]
    assert new in html
    pt.write_text(html.replace(new,old,1),encoding="utf8")
    manufacturing=target/"manufacturing/index.html"
    html=manufacturing.read_text(encoding="utf8")
    assert DESIGN_NEW in html
    manufacturing.write_text(html.replace(DESIGN_NEW,OWNER,1),encoding="utf8")
    home=target/"es/index.html"
    html=home.read_text(encoding="utf8")
    assert WIDE in html
    home.write_text(html.replace(WIDE,OWNER,1),encoding="utf8")
    before={}
    for loc in ("","es/","pt/","ru/","tr/"):
        for route in routes:
            path=target/loc/route
            before[path]=path.read_text(encoding="utf8")
    assert editorial(target)==1
    assert round2(target)==0
    assert primary(target)==0
    assert OWNER in en.read_text(encoding="utf8")
    assert OWNER in manufacturing.read_text(encoding="utf8")
    assert OWNER in home.read_text(encoding="utf8")
    assert new in pt.read_text(encoding="utf8") and old not in pt.read_text(encoding="utf8")
    after={path:path.read_text(encoding="utf8") for path in before}
    assert editorial(target)==0 and round2(target)==0 and primary(target)==0
    assert all(path.read_text(encoding="utf8")==content for path,content in after.items())

print("XUYI_IMAGE_CMS_OVERRIDE_PRESERVATION_3_TRANSFORMS_FIVE_LOCALES_REPEAT_BUILD_PASSED")