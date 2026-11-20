// Portable browser-logic regression. A temporary D1/API outage must not hide
// languages that this specific published HTML already declares via hreflang.
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import vm from "node:vm";

const script=readFileSync(new URL("../assets/site-settings.js",import.meta.url),"utf8");
const STATIC=[
  ["en","English"],["es","Español"],["pt","Português"],
  ["ru","Русский"],["tr","Türkçe"]
];
function fakeSelect(){
  const select={
    options:STATIC.map(([value,textContent])=>({value,textContent})),
    disabled:false,value:"",onchange:null,
    append(option){this.options.push(option);}
  };
  Object.defineProperty(select,"innerHTML",{
    set(markup){
      this.options=[...markup.matchAll(/<option value="([^"]+)">([^<]+)<\/option>/g)]
        .map(m=>({value:m[1],textContent:m[2]}));
    }
  });
  return select;
}
async function runCase({apiError=false,apiLanguages=[]}){
  const select=fakeSelect(),redirects=[];
  const prefix="https://leyamould.com";
  const alternate=STATIC.map(([hreflang])=>({
    hreflang,href:prefix+(hreflang==="en"?"/":"/"+hreflang+"/")
  }));
  const document={
    documentElement:{lang:"es"},
    querySelector:x=>x==="[data-language-switch]"?select:null,
    querySelectorAll:x=>x.includes('link[rel="alternate"]')?alternate:[],
    createElement:()=>({value:"",textContent:""})
  };
  const location={href:prefix+"/es/",origin:prefix,pathname:"/es/",search:"",hash:"",
    assign:path=>redirects.push(path)};
  const fetch=async()=>{
    if(apiError)throw Error("D1 is temporarily unavailable");
    return {ok:true,json:async()=>({languages:{items:apiLanguages},contacts:[]})};
  };
  vm.runInNewContext(script,{document,location,fetch,URL,encodeURIComponent});
  await new Promise(resolve=>setImmediate(resolve));
  return {select,redirects};
}
let state=await runCase({apiError:true});
assert.deepEqual(state.select.options.map(o=>o.value),STATIC.map(x=>x[0]));
assert.equal(state.select.value,"es");
assert.equal(state.select.disabled,false);
state.select.value="tr";state.select.onchange();
assert.deepEqual(state.redirects,["/tr/"]);

state=await runCase({apiLanguages:[
  {code:"en",nativeName:"English"},{code:"es",nativeName:"Español"},
  {code:"fr",nativeName:"Français"}]});
assert.deepEqual(state.select.options.map(o=>o.value),["en","es"],
 "An API-configured sixth locale must not appear unless this page has a real href alternate");
assert.equal(state.select.disabled,false);
state.select.value="en";state.select.onchange();
assert.deepEqual(state.redirects,["/"]);

console.log("XUYI_LANGUAGE_SWITCH_API_FAILOVER_PASSED hreflang-only fallback, API recovery and unpublished locale safety");
