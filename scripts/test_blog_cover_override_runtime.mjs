import assert from "node:assert/strict";
import {withReviewedCover,reviewedCoverAlt} from "../functions/blog/[[path]].js";
import {existsSync,readFileSync} from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
import guides from "../data/blog-guides.json" with {type:"json"};
import overrides from "../data/blog-cover-overrides.json" with {type:"json"};
import photoCorrections from "../data/blog-photo-corrections-20261024.json" with {type:"json"};
import photoCorrections26 from "../data/blog-photo-corrections-20261026.json" with {type:"json"};
import photoContextCorrections from "../data/blog-photo-context-corrections-20261026.json" with {type:"json"};
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
 const approved=photoCorrections[post.slug];
 const approvedPhoto=approved && original[post.slug]===approved.baseline ? approved.photo : undefined;
 const expected=approvedPhoto||overrides[post.slug]||reviewedGuideCover||original[post.slug];
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
assert.equal(Object.keys(photoContextCorrections).length,3,"Exactly the three Oct 26 article covers are reviewed");
assert.equal(Object.keys(photoCorrections26).length,3,"Exactly three earlier cover corrections should chain into the contextual images");
for(const [slug,pair] of Object.entries(photoContextCorrections)){
 assert.notEqual(pair.baseline,pair.photo,slug+': cover must change');
 assert.ok(pair.photo.startsWith('/assets/blog/'),slug+': cover must be a local site asset');
 const imagePath=path.join(ROOT,pair.photo.slice(1));
 assert.ok(existsSync(imagePath),slug+': reviewed image file must exist');
 const bytes=readFileSync(imagePath);
 assert.equal(bytes.toString('ascii',8,12),'WEBP',slug+': cover must be a valid WebP asset');
 // Contextual scene photos are applied to static localized pages by
 // blog_media_source.py. The live English D1 route must preserve its current
 // CMS-selected catalog photo rather than silently replacing it.
 assert.equal(withReviewedCover({slug,cover:pair.baseline}).cover,pair.baseline,slug+': current D1 CMS cover remains authoritative');
 const previous=photoCorrections26[slug];
 assert.ok(previous,slug+': earlier generic cover correction exists');
 assert.equal(previous.photo,pair.baseline,slug+': contextual static baseline follows the generic approved photo');
 assert.equal(withReviewedCover({slug,cover:previous.baseline}).cover,pair.baseline,slug+': original baseline upgrades only to the generic approved D1 photo');
 assert.equal(withReviewedCover({slug,cover:pair.photo}).cover,pair.photo,slug+': a CMS-selected contextual photo remains unchanged');
 assert.equal(reviewedCoverAlt({slug,cover:pair.photo}),'',slug+': runtime does not override ALT for a CMS-selected contextual photo');
 assert.equal(withReviewedCover({slug,cover:'/assets/blog/owner-selected.webp'}).cover,
              '/assets/blog/owner-selected.webp',slug+': a later CMS-selected cover wins');
 assert.equal(reviewedCoverAlt({slug,cover:'/assets/blog/owner-selected.webp'}),'',slug+': do not override a later cover ALT');
}
console.log("XUYI_D1_BLOG_RUNTIME_COVER_DEDUP_PASSED, no D1 writes, editor overrides preserved");