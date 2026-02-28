#!/usr/bin/env python3
"""
Finance Pro - 技术指标计算模块
支持常见技术分析指标计算
"""

import json
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class SignalType(Enum):
    """信号类型"""
    BUY = "买入"
    SELL = "卖出"
    HOLD = "持有"
    NEUTRAL = "中性"
    OVERBOUGHT = "超买"
    OVERSOLD = "超卖"


@dataclass
class IndicatorResult:
    """指标计算结果"""
    name: str
    value: Any
    signal: SignalType
    description: str
    raw_data: Optional[Dict] = None


class TechnicalIndicators:
    """技术指标计算器"""

    def __init__(self, data: List[Dict]):
        """
        初始化

        Args:
            data: K线数据列表，每项包含 open, high, low, close, volume
        """
        self.data = data
        self.df = None

        if PANDAS_AVAILABLE and data:
            self.df = pd.DataFrame(data)
            # 确保数值类型正确
            for col in ['open', 'high', 'low', 'close', 'volume']:
                if col in self.df.columns:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

    def _check_data(self, min_length: int = 1) -> bool:
        """检查数据是否足够"""
        if not PANDAS_AVAILABLE:
            return False
        if self.df is None or len(self.df) < min_length:
            return False
        return True

    def ma(self, period: int = 20) -> IndicatorResult:
        """
        计算移动平均线 (Moving Average)

        Args:
            period: 周期，默认20日
        """
        if not self._check_data(period):
            return IndicatorResult(
                name=f"MA{period}",
                value=None,
                signal=SignalType.NEUTRAL,
                description="数据不足"
            )

        ma_value = self.df['close'].tail(period).mean()
        current_price = self.df['close'].iloc[-1]

        # 信号判断
        if current_price > ma_value * 1.02:
            signal = SignalType.BUY
            desc = f"价格在MA{period}上方，趋势向上"
        elif current_price < ma_value * 0.98:
            signal = SignalType.SELL
            desc = f"价格在MA{period}下方，趋势向下"
        else:
            signal = SignalType.HOLD
            desc = f"价格围绕MA{period}震荡"

        return IndicatorResult(
            name=f"MA{period}",
            value=round(ma_value, 2),
            signal=signal,
            description=desc,
            raw_data={
                "period": period,
                "current_price": round(current_price, 2),
                "ma_value": round(ma_value, 2)
            }
        )

    def ema(self, period: int = 12) -> IndicatorResult:
        """计算指数移动平均线"""
        if not self._check_data(period):
            return IndicatorResult(
                name=f"EMA{period}",
                value=None,
                signal=SignalType.NEUTRAL,
                description="数据不足"
            )

        ema_value = self.df['close'].ewm(span=period, adjust=False).mean().iloc[-1]

        return IndicatorResult(
            name=f"EMA{period}",
            value=round(ema_value, 2),
            signal=SignalType.NEUTRAL,
            description=f"{period}日指数移动平均线",
            raw_data={"period": period}
        )

    def rsi(self, period: int = 14) -> IndicatorResult:
        """
        计算RSI指标 (Relative Strength Index)

        RSI > 70: 超买
        RSI < 30: 超卖
        """
        if not self._check_data(period + 1):
            return IndicatorResult(
                name=f"RSI{period}",
                value=None,
                signal=SignalType.NEUTRAL,
                description="数据不足"
            )

        delta = self.df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_value = rsi.iloc[-1]

        if rsi_value > 70:
            signal = SignalType.OVERBOUGHT
            desc = f"RSI={rsi_value:.1f} > 70，超买区域，可能回调"
        elif rsi_value < 30:
            signal = SignalType.OVERSOLD
            desc = f"RSI={rsi_value:.1f} < 30，超卖区域，可能反弹"
        else:
            signal = SignalType.NEUTRAL
            desc = f"RSI={rsi_value:.1f}，中性区域"

        return IndicatorResult(
            name=f"RSI{period}",
            value=round(rsi_value, 2),
            signal=signal,
            description=desc,
            raw_data={"period": period, "overbought": 70, "oversold": 30}
        )

    def macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> IndicatorResult:
        """
        计算MACD指标

        MACD = EMA(fast) - EMA(slow)
        Signal = EMA(MACD, signal)
        Histogram = MACD - Signal
        """
        if not self._check_data(slow + signal):
            return IndicatorResult(
                name="MACD",
                value=None,
                signal=SignalType.NEUTRAL,
                description="数据不足"
            )

        ema_fast = self.df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = self.df['close'].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line

        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        current_hist = histogram.iloc[-1]
        prev_hist = histogram.iloc[-2] if len(histogram) > 1 else 0

        # 信号判断
        if current_macd > current_signal and current_hist > 0:
            if current_hist > prev_hist:
                sig = SignalType.BUY
                desc = "MACD在零轴上方，柱状图扩大，强势上涨"
            else:
                sig = SignalType.HOLD
                desc = "MACD在零轴上方，柱状图缩小，上涨动能减弱"
        elif current_macd < current_signal and current_hist < 0:
            if current_hist < prev_hist:
                sig = SignalType.SELL
                desc = "MACD在零轴下方，柱状图扩大，强势下跌"
            else:
                sig = SignalType.HOLD
                desc = "MACD在零轴下方，柱状图缩小，下跌动能减弱"
        elif current_hist > 0 and prev_hist <= 0:
            sig = SignalType.BUY
            desc = "MACD金叉，买入信号"
        elif current_hist < 0 and prev_hist >= 0:
            sig = SignalType.SELL
            desc = "MACD死叉，卖出信号"
        else:
            sig = SignalType.NEUTRAL
            desc = "MACD无明显信号"

        return IndicatorResult(
            name="MACD",
            value={
                "macd": round(current_macd, 3),
                "signal": round(current_signal, 3),
                "histogram": round(current_hist, 3)
            },
            signal=sig,
            description=desc,
            raw_data={
                "fast": fast,
                "slow": slow,
                "signal_period": signal
            }
        )

    def bollinger(self, period: int = 20, std_dev: float = 2.0) -> IndicatorResult:
        """
        计算布林带 (Bollinger Bands)

        上轨 = MA + 2 * STD
        中轨 = MA
        下轨 = MA - 2 * STD
        """
        if not self._check_data(period):
            return IndicatorResult(
                name="BOLL",
                value=None,
                signal=SignalType.NEUTRAL,
                description="数据不足"
            )

        ma = self.df['close'].rolling(window=period).mean()
        std = self.df['close'].rolling(window=period).std()

        upper = ma + std_dev * std
        lower = ma - std_dev * std

        current_price = self.df['close'].iloc[-1]
        current_upper = upper.iloc[-1]
        current_lower = lower.iloc[-1]
        current_ma = ma.iloc[-1]

        # 计算带宽和%b
        bandwidth = (current_upper - current_lower) / current_ma * 100
        percent_b = (current_price - current_lower) / (current_upper - current_lower) if current_upper != current_lower else 0.5

        # 信号判断
        if current_price > current_upper:
            sig = SignalType.OVERBOUGHT
            desc = f"价格突破上轨，可能超买，带宽={bandwidth:.1f}%"
        elif current_price < current_lower:
            sig = SignalType.OVERSOLD
            desc = f"价格突破下轨，可能超卖，带宽={bandwidth:.1f}%"
        elif percent_b > 0.8:
            sig = SignalType.SELL
            desc = f"价格接近上轨，%B={percent_b:.2f}"
        elif percent_b < 0.2:
            sig = SignalType.BUY
            desc = f"价格接近下轨，%B={percent_b:.2f}"
        else:
            sig = SignalType.HOLD
            desc = f"价格在中轨附近，%B={percent_b:.2f}"

        return IndicatorResult(
            name="BOLL",
            value={
                "upper": round(current_upper, 2),
                "middle": round(current_ma, 2),
                "lower": round(current_lower, 2),
                "bandwidth": round(bandwidth, 2),
                "percent_b": round(percent_b, 2)
            },
            signal=sig,
            description=desc,
            raw_data={"period": period, "std_dev": std_dev}
        )

    def kdj(self, n: int = 9, m1: int = 3, m2: int = 3) -> IndicatorResult:
        """
        计算KDJ指标

        RSV = (Close - LLV(Low, N)) / (HHV(High, N) - LLV(Low, N)) * 100
        K = SMA(RSV, M1, 1)
        D = SMA(K, M2, 1)
        J = 3*K - 2*D
        """
        if not self._check_data(n):
            return IndicatorResult(
                name="KDJ",
                value=None,
                signal=SignalType.NEUTRAL,
                description="数据不足"
            )

        low_list = self.df['low'].rolling(window=n, min_periods=n).min()
        high_list = self.df['high'].rolling(window=n, min_periods=n).max()
        rsv = (self.df['close'] - low_list) / (high_list - low_list) * 100

        k = rsv.ewm(com=m1-1, adjust=False).mean()
        d = k.ewm(com=m2-1, adjust=False).mean()
        j = 3 * k - 2 * d

        current_k = k.iloc[-1]
        current_d = d.iloc[-1]
        current_j = j.iloc[-1]
        prev_k = k.iloc[-2] if len(k) > 1 else current_k
        prev_d = d.iloc[-2] if len(d) > 1 else current_d

        # 信号判断
        if current_j > 100:
            sig = SignalType.OVERBOUGHT
            desc = f"J值={current_j:.1f} > 100，超买"
        elif current_j < 0:
            sig = SignalType.OVERSOLD
            desc = f"J值={current_j:.1f} < 0，超卖"
        elif prev_k <= prev_d and current_k > current_d:
            sig = SignalType.BUY
            desc = f"KDJ金叉，K={current_k:.1f}, D={current_d:.1f}"
        elif prev_k >= prev_d and current_k < current_d:
            sig = SignalType.SELL
            desc = f"KDJ死叉，K={current_k:.1f}, D={current_d:.1f}"
        else:
            sig = SignalType.HOLD
            desc = f"KDJ震荡，K={current_k:.1f}, D={current_d:.1f}, J={current_j:.1f}"

        return IndicatorResult(
            name="KDJ",
            value={
                "k": round(current_k, 2),
                "d": round(current_d, 2),
                "j": round(current_j, 2)
            },
            signal=sig,
            description=desc,
            raw_data={"n": n, "m1": m1, "m2": m2}
        )

    def volume_analysis(self) -> IndicatorResult:
        """成交量分析"""
        if not self._check_data(20):
            return IndicatorResult(
                name="VOL",
                value=None,
                signal=SignalType.NEUTRAL,
                description="数据不足"
            )

        current_vol = self.df['volume'].iloc[-1]
        avg_vol_5 = self.df['volume'].tail(5).mean()
        avg_vol_20 = self.df['volume'].tail(20).mean()

        vol_ratio = current_vol / avg_vol_20 if avg_vol_20 > 0 else 1

        if vol_ratio > 2:
            sig = SignalType.BUY if self.df['close'].iloc[-1] > self.df['close'].iloc[-2] else SignalType.SELL
            desc = f"成交量放大{vol_ratio:.1f}倍，{'放量上涨' if sig == SignalType.BUY else '放量下跌'}"
        elif vol_ratio > 1.5:
            sig = SignalType.HOLD
            desc = f"成交量温和放大{vol_ratio:.1f}倍"
        elif vol_ratio < 0.5:
            sig = SignalType.NEUTRAL
            desc = f"成交量萎缩至{vol_ratio:.1f}倍，观望"
        else:
            sig = SignalType.HOLD
            desc = f"成交量正常，{vol_ratio:.1f}倍均量"

        return IndicatorResult(
            name="VOL",
            value={
                "current": int(current_vol),
                "ma5": int(avg_vol_5),
                "ma20": int(avg_vol_20),
                "ratio": round(vol_ratio, 2)
            },
            signal=sig,
            description=desc
        )

    def analyze_all(self, indicators: List[str] = None) -> Dict[str, Any]:
        """
        批量计算多个指标

        Args:
            indicators: 指标列表，如 ['MA', 'RSI', 'MACD', 'BOLL', 'KDJ', 'VOL']
        """
        if indicators is None:
            indicators = ['MA', 'RSI', 'MACD', 'BOLL', 'KDJ', 'VOL']

        results = {}

        indicator_map = {
            'MA': lambda: self.ma(),
            'EMA': lambda: self.ema(),
            'RSI': lambda: self.rsi(),
            'MACD': lambda: self.macd(),
            'BOLL': lambda: self.bollinger(),
            'KDJ': lambda: self.kdj(),
            'VOL': lambda: self.volume_analysis()
        }

        for ind in indicators:
            ind_upper = ind.upper()
            if ind_upper in indicator_map:
                try:
                    results[ind_upper] = indicator_map[ind_upper]()
                except Exception as e:
                    results[ind_upper] = IndicatorResult(
                        name=ind_upper,
                        value=None,
                        signal=SignalType.NEUTRAL,
                        description=f"计算错误: {str(e)}"
                    )

        # 综合评分
        buy_signals = sum(1 for r in results.values() if r.signal == SignalType.BUY)
        sell_signals = sum(1 for r in results.values() if r.signal == SignalType.SELL)

        if buy_signals > sell_signals + 1:
            overall = SignalType.BUY
        elif sell_signals > buy_signals + 1:
            overall = SignalType.SELL
        else:
            overall = SignalType.HOLD

        return {
            "success": True,
            "indicators": {
                name: {
                    "value": result.value,
                    "signal": result.signal.value,
                    "description": result.description
                }
                for name, result in results.items()
            },
            "summary": {
                "buy_signals": buy_signals,
                "sell_signals": sell_signals,
                "overall": overall.value
            }
        }


def analyze_stock_technical(data: List[Dict], indicators: List[str] = None) -> Dict[str, Any]:
    """
    便捷函数: 分析股票技术指标

    Args:
        data: K线数据
        indicators: 要计算的指标列表

    Returns:
        分析结果字典
    """
    if not PANDAS_AVAILABLE:
        return {
            "success": False,
            "error": "需要安装pandas和numpy: pip install pandas numpy"
        }

    calculator = TechnicalIndicators(data)
    return calculator.analyze_all(indicators)


if __name__ == "__main__":
    # 测试代码
    print("=" * 60)
    print("技术指标计算模块测试")
    print("=" * 60)

    # 模拟数据
    test_data = [
        {"date": "2024-01-01", "open": 100, "high": 105, "low": 98, "close": 102, "volume": 10000},
        {"date": "2024-01-02", "open": 102, "high": 108, "low": 101, "close": 106, "volume": 12000},
        {"date": "2024-01-03", "open": 106, "high": 110, "low": 104, "close": 108, "volume": 15000},
        {"date": "2024-01-04", "open": 108, "high": 112, "low": 107, "close": 110, "volume": 18000},
        {"date": "2024-01-05", "open": 110, "high": 115, "low": 109, "close": 114, "volume": 20000},
        {"date": "2024-01-06", "open": 114, "high": 118, "low": 112, "close": 116, "volume": 22000},
        {"date": "2024-01-07", "open": 116, "high": 120, "low": 115, "close": 119, "volume": 25000},
        {"date": "2024-01-08", "open": 119, "high": 122, "low": 117, "close": 120, "volume": 28000},
        {"date": "2024-01-09", "open": 120, "high": 121, "low": 115, "close": 116, "volume": 30000},
        {"date": "2024-01-10", "open": 116, "high": 118, "low": 112, "close": 114, "volume": 26000},
    ]

    # 补充更多数据以满足计算需求
    for i in range(20):
        import random
        prev_close = test_data[-1]["close"]
        change = random.uniform(-5, 5)
        close = max(50, prev_close + change)
        high = close + random.uniform(0, 3)
        low = close - random.uniform(0, 3)
        open_price = close + random.uniform(-2, 2)
        test_data.append({
            "date": f"2024-01-{11+i:02d}",
            "open": round(open_price, 2),
            "high": round(high, 2),
            "low": round(max(1, low), 2),
            "close": round(close, 2),
            "volume": int(random.uniform(10000, 50000))
        })

    calculator = TechnicalIndicators(test_data)

    print("\n--- RSI ---")
    result = calculator.rsi()
    print(f"Value: {result.value}, Signal: {result.signal.value}")
    print(f"Desc: {result.description}")

    print("\n--- MACD ---")
    result = calculator.macd()
    print(f"Value: {result.value}, Signal: {result.signal.value}")
    print(f"Desc: {result.description}")

    print("\n--- BOLL ---")
    result = calculator.bollinger()
    print(f"Value: {result.value}, Signal: {result.signal.value}")
    print(f"Desc: {result.description}")

    print("\n--- 综合分析 ---")
    analysis = calculator.analyze_all()
    print(json.dumps(analysis, indent=2, ensure_ascii=False))
