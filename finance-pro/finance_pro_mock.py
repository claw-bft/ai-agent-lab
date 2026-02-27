#!/usr/bin/env python3
"""
Finance Pro Mock - 模拟数据模式
用于测试和演示
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

def get_stock_quote_a_share(symbol: str) -> Dict[str, Any]:
    """获取A股实时行情 (模拟数据)"""
    # 模拟股票数据
    mock_data = {
        "600519.SH": {"name": "贵州茅台", "price": 1688.88, "change": 1.25},
        "00700.HK": {"name": "腾讯控股", "price": 388.20, "change": -0.85},
        "09988.HK": {"name": "阿里巴巴", "price": 78.50, "change": 2.15},
        "002594.SZ": {"name": "比亚迪", "price": 245.60, "change": 3.42},
        "300750.SZ": {"name": "宁德时代", "price": 198.50, "change": -1.20},
        "600036.SH": {"name": "招商银行", "price": 32.85, "change": 0.65},
        "000001.SZ": {"name": "平安银行", "price": 10.25, "change": -0.35},
    }
    
    # 提取代码部分
    code = symbol.split('.')[0] if '.' in symbol else symbol
    full_symbol = symbol if '.' in symbol else f"{code}.SZ"
    
    # 查找或生成模拟数据
    if full_symbol in mock_data:
        data = mock_data[full_symbol]
    else:
        # 生成随机模拟数据
        import random
        base_price = random.uniform(10, 500)
        data = {
            "name": f"股票{code}",
            "price": round(base_price, 2),
            "change": round(random.uniform(-5, 5), 2)
        }
    
    return {
        "success": True,
        "symbol": symbol,
        "name": data["name"],
        "price": data["price"],
        "change": data["change"],
        "change_amount": round(data["price"] * data["change"] / 100, 2),
        "volume": 12345678,
        "amount": 2345678901.23,
        "high": round(data["price"] * 1.02, 2),
        "low": round(data["price"] * 0.98, 2),
        "open": round(data["price"] * 0.995, 2),
        "prev_close": round(data["price"] / (1 + data["change"]/100), 2),
        "timestamp": datetime.now().isoformat(),
        "data_source": "mock"
    }

def get_stock_history(symbol: str, period: str = "1mo") -> Dict[str, Any]:
    """获取股票历史数据 (模拟)"""
    import random
    
    code = symbol.split('.')[0] if '.' in symbol else symbol
    
    # 生成30天的模拟数据
    data = []
    base_price = random.uniform(50, 500)
    
    for i in range(30):
        date = datetime.now() - timedelta(days=30-i)
        change = random.uniform(-0.03, 0.03)
        close = base_price * (1 + change)
        high = close * (1 + random.uniform(0, 0.02))
        low = close * (1 - random.uniform(0, 0.02))
        open_price = close * (1 + random.uniform(-0.01, 0.01))
        
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "open": round(open_price, 2),
            "close": round(close, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "volume": random.randint(1000000, 10000000)
        })
        
        base_price = close
    
    return {
        "success": True,
        "symbol": symbol,
        "period": period,
        "data_points": len(data),
        "data": data,
        "data_source": "mock"
    }

def calculate_ma(data: List[Dict], periods: List[int] = [5, 10, 20, 60]) -> Dict[str, Any]:
    """计算移动平均线"""
    if not data:
        return {"success": False, "error": "数据不足"}
    
    closes = [d["close"] for d in data]
    ma_results = {}
    
    for period in periods:
        if len(closes) >= period:
            ma = sum(closes[-period:]) / period
            ma_results[f"MA{period}"] = round(ma, 2)
    
    return {
        "success": True,
        "ma": ma_results
    }

def calculate_rsi(data: List[Dict], period: int = 14) -> Dict[str, Any]:
    """计算RSI指标"""
    if not data or len(data) < period + 1:
        return {"success": False, "error": "数据不足"}
    
    closes = [d["close"] for d in data]
    
    gains = []
    losses = []
    
    for i in range(1, len(closes)):
        change = closes[i] - closes[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
    
    signal = "中性"
    if rsi > 70:
        signal = "超买"
    elif rsi < 30:
        signal = "超卖"
    
    return {
        "success": True,
        "rsi": round(rsi, 2),
        "signal": signal,
        "period": period
    }

def technical_analysis(symbol: str, indicators: List[str]) -> Dict[str, Any]:
    """技术分析"""
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
    """获取财务报表数据 (模拟)"""
    code = symbol.split('.')[0] if '.' in symbol else symbol
    
    # 模拟财务数据
    mock_financial = {
        "600519": {"name": "贵州茅台", "revenue": "1207.76亿", "net_profit": "747.34亿", "gross_margin": "91.96%"},
        "00700": {"name": "腾讯控股", "revenue": "6090.15亿", "net_profit": "1152.16亿", "gross_margin": "46.12%"},
        "09988": {"name": "阿里巴巴", "revenue": "9411.68亿", "net_profit": "797.41亿", "gross_margin": "37.72%"},
    }
    
    if code in mock_financial:
        data = mock_financial[code]
    else:
        import random
        data = {
            "name": f"股票{code}",
            "revenue": f"{random.uniform(10, 1000):.2f}亿",
            "net_profit": f"{random.uniform(1, 100):.2f}亿",
            "gross_margin": f"{random.uniform(10, 50):.2f}%"
        }
    
    return {
        "success": True,
        "symbol": symbol,
        "quarter": quarter,
        "name": data["name"],
        "revenue": data["revenue"],
        "net_profit": data["net_profit"],
        "gross_margin": data["gross_margin"],
        "data_source": "mock"
    }

# 保持与原模块相同的接口
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Finance Pro Mock")
    parser.add_argument("command", choices=["quote", "analyze", "financial", "history"])
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--indicators", default="MA,RSI")
    parser.add_argument("--quarter", default="latest")
    parser.add_argument("--json", action="store_true")
    
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
        print(result)
