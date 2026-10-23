"""One-time, owner-safe CMS snapshot normalization for the reviewed Oct-23
cover collision migration. This is pre-render source input, NEVER a dist edit.
Remove this bridge once the D1 rows are repaired by the limited CMS endpoint.
"""
from copy import deepcopy

FIXES={
 "hotel-resort-reusable-water-bottle-guest-amenity-sourcing":(
  "/assets/editorial/large-capacity-plastic-jug.webp",
  "/assets/products/jug.webp"),
 "ecommerce-private-label-water-bottle-marketplace-launch-checklist":(
  "/assets/blog/custom-product-planning-20261013.webp",
  "/assets/products/sports.webp"),
 "wholesale-water-bottle-distributor-assortment-planning":(
  "/assets/editorial/sports-bottles-category-20261013.webp",
  "/assets/products/kids.webp")
}
LOCALES={"es","pt","ru","tr"}
CARD='<article class="news-card">'

def curate_index(body):
    parts=body.split(CARD)
    for slug,(old,new) in FIXES.items():
        needle='href="/blog/'+slug+'/"'
        found=0
        for i in range(1,len(parts)):
            head,sep,tail=parts[i].partition("</article>")
            if needle not in head:continue
            found+=1
            old_src='src="'+old+'"'
            new_src='src="'+new+'"'
            if old_src in head and new_src not in head:
                head=head.replace(old_src,new_src,1)
            parts[i]=head+sep+tail
        if found>1:raise RuntimeError("Repeated index card for "+slug)
    return CARD.join(parts)

def curate_snapshot(payload):
    output=deepcopy(payload)
    if output.get("site")!="xuyi-drinkware-site" or output.get("schemaVersion")!=1:
        raise RuntimeError("Refusing non-XUYI snapshot")
    for item in output.get("translations",[]):
        if item.get("locale") not in LOCALES:continue
        rid=item.get("resourceId")
        fields=item.get("content")
        if not isinstance(fields,dict) or not isinstance(fields.get("mainHtml"),str):continue
        body=fields["mainHtml"]
        if rid=="page:/blog/":
            fields["mainHtml"]=curate_index(body)
        else:
            for slug,(old,new) in FIXES.items():
                if rid!="page:/blog/"+slug+"/":continue
                anchor='<div class="blog-detail__cover"><img src="'
                old_hero=anchor+old+'"'
                if old_hero in body:
                    body=body.replace(old_hero,anchor+new+'"',1)
                fields["mainHtml"]=body
    return output
