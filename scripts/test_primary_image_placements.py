#!/usr/bin/env python3
"""Check About's Sports category and homepage use matching reviewed pictures."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
from fix_primary_image_placements import LOCALES,SQUARE,WIDE,ASSORTMENT,SMALL,OLD
dist=ROOT/"dist"
css=(dist/"assets/site.css").read_text(encoding="utf-8")
assert "max-height:300px;object-fit:contain" not in css
assert "aspect-ratio:16/9;object-fit:cover" in css
for lang in LOCALES:
    loc="" if lang=="en" else lang+"/"
    home=(dist/loc/"index.html").read_text(encoding="utf-8")
    assert home.count('<div class="kreat-intro__media"><img src="'+WIDE+'"')==1,lang
    assert home.count('src="'+SMALL+'"')>=1,("Navigation changed",lang)
    about=(dist/loc/"about/index.html").read_text(encoding="utf-8")
    assert about.count('<figure class="rs-photo"><img src="'+ASSORTMENT+'"')==1,lang
    href="/"+loc+"collections/sports-water-bottles/"
    assert about.count('<a href="'+href+'"><div><img src="'+SQUARE+'"')==1,lang
    assert OLD not in about,("Factory photo remains in About",lang)
    for page in (dist/loc/"products").glob("*/index.html"):
        markup=page.read_text(encoding="utf-8")
        main=markup.split('<main id="main-content">',1)[-1].split("</main>",1)[0]
        assert SQUARE not in main and WIDE not in main,("Named SKU image modified",str(page))
for asset in (SQUARE,WIDE):
    blob=(dist/asset.lstrip("/")).read_bytes()
    assert len(blob)>70000 and blob[:4]==b"RIFF" and blob[8:12]==b"WEBP",asset
print("XUYI_ABOUT_AND_HOMEPAGE_5_LANGUAGES_PASSED")