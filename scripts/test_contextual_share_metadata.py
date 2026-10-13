#!/usr/bin/env python3
"""Social image source must already belong to the page, with five-locale parity."""
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
from contextual_share_metadata import IMAGES,LOCALES,ORIGIN

dist=ROOT/"dist"
assert len(IMAGES)==26
total=0
for route,img in IMAGES.items():
    for lang in LOCALES:
        prefix="" if lang=="en" else lang+"/"
        path=dist/prefix/route.strip("/")/"index.html"
        source=path.read_text(encoding="utf8")
        head=source.split("</head>",1)[0]
        main=source.split("<main",1)[-1].split("</main>",1)[0]
        main_images=re.findall(r'<img\b[^>]*\bsrc="([^"]+)"',main,re.S)
        social_og=re.findall(r'<meta property="og:image" content="([^"]+)"',head)
        social_twitter=re.findall(r'<meta name="twitter:image" content="([^"]+)"',head)
        if img in main_images and not social_og:
            raise AssertionError((lang,route,"Missing eligible social preview"))
        if social_og==[ORIGIN+img]:
            assert social_twitter==[ORIGIN+img],(lang,route)
            assert 'name="twitter:card" content="summary_large_image"' in head,(lang,route)
        elif social_og:
            assert len(social_og)==1 and social_og[0].startswith(ORIGIN+"/"),(lang,route,"unknown owner asset")
        total+=1
for route in ("contact","privacy-policy"):
    for lang in LOCALES:
        prefix="" if lang=="en" else lang+"/"
        head=(dist/prefix/route/"index.html").read_text(encoding="utf8").split("</head>",1)[0]
        assert 'property="og:image"' not in head,(lang,route)
assert total==130
print("XUYI_SOCIAL_PREVIEW_130_PAGES_FIVE_LOCALES_PASSED")