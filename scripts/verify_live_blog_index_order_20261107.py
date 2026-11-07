#!/usr/bin/env python3
"""Verify all four localized Blog indexes exactly match the live English D1 order."""
import json,os,re,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
fixture=json.loads((ROOT/"scripts/fixtures/blog-index-order-baseline-20261107.json").read_text(encoding="utf8"))
batch=set(fixture["batch_slugs"])
old=fixture["existing_73_order"]
origin="https://xuyibottles.com"
def get(path):
 url=origin+path+("?order_verify=20261107" if "?" not in path else "&order_verify=20261107")
 req=urllib.request.Request(url,headers={"User-Agent":"XUYI-D1-Blog-Index-Order-Verification/1.0","Cache-Control":"no-cache"})
 with urllib.request.urlopen(req,timeout=30) as response:
  if response.status!=200:raise RuntimeError("HTTP "+str(response.status)+" "+path)
  return response.read().decode("utf8","replace")
def card_order(page,locale):
 cards=re.findall(r'<article class="news-card">[\s\S]*?</article>',page,re.I)
 order=[]
 for card in cards:
  links=re.findall(r'href="/(?:(?:en|es|pt|ru|tr)/)?blog/([a-z0-9]+(?:-[a-z0-9]+)*)/"',card)
  if len(links)!=3 or len(set(links))!=1:
   raise RuntimeError("Invalid localized card identity in "+locale)
  order.append(links[0])
 if len(order)!=76 or len(order)!=len(set(order)):
  raise RuntimeError("Wrong card count or duplicate in "+locale)
 return order
orders={}
for locale in ("en","es","pt","ru","tr"):
 prefix="" if locale=="en" else "/"+locale
 orders[locale]=card_order(get(prefix+"/blog/"),locale)
 if set(orders[locale][:3])!=batch:
  raise RuntimeError(locale+" newest three D1 articles are not first")
 if orders[locale][3:]!=old:
  raise RuntimeError(locale+" original 73-card order changed")
for locale in ("es","pt","ru","tr"):
 if orders[locale]!=orders["en"]:
  mismatch=next((i for i,(a,b) in enumerate(zip(orders["en"],orders[locale]),1) if a!=b),None)
  raise RuntimeError(locale+" Blog order differs from English at position "+str(mismatch))
meta=json.loads(get("/build-meta.json"))
if meta.get("pagesProject")!="xuyi-drinkware-site":
 raise RuntimeError("Wrong Pages project")
required=int(os.environ.get("XUYI_PUBLISH_REVISION","0"))
if int(meta.get("publishRevision",0))<required:
 raise RuntimeError("D1 publish revision is not live")
sha=os.environ.get("GITHUB_SHA")
if sha and meta.get("sourceRevision")!=sha:
 raise RuntimeError("Live Pages source revision mismatch")
print("XUYI_20261107_ALL_FIVE_BLOG_LISTS_MATCH_LIVE_ENGLISH_D1_ORDER")
print("XUYI_20261107_EXISTING_73_ARTICLE_ORDER_UNCHANGED_IN_ALL_FOUR_LOCALES")
print("XUYI_20261107_NEWEST_THREE_ARTICLES_FIRST_BY_D1_ORDER")
print("XUYI_20261107_D1_REVISION_AND_PAGES_DEPLOYMENT_LIVE_CONFIRMED",meta.get("publishRevision"),meta.get("sourceRevision"))