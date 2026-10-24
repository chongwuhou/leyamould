#!/usr/bin/env python3
"""Restricted one-time, idempotent repair of the three already-published
XUYI Oct 24 B2B blog cover records. No arbitrary SQL or caller-supplied art.
"""
import json,os,urllib.request,urllib.error

EXPECTED={
 "trade-show-promotional-water-bottle-deadline-procurement",
 "supplement-brand-shaker-bottle-bundle-oem-sourcing",
 "outdoor-tour-operator-group-water-bottle-wholesale"
}
URL="https://xuyibottles.com/api/admin/blog-batch-20261024"
def main():
    e=os.environ
    if not (e.get("GITHUB_ACTIONS")=="true"
        and e.get("GITHUB_EVENT_NAME")=="push"
        and e.get("GITHUB_REF")=="refs/heads/main"
        and e.get("GITHUB_REPOSITORY")=="chongwuhou/xuyi-drinkware-site"
        and e.get("CLOUDFLARE_ACCOUNT_ID")=="a4032d0251103d6ef680b2aaddce1afc"):
        raise SystemExit("Reviewed D1 repair requires the owner-approved GitHub workflow.")
    token=e.get("CLOUDFLARE_API_TOKEN")
    if not token:raise SystemExit("Configured publishing token unavailable")
    req=urllib.request.Request(URL,data=b'{"fixReviewedCovers":true}',
        method="POST",headers={"Authorization":"Bearer "+token,
        "Content-Type":"application/json","Accept":"application/json",
        "User-Agent":"XUYI-20261024-Approved-Cover-Repair/1.0"})
    try:
        with urllib.request.urlopen(req,timeout=90) as r:result=json.load(r)
    except urllib.error.HTTPError as exc:
        try:reason=json.loads(exc.read(1000)).get("error","Rejected")
        except Exception:reason="Rejected"
        raise RuntimeError(f"Approved D1 repair refused HTTP {exc.code}: {str(reason)[:220]}") from None
    if result.get("success") is not True:raise RuntimeError("D1 did not confirm cover repair")
    if result.get("alreadyFixed") is True:
        print("XUYI_20261024_D1_COVERS_ALREADY_APPROVED");return
    names=set(result.get("updatedSlugs",[]))
    if names!=EXPECTED or result.get("translatedRows")!=12 or result.get("indexRows")!=4:
        raise RuntimeError("Unexpected D1 correction count; manual review needed")
    print("XUYI_20261024_D1_APPROVED_COVERS",
          "POSTS",len(names),"LOCALE_HERO",result["translatedRows"],
          "LOCALE_INDEX",result["indexRows"],
          "REVISION",result.get("publishRevision"))
if __name__=="__main__":main()
