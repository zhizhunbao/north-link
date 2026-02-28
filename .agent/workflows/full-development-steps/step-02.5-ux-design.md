# Step 2.5: UX 设计

## 阶段信息

- **阶段**: 2/10 - UX 设计
- **Skill**: `dev-ui_ux_designer`
- **输入**: `docs/requirements/prd.md`
- **产出物**: `docs/design/`

---

## 执行步骤

### 1. 加载上下文

读取并分析：

- `docs/requirements/prd.md` - PRD 文档

提取关键信息：

- 目标用户画像
- 核心功能列表
- 用户故事（User Stories）
- 非功能需求（性能、可用性）

### 2. 加载 Skill

加载 `dev-ui_ux_designer` skill（`.agent/skills/dev-ui_ux_designer/SKILL.md`），获取 UI/UX 设计专业知识。

### 3. 信息架构 (Information Architecture)

基于 PRD 定义信息架构：

1. **页面清单** — 列出所有页面及其功能
2. **导航结构** — 定义页面间的导航关系
3. **内容层级** — 每个页面的信息优先级

```markdown
## 信息架构

### 页面地图 (Sitemap)

- 首页
  - 功能A
  - 功能B
- 用户中心
  - 个人信息
  - 设置

### 导航结构

- 主导航: [页面列表]
- 底部导航: [页面列表]（移动端）
- 面包屑路径: [规则]
```

### 4. 用户流程 (User Flows)

为每个核心用户故事绘制用户流程：

```
[入口] → [步骤1] → [步骤2] → [决策点] → [成功结果]
                                   ↓
                              [错误处理]
```

用 Mermaid 图表记录关键流程。

### 5. 设计系统 (Design System)

参考 skill 中的设计系统指南，定义：

1. **品牌色** — 主色、辅助色、语义色（成功/警告/错误）
2. **字体** — 标题字体、正文字体、等宽字体
3. **间距** — 基于 4px 的间距系统
4. **圆角/阴影** — 统一的视觉风格

### 6. 线框图 (Wireframes)

为核心页面创建线框图：

- 用 ASCII Art 或简单图示描述布局
- 标注组件类型、交互行为
- 注明响应式断点下的布局变化

```
┌──────────────────────────────────┐
│  [Logo]    [Nav]     [User]      │ ← Header
├──────────────────────────────────┤
│                                  │
│   [Hero Section]                 │ ← 主视觉区
│                                  │
├────────────┬─────────────────────┤
│  [Card]    │  [Card]    [Card]   │ ← 内容区
│            │                     │
├────────────┴─────────────────────┤
│  [Footer]                        │ ← Footer
└──────────────────────────────────┘
```

### 7. 交互设计 (Interaction Design)

定义关键交互行为：

- 页面过渡效果
- 按钮反馈（hover/active/loading）
- 表单验证（实时/提交时）
- 加载状态（骨架屏/spinner）
- 空状态设计
- 错误状态设计

### 8. 生成设计文档

创建以下文档：

```
docs/design/
├── information-architecture.md   # 信息架构
├── user-flows.md                 # 用户流程
├── design-system.md              # 设计系统 Token
├── wireframes.md                 # 线框图
└── interaction-design.md         # 交互设计
```

### 9. 用户确认

展示设计文档，请用户确认：

```
[C] 确认 - 设计完整，继续下一阶段
[E] 编辑 - 修改设计
[A] 添加 - 补充更多页面/组件
[S] 简化 - 减少设计范围，MVP 优先
```

---

## 完成检查

- [ ] `docs/design/` 目录已创建
- [ ] 信息架构文档完成
- [ ] 核心用户流程已定义
- [ ] 设计系统 Token 已定义
- [ ] 至少核心页面有线框图
- [ ] 交互设计已定义
- [ ] 用户已确认

## 状态更新

```yaml
phases:
  ux_design:
    status: completed
    completed_at: { current_time }
    output: "docs/design/"
```

## 下一步

→ 进入 `step-03-architecture.md`
