"""Blog image curation at the D1/CMS source-render boundary.

Preserve all later CMS-selected covers, even when their URLs differ from the
initial XUYI guide. Never walk, edit or depend upon generated dist pages.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parent
COVERS=json.loads((ROOT/'data/blog-cover-overrides.json').read_text(encoding='utf8'))
PHOTO_CORRECTIONS=json.loads((ROOT/'data/blog-photo-corrections-20261024.json').read_text(encoding='utf8'))
GUIDES=json.loads((ROOT/'data/blog-guides.json').read_text(encoding='utf8'))
ORIGINALS={p['slug']:(p['cover'] if p['cover'].startswith('/') else '/media/ppt/'+p['cover']) for p in GUIDES}
# Reviewed legacy covers plus five late-published D1-only buyer articles.
# Compare exact old image URLs; never overwrite later operator-selected paths.
SOURCE_REPAIRS={slug:(ORIGINALS[slug],new) for slug,new in COVERS.items() if slug in ORIGINALS}
SOURCE_REPAIRS.update({slug:(value['baseline'],value['photo']) for slug,value in PHOTO_CORRECTIONS.items()})
PHOTO_20261025=json.loads((ROOT/'data/blog-photo-corrections-20261025.json').read_text(encoding='utf8'))
SOURCE_REPAIRS.update({slug:(value['baseline'],value['photo']) for slug,value in PHOTO_20261025.items()})


def blog_cover_from_cms_source(markup: str, route: str, locale: str) -> str:
    """Only upgrade known original cover slots before rendering a locale.

    D1 article text, user covers and newly published/untranslated posts win.
    """
    if locale not in ('es','pt','ru','tr') or not route.startswith('/blog/'):
        return markup
    if route=='/blog/':
        for slug,(old,new) in SOURCE_REPAIRS.items():
            pattern=(r'(<a class="news-card__image" href="/blog/'+re.escape(slug)+
                     r'/"><img src=")'+re.escape(old)+r'(?=")')
            markup=re.sub(pattern,lambda m:m.group(1)+new,markup,count=1)
        return markup
    slug=route[len('/blog/'):].strip('/')
    if slug in SOURCE_REPAIRS:
        old,new=SOURCE_REPAIRS[slug]
        pattern=r'(<div class="blog-detail__cover"><img src=")'+re.escape(old)+r'(?=")'
        markup=re.sub(pattern,lambda m:m.group(1)+new,markup,count=1)
    for linked,(old,new) in SOURCE_REPAIRS.items():
        pattern=(r'(<article class="blog-related__item"><a href="/blog/'+re.escape(linked)+
                 r'/"><img src=")'+re.escape(old)+r'(?=")')
        markup=re.sub(pattern,lambda m:m.group(1)+new,markup)
    return markup

def article_social_image_from_cms_source(markup: str, route: str) -> str:
    """Use the final CMS-selected localized Blog hero for OG and BlogPosting.

    Translated article markup is owner-controlled. English fallback social
    metadata must not describe an image different from the actual D1 hero.
    This is a pre-write render operation, never a dist-file mutation.
    """
    import html
    if not re.fullmatch(r"/blog/[a-z0-9-]+/", route):
        return markup
    match = re.search(r'<div class="blog-detail__cover"><img\b[^>]*\bsrc="([^"]+)"', markup)
    if not match:
        return markup
    source = html.unescape(match.group(1))
    if not source.startswith(("/assets/", "/media/")) or ".." in source or any(c in source for c in "<>\\\"'"):
        return markup
    absolute = "https://xuyibottles.com" + source
    for attr in ('property="og:image"', 'name="twitter:image"'):
        pattern = r'(<meta ' + re.escape(attr) + r' content=")[^"]*(")'
        markup = re.sub(pattern, lambda m: m.group(1) + html.escape(absolute, quote=True) + m.group(2),
                        markup, count=1)

    def update_schema(found):
        try:
            data = json.loads(found.group(1))
        except (TypeError, ValueError):
            return found.group(0)
        nodes = data.get("@graph", []) if isinstance(data, dict) else []
        if isinstance(data, dict):
            nodes = list(nodes) + [data] if isinstance(nodes, list) else [data]
        changed = False
        for node in nodes:
            if isinstance(node, dict) and node.get("@type") == "BlogPosting":
                node["image"] = [absolute]
                changed = True
        if not changed:
            return found.group(0)
        return '<script type="application/ld+json">' + json.dumps(
            data, ensure_ascii=False, separators=(",", ":")).replace("<", r"\u003c") + "</script>"

    return re.sub(r'<script type="application/ld\+json">(.*?)</script>',
                  update_schema, markup, flags=re.S)
