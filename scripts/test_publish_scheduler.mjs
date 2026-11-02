import assert from "node:assert/strict";
import {taskPublishedToday,dailyRemaining} from "../functions/_shared/publish-scheduler.js";
const runs=[
 {task_id:"blog-a",started_at:"2026-11-02 15:00:00",published_count:1,status:"partial"},
 {task_id:"blog-a",started_at:"2026-11-02 16:30:00",published_count:2,status:"success"},
 {task_id:"blog-a",started_at:"2026-11-02 17:00:00",published_count:7,status:"failed"},
 {task_id:"blog-b",started_at:"2026-11-02 16:30:00",published_count:3,status:"success"}
];
assert.equal(taskPublishedToday(runs,"blog-a","2026-11-02"),1);
assert.equal(taskPublishedToday(runs,"blog-a","2026-11-03"),2);
assert.equal(taskPublishedToday(runs,"blog-b","2026-11-03"),3);
assert.equal(taskPublishedToday(runs,"missing","2026-11-03"),0);
assert.equal(dailyRemaining(3,1,1,1),0,"a task cannot exceed its own daily limit");
assert.equal(dailyRemaining(3,1,2,0),2,"the task can use its remaining share of the global quota");
assert.equal(dailyRemaining(3,3,2,0),0,"the global daily limit remains authoritative");
assert.equal(dailyRemaining(3,0,2,1),1,"the task-specific remainder is enforced");
console.log("XUYI_SCHEDULER_GLOBAL_AND_PER_TASK_BLOG_QUOTAS_PASS");