---
name: finance-pro
description: 金融投资专业技能包 - 趋势交易、价值投资、套利策略三轨并行
---

# Finance Pro 技能包

## 功能模块

### 1. 趋势交易 (Trend Trading)
- 多市场实时行情数据获取 (A股、港股、美股、加密货币)
- 7×24小时价格监控与条件预警
- 30+技术指标分析 (MACD, RSI, KDJ, BOLL等)
- LSTM神经网络趋势预测

### 2. 价值投资 (Value Investing)
- 财报深度解析，50+财务指标计算
- PE/PB/PS/DCF多模型估值
- 蒙特卡洛模拟与敏感性分析
- 安全边际评估

### 3. 套利策略 (Arbitrage)
- 跨市场价差监控
- 期现套利机会识别
- 统计套利模型

## 依赖工具
- tushare (A股数据)
- yfinance (美股数据)
- akshare (综合金融数据)
- pandas, numpy (数据分析)

## 使用示例

```bash
# 获取股票实时行情
finance-pro quote --symbol 000001.SZ

# 技术分析
finance-pro analyze --symbol 000001.SZ --indicators MACD,RSI,KDJ

# 财报分析
finance-pro financial --symbol 000001.SZ --quarter 2024Q3

# 设置价格预警
finance-pro alert --symbol 000001.SZ --condition "price>10.5" --channel feishu
```

## 数据获取模块 (data_fetcher.py)

为解决 akshare 网络不稳定问题，提供带重试和缓存的数据获取器。

### 特性
- **指数退避重试**: 最多5次重试，间隔 2^n 秒
- **本地缓存**: 15分钟TTL，减少网络请求
- **优雅降级**: 网络失败时自动使用过期缓存
- **超时控制**: 10秒请求超时

### 使用方法

```python
from data_fetcher import fetch_with_retry, AkshareFetcher
import akshare as ak

# 方式1: 通用数据获取
result = fetch_with_retry(ak.stock_zh_a_spot_em)
if result["success"]:
    df = result["data"]
    print(f"数据获取成功，重试次数: {result['retry_count']}")
    if result["from_cache"]:
        print("使用缓存数据")

# 方式2: 专用akshare获取器
fetcher = AkshareFetcher()
result = fetcher.fetch_stock_spot()
if result["success"]:
    df = result["data"]

# 清理缓存
from data_fetcher import clear_cache
clear_cache()

# 查看缓存统计
from data_fetcher import get_cache_stats
stats = get_cache_stats()
print(f"缓存文件数: {stats['file_count']}")
```

### 返回格式
```python
{
    "success": bool,        # 是否成功
    "data": Any,            # 数据内容 (DataFrame/dict等)
    "error": str,           # 错误信息 (失败时)
    "from_cache": bool,     # 是否来自缓存
    "expired": bool,        # 缓存是否已过期 (降级时使用)
    "retry_count": int      # 实际重试次数
}
```
