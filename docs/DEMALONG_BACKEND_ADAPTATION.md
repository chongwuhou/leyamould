# XUYI 无服务器后台移植记录

## 来源与架构
以同一电脑上 `../demalong-replacement-filters` 为母版，旭一只适配业务和数据库。

| 模块 | 原始来源 | 旭一适配 |
| --- | --- | --- |
| 登录/后台安全 | functions/_shared/admin-security.js, functions/api/admin/auth.js, security.js | 独立 XUYI_DB 和 ADMIN_TOKEN |
| 语言管理 | functions/_shared/site-settings.js, functions/api/admin/site-settings.js, functions/api/site-settings.js | en 默认；es/pt/ru/tr 初始未审核发布 |
| 联系人管理 | 同上 | Janey@xuyibottles.com；+8615395897937 |
| 询盘/SMTP | functions/_shared/forms.js、api/form-submit.js、api/admin/forms.js、api/admin/smtp.js | XUYI_DB，独立 SMTP Secret |
| 翻译 | functions/_shared/translation.js、api/admin/translations.js | 保留原翻译服务提供者和审核工作流；仅把液压滤芯的 catalog_* 数据适配为 xuyi_translation_sources/overrides |
| 后台 UI | Demalong public/admin/index.html 的 6 个面板、admin-console.css、admin-forms.js、admin-site-settings.js | 仅以 xuyi-admin-bridge.js 连接登录与导航 |

## 安全要求
- 永远不要复制德玛隆的 D1 database_id、R2 bucket、ADMIN_TOKEN、SMTP 密码、API Key、联系客户数据到 XUYI。
- XUYI 的 D1 binding 名称为 `XUYI_DB`。确认 Cloudflare Pages 实际绑定指向 **xuyi-drinkware-d1**。
- 初次登录需要为旭一单独设置 `ADMIN_TOKEN` Cloudflare Secret；SMTP 加密需要单独设置 `FORM_SETTINGS_KEY`。
- 公开接口不返回管理员凭证；未认证不能读取/修改后台配置。
- 新语言必须先完成内容翻译和审核、产出真正独立的本地化页面，才允许设 `publishReady=true`。
- 尚未部署、未验证真实邮件投递与真实 D1 写入的情况下，不能声称线上后台已完成验收。

## 初始化产品翻译
运行 `python build.py` 后，再运行 `python scripts/seed-xuyi-translation-sources.py`，输出仅用于旭一 D1 的产品源文本 SQL 到 `_local_ops/sql/xuyi-translation-sources.sql`。审核 SQL 后按 Cloudflare 迁移步骤导入到 **旭一** D1。禁止使用德玛隆数据库。

源语言 en 不自动生成错误翻译页；已审核数据需通过发布流程构建完整的多语言站点，只有审核和测试后才能对外开放语言切换和 SEO hreflang。

## 未完成项
1. 验证线上 Cloudflare Pages 对 XUYI_DB、R2、ADMIN_TOKEN、FORM_SETTINGS_KEY 的绑定，不应假设已经配置。
2. 翻译数据从 D1 导出至静态构建、完整前端页面的多语言发布流程还需接入，不能仅翻译页面标题。
3. 后台多语言设置保存后写入 D1，需配合翻译审核和 Pages 构建才是完整发布。当前没有自动触发部署。
4. 报价 PPT 属内部资料，不能直接公开售价；BPA Free 按型号确认。
