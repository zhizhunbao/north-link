# North Link 跨境货源通 — 系统架构文档

> 版本: V1.0 | 更新时间: 2026-02-28 | 作者: Bob (System Architect)
>
> 依赖: [需求分析](../requirements/requirements.md) | [PRD](../requirements/prd.md) | [UX 设计](../design/)

---

## 1. 架构概述

### 1.1 设计原则

| 原则                              | 说明                                           | 实践                               |
| --------------------------------- | ---------------------------------------------- | ---------------------------------- |
| **Modular Monolith**              | MVP 阶段选择模块化单体，快速交付               | 内部模块化，外部单一部署单元       |
| **API-First**                     | 前后端分离，所有功能通过 API 暴露              | RESTful API + OpenAPI 文档自动生成 |
| **Convention over Configuration** | 减少样板代码                                   | 统一的项目结构、命名规范           |
| **Data Privacy**                  | 商户信息和订单数据加密存储                     | AES-256 加密敏感字段               |
| **Fail Gracefully**               | 外部依赖（爬虫、汇率 API）不可用时系统仍可运行 | 缓存 + fallback + 手动录入         |
| **Zero Technical Barrier**        | 用户零技术门槛                                 | 全中文、引导式交互、合理默认值     |

### 1.2 架构决策记录 (ADR)

#### ADR-001: Modular Monolith vs Microservices

- **决策**: 选择 Modular Monolith
- **理由**: 团队规模 1-2 人；MVP 阶段需要快速迭代；所有模块共享数据库；运维成本低
- **后续**: V2.0+ 业务量增长后，可按模块边界拆分为微服务

#### ADR-002: Server-Side Rendering vs SPA

- **决策**: SPA (React) + API Server (FastAPI)
- **理由**: 管理后台类系统，无 SEO 需求；前后端完全解耦；独立部署
- **后续**: 如需公开商品页面可增加 SSR 层

#### ADR-003: 数据爬虫策略

- **决策**: MVP 阶段以手动导入/CSV导入为主，爬虫为辅
- **理由**: 爬虫开发成本高、反爬风险大；手动导入快速验证业务模式
- **后续**: V1.5 逐步增加各平台爬虫模块

### 1.3 系统架构图

```mermaid
graph TB
    subgraph Client["客户端"]
        Web["React SPA<br/>Desktop + Mobile 响应式"]
    end

    subgraph Server["应用服务器"]
        API["FastAPI<br/>REST API Gateway"]

        subgraph Modules["业务模块"]
            M1["比价模块<br/>price_comparison"]
            M2["商户模块<br/>merchant"]
            M3["利润计算模块<br/>profit_calculator"]
            M4["物流模块<br/>logistics"]
            M5["订单模块<br/>order"]
            M6["推荐模块<br/>recommendation"]
            M7["系统设置<br/>settings"]
        end

        API --> M1 & M2 & M3 & M4 & M5 & M6 & M7
    end

    subgraph Data["数据层"]
        PG["PostgreSQL<br/>主数据库"]
        Redis["Redis<br/>缓存 + 会话"]
    end

    subgraph External["外部服务"]
        FX["汇率 API<br/>ExchangeRate-API"]
        Scraper["数据采集<br/>Scrapy (后期)"]
    end

    Web -->|HTTPS| API
    Modules --> PG
    Modules --> Redis
    M1 -.->|V1.5| Scraper
    M3 --> FX
```

---

## 2. 技术选型

### 2.1 后端技术栈

| 组件     | 技术选择           | 版本   | 选型理由                                                    |
| -------- | ------------------ | ------ | ----------------------------------------------------------- |
| 语言     | **Python**         | 3.12+  | 开发效率高；数据处理生态强（pandas/scrapy）；中文开发者友好 |
| Web 框架 | **FastAPI**        | 0.115+ | 异步高性能；自动 OpenAPI 文档；Pydantic 数据验证；类型安全  |
| ORM      | **SQLAlchemy 2.0** | 2.0+   | 成熟稳定；支持异步；迁移工具 Alembic                        |
| 任务队列 | **Celery + Redis** | 5.4+   | 定时任务（数据更新）；异步爬虫；报表生成                    |
| 包管理   | **uv**             | latest | 极速依赖解析；替代 pip + venv                               |

### 2.2 前端技术栈

| 组件        | 技术选择                       | 版本   | 选型理由                                  |
| ----------- | ------------------------------ | ------ | ----------------------------------------- |
| 框架        | **React**                      | 19+    | 组件化开发；生态成熟；团队熟悉            |
| 构建工具    | **Vite**                       | 6+     | 极速冷启动；HMR；开箱即用                 |
| 语言        | **TypeScript**                 | 5.5+   | 类型安全；重构信心；IDE 支持              |
| 状态管理    | **Zustand**                    | 5+     | 轻量；无 boilerplate；React 19 兼容       |
| UI 组件库   | **Ant Design 5**               | 5.x    | 全中文文档；企业级组件丰富；表格/表单强大 |
| 路由        | **React Router**               | 7+     | 标准 SPA 路由方案                         |
| HTTP 客户端 | **Axios** + **React Query**    | latest | 请求缓存；自动重试；乐观更新              |
| 图表        | **Recharts**                   | 2+     | React 原生图表；轻量；利润报表展示        |
| CSS         | **CSS Modules** + 设计系统变量 | -      | 与 Ant Design 兼容；设计系统 token 统一   |

### 2.3 数据库

| 组件     | 技术选择          | 选型理由                                                                   |
| -------- | ----------------- | -------------------------------------------------------------------------- |
| 主数据库 | **PostgreSQL 16** | ACID 事务；JSON 支持（商品灵活属性）；全文搜索；关系数据（商户-订单-商品） |
| 缓存     | **Redis 7**       | 汇率缓存；会话管理；每日推荐缓存；Celery 消息 broker                       |
| 数据迁移 | **Alembic**       | SQLAlchemy 官方迁移工具；版本化管理                                        |

### 2.4 基础设施

| 组件     | 技术选择                    | 选型理由                                |
| -------- | --------------------------- | --------------------------------------- |
| 容器化   | **Docker + Docker Compose** | 本地开发一致性；一键启动全栈            |
| 部署平台 | **Render.com** (MVP)        | 免费层可用；PostgreSQL 托管；自动部署   |
| CI/CD    | **GitHub Actions**          | 免费；与 GitHub 深度集成；自动测试+部署 |
| 反向代理 | **Caddy** (可选)            | 自动 HTTPS；零配置                      |
| 监控     | **Sentry** (MVP)            | 免费层；错误追踪；性能监控              |

---

## 3. 系统组件

### 3.1 后端模块划分

```
backend/
├── app/
│   ├── main.py                    # FastAPI 应用入口
│   ├── config.py                  # 配置管理 (env vars)
│   ├── database.py                # 数据库连接
│   │
│   ├── modules/                   # 业务模块 (Modular Monolith)
│   │   ├── price/                 # 模块1: 比价中心
│   │   │   ├── __init__.py
│   │   │   ├── models.py          # SQLAlchemy 数据模型
│   │   │   ├── schemas.py         # Pydantic request/response 模型
│   │   │   ├── router.py          # API 路由
│   │   │   ├── service.py         # 业务逻辑
│   │   │   └── repository.py      # 数据访问层
│   │   │
│   │   ├── merchant/              # 模块2: 商户管理
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   └── repository.py
│   │   │
│   │   ├── profit/                # 模块3: 利润计算器
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── router.py
│   │   │   ├── service.py         # 核心利润计算逻辑
│   │   │   └── calculator.py      # 利润公式引擎
│   │   │
│   │   ├── logistics/             # 模块4: 物流管理
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   └── repository.py
│   │   │
│   │   ├── order/                 # 模块5: 订单管理 (P1)
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   └── repository.py
│   │   │
│   │   ├── recommendation/        # 模块6: 每日推荐
│   │   │   ├── schemas.py
│   │   │   ├── router.py
│   │   │   └── service.py         # TOP5 推荐算法
│   │   │
│   │   └── settings/              # 模块7: 系统设置
│   │       ├── models.py
│   │       ├── schemas.py
│   │       ├── router.py
│   │       └── service.py
│   │
│   ├── core/                      # 共享核心层
│   │   ├── auth.py                # JWT 认证
│   │   ├── exceptions.py          # 统一异常处理
│   │   ├── middleware.py           # CORS / 日志 / 错误处理
│   │   ├── pagination.py          # 统一分页
│   │   └── exchange_rate.py       # 汇率服务 (CAD ↔ CNY)
│   │
│   └── tasks/                     # Celery 异步任务
│       ├── __init__.py
│       ├── celery_app.py          # Celery 配置
│       ├── price_update.py        # 价格数据更新任务
│       └── daily_recommendation.py # 每日推荐生成任务
│
├── alembic/                       # 数据库迁移
│   └── versions/
├── tests/                         # 测试
│   ├── conftest.py
│   └── modules/
│       ├── test_price.py
│       ├── test_merchant.py
│       ├── test_profit.py
│       └── ...
├── pyproject.toml                 # 项目配置 (uv)
└── Dockerfile
```

### 3.2 前端模块划分

```
frontend/
├── src/
│   ├── main.tsx                   # React 入口
│   ├── App.tsx                    # 路由配置
│   ├── index.css                  # 全局样式 + 设计系统 tokens
│   │
│   ├── components/                # 通用组件
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx      # 主布局 (侧边栏 + 内容区)
│   │   │   ├── Sidebar.tsx        # 侧边导航
│   │   │   └── MobileNav.tsx      # 移动端底部导航
│   │   ├── common/
│   │   │   ├── ProfitBadge.tsx    # 利润标记 (绿/黄/红)
│   │   │   ├── PriceDisplay.tsx   # 价格展示 (CAD/CNY)
│   │   │   ├── RiskLevel.tsx      # 风险等级指示器
│   │   │   └── EmptyState.tsx     # 空状态组件
│   │   └── charts/
│   │       ├── ProfitChart.tsx    # 利润趋势图
│   │       └── CategoryPie.tsx    # 品类占比饼图
│   │
│   ├── pages/                     # 页面
│   │   ├── Dashboard/             # 仪表盘
│   │   │   ├── Dashboard.tsx
│   │   │   ├── TopRecommendations.tsx
│   │   │   ├── StatsCards.tsx
│   │   │   └── RecentActivity.tsx
│   │   ├── PriceCenter/           # 比价中心
│   │   │   ├── PriceList.tsx
│   │   │   ├── ProductDetail.tsx
│   │   │   ├── PriceFilters.tsx
│   │   │   └── ManualPriceEntry.tsx
│   │   ├── Merchants/             # 商户管理
│   │   │   ├── MerchantList.tsx
│   │   │   ├── MerchantDetail.tsx
│   │   │   └── MerchantForm.tsx
│   │   ├── Logistics/             # 物流管理
│   │   │   ├── FreightList.tsx
│   │   │   ├── ShipOrder.tsx
│   │   │   └── Tracking.tsx
│   │   ├── Orders/                # 订单管理 (P1)
│   │   ├── Reports/               # 报表中心 (P1)
│   │   └── Settings/              # 系统设置 (P1)
│   │
│   ├── hooks/                     # 自定义 Hooks
│   │   ├── useProducts.ts         # 商品数据 Hook
│   │   ├── useMerchants.ts        # 商户数据 Hook
│   │   ├── useProfitCalc.ts       # 利润计算 Hook
│   │   └── useExchangeRate.ts     # 汇率 Hook
│   │
│   ├── stores/                    # Zustand 状态管理
│   │   ├── useAppStore.ts         # 全局状态 (主题、侧边栏)
│   │   └── useFilterStore.ts      # 筛选条件状态
│   │
│   ├── services/                  # API 服务层
│   │   ├── api.ts                 # Axios 实例 + 拦截器
│   │   ├── priceService.ts
│   │   ├── merchantService.ts
│   │   ├── profitService.ts
│   │   ├── logisticsService.ts
│   │   └── settingsService.ts
│   │
│   ├── types/                     # TypeScript 类型定义
│   │   ├── product.ts
│   │   ├── merchant.ts
│   │   ├── logistics.ts
│   │   ├── order.ts
│   │   └── common.ts
│   │
│   └── utils/                     # 工具函数
│       ├── format.ts              # 价格/日期格式化
│       ├── currency.ts            # 货币换算
│       └── constants.ts           # 常量 (税率默认值等)
│
├── public/
├── package.json
├── tsconfig.json
├── vite.config.ts
└── Dockerfile
```

### 3.3 模块交互图

```mermaid
graph LR
    subgraph Frontend["前端"]
        Dashboard --> PriceCenter
        PriceCenter --> ProductDetail
        ProductDetail --> ProfitCalc["利润计算器"]
        ProductDetail --> MerchantMatch["商户匹配"]
        ProductDetail --> LogisticsRec["物流推荐"]
        MerchantMatch --> ShipOrder["发货下单"]
        LogisticsRec --> ShipOrder
    end

    subgraph API["后端 API"]
        PriceAPI["/api/v1/prices"]
        MerchantAPI["/api/v1/merchants"]
        ProfitAPI["/api/v1/profit"]
        LogisticsAPI["/api/v1/logistics"]
        OrderAPI["/api/v1/orders"]
        RecommendAPI["/api/v1/recommendations"]
        SettingsAPI["/api/v1/settings"]
    end

    Dashboard --> RecommendAPI
    PriceCenter --> PriceAPI
    ProfitCalc --> ProfitAPI
    MerchantMatch --> MerchantAPI
    LogisticsRec --> LogisticsAPI
    ShipOrder --> OrderAPI
```

---

## 4. 数据架构

### 4.1 数据模型概览

```mermaid
erDiagram
    PRODUCT ||--o{ PRICE_RECORD : has
    PRODUCT ||--o{ PRODUCT_FAVORITE : has
    PRODUCT }o--|| CATEGORY : belongs_to
    MERCHANT ||--o{ MERCHANT_QUOTE : gives
    MERCHANT }o--|| MERCHANT_CATEGORY : belongs_to
    FREIGHT_AGENT ||--o{ FREIGHT_QUOTE : offers
    ORDER ||--|| PRODUCT : contains
    ORDER ||--|| MERCHANT : sells_to
    ORDER ||--o| SHIPMENT : ships_via
    SHIPMENT ||--|| FREIGHT_AGENT : handled_by
    SHIPMENT ||--o{ TRACKING_EVENT : tracks

    PRODUCT {
        uuid id PK
        string name
        string sku
        uuid category_id FK
        string brand
        string condition "new/used/refurbished/clearance"
        jsonb attributes "灵活属性"
        timestamp created_at
    }

    PRICE_RECORD {
        uuid id PK
        uuid product_id FK
        string source "amazon/bestbuy/manual"
        string region "CA/CN"
        decimal price
        string currency "CAD/CNY"
        string price_type "retail/wholesale/buyback"
        string url
        timestamp recorded_at
    }

    CATEGORY {
        uuid id PK
        string name "显卡/硬件/苹果/保健品/母婴/美妆/海鲜/家电"
        decimal default_tariff_rate "默认关税率"
        string icon
    }

    MERCHANT {
        uuid id PK
        string name
        uuid category_id FK
        string contact_name
        string phone
        string wechat
        string address
        string tier "gold/silver/bronze"
        int total_orders
        timestamp created_at
    }

    MERCHANT_QUOTE {
        uuid id PK
        uuid merchant_id FK
        uuid product_id FK
        decimal price
        string currency
        timestamp quoted_at
    }

    FREIGHT_AGENT {
        uuid id PK
        string name
        decimal unit_price "每公斤/每件"
        string price_unit "kg/piece"
        int est_days_min
        int est_days_max
        boolean tax_included
        boolean pickup_service
        string rating "A/B/C"
        string contact
    }

    FREIGHT_QUOTE {
        uuid id PK
        uuid agent_id FK
        uuid category_id FK
        decimal price
        int est_days
        boolean tax_included
        timestamp valid_until
    }

    ORDER {
        uuid id PK
        string order_type "purchase/sale"
        uuid product_id FK
        uuid merchant_id FK
        int quantity
        decimal unit_cost
        string cost_currency
        decimal total_cost
        decimal selling_price
        decimal profit
        decimal profit_rate
        string status "draft/confirmed/shipped/delivered/completed"
        timestamp created_at
    }

    SHIPMENT {
        uuid id PK
        uuid order_id FK
        uuid freight_agent_id FK
        string tracking_number
        decimal shipping_cost
        decimal tariff_cost
        decimal clearance_fee
        string status "pending/picked_up/in_transit/customs/delivering/delivered"
        timestamp shipped_at
        timestamp delivered_at
    }

    TRACKING_EVENT {
        uuid id PK
        uuid shipment_id FK
        string status
        string location
        string description
        timestamp event_at
    }

    PRODUCT_FAVORITE {
        uuid id PK
        uuid user_id FK
        uuid product_id FK
        timestamp created_at
    }

    MERCHANT_CATEGORY {
        uuid id PK
        string name "显卡算力/数码电子/保健品母婴/生鲜海鲜"
        string description
        int sort_order
    }

    EXCHANGE_RATE {
        uuid id PK
        string from_currency
        string to_currency
        decimal rate
        string source "exchangerate-api.com"
        timestamp fetched_at
    }

    SETTINGS {
        uuid id PK
        string key "tariff_rate_electronics/shipping_template/..."
        jsonb value
        string description
        timestamp updated_at
    }

    USER {
        uuid id PK
        string username
        string password_hash
        string role "admin/user"
        boolean is_active
        timestamp created_at
        timestamp last_login
    }
```

### 4.2 数据流

```mermaid
sequenceDiagram
    participant User as 用户
    participant FE as React 前端
    participant API as FastAPI
    participant DB as PostgreSQL
    participant Redis as Redis
    participant FX as 汇率API

    Note over User,FX: 流程: 用户查看商品利润

    User->>FE: 进入比价中心
    FE->>API: GET /api/v1/prices?category=gpu&sort=profit
    API->>Redis: 检查缓存
    alt 缓存命中
        Redis-->>API: 返回缓存数据
    else 缓存未命中
        API->>DB: 查询 CA + CN 价格记录
        DB-->>API: 价格数据
        API->>Redis: 写入缓存 (TTL: 30min)
    end
    API-->>FE: 商品列表 + 价格

    User->>FE: 点击商品查看详情
    FE->>API: GET /api/v1/prices/{id}/detail
    API->>DB: 查询多平台价格
    API->>Redis: 获取最新汇率
    alt 汇率已缓存
        Redis-->>API: CAD/CNY 汇率
    else 汇率过期
        API->>FX: GET latest?base=CAD&symbols=CNY
        FX-->>API: 汇率
        API->>Redis: 缓存汇率 (TTL: 4h)
    end
    API-->>FE: 商品详情 + 多平台价格

    User->>FE: 一键计算利润
    FE->>API: POST /api/v1/profit/calculate
    Note over API: 纯利润 = 国内售价 - 加拿大成本<br/>- 国际运费 - 关税 - 清关费 - 杂费
    API->>DB: 获取税率/运费参数
    API-->>FE: 利润计算结果 + 风险等级 + 推荐商户 + 推荐物流
    FE-->>User: 展示利润面板
```

---

## 5. API 设计

### 5.1 API 规范

| 规范 | 标准                                                        |
| ---- | ----------------------------------------------------------- |
| 风格 | RESTful                                                     |
| 版本 | URL 路径版本 (`/api/v1/`)                                   |
| 认证 | JWT Bearer Token                                            |
| 分页 | `?page=1&page_size=20` → `{ items: [], total: N, page: N }` |
| 排序 | `?sort=profit_rate&order=desc`                              |
| 筛选 | `?category=gpu&condition=new&min_profit=500`                |
| 错误 | `{ "detail": "message", "code": "ERROR_CODE" }`             |
| 日期 | ISO 8601 (`2026-02-28T12:00:00Z`)                           |
| 货币 | `{ "amount": 1599.00, "currency": "CAD" }`                  |

### 5.2 API 列表

#### 比价模块 — `/api/v1/prices`

| 方法   | 路径                   | 描述                                  | 优先级 |
| ------ | ---------------------- | ------------------------------------- | ------ |
| GET    | `/prices`              | 获取商品价格列表 (支持分页/筛选/排序) | P0     |
| GET    | `/prices/{id}`         | 获取商品详情 (含多平台价格)           | P0     |
| POST   | `/prices/manual`       | 手动录入价格                          | P0     |
| PUT    | `/prices/{id}`         | 更新价格记录                          | P0     |
| DELETE | `/prices/{id}`         | 删除价格记录                          | P1     |
| POST   | `/prices/import`       | CSV 批量导入价格                      | P0     |
| GET    | `/prices/{id}/history` | 价格历史曲线                          | P1     |

#### 利润计算模块 — `/api/v1/profit`

| 方法 | 路径                | 描述                             | 优先级 |
| ---- | ------------------- | -------------------------------- | ------ |
| POST | `/profit/calculate` | 计算利润 (输入 CA 成本、CN 售价) | P0     |
| POST | `/profit/batch`     | 批量计算利润                     | P1     |
| GET  | `/profit/params`    | 获取计算参数 (税率/运费模板)     | P0     |
| PUT  | `/profit/params`    | 更新计算参数                     | P0     |

#### 商户模块 — `/api/v1/merchants`

| 方法   | 路径                            | 描述                      | 优先级 |
| ------ | ------------------------------- | ------------------------- | ------ |
| GET    | `/merchants`                    | 商户列表 (支持按品类分组) | P0     |
| POST   | `/merchants`                    | 新增商户                  | P0     |
| GET    | `/merchants/{id}`               | 商户详情 (含报价历史)     | P0     |
| PUT    | `/merchants/{id}`               | 更新商户信息              | P0     |
| DELETE | `/merchants/{id}`               | 删除商户                  | P1     |
| POST   | `/merchants/{id}/quotes`        | 录入商户报价              | P0     |
| GET    | `/merchants/match/{product_id}` | 自动匹配最高报价商户      | P0     |

#### 物流模块 — `/api/v1/logistics`

| 方法 | 路径                                 | 描述                                   | 优先级 |
| ---- | ------------------------------------ | -------------------------------------- | ------ |
| GET  | `/logistics/agents`                  | 货代列表                               | P0     |
| POST | `/logistics/agents`                  | 新增货代                               | P0     |
| PUT  | `/logistics/agents/{id}`             | 更新货代信息                           | P0     |
| POST | `/logistics/recommend`               | 推荐物流方案 (最便宜/最快/包税/批量优) | P0     |
| POST | `/logistics/ship`                    | 一键发货下单                           | P0     |
| GET  | `/logistics/shipments`               | 在途物流列表                           | P0     |
| GET  | `/logistics/shipments/{id}/tracking` | 物流轨迹                               | P0     |

#### 推荐模块 — `/api/v1/recommendations`

| 方法 | 路径                       | 描述                     | 优先级 |
| ---- | -------------------------- | ------------------------ | ------ |
| GET  | `/recommendations/daily`   | 今日 TOP5 最赚钱商品推荐 | P0     |
| GET  | `/recommendations/history` | 历史推荐记录             | P1     |

#### 订单模块 — `/api/v1/orders` (P1)

| 方法 | 路径                  | 描述                 | 优先级 |
| ---- | --------------------- | -------------------- | ------ |
| GET  | `/orders`             | 订单列表 (采购+销售) | P1     |
| POST | `/orders`             | 创建订单             | P1     |
| GET  | `/orders/{id}`        | 订单详情             | P1     |
| PUT  | `/orders/{id}/status` | 更新订单状态         | P1     |
| GET  | `/orders/reports`     | 利润报表 (日/周/月)  | P1     |
| GET  | `/orders/export`      | 导出 Excel/PDF       | P1     |

#### 系统设置 — `/api/v1/settings` (P1)

| 方法 | 路径             | 描述                       | 优先级 |
| ---- | ---------------- | -------------------------- | ------ |
| GET  | `/settings`      | 获取系统设置               | P1     |
| PUT  | `/settings`      | 更新设置 (税率/运费模板等) | P1     |
| GET  | `/exchange-rate` | 获取最新汇率               | P0     |

#### 认证 — `/api/v1/auth`

| 方法 | 路径             | 描述         | 优先级 |
| ---- | ---------------- | ------------ | ------ |
| POST | `/auth/login`    | 登录         | P0     |
| POST | `/auth/register` | 注册         | P1     |
| POST | `/auth/refresh`  | 刷新 Token   | P0     |
| GET  | `/auth/me`       | 当前用户信息 | P0     |

#### 收藏 — `/api/v1/favorites`

| 方法   | 路径                      | 描述     | 优先级 |
| ------ | ------------------------- | -------- | ------ |
| GET    | `/favorites`              | 收藏列表 | P0     |
| POST   | `/favorites/{product_id}` | 收藏商品 | P0     |
| DELETE | `/favorites/{product_id}` | 取消收藏 | P0     |

---

## 6. 安全架构

### 6.1 认证

```
JWT Token Flow:
1. POST /auth/login → { access_token, refresh_token }
2. 请求携带: Authorization: Bearer <access_token>
3. access_token 过期 (30min) → 用 refresh_token 刷新
4. refresh_token 过期 (7d) → 重新登录
```

- MVP 阶段使用简单的用户名/密码登录
- Token 存储在 httpOnly cookie (防 XSS) 或 localStorage

#### 初始管理员创建

首次部署时通过 CLI 命令创建管理员账号：

```bash
# 通过环境变量设定初始管理员
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<强密码>

# 通过 seed 脚本创建
uv run python -m app.scripts.create_admin --username $ADMIN_USERNAME --password $ADMIN_PASSWORD
```

实现方式:

- `app/scripts/create_admin.py` — CLI 命令，检查管理员是否存在，不存在则创建
- 密码使用 bcrypt 哈希存储
- Docker Compose 启动时可通过 `entrypoint` 自动执行 seed
- 生产环境通过 Render.com 的 Pre-Deploy Command 执行

### 6.2 授权

- MVP 阶段：单一管理员角色，无复杂权限
- V2.0 预留 RBAC (Role-Based Access Control) 接口

### 6.3 数据安全

| 安全措施     | 实现                                                                   |
| ------------ | ---------------------------------------------------------------------- |
| 敏感数据加密 | 商户 phone、wechat 字段 AES-256 加密                                   |
| SQL 注入防护 | SQLAlchemy 参数化查询 (ORM 默认)                                       |
| XSS 防护     | React 默认转义 + CSP headers                                           |
| CORS         | FastAPI CORSMiddleware (限定前端域名)                                  |
| HTTPS        | Caddy 自动证书 / Render 自带                                           |
| 速率限制     | FastAPI Limiter (100 req/min)                                          |
| 环境变量     | 密钥通过 `.env` 管理，不提交到 Git                                     |
| 密钥管理     | AES 密钥存于环境变量 `ENCRYPTION_KEY`，生产环境通过 Render Secret 管理 |

需加密的具体字段:

- `MERCHANT.phone` — 商户手机号
- `MERCHANT.wechat` — 商户微信号
- `MERCHANT.address` — 商户地址
- `USER.password_hash` — 密码 (bcrypt，非 AES)

---

## 7. 部署架构

### 7.1 环境

| 环境           | 用途 | 部署方式                                     |
| -------------- | ---- | -------------------------------------------- |
| **local**      | 开发 | Docker Compose (PG + Redis + API + Frontend) |
| **staging**    | 测试 | Render.com Preview Environment               |
| **production** | 生产 | Render.com Web Service + PostgreSQL + Redis  |

### 7.2 Docker Compose (本地开发)

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: northlink
      POSTGRES_USER: northlink
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  api:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql+asyncpg://northlink:${DB_PASSWORD}@db:5432/northlink
      REDIS_URL: redis://redis:6379
      JWT_SECRET: ${JWT_SECRET}
      EXCHANGE_RATE_API_KEY: ${EXCHANGE_RATE_API_KEY}
    depends_on: [db, redis]

  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      VITE_API_URL: http://localhost:8000

volumes:
  pgdata:
```

### 7.3 CI/CD 流程

```mermaid
graph LR
    Push["Git Push"] --> GHA["GitHub Actions"]
    GHA --> Lint["Lint<br/>ruff + eslint"]
    Lint --> Test["Test<br/>pytest + vitest"]
    Test --> Build["Build<br/>Docker Images"]
    Build --> Deploy["Deploy to<br/>Render.com"]
```

---

## 8. 日志与可观测性

### 8.1 日志方案

| 组件     | 技术选择               | 说明                                             |
| -------- | ---------------------- | ------------------------------------------------ |
| 日志库   | **structlog**          | 结构化 JSON 日志；上下文绑定；开发时人类友好格式 |
| 错误追踪 | **Sentry**             | 自动捕获未处理异常；性能追踪；Release 追踪       |
| 请求日志 | **FastAPI Middleware** | 每个请求记录 method/path/status/duration         |

### 8.2 日志级别规范

| 级别    | 用途               | 示例                                  |
| ------- | ------------------ | ------------------------------------- |
| ERROR   | 需要立即关注的错误 | 数据库连接失败、汇率 API 不可用       |
| WARNING | 非致命但异常的情况 | 汇率缓存过期使用 fallback、爬虫被反爬 |
| INFO    | 关键业务事件       | 用户登录、订单创建、发货下单          |
| DEBUG   | 开发调试信息       | SQL 查询、利润计算明细（仅开发环境）  |

### 8.3 日志格式

```json
{
  "timestamp": "2026-02-28T12:00:00Z",
  "level": "INFO",
  "event": "profit_calculated",
  "module": "profit",
  "product_id": "uuid",
  "profit_rate": 0.38,
  "risk_level": "low",
  "duration_ms": 120,
  "request_id": "uuid"
}
```

### 8.4 监控与告警

| 指标             | 阈值             | 告警方式     |
| ---------------- | ---------------- | ------------ |
| API 5xx 错误率   | > 1% 持续 5 分钟 | Sentry Alert |
| API 响应时间 P95 | > 3s 持续 5 分钟 | Sentry Alert |
| 汇率 API 失败    | 连续 3 次失败    | Sentry Alert |
| Celery 任务失败  | 任意失败         | Sentry Alert |

> MVP 阶段使用 Sentry 免费层即可覆盖错误追踪 + 性能监控 + 告警。V2.0 可考虑迁移到 Grafana + Prometheus。

---

## 9. 扩展性考虑

### 9.1 V1.0 → V1.5 扩展计划

| 扩展点   | 当前 (V1.0)           | 未来 (V1.5+)          |
| -------- | --------------------- | --------------------- |
| 数据来源 | 手动录入 + CSV导入    | Scrapy 爬虫自动采集   |
| 品类     | 配置化（开始 1-2 个） | 用户自定义品类        |
| 跑腿系统 | 不涉及                | 增加任务派发 + 跑腿端 |
| 通知     | Toast 页面通知        | 微信推送 / Email 通知 |
| 多语言   | 纯中文                | 中文 + 英文           |

### 9.2 模块化拆分路径 (V2.0+)

```
Modular Monolith → 按模块边界拆分

可优先拆分的模块:
1. 爬虫服务 (高 CPU，独立扩缩)
2. 推荐引擎 (计算密集型)
3. 物流跟踪 (独立数据源)
```

### 9.3 性能预估

| 指标         | 目标       | 实现方式                      |
| ------------ | ---------- | ----------------------------- |
| 页面加载     | < 2s       | 前端代码分割 + CDN 静态资源   |
| 利润计算     | < 3s       | 纯计算 + Redis 缓存汇率       |
| 商品列表     | < 1s       | PostgreSQL 索引 + Redis 缓存  |
| 每日数据更新 | 4-6 次     | Celery 定时任务               |
| 并发用户     | MVP: 10-50 | 单实例 FastAPI + asyncio 足够 |

---

## 附录 A: 关键环境变量

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/northlink

# Redis
REDIS_URL=redis://localhost:6379

# Auth
JWT_SECRET=<random-256-bit-key>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Exchange Rate
EXCHANGE_RATE_API_KEY=<api-key>

# App
APP_ENV=development  # development | staging | production
APP_DEBUG=true
CORS_ORIGINS=http://localhost:3000
```
