# Frontend Templates (Scientific Mirroring v1.0)

本模板库采用 **"科学镜像 (Scientific Mirroring)"** 组织结构。模板目录结构与项目的 `src/` 目录完全对应，旨在提供**路径直觉 (Path Intuition)**，极大降低 AI 生成代码时的路径推断错误。

## 目录结构 (与 src/ 镜像)

```
frontend/
├── features/               # 对应 src/features (按业务功能划分)
│   ├── auth/               # 认证表单套件 (SignIn, SignUp, OTP 等)
│   ├── chat/               # 聊天核心套件 (Interface, Input, Message, useChatStream)
│   ├── landing/            # 营销落地页组件 (Hero, Features, Footer, Navbar)
│   ├── errors/             # 错误页面套件 (404, 500, 403 等)
│   └── examples/           # API 调用示例、通用类型定义模板
├── shared/                 # 对应 src/shared (跨业务共享的基础设施)
│   ├── components/
│   │   ├── ui/             # 原子 UI 组件 (ConfirmDialog, PasswordInput, DataTable 等)
│   │   ├── layout/         # 页面布局容器 (AppSidebar, Header, MainLayout)
│   │   └── navigation/     # 导航交互组件 (ProfileDropdown, CommandMenu, NavProgress)
│   ├── hooks/              # 通用逻辑 Hooks (useTypewriter, useDialogState)
│   └── context/            # 全局上下文 (ThemeProvider)
└── lib/                    # 对应 src/lib
    └── *.ts.template       # 基础库封装 (api-client, handle-server-error)
```

## 核心设计原则

1.  **路径对称性**: 模板位于 `shared/components/ui/`，其在项目中的对应位置即为 `src/shared/components/ui/`。
2.  **唯一职责**:
    - `shared/`: 存放“砖头和水泥”（跨业务的基础设施）。
    - `features/`: 存放“房间”（独立的业务模块）。
3.  **变量标准化**: 统一使用 `{{alias}}` 占位符（默认替换为 `@`），支持全自动 sed 替换。

## 快速使用

### 1. 变量替换

```bash
# 将 {{alias}} 替换为 @
sed 's/{{alias}}/@/g' some-component.tsx.template > some-component.tsx
```

### 2. 让 AI 使用

你可以直接告诉 AI：“参考 `.agent/templates/frontend/features/chat` 实现一个新的聊天窗口”，AI 会自动识别出所有依赖路径。

## 依赖要求

### 必需依赖

```bash
npm install @tanstack/react-table @radix-ui/react-icons lucide-react nanoid
```

### shadcn/ui 组件

确保已安装以下基础组件：

```bash
npx shadcn@latest add button badge separator popover command dropdown-menu select tooltip alert-dialog sidebar avatar collapsible
```

---

_遵循 Bulletproof React 架构规范。_
