# Phase Review: PRD (V1.5 — AI 对话驱动按需采集)

**Review 类型**: 文档类
**执行时间**: 2026-03-01T00:42:00
**产出物**: `docs/v1.5/2026-03-01/requirements/prd.md`
**作者**: Alice (Product Manager)
**审查人**: Bob (System Architect)

> ⚠️ 本次为完全重审。文档已从"批量定时采集"根本性重写为"AI 对话驱动按需采集"模式。

---

## 自动检查

- ✅ 文件存在: `docs/v1.5/2026-03-01/requirements/prd.md`
- ✅ 文档非空，内容充实

## 审查清单

### 通用检查 — 完整性

- ✅ 文档信息: 版本、作者、日期、状态齐全
- ✅ 产品概述: "不做全量定时采集"核心原则明确
- ✅ 用户故事: 4 个 Epic, 11 个 US，每个有验收标准
- ✅ Epic 1 (AI Chat): US-1.1 对话查询 + US-1.2 上下文 + US-1.3 意图解析
- ✅ Epic 2 (按需采集): US-2.1 加拿大 + US-2.2 中国电商 + US-2.3 社交平台
- ✅ Epic 3 (订阅追踪): US-3.1 订阅 + US-3.2 通知 + US-3.3 管理
- ✅ Epic 4 (成本控制): US-4.1 使用量监控
- ✅ API 设计: 11 个新 API + 复用已有 API，RESTful 规范
- ✅ 数据模型: 6 张新表 + 现有表扩展，字段定义完整
- ✅ 技术选型: 10 个组件明确列出
- ✅ 风险评估: 6 项风险及缓解措施

### PRD 特定检查 — 技术可实现性

- ✅ Epic 结构合理: Chat > 采集 > 订阅 > 成本控制，优先级递减
- ✅ 意图类型表完整: 7 种意图+触发示例+系统动作，开发可直接映射
- ✅ 数据模型与需求对齐:
  - `chat_sessions` + `chat_messages` 支持 F1 Chat
  - `subscriptions` 支持 F4 订阅追踪
  - `scraper_tasks` 含 `trigger_type` (chat/subscription/manual) 合理
  - `social_posts` 支持 US-2.3 社交数据
  - `notifications` 支持 US-3.2 通知
- ✅ API 覆盖完整: Chat CRUD + 订阅 CRUD + 通知 + 使用量统计
- ✅ 核心流程清晰: Chat→LLM→爬虫→清洗→入库→展示→操作
- ✅ Celery Beat 仅用于订阅追踪（正确限制范围）
- ✅ 结果缓存 Redis TTL 1h（减少重复采集）
- ⚠️ `chat_messages.metadata` JSONB 存储采集结果 — 需定义结构规范（否则前端解析困难）
- ⚠️ `POST /api/v1/chat/message` 应支持 SSE/WebSocket 流式返回（LLM + 采集进度）
- ⚠️ 订阅表 `last_price` 只记录最后价格，缺少价格历史关联（需关联 `price_records`）

## 发现的问题

| #   | 严重度 | 描述                                                         | 位置          | 建议修复                          |
| --- | ------ | ------------------------------------------------------------ | ------------- | --------------------------------- |
| 1   | MEDIUM | chat_messages.metadata 的 JSONB 结构未定义规范，前端解析困难 | §5.1 数据模型 | 架构阶段定义 metadata JSON Schema |
| 2   | MEDIUM | Chat API 应支持流式返回（SSE），否则长时间采集时用户体验差   | §4.1 API      | 架构阶段设计 SSE 方案             |
| 3   | MEDIUM | subscriptions.last_price 与 price_records 缺少显式 FK 关联   | §5.1 数据模型 | database 阶段补充关联关系         |

## 结论 (重审)

- 🟢 **通过** — PRD 内容完整，用户故事可执行，数据模型合理，技术方案可行。3 个 MEDIUM 问题在后续阶段细化，不阻塞当前阶段。

## 统计 (重审)

- 检查项总数: 19
- 通过: 16 | 警告: 3 | 失败: 0

### MEDIUM 问题处理计划

| #   | 问题                 | 处理方式                  |
| --- | -------------------- | ------------------------- |
| 1   | metadata JSON Schema | → `architecture` 阶段定义 |
| 2   | SSE 流式返回         | → `architecture` 阶段设计 |
| 3   | 订阅-价格历史关联    | → `database` 阶段补充     |
