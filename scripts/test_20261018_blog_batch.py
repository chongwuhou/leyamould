from pathlib import Path
import html,json,re,sys
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from site_renderer import SERIES
from sitemap_modification import source_lastmod
from scripts.prepare_blog_release_20261018 import GUIDES,MATRICES,TRANS,SLUGS,LOCALES,EVIDENCE,UI
GUIDE_LIST=json.loads((ROOT/"data/blog-guides.json").read_text(encoding="utf8"))
MODELS={str(x["slug"]) for x in SERIES.values()}

def webp_dimensions(path):
 data=path.read_bytes()
 assert data[:4]==b"RIFF" and data[8:12]==b"WEBP",(path,"invalid WebP RIFF header")
 kind=data[12:16]
 if kind==b"VP8X":
  return int.from_bytes(data[24:27],"little")+1,int.from_bytes(data[27:30],"little")+1
 if kind==b"VP8L":
  assert data[20]==0x2f,(path,"invalid VP8L signature")
  bits=int.from_bytes(data[21:25],"little")
  return (bits&0x3fff)+1,((bits>>14)&0x3fff)+1
 if kind==b"VP8 ":
  offset=data.find(b"\x9d\x01\x2a",20,40)
  assert offset>=0,(path,"VP8 key-frame signature missing")
  return int.from_bytes(data[offset+3:offset+5],"little")&0x3fff,int.from_bytes(data[offset+5:offset+7],"little")&0x3fff
 raise AssertionError((path,"unsupported WebP chunk",kind))
assert len(GUIDE_LIST)>=25
assert set(MATRICES)=={x["slug"] for x in GUIDE_LIST}
assert set(TRANS)==set(SLUGS)
covers=[]
for slug in SLUGS:
 post=GUIDES[slug]
 word_count=len(post["intro"].split())+sum(len(x["paragraph"].split()) for x in post["sections"])
 assert word_count>=600,(slug,word_count)
 assert len(post["sections"])==7 and len(post["checklist"])==10 and len(post["faqs"])==4
 assert len(post["related"])==3 and len(set(post["related"]))==3
 assert all(x in GUIDES and x!=slug for x in post["related"])
 assert len(post["product_notes"])==3 and len({x["sku"] for x in post["product_notes"]})==3
 assert all(x["sku"] in MODELS for x in post["product_notes"])
 assert len(MATRICES[slug]["rows"])==6 and len(MATRICES[slug]["links"])==3
 assert source_lastmod("/blog/"+slug+"/")=="2026-10-18"
 assert post["updated"]=="2026-10-18" and post["primary_keyword"] and post["secondary_keywords"]
 assert post["cover"].startswith("/assets/blog/")
 cover=ROOT/post["cover"].lstrip("/")
 assert cover.is_file(),cover
 assert webp_dimensions(cover)==(1512,1040),(slug,webp_dimensions(cover))
 assert 30000<cover.stat().st_size<350000,(slug,cover.stat().st_size)
 covers.append(post["cover"])
 assert slug in EVIDENCE and len(EVIDENCE[slug]["sources"])>=1
 for locale in ["en",*LOCALES]:
  prefix="" if locale=="en" else "/"+locale
  dest=ROOT/"dist"/("" if locale=="en" else locale)/"blog"/slug/"index.html"
  assert dest.is_file(),dest
  document=dest.read_text(encoding="utf8")
  assert '<main id="main-content">' in document
  main=document.split('<main id="main-content">',1)[1].split("</main>",1)[0]
  canonical="https://xuyibottles.com"+prefix+"/blog/"+slug+"/"
  localized=post if locale=="en" else TRANS[slug][locale]
  expected_title=post["title"] if locale=="en" else localized["title"]
  expected_description=post["description"] if locale=="en" else localized["description"]
  assert f"<title>{html.escape(expected_title)}</title>" in document,(locale,slug,"title")
  assert 'name="description" content="'+html.escape(expected_description,quote=True)+'"' in document,(locale,slug,"description")
  assert f'<link rel="canonical" href="{canonical}">' in document,(locale,slug,"canonical")
  assert 'name="robots" content="index,follow"' in document,(locale,slug,"robots")
  assert f'content="https://xuyibottles.com{post["cover"]}"' in document,(locale,slug,"cover metadata")
  assert main.count('class="blog-editorial__product-link"')==3,(locale,slug,"product links")
  assert main.count('class="blog-related__item"')==3,(locale,slug,"related links")
  assert main.count('class="blog-buyer-matrix"')==1,(locale,slug,"decision matrix")
  assert main.count("<details>")==4,(locale,slug,"FAQ")
  faq_title="Frequently asked questions" if locale=="en" else UI[locale]["faq"]
  assert f'<h2>{html.escape(faq_title)}</h2>' in main,(locale,slug,"localized FAQ section")
  if locale!="en":
   assert html.escape(TRANS[slug][locale]["faqs.3.question"]) in main,(locale,slug,"fourth translated FAQ")
  assert main.count('id="primary-sources"')==1,(locale,slug,"source references")
  for note in post["product_notes"]:
   assert f'href="{prefix}/products/{note["sku"]}/"' in main,(locale,slug,note["sku"])
  for related in post["related"]:
   assert f'href="{prefix}/blog/{related}/"' in main,(locale,slug,related)
  for _,href in post["inline_links"]:
   assert f'href="{prefix}{href}"' in main,(locale,slug,href)
  for ref in EVIDENCE[slug]["sources"]:
   assert ref["url"] in main,(locale,slug,ref["url"])
  for lang in ["en","es","pt","ru","tr","x-default"]:
   assert f'hreflang="{lang}"' in document,(locale,slug,lang)
  if locale!="en":
   translated=TRANS[slug][locale]
   assert html.escape(translated["title"]) in main,(locale,slug,"localized title")
   assert html.escape(translated["sources.title"]) in main,(locale,slug,"localized sources")
   assert translated["intro"]!=post["intro"]
   for i in range(7):
    assert html.escape(translated[f"sections.{i}.heading"]) in main,(locale,slug,i)
    assert len(translated[f"sections.{i}.paragraph"])>120
  else:
   assert 'dateModified":"2026-10-18' in document,(slug,"schema modified date")
assert len(set(covers))==3
for locale in ["",*LOCALES]:
 path=ROOT/"dist"/locale/"blog"/"index.html"
 page=path.read_text(encoding="utf8")
 for slug in SLUGS:
  assert "/"+("" if not locale else locale+"/")+"blog/"+slug+"/" in page,(locale,slug,"index card")
tree=ET.parse(ROOT/"dist"/"sitemap.xml")
ns={"sm":"http://www.sitemaps.org/schemas/sitemap/0.9"}
sitemap={x.findtext("sm:loc",namespaces=ns):x.findtext("sm:lastmod",namespaces=ns) for x in tree.findall("sm:url",ns)}
assert len(sitemap)>=800,("unexpected sitemap loss",len(sitemap))
for slug in SLUGS:
 for locale in ["",*LOCALES]:
  url="https://xuyibottles.com/"+(locale+"/" if locale else "")+"blog/"+slug+"/"
  assert sitemap.get(url)=="2026-10-18",(url,sitemap.get(url))
assert sitemap.get("https://xuyibottles.com/blog/") in ("2026-10-18","2026-10-19")
robots=(ROOT/"dist"/"robots.txt").read_text(encoding="utf8")
assert "Allow: /" in robots and "Disallow: /admin/" in robots and "Sitemap: https://xuyibottles.com/sitemap.xml" in robots
# CI fetches this snapshot from the live XUYI D1 CMS before building.
# Verify that the actual saved translations and appended index cards—not only
# generated static HTML—contain the reviewed article content exactly once.
snapshot_path=ROOT/"_local_ops"/"build-snapshot.json"
assert snapshot_path.is_file(),"Build must use a fresh authenticated XUYI D1 snapshot"
snapshot=json.loads(snapshot_path.read_text(encoding="utf8"))
translation_rows=snapshot.get("translations",[])
for slug in SLUGS:
 for locale in LOCALES:
  row=next((item for item in translation_rows if item.get("resourceId")=="page:/blog/"+slug+"/" and item.get("locale")==locale),None)
  assert row is not None,(slug,locale,"missing D1 translation")
  body=row.get("content",{}).get("mainHtml","")
  assert len(body)>5000,(slug,locale,"D1 article body missing")
  assert body.count('id="primary-sources"')==1,(slug,locale,"D1 evidence section")
  assert body.count('class="blog-editorial__product-link"')==3,(slug,locale,"D1 contextual product links")
  assert body.count('class="blog-related__item"')==3,(slug,locale,"D1 related articles")
  assert body.count('class="blog-buyer-matrix"')==1,(slug,locale,"D1 decision matrix")
  assert body.count("<details>")==4,(slug,locale,"D1 FAQs")
  for ref in EVIDENCE[slug]["sources"]:assert ref["url"] in body,(slug,locale,ref["url"])
for locale in LOCALES:
 row=next((item for item in translation_rows if item.get("resourceId")=="page:/blog/" and item.get("locale")==locale),None)
 assert row is not None,(locale,"missing D1 blog index")
 body=row.get("content",{}).get("mainHtml","")
 cards=re.findall(r'<article class="news-card">.*?</article>',body,re.S)
 for slug in SLUGS:
  matches=[card for card in cards if "/blog/"+slug+"/" in card]
  assert len(matches)==1,(locale,slug,"D1 index card count",len(matches))
  assert matches[0].count('href="/blog/'+slug+'/"')==3,(locale,slug,"card image/title/read links")
print("XUYI_20261018_D1_SNAPSHOT_OWNER_TRANSLATIONS_INDEX_CARDS_PASSED")
print("XUYI_20261018_THREE_BLOGS_FIVE_LOCALES_SEO_LINKS_IMAGES_SITEMAP_PASSED")

