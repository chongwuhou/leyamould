#!/usr/bin/env python3
"""Phase-two mould-news gate: D1 articles, locales, evidence and media."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/"dist"
SNAPSHOT=ROOT/"_local_ops"/"build-snapshot.json"
JSONLD=re.compile(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',re.I|re.S)
IMG=re.compile(r"<img\b[^>]*>",re.I)
BAD_TRANSLATION_FRAGMENTS = {
    "es": ("gorras deportivas",),
    "pt": ("especificar it", "depende depende"),
    "ru": ("спортивных кепок", "оба понятны, но не являются синонимами"),
    "tr": ("anlaşılır olabilir",),
}

def attr(tag,key):
    return re.search(r"\b"+re.escape(key)+r'=["\']([^"\']+)["\']',tag,re.I)

def schema_nodes(document):
    result=[]
    for match in JSONLD.finditer(document):
        try:data=json.loads(match.group(1))
        except (ValueError,TypeError):continue
        values=data.get("@graph",[]) if isinstance(data,dict) and isinstance(data.get("@graph"),list) else [data]
        result.extend(item for item in values if isinstance(item,dict))
    return result

def main():
    state=json.loads(SNAPSHOT.read_text(encoding="utf8"))
    published=[str(row.get("slug")) for row in state.get("blogPosts",[])
               if isinstance(row,dict) and row.get("status")=="published"]
    assert published and len(published)==len(set(published)), "D1 published Blog set is invalid"
    manifest=json.loads((DIST/"locale-manifest.json").read_text(encoding="utf8"))
    locales=manifest.get("locales") or []
    assert locales, "Locale manifest is empty"
    source_locale = str(next((row.get("code") for row in locales if row.get("sortOrder") == 10), locales[0].get("code") or "en"))
    # The pre-launch site intentionally keeps indexing disabled, so sitemap.xml
    # is empty.  Validate the actual mould article routes instead of requiring
    # a water-cup `/blog/<slug>/` path or sitemap lastmod fields.
    editorial=json.loads((ROOT/"data"/"mould-news-editorial.json").read_text(encoding="utf8"))
    editorial_by_slug={str(row.get("slug")):row for row in editorial.get("items",[]) if isinstance(row,dict) and row.get("slug")}
    checked=0
    faq_pages=0
    breadcrumb_pages=0
    image_count=0
    article_keywords={}
    citation_pages=0
    evidence_pages=0
    for language in locales:
        code=str(language.get("code") or "")
        prefix=str(language.get("pathPrefix") or "")
        for slug in published:
            row=next((item for item in state.get("blogPosts",[]) if isinstance(item,dict) and str(item.get("slug"))==slug),{})
            editorial_row=row.get("editorial") if isinstance(row.get("editorial"),dict) else editorial_by_slug.get(slug,{})
            category=str(editorial_row.get("category") or row.get("category") or "news")
            category_route="news" if category=="news" else "Bottle-Cap-Machine"
            page=DIST/(prefix if prefix else ".")/category_route/(slug+".html")
            assert page.is_file(), (code,slug,"missing static mould article page")
            document=page.read_text(encoding="utf8")
            for fragment in BAD_TRANSLATION_FRAGMENTS.get(code, ()):
                assert fragment.casefold() not in document.casefold(), (code,slug,"known translation fragment",fragment)
            parsed=schema_nodes(document)
            article_schema=[item for item in parsed if item.get("@type") in {"BlogPosting","Article"}]
            assert article_schema and any(str(item.get("headline") or item.get("name") or "").strip() for item in article_schema), (code,slug,"localized article schema")
            citation_pages+=1
            assert any(marker in document for marker in ('id="primary-sources"','data-editorial-source="mould-registry"')), (code,slug,"visible source evidence")
            evidence_pages+=1
            article_keywords[(code,slug)]=next((str(item.get("headline") or item.get("name") or "").strip() for item in article_schema if str(item.get("headline") or item.get("name") or "").strip()),"")
            breadcrumbs=[item for item in parsed if item.get("@type")=="BreadcrumbList"]
            assert breadcrumbs and len(breadcrumbs[0].get("itemListElement") or [])>=2,(code,slug,"BreadcrumbList")
            breadcrumb_pages+=1
            section=re.search(r'<section\b[^>]*class=["\'][^"\']*\bblog-faq\b[^"\']*["\'][^>]*>(.*?)</section>',document,re.I|re.S)
            pairs=re.findall(r"<details\b[^>]*>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>\s*</details>",section.group(1),re.I|re.S) if section else []
            faqs=[item for item in parsed if item.get("@type")=="FAQPage"]
            if pairs:
                assert len(faqs)==1 and len(faqs[0].get("mainEntity") or [])==len(pairs),(code,slug,"FAQPage")
                faq_pages+=1
            cover=re.search(r'<img\b[^>]*class=["\'][^"\']*\bnews-detail-image\b[^"\']*["\'][^>]*>',document,re.I|re.S)
            assert cover,(code,slug,"Blog cover")
            tag=cover.group(0)
            loading=attr(tag,"loading")
            assert loading and loading.group(1).lower()=="eager",(code,slug,"cover loading")
            body=document.split("</main>",1)[0]
            for image in IMG.findall(body):
                image_count+=1
            checked+=1
    for language in locales:
        code=str(language.get("code") or "")
        if code==source_locale: continue
        for slug in published:
            localized=article_keywords.get((code,slug),"")
            source=article_keywords.get((source_locale,slug),"")
            assert localized and localized != source, (code,slug,"source-language article metadata inherited")
    print("XUYI_PHASE2_BLOG_SEO_PASSED",checked,"localized_blog_pages",faq_pages,"FAQPage",breadcrumb_pages,"BreadcrumbList",image_count,"images","localized_keywords",len(article_keywords),"citation_pages",citation_pages,"evidence_pages",evidence_pages)

if __name__=="__main__":
    main()

