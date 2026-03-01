# 代码审查报告

## 概览

- **审查日期**: 2026-02-28
- **代码版本**: `3367128` (HEAD → main)
- **审查范围**: `backend/app/`, `frontend/src/`, `backend/tests/`, `frontend/src/test/`
- **审查人**: Grace (Code Reviewer)
- **工作树状态**: 干净 (无未提交变更)

---

## 评分

| 维度           | 权重 | 得分       | 说明                                              |
| -------------- | ---- | ---------- | ------------------------------------------------- |
| **功能正确性** | 30%  | 9/10       | 8 模块全覆盖，303 测试全通过                      |
| **代码质量**   | 25%  | 9/10       | 分层清晰，命名规范，函数长度达标                  |
| **安全性**     | 20%  | 8/10       | 无注入/XSS/硬编码密钥，dev 默认密钥需生产环境覆盖 |
| **性能**       | 15%  | 8/10       | 使用子查询避免 N+1，推荐缓存待 V1.5               |
| **测试覆盖**   | 10%  | 8/10       | 后端 85%、前端 77.70%，部分模块覆盖较低           |
| **总分**       | 100% | **85/100** | **✅ 通过**                                       |

---

## 自动化检查结果

### 后端

| 检查项         | 结果                 | 说明                              |
| -------------- | -------------------- | --------------------------------- |
| `ruff check`   | ✅ All checks passed | 0 errors, 0 warnings              |
| `pytest`       | ✅ 175 passed        | 7 deprecation warnings (HTTP_422) |
| `py_compile`   | ✅ 全部通过          | 42 模块文件                       |
| 文件大小       | ✅ 全部 ≤ 300 行     | 最大: order/service.py 254 行     |
| `tsc --noEmit` | N/A                  | Python 项目                       |

### 前端

| 检查项         | 结果             | 说明                          |
| -------------- | ---------------- | ----------------------------- |
| `tsc --noEmit` | ✅ 零错误        | TypeScript 编译通过           |
| `vitest run`   | ✅ 128 passed    | 16 test files, 100% pass rate |
| `npm audit`    | ✅ 0 漏洞        | found 0 vulnerabilities       |
| 文件大小       | ✅ 全部 ≤ 224 行 | 最大: Merchant.tsx 213 行     |

---

## 安全审查

### OWASP Top 10 检查

| #   | 检查项       | 状态 | 说明                                                         |
| --- | ------------ | ---- | ------------------------------------------------------------ |
| A01 | 访问控制     | ✅   | 所有受保护端点使用 `Depends(get_current_user)`               |
| A02 | 加密失效     | ✅   | bcrypt 密码哈希，AES-256 敏感字段加密                        |
| A03 | 注入攻击     | ✅   | 全部 SQLAlchemy ORM 参数化查询，无字符串拼接                 |
| A04 | 不安全设计   | ✅   | 分层架构 Router → Service → Model                            |
| A05 | 安全配置错误 | 🟡   | dev 环境有默认密钥 (jwt_secret, encryption_key)，见 Minor #3 |
| A06 | 脆弱组件     | ✅   | `npm audit` 0 漏洞                                           |
| A07 | 认证缺陷     | ✅   | JWT + bcrypt，401 自动清除 Token                             |
| A08 | 数据完整性   | ✅   | Pydantic 验证所有输入                                        |
| A09 | 日志监控不足 | 🟡   | structlog 方案已设计，生产环境需配置 Sentry DSN              |
| A10 | SSRF         | ✅   | 无用户提供的 URL 请求                                        |

### 敏感信息扫描

- ✅ `grep hardcoded password/secret/api_key` — 无结果
- ✅ `grep dangerouslySetInnerHTML/innerHTML` — 无结果
- ✅ `grep console.log` — 无结果 (前端 + 后端)
- ✅ `.env` 在 `.gitignore` 中
- ✅ API URL 通过 `VITE_API_URL` 环境变量配置

---

## 发现问题

### 🔴 Critical (0)

无

### 🟠 Major (0)

无

### 🟡 Minor (5)

| #   | ID     | 描述                                                         | 文件                                 | 建议修复                                           |
| --- | ------ | ------------------------------------------------------------ | ------------------------------------ | -------------------------------------------------- |
| 1   | BE-001 | `_fetch_product_data` 54 行，略超 50 行限制                  | `recommendation/service.py:93-146`   | 可拆分 subquery 构建为独立方法，但声明式代码影响小 |
| 2   | BE-002 | `order/service.py` 覆盖率仅 22%，`profit/service.py` 仅 41%  | `backend/tests/`                     | V1.5 迭代补充，当前核心路径已有集成测试            |
| 3   | BE-003 | `config.py` dev 默认密钥不应出现在代码中                     | `backend/app/config.py:23,35`        | 移除默认值，强制生产环境通过 env var 提供          |
| 4   | FE-001 | Merchant.tsx 主组件 186 行 (含 JSX)，可考虑提取 Modal 子组件 | `pages/Merchant/Merchant.tsx`        | 提取 `MerchantFormModal` 组件，改善可维护性        |
| 5   | FE-002 | act(...) 控制台警告 — 部分页面测试异步状态更新               | `frontend/src/test/pages/*.test.tsx` | 可忽略或后续重构组件时消除                         |

### 🔵 Info (4)

| #   | ID     | 描述                                                             | 建议                        |
| --- | ------ | ---------------------------------------------------------------- | --------------------------- |
| 1   | IN-001 | ESLint 未配置                                                    | V1.5 版本补充               |
| 2   | IN-002 | E2E 测试 (Playwright) 未配置                                     | V1.5 版本增加核心流程 E2E   |
| 3   | IN-003 | pytest 7 个 deprecation warnings (HTTP_422_UNPROCESSABLE_ENTITY) | 升级 FastAPI 版本时统一修复 |
| 4   | IN-004 | 推荐结果无缓存                                                   | V1.5 增加 Redis 缓存        |

---

## 代码质量详评

### 后端 (Python/FastAPI)

#### 架构一致性 ✅

- **8 模块** 均遵循 `modules/{name}/` 结构，每个模块包含 `__init__.py`, `models.py`, `schemas.py`, `service.py`, `router.py`
- **分层正确**: Router → Service → Model，无跨层调用
- **核心复用**: `core/` 目录提取了 pagination, exceptions, auth, encryption 公共逻辑

#### 代码规范 ✅

- ✅ 全部 `ruff check` 通过
- ✅ 全部函数有类型注解 (参数 + 返回值)
- ✅ 无 magic number — 使用命名常量 (`WEIGHT_PROFIT`, `RISK_THRESHOLDS`, `ORDER_STATUS_TRANSITIONS`)
- ✅ 使用 early return 减少嵌套，最大嵌套 ≤ 3 层
- ✅ 函数长度绝大部分 ≤ 50 行 (仅 `_fetch_product_data` 54 行)
- ✅ 所有文件 ≤ 300 行

#### 安全实践 ✅

- ✅ 全部查询使用 SQLAlchemy ORM 参数化
- ✅ 密码使用 bcrypt 哈希
- ✅ 敏感字段 (phone/wechat/address) 使用 AES-256 加密
- ✅ JWT Token 认证，`Depends(get_current_user)` 保护端点
- ✅ 密钥通过 Pydantic Settings + 环境变量管理

### 前端 (React/TypeScript)

#### 架构一致性 ✅

- **目录结构** 符合设计:
  - `components/layout/` — AppLayout + Sidebar + MobileNav
  - `components/auth/` — ProtectedRoute
  - `pages/{Page}/` — 页面组件
  - `services/` — API 服务层 (Axios)
  - `stores/` — Zustand 状态管理
  - `providers/` — React Query

#### 代码规范 ✅

- ✅ 全部 TypeScript，无 `any` 类型
- ✅ 无 `console.log`，无注释掉的代码
- ✅ CSS 变量与设计系统一致
- ✅ Ant Design ConfigProvider 映射设计 Token
- ✅ `data-testid` 标注关键元素

#### 安全实践 ✅

- ✅ API URL 通过 `VITE_API_URL` 环境变量
- ✅ 无 `dangerouslySetInnerHTML`/`innerHTML`
- ✅ JWT 存储在 localStorage，401 自动清除并跳转登录
- ✅ 所有表单使用 Ant Design Form + rules 验证

---

## 性能审查

### 后端

| 检查项     | 状态 | 说明                                                           |
| ---------- | ---- | -------------------------------------------------------------- |
| N+1 查询   | ✅   | 使用 `selectinload` 预加载关系，`_fetch_product_data` 用子查询 |
| 数据库索引 | ✅   | 14 个索引覆盖高频查询场景                                      |
| 内存分配   | ✅   | 无大量内存分配                                                 |
| 阻塞操作   | ✅   | 全部使用 async/await                                           |
| 缓存策略   | 🟡   | 汇率有 Redis 缓存，推荐结果待 V1.5 缓存                        |

### 前端

| 检查项      | 状态 | 说明                                       |
| ----------- | ---- | ------------------------------------------ |
| Bundle 大小 | ✅   | Vite 构建，Ant Design 按需引入             |
| 懒加载      | ✅   | React.lazy + Suspense 路由级别懒加载       |
| 重渲染      | 🟡   | 暂无 useMemo/useCallback，当前规模无需优化 |
| React Query | ✅   | staleTime 5min, retry 1, 合理减少请求      |
| 内存泄漏    | ✅   | useEffect 清理函数正确 (cancelled flag)    |

---

## 测试覆盖

| 层级     | 测试数量 | 覆盖率 | 状态 |
| -------- | -------- | ------ | ---- |
| 后端     | 175      | 85%    | ✅   |
| 前端     | 128      | 77.70% | ✅   |
| **总计** | **303**  | -      | ✅   |

### 核心模块覆盖率

| 模块                      | 覆盖率 | 状态 |
| ------------------------- | ------ | ---- |
| recommendation/service.py | 100%   | ✅   |
| profit/calculator.py      | 100%   | ✅   |
| core/encryption.py        | 100%   | ✅   |
| auth/service.py           | 高     | ✅   |
| price/service.py          | 高     | ✅   |
| order/service.py          | 22%    | ⚠️   |
| profit/service.py         | 41%    | ⚠️   |

---

## 修复建议

### 无阻断发布问题 ✅

项目无 Critical 或 Major 问题，可以继续进入部署阶段。

### 建议修复 (V1.5)

- [ ] BE-002: 补充 order/profit service 测试覆盖率
- [ ] BE-003: 移除 config.py 中 dev 默认密钥
- [ ] FE-001: 拆分 Merchant.tsx 为更小的组件
- [ ] IN-001: 配置 ESLint
- [ ] IN-002: 增加 Playwright E2E 测试
- [ ] IN-004: 增加推荐结果 Redis 缓存

---

## 结论

代码整体质量 **优秀**，安全实践到位，架构清晰。**无 Critical/Major 问题**，5 个 Minor 问题和 4 个 Info 级提示均有明确的处理计划。

**✅ 审查通过，可进入部署阶段。**
