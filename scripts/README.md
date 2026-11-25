# scripts 目录说明

## 日常标准入口

```text
python scripts/preflight.py
python scripts/fetch_build_snapshot.py
python scripts/build_release.py
python scripts/test_release.py
python scripts/test_repository_hygiene.py
```

根据改动范围再运行多语言、Blog、产品、媒体、路由和 API 回归测试。生产发布只能使用标准构建生成的 `dist/`，不能直接发布仓库根目录。

## 当前职责边界

- `build_release.py`：从 D1/CMS 快照和共享源生成干净静态发布包。
- `fetch_build_snapshot.py`：读取已鉴权的 XUYI D1/CMS 快照，不向其他项目写入。
- `render_locales.py`：按 D1/config 已配置语种生成经过审核的本地化页面。
- `test_*.py`、`test_*.mjs`：回归、隔离和发布门禁，不得把测试 fixture 写入生产。
- `publish_daily_product_reviews.py`：仅保留为人工审核工具；自动五分钟调度器和 runner 已关闭并从生产入口移除。
- Blog 批量发布、翻译修复、图片批次和 SEO 批次统一使用当前通用 D1/CMS API；按日期拆分的一次性入口已经移除，禁止重新创建。
- 一次性 LEYA 内容 seed 已关闭并从生产入口移除；后续内容必须通过现行后台模块逐项审核后进入 D1。
- 内容写入完成后由正常的 LEYA 发布工作流重新构建，使静态发布元数据与 D1 发布版本保持一致。
- 媒体后台上传会先在浏览器压缩 WebP，再进入 R2；后台内容保存沿用 D1 + publish revision 的轻量流程。
- 任何脚本不得直接修改 `dist/`、线上 HTML 或 R2 缓存来替代源模板、D1/CMS 或 R2 正式修改。

`test_repository_hygiene.py` 会阻止已清理的一次性发布入口和日期批次脚本重新进入仓库。若确实需要新能力，先扩展通用入口、字段所有权、幂等条件、回滚方式和回归测试，再接入 workflow。


