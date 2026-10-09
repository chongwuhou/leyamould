// XUYI R2 shared media manager (product / page / shared).
// Uses Demalong-style session; never accepts a CI build token.
(()=>{"use strict";
const token=()=>sessionStorage.getItem("xuyiAdminToken")||"";
const $=id=>document.getElementById(id);
const say=message=>{const node=$("media-status");if(node)node.textContent=message;};
const kind=()=>($("media-kind")?.value||"product");
async function list(cursor=""){
  const key=token();if(!key){say("请先登录后台");return;}
  const url="/api/admin/media?kind="+encodeURIComponent(kind())+(cursor?"&cursor="+encodeURIComponent(cursor):"");
  const res=await fetch(url,{headers:{authorization:"Bearer "+key},cache:"no-store"});
  const data=await res.json();if(!res.ok)throw Error(data.error||"Media API unavailable");
  const host=$("media-files");if(!cursor)host.replaceChildren();
  for(const row of data.items||[]){
    const card=document.createElement("div");card.className="media-library-item";
    const photo=document.createElement("img");photo.src=row.path;photo.alt="已上传图片";photo.loading="lazy";
    photo.style.cssText="width:135px;height:95px;object-fit:contain;background:#f6f6f6;border-radius:7px";
    const text=document.createElement("code");text.textContent=row.path;
    const copy=document.createElement("button");copy.type="button";copy.className="btn ghost";copy.textContent="复制路径";
    copy.addEventListener("click",async()=>{
      try{await navigator.clipboard.writeText(row.path);say("已复制："+row.path)}
      catch{say("请手动复制图片路径："+row.path)}
    });
    card.append(photo,text,copy);host.append(card);
  }
  const more=$("media-more");more.hidden=!data.cursor;more.dataset.cursor=data.cursor||"";
  say("已载入："+host.children.length+" 张，存储在旭一独立 R2。图片路径可以填入产品或页面 CMS。");
}
async function upload(){
  const file=$("media-upload")?.files?.[0];if(!file){say("请选择 JPEG、PNG 或 WebP 图片");return;}
  if(file.size>6*1024*1024){say("单张图片不能超过 6MB");return;}
  const key=token();if(!key){say("请先登录后台");return;}
  const button=$("media-upload-btn");button.disabled=true;say("正在上传到旭一 R2…");
  try{
    const body=new FormData();body.append("kind",kind());body.append("image",file);
    const res=await fetch("/api/admin/media",{method:"POST",headers:{authorization:"Bearer "+key},body});
    const data=await res.json();if(!res.ok)throw Error(data.error||"上传失败");
    $("media-upload").value="";await list();say("已上传："+data.path+"，可以复制路径填入产品或页面编辑器。");
  }catch(error){say("上传失败："+error.message)}finally{button.disabled=false;}
}
$("media-load")?.addEventListener("click",()=>list().catch(error=>say("读取失败："+error.message)));
$("media-kind")?.addEventListener("change",()=>list().catch(error=>say("读取失败："+error.message)));
$("media-more")?.addEventListener("click",()=>list($("media-more").dataset.cursor).catch(error=>say("读取失败："+error.message)));
$("media-upload-btn")?.addEventListener("click",upload);
document.querySelector('[data-admin-target="media"]')?.addEventListener("click",()=>list().catch(error=>say("读取失败："+error.message)));
})();