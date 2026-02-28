# Stock Portfolio Analyzer

多Agent协作持仓分析系统，自动化完成新闻收集、技术面分析、可视化报告生成和部署。

## 功能特性

- **自动化分析流程**: 一键完成从数据收集到报告生成的全流程
- **多Agent协作**: 新闻Agent、分析Agent、报告Agent、部署Agent协同工作
- **技术面分析**: 支持均线、MACD、KDJ、RSI等多种技术指标
- **新闻情绪分析**: 自动收集并分析相关新闻的影响
- **可视化报告**: 生成美观的HTML报告，包含图表和评分
- **一键部署**: 支持自动部署到Vercel，便于分享和查看

## 安装

### 系统要求

- Python 3.8+
- Vercel CLI (用于部署功能)

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/claw-bft/ai-agent-lab.git
cd ai-agent-lab/stock-portfolio-analyzer

# 安装依赖
pip install -r requirements.txt

# 设置可执行权限并创建软链接
chmod +x stock-analyzer.py
ln -s $(pwd)/stock-analyzer.py /usr/local/bin/stock-analyzer
```

### 环境配置

```bash
# 配置Vercel Token（用于部署功能）
export VERCEL_TOKEN="your-vercel-token"

# 添加到 ~/.bashrc 或 ~/.zshrc 使其永久生效
echo 'export VERCEL_TOKEN="your-vercel-token"' >> ~/.bashrc
```

## 使用方法

### 命令行界面

#### 分析持仓

```bash
# 从文件分析
stock-analyzer analyze --input stocks.txt

# 直接分析股票代码
stock-analyzer analyze --stocks "002383,002602"

# 分析并部署到Vercel
stock-analyzer analyze --input stocks.txt --deploy

# JSON格式输出
stock-analyzer analyze --stocks "002383" --json

# 指定输出目录
stock-analyzer analyze --input stocks.txt --output ./reports/
```

#### 查看历史报告

```bash
# 列出所有历史报告
stock-analyzer list

# 查看特定报告
stock-analyzer show --id report-20240301

# 删除历史报告
stock-analyzer delete --id report-20240301
```

### 输入格式

#### 文本文件格式

创建 `stocks.txt` 文件：

```
# 股票持仓列表
# 格式: 股票名称 - 代码 - 现价

合众思壮 - 002383 - 11.34
世纪华通 - 002602 - 18.76
贵州茅台 - 600519 - 1680.00
腾讯控股 - 00700 - 380.50
```

#### JSON格式

```json
[
  {
    "name": "合众思壮",
    "symbol": "002383",
    "price": 11.34,
    "shares": 1000,
    "notes": "卫星导航概念股"
  },
  {
    "name": "世纪华通",
    "symbol": "002602",
    "price": 18.76,
    "shares": 500
  }
]
```

#### CSV格式

```csv
name,symbol,price,shares
合众思壮,002383,11.34,1000
世纪华通,002602,18.76,500
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

### Agent详解

#### NewsAgent - 新闻收集Agent

- **职责**: 收集每只股票的相关新闻和公告
- **数据源**: 财经新闻网站、公司公告
- **输出**: 结构化的新闻列表，包含标题、来源、时间、影响评估

#### StockAgent - 股票分析Agent

- **职责**: 进行技术面分析
- **分析指标**:
  - 均线系统（MA5/MA10/MA20/MA60）
  - MACD指标
  - KDJ指标
  - RSI指标
  - 布林带
  - 支撑/压力位
- **输出**: 技术指标评分和交易建议

#### ReportAgent - 报告生成Agent

- **职责**: 生成可视化HTML报告
- **功能**:
  - 统计概览卡片
  - 个股分析详情
  - 技术面评分图表
  - 新闻影响分析
  - 操作建议汇总
- **输出**: 美观的HTML报告文件

#### DeployAgent - 部署Agent

- **职责**: 将报告部署到Vercel
- **功能**:
  - 自动创建Vercel项目
  - 上传静态文件
  - 生成访问链接
- **输出**: 可分享的URL链接

## 系统架构

```
stock-portfolio-analyzer/
├── stock-analyzer.py         # 主入口脚本
├── agents/
│   ├── __init__.py
│   ├── news_agent.py         # 新闻收集Agent
│   ├── stock_agent.py        # 股票分析Agent
│   ├── report_agent.py       # 报告生成Agent
│   └── deploy_agent.py       # 部署Agent
├── utils/
│   ├── __init__.py
│   ├── data_fetcher.py       # 数据获取工具
│   ├── technical_analysis.py # 技术分析工具
│   └── html_generator.py     # HTML生成工具
├── templates/
│   └── report_template.html  # 报告模板
├── tests/
│   ├── test_stock_analyzer.py
│   └── test_performance.py
├── README.md                 # 使用文档
├── SKILL.md                  # 技能文档
└── requirements.txt          # 依赖管理
```

## 依赖说明

### Python依赖

```
requests>=2.28.0
pandas>=1.5.0
numpy>=1.23.0
jinja2>=3.1.0
matplotlib>=3.6.0
```

### 外部工具

- **Vercel CLI**: 用于部署功能
  ```bash
  npm install -g vercel
  ```

## 配置详解

### 配置文件

创建 `~/.stock-analyzer/config.json`：

```json
{
  "default_output_dir": "./reports",
  "vercel_project_prefix": "stock-report",
  "news_sources": ["sina", "eastmoney", "10jqka"],
  "analysis_settings": {
    "ma_periods": [5, 10, 20, 60],
    "rsi_period": 14,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9
  },
  "report_settings": {
    "theme": "default",
    "include_charts": true,
    "max_news_per_stock": 5
  }
}
```

### 任务配置

#### 早报任务 (morning_task.json)

放置在 `~/.openclaw/shared/incoming/` 目录下：

```json
{
  "task_id": "morning-stock-report",
  "task_name": "股市早报",
  "schedule": "0 8 * * 1-5",
  "stocks": [
    {"name": "合众思壮", "symbol": "002383", "price": 11.34},
    {"name": "世纪华通", "symbol": "002602", "price": 18.76}
  ],
  "options": {
    "deploy": true,
    "notify": true
  }
}
```

## 输出内容详解

### 1. 统计概览

- 持仓股票数量
- 平均技术面评分
- 新闻情绪分布
- 建议操作统计

### 2. 个股分析卡片

每只股票的详细分析包含：

- **基本信息**: 名称、代码、当前价格
- **技术评分**: 综合评分（0-100）
- **指标详情**: MACD/KDJ/RSI/MA状态
- **支撑压力**: 关键价位
- **操作建议**: 买入/持有/卖出建议

### 3. 技术面评分图表

- 雷达图展示多维度评分
- 趋势图展示价格走势
- 柱状图对比各指标

### 4. 新闻影响分析

- 正面新闻列表
- 负面新闻列表
- 中性新闻列表
- 新闻情绪评分

### 5. 操作建议汇总

- 买入建议股票列表
- 持有建议股票列表
- 卖出建议股票列表
- 关键价位提醒

## API使用

### Python API

```python
from stock_analyzer import PortfolioAnalyzer

# 初始化分析器
analyzer = PortfolioAnalyzer()

# 加载持仓
portfolio = analyzer.load_portfolio("stocks.txt")

# 执行分析
results = analyzer.analyze(portfolio)

# 生成报告
report_path = analyzer.generate_report(results, output_dir="./reports")

# 部署报告
url = analyzer.deploy(report_path)
print(f"报告已部署: {url}")
```

### 异步分析

```python
import asyncio
from stock_analyzer import AsyncPortfolioAnalyzer

async def main():
    analyzer = AsyncPortfolioAnalyzer()
    portfolio = await analyzer.load_portfolio_async("stocks.txt")
    results = await analyzer.analyze_async(portfolio)
    return results

results = asyncio.run(main())
```

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行单元测试
pytest tests/test_stock_analyzer.py -v

# 运行性能测试
pytest tests/test_performance.py -v

# 生成覆盖率报告
pytest tests/ --cov=stock_analyzer --cov-report=html
```

## 性能优化

- **并发分析**: 多只股票并行分析
- **缓存机制**: 新闻数据和分析结果缓存
- **增量更新**: 只分析有变化的数据
- **懒加载**: 按需加载历史数据

## 故障排除

### 常见问题

#### 1. Vercel部署失败

**问题**: 部署时提示认证错误  
**解决**: 检查 `VERCEL_TOKEN` 环境变量是否正确设置

```bash
vercel login
export VERCEL_TOKEN=$(cat ~/.vercel/auth.json | grep token | head -1)
```

#### 2. 数据获取失败

**问题**: 股票数据获取超时  
**解决**: 检查网络连接，或配置代理

```python
# 在配置中设置代理
{
  "proxy": {
    "http": "http://proxy.example.com:8080",
    "https": "https://proxy.example.com:8080"
  }
}
```

#### 3. 报告生成缓慢

**问题**: 大量股票时报告生成慢  
**解决**: 
- 减少同时分析的股票数量
- 使用 `--json` 格式输出（更快）
- 关闭图表生成（配置中设置 `include_charts: false`）

## 已知问题与修复记录

### Issue #1: 子任务HTML生成中断

**状态**: 已修复 ✅  
**发现时间**: 2026-02-26  
**问题描述**: 子Agent在生成大型HTML文件时因输出token过多导致中断  
**修复方案**: HTML生成拆分为多个小文件，使用文件操作替代直接输出

### Issue #2: 新闻数据解析错误

**状态**: 已修复 ✅  
**发现时间**: 2026-02-25  
**问题描述**: 某些新闻网站HTML结构变化导致解析失败  
**修复方案**: 添加多种解析策略，自动回退到备用方案

## 贡献指南

欢迎提交Issue和PR来改进分析系统功能。

### 开发流程

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 代码风格
- 添加适当的类型注解
- 编写单元测试
- 更新相关文档

## 更新日志

### v1.1.0 (2026-02-26)
- 修复HTML生成中断问题
- 优化多Agent协作流程
- 添加更多技术指标支持

### v1.0.0 (2026-02-20)
- 初始版本发布
- 支持基础技术面分析
- 支持Vercel部署

## License

MIT License

---

**由 claw-bft/ai-agent-lab 自动生成**  
**文档更新时间**: 2026-03-01
