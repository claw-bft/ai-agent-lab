---
name: financial-daily
description: 财经资讯日报生成器 - 自动采集财经新闻和市场数据，生成结构化日报
---

# Financial Daily - 财经资讯日报生成器

自动采集财经新闻和市场数据，生成结构化日报并支持多渠道推送。

## 核心功能

### 1. 新闻自动采集
- 多源财经新闻抓取
- 智能热点识别
- 去重和筛选
- 实时更新

### 2. 市场数据分析
- 主要股票指数行情
- 板块涨跌分析
- 资金流向统计
- 技术指标计算

### 3. 智能日报生成
- Markdown格式输出
- 结构化内容组织
- 图表自动生成
- 多语言支持

### 4. 多渠道推送
- GitHub自动推送
- 邮件发送
- Webhook通知
- 消息平台集成

## 快速开始

### 环境配置

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export GITHUB_TOKEN="your_github_token"
export GITHUB_REPO="username/repo"
export OUTPUT_DIR="/path/to/output"
```

### 生成日报

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

### 命令行使用

```bash
# 生成今日日报
python generator.py

# 指定日期
python generator.py --date 2026-02-28

# 仅生成不推送
python generator.py --no-push

# 查看生成的报告
cat reports/daily-2026-02-28.md
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
- 科技: 涨幅榜...
- 金融: 资金流向...

## 💡 投资机会
- 关注板块: ...
- 风险提示: ...

## 📅 重要日历
- 明日关注: ...
```

## 定时任务配置

### Cron配置

```bash
# 编辑crontab
crontab -e

# 每日上午9点生成日报
0 9 * * * cd /path/to/financial-daily && python generator.py

# 每日下午收盘后更新
0 15 * * 1-5 cd /path/to/financial-daily && python generator.py --update
```

### 使用OpenClaw Cron

```json
{
  "name": "financial-daily",
  "schedule": "0 9 * * *",
  "command": "python /path/to/financial-daily/generator.py",
  "timezone": "Asia/Shanghai",
  "enabled": true
}
```

## 数据源配置

### 新闻源

```python
# 配置新闻源
NEWS_SOURCES = [
    {"name": "新浪财经", "url": "https://finance.sina.com.cn"},
    {"name": "东方财富", "url": "https://finance.eastmoney.com"},
    {"name": "财联社", "url": "https://www.cls.cn"}
]
```

### 市场数据

```python
# 配置关注的指数
INDICES = [
    {"code": "000001.SH", "name": "上证指数"},
    {"code": "399001.SZ", "name": "深证成指"},
    {"code": "399006.SZ", "name": "创业板指"},
    {"code": "HSI", "name": "恒生指数"}
]
```

## 自定义模板

### 创建自定义模板

```python
from generator import FinancialNewsDaily

class CustomDaily(FinancialNewsDaily):
    def generate_report(self, news, market):
        # 自定义报告格式
        report = f"""# 我的定制日报

## 市场摘要
{self._format_market(market)}

## 精选新闻
{self._format_news(news[:3])}

## 我的关注
- 股票A: ...
- 股票B: ...
"""
        return report
```

## API集成

### 获取实时数据

```python
import requests

# 获取最新行情
response = requests.get(
    "https://api.example.com/market/quote",
    params={"symbols": "000001.SH,399001.SZ"}
)
data = response.json()
```

### Webhook推送

```python
# 配置Webhook
WEBHOOK_URL = "https://hooks.slack.com/services/xxx"

# 发送通知
import requests
requests.post(WEBHOOK_URL, json={
    "text": "今日财经日报已生成",
    "attachments": [{
        "title": "查看报告",
        "title_link": "https://github.com/xxx/reports/daily-2026-02-28.md"
    }]
})
```

## 输出格式

### Markdown

默认输出格式，适合GitHub、GitLab等平台。

### PDF

```bash
# 安装依赖
pip install markdown weasyprint

# 生成PDF
python generator.py --format pdf
```

### HTML

```bash
# 生成HTML
python generator.py --format html

# 启动本地服务器查看
python -m http.server 8000
```

## 测试

```bash
# 运行单元测试
python -m pytest tests/ -v

# 测试新闻采集
python -m pytest tests/test_generator.py::TestNewsCollection -v

# 测试市场数据
python -m pytest tests/test_generator.py::TestMarketData -v
```

## 性能优化

### 缓存配置

```python
# 启用缓存
CACHE_ENABLED = True
CACHE_TTL = 300  # 5分钟

# 缓存目录
CACHE_DIR = "/tmp/financial-daily-cache"
```

### 并发采集

```python
from concurrent.futures import ThreadPoolExecutor

# 并发获取多个数据源
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(fetch_source, url) for url in sources]
    results = [f.result() for f in futures]
```

## 故障排查

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 新闻采集失败 | 网络问题 | 检查网络连接，配置代理 |
| 市场数据为空 | API限制 | 检查API密钥，降低请求频率 |
| GitHub推送失败 | Token过期 | 更新GITHUB_TOKEN |
| 生成速度慢 | 数据量大 | 启用缓存，减少数据源 |

### 日志查看

```bash
# 查看详细日志
python generator.py --verbose

# 保存日志到文件
python generator.py --log-file daily.log
```

## 更新日志

### v1.0.0
- ✅ 多源新闻自动采集
- ✅ 市场数据分析
- ✅ Markdown日报生成
- ✅ GitHub自动推送
- ✅ 定时任务支持
- ✅ 自定义模板
- ✅ 多渠道推送

## 相关链接

- [research-pro](../research-pro/) - 新闻搜索和采集
- [finance-pro](../finance-pro/) - 市场数据获取
- [示例报告](./reports/)
