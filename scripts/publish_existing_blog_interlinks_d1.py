#!/usr/bin/env python3
"""One-time guarded write of 16 English blog interlinks INTO D1 CMS main_html.
Never mutates generated HTML or overrides an owner-edited paragraph.
"""
import html
import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from blog_editorial import GUIDES,render_article
from blog_editorial_inline import POSTS,SECTION,english_note
from site_renderer import SERIES

ACCOUNT="a4032d0251103d6ef680b2aaddce1afc"
NAME="xuyi-drinkware-d1"
MIGRATION="xuyi_blog16_english_body_reviewed_20261015_v1"
END="</article></div></div></section>"
RELATED='<section class="section section--soft blog-related">'
ARTICLE='<article class="article blog-editorial__body">'

def fail(message):
    raise RuntimeError("XUYI CMS English blog migration blocked: "+message)

def accepted(body,slug):
    if body.count(ARTICLE)!=1 or body.count(RELATED)!=1 or END not in body:
        return False
    article=body.split(ARTICLE,1)[1].split(END,1)[0]
    if article.count('data-editorial-model="')!=2:
        return False
    sections=SECTION.findall(article)
    if len(sections)!=6:
        return False
    for note in POSTS[slug]:
        para=sections[note["section"]][1]
        if ('data-editorial-model="'+note["sku"]+'"') not in para or ('href="/products/'+note["sku"]+'/"') not in para:
            return False
    tail=article.split(RELATED,1)[1]
    selected=GUIDES[slug]["related"]
    return (tail.count('class="blog-related__item"')==3
            and all('href="/blog/'+x+'/"' in tail for x in selected))

def curate(existing,slug):
    if accepted(existing,slug):
        return existing
    if ('data-editorial-model="' in existing or RELATED in existing
        or existing.count(ARTICLE)!=1 or existing.count(END)!=1):
        fail("changed or partial CMS article "+slug)
    post=GUIDES[slug]
    lead=re.search(r'<p class="blog-lede">(.*?)</p>',existing,re.S)
    if not lead or html.unescape(re.sub(r'<[^>]*>','',lead.group(1))).strip()!=post["intro"]:
        fail("owner-edited introduction "+slug)
    found=SECTION.findall(existing)
    if len(found)!=6:
        fail("wrong number of article sections "+slug)
    for i,(_,paragraph,_) in enumerate(found):
        if html.unescape(re.sub(r'<[^>]*>','',paragraph)).strip()!=post["sections"][i]["paragraph"]:
            fail("owner-edited section "+slug+" #"+str(i))
    notes=POSTS[slug]
    if len(notes)!=2 or len({x["section"] for x in notes})!=2 or len({x["sku"] for x in notes})!=2:
        fail("unreviewed placements "+slug)
    if not {x["sku"] for x in notes}.issubset({x["slug"] for x in SERIES.values()}):
        fail("invalid SKU "+slug)
    if len(post["related"])!=3 or slug in post["related"] or not set(post["related"]).issubset(GUIDES):
        fail("invalid related articles "+slug)
    count=[0]
    def edit(m):
        i=count[0];count[0]+=1
        return m.group(1)+m.group(2)+english_note(slug,i)+m.group(3)
    changed=SECTION.sub(edit,existing)
    if count[0]!=6:
        fail("unmatched paragraphs "+slug)
    source=render_article(slug)
    if source.count(RELATED)!=1 or source.count(END)!=1:
        fail("invalid editorial source "+slug)
    chosen=RELATED+source.split(RELATED,1)[1].split(END,1)[0]
    changed=changed.replace(END,chosen+END,1)
    if len(changed)>180000 or not accepted(changed,slug):
        fail("result failed article editorial review "+slug)
    return changed

def api(token,path,payload=None):
    request=urllib.request.Request(
        "https://api.cloudflare.com/client/v4/accounts/"+ACCOUNT+path,
        data=json.dumps(payload,ensure_ascii=False).encode("utf8") if payload is not None else None,
        headers={"Authorization":"Bearer "+token,"Content-Type":"application/json"},
        method="POST" if payload is not None else "GET")
    try:
        with urllib.request.urlopen(request,timeout=35) as response:
            result=json.load(response)
    except (urllib.error.HTTPError,urllib.error.URLError) as exc:
        fail("Cloudflare API not accessible: "+str(getattr(exc,"code","network")))
    if not result.get("success"):
        fail("Cloudflare D1 API rejected request")
    return result.get("result")

def query(token,db,sql,params=()):
    result=api(token,"/d1/database/"+db+"/query",{"sql":sql,"params":list(params)})
    if not isinstance(result,list) or len(result)!=1 or not result[0].get("success"):
        fail("D1 query failed")
    return result[0]

def run():
    if "--self-test" in sys.argv:
        assert len(POSTS)==16 and set(POSTS)==set(GUIDES)
        for slug in GUIDES:
            markup=render_article(slug)
            for i in range(6):
                markup=markup.replace(english_note(slug,i),"",1)
            original=markup.split(RELATED,1)[0]+END
            updated=curate(original,slug)
            assert accepted(updated,slug) and curate(updated,slug)==updated
            edited=original.replace('<p class="blog-lede">','<p class="blog-lede">OWNER CHANGED ',1)
            try:curate(edited,slug)
            except RuntimeError:pass
            else:fail("owner copy overwritten "+slug)
        print("XUYI_D1_16_ENGLISH_ARTICLE_EDITORIAL_SELFTEST_PASSED")
        return
    token=os.environ.get("CLOUDFLARE_API_TOKEN","")
    if not token or os.environ.get("CLOUDFLARE_ACCOUNT_ID")!=ACCOUNT:
        fail("independent XUYI Cloudflare credentials not available")
    databases=api(token,"/d1/database?name="+NAME)
    matches=[x for x in databases if x.get("name")==NAME]
    if len(matches)!=1 or not re.fullmatch("[0-9a-f-]{36}",str(matches[0].get("uuid",""))):
        fail("XUYI D1 identity not verified")
    db=matches[0]["uuid"]
    done=query(token,db,"SELECT value FROM site_state WHERE key=?",[MIGRATION])["results"]
    if done:
        if done[0]["value"]!="applied":fail("unrecognized editorial marker")
        print("XUYI_D1_ENGLISH_BLOG16_ALREADY_CURATED")
        return
    records=query(token,db,"SELECT route,main_html,publication_status FROM xuyi_page_content WHERE route LIKE '/blog/%'")["results"]
    rows={r["route"]:r for r in records}
    if len(POSTS)!=16 or set(POSTS)!=set(GUIDES):
        fail("reviewed set changed")
    changes=[]
    for slug in POSTS:
        route="/blog/"+slug+"/"
        row=rows.get(route)
        if not row or row["publication_status"]!="published":
            fail("published English CMS body missing "+slug)
        old=row["main_html"]
        new=curate(old,slug)
        if old!=new:changes.append((route,old,new))
    if len(changes) not in (0,16):
        fail("partial CMS edits present; do not silently replay")
    for route,old,new in changes:
        response=query(token,db,
            "UPDATE xuyi_page_content SET main_html=?,updated_at=CURRENT_TIMESTAMP WHERE route=? AND main_html=? AND publication_status='published'",
            [new,route,old])
        if int(response.get("meta",{}).get("changes",0))!=1:
            fail("concurrent CMS edit "+route)
        print("D1_CMS_ARTICLE_UPDATED",route)
    query(token,db,
        "INSERT INTO site_state(key,value,updated_at) VALUES(?,?,CURRENT_TIMESTAMP) ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=CURRENT_TIMESTAMP",
        [MIGRATION,"applied"])
    query(token,db,"UPDATE site_state SET value=CAST(value AS INTEGER)+1,updated_at=CURRENT_TIMESTAMP WHERE key='publish_revision'")
    print("XUYI_D1_ENGLISH_BLOG16_CMS_CONTENT_SAVED",len(changes))

if __name__=="__main__":
    run()