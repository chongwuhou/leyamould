"""Temporary, owner-safe pre-render CMS cover normalizer for the exact 2026-10-24
blog batch. Only runs until the D1 records have been repaired by the reviewed
batch endpoint. No rendered file is edited; remove after successful repair.
"""
from copy import deepcopy

FIXES={
 "trade-show-promotional-water-bottle-deadline-procurement":(
  "/assets/products/sports-alt.webp",
  "/assets/blog/water-bottle-sample-approval-20261017.webp"),
 "supplement-brand-shaker-bottle-bundle-oem-sourcing":(
  "/assets/products/shaker-alt.webp",
  "/assets/blog/replacement-water-bottle-lids-20261017.webp"),
 "outdoor-tour-operator-group-water-bottle-wholesale":(
  "/assets/products/jug-alt.webp",
  "/assets/blog/water-bottle-capacity-guide-20261017.webp")
}
LANGS={"es","pt","ru","tr"}
CARD='<article class="news-card">'

def index_with_reviewed_covers(body):
    parts=body.split(CARD)
    for slug,(old,new) in FIXES.items():
        needle='href="/blog/'+slug+'/"'
        found=0
        for i in range(1,len(parts)):
            head,sep,tail=parts[i].partition("</article>")
            if needle not in head:continue
            found+=1
            old_tag='src="'+old+'"'
            if old_tag in head:
                head=head.replace(old_tag,'src="'+new+'"',1)
            parts[i]=head+sep+tail
        if found>1:raise RuntimeError("Repeated reviewed blog card "+slug)
    return CARD.join(parts)

def curate_snapshot(snapshot):
    result=deepcopy(snapshot)
    if result.get("site")!="xuyi-drinkware-site" or result.get("schemaVersion")!=1:
        raise RuntimeError("Unexpected XUYI CMS snapshot")
    for row in result.get("translations",[]):
        if row.get("locale") not in LANGS:continue
        content=row.get("content")
        if not isinstance(content,dict) or not isinstance(content.get("mainHtml"),str):continue
        route=row.get("resourceId")
        if route=="page:/blog/":
            content["mainHtml"]=index_with_reviewed_covers(content["mainHtml"])
        else:
            for slug,(old,new) in FIXES.items():
                if route!="page:/blog/"+slug+"/":continue
                old_hero='<div class="blog-detail__cover"><img src="'+old+'"'
                if old_hero in content["mainHtml"]:
                    content["mainHtml"]=content["mainHtml"].replace(
                      old_hero,'<div class="blog-detail__cover"><img src="'+new+'"',1)
    return result
