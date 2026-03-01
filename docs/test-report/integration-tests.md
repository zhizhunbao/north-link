# 集成测试报告

> 39 个用例 | 6 个测试文件 | 全部通过 | 耗时 ~13s
>
> 依赖: PostgreSQL 测试容器 (db-test, port 5433)

---

## 测试环境

- 数据库: PostgreSQL 16 (Docker, `northlink-db-test`)
- 每个测试函数独立事务，测试后自动回滚
- HTTP 客户端: httpx AsyncClient (ASGI transport)
- 认证: 每个需要认证的测试自动创建 testuser 并登录获取 JWT

## 模块明细

### 认证路由 (test_auth_routes.py) — 5 用例

| 用例 | 描述 | 状态 |
|------|------|------|
| test_login_wrong_password | 错误密码登录返回 401 | ✅ |
| test_get_me_unauthenticated | 无 token 访问 /me 返回 401 | ✅ |
| test_get_me_authenticated | 认证用户获取自身信息 | ✅ |
| test_change_password_wrong_old | 旧密码错误返回 400/401 | ✅ |
| test_refresh_invalid_token | 无效 refresh token 返回 401 | ✅ |

### 物流路由 (test_logistics_routes.py) — 7 用例

| 用例 | 描述 | 状态 |
|------|------|------|
| test_list_agents_unauthenticated | 未认证列表返回 401 | ✅ |
| test_list_agents_empty | 空数据库返回 total=0 | ✅ |
| test_create_agent | 创建货代返回 201 + 完整数据 | ✅ |
| test_create_agent_invalid_est_days | est_days_min > max 返回 422 | ✅ |
| test_get_agent_not_found | 不存在的货代返回 404 | ✅ |
| test_create_and_update_agent | 创建→更新→验证字段变更 | ✅ |
| test_delete_agent | 创建→删除→确认 404 | ✅ |

### 商户路由 (test_merchant_routes.py) — 10 用例

| 用例 | 描述 | 状态 |
|------|------|------|
| test_list_merchants_unauthenticated | 未认证返回 401 | ✅ |
| test_list_merchants_empty | 空列表 items=[], total=0 | ✅ |
| test_create_merchant | 创建商户验证响应字段 | ✅ |
| test_create_merchant_invalid_tier | 无效 tier 返回 422 | ✅ |
| test_get_merchant_not_found | 不存在返回 404 | ✅ |
| test_create_and_get_merchant | 创建→获取完整往返 | ✅ |
| test_update_merchant | 创建→更新→验证变更 | ✅ |
| test_delete_merchant | 创建→删除→确认 404 | ✅ |
| test_list_categories | 分类列表返回 list | ✅ |
| test_list_merchants_after_create | 创建后列表 total=1 | ✅ |

### 比价路由 (test_price_routes.py) — 9 用例

| 用例 | 描述 | 状态 |
|------|------|------|
| test_list_products_unauthenticated | 未认证返回 401 | ✅ |
| test_list_products_empty | 空列表 total=0 | ✅ |
| test_create_product | 创建商品 (含 category) 返回 200 | ✅ |
| test_create_product_duplicate_sku | 重复 SKU 返回 409 | ✅ |
| test_get_product_not_found | 不存在返回 404 | ✅ |
| test_create_and_get_product | 创建→获取往返 | ✅ |
| test_update_product | 创建→更新→验证 | ✅ |
| test_delete_product | 创建→删除→确认 404 | ✅ |
| test_toggle_favorite | 收藏切换 on/off | ✅ |

### 推荐路由 (test_recommendation_routes.py) — 3 用例

| 用例 | 描述 | 状态 |
|------|------|------|
| test_get_recommendations_unauthenticated | 未认证返回 401 | ✅ |
| test_get_recommendations_empty_db | 空数据库返回空推荐列表 | ✅ |
| test_get_recommendations_returns_date | 响应包含今日日期 | ✅ |

### 设置路由 (test_settings_routes.py) — 5 用例

| 用例 | 描述 | 状态 |
|------|------|------|
| test_list_settings_unauthenticated | 未认证返回 401 | ✅ |
| test_list_settings | 认证后返回设置列表 | ✅ |
| test_get_setting_not_found | 不存在的 key 返回 404 | ✅ |
| test_bulk_update_and_get | 批量更新→单条获取验证 | ✅ |
| test_export_data | 导出包含 exported_at + settings | ✅ |
