#!/usr/bin/env python3
"""October 27 B2B source, CMS/locales and SEO routing regression; read-only."""
import json,re,html
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0,str(ROOT))
DIST=ROOT/"dist"
POSTS=json.loads((ROOT/"data/blog-guides-20261027.json").read_text("utf8"))
LANGS=("en","es","pt","ru","tr")
assert len(POSTS)==3 and len({p["slug"] for p in POSTS})==3
assert {p['slug'] for p in POSTS}==set(["apartment-resident-welcome-kit-branded-water-bottles-bulk","summer-camp-reusable-water-bottles-group-order","nonprofit-fundraiser-custom-water-bottles-wholesale"])
assert all(p["updated"]=="2026-10-27" for p in POSTS)
slug_set={p["slug"] for p in POSTS}
for post in POSTS:
    assert len(post["sections"])==7 and len(post["faqs"])==4
    assert 12<=len(post["primary_keyword"])<=100
    assert len(set(post["secondary_keywords"]))>=3
    assert len(post["checklist"])==10 and len(post["product_notes"])==3
    assert len(post["related"])==3 and post["slug"] not in post["related"]
    assert len({note["sku"] for note in post["product_notes"]})==3
    assert len(set(post["related"]))==3
    from sitemap_modification import source_lastmod
    assert source_lastmod("/blog/"+post["slug"]+"/")=="2026-10-27"
    assert source_lastmod("/pt/blog/"+post["slug"]+"/")=="2026-10-27"
    assert len(post["intro"])>150
    assert all(len(s["paragraph"])>650 for s in post["sections"])
    assert all(p["cover"]!=post["cover"] for p in POSTS if p["slug"]!=post["slug"]) and all(len(section["paragraph"])>450 for section in post["sections"])
    for lang in LANGS:
        prefix="" if lang=="en" else lang+"/"
        path=DIST/prefix/"blog"/post["slug"]/"index.html"
        assert path.is_file(),("Missing locale article",str(path))
        text=path.read_text("utf8")
        assert text.count("blog-editorial__product-link")==3,(lang,post["slug"],"SKU count")
        assert text.count('class="blog-related__item"')==3,(lang,post["slug"],"related count")
        assert text.count('class="blog-buyer-matrix"')==1,(lang,post["slug"],"buyer table")
        faq=re.search(r'<section class="blog-faq">(.*?)</section>',text,re.S)
        assert faq and faq.group(1).count("<details>")==4,(lang,post["slug"],"FAQs")
        assert text.count('class="blog-section"')==7,(lang,post["slug"],"sections")
        for note in post["product_notes"]:
            url="/"+(lang+"/" if lang!="en" else "")+"products/"+note["sku"]+"/"
            assert 'href="'+url+'"' in text,(lang,post["slug"],url)
        for related in post["related"]:
            url="/"+(lang+"/" if lang!="en" else "")+"blog/"+related+"/"
            assert 'href="'+url+'"' in text,(lang,post["slug"],url)
        route="/"+prefix+"blog/"+post["slug"]+"/"
        assert 'href="https://xuyibottles.com'+route+'"' in text,(lang,route,"canonical")
        # During the first add-only release the new locales are built before
        # their D1 CMS rows are inserted; hreflang appears after publication.
        # A staged page may therefore have no alternates, never a partial set.
        hreflangs=text.count('rel="alternate" hreflang=')
        assert hreflangs in (0,6),(lang,post["slug"],"partial hreflang",hreflangs)
        h1=re.search(r'<h1\b[^>]*>(.*?)</h1>',text,re.I|re.S)
        assert h1 and len(html.unescape(re.sub("<[^>]*>"," ",h1.group(1))).strip())>15
        assert '<meta property="og:type" content="article">' in text or 'og:title' in text
        idx=DIST/prefix/"blog"/"index.html"
        assert idx.is_file()
        assert idx.read_text("utf8").count('src="/assets/blog-pagination.js"')==1
        assert '/blog/'+post["slug"]+'/' in idx.read_text("utf8"),(lang,post["slug"],"index")
# No generated HTML corrections are applied; links are already in the CMS/source articles.
print("XUYI_20261027_B2B_THREE_LONGTAIL_ARTICLES_FIVE_LOCALES_CMS_SOURCE_LINKS_PASS")