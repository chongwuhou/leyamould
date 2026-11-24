// Replace a LEYA MOULD R2 photo in place, with side-by-side review and undo history.
(()=>{"use strict";
 const token=()=>sessionStorage.getItem("xuyiAdminToken")||"";
 const text=(node,str)=>{node.textContent=str};
 const api=async(path,options={})=>{
  const res=await fetch(path,{...options,cache:"no-store",headers:{authorization:"Bearer "+token(),...(options.headers||{})}});
  const data=await res.json().catch(()=>({}));
  if(!res.ok)throw Error(data.error||"HTTP "+res.status);
  return data;
 };
 const root=document.createElement("dialog");root.id="xuyi-r2-replace-dialog";
 root.style.cssText="max-width:min(94vw,900px);width:900px;border:1px solid #ddd;border-radius:14px;padding:22px;box-shadow:0 18px 90px #1115;max-height:90vh;overflow:auto";
 root.innerHTML=`<div style="display:flex;align-items:center;justify-content:space-between;gap:12px">
  <h2 style="margin:0">更换 R2 图片（原路径不变）</h2>
  <button type="button" class="btn ghost" data-close>关闭</button></div>
  <p data-path style="overflow-wrap:anywhere;font-size:12px"></p>
  <p style="font-size:13px">请对比<strong>杯型、瓶盖、颜色、Logo、背景和拍摄角度</strong>。具体型号必须核实完全同款；新图片将自动转换成原文件格式，并保留上一版本。</p>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:14px">
   <div><b>当前网站图片</b><img data-old alt="当前图片" style="display:block;margin-top:8px;width:100%;height:260px;object-fit:contain;background:#f6f6f6;border-radius:8px"></div>
   <div><b>准备替换的新图片</b><img data-new alt="新图片预览" style="display:block;margin-top:8px;width:100%;height:260px;object-fit:contain;background:#f6f6f6;border-radius:8px"></div>
  </div>
  <p data-spec style="font-size:13px"></p>
  <label style="display:block">选择高清图片 <input data-file type="file" accept="image/png,image/jpeg,image/webp"></label>
  <label style="display:block;margin-top:12px"><input type="checkbox" data-confirm> 我已核对新旧图片属于同一个产品型号或同一栏目，确认有使用权</label>
  <div style="display:flex;flex-wrap:wrap;gap:12px;margin-top:16px">
   <button type="button" class="btn primary" data-save disabled>确认替换并备份旧版</button>
   <button type="button" class="btn ghost" data-history>查看历史版本 / 恢复</button>
  </div>
  <p data-status role="status" style="font-size:13px;white-space:pre-wrap"></p>
  <div data-versions style="font-size:13px"></div>`;
 document.body.append(root);
 const $=a=>root.querySelector("[data-"+a+"]");
 const status=t=>text($("status"),t);
 const max=6*1024*1024;
 let current=null,url="",oldDimensions=null,preview=null,selection=null;
 const endpoint=()=>"/api/admin/media-replace?kind="+encodeURIComponent(current.kind)+"&filename="+encodeURIComponent(current.filename);
 const mimeOf=filename=>filename.endsWith(".webp")?"image/webp":filename.endsWith(".png")?"image/png":"image/jpeg";
 const bytes=b=>(b/1024).toFixed(1)+" KB";
 const revoke=()=>{if(preview){URL.revokeObjectURL(preview);preview=null}};
 const enable=()=>{$("save").disabled=!selection||!$("confirm").checked};
 const loadHistory=async()=>{
  const data=await api(endpoint());
  if(!current||data.path!==current.path)return;
  current.etag=data.etag;
  const host=$("versions");host.replaceChildren();
  const heading=document.createElement("b");heading.textContent="旧版备份：";host.append(heading);
  if(!data.versions.length){
   const label=document.createElement("span");label.textContent=" 暂无（首次替换会生成）";host.append(label);return;
  }
  for(const entry of data.versions.slice(0,6)){
   const line=document.createElement("div");line.style.cssText="display:flex;align-items:center;flex-wrap:wrap;gap:12px;margin:8px 0";
   const title=document.createElement("span");title.textContent=(entry.uploadedAt||entry.version)+" · "+bytes(entry.bytes);
   const restore=document.createElement("button");restore.type="button";restore.className="btn ghost";
   restore.textContent="恢复此版本";
   restore.addEventListener("click",async()=>{
    if(!confirm("恢复这一版图片？系统会先备份目前的图片，图片 URL 保持不变。\n"+current.path))return;
    restore.disabled=true;status("正在恢复并保存当前版本……");
    try{
     const data=await api(endpoint(),{method:"POST",headers:{"content-type":"application/json"},
      body:JSON.stringify({action:"restore",version:entry.version,etag:current.etag,confirm:"restore"})});
     status("已恢复旧图，恢复前的图片也已备份。部分访客可能暂时看到缓存（最长约 1 小时）。");
     $("old").src=current.path+"?r2preview="+Date.now();
     await loadHistory();
     document.getElementById("media-load")?.click();
    }catch(error){status("恢复未完成："+error.message)}
    finally{restore.disabled=false}
   });
   line.append(title,restore);host.append(line);
  }
 };
 const prepare=async(file)=>{
  const bmp=await createImageBitmap(file);
  oldDimensions??=null;
  const w=bmp.width,h=bmp.height;
  if(w<1||h<1||w*h>60000000){bmp.close();throw Error("图片尺寸不可用或过大")}
  const required=mimeOf(current.filename);
  let replacement=file;
  if(file.type!==required){
   const canvas=document.createElement("canvas");canvas.width=w;canvas.height=h;
   const ctx=canvas.getContext("2d");
   if(!ctx){bmp.close();throw Error("浏览器无法转换格式")}
   if(required==="image/jpeg"){ctx.fillStyle="#fff";ctx.fillRect(0,0,w,h)}
   ctx.drawImage(bmp,0,0);
   const blob=await new Promise(resolve=>canvas.toBlob(resolve,required,0.91));
   canvas.width=0;canvas.height=0;
   if(!blob||blob.type!==required){bmp.close();throw Error("浏览器不支持转换到 "+required)}
   replacement=new File([blob],file.name.replace(/\.[^.]+$/,"")+"."+current.filename.split(".").pop(),{type:required});
  }
  bmp.close();
  if(replacement.size>max)throw Error("转换后的图片超过 6MB，请先压缩原图");
  if(oldDimensions&&(w<oldDimensions.width||h<oldDimensions.height))
   throw Error("新图 "+w+"×"+h+" 小于旧图 "+oldDimensions.width+"×"+oldDimensions.height+"，不允许降清晰度");
  return {file:replacement,width:w,height:h};
 };
 document.addEventListener("click",async(event)=>{
  const clicked=event.target.closest(".media-replace-action");
  if(!clicked)return;
  if(!token()){document.getElementById("media-status").textContent="请先登录后台";return}
  current={kind:clicked.dataset.kind,filename:clicked.dataset.filename,path:clicked.dataset.path,etag:clicked.dataset.etag};
  $("path").textContent=current.path+"（同路径替换，链接不变）";
  $("file").value="";$("confirm").checked=false;$("new").removeAttribute("src");
  $("versions").replaceChildren();$("save").disabled=true;selection=null;oldDimensions=null;revoke();
  $("old").src=current.path+"?r2preview="+Date.now();
  $("old").onload=()=>{
   oldDimensions={width:$("old").naturalWidth,height:$("old").naturalHeight};
   $("spec").textContent="原图："+oldDimensions.width+"×"+oldDimensions.height+"；请选择不低于原图分辨率的新图";
  };
  status("等待选择新图片。旧 R2 对象将在覆盖前自动备份。");
  root.showModal();
  try{await loadHistory()}catch(err){status("暂时无法读取备份历史："+err.message)}
 });
 $("file").addEventListener("change",async()=>{
  revoke();$("new").removeAttribute("src");selection=null;enable();
  const file=$("file").files?.[0];if(!file)return;
  try{
   selection=await prepare(file);
   preview=URL.createObjectURL(selection.file);$("new").src=preview;
   $("spec").textContent="新图："+selection.width+"×"+selection.height+"，"+bytes(selection.file.size)+
    "（"+selection.file.type+"）；原图："+(oldDimensions?.width||"?")+"×"+(oldDimensions?.height||"?");
   status("已准备好新图，请逐项核对外观与型号后确认。");
  }catch(err){status("无法使用这张图："+err.message)}
  enable();
 });
 $("confirm").addEventListener("change",enable);
 $("save").addEventListener("click",async()=>{
  if(!current||!selection||!$("confirm").checked)return;
  if(!confirm("确定覆盖这张 R2 图片吗？全部引用此路径的页面可能同时变化。\n"+current.path))return;
  $("save").disabled=true;$("file").disabled=true;
  status("正在备份旧图片、校验新图片并写入 R2……");
  try{
   const form=new FormData();
   form.append("image",selection.file);
   form.append("etag",current.etag);
   form.append("confirm","same-subject");
   const data=await api(endpoint(),{method:"PUT",body:form});
   status("替换完成。旧图备份版本："+data.backupVersion+
    "\n已有页面引用保持有效；缓存可能导致部分访客在约一小时内暂时看到旧图。");
   $("old").src=current.path+"?r2preview="+Date.now();
   $("confirm").checked=false;selection=null;enable();
   await loadHistory();
   document.getElementById("media-load")?.click();
  }catch(err){status("替换未完成："+err.message)}
  finally{$("file").disabled=false}
 });
 $("history").addEventListener("click",async()=>{try{await loadHistory()}catch(err){status("读取失败："+err.message)}});
 $("close").addEventListener("click",()=>root.close());
 root.addEventListener("close",()=>{revoke();$("old").removeAttribute("src");$("new").removeAttribute("src");selection=null;current=null});
})();
