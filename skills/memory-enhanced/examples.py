#!/usr/bin/env python3
"""
Memory Enhanced System - 使用示例
演示如何使用记忆增强系统进行跨会话上下文保持
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory_system import MemoryStore, MemoryType, MemoryPriority


def demo_basic_usage():
    """基础使用示例"""
    print("=" * 60)
    print("示例1: 基础记忆存储与检索")
    print("=" * 60)
    
    # 创建临时存储
    memory = MemoryStore(storage_path="/tmp/demo_memory.json")
    
    # 存储用户偏好
    memory.store(
        content="用户偏好使用Python进行数据分析",
        memory_type=MemoryType.PREFERENCE,
        priority=MemoryPriority.HIGH,
        metadata={"category": "programming", "user": "demo"}
    )
    
    memory.store(
        content="用户喜欢暗色主题的IDE",
        memory_type=MemoryType.PREFERENCE,
        priority=MemoryPriority.MEDIUM,
        metadata={"category": "ui", "user": "demo"}
    )
    
    memory.store(
        content="当前正在开发股票分析系统",
        memory_type=MemoryType.CONTEXT,
        priority=MemoryPriority.HIGH,
        metadata={"project": "stock-analyzer", "user": "demo"}
    )
    
    # 检索记忆
    print("\n检索: '用户喜欢什么编程语言'")
    results = memory.search("用户喜欢什么编程语言", top_k=3)
    for entry, score in results:
        print(f"  [{score:.2f}] {entry.content}")
    
    print("\n检索: '当前项目是什么'")
    results = memory.search("当前项目是什么", top_k=3)
    for entry, score in results:
        print(f"  [{score:.2f}] {entry.content}")


def demo_conversation_context():
    """对话上下文示例"""
    print("\n" + "=" * 60)
    print("示例2: 对话上下文保持")
    print("=" * 60)
    
    memory = MemoryStore(storage_path="/tmp/demo_memory.json")
    
    # 模拟对话历史
    conversations = [
        ("用户", "我想部署一个网站到Vercel"),
        ("助手", "我可以帮您部署到Vercel。请提供项目路径。"),
        ("用户", "项目在 /root/my-project"),
        ("助手", "好的，正在为您部署..."),
    ]
    
    # 存储对话片段
    for speaker, content in conversations:
        memory.store(
            content=f"{speaker}: {content}",
            memory_type=MemoryType.CONVERSATION,
            priority=MemoryPriority.LOW,
            metadata={"speaker": speaker}
        )
    
    # 后续对话时检索上下文
    print("\n新对话: '部署完成了吗？'")
    context = memory.search("部署完成了吗？", top_k=3)
    print("检索到的相关上下文:")
    for entry, score in context:
        print(f"  - {entry.content}")


def demo_skill_memory():
    """技能使用记忆示例"""
    print("\n" + "=" * 60)
    print("示例3: 技能使用记录")
    print("=" * 60)
    
    memory = MemoryStore(storage_path="/tmp/demo_memory.json")
    
    # 记录技能使用
    skills_used = [
        ("finance-pro", "查询了茅台股票 600519.SH", "stock-analysis"),
        ("research-pro", "搜索了AI Agent最新进展", "ai-research"),
        ("coding-pro", "生成了Python数据处理代码", "code-generation"),
    ]
    
    for skill, action, project in skills_used:
        memory.store(
            content=f"使用 {skill} {action}",
            memory_type=MemoryType.SKILL,
            priority=MemoryPriority.MEDIUM,
            metadata={"skill": skill, "project": project}
        )
    
    # 检索技能使用历史
    print("\n检索: '使用过哪些技能'")
    results = memory.get_by_type(MemoryType.SKILL, limit=5)
    for entry in results:
        print(f"  - {entry.content}")
    
    print("\n检索: 'finance相关'")
    results = memory.search("finance 股票", top_k=3)
    for entry, score in results:
        print(f"  [{score:.2f}] {entry.content}")


def demo_decision_tracking():
    """决策追踪示例"""
    print("\n" + "=" * 60)
    print("示例4: 历史决策记录")
    print("=" * 60)
    
    memory = MemoryStore(storage_path="/tmp/demo_memory.json")
    
    # 记录重要决策
    decisions = [
        ("技术栈选择", "决定使用PostgreSQL而不是MySQL", "CRITICAL"),
        ("部署平台", "选择Vercel作为默认部署平台", "HIGH"),
        ("API设计", "采用RESTful API风格", "MEDIUM"),
    ]
    
    for topic, decision, priority in decisions:
        priority_enum = MemoryPriority[priority]
        memory.store(
            content=f"[{topic}] {decision}",
            memory_type=MemoryType.DECISION,
            priority=priority_enum,
            metadata={"topic": topic}
        )
    
    # 检索决策历史
    print("\n检索: '为什么选择PostgreSQL'")
    results = memory.search("为什么选择PostgreSQL", top_k=3)
    for entry, score in results:
        print(f"  [{score:.2f}] {entry.content}")


def demo_memory_stats():
    """统计信息示例"""
    print("\n" + "=" * 60)
    print("示例5: 记忆统计")
    print("=" * 60)
    
    memory = MemoryStore(storage_path="/tmp/demo_memory.json")
    
    stats = memory.get_stats()
    print(f"\n记忆统计:")
    print(f"  总记忆数: {stats['total_memories']}")
    print(f"  按类型分布:")
    for mem_type, count in stats['by_type'].items():
        print(f"    - {mem_type}: {count}")
    print(f"  按优先级分布:")
    for priority, count in stats['by_priority'].items():
        print(f"    - 优先级{priority}: {count}")


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("Memory Enhanced System - 使用示例")
    print("=" * 60)
    
    demo_basic_usage()
    demo_conversation_context()
    demo_skill_memory()
    demo_decision_tracking()
    demo_memory_stats()
    
    print("\n" + "=" * 60)
    print("示例完成!")
    print("=" * 60)
    
    # 清理临时文件
    if os.path.exists("/tmp/demo_memory.json"):
        os.remove("/tmp/demo_memory.json")
        print("\n已清理临时存储文件")


if __name__ == "__main__":
    main()
