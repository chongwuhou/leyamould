// Single-item XUYI bottle editor (not a bulk importer).
import {MANAGED_MODELS} from "./xuyi-routes.js";
import {imageKey} from "./r2-usage.js";
export const CATEGORY_OPTIONS=[
 "Plastic Sports Water Bottles","Large Capacity Water Jugs",
 "Kids Plastic Water Bottles","Plastic Shaker Bottles"
];
export const NEW_MODEL=/^[a-z0-9][a-z0-9-]{1,63}$/;
export function normalizeNewProduct(model,content,status="draft"){
 if(!NEW_MODEL.test(model)||model.includes("..")||MANAGED_MODELS.has(model))
  throw Error("New product model/slug is invalid or already exists");
 if(!content||typeof content!=="object"||Array.isArray(content))
  throw Error("Invalid product");
 const clean=(key,max=3000)=>{
  if(content[key]!==undefined&&typeof content[key]!=="string")throw Error("Invalid "+key);
  return String(content[key]||"").trim().slice(0,max+1);
 };
 const data={newProduct:true,category:clean("category",90),name:clean("name",180),
  material:clean("material",200),capacity:clean("capacity",120),
  description:clean("description",1300),image:clean("image",300),
  colors:clean("colors",300),packing:clean("packing",300),
  seoTitle:clean("seoTitle",90),seoDescription:clean("seoDescription",240)};
 if(!CATEGORY_OPTIONS.includes(data.category))throw Error("Choose a valid XUYI bottle category");
 for(const [key,max] of [["name",180],["material",200],["capacity",120],["description",1300],["seoTitle",90],["seoDescription",240]]){
  if(data[key].length>max)throw Error("Field too long: "+key);
 }
 if(data.image){
  const match=/^\/media\/([a-z]+)\/([a-zA-Z0-9._-]{3,140}\.(?:webp|jpg|png))$/.exec(data.image);
  if(!match||!imageKey(match[1],match[2]))throw Error("Choose an image from the XUYI R2 media library");
 }
 if(status==="published"){
  for(const key of ["name","material","capacity","description","image"])
   if(data[key].length<2)throw Error("To publish, complete "+key+" with verified product details");
 }
 return data;
}
