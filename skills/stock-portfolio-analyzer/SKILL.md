# Stock Portfolio Analyzer

多Agent协作持仓分析系统，自动化完成新闻收集、技术面分析、可视化报告生成和部署。

## 工作流程

```
用户上传持仓截图/提供持仓列表
    ↓
[新闻Agent] 收集每只股票的最新资讯
    ↓
[股票Agent] 进行技术面分析（均线/MACD/KDJ/支撑压力）
    ↓
[Coding Agent] 生成可视化HTML报告
    ↓
[Vercel部署] 上线可访问的报告页面
    ↓
返回报告链接
```

## 输入格式

### 方式1：截图上传
支持股票APP截图自动识别

### 方式2：文字列表
```
股票名称 - 代码 - 现价
例如：
合众思壮 - 002383 - 11.34
世纪华通 - 002602 - 18.76
...
```

### 方式3：任务配置文件
放置在 `~/.openclaw/shared/incoming/` 目录下的JSON文件：
- `morning_task.json` - 早报任务配置
- `stock_task.json` - 个股分析任务配置
- `team_task_*.json` - 协同任务配置

## 输出内容

1. **统计概览** - 持仓数量、平均评分、正面/负面新闻统计
2. **个股分析卡片** - 每只股票的详细分析
3. **技术面评分图表** - 可视化对比
4. **新闻影响时间线** - 按影响分类展示
5. **操作建议汇总表** - 支撑/压力/建议
6. **整体建议** - 数字巴菲特综合判断

## 使用示例

```bash
# 分析持仓
stock-analyzer analyze --input screenshot.jpg

# 分析文字列表
stock-analyzer analyze --stocks "002383,002602,002919"

# 查看历史报告
stock-analyzer list
```

## 依赖

- VERCEL_TOKEN - Vercel部署令牌
- 新闻搜索工具 (tavily/kimi_search)
- 股票数据接口 - 通过 finance-pro/data_fetcher 获取

## 数据源

本系统使用 **finance-pro/data_fetcher** 模块获取股票数据，具备以下特性：

- **连接重试机制**：指数退避策略，最多5次重试
- **本地JSON缓存层**：缓存时间15分钟
- **请求超时设置**：10秒超时
- **优雅降级**：网络失败时返回缓存数据或模拟数据

### 数据源配置

系统会自动检测并使用 finance-pro/data_fetcher，无需额外配置。

```python
# 在代码中使用
def analyze_stock(symbol: str, name: str) -> Dict:
    fetcher = self._get_fetcher()
    
    # 获取实时行情（自动重试+缓存）
    result = fetcher.get_stock_quote(symbol)
    if result.success:
        data = result.data
        print(f"价格: {data['price']}, 来自缓存: {result.from_cache}")
```

## 配置

```bash
export VERCEL_TOKEN="your-token"
```

## 技术栈

- 新闻Agent: kimi_search/news API
- 股票Agent: 技术分析算法
- Coding Agent: HTML/Chart.js
- 部署: Vercel CLI

---

## 已知问题与修复记录

### Issue #1: 子任务HTML生成中断
**状态**: 已修复  
**发现时间**: 2026-02-26  
**问题描述**: 子Agent在生成大型HTML文件时因输出token过多导致中断（`stopReason: error`）  
**根因**: HTML内容过长，单条消息输出超限  

**修复方案**:
1. HTML生成拆分为多个小文件（header/body/footer）
2. 使用 `write` 工具直接写入文件，而非输出到对话
3. 增加错误重试机制，主会话检测到子任务失败时自动接管
4. 简化HTML模板，减少冗余样式

**预防措施**:
- 所有大型内容生成必须通过文件操作，禁止直接输出
- 子任务超时时间设置为300秒以上
- 主会话监控子任务状态，失败时立即介入

### Issue #2: 早报任务子任务中断
**状态**: 已修复  
**发现时间**: 2026-02-27  
**问题描述**: stock-portfolio-analyzer早报子任务在cron执行时经常中断，导致定时任务无法稳定运行  
**根因**: 
1. `stock-analyzer.py` 缺少处理 `morning_task.json` 的逻辑
2. 没有专门的早报任务执行入口
3. 缺少错误处理和重试机制

**修复方案**:
1. 在 `stock-analyzer.py` 中添加 `morning-report` 命令
2. 实现 `run_morning_report_task()` 函数，专门处理早报任务配置
3. 创建 `generate_morning_report_html()` 生成早报专用HTML模板
4. 新增 `scripts/run_morning_report.sh` 脚本，带5次重试机制
5. 任务执行后自动更新 `morning_task.json` 的状态字段

**使用方法**:
```bash
# 直接执行早报任务
python3 stock-analyzer.py morning-report

# 或通过脚本执行（带重试）
bash scripts/run_morning_report.sh

# 指定自定义任务文件
python3 stock-analyzer.py morning-report --task-file /path/to/task.json
```

**任务状态追踪**:
执行后 `morning_task.json` 会自动更新以下字段:
- `last_run`: 上次执行时间
- `last_report_url`: 上次报告链接
- `last_status`: 执行状态 (success/deploy_failed)

---

## 任务配置模板

### 早报任务 (morning_task.json)
```json
{
  "task_id": "morning-stock-report",
  "task_name": "股市早报",
  "task_type": "daily_report",
  "workflow": "sequential",
  "steps": [
    {"agent": "news-aggregator", "action": "collect_news"},
    {"agent": "stock-analyzer", "action": "pre_market_scan"},
    {"agent": "code-generator", "action": "generate_report"},
    {"agent": "deploy-agent", "action": "deploy_to_vercel"}
  ]
}
```

### 个股分析任务 (stock_task.json)
```json
{
  "task_id": "technical_analysis",
  "task_type": "technical_analysis",
  "symbols": ["000001.SZ", "000002.SZ"],
  "indicators": ["MACD", "KDJ", "RSI"],
  "period": "1d"
}
```
