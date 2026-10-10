#!/usr/bin/env python3
"""End-to-end all-route QA for shared menu, mobile nav, attrs and JS UI data."""
from pathlib import Path
from html.parser import HTMLParser
import html,json,re

ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/"dist"
MANIFEST=json.loads((DIST/"locale-manifest.json").read_text(encoding="utf8"))
LANGS=tuple(x["code"] for x in MANIFEST["locales"] if x["code"]!="en")
PREFIX={x["code"]:x["pathPrefix"] for x in MANIFEST["locales"]}
MAPPING=json.loads((ROOT/"data/ui-translations.json").read_text(encoding="utf8"))
RUNTIME=json.loads((ROOT/"data/runtime-ui-translations.json").read_text(encoding="utf8"))
CRITICAL=("Plastic Water Bottles","Plastic Sports Water Bottles","Large Capacity Water Jugs",
 "Kids Plastic Water Bottles","Plastic Shaker Bottles","Bottle By Feature",
 "Straw Lid Bottles","Flip Top Bottles","Carry Handle Bottles","Large Capacity",
 "Gradient Colors","Bottle By Use","Gym & Sports","Outdoor & Travel",
 "Kids & School","Everyday Hydration","Promotional Gifts","OEM & Wholesale",
 "Custom Water Bottle","Custom Graphics","Request a Sample","Wholesale Buyer Guide",
 "Custom Molding","Custom Manufacturing","OEM / ODM Support",
 "Manufacturing Process","Quality Assurance","Shipping & Logistics",
 "Search →","Instant Quote →")
class Chrome(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True);self.main=False;self.hidden=0
  self.nodes=[];self.attrs=[]
 def handle_starttag(self,tag,attrs):
  if tag=="main":self.main=True
  if tag in ("script","style","svg","noscript"):self.hidden+=1
  if not self.main and not self.hidden:
   self.attrs += [(k,v) for k,v in attrs if k in ("alt","aria-label","placeholder","title") and v]
 def handle_endtag(self,tag):
  if tag=="main":self.main=False
  if tag in ("script","style","svg","noscript") and self.hidden:self.hidden-=1
 def handle_data(self,text):
  if not self.main and not self.hidden and text.strip():self.nodes.append(html.unescape(text.strip()))
def parse(path):
 obj=Chrome();obj.feed(path.read_text(encoding="utf8"));return obj
paths=[f.relative_to(DIST) for f in DIST.rglob("index.html")
       if f.relative_to(DIST).parts[0] not in (*PREFIX.values(),"admin")]
assert len(paths)>=130
checks=0
for loc in LANGS:
 dictionary=MAPPING[loc]
 runtime=RUNTIME[loc]
 assert len(runtime["slides"])==3
 assert len(runtime["messages"])>=12
 homepage=(DIST/loc/"index.html").read_text(encoding="utf8")
 found=re.search(r'<script type="application/json" id="xuyi-runtime-ui">([^<]+)</script>',homepage)
 assert found and json.loads(found.group(1))==runtime,(loc,"runtime script differs")
 for rel in paths:
  if not (DIST/PREFIX[loc]/rel).is_file():continue
  english=parse(DIST/rel)
  translated=parse(DIST/PREFIX[loc]/rel)
  assert len(english.nodes)==len(translated.nodes),(loc,str(rel),"chrome text count mismatch")
  assert len(english.attrs)==len(translated.attrs),(loc,str(rel),"attribute count mismatch")
  for a,b in zip(english.nodes,translated.nodes):
   if a in dictionary and dictionary[a]!=a:
    assert b==dictionary[a],(loc,str(rel),a,b)
  for (k,a),(j,b) in zip(english.attrs,translated.attrs):
   assert k==j,(loc,str(rel),k,j)
   if a in dictionary and dictionary[a]!=a:
    assert b==dictionary[a],(loc,str(rel),k,a,b)
  checks+=1
 en=parse(DIST/"index.html");other=parse(DIST/PREFIX[loc]/"index.html")
 for key in CRITICAL:
  assert key in en.nodes,(loc,"missing common source label",key)
  assert key in dictionary and dictionary[key]!=key,(loc,"missing common translation",key)
  assert dictionary[key] in other.nodes,(loc,"untranslated mega/mobile menu",key)
 for name in ("XUYI","BOTTLES",*[x["nativeName"] for x in MANIFEST["locales"]]):
  assert name in other.nodes,(loc,"brand or language name changed",name)
 # Metadata: a source-language English title is never published on a localized product page.
 for model in ("2250","2282","2307---"):
  if loc=="pt":
   source=(DIST/"products"/model/"index.html").read_text(encoding="utf8")
   target=(DIST/"pt/products"/model/"index.html").read_text(encoding="utf8")
   assert re.search(r"<title>(.*?)</title>",source).group(1)!=re.search(r"<title>(.*?)</title>",target).group(1)
# Previously untranslated source image Alt attributes in the Portuguese
# D1 product body must not regress when a site revision is rebuilt.
for model in ("2215","2250","2281","2291","2307","2308","2308---"):
 page=(DIST/"pt/products"/model/"index.html").read_text(encoding="utf8")
 assert "Large Capacity Plastic Water Jug view 1" not in page,("pt",model,"English product image alt")
print("XUYI_SHARED_CHROME_I18N_PASSED",checks,"localized pages,",len(LANGS),"languages, menu/attributes/runtime tested")