#!/usr/bin/env python3
"""
Finance Pro - 统一数据适配器
支持多数据源切换和统一管理
"""

import os
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum

class DataSourceType(Enum):
    """数据源类型"""
    AKSHARE = "akshare"
    TUSHARE = "tushare"
    YFINANCE = "yfinance"

class DataProvider(ABC):
    """数据提供者抽象基类"""
    
    @abstractmethod
    def get_name(self) -> str:
        """返回数据源名称"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查数据源是否可用"""
        pass
    
    @abstractmethod
    def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """获取股票实时行情"""
        pass
    
    @abstractmethod
    def get_stock_history(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        """获取股票历史数据"""
        pass
    
    @abstractmethod
    def search_stocks(self, keyword: str) -> Dict[str, Any]:
        """搜索股票"""
        pass

class AkshareProvider(DataProvider):
    """Akshare数据源提供者"""
    
    def __init__(self):
        self._ak = None
        self._pd = None
        self._try_import()
    
    def _try_import(self):
        """尝试导入依赖"""
        try:
            import akshare as ak
            import pandas as pd
            self._ak = ak
            self._pd = pd
        except ImportError:
            pass
    
    def get_name(self) -> str:
        return "Akshare"
    
    def is_available(self) -> bool:
        return self._ak is not None
    
    def _normalize_symbol(self, symbol: str) -> str:
        """标准化股票代码"""
        # 移除交易所后缀
        return symbol.split('.')[0] if '.' in symbol else symbol
    
    def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """获取A股实时行情"""
        if not self.is_available():
            return {"success": False, "error": "akshare未安装"}
        
        try:
            code = self._normalize_symbol(symbol)
            
            # 获取实时行情
            df = self._ak.stock_zh_a_spot_em()
            stock_info = df[df['代码'] == code]
            
            if stock_info.empty:
                return {"success": False, "error": f"未找到股票: {symbol}"}
            
            row = stock_info.iloc[0]
            
            return {
                "success": True,
                "source": "akshare",
                "symbol": symbol,
                "code": code,
                "name": str(row.get('名称', 'N/A')),
                "price": float(row.get('最新价', 0)) if self._pd.notna(row.get('最新价')) else 0,
                "change_percent": float(row.get('涨跌幅', 0)) if self._pd.notna(row.get('涨跌幅')) else 0,
                "change_amount": float(row.get('涨跌额', 0)) if self._pd.notna(row.get('涨跌额')) else 0,
                "volume": int(row.get('成交量', 0)) if self._pd.notna(row.get('成交量')) else 0,
                "amount": float(row.get('成交额', 0)) if self._pd.notna(row.get('成交额')) else 0,
                "high": float(row.get('最高', 0)) if self._pd.notna(row.get('最高')) else 0,
                "low": float(row.get('最低', 0)) if self._pd.notna(row.get('最低')) else 0,
                "open": float(row.get('今开', 0)) if self._pd.notna(row.get('今开')) else 0,
                "prev_close": float(row.get('昨收', 0)) if self._pd.notna(row.get('昨收')) else 0,
                "pe_ttm": float(row.get('市盈率-动态', 0)) if self._pd.notna(row.get('市盈率-动态')) else None,
                "pb": float(row.get('市净率', 0)) if self._pd.notna(row.get('市净率')) else None,
                "market_cap": float(row.get('总市值', 0)) if self._pd.notna(row.get('总市值')) else None,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": f"获取行情失败: {str(e)}"}
    
    def get_stock_history(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        """获取股票历史数据"""
        if not self.is_available():
            return {"success": False, "error": "akshare未安装"}
        
        try:
            code = self._normalize_symbol(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            df = self._ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
                adjust="qfq"
            )
            
            if df.empty:
                return {"success": False, "error": f"未找到历史数据: {symbol}"}
            
            records = df.to_dict('records')
            
            return {
                "success": True,
                "source": "akshare",
                "symbol": symbol,
                "code": code,
                "days": days,
                "data_points": len(records),
                "data": [
                    {
                        "date": str(r.get('日期')),
                        "open": float(r.get('开盘', 0)),
                        "close": float(r.get('收盘', 0)),
                        "high": float(r.get('最高', 0)),
                        "low": float(r.get('最低', 0)),
                        "volume": int(r.get('成交量', 0)),
                        "amount": float(r.get('成交额', 0)) if '成交额' in r else None,
                        "amplitude": float(r.get('振幅', 0)) if '振幅' in r else None,
                        "change_percent": float(r.get('涨跌幅', 0)) if '涨跌幅' in r else None
                    }
                    for r in records
                ]
            }
        except Exception as e:
            return {"success": False, "error": f"获取历史数据失败: {str(e)}"}
    
    def search_stocks(self, keyword: str) -> Dict[str, Any]:
        """搜索股票"""
        if not self.is_available():
            return {"success": False, "error": "akshare未安装"}
        
        try:
            # 获取所有A股列表
            df = self._ak.stock_zh_a_spot_em()
            
            # 按名称或代码搜索
            mask = df['名称'].str.contains(keyword, na=False) | \
                   df['代码'].str.contains(keyword, na=False)
            results = df[mask].head(10)
            
            return {
                "success": True,
                "source": "akshare",
                "keyword": keyword,
                "count": len(results),
                "stocks": [
                    {
                        "code": str(row['代码']),
                        "name": str(row['名称']),
                        "price": float(row.get('最新价', 0)) if self._pd.notna(row.get('最新价')) else 0,
                        "change": float(row.get('涨跌幅', 0)) if self._pd.notna(row.get('涨跌幅')) else 0
                    }
                    for _, row in results.iterrows()
                ]
            }
        except Exception as e:
            return {"success": False, "error": f"搜索失败: {str(e)}"}
    
    def get_index_list(self) -> Dict[str, Any]:
        """获取指数列表"""
        if not self.is_available():
            return {"success": False, "error": "akshare未安装"}
        
        try:
            # 主要指数
            indices = [
                {"code": "000001", "name": "上证指数", "exchange": "SH"},
                {"code": "000300", "name": "沪深300", "exchange": "SH"},
                {"code": "000905", "name": "中证500", "exchange": "SH"},
                {"code": "399001", "name": "深证成指", "exchange": "SZ"},
                {"code": "399006", "name": "创业板指", "exchange": "SZ"},
                {"code": "399005", "name": "中小板指", "exchange": "SZ"},
            ]
            
            # 获取实时行情
            df = self._ak.stock_zh_index_spot()
            
            result_indices = []
            for idx in indices:
                code = idx['code']
                spot = df[df['代码'] == code]
                if not spot.empty:
                    row = spot.iloc[0]
                    result_indices.append({
                        "code": code,
                        "name": idx['name'],
                        "price": float(row.get('最新价', 0)) if pd.notna(row.get('最新价')) else 0,
                        "change": float(row.get('涨跌幅', 0)) if pd.notna(row.get('涨跌幅')) else 0
                    })
            
            return {
                "success": True,
                "source": "akshare",
                "indices": result_indices
            }
        except Exception as e:
            return {"success": False, "error": f"获取指数失败: {str(e)}"}

class TushareProvider(DataProvider):
    """Tushare数据源提供者 (需要API Token)"""
    
    def __init__(self, token: Optional[str] = None):
        self._ts = None
        self._pro = None
        self.token = token or os.getenv('TUSHARE_TOKEN')
        self._try_import()
    
    def _try_import(self):
        try:
            import tushare as ts
            self._ts = ts
            if self.token:
                self._pro = ts.pro_api(self.token)
        except ImportError:
            pass
    
    def get_name(self) -> str:
        return "Tushare"
    
    def is_available(self) -> bool:
        return self._ts is not None and self._pro is not None
    
    def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        if not self.is_available():
            return {"success": False, "error": "Tushare未安装或未配置TOKEN"}
        
        try:
            # 转换代码格式
            code = symbol.split('.')[0] if '.' in symbol else symbol
            exchange = symbol.split('.')[1] if '.' in symbol else 'SH'
            ts_code = f"{code}.{exchange}"
            
            # 获取日线数据
            df = self._pro.daily(ts_code=ts_code, limit=1)
            
            if df.empty:
                return {"success": False, "error": f"未找到股票: {symbol}"}
            
            row = df.iloc[0]
            
            return {
                "success": True,
                "source": "tushare",
                "symbol": symbol,
                "code": code,
                "open": float(row.get('open', 0)),
                "high": float(row.get('high', 0)),
                "low": float(row.get('low', 0)),
                "close": float(row.get('close', 0)),
                "volume": int(row.get('vol', 0)),
                "amount": float(row.get('amount', 0)),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": f"获取行情失败: {str(e)}"}
    
    def get_stock_history(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        if not self.is_available():
            return {"success": False, "error": "Tushare未安装或未配置TOKEN"}
        
        try:
            code = symbol.split('.')[0] if '.' in symbol else symbol
            exchange = symbol.split('.')[1] if '.' in symbol else 'SH'
            ts_code = f"{code}.{exchange}"
            
            df = self._pro.daily(ts_code=ts_code, limit=days)
            
            if df.empty:
                return {"success": False, "error": f"未找到历史数据: {symbol}"}
            
            return {
                "success": True,
                "source": "tushare",
                "symbol": symbol,
                "days": days,
                "data_points": len(df),
                "data": df.to_dict('records')
            }
        except Exception as e:
            return {"success": False, "error": f"获取历史数据失败: {str(e)}"}
    
    def search_stocks(self, keyword: str) -> Dict[str, Any]:
        if not self.is_available():
            return {"success": False, "error": "Tushare未安装或未配置TOKEN"}
        
        try:
            df = self._pro.stock_basic(exchange='', list_status='L')
            mask = df['name'].str.contains(keyword, na=False) | \
                   df['ts_code'].str.contains(keyword, na=False)
            results = df[mask].head(10)
            
            return {
                "success": True,
                "source": "tushare",
                "keyword": keyword,
                "count": len(results),
                "stocks": results.to_dict('records')
            }
        except Exception as e:
            return {"success": False, "error": f"搜索失败: {str(e)}"}

class FinanceDataAdapter:
    """
    金融数据统一适配器
    支持多数据源自动切换和故障转移
    """
    
    def __init__(self, preferred_source: Optional[DataSourceType] = None):
        self.providers: Dict[DataSourceType, DataProvider] = {}
        self.preferred_source = preferred_source
        
        # 初始化所有数据源
        self._init_providers()
    
    def _init_providers(self):
        """初始化所有数据源提供者"""
        # Akshare (免费，无需Token)
        akshare = AkshareProvider()
        if akshare.is_available():
            self.providers[DataSourceType.AKSHARE] = akshare
        
        # Tushare (需要Token)
        tushare = TushareProvider()
        if tushare.is_available():
            self.providers[DataSourceType.TUSHARE] = tushare
    
    def get_available_sources(self) -> List[str]:
        """获取可用的数据源列表"""
        return [p.get_name() for p in self.providers.values()]
    
    def _get_provider(self, source: Optional[DataSourceType] = None) -> Optional[DataProvider]:
        """获取数据提供者"""
        if source and source in self.providers:
            return self.providers[source]
        
        if self.preferred_source and self.preferred_source in self.providers:
            return self.providers[self.preferred_source]
        
        # 默认优先使用akshare
        if DataSourceType.AKSHARE in self.providers:
            return self.providers[DataSourceType.AKSHARE]
        
        # 返回第一个可用的
        return next(iter(self.providers.values())) if self.providers else None
    
    def get_stock_quote(self, symbol: str, source: Optional[DataSourceType] = None) -> Dict[str, Any]:
        """获取股票实时行情"""
        provider = self._get_provider(source)
        if not provider:
            return {
                "success": False,
                "error": "没有可用的数据源。请安装: pip install akshare",
                "available_sources": self.get_available_sources()
            }
        
        result = provider.get_stock_quote(symbol)
        result['provider'] = provider.get_name()
        return result
    
    def get_stock_history(self, symbol: str, days: int = 30, 
                         source: Optional[DataSourceType] = None) -> Dict[str, Any]:
        """获取股票历史数据"""
        provider = self._get_provider(source)
        if not provider:
            return {
                "success": False,
                "error": "没有可用的数据源。请安装: pip install akshare"
            }
        
        result = provider.get_stock_history(symbol, days)
        result['provider'] = provider.get_name()
        return result
    
    def search_stocks(self, keyword: str, source: Optional[DataSourceType] = None) -> Dict[str, Any]:
        """搜索股票"""
        provider = self._get_provider(source)
        if not provider:
            return {
                "success": False,
                "error": "没有可用的数据源"
            }
        
        result = provider.search_stocks(keyword)
        result['provider'] = provider.get_name()
        return result
    
    def get_index_list(self) -> Dict[str, Any]:
        """获取主要指数列表"""
        provider = self._get_provider()
        if provider and hasattr(provider, 'get_index_list'):
            return provider.get_index_list()
        
        return {
            "success": False,
            "error": "当前数据源不支持指数查询"
        }


# 便捷函数 - 全局单例
_adapter = None

def get_adapter() -> FinanceDataAdapter:
    """获取全局数据适配器实例"""
    global _adapter
    if _adapter is None:
        _adapter = FinanceDataAdapter()
    return _adapter


def get_finance_adapter() -> FinanceDataAdapter:
    """获取金融数据适配器实例 (别名，供skill-cli使用)"""
    return get_adapter()


def get_research_adapter():
    """获取研究模块适配器 (兼容函数，供skill-cli使用)
    
    实际从research-pro导入SearchAdapter
    """
    import sys
    import os
    # 添加research-pro到路径
    research_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'research-pro')
    if research_path not in sys.path:
        sys.path.insert(0, research_path)
    
    try:
        from search_adapter import SearchAdapter
        return SearchAdapter()
    except ImportError:
        # 如果research-pro不可用，返回None
        return None


def get_stock_quote(symbol: str) -> Dict[str, Any]:
    """便捷函数: 获取股票行情"""
    return get_adapter().get_stock_quote(symbol)


def get_stock_history(symbol: str, days: int = 30) -> Dict[str, Any]:
    """便捷函数: 获取股票历史数据"""
    return get_adapter().get_stock_history(symbol, days)


def search_stocks(keyword: str) -> Dict[str, Any]:
    """便捷函数: 搜索股票"""
    return get_adapter().search_stocks(keyword)


def get_index_list() -> Dict[str, Any]:
    """便捷函数: 获取指数列表"""
    return get_adapter().get_index_list()


if __name__ == "__main__":
    # 测试代码
    print("=" * 60)
    print("Finance Pro 数据适配器测试")
    print("=" * 60)
    
    adapter = FinanceDataAdapter()
    
    print(f"\n可用数据源: {adapter.get_available_sources()}")
    
    # 测试获取行情
    print("\n--- 测试: 获取茅台行情 ---")
    result = adapter.get_stock_quote("600519.SH")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 测试搜索
    print("\n--- 测试: 搜索'茅台' ---")
    result = adapter.search_stocks("茅台")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 测试指数
    print("\n--- 测试: 获取主要指数 ---")
    result = adapter.get_index_list()
    print(json.dumps(result, indent=2, ensure_ascii=False))
