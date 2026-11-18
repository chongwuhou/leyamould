# XUYI 网站统一执行手册（人工 + 任意 AI）

版本：2026-11-12  
适用对象：网站负责人、人工后台操作员、ChatGPT、localGPT、其他 AI、脚本、GitHub Actions  
适用范围：产品、产品 SEO、Blog、翻译、评价、图片、普通页面、发布、回滚和迁移

> 这是唯一可执行的日常操作手册。  
> 项目圣经和政策文件负责说明原则；带日期的历史记录只用于追溯，不用于决定今天怎么操作。任何人工或 AI 接到任务，都先读本手册，再读相关专题标准。

## 1. 永久边界

1. Cloudflare D1/CMS 是所有业务内容的唯一真源：产品、产品 SEO、Blog、翻译、评价、页面正文、发布状态和 publish revision。
2. Cloudflare R2 是媒体对象唯一真源：图片、封面、ALT 对应关系、来源和 SHA。
3. GitHub 是模板、组件、构建器、回归测试和流程规则的真源。
4. Cloudflare Pages 的 dist、线上 HTML、浏览器开发者工具和缓存都只是结果，不能作为正式修改位置。
5. 人工可以通过后台操作；AI 可以通过正式 API 操作。AI 发布不打开浏览器。
6. GitHub API 和 Cloudflare 项目 API 可以按项目授权使用；Google API、计费不明确的 API、有限免费额度 API、试用额度 API 禁止使用。
7. 语言数量、产品数量、分类、路由、分页和字段永远从 D1/config 读取。禁止写死“五语”“101 个产品”“505 个产品”或历史批次名称。
8. 后台已有人工值优先。发生冲突时停止并重新读取，不覆盖、不强行重试。
9. AI（包括本项目的 AI 助手）不得自行决定定时发布、重复发布或绕过审核；只有用户明确授权当前任务正式发布时，才可以按本手册调用正式 API。没有明确发布授权，只能做只读检查、生成草稿或给出待审核结果。
10. AI/API 正式发布请求必须带 `X-XUYI-PUBLISH-INTENT: explicit-owner-approval`；缺少该标记时接口拒绝发布。人工后台管理员通过登录会话发布，不需要暴露该标记。

## 2. 所有任务的统一状态

任务只能按下面顺序推进：

只读核对 → 草稿/待审核 → 正式写入 D1/R2 → publish revision → 两次干净构建 → CI 回归 → 部署 → 线上核验 → 交接记录

以下情况只能称为“草稿”或“待审核”：

- 只生成了文字、翻译、图片或 JSON。
- 只保存了后台草稿。
- 只上传了 R2。
- 只完成了 GitHub 提交。
- 只完成了 D1 写入但还没有构建和线上核验。
- CI 仍在运行或有任何关键步骤失败。

只有全部门禁、部署和线上核验通过，才可以称为“已发布”。

## 3. 开工前固定读取顺序

任何人工或 AI 不得跳过：

1. AGENTS.md。
2. PROJECT_CHANGE_POLICY.md。
3. 本手册 docs/XUYI_OPERATIONAL_RUNBOOK_ZH.md。
4. 项目圣经/目录.md。
5. 与任务对应的专题标准：
   - Blog 正文：docs/BLOG_EDITORIAL_PUBLISH_CHECKLIST.md。
   - Blog 图片：docs/BLOG_COVER_VISUAL_STANDARD.md。
   - 产品容量和 oz：项目圣经中的容量标准和 data/retail-oz-size-classes.json。
   - 迁移或部署：项目圣经/系统架构与数据真源.md、项目圣经/部署与回滚.md。
6. 读取 D1 当前快照、语言配置、publish revision、目标记录和字段所有者。

如果当前仓库与任务要求的仓库、Cloudflare 项目或 D1/R2 绑定不一致，立即停止。

## 4. 两种执行模式

### 4.1 人工后台模式

人工使用后台页面完成正式操作：

1. 进入后台，读取当前语言配置、目标记录、状态和 publish revision。
2. 在对应的后台功能中编辑：
   - Blog 内容发布：英文文章、草稿、审核和发布。
   - 内容与多语言：产品、普通页面和 Blog 的多语言 Title、Meta、正文和 ALT。
   - 产品内容/SEO：产品字段、SEO Title、Meta Description 和语言记录。
   - R2 通用媒体库：上传和查看媒体引用。
   - 客户评价：录入来源可核验的真实评价。
   - 自动发布与定时任务：只有用户明确要求定时发布时使用。
3. 先保存草稿，核对事实、语言、结构、图片、内链和 SEO。
4. 审核通过后再保存或发布。
5. 等待标准构建、部署和线上核验。

人工也禁止直接改 dist、线上 HTML、R2 缓存或服务器文件。

### 4.2 AI/API 模式（必须有本次明确发布授权）

AI 不操作浏览器，只做 API 和仓库正式入口。任何 AI 都按同一套接口、字段和门禁执行，不得自行增加“临时发布方法”：

1. 读取 D1/CMS 当前值和字段所有者。
2. 生成草稿、翻译、SEO 建议、图片审核记录和发布 payload。
3. 对照本手册完成本地结构检查。
4. 没有本次明确发布授权：停在只读/草稿/待审核，不写入、不部署。
5. 有明确授权时，图片先写入 R2，再把 R2 路径和 ALT 写入 D1。
6. 使用正式 API 条件写入，并在 AI/API 正式发布请求中带 `X-XUYI-PUBLISH-INTENT: explicit-owner-approval`；等待 GitHub Actions、Cloudflare Pages 和线上核验。

AI 不得把密码、Cookie、Token 写入聊天、GitHub 文件、D1、日志或文章正文。

## 5. 任务与正式入口

| 任务 | 人工入口 | AI/API 正式入口 | 真源 |
| --- | --- | --- | --- |
| 新 Blog 或 Blog 批量发布 | Blog 内容发布 | POST /api/admin/blog-batch | D1 Blog + D1 翻译 + R2 |
| 单篇 Blog 编辑 | Blog 内容发布 | POST /api/admin/blog | D1 Blog |
| Blog 多语言正文 | 内容与多语言 | POST /api/admin/page-translations | D1 translation overrides |
| 产品正文和业务字段 | 产品内容/SEO、内容与多语言 | GET/POST /api/admin/product-content | D1 product content |
| 产品 SEO | 产品内容/SEO | GET/POST /api/admin/product-seo | D1 product SEO |
| 普通页面正文 | 内容与多语言 | GET/POST /api/admin/page-content | D1 page content |
| 多语言普通页面 | 内容与多语言 | GET/POST /api/admin/page-translations | D1 translation overrides |
| 图片 | R2 通用媒体库 | 项目授权的 R2 上传入口 | R2 对象 + D1 引用 |
| 评价 | 客户评价 | 项目现有评价 API/后台入口 | D1 review ledger |
| 模板、组件、回归测试 | GitHub 源码 | GitHub API/PR/提交 | GitHub |

不要自行猜测新接口。若接口名称和当前源码不同，先读取当前 API 文件和后台调用代码。

## 6. D1/R2 写入前检查

任何写入前必须形成一份可恢复快照，至少记录：

- 目标资源、slug、型号、语言和当前状态。
- 当前字段摘要或旧值指纹。
- 当前 D1 publish revision。
- 当前启用并可发布的语言集合。
- 目标 R2 对象、来源和 SHA。
- 本次任务是否允许发布，还是只允许草稿。

条件写入规则：

- 目标不存在：可以按正式入口创建。
- 目标存在且内容完全相同：视为幂等复用，不重复插入。
- 目标存在但内容不同：返回冲突，停止并重新读取；不覆盖人工值。
- 语言未在 D1 language_config 中存在：停止，不伪造语言。
- R2 对象不存在或引用不明确：停止，不写 D1 图片路径。

## 7. Blog 固定标准

每篇新文章必须具备：

- 一个独立的 B2B 长尾采购问题。
- Title、H1、Meta Description、首段和 FAQ 针对同一个搜索意图。
- 7 个实质章节。
- 10 条采购检查清单。
- 4 个 FAQ。
- 正文自然分布 2–5 个真实、不同、已发布的产品详情链接。
- 文末人工选择 2–3 篇已发布相关阅读。
- 真实产品或明确标注的场景示意封面。
- 全部 enabled + publishReady 语言的完整标题、描述、正文和列表卡片。

Blog 批量 API 的请求体必须是：

- posts：每篇包含 slug、完整英文文章对象和发布时间。
- translations：每个已发布目标语言一条，route 使用 /blog/文章slug/，包含 locale、title、description、完整 mainHtml。
- indexCards：每个已发布目标语言一条，包含 slug、locale、完整卡片 HTML。

完整 mainHtml 不是正文片段，也不是 Markdown。必须包含完整页面外壳：

- page-intro 和唯一 H1。
- blog-editorial、封面和 blog-detail__cover。
- blog-editorial__body 和 blog-meta。
- 7 个 blog-section。
- 3 个 blog-editorial__product-link。
- 3 个 blog-related__item。
- 1 个 blog-buyer-matrix。
- 4 个 details。
- 1 个 primary-sources。
- 1 个 blog-editorial__cta。

接口会在 D1 写入前检查这些结构。任何检查失败都停止。

### Blog 发布固定顺序

读取 D1 → 查 slug 冲突 → 写英文草稿 → 完成并审核翻译 → 看图并记录审核 → 上传 R2 → 组装完整 payload → 调用通用 Blog API → 验证 D1 语言和列表顺序 → 两次构建 → 线上核验

禁止：

- 浏览器操作 AI 发布。
- 使用日期专用 Blog 发布脚本或旧批次 endpoint。
- 把正文片段写入 translations.mainHtml。
- 用英文文章冒充译文。
- 用自动推荐模块代替人工相关阅读。
- 用首页、分类页或导航链接冒充产品正文内链。
- 通过修改 dist 解决 Blog 页面问题。

## 8. 产品、SEO、翻译和图片固定标准

### 产品和 SEO

每个型号 × 语言独立维护 Title、H1、Meta Description、OG 和正文。真实容量以 ml 为准；海外 oz 只能使用审核后的 size class/approximate。材质、颜色、认证、MOQ、尺寸、交期和厂家事实没有来源就不写。Tritan、BPA-free 等只能作为可询价定制方向，不能冒充现有 SKU 事实。

### 翻译

目标语言必须来自 D1 language_config。逐语言保存完整 Title、Meta、正文、ALT、按钮、分类、面包屑、内链和 FAQ。不能只翻标题，不能把英文整句保留为翻译，不能使用旧语言路径。Blog 列表必须按照同一份 D1 published 顺序排序。

### 图片

先看完整文章，再看最终图片。记录文章场景、受众、可见物体、版权/来源、SHA 和审核结论。新封面统一 1200×800、3:2、WebP、30–350 KB；先 R2 后 D1；旧对象默认保留，不覆盖、不删除。

### 评价

评价必须有可核验来源、准确 SKU、原文、语言、fingerprint、审核状态和去重结果。AI 可以整理、翻译和筛查，不能生成虚假客户体验。达到每日上限或已发布过时，正常跳过。

## 9. 发布、失败和回滚

| 结果 | 固定处理 |
| --- | --- |
| 401/403/503 | 停止，检查授权、绑定和服务状态，不换入口硬试 |
| 409 | 读取最新 D1，保留人工修改，不覆盖 |
| payload/结构错误 | 修正源数据或请求体，重新做前置检查 |
| R2 上传失败 | 不写 D1 媒体引用 |
| CI 构建失败 | 标记“D1 已写入、线上待发布”，修正式模板/数据后重跑 |
| 部署失败 | 不宣称完成，保留 Git/D1/R2 版本并核对当前线上版本 |
| 线上页面异常 | 记录 URL、HTTP、build SHA 和 revision，按正式源回滚 |

回滚只能使用 D1 历史记录、旧 R2 对象或 Git 正式提交。禁止用旧 dist 覆盖当前线上状态。

## 10. 交接记录模板

每次任务结束必须留下：

- 任务类型和授权范围。
- D1 表/资源/语言/旧值冲突结果。
- R2 对象、来源、SHA 和引用关系。
- GitHub 提交、Actions run 和 Cloudflare Pages 版本。
- publish revision。
- 构建、回归和线上 URL 核验结果。
- 未完成项：草稿、待审核、待构建、待翻译或待回滚。
- 如果没有完整证据，状态写“未完成”，不能写“已发布”。

## 11. 给任何 AI 或新操作员的固定指令

收到任务后，先回答并执行以下 6 项：

1. 我将使用人工后台模式还是 AI/API 模式。
2. 本次业务真源是哪个 D1/CMS 资源，媒体真源是否涉及 R2。
3. 当前语言集合和目标记录从哪里读取。
4. 本次是否允许正式发布。
5. 写入前检查和失败时的停止条件是什么。
6. 完成后要提供哪些 CI、D1、R2 和线上证据。

如果无法回答其中任何一项，只能做只读检查，不能写入、部署或声称完成。


## 12. Bug、返工、回滚与重复修改的防复发门禁（2026-11-18）

最近问题的共同根因不是单次内容错误，而是多个发布入口、旧新 DOM 契约、生成 HTML 精确匹配、缓存版本和并发队列没有形成闭环。所有人工和 AI 任务统一执行以下门禁：

1. 先读本手册、AGENTS.md、PROJECT_CHANGE_POLICY.md 和项目圣经；先确认 D1/CMS、R2、模板和构建器中的字段所有者。
2. 发布前先运行 Pages Functions 语法门禁、源隔离门禁和 D1/CMS 读取检查；语法或权限失败时不得进入完整发布。
3. 只使用一个通用 D1/CMS 发布入口。带日期的一次性脚本只能追溯，不能进入生产 workflow，也不能按提交信息再次触发。
4. 共享渲染器按 D1/CMS 语义字段生成页面；不得用历史 HTML 片段、固定文章、固定语种数、固定产品数或恰好一次字符串替换作为正式逻辑。
5. 共享组件若存在历史结构，必须明确兼容 CSS/模板和回归测试。Blog 卡片图片契约由 scripts/test_blog_card_contract.py 门禁；共享静态资源必须使用内容版本。
6. 同一生产组只保留最新运行；被新提交取代的旧运行自动取消。D1 写入必须条件化、幂等、带 revision，失败不得重复写入。
7. 通过两次干净构建、全部回归测试、部署后代表 URL 回读后，才能报告完成。回滚恢复源代码并重新构建，不用旧 dist、线上 HTML 或缓存文件覆盖 D1/CMS。
8. 每次复盘必须记录触发提交、Actions run/job、根因分类、正式修复位置、回归测试、双构建和线上结果；没有证据就标记待验证。

详细案例和根因映射见 [项目圣经/2026-11-18_近期Bug返工回滚与防复发复盘.md](../项目圣经/2026-11-18_近期Bug返工回滚与防复发复盘.md)。
