# XUYI 模板优先与全站重建持久性专项复查

日期：2026-10-14

## 用户长期不可违背的要求

所有需要保留的修改，必须修改公共模板、源数据、D1/CMS 感知代码或正式构建流水线。**仅修改 dist/、一次性生成 HTML 或线上页面，不是完成修复。**以后后台更换产品图、Blog 封面、标题、描述、内链和语言内容时，旧批处理不能还原或拒绝用户编辑。后续新增真实型号、文章和语言不得因过往固定计数而误阻断发布。所有变更应能重复运行、不重复插入，经两次完整源码构建及 CI 回归后才考虑上线。

这条规则已写入项目根目录 `AGENTS.md` 和 `PROJECT_CHANGE_POLICY.md`，对 localGPT、Codex、人工作业同等适用；自动化发布的新增场景测试位于 `.github/workflows/publish-xuyi.yml`。

## 复查中确认的同类隐患与已修复项目

| 模块 | 原问题 | 处置 |
| --- | --- | --- |
| `scripts/product_share_images.py` | 页面已有 OG 图会直接报错；按本次新增分享图数检查原有 505 页，后台修改可能阻断全站发布 | 遇到已有 OG/Twitter 图片保留，按实际产品总页数进行最低基线校验，重复运行不插入 |
| `scripts/model_catalog_buyer_comparison.py` | 必须恰好 85 款真实目录型号，新增会阻断；已有比较模块也阻断重复运行 | 改为目录基线不得少于 85；已有 CMS/源码比较块原样保留；新增第 86 款及五语页面模拟通过 |
| `scripts/curated_application_feature_answers.py` | 已有购买决策内容会触发错误，重新运行可能阻断 | 已有块跳过，空缺块按正式源码填充，二次运行无新增 |
| `scripts/test_buyer_journey_and_product_sharing.py` | 要求 OG/Twitter 图片永远和旧 Product JSON-LD 照片完全一样，误拒绝用户社交分享图 | 仅要求图片地址为站内、无重复，并保护产品 JSON-LD 的真实性 |
| `scripts/test_model_catalog_buyer_comparison.py`、`scripts/test_curated_application_feature_answers.py` | 固定模板文案校验会阻挡用户自行修改模块正文 | 原模板继续严格验证；其他 CMS 编辑版本以单块存在、非空与基本安全规则验收 |
| `scripts/test_unique_blog_thumbnails.py` | Blog 数据、重复图计数固定为 16/8，增加文章可能错误失败 | 改为已批准基线不减少，并保持每篇封面不重复及正文/分享元数据一致 |
| `scripts/test_gpt_reviewed_shaker_hd.py` | 要求已审核的产品 OG 图始终等于主图，阻挡 CMS 单独选择分享图 | 放行独立站内分享图，并继续校验 SKU 主图和 Product JSON-LD |
| `README.md` | 旧说明错误表示 G 系列不是已确认工厂型号 | 更新为 G 是工厂型号，但规格仍需核实 |

其他已有的防覆盖模块：`cms_seo_curation_guard.py`（SEO 基线指纹）、`reviewed_media_slot_guard.py`（仅替换旧图、保留后台新图）、`repair_localized_blog_thumbnails.py`（保留新的封面）、`buyer_journey_internal_links.py`（尊重已有链接）、`contextual_share_metadata.py`（保留已有社交预览）。本次既检查了代码逻辑，也复跑了对应既有回归测试。

新增 `scripts/test_source_modules_survive_owner_rebuild.py`：在临时副本中模拟真实后台改写 OG、编辑比较模块、编辑场景内容，恢复缺少的模块，添加第 86 个来源真实目录条目，验证同一处理器连续运行两次仍保留改写。

## 验证结果

- 全站正式源码构建成功：`python -B scripts/build_release.py`，输出 971 文件、101 种目录/参考型号 × 5 语言、755 条站点地图 URL。
- 两次独立全站构建，9 个代表页 HTML SHA256 一致（首页、五语页、产品、Blog、应用/功能页等）。
- GitHub Actions workflow 声明的 51 个 Python 发布测试 **51/51 通过**，包括新增加的 CMS 持久性测试。
- workflow 另有 16 个 Node.js `.mjs` 验证：本机 Windows Runner 找不到 `node` 可执行程序，**这 16 项本次未执行**，不能报告“全部 67 项通过”；GitHub Ubuntu CI 尚需正式运行验证。
- 本次 **未部署、未提交 GitHub、未修改 D1/R2 生产数据或线上 HTML**。本地通过不等于新版本已经上线。

## 仍需持续关注的风险边界

- `apply_gpt_reviewed_shaker_hd.py` 会把审核表中的旧图片 URL 在生成 HTML 中跨位置替换，虽然源不在时不会强制恢复，但如后台将旧图重新指定为其他用途，仍应进一步确认每个模型与主图上下文，不宜无审核进行大范围改写。
- 新增 Blog、产品或第六语言时，应补充有真实对应的源数据、媒体和翻译；原有模板和验证不应假定旧总数永远不变，但业务必填字段、SKU 身份和有效链接仍应严格检查。
- 动态 D1/CMS 真实发布内容与本地 snapshot 在 GitHub CI 的一致性、16 项 Node.js 测试、Cloudflare 线上发布 SHA 仍需发布时核实。
- 不因这次重建而认为 SEO 内容质量、低清产品照片或搜索引擎收录已全部解决。

**以后修改此项目：先读 AGENTS.md，再按 PROJECT_CHANGE_POLICY.md 操作，必要时参阅本文作为历史复查记录。**
