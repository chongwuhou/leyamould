#!/usr/bin/env python3
"""Validate XUYI localized release after the reviewed D1 snapshot build."""
from pathlib import Path
import json,re,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/"dist"
info=json.loads((DIST/"build-meta.json").read_text(encoding="utf8"))
sitemap=DIST/"sitemap.xml"
assert sitemap.is_file()
ET.parse(sitemap)
result={}
for locale in ("es","pt","ru","tr"):
 folder=DIST/locale
 if not folder.is_dir():
  result[locale]=0
  continue
 files=list(folder.rglob("index.html"))
 assert (folder/"index.html").is_file(),(locale,"missing locale home")
 assert len(files)>=120,(locale,"insufficient translated pages",len(files))
 for f in files:
  html=f.read_text(encoding="utf8")
  route="/"+f.relative_to(DIST).as_posix().removesuffix("index.html")
  url="https://xuyibottles.com"+route
  assert '<html lang="'+locale+'">' in html,(locale,route)
  assert '<link rel="canonical" href="'+url+'">' in html,(locale,route)
  assert '<meta name="robots" content="noindex,nofollow">' in html,(locale,route)
  assert 'hreflang="en"' in html and 'hreflang="'+locale+'"' in html,(locale,route)
  main=html.split('<main id="main-content">',1)[1].split('</main>',1)[0]
  assert '{{' not in main and '}}' not in main,(locale,route)
  assert '<main id="main-content">' in html and '</main>' in html,(locale,route)
  if locale=="ru" and route.endswith("/products/2501/"):
   main=html.split('<main id="main-content">',1)[1].split('</main>',1)[0]
   assert len(re.findall('[\u0400-\u04ff]',main))>=150,"Cyrillic product copy missing"
  if route.endswith("/contact/"):
   assert 'href="mailto:Janey@xuyibottles.com"' in html,"Localized contact email must work"
 result[locale]=len(files)
if sum(result.values()):
 assert all(result.values()),"Partial language release not allowed"
 assert sum(result.values())>=500,"Expected near-complete four-language coverage"
print("XUYI_LOCALIZED_RELEASE_PASSED",json.dumps(result,sort_keys=True))