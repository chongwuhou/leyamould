#!/usr/bin/env python3
"""Reviewed ES microcopy + About positioning: source/D1 owner priority gate."""
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from spanish_reviewed_copy import reviewed_spanish_copy,_RULES
from home_bpa_source import add_home_bpa_note,_SOURCE
from about_company_page import render,apply_body,source,baseline_body
snap=json.loads((ROOT/"_local_ops/build-snapshot.json").read_text(encoding="utf8"))
D1={(x["resourceId"][5:],x["locale"]):x["content"] for x in snap["translations"]
    if x.get("resourceId","").startswith("page:")}
assert set(_RULES)=={"/","/blog/"}
assert len(_RULES["/"])==2 and len(_RULES["/blog/"])==1
for route in ("/","/blog/"):
 original=D1[(route,"es")]
 updated=reviewed_spanish_copy(route,"es",original)
 assert updated!=original,(route,"source not corrected")
 assert updated["mainHtml"]!=original["mainHtml"]
 assert updated["title"]==original["title"] and updated["description"]==original["description"]
 assert reviewed_spanish_copy(route,"es",updated)==updated
 for old,new in _RULES[route].items():
  assert original["mainHtml"].count(old)==1
  assert old not in updated["mainHtml"] and updated["mainHtml"].count(new)==1
  # A CMS owner can change each independent element. All other corrections
  # may still apply; the newly owner-edited element must remain byte-for-byte.
  user_html=original["mainHtml"].replace(old,'<span data-cms-owner="editorial">Nueva frase de administración</span>',1)
  owner=reviewed_spanish_copy(route,"es",{**original,"mainHtml":user_html})
  assert '<span data-cms-owner="editorial">Nueva frase de administración</span>' in owner["mainHtml"]
  assert new not in owner["mainHtml"]
 assert reviewed_spanish_copy(route,"pt",original)==original
 assert reviewed_spanish_copy("/products/2501/","es",original)==original
 assert reviewed_spanish_copy(route,"es",{**original,"mainHtml":"A completely replaced CMS body"})["mainHtml"]=="A completely replaced CMS body"

blog_routes=sorted(route for route,loc in D1 if loc=="es" and route.startswith("/blog/"))
assert len(blog_routes)>=17
for route in blog_routes:
 original=D1[(route,"es")]
 new=reviewed_spanish_copy(route,"es",original)
 assert '<span class="eyebrow">XUYI · BOTELLAS DE PLÁSTICO</span>' in new["mainHtml"]
 assert '<span class="eyebrow">XUYI · VASOS DE PLÁSTICO</span>' not in new["mainHtml"]
 assert reviewed_spanish_copy(route,"es",new)==new
 # The admin may already have persisted the correction directly in D1.
 # Either reviewed source is valid; a subsequent CMS edit still wins.
 existing="XUYI · VASOS DE PLÁSTICO" if "XUYI · VASOS DE PLÁSTICO" in original["mainHtml"] else "XUYI · BOTELLAS DE PLÁSTICO"
 assert existing in original["mainHtml"]
 owner=original["mainHtml"].replace(existing,"XUYI · ARTÍCULOS APROBADOS",1)
 assert "XUYI · ARTÍCULOS APROBADOS" in reviewed_spanish_copy(route,"es",{**original,"mainHtml":owner})["mainHtml"]
 page=(ROOT/"dist/es"/route.lstrip("/")/"index.html").read_text(encoding="utf8")
 assert '<span class="eyebrow">XUYI · BOTELLAS DE PLÁSTICO</span>' in page,(route,"blog eyebrow drift")

for lang,(hero_note,headline,detail) in _SOURCE.items():
 if lang=="en":
  raw=(ROOT/"dist/index.html").read_text(encoding="utf8")
  # the published result must show the unique source-inserted element
 else:
  raw=D1[("/",lang)]["mainHtml"]
  if lang=="es":raw=reviewed_spanish_copy("/","es",D1[("/","es")])["mainHtml"]
 anchor='<p class="hero__note">'+hero_note+'</p>'
 if lang!="en":
  assert raw.count(anchor)==1,(lang,"current approved source note changed")
  merged=add_home_bpa_note(raw,lang)
  assert merged.count('class="home-bpa-verification"')==1
  assert add_home_bpa_note(merged,lang)==merged
  owner=raw.replace(anchor,'<p class="hero__note">Owner-selected home message</p>')
  assert add_home_bpa_note(owner,lang)==owner
 page=(ROOT/"dist"/("" if lang=="en" else lang)/"index.html").read_text(encoding="utf8")
 assert page.count('class="home-bpa-verification"')==1,(lang,"missing/duplicate")
 assert headline in page and detail in page,(lang,"text")
 assert "certified BPA-free" not in page.lower()
 if lang=="es":
  assert "¿Sin BPA?" in page and "SIN BPA?" not in page
  assert "Taizhou, China · Botellas de plástico · Consultas OEM/ODM" in page
  assert "Confiable <em>Botella de plástico</em> Socio fabricante." not in page
  assert "<h2>Socio fabricante confiable de <em>botellas de plástico</em>.</h2>" in page

blog=(ROOT/"dist/es/blog/index.html").read_text(encoding="utf8")
assert '<span class="eyebrow">XUYI · BOTELLAS DE PLÁSTICO</span>' in blog
assert 'XUYI · VASOS DE PLÁSTICO' not in blog
for lang in ("en","es","pt","ru","tr"):
 html=render(lang)
 assert html.count('id="what-you-wont-find-here"')==1
 assert len(source(lang)["noClaims"])==3
 page=(ROOT/"dist"/("" if lang=="en" else lang)/"about/index.html").read_text(encoding="utf8")
 assert page.count('id="what-you-wont-find-here"')==1,(lang,"About section lost")

en=source("en")
assert en["noClaimsTitle"]=="What You Won't Find Here"
assert en["noClaimsIntro"]=="Most supplier pages tell you what they are. We think it's just as useful to tell you what we're not."
assert [x[0] for x in en["noClaims"]]==["No metal. No glass.","No stock photography.","No unverified numbers."]
for phrase in ("sports bottles, kids' bottles, water jugs, shaker bottles","not a rendering","physical sample and the order specification","impressively wrong on time"):
 assert phrase in " ".join(x[1] for x in en["noClaims"])
current=D1[("/about/","en")]["mainHtml"] if ("/about/","en") in D1 else ""
if current and baseline_body(current,"en"):
 assert 'id="what-you-wont-find-here"' in apply_body(current,"en")
owner=current+"<p>Owner-added details, do not overwrite.</p>"
assert apply_body(owner,"en")==owner
print("XUYI_SPANISH_THREE_MICROCOPY_BPA_SOURCE_ABOUT_FIVE_LOCALES_CMS_POLICY_PASSED")
