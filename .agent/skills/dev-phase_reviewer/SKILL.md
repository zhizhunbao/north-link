---
name: dev-phase_reviewer
description: Phase review gate for development workflow. Use when (1) completing any phase in /dev start, (2) validating phase outputs before moving to next phase, (3) running quality checks on documents, code, tests, or deployment configs.
---

# Phase Reviewer

每个开发阶段完成后的强制审查关卡。根据阶段类型加载对应的审查清单，执行自动检查 + 人工审查，生成 Review 报告。

## 🔴 核心规则

1. **不可自审** — Reviewer 必须是与作者不同的角色
2. **严格审查** — Reviewer 必须独立、严格审查，不迁就作者。发现问题必须如实记录
3. **改了就要 Re-Review** — 任何修复后必须由 Reviewer 重新验证，验证内容包括：
   - 修复是否正确解决了原问题
   - 修复是否引入了新问题（结构错误、内容矛盾等）
   - 修复与其他章节/文档的一致性
4. **Review 报告持久化** — 所有 Review 结果保存到 `docs/reviews/phase-{NN}-{phase_key}.md`

## Reviewer 分配表

| 阶段           | 作者             | Reviewer            | 分配理由                         |
| -------------- | ---------------- | ------------------- | -------------------------------- |
| `requirements` | Alice (PM)       | Bob (Architect)     | 架构师验证需求的可行性和完整性   |
| `prd`          | Alice (PM)       | Bob (Architect)     | 架构师验证用户故事的技术可实现性 |
| `ux_design`    | Bella (Designer) | Charlie (Tech Lead) | 技术主管验证设计的可开发性       |
| `architecture` | Bob (Architect)  | Charlie (Tech Lead) | 技术主管验证架构的可任务分解性   |
| `stories`      | Charlie (Lead)   | Bob (Architect)     | 架构师验证任务与架构的一致性     |
| `database`     | Bob (Architect)  | David (Backend)     | 后端工程师验证数据模型的可用性   |
| `backend`      | David (Backend)  | Grace (Reviewer)    | 代码审查专家审查代码质量         |
| `frontend`     | Eve (Frontend)   | Grace (Reviewer)    | 代码审查专家审查代码质量         |
| `testing`      | Frank (QA)       | Charlie (Tech Lead) | 技术主管验证测试覆盖率和策略     |
| `review`       | Grace (Reviewer) | Charlie (Tech Lead) | 技术主管最终确认                 |
| `deployment`   | Henry (DevOps)   | Bob (Architect)     | 架构师验证部署与架构的一致性     |

## Review Protocol

每个阶段完成后，按以下流程执行：

```
阶段执行完成
    ↓
[1] 确定 Reviewer — 查 Reviewer 分配表，不可与作者同角色
    ↓
[2] 确定 Review 类型 — 根据阶段映射表（见下方）
    ↓
[3] 自动验证 — 运行自动检查命令
    ↓
[4] 产出物审查 — 检查产出物的内容质量（不仅仅是"文件存在"）
    ↓
[5] 阶段特定 Review — 加载 references/ 中对应的审查清单并逐项检查
    ↓
[6] 生成 Review 报告 — 保存到 docs/reviews/phase-{NN}-{phase_key}.md
    ↓
[7] 问题处理:
    - 🔴 CRITICAL/HIGH → 作者修复
        ↓
    [7.1] Re-Review（强制）:
        - 验证原问题是否修复
        - 检查修复是否引入新问题
        - 检查修复与其他章节/文档一致性
        - Re-Review 结果追加到同一 Review 文件
        - 若发现新问题 → 重复 [7]
    - 🟡 MEDIUM → 记录处理计划（明确在哪个阶段解决），用户确认后可继续
    - 🟢 全部通过 → 标记阶段完成
    ↓
[8] 用户确认 — 展示结果，用户确认后进入下一阶段
```

## 阶段 → Review 类型映射

| Phase Key      | Review 类型 | 审查清单文件                      |
| -------------- | ----------- | --------------------------------- |
| `requirements` | 文档类      | `references/document-review.md`   |
| `prd`          | 文档类      | `references/document-review.md`   |
| `ux_design`    | 文档类      | `references/document-review.md`   |
| `architecture` | 文档类      | `references/document-review.md`   |
| `stories`      | 文档类      | `references/document-review.md`   |
| `database`     | 文档类      | `references/document-review.md`   |
| `backend`      | 代码类      | `references/code-review.md`       |
| `frontend`     | 代码类      | `references/code-review.md`       |
| `review`       | 代码类      | `references/code-review.md`       |
| `testing`      | 测试类      | `references/testing-review.md`    |
| `deployment`   | 部署类      | `references/deployment-review.md` |

## 自动验证命令

在人工审查之前，先运行自动检查：

| Phase        | 自动检查                                                             |
| ------------ | -------------------------------------------------------------------- |
| requirements | 文件存在 + 非空: `docs/requirements/requirements.md`                 |
| prd          | 文件存在 + 非空: `docs/requirements/prd.md`                          |
| architecture | 文件存在 + 非空: `docs/architecture/system-architecture.md`          |
| stories      | 文件存在 + 非空: `docs/sprints/sprint-plan.md`                       |
| database     | 文件存在: `docs/codemaps/database.md`                                |
| backend      | `uv run ruff check app/` + `uv run pytest --tb=short` (cwd: backend) |
| frontend     | `npm run lint` + `npx tsc --noEmit` (cwd: frontend)                  |
| testing      | 所有测试通过 + 覆盖率 ≥ 80%                                          |
| review       | 无 CRITICAL 级别问题                                                 |
| deployment   | 文件存在: `render.yaml`                                              |

## Review 报告格式

Review 报告保存路径: `docs/reviews/phase-{NN}-{phase_key}.md`

命名规则: `phase-{序号:02d}-{phase_key}.md`，例如 `phase-04-architecture.md`

```markdown
# Phase Review: {phase_name}

**Review 类型**: {文档类/代码类/测试类/部署类}
**执行时间**: {timestamp}
**产出物**: `{output_path}`
**作者**: {author_name} ({author_role})
**审查人**: {reviewer_name} ({reviewer_role})

---

## 自动检查

- ✅/❌ [检查项]: [结果]

## 审查清单

### 通用检查 — 完整性

- ✅ [检查项]: 通过
- ⚠️ [检查项]: 建议优化 — [描述]
- ❌ [检查项]: 必须修复 — [描述]

### {phase_key} 特定检查

- ...

## 发现的问题

| #   | 严重度   | 描述 | 位置      | 建议修复 |
| --- | -------- | ---- | --------- | -------- |
| 1   | CRITICAL | ...  | file:line | ...      |
| 2   | HIGH     | ...  | file:line | ...      |
| 3   | MEDIUM   | ...  | file:line | ...      |

## 结论 (初审)

- 🟢 通过 — 可以进入下一阶段
- 🟡 条件通过 — 有 MEDIUM 问题，建议修复但可继续
- 🔴 阻止 — 有 CRITICAL/HIGH 问题，必须修复后重新 Review

## 统计 (初审)

- 检查项总数: X
- 通过: X | 警告: X | 失败: X

---

## 🔄 Re-Review ({timestamp})

### HIGH 问题修复验证

| #   | 问题 | 修复状态 | 验证     |
| --- | ---- | -------- | -------- |
| 1   | ...  | ✅/❌    | 验证描述 |

### 修复引入的新问题

| #   | 严重度 | 描述     | 建议修复 |
| --- | ------ | -------- | -------- |
| -   | -      | 无 / ... | ...      |

### MEDIUM 问题处理计划

| #   | 问题 | 处理方式              |
| --- | ---- | --------------------- |
| 1   | ...  | → 在 {phase} 阶段解决 |

## Re-Review 结论

- 🟢 通过 / 🔴 仍有问题需继续修复

## 最终统计

- 检查项总数: X
- 通过: X | 待后续: X | 已修复: X
```

## Instructions

1. Read the current phase from `.dev-state.yaml`
2. **Determine the Reviewer** using the Reviewer Assignment Table — Reviewer MUST differ from author
3. Determine the review type using the mapping table
4. Run automatic validations first
5. Load the corresponding checklist from `references/`
6. **Execute strict review** — each checklist item against the phase outputs, being honest and rigorous
7. Generate the review report and **save to** `docs/reviews/phase-{NN}-{phase_key}.md`
8. If HIGH/CRITICAL found:
   a. Author fixes the issues
   b. **Re-Review is mandatory** — verify fixes AND check for newly introduced issues
   c. Append Re-Review results to the same review file
   d. If Re-Review finds new issues, repeat from 8a
9. Update `.dev-state.yaml` with `review` field pointing to the review file
10. Present results to user for confirmation
