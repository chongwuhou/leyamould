#!/usr/bin/env python3
"""XUYI Pages/R2 hybrid model page planner.

Only pages under /products/<slug>/ and /<locale>/products/<slug>/ qualify.
No Blog, homepage, admin, images or other business pages ever overflow.
"""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
VALID_SLUG=re.compile(r"[a-z0-9][a-z0-9_-]{0,78}",re.I)
PLANNED_BUCKET="xuyi-drinkware-model-pages"
# Tombstone three historical source URLs using Pages Functions, even when
# using static-mode product pages. This does not consume dynamic requests for
# unrelated public pages.
RETIRED_SOURCE_PATHS=("/build.py","/site_renderer.py","/data/products.json")

def approved_prefixes(dist:Path):
    manifest=dist/"locale-manifest.json"
    if manifest.is_file():
        data=json.loads(manifest.read_text(encoding="utf-8"))
        if data.get("site")!="xuyi-drinkware-site":
            raise ValueError("Refusing overflow from another site")
        return tuple(x["pathPrefix"] for x in data["locales"] if x["pathPrefix"])
    # Isolated test fixture or legacy local build with no registry artifact:
    # discover *existing* route folders, never fabricate another language.
    return tuple(sorted(f.name for f in dist.iterdir() if f.is_dir()
                        and re.fullmatch(r"[a-z]{2,3}(?:-[a-z0-9-]+)?",f.name)
                        and (f/"products").is_dir()))

def plan(dist:Path,output:Path,*,switch_at:int=16000,target:int=15500,hard_stop:int=19500):
    dist=Path(dist);output=Path(output)
    if not (0<target<switch_at<hard_stop<=20000):
        raise ValueError("Invalid Pages safety budget")
    before=sum(f.is_file() for f in dist.rglob("*"))
    prefixes=approved_prefixes(dist)
    # Group only existing approved detail routes; preserve route/locale parity
    # by migrating all generated language variants of a given model together.
    groups={}
    base=dist/"products"
    if base.exists():
        for file in sorted(base.glob("*/index.html")):
            slug=file.parent.name
            if not VALID_SLUG.fullmatch(slug):continue
            pages={f"/products/{slug}/":file}
            for loc in prefixes:
                local=dist/loc/"products"/slug/"index.html"
                if local.is_file():pages[f"/{loc}/products/{slug}/"]=local
            groups[slug]=pages
    overflow={}
    current=before
    if before>=switch_at:
        for slug in sorted(groups,reverse=True):
            if current<=target:break
            pages=groups[slug]
            payload={"schemaVersion":1,"site":"xuyi-drinkware-site","model":slug,
                     "routes":{route:file.read_text(encoding="utf8") for route,file in sorted(pages.items())}}
            key=f"models/{slug}.json"
            raw=(json.dumps(payload,ensure_ascii=False,separators=(",",":"))+"\n").encode("utf8")
            output_file=output/key;output_file.parent.mkdir(parents=True,exist_ok=True)
            output_file.write_bytes(raw)
            overflow[slug]={"key":key,"sha256":hashlib.sha256(raw).hexdigest(),
                            "bytes":len(raw),"routes":list(payload["routes"])}
            for file in pages.values():file.unlink()
            current-=len(pages)
        if current>target:
            raise RuntimeError(f"Cannot move enough XUYI models to R2 ({current}>{target}); fail closed")
    if current>=hard_stop:
        raise RuntimeError(f"Cloudflare Pages hard stop {current}>={hard_stop}")
    route_includes=["/api/*","/blog/*","/media/*",*RETIRED_SOURCE_PATHS]
    if overflow:
        route_includes+=["/products/*"]+[f"/{loc}/products/*" for loc in prefixes]
    (dist/"_routes.json").write_text(json.dumps({"version":1,"include":route_includes,"exclude":[]},indent=2)+"\n",encoding="utf8")
    manifest={"schemaVersion":1,"site":"xuyi-drinkware-site","bucket":PLANNED_BUCKET,
              "mode":"hybrid" if overflow else "static",
              "projectedStaticFileCountBeforeOverflow":before,
              "staticFileCountAfterOverflow":current+1,
              "catalogModelCount":len(groups),
              "modelCount":len(overflow),
              "localizedPageCount":sum(len(v["routes"])-1 for v in overflow.values()),
              "objects":[{"key":v["key"],"sha256":v["sha256"],"bytes":v["bytes"]} for v in overflow.values()],
              "routes":[route for obj in overflow.values() for route in obj["routes"]]}
    output.mkdir(parents=True,exist_ok=True)
    (output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    return manifest

if __name__=="__main__":
    import argparse
    a=argparse.ArgumentParser()
    a.add_argument("--dist",type=Path,default=ROOT/"dist")
    a.add_argument("--output",type=Path,default=ROOT/"_local_ops/model-overflow")
    a.add_argument("--switch-at",type=int,default=16000)
    a.add_argument("--target",type=int,default=15500)
    a.add_argument("--hard-stop",type=int,default=19500)
    args=a.parse_args()
    manifest=plan(args.dist,args.output,switch_at=args.switch_at,target=args.target,hard_stop=args.hard_stop)
    print("XUYI_MODEL_OVERFLOW_PLAN",manifest["mode"],
          "models",manifest["modelCount"],"locales",manifest["localizedPageCount"],
          "files_before",manifest["projectedStaticFileCountBeforeOverflow"])
