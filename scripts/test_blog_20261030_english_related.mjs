import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {reviewedBlogRelatedAtEnd} from "../functions/_shared/blog-cms.js";
const source=filename=>JSON.parse(readFileSync("data/"+filename,"utf8"));
const approved=[...Array.from({length:3},(_,i)=>source("blog-guides-20261029-"+(i+1)+".json")),...Array.from({length:3},(_,i)=>source("blog-guides-20261030-"+(i+1)+".json"))];
for(const post of approved){
 const rendered=reviewedBlogRelatedAtEnd(post);
 assert.equal((rendered.match(/class="blog-related__item"/g)||[]).length,3,"Three specific English related links: "+post.slug);
 for(const slug of post.related)assert.ok(rendered.includes('href="/blog/'+slug+'/"'),"Exact related slug missing "+slug);
 assert.equal(reviewedBlogRelatedAtEnd({...post,relatedReading:false}),"","Respect owner explicit disable");
 const custom={...post,related:[post.related[1],post.related[0],post.related[2]],intro:"Owner edits their own article intro"};
 const customRendered=reviewedBlogRelatedAtEnd(custom);
 assert.ok(customRendered.includes('href="/blog/'+post.related[1]+'/"'),"Owner custom related selection preserved");
 const edited={...post,intro:"Owner edits article text",related:[]};
 assert.equal(reviewedBlogRelatedAtEnd(edited),"","Never reinsert old related after owner removes and rewrites text");
}
console.log("XUYI_20261029_30_EN_D1_OWNER_RELATED_THREE_LINKS_CMS_AUTHORITY_PASSED",approved.length);
