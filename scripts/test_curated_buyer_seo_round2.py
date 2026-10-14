#!/usr/bin/env python3
"""Only the 20 curated meta descriptions and 45 reviewed Blog links change."""
from pathlib import Path
import html
import json
import re
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
from curated_buyer_seo_round2 import DESCRIPTIONS,BLOG_LINKS,LOCALES,WORDS
from cms_seo_curation_guard import may_curate,current_field
dist=ROOT/"dist"
assert len(DESCRIPTIONS)==3 and len(BLOG_LINKS)==9
meta_count=links_count=0
for lang in LOCALES:
    prefix="" if lang=="en" else lang+"/"
    for route,translations in DESCRIPTIONS.items():
        assert set(translations)==set(LOCALES),route
        body=(dist/prefix/route/"index.html").read_text(encoding="utf8")
        head=body.split("</head>",1)[0]
        desc=(translations[lang] if may_curate(lang,"/"+route+"/","description")
              else current_field(lang,"/"+route+"/","description"))
        for pattern in (r'<meta name="description" content="([^"]+)"',
                        r'<meta property="og:description" content="([^"]+)"'):
            values=[html.unescape(v) for v in re.findall(pattern,head)]
            assert values==[desc],(lang,route,pattern,values)
        assert "<title>" in head
        # Ensure the Google canonical & cross-language declarations remain.
        assert 'rel="canonical"' in head and 'hreflang="' in head,(lang,route)
        for raw in re.findall(r'<script type="application/ld\+json">([\s\S]*?)</script>',head):
            data=json.loads(raw)
            for node in data.get("@graph",[data]):
                if node.get("@type")=="WebPage" and "description" in node:
                    assert node["description"]==desc,(lang,route)
        meta_count+=1
    for slug,target in BLOG_LINKS.items():
        page=(dist/prefix/"blog"/slug/"index.html").read_text(encoding="utf8")
        main=page.split("<main",1)[-1].split("</main>",1)[0]
        href="/"+prefix+target+"/"
        assert main.count('href="'+href+'"')==1,(lang,slug,target)
        if 'class="seo-next-buyer"' in main:
            assert main.count('class="seo-next-buyer"')==1,(lang,slug)
            section=main.split('class="seo-next-buyer"',1)[1].split("</section>",1)[0]
            assert html.escape(WORDS[lang][0]) in section,(lang,slug)
        assert (dist/prefix/target/"index.html").is_file()
        links_count+=1
assert meta_count==15 and links_count==45,(meta_count,links_count)
print("XUYI_BUYER_SEO_ROUND2_VERIFIED",meta_count,"locale meta",links_count,"context links")