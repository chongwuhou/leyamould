import assert from "node:assert/strict";
import {withReviewedCover} from "../functions/blog/[[path]].js";
import guides from "../data/blog-guides.json" with {type:"json"};
import overrides from "../data/blog-cover-overrides.json" with {type:"json"};
import photoCorrections from "../data/blog-photo-corrections-20261024.json" with {type:"json"};
import reviewedShakers from "../data/gpt-reviewed-shaker-hd-20261013.json" with {type:"json"};

const original=Object.fromEntries(guides.map(p=>[p.slug,(p.cover.startsWith("/")?p.cover:"/media/ppt/"+p.cover)]));
assert(guides.length>=16);
assert.equal(Object.keys(overrides).length,8);
const applied=guides.map(p=>withReviewedCover({slug:p.slug,cover:original[p.slug]}));
assert.equal(new Set(applied.map(p=>p.cover)).size,guides.length,"Published covers must be distinct for all approved articles");
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
assert.equal(Object.keys(photoCorrections).length,5);
for(const [slug,pair] of Object.entries(photoCorrections)){
 assert.equal(withReviewedCover({slug,cover:pair.baseline}).cover,pair.photo,slug);
 assert.equal(withReviewedCover({slug,cover:pair.photo}).cover,pair.photo,slug+': idempotent');
 assert.equal(withReviewedCover({slug,cover:'/assets/blog/owner-uploaded.webp'}).cover,
              '/assets/blog/owner-uploaded.webp',slug+': CMS manual edit wins');
}
console.log("XUYI_D1_BLOG_RUNTIME_COVER_DEDUP_PASSED, no D1 writes, editor overrides preserved");