# Code Templates

针对本项目技术栈的代码骨架模板。

## 目录结构

```
templates/
├── backend/
│   ├── __init__.py.template    # 模块导出
│   ├── routes.py.template      # FastAPI 路由
│   ├── service.py.template     # 服务层
│   ├── schemas.py.template     # Pydantic schemas
│   ├── models.py.template      # SQLAlchemy models
│   ├── dependencies.py.template # 依赖注入
│   ├── middleware.py.template  # 中间件
│   ├── streaming.py.template   # SSE 流式响应
│   ├── prompts.py.template     # Prompt 模板管理 (dataclass PromptTemplate)
│   ├── enums.py.template       # StrEnum 枚举定义
│   ├── extractor.py.template   # 数据提取器 (LLM + regex fallback)
│   ├── pipeline.py.template    # 多步骤处理管道
│   ├── chunker.py.template     # 文本分块
│   ├── cache.py.template       # 缓存封装
│   ├── tasks.py.template       # 后台任务
│   ├── rate_limiter.py.template # 速率限制
│   ├── processor.py.template   # 数据处理器模式
│   ├── generator.py.template   # 内容生成器模式
│   └── azure/                  # Azure 服务集成
│       ├── base.py.template    # Protocol + 基类
│       ├── config.py.template  # Pydantic Settings
│       ├── exceptions.py.template
│       ├── openai.py.template
│       ├── search.py.template
│       ├── storage.py.template
│       └── factory.py.template
├── frontend/
│   ├── component.tsx.template  # React 组件
│   ├── hook.ts.template        # 自定义 Hook
│   ├── service.ts.template     # API 服务
│   ├── store.ts.template       # Zustand Store
│   ├── types.ts.template       # TypeScript 类型
│   ├── FileInput.tsx.template  # 文件输入组件
│   ├── DataDisplay.tsx.template # 数据展示组件
│   ├── Modal.tsx.template      # 弹窗组件
│   ├── i18n-en.json.template   # 英文翻译
│   └── i18n-fr.json.template   # 法文翻译
├── tests/
│   ├── conftest.py.template    # Pytest fixtures
│   ├── test_routes.py.template # 路由测试
│   ├── test_service.py.template # 服务测试
│   └── component.test.tsx.template
├── devops/
│   ├── .env.example.template   # 环境变量示例
│   ├── github-ci.yml.template
│   ├── docker-compose.yml.template
│   ├── Dockerfile.backend.template
│   └── Dockerfile.frontend.template
└── docs/
    └── plan.md.template        # 实现计划
```

## 使用方式

### 方式 1: 让 Claude 使用模板

```
请参考 .agent/templates/backend/routes.py.template 创建新端点
```

### 方式 2: 使用脚手架脚本

```bash
python .agent/scripts/scaffold.py feature --name documents
```

## 变量替换

| 变量               | 说明       | 示例       |
| ------------------ | ---------- | ---------- |
| `{{feature_name}}` | 功能名称   | documents  |
| `{{FeatureName}}`  | PascalCase | Documents  |
| `{{date}}`         | 日期       | 2026-02-11 |

---

## 参考模板库 (Reference Template Libraries)

以下是我们研究过的 GitHub 上最有参考价值的模板库，用于指导本项目模板设计。

### 1. ⭐ FastAPI 官方全栈模板 (17k+ stars)

- **仓库**: [fastapi/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template)
- **技术栈**: FastAPI + React + SQLModel + PostgreSQL + Docker + GitHub Actions
- **维护者**: tiangolo (FastAPI 作者)

**关键设计决策**:

- 用 **SQLModel** 统一 ORM model + Pydantic schema（单文件 `models.py`）
- CRUD 用**纯函数**（`def create_user(*, session, data)`），而非 class
- `model_dump(exclude_unset=True)` 做部分更新
- `str | None` 现代类型标注，不用 `Optional`
- `uuid.UUID` 做主键

**我们采纳的**:

- ✅ `str | None` 现代语法
- ✅ `model_dump(exclude_unset=True)` 部分更新
- ❌ 未采用 SQLModel 统一（因为我们用 CosmosDB / JSON 文档模型）
- ❌ 未采用纯函数式 CRUD（我们用 class-based Service，更适合 DI 注入 Azure 服务）

### 2. ⭐ Netflix Dispatch 风格最佳实践 (9k+ stars)

- **仓库**: [zhanymkanov/fastapi-best-practices](https://github.com/zhanymkanov/fastapi-best-practices)
- **启发自**: [Netflix/dispatch](https://github.com/Netflix/dispatch)

**关键设计决策 — 每域一包**:

```
src/
├── auth/
│   ├── router.py        # API 端点
│   ├── schemas.py       # Pydantic 模型
│   ├── models.py        # DB 模型
│   ├── service.py       # 业务逻辑
│   ├── dependencies.py  # 路由依赖
│   ├── constants.py     # 常量和错误码
│   ├── exceptions.py    # 模块级异常
│   ├── config.py        # 环境变量
│   └── utils.py         # 工具函数
├── config.py            # 全局配置
├── models.py            # 全局模型
├── exceptions.py        # 全局异常
└── main.py
```

**我们采纳的**:

- ✅ 每域一包结构（documents/, research/, chat/, evaluation/）
- ✅ `router.py` + `schemas.py` + `service.py` 组合
- ⚠️ 缺少 per-module `constants.py` 和 `exceptions.py`（待补）
- ⚠️ 缺少 per-module `dependencies.py`（当前集中在 `core/dependencies.py`）

### 3. ⭐ Cookiecutter 模板生态

- **仓库**: [cookiecutter/cookiecutter](https://github.com/cookiecutter/cookiecutter)
- **用途**: 通用项目脚手架工具，使用 `{{变量名}}` 语法（和我们一致）

**相关 Cookiecutter 模板**:

- [Buuntu/fastapi-react](https://github.com/Buuntu/fastapi-react) — FastAPI + React + PostgreSQL + Docker
- [equinor/template-fastapi-react](https://github.com/equinor/template-fastapi-react) — Clean Architecture SPA
- [mongodb-labs/full-stack-fastapi-mongodb](https://github.com/mongodb-labs/full-stack-fastapi-mongodb) — FARM Stack (FastAPI + React + MongoDB)

### 4. 🤖 AI Agent 工作流参考

- **MetaGPT**: [geekan/MetaGPT](https://github.com/geekan/MetaGPT) — 多角色 AI 软件公司模拟（我们的 orchestrator 借鉴了这个思路）
- **GPT-Engineer**: [gpt-engineer-org/gpt-engineer](https://github.com/gpt-engineer-org/gpt-engineer) — 自然语言生成代码
- **GitHub Agentic Workflows**: [github/agentic-workflows](https://github.com/github/agentic-workflows) — AI Agent 集成到 GitHub Actions
- **AGENTS.md**: [github/agents-md](https://github.com/github/agents-md) — AI Agent 上下文文件规范

---

## 对比总结

| 维度     | FastAPI 官方  | Netflix 风格    | 我们的项目       | 评估                |
| -------- | ------------- | --------------- | ---------------- | ------------------- |
| 模块化   | 扁平单文件    | ✅ 每域一包     | ✅ 每域一包      | 和 Netflix 风格一致 |
| CRUD     | 纯函数        | class Service   | ✅ class Service | 我们更适合 DI       |
| Schema   | SQLModel 统一 | 分离 schemas.py | ✅ 分离          | 分离更灵活          |
| 类型标注 | `str \| None` | `str \| None`   | ✅ `str \| None` | 已统一              |
| 异常处理 | 全局          | ✅ per-module   | ⚠️ 仅全局        | 待补充              |
| 常量管理 | 无            | ✅ per-module   | ❌ 无            | 待补充              |
