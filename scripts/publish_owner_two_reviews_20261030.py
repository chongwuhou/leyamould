#!/usr/bin/env python3
"""Owner-approved ONE-TIME two exact original Excel reviews (Beijing 2026-10-30).

Never fabricate content or touch daily review scheduler or its 3/day D1 limit.
D1 ledger is authoritative; reject already used models, avoid duplicate writes.
"""
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from secrets import SystemRandom
from urllib.error import URLError
from urllib.request import Request,urlopen
from zoneinfo import ZoneInfo
from xml.etree import ElementTree
import json,os,re,sys,time

sys.path.insert(0,str(Path(__file__).resolve().parent))
from publish_daily_product_reviews import check_source,request

DAY="2026-10-30"
ROOT=Path(__file__).resolve().parent.parent
RECORD=ROOT/"_local_ops/owner-two-reviews-20261030.json"
SITE="https://xuyibottles.com"

def audit_source():
    rows=check_source()
    if len(rows)!=101:raise RuntimeError("Excel review source row count unexpectedly changed")
    return rows

def get_live_sku_slugs():
    req=Request(SITE+"/sitemap.xml",headers={"User-Agent":"XUYI-Owner-Excel-Review/2.0"})
    with urlopen(req,timeout=25) as r:root=ElementTree.fromstring(r.read())
    ns={"s":"http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls=[n.findtext("s:loc",namespaces=ns) for n in root.findall("s:url",ns)]
    return {v.rsplit("/",2)[1] for v in urls if re.fullmatch(r"https://xuyibottles\.com/products/[^/]+/",v or "")}

def state_read(token):
    for k in range(4):
        try:return request(token)
        except (URLError,TimeoutError,RuntimeError) as e:
            if k==3 or not any(s in str(e) for s in ("HTTP 429","HTTP 502","HTTP 503","HTTP 504","timed out")):raise
            time.sleep((4,8,12)[k])

def matched(row,ledger):
    return (row["model"]==ledger["model"] and row["sourceRow"]==ledger["source_row"]
            and row["sourceModel"]==ledger["source_model"]
            and row["sourceFingerprint"]==ledger["source_fingerprint"])

def main():
    rows=audit_source()
    links=get_live_sku_slugs()
    if "--dry-run" in sys.argv:
        if len(links)<100:raise RuntimeError("Product sitemap missing many canonical URLs")
        print("OCT30_OWNER_TWO_EXCEL_SOURCE_VALIDATED_101_SKUS",len(links),flush=True)
        return
    if not (os.environ.get("GITHUB_ACTIONS")=="true"
        and os.environ.get("GITHUB_REF")=="refs/heads/main"
        and os.environ.get("GITHUB_EVENT_NAME")=="push"
        and os.environ.get("GITHUB_REPOSITORY")=="chongwuhou/xuyi-drinkware-site"
        and os.environ.get("OWNER_TWO_RELEASE")=="1"):
        raise RuntimeError("One-time owner-approved production push only")
    if datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()!=DAY:
        raise RuntimeError("One-time publication expired: expected Beijing "+DAY)
    token=os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:raise RuntimeError("D1 publication credentials not configured")
    state=state_read(token)
    if state.get("today")!=DAY:raise RuntimeError("Beijing date mismatch")
    ledger=state["recorded"]
    today=[v for v in ledger if v["published_date"]==DAY]
    if len(today)>1:
        raise RuntimeError("Today already has "+str(len(today))+" reviews; adding exactly two would exceed max 3 or duplicate prior release. No write.")
    occupied=set(state["existingModels"])|{v["model"] for v in ledger}
    eligible=[v for v in rows if v["model"] not in occupied and v["sourceModel"].lower() in links]
    if len(eligible)<2:raise RuntimeError("Fewer than two unpublished Excel reviews with verified canonical product URLs")
    selected=SystemRandom().sample(eligible,2)
    payload=[{
        "sourceRow":v["sourceRow"],"sourceModel":v["sourceModel"],"model":v["model"],
        "rating":v["rating"],"author":v["author"],"content":v["reviewBody"],
        "sourceFingerprint":v["sourceFingerprint"]
    } for v in selected]
    print("OWNER_TWO_RANDOM_EXCEL_ROWS",[(x["sourceRow"],x["model"]) for x in selected],flush=True)
    # D1 atomic batch is responsible for rejecting concurrent additions.
    saved=request(token,"POST",{"date":DAY,"confirmedAuthentic":True,"items":payload})
    if saved.get("success") is not True or saved.get("inserted")!=2 or saved.get("todayCount")!=len(today)+2:
        raise RuntimeError("D1 commit uncertain; inspect ledger before retrying; never blindly post again")
    latest=state_read(token)
    found={r["model"]:r for r in latest["recorded"] if r["published_date"]==DAY}
    if len(found)!=len(today)+2 or any(v["model"] not in found or not matched(v,found[v["model"]]) for v in selected):
        raise RuntimeError("D1 commit mismatch; stop, no replay")
    RECORD.parent.mkdir(parents=True,exist_ok=True)
    RECORD.write_text(json.dumps({"date":DAY,"models":[v["model"] for v in selected],
        "sourceModels":[v["sourceModel"] for v in selected],
        "sourceRows":[v["sourceRow"] for v in selected],
        "publishRevision":saved.get("revision")},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("XUYI_OWNER_TWO_20261030_EXCEL_REVIEWS_PUBLISHED_TO_D1",
          [v["model"] for v in selected],"TODAY",len(found),
          "TOTAL_LEDGER",len(latest["recorded"]),"PUBLISH_REVISION",saved.get("revision"),flush=True)

if __name__=="__main__":main()