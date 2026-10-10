// XUYI R2 files: show deployed references and check live D1 before safe deletion.
(()=>{"use strict";
const token=()=>sessionStorage.getItem("xuyiAdminToken")||"";
const $=id=>document.getElementById(id);
const say=message=>{const node=$("media-status");if(node)node.textContent=message};
const kind=()=>$("media-kind")?.value||"product";
const editable=()=>["product","page","shared"].includes(kind());
async function api(path,options={}){
 const response=await fetch(path,{headers:{authorization:"Bearer "+token(),...(options.headers||{})},
  cache:"no-store",...options});
 const data=await response.json().catch(()=>({}));
 if(!response.ok)throw Error(data.error||"R2 接口不可用");
 return data;
}
async function list(cursor=""){
 if(!token()){say("请先登录后台");return}
 const selectedKind=kind();
 const url="/api/admin/media?kind="+encodeURIComponent(selectedKind)+(cursor?"&cursor="+encodeURIComponent(cursor):"");
 const data=await api(url);
 const host=$("media-files");if(!cursor)host.replaceChildren();
 for(const row of data.items||[]){
  const card=document.createElement("div");card.className="media-library-item";
  card.style.cssText="display:flex;flex-direction:column;gap:8px;width:225px;padding:10px;border:1px solid #dedede;border-radius:8px;overflow-wrap:anywhere";
  const photo=document.createElement("img");
  photo.src=row.path;photo.alt="旭一 R2 预览";photo.loading="lazy";
  photo.style.cssText="width:100%;height:140px;object-fit:contain;background:#f6f6f6;border-radius:7px";
  const pathLabel=document.createElement("code");pathLabel.textContent=row.path;
  pathLabel.style.cssText="font-size:11px;overflow-wrap:anywhere";
  const bytes=document.createElement("small");bytes.textContent=(Number(row.size||0)/1024).toFixed(1)+" KB";
  const state=document.createElement("p");state.style.cssText="margin:0;font-size:12px";
  const refs=document.createElement("div");refs.style.cssText="font-size:11px;white-space:pre-wrap;overflow-wrap:anywhere";
  const checked={safe:false};
  const remove=document.createElement("button");remove.type="button";remove.className="btn ghost";
  remove.textContent=row.canDelete?"删除（需先检查）":"原始图库：禁止直接删除";remove.disabled=true;
  function showState(status,items=[],count=0){
   if(status==="used"){
    state.textContent="已被引用 · "+count+" 处";state.style.color="#b04123";
    refs.textContent=(items||[]).slice(0,8).join("\n");
   }else if(status==="unused"){
    state.textContent="已全面检查：未发现引用";state.style.color="#20784b";refs.textContent="";
   }else {
    state.textContent=status==="needs-check"?"未查到静态引用，需检查 D1":"引用未知，需检查";
    state.style.color="#805b1c";refs.textContent="";
   }
   checked.safe=status==="unused"&&!!row.canDelete;
   remove.disabled=!checked.safe;
   if(checked.safe)remove.textContent="删除已确认未引用的文件";
  }
  showState(row.usageStatus,row.references,row.referenceCount);
  const copy=document.createElement("button");copy.type="button";copy.className="btn ghost";
  copy.textContent="复制地址";
  copy.addEventListener("click",async()=>{
   try{await navigator.clipboard.writeText(row.path);say("已复制："+row.path)}
   catch{say("请手动复制："+row.path)}
  });
  const verify=document.createElement("button");verify.type="button";verify.className="btn ghost";
  verify.textContent="检查引用（含 D1）";
  verify.addEventListener("click",async()=>{
   verify.disabled=true;
   try{
    const check=await api("/api/admin/media?kind="+encodeURIComponent(selectedKind)+"&filename="+encodeURIComponent(row.path.split("/").pop()));
    showState(check.usageStatus,check.references,check.referenceCount);
    if(check.truncated)refs.textContent+="\n（仅显示前 20 项）";
   }catch(err){showState("unknown");say("引用检查失败，已禁止删除："+err.message)}
   finally{verify.disabled=false}
  });
  remove.addEventListener("click",async()=>{
   if(!checked.safe||!confirm("已确认图片未被当前正式版及 D1 引用。仍要永久删除这个 R2 文件吗？\n"+row.path))return;
   remove.disabled=true;
   try{
    await api("/api/admin/media?kind="+encodeURIComponent(selectedKind)+"&filename="+encodeURIComponent(row.path.split("/").pop()),{method:"DELETE"});
    await list();say("已从旭一通用媒体桶删除："+row.path);
   }catch(err){showState("unknown");say("删除被阻止："+err.message)}
  });
  card.append(photo,pathLabel,bytes,state,refs,copy,verify,remove);host.append(card);
 }
 const more=$("media-more");more.hidden=!data.cursor;more.dataset.cursor=data.cursor||"";
 const upload=$("media-upload"),button=$("media-upload-btn");
 if(upload)upload.disabled=!editable();
 if(button)button.disabled=!editable();
 const mb=(Number(data.usageBytes||0)/1048576).toFixed(2);
 say("已显示 "+host.children.length+" 个文件；后台上传媒体占用 "+mb+" MB / 1024 MB。"+
    (data.readOnly?" 当前类别只读，源图库受保护。":" 管理素材只有在完整引用检查通过后才能删除。")+
    (!data.referenceIndexReady?" 注意：静态引用索引不可用，删除将自动拒绝。":""));
}
async function upload(){
 if(!editable()){say("原始图库仅供查看，不接受在此上传或删除");return}
 const file=$("media-upload")?.files?.[0];if(!file){say("请选择 JPEG、PNG 或 WebP 图片");return}
 if(file.size>6*1024*1024){say("单张图片不能超过 6 MB");return}
 const key=token();if(!key){say("请先登录后台");return}
 const button=$("media-upload-btn");button.disabled=true;say("正在上传旭一 R2…");
 try{
  const body=new FormData();body.append("kind",kind());body.append("image",file);
  const data=await api("/api/admin/media",{method:"POST",body});
  $("media-upload").value="";await list();
  say("已上传："+data.path+"，请复制地址并在内容 CMS 中引用。");
 }catch(err){say("上传失败："+err.message)}
 finally{button.disabled=!editable()}
}
$("media-load")?.addEventListener("click",()=>list().catch(err=>say("读取失败："+err.message)));
$("media-kind")?.addEventListener("change",()=>list().catch(err=>say("读取失败："+err.message)));
$("media-more")?.addEventListener("click",()=>list($("media-more").dataset.cursor).catch(err=>say("读取失败："+err.message)));
$("media-upload-btn")?.addEventListener("click",upload);
document.querySelector('[data-admin-target="media"]')?.addEventListener("click",()=>list().catch(err=>say("读取失败："+err.message)));
})();