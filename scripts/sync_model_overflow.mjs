import {execFileSync} from "node:child_process";
import {readFileSync,existsSync,mkdirSync,rmSync} from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const output=path.join(root,"_local_ops","model-overflow");
const manifest=JSON.parse(readFileSync(path.join(output,"manifest.json"),"utf8"));
const bucket="xuyi-drinkware-model-pages";
if(manifest.site!=="xuyi-drinkware-site"||manifest.bucket!==bucket)throw Error("XUYI overflow manifest identity mismatch");
if(manifest.mode==="static"){console.log("XUYI_R2_SYNC_SKIPPED_STATIC no overflow model pages");process.exit(0)}
if(manifest.mode!=="hybrid"||!manifest.objects?.length)throw Error("Invalid XUYI hybrid manifest");
function wrangler(args,{optional=false}={}){
 try{return execFileSync("npx",["--yes","wrangler@4.148.0",...args],{
  cwd:root,encoding:"utf8",maxBuffer:64*1024*1024,
  stdio:["ignore","pipe","pipe"],env:process.env
 })}
 catch(err){if(optional)return "";
  throw Error("R2 sync failed (check XUYI bucket permission): "+args[0]+" "+args[1]+": "+
   String(err.stderr||err.message).slice(-550))}
}
const remoteFile=path.join(output,"remote-manifest.json");
wrangler(["r2","object","get",bucket+"/__system/manifest.json","--file",remoteFile,"--remote"],{optional:true});
let remote={objects:[]};if(existsSync(remoteFile))try{remote=JSON.parse(readFileSync(remoteFile,"utf8"))}catch{}
if(remote.site&&remote.site!=="xuyi-drinkware-site")throw Error("Wrong existing R2 manifest");
const was=new Map((remote.objects||[]).map(x=>[x.key,x.sha256]));
const incoming=new Set();
let uploaded=0;
for(const obj of manifest.objects){
 if(!/^models\/[a-z0-9_-]+\.json$/.test(obj.key))throw Error("Invalid overflow object key");
 incoming.add(obj.key);
 if(was.get(obj.key)===obj.sha256)continue;
 const file=path.join(output,...obj.key.split("/"));
 if(!existsSync(file))throw Error("Missing built overflow bundle "+obj.key);
 wrangler(["r2","object","put",bucket+"/"+obj.key,"--file",file,"--content-type","application/json; charset=utf-8","--remote"]);
 uploaded++;
}
// Write manifest LAST. Prior manifests remain readable if a put fails.
wrangler(["r2","object","put",bucket+"/__system/manifest.json","--file",path.join(output,"manifest.json"),
 "--content-type","application/json; charset=utf-8","--remote"]);
// Do not remove stale bundles automatically; they are small and previous
// deployments could temporarily still depend on them (safe rollback).
console.log("XUYI_R2_HYBRID_SYNC_PASSED",{models:manifest.modelCount,uploaded,unchanged:manifest.objects.length-uploaded});