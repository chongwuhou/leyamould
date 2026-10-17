#!/usr/bin/env python3
"""XUYI homepage/company vs sports collection/commercial vs guide/informational."""
import sys, re, json
from html import unescape,escape
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from search_intent_roles import DATA,source_intent_fields,render_search_intent
routes=DATA["routes"]
for locale in ("en","es","pt","ru","tr"):
 seen={}
 for role,route in routes.items():
  folder=ROOT/"dist"/("" if locale=="en" else locale)
  f=(folder/"index.html" if route=="/" else folder/route.lstrip("/")/"index.html")
  raw=f.read_text(encoding="utf8")
  head,body=raw.split("</head>",1)
  spec=DATA["languages"][locale][role]
  title=unescape(re.search(r"<title>(.*?)</title>",head).group(1))
  description=unescape(re.search(r'<meta name="description" content="([^"]*)"',head).group(1))
  assert (title,description)==(spec["preferred"]["title"],spec["preferred"]["description"]),(locale,role,title)
  assert unescape(re.search(r'<meta property="og:title" content="([^"]*)"',head).group(1))==title,(locale,role,"og title")
  assert unescape(re.search(r'<meta property="og:description" content="([^"]*)"',head).group(1))==description,(locale,role,"og desc")
  found=re.search(r"<h1\b[^>]*>(.*?)</h1>",body,re.S)
  assert found,(locale,role,"missing H1")
  heading=re.sub(r"\s+"," ",unescape(re.sub(r"<[^>]+>"," ",found.group(1)))).strip()
  if role!="home":assert heading==spec["preferred"]["h1"],(locale,role,heading)
  assert 'rel="canonical"' in head and 'hreflang="en"' in head,(locale,role)
  for match in re.findall(r'<script type="application/ld\+json">([\s\S]*?)</script>',head):
   data=json.loads(match)
   for obj in data.get("@graph",[data]):
    if obj.get("@type")=="WebPage" and "description" in obj:assert obj["description"]==description,(locale,role,"schema desc")
    if obj.get("@type")=="BlogPosting" and role=="blog":
     assert obj["headline"]==title,(locale,"blog schema headline")
  seen[role]=title
  # Future independent D1 edits of either field must block the entire
  # historic curated pair, not just half an obsolete suggestion.
  entry=spec["baseline"]
  assert source_intent_fields(route,locale,entry["title"],entry["description"])==spec["preferred"]
  assert source_intent_fields(route,locale,"OWNER CHANGED SEO TITLE",entry["description"]) is None
  assert source_intent_fields(route,locale,entry["title"],"OWNER CHANGED SEO DESCRIPTION") is None
  fixture='<html><head><title>'+escape(entry["title"])+'</title><meta name="description" content="'+escape(entry["description"],quote=True)+'"></head><body><main><h1>'+escape(entry.get("h1","Factory overview"))+'</h1></main></body></html>'
  altered=fixture.replace("<title>","<title>OWNER ",1)
  assert render_search_intent(altered,route,locale)==altered,(locale,role,"D1 title override")
  altered=fixture.replace('content="'+escape(entry["description"],quote=True)+'"','content="OWNER DESCRIPTION"',1)
  assert render_search_intent(altered,route,locale)==altered,(locale,role,"D1 desc override")
  rerendered=render_search_intent(fixture,route,locale)
  assert render_search_intent(rerendered,route,locale)==rerendered,(locale,role,"idempotence")
  if role!="home":
   customized=fixture.replace("<h1>"+escape(entry["h1"])+"</h1>","<h1>OWNER CUSTOMIZED H1</h1>",1)
   assert "<h1>OWNER CUSTOMIZED H1</h1>" in render_search_intent(customized,route,locale),(locale,role,"D1 H1 override")
 assert len(set(seen.values()))==3,(locale,"duplicate intents")
assert render_search_intent('<title>unrelated page</title>',"/products/2095/","en")=='<title>unrelated page</title>'
assert render_search_intent('<title>new locale</title>',"/","it")=='<title>new locale</title>'
article=(ROOT/"dist/blog/sports-water-bottle-customization/index.html").read_text(encoding="utf8")
assert 'href="/collections/sports-water-bottles/"' in article, "Guide should lead to transaction page"
print("XUYI_THREE_ROUTE_INTENT_SEPARATION_15_LOCALE_PAGES_CMS_OWNER_PASSED")
