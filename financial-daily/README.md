# Financial Daily Generator

财经资讯日报生成器 - 深度采集财经热点，自动生成日报并推送到GitHub。

## 功能特性

- **新闻采集**: 自动抓取财经热点新闻
- **市场分析**: 获取主要股票指数行情
- **日报生成**: 生成Markdown格式的结构化日报
- **自动推送**: 推送到GitHub仓库保存

## 快速开始

```bash
# 生成今日日报
cd /root/.openclaw/workspace/ai-agent-lab/financial-daily
python3 generator.py

# 查看生成的报告
ls -la reports/
```

## 安装

```bash
# 确保依赖技能包已安装
# - research-pro: 新闻搜索和采集
# - finance-pro: 市场数据获取
```

## 使用方法

### 命令行执行

```bash
python3 generator.py
```

### Python API

```python
from generator import FinancialNewsDaily

# 创建日报生成器
daily = FinancialNewsDaily()

# 运行日报生成
daily.run()
```

## 日报内容结构

```markdown
# 财经资讯日报 - 2026-02-28

## 📊 市场概览
- 上证指数: 3000.00 (+0.5%)
- 深证成指: 10000.00 (+0.8%)

## 🔥 热点资讯
1. [新闻标题](链接) - 摘要...

## 📈 分析摘要
```

## 配置

### 环境变量

```bash
# GitHub配置
export GITHUB_TOKEN="your_token"
export GITHUB_REPO="claw-bft/ai-agent-lab"

# 输出目录
export OUTPUT_DIR="/root/.openclaw/workspace/financial-daily"
```

## 定时任务

```bash
# 添加到crontab，每日上午9点执行
0 9 * * * cd /path/to/financial-daily && python3 generator.py
```

## 测试

```bash
# 运行测试
python3 -m pytest tests/ -v
```

## 输出文件

- `reports/daily-YYYY-MM-DD.md` - 日报文件
- `data/news-YYYY-MM-DD.json` - 原始新闻数据
- `data/market-YYYY-MM-DD.json` - 市场数据

## 许可证

MIT
