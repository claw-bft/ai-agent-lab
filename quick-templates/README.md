# Quick Templates

快速任务模板解析器 - 检测用户输入，匹配预定义模板，快速执行任务。

## 功能特性

- **关键词匹配**: 检测用户输入的前几个词
- **参数提取**: 解析后续内容作为参数
- **快速执行**: 直接调用对应技能，无需完整描述

## 快速开始

```bash
# 查看帮助
python3 matcher.py

# 测试模板匹配
python3 matcher.py "早报"
python3 matcher.py "分析股票 000001"
python3 matcher.py "搜索 OpenClaw最新动态"
```

## 模板列表

| 模板 | 关键词 | 描述 |
|------|--------|------|
| morning_report | 早报 / morning report | 生成股市早报 |
| stock_analysis | 分析股票 / analyze stock | 分析指定股票 |
| deploy | 部署 / deploy | 部署项目到Vercel |
| search | 搜索 / search | 网络搜索 |
| code_review | 审查代码 / code review | 审查代码文件 |
| status | 状态 / status | 查看当前任务状态 |
| help | 帮助 / help | 显示可用模板列表 |

## 安装

无需额外依赖，纯Python标准库实现。

## Python API

```python
from matcher import match_template, get_help_text

# 匹配用户输入
result = match_template("分析股票 000001")
if result:
    print(f"匹配模板: {result['template_id']}")
    print(f"参数: {result['params']}")

# 获取帮助文本
help_text = get_help_text()
print(help_text)
```

## 添加新模板

编辑 `matcher.py` 中的 `TEMPLATES` 字典：

```python
TEMPLATES = {
    'your_template': {
        'keywords': ['关键词1', '关键词2'],
        'description': '模板描述',
        'handler': '处理模块',
        'params': ['参数名']
    }
}
```

## 测试

```bash
# 运行测试
python3 -m pytest tests/ -v
```

## 许可证

MIT
