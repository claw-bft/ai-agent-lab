# Memory Enhanced

记忆增强系统 - 基于向量数据库的长期记忆，支持跨会话上下文保持

## 功能特性

- **向量记忆存储**: 基于语义相似度的记忆检索
- **记忆类型分类**: 事实、偏好、决策、上下文、技能、对话
- **智能过期策略**: 根据优先级自动管理记忆生命周期
- **跨会话保持**: 记忆持久化到磁盘，重启后依然可用
- **记忆检索**: 语义搜索 + 时间衰减排序
- **记忆压缩**: 自动合并相似记忆，避免冗余

## 安装

```bash
pip install numpy
```

## 快速开始

```python
from memory_system import MemoryEnhancedSystem

# 初始化记忆系统
memory = MemoryEnhancedSystem()

# 存储记忆
memory.store(
    content="用户偏好使用Python进行数据分析",
    memory_type="preference",
    priority="high",
    tags=["user-preference"]
)

# 检索记忆
results = memory.retrieve("Python相关偏好", limit=5)
for memory in results:
    print(f"{memory.content} (相似度: {memory.score:.2f})")
```

## 核心概念

### 记忆类型 (MemoryType)

| 类型 | 说明 | 使用场景 |
|------|------|----------|
| `fact` | 事实性记忆 | 存储客观信息，如"用户住在上海" |
| `preference` | 用户偏好 | 存储用户喜好，如"喜欢深色主题" |
| `decision` | 历史决策 | 记录重要决策及其原因 |
| `context` | 项目上下文 | 当前项目状态和进度 |
| `skill` | 技能使用记录 | 用户使用技能的历史 |
| `conversation` | 对话片段 | 重要的对话内容 |

### 记忆优先级 (MemoryPriority)

| 优先级 | 分值 | 过期策略 |
|--------|------|----------|
| `CRITICAL` | 5 | 永不过期 |
| `HIGH` | 4 | 长期保留（90天） |
| `MEDIUM` | 3 | 定期清理（30天） |
| `LOW` | 2 | 快速过期（7天） |
| `EPHEMERAL` | 1 | 会话结束即清除 |

## 详细使用指南

### 1. 初始化记忆存储

```python
from memory_system import MemoryStore

# 使用默认存储路径
store = MemoryStore()

# 或指定自定义路径
store = MemoryStore(storage_path="/path/to/memory.json")
```

### 2. 存储记忆

```python
from memory_system import MemoryType, MemoryPriority

# 存储用户偏好
memory_id = store.store(
    content="用户喜欢使用Python进行数据分析",
    memory_type=MemoryType.PREFERENCE,
    priority=MemoryPriority.HIGH,
    metadata={
        "preferences": {"language": "Python", "domain": "data_analysis"},
        "source": "user_input"
    }
)

# 存储项目上下文
memory_id = store.store(
    content="当前正在开发股票分析系统",
    memory_type=MemoryType.CONTEXT,
    priority=MemoryPriority.CRITICAL,
    metadata={"project": "stock-analyzer", "status": "in_progress"}
)
```

### 3. 语义搜索

```python
# 搜索相关记忆
results = store.search("编程语言偏好", top_k=5)

for entry, similarity in results:
    print(f"内容: {entry.content}")
    print(f"类型: {entry.memory_type.value}")
    print(f"相似度: {similarity:.3f}")
    print(f"访问次数: {entry.access_count}")
    print("---")

# 按类型过滤搜索
results = store.search(
    query="项目进度",
    top_k=3,
    memory_type=MemoryType.CONTEXT
)
```

### 4. 按类型获取记忆

```python
# 获取所有用户偏好
preferences = store.get_by_type(MemoryType.PREFERENCE, limit=10)

# 获取所有事实
facts = store.get_by_type(MemoryType.FACT, limit=20)
```

### 5. 获取用户偏好汇总

```python
# 自动汇总所有偏好记忆
all_prefs = store.get_user_preferences()
print(all_prefs)
# 输出: {'language': 'Python', 'domain': 'data_analysis', 'theme': 'dark'}
```

### 6. 获取近期上下文

```python
# 获取最近24小时的记忆
recent = store.get_recent_context(hours=24)

# 获取最近一周的记忆
weekly = store.get_recent_context(hours=168)
```

### 7. 记忆管理

```python
# 根据ID检索特定记忆
entry = store.retrieve(memory_id)
if entry:
    print(f"找到记忆: {entry.content}")

# 删除记忆
deleted = store.delete(memory_id)

# 清理过期记忆
count = store.cleanup_expired()
print(f"清理了 {count} 条过期记忆")

# 获取统计信息
stats = store.get_stats()
print(f"总记忆数: {stats['total_memories']}")
print(f"活跃记忆: {stats['active_memories']}")
print(f"按类型分布: {stats['by_type']}")
```

## 使用 MemoryEnhancedAgent

`MemoryEnhancedAgent` 提供了更高层次的抽象，适合直接集成到Agent中：

```python
from memory_system import create_memory_agent

# 创建记忆增强的Agent
agent = create_memory_agent("my-agent", storage_path="agent_memory.json")

# 记住信息
agent.remember(
    content="用户要求每天早上8:30发送股票早报",
    memory_type="fact",
    priority="high"
)

# 回忆相关信息
results = agent.recall("股票早报", top_k=3)
for r in results:
    print(f"[{r['type']}] {r['content']} (相似度: {r['similarity']})")

# 获取用户偏好
prefs = agent.get_preferences()

# 获取近期上下文
context = agent.get_recent_context(hours=48)

# 遗忘特定记忆
agent.forget(memory_id)

# 查看统计
stats = agent.stats()
```

## 上下文窗口管理

```python
from memory_system import ContextWindow

# 创建上下文窗口（默认4000 tokens）
context = ContextWindow(max_tokens=4000)

# 添加记忆到上下文
context.add(memory_entry)

# 获取格式化的上下文字符串
context_str = context.get_context_string()
print(context_str)
# 输出:
# [03-01 10:30] preference: 用户喜欢使用Python
# [03-01 10:35] context: 当前正在开发项目

# 清空上下文
context.clear()
```

## CLI使用

```bash
# 存储记忆
./memory-cli store --content "重要信息" --type fact --priority high

# 检索记忆
./memory-cli retrieve --query "关键词" --limit 5

# 列出所有记忆
./memory-cli list

# 清理过期记忆
./memory-cli cleanup
```

## 项目结构

```
memory-enhanced/
├── memory_system.py       # 核心记忆系统实现
├── memory-cli             # CLI工具
├── examples.py            # 使用示例
├── tests/                # 测试目录
│   ├── test_memory_system.py
│   └── test_performance.py
├── README.md             # 使用文档
└── SKILL.md              # 技能文档
```

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行单元测试
pytest tests/test_memory_system.py -v

# 运行性能测试
pytest tests/test_performance.py -v
```

## 性能优化建议

1. **定期清理过期记忆**: 调用 `cleanup_expired()` 释放存储空间
2. **合理设置优先级**: 避免过多 CRITICAL 优先级记忆导致存储膨胀
3. **使用合适的 top_k**: 搜索时根据需求设置合理的返回数量
4. **批量操作**: 大量记忆操作时考虑批量处理

## 架构设计

### 核心组件

- **MemoryStore**: 记忆存储和管理的核心类
- **MemoryEntry**: 记忆条目数据模型
- **SimpleEmbedding**: 简单嵌入生成器（无需外部API）
- **ContextWindow**: 上下文窗口管理
- **MemoryEnhancedAgent**: Agent集成封装

### 存储格式

记忆以JSON格式持久化到磁盘：

```json
{
  "memories": {
    "memory_id_1": {
      "memory_id": "memory_id_1",
      "content": "记忆内容",
      "memory_type": "preference",
      "priority": 4,
      "timestamp": 1709251200,
      "last_accessed": 1709251200,
      "access_count": 5,
      "metadata": {},
      "embedding": [...],
      "expiration": null
    }
  },
  "vocab": {...},
  "vocab_size": 100
}
```

## 最佳实践

1. **为记忆选择合适的类型**: 帮助系统更好地理解和组织信息
2. **设置合理的优先级**: 避免重要信息被过早清理
3. **使用元数据**: 存储额外的上下文信息便于后续检索
4. **定期备份**: 重要记忆数据建议定期备份
5. **监控统计**: 定期查看 `get_stats()` 了解记忆使用情况

## 故障排除

### 记忆检索不到
- 检查记忆是否过期
- 尝试使用不同的查询词
- 确认记忆类型是否正确

### 存储文件损坏
- 备份当前文件
- 删除损坏的存储文件重新初始化
- 从备份恢复

### 性能下降
- 清理过期记忆
- 减少存储的记忆数量
- 检查是否有大量高优先级记忆

## 贡献指南

欢迎提交Issue和PR来改进记忆系统功能。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持向量记忆存储
- 语义搜索功能
- 记忆类型和优先级管理

## License

MIT
