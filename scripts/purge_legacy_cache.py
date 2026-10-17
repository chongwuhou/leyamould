#!/usr/bin/env python3
"""One-time exact legacy source cache purge for the XUYI Cloudflare zone.

Never purge all. Does not print tokens, zone IDs or full API bodies. Lack of
Zone Cache Purge permission is reported but does not block safe site releases.
"""
import json,os,urllib.error,urllib.request
ROOT="https://api.cloudflare.com/client/v4/"
HOST="xuyibottles.com"
LEGACY=("/build.py","/site_renderer.py","/data/products.json")
URLS=["https://"+host+route for host in (HOST,"www."+HOST) for route in LEGACY]
def main():
    token=os.environ.get("CLOUDFLARE_API_TOKEN","")
    if not token:
        print("XUYI_LEGACY_PURGE_BLOCKED missing token")
        return
    def api(path,method="GET",payload=None):
        req=urllib.request.Request(ROOT+path,method=method,
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={"Authorization":"Bearer "+token,"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req,timeout=25) as res:
                return res.status,json.load(res)
        except urllib.error.HTTPError as error:
            try:body=json.load(error)
            except (ValueError,UnicodeError):body={}
            return error.code,body
    # Zone ID verified for xuyibottles.com through the already-authorized
    # local Cloudflare account. The Pages CI token may have Cache Purge
    # permission even when it cannot list Zones; try exact URLs only.
    zone_id="c32f7ad3e72edcf182390b4deb90d9f9"
    status,reply=api("zones/"+zone_id+"/purge_cache","POST",{"files":URLS})
    if status==200 and reply.get("success"):
        print("XUYI_LEGACY_PURGE_REQUEST_ACCEPTED exact_urls",len(URLS))
    else:
        print("XUYI_LEGACY_PURGE_BLOCKED permission_or_api status",status,
              "errors",[x.get("code") for x in reply.get("errors",[])])
if __name__=="__main__":main()
