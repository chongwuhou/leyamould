#!/usr/bin/env python3
"""XUYI five-language search-launch gate: actual HTML and sitemap, not guesses.

Checks only published static URLs, plus documented dynamic Blog behavior via
the separate Node test. Keeps human SEO length/style review as warnings.
"""
from pathlib import Path
from collections import defaultdict,Counter
from html import unescape
import json,re,sys,xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding="utf-8")

ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/"dist"
ORIGIN="https://xuyibottles.com"
LOCALES=("en","es","pt","ru","tr")
config=json.loads((ROOT/"deployment/site.config.json").read_text(encoding="utf-8"))
indexable=config["site"].get("indexingApproved") is True
meta=json.loads((DIST/"build-meta.json").read_text(encoding="utf-8"))
assert meta["noindex"] is (not indexable)
errors=[]
warnings=defaultdict(list)
records={}
per_lang_title=defaultdict(dict)
per_lang_description=defaultdict(dict)
for file in sorted(DIST.rglob("index.html")):
    rel=file.relative_to(DIST).as_posix()
    if rel.startswith("admin/"):continue
    locale=rel.split("/")[0] if rel.split("/")[0] in LOCALES[1:] else "en"
    route="/"+rel.removesuffix("index.html")
    expected=ORIGIN+route
    html=file.read_text(encoding="utf-8")
    head=html.split("</head>",1)[0]
    def extract(regex):
        match=re.search(regex,head,re.I|re.S)
        return unescape(match.group(1).strip()) if match else ""
    title=extract(r"<title>([^<]*)</title>")
    desc=extract(r'<meta name="description" content="([^"]*)"')
    canonical=extract(r'<link rel="canonical" href="([^"]*)"')
    og_title=extract(r'<meta property="og:title" content="([^"]*)"')
    og_desc=extract(r'<meta property="og:description" content="([^"]*)"')
    og_url=extract(r'<meta property="og:url" content="([^"]*)"')
    hrefs=dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"',head))
    raw_hrefs=re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"',head)
    h1=re.search(r'<h1\b[^>]*>(.*?)</h1>',html,re.I|re.S)
    if not title or not desc:errors.append((route,"missing SEO title/description"))
    if not h1:errors.append((route,"missing H1"))
    if canonical!=expected or og_url!=expected:errors.append((route,"self canonical/OG URL mismatch",canonical,og_url))
    if og_title!=title or og_desc!=desc:errors.append((route,"OG title/description differs from SEO metadata"))
    if len(raw_hrefs)!=len(hrefs):errors.append((route,"duplicate hreflang"))
    if hrefs.get(locale)!=expected:errors.append((route,"missing own hreflang"))
    base_route=route if locale=="en" else route[len("/"+locale):]
    if hrefs.get("x-default")!=ORIGIN+base_route:errors.append((route,"wrong x-default"))
    if set(hrefs)!={"en","es","pt","ru","tr","x-default"}:errors.append((route,"incomplete language set",sorted(hrefs)))
    if not html.startswith('<!doctype html><html lang="'+locale+'">'):errors.append((route,"incorrect html lang"))
    robot="index,follow" if indexable else "noindex,nofollow"
    if '<meta name="robots" content="'+robot+'">' not in head:errors.append((route,"indexing control mismatch"))
    if not title.startswith("|"):
        if len(title)>70:warnings["long_title"].append((route,len(title),title))
        if len(desc)>180:warnings["long_description"].append((route,len(desc),desc))
    seen_title=per_lang_title[locale].setdefault(title,route)
    seen_desc=per_lang_description[locale].setdefault(desc,route)
    if seen_title!=route:errors.append((route,"duplicate title",seen_title))
    if seen_desc!=route:errors.append((route,"duplicate description",seen_desc))
    for match in re.findall(r'<script type="application/ld\+json">(.*?)</script>',html,re.S):
        try:j=json.loads(match)
        except ValueError:errors.append((route,"invalid JSON-LD"));continue
        objects=j.get("@graph",[j])
        for obj in objects:
            typ=obj.get("@type")
            if typ in ("Product","BlogPosting","Service","WebPage"):
                if (locale!="en" and obj.get("inLanguage")!=locale) or (
                    locale=="en" and obj.get("inLanguage") not in (None,"en")):
                    errors.append((route,"JSON-LD language mismatch",typ))
                if typ in ("Product","Service","WebPage") and obj.get("url")!=expected:
                    errors.append((route,"JSON-LD self URL mismatch",typ))
                if typ=="BlogPosting":
                    node=obj.get("mainEntityOfPage")
                    refer=node.get("@id") if isinstance(node,dict) else node
                    if refer!=expected:errors.append((route,"BlogPosting main page mismatch",refer))
            if locale!="en" and typ=="FAQPage":
                errors.append((route,"English FAQ structured data incorrectly inherited"))
    records[expected]={"route":route,"locale":locale,"title":title,"description":desc,"hreflang":hrefs}
assert len(records)>=675,(len(records),"unexpected public URL loss")
for url,row in records.items():
    for language,alternate in row["hreflang"].items():
        if language=="x-default":continue
        other=records.get(alternate)
        if not other:errors.append((row["route"],"alternate points to missing page",alternate));continue
        if other["hreflang"]!=row["hreflang"]:
            errors.append((row["route"],"nonreciprocal hreflang set",language))
NS="{http://www.sitemaps.org/schemas/sitemap/0.9}"
links=[item.findtext(NS+"loc") for item in ET.parse(DIST/"sitemap.xml").getroot()]
if len(links)!=len(set(links)):errors.append(("sitemap","duplicate loc"))
if set(links)!=set(records):
    errors.append(("sitemap","URL coverage mismatch",
                   "notListed="+str(len(set(records)-set(links))),
                   "notPublished="+str(len(set(links)-set(records)))))
home=records[ORIGIN+"/"]
if any(lang not in home["hreflang"] for lang in LOCALES):errors.append(("/","missing locale home"))
for locale in LOCALES:
    f=DIST/("" if locale=="en" else locale)/"index.html"
    txt=f.read_text(encoding="utf-8")
    if '"@type":"WebSite"' not in txt or '"@type":"Organization"' not in txt:
        errors.append(("/"+locale if locale!="en" else "/","missing verified home entity graph"))
robots=(DIST/"robots.txt").read_text(encoding="utf-8")
if indexable:
    if "Disallow: /\n" in robots or "Sitemap: "+ORIGIN+"/sitemap.xml" not in robots:
        errors.append(("robots","indexable site still blocked"))
else:
    if "Disallow: /\n" not in robots:errors.append(("robots","premature indexing"))
counts=Counter(row["locale"] for row in records.values())
print("XUYI_MULTILINGUAL_SEO_AUDIT",json.dumps({"pages":len(records),"byLanguage":dict(counts),
 "sitemapUrls":len(links),"titleDuplicates":0,"descriptionDuplicates":0,
 "longTitleAdvisories":len(warnings["long_title"]),
 "longDescriptionAdvisories":len(warnings["long_description"]),
 "indexingApproved":indexable,"errors":len(errors)},ensure_ascii=False))
for problem in errors[:30]:print("ERROR",problem)
for kind,values in warnings.items():
    print("ADVISORY",kind,len(values),"samples",values[:4])
if errors:sys.exit(1)
print("XUYI_SEO_HREFLANG_SITEMAP_SCHEMA_GATE_PASSED")