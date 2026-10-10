#!/usr/bin/env python3
"""Explicit indexing approval cannot deploy over old publicly cached sources."""
import sys
import urllib.error
import urllib.request
from search_submission import approved,ORIGIN

SENSITIVE=("/build.py","/site_renderer.py","/data/products.json")

def check():
    if not approved():
        print("XUYI_PUBLIC_INDEX_SECURITY_GUARD_IDLE: indexingApproved=false")
        return
    failed=[]
    for path in SENSITIVE:
        req=urllib.request.Request(ORIGIN+path,headers={"User-Agent":"XUYI-Launch-Security-Gate/1.0",
                                                      "Cache-Control":"no-cache"})
        try:
            with urllib.request.urlopen(req,timeout=15) as response:
                code=response.status
        except urllib.error.HTTPError as error:
            code=error.code
        if code not in (404,410):failed.append((path,code))
    if failed:
        raise RuntimeError("Refusing Google/Bing/Yandex/Baidu indexing release: "
                           "Cloudflare old-source cache is accessible: "+str(failed))
    print("XUYI_PREINDEX_SECURITY_GATE_PASSED all old source URLs return 404/410")

if __name__=="__main__":check()