# 缺陷修复记录

> 测试阶段共发现 6 类缺陷，全部已修复

---

## BUG-001 — auth_headers fixture 使用不存在的字段

- 严重度: **Critical**
- 影响: 所有需要认证的集成测试 (30+ 用例) 全部 ERROR
- 文件: `backend/tests/conftest.py`
- 原因: `auth_headers` fixture 创建 User 时传入了 `full_name="Test User"`，但 User 模型没有 `full_name` 字段
- 修复: 移除 `full_name` 参数

```python
# Before
test_user = User(
    username="testuser",
    password_hash=AuthService.hash_password("Test1234!"),
    full_name="Test User",  # ← 不存在的字段
    role="admin",
    is_active=True,
)

# After
test_user = User(
    username="testuser",
    password_hash=AuthService.hash_password("Test1234!"),
    role="admin",
    is_active=True,
)
```

---

## BUG-002 — Merchant 模型 datetime 列缺少 timezone

- 严重度: **Critical**
- 影响: 所有 Merchant 写入操作报错 `can't subtract offset-naive and offset-aware datetimes`
- 文件: `backend/app/modules/merchant/models.py`
- 原因: `created_at`/`updated_at`/`quoted_at` 列使用 `Mapped[datetime]` 但未指定 `DateTime(timezone=True)` 列类型。Python 默认值使用 `datetime.now(timezone.utc)` (timezone-aware)，但 SQLAlchemy 推断的列类型是 `TIMESTAMP WITHOUT TIME ZONE` (naive)，asyncpg 拒绝混合
- 修复: 所有 datetime 列添加 `DateTime(timezone=True)`，同时导入 `DateTime`

---

## BUG-003 — Logistics 模型同样的 datetime 问题

- 严重度: **Critical**
- 影响: FreightAgent/FreightQuote/Shipment/TrackingEvent 所有写入操作
- 文件: `backend/app/modules/logistics/models.py`
- 原因: 同 BUG-002
- 修复: 所有 datetime 列 (`created_at`, `updated_at`, `shipped_at`, `delivered_at`, `event_at`, `valid_until`) 添加 `DateTime(timezone=True)`

---

## BUG-004 — ExchangeRate 模型 fetched_at 缺少 timezone

- 严重度: **Medium**
- 影响: 汇率记录写入时可能报错 (当前未被集成测试覆盖)
- 文件: `backend/app/modules/profit/models.py`
- 原因: 同 BUG-002
- 修复: `fetched_at` 列添加 `DateTime(timezone=True)`

---

## BUG-005 — 集成测试与实际 API 不匹配

- 严重度: **Medium**
- 影响: 多个集成测试文件的断言与实际 API 行为不一致

### 5a. Logistics 测试 URL 尾部斜杠

- 文件: `backend/tests/integration/test_logistics_routes.py`
- 问题: 测试使用 `/api/v1/logistics/agents/` (带尾部斜杠)，但路由定义为 `/agents` (无斜杠)。FastAPI 默认 `redirect_slashes=True` 返回 307，httpx 不跟随重定向
- 修复: 移除所有 URL 尾部斜杠

### 5b. Logistics create_agent status code

- 问题: 测试期望 `200`，但路由定义 `status_code=201`
- 修复: 断言改为 `201`

### 5c. Logistics invalid est_days status code

- 问题: 测试期望 `400`，但 `ValidationException` 返回 `422`
- 修复: 断言改为 `422`

### 5d. Price 测试缺少 category_id

- 文件: `backend/tests/integration/test_price_routes.py`
- 问题: `ProductCreate` schema 要求 `category_id` (必填)，但测试 payload 未提供
- 修复: 添加 `sample_category` fixture，在测试 DB 中创建 Category，payload 中传入 `category_id`

### 5e. Settings bulk update 请求体格式

- 文件: `backend/tests/integration/test_settings_routes.py`
- 问题: 测试发送 `{"company_name": "..."}` 但端点期望 `{"settings": {"company_name": "..."}}`
- 修复: 包装为 `SettingBulkUpdate` 格式

### 5f. Settings export 端点路径

- 问题: 测试访问 `/export`，但路由定义为 `/export/data`
- 修复: URL 改为 `/export/data`

---

## BUG-006 — 前端 useEffect 中同步 setState

- 严重度: **Low**
- 影响: ESLint `react-hooks/set-state-in-effect` 规则报错 3 处
- 文件:
  - `frontend/src/pages/Merchant/Merchant.tsx`
  - `frontend/src/pages/Orders/Orders.tsx`
  - `frontend/src/pages/PriceCenter/PriceCenter.tsx`
- 原因: 在 `useEffect` 回调体内同步调用 `setLoading(true)`，ESLint 认为这会触发级联渲染
- 修复: 将 `setLoading(true)` 移到 effect 外部 (初始值)，effect 内仅在 `.then()` 异步回调中调用 setState，并添加 cleanup 函数防止组件卸载后更新
