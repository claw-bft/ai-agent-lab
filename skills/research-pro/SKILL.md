---
name: research-pro
description: 跨领域通用研究技能包 - 数据分析、自动化流程、AI增强研究
---

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
- deepresearch-conversation
- data-analyzer
- cron

## 使用示例

```bash
# 深度研究
research-pro deep --topic "新能源汽车电池技术发展趋势" --depth comprehensive

# 数据分析
research-pro analyze --file data.csv --query "计算各品类销售额占比"

# 定时任务
research-pro cron add --name "daily-report" --schedule "0 9 * * *" --task generate-report

# 实时搜索
research-pro search --query "最新AI编程工具发布" --sources news,blog,twitter

# 竞品监控
research-pro monitor --competitors "OpenAI,Anthropic,Google" --alerts product-launch
```
