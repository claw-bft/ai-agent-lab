# News Intelligence Hub

热点新闻抓取、关联分析与可视化系统

## 功能特性

- **多源新闻抓取**: 支持微博、知乎、今日头条、36氪等热点源
- **智能关联分析**: 基于语义相似度分析新闻之间的关联关系
- **影响评估**: 多维度评估新闻的社会、经济、政治、科技影响
- **可视化仪表板**: 交互式网络图、时间线、热力图等

## 安装依赖

```bash
pip install aiohttp numpy scikit-learn networkx
```

## 使用方法

```python
from engine import NewsIntelligenceEngine
import asyncio

engine = NewsIntelligenceEngine()

# 抓取新闻
news_items = asyncio.run(engine.fetch_news())

# 分析关联
relations = engine.analyze_correlations(news_items)

# 评估影响
for item in news_items:
    impact = engine.assess_impact(item)
    print(f"{item.title}: 影响评分 {impact.overall_score}")
```

## 配置文件

编辑 `config.json` 自定义数据源和分析参数：

```json
{
  "sources": [...],
  "analysis": {
    "correlation": {"threshold": 0.75},
    "impact": {"dimensions": ["social", "economic", "political", "tech"]}
  }
}
```

## 可视化仪表板

打开 `dashboard.html` 查看实时热点新闻可视化。

## 定时任务

默认每30分钟自动抓取和分析：

```cron
*/30 * * * * python engine.py
```

## License

MIT
