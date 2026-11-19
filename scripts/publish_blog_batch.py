#!/usr/bin/env python3
"""Publish a reviewed multilingual Blog batch through the generic D1/CMS route.

The source JSON is versioned editorial input. D1 remains authoritative after the
write; this client is idempotent and never sends credentials to output.
"""
from __future__ import annotations
import html
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

LOCALES=("es","pt","ru","tr")
ORIGIN=os.environ.get("XUYI_SITE_ORIGIN","https://xuyibottles.com").rstrip("/")

def esc(value):
    return html.escape(str(value or ""), quote=True)

def localized_product_note(post, locale, section_index):
    for note in post.get("product_notes",[]):
        if int(note.get("section",-1)) != section_index:
            continue
        pattern=str((note.get("text") or {}).get(locale) or "")
        label=str((note.get("label") or {}).get(locale) or note.get("sku") or "")
        if pattern.count("{product}") != 1:
            raise ValueError("invalid product note "+post["slug"])
        front, back=pattern.split("{product}")
        href=("/"+locale if locale!="en" else "")+"/products/"+str(note["sku"])+"/"
        return (' <span class="blog-editorial__product-note" data-editorial-model="'+esc(note["sku"])+'">'
                +esc(front)+'<a class="blog-editorial__product-link" href="'+href+'">'+esc(label)
                +'</a>'+esc(back)+'</span>')
    return ""

def main_html(post, locale, data):
    slug=post["slug"]
    sections=data["sections"]
    if len(sections)!=7:
        raise ValueError(slug+" must have 7 translated sections")
    prefix="" if locale=="en" else "/"+locale
    body=('<section class="page-intro"><div class="shell"><div class="breadcrumb"><a href="'+prefix+'/">Home</a> / <a href="'+prefix+'/blog/">Blog</a> / Buying Guide</div>'
          '<span class="eyebrow">'+esc(data["category"])+'</span><h1>'+esc(data["title"])+'</h1><p>'+esc(data["description"])+'</p></div></section>')
    body+=('<section class="section blog-editorial"><div class="shell"><div class="blog-detail__cover"><img src="'+esc(post["cover"])+'" alt="'+esc(post["coverAlt"])+'" width="1200" height="800" loading="eager" decoding="async"></div>'
           '<div class="blog-editorial__layout"><aside class="blog-editorial__aside"><div class="blog-toc"><span class="eyebrow">IN THIS GUIDE</span><nav aria-label="Article sections">')
    for i,(heading,_) in enumerate(sections):
        body+='<a href="#article-section-'+str(i)+'">'+esc(heading)+'</a>'
    body+=('</nav><a class="blog-toc__quote" href="'+prefix+'/contact/#inquiry">Discuss your project →</a></div></aside><article class="article blog-editorial__body">'
            '<div class="blog-meta"><span>'+esc(data["category"])+'</span><span><time datetime="'+post["updated"]+'">'+post["updated"]+'</time></span></div>'
            '<p class="blog-author-byline"><a rel="author" href="'+prefix+'/about/">XUYI Bottles · Product Sourcing Editorial Team</a></p>'
            '<p class="blog-lede">'+esc(data["intro"])+'</p>')
    body+='<div class="blog-takeaway"><strong>Before releasing a wholesale order</strong><ul>'+''.join("<li>"+esc(x)+"</li>" for x in data["checklist"][:3])+'</ul></div>'
    for i,(heading,paragraph) in enumerate(sections):
        body+=('<section class="blog-section" id="article-section-'+str(i)+'"><h2>'+esc(heading)+'</h2><p>'
               +esc(paragraph)+localized_product_note(post,locale,i)+'</p></section>')
    ev=post["evidence"]
    body+=('<section class="blog-evidence" id="primary-sources" aria-labelledby="primary-sources-heading"><span class="eyebrow">SOURCE-CHECKED BUYER NOTES</span>'
          '<h2 id="primary-sources-heading">'+esc(ev["insight"].split(".")[0])+'</h2><p>'+esc(ev["insight"])+'</p><p><strong>Practical next step:</strong> '
          +esc(ev["next_step"])+'</p><h3>Primary references</h3><ul>')
    for i,ref in enumerate(ev["sources"]):
        label=data["sourceLabels"][i] if i<len(data["sourceLabels"]) else ref["label"]
        body+='<li><a href="'+esc(ref["url"])+'" target="_blank" rel="noopener noreferrer">'+esc(label)+' ↗</a></li>'
    body+='</ul><p class="blog-evidence__caveat">These independent references do not certify an XUYI bottle, factory, material or test. Verify the exact model, destination market and current requirements.</p></section>'
    m=data["matrix"]
    body+=('<section class="blog-buyer-matrix" id="buyer-decision-table"><h2>'+esc(m["title"])+'</h2><p>'+esc(m["intro"])+'</p><div class="blog-buyer-matrix__scroll"><table><thead><tr>'
           +''.join("<th scope=\"col\">"+esc(x)+"</th>" for x in m["head"])+'</tr></thead><tbody>')
    for row in m["rows"]:
        body+='<tr><th scope="row">'+esc(row[0])+'</th><td>'+esc(row[1])+'</td><td>'+esc(row[2])+'</td></tr>'
    body+='</tbody></table></div><p class="blog-buyer-matrix__note">Buyer decision criteria, not XUYI certification, published MOQ or guaranteed delivery times. Verify the exact model and market requirements.</p></section>'
    body+='<section class="blog-checklist"><h2>Buyer checklist</h2><ul>'+''.join("<li>"+esc(x)+"</li>" for x in data["checklist"])+'</ul></section>'
    body+='<section class="blog-faq"><h2>Frequently asked questions</h2>'+''.join("<details><summary>"+esc(q)+"</summary><p>"+esc(a)+"</p></details>" for q,a in data["faqs"])+'</section>'
    body+='<div class="blog-editorial__cta"><h2>Need a quote for a specific model?</h2><p>Send the model, expected order quantity, customization and destination market so the sourcing team can review the confirmed scope.</p><a class="button" href="'+prefix+'/contact/#inquiry">Request a Plastic Bottle Quote →</a></div>'
    body+='<section class="section section--soft blog-related"><div class="shell"><div class="section__head"><div><span class="eyebrow">CONTINUE READING</span><h2 class="section__title">Related Buying Guides</h2></div></div><div class="blog-related__grid">'
    for item in data["related"]:
        body+='<article class="blog-related__item"><a href="'+prefix+'/blog/'+item["slug"]+'/"><strong>'+esc(item["title"])+'</strong></a><p>'+esc(item["description"])+'</p></article>'
    body+='</div></div></section></article></div></div></section>'
    return body

def card_html(post, locale, data):
    prefix="" if locale=="en" else "/"+locale
    url=prefix+"/blog/"+post["slug"]+"/"
    return ('<article class="news-card"><a class="news-card__image" href="'+url+'"><img src="'+esc(post["cover"])+'" alt="'+esc(data["title"])+'" width="1200" height="800" loading="lazy"></a>'
            '<div class="news-card__info"><span class="news-card__category">'+esc(data["category"])+'</span><h3><a href="'+url+'">'+esc(data["title"])+'</a></h3><p>'+esc(data["description"])+'</p>'
            '<a class="news-card__read" href="'+url+'">Read Article →</a></div></article>')

def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: publish_blog_batch.py <reviewed-batch.json>")
    token=os.environ.get("CLOUDFLARE_API_TOKEN","")
    if not token:
        raise SystemExit("CLOUDFLARE_API_TOKEN unavailable")
    rows=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    if not isinstance(rows,list) or not rows:
        raise SystemExit("source must be a non-empty list")
    posts=[]; translations=[]; cards=[]
    for source in rows:
        content={k:v for k,v in source.items() if k not in {"locales","localized_related"}}
        required=("slug","title","description","intro","cover","updated","sections","checklist","faqs","related","product_notes","buyerDecisionTable","evidence")
        for key in required:
            if key not in content:
                raise ValueError(source.get("slug","")+" missing "+key)
        posts.append({"slug":source["slug"],"publishedAt":source["updated"]+"T12:00:00.000Z","post":content})
        locales=source.get("locales") or {}
        if set(locales)!=set(LOCALES):
            raise ValueError(source["slug"]+" locale set mismatch")
        related_map=source.get("localized_related") or {}
        for locale in LOCALES:
            data=dict(locales[locale])
            data["related"]=[]
            for related_slug in source["related"]:
                item=(related_map.get(locale) or {}).get(related_slug)
                if not item:
                    raise ValueError(source["slug"]+" missing related translation "+locale+" "+related_slug)
                data["related"].append({"slug":related_slug,"title":item["title"],"description":item["description"]})
            main=main_html(source,locale,data)
            if main.count('class="blog-section"')!=7 or main.count('class="blog-editorial__product-link"')!=3 or main.count('class="blog-related__item"')!=3 or main.count('class="blog-buyer-matrix"')!=1 or main.count("<details>")!=4:
                raise ValueError(source["slug"]+" "+locale+" HTML contract failed")
            translations.append({"route":"/blog/"+source["slug"]+"/","locale":locale,"title":data["title"],"description":data["description"],"mainHtml":main})
            cards.append({"slug":source["slug"],"locale":locale,"html":card_html(source,locale,data)})
    payload={"posts":posts,"translations":translations,"indexCards":cards}
    request=urllib.request.Request(ORIGIN+"/api/admin/blog-batch",data=json.dumps(payload,ensure_ascii=False,separators=(",",":")).encode("utf-8"),method="POST",headers={"Authorization":"Bearer "+token,"Content-Type":"application/json","Accept":"application/json","User-Agent":"XUYI-Blog-Batch-Publisher/1.0","x-xuyi-publish-intent":"explicit-owner-approval"})
    try:
        with urllib.request.urlopen(request,timeout=60) as response:
            result=json.load(response)
    except urllib.error.HTTPError as err:
        detail=err.read().decode("utf-8","replace")[:500]
        raise SystemExit("XUYI Blog batch HTTP "+str(err.code)+": "+detail)
    print("XUYI_BLOG_BATCH_PUBLISHED",json.dumps(result,ensure_ascii=False,sort_keys=True))

if __name__=="__main__":
    main()
