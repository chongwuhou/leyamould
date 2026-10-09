import { authorizedBuildRequest } from "../../_shared/build-auth.js";
import { checkedImage } from "../../_shared/media-image.js";
const reply=(data,status=200)=>Response.json(data,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow"}});
export async function onRequestPost(context){
 if(!context.env.ADMIN_TOKEN)return reply({error:"Admin secret missing"},503);
 if(!(await authorizedBuildRequest(context.request,context.env)))return reply({error:"Unauthorized"},401);
 const bucket=context.env.XUYI_ASSETS;if(!bucket)return reply({error:"XUYI_ASSETS missing"},503);
 const length=Number(context.request.headers.get("content-length")||0);
 if(length>7*1024*1024)return reply({error:"Image too large"},413);
 let form;try{form=await context.request.formData()}catch{return reply({error:"Invalid upload"},400)}
 const image=form.get("image");
 let media;try{media=await checkedImage(image)}catch(error){return reply({error:String(error.message||error)},400)}
 const filename=crypto.randomUUID().replace(/-/g,"").slice(0,28)+"."+media.extension;
 const key="site-blog/"+filename;
 await bucket.put(key,media.buffer,{httpMetadata:{contentType:media.type},customMetadata:{source:"xuyi-admin-blog"}});
 return reply({saved:true,path:"/media/blog/"+filename});
}