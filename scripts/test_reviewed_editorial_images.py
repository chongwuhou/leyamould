#!/usr/bin/env python3
"""Five-language page scope, integrity and no-SKU-art-substitution gate."""
import sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
from reviewed_editorial_images import LOCALES,EDITORIAL_IMAGES,OEM_NEW,OEM_OLD
DIST=ROOT/"dist"
paths=[v[1] for v in EDITORIAL_IMAGES.values()]+[OEM_NEW]
for p in paths:
    f=DIST/p.lstrip("/")
    assert f.is_file(),p
    with Image.open(f) as image:
        assert image.format=="WEBP" and min(image.size)>=1000,(p,image.size)
for lang in LOCALES:
    prefix="" if lang=="en" else lang+"/"
    href_prefix="/" if lang=="en" else "/"+lang+"/"
    general=(DIST/prefix/"applications/everyday-hydration/index.html").read_text(encoding="utf-8")
    for category,(old,new) in EDITORIAL_IMAGES.items():
        text='<a class="category" href="'+href_prefix+'collections/'+category+'/"><div class="category__photo"><img src="'+new+'"'
        assert general.count(text)==1,(lang,category)
    oem=(DIST/prefix/"capabilities/oem-odm/index.html").read_text(encoding="utf-8")
    assert oem.count('<div class="whyv2-oem-steps__sample"><img src="'+OEM_NEW+'"')==1,lang
    assert OEM_OLD not in oem,lang
    for doc in (general,oem):
        assert "AI concept illustration" not in doc
        assert "AI-generated illustration" not in doc
        assert "ai-reviewed" not in doc
for f in DIST.glob("**/products/*/index.html"):
    s=f.read_text(encoding="utf-8")
    assert all(p not in s for p in paths),("Different SKU represented by a generic image",str(f))
assert (ROOT/"_local_ops/ai-review-2026-10-13/backup-original-oem-sampling.webp").is_file()
for x in ("slide-059.webp","slide-055.webp","slide-030.webp"):
    assert (ROOT/"_local_ops/ai-review-2026-10-13"/("original-"+x)).is_file(),x
print("XUYI_EDITORIAL_IMAGES_FIVE_LANGUAGES_PASSED 4 reviewed placements per locale, no product SKU changes")