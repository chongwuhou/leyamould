// XUYI hybrid fallback, isolated to XUYI product routes.
// Pages static files always win. R2 is read only for approved removed detail files.
const reply=(value,status)=>Response.json(value,{status,headers:{"cache-control":"no-store"}});
export function modelKey(pathname){
  const parts=pathname.split("/").filter(Boolean);
  let slug="";
  if(parts.length===2&&parts[0]==="products")slug=parts[1];
  else if(parts.length===3&&/^[a-z]{2,3}(?:-[a-z0-9]{2,8})*$/i.test(parts[0])
       &&parts[1]==="products")slug=parts[2];
  if(!/^[a-z0-9][a-z0-9_-]{0,78}$/i.test(slug))return "";
  return "models/"+slug+".json";
}
export async function serveModelOverflow(context){
  const method=context.request.method.toUpperCase();
  if(method!=="GET"&&method!=="HEAD")return context.next();
  const url=new URL(context.request.url);
  const key=modelKey(url.pathname);
  if(!key)return context.next();
  const staticResponse=await context.next();
  if(staticResponse.status!==404)return staticResponse;
  if(!context.env.LEYA_MODEL_PAGES)return staticResponse;
  let object;
  try{object=await context.env.LEYA_MODEL_PAGES.get(key)}
  catch{return reply({error:"Overflow store unavailable"},503)}
  if(!object)return staticResponse;
  let bundle;
  try{bundle=JSON.parse(await object.text())}
  catch{return reply({error:"Invalid XUYI overflow bundle"},502)}
  if(bundle?.site!=="leyamould"||bundle?.schemaVersion!==1)return reply({error:"Invalid overflow identity"},502);
  const canonical=url.pathname.endsWith("/")?url.pathname:url.pathname+"/";
  // Exact URL must exist in the approved immutable R2 manifest. Accepting a
  // syntactically valid new locale prefix does not publish phantom translations.
  const document=bundle.routes?.[canonical];
  if(!document)return staticResponse;
  if(url.pathname!==canonical){const target=new URL(url);target.pathname=canonical;return Response.redirect(target,301)}
  const headers=new Headers({"content-type":"text/html; charset=utf-8",
    "cache-control":"public, max-age=300, s-maxage=900","x-xuyi-page-storage":"r2-overflow",
    "x-content-type-options":"nosniff"});
  if(object.httpEtag)headers.set("etag",object.httpEtag);
  return new Response(method==="HEAD"?null:document,{status:200,headers});
}
export async function overflowHealth(env){
  if(!env.LEYA_MODEL_PAGES)return {ready:false,binding:false,error:"LEYA_MODEL_PAGES binding missing"};
  let raw;
  try{raw=await env.LEYA_MODEL_PAGES.get("__system/manifest.json")}
  catch{return {ready:false,binding:true,error:"R2 manifest unavailable"}}
  if(!raw)return {ready:false,binding:true,manifest:false,error:"R2 overflow manifest missing"};
  try{
    const manifest=JSON.parse(await raw.text());
    if(manifest.site!=="leyamould"||manifest.bucket!=="leyamould-model-pages")throw Error("Wrong XUYI bucket manifest");
    return {ready:true,binding:true,manifest:true,mode:manifest.mode,
      modelCount:Number(manifest.modelCount||0),localizedPageCount:Number(manifest.localizedPageCount||0),
      objectCount:manifest.objects?.length||0};
  }catch{return {ready:false,binding:true,manifest:true,error:"Invalid overflow manifest"}}
}
