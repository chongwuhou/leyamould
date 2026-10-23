#!/usr/bin/env python3
"""One-time exact-slug, owner-safe correction of Oct-23 editorial covers in D1.

Only the pre-reviewed API owns the three old/new cover pairs. This runner has
no arbitrary SQL or URL input; prints no secrets. Never modifies dist HTML.
"""
import json, os, urllib.error, urllib.request

EXPECTED={
 "hotel-resort-reusable-water-bottle-guest-amenity-sourcing",
 "ecommerce-private-label-water-bottle-marketplace-launch-checklist",
 "wholesale-water-bottle-distributor-assortment-planning",
}
URL="https://xuyibottles.com/api/admin/blog-batch-20261023"

def main():
    env=os.environ
    if not (env.get("GITHUB_ACTIONS")=="true"
        and env.get("GITHUB_EVENT_NAME")=="push"
        and env.get("GITHUB_REF")=="refs/heads/main"
        and env.get("GITHUB_REPOSITORY")=="chongwuhou/xuyi-drinkware-site"
        and env.get("CLOUDFLARE_ACCOUNT_ID")=="a4032d0251103d6ef680b2aaddce1afc"):
        raise SystemExit("Reviewed D1 migration requires the approved main GitHub workflow.")
    token=env.get("CLOUDFLARE_API_TOKEN")
    if not token:raise SystemExit("Required publishing credential unavailable.")
    request=urllib.request.Request(URL,
        data=b'{"fixApprovedCovers":true}',method="POST",headers={
         "Authorization":"Bearer "+token,
         "Content-Type":"application/json",
         "Accept":"application/json",
         "User-Agent":"XUYI-Approved-Blog-Cover-Fix/1.0"})
    try:
        with urllib.request.urlopen(request,timeout=90) as response:
            result=json.load(response)
    except urllib.error.HTTPError as error:
        try:detail=json.loads(error.read(1200)).get("error","Rejected")
        except Exception:detail="Rejected"
        raise RuntimeError(f"D1 cover repair blocked HTTP {error.code}: {str(detail)[:220]}") from None
    if not result.get("success"):
        raise RuntimeError("D1 cover repair not confirmed.")
    if result.get("alreadyFixed"):
        print("XUYI_OCT23_D1_APPROVED_COVERS_ALREADY_FIXED");return
    modified=set(result.get("updatedSlugs",[]))
    if modified!=EXPECTED or result.get("translatedRows")!=12 or result.get("indexRows")!=4:
        raise RuntimeError("D1 migration made unexpected number of changes; inspect before retry.")
    print("XUYI_OCT23_D1_COVER_REPAIR_CONFIRMED",
          "POSTS",len(modified),"LOCALIZED_HERO",result["translatedRows"],
          "LOCALIZED_INDEX",result["indexRows"],
          "REVISION",result.get("publishRevision"))
if __name__=="__main__":main()
