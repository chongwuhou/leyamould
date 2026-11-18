#!/usr/bin/env python3
"""P0 permanent owner source-of-truth policy gate.

The release must keep readable, linked template/CMS-first instructions, never
track generated dist artifacts, and keep CMS/rebuild regression tests enabled.
This is a structural guard, not a substitute for reviewing each implementation.
"""
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parent.parent
agents=(ROOT/"AGENTS.md").read_text(encoding="utf8")
policy=(ROOT/"PROJECT_CHANGE_POLICY.md").read_text(encoding="utf8")
readme=(ROOT/"README.md").read_text(encoding="utf8")
workflow=(ROOT/".github/workflows/publish-xuyi.yml").read_text(encoding="utf8")
standard=(ROOT/"项目圣经/统一内容发布与翻译审计标准.md").read_text(encoding="utf8")
ignore=(ROOT/".gitignore").read_text(encoding="utf8").splitlines()

assert agents.startswith("# XUYI website mandatory change policy")
assert "每次执行任务，第一步必须阅读本文件" in agents
assert "共享模板/组件/正式源数据或 D1/CMS" in agents
assert "不自动等于模板化" in agents
assert "已有直接在 `dist/` 后处理 HTML 的历史脚本属于待迁移旧债" in agents
assert "用户无须再次提醒" in agents
assert "## P0 / Mandatory owner directive" in policy
assert "A reusable postprocessor" in policy
assert "Temporary testing is allowed" in policy
assert "No regression on future admin updates" in policy
assert "READ BEFORE EVERY TASK" in readme and "AGENTS.md" in readme
assert "PROJECT_CHANGE_POLICY.md" in readme
assert "D1/CMS" in standard and "R2" in standard
assert "AI 只能做草稿" in standard
assert "禁止脚本、插件、自动化或 AI 直接写" in standard
assert "两次干净构建" in standard
assert "翻译审计门禁" in standard
assert "dist/" in ignore or "/dist/" in ignore
for expected in (
    "python scripts/test_source_of_truth_policy.py",
    "python scripts/test_cms_seo_rebuild_policy.py",
    "python scripts/test_source_modules_survive_owner_rebuild.py",
    "python scripts/test_verified_trust_technical_seo.py",
):
    assert expected in workflow,("Missing required release gate",expected)

if not (ROOT/".git").exists():
    # Exported WebCodex workspaces may intentionally omit .git; GitHub CI
    # performs the tracked-output assertion in the real checkout.
    print("NOTE: local workspace has no .git checkout; GitHub runner verifies tracked output")
else:
    result=subprocess.run(["git","ls-files","-z","dist"],
                          cwd=ROOT,capture_output=True,check=True,timeout=15)
    tracked=[item.decode("utf8","replace") for item in result.stdout.split(b"\0") if item]
    assert not tracked,("Generated dist content must not be tracked",tracked[:10])
print("XUYI_P0_TEMPLATE_CMS_OWNER_POLICY_GATE_PASSED")

