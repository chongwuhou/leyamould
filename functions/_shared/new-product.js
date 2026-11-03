// XUYI product editor and create-only factory-catalog importer.
import {MANAGED_MODELS} from "./xuyi-routes.js";
import {imageKey} from "./r2-usage.js";
export const CATEGORY_OPTIONS=[
 "Plastic Sports Water Bottles","Large Capacity Water Jugs",
 "Kids Plastic Water Bottles","Plastic Shaker Bottles",
 "Spray Water Bottles","Two-Way Drinking Cups","Titanium Vacuum Cups"
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
 const data={
  newProduct:true,factoryModel:clean("factoryModel",80),
  category:clean("category",90),name:clean("name",180),
  material:clean("material",200),capacity:clean("capacity",120),
  description:clean("description",1300),image:clean("image",300),
  colors:clean("colors",300),packing:clean("packing",300),
  dimensions:clean("dimensions",160),unit_weight:clean("unit_weight",120),
  temperature_range:clean("temperature_range",120),retail_box_size:clean("retail_box_size",120),
  carton_quantity:clean("carton_quantity",120),carton_size:clean("carton_size",120),
  carton_gross_weight:clean("carton_gross_weight",120),catalogOunceLabel:clean("catalogOunceLabel",80),
  sourceDocument:clean("sourceDocument",180),sourcePage:clean("sourcePage",20),
  sourceSha256:clean("sourceSha256",64),sourceImageSha256:clean("sourceImageSha256",64),
  sourceNotes:clean("sourceNotes",800),qcStatus:clean("qcStatus",40),
  imageReviewStatus:clean("imageReviewStatus",40),
  seoTitle:clean("seoTitle",90),seoDescription:clean("seoDescription",240)
 };
 if(!CATEGORY_OPTIONS.includes(data.category))throw Error("Choose a valid XUYI drinkware category");
 for(const [key,max] of [
  ["factoryModel",80],["name",180],["material",200],["capacity",120],["description",1300],
  ["colors",300],["packing",300],["dimensions",160],["unit_weight",120],["temperature_range",120],
  ["retail_box_size",120],["carton_quantity",120],["carton_size",120],["carton_gross_weight",120],
  ["catalogOunceLabel",80],["sourceDocument",180],["sourcePage",20],["sourceSha256",64],["sourceImageSha256",64],["sourceNotes",800],
  ["qcStatus",40],["imageReviewStatus",40],["seoTitle",90],["seoDescription",240]
 ]){
  if(data[key].length>max)throw Error("Field too long: "+key);
 }
  if(data.sourcePage&&!/^\d{1,3}$/.test(data.sourcePage))throw Error("Invalid factory catalog page number");
  for(const key of ["sourceSha256","sourceImageSha256"])if(data[key]&&!/^[0-9a-f]{64}$/i.test(data[key]))throw Error("Invalid "+key);
  if(data.sourceDocument&&(!data.sourcePage||!data.sourceSha256))
   throw Error("Factory catalog products require source page and PDF SHA-256");
  if(data.image){
   const match=/^\/media\/([a-z]+)\/([a-zA-Z0-9._-]{3,140}\.(?:webp|jpg|png))$/.exec(data.image);
   if(!match||!imageKey(match[1],match[2]))throw Error("Choose an image from the XUYI R2 media library");
  }
  if(status==="published"){
   if(/pending/i.test(data.imageReviewStatus))throw Error("Review the replacement product image before publishing");
   for(const key of ["name","material","capacity","description","image"])
    if(data[key].length<2)throw Error("To publish, complete "+key+" with source-backed product details");
  }
 return data;
}