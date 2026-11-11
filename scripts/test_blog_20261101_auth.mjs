import assert from "node:assert/strict";
import {authorizedReviewedBlogImageUploadRequest,authorizedReviewedBlogBatchRequest} from "../functions/_shared/build-auth.js";

const originalFetch=globalThis.fetch;
globalThis.fetch=async (url,options)=>{
 assert.equal(url,"https://api.cloudflare.com/client/v4/accounts/a4032d0251103d6ef680b2aaddce1afc/pages/projects/xuyi-drinkware-site");
 const allowed=options.headers.authorization==="Bearer xuyi-reviewed-20261101-ci";
 return Response.json({success:allowed,result:{name:allowed?"xuyi-drinkware-site":"other-site"}},{status:allowed?200:403});
};
const request=(route,method="POST",token="xuyi-reviewed-20261101-ci")=>new Request("https://xuyibottles.com"+route,{
 method,headers:{Authorization:"Bearer "+token}
});
const imagePath="/api/admin/blog-images-20261103";
const blogPath="/api/admin/blog-batch";
assert.equal(await authorizedReviewedBlogImageUploadRequest(request(imagePath),{}),true);
assert.equal(await authorizedReviewedBlogBatchRequest(request(blogPath),{}),true);
assert.equal(await authorizedReviewedBlogBatchRequest(request("/api/admin/blog-schedule-20261103"),{}),false);
assert.equal(await authorizedReviewedBlogImageUploadRequest(request(imagePath,"GET"),{}),false);
assert.equal(await authorizedReviewedBlogBatchRequest(request(blogPath,"GET"),{}),false);
assert.equal(await authorizedReviewedBlogImageUploadRequest(request("/api/admin/blog-images-20261101"),{}),false);
assert.equal(await authorizedReviewedBlogBatchRequest(request("/api/admin/blog-batch-20261101"),{}),false);
assert.equal(await authorizedReviewedBlogImageUploadRequest(request(imagePath,"POST","wrong-token"),{}),false);
assert.equal(await authorizedReviewedBlogBatchRequest(request(blogPath,"POST","wrong-token"),{}),false);
globalThis.fetch=originalFetch;
console.log("XUYI_20261103_REVIEWED_IMAGE_AND_SCHEDULE_CI_TOKEN_GATES_OK");

