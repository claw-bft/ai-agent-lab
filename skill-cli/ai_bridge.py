#!/usr/bin/env python3
"""
AI桥接层 - AI Bridge
实现AI Agent与skill-cli的真正集成
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

# 确保能导入executor
SKILL_CLI_DIR = Path(__file__).parent
sys.path.insert(0, str(SKILL_CLI_DIR))

from executor import SkillExecutor, ExecutionResult, ExecutionStatus, ParsedIntent


class AIBridge:
    """
    AI桥接层 - 连接AI Agent与技能执行器

    功能:
    1. 接收AI的自然语言指令
    2. 解析并路由到对应技能
    3. 执行并返回结构化结果
    4. 支持上下文管理和多轮对话
    """

    def __init__(self):
        self.executor = SkillExecutor()
        self.session_history: List[Dict] = []
        self.max_history = 20

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        处理用户输入，执行对应的技能

        Args:
            user_input: 用户的自然语言输入
            context: 可选的上下文信息

        Returns:
            执行结果字典
        """
        start_time = time.time()

        # 1. 预处理和意图识别增强
        enhanced_input = self._preprocess_input(user_input)

        # 2. 执行
        result = self.executor.execute_natural_language(enhanced_input)

        # 3. 后处理和格式化
        formatted_result = self._format_result(result)

        # 4. 记录历史
        self._add_to_history(user_input, formatted_result)

        # 5. 添加元数据
        formatted_result["processing_time_ms"] = int((time.time() - start_time) * 1000)
        formatted_result["session_history_count"] = len(self.session_history)

        return formatted_result

    def _preprocess_input(self, user_input: str) -> str:
        """预处理用户输入，增强意图识别"""
        # 去除多余空白
        cleaned = user_input.strip()

        # 常见意图映射
        intent_mappings = {
            # 股票相关
            "茅台": "finance-pro quote --symbol 600519.SH",
            "腾讯": "finance-pro quote --symbol 00700.HK",
            "阿里": "finance-pro quote --symbol 09988.HK",
            "比亚迪": "finance-pro quote --symbol 002594.SZ",
            "宁德时代": "finance-pro quote --symbol 300750.SZ",
            "招商银行": "finance-pro quote --symbol 600036.SH",

            # 代码相关
            "生成代码": "coding-pro generate",
            "代码审查": "coding-pro review",
            "创建仓库": "coding-pro repo create",

            # 产品相关
            "竞品分析": "product-pro competitor",
            "写PRD": "product-pro prd",
            "做PPT": "product-pro ppt",

            # 研究相关
            "深度研究": "research-pro deep",
            "搜索": "research-pro search",
            "分析数据": "research-pro analyze",
        }

        # 检查是否匹配简单意图
        for keyword, command in intent_mappings.items():
            if keyword in cleaned:
                return f"{command} {cleaned}"

        return cleaned

    def _format_result(self, result: ExecutionResult) -> Dict[str, Any]:
        """格式化执行结果"""
        return {
            "success": result.status == ExecutionStatus.SUCCESS,
            "status": result.status.value,
            "skill": result.skill_name,
            "action": result.command,
            "output": result.output,
            "error": result.error,
            "execution_time_ms": result.duration_ms,
            "metadata": result.metadata
        }

    def _add_to_history(self, input_text: str, result: Dict):
        """添加到会话历史"""
        self.session_history.append({
            "input": input_text,
            "result": result,
            "timestamp": time.time()
        })
        # 限制历史长度
        if len(self.session_history) > self.max_history:
            self.session_history = self.session_history[-self.max_history:]

    def get_history(self, limit: int = 5) -> List[Dict]:
        """获取最近的历史记录"""
        return self.session_history[-limit:]

    def clear_history(self):
        """清空历史记录"""
        self.session_history = []

    def get_available_skills(self) -> List[str]:
        """获取所有可用技能"""
        return self.executor.skill_router.get_available_skills()

    def get_skill_help(self, skill_name: Optional[str] = None) -> str:
        """获取技能帮助信息"""
        return self.executor.get_skill_help(skill_name)


class IntentParser:
    """
    增强型意图解析器
    使用更智能的方式解析自然语言命令
    """

    def __init__(self):
        self.skill_patterns = {
            "finance-pro": {
                "keywords": ["股票", "行情", "股价", "分析", "财报", "K线", "MACD", "RSI",
                           "quote", "analyze", "stock", "price", "financial"],
                "patterns": [
                    r"(?:查[看询]|获取)?\s*([\d]{6})\s*(?:股票)?(?:行情|价格|股价)?",
                    r"(?:分析|查看)?\s*(茅台|腾讯|阿里|比亚迪|宁德时代|招商银行)",
                ]
            },
            "coding-pro": {
                "keywords": ["代码", "生成", "审查", "review", "repo", "git", "github",
                           "generate", "code", "python", "CI/CD", "pipeline"],
                "patterns": [
                    r"(?:生成|写|创建)\s*(?:一个)?\s*(.+?)(?:代码|程序|脚本)?",
                    r"(?:审查|检查)\s*(.+?)(?:代码|目录|文件)?",
                ]
            },
            "product-pro": {
                "keywords": ["产品", "PRD", "竞品", "PPT", "需求", "feature",
                           "product", "competitor", "roadmap", "market"],
                "patterns": [
                    r"(?:分析|研究)\s*(.+?)(?:竞品|竞争对手)?",
                    r"(?:写|生成|创建)\s*(.+?)(?:PRD|需求文档)?",
                ]
            },
            "research-pro": {
                "keywords": ["研究", "搜索", "调研", "监控", "report",
                           "research", "search", "monitor", "analyze"],
                "patterns": [
                    r"(?:深度)?研究\s*(.+?)(?:趋势|发展|现状)?",
                    r"(?:搜索|查找)\s*(.+?)(?:信息|资料|新闻)?",
                ]
            }
        }

    def parse(self, command: str) -> Dict[str, Any]:
        """解析命令，返回结构化意图"""
        command_lower = command.lower()

        # 计算每个技能的匹配分数
        scores = {}
        for skill, config in self.skill_patterns.items():
            score = 0
            # 关键词匹配
            for keyword in config["keywords"]:
                if keyword.lower() in command_lower:
                    score += 1
            # 模式匹配
            for pattern in config["patterns"]:
                if re.search(pattern, command):
                    score += 2
            scores[skill] = score

        # 选择最佳匹配
        if scores:
            best_skill = max(scores, key=scores.get)
            best_score = scores[best_skill]

            if best_score > 0:
                return {
                    "skill": best_skill,
                    "confidence": min(best_score / 5, 1.0),
                    "all_scores": scores
                }

        return {
            "skill": "unknown",
            "confidence": 0,
            "all_scores": scores
        }


# 便捷函数接口
def execute_skill(user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    便捷函数：执行技能命令

    使用示例:
        result = execute_skill("分析一下茅台股票")
        result = execute_skill("生成一个Python爬虫")
    """
    bridge = AIBridge()
    return bridge.process(user_input, context)


def quick_quote(symbol: str) -> Dict[str, Any]:
    """快速获取股票行情"""
    return execute_skill(f"获取{symbol}的行情")


def quick_research(topic: str) -> Dict[str, Any]:
    """快速进行研究"""
    return execute_skill(f"深度研究{topic}")


def quick_code(prompt: str) -> Dict[str, Any]:
    """快速生成代码"""
    return execute_skill(f"生成代码: {prompt}")


# CLI入口
def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Skill Bridge")
    parser.add_argument("command", nargs="?", help="自然语言命令")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互模式")
    parser.add_argument("--skill", help="指定技能")
    parser.add_argument("--history", action="store_true", help="显示历史")
    parser.add_argument("--skills", action="store_true", help="列出所有技能")
    parser.add_argument("--help-skill", help="显示技能帮助")

    args = parser.parse_args()

    bridge = AIBridge()

    if args.skills:
        skills = bridge.get_available_skills()
        print("可用技能:")
        for skill in skills:
            print(f"  • {skill}")
        return

    if args.help_skill:
        print(bridge.get_skill_help(args.help_skill))
        return

    if args.history:
        history = bridge.get_history()
        print(f"最近 {len(history)} 条历史:")
        for i, h in enumerate(history, 1):
            print(f"{i}. {h['input'][:50]}...")
        return

    if args.interactive:
        print("AI Skill Bridge - 交互模式")
        print("输入 'quit' 或 'exit' 退出")
        print("输入 'help' 查看帮助")
        print("-" * 40)

        while True:
            try:
                user_input = input("\n> ").strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("再见!")
                    break

                if user_input.lower() == "help":
                    print(bridge.get_skill_help())
                    continue

                if not user_input:
                    continue

                result = bridge.process(user_input)

                # 格式化输出
                if result["success"]:
                    print(f"✓ 执行成功 [{result['skill']}]")
                    if result.get("output"):
                        print(json.dumps(result["output"], indent=2, ensure_ascii=False))
                else:
                    print(f"✗ 执行失败: {result.get('error', '未知错误')}")

                print(f"  耗时: {result['processing_time_ms']}ms")

            except KeyboardInterrupt:
                print("\n再见!")
                break
            except Exception as e:
                print(f"错误: {e}")

    elif args.command:
        result = bridge.process(args.command)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
