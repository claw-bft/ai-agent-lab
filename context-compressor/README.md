# Context Compressor

上下文压缩工具 - 自动总结长对话，减少token消耗，提升AI处理效率。

## 功能特性

- **智能消息压缩**: 保留最近N条完整消息，对早期消息自动生成摘要
- **Token优化**: 自动检测上下文长度，在超过阈值时触发压缩
- **信息保留**: 保留关键决策记录，追踪已完成的任务，维护对话连贯性

## 快速开始

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

## 安装

无需额外依赖，纯Python标准库实现。

```bash
# 直接复制 compressor.py 到项目中使用
```

## API文档

详见 [SKILL.md](./SKILL.md)

## 测试

```bash
# 运行测试
python3 -m pytest tests/ -v

# 或运行单个测试文件
python3 tests/test_compressor.py
```

## 使用场景

- **长对话Agent**: 客服机器人、个人助手
- **多轮分析任务**: 股票分析、代码审查
- **文档处理**: 长文档问答、论文阅读助手
- **节省API成本**: 减少token使用量

## 许可证

MIT
