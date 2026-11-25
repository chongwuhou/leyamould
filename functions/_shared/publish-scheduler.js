import {bumpPublishRevision,publishableLanguageCodes} from "./site-settings.js";
import {ensureBlogSchema} from "./blog-cms.js";const TASKS_SQL=`CREATE TABLE IF NOT EXISTS xuyi_publish_tasks (id TEXT PRIMARY KEY,content_type TEXT NOT NULL CHECK(content_type IN ('reviews','blog')),name TEXT NOT NULL,enabled INTEGER NOT NULL DEFAULT 1 CHECK(enabled IN (0,1)),timezone TEXT NOT NULL DEFAULT 'Asia/Shanghai',schedule_time TEXT NOT NULL,daily_limit INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)`;
const RUNS_SQL=`CREATE TABLE IF NOT EXISTS xuyi_publish_runs (id TEXT PRIMARY KEY,task_id TEXT NOT NULL,scheduled_for TEXT NOT NULL,started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,finished_at TEXT,status TEXT NOT NULL CHECK(status IN ('running','success','partial','failed')),published_count INTEGER NOT NULL DEFAULT 0,skipped_count INTEGER NOT NULL DEFAULT 0,error TEXT NOT NULL DEFAULT '',UNIQUE(task_id,scheduled_for))`;
const BLOG_QUEUE_SQL=`CREATE TABLE IF NOT EXISTS xuyi_blog_schedule (slug TEXT PRIMARY KEY,scheduled_at TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'scheduled' CHECK(status IN ('scheduled','published','cancelled','needs_review')),approved INTEGER NOT NULL DEFAULT 0 CHECK(approved IN (0,1)),content_sha256 TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,published_at TEXT)`;
const BLOG_LOCALE_QUEUE_SQL=`CREATE TABLE IF NOT EXISTS xuyi_blog_locale_schedule (slug TEXT NOT NULL,locale TEXT NOT NULL,scheduled_at TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'scheduled' CHECK(status IN ('scheduled','published','cancelled','needs_review')),approved INTEGER NOT NULL DEFAULT 0 CHECK(approved IN (0,1)),payload_json TEXT NOT NULL,content_sha256 TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,published_at TEXT,PRIMARY KEY(slug,locale))`;
// Automatic publication is retired. Queue tables/history remain available
// for manual planning, but every execution path fails closed.
export const AUTOMATIC_PUBLICATION_ENABLED=false;
const DEFAULTS=[{id:"reviews-daily",content_type:"reviews",name:"产品评价发布队列（手动）",enabled:0,timezone:"Asia/Shanghai",schedule_time:"09:17",daily_limit:3},{id:"blog-daily",content_type:"blog",name:"Blog 发布队列（手动）",enabled:0,timezone:"Asia/Shanghai",schedule_time:"00:00",daily_limit:3}];
async function ensureLocaleQueue(db){
 const row=await db.prepare("SELECT sql FROM sqlite_master WHERE type='table' AND name='xuyi_blog_locale_schedule'").first();
 const sql=String(row?.sql||"").toLowerCase();
 if(sql&&sql.includes("locale in ('es','pt','ru','tr')")){
  const legacy="xuyi_blog_locale_schedule_legacy";
  const legacyRow=await db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name=?").bind(legacy).first();
  if(!legacyRow)await db.prepare("ALTER TABLE xuyi_blog_locale_schedule RENAME TO "+legacy).run();
  await db.prepare(BLOG_LOCALE_QUEUE_SQL).run();
  await db.prepare("INSERT OR IGNORE INTO xuyi_blog_locale_schedule(slug,locale,scheduled_at,status,approved,payload_json,content_sha256,created_at,updated_at,published_at) SELECT slug,locale,scheduled_at,status,approved,payload_json,content_sha256,created_at,updated_at,published_at FROM "+legacy).run();
  await db.prepare("DROP TABLE "+legacy).run();
 }else await db.prepare(BLOG_LOCALE_QUEUE_SQL).run();
}
async function localizedBlogLocales(db){return publishableLanguageCodes(db,{excludeSource:true});}
export async function ensurePublishScheduler(db){
 await db.prepare(TASKS_SQL).run();await db.prepare(RUNS_SQL).run();await db.prepare(BLOG_QUEUE_SQL).run();await ensureLocaleQueue(db);
 await db.prepare("CREATE INDEX IF NOT EXISTS idx_xuyi_blog_schedule_due ON xuyi_blog_schedule(status,scheduled_at)").run();
 await db.prepare("CREATE INDEX IF NOT EXISTS idx_xuyi_blog_locale_schedule_due ON xuyi_blog_locale_schedule(status,scheduled_at,slug)").run();
 for(const t of DEFAULTS)await db.prepare("INSERT OR IGNORE INTO xuyi_publish_tasks(id,content_type,name,enabled,timezone,schedule_time,daily_limit) VALUES(?,?,?,?,?,?,?)").bind(t.id,t.content_type,t.name,t.enabled,t.timezone,t.schedule_time,t.daily_limit).run();
 await db.prepare("UPDATE xuyi_publish_tasks SET enabled=0 WHERE enabled<>0").run();
 }export function localClock(now,timezone){const p=Object.fromEntries(new Intl.DateTimeFormat("en-GB",{timeZone:timezone,year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hourCycle:"h23"}).formatToParts(now).map(x=>[x.type,x.value]));return {date:p.year+"-"+p.month+"-"+p.day,time:p.hour+":"+p.minute};}
export function taskPublishedToday(rows,taskId,date){
 return rows.filter(x=>{
  if(x.task_id!==taskId||!["success","partial"].includes(x.status))return false;
  try{return localClock(new Date(String(x.started_at).replace(" ","T")+"Z"),"Asia/Shanghai").date===date}catch{return false;}
 }).reduce((sum,x)=>sum+Math.max(0,Number(x.published_count||0)),0);
}
export function dailyRemaining(globalLimit,globalPublished,taskLimit,taskPublished){
 return Math.max(0,Math.min(Number(globalLimit)-Number(globalPublished),Number(taskLimit)-Number(taskPublished)));
}

function nextRunLabel(task,now,runs){
 return "自动发布已关闭 · 仅保留手动队列记录";
}
export async function getPublishTasks(db){
 await ensurePublishScheduler(db);
 const tasks=(await db.prepare("SELECT * FROM xuyi_publish_tasks ORDER BY content_type,name,id").all()).results||[];
 const runs=(await db.prepare("SELECT * FROM xuyi_publish_runs ORDER BY started_at DESC LIMIT 100").all()).results||[];
 const now=new Date();
 return {tasks:tasks.map(t=>({...t,enabled:Boolean(t.enabled),nextRun:nextRunLabel(t,now,runs)})),runs};
}export async function savePublishTask(db,input){
 await ensurePublishScheduler(db);
 const id=String(input?.id||"").trim()||("task-"+crypto.randomUUID());
 if(!/^[a-z0-9][a-z0-9-]{2,70}$/.test(id))throw Error("任务 ID 格式无效");
 const type=String(input?.content_type||"");if(!["reviews","blog"].includes(type))throw Error("任务类型只能是产品评价或 Blog");
 const name=String(input?.name||"").trim().slice(0,100);if(name.length<2)throw Error("请填写任务名称");
 const timezone=String(input?.timezone||"Asia/Shanghai");try{new Intl.DateTimeFormat("en-US",{timeZone:timezone}).format(new Date())}catch{throw Error("时区无效")}
 if(type==="reviews"&&timezone!=="Asia/Shanghai")throw Error("产品评价日期和每日发布上限按北京时间统计，评价任务时区固定为 Asia/Shanghai");
 const time=String(input?.schedule_time||"");if(!/^([01]\d|2[0-3]):[0-5]\d$/.test(time))throw Error("执行时间必须为 HH:mm");
 const limit=Number(input?.daily_limit),max=type==="reviews"?20:10;if(!Number.isInteger(limit)||limit<1||limit>max)throw Error("每日数量超出允许范围 1–"+max);
 const existing=await db.prepare("SELECT content_type FROM xuyi_publish_tasks WHERE id=?").bind(id).first();
 if(["reviews-daily","blog-daily"].includes(id)&&existing&&existing.content_type!==type)throw Error("系统默认任务类型不能更改");
 if(input?.enabled===true||input?.enabled===1)throw Error("自动发布已关闭；任务只能保存为手动队列");
 await db.prepare("INSERT INTO xuyi_publish_tasks(id,content_type,name,enabled,timezone,schedule_time,daily_limit) VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET content_type=excluded.content_type,name=excluded.name,enabled=0,timezone=excluded.timezone,schedule_time=excluded.schedule_time,daily_limit=excluded.daily_limit,updated_at=CURRENT_TIMESTAMP").bind(id,type,name,0,timezone,time,limit).run();
 return {id};
}export async function mutatePublishTask(db,action,id){
 await ensurePublishScheduler(db);const key=String(id||"");if(!/^[a-z0-9][a-z0-9-]{2,70}$/.test(key))throw Error("任务 ID 无效");
 if(action==="delete"){if(["reviews-daily","blog-daily"].includes(key))throw Error("系统默认任务不能删除，可以暂停");await db.prepare("DELETE FROM xuyi_publish_tasks WHERE id=?").bind(key).run();return {deleted:true};}
 if(action==="pause"||action==="resume"){
  if(action==="resume")throw Error("自动发布已关闭；不能恢复自动执行");
  const task=await db.prepare("SELECT content_type,daily_limit FROM xuyi_publish_tasks WHERE id=?").bind(key).first();if(!task)throw Error("任务不存在");
  const enabled=action==="resume"?1:0;
  if(enabled){const max=task.content_type==="reviews"?20:10;const active=(await db.prepare("SELECT daily_limit FROM xuyi_publish_tasks WHERE content_type=? AND enabled=1 AND id<>?").bind(task.content_type,key).all()).results||[];const total=active.reduce((sum,x)=>sum+Number(x.daily_limit||0),0);if(total+Number(task.daily_limit||0)>max)throw Error("恢复后同类型每日总上限会超过 "+max+" 条");}
  const r=await db.prepare("UPDATE xuyi_publish_tasks SET enabled=?,updated_at=CURRENT_TIMESTAMP WHERE id=?").bind(enabled,key).run();if(!r.meta?.changes)throw Error("任务不存在");return {enabled:Boolean(enabled)};
 }
 throw Error("未知任务操作");
}
export async function claimDuePublishTasks(db,now=new Date()){
 if(!AUTOMATIC_PUBLICATION_ENABLED)return {claimed:[],globalReviewLimit:0,disabled:true};
 await ensurePublishScheduler(db);
 const tasks=(await db.prepare("SELECT * FROM xuyi_publish_tasks WHERE enabled=1 ORDER BY content_type,schedule_time").all()).results||[];
 const claimed=[];
 const blogTasks=tasks.filter(t=>t.content_type==="blog");
 let blogPublishedRows=[];
 if(blogTasks.length){
  await ensureBlogSchema(db);
  await db.prepare("UPDATE xuyi_blog_schedule SET status='cancelled',approved=0,updated_at=CURRENT_TIMESTAMP WHERE status='scheduled' AND EXISTS (SELECT 1 FROM xuyi_blog_posts WHERE slug=xuyi_blog_schedule.slug AND status IN ('published','retired'))").run();
  blogPublishedRows=(await db.prepare("SELECT published_at FROM xuyi_blog_schedule WHERE status='published' AND published_at IS NOT NULL").all()).results||[];
 }
 for(const task of tasks){
  let clock;try{clock=localClock(now,task.timezone)}catch{continue}
  let scheduledFor=clock.date;
  if(task.content_type==="reviews"&&task.created_at){try{const created=localClock(new Date(String(task.created_at).replace(" ","T")+"Z"),task.timezone);if(created.date===clock.date&&created.time>=task.schedule_time)continue;}catch{}}
  if(task.content_type==="reviews"){
   if(clock.time<task.schedule_time)continue;
  }else{
   if(clock.time<task.schedule_time)continue;
   const due=await db.prepare("SELECT COUNT(*) AS n FROM xuyi_blog_schedule WHERE status='scheduled' AND approved=1 AND scheduled_at<=?").bind(now.toISOString()).first();
   if(Number(due?.n||0)<1)continue;
   const active=blogTasks.reduce((sum,t)=>sum+Number(t.daily_limit||0),0);
   const quotaDate=localClock(now,"Asia/Shanghai").date;
   const already=blogPublishedRows.filter(x=>{try{return localClock(new Date(x.published_at),"Asia/Shanghai").date===quotaDate}catch{return false}}).length;
   const taskRuns=(await db.prepare("SELECT task_id,started_at,published_count,status FROM xuyi_publish_runs WHERE task_id=? AND status IN ('success','partial')").bind(task.id).all()).results||[];
   const taskAlready=taskPublishedToday(taskRuns,task.id,quotaDate);
   if(already>=active||taskAlready>=Number(task.daily_limit||0))continue;
   const [hh,mm]=clock.time.split(":").map(Number),bucket=Math.floor((hh*60+mm)/5)*5;
   scheduledFor=clock.date+"T"+String(Math.floor(bucket/60)).padStart(2,"0")+":"+String(bucket%60).padStart(2,"0");
  }
  const id=crypto.randomUUID(),result=await db.prepare("INSERT OR IGNORE INTO xuyi_publish_runs(id,task_id,scheduled_for,status) VALUES(?,?,?,'running')").bind(id,task.id,scheduledFor).run();
  if(Number(result.meta?.changes||0)===1)claimed.push({...task,run_id:id,scheduled_for:scheduledFor});
 }
 const reviewTasks=tasks.filter(t=>t.content_type==="reviews");
 return {claimed,globalReviewLimit:reviewTasks.reduce((sum,t)=>sum+Number(t.daily_limit||0),0)};
}
export async function scheduleBlogLocalePost(db,{slug,locale,scheduledAt,approved,payloadJson}){
 await ensurePublishScheduler(db);
 const key=String(slug||""),loc=String(locale||"").toLowerCase(),time=Date.parse(String(scheduledAt||""));
 if(!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(key))throw Error("Localized schedule slug is invalid");
 if(!(await localizedBlogLocales(db)).includes(loc))throw Error("Localized schedule locale is not enabled in D1 language configuration");
 if(!Number.isFinite(time)||time<=Date.now())throw Error("Localized publication time must be in the future");
 if(approved!==true)throw Error("Localized article requires explicit owner authorization");
 const payload=String(payloadJson||"");
 if(payload.length<1000||payload.length>300000)throw Error("Localized payload size is invalid");
 let parsed;try{parsed=JSON.parse(payload)}catch{throw Error("Localized payload JSON is invalid")}
 if(parsed?.locale!==loc||!parsed?.translated?.title||!parsed?.translated?.description||!parsed?.translated?.mainHtml||!parsed?.indexCardHtml)
  throw Error("Localized payload fields are incomplete");
 const digest=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(payload));
 const hash=Array.from(new Uint8Array(digest),x=>x.toString(16).padStart(2,"0")).join("");
 const iso=new Date(time).toISOString();
 const existing=await db.prepare("SELECT status,scheduled_at,approved,payload_json,content_sha256 FROM xuyi_blog_locale_schedule WHERE slug=? AND locale=?").bind(key,loc).first();
 if(existing){
  if(existing.status==="scheduled"&&Number(existing.approved)===1&&existing.scheduled_at===iso&&existing.payload_json===payload&&existing.content_sha256===hash)
   return {slug:key,locale:loc,scheduledAt:iso,approved:true,reused:true};
  throw Error("Existing localized schedule conflicts with the approved payload: "+key+" "+loc);
 }
 await db.prepare("INSERT INTO xuyi_blog_locale_schedule(slug,locale,scheduled_at,status,approved,payload_json,content_sha256) VALUES(?,?,?,'scheduled',1,?,?)").bind(key,loc,iso,payload,hash).run();
 const saved=await db.prepare("SELECT status,scheduled_at,approved,content_sha256 FROM xuyi_blog_locale_schedule WHERE slug=? AND locale=?").bind(key,loc).first();
 if(saved?.status!=="scheduled"||Number(saved.approved)!==1||saved.scheduled_at!==iso||saved.content_sha256!==hash)
  throw Error("Localized schedule verification failed: "+key+" "+loc);
 return {slug:key,locale:loc,scheduledAt:iso,approved:true,reused:false};
}

export async function publishDueBlogPosts(db,task,now=new Date()){
 if(!AUTOMATIC_PUBLICATION_ENABLED)return {published:0,skipped:0,needsReview:0,disabled:true};
 await ensurePublishScheduler(db);await ensureBlogSchema(db);
 const active=(await db.prepare("SELECT daily_limit FROM xuyi_publish_tasks WHERE content_type='blog' AND enabled=1").all()).results||[];
 const dailyLimit=active.reduce((sum,x)=>sum+Number(x.daily_limit||0),0);
 const dueCount=Number((await db.prepare("SELECT COUNT(*) AS n FROM xuyi_blog_schedule WHERE status='scheduled' AND approved=1 AND scheduled_at<=?").bind(now.toISOString()).first())?.n||0);
 await db.prepare("UPDATE xuyi_blog_schedule SET status='cancelled',approved=0,updated_at=CURRENT_TIMESTAMP WHERE status='scheduled' AND EXISTS (SELECT 1 FROM xuyi_blog_posts WHERE slug=xuyi_blog_schedule.slug AND status IN ('published','retired'))").run();
 await db.prepare("UPDATE xuyi_blog_locale_schedule SET status='cancelled',approved=0,updated_at=CURRENT_TIMESTAMP WHERE status='scheduled' AND EXISTS (SELECT 1 FROM xuyi_blog_schedule WHERE slug=xuyi_blog_locale_schedule.slug AND status IN ('cancelled','needs_review'))").run();
 const quotaDate=localClock(now,"Asia/Shanghai").date;
 const publishedRows=(await db.prepare("SELECT published_at FROM xuyi_blog_schedule WHERE status='published' AND published_at IS NOT NULL").all()).results||[];
 const already=publishedRows.filter(x=>{try{return localClock(new Date(x.published_at),"Asia/Shanghai").date===quotaDate}catch{return false}}).length;
 const taskRuns=(await db.prepare("SELECT task_id,started_at,published_count,status FROM xuyi_publish_runs WHERE task_id=? AND status IN ('success','partial')").bind(task.id).all()).results||[];
 const taskAlready=taskPublishedToday(taskRuns,task.id,quotaDate);
 const remaining=dailyRemaining(dailyLimit,already,task.daily_limit,taskAlready);
 if(!remaining||!dueCount)return {published:0,skipped:dueCount,needsReview:0};
 const rows=(await db.prepare("SELECT q.slug,q.scheduled_at,q.content_sha256,p.status,p.content_json FROM xuyi_blog_schedule q JOIN xuyi_blog_posts p ON p.slug=q.slug WHERE q.status='scheduled' AND q.approved=1 AND q.scheduled_at<=? AND p.status='draft' ORDER BY q.scheduled_at,q.slug LIMIT ?").bind(now.toISOString(),Math.min(10,remaining)).all()).results||[];
 let published=0,needsReview=0;
 const locales=await localizedBlogLocales(db),tail="</div></div></section>";
 const blocked=/<\s*(?:script|iframe|object|embed|form|style|link|base|meta|svg|math|template)\b|\bon[a-z-]+\s*=|\bsrcdoc\s*=|(?:javascript|vbscript|data)\s*:/i;
 const count=(v,n)=>String(v).split(n).length-1;
 const hash=async v=>Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",new TextEncoder().encode(v))),x=>x.toString(16).padStart(2,"0")).join("");
 const markReview=async slug=>db.batch([
  db.prepare("UPDATE xuyi_blog_schedule SET status='needs_review',approved=0,updated_at=CURRENT_TIMESTAMP WHERE slug=? AND status='scheduled'").bind(slug),
  db.prepare("UPDATE xuyi_blog_locale_schedule SET status='needs_review',approved=0,updated_at=CURRENT_TIMESTAMP WHERE slug=? AND status='scheduled'").bind(slug)
 ]);
 for(const row of rows){
  if(await hash(row.content_json)!==row.content_sha256){needsReview++;await markReview(row.slug);continue;}
  let post;try{post=JSON.parse(row.content_json)}catch{needsReview++;await markReview(row.slug);continue;}
  const localeRows=(await db.prepare("SELECT locale,scheduled_at,status,approved,payload_json,content_sha256 FROM xuyi_blog_locale_schedule WHERE slug=?").bind(row.slug).all()).results||[];
  if(localeRows.length!==locales.length||locales.some(loc=>!localeRows.some(x=>x.locale===loc&&x.status==="scheduled"&&Number(x.approved)===1&&x.scheduled_at===row.scheduled_at))){
   needsReview++;await markReview(row.slug);continue;
  }
  const prepared=[];let invalid=false;
  for(const loc of locales){
   const q=localeRows.find(x=>x.locale===loc);
   if(await hash(q.payload_json)!==q.content_sha256){invalid=true;break;}
   let payload;try{payload=JSON.parse(q.payload_json)}catch{invalid=true;break;}
   const translated=payload?.translated,html=String(translated?.mainHtml||""),card=String(payload?.indexCardHtml||"");
   if(payload?.locale!==loc||String(translated?.title||"").length<12||String(translated?.description||"").length<25||
      html.length<5000||html.length>250000||blocked.test(html)||count(html,'class="blog-section"')!==7||
      count(html,'class="blog-editorial__product-link"')!==3||count(html,'class="blog-related__item"')!==3||
      count(html,'class="blog-buyer-matrix"')!==1||count(html,"<details>")!==4||!html.includes('src="'+post.cover+'"')||
      !card.startsWith('<article class="news-card">')||!card.endsWith("</article>")||blocked.test(card)||
      count(card,'href="/blog/'+row.slug+'/"')!==3||!card.includes('src="'+post.cover+'"')){invalid=true;break;}
   const resource="page:/blog/"+row.slug+"/",detailJson=JSON.stringify({title:translated.title,description:translated.description,mainHtml:html});
   const existing=await db.prepare("SELECT translated_json FROM xuyi_translation_overrides WHERE resource_id=? AND locale=?").bind(resource,loc).first();
   if(existing){let saved;try{saved=JSON.parse(existing.translated_json)}catch{invalid=true;break;}if(saved.title!==translated.title||saved.description!==translated.description||saved.mainHtml!==html){invalid=true;break;}}
   const indexRow=await db.prepare("SELECT translated_json FROM xuyi_translation_overrides WHERE resource_id='page:/blog/' AND locale=?").bind(loc).first();
   if(!indexRow){invalid=true;break;}
   let index;try{index=JSON.parse(indexRow.translated_json)}catch{invalid=true;break;}
   const oldHtml=String(index.mainHtml||""),href='href="/blog/'+row.slug+'/"',n=count(oldHtml,href);
   if(n===0&&!oldHtml.endsWith(tail)){invalid=true;break;}
   if(n!==0&&(n!==3||!oldHtml.includes(card))){invalid=true;break;}
   if(n===0)index.mainHtml=oldHtml.slice(0,-tail.length)+card+tail;
   prepared.push({locale:loc,q,resource,detailJson,card,indexOld:indexRow.translated_json,indexNew:n===0?JSON.stringify(index):indexRow.translated_json,updateIndex:n===0,existingDetail:Boolean(existing)});
  }
  if(invalid||prepared.length!==locales.length){needsReview++;await markReview(row.slug);continue;}
  let preGate="EXISTS (SELECT 1 FROM xuyi_blog_schedule q WHERE q.slug=? AND q.status='scheduled' AND q.approved=1 AND q.scheduled_at=? AND q.content_sha256=?) AND EXISTS (SELECT 1 FROM xuyi_blog_posts p WHERE p.slug=? AND p.status='draft' AND p.content_json=?)";
  const preArgs=[row.slug,row.scheduled_at,row.content_sha256,row.slug,row.content_json];
  for(const x of prepared){
   preGate+=" AND EXISTS (SELECT 1 FROM xuyi_blog_locale_schedule l WHERE l.slug=? AND l.locale=? AND l.status='scheduled' AND l.approved=1 AND l.scheduled_at=? AND l.content_sha256=? AND l.payload_json=?)";
   preArgs.push(row.slug,x.locale,row.scheduled_at,x.q.content_sha256,x.q.payload_json);
   preGate+=" AND EXISTS (SELECT 1 FROM xuyi_translation_overrides i WHERE i.resource_id='page:/blog/' AND i.locale=? AND i.translated_json IN (?,?))";
   preArgs.push(x.locale,x.indexOld,x.indexNew);
   preGate+=" AND NOT EXISTS (SELECT 1 FROM xuyi_translation_overrides d WHERE d.resource_id=? AND d.locale=? AND d.translated_json<>?)";
   preArgs.push(x.resource,x.locale,x.detailJson);
  }
  const statements=[];
  for(const x of prepared){
   if(!x.existingDetail)statements.push(db.prepare("INSERT INTO xuyi_translation_overrides(resource_id,locale,translated_json,reviewed_at) SELECT ?,?,?,? WHERE "+preGate+" ON CONFLICT(resource_id,locale) DO NOTHING").bind(x.resource,x.locale,x.detailJson,quotaDate,...preArgs));
   if(x.updateIndex)statements.push(db.prepare("UPDATE xuyi_translation_overrides SET translated_json=?,reviewed_at=? WHERE resource_id='page:/blog/' AND locale=? AND translated_json=? AND "+preGate).bind(x.indexNew,quotaDate,x.locale,x.indexOld,...preArgs));
  }
  let publishGate="EXISTS (SELECT 1 FROM xuyi_blog_schedule q WHERE q.slug=? AND q.status='scheduled' AND q.approved=1 AND q.scheduled_at=? AND q.content_sha256=?) AND EXISTS (SELECT 1 FROM xuyi_blog_posts p WHERE p.slug=? AND p.status='draft' AND p.content_json=?)";
  const publishArgs=[row.slug,row.scheduled_at,row.content_sha256,row.slug,row.content_json];
  for(const x of prepared){
   publishGate+=" AND EXISTS (SELECT 1 FROM xuyi_blog_locale_schedule l WHERE l.slug=? AND l.locale=? AND l.status='scheduled' AND l.approved=1 AND l.scheduled_at=? AND l.content_sha256=?)";
   publishArgs.push(row.slug,x.locale,row.scheduled_at,x.q.content_sha256);
   publishGate+=" AND EXISTS (SELECT 1 FROM xuyi_translation_overrides d WHERE d.resource_id=? AND d.locale=? AND d.translated_json=?)";
   publishArgs.push(x.resource,x.locale,x.detailJson);
   publishGate+=" AND EXISTS (SELECT 1 FROM xuyi_translation_overrides i WHERE i.resource_id='page:/blog/' AND i.locale=? AND instr(json_extract(i.translated_json,'$.mainHtml'),?)>0)";
   publishArgs.push(x.locale,x.card);
  }
  statements.push(db.prepare("UPDATE xuyi_blog_posts SET status='published',published_at=?,updated_at=CURRENT_TIMESTAMP WHERE slug=? AND status='draft' AND content_json=? AND "+publishGate).bind(now.toISOString(),row.slug,row.content_json,...publishArgs));
  statements.push(db.prepare("UPDATE xuyi_blog_schedule SET status='published',published_at=?,updated_at=CURRENT_TIMESTAMP WHERE slug=? AND status='scheduled' AND approved=1 AND content_sha256=? AND EXISTS (SELECT 1 FROM xuyi_blog_posts WHERE slug=? AND status='published')").bind(now.toISOString(),row.slug,row.content_sha256,row.slug));
  for(const x of prepared)statements.push(db.prepare("UPDATE xuyi_blog_locale_schedule SET status='published',published_at=?,updated_at=CURRENT_TIMESTAMP WHERE slug=? AND locale=? AND status='scheduled' AND approved=1 AND content_sha256=? AND EXISTS (SELECT 1 FROM xuyi_blog_posts WHERE slug=? AND status='published')").bind(now.toISOString(),row.slug,x.locale,x.q.content_sha256,row.slug));
  await db.batch(statements);
  const postState=await db.prepare("SELECT status FROM xuyi_blog_posts WHERE slug=?").bind(row.slug).first();
  const enState=await db.prepare("SELECT status FROM xuyi_blog_schedule WHERE slug=?").bind(row.slug).first();
  const locState=(await db.prepare("SELECT locale,status FROM xuyi_blog_locale_schedule WHERE slug=?").bind(row.slug).all()).results||[];
  if(postState?.status==="published"&&enState?.status==="published"&&locState.length===locales.length&&locState.every(x=>x.status==="published"))published++;
  else{
   needsReview++;await markReview(row.slug);
   if(postState?.status==="published"){
    await db.prepare("UPDATE xuyi_blog_posts SET status='draft',published_at=NULL,updated_at=CURRENT_TIMESTAMP WHERE slug=? AND status='published'").bind(row.slug).run();
    await db.prepare("UPDATE xuyi_blog_schedule SET status='needs_review',approved=0,published_at=NULL,updated_at=CURRENT_TIMESTAMP WHERE slug=?").bind(row.slug).run();
   }
  }
 }
 if(published)await bumpPublishRevision(db);
 const left=Number((await db.prepare("SELECT COUNT(*) AS n FROM xuyi_blog_schedule WHERE status='scheduled' AND approved=1 AND scheduled_at<=?").bind(now.toISOString()).first())?.n||0);
 return {published,skipped:left,needsReview};
}

export async function finishPublishRun(db,runId,result){
 const status=result?.error?"failed":(Number(result?.skipped||0)||Number(result?.needsReview||0)?"partial":"success");
 const r=await db.prepare("UPDATE xuyi_publish_runs SET finished_at=CURRENT_TIMESTAMP,status=?,published_count=?,skipped_count=?,error=? WHERE id=? AND status='running'").bind(status,Math.max(0,Number(result?.published||0)),Math.max(0,Number(result?.skipped||0)+Number(result?.needsReview||0)),String(result?.error||"").slice(0,500),String(runId||"")).run();
 return {updated:Number(r.meta?.changes||0)===1,status};
}
export async function scheduleBlogPost(db,{slug,scheduledAt,approved,contentJson}){
 await ensurePublishScheduler(db);const time=Date.parse(String(scheduledAt||""));if(!Number.isFinite(time)||time<=Date.now())throw Error("计划时间必须是未来时间");if(approved!==true)throw Error("保存发布计划前必须确认文章已完成正文、产品内链、相关阅读和封面审核");
 const content=String(contentJson||""),digest=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(content)),hash=Array.from(new Uint8Array(digest),x=>x.toString(16).padStart(2,"0")).join("");
 await db.prepare("INSERT INTO xuyi_blog_schedule(slug,scheduled_at,status,approved,content_sha256) VALUES(?,?,'scheduled',1,?) ON CONFLICT(slug) DO UPDATE SET scheduled_at=excluded.scheduled_at,status='scheduled',approved=1,content_sha256=excluded.content_sha256,updated_at=CURRENT_TIMESTAMP,published_at=NULL").bind(slug,new Date(time).toISOString(),hash).run();return {slug,scheduledAt:new Date(time).toISOString(),approved:true};
}
export async function cancelBlogSchedule(db,slug){
 await ensurePublishScheduler(db);
 const r=await db.prepare("UPDATE xuyi_blog_schedule SET status='cancelled',approved=0,updated_at=CURRENT_TIMESTAMP WHERE slug=? AND status='scheduled'").bind(slug).run();
 await db.prepare("UPDATE xuyi_blog_locale_schedule SET status='cancelled',approved=0,updated_at=CURRENT_TIMESTAMP WHERE slug=? AND status='scheduled'").bind(slug).run();
 return {cancelled:Number(r.meta?.changes||0)===1};
}


