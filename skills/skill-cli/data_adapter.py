#!/usr/bin/env python3
"""
Skill CLI 数据适配器 - 连接真实数据源
实现从mock数据到真实API的迁移
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# 技能目录
SKILLS_DIR = Path("/root/.openclaw/workspace/skills")


class DataSourceStatus(Enum):
    """数据源状态"""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    MOCK_MODE = "mock_mode"


@dataclass
class DataAdapterResult:
    """数据适配器结果"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    source: str = "unknown"  # "real", "mock", "cache"
    latency_ms: int = 0


class FinanceDataAdapter:
    """
    Finance Pro 数据适配器
    将真实 finance_pro.py 功能集成到 skill-cli
    """
    
    def __init__(self):
        self.module = None
        self.status = DataSourceStatus.UNAVAILABLE
        self._load_module()
    
    def _load_module(self):
        """加载 finance_pro 模块"""
        try:
            import importlib.util
            finance_pro_path = SKILLS_DIR / 'finance-pro' / 'finance_pro.py'
            
            if not finance_pro_path.exists():
                # 尝试其他路径
                finance_pro_path = SKILLS_DIR / 'finance-pro' / 'finance-pro.py'
            
            if finance_pro_path.exists():
                spec = importlib.util.spec_from_file_location('finance_pro_real', str(finance_pro_path))
                self.module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(self.module)
                self.status = DataSourceStatus.AVAILABLE
            else:
                self.status = DataSourceStatus.MOCK_MODE
        except Exception as e:
            print(f"[FinanceAdapter] 加载真实模块失败: {e}", file=sys.stderr)
            self.status = DataSourceStatus.MOCK_MODE
    
    def get_stock_quote(self, symbol: str) -> DataAdapterResult:
        """获取股票实时行情"""
        import time
        start = time.time()
        
        if self.status == DataSourceStatus.AVAILABLE and self.module:
            try:
                result = self.module.get_stock_quote_a_share(symbol)
                latency = int((time.time() - start) * 1000)
                
                # 如果真实数据源返回失败，降级到mock
                if not result.get("success", False):
                    mock_result = self._mock_quote(symbol)
                    mock_result.error = f"真实数据源失败: {result.get('error')}, 已降级到mock"
                    return mock_result
                
                return DataAdapterResult(
                    success=True,
                    data=result,
                    error=None,
                    source="real",
                    latency_ms=latency
                )
            except Exception as e:
                # 异常时降级到mock
                mock_result = self._mock_quote(symbol)
                mock_result.error = f"真实数据源异常: {str(e)}, 已降级到mock"
                return mock_result
        
        # Fallback to mock
        return self._mock_quote(symbol)
    
    def get_stock_history(self, symbol: str, period: str = "1mo") -> DataAdapterResult:
        """获取股票历史数据"""
        import time
        start = time.time()
        
        if self.status == DataSourceStatus.AVAILABLE and self.module:
            try:
                result = self.module.get_stock_history(symbol, period)
                latency = int((time.time() - start) * 1000)
                
                # 如果真实数据源返回失败，降级到mock
                if not result.get("success", False):
                    mock_result = self._mock_history(symbol)
                    mock_result.error = f"真实数据源失败: {result.get('error')}, 已降级到mock"
                    return mock_result
                
                return DataAdapterResult(
                    success=True,
                    data=result,
                    error=None,
                    source="real",
                    latency_ms=latency
                )
            except Exception as e:
                # 异常时降级到mock
                mock_result = self._mock_history(symbol)
                mock_result.error = f"真实数据源异常: {str(e)}, 已降级到mock"
                return mock_result
        
        return self._mock_history(symbol)
    
    def technical_analysis(self, symbol: str, indicators: List[str]) -> DataAdapterResult:
        """技术分析"""
        import time
        start = time.time()
        
        if self.status == DataSourceStatus.AVAILABLE and self.module:
            try:
                result = self.module.technical_analysis(symbol, indicators)
                latency = int((time.time() - start) * 1000)
                
                # 如果真实数据源返回失败，降级到mock
                if not result.get("success", False):
                    mock_result = self._mock_analysis(symbol, indicators)
                    mock_result.error = f"真实数据源失败: {result.get('error')}, 已降级到mock"
                    return mock_result
                
                return DataAdapterResult(
                    success=True,
                    data=result,
                    error=None,
                    source="real",
                    latency_ms=latency
                )
            except Exception as e:
                # 异常时降级到mock
                mock_result = self._mock_analysis(symbol, indicators)
                mock_result.error = f"真实数据源异常: {str(e)}, 已降级到mock"
                return mock_result
        
        return self._mock_analysis(symbol, indicators)
    
    def get_financial_report(self, symbol: str, quarter: str = "latest") -> DataAdapterResult:
        """获取财务报表"""
        import time
        start = time.time()
        
        if self.status == DataSourceStatus.AVAILABLE and self.module:
            try:
                result = self.module.get_financial_report(symbol, quarter)
                latency = int((time.time() - start) * 1000)
                
                # 如果真实数据源返回失败，降级到mock
                if not result.get("success", False):
                    mock_result = self._mock_financial(symbol)
                    mock_result.error = f"真实数据源失败: {result.get('error')}, 已降级到mock"
                    return mock_result
                
                return DataAdapterResult(
                    success=True,
                    data=result,
                    error=None,
                    source="real",
                    latency_ms=latency
                )
            except Exception as e:
                # 异常时降级到mock
                mock_result = self._mock_financial(symbol)
                mock_result.error = f"真实数据源异常: {str(e)}, 已降级到mock"
                return mock_result
        
        return self._mock_financial(symbol)
    
    def _mock_quote(self, symbol: str) -> DataAdapterResult:
        """Mock行情数据"""
        import random
        base_price = random.uniform(10, 200)
        change = random.uniform(-5, 5)
        
        return DataAdapterResult(
            success=True,
            data={
                "symbol": symbol,
                "name": f"股票-{symbol[:6]}",
                "price": round(base_price, 2),
                "change": round(change, 2),
                "change_amount": round(base_price * change / 100, 2),
                "volume": random.randint(1000000, 10000000),
                "high": round(base_price * 1.02, 2),
                "low": round(base_price * 0.98, 2),
                "open": round(base_price * (1 - change/200), 2),
                "prev_close": round(base_price / (1 + change/100), 2),
                "source": "mock",
                "note": "真实数据源不可用，使用模拟数据"
            },
            source="mock"
        )
    
    def _mock_history(self, symbol: str) -> DataAdapterResult:
        """Mock历史数据"""
        import random
        from datetime import datetime, timedelta
        
        data = []
        base_price = random.uniform(50, 150)
        for i in range(30):
            date = datetime.now() - timedelta(days=30-i)
            change = random.uniform(-0.03, 0.03)
            base_price *= (1 + change)
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(base_price * 0.99, 2),
                "close": round(base_price, 2),
                "high": round(base_price * 1.02, 2),
                "low": round(base_price * 0.98, 2),
                "volume": random.randint(1000000, 5000000)
            })
        
        return DataAdapterResult(
            success=True,
            data={
                "symbol": symbol,
                "period": "1mo",
                "data_points": len(data),
                "data": data,
                "source": "mock"
            },
            source="mock"
        )
    
    def _mock_analysis(self, symbol: str, indicators: List[str]) -> DataAdapterResult:
        """Mock技术分析"""
        import random
        
        results = {}
        for ind in indicators:
            ind = ind.upper()
            if ind == "MA":
                results["MA"] = {
                    "success": True,
                    "ma": {
                        "MA5": round(random.uniform(10, 100), 2),
                        "MA10": round(random.uniform(10, 100), 2),
                        "MA20": round(random.uniform(10, 100), 2),
                        "MA60": round(random.uniform(10, 100), 2)
                    }
                }
            elif ind == "RSI":
                rsi = random.uniform(20, 80)
                signal = "超买" if rsi > 70 else "超卖" if rsi < 30 else "中性"
                results["RSI"] = {
                    "success": True,
                    "rsi": round(rsi, 2),
                    "signal": signal,
                    "period": 14
                }
            else:
                results[ind] = {"success": False, "error": f"暂未实现指标: {ind}"}
        
        return DataAdapterResult(
            success=True,
            data={
                "symbol": symbol,
                "indicators": results,
                "source": "mock"
            },
            source="mock"
        )
    
    def _mock_financial(self, symbol: str) -> DataAdapterResult:
        """Mock财务数据"""
        import random
        
        return DataAdapterResult(
            success=True,
            data={
                "symbol": symbol,
                "quarter": "2024Q3",
                "revenue": f"{random.uniform(10, 1000):.2f}亿",
                "net_profit": f"{random.uniform(1, 100):.2f}亿",
                "gross_margin": f"{random.uniform(10, 50):.2f}%",
                "source": "mock"
            },
            source="mock"
        )


class ResearchDataAdapter:
    """
    Research Pro 数据适配器
    集成搜索和分析功能
    """
    
    def __init__(self):
        self.status = DataSourceStatus.MOCK_MODE
    
    def deep_research(self, topic: str, depth: str = "comprehensive") -> DataAdapterResult:
        """深度研究"""
        # 目前使用mock，后续可接入真实搜索API
        return DataAdapterResult(
            success=True,
            data={
                "topic": topic,
                "depth": depth,
                "summary": f"关于'{topic}'的研究摘要（模拟数据）",
                "key_findings": [
                    "发现1: 这是模拟数据",
                    "发现2: 真实数据接入需要配置搜索API",
                    "发现3: 考虑接入Tavily或类似服务"
                ],
                "sources": ["模拟源1", "模拟源2"],
                "source": "mock"
            },
            source="mock"
        )
    
    def realtime_search(self, query: str, sources: List[str] = None) -> DataAdapterResult:
        """实时搜索"""
        return DataAdapterResult(
            success=True,
            data={
                "query": query,
                "sources": sources or ["news", "blog"],
                "results": [
                    {"title": f"关于'{query}'的结果1", "url": "#", "snippet": "模拟搜索结果..."},
                    {"title": f"关于'{query}'的结果2", "url": "#", "snippet": "模拟搜索结果..."}
                ],
                "source": "mock"
            },
            source="mock"
        )


# 全局适配器实例
_finance_adapter = None
_research_adapter = None


def get_finance_adapter() -> FinanceDataAdapter:
    """获取Finance数据适配器（单例）"""
    global _finance_adapter
    if _finance_adapter is None:
        _finance_adapter = FinanceDataAdapter()
    return _finance_adapter


def get_research_adapter() -> ResearchDataAdapter:
    """获取Research数据适配器（单例）"""
    global _research_adapter
    if _research_adapter is None:
        _research_adapter = ResearchDataAdapter()
    return _research_adapter


def get_adapter_status() -> Dict[str, Any]:
    """获取所有适配器状态"""
    finance = get_finance_adapter()
    research = get_research_adapter()
    
    return {
        "finance-pro": {
            "status": finance.status.value,
            "available": finance.status == DataSourceStatus.AVAILABLE
        },
        "research-pro": {
            "status": research.status.value,
            "available": research.status == DataSourceStatus.AVAILABLE
        }
    }


if __name__ == "__main__":
    # 测试适配器
    print("测试 Finance Data Adapter")
    print("-" * 40)
    
    adapter = get_finance_adapter()
    print(f"适配器状态: {adapter.status.value}")
    print()
    
    # 测试行情获取
    result = adapter.get_stock_quote("000001.SZ")
    print(f"行情查询结果:")
    print(f"  成功: {result.success}")
    print(f"  数据源: {result.source}")
    print(f"  延迟: {result.latency_ms}ms")
    if result.data:
        print(f"  数据: {json.dumps(result.data, indent=2, ensure_ascii=False)[:200]}...")
    print()
    
    # 测试技术分析
    result = adapter.technical_analysis("000001.SZ", ["MA", "RSI"])
    print(f"技术分析结果:")
    print(f"  成功: {result.success}")
    print(f"  数据源: {result.source}")
    if result.data:
        print(f"  数据: {json.dumps(result.data, indent=2, ensure_ascii=False)[:200]}...")
