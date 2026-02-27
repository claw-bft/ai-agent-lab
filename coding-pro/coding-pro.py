#!/usr/bin/env python3
"""
Coding Pro 核心实现
程序员专业技能包 - 智能编码、版本协作、DevOps自动化
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

def generate_code(prompt: str, output_dir: str, language: str = "python") -> Dict[str, Any]:
    """
    代码生成 - 根据自然语言描述生成代码
    
    Args:
        prompt: 代码描述
        output_dir: 输出目录
        language: 编程语言
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 生成项目结构
    structure = generate_project_structure(prompt, language)
    
    # 创建文件
    created_files = []
    for file_info in structure.get("files", []):
        file_path = output_path / file_info["path"]
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_info["content"])
        
        created_files.append(str(file_path))
    
    # 创建README
    readme_path = output_path / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(f"# {structure.get('name', 'Generated Project')}\n\n")
        f.write(f"## 描述\n\n{prompt}\n\n")
        f.write(f"## 文件结构\n\n")
        for filepath in created_files:
            f.write(f"- {os.path.basename(filepath)}\n")
    
    return {
        "success": True,
        "prompt": prompt,
        "language": language,
        "output_dir": str(output_path),
        "files_created": created_files,
        "structure": structure
    }

def generate_project_structure(prompt: str, language: str) -> Dict[str, Any]:
    """根据提示生成项目结构"""
    
    # 根据提示关键词推断项目类型
    prompt_lower = prompt.lower()
    
    if "api" in prompt_lower or "fastapi" in prompt_lower or "flask" in prompt_lower:
        return generate_api_project(prompt, language)
    elif "cli" in prompt_lower or "command" in prompt_lower:
        return generate_cli_project(prompt, language)
    elif "web" in prompt_lower or "website" in prompt_lower:
        return generate_web_project(prompt, language)
    else:
        return generate_generic_project(prompt, language)

def generate_api_project(prompt: str, language: str) -> Dict[str, Any]:
    """生成API项目结构"""
    return {
        "name": "API Service",
        "files": [
            {
                "path": "main.py",
                "content": '''#!/usr/bin/env python3
"""
API服务 - 由Coding Pro生成
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="API Service", version="1.0.0")

class Item(BaseModel):
    name: str
    description: str = None

@app.get("/")
def read_root():
    return {"message": "Welcome to API Service"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.post("/items/")
def create_item(item: Item):
    return item

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
            },
            {
                "path": "requirements.txt",
                "content": "fastapi\nuvicorn\npydantic\n"
            },
            {
                "path": "Dockerfile",
                "content": '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
'''
            }
        ]
    }

def generate_cli_project(prompt: str, language: str) -> Dict[str, Any]:
    """生成CLI项目结构"""
    return {
        "name": "CLI Tool",
        "files": [
            {
                "path": "cli.py",
                "content": '''#!/usr/bin/env python3
"""
CLI工具 - 由Coding Pro生成
"""

import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="CLI Tool")
    parser.add_argument("--version", action="version", version="1.0.0")
    
    subparsers = parser.add_subparsers(dest="command")
    
    # 添加子命令
    cmd = subparsers.add_parser("hello", help="Say hello")
    cmd.add_argument("--name", default="World", help="Name to greet")
    
    args = parser.parse_args()
    
    if args.command == "hello":
        print(f"Hello, {args.name}!")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
'''
            },
            {
                "path": "setup.py",
                "content": '''from setuptools import setup, find_packages

setup(
    name="cli-tool",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "cli-tool=cli:main",
        ],
    },
)
'''
            }
        ]
    }

def generate_web_project(prompt: str, language: str) -> Dict[str, Any]:
    """生成Web项目结构"""
    return {
        "name": "Web Application",
        "files": [
            {
                "path": "index.html",
                "content": '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Application</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Web Application</h1>
        <p>由Coding Pro生成的Web应用</p>
    </div>
</body>
</html>
'''
            },
            {
                "path": "style.css",
                "content": '''/* 样式文件 */
body {
    background-color: #f5f5f5;
    color: #333;
}
'''
            },
            {
                "path": "app.js",
                "content": '''// JavaScript入口
console.log("Web Application loaded");
'''
            }
        ]
    }

def generate_generic_project(prompt: str, language: str) -> Dict[str, Any]:
    """生成通用项目结构"""
    return {
        "name": "Generated Project",
        "files": [
            {
                "path": "main.py",
                "content": f'''#!/usr/bin/env python3
"""
{prompt}
由Coding Pro生成
"""

def main():
    print("Hello from generated project!")
    print(f"Prompt: {prompt}")

if __name__ == "__main__":
    main()
'''
            },
            {
                "path": "README.md",
                "content": f"# Generated Project\n\n{prompt}\n"
            }
        ]
    }

def review_code(path: str, rules: List[str]) -> Dict[str, Any]:
    """
    代码审查
    
    Args:
        path: 代码路径
        rules: 审查规则 (security/performance/style)
    """
    target_path = Path(path)
    
    if not target_path.exists():
        return {
            "success": False,
            "error": f"路径不存在: {path}"
        }
    
    findings = []
    files_reviewed = 0
    
    # 遍历所有Python文件
    for file_path in target_path.rglob("*.py"):
        files_reviewed += 1
        content = file_path.read_text(encoding='utf-8')
        
        file_findings = []
        
        # 安全检查
        if "security" in rules:
            security_issues = check_security_issues(content)
            file_findings.extend(security_issues)
        
        # 性能检查
        if "performance" in rules:
            perf_issues = check_performance_issues(content)
            file_findings.extend(perf_issues)
        
        # 风格检查
        if "style" in rules:
            style_issues = check_style_issues(content)
            file_findings.extend(style_issues)
        
        if file_findings:
            findings.append({
                "file": str(file_path),
                "issues": file_findings
            })
    
    return {
        "success": True,
        "path": path,
        "rules": rules,
        "files_reviewed": files_reviewed,
        "total_issues": sum(len(f["issues"]) for f in findings),
        "findings": findings
    }

def check_security_issues(content: str) -> List[Dict]:
    """检查安全问题"""
    issues = []
    
    # 检查硬编码密码
    if "password" in content.lower() and "=" in content:
        issues.append({
            "type": "security",
            "severity": "high",
            "message": "可能存在硬编码密码"
        })
    
    # 检查SQL注入风险
    if "execute(" in content and "%" in content:
        issues.append({
            "type": "security",
            "severity": "medium",
            "message": "可能存在SQL注入风险"
        })
    
    return issues

def check_performance_issues(content: str) -> List[Dict]:
    """检查性能问题"""
    issues = []
    
    # 检查循环中的数据库查询
    if "for" in content and "query" in content.lower():
        issues.append({
            "type": "performance",
            "severity": "medium",
            "message": "循环中可能存在数据库查询，考虑使用批量查询"
        })
    
    return issues

def check_style_issues(content: str) -> List[Dict]:
    """检查风格问题"""
    issues = []
    
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if len(line) > 100:
            issues.append({
                "type": "style",
                "line": i,
                "severity": "low",
                "message": f"行长度超过100字符 ({len(line)}字符)"
            })
    
    return issues

def setup_cicd(template: str, provider: str) -> Dict[str, Any]:
    """
    配置CI/CD流水线
    
    Args:
        template: 项目模板 (python/node/go)
        provider: CI/CD提供商 (github-actions/gitlab-ci)
    """
    if provider == "github-actions":
        return setup_github_actions(template)
    elif provider == "gitlab-ci":
        return setup_gitlab_ci(template)
    else:
        return {
            "success": False,
            "error": f"不支持的CI/CD提供商: {provider}"
        }

def setup_github_actions(template: str) -> Dict[str, Any]:
    """配置GitHub Actions"""
    
    workflow_dir = Path(".github/workflows")
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    if template == "python":
        workflow_content = '''name: Python CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest tests/ -v
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
'''
    elif template == "node":
        workflow_content = '''name: Node.js CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [18.x, 20.x]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run tests
      run: npm test
    
    - name: Build
      run: npm run build
'''
    else:
        workflow_content = f'''name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run tests
      run: echo "Add your test commands here"
'''
    
    workflow_file = workflow_dir / "ci.yml"
    with open(workflow_file, 'w') as f:
        f.write(workflow_content)
    
    return {
        "success": True,
        "provider": "github-actions",
        "template": template,
        "workflow_file": str(workflow_file),
        "message": f"已创建GitHub Actions工作流: {workflow_file}"
    }

def setup_gitlab_ci(template: str) -> Dict[str, Any]:
    """配置GitLab CI"""
    
    if template == "python":
        ci_content = '''stages:
  - test
  - build
  - deploy

test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pytest tests/ -v
  only:
    - merge_requests
    - main

build:
  stage: build
  script:
    - echo "Building..."
  only:
    - main
'''
    else:
        ci_content = '''stages:
  - test
  - build
  - deploy

test:
  stage: test
  script:
    - echo "Running tests..."
  only:
    - merge_requests
    - main
'''
    
    ci_file = Path(".gitlab-ci.yml")
    with open(ci_file, 'w') as f:
        f.write(ci_content)
    
    return {
        "success": True,
        "provider": "gitlab-ci",
        "template": template,
        "ci_file": str(ci_file),
        "message": f"已创建GitLab CI配置: {ci_file}"
    }

def main():
    parser = argparse.ArgumentParser(description="Coding Pro - 程序员专业技能包")
    parser.add_argument("command", choices=["generate", "review", "cicd"])
    parser.add_argument("--prompt", help="代码生成描述")
    parser.add_argument("--output", default="./generated", help="输出目录")
    parser.add_argument("--language", default="python", help="编程语言")
    parser.add_argument("--path", help="代码路径")
    parser.add_argument("--rules", default="security,performance", help="审查规则")
    parser.add_argument("--template", default="python", help="项目模板")
    parser.add_argument("--provider", default="github-actions", help="CI/CD提供商")
    parser.add_argument("--json", action="store_true", help="JSON格式输出")
    
    args = parser.parse_args()
    
    if args.command == "generate":
        if not args.prompt:
            print("✗ 错误: --prompt 是必需的")
            sys.exit(1)
        result = generate_code(args.prompt, args.output, args.language)
    
    elif args.command == "review":
        if not args.path:
            print("✗ 错误: --path 是必需的")
            sys.exit(1)
        rules = [r.strip() for r in args.rules.split(",")]
        result = review_code(args.path, rules)
    
    elif args.command == "cicd":
        result = setup_cicd(args.template, args.provider)
    
    else:
        result = {"success": False, "error": "未知命令"}
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result.get("success"):
            print(f"✓ {result.get('message', '执行成功')}")
            if "files_created" in result:
                print(f"  创建文件: {len(result['files_created'])} 个")
            if "files_reviewed" in result:
                print(f"  审查文件: {result['files_reviewed']} 个")
                print(f"  发现问题: {result.get('total_issues', 0)} 个")
        else:
            print(f"✗ 错误: {result.get('error', '未知错误')}")
            sys.exit(1)

if __name__ == "__main__":
    main()
