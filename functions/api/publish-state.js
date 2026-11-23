// LEYA MOULD authenticated revision endpoint.
// LEYA-specific bindings; no access to unrelated data.
import { authorizedBuildRequest } from "../_shared/build-auth.js";

const response=(data,status=200)=>Response.json(data,{status,headers:{
  "cache-control":"no-store","x-robots-tag":"noindex,nofollow,noarchive"
}});

export async function onRequestGet(context){
  if(!(await authorizedBuildRequest(context.request,context.env))){
    return response({error:"Unauthorized"},401);
  }
  if(!context.env.LEYA_DB)return response({error:"LEYA_DB binding missing"},503);
  try{
    const rows=await context.env.LEYA_DB.prepare(
      "SELECT key,value FROM site_state WHERE key IN ('publish_revision','publish_requested_at')"
    ).all();
    const state=Object.fromEntries((rows.results||[]).map(r=>[r.key,r.value]));
    return response({
      publishRevision:Number(state.publish_revision||0),
      publishRequestedAt:state.publish_requested_at||""
    });
  }catch(err){return response({error:"Publishing state unavailable"},503)}
}

