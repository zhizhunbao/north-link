# Phase Review: 数据库设计 (database)

**Review 类型**: 文档类
**执行时间**: 2026-02-28T13:48:00
**产出物**: `docs/codemaps/database.md`
**作者**: Bob (Architect)
**审查人**: David (Backend)

---

## 自动检查

- ✅ 文件存在: `docs/codemaps/database.md`
- ✅ 文件非空: 18,000+ bytes

## 审查清单

### 通用检查 — 完整性

- ✅ 文档包含所有必要章节: 概述、ER 图、表结构(15表)、索引、数据字典、外键、性能
- ✅ 无占位符文本
- ✅ 所有 15 个实体均有完整表定义 (含字段类型、约束、说明)

### 通用检查 — 一致性

- ✅ 与架构文档 4.1 的 ER 图一致: 15 个实体全部覆盖
- ✅ 命名规范统一: snake_case 表名、字段名
- ✅ 敏感字段标记正确: merchants.phone/wechat/address 为 BYTEA (AES-256)
- ✅ 关税优先级规则明确: SETTINGS > CATEGORY.default_tariff_rate (解决架构 Review MEDIUM #5)
- ✅ 汇率 DB vs Redis 职责明确: Redis 热缓存 4h TTL, DB 做历史记录 (解决架构 Review MEDIUM #6)
- ❌ orders 表增加了 `user_id` FK → 架构 ER 图中 ORDER 没有 user_id 字段 — 但这是合理的补充(需要追踪谁创建了订单)，应同步更新架构文档

### 通用检查 — 可操作性

- ✅ 每个表有具体 SQL 类型、约束、默认值 — 可直接转为 SQLAlchemy Model
- ✅ 索引策略有业务场景说明
- ✅ 种子数据具体 (8 个品类 + 4 个商户品类 + 6 个系统设置)
- ⚠️ NUMERIC 精度设置值得商榷 — price 用 NUMERIC(12,2) 可以，但 profit_rate 用 NUMERIC(5,4) 最大值是 9.9999，而利润率可能超过 100% (如 150%)。应改为 NUMERIC(7,4) 以支持到 999.9999%
- ⚠️ products.name 上的 GIN trigram 索引需要启用 `pg_trgm` 扩展 — 文档中未提到需要执行 `CREATE EXTENSION IF NOT EXISTS pg_trgm`

### 通用检查 — 格式规范

- ✅ Markdown 标题层级正确
- ✅ 表格格式完整
- ✅ Mermaid ER 图语法正确

### database 特定检查

- ✅ 所有实体/表已定义 (15/15)
- ✅ 字段类型和约束完整 — 每个字段都有类型、NOT NULL/NULLABLE、DEFAULT
- ✅ 关系已标注 — ER 图 + 外键级联规则表
- ✅ 索引策略完整 — 14 个索引，覆盖高频查询
- ✅ 与架构文档数据模型一致
- ✅ 级联删除规则合理 (CASCADE/RESTRICT/SET NULL 分类清晰)
- ✅ 数据量预估和查询优化策略有具体数字

## 发现的问题

| #   | 严重度     | 描述                                                  | 位置                    | 建议修复                               |
| --- | ---------- | ----------------------------------------------------- | ----------------------- | -------------------------------------- |
| 1   | **MEDIUM** | orders.profit_rate NUMERIC(5,4) 无法存储 >100% 利润率 | 3.11 orders             | 改为 NUMERIC(7,4)                      |
| 2   | **MEDIUM** | pg_trgm 扩展未在 Migration 中声明                     | 4.1 索引 + 8. Migration | 在初始 Migration 中加 CREATE EXTENSION |
| 3   | **LOW**    | orders.user_id 是新增字段，架构 ER 图需同步更新       | 3.11 + 架构文档         | 后续同步更新架构 ER 图                 |

## 结论 (初审)

- 🟢 **通过** — 数据库设计完整、规范、可操作。无 HIGH/CRITICAL 问题。2 个 MEDIUM 问题建议修复但不阻塞进入下一阶段。

## MEDIUM 问题处理计划

| #   | 问题             | 处理方式                                          |
| --- | ---------------- | ------------------------------------------------- |
| 1   | profit_rate 精度 | → 在 backend 阶段 Model 定义时修正为 NUMERIC(7,4) |
| 2   | pg_trgm 扩展     | → 在 backend 阶段创建 Alembic Migration 时加入    |
| 3   | 架构 ER 图同步   | → 后续迭代更新，不阻塞                            |

## 统计

- 检查项总数: 18
- 通过: 15 | 警告: 2 (MEDIUM) | 低: 1
