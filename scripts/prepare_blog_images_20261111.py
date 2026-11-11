#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parent.parent
items=[
("custom-water-bottle-logo-printing-methods-bulk-order","assets/blog/branding-logo-options-20261013.webp","assets/blog/custom-water-bottle-logo-printing-photo-20261111.webp","Real product photography for custom bottle branding and logo-printing discussions"),
("which-water-bottle-closure-type-best-wholesale-order","assets/blog/replacement-water-bottle-lid-parts-photo-20261017.webp","assets/blog/water-bottle-closure-parts-photo-20261111.webp","Real product photography of bottle lids, seals and straw components for wholesale sourcing"),
("corporate-wellness-water-bottle-capacity-bulk-order","assets/blog/water-bottle-capacity-comparison-photo-20261017.webp","assets/blog/corporate-wellness-capacity-photo-20261111.webp","Real product photography comparing 500ml, 750ml and 1L-class bottle capacities"),
("wholesale-water-bottle-rfq-oem-pricing-checklist","assets/blog/water-bottle-sample-approval-photo-20261017.webp","assets/blog/wholesale-water-bottle-rfq-photo-20261111.webp","Natural product photography of a reusable bottle sample, cap components and quotation review materials for a wholesale RFQ"),
]
rows=[]
for slug,source,target,topic in items:
    src=ROOT/source; dst=ROOT/target
    with Image.open(src) as im:
        ImageOps.fit(im.convert("RGB"),(1200,800),method=Image.Resampling.LANCZOS,centering=(0.5,0.5)).save(dst,"WEBP",quality=92,method=6)
    data=dst.read_bytes()
    rows.append({"slug":slug,"source":target,"cover":"/media/blog/"+Path(target).name,"sha256":hashlib.sha256(data).hexdigest(),"license":"Existing XUYI editorial product photograph; not an exact SKU, customer or factory-line claim","fileBytes":len(data),"visualReview":"actual-image-and-article-compared","usageDisclosure":"Natural product photograph with no overlay graphic; final appearance may vary by confirmed SKU and production batch."})
(ROOT/"data/blog-images-reviewed-20261111.json").write_text(json.dumps({"site":"xuyi-drinkware-site","images":rows},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("XUYI_20261111_THREE_REVIEWED_COVERS_R2_READY",len(rows),[(x["fileBytes"],x["sha256"][:12]) for x in rows])

