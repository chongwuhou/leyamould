# scripts 目录说明

## 日常标准入口

```text
python scripts/preflight.py
python scripts/fetch_build_snapshot.py
python scripts/build_release.py
python scripts/test_release.py
```

根据改动范围再运行多语言、Blog、产品、媒体、路由和 API 回归测试。生产发布只能使用标准构建生成的 `dist/`，不能直接发布仓库根目录。

## 工具边界

- `build_release.py`：从 D1/CMS 快照和共享源生成干净静态发布包。
- `fetch_build_snapshot.py`：读取已鉴权的 XUYI D1/CMS 快照，不向其他项目写入。
- `render_locales.py`：按 D1/config 已配置语种生成经过审核的本地化页面。
- `test_*.py`、`test_*.mjs`：回归、隔离和审计门禁，不得把测试 fixture 写入生产。
- `publish_*.py`、`schedule_*.py`：只允许在明确的工作流条件或人工授权下执行；日期批次脚本是历史回放/验收工具，不是通用发布入口。
- 任何脚本不得直接修改 `dist/` 来替代源模板、D1/CMS 或 R2 的正式修改。

脚本是否仍然有效，以当前工作流、代码引用和测试结果为准；不要仅按文件日期删除仍被正式流程使用的脚本。
