#!/usr/bin/env python3
"""Public-asset reference inventory for XUYI's protected R2 media manager.

This is a static *deployed release* index, not an assertion that unpublished
D1 drafts do not reference a file; live D1 is also checked before deletion.
"""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import json,re
from urllib.parse import unquote

MEDIA=re.compile(r"/media/(?:ppt|excel|group|gallery|capability|blog|product|page|shared)/[a-zA-Z0-9._/-]+\.(?:webp|png|jpg|jpeg)",re.I)
def inventory(root:Path, overflow:Path|None=None):
    uses=defaultdict(set)
    for directory in [root,*([overflow] if overflow and overflow.exists() else [])]:
        for f in directory.rglob("*"):
            if not f.is_file() or f.suffix.lower() not in {".html",".js",".css",".json"}:continue
            if f.name=="r2-usage-index.json":continue
            # Never include admin/source files or potentially private JSON blobs.
            if directory==root and f.suffix==".json" and f.name not in {"build-meta.json"}:continue
            if f.stat().st_size>2_000_000:continue
            body=f.read_text(encoding="utf-8",errors="replace")
            if f.suffix==".html":
                directory_route=f.relative_to(directory).parent.as_posix()
                location="/" if directory_route=="." else "/"+directory_route.strip("/")+"/"
                if directory!=root:location="[overflow] "+location
            else:location="[runtime] "+"/"+f.relative_to(directory).as_posix()
            for match in set(MEDIA.findall(body)):
                uses[unquote(match)].add(location)
    return {key:sorted(value) for key,value in sorted(uses.items())}
def generate(root:Path,overflow:Path|None=None):
    refs=inventory(root,overflow)
    meta=json.loads((root/"build-meta.json").read_text(encoding="utf-8"))
    payload={"schemaVersion":1,"site":"xuyi-drinkware-site","publishRevision":meta["publishRevision"],
             "sourceRevision":meta["sourceRevision"],"references":refs}
    (root/"r2-usage-index.json").write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    return len(refs),sum(map(len,refs.values()))
if __name__=="__main__":
    root=Path(__file__).resolve().parent.parent
    print("XUYI_R2_REFERENCE_INDEX",*generate(root/"dist",root/"_local_ops/model-overflow"))
