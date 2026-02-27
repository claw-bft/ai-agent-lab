# Research Pro 技能包

## 功能模块

### 1. 数据分析基础设施
- 多源数据清洗与可视化
- 自然语言驱动数据分析
- 定时任务自动化调度
- 实时联网信息检索

### 2. 自动化流程编排
- 日报/周报自动生成
- 竞品动态实时监控
- 决策信息即时获取
- 7×24小时持续监控

### 3. AI增强研究能力
- 多轮深度调研报告生成
- 本质问题拆解 (第一性原理)
- 实时信源交叉验证
- 研究效率数量级提升

## 依赖工具
- tavily-search
- brave-search
- kimi_search (OpenClaw内置)
- web_search (OpenClaw内置)

## 配置说明

### Tavily API (推荐)
获取 API Key: https://tavily.com

```bash
export TAVILY_API_KEY="tvly-xxxxxxxx"
python search_adapter.py
```

### Brave Search (备选)
获取 API Key: https://brave.com/search/api

```bash
export BRAVE_API_KEY="BSxxxxxxxx"
python search_adapter.py
```

### OpenClaw 内置搜索 (无需配置)
如果运行在 OpenClaw 环境中，`kimi_search` 和 `web_search` 工具会自动可用。

## 使用示例

### 基本搜索

```python
from search_adapter import SearchAdapter, search

# 自动检测最佳后端
adapter = SearchAdapter()
print(adapter.get_status())

# 执行搜索
results = search("AI最新进展", limit=5)
for r in results:
    print(f"{r.title}: {r.url}")
```

### 指定后端搜索

```python
from search_adapter import SearchAdapter

# 强制使用 Tavily
adapter = SearchAdapter(preferred_backend="tavily")
results = adapter.search("Python异步编程", limit=5)

# 强制使用 Brave
adapter = SearchAdapter(preferred_backend="brave")
results = adapter.search("机器学习教程", limit=5)
```

### 批量搜索

```python
from search_adapter import batch_search

queries = ["Python", "Go", "Rust"]
results = batch_search(queries, limit=3)

for query, items in results.items():
    print(f"\n{query}:")
    for item in items:
        print(f"  - {item.title}")
```

### 高级搜索选项

```python
from search_adapter import SearchAdapter

adapter = SearchAdapter(preferred_backend="tavily")

# Tavily 深度搜索
results = adapter.search(
    "量子计算最新突破",
    limit=10,
    depth="advanced",  # basic 或 advanced
    include_answer=True  # 包含AI生成的答案
)
```

## 后端优先级

1. **Tavily** - 专为AI设计的搜索API，结果质量最高
2. **Brave Search** - 隐私友好的搜索API
3. **kimi_search** - OpenClaw内置搜索工具
4. **web_search** - OpenClaw备用搜索工具

## 错误处理与降级

SearchAdapter 自动处理错误并降级到可用后端：

```python
adapter = SearchAdapter()  # 首选 Tavily

# 如果 Tavily 失败，自动降级到 Brave
# 如果 Brave 失败，自动降级到 kimi_search
# 以此类推...
results = adapter.search("查询内容")
```

## 测试

```bash
# 运行测试
python tests/test_search_adapter.py

# 需要环境变量的集成测试
export TAVILY_API_KEY="your-key"
python tests/test_search_adapter.py
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 文件结构

```
research-pro/
├── search_adapter.py      # 核心搜索适配器
├── requirements.txt       # 依赖配置
├── tests/
│   └── test_search_adapter.py  # 测试文件
└── SKILL.md              # 本文件
```
