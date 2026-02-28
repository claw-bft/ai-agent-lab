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
│   └── test_memory_system.py
└── SKILL.md              # 技能文档
```

## 测试

```bash
pytest tests/ -v
```

## License

MIT
