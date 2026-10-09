#!/usr/bin/env python3
"""Only publish complete reviewed translations in XUYI D1.

Keeps canonical/hreflang accurate: no English-body fake translated pages.
Uses precisely the same header, footer, side rail and assets as the English UI.
No additional language is published solely by being enabled in settings.
"""
import html
import json
import os
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/"dist"
SNAPSHOT=ROOT/"_local_ops/build-snapshot.json"
ORIGIN="https://xuyibottles.com"

def valid_route(route):
    return isinstance(route,str) and (route=="/" or re.fullmatch(r"/(?:[a-z0-9_-]+/)+",route) is not None)

def swap_meta(page,name,value):
    tag='<meta name="'+name+'" content="'
    return re.sub(re.escape(tag)+r'[^"]*">',tag+html.escape(value,quote=True)+'">',page,count=1)

def main():
    if not SNAPSHOT.is_file():
        print("XUYI_LOCALES_SKIPPED: no reviewed D1 snapshot")
        return
    data=json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    if data.get("site")!="xuyi-drinkware-site":raise RuntimeError("Wrong locale source site")
    languages=(data.get("languages") or {}).get("languages",[])
    live={r.get("code"):r for r in languages if r.get("enabled") and r.get("publishReady") and r.get("code") in ("es","pt","ru","tr")}
    translated={}
    for item in data.get("translations",[]):
        rid=item.get("resourceId","")
        if not rid.startswith("page:"):continue
        route=rid[5:];loc=item.get("locale");fields=item.get("content") or {}
        if not valid_route(route) or loc not in live:continue
        if not all(isinstance(fields.get(k),str) and fields[k].strip() for k in ("title","description","mainHtml")):continue
        body=fields["mainHtml"]
        if len(body)<120 or re.search(r"<\s*(?:script|iframe|form|object)\b|on(?:click|load|error)\s*=|javascript\s*:",body,re.I):continue
        src=DIST/route.lstrip("/")/"index.html"
        if route=="/":src=DIST/"index.html"
        if src.is_file():translated[(route,loc)]=fields
    created=0
    for (route,loc),fields in translated.items():
        original=(DIST/route.lstrip("/")/"index.html" if route!="/" else DIST/"index.html").read_text(encoding="utf-8")
        if '<main id="main-content">' not in original:continue
        prefix,remainder=original.split('<main id="main-content">',1)
        _,suffix=remainder.split('</main>',1)
        text=prefix+'<main id="main-content">'+fields["mainHtml"]+'</main>'+suffix
        text=text.replace('<html lang="en">','<html lang="'+loc+'">',1)
        text=re.sub(r'<title>[^<]*</title>','<title>'+html.escape(fields["title"])+'</title>',text,count=1)
        text=swap_meta(text,"description",fields["description"])
        localized="/"+live[loc].get("pathPrefix",loc).strip("/")+(route if route!="/" else "/")
        localized=re.sub("/+","/",localized)
        canonical=ORIGIN+localized
        text=re.sub(r'<link rel="canonical" href="[^"]*">','<link rel="canonical" href="'+canonical+'">',text,count=1)
        text=re.sub(r'<meta property="og:url" content="[^"]*">','<meta property="og:url" content="'+canonical+'">',text,count=1)
        dest=DIST/localized.lstrip("/")/"index.html";dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(text,encoding="utf-8")
        created+=1
    # Only link routes that really exist in the generated release.
    alternates={}
    for route,loc in translated:
        prefix=live[loc].get("pathPrefix",loc).strip("/")
        dest=DIST/prefix/route.lstrip("/")/"index.html"
        if dest.is_file():alternates.setdefault(route,[]).append((loc,"/"+prefix+route))
    for route,alts in alternates.items():
        src=DIST/route.lstrip("/")/"index.html" if route!="/" else DIST/"index.html"
        for link in [src]+[DIST/url.lstrip("/")/"index.html" for _,url in alts]:
            content=link.read_text(encoding="utf-8")
            tags=['<link rel="alternate" hreflang="en" href="'+ORIGIN+route+'">']
            tags.extend('<link rel="alternate" hreflang="'+lang+'" href="'+ORIGIN+url+'">' for lang,url in sorted(alts))
            tags.append('<link rel="alternate" hreflang="x-default" href="'+ORIGIN+route+'">')
            content=content.replace('</head>',''.join(tags)+'</head>',1)
            link.write_text(content,encoding="utf-8")
    print("XUYI_REVIEWED_LOCALIZED_PAGES",created,"LANGUAGES",sorted(live),"ALTERNATE_SETS",len(alternates))

if __name__=="__main__":main()