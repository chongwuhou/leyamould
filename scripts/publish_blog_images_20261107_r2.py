#!/usr/bin/env python3
"""Upload only the three SHA-256-reviewed 2026-11-07 Blog covers to XUYI R2."""
import hashlib,json,os,time,sys
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from PIL import Image

ORIGIN="https://xuyibottles.com"
ENDPOINT="/api/admin/blog-images-20261107"

def require(ok,message):
    if not ok: raise RuntimeError(message)

def post_image(token,slug,path):
    boundary="----XUYI20261107ReviewedImageBoundary"
    data=path.read_bytes()
    body=b"".join([
      ("--"+boundary+"\r\nContent-Disposition: form-data; name=\"slug\"\r\n\r\n"+slug+"\r\n").encode(),
      ("--"+boundary+"\r\nContent-Disposition: form-data; name=\"image\"; filename=\""+path.name+"\"\r\nContent-Type: image/webp\r\n\r\n").encode(),
      data,
      ("\r\n--"+boundary+"--\r\n").encode()
    ])
    req=Request(ORIGIN+ENDPOINT,data=body,method="POST",headers={
      "Authorization":"Bearer "+token,"Content-Type":"multipart/form-data; boundary="+boundary,
      "Accept":"application/json","User-Agent":"XUYI-Reviewed-Blog-Cover-Upload/1.0"
    })
    try:
      with urlopen(req,timeout=60) as response: result=json.load(response)
    except HTTPError as err:
      raise RuntimeError("R2 image upload HTTP "+str(err.code)+" "+err.read(400).decode("utf8","replace")) from None
    except URLError as err:
      raise RuntimeError("R2 image upload network failure: "+str(err.reason)) from None
    require(result.get("saved") is True and result.get("sha256")==hashlib.sha256(data).hexdigest(),"R2 endpoint did not confirm exact image SHA for "+slug)
    return result

def main():
    if "--dry-run" in sys.argv:
        print("DRY_RUN_REVIEWED_B2B_20261107_R2",3);return
    require(os.environ.get("OWNER_BLOG1107_RELEASE")=="1","Owner dispatch flag missing")
    require(os.environ.get("GITHUB_ACTIONS")=="true","Only GitHub Actions may upload")
    require(os.environ.get("GITHUB_REPOSITORY")=="chongwuhou/xuyi-drinkware-site","Wrong repository")
    require(os.environ.get("GITHUB_REF")=="refs/heads/main","Only main may upload")
    token=os.environ.get("CLOUDFLARE_API_TOKEN","")
    require(bool(token),"Cloudflare project token missing")
    manifest=json.loads(Path("data/blog-images-reviewed-20261107.json").read_text(encoding="utf-8"))
    require(manifest.get("site")=="xuyi-drinkware-site" and len(manifest.get("images",[]))==3,"Wrong reviewed image manifest")
    for item in manifest["images"]:
      path=Path(item["source"])
      require(path.is_file(),"Missing approved source image "+str(path))
      data=path.read_bytes()
      digest=hashlib.sha256(data).hexdigest()
      require(digest==item["sha256"],"Source image changed after visual approval: "+item["slug"])
      require(30000<=len(data)<=350000,"Cover outside approved size range: "+item["slug"])
      with Image.open(path) as im:
        require(im.format=="WEBP" and im.size==(1200,800),"Cover must be 1200x800 WebP: "+item["slug"])
      post_image(token,item["slug"],path)
      # R2 writes are immediately confirmed by the authenticated upload response.
      # The public Pages media proxy may briefly serve a cached 404 while its
      # first object is propagating; use a fresh query key and retry read-back.
      last_error=None
      for attempt in range(6):
        verify_url=ORIGIN+item["cover"]+"?xuyi_r2_verify="+digest[:16]+"-"+str(attempt)
        req=Request(verify_url,headers={"User-Agent":"XUYI-R2-cover-verification/1.0","Cache-Control":"no-cache"})
        try:
          with urlopen(req,timeout=30) as response:
            public_bytes=response.read()
            require(response.status==200 and response.headers.get("Content-Type","").split(";")[0].lower()=="image/webp","Public R2 media URL did not return WebP 200: "+item["slug"])
            require(hashlib.sha256(public_bytes).hexdigest()==digest,"Public media bytes differ from reviewed cover: "+item["slug"])
          last_error=None
          break
        except HTTPError as err:
          last_error="HTTP "+str(err.code)+" "+err.read(240).decode("utf8","replace")
          if err.code not in (404,429,500,502,503,504) or attempt==5:
            raise RuntimeError("Public R2 media read-back failed for "+item["slug"]+": "+last_error) from None
        except URLError as err:
          last_error=str(err.reason)
          if attempt==5:
            raise RuntimeError("Public R2 media read-back network failure for "+item["slug"]+": "+last_error) from None
        if attempt<5:
          time.sleep(2+2*attempt)
      require(last_error is None,"Public R2 media read-back did not converge: "+item["slug"]+" "+str(last_error))
      print("R2_COVER_VERIFIED",item["slug"],"bytes",len(data),"sha256",digest)
    print("XUYI_20261107_THREE_REVIEWED_COVERS_R2_READY")
if __name__=="__main__": main()