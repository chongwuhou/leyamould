#!/usr/bin/env python3
"""Only owner-approved 2026-10-29 images, uploaded to XUYI R2 via a locked endpoint."""
from pathlib import Path
import os,sys,json,time,hashlib,urllib.request,urllib.error
ROOT=Path(__file__).resolve().parent.parent
ROWS=json.loads((ROOT/"data/blog-reviewed-cover-r2-20261029.json").read_text("utf8"))["images"]
URL="https://xuyibottles.com/api/admin/blog-covers-20261029"
def call(mode,data,content_type):
 request=urllib.request.Request(URL+"?mode="+mode,method="POST",data=data,headers={"Content-Type":content_type,"Authorization":"Bearer "+os.environ["CLOUDFLARE_API_TOKEN"],"User-Agent":"XUYI-Reviewed-Covers/2026-10-29"})
 for attempt in range(5):
  try:
   with urllib.request.urlopen(request,timeout=70) as res:return json.load(res)
  except urllib.error.HTTPError as e:
   reason=e.read(600).decode("utf8","replace")
   if e.code not in (429,500,502,503,504) or attempt==4:raise RuntimeError("R2 CMS API HTTP "+str(e.code)+" "+reason) from None
  except (urllib.error.URLError,TimeoutError):
   if attempt==4:raise
  time.sleep((4,8,12,18)[attempt])
def upload_body(slug,image):
 boundary="----xuyireviewed20261029"
 head=("--"+boundary+'\r\nContent-Disposition: form-data; name="slug"\r\n\r\n'+slug+'\r\n--'+boundary+'\r\nContent-Disposition: form-data; name="image"; filename="reviewed.webp"\r\nContent-Type: image/webp\r\n\r\n').encode()
 return head+image+('\r\n--'+boundary+'--\r\n').encode(),"multipart/form-data; boundary="+boundary
def main():
 assert len(ROWS)==3
 for row in ROWS:
  img=(ROOT/row["source"]).read_bytes()
  assert len(img)>25000 and hashlib.sha256(img).hexdigest()==row["sha256"]
 if "--dry-run" in sys.argv:print("THREE_REVIEWED_R2_COVERS_SOURCE_HASHES_PASS");return
 assert os.environ.get("GITHUB_ACTIONS")=="true" and os.environ.get("GITHUB_EVENT_NAME")=="push"
 assert os.environ.get("GITHUB_REF")=="refs/heads/main" and os.environ.get("GITHUB_REPOSITORY")=="chongwuhou/xuyi-drinkware-site"
 assert os.environ.get("OWNER_COVER_RELEASE")=="1"
 for row in ROWS:
  data,kind=upload_body(row["slug"],(ROOT/row["source"]).read_bytes())
  result=call("upload",data,kind)
  if not result.get("saved") or result.get("path")!=row["cover"] or result.get("sha256")!=row["sha256"]:raise RuntimeError("R2 image was not verified for "+row["slug"])
  print("R2_REVIEWED_IMAGE_VERIFIED",row["slug"],flush=True)
 result=call("commit",b"{}","application/json")
 if not result.get("success"):raise RuntimeError("D1 cover update unconfirmed: "+str(result)[:400])
 print("R2_THREE_IMAGES_CMS_UPDATED",result.get("changed"),"revision",result.get("publishRevision"))
if __name__=="__main__":main()
