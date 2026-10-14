> **历史记录，盎司旧版本已失效：**本文件包含直接取整换算得到的 27/34/41/68 oz 等过时示例，只用于追溯旧操作，不得重新部署或作为当前 SEO 规格来源。**现行规则与全部 23 种市场档位请以 `docs/2026-10-14_RETAIL_OZ_FULL_SITE_AUDIT.md`、`data/retail-oz-size-classes.json` 和 `AGENTS.md` 为准。**

# 2026-10-14：绿色首页、容量盎司搜索词、渐变色型号描述

项目：xuyi-drinkware-site；标准：AGENTS.md、PROJECT_CHANGE_POLICY.md。

## 已落实到源码与正式构建流程

- `scripts/verified_capacity_gradient_en.py` 登记 23 个从原始目录确认容量为 800ml 或 1000ml 的现有型号。仅英文产品详情页面将已有旧版 SEO Title / Description 和旧 H1 更新为 `800ml (27 oz)` 或 `1000ml (34 oz)`，描述同时使用严谨的 `27 fl oz` / `34 fl oz`。URL、SKU 工厂编号、规格表中的原始毫升值与所有图片不变。
- 其中 13 个有真实来源的渐变色型号增加型号特定的英文颜色/样品确认段落；无来源资料的款式不假定渐变色。不改非英语译文为未经审定的英文。
- 对所有已核对的旧标题、旧描述采用精确基线比较，任一字段经后台变更都跳过旧修复；LO 另有四个原始源文案 SHA256，源资料本身被修改亦跳过。每次重新发布由 `scripts/build_release.py` 自动运行，而不是手动改 dist 文件。
- `assets/site.css` 仅为有 `#xuyi-home-banners` 的首页增加绿色主色、绿色渐变 Hero、相关背景和交互强调色；其他页面保留原有配色与布局。五语首页新增文案明确为“BPA-FREE?”、“Ask for material and test verification by model”等材料核对提示，不宣称全站所有水杯已达到 BPA-free。
- 原始资料主要是 PC+PP+ABS、PC+PP 或 PP+PC；没有依据把这些型号直接标为 Tritan、BPA Free / certified、LFGB 或“100°C safe”。如需肯定的 BPA Free 徽标和 Tritan SEO 标题，应先将具体型号的材料牌号、完整接触材料组成和测试/合规证据核对到对应源资料。
- 官方发布流水线添加 `scripts/test_verified_capacity_gradient.py`，验证 23 个型号、13 个渐变色段落、五语首页文案、重复运行幂等和 CMS 覆盖。LO 发布回归校验不再死锁在原始旧 SEO Title/Description，仍须有可用型号、独立元数据、材料和图像。

## 竞品图片/标题边界

用户给出的 Made-in-China 参考页为 BJ-464、600ml、Tritan，并带同款声明；这些是**竞品自己的商品资料**，不能直接套为 XUYI 的材料/认证/真实来源。独立站是否有同款仍需原样品、模具或工厂型号照片交叉确认。该竞品的照片版权/许可未得到证实；目前只作内部外观参考，**未复制或部署任何第三方图片**。可使用经合法授权的供货方源图或自行拍摄同款照片，再按精确 SKU 审核进行替换。

## 本地验证与发布限制

- 两次正式源码发布构建生成 971 文件，五语 755 条公开站点地图 URL、101 型号/语言；曾核验 9 个代表页面全量重建后 SHA256 完全相同。
- 2026-10-14 本轮 52 项 Python CI 发布测试通过；之后强化了 LO 基线和 CMS 颜色覆盖保护，重新运行发布构建和对应的四项关键测试成功。
- 本地 Windows WebCodex 当前无 Node 可执行程序，workflow 的 16 项 JS 测试不能在本机代替 GitHub Actions 证实；正式生产 CI 与 Cloudflare SHA 仍需上线时核验。
- 本次**未提交 GitHub、未部署 Cloudflare、未修改原始 D1 或 R2 媒体**，因此当前的本地实现不等于 xuyibottles.com 线上已经更新。