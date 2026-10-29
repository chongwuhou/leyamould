#!/usr/bin/env python3
"""Verify exactly three new R2 WebP photos on 15 published article routes and list cards."""
from pathlib import Path
import json,time,urllib.request
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parent.parent
ROWS=json.loads((ROOT/"data/blog-reviewed-cover-r2-20261029.json").read_text("utf8"))["images"]
BASE="https://xuyibottles.com"
def fetch(path):
 req=urllib.request.Request(BASE+path+"?reviewed="+str(time.time()),headers={"User-Agent":"XUYI-Reviewed-R2-Cover-Live-Check","Cache-Control":"no-cache"})
 with urllib.request.urlopen(req,timeout=25) as res:
  if res.status!=200:raise RuntimeError("Unexpected HTTP status "+path)
  return res.read(),res.headers.get("content-type","")
def check(pair):
 row,lang=pair;prefix="" if lang=="en" else "/"+lang
 for path in (prefix+"/blog/"+row["slug"]+"/",prefix+"/blog/"):
  html=fetch(path)[0].decode("utf8","replace")
  if 'src="'+row["cover"]+'"' not in html or 'src="'+row["old"]+'"' in html:raise RuntimeError("R2 cover mismatch "+path+" "+row["slug"])
 return 1
def main():
 for row in ROWS:
  binary,mime=fetch(row["cover"])
  if len(binary)<25000 or not mime.startswith("image/webp"):raise RuntimeError("Not valid R2 WebP: "+row["cover"])
 with ThreadPoolExecutor(max_workers=8) as pool:
  assert sum(pool.map(check,[(r,l) for r in ROWS for l in ("en","es","pt","ru","tr")]))==15
 print("XUYI_R2_THREE_NEW_COVERS_FIFTEEN_ARTICLE_PAGES_ALL_LISTS_PASS")
if __name__=="__main__":main()
