# XUYI 客户评价发布标准

## 唯一来源

仅使用站长提供并已核验的两个私有来源文件及其受控派生 JSON：

- review_import_private/101_verified_buyer_reviews.json
- review_import_private/101_additional_verified_buyer_reviews.json

来源文件、原文、作者、星级、型号、行号和 SHA-256 指纹必须保持一致。私有来源不得进入 dist、R2 公共对象或公开 API。

## 发布规则

- 同一型号可以有多条不同客户评价；同一 source row、fingerprint 或 review UUID 不能重复。
- 永久账本以 review UUID 和 source fingerprint 去重；已发布记录不能因为前台删除而再次使用。
- 每个北京时间日最多新增 3 条，常规任务从未使用的真实评价中随机选择；当天已满或候选不足时正常跳过。
- AI 只能整理、翻译和筛查真实评价，不能生成或改写客户体验。
- 评价写入 D1 后必须回读 inserted 数量、型号、来源行号、指纹、publish revision 和产品页显示结果。

## 运行入口

- 常规入口：scripts/publish_daily_product_reviews.py
- 调度入口：scripts/run_publish_scheduler.py
- 校验：scripts/test_daily_product_reviews.py、scripts/test_daily_product_reviews_api.mjs

所有入口都必须先 dry-run/只读核对，再条件写入 D1；失败或响应不明确时先读取账本，不盲目重复 POST。人工和 AI 遵守同一套上限、去重、审核和回读规则。

## 完成与回滚

评价发布不等于 Blog 或全站发布。只有 D1 写入、产品页显示、构建、CI 和线上核验全部有证据，才报告完成。回滚使用 D1 历史记录和 Git 正式版本，不删除源评价，不修改 dist，不把业务数据回写到代码快照。
