# North Link 跨境货源通 — 测试报告

> 版本: V1.0 | 测试日期: 2026-02-28 | QA: Frank (Senior QA)

---

## 总览

| 指标                        | 数值      |
| --------------------------- | --------- |
| 测试总数                    | 303       |
| 通过                        | 303       |
| 失败                        | 0         |
| 通过率                      | 100%      |
| 后端代码覆盖率 (Statements) | 85%       |
| 前端代码覆盖率 (Statements) | 77.70%    |
| 前端 TypeScript 编译        | ✅ 零错误 |
| 后端 Ruff lint              | ✅ 零错误 |

## 覆盖率达标情况

| 端                   | 目标  | 实际   | 状态    |
| -------------------- | ----- | ------ | ------- |
| 后端 (pytest-cov)    | ≥ 80% | 85%    | ✅ 达标 |
| 前端 Statements (v8) | ≥ 70% | 77.70% | ✅ 达标 |
| 前端 Branches (v8)   | ≥ 70% | 76.86% | ✅ 达标 |
| 前端 Functions (v8)  | ≥ 70% | 73.87% | ✅ 达标 |
| 前端 Lines (v8)      | ≥ 70% | 76.83% | ✅ 达标 |

## 测试分布

| 类别          | 文件数 | 用例数 | 状态        |
| ------------- | ------ | ------ | ----------- |
| 后端 单元测试 | 12     | 136    | ✅ 全部通过 |
| 后端 集成测试 | 6      | 39     | ✅ 全部通过 |
| 前端 单元测试 | 16     | 128    | ✅ 全部通过 |

## 详细报告

- [后端单元测试](test-report/unit-tests.md)
- [后端集成测试](test-report/integration-tests.md)
- [覆盖率报告](test-report/coverage.md)
- [前端检查](test-report/frontend-checks.md)
- [缺陷修复记录](test-report/bugfixes.md)

## 测试期间发现并修复的缺陷

共发现 **6 类缺陷**，全部已修复。详见 [缺陷修复记录](test-report/bugfixes.md)。

| ID      | 严重度   | 模块             | 描述                                                            | 状态      |
| ------- | -------- | ---------------- | --------------------------------------------------------------- | --------- |
| BUG-001 | Critical | conftest         | `auth_headers` fixture 使用不存在的 `full_name` 字段            | ✅ 已修复 |
| BUG-002 | Critical | merchant/models  | datetime 列缺少 `timezone=True`，导致 offset-naive/aware 冲突   | ✅ 已修复 |
| BUG-003 | Critical | logistics/models | 同上 datetime timezone 问题                                     | ✅ 已修复 |
| BUG-004 | Medium   | profit/models    | `fetched_at` 列缺少 `DateTime(timezone=True)`                   | ✅ 已修复 |
| BUG-005 | Medium   | 集成测试         | 多个测试文件 URL/status code/请求体与实际 API 不匹配            | ✅ 已修复 |
| BUG-006 | Low      | 前端             | 3 个页面组件 `useEffect` 中同步调用 `setState` 违反 ESLint 规则 | ✅ 已修复 |

## 完成检查

- [x] 后端单元测试覆盖率 ≥ 80%
- [x] 前端单元测试覆盖率 ≥ 70%
- [x] 集成测试通过
- [x] 无阻断性 Bug
- [x] 测试报告已生成
