import {bumpPublishRevision} from "./site-settings.js";
import {ensureBlogSchema} from "./blog-cms.js";const TASKS_SQL=`CREATE TABLE IF NOT EXISTS xuyi_publish_tasks (id TEXT PRIMARY KEY,content_type TEXT NOT NULL CHECK(content_type IN ('reviews','blog')),name TEXT NOT NULL,enabled INTEGER NOT NULL DEFAULT 1 CHECK(enabled IN (0,1)),timezone TEXT NOT NULL DEFAULT 'Asia/Shanghai',schedule_time TEXT NOT NULL,daily_limit INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)`;
const RUNS_SQL=`CREATE TABLE IF NOT EXISTS xuyi_publish_runs (id TEXT PRIMARY KEY,task_id TEXT NOT NULL,scheduled_for TEXT NOT NULL,started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,finished_at TEXT,status TEXT NOT NULL CHECK(status IN ('running','success','partial','failed')),published_count INTEGER NOT NULL DEFAULT 0,skipped_count INTEGER NOT NULL DEFAULT 0,error TEXT NOT NULL DEFAULT '',UNIQUE(task_id,scheduled_for))`;
const BLOG_QUEUE_SQL=`CREATE TABLE IF NOT EXISTS xuyi_blog_schedule (slug TEXT PRIMARY KEY,scheduled_at TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'scheduled' CHECK(status IN ('scheduled','published','cancelled','needs_review')),approved INTEGER NOT NULL DEFAULT 0 CHECK(approved IN (0,1)),content_sha256 TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,published_at TEXT)`;
const DEFAULTS=[{id:"reviews-daily",content_type:"reviews",name:"产品评价自动发布",enabled:1,timezone:"Asia/Shanghai",schedule_time:"09:17",daily_limit:3},{id:"blog-daily",content_type:"blog",name:"Blog 文章自动发布",enabled:1,timezone:"Asia/Shanghai",schedule_time:"00:00",daily_limit:3}];export async function ensurePublishScheduler(db){
 await db.prepare(TASKS_SQL).run();await db.prepare(RUNS_SQL).run();await db.prepare(BLOG_QUEUE_SQL).run();
 await db.prepare("CREATE INDEX IF NOT EXISTS idx_xuyi_blog_schedule_due ON xuyi_blog_schedule(status,scheduled_at)").run();
 for(const t of DEFAULTS)await db.prepare("INSERT OR IGNORE INTO xuyi_publish_tasks(id,content_type,name,enabled,timezone,schedule_time,daily_limit) VALUES(?,?,?,?,?,?,?)").bind(t.id,t.content_type,t.name,t.enabled,t.timezone,t.schedule_time,t.daily_limit).run();
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
 try{
  const c=localClock(now,task.timezone);
  if(task.content_type==="blog")return "每5分钟检查（起始 "+task.schedule_time+"） ("+task.timezone+")"+(task.enabled?"":" · 已暂停");
  const ran=runs.some(r=>r.task_id===task.id&&r.scheduled_for===c.date);
  const next=(!ran&&c.time<task.schedule_time)?c.date:localClock(new Date(now.getTime()+36*60*60*1000),task.timezone).date;
  return next+" "+task.schedule_time+" ("+task.timezone+")"+(task.enabled?"":" · 已暂停");
 }catch{return "时区无效"}
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
 const enabled=input?.enabled===false||input?.enabled===0?0:1;
 if(enabled){const active=(await db.prepare("SELECT id,daily_limit FROM xuyi_publish_tasks WHERE content_type=? AND enabled=1 AND id<>?").bind(type,id).all()).results||[];const total=active.reduce((sum,x)=>sum+Number(x.daily_limit||0),0);if(total+limit>max)throw Error("同类型所有启用任务的每日总上限不能超过 "+max+" 条");}
 await db.prepare("INSERT INTO xuyi_publish_tasks(id,content_type,name,enabled,timezone,schedule_time,daily_limit) VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET content_type=excluded.content_type,name=excluded.name,enabled=excluded.enabled,timezone=excluded.timezone,schedule_time=excluded.schedule_time,daily_limit=excluded.daily_limit,updated_at=CURRENT_TIMESTAMP").bind(id,type,name,enabled,timezone,time,limit).run();
 return {id};
}export async function mutatePublishTask(db,action,id){
 await ensurePublishScheduler(db);const key=String(id||"");if(!/^[a-z0-9][a-z0-9-]{2,70}$/.test(key))throw Error("任务 ID 无效");
 if(action==="delete"){if(["reviews-daily","blog-daily"].includes(key))throw Error("系统默认任务不能删除，可以暂停");await db.prepare("DELETE FROM xuyi_publish_tasks WHERE id=?").bind(key).run();return {deleted:true};}
 if(action==="pause"||action==="resume"){
  const task=await db.prepare("SELECT content_type,daily_limit FROM xuyi_publish_tasks WHERE id=?").bind(key).first();if(!task)throw Error("任务不存在");
  const enabled=action==="resume"?1:0;
  if(enabled){const max=task.content_type==="reviews"?20:10;const active=(await db.prepare("SELECT daily_limit FROM xuyi_publish_tasks WHERE content_type=? AND enabled=1 AND id<>?").bind(task.content_type,key).all()).results||[];const total=active.reduce((sum,x)=>sum+Number(x.daily_limit||0),0);if(total+Number(task.daily_limit||0)>max)throw Error("恢复后同类型每日总上限会超过 "+max+" 条");}
  const r=await db.prepare("UPDATE xuyi_publish_tasks SET enabled=?,updated_at=CURRENT_TIMESTAMP WHERE id=?").bind(enabled,key).run();if(!r.meta?.changes)throw Error("任务不存在");return {enabled:Boolean(enabled)};
 }
 throw Error("未知任务操作");
}
export async function claimDuePublishTasks(db,now=new Date()){
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
export async function publishDueBlogPosts(db,task,now=new Date()){
 await ensurePublishScheduler(db);await ensureBlogSchema(db);
 const active=(await db.prepare("SELECT daily_limit FROM xuyi_publish_tasks WHERE content_type='blog' AND enabled=1").all()).results||[];
 const dailyLimit=active.reduce((sum,x)=>sum+Number(x.daily_limit||0),0);
 const dueCount=Number((await db.prepare("SELECT COUNT(*) AS n FROM xuyi_blog_schedule WHERE status='scheduled' AND approved=1 AND scheduled_at<=?").bind(now.toISOString()).first())?.n||0);
 await db.prepare("UPDATE xuyi_blog_schedule SET status='cancelled',approved=0,updated_at=CURRENT_TIMESTAMP WHERE status='scheduled' AND EXISTS (SELECT 1 FROM xuyi_blog_posts WHERE slug=xuyi_blog_schedule.slug AND status IN ('published','retired'))").run();
 const quotaDate=localClock(now,"Asia/Shanghai").date;
 const publishedRows=(await db.prepare("SELECT published_at FROM xuyi_blog_schedule WHERE status='published' AND published_at IS NOT NULL").all()).results||[];
 const already=publishedRows.filter(x=>{try{return localClock(new Date(x.published_at),"Asia/Shanghai").date===quotaDate}catch{return false}}).length;
 const taskRuns=(await db.prepare("SELECT task_id,started_at,published_count,status FROM xuyi_publish_runs WHERE task_id=? AND status IN ('success','partial')").bind(task.id).all()).results||[];
 const taskAlready=taskPublishedToday(taskRuns,task.id,quotaDate);
 const remaining=dailyRemaining(dailyLimit,already,task.daily_limit,taskAlready);
 if(!remaining||!dueCount)return {published:0,skipped:dueCount,needsReview:0};
 const rows=(await db.prepare("SELECT q.slug,q.scheduled_at,q.content_sha256,p.status,p.content_json FROM xuyi_blog_schedule q JOIN xuyi_blog_posts p ON p.slug=q.slug WHERE q.status='scheduled' AND q.approved=1 AND q.scheduled_at<=? AND p.status='draft' ORDER BY q.scheduled_at,q.slug LIMIT ?").bind(now.toISOString(),Math.min(10,remaining)).all()).results||[];
 let published=0,skipped=0,needsReview=0;
 const statements=[],groups=[];
 for(const row of rows){
  const digest=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(row.content_json));
  const hash=Array.from(new Uint8Array(digest),x=>x.toString(16).padStart(2,"0")).join("");
  if(hash!==row.content_sha256){
   needsReview++;
   statements.push(db.prepare("UPDATE xuyi_blog_schedule SET status='needs_review',approved=0,updated_at=CURRENT_TIMESTAMP WHERE slug=? AND status='scheduled'").bind(row.slug));
   groups.push("review");
   continue;
  }
  statements.push(db.prepare("UPDATE xuyi_blog_posts SET status='published',published_at=?,updated_at=CURRENT_TIMESTAMP WHERE slug=? AND status='draft' AND EXISTS (SELECT 1 FROM xuyi_blog_schedule WHERE slug=? AND status='scheduled' AND approved=1 AND content_sha256=?)").bind(now.toISOString(),row.slug,row.slug,hash));
  statements.push(db.prepare("UPDATE xuyi_blog_schedule SET status='published',published_at=?,updated_at=CURRENT_TIMESTAMP WHERE slug=? AND status='scheduled' AND approved=1 AND content_sha256=? AND EXISTS (SELECT 1 FROM xuyi_blog_posts WHERE slug=? AND status='published')").bind(now.toISOString(),row.slug,hash,row.slug));
  groups.push("publish");
 }
 if(statements.length){
  const results=await db.batch(statements);let index=0;
  for(const group of groups){
   if(group==="review"){index++;continue;}
   if(results[index]?.meta?.changes===1&&results[index+1]?.meta?.changes===1)published++;
   index+=2;
  }
 }
 if(published)await bumpPublishRevision(db);
 const left=Number((await db.prepare("SELECT COUNT(*) AS n FROM xuyi_blog_schedule WHERE status='scheduled' AND approved=1 AND scheduled_at<=?").bind(now.toISOString()).first())?.n||0);
 skipped=left;return {published,skipped,needsReview};
}
export async function finishPublishRun(db,runId,result){
 const status=result?.error?"failed":(Number(result?.skipped||0)||Number(result?.needsReview||0)?"partial":"success");
 const r=await db.prepare("UPDATE xuyi_publish_runs SET finished_at=CURRENT_TIMESTAMP,status=?,published_count=?,skipped_count=?,error=? WHERE id=? AND status='running'").bind(status,Math.max(0,Number(result?.published||0)),Math.max(0,Number(result?.skipped||0)+Number(result?.needsReview||0)),String(result?.error||"").slice(0,500),String(runId||"")).run();
 return {updated:Number(r.meta?.changes||0)===1,status};
}
export async function scheduleBlogPost(db,{slug,scheduledAt,approved,contentJson}){
 await ensurePublishScheduler(db);const time=Date.parse(String(scheduledAt||""));if(!Number.isFinite(time)||time<=Date.now())throw Error("定时发布时间必须是未来时间");if(approved!==true)throw Error("自动发布前必须确认文章已完成正文、产品内链、相关阅读和封面审核");
 const content=String(contentJson||""),digest=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(content)),hash=Array.from(new Uint8Array(digest),x=>x.toString(16).padStart(2,"0")).join("");
 await db.prepare("INSERT INTO xuyi_blog_schedule(slug,scheduled_at,status,approved,content_sha256) VALUES(?,?,'scheduled',1,?) ON CONFLICT(slug) DO UPDATE SET scheduled_at=excluded.scheduled_at,status='scheduled',approved=1,content_sha256=excluded.content_sha256,updated_at=CURRENT_TIMESTAMP,published_at=NULL").bind(slug,new Date(time).toISOString(),hash).run();return {slug,scheduledAt:new Date(time).toISOString(),approved:true};
}
export async function cancelBlogSchedule(db,slug){await ensurePublishScheduler(db);const r=await db.prepare("UPDATE xuyi_blog_schedule SET status='cancelled',approved=0,updated_at=CURRENT_TIMESTAMP WHERE slug=? AND status='scheduled'").bind(slug).run();return {cancelled:Number(r.meta?.changes||0)===1};}