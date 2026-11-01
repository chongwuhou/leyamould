#!/usr/bin/env python3
"""Decode exact approved editorial WebP bytes from versioned source data in CI."""
from pathlib import Path
from hashlib import sha256
from PIL import Image
import base64,io,json
ROOT=Path(__file__).resolve().parent.parent
manifest=json.loads((ROOT/"data/blog-images-reviewed-20261101.json").read_text("utf8"))
def main():
 assert len(manifest["images"])==3
 for row in manifest["images"]:
  original=(ROOT/row["sourceBase64"]).read_text("ascii")
  contents=base64.b64decode("".join(original.split()),validate=True)
  assert sha256(contents).hexdigest()==row["sha256"]
  with Image.open(io.BytesIO(contents)) as img:
   assert img.format=="WEBP" and img.size==(1200,800)
  assert 30000<=len(contents)<=350000
  out=ROOT/row["source"]
  out.parent.mkdir(parents=True,exist_ok=True)
  if out.exists() and out.read_bytes()!=contents:raise RuntimeError("existing approved media differs: "+str(out))
  out.write_bytes(contents)
  print("EXACT_B2B_IMAGE_RESTORED",row["slug"],len(contents),flush=True)
if __name__=="__main__":main()