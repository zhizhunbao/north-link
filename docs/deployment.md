# 部署文档 — North Link 跨境货源通

## 环境要求

| 组件       | 版本   | 说明                 |
| ---------- | ------ | -------------------- |
| Python     | 3.12+  | 后端运行时           |
| Node.js    | 20+    | 前端构建             |
| PostgreSQL | 16+    | 主数据库             |
| Redis      | 7+     | 缓存 (汇率、Session) |
| Docker     | 24+    | 容器化部署 (可选)    |
| uv         | latest | Python 包管理器      |

---

## 快速开始 (本地开发)

### 1. 克隆仓库

```bash
git clone <repo-url>
cd north-link
```

### 2. 启动基础设施

```bash
# 启动 PostgreSQL + Redis (开发模式)
docker compose up -d
```

### 3. 后端设置

```bash
cd backend

# 创建环境变量文件
cp .env.example .env
# 编辑 .env 文件，填入实际值

# 安装依赖
uv sync

# 运行数据库迁移
uv run alembic upgrade head

# 创建初始管理员 (首次部署)
uv run python -m app.seed

# 启动后端服务
uv run uvicorn app.main:app --reload --port 8000
```

### 4. 前端设置

```bash
cd frontend

# 创建环境变量文件
cp .env.example .env

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 5. 验证

- 后端 API: http://localhost:8000/docs
- 前端页面: http://localhost:3000
- 健康检查: http://localhost:8000/health
- 就绪检查: http://localhost:8000/health/ready

---

## Docker 全栈部署

### 使用 Docker Compose

```bash
# 构建并启动所有服务
docker compose -f docker-compose.prod.yml up --build -d

# 查看服务状态
docker compose -f docker-compose.prod.yml ps

# 查看日志
docker compose -f docker-compose.prod.yml logs -f

# 停止服务
docker compose -f docker-compose.prod.yml down
```

### 访问地址

| 服务     | 地址                       |
| -------- | -------------------------- |
| 前端     | http://localhost:3000      |
| 后端     | http://localhost:8000      |
| API 文档 | http://localhost:8000/docs |

---

## Render.com 部署 (生产环境)

### 自动部署

1. 将 `render.yaml` 推送到 GitHub 仓库
2. 在 Render Dashboard 创建 Blueprint → 选择仓库
3. Render 自动识别 `render.yaml` 并创建服务:
   - `northlink-api` — 后端 Web Service
   - `northlink-web` — 前端 Static Site
   - `northlink-db` — PostgreSQL 数据库
   - `northlink-redis` — Redis 缓存
4. 配置手动同步的环境变量:
   - `CORS_ORIGINS` — 前端域名 (如 `https://northlink-web.onrender.com`)
   - `SENTRY_DSN` — Sentry DSN (可选)
   - `EXCHANGE_RATE_API_KEY` — 汇率 API 密钥 (可选)

### 首次部署后

```bash
# 运行数据库迁移 (通过 Render Shell)
cd backend && uvicorn app.main:app  # Render 会自动运行
alembic upgrade head

# 创建初始管理员
python -m app.seed
```

---

## CI/CD (GitHub Actions)

### 自动触发

| 事件           | Jobs                                           |
| -------------- | ---------------------------------------------- |
| Push to `main` | Backend Tests → Frontend Tests → Docker Build  |
| PR to `main`   | Backend Tests + Frontend Tests + Security Scan |

### Pipeline 概述

```
Push/PR → main
    ├── backend-test    (ruff + pytest + coverage)
    ├── frontend-test   (tsc + vitest + build)
    ├── security        (Trivy vulnerability scan)
    └── docker-build    (main branch only)
```

### 配置要求

在 GitHub Repository Settings → Secrets 中配置:

| Secret          | 说明               | 必须 |
| --------------- | ------------------ | ---- |
| `CODECOV_TOKEN` | Codecov 上传 Token | 否   |

在 Repository Settings → Variables 中配置:

| Variable       | 说明             | 必须 |
| -------------- | ---------------- | ---- |
| `VITE_API_URL` | 生产环境 API URL | 是   |

---

## 环境变量

### 后端 (backend/.env)

| 变量                    | 必须 | 说明                       | 示例                                        |
| ----------------------- | ---- | -------------------------- | ------------------------------------------- |
| `DATABASE_URL`          | ✅   | PostgreSQL 异步连接字符串  | `postgresql+asyncpg://user:pass@host/db`    |
| `REDIS_URL`             | ✅   | Redis 连接 URL             | `redis://localhost:6379`                    |
| `JWT_SECRET`            | ✅   | JWT 签名密钥 (≥32 字符)    | (随机生成)                                  |
| `ENCRYPTION_KEY`        | ✅   | AES-256 加密密钥 (32 字节) | (随机生成)                                  |
| `CORS_ORIGINS`          | ✅   | 允许的前端域名 (逗号分隔)  | `http://localhost:3000,https://example.com` |
| `APP_ENV`               | 否   | 环境名称                   | `development` / `production`                |
| `APP_DEBUG`             | 否   | 调试模式                   | `false`                                     |
| `SENTRY_DSN`            | 否   | Sentry 错误追踪 DSN        | `https://xxx@sentry.io/xxx`                 |
| `EXCHANGE_RATE_API_KEY` | 否   | 汇率 API 密钥              | API key                                     |

### 前端 (frontend/.env)

| 变量           | 必须 | 说明              | 示例                    |
| -------------- | ---- | ----------------- | ----------------------- |
| `VITE_API_URL` | ✅   | 后端 API 基础 URL | `http://localhost:8000` |

---

## 健康检查

| 端点                | 说明                | 预期响应                            |
| ------------------- | ------------------- | ----------------------------------- |
| `GET /health`       | 应用存活检查        | `{"status": "ok"}`                  |
| `GET /health/ready` | 就绪检查 (DB+Redis) | `{"status": "ok", "checks": {...}}` |

---

## 回滚方案

### Docker 回滚

```bash
# 停止当前版本
docker compose -f docker-compose.prod.yml down

# 回滚到上一个镜像
docker compose -f docker-compose.prod.yml up -d

# 数据库回滚 (如需)
docker compose -f docker-compose.prod.yml exec backend alembic downgrade -1
```

### Render.com 回滚

1. Dashboard → 选择服务 → Manual Deploy → 选择之前的 commit
2. 或在 Git 中 revert commit 后自动触发重新部署

---

## 监控

| 工具      | 用途       | 配置            |
| --------- | ---------- | --------------- |
| structlog | 结构化日志 | 内置，JSON 格式 |
| Sentry    | 错误追踪   | 配置 SENTRY_DSN |
| Render    | 服务监控   | Dashboard 内置  |

---

## 常见问题

### Q: 数据库连接失败

A: 检查 `DATABASE_URL` 格式，确保使用 `postgresql+asyncpg://` 前缀。确认 PostgreSQL 服务已启动。

### Q: Redis 连接失败

A: 确认 Redis 服务已启动。健康检查 `/health/ready` 会显示具体状态。

### Q: 前端 API 请求失败

A: 检查 `VITE_API_URL` 是否指向正确的后端地址。检查 CORS_ORIGINS 是否包含前端域名。

### Q: Docker 构建失败

A: 确保 `uv.lock` 文件存在 (后端)，`package-lock.json` 存在 (前端)。
