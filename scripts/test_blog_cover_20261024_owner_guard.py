"""Regression: exact old covers only, no overwrite of owner chosen CMS images."""
from reviewed_20261024_blog_covers import FIXES,curate_snapshot,CARD
slug="trade-show-promotional-water-bottle-deadline-procurement"
old,new=FIXES[slug]
card=lambda src,slug: CARD+'<a href="/blog/'+slug+'/"><img src="'+src+'"></a></article>'
sample={"site":"xuyi-drinkware-site","schemaVersion":1,"translations":[
 {"resourceId":"page:/blog/","locale":"es","content":{"mainHtml":card(old,slug)+card(old,"other")}},
 {"resourceId":"page:/blog/"+slug+"/","locale":"es","content":{"mainHtml":'<div class="blog-detail__cover"><img src="'+old+'"'}},
 {"resourceId":"page:/blog/"+slug+"/","locale":"pt","content":{"mainHtml":'<div class="blog-detail__cover"><img src="/assets/blog/owner-choice.webp"'}}
]}
fixed=curate_snapshot(sample)
assert new not in str(sample),"Mutation of source is forbidden"
assert card(new,slug) in fixed["translations"][0]["content"]["mainHtml"]
assert card(old,"other") in fixed["translations"][0]["content"]["mainHtml"]
assert new in fixed["translations"][1]["content"]["mainHtml"]
assert "owner-choice.webp" in fixed["translations"][2]["content"]["mainHtml"]
assert fixed==curate_snapshot(fixed),"Not idempotent"
print("XUYI_20261024_COVER_OWNER_PRIORITY_GUARD_OK")
