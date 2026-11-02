import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {prepareScheduledPosts,validateLocalizedPayload} from "../functions/api/admin/blog-schedule-20261103.js";

const bundle=JSON.parse(readFileSync("_local_ops/blog-batch-20261103/payload.json","utf8"));
const prepared=prepareScheduledPosts();
assert.equal(prepared.length,3);
assert.deepEqual(prepared.map(x=>x.scheduledAt),[
  "2026-11-03T09:15:00+08:00",
  "2026-11-03T13:00:00+08:00",
  "2026-11-03T16:30:00+08:00"
]);
assert.equal(bundle.posts.length,3);
assert.equal(bundle.translations.length,12);
assert.equal(bundle.indexCards.length,12);
const validated=validateLocalizedPayload(bundle,prepared);
assert.equal(validated.translations.size,12);
assert.equal(validated.cards.size,12);
for(const p of prepared){
  for(const locale of ["es","pt","ru","tr"]){
    const key=p.slug+"|"+locale;
    const page=validated.translations.get(key);
    const card=validated.cards.get(key);
    assert.ok(page.title.length>12);
    assert.ok(page.description.length>25);
    assert.ok(page.mainHtml.length>5000);
    const articleSections=page.mainHtml.split('<section class="blog-section"').slice(1).map(x=>x.split("</section>",1)[0]);
    assert.equal(articleSections.filter(x=>x.includes('class="blog-editorial__product-link"')).length,3,"Localized product links must be naturally distributed across three sections: "+key);
    assert.ok(page.mainHtml.includes('src="'+p.post.cover+'"'));
    assert.ok(card.html.includes('src="'+p.post.cover+'"'));
    assert.ok(card.html.includes('href="/blog/'+p.slug+'/"'));
  }
}
console.log("XUYI_20261103_ALL_FIVE_LANGUAGES_VALID",{
  originals:3,localized:12,indexCards:12,totalPages:15
});