import {loadSiteSetting} from "./site-settings.js";

export const PRODUCT_ADMIN_CONFIG_KEY = "product_admin_config";
const DEFAULT_CATEGORIES = [
 "Plastic Sports Water Bottles","Large Capacity Water Jugs",
 "Kids Plastic Water Bottles","Plastic Shaker Bottles",
 "Spray Water Bottles","Two-Way Drinking Cups","Titanium Vacuum Cups"
];
const LEGACY_FIELDS=[
 ["name","产品名称",0],["material","材质/部件材料",0],["capacity","容量",0],
 ["colors","颜色选项",0],["packing","单品包装信息",0],["dimensions","产品尺寸",0],
 ["carton_quantity","外箱装量",0],["carton_size","外箱尺寸",0],["image","产品主图路径",0],
 ["description","产品描述",4],["seoTitle","SEO Title",0],["seoDescription","Meta Description",3]
];
const NEW_PRODUCT_FIELDS=[
 ["factoryModel","工厂画册印刷型号",0],["name","产品名称",0],["capacity","容量",0],
 ["material","材质",0],["dimensions","产品尺寸",0],["unit_weight","单个产品重量",0],
 ["temperature_range","温度范围",0],["colors","颜色选项",0],["packing","单品包装信息",0],
 ["retail_box_size","彩盒尺寸",0],["carton_quantity","外箱装量",0],["carton_size","外箱尺寸",0],
 ["carton_gross_weight","外箱毛重",0],["catalogOunceLabel","画册印刷的 oz 标识",0],
 ["sourceDocument","来源文件名",0],["sourcePage","来源页码",0],
 ["sourceNotes","画册备注及需要确认的规格",4],["qcStatus","资料核验状态",0],
 ["imageReviewStatus","图片审核状态",0],["image","R2 产品主图路径",0],
 ["description","产品说明",5],["seoTitle","SEO Title",0],["seoDescription","Meta Description",3]
];
function fieldList(rows){return rows.map(([key,label,rows])=>({key,label,rows}));}
export function defaultProductAdminConfig(){
 return {schemaVersion:1,categories:[...DEFAULT_CATEGORIES],
  fields:{legacy:fieldList(LEGACY_FIELDS),newProduct:fieldList(NEW_PRODUCT_FIELDS)}};
}
function normalizeCategories(value){
 const source=Array.isArray(value)&&value.length?value:DEFAULT_CATEGORIES,seen=new Set();
 return source.slice(0,100).map(value=>{
  const item=String(value??"").trim();
  if(!item||item.length>120||seen.has(item))throw Error("Invalid product category configuration");
  seen.add(item);return item;
 });
}
function normalizeFields(value,fallback){
 const source=Array.isArray(value)&&value.length?value:fallback,seen=new Set();
 return source.slice(0,100).map(item=>{
  const key=String(item?.key??"").trim(),label=String(item?.label??"").trim(),rows=Number(item?.rows||0);
  if(!/^[A-Za-z][A-Za-z0-9_]{0,63}$/.test(key)||!label||label.length>160||
     !Number.isInteger(rows)||rows<0||rows>30||seen.has(key))throw Error("Invalid product field configuration");
  seen.add(key);return {key,label,rows};
 });
}
export function normalizeProductAdminConfig(input){
 const fallback=defaultProductAdminConfig(),raw=input&&typeof input==="object"&&!Array.isArray(input)?input:{};
 return {schemaVersion:1,categories:normalizeCategories(raw.categories),fields:{
  legacy:normalizeFields(raw.fields?.legacy,fallback.fields.legacy),
  newProduct:normalizeFields(raw.fields?.newProduct,fallback.fields.newProduct)
 }};
}
export async function loadProductAdminConfig(db){
 const saved=await loadSiteSetting(db,PRODUCT_ADMIN_CONFIG_KEY,defaultProductAdminConfig());
 return {config:normalizeProductAdminConfig(saved.value),updatedAt:saved.updatedAt||""};
}
