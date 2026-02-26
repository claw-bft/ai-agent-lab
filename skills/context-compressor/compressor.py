#!/usr/bin/env python3
"""
上下文压缩工具
自动总结长对话，减少token消耗
"""

import json
import re
from datetime import datetime

def compress_conversation(messages, max_messages=20):
    """
    压缩对话历史
    - 保留最近的max_messages条
    - 对更早的消息进行总结
    """
    if len(messages) <= max_messages:
        return messages
    
    # 保留最近的消息
    recent = messages[-max_messages:]
    
    # 对早期消息进行总结
    early = messages[:-max_messages]
    summary = summarize_messages(early)
    
    # 组合：总结 + 最近消息
    return [{
        'role': 'system',
        'content': f'[对话摘要] {summary}',
        'timestamp': datetime.now().isoformat()
    }] + recent

def summarize_messages(messages):
    """总结消息列表"""
    # 提取关键信息
    decisions = []
    actions = []
    
    for msg in messages:
        content = msg.get('content', '')
        
        # 检测决策点
        if any(kw in content for kw in ['决定', '选择', '确定', '方案', '结论']):
            decisions.append(content[:100])
        
        # 检测行动项
        if any(kw in content for kw in ['完成', '部署', '创建', '修改', '删除']):
            actions.append(content[:100])
    
    # 生成摘要
    parts = []
    if decisions:
        parts.append(f"关键决策: {len(decisions)}项")
    if actions:
        parts.append(f"执行任务: {len(actions)}项")
    
    return '; '.join(parts) if parts else f"共{len(messages)}轮对话"

def should_compress(context_tokens, max_tokens=131072):
    """判断是否需要压缩"""
    return context_tokens > max_tokens * 0.5

if __name__ == '__main__':
    # 测试
    test_messages = [
        {'role': 'user', 'content': '你好'},
        {'role': 'assistant', 'content': '你好！有什么可以帮忙的？'},
        {'role': 'user', 'content': '帮我生成早报'},
        {'role': 'assistant', 'content': '好的，正在生成...'},
    ] * 10  # 模拟40轮对话
    
    compressed = compress_conversation(test_messages, max_messages=5)
    print(f"原消息数: {len(test_messages)}")
    print(f"压缩后: {len(compressed)}")
    print(f"摘要: {compressed[0]['content']}")
