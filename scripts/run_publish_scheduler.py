#!/usr/bin/env python3
"""Five-minute scheduler heartbeat for XUYI review and Blog publication."""
from datetime import datetime
from urllib.error import HTTPError,URLError
from urllib.request import Request,urlopen
from zoneinfo import ZoneInfo
import json,os
from publish_daily_product_reviews import check_source,request,plan,ORIGIN

RUNNER_API="/api/admin/scheduler-runner"
def call(token,path,payload):
 data=json.dumps(payload,separators=(",",":")).encode("utf8")
 req=Request(ORIGIN+path,data=data,method="POST",headers={"Authorization":"Bearer "+token,"Content-Type":"application/json","Accept":"application/json","User-Agent":"XUYI-Scheduler/1.0"})
 try:
  with urlopen(req,timeout=90) as response:return json.load(response)
 except HTTPError as err:raise RuntimeError("Scheduler API HTTP "+str(err.code)+" "+err.read(400).decode("utf8","replace")) from None

def dispatch_site_build():
 token=os.environ.get("GITHUB_TOKEN","")
 if not token:
  print("WARNING: GITHUB_TOKEN missing; the existing 30-minute site rebuild remains the fallback")
  return
 url="https://api.github.com/repos/chongwuhou/xuyi-drinkware-site/actions/workflows/publish-xuyi.yml/dispatches"
 body=json.dumps({"ref":"main"}).encode("utf8")
 req=Request(url,data=body,method="POST",headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","Content-Type":"application/json","User-Agent":"XUYI-Scheduler/1.0"})
 try:
  with urlopen(req,timeout=30) as response:print("SITE_BUILD_DISPATCHED",response.status)
 except (HTTPError,URLError) as err:
  print("WARNING: D1 content was published; immediate site build dispatch failed:",str(err))

def main():
 token=os.environ.get("CLOUDFLARE_API_TOKEN","")
 if not token:raise RuntimeError("Cloudflare credential missing")
 if os.environ.get("GITHUB_ACTIONS")!="true" or os.environ.get("GITHUB_REPOSITORY")!="chongwuhou/xuyi-drinkware-site" or os.environ.get("GITHUB_REF")!="refs/heads/main":
  raise RuntimeError("Scheduler is allowed only from the canonical XUYI GitHub main")
 claim=call(token,RUNNER_API,{"action":"claim"})
 reviews=claim.get("claimed",[])
 blog=claim.get("blog",[])
 print("SCHEDULER_CLAIM",len(reviews),"review tasks",len(blog),"blog tasks")
 changed=any(int(x.get("published",0) or 0)>0 for x in blog)
 for result in blog:
  if result.get("error"):raise RuntimeError("Blog scheduler failed for "+str(result.get("task_id"))+": "+result["error"])
 if reviews:
  entries=check_source()
  today=datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()
  global_limit=max(0,int(claim.get("globalReviewLimit") or 0))
  for task in reviews:
   run_id=task["run_id"]
   try:
    api_state=request(token,"GET")
    if api_state.get("today")!=today:raise RuntimeError("GitHub and D1 Beijing dates disagree")
    count=sum(x.get("published_date")==today for x in api_state.get("recorded",[]))
    if count>=global_limit:
     chosen,prior=[],count
    else:
     chosen,prior=plan(entries,api_state,today,limit=global_limit)
     chosen=chosen[:max(0,int(task.get("daily_limit") or 0))]
    if not chosen:
     call(token,RUNNER_API,{"action":"complete","run_id":run_id,"published":0,"skipped":0})
     print("NO_UNUSED_REVIEWS",task["id"],"COUNT",prior,"LIMIT",global_limit)
     continue
    batch=[{"sourceFile":x["sourceFile"],"sourceRow":x["sourceRow"],"sourceModel":x["sourceModel"],"model":x["model"],"rating":x["rating"],"author":x["author"],"content":x["reviewBody"],"sourceFingerprint":x["sourceFingerprint"]} for x in chosen]
    result=request(token,"POST",{"date":today,"items":batch,"confirmedAuthentic":True})
    if not result.get("success") or result.get("inserted")!=len(batch):raise RuntimeError("D1 publication count mismatch; inspect ledger before retry")
    stored={(x["source_file"],x["source_row"],x["source_fingerprint"],x["published_date"]) for x in result.get("recorded",[])}
    if not all((x["sourceFile"],x["sourceRow"],x["sourceFingerprint"],today) in stored for x in batch):raise RuntimeError("Publication ledger reconciliation failed")
    call(token,RUNNER_API,{"action":"complete","run_id":run_id,"published":len(batch),"skipped":0})
    print("REVIEWS_PUBLISHED",len(batch),task["id"],"TODAY",result.get("todayCount"))
    changed=True
   except Exception as exc:
    try:call(token,RUNNER_API,{"action":"complete","run_id":run_id,"published":0,"skipped":0,"error":str(exc)[:400]})
    except Exception as completion_error:print("RUN_COMPLETION_ERROR",str(completion_error))
    raise
 if changed:dispatch_site_build()
if __name__=="__main__":main()

