"""Prove cover migration is source-level, idempotent and preserves owner-chosen images."""
from reviewed_20261023_blog_covers import curate_snapshot,FIXES
slug="ecommerce-private-label-water-bottle-marketplace-launch-checklist"
old,new=FIXES[slug]
related='other-guide'
card=lambda src,target:'<article class="news-card"><a href="/blog/'+target+'/"><img src="'+src+'"></a></article>'
sample={
 "site":"xuyi-drinkware-site","schemaVersion":1,
 "translations":[
  {"resourceId":"page:/blog/","locale":"es","content":{"mainHtml":card(old,slug)+card(old,related)}},
  {"resourceId":"page:/blog/"+slug+"/","locale":"es","content":{"mainHtml":'<div class="blog-detail__cover"><img src="'+old+'">'+card(old,related)}},
  {"resourceId":"page:/blog/"+slug+"/","locale":"pt","content":{"mainHtml":'<div class="blog-detail__cover"><img src="/assets/blog/owner-chosen.webp">'}}
 ]
}
changed=curate_snapshot(sample)
assert new not in str(sample),"Do not mutate caller CMS source"
index=changed["translations"][0]["content"]["mainHtml"]
assert card(new,slug) in index and card(old,related) in index
article=changed["translations"][1]["content"]["mainHtml"]
assert '<div class="blog-detail__cover"><img src="'+new+'"' in article
assert card(old,related) in article,"Do not modify another article's cover"
assert "owner-chosen.webp" in changed["translations"][2]["content"]["mainHtml"]
assert changed==curate_snapshot(changed),"Idempotent"
print("XUYI_OCT23_COVER_CMS_OWNER_PRIORITY_SOURCE_GUARD_PASS")
