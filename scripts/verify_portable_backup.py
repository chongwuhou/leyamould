#!/usr/bin/env python3
"""Read-only D1 + R2 integrity verification for XUYI's local recovery files."""
from pathlib import Path
import hashlib
import json
import sqlite3
import sys

BASE=Path(__file__).resolve().parent.parent/"_local_ops"/"xuyi-architecture-migration"
SQL=Path(__file__).resolve().parent.parent/"_local_ops"/"xuyi-d1-backup-initial.sql"
R2=BASE/"backup-r2"

def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for part in iter(lambda:stream.read(1024*1024),b""):
            h.update(part)
    return h.hexdigest()

def main():
    if not SQL.is_file() or SQL.stat().st_size==0:
        raise RuntimeError("D1 SQL backup missing")
    db=sqlite3.connect(":memory:")
    try:
        db.executescript(SQL.read_text(encoding="utf-8"))
        tables=[t[0] for t in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )]
        if not tables:raise RuntimeError("D1 restore contains zero tables")
        print("D1_RESTORE_OK",len(tables),"tables","sha256",sha256(SQL))
    finally:db.close()

    inventory=json.loads((R2/"r2-manifest.json").read_text(encoding="utf-8"))
    if inventory.get("bucket")!="xuyi-drinkware-r2":
        raise RuntimeError("Wrong backup bucket")
    items=inventory["items"]
    ready=0;missing=[];total=0
    for index,item in enumerate(items):
        file=R2/"objects"/(str(index).zfill(6)+".bin")
        if not file.is_file() or file.stat().st_size!=int(item["size"]):
            missing.append(index);continue
        ready+=1;total+=file.stat().st_size
    print("R2_OBJECTS",ready,"of",len(items),"VERIFIED_BY_SIZE","bytes",total)
    if missing:
        print("R2_BACKUP_INCOMPLETE",len(missing),"missing objects")
        return 2
    report=R2/"r2-backup-verified.json"
    if not report.is_file():raise RuntimeError("R2 SHA256 manifest missing")
    saved=json.loads(report.read_text(encoding="utf-8"))
    if saved["objectCount"]!=len(items):
        raise RuntimeError("R2 count mismatch")
    for entry in saved["objects"]:
        blob=R2/entry["path"]
        if sha256(blob)!=entry["sha256"]:
            raise RuntimeError("R2 SHA256 failure")
    print("R2_SHA256_OK",len(items),"objects")
    print("XUYI_BACKUP_VERIFIED_FOR_OFFLINE_RECOVERY")
    return 0

if __name__=="__main__":
    sys.exit(main())
