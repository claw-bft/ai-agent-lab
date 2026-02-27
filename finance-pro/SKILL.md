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
