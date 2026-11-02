#!/usr/bin/env python3
"""Publish up to three distinct authentic Excel reviews per Beijing date.
The v2 D1 ledger is keyed by review ID/fingerprint, not SKU; multiple
customers may review the same model. Private data never enters dist.
"""
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request,urlopen
from zoneinfo import ZoneInfo
import json,os,sys

ROOT=Path(__file__).resolve().parent.parent
SOURCE_FILES=(
 (ROOT/"review_import_private"/"101_verified_buyer_reviews.json","101-zhenshipingjia.xlsx","1cce3652003a78d3e175a2c02a07caf08bda136dc63bea9e246b0006ae2f3163"),
 (ROOT/"review_import_private"/"101_additional_verified_buyer_reviews.json","101-additional-reviews-only.xlsx","ebd5f045fc476d429dcf2c6c68f6fb49c3983b145701fe4587e2e9936b771aa8"),
)
EXCLUDED_SOURCE_ROWS={("101-additional-reviews-only.xlsx",59)}
ORIGIN="https://xuyibottles.com"
API="/api/admin/daily-product-reviews"
ALIASES={"2400-transparent":"2400透明款","2401-transparent":"2401透明款","2306-transparent":"2306透明款","2307-transparent":"2307透明款","2308-transparent":"2308透明款"}

def check_source():
 combined=[];model_sets={};fingerprints=set()
 for path,source_name,expected_sha in SOURCE_FILES:
  payload=json.loads(path.read_text(encoding="utf8"))
  if payload.get("schemaVersion")!=1 or payload.get("source")!=source_name:
   raise RuntimeError("Unexpected private review source: "+source_name)
  if payload.get("sourceWorkbookSha256")!=expected_sha or payload.get("exactAliasMap")!=ALIASES:
   raise RuntimeError("Source workbook hash or approved SKU aliases changed: "+source_name)
  rows=payload.get("reviews",[])
  if len(rows)!=101 or [x.get("sourceRow") for x in rows]!=list(range(2,103)):
   raise RuntimeError("Expected all 101 original Excel rows: "+source_name)
  models=set()
  for item in rows:
   row=item["sourceRow"];expected=ALIASES.get(item["sourceModel"],item["sourceModel"])
   if item["model"]!=expected or item["model"] in models:raise RuntimeError("SKU mismatch/duplicate: "+source_name+" row "+str(row))
   if row==59 and (item["model"]!="2319" or item["author"]!="Beatriz Santos"):
    raise RuntimeError("The reviewed same-customer/SKU exclusion row changed: "+source_name)
   models.add(item["model"])
   if type(item["rating"]) is not int or not 1<=item["rating"]<=5:raise RuntimeError("Invalid rating: "+source_name+" row "+str(row))
   if not 2<=len(item["author"])<=99 or not 12<=len(item["reviewBody"])<=3000:raise RuntimeError("Invalid review: "+source_name+" row "+str(row))
   raw=item["model"]+"\n"+str(item["rating"])+"\n"+item["author"]+"\n"+item["reviewBody"]
   fp=sha256(raw.encode("utf8")).hexdigest()
   if fp!=item["sourceFingerprint"] or fp in fingerprints:raise RuntimeError("Fingerprint changed/duplicate: "+source_name+" row "+str(row))
   fingerprints.add(fp)
   if (source_name,row) not in EXCLUDED_SOURCE_ROWS:combined.append({**item,"sourceFile":source_name})
  model_sets[source_name]=models
  declared={(source_name,int(x["sourceRow"])) for x in payload.get("excludedRows",[])}
  expected_excluded={x for x in EXCLUDED_SOURCE_ROWS if x[0]==source_name}
  if declared!=expected_excluded:raise RuntimeError("Duplicate-customer exclusion changed: "+source_name)
 if model_sets[SOURCE_FILES[0][1]]!=model_sets[SOURCE_FILES[1][1]]:raise RuntimeError("The two workbooks must contain the same 101 official models")
 if len(combined)!=201 or len(fingerprints)!=202:raise RuntimeError("Expected 201 eligible reviews from 202 original rows")
 return combined

def request(token,method="GET",payload=None):
 data=json.dumps(payload,ensure_ascii=False,separators=(",",":")).encode("utf8") if payload else None
 req=Request(ORIGIN+API,data=data,method=method,headers={"Authorization":"Bearer "+token,"Accept":"application/json","User-Agent":"XUYI-Exact-Excel-Review-Publisher/2.0","Content-Type":"application/json"})
 try:
  with urlopen(req,timeout=60) as response:return json.load(response)
 except HTTPError as err:raise RuntimeError("D1 review publisher HTTP "+str(err.code)+" "+err.read(400).decode("utf8","replace")) from None

def plan(entries,state,today,rng=None):
 from secrets import SystemRandom
 ledger=state.get("recorded",[])
 used={x.get("source_fingerprint") for x in ledger}
 used.update(state.get("publishedFingerprints",[]))
 count=sum(x.get("published_date")==today for x in ledger)
 if not 0<=count<=3:raise RuntimeError("D1 daily publication count invalid")
 remaining=[x for x in entries if x["sourceFingerprint"] not in used]
 size=min(3-count,len(remaining))
 if not size:return [],count
 return (rng or SystemRandom()).sample(remaining,size),count

def main():
 entries=check_source()
 print("SOURCE_OK",len(entries),"REVIEWS","UNIQUE_MODELS",len({x["model"] for x in entries}))
 if "--dry-run" in sys.argv:
  print("DRY_RUN_NO_D1_WRITE",[(x["sourceFile"],x["sourceRow"],x["model"]) for x in entries[:3]])
  return
 token=os.environ.get("CLOUDFLARE_API_TOKEN","")
 if not token:raise RuntimeError("Cloudflare credential missing")
 if os.environ.get("GITHUB_ACTIONS")!="true" or os.environ.get("GITHUB_REPOSITORY")!="chongwuhou/xuyi-drinkware-site" or os.environ.get("GITHUB_REF")!="refs/heads/main":
  raise RuntimeError("Review publishing is allowed only from XUYI private GitHub main")
 today=datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()
 state=request(token)
 if state.get("today")!=today:raise RuntimeError("GitHub and D1 Beijing dates disagree")
 chosen,prior=plan(entries,state,today)
 if not chosen:
  print("NOTHING_TO_PUBLISH",today,"TODAY",prior,"LIFETIME",len(state["recorded"]))
  return
 batch=[{"sourceFile":x["sourceFile"],"sourceRow":x["sourceRow"],"sourceModel":x["sourceModel"],"model":x["model"],"rating":x["rating"],"author":x["author"],"content":x["reviewBody"],"sourceFingerprint":x["sourceFingerprint"]} for x in chosen]
 print("EXACT_REVIEWS_SELECTED",[(x["sourceFile"],x["sourceRow"],x["model"]) for x in batch],"DATE",today)
 result=request(token,"POST",{"date":today,"items":batch,"confirmedAuthentic":True})
 if not result.get("success") or result.get("inserted")!=len(batch) or result.get("todayCount")!=prior+len(batch):raise RuntimeError("D1 commit ambiguous; inspect append-only ledger before retry")
 stored={(x["source_file"],x["source_row"],x["source_fingerprint"],x["published_date"]) for x in result["recorded"]}
 if not all((x["sourceFile"],x["sourceRow"],x["sourceFingerprint"],today) in stored for x in batch):raise RuntimeError("Publication ledger reconciliation failed")
 print("PUBLISHED_TO_D1",len(batch),"MODELS",[x["model"] for x in batch],"TODAY",result["todayCount"],"TOTAL",len(result["recorded"]),"PUBLISH_REVISION",result.get("revision"))

if __name__=="__main__":main()