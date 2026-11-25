import assert from "node:assert/strict";
import {readFileSync} from "node:fs";

const source=readFileSync(new URL("../functions/_shared/publish-scheduler.js",import.meta.url),"utf8");
assert.match(source,/export const AUTOMATIC_PUBLICATION_ENABLED=false/);
assert.match(source,/if\(!AUTOMATIC_PUBLICATION_ENABLED\)return \{claimed:\[\],globalReviewLimit:0,disabled:true\}/);
assert.match(source,/if\(!AUTOMATIC_PUBLICATION_ENABLED\)return \{published:0,skipped:0,needsReview:0,disabled:true\}/);
console.log("LEYA_AUTOMATIC_PUBLICATION_DISABLED");

