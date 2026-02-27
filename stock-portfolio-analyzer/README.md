# Stock Portfolio Analyzer

多Agent协作持仓分析系统，自动化完成新闻收集、技术面分析、可视化报告生成和部署。

## 安装

```bash
chmod +x /root/.openclaw/workspace/skills/stock-portfolio-analyzer/stock-analyzer.py
ln -s /root/.openclaw/workspace/skills/stock-portfolio-analyzer/stock-analyzer.py /usr/local/bin/stock-analyzer
```

## 使用方法

### 分析持仓

```bash
# 从文件分析
stock-analyzer analyze --input stocks.txt

# 直接分析股票代码
stock-analyzer analyze --stocks "002383,002602"

# 分析并部署到Vercel
stock-analyzer analyze --input stocks.txt --deploy

# JSON格式输出
stock-analyzer analyze --stocks "002383" --json
```

### 查看历史报告

```bash
stock-analyzer list
```

## 输入格式

### 文本文件格式
```
股票名称 - 代码 - 现价
例如：
合众思壮 - 002383 - 11.34
世纪华通 - 002602 - 18.76
```

### JSON格式
```json
[
  {"name": "合众思壮", "symbol": "002383", "price": 11.34},
  {"name": "世纪华通", "symbol": "002602", "price": 18.76}
]
```

## 工作流程

```
用户输入
    ↓
[NewsAgent] 收集每只股票的最新资讯
    ↓
[StockAgent] 进行技术面分析（均线/MACD/KDJ/支撑压力）
    ↓
[ReportAgent] 生成可视化HTML报告
    ↓
[DeployAgent] 部署到Vercel (可选)
    ↓
返回报告链接
```

## 系统架构

```
stock-portfolio-analyzer/
├── stock-analyzer.py    # 主入口脚本
├── SKILL.md             # 技能文档
└── requirements.txt     # 依赖管理
```

## 依赖

- Python 3.8+
- Vercel CLI (用于部署)
- VERCEL_TOKEN 环境变量

## 配置

```bash
export VERCEL_TOKEN="your-token"
```

## 输出内容

1. **统计概览** - 持仓数量、平均评分
2. **个股分析卡片** - 每只股票的详细分析
3. **技术面评分图表** - MACD/KDJ/RSI/MA指标
4. **新闻影响分析** - 按影响分类展示
5. **操作建议汇总** - 支撑/压力/建议

## 已知问题与修复记录

### Issue #1: 子任务HTML生成中断
**状态**: 已修复  
**发现时间**: 2026-02-26  
**问题描述**: 子Agent在生成大型HTML文件时因输出token过多导致中断  
**修复方案**: HTML生成拆分为多个小文件，使用文件操作替代直接输出

## 任务配置

### 早报任务 (morning_task.json)
放置在 `~/.openclaw/shared/incoming/` 目录下：

```json
{
  "task_id": "morning-stock-report",
  "task_name": "股市早报",
  "stocks": [
    {"name": "合众思壮", "symbol": "002383", "price": 11.34}
  ]
}
```

---

**由 claw-bft/ai-agent-lab 自动生成**  
**生成时间**: 2026-02-26
