#!/usr/bin/env python3
"""
Test Coverage Report Generator

生成项目的测试覆盖率报告，支持后端和前端。

Usage:
    python .agent/scripts/coverage_report.py
    python .agent/scripts/coverage_report.py --backend
    python .agent/scripts/coverage_report.py --frontend
    python .agent/scripts/coverage_report.py --threshold 80
"""

import argparse
import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent


def run_command(cmd: list, cwd: Path) -> tuple[int, str, str]:
    """运行命令并返回结果"""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def run_backend_coverage() -> Optional[Dict]:
    """运行后端测试覆盖率"""
    print("\n🐍 Running backend tests with coverage...")

    backend_dir = PROJECT_ROOT / "backend"

    # 运行 pytest with coverage
    cmd = ["uv", "run", "pytest", "--cov=app", "--cov-report=json", "--cov-report=term", "-q"]
    returncode, stdout, stderr = run_command(cmd, backend_dir)

    print(stdout)
    if returncode != 0:
        print(f"❌ Backend tests failed:\n{stderr}")
        return None

    # 读取覆盖率报告
    coverage_file = backend_dir / "coverage.json"
    if coverage_file.exists():
        with open(coverage_file, "r") as f:
            return json.load(f)

    return None


def run_frontend_coverage() -> Optional[Dict]:
    """运行前端测试覆盖率"""
    print("\n⚛️  Running frontend tests with coverage...")

    frontend_dir = PROJECT_ROOT / "frontend"

    # 运行 vitest with coverage
    cmd = ["npm", "run", "test", "--", "--run", "--coverage"]
    returncode, stdout, stderr = run_command(cmd, frontend_dir)

    print(stdout)
    if returncode != 0:
        print(f"❌ Frontend tests failed:\n{stderr}")
        return None

    # 读取覆盖率报告
    coverage_file = frontend_dir / "coverage" / "coverage-summary.json"
    if coverage_file.exists():
        with open(coverage_file, "r") as f:
            return json.load(f)

    return None


def parse_backend_coverage(data: Dict) -> Dict:
    """解析后端覆盖率数据"""
    totals = data.get("totals", {})
    return {
        "lines": totals.get("percent_covered", 0),
        "statements": totals.get("percent_covered", 0),
        "branches": totals.get("percent_covered_display", "N/A"),
        "functions": "N/A",
    }


def parse_frontend_coverage(data: Dict) -> Dict:
    """解析前端覆盖率数据"""
    total = data.get("total", {})
    return {
        "lines": total.get("lines", {}).get("pct", 0),
        "statements": total.get("statements", {}).get("pct", 0),
        "branches": total.get("branches", {}).get("pct", 0),
        "functions": total.get("functions", {}).get("pct", 0),
    }


def print_coverage_table(backend: Optional[Dict], frontend: Optional[Dict]) -> None:
    """打印覆盖率表格"""
    print("\n" + "=" * 60)
    print("📊 Coverage Report")
    print("=" * 60)

    print("\n{:<20} {:>15} {:>15}".format("Metric", "Backend", "Frontend"))
    print("-" * 50)

    metrics = ["lines", "statements", "branches", "functions"]

    for metric in metrics:
        backend_val = f"{backend.get(metric, 'N/A')}%" if backend else "N/A"
        frontend_val = f"{frontend.get(metric, 'N/A')}%" if frontend else "N/A"

        if isinstance(backend_val, (int, float)):
            backend_val = f"{backend_val:.1f}%"
        if isinstance(frontend_val, (int, float)):
            frontend_val = f"{frontend_val:.1f}%"

        print("{:<20} {:>15} {:>15}".format(metric.capitalize(), backend_val, frontend_val))


def check_threshold(
    backend: Optional[Dict],
    frontend: Optional[Dict],
    threshold: int,
) -> bool:
    """检查是否满足覆盖率阈值"""
    passed = True

    print(f"\n🎯 Threshold: {threshold}%")
    print("-" * 30)

    if backend:
        backend_lines = backend.get("lines", 0)
        if backend_lines < threshold:
            print(f"❌ Backend: {backend_lines:.1f}% < {threshold}%")
            passed = False
        else:
            print(f"✅ Backend: {backend_lines:.1f}% >= {threshold}%")

    if frontend:
        frontend_lines = frontend.get("lines", 0)
        if frontend_lines < threshold:
            print(f"❌ Frontend: {frontend_lines:.1f}% < {threshold}%")
            passed = False
        else:
            print(f"✅ Frontend: {frontend_lines:.1f}% >= {threshold}%")

    return passed


def main():
    parser = argparse.ArgumentParser(description="Test Coverage Report Generator")
    parser.add_argument(
        "--backend",
        action="store_true",
        help="Run backend coverage only"
    )
    parser.add_argument(
        "--frontend",
        action="store_true",
        help="Run frontend coverage only"
    )
    parser.add_argument(
        "--threshold", "-t",
        type=int,
        default=0,
        help="Minimum coverage threshold (exit 1 if below)"
    )

    args = parser.parse_args()

    # 如果没有指定，运行两者
    run_both = not args.backend and not args.frontend

    backend_coverage = None
    frontend_coverage = None

    if args.backend or run_both:
        raw_data = run_backend_coverage()
        if raw_data:
            backend_coverage = parse_backend_coverage(raw_data)

    if args.frontend or run_both:
        raw_data = run_frontend_coverage()
        if raw_data:
            frontend_coverage = parse_frontend_coverage(raw_data)

    # 打印报告
    print_coverage_table(backend_coverage, frontend_coverage)

    # 检查阈值
    if args.threshold > 0:
        passed = check_threshold(backend_coverage, frontend_coverage, args.threshold)
        if not passed:
            print(f"\n❌ Coverage below threshold!")
            sys.exit(1)

    print("\n✅ Coverage report complete!")


if __name__ == "__main__":
    main()
