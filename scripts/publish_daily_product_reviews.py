#!/usr/bin/env python3
"""Publish up to three unseen, exact-SKU reviews per Beijing date to D1.

The append-only D1 ledger is authoritative: retries, review deletion, and
repeated workflow_dispatch calls never create an extra customer rating.
Unpublished personal data stays only in this site's private GitHub repo.
"""
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
import json
import os
import sys

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "review_import_private" / "101_verified_buyer_reviews.json"
ORIGIN = "https://xuyibottles.com"
API = "/api/admin/daily-product-reviews"
ALIASES = {
    "2400-transparent": "2400透明款", "2401-transparent": "2401透明款",
    "2306-transparent": "2306透明款", "2307-transparent": "2307透明款",
    "2308-transparent": "2308透明款",
}

def check_source():
    payload=json.loads(SOURCE.read_text(encoding="utf8"))
    assert payload["schemaVersion"]==1 and payload["source"]=="101-zhenshipingjia.xlsx"
    assert payload["exactAliasMap"]==ALIASES
    entries=payload["reviews"]
    assert len(entries)==101 and len({x["model"] for x in entries})==101
    assert [x["sourceRow"] for x in entries]==list(range(2,103))
    for item in entries:
        expected=ALIASES.get(item["sourceModel"],item["sourceModel"])
        if item["model"]!=expected:
            raise RuntimeError("Excel/factory model mismatch: row "+str(item["sourceRow"]))
        if type(item["rating"]) is not int or not 1<=item["rating"]<=5:
            raise RuntimeError("Invalid customer rating")
        if not 2<=len(item["author"])<=99 or not 12<=len(item["reviewBody"])<=3000:
            raise RuntimeError("Invalid review text or name")
        raw=item["model"]+"\n"+str(item["rating"])+"\n"+item["author"]+"\n"+item["reviewBody"]
        if sha256(raw.encode("utf8")).hexdigest()!=item["sourceFingerprint"]:
            raise RuntimeError("Review content fingerprint changed; abort")
    return entries

def request(token,method="GET",payload=None):
    data=json.dumps(payload,ensure_ascii=False,separators=(",",":")).encode("utf8") if payload else None
    req=Request(ORIGIN+API,data=data,method=method,headers={
        "Authorization":"Bearer "+token,"Accept":"application/json",
        "User-Agent":"XUYI-Exact-Excel-Review-Publisher/1.0",
        "Content-Type":"application/json"})
    try:
        with urlopen(req,timeout=60) as response:
            return json.load(response)
    except HTTPError as err:
        raise RuntimeError("D1 review publisher HTTP "+str(err.code)+" "+
                           err.read(400).decode("utf8","replace")) from None

def plan(entries,state,today):
    ledger=state.get("recorded",[])
    occupied=set(state.get("existingModels",[]))|{r["model"] for r in ledger}
    count=sum(x.get("published_date")==today for x in ledger)
    if not 0<=count<=3:raise RuntimeError("D1 daily publication count invalid")
    return [x for x in entries if x["model"] not in occupied][:3-count],count

def main():
    entries=check_source()
    print("SOURCE_OK",len(entries),"EXACT_MODELS",len(ALIASES),"APPROVED_ALIASES")
    if "--dry-run" in sys.argv:
        print("DRY_RUN_NO_D1_WRITE", [x["model"] for x in entries[:3]])
        return
    token=os.environ.get("CLOUDFLARE_API_TOKEN","")
    if not token:raise RuntimeError("Cloudflare credential missing")
    if os.environ.get("GITHUB_ACTIONS")!="true" or \
       os.environ.get("GITHUB_REPOSITORY")!="chongwuhou/xuyi-drinkware-site" or \
       os.environ.get("GITHUB_REF")!="refs/heads/main":
        raise RuntimeError("Review publishing is allowed only from XUYI private GitHub main")
    today=datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()
    state=request(token)
    if state.get("today")!=today:raise RuntimeError("GitHub and D1 Beijing dates disagree")
    chosen,prior=plan(entries,state,today)
    if not chosen:
        print("NOTHING_TO_PUBLISH",today,"TODAY",prior,"LIFETIME",len(state["recorded"]))
        return
    batch=[{
        "sourceRow":x["sourceRow"],"sourceModel":x["sourceModel"],
        "model":x["model"],"rating":x["rating"],"author":x["author"],
        "content":x["reviewBody"],"sourceFingerprint":x["sourceFingerprint"]
    } for x in chosen]
    print("EXACT_MODELS_SELECTED",[x["model"] for x in chosen],"PUBLICATION_DATE",today)
    result=request(token,"POST",{"date":today,"items":batch,"confirmedAuthentic":True})
    if not result.get("success") or result.get("inserted")!=len(batch) or \
       result.get("todayCount")!=prior+len(batch):
        raise RuntimeError("D1 commit ambiguous; inspect append-only ledger before retry")
    stored={(x["model"],x["source_row"],x["published_date"]) for x in result["recorded"]}
    if not all((x["model"],x["sourceRow"],today) in stored for x in batch):
        raise RuntimeError("Publication ledger reconciliation failed")
    print("PUBLISHED_TO_D1",len(batch),"MODELS",[x["model"] for x in batch],
          "TODAY",result["todayCount"],"TOTAL",len(result["recorded"]),
          "PUBLISH_REVISION",result.get("revision"))

if __name__=="__main__":
    main()
