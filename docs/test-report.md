# North Link 跨境货源通 — 测试报告

> 版本: V1.0 | 测试日期: 2026-02-28 | QA: Kiro (Senior QA)

---

## 总览

| 指标 | 数值 |
|------|------|
| 测试总数 | 175 |
| 通过 | 175 |
| 失败 | 0 |
| 通过率 | 100% |
| 代码覆盖率 | 85% |
| 前端 TypeScript 编译 | ✅ 零错误 |
| 前端 ESLint | ✅ 零错误 |

## 测试分布

| 类别 | 文件数 | 用例数 | 状态 |
|------|--------|--------|------|
| 单元测试 | 13 | 136 | ✅ 全部通过 |
| 集成测试 | 6 | 39 | ✅ 全部通过 |

## 详细报告

- [后端单元测试](test-report/unit-tests.md)
- [后端集成测试](test-report/integration-tests.md)
- [前端检查](test-report/frontend-checks.md)
- [覆盖率报告](test-report/coverage.md)
- [缺陷修复记录](test-report/bugfixes.md)

## 测试期间发现并修复的缺陷

共发现 **6 类缺陷**，全部已修复。详见 [缺陷修复记录](test-report/bugfixes.md)。

| ID | 严重度 | 模块 | 描述 | 状态 |
|----|--------|------|------|------|
| BUG-001 | Critical | conftest | `auth_headers` fixture 使用不存在的 `full_name` 字段 | ✅ 已修复 |
| BUG-002 | Critical | merchant/models | datetime 列缺少 `timezone=True`，导致 offset-naive/aware 冲突 | ✅ 已修复 |
| BUG-003 | Critical | logistics/models | 同上 datetime timezone 问题 | ✅ 已修复 |
| BUG-004 | Medium | profit/models | `fetched_at` 列缺少 `DateTime(timezone=True)` | ✅ 已修复 |
| BUG-005 | Medium | 集成测试 | 多个测试文件 URL/status code/请求体与实际 API 不匹配 | ✅ 已修复 |
| BUG-006 | Low | 前端 | 3 个页面组件 `useEffect` 中同步调用 `setState` 违反 ESLint 规则 | ✅ 已修复 |
