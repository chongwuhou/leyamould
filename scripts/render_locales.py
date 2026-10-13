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
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from home_banner_config import tag as banner_tag,for_locale as banner_slides
from locale_registry import approved_locales,local_url
from product_locale_seo import polish_product_head
from media_alt_render import apply_media_alts
from image_alt_quality import polish_image_alt
from product_material_performance import inject as inject_materials

ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/"dist"
SNAPSHOT=ROOT/"_local_ops/build-snapshot.json"
ORIGIN="https://xuyibottles.com"
UI_TRANSLATIONS=json.loads((ROOT/"data/ui-translations.json").read_text(encoding="utf-8"))
RUNTIME_UI_TRANSLATIONS=json.loads((ROOT/"data/runtime-ui-translations.json").read_text(encoding="utf-8"))
BLOG_DATE_LABELS={
    "es":("Publicado el","Revisado el"),
    "pt":("Publicado em","Revisto em"),
    "ru":("Опубликовано","Проверено"),
    "tr":("Yayımlandı","Gözden geçirildi")
}

def correct_reviewed_drinkware_terms(markup,locale):
    """Repair identified false-friend translations without altering SKU/specs.

    Rendered local HTML only: original D1 copy remains untouched.
    Plastic drinkware is neither liquid beverages nor a mechanical variator.
    """
    changes={
        "es":[("variadores de plástico","botellas de plástico"),
              ("bebidas de plástico","botellas de plástico")],
        "pt":[("bebidas de plástico","garrafas de plástico")],
    }
    for incorrect,correct in changes.get(locale,[]):
        pat=re.compile(re.escape(incorrect),re.I)
        def replacement(match):
            raw=match.group()
            if raw.isupper():return correct.upper()
            if raw[:1].isupper():return correct[:1].upper()+correct[1:]
            return correct
        markup=pat.sub(replacement,markup)
    return markup

def localize_blog_timeline(body,original,locale,route):
    """Reflect actual source publication/review dates in the translated page.

    Localized D1 HTML predates the truthful publication-vs-review distinction.
    Read dates from the canonical article HEAD; never backdate or guess dates.
    """
    if not re.fullmatch(r"/blog/[a-z0-9-]+/",route):return body
    def dated(key):
        match=re.search(r'<meta property="article:'+key+r'_time" content="(\d{4}-\d{2}-\d{2})">',original)
        return match.group(1) if match else None
    published,modified=dated("published"),dated("modified")
    if not published:return body  # No verified source date: preserve approved D1 copy.
    first,reviewed=BLOG_DATE_LABELS[locale]
    timeline='<time datetime="'+published+'">'+html.escape(first)+" "+published+"</time>"
    if modified and modified>published:
        timeline+=' · <time datetime="'+modified+'">'+html.escape(reviewed)+" "+modified+"</time>"
    updated,count=re.subn(r'(<div class="blog-meta">\s*<span>[^<]*</span>\s*<span>).*?(</span>\s*</div>)',
        lambda match:match.group(1)+timeline+match.group(2),body,count=1,flags=re.S)
    if count!=1:raise RuntimeError("Cannot update localized blog date safely: "+locale+" "+route)
    return updated

def localize_structured_data(markup,locale,route,localized,fields,approved_routes,path_prefix=None):
    """Match JSON-LD to the reviewed language page, never the English source.

    Product identifiers, images and the global legal Organization remain
    untouched; only page-local language, URLs and human-facing text change.
    Untranslated FAQ answers are dropped rather than represented as reviewed.
    """
    own=ORIGIN+localized
    source=ORIGIN+route
    h1match=re.search(r'<h1\b[^>]*>(.*?)</h1>',fields["mainHtml"],re.S|re.I)
    heading=html.unescape(re.sub(r'<[^>]*>',' ',h1match.group(1))).strip() if h1match else ""
    heading=re.sub(r'\s+',' ',heading) or fields["title"].split(" | ",1)[0]
    ui=UI_TRANSLATIONS.get(locale,{})
    def localize_item(item):
        if not isinstance(item,dict):return item
        typ=item.get("@type")
        if typ=="FAQPage":return None
        if typ=="Organization":return item  # One globally identifiable legal company.
        if typ in ("Product","BlogPosting","Service","WebPage"):
            for key in ("@id","url"):
                if isinstance(item.get(key),str) and item[key].startswith(source):
                    item[key]=own+item[key][len(source):]
            if isinstance(item.get("mainEntityOfPage"),dict):
                x=item["mainEntityOfPage"]
                if isinstance(x.get("@id"),str) and x["@id"].startswith(source):
                    x["@id"]=own+x["@id"][len(source):]
            elif item.get("mainEntityOfPage")==source:item["mainEntityOfPage"]=own
            item["inLanguage"]=locale
            if typ=="BlogPosting":item["headline"]=fields["title"]
            else:item["name"]=heading
            item["description"]=fields["description"]
        if typ=="BreadcrumbList":
            for crumb in item.get("itemListElement",[]):
                value=crumb.get("item","")
                if not isinstance(value,str) or not value.startswith(ORIGIN+"/"):continue
                original_route=value[len(ORIGIN):]
                if original_route in approved_routes:
                    crumb["item"]=ORIGIN+"/"+(path_prefix or locale)+original_route
                    if original_route=="/":crumb["name"]=ui.get("Home",crumb.get("name","Home"))
                    elif original_route==route:crumb["name"]=heading
                    elif original_route=="/products/":crumb["name"]=ui.get("Products",crumb.get("name","Products"))
                    elif original_route=="/blog/":crumb["name"]=ui.get("Blog",crumb.get("name","Blog"))
        return item
    def replace(match):
        try:data=json.loads(match.group(1))
        except (ValueError,TypeError) as exc:raise RuntimeError("Invalid source JSON-LD: "+route) from exc
        if not isinstance(data,dict):raise RuntimeError("JSON-LD root must be an object: "+route)
        if isinstance(data.get("@graph"),list):
            data["@graph"]=[v for raw in data["@graph"] if (v:=localize_item(raw)) is not None]
        else:
            data=localize_item(data)
            if data is None:return ""
        return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False,separators=(",",":")).replace("<",r"\u003c")+'</script>'
    return re.sub(r'<script type="application/ld\+json">([\s\S]*?)</script>',replace,markup)

def translate_chrome(chunk,locale,ui_override=None):
    mappings={**UI_TRANSLATIONS.get(locale,{})}
    if isinstance(ui_override,dict):
        mappings.update({key:value for key,value in ui_override.items()
                         if key in mappings and isinstance(value,str) and value.strip()})
    # Translate exact shared header/footer text and human-facing alt,
    # aria-label, placeholder and title values. Never edit href/src/IDs.
    def replace(match):
        content=match.group(1)
        leading=content[:len(content)-len(content.lstrip())]
        trailing=content[len(content.rstrip()):]
        value=html.unescape(content.strip())
        translated=mappings.get(value)
        if not translated:return match.group(0)
        return ">"+leading+html.escape(translated)+trailing+"<"
    chunk=re.sub(r">([^<>]+)<",replace,chunk)
    def attribute(match):
        old=html.unescape(match.group(2))
        translated=mappings.get(old)
        if not translated:return match.group(0)
        return match.group(1)+'="'+html.escape(translated,quote=True)+'"'
    return re.sub(r'\b(aria-label|alt|placeholder|title)="([^"]*)"',attribute,chunk)

def valid_route(route):
    return isinstance(route,str) and (route=="/" or re.fullmatch(r"/(?:[a-z0-9_-]+/)+",route) is not None)

def swap_meta(page,name,value):
    tag='<meta name="'+name+'" content="'
    return re.sub(re.escape(tag)+r'[^"]*">',tag+html.escape(value,quote=True)+'">',page,count=1)

def localize_verified_links(markup, locale, path_prefix, published_routes):
    """Keep navigation on the current locale only where approved pages exist.

    Unknown targets intentionally fall back to the English source page; never
    create translated-looking links that lead to a 404 or an unreviewed page.
    """
    prefix = "/" + path_prefix.strip("/")
    def replace(match):
        raw = html.unescape(match.group(2))
        parts = urlsplit(raw)
        if not raw.startswith("/") or raw.startswith("//") or parts.path not in published_routes:
            return match.group(0)
        target = prefix + parts.path
        if parts.query: target += "?" + parts.query
        if parts.fragment: target += "#" + parts.fragment
        return match.group(1) + html.escape(target, quote=True) + match.group(3)
    return re.sub(r'(<a\b[^>]*?\bhref=")([^"]+)(")', replace, markup, flags=re.I)


CONTACT_FORM_TRANSLATIONS=json.loads((ROOT/"data/contact-form-translations.json").read_text(encoding="utf-8"))

def localized_contact_body(original, translated_body, locale):
    """Use the SAME inquiry form fields as English, with translated labels.

    The D1 page translation contains safe static HTML, intentionally without
    a <form>. This build-stage component restores the shared form structure
    without granting D1 untrusted translations the ability to inject forms.
    The existing front-end + server SMTP readiness gates remain authoritative.
    """
    original_body=original.split('<main id="main-content">',1)[1].split("</main>",1)[0]
    english=re.search(r'<form class="form" id="inquiry"[\s\S]*?</form>',original_body)
    if not english:raise RuntimeError("English contact form missing")
    form=english.group(0)
    translations=CONTACT_FORM_TRANSLATIONS[locale]
    # Make stable option values independent of their translated visible text.
    form=re.sub(r'<option>([^<]+)</option>',
        lambda m:'<option value="'+html.escape(html.unescape(m.group(1)),quote=True)+'">'+m.group(1)+'</option>',form)
    def translate_node(match):
        source=html.unescape(match.group(1).strip())
        if not source or source not in translations:return match.group(0)
        original_text=match.group(1)
        before=original_text[:len(original_text)-len(original_text.lstrip())]
        after=original_text[len(original_text.rstrip()):]
        return '>'+before+html.escape(translations[source])+after+'<'
    form=re.sub(r'>([^<>]+)<',translate_node,form)
    form=re.sub(r'(aria-label|placeholder)="([^"]+)"',
        lambda m:m.group(1)+'="'+html.escape(translations.get(html.unescape(m.group(2)),html.unescape(m.group(2))),quote=True)+'"',form)
    # Remove the earlier machine-translation fallback block, not the bilingual
    # company contacts, their data-site-* attributes, or the surrounding grid.
    fallback=r'<section class="section"><div class="shell"><h2>[\s\S]*?</section>(?=</div></div></section>\s*$)'
    updated,count=re.subn(fallback,lambda _:form,translated_body,count=1)
    if count!=1:raise RuntimeError("Localized contact fallback block mismatch for "+locale)
    # The D1-reviewed foreign-language body predates the visible-number design.
    # Reuse the actual English contact number without changing the approved
    # translation or weakening the safe-form/HTML checks.
    source=re.search(r'<a\b(?=[^>]*\bdata-site-whatsapp-number\b)[^>]*>([^<]+)</a>',original_body)
    number=re.search(r'\+\d[\d ]{7,}',html.unescape(source.group(1))) if source else None
    if not number:raise RuntimeError("English contact WhatsApp number missing")
    def add_number(match):
        attrs=match.group(1)
        if "data-site-whatsapp-number" not in attrs:attrs+=" data-site-whatsapp-number"
        label=match.group(2).rstrip()
        arrow=" →" if label.endswith("→") else ""
        if arrow:label=label[:-1].rstrip()
        return attrs+">"+label+" · "+html.escape(number.group(0).strip())+arrow+"</a>"
    updated,count=re.subn(r'(<a\b(?=[^>]*\bdata-site-whatsapp\s)[^>]*)(?:>)([^<]+)</a>',add_number,updated,count=1)
    if count!=1:raise RuntimeError("Translated contact WhatsApp link missing: "+locale)
    return updated

def main():
    if not SNAPSHOT.is_file():
        print("XUYI_LOCALES_SKIPPED: no reviewed D1 snapshot")
        return
    data=json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    if data.get("site")!="xuyi-drinkware-site":raise RuntimeError("Wrong locale source site")
    languages=(data.get("languages") or {}).get("languages",[])
    ready=approved_locales(data)
    # Preserve D1-reviewed UI copy while getting the supported code and URL
    # prefix solely from the registry; no es/pt/ru/tr enumeration here.
    original={r.get("code"):r for r in languages}
    live={r["code"]:{**original.get(r["code"],{}),**r}
          for r in ready if r["code"]!="en"}
    translated={}
    for item in data.get("translations",[]):
        rid=item.get("resourceId","")
        if not rid.startswith("page:"):continue
        route=rid[5:];loc=item.get("locale");fields=item.get("content") or {}
        if not valid_route(route) or loc not in live:continue
        if not all(isinstance(fields.get(k),str) and fields[k].strip() for k in ("title","description","mainHtml")):continue
        body=fields["mainHtml"]
        if len(body)<120 or re.search(r"<\s*(?:script|iframe|object|embed|form|style|link|base|meta|svg|math|template)\b|\bon[a-z-]+\s*=|\bsrcdoc\s*=|(?:javascript|vbscript|data)\s*:",body,re.I):continue
        src=DIST/route.lstrip("/")/"index.html"
        if route=="/":src=DIST/"index.html"
        if src.is_file():translated[(route,loc)]=fields
    # Reviewed source-photo LO additions have their own five-language native
    # content and SEO copy. Existing D1 translations always win, and no older
    # page translation is changed or auto-translated.
    from lo_catalog import LO_PRODUCTS,detail as lo_detail
    from site_renderer import SERIES
    for row in LO_PRODUCTS:
        model=row["model"]
        route="/products/"+row["slug"]+"/"
        src=DIST/route.lstrip("/")/"index.html"
        # Partial isolated translation fixtures contain only selected source
        # routes. Production builds always include all LO pages.
        if not src.is_file():continue
        for loc in live:
            if (route,loc) not in translated:
                copy=row["locales"][loc]
                translated[(route,loc)]={
                    "title":copy["seoTitle"],"description":copy["seoDescription"],
                    "mainHtml":lo_detail(SERIES[model],loc)}
    # Internal G-series PHOTO references have verified pictures but no factory
    # part number or technical specifications; all five locales say so.
    from gallery_catalog import GALLERY,detail as gallery_detail,LABELS as gallery_labels
    for row in GALLERY:
        route="/products/"+row["slug"]+"/"
        src=DIST/route.lstrip("/")/"index.html"
        if not src.is_file():continue
        for loc in live:
            if (route,loc) not in translated:
                name=row["locales"][loc]
                translated[(route,loc)]={
                    "title":name+" | "+row["model"]+" | XUYI",
                    "description":name+". "+gallery_labels[loc][2],
                    "mainHtml":gallery_detail(SERIES[row["model"]],loc)}
    # D1-published catalogs are fixed HTML snapshots; add only the eight
    # source-verified LO cards to their native-language grids, without
    # replacing the approved surrounding content.
    from lo_catalog import catalog_cards
    from gallery_catalog import catalog_cards as gallery_catalog_cards
    for loc in live:
        if ("/",loc) not in translated:
            raise RuntimeError("Refusing to publish "+loc+" without a reviewed localized homepage")
    routes_by_locale = {locale: {route for route, lang in translated if lang == locale}
                        for locale in live}
    created=0
    for (route,loc),fields in translated.items():
        original=(DIST/route.lstrip("/")/"index.html" if route!="/" else DIST/"index.html").read_text(encoding="utf-8")
        if '<main id="main-content">' not in original:continue
        prefix,remainder=original.split('<main id="main-content">',1)
        _,suffix=remainder.split('</main>',1)
        ui=live[loc].get("uiText",{})
        # A small JSON bundle provides translations for the shared JavaScript
        # carousel, catalog filters, FAQ search and inquiry status messages.
        # This also prevents the homepage hero reverting to English on rotation.
        runtime=RUNTIME_UI_TRANSLATIONS.get(loc,{})
        encoded=json.dumps(runtime,ensure_ascii=False,separators=(",",":")).replace("<",r"\u003c")
        prefix=prefix.replace("</head>",'<script type="application/json" id="xuyi-runtime-ui">'+encoded+"</script></head>",1)
        body=(localized_contact_body(original,fields["mainHtml"],loc) if route=="/contact/" else fields["mainHtml"])
        if route.startswith("/blog/"):
            body=localize_blog_timeline(body,original,loc,route)
        if route=="/products/" or route.startswith("/collections/"):
            body=gallery_catalog_cards(body,loc,route)
            body=catalog_cards(body,loc,route)
        if route.startswith("/products/") and route!="/products/":
            # D1 translated bodies replace the English product HTML. Re-add
            # the same reviewed presentation module in this locale, without
            # touching the existing translated descriptions or SKU data.
            from site_renderer import SERIES
            model=route.removeprefix("/products/").strip("/")
            product=next((obj for obj in SERIES.values() if obj["slug"]==model),None)
            if product is None:raise ValueError("Missing material source for "+route)
            body=inject_materials(body,product,loc,route,routes_by_locale[loc])
        # The homepage body is a D1-approved translation of previous English
        # markup. Refresh ONLY the immutable generic hero image asset; leave
        # all user-translated text and model photos unchanged.
        if route=="/":
            from media_quality_guard import upgrade_home_visual
            body=upgrade_home_visual(body,loc)
            prefix,count=re.subn(r'<script type="application/json" id="xuyi-home-banners">[^<]*</script>',
              lambda _:banner_tag(data,loc,routes_by_locale[loc]),prefix,count=1)
            if count!=1:raise RuntimeError("English homepage must have exactly one banner configuration")
            slide=banner_slides(data,loc,routes_by_locale[loc])[0]
            heading=html.escape(slide["title"])+" <span>"+html.escape(slide["highlight"])+"</span>"
            body=re.sub(r'(<h1\b[^>]*\bid="hero-title"[^>]*>).*?(</h1>)',
              lambda m:m.group(1)+heading+m.group(2),body,count=1,flags=re.S)
            body=re.sub(r'(<p\b[^>]*\bid="hero-description"[^>]*>).*?(</p>)',
              lambda m:m.group(1)+html.escape(slide["description"])+m.group(2),body,count=1,flags=re.S)
            body=re.sub(r'(<a\b(?=[^>]*\bid="hero-cta")[^>]*>).*?(</a>)',
              lambda m:m.group(1)+html.escape(slide["cta"])+m.group(2),body,count=1,flags=re.S)
            body=re.sub(r'(<img\b(?=[^>]*\bid="hero-image")[^>]*\balt=")[^"]+(")',
              lambda m:m.group(1)+html.escape(slide["alt"])+m.group(2),body,count=1)
            body=re.sub(r'(<img\b(?=[^>]*\bid="hero-image")[^>]*\bsrc=")[^"]+(")',
              lambda m:m.group(1)+html.escape(slide["img"])+m.group(2),body,count=1)
            body=re.sub(r'(<a\b(?=[^>]*\bid="hero-cta")[^>]*\bhref=")[^"]+(")',
              lambda m:m.group(1)+html.escape(slide["link"])+m.group(2),body,count=1)
        text=translate_chrome(prefix,loc,ui)+'<main id="main-content">'+body+'</main>'+translate_chrome(suffix,loc,ui)
        text=localize_verified_links(text,loc,live[loc].get("pathPrefix",loc),routes_by_locale[loc])
        text=text.replace('<html lang="en">','<html lang="'+loc+'">',1)
        text=re.sub(r'<title>[^<]*</title>','<title>'+html.escape(fields["title"])+'</title>',text,count=1)
        text=swap_meta(text,"description",fields["description"])
        for property_name,value in (("og:title",fields["title"]),("og:description",fields["description"])):
            tag='<meta property="'+property_name+'" content="'+html.escape(value,quote=True)+'">'
            current=r'<meta property="'+property_name+'" content="[^"]*">'
            if re.search(current,text):text=re.sub(current,lambda _:tag,text,count=1)
            else:text=text.replace("</head>",tag+"</head>",1)
        localized="/"+live[loc]["pathPrefix"]+(route if route!="/" else "/")
        localized=re.sub("/+","/",localized)
        canonical=ORIGIN+localized
        text=re.sub(r'<link rel="canonical" href="[^"]*">','<link rel="canonical" href="'+canonical+'">',text,count=1)
        text=re.sub(r'<meta property="og:url" content="[^"]*">','<meta property="og:url" content="'+canonical+'">',text,count=1)
        text=localize_structured_data(text,loc,route,localized,fields,routes_by_locale[loc],live[loc]["pathPrefix"])
        text=polish_product_head(text,loc,route)
        text=correct_reviewed_drinkware_terms(text,loc)
        text=polish_image_alt(text,loc)
        text=apply_media_alts(text,data,loc)
        dest=DIST/localized.lstrip("/")/"index.html";dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(text,encoding="utf-8")
        created+=1
    # Only link routes that really exist in the generated release.
    alternates={}
    for route,loc in translated:
        prefix=live[loc]["pathPrefix"]
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
    # English-only new D1 products/articles must remain publishable BEFORE
    # their foreign translations are approved. A self link + English default
    # is safe; NEVER advertise a foreign locale without its real HTML page.
    # Read the English sitemap rather than guessing source pages or admin URLs.
    english_xml=(DIST/"sitemap.xml").read_text(encoding="utf-8")
    published_prefixes={"/"+entry["pathPrefix"]+"/" for entry in ready if entry["pathPrefix"]}
    english_urls=[
        route for route in re.findall(r"<loc>"+re.escape(ORIGIN)+r"(/[^<]*)</loc>",english_xml)
        if not any(route.startswith(prefix) for prefix in published_prefixes)
    ]
    for route in english_urls:
        if route in alternates:continue
        src=DIST/route.lstrip("/")/"index.html" if route!="/" else DIST/"index.html"
        if not src.is_file():raise RuntimeError("English sitemap URL has no page: "+route)
        content=src.read_text(encoding="utf-8")
        tags=('<link rel="alternate" hreflang="en" href="'+ORIGIN+route+'">'
              '<link rel="alternate" hreflang="x-default" href="'+ORIGIN+route+'">')
        if '<link rel="alternate" hreflang=' in content:
            if content.count(tags)==1:continue # an idempotent second renderer run
            raise RuntimeError("Stale alternates on English-only route: "+route)
        src.write_text(content.replace("</head>",tags+"</head>",1),encoding="utf-8")
    # Extend the existing English sitemap with *real* reviewed routes only.
    # The site-wide noindex gate is independent and remains unchanged.
    sitemap=DIST/"sitemap.xml"
    if alternates and sitemap.is_file():
        xml=sitemap.read_text(encoding="utf-8")
        added=[]
        for route,alts in sorted(alternates.items()):
            for _,url in sorted(alts):
                absolute=ORIGIN+url
                if "<loc>"+html.escape(absolute)+"</loc>" not in xml:
                    added.append(" <url><loc>"+html.escape(absolute)+"</loc></url>")
        if added:
            if "</urlset>" not in xml:raise RuntimeError("Invalid XUYI sitemap: no urlset closing tag")
            xml=xml.replace("</urlset>","\n".join(added)+"\n</urlset>",1)
            sitemap.write_text(xml,encoding="utf-8")
    # Actual published output is authoritative; disabled/draft or missing
    # language pages must not become sitemap/hreflang entries.
    manifest={"schemaVersion":1,"site":"xuyi-drinkware-site","sourceLocale":"en",
              "defaultLocale":"en","origin":ORIGIN,"locales":ready,
              "routes":{lang["code"]:sorted(
                "/"+f.relative_to(DIST/(lang["pathPrefix"] or ".")).as_posix().removesuffix("index.html")
                for f in (DIST/(lang["pathPrefix"] or ".")).rglob("index.html")
                if (lang["code"]!="en" or f.relative_to(DIST).parts[0] not in
                    {x["pathPrefix"] for x in ready if x["code"]!="en"}|{"admin"}))
                for lang in ready}}
    (DIST/"locale-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("XUYI_REVIEWED_LOCALIZED_PAGES",created,"LANGUAGES",sorted(live),"ALTERNATE_SETS",len(alternates))

if __name__=="__main__":main()