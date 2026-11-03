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

# D1 can contain scheduled/future blog translations before their English
# originals are released. Only validate routes that exist in the published
# English build; unpublished schedule rows are not public pages yet.
blog_routes=sorted(route for route,loc in D1 if loc=="es" and route.startswith("/blog/") and (ROOT/"dist"/route.lstrip("/")/"index.html").is_file())
assert len(blog_routes)>=17
for route in blog_routes:
 original=D1[(route,"es")]
 new=reviewed_spanish_copy(route,"es",original)
 assert '<span class="eyebrow">XUYI · ' in new["mainHtml"],(route,"branded eyebrow")
 assert 'XUYI · VASOS DE PLÁSTICO' not in new["mainHtml"],(route,"obsolete beverage label")
 assert '<span class="eyebrow">XUYI · VASOS DE PLÁSTICO</span>' not in new["mainHtml"]
 assert reviewed_spanish_copy(route,"es",new)==new
 # The admin may already have persisted the correction directly in D1.