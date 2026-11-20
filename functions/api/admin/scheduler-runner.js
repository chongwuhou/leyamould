import {authorizedSchedulerRunnerRequest} from "../../_shared/build-auth.js";
import {claimDuePublishTasks,publishDueBlogPosts,finishPublishRun} from "../../_shared/publish-scheduler.js";
const reply=(body,status=200)=>Response.json(body,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"}});
export async function onRequestPost(c){
 if(!(await authorizedSchedulerRunnerRequest(c.request,c.env)))return reply({error:"Unauthorized scheduler runner"},401);
 const db=c.env.LEYA_DB;if(!db)return reply({error:"LEYA_DB unavailable"},503);let input;try{input=await c.request.json()}catch{return reply({error:"Invalid JSON"},400)}
 try{
  if(input.action==="claim"){const result=await claimDuePublishTasks(db);const blog=[];for(const task of result.claimed.filter(x=>x.content_type==="blog")){try{const outcome=await publishDueBlogPosts(db,task);await finishPublishRun(db,task.run_id,outcome);blog.push({task_id:task.id,run_id:task.run_id,...outcome})}catch(e){const error=String(e.message||e);await finishPublishRun(db,task.run_id,{error});blog.push({task_id:task.id,run_id:task.run_id,error})}}
   return reply({claimed:result.claimed.filter(x=>x.content_type==="reviews").map(t=>({id:t.id,name:t.name,run_id:t.run_id,scheduled_for:t.scheduled_for,daily_limit:t.daily_limit,timezone:t.timezone})),globalReviewLimit:result.globalReviewLimit,blog});}
  if(input.action==="complete")return reply(await finishPublishRun(db,input.run_id,{published:input.published,skipped:input.skipped,error:input.error}));
  return reply({error:"Unknown runner action"},400);
 }catch(e){return reply({error:String(e.message||e)},500)}
}