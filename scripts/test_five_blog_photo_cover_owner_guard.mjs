import assert from "node:assert/strict";
import {PHOTO_COVERS,PHOTO_SLUGS,changeBlogPostCover,changeLocalizedBlogHero,changeLocalizedIndex} from "../functions/_shared/blog-photo-cover-guard.js";
assert.equal(PHOTO_SLUGS.length,5);
assert.equal(new Set(Object.values(PHOTO_COVERS).map(x=>x[1])).size,5);
for(const slug of PHOTO_SLUGS){
 const [oldCover,newCover]=PHOTO_COVERS[slug];
 assert.equal(changeBlogPostCover({cover:oldCover},slug).cover,newCover);
 assert.equal(changeBlogPostCover({cover:newCover},slug).cover,newCover);
 assert.equal(changeBlogPostCover({cover:"/assets/blog/owner-edit.webp"},slug).cover,"/assets/blog/owner-edit.webp");
 const hero='<div class="blog-detail__cover"><img src="'+oldCover+'" alt="real photo"><p>owner text</p>';
 const replacement=changeLocalizedBlogHero(hero,slug);
 assert(replacement.includes('src="'+newCover+'"'));
 assert(replacement.includes('owner text'));
 assert.equal(changeLocalizedBlogHero(replacement,slug),replacement);
 assert.equal(changeLocalizedBlogHero('<div class="blog-detail__cover"><img src="/assets/blog/owner-photo.webp"',slug),'<div class="blog-detail__cover"><img src="/assets/blog/owner-photo.webp"');
}
const [a,b]=PHOTO_SLUGS;
const oldA=PHOTO_COVERS[a][0],oldB=PHOTO_COVERS[b][0];
const make=(slug,img)=>'<article class="news-card"><a class="news-card__image" href="/blog/'+slug+'/"><img src="'+img+'"></a><p>owner body</p></article>';
const sample=make(a,oldA)+make(b,oldB)+make("owner-chosen","/assets/blog/owner-image.webp");
const next=changeLocalizedIndex(sample,[a,b]);
assert(next.includes(PHOTO_COVERS[a][1])&&next.includes(PHOTO_COVERS[b][1]));
assert(next.includes('/assets/blog/owner-image.webp'));
assert.equal(changeLocalizedIndex(next,[a,b]),next);
assert(!next.includes('src="'+oldA+'"')&&!next.includes('src="'+oldB+'"'));
assert.equal(changeLocalizedIndex(make(a,"/assets/blog/owner-photo.webp"),[a]),make(a,"/assets/blog/owner-photo.webp"));
console.log("XUYI_FIVE_BLOG_PHOTO_SOURCE_OWNER_OVERRIDE_AND_IDEMPOTENCE_PASS");
