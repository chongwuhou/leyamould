#!/usr/bin/env python3
"""Upload three image-reviewed, exact-SHA 2026-11-01 covers into XUYI R2. No D1 write."""
import os,sys,json,hashlib,time,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
MANIFEST=json.loads((ROOT/"data/blog-images-reviewed-20261101.json").read_text("utf8"))
ENDPOINT="https://xuyibottles.com/api/admin/blog-images-20261101"
def upload(slug,data,token):
 boundary="----xuyi-reviewed-b2b-20261101"
 head=("--"+boundary+'\r\nContent-Disposition: form-data; name="slug"\r\n\r\n'+slug+'\r\n--'+boundary+'\r\nContent-Disposition: form-data; name="image"; filename="editorial.webp"\r\nContent-Type: image/webp\r\n\r\n').encode()
 body=head+data+('\r\n--'+boundary+'--\r\n').encode()
 req=urllib.request.Request(ENDPOINT,data=body,method="POST",headers={"Authorization":"Bearer "+token,"Content-Type":"multipart/form-data; boundary="+boundary,"User-Agent":"XUYI-Verified-Oct30-B2B-Covers"})
 for i in range(5):
  try:
   with urllib.request.urlopen(req,timeout=80) as r:return json.load(r)
  except urllib.error.HTTPError as e:
   msg=e.read(800).decode("utf8","replace")
   if e.code not in (429,500,502,503,504) or i==4:raise RuntimeError("R2 upload HTTP "+str(e.code)+": "+msg) from None
  except (urllib.error.URLError,TimeoutError):
   if i==4:raise
  time.sleep((4,8,14,22)[i])
def main():
 rows=MANIFEST["images"]
 assert len(rows)==3 and MANIFEST["site"]=="xuyi-drinkware-site"
 for row in rows:
  img=(ROOT/row["source"]).read_bytes()
  assert len(img)>=30000 and hashlib.sha256(img).hexdigest()==row["sha256"]
 if "--dry-run" in sys.argv:print("OCT31_THREE_REVIEWED_IMAGES_SOURCE_SHA_PASS");return
 assert os.getenv("GITHUB_ACTIONS")=="true" and os.getenv("GITHUB_EVENT_NAME")=="push"
 assert os.getenv("GITHUB_REPOSITORY")=="chongwuhou/xuyi-drinkware-site" and os.getenv("GITHUB_REF")=="refs/heads/main"
 assert os.getenv("OWNER_BLOG1101_RELEASE")=="1"
 token=os.environ["CLOUDFLARE_API_TOKEN"]
 for row in rows:
  obj=upload(row["slug"],(ROOT/row["source"]).read_bytes(),token)
  if obj.get("saved") is not True or obj.get("url")!=row["cover"] or obj.get("sha256")!=row["sha256"]:raise RuntimeError("R2 verification mismatch "+row["slug"])
  print("B2B_20261101_IMAGE_UPLOADED",row["slug"],row["cover"],flush=True)
 print("ALL_THREE_20261101_BLOG_IMAGES_IN_R2_CONFIRMED")
if __name__=="__main__":main()