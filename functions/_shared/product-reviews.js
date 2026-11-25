// Only real buyer feedback, for the exact product they reviewed.
export const REVIEW_TABLE = [
 "CREATE TABLE IF NOT EXISTS xuyi_product_reviews (",
 "id TEXT PRIMARY KEY,",
 "model TEXT NOT NULL,",
 "rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),",
 "author TEXT NOT NULL,",
 "review_date TEXT NOT NULL,",
 "content TEXT NOT NULL,",
 "source_url TEXT NOT NULL DEFAULT '',",
 "source_verified_at TEXT NOT NULL DEFAULT '',",
 "status TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','published')),",
 "created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,",
 "updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
].join(" ");
export async function ensureProductReviews(db){
 await db.prepare(REVIEW_TABLE).run();
 const columns=(await db.prepare("PRAGMA table_info(xuyi_product_reviews)").all()).results||[];
 if(!columns.some(row=>row.name==="source_url"))await db.prepare("ALTER TABLE xuyi_product_reviews ADD COLUMN source_url TEXT NOT NULL DEFAULT ''").run();
 if(!columns.some(row=>row.name==="source_verified_at"))await db.prepare("ALTER TABLE xuyi_product_reviews ADD COLUMN source_verified_at TEXT NOT NULL DEFAULT ''").run();
}
const validDate = value => {
 if(!/^\d{4}-\d{2}-\d{2}$/.test(value))return false;
 const date=new Date(value+"T00:00:00Z");
 return Number.isFinite(date.getTime())&&date.toISOString().slice(0,10)===value;
};
export function normalizeProductReview(raw){
 const model=String(raw?.model??"").trim(),rating=Number(raw?.rating);
 const author=String(raw?.author??"").trim(),reviewDate=String(raw?.reviewDate??"").trim();
 const content=String(raw?.content??"").trim(),status=raw?.status==="published"?"published":"draft";
 const sourceUrl=String(raw?.sourceUrl??raw?.source_url??"").trim();
 if(!/^[a-zA-Z0-9_\-\u4e00-\u9fff]{1,80}$/.test(model))throw Error("请填写真实产品型号");
 if(!Number.isInteger(rating)||rating<1||rating>5)throw Error("星级必须是客户实际给出的 1–5 星");
 if(author.length<2||author.length>99||/[<>]/.test(author))throw Error("请输入允许公开的姓名（2–99 字符）");
 if(!validDate(reviewDate))throw Error("请输入真实评价日期 YYYY-MM-DD");
 if(content.length<12||content.length>3000)throw Error("请输入真实评价内容（12–3000 字符）");
 if(status==="published"){
   if(raw?.confirmedAuthentic!==true)throw Error("发布前须确认评价与该型号真实对应、星级由客户提供且已获公开授权");
   if(!/^https:\/\//i.test(sourceUrl))throw Error("发布前必须填写可核验的 HTTPS 评价来源");
 }
 return {model,rating,author,reviewDate,content,sourceUrl,status};
}
