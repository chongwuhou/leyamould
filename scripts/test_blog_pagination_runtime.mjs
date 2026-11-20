import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

// Dependency-free browser simulation: checks history, locality, growth,
// idempotence and progressive enhancement on CMS cards without DOM libraries.
const source=fs.readFileSync(new URL('../assets/blog-pagination.js',import.meta.url),'utf8');
class Node {
  constructor(tag){this.tag=tag;this.children=[];this.attrs={};this.handlers={};this.hidden=false;this.parentElement=null;this.textContent='';this.className='';this.href='';this.loading='';}
  appendChild(child){child.parentElement=this;this.children.push(child);return child;}
  replaceChildren(...nodes){this.children=[];for(const node of nodes)this.appendChild(node);}
  setAttribute(k,v){this.attrs[k]=v;}
  matches(q){return q==='article.news-card'&&this.tag==='article';}
  querySelector(q){return q==='img'?this.children.find(c=>c.tag==='img')||null:null;}
  addEventListener(name,fn){this.handlers[name]=fn;}
  scrollIntoView(){this.scrolled=true;}
}
function boot(lang,length,path='/blog/',query=''){
  const grid=new Node('div'),shell=new Node('div');shell.appendChild(grid);
  for(let i=0;i<length;i++){let article=grid.appendChild(new Node('article'));article.appendChild(new Node('img'));}
  let href='https://leyamould.com'+path+query;
  const document={documentElement:{lang},querySelector:sel=>sel==='.blog-listing__grid'?grid:null,createElement:tag=>new Node(tag)};
  const window={location:{get href(){return href;}},handlers:{},
    history:{pushState(_state,_title,url){href=new URL(url,'https://leyamould.com').href;}},
    addEventListener(event,fn){this.handlers[event]=fn;}};
  vm.runInNewContext(source,{document,window,URL});
  return {grid,shell,window,links:()=>shell.children.at(-1)?.children||[],visible:()=>grid.children.filter(x=>!x.hidden).length,href:()=>href};
}
const none=boot('en',9);
assert.equal(none.shell.children.length,1,'Small new archive has no inert pager');
const archive=boot('en',43);
assert.equal(archive.visible(),12);
assert.equal(archive.links().filter(a=>a.tag==='a'&&a.attrs['aria-current']==='page').length,1);
const next=archive.links().find(x=>x.className.includes('--next'));
assert.ok(next);
const event={button:0,defaultPrevented:false,preventDefault(){this.defaultPrevented=true;}};
next.handlers.click(event);
assert.equal(event.defaultPrevented,true);
assert.ok(archive.href().includes('page=2'));
assert.equal(archive.visible(),12);
assert.equal(archive.grid.children[0].hidden,true);
assert.equal(archive.grid.children[12].hidden,false);
assert.equal(archive.shell.children[1].textContent,'Showing 13–24 of 43 guides');
archive.window.history.pushState({},'', '/blog/?page=4');
archive.window.handlers.popstate();
assert.equal(archive.visible(),7);
assert.equal(archive.grid.children[42].hidden,false);
assert.equal(archive.grid.children[35].hidden,true);
assert.equal(boot('en',43,'/blog/','?page=999').visible(),7,'Deep link clamps to last page');
assert.equal(boot('en',43,'/blog/','?page=bogus').visible(),12);
for(const lang of ['en','es','pt','ru','tr']){
 const test=boot(lang,49,'/'+(lang==='en'?'':lang+'/')+'blog/','?utm_source=buyer&page=3');
 assert.equal(test.visible(),12,lang);
 assert.equal(test.shell.children[1].textContent.includes('25–36'),true,lang);
 assert.equal(test.links().filter(x=>x.tag==='a'&&x.attrs['aria-current']==='page').length,1,lang);
 assert.equal(test.links().some(x=>x.tag==='a'&&x.href.includes('utm_source=buyer')),true,lang);
}
assert.equal(boot('en',13).visible(),12);
assert.equal(boot('en',120).visible(),12,'No fixed number of source blog posts');
assert.equal(boot('en',0).visible(),0);
console.log('XUYI_BLOG_PAGER_5_LOCALES_12_PER_PAGE_HISTORY_ACCESSIBILITY_CMS_GROWTH_PASS');