#!/usr/bin/env python3
"""Source-controlled, D1-safe structured data and social-preview enrichment.

Facts only: visible homepage FAQ, existing blog institution author, real image
dimensions and quote-based product workflow. Never invent price, MOQ quantities,
availability, buyers, employee names, independent reviews or certifications.
Run AFTER locale rendering and CMS body merges on every release.
"""
from __future__ import annotations
import html
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, unquote

ROOT=Path(__file__).resolve().parent.parent
ORIGIN="https://leyamould.com"
LANGS={"en":"","es":"es/","pt":"pt/","ru":"ru/","tr":"tr/"}
AUTHOR_WORDING={
 "en":"By XUYI Bottles · Product Sourcing Editorial Team",
 "es":"Por XUYI Bottles · Equipo editorial de compras",
 "pt":"Por XUYI Bottles · Equipe editorial de compras",
 "ru":"Автор: XUYI Bottles · Редакция по закупкам",
 "tr":"Yazan: XUYI Bottles · Ürün tedarik editörleri",
}
SAFE_IMAGE_EXT={".png",".webp",".jpg",".jpeg"}
JSONLD=re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)',re.S)
FAQ_GROUP=re.compile(r'<div class="dark-faq">([\s\S]*?)</div>',re.S)
FAQ_ITEMS=re.compile(r'<details>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>\s*</details>',re.S)
HTML_TAG=re.compile(r"<[^>]*>")
OG_IMAGE=re.compile(r'<meta property="og:image" content="([^"]+)"[^>]*>')
BLOG_META=re.compile(r'(<div class="blog-meta">[\s\S]*?</div>)')

def clean_text(value):
    value=HTML_TAG.sub(" ",value)
    return re.sub(r"\s+"," ",html.unescape(value)).strip()

def safe_json(obj):
    return json.dumps(obj,ensure_ascii=False,separators=(",",":")).replace("<",r"\u003c")

def checked_image_size(path):
    """Parse PNG/WebP/JPEG dimensions with stdlib only; no fetched or guessed dimensions."""
    with path.open("rb") as stream:
        data=stream.read(65536)
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data)>=24:
        return int.from_bytes(data[16:20],"big"),int.from_bytes(data[20:24],"big")
    if data[:4]==b"RIFF" and data[8:12]==b"WEBP" and len(data)>=30:
        fourcc=data[12:16]
        if fourcc==b"VP8X":
            return (1+int.from_bytes(data[24:27],"little"),
                    1+int.from_bytes(data[27:30],"little"))
        if fourcc==b"VP8 " and data[23:26]==b"\x9d\x01\x2a":
            return (int.from_bytes(data[26:28],"little")&0x3fff,
                    int.from_bytes(data[28:30],"little")&0x3fff)
        if fourcc==b"VP8L" and data[20:21]==b"\x2f":
            x=data[21:25]
            return (1+x[0]+((x[1]&0x3f)<<8),
                    1+(x[1]>>6)+(x[2]<<2)+((x[3]&15)<<10))
    if data[:2]==b"\xff\xd8":
        pos=2
        while pos<len(data)-10:
            if data[pos]!=0xff:
                pos+=1
                continue
            marker=data[pos+1]
            pos+=2
            if marker in (0xd8,0xd9,0x01) or 0xd0<=marker<=0xd7:
                continue
            if pos+2>len(data):break
            size=int.from_bytes(data[pos:pos+2],"big")
            if size<2 or pos+size>len(data):break
            if marker in (0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf):
                return (int.from_bytes(data[pos+5:pos+7],"big"),
                        int.from_bytes(data[pos+3:pos+5],"big"))
            pos+=size
    return None

def image_dimensions(url):
    """Only use dimensions of original, local image files, no guessed CDN/R2 sizes."""
    u=urlsplit(html.unescape(url))
    if (u.scheme,u.netloc)!=("https","leyamould.com"):return None
    if not u.path.startswith("/assets/"):return None
    sub=unquote(u.path).lstrip("/")
    if ".." in Path(sub).parts:return None
    img=ROOT/sub
    if img.suffix.lower() not in SAFE_IMAGE_EXT or not img.is_file():return None
    try:
        dims=checked_image_size(img)
        if not dims:return None
        w,h=dims
        if not (w>=64 and h>=64):return None
        return (w,h)
    except (OSError,ValueError):return None

def improve_og(document):
    # Keep the editor-selected image URL, but dimensions are factual metadata:
    # refresh stale values from the verified local image bytes.
    m=OG_IMAGE.search(document)
    if not m:return document,0
    dims=image_dimensions(m.group(1))
    if not dims:return document,0
    head,sep,body=document.partition("</head>")
    if not sep:return document,0
    width,height=dims
    changed=0
    for key,value in (("width",width),("height",height)):
        pattern=re.compile(r'(<meta property="og:image:'+key+r'" content=")(\d+)(")')
        match=pattern.search(head)
        if match:
            if int(match.group(2))!=value:
                head=pattern.sub(lambda x:x.group(1)+str(value)+x.group(3),head,count=1)
                changed+=1
        else:
            image=OG_IMAGE.search(head)
            if image:
                tag='<meta property="og:image:'+key+'" content="'+str(value)+'">'
                head=head[:image.end()]+tag+head[image.end():]
                changed+=1
    return head+sep+body,changed
def faq_from_visible(document):
    match=FAQ_GROUP.search(document)
    if not match:return None
    questions=[(clean_text(q),clean_text(a)) for q,a in FAQ_ITEMS.findall(match.group(1))]
    if len(questions)!=5 or any(not q or not a for q,a in questions):return None
    if len({q for q,a in questions})!=5:return None
    return questions

def improve_home(document,locale):
    """Generate FAQPage from five visible answers only; never author new Q&As."""
    qs=faq_from_visible(document)
    if qs is None:raise ValueError("Homepage 5 visible FAQ answers missing: "+locale)
    if re.search(r'"@type"\s*:\s*"FAQPage"',document):
        return document,0
    prefix=LANGS[locale]
    canonical=ORIGIN+"/"+prefix
    # An independent node avoids overwriting D1 Organization/WebPage objects.
    node={
      "@context":"https://schema.org",
      "@type":"FAQPage",
      "@id":canonical+"#homepage-faq",
      "url":canonical,
      "inLanguage":locale,
      "mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}}
                    for q,a in qs]
    }
    markup='<script type="application/ld+json">'+safe_json(node)+'</script>'
    return document.replace("</head>",markup+"</head>",1),1

def improve_article(document,locale):
    """Visible organizational author linked to About, never a fake Person."""
    if 'class="blog-author-byline"' not in document:
        m=BLOG_META.search(document)
        if m:
            insertion=m.end()
        else:
            # CMS editors may replace the original blog-meta block. Preserve
            # their body and place the organizational byline at the end of main.
            closing_main=re.search(r"</main\s*>",document,re.I)
            if closing_main:
                insertion=closing_main.start()
            else:
                heading=re.search(r"</h1\s*>",document,re.I)
                if not heading:raise ValueError("Blog author insertion point not found: "+locale)
                insertion=heading.end()
        target="/"+LANGS[locale]+"about/"
        byline=('<p class="blog-author-byline"><a rel="author" href="'+target+'">'
                +html.escape(AUTHOR_WORDING[locale])+'</a></p>')
        document=document[:insertion]+byline+document[insertion:]
    prefix=LANGS[locale]
    author_url=ORIGIN+"/"+prefix+"about/"
    changed=[0]
    def update(m):
        try:source=json.loads(m.group(2))
        except ValueError:raise ValueError("Malformed JSON-LD in blog")
        objs=source.get("@graph",[]) if isinstance(source,dict) else []
        if not objs and isinstance(source,dict):objs=[source]
        for item in objs:
            if item.get("@type")!="BlogPosting":continue
            author=item.get("author")
            # Keep real, independently supplied Person or agency author.
            if isinstance(author,dict) and author.get("@type")=="Organization" and author.get("name")=="XUYI Bottles":
                if author.get("url")!=author_url:
                    author["url"]=author_url
                    changed[0]+=1
        return m.group(1)+safe_json(source)+m.group(3)
    document=JSONLD.sub(update,document)
    return document,changed[0]

def improve_product(document,locale):
    """Quote CTA semantics, not bogus Offer or InStock assertions."""
    changed=[0]
    def update(m):
        obj=json.loads(m.group(2))
        parts=obj.get("@graph",[]) if isinstance(obj,dict) and isinstance(obj.get("@graph"),list) else ([obj] if isinstance(obj,dict) else [])
        for item in parts:
            if not isinstance(item,dict) or item.get("@type")!="Product":continue
            url=item.get("url")
            if not isinstance(url,str) or not url.startswith(ORIGIN+"/"):continue
            sku=str(item.get("sku") or "").strip()
            if not sku:continue
            if "potentialAction" not in item:
                # User-facing CTA exists on product pages. This is not an
                # offer, merchant listing price, nor assertion of stock.
                action_name={
                  "en":"Request a model-specific wholesale quotation",
                  "es":"Solicitar cotización mayorista para este modelo",
                  "pt":"Solicitar cotação de atacado para este modelo",
                  "ru":"Запросить оптовое предложение для этой модели",
                  "tr":"Bu model için toptan fiyat teklifi isteyin",
                }[locale]
                target=ORIGIN+"/"+LANGS[locale]+"contact/?model="+sku+"#inquiry"
                item["potentialAction"]={
                  "@type":"CommunicateAction",
                  "name":action_name,
                  "target":{"@type":"EntryPoint","urlTemplate":target}
                }
                changed[0]+=1
        return m.group(1)+safe_json(obj)+m.group(3)
    return JSONLD.sub(update,document),changed[0]

def build_llms(dist):
    """Optional human/LLM navigation aid; no suggestion of ranking guarantees."""
    paths=[
       ("Company and manufacturing","/about/"),
       ("Manufacturing approach","/manufacturing/"),
       ("Quality control and product approval","/quality-control/"),
       ("Browse the plastic water bottle catalog","/products/"),
       ("Sports water bottles","/collections/sports-water-bottles/"),
       ("Kids plastic water bottles","/collections/kids-water-bottles/"),
       ("Large capacity water jugs","/collections/large-capacity-water-jugs/"),
       ("Shaker bottles","/collections/plastic-shaker-bottles/"),
       ("Spray water bottles","/collections/spray-water-bottles/"),
       ("Two-way drinking cups","/collections/two-way-drinking-cups/"),
       ("Titanium vacuum cups","/collections/titanium-vacuum-cups/"),
       ("OEM/ODM customization","/capabilities/oem-odm/"),
       ("Get a model-specific quotation","/contact/"),
       ("Frequently asked questions","/faq/"),
       ("Sourcing guides and explainers","/blog/"),
       ("Tritan vs PP vs PETG vs PC comparison","/blog/tritan-vs-pp-petg-pc/"),
       ("BPA-free sourcing considerations","/blog/bpa-free-plastic-water-bottle-sourcing/"),
       ("Wholesale buyer guide","/blog/wholesale-plastic-water-bottle-buying-guide/"),
       ("Private label OEM/ODM decisions","/blog/oem-vs-odm-plastic-water-bottles/"),
       ("Bottle MOQ and quotation factors","/blog/custom-water-bottle-moq-pricing/"),
    ]
    lines=[
      "# XUYI Bottles — Drinkware Manufacturer and OEM/ODM Supplier",
      "",
      "> Official website: "+ORIGIN+"/. Factory-model drinkware including plastic",
      "> sports/kids bottles, shakers, water jugs, spray bottles, two-way cups and",
      "> titanium vacuum cups for wholesale and custom sourcing.",
      "> Prices, MOQ, materials, testing and production feasibility are confirmed",
      "> individually; do not infer verified Tritan, BPA-free certification or inventory",
      "> from customizable options. Real product capacities use catalog millilitres;",
      "> oz size classes are approximate overseas buying terms, not exact conversions.",
      "",
      "## Official source pages",
      ""
    ]
    facts=json.loads((ROOT/"data/llms-verified-facts.json").read_text(encoding="utf8"))
    faq=json.loads((ROOT/"data/faq-expanded.json").read_text(encoding="utf8"))
    categories={g["id"]:g["questions"] for g in faq["categories"]}
    visible_faq=clean_text((dist/"faq/index.html").read_text(encoding="utf8"))
    summaries=[]
    for group,index in facts["questionRefs"]:
        q,a,related=categories[group][index]
        # CMS content is authoritative. If an editor has changed the live FAQ
        # answer, do not re-publish obsolete source copy in llms.txt.
        if q not in visible_faq or a not in visible_faq:continue
        sentences=re.split(r"(?<=\.)\s+",a)
        summary=" ".join(sentences[:2])
        summaries.extend(["**Q: "+q+"**","A: "+summary,"Source: "+ORIGIN+"/faq/",""])
    facts_lines=[
        "## Verified company facts",
        "",
        "- Legal name: "+facts["legalName"]+" ("+facts["englishLegalName"]+").",
        "- Operating base: "+facts["base"]+".",
        "- Product scope: "+facts["scope"],
        "- Content review date: "+facts["lastSubstantiveReview"]+" (substantive update; not regenerated on every deployment).",
        "",
        "## Frequently asked buyer questions (reviewed summaries)",
        ""
    ]+summaries
    lines[lines.index("## Official source pages"):lines.index("## Official source pages")]=facts_lines
    for title,path in paths:
        local=dist/(path.lstrip("/")+"index.html")
        if local.is_file():lines.append("- ["+title+"]("+ORIGIN+path+")")
    lines.extend(["","## Other languages",
      "- [Spanish]("+ORIGIN+"/es/)",
      "- [Portuguese]("+ORIGIN+"/pt/)",
      "- [Russian]("+ORIGIN+"/ru/)",
      "- [Turkish]("+ORIGIN+"/tr/)",
      "",
      "This is an optional navigation reference; the HTML pages and verified source",
      "documents are authoritative. No AI search engine is guaranteed to use this file.",
      ""])
    target=dist/"llms.txt"
    content="\n".join(lines)
    if not target.is_file() or target.read_text(encoding="utf8")!=content:
        target.write_text(content,encoding="utf8")
    return len(paths)

def add_at_render(document,route,locale):
    """Apply trust/technical enhancements in the shared renderer before write."""
    if locale not in ("en","es","pt","ru","tr"):
        return document
    base=str(route or "/")
    prefix="/"+locale
    if locale!="en" and base.startswith(prefix+"/"):
        base=base[len(prefix):]
    if base in ("/","") and FAQ_GROUP.search(document):
        document,_=improve_home(document,locale)
    if base.startswith("/blog/") and base!="/blog/":
        document,_=improve_article(document,locale)
    if base.startswith("/products/"):
        document,_=improve_product(document,locale)
    document,_=improve_og(document)
    return document

if __name__=="__main__":
    build_llms(ROOT/"dist")
