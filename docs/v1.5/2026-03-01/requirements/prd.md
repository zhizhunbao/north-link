# North Link V1.5 — 产品需求文档 (PRD)

## 文档信息

| 项目 | 值         |
| ---- | ---------- |
| 版本 | V1.5       |
| 作者 | Alice (PM) |
| 日期 | 2026-03-01 |
| 状态 | Draft      |

---

## 1. 产品概述

North Link V1.5 在 MVP 基础上新增 **AI 对话式数据采集**。用户通过 Chat Box 描述需求，AI 理解意图后按需从 12+ 个平台精准采集数据，在对话中展示结构化结果。感兴趣的商品可"订阅"做定期追踪。

**不做全量定时采集** — 只抓用户明确要求的数据，控制成本。

> 基于 2026-03-01 开源方案调研结果，技术方案已匹配具体开源项目。AI 使用本地大模型（Ollama），LLM 调用零成本。

---

## 2. 用户故事

### Epic 1: AI Chat 对话（核心入口）

#### US-1.1: 对话式数据查询

**作为**跨境电商从业者，**我希望**在 Chat Box 中用自然语言描述我想查的商品，**以便**系统帮我自动从相关平台采集价格。

**验收标准:**

- [ ] Dashboard 提供 Chat Box 入口
- [ ] 支持中英文自然语言输入
- [ ] AI 正确解析意图：目标平台、关键词、筛选条件
- [ ] 显示采集进度（"正在从 Amazon.ca 搜索..."）
- [ ] 结果以结构化形式返回（表格、商品卡片）

#### US-1.2: 上下文对话

**作为**用户，**我希望**在同一对话中追问或调整需求，**以便**逐步缩小搜索范围。

**验收标准:**

- [ ] 对话支持上下文（"换个平台试试"、"只看 2000 以下的"）
- [ ] 对话历史保留，可回看之前的会话
- [ ] 每条结果可操作：收藏、订阅追踪、打开链接

#### US-1.3: AI 意图解析

**作为**系统，**我需要**将用户自然语言转化为结构化采集任务，**以便**调用正确的爬虫工具。

**支持的意图类型:**

| 意图             | 触发示例                     | 系统动作                    |
| ---------------- | ---------------------------- | --------------------------- |
| `price_search`   | "查一下 XX 在 Amazon 的价格" | 指定平台搜索                |
| `price_compare`  | "几个平台比较一下 XX 的价格" | 多平台并行采集 + 对比表格   |
| `profit_calc`    | "这个从 1688 进货利润多少"   | 采集中加两端价格 + 利润计算 |
| `social_search`  | "小红书上大家怎么评价 XX"    | 社交平台关键词搜索          |
| `trend_analysis` | "抖音上最近什么品类最火"     | 社交平台热度分析            |
| `subscribe`      | "帮我盯着这个，降价通知我"   | 创建订阅追踪任务            |
| `xianyu_search`  | "闲鱼上有没有便宜的 XX"      | 闲鱼搜索 + AI 过滤优质商品  |

### Epic 2: 按需数据采集（AI 工具层）

#### US-2.1: 加拿大平台价格采集

**作为**用户，**我希望**通过对话查询加拿大平台商品价格，**以便**了解当地零售行情。

**覆盖平台 & 技术方案:**

| 平台       | 技术方案                                                   | 反爬难度 |
| ---------- | ---------------------------------------------------------- | -------- |
| Amazon.ca  | `amazon-scraper` + Playwright stealth；逆向搜索 API        | ⭐⭐⭐   |
| BestBuy.ca | **官方 Developer API** — 无需爬虫，最快出成果              | ⭐       |
| Walmart.ca | `scrapfly-scrapers` (httpx + parsel)；逆向内嵌 JSON API    | ⭐⭐     |
| Costco.ca  | `costco-monitor` + Playwright stealth；**Akamai 反爬严重** | ⭐⭐⭐⭐ |

**验收标准:**

- [ ] 对话中指定平台或 AI 自动选择平台
- [ ] 采集字段: 商品名、ASIN/SKU、价格(CAD)、原价、库存、评分、链接、图片
- [ ] 结果写入 `price_records` 表，关联到 `product`
- [ ] 新商品自动创建 `product` 记录
- [ ] 单次采集 < 30 秒

#### US-2.2: 中国平台价格采集

**作为**用户，**我希望**通过对话查询中国电商平台的采购价格，**以便**计算跨境利润。

**覆盖平台 & 技术方案:**

| 平台   | 技术方案                                | 反爬难度 |
| ------ | --------------------------------------- | -------- |
| 1688   | `Alibaba-CLI-Scraper` + Apify Actors    | ⭐⭐     |
| 淘宝   | `taobao_mcp` / `InfoSpider`；需登录态   | ⭐⭐⭐⭐ |
| 京东   | `PriceDive` (覆盖京东+淘宝+拼多多)      | ⭐⭐     |
| 拼多多 | `pinduoduo-scraper-example` / PriceDive | ⭐⭐⭐   |

**验收标准:**

- [ ] 采集字段: 商品名、商品 ID、价格(CNY)、批发价/起批量(1688)、销量、链接
- [ ] 自动中加价格对比（如用户请求）
- [ ] 自动利润率计算（含汇率转换）
- [ ] 数据入库

#### US-2.3: 社交平台数据查询

**作为**用户，**我希望**通过对话查询社交平台上的商品口碑和趋势，**以便**判断选品方向。

**覆盖平台 & 技术方案:**

| 平台                                | 技术方案                             | 反爬难度 |
| ----------------------------------- | ------------------------------------ | -------- |
| 小红书·抖音·快手·B站·微博·知乎·贴吧 | `NanmiCoder/MediaCrawler` (34k+ ⭐)  | ⭐⭐     |
| 闲鱼                                | `ai-goofish-monitor` (Playwright+AI) | ⭐⭐⭐   |

**验收标准:**

- [ ] 支持关键词搜索社交平台
- [ ] 返回笔记/视频摘要、互动数据（点赞/评论/分享）
- [ ] 闲鱼搜索含 AI 过滤（筛掉低质量商品）
- [ ] 数据写入 `social_posts` 表

### Epic 3: 订阅追踪（替代全量定时采集）

#### US-3.1: 商品订阅

**作为**用户，**我希望**在对话中订阅感兴趣的商品价格追踪，**以便**在价格变动时收到通知。

**验收标准:**

- [ ] 对话中说"帮我盯着" → 创建订阅
- [ ] 订阅维度: 具体商品 URL 或 关键词 + 平台
- [ ] 订阅频率: 每日 1-2 次（控制成本）
- [ ] 每用户最多 20 个活跃订阅（初期限制）

#### US-3.2: 价格变动通知

**作为**用户，**我希望**在订阅的商品价格变动超过阈值时收到通知，**以便**及时做出采购决策。

**验收标准:**

- [ ] 默认阈值 ±10%，用户可自定义
- [ ] 通知内容: 商品名、平台、旧价格 → 新价格、变动幅度
- [ ] 通知展示在 Dashboard 和对话中
- [ ] 支持标记通知为已读

#### US-3.3: 订阅管理

**作为**用户，**我希望**管理我的订阅列表，**以便**控制追踪范围。

**验收标准:**

- [ ] 订阅列表页面：查看所有订阅
- [ ] 支持暂停/恢复/删除订阅
- [ ] 显示每个订阅的最新价格和历史趋势

### Epic 4: 采集成本控制

#### US-4.1: 使用量监控

**作为**管理员，**我希望**看到采集系统的使用量，**以便**控制成本。

**验收标准:**

- [ ] Dashboard 展示: 今日采集次数、本月累计、按平台分布
- [ ] 每日采集次数上限（可配置，初始 100 次/天）
- [ ] 超限提醒
- [ ] 采集结果缓存：相同查询 1 小时内不重复采集

---

## 3. 功能模块交互

### 3.1 核心流程

```
用户 Chat Box 输入
  → LLM 意图解析 (Function Calling)
  → 确定: 平台 + 关键词 + 筛选条件
  → 调用对应爬虫 Tool
  → 数据清洗 + 入库
  → LLM 结果总结 + 结构化展示
  → 用户操作: 收藏 / 订阅 / 追问
```

### 3.2 页面交互

| 页面      | 内容                                             |
| --------- | ------------------------------------------------ |
| Dashboard | Chat Box 入口 + 订阅商品价格变动通知             |
| Chat 页面 | AI 对话界面（全屏或侧边栏），含富文本结果展示    |
| 订阅管理  | 订阅列表、状态、最新价格、暂停/删除              |
| 比价中心  | 复用 MVP 页面，新增"数据来源"标签、"AI 查询"入口 |
| 系统设置  | 新增"AI 配置"Tab（LLM 选择、采集上限）           |

---

## 4. API 设计概要

### 4.1 新增 API

| Method | Path                              | 描述                  |
| ------ | --------------------------------- | --------------------- |
| POST   | `/api/v1/chat/message`            | 发送对话消息          |
| GET    | `/api/v1/chat/sessions`           | 获取对话会话列表      |
| GET    | `/api/v1/chat/sessions/{id}`      | 获取单个会话对话历史  |
| DELETE | `/api/v1/chat/sessions/{id}`      | 删除会话              |
| POST   | `/api/v1/subscriptions`           | 创建订阅追踪          |
| GET    | `/api/v1/subscriptions`           | 获取订阅列表          |
| PUT    | `/api/v1/subscriptions/{id}`      | 更新订阅（暂停/恢复） |
| DELETE | `/api/v1/subscriptions/{id}`      | 删除订阅              |
| GET    | `/api/v1/notifications`           | 获取通知列表          |
| PUT    | `/api/v1/notifications/{id}/read` | 标记通知已读          |
| GET    | `/api/v1/scraper/usage`           | 获取采集使用量统计    |

### 4.2 复用 API（无需修改）

| Method | Path                            | 描述                                   |
| ------ | ------------------------------- | -------------------------------------- |
| POST   | `/api/v1/products`              | 爬虫自动创建商品（内部调用）           |
| POST   | `/api/v1/products/prices`       | 爬虫写入价格记录（内部调用）           |
| GET    | `/api/v1/recommendations/daily` | Dashboard 推荐（数据更丰富后自动生效） |

---

## 5. 数据模型变更

### 5.1 新增表

#### `chat_sessions` — 对话会话

| 列名       | 类型         | 说明                    |
| ---------- | ------------ | ----------------------- |
| id         | UUID         | 主键                    |
| user_id    | UUID         | FK→users                |
| title      | VARCHAR(200) | 会话标题（AI 自动生成） |
| created_at | TIMESTAMPTZ  | 创建时间                |
| updated_at | TIMESTAMPTZ  | 更新时间                |

#### `chat_messages` — 对话消息

| 列名       | 类型        | 说明                           |
| ---------- | ----------- | ------------------------------ |
| id         | UUID        | 主键                           |
| session_id | UUID        | FK→chat_sessions               |
| role       | VARCHAR(20) | user / assistant / system      |
| content    | TEXT        | 消息内容                       |
| metadata   | JSONB       | 结构化数据（采集结果、图表等） |
| created_at | TIMESTAMPTZ | 创建时间                       |

#### `subscriptions` — 订阅追踪

| 列名            | 类型          | 说明                      |
| --------------- | ------------- | ------------------------- |
| id              | UUID          | 主键                      |
| user_id         | UUID          | FK→users                  |
| platform        | VARCHAR(20)   | 平台标识                  |
| target_type     | VARCHAR(20)   | url / keyword             |
| target_value    | TEXT          | 具体 URL 或关键词         |
| threshold       | NUMERIC(5,2)  | 变动通知阈值（默认 10%）  |
| status          | VARCHAR(20)   | active / paused / expired |
| last_price      | NUMERIC(12,2) | 最近一次采集价格          |
| last_checked_at | TIMESTAMPTZ   | 最近一次采集时间          |
| created_at      | TIMESTAMPTZ   | 创建时间                  |
| updated_at      | TIMESTAMPTZ   | 更新时间                  |

#### `scraper_tasks` — 采集任务记录

| 列名          | 类型         | 说明                                 |
| ------------- | ------------ | ------------------------------------ |
| id            | UUID         | 主键                                 |
| trigger_type  | VARCHAR(20)  | chat / subscription / manual         |
| trigger_id    | UUID         | 关联的会话 ID 或订阅 ID              |
| platform      | VARCHAR(20)  | 平台标识                             |
| keywords      | VARCHAR(200) | 搜索关键词                           |
| status        | VARCHAR(20)  | pending / running / success / failed |
| items_found   | INTEGER      | 找到的商品数                         |
| error_message | TEXT         | 错误信息                             |
| started_at    | TIMESTAMPTZ  | 开始时间                             |
| completed_at  | TIMESTAMPTZ  | 完成时间                             |
| created_at    | TIMESTAMPTZ  | 创建时间                             |

#### `notifications` — 通知

| 列名       | 类型         | 说明                                 |
| ---------- | ------------ | ------------------------------------ |
| id         | UUID         | 主键                                 |
| user_id    | UUID         | FK→users                             |
| type       | VARCHAR(20)  | price_alert / scraper_error / system |
| title      | VARCHAR(200) | 通知标题                             |
| content    | TEXT         | 通知内容                             |
| metadata   | JSONB        | 扩展数据                             |
| is_read    | BOOLEAN      | 是否已读                             |
| created_at | TIMESTAMPTZ  | 创建时间                             |

#### `social_posts` — 社交平台采集数据

| 列名         | 类型         | 说明                                             |
| ------------ | ------------ | ------------------------------------------------ |
| id           | UUID         | 主键                                             |
| platform     | VARCHAR(20)  | 平台标识 (xiaohongshu, douyin, xianyu, weibo...) |
| post_id      | VARCHAR(100) | 平台原始帖子 ID                                  |
| title        | VARCHAR(500) | 标题                                             |
| content      | TEXT         | 内容摘要                                         |
| author       | VARCHAR(100) | 作者昵称                                         |
| likes        | INTEGER      | 点赞数                                           |
| comments     | INTEGER      | 评论数                                           |
| shares       | INTEGER      | 分享/转发数                                      |
| product_url  | VARCHAR(500) | 关联商品链接（如有）                             |
| post_url     | VARCHAR(500) | 原始帖子链接                                     |
| published_at | TIMESTAMPTZ  | 发布时间                                         |
| scraped_at   | TIMESTAMPTZ  | 采集时间                                         |
| metadata     | JSONB        | 扩展数据（标签、图片等）                         |
| created_at   | TIMESTAMPTZ  | 创建时间                                         |

### 5.2 现有表扩展

#### `price_records` — 新增字段

| 列名            | 类型         | 说明                              |
| --------------- | ------------ | --------------------------------- |
| scraper_task_id | UUID         | FK→scraper_tasks (可选)           |
| image_url       | VARCHAR(500) | 商品主图                          |
| stock_status    | VARCHAR(20)  | in_stock / out_of_stock / limited |
| rating          | NUMERIC(3,1) | 评分                              |
| review_count    | INTEGER      | 评论数                            |

---

## 6. 技术选型

| 组件       | 技术                                                                | 理由                         |
| ---------- | ------------------------------------------------------------------- | ---------------------------- |
| AI/LLM     | **本地大模型**: Ollama + Qwen2.5/Llama3/DeepSeek (Function Calling) | 零成本、隐私安全、无网络依赖 |
| Chat 前端  | React Chat 组件 + Ant Design                                        | 复用现有技术栈               |
| 加拿大电商 | httpx+parsel (Walmart), Playwright stealth (Amazon/Costco)          | 按需调用，不定时全采         |
| BestBuy    | 官方 Developer API                                                  | 最稳定、零反爬               |
| 中国电商   | PriceDive (京东/淘宝/拼多多), Alibaba-CLI-Scraper (1688)            | 按需调用                     |
| 社交平台   | MediaCrawler (7平台), ai-goofish-monitor (闲鱼)                     | 按需调用                     |
| 任务队列   | Celery 5.4+                                                         | 异步执行采集任务，不阻塞对话 |
| 定时调度   | Celery Beat                                                         | 仅用于订阅追踪定时任务       |
| 结果缓存   | Redis (TTL 1h)                                                      | 相同查询不重复采集           |

---

## 7. 风险与缓解

| 风险               | 影响         | 概率 | 缓解措施                                   |
| ------------------ | ------------ | ---- | ------------------------------------------ |
| LLM 意图解析错误   | 采集目标错误 | 中   | 用户确认 + fallback 手动选择               |
| Costco Akamai 反爬 | 采集失败     | 高   | 商业 API 兜底 + 对话中友好提示             |
| 采集成本超预算     | 费用         | 中   | 每日上限 + 结果缓存 + 按平台计费统计       |
| 中国平台需登录     | 无法采集     | 中   | MediaCrawler 登录态缓存 + 提示用户手动刷新 |
| LLM API 不可用     | 对话中断     | 低   | fallback UI (关键词输入 + 平台下拉选择)    |
| 法律合规           | 投诉         | 低   | 仅公开数据 + 按需采集 + 合理频率           |

---

## 8. MVP 注意事项

- Chat + AI + 单平台采集跑通完整链路后再扩展其他平台
- 不做全量定时采集，只有用户"订阅"的商品才做定期追踪
- 初期订阅上限 20 个/用户，观察成本后调整
- 采集结果缓存 1 小时，减少重复请求
- 每日采集次数上限 100 次（可配置）
- LLM 调用成本需计入成本控制
