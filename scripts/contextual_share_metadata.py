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
 "/collections/kids-water-bottles/":"/media/excel/row-008.webp",
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

def apply(dist):
    dist=Path(dist)
    if len(IMAGES)!=26:raise ValueError("Only 26 reviewed illustrated page types permitted")
    count=0
    owner_previews=0
    changed_page_illustrations=0
    for route,source_image in IMAGES.items():
        if not source_image.startswith(("/assets/","/media/")) or ".." in source_image:
            raise ValueError("Bad image source "+source_image)
        if source_image.startswith("/assets/") and not (dist/source_image[1:]).is_file():
            raise FileNotFoundError("Image is absent from release "+source_image)
        url=ORIGIN+source_image
        for locale in LOCALES:
            prefix="" if locale=="en" else locale+"/"
            path=dist/prefix/route.strip("/")/"index.html"
            if not path.is_file():raise FileNotFoundError(path)
            content=path.read_text(encoding="utf8")
            head,separator,body=content.partition("</head>")
            main=content.split("<main",1)[-1].split("</main>",1)[0]
            if separator!="</head>":
                raise ValueError("Malformed head in "+str(path))
            # Subsequent D1 page edits are authoritative; do not force back
            # previously selected source images or overwrite CMS social tags.
            if re.search(r'<meta\s+property="og:image"',head):
                owner_previews+=1
                continue
            if source_image not in re.findall(r'<img\b[^>]*\bsrc="([^"]+)"',main,re.S):
                changed_page_illustrations+=1
                continue
            if re.search(r'<meta\s+name="twitter:image"',head):
                owner_previews+=1
                continue
            tags='<meta property="og:image" content="'+escape(url,quote=True)+'">'
            tags+='<meta name="twitter:card" content="summary_large_image">'
            tags+='<meta name="twitter:image" content="'+escape(url,quote=True)+'">'
            path.write_text(head+tags+separator+body,encoding="utf8")
            count+=1
    if count+owner_previews+changed_page_illustrations!=130:
        raise ValueError("Unexpected illustrated route coverage")
    print("XUYI_CONTEXTUAL_SOCIAL_PREVIEWS",count,"generated,",
          owner_previews,"owner-managed,",changed_page_illustrations,"changed media; privacy/contact untouched")
    return count

if __name__=="__main__":
    apply(ROOT/"dist")