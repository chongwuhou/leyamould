# XUYI Drinkware — B2B Static Frontend

XUYI 是由 Cloudflare Pages 静态构建交付、由 D1/CMS 管理业务内容、由 R2 管理媒体资源的多语言 B2B 水杯网站。

## 唯一操作入口

READ BEFORE EVERY TASK: 先阅读 AGENTS.md、PROJECT_CHANGE_POLICY.md 和项目圣经，再按统一执行手册操作。

- [AGENTS.md](AGENTS.md)：强制边界、费用/额度禁令和安全要求。
- [PROJECT_CHANGE_POLICY.md](PROJECT_CHANGE_POLICY.md)：源代码、D1、R2、构建和发布边界。
- [XUYI 网站统一执行手册](docs/XUYI_OPERATIONAL_RUNBOOK_ZH.md)：人工后台与 AI/API 的统一流程。
- [仓库维护与真源地图](docs/REPOSITORY_MAINTENANCE.md)：目录职责、清理规则和验收证据。
- [项目圣经索引](项目圣经/目录.md)：架构、发布、内容、翻译和回滚规则。

## 真源与职责

- 产品、Blog、评价、翻译、SEO、发布状态和语言配置：Cloudflare D1/CMS。
- 图片与媒体对象：Cloudflare R2；引用、ALT、语言和审核关系由 D1/CMS 管理。
- 页面结构、共享组件和样式：templates/site/、根目录渲染模块和受控 CSS/JS。
- 发布状态：GitHub Actions、生产 build-meta.json、D1 publish revision 和线上回读。
- 静态 HTML 是构建产物，不是业务数据源；禁止直接修改 dist/、线上 HTML 或 Pages 成品。

## 技术与运行

- GitHub → Cloudflare Pages：静态 HTML/CSS/JS。
- Cloudflare Pages Functions：Admin/API、D1/R2 访问、询盘和显式动态备用路由。
- R2 绑定：XUYI_ASSETS；D1 绑定：XUYI_DB；KV 仅用于受控站点设置。
- 本地构建入口：python scripts/build_release.py。
- 本地检查入口：python scripts/preflight.py、python scripts/test_repository_hygiene.py、python scripts/test_release.py。

## 内容维护

日常发布只能使用通用 D1/CMS API 或正式后台；文章、翻译、产品、评价和图片必须先写入正式源，再构建、部署和线上核验。目标语种、产品数量、分类、路由、分页和公开状态始终从 D1/config 读取，仓库不保留日期批次副本或固定数量说明。

## 当前边界

站点提供产品目录、OEM/ODM、制造、质量控制、物流、Blog、FAQ、联系和隐私页面；没有结账功能。产品事实、容量、材质、认证、MOQ、交期和客户案例只能使用已核实来源。

任何历史批次、临时排查或过程性思考都不属于运行入口。需要判断当前状态时，读取 D1/CMS、R2、配置、CI、build-meta 和线上页面。
