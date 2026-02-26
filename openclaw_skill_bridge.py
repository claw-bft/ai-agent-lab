#!/usr/bin/env python3
"""
OpenClaw Skill Bridge - OpenClaw与skill-cli的桥接模块

将skill-cli的自然语言执行层集成到OpenClaw主响应流程中，
使AI能够自动识别用户意图并调用相应技能包执行。

Author: Kimi Claw
Created: 2026-02-26
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# 添加skill-cli到路径
SKILL_CLI_DIR = Path(__file__).parent / "skills" / "skill-cli"
sys.path.insert(0, str(SKILL_CLI_DIR))

# 尝试导入自然语言执行层组件
try:
    from intent_parser import IntentParser, Intent, IntentType
    from skill_router import SkillRouter, SkillRoute
    from executor import SkillExecutor, ExecutionResult, ExecutionStatus
    from context_manager import ContextManager, ContextEntry
    SKILL_CLI_AVAILABLE = True
except ImportError as e:
    SKILL_CLI_AVAILABLE = False
    print(f"[SkillBridge] Warning: skill-cli modules not available: {e}", file=sys.stderr)


class SkillBridge:
    """
    OpenClaw技能桥接器
    
    职责：
    1. 拦截用户消息，进行意图解析
    2. 根据意图路由到对应技能包
    3. 执行技能命令并获取结果
    4. 管理多轮对话上下文
    5. 将结果返回给OpenClaw主流程
    """
    
    def __init__(self, workspace_dir: str = "/root/.openclaw/workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.skills_dir = self.workspace_dir / "skills"
        self.context_dir = self.workspace_dir / ".context"
        
        if SKILL_CLI_AVAILABLE:
            self.intent_parser = IntentParser()
            self.skill_router = SkillRouter(str(self.skills_dir))
            self.executor = SkillExecutor(str(self.skills_dir))
            self.context_manager = ContextManager(str(self.context_dir))
        else:
            self.intent_parser = None
            self.skill_router = None
            self.executor = None
            self.context_manager = None
        
        self.session_id = "default_session"
        self.enabled = True
        self.auto_execute = True  # 是否自动执行识别到的技能
        self.confidence_threshold = 0.5  # 置信度阈值
    
    def process_message(self, message: str, session_id: str = None) -> Dict[str, Any]:
        """
        处理用户消息 - 主入口点
        
        Args:
            message: 用户输入的消息
            session_id: 会话ID（可选）
            
        Returns:
            处理结果字典，包含：
            - handled: 是否已处理
            - skill_used: 使用的技能
            - result: 执行结果
            - response: 给用户的响应
        """
        if not self.enabled or not SKILL_CLI_AVAILABLE:
            return {"handled": False, "reason": "skill-bridge disabled or unavailable"}
        
        session_id = session_id or self.session_id
        
        # 1. 添加上下文记录
        self.context_manager.add_entry(session_id, "user", message)
        
        # 2. 检测是否是跟进问题
        follow_up = self.context_manager.detect_follow_up(session_id, message)
        if follow_up and follow_up.get("is_follow_up"):
            # 使用上次的技能继续处理
            last_skill = follow_up.get("last_skill")
            if last_skill:
                result = self._execute_with_context(session_id, message, last_skill)
                return self._build_response(result, session_id)
        
        # 3. 解析意图
        intent = self.intent_parser.parse(message)
        
        # 4. 检查置信度
        if intent.confidence < self.confidence_threshold:
            # 置信度太低，不自动处理
            return {
                "handled": False,
                "reason": "low_confidence",
                "confidence": intent.confidence,
                "threshold": self.confidence_threshold,
                "intent": intent.type.value
            }
        
        # 5. 路由到技能
        route = self.skill_router.route(intent)
        
        # 6. 执行或返回建议
        if self.auto_execute and route.confidence >= self.confidence_threshold:
            result = self.executor.execute_natural_language(message)
            
            # 记录到上下文
            self.context_manager.add_entry(
                session_id, 
                "assistant", 
                result.output[:500] if result.output else "",
                intent=intent.type.value,
                skill_used=result.skill_name
            )
            
            return self._build_response(result, session_id)
        else:
            # 返回建议但不自动执行
            return {
                "handled": True,
                "auto_executed": False,
                "suggested_skill": route.skill_name,
                "suggested_command": route.command,
                "suggested_args": route.args,
                "confidence": route.confidence,
                "reason": route.reason
            }
    
    def _execute_with_context(self, session_id: str, message: str, skill_hint: str) -> ExecutionResult:
        """在特定技能上下文中执行"""
        # 构建带上下文的提示
        context_str = self.context_manager.build_prompt_context(session_id, message)
        
        # 直接执行，但优先使用指定的技能
        result = self.executor.execute_natural_language(message)
        
        # 如果路由到的技能与提示不符，且提示的技能存在，则重试
        if result.skill_name != skill_hint:
            skill_path = self.skills_dir / skill_hint
            if skill_path.exists():
                # 使用指定的技能
                result = self.executor.execute_structured(skill_hint, "help", [])
                result.output = f"[使用 {skill_hint}]\n{result.output}"
        
        return result
    
    def _build_response(self, result: ExecutionResult, session_id: str) -> Dict[str, Any]:
        """构建响应"""
        response_lines = []
        
        if result.status == ExecutionStatus.SUCCESS:
            response_lines.append(f"✅ 技能执行成功: {result.skill_name}/{result.command}")
            if result.output:
                response_lines.append(f"\n{result.output}")
        elif result.status == ExecutionStatus.PARTIAL:
            response_lines.append(f"⚠️ 技能部分实现: {result.skill_name}")
            response_lines.append(result.output)
            response_lines.append("\n💡 该技能包需要补充完整实现")
        elif result.status == ExecutionStatus.NOT_FOUND:
            response_lines.append(f"❌ 技能未找到: {result.skill_name}")
        else:
            response_lines.append(f"❌ 执行失败: {result.status.value}")
            if result.error:
                response_lines.append(f"错误: {result.error}")
        
        response_lines.append(f"\n⏱️ 耗时: {result.duration_ms:.1f}ms")
        
        return {
            "handled": True,
            "auto_executed": True,
            "skill_used": result.skill_name,
            "command": result.command,
            "status": result.status.value,
            "output": result.output,
            "error": result.error,
            "duration_ms": result.duration_ms,
            "response": "\n".join(response_lines),
            "metadata": result.metadata
        }
    
    def get_available_skills(self) -> List[Dict[str, str]]:
        """获取所有可用技能"""
        if self.skill_router:
            return self.skill_router.list_available_skills()
        return []
    
    def get_session_stats(self, session_id: str = None) -> Dict[str, Any]:
        """获取会话统计"""
        if not self.context_manager:
            return {"error": "Context manager not available"}
        session_id = session_id or self.session_id
        return self.context_manager.get_session_stats(session_id)
    
    def save_session(self, session_id: str = None) -> bool:
        """保存会话"""
        if not self.context_manager:
            return False
        session_id = session_id or self.session_id
        return self.context_manager.save_session(session_id)
    
    def clear_session(self, session_id: str = None):
        """清除会话"""
        if self.context_manager:
            session_id = session_id or self.session_id
            self.context_manager.clear_session(session_id)


# ============ OpenClaw集成钩子 ============

def on_message_received(message: str, session_id: str = None) -> Optional[Dict[str, Any]]:
    """
    OpenClaw消息接收钩子
    
    在OpenClaw主流程中调用此函数，检查是否需要由skill-cli处理
    
    使用示例（在OpenClaw主流程中）：
    
        from openclaw_skill_bridge import on_message_received
        
        def handle_user_message(message, session_id):
            # 先尝试skill-cli处理
            result = on_message_received(message, session_id)
            if result and result.get("handled"):
                return result.get("response")
            
            # 否则使用默认处理流程
            return default_handler(message)
    """
    bridge = SkillBridge()
    return bridge.process_message(message, session_id)


def get_skill_bridge_instance() -> SkillBridge:
    """获取SkillBridge单例实例"""
    return SkillBridge()


# ============ CLI测试 ============

if __name__ == "__main__":
    print("=" * 70)
    print("OpenClaw Skill Bridge - 桥接模块测试")
    print("=" * 70)
    
    if not SKILL_CLI_AVAILABLE:
        print("\n❌ skill-cli模块不可用，请确保intent_parser.py等文件存在")
        sys.exit(1)
    
    bridge = SkillBridge()
    
    print(f"\n✅ 桥接模块初始化成功")
    print(f"   工作目录: {bridge.workspace_dir}")
    print(f"   技能目录: {bridge.skills_dir}")
    print(f"   可用技能: {len(bridge.get_available_skills())}个")
    
    # 测试用例
    test_cases = [
        "查询一下茅台股票",
        "分析一下600519的走势",
        "帮我写一个Python爬虫",
        "研究一下AI发展趋势",
        "分析竞品情况",
    ]
    
    print("\n" + "-" * 70)
    print("测试自然语言处理")
    print("-" * 70)
    
    for msg in test_cases:
        print(f"\n📝 用户: {msg}")
        result = bridge.process_message(msg, session_id="test_session")
        
        if result.get("handled"):
            if result.get("auto_executed"):
                print(f"   🤖 执行: {result['skill_used']}/{result['command']}")
                print(f"   📊 状态: {result['status']}")
                print(f"   ⏱️  耗时: {result['duration_ms']:.1f}ms")
                if result.get("output"):
                    preview = result['output'][:150].replace('\n', ' ')
                    print(f"   📄 输出: {preview}...")
            else:
                print(f"   💡 建议: {result['suggested_skill']} {result['suggested_command']}")
                print(f"   📊 置信度: {result['confidence']:.2f}")
        else:
            print(f"   ⏭️  未处理: {result.get('reason')}")
    
    # 测试跟进问题
    print("\n" + "-" * 70)
    print("测试跟进问题检测")
    print("-" * 70)
    
    follow_up_tests = [
        "再查一下五粮液",
        "还有呢",
        "这个怎么样",
    ]
    
    for msg in follow_up_tests:
        print(f"\n📝 用户: {msg}")
        follow_up = bridge.context_manager.detect_follow_up("test_session", msg)
        if follow_up and follow_up.get("is_follow_up"):
            print(f"   🔗 检测到跟进问题")
            print(f"   📎 引用: {follow_up['reference'][:50]}...")
            print(f"   🛠️  上次技能: {follow_up['last_skill']}")
        else:
            print(f"   🆕 新话题")
    
    # 会话统计
    print("\n" + "-" * 70)
    print("会话统计")
    print("-" * 70)
    stats = bridge.get_session_stats("test_session")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    # 保存会话
    bridge.save_session("test_session")
    print("\n✅ 测试完成，会话已保存")
