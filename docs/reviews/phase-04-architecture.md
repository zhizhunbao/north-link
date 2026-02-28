# Phase Review: 系统架构 (architecture)

**Review 类型**: 文档类
**执行时间**: 2026-02-28T13:09:12
**产出物**: `docs/architecture/system-architecture.md`
**审查人**: Charlie (Tech Lead)

---

## 自动检查

- ✅ 文件存在: `docs/architecture/system-architecture.md`
- ✅ 文件非空: 31,364 bytes

## 审查清单

### 通用检查 — 完整性

- ✅ 文档包含所有必要章节
- ❌ PRODUCT_FAVORITE 和 MERCHANT_CATEGORY 实体在 ER 关系中出现但未定义字段 — 数据模型不完整
- ⚠️ 推荐模块 (recommendation) 的算法逻辑仅写了"基于利润率 + 风险等级 + 历史成交" — 过于模糊，无法实现
- ⚠️ 无错误码规范 — API 设计中 `"code": "ERROR_CODE"` 只是占位符，未定义具体错误码体系

### 通用检查 — 一致性

- ✅ 7 个模块名称与 PRD 一致
- ❌ roles.yaml 中 Eve (Frontend) 写的是 "Support bilingual (EN/FR)"，但架构文档写的是"纯中文"、PRD 写的也是"全中文界面" — 存在矛盾，需要明确 V1.0 只支持中文
- ⚠️ 数据模型中 CATEGORY 表有 `default_tariff_rate`，同时 SETTINGS 表也存 tariff 配置 — 关税数据存在两处，可能导致数据不一致
- ⚠️ EXCHANGE_RATE 既有数据库表又有 Redis 缓存 — 未说明两者关系（Redis 是 DB 的缓存？还是 Redis 是唯一来源？）

### 通用检查 — 可操作性

- ✅ 目录结构具体到文件级
- ✅ Docker Compose 配置可直接使用
- ❌ 初始管理员账号如何创建？Auth 章节只描述了 JWT 流程，但没有说明首次部署时如何 seed 管理员用户
- ⚠️ Celery 定时任务提到"每日 4-6 次更新"，但无 cron 表达式、无任务失败重试策略

### 通用检查 — 格式规范

- ✅ Markdown 标题层级正确
- ✅ 表格格式完整
- ✅ 代码块标注语言类型

### architecture 特定检查

- ✅ 技术选型有理由说明 — 每个组件都有选型理由列
- ✅ 系统架构图清晰 — Mermaid 图组件 + 关系完整
- ✅ API 接口定义完整 — 40+ 端点，覆盖全部模块
- ✅ 数据流向清晰 — 时序图展示完整流程
- ⚠️ 安全架构偏薄 — 提到了 JWT/CORS/AES-256 但未说明敏感字段哪些需要加密、密钥如何管理（KMS？环境变量轮换？）
- ❌ 无日志与监控策略 — 只提到 Sentry 做错误追踪，但无结构化日志方案（loguru? structlog?）、无 APM、无告警规则
- ⚠️ 部署架构中 staging 环境描述为 "Render.com Preview Environment" 但未说明与 production 的配置差异

## 发现的问题

| #   | 严重度     | 描述                                                             | 位置               | 建议修复                                              |
| --- | ---------- | ---------------------------------------------------------------- | ------------------ | ----------------------------------------------------- |
| 1   | **HIGH**   | PRODUCT_FAVORITE / MERCHANT_CATEGORY 实体未定义字段，ER 图不完整 | 4.1 数据模型       | 补全实体字段定义                                      |
| 2   | **HIGH**   | 初始管理员创建方式未定义 — 首次部署无法登录                      | 6.1 认证           | 增加 seed 脚本或首次注册机制                          |
| 3   | **HIGH**   | 日志与可观测性完全缺失 — 生产环境出问题无法排查                  | 全文               | 增加日志方案章节（structlog + Sentry + 日志级别规范） |
| 4   | **MEDIUM** | 推荐算法描述模糊，无法据此实现                                   | 3.1 recommendation | 补充具体排序公式或至少定义权重                        |
| 5   | **MEDIUM** | 关税数据存在两处 (CATEGORY.default_tariff_rate + SETTINGS)       | 4.1 数据模型       | 明确 SETTINGS 覆盖 CATEGORY 默认值的优先级            |
| 6   | **MEDIUM** | EXCHANGE_RATE 表 vs Redis 缓存职责不清                           | 4.1 + 4.2          | 明确: DB 做历史记录，Redis 做热缓存                   |
| 7   | **MEDIUM** | roles.yaml EN/FR 双语 vs 架构文档纯中文矛盾                      | 全文               | 统一为 V1.0 纯中文，V2.0 再考虑多语言                 |
| 8   | **MEDIUM** | 错误码体系未定义                                                 | 5.1 API 规范       | 定义至少 20 个业务错误码 (PRICE_NOT_FOUND 等)         |
| 9   | **LOW**    | Celery 任务调度细节缺失                                          | 3.1 tasks/         | 定义 cron 表达式 + 重试策略                           |
| 10  | **LOW**    | 敏感字段范围和密钥管理方案未细化                                 | 6.3 数据安全       | 列出需要加密的具体字段                                |

## 结论 (初审)

- 🟡 **条件通过** — 架构整体方向正确，技术选型合理，API 设计完整。但存在 **3 个 HIGH 级问题**需要修复后才能标记完成：
  1. 数据模型补全 (PRODUCT_FAVORITE / MERCHANT_CATEGORY / USER)
  2. 初始管理员创建机制
  3. 日志与可观测性方案

> MEDIUM 级问题建议修复，但可在后续阶段（数据库设计、后端开发）中逐步解决。

## 统计 (初审)

- 检查项总数: 24
- 通过: 14 | 警告: 7 (MEDIUM) | 失败: 3 (HIGH)

---

## 🔄 Re-Review (2026-02-28T13:09:12)

### HIGH 问题修复验证

| #   | 问题           | 修复状态  | 验证                                                                               |
| --- | -------------- | --------- | ---------------------------------------------------------------------------------- |
| 1   | ER 图实体缺失  | ✅ 已修复 | 新增 PRODUCT_FAVORITE (3 字段)、MERCHANT_CATEGORY (4 字段)、USER (7 字段) 实体定义 |
| 2   | 初始管理员创建 | ✅ 已修复 | 新增 CLI seed 脚本方案 + Docker entrypoint + Render Pre-Deploy 说明                |
| 3   | 日志与可观测性 | ✅ 已修复 | 新增第 8 章: structlog 日志库 + 日志级别规范 + JSON 格式 + Sentry 监控告警         |

### 附加改进

- ✅ 敏感字段范围明确化 (phone/wechat/address 加密，password 用 bcrypt)
- ✅ 密钥管理方案 (ENCRYPTION_KEY 环境变量 + Render Secret)
- ✅ EXCHANGE_RATE 增加 source 字段

### MEDIUM 问题处理计划

| #   | 问题             | 处理方式                                |
| --- | ---------------- | --------------------------------------- |
| 4   | 推荐算法模糊     | → 在 stories 阶段细化为具体 User Story  |
| 5   | 关税数据两处     | → 在 database 阶段定义优先级规则        |
| 6   | 汇率 DB vs Redis | → 在 database 阶段明确职责分工          |
| 7   | 多语言矛盾       | → 已确认 V1.0 纯中文，需更新 roles.yaml |
| 8   | 错误码未定义     | → 在 backend 阶段定义                   |
| 9   | Celery 调度细节  | → 在 backend 阶段定义                   |
| 10  | 敏感字段范围     | ✅ 已在本次修复中解决                   |

## Re-Review 结论

- 🟢 **通过** — 3 个 HIGH 问题已全部修复并验证。7 个 MEDIUM 问题已明确处理计划，不阻塞进入下一阶段。

## 最终统计

- 检查项总数: 24
- 通过: 17 | 待后续阶段处理: 6 (MEDIUM) | 已修复: 4 (3 HIGH + 1 LOW)
