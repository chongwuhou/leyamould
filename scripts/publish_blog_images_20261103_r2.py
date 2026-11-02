#!/usr/bin/env python3
"""Upload only the three SHA-256-reviewed 2026-11-03 Blog covers to XUYI R2."""
import hashlib,json,os
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from PIL import Image

ORIGIN="https://xuyibottles.com"
ENDPOINT="/api/admin/blog-images-20261103"

def require(ok,message):
    if not ok: raise RuntimeError(message)

def post_image(token,slug,path):
    boundary="----XUYI20261103ReviewedImageBoundary"
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
    require(os.environ.get("OWNER_BLOG1103_RELEASE")=="1","Owner dispatch flag missing")
    require(os.environ.get("GITHUB_ACTIONS")=="true","Only GitHub Actions may upload")
    require(os.environ.get("GITHUB_REPOSITORY")=="chongwuhou/xuyi-drinkware-site","Wrong repository")
    require(os.environ.get("GITHUB_REF")=="refs/heads/main","Only main may upload")
    token=os.environ.get("CLOUDFLARE_API_TOKEN","")
    require(bool(token),"Cloudflare project token missing")
    manifest=json.loads(Path("data/blog-images-reviewed-20261103.json").read_text(encoding="utf-8"))
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
      req=Request(ORIGIN+item["cover"],headers={"User-Agent":"XUYI-R2-cover-verification/1.0","Cache-Control":"no-cache"})
      with urlopen(req,timeout=30) as response:
        content=response.read()
        require(response.status==200 and response.headers.get("Content-Type","").split(";")[0].lower()=="image/webp","Public R2 media URL did not return WebP 200: "+item["slug"])
        require(hashlib.sha256(content).hexdigest()==digest,"Public media bytes differ from reviewed cover: "+item["slug"])
      print("R2_COVER_VERIFIED",item["slug"],"bytes",len(data),"sha256",digest)
    print("XUYI_20261103_THREE_REVIEWED_COVERS_R2_READY")
if __name__=="__main__": main()