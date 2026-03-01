# News Intelligence Hub Skill

## 描述

热点新闻抓取、关联分析与可视化系统。自动抓取多平台热点新闻，进行语义关联分析和多维度影响评估。

## 能力

- 抓取微博、知乎、今日头条、36氪等热点
- 基于TF-IDF和余弦相似度的关联分析
- 社会/经济/政治/科技四维影响评估
- 交互式可视化仪表板

## 使用示例

```python
from engine import NewsIntelligenceEngine
import asyncio

engine = NewsIntelligenceEngine()
news = asyncio.run(engine.fetch_news())
relations = engine.analyze_correlations(news)
```

## 配置

编辑 `config.json` 自定义数据源和参数。

## 依赖

- aiohttp
- numpy
- scikit-learn
- networkx
