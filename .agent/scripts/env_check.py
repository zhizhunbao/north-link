#!/usr/bin/env python3
"""
Environment Configuration Checker

验证项目所需的环境变量和配置是否正确设置。

Usage:
    python .agent/scripts/env_check.py
    python .agent/scripts/env_check.py --env production
    python .agent/scripts/env_check.py --fix  # 生成 .env.example
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, NamedTuple

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent


class EnvVar(NamedTuple):
    """环境变量定义"""
    name: str
    required: bool
    description: str
    default: str = ""
    sensitive: bool = False


# 环境变量配置
ENV_VARS: Dict[str, List[EnvVar]] = {
    "development": [
        # Application
        EnvVar("ENVIRONMENT", True, "运行环境", "development"),
        EnvVar("DEBUG", False, "调试模式", "true"),
        EnvVar("LOG_LEVEL", False, "日志级别", "INFO"),

        # Database
        EnvVar("DATABASE_URL", True, "数据库连接字符串", "", True),

        # Azure OpenAI
        EnvVar("AZURE_OPENAI_ENDPOINT", True, "Azure OpenAI 端点", "", False),
        EnvVar("AZURE_OPENAI_API_KEY", True, "Azure OpenAI API Key", "", True),
        EnvVar("AZURE_OPENAI_API_VERSION", False, "API 版本", "2024-02-15-preview"),
        EnvVar("AZURE_OPENAI_DEPLOYMENT", False, "部署名称", "gpt-4"),

        # Azure AI Search
        EnvVar("AZURE_SEARCH_ENDPOINT", False, "Azure Search 端点", ""),
        EnvVar("AZURE_SEARCH_API_KEY", False, "Azure Search API Key", "", True),
        EnvVar("AZURE_SEARCH_INDEX", False, "搜索索引名称", "documents"),

        # Azure Storage
        EnvVar("AZURE_STORAGE_CONNECTION_STRING", False, "Storage 连接字符串", "", True),
        EnvVar("AZURE_STORAGE_CONTAINER", False, "Blob 容器名称", "documents"),

        # Azure Entra ID
        EnvVar("AZURE_CLIENT_ID", True, "Azure AD Client ID", ""),
        EnvVar("AZURE_TENANT_ID", True, "Azure AD Tenant ID", ""),

        # Frontend
        EnvVar("VITE_API_URL", False, "后端 API URL", "http://localhost:8000"),
        EnvVar("VITE_AZURE_CLIENT_ID", True, "前端 Azure Client ID", ""),
    ],
    "production": [
        # Production 需要所有变量
        EnvVar("ENVIRONMENT", True, "运行环境", "production"),
        EnvVar("DEBUG", True, "调试模式 (生产必须为 false)", "false"),
        EnvVar("DATABASE_URL", True, "数据库连接字符串", "", True),
        EnvVar("AZURE_OPENAI_ENDPOINT", True, "Azure OpenAI 端点", ""),
        EnvVar("AZURE_OPENAI_API_KEY", True, "Azure OpenAI API Key", "", True),
        EnvVar("AZURE_SEARCH_ENDPOINT", True, "Azure Search 端点", ""),
        EnvVar("AZURE_SEARCH_API_KEY", True, "Azure Search API Key", "", True),
        EnvVar("AZURE_STORAGE_CONNECTION_STRING", True, "Storage 连接字符串", "", True),
        EnvVar("AZURE_CLIENT_ID", True, "Azure AD Client ID", ""),
        EnvVar("AZURE_TENANT_ID", True, "Azure AD Tenant ID", ""),
    ],
}


def check_env_vars(env_type: str = "development") -> Dict[str, any]:
    """检查环境变量"""
    vars_to_check = ENV_VARS.get(env_type, ENV_VARS["development"])
    results = {
        "passed": [],
        "failed": [],
        "warnings": [],
    }

    print(f"\n🔍 Checking environment variables for: {env_type}\n")
    print("-" * 60)

    for var in vars_to_check:
        value = os.environ.get(var.name, "")
        has_value = bool(value)

        if var.required and not has_value:
            results["failed"].append(var)
            status = "❌ MISSING"
        elif not var.required and not has_value:
            results["warnings"].append(var)
            status = "⚠️  NOT SET"
        else:
            results["passed"].append(var)
            # 隐藏敏感值
            display_value = "****" if var.sensitive else value[:30] + "..." if len(value) > 30 else value
            status = f"✅ {display_value}"

        print(f"{var.name:40} {status}")

    print("-" * 60)
    return results


def print_summary(results: Dict) -> bool:
    """打印摘要"""
    passed = len(results["passed"])
    failed = len(results["failed"])
    warnings = len(results["warnings"])

    print(f"\n📊 Summary:")
    print(f"   ✅ Passed:   {passed}")
    print(f"   ❌ Failed:   {failed}")
    print(f"   ⚠️  Warnings: {warnings}")

    if failed > 0:
        print(f"\n❌ Missing required variables:")
        for var in results["failed"]:
            print(f"   - {var.name}: {var.description}")
        return False

    if warnings > 0:
        print(f"\n⚠️  Optional variables not set:")
        for var in results["warnings"]:
            print(f"   - {var.name}: {var.description}")

    print(f"\n✅ Environment check {'passed' if failed == 0 else 'FAILED'}!")
    return failed == 0


def generate_env_example(env_type: str = "development") -> None:
    """生成 .env.example 文件"""
    vars_to_include = ENV_VARS.get(env_type, ENV_VARS["development"])

    content = f"""# Environment Configuration
# Generated for: {env_type}
# Copy this file to .env and fill in the values

"""

    current_section = ""
    for var in vars_to_include:
        # 根据变量名推断分组
        if var.name.startswith("AZURE_OPENAI"):
            section = "Azure OpenAI"
        elif var.name.startswith("AZURE_SEARCH"):
            section = "Azure AI Search"
        elif var.name.startswith("AZURE_STORAGE"):
            section = "Azure Storage"
        elif var.name.startswith("AZURE_") or var.name.startswith("VITE_AZURE"):
            section = "Azure Entra ID"
        elif var.name.startswith("DATABASE"):
            section = "Database"
        elif var.name.startswith("VITE_"):
            section = "Frontend"
        else:
            section = "Application"

        if section != current_section:
            content += f"\n# {section}\n"
            current_section = section

        required = "(required)" if var.required else "(optional)"
        content += f"# {var.description} {required}\n"
        content += f"{var.name}={var.default}\n"

    # 写入文件
    backend_env = PROJECT_ROOT / "backend" / ".env.example"
    backend_env.write_text(content)
    print(f"✅ Generated: {backend_env}")

    # 为前端生成单独的文件
    frontend_vars = [v for v in vars_to_include if v.name.startswith("VITE_")]
    if frontend_vars:
        frontend_content = "# Frontend Environment\n\n"
        for var in frontend_vars:
            frontend_content += f"# {var.description}\n"
            frontend_content += f"{var.name}={var.default}\n"

        frontend_env = PROJECT_ROOT / "frontend" / ".env.example"
        frontend_env.write_text(frontend_content)
        print(f"✅ Generated: {frontend_env}")


def check_files() -> None:
    """检查必要的配置文件"""
    print("\n📁 Checking configuration files:\n")

    files_to_check = [
        ("backend/.env", "后端环境配置"),
        ("backend/pyproject.toml", "Python 项目配置"),
        ("frontend/.env", "前端环境配置"),
        ("frontend/package.json", "Node.js 项目配置"),
    ]

    for file_path, description in files_to_check:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}: {description}")
        else:
            print(f"   ❌ {file_path}: {description} (MISSING)")


def main():
    parser = argparse.ArgumentParser(description="Environment Configuration Checker")
    parser.add_argument(
        "--env", "-e",
        choices=["development", "production"],
        default="development",
        help="Environment type to check"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Generate .env.example file"
    )
    parser.add_argument(
        "--files",
        action="store_true",
        help="Also check configuration files"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("🔧 Environment Configuration Checker")
    print("=" * 60)

    if args.fix:
        generate_env_example(args.env)
        return

    results = check_env_vars(args.env)

    if args.files:
        check_files()

    success = print_summary(results)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
