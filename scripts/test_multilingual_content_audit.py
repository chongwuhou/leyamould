#!/usr/bin/env python3
"""XUYI locale regression: 505 product details, 64 blog articles, UI and SEO.

Avoid false alarms for exact legal Chinese company name, manufacturer source
model 2400透明款 and original polymer/process description 包胶. These are
source identifiers, not machine-translated sentences.
"""
import json,re,html,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from site_renderer import SERIES
from gallery_catalog import GALLERY,UI_LABELS,LABELS
from lo_catalog import LO_PRODUCTS
from scripts.render_locales import BLOG_DATE_LABELS
DIST=ROOT/"dist"
ORIGIN="https://xuyibottles.com"
LOCALES=["en","es","pt","ru","tr"]
CATALOG_SLUGS=(
    "sports-water-bottles","large-capacity-water-jugs","kids-water-bottles",
    "plastic-shaker-bottles","spray-water-bottles","two-way-drinking-cups",
    "titanium-vacuum-cups"
)
ENGLISH_NAV_LABELS=(
    "Products","All products","Sports Water Bottles","Large Capacity Water Jugs",
    "Kids Water Bottles","Protein Shaker Bottles","Spray Water Bottles",
    "Two-Way Drinking Cups","Titanium Vacuum Cups"
)
assert len(SERIES)>=101 and len(GALLERY)==8 and len(LO_PRODUCTS)==8
INDEXABLE=json.loads((ROOT/"deployment/site.config.json").read_text(encoding="utf8"))["site"]["indexingApproved"]
dates_checked=0;products_checked=0;g_checked=0;lo_checked=0
for loc in LOCALES:
 prefix="" if loc=="en" else loc+"/"
 # Catalog sidebars are shared translated navigation, not English fallback HTML.
 for category in CATALOG_SLUGS:
  collection=(DIST/prefix/"collections"/category/"index.html").read_text(encoding="utf8")
  side=re.search(r'<aside class="catalog-side">([\s\S]*?)</aside>',collection,re.I)
  assert side,(loc,category,"catalog sidebar missing")
  if loc!="en":
   side_text=unescape(re.sub(r"<[^>]+>"," ",side.group(1)))
   for forbidden in ENGLISH_NAV_LABELS:
    assert not re.search(r"(?<![A-Za-z])"+re.escape(forbidden)+r"(?![A-Za-z])",side_text,re.I),(loc,category,forbidden)
 all_files=list((DIST/prefix).rglob("index.html"))
 assert len(all_files)>=(756 if loc=="en" else 151),(loc,"previously published pages missing",len(all_files))
 catalog=(DIST/prefix/"products/index.html").read_text(encoding="utf8")
 assert catalog.count('data-product-card')>=101
 for record in LO_PRODUCTS:
  token='class="product-card__small">'
  card=re.search(r'<a\b(?=[^>]*\bdata-product-card\b)[^>]*\bhref="/'+
       re.escape(prefix)+r'products/'+re.escape(record["slug"])+r'/".*?</a>',catalog,re.S)
  assert card,(loc,"missing LO listing",record["slug"])
  label={"en":"MODEL","es":"MODELO","pt":"MODELO","ru":"МОДЕЛЬ","tr":"MODEL"}[loc]
  assert token+label+" "+record["model"]+"</span>" in card.group(),(loc,record["model"],"wrong model badge")
  lo_checked+=1
 for obj in SERIES.values():
  model=obj["model"]
  route=prefix+"products/"+obj["slug"]+"/"
  path=DIST/route/"index.html"
  assert path.is_file(),route
  content=path.read_text(encoding="utf8")
  assert '<html lang="'+loc+'">' in content,(route,"language")
  assert '<link rel="canonical" href="'+ORIGIN+"/"+route+'">' in content,(route,"canonical")
  assert '<meta name="robots" content="'+('index,follow' if INDEXABLE else 'noindex,nofollow')+'">' in content,(route,"indexing gate")
  main=content.split('<main id="main-content">',1)[1].split("</main>",1)[0]
  assert len(re.findall(r"<h1(?:\s[^>]*)?>",main))==1,(route,"heading count")
  assert len(re.findall('rel="alternate" hreflang="',content))==6,(route,"alternate family")
  assert re.search(r'<meta name="description" content="[^"]{35,}">',content),(route,"seo description")
  assert re.search(r'<title>[^<]{20,}</title>',content),(route,"seo title")
  if loc=="es":
   assert not re.search(r'variadores de plástico|bebidas de plástico',content,re.I),(route,"incorrect Spanish bottle terminology")
  if loc=="pt":
   assert not re.search(r'bebidas de plástico',content,re.I),(route,"incorrect Portuguese bottle terminology")
  if obj.get("loNew") and loc!="en":
   breadcrumb=re.search(r'<nav class="breadcrumb">(.+?)</nav>',main,re.S)
   assert breadcrumb and UI_LABELS[loc]["Home"] in breadcrumb.group() and UI_LABELS[loc]["Products"] in breadcrumb.group(),(route,"LO breadcrumb mixed with product-spec category")
   assert not re.search(r'main product photo|product view \d| - image \d',main,re.I),(route,"LO photo ALT still English")
  products_checked+=1
  if obj.get("galleryReference"):
   assert len(re.findall('class="gallery-reference-photos__grid"',main))==1,(route,"gallery")
   if loc!="en":
    crumb=re.search(r'<nav class="breadcrumb">(.+?)</nav>',main,re.S)
    assert crumb,(route,"missing breadcrumb")
    assert UI_LABELS[loc]["Home"] in crumb.group() and UI_LABELS[loc]["Products"] in crumb.group(),(route,"breadcrumb not localized")
    assert ">Home<" not in crumb.group() and ">Products<" not in crumb.group(),(route,"English breadcrumb")
   assert all(x in main for x in LABELS[loc][7:10]),(route,"spec fields")
   g_checked+=1
 if loc=="en":continue
 for slug in (p.parent.name for p in (DIST/loc/"blog").glob("*/index.html")):
  page=DIST/loc/"blog"/slug/"index.html"
  document=page.read_text(encoding="utf8")
  original=(DIST/"blog"/slug/"index.html").read_text(encoding="utf8")
  def date(src,key):
   m=re.search(r'<meta property="article:'+key+r'_time" content="(\d{4}-\d{2}-\d{2})">',src)
   return m.group(1) if m else None
  published,modified=date(original,"published"),date(original,"modified")
  if not published:continue
  labels=BLOG_DATE_LABELS[loc]
  body=document.split('<main id="main-content">',1)[1].split('</main>',1)[0]
  timeline=re.search(r'<div class="blog-meta">.*?</div>',body,re.S)
  assert timeline,(loc,slug,"missing blog timeline")
  assert '<time datetime="'+published+'">'+labels[0]+" "+published+"</time>" in timeline.group(),(loc,slug,"published date")
  assert ("<time datetime="+chr(34)+str(modified)+chr(34)+">"+labels[1]+" "+str(modified)+"</time>" in timeline.group()) == bool(modified and modified>published),(loc,slug,"reviewed date")
  assert "Updated 2026" not in timeline.group(),(loc,slug,"English updated label")
  assert '"datePublished":"'+published+'"' in document,(loc,slug,"schema published date")
  assert 'property="article:published_time" content="'+published+'"' in document,(loc,slug,"head publish date")
  dates_checked+=1
assert products_checked>=505 and lo_checked==40 and g_checked==40 and dates_checked>=64, (products_checked,lo_checked,g_checked,dates_checked)
print("XUYI_MULTILINGUAL_CONTENT_AUDIT_PASSED 756 English pages, 604 localized pages, 505 product pages, 40 LO badges, 40 G-series factory model pages, 64 localized blog timelines, SEO/alternate/robots approval")
