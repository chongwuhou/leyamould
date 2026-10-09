#!/usr/bin/env python3
"""Safe local Fresh / CloneData scaffolding, adapted from Demalong's wizard.

This command NEVER creates Cloudflare resources, reads production D1/R2, or
copies secrets. CloneData copies only source-controlled PUBLIC catalog content;
it explicitly does not claim to copy remote D1 or R2. Those require a separate,
explicitly authorized migration and independent credentials.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import shutil
import sys

SRC=Path(__file__).resolve().parent.parent
RESERVED={"xuyi-drinkware-site","demalong-replacement-filters-auto"}
def require_config(path):
    cfg=json.loads(path.read_text(encoding="utf-8"))
    cloud=cfg.get("cloudflare") or {}
    site=cfg.get("site") or {}
    brand=cfg.get("brand") or {}
    project=cloud.get("pagesProjectName","")
    d1=cloud.get("d1Database","")
    r2=cloud.get("r2Bucket","")
    origin=site.get("origin","")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,60}",project) or project in RESERVED:
        raise RuntimeError("Destination Pages project must be a NEW unique name")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,60}",d1) or d1=="xuyi-drinkware-d1":
        raise RuntimeError("Destination D1 must be NEW")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,60}",r2) or r2=="xuyi-drinkware-r2":
        raise RuntimeError("Destination R2 must be NEW")
    if not re.fullmatch(r"https://[a-z0-9.-]+",origin) or origin=="https://xuyibottles.com":
        raise RuntimeError("Destination origin must be a different HTTPS hostname")
    if not brand.get("name") or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+",brand.get("email","")):
        raise RuntimeError("Destination brand name and email required")
    return cfg

def copy(src,dest):
    dest.parent.mkdir(parents=True,exist_ok=True)
    if src.is_dir():
        shutil.copytree(src,dest,dirs_exist_ok=False,
            ignore=shutil.ignore_patterns("__pycache__","*.pyc",".env*","*.log","dist","_local_ops"))
    else:shutil.copy2(src,dest)

def scaffold_html(cfg):
    title=cfg["brand"]["name"]
    email=cfg["brand"]["email"]
    escaped=lambda x:x.replace("&","&amp;").replace("<","&lt;").replace('"',"&quot;")
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>{escaped(title)}</title>
<meta name="description" content="Independent website scaffold.">
<link rel="stylesheet" href="/assets/site.css"></head>
<body><header class="header"><div class="shell header__inner"><a class="logo" href="/">{escaped(title)}</a>
<nav class="nav"><a class="nav__link" href="/">Home</a><a class="nav__link" href="/contact/">Contact</a></nav></div></header>
<main id="main-content"><section class="section"><div class="shell"><h1>{escaped(title)}</h1>
<p>New independent site scaffold. Add verified products and approved content before launching.</p>
<a class="button" href="/contact/">Contact us</a></div></section></main>
<footer class="section"><div class="shell"><a href="mailto:{escaped(email)}">{escaped(email)}</a></div></footer></body></html>'''

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",required=True,choices=["Fresh","CloneData"])
    parser.add_argument("--config",required=True,type=Path)
    parser.add_argument("--destination",required=True,type=Path)
    parser.add_argument("--dry-run",action="store_true")
    args=parser.parse_args()
    cfg=require_config(args.config.resolve())
    dest=args.destination.resolve()
    if dest==SRC or SRC in dest.parents or dest in SRC.parents:
        raise SystemExit("Destination must not overlap source or its parents")
    if dest.exists():raise SystemExit("Destination exists; refusing overwrite")
    if args.dry_run:
        print("CLONE_PREFLIGHT_OK",args.mode,dest,"NO_CHANGES")
        return
    dest.mkdir(parents=True)
    try:
        copy(SRC/"templates/site",dest/"templates/site")
        copy(SRC/"assets/site.css",dest/"assets/site.css")
        copy(SRC/"scripts/clone_site.py",dest/"scripts/clone_site.py")
        (dest/"deployment").mkdir()
        (dest/"deployment/site.config.json").write_text(
            json.dumps({"site":cfg["site"],"cloudflare":cfg["cloudflare"],
                "brand":cfg["brand"],"indexingApproved":False},indent=2),encoding="utf-8")
        (dest/"index.html").write_text(scaffold_html(cfg),encoding="utf-8")
        (dest/"contact/index.html").parent.mkdir(parents=True)
        (dest/"contact/index.html").write_text(scaffold_html(cfg),encoding="utf-8")
        if args.mode=="CloneData":
            # Source-controlled public materials only. No private D1 or R2 snapshots.
            copy(SRC/"data",dest/"data")
            copy(SRC/"assets/products",dest/"assets/products")
            copy(SRC/"assets/catalog",dest/"assets/catalog")
        (dest/"MIGRATION-RECEIPT.json").write_text(json.dumps({
            "source":"XUYI local public source template","mode":args.mode,
            "targetPagesProject":cfg["cloudflare"]["pagesProjectName"],
            "targetD1":cfg["cloudflare"]["d1Database"],
            "targetR2":cfg["cloudflare"]["r2Bucket"],
            "sourceControlledDataCloned":args.mode=="CloneData",
            "productionD1Migrated":False,"productionR2Migrated":False,
            "cloudflareResourcesCreated":False,"githubSecretsConfigured":False,
            "deploymentReady":False
        },indent=2),encoding="utf-8")
        print("XUYI_LOCAL_CLONE_CREATED",args.mode,str(dest))
    except Exception:
        shutil.rmtree(dest)
        raise

if __name__=="__main__":main()