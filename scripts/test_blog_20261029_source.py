#!/usr/bin/env python3
"""October 28 B2B source, CMS/locales and SEO routing regression; read-only."""
import json,re,html
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0,str(ROOT))
DIST=ROOT/"dist"
POSTS=[json.loads((ROOT/f"data/blog-guides-20261029-{i}.json").read_text("utf8")) for i in (1,2,3)]
LANGS=("en","es","pt","ru","tr")
assert len(POSTS)==3 and len({p["slug"] for p in POSTS})==3
assert {p['slug'] for p in POSTS}==set(["warehouse-staff-custom-water-bottles-bulk-procurement","airport-rail-station-travel-retail-water-bottles-wholesale","coworking-space-member-welcome-kit-water-bottles-wholesale"])
assert all(p["updated"]=="2026-10-29" for p in POSTS)
slug_set={p["slug"] for p in POSTS}
# A source-first release stages new English articles before the four localized
# rows are add-only inserted in D1. Once each CMS translation exists, its page
# becomes mandatory in every subsequent clean build.
snapshot=ROOT/"_local_ops/build-snapshot.json"
state=json.loads(snapshot.read_text("utf8")) if snapshot.is_file() else {}
published_locales={(row.get("resourceId"),row.get("locale")) for row in state.get("translations",[]) if isinstance(row,dict)}
for post in POSTS:
    assert len(post["sections"])==7 and len(post["faqs"])==4
    assert 12<=len(post["primary_keyword"])<=100
    assert len(set(post["secondary_keywords"]))>=3
    assert len(post["checklist"])==10 and len(post["product_notes"])==3
    assert len(post["related"])==3 and post["slug"] not in post["related"]
    assert len({note["sku"] for note in post["product_notes"]})==3
    assert len(set(post["related"]))==3
    from sitemap_modification import source_lastmod
    assert source_lastmod("/blog/"+post["slug"]+"/")=="2026-10-29"
    assert source_lastmod("/pt/blog/"+post["slug"]+"/")=="2026-10-29"
    from PIL import Image
    from hashlib import sha256
    image_path=ROOT/post["cover"].lstrip("/")
    assert image_path.is_file() and image_path.stat().st_size>30000,("Missing reviewed image",post["slug"])
    with Image.open(image_path) as img:
        assert img.format=="WEBP" and img.width>=960 and img.height>=640
    assert len({sha256((ROOT/p["cover"].lstrip("/")).read_bytes()).hexdigest() for p in POSTS})==3
    assert len(post["intro"])>150
    assert all(len(s["paragraph"])>650 for s in post["sections"])
    assert all(p["cover"]!=post["cover"] for p in POSTS if p["slug"]!=post["slug"]) and all(len(section["paragraph"])>450 for section in post["sections"])
    for lang in LANGS:
        prefix="" if lang=="en" else lang+"/"
        path=DIST/prefix/"blog"/post["slug"]/"index.html"
        cms_locale=("page:/blog/"+post["slug"]+"/",lang) in published_locales
        if lang!="en" and not cms_locale:
            # The staged push must not fabricate editor-approved translations.
            assert not path.is_file(),("Unexpected pre-CMS locale article",str(path))
            continue
        assert path.is_file(),("Missing published locale article",str(path))
        text=path.read_text("utf8")
        # Baseline cover is mandatory unless the site owner changed the cover
        # in the CMS; any such manual revision takes precedence over source.
        cms_entry=next((x for x in state.get("blogPosts",[]) if x.get("slug")==post["slug"]),None)
        owner_content=cms_entry.get("content") if isinstance(cms_entry,dict) else None
        owner_photo=owner_content.get("cover") if isinstance(owner_content,dict) else None
        effective_cover=owner_photo or post["cover"]
        assert 'src="'+effective_cover+'"' in text,(lang,post["slug"],"Wrong article hero image",effective_cover)
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
        # A staged page may have two default alternates; the D1-published page has six.
        hreflangs=text.count('rel="alternate" hreflang=')
        assert hreflangs in (2,6),(lang,post["slug"],"incomplete staged/live hreflang",hreflangs)
        h1=re.search(r'<h1\b[^>]*>(.*?)</h1>',text,re.I|re.S)
        assert h1 and len(html.unescape(re.sub("<[^>]*>"," ",h1.group(1))).strip())>15
        assert '<meta property="og:type" content="article">' in text or 'og:title' in text
        idx=DIST/prefix/"blog"/"index.html"
        assert idx.is_file()
        assert idx.read_text("utf8").count('src="/assets/blog-pagination.js"')==1
        assert '/blog/'+post["slug"]+'/' in idx.read_text("utf8"),(lang,post["slug"],"index")
# No generated HTML corrections are applied; links are already in the CMS/source articles.
print("XUYI_20261029_B2B_THREE_LONGTAIL_ARTICLES_FIVE_LOCALES_CMS_SOURCE_LINKS_PASS")