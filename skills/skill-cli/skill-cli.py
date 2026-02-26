#!/usr/bin/env python3
"""
技能包CLI执行器 - Skill CLI Executor
将SKILL.md定义转化为可执行命令
"""

import os
import sys
import json
import re
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

SKILLS_DIR = Path("/root/.openclaw/workspace/skills")

def get_available_skills() -> List[str]:
    """获取所有可用的技能包列表"""
    if not SKILLS_DIR.exists():
        return []
    return [d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]

def parse_skill_md(skill_name: str) -> Dict[str, Any]:
    """解析SKILL.md文件，提取命令定义"""
    skill_path = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_path.exists():
        return {}
    
    content = skill_path.read_text(encoding='utf-8')
    
    # 提取技能名称和描述
    name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
    desc_match = re.search(r'^description:\s*(.+)$', content, re.MULTILINE)
    
    # 提取使用示例中的命令
    examples = []
    example_section = re.search(r'## 使用示例.*?(?=##|$)', content, re.DOTALL)
    if example_section:
        # 提取bash代码块中的命令
        bash_blocks = re.findall(r'```bash\n(.*?)```', example_section.group(0), re.DOTALL)
        for block in bash_blocks:
            lines = [l.strip() for l in block.strip().split('\n') if l.strip() and not l.strip().startswith('#')]
            examples.extend(lines)
    
    return {
        "name": name_match.group(1) if name_match else skill_name,
        "description": desc_match.group(1) if desc_match else "",
        "examples": examples
    }

def execute_skill_command(skill_name: str, args: List[str]) -> Dict[str, Any]:
    """执行技能命令"""
    skill_info = parse_skill_md(skill_name)
    
    if not skill_info:
        return {
            "success": False,
            "error": f"技能包 '{skill_name}' 不存在或缺少SKILL.md"
        }
    
    # 构建命令映射
    command_map = build_command_map(skill_name)
    
    if not args:
        return {
            "success": True,
            "skill": skill_name,
            "description": skill_info.get("description", ""),
            "available_commands": list(command_map.keys()),
            "examples": skill_info.get("examples", [])
        }
    
    # 解析子命令
    subcommand = args[0]
    
    if subcommand in command_map:
        handler = command_map[subcommand]
        return handler(skill_name, args[1:])
    else:
        # 尝试使用AI执行自然语言命令
        return execute_natural_language(skill_name, " ".join(args))

def build_command_map(skill_name: str) -> Dict[str, callable]:
    """为技能包构建命令映射"""
    
    # 通用命令处理器
    handlers = {
        "help": handle_help,
        "info": handle_info,
        "examples": handle_examples,
    }
    
    # 根据技能类型添加特定处理器
    if skill_name == "coding-pro":
        handlers.update({
            "generate": handle_coding_generate,
            "review": handle_coding_review,
            "repo": handle_coding_repo,
            "cicd": handle_coding_cicd,
        })
    elif skill_name == "finance-pro":
        handlers.update({
            "quote": handle_finance_quote,
            "analyze": handle_finance_analyze,
            "financial": handle_finance_financial,
            "alert": handle_finance_alert,
        })
    elif skill_name == "product-pro":
        handlers.update({
            "competitor": handle_product_competitor,
            "prd": handle_product_prd,
            "ppt": handle_product_ppt,
            "research": handle_product_research,
        })
    elif skill_name == "research-pro":
        handlers.update({
            "deep": handle_research_deep,
            "analyze": handle_research_analyze,
            "search": handle_research_search,
            "monitor": handle_research_monitor,
        })
    
    return handlers

# ============ 通用处理器 ============

def handle_help(skill_name: str, args: List[str]) -> Dict[str, Any]:
    """显示帮助信息"""
    skill_info = parse_skill_md(skill_name)
    return {
        "success": True,
        "skill": skill_name,
        "description": skill_info.get("description", ""),
        "examples": skill_info.get("examples", [])
    }

def handle_info(skill_name: str, args: List[str]) -> Dict[str, Any]:
    """显示技能包详细信息"""
    skill_path = SKILLS_DIR / skill_name
    skill_file = skill_path / "SKILL.md"
    
    info = {
        "success": True,
        "skill": skill_name,
        "path": str(skill_path),
        "exists": skill_path.exists(),
        "has_skill_md": skill_file.exists(),
    }
    
    if skill_file.exists():
        content = skill_file.read_text(encoding='utf-8')
        info["size_bytes"] = len(content)
        info["line_count"] = len(content.split('\n'))
    
    return info

def handle_examples(skill_name: str, args: List[str]) -> Dict[str, Any]:
    """显示使用示例"""
    skill_info = parse_skill_md(skill_name)
    return {
        "success": True,
        "skill": skill_name,
        "examples": skill_info.get("examples", [])
    }

# ============ Coding Pro 处理器 ============

def handle_coding_generate(skill_name: str, args: List[str]) -> Dict[str, Any]:
    """代码生成"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--output", default="./generated")
    try:
        parsed = parser.parse_args(args)
        return {
            "success": True,
            "action": "code_generate",
            "prompt": parsed.prompt,
            "output": parsed.output,
            "message": f"代码生成任务已创建: {parsed.prompt[:50]}..."
        }
    except SystemExit:
        return {"success": False, "error": "参数解析失败"}

def handle_coding_review(skill_name: str, args: List[str]) -> Dict[str, Any]:
    """代码审查"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True)
    parser.add_argument("--rules", default="security,performance")
    try:
        parsed = parser.parse_args(args)
        return {
            "success": True,
            "action": "code_review",
            "path": parsed.path,
            "rules": parsed.rules.split(','),
            "message": f"代码审查: {parsed.path}"
        }
    except SystemExit:
        return {"success": False, "error": "参数解析失败"}

def handle_coding_repo(skill_name: str, args: List[str]) -> Dict[str, Any]:
    """仓库管理"""
    if not args:
        return {"success": False, "error": "缺少子命令 (create/clone/push)"}
    
    subcmd = args[0]
    if subcmd == "create":
        return {
            "success": True,
            "action": "repo_create",
            "message": "GitHub仓库创建功能需要配置gh CLI"
        }
    return {"success": False, "error": f"未知子命令: {subcmd}"}

def handle_coding_cicd(skill_name: str, args: List[str]) -> Dict[str, Any]:
    """CI/CD配置"""
    return {
        "success": True,
        "action": "cicd_setup",
        "message": "CI/CD配置功能 - 支持GitHub Actions/GitLab CI"
    }

# ============ Finance Pro 处理器 ============

def handle_finance_quote(skill_name: str, args: List[str]) -> Dict[str, Any]:
    """获取股票行情"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True)
    try:
        parsed = parser.parse_args(args)
        return {
            "success": True,
            "action": "stock_quote",
            "symbol": parsed.symbol,
            "message": f"获取 {parsed.symbol} 行情数据"
        }
    except SystemExit:
        return {"success": False, "error": "缺少 --symbol 参数"}

def handle_finance_analyze(skill_name: str, args: List[str]) -> Dict[str, Any]:
    """技术分析"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--indicators", default="MACD,RSI")
    try:
        parsed = parser.parse_args(args)
        return {
            "success": True,
            "action": "technical_analysis",
            "symbol": parsed.symbol,
            "indicators": parsed.indicators.split(','),
            "message": f"技术分析: {parsed.symbol}"
        }
    except SystemExit:
        return {"success": False, "error": "缺少 --symbol 参数"}

def handle_finance_financial(skill_name: str, args: List[str]) -> Dict[str, Any]:
    """财报分析"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--quarter", default="latest")
    try:
        parsed = parser.parse_args(args)
        return {
            "success": True,
            "action": "financial_analysis",
            "symbol": parsed.symbol,
            "quarter": parsed.quarter,
            "message": f"财报分析: {parsed.symbol}"
        }
    except SystemExit:
        return {"success": False, "error": "缺少 --symbol 参数"}

def handle_finance_alert(skill_name: str, args: List[str]) -> Dict[str, Any]:
    """价格预警"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--condition", required=True)
    parser.add_argument("--channel", default="feishu")
    try:
        parsed = parser.parse_args(args)
        return {
            "success": True,
            "action": "price_alert",
            "symbol": parsed.symbol,
            "condition": parsed.condition,
            "channel": parsed.channel,
            "message": f"价格预警设置: {parsed.symbol} {parsed.condition}"
        }
    except SystemExit:
        return {"success": False, "error": "缺少必要参数"}

# ============ Product Pro 处理器 ============

def handle_product_competitor(skill_name: str, args: List[str]) -> Dict[str, Any]:
    """竞品分析"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", required=True)
    parser.add_argument("--output", default="competitor-report.md")
    try:
        parsed = parser.parse_args(args)
        return {
            "success": True,
            "action": "competitor_analysis",
            "product": parsed.product,
            "output": parsed.output,
            "message": f"竞品分析: {parsed.product}"
        }
    except SystemExit:
        return {"success": False, "error": "缺少 --product 参数"}

def handle_product_prd(skill_name: str, args: List[str]) -> Dict[str, Any]:
    """PRD撰写"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--feature", required=True)
    parser.add_argument("--template", default="standard")
    try:
        parsed = parser.parse_args(args)
        return {
            "success": True,
            "action": "prd_create",
            "feature": parsed.feature,
            "template": parsed.template,
            "message": f"PRD创建: {parsed.feature}"
        }
    except SystemExit:
        return {"success": False, "error": "缺少 --feature 参数"}

def handle_product_ppt(skill_name: str, args: List[str]) -> Dict[str, Any]:
    """PPT生成"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--slides", type=int, default=10)
    try:
        parsed = parser.parse_args(args)
        return {
            "success": True,
            "action": "ppt_create",
            "topic": parsed.topic,
            "slides": parsed.slides,
            "message": f"PPT生成: {parsed.topic} ({parsed.slides}页)"
        }
    except SystemExit:
        return {"success": False, "error": "缺少 --topic 参数"}

def handle_product_research(skill_name: str, args: List[str]) -> Dict[str, Any]:
    """用户调研"""
    return {
        "success": True,
        "action": "user_research",
        "message": "用户调研功能 - 支持问卷/访谈/数据分析"
    }

# ============ Research Pro 处理器 ============

def handle_research_deep(skill_name: str, args: List[str]) -> Dict[str, Any]:
    """深度研究"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--depth", default="comprehensive", choices=["quick", "standard", "comprehensive"])
    try:
        parsed = parser.parse_args(args)
        return {
            "success": True,
            "action": "deep_research",
            "topic": parsed.topic,
            "depth": parsed.depth,
            "message": f"深度研究: {parsed.topic} ({parsed.depth})"
        }
    except SystemExit:
        return {"success": False, "error": "缺少 --topic 参数"}

def handle_research_analyze(skill_name: str, args: List[str]) -> Dict[str, Any]:
    """数据分析"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--query", required=True)
    try:
        parsed = parser.parse_args(args)
        return {
            "success": True,
            "action": "data_analysis",
            "file": parsed.file,
            "query": parsed.query,
            "message": f"数据分析: {parsed.file}"
        }
    except SystemExit:
        return {"success": False, "error": "缺少必要参数"}

def handle_research_search(skill_name: str, args: List[str]) -> Dict[str, Any]:
    """实时搜索"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--sources", default="news,blog")
    try:
        parsed = parser.parse_args(args)
        return {
            "success": True,
            "action": "realtime_search",
            "query": parsed.query,
            "sources": parsed.sources.split(','),
            "message": f"搜索: {parsed.query}"
        }
    except SystemExit:
        return {"success": False, "error": "缺少 --query 参数"}

def handle_research_monitor(skill_name: str, args: List[str]) -> Dict[str, Any]:
    """竞品监控"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--competitors", required=True)
    parser.add_argument("--alerts", default="product-launch")
    try:
        parsed = parser.parse_args(args)
        return {
            "success": True,
            "action": "competitor_monitor",
            "competitors": parsed.competitors.split(','),
            "alerts": parsed.alerts.split(','),
            "message": f"监控: {parsed.competitors}"
        }
    except SystemExit:
        return {"success": False, "error": "缺少 --competitors 参数"}

# ============ 自然语言执行 ============

def execute_natural_language(skill_name: str, command: str) -> Dict[str, Any]:
    """使用AI执行自然语言命令"""
    return {
        "success": True,
        "action": "natural_language",
        "skill": skill_name,
        "command": command,
        "message": f"自然语言执行: {command}",
        "note": "此命令需要AI解释执行"
    }

# ============ CLI入口 ============

def main():
    # 手动解析参数以支持技能命令中的--参数
    args_list = sys.argv[1:]
    
    # 检查是否是list命令
    if not args_list or args_list[0] in ["list", "--list", "-l"]:
        skills = get_available_skills()
        use_json = "--json" in args_list or "-j" in args_list
        result = {
            "success": True,
            "skills": skills,
            "count": len(skills)
        }
        if use_json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"可用技能包 ({len(skills)}个):")
            for skill in skills:
                info = parse_skill_md(skill)
                desc = info.get("description", "")[:40]
                print(f"  • {skill:<20} {desc}...")
        return
    
    # 解析参数
    skill_name = args_list[0]
    skill_args = args_list[1:]
    use_json = "--json" in skill_args or "-j" in skill_args
    # 移除--json参数
    skill_args = [a for a in skill_args if a not in ["--json", "-j"]]
    
    # 执行技能命令
    result = execute_skill_command(skill_name, skill_args)
    
    if use_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result.get("success"):
            print(f"✓ {result.get('message', '执行成功')}")
            if "examples" in result and result["examples"]:
                print("\n使用示例:")
                for ex in result["examples"][:3]:
                    print(f"  $ {ex}")
        else:
            print(f"✗ 错误: {result.get('error', '未知错误')}")
            sys.exit(1)

if __name__ == "__main__":
    main()
