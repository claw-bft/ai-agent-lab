---
name: stock-portfolio-analyzer
description: 股票投资组合分析器 - 多数据源、智能缓存、重试机制的股票数据获取与分析
---

# Stock Portfolio Analyzer - 股票投资组合分析器

增强版股票数据获取模块，支持多数据源、智能缓存和自动重试机制，解决网络连接问题。

## 核心功能

### 1. 多数据源支持
- **AkShare**: A股数据（主要来源）
- **Yahoo Finance**: 美股/港股数据
- **本地缓存**: 离线数据支持
- **模拟数据**: 网络故障时的备用方案

### 2. 智能缓存机制
- 自动缓存最近数据
- 可配置的缓存过期时间
- 减少API调用频率

### 3. 重试与降级
- 自动重试失败请求
- 指数退避策略
- 数据源自动切换

## 安装依赖

```bash
pip install requests akshare yfinance pandas
```

## 使用示例

### 基本用法 - 获取股票数据

```python
from enhanced_data_fetcher import EnhancedDataFetcher

# 创建数据获取器
fetcher = EnhancedDataFetcher()

# 获取A股数据
result = fetcher.get_stock_data('000001.SZ')
if result.success:
    print(f"股票名称: {result.data['name']}")
    print(f"当前价格: {result.data['price']}")
    print(f"涨跌幅: {result.data['change_percent']}%")
else:
    print(f"获取失败: {result.error}")
```

### 批量获取多只股票

```python
from enhanced_data_fetcher import EnhancedDataFetcher

fetcher = EnhancedDataFetcher()

# 股票列表
symbols = ['000001.SZ', '600519.SH', '000858.SZ']

# 批量获取
results = fetcher.get_batch_stock_data(symbols)

for symbol, result in results.items():
    if result.success:
        print(f"{symbol}: {result.data['price']}元")
    else:
        print(f"{symbol}: 获取失败")
```

### 获取历史行情

```python
from enhanced_data_fetcher import EnhancedDataFetcher
from datetime import datetime, timedelta

fetcher = EnhancedDataFetcher()

# 获取最近30天历史数据
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

result = fetcher.get_historical_data(
    symbol='000001.SZ',
    start_date=start_date.strftime('%Y%m%d'),
    end_date=end_date.strftime('%Y%m%d')
)

if result.success:
    df = result.data
    print(f"数据条数: {len(df)}")
    print(f"最高价: {df['high'].max()}")
    print(f"最低价: {df['low'].min()}")
```

### 自定义缓存目录

```python
from enhanced_data_fetcher import EnhancedDataFetcher
from pathlib import Path

# 使用自定义缓存目录
cache_dir = Path('/path/to/cache')
fetcher = EnhancedDataFetcher(cache_dir=cache_dir)

# 获取数据（自动使用缓存）
result = fetcher.get_stock_data('000001.SZ')
```

### 投资组合分析

```python
from enhanced_data_fetcher import EnhancedDataFetcher

fetcher = EnhancedDataFetcher()

# 定义投资组合
portfolio = {
    '000001.SZ': {'shares': 1000, 'cost': 10.5},
    '600519.SH': {'shares': 100, 'cost': 1680.0},
    '000858.SZ': {'shares': 500, 'cost': 145.0},
}

# 分析组合
total_value = 0
total_cost = 0

for symbol, holding in portfolio.items():
    result = fetcher.get_stock_data(symbol)
    if result.success:
        current_price = result.data['price']
        value = current_price * holding['shares']
        cost = holding['cost'] * holding['shares']
        
        profit = value - cost
        profit_pct = (profit / cost) * 100
        
        print(f"{symbol}: 盈亏 {profit:+.2f}元 ({profit_pct:+.2f}%)")
        
        total_value += value
        total_cost += cost

print(f"\n组合总成本: {total_cost:.2f}元")
print(f"组合总市值: {total_value:.2f}元")
print(f"总盈亏: {total_value - total_cost:+.2f}元")
```

## API参考

### `EnhancedDataFetcher`

数据获取器类。

**初始化:**
```python
fetcher = EnhancedDataFetcher(cache_dir=None)
```

**方法:**

#### `get_stock_data(symbol: str) -> StockDataResult`
获取单只股票数据。

**参数:**
- `symbol` (str): 股票代码，如 '000001.SZ'

**返回:**
- `StockDataResult`: 包含 success, data, error, source, timestamp

#### `get_batch_stock_data(symbols: List[str]) -> Dict[str, StockDataResult]`
批量获取股票数据。

**参数:**
- `symbols` (list): 股票代码列表

**返回:**
- 字典，key为股票代码，value为StockDataResult

#### `get_historical_data(symbol: str, start_date: str, end_date: str) -> StockDataResult`
获取历史行情数据。

**参数:**
- `symbol` (str): 股票代码
- `start_date` (str): 开始日期，格式 'YYYYMMDD'
- `end_date` (str): 结束日期，格式 'YYYYMMDD'

**返回:**
- `StockDataResult`: data字段为DataFrame

### `StockDataResult`

数据结果类。

**属性:**
- `success` (bool): 是否成功
- `data` (dict): 数据内容
- `error` (str): 错误信息（失败时）
- `source` (str): 数据来源
- `timestamp` (str): 时间戳

## 数据源优先级

1. **缓存数据** - 如果未过期，直接返回
2. **AkShare** - A股主要数据源
3. **Yahoo Finance** - 美股/港股
4. **模拟数据** - 网络故障时的备用

## 错误处理

```python
from enhanced_data_fetcher import EnhancedDataFetcher

fetcher = EnhancedDataFetcher()
result = fetcher.get_stock_data('INVALID')

if not result.success:
    # 处理错误
    print(f"错误: {result.error}")
    print(f"数据来源: {result.source}")
```

## 文件结构

```
skills/stock-portfolio-analyzer/
├── enhanced_data_fetcher.py   # 核心数据获取模块
└── SKILL.md                   # 本文件
```

## 更新日志

### 2026-02-28
- ✅ 创建 SKILL.md 使用文档
- ✅ 添加完整使用示例
- ✅ 补充 API 参考文档
