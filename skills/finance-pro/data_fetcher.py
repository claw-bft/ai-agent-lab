#!/usr/bin/env python3
"""
Data Fetcher - 健壮的股票数据获取模块
实现akshare数据获取的健壮性增强，包括重试机制、本地缓存和优雅降级
"""

import os
import json
import time
import hashlib
import functools
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('data_fetcher')

# 默认配置
DEFAULT_CONFIG = {
    'max_retries': 5,
    'timeout': 10,
    'cache_duration_minutes': 15,
    'base_delay': 1.0,  # 初始重试延迟（秒）
    'max_delay': 60.0,  # 最大重试延迟（秒）
    'backoff_factor': 2.0,  # 指数退避因子
}

# 缓存目录
CACHE_DIR = Path(__file__).parent / '.cache'
CACHE_DIR.mkdir(exist_ok=True)


@dataclass
class FetchResult:
    """数据获取结果"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    from_cache: bool = False
    cache_time: Optional[str] = None
    fetch_time: Optional[str] = None
    retries: int = 0
    
    def to_dict(self) -> Dict:
        return asdict(self)


class CacheManager:
    """本地JSON缓存管理器"""
    
    def __init__(self, cache_dir: Path = None, duration_minutes: int = 15):
        self.cache_dir = cache_dir or CACHE_DIR
        self.cache_dir.mkdir(exist_ok=True)
        self.duration = timedelta(minutes=duration_minutes)
    
    def _get_cache_key(self, func_name: str, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = f"{func_name}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, func_name: str, *args, **kwargs) -> Optional[Dict]:
        """获取缓存数据"""
        cache_key = self._get_cache_key(func_name, *args, **kwargs)
        cache_path = self._get_cache_path(cache_key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            
            cache_time = datetime.fromisoformat(cached.get('cache_time', '2000-01-01'))
            if datetime.now() - cache_time > self.duration:
                logger.debug(f"缓存已过期: {func_name}")
                return None
            
            logger.debug(f"缓存命中: {func_name}")
            return cached
        except Exception as e:
            logger.warning(f"读取缓存失败: {e}")
            return None
    
    def set(self, func_name: str, data: Any, *args, **kwargs) -> bool:
        """设置缓存数据"""
        cache_key = self._get_cache_key(func_name, *args, **kwargs)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            cache_data = {
                'cache_time': datetime.now().isoformat(),
                'func_name': func_name,
                'args': str(args),
                'kwargs': str(sorted(kwargs.items())),
                'data': data
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"缓存已保存: {func_name}")
            return True
        except Exception as e:
            logger.warning(f"保存缓存失败: {e}")
            return False
    
    def clear(self, func_name: str = None):
        """清除缓存"""
        if func_name:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached = json.load(f)
                    if cached.get('func_name') == func_name:
                        cache_file.unlink()
                        logger.info(f"已清除缓存: {func_name}")
                except:
                    pass
        else:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            logger.info("已清除所有缓存")
    
    def cleanup_expired(self):
        """清理过期缓存"""
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                cache_time = datetime.fromisoformat(cached.get('cache_time', '2000-01-01'))
                if datetime.now() - cache_time > self.duration:
                    cache_file.unlink()
                    count += 1
            except:
                pass
        if count > 0:
            logger.info(f"已清理 {count} 个过期缓存文件")


class RetryHandler:
    """重试处理器 - 指数退避策略"""
    
    def __init__(self, max_retries: int = 5, base_delay: float = 1.0, 
                 max_delay: float = 60.0, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
    
    def calculate_delay(self, attempt: int) -> float:
        """计算第attempt次重试的延迟时间"""
        delay = self.base_delay * (self.backoff_factor ** attempt)
        return min(delay, self.max_delay)
    
    def execute(self, func: Callable, *args, **kwargs) -> tuple[Any, int, Optional[str]]:
        """执行带重试的函数
        Returns:
            (result, retries_used, error_message)
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                return result, attempt, None
            except Exception as e:
                last_error = str(e)
                logger.warning(f"第 {attempt + 1} 次尝试失败: {last_error}")
                
                if attempt < self.max_retries:
                    delay = self.calculate_delay(attempt)
                    logger.info(f"等待 {delay:.1f} 秒后重试...")
                    time.sleep(delay)
        
        return None, self.max_retries, last_error


class DataFetcher:
    """健壮的数据获取器 - 集成重试机制、缓存和优雅降级"""
    
    def __init__(self, config: Dict = None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.cache = CacheManager(duration_minutes=self.config['cache_duration_minutes'])
        self.retry_handler = RetryHandler(
            max_retries=self.config['max_retries'],
            base_delay=self.config['base_delay'],
            max_delay=self.config['max_delay'],
            backoff_factor=self.config['backoff_factor']
        )
        self._ak = None
    
    def _get_akshare(self):
        """延迟加载akshare模块"""
        if self._ak is None:
            try:
                import akshare as ak
                self._ak = ak
                logger.info("akshare模块加载成功")
            except ImportError:
                logger.error("akshare模块未安装")
                raise ImportError("akshare模块未安装，请运行: pip install akshare")
        return self._ak
    
    def _fetch_with_retry(self, fetch_func: Callable, cache_key: str, 
                          *args, **kwargs) -> FetchResult:
        """带重试和缓存的数据获取"""
        fetch_time = datetime.now().isoformat()
        
        # 1. 尝试获取缓存
        cached = self.cache.get(cache_key, *args, **kwargs)
        if cached:
            return FetchResult(
                success=True,
                data=cached.get('data'),
                from_cache=True,
                cache_time=cached.get('cache_time'),
                fetch_time=fetch_time,
                retries=0
            )
        
        # 2. 尝试获取新数据（带重试）
        result, retries, error = self.retry_handler.execute(fetch_func, *args, **kwargs)
        
        if result is not None:
            # 保存到缓存
            self.cache.set(cache_key, result, *args, **kwargs)
            return FetchResult(
                success=True,
                data=result,
                from_cache=False,
                fetch_time=fetch_time,
                retries=retries
            )
        
        # 3. 失败时返回空数据（优雅降级）
        logger.error(f"数据获取失败，已重试 {retries} 次: {error}")
        return FetchResult(
            success=False,
            data=None,
            error=error,
            from_cache=False,
            fetch_time=fetch_time,
            retries=retries
        )
    
    # ========== 股票数据获取方法 ==========
    
    def get_stock_quote(self, symbol: str) -> FetchResult:
        """获取股票实时行情"""
        def _fetch():
            ak = self._get_akshare()
            # 转换symbol格式
            if '.' in symbol:
                code, exchange = symbol.split('.')
                if exchange == 'SZ':
                    df = ak.stock_sz_a_spot_em()
                elif exchange == 'SH':
                    df = ak.stock_sh_a_spot_em()
                else:
                    df = ak.stock_zh_a_spot_em()
                # 筛选特定股票
                result = df[df['代码'] == code]
                if not result.empty:
                    row = result.iloc[0]
                    return {
                        'symbol': symbol,
                        'name': row.get('名称', ''),
                        'price': float(row.get('最新价', 0)),
                        'change': float(row.get('涨跌额', 0)),
                        'change_percent': float(row.get('涨跌幅', 0)),
                        'volume': int(row.get('成交量', 0)),
                        'amount': float(row.get('成交额', 0)),
                        'high': float(row.get('最高', 0)),
                        'low': float(row.get('最低', 0)),
                        'open': float(row.get('今开', 0)),
                        'pre_close': float(row.get('昨收', 0)),
                        'pe_ttm': float(row.get('市盈率-动态', 0)) if pd.notna(row.get('市盈率-动态')) else None,
                        'pb': float(row.get('市净率', 0)) if pd.notna(row.get('市净率')) else None,
                    }
            return None
        
        import pandas as pd
        return self._fetch_with_retry(_fetch, 'get_stock_quote', symbol)
    
    def get_stock_history(self, symbol: str, days: int = 30) -> FetchResult:
        """获取股票历史数据"""
        def _fetch():
            ak = self._get_akshare()
            if '.' in symbol:
                code, _ = symbol.split('.')
            else:
                code = symbol
            
            df = ak.stock_zh_a_hist(symbol=code, period="daily", 
                                    start_date=None, end_date=None, adjust="qfq")
            if df is not None and not df.empty:
                # 只取最近days天
                df = df.tail(days)
                records = []
                for _, row in df.iterrows():
                    records.append({
                        'date': row.get('日期', ''),
                        'open': float(row.get('开盘', 0)),
                        'close': float(row.get('收盘', 0)),
                        'high': float(row.get('最高', 0)),
                        'low': float(row.get('最低', 0)),
                        'volume': int(row.get('成交量', 0)),
                        'amount': float(row.get('成交额', 0)),
                        'amplitude': float(row.get('振幅', 0)),
                        'change_percent': float(row.get('涨跌幅', 0)),
                        'change': float(row.get('涨跌额', 0)),
                        'turnover': float(row.get('换手率', 0)) if '换手率' in row else None,
                    })
                return {'symbol': symbol, 'days': len(records), 'data': records}
            return None
        
        return self._fetch_with_retry(_fetch, 'get_stock_history', symbol, days)
    
    def get_stock_list(self) -> FetchResult:
        """获取A股股票列表"""
        def _fetch():
            ak = self._get_akshare()
            df = ak.stock_zh_a_spot_em()
            stocks = []
            for _, row in df.iterrows():
                stocks.append({
                    'code': row.get('代码', ''),
                    'name': row.get('名称', ''),
                    'price': float(row.get('最新价', 0)),
                    'change_percent': float(row.get('涨跌幅', 0)),
                })
            return {'count': len(stocks), 'stocks': stocks}
        
        return self._fetch_with_retry(_fetch, 'get_stock_list')
    
    def get_index_quote(self, index_code: str = "000001") -> FetchResult:
        """获取指数行情"""
        def _fetch():
            ak = self._get_akshare()
            df = ak.index_zh_a_hist(symbol=index_code, period="daily")
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                return {
                    'index_code': index_code,
                    'date': latest.get('日期', ''),
                    'close': float(latest.get('收盘', 0)),
                    'open': float(latest.get('开盘', 0)),
                    'high': float(latest.get('最高', 0)),
                    'low': float(latest.get('最低', 0)),
                    'volume': int(latest.get('成交量', 0)),
                    'change': float(latest.get('涨跌额', 0)),
                    'change_percent': float(latest.get('涨跌幅', 0)),
                }
            return None
        
        return self._fetch_with_retry(_fetch, 'get_index_quote', index_code)
    
    def get_stock_financial(self, symbol: str) -> FetchResult:
        """获取股票财务指标"""
        def _fetch():
            ak = self._get_akshare()
            if '.' in symbol:
                code, _ = symbol.split('.')
            else:
                code = symbol
            
            df = ak.stock_financial_analysis_indicator(symbol=code)
            if df is not None and not df.empty:
                latest = df.iloc[0]
                return {
                    'symbol': symbol,
                    'roe': float(latest.get('净资产收益率', 0)) if '净资产收益率' in latest else None,
                    'eps': float(latest.get('每股收益', 0)) if '每股收益' in latest else None,
                    'revenue_growth': float(latest.get('营业收入同比增长率', 0)) if '营业收入同比增长率' in latest else None,
                    'profit_growth': float(latest.get('净利润同比增长率', 0)) if '净利润同比增长率' in latest else None,
                    'debt_ratio': float(latest.get('资产负债率', 0)) if '资产负债率' in latest else None,
                }
            return None
        
        return self._fetch_with_retry(_fetch, 'get_stock_financial', symbol)
    
    # ========== 工具方法 ==========
    
    def clear_cache(self, func_name: str = None):
        """清除缓存"""
        self.cache.clear(func_name)
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计"""
        cache_files = list(self.cache.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)
        return {
            'cache_count': len(cache_files),
            'total_size_bytes': total_size,
            'cache_dir': str(self.cache.cache_dir)
        }


# 全局实例（单例模式）
_fetcher_instance = None

def get_fetcher(config: Dict = None) -> DataFetcher:
    """获取DataFetcher单例实例"""
    global _fetcher_instance
    if _fetcher_instance is None:
        _fetcher_instance = DataFetcher(config)
    return _fetcher_instance


def fetch_stock_quote(symbol: str, use_cache: bool = True) -> Dict:
    """便捷函数：获取股票实时行情"""
    fetcher = get_fetcher()
    if not use_cache:
        fetcher.clear_cache('get_stock_quote')
    result = fetcher.get_stock_quote(symbol)
    return result.to_dict()


def fetch_stock_history(symbol: str, days: int = 30, use_cache: bool = True) -> Dict:
    """便捷函数：获取股票历史数据"""
    fetcher = get_fetcher()
    if not use_cache:
        fetcher.clear_cache('get_stock_history')
    result = fetcher.get_stock_history(symbol, days)
    return result.to_dict()


def fetch_stock_list(use_cache: bool = True) -> Dict:
    """便捷函数：获取A股列表"""
    fetcher = get_fetcher()
    if not use_cache:
        fetcher.clear_cache('get_stock_list')
    result = fetcher.get_stock_list()
    return result.to_dict()


if __name__ == "__main__":
    # 测试代码
    print("=" * 50)
    print("Data Fetcher 测试")
    print("=" * 50)
    
    # 测试获取股票行情
    print("\n1. 测试获取股票行情 (000001.SZ):")
    result = fetch_stock_quote("000001.SZ")
    print(f"   成功: {result['success']}")
    print(f"   来自缓存: {result['from_cache']}")
    print(f"   重试次数: {result['retries']}")
    if result['success']:
        print(f"   数据: {result['data']}")
    else:
        print(f"   错误: {result['error']}")
    
    # 测试缓存
    print("\n2. 测试缓存功能:")
    result2 = fetch_stock_quote("000001.SZ")
    print(f"   第二次请求来自缓存: {result2['from_cache']}")
    
    # 测试历史数据
    print("\n3. 测试获取历史数据:")
    result3 = fetch_stock_history("000001.SZ", days=5)
    print(f"   成功: {result3['success']}")
    if result3['success']:
        print(f"   获取天数: {result3['data']['days']}")
    
    # 缓存统计
    print("\n4. 缓存统计:")
    fetcher = get_fetcher()
    stats = fetcher.get_cache_stats()
    print(f"   缓存文件数: {stats['cache_count']}")
    print(f"   总大小: {stats['total_size_bytes']} bytes")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)
