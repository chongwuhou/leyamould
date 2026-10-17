#!/usr/bin/env python3
"""A CMS-authored internal link survives both source curation and a rerun."""
from pathlib import Path
from tempfile import TemporaryDirectory
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
from buyer_journey_internal_links import apply as add_buyer_links,PATHWAYS,LOCALES
from curated_buyer_seo_round2 import apply as add_blog_links,BLOG_LINKS,DESCRIPTIONS

def path_for(root,lang,route):
    prefix="" if lang=="en" else lang+"/"
    return root/prefix/route/"index.html"

def write(root,lang,route,body=""):
    file=path_for(root,lang,route)
    file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(
        '<html><head><meta name="description" content="Owner source summary">'
        '<meta property="og:description" content="Owner source summary">'
        '</head><body><main><p>CMS-authored content stays intact.</p>'
        +body+'</main></body></html>',encoding="utf8")

with TemporaryDirectory(prefix="xuyi-buyer-owner-") as tmp:
    dist=Path(tmp)
    for lang in LOCALES:
        for route in set(PATHWAYS)|{dest for group in PATHWAYS.values() for dest in group}:
            write(dist,lang,route)
        owner=path_for(dist,lang,"collections/kids-water-bottles")
        original=owner.read_text(encoding="utf8")
        href="/"+("" if lang=="en" else lang+"/")+"features/straw-lid/"
        owner.write_text(original.replace("</main>",'<a href="'+href+'">Editor-approved straw options</a></main>'),encoding="utf8")
    assert add_buyer_links(dist)==70
    for lang in LOCALES:
        owner=path_for(dist,lang,"collections/kids-water-bottles")
        content=owner.read_text(encoding="utf8")
        href="/"+("" if lang=="en" else lang+"/")+"features/straw-lid/"
        assert content.count('href="'+href+'"')==1 and "Editor-approved straw options" in content
    assert add_buyer_links(dist)==0

with TemporaryDirectory(prefix="xuyi-blog-owner-") as tmp:
    dist=Path(tmp)
    routes=set(DESCRIPTIONS)|{"blog/"+slug for slug in BLOG_LINKS}|set(BLOG_LINKS.values())
    chosen=next(iter(BLOG_LINKS))
    for lang in LOCALES:
        for route in routes:write(dist,lang,route)
        target=BLOG_LINKS[chosen]
        href="/"+("" if lang=="en" else lang+"/")+target+"/"
        owner=path_for(dist,lang,"blog/"+chosen)
        owner.write_text(owner.read_text(encoding="utf8").replace(
            "</main>",'<a href="'+href+'">CMS-approved guide link</a></main>'),encoding="utf8")
    assert add_blog_links(dist)[1]==40
    for lang in LOCALES:
        owner=path_for(dist,lang,"blog/"+chosen)
        href="/"+("" if lang=="en" else lang+"/")+BLOG_LINKS[chosen]+"/"
        content=owner.read_text(encoding="utf8")
        assert content.count('href="'+href+'"')==1 and "CMS-approved guide link" in content
    assert add_blog_links(dist)[1]==0

print("XUYI_OWNER_AUTHORED_INTERNAL_LINKS_PRESERVED_FIVE_LOCALES_AND_REPEAT_BUILD_PASSED")
