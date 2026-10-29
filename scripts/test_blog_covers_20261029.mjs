import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
const images=JSON.parse(readFileSync("data/blog-reviewed-cover-r2-20261029.json","utf8")).images;
assert.equal(images.length,3);
for(const [i,p] of images.entries()){
 const post=JSON.parse(readFileSync("data/blog-guides-20261029-"+(i+1)+".json","utf8"));
 assert.equal(post.slug,p.slug);assert.equal(post.cover,p.cover);
 assert.match(p.cover,/^\/media\/blog\/[a-z0-9-]{20,70}\.webp$/);
 const buffer=readFileSync(p.source);
 assert.equal(createHash("sha256").update(buffer).digest("hex"),p.sha256);
}
const endpoint=readFileSync("functions/api/admin/blog-covers-20261029.js","utf8");
assert.ok(endpoint.includes("Owner-modified article cover preserved"));
assert.ok(endpoint.includes("translated_json"));
assert.ok(endpoint.includes("bucket.head"));
assert.ok(endpoint.includes("await db.batch(stmts)"));
const auth=readFileSync("functions/_shared/build-auth.js","utf8");
assert.ok(auth.includes('url.pathname!=="/api/admin/blog-covers-20261029"'));
console.log("XUYI_THREE_R2_IMAGES_SOURCE_HASH_OWNER_GUARD_PASS");
