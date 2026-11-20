#!/usr/bin/env python3
"""Validate XUYI localized release after the reviewed D1 snapshot build."""
from pathlib import Path
import json,re,xml.etree.ElementTree as ET,os,sys

ROOT=Path(__file__).resolve().parent.parent
os.environ.setdefault("LEYA_BUILD_SNAPSHOT",str(ROOT/"_local_ops/build-snapshot.json"))
sys.path.insert(0,str(ROOT))
from site_renderer import NEW_PRODUCT_COUNT
DIST=ROOT/"dist"
info=json.loads((DIST/"build-meta.json").read_text(encoding="utf8"))
indexable=not info["noindex"]
sitemap=DIST/"sitemap.xml"
assert sitemap.is_file()
ET.parse(sitemap)
result={}
manifest=json.loads((DIST/"locale-manifest.json").read_text(encoding="utf8"))
published=[lang for lang in manifest["locales"] if lang["code"]!=manifest["defaultLocale"]]
for language in published:
 locale=language["code"]
 folder=DIST/language["pathPrefix"]
 if not folder.is_dir():
  result[locale]=0
  continue
 files=list(folder.rglob("index.html"))
 assert (folder/"index.html").is_file(),(locale,"missing locale home")
 assert len(files)>=1,(locale,"no approved translated pages")
 if locale in ("es","pt","ru","tr"):
  assert len(files)>=120,(locale,"legacy language unexpectedly lost published pages",len(files))
 for f in files:
  html=f.read_text(encoding="utf8")
  route="/"+f.relative_to(DIST).as_posix().removesuffix("index.html")
  url="https://leyamould.com"+route
  assert '<html lang="'+locale+'">' in html,(locale,route)
  assert '<link rel="canonical" href="'+url+'">' in html,(locale,route)
  assert '<meta name="robots" content="'+("index,follow" if indexable else "noindex,nofollow")+'">' in html,(locale,route)
  assert 'hreflang="en"' in html and 'hreflang="'+locale+'"' in html,(locale,route)
  main=html.split('<main id="main-content">',1)[1].split('</main>',1)[0]
  assert '{{' not in main and '}}' not in main,(locale,route)
  assert '<main id="main-content">' in html and '</main>' in html,(locale,route)
  segments=f.relative_to(folder).parts
  if len(segments)==3 and segments[0]=="products" and segments[1].isdigit():
   model=segments[1]
   title=re.search(r"<title>([^<]+)</title>",html)
   desc=re.search(r'<meta name="description" content="([^"]+)"',html)
   assert title and title.group(1).count(model)==1,(locale,route,"SEO model repeated")
   assert desc and desc.group(1).count(model)==1,(locale,route,"description model repeated")
  if route=="/"+language["pathPrefix"]+"/":
   assert ">FAQ<" not in html,(locale,"untranslated footer FAQ")
  if locale=="ru" and route.endswith("/products/2501/"):
   main=html.split('<main id="main-content">',1)[1].split('</main>',1)[0]
   assert len(re.findall('[\u0400-\u04ff]',main))>=150,"Cyrillic product copy missing"
  if route.endswith("/contact/"):
   assert 'href="mailto:Janey@xuyibottles.com"' in html,"Localized contact email must work"
   assert html.count('id="inquiry"')==1,(locale,"contact form must match English")
   assert 'data-site-email' in html and 'data-site-whatsapp' in html,(locale,"D1 contacts missing")
   for required in ('company','email','model','quantity','country','type','material','requirements','consent','website'):
    assert 'name="'+required+'"' in html,(locale,"contact form field",required)
   assert '<button class="button" type="submit">' in html,(locale,"submit action missing")
 # The localized Blog index must contain every published D1 slug in the same order,
 # including articles added after the older page:/blog/ override was saved.
 blog_index=folder/"blog"/"index.html"
 assert blog_index.is_file(),(locale,"missing localized Blog index")
 blog_html=blog_index.read_text(encoding="utf8")
 blog_main=blog_html.split('<main id="main-content">',1)[1].split('</main>',1)[0]
 blog_cards=re.findall(r'<article class="news-card">[\s\S]*?</article>',blog_main,re.I)
 expected_blog=[str(row.get("slug")) for row in json.loads((ROOT/"_local_ops/build-snapshot.json").read_text(encoding="utf8")).get("blogPosts",[])
                if row.get("status")=="published"]
 actual_blog=[]
 for card in blog_cards:
  found=set(re.findall(r'href="/'+re.escape(locale)+r'/blog/([a-z0-9]+(?:-[a-z0-9]+)*)/"',card))
  assert len(found)==1,(locale,"localized Blog card identity",found)
  actual_blog.append(next(iter(found)))
 assert actual_blog==expected_blog,(locale,"localized Blog index is not complete or in D1 order",len(actual_blog),len(expected_blog))
 result[locale]=len(files)
# Match the actual approved D1 snapshot, not only a permissive minimum.
snapshot=ROOT/"_local_ops/build-snapshot.json"
if snapshot.is_file():
 data=json.loads(snapshot.read_text(encoding="utf8"))
 if data.get("site")=="leyamould":
  for locale in result:
   expected=sum(1 for row in data.get("translations",[]) if
     row.get("locale")==locale and str(row.get("resourceId","")).startswith("page:"))
   if expected:
    # Eight reviewed LO source-image products are generated in five
    # languages alongside, not instead of, the D1-managed translations.
    lo_products=json.loads((ROOT/"data/lo-products.json").read_text(encoding="utf8"))["products"]
    gallery_products=json.loads((ROOT/"data/gallery-reference-products.json").read_text(encoding="utf8"))["items"]
    added=sum(1 for row in lo_products+gallery_products if
      (DIST/locale/"products"/row["slug"]/"index.html").is_file() and
      not any(item.get("locale")==locale and item.get("resourceId")=="page:/products/"+row["slug"]+"/"
              for item in data.get("translations",[])))
    # Include the 153 new source-verified factory products generated in every locale.
    # At most one legacy alias may collapse onto an existing canonical route.
    missing_or_collapsed=(expected+added+NEW_PRODUCT_COUNT)-result[locale]
    assert 0 <= missing_or_collapsed <= 1, (locale,"D1 + LO + gallery + new factory product translation count mismatch",result[locale],expected,added,NEW_PRODUCT_COUNT,missing_or_collapsed)
if sum(result.values()):
 assert all(result.values()),"Partial language release not allowed"
 assert sum(result.values())>=len(result),"Expected approved localized pages"
print("XUYI_LOCALIZED_RELEASE_PASSED",json.dumps(result,sort_keys=True))