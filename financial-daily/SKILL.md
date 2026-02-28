---
name: financial-daily
description: 财经资讯日报生成器 - 深度采集财经热点，自动生成日报并推送到GitHub
---

# Financial Daily Generator

自动采集财经新闻和市场数据，生成结构化日报并推送到GitHub仓库。

## 核心功能

- **新闻采集**: 自动抓取财经热点新闻
- **市场分析**: 获取主要股票指数行情
- **日报生成**: 生成Markdown格式的结构化日报
- **自动推送**: 推送到GitHub仓库保存

## 使用方法

### 命令行执行

```bash
# 生成今日日报
cd /root/.openclaw/workspace/ai-agent-lab/financial-daily
python3 generator.py

# 查看生成的报告
ls -la reports/
```

### 定时任务配置

```json
{
  "schedule": "0 9 * * *",
  "command": "python3 /root/.openclaw/workspace/ai-agent-lab/financial-daily/generator.py",
  "description": "每日上午9点生成财经日报"
}
```

## 日报内容结构

```markdown
# 财经资讯日报 - 2026-02-28

## 📊 市场概览
- 上证指数: 3000.00 (+0.5%)
- 深证成指: 10000.00 (+0.8%)
- 创业板指: 2000.00 (+1.2%)

## 🔥 热点资讯
1. [新闻标题](链接) - 摘要...
2. [新闻标题](链接) - 摘要...

## 📈 行业动态
- 科技: ...
- 金融: ...

## 💡 投资机会
- 关注板块: ...
- 风险提示: ...
```

## 配置说明

### 环境变量

```bash
# GitHub配置
export GITHUB_TOKEN="your_token"
export GITHUB_REPO="claw-bft/ai-agent-lab"

# 输出目录
export OUTPUT_DIR="/root/.openclaw/workspace/financial-daily"
```

### 依赖技能包

- **research-pro**: 新闻搜索和采集
- **finance-pro**: 市场数据获取

## 代码示例

```python
from generator import FinancialNewsDaily

# 创建日报生成器
daily = FinancialNewsDaily()

# 采集新闻
news = daily.collect_news()

# 获取市场数据
market = daily.analyze_market()

# 生成报告
report = daily.generate_report(news, market)

# 推送到GitHub
daily.push_to_github(report)
```

## 输出文件

- `reports/daily-YYYY-MM-DD.md` - 日报文件
- `data/news-YYYY-MM-DD.json` - 原始新闻数据
- `data/market-YYYY-MM-DD.json` - 市场数据

## 更新日志

### 2026-02-28
- ✅ 实现新闻自动采集
- ✅ 集成市场数据分析
- ✅ 支持GitHub自动推送
- ✅ 添加定时任务配置
