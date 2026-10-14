#!/usr/bin/env python3
"""All published XUYI Blog cards must be unique, even as the CMS adds posts."""
from collections import Counter
from pathlib import Path
import json
import re
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
from repair_localized_blog_thumbnails import ORIGINALS,OVERRIDES
SHAKER_MANIFEST=json.loads((ROOT/"data/gpt-reviewed-shaker-hd-20261013.json").read_text(encoding="utf8"))
REVIEWED_SOURCE_IMAGES={item["old"]:item["new"] for item in SHAKER_MANIFEST["approved"]}

DIST=ROOT/"dist"
LANGS=("en","es","pt","ru","tr")
assert len(ORIGINALS)>=16,len(ORIGINALS)
assert len(OVERRIDES)>=8,len(OVERRIDES)
initial=Counter(ORIGINALS.values())
assert sum(n-1 for n in initial.values())>=8
assert all(initial[ORIGINALS[slug]]>=2 for slug in OVERRIDES)
assert len(set(OVERRIDES.values()))==len(OVERRIDES.values())
post_slugs=set(ORIGINALS)
for lang in LANGS:
    prefix="" if lang=="en" else lang+"/"
    path=DIST/prefix/"blog/index.html"
    body=path.read_text(encoding="utf8")
    pattern=(r'<a class="news-card__image" href="/'+re.escape(prefix)+
             r'blog/([^/]+)/"><img src="([^"]+)"')
    cards=re.findall(pattern,body)
    assert len(cards)>=16,(lang,len(cards))
    found={slug:img for slug,img in cards}
    assert len(found)==len(cards) and post_slugs.issubset(found),lang
    assert len(set(found.values()))==len(found),("Duplicate blog thumbnail",lang,found)
    for slug,path_new in found.items():
        # The owner may replace a specific article cover through CMS. What
        # matters is that listing, actual article hero and social metadata
        # agree; do not require an old editorial override URL forever.
        expected=path_new
        article=(DIST/prefix/"blog"/slug/"index.html").read_text(encoding="utf8")
        assert '<meta property="og:image" content="https://xuyibottles.com'+expected+'"' in article,(lang,slug,"OG")
        assert '"image":["https://xuyibottles.com'+expected+'"]' in article,(lang,slug,"JSON-LD")
        assert ('<div class="blog-detail__cover"><img src="'+expected+'"') in article,(lang,slug,"article hero")
        if expected.startswith("/assets/"):
            f=DIST/expected.lstrip("/")
            assert f.is_file(),("Blog image missing",f)
            data=f.read_bytes()
            assert data[:4]==b"RIFF" and data[8:12]==b"WEBP" and len(data)>30000,f
    for slug in post_slugs:
        article=(DIST/prefix/"blog"/slug/"index.html").read_text(encoding="utf8")
        related=(r'<article class="blog-related__item"><a href="/'+
                 re.escape(prefix)+r'blog/([^/]+)/"><img src="([^"]+)"')
        for linked,img in re.findall(related,article):
            assert linked in found,(lang,slug,linked)
            assert img==found[linked],(lang,slug,linked,img)
print("XUYI_BLOG_UNIQUE_THUMBNAILS_FIVE_LANGUAGES_PASSED; CMS covers and social metadata consistent")