# North Link 跨境货源通 — 交互设计

> 版本: V1.0 | 更新时间: 2026-02-28 | 作者: Bella (UI/UX Designer)

## 1. 页面过渡

### 1.1 路由切换

```css
/* 页面进入 */
.page-enter {
  animation: pageIn 0.3s ease-out;
}

@keyframes pageIn {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 侧边栏高亮切换 */
.nav-item.active {
  background: var(--color-primary-bg);
  color: var(--color-primary);
  transition: all var(--transition-normal);
}
```

### 1.2 列表加载

- **首次加载**: 骨架屏 → 从上到下依次 fadeIn（每项间隔 50ms）
- **翻页/筛选**: 列表区域淡出 → 加载 → 淡入（整体 200ms）
- **下拉刷新** (移动端): 拉下弹性动画 → spinner → 内容更新

## 2. 按钮反馈

```css
/* Primary 按钮 */
.btn-primary {
  background: var(--color-primary);
  color: white;
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-6);
  font-weight: var(--font-semibold);
  transition: all var(--transition-normal);
  cursor: pointer;
}

.btn-primary:hover {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-primary:active {
  transform: translateY(0);
  box-shadow: var(--shadow-xs);
}

/* Loading 状态 */
.btn-primary.loading {
  pointer-events: none;
  opacity: 0.75;
}
.btn-primary.loading::after {
  content: "";
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-left: var(--space-2);
}
```

## 3. 卡片交互

```css
/* 推荐商品卡片 */
.product-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-subtle);
  transition: all var(--transition-normal);
  cursor: pointer;
}

.product-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
  border-color: var(--color-primary-light);
}

/* 利润指示条 */
.profit-bar {
  height: 4px;
  border-radius: var(--radius-full);
  background: var(--color-border);
  overflow: hidden;
}

.profit-bar-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 0.8s ease-out;
  /* 颜色根据利润率动态设置 */
}
```

## 4. 表单验证

### 4.1 验证时机

| 场景         | 验证时机        | 反馈方式              |
| ------------ | --------------- | --------------------- |
| 必填字段     | blur + submit   | 红色边框 + 错误文字   |
| 价格输入     | 实时 (onChange) | 自动格式化 + 范围检查 |
| 商户选择     | submit          | 高亮未选择的下拉框    |
| 手动录入价格 | blur            | 校验数字格式          |

### 4.2 样式

```css
/* 错误状态 */
.input-error {
  border-color: var(--color-danger);
  background: var(--color-danger-bg);
}

.input-error-text {
  color: var(--color-danger);
  font-size: var(--text-sm);
  margin-top: var(--space-1);
  animation: shakeIn 0.3s ease-out;
}

@keyframes shakeIn {
  0%,
  100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-4px);
  }
  75% {
    transform: translateX(4px);
  }
}
```

## 5. 加载状态

### 5.1 骨架屏 (Skeleton)

用于首次页面加载、数据表格加载。

```css
.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-border-subtle) 25%,
    var(--color-border) 50%,
    var(--color-border-subtle) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
  border-radius: var(--radius-md);
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}
```

### 5.2 加载状态映射

| 场景          | 加载样式     | 时长 |
| ------------- | ------------ | ---- |
| 页面首次加载  | 骨架屏       | ≤2s  |
| 利润计算      | 按钮 spinner | ≤3s  |
| 列表筛选/翻页 | 列表区域淡出 | ≤1s  |
| 发货下单提交  | 全屏 overlay | ≤5s  |
| 物流状态刷新  | 区域 spinner | ≤2s  |

## 6. 空状态设计

| 页面       | 空状态文案                      | CTA 按钮           |
| ---------- | ------------------------------- | ------------------ |
| 推荐列表   | 📊 暂无推荐，数据更新中...      | 进入比价中心手动找 |
| 商品收藏   | ⭐ 还没有收藏商品               | 去比价中心看看     |
| 商户列表   | 👥 还没有添加商户               | 添加第一个商户     |
| 物流跟踪   | 🚚 暂无在途订单                 | 去发货             |
| 订单列表   | 📦 还没有订单记录               | 创建第一笔订单     |
| 搜索无结果 | 🔍 没找到相关商品，换个关键词？ | 清除筛选条件       |

## 7. 错误状态设计

### Toast 通知

```
位置: 右上角
自动消失: 3秒 (成功) / 5秒 (错误)
样式:
  ✅ 成功: 绿色左边框 + success 背景
  ❌ 错误: 红色左边框 + danger 背景
  ⚠️ 警告: 金色左边框 + warning 背景
  ℹ️ 信息: 蓝色左边框 + primary 背景
```

### 全局错误

```
网络断开:  顶部横幅 "网络连接已断开，请检查网络" + 重试按钮
服务器错误: 页面中心 "服务暂时不可用，请稍后重试" + 重试
403:       "无权访问此页面" + 返回首页
404:       "页面走丢了" + 返回首页
```

## 8. 关键微交互

| 交互             | 动画                    | 时长  |
| ---------------- | ----------------------- | ----- |
| 利润数字更新     | 数字翻转动画 (countUp)  | 600ms |
| 收藏星标点亮     | 缩放弹跳 + 填充色过渡   | 300ms |
| 风险等级指示     | 圆点依次亮起            | 400ms |
| 物流时间线节点   | 脉冲动画 (当前节点)     | 持续  |
| 利润颜色条       | 从左到右填充            | 800ms |
| 侧边栏折叠/展开  | 宽度过渡 + 文字淡入淡出 | 300ms |
| 移动端底部栏切换 | 图标缩放 + 颜色过渡     | 200ms |

## 9. 可访问性规范

### 9.1 目标

- **WCAG 2.1 AA** 级别合规
- 面向非技术用户（宝妈、个体货源商），易用性优先

### 9.2 键盘导航

| 操作       | 按键                | 说明                          |
| ---------- | ------------------- | ----------------------------- |
| 导航切换   | `Tab` / `Shift+Tab` | 所有可交互元素可通过 Tab 聚焦 |
| 确认操作   | `Enter` / `Space`   | 按钮、链接、下拉选择          |
| 关闭弹窗   | `Escape`            | Modal、抽屉、下拉关闭         |
| 表格行选择 | `↑` `↓`             | 商品列表、商户列表行间导航    |

### 9.3 ARIA 标注规范

```html
<!-- 利润指标卡片 -->
<div role="status" aria-label="今日利润 3200 元，利润率 21%，低风险">
  <!-- 风险等级 -->
  <span role="img" aria-label="低风险" class="risk-indicator risk-low">🟢</span>

  <!-- 侧边栏导航 -->
  <nav aria-label="主导航">
    <a href="/dashboard" aria-current="page">仪表盘</a>
  </nav>

  <!-- 数据表格 -->
  <table aria-label="商品比价列表">
    <th scope="col">商品名称</th>
  </table>

  <!-- 表单 -->
  <input id="cost" aria-label="加拿大成本" aria-required="true" />
  <span role="alert" aria-live="polite">请输入有效金额</span>
</div>
```

### 9.4 颜色与对比度

| 元素   | 前景         | 背景    | 对比度 | 达标           |
| ------ | ------------ | ------- | ------ | -------------- |
| 正文   | #1a1a2e      | #ffffff | 16.7:1 | ✅ AAA         |
| 利润绿 | #10b981 文字 | #ecfdf5 | 4.6:1  | ✅ AA          |
| 警告红 | #ef4444 文字 | #fef2f2 | 4.5:1  | ✅ AA          |
| 禁用态 | #9ca3af      | #f3f4f6 | 3.1:1  | ⚠️ 仅大文本 AA |

> 所有功能信息不可仅依赖颜色传达。利润指标同时使用颜色 + 文字（🟢低风险/🟡中风险/🔴高风险）+ 数值。

### 9.5 焦点管理

- 弹窗打开时焦点移至弹窗第一个可交互元素
- 弹窗关闭后焦点返回触发元素
- 页面跳转后焦点移至 `<h1>` 或主要内容区域
- 焦点环（focus ring）使用 `2px solid var(--color-primary)` + `2px offset`，不可隐藏
