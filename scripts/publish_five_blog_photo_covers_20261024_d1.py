#!/usr/bin/env python3
"""Strict, audit-friendly 5-article Blog photo cover migration.

Only this one reviewed action is available to production GitHub Actions.
No caller-provided slugs, URLs, SQL, content or arbitrary editorial changes.
"""
import json,os,urllib.error,urllib.request
EXPECTED={
 "water-bottle-cap-types-bulk-guide",
 "bottle-factory-rfq-template",
 "outdoor-tour-operator-group-water-bottle-wholesale",
 "supplement-brand-shaker-bottle-bundle-oem-sourcing",
 "trade-show-promotional-water-bottle-deadline-procurement"
}
URL="https://xuyibottles.com/api/admin/blog-photo-cover-20261024"
def main():
    e=os.environ
    if not (e.get("GITHUB_ACTIONS")=="true"
      and e.get("GITHUB_EVENT_NAME")=="push"
      and e.get("GITHUB_REF")=="refs/heads/main"
      and e.get("GITHUB_REPOSITORY")=="chongwuhou/xuyi-drinkware-site"
      and e.get("CLOUDFLARE_ACCOUNT_ID")=="a4032d0251103d6ef680b2aaddce1afc"):
        raise SystemExit("Release is allowed only in the owner-approved GitHub main workflow")
    token=e.get("CLOUDFLARE_API_TOKEN")
    if not token:raise SystemExit("Existing Cloudflare publishing credential missing")
    req=urllib.request.Request(URL,
       data=b'{"approvedFivePhotoCovers":true}',method="POST",
       headers={"Authorization":"Bearer "+token,
       "Content-Type":"application/json","Accept":"application/json",
       "User-Agent":"XUYI-Audited-Blog-Photo-Release/1.0"})
    try:
        with urllib.request.urlopen(req,timeout=95) as r:data=json.load(r)
    except urllib.error.HTTPError as err:
        try:detail=json.loads(err.read(1000)).get("error","Rejected")
        except Exception:detail="Rejected"
        raise RuntimeError(f"Reviewed CMS update denied HTTP {err.code}: {detail[:220]}") from None
    if data.get("success") is not True:raise RuntimeError("D1 did not confirm review-safe photo update")
    updated=set(data.get("updatedSlugs",[]))
    if not data.get("alreadyApplied") and updated!=EXPECTED:
        raise RuntimeError(f"Expected five approved untouched posts, updated {len(updated)}; check CMS owner edits")
    if not data.get("alreadyApplied") and (data.get("heroRows")!=20 or data.get("indexRows")!=4):
        raise RuntimeError("Unexpected translation/index update count; inspect D1 before retry")
    print("XUYI_FIVE_REVIEWED_PHOTO_COVERS_CONFIRMED",
      "POSTS",len(updated),"LOCALE_HERO",data.get("heroRows"),
      "LOCALE_INDEX",data.get("indexRows"),"REVISION",data.get("publishRevision"))
if __name__=="__main__":main()
