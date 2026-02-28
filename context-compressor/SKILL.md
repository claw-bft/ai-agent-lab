---
name: context-compressor
description: 上下文压缩工具 - 自动总结长对话，减少token消耗，提升AI处理效率
---

# Context Compressor - 上下文压缩工具

智能压缩长对话历史，在保留关键信息的同时减少token消耗，让AI能够处理更长的上下文。

## 核心功能

### 1. 智能消息压缩
- 保留最近N条完整消息（默认20条）
- 对早期消息自动生成摘要
- 提取关键决策点和行动项

### 2. Token优化
- 自动检测上下文长度
- 在超过阈值时触发压缩
- 可配置的压缩策略

### 3. 信息保留
- 保留关键决策记录
- 追踪已完成的任务
- 维护对话连贯性

## 安装依赖

```bash
# 无需额外依赖，纯Python标准库实现
```

## 使用示例

### 基本用法

```python
from compressor import compress_conversation, should_compress

# 模拟长对话
messages = [
    {'role': 'user', 'content': '帮我分析股票'},
    {'role': 'assistant', 'content': '好的，请提供股票代码'},
    {'role': 'user', 'content': '000001.SZ'},
    # ... 更多消息
] * 20  # 40轮对话

# 压缩对话
compressed = compress_conversation(messages, max_messages=10)
print(f"原消息数: {len(messages)}")
print(f"压缩后: {len(compressed)}")
```

### 判断是否压缩

```python
from compressor import should_compress

# 检查是否需要压缩
current_tokens = 80000  # 当前token数
if should_compress(current_tokens, max_tokens=131072):
    print("需要压缩上下文")
    compressed = compress_conversation(messages)
```

### 在Agent中集成

```python
class SmartAgent:
    def __init__(self):
        self.messages = []
        self.max_context = 20
    
    def chat(self, user_input):
        # 添加用户消息
        self.messages.append({'role': 'user', 'content': user_input})
        
        # 检查并压缩上下文
        if len(self.messages) > self.max_context * 2:
            from compressor import compress_conversation
            self.messages = compress_conversation(
                self.messages, 
                max_messages=self.max_context
            )
        
        # 调用AI生成回复...
        response = self._call_ai(self.messages)
        
        # 记录回复
        self.messages.append({'role': 'assistant', 'content': response})
        return response
```

## API参考

### `compress_conversation(messages, max_messages=20)`

压缩对话历史。

**参数:**
- `messages` (list): 消息列表，每项为 `{'role': str, 'content': str}`
- `max_messages` (int): 保留的最近消息数量

**返回:**
- 压缩后的消息列表（包含摘要+最近消息）

### `should_compress(context_tokens, max_tokens=131072)`

判断是否需要压缩。

**参数:**
- `context_tokens` (int): 当前上下文token数
- `max_tokens` (int): 最大token限制

**返回:**
- `bool`: 是否需要压缩

### `summarize_messages(messages)`

生成消息摘要（内部函数）。

**参数:**
- `messages` (list): 要总结的消息列表

**返回:**
- `str`: 摘要文本

## 压缩策略

1. **保留最近消息**: 最近的N条消息完整保留，确保上下文连贯
2. **提取关键信息**: 从早期消息中提取决策点和行动项
3. **生成结构化摘要**: 格式 `[对话摘要] 关键决策: X项; 执行任务: Y项`

## 使用场景

- **长对话Agent**: 客服机器人、个人助手
- **多轮分析任务**: 股票分析、代码审查
- **文档处理**: 长文档问答、论文阅读助手
- **节省API成本**: 减少token使用量

## 文件结构

```
context-compressor/
├── compressor.py      # 核心压缩模块
└── SKILL.md          # 本文件
```

## 更新日志

### 2026-02-28
- ✅ 创建 SKILL.md 使用文档
- ✅ 添加完整使用示例
- ✅ 补充 API 参考文档
