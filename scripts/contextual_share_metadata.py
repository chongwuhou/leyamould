#!/usr/bin/env python3
"""Add accurate social previews using images that already illustrate each page.

Only 26 non-product-detail routes with an existing relevant image are eligible.
Contact/privacy have no page images and intentionally remain untouched.
"""
from pathlib import Path
from html import escape
import re

ROOT=Path(__file__).resolve().parent.parent
ORIGIN="https://xuyibottles.com"
LOCALES=("en","es","pt","ru","tr")

# Explicitly vetted against the English page's <main> illustrations and asset
# existence. These URL paths are the same on translated pages.
IMAGES={
 "/":"/assets/hero/sports-bottles-wide-20261013.webp",
 "/about/":"/assets/curated-hd/customizable-assortment.webp",
 "/applications/everyday-hydration/":"/media/ppt/slide-066.webp",
 "/applications/gym-sports/":"/media/ppt/slide-037.webp",
 "/applications/kids-school/":"/media/ppt/slide-030.webp",
 "/applications/outdoor-travel/":"/media/ppt/slide-055.webp",
 "/applications/promotional-gifts/":"/media/ppt/slide-061.webp",
 "/blog/":"/assets/blog/bottle-inspection-topics-20261013.webp",
 "/capabilities/":"/media/ppt/slide-020.webp",
 "/capabilities/oem-odm/":"/media/ppt/slide-059.webp",
 "/collections/kids-water-bottles/":"/assets/social/product-social-kids.webp",
 "/collections/large-capacity-water-jugs/":"/assets/lo/lo-001-01.webp",
 "/collections/plastic-shaker-bottles/":"/assets/sku-hd/slide-091-gpt-reviewed-20261013.webp",
 "/collections/sports-water-bottles/":"/assets/lo/lo-002-01.webp",
 "/faq/":"/media/ppt/slide-037.webp",
 "/features/carry-handle/":"/media/ppt/slide-059.webp",
 "/features/flip-top/":"/media/ppt/slide-037.webp",
 "/features/gradient-colors/":"/media/ppt/slide-060.webp",
 "/features/large-capacity/":"/media/ppt/slide-055.webp",
 "/features/straw-lid/":"/media/ppt/slide-066.webp",
 "/manufacturing/":"/media/group/factory-bottle-packing.webp",
 "/products/":"/assets/lo/lo-001-01.webp",
 "/quality-control/":"/media/group/qa-color-box.webp",
 "/request-sample/":"/media/ppt/slide-059.webp",
 "/shipping-logistics/":"/media/group/factory-shipment.webp",
 "/why-us/":"/media/ppt/slide-037.webp"
}

def apply_to_document(document,route,locale,source_root=ROOT):
    """Render a reviewed page illustration into HTML before the page is written."""
    base=str(route or "/")
    prefix="/"+locale
    if locale!="en" and base.startswith(prefix+"/"):
        base=base[len(prefix):]
    source_image=IMAGES.get(base)
    if not source_image:
        return document,"not_applicable"
    if locale not in LOCALES:
        return document,"not_applicable"
    if not source_image.startswith(("/assets/","/media/")) or ".." in source_image:
        raise ValueError("Bad image source "+source_image)
    if source_image.startswith("/assets/") and not (Path(source_root)/source_image.lstrip("/")).is_file():
        raise FileNotFoundError("Reviewed image is absent from source "+source_image)
    head,separator,body=document.partition("</head>")
    if separator!="</head>":
        raise ValueError("Malformed head for "+base)
    if re.search(r'<meta\s+property="og:image"',head):
        return document,"owner"
    main=document.split("<main",1)[-1].split("</main>",1)[0]
    if source_image not in re.findall(r'<img\b[^>]*\bsrc="([^"]+)"',main,re.S):
        return document,"changed"
    if re.search(r'<meta\s+name="twitter:image"',head):
        return document,"owner"
    url=ORIGIN+source_image
    tags='<meta property="og:image" content="'+escape(url,quote=True)+'">'
    if not re.search(r'<meta\s+name="twitter:card"',head):
        tags+='<meta name="twitter:card" content="summary_large_image">'
    tags+='<meta name="twitter:image" content="'+escape(url,quote=True)+'">'
    return head+tags+separator+body,"generated"

def apply(dist):
    dist=Path(dist)
    if len(IMAGES)!=26:raise ValueError("Only 26 reviewed illustrated page types permitted")
    count=0
    owner_previews=0
    changed_page_illustrations=0
    for route in IMAGES:
        for locale in LOCALES:
            prefix="" if locale=="en" else locale+"/"
            localized=route if locale=="en" else "/"+locale+route
            path=dist/prefix/route.strip("/")/"index.html"
            if not path.is_file():raise FileNotFoundError(path)
            content=path.read_text(encoding="utf8")
            updated,status=apply_to_document(content,localized,locale,dist)
            if status=="generated":
                path.write_text(updated,encoding="utf8")
                count+=1
            elif status=="owner":
                owner_previews+=1
            elif status=="changed":
                changed_page_illustrations+=1
    if count+owner_previews+changed_page_illustrations!=130:
        raise ValueError("Unexpected illustrated route coverage")
    print("XUYI_CONTEXTUAL_SOCIAL_PREVIEWS",count,"generated,",
          owner_previews,"owner-managed,",changed_page_illustrations,"changed media; privacy/contact untouched")
    return count
if __name__=="__main__":
    apply(ROOT/"dist")