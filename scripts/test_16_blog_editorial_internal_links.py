#!/usr/bin/env python3
"""Editorial acceptance of 16 real blog posts x five locales (not sitewide link counts)."""
from pathlib import Path
from html.parser import HTMLParser
from html import unescape
import json,hashlib,re,sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from blog_editorial_inline import POSTS,BASE,LANGS,reviewed_localized_article
from blog_editorial import GUIDES,render_article
from site_renderer import SERIES
from turkish_bottle_cap_source import reviewed_turkish_bottle_caps
from spanish_reviewed_copy import reviewed_spanish_copy
SNAP=json.loads((ROOT/"_local_ops/build-snapshot.json").read_text(encoding="utf8"))
D1={(r["resourceId"][5:],r["locale"]):r["content"] for r in SNAP["translations"]
    if r.get("resourceId","").startswith("page:")}
assert len(POSTS)==16 and set(POSTS)==set(GUIDES)
real_models={r["slug"] for r in SERIES.values()}
accepted=0
for slug,notes in POSTS.items():
    guide=GUIDES[slug]
    assert len(notes)==2 and len({x["section"] for x in notes})==2
    assert all(0<=x["section"]<len(guide["sections"]) for x in notes)
    skus={x["sku"] for x in notes}
    assert len(skus)==2 and skus.issubset(real_models)
    chosen=guide["related"]
    assert 2<=len(chosen)<=3 and len(set(chosen))==len(chosen)
    assert slug not in chosen and set(chosen).issubset(GUIDES)
    for locale in LANGS:
        prefix="" if locale=="en" else "/"+locale
        path=ROOT/"dist"/("" if locale=="en" else locale)/"blog"/slug/"index.html"
        page=path.read_text(encoding="utf8")
        main=page.split('<main id="main-content">',1)[1].split("</main>",1)[0]
        assert 'class="blog-product-proof"' not in main,(slug,locale,"old auto callout still active")
        article=re.search(r'<article class="article blog-editorial__body">(.+?)</article></div></div></section>',main,re.S)
        assert article,(slug,locale,"related guides must be INSIDE article before closing")
        body=article.group(1)
        sections=re.findall(r'<section class="blog-section"[^>]*>.*?</section>',body,re.S)
        assert len(sections)==6,(slug,locale,len(sections))
        with_links=[i for i,x in enumerate(sections) if 'data-editorial-model="' in x]
        assert with_links==sorted(x["section"] for x in notes),(slug,locale,"not placed in distinct buying paragraphs")
        assert sum(x.count('class="blog-editorial__product-link"') for x in sections)==2
        for note in notes:
            i=note["section"];sku=note["sku"]
            expected=prefix+"/products/"+sku+"/"
            block=sections[i]
            assert ('data-editorial-model="'+sku+'"') in block
            assert ('href="'+expected+'"') in block
            assert block.count('class="blog-editorial__product-link"')==1
            assert (ROOT/"dist"/expected.lstrip("/")/"index.html").exists(),(slug,locale,expected)
            assert "{model}" not in block and note["text"][locale].count("{model}")==1
        # The existing three carefully selected guides have been moved from
        # the generic outer layout to the article END after the inquiry CTA.
        assert body.count('class="section section--soft blog-related"')==1,(slug,locale)
        assert body.rfind("blog-related")>body.rfind("blog-editorial__cta"),(slug,locale)
        related=re.search(r'<section class="section section--soft blog-related">(.+)</section>\s*$',body,re.S)
        assert related,(slug,locale)
        cards=re.findall(r'<article class="blog-related__item">.*?</article>',related.group(1),re.S)
        assert len(cards)==len(chosen),(slug,locale,len(cards))
        for card,related_slug in zip(cards,chosen):
            link=re.search(r'<a href="([^"]+)"',card)
            assert link,(slug,locale,"related link absent")
            url=link.group(1)
            expected=prefix+"/blog/"+related_slug+"/"
            # The original localization pipeline rewrites internal anchors
            # to locale-prefixed pages at the template/render stage.
            assert url==expected,(slug,locale,url,expected)
            assert (ROOT/"dist"/url.lstrip("/")/"index.html").exists()
            assert '<strong>' in card
        assert 'class="section section--soft blog-related"' not in main[article.end():]
        if locale!="en":
            route="/blog/"+slug+"/"
            original=D1[(route,locale)]["mainHtml"]
            assert hashlib.sha256(original.encode("utf8")).hexdigest()==BASE[slug][locale]
            fields=reviewed_turkish_bottle_caps(route,locale,D1[(route,locale)])
            fields=reviewed_spanish_copy(route,locale,fields)
            reviewed=reviewed_localized_article(fields["mainHtml"],route,locale,source_original=original)
            assert reviewed.count('data-editorial-model="')==2
            assert reviewed_localized_article(reviewed,route,locale,source_original=original)==reviewed
            owner=original.replace('<p class="blog-lede">','<p class="blog-lede">Manual CMS edit: ',1)
            assert owner!=original
            assert reviewed_localized_article(owner,route,locale,source_original=owner)==owner,(slug,locale,"owner overwritten")
            assert reviewed_localized_article('<article>Brand-new owner article</article>',route,locale,source_original='<article>Brand-new owner article</article>')=='<article>Brand-new owner article</article>'
        else:
            authored=render_article(slug)
            assert authored.count('data-editorial-model="')==2
        accepted+=1
# New independently approved articles aren't restricted by the historical
# set of 16 or given invented model references.
new='<article class="article blog-editorial__body"><p>New owner copy</p></article>'
assert reviewed_localized_article(new,"/blog/future-2027-guide/","es",new)==new
print("XUYI_16_PUBLISHED_ARTICLES_X_5_LOCALES_2_BODY_SKU_LINKS_3_END_RELATED_OWNER_FIRST_PASSED",accepted)