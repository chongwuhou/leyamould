// XUYI 3-slot homepage Banner: explicit images, links and reviewed localized copy.
export const LANGS=["en","es","pt","ru","tr"];
const STRING_FIELDS=["title","highlight","description","alt","cta"];
const limits={title:100,highlight:110,description:500,alt:220,cta:95};
function str(value,key){
 if(typeof value!=="string"||!value.trim()||value.length>limits[key]||/[<>\u0000-\u001f]/.test(value))
  throw Error("Invalid banner "+key);
 return value.trim();
}
export function safeBannerPath(value){
 if(typeof value!=="string"||!value.startsWith("/")||value.startsWith("//")||/[<>"'\s\\]/.test(value))
  return false;
 return /^\/(?:assets\/[a-zA-Z0-9/_-]+\.(?:webp|jpg|jpeg|png)|media\/(?:product|page|shared|ppt|excel|group|gallery|capability|blog)\/[a-zA-Z0-9._-]+\.(?:webp|jpg|jpeg|png))$/.test(value);
}
export function safeBannerLink(value){
 if(typeof value!=="string"||/[<>"'\s\\]/.test(value))return false;
 if(value.startsWith("/"))return !value.startsWith("//")&&/^\/[a-zA-Z0-9_/?#=%&.+~-]*$/.test(value);
 try{const u=new URL(value);return u.protocol==="https:"&&!!u.hostname&&!u.username&&!u.password}
 catch{return false}
}
export function normalizeBanners(input){
 if(!input||typeof input!=="object"||!Array.isArray(input.slides)||input.slides.length!==3)
  throw Error("Homepage must contain exactly 3 banner slides");
 return {schemaVersion:1,slides:input.slides.map((row,i)=>{
  if(!row||typeof row!=="object"||!safeBannerPath(row.img)||!safeBannerLink(row.link))
   throw Error("Invalid banner image or link on slide "+(i+1));
  const item={img:row.img,link:row.link};
  for(const k of STRING_FIELDS)item[k]=str(row[k],k);
  item.translations={};
  for(const locale of LANGS.slice(1)){
   const value=row.translations?.[locale];
   if(!value||typeof value!=="object")throw Error("Missing reviewed "+locale+" banner text");
   item.translations[locale]={};
   for(const k of STRING_FIELDS)item.translations[locale][k]=str(value[k],k);
  }
  return item;
 })};
}