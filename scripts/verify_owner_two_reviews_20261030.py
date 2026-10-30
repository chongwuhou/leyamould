#!/usr/bin/env python3
"""Read-only proof of the exact same two Excel reviews in D1 and live product pages."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request,urlopen
import json,os,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from publish_daily_product_reviews import check_source,request
ROOT=Path(__file__).resolve().parent.parent
manifest=ROOT/"_local_ops/owner-two-reviews-20261030.json"
DATE="2026-10-30"
SITE="https://xuyibottles.com"
def check_model(item):
    sku=item["sourceModel"].lower()
    url=SITE+"/products/"+sku+"/"
    with urlopen(Request(url,headers={"User-Agent":"XUYI-Owner-Exact-Excel-Review-Verify","Cache-Control":"no-cache"}),timeout=25) as r:
        if r.status!=200:raise RuntimeError("Product page HTTP not 200: "+url)
        page=r.read().decode("utf-8","replace")
    pieces=page.split('id="xuyi-customer-reviews"',1)
    if len(pieces)!=2 or 'datetime="'+DATE+'"' not in pieces[1].split("</section>",1)[0]:
        raise RuntimeError("Expected new dated customer review missing: "+url)
    return url
def main():
    token=os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token or not manifest.exists():raise RuntimeError("Missing D1 token or same-run selection manifest")
    record=json.loads(manifest.read_text(encoding="utf8"))
    if record["date"]!=DATE or len(record["models"])!=2 or len(set(record["models"]))!=2:
        raise RuntimeError("Invalid selection record")
    source={x["model"]:x for x in check_source()}
    state=request(token)
    day={v["model"]:v for v in state["recorded"] if v["published_date"]==DATE}
    for model,row in zip(record["models"],record["sourceRows"]):
        if model not in source or model not in day:raise RuntimeError("Selected Excel model absent from D1")
        s=source[model];d=day[model]
        if s["sourceRow"]!=row or s["sourceRow"]!=d["source_row"] or s["sourceFingerprint"]!=d["source_fingerprint"]:
            raise RuntimeError("D1 ledger mismatch for "+model)
    with ThreadPoolExecutor(max_workers=2) as ex:
        urls=list(ex.map(check_model,[source[m] for m in record["models"]]))
    print("XUYI_OWNER_TWO_20261030_D1_EXCEL_AND_LIVE_PAGES_VERIFIED",
          json.dumps({"models":record["models"],"links":urls,"dayCount":len(day),
                      "lifetime":len(state["recorded"])},ensure_ascii=False),flush=True)
if __name__=="__main__":main()