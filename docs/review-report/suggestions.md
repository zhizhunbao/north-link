# 优化建议 (Low)

> 非阻塞性建议，可在后续迭代中改进

---

## CR-010 — Database session auto-commit 模式

- 文件: `backend/app/database.py`
- 现状: `get_db()` 在 yield 后自动 commit，这意味着即使是 GET 请求也会触发 commit
- 建议: 考虑将 commit 责任交给 service 层，或仅在写操作时 commit

---

## CR-011 — PaginatedResponse.total_pages 是 @property 不会被序列化

- 文件: `backend/app/core/pagination.py`
- 现状: `total_pages` 定义为 `@property`，Pydantic V2 默认不序列化 property
- 影响: 前端无法获取 `total_pages` 字段
- 建议: 改为 `@computed_field`

```python
from pydantic import computed_field

class PaginatedResponse(BaseModel, Generic[T]):
    ...
    @computed_field
    @property
    def total_pages(self) -> int:
        if self.page_size <= 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size
```

---

## CR-012 — Exchange Rate 服务仅使用硬编码 fallback

- 文件: `backend/app/modules/profit/exchange_rate.py`
- 现状: `get_exchange_rate()` 始终返回 `FALLBACK_RATE_CAD_TO_CNY = 5.20`，Redis 和 API 集成标记为 TODO
- 建议: MVP 可接受，但应在 V1.1 中优先实现 Redis 缓存 + API 调用

---

## CR-013 — 前端 Dashboard 统计卡片硬编码为 0

- 文件: `frontend/src/pages/Dashboard/Dashboard.tsx`
- 现状: "在途物流" 和 "今日利润" 统计值硬编码为 `0`
- 建议: 接入实际 API 或标注为 "Coming Soon"

---

## CR-014 — 前端 PriceCenter 价格显示为 "-"

- 文件: `frontend/src/pages/PriceCenter/PriceCenter.tsx`
- 现状: 加拿大/国内价格始终显示 `-`，未从 `ProductListItem` 的 `lowest_ca_price`/`highest_cn_price` 读取
- 建议: 绑定实际数据字段

---

## CR-015 — 前端 Logistics ShipmentTab 使用硬编码数据

- 文件: `frontend/src/pages/Logistics/Logistics.tsx`
- 现状: `ShipmentTab` 组件使用硬编码的 Timeline 数据
- 建议: 接入 `/api/v1/logistics/shipments` API

---

## CR-016 — 缺少 Alembic 迁移文件

- 现状: `pyproject.toml` 依赖了 `alembic`，但项目中没有 `alembic.ini` 和 `migrations/` 目录
- 建议: 初始化 Alembic 并生成初始迁移，确保数据库 schema 可版本化管理

---

## CR-017 — 前端缺少环境变量配置文件

- 现状: `api.ts` 使用 `import.meta.env.VITE_API_URL`，但没有 `.env` 或 `.env.example` 文件
- 建议: 添加 `frontend/.env.example` 文件，文档化所需环境变量
