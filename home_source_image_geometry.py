"""Source-time dimension hints for homepage imagery with verified media provenance.

Adds intrinsic width/height ONLY for source-reviewed assets or Excel originals.
For five R2 images without trustworthy intrinsic metadata, reserve a CSS
layout aspect ratio appropriate to their existing editorial thumbnail slot;
never assert an unverified pixel dimension. CMS-selected image URL survives.
"""
import json,re
from html import unescape
from pathlib import Path
ROOT=Path(__file__).resolve().parent
KNOWN=json.loads((ROOT/"data/home-image-intrinsic-sizes.json").read_text(encoding="utf8"))["dimensions"]
APPROVED={item["old"]:item["new"] for item in json.loads((ROOT/"data/gpt-reviewed-shaker-hd-20261013.json").read_text(encoding="utf8"))["approved"]}
IMAGE_TAG=re.compile(r"<img\b[^>]*>",re.I)
SRC=re.compile(r'\bsrc="([^"]+)"',re.I)
def source_image_geometry(body,route,locale):
    if route!="/":return body
    def dimensions(m):
        tag=m.group(0)
        if re.search(r'\b(width|height)\s*=',tag,re.I):return tag
        src=SRC.search(tag)
        if src is None:return tag
        path=unescape(src.group(1))
        # Reserve reviewed final HQ geometry for approved PPT image aliases.
        known=KNOWN.get(path) or KNOWN.get(APPROVED.get(path))
        if known:
            w,h=known
            if not (isinstance(w,int) and isinstance(h,int) and w>0 and h>0):raise ValueError("Invalid reviewed pixel geometry "+path)
            addition=f' width="{w}" height="{h}"'
        elif path.startswith("/media/"):
            # Explicit layout-only reservation for remotely hosted images.
            # Not a claim that these are their physical bitmap dimensions.
            if re.search(r'\bstyle\s*=',tag,re.I):return tag
            addition=' style="aspect-ratio:4/3"'
        else:
            return tag  # Owner-managed new URL: do not infer its dimensions.
        return tag[:-1]+addition+">"
    return IMAGE_TAG.sub(dimensions,body)
