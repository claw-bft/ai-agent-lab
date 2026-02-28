# Finance Pro

金融投资专业技能包 - 趋势交易、价值投资、套利策略三轨并行

## 功能特性

- **趋势交易**: 多市场实时行情数据获取，技术指标分析，趋势预测
- **价值投资**: 财报深度解析，多模型估值，安全边际评估
- **套利策略**: 跨市场价差监控，期现套利机会识别

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

```python
from finance_pro import FinancePro

# 初始化
fp = FinancePro()

# 获取股票行情
quote = fp.get_quote("000001.SZ")
print(quote)

# 技术分析
analysis = fp.technical_analysis("000001.SZ", indicators=["MACD", "RSI"])
print(analysis)
```

## 依赖

- akshare
- yfinance
- pandas
- numpy
- requests

## 项目结构

```
finance-pro/
├── finance_pro.py      # 核心实现
├── data_adapter.py     # 数据适配器
├── requirements.txt    # 依赖配置
├── tests/             # 测试目录
│   └── test_finance.py
└── SKILL.md           # 技能文档
```

## 测试

```bash
pytest tests/ -v
```

## License

MIT
