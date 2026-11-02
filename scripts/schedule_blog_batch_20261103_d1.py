#!/usr/bin/env python3
"""Queue three XUYI B2B originals and twelve localized pages for 2026-11-03."""
import json,os,re,urllib.request,urllib.error
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path

ORIGIN="https://xuyibottles.com"
ENDPOINT="/api/admin/blog-schedule-20261103"
LANGS=("es","pt","ru","tr")
SCHEDULES={
 "bulk-water-bottles-for-school-student-programs":"2026-11-03T09:15:00+08:00",
 "parks-recreation-water-bottle-bulk-procurement":"2026-11-03T13:00:00+08:00",
 "corporate-wellness-water-bottle-bulk-sourcing":"2026-11-03T16:30:00+08:00"
}
PRODUCTS={
 "bulk-water-bottles-for-school-student-programs":["2501","2508","2509"],
 "parks-recreation-water-bottle-bulk-procurement":["2501","2502","2505"],
 "corporate-wellness-water-bottle-bulk-sourcing":["2511","2512","2513"]
}

def require(ok,message):
 if not ok: raise RuntimeError(message)

def get(url):
 req=urllib.request.Request(ORIGIN+url,headers={"User-Agent":"XUYI-20261103-five-language-prepublish-check"})
 try:
  with urllib.request.urlopen(req,timeout=25) as response:
   response.read(1200)
   require(response.status==200,"HTTP status not 200: "+url)
 except urllib.error.HTTPError as err:
  raise RuntimeError("Prepublish URL HTTP "+str(err.code)+": "+url) from None
 except urllib.error.URLError as err:
  raise RuntimeError("Prepublish URL network error: "+str(err.reason)+": "+url) from None

def main():
 require(os.environ.get("OWNER_BLOG1103_RELEASE")=="1","Owner dispatch flag missing")
 require(os.environ.get("GITHUB_ACTIONS")=="true","Only GitHub Actions may schedule")
 require(os.environ.get("GITHUB_REPOSITORY")=="chongwuhou/xuyi-drinkware-site","Wrong repository")
 require(os.environ.get("GITHUB_REF")=="refs/heads/main","Only main may schedule")
 token=os.environ.get("CLOUDFLARE_API_TOKEN","")
 require(bool(token),"Cloudflare project token missing")
 payload_path=Path("_local_ops/blog-batch-20261103/payload.json")
 require(payload_path.is_file(),"Five-language CMS payload missing; run prepare_blog_release_20261103.py first")
 bundle=json.loads(payload_path.read_text(encoding="utf-8"))
 posts=bundle.get("posts",[])
 translations=bundle.get("translations",[])
 cards=bundle.get("indexCards",[])
 require(len(posts)==3 and len(translations)==12 and len(cards)==12,"Expected 3 originals, 12 translations and 12 index cards")
 require(set(p["slug"] for p in posts)==set(SCHEDULES),"Unexpected article slugs in release payload")
 require({(x["slug"],x["locale"]) for x in translations}=={(slug,loc) for slug in SCHEDULES for loc in LANGS},"Localized article set is incomplete")
 require({(x["slug"],x["locale"]) for x in cards}=={(slug,loc) for slug in SCHEDULES for loc in LANGS},"Localized index-card set is incomplete")
 urls=set()
 for item in posts:
  post=item["post"];slug=item["slug"]
  require(post.get("updated")=="2026-11-03" and slug in SCHEDULES,"Unexpected English source "+slug)
  require(item.get("publishedAt")=="2026-11-03T00:00:00Z","Unexpected source date "+slug)
  body="\n".join(x["paragraph"] for x in post.get("sections",[]))
  links=sorted(set(re.findall(r"\]\(/products/([A-Za-z0-9_-]+)/",body)))
  require(links==sorted(PRODUCTS[slug]),"Product links changed: "+slug)
  require(len(post.get("sections",[]))==7 and len(post.get("checklist",[]))==10 and len(post.get("faqs",[]))==4 and len(post.get("related",[]))==3,"Editorial structure changed: "+slug)
  urls.update("/products/"+model+"/" for model in links)
  urls.update("/blog/"+related+"/" for related in post["related"])
 for item in translations:
  loc=item["locale"];slug=item["slug"];html=item["mainHtml"]
  require(item["route"]=="/blog/"+slug+"/" and loc in LANGS,"Localized route mismatch")
  require(len(html)>5000 and html.count('class="blog-section"')==7 and html.count('class="blog-editorial__product-link"')==3 and html.count('class="blog-related__item"')==3 and html.count('class="blog-buyer-matrix"')==1 and html.count("<details>")==4,"Localized body structure failed: "+slug+" "+loc)
  urls.update(re.findall(r'href="/('+loc+r'/[^"]+)"',html))
 # Check all distinct localized product, related-reading and contextual links before
 # inserting any public CMS override. The new article routes themselves are not
 # fetched because they are intentionally unpublished until their D1 schedule.
 urls={u if u.startswith("/") else "/"+u for u in urls}
 with ThreadPoolExecutor(max_workers=12) as pool:
  futures=[pool.submit(get,u) for u in sorted(urls)]
  for future in as_completed(futures):future.result()
 print("XUYI_20261103_PREPUBLISH_LINKS_VERIFIED",len(urls))
 request_body=json.dumps({
  "editorialApproved":True,
  "translations":translations,
  "indexCards":cards
 },ensure_ascii=True,separators=(",",":")).encode("utf-8")
 req=urllib.request.Request(ORIGIN+ENDPOINT,data=request_body,method="POST",headers={
  "Authorization":"Bearer "+token,"Content-Type":"application/json","Accept":"application/json",
  "User-Agent":"XUYI-Owner-Authorized-Five-Language-Blog-Scheduler/1.0"
 })
 try:
  with urllib.request.urlopen(req,timeout=180) as response: result=json.load(response)
 except urllib.error.HTTPError as err:
  raise RuntimeError("D1 five-language scheduling HTTP "+str(err.code)+" "+err.read(900).decode("utf8","replace")) from None
 require(result.get("success") is True and len(result.get("verifiedRows",[]))==3 and len(result.get("verifiedLocaleRows",[]))==12,
         "D1 did not confirm all 15 scheduled language pages")
 print("XUYI_20261103_FIVE_LANGUAGE_BLOG_SCHEDULED",json.dumps(result.get("scheduled",[]),ensure_ascii=False))
 print("XUYI_20261103_LOCALIZED_QUEUES_VERIFIED",len(result.get("localeSchedules",[])))
 print("XUYI_20261103_EN_ES_PT_RU_TR_D1_SCHEDULE_VERIFIED")
if __name__=="__main__":main()