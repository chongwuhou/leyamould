#!/usr/bin/env python3
from admin_route import admin_path
assert admin_path(None)=="admin"
assert admin_path("admin")=="admin"
assert admin_path("office-xuyi-2026")=="office-xuyi-2026"
for slug in ("products","blog","about","media","api","admin/other","../admin",
             "es","pt","ru","tr","office space","","XUYI","x"*49):
    try:admin_path(slug)
    except ValueError:continue
    raise AssertionError("Unsafe admin route accepted: "+slug)
print("XUYI_ADMIN_PATH_VALIDATION_PASSED")