#!/usr/bin/env python3
"""All 16 XUYI Blog cards must be unique in each language; only duplicate slots change."""
from collections import Counter
from pathlib import Path
import json
import re
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
from repair_localized_blog_thumbnails import ORIGINALS,OVERRIDES

DIST=ROOT/"dist"
LANGS=("en","es","pt","ru","tr")
assert len(ORIGINALS)==16,len(ORIGINALS)
assert len(OVERRIDES)==8,len(OVERRIDES)
initial=Counter(ORIGINALS.values())
assert sum(n-1 for n in initial.values())==8
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
    assert len(cards)==16,(lang,len(cards))
    found={slug:img for slug,img in cards}
    assert len(found)==16 and set(found)==post_slugs,lang
    assert len(set(found.values()))==16,("Duplicate blog thumbnail",lang,found)
    for slug,path_new in found.items():
        expected=OVERRIDES.get(slug,ORIGINALS[slug])
        assert path_new==expected,("Unexpectedly changed an originally unique image",lang,slug)
        article=(DIST/prefix/"blog"/slug/"index.html").read_text(encoding="utf8")
        assert '<meta property="og:image" content="https://xuyibottles.com'+expected+'"' in article,(lang,slug,"OG")
        assert '"image":["https://xuyibottles.com'+expected+'"]' in article,(lang,slug,"JSON-LD")
        assert expected in article,(lang,slug,"article")
        if expected.startswith("/assets/"):
            f=DIST/expected.lstrip("/")
            assert f.is_file(),("Blog image missing",f)
            data=f.read_bytes()
            assert data[:4]==b"RIFF" and data[8:12]==b"WEBP" and len(data)>30000,f
print("XUYI_BLOG_UNIQUE_16_THUMBNAILS_FIVE_LANGUAGES_PASSED; original unique images preserved")