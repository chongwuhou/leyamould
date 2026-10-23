# 用 ChatGPT 更新旭一水杯网站：换电脑 / 让同事接手（简单版）

> **一句话：** AI 不是直接登录服务器改网页。AI 在获得你的授权后修改 GitHub 的**正式源代码或已审核数据**，GitHub Actions 自动检查并发布到 Cloudflare；需要时，再通过受限接口写入 D1 数据库。**换电脑通常只需登录账号；换人必须单独授权。**
>
> 本文只讲已经存在的 XUYI 项目，不教人从零搭网站，也不要求上传任何密钥。更新日期：2026-10-23。

## 1. 你之前做对了什么？

实际已经具备的四件事：

1. **有私有 GitHub 仓库**：[`chongwuhou/xuyi-drinkware-site`](https://github.com/chongwuhou/xuyi-drinkware-site)，正式分支是 `main`。
2. **在 ChatGPT 中连接/授权了 GitHub 和 localGPT**：AI 因此能访问已获许可的仓库，以及已连接电脑上的 WebCodex 本地项目。两者用途不同，**不一定每个任务都需要本地电脑**。
3. **你把发布流程配置在 GitHub Actions**：仓库内有 `.github/workflows/publish-xuyi.yml`；构建通过后部署到 Cloudflare Pages 项目 `xuyi-drinkware-site`，域名是 https://xuyibottles.com/。与 Cloudflare 交互所需的 `CLOUDFLARE_API_TOKEN` 已由仓库的 Actions Secret 提供，**不用给 AI、同事或新电脑复制明文**。
4. **网站已经连接 Cloudflare D1/CMS**：正式博客、翻译、评价由有权限的后台与受限发布接口管理，页面由共享模板重新生成；产品图片等已有资源也有独立存储。**改 GitHub 文件不等于任何内容都能任意写入 D1**，必须走现有审核入口。

流程：**你发指令 → AI 核对规则和数据 → 改 GitHub 正式源 / 经授权的 D1 内容 → GitHub Actions 测试 → Cloudflare Pages → 线上核验**。

## 2. 换一台电脑，还是你本人操作（最省事）

**通常不需要重新部署 Cloudflare、不需要 SSH、不需要搬运 API 密钥。**

1. 新电脑登录**同一个 ChatGPT 账号**。
2. 进入 ChatGPT 的**设置 → Plugins（插件/连接的应用）**，确认 GitHub 连接已授权并可访问上述私有仓库；如有提示，重新连接/授权 GitHub。
3. 新开聊天，告诉 AI 仓库名，并要求先阅读 `AGENTS.md`、`PROJECT_CHANGE_POLICY.md` 和本文档。
4. **先做只读验证**：让 AI 读取仓库最近的提交、GitHub Actions 运行情况；确认访问的正是 XUYI 仓库。
5. 然后再下达具体编辑/发布命令，并检查运行记录和网站实际变化。

**localGPT 何时需要？** 如果任务依赖你原来 Windows 电脑中的工程、未提交的文件或本地运行结果，就需要原电脑的 localGPT/WebCodex 服务在线且已授权，或在新电脑上自行安装/连接兼容的本地项目服务。**本地连接不会仅因复制 GitHub 链接就迁移。** 如果只需访问 GitHub 上的完整源数据，当前授权的 GitHub 连接可以独立工作；是否允许提交取决于它的实际权限。

## 3. 别的同事用他自己的 ChatGPT 账号（安全做法）

**你这个仓库是 private（私有）。别人不知道密码，也不会自动继承你的 AI 权限。**

1. **你先在 GitHub 授权仓库访问**：仓库 `Settings → Collaborators / Manage access`（界面名称可能变化）邀请其自己的 GitHub 账号；根据实际需要只给 **Read**（查阅）或 **Write**（允许提交）权限。不要把你的 GitHub / ChatGPT 登录信息交给同事。
2. **同事自己连接 GitHub**：在他自己的 ChatGPT 账号中连接 GitHub，并授权访问 `chongwuhou/xuyi-drinkware-site`；连接是否有写权限必须以实际工具及 GitHub 授权为准。
3. **让同事用只读任务测试**：读出最近一次成功的 Actions 记录、最新提交、`AGENTS.md` 与本文。
4. **先用小任务试运行**：建议先只改本文档，提交到分支、通过 Pull Request 由你审阅，再合并；不要让新同事第一步就修改生产代码、D1 或 Cloudflare 配置。
5. 审阅通过后，再明确授权他承担内容更新；由 AI 按站点规则操作并给出**文件差异、提交号、Actions 结果与线上链接**。

**不推荐**：共享 ChatGPT 账号、共享个人 GitHub Token、复制 Cloudflare API Token 给员工、让所有人拥有 Cloudflare 管理员权限。对仅写文章的同事，仓库协作权限 + 审核流程通常就够了。

## 4. 复制这几句给新电脑或新同事

### 第一句：只读连接测试

> 请连接我的 GitHub 私有仓库 `chongwuhou/xuyi-drinkware-site`，先阅读 `AGENTS.md`、`PROJECT_CHANGE_POLICY.md`、`docs/AI_COLLABORATION_QUICKSTART_ZH.md`。列出当前 `main` 最新提交与最近一次发布结果。**只读取，不修改、不发布**。如果没有权限，请说明缺少哪种连接或权限。

### 更新博客（必须经发布授权）

> 请在 XUYI 网站新增 3 篇**不重复的海外 B 端采购博客**。沿用项目已验证的编辑规则：五语言（en/es/pt/ru/tr）、真实相关型号内链、人工精选相关阅读、采购清单与 FAQ。只改正式源模板/已审核数据与相应 D1/CMS 发布流程；保留后台人工改动。检查构建和线上结果后给出 3 条正式文章链接、GitHub 提交与 Actions 运行记录。**我授权本次正式发布**。

### 随机评价（每日最多 3 条，不按 Excel 顺序）

> 请按现有 `101-zhenshipingjia.xlsx` 的已核实数据及 D1 发布流水，从**尚未发布**的真实评价里随机选取；**北京时间当天累计最多 3 条**，已满则停止，不要突破限制。不得改写姓名、原文、星级，不得重复型号，也不得覆盖后台评价。完成受限发布、重建及五语言核验，告诉我实际新增几个、哪几个型号。**我授权在现有规则内发布**。

### 修改图片、产品、SEO

> 请先判断**哪一个共享模板、正式源字段或 D1/CMS 字段**拥有这个内容，查明后台是否有人编辑；不得直接改 `dist/` 或线上 HTML，不得编造型号参数或证书。先核对真实来源和影响范围，经我确认的范围内再提交、测试并发布。

## 5. 你怎么知道这次真的改成功了？

不要只听到“完成了”三个字；至少检查：

- **GitHub 提交**：改的是 `chongwuhou/xuyi-drinkware-site` 的正式源，能看到 commit 或 Pull Request，而不是仅写在 AI 对话里。
- **CI 运行**：[Actions 发布记录](https://github.com/chongwuhou/xuyi-drinkware-site/actions/workflows/publish-xuyi.yml) 中的相关运行显示 **Success**；正式构建、测试、Cloudflare 发布和 live verification 成功。**仅修改 `docs/` / `README.md` 通常不会触发生产部署**，这是正常的。
- **正式线上**：打开 https://xuyibottles.com/ 对应页面，并核对 `https://xuyibottles.com/build-meta.json` 的构建 SHA / 发布修订号是否和本次任务匹配。
- **数据库数据**：博客核对 D1 实际插入的文章与翻译；评价核对发布流水、日期和型号，不能仅凭“随机选中”推断已发布。

**注意**：这个站点对特定一次性博客批次使用专门的发布脚本和受限 D1 接口，有些写入还要求**精确的审核提交信息**。普通提交或只触发 Actions 并不一定会入库。让 AI 基于最新仓库检查现有机制，**不要复制过去某天的发布消息冒充今天发布**。

## 6. 遇到问题看这里

| 情况 | 最常见原因 / 怎么办 |
| --- | --- |
| AI 看不到私有仓库 | GitHub 账号没被邀请，或 ChatGPT 的 GitHub 连接没授予该仓库访问权。 |
| AI 能读，不能提交 | GitHub 仓库权限、连接的写入能力或分支规则不允许；请仓库所有者核对。 |
| AI 找不到本地项目 | localGPT/WebCodex 电脑关机、运行器未连接，或新电脑尚未注册本地项目；不涉及本地文件时可先使用 GitHub 连接。 |
| GitHub Actions 没启动 | 本次改动可能只涉及文档，或没有命中工作流的触发路径；查看对应工作流 `on.push.paths`。 |
| Actions 成功，线上没变化 | 可能是只构建未触发对应 D1 入库，或页面版本/缓存还未核实；对照构建 SHA、D1 修订号和目标 URL。 |
| 评价没有新增 3 条 | 当天已满 3 条、该型号已发布、已有后台评价、剩余候选不足等，都应**正常跳过**，绝不能绕过去重和每日上限。 |

## 7. 长期安全约定（请保留）

- 不泄露/转发 `CLOUDFLARE_API_TOKEN`、登录 Cookie、SSH 密码、D1 后台凭据；仓库里的 Actions Secret 由平台保管。
- 不让新人拿你的账号“代登录”；需要收回权限时从 GitHub 仓库协作者和对应 ChatGPT 应用授权中分别撤销。
- 新任务必须先读 `AGENTS.md`、`PROJECT_CHANGE_POLICY.md`；内容来自**共享模板 / 正式数据源 / D1-CMS**，后台改动优先，不直接修改生成的 `dist/`。
- 新员工建议“**先只读 → 再 Pull Request → 审核通过后发布**”。批量生产更新前明确本次授权，避免误发布。
- 如果未来重建仓库或改换 Cloudflare 项目，**要重新检查工作流绑定、Actions Secret、Pages/D1 连接及授权**；单有 GitHub 代码不等于自动继承部署权限。

---

**这份文档对应的是当前已搭好的 XUYI 环境。** 对新电脑和新同事，最快的起点是确认 GitHub 可读、权限准确；除非需要本地文件操作，否则无需先装一套服务器，也无需迁移 D1 或图片。
