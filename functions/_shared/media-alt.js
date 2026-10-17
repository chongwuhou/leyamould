// XUYI reviewed image descriptions, not automatic keyword stuffing.
// The alt belongs to the image; product-card contextual captions may be more
// specific and must not be overwritten outside managed /media/ paths.
export const ALT_MAX=180;
export const ALT_LANG=/^[a-z]{2,3}(?:-[a-z0-9]{2,8})*$/;
export function normalizeAltMap(raw,{requireEnglish=true}={}){
 if(!raw||typeof raw!=="object"||Array.isArray(raw))throw Error("ALT descriptions must be an object");
 const result={};
 for(const [code,text] of Object.entries(raw)){
  if(!ALT_LANG.test(code))throw Error("Invalid ALT language code");
  const value=String(text??"").trim().replace(/\s+/g," ");
  if(!value)continue;
  if(value.length>ALT_MAX||/[<>\r\n\u0000-\u001f]/.test(value))
   throw Error("ALT must be a short plain-text description, max 180 characters");
  if(/https?:\/\/|\.(?:png|jpe?g|webp)\b/i.test(value))
   throw Error("ALT describes the visible image, not a file URL");
  result[code]=value;
 }
 if(requireEnglish&&!result.en)throw Error("English image ALT is required; describe the photo accurately");
 return result;
}
export async function ensureMediaAlt(db){
 await db.prepare(`CREATE TABLE IF NOT EXISTS xuyi_media_alt (
  path TEXT PRIMARY KEY,alt_json TEXT NOT NULL,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
 )`).run();
}
export async function upsertMediaAlt(db,path,alt){
 await ensureMediaAlt(db);
 await db.prepare(`INSERT INTO xuyi_media_alt(path,alt_json,updated_at)
 VALUES(?,?,CURRENT_TIMESTAMP)
 ON CONFLICT(path) DO UPDATE SET alt_json=excluded.alt_json,updated_at=CURRENT_TIMESTAMP`)
  .bind(path,JSON.stringify(normalizeAltMap(alt))).run();
}
export async function englishAltFor(db,path){
 try{
  const row=await db.prepare("SELECT alt_json FROM xuyi_media_alt WHERE path=?").bind(path).first();
  if(!row)return "";
  return normalizeAltMap(JSON.parse(row.alt_json),{requireEnglish:false}).en||"";
 }catch(error){
  // Old deployments may not have the metadata table; ordinary blog reading
  // must still work with the existing descriptive article-title ALT.
  if(/no such table/i.test(String(error?.message||error)))return "";
  throw error;
 }
}
