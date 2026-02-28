#!/usr/bin/env python3
"""
Finance Pro 核心实现
金融投资专业技能包 - 趋势交易、价值投资、套利策略
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# 尝试导入金融数据库
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

def get_stock_quote_a_share(symbol: str) -> Dict[str, Any]:
    """获取A股实时行情"""
    if not AKSHARE_AVAILABLE:
        return {
            "success": False,
            "error": "akshare未安装，请运行: pip install akshare"
        }

    try:
        # 处理symbol格式 (000001.SZ -> 000001)
        code = symbol.split('.')[0] if '.' in symbol else symbol

        # 获取实时行情
        df = ak.stock_zh_a_spot_em()
        stock_info = df[df['代码'] == code]

        if stock_info.empty:
            return {
                "success": False,
                "error": f"未找到股票: {symbol}"
            }

        row = stock_info.iloc[0]
        return {
            "success": True,
            "symbol": symbol,
            "name": row.get('名称', 'N/A'),
            "price": float(row.get('最新价', 0)),
            "change": float(row.get('涨跌幅', 0)),
            "change_amount": float(row.get('涨跌额', 0)),
            "volume": int(row.get('成交量', 0)),
            "amount": float(row.get('成交额', 0)),
            "high": float(row.get('最高', 0)),
            "low": float(row.get('最低', 0)),
            "open": float(row.get('今开', 0)),
            "prev_close": float(row.get('昨收', 0)),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"获取行情失败: {str(e)}"
        }

def get_stock_history(symbol: str, period: str = "1mo") -> Dict[str, Any]:
    """获取股票历史数据"""
    if not AKSHARE_AVAILABLE:
        return {
            "success": False,
            "error": "akshare未安装"
        }

    try:
        code = symbol.split('.')[0] if '.' in symbol else symbol

        # 获取历史数据
        df = ak.stock_zh_a_hist(symbol=code, period="daily",
                                start_date=(datetime.now() - timedelta(days=90)).strftime("%Y%m%d"),
                                end_date=datetime.now().strftime("%Y%m%d"),
                                adjust="qfq")

        if df.empty:
            return {
                "success": False,
                "error": f"未找到历史数据: {symbol}"
            }

        # 转换为列表
        records = df.tail(30).to_dict('records')

        return {
            "success": True,
            "symbol": symbol,
            "period": period,
            "data_points": len(records),
            "data": [
                {
                    "date": r.get('日期'),
                    "open": float(r.get('开盘', 0)),
                    "close": float(r.get('收盘', 0)),
                    "high": float(r.get('最高', 0)),
                    "low": float(r.get('最低', 0)),
                    "volume": int(r.get('成交量', 0))
                }
                for r in records
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"获取历史数据失败: {str(e)}"
        }

def calculate_ma(data: List[Dict], periods: List[int] = [5, 10, 20, 60]) -> Dict[str, Any]:
    """计算移动平均线"""
    if not data or not PANDAS_AVAILABLE:
        return {"success": False, "error": "数据不足或未安装pandas"}

    try:
        df = pd.DataFrame(data)
        df['close'] = pd.to_numeric(df['close'])

        ma_results = {}
        for period in periods:
            if len(df) >= period:
                ma = df['close'].tail(period).mean()
                ma_results[f"MA{period}"] = round(ma, 2)

        return {
            "success": True,
            "ma": ma_results
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def calculate_rsi(data: List[Dict], period: int = 14) -> Dict[str, Any]:
    """计算RSI指标"""
    if not data or not PANDAS_AVAILABLE:
        return {"success": False, "error": "数据不足或未安装pandas"}

    try:
        df = pd.DataFrame(data)
        df['close'] = pd.to_numeric(df['close'])

        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        current_rsi = rsi.iloc[-1]

        signal = "中性"
        if current_rsi > 70:
            signal = "超买"
        elif current_rsi < 30:
            signal = "超卖"

        return {
            "success": True,
            "rsi": round(current_rsi, 2),
            "signal": signal,
            "period": period
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def technical_analysis(symbol: str, indicators: List[str]) -> Dict[str, Any]:
    """技术分析"""
    # 获取历史数据
    history = get_stock_history(symbol)
    if not history.get("success"):
        return history

    data = history.get("data", [])

    results = {
        "success": True,
        "symbol": symbol,
        "indicators": {}
    }

    for indicator in indicators:
        indicator = indicator.upper()
        if indicator == "MA":
            results["indicators"]["MA"] = calculate_ma(data)
        elif indicator == "RSI":
            results["indicators"]["RSI"] = calculate_rsi(data)
        else:
            results["indicators"][indicator] = {
                "success": False,
                "error": f"暂未实现指标: {indicator}"
            }

    return results

def get_financial_report(symbol: str, quarter: str = "latest") -> Dict[str, Any]:
    """获取财务报表数据"""
    if not AKSHARE_AVAILABLE:
        return {
            "success": False,
            "error": "akshare未安装"
        }

    try:
        code = symbol.split('.')[0] if '.' in symbol else symbol

        # 获取主要财务指标
        df = ak.stock_financial_report_sina(stock=code, symbol="利润表")

        if df.empty:
            return {
                "success": False,
                "error": f"未找到财务数据: {symbol}"
            }

        # 获取最新一期
        latest = df.iloc[0]

        return {
            "success": True,
            "symbol": symbol,
            "quarter": quarter,
            "revenue": latest.get('营业收入', 'N/A'),
            "net_profit": latest.get('净利润', 'N/A'),
            "gross_margin": latest.get('毛利率', 'N/A'),
            "data": df.head(4).to_dict('records')
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"获取财报失败: {str(e)}"
        }

def main():
    parser = argparse.ArgumentParser(description="Finance Pro - 金融投资专业技能包")
    parser.add_argument("command", choices=["quote", "analyze", "financial", "history"])
    parser.add_argument("--symbol", required=True, help="股票代码 (如: 000001.SZ)")
    parser.add_argument("--indicators", default="MA,RSI", help="技术指标 (逗号分隔)")
    parser.add_argument("--quarter", default="latest", help="财报季度")
    parser.add_argument("--json", action="store_true", help="JSON格式输出")

    args = parser.parse_args()

    if args.command == "quote":
        result = get_stock_quote_a_share(args.symbol)
    elif args.command == "history":
        result = get_stock_history(args.symbol)
    elif args.command == "analyze":
        indicators = [i.strip() for i in args.indicators.split(",")]
        result = technical_analysis(args.symbol, indicators)
    elif args.command == "financial":
        result = get_financial_report(args.symbol, args.quarter)
    else:
        result = {"success": False, "error": "未知命令"}

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result.get("success"):
            print(f"✓ {result.get('symbol', '')} 查询成功")
            if "price" in result:
                print(f"  价格: {result['price']}")
                print(f"  涨跌: {result.get('change', 0):.2f}%")
            if "indicators" in result:
                for name, data in result["indicators"].items():
                    if data.get("success"):
                        print(f"  {name}: {json.dumps(data, ensure_ascii=False)}")
        else:
            print(f"✗ 错误: {result.get('error', '未知错误')}")
            sys.exit(1)

if __name__ == "__main__":
    main()
