#!/usr/bin/env python3
"""Prepare an idempotent D1 baseline from already published XUYI page markup.

Never publishes new models or translations. Never writes the remote D1 itself.
Usage: python scripts/seed_reviewed_baseline.py --output _local_ops/d1-baseline.sql
"""
from __future__ import annotations
from pathlib import Path
from html.parser import HTMLParser
import argparse
import json
import re

ROOT=Path(__file__).resolve().parent.parent
DIST=ROOT/"dist"
def sql(value):
    return "'"+str(value).replace("'","''")+"'"

class Head(HTMLParser):
    def __init__(self):
        super().__init__();self.title="";self.desc="";self.in_title=False
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=="title":self.in_title=True
        if tag=="meta" and d.get("name")=="description":self.desc=d.get("content","")
    def handle_endtag(self,tag):
        if tag=="title":self.in_title=False
    def handle_data(self,data):
        if self.in_title:self.title+=data

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    pages_js=(ROOT/"functions/api/admin/pages.js").read_text(encoding="utf-8")
    site_js=(ROOT/"functions/api/admin/site-config.js").read_text(encoding="utf-8")
    matched=re.search(r"const DEFAULT_PAGES\s*=\s*(\[[\s\S]*?\])\.map",pages_js)
    assert matched,"Missing XUYI managed pages source"
    rows=json.loads(matched.group(1))
    matched=re.search(r"const DEFAULT_NAVIGATION\s*=\s*(\[[\s\S]*?\]);",site_js)
    assert matched,"Missing XUYI managed navigation source"
    nav=json.loads(matched.group(1))
    out=["-- XUYI approved-public-HTML baseline, source-only; non-destructive, INSERT OR IGNORE.",
         "-- New pages are still noindex, no new product is published.",
         "-- Wrangler/D1 handles statement transactions;"]
    page_count=0
    for route,label in rows:
        local=DIST/route.lstrip("/")/"index.html" if route!="/" else DIST/"index.html"
        if not local.is_file():raise RuntimeError("Managed XUYI page missing: "+route)
        parser=Head();parser.feed(local.read_text(encoding="utf-8"))
        if not 2<=len(parser.title)<=90 or not 8<=len(parser.desc)<=240:
            raise RuntimeError("Bad reviewed public SEO markup: "+route)
        out.append("INSERT OR IGNORE INTO site_pages(route,label,seo_title,meta_description,robots,sitemap_enabled) VALUES("+",".join(
            map(sql,(route,label,parser.title,parser.desc,"noindex,nofollow")))+",0);")
        page_count+=1
    for row in nav:
        uri=row["url"]
        local=DIST/uri.lstrip("/")/"index.html" if uri!="/" else DIST/"index.html"
        if not local.is_file():raise RuntimeError("Navigation path unavailable: "+uri)
        row_values=(row["id"],row.get("parentId",""),row["label"],uri,int(row["sortOrder"]),int(row.get("newWindow",False)))
        out.append("INSERT OR IGNORE INTO site_navigation(id,parent_id,label,url,sort_order,enabled,new_window) VALUES("+
            ",".join(sql(v) for v in row_values[:5])+",1,"+str(row_values[5])+");")
    out.extend([
        "INSERT INTO site_state(key,value,updated_at) VALUES('publish_revision','1',CURRENT_TIMESTAMP) "
        "ON CONFLICT(key) DO UPDATE SET value=CAST(site_state.value AS INTEGER)+1,updated_at=CURRENT_TIMESTAMP;",
        "INSERT INTO site_state(key,value,updated_at) VALUES('publish_requested_at',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated_at=CURRENT_TIMESTAMP;",
        "-- End of seed statements;"])
    # Dry-run SQL statements in an isolated SQLite database with the same
    # minimal tables. This is a structural check, not permission to publish.
    import sqlite3
    con=sqlite3.connect(":memory:")
    con.executescript("""CREATE TABLE site_pages(route TEXT PRIMARY KEY,label TEXT,seo_title TEXT,
      meta_description TEXT,robots TEXT,sitemap_enabled INTEGER);
      CREATE TABLE site_navigation(id TEXT PRIMARY KEY,parent_id TEXT,label TEXT,url TEXT,
      sort_order INTEGER,enabled INTEGER,new_window INTEGER);
      CREATE TABLE site_state(key TEXT PRIMARY KEY,value TEXT,updated_at TEXT);""")
    con.executescript("\n".join(out))
    assert con.execute("SELECT COUNT(*) FROM site_pages").fetchone()[0]==page_count
    assert con.execute("SELECT COUNT(*) FROM site_navigation").fetchone()[0]==len(nav)
    assert con.execute("SELECT value FROM site_state WHERE key='publish_revision'").fetchone()[0]=="1"
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text("\n".join(out)+"\n",encoding="utf-8")
    print("XUYI_D1_BASELINE_PREPARED","pages",page_count,"navigation",len(nav),"status","idempotent_insert_only","output",args.output)
if __name__=="__main__":main()