---
name: memory-enhanced
description: 记忆增强系统 - 基于向量数据库的长期记忆，支持跨会话上下文保持
---

# Memory Enhanced System

基于向量数据库的长期记忆系统，支持跨会话上下文保持。让AI Agent能够"记住"用户偏好、历史决策和项目上下文。

## 核心功能

- **向量记忆存储**: 基于语义相似度的记忆检索
- **记忆类型分类**: 事实、偏好、决策、上下文、技能、对话
- **智能过期策略**: 根据优先级自动管理记忆生命周期
- **跨会话保持**: 记忆持久化到磁盘，重启后依然可用
- **记忆检索**: 语义搜索 + 时间衰减排序
- **记忆压缩**: 自动合并相似记忆，避免冗余

## 架构

```
memory-enhanced/
├── memory_system.py       # 核心记忆系统实现
├── memory-cli              # CLI工具
├── test_memory_system.py   # 测试用例
└── SKILL.md               # 本文档
```

### 核心组件

| 组件 | 类名 | 功能 |
|------|------|------|
| 记忆系统 | `MemoryEnhancedSystem` | 核心API，记忆CRUD操作 |
| 记忆条目 | `MemoryEntry` | 单个记忆的数据结构 |
| 嵌入生成器 | `SimpleEmbedding` | 本地文本向量化(无需API) |
| 记忆类型 | `MemoryType` | 记忆分类枚举 |
| 优先级 | `MemoryPriority` | 记忆重要性级别 |

## 使用方式

### 方式1: CLI工具

```bash
# 存储记忆
./memory-cli store \
  --content "用户偏好使用Python进行数据分析" \
  --type preference \
  --priority high \
  --tag "user-preference"

# 检索记忆
./memory-cli retrieve \
  --query "用户喜欢什么编程语言" \
  --limit 5

# 查看记忆统计
./memory-cli stats

# 清理过期记忆
./memory-cli cleanup

# 导出记忆
./memory-cli export --output memories.json

# 导入记忆
./memory-cli import --input memories.json
```

### 方式2: Python API

```python
from memory_system import MemoryEnhancedSystem, MemoryType, MemoryPriority

# 创建记忆系统
memory = MemoryEnhancedSystem(storage_path="./memory_store")

# 存储记忆
memory_id = memory.store(
    content="用户偏好使用Python进行数据分析",
    memory_type=MemoryType.PREFERENCE,
    priority=MemoryPriority.HIGH,
    metadata={"tag": "user-preference", "topic": "programming"}
)

# 检索记忆
results = memory.retrieve(
    query="用户喜欢什么编程语言",
    limit=5,
    memory_type=MemoryType.PREFERENCE
)

for entry, score in results:
    print(f"[{score:.2f}] {entry.content}")

# 获取相关上下文
context = memory.get_context_for(
    query="数据分析项目",
    max_items=3
)
```

## 记忆类型

| 类型 | 说明 | 示例 |
|------|------|------|
| FACT | 事实性记忆 | "Python 3.12发布了" |
| PREFERENCE | 用户偏好 | "用户喜欢暗色主题" |
| DECISION | 历史决策 | "决定使用PostgreSQL" |
| CONTEXT | 项目上下文 | "当前在开发股票分析系统" |
| SKILL | 技能使用记录 | "使用过finance-pro查询股票" |
| CONVERSATION | 对话片段 | "用户询问如何部署到Vercel" |

## 优先级与过期策略

| 优先级 | 保留时间 | 用途 |
|--------|----------|------|
| CRITICAL | 永不过期 | 关键配置、安全信息 |
| HIGH | 90天 | 重要偏好、核心决策 |
| MEDIUM | 30天 | 一般上下文 |
| LOW | 7天 | 临时信息 |
| EPHEMERAL | 会话结束 | 临时计算结果 |

## 与Agent协作协议集成

```python
from agent_protocol import CollaborationAgent
from memory_system import MemoryEnhancedSystem

class MemoryEnhancedAgent(CollaborationAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory = MemoryEnhancedSystem()
    
    def _handle_task(self, message):
        # 检索相关历史记忆
        context = self.memory.get_context_for(
            message.payload.get("description", "")
        )
        
        # 执行任务...
        
        # 存储执行结果
        self.memory.store(
            content=f"完成任务: {task_description}",
            memory_type=MemoryType.SKILL,
            priority=MemoryPriority.MEDIUM
        )
```

## 存储格式

记忆以JSON格式持久化:

```json
{
  "memory_id": "a1b2c3d4",
  "content": "用户偏好使用Python",
  "memory_type": "preference",
  "priority": 4,
  "timestamp": 1700000000,
  "last_accessed": 1700000100,
  "access_count": 5,
  "metadata": {"tag": "programming"},
  "embedding": [0.1, 0.2, ...],
  "expiration": null
}
```

## 配置选项

```python
memory = MemoryEnhancedSystem(
    storage_path="./memory_store",
    embedding_dim=128,           # 向量维度
    max_memories=10000,          # 最大记忆数
    cleanup_interval=3600        # 清理间隔(秒)
)
```

## 性能指标

- 存储操作: < 10ms
- 检索操作(1000条记忆): < 50ms
- 内存占用: ~500KB/1000条记忆
- 磁盘占用: ~2MB/1000条记忆

## 更新日志

### 2026-02-27
- ✅ 实现核心记忆系统 (memory_system.py)
- ✅ 实现本地嵌入生成器 (无需外部API)
- ✅ 实现CLI工具 (memory-cli)
- ✅ 添加完整测试用例
- ✅ 支持记忆持久化和导入导出
