import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {blogHtml, reviewedBlogRelatedAtEnd} from "../functions/_shared/blog-cms.js";

const posts=[1,2,3].map(i=>JSON.parse(readFileSync("data/blog-guides-20261102-"+i+".json","utf8")));
for(const post of posts){
  const related=reviewedBlogRelatedAtEnd(post);
  assert.equal((related.match(/class="blog-related__item"/g)||[]).length,3,"Exactly three live-D1 related cards: "+post.slug);
  for(const slug of post.related)assert.ok(related.includes('href="/blog/'+slug+'/"'),"Missing selected related slug "+slug);
  assert.equal(reviewedBlogRelatedAtEnd({...post,relatedReading:false}),"","Respect explicit owner disable: "+post.slug);
  const html=blogHtml(post);
  assert.equal((html.match(/class="blog-related__item"/g)||[]).length,3,"Dynamic D1 renderer must emit three cards: "+post.slug);
  assert.equal((html.match(/class="blog-editorial__product-link"/g)||[]).length,3,"Keep three contextual SKU links: "+post.slug);
  assert.ok(html.includes('class="blog-editorial__cta"'),"Preserve owner inquiry CTA: "+post.slug);
}
console.log("XUYI_20261102_LIVE_D1_ENGLISH_RELATED_CARDS_PASSED",posts.length);
