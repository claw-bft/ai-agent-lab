#!/usr/bin/env python3
"""
AI Agent Lab - 集成入口
将skill-cli AI执行层与主系统集成

使用方法:
    python3 ai_agent.py "查询茅台股票"
    python3 ai_agent.py --interactive
    python3 ai_agent.py --test
"""

import sys
import os
import json
import argparse
from pathlib import Path

# 添加skill-cli到路径
SKILL_CLI_DIR = Path("/root/.openclaw/workspace/skills/skill-cli")
sys.path.insert(0, str(SKILL_CLI_DIR))

try:
    from executor import SkillExecutor, ExecutionStatus
    from intent_parser import IntentParser
    from skill_router import SkillRouter
    from context_manager import ContextManager
    AI_EXECUTOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  AI执行层加载失败: {e}")
    AI_EXECUTOR_AVAILABLE = False

class AIAgent:
    """AI Agent主类 - 集成自然语言执行层"""
    
    def __init__(self):
        self.session_id = "main_session"
        self.context_manager = ContextManager() if AI_EXECUTOR_AVAILABLE else None
        self.executor = SkillExecutor() if AI_EXECUTOR_AVAILABLE else None
        
    def process(self, text: str) -> dict:
        """处理自然语言输入"""
        if not AI_EXECUTOR_AVAILABLE:
            return {
                "success": False,
                "error": "AI执行层不可用",
                "suggestion": "请检查skill-cli模块是否正确安装"
            }
        
        # 记录用户输入到上下文
        if self.context_manager:
            self.context_manager.add_entry(
                self.session_id, 
                "user", 
                text
            )
        
        # 执行自然语言命令
        result = self.executor.execute_natural_language(text)
        
        # 记录执行结果到上下文
        if self.context_manager:
            self.context_manager.add_entry(
                self.session_id,
                "assistant",
                result.output[:500] if result.output else "执行完成",
                intent=result.metadata.get("intent"),
                skill_used=result.skill_name
            )
        
        return {
            "success": result.status == ExecutionStatus.SUCCESS,
            "skill": result.skill_name,
            "command": result.command,
            "status": result.status.value,
            "output": result.output,
            "error": result.error,
            "duration_ms": result.duration_ms,
            "metadata": result.metadata
        }
    
    def interactive_mode(self):
        """交互模式"""
        print("=" * 60)
        print("AI Agent Lab - 交互模式")
        print("=" * 60)
        print("输入自然语言命令，或输入 'quit' 退出")
        print()
        
        while True:
            try:
                text = input("> ").strip()
                if not text:
                    continue
                if text.lower() in ["quit", "exit", "q"]:
                    break
                
                result = self.process(text)
                
                if result["success"]:
                    print(f"✓ [{result['skill']}/{result['command']}] 执行成功")
                    if result["output"]:
                        print(result["output"])
                else:
                    print(f"✗ 执行失败: {result.get('error', '未知错误')}")
                
                print()
                
            except KeyboardInterrupt:
                print("\n再见!")
                break
            except Exception as e:
                print(f"✗ 错误: {e}")
    
    def run_tests(self):
        """运行集成测试"""
        print("=" * 60)
        print("AI Agent Lab - 集成测试")
        print("=" * 60)
        
        test_cases = [
            ("查询茅台股票", "finance-pro"),
            ("研究AI发展趋势", "research-pro"),
            ("写个Python函数", "coding-pro"),
            ("分析竞品", "product-pro"),
        ]
        
        passed = 0
        for text, expected_skill in test_cases:
            print(f"\n📝 测试: {text}")
            result = self.process(text)
            
            skill_match = result["skill"] == expected_skill
            status = "✓" if skill_match else "✗"
            
            print(f"   {status} 技能: {result['skill']} (预期: {expected_skill})")
            print(f"   命令: {result['command']}")
            print(f"   状态: {result['status']}")
            print(f"   耗时: {result['duration_ms']:.1f}ms")
            
            if skill_match:
                passed += 1
        
        print(f"\n{'=' * 60}")
        print(f"测试结果: {passed}/{len(test_cases)} 通过")
        return passed == len(test_cases)

def main():
    parser = argparse.ArgumentParser(description="AI Agent Lab - 自然语言执行入口")
    parser.add_argument("command", nargs="?", help="自然语言命令")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互模式")
    parser.add_argument("--test", action="store_true", help="运行测试")
    parser.add_argument("--json", "-j", action="store_true", help="JSON输出")
    
    args = parser.parse_args()
    
    agent = AIAgent()
    
    if args.test:
        success = agent.run_tests()
        sys.exit(0 if success else 1)
    
    elif args.interactive:
        agent.interactive_mode()
    
    elif args.command:
        result = agent.process(args.command)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            if result["success"]:
                print(f"✓ 执行成功")
                if result["output"]:
                    print(result["output"])
            else:
                print(f"✗ 错误: {result.get('error', '未知错误')}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
