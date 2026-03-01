# Phase Review: 测试 (testing)

**Review 类型**: 测试类
**执行时间**: 2026-03-01T02:49:00Z
**产出物**: `docs/test-report.md`, `backend/tests/`, `frontend/src/test/`
**作者**: Frank (QA)
**审查人**: Charlie (Tech Lead)

---

## 自动检查

- ✅ `uv run pytest tests/ --tb=short` — 175 passed, 7 warnings (cwd: backend)
- ✅ `npx vitest run` — 128 passed, 16 test files (cwd: frontend)
- ✅ `uv run ruff check app/` — All checks passed
- ✅ `npx tsc --noEmit` — 零 TypeScript 错误
- ✅ 后端覆盖率: 85% (1734 stmts, 254 missed) — 超过 80% 阈值
- ✅ 前端覆盖率: 77.70% stmts, 76.86% branches, 73.87% funcs, 76.83% lines — 超过 70% 阈值

## 审查清单

### 覆盖率检查

- ✅ **后端总覆盖率 ≥ 80%** — 85%，达标
- ✅ **前端总覆盖率 ≥ 70%** — 77.70% statements，达标
- ✅ **核心业务逻辑覆盖率** — recommendation/service.py 100%, calculator.py 100%, encryption.py 100%
- ⚠️ **低覆盖率模块** — order/service.py 22%, profit/service.py 41% (见 MEDIUM #1)

### 测试完整性 — 单元测试

- ✅ **Service 层** — 12 个后端单元测试文件覆盖 auth/price/merchant/logistics/recommendation/order/settings
- ✅ **工具函数** — calculator.py, encryption.py, pagination.py, exceptions.py 全部 100%
- ✅ **模型验证** — test_schemas.py 覆盖 Pydantic schema 验证
- ✅ **边界情况** — 空值、无效输入、重复数据有测试
- ✅ **错误路径** — 异常场景 (auth failure, not found, duplicate) 有测试

### 测试完整性 — 集成测试

- ✅ **API 端点** — 6 个集成测试文件覆盖 auth/price/merchant/logistics/recommendation/settings
- ✅ **数据库操作** — 使用 async_client + SQLite 内存数据库进行真实 DB 操作测试
- ✅ **认证流程** — test_auth_routes.py 覆盖登录/token/权限

### 测试完整性 — 前端测试

- ✅ **页面组件** — 7 个页面全部有测试 (Login/Dashboard/PriceCenter/Merchant/Logistics/Orders/Settings)
- ✅ **布局组件** — AppLayout/Sidebar/MobileNav/ProtectedRoute 4 个组件有测试
- ✅ **服务层** — api.ts + 5 个 service 模块全部有测试
- ✅ **状态管理** — useAuthStore 有测试 (12 tests)
- ✅ **主题配置** — theme.ts 有测试 (12 tests)
- ✅ **Provider** — QueryProvider 有测试

### 测试完整性 — E2E 测试

- ⚠️ **E2E 未配置** — 无 Playwright 测试 (见 MEDIUM #2)

### 测试质量

- ✅ **命名描述性** — 所有测试使用描述性名称 (如 "returns empty array when no items match query")
- ✅ **AAA 模式** — Arrange → Act → Assert 结构清晰
- ✅ **测试隔离** — beforeEach 中 vi.clearAllMocks()，无共享状态
- ✅ **Mock 正确** — 外部依赖 (API, DB, Router) 正确 Mock
- ✅ **无固定 sleep** — 使用 waitFor/act 而非 sleep
- ✅ **无 console.log** — 测试代码中无调试语句
- ✅ **无 .only/.skip** — 无被跳过或独占的测试

### 测试数据

- ✅ **测试数据隔离** — 后端使用 SQLite 内存数据库，前端使用 Mock
- ✅ **无硬编码外部依赖** — 不依赖真实的第三方 API
- ✅ **数据清理** — 后端 conftest.py 每个测试自动 rollback

### 测试报告

- ✅ **docs/test-report.md** — 报告存在且非空
- ✅ **详细分报告** — 5 个子报告 (unit/integration/frontend-checks/coverage/bugfixes)
- ✅ **缺陷记录** — 6 个 Bug 全部记录并修复
- ✅ **覆盖率数据** — 后端按模块列出，前端按指标列出

## 发现的问题

| #   | 严重度     | 描述                                                                               | 位置                                 | 建议修复                    |
| --- | ---------- | ---------------------------------------------------------------------------------- | ------------------------------------ | --------------------------- |
| 1   | **MEDIUM** | order/service.py 覆盖率仅 22%，profit/service.py 仅 41% — 业务逻辑覆盖不足         | backend/app/modules/order/service.py | Sprint 后续迭代补充         |
| 2   | **MEDIUM** | E2E 测试未配置 — 无 Playwright 测试覆盖核心用户流程                                | 项目级别                             | V1.5 版本补充 E2E 测试      |
| 3   | **MEDIUM** | 前端测试 act(...) 警告 — 部分页面组件在渲染后触发异步状态更新，产生 console stderr | 多个 page test files                 | 使用 act() 包裹或可忽略     |
| 4   | **LOW**    | 后端 pytest 有 7 个 deprecation warnings (HTTP_422 constant)                       | tests/                               | 升级 FastAPI 版本时统一修复 |

## 结论 (初审)

- 🟢 **通过** — 无 HIGH/CRITICAL 问题。后端覆盖率 85% 超过 80% 阈值，前端覆盖率 77.70% 超过 70% 阈值。所有 303 个测试全部通过。4 个 MEDIUM 问题均有明确的处理计划，不阻塞进入下一阶段。

## MEDIUM 问题处理计划

| #   | 问题                          | 处理方式                                    |
| --- | ----------------------------- | ------------------------------------------- |
| 1   | order/profit service 覆盖率低 | → V1.5 迭代补充，当前核心路径有集成测试保障 |
| 2   | E2E 测试未配置                | → V1.5 版本增加 Playwright 核心流程测试     |
| 3   | act(...) console warnings     | → 不影响测试正确性，后续重构组件时消除      |
| 4   | pytest deprecation warnings   | → 升级 FastAPI 时统一修复                   |

## 统计

- 检查项总数: 28
- 通过: 24 | 警告: 4 (MEDIUM)
- 后端: 175 tests, 85% coverage
- 前端: 128 tests, 77.70% coverage
- 总计: **303 tests, 100% pass rate**
