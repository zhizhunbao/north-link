# 代码类阶段 Review 清单

适用阶段: `backend`, `frontend`, `review`

## 自动检查（先跑工具）

```bash
# Python (backend)
uv run ruff check app/              # Lint
uv run ruff format --check app/     # 格式
uv run mypy app/                    # 类型
uv run bandit -r app/               # 安全
uv run pytest --tb=short -q         # 测试

# TypeScript (frontend)
npm run lint                         # ESLint
npx tsc --noEmit                     # 类型
npm test                             # 测试
```

## 安全检查 (CRITICAL)

- [ ] **无硬编码凭证** — 无 API keys, passwords, tokens, secrets 出现在代码中
- [ ] **无 SQL 注入** — 所有数据库查询使用参数化查询，无字符串拼接
- [ ] **无 XSS 漏洞** — 用户输入经过转义，使用 `textContent` 而非 `innerHTML`
- [ ] **输入验证完整** — 所有用户输入有 Pydantic/Zod 验证
- [ ] **无路径遍历** — 用户提供的文件路径已安全处理
- [ ] **认证授权** — 受保护的端点有权限检查
- [ ] **密钥管理** — 使用环境变量，`.env` 在 `.gitignore` 中

## 代码质量 (HIGH)

- [ ] **函数大小** — 所有函数 ≤ 50 行
- [ ] **文件大小** — 所有文件 ≤ 800 行
- [ ] **嵌套深度** — 最大嵌套 ≤ 4 层（使用 early return 减少嵌套）
- [ ] **无空 try/catch** — 异常被正确处理，非静默吞掉
- [ ] **无 console.log** — 生产代码中无调试语句
- [ ] **无注释掉的代码** — 已删除或有 TODO issue 关联
- [ ] **类型完整** — 无 `any` 类型（TypeScript），有类型注解（Python）
- [ ] **命名清晰** — 无 `x`, `tmp`, `data` 等模糊命名

## 架构一致性 (HIGH)

- [ ] **目录结构** — 符合 `architecture` 阶段定义的结构
- [ ] **分层正确** — Router → Service → Repository 分层清晰
- [ ] **API 契约** — 接口定义与 PRD/架构文档一致
- [ ] **不可变模式** — 创建新对象而非修改现有对象

## 性能 (MEDIUM)

- [ ] **无 O(n²)** — 可优化的嵌套循环已优化
- [ ] **无 N+1 查询** — 使用 JOIN 或预加载
- [ ] **缓存策略** — 热点数据有适当缓存
- [ ] **React 优化** — 无不必要的重渲染（useMemo/useCallback）

## 最佳实践 (MEDIUM)

- [ ] **DRY 原则** — 无重复代码（提取公共逻辑）
- [ ] **单一职责** — 每个模块/类/函数只做一件事
- [ ] **无 magic number** — 使用命名常量
- [ ] **错误信息友好** — 用户可理解的错误提示
- [ ] **新代码有测试** — 新增功能有对应测试

## 前端特定检查（仅 frontend 阶段）

- [ ] **可访问性** — 关键元素有 ARIA 标签
- [ ] **响应式** — 主要页面适配移动端
- [ ] **data-testid** — 关键交互元素有 testid 属性
- [ ] **i18n** — 用户可见文本使用 i18n key（如项目需要）
- [ ] **公共 API 有 JSDoc** — 组件 Props 有文档

## 审批标准

- ✅ **批准**: 无 CRITICAL/HIGH 问题
- ⚠️ **条件通过**: 仅 MEDIUM 问题（可谨慎继续）
- ❌ **阻止**: 发现 CRITICAL/HIGH 问题，必须修复
