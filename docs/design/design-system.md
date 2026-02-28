# North Link 跨境货源通 — 设计系统

> 版本: V1.0 | 更新时间: 2026-02-28 | 作者: Bella (UI/UX Designer)

## 1. 品牌色

### 主色 — 北极蓝 (Arctic Blue)

寓意跨境、信任、专业。加拿大冰蓝 + 科技感。

```css
:root {
  /* Primary - Arctic Blue */
  --color-primary: hsl(210, 85%, 52%);
  --color-primary-light: hsl(210, 85%, 66%);
  --color-primary-dark: hsl(210, 85%, 38%);
  --color-primary-bg: hsl(210, 85%, 96%);

  /* Accent - Maple Gold */
  --color-accent: hsl(38, 90%, 55%);
  --color-accent-light: hsl(38, 90%, 70%);
  --color-accent-dark: hsl(38, 90%, 42%);

  /* Semantic */
  --color-success: hsl(152, 70%, 42%);
  --color-success-bg: hsl(152, 70%, 95%);
  --color-warning: hsl(38, 90%, 50%);
  --color-warning-bg: hsl(38, 90%, 95%);
  --color-danger: hsl(0, 75%, 55%);
  --color-danger-bg: hsl(0, 75%, 96%);

  /* Profit Indicators */
  --color-profit-high: hsl(152, 70%, 42%); /* 绿 - 高利润 */
  --color-profit-medium: hsl(38, 90%, 50%); /* 金 - 一般 */
  --color-profit-low: hsl(0, 75%, 55%); /* 红 - 不推荐 */
}
```

### 浅色主题 & 深色主题

```css
:root {
  /* Light Theme (Default) */
  --color-bg: hsl(216, 25%, 97%);
  --color-surface: hsl(0, 0%, 100%);
  --color-surface-elevated: hsl(0, 0%, 100%);
  --color-border: hsl(216, 20%, 90%);
  --color-border-subtle: hsl(216, 15%, 93%);
  --color-text: hsl(216, 25%, 12%);
  --color-text-secondary: hsl(216, 12%, 48%);
  --color-text-tertiary: hsl(216, 8%, 65%);
}

[data-theme="dark"] {
  --color-bg: hsl(216, 25%, 7%);
  --color-surface: hsl(216, 20%, 11%);
  --color-surface-elevated: hsl(216, 20%, 14%);
  --color-border: hsl(216, 15%, 20%);
  --color-border-subtle: hsl(216, 12%, 16%);
  --color-text: hsl(216, 15%, 92%);
  --color-text-secondary: hsl(216, 10%, 58%);
  --color-text-tertiary: hsl(216, 8%, 42%);
}
```

## 2. 字体

```css
:root {
  /* 标题 - Outfit: 现代、几何感、易读 */
  --font-display: "Outfit", system-ui, sans-serif;

  /* 正文 - Inter: 专业、清晰、支持中文 fallback */
  --font-sans: "Inter", "PingFang SC", "Microsoft YaHei", system-ui, sans-serif;

  /* 数字/代码 - JetBrains Mono: 等宽、清晰区分数字 */
  --font-mono: "JetBrains Mono", "Fira Code", monospace;

  /* Font Sizes */
  --text-xs: 0.75rem; /* 12px */
  --text-sm: 0.875rem; /* 14px */
  --text-base: 1rem; /* 16px */
  --text-lg: 1.125rem; /* 18px */
  --text-xl: 1.25rem; /* 20px */
  --text-2xl: 1.5rem; /* 24px */
  --text-3xl: 1.875rem; /* 30px */
  --text-4xl: 2.25rem; /* 36px */

  /* Font Weights */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* Line Heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
}
```

### 字体用途规则

| 场景          | 字体             | 大小          | 粗细              |
| ------------- | ---------------- | ------------- | ----------------- |
| 页面标题      | `--font-display` | `--text-3xl`  | `--font-bold`     |
| 卡片标题      | `--font-display` | `--text-xl`   | `--font-semibold` |
| 正文          | `--font-sans`    | `--text-base` | `--font-normal`   |
| 小字/标签     | `--font-sans`    | `--text-sm`   | `--font-medium`   |
| 价格/利润数字 | `--font-mono`    | `--text-xl`   | `--font-bold`     |
| 元数据        | `--font-sans`    | `--text-xs`   | `--font-normal`   |

## 3. 间距

```css
:root {
  /* 基于 4px 的间距系统 */
  --space-0: 0;
  --space-1: 0.25rem; /* 4px */
  --space-2: 0.5rem; /* 8px */
  --space-3: 0.75rem; /* 12px */
  --space-4: 1rem; /* 16px */
  --space-5: 1.25rem; /* 20px */
  --space-6: 1.5rem; /* 24px */
  --space-8: 2rem; /* 32px */
  --space-10: 2.5rem; /* 40px */
  --space-12: 3rem; /* 48px */
  --space-16: 4rem; /* 64px */
}
```

### 间距使用规则

| 场景           | 间距                       |
| -------------- | -------------------------- |
| 组件内 padding | `--space-4` ~ `--space-6`  |
| 元素间距       | `--space-3` ~ `--space-4`  |
| 卡片间距       | `--space-4` ~ `--space-6`  |
| 页面边距       | `--space-6` ~ `--space-8`  |
| 区域分隔       | `--space-8` ~ `--space-12` |

## 4. 圆角与阴影

```css
:root {
  /* Radius */
  --radius-sm: 0.375rem; /* 6px - 标签、小按钮 */
  --radius-md: 0.5rem; /* 8px - 输入框、按钮 */
  --radius-lg: 0.75rem; /* 12px - 卡片 */
  --radius-xl: 1rem; /* 16px - 大卡片、模态 */
  --radius-2xl: 1.5rem; /* 24px - 特殊容器 */
  --radius-full: 9999px; /* 圆形 - 头像、标签 */

  /* Shadows */
  --shadow-xs: 0 1px 2px hsl(216 25% 0% / 0.04);
  --shadow-sm:
    0 1px 3px hsl(216 25% 0% / 0.06), 0 1px 2px hsl(216 25% 0% / 0.04);
  --shadow-md:
    0 4px 6px hsl(216 25% 0% / 0.06), 0 2px 4px hsl(216 25% 0% / 0.04);
  --shadow-lg:
    0 10px 20px hsl(216 25% 0% / 0.08), 0 4px 8px hsl(216 25% 0% / 0.04);
  --shadow-xl:
    0 20px 40px hsl(216 25% 0% / 0.1), 0 8px 16px hsl(216 25% 0% / 0.04);

  /* Transitions */
  --transition-fast: 150ms ease-out;
  --transition-normal: 200ms ease-out;
  --transition-slow: 300ms ease-out;
}
```

## 5. 组件基础样式

### 5.1 按钮

```
Primary:    背景 primary + 白色文字     → CTA 按钮（一键计算、发货下单）
Secondary:  边框 primary + primary文字  → 次要按钮（筛选、导出）
Ghost:      无边框 + text-secondary     → 辅助操作（取消、返回）
Danger:     背景 danger + 白色文字      → 破坏性操作（删除）
```

### 5.2 卡片

```
背景:       var(--color-surface)
圆角:       var(--radius-lg)
阴影:       var(--shadow-sm)
内边距:     var(--space-5)
Hover:      shadow-md + translateY(-2px)
```

### 5.3 输入框

```
背景:       var(--color-surface)
边框:       1px solid var(--color-border)
圆角:       var(--radius-md)
内边距:     var(--space-3) var(--space-4)
Focus:      border-color: var(--color-primary) + ring
```

### 5.4 利润指示器

```
高利润 (≥30%):  背景 success-bg + 文字 success + ▲ 图标
一般 (15-30%):  背景 warning-bg + 文字 warning + ● 图标
低/亏损 (<15%): 背景 danger-bg + 文字 danger + ▼ 图标
```
