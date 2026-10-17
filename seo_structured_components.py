"""Schema for visible product FAQs and real collection listing cards."""
from __future__ import annotations
from html import unescape
import json
import re

ORIGIN="https://xuyibottles.com"
DETAIL = re.compile(r"<details\b[^>]*>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>\s*</details>",re.I|re.S)
FAQ_LIST = re.compile(r'<div\b[^>]*class="[^"]*\bfaq-list\b[^"]*"[^>]*>(.*?)</div>',re.I|re.S)
CARD = re.compile(r'<a\b(?=[^>]*\bdata-product-card\b)([^>]*?)>',re.I|re.S)
HREF = re.compile(r'\bhref="([^"]+)"',re.I)

def plain(markup):
    return re.sub(r"\s+"," ",unescape(re.sub(r"<[^>]+>"," ",markup))).strip()

def visible_faq(page):
    body=page.split("<main",1)[-1].split("</main>",1)[0]
    group=FAQ_LIST.search(body)
    if not group:return []
    pairs=[(plain(q),plain(a)) for q,a in DETAIL.findall(group.group(1))]
    pairs=[(q,a) for q,a in pairs if len(q)>=8 and len(a)>=15]
    return pairs if len({q for q,a in pairs})==len(pairs) else []

def actual_product_cards(page):
    body=page.split("<main",1)[-1].split("</main>",1)[0]
    links=[]
    for match in CARD.finditer(body):
        href=HREF.search(match.group(1))
        if not href:continue
        url=unescape(href.group(1)).split("?",1)[0].split("#",1)[0]
        if not re.fullmatch(r"/(?:es/|pt/|ru/|tr/)?products/[a-z0-9_-]+/",url,re.I):continue
        if url not in links:links.append(url)
    return links

def build_schema(page,route,locale):
    canonical=ORIGIN+route
    if re.fullmatch(r"/(?:es/|pt/|ru/|tr/)?products/[a-z0-9_-]+/",route):
        pairs=visible_faq(page)
        if not pairs:return None
        return {"@context":"https://schema.org","@type":"FAQPage",
                "@id":canonical+"#product-faq","url":canonical,"inLanguage":locale,
                "mainEntity":[{"@type":"Question","name":q,
                    "acceptedAnswer":{"@type":"Answer","text":a}} for q,a in pairs]}
    if re.fullmatch(r"/(?:es/|pt/|ru/|tr/)?collections/[a-z0-9_-]+/",route):
        links=actual_product_cards(page)
        if not links:return None
        return {"@context":"https://schema.org","@type":"ItemList",
                "@id":canonical+"#visible-product-list","url":canonical,
                "inLanguage":locale,"numberOfItems":len(links),
                "itemListElement":[{"@type":"ListItem","position":i+1,"url":ORIGIN+url}
                                   for i,url in enumerate(links)]}
    return None
def add_at_render(page,route,locale):
    """Build JSON-LD only for the selected visible source components."""
    data=build_schema(page,route,locale)
    if not data or "</head>" not in page:return page
    payload=json.dumps(data,ensure_ascii=False,separators=(",",":")).replace("<",r"\u003c")
    if data["@id"] in page:return page
    left=chr(60)
    tag=left+'script type="application/ld+json">'+payload+left+'/script>'
    return page.replace("</head>",tag+"</head>",1)


