#!/usr/bin/env python3
"""
上下文管理器 - Context Manager
管理多轮对话状态和上下文
"""

import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

class ContextType(Enum):
    """上下文类型"""
    CONVERSATION = "conversation"  # 对话上下文
    TASK = "task"                  # 任务上下文
    SESSION = "session"            # 会话上下文

@dataclass
class ContextEntry:
    """上下文条目"""
    timestamp: float
    role: str  # user / assistant / system
    content: str
    intent: Optional[str] = None
    skill_used: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class ContextManager:
    """上下文管理器"""
    
    def __init__(self, context_dir: str = "/root/.openclaw/workspace/.context"):
        self.context_dir = Path(context_dir)
        self.context_dir.mkdir(parents=True, exist_ok=True)
        self.active_contexts: Dict[str, List[ContextEntry]] = {}
        self.max_history = 20  # 最大历史记录数
    
    def add_entry(self, session_id: str, role: str, content: str, 
                  intent: str = None, skill_used: str = None, 
                  metadata: Dict = None) -> ContextEntry:
        """
        添加上下文条目
        
        Args:
            session_id: 会话ID
            role: 角色 (user/assistant/system)
            content: 内容
            intent: 意图类型
            skill_used: 使用的技能
            metadata: 元数据
            
        Returns:
            ContextEntry对象
        """
        entry = ContextEntry(
            timestamp=time.time(),
            role=role,
            content=content,
            intent=intent,
            skill_used=skill_used,
            metadata=metadata or {}
        )
        
        if session_id not in self.active_contexts:
            self.active_contexts[session_id] = []
        
        self.active_contexts[session_id].append(entry)
        
        # 限制历史记录长度
        if len(self.active_contexts[session_id]) > self.max_history:
            self.active_contexts[session_id] = self.active_contexts[session_id][-self.max_history:]
        
        return entry
    
    def get_context(self, session_id: str, limit: int = 10) -> List[ContextEntry]:
        """
        获取会话上下文
        
        Args:
            session_id: 会话ID
            limit: 返回条目数限制
            
        Returns:
            ContextEntry列表
        """
        if session_id not in self.active_contexts:
            return []
        
        return self.active_contexts[session_id][-limit:]
    
    def get_last_intent(self, session_id: str) -> Optional[str]:
        """获取最近的意图"""
        context = self.get_context(session_id, limit=5)
        for entry in reversed(context):
            if entry.intent:
                return entry.intent
        return None
    
    def get_last_skill(self, session_id: str) -> Optional[str]:
        """获取最近使用的技能"""
        context = self.get_context(session_id, limit=5)
        for entry in reversed(context):
            if entry.skill_used:
                return entry.skill_used
        return None
    
    def build_prompt_context(self, session_id: str, current_input: str) -> str:
        """
        构建用于提示的上下文字符串
        
        Args:
            session_id: 会话ID
            current_input: 当前输入
            
        Returns:
            格式化的上下文字符串
        """
        context = self.get_context(session_id, limit=5)
        
        if not context:
            return ""
        
        lines = ["【对话上下文】"]
        for entry in context:
            time_str = time.strftime("%H:%M", time.localtime(entry.timestamp))
            lines.append(f"[{time_str}] {entry.role}: {entry.content[:100]}")
        
        lines.append(f"[当前] user: {current_input}")
        
        return "\n".join(lines)
    
    def detect_follow_up(self, session_id: str, current_input: str) -> Optional[Dict]:
        """
        检测是否是跟进问题
        
        Args:
            session_id: 会话ID
            current_input: 当前输入
            
        Returns:
            如果是跟进问题，返回相关信息；否则None
        """
        context = self.get_context(session_id, limit=3)
        
        if not context:
            return None
        
        # 跟进问题关键词
        follow_up_indicators = [
            "再", "还", "另外", "还有", "那", "这个", "它", "他", "她",
            "more", "another", "also", "what about", "how about",
        ]
        
        current_lower = current_input.lower()
        
        # 检查是否是简短跟进
        if len(current_input) < 15:
            for indicator in follow_up_indicators:
                if indicator in current_lower or indicator in current_input:
                    last_entry = context[-1] if context else None
                    if last_entry:
                        return {
                            "is_follow_up": True,
                            "reference": last_entry.content,
                            "last_skill": last_entry.skill_used,
                            "last_intent": last_entry.intent
                        }
        
        return None
    
    def save_session(self, session_id: str) -> bool:
        """保存会话到文件"""
        if session_id not in self.active_contexts:
            return False
        
        file_path = self.context_dir / f"{session_id}.json"
        
        try:
            data = {
                "session_id": session_id,
                "saved_at": time.time(),
                "entries": [
                    {
                        "timestamp": e.timestamp,
                        "role": e.role,
                        "content": e.content,
                        "intent": e.intent,
                        "skill_used": e.skill_used,
                        "metadata": e.metadata
                    }
                    for e in self.active_contexts[session_id]
                ]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存会话失败: {e}")
            return False
    
    def load_session(self, session_id: str) -> bool:
        """从文件加载会话"""
        file_path = self.context_dir / f"{session_id}.json"
        
        if not file_path.exists():
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.active_contexts[session_id] = [
                ContextEntry(
                    timestamp=e["timestamp"],
                    role=e["role"],
                    content=e["content"],
                    intent=e.get("intent"),
                    skill_used=e.get("skill_used"),
                    metadata=e.get("metadata", {})
                )
                for e in data.get("entries", [])
            ]
            
            return True
        except Exception as e:
            print(f"加载会话失败: {e}")
            return False
    
    def clear_session(self, session_id: str):
        """清除会话"""
        if session_id in self.active_contexts:
            del self.active_contexts[session_id]
        
        file_path = self.context_dir / f"{session_id}.json"
        if file_path.exists():
            file_path.unlink()
    
    def list_sessions(self) -> List[str]:
        """列出所有会话ID"""
        sessions = list(self.active_contexts.keys())
        
        # 也检查文件
        for file_path in self.context_dir.glob("*.json"):
            session_id = file_path.stem
            if session_id not in sessions:
                sessions.append(session_id)
        
        return sessions
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """获取会话统计"""
        context = self.get_context(session_id, limit=1000)
        
        if not context:
            return {"exists": False}
        
        user_count = sum(1 for e in context if e.role == "user")
        assistant_count = sum(1 for e in context if e.role == "assistant")
        
        skills_used = set(e.skill_used for e in context if e.skill_used)
        intents = set(e.intent for e in context if e.intent)
        
        duration = 0
        if len(context) >= 2:
            duration = context[-1].timestamp - context[0].timestamp
        
        return {
            "exists": True,
            "total_entries": len(context),
            "user_messages": user_count,
            "assistant_messages": assistant_count,
            "skills_used": list(skills_used),
            "intents": list(intents),
            "duration_seconds": duration
        }


# 测试代码
if __name__ == "__main__":
    manager = ContextManager()
    session_id = "test_session_001"
    
    print("=" * 60)
    print("上下文管理器测试")
    print("=" * 60)
    
    # 添加一些条目
    manager.add_entry(session_id, "user", "查询茅台股票", intent="get_quote", skill_used="finance-pro")
    manager.add_entry(session_id, "assistant", "茅台(600519.SH)当前股价...", skill_used="finance-pro")
    manager.add_entry(session_id, "user", "再查一下五粮液", intent="get_quote", skill_used="finance-pro")
    
    # 获取上下文
    context = manager.get_context(session_id)
    print(f"\n✓ 上下文条目数: {len(context)}")
    
    # 检测跟进
    follow_up = manager.detect_follow_up(session_id, "还有呢")
    print(f"✓ 跟进检测: {follow_up}")
    
    # 保存会话
    saved = manager.save_session(session_id)
    print(f"✓ 会话保存: {'成功' if saved else '失败'}")
    
    # 统计
    stats = manager.get_session_stats(session_id)
    print(f"✓ 会话统计: {stats}")
