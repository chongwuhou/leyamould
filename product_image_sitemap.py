"""Source-owned product image extension for the existing XUYI XML sitemap.

Use the exact model photo selected by catalog + D1 product data (English),
or by an owner-approved translated D1 body (localized pages).
Never rename R2 objects, invent a matching SKU photo, or add a second sitemap.
"""
from html.parser import HTMLParser
from html import escape
from urllib.parse import urlsplit
import re
import json
from functools import lru_cache
from pathlib import Path

@lru_cache(maxsize=1)
def approved_shaker_image_aliases():
    """Existing reviewed source manifest used by the legacy renderer.

    This is only a read of a versioned *approved* photo mapping. No path
    renaming, R2 changes, or extra generated image names.
    """
    path=Path(__file__).parent/"data/gpt-reviewed-shaker-hd-20261013.json"
    data=json.loads(path.read_text(encoding="utf8"))
    if data.get("site")!="xuyi-drinkware-site" or data.get("schemaVersion")!=1:
        raise ValueError("Unrecognized reviewed image source")
    return {v["old"]:v["new"] for v in data["approved"]}


IMAGE_NAMESPACE="http://www.google.com/schemas/sitemap-image/1.1"
IMAGE_EXTENSION=r' xmlns:image="'+IMAGE_NAMESPACE+'"'
VALID_MEDIA=re.compile(r"^/(?:media|assets)/[a-zA-Z0-9_./-]+\.(?:webp|png|jpe?g|avif)$",re.I)

class _ProductMainPhoto(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.found=None
    def handle_starttag(self,tag,attrs):
        if tag!="img" or self.found is not None:return
        attributes=dict(attrs)
        if attributes.get("id")=="main-photo":self.found=attributes.get("src")

def image_path(value,origin="https://xuyibottles.com"):
    """Public path only. Same-origin URLs prevent CDN host churn."""
    if not isinstance(value,str) or not value or value!=value.strip():return None
    parts=urlsplit(value)
    base=urlsplit(origin)
    if parts.scheme or parts.netloc:
        if parts.scheme!=base.scheme or parts.netloc!=base.netloc:return None
    if parts.query or parts.fragment:return None
    path=parts.path
    if not VALID_MEDIA.fullmatch(path) or "/../" in path or "/./" in path or "//" in path:return None
    # The normal release maps six previously approved shaker originals to
    # stable published assets. Use that *same* reviewed mapping at source time
    # so sitemap URLs exactly equal the actual page main image.
    return approved_shaker_image_aliases().get(path,path)

def source_main_photo(row,translated_body=None,origin="https://xuyibottles.com"):
    """A D1 translated body wins. If the editor removes a photo, omit XML entry."""
    if translated_body is not None:
        parser=_ProductMainPhoto()
        parser.feed(translated_body)
        return image_path(parser.found,origin)
    images=row.get("images") or []
    return image_path(images[0],origin) if images else None

def image_for_product_route(route,series,localized_body=None,origin="https://xuyibottles.com"):
    """Tolerates new verified models, locale pages, and CMS image replacements."""
    if not re.fullmatch(r"/products/[a-zA-Z0-9_-]+/",route):return None
    slug=route.split("/")[2]
    row=next((item for item in series.values() if item.get("slug")==slug),None)
    if row is None:return None
    return source_main_photo(row,localized_body,origin)

def xml_image_for_product(route,series,localized_body=None,origin="https://xuyibottles.com"):
    path=image_for_product_route(route,series,localized_body,origin)
    if path is None:return ""
    # The only required Google image-sitemap element: image:loc. No deprecated
    # image:title, image:caption, image:license or guessed product metadata.
    return "<image:image><image:loc>"+escape(origin+path,quote=True)+"</image:loc></image:image>"