#!/usr/bin/env python3
"""Reviewed contextual social previews are emitted by page source renderers."""
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"scripts"))
from contextual_share_metadata import IMAGES,LOCALES,ORIGIN,apply_to_document
from product_share_source import CATEGORY_PREVIEWS

DIST=ROOT/"dist"
checked=generated=owner=changed=0
for route,source_image in IMAGES.items():
    for locale in LOCALES:
        prefix="" if locale=="en" else locale+"/"
        localized=route if locale=="en" else "/"+locale+route
        page=DIST/prefix/route.strip("/")/"index.html"
        assert page.is_file(),(locale,route,"missing rendered page")
        markup=page.read_text(encoding="utf8")
        updated,status=apply_to_document(markup,localized,locale,DIST)
        assert updated==markup,(locale,route,"social preview renderer is not idempotent")
        head=markup.split("</head>",1)[0]
        main=markup.split("<main",1)[-1].split("</main>",1)[0]
        visible_images=re.findall(r'<img\b[^>]*\bsrc="([^"]+)"',main,re.S)
        og_urls=re.findall(r'<meta\s+property="og:image"\s+content="([^"]+)"',head)
        if source_image in visible_images:
            assert og_urls,(locale,route,"visible reviewed image lacks OG preview")
        if ORIGIN+source_image in og_urls:
            # A small, explicitly reviewed set of category social cards is
            # designed for sharing and need not be repeated in the visible page.
            if source_image in CATEGORY_PREVIEWS.values():
                assert (DIST/source_image.lstrip("/")).is_file(),(locale,route,"missing approved category share card")
            else:
                assert source_image in visible_images,(locale,route,"stale OG image no longer visible on page")
            if source_image.startswith("/assets/"):
                assert re.search(r'<meta\s+property="og:image:width"\s+content="\d+"',head)
                assert re.search(r'<meta\s+property="og:image:height"\s+content="\d+"',head)
        assert len(re.findall(r'<meta\s+property="og:image"',head))<=1,(locale,route,"duplicate OG image")
        if status=="owner":owner+=1
        elif status=="changed":changed+=1
        elif status=="generated":generated+=1
        checked+=1
assert checked==len(IMAGES)*len(LOCALES)
print("XUYI_SOURCE_SOCIAL_PREVIEWS_PASSED",checked,"routes; current",owner,"owner-managed,",changed,"changed illustrations,",generated,"pending source inserts")