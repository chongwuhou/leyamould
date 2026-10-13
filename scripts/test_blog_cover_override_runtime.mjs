import assert from "node:assert/strict";
import {withReviewedCover} from "../functions/blog/[[path]].js";
import guides from "../data/blog-guides.json" with {type:"json"};
import overrides from "../data/blog-cover-overrides.json" with {type:"json"};
import reviewedShakers from "../data/gpt-reviewed-shaker-hd-20261013.json" with {type:"json"};

const original=Object.fromEntries(guides.map(p=>[p.slug,"/media/ppt/"+p.cover]));
assert.equal(guides.length,16);
assert.equal(Object.keys(overrides).length,8);
const applied=guides.map(p=>withReviewedCover({slug:p.slug,cover:original[p.slug]}));
assert.equal(new Set(applied.map(p=>p.cover)).size,16,"D1 published list must have 16 unique covers");
for(const post of applied){
 const reviewedGuideCover=post.slug==="shaker-bottle-wholesale"
   ? reviewedShakers.approved.find(x=>x.old===original[post.slug])?.new
   : undefined;
 const expected=overrides[post.slug]||reviewedGuideCover||original[post.slug];
 assert.equal(post.cover,expected,post.slug);
 assert.equal(withReviewedCover({slug:post.slug,cover:"/assets/media/editor-updated.webp"}).cover,
              "/assets/media/editor-updated.webp",
              "Do not overwrite a later manual D1 editor cover selection");
}
assert.equal(withReviewedCover({slug:"new-independent-article",cover:"/media/blog/custom.webp"}).cover,
             "/media/blog/custom.webp");
console.log("XUYI_D1_BLOG_RUNTIME_COVER_DEDUP_PASSED, no D1 writes, editor overrides preserved");