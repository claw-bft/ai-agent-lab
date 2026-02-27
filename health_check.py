#!/usr/bin/env python3
"""
AI Agent Lab - 项目健康检查脚本
快速检查项目关键指标
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

def run_command(cmd, cwd=None, timeout=10):
    """运行shell命令"""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd,
            capture_output=True, text=True, timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except:
        return False, "", ""

def main():
    project_root = Path(__file__).parent.absolute()
    
    print("🤖 AI Agent Lab Health Check")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # Python文件统计
    py_files = [f for f in project_root.rglob("*.py") if "__pycache__" not in str(f)]
    print(f"📦 Python files: {len(py_files)}")
    
    # 代码行数
    total_lines = sum(len(open(f, 'r', errors='ignore').readlines()) for f in py_files)
    print(f"📝 Lines of code: {total_lines:,}")
    
    # 测试文件
    test_files = list(project_root.rglob("test_*.py")) + list(project_root.rglob("*_test.py"))
    print(f"🧪 Test files: {len(test_files)}")
    
    # SKILL.md文件
    skill_md_files = list(project_root.rglob("SKILL.md"))
    print(f"📚 SKILL.md files: {len(skill_md_files)}")
    
    # Git状态
    success, branch, _ = run_command("git branch --show-current", cwd=project_root)
    if success:
        print(f"🌿 Git branch: {branch.strip()}")
    
    # 最近提交
    success, commit, _ = run_command("git log -1 --oneline", cwd=project_root)
    if success:
        print(f"📌 Latest commit: {commit.strip()}")
    
    print("-" * 50)
    print("✅ Health check completed!")

if __name__ == "__main__":
    main()
