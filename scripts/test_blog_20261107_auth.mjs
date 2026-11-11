import assert from 'node:assert/strict';
import {authorizedReviewedBlogBatchRequest,authorizedReviewedBlogImageUploadRequest} from '../functions/_shared/build-auth.js';
const originalFetch=globalThis.fetch;
let verifications=0;
try{
 globalThis.fetch=async(url,options)=>{
   assert.ok(String(url).endsWith('/accounts/a4032d0251103d6ef680b2aaddce1afc/pages/projects/xuyi-drinkware-site'));
   assert.equal(options.headers.authorization,'Bearer XUYI_TEST_ONLY_TOKEN');
   verifications++;
   return Response.json({success:true,result:{name:'xuyi-drinkware-site'}});
 };
 const req=path=>new Request('https://xuyibottles.com'+path,{method:'POST',headers:{authorization:'Bearer XUYI_TEST_ONLY_TOKEN'}});
 assert.equal(await authorizedReviewedBlogBatchRequest(req('/api/admin/blog-batch'),{}),true);
 assert.equal(await authorizedReviewedBlogBatchRequest(req('/api/admin/blog-batch-20261107'),{}),false);
 assert.equal(await authorizedReviewedBlogImageUploadRequest(req('/api/admin/blog-images-20261107'),{}),true);
 assert.equal(await authorizedReviewedBlogBatchRequest(req('/api/admin/blog-batch-arbitrary'),{}),false);
 assert.equal(await authorizedReviewedBlogImageUploadRequest(req('/api/admin/blog-images-arbitrary'),{}),false);
 assert.equal(verifications,2);
 console.log('XUYI_20261107_EXACT_BLOG_R2_D1_GITHUB_CI_AUTH_PATHS_PASS');
}finally{globalThis.fetch=originalFetch;}

