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
sys.path.insert(0,str(ROOT))
DIST=ROOT/"dist"
ORIGIN="https://xuyibottles.com"
manifest=json.loads((DIST/"locale-manifest.json").read_text(encoding="utf-8"))
assert manifest["site"]=="xuyi-drinkware-site" and manifest["sourceLocale"]=="en"
LOCALES=tuple(lang["code"] for lang in manifest["locales"])
PREFIX={lang["code"]:lang["pathPrefix"] for lang in manifest["locales"]}
PREFIX_TO_CODE={prefix:code for code,prefix in PREFIX.items() if prefix}
config=json.loads((ROOT/"deployment/site.config.json").read_text(encoding="utf-8"))
assert config["localizationFrameworkVersion"]==2
indexable=config["site"].get("indexingApproved") is True
meta=json.loads((DIST/"build-meta.json").read_text(encoding="utf-8"))
assert meta["noindex"] is (not indexable)
errors=[]
warnings=defaultdict(list)
records={}
per_lang_title=defaultdict(dict)
per_lang_description=defaultdict(dict)
def all_published_documents():
    seen=set()
    for file in sorted(DIST.rglob("index.html")):
        rel=file.relative_to(DIST).as_posix()
        seen.add(rel)
        yield rel,file.read_text(encoding="utf-8")
    # Exact route copies in the reviewed R2 overflow bundles remain public
    # canonical pages even when removed from Cloudflare Pages' file budget.
    source=ROOT/"_local_ops/model-overflow"
    manifest_file=source/"manifest.json"
    if not manifest_file.is_file():return
    storage=json.loads(manifest_file.read_text(encoding="utf-8"))
    if storage.get("site")!="xuyi-drinkware-site":raise RuntimeError("Wrong R2 overflow identity")
    for item in storage.get("objects",[]):
        bundle=json.loads((source/item["key"]).read_text(encoding="utf-8"))
        if bundle.get("site")!="xuyi-drinkware-site":raise RuntimeError("Wrong R2 HTML bundle")
        for route,document in bundle["routes"].items():
            rel=route.lstrip("/")+"index.html"
            if rel in seen:raise RuntimeError("Static and overflow page duplicated: "+rel)
            seen.add(rel)
            yield rel,document
for rel,html in all_published_documents():
    if rel.startswith("admin/"):continue
    locale=PREFIX_TO_CODE.get(rel.split("/")[0],"en")
    route="/"+rel.removesuffix("index.html")
    expected=ORIGIN+route
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
    base_route=route if locale=="en" else route[len("/"+PREFIX[locale]):]
    if hrefs.get("x-default")!=ORIGIN+base_route:errors.append((route,"wrong x-default"))
    expected_codes={lang for lang in LOCALES if base_route in manifest["routes"].get(lang,[])}
    if set(hrefs)!=expected_codes|{"x-default"}:
        errors.append((route,"invalid published-language set",sorted(hrefs),sorted(expected_codes)))
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
                # Homepage and product FAQs are only valid if CMS language matches.
                if route=="/"+PREFIX[locale].strip("/")+"/":
                    if len(obj.get("mainEntity",[]))!=5 or 'class="dark-faq"' not in html:
                        errors.append((route,"Localized homepage FAQPage mismatch"))
                elif re.fullmatch(r"/(?:es|pt|ru|tr)/products/[a-z0-9_-]+/",route):
                    from seo_structured_components import visible_faq
                    pairs=visible_faq(html)
                    if [x.get("name") for x in obj.get("mainEntity",[])]!=[q for q,a in pairs]:
                        errors.append((route,"Product FAQPage differs from visible translation"))
                elif re.fullmatch(r"/"+re.escape(PREFIX[locale])+r"/blog/[a-z0-9-]+/",route):
                    from seo_structured_components import visible_blog_faq
                    pairs=visible_blog_faq(html)
                    if [x.get("name") for x in obj.get("mainEntity",[])]!=[q for q,a in pairs]:
                        errors.append((route,"Blog FAQPage differs from visible translation"))
                else:errors.append((route,"FAQPage on unsupported translated page"))
    records[expected]={"route":route,"locale":locale,"title":title,"description":desc,"hreflang":hrefs}
expected_published=sum(len(manifest["routes"].get(code,[])) for code in LOCALES)
if len(records)!=expected_published:
    errors.append(("manifest","published URL coverage mismatch",len(records),expected_published))
if len(manifest["routes"].get(manifest["defaultLocale"],[]))<130:
    errors.append(("manifest","English source catalog unexpectedly lost pages"))
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
    f=DIST/(PREFIX[locale] or ".")/"index.html"
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
