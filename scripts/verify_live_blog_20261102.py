#!/usr/bin/env python3
"""Verify all 15 localized B2B pages, three real R2 covers, index cards, and sitemap."""
import urllib.request,json,re,time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
rows=json.loads((ROOT/"data/blog-images-reviewed-20261102.json").read_text("utf8"))["images"]
origin="https://xuyibottles.com"
def get(path):
 req=urllib.request.Request(origin+path+"?owner_b2b_20261102="+str(int(time.time())),headers={"User-Agent":"XUYI-Owner-B2B-Live-Verification","Cache-Control":"no-cache"})
 with urllib.request.urlopen(req,timeout=25) as res:
  if res.status!=200:raise RuntimeError("HTTP "+str(res.status)+" "+path)
  return res.read(),res.headers.get("content-type","")
def check(inp):
 row,loc=inp
 prefix="" if loc=="en" else "/"+loc
 page=get(prefix+"/blog/"+row["slug"]+"/")[0].decode("utf8","replace")
 idx=get(prefix+"/blog/")[0].decode("utf8","replace")
 for html in (page,idx):
  if 'src="'+row["cover"]+'"' not in html:raise RuntimeError("Approved R2 image missing from "+row["slug"]+" "+loc)
 if page.count('class="blog-editorial__product-link"')!=3:raise RuntimeError("Missing exact SKU links "+row["slug"]+" "+loc)
 if page.count('class="blog-related__item"')!=3:raise RuntimeError("Missing related reads "+row["slug"]+" "+loc)
 if '2026-11-02' not in page:raise RuntimeError("Wrong publication date "+row["slug"]+" "+loc)
 if '/blog/'+row["slug"]+'/' not in idx:raise RuntimeError("Missing localized index card "+row["slug"]+" "+loc)
 return (row["slug"],loc)
def main():
 for row in rows:
  data,mime=get(row["cover"])
  if len(data)<30000 or not mime.startswith("image/webp"):raise RuntimeError("Invalid R2 media "+row["cover"])
 sitemap=get("/sitemap.xml")[0].decode("utf8","replace")
 for row in rows:
  if '/blog/'+row["slug"]+'/' not in sitemap:raise RuntimeError("Missing sitemap "+row["slug"])
 with ThreadPoolExecutor(max_workers=9) as pool:
  checked=list(pool.map(check,[(row,loc) for row in rows for loc in ("en","es","pt","ru","tr")]))
 assert len(checked)==15
 print("XUYI_20261102_THREE_B2B_ARTICLES_15_LOCALE_ROUTES_THREE_R2_COVERS_INDEX_AND_SITEMAP_PASS",flush=True)
if __name__=="__main__":main()