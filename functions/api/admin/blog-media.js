import { authorizedBuildRequest } from "../../_shared/build-auth.js";
const types=new Map([["image/jpeg","jpg"],["image/png","png"],["image/webp","webp"]]);
const reply=(data,status=200)=>Response.json(data,{status,headers:{"cache-control":"no-store","x-robots-tag":"noindex,nofollow"}});
function validMagic(type,b){
 const v=new Uint8Array(b);
 if(type==="image/jpeg")return v[0]===255&&v[1]===216&&v[2]===255;
 if(type==="image/png")return v[0]===137&&v[1]===80&&v[2]===78&&v[3]===71;
 if(type==="image/webp")return String.fromCharCode(...v.slice(0,4))==="RIFF"&&String.fromCharCode(...v.slice(8,12))==="WEBP";
 return false;
}
export async function onRequestPost(context){
 if(!context.env.ADMIN_TOKEN)return reply({error:"Admin secret missing"},503);
 if(!(await authorizedBuildRequest(context.request,context.env)))return reply({error:"Unauthorized"},401);
 const bucket=context.env.XUYI_ASSETS;if(!bucket)return reply({error:"XUYI_ASSETS missing"},503);
 const length=Number(context.request.headers.get("content-length")||0);
 if(length>7*1024*1024)return reply({error:"Image too large"},413);
 let form;try{form=await context.request.formData()}catch{return reply({error:"Invalid upload"},400)}
 const image=form.get('image');
 if(!(image instanceof File)||!types.has(image.type)||image.size>6*1024*1024||image.size<200)return reply({error:"Unsupported image"},400);
 const buffer=await image.arrayBuffer();
 if(!validMagic(image.type,buffer))return reply({error:"Image type does not match contents"},400);
 const ext=types.get(image.type);
 const filename=crypto.randomUUID().replace(/-/g,'').slice(0,28)+'.'+ext;
 const key="site-blog/"+filename;
 await bucket.put(key,buffer,{httpMetadata:{contentType:image.type},customMetadata:{source:"xuyi-admin-blog"}});
 return reply({saved:true,path:"/media/blog/"+filename});
}