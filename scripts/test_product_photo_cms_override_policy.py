#!/usr/bin/env python3
"""Owner-selected actual SKU photos may survive future all-site builds."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import shutil
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/"scripts"))
from apply_gpt_reviewed_shaker_hd import apply

dist=ROOT/"dist"
data=json.loads((ROOT/"data/gpt-reviewed-shaker-hd-20261013.json").read_text(encoding="utf8"))
approved=data["approved"]

with TemporaryDirectory(prefix="xuyi-sku-cms-") as td:
    target=Path(td)
    for row in approved:
        media=row["new"].lstrip("/")
        path=target/media
        path.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/media,path)
        for lang in ("","es/","pt/","ru/","tr/"):
            for sku in row["skuIds"]:
                file=target/lang/"products"/sku/"index.html"
                file.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(dist/lang/"products"/sku/"index.html",file)

    # One owner-approved replacement already reflected everywhere including
    # OG/schema; the legacy source should never be forcibly reinstated.
    customized=target/"es/products/501/index.html"
    old=approved[0]["new"]
    human="/assets/sku-hd/owner-approved-501-model.webp"
    source=customized.read_text(encoding="utf8")
    assert old in source
    customized.write_text(source.replace(old,human),encoding="utf8")

    # Another SKU still has the original image and should be upgraded.
    legacy=target/"pt/products/502/index.html"
    source=legacy.read_text(encoding="utf8")
    row=next(x for x in approved if x["skuIds"]==["502"])
    assert row["new"] in source
    legacy.write_text(source.replace(row["new"],row["old"]),encoding="utf8")

    assert apply(target)>0
    assert human in customized.read_text(encoding="utf8")
    result=legacy.read_text(encoding="utf8")
    assert row["new"] in result and row["old"] not in result

    pages={file:file.read_bytes() for file in target.rglob("index.html")}
    assert apply(target)==0
    assert all(file.read_bytes()==body for file,body in pages.items())
print("XUYI_SKU_IMAGE_CMS_OWNER_OVERRIDE_AND_REPEAT_BUILD_PASSED")