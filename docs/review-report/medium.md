# 中等问题 (Medium)

> 建议在 V1.1 前修复

---

## CR-004 — 前端 API 路径与后端路由不匹配

- 文件: `frontend/src/services/priceService.ts`
- 问题: 前端调用 `/api/v1/prices/products`，但后端路由前缀是 `/api/v1/products`
- 影响: 前端比价中心页面无法正常加载数据

```typescript
// 当前 (错误)
getProducts: (params) => api.get("/api/v1/prices/products", { params }),
getProduct: (id) => api.get(`/api/v1/prices/products/${id}`),
getCategories: () => api.get("/api/v1/prices/categories"),

// 应改为
getProducts: (params) => api.get("/api/v1/products", { params }),
getProduct: (id) => api.get(`/api/v1/products/${id}`),
getCategories: () => api.get("/api/v1/products/categories"),
```

---

## CR-005 — 前端 Merchant 接口字段与后端 Schema 不匹配

- 文件: `frontend/src/services/merchantService.ts` + `Merchant.tsx`
- 问题: 前端使用 `contact_person`、`rating`、`notes` 字段，但后端 Schema 使用 `contact_name`、`tier`，无 `notes` 字段
- 影响: 商户管理页面的联系人、评级显示和编辑功能异常

| 前端字段 | 后端字段 | 状态 |
|----------|----------|------|
| `contact_person` | `contact_name` | ❌ 不匹配 |
| `rating` (S/A/B/C) | `tier` (gold/silver/bronze) | ❌ 不匹配 |
| `notes` | 不存在 | ❌ 缺失 |

---

## CR-006 — 前端 Logistics 接口字段与后端 Schema 不匹配

- 文件: `frontend/src/services/logisticsService.ts`
- 问题: 前端 `FreightAgent` 接口包含 `channel`、`currency` 字段，但后端 Schema 使用 `price_unit`，无 `channel`/`currency`

| 前端字段 | 后端字段 | 状态 |
|----------|----------|------|
| `channel` | 不存在 | ❌ 缺失 |
| `currency` | `price_unit` (kg/piece) | ❌ 不匹配 |

---

## CR-007 — Login 发送 form-urlencoded 但后端期望 JSON

- 文件: `frontend/src/stores/useAuthStore.ts`
- 问题: `login` 方法使用 `URLSearchParams` + `application/x-www-form-urlencoded`，但后端 `LoginRequest` 是 Pydantic `BaseModel`，期望 JSON body
- 影响: 登录请求可能返回 422 Validation Error

```typescript
// 当前 (form-urlencoded)
const formData = new URLSearchParams();
formData.append("username", username);
formData.append("password", password);
await api.post("/api/v1/auth/login", formData, {
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
});

// 应改为 JSON
await api.post("/api/v1/auth/login", { username, password });
```

---

## CR-008 — SQL 注入风险: search 参数直接拼接 LIKE

- 文件: `backend/app/modules/merchant/service.py`, `backend/app/modules/price/service.py`
- 问题: `search` 参数直接拼接到 `ilike(f"%{search}%")`，如果用户输入 `%` 或 `_` 等 SQL 通配符，会导致非预期的匹配结果
- 风险: 低（SQLAlchemy 参数化查询防止了真正的 SQL 注入，但通配符未转义）
- 建议: 转义 `%` 和 `_` 字符

```python
def _escape_like(value: str) -> str:
    return value.replace("%", "\\%").replace("_", "\\_")

# 使用
query = query.where(Merchant.name.ilike(f"%{_escape_like(search)}%"))
```

---

## CR-009 — Settings 路由 PUT "/" 与 PUT "/{key}" 冲突

- 文件: `backend/app/modules/settings/router.py`
- 问题: `PUT /api/v1/settings/` (bulk update) 和 `PUT /api/v1/settings/{key}` 共存，当 key 为空字符串时可能产生路由歧义
- 建议: 将 bulk update 改为 `PUT /api/v1/settings/bulk` 或 `POST /api/v1/settings/bulk`
