// Explicit full-site rebuild request; based on Demalong's D1 revision contract.
import { authorizedBuildRequest } from "../../_shared/build-auth.js";
import { bumpPublishRevision } from "../../_shared/site-settings.js";

const reply=(data,status=200)=>Response.json(data,{status,headers:{
  "cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"
}});

async function guard(context){
  if(!context.env.ADMIN_TOKEN)return reply({error:"Admin credentials missing"},503);
  if(!(await authorizedBuildRequest(context.request,context.env)))
    return reply({error:"Unauthorized"},401);
  if(!context.env.XUYI_DB)return reply({error:"XUYI_DB binding missing"},503);
  return null;
}
export async function onRequestGet(context){
  const denied=await guard(context);if(denied)return denied;
  try{
    const row=await context.env.XUYI_DB.prepare(
      "SELECT value FROM site_state WHERE key='publish_revision'"
    ).first();
    return reply({publishRevision:Number(row?.value||0),mode:"d1-revision-ci"});
  }catch{return reply({error:"Publish state unavailable"},503)}
}
export async function onRequestPost(context){
  const denied=await guard(context);if(denied)return denied;
  const result=await bumpPublishRevision(context.env.XUYI_DB);
  return reply({queued:true,...result,
    message:"Revision queued. Deployment depends on the XUYI GitHub Actions controller being enabled."});
}