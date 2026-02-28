---
name: quick-templates
description: 快速任务模板匹配器 - 预定义常用任务模板，支持关键词快速触发
---

# Quick Templates - 快速任务模板

预定义的常用任务模板系统，支持关键词快速匹配和参数提取，让用户能够快速调用常用功能。

## 核心功能

### 1. 关键词匹配
- 智能关键词识别
- 多别名支持
- 模糊匹配
- 优先级排序

### 2. 参数提取
- 自动参数解析
- 类型转换
- 默认值处理
- 验证检查

### 3. 模板管理
- 动态模板注册
- 模板分类
- 权限控制
- 版本管理

### 4. 执行引擎
- 同步/异步执行
- 超时控制
- 错误处理
- 结果格式化

## 快速开始

### 安装

```bash
pip install -r requirements.txt
```

### 基础使用

```python
from matcher import TemplateMatcher

# 创建匹配器
matcher = TemplateMatcher()

# 匹配用户输入
result = matcher.match("早报")
if result:
    print(f"匹配到模板: {result.template.name}")
    print(f"参数: {result.parameters}")
```

## 内置模板

### 早报生成

| 属性 | 值 |
|------|-----|
| **触发词** | `早报`, `morning report` |
| **功能** | 生成股市早报 |
| **参数** | 无 |

**示例**:
```
用户: 早报
系统: 立即执行早报生成任务...
```

### 股票分析

| 属性 | 值 |
|------|-----|
| **触发词** | `分析股票`, `analyze stock` |
| **功能** | 分析指定股票 |
| **参数** | 股票代码或名称 |

**示例**:
```
用户: 分析股票 000001
系统: 分析平安银行...
用户: 分析股票 贵州茅台
系统: 分析贵州茅台...
```

### 网页部署

| 属性 | 值 |
|------|-----|
| **触发词** | `部署`, `deploy` |
| **功能** | 部署项目到Vercel |
| **参数** | 项目路径 |

**示例**:
```
用户: 部署 /path/to/project
系统: 开始部署项目到Vercel...
```

### 网络搜索

| 属性 | 值 |
|------|-----|
| **触发词** | `搜索`, `search` |
| **功能** | 搜索网络信息 |
| **参数** | 搜索关键词 |

**示例**:
```
用户: 搜索 OpenClaw最新动态
系统: 搜索中...
```

### 代码审查

| 属性 | 值 |
|------|-----|
| **触发词** | `审查代码`, `code review` |
| **功能** | 审查代码文件 |
| **参数** | 文件路径 |

**示例**:
```
用户: 审查代码 /path/to/file.py
系统: 开始代码审查...
```

### 任务状态

| 属性 | 值 |
|------|-----|
| **触发词** | `状态`, `status` |
| **功能** | 查看当前任务状态 |
| **参数** | 无 |

**示例**:
```
用户: 状态
系统: 当前有3个任务运行中...
```

### 帮助

| 属性 | 值 |
|------|-----|
| **触发词** | `帮助`, `help` |
| **功能** | 显示可用模板列表 |
| **参数** | 无 |

## 自定义模板

### 注册新模板

```python
from matcher import Template, TemplateMatcher

# 定义模板
template = Template(
    name="weather",
    aliases=["天气", "weather"],
    description="查询天气",
    handler=query_weather,
    parameters=[
        {"name": "city", "type": "string", "required": False, "default": "北京"}
    ]
)

# 注册模板
matcher.register(template)

# 处理函数
def query_weather(city="北京"):
    # 查询天气逻辑
    return f"{city}今天晴，25°C"
```

### 模板配置

```python
# 模板配置
TEMPLATE_CONFIG = {
    "weather": {
        "aliases": ["天气", "weather", "tq"],
        "description": "查询指定城市天气",
        "handler": "handlers.weather.query",
        "parameters": {
            "city": {
                "type": "string",
                "required": False,
                "default": "北京",
                "description": "城市名称"
            }
        }
    }
}
```

## 高级匹配

### 模糊匹配

```python
# 启用模糊匹配
matcher = TemplateMatcher(fuzzy_match=True, threshold=0.8)

# 即使输入有轻微错误也能匹配
result = matcher.match("早抱")  # 匹配到 "早报"
```

### 上下文匹配

```python
# 带上下文的匹配
context = {"last_command": "股票分析"}
result = matcher.match("再来一个", context=context)
```

## 参数解析

### 自动类型转换

```python
# 定义参数类型
template = Template(
    name="calculate",
    aliases=["计算"],
    parameters=[
        {"name": "a", "type": "int"},
        {"name": "b", "type": "int"},
        {"name": "operator", "type": "string", "enum": ["+", "-", "*", "/"]}
    ]
)

# 输入: "计算 10 20 +"
# 解析: {"a": 10, "b": 20, "operator": "+"}
```

### 复杂参数

```python
# 支持JSON格式参数
template = Template(
    name="config",
    aliases": ["配置"],
    parameters=[
        {"name": "settings", "type": "json"}
    ]
)

# 输入: 配置 {"theme": "dark", "lang": "zh"}
```

## 执行控制

### 异步执行

```python
import asyncio

async def execute_template(template, params):
    result = await matcher.execute_async(template, params)
    return result

# 使用
asyncio.run(execute_template(template, {}))
```

### 超时控制

```python
# 设置超时
result = matcher.execute(template, params, timeout=30)
```

### 错误处理

```python
try:
    result = matcher.execute(template, params)
except TemplateNotFoundError:
    print("模板不存在")
except ParameterError as e:
    print(f"参数错误: {e}")
except ExecutionError as e:
    print(f"执行错误: {e}")
```

## 集成示例

### 与ChatBot集成

```python
class ChatBot:
    def __init__(self):
        self.matcher = TemplateMatcher()
    
    def handle_message(self, message):
        # 先尝试匹配模板
        result = self.matcher.match(message)
        if result:
            return self.execute_template(result)
        
        # 未匹配到模板，使用AI回复
        return self.ai_reply(message)
```

### 与OpenClaw集成

```python
# 在OpenClaw中注册快速模板
from openclaw import register_quick_template

@register_quick_template(
    aliases=["日报"],
    description="生成工作日报"
)
def daily_report():
    # 生成日报逻辑
    pass
```

## 测试

```bash
# 运行测试
python -m pytest tests/ -v

# 测试匹配功能
python -m pytest tests/test_matcher.py::TestMatching -v

# 测试参数解析
python -m pytest tests/test_matcher.py::TestParameterParsing -v
```

## 性能优化

### 缓存

```python
# 启用匹配缓存
matcher = TemplateMatcher(cache_enabled=True)
```

### 预编译

```python
# 预编译正则表达式
matcher.precompile_patterns()
```

## 更新日志

### v1.0.0
- ✅ 关键词匹配引擎
- ✅ 参数自动提取
- ✅ 7个内置模板
- ✅ 自定义模板注册
- ✅ 模糊匹配支持
- ✅ 异步执行
- ✅ 超时控制

## 相关链接

- [matcher.py](./matcher.py) - 核心匹配器实现
- [INTEGRATION.md](./INTEGRATION.md) - 集成指南
- [示例代码](./examples/)
