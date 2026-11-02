import assert from "node:assert/strict";
import {prepareScheduledPosts} from "../functions/api/admin/blog-schedule-20261103.js";

const posts=prepareScheduledPosts();
assert.equal(posts.length,3);
assert.deepEqual(posts.map(x=>x.slug),[
  "bulk-water-bottles-for-school-student-programs",
  "parks-recreation-water-bottle-bulk-procurement",
  "corporate-wellness-water-bottle-bulk-sourcing"
]);
assert.deepEqual(posts.map(x=>x.scheduledAt),[
  "2026-11-03T09:15:00+08:00",
  "2026-11-03T13:00:00+08:00",
  "2026-11-03T16:30:00+08:00"
]);
for(const item of posts){
  assert.equal(item.post.updated,"2026-11-03");
  assert.ok(item.post.coverAlt.length>=40);
  assert.equal(item.post.sections.length,7);
  assert.equal(item.post.checklist.length,10);
  assert.equal(item.post.faqs.length,4);
  assert.equal(item.post.related.length,3);
  assert.ok(item.contentJson.length<100000);
}
console.log("XUYI_20261103_THREE_ENGLISH_D1_SCHEDULE_PAYLOADS_VALID",posts.length);