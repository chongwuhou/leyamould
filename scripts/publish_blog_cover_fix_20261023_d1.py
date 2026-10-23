#!/usr/bin/env python3
"""Persist only the three reviewed Oct-23 Blog cover repairs through XUYI's
single-use, project-verified CMS endpoint. No arbitrary blog content is sent.
"""
import json,os,sys,urllib.request,urllib.error
URL="https://xuyibottles.com/api/admin/blog-batch-20261023"
ACCOUNT="a4032d0251103d6ef680b2aaddce1afc"
REPOSITORY="chongwuhou/xuyi-drinkware-site"
EXPECTED={
 "hotel-resort-reusable-water-bottle-guest-amenity-sourcing",
 "ecommerce-private-label-water-bottle-marketplace-launch-checklist",
 "wholesale-water-bottle-distributor-assortment-planning"
}
def main():
    if "--dry-run" in sys.argv:
        print("D1_APPROVED_BLOG_COVER_REPAIR_DRY_RUN",len(EXPECTED));return
    if (os.getenv("GITHUB_ACTIONS")!="true" or
        os.getenv("GITHUB_EVENT_NAME")!="push" or
        os.getenv("GITHUB_REF")!="refs/heads/main" or
        os.getenv("GITHUB_REPOSITORY")!=REPOSITORY or
        os.getenv("CLOUDFLARE_ACCOUNT_ID")!=ACCOUNT):
        raise RuntimeError("XUYI main release required for CMS repair")
    token=os.getenv("CLOUDFLARE_API_TOKEN")
    if not token:raise RuntimeError("Cloudflare secret unavailable")
    req=urllib.request.Request(URL,data=b'{"fixApprovedCovers":true}',method="POST",
      headers={"Authorization":"Bearer "+token,
               "Content-Type":"application/json",
               "Accept":"application/json",
               "User-Agent":"XUYI-Reviewed-Blog-Cover-CMS-Repair/1.0"})
    try:
        with urllib.request.urlopen(req,timeout=90) as response:result=json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError("Reviewed cover CMS repair rejected: HTTP "+str(error.code)+
                           " "+error.read(350).decode("utf8","replace")) from None
    if not result.get("success"):raise RuntimeError("No CMS repair confirmation")
    if result.get("alreadyFixed"):
        print("XUYI_BLOG_COVER_REPAIR_ALREADY_FIXED");return
    if set(result.get("updatedSlugs",[]))!=EXPECTED or result.get("translatedRows")!=12 or result.get("indexRows")!=4:
        raise RuntimeError("Approved covers not fully repaired in CMS; investigate before retry")
    print("XUYI_20261023_BLOG_COVERS_D1_PERSISTED",
          "ARTICLES",len(result["updatedSlugs"]),
          "TRANSLATIONS",result["translatedRows"],"INDICES",result["indexRows"],
          "PUBLISH_REVISION",result.get("publishRevision"))
if __name__=="__main__":main()
