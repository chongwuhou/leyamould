#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
items=[
("custom-water-bottle-logo-printing-methods-bulk-order","assets/blog/branding-logo-options-20261013.webp","assets/blog/custom-water-bottle-logo-printing-methods-20261111.webp","Logo printing and branding options for custom water bottles in bulk"),
("which-water-bottle-closure-type-best-wholesale-order","assets/blog/water-bottle-cap-types-bulk-20261016.webp","assets/blog/water-bottle-cap-types-wholesale-20261111.webp","Water bottle closure types for a wholesale order"),
("corporate-wellness-water-bottle-capacity-bulk-order","assets/blog/water-bottle-capacity-guide-20261017.webp","assets/blog/corporate-wellness-water-bottle-capacity-20261111.webp","500ml, 750ml and 1L-class capacity planning for corporate bottle procurement"),
]
rows=[]
for slug,source,target,topic in items:
    src=ROOT/source; dst=ROOT/target
    with Image.open(src) as im:
        im.convert("RGB").resize((1200,800),Image.Resampling.LANCZOS).save(dst,"WEBP",quality=92,method=6)
    data=dst.read_bytes()
    rows.append({"slug":slug,"source":target,"cover":"/media/blog/"+Path(target).name,"sha256":hashlib.sha256(data).hexdigest(),"license":"Existing XUYI editorial asset; contextual illustration, not an exact SKU or factory photograph","fileBytes":len(data),"visualReview":"actual-image-and-article-compared","usageDisclosure":"Contextual illustration; no claim of a pictured XUYI customer, factory, exact SKU or certification."})
(ROOT/"data/blog-images-reviewed-20261111.json").write_text(json.dumps({"site":"xuyi-drinkware-site","images":rows},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("XUYI_20261111_THREE_REVIEWED_COVERS_R2_READY",len(rows),[(x["fileBytes"],x["sha256"][:12]) for x in rows])